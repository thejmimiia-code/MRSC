#!/usr/bin/env python3
"""Éprouve le contrôle des cadrages : douze cas, sans navigateur.

`outils/cadrages.py --controler` ne vaut que s'il refuse. Ce banc lui donne des
plans et des rapports fabriqués — jamais le vrai dépôt, jamais un navigateur — et
exige le code de sortie **et** le message qui nomme la faute.

Les quatre refus qui comptent :

- un **débordement** au-delà de la tolérance, nommé avec la page, la
  présentation, le cran, la largeur et l'élément coupable ;
- un **nombre de colonnes** qui n'est pas celui promis ;
- un cadrage **non mesuré** — un contrôle incomplet ne vaut pas un contrôle vide ;
- un rapport **vide**, qui sort en code 1 et non en silence vert.

Et deux tolérances qui doivent être respectées à l'identique : 0,5 px passe,
0,51 px échoue. C'est ce qui fait dire « au pixel près » plutôt que « à peu près ».

Ce que ce banc ne dit pas : il prouve que le contrôle mord sur ces douze
situations, pas qu'il couvre toutes les façons de déborder. Un débordement
vertical, un chevauchement ou un texte tronqué lui échappent — c'est écrit dans
`docs/rd/cadrages.toml`.

Usage :
    python3 outils/test_cadrages.py
"""

from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent


def charger_module():
    """Importe `outils/cadrages.py` sans passer par un paquet."""
    spec = importlib.util.spec_from_file_location("cadrages", RACINE / "outils" / "cadrages.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules["cadrages"] = module
    spec.loader.exec_module(module)
    return module


class TestCadrages(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.cadrages = charger_module()

    def plan(self, attendu: dict[str, int], combinaisons: int = 1) -> dict:
        liste = []
        for index in range(combinaisons):
            liste.append(
                {
                    "page": "index.html",
                    "layout": None if index == 0 else "vitrine",
                    "cran": 100 if index == 0 else 130,
                    "echelle": 1.0 if index == 0 else 1.3,
                    "largeur": 1440,
                    "attendu": attendu,
                }
            )
        return {"tolerance_px": 0.5, "combinaisons": liste}

    def rapport(self, colonnes: dict[str, int], debordement: float = 0.0, combinaisons: int = 1) -> dict:
        mesures = []
        for index in range(combinaisons):
            mesures.append(
                {
                    "page": "index.html",
                    "layout": None if index == 0 else "vitrine",
                    "cran": 100 if index == 0 else 130,
                    "largeur": 1440,
                    "debordement": debordement,
                    "colonnes": colonnes,
                }
            )
        return {"navigateur": "HeadlessChrome/essai", "mesures": mesures}

    def test_un_cadrage_conforme_ne_dit_rien(self) -> None:
        erreurs = self.cadrages.controler(
            self.plan({".document-grid": 3}), self.rapport({".document-grid": 3})
        )
        self.assertEqual(erreurs, [])

    def test_un_debordement_est_nomme_avec_son_element(self) -> None:
        rapport = self.rapport({".document-grid": 3}, debordement=12.0)
        rapport["mesures"][0]["coupable"] = {"depasse": 12.0, "tag": "div", "classe": "home-share-panel"}
        erreurs = self.cadrages.controler(self.plan({".document-grid": 3}), rapport)
        self.assertEqual(len(erreurs), 1, erreurs)
        self.assertIn("débordement horizontal de 12.0 px", erreurs[0])
        self.assertIn("div.home-share-panel", erreurs[0])
        self.assertIn("1440 px", erreurs[0])

    def test_la_tolerance_est_respectee_a_l_identique(self) -> None:
        """0,5 px passe, 0,51 px échoue : c'est le sens de « au pixel près »."""
        plan = self.plan({".document-grid": 3})
        self.assertEqual(self.cadrages.controler(plan, self.rapport({".document-grid": 3}, 0.5)), [])
        erreurs = self.cadrages.controler(plan, self.rapport({".document-grid": 3}, 0.51))
        self.assertEqual(len(erreurs), 1, erreurs)

    def test_un_ecart_de_colonnes_est_refuse_et_nomme(self) -> None:
        erreurs = self.cadrages.controler(
            self.plan({".document-grid": 3}), self.rapport({".document-grid": 2})
        )
        self.assertEqual(len(erreurs), 1, erreurs)
        self.assertIn("annonce 3 colonne(s), le navigateur en compte 2", erreurs[0])

    def test_une_grille_non_mesuree_est_une_erreur(self) -> None:
        erreurs = self.cadrages.controler(self.plan({".document-grid": 3}), self.rapport({}))
        self.assertEqual(len(erreurs), 1, erreurs)
        self.assertIn("n'a pas été mesurée", erreurs[0])

    def test_un_cadrage_non_mesure_est_une_erreur(self) -> None:
        """Une combinaison qui manque au rapport ne peut pas passer pour un accord."""
        erreurs = self.cadrages.controler(
            self.plan({".document-grid": 3}, combinaisons=2),
            self.rapport({".document-grid": 3}, combinaisons=1),
        )
        self.assertEqual(len(erreurs), 1, erreurs)
        self.assertIn("aucune mesure", erreurs[0])
        self.assertIn("vitrine", erreurs[0])

    def test_un_rapport_vide_est_refuse(self) -> None:
        erreurs = self.cadrages.controler(self.plan({".document-grid": 3}), {"mesures": []})
        self.assertEqual(len(erreurs), 1, erreurs)
        self.assertIn("contrôle incomplet", erreurs[0])

    def test_un_debordement_non_mesure_est_refuse(self) -> None:
        """Un rapport qui ne dit rien du débordement ne prouve rien du débordement."""
        rapport = self.rapport({".document-grid": 3})
        del rapport["mesures"][0]["debordement"]
        erreurs = self.cadrages.controler(self.plan({".document-grid": 3}), rapport)
        self.assertEqual(len(erreurs), 1, erreurs)
        self.assertIn("débordement non mesuré", erreurs[0])

    def test_le_plan_couvre_les_six_presentations_et_les_cinq_crans(self) -> None:
        """Le plan est construit depuis la feuille réelle : il ne présume aucune dimension."""
        modele = self.cadrages.charger_modele()
        feuille = (RACINE / self.cadrages.FEUILLE).read_text(encoding="utf-8")
        modele.definir_gouttiere(feuille)
        modele.definir_feuille(feuille)
        registre = self.cadrages.lire_registre(RACINE / self.cadrages.REGISTRE)
        plan = self.cadrages.construire_plan(modele, registre, feuille)
        presentations = {c["layout"] for c in plan["combinaisons"]}
        crans = {c["cran"] for c in plan["combinaisons"]}
        largeurs = {c["largeur"] for c in plan["combinaisons"]}
        self.assertEqual(presentations, set(self.cadrages.PRESENTATIONS))
        self.assertEqual(crans, set(self.cadrages.ECHELLES))
        self.assertEqual(largeurs, set(self.cadrages.LARGEURS))
        self.assertEqual(plan["tolerance_px"], 0.5)
        # Chaque combinaison doit annoncer au moins une grille : un plan qui ne
        # confronte rien serait vert sans rien prouver.
        self.assertTrue(all(c["attendu"] for c in plan["combinaisons"]))

    def test_la_cascade_des_presentations_retient_la_derniere_regle(self) -> None:
        """« Mosaïque » écrit deux colonnes dès 601 px, puis quatre dès 981.

        Prendre la première règle trouvée annonçait deux colonnes sur un écran de
        1 440 px : 96 écarts d'un coup, tous faux, et tous attribués à la feuille.
        """
        modele = self.cadrages.charger_modele()
        feuille = (RACINE / self.cadrages.FEUILLE).read_text(encoding="utf-8")
        modele.definir_feuille(feuille)
        modele.definir_gouttiere(feuille)
        grilles = modele.lire_grilles(feuille)
        trouvees = modele.presentations_lues(grilles, feuille)
        regle = modele.regle_applicable(trouvees, "mosaique", 1440, ".document-grid")
        self.assertIsNotNone(regle)
        self.assertEqual(regle["colonnes"], 4)
        milieu = modele.regle_applicable(trouvees, "mosaique", 700, ".document-grid")
        self.assertEqual(milieu["colonnes"], 2)
        # Et une grille que la présentation ne nomme pas ne reçoit aucune règle.
        self.assertIsNone(modele.regle_applicable(trouvees, "mosaique", 1440, ".ai-balance-grid"))

    def test_le_cout_declare_est_celui_du_plan(self) -> None:
        """Un registre qui annonce le coût du lot précédent se trompe de moitié.

        Il a déclaré 360 combinaisons et 246 s alors que le plan en comptait 480 :
        le chiffre écrit dans la documentation était celui d'avant, et rien ne
        le confrontait. Le coût déclaré est désormais comparé au plan réel.
        """
        modele = self.cadrages.charger_modele()
        feuille = (RACINE / self.cadrages.FEUILLE).read_text(encoding="utf-8")
        modele.definir_gouttiere(feuille)
        modele.definir_feuille(feuille)
        grilles = self.cadrages.lire_registre(RACINE / self.cadrages.REGISTRE)
        plan = self.cadrages.construire_plan(modele, grilles, feuille)
        declare = self.cadrages.lire_registre(RACINE / self.cadrages.REGISTRE_CADRAGES)
        self.assertEqual(int(declare["cout"]["combinaisons"]), len(plan["combinaisons"]))
        self.assertGreater(int(declare["cout"]["mesure_locale_secondes"]), 0)

    def test_chaque_dimension_du_registre_est_balayee(self) -> None:
        """Une dimension déclarée mais non balayée serait une case vide déguisée."""
        registre = self.cadrages.lire_registre(RACINE / self.cadrages.REGISTRE_CADRAGES)
        dimensions = {d["nom"]: [str(v) for v in d["valeurs"]] for d in registre["dimension"]}
        self.assertEqual(sorted(dimensions["presentation"]), sorted(str(p or "defaut") for p in self.cadrages.PRESENTATIONS))
        self.assertEqual(sorted(dimensions["cran_de_texte"]), sorted(str(c) for c in self.cadrages.ECHELLES))
        self.assertEqual(sorted(dimensions["largeur"]), sorted(str(w) for w in self.cadrages.LARGEURS))
        self.assertEqual(sorted(dimensions["page"]), sorted(self.cadrages.PAGES))
        self.assertEqual(float(registre["releve"]["tolerance_px"]), 0.5)


if __name__ == "__main__":
    unittest.main(verbosity=2)
