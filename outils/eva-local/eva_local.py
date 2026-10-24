#!/usr/bin/env python3
"""Exécution locale sur le PC Windows de l'utilisateur, pas dans le sandbox.

Produit une reconstruction texturée NON RIGGÉE pour examen, jamais une EVA
finalisée déclarée automatiquement. Aucun envoi des images à un service 3D.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import sys
import uuid

from securite import COMMIT, empreinte, preparer_source


def diagnostic():
    import torch
    if not torch.cuda.is_available():
        raise RuntimeError('CUDA indisponible. Vérifiez le pilote NVIDIA Windows et le PyTorch CUDA du venv ; aucun repli CPU silencieux.')
    props = torch.cuda.get_device_properties(0)
    total = props.total_memory/(1024**3)
    free,_ = torch.cuda.mem_get_info(0)
    if props.major < 7:
        raise RuntimeError('Ce profil vise un GPU NVIDIA Turing ou ultérieur.')
    if total < 7.5:
        raise RuntimeError('Ce profil vise environ 8 Gio de VRAM ; arrêt avant téléchargement des poids.')
    if free < 6*1024**3:
        raise RuntimeError('Moins de 6 Gio de VRAM libre. Fermez les logiciels GPU, puis relancez ; aucun processus n’est arrêté automatiquement.')
    # Ne collecter ni nom de machine, identifiant de produit ou UUID matériel.
    info = {'gpu':props.name,'vram_gio':round(total,2),'vram_libre_gio':round(free/(1024**3),2),'torch':torch.__version__,'cuda_runtime':torch.version.cuda}
    print(json.dumps(info,ensure_ascii=False,indent=2),flush=True)
    return info


def sauvegarder_json(path, obj):
    path = Path(path)
    temp = path.with_suffix('.tmp')
    temp.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    temp.replace(path)


def preparer_image(path, cache, sortie):
    import numpy as np
    import rembg
    from PIL import Image
    os.environ['U2NET_HOME'] = str(cache/'segmentation')
    print('Détourage local CPU (premier téléchargement du modèle U2Net si nécessaire).',flush=True)
    session = rembg.new_session('u2net',providers=['CPUExecutionProvider'])
    image = Image.open(path)
    image.load()
    if image.width*image.height > 30_000_000:
        raise ValueError('Image trop grande pour ce profil.')
    rgba = rembg.remove(image.convert('RGB'),session=session).convert('RGBA')
    alpha = np.asarray(rgba)[:,:,3]
    yy,xx = np.where(alpha>8)
    if len(xx)<100:
        raise ValueError('Détourage vide. Aucune génération lancée.')
    crop = rgba.crop((int(xx.min()),int(yy.min()),int(xx.max()+1),int(yy.max()+1)))
    size = int(max(crop.size)/.85)
    square = Image.new('RGBA',(size,size),(128,128,128,255))
    square.alpha_composite(crop,((size-crop.width)//2,(size-crop.height)//2))
    square = square.convert('RGB')
    square.save(sortie/'entree-detouree.png')
    return square


def exporter_glb(mesh, path):
    import numpy as np
    import trimesh
    if not len(mesh.vertices) or not len(mesh.faces) or not np.isfinite(mesh.vertices).all():
        raise ValueError('Maillage vide ou non fini.')
    tmp = path.with_suffix('.part')
    try:
        mesh.export(str(tmp),file_type='glb')
        data = tmp.read_bytes()
        if data[:4] != b'glTF' or len(data)<100:
            raise ValueError('Export GLB invalide.')
        # Rechargement effectif avant de publier le fichier dans les résultats.
        check = trimesh.load(str(tmp),file_type='glb',force='scene')
        if not check.geometry:
            raise ValueError('GLB exporté sans géométrie.')
        tmp.replace(path)
    finally:
        tmp.unlink(missing_ok=True)


def generer(args):
    import numpy as np
    import torch
    from huggingface_hub import HfApi, snapshot_download
    from geometrie import installer_marching_cubes_cpu, cuire_texture, normaliser_metres

    image_path = args.image.resolve(strict=True)
    if image_path.suffix.lower() not in ('.png','.jpg','.jpeg','.webp'):
        raise ValueError('Format image non pris en charge.')
    cache = args.cache.resolve()
    cache.mkdir(parents=True,exist_ok=True)
    sortie = args.sortie.resolve()/('run-'+datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')+'-'+uuid.uuid4().hex[:6])
    sortie.mkdir(parents=True,exist_ok=False)
    rapport = {'outils_sha256':{name:empreinte(Path(__file__).parent/name) for name in ['eva_local.py','geometrie.py','securite.py']},'options':{'resolution_surface':args.resolution,'texture_pixels':args.texture,'chunk_size':2048},'statut':'en_cours','source_commit':COMMIT,'reference_sha256':empreinte(image_path),'limitations':['Reconstruction mono-image, dos et détails inférés','Aucun squelette ni animation généré','Pas de validation de ressemblance ou de finition artistique'],'etapes':[]}
    report_path = sortie/'rapport.json'
    sauvegarder_json(report_path,rapport)
    try:
        rapport['configuration'] = diagnostic()
        source = preparer_source(cache)
        installer_marching_cubes_cpu()
        sys.path.insert(0,str(source))
        from tsr.system import TSR
        rapport['etapes'].append('sources_verifiees_et_extraction_cpu_preparee')
        image = preparer_image(image_path,cache,sortie)
        # Résoudre une révision une fois, puis télécharger à cette révision.
        # Pas de prétendue empreinte de poids que nous n'avons pas récupérés ici.
        model_sha = HfApi().model_info('stabilityai/TripoSR').sha
        rapport['revision_poids_huggingface'] = model_sha
        sauvegarder_json(report_path,rapport)
        print('Téléchargement/cache des poids officiels TripoSR ; cela peut représenter plusieurs Go.',flush=True)
        model_path = snapshot_download('stabilityai/TripoSR',revision=model_sha,allow_patterns=['config.yaml','model.ckpt'],cache_dir=str(cache/'poids'))
        rapport['poids_sha256'] = empreinte(Path(model_path)/'model.ckpt')
        model = TSR.from_pretrained(model_path,config_name='config.yaml',weight_name='model.ckpt')
        model.eval()
        model.renderer.set_chunk_size(2048)
        model.to('cuda:0')
        print('Reconstruction neurale GPU ; aucune durée ni fidélité garanties.',flush=True)
        with torch.inference_mode():
            scene_codes = model([image],device='cuda:0')
            meshes = model.extract_mesh(scene_codes,has_vertex_color=True,resolution=args.resolution)
        mesh = meshes[0]
        if not len(mesh.faces) or not np.isfinite(mesh.vertices).all():
            raise ValueError('Le moteur n’a pas produit un maillage exploitable.')
        if mesh.is_watertight and mesh.volume<0:
            mesh.invert()
        raw_path = sortie/'eva-geometrie-couleurs-non-riggee.glb'
        exporter_glb(normaliser_metres(mesh),raw_path)
        rapport['etapes'].append('geometrie_generee_et_glb_recharge')
        rapport['geometrie'] = {'fichier':raw_path.name,'sha256':empreinte(raw_path),'sommets':len(mesh.vertices),'triangles':len(mesh.faces)}
        sauvegarder_json(report_path,rapport)
        print('Géométrie sauvegardée. Cuisson de texture UV locale, sans OpenGL ni toolkit CUDA.',flush=True)
        textured,texture = cuire_texture(mesh,model,scene_codes[0],args.texture,chunk_size=2048)
        texture.save(sortie/'texture-neurale.png')
        textured_path = sortie/'eva-reconstruction-texturee-non-riggee.glb'
        exporter_glb(normaliser_metres(textured),textured_path)
        rapport['etapes'].append('texture_cuite_et_glb_recharge')
        rapport['resultat'] = {'fichier':textured_path.name,'sha256':empreinte(textured_path),'texture_pixels':args.texture,'rig':False,'animations':False,'validation_artistique':False}
        rapport['statut'] = 'reconstruction_a_examiner_non_riggee'
        sauvegarder_json(report_path,rapport)
        print(f'Résultats : {sortie}',flush=True)
        print('Reconstruction exportée, NON RIGGÉE. À examiner avant retopologie, rig et finition. Ce n’est pas une EVA finalisée.',flush=True)
    except Exception as exc:
        rapport['statut'] = 'echec_ou_resultat_partiel'
        rapport['erreur'] = f'{type(exc).__name__}: {exc}'
        sauvegarder_json(report_path,rapport)
        print(f'Échec consigné dans {report_path}. Les étapes déjà réussies sont conservées.',file=sys.stderr,flush=True)
        raise


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--diagnostic',action='store_true')
    mode.add_argument('--generer',action='store_true')
    parser.add_argument('--accepter-licence',action='store_true')
    parser.add_argument('--image',type=Path)
    parser.add_argument('--cache',type=Path,required=True)
    parser.add_argument('--sortie',type=Path)
    parser.add_argument('--resolution',type=int,choices=[128,192,256],default=256)
    parser.add_argument('--texture',type=int,choices=[512,1024,2048],default=2048)
    args = parser.parse_args()
    os.environ['HF_HUB_DISABLE_TELEMETRY']='1'
    os.environ['DO_NOT_TRACK']='1'
    if args.diagnostic:
        diagnostic()
        return
    if not args.accepter_licence or not args.image or not args.sortie:
        parser.error('--generer requiert --accepter-licence, --image et --sortie. Lisez les licences et le guide.')
    generer(args)


if __name__=='__main__':
    try:
        main()
    except Exception as exc:
        print(f'ARRÊT — {type(exc).__name__}: {exc}',file=sys.stderr)
        raise SystemExit(1)
