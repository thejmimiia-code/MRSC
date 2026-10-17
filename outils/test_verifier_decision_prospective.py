#!/usr/bin/env python3
"""Tests unitaires du comptage de la Boussole prospective."""

import datetime as dt
import importlib.util
import unittest
from pathlib import Path

MODULE_PATH = Path(__file__).with_name("verifier-decision-prospective.py")
SPEC = importlib.util.spec_from_file_location("verifier_decision_prospective", MODULE_PATH)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class CompterQuestionsBoussoleTests(unittest.TestCase):
    def test_compte_uniquement_les_elements_de_la_liste(self):
        html = '''
        <section id="boussole-savoirs">
          <ol class="knowledge-compass"><li>Une</li><li>Deux</li></ol>
          <ul><li>Hors boussole</li></ul>
        </section>
        '''
        self.assertEqual(MODULE.compter_questions_boussole(html), 2)

    def test_refuse_une_section_absente(self):
        with self.assertRaisesRegex(ValueError, "section"):
            MODULE.compter_questions_boussole("<main></main>")

    def test_refuse_une_liste_absente(self):
        with self.assertRaisesRegex(ValueError, "knowledge-compass"):
            MODULE.compter_questions_boussole('<section id="boussole-savoirs"></section>')

    def test_lit_la_date_du_brief_et_du_tableau(self):
        texte = "**Date : 17 octobre 2026. Statut : brouillon.**\n| Fait | Valeur au 17 octobre 2026 |"
        self.assertEqual(MODULE.date_du_brief(texte), dt.date(2026, 10, 17))

    def test_refuse_deux_dates_differentes(self):
        texte = "**Date : 17 octobre 2026. Statut : brouillon.**\n| Fait | Valeur au 18 octobre 2026 |"
        with self.assertRaisesRegex(ValueError, "différente"):
            MODULE.date_du_brief(texte)

    def test_refuse_un_mois_inconnu(self):
        texte = "**Date : 17 octembre 2026.**\n| Valeur au 17 octembre 2026 |"
        with self.assertRaisesRegex(ValueError, "date française"):
            MODULE.date_du_brief(texte)

    def test_arrondit_les_poids_affiches(self):
        tableau = "| `apprendre.html` | 158.8 | 308.6 | 619.5 |"
        self.assertEqual(MODULE.poids_page(tableau, "apprendre.html"), (159, 309))

    def test_calcule_la_revue_depuis_les_metadonnees(self):
        meta = {"derniere_revue": dt.date(2026, 10, 13), "cadence_revue_jours": 30}
        self.assertEqual(MODULE.date_prochaine_revue(meta), dt.date(2026, 11, 12))

    def test_refuse_des_metadonnees_de_revue_incompletes(self):
        with self.assertRaisesRegex(ValueError, "métadonnées"):
            MODULE.date_prochaine_revue({"derniere_revue": dt.date(2026, 10, 13)})


if __name__ == "__main__":
    unittest.main(verbosity=2)
