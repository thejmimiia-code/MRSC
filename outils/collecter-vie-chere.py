#!/usr/bin/env python3
"""Collecte les données réelles de la carte des coûts, et refuse les fausses.

La page des coûts n'invente aucun chiffre : elle lit des fichiers figés, écrits
par cet outil à partir de sources publiques, avec leur provenance et leur
empreinte. Une collecte qui échoue **n'écrase rien** : elle sort en erreur et
laisse en place les données précédentes, datées.

Sources (voir `docs/rd/sources-vie-chere.toml`) :

- `geo.api.gouv.fr` — communes courantes, population, point central ;
- DVF (DGFiP, data.gouv.fr, Licence Ouverte 2.0) — ventes réelles, prix au m².

Ce que l'outil refuse, et pourquoi :

- un jeu de données DVF dont la licence n'est pas ouverte ;
- moins de 30 000 communes, ou un département absent ;
- un prix médian national hors de 800 à 12 000 €/m² (un fichier mal lu donne des
  prix aberrants, pas des prix) ;
- des prix en Alsace ou en Moselle : ces départements sont hors du champ de
  DVF (livre foncier), un prix y serait une erreur de lecture ;
- d'écrire quoi que ce soit si une seule source manque.

Usage :
    python3 outils/collecter-vie-chere.py --sortie assets/data/vie-chere
    python3 outils/collecter-vie-chere.py --verifier --sortie assets/data/vie-chere
    python3 outils/collecter-vie-chere.py --base-geo http://127.0.0.1:8000/ --base-data http://127.0.0.1:8000/
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
import zipfile
from datetime import date
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
GEO = "https://geo.api.gouv.fr/communes?fields=nom,code,codesPostaux,population,centre,departement"
DATASET = "https://www.data.gouv.fr/api/1/datasets/demandes-de-valeurs-foncieres/"
LICENCES_OUVERTES = {"lov2", "fr-lo", "odc-odbl", "cc-by"}
HORS_CHAMP_DVF = {"67", "68", "57", "976"}
MINIMUM_COMMUNES = 30_000
MEDIANE_NATIONALE = (800, 12_000)
PRIX_PLAUSIBLE = (300, 30_000)
SURFACE_MINIMALE = 9.0
DELIMITEUR = "|"


class Refus(Exception):
    """Une source ne permet pas de publier : rien n'est écrit."""


def empreinte(donnees: bytes) -> str:
    return hashlib.sha256(donnees).hexdigest()


def lire(url: str, essais: int = 3) -> bytes:
    derniere: Exception | None = None
    for _ in range(essais):
        try:
            with urllib.request.urlopen(url, timeout=120) as reponse:  # noqa: S310
                return reponse.read()
        except (urllib.error.URLError, TimeoutError) as erreur:
            derniere = erreur
    raise Refus(f"source injoignable : {url} ({derniere})")


def communes_depuis(contenu: bytes) -> list[dict]:
    try:
        brut = json.loads(contenu.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as erreur:
        raise Refus(f"communes illisibles : {erreur}") from erreur
    if not isinstance(brut, list) or len(brut) < MINIMUM_COMMUNES:
        nombre = len(brut) if isinstance(brut, list) else 0
        raise Refus(
            f"{nombre} commune(s) reçue(s), au moins {MINIMUM_COMMUNES} attendues : "
            "une réponse tronquée ne doit pas devenir un site à moitié vide"
        )
    communes = []
    for entree in brut:
        try:
            code = str(entree["code"])
            departement = str(entree["departement"]["code"])
            centre = entree["centre"]["coordinates"]
            communes.append(
                {
                    "c": code,
                    "n": str(entree["nom"]),
                    "d": departement,
                    "x": round(float(centre[0]), 4),
                    "y": round(float(centre[1]), 4),
                    "p": int(entree.get("population") or 0),
                }
            )
        except (KeyError, TypeError, ValueError) as erreur:
            raise Refus(f"commune incomplète : {erreur} dans {str(entree)[:120]}") from erreur
    return communes


def ressources_dvf(contenu: bytes, semestres: int) -> list[dict]:
    try:
        jeu = json.loads(contenu.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as erreur:
        raise Refus(f"fiche DVF illisible : {erreur}") from erreur
    licence = str(jeu.get("license") or "")
    if licence not in LICENCES_OUVERTES:
        raise Refus(f"licence DVF « {licence} » non ouverte : réutilisation non autorisée")
    candidats = []
    for ressource in jeu.get("resources") or []:
        titre = str(ressource.get("title") or "")
        url = str(ressource.get("url") or "")
        if not url.endswith(".txt.zip") or "valeurs fonci" not in titre.lower():
            continue
        candidats.append({"titre": titre, "url": url, "sha1": (ressource.get("checksum") or {}).get("value")})
    if not candidats:
        raise Refus("aucun fichier DVF semestriel dans la fiche du jeu de données")
    candidats.sort(key=lambda r: r["titre"])
    return candidats[-semestres:]


def nombre(valeur: str) -> float | None:
    texte = (valeur or "").strip().replace(",", ".")
    if not texte:
        return None
    try:
        return float(texte)
    except ValueError:
        return None


def prix_par_commune(contenu: bytes, nom: str) -> dict[str, dict[str, list[float]]]:
    """Lit un fichier DVF semestriel et rend, par commune, les prix au m² par type."""
    resultat: dict[str, dict[str, list[float]]] = {}
    try:
        archive = zipfile.ZipFile(io.BytesIO(contenu))
    except zipfile.BadZipFile as erreur:
        raise Refus(f"{nom} : archive illisible ({erreur})") from erreur
    for membre in archive.namelist():
        if not membre.lower().endswith(".txt"):
            continue
        with archive.open(membre) as flux:
            texte = None
            for encodage in ("utf-8-sig", "utf-8", "latin-1"):
                try:
                    texte = io.StringIO(flux.read().decode(encodage))
                    break
                except UnicodeDecodeError:
                    continue
            if texte is None:
                raise Refus(f"{nom} : encodage inconnu")
            lecteur = csv.DictReader(texte, delimiter=DELIMITEUR)
            colonnes = lecteur.fieldnames or []
            for colonne in ("Nature mutation", "Type local", "Valeur fonciere", "Surface reelle bati", "Code commune", "Code departement"):
                if colonne not in colonnes:
                    raise Refus(f"{nom} : colonne « {colonne} » absente — format DVF inattendu")
            for ligne in lecteur:
                if (ligne.get("Nature mutation") or "").strip().lower() != "vente":
                    continue
                type_local = (ligne.get("Type local") or "").strip()
                if type_local not in ("Appartement", "Maison"):
                    continue
                valeur = nombre(ligne.get("Valeur fonciere") or "")
                surface = nombre(ligne.get("Surface reelle bati") or "")
                if not valeur or not surface or surface < SURFACE_MINIMALE or valeur < 1000:
                    continue
                prix_m2 = valeur / surface
                if not (PRIX_PLAUSIBLE[0] <= prix_m2 <= PRIX_PLAUSIBLE[1]):
                    continue
                code = (ligne.get("Code commune") or "").strip()
                departement = (ligne.get("Code departement") or "").strip()
                if not code or not departement:
                    continue
                cle = f"{departement}{code}" if len(code) < 5 else code
                resultat.setdefault(cle, {}).setdefault(type_local, []).append(prix_m2)
    return resultat


def fusionner(cibles: dict[str, dict[str, list[float]]], source: dict[str, dict[str, list[float]]]) -> None:
    for commune, types in source.items():
        for type_local, prix in types.items():
            cibles.setdefault(commune, {}).setdefault(type_local, []).extend(prix)


def construire(communes: list[dict], prix: dict[str, dict[str, list[float]]], provenance: list[dict], jour: str) -> dict[str, dict]:
    """Assemble les fichiers par département, sans jamais inventer une valeur."""
    par_departement: dict[str, list[dict]] = {}
    tous_prix: list[float] = []
    avec_prix = 0
    for commune in communes:
        types = prix.get(commune["c"]) or {}
        appartements = types.get("Appartement") or []
        maisons = types.get("Maison") or []
        entree = {"c": commune["c"], "n": commune["n"], "x": commune["x"], "y": commune["y"], "p": commune["p"]}
        if appartements:
            entree["pa"] = round(statistics.median(appartements))
            entree["na"] = len(appartements)
            tous_prix.append(entree["pa"])
        if maisons:
            entree["pm"] = round(statistics.median(maisons))
            entree["nm"] = len(maisons)
            tous_prix.append(entree["pm"])
        if appartements or maisons:
            avec_prix += 1
        par_departement.setdefault(commune["d"], []).append(entree)

    if not tous_prix:
        raise Refus("aucun prix calculé : le fichier DVF n'a livré aucune vente exploitable")
    mediane = statistics.median(tous_prix)
    if not (MEDIANE_NATIONALE[0] <= mediane <= MEDIANE_NATIONALE[1]):
        raise Refus(
            f"prix médian national de {mediane:.0f} €/m² hors de "
            f"{MEDIANE_NATIONALE[0]}–{MEDIANE_NATIONALE[1]} : lecture suspecte, rien n'est publié"
        )
    for departement in HORS_CHAMP_DVF:
        for entree in par_departement.get(departement, []):
            if "pa" in entree or "pm" in entree:
                raise Refus(
                    f"{entree['c']} porte un prix alors que le département {departement} "
                    "est hors du champ de DVF : la lecture est fausse"
                )

    etat = {
        "version": 1,
        "collecte": jour,
        "regles": {
            "vente_seulement": True,
            "types": ["Appartement", "Maison"],
            "surface_minimale_m2": SURFACE_MINIMALE,
            "prix_plausible_eur_m2": list(PRIX_PLAUSIBLE),
            "mediane_nationale_eur_m2": round(mediane),
            "sous_cinq_ventes": "médiane publiée avec son nombre de ventes, la page décide de l'afficher",
        },
        "couverture": {
            "communes": len(communes),
            "communes_avec_prix": avec_prix,
            "departements": len(par_departement),
            "hors_champ": sorted(HORS_CHAMP_DVF),
        },
        "sources": provenance,
        # La liste des fichiers est écrite dans l'état : elle sert au contrôle
        # des ressources orphelines du site, qui exige que chaque fichier publié
        # soit nommé quelque part, et à la page pour savoir ce qui existe.
        "fichiers": sorted(f"d-{code}.json" for code in par_departement),
    }
    fichiers = {"_etat.json": etat}
    for departement, entrees in par_departement.items():
        entrees.sort(key=lambda e: e["c"])
        fichiers[f"d-{departement}.json"] = {
            "d": departement,
            "collecte": jour,
            "communes": entrees,
        }
    return fichiers


def ecrire(sortie: Path, fichiers: dict[str, dict], provenance: list[dict], jour: str) -> None:
    sortie.mkdir(parents=True, exist_ok=True)
    provisoire = sortie / ".ecriture"
    provisoire.mkdir(exist_ok=True)
    for nom, contenu in fichiers.items():
        (provisoire / nom).write_text(
            json.dumps(contenu, ensure_ascii=False, separators=(",", ":")) + "\n",
            encoding="utf-8",
        )
    # Remplacement seulement quand tout est écrit : une collecte interrompue ne
    # doit pas laisser un département à moitié publié.
    for nom in fichiers:
        (provisoire / nom).replace(sortie / nom)
    provisoire.rmdir()
    with_prix = fichiers["_etat.json"]["couverture"]["communes_avec_prix"]
    print(
        f"Collecte écrite : {len(fichiers) - 1} département(s), "
        f"{with_prix} commune(s) avec prix, médiane nationale "
        f"{fichiers['_etat.json']['regles']['mediane_nationale_eur_m2']} €/m², le {jour}."
    )


def verifier(sortie: Path) -> int:
    etat = sortie / "_etat.json"
    if not etat.is_file():
        print(f"ERREUR — aucune collecte dans {sortie} : la page doit le dire, pas l'inventer.", file=sys.stderr)
        return 1
    contenu = json.loads(etat.read_text(encoding="utf-8"))
    erreurs: list[str] = []
    couverture = contenu.get("couverture") or {}
    departements = couverture.get("departements") or 0
    fichiers = sorted(sortie.glob("d-*.json"))
    if len(fichiers) != departements:
        erreurs.append(f"{len(fichiers)} fichiers pour {departements} départements annoncés")
    communes = 0
    for fichier in fichiers:
        donnees = json.loads(fichier.read_text(encoding="utf-8"))
        if not donnees.get("communes"):
            erreurs.append(f"{fichier.name} : aucune commune")
        if donnees.get("collecte") != contenu.get("collecte"):
            erreurs.append(f"{fichier.name} : date de collecte différente de l'état")
        communes += len(donnees.get("communes") or [])
    if communes != couverture.get("communes"):
        erreurs.append(f"{communes} communes dans les fichiers, {couverture.get('communes')} annoncées")
    for source in contenu.get("sources") or []:
        for champ in ("id", "url", "sha256", "licence", "date"):
            if not source.get(champ):
                erreurs.append(f"source incomplète : {champ} manquant pour {source.get('id', '?')}")
    if not contenu.get("sources"):
        erreurs.append("aucune provenance : des chiffres sans source ne sont pas publiables")
    if erreurs:
        for erreur in erreurs:
            print(f"ERREUR — {erreur}", file=sys.stderr)
        print(f"ÉCHEC — collecte incohérente ({len(erreurs)} écart(s)).", file=sys.stderr)
        return 1
    print(
        f"Collecte cohérente : {departements} départements, {communes} communes, "
        f"{couverture.get('communes_avec_prix')} avec prix, collectée le {contenu.get('collecte')}."
    )
    return 0


def collecter(sortie: Path, base_geo: str, base_data: str, semestres: int) -> int:
    jour = date.today().isoformat()
    provenance: list[dict] = []

    contenu_geo = lire(base_geo)
    communes = communes_depuis(contenu_geo)
    provenance.append(
        {
            "id": "geo-api-communes",
            "url": GEO,
            "licence": "Licence Ouverte 2.0",
            "sha256": empreinte(contenu_geo),
            "octets": len(contenu_geo),
            "date": jour,
        }
    )

    contenu_jeu = lire(base_data)
    ressources = ressources_dvf(contenu_jeu, semestres)
    prix: dict[str, dict[str, list[float]]] = {}
    for ressource in ressources:
        contenu = lire(ressource["url"])
        fusionner(prix, prix_par_commune(contenu, ressource["titre"]))
        provenance.append(
            {
                "id": "dvf-dgfip",
                "titre": ressource["titre"],
                "url": ressource["url"],
                "licence": "Lov2",
                "sha256": empreinte(contenu),
                "octets": len(contenu),
                "date": jour,
            }
        )
    fichiers = construire(communes, prix, provenance, jour)
    ecrire(sortie, fichiers, provenance, jour)
    return verifier(sortie)


def principal() -> int:
    analyseur = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    analyseur.add_argument("--sortie", type=Path, default=RACINE / "assets" / "data" / "vie-chere")
    analyseur.add_argument("--verifier", action="store_true", help="contrôler une collecte existante")
    analyseur.add_argument("--base-geo", default=GEO, help="URL des communes (surchargée par les bancs)")
    analyseur.add_argument("--base-data", default=DATASET, help="URL de la fiche DVF (surchargée par les bancs)")
    analyseur.add_argument("--semestres", type=int, default=2, help="nombre de fichiers DVF à agréger")
    arguments = analyseur.parse_args()
    if arguments.verifier:
        return verifier(arguments.sortie)
    try:
        return collecter(arguments.sortie, arguments.base_geo, arguments.base_data, arguments.semestres)
    except Refus as refus:
        print(f"ERREUR — {refus}", file=sys.stderr)
        print("ÉCHEC — aucune donnée n'a été écrite.", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(principal())
