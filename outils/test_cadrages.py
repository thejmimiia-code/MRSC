#!/usr/bin/env python3
"""Éprouve le contrôle des cadrages : trente et un cas, sans navigateur.

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

    def plan(self, attendu: dict[str, int], combinaisons: int = 1, repliable: bool = True) -> dict:
        liste = []
        for index in range(combinaisons):
            liste.append(
                {
                    "page": "index.html",
                    "layout": None if index == 0 else "vitrine",
                    "cran": 100 if index == 0 else 130,
                    "echelle": 1.0 if index == 0 else 1.3,
                    "largeur": 1440,
                    "attendu": {
                        selecteur: {"colonnes": colonnes, "repliable": repliable}
                        for selecteur, colonnes in attendu.items()
                    },
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
                    "grilles": {
                        selecteur: {
                            "total": 1,
                            "instances": [
                                {
                                    "cartes": 3,
                                    "colonnes": colonnes[selecteur],
                                    "pistes": colonnes[selecteur],
                                    "rangees": 1,
                                    "manque": 0.0,
                                }
                            ],
                        }
                        for selecteur in colonnes
                    },
                    "coupes": [],
                    "masques": 0,
                    "chevauchements": [],
                    "contraste": {
                        "mesures": 12,
                        "decoratifs": 1,
                        "fond_image": 0,
                        "sans_texte": 0,
                        "candidats": [],
                    },
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
        self.assertIn("annonce 3 colonne(s) occupée(s) pour 3 carte(s), le navigateur en compte 2", erreurs[0])

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
        # Une page qui porte une grille déclarée doit en annoncer au moins une :
        # un plan qui ne confronte rien serait vert sans rien prouver.
        avec_grilles = {c["page"] for c in plan["combinaisons"] if c["attendu"]}
        self.assertEqual(avec_grilles, set(plan["grilles"]))
        # Une page sans grille déclarée n'a aucune cible nommée : elle est
        # visitée dans la présentation par défaut seulement, et le plan le dit
        # en n'annonçant rien — jamais en se taisant sur une page absente.
        sans_grille = set(self.cadrages.PAGES) - avec_grilles
        self.assertEqual(sans_grille, {"404.html", "anglais-aventure.html", "confidentialite.html", "localisation.html", "nous-contacter.html"})
        for page in sans_grille:
            combinaisons = [c for c in plan["combinaisons"] if c["page"] == page]
            self.assertTrue(combinaisons, f"{page} n'est visitée dans aucun cadrage")
            self.assertEqual({c["layout"] for c in combinaisons}, {None})

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

    def test_un_mot_coupe_est_refuse_et_nomme(self) -> None:
        """Un mot rogné par une zone de découpe est un mot que personne ne lit."""
        rapport = self.rapport({".document-grid": 3})
        rapport["mesures"][0]["coupes"] = [
            {"tag": "article", "classe": "document-card", "depasse": 7.5, "texte": "le dossier de"}
        ]
        erreurs = self.cadrages.controler(self.plan({".document-grid": 3}), rapport)
        self.assertEqual(len(erreurs), 1, erreurs)
        self.assertIn("article.document-card coupe un mot de 7.5 px", erreurs[0])
        self.assertIn("le dossier de", erreurs[0])

    def test_un_chevauchement_de_cartes_est_refuse_et_nomme(self) -> None:
        rapport = self.rapport({".document-grid": 3})
        rapport["mesures"][0]["chevauchements"] = [
            {
                "selecteur": ".document-grid",
                "premiere": "article.document-card",
                "seconde": "aside.document-note",
                "largeur": 40.0,
                "hauteur": 12.5,
            }
        ]
        erreurs = self.cadrages.controler(self.plan({".document-grid": 3}), rapport)
        self.assertEqual(len(erreurs), 1, erreurs)
        self.assertIn("se chevauchent de 40.0 × 12.5 px", erreurs[0])
        self.assertIn(".document-grid", erreurs[0])

    def test_un_releve_de_texte_absent_ne_passe_pas_pour_un_accord(self) -> None:
        """Un rapport d'avant ce contrôle ne prouve rien du texte : il est refusé."""
        rapport = self.rapport({".document-grid": 3})
        del rapport["mesures"][0]["coupes"]
        del rapport["mesures"][0]["chevauchements"]
        erreurs = self.cadrages.controler(self.plan({".document-grid": 3}), rapport)
        self.assertEqual(len(erreurs), 2, erreurs)
        self.assertIn("texte coupé non mesuré", erreurs[0])
        self.assertIn("chevauchement non mesuré", erreurs[1])

    def test_une_derniere_rangee_incomplete_est_nommee(self) -> None:
        """Cinq cartes en deux colonnes : le fait est chiffré, il n'est pas refusé."""
        plan = self.plan({".document-grid": 2})
        rapport = self.rapport({".document-grid": 2})
        rapport["mesures"][0]["grilles"][".document-grid"] = {
            "total": 1,
            "instances": [
                {"cartes": 5, "colonnes": 2, "pistes": 2, "rangees": 3, "derniere": 1, "manque": 412.5}
            ],
        }
        trouves, sans_releve = self.cadrages.orphelins(plan, rapport)
        self.assertEqual(sans_releve, [])
        self.assertEqual(len(trouves), 1, trouves)
        self.assertEqual(trouves[0]["selecteur"], ".document-grid")
        self.assertEqual(trouves[0]["cadrages"], 1)
        self.assertAlmostEqual(trouves[0]["pire_manque"], 412.5)
        self.assertIn("1 carte(s) sur la dernière rangée, 2 colonne(s) au plus", trouves[0]["exemple"])
        # Le diagnostic ne refuse rien : c'est une mesure, pas un verdict.
        self.assertEqual(self.cadrages.controler(plan, rapport), [])

    def test_une_rangee_pleine_ne_dit_rien(self) -> None:
        plan = self.plan({".document-grid": 3})
        trouves, sans_releve = self.cadrages.orphelins(plan, self.rapport({".document-grid": 3}))
        self.assertEqual(trouves, [])
        self.assertEqual(sans_releve, [])

    def test_une_grille_sans_releve_de_rangee_est_signalee(self) -> None:
        """Un diagnostic qui ne peut pas lire sa source le dit, il n'imprime pas moins."""
        plan = self.plan({".document-grid": 3})
        rapport = self.rapport({".document-grid": 3})
        del rapport["mesures"][0]["grilles"]
        _trouves, sans_releve = self.cadrages.orphelins(plan, rapport)
        self.assertEqual(sans_releve, [".document-grid"])

    def test_le_seuil_de_contraste_suit_la_taille_et_la_graisse(self) -> None:
        """4,5:1 pour un petit texte, 3:1 pour un grand, 3:1 pour un gras de 18,66 px."""
        seuil = self.cadrages.seuil_de_contraste
        self.assertEqual(seuil(16, False), 4.5)
        self.assertEqual(seuil(16, True), 4.5)     # gras, mais loin de 18,66 px
        self.assertEqual(seuil(23.9, True), 3.0)   # gras et au-dessus de 18,66 px
        self.assertEqual(seuil(18.66, True), 3.0)  # la borne exacte compte
        self.assertEqual(seuil(18.66, False), 4.5)
        self.assertEqual(seuil(24, False), 3.0)
        self.assertEqual(seuil(43.2, True), 3.0)

    def test_un_contraste_insuffisant_est_refuse_et_nomme(self) -> None:
        plan = self.plan({".document-grid": 3})
        rapport = self.rapport({".document-grid": 3})
        rapport["mesures"][0]["contraste"]["candidats"] = [
            {"tag": "p", "classe": "hero-lede", "ratio": 2.9, "taille": 16, "gras": False, "texte": "Lire la suite"}
        ]
        erreurs = self.cadrages.controler(plan, rapport)
        self.assertEqual(len(erreurs), 1, erreurs)
        self.assertIn("p.hero-lede contraste 2.9:1, seuil 4.5:1 pour 16 px", erreurs[0])
        self.assertIn("Lire la suite", erreurs[0])

    def test_un_grand_texte_a_3_2_passe_et_un_petit_a_3_2_echoue(self) -> None:
        """Le même rapport ne veut pas dire la même chose selon la taille."""
        candidat = {"tag": "h2", "classe": "titre", "ratio": 3.2, "gras": False, "texte": "Un titre"}
        plan = self.plan({".document-grid": 3})

        grand = self.rapport({".document-grid": 3})
        grand["mesures"][0]["contraste"]["candidats"] = [{**candidat, "taille": 32}]
        self.assertEqual(self.cadrages.controler(plan, grand), [])

        petit = self.rapport({".document-grid": 3})
        petit["mesures"][0]["contraste"]["candidats"] = [{**candidat, "taille": 16}]
        erreurs = self.cadrages.controler(plan, petit)
        self.assertEqual(len(erreurs), 1, erreurs)
        self.assertIn("seuil 4.5:1", erreurs[0])

    def test_un_contraste_absent_ou_vide_ne_passe_pas_pour_un_accord(self) -> None:
        """Un rapport d'avant ce contrôle, ou un état où rien n'a pu être mesuré."""
        plan = self.plan({".document-grid": 3})
        absent = self.rapport({".document-grid": 3})
        del absent["mesures"][0]["contraste"]
        erreurs = self.cadrages.controler(plan, absent)
        self.assertEqual(len(erreurs), 1, erreurs)
        self.assertIn("contraste non mesuré", erreurs[0])

        vide = self.rapport({".document-grid": 3})
        vide["mesures"][0]["contraste"]["mesures"] = 0
        erreurs = self.cadrages.controler(plan, vide)
        self.assertEqual(len(erreurs), 1, erreurs)
        self.assertIn("aucun texte mesuré pour le contraste", erreurs[0])

    def test_toutes_les_pages_publiees_sont_visitees(self) -> None:
        """La liste des pages est lue sur le disque : neuf pages échappaient au contrôle."""
        pages = self.cadrages.pages_publiees()
        self.assertIn("documents.html", pages)
        self.assertIn("transparence.html", pages)
        self.assertEqual(sorted(pages), sorted(self.cadrages.PAGES))
        self.assertGreaterEqual(len(pages), 13)

    def test_cinq_cartes_dans_six_colonnes_ne_sont_pas_un_ecart(self) -> None:
        """Le 3 novembre 2026 : 14 écarts faux, tous dus au nombre de cartes.

        `.link-grid` permet six colonnes à 1 440 px et n'a que cinq liens :
        `auto-fit` replie la sixième piste. La capacité est six, l'occupation est
        cinq, et le dessin est conforme.
        """
        rapport = self.rapport({".document-grid": 6})
        rapport["mesures"][0]["grilles"][".document-grid"]["instances"][0].update(
            {"cartes": 5, "colonnes": 5, "pistes": 6}
        )
        self.assertEqual(self.cadrages.controler(self.plan({".document-grid": 6}), rapport), [])

    def test_une_grille_fixe_garde_ses_colonnes_meme_avec_une_carte(self) -> None:
        """`repeat(4, …)` ne replie rien : une carte occupe la première de quatre.

        Le 3 novembre 2026, la borne des cartes appliquée à un dessin fixe a
        produit 30 écarts faux en « Mosaïque », où la feuille écrit `repeat(4)`.
        """
        rapport = self.rapport({".document-grid": 4})
        rapport["mesures"][0]["grilles"][".document-grid"]["instances"][0].update(
            {"cartes": 1, "colonnes": 4, "pistes": 4}
        )
        plan = self.plan({".document-grid": 4}, repliable=False)
        self.assertEqual(self.cadrages.controler(plan, rapport), [])

    def test_une_occupation_differente_est_refusee_avec_les_deux_nombres(self) -> None:
        rapport = self.rapport({".document-grid": 6})
        rapport["mesures"][0]["grilles"][".document-grid"]["instances"][0].update(
            {"cartes": 6, "colonnes": 4, "pistes": 6}
        )
        erreurs = self.cadrages.controler(self.plan({".document-grid": 6}), rapport)
        self.assertEqual(len(erreurs), 1, erreurs)
        self.assertIn("annonce 6 colonne(s) occupée(s) pour 6 carte(s), le navigateur en compte 4", erreurs[0])
        self.assertIn("6 piste(s) déclarée(s), 2 repliée(s)", erreurs[0])

    def test_chaque_exemplaire_est_confronte_et_nomme(self) -> None:
        """Un sélecteur peut nommer plusieurs grilles : aucune ne passe par omission."""
        rapport = self.rapport({".document-grid": 2})
        rapport["mesures"][0]["grilles"][".document-grid"] = {
            "total": 2,
            "instances": [
                {"cartes": 2, "colonnes": 2, "pistes": 2, "rangees": 1, "manque": 0.0},
                {"cartes": 2, "colonnes": 1, "pistes": 2, "rangees": 2, "manque": 0.0},
            ],
        }
        erreurs = self.cadrages.controler(self.plan({".document-grid": 2}), rapport)
        self.assertEqual(len(erreurs), 1, erreurs)
        self.assertIn("exemplaire 2/2", erreurs[0])

    def test_un_exemplaire_non_inspecte_est_signale(self) -> None:
        """Le relevé plafonne à douze exemplaires : le taire ferait croire à un accord."""
        rapport = self.rapport({".document-grid": 2})
        rapport["mesures"][0]["grilles"][".document-grid"]["total"] = 14
        erreurs = self.cadrages.controler(self.plan({".document-grid": 2}), rapport)
        self.assertEqual(len(erreurs), 1, erreurs)
        self.assertIn("compte 14 exemplaire(s), 1 seul(s) inspecté(s)", erreurs[0])

    def test_un_rapport_sans_grilles_est_refuse(self) -> None:
        """Le nombre de colonnes d'un relevé ancien ne prouve rien de la capacité."""
        rapport = self.rapport({".document-grid": 3})
        del rapport["mesures"][0]["grilles"]
        erreurs = self.cadrages.controler(self.plan({".document-grid": 3}), rapport)
        self.assertEqual(len(erreurs), 1, erreurs)
        self.assertIn("grilles non mesurées", erreurs[0])

    def test_un_texte_masque_volontairement_n_est_pas_coupe(self) -> None:
        """Le 3 novembre 2026, 160 « mots coupés » étaient un utilitaire visuel masqué."""
        plan = self.plan({".document-grid": 3})
        rapport = self.rapport({".document-grid": 3})
        rapport["mesures"][0]["masques"] = 7
        rapport["mesures"][0]["coupes"] = []
        self.assertEqual(self.cadrages.controler(plan, rapport), [])

    def test_les_ecartes_du_contraste_sont_nommes(self) -> None:
        """Une exemption qui ne se nomme pas devient un angle mort."""
        rapport = self.rapport({".document-grid": 3})
        rapport["mesures"][0]["contraste"]["decoratifs_selecteurs"] = ["span.adventure-map-mark"]
        rapport["mesures"][0]["contraste"]["fond_image_selecteurs"] = ["section.home-hero"]
        bilan = self.cadrages.ecartes(rapport)
        self.assertEqual(bilan["decoratifs"], [("span.adventure-map-mark", 1)])
        self.assertEqual(bilan["fond_image"], [("section.home-hero", 1)])

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


class TestDegrade(unittest.TestCase):
    """Le contraste d'un texte posé sur un dégradé : une plage, pas une couleur.

    Jusqu'au 3 novembre 2026, un texte sur un dégradé était **compté** et jamais
    jugé. Or le site en pose partout : bandeaux, panneaux d'appel, héros. Le
    navigateur rend les arrêts de chaque couche ; ce contrôle-ci cherche le pire
    point de la plage et applique le même seuil que pour un fond uni.
    """

    BLANC = {"r": 255, "g": 255, "b": 255, "a": 1}
    NOIR = {"r": 0, "g": 0, "b": 0, "a": 1}

    def setUp(self) -> None:
        self.m = self._module()

    @staticmethod
    def _module():
        import importlib.util
        import sys
        spec = importlib.util.spec_from_file_location("cadrages", RACINE / "outils" / "cadrages.py")
        module = importlib.util.module_from_spec(spec)
        sys.modules["cadrages"] = module
        spec.loader.exec_module(module)
        return module

    def test_plage_uniforme_rend_une_couleur(self) -> None:
        plage = self.m.plage_degrade(self.BLANC, [[self.BLANC]])
        self.assertTrue(plage)
        self.assertTrue(all(couleur["r"] == 255 for couleur in plage))

    def test_plage_suit_les_deux_extremes(self) -> None:
        plage = self.m.plage_degrade(self.BLANC, [[self.NOIR, self.BLANC]])
        lumineuses = [self.m.luminance_wcag(couleur) for couleur in plage]
        self.assertAlmostEqual(min(lumineuses), 0.0, places=3)
        self.assertAlmostEqual(max(lumineuses), 1.0, places=3)

    def test_arret_transparent_laisse_voir_la_base(self) -> None:
        """Un halo `transparent` sur un marine : le fond reste le marine."""
        marine = {"r": 29, "g": 50, "b": 104, "a": 1}
        transparent = {"r": 0, "g": 0, "b": 0, "a": 0}
        plage = self.m.plage_degrade(marine, [[{"r": 255, "g": 255, "b": 255, "a": 0.2}, transparent]])
        for couleur in plage:
            self.assertLess(couleur["r"], 200, "une couche à 20 % ne peut pas blanchir un marine")

    def test_texte_blanc_sur_degrade_clair_refuse(self) -> None:
        candidat = {
            "couleur": self.BLANC,
            "base": self.BLANC,
            "couches": [[{"r": 250, "g": 250, "b": 250, "a": 1}, {"r": 245, "g": 247, "b": 251, "a": 1}]],
            "taille": 16,
            "gras": False,
        }
        pire, _ = self.m.pire_contraste_degrade(candidat)
        self.assertLess(pire, 1.2)
        self.assertLess(pire, self.m.seuil_de_contraste(16, False))

    def test_texte_sombre_sur_degrade_clair_passe(self) -> None:
        candidat = {
            "couleur": {"r": 20, "g": 30, "b": 50, "a": 1},
            "base": self.BLANC,
            "couches": [[{"r": 250, "g": 250, "b": 250, "a": 1}, {"r": 240, "g": 244, "b": 250, "a": 1}]],
            "taille": 16,
            "gras": False,
        }
        pire, _ = self.m.pire_contraste_degrade(candidat)
        self.assertGreaterEqual(pire, self.m.seuil_de_contraste(16, False))

    def test_zone_sous_le_texte_restreint_la_plage(self) -> None:
        """Le pire point de la plage entière n'est pas le pire point sous le texte.

        Un bandeau clair→sombre : un texte sombre posé sur le haut clair passe,
        alors que la plage entière le refuserait. C'est tout l'intérêt de
        projeter la boîte du texte sur l'axe du dégradé.
        """
        clair = {"r": 250, "g": 248, "b": 240, "a": 1}
        sombre = {"r": 20, "g": 25, "b": 35, "a": 1}
        texte = {"r": 40, "g": 45, "b": 60, "a": 1}
        entiere = {"couleur": texte, "base": clair, "couches": [[clair, sombre]], "taille": 16, "gras": False}
        haute = {
            "couleur": texte,
            "base": clair,
            "couches": [
                {
                    "type": "lineaire",
                    "zone": [0.0, 0.1],
                    "arrets": [dict(clair, t=0.0), dict(sombre, t=1.0)],
                }
            ],
            "taille": 16,
            "gras": False,
        }
        pire_entier, _ = self.m.pire_contraste_degrade(entiere)
        pire_haute, _ = self.m.pire_contraste_degrade(haute)
        self.assertLess(pire_entier, 2.0, "sur la plage entière, le texte sombre touche le sombre")
        self.assertGreater(pire_haute, pire_entier, "restreint au haut clair, il passe mieux")
        self.assertGreaterEqual(pire_haute, self.m.seuil_de_contraste(16, False))

    def test_zone_basse_du_degrade_refuse_le_texte_sombre(self) -> None:
        clair = {"r": 250, "g": 248, "b": 240, "a": 1}
        sombre = {"r": 20, "g": 25, "b": 35, "a": 1}
        candidat = {
            "couleur": {"r": 40, "g": 45, "b": 60, "a": 1},
            "base": clair,
            "couches": [
                {"type": "lineaire", "zone": [0.9, 1.0], "arrets": [dict(clair, t=0.0), dict(sombre, t=1.0)]}
            ],
            "taille": 16,
            "gras": False,
        }
        pire, fond = self.m.pire_contraste_degrade(candidat)
        self.assertLess(pire, 2.0)
        self.assertLess(fond["r"], 60, "le pire fond retenu est bien le bas sombre")

    def test_zone_illisible_vaut_la_plage_entiere(self) -> None:
        """Une zone qu'on ne sait pas lire est un majorant, jamais un silence."""
        noir = {"r": 0, "g": 0, "b": 0, "a": 1}
        plage = self.m.plage_degrade({"r": 255, "g": 255, "b": 255, "a": 1}, [{"zone": "inconnue", "arrets": [noir, dict(noir, t=1.0)]}])
        lumineuses = [self.m.luminance_wcag(couleur) for couleur in plage]
        self.assertAlmostEqual(min(lumineuses), 0.0, places=3)

    def test_degrade_sous_le_seuil_est_refuse_par_le_controle(self) -> None:
        """Le contrôle doit nommer le pire point, pas seulement le rapport."""
        plan = {"tolerance_px": 0.5, "combinaisons": [{"page": "index.html", "layout": None, "cran": 100, "largeur": 1440}]}
        mesure = {
            "page": "index.html",
            "layout": None,
            "cran": 100,
            "largeur": 1440,
            "debordement": 0,
            "grilles": [],
            "coupes": [],
            "masques": 0,
            "chevauchements": [],
            "contraste": {
                "mesures": 10,
                "decoratifs": 0,
                "fond_image": 0,
                "degrades": 1,
                "candidats": [],
                "candidats_degrade": [
                    {
                        "tag": "p",
                        "classe": "page-lead",
                        "couleur": {"r": 255, "g": 255, "b": 255, "a": 1},
                        "base": {"r": 255, "g": 255, "b": 255, "a": 1},
                        "couches": [[{"r": 252, "g": 252, "b": 252, "a": 1}, {"r": 248, "g": 250, "b": 254, "a": 1}]],
                        "taille": 18,
                        "gras": False,
                        "texte": "Un texte blanc sur un fond clair",
                    }
                ],
            },
        }
        erreurs = self.m.controler(plan, {"mesures": [mesure]})
        self.assertTrue(erreurs, "un texte blanc sur un dégradé clair doit être refusé")
        self.assertIn("sur un dégradé", erreurs[0])
        self.assertIn("pire point", erreurs[0])


if __name__ == "__main__":
    unittest.main(verbosity=2)
