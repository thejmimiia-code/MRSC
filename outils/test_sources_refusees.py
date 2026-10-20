#!/usr/bin/env python3
"""Tests unitaires pour le registre des sources tentées et refusées."""

from __future__ import annotations

import copy
import importlib.util
import unittest
from datetime import date, timedelta
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
SPEC = importlib.util.spec_from_file_location(
    "construire_sources_refusees",
    RACINE / "outils" / "construire-sources-refusees.py",
)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class TestSourcesRefusees(unittest.TestCase):
    def setUp(self) -> None:
        self.aujourdhui = date(2026, 10, 20)
        self.registre = MODULE.charger()
        self.fiches_urls = MODULE.index_catalogue()

    def test_registre_courant_valide(self) -> None:
        erreurs = MODULE.valider(self.registre, self.aujourdhui, self.fiches_urls)
        self.assertEqual(erreurs, [])

    def test_refuse_sans_motif_ou_trop_court(self) -> None:
        copie = copy.deepcopy(self.registre)
        copie["refus"][0]["motif"] = "Trop court."
        erreurs = MODULE.valider(copie, self.aujourdhui, self.fiches_urls)
        self.assertTrue(any("motif trop court" in e for e in erreurs))

    def test_refuse_date_future(self) -> None:
        copie = copy.deepcopy(self.registre)
        copie["refus"][0]["date"] = self.aujourdhui + timedelta(days=2)
        erreurs = MODULE.valider(copie, self.aujourdhui, self.fiches_urls)
        self.assertTrue(any("date dans le futur" in e for e in erreurs))

    def test_refuse_fiche_inconnue(self) -> None:
        copie = copy.deepcopy(self.registre)
        copie["refus"][0]["fiche"] = "fiche-imaginaire"
        erreurs = MODULE.valider(copie, self.aujourdhui, self.fiches_urls)
        self.assertTrue(any("fiche inconnue" in e for e in erreurs))

    def test_refuse_url_encore_active_dans_catalogue(self) -> None:
        copie = copy.deepcopy(self.registre)
        copie["refus"][0]["url"] = "https://doc.hal.science/visualisation-dun-depot/"
        erreurs = MODULE.valider(copie, self.aujourdhui, self.fiches_urls)
        self.assertTrue(any("encore citée comme source active" in e for e in erreurs))

    def test_refuse_remplacement_absent_du_catalogue(self) -> None:
        copie = copy.deepcopy(self.registre)
        copie["refus"][0]["url_remplacement"] = "https://exemple.test/page-non-citee"
        erreurs = MODULE.valider(copie, self.aujourdhui, self.fiches_urls)
        self.assertTrue(any("url_remplacement" in e for e in erreurs))

    def test_refuse_citation_longue_sous_droits(self) -> None:
        copie = copy.deepcopy(self.registre)
        copie["refus"][0]["motif"] = (
            "Page écartée après lecture car elle écrit « "
            + ("texte recopié mot à mot depuis la source externe " * 3)
            + " »."
        )
        erreurs = MODULE.valider(copie, self.aujourdhui, self.fiches_urls)
        self.assertTrue(any("extrait entre guillemets trop long" in e for e in erreurs))

    def test_refuse_limite_trop_courte(self) -> None:
        copie = copy.deepcopy(self.registre)
        copie["refus"][0]["limite"] = "Limite brève."
        erreurs = MODULE.valider(copie, self.aujourdhui, self.fiches_urls)
        self.assertTrue(any("limite trop courte" in e for e in erreurs))

    def test_document_genere_ne_pretend_aucune_validation(self) -> None:
        markdown = MODULE.construire(self.registre)
        self.assertIn("Un refus consigné ne valide jamais la fiche associée", markdown)
        self.assertIn("Ce qu'il ne prouve pas", markdown)


if __name__ == "__main__":
    unittest.main()
