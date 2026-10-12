"""Fonction du site M.R.S.C — la source distante du simulateur est-elle utilisable ?

Le site embarque une copie du moteur (« source locale »), mais le simulateur
poursuit son développement dans son propre dépôt, où il est hébergé sur Render
(« source distante »). Cette fonction dit, côté serveur — donc sans les
limitations du navigateur — si cette source distante est **réellement
fonctionnelle** : page servie *et* API de calcul qui répond.

Le site M.R.S.C peut être déployé sur Vercel : c'est l'hébergeur possible de
cette fonction, pas l'adresse active du simulateur.

C'est elle qui décide de la bascule : `assets/js/site.js` embarque la source
distante quand elle répond « disponible », et retombe sinon sur la copie locale.
Vérifier les deux aspects évite le piège classique : une page de présentation
statique s'affiche très bien… mais sans moteur pour calculer.

Environnement :
    SIMULATEUR_SOURCE_DISTANTE                 force l'adresse à vérifier ;
                                               seuls les hôtes HTTPS autorisés
                                               sont appelés.
    SIMULATEUR_SOURCE_DISTANTE_HOTES_AUTORISES hôtes HTTPS exacts additionnels,
                                               séparés par des virgules, pour la
                                               préproduction.
    SIMULATEUR_SOURCE_DISTANTE_TEST_LOCALE     exception localhost réservée aux
                                               tests ; ne pas définir en production.

Sans surcharge, l'adresse vient de `simulateur.html` (`data-source-distante`) :
une seule source de vérité, partagée avec la page.

⚠️ Fichier propre au site M.R.S.C (pas une route du moteur).
"""

from __future__ import annotations

import json
import os
import re
import time
import urllib.error
import urllib.request
from urllib.parse import urlsplit
from http.server import BaseHTTPRequestHandler
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
PAGE_DU_SITE = RACINE / "simulateur.html"
DELAI = 8.0  # secondes, par requête
DUREE_CACHE = 300.0  # secondes
UA = "MRSC-verification-source/1.0 (+https://github.com/thejmimiia-code/MRSC)"

#: Marqueurs qui trahissent la page du moteur (et non une page de présentation).
MARQUEURS_PAGE = ("console-pilotage", "Simulateur Macro-Politique", "leviers")
#: Routes interrogées et clés attendues dans la réponse JSON du moteur.
ROUTES_API = (("/api/scenarios", ("scenarios",)), ("/api/catalogue", ("parametres", "domaines")))

_cache: dict[str, tuple[float, dict[str, object]]] = {}
HOTE_SOURCE_PRODUCTION = "simulateur-macro-politique.onrender.com"


def _source_autorisee(source: str) -> bool:
    """Refuse les cibles arbitraires (localhost, IP privées, ports et redirections).

    Un hôte de préproduction peut être ajouté à la configuration de déploiement
    via SIMULATEUR_SOURCE_DISTANTE_HOTES_AUTORISES. Les tests locaux doivent
    s'activer explicitement avec SIMULATEUR_SOURCE_DISTANTE_TEST_LOCALE=1.
    """
    try:
        cible = urlsplit(source)
        hote = (cible.hostname or "").lower().rstrip(".")
        port = cible.port
    except ValueError:
        return False
    if not hote or cible.username or cible.password or cible.query or cible.fragment:
        return False
    if cible.path not in ("", "/"):
        return False
    if cible.scheme == "https":
        if port not in (None, 443):
            return False
        supplementaires = {
            valeur.strip().lower().rstrip(".")
            for valeur in os.environ.get("SIMULATEUR_SOURCE_DISTANTE_HOTES_AUTORISES", "").split(",")
            if valeur.strip()
        }
        return hote == HOTE_SOURCE_PRODUCTION or hote in supplementaires
    return (
        os.environ.get("SIMULATEUR_SOURCE_DISTANTE_TEST_LOCALE") == "1"
        and cible.scheme == "http"
        and hote in {"localhost", "127.0.0.1", "::1"}
        and port is not None
    )


class _SansRedirection(urllib.request.HTTPRedirectHandler):
    """N'autorise pas une source déclarée à rediriger vers une cible privée."""

    def redirect_request(self, req, fp, code, msg, headers, newurl):  # noqa: ANN001
        return None


_OPENER = urllib.request.build_opener(_SansRedirection())


def adresse_configurée() -> str:
    """Adresse de la source distante : variable d'environnement, sinon la page."""
    forcee = os.environ.get("SIMULATEUR_SOURCE_DISTANTE", "").strip()
    if forcee:
        return forcee
    try:
        page = PAGE_DU_SITE.read_text(encoding="utf-8")
    except OSError:
        return ""
    trouve = re.search(r'data-source-distante="([^"]+)"', page)
    return trouve.group(1).strip() if trouve else ""


def _lire(url: str) -> tuple[int, bytes]:
    requete = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "*/*"})
    try:
        with _OPENER.open(requete, timeout=DELAI) as reponse:
            return reponse.status, reponse.read(200_000)
    except urllib.error.HTTPError as erreur:
        return erreur.code, erreur.read(20_000)
    except (urllib.error.URLError, OSError, ValueError) as erreur:
        return 0, str(erreur).encode("utf-8", "replace")


def _indice_page(contenu: bytes) -> bool:
    texte = contenu.decode("utf-8", "replace")
    return sum(marqueur in texte for marqueur in MARQUEURS_PAGE) >= 2


def _indice_api(contenu: bytes, cles: tuple[str, ...]) -> bool:
    try:
        charge = json.loads(contenu.decode("utf-8", "replace"))
    except (json.JSONDecodeError, UnicodeDecodeError):
        return False
    return isinstance(charge, dict) and any(cle in charge for cle in cles)


def verifier(source: str) -> dict[str, object]:
    """Interroge la source : page d'abord, API ensuite."""
    resultat: dict[str, object] = {
        "source": "",
        "disponible": False,
        "page": {"statut": 0, "indice_simulateur": False},
        "api": {"route": "", "statut": 0, "indice_moteur": False},
        "verifie_le": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }
    if not source:
        resultat["message"] = "Aucune source distante configurée (attribut data-source-distante)."
        return resultat
    if not _source_autorisee(source):
        resultat["message"] = "La source configurée n’est pas sur la liste des hôtes HTTPS autorisés."
        return resultat

    # La validation a garanti l'absence d'identifiants, de chemin arbitraire et
    # de port inhabituel : l'adresse peut être exposée sans révéler un secret.
    cible = urlsplit(source)
    port = f":{cible.port}" if cible.port is not None else ""
    resultat["source"] = f"{cible.scheme}://{cible.hostname}{port}/"
    base = resultat["source"]
    statut, contenu = _lire(base)
    indice = statut == 200 and _indice_page(contenu)
    resultat["page"] = {"statut": statut, "indice_simulateur": indice}
    if statut == 0:
        resultat["message"] = (
            "Adresse injoignable depuis cet environnement (réseau indisponible ou filtre sortant) : "
            "la copie locale du site M.R.S.C fait le calcul."
        )
        return resultat
    if not indice:
        resultat["message"] = (
            "La page du simulateur n'est pas servie à cette adresse : la version en ligne reste "
            "consultable comme site, mais la copie locale du site M.R.S.C fait le calcul."
        )
        return resultat

    for route, cles in ROUTES_API:
        statut_api, contenu_api = _lire(base + route.lstrip("/"))
        moteur = statut_api == 200 and _indice_api(contenu_api, cles)
        resultat["api"] = {"route": route, "statut": statut_api, "indice_moteur": moteur}
        if moteur:
            resultat["disponible"] = True
            resultat["message"] = "Source distante fonctionnelle : page et API de calcul répondent."
            return resultat

    resultat["message"] = (
        "La page répond, mais aucune API de calcul n'est exposée à cette adresse : la version en "
        "ligne ne peut pas simuler, la copie locale du site M.R.S.C est utilisée."
    )
    return resultat


def etat(rafraichir: bool = False) -> dict[str, object]:
    source = adresse_configurée()
    maintenant = time.monotonic()
    entree = _cache.get(source)
    if entree and not rafraichir and maintenant - entree[0] < DUREE_CACHE:
        resultat = dict(entree[1])
        resultat["cache"] = True
        return resultat
    resultat = verifier(source)
    resultat["cache"] = False
    _cache[source] = (maintenant, resultat)
    return resultat


class handler(BaseHTTPRequestHandler):  # noqa: N801 - nom attendu par Vercel
    """GET /api/verifier-source → état mis en cache de la source distante."""

    server_version = "MRSC"
    sys_version = ""

    def do_GET(self) -> None:  # noqa: N802 - API stdlib
        # Une query publique ne peut pas contourner le cache de cinq minutes
        # pour déclencher des requêtes réseau répétées.
        charge = etat()
        corps = json.dumps(charge, ensure_ascii=False, indent=2).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(corps)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.end_headers()
        self.wfile.write(corps)

    def do_HEAD(self) -> None:  # noqa: N802 - API stdlib
        charge = etat()
        corps = json.dumps(charge, ensure_ascii=False).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(corps)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.end_headers()
