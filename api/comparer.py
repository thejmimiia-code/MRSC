"""Fonction Vercel — route comparer du simulateur.

Fichier généré par `outils/generer-fonctions-api.py` : ne pas modifier à la
main. Toute la logique vient du moteur, voir `simulateur/pont_api.py`.
"""

import pathlib
import sys

RACINE = pathlib.Path(__file__).resolve().parent.parent
if str(RACINE) not in sys.path:
    sys.path.insert(0, str(RACINE))

from simulateur.pont_api import FonctionAPI  # noqa: E402


class handler(FonctionAPI):
    ROUTE = "/api/comparer"
