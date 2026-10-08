#!/usr/bin/env python3
"""
simulateur/dashboard.py — Serveur web du simulateur macro-politique.

Deux niveaux de service cohabitent :

  * **Simulateur interactif** (page `/`) : catalogue de leviers réglables, contexte de
    données publiques « instant T », 20 domaines d'impact, matrice croisée
    levier × domaine, exports.
      - `GET  /api/catalogue`  : leviers, familles, préréglages, domaines ;
      - `GET  /api/contexte`   : contexte réel + provenance + sources navigateur ;
      - `GET  /api/marches`    : 13 indices représentatifs, cotations à la demande et fraîcheur ;
      - `POST /api/donnees`    : valeurs collectées par le navigateur (API publiques) ;
      - `POST /api/simuler`    : simulation paramétrique complète ;
      - `GET  /api/comparer`   : comparaison des préréglages à l'année finale ;
      - `GET  /api/bulles`     : bulles explicatives de tous les leviers (chaîne
                                 d'interaction, répercussions mesurées, lecture
                                 opportunités / désagréments) ;
      - `GET  /api/bulle`      : bulle d'un seul levier (`?levier=…`).

  * **Scénarios historiques** du dépôt, conservés à l'identique pour la
    compatibilité (scripts, CI, utilisateurs) :
      - `GET /api/scenarios`, `GET /api/run?scenario=`, `GET /api/export?…`.

Aucune dépendance externe : uniquement la bibliothèque standard. Le serveur est
multi-thread (`ThreadingHTTPServer`, `daemon_threads=True`) en HTTP/1.1 avec
`Content-Length` explicite (nécessaire derrière un proxy à connexions
persistantes).
"""

from __future__ import annotations

import argparse
import csv as csv_mod
import json
import os
import sys
import traceback
from dataclasses import asdict
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Lock
from typing import Any
from urllib.parse import parse_qs, urlparse

from simulateur.bulles import DETAILS, bulle_levier, bulles_catalogue
from simulateur.clarte import lecture_claire
from simulateur.cli import CATALOGUE_SCENARIOS, SCENARIOS_DISPONIBLES, executer_scenario
from simulateur.compression import EN_TETE_VARY, repondre
from simulateur.conseil import conseil_mouvement
from simulateur.donnees_live import (
    INDICATEURS,
    Lecture,
    browser_payload,
    charger_cache,
    construire_contexte,
    interroger,
    sauver_cache,
)
from simulateur.interface import HTML_PAGE
from simulateur.lexique import lexique_public
from simulateur.marches import obtenir_cotations
from simulateur.moteur_parametrique import (
    catalogue_complet,
    comparer,
)
from simulateur.moteur_parametrique import (
    simuler as simuler_parametrique,
)
from simulateur.observatoire import observatoire_public
from simulateur.parametres import PRESETS
from simulateur.seuils import bareme_public

#: Catalogue des scénarios historiques : clé → (fabrique de décisions, nom,
#: description, couleur). `fn` est exposé pour la compatibilité des tests.
SCENARIOS: dict[str, dict[str, Any]] = {
    "mandature": {
        "nom": "Plan de mandature républicaine",
        "description": "Réformes structurelles, fraude, niches : déficit sous 3 % en année 5.",
        "couleur": "#22c55e",
        "fn": CATALOGUE_SCENARIOS["mandature"][0],
    },
    "statut_quo": {
        "nom": "Statu quo",
        "description": "Immobilisme politique et dérive budgétaire.",
        "couleur": "#f59e0b",
        "fn": CATALOGUE_SCENARIOS["statut_quo"][0],
    },
    "austerite": {
        "nom": "Austérité brute",
        "description": "Coupes territoriales et fronde fiscale.",
        "couleur": "#ef4444",
        "fn": CATALOGUE_SCENARIOS["austerite"][0],
    },
    "choc_mondial": {
        "nom": "Choc mondial (stagflation)",
        "description": "Pétrole en hausse, resserrement Fed, commerce fragilisé.",
        "couleur": "#8b5cf6",
        "fn": CATALOGUE_SCENARIOS["choc_mondial"][0],
    },
    "crise_taiwan": {
        "nom": "Crise de Taïwan",
        "description": "Blocus, semi-conducteurs, Chips Act souverain.",
        "couleur": "#f97316",
        "fn": CATALOGUE_SCENARIOS["crise_taiwan"][0],
    },
    "hormuz": {
        "nom": "Fermeture d'Hormuz",
        "description": "20 % du pétrole mondial coupé, Brent au-delà de 150 $.",
        "couleur": "#dc2626",
        "fn": CATALOGUE_SCENARIOS["hormuz"][0],
    },
    "escalade_nucleaire": {
        "nom": "Escalade nucléaire tactique",
        "description": "OTAN-Russie : franchissement du seuil, marchés fermés.",
        "couleur": "#7f1d1d",
        "fn": CATALOGUE_SCENARIOS["escalade_nucleaire"][0],
    },
    "convergence_ww3": {
        "nom": "Convergence Chine-Russie-Iran",
        "description": "Guerre mondiale, blocs fermés, économie de guerre.",
        "couleur": "#4c1d95",
        "fn": CATALOGUE_SCENARIOS["convergence_ww3"][0],
    },
    "resilience": {
        "nom": "Résilience républicaine",
        "description": "Mandature + réarmement OTAN à 3,5 % du PIB.",
        "couleur": "#38bdf8",
        "fn": CATALOGUE_SCENARIOS["resilience"][0],
    },
    "double_mandature": {
        "nom": "Deux mandatures consécutives (2027-2037)",
        "description": "Dix ans : verrou constitutionnel des réformes, second dividende "
                       "de la dette réinvesti, investissements à cycle long.",
        "couleur": "#2dd4bf",
        "fn": CATALOGUE_SCENARIOS["double_mandature"][0],
    },
    "alternance_2032": {
        "nom": "Stress-test : alternance 2032",
        "description": "Deux mandatures sans verrou constitutionnel : réformes révocables, "
                       "usure maximale du capital politique.",
        "couleur": "#f43f5e",
        "fn": CATALOGUE_SCENARIOS["alternance_2032"][0],
    },
}

#: Référence de contexte réutilisée entre les requêtes (mise en cache mémoire).
_CONTEXTE_CACHE: dict[str, Any] = {"contexte": None}


# ────────────────────────────────────────────────────────────────────────────
# Simulation historique (API d'origine, conservée à l'identique)
# ────────────────────────────────────────────────────────────────────────────

def run_simulation_api(scenario: str) -> dict[str, Any]:
    """Exécute un scénario historique et retourne une charge utile sérialisable."""
    if scenario not in SCENARIOS:
        return {"error": f"Scénario inconnu : {scenario}"}
    try:
        resultats = executer_scenario(scenario)
        return {
            "scenario": scenario,
            "nom": SCENARIOS[scenario]["nom"],
            "resultats": [asdict(r) for r in resultats],
        }
    except Exception as exc:  # pragma: no cover - garde-fou
        return {"error": str(exc), "traceback": traceback.format_exc()}


def contexte_courant(rafraichir: bool = False):
    """Retourne le contexte « instant T » (cache mémoire, sinon collecte)."""
    if _CONTEXTE_CACHE["contexte"] is None or rafraichir:
        _CONTEXTE_CACHE["contexte"] = construire_contexte(rafraichir=rafraichir)
    return _CONTEXTE_CACHE["contexte"]


_CACHE_BULLES: dict[tuple, Any] = {}
_VERROU_BULLES = Lock()


def catalogue_bulles(contexte, cles=None, avec_mesure: bool = True, detail: str = "resume"):
    """Catalogue de bulles **mémoïsé** : le calcul complet coûte plusieurs secondes.

    Mesuré sur ce dépôt : la construction des 101 bulles « détail complet »
    prenait environ 4,6 s et produisait 2,1 Mio de JSON. Le contenu ne dépend
    que du catalogue des leviers et du contexte « instant T » : il est donc
    identique d'une requête à l'autre tant que le contexte n'a pas changé. On le
    calcule une fois, puis on le ressert.

    La clé de cache contient l'horodatage du contexte : un « Rafraîchir les
    données » change l'horodatage et invalide donc naturellement le cache. Un
    verrou évite que deux requêtes concurrentes ne calculent la même chose.
    """
    cle_cache = (detail, avec_mesure, tuple(cles or ()), contexte.mode, contexte.horodatage)
    with _VERROU_BULLES:
        if cle_cache in _CACHE_BULLES:
            return _CACHE_BULLES[cle_cache]
    resultat = bulles_catalogue(contexte, cles=cles, avec_mesure=avec_mesure, detail=detail)
    with _VERROU_BULLES:
        # Petit cache : au-delà de 6 entrées on repart de zéro (les variantes
        # « résumé / complet » et les sous-ensembles de leviers sont en nombre
        # fini, mais un usage soutenu ne doit pas faire croître la mémoire).
        if len(_CACHE_BULLES) >= 6:
            _CACHE_BULLES.clear()
        _CACHE_BULLES[cle_cache] = resultat
    return resultat


def _avec_lecture(sortie) -> dict[str, Any]:
    """Ajoute la « lecture en clair » à une sortie de simulation sérialisée.

    Les chiffres du moteur sont exacts ; ils ne sont pas forcément lisibles par
    quelqu'un qui ne pratique pas les finances publiques. `lecture_claire`
    traduit la trajectoire en phrases ordinaires, à partir des mêmes nombres —
    jamais à côté d'eux.
    """
    charge = sortie.en_dict()
    try:
        charge["lecture"] = lecture_claire(charge)
    except Exception:  # pragma: no cover - la lecture est un confort
        charge["lecture"] = {}
    return charge


def enregistrer_donnees_navigateur(lectures_brutes: dict[str, Any]) -> dict[str, Any]:
    """Fusionne des valeurs collectées par le navigateur dans le cache local.

    Le navigateur de l'utilisateur peut atteindre des API publiques même quand
    le serveur vit dans un environnement réseau fermé : ces valeurs sont donc
    écrites dans le cache puis utilisées pour recalibrer le contexte.
    """
    lectures = charger_cache()
    for cle, brut in (lectures_brutes or {}).items():
        if cle not in INDICATEURS or not isinstance(brut, dict):
            continue
        try:
            valeur = float(brut.get("valeur"))
        except (TypeError, ValueError):
            continue
        lectures[cle] = Lecture(
            cle=cle,
            valeur=valeur,
            periode=brut.get("periode"),
            fournisseur=brut.get("fournisseur") or "navigateur (API publique)",
            url=brut.get("url") or "",
            statut="live",
            detail="collecté par le navigateur de l'utilisateur",
            qualite_code=(str(brut["qualite_code"]) if brut.get("qualite_code") else None),
        )
    if lectures:
        try:
            sauver_cache(lectures)
        except OSError:
            pass
    _CONTEXTE_CACHE["contexte"] = construire_contexte(lectures)
    return {"contexte": _CONTEXTE_CACHE["contexte"].en_dict(),
            "lectures": sorted(lectures)}


def rapport_collecte() -> dict[str, Any]:
    """Diagnostic de collecte : quelles séries sont live, en référence ou absentes."""
    contexte = contexte_courant()
    details = contexte.provenance
    return {
        "mode": contexte.mode,
        "horodatage": contexte.horodatage,
        "live": [champ for champ, info in details.items() if info["statut"] == "live"],
        "reference": [champ for champ, info in details.items() if info["statut"] == "reference"],
        "indisponible": [champ for champ, info in details.items()
                         if info["statut"] not in ("live", "reference")],
        "fournisseurs": sorted({info["source"] for info in details.values()}),
    }


# ────────────────────────────────────────────────────────────────────────────
# Handler HTTP
# ────────────────────────────────────────────────────────────────────────────

class DashboardHandler(BaseHTTPRequestHandler):
    """Routeur HTTP du simulateur (bibliothèque standard uniquement)."""

    protocol_version = "HTTP/1.1"
    server_version = "SimulateurMacroPolitique/2.0"
    #: Vrai pendant une requête HEAD : on envoie les en-têtes (statut, type,
    #: longueur) mais jamais le corps. Les sondes de disponibilité des aperçus
    #: et des moniteurs utilisent HEAD ; sans cette prise en charge elles
    #: recevaient un 501 et l'aperçu pouvait rester vide.
    _tete_seulement = False

    # ── utilitaires de réponse ─────────────────────────────────────────────
    def log_message(self, format: str, *args) -> None:  # noqa: A002 - API stdlib
        if os.environ.get("SIMULATEUR_LOG"):
            super().log_message(format, *args)

    def _send_status(self, status: int) -> None:
        self.send_response(status)
        self.send_header("Content-Length", "0")
        self.end_headers()

    def _preparer_charge(self, charge: bytes) -> tuple[bytes, str | None]:
        """Compresse la charge si le navigateur l'accepte (voir compression.py).

        Le gain est mesuré et documenté dans docs/RD_OPTIMISATION_FLUIDITE.md :
        une simulation complète passe d'environ 240 Kio à une trentaine de Kio
        sur le réseau, pour le même contenu.
        """
        return repondre(self.headers.get("Accept-Encoding"), charge)

    def _send_html(self, contenu: str) -> None:
        charge, encodage = self._preparer_charge(contenu.encode("utf-8"))
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(charge)))
        self.send_header("Vary", EN_TETE_VARY)
        if encodage:
            self.send_header("Content-Encoding", encodage)
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        if not self._tete_seulement:
            self.wfile.write(charge)

    def _send_json(self, donnees: dict[str, Any], status: int = 200) -> None:
        charge, encodage = self._preparer_charge(
            json.dumps(donnees, ensure_ascii=False, default=str).encode("utf-8")
        )
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(charge)))
        self.send_header("Vary", EN_TETE_VARY)
        if encodage:
            self.send_header("Content-Encoding", encodage)
        self.end_headers()
        if not self._tete_seulement:
            self.wfile.write(charge)

    def _send_fichier(self, chemin: str, type_mime: str = "application/octet-stream") -> None:
        donnees = Path(chemin).read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", type_mime)
        self.send_header("Content-Disposition", f'attachment; filename="{Path(chemin).name}"')
        self.send_header("Content-Length", str(len(donnees)))
        self.end_headers()
        if not self._tete_seulement:
            self.wfile.write(donnees)

    def _lire_corps(self) -> Any:
        try:
            longueur = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            return None
        if longueur <= 0:
            return None
        brut = self.rfile.read(longueur)
        try:
            return json.loads(brut.decode("utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError):
            return None

    @staticmethod
    def _parametres_depuis_requete(corps: Any, query: dict[str, list[str]]) -> dict[str, float]:
        if isinstance(corps, dict) and "parametres" in corps:
            return dict(corps.get("parametres") or {})
        if "params" in query:
            try:
                return dict(json.loads(query["params"][0]))
            except (json.JSONDecodeError, IndexError, TypeError):
                return {}
        return {}

    # ── HEAD ───────────────────────────────────────────────────────────────
    def do_HEAD(self) -> None:  # noqa: N802 - API stdlib
        """Sonde de disponibilité : mêmes en-têtes que GET, corps vide.

        Les aperçus hébergés et les moniteurs vérifient souvent qu'un service
        répond par un HEAD avant d'afficher la page ; un 501 laissait alors
        l'aperçu vide alors que le serveur fonctionnait.
        """
        self._tete_seulement = True
        try:
            self.do_GET()
        finally:
            self._tete_seulement = False

    # ── GET ────────────────────────────────────────────────────────────────
    def do_GET(self) -> None:  # noqa: N802 - API stdlib
        parsed = urlparse(self.path)
        chemin = parsed.path
        query = parse_qs(parsed.query)

        if chemin in ("/", ""):
            try:
                scenarios_json = json.dumps(
                    {cle: {k: v for k, v in valeur.items() if k != "fn"}
                     for cle, valeur in SCENARIOS.items()},
                    ensure_ascii=False,
                )
                self._send_html(HTML_PAGE.replace("===SCENARIOS_JSON===", scenarios_json))
            except Exception:
                self._send_json({"error": traceback.format_exc(), "route": chemin})

        elif chemin == "/api/catalogue":
            self._send_json(catalogue_complet())

        elif chemin == "/api/contexte":
            rafraichir = query.get("refresh", ["0"])[0] in ("1", "true", "oui")
            contexte = contexte_courant(rafraichir=rafraichir)
            self._send_json({
                "contexte": contexte.en_dict(),
                "browser": browser_payload(),
                "observatoire": observatoire_public(),
                "diagnostic": rapport_collecte(),
            })

        elif chemin == "/api/marches":
            actualiser = query.get("refresh", ["0"])[0] in ("1", "true", "oui")
            self._send_json(obtenir_cotations(actualiser=actualiser))

        elif chemin == "/api/simuler":
            parametres = self._parametres_depuis_requete(None, query)
            avec_impacts = query.get("impacts", ["1"])[0] not in ("0", "false", "non")
            try:
                sortie = simuler_parametrique(
                    parametres, contexte_courant(), avec_impacts=avec_impacts
                )
                self._send_json(_avec_lecture(sortie))
            except ValueError as exc:
                self._send_json({"error": str(exc)}, status=400)
            except Exception:
                self._send_json({"error": traceback.format_exc()}, status=500)

        elif chemin == "/api/comparer":
            try:
                self._send_json(comparer(contexte=contexte_courant()))
            except Exception:
                self._send_json({"error": traceback.format_exc()}, status=500)

        elif chemin == "/api/garde_fous":
            # Barème complet (audit et traçabilité) : chaque seuil est livré
            # avec sa strate, ses bornes et sa source institutionnelle.
            try:
                self._send_json(bareme_public())
            except Exception:
                self._send_json({"error": traceback.format_exc()}, status=500)

        elif chemin == "/api/bulles":
            detail = query.get("detail", ["resume"])[0]
            if detail not in DETAILS:
                self._send_json({"error": f"détail inconnu : {detail}"}, status=400)
                return
            avec_mesure = query.get("mesure", ["1"])[0] not in ("0", "false", "non")
            brutes = [cle for valeur in query.get("levier", []) for cle in valeur.split(",") if cle]
            try:
                self._send_json(catalogue_bulles(
                    contexte_courant(), cles=brutes or None,
                    avec_mesure=avec_mesure, detail=detail,
                ))
            except ValueError as exc:
                self._send_json({"error": str(exc)}, status=400)
            except Exception:
                self._send_json({"error": traceback.format_exc()}, status=500)

        elif chemin == "/api/bulle":
            cle = query.get("levier", [""])[0]
            detail = query.get("detail", ["complet"])[0]
            avec_mesure = query.get("mesure", ["1"])[0] not in ("0", "false", "non")
            if not cle:
                self._send_json({"error": "Paramètre `levier` requis."}, status=400)
                return
            try:
                self._send_json(bulle_levier(
                    cle, contexte_courant(), avec_mesure=avec_mesure, detail=detail,
                ))
            except ValueError as exc:
                self._send_json({"error": str(exc)}, status=400)
            except Exception:
                self._send_json({"error": traceback.format_exc()}, status=500)

        elif chemin == "/api/lexique":
            # Lexique « compréhensible pour tous » : chaque terme technique
            # employé par la page, défini en français ordinaire, cherchable.
            recherche = query.get("q", [""])[0]
            self._send_json(lexique_public(recherche or None))

        elif chemin == "/api/presets":
            self._send_json({"presets": PRESETS})

        elif chemin == "/api/proxy":
            # Relais serveur vers une source **déclarée au registre** : aucune
            # URL arbitraire n'est acceptée (pas de proxy ouvert), et la lecture
            # est déjà convertie dans l'unité du modèle.
            cle = query.get("indicateur", [""])[0]
            if cle not in INDICATEURS:
                self._send_json({"error": f"indicateur inconnu : {cle}"}, status=400)
                return
            try:
                lecture = interroger(cle, timeout=12.0)
            except Exception:
                self._send_json({"error": traceback.format_exc()}, status=500)
                return
            self._send_json({"lecture": lecture.en_dict(), "indicateur": cle})

        # ── API historiques ───────────────────────────────────────────────
        elif chemin == "/api/run":
            scenario = query.get("scenario", ["mandature"])[0]
            self._send_json(run_simulation_api(scenario))

        elif chemin == "/api/scenarios":
            self._send_json({
                "scenarios": {
                    cle: {"nom": valeur["nom"], "description": valeur["description"],
                          "couleur": valeur["couleur"]}
                    for cle, valeur in SCENARIOS.items()
                }
            })

        elif chemin == "/api/export":
            scenario = query.get("scenario", ["mandature"])[0]
            fmt = query.get("format", ["json"])[0]
            if scenario not in SCENARIOS:
                self._send_json({"error": f"Scénario inconnu : {scenario}"}, status=404)
                return
            try:
                resultat = run_simulation_api(scenario)
                if "error" in resultat:
                    self._send_json(resultat, status=400)
                    return
                nom_fichier = f"{scenario}_simulateur.{fmt}"
                chemin_fichier = os.path.join(os.getcwd(), nom_fichier)
                if fmt == "json":
                    payload = {
                        "scenario": scenario,
                        "nom": SCENARIOS[scenario]["nom"],
                        "modele": "Gigogne 5 échelons",
                        "resultats": resultat["resultats"],
                    }
                    with open(chemin_fichier, "w", encoding="utf-8") as fichier:
                        json.dump(payload, fichier, ensure_ascii=False, indent=2)
                elif fmt == "csv":
                    champs = list(resultat["resultats"][0].keys())
                    with open(chemin_fichier, "w", newline="", encoding="utf-8") as fichier:
                        ecrivain = csv_mod.DictWriter(fichier, fieldnames=champs,
                                                      extrasaction="ignore")
                        ecrivain.writeheader()
                        for ligne in resultat["resultats"]:
                            if isinstance(ligne.get("commentaires"), list):
                                ligne["commentaires"] = "; ".join(ligne["commentaires"])
                            ecrivain.writerow(ligne)
                else:
                    self._send_json({"error": "Format non supporté. Utilisez json ou csv."},
                                    status=400)
                    return
                self._send_fichier(chemin_fichier,
                                   "application/json" if fmt == "json" else "text/csv")
                os.remove(chemin_fichier)
            except Exception:
                self._send_json({"error": traceback.format_exc()}, status=500)

        else:
            self._send_status(404)

    # ── POST ───────────────────────────────────────────────────────────────
    def do_POST(self) -> None:  # noqa: N802 - API stdlib
        parsed = urlparse(self.path)
        chemin = parsed.path
        corps = self._lire_corps()

        if chemin == "/api/simuler":
            if not isinstance(corps, dict):
                self._send_json({"error": "Corps JSON attendu."}, status=400)
                return
            try:
                sortie = simuler_parametrique(
                    corps.get("parametres") or {},
                    contexte_courant(),
                    horizon=int(corps.get("horizon", 5)),
                    avec_impacts=bool(corps.get("avec_impacts", True)),
                    max_leviers_impacts=int(corps.get("max_impacts", 16)),
                )
                self._send_json(_avec_lecture(sortie))
            except ValueError as exc:
                self._send_json({"error": str(exc)}, status=400)
            except Exception:
                self._send_json({"error": traceback.format_exc()}, status=500)

        elif chemin == "/api/donnees":
            if not isinstance(corps, dict):
                self._send_json({"error": "Corps JSON attendu."}, status=400)
                return
            try:
                self._send_json(enregistrer_donnees_navigateur(corps.get("lectures") or {}))
            except Exception:
                self._send_json({"error": traceback.format_exc()}, status=500)

        elif chemin == "/api/conseil":
            # Conseiller temps réel (« effet papillon ») : compare deux exécutions
            # réelles du moteur, le levier à sa position avant le dernier
            # mouvement puis à sa position à l'instant T, toutes choses égales.
            if not isinstance(corps, dict) or not corps.get("cle"):
                self._send_json({"error": "Corps JSON avec « cle » attendu."}, status=400)
                return
            try:
                conseil = conseil_mouvement(
                    corps.get("parametres") or {},
                    str(corps["cle"]),
                    float(corps.get("avant", 0.0)),
                    float(corps.get("apres", corps.get("avant", 0.0))),
                    contexte_courant(),
                    horizon=int(corps.get("horizon", 5)),
                )
                self._send_json(conseil)
            except (TypeError, ValueError) as exc:
                self._send_json({"error": str(exc)}, status=400)
            except Exception:
                self._send_json({"error": traceback.format_exc()}, status=500)

        else:
            self._send_status(405)


# ────────────────────────────────────────────────────────────────────────────
# Serveur
# ────────────────────────────────────────────────────────────────────────────

def create_server(host: str = "0.0.0.0", port: int = 8080) -> ThreadingHTTPServer:
    """Crée le serveur HTTP du simulateur (multi-thread, HTTP/1.1)."""
    serveur = ThreadingHTTPServer((host, port), DashboardHandler)
    serveur.daemon_threads = True
    return serveur


def _port_defaut() -> int:
    """Port d'écoute : celui de l'hébergeur s'il en impose un, sinon 8080.

    Presque toutes les plateformes (Render, Railway, Heroku, Scalingo, Fly,
    Clever Cloud…) injectent ``PORT`` et refusent toute autre valeur. Lire la
    variable permet de garder la même commande en local et en ligne, tout en
    laissant ``--port`` gagner lorsqu'il est fourni explicitement.
    """
    brut = os.environ.get("PORT", "").strip()
    try:
        return int(brut) if brut else 8080
    except ValueError:
        print(f"  PORT invalide ({brut!r}) — repli sur 8080.", file=sys.stderr)
        return 8080


def main() -> None:
    analyseur = argparse.ArgumentParser(
        description="Simulateur macro-politique — serveur web interactif"
    )
    analyseur.add_argument("--host", default=os.environ.get("HOST", "0.0.0.0"),
                           help="Adresse d'écoute (défaut : $HOST ou 0.0.0.0)")
    analyseur.add_argument("--port", type=int, default=_port_defaut(),
                           help="Port d'écoute (défaut : $PORT ou 8080)")
    analyseur.add_argument("--rafraichir", action="store_true",
                           help="Interroge les API publiques au démarrage")
    arguments = analyseur.parse_args()

    contexte = contexte_courant(rafraichir=arguments.rafraichir)
    serveur = create_server(arguments.host, arguments.port)
    print(f"  Simulateur lancé : http://{arguments.host}:{arguments.port}")
    print(f"  Contexte : {contexte.mode} · horodatage {contexte.horodatage}")
    print(f"  Scénarios historiques : {', '.join(SCENARIOS_DISPONIBLES)}")
    print(f"  {'=' * 62}")
    try:
        serveur.serve_forever()
    except KeyboardInterrupt:
        print("\n  Arrêt du simulateur.")
        serveur.shutdown()


if __name__ == "__main__":
    main()
