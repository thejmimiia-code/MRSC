#!/usr/bin/env python3
"""Banc de mutation de `verifier-rd-continue.py`.

Ce contrôle garde la continuité de la R&D : les skills des agents, le
portefeuille d'initiatives, la carte des lacunes, les avancées, les sources
refusées, le registre de relecture, ce que la page de transparence en dit, et la
veille hebdomadaire. C'est la mémoire du projet — et sa seule preuve était son
propre vert.

Quatre fautes sont plantées dans une copie complète du dépôt :

1. une initiative du portefeuille privée de son champ `question` ;
2. une section `## Garde-fous` retirée d'un skill — le skill devient inexploitable
   et les initiatives qui s'y appuient le signalent ;
3. l'ancre `rd-innovation` renommée dans `transparence.html` ;
4. la veille hebdomadaire déplacée du lundi au mardi, sans mise à jour des
   autres workflows qui doivent la citer.

Usage :
    python3 outils/test_mutations_rd_continue.py
"""

from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RACINE / "outils"))

import banc_mutations  # noqa: E402

OUTIL = "verifier-rd-continue.py"
PORTEFEUILLE = "docs/rd/portefeuille.toml"
VEILLE = ".github/workflows/veille-apprentissages.yml"


def executer(mutation) -> subprocess.CompletedProcess[str]:  # noqa: ANN001 - préparation de copie
    with tempfile.TemporaryDirectory(prefix="mrsc-rd-") as dossier:
        copie = Path(dossier) / "copie"
        banc_mutations.copie_complete(copie)
        mutation(copie)
        return banc_mutations.lancer(OUTIL, copie)


def retirer_champ_question(copie: Path) -> None:
    """Supprime le premier `question = …` du portefeuille, quel qu'il soit.

    La ligne est lue dans la copie : le banc ne doit pas se périmer le jour où
    une initiative est réécrite.
    """
    texte = (copie / PORTEFEUILLE).read_text(encoding="utf-8")
    debut = texte.index("question = ")
    fin = texte.index("\n", debut) + 1
    banc_mutations.muter(copie, PORTEFEUILLE, texte[debut:fin], "")


class TestRdContinue(unittest.TestCase):
    def test_copie_intacte_passe(self) -> None:
        resultat = executer(lambda copie: None)
        self.assertEqual(resultat.returncode, 0, resultat.stdout[-2000:] + resultat.stderr[-2000:])
        self.assertNotIn("ÉCHEC", resultat.stdout)

    def test_initiative_sans_question_refusee(self) -> None:
        resultat = executer(retirer_champ_question)
        self.assertEqual(resultat.returncode, 1, resultat.stdout[-2000:])
        self.assertIn("champs manquants question", resultat.stdout)

    def test_skill_sans_garde_fous_refuse(self) -> None:
        def casser(copie: Path) -> None:
            skill = sorted((copie / ".agents" / "skills").glob("*/SKILL.md"))[0]
            banc_mutations.muter(
                copie, skill.relative_to(copie).as_posix(), "## Garde-fous", "## Autre chose"
            )

        resultat = executer(casser)
        self.assertEqual(resultat.returncode, 1, resultat.stdout[-2000:])
        self.assertIn("frontmatter ou sections manquants : ## Garde-fous", resultat.stdout)

    def test_ancre_de_transparence_renommee_refusee(self) -> None:
        def renommer(copie: Path) -> None:
            banc_mutations.muter(copie, "transparence.html", 'id="rd-innovation"', 'id="rd-ailleurs"')

        resultat = executer(renommer)
        self.assertEqual(resultat.returncode, 1, resultat.stdout[-2000:])
        self.assertIn("La R&D continue est visible", resultat.stdout)

    def test_veille_decalee_refusee(self) -> None:
        def decaler(copie: Path) -> None:
            banc_mutations.muter(copie, VEILLE, 'cron: "20 7 * * 1"', 'cron: "20 7 * * 2"')

        resultat = executer(decaler)
        self.assertEqual(resultat.returncode, 1, resultat.stdout[-2000:])
        self.assertIn("Veille hebdomadaire", resultat.stdout)


if __name__ == "__main__":
    unittest.main(verbosity=2)
