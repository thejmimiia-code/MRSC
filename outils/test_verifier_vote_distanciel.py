#!/usr/bin/env python3
"""Tests du registre documentaire de menaces — aucune cryptographie testée."""

import copy
import hashlib
import importlib.util
import tomllib
import unittest
from pathlib import Path

MODULE_PATH = Path(__file__).with_name("verifier-vote-distanciel.py")
SPEC = importlib.util.spec_from_file_location("verifier_vote_distanciel", MODULE_PATH)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)
RACINE = Path(__file__).parents[1]
REGISTRE_PATH = RACINE / "docs" / "rd" / "vote-distanciel-menaces.toml"
REGLES_PATH = RACINE / "docs" / "rd" / "vote-distanciel-regles.toml"
STATUTS_PATH = RACINE / "assets" / "documents" / "statuts-2020.pdf"


class RegistreMenacesTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with REGISTRE_PATH.open("rb") as fichier:
            cls.registre = tomllib.load(fichier)
        with REGLES_PATH.open("rb") as fichier:
            cls.regles = tomllib.load(fichier)
        cls.empreinte_statuts = hashlib.sha256(STATUTS_PATH.read_bytes()).hexdigest()

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

    def test_regles_statutaires_courantes_sont_coherentes(self):
        self.assertEqual(MODULE.verifier_regles(self.regles, self.empreinte_statuts), [])

    def test_refuse_une_empreinte_statutaire_obsolete(self):
        self.assertTrue(any(
            "empreinte" in erreur
            for erreur in MODULE.verifier_regles(self.regles, "0" * 64)
        ))

    def test_refuse_une_regle_statutaire_supprimee(self):
        registre = copy.deepcopy(self.regles)
        registre["regle"].pop()
        self.assertTrue(any(
            "15 règles" in erreur
            for erreur in MODULE.verifier_regles(registre, self.empreinte_statuts)
        ))

    def test_refuse_une_regle_statutaire_dite_validee(self):
        registre = copy.deepcopy(self.regles)
        registre["regle"][0]["statut"] = "validee"
        self.assertTrue(any(
            "à faire relire" in erreur
            for erreur in MODULE.verifier_regles(registre, self.empreinte_statuts)
        ))


if __name__ == "__main__":
    unittest.main(verbosity=2)
