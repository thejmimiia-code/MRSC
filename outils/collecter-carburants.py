#!/usr/bin/env python3
"""Collecte les prix des carburants, département par département.

Pourquoi ces prix-là, et pas « le coût de la vie » : les carburants sont, avec
l'immobilier, l'un des rares postes de dépense d'un foyer dont le prix est
**mesuré, publié, géolocalisé et libre**. La DGCCRF tient un système
d'information des prix pratiqués dans les points de vente, publié sous Licence
Ouverte 2.0 et rafraîchi toutes les dix minutes. Ce que l'outil en tire est une
**médiane départementale** et le nombre de stations qui la fonde — jamais une
moyenne nationale présentée comme un prix local.

Ce que l'outil refuse, et pourquoi :

- un flux absent ou illisible : rien n'est écrit, les données précédentes restent ;
- moins de 3 000 stations ou moins de 50 départements : une réponse tronquée
  donnerait une carte à moitié vide qui aurait l'air complète ;
- une médiane de carburant hors de 0,50 à 3,50 €/L : un fichier mal lu produit
  des prix aberrants, pas des prix ;
- un département sans aucune station : il est absent, pas à zéro ;
- un fichier existant dont la date de collecte est dans le futur.

Ce que l'outil ne dit pas : le prix payé par un foyer donné (il dépend de la
station, du carburant, des promotions et des aides), le coût d'un trajet, ni la
consommation d'un véhicule. Une médiane départementale n'est pas un budget.

Usage :
    python3 outils/collecter-carburants.py
    python3 outils/collecter-carburants.py --base http://127.0.0.1:8000/
    python3 outils/collecter-carburants.py --verifier
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import statistics
import sys
import urllib.error
import urllib.request
from datetime import date, datetime
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
# Les URL tiennent sur une seule ligne, sans concaténation : la sentinelle de
# relecture lit le texte du fichier, et deux fragments collés y apparaissent
# comme deux URL tronquées — une source fantôme qu'elle refuserait de signer.
SOURCE = "https://data.economie.gouv.fr/api/explore/v2.1/catalog/datasets/prix-des-carburants-en-france-flux-instantane-v2/exports/csv"
FICHE = "https://www.data.gouv.fr/datasets/prix-des-carburants-en-france-flux-instantane-v2-amelioree"
LICENCE = "Licence Ouverte 2.0 (lov2)"
PRODUCTEUR = "DGCCRF / Ministères économiques et financiers"
SORTIE = RACINE / "assets" / "data" / "vie-chere" / "carburants.json"
DEPARTEMENTS = [f"{n:02d}" for n in range(1, 20)] + ["2A", "2B"] + [f"{n:02d}" for n in range(21, 96)]
MINIMUM_STATIONS = 3_000
MINIMUM_DEPARTEMENTS = 50
PRIX_PLAUSIBLE = (0.5, 3.5)
CARBURANTS = {
    "gazole_prix": "gazole",
    "sp95_prix": "sp95",
    "sp98_prix": "sp98",
    "e10_prix": "e10",
    "e85_prix": "e85",
    "gplc_prix": "gplc",
}


class Refus(Exception):
    """Une source ne permet pas de publier : rien n'est écrit."""


def lire(url: str, essais: int = 3) -> bytes:
    derniere: Exception | None = None
    for _ in range(essais):
        try:
            with urllib.request.urlopen(url, timeout=120) as reponse:  # noqa: S310
                return reponse.read()
        except (urllib.error.URLError, TimeoutError) as erreur:
            derniere = erreur
    raise Refus(f"source injoignable : {url} ({derniere})")


def nombre(valeur: str) -> float | None:
    texte = (valeur or "").strip().replace(",", ".")
    if not texte:
        return None
    try:
        return float(texte)
    except ValueError:
        return None


def lire_stations(contenu: bytes) -> list[dict[str, str]]:
    try:
        texte = contenu.decode("utf-8-sig")
    except UnicodeDecodeError as erreur:
        raise Refus(f"flux illisible : {erreur}") from erreur
    premiere = texte.splitlines()[0] if texte.strip() else ""
    if "code_departement" not in premiere:
        raise Refus("le flux n'a pas de colonne code_departement : format inattendu, rien n'est publié")
    lignes = list(csv.DictReader(io.StringIO(texte)))
    if len(lignes) < MINIMUM_STATIONS:
        raise Refus(
            f"{len(lignes)} station(s) reçue(s), au moins {MINIMUM_STATIONS} attendues : "
            "une réponse tronquée ne doit pas devenir une carte à moitié vide"
        )
    return lignes


def medianes(lignes: list[dict[str, str]]) -> dict[str, dict[str, dict[str, float]]]:
    valeurs: dict[str, dict[str, list[float]]] = {}
    for ligne in lignes:
        departement = (ligne.get("code_departement") or "").strip()
        if departement not in DEPARTEMENTS:
            continue
        for colonne, nom in CARBURANTS.items():
            prix = nombre(ligne.get(colonne) or "")
            if prix is None:
                continue
            valeurs.setdefault(departement, {}).setdefault(nom, []).append(prix)
    resultat: dict[str, dict[str, dict[str, float]]] = {}
    for departement, par_carburant in valeurs.items():
        for nom, prix in par_carburant.items():
            med = statistics.median(prix)
            if not PRIX_PLAUSIBLE[0] <= med <= PRIX_PLAUSIBLE[1]:
                raise Refus(
                    f"{departement} — {nom} : médiane {med:.3f} €/L hors de "
                    f"{PRIX_PLAUSIBLE[0]} à {PRIX_PLAUSIBLE[1]} €/L, fichier suspect"
                )
            resultat.setdefault(departement, {})[nom] = {
                "mediane": round(med, 3),
                "stations": len(prix),
            }
    if len(resultat) < MINIMUM_DEPARTEMENTS:
        raise Refus(
            f"{len(resultat)} département(s) couvert(s), au moins {MINIMUM_DEPARTEMENTS} attendus"
        )
    return resultat


def collecter(base: str) -> dict:
    contenu = lire(base or SOURCE)
    lignes = lire_stations(contenu)
    donnees = medianes(lignes)
    return {
        "collecte_le": date.today().isoformat(),
        "source": {
            "producteur": PRODUCTEUR,
            "licence": LICENCE,
            "url": SOURCE,
            "fiche": FICHE,
            "sha256": hashlib.sha256(contenu).hexdigest(),
            "stations": len(lignes),
        },
        "unite": "€/L",
        "methode": "médiane des prix affichés par les stations du département, tous horaires confondus",
        "ne_dit_pas": (
            "Ni le prix payé par un foyer (il dépend de la station et des promotions), "
            "ni le coût d'un trajet, ni la consommation d'un véhicule."
        ),
        "departements": {cle: donnees[cle] for cle in sorted(donnees)},
    }


def verifier(chemin: Path) -> int:
    if not chemin.is_file():
        print(f"ERREUR — aucune collecte dans {chemin} : la page doit le dire, pas l'inventer.", file=sys.stderr)
        return 1
    try:
        donnees = json.loads(chemin.read_text(encoding="utf-8"))
    except json.JSONDecodeError as erreur:
        print(f"ERREUR — fichier illisible : {erreur}", file=sys.stderr)
        return 1
    erreurs: list[str] = []
    source = donnees.get("source") or {}
    for cle in ("producteur", "licence", "url", "sha256"):
        if not source.get(cle):
            erreurs.append(f"provenance incomplète : « {cle} » absent")
    if "Ouverte" not in str(source.get("licence", "")):
        erreurs.append(f"licence non ouverte : {source.get('licence')!r}")
    if source.get("stations", 0) < MINIMUM_STATIONS:
        erreurs.append(f"moins de {MINIMUM_STATIONS} stations dans la provenance")
    collecte = str(donnees.get("collecte_le", ""))
    try:
        if datetime.strptime(collecte, "%Y-%m-%d").date() > date.today():
            erreurs.append(f"date de collecte dans le futur : {collecte}")
    except ValueError:
        erreurs.append(f"date de collecte illisible : {collecte!r}")
    departements = donnees.get("departements") or {}
    if len(departements) < MINIMUM_DEPARTEMENTS:
        erreurs.append(f"{len(departements)} département(s) au lieu de {MINIMUM_DEPARTEMENTS}")
    for departement, par_carburant in departements.items():
        if departement not in DEPARTEMENTS:
            erreurs.append(f"département inconnu : {departement}")
        if not par_carburant:
            erreurs.append(f"{departement} : aucun carburant")
        for nom, valeurs in par_carburant.items():
            med = valeurs.get("mediane")
            if not isinstance(med, (int, float)) or not PRIX_PLAUSIBLE[0] <= med <= PRIX_PLAUSIBLE[1]:
                erreurs.append(f"{departement} — {nom} : médiane invraisemblable {med!r}")
            if int(valeurs.get("stations", 0)) < 1:
                erreurs.append(f"{departement} — {nom} : médiane sans station")
    if erreurs:
        print("ÉCHEC — collecte des carburants", file=sys.stderr)
        for erreur in erreurs:
            print(f"    {erreur}", file=sys.stderr)
        return 1
    print(
        f"Carburants conformes : {len(departements)} départements, collecte du {collecte}, "
        f"licence {source.get('licence')}, {source.get('stations')} stations."
    )
    return 0


def principal() -> int:
    analyseur = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    analyseur.add_argument("--sortie", type=Path, default=SORTIE)
    analyseur.add_argument("--base", default="", help="base de test (banc HTTP local)")
    analyseur.add_argument("--verifier", action="store_true")
    arguments = analyseur.parse_args()
    if arguments.verifier:
        return verifier(arguments.sortie)
    try:
        donnees = collecter(arguments.base)
    except Refus as erreur:
        print(f"ERREUR — {erreur}", file=sys.stderr)
        print("Rien n'a été écrit : les données précédentes restent en place.", file=sys.stderr)
        return 1
    arguments.sortie.parent.mkdir(parents=True, exist_ok=True)
    arguments.sortie.write_text(
        json.dumps(donnees, ensure_ascii=False, indent=1, sort_keys=True) + "\n", encoding="utf-8"
    )
    try:
        nom = arguments.sortie.relative_to(RACINE).as_posix()
    except ValueError:
        nom = str(arguments.sortie)  # banc : sortie hors du dépôt
    print(
        f"Collecte écrite : {nom} — "
        f"{len(donnees['departements'])} départements, {donnees['source']['stations']} stations, "
        f"{arguments.sortie.stat().st_size // 1024} Kio."
    )
    return 0


if __name__ == "__main__":
    sys.exit(principal())
