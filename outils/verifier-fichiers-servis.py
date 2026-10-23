#!/usr/bin/env python3
"""Vérifie hors ligne qu'un relevé d'en-têtes reste vrai sur les fichiers du dépôt.

Le relevé réseau (`outils/verifier-publication.py`) interroge le site publié et ne
peut pas tourner hors ligne. Ce script ne fait pas de réseau : il confronte le
**relevé enregistré** (`docs/rd/en-tetes-servis-*.toml`) aux fichiers réellement
présents dans le dépôt, et échoue dès qu'ils ne concordent plus.

Ce que cela prouve, et rien de plus :

- un fichier binaire servi doit faire **exactement** la taille du fichier du
  dépôt — c'est la preuve que la version publiée est celle du dépôt, sans
  recompression ni corruption ;
- un fichier texte servi doit arriver **compressé et plus petit** que sa version
  locale — le nombre exact ne peut pas être vérifié durablement, un contenu
  publié changeant à chaque correction ;
- le relevé doit couvrir exactement les cibles de la sonde réseau : une cible
  ajoutée sans mesure, ou mesurée puis retirée, fait échouer le contrôle ;
- un binaire modifié **après** le relevé peut porter `perime_le = AAAA-MM-JJ`
  (la date de la modification). Le contrôle le déclare alors « relevé périmé »
  au lieu de faire échouer : aucune mesure réseau n'est possible avant que la
  version modifiée soit publiée, et l'inventer serait pire que l'absence. Dès
  que la mesure est refaite, le marqueur doit disparaître, sinon le contrôle
  échoue — il n'existe pas pour laisser un relevé faux dormir.

Ce script ne mesure ni le rendu, ni la performance, ni une empreinte carbone, et
il ne dit rien de la qualité des contenus.

Usage :
    python3 outils/verifier-fichiers-servis.py                     # dernier relevé
    python3 outils/verifier-fichiers-servis.py --releve chemin.toml
"""

from __future__ import annotations

import argparse
import sys
import tomllib
from datetime import date
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
DOSSIER = RACINE / "docs" / "rd"
NATURES = ("texte", "binaire")
CHAMPS = ("chemin", "url", "nature", "type_mime", "encodage", "octets_servis", "cache")


def dernier_releve(dossier: Path = DOSSIER) -> Path:
    releves = sorted(dossier.glob("en-tetes-servis-*.toml"))
    if not releves:
        raise FileNotFoundError("aucun relevé docs/rd/en-tetes-servis-*.toml")
    return releves[-1]


def charger(chemin: Path) -> dict:
    return tomllib.loads(chemin.read_text(encoding="utf-8"))


def cibles_sonde(racine: Path = RACINE) -> set[str]:
    """Chemins contrôlés par la sonde réseau, la racine ramenée à `index.html`."""
    import importlib.util

    spec = importlib.util.spec_from_file_location("verifier_publication", racine / "outils" / "verifier-publication.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return {(chemin or "index.html") for chemin, _, _ in module.CIBLES}


def valider(registre: dict, racine: Path = RACINE, cibles: set[str] | None = None, aujourdhui: date | None = None) -> tuple[list[str], list[str]]:
    """Retourne (erreurs bloquantes, avertissements informatifs)."""
    erreurs: list[str] = []
    avertissements: list[str] = []
    aujourdhui = aujourdhui or date.today()
    meta = registre.get("meta", {})
    if meta.get("version") != 1:
        erreurs.append("meta.version doit valoir 1")
    mesure = meta.get("mesure_le")
    if not isinstance(mesure, date):
        erreurs.append("meta.mesure_le absente ou non lue comme une date")
    elif mesure > aujourdhui:
        erreurs.append(f"meta.mesure_le est dans le futur ({mesure.isoformat()})")
    for champ in ("base_url", "rapport"):
        if not str(meta.get(champ, "")).startswith("https://"):
            erreurs.append(f"meta.{champ} doit être une adresse https")
    outil = str(meta.get("outil", "")).strip()
    if not outil or not (racine / outil).is_file():
        erreurs.append(f"meta.outil doit désigner un outil du dépôt (reçu {outil!r})")

    fichiers = registre.get("fichier") or []
    if not fichiers:
        return erreurs + ["aucun fichier relevé"], avertissements

    vus: set[str] = set()
    for entree in fichiers:
        if not isinstance(entree, dict):
            erreurs.append("une entrée « fichier » n'est pas une table")
            continue
        chemin = str(entree.get("chemin", "")).strip()
        etiquette = chemin or "(sans chemin)"
        absents = [champ for champ in CHAMPS if entree.get(champ) in (None, "")]
        if absents:
            erreurs.append(f"{etiquette} : champs manquants {', '.join(absents)}")
            continue
        if chemin in vus:
            erreurs.append(f"{etiquette} : chemin dupliqué")
        vus.add(chemin)
        nature = entree["nature"]
        if nature not in NATURES:
            erreurs.append(f"{etiquette} : nature inconnue {nature!r}")
            continue
        local = racine / chemin
        if not local.is_file():
            erreurs.append(f"{etiquette} : fichier absent du dépôt")
            continue
        taille = local.stat().st_size
        servi = entree["octets_servis"]
        if not isinstance(servi, int) or isinstance(servi, bool) or servi <= 0:
            erreurs.append(f"{etiquette} : octets_servis n'est pas un entier positif")
            continue
        perime = entree.get("perime_le")
        if perime is not None:
            if nature != "binaire":
                erreurs.append(
                    f"{etiquette} : `perime_le` ne s'applique qu'aux binaires — un texte servi "
                    "n'est pas comparé à l'octet"
                )
            elif not isinstance(perime, date):
                erreurs.append(f"{etiquette} : `perime_le` doit être une date TOML (AAAA-MM-JJ)")
            elif perime <= mesure:
                erreurs.append(
                    f"{etiquette} : `perime_le` ({perime.isoformat()}) n'est pas postérieure à "
                    f"la mesure ({mesure.isoformat()}) — la péremption suit la modification, pas la mesure"
                )
            elif perime > aujourdhui:
                erreurs.append(f"{etiquette} : `perime_le` est dans le futur ({perime.isoformat()})")

        if nature == "binaire":
            if servi != taille:
                if isinstance(perime, date) and mesure < perime <= aujourdhui:
                    # Le fichier a changé depuis le relevé, et la date le dit : le
                    # contrôle ne peut pas prouver ce qu'il ne mesure pas. Il le
                    # déclare au lieu de l'inventer, et exige la mesure après
                    # publication.
                    avertissements.append(
                        f"{etiquette} : relevé périmé depuis le {perime.isoformat()} "
                        f"({taille} octets dans le dépôt, {servi} annoncés servis) — "
                        "mesure réseau à refaire après publication, puis retirer `perime_le`"
                    )
                else:
                    erreurs.append(
                        f"{etiquette} : {taille} octets dans le dépôt mais {servi} annoncés servis — "
                        "le fichier a changé depuis le relevé, refaire la mesure"
                    )
            elif isinstance(perime, date):
                erreurs.append(
                    f"{etiquette} : marqué `perime_le` alors que le fichier concorde de nouveau — "
                    "la mesure a été refaite, retirer le marqueur"
                )
            if str(entree.get("encodage", "")) != "aucun":
                erreurs.append(f"{etiquette} : un binaire servi sans compression doit porter encodage = \"aucun\"")
        else:
            if not str(entree.get("encodage", "")).strip() or str(entree.get("encodage")) == "aucun":
                erreurs.append(f"{etiquette} : un texte servi doit annoncer un encodage de transfert")
            if servi >= taille:
                erreurs.append(
                    f"{etiquette} : servi {servi} octets pour {taille} dans le dépôt — la compression "
                    "annoncée n'est pas plausible, refaire la mesure"
                )
            elif servi > taille * 0.95:
                avertissements.append(f"{etiquette} : compression marginale ({servi}/{taille})")
        if atmoins := entree.get("cache"):
            if "max-age" not in str(atmoins):
                avertissements.append(f"{etiquette} : cache sans max-age ({atmoins})")

    if cibles is not None:
        manquants = sorted(cibles - vus)
        superflus = sorted(vus - cibles)
        if manquants:
            erreurs.append(f"cibles de la sonde sans relevé : {', '.join(manquants)}")
        if superflus:
            erreurs.append(f"relevé de fichiers que la sonde ne contrôle pas : {', '.join(superflus)}")
    poids = sum(entree["octets_servis"] for entree in fichiers if isinstance(entree.get("octets_servis"), int))
    avertissements.append(f"poids théorique du relevé : {poids} octets pour {len(fichiers)} fichiers (sans HTML imbriqué)")
    return erreurs, avertissements


def main() -> int:
    analyseur = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    analyseur.add_argument("--releve", type=Path, help="relevé à vérifier (par défaut le plus récent)")
    analyseur.add_argument("--sans-cibles", action="store_true", help="ne pas confronter la liste des cibles de la sonde")
    arguments = analyseur.parse_args()

    try:
        chemin = arguments.releve or dernier_releve()
        registre = charger(chemin)
    except (OSError, tomllib.TOMLDecodeError) as erreur:
        print(f"Relevé illisible : {erreur}", file=sys.stderr)
        return 2

    cibles = None if arguments.sans_cibles else cibles_sonde()
    erreurs, avertissements = valider(registre, RACINE, cibles)
    nom = chemin.relative_to(RACINE) if chemin.is_relative_to(RACINE) else chemin
    if erreurs:
        print(f"Relevé {nom} non concordant :", file=sys.stderr)
        for erreur in erreurs:
            print(f"  - {erreur}", file=sys.stderr)
        return 1
    fichiers = registre.get("fichier") or []
    perimes = [entree for entree in fichiers if entree.get("perime_le")]
    binaires = sum(1 for entree in fichiers if entree.get("nature") == "binaire") - len(perimes)
    textes = len(fichiers) - binaires - len(perimes)
    constat = (
        f"Relevé {nom} concordant : {len(fichiers)} fichiers, dont {binaires} binaires servis octet pour octet "
        f"et {textes} textes compressés — mesure du {registre['meta']['mesure_le'].isoformat()}."
    )
    if perimes:
        constat += (
            f" {len(perimes)} binaires modifiés depuis (qualité d'encodage relevée le 23 octobre 2026) "
            "attendent une mesure réseau après publication."
        )
    print(constat)
    for avertissement in avertissements:
        print(f"  · {avertissement}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
