#!/usr/bin/env python3
"""Banc de mutation du relevé qualifié des lacunes et du bloc prospectif.

Une carte de lacunes qui ne serait qu'un document de plus n'apporterait rien :
le dépôt en a déjà deux. Ce qui doit être prouvé, c'est que le relevé **refuse**
de vieillir en silence. Chaque cas plante une faute réelle dans une copie
complète du dépôt et exige un échec explicite de `construire-couverture-sujets.py
--verifier` :

1. la copie intacte passe ;
2. une carte éditée à la main est refusée ;
3. une carte supprimée est refusée ;
4. un repère de difficulté modifié sans régénération est refusé ;
5. une fiche détachée du référentiel est refusée, et le message le dit ;
6. un repère hors 1–4 est refusé comme source incohérente ;
7. un statut embelli sans régénération est refusé : on ne coche pas une case
   pour faire paraître le catalogue plus complet ;
8. une carte de sujet supprimée change le relevé, donc la porte échoue ;
9. un chiffre de prospective désynchronisé est refusé ;
10. les bornes du relevé supprimées sont refusées ;
11. la note prospective absente est refusée.

Le banc éprouve le contrôle livré, pas une variante : seul `MRSC_RACINE`
change, et la copie est détruite à chaque cas.

Usage :
    python3 outils/test_mutations_couverture_sujets.py
"""

from __future__ import annotations

import contextlib
import sys
import tempfile
import unittest
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RACINE / "outils"))

import banc_mutations  # noqa: E402

OUTIL = "construire-couverture-sujets.py"
CATALOGUE = "docs/apprentissage/catalogue.toml"
REFERENTIEL = "docs/apprentissage/referentiel.toml"
CARTE = "docs/rd/couverture-sujets.md"
NOTE = "docs/rd/prospective-lacunes-2027.md"
CARTE_SUJET = "docs/rd/sujet-securite-sciences.md"
DEBUT = "<!-- DEBUT RELEVE COUVERTURE -->"


@contextlib.contextmanager
def copie_preparee(preparer=lambda copie: None):  # noqa: ANN001, ANN201 - préparation de copie
    with tempfile.TemporaryDirectory(prefix="mrsc-couverture-") as dossier:
        copie = Path(dossier) / "copie"
        banc_mutations.copie_complete(copie)
        preparer(copie)
        yield copie


def verifier(copie: Path):  # noqa: ANN201 - résultat de subprocess
    return banc_mutations.lancer(OUTIL, copie, arguments=("--verifier",))


class TestCouvertureSujets(unittest.TestCase):
    def test_copie_intacte_passe(self) -> None:
        with copie_preparee() as copie:
            resultat = verifier(copie)
            self.assertEqual(resultat.returncode, 0, resultat.stderr)

    def test_carte_editee_a_la_main_refusee(self) -> None:
        def preparer(copie: Path) -> None:
            banc_mutations.muter(copie, CARTE, "| Fiches du catalogue | 107 |", "| Fiches du catalogue | 108 |")

        with copie_preparee(preparer) as copie:
            resultat = verifier(copie)
            self.assertNotEqual(resultat.returncode, 0)
            self.assertIn("a divergé", resultat.stderr)

    def test_carte_supprimee_refusee(self) -> None:
        def preparer(copie: Path) -> None:
            banc_mutations.cible(copie, CARTE).unlink()

        with copie_preparee(preparer) as copie:
            resultat = verifier(copie)
            self.assertNotEqual(resultat.returncode, 0)
            self.assertIn("a divergé", resultat.stderr)

    def test_repere_modifie_sans_regeneration_refuse(self) -> None:
        def preparer(copie: Path) -> None:
            banc_mutations.muter(
                copie,
                CATALOGUE,
                'niveau = 4\nhorizon_contenu = "Après moyenne et médiane',
                'niveau = 2\nhorizon_contenu = "Après moyenne et médiane',
            )

        with copie_preparee(preparer) as copie:
            resultat = verifier(copie)
            self.assertNotEqual(resultat.returncode, 0)
            self.assertIn("a divergé", resultat.stderr)

    def test_fiche_detachee_du_referentiel_refusee(self) -> None:
        def preparer(copie: Path) -> None:
            banc_mutations.muter(
                copie,
                CATALOGUE,
                'id = "maths-comparer-deux-releves"',
                'id = "maths-comparer-deux-releves-bis"',
            )

        with copie_preparee(preparer) as copie:
            resultat = verifier(copie)
            self.assertNotEqual(resultat.returncode, 0)
            self.assertIn("Source de vérité incohérente", resultat.stderr)
            self.assertIn("fiche non reliée", resultat.stderr)

    def test_repere_hors_1_4_refuse(self) -> None:
        def preparer(copie: Path) -> None:
            banc_mutations.muter(
                copie,
                CATALOGUE,
                'niveau = 4\nhorizon_contenu = "Après moyenne et médiane',
                'niveau = 9\nhorizon_contenu = "Après moyenne et médiane',
            )

        with copie_preparee(preparer) as copie:
            resultat = verifier(copie)
            self.assertNotEqual(resultat.returncode, 0)
            self.assertIn("repère de difficulté hors 1–4", resultat.stderr)

    def test_statut_embelli_sans_regeneration_refuse(self) -> None:
        def preparer(copie: Path) -> None:
            banc_mutations.muter(
                copie,
                REFERENTIEL,
                'id = "argumentation"\ntitre = "Résumer, argumenter et adapter le ton au destinataire"\nstatut = "partiel"',
                'id = "argumentation"\ntitre = "Résumer, argumenter et adapter le ton au destinataire"\nstatut = "actif"',
            )

        with copie_preparee(preparer) as copie:
            resultat = verifier(copie)
            self.assertNotEqual(resultat.returncode, 0)
            self.assertIn("a divergé", resultat.stderr)

    def test_carte_de_sujet_supprimee_refusee(self) -> None:
        def preparer(copie: Path) -> None:
            banc_mutations.cible(copie, CARTE_SUJET).unlink()

        with copie_preparee(preparer) as copie:
            resultat = verifier(copie)
            self.assertNotEqual(resultat.returncode, 0)
            self.assertIn("a divergé", resultat.stderr)

    def test_releve_prospectif_desynchronise_refuse(self) -> None:
        def preparer(copie: Path) -> None:
            banc_mutations.muter(copie, NOTE, "| Fiches du catalogue | 107 |", "| Fiches du catalogue | 108 |")

        with copie_preparee(preparer) as copie:
            resultat = verifier(copie)
            self.assertNotEqual(resultat.returncode, 0)
            self.assertIn("relevé prospectif a divergé", resultat.stderr)

    def test_bornes_supprimees_refusees(self) -> None:
        def preparer(copie: Path) -> None:
            banc_mutations.muter(copie, NOTE, DEBUT, "<!-- borne effacée -->")

        with copie_preparee(preparer) as copie:
            resultat = verifier(copie)
            self.assertNotEqual(resultat.returncode, 0)
            self.assertIn("bornes", resultat.stderr)

    def test_note_prospective_absente_refusee(self) -> None:
        def preparer(copie: Path) -> None:
            banc_mutations.cible(copie, NOTE).unlink()

        with copie_preparee(preparer) as copie:
            resultat = verifier(copie)
            self.assertNotEqual(resultat.returncode, 0)
            self.assertIn("absent", resultat.stderr)


if __name__ == "__main__":
    unittest.main(verbosity=2)
