#!/usr/bin/env python3
"""Éprouve `annoncer-echec-graphismes.py` : il recopie les constats, et avoue le vide.

Un outil d'annotation qui se tairait devant un relevé vide reproduirait
exactement le défaut qu'il corrige : une CI rouge sans explication.

Usage :
    python3 outils/test_annoncer_echec_graphismes.py
"""

from __future__ import annotations

import importlib.util
import io
import json
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent


def charger():
    spec = importlib.util.spec_from_file_location(
        "annoncer_echec_graphismes", RACINE / "outils" / "annoncer-echec-graphismes.py"
    )
    module = importlib.util.module_from_spec(spec)
    sys.modules["annoncer_echec_graphismes"] = module
    spec.loader.exec_module(module)
    return module


class TestAnnoncerEchec(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.outil = charger()

    def annoncer(self, dossier: Path) -> str:
        sortie = io.StringIO()
        with redirect_stdout(sortie):
            self.outil.annoncer(dossier)
        return sortie.getvalue()

    def test_les_erreurs_sont_recopiees_en_annotations(self) -> None:
        with tempfile.TemporaryDirectory() as dossier:
            chemin = Path(dossier) / "releve.json"
            chemin.write_text(
                json.dumps({"erreurs": [{"route": "apprendre.html", "motif": "densité insuffisante"}]}),
                encoding="utf-8",
            )
            sortie = self.annoncer(Path(dossier))
        self.assertIn("::error title=Graphismes::", sortie)
        self.assertIn("densité insuffisante", sortie)

    def test_un_releve_sans_constat_dit_que_l_echec_vient_d_ailleurs(self) -> None:
        """Un JSON valide et vide ne doit pas laisser croire que tout va bien."""
        with tempfile.TemporaryDirectory() as dossier:
            (Path(dossier) / "mutation-distorsion.json").write_text(
                json.dumps({"erreurs": []}), encoding="utf-8"
            )
            sortie = self.annoncer(Path(dossier))
        self.assertIn("aucun constat écrit", sortie)

    def test_un_dossier_vide_est_nomme(self) -> None:
        with tempfile.TemporaryDirectory() as dossier:
            sortie = self.annoncer(Path(dossier))
        self.assertIn("aucun relevé", sortie)

    def test_un_releve_illisible_est_nomme(self) -> None:
        with tempfile.TemporaryDirectory() as dossier:
            (Path(dossier) / "releve.json").write_text("{ pas du json", encoding="utf-8")
            sortie = self.annoncer(Path(dossier))
        self.assertIn("illisible", sortie)

    def test_plus_de_six_erreurs_sont_comptees(self) -> None:
        """Les annotations sont bornées : le reste est dit, pas passé sous silence."""
        with tempfile.TemporaryDirectory() as dossier:
            (Path(dossier) / "releve.json").write_text(
                json.dumps({"erreurs": [f"erreur {i}" for i in range(9)]}), encoding="utf-8"
            )
            sortie = self.annoncer(Path(dossier))
        self.assertIn("3 autre(s)", sortie)


if __name__ == "__main__":
    unittest.main()
