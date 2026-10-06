#!/usr/bin/env python3
"""Serveur local du site M.R.S.C — se comporte comme Vercel et GitHub Pages.

Les deux hébergeurs servent ``404.html`` pour toute adresse inconnue et
n'affichent jamais de listing de dossier. Ce serveur reproduit ce comportement
pour que l'aperçu local corresponde exactement à ce que voient les visiteurs
(et pour vérifier une page 404 avant publication).

Usage :
    python3 outils/serveur-local.py [--port 4173] [--bind 0.0.0.0]
"""

from __future__ import annotations

import argparse
import mimetypes
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent


class ServeurSite(SimpleHTTPRequestHandler):
    """Fichiers statiques, dossier interdit, ``404.html`` en guise d'erreur."""

    def list_directory(self, path):  # noqa: ARG002 — signature imposée par la classe parente
        """Aucun listing de dossier : on répond 404 (comme Vercel et GitHub Pages)."""
        self.send_error(404, "Not Found")
        return None

    def send_error(self, code, message=None, explain=None):  # noqa: ARG002
        if code == 404:
            page = RACINE / "404.html"
            if page.is_file():
                contenu = page.read_bytes()
                self.send_response(404)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(contenu)))
                self.send_header("Cache-Control", "no-store")
                self.end_headers()
                if self.command != "HEAD":
                    self.wfile.write(contenu)
                return
        super().send_error(code, message, explain)


def main() -> None:
    analyseur = argparse.ArgumentParser(description="Aperçu local du site M.R.S.C.")
    analyseur.add_argument("--port", type=int, default=4173, help="port d'écoute (4173 par défaut)")
    analyseur.add_argument("--bind", default="0.0.0.0", help="adresse d'écoute (0.0.0.0 par défaut)")
    options = analyseur.parse_args()

    mimetypes.add_type("image/jpeg", ".jpg")
    gestionnaire = partial(ServeurSite, directory=str(RACINE))
    with ThreadingHTTPServer((options.bind, options.port), gestionnaire) as serveur:
        print(f"Site M.R.S.C servi sur http://{options.bind}:{options.port} (racine : {RACINE})")
        print("Adresse inconnue → page 404.html, comme sur Vercel et GitHub Pages.")
        try:
            serveur.serve_forever()
        except KeyboardInterrupt:
            print("\nArrêt du serveur.")


if __name__ == "__main__":
    main()
