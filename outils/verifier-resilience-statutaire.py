#!/usr/bin/env python3
"""Vérifie la structure documentaire du registre de résilience statutaire.

Ce contrôle ne constitue ni une validation juridique ni une preuve d'exhaustivité.
"""
from __future__ import annotations

import sys
import tomllib
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
REGISTRE = RACINE / "docs" / "rd" / "statuts-risques.toml"
MATRICE = RACINE / "docs" / "rd" / "statuts-matrice-tracabilite.toml"
RISQUES_REQUIS = {
    "captation-gouvernance", "influence-exterieure", "manipulation-electorat",
    "manipulation-information", "manipulation-vote", "conflit-interets",
    "sanction-detournee", "captation-financiere", "captation-numerique",
    "atteinte-donnees", "blocage-sabotage", "desaccord-interpretatif",
    "crise-institutionnelle", "catastrophe-danger", "rupture-succession",
    "erreur-complexite",
}
INVARIANTS_REQUIS = {
    "droits-non-derogeables", "competence-prealable", "separation-des-pouvoirs",
    "regle-non-retroactive", "recours-effectif", "urgence-temporaire",
    "preuve-proportionnee", "aucune-souverainete-parallele",
}
PORTES_REQUISES = {
    "avant-redaction-reglement", "avant-adoption-reglement", "avant-operation-sensible"
}


def verifier(registre: dict) -> list[str]:
    erreurs: list[str] = []
    meta = registre.get("meta", {})
    if (
        meta.get("initiative") != "resilience-statutaire-globale"
        or meta.get("statut") != "a-faire-relire"
        or meta.get("probabilites") is not False
        or meta.get("exhaustif") is not False
    ):
        erreurs.append("registre à faire relire, sans probabilité ni prétention d’exhaustivité")
    if not meta.get("regle"):
        erreurs.append("registre avec règle de non-compensation")

    invariants = registre.get("invariant", [])
    ids_invariants = [item.get("id") for item in invariants]
    if set(ids_invariants) != INVARIANTS_REQUIS or len(ids_invariants) != len(set(ids_invariants)):
        erreurs.append("exactement 8 invariants sans doublon")
    for item in invariants:
        if not item.get("exigence") or not item.get("preuve_attendue"):
            erreurs.append(f"invariant {item.get('id', '?')} avec exigence et preuve")

    risques = registre.get("risque", [])
    ids_risques = [item.get("id") for item in risques]
    if set(ids_risques) != RISQUES_REQUIS or len(ids_risques) != len(set(ids_risques)):
        erreurs.append("exactement 16 familles de risques sans doublon")
    for item in risques:
        identifiant = item.get("id", "?")
        if not item.get("domaine") or not item.get("condition_arret"):
            erreurs.append(f"risque {identifiant} avec domaine et arrêt")
        for champ, minimum in (("scenarios", 4), ("actifs", 3), ("controles", 4)):
            valeurs = item.get(champ, [])
            if not isinstance(valeurs, list) or len(valeurs) < minimum or any(not valeur for valeur in valeurs):
                erreurs.append(f"risque {identifiant} avec au moins {minimum} {champ}")
        if item.get("statut") != "a-faire-relire":
            erreurs.append(f"risque {identifiant} maintenu à faire relire")
        if any(champ in item for champ in ("score", "probabilite", "rang", "valide")):
            erreurs.append(f"risque {identifiant} sans score, probabilité, rang ni validation")

    portes = registre.get("porte", [])
    ids_portes = [item.get("id") for item in portes]
    if set(ids_portes) != PORTES_REQUISES or len(ids_portes) != len(set(ids_portes)):
        erreurs.append("exactement 3 portes de décision sans doublon")
    for item in portes:
        identifiant = item.get("id", "?")
        if len(item.get("exigences", [])) < 5 or not item.get("decision") or item.get("statut") != "bloquante":
            erreurs.append(f"porte {identifiant} bloquante, complète et décidée humainement")
    return erreurs


def verifier_matrice(matrice: dict) -> list[str]:
    erreurs: list[str] = []
    meta = matrice.get("meta", {})
    if (
        meta.get("initiative") != "resilience-statutaire-globale"
        or meta.get("source") != "assets/documents/statuts-2020.pdf"
        or meta.get("statut") != "a-faire-relire"
    ):
        erreurs.append("matrice reliée aux statuts et maintenue à faire relire")
    articles = matrice.get("article", [])
    ids = [item.get("id") for item in articles]
    if len(articles) != 20 or len(ids) != len(set(ids)):
        erreurs.append("exactement 20 groupes d’articles sans doublon")
    champs = {"id", "pages", "objet", "competence", "preuve", "recours", "urgence", "point_a_trancher", "statut"}
    for item in articles:
        identifiant = item.get("id", "?")
        if any(champ not in item or item.get(champ) is None or item.get(champ) == "" for champ in champs):
            erreurs.append(f"article {identifiant} avec traçabilité complète")
        if item.get("statut") not in {"a-faire-relire", "bloque-verification-source", "bloque-interpretation-juridique"}:
            erreurs.append(f"article {identifiant} sans validation prématurée")
    absents = next((item for item in articles if item.get("id") == "articles-17-18"), {})
    if absents.get("statut") != "bloque-verification-source" or absents.get("pages") != []:
        erreurs.append("articles 17 et 18 maintenus bloqués sans page inventée")
    dissolution = next((item for item in articles if item.get("id") == "article-19"), {})
    if dissolution.get("statut") != "bloque-interpretation-juridique":
        erreurs.append("dissolution maintenue bloquée pour interprétation juridique")
    return erreurs


def principal() -> int:
    with REGISTRE.open("rb") as fichier:
        registre = tomllib.load(fichier)
    with MATRICE.open("rb") as fichier:
        matrice = tomllib.load(fichier)
    erreurs = verifier(registre) + verifier_matrice(matrice)
    if erreurs:
        print("Registre de résilience incomplet :", file=sys.stderr)
        for erreur in erreurs:
            print(f"- {erreur}", file=sys.stderr)
        return 1
    print("Résilience statutaire cadrée : 8 invariants, 16 familles de risques, 20 groupes d’articles et 3 portes bloquantes ; aucune validation ou exhaustivité déclarée.")
    return 0


if __name__ == "__main__":
    raise SystemExit(principal())
