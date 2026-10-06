#!/usr/bin/env python3
"""Le moteur embarqué a-t-il pris du retard sur le dépôt amont ?

Le simulateur se développe en continu ; le site embarque une copie datée de son
moteur (`simulateur/PROVENANCE.json`). Ce script compare la révision copiée à
celle de la branche `main` du dépôt amont, **sans rien cloner ni modifier**, et
sort en erreur (code 1) quand une mise à jour est disponible — ce qui permet de
brancher une alerte automatique (voir `.github/workflows/maj-simulateur.yml`).

Usage :
    python3 outils/verifier-maj-amont.py [--json]

Pour appliquer la mise à jour ensuite :
    python3 outils/mettre-a-jour-simulateur.py
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
PROVENANCE = RACINE / "simulateur" / "PROVENANCE.json"


def revision_amont(depot: str, branche: str = "main") -> str:
    resultat = subprocess.run(
        ["git", "ls-remote", depot, branche],
        capture_output=True,
        text=True,
        timeout=120,
        check=False,
    )
    if resultat.returncode != 0 or not resultat.stdout.strip():
        raise SystemExit(
            f"Impossible d'interroger {depot} ({branche}) :\n{resultat.stderr.strip()}"
        )
    return resultat.stdout.split()[0]


def main() -> int:
    analyseur = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    analyseur.add_argument("--json", action="store_true", help="sortie JSON (pour un workflow)")
    options = analyseur.parse_args()

    provenance = json.loads(PROVENANCE.read_text(encoding="utf-8"))
    copiee = provenance["revision"]
    amont = revision_amont(provenance["depot_amont"])

    etat = {
        "depot_amont": provenance["depot_amont"],
        "branche": "main",
        "revision_copiee": copiee,
        "revision_amont": amont,
        "a_jour": copiee == amont,
        "copie_le": provenance.get("copie_le"),
    }
    if options.json:
        print(json.dumps(etat, ensure_ascii=False, indent=2))
    else:
        print(f"Dépôt amont        : {etat['depot_amont']}")
        print(f"Révision embarquée : {copiee[:12]} (copiée le {etat['copie_le']})")
        print(f"Révision amont     : {amont[:12]}")
        print()
        if etat["a_jour"]:
            print("Le moteur embarqué est à jour.")
        else:
            print("Mise à jour disponible. Pour l'appliquer :")
            print("    python3 outils/mettre-a-jour-simulateur.py")
            print("    python3 outils/verifier-integration.py")
            print("puis relire et valider le diff avant de publier.")

    return 0 if etat["a_jour"] else 1


if __name__ == "__main__":
    sys.exit(main())
