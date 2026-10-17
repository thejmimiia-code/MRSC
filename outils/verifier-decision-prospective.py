#!/usr/bin/env python3
"""Vérifie les faits internes du brief prospectif sans prendre la décision.

Ce contrôle détecte les nombres devenus incohérents avec les sources du dépôt.
Il ne valide ni les scénarios, ni leur pertinence, ni une option A/B/C.
"""

from __future__ import annotations

import datetime as dt
import re
import sys
import tomllib
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
BRIEF = RACINE / "docs" / "rd" / "decision-prospective.md"
CATALOGUE = RACINE / "docs" / "apprentissage" / "catalogue.toml"
PORTEFEUILLE = RACINE / "docs" / "rd" / "portefeuille.toml"
APPRENDRE = RACINE / "apprendre.html"
POIDS = RACINE / "docs" / "rd" / "poids-pages.md"
MOIS_FR = {
    "janvier": 1, "février": 2, "mars": 3, "avril": 4,
    "mai": 5, "juin": 6, "juillet": 7, "août": 8,
    "septembre": 9, "octobre": 10, "novembre": 11, "décembre": 12,
}


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


def date_du_brief(markdown: str) -> dt.date:
    entete = re.search(r"\*\*Date : (\d{1,2}) ([a-zéû]+) (\d{4})\.", markdown)
    if not entete or entete.group(2) not in MOIS_FR:
        raise ValueError("date française du brief introuvable ou invalide")
    date = dt.date(int(entete.group(3)), MOIS_FR[entete.group(2)], int(entete.group(1)))
    libelle_tableau = f"Valeur au {entete.group(1)} {entete.group(2)} {entete.group(3)}"
    if libelle_tableau not in markdown:
        raise ValueError("date du tableau différente de la date du brief")
    return date


def etat_trace_decision(markdown: str) -> str:
    section = re.search(r"## 10\. Trace de décision(?P<contenu>.*?)(?:\n## |\Z)", markdown, re.S)
    if not section:
        raise ValueError("section de trace de décision introuvable")
    champs = [
        "Option retenue", "Date", "Personne ou instance qui décide",
        "Conditions ajoutées", "Date de réexamen",
    ]
    valeurs: list[str] = []
    for champ in champs:
        ligne = re.search(rf"^\| {re.escape(champ)} \|(?P<valeur>.*?)\|\s*$", section.group("contenu"), re.M)
        if not ligne:
            raise ValueError(f"champ de décision absent : {champ}")
        valeurs.append(ligne.group("valeur").strip())
    remplis = sum(bool(valeur) for valeur in valeurs)
    if remplis == 0:
        return "en attente"
    if remplis != len(valeurs):
        raise ValueError(f"trace de décision partielle : {remplis}/{len(valeurs)} champs remplis")
    if valeurs[0] not in {"A", "B", "C"}:
        raise ValueError("option retenue invalide : utiliser A, B ou C")
    try:
        dt.date.fromisoformat(valeurs[1])
        dt.date.fromisoformat(valeurs[4])
    except ValueError as erreur:
        raise ValueError("dates de décision attendues au format AAAA-MM-JJ") from erreur
    return f"option {valeurs[0]} consignée"


def verifier_etat_initiative(decision: str, initiatives: list[dict]) -> str:
    correspondances = [
        initiative for initiative in initiatives
        if initiative.get("id") == "prospective-apprentissages-2030"
    ]
    if len(correspondances) != 1:
        raise ValueError("initiative prospective-apprentissages-2030 absente ou dupliquée")
    etat = correspondances[0].get("etat")
    if decision == "en attente" and etat != "a-cadrer":
        raise ValueError("décision en attente mais initiative hors de l’état a-cadrer")
    if decision != "en attente" and etat == "a-cadrer":
        raise ValueError("décision consignée mais initiative encore dans l’état a-cadrer")
    return str(etat)


def poids_page(markdown: str, page: str) -> tuple[int, int]:
    motif = rf"^\| `{re.escape(page)}` \| ([0-9.]+) \| ([0-9.]+) \|"
    ligne = re.search(motif, markdown, re.M)
    if not ligne:
        raise ValueError(f"mesure de {page} introuvable")
    return round(float(ligne.group(1))), round(float(ligne.group(2)))


def date_prochaine_revue(meta: dict) -> dt.date:
    derniere = meta.get("derniere_revue")
    cadence = meta.get("cadence_revue_jours")
    if not isinstance(derniere, dt.date) or not isinstance(cadence, int):
        raise ValueError("métadonnées de revue du portefeuille invalides")
    return derniere + dt.timedelta(days=cadence)


def principal() -> int:
    brief = BRIEF.read_text(encoding="utf-8")
    date_reference = date_du_brief(brief)
    decision = etat_trace_decision(brief)
    catalogue = charger_toml(CATALOGUE).get("fiche", [])
    portefeuille = charger_toml(PORTEFEUILLE)
    initiatives = portefeuille.get("initiative", [])
    etat_initiative = verifier_etat_initiative(decision, initiatives)
    fiches = len(catalogue)
    prototypes = sum(fiche.get("statut_editorial") == "Prototype à relire" for fiche in catalogue)
    domaines = len({fiche.get("domaine") for fiche in catalogue if fiche.get("domaine")})
    total_initiatives = len(initiatives)
    p0 = sum(initiative.get("priorite") == "P0" for initiative in initiatives)
    questions = compter_questions_boussole(APPRENDRE.read_text(encoding="utf-8"))
    echues = 0
    for fiche in catalogue:
        revue = fiche.get("revue_le")
        intervalle = fiche.get("intervalle_revue_jours")
        if revue and isinstance(intervalle, int):
            echeance = dt.date.fromisoformat(revue) + dt.timedelta(days=intervalle)
            echues += echeance < date_reference
    prochaine_revue = date_prochaine_revue(portefeuille.get("meta", {}))
    poids_mobile, poids_ecran = poids_page(POIDS.read_text(encoding="utf-8"), "apprendre.html")

    attentes = {
        "fiches et domaines": rf"\| Fiches d'apprentissage publiées \| {fiches} dans {domaines} domaines \|",
        "prototypes": rf"\| Fiches explicitement « prototypes à relire » \| \*\*{prototypes}\*\* \|",
        "initiatives": rf"\| Initiatives R&D suivies \| {total_initiatives}, dont {p0} en priorité P0 \|",
        "revues échues": rf"\| Fiches dont la date de revue est échue \| \*\*{echues}\*\* \|",
        "prochaine revue": rf"\| Prochaine revue du portefeuille R&D \| \*\*{prochaine_revue.isoformat()}\*\* \|",
        "Boussole": rf"\| Boussole publiée \| {questions} questions statiques,",
        "poids Apprendre": rf"\| Poids estimé de la page Apprendre \| {poids_mobile} Kio mobile / {poids_ecran} Kio grand écran",
    }
    erreurs = [nom for nom, motif in attentes.items() if not re.search(motif, brief)]
    if erreurs:
        print("Brief prospectif désynchronisé : " + ", ".join(erreurs), file=sys.stderr)
        print(
            f"Valeurs calculées : {fiches} fiches dans {domaines} domaines, {prototypes} prototypes, "
            f"{total_initiatives} initiatives dont {p0} P0, {questions} questions, "
            f"{echues} revue échue, poids {poids_mobile}/{poids_ecran} Kio.",
            file=sys.stderr,
        )
        return 1

    print(
        f"Brief prospectif synchronisé au {date_reference.isoformat()} : "
        f"{fiches} fiches dans {domaines} domaines, {prototypes} prototypes, "
        f"{total_initiatives} initiatives dont {p0} P0, {questions} questions, "
        f"{echues} revue échue, poids {poids_mobile}/{poids_ecran} Kio, "
        f"décision {decision}, initiative {etat_initiative}."
    )
    return 0


if __name__ == "__main__":
    try:
        sys.exit(principal())
    except (OSError, ValueError, tomllib.TOMLDecodeError) as erreur:
        print(f"Brief prospectif impossible à vérifier : {erreur}", file=sys.stderr)
        sys.exit(1)
