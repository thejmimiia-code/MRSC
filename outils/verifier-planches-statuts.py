#!/usr/bin/env python3
"""Contrôle des planches des statuts et de leur archive.

Vérifie, sans réseau et sans dépendance externe :

1. que les planches citées par `docs/rd/plan-statuts-animation.md` existent ;
2. qu'aucune autre référence `statuts-animation/…` du dépôt ne pointe vers un
   fichier absent (hors archive) ;
3. qu'aucun PNG n'est suivi dans `docs/rd/statuts-animation/` ;
4. que les liens d'image des documents `docs/rd/*.md` désignent un fichier
   présent, ou à défaut une planche figurant au manifeste de l'archive ;
5. que le manifeste d'empreintes de l'archive décrit bien les 343 fichiers de son périmètre associatif.

Le manifeste n'est vérifié **en contenu** que sur demande, avec
`--empreintes DOSSIER` : il décrit une archive restaurée (l'étiquette
`planches-statuts-animation-2026-10`), pas l'arbre de travail. Comparer les
fichiers présents dans le dépôt au manifeste produirait de faux écarts — la bible
du film, par exemple, vit dans l'arbre et change, alors que l'archive est figée.

Usage :
    python3 outils/verifier-planches-statuts.py [--verifier]
    python3 outils/verifier-planches-statuts.py --empreintes /tmp/verif-archive

`--verifier` est accepté pour rester homogène avec les autres outils ; le
contrôle est identique. Code de sortie : 0 si tout est conforme, 1 sinon.
"""

from __future__ import annotations

import argparse
import hashlib
import os
import re
import subprocess
import sys
from pathlib import Path

#: Racine lue par le contrôle. La surcharge sert au banc de mutation
#: (`outils/test_mutations_planches_statuts.py`), qui casse une planche, un lien
#: d'image ou le manifeste dans une copie du dépôt.
RACINE = Path(os.environ.get("MRSC_RACINE") or Path(__file__).resolve().parent.parent).resolve()
PLAN = RACINE / "docs" / "rd" / "plan-statuts-animation.md"
DOSSIER = RACINE / "docs" / "rd" / "statuts-animation"
MANIFESTE = DOSSIER / "ARCHIVE-film-associatif.sha256"
FICHIERS_ARCHIVES = 343
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


def entrees_du_manifeste(lignes: list[str]) -> list[tuple[str, str]]:
    """(empreinte, nom) des lignes bien formées du manifeste."""
    entrees = []
    for ligne in lignes:
        morceaux = ligne.split("  ", 1)
        if len(morceaux) == 2 and re.fullmatch(r"[0-9a-f]{64}", morceaux[0]):
            entrees.append((morceaux[0], morceaux[1].strip()))
    return entrees


def verifier_empreintes(dossier: Path, entrees: list[tuple[str, str]]) -> tuple[int, int, list[str]]:
    """Compare les empreintes de `dossier` au manifeste.

    Rend (fichiers vérifiés, fichiers absents, écarts). Un fichier absent n'est
    pas un écart : l'archive restaurée peut être partielle ; c'est le compte qui
    dit ce qui a été réellement vérifié.
    """
    verifies = 0
    absents = 0
    ecarts: list[str] = []
    for empreinte, nom in entrees:
        chemin = dossier / nom
        if not chemin.is_file():
            absents += 1
            continue
        calcule = hashlib.sha256(chemin.read_bytes()).hexdigest()
        verifies += 1
        if calcule != empreinte:
            ecarts.append(
                f"empreinte différente : {nom} (attendu {empreinte[:16]}…, calculé {calcule[:16]}…)"
            )
    return verifies, absents, ecarts


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
    analyseur = argparse.ArgumentParser(description="Planches des statuts et archive")
    analyseur.add_argument("--verifier", action="store_true", help="homogénéité avec les autres outils (sans effet)")
    analyseur.add_argument(
        "--empreintes",
        metavar="DOSSIER",
        help="vérifie les empreintes d'une archive restaurée dans DOSSIER",
    )
    options = analyseur.parse_args()

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

    # Un dépôt git illisible ne doit pas se lire « aucun PNG suivi ». Avant le
    # 28 octobre 2026, `git ls-files` en échec rendait une sortie vide, et le
    # contrôle annonçait fièrement l'absence de PNG qu'il n'avait pas cherchés.
    interrogation = subprocess.run(
        ["git", "ls-files", "docs/rd/statuts-animation"],
        cwd=RACINE, capture_output=True, text=True, check=False,
    )
    if interrogation.returncode != 0:
        erreurs.append(
            "dépôt git illisible depuis "
            f"{RACINE} : le contrôle des PNG suivis n'a pas pu être fait "
            f"({interrogation.stderr.strip().splitlines()[0] if interrogation.stderr.strip() else 'sans message'})"
        )
    suivis = interrogation.stdout.splitlines()
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

    # Vérification en contenu, seulement sur demande : le manifeste décrit
    # l'archive restaurée, pas l'arbre de travail.
    verifies = absents = 0
    if options.empreintes:
        dossier = Path(options.empreintes)
        if not dossier.is_dir():
            erreurs.append(f"archive introuvable : {dossier}")
        else:
            lignes_manifeste = MANIFESTE.read_text(encoding="utf-8").splitlines() if MANIFESTE.is_file() else []
            verifies, absents, ecarts = verifier_empreintes(dossier, entrees_du_manifeste(lignes_manifeste))
            erreurs.extend(ecarts)
            if not verifies and not absents:
                erreurs.append(f"archive vide ou manifeste illisible : {dossier}")

    if erreurs:
        print("ÉCHEC — planches des statuts")
        for erreur in erreurs:
            print(f"  - {erreur}")
        return 1

    if options.empreintes:
        print(
            f"OK — archive vérifiée : {verifies} empreinte(s) conforme(s), "
            f"{absents} fichier(s) absent(s) de la copie restaurée, aucun écart."
        )
    print(
        f"OK — planches des statuts : {len(citees)} planches citées présentes, "
        f"aucune référence cassée, aucun PNG suivi, {len(archivees)} fichiers archivés, "
        f"{len(liens)} liens d'image contrôlés dont {archives_docs} vers l'archive, "
        f"manifeste de {FICHIERS_ARCHIVES} empreintes bien formées "
        f"(contenu non vérifié ici : l'archive vit hors de l'arbre, voir --empreintes)."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
