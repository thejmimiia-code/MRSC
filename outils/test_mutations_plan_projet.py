#!/usr/bin/env python3
"""Banc de mutation de `verifier-plan-projet.py`.

Douze situations sont plantées dans une copie complète du dépôt : une copie
intacte, un compte de zone falsifié, une zone retirée, une initiative retirée,
un état d’action inconnu, une preuve absente, une porte humaine racontée comme
franchie, une URL externe recopiée, une formulation de R&D terminée, une
section retirée, un chemin local cassé et un total falsifié. Les onze fautes
doivent être refusées en les nommant ; la copie intacte doit rester verte.

Usage :
    python3 outils/test_mutations_plan_projet.py
"""

from __future__ import annotations

import sys
import tempfile
import tomllib
import unittest
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RACINE / "outils"))

import banc_mutations  # noqa: E402

OUTIL = "verifier-plan-projet.py"
PLAN = "docs/rd/plan-projet-complet-2026-11-11.md"
MATRICE = "docs/rd/plan-projet-complet-2026-11-11.toml"


def executer(mutation):  # noqa: ANN001 - préparation de copie
    with tempfile.TemporaryDirectory(prefix="mrsc-plan-projet-") as dossier:
        copie = Path(dossier) / "copie"
        banc_mutations.copie_complete(copie)
        mutation(copie)
        return banc_mutations.lancer(OUTIL, copie)


def remplacer(copie: Path, fichier: str, ancien: str, nouveau: str) -> None:
    chemin = banc_mutations.cible(copie, fichier)
    texte = chemin.read_text(encoding="utf-8")
    if ancien not in texte:
        raise AssertionError(f"fragment absent de {fichier} : {ancien[:80]}")
    chemin.write_text(texte.replace(ancien, nouveau, 1), encoding="utf-8")


class TestPlanProjet(unittest.TestCase):
    def test_copie_intacte_passe(self) -> None:
        resultat = executer(lambda copie: None)
        self.assertEqual(resultat.returncode, 0, resultat.stdout + resultat.stderr)
        self.assertIn("Plan du projet vérifié", resultat.stdout)

    def test_compte_de_zone_falsifie_refuse(self) -> None:
        def falsifier(copie: Path) -> None:
            donnees = tomllib.loads(banc_mutations.cible(copie, MATRICE).read_text(encoding="utf-8"))
            nombre = next(z["nombre"] for z in donnees["zone"] if z["id"] == "docs")
            remplacer(copie, MATRICE, f"nombre = {nombre}", "nombre = 1")

        resultat = executer(falsifier)
        self.assertEqual(resultat.returncode, 1, resultat.stdout + resultat.stderr)
        self.assertIn("nombre de fichiers inexact", resultat.stderr)

    def test_zone_retiree_refusee(self) -> None:
        def retirer(copie: Path) -> None:
            chemin = banc_mutations.cible(copie, MATRICE)
            texte = chemin.read_text(encoding="utf-8")
            debut = texte.index('id = ".githooks"')
            debut_bloc = texte.rfind("[[zone]]", 0, debut)
            fin_bloc = texte.find("[[zone]]", debut)
            self.assertGreater(debut_bloc, 0)
            self.assertGreater(fin_bloc, debut_bloc)
            chemin.write_text(texte[:debut_bloc] + texte[fin_bloc:], encoding="utf-8")

        resultat = executer(retirer)
        self.assertEqual(resultat.returncode, 1, resultat.stdout + resultat.stderr)
        self.assertIn("zone absente du plan du projet", resultat.stderr)

    def test_initiative_retiree_refusee(self) -> None:
        def retirer(copie: Path) -> None:
            remplacer(copie, MATRICE, 'id = "relire-les-44-prototypes"', 'id = "initiative-retiree"')

        resultat = executer(retirer)
        self.assertEqual(resultat.returncode, 1, resultat.stdout + resultat.stderr)
        self.assertIn("initiative absente du plan du projet", resultat.stderr)

    def test_etat_inconnu_refuse(self) -> None:
        resultat = executer(lambda copie: remplacer(
            copie, MATRICE, 'etat = "bloquee-humain"', 'etat = "etat-inconnu"'))
        self.assertEqual(resultat.returncode, 1, resultat.stdout + resultat.stderr)
        self.assertIn("état d’action inconnu", resultat.stderr)

    def test_preuve_absente_refusee(self) -> None:
        resultat = executer(lambda copie: remplacer(
            copie, MATRICE, 'preuve = "docs/rd/portefeuille.toml"',
            'preuve = "docs/rd/portefeuille-absent.toml"'))
        self.assertEqual(resultat.returncode, 1, resultat.stdout + resultat.stderr)
        self.assertIn("preuve introuvable", resultat.stderr)

    def test_porte_humaine_franchie_refusee(self) -> None:
        resultat = executer(lambda copie: remplacer(
            copie, MATRICE,
            'etat = "bloquee-humain"\nporte = "expertise-domaine"',
            'etat = "fait-agent"\nporte = "expertise-domaine"'))
        self.assertEqual(resultat.returncode, 1, resultat.stdout + resultat.stderr)
        self.assertIn("porte humaine présentée comme franchie", resultat.stderr)

    def test_url_externe_recopiee_refusee(self) -> None:
        def ajouter(copie: Path) -> None:
            chemin = banc_mutations.cible(copie, PLAN)
            faux = "https" + "://exemple.test/"
            chemin.write_text(chemin.read_text(encoding="utf-8") + "\n" + faux + "\n", encoding="utf-8")

        resultat = executer(ajouter)
        self.assertEqual(resultat.returncode, 1, resultat.stdout + resultat.stderr)
        self.assertIn("URL externe recopiée", resultat.stderr)

    def test_formulation_interdite_refusee(self) -> None:
        resultat = executer(lambda copie: remplacer(
            copie, PLAN, "## 10. Limites, entretien et prochaine action",
            "R&D terminée.\n\n## 10. Limites, entretien et prochaine action"))
        self.assertEqual(resultat.returncode, 1, resultat.stdout + resultat.stderr)
        self.assertIn("formulation interdite", resultat.stderr)

    def test_section_retiree_refusee(self) -> None:
        resultat = executer(lambda copie: remplacer(
            copie, PLAN, "## 8. Portes de décision et rôles", "## 8. Autre chose"))
        self.assertEqual(resultat.returncode, 1, resultat.stdout + resultat.stderr)
        self.assertIn("section absente du plan du projet", resultat.stderr)

    def test_chemin_local_casse_refuse(self) -> None:
        resultat = executer(lambda copie: remplacer(
            copie, PLAN, "`docs/rd/portefeuille.toml`", "`docs/rd/portefeuille-absent.toml`"))
        self.assertEqual(resultat.returncode, 1, resultat.stdout + resultat.stderr)
        self.assertIn("chemin local introuvable", resultat.stderr)

    def test_total_falsifie_refuse(self) -> None:
        def falsifier(copie: Path) -> None:
            donnees = tomllib.loads(banc_mutations.cible(copie, MATRICE).read_text(encoding="utf-8"))
            remplacer(copie, MATRICE, f"total = {donnees['meta']['total']}", "total = 1")

        resultat = executer(falsifier)
        self.assertEqual(resultat.returncode, 1, resultat.stdout + resultat.stderr)
        self.assertIn("total de fichiers inexact", resultat.stderr)


if __name__ == "__main__":
    unittest.main(verbosity=2)
