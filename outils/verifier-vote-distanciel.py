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
REVUES = RACINE / "docs" / "rd" / "vote-distanciel-revues.toml"
DONNEES = RACINE / "docs" / "rd" / "vote-distanciel-donnees.toml"
CORRELATION = RACINE / "docs" / "rd" / "vote-distanciel-correlation.toml"
CONTINUITE = RACINE / "docs" / "rd" / "vote-distanciel-continuite.toml"
ACCESSIBILITE = RACINE / "docs" / "rd" / "vote-distanciel-accessibilite.toml"
ASSISTANCE = RACINE / "docs" / "rd" / "vote-distanciel-assistance.toml"
CLES = RACINE / "docs" / "rd" / "vote-distanciel-cles.toml"
CHAINE_LOGICIELLE = RACINE / "docs" / "rd" / "vote-distanciel-chaine-logicielle.toml"
RESULTATS = RACINE / "docs" / "rd" / "vote-distanciel-resultats.toml"
DOSSIER = RACINE / "docs" / "rd" / "vote-distanciel-dossier-deliberation.md"
STATUTS = RACINE / "assets" / "documents" / "statuts-2020.pdf"

SECTIONS_DOSSIER = [
    "## 1. À quoi sert ce dossier",
    "## 2. Ce qui est établi, ce qui ne l’est pas",
    "## 3. Les huit profils, un par un",
    "## 4. Trois voies ouvertes, une voie bloquée",
    "## 5. Les huit ambiguïtés à trancher",
    "## 6. La question de l’emplacement d’un éventuel système",
    "## 7. Les quinze conditions cumulatives",
    "## 8. Trace de décision à remplir",
    "## 9. Déroulé proposé d’une séance",
    "## 10. Registre des objections",
    "## 11. Ce que ce dossier ne fait pas",
    "## 12. Sources internes",
]
# Formules interdites : elles promettraient une propriété que rien dans le dépôt n'établit.
FORMULES_INTERDITES_DOSSIER = [
    "super sécurisé", "inviolable", "infalsifiable", "totalement sûr",
    "100 % sécurisé", "sécurité garantie",
]

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
    "conseil-ethique-electronique", "phases-participatives", "ago-proces-verbal",
}
CHAMPS_REGLE = {"id", "article", "pages", "portee", "releve", "ambiguite", "statut"}
CHAMPS_CAS = {"id", "menaces", "alteration", "attendu", "condition_arret", "statut"}
OPTIONS_COMPARAISON = {"A", "belenios", "helios", "electionguard"}
CHAMPS_CRITERE = {"id", "famille", "bloquant", "question", "preuve_attendue"}
PROFILS_REQUIS = {
    "bureau-executif", "conseil-ethique", "territoriale-constitutive",
    "ago-premiere", "ago-seconde", "age-premiere", "age-seconde", "dissolution",
}
ROLES_REVUE = {
    "association-decisionnaire", "juridique-statutaire", "cryptographie-vote",
    "protection-donnees", "accessibilite-usages", "operations-securite",
}
REVUES_REQUISES = {
    "source-statutaire", "modele-menaces", "comparaison-candidats",
    "protocole-banc", "decision-de-phase",
}
CATEGORIES_DONNEES = {
    "identite-eligibilite", "justificatif-anonyme", "bulletin-chiffre",
    "recu-inclusion", "preuves-publiques", "journal-emission", "journal-urne",
    "registre-procurations",
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
        erreurs.append("registre contenant exactement les 18 règles statutaires requises sans doublon")
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


def verifier_donnees(registre: dict) -> list[str]:
    erreurs: list[str] = []
    meta = registre.get("meta", {})
    if meta.get("initiative") != "vote-distanciel-verifiable" or meta.get("statut") != "a-faire-expertiser":
        erreurs.append("modèle de données relié à l’initiative et maintenu à expertiser")
    categories = registre.get("categorie", [])
    ids = [categorie.get("id") for categorie in categories]
    if set(ids) != CATEGORIES_DONNEES or len(ids) != len(set(ids)):
        erreurs.append("modèle contenant exactement les 8 catégories de données")
    champs = {
        "id", "finalite_projetee", "detenteur_projete", "public",
        "contenu_interdit", "retention", "statut",
    }
    for index, categorie in enumerate(categories, start=1):
        vides = [
            champ for champ in champs
            if champ not in categorie or categorie.get(champ) is None or categorie.get(champ) == ""
        ]
        if vides:
            erreurs.append(f"catégorie {index} avec champs renseignés : {', '.join(sorted(vides))}")
        if categorie.get("statut") != "a-faire-expertiser":
            erreurs.append(f"catégorie {categorie.get('id', index)} maintenue à expertiser")
        interdits = categorie.get("contenu_interdit", [])
        if not isinstance(interdits, list) or len(interdits) < 3:
            erreurs.append(f"catégorie {categorie.get('id', index)} avec au moins 3 contenus interdits")
    liaisons = registre.get("liaison_interdite", [])
    paires: set[frozenset[str]] = set()
    for index, liaison in enumerate(liaisons, start=1):
        gauche, droite = liaison.get("gauche"), liaison.get("droite")
        if gauche not in CATEGORIES_DONNEES or droite not in CATEGORIES_DONNEES or gauche == droite:
            erreurs.append(f"liaison interdite {index} entre catégories distinctes connues")
        if not liaison.get("raison"):
            erreurs.append(f"liaison interdite {index} avec raison")
        paires.add(frozenset((gauche, droite)))
    if len(liaisons) < 6 or len(paires) != len(liaisons):
        erreurs.append("au moins 6 liaisons interdites sans doublon")
    paire_identite_bulletin = frozenset(("identite-eligibilite", "bulletin-chiffre"))
    if paire_identite_bulletin not in paires:
        erreurs.append("liaison identité–bulletin explicitement interdite")
    return erreurs


def verifier_correlation(registre: dict) -> list[str]:
    """Vérifie que l'épreuve reste synthétique, non exécutable et sans seuil inventé."""
    erreurs: list[str] = []
    meta = registre.get("meta", {})
    if (
        meta.get("initiative") != "vote-distanciel-verifiable"
        or meta.get("statut") != "a-faire-expertiser"
        or meta.get("donnees") != "synthetiques-uniquement"
        or meta.get("execution_autorisee") is not False
    ):
        erreurs.append("épreuve de corrélation synthétique, non exécutable et à expertiser")
    if meta.get("seuil_accepte") != "a-definir-avant-exercice-par-revue-humaine":
        erreurs.append("aucun seuil de corrélation inventé avant revue humaine")
    if not meta.get("regle_arret"):
        erreurs.append("épreuve de corrélation avec règle d’arrêt")

    vues = registre.get("vue", [])
    ids_vues = [vue.get("id") for vue in vues]
    vues_requises = {"emetteur", "urne", "public", "collusion-emetteur-urne"}
    if set(ids_vues) != vues_requises or len(ids_vues) != len(set(ids_vues)):
        erreurs.append("exactement 4 vues d’attaque distinctes")
    for vue in vues:
        categories = vue.get("categories", [])
        if not vue.get("acteur_projete") or not categories or not vue.get("contenu_interdit"):
            erreurs.append(f"vue {vue.get('id', '?')} bornée par acteur, catégories et interdits")
        if set(categories) - CATEGORIES_DONNEES:
            erreurs.append(f"vue {vue.get('id', '?')} sans catégorie inconnue")

    signaux = registre.get("signal", [])
    ids_signaux = [signal.get("id") for signal in signaux]
    if set(ids_signaux) != {"temps", "taille", "identifiant", "reseau", "sauvegarde"}:
        erreurs.append("épreuve couvrant exactement les 5 signaux de corrélation")
    if len(ids_signaux) != len(set(ids_signaux)):
        erreurs.append("signaux de corrélation sans doublon")
    for signal in signaux:
        if not signal.get("variation_synthetique") or not signal.get("mesure_projetee"):
            erreurs.append(f"signal {signal.get('id', '?')} avec variation et mesure projetées")

    prerequis = registre.get("prerequis", [])
    if len(prerequis) < 5 or len({item.get("id") for item in prerequis}) != len(prerequis):
        erreurs.append("au moins 5 prérequis sans doublon")
    for item in prerequis:
        if item.get("statut") != "a-attribuer" or not item.get("preuve_attendue"):
            erreurs.append(f"prérequis {item.get('id', '?')} maintenu à attribuer avec preuve")
    return erreurs


def verifier_continuite(registre: dict) -> list[str]:
    """Vérifie les arrêts sûrs sans autoriser une procédure opérationnelle."""
    erreurs: list[str] = []
    meta = registre.get("meta", {})
    if (
        meta.get("initiative") != "vote-distanciel-verifiable"
        or meta.get("statut") != "a-faire-relire"
        or meta.get("donnees") != "synthetiques-uniquement"
        or meta.get("execution_autorisee") is not False
    ):
        erreurs.append("continuité synthétique, non exécutable et à faire relire")
    if not meta.get("principe"):
        erreurs.append("continuité avec principe de non-dégradation")

    incidents = registre.get("incident", [])
    ids = [incident.get("id") for incident in incidents]
    requis = {
        "indisponibilite-avant-ouverture", "indisponibilite-pendant-ouverture",
        "divergence-a-la-cloture", "preuves-indisponibles", "part-de-cle-indisponible",
        "registre-eligibilite-indisponible", "suspicion-de-correlation-ou-fuite",
    }
    if set(ids) != requis or len(ids) != len(set(ids)):
        erreurs.append("exactement 7 incidents de continuité sans doublon")
    for incident in incidents:
        identifiant = incident.get("id", "?")
        champs = ("detection_projetee", "action_par_defaut", "preuve_attendue")
        if any(not incident.get(champ) for champ in champs):
            erreurs.append(f"incident {identifiant} détectable, borné et prouvable")
        roles = set(incident.get("autorite_humaine_requise", []))
        if "association-decisionnaire" not in roles or roles - ROLES_REVUE:
            erreurs.append(f"incident {identifiant} soumis à une autorité humaine connue")
        if len(incident.get("interdits", [])) < 3:
            erreurs.append(f"incident {identifiant} avec au moins 3 contournements interdits")
        if incident.get("statut") != "a-faire-relire":
            erreurs.append(f"incident {identifiant} maintenu à faire relire")
    return erreurs


def verifier_accessibilite(registre: dict) -> list[str]:
    """Vérifie que la revue d'accessibilité ne simule ni conformité ni personne réelle."""
    erreurs: list[str] = []
    meta = registre.get("meta", {})
    if (
        meta.get("initiative") != "vote-distanciel-verifiable"
        or meta.get("statut") != "a-faire-expertiser"
        or meta.get("donnees") != "profils-synthetiques-uniquement"
        or meta.get("conformite_declaree") is not False
        or meta.get("essai_avec_personnes_autorise") is not False
    ):
        erreurs.append("accessibilité synthétique, sans conformité déclarée ni essai avec personnes")
    if not meta.get("principe"):
        erreurs.append("accessibilité avec principe d’équivalence du repli")

    barrieres = registre.get("barriere", [])
    ids = [item.get("id") for item in barrieres]
    requis = {
        "navigation-clavier", "lecteur-ecran", "zoom-et-contrastes",
        "comprehension-et-erreurs", "temps-et-fatigue",
        "connexion-ou-equipement-limite", "assistance-humaine",
        "verification-independante",
    }
    if set(ids) != requis or len(ids) != len(set(ids)):
        erreurs.append("exactement 8 barrières d’accessibilité sans doublon")
    for item in barrieres:
        identifiant = item.get("id", "?")
        champs = ("parcours_projete", "preuve_attendue", "repli_a_expertiser", "risque_repli")
        if any(not item.get(champ) for champ in champs):
            erreurs.append(f"barrière {identifiant} avec parcours, preuve, repli et risque")
        if item.get("statut") != "a-faire-expertiser":
            erreurs.append(f"barrière {identifiant} maintenue à faire expertiser")

    garde_fous = registre.get("garde_fou", [])
    ids_garde_fous = {item.get("id") for item in garde_fous}
    requis_garde_fous = {
        "aucune-donnee-de-sante", "equivalence-du-secret",
        "equivalence-statutaire", "publication-humaine",
    }
    if ids_garde_fous != requis_garde_fous or len(garde_fous) != len(ids_garde_fous):
        erreurs.append("exactement 4 garde-fous d’accessibilité sans doublon")
    if any(not item.get("exigence") for item in garde_fous):
        erreurs.append("garde-fous d’accessibilité avec exigences explicites")
    return erreurs


def verifier_assistance(registre: dict) -> list[str]:
    """Vérifie les frontières entre aide, support, procuration et choix."""
    erreurs: list[str] = []
    meta = registre.get("meta", {})
    if (
        meta.get("initiative") != "vote-distanciel-verifiable"
        or meta.get("statut") != "a-faire-relire"
        or meta.get("donnees") != "synthetiques-uniquement"
        or meta.get("execution_autorisee") is not False
    ):
        erreurs.append("assistance synthétique, non exécutable et à faire relire")
    if not meta.get("principe"):
        erreurs.append("assistance avec principe de séparation explicite")

    situations = registre.get("situation", [])
    ids = [item.get("id") for item in situations]
    requis = {
        "explication-generale", "aide-a-la-navigation", "support-technique",
        "procuration-statutaire", "contestation-accessible", "suspicion-de-coercition",
    }
    if set(ids) != requis or len(ids) != len(set(ids)):
        erreurs.append("exactement 6 situations d’assistance sans doublon")
    for item in situations:
        identifiant = item.get("id", "?")
        champs = ("fonction", "autorise_projete", "preuve_attendue", "condition_arret")
        if any(not item.get(champ) for champ in champs):
            erreurs.append(f"situation {identifiant} avec fonction, limite, preuve et arrêt")
        if len(item.get("interdit", [])) < 3:
            erreurs.append(f"situation {identifiant} avec au moins 3 actes interdits")
        if item.get("statut") != "a-faire-relire":
            erreurs.append(f"situation {identifiant} maintenue à faire relire")

    separations = registre.get("separation", [])
    paires = [frozenset((item.get("gauche"), item.get("droite"))) for item in separations]
    if len(separations) != 4 or len(set(paires)) != 4:
        erreurs.append("exactement 4 séparations fonctionnelles sans doublon")
    if any(None in paire or not item.get("raison") for paire, item in zip(paires, separations)):
        erreurs.append("séparations fonctionnelles nommées et motivées")
    paire_assistance_procuration = frozenset(("assistance", "procuration"))
    if paire_assistance_procuration not in paires:
        erreurs.append("assistance explicitement séparée de la procuration")
    return erreurs


def verifier_cles(registre: dict) -> list[str]:
    """Vérifie que le cycle des clés reste synthétique et non exécutable."""
    erreurs: list[str] = []
    meta = registre.get("meta", {})
    if (
        meta.get("initiative") != "vote-distanciel-verifiable"
        or meta.get("statut") != "a-faire-expertiser"
        or meta.get("donnees") != "secrets-synthetiques-uniquement"
        or meta.get("execution_autorisee") is not False
        or meta.get("cryptographie_maison") is not False
    ):
        erreurs.append("cycle des clés synthétique, non exécutable et sans cryptographie maison")
    if not meta.get("principe"):
        erreurs.append("cycle des clés avec principe de séparation")

    phases = registre.get("phase", [])
    ids = [item.get("id") for item in phases]
    requis = {
        "designation-autorites", "generation-distribuee", "verification-avant-ouverture",
        "conservation-temporaire", "depouillement-a-seuil", "destruction-et-contestation",
    }
    if set(ids) != requis or len(ids) != len(set(ids)):
        erreurs.append("exactement 6 phases du cycle des clés sans doublon")
    for item in phases:
        identifiant = item.get("id", "?")
        champs = ("entree_requise", "sortie_attendue", "preuve_attendue", "condition_arret")
        if any(not item.get(champ) for champ in champs):
            erreurs.append(f"phase {identifiant} avec entrée, sortie, preuve et arrêt")
        if len(item.get("interdits", [])) < 3:
            erreurs.append(f"phase {identifiant} avec au moins 3 actes interdits")
        if item.get("statut") != "a-faire-expertiser":
            erreurs.append(f"phase {identifiant} maintenue à faire expertiser")

    incompatibilites = registre.get("incompatibilite", [])
    paires = [frozenset((item.get("gauche"), item.get("droite"))) for item in incompatibilites]
    if len(incompatibilites) != 5 or len(set(paires)) != 5:
        erreurs.append("exactement 5 incompatibilités de rôles sans doublon")
    if any(None in paire or not item.get("raison") for paire, item in zip(paires, incompatibilites)):
        erreurs.append("incompatibilités de rôles nommées et motivées")
    sauvegarde = frozenset(("sauvegarde-centralisee", "plusieurs-parts"))
    if sauvegarde not in paires:
        erreurs.append("centralisation de plusieurs parts explicitement interdite")
    return erreurs


def verifier_chaine_logicielle(registre: dict) -> list[str]:
    """Vérifie le plan de preuves de la chaîne logicielle sans construire de candidat."""
    erreurs: list[str] = []
    meta = registre.get("meta", {})
    if (
        meta.get("initiative") != "vote-distanciel-verifiable"
        or meta.get("statut") != "a-faire-expertiser"
        or meta.get("execution_autorisee") is not False
        or meta.get("selection_effectuee") is not False
    ):
        erreurs.append("chaîne logicielle non exécutée, non sélectionnée et à expertiser")
    if not meta.get("principe"):
        erreurs.append("chaîne logicielle avec principe de traçabilité")

    controles = registre.get("controle", [])
    ids = [item.get("id") for item in controles]
    requis = {
        "source-epinglee", "dependances-fermees", "construction-reproductible",
        "provenance-et-signatures", "analyse-des-ecarts", "mise-a-jour-gelee",
        "retrait-et-verification-future",
    }
    if set(ids) != requis or len(ids) != len(set(ids)):
        erreurs.append("exactement 7 contrôles de chaîne logicielle sans doublon")
    for item in controles:
        identifiant = item.get("id", "?")
        champs = ("question", "preuve_attendue", "condition_arret")
        if any(not item.get(champ) for champ in champs):
            erreurs.append(f"contrôle {identifiant} avec question, preuve et arrêt")
        if len(item.get("interdits", [])) < 3:
            erreurs.append(f"contrôle {identifiant} avec au moins 3 pratiques interdites")
        if item.get("statut") != "a-faire-expertiser":
            erreurs.append(f"contrôle {identifiant} maintenu à faire expertiser")

    portes = registre.get("porte", [])
    if len(portes) != 1:
        erreurs.append("exactement une porte bloquante avant banc")
    else:
        porte = portes[0]
        if (
            porte.get("id") != "avant-banc"
            or set(porte.get("exigences", [])) != requis
            or porte.get("decision") != "revue-humaine-requise"
            or porte.get("statut") != "bloquante"
        ):
            erreurs.append("porte avant banc couvrant les 7 contrôles avec décision humaine")
    return erreurs


def verifier_resultats(registre: dict) -> list[str]:
    """Vérifie que calcul, vérification, contestation et proclamation restent séparés."""
    erreurs: list[str] = []
    meta = registre.get("meta", {})
    if (
        meta.get("initiative") != "vote-distanciel-verifiable"
        or meta.get("statut") != "a-faire-relire"
        or meta.get("donnees") != "synthetiques-uniquement"
        or meta.get("execution_autorisee") is not False
        or meta.get("resultat_autorise") is not False
    ):
        erreurs.append("cycle des résultats synthétique, non exécutable et sans résultat autorisé")
    if not meta.get("principe"):
        erreurs.append("cycle des résultats avec principe de non-proclamation automatique")

    etapes = registre.get("etape", [])
    ids = [item.get("id") for item in etapes]
    requis = {
        "gel-du-tableau", "verification-cryptographique", "verification-statutaire",
        "revue-des-incidents", "fenetre-de-contestation", "decision-de-proclamation",
    }
    if set(ids) != requis or len(ids) != len(set(ids)):
        erreurs.append("exactement 6 étapes du résultat sans doublon")
    for item in etapes:
        identifiant = item.get("id", "?")
        champs = ("entree_requise", "sortie_attendue", "preuve_attendue", "condition_arret")
        if any(not item.get(champ) for champ in champs):
            erreurs.append(f"étape {identifiant} avec entrée, sortie, preuve et arrêt")
        if len(item.get("interdits", [])) < 3:
            erreurs.append(f"étape {identifiant} avec au moins 3 pratiques interdites")
        if item.get("statut") != "a-faire-relire":
            erreurs.append(f"étape {identifiant} maintenue à faire relire")

    publications = registre.get("publication", [])
    if len(publications) != 1:
        erreurs.append("exactement un paquet public minimal projeté")
    else:
        paquet = publications[0]
        if (
            paquet.get("id") != "paquet-public-minimal"
            or len(paquet.get("contenu_projete", [])) < 6
            or len(paquet.get("contenu_interdit", [])) < 6
            or paquet.get("statut") != "a-faire-expertiser"
        ):
            erreurs.append("paquet public minimal complet et maintenu à expertiser")

    portes = registre.get("porte", [])
    if len(portes) != 1:
        erreurs.append("exactement une porte bloquante avant proclamation")
    else:
        porte = portes[0]
        if (
            porte.get("id") != "avant-proclamation"
            or set(porte.get("etapes", [])) != requis
            or porte.get("decision") != "association-decisionnaire"
            or porte.get("statut") != "bloquante"
        ):
            erreurs.append("porte avant proclamation couvrant les 6 étapes et la décision associative")
    return erreurs


def verifier_revues(registre: dict) -> list[str]:
    erreurs: list[str] = []
    meta = registre.get("meta", {})
    if meta.get("initiative") != "vote-distanciel-verifiable" or meta.get("statut") != "a-attribuer":
        erreurs.append("plan de revues relié à l’initiative et maintenu à attribuer")
    roles = registre.get("role", [])
    ids_roles = [role.get("id") for role in roles]
    if set(ids_roles) != ROLES_REVUE or len(ids_roles) != len(set(ids_roles)):
        erreurs.append("plan contenant exactement les 6 rôles de revue")
    for role in roles:
        if role.get("statut") != "a-attribuer" or not role.get("responsabilite") or not role.get("preuve_attendue"):
            erreurs.append(f"rôle {role.get('id', '?')} non attribué avec responsabilité et preuve")
        if any(champ in role for champ in ("nom", "courriel", "personne")):
            erreurs.append(f"rôle {role.get('id', '?')} sans donnée personnelle")
    revues = registre.get("revue", [])
    ids_revues = [revue.get("id") for revue in revues]
    if set(ids_revues) != REVUES_REQUISES or len(ids_revues) != len(set(ids_revues)):
        erreurs.append("plan contenant exactement les 5 revues requises")
    roles_couverts: set[str] = set()
    for revue in revues:
        requis = set(revue.get("roles_requis", []))
        inconnus = requis - ROLES_REVUE
        if inconnus:
            erreurs.append(f"revue {revue.get('id', '?')} avec rôles inconnus")
        roles_couverts.update(requis)
        artefacts = revue.get("artefacts", [])
        if not artefacts or any(not (RACINE / chemin).is_file() for chemin in artefacts):
            erreurs.append(f"revue {revue.get('id', '?')} avec artefacts existants")
        if revue.get("statut") != "a-attribuer" or not revue.get("question") or not revue.get("condition_sortie"):
            erreurs.append(f"revue {revue.get('id', '?')} maintenue à attribuer et bornée")
    if roles_couverts != ROLES_REVUE:
        erreurs.append("les 6 rôles sont mobilisés par au moins une revue")
    decision = next((revue for revue in revues if revue.get("id") == "decision-de-phase"), {})
    if set(decision.get("roles_requis", [])) != ROLES_REVUE:
        erreurs.append("décision de phase soumise aux 6 rôles")
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


def extraire_section(markdown: str, titre: str) -> str:
    """Retourne le texte d'une section de niveau 2, sans son titre."""
    index = markdown.find(titre)
    if index < 0:
        return ""
    debut = index + len(titre)
    suivant = markdown.find("\n## ", debut)
    return markdown[debut: suivant if suivant >= 0 else len(markdown)]


def lignes_tableau(section: str) -> list[str]:
    return [
        ligne for ligne in section.splitlines()
        if ligne.startswith("|") and not re.match(r"^\|\s*-", ligne)
    ]


def verifier_dossier(
    markdown: str,
    profils: dict,
    regles: dict,
    menaces: dict,
    cas_essai: dict,
    revues: dict,
    comparaison: dict,
) -> list[str]:
    """Vérifie que le dossier de délibération reste fidèle aux registres, sans rien décider."""
    erreurs: list[str] = []
    for titre in SECTIONS_DOSSIER:
        if titre not in markdown:
            erreurs.append(f"section de dossier absente : {titre}")

    texte_normalise = markdown.casefold()
    for formule in FORMULES_INTERDITES_DOSSIER:
        if formule in texte_normalise:
            erreurs.append(f"formule de promesse interdite dans le dossier : {formule!r}")

    compte_profils = len(profils.get("profil", []))
    compte_regles = len(regles.get("regle", []))
    compte_menaces = len(menaces.get("menace", []))
    compte_cas = len(cas_essai.get("cas", []))
    compte_criteres = len(comparaison.get("critere", []))
    compte_roles = len(revues.get("role", []))
    compte_revues = len(revues.get("revue", []))
    attendus = [
        (f"{compte_profils} profils", "nombre de profils"),
        (f"{compte_regles} relevés", "nombre de règles relevées"),
        (f"{compte_menaces} menaces", "nombre de menaces"),
        (f"{compte_cas} cas", "nombre de cas d’essai"),
        (f"{compte_criteres} critères bloquants", "nombre de critères"),
        (f"{compte_roles} rôles et {compte_revues} revues", "nombre de rôles et de revues"),
    ]
    for expression, libelle in attendus:
        if expression not in markdown:
            erreurs.append(f"dossier incohérent avec le registre : {libelle} attendu « {expression} »")

    section_profils = extraire_section(markdown, "## 3. Les huit profils, un par un")
    section_synthese = extraire_section(section_profils, "### 3.9 Tableau de synthèse — sans classement")
    for profil in profils.get("profil", []):
        identifiant = profil.get("id", "")
        statut = profil.get("statut", "")
        if f"`{identifiant}`" not in section_profils:
            erreurs.append(f"profil de dossier absent : {identifiant}")
            continue
        motif = rf"^\| `{re.escape(identifiant)}` \|.*\| `{re.escape(statut)}` \|\s*$"
        if not re.search(motif, section_synthese, re.M):
            erreurs.append(f"statut du profil {identifiant} non repris à l’identique dans la synthèse")

    if "`aucun`" not in markdown:
        erreurs.append("possibilité de ne retenir aucun profil absente du dossier")

    for voie, intitule in (("A", "Ne pas voter à distance"), ("B", "Expertiser un service existant"), ("C", "Auto-héberger un logiciel existant")):
        if f"### Voie {voie} — {intitule}" not in markdown:
            erreurs.append(f"voie {voie} absente ou renommée dans le dossier")
    if "### Voie D — Construire un système" not in markdown or "bloquée" not in extraire_section(markdown, "### Voie D — Construire un système"):
        erreurs.append("voie D non présentée comme bloquée")

    ambiguites = [
        ligne for ligne in lignes_tableau(extraire_section(markdown, "## 5. Les huit ambiguïtés à trancher"))
        if re.match(r"^\|\s*\d+\s*\|", ligne)
    ]
    if len(ambiguites) != 8:
        erreurs.append(f"huit ambiguïtés attendues dans le dossier : {len(ambiguites)} ligne(s) numérotée(s)")

    conditions = [
        ligne for ligne in lignes_tableau(extraire_section(markdown, "## 7. Les quinze conditions cumulatives"))
        if re.match(r"^\|\s*\d+\s*\|", ligne)
    ]
    if len(conditions) != 15:
        erreurs.append(f"quinze conditions attendues dans le dossier : {len(conditions)} ligne(s) numérotée(s)")

    objections = lignes_tableau(extraire_section(markdown, "## 10. Registre des objections"))
    if len(objections) < 2:
        erreurs.append("registre des objections absent : en-tête de tableau attendu")

    if "Seul le tableau du §6" not in markdown:
        erreurs.append("renvoi au tableau de décision faisant foi absent")

    section_trace = extraire_section(markdown, "## 8. Trace de décision à remplir")
    if re.search(
        r"Profil retenu\s*\|\s*`?(?:bureau-executif|conseil-ethique|territoriale-constitutive|ago-|age-|dissolution|aucun)",
        section_trace,
    ):
        erreurs.append("le dossier ne doit pas présélectionner un profil : la décision reste en attente")
    return erreurs


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
    menaces = registre.get("menace", [])
    ids = [menace.get("id") for menace in menaces]
    if set(ids) != MENACES_REQUISES or len(ids) != len(set(ids)):
        manquants.append("registre contenant exactement les 10 menaces requises sans doublon")
    for index, menace in enumerate(menaces, start=1):
        champs_vides = [champ for champ in CHAMPS_MENACE if not menace.get(champ)]
        if champs_vides:
            manquants.append(f"menace {index} avec champs renseignés : {', '.join(sorted(champs_vides))}")
        if menace.get("statut") != "a-expertiser":
            manquants.append(f"menace {menace.get('id', index)} maintenue à l’état a-expertiser")
    invariants = registre.get("invariant", [])
    if len(invariants) < 7 or any(not item.get("preuve_attendue") for item in invariants):
        manquants.append("au moins 7 invariants avec preuve attendue")
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

    with DONNEES.open("rb") as fichier:
        donnees = tomllib.load(fichier)
    manquants.extend(verifier_donnees(donnees))

    with CORRELATION.open("rb") as fichier:
        correlation = tomllib.load(fichier)
    manquants.extend(verifier_correlation(correlation))

    with CONTINUITE.open("rb") as fichier:
        continuite = tomllib.load(fichier)
    manquants.extend(verifier_continuite(continuite))

    with ACCESSIBILITE.open("rb") as fichier:
        accessibilite = tomllib.load(fichier)
    manquants.extend(verifier_accessibilite(accessibilite))

    with ASSISTANCE.open("rb") as fichier:
        assistance = tomllib.load(fichier)
    manquants.extend(verifier_assistance(assistance))

    with CLES.open("rb") as fichier:
        cles = tomllib.load(fichier)
    manquants.extend(verifier_cles(cles))

    with CHAINE_LOGICIELLE.open("rb") as fichier:
        chaine_logicielle = tomllib.load(fichier)
    manquants.extend(verifier_chaine_logicielle(chaine_logicielle))

    with RESULTATS.open("rb") as fichier:
        resultats = tomllib.load(fichier)
    manquants.extend(verifier_resultats(resultats))

    with REVUES.open("rb") as fichier:
        revues = tomllib.load(fichier)
    manquants.extend(verifier_revues(revues))

    etat_decision, erreurs_decision = verifier_decision(DECISION.read_text(encoding="utf-8"))
    manquants.extend(erreurs_decision)

    dossier = DOSSIER.read_text(encoding="utf-8") if DOSSIER.is_file() else ""
    if not dossier:
        manquants.append("dossier de délibération présent")
    else:
        manquants.extend(verifier_dossier(dossier, profils, regles, registre, cas_essai, revues, comparaison))

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
        "à expertiser, 18 règles et 8 profils statutaires à relire, 12 cas synthétiques à concevoir, "
        f"4 options et 15 critères sans score, 3 sources à évaluer, 8 catégories, 6 liaisons interdites, 5 signaux de corrélation, 7 incidents de continuité, 8 barrières d’accessibilité, 6 situations d’assistance, 6 phases de clés, 7 contrôles logiciels et 6 étapes de résultat, "
        f"6 rôles et 5 revues à attribuer, décision {etat_decision}, initiative P0 à cadrer, "
        "dossier de délibération cohérent avec les registres, "
        "aucune identité ni bulletin réel autorisé."
    )
    return 0


if __name__ == "__main__":
    try:
        sys.exit(principal())
    except (OSError, tomllib.TOMLDecodeError) as erreur:
        print(f"Cadrage du vote distanciel impossible à vérifier : {erreur}", file=sys.stderr)
        sys.exit(1)
