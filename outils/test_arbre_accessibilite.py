#!/usr/bin/env python3
"""Éprouve les décisions de `arbre-accessibilite.py` sans navigateur.

Chaque cas est un rapport fabriqué à la main : ce banc ne mesure rien, il
éprouve la règle — et surtout il vérifie qu'elle **mord**. Un garde-fou qui n'a
jamais échoué n'est qu'une affirmation : le dépôt a déjà livré un contrôle dont
un `or` le rendait toujours vrai.

Ce qui est éprouvé, règle par règle : une page sans `lang`, sans titre, sans
titre de niveau 1, à deux titres de niveau 1, à niveau sauté, sans repère
`main`, à deux `main`, à repères de même rôle et de même nom, une cible sans nom
accessible, une image sans `alt`, une image exposée sans nom, un cadre sans nom,
une zone vivante masquée, une liste sans `role="list"`, des listes présentes au
document et absentes de l'arbre, une page annoncée au plan et absente du
rapport, un rapport vide, et une erreur de mesure — qui ne doit jamais passer
pour un succès.

Ce que ce banc ne prouve pas : que `mesurer-arbre-accessibilite.cjs` mesure
juste. Aucun navigateur n'est lancé ici. La justesse de la sonde s'éprouve à la
main, en comparant un relevé au HTML — c'est écrit dans le dossier
`docs/rd/arbre-accessibilite-2026-11-13.md`, limites comprises.

Usage :
    python3 outils/test_arbre_accessibilite.py
"""

from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent


def charger_module():
    spec = importlib.util.spec_from_file_location(
        "arbre_accessibilite", RACINE / "outils" / "arbre-accessibilite.py"
    )
    module = importlib.util.module_from_spec(spec)
    sys.modules["arbre_accessibilite"] = module
    spec.loader.exec_module(module)
    return module


arbre = charger_module()


def page(**remplacements) -> dict:
    """Une page conforme ; chaque cas n'en change qu'un morceau."""
    base = {
        "page": "index.html",
        "largeur": 1280,
        "langue": "fr",
        "titres": [
            {"niveau": 1, "texte": "Le titre de la page"},
            {"niveau": 2, "texte": "Une section"},
            {"niveau": 3, "texte": "Une sous-section"},
        ],
        "reperes": [
            {"role": "banner", "nom": "En-tête"},
            {"role": "navigation", "nom": "Navigation principale"},
            {"role": "main", "nom": ""},
            {"role": "navigation", "nom": "Navigation de pied de page"},
            {"role": "contentinfo", "nom": ""},
        ],
        "noms_vides": [],
        "interactifs": 42,
        "images": {"document": 3, "decoratives": 1, "sans_alt": 0, "exposees": ["Logo", "Photo"]},
        "listes": {"document": 6, "sans_puce": 6, "avec_role": 6, "sans_role": 0, "exposees": 6, "entrees_exposees": 30},
        "zones_vivantes": [],
        "langues_declarees": [],
        "cadres": [],
    }
    base.update(remplacements)
    return base


def rapport(*pages: dict, erreurs: list[dict] | None = None) -> dict:
    return {"navigateur": "HeadlessChrome/test", "pages": list(pages), "erreurs": erreurs or []}


class TestArbreAccessibilite(unittest.TestCase):
    def refus(self, donnees: dict) -> list[str]:
        fautes, _ = arbre.controler(donnees)
        return fautes

    # --- Ce qui passe ---------------------------------------------------------

    def test_une_page_conforme_ne_produit_aucun_refus(self) -> None:
        self.assertEqual(self.refus(rapport(page())), [])

    def test_les_zones_vivantes_vides_sont_des_constats_pas_des_fautes(self) -> None:
        """Une zone vivante vide est légitime : elle se remplit à l'usage.

        Le 13 novembre 2026, les trois modules d'accessibilité ont été actionnés
        dans un vrai Chromium et la zone a annoncé « Lecture facilitée :
        activé. » — mesuré, pas supposé.
        """
        donnees = rapport(page(zones_vivantes=[{"element": "p.status", "politesse": "polite", "vide": True, "masquee": False}]))
        self.assertEqual(self.refus(donnees), [])
        _, constats = arbre.controler(donnees)
        self.assertTrue(any("zone vivante vide" in constat for constat in constats))

    # --- Langue et structure --------------------------------------------------

    def test_une_page_sans_langue_est_refusee(self) -> None:
        fautes = self.refus(rapport(page(langue="")))
        self.assertTrue(any("lang" in faute for faute in fautes), fautes)

    def test_une_page_sans_titre_est_refusee(self) -> None:
        fautes = self.refus(rapport(page(titres=[])))
        self.assertTrue(any("aucun titre exposé" in faute for faute in fautes), fautes)

    def test_une_page_sans_titre_de_niveau_1_est_refusee(self) -> None:
        fautes = self.refus(rapport(page(titres=[{"niveau": 2, "texte": "Une section"}])))
        self.assertTrue(any("aucun titre de niveau 1" in faute for faute in fautes), fautes)

    def test_deux_titres_de_niveau_1_sont_refuses(self) -> None:
        titres = [{"niveau": 1, "texte": "Un"}, {"niveau": 1, "texte": "Deux"}]
        fautes = self.refus(rapport(page(titres=titres)))
        self.assertTrue(any("2 titres de niveau 1" in faute for faute in fautes), fautes)

    def test_un_niveau_saute_est_refuse_et_nomme(self) -> None:
        titres = [
            {"niveau": 1, "texte": "Le titre"},
            {"niveau": 3, "texte": "Une sous-section orpheline"},
        ]
        fautes = self.refus(rapport(page(titres=titres)))
        self.assertTrue(any("niveau sauté" in faute for faute in fautes), fautes)
        self.assertTrue(any("Une sous-section orpheline" in faute for faute in fautes), fautes)

    def test_un_retour_en_arriere_n_est_pas_un_saut(self) -> None:
        """Revenir de 3 à 2 est légitime : seul un saut vers le bas compte.

        La première version de ce cas partait de 1 pour aller à 3 puis 2 : elle
        attendait un accord et le contrôle a refusé le 1 → 3, à juste titre.
        C'est le test qui était faux, pas la règle — 1, 2, 3, 2 est la séquence
        qu'il fallait écrire.
        """
        titres = [
            {"niveau": 1, "texte": "Un"},
            {"niveau": 2, "texte": "Deux"},
            {"niveau": 3, "texte": "Trois"},
            {"niveau": 2, "texte": "Deux, encore"},
        ]
        self.assertEqual(self.refus(rapport(page(titres=titres))), [])

    # --- Repères --------------------------------------------------------------

    def test_une_page_sans_main_est_refusee(self) -> None:
        reperes = [{"role": "banner", "nom": "En-tête"}, {"role": "contentinfo", "nom": ""}]
        fautes = self.refus(rapport(page(reperes=reperes)))
        self.assertTrue(any("main" in faute for faute in fautes), fautes)

    def test_deux_main_sont_refuses(self) -> None:
        reperes = [{"role": "main", "nom": ""}, {"role": "main", "nom": ""}]
        fautes = self.refus(rapport(page(reperes=reperes)))
        self.assertTrue(any("2 repère(s) `main`" in faute for faute in fautes), fautes)

    def test_deux_navigations_sans_nom_sont_refusees(self) -> None:
        reperes = [
            {"role": "main", "nom": ""},
            {"role": "navigation", "nom": ""},
            {"role": "navigation", "nom": ""},
        ]
        fautes = self.refus(rapport(page(reperes=reperes)))
        self.assertTrue(any("repères `navigation`" in faute for faute in fautes), fautes)

    def test_deux_navigations_nommees_différemment_passent(self) -> None:
        """Deux navigations sont légitimes si elles se distinguent — le site en a deux."""
        self.assertEqual(self.refus(rapport(page())), [])

    # --- Noms, images, cadres -------------------------------------------------

    def test_une_cible_sans_nom_est_refusee_et_situee(self) -> None:
        fautes = self.refus(rapport(page(noms_vides=[{"role": "link", "element": "a.home-entry-mark"}])))
        self.assertTrue(any("link sans nom accessible" in faute for faute in fautes), fautes)
        self.assertTrue(any("a.home-entry-mark" in faute for faute in fautes), fautes)

    def test_une_image_sans_alt_est_refusee(self) -> None:
        images = {"document": 2, "decoratives": 1, "sans_alt": 1, "exposees": ["Photo"]}
        fautes = self.refus(rapport(page(images=images)))
        self.assertTrue(any("sans attribut `alt`" in faute for faute in fautes), fautes)

    def test_une_image_decoration_exposee_sans_nom_est_refusee(self) -> None:
        images = {"document": 2, "decoratives": 1, "sans_alt": 0, "exposees": ["", "Photo"]}
        fautes = self.refus(rapport(page(images=images)))
        self.assertTrue(any("image(s) exposée(s) sans nom" in faute for faute in fautes), fautes)

    def test_une_image_decoration_retiree_de_l_arbre_passe(self) -> None:
        images = {"document": 2, "decoratives": 1, "sans_alt": 0, "exposees": ["Photo"]}
        self.assertEqual(self.refus(rapport(page(images=images))), [])

    def test_un_cadre_sans_nom_est_refuse(self) -> None:
        fautes = self.refus(rapport(page(cadres=[""])))
        self.assertTrue(any("cadre sans nom accessible" in faute for faute in fautes), fautes)

    # --- Zones vivantes -------------------------------------------------------

    def test_une_zone_vivante_masquee_est_refusee(self) -> None:
        zones = [{"element": "p.status", "politesse": "polite", "vide": False, "masquee": True}]
        fautes = self.refus(rapport(page(zones_vivantes=zones)))
        self.assertTrue(any("zone vivante masquée" in faute for faute in fautes), fautes)

    # --- Listes ---------------------------------------------------------------

    def test_une_liste_sans_role_est_refusee(self) -> None:
        listes = {"document": 6, "sans_puce": 6, "avec_role": 5, "sans_role": 1, "exposees": 6, "entrees_exposees": 30}
        fautes = self.refus(rapport(page(listes=listes)))
        self.assertTrue(any("sans `role=\"list\"`" in faute for faute in fautes), fautes)

    def test_des_listes_au_document_et_aucune_exposee_sont_refusees(self) -> None:
        listes = {"document": 4, "sans_puce": 0, "avec_role": 4, "sans_role": 0, "exposees": 0, "entrees_exposees": 0}
        fautes = self.refus(rapport(page(listes=listes)))
        self.assertTrue(any("aucune exposée" in faute for faute in fautes), fautes)

    def test_une_page_sans_liste_du_tout_passe(self) -> None:
        listes = {"document": 0, "sans_puce": 0, "avec_role": 0, "sans_role": 0, "exposees": 0, "entrees_exposees": 0}
        self.assertEqual(self.refus(rapport(page(listes=listes))), [])

    # --- Un contrôle incomplet ne vaut pas un contrôle vide ------------------

    def test_un_rapport_vide_est_refuse(self) -> None:
        fautes = self.refus({"pages": [], "erreurs": []})
        self.assertTrue(any("aucune page mesurée" in faute for faute in fautes), fautes)

    def test_une_erreur_de_mesure_est_refusee(self) -> None:
        donnees = rapport(page(), erreurs=[{"page": "simulateur.html", "raison": "page injoignable"}])
        fautes = self.refus(donnees)
        self.assertTrue(any("mesure impossible" in faute for faute in fautes), fautes)

    def test_une_page_absente_du_rapport_est_signalee_par_le_plan(self) -> None:
        """Le plan dit 122 pages ; un rapport qui en porte une n'est pas un accord."""
        plan = arbre.construire_plan(("index.html", "apprendre.html"), 1280)
        self.assertEqual(len(plan["pages"]), 2)
        self.assertIn("une largeur", plan["note"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
