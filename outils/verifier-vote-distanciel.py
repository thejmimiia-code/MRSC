#!/usr/bin/env python3
"""Vérifie les garde-fous documentaires du chantier de vote distanciel.

Ce script ne teste aucune cryptographie et ne certifie aucun système de vote.
"""

from __future__ import annotations

import sys
import tomllib
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
NOTE = RACINE / "docs" / "rd" / "vote-distanciel-verifiable.md"
PORTEFEUILLE = RACINE / "docs" / "rd" / "portefeuille.toml"

SECTIONS_REQUISES = [
    "## 1. Reformulation de l’objectif",
    "## 2. Questions bloquantes avant toute conception détaillée",
    "## 3. Propriétés à ne pas confondre",
    "## 4. Architecture candidate — à expertiser, pas à développer directement",
    "## 5. Menaces et réponses minimales",
    "## 6. Choix technologique proposé",
    "## 7. Phases et portes de décision",
    "## 8. Critères d’arrêt immédiat",
    "## 9. Décision de cette passe",
]

GARDE_FOUS_REQUIS = [
    "aucun système de vote n’est disponible",
    "Ne pas développer de système de vote réel",
    "aucune identité réelle",
    "Ne jamais inventer de primitive cryptographique",
    "procédure d’annulation",
    "dépouillement à seuil",
    "canal de secours",
]


def principal() -> int:
    texte = NOTE.read_text(encoding="utf-8")
    texte_normalise = texte.casefold()
    manquants = [
        element for element in SECTIONS_REQUISES
        if element.casefold() not in texte_normalise
    ]
    manquants.extend(
        element for element in GARDE_FOUS_REQUIS
        if element.casefold() not in texte_normalise
    )

    with PORTEFEUILLE.open("rb") as fichier:
        initiatives = tomllib.load(fichier).get("initiative", [])
    votes = [item for item in initiatives if item.get("id") == "vote-distanciel-verifiable"]
    if len(votes) != 1:
        manquants.append("initiative unique vote-distanciel-verifiable")
    else:
        initiative = votes[0]
        if initiative.get("etat") != "a-cadrer":
            manquants.append("initiative maintenue à l’état a-cadrer")
        if initiative.get("priorite") != "P0":
            manquants.append("initiative classée P0")
        action = initiative.get("prochaine_action", "")
        if "aucun bulletin réel" not in action:
            manquants.append("interdiction de bulletin réel dans la prochaine action")

    if manquants:
        print("Cadrage du vote distanciel incomplet :", file=sys.stderr)
        for element in manquants:
            print(f"- {element}", file=sys.stderr)
        return 1

    print(
        "Cadrage du vote distanciel présent : 9 sections, initiative P0 à cadrer, "
        "aucune identité ni bulletin réel autorisé."
    )
    return 0


if __name__ == "__main__":
    try:
        sys.exit(principal())
    except (OSError, tomllib.TOMLDecodeError) as erreur:
        print(f"Cadrage du vote distanciel impossible à vérifier : {erreur}", file=sys.stderr)
        sys.exit(1)
