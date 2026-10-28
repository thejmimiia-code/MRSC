#!/usr/bin/env python3
"""Outils partagés des bancs de mutation : copie jetable, mutation, exécution.

Un banc de mutation vérifie qu'un contrôle **échoue** quand on plante la faute
qu'il prétend voir. Il lui faut donc deux choses qu'aucun test ordinaire ne
demande : un dépôt modifiable sans risque, et un moyen de lancer l'outil sur
cette copie.

La copie est faite de **liens symboliques** : seuls les fichiers réellement mutés
deviennent de vraies copies, et les dossiers parents sont matérialisés au besoin.
Rien n'est jamais écrit dans l'arbre de travail.

Ce module n'est pas un test : il est importé par `test_mutations_affichages.py`
et `test_mutations_site_statique.py`. Il ne prouve rien à lui seul ; ses deux
garanties — le dépôt reste intact, la copie intacte est verte — sont vérifiées
par chaque banc qui l'utilise.
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent

#: Entrées jamais recopiées : l'historique git n'a rien à faire dans un banc, et
#: les caches locaux ne sont pas lus par les contrôles.
EXCLUES = frozenset({".git", "__pycache__", "node_modules", "_site"})


def copie_jetable(dossier: Path, racine: Path = RACINE) -> None:
    """Remplit `dossier` de liens symboliques vers chaque entrée de `racine`."""
    for entree in racine.iterdir():
        if entree.name in EXCLUES:
            continue
        (dossier / entree.name).symlink_to(entree, target_is_directory=entree.is_dir())


def copie_complete(dossier: Path, racine: Path = RACINE) -> None:
    """Copie réellement l'arborescence, sans `.git` ni caches.

    Les liens symboliques suffisent à la plupart des bancs, mais pas à ceux dont
    l'outil compare des chemins **résolus** : `verifier-site-statique.py` vérifie
    qu'aucune cible ne sort du dépôt, et un lien vers l'original sort de la copie
    par construction. Pour ces contrôles-là, une vraie copie est la seule
    honnête — le dépôt pèse moins de 30 Mio, la copie prend moins d'une seconde.
    """
    shutil.copytree(
        racine,
        dossier,
        symlinks=False,
        ignore=shutil.ignore_patterns(*EXCLUES),
        dirs_exist_ok=True,
    )


def ouvrir(dossier: Path, relatif: str, racine: Path = RACINE) -> Path:
    """Rend un chemin réel dans la copie, en défaisant les liens du chemin.

    Pour écrire `assets/css/site.css` sans toucher au dépôt, il faut que
    `assets` puis `assets/css` soient de vrais dossiers : ils sont recréés, et
    leurs autres enfants restent des liens vers l'original. La fonction est
    idempotente, parce que deux mutations successives empruntent le même chemin.
    """
    morceaux = Path(relatif).parts
    courant, original = dossier, racine
    for position, morceau in enumerate(morceaux[:-1]):
        suivant, cible = courant / morceau, original / morceau
        descendant = morceaux[position + 1]
        if suivant.is_symlink():
            suivant.unlink()
        suivant.mkdir(exist_ok=True)
        for enfant in cible.iterdir():
            if enfant.name == descendant or (suivant / enfant.name).exists():
                continue
            (suivant / enfant.name).symlink_to(enfant, target_is_directory=enfant.is_dir())
        courant, original = suivant, cible
    return courant / morceaux[-1]


def muter(dossier: Path, relatif: str, ancien: str, nouveau: str, racine: Path = RACINE) -> None:
    """Remplace un fragment dans une copie réelle du fichier, jamais dans l'original.

    Lève `AssertionError` si le fragment est absent : une mutation qui ne change
    rien ferait passer le banc pour un succès sans avoir rien prouvé.
    """
    chemin = ouvrir(dossier, relatif, racine)
    if chemin.is_symlink():
        chemin.unlink()
    if not chemin.exists():
        shutil.copyfile(racine / relatif, chemin)
    texte = chemin.read_text(encoding="utf-8")
    if ancien not in texte:
        raise AssertionError(f"fragment absent de {relatif} : la mutation ne mordrait pas")
    chemin.write_text(texte.replace(ancien, nouveau, 1), encoding="utf-8")


def lancer(
    outil: str,
    dossier: Path,
    variable: str = "MRSC_RACINE",
    racine: Path = RACINE,
    arguments: tuple[str, ...] = (),
) -> subprocess.CompletedProcess[str]:
    """Exécute `outils/<outil>` en lui faisant lire la copie au lieu du dépôt.

    L'outil reste celui du dépôt : c'est bien le contrôle livré que l'on éprouve,
    pas une variante. Seule la racine qu'il lit change, par la variable
    d'environnement que chaque contrôle concerné documente.
    """
    environnement = dict(os.environ, **{variable: str(dossier)})
    return subprocess.run(
        [sys.executable, str(racine / "outils" / outil), *arguments],
        capture_output=True,
        text=True,
        check=False,
        env=environnement,
    )
