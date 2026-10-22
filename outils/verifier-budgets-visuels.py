#!/usr/bin/env python3
"""Vérifie hors ligne les budgets d’affichage des titres et la couverture des modes.

Ce contrôle existe pour deux risques qu’aucun test du dépôt ne voyait :

  1. un `<title>` trop long, tronqué dans les résultats de recherche — le titre
     de l’accueil fait 73 caractères depuis qu’il reprend la formule du H1, et
     cette longueur a été acceptée par une personne, pas mesurée comme idéale ;
  2. un H1 qui déborde ou s’allonge sans que personne ne le remarque à 320 px.

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
import re
import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
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


def main() -> int:
    css = lire_css()
    try:
        lignes = verifier_titres(titres_des_pages())
        lignes += verifier_h1_accueil(css)
        lignes += verifier_modes(css)
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
