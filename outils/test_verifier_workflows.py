#!/usr/bin/env python3
"""Éprouve `verifier-workflows.py` : il doit mordre, et il doit avouer.

Le 3 novembre 2026, un nom d'étape contenant « : » a rendu
`.github/workflows/verification.yml` illisible. GitHub a répondu « This run
likely failed because of a workflow file issue » et n'a lancé **aucun** job :
pendant une heure, le dépôt a été sans contrôle du tout, sans que rien ne le
dise. Ce banc plante cette faute exacte, et les autres que le contrôle
prétend voir.

Le cas le plus important est le dernier : sans analyseur YAML, le contrôle ne
peut rien lire. Il doit alors sortir en **code 2** en le disant — jamais en
code 0 comme si six fichiers avaient été vérifiés.

Usage :
    python3 outils/test_verifier_workflows.py
"""

from __future__ import annotations

import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RACINE / "outils"))

import banc_mutations  # noqa: E402

OUTIL = "verifier-workflows.py"
WORKFLOW = ".github/workflows/verification.yml"


def lancer_sur(copie: Path, **environnement: str) -> subprocess.CompletedProcess[str]:
    """Lance l'outil sur la copie, avec des variables en plus si besoin."""
    return subprocess.run(
        [sys.executable, str(RACINE / "outils" / OUTIL)],
        capture_output=True,
        text=True,
        check=False,
        env=dict(os.environ, MRSC_RACINE=str(copie), **environnement),
    )


def copie_avec_workflow(dossier: Path) -> Path:
    """Copie du dépôt dont le workflow est réel, prêt à être muté."""
    copie = dossier / "copie"
    copie.mkdir()
    banc_mutations.copie_jetable(copie)
    banc_mutations.ouvrir(copie, WORKFLOW)
    return copie


class TestVerifierWorkflows(unittest.TestCase):
    def test_copie_intacte_passe(self) -> None:
        with tempfile.TemporaryDirectory() as dossier:
            copie = copie_avec_workflow(Path(dossier))
            resultat = lancer_sur(copie)
        self.assertEqual(resultat.returncode, 0, resultat.stdout + resultat.stderr)
        self.assertIn("Workflows :", resultat.stdout)
        self.assertIn("conformes", resultat.stdout)

    def test_deux_points_dans_un_nom_etape_refuse(self) -> None:
        """La faute du 3 novembre : un scalaire YAML non cité qui devient une table."""
        with tempfile.TemporaryDirectory() as dossier:
            copie = copie_avec_workflow(Path(dossier))
            banc_mutations.muter(
                copie,
                WORKFLOW,
                "      - name: Récupérer les sources\n",
                "      - name: Récupérer les sources : cassé\n",
            )
            resultat = lancer_sur(copie)
        self.assertEqual(resultat.returncode, 1, resultat.stdout + resultat.stderr)
        self.assertIn("YAML illisible", resultat.stderr)
        self.assertIn(WORKFLOW, resultat.stderr)

    def test_job_sans_runs_on_refuse(self) -> None:
        with tempfile.TemporaryDirectory() as dossier:
            copie = copie_avec_workflow(Path(dossier))
            banc_mutations.muter(copie, WORKFLOW, "    runs-on: ubuntu-24.04\n", "", )
            resultat = lancer_sur(copie)
        self.assertEqual(resultat.returncode, 1, resultat.stdout + resultat.stderr)
        self.assertIn("runs-on", resultat.stderr)

    def test_etape_sans_nom_refusee(self) -> None:
        with tempfile.TemporaryDirectory() as dossier:
            copie = copie_avec_workflow(Path(dossier))
            banc_mutations.muter(
                copie,
                WORKFLOW,
                "      - name: Récupérer les sources\n",
                "      - name: ''\n",
            )
            resultat = lancer_sur(copie)
        self.assertEqual(resultat.returncode, 1, resultat.stdout + resultat.stderr)
        self.assertIn("sans « name »", resultat.stderr)

    def test_etape_avec_run_et_uses_refusee(self) -> None:
        with tempfile.TemporaryDirectory() as dossier:
            copie = copie_avec_workflow(Path(dossier))
            banc_mutations.muter(
                copie,
                WORKFLOW,
                "      - name: Compiler les modules Python\n        run: python3 -m py_compile simulateur/*.py api/*.py outils/*.py\n",
                "      - name: Compiler les modules Python\n"
                "        uses: actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1\n"
                "        run: python3 -m py_compile simulateur/*.py api/*.py outils/*.py\n",
            )
            resultat = lancer_sur(copie)
        self.assertEqual(resultat.returncode, 1, resultat.stdout + resultat.stderr)
        self.assertIn("et un seul des deux", resultat.stderr)

    def test_sans_jobs_refuse(self) -> None:
        with tempfile.TemporaryDirectory() as dossier:
            copie = copie_avec_workflow(Path(dossier))
            banc_mutations.muter(copie, WORKFLOW, "jobs:\n", "jobs_vides:\n")
            resultat = lancer_sur(copie)
        self.assertEqual(resultat.returncode, 1, resultat.stdout + resultat.stderr)
        self.assertIn("aucune clé « jobs »", resultat.stderr)

    def test_aucun_workflow_refuse(self) -> None:
        """Un dossier vide ne prouve rien : le dire, plutôt que d'imprimer moins."""
        with tempfile.TemporaryDirectory() as dossier:
            copie = Path(dossier) / "copie"
            copie.mkdir()
            (copie / ".github" / "workflows").mkdir(parents=True)
            resultat = lancer_sur(copie)
        self.assertEqual(resultat.returncode, 2, resultat.stdout + resultat.stderr)
        self.assertIn("Aucun workflow", resultat.stderr)

    def test_sans_analyseur_yaml_sort_en_deux(self) -> None:
        """Pas d'analyseur : rien n'a été vérifié, et l'outil le crie."""
        with tempfile.TemporaryDirectory() as dossier:
            copie = copie_avec_workflow(Path(dossier))
            resultat = lancer_sur(copie, MRSC_YAML_MODULE="yaml_absent_pour_le_banc")
        self.assertEqual(resultat.returncode, 2, resultat.stdout + resultat.stderr)
        self.assertIn("Analyseur YAML absent", resultat.stderr)
        self.assertNotIn("conformes", resultat.stdout)


if __name__ == "__main__":
    unittest.main()
