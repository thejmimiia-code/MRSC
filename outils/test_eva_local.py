#!/usr/bin/env python3
"""Tests CPU/contrats du lanceur : ne valent pas une exécution ML/Windows."""
import hashlib
from contextlib import nullcontext
import importlib.util
import io
from pathlib import Path
import struct
import sys
import tarfile
import tempfile
import types
import unittest
from unittest import mock
import zipfile

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'outils/eva-local'))
import securite
import geometrie
from eva_local import exporter_glb
spec=importlib.util.spec_from_file_location('pack_eva',ROOT/'outils/preparer-eva-local.py')
pack=importlib.util.module_from_spec(spec)
spec.loader.exec_module(pack)


class SourceEtPaquet(unittest.TestCase):
    def archive(self,root,members):
        path=root/'fixture.tar.gz'
        with tarfile.open(path,'w:gz') as tar:
            for name,data,kind in members:
                info=tarfile.TarInfo(name)
                if kind=='link':
                    info.type=tarfile.SYMTYPE
                    info.linkname='../outside'
                    tar.addfile(info)
                else:
                    info.size=len(data)
                    tar.addfile(info,io.BytesIO(data))
        return path,hashlib.sha256(path.read_bytes()).hexdigest()

    def test_extraction_limitee(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            p,h=self.archive(root,[(securite.PREFIX+'/tsr/system.py',b'# code','file'),(securite.PREFIX+'/LICENSE',b'licence','file'),(securite.PREFIX+'/figures/enorme.bin',b'non requis','file')])
            securite.extraire_archive(p,root/'source',h)
            self.assertTrue((root/'source/tsr/system.py').exists())
            self.assertFalse((root/'source/figures').exists())

    def test_refuse_empreinte_traversee_et_lien(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            for name,kind in [('../outside','file'),(securite.PREFIX+'/tsr/../../outside','file'),(securite.PREFIX+'/tsr/link','link')]:
                p,h=self.archive(root,[(name,b'bad',kind)])
                with self.assertRaises(ValueError):
                    securite.extraire_archive(p,root/'source',h)
                self.assertFalse((root/'outside').exists())
            with self.assertRaises(ValueError):
                securite.extraire_archive(p,root/'other','0'*64)

    def test_paquet_reproductible_et_sans_ancien_modele(self):
        with tempfile.TemporaryDirectory() as td:
            a,b=Path(td)/'a.zip',Path(td)/'b.zip'
            self.assertEqual(pack.preparer(a),pack.preparer(b))
            with zipfile.ZipFile(a) as z:
                names=z.namelist()
                self.assertIn('EVA-local/Demarrer.cmd',names)
                self.assertIn('EVA-local/references/eva-face-reference.png',names)
                self.assertFalse(any(n.endswith('.glb') for n in names))
                self.assertFalse(any('model.ckpt' in n for n in names))
                self.assertFalse(any('..' in Path(n).parts for n in names))
        with self.assertRaises(ValueError):
            pack.preparer(ROOT/'livraison.zip')

    def test_pas_de_generateur_hunyuan_installe(self):
        requirements=(ROOT/'outils/eva-local/requirements-local.txt').read_text()
        launcher=(ROOT/'outils/eva-local/Lancer-Eva.ps1').read_text()
        self.assertNotIn('hunyuan',requirements.lower())
        self.assertNotIn('torchmcubes',requirements)
        self.assertIn('-AccepterLicence',launcher)
        self.assertNotIn('Set-ExecutionPolicy',launcher)
        self.assertNotIn('Restart-Computer',launcher)


class GeometrieCPU(unittest.TestCase):
    def test_rasterisation_barycentrique_et_orientation_v(self):
        import numpy as np
        vertices=np.array([[0,0,0],[1,0,0],[0,1,0]],dtype=np.float32)
        uvs=np.array([[0,0],[1,0],[0,1]],dtype=np.float32)
        positions,mask=geometrie.rasteriser_positions(vertices,[[0,1,2]],uvs,16)
        self.assertTrue(mask.any())
        self.assertTrue(mask[14,1])
        np.testing.assert_allclose(positions[14,1],[1.5/16,1.5/16,0],atol=1e-6)
        self.assertFalse(mask[1,14])
        with self.assertRaises(ValueError):
            geometrie.rasteriser_positions(vertices,[[0,1,3]],uvs,16)
        with self.assertRaises(ValueError):
            geometrie.rasteriser_positions(vertices,[[0,1,2]],uvs,4096)

    def test_marge_n_efface_pas_la_surface(self):
        import numpy as np
        colors=np.zeros((8,8,3),dtype=np.uint8)
        mask=np.zeros((8,8),dtype=bool)
        colors[3,3]=[100,50,25]
        mask[3,3]=True
        result=geometrie.marger_texture(colors,mask,1)
        np.testing.assert_array_equal(result[3,3],[100,50,25])
        np.testing.assert_array_equal(result[3,4],[100,50,25])
        np.testing.assert_array_equal(result[0,0],[0,0,0])

    def test_axes_marching_cubes_pas_de_miroir(self):
        import numpy as np
        class Tensor:
            def __init__(self,data): self.data=data
            def detach(self): return self
            def float(self): return self
            def cpu(self): return self
            def numpy(self): return self.data
        fake=types.ModuleType('torch')
        fake.from_numpy=lambda x:x
        field=3.25-np.indices((8,9,10),dtype=np.float32)[0]
        with mock.patch.dict(sys.modules,{'torch':fake}):
            geometrie.installer_marching_cubes_cpu()
            v,f=sys.modules['torchmcubes'].marching_cubes(Tensor(field),0)
            # Inversion de TripoSR après celle de l'adaptateur.
            v=v[:,[2,1,0]]
            np.testing.assert_allclose(v[:,0],3.25)
            self.assertEqual((v[:,1].max(),v[:,2].max()),(8,9))
            self.assertGreater(len(f),0)

    def test_cuisson_uv_cpu_avec_champ_neural_simule(self):
        import numpy as np
        import trimesh
        class Array:
            def __init__(self,a): self.a=a
            def detach(self): return self
            def float(self): return self
            def cpu(self): return self
            def numpy(self): return self.a
        class Renderer:
            def query_triplane(self,decoder,points,scene):
                return {'color':Array(np.clip((points+1)/2,0,1))}
        fake=types.ModuleType('torch')
        fake.as_tensor=lambda a,device=None:np.asarray(a)
        fake.inference_mode=nullcontext
        mesh=trimesh.creation.icosphere(subdivisions=1,radius=.3)
        model=types.SimpleNamespace(renderer=Renderer(),decoder=None)
        with mock.patch.dict(sys.modules,{'torch':fake}):
            textured,image=geometrie.cuire_texture(mesh,model,types.SimpleNamespace(device='cpu'),64,64)
        self.assertEqual(image.size,(64,64))
        self.assertEqual(len(textured.faces),len(mesh.faces))
        self.assertGreater(np.asarray(image).max(),100)
        self.assertIsNotNone(textured.visual.material.baseColorTexture)
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/'texture.glb'
            exporter_glb(geometrie.normaliser_metres(textured),p)
            scene=trimesh.load(p,force='scene')
            self.assertEqual(next(iter(scene.geometry.values())).visual.material.baseColorTexture.size,(64,64))

    def test_metres_et_glb_effectivement_recharge(self):
        import numpy as np
        import trimesh
        mesh=trimesh.creation.box(extents=[.4,.3,2])
        result=geometrie.normaliser_metres(mesh)
        np.testing.assert_allclose(result.bounds[:,1],[0,1.8],atol=1e-7)
        self.assertGreater(result.volume,0)
        with tempfile.TemporaryDirectory() as td:
            path=Path(td)/'essai.glb'
            exporter_glb(result,path)
            data=path.read_bytes()
            self.assertEqual(struct.unpack_from('<III',data),(0x46546C67,2,len(data)))
            self.assertFalse(path.with_suffix('.part').exists())


if __name__=='__main__':
    unittest.main()
