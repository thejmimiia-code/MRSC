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
    regles: list[Regle] = field(default_factory=list)
    source: str = ""
    #: Vraie dès qu'une de ses règles est asymétrique : la grille n'est alors pas
    #: convertible en `auto-fit`, et le rapport doit le dire au lieu de proposer.
    asymetrique: bool = False
    valeur_asymetrique: str = ""
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


def ecart_colonnes(corps: str) -> float | None:
    """L'écart **entre colonnes** déclaré par ce bloc, en pixels.

    Le 31 octobre 2026, la lecture prenait le premier nombre de `gap` sans
    regarder lequel c'était : `gap: .75rem 1.1rem` vaut 12 px entre les lignes
    et **17,6 px entre les colonnes**, et c'est le second qui décide du nombre
    de colonnes. Deux grilles de la feuille sont dans ce cas. Le calcul du
    seuil de repli s'en trouvait décalé d'un écart de grille — la même erreur
    que celle déjà corrigée sur `.document-grid`, sous une autre forme.
    """
    trouve = GAP_REM.search(corps)
    if not trouve:
        return None
    propriete, valeur = trouve.group(1), trouve.group(2).split()
    mesures = []
    for morceau in valeur:
        longueur = LONGUEUR.match(morceau)
        if not longueur:
            return None
        nombre = float(longueur.group(1))
        mesures.append(nombre * 16 if longueur.group(2) == "rem" else nombre)
    if not mesures:
        return None
    if propriete == "row-gap":
        return None
    if len(mesures) == 1:
        return mesures[0]
    return mesures[1]  # `gap: <ligne> <colonne>` — la colonne est la seconde


def lire_grilles(texte: str) -> dict[str, Grille]:
    """Toutes les grilles dont la feuille fixe ou calcule le nombre de colonnes."""
    texte = sans_commentaires(texte)
    grilles: dict[str, Grille] = {}
    for ordre, (selecteurs, corps, largeur_max, largeur_min, ligne) in enumerate(decouper(texte)):
        trouve = DECLARATION_COLONNES.search(corps)
        if not trouve:
            continue
        valeur = " ".join(trouve.group(1).split())
        forme, colonnes, minimum = classer_valeur(valeur)
        gap = ecart_colonnes(corps)
        for selecteur in selecteurs:
            grille = grilles.setdefault(selecteur, Grille(selecteur=selecteur, source=f"site.css:{ligne}"))
            if gap is not None:
                grille.gap = round(gap, 2)
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
        nouvelle = auto_fit(minimum, grille.gap, largeur, grille.items)
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
    return min(
        (
            conteneur(largeur)
            - (auto_fit(minimum, grille.gap, largeur, grille.items) - 1) * grille.gap
        )
        / auto_fit(minimum, grille.gap, largeur, grille.items)
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
        return auto_fit(base.minimum, grille.gap, CONTENU_DEFAUT + GARNITURE_LATERALE, grille.items)
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
    """Le plus petit minimum qui renonce à la paire là où la cascade y renonçait."""
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
    place = conteneur(CONTENU_DEFAUT + GARNITURE_LATERALE)
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
    valides = [n for n in CANDIDATS if auto_fit(n, gap, int(contenu) + GARNITURE_LATERALE) == k]
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


def verifier(
    grilles: dict[str, Grille], registre: dict, capacites: dict[str, dict] | None = None
) -> list[str]:
    """Chaque grille convertie doit rester dynamique, et son minimum doit être le calculé.

    Trois fautes possibles, et une seule suffit : la grille ne déclare plus
    `auto-fit`, son minimum n'est plus celui que la règle donne, ou un palier de
    largeur lui réimpose un nombre de colonnes. C'est la troisième qui guette :
    un correctif ajouté plus tard dans un `@media` annulerait la conversion sans
    que rien ne le dise.
    """
    erreurs: list[str] = []
    capacites = capacites or {}
    entrees = registre.get("grille", [])
    if not entrees:
        return [f"{REGISTRE} ne déclare aucune grille convertie — le registre ne prouve rien"]
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
        capacites = lire_capacites(RACINE, [e.get("selecteur") or "" for e in registre.get("grille", [])])
        appliquer_capacites(grilles, capacites)
        erreurs = verifier(grilles, registre, capacites)
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
                (conteneur(largeur) - (colonnes_anciennes(grille, largeur) - 1) * grille.gap)
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
