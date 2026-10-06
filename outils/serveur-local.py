#!/usr/bin/env python3
"""Serveur local du site M.R.S.C — se comporte comme Vercel et GitHub Pages.

Trois responsabilités :

1. **Fichiers statiques** du site, comme les hébergeurs ;
2. **Adresse inconnue → `404.html`**, jamais de listing de dossier (Vercel et
   GitHub Pages servent `404.html` et n'affichent pas les répertoires) ;
3. **`/api/…` → moteur du simulateur**, en relais interne. Sur Vercel, ces
   routes sont servies par les fonctions de `api/` (voir `simulateur/pont_api.py`) ;
   en local, le moteur est lancé dans le même processus et atteint par proxy,
   ce qui donne un aperçu complet page + API sur une seule adresse.

Usage :
    python3 outils/serveur-local.py [--port 4173] [--bind 0.0.0.0] [--sans-moteur]
"""

from __future__ import annotations

import argparse
import json
import mimetypes
import sys
import threading
import urllib.error
import urllib.request
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
if str(RACINE) not in sys.path:  # le script vit dans outils/, le moteur à la racine
    sys.path.insert(0, str(RACINE))


def dire(message: str) -> None:
    """Affiche une ligne immédiatement (les journaux d'aperçu ne sont pas interactifs)."""
    print(message, flush=True)


class ServeurSite(SimpleHTTPRequestHandler):
    """Fichiers statiques, dossier interdit, ``404.html``, relais ``/api/``."""

    #: Adresse interne du moteur du simulateur (renseignée au démarrage).
    moteur: str | None = None

    # ── Pages et ressources ────────────────────────────────────────────────
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

    # ── Relais de l'API du simulateur ──────────────────────────────────────
    def do_GET(self) -> None:  # noqa: N802 - API stdlib
        if self.path.startswith("/api/"):
            return self._relayer("GET")
        return super().do_GET()

    def do_POST(self) -> None:  # noqa: N802 - API stdlib
        if self.path.startswith("/api/"):
            return self._relayer("POST")
        self.send_error(405, "Method Not Allowed")

    def do_HEAD(self) -> None:  # noqa: N802 - API stdlib
        if self.path.startswith("/api/"):
            return self._relayer("HEAD")
        return super().do_HEAD()

    def _relayer(self, methode: str) -> None:
        longueur = int(self.headers.get("Content-Length") or 0)
        corps = self.rfile.read(longueur) if longueur else None

        if not self.moteur:
            return self._repondre_json(
                503,
                {
                    "erreur": "Moteur du simulateur indisponible dans cet aperçu.",
                    "remede": "Relancer sans --sans-moteur, ou vérifier le paquet simulateur/.",
                },
            )

        requete = urllib.request.Request(self.moteur + self.path, data=corps, method=methode)
        for entete in ("Content-Type", "Accept"):
            valeur = self.headers.get(entete)
            if valeur:
                requete.add_header(entete, valeur)
        try:
            with urllib.request.urlopen(requete, timeout=180) as reponse:
                contenu = reponse.read()
                statut = reponse.status
                type_mime = reponse.headers.get("Content-Type", "application/json; charset=utf-8")
        except urllib.error.HTTPError as erreur:
            contenu = erreur.read()
            statut = erreur.code
            type_mime = erreur.headers.get("Content-Type", "application/json; charset=utf-8")
        except (urllib.error.URLError, OSError) as erreur:
            return self._repondre_json(
                502, {"erreur": f"Le moteur du simulateur n'a pas répondu : {erreur}"}
            )

        self.send_response(statut)
        self.send_header("Content-Type", type_mime)
        self.send_header("Content-Length", str(len(contenu)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        if methode != "HEAD":
            self.wfile.write(contenu)

    def _repondre_json(self, statut: int, charge: dict[str, str]) -> None:
        contenu = json.dumps(charge, ensure_ascii=False).encode("utf-8")
        self.send_response(statut)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(contenu)))
        self.end_headers()
        if self.command != "HEAD":
            self.wfile.write(contenu)


def demarrer_moteur(port: int) -> ThreadingHTTPServer | None:
    """Lance le moteur du simulateur en tâche de fond (None s'il est absent)."""
    try:
        from simulateur.dashboard import create_server
    except ImportError as erreur:  # pragma: no cover - dépend de l'environnement
        dire(f"Moteur non chargé ({erreur}) : /api/ répondra 503.")
        return None
    serveur = create_server("127.0.0.1", port)
    threading.Thread(target=serveur.serve_forever, daemon=True).start()
    return serveur


def main() -> None:
    analyseur = argparse.ArgumentParser(description="Aperçu local du site M.R.S.C.")
    analyseur.add_argument("--port", type=int, default=4173, help="port d'écoute (4173 par défaut)")
    analyseur.add_argument("--bind", default="0.0.0.0", help="adresse d'écoute (0.0.0.0 par défaut)")
    analyseur.add_argument("--sans-moteur", action="store_true", help="ne pas lancer l'API du simulateur")
    options = analyseur.parse_args()

    mimetypes.add_type("image/jpeg", ".jpg")

    moteur = None
    if not options.sans_moteur:
        moteur = demarrer_moteur(options.port + 1)
        if moteur:
            ServeurSite.moteur = f"http://127.0.0.1:{options.port + 1}"
            dire(f"API du simulateur chargée en interne sur le port {options.port + 1}.")

    gestionnaire = partial(ServeurSite, directory=str(RACINE))
    with ThreadingHTTPServer((options.bind, options.port), gestionnaire) as serveur:
        dire(f"Site M.R.S.C servi sur http://{options.bind}:{options.port} (racine : {RACINE})")
        dire("Adresse inconnue → page 404.html · /api/… → moteur du simulateur.")
        try:
            serveur.serve_forever()
        except KeyboardInterrupt:
            dire("\nArrêt du serveur.")
        finally:
            if moteur:
                moteur.shutdown()


if __name__ == "__main__":
    main()
