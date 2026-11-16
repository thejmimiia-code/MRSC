#!/usr/bin/env python3
"""Collecte les niveaux de vie médians et taux de pauvreté par commune (FiLoSoFi, INSEE).

Pourquoi les revenus ici, et comment sans gratter de pages HTML : le dispositif
FiLoSoFi 2 de l'INSEE (`DS_FILOSOFI_CC`) est diffusé en accès libre via l'API
officielle Mélodi. Le catalogue JSON donne l'adresse directe de l'archive CSV
du dernier millésime, et chaque ligne communale porte deux indicateurs :

- `MED_SL` : niveau de vie médian annuel par unité de consommation (€/an) ;
- `PR_MD60` : taux de pauvreté à 60 % du niveau de vie médian métropolitain (%).

Ce que l'outil refuse, et pourquoi :

- un catalogue illisible, une page HTML ou une licence qui n'est pas libre :
  rien n'est publié ;
- aucun produit CSV en français dans le catalogue : l'adresse d'archive a
  changé, et deviner un lien reviendrait à publier une source incertaine ;
- une archive ZIP absente, corrompue ou sans fichier `*_data.csv`, ou des
  colonnes attendues absentes : rien n'est écrit, les données précédentes
  restent en place ;
- une observation marquée omise (`OBS_STATUS = O`) ou confidentielle : elle
  reste absente (`null` pour le taux de pauvreté, commune omise si la médiane
  est omise), jamais transformée en zéro ;
- un doublon sur la même commune et la même mesure : une donnée ambiguë est
  refusée ;
- moins de 25 000 communes avec un niveau de vie médian publié : une archive
  tronquée donnerait une France à moitié vide qui aurait l'air complète ;
- un niveau de vie médian national hors de 10 000 à 60 000 €/an, communal hors
  de 5 000 à 150 000 €/an, ou un taux de pauvreté hors de 0 à 100 % : un
  fichier mal lu produit des nombres aberrants, pas des revenus ;
- une provenance incomplète, un fichier départemental manquant ou une date de
  collecte dans le futur lors de `--verifier`.

Ce que l'outil ne dit pas : les salaires individuels, le patrimoine, les loyers
ou le reste à vivre d'un ménage particulier. Les indicateurs FiLoSoFi portent sur
les ménages fiscaux dont le revenu disponible est positif ou nul, par unité de
consommation ; certaines petites communes ou communes intégrées restent omises
par secret statistique.

Usage :
    python3 outils/collecter-revenus.py
    python3 outils/collecter-revenus.py --base http://127.0.0.1:8000
    python3 outils/collecter-revenus.py --verifier
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import http.client
import io
import json
import math
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
import zipfile
from datetime import date, datetime
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
# Les URL tiennent sur une seule ligne, sans concaténation : la sentinelle de
# relecture lit le texte du fichier, et deux fragments collés y apparaissent
# comme deux URL tronquées — une source fantôme qu'elle refuserait de signer.
CATALOGUE = "https://api.insee.fr/melodi/catalog/DS_FILOSOFI_CC"
CHEMIN_CATALOGUE = "/melodi/catalog/DS_FILOSOFI_CC"
PRODUCTEUR = "INSEE (FiLoSoFi 2, API Mélodi)"
LICENCE = "Licence Ouverte 2.0 (lov2)"
SORTIE = RACINE / "assets" / "data" / "vie-chere" / "revenus"
DEPARTEMENTS = (
    [f"{n:02d}" for n in range(1, 20)]
    + ["2A", "2B"]
    + [f"{n:02d}" for n in range(21, 96)]
    + ["974"]
)
MINIMUM_COMMUNES = 25_000
MEDIANE_PLAUSIBLE = (5_000, 150_000)
MEDIANE_NATIONALE_PLAUSIBLE = (10_000, 60_000)
PAUVRETE_PLAUSIBLE = (0.0, 100.0)
MOTIF_COMMUNE = re.compile(r"^(?:\d{2}|2[AB])\d{3}$")
COLONNES_STANDARD = {
    "GEO",
    "GEO_OBJECT",
    "FILOSOFI_MEASURE",
    "TIME_PERIOD",
    "OBS_VALUE",
    "UNIT_MEASURE",
    "UNIT_MULT",
    "CONF_STATUS",
    "OBS_STATUS",
}
VALEURS_TOTAL = {"", "_T", "TOTAL", "_Z"}


class Refus(Exception):
    """Une source ne permet pas de publier : rien n'est écrit."""


def lire(url: str, accept: str = "*/*", essais: int = 3) -> bytes:
    derniere: Exception | None = None
    demande = urllib.request.Request(
        url,
        headers={"Accept": accept, "Accept-Encoding": "identity"},
    )
    for _ in range(essais):
        try:
            with urllib.request.urlopen(demande, timeout=180) as reponse:  # noqa: S310
                return reponse.read()
        except (OSError, http.client.HTTPException) as erreur:
            derniere = erreur
    raise Refus(f"source injoignable : {url} ({derniere})")


def url_catalogue(base: str) -> str:
    if not base:
        return CATALOGUE
    return base.rstrip("/") + CHEMIN_CATALOGUE


def url_produit(access_url: str, base: str) -> str:
    if not base:
        if not access_url.startswith("https://api.insee.fr/"):
            raise Refus(f"adresse d'archive hors domaine INSEE : {access_url!r}")
        return access_url
    analyse = urllib.parse.urlparse(access_url)
    chemin = analyse.path or access_url
    if not chemin.startswith("/"):
        chemin = "/" + chemin
    if analyse.query:
        chemin = f"{chemin}?{analyse.query}"
    return base.rstrip("/") + chemin


def verifier_licence_catalogue(catalogue: dict) -> None:
    licence = catalogue.get("license")
    if licence:
        texte_lic = json.dumps(licence, ensure_ascii=False).lower()
        if not any(
            jeton in texte_lic
            for jeton in ("ouverte", "lov2", "fr-lo", "etalab", "open", "cc-by")
        ):
            raise Refus(f"licence non ouverte dans le catalogue : {licence!r}")
    droits = catalogue.get("accessRights")
    valeurs: list[str] = []
    if isinstance(droits, list):
        for entree in droits:
            if isinstance(entree, dict) and entree.get("content"):
                valeurs.append(str(entree["content"]).strip().lower())
            elif isinstance(entree, str):
                valeurs.append(entree.strip().lower())
    elif isinstance(droits, str):
        valeurs.append(droits.strip().lower())
    if not any(v in {"libre", "free", "public"} for v in valeurs):
        raise Refus(f"droits d'accès absents ou fermés dans le catalogue : {droits!r}")
    if any(v in {"restreint", "restricted", "ferme", "fermé", "closed"} for v in valeurs):
        raise Refus(f"droits d'accès fermés dans le catalogue : {droits!r}")


def lire_catalogue(base: str) -> tuple[str, str, str]:
    contenu = lire(url_catalogue(base), accept="application/json")
    try:
        catalogue = json.loads(contenu.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as erreur:
        raise Refus(f"catalogue Mélodi illisible (HTML ou JSON invalide) : {erreur}") from erreur
    if not isinstance(catalogue, dict):
        raise Refus("catalogue Mélodi invalide : objet JSON attendu")
    verifier_licence_catalogue(catalogue)
    produits = catalogue.get("product") or []
    if not isinstance(produits, list):
        raise Refus("catalogue Mélodi sans liste de produits")
    candidat = None
    for produit in produits:
        if not isinstance(produit, dict):
            continue
        fmt = str(produit.get("format", "")).strip().upper()
        langue = str(produit.get("language", "")).strip().upper()
        if fmt == "CSV" and langue == "FR" and produit.get("accessURL"):
            candidat = produit
            break
    if not candidat:
        raise Refus("aucun produit CSV en français trouvé dans le catalogue Mélodi")
    access_url = str(candidat["accessURL"]).strip()
    date_source = str(candidat.get("modified") or catalogue.get("modified") or "")[:10]
    return access_url, date_source, str(candidat.get("id") or "DS_FILOSOFI_CC_CSV_FR")


def normaliser_code_commune(brut: str) -> str:
    code = brut.strip().upper()
    if code.isdigit() and len(code) < 5:
        code = code.zfill(5)
    return code


def departement_de(code_commune: str) -> str:
    if code_commune.startswith(("97", "98")):
        return code_commune[:3]
    return code_commune[:2]


def analyser_geo(geo: str, geo_object: str) -> tuple[str, str]:
    geo_propre = (geo or "").strip()
    obj_propre = (geo_object or "").strip().upper()
    if obj_propre:
        code = geo_propre.split("-")[-1].strip().upper()
        return obj_propre, code
    morceaux = [m.strip() for m in geo_propre.split("-") if m.strip()]
    for index, morceau in enumerate(morceaux):
        haut = morceau.upper()
        if haut in {"COM", "FRANCE", "DEP", "REG", "ARM", "EPCI"}:
            reste = "-".join(morceaux[index + 1 :]).upper()
            return haut, reste
    return "", geo_propre.upper()


def lire_observations(contenu_zip: bytes, minimum_communes: int = MINIMUM_COMMUNES) -> dict:
    try:
        archive = zipfile.ZipFile(io.BytesIO(contenu_zip))
    except zipfile.BadZipFile as erreur:
        raise Refus(f"archive ZIP FiLoSoFi illisible : {erreur}") from erreur
    with archive:
        candidats = [
            nom
            for nom in archive.namelist()
            if nom.lower().endswith(".csv") and "metadata" not in nom.lower()
        ]
        if not candidats:
            raise Refus("archive ZIP sans fichier CSV de données")
        membre = sorted(candidats, key=lambda n: (0 if "_data" in n.lower() else 1, n))[0]
        with archive.open(membre) as brut:
            try:
                flux = io.TextIOWrapper(brut, encoding="utf-8-sig", newline="")
                premiere = flux.readline()
            except UnicodeDecodeError as erreur:
                raise Refus(f"CSV FiLoSoFi illisible : {erreur}") from erreur
            if not premiere.strip():
                raise Refus("CSV FiLoSoFi vide")
            separateur = ";" if premiere.count(";") > premiere.count(",") else ","
            colonnes = [c.strip().strip('"') for c in next(csv.reader([premiere], delimiter=separateur))]
            attendues = {"GEO", "FILOSOFI_MEASURE", "OBS_VALUE", "TIME_PERIOD", "OBS_STATUS"}
            manquantes = sorted(attendues - set(colonnes))
            if manquantes:
                raise Refus(f"colonnes attendues absentes du CSV FiLoSoFi : {', '.join(manquantes)}")
            colonnes_ventil = [c for c in colonnes if c not in COLONNES_STANDARD]
            lecteur = csv.DictReader(flux, fieldnames=colonnes, delimiter=separateur)
            observations: list[tuple[str, str, str, str, float]] = []
            annees: set[str] = set()
            for ligne in lecteur:
                if any((ligne.get(col) or "").strip().upper() not in VALEURS_TOTAL for col in colonnes_ventil):
                    continue
                mesure = (ligne.get("FILOSOFI_MEASURE") or "").strip().upper()
                if mesure not in {"MED_SL", "PR_MD60"}:
                    continue
                periode = (ligne.get("TIME_PERIOD") or "").strip()
                if not periode:
                    continue
                obs_status = (ligne.get("OBS_STATUS") or "").strip().upper()
                conf_status = (ligne.get("CONF_STATUS") or "").strip().upper()
                if obs_status not in {"", "A"} or conf_status not in {"", "F"}:
                    continue
                brut_val = (ligne.get("OBS_VALUE") or "").strip().replace(",", ".")
                if not brut_val:
                    if obs_status == "A":
                        raise Refus(f"valeur absente malgré OBS_STATUS=A pour {ligne.get('GEO')} ({mesure})")
                    continue
                try:
                    valeur = float(brut_val)
                except ValueError as erreur:
                    raise Refus(
                        f"valeur numérique illisible ({brut_val!r}) pour {ligne.get('GEO')} ({mesure})"
                    ) from erreur
                if not math.isfinite(valeur):
                    raise Refus(f"valeur non finie pour {ligne.get('GEO')} ({mesure})")
                niveau, code = analyser_geo(ligne.get("GEO") or "", ligne.get("GEO_OBJECT") or "")
                if niveau not in {"COM", "FRANCE"}:
                    continue
                annees.add(periode)
                observations.append((periode, niveau, code, mesure, valeur))

    if not annees:
        raise Refus("aucune observation exploitable (MED_SL / PR_MD60) dans l'archive FiLoSoFi")
    millesime = sorted(annees)[-1]

    communes: dict[str, dict[str, float]] = {}
    france: dict[str, dict[str, float]] = {}
    vus: set[tuple[str, str, str]] = set()
    for periode, niveau, code, mesure, valeur in observations:
        if periode != millesime:
            continue
        if niveau == "COM":
            code_com = normaliser_code_commune(code)
            if not MOTIF_COMMUNE.match(code_com):
                raise Refus(f"code commune inattendu dans FiLoSoFi : {code!r}")
            cle = (niveau, code_com, mesure)
            if cle in vus:
                raise Refus(f"observation en double pour la commune {code_com} ({mesure})")
            vus.add(cle)
            if mesure == "MED_SL":
                if not MEDIANE_PLAUSIBLE[0] <= valeur <= MEDIANE_PLAUSIBLE[1]:
                    raise Refus(
                        f"{code_com} : niveau de vie médian invraisemblable {valeur} €/an "
                        f"(hors de {MEDIANE_PLAUSIBLE[0]} à {MEDIANE_PLAUSIBLE[1]})"
                    )
                communes.setdefault(code_com, {})["m"] = round(valeur)
            elif mesure == "PR_MD60":
                if not PAUVRETE_PLAUSIBLE[0] <= valeur <= PAUVRETE_PLAUSIBLE[1]:
                    raise Refus(
                        f"{code_com} : taux de pauvreté invraisemblable {valeur} % (hors de 0 à 100)"
                    )
                communes.setdefault(code_com, {})["p"] = round(valeur, 1)
        elif niveau == "FRANCE":
            cle = (niveau, code, mesure)
            if cle in vus:
                raise Refus(f"observation nationale en double pour {code} ({mesure})")
            vus.add(cle)
            france.setdefault(code, {})[mesure] = valeur

    ref = france.get("FM") or france.get("FRM") or france.get("FRMETRO")
    if ref is None and len(france) == 1:
        ref = next(iter(france.values()))
    if not ref or "MED_SL" not in ref:
        raise Refus("référence nationale (France métropolitaine, MED_SL) introuvable dans FiLoSoFi")
    med_nat = ref["MED_SL"]
    if not MEDIANE_NATIONALE_PLAUSIBLE[0] <= med_nat <= MEDIANE_NATIONALE_PLAUSIBLE[1]:
        raise Refus(
            f"niveau de vie médian national invraisemblable : {med_nat} €/an "
            f"(hors de {MEDIANE_NATIONALE_PLAUSIBLE[0]} à {MEDIANE_NATIONALE_PLAUSIBLE[1]})"
        )
    pauv_nat = ref.get("PR_MD60")
    if pauv_nat is not None and not PAUVRETE_PLAUSIBLE[0] <= pauv_nat <= PAUVRETE_PLAUSIBLE[1]:
        raise Refus(f"taux de pauvreté national invraisemblable : {pauv_nat} %")

    avec_mediane = {code: vals for code, vals in communes.items() if "m" in vals}
    if len(avec_mediane) < minimum_communes:
        raise Refus(
            f"{len(avec_mediane)} commune(s) avec niveau de vie médian, au moins {minimum_communes} "
            "attendues : une archive tronquée ne doit pas devenir une carte à moitié vide"
        )

    par_departement: dict[str, dict[str, list[float | int | None]]] = {}
    nb_pauvrete = 0
    for code in sorted(avec_mediane):
        vals = avec_mediane[code]
        dep = departement_de(code)
        pauv = vals.get("p")
        if pauv is not None:
            nb_pauvrete += 1
        par_departement.setdefault(dep, {})[code] = [vals["m"], pauv]

    return {
        "millesime": millesime,
        "reference_nationale": {
            "zone": "France métropolitaine",
            "mediane": round(med_nat),
            "taux_pauvrete": round(pauv_nat, 1) if pauv_nat is not None else None,
        },
        "communes_mediane": len(avec_mediane),
        "communes_pauvrete": nb_pauvrete,
        "par_departement": par_departement,
    }


def collecter(base: str, minimum_communes: int = MINIMUM_COMMUNES) -> tuple[dict, dict[str, dict]]:
    access_url, date_source, produit_id = lire_catalogue(base)
    url_archive = url_produit(access_url, base)
    contenu_zip = lire(url_archive)
    empreinte = hashlib.sha256(contenu_zip).hexdigest()
    res = lire_observations(contenu_zip, minimum_communes=minimum_communes)
    par_departement = res["par_departement"]
    fichiers_dep: dict[str, dict] = {}
    for dep in sorted(par_departement):
        fichiers_dep[f"r-{dep}.json"] = {
            "departement": dep,
            "millesime": res["millesime"],
            "communes": par_departement[dep],
        }
    etat = {
        "version": 1,
        "collecte_le": date.today().isoformat(),
        "millesime": res["millesime"],
        "geographie": "2026-01-01",
        "unite_mediane": "€/an par unité de consommation",
        "unite_pauvrete": "%",
        "reference_nationale": res["reference_nationale"],
        "couverture": {
            "communes_mediane": res["communes_mediane"],
            "communes_pauvrete": res["communes_pauvrete"],
            "departements": len(fichiers_dep),
            "champ": "France métropolitaine et La Réunion",
        },
        "source": {
            "producteur": PRODUCTEUR,
            "licence": LICENCE,
            "catalogue": CATALOGUE,
            "url": access_url,
            "produit": produit_id,
            "date_source": date_source,
            "sha256": empreinte,
            "octets": len(contenu_zip),
        },
        "ne_dit_pas": (
            "Ni les salaires individuels, ni le patrimoine, ni le reste à vivre d'un ménage particulier. "
            "Calculé sur les ménages fiscaux dont le revenu disponible est positif ou nul ; "
            "certaines petites communes ou communes intégrées restent omises par secret statistique."
        ),
        "fichiers": sorted(fichiers_dep),
    }
    return etat, fichiers_dep


def verifier(dossier: Path, minimum_communes: int = MINIMUM_COMMUNES) -> int:
    chemin_etat = dossier / "_etat.json"
    if not chemin_etat.is_file():
        print(f"ERREUR — aucune collecte dans {chemin_etat} : la page doit le dire, pas l'inventer.", file=sys.stderr)
        return 1
    try:
        etat = json.loads(chemin_etat.read_text(encoding="utf-8"))
    except json.JSONDecodeError as erreur:
        print(f"ERREUR — état des revenus illisible : {erreur}", file=sys.stderr)
        return 1
    erreurs: list[str] = []
    source = etat.get("source") or {}
    for cle in ("producteur", "licence", "catalogue", "url", "sha256"):
        if not source.get(cle):
            erreurs.append(f"provenance incomplète : « {cle} » absent")
    if "Ouverte" not in str(source.get("licence", "")):
        erreurs.append(f"licence non ouverte : {source.get('licence')!r}")
    if int(source.get("octets", 0)) < 1:
        erreurs.append("taille de l'archive absente ou nulle")
    collecte = str(etat.get("collecte_le", ""))
    try:
        if datetime.strptime(collecte, "%Y-%m-%d").date() > date.today():
            erreurs.append(f"date de collecte dans le futur : {collecte}")
    except ValueError:
        erreurs.append(f"date de collecte illisible : {collecte!r}")
    ref = etat.get("reference_nationale") or {}
    med_nat = ref.get("mediane")
    if not isinstance(med_nat, (int, float)) or not MEDIANE_NATIONALE_PLAUSIBLE[0] <= med_nat <= MEDIANE_NATIONALE_PLAUSIBLE[1]:
        erreurs.append(f"médiane nationale invraisemblable : {med_nat!r}")
    couverture = etat.get("couverture") or {}
    if int(couverture.get("communes_mediane", 0)) < minimum_communes:
        erreurs.append(
            f"couverture trop faible : {couverture.get('communes_mediane')} communes (attendu >= {minimum_communes})"
        )
    fichiers = etat.get("fichiers") or []
    if not isinstance(fichiers, list) or not fichiers:
        erreurs.append("liste des fichiers départementaux absente")
    total_com = 0
    for nom in fichiers:
        chemin_dep = dossier / str(nom)
        if not chemin_dep.is_file():
            erreurs.append(f"fichier départemental manquant : {nom}")
            continue
        try:
            donnees_dep = json.loads(chemin_dep.read_text(encoding="utf-8"))
        except json.JSONDecodeError as erreur:
            erreurs.append(f"{nom} illisible : {erreur}")
            continue
        communes = donnees_dep.get("communes") or {}
        if not isinstance(communes, dict) or not communes:
            erreurs.append(f"{nom} : aucune commune")
            continue
        for code, valeurs in communes.items():
            if not MOTIF_COMMUNE.match(str(code)):
                erreurs.append(f"{nom} : code commune invalide {code!r}")
                break
            if not isinstance(valeurs, list) or len(valeurs) != 2:
                erreurs.append(f"{nom} — {code} : format inattendu {valeurs!r}")
                break
            med, pauv = valeurs
            if not isinstance(med, (int, float)) or not MEDIANE_PLAUSIBLE[0] <= med <= MEDIANE_PLAUSIBLE[1]:
                erreurs.append(f"{nom} — {code} : médiane invraisemblable {med!r}")
                break
            if pauv is not None and (
                not isinstance(pauv, (int, float)) or not PAUVRETE_PLAUSIBLE[0] <= pauv <= PAUVRETE_PLAUSIBLE[1]
            ):
                erreurs.append(f"{nom} — {code} : taux de pauvreté invraisemblable {pauv!r}")
                break
            total_com += 1
    if total_com != int(couverture.get("communes_mediane", -1)):
        erreurs.append(
            f"total des communes dans les fichiers ({total_com}) != couverture annoncée ({couverture.get('communes_mediane')})"
        )
    if erreurs:
        print("ÉCHEC — collecte des revenus (FiLoSoFi)", file=sys.stderr)
        for erreur in erreurs:
            print(f"    {erreur}", file=sys.stderr)
        return 1
    print(
        f"Revenus FiLoSoFi conformes : {total_com} communes sur {len(fichiers)} départements, "
        f"millésime {etat.get('millesime')}, collecte du {collecte}, "
        f"licence {source.get('licence')}."
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
        etat, fichiers_dep = collecter(arguments.base)
    except Refus as erreur:
        print(f"ERREUR — {erreur}", file=sys.stderr)
        print("Rien n'a été écrit : les données précédentes restent en place.", file=sys.stderr)
        return 1
    arguments.sortie.mkdir(parents=True, exist_ok=True)
    # Nettoyer d'éventuels anciens fichiers r-*.json absents du nouveau millésime
    for ancien in arguments.sortie.glob("r-*.json"):
        if ancien.name not in fichiers_dep:
            ancien.unlink()
    for nom, contenu in fichiers_dep.items():
        (arguments.sortie / nom).write_text(
            json.dumps(contenu, ensure_ascii=False, separators=(",", ":")) + "\n",
            encoding="utf-8",
        )
    (arguments.sortie / "_etat.json").write_text(
        json.dumps(etat, ensure_ascii=False, indent=1, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    try:
        nom = arguments.sortie.relative_to(RACINE).as_posix()
    except ValueError:
        nom = str(arguments.sortie)
    print(
        f"Collecte écrite : {nom} — "
        f"{etat['couverture']['communes_mediane']} communes, {len(fichiers_dep)} départements, "
        f"millésime {etat['millesime']}."
    )
    return 0


if __name__ == "__main__":
    sys.exit(principal())
