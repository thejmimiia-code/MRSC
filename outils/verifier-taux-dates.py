#!/usr/bin/env python3
"""Refuse une règle chiffrée (taux, plafond, montant légal) écrite sans sa date.

La carte de sujet `docs/rd/sujet-revenus-salaire-impots.md` a fixé une règle le
28 octobre 2026 : **un taux daté n'entre pas dans une fiche**. Les taux et
plafonds de cotisations changent à chaque exercice ; une fiche qui écrirait
« la CSG est de 9,2 % » deviendrait fausse au premier changement sans qu'aucun
contrôle du dépôt ne le voie. `auditer-prototypes.py` vérifie la forme des
champs, `confronter-sources.py` cherche des ancres lexicales : aucun des deux ne
compare un barème à sa date.

Ce contrôle est volontairement étroit, parce qu'une règle large condamnerait les
fiches de mathématiques : il ne regarde qu'une phrase qui réunit **un chiffre en
pourcentage ou en euros** et **un terme de droit, de fiscalité ou de protection
sociale**. Une telle phrase doit alors porter son année, ou dire qu'elle parle
d'un exemple inventé. Et une fiche qui énonce une règle datée doit citer au moins
une source dont la date de contrôle des droits est consignée.

Ce qu'il ne fait pas : il ne juge pas si le chiffre est exact, il ne dit pas que
la fiche est relue, et il ne remplace aucune relecture compétente. Une phrase
verte ici peut être fausse.

Usage :
    python3 outils/verifier-taux-dates.py                  # 0 si tout est conforme
    python3 outils/verifier-taux-dates.py --fiche econ-lire-facture
    python3 outils/verifier-taux-dates.py --catalogue autre.toml
"""

from __future__ import annotations

import argparse
import re
import sys
import tomllib
from pathlib import Path
from typing import Iterable

RACINE = Path(__file__).resolve().parent.parent
CATALOGUE = RACINE / "docs" / "apprentissage" / "catalogue.toml"

#: Champs de contenu lus dans le catalogue. Les métadonnées (titre, matière,
#: niveau) ne portent pas de règle chiffrée : les inclure n'ajouterait que du bruit.
CHAMPS_TEXTE = (
    "resume", "objectif", "situation", "analogie", "limite_analogie",
    "exercice", "aide", "transferer",
)
CHAMPS_LISTE = ("notions", "demarche", "correction", "a_retenir")

#: Vocabulaire du droit, de la fiscalité et de la protection sociale. Hors de
#: cette liste, un pourcentage est un contenu pédagogique ordinaire : « 20 %
#: d'une remise » n'est pas une règle qui vieillit.
TERMES_REGLE = re.compile(
    r"\b(?:cotisations?|CSG|CRDS|pr[ée]l[èe]vements?|imp[oô]ts?|taxes?|TVA|taux"
    r"|plafonds?|bar[èe]mes?|retenues?|contributions?|amendes?|majorations?"
    r"|p[ée]nalit[ée]s?|abattements?|exon[ée]rations?|SMIC"
    r"|salaire minimum|revenu fiscal)\b",
    re.IGNORECASE,
)

#: Un chiffre suivi d'une unité monétaire ou d'un pourcentage. Les milliers sont
#: admis avec une espace ordinaire, insécable ou fine, comme les écrit le site.
CHIFFRE = re.compile(
    r"(?<![\w.,])\d{1,3}(?:[ \u00a0\u202f]\d{3})*(?:[.,]\d+)?\s?(?:%|€|euros?\b|centimes?\b)"
)

#: Une année explicite dans la phrase : c'est elle qui date la règle.
ANNEE = re.compile(r"\b(?:19|20)\d{2}\b")

#: Un exemple assumé comme inventé n'a pas besoin d'être daté : la fiche ne dit
#: pas que la règle vaut, elle dit qu'elle illustre.
MARQUEUR_EXEMPLE = re.compile(
    r"\b(?:ficti(?:f|ve|fs|ves)|invent[ée]e?s?|imaginaire|simul[ée]e?s?)\b",
    re.IGNORECASE,
)


def phrases(texte: str) -> Iterable[str]:
    """Découpe en phrases sans casser « 9,2 % » ni une abréviation courante."""
    return (morceau.strip() for morceau in re.split(r"(?<=[.!?])\s+", texte) if morceau.strip())


def textes_de(fiche: dict) -> list[tuple[str, str]]:
    """Rend les textes de contenu d'une fiche, avec le nom du champ qui les porte."""
    textes = [(champ, fiche[champ]) for champ in CHAMPS_TEXTE if isinstance(fiche.get(champ), str)]
    for champ in CHAMPS_LISTE:
        for index, valeur in enumerate(fiche.get(champ) or []):
            if isinstance(valeur, str):
                textes.append((f"{champ}[{index}]", valeur))
    return textes


def regle_chiffree(phrase: str) -> bool:
    """Vrai si la phrase réunit un chiffre monétaire ou en pourcentage et un terme de règle."""
    return bool(CHIFFRE.search(phrase) and TERMES_REGLE.search(phrase))


def source_datee(fiche: dict) -> bool:
    """Vrai si la fiche consigne la date de contrôle des droits d'au moins une source."""
    return any(
        isinstance(source, dict) and source.get("droits_controles_le")
        for source in fiche.get("sources") or []
    )


def controler(fiches: Iterable[dict]) -> tuple[list[str], dict[str, int]]:
    """Rend les défauts trouvés et les compteurs qui les expliquent."""
    defauts: list[str] = []
    compteurs = {"fiches": 0, "regles_datées": 0, "defauts": 0}
    for fiche in fiches:
        compteurs["fiches"] += 1
        identifiant = fiche.get("id", "?")
        regle_datee_ici = False
        for champ, texte in textes_de(fiche):
            for phrase in phrases(texte):
                if not regle_chiffree(phrase):
                    continue
                if ANNEE.search(phrase):
                    regle_datee_ici = True
                    continue
                if MARQUEUR_EXEMPLE.search(phrase):
                    continue
                compteurs["defauts"] += 1
                extrait = phrase if len(phrase) <= 180 else phrase[:177] + "…"
                defauts.append(
                    f"{identifiant} — {champ} : règle chiffrée sans son année — « {extrait} »"
                )
        if regle_datee_ici:
            compteurs["regles_datées"] += 1
            if not source_datee(fiche):
                compteurs["defauts"] += 1
                defauts.append(
                    f"{identifiant} — la fiche énonce une règle chiffrée datée sans citer "
                    "aucune source dont la date de contrôle des droits est consignée "
                    "(champ droits_controles_le)"
                )
    return defauts, compteurs


def charger(catalogue: Path = CATALOGUE) -> list[dict]:
    with catalogue.open("rb") as fichier:
        return tomllib.load(fichier).get("fiche", [])


def main(argv: list[str] | None = None) -> int:
    analyseur = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    analyseur.add_argument("--catalogue", type=Path, default=CATALOGUE)
    analyseur.add_argument("--fiche", help="ne contrôle qu'une fiche, par identifiant")
    argument = analyseur.parse_args(argv)

    fiches = charger(argument.catalogue)
    if argument.fiche:
        fiches = [fiche for fiche in fiches if fiche.get("id") == argument.fiche]
        if not fiches:
            print(f"Fiche inconnue : {argument.fiche}", file=sys.stderr)
            return 2

    defauts, compteurs = controler(fiches)
    if defauts:
        print("ÉCHEC — règles chiffrées sans date", file=sys.stderr)
        for defaut in defauts:
            print(f"    {defaut}", file=sys.stderr)
        print(
            f"\n{compteurs['defauts']} défaut(s) sur {compteurs['fiches']} fiche(s). "
            "Ajouter l'année de la règle, ou écrire qu'il s'agit d'un exemple inventé, "
            "et citer une source dont droits_controles_le est renseigné. "
            "Voir docs/rd/sujet-revenus-salaire-impots.md.",
            file=sys.stderr,
        )
        return 1

    print(
        f"Taux et montants légaux : {compteurs['fiches']} fiche(s) contrôlée(s), "
        f"{compteurs['regles_datées']} énonçant une règle chiffrée datée, 0 défaut. "
        "Ce contrôle ne dit rien de l'exactitude des chiffres ni d'une relecture."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
