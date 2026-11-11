#!/usr/bin/env python3
"""Banc de mutation de `verifier-plan-complet.py`.

Le plan complet n’est utile que s’il ne peut pas perdre silencieusement une
initiative, une section, un chemin, un repère ou sa réserve d’absence de
validation humaine. Six cas sont plantés dans une copie complète du dépôt :

1. une copie intacte, qui doit passer ;
2. une initiative du portefeuille retirée du plan ;
3. un chemin local cité remplacé par un fichier absent ;
4. une section structurante renommée ;
5. une phrase qui déclare la R&D terminée ;
6. les trois occurrences de l’échéance prospective effacées.

Usage :
    python3 outils/test_mutations_plan_complet.py
"""

from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RACINE / "outils"))

import banc_mutations  # noqa: E402

OUTIL = "verifier-plan-complet.py"
PLAN = "docs/rd/plan-complet-rd-innovation-prospective.md"


def executer(mutation):  # noqa: ANN001 - préparation de copie
    with tempfile.TemporaryDirectory(prefix="mrsc-plan-") as dossier:
        copie = Path(dossier) / "copie"
        banc_mutations.copie_complete(copie)
        mutation(copie)
        return banc_mutations.lancer(OUTIL, copie)


class TestPlanComplet(unittest.TestCase):
    def test_copie_intacte_passe(self) -> None:
        resultat = executer(lambda copie: None)
        self.assertEqual(resultat.returncode, 0, resultat.stdout + resultat.stderr)
        self.assertIn("Plan complet vérifié", resultat.stdout)

    def test_initiative_retiree_refusee(self) -> None:
        def retirer(copie: Path) -> None:
            chemin = banc_mutations.cible(copie, PLAN)
            texte = chemin.read_text(encoding="utf-8")
            compte = texte.count("`relire-les-44-prototypes`")
            self.assertGreaterEqual(compte, 1)
            chemin.write_text(
                texte.replace("`relire-les-44-prototypes`", "`initiative-retiree`"),
                encoding="utf-8",
            )

        resultat = executer(retirer)
        self.assertEqual(resultat.returncode, 1, resultat.stdout + resultat.stderr)
        self.assertIn("initiative absente du plan", resultat.stderr)

    def test_chemin_local_casse_refuse(self) -> None:
        def casser(copie: Path) -> None:
            banc_mutations.muter(
                copie,
                PLAN,
                "`docs/rd/portefeuille.toml`",
                "`docs/rd/portefeuille-absent.toml`",
            )

        resultat = executer(casser)
        self.assertEqual(resultat.returncode, 1, resultat.stdout + resultat.stderr)
        self.assertIn("chemin local introuvable", resultat.stderr)

    def test_section_renommee_refusee(self) -> None:
        def renommer(copie: Path) -> None:
            banc_mutations.muter(
                copie,
                PLAN,
                "## 7. Portes de décision et rôles",
                "## 7. Autre chose",
            )

        resultat = executer(renommer)
        self.assertEqual(resultat.returncode, 1, resultat.stdout + resultat.stderr)
        self.assertIn("section absente du plan", resultat.stderr)

    def test_formulation_interdite_refusee(self) -> None:
        def ajouter(copie: Path) -> None:
            banc_mutations.muter(
                copie,
                PLAN,
                "**Prochaine action prise par l’agent :**",
                "R&D terminée. **Prochaine action prise par l’agent :**",
            )

        resultat = executer(ajouter)
        self.assertEqual(resultat.returncode, 1, resultat.stdout + resultat.stderr)
        self.assertIn("formulation interdite", resultat.stderr)

    def test_reperes_effaces_refuses(self) -> None:
        def effacer(copie: Path) -> None:
            chemin = banc_mutations.cible(copie, PLAN)
            texte = chemin.read_text(encoding="utf-8")
            compte = texte.count("31 janvier 2027")
            self.assertGreaterEqual(compte, 1)
            chemin.write_text(
                texte.replace("31 janvier 2027", "une date à décider"),
                encoding="utf-8",
            )

        resultat = executer(effacer)
        self.assertEqual(resultat.returncode, 1, resultat.stdout + resultat.stderr)
        self.assertIn("repère absent du plan", resultat.stderr)


if __name__ == "__main__":
    unittest.main(verbosity=2)
