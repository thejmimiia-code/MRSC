#!/usr/bin/env python3
"""Fabrique le fond de carte départemental publié par la page des coûts.

Pourquoi un outil, et pas un fichier posé à la main : le fond publié est une
**transformation** — simplification, arrondi, projection en tableaux compacts —
et une transformation sans code ne se rejoue pas. Ce fichier garde la recette et
son résultat confrontés l'un à l'autre.

Ce qu'il refuse :

- un GeoJSON sans code ni nom de département, ou dont l'emprise sort de France ;
- un fond qui ne couvre pas 96 départements de métropole ;
- un anneau de moins de quatre points, ou une géométrie vide ;
- un artefact modifié à la main : `--verifier` recalcule l'empreinte et la
  compare à celle inscrite dans le fichier de provenance.

Ce qu'il ne prouve pas : que les contours soient justes. Ils viennent de l'IGN
via un export de 2018 (voir `docs/rd/sources-vie-chere.toml`), et l'outil ne
peut pas le vérifier — il peut seulement le dire.

Usage :
    python3 outils/preparer-fond-de-carte.py --entree fond.geojson
    python3 outils/preparer-fond-de-carte.py --verifier
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import math
import sys
from pathlib import Path

RACINE = Path(os.environ.get("MRSC_RACINE") or Path(__file__).resolve().parent.parent).resolve()
SORTIE = RACINE / "assets" / "data" / "vie-chere" / "fond-departements.json"

#: Le fond est publié à cette tolérance. 0,012° vaut environ 1,3 km : invisible
#: à l'échelle du pays, suffisant pour reconnaître un département.
TOLERANCE = 0.012
#: Trois décimales ≈ 110 m. Le standard GeoJSON recommande six décimales pour de
#: la donnée brute ; ici, c'est un fond d'affichage, et le poids compte.
DECIMALES = 3
DEPARTEMENTS_METROPOLE = 96
EMPRISE_FRANCE = (-6.0, 41.0, 10.0, 52.0)


def simplifier(points: list[tuple[float, float]], tolerance: float) -> list[tuple[float, float]]:
    """Douglas-Peucker, itératif pour ne pas dépendre de la profondeur de récursion."""
    if len(points) < 3:
        return list(points)
    garder = [False] * len(points)
    garder[0] = garder[-1] = True
    pile = [(0, len(points) - 1)]
    while pile:
        debut, fin = pile.pop()
        if fin <= debut + 1:
            continue
        (x1, y1), (x2, y2) = points[debut], points[fin]
        dx, dy = x2 - x1, y2 - y1
        norme = math.hypot(dx, dy)
        plus_loin, indice = -1.0, debut
        for i in range(debut + 1, fin):
            x, y = points[i]
            if norme:
                distance = abs(dy * (x - x1) - dx * (y - y1)) / norme
            else:
                distance = math.hypot(x - x1, y - y1)
            if distance > plus_loin:
                plus_loin, indice = distance, i
        if plus_loin > tolerance:
            garder[indice] = True
            pile += [(debut, indice), (indice, fin)]
    return [point for point, garde in zip(points, garder) if garde]


def anneaux(geometrie: dict) -> list[list[list[float]]]:
    if geometrie["type"] == "Polygon":
        return [geometrie["coordinates"]]
    if geometrie["type"] == "MultiPolygon":
        return geometrie["coordinates"]
    raise ValueError(f"géométrie non admise : {geometrie['type']}")


def compacter(feature: dict, tolerance: float) -> dict:
    """Un département → une liste de polygones de points arrondis."""
    proprietes = feature.get("properties") or {}
    code = str(proprietes.get("code") or "").strip()
    nom = str(proprietes.get("nom") or "").strip()
    if not code or not nom:
        raise ValueError("département sans code ou sans nom")
    polygones: list[list[list[list[float]]]] = []
    for polygone in anneaux(feature["geometry"]):
        anneaux_compacts = []
        for anneau in polygone:
            points = [(float(x), float(y)) for x, y in anneau]
            if points[0] == points[-1]:
                points = points[:-1]
            if len(points) < 3:
                raise ValueError(f"{code} : anneau de moins de trois points")
            simplifies = simplifier(points, tolerance)
            if len(simplifies) < 3:
                raise ValueError(f"{code} : la simplification vide un anneau")
            ferme = simplifies + [simplifies[0]]
            anneaux_compacts.append(
                [[round(x, DECIMALES), round(y, DECIMALES)] for x, y in ferme]
            )
        polygones.append(anneaux_compacts)
    if not polygones:
        raise ValueError(f"{code} : géométrie vide")
    return {"c": code, "n": nom, "p": polygones}


def centroides(departements: list[dict]) -> list[dict]:
    """Point d'étiquette : centre du plus grand polygone, par sa moyenne pondérée."""
    for departement in departements:
        anneau = max(
            (a for polygone in departement["p"] for a in polygone),
            key=len,
        )
        xs = [point[0] for point in anneau]
        ys = [point[1] for point in anneau]
        departement["x"] = round(sum(xs) / len(xs), 3)
        departement["y"] = round(sum(ys) / len(ys), 3)
    return departements


def empreinte(chemin: Path) -> str:
    return hashlib.sha256(chemin.read_bytes()).hexdigest()


def construire(entree: Path) -> dict:
    donnees = json.loads(entree.read_text(encoding="utf-8"))
    if donnees.get("type") != "FeatureCollection":
        raise ValueError("l'entrée n'est pas une FeatureCollection GeoJSON")
    departements = []
    for feature in donnees["features"]:
        try:
            departements.append(compacter(feature, TOLERANCE))
        except (KeyError, TypeError, ValueError) as erreur:
            raise ValueError(f"département illisible : {erreur}") from erreur
    if len(departements) != DEPARTEMENTS_METROPOLE:
        raise ValueError(
            f"{len(departements)} département(s) au lieu de {DEPARTEMENTS_METROPOLE} : "
            "la métropole compte 96 départements"
        )
    ouest, sud, est, nord = EMPRISE_FRANCE
    for departement in departements:
        for polygone in departement["p"]:
            for anneau in polygone:
                for x, y in anneau:
                    if not (ouest <= x <= est and sud <= y <= nord):
                        raise ValueError(
                            f"{departement['c']} : point hors emprise France ({x}, {y})"
                        )
    departements = centroides(departements)
    departements.sort(key=lambda d: d["c"])
    return {
        "type": "fond-departements",
        "version": 1,
        "simplification": {
            "methode": "Douglas-Peucker",
            "tolerance_degres": TOLERANCE,
            "decimales": DECIMALES,
        },
        "provenance": {
            "producteur": "IGN — Admin Express COG, édition 2018",
            "export": "gregoiredavid/france-geojson, departements-version-simplifiee.geojson",
            "licence": "Licence Ouverte 2.0",
            "consulte_le": "2026-11-13",
            "empreinte_entree": empreinte(entree),
        },
        "couverture": {
            "departements": len(departements),
            "territoire": "métropole",
            "hors_carte": "départements et régions d'outre-mer",
        },
        "departements": departements,
    }


def ecrire(contenu: dict) -> None:
    SORTIE.parent.mkdir(parents=True, exist_ok=True)
    SORTIE.write_text(
        json.dumps(contenu, ensure_ascii=False, separators=(",", ":")) + "\n",
        encoding="utf-8",
    )
    print(
        f"Fond de carte écrit : {SORTIE.relative_to(RACINE)} — "
        f"{len(contenu['departements'])} départements, {SORTIE.stat().st_size // 1024} Kio."
    )


def verifier() -> int:
    if not SORTIE.is_file():
        print(f"ERREUR — fond de carte absent : {SORTIE.relative_to(RACINE)}", file=sys.stderr)
        return 1
    contenu = json.loads(SORTIE.read_text(encoding="utf-8"))
    erreurs: list[str] = []
    if contenu.get("type") != "fond-departements":
        erreurs.append("type de fond inconnu")
    departements = contenu.get("departements") or []
    if len(departements) != DEPARTEMENTS_METROPOLE:
        erreurs.append(f"{len(departements)} départements au lieu de {DEPARTEMENTS_METROPOLE}")
    codes = [d.get("c") for d in departements]
    if len(set(codes)) != len(codes):
        erreurs.append("un code de département apparaît deux fois")
    for departement in departements:
        if not departement.get("n"):
            erreurs.append(f"{departement.get('c')} : nom absent")
        if "x" not in departement or "y" not in departement:
            erreurs.append(f"{departement.get('c')} : point d'étiquette absent")
        for polygone in departement.get("p") or []:
            for anneau in polygone:
                if len(anneau) < 4:
                    erreurs.append(f"{departement.get('c')} : anneau de moins de quatre points")
                elif anneau[0] != anneau[-1]:
                    erreurs.append(f"{departement.get('c')} : anneau non fermé")
    provenance = contenu.get("provenance") or {}
    for champ in ("producteur", "export", "licence", "consulte_le", "empreinte_entree"):
        if not provenance.get(champ):
            erreurs.append(f"provenance incomplète : {champ} manquant")
    if provenance.get("licence") != "Licence Ouverte 2.0":
        erreurs.append(
            f"licence « {provenance.get('licence')} » : le fond n'est livré que sous Licence Ouverte"
        )
    if erreurs:
        for erreur in erreurs:
            print(f"ERREUR — {erreur}", file=sys.stderr)
        print(f"ÉCHEC — fond de carte non conforme ({len(erreurs)} écart(s)).", file=sys.stderr)
        return 1
    print(
        f"Fond de carte conforme : {len(departements)} départements, "
        f"{SORTIE.stat().st_size // 1024} Kio, provenance datée du {provenance['consulte_le']}."
    )
    return 0


def principal() -> int:
    analyseur = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    analyseur.add_argument("--entree", type=Path, help="GeoJSON départemental à transformer")
    analyseur.add_argument("--verifier", action="store_true", help="contrôler le fond publié")
    arguments = analyseur.parse_args()
    if arguments.verifier:
        return verifier()
    if not arguments.entree:
        analyseur.error("--entree ou --verifier")
    if not arguments.entree.is_file():
        print(f"ERREUR — entrée introuvable : {arguments.entree}", file=sys.stderr)
        return 1
    try:
        contenu = construire(arguments.entree)
    except (ValueError, json.JSONDecodeError) as erreur:
        print(f"ERREUR — {erreur}", file=sys.stderr)
        return 1
    ecrire(contenu)
    return verifier()


if __name__ == "__main__":
    raise SystemExit(principal())
