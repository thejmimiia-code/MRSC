#!/usr/bin/env python3
"""Contrôle structurel hors ligne du protocole et de son gabarit.

Ces assertions vérifient la présence et les liens du cadre documentaire. Elles
ne contrôlent ni l'exactitude des contenus du site, ni les sources externes, ni
une relecture humaine ou un essai d'accessibilité.
"""
from __future__ import annotations

import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PROTOCOLE = ROOT / "docs" / "protocole-editorial.md"
GABARIT = ROOT / "docs" / "gabarits" / "contenu-editorial.md"


class ProtocoleEditorialTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.protocole = PROTOCOLE.read_text(encoding="utf-8")
        cls.gabarit = GABARIT.read_text(encoding="utf-8")

    def test_les_deux_documents_de_reference_existent(self) -> None:
        self.assertTrue(PROTOCOLE.is_file())
        self.assertTrue(GABARIT.is_file())

    def test_la_voix_retient_le_choix_positif_et_accessible(self) -> None:
        for expression in (
            "accueillante et positive",
            "concrète et accessible",
            "Nos expériences ont quelque chose à apporter.",
            "Partir de ce que nous vivons",
            "Mettre les savoirs en commun",
            "Rendre les propositions compréhensibles",
            "sans document ou validation qui l’atteste",
        ):
            with self.subTest(expression=expression):
                self.assertIn(expression, self.protocole)

    def test_la_trame_et_ses_adaptations_sont_decrites(self) -> None:
        for expression in (
            "Se repérer",
            "Comprendre",
            "Voir un exemple",
            "Essayer si on le souhaite",
            "Retenir l’essentiel",
            "Vérifier et approfondir",
            "Adaptations par type de page",
            "Fiche d’apprentissage",
            "Outil ou simulateur",
        ):
            with self.subTest(expression=expression):
                self.assertIn(expression, self.protocole)

    def test_les_sources_exigent_une_trace_verifiable_et_des_limites(self) -> None:
        for expression in (
            "auteur ou organisme responsable",
            "titre exact, date ou version",
            "URL, passage/page/table utilisé et date de consultation",
            "territoire, population, période ou juridiction",
            "limites, incertitudes, désaccords",
            "à proximité de l’affirmation",
            "Ne pas inventer de référence",
        ):
            with self.subTest(expression=expression):
                self.assertIn(expression, self.protocole)

    def test_les_activites_restent_facultatives_et_accessibles(self) -> None:
        for expression in (
            "facultative",
            "sans note, classement, pénalité",
            "un indice, une correction",
            "au clavier et au toucher",
            "prefers-reduced-motion",
            "une preuve d’apprentissage ou d’efficacité pédagogique",
        ):
            with self.subTest(expression=expression):
                self.assertIn(expression, self.protocole)

    def test_le_gabarit_couvre_redaction_sources_statut_et_revision(self) -> None:
        for expression in (
            "Question et utilité pour la personne",
            "Ouverture",
            "Exemple concret",
            "Activité ludique facultative",
            "Sources affichées et registre des affirmations",
            "Auteur ou organisme",
            "Vérification factuelle effectuée",
            "Prochaine révision",
            "Limites à afficher",
        ):
            with self.subTest(expression=expression):
                self.assertIn(expression, self.gabarit)
        self.assertIn("[brouillon / à vérifier / prototype / relu / publié / à réviser]", self.gabarit)

    def test_le_protocole_est_raccorde_aux_consignes_aux_docs_et_a_la_ci(self) -> None:
        consignes = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        rapport = (ROOT / "docs" / "rd-coherence-visuelle-editoriale.md").read_text(encoding="utf-8")
        ci = (ROOT / ".github" / "workflows" / "verification.yml").read_text(encoding="utf-8")
        publication = (ROOT / ".github" / "workflows" / "deploy-pages.yml").read_text(encoding="utf-8")
        self.assertIn("docs/protocole-editorial.md", consignes)
        self.assertIn("docs/gabarits/contenu-editorial.md", consignes)
        self.assertIn("docs/protocole-editorial.md", readme)
        self.assertIn("docs/protocole-editorial.md", rapport)
        self.assertIn("python3 outils/test_protocole_editorial.py", ci)
        self.assertIn("python3 outils/test_protocole_editorial.py", publication)


if __name__ == "__main__":
    unittest.main(verbosity=2)
