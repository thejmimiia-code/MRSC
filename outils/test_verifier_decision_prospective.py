#!/usr/bin/env python3
"""Tests unitaires du comptage de la Boussole prospective."""

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


if __name__ == "__main__":
    unittest.main(verbosity=2)
