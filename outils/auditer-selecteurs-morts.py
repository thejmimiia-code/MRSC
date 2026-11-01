#!/usr/bin/env python3
"""Relève les classes de la feuille qu'aucune page, aucun script, aucun générateur n'ouvre.

Le 1er novembre 2026, le modèle des grilles annonçait quatre grilles « proportion »
restantes. Deux d'entre elles — `.ai-feature-panel` et `.simulateur-promo-panel` —
n'existaient **que dans la feuille** : aucune page ne les employait, aucun
générateur non plus. Le relevé ne pouvait pas le dire, et il proposait donc pour
elles des conversions sans objet. Une grille que personne n'ouvre n'a pas de
repli à reproduire ; elle a une règle à retirer.

Ce contrôle lit `assets/css/site.css` (et pas seulement ses déclarations de
grille), puis cherche chaque classe dans les sources qui peuvent en produire une
instance : pages HTML servies, scripts `.js`/`.mjs`/`.cjs`, générateurs `.py`,
données `.json`/`.svg`. Trois verdicts, jamais deux :

- **lue** — le nom figure en toutes lettres dans une de ces sources ;
- **dynamique** — le nom ne figure nulle part, mais une source le construit à
  l'exécution (`adventure-learning-world-${n}`, `"carte-" + i`) : la classe peut
  exister, on ne peut pas le savoir d'ici ;
- **morte** — ni l'un ni l'autre. Seul ce verdict est refusé.

Ce qu'il ne voit pas, et qu'il faut savoir avant de le croire :

- une classe construite par une source qu'il ne lit pas (un service distant, un
  modèle de page hébergé ailleurs) serait dite morte à tort ;
- il ne dit rien de l'utilité d'une classe **lue** : une règle peut viser une
  classe présente et n'avoir aucun effet ;
- un nom cité dans un registre, dans ce journal ou dans la documentation d'un
  outil n'est pas une instance, c'est une trace : `.md` et `.toml` sont hors
  corpus, et l'outil comme ses bancs (`test_*`) se retirent de leur propre
  relevé — un banc ne rend aucune page.

Usage :
    python3 outils/auditer-selecteurs-morts.py            # relevé lisible
    python3 outils/auditer-selecteurs-morts.py --liste    # un nom par ligne
    python3 outils/auditer-selecteurs-morts.py --verifier # code 1 si une morte
"""

from __future__ import annotations

import argparse
import os
import re
import sys
from pathlib import Path

#: Racine lue. La surcharge sert au banc, qui casse une copie du dépôt.
RACINE = Path(os.environ.get("MRSC_RACINE") or Path(__file__).resolve().parent.parent).resolve()

FEUILLES = ("assets/css/site.css", "assets/css/anglais-aventure.css")

#: Extensions lues comme sources d'instances. Les `.md` et `.toml` sont
#: volontairement absents : un registre cite un nom, il ne crée pas d'élément.
EXTENSIONS = {".html", ".js", ".mjs", ".cjs", ".py", ".json", ".svg"}

#: Dossiers hors corpus : la documentation décrit, elle ne sert pas.
EXCLUS = {".git", "docs", "node_modules", "__pycache__", ".github"}

#: Nombre minimal de sources lues pour croire le relevé. En dessous, l'outil
#: n'a pas lu son corpus et le dit au lieu de déclarer tout mort.
SOURCES_MINIMALES = 20

CLASSE = re.compile(r"\.(-?[_a-zA-Z][\w-]*)")

#: Un nom de classe construit à l'exécution : préfixe suivi d'une interpolation
#: de gabarit (`${`), d'une accolade de f-ligne (`{`) ou d'une concaténation.
DYNAMIQUES = (
    re.compile(r"([A-Za-z][\w-]*)-\$\{"),
    re.compile(r"([A-Za-z][\w-]*)-\{(?!\s*\})"),
    re.compile(r"[\"']([A-Za-z][\w-]*-)[\"']\s*\+"),
    re.compile(r"[\"']([A-Za-z][\w-]*-\s*)$", re.M),
)


def sans_commentaires(texte: str) -> str:
    """Retire les commentaires CSS, en gardant les sauts de ligne et les colonnes."""
    sortie: list[str] = []
    i, longueur = 0, len(texte)
    while i < longueur:
        if texte.startswith("/*", i):
            fin = texte.find("*/", i + 2)
            fin = longueur if fin == -1 else fin + 2
            sortie.append(re.sub(r"[^\n]", " ", texte[i:fin]))
            i = fin
            continue
        sortie.append(texte[i])
        i += 1
    return "".join(sortie)


def selecteurs_de(texte: str) -> list[tuple[str, int]]:
    """Les sélecteurs de la feuille, avec leur numéro de ligne.

    Ne lit que le texte qui précède une accolade ouvrante : une couleur, une
    police ou un contenu entre guillemets n'est pas un sélecteur, et compter
    `.5` dans `minmax(.5fr, 1fr)` comme une classe ferait un faux mort de plus.
    """
    propre = sans_commentaires(texte)
    trouves: list[tuple[str, int]] = []
    debut = 0
    profondeur = 0
    morceau_debut = 0
    for i, caractere in enumerate(propre):
        if caractere == "{":
            if profondeur == 0:
                morceau = propre[debut:i].strip()
                if morceau and not morceau.startswith("@"):
                    ligne = propre.count("\n", 0, i) + 1
                    trouves.append((morceau, ligne))
            profondeur += 1
        elif caractere == "}":
            profondeur = max(0, profondeur - 1)
            if profondeur == 0:
                debut = i + 1
        elif caractere == ";" and profondeur == 0:
            # Fin d'une at-règle sans bloc (`@import`, `@charset`).
            debut = i + 1
        morceau_debut = i
    del morceau_debut
    return trouves


def classes_de_feuille(racine: Path) -> tuple[dict[str, int], list[str]]:
    """Classe -> première ligne où elle apparaît comme sélecteur, et les feuilles lues."""
    classes: dict[str, int] = {}
    feuilles: list[str] = []
    for nom in FEUILLES:
        chemin = racine / nom
        if not chemin.is_file():
            continue
        feuilles.append(nom)
        for selecteur, ligne in selecteurs_de(chemin.read_text(encoding="utf-8")):
            for trouve in CLASSE.finditer(selecteur):
                classes.setdefault(trouve.group(1), ligne)
    return classes, feuilles


def sources(racine: Path) -> list[Path]:
    """Les fichiers qui peuvent produire une instance de classe."""
    fichiers: list[Path] = []
    soi_meme = Path(__file__).resolve()
    for chemin in racine.rglob("*"):
        if not chemin.is_file():
            continue
        # L'outil et ses bancs se retirent de leur propre corpus : ils citent
        # les noms qu'ils cherchent et se compteraient comme une instance de
        # chacun d'eux. Un banc ne rend aucune page : cité, un nom n'y est pas
        # employé.
        if chemin.resolve() == soi_meme or chemin.name.startswith(("test_", "__")):
            continue
        if any(partie in EXCLUS for partie in chemin.relative_to(racine).parts):
            continue
        if chemin.suffix.lower() in EXTENSIONS:
            fichiers.append(chemin)
    return sorted(fichiers)


def lire(fichiers: list[Path]) -> tuple[str, list[str]]:
    """Le corpus concaténé, et les fichiers qu'on n'a pas pu lire (ils sont nommés)."""
    morceaux: list[str] = []
    illisibles: list[str] = []
    for chemin in fichiers:
        try:
            morceaux.append(chemin.read_text(encoding="utf-8", errors="strict"))
        except (UnicodeDecodeError, OSError):
            illisibles.append(str(chemin))
    return "\n".join(morceaux), illisibles


def prefixes_dynamiques(corpus: str) -> set[str]:
    """Les préfixes de classe qu'une source complète à l'exécution."""
    prefixes: set[str] = set()
    for motif in DYNAMIQUES:
        for trouve in motif.finditer(corpus):
            prefixes.add(trouve.group(1).rstrip("-") + "-")
    return prefixes


def verdicts(racine: Path) -> dict:
    """Le relevé complet, sans conclusion cachée."""
    classes, feuilles = classes_de_feuille(racine)
    fichiers = sources(racine)
    corpus, illisibles = lire(fichiers)
    prefixes = prefixes_dynamiques(corpus) if corpus else set()
    # Un préfixe n'excuse que les classes qui existent dans la feuille : sans ce
    # filtre, un fragment de phrase (« est-à- ») passerait pour un préfixe.
    prefixes = {p for p in prefixes if any(c.startswith(p) for c in classes)}
    lues, dynamiques, mortes = [], [], []
    for classe in sorted(classes):
        if classe in corpus:
            lues.append(classe)
        elif any(classe.startswith(prefixe) for prefixe in prefixes):
            dynamiques.append(classe)
        else:
            mortes.append(classe)
    return {
        "classes": classes,
        "feuilles": feuilles,
        "fichiers": fichiers,
        "illisibles": illisibles,
        "prefixes": prefixes,
        "lues": lues,
        "dynamiques": dynamiques,
        "mortes": mortes,
    }


def principal(arguments: list[str] | None = None) -> int:
    analyseur = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    analyseur.add_argument("--verifier", action="store_true", help="code 1 si une classe est morte")
    analyseur.add_argument("--liste", action="store_true", help="un nom mort par ligne, sans commentaire")
    options = analyseur.parse_args(arguments)

    releve = verdicts(RACINE)
    if not releve["feuilles"]:
        print(f"illisible : aucune feuille attendue n'existe ({', '.join(FEUILLES)})", file=sys.stderr)
        return 2
    if len(releve["fichiers"]) < SOURCES_MINIMALES:
        print(
            f"illisible : {len(releve['fichiers'])} source(s) lue(s), moins que les "
            f"{SOURCES_MINIMALES} nécessaires pour croire un verdict « morte »",
            file=sys.stderr,
        )
        return 2
    if releve["illisibles"]:
        print(
            "illisible : " + str(len(releve["illisibles"])) + " source(s) n'ont pas pu être lues ("
            + ", ".join(releve["illisibles"][:3]) + ") — un nom qui s'y trouve serait dit mort",
            file=sys.stderr,
        )
        return 2

    if options.liste:
        for classe in releve["mortes"]:
            print(classe)
        return 1 if releve["mortes"] else 0

    print(
        f"{len(releve['classes'])} classe(s) dans {', '.join(releve['feuilles'])} : "
        f"{len(releve['lues'])} lue(s) dans {len(releve['fichiers'])} source(s), "
        f"{len(releve['dynamiques'])} construite(s) à l'exécution, "
        f"{len(releve['mortes'])} morte(s)."
    )
    if releve["dynamiques"]:
        print(
            "  construites à l'exécution, donc indécidables ici : "
            + ", ".join(releve["dynamiques"]) + " (préfixes : "
            + ", ".join(sorted(releve["prefixes"])) + ")"
        )
    for classe in releve["mortes"]:
        print(f"  morte  .{classe}  (feuille, ligne {releve['classes'][classe]})")
    if releve["mortes"]:
        print(
            "Une classe morte n'est pas une faute en soi : c'est une règle qu'aucune page "
            "n'ouvre. Le refus ci-dessous dit seulement qu'on ne peut plus prétendre la "
            "mesurer dans un navigateur."
        )
        return 1 if options.verifier else 0
    print("Aucune classe morte : chaque sélecteur de la feuille a une instance ou une construction lisible.")
    return 0


if __name__ == "__main__":
    sys.exit(principal())
