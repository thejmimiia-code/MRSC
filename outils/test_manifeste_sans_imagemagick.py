#!/usr/bin/env python3
"""Tests de la vérification du manifeste d'images sans ImageMagick.

La génération des variantes a besoin d'ImageMagick ; la *vérification* du
manifeste, elle, tourne sur un runner qui ne l'installe pas. Elle lisait pourtant
les dimensions par ce binaire : une porte de CI dépendait d'un outil absent, et
échouait donc sans rapport avec les fichiers du dépôt.

Ces tests lisent les dimensions dans l'en-tête des fichiers, vérifient que la
largeur native et les paliers utiles en découlent, et que la vérification
complète rend zéro quand aucun outil externe n'est disponible.
"""

from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
IMAGES = RACINE / "assets" / "images"


def charger_module():
    specification = importlib.util.spec_from_file_location(
        "optimiser_images", RACINE / "outils" / "optimiser-images.py"
    )
    module = importlib.util.module_from_spec(specification)
    specification.loader.exec_module(module)
    return module


MODULE = charger_module()


def faux_png(largeur: int, hauteur: int) -> bytes:
    """En-tête PNG minimal : la lecture s'arrête aux dimensions."""
    return (
        b"\x89PNG\r\n\x1a\n"
        + (13).to_bytes(4, "big")
        + b"IHDR"
        + largeur.to_bytes(4, "big")
        + hauteur.to_bytes(4, "big")
        + b"\x08\x02\x00\x00\x00"
        + b"\x00\x00\x00\x00"
    )


class LectureSansDependance(unittest.TestCase):
    def test_largeurs_natives_lues_dans_l_entete(self):
        attendues = {
            "mondes-savoirs-hero.jpg": (1672, 941),
            "escales-anglais-hero.jpg": (1672, 941),
            "accueil-logo-mrsc-3d.jpg": (1400, 933),
        }
        for nom, dimensions in attendues.items():
            with self.subTest(nom=nom):
                self.assertEqual(
                    MODULE.dimensions_sans_dependance(IMAGES / nom), dimensions
                )

    def test_webp_lu_dans_l_entete(self):
        for nom, largeur in (
            ("mondes-savoirs-hero-800.webp", 800),
            ("escales-anglais-hero-1672.webp", 1672),
        ):
            with self.subTest(nom=nom):
                self.assertEqual(
                    MODULE.dimensions_sans_dependance(IMAGES / nom)[0], largeur
                )

    def test_verification_entiere_sans_imagemagick(self):
        """La porte de CI ne doit dépendre d'aucun binaire d'image."""
        original = MODULE.outil_imagemagick
        MODULE.outil_imagemagick = lambda: None
        try:
            self.assertEqual(MODULE.verifier(), 0)
        finally:
            MODULE.outil_imagemagick = original

    def test_paliers_utiles_ajoutes_quand_la_source_les_permet(self):
        with tempfile.TemporaryDirectory() as dossier:
            large = Path(dossier) / "large.png"
            large.write_bytes(faux_png(3000, 1688))
            self.assertEqual(
                MODULE.largeurs_effectives(large, (800, 1200)), [800, 1200, 2560, 2880, 3000]
            )

    def test_aucune_largeur_plus_grande_que_la_source(self):
        with tempfile.TemporaryDirectory() as dossier:
            petite = Path(dossier) / "petite.png"
            petite.write_bytes(faux_png(1000, 563))
            largeurs = MODULE.largeurs_effectives(petite, (800, 1200, 1672, 2880))
            self.assertEqual(largeurs, [800, 1000])
            self.assertTrue(all(largeur <= 1000 for largeur in largeurs))

    def test_format_inconnu_nomme_le_fichier(self):
        original = MODULE.outil_imagemagick
        MODULE.outil_imagemagick = lambda: None
        try:
            with tempfile.TemporaryDirectory() as dossier:
                opaque = Path(dossier) / "opaque.bin"
                opaque.write_bytes(b"\x00\x01\x02\x03" * 8)
                with self.assertRaises(RuntimeError) as contexte:
                    MODULE.lire_dimensions(opaque)
                self.assertIn("opaque.bin", str(contexte.exception))
        finally:
            MODULE.outil_imagemagick = original


if __name__ == "__main__":
    unittest.main(verbosity=2)
