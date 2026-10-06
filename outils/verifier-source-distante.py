#!/usr/bin/env python3
"""La version en ligne du simulateur est-elle utilisable depuis le site ?

Le site sait basculer automatiquement sur la version en développement du
simulateur (source distante) *si* celle-ci expose bien une API de calcul — sinon
il garde la copie embarquée du moteur. Ce script fait la même vérification
depuis votre machine, avec les mêmes règles que la fonction
`api/verifier-source.py` (une seule implémentation, donc pas de divergence).

Usage :
    python3 outils/verifier-source-distante.py [--url https://…]

Sortie : 0 si la source distante est fonctionnelle, 1 sinon (la raison est
afficheé). Idéal avant de communiquer l'adresse, ou après une mise à jour du
projet amont.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent


def charger_fonction():  # noqa: ANN201 - module dynamique (nom de fichier avec tiret)
    specification = importlib.util.spec_from_file_location(
        "verifier_source", RACINE / "api" / "verifier-source.py"
    )
    module = importlib.util.module_from_spec(specification)
    specification.loader.exec_module(module)
    return module


def main() -> int:
    analyseur = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    analyseur.add_argument("--url", help="adresse à vérifier (par défaut : data-source-distante de simulateur.html)")
    analyseur.add_argument("--json", action="store_true", help="sortie JSON brute")
    options = analyseur.parse_args()

    fonction = charger_fonction()
    source = options.url or fonction.adresse_configurée()
    if not source:
        print("Aucune source distante configurée (attribut data-source-distante de simulateur.html).")
        return 1

    resultat = fonction.verifier(source)
    if options.json:
        print(json.dumps(resultat, ensure_ascii=False, indent=2))
        return 0 if resultat["disponible"] else 1

    print(f"Source distante : {resultat['source']}")
    print(f"  page : statut {resultat['page']['statut']}, page du moteur : {'oui' if resultat['page']['indice_simulateur'] else 'non'}")
    api = resultat["api"]
    if api["route"]:
        print(f"  api  : {api['route']} → statut {api['statut']}, moteur : {'oui' if api['indice_moteur'] else 'non'}")
    print()
    print(resultat["message"])
    print()
    if resultat["disponible"]:
        print("Conséquence : le site affiche la version en développement, et la copie embarquée")
        print("ne sert plus que de repli. Rien à faire.")
        return 0

    print("Conséquence : le site garde la copie embarquée du moteur (qui fonctionne).")
    print("Pour que la version en ligne prenne le relais, il faut que le projet amont expose")
    print("sa page *et* son API de calcul — voir docs/integration-simulateur.md, § 5.")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
