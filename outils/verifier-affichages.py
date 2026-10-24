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


# Les cinq commandes de l'en-tête compact sont plus exigeantes : elles se
# touchent au pouce, sans visée, et se serraient à 24 px sur téléphone.
# Le 23 octobre 2026, deux passages : 44 px d'abord (trop lourd : 149 px
# d'en-tête sur téléphone), puis 32 px sur téléphone, 36 px ailleurs en compact.
# Le plancher du contrôle vaut 32 px : c'est le minimum admis, pas la règle.
PLANCHER_COMMANDES_ENTETE_PX = 32


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


def regles(texte: str) -> list[tuple[str, str]]:
    """Toutes les règles (sélecteur, corps), y compris dans un bloc média.

    `blocs_de` exige un sélecteur exact ; ici les sélecteurs s'étalent sur
    plusieurs lignes (`:is(` + une liste), d'où cette recherche par fragment.
    """
    return [
        (correspondance.group(1).strip(), correspondance.group(2))
        for correspondance in re.finditer(r"([^{}]+)\{([^}]*)\}", texte)
    ]


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
    # Ajouté le 24 octobre 2026 : à 390 px, les liens légaux du pied de page
    # faisaient 19 px de haut et se touchaient — seuls écarts réels du balayage
    # WCAG 2.2 (2.5.8) sur les 98 pages.
    ("site.css", ".footer-legal a"),
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
    """L'en-tête compact ne doit pas rapetisser ses commandes sous 32 px."""
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
            if hauteur < PLANCHER_COMMANDES_ENTETE_PX:
                ligne = numero_ligne(texte, correspondance.start())
                erreurs.append(
                    f"site.css:{ligne} — commande de l'en-tête compact ramenée à "
                    f"min-height: {hauteur:g}px au lieu de {PLANCHER_COMMANDES_ENTETE_PX}px"
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


def controler_illustrations() -> list[str]:
    """Une illustration ne doit jamais être agrandie au-delà de sa source.

    Le 23 octobre 2026, l'illustration de la section « Aventure pédagogique »
    s'affichait sur 497 × 941 px : `aspect-ratio` ne fixe une dimension que si
    l'autre est automatique, et l'attribut `height="941"` du HTML tenait lieu de
    hauteur. L'image était donc étirée de 2,1 fois pour couvrir sa boîte, d'où
    des pixels visibles. Deux pièces doivent rester : la hauteur automatique
    dans la feuille et une déclaration `sizes` qui dit la vérité sur la largeur.
    """
    erreurs: list[str] = []
    site = (RACINE / "assets" / "css" / "site.css").read_text(encoding="utf-8")
    regle = re.search(r"\.english-promo-art img\s*\{([^}]*)\}", site)
    if not regle:
        erreurs.append("site.css — la règle .english-promo-art img est introuvable")
    else:
        contenu = regle.group(1)
        for declaration, message in (
            ("height: auto", "sans `height: auto`, l'attribut height du HTML fige la hauteur "
                             "et l'image est étirée 2,1 fois pour couvrir sa boîte"),
            ("aspect-ratio", "sans `aspect-ratio`, la boîte suit la hauteur de la source et "
                             "le bandeau change de hauteur selon la variante servie"),
            ("object-fit: cover", "sans `object-fit`, la déformation remplacerait le recadrage"),
        ):
            if declaration not in contenu:
                erreurs.append(f"site.css — .english-promo-art img : {declaration} manquant ; {message}")
    page = (RACINE / "apprendre.html").read_text(encoding="utf-8")
    figure = re.search(r'<figure class="english-promo-art">(.*?)</figure>', page, re.S)
    if not figure:
        erreurs.append("apprendre.html — la figure .english-promo-art est introuvable")
    else:
        bloc = figure.group(1)
        attendu = 'sizes="(max-width: 760px) calc(100vw - 4rem), 520px"'
        declarees = re.findall(r"sizes=\"([^\"]*)\"", bloc)
        # Les deux sources (AVIF et WebP) portent la même déclaration : une seule
        # occurrence laisserait l'autre format annoncer une autre largeur, et le
        # navigateur choisirait une variante trop petite pour ce format.
        if len(declarees) != 2 or set(declarees) != {"(max-width: 760px) calc(100vw - 4rem), 520px"}:
            erreurs.append(
                "apprendre.html — les deux sources de l'illustration doivent déclarer "
                "`(max-width: 760px) calc(100vw - 4rem), 520px` : " + attendu
            )
        if not re.search(r'<img[^>]*width="1672"[^>]*height="941"', bloc):
            erreurs.append(
                "apprendre.html — les dimensions intrinsèques de l'illustration (1672 × 941) "
                "ont disparu : la place ne serait plus réservée avant chargement"
            )
    # Le plafond de 520 px rend la déclaration `sizes` vraie dans toutes les
    # présentations ; sans lui, la colonne s'élargit et la variante choisie
    # devient trop petite pour la place occupée.
    if "width: min(100%, 520px)" not in site:
        erreurs.append("site.css — le plafond de 520 px de .english-promo-art a disparu")
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


def controler_densite_du_rendu_3d() -> list[str]:
    """Les décors 3D doivent se dessiner au pixel de l'écran, sans plafond.

    Le 22 octobre 2026, un décor plafonnait la densité à `min(devicePixelRatio,
    2)` : sur un téléphone à 3×, un tampon de 642 px était étiré sur 964 px de
    dalle, d'où un flou de 1,5×. Le 23 octobre, le héros des Mondes est devenu
    lui aussi un décor vectoriel : les deux fichiers sont donc soumis aux mêmes
    règles, sinon le second pourrait réintroduire ce que le premier a corrigé.
    """
    erreurs: list[str] = []
    for nom in ("anglais-aventure.js", "decor-atlas.js"):
        source = (RACINE / "assets" / "js" / nom).read_text(encoding="utf-8")
        plafond = re.search(
            r"Math\.min\(\s*(?:window\.)?devicePixelRatio(?:\s*\|\|\s*[\d.]+)?\s*,\s*([\d.]+)\s*\)",
            source,
        )
        if plafond:
            ligne = numero_ligne(source, plafond.start())
            erreurs.append(
                f"{nom}:{ligne} — la densité est plafonnée à {plafond.group(1)}× : "
                "au-delà, le tampon est étiré et le décor devient flou"
            )
        densite = re.search(r"DENSITE_MAX\s*=\s*([\d.]+)", source)
        if not densite or float(densite.group(1)) < 3:
            erreurs.append(
                f"{nom} — `DENSITE_MAX` doit valoir au moins 3 : en dessous, "
                "un écran de téléphone à 3× affiche un rendu agrandi"
            )
        budget = re.search(r"BUDGET_PIXELS\s*=\s*([\d_]+)", source)
        if not budget or int(budget.group(1).replace("_", "")) < 6_000_000:
            erreurs.append(
                f"{nom} — `BUDGET_PIXELS` doit rester à 6 Mpx au moins : "
                "un budget plus bas rabote la densité sur les grands écrans denses"
            )
    return erreurs


def controler_decor_du_heros() -> list[str]:
    """Le héros des Mondes doit garder son décor vectoriel **et** son repli.

    Le canvas remplace une image : s'il disparaît du document, ou si le repli
    cesse d'être fourni, la page se retrouve soit sans illustration, soit avec
    une image que rien n'affiche. Les deux sont vérifiés ensemble parce que
    c'est cet équilibre qui rend le remplacement sûr.
    """
    erreurs: list[str] = []
    html = (RACINE / "anglais-aventure.html").read_text(encoding="utf-8")
    if "data-decor-atlas" not in html:
        erreurs.append(
            "anglais-aventure.html — le canvas `data-decor-atlas` du héros a disparu : "
            "l'illustration redeviendrait une image à résolution finie"
        )
    if not re.search(r'<canvas[^>]*data-decor-atlas[^>]*role="img"[^>]*aria-label="[^"]{20,}"', html):
        erreurs.append(
            "anglais-aventure.html — le canvas du héros doit porter `role=\"img\"` et un "
            "`aria-label` descriptif, sinon le décor n'est annoncé par aucune aide technique"
        )
    if not re.search(r'<img[^>]*class="adventure-hero-art"[^>]*data-src="assets/images/', html):
        erreurs.append(
            "anglais-aventure.html — le repli `data-src` du héros est absent : sans WebGL, "
            "la page n'aurait aucune illustration"
        )
    source = (RACINE / "assets" / "js" / "decor-atlas.js").read_text(encoding="utf-8")
    for morceau, message in (
        ("webglcontextlost", "la perte de contexte WebGL doit basculer sur le repli"),
        ("data-srcset", "le repli doit rester différé (`data-srcset`) pour ne pas être téléchargé à chaque visite"),
    ):
        if morceau not in source:
            erreurs.append(f"decor-atlas.js — {message}")
    # Le chargement du repli doit se trouver dans la fonction d'échec, pas
    # seulement quelque part dans le fichier : c'est là qu'il sert.
    echec = re.search(r"const echouer = \(\) => \{(.*?)\n  \};", source, re.S)
    if not echec:
        erreurs.append("decor-atlas.js — la fonction d'échec `echouer` est introuvable")
    elif "image.dataset.src" not in echec.group(1) or "image.src =" not in echec.group(1):
        erreurs.append(
            "decor-atlas.js — la fonction d'échec ne charge plus le repli : sans WebGL, "
            "le héros resterait vide"
        )
    # Limite assumée, et mesurée : ce contrôle lit le code source, il ne
    # l'exécute pas. Une sortie ajoutée après `if (!image) return;`, ou une
    # condition rendue toujours fausse, neutralise le repli en laissant tous les
    # appels en place — deux mutations l'ont vérifié. C'est la mesure navigateur
    # (WebGL désactivé, repli chargé) qui prouve le comportement, pas cette porte.
    # Le présent contrôle garantit seulement que le mécanisme n'a pas été retiré.
    return erreurs


QUALITE_MINIMALE = {"avif": 78, "webp": 88}


def controler_qualite_d_encodage() -> list[str]:
    """Les variantes se servent en 1:1 : leur compression doit donc être haute.

    En qualité 60, l'AVIF du héros mesurait 31,9 dB à 800 px (32,8 dB en q72,
    33,2 dB en q78) : le flou de compression, superposé à un affichage 1:1 sur
    téléphone, se lit comme du pixel. Ce plancher interdit de redescendre la
    qualité pour gagner du poids sans assumer la perte de netteté.
    """
    chemin = RACINE / "outils" / "optimiser-images.py"
    source = chemin.read_text(encoding="utf-8")
    erreurs: list[str] = []
    blocs = re.findall(r'"qualites"\s*:\s*\{([^}]*)\}', source)
    if not blocs:
        return ["optimiser-images.py — aucune déclaration `\"qualites\"` trouvée"]
    for bloc in blocs:
        for format_image, minimum in QUALITE_MINIMALE.items():
            trouve = re.search(rf'"{format_image}"\s*:\s*(\d+)', bloc)
            if not trouve:
                erreurs.append(f"optimiser-images.py — qualité {format_image} absente de « {bloc.strip()} »")
            elif int(trouve.group(1)) < minimum:
                erreurs.append(
                    f"optimiser-images.py — {format_image} en qualité {trouve.group(1)}, "
                    f"sous le plancher {minimum} : les variantes servies en 1:1 deviendraient floues"
                )
    return erreurs


def controler_panneau_du_menu() -> list[str]:
    """Le panneau du menu doit rester atteignable sur un écran court.

    Le 23 octobre 2026, en paysage sur téléphone (844 × 390), le panneau partait
    de `top: 100%` sans plafond : il descendait à 522 px sur un écran de 390 px,
    et les derniers liens étaient hors d'atteinte. Trois protections doivent
    rester dans la même règle, faute de quoi le défaut revient silencieusement :
    un plafond mesuré, un défilement interne et un centrage qui ne pousse rien
    hors du cadre.
    """
    erreurs: list[str] = []
    texte = (RACINE / "assets" / "css" / "site.css").read_text(encoding="utf-8")
    panneaux = [
        corps for corps in blocs_de(texte, ".has-js .nav-links")
        if "overflow-y: auto" in corps
    ]
    if not panneaux:
        erreurs.append(
            "site.css — le panneau du menu n'a plus de défilement interne "
            "(overflow-y: auto) : sur un écran court, ses derniers liens sortent de l'écran"
        )
    else:
        # Une seule règle doit réunir les trois protections : réparties sur deux
        # blocs, l'une des deux peut disparaître sans que l'autre s'en aperçoive.
        proteges = [
            corps for corps in panneaux
            if "100dvh - var(--hauteur-entete" in corps
            and "justify-content: safe center" in corps
        ]
        if not proteges:
            corps = "\n".join(panneaux)
            if "100dvh - var(--hauteur-entete" not in corps:
                erreurs.append(
                    "site.css — le panneau du menu n'est plus plafonné à la place "
                    "restante sous l'en-tête (calc(100dvh - var(--hauteur-entete)))"
                )
            if "justify-content: safe center" not in corps:
                erreurs.append(
                    "site.css — le panneau défilable centre de nouveau ses liens : le "
                    "premier lien sort par le haut et devient inatteignable "
                    "(justify-content: safe center)"
                )
    # La hauteur de l'en-tête varie (logo, cran de texte, paysage) : elle doit être
    # mesurée, pas devinée par une constante.
    script = (RACINE / "assets" / "js" / "site.js").read_text(encoding="utf-8")
    if "--hauteur-entete" not in script:
        erreurs.append(
            "site.js — la hauteur de l'en-tête n'est plus publiée dans --hauteur-entete : "
            "le plafond du panneau ne suit plus le cran de texte ni le mode compact"
        )
    elif ".observe(header)" not in script:
        erreurs.append(
            "site.js — --hauteur-entete n'est plus remis à jour (ResizeObserver absent) : "
            "il se figerait à la hauteur du premier rendu"
        )
    elif "publierHauteurEntete();" not in script:
        erreurs.append(
            "site.js — --hauteur-entete n'est pas mesuré au chargement : le premier "
            "affichage garderait la valeur de repli de la feuille de style"
        )
    # Un seul bouton de préférence : les quatre réglages sont réunis dans un
    # panneau construit en JavaScript (aucune des 98 pages n'est modifiée) et
    # l'en-tête compact ne montre plus que « Menu » et « Personnalisation ».
    if "customize-settings" not in script:
        erreurs.append(
            "site.js — les réglages ne sont plus réunis derrière « Personnalisation » : "
            "l'en-tête compact réaffiche quatre commandes"
        )
    else:
        if "#site-customize-panel" not in script and "site-customize-panel" not in script:
            erreurs.append(
                "site.js — le panneau de « Personnalisation » a perdu son identifiant "
                "#site-customize-panel : le résumé ne décrit plus la zone qu'il ouvre "
                "(aria-controls)"
            )
        # Le déplacement doit se faire sur les trois éléments, sinon un réglage
        # reste dans l'en-tête et une troisième commande réapparaît.
        deplacement = re.search(
            r"\[([^\]]*)\]\.forEach\(\s*\(element\)\s*=>\s*\{[^}]*panneauPersonnalisation\.append\(element\)",
            script,
        )
        attendus = ("headerCompactToggle", "settings", "layoutSettings")
        manquants = [
            variable for variable in attendus
            if not deplacement or variable not in deplacement.group(1)
        ]
        if manquants:
            erreurs.append(
                "site.js — le panneau de « Personnalisation » ne déplace plus les quatre "
                "réglages : " + ", ".join(manquants) + " reste dans l'en-tête"
            )
    # Dans le panneau, chaque réglage est une ligne pleine largeur. Le préfixe
    # `html.has-js .site-header` n'est pas décoratif : les règles de l'en-tête
    # compact (`html.has-js .site-header.is-compact …`) portent plus de classes et
    # remettent les réglages côte à côte si on les cible avec un sélecteur plus
    # faible.
    lignes = [
        corps for selecteur, corps in regles(texte)
        if ".customize-settings-panel" in selecteur
        and "> summary" in selecteur
        and selecteur.startswith("html.has-js .site-header .customize-settings-panel")
        and "display: flex" in corps
        and "width: 100%" in corps
    ]
    if not lignes:
        erreurs.append(
            "site.css — les réglages du panneau « Personnalisation » ne sont plus des "
            "lignes pleine largeur (html.has-js .site-header .customize-settings-panel "
            ":is(...) { display: flex; width: 100% }) : un réglage réapparaît sur deux "
            "lignes ou déborde de son cadre"
        )
    # Un panneau de réglage ouvert reste dans le flux : en `position: static`, il
    # est contenu par la ligne qui le porte. Flottant, il sortait du panneau
    # (mesuré à x = 370 px pour 350 px de ligne).
    imbriques = [
        corps for selecteur, corps in regles(texte)
        if ".customize-settings-panel" in selecteur
        and "display-settings-panel" in selecteur
        and "position: static" in corps
    ]
    if not imbriques:
        erreurs.append(
            "site.css — les panneaux de réglage redeviennent flottants dans "
            "« Personnalisation » (position: static) : ouverts, ils débordent de la ligne "
            "qui les porte"
        )
    panneau = [
        corps for corps in blocs_de(texte, ".customize-settings-panel")
        if "position: absolute" in corps and "right: 0" in corps and "overflow: auto" in corps
    ]
    if not panneau:
        erreurs.append(
            "site.css — le panneau « Personnalisation » n'est plus ancré sous son bouton "
            "avec un défilement interne (position: absolute; right: 0; overflow: auto)"
        )
    # Deux commandes, deux colonnes égales : c'est la grille qui empêche le
    # libellé de se casser (« Parcour/s ») et qui laisse 32 px de haut à chaque
    # bouton. Une seule colonne sous 300 px, sinon deux colonnes de 19 px
    # débordent de leur cadre.
    grille = [
        corps for selecteur, corps in regles(texte)
        if ".header-compact-tools" in selecteur and "display: grid" in corps
        and "repeat(2, minmax(0, 1fr))" in corps
    ]
    if not grille:
        erreurs.append(
            "site.css — les deux commandes de l'en-tête compact ne sont plus en grille "
            "(repeat(2, minmax(0, 1fr))) sous 520 px : leurs largeurs divergent"
        )
    une_colonne = [
        corps for selecteur, corps in regles(texte)
        if ".header-compact-tools" in selecteur
        and "grid-template-columns: minmax(0, 1fr)" in corps
    ]
    if not une_colonne:
        erreurs.append(
            "site.css — le repli à une colonne sous 300 px a disparu : les commandes "
            "se compriment sous 50 px de large"
        )
    return erreurs



def controler_habillage_du_panneau() -> list[str]:
    """L'habillage du panneau « Personnalisation » doit rester dessiné, pas deviné.

    Trois défauts ont été vus à l'écran, pas à la lecture, dans la première
    version du panneau : un glyphe « ⌄ » dont le dessin dépendait de la police de
    substitution de la machine, quatre lignes grises identiques sans repère
    visuel (dont un bouton « Agrandir » centré au milieu des autres), et surtout
    un compteur de taille de texte en blanc sur blanc — 1:1 de contraste, donc
    invisible. Ce contrôle fixe les quatre décisions qui les corrigent.
    """
    erreurs: list[str] = []
    texte = (RACINE / "assets" / "css" / "site.css").read_text(encoding="utf-8")
    regles_css = regles(texte)

    # 1. Les chevrons sont des masques, pas des glyphes. `font-size: 0` est ce qui
    #    empêche le caractère d'origine de s'afficher sous le masque.
    chevrons = [
        corps for selecteur, corps in regles_css
        if ".customize-settings-chevron" in selecteur
        and "mask:" in corps
        and "font-size: 0" in corps
    ]
    if not chevrons:
        erreurs.append(
            "site.css — le chevron du panneau « Personnalisation » n'est plus un masque "
            "SVG (mask: … et font-size: 0) : son dessin dépend de la police de la machine"
        )
    # 2. Chaque réglage porte une icône, dessinée en masque sur son résumé.
    icones = [
        corps for selecteur, corps in regles_css
        if ".customize-settings-panel" in selecteur
        and "> summary::before" in selecteur.replace(") > summary::before", ") > summary::before")
        and "mask:" in corps
    ]
    if len(icones) < 3:
        erreurs.append(
            f"site.css — {len(icones)} icône(s) seulement sur les réglages du panneau "
            "(trois attendues, une par réglage) : les lignes redeviennent des libellés "
            "gris interchangeables"
        )
    # 3. Le compteur de taille de texte est lisible sur le fond du panneau : dans
    #    l'en-tête, il héritait du blanc de la barre marine.
    compteur = [
        corps for selecteur, corps in regles_css
        if ".display-text-level" in selecteur and ".customize-settings-panel" in selecteur
        and "color: var(--navy-ink)" in corps
    ]
    if not compteur:
        erreurs.append(
            "site.css — le compteur de taille de texte du panneau n'a plus de couleur "
            "propre (color: var(--navy-ink)) : il redevient blanc sur blanc, donc "
            "invisible (1:1 de contraste)"
        )
    # 4. Le texte des cartes de présentation tient 4,5:1 sur le fond bleu clair de la
    #    carte sélectionnée : --muted n'y donnait que 4,36:1.
    for selecteur in (".layout-choice-copy > span", ".layout-choice-hint"):
        lisibles = [
            corps for nom_regle, corps in regles_css
            if selecteur in nom_regle and "color: var(--text-soft)" in corps
        ]
        if not lisibles:
            erreurs.append(
                f"site.css — {selecteur} n'utilise plus --text-soft : --muted ne donne "
                "que 4,36:1 sur le fond d'une carte sélectionnée, sous le seuil AA de 4,5:1"
            )
    return erreurs



def controler_lecture_a_voix_haute() -> list[str]:
    """« Écouter la page » doit rester une lecture locale, à la demande.

    Ajoutée le 23 octobre 2026 pour l'inclusion : une personne qui lit
    difficilement, voit peu ou se fatigue peut écouter le contenu principal.
    Quatre garanties sont vérifiables dans le code : aucune lecture sans geste,
    aucune requête réseau, la langue de chaque bloc respectée, et un arrêt qui
    annule vraiment la voix. Ce contrôle lit la source ; c'est l'essai navigateur
    de `test-experience.cjs` qui prouve l'enchaînement.
    """
    erreurs: list[str] = []
    script = (RACINE / "assets" / "js" / "site.js").read_text(encoding="utf-8")
    # Le module va du commentaire de section jusqu'au bloc de réglages qui suit :
    # les fonctions de collecte sont déclarées avant la commande elle-même. On
    # délimite par la fin réelle du module plutôt que par un nombre de
    # caractères : un ajout de fonction décalait la fenêtre et faisait croire à
    # une disparition.
    depart = script.find("--- Écouter la page")
    index = script.find("construireLectureVocale")
    fin = script.find("\n  if (settings) {", index if index >= 0 else 0)
    if index < 0 or depart < 0 or fin < 0:
        return ["site.js — la commande « Écouter la page » a disparu du panneau de personnalisation"]
    corps = script[depart:fin]
    for morceau, message in (
        ("speechSynthesis", "la synthèse vocale de l'appareil n'est plus utilisée"),
        ("speechSynthesis.cancel()", "la lecture ne peut plus être arrêtée net"),
        ("closest(\"[lang]\")", "la langue du bloc n'est plus respectée : une réplique "
                                  "anglaise serait prononcée avec la voix française"),
        ("pagehide", "quitter la page ne coupe plus la voix"),
        ("aria-live", "l'état de la lecture n'est plus annoncé aux aides techniques"),
        ("checkVisibility", "la visibilité n'est plus vérifiée : le contenu d'un `<details>` "
                            "refermé garde une boîte dans Chromium et serait lu quand même"),
        ("element.checkVisibility({ checkVisibilityCSS: true, contentVisibilityAuto: true })",
         "la vérification de visibilité n'active plus `checkVisibilityCSS` : un contenu "
         "masqué par le style passerait"),
        ("element.innerText", "le texte lu ne suit plus la mise en page : deux phrases séparées "
                              "par un élément mis en bloc s'entendraient collées"),
        ("const VITESSES = [0.75, 1, 1.25, 1.5]", "les vitesses de lecture ont disparu : une "
                                                  "personne qui lit lentement ne peut plus ralentir la voix"),
        ("enonce.rate = vitesse", "le débit choisi n'est plus appliqué à la lecture"),

        ("readAloudBack", "le retour au passage précédent a disparu"),
        ("savePreference(CLE_VITESSE", "la vitesse choisie n'est plus conservée sur l'appareil"),
    ):
        if morceau not in corps:
            erreurs.append(f"site.js — {message}")
    # Aucun envoi réseau : ni requête, ni service tiers, ni clé.
    for interdit in ("fetch(", "XMLHttpRequest", "speechsynthesis-api", "api.openai", "https://api."):
        if interdit in corps:
            erreurs.append(
                f"site.js — la lecture à voix haute contient « {interdit} » : le texte ne doit "
                "jamais quitter l'appareil"
            )
    # La commande vit dans le panneau, pas dans l'en-tête : celui-ci garde deux boutons.
    # La commande doit être *ajoutée* à la liste des blocs du panneau, et non
    # seulement construite : une fonction jamais appelée ne s'affiche nulle part.
    if not re.search(r"\[headerCompactToggle, settings, layoutSettings, lectureVocale\]", script):
        erreurs.append(
            "site.js — la lecture à voix haute n'est plus placée dans le panneau Personnalisation : "
            "la commande est construite mais jamais affichée"
        )
    # Le nom accessible doit contenir le texte visible, sinon axe le signale
    # (`label-content-name-mismatch`) et une personne qui dicte à la voix ne
    # retrouve plus le bouton qu'elle voit.
    for texte, nom in re.findall(
        r'boutonLecture\.textContent = "([^"]+)"[\s\S]{0,400}?'
        r'boutonLecture\.setAttribute\("aria-label", "([^"]+)"\)',
        corps,
    ):
        if texte not in nom:
            erreurs.append(
                f'site.js — le nom accessible « {nom} » ne reprend pas le texte visible '
                f'« {texte} » : une commande dictée à la voix ne serait pas reconnue'
            )
    # Le jeton de génération doit être vérifié dans les deux rappels : sans lui,
    # une énonciation annulée relance la file et la lecture se dédouble.
    if corps.count("if (jeton !== generation) return;") < 2:
        erreurs.append(
            "site.js — le jeton de génération manque dans au moins un rappel : une énonciation "
            "annulée peut relancer la file et la lecture se dédoubler"
        )
    # L'arrêt doit annuler la voix dans sa propre fonction, pas seulement au
    # démarrage : une commande qui n'arrête rien laisse parler l'appareil.
    arret = re.search(r"const arreter = \(motif\) => \{(.*?)\n    \};", corps, re.S)
    if not arret or "speechSynthesis.cancel()" not in arret.group(1):
        erreurs.append(
            "site.js — la fonction d'arrêt n'annule plus la synthèse : le bouton « Arrêter » "
            "laisserait l'appareil parler"
        )
    css = (RACINE / "assets" / "css" / "site.css").read_text(encoding="utf-8")
    for declaration in (".lecture-en-cours", "outline"):
        if declaration not in css:
            erreurs.append(
                "site.css — le bloc en cours de lecture n'est plus marqué : la personne qui suit "
                "des yeux perd le fil"
            )
            break
    # La valeur compte, pas seulement sa présence : 24 px passerait la recherche
    # de texte tout en cassant la cible tactile.
    selecteur_vitesse = re.search(
        r"\.read-aloud-speed\s+select\s*\{[^}]*min-height:\s*([0-9.]+)px", css
    )
    if not selecteur_vitesse or float(selecteur_vitesse.group(1)) < 44:
        erreurs.append(
            "site.css — le sélecteur de vitesse doit garder une cible de 44 px : "
            f"valeur trouvée {selecteur_vitesse.group(1) if selecteur_vitesse else 'aucune'}"
        )
    if not re.search(r"\.lecture-en-cours\s*\{[^}]*outline:\s*3px", css):
        erreurs.append(
            "site.css — le bloc en cours de lecture n'a plus de contour visible "
            "(.lecture-en-cours { outline: 3px … })"
        )
    return erreurs


def controler_pied_de_page() -> list[str]:
    """Le bas de page se lit centré, sur une colonne, sans ponctuation orpheline.

    Le 23 octobre 2026, la personne responsable du site a signalé un pied de page
    « anarchique » : le script qui met chaque phrase en début de ligne découpait
    aussi le pied de page, si bien qu'un point final isolé après un lien formait
    une ligne à lui seul ; et le bloc du bas mêlait droits, liens légaux et note
    de version dans un flux qui se cassait au hasard. Elle a ensuite demandé que
    ce bas de page soit centré. Quatre pièces doivent rester : plus de découpage
    dans le pied de page, une ponctuation seule rattachée à sa phrase, une seule
    colonne centrée, et une liste légale sans puce ni filet.
    """
    erreurs: list[str] = []
    script = (RACINE / "assets" / "js" / "site.js").read_text(encoding="utf-8")

    # 1. Le découpage en phrases ne s'applique qu'au contenu principal.
    if '.site-footer' in script.split("Chaque phrase de contenu")[1].split("})();")[0]:
        erreurs.append(
            "site.js — le découpage en phrases s'applique de nouveau au pied de page : "
            "ses mentions légales se retrouvent coupées en blocs"
        )
    # 2. Une ponctuation seule rejoint la phrase précédente au lieu de former un bloc.
    if "\u0070{L}\u0070{N}" not in script and r"\p{L}\p{N}" not in script:
        erreurs.append(
            "site.js — le découpage ne vérifie plus qu'un morceau contient une lettre ou un "
            "chiffre : un point final isolé après un lien redevient une ligne à lui seul"
        )
    # 2 bis. Une ponctuation qui ouvre le texte appartient au lien qui précède : on
    # ne découpe pas, sinon elle s'affiche collée devant la phrase suivante.
    if "if (!phrases.length) return;" not in script:
        erreurs.append(
            "site.js — un texte qui commence par une ponctuation est de nouveau découpé : "
            "le point du lien précédent s'affiche collé devant la phrase suivante"
        )

    texte = (RACINE / "assets" / "css" / "site.css").read_text(encoding="utf-8")
    # Recherche ciblée : après un bloc média, le balayage générique `regles()`
    # démarre sur une accolade fermante et manque la règle suivante.
    bas = re.search(r"\.footer-bottom\s*\{([^}]*)\}", texte)
    manquants = [
        declaration
        for declaration in (
            "display: grid",
            "grid-template-columns: minmax(0, 1fr)",
            "justify-items: center",
            "text-align: center",
        )
        if not bas or declaration not in bas.group(1)
    ]
    if manquants:
        erreurs.append(
            "site.css — le bas de page n'est plus une colonne centrée "
            f"({', '.join(manquants)} manquant) : droits, liens et note de version "
            "se répartissent gauche et droite et laissent des trous"
        )
    # La règle globale `p { text-align: start }` s'applique directement aux
    # paragraphes du pied de page et gagne sur l'héritage : sans un centrage
    # explicite, les droits et la note de version restent alignés à gauche dans
    # un bloc centré (constaté le 23 octobre 2026, capture à l'appui).
    paragraphes = re.search(r"\.footer-bottom p\s*\{([^}]*)\}", texte)
    if not paragraphes or "text-align: center" not in paragraphes.group(1):
        erreurs.append(
            "site.css — les paragraphes du bas de page ne sont pas centrés "
            "(.footer-bottom p { text-align: center }) : la règle globale "
            "`p { text-align: start }` les réaligne à gauche dans un bloc centré"
        )
    legal = re.search(r"\.footer-legal\s*\{([^}]*)\}", texte)
    if not legal or "list-style: none" not in legal.group(1) or "justify-content: center" not in legal.group(1):
        erreurs.append(
            "site.css — les liens légaux ne sont plus une liste centrée sans puce "
            "(.footer-legal { list-style: none; justify-content: center }) : une puce "
            "ou un alignement à gauche casse le bloc"
        )
    if re.search(r"\.footer-legal li \+ li\s*\{[^}]*border-left", texte):
        erreurs.append(
            "site.css — un filet vertical sépare de nouveau les liens légaux : quand la "
            "rangée se replie, il ouvre la ligne et se lit comme une barre orpheline"
        )
    telephone = re.search(r"@media \(max-width: 520px\) \{(.*?)\n\}", texte, re.S)
    if not telephone or "max-width: 20rem" not in telephone.group(1):
        erreurs.append(
            "site.css — la liste légale n'est plus bornée sur téléphone "
            "(@media (max-width: 520px) { .footer-legal { max-width: 20rem } }) : "
            "à 390 px quatre entrées tiennent sur une ligne et la cinquième retombe seule"
        )

    # 3. Les pages portent la liste, pas la suite de liens séparés par des points.
    pages = sorted(chemin for chemin in RACINE.glob("*.html"))
    fautives = []
    for page in pages:
        contenu = page.read_text(encoding="utf-8")
        if '<ul class="footer-legal">' not in contenu:
            fautives.append(page.name)
    if fautives:
        erreurs.append(
            f"{len(fautives)} page(s) n'ont pas la liste légale en pied de page "
            f"({', '.join(fautives[:3])}…) : les séparateurs peuvent s'y retrouver "
            "orphelins en fin de ligne"
        )
    return erreurs


CONTROLES = (
    ("tailles de texte", controler_tailles_de_texte),
    ("cibles tactiles", controler_cibles_tactiles),
    ("en-tête compact", controler_en_tete_compact),
    ("panneau du menu", controler_panneau_du_menu),
    ("mesure de lecture", controler_mesure_de_lecture),
    ("plafonds d'images par densité", controler_plafonds_d_images),
    ("illustrations non agrandies", controler_illustrations),
    ("pistes de grille", controler_pistes_de_grille),
    ("césure des mots longs", controler_cesure),
    ("densité du rendu 3D", controler_densite_du_rendu_3d),
    ("décor du héros et son repli", controler_decor_du_heros),
    ("qualité d'encodage des images", controler_qualite_d_encodage),
    ("habillage du panneau", controler_habillage_du_panneau),
    ("pied de page", controler_pied_de_page),
    ("lecture à voix haute", controler_lecture_a_voix_haute),
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
        f"commandes d’en-tête ≥ {PLANCHER_COMMANDES_ENTETE_PX}px, "
        "plafonds d’image par densité, mesure de lecture)."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
