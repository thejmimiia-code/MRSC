#!/usr/bin/env python3
"""Contrôle des planches des statuts et de leur archive.

Vérifie, sans réseau et sans dépendance externe :

1. que les planches citées par `docs/rd/plan-statuts-animation.md` existent ;
2. qu'aucune autre référence `statuts-animation/…` du dépôt ne pointe vers un
   fichier absent (hors archive) ;
3. qu'aucun PNG n'est suivi dans `docs/rd/statuts-animation/` ;
4. que les liens d'image des documents `docs/rd/*.md` désignent un fichier
   présent, ou à défaut une planche figurant au manifeste de l'archive ;
5. que le manifeste d'empreintes de l'archive décrit bien 507 fichiers.

Usage :
    python3 outils/verifier-planches-statuts.py [--verifier]

`--verifier` est accepté pour rester homogène avec les autres outils ; le
contrôle est identique. Code de sortie : 0 si tout est conforme, 1 sinon.
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
PLAN = RACINE / "docs" / "rd" / "plan-statuts-animation.md"
DOSSIER = RACINE / "docs" / "rd" / "statuts-animation"
MANIFESTE = DOSSIER / "ARCHIVE-planches-2026-10.sha256"
FICHIERS_ARCHIVES = 507
EXTENSIONS = (".md", ".html", ".toml", ".py", ".json", ".yml", ".yaml")


def references_planches() -> list[tuple[Path, str]]:
    """Retourne (fichier, chemin relatif) pour chaque référence statuts-animation/…"""
    trouves: list[tuple[Path, str]] = []
    for fichier in RACINE.rglob("*"):
        if not fichier.is_file() or fichier.suffix not in EXTENSIONS:
            continue
        if ".git" in fichier.parts or "statuts-animation" in fichier.parts:
            continue
        try:
            texte = fichier.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        for nom in re.findall(
            r"statuts-animation/([A-Za-z0-9._-]+\.[A-Za-z0-9]{2,4})(?![A-Za-z0-9])", texte
        ):
            trouves.append((fichier, nom))
    return trouves


def liens_images_docs() -> list[tuple[Path, str, bool]]:
    """Liens d'image des documents de `docs/rd/` : (fichier, cible, existe)."""
    trouves: list[tuple[Path, str, bool]] = []
    for fichier in sorted((RACINE / "docs" / "rd").rglob("*.md")):
        try:
            texte = fichier.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        for cible in re.findall(r"\]\(([^)\s]+\.(?:png|jpe?g|webp))\)", texte):
            if "://" in cible:
                continue
            chemin = (fichier.parent / cible).resolve()
            trouves.append((fichier, cible, chemin.is_file()))
    return trouves


def main() -> int:
    erreurs: list[str] = []

    if not PLAN.is_file():
        print("ÉCHEC — plan des statuts absent")
        return 1
    plan = PLAN.read_text(encoding="utf-8")
    citees = sorted(set(re.findall(r"\]\((statuts-animation/[^)]+)\)", plan)))
    if not citees:
        erreurs.append("aucune planche citée dans le plan")
    for lien in citees:
        if not (RACINE / "docs" / "rd" / lien).is_file():
            erreurs.append(f"planche citée absente : {lien}")

    # Les documents peuvent citer une planche archivée (exemple de commande de
    # récupération) : la référence reste valide si le fichier figure au manifeste.
    archivees: set[str] = set()
    if MANIFESTE.is_file():
        for ligne in MANIFESTE.read_text(encoding="utf-8").splitlines():
            morceaux = ligne.split("  ", 1)
            if len(morceaux) == 2:
                archivees.add(morceaux[1].strip())
    for fichier, nom in sorted(set(references_planches())):
        if (DOSSIER / nom).exists() or nom in archivees:
            continue
        erreurs.append(f"référence sans fichier ni archive : {fichier.relative_to(RACINE)} → statuts-animation/{nom}")

    liens = liens_images_docs()
    archives_docs = 0
    for fichier, cible, existe in liens:
        if existe:
            continue
        if Path(cible).name in archivees:
            archives_docs += 1
            continue
        erreurs.append(f"lien d'image non résolu : {fichier.relative_to(RACINE)} → {cible}")

    suivis = subprocess.run(
        ["git", "ls-files", "docs/rd/statuts-animation"],
        cwd=RACINE, capture_output=True, text=True, check=False,
    ).stdout.splitlines()
    if suivis:
        for chemin in suivis:
            if chemin.lower().endswith(".png"):
                erreurs.append(f"PNG suivi dans l'arbre : {chemin}")

    if not MANIFESTE.is_file():
        erreurs.append("manifeste d'archive absent")
    else:
        lignes = [ligne for ligne in MANIFESTE.read_text(encoding="utf-8").splitlines() if ligne.strip()]
        if len(lignes) != FICHIERS_ARCHIVES:
            erreurs.append(f"manifeste : {len(lignes)} empreintes au lieu de {FICHIERS_ARCHIVES}")
        if len({ligne.split("  ", 1)[-1] for ligne in lignes}) != len(lignes):
            erreurs.append("manifeste : noms de fichiers en double")
        for ligne in lignes:
            if not re.fullmatch(r"[0-9a-f]{64}  [^/]+", ligne):
                erreurs.append(f"ligne de manifeste invalide : {ligne[:80]}")
                break

    if erreurs:
        print("ÉCHEC — planches des statuts")
        for erreur in erreurs:
            print(f"  - {erreur}")
        return 1

    print(
        f"OK — planches des statuts : {len(citees)} planches citées présentes, "
        f"aucune référence cassée, aucun PNG suivi, {len(archivees)} fichiers archivés, "
        f"{len(liens)} liens d'image contrôlés dont {archives_docs} vers l'archive, "
        f"manifeste de {FICHIERS_ARCHIVES} empreintes conforme."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
