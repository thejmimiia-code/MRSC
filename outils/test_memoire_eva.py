#!/usr/bin/env python3
"""Banc de `memoire-eva.py` : la mémoire doit se tromper quand elle ment.

Dix cas, tous dans une **vraie copie** du dépôt (l'outil écrit quatre fichiers :
index, graphe Mermaid, graphe DOT et plan rendu ; écrire par un lien symbolique
modifierait le dépôt pendant le test).

1. régénération puis contrôle : accord, trois horizons non vides ;
2. déterminisme : deux régénérations rendent exactement les mêmes octets ;
3. un pointeur mort est refusé, avec le nom du fichier absent ;
4. un pointeur hors du fichier (ligne 9 999) est refusé ;
5. un résumé trop long est refusé — un résumé long est une copie déguisée ;
6. le même fait écrit deux fois au même horizon est refusé ;
7. un renvoi de court terme qui ne résout plus est refusé ;
8. un index absent ne produit pas une recherche vide : code 2 ;
9. la recherche imprime un **pointeur** et le poids lu, jamais le corpus ;
10. une source disparue sort en code 2, pas en mémoire incomplète.

Usage :
    python3 outils/test_memoire_eva.py
"""

from __future__ import annotations

import json
import re
import sys
import tempfile
import unittest
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RACINE / "outils"))

import banc_mutations  # noqa: E402

OUTIL = "memoire-eva.py"
INDEX = "docs/rd/eva/memoire.json"


def copie_complete(dossier: str) -> Path:
    """Une copie réelle : l'outil **écrit** dans la racine qu'on lui donne."""
    copie = Path(dossier) / "depot"
    banc_mutations.copie_complete(copie)
    return copie


def regenerer(copie: Path):
    return banc_mutations.lancer(OUTIL, copie, arguments=("--regenerer",))


def controler(copie: Path):
    return banc_mutations.lancer(OUTIL, copie, arguments=("--verifier",))


class TestMemoireEva(unittest.TestCase):
    def setUp(self) -> None:
        self._dossier = tempfile.TemporaryDirectory(prefix="mrsc-memoire-eva-")
        self.copie = copie_complete(self._dossier.name)
        resultat = regenerer(self.copie)
        self.assertEqual(resultat.returncode, 0, resultat.stdout + resultat.stderr)

    def tearDown(self) -> None:
        self._dossier.cleanup()

    def index(self) -> dict:
        return json.loads((self.copie / INDEX).read_text(encoding="utf-8"))

    def ecrire_index(self, index: dict) -> None:
        (self.copie / INDEX).write_text(
            json.dumps(index, ensure_ascii=False, indent=1) + "\n", encoding="utf-8"
        )

    def test_regenerer_puis_controler(self) -> None:
        resultat = controler(self.copie)
        self.assertEqual(resultat.returncode, 0, resultat.stdout + resultat.stderr)
        self.assertIn("Mémoire cohérente", resultat.stdout)
        index = self.index()
        for horizon in ("court", "moyen", "long"):
            self.assertGreater(index["compte"][horizon], 0, horizon)
        self.assertLess(index["poids_corpus"], 10**9)

    def test_deux_regenerations_rendent_les_memes_octets(self) -> None:
        """Un index qui change d'ordre rendrait tout contrôle de fraîcheur inutile."""
        premier = (self.copie / INDEX).read_bytes()
        self.assertEqual(regenerer(self.copie).returncode, 0)
        self.assertEqual((self.copie / INDEX).read_bytes(), premier)

    def test_pointeur_mort_refuse(self) -> None:
        index = self.index()
        index["entrees"][0]["source"] = "docs/rd/fichier-qui-n-existe-pas.md"
        self.ecrire_index(index)
        resultat = controler(self.copie)
        self.assertEqual(resultat.returncode, 1, resultat.stdout)
        self.assertIn("pointeur mort", resultat.stderr)
        self.assertIn("fichier-qui-n-existe-pas", resultat.stderr)

    def test_ligne_hors_du_fichier_refusee(self) -> None:
        index = self.index()
        index["entrees"][0]["ligne"] = 9999
        self.ecrire_index(index)
        resultat = controler(self.copie)
        self.assertEqual(resultat.returncode, 1, resultat.stdout)
        self.assertIn("hors de", resultat.stderr)

    def test_resume_trop_long_refuse(self) -> None:
        """Un résumé long n'est plus un renvoi : c'est une copie qui se désynchronise."""
        index = self.index()
        index["entrees"][0]["resume"] = "mot " * 60
        self.ecrire_index(index)
        resultat = controler(self.copie)
        self.assertEqual(resultat.returncode, 1, resultat.stdout)
        self.assertIn("caractères (max 160)", resultat.stderr)

    def test_meme_fait_deux_fois_refuse(self) -> None:
        index = self.index()
        document = next(e for e in index["entrees"] if e["horizon"] == "long")
        copie = dict(document)
        copie["id"] = "long:doublon"
        index["entrees"].append(copie)
        self.ecrire_index(index)
        resultat = controler(self.copie)
        self.assertEqual(resultat.returncode, 1, resultat.stdout)
        self.assertIn("même fait écrit deux fois", resultat.stderr)

    def test_renvoi_de_court_terme_qui_ne_resout_plus_est_refuse(self) -> None:
        index = self.index()
        renvoi = next(e for e in index["entrees"] if e.get("cache_de") and e["cache_de"].startswith("moyen:"))
        renvoi["cache_de"] = "moyen:avancee:disparue"
        self.ecrire_index(index)
        resultat = controler(self.copie)
        self.assertEqual(resultat.returncode, 1, resultat.stdout)
        self.assertIn("renvoi vers une entrée inconnue", resultat.stderr)

    def test_index_absent_ne_produit_pas_une_recherche_vide(self) -> None:
        (self.copie / INDEX).unlink()
        resultat = banc_mutations.lancer(
            OUTIL, self.copie, arguments=("--chercher", "gouttière")
        )
        self.assertEqual(resultat.returncode, 2, resultat.stdout)
        self.assertIn("Aucune recherche", resultat.stderr)
        self.assertIn("inventée", resultat.stderr)

    def test_la_recherche_imprime_un_pointeur_et_le_poids_lu(self) -> None:
        resultat = banc_mutations.lancer(
            OUTIL, self.copie, arguments=("--chercher", "gouttière conteneur")
        )
        self.assertEqual(resultat.returncode, 0, resultat.stderr)
        self.assertIn("octets", resultat.stdout)
        self.assertRegex(resultat.stdout, r"docs/rd/[\w./-]+\.(?:md|toml):\d+")
        # Le corpus ne doit jamais défiler : on cite, on ne recopie pas.
        self.assertLess(len(resultat.stdout.splitlines()), 30)
        self.assertIn("ponytail", self.index()["regle"]["methode"])

    def test_source_disparue_sort_en_code_2(self) -> None:
        (self.copie / "docs/rd/portefeuille.toml").unlink()
        resultat = controler(self.copie)
        self.assertEqual(resultat.returncode, 2, resultat.stdout)
        self.assertIn("illisible", resultat.stderr)
        self.assertIn("portefeuille", resultat.stderr)


if __name__ == "__main__":
    unittest.main(verbosity=2)
