"""Téléchargement et extraction limités au code TripoSR épinglé, sans exécution."""
from pathlib import Path, PurePosixPath
import hashlib
import json
import shutil
import tarfile
import tempfile
import urllib.request

COMMIT = '107cefdc244c39106fa830359024f6a2f1c78871'
SOURCE_URL = f'https://codeload.github.com/VAST-AI-Research/TripoSR/tar.gz/{COMMIT}'
ARCHIVE_SHA256 = 'bcb414550dcfcb9f5ea6a7b9c12f2bbff889f5b4a564a493178393360d9034ec'
PREFIX = f'TripoSR-{COMMIT}'


def empreinte(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for data in iter(lambda: f.read(1024*1024), b''):
            h.update(data)
    return h.hexdigest()


def extraire_archive(archive, destination, attendu=ARCHIVE_SHA256):
    """N'extrait que tsr/, README et licence, sans lien ou traversée de chemin."""
    if empreinte(archive) != attendu:
        raise ValueError('Empreinte de source incorrecte : aucune extraction.')
    destination = Path(destination)
    destination.mkdir(parents=True, exist_ok=True)
    total = 0
    with tarfile.open(archive, 'r:gz') as tar:
        for member in tar:
            name = PurePosixPath(member.name)
            if name.is_absolute() or '..' in name.parts or '\\' in member.name:
                raise ValueError('Chemin non sûr dans l’archive.')
            if member.issym() or member.islnk() or member.isdev():
                raise ValueError('Lien ou fichier spécial interdit dans l’archive.')
            if not name.parts or name.parts[0] != PREFIX:
                raise ValueError('Racine source inattendue.')
            parts = name.parts[1:]
            if not parts or not (parts[0] == 'tsr' or parts == ('LICENSE',) or parts == ('README.md',)):
                continue
            out = destination.joinpath(*parts)
            if member.isdir():
                out.mkdir(parents=True, exist_ok=True)
                continue
            if not member.isfile() or member.size > 5*1024*1024:
                raise ValueError('Fichier source inattendu ou trop volumineux.')
            total += member.size
            if total > 64*1024*1024:
                raise ValueError('Sources trop volumineuses.')
            out.parent.mkdir(parents=True, exist_ok=True)
            source = tar.extractfile(member)
            if source is None:
                raise ValueError('Contenu source absent.')
            with source, out.open('wb') as target:
                shutil.copyfileobj(source, target)
    if not (destination/'tsr/system.py').is_file() or not (destination/'LICENSE').is_file():
        raise ValueError('Sources essentielles absentes.')


def preparer_source(cache):
    cache = Path(cache)
    cache.mkdir(parents=True, exist_ok=True)
    destination = cache/f'TripoSR-{COMMIT}'
    if destination.exists():
        marker = destination/'mrsc-source.json'
        if not marker.is_file():
            raise ValueError('Cache source incomplet. Conservez-le pour examen et utilisez un autre dossier de travail.')
        metadata = json.loads(marker.read_text(encoding='utf-8'))
        if metadata.get('commit') != COMMIT or any(
            empreinte(destination/rel) != digest for rel, digest in metadata['fichiers'].items()
        ):
            raise ValueError('Sources du cache modifiées ; arrêt sans exécution.')
        return destination
    archive = cache/f'TripoSR-{COMMIT}.tar.gz'
    if not archive.exists() or empreinte(archive) != ARCHIVE_SHA256:
        partial = archive.with_suffix('.part')
        try:
            with urllib.request.urlopen(SOURCE_URL, timeout=120) as response, partial.open('wb') as f:
                size = 0
                while True:
                    data = response.read(1024*1024)
                    if not data:
                        break
                    size += len(data)
                    if size > 80*1024*1024:
                        raise ValueError('Archive source trop volumineuse.')
                    f.write(data)
            if empreinte(partial) != ARCHIVE_SHA256:
                raise ValueError('Archive téléchargée non conforme à la révision contrôlée.')
            partial.replace(archive)
        finally:
            partial.unlink(missing_ok=True)
    with tempfile.TemporaryDirectory(prefix='eva-source-', dir=cache) as tmp:
        stage = Path(tmp)/'source'
        extraire_archive(archive, stage)
        system = stage/'tsr/system.py'
        code = system.read_text(encoding='utf-8')
        old = 'torch.load(weight_path, map_location="cpu")'
        if code.count(old) != 1:
            raise ValueError('Chargement des poids différent de la version contrôlée.')
        system.write_text(code.replace(old, 'torch.load(weight_path, map_location="cpu", weights_only=True)'), encoding='utf-8')
        files = {str(p.relative_to(stage)).replace('\\','/'): empreinte(p) for p in stage.rglob('*') if p.is_file()}
        (stage/'mrsc-source.json').write_text(json.dumps({'commit':COMMIT, 'archive_sha256':ARCHIVE_SHA256, 'modification':'torch.load weights_only=True', 'fichiers':files}, indent=2), encoding='utf-8')
        stage.rename(destination)
    return destination
