#!/usr/bin/env python3
"""Vérifie les résultats numériques écrits dans les deux fiches du lot.

Pas de validation pédagogique : ces tests couvrent des passages identifiés,
ni tout le langage naturel des fiches ni une compréhension humaine.
"""
from fractions import Fraction
from pathlib import Path
import statistics
import tomllib
import unittest

ROOT = Path(__file__).resolve().parent.parent
FICHES = {f['id']: f for f in tomllib.loads((ROOT / 'docs/apprentissage/catalogue.toml').read_text())['fiche']}


def milieu(valeurs):
    valeurs = sorted(valeurs)
    n = len(valeurs)
    if not n:
        raise ValueError('Série vide')
    return Fraction(valeurs[n // 2]) if n % 2 else Fraction(valeurs[n // 2 - 1] + valeurs[n // 2], 2)


class ExemplesStatistiques(unittest.TestCase):
    def test_exemple_explique(self):
        fiche = FICHES['maths-moyenne-mediane']
        valeurs = [20, 4, 2, 5, 4]
        self.assertIn('20, 4, 2, 5, 4', fiche['situation'])
        texte = ' '.join(fiche['demarche'])
        self.assertIn(f'= 35 ÷ 5 = {statistics.mean(valeurs)} minutes de moyenne', texte)
        self.assertIn(f'La médiane vaut {milieu(valeurs)} minutes', texte)
        self.assertIn(f'(4 + 8) ÷ 2 = {milieu([2,4,8,14])} minutes', texte)

    def test_corrections_a_b_c(self):
        fiche = FICHES['maths-moyenne-mediane']
        self.assertIn('9, 3, 5, 1, 2', fiche['exercice'])
        self.assertIn('9 par 29', fiche['exercice'])
        self.assertIn('1, 2, 8, 15', fiche['exercice'])
        for valeurs, correction in zip(([1,2,3,5,9], [1,2,3,5,29]), fiche['correction'][:2]):
            self.assertIn(f'moyenne {statistics.mean(valeurs)} minutes', correction)
            self.assertIn(f'{milieu(valeurs)} minutes', correction)
        self.assertIn(f'médiane {milieu([1,2,8,15])} minutes', fiche['correction'][2])
        self.assertEqual(milieu([1,2,8,15]), statistics.median([1,2,8,15]))

    def test_zero_et_absence(self):
        fiche = FICHES['maths-moyenne']
        texte = ' '.join(fiche['correction'])
        for valeurs in ([3,6,9], [0,4,8], [4,8]):
            self.assertIn(f'moyenne {statistics.mean(valeurs)} points' if valeurs != [3,6,9] else 'moyenne est de 6 points', texte)
        self.assertIn('La moyenne des 3 manches reste inconnue', texte)
        self.assertIn('0, 4, 8', fiche['exercice'])
        self.assertIn('une valeur manquante, 4, 8', fiche['exercice'])
        self.assertNotEqual(statistics.mean([0,4,8]), statistics.mean([4,8]))

    def test_doublons_et_limites(self):
        valeurs = [2,4,4,5,20]
        m = milieu(valeurs)
        self.assertGreaterEqual(sum(v <= m for v in valeurs), len(valeurs)/2)
        self.assertGreaterEqual(sum(v >= m for v in valeurs), len(valeurs)/2)
        self.assertLess(sum(v < m for v in valeurs), len(valeurs)/2)
        self.assertEqual(milieu(valeurs), milieu(list(reversed(valeurs))))
        self.assertEqual(milieu([v+7 for v in valeurs]), m+7)
        with self.assertRaises(ValueError):
            milieu([])

    def test_mutations_des_reponses(self):
        # Une faute dans le contenu doit être détectée, pas seulement un
        # calcul recopié dans ce test. Mutations en mémoire, puis restauration.
        fiche = FICHES['maths-moyenne-mediane']
        original = fiche['correction'][:]
        try:
            fiche['correction'][0] = original[0].replace('moyenne 4 minutes', 'moyenne 5 minutes')
            with self.assertRaises(AssertionError):
                self.test_corrections_a_b_c()
            fiche['correction'] = original[:]
            fiche['correction'][2] = original[2].replace('médiane 5 minutes', 'médiane 8 minutes')
            with self.assertRaises(AssertionError):
                self.test_corrections_a_b_c()
        finally:
            fiche['correction'] = original

    def test_statut_non_valide(self):
        for id in ['maths-moyenne', 'maths-moyenne-mediane']:
            self.assertEqual(FICHES[id]['statut_editorial'], 'Prototype à relire')


if __name__ == '__main__':
    unittest.main()
