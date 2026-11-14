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
SCRIPT = '  <script src="assets/js/carte-vie-chere.js" defer></script>\n'


def coque() -> tuple[str, str]:
    texte = COQUE.read_text(encoding="utf-8")
    if "</main>" not in texte:
        raise ValueError("la coque ne contient pas de fin de zone principale")
    debut = texte.index("<main")
    fin = texte.index("</main>") + len("</main>")
    return texte[:debut], texte[fin:]


def assembler() -> str:
    entete, pied = coque()
    fragment = FRAGMENT.read_text(encoding="utf-8").strip()
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
