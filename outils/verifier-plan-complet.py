#!/usr/bin/env python3
"""Vérifie que le plan complet de R&D reste complet et honnête.

Le plan `docs/rd/plan-complet-rd-innovation-prospective.md` est une synthèse,
pas une source de vérité. Ce contrôle ne juge ni les scénarios, ni les
priorités, ni une décision de l’association : il empêche seulement la carte de
perdre une initiative, une section, un chemin local ou une réserve, et refuse
qu’une phrase y présente la R&D comme terminée ou validée par une personne.

Les identifiants viennent de `docs/rd/portefeuille.toml` : ajouter une
initiative sans la reporter dans le plan fait échouer la porte. Les chemins
locaux cités entre accents graves sont confrontés au dépôt. La racine peut être
surchargée par `MRSC_RACINE` pour le banc de mutation.

Usage :
    python3 outils/verifier-plan-complet.py
"""

from __future__ import annotations

import os
import re
import sys
import tomllib
from pathlib import Path

RACINE = Path(os.environ.get("MRSC_RACINE") or Path(__file__).resolve().parent.parent).resolve()
PLAN = RACINE / "docs" / "rd" / "plan-complet-rd-innovation-prospective.md"
PORTEFEUILLE = RACINE / "docs" / "rd" / "portefeuille.toml"

SECTIONS = (
    "## 1. Portée de la demande et limites",
    "## 2. Méthode et sources de vérité",
    "## 3. État mesuré au 10 novembre 2026",
    "## 4. Cartographie des 19 initiatives",
    "## 5. Plan par chantiers",
    "## 6. Ordonnancement et horizons",
    "## 7. Portes de décision et rôles",
    "## 8. Indicateurs de maintenance",
    "## 9. Ce que ce lot fait réellement",
    "## 10. Tenir le plan à jour",
)

REPERES = (
    "docs/apprentissage/relectures.toml",
    "31 janvier 2027",
    "2026-11-19",
    "décision",
)

INTERDITES = re.compile(
    r"(?i)\b(?:tout est relu|validation humaine obtenue|R&D terminée|projet achevé)\b"
)

CHEMIN = re.compile(
    r"`((?:docs|outils|assets|\.github)/[^`]+?"
    r"\.(?:md|toml|py|js|cjs|mjs|html|css|json|dot|yml|yaml|txt|xml|sh|patch|sha256))`"
)


def controler() -> list[str]:
    if not PLAN.is_file():
        return [f"plan complet absent : {PLAN.relative_to(RACINE)}"]
    texte = PLAN.read_text(encoding="utf-8")
    erreurs: list[str] = []

    for section in SECTIONS:
        if section not in texte:
            erreurs.append(f"section absente du plan : {section}")

    try:
        registre = tomllib.loads(PORTEFEUILLE.read_text(encoding="utf-8"))
    except (OSError, tomllib.TOMLDecodeError) as erreur:
        return [f"portefeuille illisible : {erreur}"]
    initiatives = registre.get("initiative", [])
    if not initiatives:
        erreurs.append("portefeuille sans initiative : le plan ne peut pas être confronté")
    identifiants = [str(i.get("id", "")) for i in initiatives if i.get("id")]
    for identifiant in identifiants:
        if f"`{identifiant}`" not in texte:
            erreurs.append(f"initiative absente du plan : {identifiant}")
    for identifiant in (str(i["id"]) for i in initiatives if i.get("priorite") == "P0"):
        if f"`{identifiant}`" not in texte:
            erreurs.append(f"initiative P0 absente du plan : {identifiant}")

    chemins = sorted(set(CHEMIN.findall(texte)))
    for chemin in chemins:
        if not (RACINE / chemin).exists():
            erreurs.append(f"chemin local introuvable : {chemin}")

    for repere in REPERES:
        if repere not in texte:
            erreurs.append(f"repère absent du plan : {repere}")

    trouve = INTERDITES.search(texte)
    if trouve:
        erreurs.append(f"formulation interdite : {trouve.group(0)}")

    return erreurs


def main() -> int:
    erreurs = controler()
    if erreurs:
        print("ÉCHEC — plan complet de R&D, d’innovation et de prospective", file=sys.stderr)
        for erreur in erreurs:
            print(f"    {erreur}", file=sys.stderr)
        return 1
    texte = PLAN.read_text(encoding="utf-8")
    initiatives = tomllib.loads(PORTEFEUILLE.read_text(encoding="utf-8")).get("initiative", [])
    p0 = sum(i.get("priorite") == "P0" for i in initiatives)
    chemins = len(set(CHEMIN.findall(texte)))
    print(
        f"Plan complet vérifié : {len(initiatives)} initiatives, {p0} P0, "
        f"{len(SECTIONS)} sections, {chemins} chemins locaux, "
        f"{len(REPERES)} repères, aucune formulation de validation inventée."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
