#!/usr/bin/env python3
"""Banc de `outils/verifier-source-distante.py`, sans réseau extérieur.

Ce script dit si la version en ligne du simulateur est utilisable : la page est
servie **et** une API de calcul répond. Il décide de la bascule automatique du
site et il n'avait aucun test — le dernier contrôle de l'inventaire dans ce cas.

Le banc ne simule pas la lecture HTTP : il la fait. Un petit serveur se lie à un
port éphémère sur la boucle locale, sert les réponses voulues, et le script est
lancé en sous-processus avec `SIMULATEUR_SOURCE_DISTANTE_TEST_LOCALE=1`, la seule
exception prévue pour les tests locaux. Sont donc réellement exercés : la liste
d'hôtes autorisés, `urllib`, la reconnaissance des marqueurs de page, la lecture
du JSON d'API, l'ordre des routes et le code de sortie.

Sept cas :

1. page du moteur **et** API de calcul : code 0, « fonctionnelle » ;
2. page de présentation (sans les marqueurs) : code 1, et jamais « disponible » ;
3. page correcte, API absente (404) : code 1, la raison est dite ;
4. page correcte, `/api/scenarios` absente mais `/api/catalogue` présente :
   code 0 — la seconde route suffit, ce qui prouve que la boucle essaie les deux ;
5. API qui répond 200 avec un JSON sans les clés attendues : code 1 ;
6. port fermé : code 1, message « injoignable » — et surtout pas un succès ;
7. adresse sur un hôte non autorisé : code 1, refus **sans aucune requête**.

Le mode `--json` est vérifié sur le premier cas : `disponible`, les deux statuts
et la révision des routes.

Usage :
    python3 outils/test_verifier_source_distante.py
"""

from __future__ import annotations

import json
import subprocess
import sys
import threading
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
SCRIPT = RACINE / "outils" / "verifier-source-distante.py"

PAGE_MOTEUR = (
    "<!doctype html><title>Simulateur Macro-Politique</title>"
    "<main id='console-pilotage'>Leviers et scénarios</main>"
)
PAGE_PRESENTATION = "<!doctype html><title>Un simulateur arrive bientôt</title><p>Page de présentation.</p>"


def reponse(route: str, serveur: dict[str, tuple[int, bytes]]) -> tuple[int, bytes]:
    return serveur.get(route, (404, b"introuvable"))


class Serveur:
    """Serveur local dont les réponses sont écrites par le cas de test."""

    def __init__(self, routes: dict[str, tuple[int, bytes]]) -> None:
        self.routes = routes
        serveur = self

        class Gestionnaire(BaseHTTPRequestHandler):
            def do_GET(self) -> None:  # noqa: N802 - API stdlib
                statut, corps = reponse(self.path, serveur.routes)
                self.send_response(statut)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(corps)))
                self.end_headers()
                self.wfile.write(corps)

            def log_message(self, *args) -> None:  # noqa: ANN002 - silence
                pass

        self.httpd = ThreadingHTTPServer(("127.0.0.1", 0), Gestionnaire)
        self.port = self.httpd.server_address[1]
        self.thread = threading.Thread(target=self.httpd.serve_forever, daemon=True)

    def __enter__(self) -> "Serveur":
        self.thread.start()
        return self

    def __exit__(self, *exception) -> None:  # noqa: ANN002
        self.httpd.shutdown()
        self.httpd.server_close()
        self.thread.join(timeout=5)

    @property
    def adresse(self) -> str:
        return f"http://127.0.0.1:{self.port}"


def lancer(*arguments: str, url: str | None = None) -> subprocess.CompletedProcess[str]:
    """Lance le script du dépôt, avec l'exception localhost explicitement activée."""
    commande = [sys.executable, str(SCRIPT), *arguments]
    if url:
        commande += ["--url", url]
    return subprocess.run(
        commande,
        capture_output=True,
        text=True,
        check=False,
        env={
            **__import__("os").environ,
            "SIMULATEUR_SOURCE_DISTANTE_TEST_LOCALE": "1",
            # Aucune variable ne doit court-circuiter l'adresse passée en argument.
            "SIMULATEUR_SOURCE_DISTANTE": "",
        },
    )


class TestSourceDistante(unittest.TestCase):
    def test_page_et_api_fonctionnelles(self) -> None:
        routes = {"/": (200, PAGE_MOTEUR.encode()), "/api/scenarios": (200, b'{"scenarios": []}')}
        with Serveur(routes) as serveur:
            resultat = lancer(url=serveur.adresse)
        self.assertEqual(resultat.returncode, 0, resultat.stdout + resultat.stderr)
        self.assertIn("Source distante fonctionnelle", resultat.stdout)
        self.assertIn("le site affiche la version en développement", resultat.stdout)

    def test_page_de_presentation_refusee(self) -> None:
        """Une page de présentation s'affiche très bien, et ne calcule rien."""
        with Serveur({"/": (200, PAGE_PRESENTATION.encode())}) as serveur:
            resultat = lancer(url=serveur.adresse)
        self.assertEqual(resultat.returncode, 1, resultat.stdout)
        self.assertIn("La page du simulateur n'est pas servie", resultat.stdout)
        self.assertIn("la copie locale du site M.R.S.C fait le calcul", resultat.stdout)

    def test_api_absente_refusee(self) -> None:
        with Serveur({"/": (200, PAGE_MOTEUR.encode())}) as serveur:
            resultat = lancer(url=serveur.adresse)
        self.assertEqual(resultat.returncode, 1, resultat.stdout)
        self.assertIn("aucune API de calcul n'est exposée", resultat.stdout)
        self.assertIn("statut 404", resultat.stdout)

    def test_seconde_route_suffit(self) -> None:
        """`/api/scenarios` manque : `/api/catalogue` doit être essayée ensuite."""
        routes = {
            "/": (200, PAGE_MOTEUR.encode()),
            "/api/catalogue": (200, json.dumps({"parametres": [], "domaines": []}).encode()),
        }
        with Serveur(routes) as serveur:
            resultat = lancer(url=serveur.adresse)
        self.assertEqual(resultat.returncode, 0, resultat.stdout)
        self.assertIn("/api/catalogue", resultat.stdout)
        self.assertIn("Source distante fonctionnelle", resultat.stdout)

    def test_json_sans_les_cles_attendues_refuse(self) -> None:
        """Un 200 ne suffit pas : la réponse doit porter les clés du moteur."""
        routes = {"/": (200, PAGE_MOTEUR.encode()), "/api/scenarios": (200, b'{"erreur": "maintenance"}')}
        with Serveur(routes) as serveur:
            resultat = lancer(url=serveur.adresse)
        self.assertEqual(resultat.returncode, 1, resultat.stdout)
        # Les deux routes sont nommées : la première a répondu 200 avec un JSON
        # sans les clés attendues, la seconde 404. Avant le 29 octobre 2026,
        # seule la dernière était affichée et la raison du refus se perdait.
        self.assertIn("/api/scenarios → statut 200, moteur : non", resultat.stdout)
        self.assertIn("/api/catalogue → statut 404, moteur : non", resultat.stdout)
        self.assertIn("aucune API de calcul n'est exposée", resultat.stdout)

    def test_port_ferme_dit_injoignable(self) -> None:
        # Un port fermé : on en ouvre un puis on le referme, sans jamais servir.
        with Serveur({}) as serveur:
            adresse = serveur.adresse
        resultat = lancer(url=adresse)
        self.assertEqual(resultat.returncode, 1, resultat.stdout)
        self.assertIn("Adresse injoignable", resultat.stdout)
        self.assertNotIn("fonctionnelle", resultat.stdout)

    def test_json_refuse_sort_en_erreur(self) -> None:
        """`--json` ne doit pas transformer un refus en succès.

        Trouvé en muttant `return 0 if resultat["disponible"] else 1` en
        `return 0` : aucun cas ne l'a vu, parce que `--json` n'était vérifié que
        sur l'adresse qui fonctionne.
        """
        with Serveur({"/": (200, PAGE_PRESENTATION.encode())}) as serveur:
            resultat = lancer("--json", url=serveur.adresse)
        self.assertEqual(resultat.returncode, 1, resultat.stdout)
        charge = json.loads(resultat.stdout)
        self.assertFalse(charge["disponible"])
        self.assertEqual(charge["api_essais"], [])

    def test_hote_non_autorise_refuse_sans_requete(self) -> None:
        resultat = lancer(url="https://exemple.invalid")
        self.assertEqual(resultat.returncode, 1, resultat.stdout)
        self.assertIn("pas sur la liste des hôtes HTTPS autorisés", resultat.stdout)
        # Aucun délai réseau : la décision est prise avant toute connexion.
        self.assertIn("statut 0", resultat.stdout)

    def test_json_decrit_les_deux_verifications(self) -> None:
        routes = {"/": (200, PAGE_MOTEUR.encode()), "/api/scenarios": (200, b'{"scenarios": []}')}
        with Serveur(routes) as serveur:
            resultat = lancer("--json", url=serveur.adresse)
        self.assertEqual(resultat.returncode, 0, resultat.stdout + resultat.stderr)
        charge = json.loads(resultat.stdout)
        self.assertTrue(charge["disponible"])
        self.assertEqual(charge["page"], {"statut": 200, "indice_simulateur": True})
        self.assertEqual(charge["api"]["route"], "/api/scenarios")
        self.assertEqual(charge["api"]["statut"], 200)
        self.assertTrue(charge["api"]["indice_moteur"])
        # La liste des routes essayées accompagne le résultat : un consommateur
        # de l'API peut dire laquelle a répondu quoi.
        self.assertEqual(charge["api_essais"], [{"route": "/api/scenarios", "statut": 200, "indice_moteur": True}])
        # L'adresse est normalisée, sans identifiants ni chemin : elle peut être publiée.
        self.assertTrue(charge["source"].startswith("http://127.0.0.1:"))
        self.assertTrue(charge["verifie_le"].endswith("Z"))


if __name__ == "__main__":
    unittest.main(verbosity=2)
