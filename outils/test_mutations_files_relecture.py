#!/usr/bin/env python3
"""Banc de mutation des deux outils qui construisent la file de relecture.

`outils/file-relecture.py` et `outils/construire-paquets-relecture.py` ne relisent
rien : ils fabriquent la file de travail qu'une personne devra suivre pour les
59 prototypes. Leur seule garde était `--verifier`, c'est-à-dire la comparaison
du fichier commité avec sa régénération — et rien ne prouvait que cette
comparaison savait refuser, ni que le tri par mots-clés classait encore quelque
chose.

Les deux outils partagent le même module de tri, donc le même banc : deux bancs
séparés finiraient par diverger sur ce qu'ils considèrent comme la vérité.

Cinq cas sont éprouvés dans une copie complète du dépôt :

1. le catalogue change sans que la file soit régénérée → `--verifier` refuse ;
2. même chose pour les paquets ;
3. la file est supprimée → `--verifier` refuse en la nommant ;
4. la file est éditée à la main (une ligne modifiée) → `--verifier` refuse ;
5. **le tri doit classer** : une fiche ajoutée au catalogue, porteuse du mot
   « vaccin » dans un domaine neutre, doit apparaître avec son motif et être
   rangée « hors domaine sensible, signalé par mots-clés ». Sans ce cas, un tri
   silencieusement cassé resterait vert.

Usage :
    python3 outils/test_mutations_files_relecture.py
"""

from __future__ import annotations

import contextlib
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RACINE / "outils"))

import banc_mutations  # noqa: E402

FILE_RELECTURE = "file-relecture.py"
PAQUETS = "construire-paquets-relecture.py"
CATALOGUE = "docs/apprentissage/catalogue.toml"
FILE_MD = "docs/apprentissage/file-relecture.md"
PAQUETS_MD = "docs/apprentissage/paquets-relecture.md"
IDENTIFIANT_NEUF = "banc-vaccin-a-relire"


@contextlib.contextmanager
def copie_preparee(preparer=lambda copie: None):  # noqa: ANN001, ANN201 - préparation de copie
    """Copie complète du dépôt, préparée, détruite en sortie de contexte."""
    with tempfile.TemporaryDirectory(prefix="mrsc-relecture-") as dossier:
        copie = Path(dossier) / "copie"
        banc_mutations.copie_complete(copie)
        preparer(copie)
        yield copie


def ajouter_fiche(copie: Path) -> None:
    """Ajoute un prototype neutre dont le titre porte un mot-clé de santé.

    La fiche est recopiée d'un prototype existant : le catalogue a une forme
    stricte, et inventer une entrée à la main ferait échouer le banc pour une
    raison qui n'a rien à voir avec ce qu'il éprouve.
    """
    catalogue = (copie / CATALOGUE).read_text(encoding="utf-8")
    blocs = catalogue.split("[[fiche]]")
    modele = next(bloc for bloc in blocs if 'statut_editorial = "Prototype à relire"' in bloc)
    lignes = modele.splitlines()
    lignes[1] = f'id = "{IDENTIFIANT_NEUF}"'
    neuf = "\n".join(lignes)
    neuf = re.sub(r'titre = ".*?"', 'titre = "Comprendre un vaccin et sa notice"', neuf, count=1)
    neuf = re.sub(r'domaine = ".*?"', 'domaine = "langue-communication"', neuf, count=1)
    (copie / CATALOGUE).write_text(catalogue + "[[fiche]]" + neuf + "\n", encoding="utf-8")


class TestFilesRelecture(unittest.TestCase):
    def test_copie_intacte_passe(self) -> None:
        with copie_preparee() as copie:
            for outil in (FILE_RELECTURE, PAQUETS):
                resultat = banc_mutations.lancer(outil, copie, arguments=("--verifier",))
                self.assertEqual(resultat.returncode, 0, outil + resultat.stderr)

    def test_catalogue_change_sans_regeneration_refuse(self) -> None:
        def changer(copie: Path) -> None:
            blocs = (copie / CATALOGUE).read_text(encoding="utf-8").split("[[fiche]]")
            modele = next(bloc for bloc in blocs if 'statut_editorial = "Prototype à relire"' in bloc)
            ancien = next(ligne for ligne in modele.splitlines() if ligne.startswith("titre = "))
            banc_mutations.muter(
                copie,
                CATALOGUE,
                ancien,
                'titre = "Un titre changé sans régénérer la file de relecture"',
            )

        with copie_preparee(changer) as copie:
            for outil in (FILE_RELECTURE, PAQUETS):
                resultat = banc_mutations.lancer(outil, copie, arguments=("--verifier",))
                self.assertEqual(resultat.returncode, 1, outil + resultat.stdout)
                self.assertIn("a divergé", resultat.stderr)

    def test_file_supprimee_refusee(self) -> None:
        with copie_preparee(lambda copie: (copie / FILE_MD).unlink()) as copie:
            resultat = banc_mutations.lancer(FILE_RELECTURE, copie, arguments=("--verifier",))
        self.assertEqual(resultat.returncode, 1, resultat.stdout)
        self.assertIn("absent", resultat.stderr)

    def test_file_editee_a_la_main_refusee(self) -> None:
        """Le cas d'une correction faite dans le Markdown : elle serait écrasée sans bruit."""
        with copie_preparee() as copie:
            banc_mutations.muter(
                copie,
                FILE_MD,
                "Régénérer avec `python3 outils/file-relecture.py`",
                "Régénérer à la main, ce fichier est libre",
            )
            resultat = banc_mutations.lancer(FILE_RELECTURE, copie, arguments=("--verifier",))
        self.assertEqual(resultat.returncode, 1, resultat.stdout)
        self.assertIn("a divergé", resultat.stderr)

    def test_fiche_sensible_hors_domaine_est_classee(self) -> None:
        """Le tri doit mordre : sans lui, la file resterait verte et muette."""
        with copie_preparee(ajouter_fiche) as copie:
            genere = banc_mutations.lancer(FILE_RELECTURE, copie)
            self.assertEqual(genere.returncode, 0, genere.stderr)
            file_md = (copie / FILE_MD).read_text(encoding="utf-8")
            genere_paquets = banc_mutations.lancer(PAQUETS, copie)
            self.assertEqual(genere_paquets.returncode, 0, genere_paquets.stderr)
            paquets_md = (copie / PAQUETS_MD).read_text(encoding="utf-8")

        lignes = [ligne for ligne in file_md.splitlines() if IDENTIFIANT_NEUF in ligne]
        self.assertEqual(len(lignes), 1, "la fiche ajoutée n'apparaît pas une fois dans la file")
        self.assertIn("santé : vaccin", lignes[0])
        self.assertIn(IDENTIFIANT_NEUF, paquets_md)
        self.assertIn("hors domaine sensible, signalé par mots-clés", paquets_md)


if __name__ == "__main__":
    unittest.main(verbosity=2)
