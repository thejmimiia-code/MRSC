#!/usr/bin/env python3
"""Contrats structurels du GLB original : pas une validation artistique."""
import json
import hashlib
import math
from pathlib import Path
import struct
import unittest

ROOT = Path(__file__).resolve().parents[1]
BLOB = (ROOT / 'assets/models/eva/eva-etude-01.glb').read_bytes()
LENGTH, KIND = struct.unpack_from('<II', BLOB, 12)
DOC = json.loads(BLOB[20:20+LENGTH])
BIN_OFFSET = 20+LENGTH+8
DATA = BLOB[BIN_OFFSET:]


def values(index):
    a = DOC['accessors'][index]
    v = DOC['bufferViews'][a['bufferView']]
    fmt = {5126:'f', 5123:'H', 5125:'I', 5121:'B'}[a['componentType']]
    n = {'SCALAR':1,'VEC2':2,'VEC3':3,'VEC4':4,'MAT4':16}[a['type']]
    step = v.get('byteStride', struct.calcsize('<'+fmt*n))
    start = v.get('byteOffset',0)+a.get('byteOffset',0)
    return [struct.unpack_from('<'+fmt*n, DATA, start+i*step) for i in range(a['count'])]


class ModeleEva(unittest.TestCase):
    def test_conteneur_autonome(self):
        self.assertEqual(struct.unpack_from('<III',BLOB), (0x46546C67,2,len(BLOB)))
        self.assertEqual(KIND,0x4E4F534A)
        self.assertEqual(struct.unpack_from('<I',BLOB,20+LENGTH+4)[0],0x004E4942)
        self.assertLess(len(BLOB),4*1024*1024)
        rapport = json.loads((ROOT / 'docs/rd/validation-eva-glb-2026-10-24.json').read_text())
        self.assertEqual(rapport['sha256'], hashlib.sha256(BLOB).hexdigest())
        self.assertEqual(rapport['octets'], len(BLOB))
        self.assertEqual(rapport['issues']['numErrors'], 0)
        self.assertEqual(rapport['issues']['numWarnings'], 0)
        self.assertFalse(any('uri' in x for x in DOC['buffers']+DOC['images']))

    def test_squelette_et_clips(self):
        names={n.get('name') for n in DOC['nodes']}
        for name in ['Hips','Spine','Chest','Neck','Head','LeftArm','RightForeArm','LeftLeg','RightFoot','LeftFinger0']:
            self.assertIn(name,names)
        self.assertEqual(len(DOC['skins'][0]['joints']),41)
        self.assertEqual({a['name'] for a in DOC['animations']},{'Respiration','Salut','Marche_sur_place'})
        for a in DOC['animations']:
            self.assertTrue(a['channels'])
            for s in a['samplers']:
                times=[v[0] for v in values(s['input'])]
                self.assertEqual(times,sorted(set(times)))
                self.assertGreater(times[-1],0)
                for q in values(s['output']):
                    self.assertAlmostEqual(sum(v*v for v in q),1,places=5)

    def test_maillages_et_poids(self):
        triangles=0
        for m in DOC['meshes']:
            for p in m['primitives']:
                a=p['attributes']
                self.assertIn('JOINTS_0',a)
                self.assertIn('WEIGHTS_0',a)
                positions=values(a['POSITION'])
                for pos in positions:
                    self.assertTrue(all(math.isfinite(x) and abs(x)<3 for x in pos))
                for w in values(a['WEIGHTS_0']):
                    self.assertTrue(all(0<=v<=1 for v in w))
                    self.assertAlmostEqual(sum(w),1,places=5)
                for joint in values(a['JOINTS_0']):
                    self.assertTrue(all(0<=j<41 for j in joint))
                indices=values(p['indices'])
                self.assertTrue(all(0<=i[0]<len(positions) for i in indices))
                triangles+=len(indices)//3
        self.assertLessEqual(len(DOC['meshes']),16)
        self.assertLess(triangles,65000)
        self.assertGreater(triangles,1000)

    def test_textures_originales_embarquees(self):
        self.assertEqual(len(DOC['images']),3)
        for image in DOC['images']:
            self.assertEqual(image['mimeType'],'image/png')
            v=DOC['bufferViews'][image['bufferView']]
            start=v.get('byteOffset',0)
            self.assertEqual(DATA[start:start+8],b'\x89PNG\r\n\x1a\n')
            self.assertEqual(struct.unpack_from('>II',DATA,start+16),(512,512))
        names={m.get('name') for m in DOC['materials']}
        self.assertTrue({'Peau_satin','Tshirt_anthracite','Jean_indigo','Cheveux_chataigne','Cuivre'}<=names)


if __name__=='__main__':
    unittest.main()
