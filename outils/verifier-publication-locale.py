#!/usr/bin/env python3
"""Vérifie que le site publié ne manque d'aucun fichier présent dans le dépôt.

Le workflow `.github/workflows/deploy-pages.yml` ne publie **qu'une partie** du
dépôt : une liste de pages à la racine, `assets/`, `apprendre/fiches/` et la
page du simulateur. Un fichier peut donc exister dans le dépôt, être référencé
par les pages, et manquer quand même sur le site — c'est le cas du favicon,
absent de la liste de copie.

Cet outil relit la liste de copie du workflow, reconstruit le périmètre publié
réel, puis contrôle, sans réseau :

1. que toute page publique du dépôt est bien dans la liste de copie ;
2. que chaque source copiée existe dans le dépôt ;
3. que chaque page publiée a ses liens `href`/`src` vers un fichier publié ;
4. que les `url()` des feuilles de style publiées pointent vers un fichier publié ;
5. que chaque adresse du `sitemap.xml` correspond à une page publiée ;
6. que la liste blanche de l'aperçu local (`outils/serveur-local.py`) est
   exactement celle des fichiers racine publiés — deux listes qui divergent
   produisent un aperçu qui ne ressemble pas au site.

Usage :
    python3 outils/verifier-publication-locale.py

Code de sortie : 0 si le périmètre publié est complet, 1 sinon.
"""

from __future__ import annotations

import os
import posixpath
import re
import shlex
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from urllib.parse import unquote

#: Racine lue par le contrôle. La surcharge sert au banc de mutation
#: (`outils/test_mutations_publication_locale.py`), qui retire un fichier de la
#: liste de copie ou casse un lien dans une copie du dépôt.
RACINE = Path(os.environ.get("MRSC_RACINE") or Path(__file__).resolve().parent.parent).resolve()
WORKFLOW = RACINE / ".github" / "workflows" / "deploy-pages.yml"
SERVEUR = RACINE / "outils" / "serveur-local.py"
ETAPE = "Prepare public site files"
SITE_URL = "https://thejmimiia-code.github.io/MRSC/"
EXTERNES = ("http://", "https://", "mailto:", "tel:", "data:", "javascript:", "#")


def lignes_etape() -> list[str]:
    """Lignes du bloc `run:` de l'étape de préparation du site."""
    lignes = WORKFLOW.read_text(encoding="utf-8").splitlines()
    debut = next((i for i, ligne in enumerate(lignes) if ETAPE in ligne), None)
    if debut is None:
        return []
    bloc: list[str] = []
    for ligne in lignes[debut + 1 :]:
        if re.match(r"^\s{6}- name:", ligne):
            break
        bloc.append(ligne.strip())
    return bloc


def perimetre() -> tuple[dict[str, Path], list[str]]:
    """Chemins publiés (relatifs au site) associés à leur source dans le dépôt."""
    publies: dict[str, Path] = {}
    erreurs: list[str] = []
    for ligne in lignes_etape():
        if not ligne.startswith("cp "):
            continue
        try:
            morceaux = shlex.split(ligne)
        except ValueError:
            erreurs.append(f"commande de copie illisible : {ligne}")
            continue
        if morceaux[1] == "-R":
            morceaux = [morceaux[0]] + morceaux[2:]
        if len(morceaux) < 3:
            continue
        sources, destination = morceaux[1:-1], morceaux[-1]
        if not destination.startswith("_site"):
            erreurs.append(f"copie hors de _site : {ligne}")
            continue
        prefixe = destination[len("_site") :].strip("/")
        for source in sources:
            chemin = RACINE / source
            if not chemin.exists():
                erreurs.append(f"source absente du dépôt : {source}")
                continue
            if chemin.is_dir():
                for fichier in sorted(chemin.rglob("*")):
                    if not fichier.is_file():
                        continue
                    relatif = fichier.relative_to(chemin).as_posix()
                    publies[posixpath.join(prefixe, relatif) if prefixe else relatif] = fichier
            else:
                publies[posixpath.join(prefixe, chemin.name) if prefixe else chemin.name] = chemin
    return publies, erreurs


def liste_apercu_local() -> set[str]:
    """Fichiers racine servis par l'aperçu local, lus dans son code."""
    if not SERVEUR.is_file():
        return set()
    texte = SERVEUR.read_text(encoding="utf-8")
    bloc = re.search(r"FICHIERS_RACINE_PUBLICS\s*=\s*frozenset\(\{(.*?)\}\)", texte, re.S)
    return set(re.findall(r'"([^"]+)"', bloc.group(1))) if bloc else set()


def resoudre(base: str, reference: str) -> str | None:
    """Chemin publié visé par une référence, ou None si elle est hors périmètre."""
    reference = unquote(reference.split("#")[0].split("?")[0])
    if not reference or reference.startswith(EXTERNES) or reference.startswith("${"):
        return None
    if reference.startswith("/MRSC/"):
        return reference[len("/MRSC/") :] or "index.html"
    if reference.startswith("/"):
        return None
    chemin = posixpath.normpath(posixpath.join(base, reference))
    if chemin.startswith(".."):
        return None
    return "index.html" if chemin == "." else chemin


def existe(chemin: str, publies: dict[str, Path]) -> bool:
    return chemin in publies or f"{chemin.rstrip('/')}/index.html" in publies


def main() -> int:
    if not WORKFLOW.is_file():
        print("ÉCHEC — workflow de publication absent")
        return 1

    publies, erreurs = perimetre()
    if not publies:
        print("ÉCHEC — aucune copie reconnue dans l'étape de préparation")
        return 1

    # Toute page publique du dépôt doit être publiée : une page oubliée dans la
    # liste de copie ne serait référencée par rien et passerait inaperçue.
    pages_publiques = sorted(
        [chemin.name for chemin in RACINE.glob("*.html")]
        + [f"apprendre/fiches/{chemin.name}" for chemin in (RACINE / "apprendre" / "fiches").glob("*.html")]
        + ["simulateur/index.html"]
    )
    for page in pages_publiques:
        if page not in publies:
            erreurs.append(f"page publique absente du périmètre publié : {page}")

    references = 0
    manquants: dict[str, list[str]] = {}
    for chemin, source in sorted(publies.items()):
        if not chemin.endswith(".html"):
            continue
        contenu = source.read_text(encoding="utf-8")
        for attribut, valeur in re.findall(r'(href|src)="([^"]+)"', contenu):
            cible = resoudre(posixpath.dirname(chemin), valeur)
            if cible is None:
                continue
            references += 1
            if not existe(cible, publies):
                manquants.setdefault(f"{cible} (référence {attribut}=\"{valeur}\")", []).append(chemin)

    for chemin, source in sorted(publies.items()):
        if not chemin.endswith(".css"):
            continue
        for valeur in re.findall(r'url\(\s*["\']?([^"\')]+)["\']?\s*\)', source.read_text(encoding="utf-8")):
            cible = resoudre(posixpath.dirname(chemin), valeur)
            if cible is None:
                continue
            references += 1
            if not existe(cible, publies):
                manquants.setdefault(f"{cible} (url dans {chemin})", []).append(chemin)

    for cible, pages_concernees in sorted(manquants.items()):
        erreurs.append(
            f"{cible} n'est pas publié — {len(pages_concernees)} page(s), "
            f"par exemple {pages_concernees[0]}"
        )

    attendus_racine = {chemin for chemin in publies if "/" not in chemin}
    apercu = liste_apercu_local()
    if not apercu:
        erreurs.append("liste blanche de l'aperçu local illisible dans outils/serveur-local.py")
    else:
        manquants_apercu = sorted(attendus_racine - apercu)
        superflus_apercu = sorted(apercu - attendus_racine)
        if manquants_apercu:
            erreurs.append(
                "aperçu local : fichiers publiés non servis — " + ", ".join(manquants_apercu)
            )
        if superflus_apercu:
            erreurs.append(
                "aperçu local : fichiers servis mais non publiés — " + ", ".join(superflus_apercu)
            )

    if "sitemap.xml" in publies:
        arbre = ET.fromstring(publies["sitemap.xml"].read_text(encoding="utf-8"))
        namespace = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9"}
        for noeud in arbre.findall("s:url/s:loc", namespace):
            adresse = (noeud.text or "").strip()
            if not adresse.startswith(SITE_URL):
                erreurs.append(f"sitemap : adresse hors du site — {adresse}")
                continue
            chemin = adresse[len(SITE_URL) :] or "index.html"
            if chemin.endswith("/"):
                chemin += "index.html"
            references += 1
            if chemin not in publies:
                erreurs.append(f"sitemap : {adresse} ne correspond à aucun fichier publié")

    if erreurs:
        print("ÉCHEC — le site publié serait incomplet")
        for erreur in erreurs:
            print(f"  - {erreur}")
        return 1

    pages = sum(1 for chemin in publies if chemin.endswith(".html"))
    print(
        f"OK — périmètre publié complet : {len(publies)} fichiers, {pages} pages, "
        f"{references} références internes toutes résolues dans le site publié, "
        f"aperçu local aligné sur {len(attendus_racine)} fichiers racine."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
