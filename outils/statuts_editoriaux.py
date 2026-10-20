"""Statuts éditoriaux du catalogue : une seule définition, importée partout.

Une fiche peut porter deux statuts explicites, et deux seulement :

- « Prototype à relire » — la fiche existe, elle est publiée, mais aucune
  relecture humaine n'est consignée. C'est le cas de toutes les fiches de
  développement à ce jour.
- « Relu — relecture consignée » — une relecture humaine figure dans
  `docs/apprentissage/relectures.toml` avec un verdict « conforme ».
  Ce statut ne vaut **pas** publication validée : il dit seulement qu'une
  personne a relu, quand, sur quel périmètre et avec quelles objections.

Les fiches sans statut sont les entrées du corpus initial : leur absence de
marqueur ne vaut pas validation non plus.

Ce module existe pour qu'aucun script ne compare une chaîne écrite à la main ni
ne compte « toute fiche portant un statut » comme si elle était un prototype.
"""

from __future__ import annotations

PROTOTYPE = "Prototype à relire"
RELU = "Relu — relecture consignée"
STATUTS = (PROTOTYPE, RELU)


def est_prototype(fiche: dict) -> bool:
    """Vrai si la fiche attend encore une relecture humaine consignée."""
    return fiche.get("statut_editorial") == PROTOTYPE


def est_relue(fiche: dict) -> bool:
    """Vrai si une relecture conforme est consignée pour cette fiche."""
    return fiche.get("statut_editorial") == RELU


def porte_un_statut(fiche: dict) -> bool:
    """Vrai si la fiche porte l'un des deux statuts explicites connus."""
    return fiche.get("statut_editorial") in STATUTS


def compter(fiches: list[dict]) -> dict[str, int]:
    """Compte prototype, relues et entrées initiales, sans jamais les confondre."""
    prototypes = sum(1 for fiche in fiches if est_prototype(fiche))
    relues = sum(1 for fiche in fiches if est_relue(fiche))
    return {
        "total": len(fiches),
        "prototypes": prototypes,
        "relues": relues,
        "initiales": len(fiches) - prototypes - relues,
    }
