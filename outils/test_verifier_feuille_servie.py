#!/usr/bin/env python3
"""Banc hors ligne du contrôle « la feuille servie est celle de la source ».

Le défaut du 5 novembre 2026 n'était pas dans le code : `site.css` portait
l'habillage commun des deux panneaux, mais le site publiait encore l'ancienne
feuille. Un contrôle qui n'a jamais vu une feuille périmée ne peut pas le dire.
Ces essais servent quatre états sur un serveur HTTP de boucle locale — aucun
octet ne sort de la machine — et exigent un verdict distinct pour chacun :

1. feuille identique → 0 ;
2. feuille périmée → 1, avec **les deux empreintes** ;
3. feuille ou source absente → 2, sans jamais affirmer « identique » ;
4. réponse compressée → lue après décompression, et non prise pour une divergence.

Usage : python3 outils/test_verifier_feuille_servie.py
"""

from __future__ import annotations

import contextlib
import functools
import gzip
import hashlib
import http.server
import os
import subprocess
import sys
import tempfile
import threading
import unittest
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
SCRIPT = RACINE / "outils" / "verifier-feuille-servie.py"
CSS = (RACINE / "assets" / "css" / "site.css").read_bytes()


def empreinte(octets: bytes) -> str:
    return hashlib.sha256(octets).hexdigest()[:16]


@contextlib.contextmanager
def servir(dossier: Path, *, compresser: bool = False):
    """Sert `dossier` sur 127.0.0.1 et note les chemins réellement demandés."""
    chemins: list[str] = []

    class SansJournal(http.server.SimpleHTTPRequestHandler):
        def log_message(self, *args):  # noqa: ANN002 - signature de la classe parente
            pass

        def do_GET(self):  # noqa: N802 - nom imposé par http.server
            chemins.append(self.path)
            if not compresser or not self.path.startswith("/assets/css/site.css"):
                return super().do_GET()
            octets = gzip.compress(CSS)
            self.send_response(200)
            self.send_header("Content-Type", "text/css")
            self.send_header("Content-Encoding", "gzip")
            self.send_header("Content-Length", str(len(octets)))
            self.end_headers()
            self.wfile.write(octets)

    gestionnaire = functools.partial(SansJournal, directory=str(dossier))
    serveur = http.server.ThreadingHTTPServer(("127.0.0.1", 0), gestionnaire)
    fil = threading.Thread(target=serveur.serve_forever, daemon=True)
    fil.start()
    try:
        yield f"http://127.0.0.1:{serveur.server_address[1]}/", chemins
    finally:
        serveur.shutdown()
        serveur.server_close()
        fil.join(timeout=5)


def ecrire_feuille(dossier: Path, octets: bytes | None) -> None:
    if octets is None:
        return
    fichier = dossier / "assets" / "css" / "site.css"
    fichier.parent.mkdir(parents=True, exist_ok=True)
    fichier.write_bytes(octets)


def executer(base_url: str, *, racine: Path | None = None, tentatives: str = "1") -> subprocess.CompletedProcess:
    environnement = dict(os.environ)
    if racine is not None:
        environnement["MRSC_RACINE"] = str(racine)
    return subprocess.run(
        [
            sys.executable, str(SCRIPT),
            "--base-url", base_url,
            "--tentatives", tentatives,
            "--attente", "0",
        ],
        capture_output=True,
        text=True,
        env=environnement,
        check=False,
    )


class FeuilleServieTest(unittest.TestCase):
    def test_feuille_identique_passe_et_demande_une_adresse_a_jour(self):
        with tempfile.TemporaryDirectory() as brut:
            ecrire_feuille(Path(brut), CSS)
            with servir(Path(brut)) as (base_url, chemins):
                resultat = executer(base_url)
        self.assertEqual(resultat.returncode, 0, resultat.stdout + resultat.stderr)
        self.assertIn("identique à la source", resultat.stdout)
        self.assertIn(empreinte(CSS), resultat.stdout)
        # L'adresse porte l'empreinte locale : sans elle, un intermédiaire peut
        # répondre avec une copie en cache et le contrôle passerait à tort.
        self.assertTrue(
            any(f"?v={empreinte(CSS)}" in chemin for chemin in chemins),
            f"aucune requête à jour : {chemins}",
        )

    def test_feuille_perimee_echoue_en_nommant_les_deux_empreintes(self):
        perimee = CSS + b"\n/* ancienne feuille */\n"
        with tempfile.TemporaryDirectory() as brut:
            ecrire_feuille(Path(brut), perimee)
            with servir(Path(brut)) as (base_url, _):
                resultat = executer(base_url, tentatives="2")
        self.assertEqual(resultat.returncode, 1, resultat.stdout + resultat.stderr)
        self.assertIn("diverge", resultat.stderr)
        self.assertIn(empreinte(perimee), resultat.stdout)
        self.assertIn(empreinte(CSS), resultat.stdout)
        self.assertIn("déploiement GitHub Pages", resultat.stderr)

    def test_feuille_absente_ne_dit_pas_identique(self):
        with tempfile.TemporaryDirectory() as brut:
            with servir(Path(brut)) as (base_url, _):
                resultat = executer(base_url)
        self.assertEqual(resultat.returncode, 2, resultat.stdout + resultat.stderr)
        self.assertIn("Relevé impossible", resultat.stderr)
        self.assertNotIn("identique à la source", resultat.stdout)
        self.assertNotIn("**diverge**", resultat.stderr)

    def test_source_absente_ne_dit_pas_identique(self):
        with tempfile.TemporaryDirectory() as brut, tempfile.TemporaryDirectory() as vide:
            ecrire_feuille(Path(brut), CSS)
            with servir(Path(brut)) as (base_url, _):
                resultat = executer(base_url, racine=Path(vide))
        self.assertEqual(resultat.returncode, 2, resultat.stdout + resultat.stderr)
        self.assertIn("absente", resultat.stderr)
        self.assertNotIn("identique à la source", resultat.stdout)

    def test_reponse_compressee_est_lue_avant_d_etre_comparee(self):
        with tempfile.TemporaryDirectory() as brut:
            with servir(Path(brut), compresser=True) as (base_url, _):
                resultat = executer(base_url)
        self.assertEqual(resultat.returncode, 0, resultat.stdout + resultat.stderr)
        self.assertIn("identique à la source", resultat.stdout)


if __name__ == "__main__":
    unittest.main(verbosity=2)
