#!/usr/bin/env python3
"""Intégrité des références IA, pas validation de cohérence multivue."""
import hashlib
import json
from pathlib import Path
import struct
import unittest

ROOT=Path(__file__).resolve().parents[1]
META=json.loads((ROOT/'docs/rd/eva-references-2026-10-24.json').read_text())

class ReferencesEva(unittest.TestCase):
    def test_integrite_et_dimensions(self):
        self.assertEqual(len(META['images']),3)
        for row in META['images']:
            with self.subTest(fichier=row['fichier']):
                data=(ROOT/row['fichier']).read_bytes()
                self.assertEqual(data[:8],b'\x89PNG\r\n\x1a\n')
                self.assertEqual(struct.unpack_from('>II',data,16),(848,1264))
                self.assertEqual((row['largeur'],row['hauteur']),(848,1264))
                self.assertEqual(hashlib.sha256(data).hexdigest(),row['sha256'])
                self.assertEqual(len(data),row['octets'])

    def test_apercus_legers_et_originaux_separes(self):
        total=0
        page=(ROOT/'animations.html').read_text()
        for row in META['images']:
            data=(ROOT/row['apercu']).read_bytes()
            self.assertEqual(data[:4],b'RIFF')
            self.assertEqual(data[8:12],b'WEBP')
            self.assertEqual(len(data),row['octets_apercu'])
            total+=len(data)
            self.assertIn(f'src="{row["apercu"]}"',page)
            self.assertIn(f'href="{row["fichier"]}"',page)
            self.assertNotIn(f'src="{row["fichier"]}"',page)
        self.assertLess(total,200*1024)
        self.assertIn('pas vues calibrées',META['statut'])

if __name__=='__main__':
    unittest.main()
