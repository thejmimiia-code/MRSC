#!/usr/bin/env python3
"""Banc de mutation de `relecture-agent-prototypes.py`.

Dix fautes sont plantées dans une copie complète du dépôt : une relecture
retirée, une source ouverte inventée, une validation humaine revendiquée,
un compte arithmétique embelli, un repère du rapport effacé, une écriture dans
le registre humain, une fiche promue sans registre, une consignation tentée
depuis une racine de banc — et une copie intacte, qui doit passer.

Le banc ne prouve pas que la relecture de contenu est bonne ; il prouve que la
porte refuse les sept manières les plus tentatrices de la raconter à tort.

Usage :
    python3 outils/test_mutations_relecture_agent_prototypes.py
"""

from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RACINE / "outils"))

import banc_mutations  # noqa: E402

OUTIL = "relecture-agent-prototypes.py"
REGISTRE = "docs/rd/relecture-agent-prototypes.toml"
RAPPORT = "docs/rd/relecture-agent-prototypes-2026-11-10.md"
CATALOGUE = "docs/apprentissage/catalogue.toml"
REGISTRE_HUMAIN = "docs/apprentissage/relectures.toml"


def executer(mutation, arguments=()):  # noqa: ANN001 - préparation de copie
    with tempfile.TemporaryDirectory(prefix="mrsc-relecture-agent-") as dossier:
        copie = Path(dossier) / "copie"
        banc_mutations.copie_complete(copie)
        mutation(copie)
        return banc_mutations.lancer(OUTIL, copie, arguments=arguments)


class TestRelectureAgentPrototypes(unittest.TestCase):
    def test_copie_intacte_passe(self) -> None:
        resultat = executer(lambda copie: None)
        self.assertEqual(resultat.returncode, 0, resultat.stdout + resultat.stderr)
        self.assertIn("aucune validation humaine revendiquée", resultat.stdout)

    def test_relecture_retiree_refusee(self) -> None:
        def retirer(copie: Path) -> None:
            chemin = banc_mutations.cible(copie, REGISTRE)
            texte = chemin.read_text(encoding="utf-8")
            debut = texte.find("[[relecture]]")
            suivant = texte.find("[[relecture]]", debut + 1)
            self.assertGreater(debut, 0)
            self.assertGreater(suivant, debut)
            chemin.write_text(texte[:debut] + texte[suivant:], encoding="utf-8")

        resultat = executer(retirer)
        self.assertEqual(resultat.returncode, 1, resultat.stdout + resultat.stderr)
        self.assertIn("prototypes sans relecture consignée", resultat.stderr)

    def test_source_ouverte_inventee_refusee(self) -> None:
        def inventer(copie: Path) -> None:
            banc_mutations.muter(
                copie, REGISTRE,
                'sources_ouvertes = ["Carey, Steiner et Petri — Ten simple rules for reading a scientific paper, PLOS Computational Biology (2020)"]',
                'sources_ouvertes = ["Source inventée par le banc"]',
            )

        resultat = executer(inventer)
        self.assertEqual(resultat.returncode, 1, resultat.stdout + resultat.stderr)
        self.assertIn("source ouverte inventée", resultat.stderr)

    def test_validation_humaine_revendiquee_refusee(self) -> None:
        def revendiquer(copie: Path) -> None:
            banc_mutations.muter(
                copie, REGISTRE,
                "Conserver le statut « Prototype à relire ».",
                "Validation humaine obtenue. Conserver le statut « Prototype à relire ».",
            )

        resultat = executer(revendiquer)
        self.assertEqual(resultat.returncode, 1, resultat.stdout + resultat.stderr)
        self.assertIn("formulation interdite", resultat.stderr)

    def test_arithmetique_embellie_refusee(self) -> None:
        def embellir(copie: Path) -> None:
            banc_mutations.muter(
                copie, REGISTRE,
                "0 expression(s) arithmétique(s) simple(s) recalculée(s) sans écart",
                "99 expression(s) arithmétique(s) simple(s) recalculée(s) sans écart",
            )

        resultat = executer(embellir)
        self.assertEqual(resultat.returncode, 1, resultat.stdout + resultat.stderr)
        self.assertIn("nombre d’expressions recalculées annoncé à tort", resultat.stderr)

    def test_repere_du_rapport_efface_refuse(self) -> None:
        def effacer(copie: Path) -> None:
            banc_mutations.muter(copie, RAPPORT, "81 / 81", "80 / 81")

        resultat = executer(effacer)
        self.assertEqual(resultat.returncode, 1, resultat.stdout + resultat.stderr)
        self.assertIn("repère absent", resultat.stderr)

    def test_registre_humain_ecrit_refuse(self) -> None:
        def ecrire(copie: Path) -> None:
            chemin = banc_mutations.cible(copie, REGISTRE_HUMAIN)
            with chemin.open("a", encoding="utf-8") as flux:
                flux.write(
                    "\n[[relecture]]\n"
                    'fiche = "recherche-lire-etude"\n'
                    "date = 2026-11-10\n"
                    'role = "faute plantée par le banc"\n'
                    'perimetre = ["sources"]\n'
                    'verdict = "a-corriger"\n'
                    "sources_ouvertes = []\n"
                    "droits_verifies_le = 2026-11-10\n"
                    'objections = ["faute plantée"]\n'
                    "points_bloquants = []\n"
                    'suite = "rien"\n'
                )

        resultat = executer(ecrire)
        self.assertEqual(resultat.returncode, 1, resultat.stdout + resultat.stderr)
        self.assertIn("un agent n’y écrit jamais", resultat.stderr)

    def test_statut_promu_sans_registre_refuse(self) -> None:
        def promouvoir(copie: Path) -> None:
            banc_mutations.muter(
                copie, CATALOGUE,
                'statut_editorial = "Prototype à relire"',
                'statut_editorial = "Relu — relecture consignée"',
            )

        resultat = executer(promouvoir)
        self.assertEqual(resultat.returncode, 1, resultat.stdout + resultat.stderr)
        self.assertIn("statuts promus sans registre humain", resultat.stderr)

    def test_champ_editorial_retire_refuse(self) -> None:
        def retirer(copie: Path) -> None:
            banc_mutations.muter(
                copie, CATALOGUE,
                'transferer = "Cette grille peut aider à lire une ',
                'transfert_inconnu = "Cette grille peut aider à lire une ',
            )

        resultat = executer(retirer)
        self.assertEqual(resultat.returncode, 1, resultat.stdout + resultat.stderr)
        self.assertIn("champ éditorial absent ou vide : transferer", resultat.stderr)

    def test_consigner_depuis_un_banc_refuse(self) -> None:
        resultat = executer(lambda copie: None, arguments=("--consigner",))
        self.assertEqual(resultat.returncode, 1, resultat.stdout + resultat.stderr)
        self.assertIn("refuse d’écrire", resultat.stderr)


if __name__ == "__main__":
    unittest.main(verbosity=2)
