#!/usr/bin/env python3
"""Vérifie hors ligne les budgets d’affichage des titres et la couverture des modes.

Ce contrôle existe pour deux risques qu’aucun test du dépôt ne voyait :

  1. un `<title>` trop long, tronqué dans les résultats de recherche — le titre
     de l’accueil fait 73 caractères depuis qu’il reprend la formule du H1, et
     cette longueur a été acceptée par une personne, pas mesurée comme idéale ;
  2. un H1 qui déborde ou s’allonge sans que personne ne le remarque à 320 px ;
  3. une illustration servie dans une variante trop petite pour la place qu’elle occupe,
     donc agrandie par le navigateur — celle des mondes l’était de 3,1× sur téléphone.

Il lit les valeurs réellement écrites dans `assets/css/site.css` — plancher du
`clamp()` de `h1`, largeur du conteneur, marge étroite, `max-width` du titre de
l’accueil — au lieu de recopier des constantes qui dériveraient.

Ce que ce contrôle ne fait pas, et ne peut pas faire ici :

  - il ne rend aucune page : aucun navigateur n’est lancé, aucun pixel n’est lu ;
  - les nombres de lignes sont des **estimations**, à partir d’une avance moyenne
    de 0,5 em par caractère et d’une police système supposée ; le crénage, les
    césures, le zoom texte et la police réellement installée changent le résultat ;
  - il ne dit rien de la lisibilité, de la compréhension, ni du rendu dans un
    lecteur d’écran. Une validation visuelle humaine reste nécessaire.

Les budgets sont des **arbitrages de travail**, pas des normes : les dépasser
demande une décision explicite, pas un ajustement du chiffre attendu.

    python3 outils/verifier-budgets-visuels.py
"""

from __future__ import annotations

import math
import os
import re
import sys
from pathlib import Path

#: Racine lue par le contrôle. La surcharge sert au banc de mutation
#: (`outils/test_mutations_budgets_visuels.py`), qui allonge un titre, retire un
#: `<title>` ou change une valeur de `site.css` dans une copie du dépôt.
RACINE = Path(os.environ.get("MRSC_RACINE") or Path(__file__).resolve().parent.parent).resolve()
CSS = RACINE / "assets" / "css" / "site.css"

# Longueur au-delà de laquelle un titre de page est tronqué dans la plupart des
# résultats de recherche. Repère de travail, non une règle des moteurs.
LONGUEUR_TITRE_CIBLE = 60

# Pages dont le titre dépasse la cible, avec l'accord explicite qui l'autorise et
# la longueur maximale désormais refusée. Un titre ne peut qu'y raccourcir : le
# chiffre est un plafond, jamais une cible à atteindre.
TITRES_EXCEPTIONNELS = {
    "index.html": (
        73,
        "titre aligné sur la formule du H1 « Apprendre, vérifier et débattre des sujets "
        "qui nous concernent » à la demande de la personne responsable du site ; troncature "
        "possible en résultats de recherche, arbitrage assumé et non mesuré",
    ),
}

# H1 de l'accueil : caractères, lignes estimées à 320 px, lignes estimées en grand
# écran. Plafonds de non-régression, pas objectifs de conception.
H1_BUDGET = {"index.html": (63, 6, 4)}

# Hypothèse de largeur moyenne d'un caractère, en em, pour la police système.
AVANCE_MOYENNE_EM = 0.5
TAILLE_RACINE_PX = 16

# Modes d'affichage et de contraste qui doivent continuer à styler les repères
# chiffrés de l'accueil (bordure, fonds, empilement).
MODE_SELECTEURS = {
    "contraste renforcé": r"html\.contraste-renforce[^{]*\{[^}]*\.home-hero-facts",
    "couleurs forcées": r"@media\s*\(forced-colors:\s*active\)",
    "lecture": r'html\[data-layout="lecture"\][^{]*\{',
}


class Echec(Exception):
    """Budget ou couverture rompus."""


def lire_css() -> str:
    try:
        return CSS.read_text(encoding="utf-8")
    except OSError as erreur:
        raise Echec(f"feuille de style illisible : {erreur}") from erreur


def plancher_rem(css: str) -> float:
    """Plancher du `clamp()` de `h1`, en rem."""
    bloc = re.search(r"\nh1\s*\{([^}]*)\}", css)
    if not bloc:
        raise Echec("règle `h1 { … }` introuvable dans assets/css/site.css")
    clamp = re.search(r"font-size:\s*clamp\(\s*([\d.]+)rem", bloc.group(1))
    if not clamp:
        raise Echec("`font-size: clamp(…)` introuvable dans la règle `h1`")
    return float(clamp.group(1))


def largeur_contenu_px(css: str) -> int:
    contenu = re.search(r"--content:\s*(\d+)px", css)
    if not contenu:
        raise Echec("variable `--content` introuvable")
    return int(contenu.group(1))


def marge_etroite_rem(css: str) -> float:
    """Marge horizontale du conteneur sous 760 px."""
    for bloc in re.finditer(r"@media\s*\(max-width:\s*760px\)\s*\{", css):
        suivant = css[bloc.end() : bloc.end() + 4000]
        conteneur = re.search(r"\.container[^{]*\{[^}]*calc\(100%\s*-\s*([\d.]+)rem\)", suivant)
        if conteneur:
            return float(conteneur.group(1))
    raise Echec("marge du conteneur sous 760 px introuvable")


def max_width_titre_ch(css: str) -> int | None:
    """`max-width` du titre de l'accueil, en `ch`, s'il est déclaré."""
    regle = re.search(r"\.home-hero-civic\s+\.hero-title\s*\{[^}]*max-width:\s*(\d+)ch", css)
    return int(regle.group(1)) if regle else None


def titres_des_pages() -> dict[str, str]:
    titres: dict[str, str] = {}
    for page in sorted(RACINE.glob("*.html")):
        contenu = page.read_text(encoding="utf-8")
        trouve = re.search(r"<title>(.*?)</title>", contenu, re.S)
        if not trouve:
            raise Echec(f"{page.name} : aucune balise `<title>`")
        titres[page.name] = re.sub(r"\s+", " ", trouve.group(1)).strip()
    if not titres:
        raise Echec("aucune page HTML trouvée à la racine : le contrôle ne mesure rien")
    return titres


def texte_h1(contenu: str, page: str) -> str:
    bloc = re.search(r"<h1\b[^>]*>(.*?)</h1>", contenu, re.S | re.I)
    if not bloc:
        raise Echec(f"{page} : aucun `<h1>`")
    sans_balises = re.sub(r"<[^>]+>", "", bloc.group(1))
    return re.sub(r"\s+", " ", sans_balises).strip()


def verifier_titres(titres: dict[str, str]) -> list[str]:
    lignes: list[str] = []
    trop_longs: list[str] = []
    for page, titre in titres.items():
        plafond, _raison = TITRES_EXCEPTIONNELS.get(page, (LONGUEUR_TITRE_CIBLE, ""))
        if len(titre) > plafond:
            trop_longs.append(f"{page} : {len(titre)} caractères pour un plafond de {plafond}")
    if trop_longs:
        raise Echec(
            "titres trop longs pour l'affichage en résultats de recherche : "
            + " ; ".join(trop_longs)
            + ". Raccourcir le titre, ou inscrire l'exception et sa raison dans TITRES_EXCEPTIONNELS."
        )
    exceptionnels = [page for page in titres if page in TITRES_EXCEPTIONNELS]
    lignes.append(
        f"OK     Titres de page : {len(titres)} pages sous leur plafond "
        f"({LONGUEUR_TITRE_CIBLE} caractères"
        + (f" ; exception assumée : {', '.join(sorted(exceptionnels))}" if exceptionnels else "")
        + ")."
    )
    return lignes


def verifier_h1_accueil(css: str) -> list[str]:
    page = "index.html"
    contenu = (RACINE / page).read_text(encoding="utf-8")
    texte = texte_h1(contenu, page)
    plafond_caracteres, plafond_lignes_320, plafond_lignes_large = H1_BUDGET[page]

    if len(texte) > plafond_caracteres:
        raise Echec(
            f"Le H1 de l'accueil fait {len(texte)} caractères, au-delà du plafond de "
            f"{plafond_caracteres} accepté. Allonger demande une décision, pas un ajustement du budget."
        )

    police_px = plancher_rem(css) * TAILLE_RACINE_PX
    dispo_320 = 320 - 2 * marge_etroite_rem(css) * TAILLE_RACINE_PX
    avance_px = AVANCE_MOYENNE_EM * police_px
    caracteres_par_ligne = max(1.0, dispo_320 / avance_px)
    lignes_320 = math.ceil(len(texte) / caracteres_par_ligne)
    if lignes_320 > plafond_lignes_320:
        raise Echec(
            f"Le H1 de l'accueil occuperait environ {lignes_320} lignes à 320 px "
            f"(plafond {plafond_lignes_320}). Vérifier le rendu réel avant de relever le budget."
        )

    mot = max(texte.replace("\u00a0", " ").split(), key=len)
    largeur_mot = len(mot) * avance_px
    if largeur_mot > dispo_320:
        raise Echec(
            f"Le mot le plus long du H1 (« {mot} ») est estimé à {largeur_mot:.0f} px "
            f"pour {dispo_320:.0f} px disponibles à 320 px : débordement probable."
        )

    limite_ch = max_width_titre_ch(css)
    largeur_large = limite_ch if limite_ch else largeur_contenu_px(css) / avance_px
    lignes_large = math.ceil(len(texte) / max(1.0, largeur_large))
    if lignes_large > plafond_lignes_large:
        raise Echec(
            f"Le H1 de l'accueil occuperait environ {lignes_large} lignes en grand écran "
            f"(plafond {plafond_lignes_large}, largeur de référence {largeur_large:.0f} caractères)."
        )

    lignes = [
        f"OK     H1 de l'accueil : {len(texte)} caractères, {lignes_320} ligne(s) estimée(s) "
        f"à 320 px, {lignes_large} en grand écran, mot le plus long « {mot} » "
        f"estimé à {largeur_mot:.0f} px pour {dispo_320:.0f} px disponibles."
    ]
    if limite_ch is None:
        lignes.append(
            "       Note : aucune règle `.home-hero-civic .hero-title { max-width: …ch }` ; "
            "l'estimation en grand écran utilise la largeur du conteneur."
        )
    return lignes


def verifier_modes(css: str) -> list[str]:
    manquants: list[str] = []
    for nom, motif in MODE_SELECTEURS.items():
        blocs = [
            bloc.group(0)
            for bloc in re.finditer(
                {
                    "contraste renforcé": r"html\.contraste-renforce[^{]*\{[^}]*\}",
                    "couleurs forcées": r"@media\s*\(forced-colors:\s*active\)\s*\{.*?\n\}",
                    "lecture": r'html\[data-layout="lecture"\][^{]*\{[^}]*\}',
                }[nom],
                css,
                re.S,
            )
        ]
        if not any(".home-hero-facts" in bloc for bloc in blocs):
            manquants.append(nom)
    if manquants:
        raise Echec(
            "les repères chiffrés de l'accueil (.home-hero-facts) ne sont plus stylés en : "
            + ", ".join(manquants)
            + ". Un mode d'affichage ne doit pas laisser ce bloc sans bordure ni empilement."
        )
    return [
        f"OK     Modes d'affichage : .home-hero-facts couvert en "
        + ", ".join(MODE_SELECTEURS)
        + " (bordure, fonds ou empilement selon le mode)."
    ]


# --- Héros des mondes : géométrie et netteté --------------------------------
# Le 22 octobre 2026, l'illustration des mondes a été signalée comme pixelisée.
# La cause n'était pas la compression (36,4 dB de PSNR) mais la géométrie : en
# `object-fit: cover` dans une boîte de 150 à 180vw de haut, il aurait fallu une
# source de plus de 3 700 px de large à 3×, qu'aucune variante ne fournissait.
# Sous 700 px, le héros est donc devenu un bandeau au ratio naturel de l'image.
HEROS_MONDES = {
    "page": "anglais-aventure.html",
    "motif_srcset": "assets/images/mondes-savoirs-hero",
    "ratio": 1672 / 941,
    "hauteur_max_px": 720,
    "hauteur_vw": 0.76,
    # Téléphones : bandeau plein cadre au ratio naturel, donc la source requise
    # vaut la largeur de l'écran en pixels d'appareil.
    "paliers_mobiles": ((320, 3), (360, 3), (390, 3), (393, 3), (430, 3)),
    # Écrans larges, avec et sans haute densité. Le mode attendu est déduit des
    # règles CSS : panneau contenu en haute densité (2× et plus) et au-delà de
    # 1 680 px en 1×, plein cadre ailleurs.
    "paliers_larges": (
        (768, 2), (834, 2), (1024, 2), (1280, 2), (1440, 2), (1728, 2),
        (768, 1), (1024, 1), (1440, 1), (1680, 1), (1920, 1), (2560, 1),
    ),
    # Largeurs d'affichage maximales des panneaux, lues dans le CSS et vérifiées
    # à l'exécution : 836 px = la moitié du master de 1 672 px, donc 1:1 à 2×.
    "panneau_dense": 836,
    "panneau_un_x": 1672,
    "seuil_panneau_un_x": 1680,
}


def bloc_media(css: str, largeur_max: int) -> str:
    """Contenu du premier bloc `@media (max-width: <largeur_max>px)`, accolades comprises."""
    ouverture = re.search(rf"@media\s*\(max-width:\s*{largeur_max}px\)\s*\{{", css)
    if not ouverture:
        raise Echec(f"bloc @media (max-width: {largeur_max}px) introuvable")
    profondeur = 1
    index = ouverture.end()
    while index < len(css) and profondeur:
        if css[index] == "{":
            profondeur += 1
        elif css[index] == "}":
            profondeur -= 1
        index += 1
    return css[ouverture.end() : index - 1]


def declarations(bloc: str, selecteur: str) -> str:
    """Déclarations d'une règle, espaces normalisés. Vide si la règle est absente."""
    regle = re.search(rf"{re.escape(selecteur)}\s*\{{([^}}]*)\}}", bloc)
    return re.sub(r"\s+", " ", regle.group(1)) if regle else ""


def largeurs_servies(html: str, motif: str) -> list[int]:
    """Largeurs déclarées dans les `srcset` qui servent cette image."""
    largeurs: set[int] = set()
    for attribut in re.findall(r'(?:data-)?(?:image)?srcset="([^"]+)"', html):
        if motif not in attribut:
            continue
        largeurs.update(int(valeur) for valeur in re.findall(r"\s(\d+)w", attribut))
    return sorted(largeurs)


def bloc_media_motif(css: str, motif: str) -> str:
    """Contenu du premier bloc `@media` dont la condition contient le motif."""
    ouverture = re.search(rf"@media[^{{]*{re.escape(motif)}[^{{]*\{{", css)
    if not ouverture:
        raise Echec(f"bloc @media contenant « {motif} » introuvable")
    profondeur = 1
    index = ouverture.end()
    while index < len(css) and profondeur:
        if css[index] == "{":
            profondeur += 1
        elif css[index] == "}":
            profondeur -= 1
        index += 1
    return css[ouverture.end() : index - 1]


def source_requise(largeur: int, densite: float, panneau_max: int | None) -> float:
    """Pixels de source nécessaires pour cet écran.

    En panneau, l'image est affichée à sa largeur contenue : le besoin vaut la
    largeur d'affichage en pixels d'appareil. En plein cadre, `object-fit:
    cover` impose de couvrir la boîte entière : le besoin vaut le plus grand des
    deux côtés, converti en largeur de source équivalente.
    """
    if panneau_max is not None:
        return min(largeur, panneau_max) * densite
    hauteur = min(HEROS_MONDES["hauteur_max_px"], HEROS_MONDES["hauteur_vw"] * largeur)
    return max(largeur, hauteur * HEROS_MONDES["ratio"]) * densite


def verifier_heros_mondes(css: str) -> list[str]:
    """Aucun pixel étiré sur téléphone, et agrandissement desktop non aggravé."""
    css_aventure = (RACINE / "assets" / "css" / "anglais-aventure.css").read_text(encoding="utf-8")
    etroit = bloc_media(css_aventure, 700)
    tres_etroit = bloc_media(css_aventure, 430)

    attendus = (
        ("max-width: 700px", ".adventure-hero-art", ("position: static", "height: auto", "object-fit: contain")),
        ("max-width: 700px", ".adventure-hero-shade", ("display: none",)),
        ("max-width: 700px", ".adventure-hero", ("min-height: 0",)),
        ("max-width: 430px", ".adventure-hero", ("min-height: 0",)),
    )
    for bloc_nom, selecteur, morceaux in attendus:
        bloc = etroit if bloc_nom == "max-width: 700px" else tres_etroit
        regle = declarations(bloc, selecteur)
        if not regle:
            raise Echec(f"{bloc_nom} : la règle `{selecteur}` est absente du bloc")
        manquants = [morceau for morceau in morceaux if morceau not in regle]
        if manquants:
            raise Echec(
                f"{bloc_nom} : `{selecteur}` doit porter {', '.join(manquants)}. "
                "Sans cela, l'illustration redevient une image de fond étirée dans une boîte "
                "haute, et la source nécessaire dépasse largement les variantes servies."
            )

    # Panneau contenu : écrans denses (2× et plus) et très grands écrans 1×.
    dense = declarations(bloc_media_motif(css_aventure, "min-resolution: 2dppx"), ".adventure-hero")
    large = declarations(bloc_media_motif(css_aventure, "max-resolution: 1.99dppx"), ".adventure-hero")
    if f"--hero-art-max: {HEROS_MONDES['panneau_dense']}px" not in dense:
        raise Echec(
            f"le panneau des écrans denses doit fixer `--hero-art-max: {HEROS_MONDES['panneau_dense']}px` "
            "(la moitié du master), sinon l'image reste étirée à 2×."
        )
    if f"--hero-art-max: {HEROS_MONDES['panneau_un_x']}px" not in large:
        raise Echec(
            f"le panneau des très grands écrans doit fixer `--hero-art-max: {HEROS_MONDES['panneau_un_x']}px`, "
            "sinon l'image est étirée au-delà de la largeur du master en 1×."
        )
    # Les valeurs seules ne suffisent pas : il faut que la règle qui les applique
    # existe. Sans ce `max-width`, le panneau retombe en pleine largeur et l'image
    # est de nouveau étirée à 2× — une mutation l'a montré.
    application = next(
        (
            regle.group(1)
            for regle in re.finditer(r"\.adventure-hero-art\s*\{([^}]*)\}", css_aventure)
            if "max-width: var(--hero-art-max" in re.sub(r"\s+", " ", regle.group(1))
        ),
        "",
    )
    if not application:
        raise Echec(
            "aucune règle `.adventure-hero-art` n'applique `max-width: var(--hero-art-max…)` : "
            "le panneau serait pleine largeur malgré les valeurs déclarées."
        )
    if "position: static" not in re.sub(r"\s+", " ", application):
        raise Echec(
            "la règle du panneau doit aussi passer `.adventure-hero-art` en `position: static`, "
            "sinon l'image reste une image de fond plein cadre."
        )

    html = (RACINE / HEROS_MONDES["page"]).read_text(encoding="utf-8")
    if 'sizes="100vw"' not in html:
        raise Echec(
            "Le héros des mondes ne déclare plus `sizes=\"100vw\"` : une valeur inférieure "
            "à la largeur réelle ferait choisir une variante trop petite, donc un agrandissement."
        )
    largeurs = largeurs_servies(html, HEROS_MONDES["motif_srcset"])
    if not largeurs:
        raise Echec("aucune largeur de srcset trouvée pour l'illustration des mondes")
    servie = max(largeurs)

    # Une variante plus large que le srcset ne sert à rien : le navigateur ne la
    # verra jamais. Ce contrôle se déclenche le jour où un master plus large est
    # déposé — il rappelle qu'il faut alors compléter les `srcset` et relever les
    # largeurs de panneau, au lieu de croire la netteté réglée.
    nom_base = Path(HEROS_MONDES["motif_srcset"]).name
    sur_disque = sorted(
        largeur
        for fichier in (RACINE / "assets" / "images").glob(f"{nom_base}-*.avif")
        if (trouve := re.fullmatch(rf"{re.escape(nom_base)}-(\d+)\.avif", fichier.name))
        and (largeur := int(trouve.group(1)))
    )
    if sur_disque and sur_disque[-1] > servie:
        raise Echec(
            f"une variante {sur_disque[-1]}px existe sur le disque mais les `srcset` s'arrêtent à "
            f"{servie}px : elle ne sera jamais servie. Ajouter les largeurs manquantes aux `srcset` "
            "de anglais-aventure.html et apprendre.html, puis relever les largeurs de panneau dans "
            "outils/verifier-budgets-visuels.py."
        )

    def verifier_palier(largeur: int, densite: float, panneau_max: int | None, contexte: str) -> float:
        requise = source_requise(largeur, densite, panneau_max)
        if requise > servie:
            raise Echec(
                f"{contexte} {largeur}px à {densite}× : {requise:.0f}px de source nécessaires pour "
                f"{servie}px disponibles — l'image serait agrandie {requise / servie:.2f}×, donc "
                "visiblement floue. Réduire la largeur d'affichage : aucune illustration plus large n'est disponible (le générateur d'images plafonne à 1,06 Mpx, sous le master de 1,67 Mpx)."
            )
        return requise / servie

    facteurs: list[tuple[str, float]] = []
    for largeur, densite in HEROS_MONDES["paliers_mobiles"]:
        # Bandeau au ratio naturel : l'image occupe toute la largeur, donc la
        # source requise vaut la largeur de l'écran en pixels d'appareil.
        facteurs.append(
            (f"{largeur}px×{densite}", verifier_palier(largeur, densite, largeur, "téléphone"))
        )

    for largeur, densite in HEROS_MONDES["paliers_larges"]:
        panneau_max: int | None = None
        if densite >= 2:
            panneau_max = HEROS_MONDES["panneau_dense"]
        elif largeur >= HEROS_MONDES["seuil_panneau_un_x"]:
            panneau_max = HEROS_MONDES["panneau_un_x"]
        contexte = "panneau" if panneau_max is not None else "plein cadre"
        facteurs.append(
            (f"{largeur}px×{densite} {contexte}", verifier_palier(largeur, densite, panneau_max, contexte))
        )

    pire = max(facteurs, key=lambda item: item[1])
    return [
        "OK     Héros des mondes : aucun agrandissement sur les "
        f"{len(facteurs)} combinaisons écran × densité testées, de 320 px à 3× à 2 560 px à 1×. "
        f"Plus grande source requise : {pire[1] * servie:.0f}px pour {servie}px servis ({pire[0]}).",
        "       Bandeau au ratio naturel sous 700 px, panneau contenu à 2× et au-delà de "
        f"{HEROS_MONDES['seuil_panneau_un_x']} px en 1×, plein cadre ailleurs. "
        "Le générateur d'images plafonnant à 1,06 Mpx, sous les 1,67 Mpx du master, ces largeurs sont le maximum atteignable aujourd'hui.",
    ]


def main() -> int:
    css = lire_css()
    try:
        lignes = verifier_titres(titres_des_pages())
        lignes += verifier_h1_accueil(css)
        lignes += verifier_modes(css)
        lignes += verifier_heros_mondes(css)
    except Echec as erreur:
        print(f"ÉCHEC — {erreur}", file=sys.stderr)
        return 1

    for ligne in lignes:
        print(ligne)
    print(
        "\nBudgets d'affichage : longueurs et nombres de lignes sont des estimations hors ligne "
        "(police système, avance moyenne, aucun rendu). Une validation visuelle humaine reste nécessaire."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
