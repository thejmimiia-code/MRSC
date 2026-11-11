#!/usr/bin/env python3
"""Banc de mutation de `verifier-sources-ouvertes.py`.

Onze situations sont plantées dans une copie complète du dépôt : une copie
intacte, une ouverture retirée, une page d’erreur embellie en contenu, une
source ouverte inventée, un compte falsifié, une URL externe recopiée, une
écriture dans le registre des seules relectures humaines, une lecture du
complément retirée, un accueil IGN déclaré résolu, l’accueil IGN raconté comme
une page lue et une réponse HTTP 403 embellie en contenu. Les dix fautes doivent
être refusées en les nommant ; la copie intacte doit rester verte.

Le banc ne prouve pas que les pages Web sont vraies. Il prouve que le registre
du 11 novembre 2026 et son complément ne peuvent pas raconter ces pages à tort.

Usage :
    python3 outils/test_mutations_sources_ouvertes.py
"""

from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RACINE / "outils"))

import banc_mutations  # noqa: E402

OUTIL = "verifier-sources-ouvertes.py"
LEDGER = "docs/rd/sources-ouvertes-2026-11-11.toml"
RAPPORT = "docs/rd/sources-ouvertes-2026-11-11.md"
REGISTRE_AGENT = "docs/rd/relecture-agent-prototypes.toml"
REGISTRE_HUMAIN = "docs/apprentissage/relectures.toml"
COMPLEMENT = "docs/rd/sources-complement-2026-11-11.toml"
TROISIEME = "docs/rd/sources-ign-2026-11-11.toml"


def executer(mutation):  # noqa: ANN001 - préparation de copie
    with tempfile.TemporaryDirectory(prefix="mrsc-sources-ouvertes-") as dossier:
        copie = Path(dossier) / "copie"
        banc_mutations.copie_complete(copie)
        mutation(copie)
        return banc_mutations.lancer(OUTIL, copie)


class TestVerifierSourcesOuvertes(unittest.TestCase):
    def test_copie_intacte_passe(self) -> None:
        resultat = executer(lambda copie: None)
        self.assertEqual(resultat.returncode, 0, resultat.stdout + resultat.stderr)
        self.assertIn("Sources ouvertes vérifiées", resultat.stdout)

    def test_ouverture_retiree_refusee(self) -> None:
        def retirer(copie: Path) -> None:
            chemin = banc_mutations.cible(copie, LEDGER)
            texte = chemin.read_text(encoding="utf-8")
            debut = texte.find("[[ouverture]]")
            suivant = texte.find("[[ouverture]]", debut + 1)
            self.assertGreater(debut, 0)
            self.assertGreater(suivant, debut)
            chemin.write_text(texte[:debut] + texte[suivant:], encoding="utf-8")

        resultat = executer(retirer)
        self.assertEqual(resultat.returncode, 1, resultat.stdout + resultat.stderr)
        self.assertIn("adresse de source absente du registre", resultat.stderr)

    def test_statut_embelli_refuse(self) -> None:
        def embellir(copie: Path) -> None:
            banc_mutations.muter(
                copie, LEDGER,
                'statut = "page-erreur-servie"',
                'statut = "contenu"',
            )

        resultat = executer(embellir)
        self.assertEqual(resultat.returncode, 1, resultat.stdout + resultat.stderr)
        self.assertIn("statut de source embelli", resultat.stderr)

    def test_source_ouverte_inventee_refusee(self) -> None:
        def inventer(copie: Path) -> None:
            banc_mutations.muter(
                copie, REGISTRE_AGENT,
                "sources_ouvertes = [",
                'sources_ouvertes = ["Source inventée par le banc", ',
            )

        resultat = executer(inventer)
        self.assertEqual(resultat.returncode, 1, resultat.stdout + resultat.stderr)
        self.assertIn("source ouverte inventée", resultat.stderr)

    def test_compte_registre_falsifie_refuse(self) -> None:
        def falsifier(copie: Path) -> None:
            banc_mutations.muter(
                copie, REGISTRE_AGENT,
                "sources_non_ouvertes = 0",
                "sources_non_ouvertes = 99",
            )

        resultat = executer(falsifier)
        self.assertEqual(resultat.returncode, 1, resultat.stdout + resultat.stderr)
        self.assertIn("sources_non_ouvertes incohérent", resultat.stderr)

    def test_url_externe_recopiee_refusee(self) -> None:
        def recopier(copie: Path) -> None:
            banc_mutations.muter(
                copie, RAPPORT,
                "Aucune URL externe nouvelle ;",
                "https://exemple.test/ Aucune URL externe nouvelle ;",
            )

        resultat = executer(recopier)
        self.assertEqual(resultat.returncode, 1, resultat.stdout + resultat.stderr)
        self.assertIn("URL externe recopiée", resultat.stderr)

    def test_registre_humain_ecrit_refuse(self) -> None:
        def ecrire(copie: Path) -> None:
            chemin = banc_mutations.cible(copie, REGISTRE_HUMAIN)
            with chemin.open("a", encoding="utf-8") as flux:
                flux.write(
                    "\n[[relecture]]\n"
                    'fiche = "recherche-lire-etude"\n'
                    "date = 2026-11-11\n"
                    'role = "faute plantée par le banc"\n'
                    'perimetre = ["sources"]\n'
                    'verdict = "a-corriger"\n'
                    "sources_ouvertes = []\n"
                    "droits_verifies_le = 2026-11-11\n"
                    'objections = ["faute plantée"]\n'
                    "points_bloquants = []\n"
                    'suite = "rien"\n'
                )

        resultat = executer(ecrire)
        self.assertEqual(resultat.returncode, 1, resultat.stdout + resultat.stderr)
        self.assertIn("registre humain écrit", resultat.stderr)

    def test_lecture_complement_retiree_refusee(self) -> None:
        def retirer(copie: Path) -> None:
            chemin = banc_mutations.cible(copie, COMPLEMENT)
            texte = chemin.read_text(encoding="utf-8")
            debut = texte.find("[[lecture]]")
            suivant = texte.find("[[lecture]]", debut + 1)
            self.assertGreater(debut, 0)
            self.assertGreater(suivant, debut)
            chemin.write_text(texte[:debut] + texte[suivant:], encoding="utf-8")

        resultat = executer(retirer)
        self.assertEqual(resultat.returncode, 1, resultat.stdout + resultat.stderr)
        self.assertIn("lecture de remplacement absente ou inventée", resultat.stderr)

    def test_accueil_ign_declare_resolu_refuse(self) -> None:
        def resoudre(copie: Path) -> None:
            banc_mutations.muter(
                copie, COMPLEMENT,
                'nouveau_statut = "aucune-page-lue"',
                'nouveau_statut = "remplacement-exact"',
            )

        resultat = executer(resoudre)
        self.assertEqual(resultat.returncode, 1, resultat.stdout + resultat.stderr)
        self.assertIn("résultat de seconde passe inexact", resultat.stderr)

    def test_accueil_ign_declare_lu_refuse(self) -> None:
        def lire_accueil(copie: Path) -> None:
            chemin = banc_mutations.cible(copie, TROISIEME)
            texte = chemin.read_text(encoding="utf-8")
            ancre = "[[lecture]]"
            self.assertIn(ancre, texte)
            faux = (
                "[[lecture]]\n"
                'reference = "www.ign.fr/"\n'
                'organisme = "IGN"\n'
                'titre = "Accueil IGN prétendument lu"\n'
                'date_page = "11 novembre 2026"\n'
                'fiches = ["geo-lire-legende-carte"]\n'
                'pour = "contexte-officiel"\n'
                'tranche = "0"\n'
                'repere = "Fausse lecture plantée par le banc."\n'
                'limite = "Fausse limite plantée par le banc."\n\n'
            )
            chemin.write_text(texte.replace(ancre, faux + ancre, 1), encoding="utf-8")

        resultat = executer(lire_accueil)
        self.assertEqual(resultat.returncode, 1, resultat.stdout + resultat.stderr)
        self.assertIn("accueil IGN raconté comme une page lue", resultat.stderr)

    def test_http_403_embelli_refuse(self) -> None:
        def embellir(copie: Path) -> None:
            banc_mutations.muter(
                copie, TROISIEME,
                'statut = "http-403"',
                'statut = "contenu"',
            )

        resultat = executer(embellir)
        self.assertEqual(resultat.returncode, 1, resultat.stdout + resultat.stderr)
        self.assertIn("statut de tentative embelli ou inconnu", resultat.stderr)


if __name__ == "__main__":
    unittest.main(verbosity=2)
