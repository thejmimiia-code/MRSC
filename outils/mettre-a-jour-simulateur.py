#!/usr/bin/env python3
"""Met à jour le moteur du simulateur embarqué dans le site M.R.S.C.

Le moteur vit dans son propre dépôt ; le site en embarque une copie
(`simulateur/`) pour que l'hébergement soit autonome (fonctions Vercel, aperçu
local). Ce script rapatrie la version voulue dans un dossier temporaire, applique le
correctif de sécurité versionné du site (ou constate qu’il est déjà amont),
met à jour `PROVENANCE.json`, puis régénère la page publiée. Un conflit arrête
la mise à jour avant de remplacer les fichiers du moteur.

Usage :
    python3 outils/mettre-a-jour-simulateur.py [--revision <branche|étiquette|commit>]
                                               [--depuis <dépôt local déjà cloné>]

Les fichiers listés dans `fichiers_ajoutes_par_le_site` (par exemple
`pont_api.py`, le pont vers les fonctions serverless) ne sont **jamais**
écrasés ni supprimés : ils n'existent pas dans le dépôt amont.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
DESTINATION = RACINE / "simulateur"
PROVENANCE = DESTINATION / "PROVENANCE.json"
CORRECTIF = RACINE / "outils" / "patchs" / "simulateur-securite-mrsc.patch"


def git(*arguments: str, cwd: Path) -> str:
    resultat = subprocess.run(
        ["git", *arguments], cwd=cwd, capture_output=True, text=True, check=False, timeout=300
    )
    if resultat.returncode != 0:
        raise SystemExit(f"git {' '.join(arguments)} a échoué :\n{resultat.stderr.strip()}")
    return resultat.stdout.strip()


def appliquer_correctif(paquet_stage: Path) -> bool:
    """Applique le patch dans une copie temporaire avant de toucher au dépôt.

    Renvoie False si la version amont contient déjà l'intégralité du correctif.
    Une application partielle ou un conflit bloque la mise à jour afin qu'un
    changement de sécurité ne soit jamais perdu silencieusement.
    """
    if not CORRECTIF.is_file():
        raise SystemExit(f"Correctif de sécurité manquant : {CORRECTIF}")

    def lancer(*arguments: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            ["git", "apply", *arguments, str(CORRECTIF)],
            cwd=paquet_stage.parent,
            capture_output=True,
            text=True,
            check=False,
            timeout=60,
        )

    verification = lancer("--check")
    if verification.returncode == 0:
        application = lancer()
        if application.returncode != 0:
            raise SystemExit(
                "Impossible d'appliquer le correctif de sécurité dans la copie temporaire :\n"
                + application.stderr.strip()
            )
        return True

    inverse = lancer("--reverse", "--check")
    if inverse.returncode == 0:
        print("Le correctif est déjà intégré à la révision amont.")
        return False
    raise SystemExit(
        "Le correctif de sécurité n'est plus applicable à cette révision amont. "
        "Aucun fichier du moteur local n'a été remplacé ; révisez le patch avant de continuer.\n"
        + verification.stderr.strip()
    )


def main() -> int:
    provenance = json.loads(PROVENANCE.read_text(encoding="utf-8"))
    analyseur = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    analyseur.add_argument("--revision", default="main", help="branche, étiquette ou commit à copier")
    analyseur.add_argument("--depot", default=provenance["depot_amont"], help="dépôt amont")
    analyseur.add_argument("--depuis", type=Path, help="copier depuis un clone local au lieu de cloner")
    options = analyseur.parse_args()

    provisoire: tempfile.TemporaryDirectory[str] | None = None
    if options.depuis:
        source = options.depuis.resolve()
        git("rev-parse", "--git-dir", cwd=source)
    else:
        provisoire = tempfile.TemporaryDirectory(prefix="simulateur-amont-")
        source = Path(provisoire.name) / "depot"
        print(f"Clonage de {options.depot} ({options.revision})…")
        git("clone", "--quiet", "--depth", "1", "--branch", options.revision, options.depot, str(source), cwd=Path.cwd())

    paquet = source / "simulateur"
    if not (paquet / "interface.py").is_file():
        raise SystemExit(f"{paquet} ne contient pas le moteur attendu (interface.py absent).")

    ajoutes = set(provenance.get("fichiers_ajoutes_par_le_site", []))
    copiés, ignorés = [], []
    staging_temp = tempfile.TemporaryDirectory(prefix="simulateur-correctif-")
    paquet_stage = Path(staging_temp.name) / "simulateur"
    paquet_stage.mkdir()
    try:
        for fichier in sorted(paquet.glob("*.py")):
            if fichier.name in ajoutes:
                ignorés.append(fichier.name)
                continue
            shutil.copy2(fichier, paquet_stage / fichier.name)
        correctif_applique = appliquer_correctif(paquet_stage)
        # Le dépôt courant n'est touché qu'après copie complète et patch valide.
        for fichier in sorted(paquet_stage.glob("*.py")):
            shutil.copy2(fichier, DESTINATION / fichier.name)
            copiés.append(fichier.name)
    finally:
        staging_temp.cleanup()

    nouveaux = json.loads(PROVENANCE.read_text(encoding="utf-8"))
    nouveaux.update(
        {
            "revision": git("rev-parse", "HEAD", cwd=source),
            "revision_courte": git("rev-parse", "--short", "HEAD", cwd=source),
            "date_revision": git("log", "-1", "--format=%cI", cwd=source),
            "sujet": git("log", "-1", "--format=%s", cwd=source),
            "copie_le": dt.date.today().isoformat(),
            "correctif_local": {
                "fichier": str(CORRECTIF.relative_to(RACINE)),
                "sha256": hashlib.sha256(CORRECTIF.read_bytes()).hexdigest(),
                "etat": "appliqué" if correctif_applique else "déjà intégré à l’amont",
            },
        }
    )
    PROVENANCE.write_text(
        json.dumps(nouveaux, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    if provisoire:
        provisoire.cleanup()

    print(f"{len(copiés)} fichiers du moteur mis à jour depuis {nouveaux['revision_courte']}.")
    if ignorés:
        print(f"Fichiers propres au site conservés : {', '.join(ignorés)}.")
    print("Régénération de la page publiée…")
    subprocess.run(
        [sys.executable, str(RACINE / "outils" / "construire-simulateur.py")],
        cwd=RACINE,
        check=True,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
