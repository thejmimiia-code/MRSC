#!/usr/bin/env python3
"""Tests unitaires pour le prototype borné de confrontation d'affirmations aux sources."""

from __future__ import annotations

import copy
import importlib.util
import unittest
from datetime import date, timedelta
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
SPEC = importlib.util.spec_from_file_location(
    "confronter_sources",
    RACINE / "outils" / "confronter-sources.py",
)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class TestConfronterSources(unittest.TestCase):
    def setUp(self) -> None:
        self.aujourdhui = date(2026, 10, 20)
        self.registre = MODULE.charger()
        self.fiches_urls = MODULE.index_catalogue()

    def test_registre_courant_valide(self) -> None:
        erreurs = MODULE.valider(self.registre, self.aujourdhui, self.fiches_urls)
        self.assertEqual(erreurs, [])

    def test_confronter_texte_quatre_etats(self) -> None:
        texte = "Le climat est une moyenne sur plusieurs décennies, référence de 30 ans."
        r1 = MODULE.confronter_texte(texte, ["moyenne", "décennies", "30 ans"])
        self.assertEqual(r1["etat"], "indice-concordant")

        r2 = MODULE.confronter_texte(texte, ["moyenne", "dissolution"])
        self.assertEqual(r2["etat"], "constat-couverture-partielle")
        self.assertEqual(r2["ancres_absentes"], ["dissolution"])

        r3 = MODULE.confronter_texte(texte, ["inconnue", "équation"])
        self.assertEqual(r3["etat"], "constat-ancre-absente")

        r4 = MODULE.confronter_texte(None, ["moyenne", "30 ans"])
        self.assertEqual(r4["etat"], "constat-page-inaccessible")
        self.assertIn("aucune conclusion sur la fiche", r4["note"])

    def test_faux_positif_negation_et_faux_negatif_pdf(self) -> None:
        # Faux positif : mots présents dans une interdiction
        page_interdiction = (
            "Il est interdit d'indiquer dans une publicité que le prêt améliore le budget de l'emprunteur."
        )
        res_fp = MODULE.confronter_texte(page_interdiction, ["améliore", "budget"])
        self.assertEqual(res_fp["etat"], "indice-concordant")

        # Faux négatif : mot coupé par l'extraction PDF (« dur é e » au lieu de « durée »)
        page_pdf = "vitesse = distanceparcourue / dur é e de parcours"
        res_fn = MODULE.confronter_texte(page_pdf, ["vitesse", "durée"])
        self.assertEqual(res_fn["etat"], "constat-couverture-partielle")
        self.assertEqual(res_fn["ancres_absentes"], ["durée"])

    def test_refuse_extrait_sous_droits_ou_ancre_trop_longue(self) -> None:
        copie = copy.deepcopy(self.registre)
        copie["confrontation"][0]["extrait_source"] = "Extrait recopié de la page externe."
        copie["confrontation"][0]["ancres_attendues"].append(
            "une phrase entière de plus de cinq mots copiée de la source"
        )
        erreurs = MODULE.valider(copie, self.aujourdhui, self.fiches_urls)
        self.assertTrue(any("champ(s) interdit(s)" in e for e in erreurs))
        self.assertTrue(any("ancre trop longue" in e for e in erreurs))

    def test_refuse_etat_de_validation_interdit(self) -> None:
        copie = copy.deepcopy(self.registre)
        copie["confrontation"][0]["etat_releve"] = "valide"
        erreurs = MODULE.valider(copie, self.aujourdhui, self.fiches_urls)
        self.assertTrue(any("etat_releve inconnu ou interdit" in e for e in erreurs))

    def test_refuse_sans_faux_positif_ni_faux_negatif_documentes(self) -> None:
        copie = copy.deepcopy(self.registre)
        copie["confrontation"][0]["faux_positif_possible"] = "Court."
        copie["confrontation"][0]["faux_negatif_possible"] = "Court aussi."
        erreurs = MODULE.valider(copie, self.aujourdhui, self.fiches_urls)
        self.assertTrue(any("faux_positif_possible trop court" in e for e in erreurs))
        self.assertTrue(any("faux_negatif_possible trop court" in e for e in erreurs))

    def test_refuse_url_absente_du_catalogue(self) -> None:
        copie = copy.deepcopy(self.registre)
        copie["confrontation"][0]["url_source"] = "https://exemple.test/source-inconnue"
        erreurs = MODULE.valider(copie, self.aujourdhui, self.fiches_urls)
        self.assertTrue(any("absente des sources" in e for e in erreurs))

    def test_refuse_moins_de_trois_fiches(self) -> None:
        copie = copy.deepcopy(self.registre)
        copie["confrontation"] = copie["confrontation"][:2]
        erreurs = MODULE.valider(copie, self.aujourdhui, self.fiches_urls)
        self.assertTrue(any("au moins 3 exigées" in e for e in erreurs))

    def test_reste_hors_de_la_porte_de_publication(self) -> None:
        deploy_workflow = (RACINE / ".github" / "workflows" / "deploy-pages.yml").read_text(encoding="utf-8")
        self.assertNotIn("confronter-sources.py", deploy_workflow)


if __name__ == "__main__":
    unittest.main()
