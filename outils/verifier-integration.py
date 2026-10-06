#!/usr/bin/env python3
"""Vérifie l'intégration du simulateur au site M.R.S.C, sans navigateur.

Contrôles effectués :

1. la page publiée `simulateur/index.html` est à jour par rapport au moteur ;
2. les fonctions de `api/` correspondent exactement aux routes du moteur ;
3. **chaque fonction sert bien sa route** : le gestionnaire de `api/*.py` est
   monté dans un serveur local, comme le fait Vercel, puis interrogé ;
4. les pages du site, `404.html`, `assets/` et les liens de navigation sont
   présents ;
5. la fonction `api/verifier-source.py` (source distante du simulateur) répond
   correctement, sur une source simulée puis sur une source injoignable.

Usage :
    python3 outils/verifier-integration.py
"""

from __future__ import annotations

import contextlib
import importlib.util
import io
import json
import os
import subprocess
import sys
import threading
import urllib.error
import urllib.request
from http.server import ThreadingHTTPServer
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RACINE))

#: Sortie réelle : le moteur est bavard, ses impressions sont mises de côté.
SORTIE = sys.stdout


def dire(message: str) -> None:
    SORTIE.write(message + "\n")
    SORTIE.flush()


def charger_module(chemin: Path, nom: str):  # noqa: ANN201 - module dynamique
    """Charge un script par son chemin (les noms des outils contiennent des tirets)."""
    specification = importlib.util.spec_from_file_location(nom, chemin)
    module = importlib.util.module_from_spec(specification)
    specification.loader.exec_module(module)
    return module


#: Routes exposées dans api/, telles que les connaît le générateur de fonctions.
ROUTES: tuple[str, ...] = charger_module(
    RACINE / "outils" / "generer-fonctions-api.py", "generer_fonctions_api"
).ROUTES

PAGES = (
    "index.html",
    "ia-societe.html",
    "simulateur.html",
    "documents.html",
    "liens-utiles.html",
    "localisation.html",
    "nous-contacter.html",
    "transparence.html",
    "404.html",
)

#: Statuts acceptés par route : une route paramétrée sans paramètre répond 400,
#: c'est le comportement voulu, pas une panne.
STATUTS_ACCEPTES: dict[str, tuple[int, ...]] = {
    "bulle": (200, 400),
    "donnees": (200, 400),
    "proxy": (200, 400),
}

#: Routes interrogées telles que la page publiée le fait, et statut attendu.
ROUTES_TESTS: dict[str, tuple[str, int]] = {
    "/api/catalogue": ("", 200),
    "/api/contexte": ("?refresh=0", 200),
    "/api/presets": ("", 200),
    "/api/scenarios": ("", 200),
    "/api/simuler": ("", 200),
    "/api/comparer": ("", 200),
    "/api/run?scenario=mandature": ("", 200),
    "/api/bulle?levier=tva_taux_normal": ("", 200),
}

echecs: list[str] = []


def verifier(libelle: str, condition: bool, detail: str = "") -> None:
    dire(f"{'OK   ' if condition else 'ÉCHEC'} {libelle}" + (f" — {detail}" if detail else ""))
    if not condition:
        echecs.append(libelle)


def lancer(script: str, *arguments: str) -> tuple[int, str]:
    resultat = subprocess.run(
        [sys.executable, str(RACINE / "outils" / script), *arguments],
        cwd=RACINE,
        capture_output=True,
        text=True,
        timeout=600,
        check=False,
    )
    return resultat.returncode, (resultat.stdout or resultat.stderr).strip()


def page_a_jour() -> None:
    code, sortie = lancer("construire-simulateur.py", "--verifier")
    verifier("Page du simulateur à jour", code == 0, sortie.splitlines()[-1] if sortie else "")


def fonctions_conformes() -> None:
    code, sortie = lancer("generer-fonctions-api.py", "--verifier")
    verifier("Fonctions api/ conformes au moteur", code == 0, sortie.splitlines()[-1] if sortie else "")


def fichiers_du_site() -> None:
    for page in PAGES:
        chemin = RACINE / page
        verifier(f"Page présente : {page}", chemin.is_file() and chemin.stat().st_size > 500)
    for ressource in ("assets/css/site.css", "assets/js/site.js", "assets/images/logo-mrsc.jpg"):
        verifier(f"Ressource présente : {ressource}", (RACINE / ressource).is_file())
    publiques = [page for page in PAGES if page != "404.html"]
    verifier(
        "Le simulateur est dans la navigation des pages",
        all('href="simulateur.html"' in (RACINE / page).read_text(encoding="utf-8") for page in publiques),
        f"{len(publiques)} pages publiques vérifiées",
    )
    verifier(
        "La page d'accueil renvoie vers le simulateur",
        'href="simulateur/"' in (RACINE / "index.html").read_text(encoding="utf-8"),
    )
    verifier(
        "La page du simulateur est publiée",
        (RACINE / "simulateur" / "index.html").is_file(),
    )


def demander(fichier: Path, chemin: str, methode: str, corps: bytes | None) -> tuple[int, bytes]:
    """Monte une fonction de api/ comme Vercel, l'interroge, puis l'arrête."""
    module = charger_module(fichier, f"api_{fichier.stem}_{methode}")
    module.handler.log_message = lambda *arguments: None  # sortie de test silencieuse
    with ThreadingHTTPServer(("127.0.0.1", 0), module.handler) as serveur:
        threading.Thread(target=serveur.serve_forever, daemon=True).start()
        requete = urllib.request.Request(
            f"http://127.0.0.1:{serveur.server_address[1]}{chemin}", data=corps, method=methode
        )
        if corps:
            requete.add_header("Content-Type", "application/json")
        try:
            with urllib.request.urlopen(requete, timeout=180) as reponse:
                statut, contenu = reponse.status, reponse.read()
        except urllib.error.HTTPError as erreur:
            statut, contenu = erreur.code, erreur.read()
        except (urllib.error.URLError, OSError) as erreur:
            statut, contenu = 0, str(erreur).encode()
        finally:
            serveur.shutdown()
    return statut, contenu


def routes_servies() -> None:
    for route in ROUTES:
        methode = "POST" if route in ("simuler", "donnees") else "GET"
        corps = json.dumps({"parametres": {}, "horizon": 5}).encode() if methode == "POST" else None
        statut, contenu = demander(RACINE / "api" / f"{route}.py", f"/api/{route}", methode, corps)
        acceptes = STATUTS_ACCEPTES.get(route, (200,))
        verifier(
            f"Fonction api/{route}.py sert /api/{route}",
            statut in acceptes,
            f"statut {statut}, {len(contenu)} octets",
        )

    for chemin, (requete, attendu) in ROUTES_TESTS.items():
        nom = chemin.split("?")[0].split("/")[-1]
        statut, contenu = demander(RACINE / "api" / f"{nom}.py", chemin + requete, "GET", None)
        verifier(
            f"Réponse exploitable : {chemin}{requete}",
            statut == attendu and contenu.lstrip()[:1] in (b"{", b"<"),
            f"statut {statut}, {len(contenu)} octets",
        )


def source_distante() -> None:
    """Vérifie la fonction de bascule, face à une source simulée puis injoignable."""
    from http.server import BaseHTTPRequestHandler

    class Stub(BaseHTTPRequestHandler):
        """Fausse source distante, pour un contrôle sans réseau externe."""

        def do_GET(self) -> None:  # noqa: N802 - API stdlib
            _repondre_stub(self)

        def log_message(self, *arguments: object) -> None:  # noqa: N802 - API stdlib
            """Silencieux : c'est un serveur de test."""

    with ThreadingHTTPServer(("127.0.0.1", 0), Stub) as stub:
        threading.Thread(target=stub.serve_forever, daemon=True).start()
        adresse = f"http://127.0.0.1:{stub.server_address[1]}/"

        os.environ["SIMULATEUR_SOURCE_DISTANTE"] = adresse
        statut, contenu = demander(RACINE / "api" / "verifier-source.py", "/api/verifier-source", "GET", None)
        charge = json.loads(contenu or b"{}")
        verifier(
            "Source distante fonctionnelle : la bascule est autorisée",
            statut == 200 and charge.get("disponible") is True and charge.get("page", {}).get("indice_simulateur"),
            f"statut {statut}, disponible={charge.get('disponible')}",
        )

        stub.shutdown()

    os.environ["SIMULATEUR_SOURCE_DISTANTE"] = "http://127.0.0.1:9/"
    statut, contenu = demander(RACINE / "api" / "verifier-source.py", "/api/verifier-source", "GET", None)
    charge = json.loads(contenu or b"{}")
    verifier(
        "Source distante injoignable : bascule refusée sans erreur",
        statut == 200 and charge.get("disponible") is False and bool(charge.get("message")),
        f"statut {statut}, disponible={charge.get('disponible')}",
    )
    os.environ.pop("SIMULATEUR_SOURCE_DISTANTE", None)


def _repondre_stub(soi) -> None:  # noqa: ANN001 - handler HTTP minimal
    """Fausse source distante : une page du moteur et une API qui répond."""
    chemin = soi.path.split("?")[0]
    if chemin in ("/", "/index.html"):
        corps = (
            "<!DOCTYPE html><html lang='fr'><head><title>Simulateur Macro-Politique</title></head>"
            "<body><div id='console-pilotage'></div><p>93 leviers de politique publique</p></body></html>"
        ).encode("utf-8")
        type_mime = "text/html; charset=utf-8"
    elif chemin == "/api/scenarios":
        corps = json.dumps({"scenarios": {"mandature": {"nom": "Plan de mandature"}}}).encode("utf-8")
        type_mime = "application/json; charset=utf-8"
    else:
        soi.send_response(404)
        soi.send_header("Content-Length", "0")
        soi.end_headers()
        return
    soi.send_response(200)
    soi.send_header("Content-Type", type_mime)
    soi.send_header("Content-Length", str(len(corps)))
    soi.end_headers()
    soi.wfile.write(corps)


def main() -> int:
    dire("── Intégration du simulateur au site M.R.S.C ──")
    page_a_jour()
    fonctions_conformes()
    fichiers_du_site()
    # Le moteur écrit des tableaux de simulation : on garde la sortie du test lisible.
    with contextlib.redirect_stdout(io.StringIO()):
        routes_servies()
        source_distante()
    dire("")
    if echecs:
        dire(f"{len(echecs)} contrôle(s) en échec : {', '.join(echecs)}")
        return 1
    dire("Tous les contrôles passent.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
