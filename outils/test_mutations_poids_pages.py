#!/usr/bin/env python3
"""Banc de mutation de `verifier-poids-pages.py`, la promesse publique de sobriété.

Le site affiche des budgets de poids — 300 Kio mobile, 450 Kio grand écran, gzip
estimé — et rien ne prouvait que le contrôle qui les fait respecter savait
refuser quoi que ce soit. C'est la promesse la plus facile à contredire sans le
voir : il suffit d'ajouter une illustration lourde pour qu'une page double, et
l'ancien vert resterait vert si le calcul se trompait.

Quatre fautes sont plantées, chacune dans une copie complète du dépôt :

1. une image lourde de 400 Kio, référencée par l'accueil — le budget mobile
   (300 Kio) est dépassé ;
2. une ressource locale absente, référencée par une page ;
3. un `<picture>` dont le repli n'existe pas ;
4. le budget lui-même : la même copie intacte, lancée avec `--budget-mobile 1`,
   doit signaler un dépassement — sans quoi rien ne prouverait que le seuil est
   appliqué plutôt que décoratif.

Usage :
    python3 outils/test_mutations_poids_pages.py
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

OUTIL = "verifier-poids-pages.py"
FIN_PAGE = "</body>\n"


def executer(mutation, *arguments: str):  # noqa: ANN001, ANN201 - préparation de copie
    with tempfile.TemporaryDirectory(prefix="mrsc-poids-") as dossier:
        copie = Path(dossier) / "copie"
        banc_mutations.copie_complete(copie)
        if mutation is not None:
            mutation(copie)
        return banc_mutations.lancer(OUTIL, copie, arguments=arguments)


def ajouter_html(balise: str):  # noqa: ANN202 - fabrique de mutation
    def mutation(copie: Path) -> None:
        banc_mutations.muter(copie, "index.html", FIN_PAGE, balise + "\n" + FIN_PAGE)

    return mutation


class TestPoidsPages(unittest.TestCase):
    def test_copie_intacte_passe(self) -> None:
        resultat = executer(None)
        self.assertEqual(resultat.returncode, 0, resultat.stdout + resultat.stderr)
        self.assertIn("sous les budgets de travail", resultat.stdout)

    def test_image_lourde_fait_echouer_le_budget(self) -> None:
        """400 Kio incompressibles : le budget mobile de 300 Kio doit céder."""

        def ajouter(copie: Path) -> None:
            (copie / "assets" / "images" / "lourde.png").write_bytes(os.urandom(400 * 1024))
            balise = '<img src="assets/images/lourde.png" alt="">'
            banc_mutations.muter(copie, "index.html", FIN_PAGE, balise + "\n" + FIN_PAGE)

        resultat = executer(ajouter)
        self.assertEqual(resultat.returncode, 1, resultat.stdout[-2000:])
        self.assertIn("index.html :", resultat.stderr)
        self.assertIn("Kio mobile > 300 Kio", resultat.stderr)

    def test_ressource_absente_refusee(self) -> None:
        resultat = executer(ajouter_html('<img src="assets/images/absente.png" alt="">'))
        self.assertEqual(resultat.returncode, 1, resultat.stdout[-2000:])
        self.assertIn("ressource locale absente", resultat.stderr)
        self.assertIn("assets/images/absente.png", resultat.stderr)

    def test_picture_sans_repli_refuse(self) -> None:
        """Un `<picture>` sans source exploitable n'a pas d'alternative : le contrôle doit le dire."""
        resultat = executer(ajouter_html('<picture><img alt="sans image" src=""></picture>'))
        self.assertEqual(resultat.returncode, 1, resultat.stdout[-2000:])
        self.assertIn("picture> sans image de repli", resultat.stderr)

    def test_budget_abaisse_refuse_la_copie_intacte(self) -> None:
        """Le seuil est un contrôle, pas un commentaire : à 1 Kio, rien ne passe."""
        resultat = executer(None, "--budget-mobile", "1")
        self.assertEqual(resultat.returncode, 1, resultat.stdout[-2000:])
        self.assertIn("Kio mobile > 1 Kio", resultat.stderr)


if __name__ == "__main__":
    unittest.main(verbosity=2)
