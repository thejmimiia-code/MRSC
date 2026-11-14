#!/usr/bin/env python3
"""Assemble la page « Coût de la vie » à partir de la coque du site.

La page est écrite en deux morceaux : un fragment de contenu
(`couts-vie-chere/contenu.txt`) et la coque commune — en-tête, navigation,
pied de page — reprise de `localisation.html`. Pourquoi ainsi : recopier la
coque à la main dans une onzième page la ferait diverger au premier changement
de navigation, et le contrôle d'intégration finirait par la signaler sans qu'on
sache laquelle des deux versions est la bonne. Ici, la coque a **une** source.

Ce que l'outil refuse :

- une coque qui ne contient pas `</main>` ou pas de pied de page ;
- une page qui garderait l'`aria-current` de la page d'origine (deux pages
  « courantes » dans la navigation seraient un mensonge d'état) ;
- une page sans titre, sans description, sans canonique ni lien d'évitement ;
- un fragment de contenu qui n'a pas de `h1`.

Usage :
    python3 outils/construire-page-couts.py
    python3 outils/construire-page-couts.py --verifier
"""

from __future__ import annotations

import argparse
import html
import json
import os
import re
import sys
from pathlib import Path

RACINE = Path(os.environ.get("MRSC_RACINE") or Path(__file__).resolve().parent.parent).resolve()
COQUE = RACINE / "localisation.html"
FRAGMENT = RACINE / "couts-vie-chere" / "contenu.txt"
PAGE = RACINE / "couts-vie-chere.html"
TITRE = "Coût de la vie par commune — M.R.S.C"
DESCRIPTION = (
    "Carte de France des prix réels au m² et de la population par commune, "
    "à partir des ventes enregistrées (DVF, DGFiP) et du découpage administratif "
    "de l’État. Les chiffres absents sont dits absents."
)
CANONIQUE = "https://thejmimiia-code.github.io/MRSC/couts-vie-chere.html"
LOYERS = RACINE / "assets" / "data" / "vie-chere" / "loyers.json"
#: Le fragment porte la section des loyers, avec ses deux marques : le tableau
#: lui-même n'est pas écrit à la main, il est le rendu de la collecte. Recopier
#: cinquante-trois lignes à la main ferait diverger la page de la donnée au
#: premier millésime, sans que rien ne le signale.
MARQUE_DEBUT = "<!-- loyers:debut -->"
MARQUE_FIN = "<!-- loyers:fin -->"
#: La cellule « ce qui est affiché » du tableau des postes décrit un état, pas une
#: intention : elle est donc écrite par le même rendu que le tableau, pour qu'elle
#: ne puisse pas affirmer une collecte qui n'a pas eu lieu.
MARQUE_ETAT = "<!-- loyers:etat -->"
SCRIPT = '  <script src="assets/js/carte-vie-chere.js" defer></script>\n'


def nombre_fr(valeur: float, decimales: int = 0) -> str:
    """Un nombre à la française : virgule décimale, espaces fines des milliers."""
    texte = f"{valeur:,.{decimales}f}".replace(",", "\u202f")
    return texte.replace(".", ",")


def bloc_loyers() -> str:
    """Le rendu de la collecte des loyers, ou l'aveu qu'elle n'a pas eu lieu."""
    if not LOYERS.is_file():
        return (
            '<p class="couts-note">Aucune collecte de loyers n’a encore été faite : '
            "la page ne les estime pas et n’affiche aucun chiffre. La source est identifiée "
            "(observatoires locaux des loyers, Licence Ouverte 2.0) et la collecte est en place ; "
            "le premier passage la fera entrer.</p>"
        )
    donnees = json.loads(LOYERS.read_text(encoding="utf-8"))
    territoires = donnees.get("territoires") or []
    if not territoires:
        raise ValueError("la collecte des loyers ne contient aucun territoire")
    annee = donnees.get("annee")
    lignes = []
    for territoire in territoires:
        logements = territoire.get("logements")
        lignes.append(
            "              <tr>"
            f'<th scope="row">{html.escape(str(territoire["nom"]))} '
            f'<span>({html.escape(str(territoire["observatoire"]))})</span></th>'
            f'<td>{nombre_fr(float(territoire["loyer_median"]), 2)}&nbsp;€/m²</td>'
            f'<td>{nombre_fr(float(territoire["loyer_mensuel_median"]))}&nbsp;€</td>'
            f'<td>{nombre_fr(float(territoire["surface_moyenne"]))}&nbsp;m²</td>'
            f'<td>{nombre_fr(float(logements)) if logements is not None else "non publié"}</td>'
            "</tr>"
        )
    source = donnees.get("source") or {}
    sans_logements = sum(1 for territoire in territoires if territoire.get("logements") is None)
    phrase_absences = (
        f" {sans_logements} d’entre eux publient un loyer sans nombre de logements : "
        "la colonne l’écrit « non publié », elle n’écrit pas zéro."
        if sans_logements
        else ""
    )
    return (
        f"<p>{len(territoires)} territoires sont observés par le réseau des observatoires "
        f"locaux des loyers en {html.escape(str(annee))}. La maille est l’agglomération, pas la "
        "commune : cette liste n’est donc pas un calque de la carte, et le site ne rattache "
        f"aucune agglomération à ses communes, faute de source qui le publie.{phrase_absences}</p>\n"
        '            <div class="couts-tableau-defilant" tabindex="0" role="region" '
        'aria-labelledby="titre-tableau-loyers">\n'
        '              <table class="couts-tableau">\n'
        '                <caption id="titre-tableau-loyers">Loyers observés en '
        f"{html.escape(str(annee))}, agglomération par agglomération</caption>\n"
        "                <thead>\n"
        "                  <tr><th scope=\"col\">Territoire observé</th>"
        "<th scope=\"col\">Loyer médian au m²</th>"
        "<th scope=\"col\">Loyer médian mensuel</th>"
        "<th scope=\"col\">Surface moyenne</th>"
        "<th scope=\"col\">Logements observés</th></tr>\n"
        "                </thead>\n"
        "                <tbody>\n" + "\n".join(lignes) + "\n"
        "                </tbody>\n"
        "              </table>\n"
        "            </div>\n"
        '            <p class="couts-source">Observatoires locaux des loyers (réseau OLL animé par '
        f"l’ANIL), « {html.escape(str(source.get('ressource_titre')))} », "
        f"{html.escape(str(source.get('licence')))}. Ressource modifiée le "
        f"{html.escape(str(source.get('date_ressource'))[:10])}, collecte du "
        f"{html.escape(str(donnees.get('collecte_le')))}. "
        f'<a href="{html.escape(str(source.get("fiche")))}">Fiche du jeu de données</a>. '
        "Ce que ces chiffres ne disent pas : le loyer d’un logement précis, celui d’une commune "
        "à l’intérieur de l’agglomération, les charges, ni ce qu’un ménage donné peut se "
        "permettre.</p>"
    )


def etat_loyers() -> str:
    if not LOYERS.is_file():
        return (
            "Rien pour l’instant : la collecte des loyers par agglomération n’a pas encore eu "
            "lieu ; la source est identifiée et l’outil en place"
        )
    return (
        "Affiché : loyer médian au m² et loyer médian mensuel, surface moyenne et nombre de "
        "logements observés, agglomération par agglomération"
    )


def injecter(fragment: str) -> str:
    """Remplace le contenu entre les deux marques par le rendu de la collecte."""
    if MARQUE_DEBUT not in fragment or MARQUE_FIN not in fragment:
        raise ValueError(f"le fragment n'a pas ses deux marques de loyers ({MARQUE_DEBUT})")
    debut = fragment.index(MARQUE_DEBUT)
    fin = fragment.index(MARQUE_FIN)
    if fin < debut:
        raise ValueError("les marques de loyers sont dans le désordre")
    # Les deux bords sont rognés : une indentation laissée seule sur sa ligne
    # ferait un « espace final », que la porte du site statique refuse — à raison.
    avant = fragment[:debut].rstrip()
    apres = fragment[fin + len(MARQUE_FIN):].lstrip("\n")
    fragment = avant + "\n" + bloc_loyers() + "\n" + apres
    if fragment.count(MARQUE_ETAT) != 1:
        raise ValueError(f"le fragment n'a pas exactement une marque d'état des loyers ({MARQUE_ETAT})")
    return fragment.replace(MARQUE_ETAT, etat_loyers())


def coque() -> tuple[str, str]:
    texte = COQUE.read_text(encoding="utf-8")
    if "</main>" not in texte:
        raise ValueError("la coque ne contient pas de fin de zone principale")
    debut = texte.index("<main")
    fin = texte.index("</main>") + len("</main>")
    return texte[:debut], texte[fin:]


def assembler() -> str:
    entete, pied = coque()
    fragment = injecter(FRAGMENT.read_text(encoding="utf-8").strip())
    if "<h1" not in fragment:
        raise ValueError("le fragment de contenu n'a pas de titre de niveau 1")
    entete = re.sub(r"<title>.*?</title>", f"<title>{TITRE}</title>", entete, count=1)
    entete = re.sub(
        r'<meta name="description" content="[^"]*">',
        f'<meta name="description" content="{DESCRIPTION}">',
        entete,
        count=1,
    )
    entete = re.sub(
        r'<link rel="canonical" href="[^"]*">',
        f'<link rel="canonical" href="{CANONIQUE}">',
        entete,
        count=1,
    )
    # Une seule page « courante » à la fois : celle d'où la coque est reprise
    # n'est pas cette page-ci.
    entete = entete.replace(' aria-current="page"', "")
    pied = pied.replace(' aria-current="page"', "")
    entete = entete.replace("data-print-url=\"https://thejmimiia-code.github.io/MRSC/localisation.html\"",
                            "data-print-url=\"https://thejmimiia-code.github.io/MRSC/couts-vie-chere.html\"")
    if SCRIPT.strip() not in entete:
        entete = entete.replace("</head>", SCRIPT + "</head>", 1)
    return entete + '<main id="contenu">\n' + fragment + "\n  </main>" + pied


def verifier(contenu: str) -> int:
    erreurs: list[str] = []
    if TITRE not in contenu:
        erreurs.append("titre absent")
    if CANONIQUE not in contenu:
        erreurs.append("canonique absente")
    if "carte-vie-chere.js" not in contenu:
        erreurs.append("script de la carte absent")
    if 'class="skip-link"' not in contenu:
        erreurs.append("lien d'évitement absent")
    if 'aria-current="page"' in contenu.split("<main")[0]:
        erreurs.append("une entrée de navigation se déclare page courante")
    if contenu.count("<h1") != 1:
        erreurs.append(f"{contenu.count('<h1')} titre(s) de niveau 1 au lieu d'un")
    if contenu.count("<main") != 1:
        erreurs.append(f"{contenu.count('<main')} zone(s) principale(s)")
    for marque in (MARQUE_DEBUT, MARQUE_FIN, MARQUE_ETAT):
        if marque in contenu:
            erreurs.append(f"marque de loyers non remplacée dans la page : {marque}")
    if LOYERS.is_file():
        if "Loyer médian mensuel" not in contenu:
            erreurs.append("collecte des loyers présente mais tableau absent de la page")
    elif "Aucune collecte de loyers" not in contenu:
        erreurs.append("aucune collecte de loyers, et la page ne le dit pas")
    if erreurs:
        for erreur in erreurs:
            print(f"ERREUR — {erreur}", file=sys.stderr)
        return 1
    return 0


def principal() -> int:
    analyseur = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    analyseur.add_argument("--verifier", action="store_true", help="la page publiée est-elle le rendu du fragment ?")
    arguments = analyseur.parse_args()
    try:
        contenu = assembler()
    except (OSError, ValueError) as erreur:
        print(f"ERREUR — {erreur}", file=sys.stderr)
        return 1
    if arguments.verifier:
        if not PAGE.is_file():
            print("ERREUR — page absente : lancer sans --verifier.", file=sys.stderr)
            return 1
        if PAGE.read_text(encoding="utf-8") != contenu:
            print("ERREUR — la page publiée n'est plus le rendu du fragment : relancer l'outil.", file=sys.stderr)
            return 1
        if verifier(contenu):
            return 1
        print("Page des coûts à jour : coque commune, un seul titre de niveau 1, aucune navigation trompeuse.")
        return 0
    if verifier(contenu):
        return 1
    PAGE.write_text(contenu, encoding="utf-8")
    print(f"Page écrite : {PAGE.relative_to(RACINE)} — {PAGE.stat().st_size // 1024} Kio.")
    return 0


if __name__ == "__main__":
    raise SystemExit(principal())
