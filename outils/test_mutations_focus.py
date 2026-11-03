#!/usr/bin/env python3
"""Éprouve la mesure du focus dans un vrai navigateur : elle doit mordre.

Le 3 novembre 2026, la mesure a trouvé quarante liens dont l'anneau de focus
tombait à **1,76:1** sur la surface marine de `.creator-note`. La correction a
posé un jeton `--focus-ring`, et la mesure suivante n'a plus rien trouvé. Mais
une mesure qui ne trouve plus rien est exactement ce qu'on obtient d'une mesure
qui ne regarde plus : ce banc retire la correction dans une copie et exige que
le refus revienne, avec le rapport nommé.

Trois cas, comme pour les cadrages :
  1. la copie intacte **passe** — un contrôle qui refuserait toujours ne prouve
     rien non plus ;
  2. la correction retirée (`.creator-note` quitte la liste des surfaces
     sombres) → refus, et le message dit 1,76:1 ;
  3. l'anneau effacé sous le focus (`outline: none`) → refus pour absence
     d'indicateur : ce n'est pas un contraste faible, c'est un repère disparu.

Sans Chromium, le banc sort en **code 2** et le dit — jamais vert. Il vit avec
les autres bancs navigateur, dans le job `graphismes`.

Usage :
    MRSC_BROWSER_NODE_MODULES=… python3 outils/test_mutations_focus.py
"""

from __future__ import annotations

import json
import os
import shutil
import socket
import subprocess
import sys
import tempfile
import time
import unittest
import urllib.request
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RACINE / "outils"))

import banc_mutations  # noqa: E402

PAGE = "transparence.html"
FEUILLE = "assets/css/site.css"


def port_libre() -> int:
    with socket.socket() as prise:
        prise.bind(("127.0.0.1", 0))
        return prise.getsockname()[1]


def attendre(url: str, secondes: float = 20.0) -> None:
    fin = time.monotonic() + secondes
    while time.monotonic() < fin:
        try:
            urllib.request.urlopen(url, timeout=1).read(1)
            return
        except OSError:
            time.sleep(0.2)
    raise AssertionError(f"le serveur local n'a pas répondu en {secondes} s : {url}")


class BancFocus(unittest.TestCase):
    def setUp(self) -> None:
        """Remet la feuille intacte : les mutations ne doivent pas se cumuler.

        Trois cas partagent une copie. Le premier essai de ce banc a appris
        pourquoi : la règle `outline: none` ajoutée par un cas est restée dans la
        feuille, et les deux cas suivants ont accusé « aucun indicateur » partout.
        Une copie jetable n'est pas une copie neuve.
        """
        self.restaurer()

    def restaurer(self) -> None:
        shutil.copyfile(RACINE / FEUILLE, self.copie / FEUILLE)

    @classmethod
    def setUpClass(cls) -> None:
        modules = os.environ.get("MRSC_BROWSER_NODE_MODULES")
        if not modules or not Path(modules).is_dir():
            print(
                "Navigateur absent : MRSC_BROWSER_NODE_MODULES ne pointe pas sur des modules "
                "installés — aucun cas n'a été exécuté (code 2).",
                file=sys.stderr,
            )
            raise SystemExit(2)
        cls.dossier = tempfile.TemporaryDirectory()
        cls.copie = Path(cls.dossier.name) / "copie"
        banc_mutations.copie_complete(cls.copie)
        cls.port = port_libre()
        cls.serveur = subprocess.Popen(
            [sys.executable, "-m", "http.server", str(cls.port), "--bind", "127.0.0.1"],
            cwd=cls.copie,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        attendre(f"http://127.0.0.1:{cls.port}/{PAGE}")

    @classmethod
    def tearDownClass(cls) -> None:
        cls.serveur.terminate()
        cls.serveur.wait(timeout=10)
        cls.dossier.cleanup()

    def mesurer(self) -> tuple[int, list[str]]:
        """Mesure la page dans la copie, puis rend le code du contrôle et ses refus."""
        plan = Path(self.dossier.name) / "plan.json"
        rapport = Path(self.dossier.name) / "rapport.json"
        plan.write_text(
            json.dumps({"pages": [PAGE], "largeurs": [390], "limite": 500}, indent=1),
            encoding="utf-8",
        )
        mesure = subprocess.run(
            ["node", str(RACINE / "outils" / "mesurer-focus.cjs"), str(plan), str(rapport)],
            capture_output=True,
            text=True,
            check=False,
            cwd=RACINE,
            env=dict(os.environ, MRSC_TEST_URL=f"http://127.0.0.1:{self.port}/"),
        )
        self.assertEqual(mesure.returncode, 0, mesure.stdout + mesure.stderr)
        controle = subprocess.run(
            [
                sys.executable,
                str(RACINE / "outils" / "focus.py"),
                "--controler",
                str(plan),
                str(rapport),
            ],
            capture_output=True,
            text=True,
            check=False,
            cwd=RACINE,
        )
        return controle.returncode, (controle.stderr or "").splitlines()

    def test_copie_intacte_passe(self) -> None:
        code, refus = self.mesurer()
        self.assertEqual(code, 0, "\n".join(refus[:10]))

    def test_correction_retiree_refusee(self) -> None:
        """Le cas du 3 novembre 2026 : l'anneau bleu sur la surface marine."""
        banc_mutations.muter(
            self.copie,
            FEUILLE,
            ".site-footer,\n.creator-note,\n.ai-path-panel,",
            ".site-footer,\n.ai-path-panel,",
        )
        code, refus = self.mesurer()
        self.assertEqual(code, 1, "\n".join(refus[:10]))
        self.assertTrue(any("1.76:1" in ligne for ligne in refus), refus[:10])

    def test_anneau_efface_refuse(self) -> None:
        """Un anneau effacé sous le focus n'est pas un anneau : c'est un repère perdu."""
        source = (self.copie / FEUILLE).read_text(encoding="utf-8")
        (self.copie / FEUILLE).write_text(
            source + "\n.creator-note :focus-visible { outline: none; }\n", encoding="utf-8"
        )
        code, refus = self.mesurer()
        self.assertEqual(code, 1, "\n".join(refus[:10]))
        self.assertTrue(any("aucun indicateur" in ligne for ligne in refus), refus[:10])


if __name__ == "__main__":
    unittest.main(verbosity=2)
