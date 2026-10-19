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
MATRICE = RACINE / "docs" / "rd" / "statuts-matrice-tracabilite.toml"
REGLEMENT = RACINE / "docs" / "rd" / "reglement-interieur-projet.md"
spec = importlib.util.spec_from_file_location("verifier_resilience_statutaire", SCRIPT)
MODULE = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(MODULE)


class ResilienceStatutaireTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with REGISTRE.open("rb") as fichier:
            cls.registre = tomllib.load(fichier)
        with MATRICE.open("rb") as fichier:
            cls.matrice = tomllib.load(fichier)
        cls.reglement = REGLEMENT.read_text(encoding="utf-8")

    def test_registre_courant_est_coherent(self):
        self.assertEqual(MODULE.verifier(self.registre), [])
        self.assertEqual(MODULE.verifier_matrice(self.matrice), [])
        self.assertEqual(MODULE.verifier_reglement(self.reglement), [])

    def test_refuse_un_projet_presente_comme_adopte(self):
        projet = self.reglement.replace("Ce document n’est pas un règlement en vigueur", "Ce règlement est adopté")
        self.assertTrue(any("non adopté" in erreur for erreur in MODULE.verifier_reglement(projet)))

    def test_refuse_un_article_de_reglement_supprime(self):
        projet = self.reglement.replace("### Article RI-82 — Entrée en vigueur et dispositions transitoires", "### Annexe supprimée")
        self.assertTrue(any("82 articles" in erreur for erreur in MODULE.verifier_reglement(projet)))

    def test_refuse_un_groupe_d_articles_supprime(self):
        matrice = copy.deepcopy(self.matrice)
        matrice["article"].pop()
        self.assertTrue(any("20 groupes" in erreur for erreur in MODULE.verifier_matrice(matrice)))

    def test_maintient_la_dissolution_bloquee(self):
        matrice = copy.deepcopy(self.matrice)
        next(item for item in matrice["article"] if item["id"] == "article-19")["statut"] = "valide"
        self.assertTrue(any("dissolution" in erreur for erreur in MODULE.verifier_matrice(matrice)))

    def test_refuse_un_article_sans_classement_normatif(self):
        matrice = copy.deepcopy(self.matrice)
        matrice["classement"].pop()
        self.assertTrue(any("classement normatif" in erreur for erreur in MODULE.verifier_matrice(matrice)))

    def test_refuse_de_classer_la_dissolution_comme_simple_procedure(self):
        matrice = copy.deepcopy(self.matrice)
        next(item for item in matrice["classement"] if item["article"] == "article-19")["niveau"] = "procedure"
        self.assertTrue(any("article-19" in erreur for erreur in MODULE.verifier_matrice(matrice)))

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
