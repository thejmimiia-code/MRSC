"""
simulateur/pont_api.py — Pont HTTP du moteur vers les hébergeurs sans serveur.

Le moteur du simulateur (`simulateur.dashboard.DashboardHandler`) route sur
`self.path` et sert toutes les routes depuis un seul processus. Sur un
hébergeur à fonctions (Vercel), chaque fichier de `api/` devient une route
distincte et reçoit l'URL complète de la requête : il faut donc réécrire le
chemin reçu sur la route déclarée, en conservant la chaîne de requête.

    api/catalogue.py  ->  class handler(FonctionAPI): ROUTE = "/api/catalogue"

⚠️ Ce fichier est un **ajout du dépôt du site M.R.S.C**, il ne vient pas du
dépôt du simulateur : `outils/mettre-a-jour-simulateur.py` ne doit ni
l'écraser ni le supprimer lors d'une mise à jour du moteur.
"""

from __future__ import annotations

import os

# Sur un hébergeur à fonctions, le dossier du projet est en lecture seule :
# le cache des données publiques part dans /tmp (éphémère, une instance à la
# fois). Le moteur retombe sans cache si l'écriture échoue, mais autant lui
# donner un chemin inscriptible. Ce réglage doit précéder l'import du moteur,
# qui lit la variable à l'initialisation de `simulateur.donnees_live`.
os.environ.setdefault("SIMULATEUR_CACHE", "/tmp/simulateur_cache")

from simulateur.dashboard import DashboardHandler  # noqa: E402


class FonctionAPI(DashboardHandler):
    """Sert une route unique du moteur, quel que soit le chemin reçu."""

    #: Route servie, par exemple « /api/catalogue » (défini par la sous-classe).
    ROUTE = ""

    def do_GET(self) -> None:  # noqa: N802 - API stdlib
        self._deleguer("GET")

    def do_POST(self) -> None:  # noqa: N802 - API stdlib
        self._deleguer("POST")

    def do_HEAD(self) -> None:  # noqa: N802 - API stdlib
        self._deleguer("HEAD")

    def _deleguer(self, methode: str) -> None:
        if not self.ROUTE:
            raise RuntimeError("La sous-classe doit définir ROUTE (ex. « /api/catalogue »).")
        requete = self.path.split("?", 1)
        # Idempotent : do_HEAD rappelle self.do_GET(), qui repasse ici.
        self.path = self.ROUTE + (("?" + requete[1]) if len(requete) > 1 else "")
        if methode == "GET":
            DashboardHandler.do_GET(self)
        elif methode == "POST":
            DashboardHandler.do_POST(self)
        else:
            DashboardHandler.do_HEAD(self)
