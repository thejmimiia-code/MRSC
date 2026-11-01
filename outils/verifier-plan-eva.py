#!/usr/bin/env python3
"""Vérifie le plan d'ÉVA : aucune capacité sans test, aucun refus sans condition.

Un plan de recherche court toujours le même risque : la phase agréable passe
« fait » parce qu'elle a un document, et la phase impossible devient une phrase
qui a l'air d'un engagement. Ce contrôle rend trois fautes mécaniques :

1. **une capacité annoncée sans preuve** — statut `fait` sans fichier de preuve,
   sans test, ou sans citation au journal ; `en-cours` sans test ;
2. **un refus sans porte de sortie** — `hors-portee` ou `en-attente` sans
   condition de révision, c'est-à-dire un abandon déguisé en prudence ;
3. **une incohérence de structure** — dépendance inconnue, cycle, branche du
   portefeuille que le plan ne sert pas, date future, ou une phase déclarée
   faite alors que ce dont elle dépend ne l'est pas.

Il ne juge pas le contenu : il vérifie qu'une phrase qui prétend quelque chose a
un endroit où être contredite. La lecture du test, elle, reste humaine — et
`docs/rd/inventaire-controles.md` le dit de chaque contrôle.

Codes de sortie : 0 accord, 1 refus motivé, 2 plan ou portefeuille illisible.

Usage :
    python3 outils/verifier-plan-eva.py
"""

from __future__ import annotations

import datetime as dt
import os
import re
import sys
import tomllib
from pathlib import Path

RACINE = Path(os.environ.get("MRSC_RACINE") or Path(__file__).resolve().parent.parent).resolve()
PLAN = Path("docs/rd/eva/plan.toml")
PORTEFEUILLE = Path("docs/rd/portefeuille.toml")
JOURNAL = Path("docs/rd/journal.md")

HORIZONS = {"court", "moyen", "long"}
STATUTS = {"fait", "en-cours", "a-faire", "en-attente", "hors-portee"}
#: Statuts qui prétendent quelque chose : ils exigent un test qui puisse les
#: contredire. Les deux autres sont des refus, et un refus n'a pas de test.
STATUTS_PROUVES = {"fait", "en-cours"}
STATUTS_REFUSES = {"en-attente", "hors-portee"}
CHAMPS = ("id", "titre", "horizon", "statut", "objectif", "limite")


class SourceIllisible(Exception):
    """Un fichier du plan manque ou ne se lit pas : on ne devine pas."""


def lire(chemin: Path, quoi: str) -> str:
    if not chemin.is_file():
        raise SourceIllisible(f"{quoi} introuvable : {chemin}")
    try:
        return chemin.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as erreur:
        raise SourceIllisible(f"{quoi} illisible : {chemin} ({erreur})") from erreur


def charger(chemin: Path, quoi: str) -> dict:
    texte = lire(chemin, quoi)
    try:
        return tomllib.loads(texte)
    except tomllib.TOMLDecodeError as erreur:
        raise SourceIllisible(f"{quoi} illisible : {chemin} ({erreur})") from erreur


def cycles(phases: dict[str, list[str]]) -> list[str]:
    """Les cycles de dépendances, nommés par leur chemin."""
    trouves: list[str] = []
    etat: dict[str, int] = {}

    def visiter(noeud: str, chemin: list[str]) -> None:
        if etat.get(noeud) == 1:
            debut = chemin.index(noeud) if noeud in chemin else 0
            trouves.append(" → ".join(chemin[debut:] + [noeud]))
            return
        if etat.get(noeud) == 2:
            return
        etat[noeud] = 1
        for suivant in phases.get(noeud, []):
            if suivant in phases:
                visiter(suivant, chemin + [noeud])
        etat[noeud] = 2

    for noeud in sorted(phases):
        visiter(noeud, [])
    return trouves


def verifier(racine: Path) -> list[str]:
    plan = charger(racine / PLAN, "plan")
    portefeuille = charger(racine / PORTEFEUILLE, "portefeuille")
    journal = lire(racine / JOURNAL, "journal")
    erreurs: list[str] = []

    meta = plan.get("meta") or {}
    if not meta:
        erreurs.append("aucun bloc [meta] : le plan n'est pas daté")
    for champ in ("cadre", "fiction", "hors_plan"):
        if not meta.get(champ):
            erreurs.append(f"[meta] : `{champ}` manquant — ce que le plan déclare ne pas décider")
    date_meta = str(meta.get("date") or "")
    if re.fullmatch(r"\d{4}-\d{2}-\d{2}", date_meta):
        if dt.date.fromisoformat(date_meta) > dt.date.today():
            erreurs.append(f"[meta] : date {date_meta} dans le futur")
    else:
        erreurs.append(f"[meta] : date `{date_meta}` illisible (attendu AAAA-MM-JJ)")

    phases = plan.get("phase") or []
    if not phases:
        erreurs.append("aucune [[phase]] : un plan vide passerait pour un plan complet")

    initiatives = [str(i.get("id")) for i in portefeuille.get("initiative") or [] if i.get("id")]
    connues = set(initiatives)
    servies: set[str] = set()
    par_id: dict[str, dict] = {}

    for phase in phases:
        identifiant = str(phase.get("id") or "")
        if not identifiant:
            erreurs.append("une phase n'a pas d'identifiant")
            continue
        if identifiant in par_id:
            erreurs.append(f"{identifiant} : identifiant de phase en double")
        par_id[identifiant] = phase
        for champ in CHAMPS:
            if not phase.get(champ):
                erreurs.append(f"{identifiant} : champ `{champ}` manquant")

        horizon, statut = phase.get("horizon"), phase.get("statut")
        if horizon not in HORIZONS:
            erreurs.append(f"{identifiant} : horizon `{horizon}` hors de {sorted(HORIZONS)}")
        if statut not in STATUTS:
            erreurs.append(f"{identifiant} : statut `{statut}` hors de {sorted(STATUTS)}")

        branches = phase.get("branches") or []
        if not branches:
            erreurs.append(f"{identifiant} : ne sert aucune branche du portefeuille")
        for branche in branches:
            if branche not in connues:
                erreurs.append(f"{identifiant} : branche `{branche}` inconnue du portefeuille")
            servies.add(str(branche))

        preuve, test = phase.get("preuve"), phase.get("test")
        if statut in STATUTS_PROUVES:
            if not preuve:
                erreurs.append(f"{identifiant} : statut `{statut}` sans preuve")
            elif not (racine / str(preuve)).exists():
                erreurs.append(f"{identifiant} : preuve `{preuve}` absente du dépôt")
            if not test:
                erreurs.append(f"{identifiant} : statut `{statut}` sans test")
            elif not (racine / str(test)).exists():
                erreurs.append(f"{identifiant} : test `{test}` absent du dépôt")
            elif not Path(str(test)).name.startswith("test_"):
                erreurs.append(
                    f"{identifiant} : `{test}` n'est pas un banc — un test commence par `test_`"
                )
            elif preuve and str(test) == str(preuve):
                erreurs.append(f"{identifiant} : le même fichier sert de preuve et de test")
            if statut == "fait" and identifiant not in journal:
                # Une phase « faite » que le journal ne raconte pas n'a pas d'histoire :
                # c'est une case cochée, pas un résultat daté.
                erreurs.append(
                    f"{identifiant} : statut `fait` sans citation de la phase dans le journal"
                )

        if statut in STATUTS_REFUSES:
            condition = str(phase.get("condition") or "").strip()
            if len(condition) < 40:
                erreurs.append(
                    f"{identifiant} : statut `{statut}` sans condition de révision "
                    "(au moins 40 caractères : ce qui ferait changer d'avis)"
                )
            if phase.get("test") is None and statut == "en-attente":
                erreurs.append(f"{identifiant} : `en-attente` doit nommer le test qui l'attend")

        for dependance in phase.get("depends_on") or []:
            if dependance == identifiant:
                erreurs.append(f"{identifiant} : se dépend elle-même")
            elif dependance not in {str(p.get("id")) for p in phases}:
                erreurs.append(f"{identifiant} : dépendance inconnue `{dependance}`")

    manquantes = sorted(connues - servies)
    if manquantes:
        erreurs.append(
            "branche(s) du portefeuille servies par aucune phase : " + ", ".join(manquantes)
        )

    graphe = {
        str(p.get("id")): [str(d) for d in p.get("depends_on") or []]
        for p in phases
        if p.get("id")
    }
    for boucle in cycles(graphe):
        erreurs.append(f"cycle de dépendances : {boucle}")

    # Un statut ne peut pas dépasser celui de ce dont il dépend : une phase faite
    # sur des fondations absentes est une case cochée trop tôt.
    ordre = {"a-faire": 0, "en-attente": 0, "hors-portee": 0, "en-cours": 1, "fait": 2}
    for phase in phases:
        statut = str(phase.get("statut"))
        for dependance in phase.get("depends_on") or []:
            amont = par_id.get(str(dependance))
            if amont is None:
                continue
            if statut == "fait" and amont.get("statut") != "fait":
                erreurs.append(
                    f"{phase.get('id')} : déclarée faite, mais elle dépend de "
                    f"{dependance} (`{amont.get('statut')}`)"
                )
            elif statut == "en-cours" and ordre.get(str(amont.get("statut")), 0) < ordre["en-attente"]:
                erreurs.append(
                    f"{phase.get('id')} : en cours alors que {dependance} est "
                    f"`{amont.get('statut')}`"
                )
    return erreurs


def principal() -> int:
    try:
        erreurs = verifier(RACINE)
    except SourceIllisible as erreur:
        print(f"Plan illisible : {erreur}", file=sys.stderr)
        return 2
    if erreurs:
        for erreur in erreurs:
            print(f"  - {erreur}", file=sys.stderr)
        print(f"Refusé : {len(erreurs)} écart(s) dans le plan d'ÉVA.", file=sys.stderr)
        return 1
    plan = charger(RACINE / PLAN, "plan")
    phases = plan.get("phase") or []
    statuts: dict[str, int] = {}
    for phase in phases:
        statuts[str(phase.get("statut"))] = statuts.get(str(phase.get("statut")), 0) + 1
    print(
        f"Plan d'ÉVA cohérent : {len(phases)} phases ("
        + ", ".join(f"{n} {s}" for s, n in sorted(statuts.items()))
        + "), toutes les branches du portefeuille servies, aucune capacité sans test, "
        "aucun refus sans condition."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(principal())
