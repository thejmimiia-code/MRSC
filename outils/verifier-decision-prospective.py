#!/usr/bin/env python3
"""Vérifie les faits internes du brief prospectif sans prendre la décision.

Ce contrôle détecte les nombres devenus incohérents avec les sources du dépôt.
Il ne valide ni les scénarios, ni leur pertinence, ni une option A/B/C.
"""

from __future__ import annotations

import re
import sys
import tomllib
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
BRIEF = RACINE / "docs" / "rd" / "decision-prospective.md"
CATALOGUE = RACINE / "docs" / "apprentissage" / "catalogue.toml"
PORTEFEUILLE = RACINE / "docs" / "rd" / "portefeuille.toml"
APPRENDRE = RACINE / "apprendre.html"


def charger_toml(chemin: Path) -> dict:
    with chemin.open("rb") as fichier:
        return tomllib.load(fichier)


def compter_questions_boussole(html: str) -> int:
    bloc = re.search(r'id="boussole-savoirs"(?P<contenu>.*?)(?:</section>|<section\b)', html, re.S)
    if not bloc:
        raise ValueError("section #boussole-savoirs introuvable")
    liste = re.search(r'<ol class="knowledge-compass">(?P<contenu>.*?)</ol>', bloc.group("contenu"), re.S)
    if not liste:
        raise ValueError("liste .knowledge-compass introuvable")
    return len(re.findall(r"<li\b", liste.group("contenu")))


def principal() -> int:
    brief = BRIEF.read_text(encoding="utf-8")
    catalogue = charger_toml(CATALOGUE).get("fiche", [])
    initiatives = charger_toml(PORTEFEUILLE).get("initiative", [])
    fiches = len(catalogue)
    prototypes = sum(fiche.get("statut_editorial") == "Prototype à relire" for fiche in catalogue)
    domaines = len({fiche.get("domaine") for fiche in catalogue if fiche.get("domaine")})
    total_initiatives = len(initiatives)
    p0 = sum(initiative.get("priorite") == "P0" for initiative in initiatives)
    questions = compter_questions_boussole(APPRENDRE.read_text(encoding="utf-8"))

    attentes = {
        "fiches et domaines": rf"\| Fiches d'apprentissage publiées \| {fiches} dans {domaines} domaines \|",
        "prototypes": rf"\| Fiches explicitement « prototypes à relire » \| \*\*{prototypes}\*\* \|",
        "initiatives": rf"\| Initiatives R&D suivies \| {total_initiatives}, dont {p0} en priorité P0 \|",
        "Boussole": rf"\| Boussole publiée \| {questions} questions statiques,",
    }
    erreurs = [nom for nom, motif in attentes.items() if not re.search(motif, brief)]
    if erreurs:
        print("Brief prospectif désynchronisé : " + ", ".join(erreurs), file=sys.stderr)
        print(
            f"Valeurs calculées : {fiches} fiches dans {domaines} domaines, {prototypes} prototypes, "
            f"{total_initiatives} initiatives dont {p0} P0, {questions} questions.",
            file=sys.stderr,
        )
        return 1

    print(
        f"Brief prospectif synchronisé : {fiches} fiches dans {domaines} domaines, {prototypes} prototypes, "
        f"{total_initiatives} initiatives dont {p0} P0, {questions} questions."
    )
    return 0


if __name__ == "__main__":
    sys.exit(principal())
