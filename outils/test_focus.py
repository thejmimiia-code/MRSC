#!/usr/bin/env python3
"""Éprouve la décision de `focus.py` sans navigateur.

Le seuil de 3:1 (WCAG 2.2 AA, 1.4.11) n'est éprouvé nulle part ailleurs : ce
banc le pousse dans les deux sens — 3,0:1 passe, 2,99:1 est refusé — et vérifie
les cas où le contrôle doit **avouer** plutôt que juger : un indicateur posé sur
une image, un relevé vide, une page annoncée au plan et absente du rapport, ou
une apparence de focus non retrouvée après défocalisation.

Chaque cas est un rapport fabriqué à la main : ce banc ne mesure rien, il
éprouve la règle. La mesure réelle est celle de `mesurer-focus.cjs`, et son
pouvoir de mordre est éprouvé par `test_mutations_focus.py`, dans un vrai
Chromium.

Usage :
    python3 outils/test_focus.py
"""

from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent


def charger_module():
    spec = importlib.util.spec_from_file_location("focus", RACINE / "outils" / "focus.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules["focus"] = module
    spec.loader.exec_module(module)
    return module


focus = charger_module()

PLAN = {"pages": ["index.html"], "largeurs": [390]}


def rapport(*elements: dict, page: str = "index.html", largeur: int = 390, borne: bool = False) -> dict:
    return {
        "pages": [
            {"page": page, "largeur": largeur, "borne": borne, "elements": list(elements)}
        ]
    }


def element(**remplacements) -> dict:
    base = {
        "position": 1,
        "selecteur": "a.lien",
        "libelle": "Un lien",
        "fond": {"r": 255, "g": 255, "b": 255, "a": 1},
        "fond_image": False,
        "indicateur": "contour",
        "couleur": {"r": 41, "g": 88, "b": 162, "a": 1},
        "epaisseur": 3,
        "contraste": 6.97,
        "retabli": True,
    }
    base.update(remplacements)
    return base


class TestSeuil(unittest.TestCase):
    def test_indicateur_conforme_passe(self) -> None:
        self.assertEqual(focus.controler(PLAN, rapport(element())), [])

    def test_seuil_atteint_passe(self) -> None:
        """3,0:1 est conforme : le seuil est une borne, pas un arrondi."""
        self.assertEqual(focus.controler(PLAN, rapport(element(contraste=3.0))), [])

    def test_seuil_manque_de_un_centieme_refuse(self) -> None:
        refus = focus.controler(PLAN, rapport(element(contraste=2.99)))
        self.assertEqual(len(refus), 1)
        self.assertIn("2.99:1", refus[0])
        self.assertIn("3.0:1", refus[0])
        self.assertIn("a.lien", refus[0])

    def test_aucun_indicateur_refuse(self) -> None:
        """Rien ne change à l'écran : c'est 2.4.7 qui tombe, pas 1.4.11."""
        refus = focus.controler(PLAN, rapport(element(indicateur="aucun", contraste=None)))
        self.assertEqual(len(refus), 1)
        self.assertIn("aucun indicateur", refus[0])
        self.assertIn("2.4.7", refus[0])

    def test_indicateur_sans_rapport_refuse(self) -> None:
        """Un indicateur dont la couleur est illisible ne vaut pas un indicateur conforme."""
        refus = focus.controler(PLAN, rapport(element(contraste=None)))
        self.assertEqual(len(refus), 1)
        self.assertIn("sans rapport calculable", refus[0])

    def test_ombre_sous_le_seuil_refusee(self) -> None:
        refus = focus.controler(PLAN, rapport(element(indicateur="ombre", contraste=1.2)))
        self.assertEqual(len(refus), 1)
        self.assertIn("ombre", refus[0])


class TestAveu(unittest.TestCase):
    def test_fond_image_compte_et_non_juge(self) -> None:
        """Un fond en image n'est pas calculable : il est compté, jamais refusé."""
        refus = focus.controler(
            PLAN, rapport(element(fond_image=True, contraste=None, indicateur="aucun"))
        )
        self.assertEqual(refus, [])
        resume = focus.resumer(rapport(element(fond_image=True)))
        self.assertIn("1 sur fond d'image", resume)

    def test_focus_non_retrouve_refuse(self) -> None:
        """Si le focus rendu diffère du focus réel, la mesure ne vaut rien : elle le dit."""
        refus = focus.controler(PLAN, rapport(element(retabli=False)))
        self.assertEqual(len(refus), 1)
        self.assertIn("apparence de focus non retrouvée", refus[0])

    def test_releve_vide_refuse(self) -> None:
        refus = focus.controler(PLAN, rapport())
        self.assertEqual(len(refus), 1)
        self.assertIn("relevé vide", refus[0])

    def test_page_annoncee_absente_du_rapport_refusee(self) -> None:
        """Un cadrage non mesuré est une erreur, pas un silence."""
        refus = focus.controler(PLAN, {"pages": []})
        self.assertEqual(len(refus), 1)
        self.assertIn("aucun relevé", refus[0])
        self.assertIn("index.html", refus[0])

    def test_largeur_annoncee_absente_du_rapport_refusee(self) -> None:
        plan = {"pages": ["index.html"], "largeurs": [390, 1440]}
        refus = focus.controler(plan, rapport(element()))
        self.assertEqual(len(refus), 1)
        self.assertIn("1440 px", refus[0])

    def test_resume_dit_le_plafond(self) -> None:
        resume = focus.resumer(
            {"pages": [{"page": "index.html", "largeur": 390, "borne": True, "elements": [element()]}]}
        )
        self.assertIn("1 relevé(s) arrêté(s) au plafond", resume)


if __name__ == "__main__":
    unittest.main()
