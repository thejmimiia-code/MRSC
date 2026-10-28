#!/usr/bin/env python3
"""Vérifie que l'inventaire des contrôles reste complet et honnête.

`docs/rd/inventaire-controles.md` répond, outil par outil, à une question :
qu'est-ce qui prouve que ce contrôle peut échouer ? Un inventaire tenu à la main
pourrit en une semaine : un outil ajouté n'y entre pas, un statut reste écrit
après la disparition du test qu'il décrivait.

Ce contrôle ne juge pas les statuts. Il vérifie trois choses mécaniques :

1. **couverture** — tout fichier d'`outils/` (`.py`, `.mjs`, `.cjs`) hors
   `test_*` et `__*` figure dans l'inventaire, une fois ;
2. **existence** — tout chemin cité dans l'inventaire existe dans le dépôt ;
3. **vocabulaire** — le statut est l'un des six admis, et le fichier de test
   annoncé pour un statut qui en exige un existe vraiment.

Il ne dit pas qu'un statut `banc` est mérité : c'est la lecture du banc qui le
dit. Il empêche seulement l'inventaire de mentir par omission.

Usage :
    python3 outils/verifier-inventaire-controles.py
"""

from __future__ import annotations

import os
import re
import sys
from pathlib import Path

#: Racine lue par le contrôle. La surcharge sert au banc de mutation
#: (`outils/test_verifier_inventaire_controles.py`), qui casse l'inventaire dans
#: une copie du dépôt plutôt que dans l'arbre de travail.
RACINE = Path(os.environ.get("MRSC_RACINE") or Path(__file__).resolve().parent.parent).resolve()
INVENTAIRE = RACINE / "docs" / "rd" / "inventaire-controles.md"
OUTILS = RACINE / "outils"

#: Statuts admis et ce qu'ils exigent : au moins un banc ou un test cité pour
#: les trois premiers, aucun pour les deux derniers.
STATUTS = {
    "banc": True,
    "faute-en-memoire": True,
    "test": True,
    "test-en-soi": False,
    "aucun-test": False,
    "hors-portee": False,
}

LIGNE = re.compile(r"^\|\s*`(?P<outil>outils/[^`]+)`\s*\|(?P<reste>.+)\|\s*`(?P<statut>[a-z-]+)`\s*\|\s*$")
CHEMIN = re.compile(r"`(?P<chemin>(?:outils|docs|assets)/[^`]+?\.(?:py|mjs|cjs|md|toml|html|css|js))`")


def outils_reellement_presents() -> set[str]:
    """Tous les fichiers d'`outils/` qui ne sont pas eux-mêmes des tests."""
    presents = set()
    for chemin in OUTILS.iterdir():
        if chemin.suffix not in {".py", ".mjs", ".cjs"}:
            continue
        if chemin.name.startswith(("test_", "__")):
            continue
        presents.add(f"outils/{chemin.name}")
    return presents


def lignes_inventaire(texte: str) -> list[dict[str, str]]:
    entrees = []
    for ligne in texte.splitlines():
        trouve = LIGNE.match(ligne)
        if trouve:
            entrees.append(trouve.groupdict())
    return entrees


def controler() -> list[str]:
    erreurs: list[str] = []
    if not INVENTAIRE.is_file():
        return [f"inventaire absent : {INVENTAIRE.relative_to(RACINE)}"]

    texte = INVENTAIRE.read_text(encoding="utf-8")
    entrees = lignes_inventaire(texte)
    if not entrees:
        return ["inventaire illisible : aucune ligne de tableau reconnue"]

    vus: dict[str, str] = {}
    for entree in entrees:
        outil, statut = entree["outil"], entree["statut"]
        if outil in vus:
            erreurs.append(f"{outil} : inscrit deux fois dans l'inventaire")
        vus[outil] = statut
        if not (RACINE / outil).is_file():
            erreurs.append(f"{outil} : inscrit dans l'inventaire mais absent du dépôt")
        if statut not in STATUTS:
            erreurs.append(f"{outil} : statut inconnu « {statut} » (admis : {', '.join(STATUTS)})")
            continue
        if STATUTS[statut]:
            # `.mjs` depuis le 28 octobre 2026 : `test_auditer_criteres_22.mjs` éprouve
            # un script Node, et l'inventaire refusait de le citer.
            cites = re.findall(r"`(test_[a-z0-9_-]+\.(?:py|cjs|mjs))`", entree["reste"])
            if not cites:
                erreurs.append(
                    f"{outil} : statut « {statut} » sans fichier de test cité pour le justifier"
                )
            for cite in cites:
                if not (OUTILS / cite).is_file():
                    erreurs.append(f"{outil} : le test cité « {cite} » n'existe pas")

    manquants = sorted(outils_reellement_presents() - set(vus))
    if manquants:
        erreurs.append(
            "outils absents de l'inventaire : " + ", ".join(manquants)
            + " — ajouter une ligne avec son rôle, sa garde actuelle et son statut"
        )

    for chemin in {trouve.group("chemin") for trouve in CHEMIN.finditer(texte)}:
        if not (RACINE / chemin).exists():
            erreurs.append(f"inventaire : chemin cité introuvable « {chemin} »")

    return erreurs


def resume() -> str:
    texte = INVENTAIRE.read_text(encoding="utf-8")
    comptes: dict[str, int] = {}
    for entree in lignes_inventaire(texte):
        comptes[entree["statut"]] = comptes.get(entree["statut"], 0) + 1
    detail = ", ".join(f"{statut} : {comptes.get(statut, 0)}" for statut in STATUTS)
    return f"Inventaire des contrôles : {sum(comptes.values())} outils — {detail}"


def main() -> int:
    erreurs = controler()
    if erreurs:
        print("ÉCHEC — inventaire des contrôles", file=sys.stderr)
        for erreur in erreurs:
            print(f"    {erreur}", file=sys.stderr)
        return 1
    print(resume())
    print("Un statut « aucun-test » n'est pas un défaut : c'est du travail nommé.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
