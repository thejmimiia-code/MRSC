#!/usr/bin/env python3
"""Tests du registre documentaire de menaces — aucune cryptographie testée."""

import copy
import importlib.util
import tomllib
import unittest
from pathlib import Path

MODULE_PATH = Path(__file__).with_name("verifier-vote-distanciel.py")
SPEC = importlib.util.spec_from_file_location("verifier_vote_distanciel", MODULE_PATH)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)
REGISTRE_PATH = Path(__file__).parents[1] / "docs" / "rd" / "vote-distanciel-menaces.toml"


class RegistreMenacesTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with REGISTRE_PATH.open("rb") as fichier:
            cls.registre = tomllib.load(fichier)

    def test_registre_courant_est_coherent(self):
        self.assertEqual(MODULE.verifier_registre(self.registre), [])

    def test_refuse_une_menace_supprimee(self):
        registre = copy.deepcopy(self.registre)
        registre["menace"].pop()
        self.assertTrue(any("10 menaces" in erreur for erreur in MODULE.verifier_registre(registre)))

    def test_refuse_un_champ_de_preuve_vide(self):
        registre = copy.deepcopy(self.registre)
        registre["menace"][0]["preuve_attendue"] = ""
        self.assertTrue(any("preuve_attendue" in erreur for erreur in MODULE.verifier_registre(registre)))

    def test_refuse_une_menace_dite_maitrisee(self):
        registre = copy.deepcopy(self.registre)
        registre["menace"][0]["statut"] = "maitrisee"
        self.assertTrue(any("a-expertiser" in erreur for erreur in MODULE.verifier_registre(registre)))

    def test_refuse_un_invariant_duplique(self):
        registre = copy.deepcopy(self.registre)
        registre["invariant"].append(copy.deepcopy(registre["invariant"][0]))
        self.assertTrue(any("sans doublon" in erreur for erreur in MODULE.verifier_registre(registre)))

    def test_refuse_un_registre_detache_de_l_initiative(self):
        registre = copy.deepcopy(self.registre)
        registre["meta"]["initiative"] = "autre"
        self.assertTrue(any("initiative" in erreur for erreur in MODULE.verifier_registre(registre)))


if __name__ == "__main__":
    unittest.main(verbosity=2)
