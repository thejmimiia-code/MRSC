#!/usr/bin/env python3
"""Contrôle qu'une fusion ou une suppression de branche ne perd rien.

Deux usages.

**Contrôles hors ligne** (par défaut, sans réseau) — exécutés à chaque
proposition par la porte de vérification :

1. aucune fusion en cours ni fichier non fusionné dans l'index ;
2. aucun marqueur de conflit (`<<<<<<<`, `>>>>>>>`) dans les fichiers suivis ;
3. aucun fichier de sauvegarde de fusion (`.orig`, `.rej`, `.bak`) suivi ;
4. journal de R&D en ordre antichronologique, sans titre en double.

**Audit des branches distantes** (`--branches`) — à lancer avant de supprimer
une branche ou après une vague de fusions. Pour chaque branche distante, l'outil
vérifie que **tout son contenu reste atteignable depuis les autres références**
(main, étiquettes, autres branches) : c'est la condition exacte pour pouvoir
supprimer la branche sans perte. Une branche qui porte un contenu unique est
signalée avec la liste des fichiers concernés.

Usage :
    python3 outils/verifier-fusions.py              # contrôles hors ligne
    python3 outils/verifier-fusions.py --branches   # + audit des branches

Code de sortie : 0 si rien n'est perdu et qu'aucune erreur ne reste, 1 sinon.
"""

from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
from pathlib import Path

#: Racine lue par le contrôle. La surcharge sert au banc de mutation
#: (`outils/test_mutations_fusions.py`), qui fabrique de petits dépôts git où
#: l'on casse le journal, l'index ou une branche — sans jamais toucher au dépôt
#: réel, dont l'historique n'a pas à servir de cobaye.
RACINE = Path(os.environ.get("MRSC_RACINE") or Path(__file__).resolve().parent.parent).resolve()
JOURNAL = RACINE / "docs" / "rd" / "journal.md"
MARQUEURS = re.compile(r"^(<<<<<<< |>>>>>>> )", re.MULTILINE)
SAUVEGARDES = (".orig", ".rej", ".bak", ".BACKUP", ".LOCAL", ".REMOTE")
EXTENSIONS_TEXTE = (
    ".md", ".html", ".css", ".js", ".py", ".toml", ".json", ".yml", ".yaml",
    ".txt", ".xml", ".cjs", ".sh", ".patch", ".gitignore",
)


def git(*arguments: str) -> str:
    return subprocess.run(
        ["git", *arguments], cwd=RACINE, capture_output=True, text=True, check=False
    ).stdout


def fichiers_suivis() -> list[str]:
    return [ligne for ligne in git("ls-files", "-z").split("\0") if ligne]


def controler_etat_de_fusion(erreurs: list[str]) -> None:
    if (RACINE / ".git" / "MERGE_HEAD").exists():
        erreurs.append("une fusion est en cours : terminer ou annuler avant de continuer")
    non_fusionnes = git("ls-files", "-u")
    if non_fusionnes.strip():
        chemins = sorted({ligne.split("\t")[-1] for ligne in non_fusionnes.splitlines()})
        erreurs.append(
            f"{len(chemins)} fichier(s) non fusionné(s) dans l'index : {', '.join(chemins[:5])}"
        )


def controler_marqueurs(erreurs: list[str], suivis: list[str]) -> None:
    for chemin in suivis:
        if not chemin.endswith(EXTENSIONS_TEXTE):
            continue
        fichier = RACINE / chemin
        try:
            texte = fichier.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        if MARQUEURS.search(texte):
            erreurs.append(f"marqueur de conflit dans {chemin}")


def controler_sauvegardes(erreurs: list[str], suivis: list[str]) -> None:
    for chemin in suivis:
        if chemin.endswith(SAUVEGARDES):
            erreurs.append(f"fichier de sauvegarde de fusion suivi : {chemin}")


def controler_journal(erreurs: list[str]) -> None:
    if not JOURNAL.is_file():
        erreurs.append("journal de R&D absent")
        return
    titres = re.findall(r"(?m)^## (\d{4}-\d{2}-\d{2}) — (.+)$", JOURNAL.read_text(encoding="utf-8"))
    if not titres:
        erreurs.append("journal : aucune entrée datée reconnue")
        return
    dates = [date for date, _ in titres]
    for precedent, suivant in zip(dates, dates[1:]):
        if suivant > precedent:
            erreurs.append(
                f"journal : entrée du {suivant} placée après celle du {precedent} (ordre antichronologique attendu)"
            )
            break
    libelles = [libelle for _, libelle in titres]
    doublons = sorted({libelle for libelle in libelles if libelles.count(libelle) > 1})
    if doublons:
        erreurs.append(f"journal : titres en double — {', '.join(doublons[:3])}")


def blobs_atteignables(exclure: str) -> set[str]:
    """Objets atteignables depuis toutes les références sauf `exclure`."""
    references = [
        reference
        for reference in git("for-each-ref", "--format=%(refname)").splitlines()
        if reference != exclure
    ]
    if not references:
        return set()
    sortie = subprocess.run(
        ["git", "rev-list", "--objects", "--no-object-names", *references],
        cwd=RACINE, capture_output=True, text=True, check=False,
    ).stdout
    return set(sortie.split())


def controler_branches(erreurs: list[str], avertissements: list[str]) -> None:
    distantes = [
        reference
        for reference in git("for-each-ref", "--format=%(refname)", "refs/remotes/origin").splitlines()
        if not reference.endswith("/main") and not reference.endswith("/HEAD")
    ]
    if not distantes:
        print("  audit des branches : aucune branche distante hors main")
        return

    main = "refs/remotes/origin/main"
    for reference in sorted(distantes):
        nom = reference[len("refs/remotes/origin/") :]
        est_ancetre = subprocess.run(
            ["git", "merge-base", "--is-ancestor", reference, main],
            cwd=RACINE, capture_output=True, check=False,
        ).returncode == 0
        if est_ancetre:
            print(f"  {nom} : contenue dans main")
            continue

        arbre = subprocess.run(
            ["git", "ls-tree", "-r", reference],
            cwd=RACINE, capture_output=True, text=True, check=False,
        ).stdout
        blobs = {}
        for ligne in arbre.splitlines():
            meta, chemin = ligne.split("\t", 1)
            blobs[chemin] = meta.split()[2]
        atteignables = blobs_atteignables(reference)
        uniques = sorted(chemin for chemin, blob in blobs.items() if blob not in atteignables)
        if uniques:
            erreurs.append(
                f"branche {nom} : {len(uniques)} fichier(s) présents nulle part ailleurs "
                f"(suppression = perte), par exemple {', '.join(uniques[:3])}"
            )
        else:
            print(
                f"  {nom} : contenu entièrement atteignable ailleurs "
                f"({len(blobs)} fichiers) — supprimable sans perte"
            )

    if len(distantes) > 1:
        avertissements.append(
            f"{len(distantes)} branches distantes hors main : envisager la suppression des branches absorbées"
        )


def main() -> int:
    analyseur = argparse.ArgumentParser(description=__doc__)
    analyseur.add_argument("--branches", action="store_true", help="auditer aussi les branches distantes")
    arguments = analyseur.parse_args()

    erreurs: list[str] = []
    avertissements: list[str] = []
    suivis = fichiers_suivis()

    controler_etat_de_fusion(erreurs)
    controler_marqueurs(erreurs, suivis)
    controler_sauvegardes(erreurs, suivis)
    controler_journal(erreurs)

    print("  contrôles hors ligne : état de fusion, marqueurs, sauvegardes, journal")
    if arguments.branches:
        controler_branches(erreurs, avertissements)

    for avertissement in avertissements:
        print(f"  AVERTISSEMENT — {avertissement}")

    if erreurs:
        print("ÉCHEC — une fusion ou une suppression perdrait du contenu ou laisserait une erreur")
        for erreur in erreurs:
            print(f"  - {erreur}")
        return 1

    print(
        f"OK — aucune fusion en cours, aucun marqueur de conflit dans {len(suivis)} fichiers suivis, "
        f"journal en ordre antichronologique et sans doublon."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
