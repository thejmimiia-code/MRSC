#!/usr/bin/env python3
"""Banc de mutation de `verifier-budgets-visuels.py`.

Ce contrôle existe parce qu'aucun test ne voyait deux choses : un `<title>` trop
long, tronqué dans les résultats de recherche, et un H1 qui s'allonge sans que
personne ne le remarque à 320 px. Il lit les valeurs réellement écrites dans
`assets/css/site.css` au lieu de recopier des constantes — et rien ne prouvait
qu'il savait échouer.

Trois fautes sont plantées dans une copie complète du dépôt :

1. un `<title>` allongé bien au-delà du plafond de 60 caractères ;
2. une page privée de sa balise `<title>` ;
3. le plancher du `clamp()` de `h1` gonflé dans `site.css`, qui fait exploser le
   nombre de lignes estimées du titre d'accueil.

La géométrie du héros des mondes et la couverture des modes d'affichage ne sont
pas éprouvées ici : leurs seuils sont des estimations hors ligne, et une
mutation de `srcset` que j'ai essayée n'a pas fait échouer le contrôle — mieux
vaut l'écrire que de laisser croire que tout le fichier est couvert.

Usage :
    python3 outils/test_mutations_budgets_visuels.py
"""

from __future__ import annotations

import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RACINE / "outils"))

import banc_mutations  # noqa: E402

OUTIL = "verifier-budgets-visuels.py"


def executer(mutation) -> subprocess.CompletedProcess[str]:  # noqa: ANN001 - préparation de copie
    with tempfile.TemporaryDirectory(prefix="mrsc-budgets-") as dossier:
        copie = Path(dossier) / "copie"
        banc_mutations.copie_complete(copie)
        mutation(copie)
        return banc_mutations.lancer(OUTIL, copie)


def balise_titre(copie: Path, page: str) -> str:
    """Balise `<title>` telle qu'elle est écrite dans la copie."""
    contenu = (copie / page).read_text(encoding="utf-8")
    trouve = re.search(r"<title>.*?</title>", contenu, re.S)
    if not trouve:
        raise AssertionError(f"{page} n'a pas de <title> : le banc ne peut pas le muter")
    return trouve.group(0)


class TestBudgetsVisuels(unittest.TestCase):
    def test_copie_intacte_passe(self) -> None:
        resultat = executer(lambda copie: None)
        self.assertEqual(resultat.returncode, 0, resultat.stdout + resultat.stderr)
        self.assertIn("Budgets d'affichage", resultat.stdout)

    def test_titre_trop_long_refuse(self) -> None:
        def allonger(copie: Path) -> None:
            banc_mutations.muter(
                copie,
                "documents.html",
                balise_titre(copie, "documents.html"),
                "<title>" + "Documents " * 8 + "</title>",
            )

        resultat = executer(allonger)
        self.assertEqual(resultat.returncode, 1, resultat.stdout[-2000:])
        self.assertIn("titres trop longs", resultat.stderr)
        self.assertIn("documents.html", resultat.stderr)

    def test_page_sans_titre_refusee(self) -> None:
        def retirer(copie: Path) -> None:
            banc_mutations.muter(copie, "documents.html", balise_titre(copie, "documents.html"), "")

        resultat = executer(retirer)
        self.assertEqual(resultat.returncode, 1, resultat.stdout[-2000:])
        self.assertIn("aucune balise", resultat.stderr)

    def test_plancher_du_h1_gonfle_refuse(self) -> None:
        """Le H1 était mesuré sur des valeurs lues dans le CSS : celles-ci doivent mordre."""
        def gonfler(copie: Path) -> None:
            banc_mutations.muter(copie, "assets/css/site.css", "font-size: clamp(", "font-size: clamp(3")

        resultat = executer(gonfler)
        self.assertEqual(resultat.returncode, 1, resultat.stdout[-2000:])
        self.assertIn("H1 de l'accueil", resultat.stderr)


if __name__ == "__main__":
    unittest.main(verbosity=2)
