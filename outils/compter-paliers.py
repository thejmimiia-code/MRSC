#!/usr/bin/env python3
"""Compte les valeurs fixes d'affichage et refuse les paliers non déclarés.

Le 30 octobre 2026, une règle a été écrite dans le journal : l'agencement ne
doit plus reposer sur des **valeurs fixes de fenêtre**, parce que personne ne
travaille en plein écran et que chacun module sa fenêtre. Une règle pareille
n'a de valeur que si elle est **comptée** : une feuille de style gagne des
paliers un par un, sans que personne ne décide de l'ensemble. Ce contrôle rend
la dette visible et rend son augmentation impossible à faire passer en silence.

Ce qu'il fait, et rien de plus :

1. il lit `assets/css/site.css` et relève chaque bloc `@media` ;
2. il **canonise** la condition — espaces après les deux-points, virgules — et
   refuse deux écritures de la même condition, qui feraient mentir le comptage ;
3. il classe chaque condition : `format` quand elle dépend de la taille de la
   fenêtre (largeur, hauteur, orientation), `preference` quand elle dépend d'un
   réglage de la personne ou du média d'impression ;
4. il confronte chaque condition `format` à son inscription dans
   `docs/rd/paliers-affichage.toml` : une raison écrite, une décision
   (`dette` ou `assume`), un compte exact.

Il ne juge pas les raisons. Il exige qu'elles existent, qu'elles dépassent une
phrase creuse, et que le compte colle — parce qu'un palier ajouté, c'est un
écran de plus que le site présume.

**Il ne lit pas ce qu'il ne peut pas lire en silence.** Une feuille absente, des
accolades déséquilibrées, un registre illisible : code 2 et un message qui dit
quelle source manque. Un contrôle qui n'a pas pu compter n'a pas le droit
d'annoncer que tout va bien.

Usage :
    python3 outils/compter-paliers.py              # vérifie et compte
    python3 outils/compter-paliers.py --releve     # imprime le relevé détaillé
    python3 outils/compter-paliers.py --mettre-a-jour
        # reporte les comptes du CSS dans le registre et ajoute les paliers
        # inconnus **avec une raison vide** : la vérification échoue ensuite
        # tant qu'un humain n'a pas écrit pourquoi ce palier existe.
"""

from __future__ import annotations

import argparse
import os
import re
import sys
import tomllib
from pathlib import Path

#: Racine lue par le contrôle. La surcharge sert au banc
#: (`outils/test_paliers_affichage.py`), qui casse une copie du dépôt.
RACINE = Path(os.environ.get("MRSC_RACINE") or Path(__file__).resolve().parent.parent).resolve()
FEUILLE = Path("assets/css/site.css")
REGISTRE = Path("docs/rd/paliers-affichage.toml")

#: Longueur en dessous de laquelle une raison est une formule creuse.
RAISON_MINIMALE = 40

DECISIONS = ("dette", "assume")

#: Mots qui trahissent une raison laissée en attente.
ATTENTES = ("à compléter", "a completer", "todo", "à faire", "a faire", "xxx")

#: Marqueurs d'une condition qui dépend de la géométrie de la fenêtre.
MARQUEURS_FORMAT = ("width", "height", "orientation", "aspect-ratio")

#: Marqueurs d'une condition qui dépend d'un réglage de la personne.
MARQUEURS_PREFERENCE = (
    "prefers-",
    "forced-colors",
    "any-pointer",
    "hover",
    "pointer",
    "resolution",
    "print",
    "scan",
    "color-gamut",
    "update",
)


class SourceIllisible(Exception):
    """Une source indispensable n'a pas pu être lue. Code de sortie 2."""


def canoniser(condition: str) -> str:
    """Écriture unique d'une condition : `(max-width:760px)` devient `(max-width: 760px)`.

    Sans cette fonction, la même condition écrite deux fois de deux façons
    compte pour deux paliers distincts et le relevé ment. Trouvé le 31 octobre
    2026 : la feuille contenait `(max-width:760px)` et `(forced-colors:active)`
    à côté de leurs jumelles espacées.
    """
    texte = " ".join(condition.split())
    texte = re.sub(
        r"\(\s*([a-zA-Z-]+)\s*:\s*([^()]+?)\s*\)",
        lambda trouve: f"({trouve.group(1)}: {trouve.group(2)})",
        texte,
    )
    texte = re.sub(r"\s*,\s*", ", ", texte)
    return texte.strip()


def classer(condition: str) -> str:
    """`format`, `preference` ou `autre` — selon ce dont la condition dépend."""
    if any(marqueur in condition for marqueur in MARQUEURS_FORMAT):
        return "format"
    if any(marqueur in condition for marqueur in MARQUEURS_PREFERENCE):
        return "preference"
    return "autre"


def lire_feuille(racine: Path) -> str:
    chemin = racine / FEUILLE
    if not chemin.is_file():
        raise SourceIllisible(f"feuille de style introuvable : {FEUILLE}")
    try:
        return chemin.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as erreur:
        raise SourceIllisible(f"feuille de style illisible : {FEUILLE} ({erreur})") from erreur


def etendue(texte: str, ouvrante: int) -> int:
    """Position de l'accolade fermante qui correspond à celle-ci, accolades comptées.

    Une feuille tronquée rendrait `-1` : c'est une source illisible, pas une
    mesure. La compter vaut mieux que la deviner.
    """
    profondeur = 0
    for position in range(ouvrante, len(texte)):
        if texte[position] == "{":
            profondeur += 1
        elif texte[position] == "}":
            profondeur -= 1
            if profondeur == 0:
                return position
    return -1


def compter_regles(bloc: str) -> int:
    """Nombre de règles de style écrites directement dans un bloc `@media`.

    Le 31 octobre 2026, ce comptage a été ajouté parce que la dette ne bougeait
    plus : douze grilles venaient de quitter leurs paliers et le relevé
    annonçait toujours 41 blocs. Il comptait les **blocs** `@media`, pas ce
    qu'ils décident — un bloc qui ne garde qu'une règle sans rapport avec la
    largeur continuait de peser autant qu'un bloc qui en porte dix.
    """
    profondeur, regles, position = 0, 0, 0
    while position < len(bloc):
        caractere = bloc[position]
        if caractere == "{":
            profondeur += 1
            if profondeur == 1:
                entete = bloc[:position].rstrip().rsplit("}", 1)[-1].strip()
                if entete and not entete.startswith("@"):
                    regles += 1
        elif caractere == "}":
            profondeur -= 1
        position += 1
    return regles


def relever(texte: str) -> list[dict[str, object]]:
    """Toutes les conditions `@media`, avec leur écriture d'origine et leur ligne.

    Les accolades sont équilibrées avant toute chose : une feuille tronquée
    donnerait un relevé partiel, c'est-à-dire plus faux qu'aucun relevé.
    """
    sans_commentaires = re.sub(r"/\*.*?\*/", lambda trouve: "\n" * trouve.group(0).count("\n"), texte, flags=re.S)
    if sans_commentaires.count("{") != sans_commentaires.count("}"):
        raise SourceIllisible(
            "accolades déséquilibrées dans "
            f"{FEUILLE} : {sans_commentaires.count('{')} ouvrantes, "
            f"{sans_commentaires.count('}')} fermantes — le relevé serait partiel"
        )
    conditions = []
    for trouve in re.finditer(r"@media\s*([^{]+)\{", sans_commentaires):
        brute = " ".join(trouve.group(1).split())
        ouvrante = trouve.end() - 1
        fermante = etendue(sans_commentaires, ouvrante)
        if fermante == -1:
            raise SourceIllisible(
                f"bloc @media jamais refermé ligne {sans_commentaires[: trouve.start()].count(chr(10)) + 1}"
                f" ({brute}) — le relevé s'arrêterait là sans le dire"
            )
        conditions.append(
            {
                "brute": brute,
                "canonique": canoniser(brute),
                "ligne": sans_commentaires[: trouve.start()].count("\n") + 1,
                "classe": classer(canoniser(brute)),
                "regles": compter_regles(sans_commentaires[ouvrante + 1 : fermante]),
            }
        )
    return conditions


def lire_registre(racine: Path) -> dict:
    chemin = racine / REGISTRE
    if not chemin.is_file():
        raise SourceIllisible(f"registre des paliers introuvable : {REGISTRE}")
    try:
        return tomllib.loads(chemin.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, tomllib.TOMLDecodeError) as erreur:
        raise SourceIllisible(f"registre des paliers illisible : {REGISTRE} ({erreur})") from erreur


def inscrire(registre: dict) -> dict[str, dict]:
    """Indexe les inscriptions par condition canonisée."""
    index = {}
    for entree in registre.get("condition", []):
        if "condition" not in entree:
            raise SourceIllisible("registre des paliers : une entrée [[condition]] n'a pas de champ `condition`")
        index[canoniser(str(entree["condition"]))] = entree
    return index


def controler(conditions: list[dict[str, object]], registre: dict) -> tuple[list[str], dict[str, object]]:
    """Compare le relevé aux inscriptions. Rend les erreurs et le bilan chiffré."""
    erreurs: list[str] = []
    index = inscrire(registre)

    comptes: dict[str, int] = {}
    regles: dict[str, int] = {}
    lignes: dict[str, list[int]] = {}
    ecritures: dict[str, set[str]] = {}
    classes: dict[str, str] = {}
    for condition in conditions:
        canonique = str(condition["canonique"])
        comptes[canonique] = comptes.get(canonique, 0) + 1
        regles[canonique] = regles.get(canonique, 0) + int(condition.get("regles", 0))
        lignes.setdefault(canonique, []).append(int(condition["ligne"]))
        ecritures.setdefault(canonique, set()).add(str(condition["brute"]))
        classes[canonique] = str(condition["classe"])

    for canonique, variantes in ecritures.items():
        if len(variantes) > 1:
            liste = " · ".join(sorted(f"« {variante} »" for variante in variantes))
            erreurs.append(
                f"{canonique} : deux écritures de la même condition ({liste}) — "
                "elles compteraient pour deux paliers, réécrivez l'écart"
            )
        elif canonique not in variantes:
            erreurs.append(
                f"« {next(iter(variantes))} » : écriture non canonique, à réécrire « {canonique} »"
            )

    for canonique, nombre in sorted(comptes.items()):
        entree = index.get(canonique)
        if entree is None:
            if classes[canonique] == "format":
                erreurs.append(
                    f"palier non déclaré : {canonique} — {nombre} bloc(s), ligne(s) "
                    f"{', '.join(str(ligne) for ligne in lignes[canonique])}. "
                    f"Ajoutez [[condition]] dans {REGISTRE} avec la raison de ce palier "
                    "et la décision « dette » ou « assume »."
                )
            continue
        declaree = str(entree.get("classe", "")).strip()
        if declaree and declaree != classes[canonique]:
            erreurs.append(
                f"{canonique} : classée « {declaree} » dans le registre, mais le CSS en fait "
                f"un palier de « {classes[canonique]} »"
            )
        raison = str(entree.get("presume", "")).strip()
        if not raison:
            erreurs.append(f"{canonique} : la raison est vide — un palier sans raison est une habitude")
        elif len(raison) < RAISON_MINIMALE:
            erreurs.append(
                f"{canonique} : raison trop courte ({len(raison)} caractères, {RAISON_MINIMALE} demandés)"
            )
        elif any(attente in raison.lower() for attente in ATTENTES):
            erreurs.append(f"{canonique} : la raison annonce encore un travail à faire (« {raison[:60]} »)")
        decision = str(entree.get("decision", "")).strip()
        if decision not in DECISIONS:
            erreurs.append(
                f"{canonique} : décision « {decision or 'absente'} » inconnue (attendu : dette ou assume)"
            )
        declare_regles = entree.get("regles")
        if isinstance(declare_regles, int):
            delta = regles[canonique] - declare_regles
            if delta > 0:
                erreurs.append(
                    f"{canonique} : {regles[canonique]} règles dans la feuille, {declare_regles} "
                    f"déclarées — la dette a augmenté de {delta} règle(s) qui dépendent d'une largeur"
                )
            elif delta < 0:
                erreurs.append(
                    f"{canonique} : {regles[canonique]} règles, {declare_regles} déclarées — "
                    "la dette a diminué, c'est une avancée : mettez le registre à jour et datez-la"
                )
        declare = entree.get("occurrences")
        if not isinstance(declare, int):
            erreurs.append(f"{canonique} : le champ `occurrences` n'est pas un entier")
        elif nombre > declare:
            erreurs.append(
                f"{canonique} : {nombre} blocs dans la feuille, {declare} déclarés — "
                "la dette a augmenté ; un palier de plus est un écran de plus que le site présume"
            )
        elif nombre < declare:
            erreurs.append(
                f"{canonique} : {nombre} blocs, {declare} déclarés — la dette a diminué, "
                "c'est une avancée : mettez le registre à jour (--mettre-a-jour) et datez-la"
            )

    for canonique, entree in index.items():
        if canonique in comptes:
            continue
        if entree.get("classe") == "preference":
            continue
        erreurs.append(
            f"{canonique} : déclaré dans le registre mais absent de la feuille — "
            "une inscription orpheline finit par couvrir un palier qui n'existe plus"
        )

    bilan = {
        "conditions": len(comptes),
        "blocs": sum(comptes.values()),
        "regles": sum(regles.values()),
        "comptes": comptes,
        "comptes_regles": regles,
        "lignes": lignes,
        "classes": classes,
        "inscriptions": index,
    }
    return erreurs, bilan


def bilan_par_classe(bilan: dict[str, object]) -> dict[str, dict[str, int]]:
    par_classe: dict[str, dict[str, int]] = {}
    comptes = bilan["comptes"]
    classes = bilan["classes"]
    for canonique, nombre in comptes.items():  # type: ignore[union-attr]
        classe = classes[canonique]  # type: ignore[index]
        seau = par_classe.setdefault(classe, {"conditions": 0, "blocs": 0})
        seau["conditions"] += 1
        seau["blocs"] += nombre  # type: ignore[operator]
    return par_classe


def releve(registre: dict, bilan: dict[str, object]) -> str:
    """Le relevé lisible : ce que le site présume, et combien cela coûte."""
    date = registre.get("releve", {}).get("date", "date non inscrite")
    par_classe = bilan_par_classe(bilan)
    index = bilan["inscriptions"]
    decisions = {"dette": 0, "assume": 0}
    for canonique, entree in index.items():  # type: ignore[union-attr]
        if canonique in bilan["comptes"] and entree.get("classe") == "format":  # type: ignore[operator]
            decisions[str(entree.get("decision", ""))] = decisions.get(str(entree.get("decision", "")), 0) + 1

    lignes = [
        f"Paliers d'affichage — relevé du {date}",
        f"{bilan['conditions']} conditions distinctes, {bilan['blocs']} blocs @media, "
        f"{bilan['regles']} règles dans {FEUILLE}",
    ]
    for classe, ordre in (("format", "format (taille de fenêtre)"), ("preference", "préférence (réglage de la personne)"), ("autre", "autre")):
        if classe in par_classe:
            seau = par_classe[classe]
            lignes.append(f"  {ordre} : {seau['conditions']} conditions, {seau['blocs']} blocs")
    lignes.append(
        f"Dette de format : {decisions.get('dette', 0)} paliers en dette, "
        f"{decisions.get('assume', 0)} assumés avec leur raison"
    )
    plus_frequent = sorted(bilan["comptes"].items(), key=lambda paire: (-paire[1], paire[0]))[:5]  # type: ignore[union-attr]
    lignes.append("Les plus employés : " + " · ".join(f"{condition} ({nombre})" for condition, nombre in plus_frequent))
    plus_etroit = sorted(
        condition
        for condition in bilan["comptes"]  # type: ignore[union-attr]
        if bilan["classes"][condition] == "format" and "max-width" in condition  # type: ignore[index]
    )
    if plus_etroit:
        lignes.append("Paliers de largeur maximale : " + " · ".join(plus_etroit))
    return "\n".join(lignes)


def mettre_a_jour(racine: Path, conditions: list[dict[str, object]]) -> list[str]:
    """Reporte les comptes et ajoute les paliers inconnus, raison vide comprise.

    Une raison vide n'est pas un oubli du script : c'est le résultat voulu. Le
    script ne peut pas inventer pourquoi un palier existe ; il peut seulement
    refuser de laisser passer celui dont personne n'a écrit la raison.
    """
    chemin = racine / REGISTRE
    if not chemin.is_file():
        raise SourceIllisible(f"registre des paliers introuvable : {REGISTRE}")
    # Une écriture ne sort jamais de la racine qu'on a reçu l'ordre de lire. Le
    # 31 octobre 2026, un banc a écrit dans le vrai registre par un lien
    # symbolique : la copie était fidèle, le lien ne l'était pas.
    if not chemin.resolve().is_relative_to(racine.resolve()):
        raise SourceIllisible(
            f"le registre {REGISTRE} pointe hors de la racine lue ({chemin.resolve()}) — "
            "refus d'écrire à travers un lien"
        )
    texte = chemin.read_text(encoding="utf-8")
    comptes: dict[str, int] = {}
    regles: dict[str, int] = {}
    for condition in conditions:
        canonique = str(condition["canonique"])
        comptes[canonique] = comptes.get(canonique, 0) + 1
        regles[canonique] = regles.get(canonique, 0) + int(condition.get("regles", 0))

    sorties: list[str] = []
    courant: str | None = None
    for ligne in texte.splitlines():
        trouve = re.match(r'^condition\s*=\s*"(.+)"\s*$', ligne)
        if trouve:
            courant = canoniser(trouve.group(1))
            sorties.append(ligne)
            continue
        compte = re.match(r"^(occurrences\s*=\s*)(\d+)(\s*)$", ligne)
        if compte and courant and courant in comptes:
            if str(comptes[courant]) != compte.group(2):
                sorties.append(f"{compte.group(1)}{comptes[courant]}{compte.group(3)}")
                continue
        nombre_regles = re.match(r"^(regles\s*=\s*)(\d+)(\s*)$", ligne)
        if nombre_regles and courant and courant in regles:
            if str(regles[courant]) != nombre_regles.group(2):
                sorties.append(f"{nombre_regles.group(1)}{regles[courant]}{nombre_regles.group(3)}")
                continue
        sorties.append(ligne)

    ajoutes = []
    connues = set(inscrire(lire_registre(racine)))
    for canonique in sorted(comptes):
        if canonique in connues or classer(canonique) != "format":
            continue
        sorties.extend(
            [
                "",
                "[[condition]]",
                f'condition = "{canonique}"',
                'classe = "format"',
                f"occurrences = {comptes[canonique]}",
                f"regles = {regles[canonique]}",
                'presume = ""',
                'decision = "dette"',
            ]
        )
        ajoutes.append(canonique)

    chemin.write_text("\n".join(sorties) + "\n", encoding="utf-8")
    return ajoutes


def principal(arguments: list[str] | None = None) -> int:
    analyseur = argparse.ArgumentParser(
        description="Compte les paliers d'affichage et refuse ceux que personne n'a déclarés.",
    )
    analyseur.add_argument("--releve", action="store_true", help="imprime le relevé détaillé avant de vérifier")
    analyseur.add_argument(
        "--mettre-a-jour",
        action="store_true",
        help="reporte les comptes du CSS dans le registre et ajoute les paliers inconnus, raison vide",
    )
    options = analyseur.parse_args(arguments)

    try:
        conditions = relever(lire_feuille(RACINE))
        if options.mettre_a_jour:
            ajoutes = mettre_a_jour(RACINE, conditions)
            for canonique in ajoutes:
                print(f"palier ajouté au registre, raison à écrire : {canonique}", file=sys.stderr)
        registre = lire_registre(RACINE)
        erreurs, bilan = controler(conditions, registre)
    except SourceIllisible as erreur:
        print(f"Impossible de compter les paliers : {erreur}", file=sys.stderr)
        return 2

    if options.releve:
        print(releve(registre, bilan))

    if erreurs:
        for erreur in erreurs:
            print(f"  - {erreur}", file=sys.stderr)
        print(
            f"Refusé : {len(erreurs)} écart(s) entre la feuille et le registre des paliers "
            f"({REGISTRE}).",
            file=sys.stderr,
        )
        return 1

    par_classe = bilan_par_classe(bilan)
    format_ = par_classe.get("format", {"conditions": 0, "blocs": 0})
    regles_format = sum(
        bilan["comptes_regles"][condition]
        for condition in bilan["comptes"]
        if bilan["classes"][condition] == "format"
    )
    print(
        f"Paliers déclarés : {format_['conditions']} conditions de format, {format_['blocs']} blocs, "
        f"{regles_format} règles, chacune avec sa raison et sa décision · "
        f"{bilan['conditions'] - format_['conditions']} conditions de préférence ou autres, "
        "qui ne présument aucune taille d'écran."
    )
    return 0


if __name__ == "__main__":
    sys.exit(principal())
