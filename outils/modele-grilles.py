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
from html.parser import HTMLParser
from dataclasses import dataclass, field
from pathlib import Path

RACINE = Path(os.environ.get("MRSC_RACINE") or Path(__file__).resolve().parent.parent).resolve()
FEUILLE = Path("assets/css/site.css")

#: Largeurs de fenêtre balayées, de la plus étroite tenable au grand écran.
LARGEURS = list(range(240, 2561, 10))

#: Le même balayage au pixel. Depuis le 1er novembre 2026, la promesse « aucune
#: largeur ne change de nombre de colonnes » se vérifie ici : au pas de 10 px,
#: trois grilles converties la veille passaient pour exactes alors qu'elles
#: changeaient de colonnes à **761 px**, une largeur que le pas sautait. Une
#: bande étroite n'est pas une bande nulle — la première est invisible, la
#: seconde est vraie.
LARGEURS_FINES = list(range(240, 2561, 1))

#: Largeur du conteneur : `width: min(var(--content), calc(100% - 3rem))`.
#: `--content` vaut 1160 px par défaut ; les présentations le changent (940,
#: 1240, 1380, 1480) et ce script ne mesure que la présentation par défaut.
CONTENU_DEFAUT = 1160

#: La gouttière horizontale du conteneur n'est **plus une constante**.
#:
#: Le 1er novembre 2026, la première confrontation à un vrai navigateur a trouvé
#: 70 points divergents sur 743, dans 23 grilles sur 34. Les largeurs d'éléments
#: mesurées désignaient un seul coupable, présent depuis le premier jour : le
#: modèle présumait 48 px de gouttière **partout**, alors que la feuille écrit
#: `calc(100% - 3rem)` et, sous 760 px, `calc(100% - 2rem)`. Le conteneur
#: rétrécit donc de 16 px quand la fenêtre grandit d'un pixel, et aucune base de
#: `flex` ne peut produire un repli dans ce sens : les six grilles converties sur
#: un palier de 760 px promettaient un repli géométriquement impossible.
#:
#: Une gouttière en `rem` suit la taille du texte : à 130 %, 3rem vaut 62,4 px.
@dataclass(frozen=True)
class Gouttiere:
    """Ce que la feuille retire à `100%` pour fabriquer le conteneur."""

    large: float = 3.0  # en `rem`, au-dessus du seuil
    etroit: float = 2.0  # en `rem`, au seuil et en dessous
    seuil: int = 760
    source: str = "non lue"

    def en_px(self, largeur: int, echelle: float = 1.0) -> float:
        rem = self.etroit if largeur <= self.seuil else self.large
        return rem * RACINE_PX * echelle


class GouttiereIllisible(Exception):
    """La feuille ne dit pas ce que le conteneur retire : le modèle doit se taire."""


#: Remplie par `lire_grilles` à partir de la feuille. Vide tant que rien n'a été
#: lu : `conteneur()` refuse alors de calculer, plutôt que de retomber sur 48 px.
GOUTTIERE: Gouttiere | None = None


def lire_gouttiere(texte: str) -> Gouttiere:
    """La gouttière du `.container`, lue dans la feuille.

    Deux déclarations suffisent : `width: min(var(--content), calc(100% - Nrem))`
    dans la règle de base, et la même sous une condition `(max-width: …px)`. Un
    `%` sans `rem`, une variable ou une valeur en `px` ne sont pas interprétés :
    la lecture échoue et l'appelant doit le dire. C'est le seul chiffre que ce
    modèle présumait encore, et il portait vingt-deux grilles.
    """
    base: float | None = None
    etroit: float | None = None
    seuil: int | None = None
    for selecteurs, corps, largeur_max, largeur_min, _ in decouper(sans_commentaires(texte)):
        if not any(selecteur == ".container" for selecteur in selecteurs):
            continue
        trouve = re.search(r"width\s*:\s*min\([^;]*calc\(\s*100%\s*-\s*([\d.]+)rem\s*\)", corps)
        if not trouve:
            continue
        valeur = float(trouve.group(1))
        if largeur_max is not None:
            etroit = valeur
            seuil = largeur_max
        elif largeur_min is None:
            base = valeur
    if base is None:
        raise GouttiereIllisible(
            "aucune règle `.container` ne dit ce qu'elle retire à 100% — "
            "le conteneur ne peut pas être calculé, et 48 px serait une supposition"
        )
    return Gouttiere(
        large=base,
        etroit=etroit if etroit is not None else base,
        seuil=seuil if seuil is not None else 0,
        source="site.css",
    )


def definir_gouttiere(texte: str) -> Gouttiere:
    """Inscrit la gouttière lue pour les calculs suivants."""
    global GOUTTIERE
    GOUTTIERE = lire_gouttiere(texte)
    return GOUTTIERE


def gouttiere() -> Gouttiere:
    if GOUTTIERE is None:
        raise GouttiereIllisible(
            "la gouttière du conteneur n'a pas été lue — appeler `definir_gouttiere` "
            "avec la feuille avant tout calcul de largeur"
        )
    return GOUTTIERE

#: Largeur de carte en dessous de laquelle une grille tasse son contenu.
CARTE_MINIMALE = 220

#: Planchers candidats pour `minmax(min(Npx, 100%), 1fr)`, par pas de 10 px.
CANDIDATS = list(range(180, 481, 10))

MEDIA_LARGEUR = re.compile(r"\((min|max)-width\s*:\s*(\d+)px\s*\)")

#: La valeur complète d'une déclaration de colonnes, jusqu'au point-virgule.
DECLARATION_COLONNES = re.compile(r"grid-template-columns\s*:\s*([^;]+)")

#: Les formes que ce modèle sait lire. Tout le reste est **asymétrique** — un
#: panneau texte + bouton (`minmax(0, 1fr) auto`), un formulaire à bouton
#: (`minmax(180px, 1.5fr) repeat(2, minmax(160px, 1fr)) auto`), une colonne de
#: navigation (`20px 54px minmax(0, 1fr)`). Ces dispositions ne se ramènent pas à
#: un nombre de colonnes égales : les convertir en `auto-fit` **changerait le
#: dessin**, pas seulement le moment du repli.
#:
#: Le 31 octobre 2026, la version précédente cherchait un fragment de
#: `repeat(...)` n'importe où dans la valeur : `.join-panel` (`1fr auto`)
#: s'annonçait « 1 colonne » et `.learning-filters` « 2 colonnes ». Le rapport
#: proposait alors de convertir des panneaux qui n'ont rien à convertir, et le
#: compte des grilles à traiter était faux par excès.
REPEAT_FIXE = re.compile(r"^repeat\(\s*(\d+)\s*,\s*minmax\([^()]*\)\s*\)$")
#: `repeat(3, 1fr)` et `1fr 1fr` sont des colonnes **égales** écrites sans
#: `minmax`. Le 31 octobre 2026, le modèle les classait « asymétriques » : trois
#: aperçus de présentation et le bloc `.map-info` échappaient donc au compte, et
#: le rapport annonçait 34 grilles inégales là où quatre d'entre elles étaient
#: seulement écrites autrement. Une écriture n'est pas un dessin.
REPEAT_FR = re.compile(r"^repeat\(\s*(\d+)\s*,\s*(?:minmax\(\s*0\s*,\s*1fr\s*\)|1fr)\s*\)$")
FR_EGALES = re.compile(r"^(?:1fr)(?:\s+1fr)+$")
AUTOFIT_MIN = re.compile(
    r"^repeat\(\s*auto-fit\s*,\s*minmax\(\s*min\(\s*(\d+)px\s*,\s*100%\s*\)\s*,\s*1fr\s*\)\s*\)$"
)
AUTOFIT_NU = re.compile(r"^repeat\(\s*auto-fit\s*,\s*minmax\(\s*(\d+)px\s*,\s*1fr\s*\)\s*\)$")
UNE_COLONNE = re.compile(r"^minmax\(\s*0\s*,\s*1fr\s*\)$")

FORMES = ("fixe", "dynamique", "asymetrique")
def classer_valeur(valeur: str) -> tuple[str, int | None, int | None]:
    """Forme, nombre de colonnes fixes, minimum de piste dynamique.

    `("fixe", k, None)` pour `repeat(k, minmax(...))`, `("dynamique", None, N)`
    pour `repeat(auto-fit, minmax(min(Npx,100%), 1fr))`, `("asymetrique", None,
    None)` pour tout le reste — et « tout le reste » est dit, pas deviné.
    """
    valeur = " ".join(valeur.split())
    trouvé = REPEAT_FIXE.match(valeur) or REPEAT_FR.match(valeur)
    if trouvé:
        return "fixe", int(trouvé.group(1)), None
    if FR_EGALES.match(valeur):
        return "fixe", len(valeur.split()), None
    trouvé = AUTOFIT_MIN.match(valeur) or AUTOFIT_NU.match(valeur)
    if trouvé:
        return "dynamique", None, int(trouvé.group(1))
    if UNE_COLONNE.match(valeur):
        return "fixe", 1, None
    return "asymetrique", None, None


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
    #: L'écart tel qu'il est écrit (`1.15rem`, `clamp(2rem, 5vw, 4.5rem)`).
    #: `gap` n'en est que la valeur à la fenêtre maximale ; un calcul mené à une
    #: autre largeur doit passer par `ecart_a()`.
    gap_expr: str = ""
    #: Faux quand la feuille écrit un écart que ce modèle ne sait pas évaluer.
    gap_lu: bool = True
    regles: list[Regle] = field(default_factory=list)
    source: str = ""
    #: Vraie dès qu'une de ses règles est asymétrique : la grille n'est alors pas
    #: convertible en `auto-fit`, et le rapport doit le dire au lieu de proposer.
    asymetrique: bool = False
    valeur_asymetrique: str = ""
    #: Base de `flex` choisie quand elle diffère du minimum déclaré — écrite en
    #: `em` pour suivre la taille du texte (voir `plancher_de_compromis`).
    base_flex: float | None = None
    #: Le remplissage horizontal écrit par la règle de base (`clamp(1.5rem,4vw,2.6rem)`).
    #: Un conteneur qui porte son propre remplissage ne donne pas sa largeur à ses
    #: enfants, et le nombre de colonnes se décide sur la largeur utile.
    padding_expr: str | None = None
    #: Faux quand ce remplissage n'est pas évaluable : la largeur utile est alors
    #: inconnue, et le modèle refuse de prédire au lieu de supposer.
    padding_lu: bool = True
    #: Nombre d'éléments que les pages mettent au plus dans cette grille, mesuré
    #: dans le HTML (`lire_capacites`). 0 = non mesuré. `auto-fit` ne remplit pas
    #: une piste vide : une grille de deux éléments ne montre jamais trois
    #: colonnes, même si l'arithmétique en calcule trois. Sans ce champ, le
    #: modèle annonçait « 3 colonnes » et une carte de 192 px là où l'écran
    #: affiche deux cartes de 570 px.
    items: int = 0


def sans_commentaires(texte: str) -> str:
    """Remplace chaque commentaire par ses sauts de ligne, pour garder les numéros."""
    return re.sub(r"/\*.*?\*/", lambda trouve: "\n" * trouve.group(0).count("\n"), texte, flags=re.S)


def decouper(texte: str) -> list[tuple[list[str], str, int | None, int | None, int]]:
    """Rend (sélecteurs, corps, largeur max, largeur min, ligne) pour chaque règle.

    Un analyseur volontairement pauvre : des blocs et des règles, pas
    d'imbrication de règles. Il doit être capable de dire « je ne sais pas lire
    ça » plutôt que de sauter une règle en silence.

    Il tient une **pile de blocs** et referme les blocs vides comme les autres.
    Le 31 octobre 2026, la version précédente ne refermait un `@media` qu'après
    une règle : retirer la dernière règle d'un bloc laissait `@media (...) { }`,
    et les règles **suivantes** étaient attribuées à cette condition. Huit
    grilles converties ont disparu du rapport sans un mot, et le contrôle a
    annoncé 16 grilles au lieu de 33. Un compteur qui perd des lignes sans le
    dire est pire qu'un compteur faux : il fait croire au progrès.
    """
    regles = []
    blocs: list[tuple[int | None, int | None]] = []
    i, n = 0, len(texte)
    while i < n:
        while i < n and texte[i] in " \t\r\n}":
            if texte[i] == "}":
                if not blocs:
                    raise SystemExit(
                        "accolade fermante sans bloc ouvert ligne "
                        f"{texte[:i].count(chr(10)) + 1} — la feuille n'est pas lisible"
                    )
                blocs.pop()
            i += 1
        if i >= n:
            break
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
            blocs.append((largeur_max, largeur_min))
            i = ouvrante + 1
            continue
        if entete_nu.startswith("@"):
            # `@supports`, `@font-face`, `@keyframes`… : le bloc est traversé,
            # pas interprété. Il hérite de la condition du bloc qui le contient,
            # pour qu'une règle imbriquée ne devienne pas « sans condition ».
            blocs.append(blocs[-1] if blocs else (None, None))
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
        largeur_max, largeur_min = blocs[-1] if blocs else (None, None)
        selecteurs = [s.strip() for s in re.split(r",(?![^(]*\))", entete_nu) if s.strip()]
        regles.append((selecteurs, corps, largeur_max, largeur_min, ligne))
        i = j + 1
    return regles


#: Éléments sans contenu : ils ne comptent pas comme un enfant de grille.
VIDES = frozenset(
    "area base br col embed hr img input link meta source track wbr".split()
)

GAP_REM = re.compile(r"(?:^|;)\s*(gap|column-gap|row-gap)\s*:\s*([^;]+)")
LONGUEUR = re.compile(r"^([\d.]+)(rem|px)$")


def ecart_colonnes(corps: str) -> str | None:
    """L'expression de l'écart **entre colonnes** déclarée par ce bloc.

    Le 31 octobre 2026, la lecture prenait le premier nombre de `gap` sans
    regarder lequel c'était : `gap: .75rem 1.1rem` vaut 12 px entre les lignes
    et **17,6 px entre les colonnes**, et c'est le second qui décide du nombre
    de colonnes. Elle rendait aussi un nombre tout fait, ce qui obligeait à
    supposer qu'un écart ne dépend pas de la fenêtre — faux pour les huit
    grilles qui écrivent `clamp(2rem, 5vw, 4.5rem)`. L'expression est donc
    gardée telle quelle, et évaluée par `ecart_a()` à chaque largeur.
    """
    trouve = GAP_REM.search(corps)
    if not trouve:
        return None
    propriete, valeur = trouve.group(1), " ".join(trouve.group(2).split())
    if propriete == "row-gap":
        return None
    # `clamp(2rem, 5vw, 4.5rem)` contient des espaces : un découpage naïf rendait
    # `clamp(2rem,` — un écart illisible, donc un calcul d'écart muet (0 px
    # annoncé partout). On découpe au premier niveau de parenthèses.
    morceaux, profondeur, courant = [], 0, ""
    for caractere in valeur:
        if caractere == "(":
            profondeur += 1
        elif caractere == ")":
            profondeur -= 1
        if caractere == " " and profondeur == 0:
            if courant:
                morceaux.append(courant)
            courant = ""
            continue
        courant += caractere
    if courant:
        morceaux.append(courant)
    return morceaux[1] if len(morceaux) == 2 else morceaux[0]


CLAMP = re.compile(r"^clamp\(\s*([^,]+?)\s*,\s*([^,]+?)\s*,\s*(.+?)\s*\)$")


def mesure_en_px(morceau: str, largeur: int | None = None, echelle: float = 1.0) -> float | None:
    """Une longueur CSS en pixels, évaluée à une largeur de fenêtre donnée.

    Rend `None` quand l'expression n'est pas une longueur évaluable ici — un
    `%`, une `ch`, une variable. L'appelant doit alors **le dire** : supposer
    16 px en silence est exactement ce que ce fichier reproche aux autres.
    """
    morceau = morceau.strip()
    # Un zéro sans unité est un zéro : `padding: 0` ne réserve aucune place, et
    # le refuser rendait illisible le remplissage de toute grille qui l'écrit.
    if re.match(r"^[+-]?0+(?:\.0+)?$", morceau):
        return 0.0
    trouvé = LONGUEUR.match(morceau)
    if trouvé:
        nombre = float(trouvé.group(1))
        return nombre * RACINE_PX * echelle if trouvé.group(2) == "rem" else nombre
    trouvé = re.match(r"^([\d.]+)vw$", morceau)
    if trouvé and largeur is not None:
        # `vw` ne suit pas la taille du texte : 5vw vaut 5 % de la fenêtre, quel
        # que soit le réglage. C'est la moitié des écarts de `.hero-grid`.
        return float(trouvé.group(1)) * largeur / 100
    borné = CLAMP.match(morceau)
    if borné:
        bas = mesure_en_px(borné.group(1), largeur, echelle)
        milieu = mesure_en_px(borné.group(2), largeur, echelle)
        haut = mesure_en_px(borné.group(3), largeur, echelle)
        if None in (bas, milieu, haut):
            return None
        return max(bas, min(milieu, haut))
    return None


def fenetre_maximale() -> int:
    """La plus petite fenêtre où le conteneur atteint `--content`.

    Dérivée de la gouttière lue, et non écrite 1208 px : le jour où la feuille
    change `3rem`, tout ce qui se mesure « à la fenêtre maximale » doit changer
    avec elle.
    """
    return int(round(CONTENU_DEFAUT + gouttiere().large * RACINE_PX))


def ecart_a(grille: "Grille", largeur: int, echelle: float = 1.0) -> float | None:
    """L'écart entre colonnes de cette grille, à cette largeur et taille de texte."""
    if not grille.gap_expr:
        return None
    return mesure_en_px(grille.gap_expr, largeur, echelle)


def lire_grilles(texte: str) -> dict[str, Grille]:
    """Toutes les grilles dont la feuille fixe ou calcule le nombre de colonnes."""
    texte = sans_commentaires(texte)
    definir_gouttiere(texte)
    grilles: dict[str, Grille] = {}
    for ordre, (selecteurs, corps, largeur_max, largeur_min, ligne) in enumerate(decouper(texte)):
        trouve = DECLARATION_COLONNES.search(corps)
        if not trouve:
            continue
        valeur = " ".join(trouve.group(1).split())
        forme, colonnes, minimum = classer_valeur(valeur)
        gap_expr = ecart_colonnes(corps)
        remplissage = padding_horizontal(corps) if largeur_max is None and largeur_min is None else None
        for selecteur in selecteurs:
            grille = grilles.setdefault(selecteur, Grille(selecteur=selecteur, source=f"site.css:{ligne}"))
            if remplissage and grille.padding_expr is None:
                grille.padding_expr = remplissage
                grille.padding_lu = padding_horizontal_px(remplissage, CONTENU_DEFAUT) is not None
            if gap_expr is not None:
                grille.gap_expr = gap_expr
                valeur_max = mesure_en_px(gap_expr, fenetre_maximale())
                if valeur_max is None:
                    grille.gap_lu = False
                else:
                    grille.gap = round(valeur_max, 2)
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
            if forme == "asymetrique" and not grille.asymetrique:
                grille.asymetrique = True
                grille.valeur_asymetrique = valeur
            if largeur_max is None and largeur_min is None and colonnes:
                grille.colonnes_base = colonnes
    return grilles


def conteneur(largeur: int, contenu: float = CONTENU_DEFAUT, echelle: float = 1.0) -> float:
    """Largeur du `.container` à cette fenêtre et cette taille de texte.

    `echelle` vaut 1 à taille normale, 1,15 à 115 %, 1,3 à 130 % : une gouttière
    écrite en `rem` grandit avec le texte, donc le conteneur **rétrécit** quand
    quelqu'un agrandit. C'était l'une des trois causes de divergence mesurées le
    1er novembre 2026, et elle rendait fausse toute prédiction au-delà de 100 %.
    """
    return min(contenu, largeur - gouttiere().en_px(largeur, echelle))


PADDING_DECLARATION = re.compile(r"(?<![\w-])padding(?:-inline|-left|-right)?\s*:\s*([^;]+)")


def padding_horizontal(corps: str) -> str | None:
    """L'expression du remplissage **horizontal** d'un bloc, s'il y en a un.

    Une grille qui porte son propre remplissage ne donne pas le conteneur entier
    à ses enfants : `.learning-work-panel` vaut 713 px à 761 px de fenêtre et
    n'en laisse que 652 à ses deux panneaux. Le prédicat du repli porte donc sur
    la largeur **utile**, pas sur celle du conteneur.
    """
    trouve = PADDING_DECLARATION.search(corps)
    if not trouve:
        return None
    valeur = " ".join(trouve.group(1).split())
    return valeur


def padding_horizontal_px(expression: str, largeur: int, echelle: float = 1.0) -> float | None:
    """Le remplissage horizontal total (gauche + droite), en pixels."""
    morceaux, profondeur, courant = [], 0, ""
    for caractere in expression:
        if caractere == "(":
            profondeur += 1
        elif caractere == ")":
            profondeur -= 1
        if caractere == " " and profondeur == 0:
            if courant:
                morceaux.append(courant)
            courant = ""
            continue
        courant += caractere
    if courant:
        morceaux.append(courant)
    if not morceaux or len(morceaux) > 4:
        return None
    # `padding: a` → a des deux côtés ; `a b` → b ; `a b c` → b ; `a b c d` → b+d.
    if len(morceaux) == 1:
        gauche = droite = mesure_en_px(morceaux[0], largeur, echelle)
    elif len(morceaux) == 2:
        gauche = droite = mesure_en_px(morceaux[1], largeur, echelle)
    elif len(morceaux) == 3:
        gauche = droite = mesure_en_px(morceaux[1], largeur, echelle)
    else:
        gauche = mesure_en_px(morceaux[1], largeur, echelle)
        droite = mesure_en_px(morceaux[3], largeur, echelle)
    if gauche is None or droite is None:
        return None
    return gauche + droite


def conteneur_de(grille: "Grille", largeur: int, echelle: float = 1.0) -> float:
    """La largeur que cette grille laisse **à ses enfants**, remplissage déduit.

    Rend le conteneur entier quand la règle n'écrit aucun remplissage. Quand elle
    en écrit un que ce modèle ne sait pas évaluer, elle lève : une largeur utile
    supposée fausse est exactement ce qui a coûté 70 divergences.
    """
    place = conteneur(largeur, echelle=echelle)
    if not grille.padding_expr:
        return place
    if not grille.padding_lu:
        raise GouttiereIllisible(
            f"{grille.selecteur} : remplissage `{grille.padding_expr[:40]}` illisible — "
            "la largeur utile de ses enfants ne peut pas être calculée"
        )
    rembourrage = padding_horizontal_px(grille.padding_expr, largeur, echelle)
    if rembourrage is None:
        raise GouttiereIllisible(
            f"{grille.selecteur} : remplissage `{grille.padding_expr[:40]}` non évaluable "
            f"à {largeur} px — la largeur utile de ses enfants ne peut pas être calculée"
        )
    return place - rembourrage


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
                return auto_fit_grille(grille, regle.minimum, largeur)
            if regle.colonnes:
                resultat = regle.colonnes
    return resultat


def auto_fit_grille(grille: "Grille", minimum: int, largeur: int) -> int:
    """`auto_fit` avec l'écart **de cette largeur**, et non celui de la fenêtre maximale."""
    gap = ecart_a(grille, largeur)
    return auto_fit(minimum, grille.gap if gap is None else gap, largeur, grille.items)


def auto_fit(minimum: int, gap: float, largeur: int, items: int = 0) -> int:
    """Colonnes que `repeat(auto-fit, minmax(min(Npx,100%), 1fr))` produit.

    `items` borne le résultat : `auto-fit` replie les pistes vides, donc une
    grille qui ne reçoit que deux éléments n'en montre jamais trois.
    """
    place = conteneur(largeur)
    colonnes = max(1, math.floor((place + gap) / (minimum + gap)))
    return min(colonnes, items) if items else colonnes


def ecart(grille: Grille, minimum: int) -> tuple[int, int, list[tuple[int, int, int]]]:
    """(nombre d'écarts, écart maximal, écarts détaillés) entre ancienne et nouvelle règle."""
    details = []
    for largeur in LARGEURS:
        ancienne = colonnes_anciennes(grille, largeur)
        nouvelle = auto_fit_grille(grille, minimum, largeur)
        if ancienne != nouvelle:
            details.append((largeur, ancienne, nouvelle))
    maximal = max((abs(a - n) for _, a, n in details), default=0)
    return len(details), maximal, details


def meilleur_minimum(grille: Grille) -> tuple[int, int, int, list[tuple[int, int, int]]]:
    """Le `N` qui reproduit le mieux l'ancienne cascade — **diagnostic, pas décision**.

    Le 31 octobre 2026, ce chiffre a été pris pour la recommandation, et huit
    grilles ont été converties avec lui : elles montraient 3 ou 4 colonnes au
    conteneur maximal au lieu de 4, `minimum_pour_k` en demandait 270 et le CSS
    portait 230. Deux règles différentes, un seul nom dans le rapport. La
    recommandation est désormais `minimum_pour_k` et rien d'autre ; cette
    fonction garde son usage — dire à quel point l'ancienne cascade est
    reproduite — et n'est plus proposée comme consigne.
    """
    classement = []
    for minimum in CANDIDATS:
        nombre, maximal, details = ecart(grille, minimum)
        classement.append((nombre, maximal, minimum, details))
    nombre, maximal, minimum, details = min(classement, key=lambda c: (c[0], c[1], c[2]))
    return minimum, nombre, maximal, details


def carte_minimale(grille: Grille, minimum: int) -> float:
    """Largeur de carte la plus faible sur le balayage, pour la nouvelle règle."""
    valeurs = []
    for largeur in LARGEURS:
        colonnes = auto_fit_grille(grille, minimum, largeur)
        gap = ecart_a(grille, largeur)
        gap = grille.gap if gap is None else gap
        valeurs.append((conteneur(largeur) - (colonnes - 1) * gap) / colonnes)
    return min(valeurs)


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
        return auto_fit_grille(grille, base.minimum, fenetre_maximale())
    return 0


def seuil_une_colonne(grille: Grille) -> int | None:
    """La plus grande fenêtre où l'ancienne cascade ne montrait qu'une colonne.

    C'est la seule information de conception que porte une grille à deux
    colonnes : entre deux colonnes et une, il n'y a pas d'étape intermédiaire,
    donc pas de largeur de carte à préserver — seulement un moment où l'on
    renonce à la paire.
    """
    apparentes = [largeur for largeur in LARGEURS if colonnes_anciennes(grille, largeur) == 1]
    return max(apparentes) if apparentes else None


def seuil_note(grille: Grille) -> str:
    """Le seuil de repli à une colonne, s'il compte pour cette grille."""
    if colonnes_de_conception(grille) != 2:
        return ""
    seuil = seuil_une_colonne(grille)
    return f" (repli à 1 col. sous {seuil}px)" if seuil else ""


def minimum_de_repli(grille: Grille) -> int | None:
    """Le plus petit minimum qui renonce à la paire là où la cascade y renonçait.

    Le seuil se lit sur `conteneur(seuil)`, et non sur `conteneur(seuil + 1)` :
    sous 760 px la gouttière est plus étroite, donc le conteneur y est **plus
    large**. Une paire renoncée à 760 px peut donc revenir un peu au-dessus, dès
    que le conteneur dépasse ce que deux panneaux réclament — elle ne revient
    jamais en arrière, et c'est cet invariant, et non le souvenir du palier, que
    le contrôle vérifie (`bandes_de_retour`).
    """
    seuil = seuil_une_colonne(grille)
    if seuil is None:
        return None
    place = conteneur(seuil)
    candidats = [n for n in CANDIDATS if 2 * n + grille.gap > place]
    return min(candidats) if candidats else None


def minimum_sans_troisieme_colonne(grille: Grille) -> int | None:
    """Le plus petit minimum qui interdit une troisième colonne au conteneur maximal.

    Une grille dessinée à deux colonnes n'a pas de troisième colonne à gagner :
    l'ajouter, c'est soit laisser une carte seule sur sa ligne (quatre documents
    deviennent 3 + 1), soit couper une paire (une `<dl>` de trois paires donne
    `dt dd dt` puis `dd dt dd`). `auto-fit` sert ici à **retirer le palier**, pas
    à changer le dessin. Le 31 octobre 2026, cette règle manquait : `.document-grid`
    aurait affiché trois colonnes et une carte orpheline sur un écran de 1 920 px.
    """
    place = conteneur(fenetre_maximale())
    candidats = [n for n in CANDIDATS if 3 * n + 2 * grille.gap > place]
    return min(candidats) if candidats else None


def minimum_recommande(grille: Grille, capacite: dict | None = None) -> int | None:
    """La largeur de piste que la règle donne à cette grille. Une seule source.

    Trois cas, et chacun répond à une question différente :

    - **Trois colonnes ou plus** : la grille a des étapes intermédiaires, et la
      bonne question est « jusqu'où les cartes peuvent-elles s'élargir sans que
      la grille perde sa forme au conteneur maximal ? ». On prend donc le plus
      large minimum qui garde `k` colonnes à 1160 px.
    - **Deux colonnes** : il n'y a aucune étape intermédiaire. Prendre le plus
      large minimum qui garde deux colonnes à 1160 px donnerait des panneaux de
      570 px et un repli dès 1 207 px de fenêtre — une régression visible sur un
      ordinateur portable. La seule information de conception est le moment où
      l'on renonce à la paire ; le minimum se calcule pour que ce moment reste
      celui de l'ancienne cascade (`minimum_de_repli`).
    - **Deux colonnes qui pourraient en devenir trois** : `auto-fit` ajouterait
      une colonne que personne n'a dessinée. Le minimum est alors relevé juste
      assez pour que trois colonnes ne tiennent pas au conteneur maximal
      (`minimum_sans_troisieme_colonne`), sauf si les pages ne mettent jamais
      plus de deux éléments dans la grille — `auto-fit` ne remplit pas une piste
      vide, la troisième colonne ne peut pas apparaître, et relever le minimum
      ne protégerait de rien. C'est une capacité **mesurée**, pas supposée.

    Ces distinctions ont coûté deux erreurs, corrigées le 31 octobre 2026 : la
    première version appliquait la règle des trois colonnes aux grilles à deux et
    proposait de replier `.document-grid` à 1 027 px au lieu de 760 ; la seconde
    ignorait la capacité des pages et aurait ajouté une colonne orpheline.
    """
    k = colonnes_de_conception(grille)
    if not k:
        return None
    if k >= 3:
        return minimum_pour_k(k, grille.gap)
    if seuil_une_colonne(grille) is None:
        return minimum_pour_k(k, grille.gap)
    repli = minimum_de_repli(grille)
    if repli is None:
        return None
    cap = minimum_sans_troisieme_colonne(grille)
    if cap is None:
        return repli
    items = (capacite or {}).get("items") or []
    if items and max(items) <= k:
        return repli
    return max(repli, cap)


def minimum_pour_k(k: int, gap: float, contenu: float = CONTENU_DEFAUT) -> int | None:
    """Le plus large minimum de piste qui laisse encore `k` colonnes au conteneur maximal.

    Une grille de conception à `k` colonnes n'a pas besoin d'un palier pour
    retomber à `k-1` : il suffit que chaque piste réclame une largeur telle que
    `k` pistes ne tiennent plus quand le conteneur rétrécit. Choisir le minimum le
    plus **large** possible dans cette plage donne les cartes les plus lisibles,
    et fait tomber le nombre de colonnes exactement au moment où la largeur ne
    suffit plus — pas à une largeur ronde choisie d'avance.
    """
    valides = [n for n in CANDIDATS if auto_fit(n, gap, fenetre_maximale()) == k]
    return max(valides) if valides else None


def normaliser(valeur: str) -> str:
    """Compare deux écritures de la même valeur (`minmax(0, 1fr)` = `minmax(0,1fr)`)."""
    return re.sub(r"\s+", "", valeur).replace(",", ",")


def declarations_mortes(grilles: dict[str, Grille]) -> list[dict]:
    """Les déclarations de colonnes, sous condition de largeur, qui ne décident rien.

    Une règle `@media` qui réécrit la valeur déjà en vigueur ne protège de rien :
    elle alourdit la feuille et fait croire à un palier qui n'existe pas. Le
    31 octobre 2026, `.contact-grid` figurait dans le bloc de 760 px pour y
    imposer `minmax(0, 1fr)` à une grille déjà à une colonne — et le compteur de
    règles ne pouvait pas le voir, puisqu'une règle qui perd son effet reste une
    règle. C'est cette limite-là que ce contrôle ferme.
    """
    mortes = []
    for selecteur, grille in grilles.items():
        for regle in grille.regles:
            if regle.largeur_max is None and regle.largeur_min is None:
                continue
            largeur = regle.largeur_max if regle.largeur_max is not None else regle.largeur_min + 1
            en_vigueur = None
            for autre in sorted(grille.regles, key=lambda x: x.ordre):
                if autre is regle or not applique(autre, largeur):
                    continue
                en_vigueur = autre.valeur
            if en_vigueur is not None and normaliser(en_vigueur) == normaliser(regle.valeur):
                mortes.append(
                    {
                        "selecteur": selecteur,
                        "ligne": regle.ligne,
                        "valeur": regle.valeur,
                        "largeur": largeur,
                    }
                )
    return mortes


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


def convertibles(grilles: dict[str, Grille]) -> list[Grille]:
    """Les grilles que l'on peut réellement ramener à une largeur de piste."""
    return sorted(
        (
            grille
            for grille in grilles.values()
            if colonnes_de_conception(grille) and not grille.asymetrique
        ),
        key=lambda grille: grille.selecteur,
    )


def asymetriques(grilles: dict[str, Grille]) -> list[Grille]:
    """Les grilles à pistes inégales : elles gardent leurs paliers, et c'est normal."""
    return sorted(
        (grille for grille in grilles.values() if grille.asymetrique),
        key=lambda grille: grille.selecteur,
    )


class _CompteurEnfants(HTMLParser):
    """Compte les enfants directs de chaque élément portant une classe mesurée.

    Le 31 octobre 2026, le modèle ne savait rien de ce que les pages mettent
    **dans** les grilles : il optimisait des largeurs de piste sans savoir
    combien de cartes elles reçoivent. Or c'est ce qui décide si la colonne
    ajoutée par `auto-fit` laisse une carte seule sur sa ligne, et si la grille
    est une liste de paires (`<dl>`) qu'il ne faut pas couper en trois.
    """

    def __init__(self, selecteurs: set[str]) -> None:
        super().__init__(convert_charrefs=True)
        self.selecteurs = selecteurs
        self.pile: list[str] = []
        self.encours: list[dict] = []
        self.resultats: list[tuple[str, str, int]] = []

    def handle_starttag(self, balise, attributs):
        if balise in VIDES:
            return
        classes = set(((dict(attributs).get("class") or "")).split())
        for suivi in self.encours:
            if len(self.pile) + 1 == suivi["niveau"] + 1:
                suivi["compte"] += 1
        self.pile.append(balise)
        for selecteur in classes & self.selecteurs:
            self.encours.append(
                {"selecteur": selecteur, "balise": balise, "niveau": len(self.pile), "compte": 0}
            )

    def handle_endtag(self, balise):
        for i in range(len(self.pile) - 1, -1, -1):
            if self.pile[i] == balise:
                del self.pile[i:]
                break
        for suivi in [s for s in self.encours if s["niveau"] > len(self.pile)]:
            self.resultats.append((suivi["selecteur"], suivi["balise"], suivi["compte"]))
            self.encours.remove(suivi)


def pages_du_site(racine: Path) -> list[Path]:
    """Les pages HTML du dépôt, sous-dossiers compris.

    `Path.rglob` ne descend pas dans un lien symbolique ; or les bancs montent le
    dépôt en liens. Un walk qui suit les liens mesure donc la même chose dans le
    dépôt et dans une copie de banc, et `.learning-code-grid` — dont les pages
    vivent dans `apprendre/fiches/` — n'est plus « absente » par accident de
    parcours.
    """
    pages = []
    for dossier, sous_dossiers, fichiers in os.walk(racine, followlinks=True):
        sous_dossiers[:] = sorted(
            nom
            for nom in sous_dossiers
            if nom not in {".git", "node_modules", "outils", "docs"} and not nom.startswith(".")
        )
        pages.extend(Path(dossier) / nom for nom in sorted(fichiers) if nom.endswith(".html"))
    return pages


class _EnfantsClasses(HTMLParser):
    """Les classes des enfants **directs** d'un élément portant une classe suivie.

    Sert à une seule question, mais elle a coûté une CI rouge le 31 octobre
    2026 : un enfant de conteneur flex peut-il encore porter un plafond écrit en
    `width` ? La réponse dépend de ce que les pages mettent dans la grille, donc
    du HTML — pas de la feuille seule.
    """

    def __init__(self, cibles: set[str]) -> None:
        super().__init__(convert_charrefs=True)
        self.cibles = cibles
        self.pile: list[tuple[str, str | None]] = []
        self.enfants: dict[str, set[str]] = {}

    def handle_starttag(self, balise, attributs):
        if balise in VIDES:
            return
        classes = set(((dict(attributs).get("class") or "")).split())
        if self.pile and self.pile[-1][1]:
            self.enfants.setdefault(self.pile[-1][1], set()).update(classes)
        marque = next(iter(sorted(classes & self.cibles)), None)
        self.pile.append((balise, marque))

    def handle_endtag(self, balise):
        for i in range(len(self.pile) - 1, -1, -1):
            if self.pile[i][0] == balise:
                del self.pile[i:]
                return


def enfants_des_grilles(racine: Path, selecteurs: list[str]) -> dict[str, set[str]]:
    """`{"english-promo-panel": {"english-promo-copy", "english-promo-art"}, …}`.

    Un sélecteur absent des pages n'apparaît pas : le contrôle doit alors dire
    qu'il n'a rien pu regarder, pas supposer un enfant unique.
    """
    import collections

    cibles = {selecteur.lstrip(".") for selecteur in selecteurs if selecteur.startswith(".")}
    enfants: dict[str, set[str]] = collections.defaultdict(set)
    for page in pages_du_site(racine):
        try:
            texte = page.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        lecteur = _EnfantsClasses(cibles)
        try:
            lecteur.feed(texte)
        except Exception:  # page mal formée : on ne prétend rien y mesurer
            continue
        for cible, classes in lecteur.enfants.items():
            enfants["." + cible].update(classes)
    return dict(enfants)


def lire_capacites(racine: Path, selecteurs: list[str]) -> dict[str, dict]:
    """Ce que les pages mettent réellement dans chaque grille.

    Rend `{sélecteur: {"items": [...], "apparies": bool, "pages": [...]}}`. Un
    sélecteur absent de toutes les pages est absent du dictionnaire : le rapport
    doit alors dire que la capacité n'est pas mesurée, pas la supposer.
    """
    import collections

    cibles = {selecteur.lstrip(".") for selecteur in selecteurs if selecteur.startswith(".")}
    contenus: dict[str, list[tuple[str, str, int]]] = collections.defaultdict(list)
    for page in pages_du_site(racine):
        try:
            texte = page.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        compteur = _CompteurEnfants(cibles)
        try:
            compteur.feed(texte)
        except Exception:  # page mal formée : on ne prétend rien mesurer
            continue
        vus: set[str] = set()
        for selecteur, balise, nombre in compteur.resultats:
            vus.add(selecteur)
            contenus["." + selecteur].append((page.name, balise, nombre))
    capacites: dict[str, dict] = {}
    for selecteur, trouvailles in contenus.items():
        capacites[selecteur] = {
            "items": sorted({nombre for _, _, nombre in trouvailles}),
            "apparies": any(balise == "dl" for _, balise, _ in trouvailles),
            "pages": sorted({page for page, _, _ in trouvailles}),
        }
    return capacites


def appliquer_capacites(grilles: dict[str, Grille], capacites: dict[str, dict]) -> None:
    """Inscrit dans chaque grille le nombre d'éléments que les pages y mettent."""
    for selecteur, capacite in capacites.items():
        grille = grilles.get(selecteur)
        if grille is not None and capacite.get("items"):
            grille.items = max(capacite["items"])


def pistes(valeur: str) -> list[str]:
    """Découpe une valeur de `grid-template-columns` en pistes de premier niveau."""
    morceaux, profondeur, courant = [], 0, ""
    for caractere in valeur:
        if caractere == "(":
            profondeur += 1
        elif caractere == ")":
            profondeur -= 1
        if caractere == " " and profondeur == 0:
            if courant:
                morceaux.append(courant)
            courant = ""
            continue
        courant += caractere
    if courant:
        morceaux.append(courant)
    return morceaux


def nature_piste(piste: str) -> tuple[str, float | None, float | None]:
    """`(nature, minimum, maximum)` d'une piste : `contenu`, `fixe` ou `souple`."""
    piste = piste.strip()
    if piste in ("auto", "max-content", "min-content", "fit-content"):
        return "contenu", None, None
    borne = re.match(r"^minmax\(\s*([^,]+?)\s*,\s*(.+?)\s*\)$", piste)
    if borne:
        bas, haut = borne.group(1), borne.group(2)
        if bas in ("auto", "max-content", "min-content") or haut in ("auto", "max-content", "min-content"):
            return "contenu", None, None
        borne_basse = re.match(r"^([\d.]+)(px|rem)$", bas)
        minimum = float(borne_basse.group(1)) * (16 if borne_basse.group(2) == "rem" else 1) if borne_basse else 0.0
        # Le `fr` **est** le poids : le perdre faisait croire qu'un `1.05fr` et un
        # `.95fr` se partageaient l'espace à parts égales, et le calcul d'écart
        # entre grille et `flex` rendait zéro partout.
        poids = re.match(r"^([\d.]+)fr$", haut)
        if poids:
            return "souple", minimum, float(poids.group(1))
        return "borne", minimum, None
    if re.match(r"^[\d.]+fr$", piste):
        return "souple", 0.0, float(piste[:-2])
    mesure = re.match(r"^([\d.]+)(px|rem)$", piste)
    if mesure:
        valeur = float(mesure.group(1))
        return "fixe", valeur * (16 if mesure.group(2) == "rem" else 1), None
    return "contenu", None, None


def colonnes_de_la_cascade(grille: Grille, largeur: int) -> int:
    """Colonnes que la feuille actuelle prescrit à cette largeur, pistes inégales comprises.

    `colonnes_anciennes` ne lit que les règles qui **déclarent** un nombre de
    colonnes ; une grille à pistes inégales y répondait toujours « 1 », et le
    moindre calcul de flexion comparé à ce chiffre paraissait faux. Ici, une
    valeur inégale est comptée par ses pistes : `minmax(0, 1.15fr) minmax(280px,
    .75fr)` vaut deux colonnes tant que la règle de base s'applique.
    """
    en_vigueur = None
    for regle in sorted(grille.regles, key=lambda x: x.ordre):
        if applique(regle, largeur):
            en_vigueur = regle
    if en_vigueur is None:
        return 1
    if en_vigueur.colonnes:
        return en_vigueur.colonnes
    if en_vigueur.minimum:
        return auto_fit_grille(grille, en_vigueur.minimum, largeur)
    return max(1, len(pistes(en_vigueur.valeur)))


def largeurs_pistes(grille: Grille, largeur: int) -> dict | None:
    """Largeur de chaque colonne, aujourd'hui (grille) et avec un `flex-wrap`.

    Le nombre de colonnes ne dit pas tout : deux écritures peuvent afficher deux
    colonnes et ne pas leur donner la même largeur. `1.05fr / .95fr` partage
    tout l'espace selon le rapport ; `flex: 1.05 1 330px` ne partage que le
    **surplus** au-dessus du plancher. Convertir sans le dire changerait le
    dessin de quelques pour cent sans qu'aucun compteur ne le signale.

    Rend `None` quand la forme ne s'évalue pas (piste de contenu, écart
    illisible) : l'appelant doit alors renoncer, pas deviner.
    """
    if grille.asymetrique is True and not grille.regles:
        return None
    gap = ecart_a(grille, largeur)
    if gap is None:
        return None
    en_vigueur = None
    for regle in sorted(grille.regles, key=lambda x: x.ordre):
        if applique(regle, largeur):
            en_vigueur = regle
    if en_vigueur is None:
        return None
    if en_vigueur.colonnes:
        # Forme fixe : une seule largeur, égale, et un `flex` n'apporterait rien.
        return None
    natures = [nature_piste(piste) for piste in pistes(en_vigueur.valeur)]
    if any(nature != "souple" for nature, _, _ in natures) or not natures:
        return None
    place = conteneur(largeur) - (len(natures) - 1) * gap
    if place <= 0:
        return None
    # Grille : répartition par `fr`, planchers respectés.
    poids = [maximum or 1.0 for _, _, maximum in natures]
    planchers = [minimum or 0.0 for _, minimum, _ in natures]
    largeurs = [0.0] * len(natures)
    libres = set(range(len(natures)))
    reste = place
    while libres:
        total = sum(poids[i] for i in libres)
        bloque = {i for i in libres if reste * poids[i] / total < planchers[i]}
        if not bloque:
            for i in libres:
                largeurs[i] = reste * poids[i] / total
            break
        for i in bloque:
            largeurs[i] = planchers[i]
            reste -= planchers[i]
            libres.discard(i)
    grille_largeurs = list(largeurs)
    # `flex-wrap` : base = plancher de la piste, le plus grand plancher si elle
    # n'en a pas ; la croissance reprend le rapport des `fr`.
    plancher_commun = max(planchers) or 0.0
    # Une grille `minmax(0, 1.35fr) minmax(0, 1fr)` n'a aucun plancher : ses
    # colonnes ne dépendent que de la place. La base d'un `flex` est alors une
    # **décision** (où l'on renonce à la paire), et c'est elle qu'on mesure —
    # pas `0`, qui empêcherait tout repli. Le 1er novembre 2026, ce cas tombait
    # dans « contenu » avec les vraies pistes `auto`, ce qui est faux : rien
    # n'y dépend du texte.
    if plancher_commun <= 0 and not grille.base_flex:
        return None
    if grille.base_flex:
        plancher_commun = grille.base_flex
    bases = [grille.base_flex or (m if m and m > 0 else plancher_commun) for m in planchers]
    if sum(bases) + (len(bases) - 1) * gap > place + (len(bases) - 1) * gap:
        pass
    if sum(bases) + (len(bases) - 1) * gap > conteneur(largeur):
        flex_largeurs = None  # replié : une seule colonne par ligne
    else:
        surplus = conteneur(largeur) - sum(bases) - (len(bases) - 1) * gap
        total_poids = sum(poids)
        flex_largeurs = [
            base + surplus * poids[i] / total_poids for i, base in enumerate(bases)
        ]
    if flex_largeurs is None:
        return {"grille": grille_largeurs, "flex": None, "gap": gap}
    ecart_max = max(abs(a - b) for a, b in zip(grille_largeurs, flex_largeurs))
    return {"grille": grille_largeurs, "flex": flex_largeurs, "gap": gap, "ecart": ecart_max}


def ecart_de_largeur(grille: Grille) -> dict:
    """L'écart maximal, en pixels et en part de la colonne, entre grille et `flex`."""
    pire_px, pire_part, mesures = 0.0, 0.0, 0
    for largeur in LARGEURS:
        resultat = largeurs_pistes(grille, largeur)
        if not resultat or resultat["flex"] is None:
            continue
        mesures += 1
        for attendu, obtenu in zip(resultat["grille"], resultat["flex"]):
            if attendu <= 0:
                continue
            pire_px = max(pire_px, abs(attendu - obtenu))
            pire_part = max(pire_part, abs(attendu - obtenu) / attendu)
    return {"px": pire_px, "part": pire_part, "mesures": mesures}


def colonnes_en_flex(
    grille: Grille, largeur: int, plancher: float, items: int = 0, echelle: float = 1.0
) -> int:
    """Le nombre de panneaux qu'un `flex-wrap` alignerait à cette largeur.

    La règle est écrite **une fois**, ici : un panneau de plus tient quand
    `(n + 1) × plancher + n × écart` ne dépasse pas le conteneur. Le plafond par
    `items` n'est pas une précaution de style : `flex-wrap` ne crée pas
    d'élément, une grille de deux panneaux n'en montrera jamais trois.
    """
    place = conteneur_de(grille, largeur, echelle)
    ecart = ecart_a(grille, largeur, echelle)
    ecart = grille.gap if ecart is None else ecart
    colonnes = 1
    while (colonnes + 1) * plancher + colonnes * ecart <= place:
        colonnes += 1
    if items:
        colonnes = min(colonnes, items)
    return colonnes


def padding_du_selecteur(racine: Path, selecteur: str) -> str | None:
    """Le remplissage horizontal écrit par la règle **de base** de ce sélecteur.

    Une grille convertie en `flex` n'a plus de `grid-template-columns` : elle a
    donc disparu de `lire_grilles`, et son remplissage avec elle. Or c'est lui
    qui décide de la largeur utile de ses enfants — `.learning-work-panel` valait
    713 px de large et ne laissait que 652 px à ses deux panneaux.
    """
    chemin = racine / FEUILLE
    if not chemin.is_file():
        return None
    for selecteurs, corps, largeur_max, largeur_min, _ in decouper(sans_commentaires(chemin.read_text(encoding="utf-8"))):
        if largeur_max is not None or largeur_min is not None:
            continue
        if not any(s == selecteur for s in selecteurs):
            continue
        trouve = padding_horizontal(corps)
        if trouve:
            return trouve
    return None


def completer_grille(grille: Grille, racine: Path) -> None:
    """Inscrit sur une grille synthétique le remplissage que la feuille lui écrit."""
    if grille.padding_expr:
        return
    trouve = padding_du_selecteur(racine, grille.selecteur)
    if trouve:
        grille.padding_expr = trouve
        grille.padding_lu = padding_horizontal_px(trouve, CONTENU_DEFAUT) is not None


def bandes_de_retour(grille: Grille, base: float, echelle: float = 1.0) -> list[dict]:
    """Les largeurs où la grille **perd** une colonne en gagnant de la place.

    C'est l'invariant qui compte vraiment, et il ne dépend d'aucune cascade
    d'avant : quand la fenêtre s'élargit, une grille qui replie ne peut pas
    passer de deux colonnes à une. Or le 1er novembre 2026, la gouttière du
    conteneur passant de `2rem` à `3rem` à 761 px, le conteneur **rétrécit** de
    16 px quand la fenêtre grandit d'un pixel : une base mal choisie produit
    alors exactement cette marche arrière — celle que l'ancien contrôle appelait
    « une bande d'un pixel » sans jamais la nommer ainsi.
    """
    bandes: list[dict] = []
    encours: dict | None = None
    precedent = colonnes_en_flex(grille, LARGEURS_FINES[0], base, grille.items, echelle)
    for largeur in LARGEURS_FINES[1:]:
        colonnes = colonnes_en_flex(grille, largeur, base, grille.items, echelle)
        if colonnes < precedent:
            if encours is not None and encours["fin"] == largeur - 1 and encours["apres"] == colonnes:
                encours["fin"] = largeur
            else:
                encours = {
                    "debut": largeur,
                    "fin": largeur,
                    "avant": precedent,
                    "apres": colonnes,
                }
                bandes.append(encours)
        else:
            encours = None
        precedent = colonnes
    return bandes


def bandes_de_changement(grille: Grille, plancher: float | None = None) -> list[dict]:
    """Où, et de combien, une conversion changerait le nombre de colonnes.

    Un compte de largeurs (« 29 sur 233 ») ne dit pas **où**. Le 31 octobre
    2026, deux conversions avaient un compte voisin et des conséquences très
    différentes : treize largeurs sur 233 pour une grille qui passait de deux
    colonnes à deux colonnes ne changeaient presque rien, alors qu'une grille
    qui passait de **une à deux** colonnes sur la même plage redessinait la
    page. La plage, elle, se lit : « de 704 à 1 032 px, une colonne devient
    deux ».
    """
    valeur = plancher if plancher is not None else plancher_de(grille)
    if valeur is None or valeur <= 0:
        return []
    bandes: list[dict] = []
    encours: dict | None = None
    for largeur in LARGEURS:
        flex = colonnes_en_flex(grille, largeur, valeur, grille.items)
        cascade = colonnes_de_la_cascade(grille, largeur)
        if flex == cascade:
            encours = None
            continue
        if encours is not None and encours["cascade"] == cascade and encours["flex"] == flex:
            encours["fin"] = largeur
            continue
        encours = {"debut": largeur, "fin": largeur, "cascade": cascade, "flex": flex}
        bandes.append(encours)
    return bandes


#: Une piste écrite en pixels **nus** : `44px`, pas `minmax(44px, 1fr)`.
PISTE_PX = re.compile(r"^[\d.]+px$")

#: Un plafond : les deux bornes d'un `minmax(...)` en longueurs, sans `fr`.
PLAFOND = re.compile(r"^minmax\(\s*([\d.]+)(px|rem)\s*,\s*([\d.]+)(px|rem)\s*\)$")


def pistes_en_px(valeur: str) -> list[str]:
    """Les pistes que la taille du texte ne fera jamais bouger.

    `44px 1fr` réserve 44 px au numéro, quoi qu'il arrive. `2.75rem 1fr`
    réserve 44 px à 100 % — mais 57 px quand la personne règle le texte à
    130 %, ce que le site sait faire (`html.texte-tres-agrandi`). La première
    écriture ignore ce réglage ; la seconde le suit. C'est la seule différence,
    et elle n'apparaît sur aucune capture d'écran par défaut.
    """
    return [p.strip() for p in pistes(valeur) if PISTE_PX.fullmatch(p.strip())]


def plafonds(valeur: str) -> list[str]:
    """Les pistes à plafond : `minmax(230px, 300px)`.

    Elles ne sont pas des colonnes d'icône. Un `flex` ne sait pas plafonner un
    élément qui rétrécit, donc la conversion demanderait une `max-width` — et
    une autre décision : sur une seule colonne, la grille étire ce panneau à
    toute la largeur, alors qu'un élément flex de base 300 px y resterait à
    300 px. Deux comportements, pas un.
    """
    return [p.strip() for p in pistes(valeur) if PLAFOND.fullmatch(p.strip())]


def largeur_plafonnee(grille: Grille, valeur: str) -> dict | None:
    """Ce que vaut, largeur par largeur, la piste qui porte un plafond.

    Une piste `minmax(230px, 300px)` à côté d'une piste `1fr` ne se contente
    pas de plafonner : elle prend sa **borne haute** tant que la place restante
    le permet, puisque l'autre piste peut descendre à zéro. Rendre les deux
    bornes et la valeur observée dit si la borne basse sert encore à quelque
    chose — ou si elle est un garde-fou que la cascade n'atteint jamais.
    """
    pistes_plafonnees = plafonds(valeur)
    if len(pistes_plafonnees) != 1 or len(pistes(valeur)) != 2:
        return None
    trouve = PLAFOND.fullmatch(pistes_plafonnees[0])
    if not trouve:
        return None
    bas = float(trouve.group(1)) * (RACINE_PX if trouve.group(2) == "rem" else 1)
    haut = float(trouve.group(3)) * (RACINE_PX if trouve.group(4) == "rem" else 1)
    mesurees = []
    for largeur in LARGEURS:
        if colonnes_de_la_cascade(grille, largeur) != 2:
            continue
        gap = ecart_a(grille, largeur)
        gap = grille.gap if gap is None else gap
        place = conteneur(largeur) - gap
        mesurees.append(min(haut, max(bas, place)))
    if not mesurees:
        return None
    return {
        "bas": bas,
        "haut": haut,
        "mini": min(mesurees),
        "maxi": max(mesurees),
        "largeurs": len(mesurees),
        "borne_basse_atteinte": min(mesurees) <= bas + 0.5,
    }


def plancher_de(grille: Grille) -> float | None:
    """Le plus grand minimum de piste d'une grille à pistes souples, ou `None`."""
    natures = [nature_piste(piste) for piste in pistes(grille.valeur_asymetrique)]
    if not natures or any(nature != "souple" for nature, _, _ in natures):
        return None
    valeur = max((minimum or 0.0) for _, minimum, _ in natures)
    return valeur if valeur > 0 else None


#: Taille de la police racine, en pixels : la valeur que le navigateur applique
#: à `1rem` quand la personne n'a rien changé. Les bases écrites en `em` s'y
#: rapportent — c'est ce qui les fait suivre la taille du texte.
RACINE_PX = 16.0


def bandes_fines(grille: Grille, base: float) -> list[dict]:
    """Les bandes de changement au pixel près, avec la base réellement écrite.

    `bandes_de_changement` balaie au pas de 10 px : elle ne voit pas une bande
    d'un ou deux pixels, et c'est exactement là que se cachaient trois erreurs.
    """
    bandes: list[dict] = []
    encours: dict | None = None
    for largeur in LARGEURS_FINES:
        flex = colonnes_en_flex(grille, largeur, base, grille.items)
        cascade = colonnes_de_la_cascade(grille, largeur)
        if flex == cascade:
            encours = None
            continue
        if encours is not None and encours["cascade"] == cascade and encours["flex"] == flex:
            encours["fin"] = largeur
            continue
        encours = {"debut": largeur, "fin": largeur, "cascade": cascade, "flex": flex}
        bandes.append(encours)
    return bandes


def fenetre_de_base(grille: Grille, repli: int) -> dict | None:
    """Les bases, en pixels, qui replient exactement là où le palier repliait.

    Un palier est une marche : sous `repli` la grille montrait une colonne, à
    `repli + 1` elle en montrait deux. Une base de `flex` n'a qu'un seuil, et
    ce seuil tombe là où `n × base + (n-1) × écart` cesse de tenir dans le
    conteneur. La condition s'écrit donc en deux inégalités, et la fenêtre qui
    en sort est **étroite** : 0,46 px pour `.hero-grid`. Écrire 20.4em au lieu
    de 20.37em sortait de la fenêtre d'un tiers de pixel — et créait une bande
    de 1 px que le balayage au pas de 10 px ne voyait pas.

    Rend `None` quand la fenêtre est vide (l'écart varie avec la largeur, et
    `clamp` peut la décaler plus vite que le conteneur ne grandit) : aucune
    base ne reproduit alors le palier, et il faut le dire.
    """
    natures = [nature_piste(piste) for piste in pistes(grille.valeur_asymetrique)]
    n = len(natures)
    if n < 2 or not all(nature == "souple" for nature, _, _ in natures):
        return None

    def eclatement(largeur: int) -> float:
        ecart = ecart_a(grille, largeur)
        return grille.gap if ecart is None else ecart

    haut = (conteneur(repli + 1) - (n - 1) * eclatement(repli + 1)) / n
    bas = (conteneur(repli) - (n - 1) * eclatement(repli)) / n
    if haut <= bas:
        return None
    return {"bas": bas, "haut": haut, "largeur": haut - bas}


def repli_de(grille: Grille) -> int | None:
    """La largeur sous laquelle la cascade actuelle ne montre plus qu'une colonne.

    Rend `None` quand la cascade a **plusieurs** marches (`.footer-grid` passe
    de quatre colonnes à deux, puis à une) : une base de `flex` n'a qu'un seuil,
    et deux marches ne se reproduisent pas avec un seul nombre.
    """
    marches = [
        regle.largeur_max
        for regle in grille.regles
        if regle.largeur_max is not None
        # Une règle de palier peut dire « une colonne » de deux façons : par un
        # nombre (`repeat(1, …)` lu en `colonnes`) ou par une valeur d'une seule
        # piste (`minmax(0, 1fr)`). Ne lire que la première faisait répondre
        # « aucune base » à une grille dont la fenêtre se calculait pourtant.
        and (regle.colonnes == 1 or len(pistes(regle.valeur)) == 1)
    ]
    return max(marches) if len(set(marches)) == 1 and marches else None


def base_en_em(dans_fenetre: dict, racine_px: float = RACINE_PX) -> dict:
    """La plus grande écriture en `em` qui reste **dans** la fenêtre.

    L'arrondi va vers le bas : la valeur écrite doit rester sous la borne haute,
    sinon le `flex` attend un tiers de pixel de plus que le palier et laisse une
    bande d'un pixel. Le 31 octobre 2026, l'arrondi allait vers le haut « pour ne
    pas rendre une base plus petite que celle qui venait d'être vérifiée » — le
    raisonnement était incomplet : plus petite que la borne haute, plus grande
    que la borne basse, voilà la seule condition.
    """
    centiemes = math.floor(dans_fenetre["haut"] / racine_px * 100)
    valeur = centiemes / 100
    return {
        "em": valeur,
        "px": valeur * racine_px,
        "expr": f"{valeur:.2f}".rstrip("0").rstrip(".") + "em",
        # Une fenêtre plus étroite qu'un centième de `em` (0,16 px) n'a aucune
        # écriture valable : le dire vaut mieux que proposer un chiffre dehors.
        "dans_fenetre": dans_fenetre["bas"] < valeur * racine_px <= dans_fenetre["haut"],
    }


def plancher_de_compromis(grille: Grille, pas: float = 0.5) -> dict | None:
    """La base la plus petite qui **reproduit** le repli actuel, et son écriture en `em`.

    Le 31 octobre 2026, trois conversions ont été acceptées en créant une plage
    où le nombre de colonnes change (`600–760 px`). C'est défendable, mais ce
    n'est pas la seule issue : une base plus large déplace le repli sans
    supprimer de règle de grille. La question n'est donc plus « convertir ou
    non », elle devient « avec quelle base, et qu'est-ce que cela coûte ».

    Cette fonction cherche la plus **petite** base qui laisse intact le nombre
    de colonnes à toutes les largeurs mesurées — la moins gourmande en largeur
    de colonne, donc celle qui change le moins le dessin. Rend `None` quand
    aucune base ne le fait : le dire vaut mieux que proposer un chiffre qui ne
    reproduit rien.

    La base est rendue aussi en `em` (`px / 16`) : écrite ainsi dans la feuille,
    elle **suit la taille du texte** — un réglage à 130 % élargit la base de
    30 %, donc avance le repli, ce qu'aucune condition de largeur d'écran ne
    sait faire.
    """
    reference = [colonnes_de_la_cascade(grille, largeur) for largeur in LARGEURS]
    reference_fine = [colonnes_de_la_cascade(grille, largeur) for largeur in LARGEURS_FINES]

    def reproduit(base: float, largeurs: list[int], attendus: list[int]) -> bool:
        return all(
            colonnes_en_flex(grille, largeur, base, grille.items) == attendu
            for largeur, attendu in zip(largeurs, attendus)
        )

    # Une seule marche : la fenêtre se calcule exactement. La recherche par pas
    # de 0,5 px, elle, ratait la fenêtre de `.simulateur-intro` (0,48 px de
    # large) : 456,0 était juste en dessous de la borne basse et 456,5 juste
    # au-dessus de la haute. Une recherche qui tombe à côté d'une fenêtre étroite
    # conclut « aucune base » — et ce refus-là serait faux.
    marche = repli_de(grille)
    if marche is not None:
        fenetre = fenetre_de_base(grille, marche)
        if fenetre:
            candidate = base_en_em(fenetre)
            if reproduit(candidate["px"], LARGEURS_FINES, reference_fine):
                return {
                    "px": round(candidate["px"], 2),
                    "em": candidate["em"],
                    "expr": candidate["expr"],
                    "verifie_au_pixel": True,
                }
            return None

    haut = conteneur(max(LARGEURS)) / 2 + 1
    base = grille.gap
    while base < haut:
        # Le balayage grossier écarte vite les mauvaises bases ; le balayage au
        # pixel tranche. Depuis le 1er novembre 2026, une base validée seulement
        # au pas de 10 px peut laisser une bande d'un pixel : c'est arrivé trois
        # fois sur les six grilles converties la veille.
        if reproduit(base, LARGEURS, reference) and reproduit(
            base, LARGEURS_FINES, reference_fine
        ):
            # L'écriture en `em` est arrondie **vers le bas**, puis vérifiée au
            # pixel : la valeur écrite doit rester sous la borne haute de la
            # fenêtre, sinon le `flex` attend un tiers de pixel de plus que le
            # palier. L'arrondi au-dessus du 31 octobre 2026 avait créé
            # exactement cette bande-là.
            centiemes = math.floor(base / RACINE_PX * 100)
            for recul in range(0, 6):
                candidat = (centiemes - recul) / 100
                if candidat <= 0:
                    break
                if reproduit(candidat * RACINE_PX, LARGEURS_FINES, reference_fine):
                    return {
                        "px": round(candidat * RACINE_PX, 2),
                        "em": candidat,
                        "expr": f"{candidat:.2f}".rstrip("0").rstrip(".") + "em",
                        "verifie_au_pixel": True,
                    }
            return None
        base += pas
    return None


def pistes_des_inegales(
    grilles: dict[str, Grille], capacites: dict[str, dict] | None = None
) -> list[dict]:
    """Ce qu'un `flex-wrap` exprimerait d'une grille à pistes inégales — et ce qu'il ne peut pas.

    Trois réponses, et deux valent d'être dites :

    - `contenu` : une piste `auto` ou `max-content` fait dépendre le repli du
      **texte**, pas de l'arithmétique. Aucun modèle ne peut trancher sans
      navigateur ; le script le dit au lieu de proposer un chiffre.
    - `proportion` : toutes les pistes sont souples avec un plancher en pixels.
      Un `flex: <g> 1 <plancher>` par élément reproduit le rapport, et le repli
      tombe quand `n × plancher + (n-1) × écart` dépasse le conteneur. L'écart
      avec la cascade actuelle est calculable — donc la décision peut se prendre
      sur des nombres.
    - `plafond` : une piste `minmax(230px, 300px)`. Un `flex` ne plafonne pas
      un élément qui rétrécit, et la conversion devrait décider d'un second
      comportement : pleine largeur quand le panneau est seul sur sa ligne. Le
      modèle le dit au lieu de proposer une base.
    - `badge` : une piste fixe (`44px`) à côté d'une piste souple — la colonne
      d'un numéro ou d'une icône. Ces grilles n'ont **aucun palier** : elles ne
      se replient jamais, il n'y a donc rien à rendre dynamique. Le seul défaut
      qui reste est l'unité : en `px`, la colonne ne suit pas la taille du
      texte ; en `rem`, si.
    - `fixe` : des pistes en pixels ; rien à rendre dynamique.
    - `sans-plancher` : des `fr` sans plancher en pixels
      (`minmax(0,1.35fr) minmax(0,1fr)`). Rien ne dépend du texte, mais le
      repli vient d'un palier : une base **choisie** peut le remplacer, à
      condition d'être vérifiée au pixel.
    - `decor` : des `fr` sans plancher et **sans palier** — un aperçu
      schématique de présentation. Ses colonnes ne changent jamais.
    """
    capacites = capacites or {}
    resultats = []
    for grille in asymetriques(grilles):
        items = (capacites.get(grille.selecteur) or {}).get("items") or []
        grille.items = max(items) if items else 0
        valeur = grille.valeur_asymetrique
        if valeur.startswith("repeat("):
            resultats.append({"selecteur": grille.selecteur, "forme": "motif", "valeur": valeur})
            continue
        natures = [nature_piste(p) for p in pistes(valeur)]
        if not natures:
            resultats.append({"selecteur": grille.selecteur, "forme": "illisible", "valeur": valeur})
            continue
        if any(nature == "contenu" for nature, _, _ in natures):
            resultats.append({"selecteur": grille.selecteur, "forme": "contenu", "valeur": valeur})
            continue
        # `minmax(230px, 300px)` : la colonne a un **plafond**. C'est le seul
        # cas où `flex` ne sait pas faire sans une `max-width`, et où il faudrait
        # décider d'un second comportement (pleine largeur quand le panneau est
        # seul sur sa ligne). Dit, pas deviné.
        if plafonds(valeur) or any(nature == "borne" for nature, _, _ in natures):
            resultats.append(
                {
                    "selecteur": grille.selecteur,
                    "forme": "plafond",
                    "valeur": valeur,
                    "plafonds": plafonds(valeur),
                }
            )
            continue
        # Une piste fixe à côté d'une piste souple : `44px 1fr` réserve la
        # colonne d'un numéro ou d'une icône. Le 1er novembre 2026, ces grilles
        # s'appelaient « borne » — le mot d'un plafond — alors qu'aucune n'en
        # avait, et qu'aucune n'a de palier : elles ne se replient jamais. Le
        # seul défaut qui leur reste est l'unité : en px, la colonne ne suit pas
        # la taille du texte.
        fixes = [p.strip() for p in pistes(valeur) if re.fullmatch(r"[\d.]+(?:px|rem)", p.strip())]
        if fixes:
            resultats.append(
                {
                    "selecteur": grille.selecteur,
                    "forme": "badge",
                    "valeur": valeur,
                    "fixes": fixes,
                    "px": pistes_en_px(valeur),
                    "paliers": paliers(grille),
                }
            )
            continue
        if all(nature == "fixe" for nature, _, _ in natures):
            resultats.append({"selecteur": grille.selecteur, "forme": "fixe", "valeur": valeur})
            continue
        plancher = max((minimum or 0.0) for nature, minimum, _ in natures if nature == "souple")
        if plancher <= 0:
            # Aucune piste n'a de plancher : les colonnes ne dépendent que de la
            # place. Le 1er novembre 2026, ces grilles tombaient dans « contenu »
            # avec les vraies pistes `auto` — un mot qui dit « le texte décide »
            # là où rien ne dépend du texte. Deux cas, et un seul a un travail :
            #   .sans-plancher : un palier décide du repli, et seule une base
            #                    choisie peut le remplacer ;
            #   .decor        : aucun palier, les colonnes ne changent jamais.
            conditions = paliers(grille)
            resultats.append(
                {
                    "selecteur": grille.selecteur,
                    "forme": "sans-plancher" if conditions else "decor",
                    "valeur": valeur,
                    "paliers": conditions,
                    "compromis": plancher_de_compromis(grille) if conditions else None,
                }
            )
            continue
        # `flex-wrap` ne crée pas d'élément : une grille à deux panneaux n'en
        # affichera jamais trois, même si deux planchers de 280 px tiennent trois
        # fois dans 1 160 px. Le 31 octobre 2026, l'oubli de cette borne avait
        # déjà produit un faux rapport sur les grilles `auto-fit` ; il est évité
        # ici avant d'écrire la moindre ligne de CSS.
        items = grille.items
        ecarts = sum(
            1
            for largeur in LARGEURS
            if colonnes_en_flex(grille, largeur, plancher, items)
            != colonnes_de_la_cascade(grille, largeur)
        )
        resultats.append(
            {
                "selecteur": grille.selecteur,
                "forme": "proportion",
                "valeur": valeur,
                "plancher": int(plancher),
                "ecarts": ecarts,
            }
        )
    return resultats


def etat(grilles: dict[str, Grille], capacites: dict[str, dict] | None = None) -> list[dict]:
    """Le tableau : grille, colonnes de base, paliers restants, recommandation."""
    capacites = capacites or {}
    lignes = []
    for grille in convertibles(grilles):
        selecteur = grille.selecteur
        conditions = paliers(grille)
        entree = {
            "selecteur": selecteur,
            "colonnes": colonnes_de_conception(grille),
            "gap": grille.gap,
            "paliers": conditions,
            "source": grille.source,
            "items": (capacites.get(selecteur) or {}).get("items", []),
            "apparies": (capacites.get(selecteur) or {}).get("apparies", False),
        }
        if conditions:
            # La consigne vient de la règle, jamais d'une recherche d'ajustement.
            minimum = minimum_recommande(grille, capacites.get(selecteur))
            if minimum is None:
                entree["minimum_recommande"] = None
            else:
                nombre, maximal, _ = ecart(grille, minimum)
                entree["minimum_recommande"] = minimum
                entree["ecarts"] = nombre
                entree["ecart_maximal"] = maximal
                entree["carte_minimale"] = round(carte_minimale(grille, minimum), 1)
        lignes.append(entree)
    return lignes


def rapport(
    lignes: list[dict],
    inegales: list[Grille] | None = None,
    grilles: dict[str, Grille] | None = None,
) -> str:
    avec = [ligne for ligne in lignes if ligne["paliers"]]
    sorties = [
        f"{len(lignes)} grilles à pistes égales fixent leur nombre de colonnes dans {FEUILLE} ; "
        f"{len(avec)} le font encore par un palier de largeur.",
        "",
    ]
    mortes = declarations_mortes(grilles or {})
    sorties.append(
        f"{len(mortes)} déclaration(s) sous condition de largeur ne décide(nt) rien : "
        + ("aucune" if not mortes else ", ".join(m["selecteur"] for m in mortes))
        + "."
    )
    sorties.append("")
    if inegales:
        sorties.append(
            f"{len(inegales)} grilles à pistes inégales (texte + bouton, formulaire, sommaire) "
            "ne se convertissent pas sans changer le dessin : elles ne sont pas comptées ci-dessus "
            "et gardent leurs paliers."
        )
        sorties.append("")
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
        if ligne.get("items"):
            sorties.append(
                f"    pages : {max(ligne['items'])} élément(s) au plus par grille"
                + (
                    " — liste de paires (`dl`), une troisième colonne la couperait"
                    if ligne.get("apparies")
                    else ""
                )
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


def grille_synthetique(selecteur: str, valeur: str, gap_expr: str) -> Grille:
    """Reconstruit la grille **d'avant** à partir de ce que le registre déclare.

    Une fois convertie, la grille n'a plus de `grid-template-columns` : le
    modèle ne peut plus mesurer l'écart qu'elle a coûté. Le registre garde donc
    l'ancienne valeur, et le contrôle **recalcule** l'écart au lieu de croire le
    nombre écrit — sans quoi ce nombre serait un total recopié à la main.
    """
    grille = Grille(selecteur=selecteur, gap_expr=gap_expr)
    valeur_gap = mesure_en_px(gap_expr, fenetre_maximale())
    grille.gap = round(valeur_gap, 2) if valeur_gap is not None else 16.0
    grille.gap_lu = valeur_gap is not None
    grille.regles = [Regle([selecteur], valeur, None, None, None, None, 1, 0)]
    # La valeur d'avant est celle de la grille : sans ces deux champs,
    # `fenetre_de_base` ne saurait pas combien de pistes compter et répondrait
    # « aucune base ne reproduit ce repli » — un refus juste, pour une mauvaise
    # raison, exactement le défaut reproché au relevé la veille.
    grille.asymetrique = True
    grille.valeur_asymetrique = valeur
    return grille


def flex_attendu(valeur: str, base: float | None = None, base_expr: str = "") -> list[str]:
    """Les déclarations `flex` que la règle donne, une par piste, sans ajustement.

    Le plancher d'une piste est son minimum déclaré ; une piste sans minimum
    reçoit le plus grand plancher des autres, pour que le repli tombe quand les
    deux ne tiennent plus — et non quand le premier panneau rétrécit à zéro. Le
    coefficient de croissance est le `fr` : c'est lui qui porte le rapport.
    """
    natures = [nature_piste(piste) for piste in pistes(valeur)]
    if any(nature != "souple" for nature, _, _ in natures) or not natures:
        return []
    if base_expr:
        # Une base écrite en `em` suit la taille du texte : c'est cette écriture
        # qu'on exige dans la feuille, pas un nombre de pixels figé.
        return [f"{(maximum or 1.0):g} 1 {base_expr}" for _, _, maximum in natures]
    planchers = [minimum or 0.0 for _, minimum, _ in natures]
    commun = max(planchers) or 0.0
    if commun <= 0:
        return []
    attendus = []
    for minimum, maximum in ((minimum or 0.0, maximum) for _, minimum, maximum in natures):
        base = minimum if minimum > 0 else commun
        attendus.append(f"{maximum:g} 1 {base:g}px")
    return attendus


def _sans_zero_inutile(corps: str) -> str:
    """`.8` et `0.8` sont la même déclaration : la comparaison ne doit pas en dépendre.

    Le contrôle cherchait la chaîne exacte `flex: 0.8 1 260px` là où la feuille
    écrivait `flex: .8 1 260px` — une faute de forme, pas de fond. La feuille
    écrit `.95fr` depuis toujours ; le contrôle apprend la même tolérance.
    """
    return re.sub(r"(?<![\d.])\.(\d)", r"0.\1", corps)


def verifier_flex(racine: Path, registre: dict) -> list[str]:
    """Contrôle les grilles converties en `flex-wrap`.

    Quatre fautes, et chacune a coûté quelque chose : une règle de base qui
    n'est plus `flex` avec `flex-wrap` (le repli disparaîtrait), des
    déclarations `flex` qui ne sont plus celles de la règle (le rapport entre
    colonnes dérive), une déclaration d'écart recopiée à la main au lieu d'être
    recalculée, et — la plus discrète — une présentation qui impose encore
    `grid-template-columns` à cette grille : sur un conteneur flex, elle est
    sans effet, et la présentation ne replie plus rien.
    """
    entrees = registre.get("grille_flex", [])
    if not entrees:
        return []
    chemin = racine / FEUILLE
    if not chemin.is_file():
        raise SourceIllisible(f"feuille de style introuvable : {FEUILLE}")
    texte = sans_commentaires(chemin.read_text(encoding="utf-8"))
    regles = decouper(texte)
    erreurs: list[str] = []
    enfants = enfants_des_grilles(
        racine, [entree.get("selecteur") or "" for entree in entrees if entree.get("selecteur")]
    )
    for entree in entrees:
        selecteur = entree.get("selecteur") or ""
        if not selecteur:
            erreurs.append("grille_flex sans sélecteur")
            continue
        base = [
            corps
            for selecteurs, corps, lmax, lmin, _ in regles
            if selecteur in selecteurs and lmax is None and lmin is None
        ]
        if not base:
            erreurs.append(f"{selecteur} : aucune règle de base trouvée dans {FEUILLE}")
            continue
        corps_base = re.sub(r"\s+", " ", base[0])
        if "display: flex" not in corps_base and "display:flex" not in corps_base:
            erreurs.append(f"{selecteur} : sa règle de base n'est plus `display: flex`")
        if "flex-wrap: wrap" not in corps_base and "flex-wrap:wrap" not in corps_base:
            erreurs.append(f"{selecteur} : sa règle de base n'a plus `flex-wrap: wrap` — le repli disparaît")
        if "grid-template-columns" in corps_base:
            erreurs.append(f"{selecteur} : sa règle de base déclare encore `grid-template-columns`")

        valeur = entree.get("grille_avant") or ""
        gap_expr = entree.get("gap_avant") or ""
        # Une base écrite en `em` (31 octobre 2026) : elle ne vient pas du
        # minimum déclaré, elle est **choisie** pour que le repli tombe au même
        # endroit que le palier qu'elle remplace — et pour suivre la taille du
        # texte, ce qu'aucune condition de largeur d'écran ne sait faire. Le
        # registre doit donc dire les deux : l'écriture et le nombre de pixels
        # qu'elle vaut à taille de texte normale.
        base_expr = entree.get("plancher_expr") or ""
        base_px = entree.get("plancher_px")
        if base_expr:
            if not re.fullmatch(r"[\d.]+em", base_expr):
                erreurs.append(
                    f"{selecteur} : `plancher_expr` ({base_expr}) n'est pas une longueur en em"
                )
            elif not isinstance(base_px, (int, float)):
                erreurs.append(
                    f"{selecteur} : `plancher_expr` sans `plancher_px` — la valeur en pixels "
                    "n'est pas vérifiable"
                )
            else:
                mesure = float(base_expr[:-2]) * RACINE_PX
                # Tolérance d'un centième de pixel, pas d'un demi : la fenêtre
                # des bases qui replient au bon endroit fait 0,46 px, et le
                # 1er novembre 2026 un écart de 0,14 px entre `21.29em`
                # (340,64 px) et le `plancher_px` déclaré (340,5) est passé
                # sous une tolérance de 0,5 px — en cachant une bande réelle.
                if abs(mesure - float(base_px)) > 0.01:
                    erreurs.append(
                        f"{selecteur} : `{base_expr}` vaut {mesure:.2f} px, le registre déclare "
                        f"{float(base_px):g} px — la base mesurée est celle qui est écrite"
                    )
        attendus = flex_attendu(valeur, base_expr=base_expr)
        if not attendus:
            erreurs.append(
                f"{selecteur} : `grille_avant` n'est pas une suite de pistes souples "
                f"({valeur[:50]}) — le registre ne décrit pas ce qui a été converti"
            )
        for attendu in attendus:
            trouve = any(
                selecteurs
                and any(s.startswith(selecteur) for s in selecteurs)
                and f"flex: {attendu}" in _sans_zero_inutile(re.sub(r"\s+", " ", corps))
                for selecteurs, corps, _, _, _ in regles
            )
            if not trouve:
                erreurs.append(
                    f"{selecteur} : aucune règle n'écrit `flex: {attendu}` — "
                    "la règle donne ce rapport, le registre dit qu'il a été appliqué"
                )
        if not any(
            any(s.startswith(selecteur) for s in selecteurs)
            and "min-width: 0" in re.sub(r"\s+", " ", corps)
            for selecteurs, corps, _, _, _ in regles
        ):
            erreurs.append(
                f"{selecteur} : ses panneaux n'ont pas `min-width: 0` — en flex, un "
                "panneau refuse de rétrécir sous son contenu, ce que la grille autorisait"
            )

        # Écart recalculé, jamais recopié.
        if valeur and gap_expr:
            synthetique = grille_synthetique(selecteur, valeur, gap_expr)
            if base_expr and isinstance(base_px, (int, float)):
                synthetique.base_flex = float(base_expr[:-2]) * RACINE_PX
            mesure = ecart_de_largeur(synthetique)
            declare_px = float(entree.get("ecart_max_px", -1))
            declare_part = float(entree.get("ecart_part", -1))
            if abs(declare_px - mesure["px"]) > 1.5:
                erreurs.append(
                    f"{selecteur} : écart déclaré {declare_px:g}px, la règle en donne "
                    f"{mesure['px']:.1f}px"
                )
            if abs(declare_part - mesure["part"]) > 0.005:
                erreurs.append(
                    f"{selecteur} : écart déclaré {declare_part:.3f}, la règle en donne "
                    f"{mesure['part']:.3f} de la colonne"
                )

        # La promesse « aucune largeur ne change de nombre de colonnes » se
        # vérifie, elle ne s'affirme pas. Le 31 octobre 2026, `.hero-grid` a été
        # converti avec une base choisie pour reproduire exactement son ancien
        # repli ; rien dans la feuille ne permettait de le contrôler, puisque la
        # règle de palier avait disparu avec la conversion. Le registre garde
        # donc la largeur du repli d'avant (`repli_avant_px`), et le contrôle
        # reconstruit la cascade d'avant pour confronter les deux.
        #
        # Le 1er novembre 2026, cette promesse est tombée pour six grilles sur
        # onze : avec la **vraie** gouttière, reproduire un repli à 760 px exige
        # une base supérieure à 333,6 px à 760 px (conteneur 728) et inférieure
        # à 326,06 px à 761 px (conteneur 713) — l'intersection est vide, parce
        # que le conteneur rétrécit de 16 px quand la fenêtre grandit d'un pixel.
        # Une promesse irréalisable ne s'adoucit pas, elle se retire : ces
        # grilles déclarent `repli_refuse_px`, le contrôle **démontre** alors que
        # la fenêtre est vide, et exige à la place l'invariant qui compte
        # vraiment — une grille ne perd jamais une colonne en gagnant de la place.
        refuse = entree.get("repli_refuse_px")
        if refuse is not None:
            if not isinstance(refuse, int) or refuse <= 0:
                erreurs.append(
                    f"{selecteur} : `repli_refuse_px` ({refuse!r}) n'est pas une largeur en pixels"
                )
            elif not (base_expr and isinstance(base_px, (int, float))):
                erreurs.append(
                    f"{selecteur} : `repli_refuse_px` sans base déclarée — le refus porte "
                    "sur une base qui n'est pas écrite"
                )
            else:
                avant = grille_synthetique(selecteur, valeur, gap_expr)
                completer_grille(avant, racine)
                avant.items = len(attendus)
                fenetre = fenetre_de_base(avant, refuse)
                if fenetre is not None:
                    erreurs.append(
                        f"{selecteur} : le registre déclare irréalisable le repli à {refuse} px, "
                        f"or une base y arrive — celles de {fenetre['bas']:.2f} à "
                        f"{fenetre['haut']:.2f} px. Le refus n'a plus d'objet : c'est la "
                        "déclaration de base qu'il faut revoir"
                    )
            if entree.get("repli_avant_px") is not None:
                erreurs.append(
                    f"{selecteur} : `repli_avant_px` et `repli_refuse_px` ensemble — "
                    "le repli est soit reproduit, soit démontré irréalisable, pas les deux"
                )

        repli = entree.get("repli_avant_px")
        if repli is not None:
            if not isinstance(repli, int) or repli <= 0:
                erreurs.append(
                    f"{selecteur} : `repli_avant_px` ({repli!r}) n'est pas une largeur en pixels"
                )
            elif not (base_expr and isinstance(base_px, (int, float))):
                erreurs.append(
                    f"{selecteur} : `repli_avant_px` sans base déclarée — la promesse "
                    "« le repli ne change pas » porte sur une base qui n'est pas écrite"
                )
            else:
                avant = grille_synthetique(selecteur, valeur, gap_expr)
                completer_grille(avant, racine)
                avant.items = len(attendus)
                avant.regles.append(
                    Regle([selecteur], "minmax(0, 1fr)", None, None, repli, None, 2, 1)
                )
                ecrite = float(base_expr[:-2]) * RACINE_PX
                avant.base_flex = ecrite
                bandes = bandes_fines(avant, ecrite)
                if bandes:
                    premiere = bandes[0]
                    fenetre = fenetre_de_base(avant, repli)
                    ou = (
                        f"la fenêtre des bases qui replient à {repli} px va de "
                        f"{fenetre['bas']:.2f} à {fenetre['haut']:.2f} px, et `{base_expr}` "
                        f"en vaut {ecrite:.2f}"
                        if fenetre
                        else "aucune base ne reproduit ce repli"
                    )
                    erreurs.append(
                        f"{selecteur} : `repli_avant_px = {repli}` annoncé comme reproduit, "
                        f"mais à {premiere['debut']} px (bande {premiere['debut']}–{premiere['fin']}) "
                        f"la grille d'avant montrait {premiere['cascade']} colonne(s) et le flex "
                        f"en donne {premiere['flex']} — {ou} : la base ne reproduit pas le repli"
                    )

        # L'invariant qui survit à tout le reste, et qui ne présume aucune
        # cascade d'avant : **une grille ne perd jamais une colonne en gagnant de
        # la place**. Il se vérifie aux trois tailles de texte, parce qu'une base
        # en `em` et un écart en `rem` bougent tous les deux avec le réglage de la
        # personne — et qu'aucune mesure d'écran ne peut le savoir à sa place.
        if base_expr and isinstance(base_px, (int, float)) and attendus:
            base_em = float(base_expr[:-2]) if base_expr.endswith("em") else None
            synthetique = grille_synthetique(selecteur, valeur, gap_expr)
            completer_grille(synthetique, racine)
            synthetique.items = len(attendus)
            for echelle in (1.0, 1.15, 1.3):
                base_echelle = (
                    base_em * RACINE_PX * echelle if base_em is not None else float(base_px)
                )
                retours = bandes_de_retour(synthetique, base_echelle, echelle)
                if retours:
                    premiere = retours[0]
                    erreurs.append(
                        f"{selecteur} : à {premiere['debut']} px et texte ×{echelle:g}, la grille "
                        f"passe de {premiere['avant']} à {premiere['apres']} colonne(s) alors que "
                        f"la fenêtre s'élargit (bande {premiere['debut']}–{premiere['fin']}) — "
                        "une base trop grande pour la gouttière de ce côté du seuil"
                    )

        # Plafond en `width` sur un enfant : en flex, il ne s'applique pas.
        # `flex-basis: 100%` sur les présentations remplace la largeur de la
        # boîte ; le plafond qui rendait vraie une déclaration `sizes` cessait
        # donc d'agir, et l'image repartait à 879 px en présentation Lecture
        # (densité 0,91, mesuré le 31 octobre 2026). Un `max-width` s'applique,
        # lui, à la taille principale d'une boîte flexible.
        for classe in sorted(enfants.get(selecteur, set())):
            for selecteurs, corps, _, _, ligne in regles:
                corps_nu = re.sub(r"\s+", " ", corps)
                if "max-width" in corps_nu:
                    continue
                plafond = re.search(r"width:\s*min\(\s*100%\s*,\s*\d+(?:\.\d+)?px\s*\)", corps_nu)
                if not plafond:
                    continue
                if not any(f".{classe}" in s for s in selecteurs):
                    continue
                erreurs.append(
                    f"{selecteur} : plafond en `width` sur .{classe} (ligne {ligne}) — "
                    "en flex, `flex-basis` remplace la largeur et le plafond ne décide rien : "
                    "écrire `max-width`"
                )

        # Déclarations de grille sur un conteneur flex : inertes par définition.
        # `justify-items: start` du palier de 761 px en était une : elle alignait
        # les panneaux d'une grille, elle ne fait rien en flex.
        for selecteurs, corps, lmax, lmin, ligne in regles:
            if not any(s == selecteur or s.startswith(selecteur + " ") or s.startswith(selecteur + ">")
                       or s.startswith(selecteur + " >") for s in selecteurs):
                continue
            corps_nu = re.sub(r"\s+", " ", corps)
            for propriete in ("grid-template-columns", "grid-template-rows", "grid-auto-flow", "justify-items"):
                if propriete in corps_nu:
                    erreurs.append(
                        f"{selecteur} : `{propriete}` ligne {ligne} sur un conteneur flex — "
                        "cette déclaration ne décide rien"
                    )

        # Présentations : une grille flex ne se replie pas par `grid-template-columns`.
        for selecteurs, corps, _, _, ligne in regles:
            if not any("html[data-layout" in s for s in selecteurs):
                continue
            if "grid-template-columns" not in corps:
                continue
            if not any(selecteur in s for s in selecteurs):
                continue
            erreurs.append(
                f"{selecteur} : la présentation ligne {ligne} lui impose encore "
                "`grid-template-columns` — sans effet sur un conteneur flex, donc sans repli"
            )
        for presentation in entree.get("presentation_repliee", []):
            marqueur = f'html[data-layout="{presentation}"]'
            trouve = any(
                any(marqueur in s and selecteur in s for s in selecteurs)
                and "flex-basis" in re.sub(r"\s+", " ", corps)
                for selecteurs, corps, _, _, _ in regles
            )
            if not trouve:
                erreurs.append(
                    f"{selecteur} : la présentation « {presentation} » le repliait, et "
                    "aucune règle `flex-basis` ne le replie plus"
                )
    return erreurs


#: Les feuilles écrites ici. Le 1er novembre 2026, la colonne d'icône du
#: panneau du simulateur (`20px 54px`) était en pixels nus comme celles du site :
#: la vérifier seulement dans `site.css` aurait laissé la moitié du défaut.
#: `construire-simulateur.py` est lu pour la même raison — il porte les seules
#: règles du simulateur qui soient de nous. La feuille du moteur embarqué vient
#: de l'amont (`simulateur/PROVENANCE.json`) et n'est pas de ce lot : ses pistes
#: (`1fr 96px 74px auto`) restent en pixels, et ce n'est pas une faute qu'on
#: puisse corriger ici.
FEUILLES_SERVIES = (
    "assets/css/site.css",
    "assets/css/anglais-aventure.css",
    "outils/construire-simulateur.py",
)


def feuilles_lues(racine: Path) -> list[tuple[str, str]]:
    """Le CSS servi, par source, y compris les blocs `<style>` de la page du simulateur."""
    sources: list[tuple[str, str]] = []
    for relatif in FEUILLES_SERVIES:
        chemin = racine / relatif
        if chemin.is_file():
            sources.append((relatif, chemin.read_text(encoding="utf-8")))
    return sources


def verifier_pistes_en_px(grilles: dict[str, Grille], racine: Path | None = None) -> list[str]:
    """Aucune piste de grille ne doit rester écrite en pixels **nus**.

    Le 1er novembre 2026, quatre grilles réservaient leur colonne de numéro ou
    d'icône en pixels : `44px 1fr`, `38px minmax(0,1fr)`, `20px 54px minmax(0,1fr)`
    et `18px 40px minmax(0,1fr)`. Aucune ne se replie jamais — elles n'ont aucun
    palier, et c'est normal — mais toutes ignorent le réglage de taille de texte
    du site : à 130 %, le texte grandit dans `.texte-tres-agrandi`, la colonne
    non. `2.75rem` vaut les mêmes 44 px à 100 %, et suit le réglage.

    Une piste écrite dans un `minmax(...)` n'est pas concernée : elle porte déjà
    une décision de largeur, pas une taille d'icône.
    """
    erreurs: list[str] = []
    vus: set[tuple[str, int, str]] = set()

    def relever(source: str, table: dict[str, Grille]) -> None:
        for selecteur, grille in sorted(table.items()):
            for regle in grille.regles:
                if not regle.valeur:
                    continue
                for piste in pistes_en_px(regle.valeur):
                    cle = (source, regle.ligne, piste)
                    if cle in vus:
                        continue
                    vus.add(cle)
                    erreurs.append(
                        f"{selecteur} ({source}) : piste `{piste}` en pixels nus "
                        f"(ligne {regle.ligne}) — elle ne suit pas la taille du texte ; "
                        "écrire la même longueur en rem"
                    )

    relever(FEUILLE, grilles)
    if racine is not None:
        # Les autres sources ne passent pas par `lire_grilles` : la feuille du
        # simulateur porte des conditions que ce modèle ne sait pas placer sur
        # un axe de largeur (`orientation: landscape and max-height`), et il
        # refuse alors de lire quoi que ce soit. Une lecture étroite, qui ne
        # cherche que les déclarations de colonnes, ne dépend pas de ces
        # conditions — et dit ce qu'elle ne lit pas : elle ne nomme que la
        # dernière ligne du sélecteur, sans numéro de ligne.
        for source, texte in feuilles_lues(racine):
            if source == FEUILLE:
                continue
            for bloc in re.finditer(
                r"([^{}]+)\{([^{}]*?grid-template-columns\s*:\s*([^;]+);)", texte
            ):
                selecteur = bloc.group(1).strip().splitlines()[-1].strip()
                for piste in pistes_en_px(bloc.group(3)):
                    erreurs.append(
                        f"{selecteur} ({source}) : piste `{piste}` en pixels nus — "
                        "elle ne suit pas la taille du texte ; écrire la même longueur en rem"
                    )
    return erreurs


def verifier(
    grilles: dict[str, Grille],
    registre: dict,
    capacites: dict[str, dict] | None = None,
    racine: Path | None = None,
) -> list[str]:
    """Chaque grille convertie doit rester dynamique, et son minimum doit être le calculé.

    Trois fautes possibles, et une seule suffit : la grille ne déclare plus
    `auto-fit`, son minimum n'est plus celui que la règle donne, ou un palier de
    largeur lui réimpose un nombre de colonnes. C'est la troisième qui guette :
    un correctif ajouté plus tard dans un `@media` annulerait la conversion sans
    que rien ne le dise.
    """
    erreurs: list[str] = verifier_pistes_en_px(grilles, racine)
    capacites = capacites or {}
    entrees = registre.get("grille", [])
    if not entrees:
        erreurs.append(f"{REGISTRE} ne déclare aucune grille convertie — le registre ne prouve rien")
        return erreurs
    for entree in entrees:
        selecteur = entree.get("selecteur")
        if not selecteur or selecteur not in grilles:
            erreurs.append(f"{selecteur or '(sans sélecteur)'} : absent de {FEUILLE}")
            continue
        grille = grilles[selecteur]
        if grille.asymetrique:
            erreurs.append(
                f"{selecteur} : la règle de base est redevenue inégale "
                f"({grille.valeur_asymetrique[:60]}) — ce n'est plus `auto-fit`"
            )
            continue
        k = int(entree.get("colonnes", 0))
        declare = entree.get("minimum")
        capacite = capacites.get(selecteur)
        # Ce que les pages mettent dans la grille décide de la consigne : une
        # grille à deux éléments ne peut pas afficher trois colonnes, une grille
        # à quatre en afficherait une orpheline. Le registre doit donc déclarer
        # ce qu'il a mesuré, et le contrôle le remesure.
        declare_items = sorted(int(n) for n in (entree.get("items") or []))
        mesures_items = sorted(int(n) for n in (capacite or {}).get("items", []))
        if declare_items != mesures_items:
            erreurs.append(
                f"{selecteur} : capacité déclarée {declare_items or 'non déclarée'}, "
                f"les pages en contiennent {mesures_items or 'aucune mesure'}"
            )
        attendu = minimum_recommande(grille, capacite)
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
    # Les grilles déclarées fixes **à dessein** : le registre les nomme pour que
    # leur forme ne disparaisse pas par inadvertance, et pour que le rapport ne
    # propose pas de les convertir. Sans cette section, cinq aperçus de
    # présentation recevaient une consigne qui n'avait aucun sens.
    # Les plafonds refusés : le registre les nomme pour que le refus ne se
    # perde pas, et le contrôle vérifie que la raison a toujours un objet. Une
    # grille qui perd son plafond rendrait cette décision fausse.
    for entree in registre.get("grille_plafond", []):
        selecteur = entree.get("selecteur")
        if not selecteur or selecteur not in grilles:
            erreurs.append(
                f"{selecteur or '(sans sélecteur)'} : plafond déclaré absent de {FEUILLE} — "
                "la décision écrite n'a plus d'objet"
            )
            continue
        grille = grilles[selecteur]
        valeur = grille.valeur_asymetrique or ""
        if not plafonds(valeur):
            erreurs.append(
                f"{selecteur} : déclaré à plafond ({entree.get('valeur')}), "
                f"la feuille écrit {valeur[:60]!r}"
            )
    for entree in registre.get("grille_fixe", []):
        selecteur = entree.get("selecteur")
        if not selecteur or selecteur not in grilles:
            erreurs.append(f"{selecteur or '(sans sélecteur)'} : grille fixe déclarée absente de {FEUILLE}")
            continue
        grille = grilles[selecteur]
        k = colonnes_de_conception(grille)
        if grille.asymetrique:
            erreurs.append(
                f"{selecteur} : déclarée fixe à {entree.get('colonnes')} colonnes, "
                f"mais sa règle de base est inégale ({grille.valeur_asymetrique[:50]})"
            )
            continue
        if not k:
            erreurs.append(f"{selecteur} : déclarée fixe, aucune règle de base ne fixe ses colonnes")
            continue
        if int(entree.get("colonnes", 0)) != k:
            erreurs.append(
                f"{selecteur} : déclarée fixe à {entree.get('colonnes')} colonnes, "
                f"la feuille en donne {k}"
            )
    return erreurs


#: Largeurs échantillonnées dans le relevé navigateur, en plus des ruptures.
#: Le relevé ne rejoue pas les 2 321 largeurs du modèle : un navigateur coûte
#: des secondes par largeur, là où le modèle coûte des millisecondes. Il mesure
#: donc les deux largeurs qui encadrent chaque rupture annoncée — c'est là que
#: le 1er novembre 2026 une bande d'un pixel a échappé au pas de 10 px — plus
#: quelques largeurs de repère.
LARGEURS_REPERE = (240, 320, 390, 520, 760, 761, 920, 1000, 1160, 1280, 1440, 1920, 2560)


def pages_des_grilles(racine: Path, selecteurs: list[str]) -> dict[str, str]:
    """La page où chaque grille reçoit le plus d'éléments, en chemin relatif.

    Un sélecteur absent des pages n'apparaît pas : le relevé doit alors dire
    qu'il n'a rien pu mesurer, pas choisir une page au hasard.
    """
    import collections

    cibles = {selecteur.lstrip(".") for selecteur in selecteurs if selecteur.startswith(".")}
    trouves: dict[str, dict[str, int]] = collections.defaultdict(dict)
    for page in pages_du_site(racine):
        try:
            texte = page.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        compteur = _CompteurEnfants(cibles)
        try:
            compteur.feed(texte)
        except Exception:  # page mal formée : on ne prétend rien y mesurer
            continue
        relatif = page.relative_to(racine).as_posix()
        for selecteur, _, nombre in compteur.resultats:
            cle = "." + selecteur
            trouves[cle][relatif] = max(trouves[cle].get(relatif, 0), nombre)
    return {
        selecteur: sorted(pages.items(), key=lambda kv: (-kv[1], kv[0]))[0][0]
        for selecteur, pages in trouves.items()
        if pages
    }


def _ruptures(prediction, largeurs: list[int]) -> list[int]:
    """Les largeurs où le nombre de colonnes annoncé change, et celle d'avant."""
    points: set[int] = set()
    precedent = None
    for largeur in largeurs:
        colonnes = prediction(largeur)
        if precedent is not None and colonnes != precedent:
            points.add(largeur - 1)
            points.add(largeur)
        precedent = colonnes
    return sorted(points)


def releve_navigateur(
    racine: Path, grilles: dict[str, Grille], registre: dict
) -> dict:
    """Ce que le modèle **annonce**, à confronter à un vrai navigateur.

    Le 1er novembre 2026, trois grilles converties la veille changeaient de
    nombre de colonnes à 761 px : le modèle ne pouvait pas le voir, puisqu'il
    vérifiait sa propre arithmétique. Ce relevé sort du modèle les nombres qu'il
    affirme, largeur par largeur et taille de texte par taille de texte, pour
    qu'un navigateur les contredise. Il ne juge rien ici : il publie une
    prédiction datée.
    """
    familles: list[tuple[str, dict]] = (
        [("flex", entree) for entree in registre.get("grille_flex", [])]
        + [("grille", entree) for entree in registre.get("grille", [])]
        + [("grille", entree) for entree in registre.get("grille_plafond", [])]
    )
    selecteurs = [str(entree.get("selecteur") or "") for _, entree in familles]
    pages = pages_des_grilles(racine, [s for s in selecteurs if s])
    capacites = lire_capacites(racine, [s for s in selecteurs if s])
    appliquer_capacites(grilles, capacites)

    releve: dict = {
        "feuille": str(FEUILLE),
        "largeurs_repere": list(LARGEURS_REPERE),
        "avertissement": (
            "Prédiction du modèle, pas une mesure : chaque point dit ce que la "
            "feuille devrait produire d'après `modele-grilles.py`. Un navigateur "
            "le contredit ou le confirme, il ne le remplace pas."
        ),
        "grilles": [],
        "non_mesurables": [],
    }
    for famille, entree in familles:
        selecteur = str(entree.get("selecteur") or "")
        # Une grille convertie en `flex-wrap` n'a plus de `grid-template-columns` :
        # `lire_grilles` ne la voit donc plus, et c'est normal. Sa cascade d'avant
        # est écrite au registre (`grille_avant`, `gap_avant`) : le relevé la
        # reconstruit, comme le fait déjà le contrôle de la promesse de repli.
        if famille == "flex" and selecteur:
            grille = grille_synthetique(
                selecteur,
                str(entree.get("grille_avant") or ""),
                str(entree.get("gap_avant") or ""),
            )
        else:
            grille = grilles.get(selecteur)
        if not selecteur or grille is None:
            releve["non_mesurables"].append(
                {"selecteur": selecteur, "raison": "sélecteur absent de la feuille"}
            )
            continue
        if selecteur in capacites and capacites[selecteur].get("items"):
            grille.items = max(capacites[selecteur]["items"])
        # Le remplissage du conteneur lui-même : une grille qui en porte un ne
        # donne pas sa largeur à ses enfants, et le navigateur compte les
        # colonnes dans la largeur utile.
        completer_grille(grille, racine)
        page = pages.get(selecteur)
        if not page:
            releve["non_mesurables"].append(
                {"selecteur": selecteur, "raison": "aucune page ne contient cette grille"}
            )
            continue

        if famille == "flex":
            ecrite = base_ecrite(racine, selecteur)
            if ecrite is None:
                releve["non_mesurables"].append(
                    {
                        "selecteur": selecteur,
                        "raison": "aucune base de `flex` lisible dans la feuille",
                    }
                )
                continue
            base_expr, mesure = ecrite
            base_px = entree.get("plancher_px") or mesure
            # Une base en `em` suit la taille du texte : à 130 %, elle vaut 30 %
            # de plus, et le repli doit avancer. C'est la promesse écrite dans la
            # feuille, et elle n'a jamais été mesurée nulle part. Une base en
            # pixels, elle, ne bouge pas : mesurer trois fois la même chose
            # n'apprendrait rien, et le relevé l'écrit.
            suivant_le_texte = base_expr.endswith("em")
            echelles = (1.0, 1.15, 1.3) if suivant_le_texte else (1.0,)
            base_em = float(base_expr[:-2]) if suivant_le_texte else 0.0
            points: list[dict] = []
            for echelle in echelles:
                base = base_em * RACINE_PX * echelle if suivant_le_texte else float(base_px)

                def prediction(largeur: int, base=base, echelle=echelle) -> int:
                    return colonnes_en_flex(grille, largeur, base, grille.items, echelle)

                retenues = set(_ruptures(prediction, LARGEURS_FINES)) | set(LARGEURS_REPERE)
                for largeur in sorted(retenues):
                    points.append(
                        {
                            "largeur": largeur,
                            "echelle": echelle,
                            "attendu": prediction(largeur),
                            # La largeur que le modèle présume pour les enfants :
                            # le rapporteur la compare à celle que le navigateur
                            # mesure, et c'est là que se lisent la gouttière et
                            # le remplissage. Le rapporteur ne la recalcule pas —
                            # deux arithmétiques qui divergent feraient accuser
                            # la feuille d'un désaccord entre deux constantes.
                            "conteneur": round(conteneur_de(grille, largeur, echelle), 2),
                        }
                    )
            releve["grilles"].append(
                {
                    "selecteur": selecteur,
                    "page": page,
                    "forme": "flex",
                    "base_expr": base_expr,
                    "base_px": float(base_px),
                    "suit_le_texte": suivant_le_texte,
                    "items": grille.items,
                    "points": points,
                }
            )
            continue

        def prediction_grille(largeur: int) -> int:
            return colonnes_de_la_cascade(grille, largeur)

        retenues = set(_ruptures(prediction_grille, LARGEURS_FINES)) | set(LARGEURS_REPERE)
        releve["grilles"].append(
            {
                "selecteur": selecteur,
                "page": page,
                "forme": "grille",
                "items": grille.items,
                # Les pistes d'une grille auto-fit sont en pixels : agrandir le
                # texte ne change pas leur nombre. Une seule échelle suffit, et
                # le dire vaut mieux que de mesurer trois fois la même chose.
                "points": [
                    {
                        "largeur": largeur,
                        "echelle": 1.0,
                        "attendu": prediction_grille(largeur),
                        "conteneur": round(conteneur_de(grille, largeur), 2),
                    }
                    for largeur in sorted(retenues)
                ],
            }
        )
    return releve


FLEX_ECRIT = re.compile(r"flex\s*:\s*[\d.]+\s+\d+\s+([\d.]+)(em|px)")


def base_ecrite(racine: Path, selecteur: str) -> tuple[str, float] | None:
    """La base de `flex` telle qu'elle est **écrite** dans la feuille.

    Le registre porte `plancher_expr` pour les bases converties en `em` ; les
    quatre grilles converties le 31 octobre en pixels n'en ont pas, et leur base
    ne vit que dans la feuille. Lire la feuille plutôt que le registre évite de
    recopier un chiffre — et c'est la valeur écrite qui décide du repli.
    """
    chemin = racine / FEUILLE
    if not chemin.is_file():
        return None
    for selecteurs, corps, *_ in decouper(sans_commentaires(chemin.read_text(encoding="utf-8"))):
        if not any(s == selecteur or s.startswith(selecteur + " ") or s.startswith(selecteur + ">")
                   or s.startswith(selecteur + " >") for s in selecteurs):
            continue
        trouve = FLEX_ECRIT.search(corps)
        if trouve:
            return f"{trouve.group(1)}{trouve.group(2)}", float(trouve.group(1)) * (
                RACINE_PX if trouve.group(2) == "em" else 1.0
            )
    return None


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
        "--pistes",
        action="store_true",
        help="dire ce qu'un `flex-wrap` exprimerait des grilles à pistes inégales",
    )
    analyseur.add_argument(
        "--releve-json",
        metavar="CHEMIN",
        help="écrire ce que le modèle annonce, largeur par largeur, pour un navigateur",
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

    if options.releve_json:
        try:
            registre = lire_registre(RACINE)
        except SourceIllisible as erreur:
            print(f"Impossible de relever les grilles : {erreur}", file=sys.stderr)
            return 2
        releve = releve_navigateur(RACINE, grilles, registre)
        destination = Path(options.releve_json)
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(
            json.dumps(releve, ensure_ascii=False, indent=1) + "\n", encoding="utf-8"
        )
        points = sum(len(grille["points"]) for grille in releve["grilles"])
        gouttiere_lue = gouttiere()
        print(
            f"Conteneur lu : gouttière {gouttiere_lue.large:g}rem au-dessus de "
            f"{gouttiere_lue.seuil} px, {gouttiere_lue.etroit:g}rem à {gouttiere_lue.seuil} px "
            "et moins, multipliée par la taille du texte."
        )
        print(
            f"Relevé écrit : {destination} — {len(releve['grilles'])} grille(s), "
            f"{points} point(s) à confronter à un navigateur."
        )
        for absent in releve["non_mesurables"]:
            print(
                f"  ! {absent['selecteur']} : {absent['raison']} — non mesuré",
                file=sys.stderr,
            )
        return 0

    if options.verifier:
        try:
            registre = lire_registre(RACINE)
        except SourceIllisible as erreur:
            print(f"Impossible de vérifier les grilles : {erreur}", file=sys.stderr)
            return 2
        capacites = lire_capacites(RACINE, [e.get("selecteur") or "" for e in registre.get("grille", [])])
        appliquer_capacites(grilles, capacites)
        erreurs = verifier(grilles, registre, capacites, RACINE)
        erreurs.extend(verifier_flex(RACINE, registre))
        for morte in declarations_mortes(grilles):
            erreurs.append(
                f"{morte['selecteur']} : la déclaration ligne {morte['ligne']} "
                f"(`{morte['valeur'][:40]}`) ne décide rien — c'est déjà la valeur en vigueur "
                f"à {morte['largeur']}px"
            )
        sans_capacite = [
            selecteur
            for selecteur in (e.get("selecteur") or "" for e in registre.get("grille", []))
            if selecteur and selecteur not in capacites
        ]
        for selecteur in sans_capacite:
            print(
                f"  ! {selecteur} : absent des pages — sa capacité n'est pas mesurée, "
                "et le minimum applique la règle la plus prudente",
                file=sys.stderr,
            )
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
        k = colonnes_de_conception(grille)
        capacite = lire_capacites(RACINE, [grille.selecteur]).get(grille.selecteur)
        appliquer_capacites(grilles, {grille.selecteur: capacite} if capacite else {})
        minimum = minimum_recommande(grille, capacite)
        if minimum is None:
            print(f"{grille.selecteur} : aucune piste ne garde {k} colonnes au conteneur maximal")
            return 2
        nombre, maximal, details = ecart(grille, minimum)
        print(f"{grille.selecteur} — {k} colonnes, gap {grille.gap:g}px")
        for condition in paliers(grille):
            print(f"  palier {condition}")
        print(
            f"  règle : minmax(min({minimum}px, 100%), 1fr) — {nombre} écart(s) avec l'ancienne "
            f"cascade, maximum {maximal}, carte la plus étroite {carte_minimale(grille, minimum):.0f}px"
        )
        for largeur, ancienne, nouvelle in details[:20]:
            print(f"    {largeur}px : {ancienne} → {nouvelle}")
        return 0

    if options.regle:
        try:
            declarees = lire_registre(RACINE).get("grille_fixe", [])
        except SourceIllisible:
            declarees = []
        fixes = {entree.get("selecteur") for entree in declarees}
        capacites = lire_capacites(RACINE, [g.selecteur for g in convertibles(grilles)])
        appliquer_capacites(grilles, capacites)
        mesurees = 0
        for grille in convertibles(grilles):
            selecteur = grille.selecteur
            k = colonnes_de_conception(grille)
            if not k or selecteur in fixes:
                continue
            minimum = minimum_recommande(grille, capacites.get(selecteur))
            if minimum is None:
                print(f"{selecteur:32} {k} col. — aucune piste ne tient")
                continue
            mesurees += 1
            avant = min(
                (conteneur(largeur) - (colonnes_anciennes(grille, largeur) - 1) * (ecart_a(grille, largeur) or grille.gap))
                / colonnes_anciennes(grille, largeur)
                for largeur in LARGEURS
            )
            print(
                f"{selecteur:32} {k} col.{seuil_note(grille)} → minmax(min({minimum}px, 100%), 1fr) · "
                f"pire carte {avant:.0f}px → {carte_minimale(grille, minimum):.0f}px · "
                f"{len(paliers(grille))} palier(s) de largeur"
            )
        print(f"{mesurees} grilles mesurées.")
        if fixes:
            print(f"{len(fixes)} grille(s) déclarée(s) fixe(s) à dessein : {', '.join(sorted(fixes))}")
        inegales = asymetriques(grilles)
        if inegales:
            print(
                f"{len(inegales)} grilles à pistes inégales ne sont pas convertibles et gardent "
                "leurs paliers :"
            )
            for grille in inegales:
                print(f"  {grille.selecteur:32} {grille.valeur_asymetrique[:60]}")
        return 0

    if options.pistes:
        capacites_inegales = lire_capacites(
            RACINE, [g.selecteur for g in asymetriques(grilles)]
        )
        resultats = pistes_des_inegales(grilles, capacites_inegales)
        formes: dict[str, int] = {}
        for resultat in resultats:
            formes[resultat["forme"]] = formes.get(resultat["forme"], 0) + 1
        gouttiere_lue = gouttiere()
        print(
            "Conteneur : "
            f"`100% - {gouttiere_lue.large:g}rem` au-dessus de {gouttiere_lue.seuil} px, "
            f"`100% - {gouttiere_lue.etroit:g}rem` à {gouttiere_lue.seuil} px et moins "
            f"(lu dans {gouttiere_lue.source}) — la gouttière suit la taille du texte."
        )
        print(
            f"{len(resultats)} grilles à pistes inégales : "
            + ", ".join(f"{nombre} {forme}" for forme, nombre in sorted(formes.items()))
        )
        print(
            "  contenu   : une piste `auto` ou `max-content` fait dépendre le repli du texte — "
            "aucun modèle ne le tranche sans navigateur"
        )
        print("  proportion : un `flex: <g> 1 <plancher>px` reproduirait le rapport entre colonnes")
        print(
            "  plafond   : une colonne a un **plafond** (`minmax(230px, 300px)`) — un `flex` "
            "n'en a pas, et sur une seule ligne il ne prendrait pas toute la largeur"
        )
        print(
            "  badge     : une piste fixe à côté d'une piste souple (`2.75rem 1fr`) — aucun palier, "
            "donc rien à replier ; seule l'unité compte (px ne suit pas la taille du texte, rem si)"
        )
        print(
            "  sans-plancher : des `fr` sans plancher — le repli vient d'un palier, et seule une "
            "base choisie peut le remplacer, vérifiée au pixel"
        )
        print("  decor     : des `fr` sans plancher ni palier — un aperçu, rien à rendre dynamique")
        print("  motif / fixe / illisible : rien à rendre dynamique")
        for resultat in resultats:
            if resultat["forme"] == "proportion":
                grille = grilles[resultat["selecteur"]]
                largeur = ecart_de_largeur(grille)
                print(
                    f"  {resultat['selecteur'][:44]:44} plancher {resultat['plancher']}px · "
                    f"{resultat['ecarts']} largeur(s) sur {len(LARGEURS)} diffèrent de la cascade · "
                    f"colonnes jusqu'à {largeur['px']:.0f}px ({largeur['part']:.1%}) d'écart"
                )
                compromis = plancher_de_compromis(grille)
                print(
                    "      compromis : "
                    + (
                        f"{compromis['px']:g} px ({compromis['expr']}) reproduirait le repli "
                        "actuel, et suivrait la taille du texte"
                        if compromis
                        else "aucune base ne reproduit le repli actuel"
                    )
                )
                for bande in bandes_de_changement(grille, resultat["plancher"]):
                    print(
                        f"      {bande['debut']}–{bande['fin']} px : {bande['cascade']} colonne(s) "
                        f"deviennent {bande['flex']}"
                    )
            elif resultat["forme"] in ("sans-plancher", "decor"):
                compromis = resultat.get("compromis")
                conditions = resultat.get("paliers") or []
                print(
                    f"  {resultat['selecteur'][:44]:44} {resultat['forme']:9} "
                    f"{len(conditions)} palier(s)"
                    + (
                        f" · compromis {compromis['px']:g} px ({compromis['expr']}), vérifié au pixel"
                        if compromis
                        else (
                            " · aucune base ne reproduit le repli au pixel près"
                            if conditions
                            else " · aucune largeur ne change de nombre de colonnes"
                        )
                    )
                )
            elif resultat["forme"] == "badge":
                paliers_grille = resultat.get("paliers") or []
                px = resultat.get("px") or []
                print(
                    f"  {resultat['selecteur'][:44]:44} badge {', '.join(resultat.get('fixes') or [])} · "
                    f"{len(paliers_grille)} palier(s)"
                    + (f" · à réécrire en rem : {', '.join(px)}" if px else " · déjà en rem")
                )
            elif resultat["forme"] == "plafond":
                grille = grilles[resultat["selecteur"]]
                bornes = largeur_plafonnee(grille, resultat["valeur"])
                detail = ""
                if bornes:
                    detail = (
                        f" · la piste vaut {bornes['mini']:g} à {bornes['maxi']:g} px sur "
                        f"{bornes['largeurs']} largeur(s) à deux colonnes"
                        + (
                            f" — la borne basse ({bornes['bas']:g} px) n'est jamais atteinte"
                            if not bornes["borne_basse_atteinte"]
                            else f" — la borne basse ({bornes['bas']:g} px) sert"
                        )
                    )
                print(
                    f"  {resultat['selecteur'][:44]:44} plafond {', '.join(resultat.get('plafonds') or [])} · "
                    "un `flex` ne sait pas plafonner un panneau qui rétrécit" + detail
                )
            else:
                print(f"  {resultat['selecteur'][:44]:44} {resultat['forme']}")
        proches = [
            r for r in resultats if r["forme"] == "proportion" and r["ecarts"] <= len(LARGEURS) // 8
        ]
        print(
            f"{len(proches)} grille(s) changeraient de nombre de colonnes sur moins d'un huitième "
            "du balayage : ce sont les seules qu'un `flex-wrap` remplacerait sans redessiner."
        )
        print(
            "  Rien n'est écrit dans la feuille : ce relevé mesure avant de convertir, "
            "et un rendu réel (contenu, ratio, hauteur) demanderait un navigateur."
        )
        return 0

    capacites = lire_capacites(RACINE, [g.selecteur for g in convertibles(grilles)])
    appliquer_capacites(grilles, capacites)
    lignes = etat(grilles, capacites)
    if options.json:
        print(json.dumps(lignes, ensure_ascii=False, indent=2))
    else:
        print(rapport(lignes, asymetriques(grilles), grilles))
    return 0


if __name__ == "__main__":
    sys.exit(principal())
