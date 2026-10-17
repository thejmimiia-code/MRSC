#!/usr/bin/env python3
"""Génère et vérifie les variantes AVIF/WebP des grandes illustrations du site.

Objectif : servir une image adaptée à la largeur d’affichage et au format
accepté par le navigateur, sans dépendre d’un service distant ni d’un CDN.
Les images d’origine restent la référence et le repli JPEG ; elles ne sont
jamais modifiées ni supprimées par ce script.

    python3 outils/optimiser-images.py            # génère les variantes absentes ou périmées
    python3 outils/optimiser-images.py --forcer   # régénère toutes les variantes
    python3 outils/optimiser-images.py --verifier # contrôle hors ligne, sans ImageMagick

Le manifeste `docs/rd/derives-images.json` enregistre les empreintes des
sources, les largeurs, les formats, les qualités et les tailles produites. Il
permet de détecter une source modifiée sans que ses variantes aient été
régénérées. La génération demande ImageMagick (`convert` ou `magick`) ; le
contrôle, non. Aucun chiffre de ce script n’est une mesure réseau, un bilan
carbone ou une preuve de rendu dans un navigateur.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
IMAGES = ROOT / "assets" / "images"
MANIFESTE = ROOT / "docs" / "rd" / "derives-images.json"
VERSION = 1

# Largeurs réellement utiles : 800 px couvre un téléphone en 2× ou un écran
# étroit en 1× ; la largeur d’origine couvre les grands écrans. Les qualités
# ont été retenues après comparaison PSNR et contrôle visuel à 800 px
# (voir docs/rd/poids-et-sobriete-numerique.md).
SOURCES = (
    {
        "fichier": "accueil-logo-mrsc-3d.jpg",
        "largeurs": (800, 1400),
        "qualites": {"avif": 60, "webp": 80},
    },
    {
        "fichier": "mondes-savoirs-hero.jpg",
        "largeurs": (800, 1200, 1672),
        "qualites": {"avif": 60, "webp": 80},
    },
    {
        "fichier": "escales-anglais-hero.jpg",
        "largeurs": (800, 1672),
        "qualites": {"avif": 60, "webp": 80},
    },
)


def empreinte(chemin: Path) -> str:
    digest = hashlib.sha256()
    with chemin.open("rb") as flux:
        for bloc in iter(lambda: flux.read(1024 * 1024), b""):
            digest.update(bloc)
    return digest.hexdigest()


def nom_variante(source: Path, largeur: int, format_image: str) -> str:
    return f"{source.stem}-{largeur}.{format_image}"


def chemin_variante(source: Path, largeur: int, format_image: str) -> Path:
    return IMAGES / nom_variante(source, largeur, format_image)


def outil_imagemagick() -> list[str] | None:
    for nom in ("magick", "convert"):
        chemin = shutil.which(nom)
        if chemin:
            return [chemin]
    return None


def lire_dimensions(chemin: Path) -> tuple[int, int]:
    commande = outil_imagemagick()
    if not commande:
        raise RuntimeError("ImageMagick est requis pour mesurer les variantes générées")
    resultat = subprocess.run(
        [*commande, str(chemin), "-format", "%w %h", "info:"],
        check=True,
        capture_output=True,
        text=True,
    )
    largeur, hauteur = resultat.stdout.split()
    return int(largeur), int(hauteur)


def construire_manifeste(regenerer: bool = False) -> dict:
    commande = outil_imagemagick()
    if not commande:
        raise RuntimeError("ImageMagick (`magick` ou `convert`) est requis pour générer les variantes")
    entrees = []
    for source_config in SOURCES:
        source = IMAGES / source_config["fichier"]
        if not source.is_file():
            raise FileNotFoundError(f"source absente : {source.relative_to(ROOT)}")
        variants = []
        for largeur in source_config["largeurs"]:
            for format_image, qualite in source_config["qualites"].items():
                destination = chemin_variante(source, largeur, format_image)
                if regenerer or not destination.is_file():
                    sous_commande = [
                        *commande, str(source), "-auto-orient", "-resize", f"{largeur}x",
                        "-strip", "-quality", str(qualite), str(destination),
                    ]
                    subprocess.run(sous_commande, check=True)
                largeur_obtenue, hauteur_obtenue = lire_dimensions(destination)
                if largeur_obtenue != largeur:
                    raise RuntimeError(
                        f"{destination.relative_to(ROOT)} : largeur {largeur_obtenue} au lieu de {largeur}"
                    )
                if destination.stat().st_size >= source.stat().st_size:
                    raise RuntimeError(
                        f"{destination.relative_to(ROOT)} : variante plus lourde que la source"
                    )
                variants.append(
                    {
                        "fichier": destination.relative_to(ROOT).as_posix(),
                        "largeur": largeur_obtenue,
                        "hauteur": hauteur_obtenue,
                        "format": format_image,
                        "qualite": qualite,
                        "octets": destination.stat().st_size,
                    }
                )
        entrees.append(
            {
                "source": source.relative_to(ROOT).as_posix(),
                "octets_source": source.stat().st_size,
                "sha256_source": empreinte(source),
                "variantes": variants,
            }
        )
    return {"version": VERSION, "outil": "outils/optimiser-images.py", "sources": entrees}


def ecrire_manifeste(manifeste: dict) -> None:
    MANIFESTE.parent.mkdir(parents=True, exist_ok=True)
    MANIFESTE.write_text(
        json.dumps(manifeste, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


def verifier() -> int:
    erreurs: list[str] = []
    if not MANIFESTE.is_file():
        print(f"ÉCHEC — manifeste absent : {MANIFESTE.relative_to(ROOT)}", file=sys.stderr)
        return 1
    try:
        manifeste = json.loads(MANIFESTE.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as erreur:
        print(f"ÉCHEC — manifeste illisible : {erreur}", file=sys.stderr)
        return 1
    if manifeste.get("version") != VERSION:
        erreurs.append(f"version de manifeste {manifeste.get('version')!r} au lieu de {VERSION}")
    attendues = {config["fichier"]: config for config in SOURCES}
    vues = set()
    total_source = 0
    total_variantes = 0
    for entree in manifeste.get("sources", []):
        source_relatif = entree.get("source", "")
        nom = Path(source_relatif).name
        vues.add(nom)
        if nom not in attendues:
            erreurs.append(f"source inattendue dans le manifeste : {source_relatif}")
            continue
        source = ROOT / source_relatif
        if not source.is_file():
            erreurs.append(f"source absente : {source_relatif}")
            continue
        if empreinte(source) != entree.get("sha256_source"):
            erreurs.append(
                f"{source_relatif} : source modifiée depuis la génération ; relancer le script"
            )
        if source.stat().st_size != entree.get("octets_source"):
            erreurs.append(f"{source_relatif} : taille de source incohérente")
        total_source += source.stat().st_size
        config = attendues[nom]
        attendues_variantes = {
            (largeur, format_image)
            for largeur in config["largeurs"]
            for format_image in config["qualites"]
        }
        presentes = set()
        for variante in entree.get("variantes", []):
            chemin = ROOT / variante.get("fichier", "")
            presentes.add((variante.get("largeur"), variante.get("format")))
            if not chemin.is_file():
                erreurs.append(f"variante absente : {variante.get('fichier')}")
                continue
            if chemin.stat().st_size != variante.get("octets"):
                erreurs.append(f"{variante.get('fichier')} : taille incohérente avec le manifeste")
            if variante.get("format") == "avif" and chemin.suffix != ".avif":
                erreurs.append(f"{variante.get('fichier')} : extension incohérente")
            if variante.get("format") == "webp" and chemin.suffix != ".webp":
                erreurs.append(f"{variante.get('fichier')} : extension incohérente")
            if chemin.stat().st_size >= source.stat().st_size:
                erreurs.append(f"{variante.get('fichier')} : variante plus lourde que la source")
            total_variantes += chemin.stat().st_size
        manquantes = attendues_variantes - presentes
        if manquantes:
            erreurs.append(
                f"{source_relatif} : variantes manquantes "
                + ", ".join(f"{largeur}px {format_image}" for largeur, format_image in sorted(manquantes))
            )
    for nom in sorted(set(attendues) - vues):
        erreurs.append(f"source non décrite dans le manifeste : {nom}")
    if erreurs:
        for erreur in erreurs:
            print(f"ÉCHEC — {erreur}", file=sys.stderr)
        return 1
    print(
        f"Variantes d’images : {len(manifeste['sources'])} sources, "
        f"{total_variantes / 1024:.1f} Kio dérivés pour {total_source / 1024:.1f} Kio de sources, "
        "manifeste et empreintes cohérents."
    )
    return 0


def main() -> int:
    analyseur = argparse.ArgumentParser(description=__doc__)
    analyseur.add_argument("--verifier", action="store_true", help="contrôler sans régénérer")
    analyseur.add_argument("--forcer", action="store_true", help="régénérer toutes les variantes")
    options = analyseur.parse_args()

    if options.verifier:
        return verifier()
    try:
        manifeste = construire_manifeste(regenerer=options.forcer)
    except (OSError, RuntimeError, subprocess.CalledProcessError) as erreur:
        print(f"ÉCHEC — génération impossible : {erreur}", file=sys.stderr)
        return 1
    ecrire_manifeste(manifeste)
    total_source = sum(entree["octets_source"] for entree in manifeste["sources"])
    total_variantes = sum(
        variante["octets"]
        for entree in manifeste["sources"]
        for variante in entree["variantes"]
    )
    print(
        f"Images optimisées : {len(manifeste['sources'])} sources, "
        f"{total_variantes / 1024:.1f} Kio de variantes pour {total_source / 1024:.1f} Kio de sources."
    )
    print(f"Manifeste : {MANIFESTE.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
