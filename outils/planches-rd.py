#!/usr/bin/env python3
"""Fabrique les planches visuelles de la R&D — pour montrer, pas pour prouver.

Une planche n'est pas un contrôle : c'est une pièce qu'une personne regarde
pour décider. Le 4 novembre 2026, la teinte du jeton `--muted` a été retenue
ainsi — sur une planche, pas sur un tableau de nombres. Une décision prise sur
une image doit donc laisser une image reproductible, sinon la pièce du dossier
devient une capture sans origine.

Ce que ce script dessine : les couleurs, les tailles de texte et les rapports de
contraste **réels** du site, recalculés par la formule WCAG 2.2, plus les textes
des pages. Ce qu'il ne fait pas : une capture du navigateur. Aucun Chromium
n'est requis, et chaque planche l'écrit sur elle-même — un dessin mesuré ne doit
jamais se faire passer pour une capture.

Les fichiers produits sont destinés au Drive de passation, pas au dépôt : une
image de 150 Ko dans Git ne prouverait rien de plus que le script qui la refait.
Leur dossier, écrit ici pour qu'il se retrouve sans fouiller le Drive :
`MRSC — ESPACE PRIVÉ ISOLÉ` → `06 — Planches R&D du site (preuves visuelles)`
(`1Ne-139sA65TZg_oDXq2ixWEy2hh7Wy5N`), et nulle part ailleurs.

Usage :
    python3 outils/planches-rd.py                 # écrit dans build/planches-rd
    python3 outils/planches-rd.py --sortie /tmp  # ailleurs

Dépendance : Pillow, et les polices DejaVu du système. Sans elles, le script
sort en code 2 et le dit — jamais une planche vide.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

try:
    from PIL import Image, ImageDraw, ImageFont
except ModuleNotFoundError:  # pragma: no cover — dépendance absente
    print(
        "Planches : Pillow est absent (pip install pillow). Aucune planche n'a été écrite.",
        file=sys.stderr,
    )
    raise SystemExit(2)

RACINE = Path(__file__).resolve().parent.parent
SORTIE = RACINE / "build" / "planches-rd"
LARGEUR, HAUTEUR = 2000, 1400

ENCRE = (24, 36, 59)
NAVY = (29, 50, 104)
MUTED = (95, 107, 129)
ANCIEN = (100, 112, 134)
TRAIT = (227, 232, 240)
PAPIER = (248, 249, 252)
BLANC = (255, 255, 255)
ROUGE = (163, 35, 44)
VERT = (66, 107, 38)
OR = (210, 146, 54)
BLEU = (41, 88, 162)
CREME = (248, 241, 223)
BLEU_PALE = (237, 242, 250)
VERT_PALE = (239, 245, 233)

POLICES = Path("/usr/share/fonts/truetype/dejavu")

if not POLICES.is_dir():  # pragma: no cover — polices absentes
    print(
        f"Planches : les polices DejaVu sont absentes de {POLICES}. Aucune planche n'a été écrite.",
        file=sys.stderr,
    )
    raise SystemExit(2)


def police(taille: int, gras: bool = False) -> ImageFont.FreeTypeFont:
    nom = "DejaVuSans-Bold.ttf" if gras else "DejaVuSans.ttf"
    return ImageFont.truetype(str(POLICES / nom), taille)


def mono(taille: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(POLICES / "DejaVuSansMono.ttf"), taille)


def luminance(couleur: tuple[int, int, int]) -> float:
    def canal(valeur: float) -> float:
        v = valeur / 255
        return v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4

    return 0.2126 * canal(couleur[0]) + 0.7152 * canal(couleur[1]) + 0.0722 * canal(couleur[2])


def rapport(a: tuple[int, int, int], b: tuple[int, int, int]) -> float:
    la, lb = luminance(a), luminance(b)
    return (max(la, lb) + 0.05) / (min(la, lb) + 0.05)


def texte(draw: ImageDraw.ImageDraw, x: int, y: int, contenu: str, font, couleur=ENCRE) -> int:
    draw.text((x, y), contenu, font=font, fill=couleur)
    return y + font.size * 1.35


def largeur_texte(font, contenu: str) -> int:
    return int(font.getlength(contenu))


def envelopper(font, contenu: str, largeur_max: int) -> list[str]:
    mots, lignes, courante = contenu.split(), [], ""
    for mot in mots:
        essai = f"{courante} {mot}".strip()
        if largeur_texte(font, essai) <= largeur_max:
            courante = essai
        else:
            if courante:
                lignes.append(courante)
            courante = mot
    if courante:
        lignes.append(courante)
    return lignes


def paragraphe(draw, x, y, contenu, font, largeur_max, couleur=ENCRE, interligne=1.25) -> int:
    for ligne in envelopper(font, contenu, largeur_max):
        draw.text((x, y), ligne, font=font, fill=couleur)
        y += int(font.size * interligne)
    return y


def pastille(draw, x, y, libelle, font, fond, encre) -> int:
    largeur = largeur_texte(font, libelle) + 28
    hauteur = font.size + 16
    draw.rounded_rectangle([x, y, x + largeur, y + hauteur], radius=hauteur // 2, fill=fond)
    draw.text((x + 14, y + 7), libelle, font=font, fill=encre)
    return x + largeur


def cadre(draw, x, y, largeur, hauteur, fond=BLANC, bord=TRAIT, rayon=18) -> None:
    draw.rounded_rectangle([x, y, x + largeur, y + hauteur], radius=rayon, fill=fond, outline=bord, width=2)


def bandeau(image: ImageDraw.ImageDraw, titre: str, sous_titre: str) -> None:
    image.rectangle([0, 0, LARGEUR, 118], fill=NAVY)
    image.text((78, 30), titre, font=police(42, gras=True), fill=BLANC)
    image.text((80, 84), sous_titre, font=police(22), fill=(196, 210, 234))


def pied(image: ImageDraw.ImageDraw, sources: str, question: str) -> None:
    y = HAUTEUR - 128
    image.line([78, y, LARGEUR - 78, y], fill=TRAIT, width=2)
    image.text((78, y + 16), question, font=police(24, gras=True), fill=BLEU)
    image.text((78, y + 54), sources, font=mono(17), fill=MUTED)
    image.text(
        (78, y + 82),
        "Dessin mesuré : couleurs, tailles et rapports sont ceux du site, recalculés par la formule WCAG 2.2 — "
        "ce n’est pas une capture du navigateur (aucun Chromium dans cet environnement).",
        font=police(17),
        fill=MUTED,
    )


def planche_muted() -> Path:
    image = Image.new("RGB", (LARGEUR, HAUTEUR), BLANC)
    dessin = ImageDraw.Draw(image)
    bandeau(
        dessin,
        "Le jeton --muted : ce qui a changé, et pourquoi",
        "M.R.S.C. — R&D · 4 novembre 2026 · PR #270 · quatre fonds, deux couleurs, un seuil",
    )

    y = 156
    y = paragraphe(
        dessin,
        78,
        y,
        "Le texte de second plan du site tenait 5,00:1 sur blanc — donc il passait tous les contrôles. "
        "Mais sur les fonds teintés (crème, vert pâle, bleu pâle), il tombait à 4,43–4,50:1, sous le seuil de "
        "4,5:1 que WCAG 2.2 AA exige pour un petit texte. Personne ne le voyait : ces fonds étaient des "
        "dégradés, et la mesure ne lisait que des couleurs unies.",
        police(24),
        1844,
    )

    fonds = [
        ("Bandeau de page · crème", CREME, "tint-gold #f8f1df"),
        ("Carte de leçon · bleu pâle", BLEU_PALE, "mesuré rgb(237, 242, 250)"),
        ("Carte teintée · vert pâle", VERT_PALE, "tint-green #eff5e9"),
        ("Surface · blanc", BLANC, "surface #ffffff"),
    ]
    phrase = "Retrouvez les documents de l’association et les informations officielles."

    colonnes = [(78, "AVANT  —  #647086", ANCIEN), (1022, "APRÈS  —  #5f6b81", (95, 107, 129))]
    y_table = 366
    for x, titre_colonne, teinte in colonnes:
        dessin.text((x, y_table), titre_colonne, font=police(26, gras=True), fill=teinte)
        dessin.line([x, y_table + 40, x + 900, y_table + 40], fill=teinte, width=3)

    for index, (nom, fond, ref) in enumerate(fonds):
        haut = y_table + 76 + index * 196
        for x, _, teinte in colonnes:
            cadre(dessin, x, haut, 900, 164, fond=fond, bord=(255, 255, 255) if fond == BLANC else None or TRAIT)
            dessin.rounded_rectangle([x, haut, x + 900, haut + 164], radius=18, outline=TRAIT, width=2)
            dessin.text((x + 24, haut + 18), nom, font=police(19), fill=(70, 83, 105))
            dessin.text((x + 24, haut + 46), ref, font=mono(15), fill=(112, 124, 145))
            # Le texte réel de la page, à sa taille de lecture (agrandi ici de
            # moitié pour être lisible sur une planche, ce qui ne change pas le
            # rapport : il ne dépend pas de la taille, seulement le seuil).
            dessin.text((x + 24, haut + 96), phrase, font=police(21), fill=teinte)
            valeur = rapport(teinte, fond)
            passe = valeur >= 4.5
            libelle = f"{valeur:.3f}:1".replace(".", ",") + ("  ·  passe" if passe else "  ·  sous 4,5:1")
            pastille(
                dessin,
                x + 620,
                haut + 12,
                libelle,
                police(19, gras=True),
                (232, 244, 234) if passe else (250, 232, 233),
                VERT if passe else ROUGE,
            )

    dessin.text(
        (78, 1214),
        "732 refus avec l’ancienne valeur, sur cinq sélecteurs (p.page-lead, p, small, span.phrase, p.home-hero-note) — "
        "zéro avec la nouvelle. Teinte inchangée, clarté −4 %.",
        font=police(21),
        fill=ENCRE,
    )
    pied(
        dessin,
        "assets/css/site.css (--muted) · docs/rd/inventaire-couleurs-jetons.md · docs/rd/formats-affichage.md §13",
        "À dire : le contraste du texte secondaire te paraît-il encore assez doux, ou faut-il l’assombrir davantage ?",
    )
    chemin = SORTIE / "Planche-1-jeton-muted-avant-apres.png"
    image.save(chemin)
    return chemin


def planche_degrades() -> Path:
    image = Image.new("RGB", (LARGEUR, HAUTEUR), BLANC)
    dessin = ImageDraw.Draw(image)
    bandeau(
        dessin,
        "17 500 textes sur un dégradé : ce qui est jugé maintenant",
        "M.R.S.C. — R&D · 4 novembre 2026 · PR #270 · une plage n’est pas une couleur, et un dégradé n’est pas une image",
    )

    # --- Deux vignettes : le majorant, puis la portion sous le texte ---------
    vignette_l, vignette_h = 900, 300
    for x, titre, sous in [
        (78, "AVANT — la plage entière", "le pire point de l’étendue, où que soit le texte"),
        (1022, "APRÈS — la portion sous le texte", "la boîte du texte projetée sur l’axe du dégradé"),
    ]:
        cadre(dessin, x, 156, vignette_l, vignette_h)
        dessin.text((x + 24, 172), titre, font=police(24, gras=True), fill=ENCRE)
        dessin.text((x + 24, 202), sous, font=police(17), fill=MUTED)
        # La bande dégradée, rendue couleur par couleur.
        gauche, haut, large, hauteur = x + 24, 246, vignette_l - 48, 118
        for pas in range(large):
            part = pas / (large - 1)
            r = int(CREME[0] + (NAVY[0] - CREME[0]) * part)
            g = int(CREME[1] + (NAVY[1] - CREME[1]) * part)
            b = int(CREME[2] + (NAVY[2] - CREME[2]) * part)
            dessin.line([gauche + pas, haut, gauche + pas, haut + hauteur], fill=(r, g, b))
        # Le texte, posé à gauche, sur la partie claire.
        dessin.rectangle([gauche + 18, haut + 20, gauche + 320, haut + 96], outline=ENCRE, width=2)
        dessin.text((gauche + 30, haut + 44), "Le texte est ici", font=police(20), fill=ENCRE)
        if x == 78:
            dessin.line([gauche + large - 4, haut - 14, gauche + large - 4, haut + hauteur + 14], fill=ROUGE, width=4)
            dessin.text((gauche + large - 250, haut - 34), "pire point retenu", font=police(17, gras=True), fill=ROUGE)
        else:
            # La portion échantillonnée : un crochet au-dessus de la bande.
            droite = gauche + 330
            dessin.line([gauche + 18, haut - 6, gauche + 18, haut - 16], fill=ENCRE, width=3)
            dessin.line([gauche + 18, haut - 16, droite, haut - 16], fill=ENCRE, width=3)
            dessin.line([droite, haut - 16, droite, haut - 6], fill=ENCRE, width=3)
            dessin.text((gauche + 18, haut + hauteur + 10), "seule cette portion est échantillonnée", font=police(16, gras=True), fill=ENCRE)
        dessin.text(
            (x + 24, 408),
            "sur les 17 500 textes : pire rapport 4,723:1" if x == 78 else "sur les 17 500 textes : pire rapport 4,782:1",
            font=mono(19),
            fill=ENCRE,
        )

    # --- L’effet chiffré de la géométrie ------------------------------------
    y = 494
    dessin.text((78, y), "Ce que la géométrie change, verdict par verdict", font=police(26, gras=True), fill=ENCRE)
    colonnes = [
        ("16 515", "verdicts plus permissifs", VERT),
        ("985", "verdicts identiques", MUTED),
        ("0", "verdict plus sévère", BLEU),
    ]
    for index, (nombre, libelle, teinte) in enumerate(colonnes):
        x = 78 + index * 400
        cadre(dessin, x, y + 44, 370, 118)
        dessin.text((x + 24, y + 58), nombre, font=police(44, gras=True), fill=teinte)
        dessin.text((x + 24, y + 112), libelle, font=police(19), fill=ENCRE)
    dessin.text(
        (1330, y + 52),
        "Aucun refus n’a été levé par ce resserrement, et aucun créé :",
        font=police(19),
        fill=ENCRE,
    )
    dessin.text((1330, y + 80), "la borne était plus large que nécessaire, elle ne cachait rien.", font=police(19), fill=ENCRE)
    dessin.text((1330, y + 116), "Le défaut réel venait du jeton — planche 1.", font=police(19, gras=True), fill=BLEU)

    # --- Les trois fautes corrigées en chemin -------------------------------
    y = 700
    dessin.text((78, y), "Trois fautes de méthode, corrigées avant de publier le chiffre", font=police(26, gras=True), fill=ENCRE)
    fautes = [
        (
            "1 · Le fond opaque était ignoré",
            "Un bouton plein sur un bandeau dégradé était jugé contre le bandeau qu’il recouvre.",
            "24 boutons accusés à 1,06:1 — faux refus.",
        ),
        (
            "2 · « Fond d’image » était trop grossier",
            "Les 27 700 textes dits « sur fond d’image » étaient tous sur des dégradés.",
            "27 700 → 0 sur image · 17 500 jugés.",
        ),
        (
            "3 · Les arrêts passaient pour des calques",
            "La virgule entre deux arrêts ressemble à celle entre deux couches : chaque arrêt devenait un calque.",
            "Plage recalculée · banc test_contraste-degrade.py.",
        ),
    ]
    for index, (titre, explication, chiffre) in enumerate(fautes):
        x = 78 + index * 620
        cadre(dessin, x, y + 44, 580, 210, fond=PAPIER)
        dessin.text((x + 24, y + 62), titre, font=police(21, gras=True), fill=ENCRE)
        fin = paragraphe(dessin, x + 24, y + 96, explication, police(18), 532)
        dessin.text((x + 24, min(y + 216, fin + 10)), chiffre, font=mono(16), fill=BLEU)

    # --- Le compte du relevé ------------------------------------------------
    y = 1000
    cadre(dessin, 78, y, 1844, 150, fond=PAPIER)
    dessin.text((104, y + 20), "Le relevé du 3 novembre 2026, sur 1 060 cadrages", font=police(22, gras=True), fill=ENCRE)
    compteurs = [
        ("385 810", "textes sur fond uni"),
        ("17 500", "textes sur dégradé"),
        ("0", "texte sur fond d’image"),
        ("1 060 / 1 060", "cadrages mesurés"),
        ("0", "refus de contraste"),
    ]
    for index, (nombre, libelle) in enumerate(compteurs):
        x = 104 + index * 356
        dessin.text((x, y + 62), nombre, font=police(30, gras=True), fill=NAVY)
        dessin.text((x, y + 106), libelle, font=police(18), fill=MUTED)

    pied(
        dessin,
        "outils/mesurer-cadrages.cjs · outils/cadrages.py · outils/test_contraste-degrade.py · docs/rd/formats-affichage.md §13",
        "À dire : la zone retenue par cette planche est-elle la bonne, ou faut-il descendre à la ligne de texte ?",
    )
    chemin = SORTIE / "Planche-2-degrades-ce-qui-est-juge.png"
    image.save(chemin)
    return chemin


def planche_decisions() -> Path:
    image = Image.new("RGB", (LARGEUR, HAUTEUR), BLANC)
    dessin = ImageDraw.Draw(image)
    bandeau(
        dessin,
        "Trois décisions qui t’attendent — rien n’est tranché ici",
        "M.R.S.C. — R&D · 4 novembre 2026 · mesuré, nommé, laissé à une personne",
    )

    # --- A. Rangées incomplètes --------------------------------------------
    y = 148
    cadre(dessin, 78, y, 1844, 520)
    dessin.text((104, y + 22), "A · 16 couples page/grille laissent un vide dans leur dernière rangée", font=police(25, gras=True), fill=ENCRE)
    dessin.text(
        (104, y + 58),
        "Ce n’est pas une faute : sept cartes en six colonnes laissent une carte seule. La question est de savoir si ce vide est voulu.",
        font=police(19),
        fill=MUTED,
    )
    gauche, haut = 104, y + 96
    largeur_dispo, gouttiere, colonnes = 1000, 22, 6
    largeur_colonne = (largeur_dispo - gouttiere * (colonnes - 1)) / colonnes
    for index in range(7):
        rangee, colonne = divmod(index, colonnes)
        x = gauche + colonne * (largeur_colonne + gouttiere)
        yy = haut + rangee * 92
        dessin.rounded_rectangle([x, yy, x + largeur_colonne, yy + 72], radius=10, fill=BLEU_PALE, outline=(196, 210, 234), width=2)
    dessin.rounded_rectangle(
        [gauche + largeur_colonne + gouttiere, haut + 92, gauche + largeur_dispo, haut + 164],
        radius=10,
        fill=(250, 244, 232),
        outline=OR,
        width=2,
    )
    dessin.text((gauche + largeur_colonne + gouttiere + 24, haut + 112), "1 176,50 px libres", font=police(23, gras=True), fill=(122, 78, 16))
    dessin.text((104, haut + 186), "apprendre.html · .learning-catalogue-grid — Compacte, 75 %, 1 440 px : une carte sur six colonnes.", font=police(18), fill=ENCRE)
    dessin.text((104, haut + 212), "C’est le pire des seize couples ; les quinze autres sont nommés par `cadrages.py --orphelins`, à chaque CI.", font=police(18), fill=MUTED)

    # Les quatre plus gros vides, en barres proportionnelles.
    barres = [
        ("apprendre · .learning-catalogue-grid", 1176.50),
        ("ia-societe · .ai-fraud-lesson-list", 1048.19),
        ("liens-utiles · .link-grid", 1048.19),
        ("huit grilles à 3 col. · Vitrine 115 %", 850.67),
    ]
    haut_barres = y + 372
    for index, (nom, valeur) in enumerate(barres):
        yy = haut_barres + index * 34
        dessin.text((104, yy), nom, font=police(16), fill=ENCRE)
        longueur = int(valeur / 1176.50 * 300)
        dessin.rounded_rectangle([470, yy + 3, 470 + longueur, yy + 19], radius=5, fill=(232, 205, 158))
        lisible = f"{valeur:,.2f}".replace(",", " ").replace(".", ",")
        dessin.text((470 + longueur + 10, yy - 1), lisible + " px", font=mono(15), fill=(122, 78, 16))
    # Le choix, à droite, dans sa propre colonne : rien ne se chevauche.
    dessin.rectangle([1400, y + 96, 1402, y + 470], fill=TRAIT)
    dessin.text((1432, y + 108), "Les trois issues possibles", font=police(20, gras=True), fill=ENCRE)
    issues = [
        ("1 · Autre nombre de colonnes", "la grille cesse d’accueillir six cartes ;"),
        ("", "le dessin se referme sur quatre colonnes."),
        ("2 · Carte seule assumée", "le vide reste, et le motif est écrit"),
        ("", "dans le registre, à côté du chiffre."),
        ("3 · Garder tel quel", "on ne touche à rien et le diagnostic"),
        ("", "continue de l’imprimer à chaque CI."),
    ]
    yy = y + 156
    for titre, suite in issues:
        if titre:
            dessin.text((1432, yy), titre, font=police(19, gras=True), fill=BLEU)
            yy += 26
        dessin.text((1432, yy), suite, font=police(17), fill=ENCRE)
        yy += 34 if not titre else 12

    # --- B. Le glyphe décoratif --------------------------------------------
    y = 690
    cadre(dessin, 78, y, 900, 400)
    dessin.text((104, y + 22), "B · Le glyphe ✦ du jeu « Les Mondes »", font=police(25, gras=True), fill=ENCRE)
    dessin.text((104, y + 58), "span.adventure-map-mark · aria-hidden · 2 rem · sur surface blanche", font=mono(16), fill=MUTED)
    dessin.text((104, y + 96), "✦", font=police(84), fill=OR)
    dessin.text((196, y + 100), "2,66:1", font=police(40, gras=True), fill=ROUGE)
    dessin.text((196, y + 152), "aujourd’hui — #d29236", font=mono(17), fill=MUTED)
    candidats = [("b57c26", 3.06), ("a8701f", 4.20), ("9a6415", 4.99), ("835100", 6.68)]
    for index, (code, valeur) in enumerate(candidats):
        x = 104 + index * 214
        dessin.text((x, y + 200), "✦", font=police(48), fill=tuple(int(code[i : i + 2], 16) for i in (0, 2, 4)))
        dessin.text((x + 56, y + 208), f"{valeur:.2f}:1".replace(".", ","), font=police(21, gras=True), fill=ENCRE)
        dessin.text((x + 56, y + 238), f"#{code}", font=mono(15), fill=MUTED)
    dessin.text((104, y + 286), "Décoratif déclaré : il n’est pas jugé comme du texte. Le seuil non textuel est 3:1.", font=police(17), fill=MUTED)
    dessin.text((104, y + 322), "Question : l’assumer tel quel, le foncer à 3:1,", font=police(18, gras=True), fill=BLEU)
    dessin.text((104, y + 348), "ou le traiter comme du texte (4,5:1) ?", font=police(18, gras=True), fill=BLEU)

    # --- C. Les divergences sous le pixel ----------------------------------
    cadre(dessin, 1022, y, 900, 400)
    dessin.text((1048, y + 22), "C · Quatre colonnes s’écartent de moins d’un pixel", font=police(25, gras=True), fill=ENCRE)
    dessin.text((1048, y + 58), "écart entre le nombre de colonnes déclaré et celui mesuré", font=police(18), fill=MUTED)
    ecarts = [(".mission-grid", 0.78), (".home-share-panel", 0.60), (".hero-grid", 0.28), (".english-promo-panel", 0.20)]
    for index, (nom, valeur) in enumerate(ecarts):
        yy = y + 102 + index * 48
        dessin.text((1048, yy), nom, font=mono(18), fill=ENCRE)
        longueur = max(5, int(valeur / 0.78 * 300))
        dessin.rounded_rectangle([1420, yy + 4, 1420 + longueur, yy + 22], radius=5, fill=(196, 210, 234))
        dessin.text((1760, yy), f"{valeur:.2f} px".replace(".", ","), font=mono(18), fill=MUTED)
    dessin.text((1048, y + 300), "À 96 dpi, 0,2 à 0,8 px ne se voient pas : ce sont des arrondis de", font=police(17), fill=ENCRE)
    dessin.text((1048, y + 324), "calcul de piste, pas des défauts visibles.", font=police(17), fill=ENCRE)
    dessin.text((1048, y + 356), "Question : comptés comme aujourd’hui, ou absorbés ?", font=police(18, gras=True), fill=BLEU)

    pied(
        dessin,
        "docs/rd/cadrages.toml [rangees] · assets/css/anglais-aventure.css (map-mark) · docs/rd/journal.md",
        "Réponds par A, B, C — ou par « garde tel quel » : chaque choix sera écrit avec son motif.",
    )
    chemin = SORTIE / "Planche-3-decisions-en-attente.png"
    image.save(chemin)
    return chemin


def principal(arguments: list[str] | None = None) -> int:
    global SORTIE
    analyseur = argparse.ArgumentParser(description="Dessine les planches visuelles de la R&D.")
    analyseur.add_argument(
        "--sortie",
        type=Path,
        default=SORTIE,
        help="dossier d'écriture (par défaut : build/planches-rd, hors dépôt versionné)",
    )
    options = analyseur.parse_args(arguments)
    SORTIE = options.sortie
    SORTIE.mkdir(parents=True, exist_ok=True)
    for fabrique in (planche_muted, planche_degrades, planche_decisions):
        print(fabrique())
    print(
        f"Planches : 3 fichier(s) écrit(s) dans {SORTIE}. Dessin mesuré (WCAG 2.2), "
        "pas une capture de navigateur.",
        file=sys.stderr,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(principal())
