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

import os
import re
import sys
from pathlib import Path

#: Racine lue par le contrôle. La surcharge sert un usage précis : rejouer les
#: mutations sur une copie du dépôt (`outils/test_mutations_affichages.py`) sans
#: toucher aux fichiers réels. Une porte qui modifie l'arbre qu'elle contrôle
#: finit par le laisser modifié après un échec.
RACINE = Path(os.environ.get("MRSC_RACINE") or Path(__file__).resolve().parent.parent).resolve()
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

    Le 5 novembre 2026, ce lecteur appariait les accolades avec une expression
    régulière. Il le faisait mal, et il le savait : un commentaire de ce fichier
    disait déjà « après un bloc média, le balayage générique regles() démarre
    sur une accolade fermante et manque la règle suivante ». Ce jour-là, la
    suppression d'un bloc média voisin a fait disparaître de la lecture la règle
    de grille de `.header-compact-tools` — fichier intact, contenu intact,
    appariement différent — et le contrôle a crié au lieu de lire. On parcourt
    donc les accolades en profondeur : chaque corps va avec son préambule, et un
    bloc média refermé ne fabrique pas de règle.
    """
    sans_commentaires = re.sub(r"/\*.*?\*/", " ", texte, flags=re.S)
    resultat: list[tuple[str, str]] = []
    pile: list[str] = []
    tampon: list[str] = []
    for caractere in sans_commentaires:
        if caractere == "{":
            pile.append("".join(tampon).strip())
            tampon = []
        elif caractere == "}":
            corps = "".join(tampon)
            preambule = pile.pop() if pile else ""
            # Un préambule d'arobase (`@media`, `@keyframes`) ouvre un bloc qui
            # contient des règles : son corps, à la fermeture, est vide. Un corps
            # vide n'est pas une règle, et un `@media` n'a pas de déclarations.
            if corps.strip() and preambule and not preambule.startswith("@"):
                resultat.append((preambule, corps))
            tampon = []
        else:
            tampon.append(caractere)
    return resultat


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


def controler_entete_reduit_persistant() -> list[str]:
    """Le mode réduit survit au clic sur une entrée du menu.

    Le 5 novembre 2026, « Réduire » n'était pas mémorisé. Chaque entrée du menu
    charge une autre page, où `setHeaderCompact` repartait du seul format de
    fenêtre : mesuré en Chromium à 1 440 px, l'en-tête passait de 49 px à
    198 px au moment du clic, et à 980 × 440 de 49 px à 194 px. La préférence
    doit être lue au chargement, écrite par la bascule, suivie quand un autre
    onglet la change, et gagner sur les changements de format — sinon le saut
    revient par une porte différente.

    Ce contrôle ne mesure pas le rendu : il tient les cinq bouts de `site.js`
    que l'essai navigateur (`test-experience.cjs`) a vus corriger le défaut.
    """
    erreurs: list[str] = []
    script = (RACINE / "assets" / "js" / "site.js").read_text(encoding="utf-8")
    marqueurs = (
        (
            'const CLE_ENTETE_COMPACTE = "mrsc-entete-compacte";',
            "la clé de la préférence d'en-tête compact a disparu",
        ),
        (
            "preferenceCompacte = lirePreferenceEnteteCompacte();",
            "la préférence d'en-tête compact n'est plus lue au chargement",
        ),
        (
            "const etatCompactVoulu = () => preferenceCompacte ?? Boolean(compactViewport?.matches);",
            "la préférence d'en-tête compact ne gagne plus sur le format de fenêtre",
        ),
        (
            'savePreference(CLE_ENTETE_COMPACTE, compact ? "oui" : "non");',
            "le choix de « Réduire » / « Agrandir » n'est plus enregistré",
        ),
        (
            "if (event.key === null || event.key === CLE_ENTETE_COMPACTE) {",
            "la préférence d'en-tête compact n'est plus suivie d'un onglet à l'autre",
        ),
    )
    for fragment, message in marqueurs:
        if fragment not in script:
            erreurs.append(f"site.js — {message} : le mode réduit sauterait au clic dans le menu")
    # Trois appels : chargement, rappel de stockage, franchissement du seuil de
    # format. Un seul ne suffit pas : la page d'arrivée serait la seule corrigée.
    appels = script.count("setHeaderCompact(etatCompactVoulu());")
    if appels < 3:
        erreurs.append(
            f"site.js — la préférence d'en-tête compact n'est relue que {appels} fois "
            "sur 3 (chargement, autre onglet, changement de format) : le mode réduit "
            "sauterait au clic dans le menu ou au premier redimensionnement"
        )
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
    """Un plafond de densité ne se justifie que pour une source à résolution finie.

    L'image d'accueil restaurée reste limitée à 700 CSS px pour sa source
    de 1400 px à densité 2. Les logos et les décors gardent leurs plafonds.
    """
    erreurs: list[str] = []
    site = (RACINE / "assets" / "css" / "site.css").read_text(encoding="utf-8")
    for seuil in ("3dppx", "3.5dppx"):
        if not re.search(rf"@media\s*\(min-resolution:\s*{re.escape(seuil)}\)[^@]*max-width:\s*\d+px", site):
            erreurs.append(f"site.css — les logos perdent leur plafond de densité {seuil}")
    aventures = (RACINE / "assets" / "css" / "anglais-aventure.css").read_text(encoding="utf-8")
    for plafond in ("836px", "668px", "557px", "477px"):
        if f"--hero-art-max: {plafond}" not in aventures:
            erreurs.append(
                f"anglais-aventure.css — plafond {plafond} du héros des mondes absent"
            )
    if "max-width: min(100%, 700px)" not in site:
        erreurs.append(
            "site.css — .home-hero-visual n'est plus borné à la largeur de la source à densité 2 (700px)"
        )
    return erreurs


def controler_illustrations() -> list[str]:
    """Un héros ne doit jamais être agrandi : il est vectoriel ou servi à sa taille.

    Le 23 octobre 2026, l'illustration de la section « Aventure pédagogique »
    s'affichait sur 497 × 941 px : `aspect-ratio` ne fixe une dimension que si
    l'autre est automatique, et l'attribut `height="941"` du HTML tenait lieu de
    hauteur. L'image était donc étirée de 2,1 fois pour couvrir sa boîte, d'où
    des pixels visibles.

    Les images antérieures sont restaurées après rejet des tracés SVG.
    Le contrôle exige les fichiers retenus, leurs dimensions, leurs variantes
    adaptatives et un ratio de boîte égal à celui de la source. La densité
    réellement servie est mesurée par verifier-graphismes.cjs.
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
                             "et l'image est étirée pour couvrir sa boîte"),
            ("aspect-ratio", "sans `aspect-ratio`, la boîte suit la hauteur de la source et "
                             "le bandeau change de hauteur selon la variante servie"),
            ("object-fit: contain", "sans `object-fit`, la déformation remplacerait le recadrage"),
        ):
            if declaration not in contenu:
                erreurs.append(f"site.css — .english-promo-art img : {declaration} manquant ; {message}")

    attends = (
        # page, figure, fichier source, largeur, hauteur
        ("index.html", "home-hero-visual", "accueil-logo-mrsc-3d.jpg", 1400, 933),
        ("apprendre.html", "english-promo-art", "mondes-savoirs-hero.jpg", 1672, 941),
    )
    for page, figure, fichier, largeur, hauteur in attends:
        texte = (RACINE / page).read_text(encoding="utf-8")
        bloc = re.search(rf'<figure class="{figure}"[^>]*>(.*?)</figure>', texte, re.S)
        if not bloc:
            erreurs.append(f"{page} — la figure .{figure} est introuvable")
            continue
        corps = bloc.group(1)
        if "<picture" not in corps or "srcset=" not in corps:
            erreurs.append(f"{page} — variantes adaptatives absentes")
        image = re.search(r"<img[^>]*>", corps)
        if not image:
            erreurs.append(f"{page} — la figure .{figure} n'a plus d'image")
            continue
        balise = image.group(0)
        if f'src="assets/images/{fichier}"' not in balise:
            erreurs.append(f"{page} — la figure .{figure} ne pointe plus sur {fichier}")
        if not re.search(r'alt="[^"]+"', balise):
            erreurs.append(f"{page} — l'illustration a perdu son texte alternatif")
        if not re.search(rf'width="{largeur}"', balise) or not re.search(rf'height="{hauteur}"', balise):
            erreurs.append(
                f"{page} — les dimensions intrinsèques de {fichier} doivent rester "
                f"{largeur} × {hauteur} : la place est réservée avant chargement, "
                "et un rapport différent déforme le tracé"
            )
        fichier_source = RACINE / "assets" / "images" / fichier
        if not fichier_source.is_file():
            erreurs.append(f"assets/images/{fichier} — fichier absent")
            continue
    # Le ratio de boîte doit suivre la source restaurée, sans rognage.
    corps = re.search(r"\.english-promo-art img\s*\{([^}]*)\}", site)
    if corps is None:
        erreurs.append("site.css — la règle .english-promo-art img a disparu")
    else:
        ratio = re.search(r"aspect-ratio:\s*([\d.]+)\s*/\s*([\d.]+)", corps.group(1))
        if ratio is None:
            erreurs.append("site.css — .english-promo-art img n'a plus de ratio explicite")
        else:
            attendu = 1672 / 941
            obtenu = float(ratio.group(1)) / float(ratio.group(2))
            if abs(obtenu - attendu) > 1e-6:
                erreurs.append(
                    f"site.css — aspect-ratio {ratio.group(1)} / {ratio.group(2)} ne correspond plus "
                    f"à l’image 1672 × 941 ({attendu:.3f}) : le dessin serait recadré"
                )
    # Le plafond de l'illustration n'est pas un ornement : sans lui, la
    # déclaration `sizes` ment au navigateur (874 px rendus, variante de
    # 1 200 px servie). Il doit être un `max-width`, pas un `width` : depuis que
    # le panneau est en `flex-wrap`, `flex-basis: 100%` remplace la largeur de
    # la boîte et un plafond en `width` ne décide plus rien (densité 0,91
    # mesurée le 31 octobre 2026).
    # La recherche porte sur la règle, pas sur le texte : `@media (max-width:
    # 520px)` contient la même chaîne, et le garde-fou se croyait satisfait
    # alors que le plafond n'existait plus — le banc de mutation l'a montré.
    if re.search(r"\.english-promo-art\s*\{[^{}]*max-width:\s*520px", site) is None:
        erreurs.append(
            "site.css — le plafond de 520 px de .english-promo-art a disparu "
            "(il s'écrit `max-width`, sinon `flex-basis` le rend inopérant)"
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


def corps_de_fonction(script: str, nom: str) -> str | None:
    """Rend le corps d'une fonction JavaScript, accolades équilibrées, ou None.

    Sert à vérifier ce que fait un calcul, pas seulement qu'un nom existe : un
    marqueur cherché dans tout le fichier trouverait la même chaîne ailleurs.
    """
    debut = script.find(f"function {nom}(")
    if debut < 0:
        return None
    ouverture = script.find("{", debut)
    if ouverture < 0:
        return None
    profondeur = 0
    for position in range(ouverture, len(script)):
        caractere = script[position]
        if caractere == "{":
            profondeur += 1
        elif caractere == "}":
            profondeur -= 1
            if profondeur == 0:
                return script[ouverture:position + 1]
    return None


#: Ce qui fait qu'un panneau en est un : sa surface, son contour, sa profondeur
#: et son animation. C'est exactement la liste que le lot du 5 novembre 2026 a
#: rendue commune aux deux panneaux flottants du site. La géométrie (`left`,
#: `top`, `width`, `max-height`) n'y figure pas : elle est écrite par le calcul
#: dans `site.js`, et les deux la reçoivent par le même appel.
HABILLAGE_COMMUN = (
    "background",
    "border",
    "border-radius",
    "box-shadow",
    "padding",
    "width",
    "animation",
)


def sans_commentaires_css(corps: str) -> str:
    """La règle privée de ses commentaires : une prose n'est pas une déclaration.

    Sans cela, le commentaire qui explique « le centrage venait de
    `justify-content: center` » se lit comme une déclaration, et le contrôle
    accuse la règle d'un défaut qu'elle ne porte pas.
    """
    return re.sub(r"/\*.*?\*/", " ", corps, flags=re.S)


def declarations(corps: str) -> dict[str, str]:
    """Déclarations d'une règle, la dernière l'emportant : `propriété` → valeur."""
    trouvees: dict[str, str] = {}
    for ligne in sans_commentaires_css(corps).splitlines():
        ligne = ligne.strip()
        if ":" not in ligne or ligne.startswith("/*") or ligne.startswith("*"):
            continue
        propriete, _, valeur = ligne.partition(":")
        trouvees[propriete.strip()] = " ".join(valeur.split()).rstrip(";").strip()
    return trouvees


def controler_habillage_identique_du_menu(texte: str, panneaux: list[str]) -> list[str]:
    """Le panneau du menu porte l'habillage du panneau « Personnalisation ».

    Le 5 novembre 2026, la géométrie des deux panneaux a été unifiée la première.
    L'habillage, lui, ne l'était pas : le panneau du menu restait une dalle
    marine à bordure claire, quand son voisin dans le même en-tête était une
    carte de papier. Deux panneaux posés côte à côte qui ne se ressemblent pas
    n'ont pas le même comportement, quelle que soit leur géométrie.

    Ce contrôle ne cherche pas des mots dans le fichier : il lit les deux règles
    et compare les déclarations qui font l'habillage. C'est la seule façon de
    vérifier « à l'identique » — une valeur recopiée à la main finirait par
    diverger sans que rien ne le dise.
    """
    erreurs: list[str] = []
    if not panneaux:
        return erreurs
    reference = [
        declarations(corps) for corps in blocs_de(texte, ".customize-settings-panel")
        if "background" in corps and "box-shadow" in corps
    ]
    if not reference:
        return [
            "site.css — le panneau « Personnalisation » n'a plus d'habillage lisible "
            "(background et box-shadow) : l'unité des deux panneaux ne peut plus être vérifiée"
        ]
    attendu = reference[0]
    reel = declarations(panneaux[0])
    for propriete in HABILLAGE_COMMUN:
        if propriete not in attendu:
            continue
        if propriete not in reel:
            erreurs.append(
                f"site.css — le panneau du menu n'a plus `{propriete}` dans sa règle : "
                f"il perd l'habillage du panneau « Personnalisation » ({attendu[propriete]})"
            )
        elif reel[propriete] != attendu[propriete]:
            erreurs.append(
                f"site.css — `{propriete}` du panneau du menu diverge de celui de "
                f"« Personnalisation » : « {reel[propriete]} » au lieu de "
                f"« {attendu[propriete]} »"
            )
    # Les entrées du panneau se comportent comme les lignes du panneau voisin :
    # même allumage au survol et sur la page courante (fond `--blue-soft`, encre
    # `--blue`), même anneau de focus bleu — l'anneau clair des surfaces marines
    # serait invisible sur du papier —, et pas de trait doré, qui ne tient pas
    # 3:1 sur une surface claire (mesuré : 2,21:1).
    regles = regles_indexees(texte)
    survol = regles.get('html.has-js.menu-flottant .nav-links a:hover, html.has-js.menu-flottant .nav-links a[aria-current="page"]', "")
    if "background: var(--blue-soft)" not in survol or "color: var(--blue)" not in survol:
        erreurs.append(
            "site.css — le survol et la page courante du panneau du menu n'ont plus "
            "l'allumage des lignes de « Personnalisation » (background: var(--blue-soft); "
            "color: var(--blue)) : le panneau perd son repère de navigation"
        )
    focus = regles.get("html.has-js.menu-flottant .nav-links a:focus-visible", "")
    if "outline: 2px solid var(--blue)" not in focus:
        erreurs.append(
            "site.css — l'anneau de focus d'une entrée du panneau n'est plus celui des "
            "lignes de « Personnalisation » (outline: 2px solid var(--blue)) : l'anneau "
            "clair des surfaces marines est invisible sur la surface du panneau"
        )
    trait = regles.get("html.has-js.menu-flottant .nav-links a::after", "")
    if "content: none" not in trait:
        erreurs.append(
            "site.css — le trait doré de la barre en ligne est revenu dans le panneau "
            "(html.has-js.menu-flottant .nav-links a::after { content: none; }) : il ne "
            "tient que 2,21:1 sur la surface claire, sous le 3:1 du critère 1.4.11"
        )
    return erreurs


def controler_habillage_petit_ecran(texte: str) -> list[str]:
    """À 520 px, les deux panneaux restent la même carte, avec les mêmes lignes.

    Le 5 novembre 2026, l'habillage a été rendu commun dans la règle de base,
    mais le palier de 520 px ne l'était pas : « Personnalisation » y passait à
    un padding de .35rem, un rayon de 14 px et des lignes de 40 px, tandis que
    le menu gardait .45rem, 16 px et 44 px. Sur un téléphone — là où le menu
    sert le plus — les deux panneaux voisins ne se ressemblaient toujours pas.

    Le contrôle exige une **seule règle** pour les deux sélecteurs : deux valeurs
    recopiées dans deux règles finiraient par diverger sans que rien ne le dise.
    """
    communes = [
        (selecteur, corps)
        for selecteur, corps in regles(texte)
        if ".customize-settings-panel" in selecteur
    ]
    carte = [
        corps for selecteur, corps in communes
        if "html.has-js.menu-flottant .nav-links" in selecteur
        and "padding:" in corps and "border-radius:" in corps
    ]
    if not carte:
        return [
            "site.css — à 520 px, les deux panneaux n'ont plus la même règle de carte "
            "(.customize-settings-panel et html.has-js.menu-flottant .nav-links dans un "
            "seul sélecteur, avec padding et border-radius) : le menu garde son ancien "
            "rayon et son ancien espacement sur téléphone"
        ]
    lignes = [
        corps for selecteur, corps in communes
        if "html.has-js.menu-flottant .nav-links a" in selecteur
        and "min-height:" in corps
    ]
    if not lignes:
        return [
            "site.css — à 520 px, les entrées du menu ne partagent plus la règle des "
            "lignes de « Personnalisation » (min-height, padding, gap, font-size) : "
            "les deux panneaux n'ont plus la même hauteur de ligne"
        ]
    return []


def regles_indexees(texte: str) -> dict[str, str]:
    """Habillage : règles indexées par sélecteur normalisé (espaces et retours)."""
    index: dict[str, str] = {}
    for selecteur, corps in regles(texte):
        cle = " ".join(selecteur.split())
        index.setdefault(cle, corps)
    return index


def controler_panneau_du_menu() -> list[str]:
    """Le panneau du menu se déploie comme « Personnalisation », et reste atteignable.

    Le 23 octobre 2026, en paysage sur téléphone (844 × 390), le panneau partait
    de `top: 100%` sans plafond : il descendait à 522 px sur un écran de 390 px,
    et les derniers liens étaient hors d'atteinte. Trois protections doivent
    rester dans la même règle, faute de quoi le défaut revient silencieusement :
    un plafond mesuré, un défilement interne et un centrage qui ne pousse rien
    hors du cadre.

    Le 5 novembre 2026, ce panneau a cessé d'avoir sa propre géométrie : elle
    était écrite en double — pleine largeur sous 1260 px, gouttières négatives
    sous 760 et 520, plafond dans une troisième règle — et il ne se déployait
    pas comme le panneau « Personnalisation » posé à côté de lui. Les deux
    passent désormais par `placerPanneauFlottant` dans `site.js`. Ce contrôle
    vérifie donc aussi cette unité : la même fonction pour les deux panneaux,
    une seule règle de géométrie, et une classe `menu-flottant` publiée par le
    script — sans elle, la feuille appliquerait une géométrie flottante à une
    navigation en ligne.
    """
    erreurs: list[str] = []
    texte = (RACINE / "assets" / "css" / "site.css").read_text(encoding="utf-8")
    panneaux = [
        corps for corps in blocs_de(texte, "html.has-js.menu-flottant .nav-links")
        if "overflow-y: auto" in corps
    ]
    if not panneaux:
        erreurs.append(
            "site.css — le panneau du menu n'a plus de défilement interne "
            "(overflow-y: auto) : sur un écran court, ses derniers liens sortent de l'écran"
        )
    erreurs.extend(controler_habillage_identique_du_menu(texte, panneaux))
    # L'habillage commun vaut à tous les formats, y compris sous 520 px : un
    # ajustement appliqué à un seul des deux panneaux les désaccorde à nouveau.
    erreurs.extend(controler_habillage_petit_ecran(texte))
    # Une deuxième règle de géométrie pour le même panneau, c'est deux vérités à
    # tenir d'accord : c'est exactement ce que le lot du 5 novembre 2026 a retiré.
    autres = [
        corps for corps in blocs_de(texte, ".has-js .nav-links")
        if "position: absolute" in corps
    ]
    if autres:
        erreurs.append(
            "site.css — le panneau du menu a de nouveau une géométrie par palier "
            f"({len(autres)} règle(s) `position: absolute` hors de la règle mesurée) : "
            "il se déploierait autrement que le panneau « Personnalisation »"
        )
    else:
        # Une seule règle doit réunir les trois protections : réparties sur deux
        # blocs, l'une des deux peut disparaître sans que l'autre s'en aperçoive.
        corps = "\n".join(panneaux)
        if "100dvh - var(--hauteur-entete" not in corps:
            erreurs.append(
                "site.css — le panneau du menu n'est plus plafonné à la place "
                "restante sous l'en-tête (calc(100dvh - var(--hauteur-entete)))"
            )
        # Le centrage a changé de réponse le 5 novembre 2026, en même temps que
        # l'habillage. La barre en ligne a une seule rangée : `center` y répartit
        # ce qui reste, et c'était la règle de base. Dans une **colonne**, le même
        # `center` répartit le vide *entre* les entrées dès que le panneau est plus
        # haut qu'elles — les liens se dispersent —, ce que `safe center` ne
        # corrigeait qu'au-delà du bord haut. `flex-start` supprime les deux
        # défauts d'un coup : premier lien en haut, entrées alignées. On refuse
        # donc explicitement tout centrage vertical ici.
        centrages = [
            ligne for ligne in sans_commentaires_css(corps).splitlines()
            if "justify-content" in ligne and "flex-start" not in ligne
            and "justify-content:" in ligne
        ]
        if "justify-content: flex-start" not in corps:
            erreurs.append(
                "site.css — le panneau du menu ne s'aligne plus depuis le haut "
                "(justify-content: flex-start) : en colonne, un centrage disperse les "
                "entrées et pousse la première hors du panneau défilable"
            )
        elif centrages:
            erreurs.append(
                "site.css — le panneau du menu porte un second alignement vertical "
                f"({', '.join(ligne.strip() for ligne in centrages)}) : la dernière "
                "déclaration l'emporte, et c'est celle qui pousse les liens hors du cadre"
            )
    # La hauteur de l'en-tête varie (logo, cran de texte, paysage) : elle doit être
    # mesurée, pas devinée par une constante.
    script = (RACINE / "assets" / "js" / "site.js").read_text(encoding="utf-8")
    # Les deux panneaux, une seule fonction de placement. Deux calculs séparés
    # divergeraient au premier format oublié, et rien ne le dirait : le panneau
    # du menu était dans ce cas jusqu'au 5 novembre 2026.
    for appel in ("placerPanneauFlottant(panneauPersonnalisation", "placerPanneauFlottant(navigation, toggle)"):
        if appel not in script:
            erreurs.append(
                f"site.js — le panneau du menu n'est plus placé comme « Personnalisation » : "
                f"appel attendu absent ({appel})"
            )
    if 'classList.toggle("menu-flottant"' not in script:
        erreurs.append(
            "site.js — la classe `menu-flottant` n'est plus publiée : la feuille de style "
            "appliquerait la géométrie flottante à une navigation en ligne"
        )
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
    # Le panneau n'est plus ancré par une règle de format : il est **placé à la
    # mesure** dans `site.js`, parce qu'aucun point de rupture ne suit une
    # fenêtre qu'on redimensionne, qu'on zoome ou qu'on tourne. Trois règles
    # successives l'ont montré : `right: 0` (le panneau sortait par la gauche
    # dans l'en-tête compact), puis `min-width: 761px and min-height: 561px`
    # (28 octobre 2026), puis son élargissement à `min-width: 921px` (30 octobre
    # 2026) — et le format 980 × 4xx, large et bas, passait encore au travers.
    #
    # Ce contrôle vérifie donc le calcul, pas la règle : que la fonction de
    # placement mesure, borne et se rebranche sur tous les changements qui
    # déplacent le bouton. Et l'inverse, aussi important : qu'aucune règle de
    # format ne réintroduise un ancrage fixe qui contredirait la mesure.
    placement = corps_de_fonction(script, "placerPanneauFlottant")
    if placement is None:
        erreurs.append(
            "site.js — les panneaux ne sont plus placés à la mesure "
            "(aucune fonction placerPanneauFlottant) : ils retombent sur un ancrage "
            "fixe de la feuille de style et ressortent de l'écran dès que la fenêtre "
            "n'est pas celle qu'imaginait le point de rupture"
        )
    else:
        bornes = {
            "getBoundingClientRect()": "il ne mesure plus le bouton (getBoundingClientRect)",
            "visualViewport": "il ignore la fenêtre visuelle (barre d'adresse, clavier virtuel)",
            "largeurFenetre - largeur - MARGE_PANNEAU": "il ne borne plus la position en largeur",
            "hauteurFenetre - haut - MARGE_PANNEAU": "il ne borne plus la hauteur au bas de la fenêtre",
            "style.left": "il ne replace plus le panneau horizontalement",
            "style.maxHeight": "il ne replace plus sa hauteur maximale",
        }
        oubliees = [raison for marqueur, raison in bornes.items() if marqueur not in placement]
        if oubliees:
            erreurs.append(
                "site.js — le placement du panneau « Personnalisation » ne tient plus : "
                + " ; ".join(oubliees)
                + ". Une coordonnée non bornée ressort de l'écran dès qu'un format s'éloigne "
                "de celui qu'on avait en tête"
            )
    rebranchements = {
        "personnalisation.addEventListener(\"toggle\", placerPanneauPersonnalisation)":
            "il n'est plus placé à l'ouverture du panneau",
        # Depuis le 5 novembre 2026, les écoutes appellent `ajusterPanneauxFlottants`,
        # qui pose la classe `menu-flottant` avant de placer : la classe décide si
        # la feuille applique la géométrie mesurée, placer avant elle donnerait
        # des coordonnées que rien n'utilise.
        'window.addEventListener("resize", ajusterPanneauxFlottants':
            "il ne se replace plus quand la fenêtre change de taille",
        'window.visualViewport.addEventListener("resize", ajusterPanneauxFlottants':
            "il ne se replace plus quand la fenêtre visuelle change (barre d'adresse)",
        "new ResizeObserver(publierHauteurEntete)":
            "il ne se replace plus quand l'en-tête change de hauteur (texte agrandi, en-tête réduit)",
        "new MutationObserver(placerPanneauPersonnalisation)":
            "il ne voit plus un panneau restauré ouvert par le navigateur (attribut open posé après load)",
        "apresChangementReglages.push(ajusterPanneauxFlottants)":
            "il ne se replace plus quand la taille du texte ou l'espacement change : "
            "la navigation peut passer sous le bouton « Menu » sans que le panneau le sache",
    }
    for appel, raison in rebranchements.items():
        if appel not in script:
            erreurs.append(
                "site.js — le panneau « Personnalisation » n'est plus replacé : " + raison
                + ". Un panneau placé une fois reste au format de son ouverture"
            )
    ancrages = re.findall(
        r"@media[^{]*\{[^@]*?\.customize-settings-panel\s*\{[^}]*position:\s*fixed",
        texte,
        re.S,
    )
    if ancrages or "html.entete-compacte .customize-settings-panel" in texte:
        erreurs.append(
            "site.css — le panneau « Personnalisation » est de nouveau ancré par un point "
            "de rupture (position: fixed dans une @media, ou règle html.entete-compacte "
            ".customize-settings-panel) : cette valeur contredit le placement mesuré et "
            "ressort de l'écran dans les formats que le point de rupture n'a pas prévus"
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
    if not re.search(r"\[headerCompactToggle, settings, apparenceSettings, layoutSettings, lectureVocale\]", script):
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
    # Un morceau de phrase ne doit pas s'entendre fini. Mesuré le 24 octobre
    # 2026 sur les 98 pages du site : 46 segments sur 6 462 se terminaient sur
    # un mot nu, que le moteur enchaînait au suivant comme un mot de plus. La
    # règle doit rester dans `decouperSegment`, conditionnée à la présence d'une
    # suite (sinon le dernier morceau d'un passage finirait par une virgule), et
    # la virgule doit compter dans la longueur maximale.
    decoupe = re.search(r"const decouperSegment = \(texte\) => \{(.*?)\n  \};", corps, re.S)
    if not decoupe:
        erreurs.append("site.js — la fonction de découpage en segments a disparu")
    else:
        corps_decoupe = decoupe.group(1)
        # La ligne réelle, pas une sous-chaîne : la première version cherchait
        # `morceau += ","` n'importe où, et une virgule mise en commentaire
        # passait le contrôle en laissant le défaut intact.
        if not re.search(r'(?m)^\s+morceau \+= ",";$', corps_decoupe):
            erreurs.append(
                "site.js — un morceau coupé au milieu d'une phrase ne reçoit plus de virgule : "
                "le moteur enchaînerait le morceau suivant comme un mot de plus"
            )
        if "if (reste && " not in corps_decoupe:
            erreurs.append(
                "site.js — la virgule de continuation n'est plus conditionnée à la présence "
                "d'une suite : le dernier morceau d'un passage finirait par une virgule"
            )
        if "morceau.length >= LONGUEUR_MAX_SEGMENT" not in corps_decoupe:
            erreurs.append(
                "site.js — la virgule n'est plus décomptée de la longueur maximale : "
                "un segment peut dépasser la limite qu'un moteur interrompt"
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


def controler_espacement_du_texte() -> list[str]:
    """L'espacement du critère WCAG 1.4.12 ne doit pas casser la mise en page.

    Mesuré le 24 octobre 2026 : à interlettrage 0,12 em et espacement des mots
    0,16 em, les sept entrées de navigation demandaient 47 px de plus que
    l'écran à 1 280 px. La barre sortait du cadre des deux côtés et « Nous
    contacter » finissait hors de la fenêtre, sans que la page signale de
    défilement horizontal — le défaut était donc invisible aux contrôles de
    débordement. `flex-wrap` sur `.nav-links` le corrige : la ligne reste
    unique tant qu'elle suffit, et passe à la ligne seulement quand elle ne
    suffit plus. Ce contrôle lit la source ; c'est
    `outils/auditer-criteres-22.mjs` qui mesure les 98 pages.
    """
    erreurs: list[str] = []
    feuille = (RACINE / "assets" / "css" / "site.css").read_text(encoding="utf-8")

    blocs = blocs_de(feuille, ".nav-links")
    if not blocs:
        erreurs.append("site.css — la règle .nav-links a disparu")
    elif not any(re.search(r"flex-wrap:\s*wrap", corps) for corps in blocs):
        erreurs.append(
            "site.css — .nav-links n'a plus flex-wrap: wrap : avec l'espacement du "
            "critère 1.4.12, la barre de navigation déborde de 47 px à 1 280 px et "
            "« Nous contacter » sort de la fenêtre"
        )

    # Le bouton de la colonne latérale d'une fiche : 230 à 300 px de large, un
    # libellé de 361 px sous l'espacement du critère. Sans cette règle, les 84
    # fiches débordent de 22 px à 1 280 px.
    boutons = [corps for selecteur, corps in regles(feuille)
               if ".learning-lesson-aside .button" in selecteur]
    if not boutons:
        erreurs.append(
            "site.css — la règle .learning-lesson-aside .button a disparu : son libellé "
            "« Retour aux mondes et parcours » déborderait de 22 px sur les 84 fiches "
            "dès que l'espacement du critère 1.4.12 est appliqué"
        )
    elif not any(re.search(r"white-space:\s*normal", corps) for corps in boutons):
        erreurs.append(
            "site.css — .learning-lesson-aside .button n'autorise plus le retour à la "
            "ligne : le libellé déborderait de 22 px sous l'espacement du critère 1.4.12"
        )

    regle = [corps for selecteur, corps in regles(feuille) if "espacement-renforce" in selecteur]
    if not regle:
        erreurs.append("site.css — le réglage « espacement renforcé » a disparu")
        return erreurs
    corps = " ".join(regle)

    def valeur(propriete: str) -> float | None:
        trouve = re.search(propriete + r":\s*([0-9.]+)", corps)
        return float(trouve.group(1)) if trouve else None

    interligne = valeur("line-height")
    interlettrage = valeur("letter-spacing")
    espacement_mots = valeur("word-spacing")
    if interligne is None or interligne < 1.5:
        erreurs.append(
            f"site.css — l'interligne du réglage d'espacement vaut {interligne} : le "
            "critère 1.4.12 en demande 1,5"
        )
    if interlettrage is None or interlettrage < 0.12:
        erreurs.append(
            f"site.css — l'interlettrage du réglage d'espacement vaut {interlettrage} em : "
            "le critère 1.4.12 en demande 0,12 em"
        )
    if espacement_mots is None or espacement_mots < 0.16:
        erreurs.append(
            f"site.css — l'espacement des mots du réglage vaut {espacement_mots} em : "
            "le critère 1.4.12 en demande 0,16 em"
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

    # 4. La mention d'impression ouvre sa propre ligne, calée à gauche.
    # Collée après le point, elle commençait au milieu d'une ligne centrée et se
    # coupait en deux (« Une copie imprimée / n'est pas une version certifiée »),
    # signalé le 25 octobre 2026 avec capture.
    imprimable = re.search(r"\.footer-rd-print\s*\{([^}]*)\}", texte)
    if not imprimable:
        erreurs.append(
            "site.css — la règle .footer-rd-print a disparu : la mention d'impression "
            "se recolle après le point et se coupe au milieu d'une ligne centrée"
        )
    else:
        manquants = [
            declaration
            for declaration in ("display: block", "text-align: start")
            if declaration not in imprimable.group(1)
        ]
        if manquants:
            erreurs.append(
                "site.css — la mention d'impression n'ouvre plus sa propre ligne calée à "
                f"gauche ({', '.join(manquants)} manquant dans .footer-rd-print) : elle "
                "démarre derrière le point de la phrase précédente"
            )
    if not re.search(r"\.footer-bottom\s+\.footer-rd\s*\{[^}]*max-width:\s*none", texte):
        erreurs.append(
            "site.css — la note de version est de nouveau bornée à 72ch dans le bas de "
            "page (.footer-bottom .footer-rd { max-width: none }) : la mention "
            "d'impression ne rejoint plus le bord gauche du conteneur"
        )
    sans_saut = []
    for page in sorted(
        chemin for chemin in list(RACINE.glob("*.html")) + list((RACINE / "apprendre" / "fiches").glob("*.html"))
    ):
        if '<span class="footer-rd-print">' not in page.read_text(encoding="utf-8"):
            sans_saut.append(page.name)
    if sans_saut:
        erreurs.append(
            f"{len(sans_saut)} page(s) collent la mention d'impression derrière le point, "
            f"sans <span class=\"footer-rd-print\"> ({', '.join(sans_saut[:3])}…) : le "
            "générateur de fiches et les pages racine doivent porter le même pied de page"
        )

    # 5. La copie imprimée porte elle-même l'attribution exigée par la licence.
    # Jusqu'au 25 octobre 2026, la ligne d'impression lisait un attribut que
    # personne n'écrivait : elle s'imprimait avec un tiret vide, donc sans
    # l'adresse que la licence rend obligatoire.
    impression = re.search(r"html::after\s*\{([^}]*)\}", texte)
    if not impression:
        erreurs.append(
            "site.css — la ligne d'impression a disparu (html::after dans @media print) : "
            "une copie papier ne porte plus ni source, ni licence, ni statut"
        )
    else:
        contenu = impression.group(1)
        manquants = [
            expression
            for expression in ("attr(data-print-url)", "transparence.html#licence", "version certifiée")
            if expression not in contenu
        ]
        if manquants:
            erreurs.append(
                "site.css — la ligne d'impression ne porte plus "
                f"{', '.join(manquants)} : la licence exige une attribution qui cite l'adresse, "
                "et la copie doit dire qu'elle n'est pas certifiée"
            )
        if "content:" not in contenu:
            erreurs.append("site.css — la ligne d'impression n'a plus de contenu (content:)")

    pages_publiees = sorted(
        list(RACINE.glob("*.html")) + list((RACINE / "apprendre" / "fiches").glob("*.html"))
    )
    sans_adresse, adresses_fausses = [], []
    bases = set()
    for page in pages_publiees:
        contenu_page = page.read_text(encoding="utf-8")
        attribut = re.search(r'<html[^>]*\bdata-print-url="([^"]*)"', contenu_page)
        canonique = re.search(r'<link rel="canonical" href="([^"]+)">', contenu_page)
        if not attribut or not attribut.group(1).strip():
            sans_adresse.append(page.name)
            continue
        if attribut.group(1).startswith("http"):
            bases.add(re.match(r"(https?://[^/]+/[^/]+/)", attribut.group(1)).group(1)
                      if re.match(r"(https?://[^/]+/[^/]+/)", attribut.group(1)) else attribut.group(1))
        if canonique and attribut.group(1) != canonique.group(1):
            adresses_fausses.append(f"{page.name} ({attribut.group(1)} au lieu de {canonique.group(1)})")
    if sans_adresse:
        erreurs.append(
            f"{len(sans_adresse)} page(s) n'ont pas d'adresse d'impression (data-print-url) "
            f"({', '.join(sans_adresse[:3])}…) : la copie papier s'imprime sans la source "
            "que la licence rend obligatoire"
        )
    if adresses_fausses:
        erreurs.append(
            f"{len(adresses_fausses)} page(s) annoncent une autre adresse à l'impression que leur "
            f"canonique ({'; '.join(adresses_fausses[:2])}…) : l'attribution pointerait ailleurs"
        )
    # Une adresse de licence figée dans la feuille doit suivre le domaine des
    # canoniques : un changement de domaine la laisserait pointer vers l'ancien.
    if bases:
        base_site = sorted(bases)[0]
        if base_site not in texte:
            erreurs.append(
                f"site.css — la base publiée des pages ({base_site}) n'apparaît pas dans la "
                "feuille : l'adresse de licence de la ligne d'impression pointe vers un autre "
                "domaine que les canoniques"
            )
    return erreurs


#: Ce qui fait que « Menu » et « Personnalisation » sont le même bouton. Le
#: 5 novembre 2026, les deux panneaux avaient été unifiés mais pas les deux
#: commandes : un relevé de styles calculés dans Chromium montrait 14 px contre
#: 12,8 px de police, 10,4 px contre 10 px de gouttière, `nowrap` d'un seul
#: côté et deux transitions de durées différentes. La porte ne voit pas les
#: pixels : elle exige que ces propriétés soient écrites **une seule fois**,
#: dans une règle qui nomme les deux sélecteurs, et qu'aucune règle propre ne
#: les redéclare. Les valeurs restent libres ; la divergence, elle, ne l'est pas.
BOUTONS_PARTAGES = (
    "align-items", "justify-content", "gap", "min-width", "min-height",
    "padding", "border", "border-radius", "background", "color",
    "font-family", "font-size", "font-weight", "line-height",
    "text-align", "white-space", "overflow-wrap", "hyphens",
    "cursor", "transition",
)


def controler_boutons_entete_identiques() -> list[str]:
    """Les deux commandes de l'en-tête partagent une seule règle d'habillage.

    Le contrôle ne recopie aucune valeur de couleur ou de taille : un dessin
    peut changer sans casser la parité, tant qu'il change pour les deux. Il
    refuse en revanche qu'une des deux règles propres reprenne une propriété
    commune à son compte — c'est exactement ainsi que la divergence du 5
    novembre était née, sans que le garde-fou des panneaux la voie.
    """
    erreurs: list[str] = []
    texte = (RACINE / "assets" / "css" / "site.css").read_text(encoding="utf-8")
    index = regles_indexees(texte)
    commune = index.get(".nav-toggle, .customize-settings > summary", "")
    if not commune:
        return [
            "site.css — la règle commune aux deux commandes d'en-tête « Menu » et "
            "« Personnalisation » a disparu : elles ne partagent plus leur habillage"
        ]
    presentes = declarations(commune)
    for propriete in BOUTONS_PARTAGES:
        if propriete not in presentes:
            erreurs.append(
                f"site.css — la règle commune des boutons d'en-tête n'a plus "
                f"`{propriete}` : une valeur recopiée d'un seul côté peut diverger"
            )
    for selecteur in (".nav-toggle", ".customize-settings > summary"):
        # `blocs_de` cherche un sélecteur exact mais `^` de son motif matche
        # aussi un début de ligne : la seconde ligne du sélecteur commun se
        # lirait comme une règle propre. L'index des règles, lui, tient le
        # préambule entier.
        propre = declarations(index.get(selecteur, ""))
        for propriete in BOUTONS_PARTAGES:
            if propriete in propre:
                erreurs.append(
                    f"site.css — `{selecteur}` redéclare `{propriete}` pour lui seul : "
                    "les deux commandes de l'en-tête ne sont plus le même bouton"
                )
    allumage = index.get(
        '.nav-toggle:hover, .nav-toggle[aria-expanded="true"], '
        '.customize-settings > summary:hover, .customize-settings[open] > summary',
        "",
    )
    if not allumage or "border-color: var(--gold)" not in allumage or "background: var(--on-navy-fill-strong)" not in allumage:
        erreurs.append(
            "site.css — le survol et l'ouverture des deux commandes d'en-tête ne "
            "sont plus portés par une seule règle : l'une peut s'allumer sans l'autre"
        )
    return erreurs


def controler_ouverture_accueil() -> list[str]:
    """L'ouverture de l'accueil garde ses phrases et ses gras dans la ligne.

    Le 9 novembre 2026, la personne a signalé une présentation peu
    professionnelle avec des collages à la copie (« compréhensibles.Ce »,
    « différent :des fiches pour », « publique.Vous »). Trois causes ont été
    mesurées dans le rendu, aucune n'était une coquille : la règle globale
    `main p > strong:first-child` mettait le gras en bloc, le découpage en
    `span.phrase` de `site.js` supprimait les espaces entre phrases, et une
    grille `auto-fit` laissait le repère « 0 » seul dans une demi-carte.
    """
    erreurs: list[str] = []
    css = (RACINE / "assets" / "css" / "site.css").read_text(encoding="utf-8")
    js = (RACINE / "assets" / "js" / "site.js").read_text(encoding="utf-8")

    gras = re.search(
        r"\.home-hero-civic\s+\.hero-copy\s*>\s*p\s*>\s*strong:first-child\s*\{[^}]*display:\s*inline",
        css,
    )
    if not gras:
        erreurs.append(
            "site.css — le gras de l'ouverture de l'accueil n'est plus remis dans la ligne : "
            "`main p > strong:first-child` le coupe à nouveau du reste de la phrase"
        )

    _, _, decoupage = js.partition("Chaque phrase de contenu")
    if 'if (bloc.closest(".home-hero-civic, .home-association, .association-reperes")) return;' not in decoupage:
        erreurs.append(
            "site.js — l'ouverture de l'accueil est de nouveau découpée en blocs `.phrase` : "
            "les phrases se recollent à la copie"
        )

    # Ancrer en début de ligne : la règle composée `.home-hero-civic
    # .home-hero-facts { gap: … }` ne décide pas de la bande.
    bande = re.search(r"(?m)^\.home-hero-facts\s*\{([^}]*)\}", css)
    if not bande or "flex-wrap: wrap" not in bande.group(1):
        erreurs.append(
            "site.css — les repères chiffrés de l'accueil ne sont plus une bande souple : "
            "la carte « 0 » redevient orpheline"
        )
    return erreurs


def controler_presentation_association() -> list[str]:
    """Le parcours « découvrir l'association » reste lisible et lié.

    Le 9 novembre 2026, après la refonte de l'ouverture, la section
    « L'association » de l'accueil était encore un bloc de neuf paragraphes
    avec trois cartes sans aucun lien, et la page Documents répétait deux fois
    la même notice. Ce garde-fou tient ce qui a été mesuré : trois repères
    rattachés aux statuts, trois portes d'entrée réellement liées, un texte
    suivi (pas de `.phrase` collées) et quatre notices distinctes. Le 10
    novembre 2026, la carte du siège social a été retirée à la demande de la
    personne : il ne reste que trois repères, et le garde-fou refuse leur
    retour. Il ne juge ni la vérité des statuts ni l'esthétique du rendu.
    """
    erreurs: list[str] = []
    accueil = (RACINE / "index.html").read_text(encoding="utf-8")
    documents = (RACINE / "documents.html").read_text(encoding="utf-8")
    js = (RACINE / "assets" / "js" / "site.js").read_text(encoding="utf-8")

    mission = re.search(
        r'<section class="section home-association" id="mission".*?</section>',
        accueil,
        flags=re.DOTALL,
    )
    if not mission:
        erreurs.append(
            "index.html — la section de présentation de l'association a perdu son point d'ancrage : "
            "le parcours n'est plus vérifiable"
        )
        return erreurs
    bloc = mission.group(0)
    if bloc.count('class="home-discover-link"') != 3:
        erreurs.append(
            "index.html — les trois portes d'entrée de la présentation n'ont pas toutes un lien explicite : "
            "la découverte redevient une suite de cartes inertes"
        )
    if 'href="assets/documents/statuts-2020.pdf"' not in bloc:
        erreurs.append(
            "index.html — les repères de l'association ne renvoient plus aux statuts : "
            "le fait affiché n'est plus traçable"
        )
    if bloc.count("<dt>") != 3:
        erreurs.append(
            "index.html — les repères vérifiables de l'association ne sont plus au nombre de trois"
        )
    if "<dt>Siège</dt>" in bloc or "Siège social fixé à Beaurepaire" in bloc:
        erreurs.append(
            "index.html — la carte du siège social est revenue dans les repères : "
            "ce détail a été retiré à la demande de la personne"
        )
    _, _, decoupage = js.partition("Chaque phrase de contenu")
    if '.home-association, .association-reperes' not in decoupage:
        erreurs.append(
            "site.js — la présentation de l'association est de nouveau découpée en blocs `.phrase` : "
            "les paragraphes se collent à la copie"
        )
    cartes = re.findall(r'<article class="document-card">.*?</article>', documents, flags=re.DOTALL)
    notices = [re.search(r"<p>(.*?)</p>", carte, flags=re.DOTALL) for carte in cartes]
    textes = [n.group(1).strip() for n in notices if n]
    if len(cartes) != 4 or len(textes) != 4 or len(set(textes)) != 4:
        erreurs.append(
            "documents.html — deux notices de documents sont à nouveau identiques : "
            "on ne peut plus savoir ce que l'on ouvre"
        )
    return erreurs



def controler_filtre_texte_fin() -> list[str]:
    """Un décor sans texte lisible ne se compte pas comme du texte trop petit.

    Le 6 novembre 2026, `auditer-affichages.mjs` sortait en code 1 sur un site
    sain : ses 2 470 mesures comptaient chacune `span.customize-settings-chevron`,
    un masque SVG à `font-size: 0` qui porte encore le caractère `⌄` et se
    déclare `aria-hidden`. L'auditeur a été corrigé le 12 novembre 2026 —
    l'écart est à faire dans l'outil, pas dans la feuille de style — et
    `test_auditer_affichages.mjs` exécute désormais le filtre sur quatre DOM
    témoins : le décor à écarter, un vrai texte à conserver, un `aria-hidden`
    visible à conserver, et un élément vide qui ne compte ni comme défaut ni
    comme écart.

    Cette garde-ci ne remplace pas ce banc : elle tient la décision hors du
    navigateur, pour qu'un futur passage ne puisse pas effacer le filtre, ni
    le transformer en congé général pour tous les `aria-hidden`.
    """
    erreurs: list[str] = []
    fichier = RACINE / "outils" / "auditer-affichages.mjs"
    if not fichier.is_file():
        return ["outils/auditer-affichages.mjs — l'auditeur d'affichage a disparu"]
    texte = fichier.read_text(encoding="utf-8")
    if "const decorSansTexte = corps === 0 && Boolean(texte) && element.getAttribute('aria-hidden') === 'true';" not in texte:
        erreurs.append(
            "auditer-affichages.mjs — le filtre du décor sans texte lisible a disparu : "
            "le chevron aria-hidden à font-size 0 redevient un faux défaut de « texte sous 12 px »"
        )
    if (
        "decorsEcartes.push" not in texte
        or "decorsEcartes: uniques(decorsEcartes), nbDecorsEcartes: decorsEcartes.length," not in texte
    ):
        erreurs.append(
            "auditer-affichages.mjs — l'écart n'est plus compté ni nommé (`nbDecorsEcartes`) : "
            "le chiffre de « texte sous 12 px » baisserait sans que personne ne sache pourquoi"
        )
    # Les deux pièges de l'autre côté. Un filtre qui n'exigerait pas le corps nul
    # écarterait un vrai texte visible de 11 px simplement masqué aux lecteurs
    # d'écran ; un filtre qui n'exigerait pas la présence d'un texte gonflerait
    # le compteur d'écarts avec des éléments qui n'avaient jamais été comptés
    # comme défaut. Le banc éprouve les deux sur des DOM témoins ; cette garde
    # refuse les formes qui les rouvriraient.
    if "Boolean(texte)" not in texte:
        erreurs.append(
            "auditer-affichages.mjs — le filtre n'exige plus la présence d'un texte : "
            "il écarte ou compte des éléments qui n'ont jamais porté de texte lisible"
        )
    return erreurs


CONTROLES = (
    ("tailles de texte", controler_tailles_de_texte),
    ("cibles tactiles", controler_cibles_tactiles),
    ("en-tête compact", controler_en_tete_compact),
    ("mode réduit persistant", controler_entete_reduit_persistant),
    ("panneau du menu", controler_panneau_du_menu),
    ("mesure de lecture", controler_mesure_de_lecture),
    ("plafonds d'images par densité", controler_plafonds_d_images),
    ("illustrations restaurées et proportions", controler_illustrations),
    ("pistes de grille", controler_pistes_de_grille),
    ("césure des mots longs", controler_cesure),
    ("densité du rendu 3D", controler_densite_du_rendu_3d),
    ("décor du héros et son repli", controler_decor_du_heros),
    ("qualité d'encodage des images", controler_qualite_d_encodage),
    ("habillage du panneau", controler_habillage_du_panneau),
    ("boutons de l’en-tête identiques", controler_boutons_entete_identiques),
    ("pied de page et copie imprimée", controler_pied_de_page),
    ("lecture à voix haute", controler_lecture_a_voix_haute),
    ("espacement du texte (WCAG 1.4.12)", controler_espacement_du_texte),
    ("ouverture de l'accueil sans collage", controler_ouverture_accueil),
    ("parcours de présentation de l'association", controler_presentation_association),
    ("filtre du texte fin (décor aria-hidden)", controler_filtre_texte_fin),
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
