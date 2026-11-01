#!/usr/bin/env python3
"""Banc de `verifier-plan-eva.py` : chaque refus doit mordre.

Neuf cas, tous dans une copie jetable du dépôt (le plan est lu, jamais exécuté,
et les mutations portent sur `plan.toml`, le portefeuille et le journal) :

1. le plan livré passe ;
2. une phase « faite » dont le test n'existe pas est refusée ;
3. une phase « faite » que le journal ne raconte pas est refusée ;
4. une phase « hors-portée » sans condition est refusée — un abandon déguisé ;
5. une condition trop courte est refusée (le refus doit dire ce qui le lèverait) ;
6. un cycle de dépendances est refusé ;
7. une dépendance inconnue est refusée ;
8. une branche du portefeuille que le plan ne sert pas est refusée ;
9. un plan illisible sort en code 2, sans trace d'exception.

Usage :
    python3 outils/test_verifier_plan_eva.py
"""

from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RACINE / "outils"))

import banc_mutations  # noqa: E402

OUTIL = "verifier-plan-eva.py"
PLAN = "docs/rd/eva/plan.toml"
JOURNAL = "docs/rd/journal.md"


def executer(mutations=()):
    """Rejoue le contrôle dans une copie, avec les mutations demandées."""
    with tempfile.TemporaryDirectory(prefix="mrsc-plan-eva-") as dossier:
        copie = Path(dossier)
        banc_mutations.copie_jetable(copie)
        for mutation in mutations:
            banc_mutations.muter(copie, *mutation)
        return banc_mutations.lancer(OUTIL, copie)


class TestVerifierPlanEva(unittest.TestCase):
    def test_le_plan_livre_passe(self) -> None:
        resultat = executer()
        self.assertEqual(resultat.returncode, 0, resultat.stdout + resultat.stderr)
        self.assertIn("Plan d'ÉVA cohérent", resultat.stdout)
        self.assertIn("aucune capacité sans test", resultat.stdout)

    def test_phase_faite_sans_test_refusee(self) -> None:
        resultat = executer(
            [(PLAN, 'test = "outils/test_memoire_eva.py"', 'test = "outils/test-qui-n-existe-pas.py"')]
        )
        self.assertEqual(resultat.returncode, 1, resultat.stdout)
        self.assertIn("absent du dépôt", resultat.stderr)

    def test_phase_faite_sans_citation_au_journal_refusee(self) -> None:
        """Le journal est la mémoire : une phase qu'il ignore n'a pas d'histoire."""
        resultat = executer(
            [(JOURNAL, "memoire-trois-horizons", "phase-sans-trace")]
        )
        self.assertEqual(resultat.returncode, 1, resultat.stdout)
        self.assertIn("sans citation de la phase dans le journal", resultat.stderr)

    def test_hors_portee_sans_condition_refuse(self) -> None:
        texte = (RACINE / PLAN).read_text(encoding="utf-8")
        bloc = texte.split("[[phase]]")
        cible = next(b for b in bloc if 'id = "conscience-et-corps"' in b)
        condition = next(l for l in cible.splitlines() if l.startswith("condition = "))
        resultat = executer([(PLAN, condition + "\n", "")])
        self.assertEqual(resultat.returncode, 1, resultat.stdout)
        self.assertIn("sans condition de révision", resultat.stderr)

    def test_condition_trop_courte_refusee(self) -> None:
        texte = (RACINE / PLAN).read_text(encoding="utf-8")
        bloc = texte.split("[[phase]]")
        cible = next(b for b in bloc if 'id = "conscience-et-corps"' in b)
        condition = next(l for l in cible.splitlines() if l.startswith("condition = "))
        resultat = executer([(PLAN, condition, 'condition = "plus tard"')])
        self.assertEqual(resultat.returncode, 1, resultat.stdout)
        self.assertIn("40 caractères", resultat.stderr)

    def test_cycle_de_dependances_refuse(self) -> None:
        resultat = executer(
            # `memoire-trois-horizons` ne dépend de rien ; la faire dépendre d'une
            # phase qui dépend d'elle ferme la boucle par les deux bouts.
            [(PLAN, "depends_on = []", 'depends_on = ["rappel-mesure"]')]
        )
        self.assertEqual(resultat.returncode, 1, resultat.stdout)
        self.assertIn("cycle de dépendances", resultat.stderr)

    def test_dependance_inconnue_refusee(self) -> None:
        resultat = executer([(PLAN, 'depends_on = ["memoire-trois-horizons"]', 'depends_on = ["phase-fantome"]')])
        self.assertEqual(resultat.returncode, 1, resultat.stdout)
        self.assertIn("dépendance inconnue", resultat.stderr)

    def test_branche_non_servie_refusee(self) -> None:
        """Les dix-neuf branches du portefeuille doivent apparaître quelque part."""
        texte = (RACINE / PLAN).read_text(encoding="utf-8")
        with tempfile.TemporaryDirectory(prefix="mrsc-plan-eva-") as dossier:
            # **Vraie** copie, pas des liens : `copie_jetable` lie `docs/` en
            # entier, et écrire `copie/docs/rd/eva/plan.toml` écrivait dans le
            # dépôt. C'est arrivé le 1er novembre 2026 en écrivant ce banc, et
            # le plan du dépôt s'est retrouvé mutilé — la garde contre les liens
            # symboliques n'est pas une précaution de style.
            copie = Path(dossier) / "depot"
            banc_mutations.copie_complete(copie)
            (copie / PLAN).write_text(
                texte.replace('"relire-les-44-prototypes", "co-conception-et-essais"', '"relire-les-44-prototypes"'),
                encoding="utf-8",
            )
            resultat = banc_mutations.lancer(OUTIL, copie)
        self.assertEqual(resultat.returncode, 1, resultat.stdout)
        self.assertIn("servies par aucune phase", resultat.stderr)
        self.assertIn("co-conception-et-essais", resultat.stderr)

    def test_plan_illisible_sort_en_code_2(self) -> None:
        resultat = executer([(PLAN, "[[phase]]", "[[phase")])
        self.assertEqual(resultat.returncode, 2, resultat.stdout)
        self.assertIn("illisible", resultat.stderr)
        self.assertNotIn("Traceback", resultat.stderr)


if __name__ == "__main__":
    unittest.main(verbosity=2)
