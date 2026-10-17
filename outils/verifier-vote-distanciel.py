#!/usr/bin/env python3
"""Vérifie les garde-fous documentaires du chantier de vote distanciel.

Ce script ne teste aucune cryptographie et ne certifie aucun système de vote.
"""

from __future__ import annotations

import datetime as dt
import hashlib
import re
import sys
import tomllib
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
NOTE = RACINE / "docs" / "rd" / "vote-distanciel-verifiable.md"
PORTEFEUILLE = RACINE / "docs" / "rd" / "portefeuille.toml"
MENACES = RACINE / "docs" / "rd" / "vote-distanciel-menaces.toml"
REGLES = RACINE / "docs" / "rd" / "vote-distanciel-regles.toml"
CAS_ESSAI = RACINE / "docs" / "rd" / "vote-distanciel-cas-essai.toml"
DECISION = RACINE / "docs" / "rd" / "vote-distanciel-decision.md"
COMPARAISON = RACINE / "docs" / "rd" / "vote-distanciel-comparaison.toml"
SOURCES = RACINE / "docs" / "rd" / "vote-distanciel-sources.toml"
PROFILS = RACINE / "docs" / "rd" / "vote-distanciel-profils.toml"
STATUTS = RACINE / "assets" / "documents" / "statuts-2020.pdf"

MENACES_REQUISES = {
    "serveur-urne-compromis", "terminal-compromis", "coercition-domicile",
    "correlation-metadonnees", "collusion-autorites", "perte-de-cles",
    "deni-de-service", "emission-frauduleuse",
    "logiciel-ou-dependance-compromis", "reidentification-future",
}
CHAMPS_MENACE = {
    "id", "acteur", "actif", "scenario", "controle_propose",
    "preuve_attendue", "risque_residuel", "condition_arret", "statut",
}
CHAMPS_INVARIANT = {"id", "description", "preuve_attendue"}
REGLES_REQUISES = {
    "vote-concernes-impactes", "une-cotisation-une-voix", "bureau-electronique",
    "bureau-procuration", "territorial-secret-blanc", "ago-corps-ordre-du-jour",
    "ago-premiere-convocation", "ago-seconde-convocation", "ago-procuration",
    "ago-secret", "ago-session-numerique", "age-premiere-convocation",
    "age-procuration", "age-seconde-convocation", "dissolution-seuils",
}
CHAMPS_REGLE = {"id", "article", "pages", "portee", "releve", "ambiguite", "statut"}
CHAMPS_CAS = {"id", "menaces", "alteration", "attendu", "condition_arret", "statut"}
OPTIONS_COMPARAISON = {"A", "belenios", "helios", "electionguard"}
CHAMPS_CRITERE = {"id", "famille", "bloquant", "question", "preuve_attendue"}
PROFILS_REQUIS = {
    "bureau-executif", "conseil-ethique", "territoriale-constitutive",
    "ago-premiere", "ago-seconde", "age-premiere", "age-seconde", "dissolution",
}

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


def verifier_registre(registre: dict) -> list[str]:
    erreurs: list[str] = []
    meta = registre.get("meta", {})
    if meta.get("initiative") != "vote-distanciel-verifiable":
        erreurs.append("registre relié à l’initiative vote-distanciel-verifiable")
    if meta.get("statut") != "a-expertiser":
        erreurs.append("registre maintenu au statut a-expertiser")

    menaces = registre.get("menace", [])
    ids = [menace.get("id") for menace in menaces]
    if set(ids) != MENACES_REQUISES or len(ids) != len(set(ids)):
        erreurs.append("registre contenant exactement les 10 menaces requises sans doublon")
    for index, menace in enumerate(menaces, start=1):
        champs_vides = [champ for champ in CHAMPS_MENACE if not menace.get(champ)]
        if champs_vides:
            erreurs.append(f"menace {index} avec champs renseignés : {', '.join(sorted(champs_vides))}")
        if menace.get("statut") != "a-expertiser":
            erreurs.append(f"menace {menace.get('id', index)} maintenue à l’état a-expertiser")

    invariants = registre.get("invariant", [])
    ids_invariants = [item.get("id") for item in invariants]
    if len(invariants) < 7 or len(ids_invariants) != len(set(ids_invariants)):
        erreurs.append("au moins 7 invariants sans doublon")
    for index, invariant in enumerate(invariants, start=1):
        champs_vides = [champ for champ in CHAMPS_INVARIANT if not invariant.get(champ)]
        if champs_vides:
            erreurs.append(f"invariant {index} avec champs renseignés : {', '.join(sorted(champs_vides))}")
    return erreurs


def verifier_regles(registre: dict, empreinte_statuts: str) -> list[str]:
    erreurs: list[str] = []
    meta = registre.get("meta", {})
    if meta.get("source") != "assets/documents/statuts-2020.pdf":
        erreurs.append("registre relié à la copie locale des statuts")
    if meta.get("sha256") != empreinte_statuts:
        erreurs.append("empreinte du PDF des statuts synchronisée")
    if meta.get("statut") != "a-faire-relire":
        erreurs.append("registre statutaire maintenu à faire relire")
    regles = registre.get("regle", [])
    ids = [regle.get("id") for regle in regles]
    if set(ids) != REGLES_REQUISES or len(ids) != len(set(ids)):
        erreurs.append("registre contenant exactement les 15 règles statutaires requises sans doublon")
    for index, regle in enumerate(regles, start=1):
        champs_vides = [champ for champ in CHAMPS_REGLE if not regle.get(champ)]
        if champs_vides:
            erreurs.append(f"règle {index} avec champs renseignés : {', '.join(sorted(champs_vides))}")
        if regle.get("statut") != "a-faire-relire":
            erreurs.append(f"règle {regle.get('id', index)} maintenue à faire relire")
    return erreurs


def verifier_profils(registre: dict) -> list[str]:
    erreurs: list[str] = []
    meta = registre.get("meta", {})
    if meta.get("initiative") != "vote-distanciel-verifiable":
        erreurs.append("profils reliés à l’initiative vote-distanciel-verifiable")
    if meta.get("statut") != "a-faire-relire":
        erreurs.append("profils maintenus à faire relire")
    profils = registre.get("profil", [])
    ids = [profil.get("id") for profil in profils]
    if set(ids) != PROFILS_REQUIS or len(ids) != len(set(ids)):
        erreurs.append("registre contenant exactement les 8 profils statutaires")
    regles_couvertes: set[str] = set()
    for index, profil in enumerate(profils, start=1):
        if not profil.get("titre") or not profil.get("regles") or not profil.get("questions_bloquantes"):
            erreurs.append(f"profil {profil.get('id', index)} avec titre, règles et questions bloquantes")
        regles = set(profil.get("regles", []))
        inconnues = regles - REGLES_REQUISES
        if inconnues:
            erreurs.append(f"profil {profil.get('id', index)} avec règles inconnues : {', '.join(sorted(inconnues))}")
        regles_couvertes.update(regles)
        statut_attendu = "bloque-interpretation" if profil.get("id") == "dissolution" else "a-faire-relire"
        if profil.get("statut") != statut_attendu:
            erreurs.append(f"profil {profil.get('id', index)} au statut {statut_attendu}")
        champs_interdits = {"quorum", "majorite", "duree", "procurations", "secret"} & set(profil)
        if champs_interdits:
            erreurs.append(f"profil {profil.get('id', index)} non exécutable avant relecture")
    # La règle du conseil d'éthique est consignée en référence libre car elle n'est
    # pas encore structurée dans le registre des 15 règles ; toutes les autres le sont.
    if not REGLES_REQUISES.issubset(regles_couvertes):
        manquantes = REGLES_REQUISES - regles_couvertes
        erreurs.append(f"règles statutaires non reliées aux profils : {', '.join(sorted(manquantes))}")
    return erreurs


def verifier_cas_essai(registre: dict) -> list[str]:
    erreurs: list[str] = []
    meta = registre.get("meta", {})
    if meta.get("initiative") != "vote-distanciel-verifiable":
        erreurs.append("cas d’essai reliés à l’initiative vote-distanciel-verifiable")
    if meta.get("statut") != "a-faire-expertiser" or meta.get("donnees") != "synthetiques-uniquement":
        erreurs.append("cas maintenus à expertiser avec données synthétiques uniquement")
    cas = registre.get("cas", [])
    ids = [item.get("id") for item in cas]
    if len(cas) < 12 or len(ids) != len(set(ids)):
        erreurs.append("au moins 12 cas d’essai sans doublon")
    couverture: set[str] = set()
    for index, item in enumerate(cas, start=1):
        champs_vides = [champ for champ in CHAMPS_CAS if not item.get(champ)]
        if champs_vides:
            erreurs.append(f"cas {index} avec champs renseignés : {', '.join(sorted(champs_vides))}")
        if item.get("statut") != "a-concevoir":
            erreurs.append(f"cas {item.get('id', index)} maintenu à concevoir")
        menaces = set(item.get("menaces", []))
        inconnues = menaces - MENACES_REQUISES
        if inconnues:
            erreurs.append(f"cas {item.get('id', index)} avec menaces inconnues : {', '.join(sorted(inconnues))}")
        couverture.update(menaces)
    if couverture != MENACES_REQUISES:
        erreurs.append("les 10 menaces sont couvertes par au moins un cas projeté")
    return erreurs


def verifier_comparaison(registre: dict) -> list[str]:
    erreurs: list[str] = []
    meta = registre.get("meta", {})
    if meta.get("initiative") != "vote-distanciel-verifiable":
        erreurs.append("comparaison reliée à l’initiative vote-distanciel-verifiable")
    if meta.get("statut") != "a-faire-expertiser":
        erreurs.append("comparaison maintenue à faire expertiser")
    options = registre.get("option", [])
    ids_options = [option.get("id") for option in options]
    if set(ids_options) != OPTIONS_COMPARAISON or len(ids_options) != len(set(ids_options)):
        erreurs.append("comparaison contenant A, Belenios, Helios et ElectionGuard sans doublon")
    for option in options:
        if option.get("statut") != "a-evaluer" or not option.get("limite") or not option.get("source"):
            erreurs.append(f"option {option.get('id', '?')} non sélectionnée, sourcée et limitée")
        champs_interdits = {"score", "note", "rang", "probabilite"} & set(option)
        if champs_interdits:
            erreurs.append(f"option {option.get('id', '?')} sans score, rang ni probabilité")
    criteres = registre.get("critere", [])
    ids_criteres = [critere.get("id") for critere in criteres]
    if len(criteres) < 15 or len(ids_criteres) != len(set(ids_criteres)):
        erreurs.append("au moins 15 critères sans doublon")
    for index, critere in enumerate(criteres, start=1):
        champs_vides = [champ for champ in CHAMPS_CRITERE if champ not in critere or critere.get(champ) in {None, ""}]
        if champs_vides:
            erreurs.append(f"critère {index} avec champs renseignés : {', '.join(sorted(champs_vides))}")
        if critere.get("bloquant") is not True:
            erreurs.append(f"critère {critere.get('id', index)} maintenu bloquant")
    return erreurs


def verifier_sources(registre: dict) -> list[str]:
    erreurs: list[str] = []
    meta = registre.get("meta", {})
    if meta.get("statut") != "releve-partiel-a-expertiser":
        erreurs.append("relevé des sources maintenu partiel et à expertiser")
    projets = registre.get("projet", [])
    ids = [projet.get("id") for projet in projets]
    if set(ids) != {"belenios", "helios", "electionguard"} or len(ids) != len(set(ids)):
        erreurs.append("relevé contenant exactement Belenios, Helios et ElectionGuard")
    champs = {
        "id", "depot", "url", "branche", "commit", "date_commit", "archive",
        "licence_api", "derniere_release_github", "observation_readme", "limite",
        "points_a_resoudre", "preuves_a_chercher", "statut",
    }
    for index, projet in enumerate(projets, start=1):
        vides = [
            champ for champ in champs
            if champ not in projet or projet.get(champ) is None or projet.get(champ) == ""
        ]
        if vides:
            erreurs.append(f"source {index} avec champs renseignés : {', '.join(sorted(vides))}")
        if not re.fullmatch(r"[0-9a-f]{40}", str(projet.get("commit", ""))):
            erreurs.append(f"source {projet.get('id', index)} avec commit Git complet")
        try:
            dt.datetime.fromisoformat(str(projet.get("date_commit", "")).replace("Z", "+00:00"))
        except ValueError:
            erreurs.append(f"source {projet.get('id', index)} avec date de commit ISO")
        for champ_liste in ("points_a_resoudre", "preuves_a_chercher"):
            valeurs = projet.get(champ_liste, [])
            if not isinstance(valeurs, list) or len(valeurs) < 2 or any(not isinstance(v, str) or not v for v in valeurs):
                erreurs.append(f"source {projet.get('id', index)} avec {champ_liste} explicites")
        if projet.get("statut") != "a-evaluer":
            erreurs.append(f"source {projet.get('id', index)} maintenue à évaluer")
        if projet.get("archive") is not False:
            erreurs.append(f"état d’archivage de {projet.get('id', index)} attendu explicitement faux au relevé")
        champs_interdits = {"score", "note", "rang", "selection"} & set(projet)
        if champs_interdits:
            erreurs.append(f"source {projet.get('id', index)} sans score ni sélection")
    return erreurs


def verifier_decision(markdown: str) -> tuple[str, list[str]]:
    erreurs: list[str] = []
    champs = [
        "Version des statuts confirmée", "Règlement intérieur vérifié",
        "Profil retenu", "Option retenue", "Instance ou rôle décideur",
        "Date de décision", "Date de réexamen", "Conditions ou objections",
    ]
    valeurs: dict[str, str] = {}
    for champ in champs:
        ligne = re.search(rf"^\| {re.escape(champ)} \|(?P<valeur>.*?)\|\s*$", markdown, re.M)
        if not ligne:
            erreurs.append(f"champ de décision absent : {champ}")
        else:
            valeurs[champ] = ligne.group("valeur").strip()
    if erreurs:
        return "invalide", erreurs
    remplis = sum(bool(valeur) for valeur in valeurs.values())
    if remplis == 0:
        return "en attente", []
    if remplis != len(champs):
        return "invalide", [f"trace de décision partielle : {remplis}/{len(champs)} champs remplis"]

    profils = {
        "bureau-executif", "conseil-ethique", "territoriale-constitutive",
        "ago-premiere", "ago-seconde", "age-premiere", "age-seconde",
        "dissolution", "aucun",
    }
    if valeurs["Profil retenu"] not in profils:
        erreurs.append("profil retenu inconnu")
    if valeurs["Option retenue"] not in {"A", "B", "C"}:
        erreurs.append("option retenue invalide : A, B ou C uniquement")
    if valeurs["Profil retenu"] == "dissolution":
        erreurs.append("profil dissolution bloqué avant interprétation des articles 15 et 19")
    if valeurs["Profil retenu"] == "aucun" and valeurs["Option retenue"] != "A":
        erreurs.append("profil aucun compatible uniquement avec l’option A")
    try:
        date_decision = dt.date.fromisoformat(valeurs["Date de décision"])
        date_reexamen = dt.date.fromisoformat(valeurs["Date de réexamen"])
        if date_reexamen <= date_decision:
            erreurs.append("date de réexamen attendue après la décision")
    except ValueError:
        erreurs.append("dates attendues au format AAAA-MM-JJ")
    return ("décision consignée" if not erreurs else "invalide"), erreurs


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

    with MENACES.open("rb") as fichier:
        registre = tomllib.load(fichier)
    manquants.extend(verifier_registre(registre))

    empreinte_statuts = hashlib.sha256(STATUTS.read_bytes()).hexdigest()
    with REGLES.open("rb") as fichier:
        regles = tomllib.load(fichier)
    manquants.extend(verifier_regles(regles, empreinte_statuts))

    with PROFILS.open("rb") as fichier:
        profils = tomllib.load(fichier)
    manquants.extend(verifier_profils(profils))

    with CAS_ESSAI.open("rb") as fichier:
        cas_essai = tomllib.load(fichier)
    manquants.extend(verifier_cas_essai(cas_essai))

    with COMPARAISON.open("rb") as fichier:
        comparaison = tomllib.load(fichier)
    manquants.extend(verifier_comparaison(comparaison))

    with SOURCES.open("rb") as fichier:
        sources = tomllib.load(fichier)
    manquants.extend(verifier_sources(sources))

    etat_decision, erreurs_decision = verifier_decision(DECISION.read_text(encoding="utf-8"))
    manquants.extend(erreurs_decision)

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
        "Cadrage du vote distanciel présent : 9 sections, 7 invariants, 10 menaces "
        "à expertiser, 15 règles et 8 profils statutaires à relire, 12 cas synthétiques à concevoir, "
        f"4 options et 15 critères sans score, 3 sources épinglées à évaluer, décision {etat_decision}, initiative P0 à cadrer, "
        "aucune identité ni bulletin réel autorisé."
    )
    return 0


if __name__ == "__main__":
    try:
        sys.exit(principal())
    except (OSError, tomllib.TOMLDecodeError) as erreur:
        print(f"Cadrage du vote distanciel impossible à vérifier : {erreur}", file=sys.stderr)
        sys.exit(1)
