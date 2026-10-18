#!/usr/bin/env python3
from __future__ import annotations

import copy
import importlib.util
import tomllib
import unittest
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
SCRIPT = RACINE / "outils" / "verifier-resilience-statutaire.py"
REGISTRE = RACINE / "docs" / "rd" / "statuts-risques.toml"
spec = importlib.util.spec_from_file_location("verifier_resilience_statutaire", SCRIPT)
MODULE = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(MODULE)


class ResilienceStatutaireTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with REGISTRE.open("rb") as fichier:
            cls.registre = tomllib.load(fichier)

    def test_registre_courant_est_coherent(self):
        self.assertEqual(MODULE.verifier(self.registre), [])

    def test_refuse_une_pretention_d_exhaustivite(self):
        registre = copy.deepcopy(self.registre)
        registre["meta"]["exhaustif"] = True
        self.assertTrue(any("exhaustivité" in erreur for erreur in MODULE.verifier(registre)))

    def test_refuse_un_risque_supprime(self):
        registre = copy.deepcopy(self.registre)
        registre["risque"].pop()
        self.assertTrue(any("16 familles" in erreur for erreur in MODULE.verifier(registre)))

    def test_refuse_un_risque_dit_valide(self):
        registre = copy.deepcopy(self.registre)
        registre["risque"][0]["statut"] = "valide"
        self.assertTrue(any("maintenu à faire relire" in erreur for erreur in MODULE.verifier(registre)))

    def test_refuse_une_porte_non_bloquante(self):
        registre = copy.deepcopy(self.registre)
        registre["porte"][0]["statut"] = "indicative"
        self.assertTrue(any("porte" in erreur for erreur in MODULE.verifier(registre)))


if __name__ == "__main__":
    unittest.main(verbosity=2)
