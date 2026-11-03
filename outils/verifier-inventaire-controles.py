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
   annoncé pour un statut qui en exige un existe vraiment ;
4. **comptes** — le tableau « Combien » et la phrase « N contrôles sur M » sont
   confrontés aux lignes réelles. Ces nombres étaient recopiés à la main et
   avaient pris six unités de retard ; un total écrit à la main n'est pas un
   contrôle, c'est une opinion datée.

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
#: Ligne du tableau « Combien », sous la forme `| \`banc\` | 30 | … |`.
COMPTE = re.compile(r"^\|\s*`(?P<statut>[a-z-]+)`\s*\|\s*(?P<nombre>\d+)\s*\|")
#: La phrase de synthèse : « **48 contrôles sur 48** ».
PHRASE = re.compile(r"\*\*(?P<avec>\d+) contrôles sur (?P<total>\d+)\*\*")


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

    erreurs.extend(controler_comptes(texte, entrees))
    return erreurs


def compter(entrees: list[dict[str, str]]) -> dict[str, int]:
    """Nombre de lignes par statut, lu dans le tableau de l'inventaire."""
    comptes: dict[str, int] = {statut: 0 for statut in STATUTS}
    for entree in entrees:
        comptes[entree["statut"]] = comptes.get(entree["statut"], 0) + 1
    return comptes


def controler_comptes(texte: str, entrees: list[dict[str, str]]) -> list[str]:
    """Confronte les totaux écrits dans le document aux lignes réelles.

    Un document qui annonce « 22 » quand le tableau en porte 30 n'est pas un
    document faux : c'est un document daté, présenté comme s'il était à jour.
    """
    erreurs: list[str] = []
    comptes = compter(entrees)
    annonces: dict[str, int] = {}
    for ligne in texte.splitlines():
        trouve = COMPTE.match(ligne)
        if trouve:
            statut, nombre = trouve.group("statut"), int(trouve.group("nombre"))
            if statut not in STATUTS:
                erreurs.append(f"inventaire : le tableau « Combien » annonce un statut inconnu « {statut} »")
                continue
            annonces[statut] = nombre
            if nombre != comptes.get(statut, 0):
                erreurs.append(
                    f"inventaire : le tableau « Combien » annonce {nombre} « {statut} », "
                    f"le tableau des outils en compte {comptes.get(statut, 0)}"
                )
    oublies = sorted(statut for statut in STATUTS if statut not in annonces)
    if oublies:
        erreurs.append(
            "inventaire : le tableau « Combien » omet " + ", ".join(f"« {s} »" for s in oublies)
            + " — un statut absent se lit comme un statut à zéro"
        )

    phrase = PHRASE.search(texte)
    total = sum(comptes.values()) - comptes.get("hors-portee", 0)
    avec = total - comptes.get("test-en-soi", 0) - comptes.get("aucun-test", 0)
    if not phrase:
        erreurs.append("inventaire : la phrase « N contrôles sur N » a disparu — les totaux ne sont plus confrontés")
    else:
        if int(phrase.group("avec")) != avec:
            erreurs.append(
                f"inventaire : la phrase annonce {phrase.group('avec')} contrôles éprouvés, "
                f"l'inventaire en compte {avec}"
            )
        if int(phrase.group("total")) != total:
            erreurs.append(
                f"inventaire : la phrase annonce {phrase.group('total')} contrôles, "
                f"l'inventaire en compte {total} hors « hors-portee »"
            )
    return erreurs


def resume() -> str:
    texte = INVENTAIRE.read_text(encoding="utf-8")
    comptes = compter(lignes_inventaire(texte))
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
