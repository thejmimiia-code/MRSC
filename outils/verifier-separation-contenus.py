#!/usr/bin/env python3
"""Empêche le retour des chemins connus de contenus personnels dans MRSC.

Contrôle local borné, pas un détecteur universel de données sensibles.
L'historique, les PR et les étiquettes ne sont pas purgés par ce contrôle.
"""
from pathlib import Path
import fnmatch
import re
import sys

RACINE = Path(__file__).resolve().parent.parent
INTERDITS = (
    "animations.html", "assets/css/animations.css", "assets/js/animations.js",
    "assets/images/animation/eva*", "assets/images/eva/*",
    "assets/images/eva-*", "assets/models/eva/*",
    "docs/rd/statuts-animation/eva-*",
    "docs/rd/statuts-animation/ARCHIVE-planches-2026-10.sha256".lower(),
)
PERSONNAGE = re.compile(r"(?:\beva|\belle)-(?:\d|choisie|lock|moderne|exo)", re.IGNORECASE)
REFERENCES = re.compile(
    r"animations\.html|assets/(?:images/(?:animation/eva|eva[-/])|models/eva/)"
    r"|animation-lab-link", re.IGNORECASE,
)


def erreurs(racine: Path) -> list[str]:
    resultat = []
    # Les archives de travail ne doivent pas être placées dans ces dossiers,
    # même si un .gitignore empêcherait leur commit.
    candidats = list(racine.glob("*.html"))
    for dossier in ("assets", "docs/rd/statuts-animation"):
        base = racine / dossier
        if base.exists():
            candidats.extend(f for f in base.rglob("*") if f.is_file())
    for fichier in candidats:
        relatif = fichier.relative_to(racine).as_posix().lower()
        if any(fnmatch.fnmatchcase(relatif, motif) for motif in INTERDITS):
            resultat.append(f"contenu exclu présent : {relatif}")
        if fichier.suffix in {".html", ".js", ".css"}:
            if REFERENCES.search(fichier.read_text(encoding="utf-8")):
                resultat.append(f"référence retirée encore utilisée : {relatif}")
    documents = [racine / "docs/rd/journal.md", racine / "docs/rd/plan-statuts-animation.md"]
    base = racine / "docs/rd/statuts-animation"
    if base.exists():
        documents.extend(f for f in base.iterdir() if f.suffix in {".md", ".sha256"})
    for fichier in documents:
        if fichier.is_file() and PERSONNAGE.search(fichier.read_text(encoding="utf-8")):
            resultat.append(f"inventaire ou référence de personnage réintroduit : {fichier.relative_to(racine)}")
    for nom in ("sitemap.xml", ".github/workflows/deploy-pages.yml", "outils/serveur-local.py", "outils/construire-apprentissages.py"):
        fichier = racine / nom
        if fichier.is_file() and REFERENCES.search(fichier.read_text(encoding="utf-8")):
            resultat.append(f"route retirée encore déclarée : {nom}")
    return sorted(set(resultat))


def main() -> int:
    problemes = erreurs(RACINE)
    if problemes:
        print("ÉCHEC — séparation des contenus")
        print("\n".join(f"- {p}" for p in problemes))
        return 1
    print("OK — chemins connus de contenus personnels absents ; aucune route du prototype retiré.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
