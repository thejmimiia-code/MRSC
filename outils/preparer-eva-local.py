#!/usr/bin/env python3
"""Prépare un paquet Windows ; ne lance aucun calcul sur le PC de l'utilisateur."""
import argparse
import hashlib
import json
from pathlib import Path
import zipfile

ROOT=Path(__file__).resolve().parents[1]
FILES=['Natif.ps1','Demarrer.cmd','Lancer-Eva.ps1','LISEZ-MOI.md','requirements-local.txt','eva_local.py','geometrie.py','securite.py']


def preparer(destination):
    destination=Path(destination).resolve()
    if ROOT==destination or ROOT in destination.parents:
        raise ValueError('Le ZIP de livraison doit rester hors du dépôt Git.')
    sources={name:ROOT/'outils/eva-local'/name for name in FILES}
    sources['references/eva-face-reference.png']=ROOT/'assets/images/eva-references/eva-face-reference.png'
    contents={name:p.read_bytes() for name,p in sources.items()}
    contents['LISEZ-MOI.txt']=contents['LISEZ-MOI.md']
    manifest={'statut':'Essai local non exécuté par ce paquet ; reconstruction attendue non riggée, pas personnage finalisé.','fichiers':{name:hashlib.sha256(data).hexdigest() for name,data in contents.items()}}
    contents['manifest-paquet.json']=(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n').encode('utf-8')
    destination.parent.mkdir(parents=True,exist_ok=True)
    with zipfile.ZipFile(destination,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
        for name,data in sorted(contents.items()):
            info=zipfile.ZipInfo('EVA-local/'+name,date_time=(1980,1,1,0,0,0))
            info.compress_type=zipfile.ZIP_DEFLATED
            info.external_attr=0o100644<<16
            z.writestr(info,data)
    return hashlib.sha256(destination.read_bytes()).hexdigest()


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--sortie',type=Path,required=True)
    args=parser.parse_args()
    print(args.sortie,preparer(args.sortie))
