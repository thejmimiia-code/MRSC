#!/usr/bin/env python3
"""Lie la page IA au contenu exact du CSS, pour éviter HTML neuf + CSS en cache.

Après une modification de site.css : python3 outils/versionner-css-ia.py
En CI : python3 outils/versionner-css-ia.py --verifier
Ne modifie ni le cache du navigateur ni la politique de l'hébergeur.
"""
import argparse
import hashlib
from pathlib import Path
import re

RACINE = Path(__file__).resolve().parent.parent
MOTIF = r'href="assets/css/site\.css(?:\?v=[a-f0-9]+)?"'


def versionner(racine=RACINE, verifier=False):
    empreinte = hashlib.sha256((racine / 'assets/css/site.css').read_bytes()).hexdigest()[:16]
    page = racine / 'ia-societe.html'
    texte = page.read_text(encoding='utf-8')
    if len(re.findall(MOTIF, texte)) != 1:
        raise ValueError('Une seule référence au CSS est attendue sur la page IA')
    corrige = re.sub(MOTIF, f'href="assets/css/site.css?v={empreinte}"', texte)
    if verifier and texte != corrige:
        raise ValueError('CSS IA non synchronisé : exécuter python3 outils/versionner-css-ia.py')
    if not verifier:
        page.write_text(corrige, encoding='utf-8')
    return empreinte


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--verifier', action='store_true')
    args = parser.parse_args()
    try:
        print('Version CSS IA :', versionner(verifier=args.verifier))
    except ValueError as erreur:
        parser.exit(1, str(erreur) + '\n')
