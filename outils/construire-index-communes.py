#!/usr/bin/env python3
"""Écrit l'index de recherche des communes, et refuse un index faux ou périmé.

La carte charge un département à la fois : le champ « Chercher une commune »
ne peut donc pas trouver une commune dont le département n'est pas ouvert, à
moins de télécharger les cent douze fichiers — ce que personne ne veut. Cet
index ne porte que deux choses, le nom et le code INSEE de chaque commune,
pour que la recherche puisse répondre sans rien inventer et sans télécharger
les prix. Les coordonnées, la population et les prix restent dans le fichier du
département : c'est lui qui a la charge de la fiche.

L'index est un **dérivé** des fichiers `d-<département>.json` : ce programme le
recalcule, il ne l'écrit jamais à partir d'autre chose. `--verifier` le
recalcule encore et compare les octets ; un index qui ne correspond plus à la
collecte est refusé, jamais corrigé en silence.

Usage :
    python3 outils/construire-index-communes.py
    python3 outils/construire-index-communes.py --verifier
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path

RACINE = Path(os.environ.get("MRSC_RACINE") or Path(__file__).resolve().parent.parent).resolve()
DONNEES = RACINE / "assets" / "data" / "vie-chere"
SORTIE = DONNEES / "communes-index.json"

#: En dessous, l'index ne couvre plus la France : une collecte amputée passerait
#: pour une recherche complète. La métropole compte un peu moins de 35 000
#: communes ; le plancher laisse la marge des fusions annuelles, pas plus.
MINIMUM_COMMUNES = 30_000

#: Un nom de commune n'est jamais un code : « 69123 » à la place de « Lyon »
#: ferait afficher un lieu qui n'existe pas (même leçon que `L7500` pour les
#: loyers, le 14 novembre 2026). Le motif exige un chiffre : la première version
#: refusait « Y », la commune de la Somme, parce qu'un nom d'une lettre en
#: capitale ressemble à un code. Aucun nom de commune ne contient de chiffre.
MOTIF_NOM_DE_CODE = re.compile(r"^[A-Z0-9 ]*\d[A-Z0-9 ]*$")


class Refus(Exception):
    """Un défaut qui empêche d'écrire un index honnête."""


def fichiers_departements(donnees: Path = DONNEES) -> list[Path]:
    return sorted(donnees.glob("d-*.json"))


def lire_json(chemin: Path) -> dict:
    try:
        return json.loads(chemin.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as erreur:
        raise Refus(f"{chemin.name} illisible : {erreur}") from erreur


def construire(donnees: Path = DONNEES, minimum: int = MINIMUM_COMMUNES) -> dict:
    """Recalcule l'index depuis les fichiers de département, sans rien croire."""
    etat = donnees / "_etat.json"
    if not etat.is_file():
        raise Refus(
            "aucune collecte : `_etat.json` est absent. L'index ne se fabrique pas "
            "à partir d'autre chose que la collecte."
        )
    collecte = str(lire_json(etat).get("collecte") or "")
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", collecte):
        raise Refus(f"date de collecte illisible dans `_etat.json` : {collecte!r}")

    fichiers = fichiers_departements(donnees)
    if not fichiers:
        raise Refus("aucun fichier `d-<département>.json` : il n'y a rien à indexer")

    communes: list[list] = []
    codes: set[str] = set()
    for chemin in fichiers:
        contenu = lire_json(chemin)
        departement = str(contenu.get("d") or "")
        if chemin.stem != f"d-{departement}":
            raise Refus(f"{chemin.name} annonce le département {departement!r}")
        for commune in contenu.get("communes") or []:
            nom = str(commune.get("n") or "").strip()
            code = str(commune.get("c") or "").strip()
            if not nom or not code:
                raise Refus(f"{chemin.name} : une commune sans nom ou sans code")
            if not code.startswith(departement):
                raise Refus(
                    f"{chemin.name} : le code {code!r} ne commence pas par le département "
                    f"{departement!r} — l'index enverrait la recherche au mauvais endroit"
                )
            if code in codes:
                raise Refus(f"code {code!r} présent deux fois : deux communes porteraient le même")
            codes.add(code)
            if MOTIF_NOM_DE_CODE.match(nom):
                raise Refus(f"{code} : le nom {nom!r} est un code, pas un lieu")
            if any(0x80 <= ord(caractere) <= 0x9F for caractere in nom):
                raise Refus(f"{code} : le nom {nom!r} contient un caractère de contrôle illisible")
            # Un troisième champ dit si la collecte publie un prix pour cette
            # commune. La liste de suggestions peut donc prévenir avant le clic
            # qu'une commune n'a pas de prix, au lieu de laisser la fiche
            # l'apprendre. Ce n'est pas un prix : c'est la présence d'un prix.
            avec_prix = 1 if (commune.get("pa") or commune.get("pm")) else 0
            communes.append([nom, code, avec_prix])

    if len(communes) < minimum:
        raise Refus(
            f"{len(communes)} commune(s) indexée(s), au moins {minimum} attendues : "
            "un index tronqué ferait dire « aucune commune » à une recherche juste"
        )
    communes.sort(key=lambda entree: (entree[0], entree[1]))
    return {"collecte": collecte, "communes": communes}


def serialiser(index: dict) -> bytes:
    return (json.dumps(index, ensure_ascii=False, separators=(",", ":")) + "\n").encode("utf-8")


def ecrire(chemin: Path = SORTIE, donnees: Path = DONNEES, minimum: int = MINIMUM_COMMUNES) -> int:
    index = construire(donnees, minimum)
    contenu = serialiser(index)
    chemin.parent.mkdir(parents=True, exist_ok=True)
    provisoire = chemin.with_name(chemin.name + ".ecriture")
    provisoire.write_bytes(contenu)
    # Remplacement seulement quand tout est écrit : un index interrompu ne doit
    # pas laisser la recherche à moitié muette.
    provisoire.replace(chemin)
    print(
        f"Index de recherche écrit : {len(index['communes'])} communes, "
        f"{len(contenu) // 1024} Kio, collecte du {index['collecte']}."
    )
    return 0


def verifier(chemin: Path = SORTIE, donnees: Path = DONNEES, minimum: int = MINIMUM_COMMUNES) -> int:
    if not chemin.is_file():
        print(
            f"ERREUR — aucun index de recherche dans {chemin} : la page dirait « aucune "
            "commune » à une recherche juste.",
            file=sys.stderr,
        )
        return 1
    try:
        attendu = serialiser(construire(donnees, minimum))
    except Refus as erreur:
        print(f"ERREUR — {erreur}", file=sys.stderr)
        return 1
    present = chemin.read_bytes()
    if present != attendu:
        index = json.loads(attendu.decode("utf-8"))
        print(
            "ERREUR — l'index de recherche n'est plus le rendu de la collecte : "
            f"{len(index['communes'])} communes attendues, collecte du {index['collecte']}. "
            "Le relancer avec `python3 outils/construire-index-communes.py`.",
            file=sys.stderr,
        )
        return 1
    index = json.loads(present.decode("utf-8"))
    print(
        f"Index de recherche conforme : {len(index['communes'])} communes, "
        f"{len(present) // 1024} Kio, collecte du {index['collecte']}."
    )
    return 0


def principal() -> int:
    analyseur = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    analyseur.add_argument("--sortie", type=Path, default=SORTIE)
    analyseur.add_argument("--donnees", type=Path, default=DONNEES)
    analyseur.add_argument(
        "--minimum",
        type=int,
        default=MINIMUM_COMMUNES,
        help="plancher de communes indexées (le banc s'en sert pour de petits arbres)",
    )
    analyseur.add_argument("--verifier", action="store_true")
    arguments = analyseur.parse_args()
    try:
        if arguments.verifier:
            return verifier(arguments.sortie, arguments.donnees, arguments.minimum)
        return ecrire(arguments.sortie, arguments.donnees, arguments.minimum)
    except Refus as erreur:
        print(f"ÉCHEC — index des communes", file=sys.stderr)
        print(f"    {erreur}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(principal())
