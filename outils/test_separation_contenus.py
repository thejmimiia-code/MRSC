#!/usr/bin/env python3
"""Tests de non-réintroduction des chemins de contenus personnels connus."""
import importlib.util
from pathlib import Path
import tempfile
import unittest

spec = importlib.util.spec_from_file_location("separation", Path(__file__).with_name("verifier-separation-contenus.py"))
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class Separation(unittest.TestCase):
    def controle(self, nom, contenu=""):
        with tempfile.TemporaryDirectory() as dossier:
            racine = Path(dossier)
            p = racine / nom
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(contenu)
            return module.erreurs(racine)

    def test_presentation_generale_conservee(self):
        self.assertEqual(self.controle("eva.html", "Présentation générale de recherche en IA"), [])

    def test_image_reintroduite_detectee(self):
        self.assertTrue(self.controle("assets/images/animation/eva-reference.webp"))

    def test_nouvelles_references_detectees(self):
        self.assertTrue(self.controle("assets/images/eva-references/face.png"))

    def test_ancienne_reference_documentaire_detectee(self):
        self.assertTrue(self.controle("docs/rd/statuts-animation/eva-reference.jpg"))

    def test_lien_personnalisation_detecte(self):
        self.assertTrue(self.controle("assets/js/site.js", "link.href = 'animations.html';"))

    def test_route_de_publication_detectee(self):
        self.assertTrue(self.controle(".github/workflows/deploy-pages.yml", "cp animations.html _site/"))

    def test_film_associatif_conserve(self):
        self.assertEqual(self.controle("docs/rd/statuts-animation/amblin-01-annees-80.webp"), [])


if __name__ == "__main__":
    unittest.main()
