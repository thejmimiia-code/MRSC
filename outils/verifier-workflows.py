#!/usr/bin/env python3
"""Vérifie que les workflows GitHub Actions sont du YAML lisible.

Le 3 novembre 2026, un nom d'étape contenant « : » a suffi à rendre
`.github/workflows/verification.yml` illisible. GitHub n'a lancé aucun job :
« This run likely failed because of a workflow file issue ». Aucun contrôle du
dépôt ne lisait ce fichier — un YAML cassé n'était donc pas une erreur, c'était
un silence, et le silence ressemble à un succès jusqu'à ce qu'on regarde.

Ce contrôle lit chaque fichier de `.github/workflows/` avec un vrai analyseur
YAML, puis vérifie la forme attendue :

- le fichier se lit ;
- il porte une clé `jobs` non vide ;
- chaque job déclare `runs-on` ;
- chaque étape porte un `name` et exactement un `run` ou un `uses`.

Ce qu'il ne dit pas : il ne vérifie ni la logique, ni les versions d'actions, ni
les droits — c'est le rôle de `verifier-securite.py`. Il ne remplace pas une
exécution : un workflow valide peut échouer, et un workflow refusé par lui ne
doit pas être « corrigé » en supprimant le contrôle.

Sans analyseur YAML disponible, l'outil sort en **code 2** et le dit : un
contrôle qui ne peut pas lire sa source ne doit jamais passer pour vert.

Usage :
    python3 outils/verifier-workflows.py
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

RACINE = Path(os.environ.get("MRSC_RACINE") or Path(__file__).resolve().parent.parent).resolve()
WORKFLOWS = RACINE / ".github" / "workflows"

#: Nom du module importé. La surcharge sert au banc : il pointe un module absent
#: pour éprouver le refus « pas d'analyseur », qui est une branche à part entière.
MODULE_YAML = os.environ.get("MRSC_YAML_MODULE") or "yaml"


def charger_yaml():
    """Importe l'analyseur YAML, ou explique pourquoi le contrôle s'arrête."""
    try:
        return __import__(MODULE_YAML)
    except ImportError:
        print(
            f"Analyseur YAML absent (module « {MODULE_YAML} ») : aucun workflow "
            "n'a été vérifié — code 2, jamais vert. Installer PyYAML.",
            file=sys.stderr,
        )
        raise SystemExit(2)


def fichiers() -> list[Path]:
    if not WORKFLOWS.is_dir():
        print(f"Dossier des workflows introuvable : {WORKFLOWS}", file=sys.stderr)
        raise SystemExit(2)
    trouves = sorted(
        chemin
        for chemin in WORKFLOWS.iterdir()
        if chemin.suffix in {".yml", ".yaml"} and chemin.is_file()
    )
    if not trouves:
        # Un dossier vide ne prouve rien : le dire plutôt que d'imprimer « OK ».
        print(f"Aucun workflow trouvé dans {WORKFLOWS} — rien n'a été vérifié.", file=sys.stderr)
        raise SystemExit(2)
    return trouves


def controler(module_yaml, fichiers_lus: list[Path], racine: Path) -> list[str]:
    erreurs: list[str] = []
    for chemin in fichiers_lus:
        relatif = chemin.relative_to(racine)
        texte = chemin.read_text(encoding="utf-8")
        try:
            document = module_yaml.safe_load(texte)
        except Exception as erreur:  # noqa: BLE001 — le message de l'analyseur est le constat
            premiere = str(erreur).splitlines()
            erreurs.append(
                f"{relatif} : YAML illisible — {' '.join(premiere[:3]).strip()}"
            )
            continue
        if not isinstance(document, dict) or not document.get("jobs"):
            erreurs.append(f"{relatif} : aucune clé « jobs » lisible")
            continue
        for nom, job in (document.get("jobs") or {}).items():
            if not isinstance(job, dict):
                erreurs.append(f"{relatif} : le job « {nom} » n'est pas une table")
                continue
            if not job.get("runs-on"):
                erreurs.append(f"{relatif} : le job « {nom} » ne déclare pas « runs-on »")
            etapes = job.get("steps") or []
            if not isinstance(etapes, list):
                erreurs.append(f"{relatif} : les étapes du job « {nom} » ne sont pas une liste")
                continue
            for rang, etape in enumerate(etapes, start=1):
                if not isinstance(etape, dict):
                    erreurs.append(
                        f"{relatif} : étape {rang} du job « {nom} » — ce n'est pas une table"
                    )
                    continue
                if not etape.get("name"):
                    erreurs.append(
                        f"{relatif} : étape {rang} du job « {nom} » sans « name » — "
                        "une étape sans nom ne dit pas ce qu'elle fait quand elle échoue"
                    )
                porte_run = "run" in etape
                porte_uses = "uses" in etape
                if porte_run == porte_uses:
                    erreurs.append(
                        f"{relatif} : étape {rang} du job « {nom} » doit porter soit "
                        "« run », soit « uses » — et un seul des deux"
                    )
    return erreurs


def principal() -> int:
    module_yaml = charger_yaml()
    lus = fichiers()
    erreurs = controler(module_yaml, lus, RACINE)
    if erreurs:
        for erreur in erreurs:
            print(f"  - {erreur}", file=sys.stderr)
        print(
            f"Refusé : {len(erreurs)} problème(s) dans {len(lus)} fichier(s) de workflow.",
            file=sys.stderr,
        )
        return 1
    print(
        f"Workflows : {len(lus)} fichier(s) lus et conformes "
        f"(clé « jobs », « runs-on » par job, « name » et « run » ou « uses » par étape)."
    )
    return 0


if __name__ == "__main__":
    sys.exit(principal())
