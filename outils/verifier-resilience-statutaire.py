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
REGLEMENT = RACINE / "docs" / "rd" / "reglement-interieur-projet.md"
FICHES = RACINE / "docs" / "rd" / "reglement-fiches-redaction.toml"
ROLES_REQUIS = {
    "association-decisionnaire", "juridique-statutaire", "cryptographie-vote",
    "protection-donnees", "accessibilite-usages", "operations-securite",
}
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

    classements = matrice.get("classement", [])
    articles_classes = [item.get("article") for item in classements]
    if set(articles_classes) != set(ids) or len(articles_classes) != len(set(articles_classes)):
        erreurs.append("classement normatif unique pour chacun des 20 groupes")
    niveaux_permis = {"statuts", "reglement", "procedure", "mixte", "decision-prealable"}
    for item in classements:
        identifiant = item.get("article", "?")
        if item.get("niveau") not in niveaux_permis or not item.get("justification"):
            erreurs.append(f"classement {identifiant} avec niveau permis et justification")
    for identifiant in ("article-9", "articles-10-4-10-7", "articles-17-18", "article-19"):
        classement = next((item for item in classements if item.get("article") == identifiant), {})
        if classement.get("niveau") != "decision-prealable":
            erreurs.append(f"classement {identifiant} maintenu en décision préalable")
    return erreurs


def verifier_reglement(markdown: str) -> list[str]:
    erreurs: list[str] = []
    if "Statut : `a-rediger-et-faire-relire`" not in markdown or "Ce document n’est pas un règlement en vigueur" not in markdown:
        erreurs.append("projet de règlement explicitement non adopté et à faire relire")
    articles = [ligne for ligne in markdown.splitlines() if ligne.startswith("### Article RI-")]
    numeros = []
    for ligne in articles:
        try:
            numeros.append(int(ligne.split("RI-", 1)[1].split(" ", 1)[0]))
        except (ValueError, IndexError):
            erreurs.append("numérotation lisible des articles du projet")
    if numeros != list(range(1, 83)):
        erreurs.append("exactement 82 articles de travail numérotés sans lacune")
    blocages = (
        "compétence, quorum et majorité d’adoption",
        "transition entre désignations initiales",
        "absence des articles 17 et 18",
        "articulation juridique des articles 15 et 19",
        "existence, adoption et portée de la charte",
    )
    if any(texte not in markdown for texte in blocages):
        erreurs.append("cinq décisions préalables visibles avant rédaction")
    interdictions = (
        "Aucune violence", "Aucune cryptographie maison", "modification statutaire provisoire",
        "Il ne crée aucun droit, pouvoir, sanction",
    )
    if any(texte not in markdown for texte in interdictions):
        erreurs.append("garde-fous contre pouvoir, violence et improvisation technique")
    return erreurs


def verifier_fiches(registre: dict) -> list[str]:
    erreurs: list[str] = []
    meta = registre.get("meta", {})
    if (
        meta.get("initiative") != "resilience-statutaire-globale"
        or meta.get("statut") != "a-faire-relire"
        or meta.get("adoption") is not False
        or meta.get("effet_juridique") is not False
    ):
        erreurs.append("fiches non adoptées, sans effet juridique et à faire relire")
    fiches = registre.get("fiche", [])
    ids = [fiche.get("id") for fiche in fiches]
    titres = [fiche.get("titre") for fiche in fiches]
    titres_requis = {"I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X", "XI", "XII", "XIII", "XIV", "XV", "XVI", "XVII", "XVIII", "XIX"}
    if len(fiches) != 19 or len(ids) != len(set(ids)) or set(titres) != titres_requis:
        erreurs.append("exactement 19 fiches et titres sans doublon")
    for fiche in fiches:
        identifiant = fiche.get("id", "?")
        champs = ("sources", "objectif", "a_rediger", "interdit", "preuve_attendue", "roles_requis")
        if any(not fiche.get(champ) for champ in champs):
            erreurs.append(f"fiche {identifiant} avec source, objectif, limites, preuve et rôles")
        roles = set(fiche.get("roles_requis", []))
        if roles - ROLES_REQUIS or "juridique-statutaire" not in roles and identifiant in {
            "hierarchie-definitions", "age-dissolution", "discipline-recours", "adoption-revision"
        }:
            erreurs.append(f"fiche {identifiant} avec rôles connus et revue juridique requise")
        if fiche.get("statut") != "a-faire-relire":
            erreurs.append(f"fiche {identifiant} maintenue à faire relire")
    return erreurs


def principal() -> int:
    with REGISTRE.open("rb") as fichier:
        registre = tomllib.load(fichier)
    with MATRICE.open("rb") as fichier:
        matrice = tomllib.load(fichier)
    with FICHES.open("rb") as fichier:
        fiches = tomllib.load(fichier)
    erreurs = (
        verifier(registre) + verifier_matrice(matrice)
        + verifier_reglement(REGLEMENT.read_text(encoding="utf-8"))
        + verifier_fiches(fiches)
    )
    if erreurs:
        print("Registre de résilience incomplet :", file=sys.stderr)
        for erreur in erreurs:
            print(f"- {erreur}", file=sys.stderr)
        return 1
    print("Résilience statutaire cadrée : 8 invariants, 16 familles de risques, 20 groupes d’articles, 82 articles de règlement projetés, 19 fiches de rédaction et 3 portes bloquantes ; aucune validation ou exhaustivité déclarée.")
    return 0


if __name__ == "__main__":
    raise SystemExit(principal())
