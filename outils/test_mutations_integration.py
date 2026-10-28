#!/usr/bin/env python3
"""Banc de mutation de `verifier-integration.py`, la dernière porte sans preuve.

Mille six cents lignes, seize routes exercées en montant les fonctions de `api/`
comme le fait Vercel, un contrôle qui compare les nombres écrits en prose au
catalogue réel, et un autre qui refuse une ressource publiée que plus rien
n'appelle. Rien n'éprouvait cette porte ailleurs que par son propre vert.

Trois fautes sont plantées dans une copie complète du dépôt :

1. une ressource ajoutée à `assets/` que rien ne cite — le cas d'un fichier livré
   que le site ne demande jamais ;
2. un nombre annoncé dans `apprendre.html` qui ne correspond plus au catalogue ;
3. une page publique supprimée du dépôt.

Ce banc est le plus lent du dépôt : `verifier-integration.py` lance lui-même
quatre outils et monte un serveur, soit une vingtaine de secondes par exécution.
Trois fautes suffisent — elles couvrent les trois familles que la porte vérifie
elle-même : le périmètre publié, les chiffres recalculés, la présence des pages.
Les routes HTTP, elles, ont déjà leur propre contrôle (`verifier-securite.py`).

Usage :
    python3 outils/test_mutations_integration.py
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

OUTIL = "verifier-integration.py"


def executer(mutation) -> subprocess.CompletedProcess[str]:  # noqa: ANN001 - fonction de préparation
    """Copie complète, une faute préparée dans la copie, puis la porte réelle."""
    with tempfile.TemporaryDirectory(prefix="mrsc-integration-") as dossier:
        copie = Path(dossier) / "copie"
        banc_mutations.copie_complete(copie)
        mutation(copie)
        return banc_mutations.lancer(OUTIL, copie)


class TestIntegration(unittest.TestCase):
    def test_copie_intacte_passe(self) -> None:
        resultat = executer(lambda copie: None)
        self.assertEqual(resultat.returncode, 0, resultat.stdout[-2000:] + resultat.stderr[-2000:])
        self.assertIn("Tous les contrôles passent", resultat.stdout)

    def test_ressource_orpheline_refusee(self) -> None:
        """Un fichier livré que rien ne cite : la panne est silencieuse, donc à voir."""

        def ajouter(copie: Path) -> None:
            (copie / "assets" / "images" / "orpheline.png").write_bytes(b"\x89PNG orpheline")

        resultat = executer(ajouter)
        self.assertEqual(resultat.returncode, 1, resultat.stdout[-2000:])
        self.assertIn("orphelines : assets/images/orpheline.png", resultat.stdout)

    def test_chiffre_annonce_faux_refuse(self) -> None:
        """Le total est recalculé depuis `catalogue.toml`, jamais recopié : il doit mordre."""

        def mentir(copie: Path) -> None:
            banc_mutations.muter(
                copie,
                "apprendre.html",
                "85 fiches du catalogue à 15 univers",
                "86 fiches du catalogue à 15 univers",
            )

        resultat = executer(mentir)
        self.assertEqual(resultat.returncode, 1, resultat.stdout[-2000:])
        self.assertIn("Les nombres annoncés dans apprendre.html", resultat.stdout)
        self.assertIn("ÉCHEC", resultat.stdout)

    def test_page_publique_absente_refusee(self) -> None:
        resultat = executer(lambda copie: (copie / "eva.html").unlink())
        self.assertEqual(resultat.returncode, 1, resultat.stdout[-2000:])
        self.assertIn("ÉCHEC Page présente : eva.html", resultat.stdout)


if __name__ == "__main__":
    unittest.main(verbosity=2)
