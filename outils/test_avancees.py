#!/usr/bin/env python3
"""Tests du registre des avancées réutilisables.

Un registre qui accepte n'importe quoi est une brochure. Ces tests vérifient que
chaque exigence mord : preuve absente, limite trop courte, initiative inconnue,
date future, identifiant dupliqué. Et que le document publié ne prétend jamais
certifier une avancée.
"""

from __future__ import annotations

import copy
import importlib.util
import sys
import tempfile
import unittest
from datetime import date
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent


def charger_module():
    specification = importlib.util.spec_from_file_location("avancees", RACINE / "outils" / "construire-avancees.py")
    module = importlib.util.module_from_spec(specification)
    specification.loader.exec_module(module)
    return module


MODULE = charger_module()
AUJOURDHUI = date(2026, 10, 20)


def base() -> dict:
    return {
        "meta": {"version": 1, "derniere_revue": date(2026, 10, 20), "regle": "preuve et limite exigées"},
        "avancee": [
            {
                "id": "avancee-de-test",
                "date": date(2026, 10, 20),
                "titre": "Une avancée de démonstration",
                "constat": "Un fait constaté pendant un lot de travail.",
                "changement": "Ce que le projet fait désormais autrement.",
                "preuves": ["outils/construire-avancees.py", "docs/rd/avancees.toml"],
                "controle": "python3 outils/construire-avancees.py --verifier",
                "limite": (
                    "Ce constat ne prouve pas que le résultat est de qualité : il décrit seulement une manière de "
                    "travailler devenue vérifiable, et une personne doit encore trancher ce que la machine ne voit pas."
                ),
                "suite": "Éprouver la même discipline sur le lot suivant.",
                "initiatives": ["relire-les-44-prototypes"],
            }
        ],
    }


def erreurs(registre: dict) -> list[str]:
    return MODULE.valider(registre, AUJOURDHUI, connues={"relire-les-44-prototypes"})


class LeRegistreMord(unittest.TestCase):
    def test_registre_valide_accepte(self):
        self.assertEqual(erreurs(base()), [])

    def test_preuve_absente_refusee(self):
        registre = base()
        registre["avancee"][0]["preuves"] = ["outils/inexistant.py", "docs/rd/avancees.toml"]
        self.assertTrue(any("preuves absentes" in erreur for erreur in erreurs(registre)))

    def test_une_seule_preuve_refusee(self):
        registre = base()
        registre["avancee"][0]["preuves"] = ["docs/rd/avancees.toml"]
        self.assertTrue(any("deux preuves" in erreur for erreur in erreurs(registre)))

    def test_limite_trop_courte_refusee(self):
        registre = base()
        registre["avancee"][0]["limite"] = "Cela ne prouve rien."
        self.assertTrue(any("limite trop courte" in erreur for erreur in erreurs(registre)))

    def test_initiative_inconnue_refusee(self):
        registre = base()
        registre["avancee"][0]["initiatives"] = ["initiative-fantome"]
        self.assertTrue(any("portefeuille" in erreur for erreur in erreurs(registre)))

    def test_date_future_refusee(self):
        registre = base()
        registre["avancee"][0]["date"] = date(2027, 1, 1)
        self.assertTrue(any("futur" in erreur for erreur in erreurs(registre)))

    def test_identifiant_duplique_refuse(self):
        registre = base()
        registre["avancee"].append(copy.deepcopy(registre["avancee"][0]))
        self.assertTrue(any("dupliqué" in erreur for erreur in erreurs(registre)))

    def test_identifiant_non_slug_refuse(self):
        registre = base()
        registre["avancee"][0]["id"] = "Avancee_Test!"
        self.assertTrue(any("slug" in erreur for erreur in erreurs(registre)))

    def test_controle_sans_outil_refuse(self):
        registre = base()
        registre["avancee"][0]["controle"] = "on regarde à l'œil"
        self.assertTrue(any("contrôle" in erreur for erreur in erreurs(registre)))

    def test_champ_manquant_refuse(self):
        registre = base()
        del registre["avancee"][0]["suite"]
        self.assertTrue(any("champs manquants" in erreur for erreur in erreurs(registre)))


class LeDocumentNeCertifieRien(unittest.TestCase):
    def test_le_document_ne_pretend_jamais_certifier(self):
        contenu = MODULE.construire(base(), AUJOURDHUI).casefold()
        for terme in ("validée", "approuvée", "certifiée", "garantie de qualité"):
            self.assertNotIn(terme, contenu)
        self.assertIn("ce que ce registre ne dit pas", contenu)

    def test_le_registre_reel_du_depot_est_traçable(self):
        registre = MODULE.charger()
        self.assertEqual(MODULE.valider(registre, date.today()), [])
        contenu = MODULE.construire(registre, date.today())
        self.assertIn("ne certifie rien", contenu)
        self.assertIn("## 2. Les avancées", contenu)

    def test_fichier_du_depot_synchronise(self):
        registre = MODULE.charger()
        attendu = MODULE.construire(registre, date.today())
        actuel = (RACINE / "docs" / "rd" / "avancees.md").read_text(encoding="utf-8")
        self.assertEqual(actuel, attendu, "régénérer avec python3 outils/construire-avancees.py")

    def test_sortie_hors_depot(self):
        with tempfile.TemporaryDirectory() as dossier:
            cible = Path(dossier) / "avancees.md"
            registre = MODULE.charger()
            cible.write_text(MODULE.construire(registre, date.today()), encoding="utf-8")
            self.assertTrue(cible.is_file())


if __name__ == "__main__":
    unittest.main()
