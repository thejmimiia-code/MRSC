#!/usr/bin/env python3
"""Contrôle des invariants d'affichage, tous formats confondus.

Ce que ce script vérifie a été **mesuré dans un navigateur** (Chromium sans
interface) sur 13 pages, 19 formats d'écran, 6 présentations, 5 tailles de texte
et les deux réglages de contraste et d'espacement. La mesure complète demande un
navigateur ; la porte de CI, elle, doit tourner partout. Ce contrôle-ci vérifie
donc que les règles sur lesquelles la mesure reposait sont toujours là, et
nomme le fichier et la ligne quand l'une disparaît.

Il n'affirme pas que la page s'affiche bien : il affirme que les garde-fous
d'affichage n'ont pas été retirés par inadvertance.

Usage :
    python3 outils/verifier-affichages.py
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
FEUILLES = (
    RACINE / "assets" / "css" / "site.css",
    RACINE / "assets" / "css" / "anglais-aventure.css",
)

PLANCHER_TEXTE_REM = 0.75  # 12 px à 16 px de base
PLANCHER_CIBLE_PX = 24  # WCAG 2.2, 2.5.8


CRAN_LE_PLUS_REDUIT = 0.75  # le plus petit réglage de taille de texte du site


def plancher_au_dessus_du_seuil(plancher: str) -> bool:
    """Le plancher tient-il 12 px au cran de texte le plus réduit ?"""
    try:
        if plancher.endswith("px"):
            return float(plancher.removesuffix("px")) >= 12
        if plancher.endswith("rem"):
            return float(plancher.removesuffix("rem")) * 16 * CRAN_LE_PLUS_REDUIT >= 12
    except ValueError:
        return True
    return True


def numero_ligne(texte: str, position: int) -> int:
    return texte.count("\n", 0, position) + 1


def taille_rem(valeur: str) -> float | None:
    correspondance = re.fullmatch(r"\.?\d+(?:\.\d+)?rem", valeur.strip())
    if not correspondance:
        return None
    return float(valeur.strip().removesuffix("rem"))


def controler_tailles_de_texte() -> list[str]:
    """Aucune taille de texte sous 12 px, hors réglage explicite de la personne.

    Le réglage « texte 50 % » de la page est un choix assumé : il n'est pas
    examiné ici, et il est signalé dans la documentation.
    """
    erreurs: list[str] = []
    for feuille in FEUILLES:
        texte = feuille.read_text(encoding="utf-8")
        for correspondance in re.finditer(r"font-size:\s*([^;{}]+);", texte):
            # `!important` ne doit pas soustraire une valeur au contrôle.
            valeur = correspondance.group(1).replace("!important", "").strip()
            # `max(12px, .75rem)` accroche la taille à un plancher : c'est le
            # seul cas de fonction accepté, et il faut que le plancher tienne.
            if valeur.startswith("max("):
                plancher = valeur[4:].split(",")[0].strip()
                if plancher_au_dessus_du_seuil(plancher):
                    continue
                ligne = numero_ligne(texte, correspondance.start())
                erreurs.append(
                    f"{feuille.name}:{ligne} — plancher « {valeur} » inférieur à 12 px"
                )
                continue
            # `clamp(min, …)` : c'est le premier argument qui fixe le plancher.
            # Il se juge au cran de texte le plus réduit du site (75 %), où 1rem
            # vaut 12 px : un minimum de .75rem y tombe à 9 px.
            if valeur.startswith("clamp("):
                plancher = valeur[6:].split(",")[0].strip()
                if not plancher_au_dessus_du_seuil(plancher):
                    ligne = numero_ligne(texte, correspondance.start())
                    erreurs.append(
                        f"{feuille.name}:{ligne} — clamp « {valeur} » descend sous "
                        f"12 px au cran de texte le plus réduit"
                    )
                continue
            if "var(" in valeur or "calc(" in valeur:
                continue
            rem = taille_rem(valeur)
            px = None
            if valeur.endswith("px"):
                try:
                    px = float(valeur.removesuffix("px"))
                except ValueError:
                    px = None
            trop_petit = (rem is not None and rem < PLANCHER_TEXTE_REM) or (
                px is not None and px < 12
            )
            if trop_petit:
                ligne = numero_ligne(texte, correspondance.start())
                erreurs.append(
                    f"{feuille.name}:{ligne} — taille de texte {valeur} "
                    f"sous le plancher de {PLANCHER_TEXTE_REM}rem (12 px)"
                )
    return erreurs


def blocs_de(texte: str, selecteur: str) -> list[str]:
    """Corps de toutes les règles dont le sélecteur est exact, dans l'ordre."""
    motif = re.compile(r"(?:^|\})\s*" + re.escape(selecteur) + r"\s*\{([^}]*)\}", re.MULTILINE)
    return [correspondance.group(1) for correspondance in motif.finditer(texte)]


def hauteur_minimale_effective(blocs: list[str]) -> float | None:
    """Valeur de min-height qui l'emporte : la dernière déclarée."""
    valeur = None
    for corps in blocs:
        for correspondance in re.finditer(r"min-height:\s*([0-9.]+)(px|rem)", corps):
            nombre = float(correspondance.group(1))
            valeur = nombre * 16 if correspondance.group(2) == "rem" else nombre
    return valeur


CIBLES = (
    ("site.css", ".identity-contact"),
    ("site.css", ".nav-links a"),
    ("site.css", ".statute-link"),
    ("site.css", ".home-action-link"),
    ("anglais-aventure.css", ".adventure-breadcrumb a"),
)


def controler_cibles_tactiles() -> list[str]:
    erreurs: list[str] = []
    for nom, selecteur in CIBLES:
        feuille = RACINE / "assets" / "css" / nom
        blocs = blocs_de(feuille.read_text(encoding="utf-8"), selecteur)
        if not blocs:
            erreurs.append(f"{nom} — règle {selecteur} introuvable")
            continue
        hauteur = hauteur_minimale_effective(blocs)
        if hauteur is None or hauteur < PLANCHER_CIBLE_PX:
            erreurs.append(
                f"{nom} — {selecteur} : min-height effective {hauteur} "
                f"au lieu de {PLANCHER_CIBLE_PX}px (cible tactile minimale)"
            )
    return erreurs


def controler_en_tete_compact() -> list[str]:
    """L'en-tête compact ne doit pas rapetisser ses commandes sous 24 px."""
    texte = (RACINE / "assets" / "css" / "site.css").read_text(encoding="utf-8")
    # Seules les règles qui visent les commandes elles-mêmes comptent : le
    # conteneur de l'en-tête, lui, a le droit d'avoir min-height: 0. La dernière
    # déclaration l'emporte, comme dans la cascade.
    # Toute règle qui vise les commandes doit tenir le plancher : les règles
    # diffèrent par leur portée média, si bien qu'une valeur basse déclarée
    # quelque part finit par s'appliquer à un format d'écran.
    erreurs = []
    vues = 0
    for correspondance in re.finditer(r"([^{}]+)\{([^}]*)\}", texte):
        selecteur, corps = correspondance.group(1), correspondance.group(2)
        if ".is-compact" not in selecteur:
            continue
        if not re.search(r"nav-toggle|header-compact-toggle|> summary", selecteur):
            continue
        # `min-height: 0` s'écrit sans unité : c'est justement la valeur qui
        # annule une cible tactile.
        for valeur in re.finditer(r"min-height:\s*([0-9.]+)(px|rem)?\b", corps):
            vues += 1
            hauteur = float(valeur.group(1))
            if (valeur.group(2) or "") == "rem":
                hauteur *= 16
            if hauteur < PLANCHER_CIBLE_PX:
                ligne = numero_ligne(texte, correspondance.start())
                erreurs.append(
                    f"site.css:{ligne} — commande de l'en-tête compact ramenée à "
                    f"min-height: {hauteur:g}px au lieu de {PLANCHER_CIBLE_PX}px"
                )
    if vues == 0:
        erreurs.append("site.css — aucune min-height déclarée sur les commandes de l'en-tête compact")
    return erreurs


def controler_mesure_de_lecture() -> list[str]:
    texte = (RACINE / "assets" / "css" / "site.css").read_text(encoding="utf-8")
    blocs = blocs_de(texte, "main .container p")
    if not blocs:
        return ["site.css — règle « main .container p » (mesure de lecture) introuvable"]
    if not any(re.search(r"max-width:\s*(?:min\([^)]*\)|[0-9.]+ch)", corps) for corps in blocs):
        return ["site.css — la mesure de lecture n'a plus de max-width en ch"]
    return []


def controler_plafonds_d_images() -> list[str]:
    """Chaque héros garde ses paliers de densité, sinon l'image est étirée."""
    erreurs: list[str] = []
    site = (RACINE / "assets" / "css" / "site.css").read_text(encoding="utf-8")
    for seuil in ("2dppx", "2.5dppx", "3dppx", "3.5dppx"):
        motif = rf"@media\s*\(min-resolution:\s*{re.escape(seuil)}\)\s*\{{[^}}]*home-hero-visual[^}}]*max-width"
        if not re.search(motif, site):
            erreurs.append(
                f"site.css — palier {seuil} absent ou incomplet pour .home-hero-visual"
            )
    aventures = (RACINE / "assets" / "css" / "anglais-aventure.css").read_text(encoding="utf-8")
    for plafond in ("836px", "668px", "557px", "477px"):
        if f"--hero-art-max: {plafond}" not in aventures:
            erreurs.append(
                f"anglais-aventure.css — plafond {plafond} du héros des mondes absent"
            )
    if "max-width: min(100%, 1400px)" not in site:
        erreurs.append(
            "site.css — .home-hero-visual n'est plus plafonné à la largeur de sa source (1400px)"
        )
    return erreurs


def controler_pistes_de_grille() -> list[str]:
    """`1fr` vaut `minmax(auto, 1fr)` : la largeur minimale du contenu peut
    élargir la piste et faire défiler la page. `minmax(0, 1fr)` l'empêche."""
    erreurs = []
    for feuille in FEUILLES:
        texte = feuille.read_text(encoding="utf-8")
        for correspondance in re.finditer(r"grid-template-columns:\s*1fr\s*;", texte):
            ligne = numero_ligne(texte, correspondance.start())
            erreurs.append(
                f"{feuille.name}:{ligne} — piste « 1fr » nue : écrire minmax(0, 1fr)"
            )
    return erreurs


def controler_cesure() -> list[str]:
    texte = (RACINE / "assets" / "css" / "site.css").read_text(encoding="utf-8")
    erreurs = []
    if not re.search(r"main\s*\{\s*overflow-wrap:\s*break-word", texte):
        erreurs.append("site.css — la césure des mots longs (overflow-wrap) a disparu")
    if not re.search(r"\.trace-list li[^{]*\{[^}]*min-width:\s*0", texte):
        erreurs.append("site.css — les éléments de liste de traçabilité n'ont plus min-width: 0")
    if "overflow-wrap: anywhere" not in texte:
        erreurs.append("site.css — la césure des tokens insécables (anywhere) a disparu")
    return erreurs


CONTROLES = (
    ("tailles de texte", controler_tailles_de_texte),
    ("cibles tactiles", controler_cibles_tactiles),
    ("en-tête compact", controler_en_tete_compact),
    ("mesure de lecture", controler_mesure_de_lecture),
    ("plafonds d'images par densité", controler_plafonds_d_images),
    ("pistes de grille", controler_pistes_de_grille),
    ("césure des mots longs", controler_cesure),
)


def main() -> int:
    total = 0
    for nom, controle in CONTROLES:
        erreurs = controle()
        if erreurs:
            total += len(erreurs)
            print(f"ÉCHEC — {nom}", file=sys.stderr)
            for erreur in erreurs:
                print(f"    {erreur}", file=sys.stderr)
        else:
            print(f"OK     {nom}")
    if total:
        print(
            f"\nAffichage : {total} garde-fou(s) manquant(s). La mesure de référence "
            "est décrite dans docs/rd/formats-affichage.md.",
            file=sys.stderr,
        )
        return 1
    print(
        f"\nAffichage : les {len(CONTROLES)} garde-fous des formats d’écran sont en place "
        f"(texte ≥ {PLANCHER_TEXTE_REM}rem, cibles ≥ {PLANCHER_CIBLE_PX}px, "
        "plafonds d’image par densité, mesure de lecture)."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
