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
CAS_PATH = RACINE / "docs" / "rd" / "vote-distanciel-cas-essai.toml"
STATUTS_PATH = RACINE / "assets" / "documents" / "statuts-2020.pdf"
DECISION_PATH = RACINE / "docs" / "rd" / "vote-distanciel-decision.md"


def table_decision(valeurs: list[str]) -> str:
    champs = [
        "Version des statuts confirmée", "Règlement intérieur vérifié",
        "Profil retenu", "Option retenue", "Instance ou rôle décideur",
        "Date de décision", "Date de réexamen", "Conditions ou objections",
    ]
    return "\n".join(f"| {champ} | {valeur} |" for champ, valeur in zip(champs, valeurs))


class RegistreMenacesTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with REGISTRE_PATH.open("rb") as fichier:
            cls.registre = tomllib.load(fichier)
        with REGLES_PATH.open("rb") as fichier:
            cls.regles = tomllib.load(fichier)
        with CAS_PATH.open("rb") as fichier:
            cls.cas = tomllib.load(fichier)
        cls.decision = DECISION_PATH.read_text(encoding="utf-8")
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

    def test_cas_synthetiques_couvrent_les_menaces(self):
        self.assertEqual(MODULE.verifier_cas_essai(self.cas), [])

    def test_refuse_un_cas_execute_sans_expertise(self):
        registre = copy.deepcopy(self.cas)
        registre["cas"][0]["statut"] = "reussi"
        self.assertTrue(any("à concevoir" in erreur for erreur in MODULE.verifier_cas_essai(registre)))

    def test_refuse_une_menace_non_couverte(self):
        registre = copy.deepcopy(self.cas)
        for item in registre["cas"]:
            item["menaces"] = [m for m in item["menaces"] if m != "terminal-compromis"]
        self.assertTrue(any("10 menaces" in erreur for erreur in MODULE.verifier_cas_essai(registre)))

    def test_refuse_une_menace_inconnue(self):
        registre = copy.deepcopy(self.cas)
        registre["cas"][0]["menaces"].append("menace-inventee")
        self.assertTrue(any("inconnues" in erreur for erreur in MODULE.verifier_cas_essai(registre)))

    def test_decision_courante_est_en_attente(self):
        self.assertEqual(MODULE.verifier_decision(self.decision), ("en attente", []))

    def test_refuse_une_decision_partielle(self):
        etat, erreurs = MODULE.verifier_decision(table_decision(["oui", "", "", "", "", "", "", ""]))
        self.assertEqual(etat, "invalide")
        self.assertTrue(any("partielle" in erreur for erreur in erreurs))

    def test_refuse_option_d(self):
        valeurs = ["oui", "oui", "ago-premiere", "D", "Conseil", "2026-10-18", "2027-01-31", "Aucune"]
        etat, erreurs = MODULE.verifier_decision(table_decision(valeurs))
        self.assertEqual(etat, "invalide")
        self.assertTrue(any("A, B ou C" in erreur for erreur in erreurs))

    def test_refuse_dissolution_non_interpretee(self):
        valeurs = ["oui", "oui", "dissolution", "B", "Conseil", "2026-10-18", "2027-01-31", "Aucune"]
        etat, erreurs = MODULE.verifier_decision(table_decision(valeurs))
        self.assertEqual(etat, "invalide")
        self.assertTrue(any("dissolution" in erreur for erreur in erreurs))

    def test_accepte_une_decision_complete_bornee(self):
        valeurs = ["oui", "non applicable", "ago-premiere", "B", "Conseil", "2026-10-18", "2027-01-31", "Sous conditions"]
        self.assertEqual(MODULE.verifier_decision(table_decision(valeurs)), ("décision consignée", []))


if __name__ == "__main__":
    unittest.main(verbosity=2)
