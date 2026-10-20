#!/usr/bin/env python3
"""Contrôle le registre des relectures humaines, sans jamais en écrire une à la place de personne.

Le registre `docs/apprentissage/relectures.toml` est le seul endroit où une
relecture humaine est consignée. Ce script ne relit rien, ne note rien, ne
valide rien : il vérifie que ce qui est consigné est complet, daté, rattaché à
une fiche réelle et **cohérent avec le catalogue**.

La cohérence est réciproque, pour qu'aucun statut ne bouge en silence :

- une fiche au statut « Relu — relecture consignée » doit avoir une relecture
  « conforme » comme dernière entrée ;
- une fiche au statut « Prototype à relire » ne peut pas avoir une dernière
  relecture « conforme » : il faudrait alors changer son statut ;
- une fiche sans statut (corpus initial) n'est pas concernée : son absence de
  marqueur ne vaut ni relecture ni validation.

Usage :
    python3 outils/registre-relecture.py                 # contrôle + état
    python3 outils/registre-relecture.py --etat          # état seul, sans échec
    python3 outils/registre-relecture.py --modele <fiche>  # bloc TOML à compléter
"""

from __future__ import annotations

import argparse
import sys
import tomllib
from datetime import date
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent

# Statuts éditoriaux : définitions partagées, jamais recopiées en chaîne locale.
sys.path.insert(0, str(RACINE / "outils"))
from statuts_editoriaux import PROTOTYPE, RELU, est_prototype, est_relue  # noqa: E402

REGISTRE = RACINE / "docs" / "apprentissage" / "relectures.toml"
CATALOGUE = RACINE / "docs" / "apprentissage" / "catalogue.toml"
VERDICTS = ("conforme", "a-corriger", "insuffisant")
CHAMPS_OBLIGATOIRES = ("fiche", "date", "role", "perimetre", "verdict", "suite")


def charger_catalogue() -> dict[str, dict]:
    with CATALOGUE.open("rb") as fichier:
        return {fiche["id"]: fiche for fiche in tomllib.load(fichier).get("fiche", [])}


def charger_registre(erreurs: list[str]) -> list[dict]:
    if not REGISTRE.is_file():
        erreurs.append("docs/apprentissage/relectures.toml absent : le registre des relectures est obligatoire")
        return []
    try:
        with REGISTRE.open("rb") as fichier:
            donnees = tomllib.load(fichier)
    except (OSError, tomllib.TOMLDecodeError) as erreur:
        erreurs.append(f"docs/apprentissage/relectures.toml illisible : {erreur}")
        return []
    if donnees.get("version") != 1:
        erreurs.append("relectures.toml : version attendue : 1")
    entrees = donnees.get("relecture", [])
    if not isinstance(entrees, list):
        erreurs.append("relectures.toml : « relecture » doit être une liste d'entrées")
        return []
    return entrees


def controler_entree(index: int, entree: object, fiches: dict[str, dict], aujourdhui: date, erreurs: list[str]) -> None:
    if not isinstance(entree, dict):
        erreurs.append(f"relecture #{index} : entrée invalide")
        return
    manquants = [champ for champ in CHAMPS_OBLIGATOIRES if not entree.get(champ)]
    if manquants:
        erreurs.append(f"relecture #{index} : champ(s) obligatoire(s) absent(s) : {', '.join(manquants)}")
        return
    identifiant = entree["fiche"]
    if identifiant not in fiches:
        erreurs.append(f"relecture #{index} : fiche inconnue du catalogue : {identifiant}")
    if not isinstance(entree["date"], date):
        erreurs.append(f"relecture #{index} ({identifiant}) : date éditoriale explicite attendue, AAAA-MM-JJ")
    elif entree["date"] > aujourdhui:
        erreurs.append(f"relecture #{index} ({identifiant}) : date future interdite")
    if entree["verdict"] not in VERDICTS:
        erreurs.append(
            f"relecture #{index} ({identifiant}) : verdict inconnu « {entree['verdict']} », "
            f"attendu : {', '.join(VERDICTS)}"
        )
    perimetre = entree["perimetre"]
    if not isinstance(perimetre, list) or not all(isinstance(item, str) and item.strip() for item in perimetre):
        erreurs.append(f"relecture #{index} ({identifiant}) : « perimetre » doit être une liste de textes non vides")
    objections = entree.get("objections", [])
    if not isinstance(objections, list):
        erreurs.append(f"relecture #{index} ({identifiant}) : « objections » doit être une liste")
    elif entree["verdict"] != "conforme" and not objections:
        erreurs.append(
            f"relecture #{index} ({identifiant}) : un verdict « {entree['verdict']} » exige au moins une objection écrite"
        )
    for champ in ("points_bloquants", "sources_ouvertes"):
        valeur = entree.get(champ, [])
        if not isinstance(valeur, list) or not all(isinstance(item, str) for item in valeur):
            erreurs.append(f"relecture #{index} ({identifiant}) : « {champ} » doit être une liste de textes")
    droits = entree.get("droits_verifies_le")
    if droits is not None:
        if not isinstance(droits, date):
            erreurs.append(f"relecture #{index} ({identifiant}) : droits_verifies_le doit être une date")
        elif droits > aujourdhui:
            erreurs.append(f"relecture #{index} ({identifiant}) : droits_verifies_le ne peut pas être futur")
    for cle in ("role", "suite"):
        if isinstance(entree.get(cle), str) and not entree[cle].strip():
            erreurs.append(f"relecture #{index} ({identifiant}) : « {cle} » vide")


def controler_coherence(entrees: list[dict], fiches: dict[str, dict], erreurs: list[str]) -> dict[str, dict]:
    """Croise registre et catalogue : aucun statut ne change sans trace, et réciproquement."""
    dernieres: dict[str, dict] = {}
    for entree in entrees:
        identifiant = entree.get("fiche")
        if not isinstance(identifiant, str) or not isinstance(entree.get("date"), date):
            continue
        actuelle = dernieres.get(identifiant)
        if actuelle is None or entree["date"] > actuelle["date"]:
            dernieres[identifiant] = entree
    for identifiant, entree in dernieres.items():
        fiche = fiches.get(identifiant)
        if fiche is None:
            continue
        conforme = entree.get("verdict") == "conforme"
        if conforme and not est_relue(fiche):
            erreurs.append(
                f"{identifiant} : relecture conforme du {entree['date']} mais statut « {fiche.get('statut_editorial') or 'aucun'} » ; "
                f"passer la fiche au statut « {RELU} » avec sa note, ou corriger le verdict"
            )
        if not conforme and est_relue(fiche):
            erreurs.append(
                f"{identifiant} : statut « {RELU} » alors que la dernière relecture du {entree['date']} donne "
                f"« {entree.get('verdict')} » ; le statut doit redevenir « {PROTOTYPE} »"
            )
    for identifiant, fiche in fiches.items():
        if est_relue(fiche) and identifiant not in dernieres:
            erreurs.append(
                f"{identifiant} : statut « {RELU} » sans aucune relecture au registre — un statut ne se déclare pas"
            )
    return dernieres


def resumer(fiches: dict[str, dict], dernieres: dict[str, dict]) -> str:
    prototypes = [fiche for fiche in fiches.values() if est_prototype(fiche)]
    relues = [fiche for fiche in fiches.values() if est_relue(fiche)]
    initiales = len(fiches) - len(prototypes) - len(relues)
    compte = {verdict: 0 for verdict in VERDICTS}
    for entree in dernieres.values():
        if entree.get("verdict") in compte:
            compte[entree["verdict"]] += 1
    return (
        f"Registre de relecture : {len(dernieres)} fiche(s) avec relecture consignée "
        f"(conforme {compte['conforme']}, à corriger {compte['a-corriger']}, insuffisant {compte['insuffisant']}) — "
        f"{len(relues)} fiche(s) au statut « {RELU} », {len(prototypes)} prototype(s) en attente, "
        f"{initiales} entrée(s) du corpus initial sans statut."
    )


def modele(identifiant: str, fiches: dict[str, dict]) -> str:
    fiche = fiches.get(identifiant)
    if fiche is None:
        return f"# Fiche inconnue du catalogue : {identifiant}"
    statut = fiche.get("statut_editorial") or "aucun statut (corpus initial)"
    return "\n".join(
        [
            f"# Paquet de relecture : python3 outils/construire-paquets-relecture.py --fiche {identifiant}",
            f"# Statut actuel dans le catalogue : {statut}",
            f"# Titre : {fiche['titre']}",
            "",
            "[[relecture]]",
            f'fiche = "{identifiant}"',
            "date = AAAA-MM-JJ",
            'role = "expertise du domaine — préciser lequel"',
            'perimetre = ["exemples et corrections", "sources et droits", "accessibilité"]',
            'verdict = "conforme"          # conforme | a-corriger | insuffisant',
            "sources_ouvertes = []",
            "droits_verifies_le = AAAA-MM-JJ",
            "objections = []",
            "points_bloquants = []",
            'suite = "ce qui est décidé ensuite, et par qui"',
        ]
    )


def main() -> int:
    analyseur = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    analyseur.add_argument("--etat", action="store_true", help="afficher l'état sans échouer sur une incohérence")
    analyseur.add_argument("--modele", metavar="FICHE", help="imprimer un bloc [[relecture]] à compléter")
    arguments = analyseur.parse_args()

    try:
        fiches = charger_catalogue()
    except (OSError, KeyError, tomllib.TOMLDecodeError) as erreur:
        print(f"Catalogue illisible : {erreur}", file=sys.stderr)
        return 2

    if arguments.modele:
        print(modele(arguments.modele, fiches))
        return 0

    erreurs: list[str] = []
    entrees = charger_registre(erreurs)
    aujourdhui = date.today()
    for index, entree in enumerate(entrees, start=1):
        controler_entree(index, entree, fiches, aujourdhui, erreurs)
    dernieres = controler_coherence(entrees, fiches, erreurs)
    print(resumer(fiches, dernieres))
    if erreurs and not arguments.etat:
        print("\nÉCHECS :", file=sys.stderr)
        for erreur in erreurs:
            print(f"- {erreur}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
