#!/usr/bin/env python3
"""Vérifie le refus d'une référence CSS périmée, sans modifier le dépôt."""
import importlib.util
from pathlib import Path
import tempfile
import unittest

spec = importlib.util.spec_from_file_location('version_css_ia', Path(__file__).with_name('versionner-css-ia.py'))
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class VersionCssIA(unittest.TestCase):
    def test_reference_et_modification(self):
        with tempfile.TemporaryDirectory() as dossier:
            root = Path(dossier)
            (root / 'assets/css').mkdir(parents=True)
            css = root / 'assets/css/site.css'
            css.write_text('body { color: navy; }')
            page = root / 'ia-societe.html'
            page.write_text('<link rel="stylesheet" href="assets/css/site.css">')
            with self.assertRaises(ValueError):
                module.versionner(root, verifier=True)
            premiere = module.versionner(root)
            self.assertEqual(module.versionner(root, verifier=True), premiere)
            avant = page.read_bytes()
            module.versionner(root)
            self.assertEqual(page.read_bytes(), avant)
            css.write_text('body { color: black; }')
            with self.assertRaises(ValueError):
                module.versionner(root, verifier=True)
            self.assertNotEqual(module.versionner(root), premiere)
            module.versionner(root, verifier=True)

    def test_reference_absente(self):
        with tempfile.TemporaryDirectory() as dossier:
            root = Path(dossier)
            (root / 'assets/css').mkdir(parents=True)
            (root / 'assets/css/site.css').write_text('')
            (root / 'ia-societe.html').write_text('<html></html>')
            with self.assertRaises(ValueError):
                module.versionner(root)


if __name__ == '__main__':
    unittest.main()
