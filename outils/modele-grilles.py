#!/usr/bin/env python3
"""Mesure ce que les grilles décident, au lieu de le présumer par un palier.

La règle du 30 octobre 2026 dit : l'agencement suit l'espace disponible, pas une
largeur d'écran supposée. Ce script la rend **calculable** sur les grilles.

Il lit `assets/css/site.css`, reconstitue pour un sélecteur donné la cascade
réelle de `grid-template-columns` — règle de base, puis chaque bloc `@media` qui
la reprend, appliqué dans l'ordre du fichier — et calcule le nombre de colonnes
obtenu à chaque largeur de fenêtre. Il fait la même chose pour une grille
convertie en `repeat(auto-fit, minmax(min(Npx, 100%), 1fr))`, où le nombre de
colonnes ne dépend plus que du conteneur :

    colonnes(W) = max(1, floor((C(W) + g) / (N + g)))

avec `C(W) = min(--content, W - 3rem)` — la largeur du conteneur, telle que la
feuille la définit. Ce n'est pas une approximation du navigateur : c'est
l'arithmétique exacte de `auto-fit` sans élément orphelin, et c'est le modèle le
plus favorable à l'ancienne règle, puisqu'il ignore ses sauts.

Ce que le script cherche, pour chaque grille : le plus petit `N` qui **colle le
mieux** à l'ancienne cascade, et l'écart exact qui reste. Un écart nul veut dire
que le palier peut disparaître sans que rien ne change à l'écran ; un écart
borné, que la grille change de façon continue là où elle sautait.

Usage :
    python3 outils/modele-grilles.py                     # état de toutes les grilles
    python3 outils/modele-grilles.py --grille .principle-grid
    python3 outils/modele-grilles.py --grille .principle-grid --minimum 260
    python3 outils/modele-grilles.py --json

Il ne remplace pas un navigateur : il ne dit rien d'une carte trop étroite pour
son contenu, d'un texte qui déborde, ni des grilles dont la largeur ne vient pas
de `.container`. Il dit ce que les règles **prescrivent**, largeur par largeur.
"""

from __future__ import annotations

import argparse
import json
import math
import os
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

RACINE = Path(os.environ.get("MRSC_RACINE") or Path(__file__).resolve().parent.parent).resolve()
FEUILLE = Path("assets/css/site.css")

#: Largeurs de fenêtre balayées, de la plus étroite tenable au grand écran.
LARGEURS = list(range(240, 2561, 10))

#: Largeur du conteneur : `width: min(var(--content), calc(100% - 3rem))`.
#: `--content` vaut 1160 px par défaut ; les présentations le changent (940,
#: 1240, 1380, 1480) et ce script ne mesure que la présentation par défaut.
CONTENU_DEFAUT = 1160
GARNITURE_LATERALE = 48  # 3rem

#: Largeur de carte en dessous de laquelle une grille tasse son contenu.
CARTE_MINIMALE = 220

#: Planchers candidats pour `minmax(min(Npx, 100%), 1fr)`, par pas de 10 px.
CANDIDATS = list(range(180, 481, 10))

MEDIA_LARGEUR = re.compile(r"\((min|max)-width\s*:\s*(\d+)px\s*\)")
#: Les quatre écritures que la feuille emploie réellement. Une colonne unique
#: (`minmax(0, 1fr)`) compte : c'est le repli que les paliers imposent partout,
#: et l'ignorer faisait croire à une cascade plus haute qu'elle n'est — mesuré
#: le 31 octobre 2026, le modèle annonçait deux colonnes à 240 px là où la
#: feuille n'en donnait qu'une.
DECLARATION_GRILLE = re.compile(
    r"grid-template-columns\s*:\s*(repeat\(\s*(\d+)\s*,\s*minmax\([^)]*\)\s*\)|"
    r"repeat\(\s*auto-fit\s*,\s*minmax\(\s*min\((\d+)px\s*,?\s*100%\)\s*,\s*1fr\s*\)\s*\)|"
    r"repeat\(\s*auto-fit\s*,\s*minmax\(\s*(\d+)px\s*,\s*1fr\s*\)\s*\)|"
    r"minmax\(\s*0\s*,\s*1fr\s*\)(?!\s*\))"
    r")"
)


@dataclass
class Regle:
    """Une déclaration de colonnes, avec la condition de largeur qui la porte."""

    selecteurs: list[str]
    valeur: str
    colonnes: int | None
    minimum: int | None
    largeur_max: int | None
    largeur_min: int | None
    ligne: int
    ordre: int


@dataclass
class Grille:
    """Ce qu'une grille décide, et à partir de quoi."""

    selecteur: str
    colonnes_base: int = 0
    gap: float = 16.0
    regles: list[Regle] = field(default_factory=list)
    source: str = ""


def sans_commentaires(texte: str) -> str:
    """Remplace chaque commentaire par ses sauts de ligne, pour garder les numéros."""
    return re.sub(r"/\*.*?\*/", lambda trouve: "\n" * trouve.group(0).count("\n"), texte, flags=re.S)


def decouper(texte: str) -> list[tuple[list[str], str, int | None, int | None, int]]:
    """Rend (sélecteurs, corps, largeur max, largeur min, ligne) pour chaque règle.

    Un analyseur volontairement pauvre : deux niveaux (`@media` et règle), pas de
    `@supports`, pas d'imbrication. Il doit être capable de dire « je ne sais pas
    lire ça » plutôt que de sauter une règle en silence.
    """
    regles = []
    pile_media: list[tuple[int | None, int | None]] = []
    i, n = 0, len(texte)
    while i < n:
        ouvrante = texte.find("{", i)
        if ouvrante == -1:
            break
        entete = texte[i:ouvrante]
        ligne = texte[:i].count("\n") + 1 + entete.count("\n")
        # Une liste de sélecteurs peut s'écrire sur plusieurs lignes : la réduire
        # à sa dernière ligne perdait `.ai-metric-grid,` et le modèle ignorait
        # alors la moitié des règles. Trouvé le 31 octobre 2026 en comparant le
        # nombre de règles lues aux sélecteurs présents dans la feuille.
        entete_nu = " ".join(entete.split())
        if entete_nu.startswith("@media"):
            bornes = MEDIA_LARGEUR.findall(entete_nu)
            largeur_max = next((int(v) for c, v in bornes if c == "max"), None)
            largeur_min = next((int(v) for c, v in bornes if c == "min"), None)
            if not bornes and ("orientation" in entete_nu or "height" in entete_nu):
                # Une condition de hauteur ne se ramène pas à une largeur : la
                # dire, plutôt que de la traiter comme vraie ou fausse.
                raise SystemExit(
                    f"condition non largeur rencontrée ligne {ligne} : {entete_nu} — "
                    "ce modèle ne sait pas la placer sur un axe de largeur"
                )
            pile_media.append((largeur_max, largeur_min))
            i = ouvrante + 1
            continue
        if entete_nu.startswith("@"):
            i = ouvrante + 1
            continue
        # Règle ordinaire : trouver sa fermeture.
        profondeur, j = 0, ouvrante
        while j < n:
            if texte[j] == "{":
                profondeur += 1
            elif texte[j] == "}":
                profondeur -= 1
                if profondeur == 0:
                    break
            j += 1
        corps = texte[ouvrante + 1 : j]
        largeur_max, largeur_min = pile_media[-1] if pile_media else (None, None)
        selecteurs = [s.strip() for s in re.split(r",(?![^(]*\))", entete_nu) if s.strip()]
        regles.append((selecteurs, corps, largeur_max, largeur_min, ligne))
        i = j + 1
        # Refermer les blocs `@media` traversés : on avance jusqu'au `}` qui suit.
        while i < n and texte[i:].lstrip().startswith("}"):
            i = texte.index("}", i) + 1
            if pile_media:
                pile_media.pop()
    return regles


def lire_grilles(texte: str) -> dict[str, Grille]:
    """Toutes les grilles dont la feuille fixe ou calcule le nombre de colonnes."""
    texte = sans_commentaires(texte)
    grilles: dict[str, Grille] = {}
    for ordre, (selecteurs, corps, largeur_max, largeur_min, ligne) in enumerate(decouper(texte)):
        trouve = DECLARATION_GRILLE.search(corps)
        if not trouve:
            continue
        valeur = " ".join(trouve.group(1).split())
        colonnes = int(trouve.group(2)) if trouve.group(2) else (1 if trouve.group(0).startswith("grid-template-columns: minmax") or trouve.group(0).startswith("grid-template-columns:minmax") else None)
        minimum = int(trouve.group(3) or trouve.group(4)) if (trouve.group(3) or trouve.group(4)) else None
        gap = re.search(r"(?:^|;)\s*gap\s*:\s*([\d.]+)rem", corps)
        for selecteur in selecteurs:
            grille = grilles.setdefault(selecteur, Grille(selecteur=selecteur, source=f"site.css:{ligne}"))
            if gap:
                grille.gap = round(float(gap.group(1)) * 16, 2)
            regle = Regle(
                selecteurs=selecteurs,
                valeur=valeur,
                colonnes=colonnes,
                minimum=minimum,
                largeur_max=largeur_max,
                largeur_min=largeur_min,
                ligne=ligne,
                ordre=ordre,
            )
            grille.regles.append(regle)
            if largeur_max is None and largeur_min is None and colonnes:
                grille.colonnes_base = colonnes
    return grilles


def conteneur(largeur: int, contenu: int = CONTENU_DEFAUT) -> float:
    return min(contenu, largeur - GARNITURE_LATERALE)


def applique(regle: Regle, largeur: int) -> bool:
    if regle.largeur_max is not None and largeur > regle.largeur_max:
        return False
    if regle.largeur_min is not None and largeur < regle.largeur_min:
        return False
    return True


def colonnes_anciennes(grille: Grille, largeur: int) -> int:
    """Colonnes prescrites par la feuille actuelle, à cette largeur."""
    resultat = grille.colonnes_base or 1
    for regle in sorted(grille.regles, key=lambda r: r.ordre):
        if applique(regle, largeur):
            if regle.minimum:
                return auto_fit(regle.minimum, grille.gap, largeur)
            if regle.colonnes:
                resultat = regle.colonnes
    return resultat


def auto_fit(minimum: int, gap: float, largeur: int) -> int:
    """Colonnes que `repeat(auto-fit, minmax(min(Npx,100%), 1fr))` produit."""
    place = conteneur(largeur)
    return max(1, math.floor((place + gap) / (minimum + gap)))


def ecart(grille: Grille, minimum: int) -> tuple[int, int, list[tuple[int, int, int]]]:
    """(nombre d'écarts, écart maximal, écarts détaillés) entre ancienne et nouvelle règle."""
    details = []
    for largeur in LARGEURS:
        ancienne = colonnes_anciennes(grille, largeur)
        nouvelle = auto_fit(minimum, grille.gap, largeur)
        if ancienne != nouvelle:
            details.append((largeur, ancienne, nouvelle))
    maximal = max((abs(a - n) for _, a, n in details), default=0)
    return len(details), maximal, details


def meilleur_minimum(grille: Grille) -> tuple[int, int, int, list[tuple[int, int, int]]]:
    """Le plus petit `N` qui colle le mieux, à écart égal tranché par la plus petite carte pleine."""
    classement = []
    for minimum in CANDIDATS:
        nombre, maximal, details = ecart(grille, minimum)
        classement.append((nombre, maximal, minimum, details))
    nombre, maximal, minimum, details = min(classement, key=lambda c: (c[0], c[1], c[2]))
    return minimum, nombre, maximal, details


def carte_minimale(grille: Grille, minimum: int) -> float:
    """Largeur de carte la plus faible sur le balayage, pour la nouvelle règle."""
    return min(
        (conteneur(largeur) - (auto_fit(minimum, grille.gap, largeur) - 1) * grille.gap)
        / auto_fit(minimum, grille.gap, largeur)
        for largeur in LARGEURS
    )


def colonnes_de_conception(grille: Grille) -> int:
    """Le nombre de colonnes que la grille donne au conteneur maximal, quelle que soit l'écriture.

    Une grille écrite en `repeat(4, ...)` annonce 4 ; une grille convertie en
    `auto-fit` ne l'annonce nulle part et pourtant le donne : c'est la même
    intention, lue autrement. Sans cette fonction, une grille convertie
    apparaissait comme « 0 colonne » — le genre de rapport faux qui fait douter
    d'un contrôle juste.
    """
    if grille.colonnes_base:
        return grille.colonnes_base
    base = next((r for r in grille.regles if r.largeur_max is None and r.largeur_min is None), None)
    if base and base.minimum:
        # `auto_fit` attend une largeur de **fenêtre** : lui passer une largeur de
        # conteneur appliquait la soustraction deux fois (1112 au lieu de 1160),
        # et une grille de quatre colonnes s'annonçait à trois.
        return auto_fit(base.minimum, grille.gap, CONTENU_DEFAUT + GARNITURE_LATERALE)
    return 0


def minimum_pour_k(k: int, gap: float, contenu: float = CONTENU_DEFAUT) -> int | None:
    """Le plus large minimum de piste qui laisse encore `k` colonnes au conteneur maximal.

    Une grille de conception à `k` colonnes n'a pas besoin d'un palier pour
    retomber à `k-1` : il suffit que chaque piste réclame une largeur telle que
    `k` pistes ne tiennent plus quand le conteneur rétrécit. Choisir le minimum le
    plus **large** possible dans cette plage donne les cartes les plus lisibles,
    et fait tomber le nombre de colonnes exactement au moment où la largeur ne
    suffit plus — pas à une largeur ronde choisie d'avance.
    """
    valides = [n for n in CANDIDATS if auto_fit(n, gap, int(contenu) + GARNITURE_LATERALE) == k]
    return max(valides) if valides else None


def paliers(grille: Grille) -> list[str]:
    """Les conditions de largeur qui décident encore des colonnes de cette grille."""
    conditions = []
    for regle in grille.regles:
        if regle.largeur_max is None and regle.largeur_min is None:
            continue
        if regle.colonnes or regle.minimum:
            borne = (
                f"max-width: {regle.largeur_max}px"
                if regle.largeur_max is not None
                else f"min-width: {regle.largeur_min}px"
            )
            conditions.append(f"({borne}) → {regle.valeur}")
    return sorted(set(conditions))


def etat(grilles: dict[str, Grille]) -> list[dict]:
    """Le tableau : grille, colonnes de base, paliers restants, recommandation."""
    lignes = []
    for selecteur, grille in sorted(grilles.items()):
        if not colonnes_de_conception(grille):
            continue
        conditions = paliers(grille)
        entree = {
            "selecteur": selecteur,
            "colonnes": colonnes_de_conception(grille),
            "gap": grille.gap,
            "paliers": conditions,
            "source": grille.source,
        }
        if conditions:
            minimum, nombre, maximal, details = meilleur_minimum(grille)
            entree["minimum_recommande"] = minimum
            entree["ecarts"] = nombre
            entree["ecart_maximal"] = maximal
            entree["carte_minimale"] = round(carte_minimale(grille, minimum), 1)
        lignes.append(entree)
    return lignes


def rapport(lignes: list[dict]) -> str:
    avec = [ligne for ligne in lignes if ligne["paliers"]]
    sorties = [
        f"{len(lignes)} grilles fixent leur nombre de colonnes dans {FEUILLE} ; "
        f"{len(avec)} le font encore par un palier de largeur.",
        "",
    ]
    for ligne in avec:
        sorties.append(
            f"{ligne['selecteur']}  ({ligne['colonnes']} colonnes, gap {ligne['gap']:g}px) — {ligne['source']}"
        )
        for condition in ligne["paliers"]:
            sorties.append(f"    palier {condition}")
        sorties.append(
            f"    auto-fit à {ligne['minimum_recommande']}px : "
            f"{ligne['ecarts']} largeur(s) sur {len(LARGEURS)} diffèrent, "
            f"écart maximal {ligne['ecart_maximal']} colonne(s), "
            f"carte la plus étroite {ligne['carte_minimale']:g}px"
        )
    return "\n".join(sorties)


REGISTRE = Path("docs/rd/grilles-dynamiques.toml")


class SourceIllisible(Exception):
    """Une source indispensable n'a pas pu être lue. Code de sortie 2."""


def lire_registre(racine: Path) -> dict:
    import tomllib

    chemin = racine / REGISTRE
    if not chemin.is_file():
        raise SourceIllisible(f"registre des grilles introuvable : {REGISTRE}")
    try:
        return tomllib.loads(chemin.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, tomllib.TOMLDecodeError) as erreur:
        raise SourceIllisible(f"registre des grilles illisible : {REGISTRE} ({erreur})") from erreur


def verifier(grilles: dict[str, Grille], registre: dict) -> list[str]:
    """Chaque grille convertie doit rester dynamique, et son minimum doit être le calculé.

    Trois fautes possibles, et une seule suffit : la grille ne déclare plus
    `auto-fit`, son minimum n'est plus celui que la règle donne, ou un palier de
    largeur lui réimpose un nombre de colonnes. C'est la troisième qui guette :
    un correctif ajouté plus tard dans un `@media` annulerait la conversion sans
    que rien ne le dise.
    """
    erreurs: list[str] = []
    entrees = registre.get("grille", [])
    if not entrees:
        return [f"{REGISTRE} ne déclare aucune grille convertie — le registre ne prouve rien"]
    for entree in entrees:
        selecteur = entree.get("selecteur")
        if not selecteur or selecteur not in grilles:
            erreurs.append(f"{selecteur or '(sans sélecteur)'} : absent de {FEUILLE}")
            continue
        grille = grilles[selecteur]
        k = int(entree.get("colonnes", 0))
        declare = entree.get("minimum")
        attendu = minimum_pour_k(k, grille.gap) if k else None
        if attendu is None:
            erreurs.append(f"{selecteur} : aucune piste ne donne {k} colonnes au conteneur maximal")
            continue
        if declare != attendu:
            erreurs.append(
                f"{selecteur} : minimum déclaré {declare}px, la règle en donne {attendu}px "
                f"pour {k} colonnes et un écart de {grille.gap:g}px"
            )
        base = next(
            (r for r in grille.regles if r.largeur_max is None and r.largeur_min is None),
            None,
        )
        if base is None or base.minimum is None:
            erreurs.append(f"{selecteur} : sa règle de base ne déclare pas `auto-fit`")
        elif base.minimum != attendu:
            erreurs.append(
                f"{selecteur} : la feuille déclare `minmax(min({base.minimum}px, 100%), 1fr)`, "
                f"la règle demande {attendu}px"
            )
        for condition in paliers(grille):
            erreurs.append(
                f"{selecteur} : un palier de largeur réimpose des colonnes ({condition}) — "
                "la conversion est annulée par ce bloc"
            )
    return erreurs


def principal(arguments: list[str] | None = None) -> int:
    analyseur = argparse.ArgumentParser(description="Mesure les grilles au lieu de présumer leurs paliers.")
    analyseur.add_argument("--grille", help="ne mesurer qu'un sélecteur")
    analyseur.add_argument("--minimum", type=int, help="tester un minimum de piste précis")
    analyseur.add_argument("--json", action="store_true", help="sortie machine")
    analyseur.add_argument(
        "--regle",
        action="store_true",
        help="imprimer, grille par grille, le minimum que la règle de calcul donne",
    )
    analyseur.add_argument(
        "--verifier",
        action="store_true",
        help="contrôle les grilles converties contre docs/rd/grilles-dynamiques.toml",
    )
    options = analyseur.parse_args(arguments)

    chemin = RACINE / FEUILLE
    if not chemin.is_file():
        print(f"Feuille de style introuvable : {FEUILLE}", file=sys.stderr)
        return 2
    grilles = lire_grilles(chemin.read_text(encoding="utf-8"))

    if options.verifier:
        try:
            registre = lire_registre(RACINE)
        except SourceIllisible as erreur:
            print(f"Impossible de vérifier les grilles : {erreur}", file=sys.stderr)
            return 2
        erreurs = verifier(grilles, registre)
        if erreurs:
            for erreur in erreurs:
                print(f"  - {erreur}", file=sys.stderr)
            print(f"Refusé : {len(erreurs)} écart(s) entre la feuille et {REGISTRE}.", file=sys.stderr)
            return 1
        converties = len(registre.get("grille", []))
        print(
            f"Grilles dynamiques : {converties} grilles déclarent leur largeur de piste au lieu "
            "d'un nombre de colonnes, et aucune ne se laisse réimposer un palier."
        )
        return 0

    if options.grille:
        grille = grilles.get(options.grille)
        if grille is None:
            print(f"Sélecteur inconnu dans la feuille : {options.grille}", file=sys.stderr)
            return 2
        if options.minimum is not None:
            nombre, maximal, details = ecart(grille, options.minimum)
            print(
                f"{grille.selecteur} à auto-fit {options.minimum}px : {nombre} écart(s), "
                f"maximum {maximal}"
            )
            for largeur, ancienne, nouvelle in details[:20]:
                print(f"  {largeur}px : {ancienne} → {nouvelle}")
            return 0
        minimum, nombre, maximal, details = meilleur_minimum(grille)
        print(f"{grille.selecteur} — {colonnes_de_conception(grille)} colonnes, gap {grille.gap:g}px")
        for condition in paliers(grille):
            print(f"  palier {condition}")
        print(
            f"  meilleur auto-fit {minimum}px : {nombre} écart(s), maximum {maximal}, "
            f"carte la plus étroite {carte_minimale(grille, minimum):.0f}px"
        )
        for largeur, ancienne, nouvelle in details[:20]:
            print(f"    {largeur}px : {ancienne} → {nouvelle}")
        return 0

    if options.regle:
        mesurees = 0
        for selecteur, grille in sorted(grilles.items()):
            k = colonnes_de_conception(grille)
            if not k:
                continue
            minimum = minimum_pour_k(k, grille.gap)
            if minimum is None:
                print(f"{selecteur:32} {k} col. — aucune piste ne tient")
                continue
            mesurees += 1
            avant = min(
                (conteneur(largeur) - (colonnes_anciennes(grille, largeur) - 1) * grille.gap)
                / colonnes_anciennes(grille, largeur)
                for largeur in LARGEURS
            )
            print(
                f"{selecteur:32} {k} col. → minmax(min({minimum}px, 100%), 1fr) · "
                f"pire carte {avant:.0f}px → {carte_minimale(grille, minimum):.0f}px · "
                f"{len(paliers(grille))} palier(s) de largeur"
            )
        print(f"{mesurees} grilles mesurées.")
        return 0

    lignes = etat(grilles)
    if options.json:
        print(json.dumps(lignes, ensure_ascii=False, indent=2))
    else:
        print(rapport(lignes))
    return 0


if __name__ == "__main__":
    sys.exit(principal())
