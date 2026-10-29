#!/usr/bin/env python3
"""Banc de `outils/etat-rd.py`, le rapport d'état de la R&D.

Ce script imprime un tableau que le brief de décision prospective cite comme
pièce justificative : « Initiatives R&D », « Fiches publiées », « Page la plus
lourde, mobile »… Il n'avait aucun test, et son pire défaut n'était pas de se
tromper, mais de **se taire**.

Avant le 29 octobre 2026 :

- un `poids-pages.md` absent ou reformaté faisait disparaître trois lignes du
  tableau, qui restait lisible — donc rassurant ;
- un journal sans entrée datée faisait disparaître la ligne d'ancienneté ;
- une fiche dont `revue_le` ne se lit pas était écartée du compte des revues
  échues : une date mal écrite rendait la fiche **moins** suivie ;
- un portefeuille absent levait une trace d'exception.

Sans ces lignes, le tableau ne dit pas « je ne sais pas » : il dit moins, et il
a l'air complet. C'est la même famille de défaut que la sentinelle réseau et le
contrôle des planches — une impossibilité qui ressemble à une bonne nouvelle.

Sept cas, sur une copie complète du dépôt :

1. copie intacte : code 0, tous les indicateurs présents, aucun « non lu » ;
2. relevé de poids supprimé : code 1, ligne « **non lu** — relevé de poids absent » ;
3. relevé de poids reformaté (tableau à trois colonnes) : code 1, et la raison dite ;
4. journal sans entrée datée : code 1, « aucune entrée datée » ;
5. une fiche au `revue_le` illisible : code 1, et la fiche est **nommée** ;
6. portefeuille supprimé : code 1, message clair, aucune trace d'exception ;
7. `--date` au-delà de l'échéance : la revue du portefeuille est dite « échue ».

Usage :
    python3 outils/test_etat_rd.py
"""

from __future__ import annotations

import re
import sys
import tempfile
import unittest
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RACINE / "outils"))

import banc_mutations  # noqa: E402

OUTIL = "etat-rd.py"
POIDS = "docs/rd/poids-pages.md"
JOURNAL = "docs/rd/journal.md"
CATALOGUE = "docs/apprentissage/catalogue.toml"
PORTEFEUILLE = "docs/rd/portefeuille.toml"


def executer(mutation=None, arguments: tuple[str, ...] = ()) -> object:  # noqa: ANN001
    """Copie complète, mutation, puis l'état réel de l'outil livré."""
    with tempfile.TemporaryDirectory(prefix="mrsc-etat-rd-") as dossier:
        copie = Path(dossier) / "copie"
        banc_mutations.copie_complete(copie)
        if mutation is not None:
            mutation(copie)
        return banc_mutations.lancer(OUTIL, copie, arguments=arguments)


def premiere_fiche_avec_revue(copie: Path) -> str:
    """Fragment exact à muter, lu dans le catalogue : rien n'est recopié ici."""
    texte = (copie / CATALOGUE).read_text(encoding="utf-8")
    trouve = re.search(r'revue_le = "(\d{4}-\d{2}-\d{2})"', texte)
    if not trouve:
        raise AssertionError("aucune fiche datée au catalogue : le banc ne peut pas muter")
    return trouve.group(1)


class TestEtatRd(unittest.TestCase):
    def test_copie_intacte_rend_le_tableau_complet(self) -> None:
        resultat = executer()
        self.assertEqual(resultat.returncode, 0, resultat.stdout + resultat.stderr)
        self.assertIn("| Initiatives R&D |", resultat.stdout)
        self.assertIn("| Fiches publiées |", resultat.stdout)
        self.assertIn("| Dernière entrée de journal |", resultat.stdout)
        self.assertIn("| Pages mesurées |", resultat.stdout)
        self.assertIn("| Page la plus lourde, mobile |", resultat.stdout)
        self.assertNotIn("non lu", resultat.stdout)
        self.assertNotIn("État incomplet", resultat.stdout)
        # Le rappel de portée reste attaché au tableau : un compte n'est pas une preuve.
        self.assertIn("Ce que ces chiffres ne mesurent pas", resultat.stdout)

    def test_releve_de_poids_absent_est_nomme(self) -> None:
        def supprimer(copie: Path) -> None:
            (copie / POIDS).unlink()

        resultat = executer(supprimer)
        self.assertEqual(resultat.returncode, 1, resultat.stdout)
        self.assertIn("**non lu** — relevé de poids absent", resultat.stdout)
        self.assertIn("**État incomplet :** 1 raison(s)", resultat.stdout)
        # Le pire serait de garder l'air complet : plus de ligne de poids sans le dire.
        self.assertNotIn("| Page la plus lourde, mobile |", resultat.stdout)

    def test_releve_de_poids_reformate_est_refuse(self) -> None:
        """Trois colonnes au lieu de quatre : le tableau ne se lit plus."""
        def reformater(copie: Path) -> None:
            chemin = copie / POIDS
            chemin.write_text(
                "# Poids estimé des pages publiques\n\n"
                "| Page | Mobile | Grand écran |\n| --- | ---: | ---: |\n"
                "| `index.html` | 154.4 | 252.8 |\n",
                encoding="utf-8",
            )

        resultat = executer(reformater)
        self.assertEqual(resultat.returncode, 1, resultat.stdout)
        self.assertIn("aucune ligne de tableau exploitable", resultat.stdout)
        self.assertIn("État incomplet", resultat.stdout)

    def test_journal_sans_entree_datee_est_nomme(self) -> None:
        def effacer_les_dates(copie: Path) -> None:
            chemin = copie / JOURNAL
            texte = chemin.read_text(encoding="utf-8")
            chemin.write_text(re.sub(r"(?m)^## \d{4}-\d{2}-\d{2}", "## Sans date", texte), encoding="utf-8")

        resultat = executer(effacer_les_dates)
        self.assertEqual(resultat.returncode, 1, resultat.stdout)
        self.assertIn("aucune entrée datée dans le journal", resultat.stdout)
        self.assertNotIn("| Dernière entrée de journal |", resultat.stdout)

    def test_fiche_a_date_illisible_est_nommee(self) -> None:
        """Une date mal écrite ne doit pas retirer la fiche du suivi en silence."""
        def casser_une_date(copie: Path) -> None:
            chemin = copie / CATALOGUE
            texte = chemin.read_text(encoding="utf-8")
            banc_mutations.muter(copie, CATALOGUE, f'revue_le = "{premiere_fiche_avec_revue(copie)}"', 'revue_le = "2026-13-45"')

        resultat = executer(casser_une_date)
        self.assertEqual(resultat.returncode, 1, resultat.stdout)
        self.assertIn("| Revues non calculables | 1 :", resultat.stdout)
        self.assertIn("fr-lire-consigne", resultat.stdout)

    def test_portefeuille_absent_est_un_manque_pas_un_plantage(self) -> None:
        def supprimer(copie: Path) -> None:
            (copie / PORTEFEUILLE).unlink()

        resultat = executer(supprimer)
        self.assertEqual(resultat.returncode, 1, resultat.stdout)
        self.assertIn("**non lu** — fichier absent : portefeuille.toml", resultat.stdout)
        self.assertNotIn("Traceback", resultat.stderr)
        self.assertNotIn("Traceback", resultat.stdout)

    def test_echeance_calculee_depuis_la_date_demandee(self) -> None:
        """`--date` doit compter les jours, et dire « échue » au-delà.

        Aucune date d'échéance n'est recopiée ici : le jour de référence est
        celui d'aujourd'hui, et 2056 est au-delà de toute échéance déclarée par
        le portefeuille. Ce qui est vérifié, c'est le calcul, pas une valeur.
        """
        resultat = executer()
        self.assertEqual(resultat.returncode, 0, resultat.stdout)
        self.assertRegex(resultat.stdout, r"\(dans \d+ jour\(s\)\)")
        self.assertNotIn("(échue)", resultat.stdout)

        resultat = executer(arguments=("--date", "2056-01-01"))
        self.assertEqual(resultat.returncode, 0, resultat.stdout)
        self.assertIn("| Revue du portefeuille |", resultat.stdout)
        self.assertIn("(échue)", resultat.stdout)
        # La même exécution garde un journal d'une ancienneté calculée, pas figée.
        self.assertRegex(resultat.stdout, r"\| Dernière entrée de journal \| \d{4}-\d{2}-\d{2} \(\d+ jour\(s\)\) \|")


if __name__ == "__main__":
    unittest.main(verbosity=2)
