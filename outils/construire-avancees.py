#!/usr/bin/env python3
"""Rend lisible et vérifiable le registre des avancées réutilisables de la R&D.

Ce script ne juge aucune avancée. Il vérifie qu'une entrée est **traçable** :
une preuve locale qui existe, un contrôle qu'on peut exécuter, une limite
écrite, une suite et une initiative du portefeuille. Il produit
`docs/rd/avancees.md` à partir de `docs/rd/avancees.toml`.

La différence avec le journal : le journal raconte un lot dans l'ordre du temps ;
ce registre retient ce qui reste vrai après le lot et ce qu'un autre agent doit
savoir pour ne pas le défaire. Une avancée sans limite écrite n'y entre pas.

Usage :
    python3 outils/construire-avancees.py              # écrit docs/rd/avancees.md
    python3 outils/construire-avancees.py --verifier   # échoue si le fichier a divergé
    python3 outils/construire-avancees.py --sortie autre.md
"""

from __future__ import annotations

import argparse
import sys
import tomllib
from datetime import date
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
SOURCE = RACINE / "docs" / "rd" / "avancees.toml"
PORTEFEUILLE = RACINE / "docs" / "rd" / "portefeuille.toml"
SORTIE = RACINE / "docs" / "rd" / "avancees.md"

CHAMPS = ("id", "date", "titre", "constat", "changement", "preuves", "controle", "limite", "suite", "initiatives")
LIMITE_MIN = 120


def charger(source: Path = SOURCE) -> dict:
    return tomllib.loads(source.read_text(encoding="utf-8"))


def initiatives_connues(portefeuille: Path = PORTEFEUILLE) -> set[str]:
    registre = tomllib.loads(portefeuille.read_text(encoding="utf-8"))
    return {str(initiative.get("id", "")) for initiative in registre.get("initiative", [])}


def valider(registre: dict, aujourdhui: date, connues: set[str] | None = None) -> list[str]:
    """Retourne la liste des erreurs de traçabilité. Aucune erreur = registre exploitable."""
    erreurs: list[str] = []
    avancees = registre.get("avancee")
    if not isinstance(avancees, list) or not avancees:
        return ["aucune avancée déclarée"]
    if connues is None:
        connues = initiatives_connues()
    vus: set[str] = set()
    for index, avancee in enumerate(avancees, start=1):
        if not isinstance(avancee, dict):
            erreurs.append(f"entrée {index} : ce n'est pas une table")
            continue
        identifiant = str(avancee.get("id", "")).strip()
        etiquette = identifiant or f"entrée {index}"
        absents = [champ for champ in CHAMPS if not avancee.get(champ)]
        if absents:
            erreurs.append(f"{etiquette} : champs manquants {', '.join(absents)}")
        if not identifiant:
            continue
        if identifiant in vus:
            erreurs.append(f"{etiquette} : identifiant dupliqué")
        vus.add(identifiant)
        if not identifiant.replace("-", "").isalnum() or identifiant != identifiant.lower():
            erreurs.append(f"{etiquette} : identifiant non slug (minuscules, chiffres et tirets)")
        quand = avancee.get("date")
        if not isinstance(quand, date):
            erreurs.append(f"{etiquette} : date absente ou non lue comme une date")
        elif quand > aujourdhui:
            erreurs.append(f"{etiquette} : date dans le futur ({quand.isoformat()})")
        preuves = avancee.get("preuves") or []
        if not isinstance(preuves, list) or len(preuves) < 2:
            erreurs.append(f"{etiquette} : au moins deux preuves locales sont exigées")
        else:
            manquantes = [str(ref) for ref in preuves if not (RACINE / str(ref)).exists()]
            if manquantes:
                erreurs.append(f"{etiquette} : preuves absentes du dépôt {', '.join(manquantes)}")
        controle = str(avancee.get("controle", "")).strip()
        if controle and not any(mot in controle for mot in ("outils/", "npm ", "node ")):
            erreurs.append(f"{etiquette} : le contrôle doit citer un outil du dépôt")
        limite = str(avancee.get("limite", "")).strip()
        if limite and len(limite) < LIMITE_MIN:
            erreurs.append(f"{etiquette} : limite trop courte ({len(limite)} caractères, {LIMITE_MIN} exigés)")
        initiatives = avancee.get("initiatives") or []
        if not isinstance(initiatives, list):
            erreurs.append(f"{etiquette} : « initiatives » doit être une liste")
        else:
            inconnues = sorted(set(map(str, initiatives)) - connues)
            if inconnues:
                erreurs.append(f"{etiquette} : initiatives absentes du portefeuille {', '.join(inconnues)}")
    return erreurs


def resumer(registre: dict) -> dict[str, object]:
    avancees = [a for a in registre.get("avancee", []) if isinstance(a, dict)]
    dates = sorted(a["date"] for a in avancees if isinstance(a.get("date"), date))
    outils = sorted({partie.strip() for a in avancees for partie in str(a.get("controle", "")).split("&&") if partie.strip()})
    return {
        "nombre": len(avancees),
        "premiere": dates[0] if dates else None,
        "derniere": dates[-1] if dates else None,
        "controles": outils,
        "initiatives": sorted({str(i) for a in avancees for i in (a.get("initiatives") or [])}),
    }


def construire(registre: dict, aujourdhui: date) -> str:
    chiffres = resumer(registre)
    lignes: list[str] = [
        "# Avancées réutilisables de la R&D",
        "",
        "**Document de travail généré.** Il ne certifie rien et ne remplace ni une relecture, ni un audit, "
        "ni une décision éditoriale. Il retient ce qu'un lot a appris de durable, avec la preuve locale qui "
        "le soutient, le contrôle qui le maintient et la limite qui l'accompagne.",
        "",
        "**À quoi cela sert :** un autre agent reprend le projet sans avoir à reconstituer l'histoire. "
        "Chaque entrée dit aussi ce qu'elle ne prouve pas, pour qu'une avancée ne se transforme pas en argument "
        "d'autorité.",
        "",
        f"**Date de génération :** {aujourdhui.isoformat()}.",
        "",
        "## 1. Vue d'ensemble",
        "",
        "| Mesure | Valeur |",
        "| --- | ---: |",
        f"| Avancées consignées | {chiffres['nombre']} |",
    ]
    if chiffres["premiere"] and chiffres["derniere"]:
        lignes.append(f"| Période couverte | du {chiffres['premiere'].isoformat()} au {chiffres['derniere'].isoformat()} |")
    lignes.append(f"| Contrôles exécutables cités | {len(chiffres['controles'])} |")
    lignes.append(f"| Initiatives du portefeuille concernées | {len(chiffres['initiatives'])} |")
    lignes.append("")
    lignes.append(
        "Ces nombres mesurent la traçabilité du registre, pas la valeur des avancées. Une entrée peut être "
        "parfaitement traçable et se révéler fausse plus tard : c'est le contrôle qui la contredira."
    )
    lignes.append("")
    lignes.append("## 2. Les avancées")
    lignes.append("")
    for avancee in sorted(registre.get("avancee", []), key=lambda a: (a.get("date") or aujourdhui, a.get("id", ""))):
        lignes.append(f"### `{avancee['id']}` — {avancee['titre']}")
        lignes.append("")
        lignes.append(f"*Consignée le {avancee['date'].isoformat()}.*")
        lignes.append("")
        lignes.append(f"**Constat.** {avancee['constat']}")
        lignes.append("")
        lignes.append(f"**Ce que cela change.** {avancee['changement']}")
        lignes.append("")
        lignes.append("**Preuves dans le dépôt :**")
        lignes.append("")
        for preuve in avancee["preuves"]:
            lignes.append(f"- `{preuve}`")
        lignes.append("")
        lignes.append(f"**Contrôle qui la maintient :** `{avancee['controle']}`")
        lignes.append("")
        lignes.append(f"**Limite — ce que cela ne prouve pas.** {avancee['limite']}")
        lignes.append("")
        lignes.append(f"**Suite.** {avancee['suite']}")
        lignes.append("")
        lignes.append("Initiatives liées : " + ", ".join(f"`{identifiant}`" for identifiant in avancee["initiatives"]) + ".")
        lignes.append("")
    lignes.append("## 3. Ce que ce registre ne dit pas")
    lignes.append("")
    lignes.append("- Il ne dit pas qu'une fiche est relue, juste ou publiable : la relecture humaine reste dans `docs/apprentissage/relectures.toml`.")
    lignes.append("- Il ne remplace pas le journal : le journal garde l'ordre des décisions, ce registre garde ce qui reste vrai après elles.")
    lignes.append("- Il ne détecte pas une avancée devenue fausse : seule une personne qui relit le registre peut retirer une entrée.")
    lignes.append("- Il ne mesure ni usage, ni qualité, ni apprentissage : aucun chiffre d'audience n'y entre.")
    lignes.append("")
    lignes.append("## 4. Ajouter une avancée")
    lignes.append("")
    lignes.append("1. Vérifier que l'apprentissage reste vrai au-delà du lot : sinon, c'est une note de journal.")
    lignes.append("2. Écrire l'entrée dans `docs/rd/avancees.toml` : constat, changement, deux preuves locales au moins, contrôle exécutable, limite d'au moins 120 caractères, suite, initiative du portefeuille.")
    lignes.append("3. Régénérer avec `python3 outils/construire-avancees.py`, puis lancer `python3 outils/test_avancees.py`.")
    lignes.append("4. Retirer sans regret une entrée devenue fausse : la mémoire du projet n'est pas un palmarès.")
    lignes.append("")
    lignes.append("Généré depuis `docs/rd/avancees.toml` ; vérifier avec `--verifier`.")
    lignes.append("")
    return "\n".join(lignes)


def main() -> int:
    analyseur = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    analyseur.add_argument("--verifier", action="store_true", help="échouer si le fichier a divergé")
    analyseur.add_argument("--sortie", type=Path, default=SORTIE, help="chemin du fichier produit")
    arguments = analyseur.parse_args()

    try:
        registre = charger()
    except (OSError, tomllib.TOMLDecodeError) as erreur:
        print(f"Registre des avancées illisible : {erreur}", file=sys.stderr)
        return 2

    aujourdhui = date.today()
    erreurs = valider(registre, aujourdhui)
    if erreurs:
        print("Registre des avancées non traçable :", file=sys.stderr)
        for erreur in erreurs:
            print(f"  - {erreur}", file=sys.stderr)
        return 1

    contenu = construire(registre, aujourdhui)
    sortie = arguments.sortie if arguments.sortie.is_absolute() else RACINE / arguments.sortie
    nom = str(sortie.relative_to(RACINE)) if sortie.is_relative_to(RACINE) else str(sortie)
    if arguments.verifier:
        if not sortie.exists():
            print(f"{nom} absent : lancez le script sans --verifier.", file=sys.stderr)
            return 1
        if sortie.read_text(encoding="utf-8") != contenu:
            print(f"{nom} a divergé du registre : régénérez-le.", file=sys.stderr)
            return 1
        chiffres = resumer(registre)
        print(f"Les avancées sont à jour ({nom}) : {chiffres['nombre']} entrées traçables.")
        return 0

    sortie.parent.mkdir(parents=True, exist_ok=True)
    sortie.write_text(contenu, encoding="utf-8")
    chiffres = resumer(registre)
    print(f"{nom} écrit : {len(contenu)} caractères — {chiffres['nombre']} avancées traçables.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
