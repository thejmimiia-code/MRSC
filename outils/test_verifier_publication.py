#!/usr/bin/env python3
"""Tests du contrôle réseau de publication — en particulier du périmètre.

Le 25 octobre 2026, le site publié servait la racine entière du dépôt
(`README.md`, `AGENTS.md`, `outils/`, `docs/`…) parce que GitHub Pages était
réglé sur « Deploy from a branch ». Le contrôle ne regardait que la liste des
fichiers attendus : tout répondait 200, donc il passait au vert alors que le
site publiait ce qu’il devait cacher.

Ces tests vérifient que le contrôle mord désormais dans les deux sens :

1. un hébergement qui sert aussi les documents internes → échec explicite ;
2. un hébergement qui ne sert que le périmètre → succès ;
3. la liste `HORS_PERIMETRE` ne contient que des chemins réellement présents
   dans le dépôt (une cible en trop testerait dans le vide).

Ils tournent hors ligne, contre deux serveurs HTTP locaux temporaires : aucun
réseau, aucune publication.
"""

from __future__ import annotations

import contextlib
import functools
import http.server
import importlib.util
import subprocess
import sys
import tempfile
import threading
import unittest
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
SCRIPT = RACINE / "outils" / "verifier-publication.py"


def charger_module():
    specification = importlib.util.spec_from_file_location("verifier_publication", SCRIPT)
    module = importlib.util.module_from_spec(specification)
    specification.loader.exec_module(module)
    return module


MODULE = charger_module()


@contextlib.contextmanager
def servir(dossier: Path):
    """Sert `dossier` sur 127.0.0.1, sur un port libre, le temps du test."""

    class SansJournal(http.server.SimpleHTTPRequestHandler):
        def log_message(self, *args):  # noqa: ANN002 - signature de la classe parente
            pass

    gestionnaire = functools.partial(SansJournal, directory=str(dossier))
    serveur = http.server.ThreadingHTTPServer(("127.0.0.1", 0), gestionnaire)
    fil = threading.Thread(target=serveur.serve_forever, daemon=True)
    fil.start()
    try:
        yield f"http://127.0.0.1:{serveur.server_address[1]}/"
    finally:
        serveur.shutdown()
        serveur.server_close()
        fil.join(timeout=5)


def construire_site(dossier: Path, *, interne: bool) -> None:
    """Écrit les fichiers du périmètre public, et les documents internes si demandé."""
    for chemin, _, _ in MODULE.CIBLES:
        if not chemin:
            continue  # l’accueil est `index.html` côté serveur
        fichier = dossier / chemin
        fichier.parent.mkdir(parents=True, exist_ok=True)
        fichier.write_bytes(b"contenu de test\n")
    (dossier / "index.html").write_text("<html lang=\"fr\"><title>test</title></html>\n", encoding="utf-8")
    if interne:
        for chemin, _ in MODULE.HORS_PERIMETRE:
            fichier = dossier / chemin
            fichier.parent.mkdir(parents=True, exist_ok=True)
            fichier.write_text("document interne\n", encoding="utf-8")


def executer(base_url: str, *, tentatives: str = "1") -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(SCRIPT), "--base-url", base_url, "--tentatives", tentatives, "--attente", "0"],
        capture_output=True,
        text=True,
        check=False,
    )


class PerimetreTest(unittest.TestCase):
    def test_un_site_qui_sert_la_racine_du_depot_echoue(self):
        with tempfile.TemporaryDirectory() as brut:
            dossier = Path(brut)
            construire_site(dossier, interne=True)
            with servir(dossier) as base_url:
                resultat = executer(base_url)
        self.assertEqual(resultat.returncode, 1, resultat.stdout + resultat.stderr)
        self.assertIn("Périmètre de publication violé", resultat.stderr)
        # Les fichiers attendus, eux, répondent tous 200 et le contrôle ne
        # signale aucun fichier manquant : c’est tout le piège que ce test
        # verrouille — avant, ce seul constat suffisait à passer au vert.
        self.assertNotIn("Fichiers manquants ou injoignables", resultat.stderr)
        self.assertRegex(resultat.stdout, r"\| `README\.md` \| Documentation de développement \| 200 \|")
        self.assertNotIn("aucun n’est servi", resultat.stdout)
        for chemin, _ in MODULE.HORS_PERIMETRE:
            self.assertIn(f"`{chemin}`", resultat.stdout)
        self.assertIn("README.md : servi en 200", resultat.stderr)

    def test_un_site_limite_au_perimetre_reussit(self):
        with tempfile.TemporaryDirectory() as brut:
            dossier = Path(brut)
            construire_site(dossier, interne=False)
            with servir(dossier) as base_url:
                resultat = executer(base_url)
        self.assertEqual(resultat.returncode, 0, resultat.stdout + resultat.stderr)
        self.assertIn("aucun n’est servi", resultat.stdout)
        self.assertNotIn("Périmètre de publication violé", resultat.stderr)

    def test_un_hebergement_injoignable_ne_fait_pas_croire_a_une_fuite(self):
        # Une panne réseau ne doit pas être annoncée comme une publication
        # excessive : le contrôle échoue, mais dit « non vérifié ».
        resultat = executer("http://127.0.0.1:9/")
        self.assertEqual(resultat.returncode, 1)
        self.assertIn("Périmètre non vérifié", resultat.stderr)
        self.assertNotIn("Périmètre de publication violé", resultat.stderr)

    def test_les_cibles_hors_perimetre_existent_dans_le_depot(self):
        for chemin, description in MODULE.HORS_PERIMETRE:
            with self.subTest(chemin=chemin):
                self.assertTrue(description.strip())
                self.assertTrue(
                    (RACINE / chemin).is_file(),
                    f"{chemin} est absent du dépôt : la cible testerait dans le vide",
                )

    def test_le_perimetre_ne_recoupe_pas_les_fichiers_publies(self):
        publies = {(chemin or "index.html") for chemin, _, _ in MODULE.CIBLES}
        for chemin, _ in MODULE.HORS_PERIMETRE:
            with self.subTest(chemin=chemin):
                self.assertNotIn(chemin, publies)


if __name__ == "__main__":
    unittest.main(verbosity=2)
