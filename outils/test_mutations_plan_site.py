#!/usr/bin/env python3
"""Banc de mutation de `verifier-plan-site.py`.

Treize situations sont plantées dans une copie complète du dépôt : une copie
intacte, une redite réintroduite, une section ajoutée, l’ordre des sections
inversé, une ancre retirée, une porte détournée, une classe CSS perdue, une
page obligatoire retirée du plan, l’option retenue effacée, une URL externe
recopiée, une formulation de validation inventée, une section du plan retirée
et une relecture humaine fabriquée. Les douze fautes doivent être refusées en
les nommant ; la copie intacte doit rester verte.

Usage :
    python3 outils/test_mutations_plan_site.py
"""

from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RACINE / "outils"))

import banc_mutations  # noqa: E402

OUTIL = "verifier-plan-site.py"
ACCUEIL = "index.html"
PLAN = "docs/rd/plan-site-complet-2026-11-11.md"
MATRICE = "docs/rd/plan-site-complet-2026-11-11.toml"
HUMAIN = "docs/apprentissage/relectures.toml"


def executer(mutation):  # noqa: ANN001 - préparation de copie
    with tempfile.TemporaryDirectory(prefix="mrsc-plan-site-") as dossier:
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


def ajouter(copie: Path, fichier: str, texte_ajoute: str) -> None:
    chemin = banc_mutations.cible(copie, fichier)
    chemin.write_text(chemin.read_text(encoding="utf-8") + "\n" + texte_ajoute + "\n", encoding="utf-8")


class TestPlanSite(unittest.TestCase):
    def test_copie_intacte_passe(self) -> None:
        resultat = executer(lambda copie: None)
        self.assertEqual(resultat.returncode, 0, resultat.stdout + resultat.stderr)
        self.assertIn("Plan du site vérifié", resultat.stdout)

    def test_redite_reintroduite_refusee(self) -> None:
        def ajouter_redite(copie: Path) -> None:
            chemin = banc_mutations.cible(copie, ACCUEIL)
            texte = chemin.read_text(encoding="utf-8")
            chemin.write_text(
                texte.replace("  </main>", "    <p>Aucun compte n’est demandé.</p>\n  </main>", 1),
                encoding="utf-8",
            )

        resultat = executer(ajouter_redite)
        self.assertEqual(resultat.returncode, 1, resultat.stdout + resultat.stderr)
        self.assertIn("redondance revenue : compte", resultat.stderr)

    def test_section_ajoutee_refusee(self) -> None:
        def ajouter_section(copie: Path) -> None:
            chemin = banc_mutations.cible(copie, ACCUEIL)
            texte = chemin.read_text(encoding="utf-8")
            chemin.write_text(
                texte.replace("  </main>", '    <section class="section"><p>Encore une présentation.</p></section>\n  </main>', 1),
                encoding="utf-8",
            )

        resultat = executer(ajouter_section)
        self.assertEqual(resultat.returncode, 1, resultat.stdout + resultat.stderr)
        self.assertIn("nombre de sections inexact", resultat.stderr)

    def test_ordre_inverse_refuse(self) -> None:
        def inverser(copie: Path) -> None:
            chemin = banc_mutations.cible(copie, ACCUEIL)
            texte = chemin.read_text(encoding="utf-8")
            texte = texte.replace('id="actions"', "@@TMP@@", 1)
            texte = texte.replace('id="rd-eva"', 'id="actions"', 1)
            texte = texte.replace("@@TMP@@", 'id="rd-eva"', 1)
            chemin.write_text(texte, encoding="utf-8")

        resultat = executer(inverser)
        self.assertEqual(resultat.returncode, 1, resultat.stdout + resultat.stderr)
        self.assertIn("ordre des sections illogique", resultat.stderr)

    def test_ancre_retiree_refusee(self) -> None:
        resultat = executer(lambda copie: remplacer(
            copie, ACCUEIL, 'id="rejoindre"', 'id="rejoindre-absent"'))
        self.assertEqual(resultat.returncode, 1, resultat.stdout + resultat.stderr)
        self.assertIn("ancre absente de l’accueil : rejoindre", resultat.stderr)

    def test_porte_detournee_refusee(self) -> None:
        resultat = executer(lambda copie: remplacer(
            copie, ACCUEIL, 'href="#rd-eva">Suivre le chantier ÉVA',
            'href="#actions">Suivre le chantier ÉVA'))
        self.assertEqual(resultat.returncode, 1, resultat.stdout + resultat.stderr)
        self.assertIn("porte 04 : destination", resultat.stderr)

    def test_classe_css_perdue_refusee(self) -> None:
        resultat = executer(lambda copie: remplacer(
            copie, ACCUEIL, 'class="home-hero-note"', 'class="note-accueil"'))
        self.assertEqual(resultat.returncode, 1, resultat.stdout + resultat.stderr)
        self.assertIn("classe CSS perdue lors de la refonte : home-hero-note", resultat.stderr)

    def test_page_obligatoire_retiree_refusee(self) -> None:
        resultat = executer(lambda copie: remplacer(
            copie, MATRICE, 'chemin = "index.html"', 'chemin = "accueil-absent.html"'))
        self.assertEqual(resultat.returncode, 1, resultat.stdout + resultat.stderr)
        self.assertIn("page obligatoire absente du plan du site : index.html", resultat.stderr)

    def test_option_retenue_effacee_refusee(self) -> None:
        resultat = executer(lambda copie: remplacer(
            copie, MATRICE, 'decision = "retenue"', 'decision = "écartée"'))
        self.assertEqual(resultat.returncode, 1, resultat.stdout + resultat.stderr)
        self.assertIn("brainstorming : 3 option(s), 0 retenue(s)", resultat.stderr)

    def test_url_externe_recopiee_refusee(self) -> None:
        def ajouter_url(copie: Path) -> None:
            faux = "https" + "://exemple.test/"
            ajouter(copie, PLAN, faux)

        resultat = executer(ajouter_url)
        self.assertEqual(resultat.returncode, 1, resultat.stdout + resultat.stderr)
        self.assertIn("URL externe recopiée", resultat.stderr)

    def test_validation_inventee_refusee(self) -> None:
        resultat = executer(lambda copie: ajouter(copie, PLAN, "R&D terminée."))
        self.assertEqual(resultat.returncode, 1, resultat.stdout + resultat.stderr)
        self.assertIn("formulation interdite", resultat.stderr)

    def test_section_du_plan_retiree_refusee(self) -> None:
        resultat = executer(lambda copie: remplacer(
            copie, PLAN, "## 8. Limites, contrôles et prochaine action", "## 8. Autre chose"))
        self.assertEqual(resultat.returncode, 1, resultat.stdout + resultat.stderr)
        self.assertIn("section absente du plan du site", resultat.stderr)

    def test_repere_statutaire_retire_refuse(self) -> None:
        """La « pépinière d’idées » de l’article 2 ne doit pas disparaître en silence.

        Sans elle, l’ouverture redevient une description de site : c’est la faute
        que la personne a signalée le 11 novembre 2026 à 19 h 45 UTC.
        """
        resultat = executer(lambda copie: remplacer(
            copie, ACCUEIL, "<strong>pépinière d’idées</strong>", "<strong>boîte à idées</strong>"))
        self.assertEqual(resultat.returncode, 1, resultat.stdout + resultat.stderr)
        self.assertIn("repère d’accueil exigé par une autre garde, absent", resultat.stderr)

    def test_relecture_humaine_fabriquee_refusee(self) -> None:
        resultat = executer(lambda copie: ajouter(
            copie, HUMAIN, '[[relecture]]\nfiche = "test"\ndate = 2026-11-11\n'))
        self.assertEqual(resultat.returncode, 1, resultat.stdout + resultat.stderr)
        self.assertIn("registre humain non vide", resultat.stderr)


if __name__ == "__main__":
    unittest.main(verbosity=2)
