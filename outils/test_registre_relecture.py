#!/usr/bin/env python3
"""Tests du contrôle du registre des relectures humaines.

Le registre est la seule trace opposable d'une relecture : si ce contrôle se
casse, un statut peut bouger sans preuve, ou une relecture peut être inventée.
Ces tests vérifient les deux directions, sans toucher au vrai registre.
"""

from __future__ import annotations

import importlib.util
import sys
import unittest
from datetime import date, timedelta
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RACINE / "outils"))
from statuts_editoriaux import PROTOTYPE, RELU  # noqa: E402


def charger_module():
    specification = importlib.util.spec_from_file_location(
        "registre_relecture", RACINE / "outils" / "registre-relecture.py"
    )
    module = importlib.util.module_from_spec(specification)
    specification.loader.exec_module(module)
    return module


MODULE = charger_module()
AUJOURDHUI = date(2026, 10, 20)


def fiche(statut: str | None) -> dict:
    return {"id": "demo", "titre": "Fiche de démonstration", "statut_editorial": statut}


def entree(**remplacements) -> dict:
    base = {
        "fiche": "demo",
        "date": AUJOURDHUI,
        "role": "expertise du domaine — démonstration",
        "perimetre": ["exemples et corrections"],
        "verdict": "conforme",
        "suite": "décision de publication à prendre",
        "objections": [],
        "points_bloquants": [],
    }
    base.update(remplacements)
    return base


class ControleEntree(unittest.TestCase):
    def controler(self, une_entree: dict) -> list[str]:
        erreurs: list[str] = []
        MODULE.controler_entree(1, une_entree, {"demo": fiche(PROTOTYPE)}, AUJOURDHUI, erreurs)
        return erreurs

    def test_entree_complete_acceptee(self):
        self.assertEqual(self.controler(entree()), [])

    def test_date_future_refusee(self):
        erreurs = self.controler(entree(date=AUJOURDHUI + timedelta(days=1)))
        self.assertTrue(any("date future" in erreur for erreur in erreurs), erreurs)

    def test_verdict_inconnu_refuse(self):
        erreurs = self.controler(entree(verdict="excellent"))
        self.assertTrue(any("verdict inconnu" in erreur for erreur in erreurs), erreurs)

    def test_verdict_negatif_sans_objection_refuse(self):
        erreurs = self.controler(entree(verdict="a-corriger"))
        self.assertTrue(any("objection" in erreur for erreur in erreurs), erreurs)

    def test_verdict_negatif_avec_objection_accepte(self):
        self.assertEqual(self.controler(entree(verdict="insuffisant", objections=["exemple ambigu"])), [])

    def test_champ_obligatoire_absent_refuse(self):
        une_entree = entree()
        del une_entree["role"]
        erreurs = self.controler(une_entree)
        self.assertTrue(any("role" in erreur for erreur in erreurs), erreurs)

    def test_fiche_inconnue_refusee(self):
        erreurs = self.controler(entree(fiche="inconnue"))
        self.assertTrue(any("fiche inconnue" in erreur for erreur in erreurs), erreurs)


class CoherenceCatalogue(unittest.TestCase):
    def controler(self, entrees: list[dict], statut: str | None) -> list[str]:
        erreurs: list[str] = []
        MODULE.controler_coherence(entrees, {"demo": fiche(statut)}, erreurs)
        return erreurs

    def test_relecture_conforme_sans_statut_relu_refusee(self):
        erreurs = self.controler([entree()], PROTOTYPE)
        self.assertTrue(any("statut doit" in erreur or "passer la fiche au statut" in erreur for erreur in erreurs), erreurs)

    def test_relecture_conforme_avec_statut_relu_acceptee(self):
        self.assertEqual(self.controler([entree()], RELU), [])

    def test_statut_relu_sans_relecture_refuse(self):
        erreurs = self.controler([], RELU)
        self.assertTrue(any("ne se déclare pas" in erreur for erreur in erreurs), erreurs)

    def test_relecture_negative_avec_statut_relu_refusee(self):
        erreurs = self.controler([entree(verdict="a-corriger", objections=["à revoir"])], RELU)
        self.assertTrue(any("redevenir" in erreur for erreur in erreurs), erreurs)

    def test_fiche_initiale_sans_statut_non_concernee(self):
        self.assertEqual(self.controler([], None), [])


class ChargementReel(unittest.TestCase):
    def test_registre_reel_du_depot_coherent(self):
        erreurs: list[str] = []
        entrees = MODULE.charger_registre(erreurs)
        fiches = MODULE.charger_catalogue()
        for index, element in enumerate(entrees, start=1):
            MODULE.controler_entree(index, element, fiches, date.today(), erreurs)
        MODULE.controler_coherence(entrees, fiches, erreurs)
        self.assertEqual(erreurs, [], erreurs)

    def test_modele_ne_declare_aucune_relecture(self):
        texte = MODULE.modele("demo", {"demo": fiche(PROTOTYPE)})
        self.assertIn("AAAA-MM-JJ", texte)
        self.assertIn("[[relecture]]", texte)
        self.assertNotIn(str(AUJOURDHUI), texte)


if __name__ == "__main__":
    unittest.main()
