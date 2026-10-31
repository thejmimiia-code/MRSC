#!/usr/bin/env python3
"""Nomme, dans une annotation GitHub, ce que la mesure navigateur a refusé.

Le job `graphismes` mesure trois visuels dans un vrai navigateur et écrit ses
résultats dans des fichiers JSON ; il échoue ensuite sur un code de sortie. Le
31 octobre 2026, ce job est tombé en rouge et **personne ne pouvait dire
pourquoi** : les journaux et les artefacts vivent sur un stockage que l'atelier
n'atteint pas, et l'étape n'émettait aucune annotation. Un contrôle qui échoue
sans dire ce qu'il a vu oblige à relancer à l'aveugle.

Ce script lit les relevés et imprime une ligne `::error title=...::...` par
constat. GitHub les transforme en annotations, lisibles par l'API — donc par un
mainteneur qui n'a pas les journaux. Il ne juge rien : il recopie ce que les
mesures ont écrit, et dit quand il ne trouve rien.

Usage :
    python3 outils/annoncer-echec-graphismes.py <dossier des relevés>
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

#: Longueur maximale d'une annotation GitHub.
LONGUEUR = 900


def releves(dossier: Path) -> list[Path]:
    """Les relevés JSON du dossier, triés — y compris ceux des passes mutées."""
    if not dossier.is_dir():
        return []
    return sorted(chemin for chemin in dossier.glob("*.json") if chemin.is_file())


def constats(chemin: Path) -> list[str]:
    """Les erreurs nommées par un relevé, ou le fait qu'il n'en porte aucune."""
    try:
        donnees = json.loads(chemin.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as erreur:
        return [f"{chemin.name} : illisible ({erreur})"]
    if not isinstance(donnees, dict):
        return [f"{chemin.name} : forme inattendue"]
    erreurs = donnees.get("erreurs")
    if isinstance(erreurs, list) and erreurs:
        lignes = []
        for erreur in erreurs[:6]:
            if isinstance(erreur, dict):
                morceau = ", ".join(f"{cle}={valeur}" for cle, valeur in list(erreur.items())[:6])
            else:
                morceau = str(erreur)
            lignes.append(f"{chemin.name} : {morceau}")
        if len(erreurs) > 6:
            lignes.append(f"{chemin.name} : … {len(erreurs) - 6} autre(s)")
        return lignes
    return [
        f"{chemin.name} : aucun constat écrit — l'échec vient d'ailleurs "
        "(une assertion du script, pas d'une mesure)"
    ]


def annoncer(dossier: Path) -> int:
    fichiers = releves(dossier)
    if not fichiers:
        print(
            f"::error title=Graphismes::aucun relevé dans {dossier} — "
            "la mesure n'a pas tourné ou n'a rien écrit"
        )
        return 0
    for chemin in fichiers:
        for constat in constats(chemin):
            print(f"::error title=Graphismes::{constat[:LONGUEUR]}")
    return 0


def principal(arguments: list[str]) -> int:
    if len(arguments) != 1:
        print(__doc__, file=sys.stderr)
        return 2
    return annoncer(Path(arguments[0]))


if __name__ == "__main__":
    sys.exit(principal(sys.argv[1:]))
