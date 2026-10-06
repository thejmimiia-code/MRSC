#!/usr/bin/env python3
"""Génère les fonctions Vercel de `api/` à partir des routes du simulateur.

Sur Vercel, chaque fichier `.py` de `api/` devient une route (« file-based
Python functions ») et doit exposer une classe `handler` dérivant de
`BaseHTTPRequestHandler` : d'où un fichier par route du moteur, chacun
déclarant sa route à `simulateur.pont_api.FonctionAPI`.

Usage :
    python3 outils/generer-fonctions-api.py [--verifier]

`--verifier` compare les fichiers présents aux routes réellement servies par
`simulateur/dashboard.py` et sort en erreur en cas d'écart (utilisable en CI).
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RACINE))

#: Routes du moteur à exposer (voir `simulateur/dashboard.py`, do_GET/do_POST).
ROUTES: tuple[str, ...] = (
    "catalogue",
    "contexte",
    "donnees",
    "simuler",
    "comparer",
    "presets",
    "bulles",
    "bulle",
    "proxy",
    "run",
    "scenarios",
    "export",
)

GABARIT = '''"""Fonction Vercel — route {route} du simulateur.

Fichier généré par `outils/generer-fonctions-api.py` : ne pas modifier à la
main. Toute la logique vient du moteur, voir `simulateur/pont_api.py`.
"""

import pathlib
import sys

RACINE = pathlib.Path(__file__).resolve().parent.parent
if str(RACINE) not in sys.path:
    sys.path.insert(0, str(RACINE))

from simulateur.pont_api import FonctionAPI  # noqa: E402


class handler(FonctionAPI):
    ROUTE = "/api/{route}"
'''


def routes_du_moteur() -> set[str]:
    """Routes réellement servies, lues dans le source du moteur."""
    source = (RACINE / "simulateur" / "dashboard.py").read_text(encoding="utf-8")
    return {nom for nom in re.findall(r'chemin == "(/api/[a-z]+)"', source)}


def main() -> int:
    analyseur = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    analyseur.add_argument("--verifier", action="store_true", help="ne rien écrire, signaler les écarts")
    options = analyseur.parse_args()

    attendues = {f"/api/{route}" for route in ROUTES}
    servies = routes_du_moteur()
    manquantes = sorted(servies - attendues)
    inconnues = sorted(attendues - servies)
    if manquantes or inconnues:
        print("Désaccord entre api/ et le moteur :")
        if manquantes:
            print(f"  routes du moteur non exposées : {', '.join(manquantes)}")
        if inconnues:
            print(f"  routes exposées mais absentes du moteur : {', '.join(inconnues)}")
        return 1

    dossier = RACINE / "api"
    for nom in sorted(dossier.glob("*.py")):
        if nom.stem not in ROUTES:
            print(f"  fichier inattendu dans api/ : {nom.name}")

    if options.verifier:
        absents = [route for route in ROUTES if not (dossier / f"{route}.py").is_file()]
        if absents:
            print(f"Fonctions manquantes dans api/ : {', '.join(absents)}")
            return 1
        print(f"{len(ROUTES)} routes exposées et présentes dans api/.")
        return 0

    dossier.mkdir(exist_ok=True)
    for route in ROUTES:
        (dossier / f"{route}.py").write_text(GABARIT.format(route=route), encoding="utf-8")
    print(f"{len(ROUTES)} fonctions écrites dans api/ : {', '.join(ROUTES)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
