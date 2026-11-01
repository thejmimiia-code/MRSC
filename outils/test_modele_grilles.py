#!/usr/bin/env python3
"""Éprouve le modèle des grilles : dix fautes, dont deux sources illisibles.

`outils/modele-grilles.py` ne vaut que s'il refuse. Ce banc casse une chose à la
fois dans une copie jetable (`outils/banc_mutations.py` : liens symboliques,
`cible()` matérialise ce qu'il faut écrire) et exige le code de sortie **et** le
message qui nomme la faute.

Les trois refus qui comptent le plus :

- une grille déclarée dynamique qui **redevient** un nombre de colonnes fixe ;
- un minimum de piste qui ne correspond plus à la règle de calcul — c'est la
  façon la plus discrète d'introduire un chiffre magique ;
- un palier de largeur ajouté plus tard, qui **annule** la conversion sans que la
  règle de base change d'un caractère.

Et deux sources illisibles, qui doivent sortir en code 2 : une feuille absente,
un registre absent. Un contrôle qui n'a pas pu mesurer n'a pas le droit de dire
que tout va bien.

Ce que ce banc ne dit pas : il prouve que le contrôle mord sur ces dix
situations, pas qu'il couvre toutes les façons de perdre une grille dynamique.
Un `@supports` qui réécrirait les colonnes, ou un style en ligne, lui échappent.

Usage :
    python3 outils/test_modele_grilles.py
"""

from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RACINE / "outils"))

import banc_mutations  # noqa: E402

OUTIL = "modele-grilles.py"
FEUILLE = "assets/css/site.css"
REGISTRE = "docs/rd/grilles-dynamiques.toml"


def charger_module():
    """Importe `modele-grilles.py`, dont le nom porte un tiret."""
    spec = importlib.util.spec_from_file_location("modele_grilles", RACINE / "outils" / OUTIL)
    module = importlib.util.module_from_spec(spec)
    sys.modules["modele_grilles"] = module
    spec.loader.exec_module(module)
    return module


class TestModeleGrilles(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.modele = charger_module()

    def copie(self, dossier: str) -> Path:
        copie = Path(dossier)
        banc_mutations.copie_jetable(copie)
        return copie

    # — arithmétique du modèle -------------------------------------------------

    def test_auto_fit_ne_descend_jamais_quand_la_fenetre_s_elargit(self) -> None:
        """Une grille dynamique ne peut pas perdre une colonne en gagnant de la place."""
        grille = self.modele.Grille(selecteur=".essai", colonnes_base=4, gap=16)
        for minimum in (200, 270, 370, 480):
            colonnes = [
                self.modele.auto_fit(minimum, grille.gap, largeur)
                for largeur in self.modele.LARGEURS
            ]
            self.assertEqual(
                colonnes,
                sorted(colonnes),
                f"à {minimum}px, le nombre de colonnes redescend : {colonnes}",
            )

    def test_la_regle_retrouve_le_nombre_de_colonnes_de_conception(self) -> None:
        for k, gap in ((2, 16), (3, 16), (4, 16), (4, 13.6), (5, 8)):
            minimum = self.modele.minimum_pour_k(k, gap)
            self.assertIsNotNone(minimum, f"aucune piste ne donne {k} colonnes")
            self.assertEqual(
                self.modele.auto_fit(minimum, gap, self.modele.CONTENU_DEFAUT + 48),
                k,
                f"{k} colonnes demandées, {minimum}px ne les donnent pas",
            )

    def test_des_colonnes_egales_sans_minmax_restent_egales(self) -> None:
        """`repeat(3, 1fr)` et `1fr 1fr` sont des colonnes égales, pas des pistes inégales.

        Le 31 octobre 2026, le modèle ne reconnaissait que `repeat(k, minmax(…))` :
        cinq aperçus de présentation et un bloc de carte échappaient au compte, et
        le rapport annonçait 34 grilles inégales là où quatre étaient seulement
        écrites autrement. Une écriture n'est pas un dessin.
        """
        for valeur, k in (
            ("repeat(3,1fr)", 3),
            ("repeat(2, 1fr)", 2),
            ("repeat(2, minmax(0, 1fr))", 2),
            ("1fr 1fr", 2),
            ("1fr 1fr 1fr", 3),
        ):
            self.assertEqual(self.modele.classer_valeur(valeur), ("fixe", k, None), valeur)
        for valeur in ("1fr 2fr", "minmax(0,1fr) auto", "44px 1fr", "repeat(2, max-content)"):
            self.assertEqual(self.modele.classer_valeur(valeur)[0], "asymetrique", valeur)

    def test_une_grille_declaree_fixe_qui_devient_dynamique_est_refusee(self) -> None:
        """Un aperçu de présentation qui passerait en largeur de piste cesserait de montrer ce qu'il annonce."""
        with tempfile.TemporaryDirectory() as dossier:
            copie = self.copie(dossier)
            banc_mutations.muter(
                copie,
                FEUILLE,
                '.layout-choice-preview[data-preview="mosaique"] { grid-template-columns: repeat(3,1fr);',
                '.layout-choice-preview[data-preview="mosaique"] { grid-template-columns: repeat(auto-fit, minmax(min(120px, 100%), 1fr));',
            )
            resultat = banc_mutations.lancer(OUTIL, copie, arguments=("--verifier",))
        self.assertEqual(resultat.returncode, 1, resultat.stdout)
        self.assertIn("déclarée fixe", resultat.stderr)

    def test_une_grille_fixe_qui_change_de_nombre_de_colonnes_est_refusee(self) -> None:
        """Une grille fixe déclarée à trois colonnes qui en affiche deux a changé de dessin."""
        with tempfile.TemporaryDirectory() as dossier:
            copie = self.copie(dossier)
            banc_mutations.muter(
                copie,
                FEUILLE,
                '.layout-choice-preview[data-preview="panorama"] { grid-template-columns: repeat(3,1fr);',
                '.layout-choice-preview[data-preview="panorama"] { grid-template-columns: repeat(2,1fr);',
            )
            resultat = banc_mutations.lancer(OUTIL, copie, arguments=("--verifier",))
        self.assertEqual(resultat.returncode, 1, resultat.stdout)
        self.assertIn("la feuille en donne 2", resultat.stderr)

    def test_les_pistes_d_une_valeur_sont_lues_au_premier_niveau(self) -> None:
        """`minmax(0, 1.15fr) minmax(280px, .75fr)` fait deux pistes, pas quatre."""
        self.assertEqual(
            self.modele.pistes("minmax(0, 1.15fr) minmax(280px, .75fr)"),
            ["minmax(0, 1.15fr)", "minmax(280px, .75fr)"],
        )
        self.assertEqual(
            self.modele.nature_piste("minmax(280px, .75fr)")[0], "souple"
        )
        self.assertEqual(self.modele.nature_piste("auto")[0], "contenu")
        self.assertEqual(self.modele.nature_piste("44px")[:2], ("fixe", 44.0))

    def test_une_piste_auto_ne_se_decide_pas_sans_navigateur(self) -> None:
        """Une piste `auto` fait dépendre le repli du texte : le modèle doit le dire."""
        self.assertEqual(self.modele.nature_piste("max-content")[0], "contenu")
        self.assertEqual(self.modele.nature_piste("minmax(auto, 1fr)")[0], "contenu")

    def test_la_cascade_compte_les_pistes_inegales(self) -> None:
        """`colonnes_anciennes` répond « 1 » pour une grille inégale : ce n'est pas sa forme."""
        grille = self.modele.Grille(selecteur=".inégale", gap=16)
        grille.regles = [
            self.modele.Regle(
                [".inégale"], "minmax(0, 1.15fr) minmax(280px, .75fr)", None, None, None, None, 1, 0
            ),
            self.modele.Regle([".inégale"], "minmax(0, 1fr)", 1, None, 760, None, 2, 1),
        ]
        self.assertEqual(self.modele.colonnes_de_la_cascade(grille, 1160), 2)
        self.assertEqual(self.modele.colonnes_de_la_cascade(grille, 700), 1)

    def test_une_grille_a_pistes_inegales_n_est_pas_convertible(self) -> None:
        """`1fr auto` n'est pas un nombre de colonnes : le modèle doit le dire, pas le convertir.

        Le 31 octobre 2026, la version précédente cherchait un `repeat(...)`
        n'importe où dans la valeur : `.join-panel` (`minmax(0,1fr) auto`)
        s'annonçait « 1 colonne » et `.learning-filters` « 2 colonnes ». Le
        rapport proposait de convertir des panneaux qui n'ont rien à convertir.
        """
        for valeur, forme in (
            ("minmax(0, 1fr) auto", "asymetrique"),
            ("minmax(180px, 1.5fr) repeat(2, minmax(160px, 1fr)) auto", "asymetrique"),
            ("20px 54px minmax(0, 1fr)", "asymetrique"),
            ("minmax(0, .9fr) minmax(320px, 1.1fr)", "asymetrique"),
            ("repeat(3, minmax(0, 1fr))", "fixe"),
            ("minmax(0, 1fr)", "fixe"),
            ("repeat(auto-fit, minmax(min(270px, 100%), 1fr))", "dynamique"),
        ):
            self.assertEqual(self.modele.classer_valeur(valeur)[0], forme, valeur)

    def test_une_grille_a_deux_colonnes_garde_son_seuil_de_repli(self) -> None:
        """Deux colonnes : il n'y a pas d'étape intermédiaire, seulement un moment où l'on renonce.

        La règle des trois colonnes appliquée aux grilles à deux aurait replié
        `.document-grid` dès 1 027 px au lieu de 760 — une régression visible sur
        un ordinateur portable. Une grille de deux éléments, elle, n'a aucune
        raison de relever son minimum pour empêcher une troisième colonne qui ne
        peut pas apparaître : `auto-fit` ne remplit pas une piste vide.
        """
        grille = self.modele.Grille(selecteur=".deux", colonnes_base=2, gap=16)
        grille.regles = [
            self.modele.Regle([".deux"], "repeat(2, minmax(0, 1fr))", 2, None, None, None, 1, 0),
            self.modele.Regle([".deux"], "minmax(0, 1fr)", 1, None, 760, None, 2, 1),
        ]
        self.assertEqual(self.modele.seuil_une_colonne(grille), 760)
        minimum = self.modele.minimum_recommande(grille, {"items": [2]})
        self.assertIsNotNone(minimum)
        # Deux colonnes doivent encore tenir juste au-dessus du seuil…
        self.assertEqual(self.modele.auto_fit(minimum, grille.gap, 770), 2, minimum)
        # … et ne plus tenir juste en dessous.
        self.assertEqual(self.modele.auto_fit(minimum, grille.gap, 750), 1, minimum)

    def test_une_grille_a_quatre_elements_interdit_la_troisieme_colonne(self) -> None:
        """Quatre cartes en trois colonnes laissent la dernière seule : la règle relève le minimum.

        C'est ce qui distingue une grille convertie pour **retirer un palier**
        d'une grille convertie pour **changer de dessin**. Sans cette règle,
        `.document-grid` affichait trois colonnes et une carte orpheline sur un
        écran de 1 920 px, un défaut que le modèle arithmétique ne voyait pas.
        """
        grille = self.modele.Grille(selecteur=".quatre", colonnes_base=2, gap=16)
        grille.regles = [
            self.modele.Regle([".quatre"], "repeat(2, minmax(0, 1fr))", 2, None, None, None, 1, 0),
            self.modele.Regle([".quatre"], "minmax(0, 1fr)", 1, None, 760, None, 2, 1),
        ]
        minimum = self.modele.minimum_recommande(grille, {"items": [4]})
        self.assertEqual(minimum, self.modele.minimum_sans_troisieme_colonne(grille))
        large = self.modele.CONTENU_DEFAUT + self.modele.GARNITURE_LATERALE
        self.assertEqual(self.modele.auto_fit(minimum, grille.gap, large), 2, minimum)
        # Le repli doit rester sous le seuil ancien, sinon le palier supprimé
        # revient par la petite porte.
        self.assertLess(self.modele.auto_fit(minimum, grille.gap, 780), 2)

    def test_la_capacite_borne_le_nombre_de_colonnes(self) -> None:
        """Une grille de deux éléments ne montre jamais trois colonnes, quoi qu'en dise l'arithmétique."""
        self.assertEqual(self.modele.auto_fit(350, 16, 2400), 3)
        self.assertEqual(self.modele.auto_fit(350, 16, 2400, 2), 2)

    def test_un_media_vide_ne_decale_pas_la_lecture(self) -> None:
        """Un `@media` sans règle ne doit pas attribuer les règles suivantes à sa condition.

        Le 31 octobre 2026, la conversion de `.eva-listes-grid` a laissé
        `@media (max-width: 760px) {}`, et les huit grilles suivantes ont été
        lues comme des règles de ce palier : le rapport est passé de 33 grilles à
        16 sans un mot.
        """
        feuille = """
@media (max-width: 760px) {
}
.une { display: grid; grid-template-columns: repeat(auto-fit, minmax(min(350px, 100%), 1fr)); }
@media (max-width: 760px) {
  .deux { grid-template-columns: minmax(0, 1fr); }
}
"""
        regles = self.modele.decouper(feuille)
        largeurs = {tuple(selecteurs): largeur for selecteurs, _, largeur, _, _ in regles}
        self.assertEqual(largeurs[(".une",)], None)
        self.assertEqual(largeurs[(".deux",)], 760)

    def test_l_ecart_entre_colonnes_est_le_second_nombre(self) -> None:
        """`gap: .75rem 1.1rem` vaut 12 px entre les lignes et 17,6 px entre les colonnes.

        Le modèle prenait le premier nombre : le seuil de repli de
        `.knowledge-compass` se décalait d'un écart de grille, et la recommandation
        avec lui.
        """
        lire = self.modele.ecart_colonnes
        self.assertEqual(lire("display:grid; gap: .75rem 1.1rem;"), "1.1rem")
        self.assertEqual(lire("gap: 1rem;"), "1rem")
        self.assertEqual(lire("column-gap: 20px;"), "20px")
        self.assertIsNone(lire("row-gap: 20px;"))
        self.assertIsNone(lire("display: grid;"))
        self.assertAlmostEqual(self.modele.mesure_en_px(lire("gap: .75rem 1.1rem;")), 17.6)
        self.assertAlmostEqual(self.modele.mesure_en_px("1rem"), 16.0)

    def test_un_ecart_en_clamp_varie_avec_la_fenetre(self) -> None:
        """`clamp(2rem, 5vw, 4.5rem)` vaut 32 px à 640, 38 px à 760, 72 px au-delà de 1 440.

        Le modèle prenait la première valeur écrite — parfois `clamp(2rem,` tronqué
        à l'espace — et huit grilles portaient donc un écart faux, donc un point
        de repli faux. Un écart qui dépend de la fenêtre ne peut pas être un
        nombre unique.
        """
        for largeur, attendu in ((640, 32.0), (760, 38.0), (1440, 72.0), (2000, 72.0)):
            self.assertAlmostEqual(
                self.modele.mesure_en_px("clamp(2rem, 5vw, 4.5rem)", largeur), attendu
            )
        self.assertIsNone(self.modele.mesure_en_px("clamp(2rem, 5vw, 4.5rem)"))

    def test_capacite_fausse_est_refusee(self) -> None:
        """Déclarer deux éléments là où la page en met quatre relève le minimum pour rien.

        C'est le genre de chiffre qu'on « corrige » à la main dans un registre
        quand il dérange ; le contrôle doit le remesurer dans les pages, pas le
        croire.
        """
        with tempfile.TemporaryDirectory() as dossier:
            copie = self.copie(dossier)
            banc_mutations.muter(
                copie,
                REGISTRE,
                "selecteur = \".document-grid\"\ncolonnes = 2\nminimum = 380\nitems = [4]",
                "selecteur = \".document-grid\"\ncolonnes = 2\nminimum = 380\nitems = [2]",
            )
            resultat = banc_mutations.lancer(OUTIL, copie, arguments=("--verifier",))
        self.assertEqual(resultat.returncode, 1, resultat.stdout)
        self.assertIn("capacité déclarée [2]", resultat.stderr)

    def test_une_grille_flex_dont_le_rapport_change_est_refusee(self) -> None:
        """`flex: 1.05 1 330px` n'est pas une préférence : c'est le rapport de la grille convertie.

        Changer la base d'un panneau de 330 à 300 px déplace le point de repli
        sans que rien d'autre ne bouge dans la feuille — la grille ne serait plus
        celle qui a été mesurée.
        """
        with tempfile.TemporaryDirectory() as dossier:
            copie = self.copie(dossier)
            banc_mutations.muter(
                copie, FEUILLE, "flex: 0.95 1 330px;", "flex: 0.95 1 300px;"
            )
            resultat = banc_mutations.lancer(OUTIL, copie, arguments=("--verifier",))
        self.assertEqual(resultat.returncode, 1, resultat.stdout)
        self.assertIn("aucune règle n'écrit `flex: 0.95 1 330px`", resultat.stderr)

    def test_une_grille_flex_sans_repli_est_refusee(self) -> None:
        """Sans `flex-wrap: wrap`, deux panneaux de 330 px débordent au lieu de s'empiler."""
        with tempfile.TemporaryDirectory() as dossier:
            copie = self.copie(dossier)
            banc_mutations.muter(
                copie,
                FEUILLE,
                "  display: flex;\n  flex-wrap: wrap;\n  align-items: center;\n  gap: clamp(2rem, 5vw, 4.5rem);",
                "  display: flex;\n  align-items: center;\n  gap: clamp(2rem, 5vw, 4.5rem);",
            )
            resultat = banc_mutations.lancer(OUTIL, copie, arguments=("--verifier",))
        self.assertEqual(resultat.returncode, 1, resultat.stdout)
        self.assertIn("le repli disparaît", resultat.stderr)

    def test_une_presentation_qui_impose_une_grille_a_une_grille_flex_est_refusee(self) -> None:
        """`grid-template-columns` sur un conteneur flex est sans effet : le repli annoncé n'existe pas.

        C'est le piège de la conversion : la présentation « Lecture » repliait
        `.ai-hero-grid` par cette déclaration, qui ne fait plus rien une fois la
        grille passée en `flex-wrap`.
        """
        with tempfile.TemporaryDirectory() as dossier:
            copie = self.copie(dossier)
            # La mutation vise une **condition** stable — la règle de base de la
            # grille — et non la ligne partagée qui porte les présentations : le
            # 31 octobre 2026, celle-ci a changé deux fois dans la même journée,
            # et chaque fois un banc est mort de son propre contenu.
            banc_mutations.muter(
                copie,
                FEUILLE,
                ".ai-hero-grid > :first-child {",
                'html[data-layout="lecture"] main :is(.ai-hero-grid) { grid-template-columns: minmax(0,1fr); }\n.ai-hero-grid > :first-child {',
            )
            resultat = banc_mutations.lancer(OUTIL, copie, arguments=("--verifier",))
        self.assertEqual(resultat.returncode, 1, resultat.stdout)
        self.assertIn("sans effet sur un conteneur flex", resultat.stderr)

    def test_un_zero_de_plus_ne_change_pas_le_rapport(self) -> None:
        """`flex: .8` et `flex: 0.8` sont la même déclaration.

        Le contrôle cherchait la chaîne exacte : la feuille écrit `.95fr`
        depuis toujours, et la première conversion qui a écrit `.8` s'est fait
        refuser pour une faute de forme. La tolérance ne doit pas devenir une
        indifférence : le cas suivant vérifie qu'un chiffre de plus ne passe pas.
        """
        with tempfile.TemporaryDirectory() as dossier:
            copie = self.copie(dossier)
            banc_mutations.muter(
                copie, FEUILLE, ".home-share-panel > :last-child {\n  flex: .8 1 260px;",
                ".home-share-panel > :last-child {\n  flex: 0.8 1 260px;",
            )
            resultat = banc_mutations.lancer(OUTIL, copie, arguments=("--verifier",))
        self.assertEqual(resultat.returncode, 0, resultat.stderr)

    def test_un_rapport_de_flex_falsifie_est_toujours_refuse(self) -> None:
        """La tolérance porte sur l'écriture, jamais sur la valeur."""
        with tempfile.TemporaryDirectory() as dossier:
            copie = self.copie(dossier)
            banc_mutations.muter(
                copie, FEUILLE, "flex: .8 1 260px;", "flex: 1.8 1 260px;",
            )
            resultat = banc_mutations.lancer(OUTIL, copie, arguments=("--verifier",))
        self.assertEqual(resultat.returncode, 1, resultat.stdout)
        self.assertIn("aucune règle n'écrit `flex: 0.8 1 260px`", resultat.stderr)

    def test_un_ecart_de_flex_recopie_a_la_main_est_refuse(self) -> None:
        """Le registre déclare l'écart qu'a coûté la conversion ; le contrôle le recalcule."""
        with tempfile.TemporaryDirectory() as dossier:
            copie = self.copie(dossier)
            banc_mutations.muter(copie, REGISTRE, "ecart_max_px = 16.5", "ecart_max_px = 4")
            resultat = banc_mutations.lancer(OUTIL, copie, arguments=("--verifier",))
        self.assertEqual(resultat.returncode, 1, resultat.stdout)
        self.assertIn("écart déclaré", resultat.stderr)

    def test_une_declaration_de_grille_sur_un_conteneur_flex_est_refusee(self) -> None:
        """`justify-items` sur un conteneur flex ne décide rien.

        Le palier de 761 px alignait `.english-promo-panel` par cette
        déclaration, en même temps qu'il plafonnait son illustration. Une fois la
        grille passée en `flex-wrap`, la moitié du palier ne faisait plus rien —
        et aucun compteur ne le voyait, puisque la règle restait une règle.
        """
        with tempfile.TemporaryDirectory() as dossier:
            copie = self.copie(dossier)
            banc_mutations.muter(
                copie,
                FEUILLE,
                ".english-promo-panel > :first-child {",
                ".english-promo-panel { justify-items: start; }\n.english-promo-panel > :first-child {",
            )
            resultat = banc_mutations.lancer(OUTIL, copie, arguments=("--verifier",))
        self.assertEqual(resultat.returncode, 1, resultat.stdout)
        self.assertIn("ne décide rien", resultat.stderr)

    def grille_avec_palier(self, valeur: str, palier_max: int, valeur_palier: str):
        """Une grille d'avant conversion : règle de base, puis un palier qui replie.

        `.ai-path-panel` était exactement cela — `minmax(0, .9fr) minmax(320px,
        1.1fr)`, et un `@media (max-width: 1000px)` qui forçait une colonne. Une
        grille synthétique sans palier n'aurait pas de cascade à comparer : la
        bande y serait toujours la même, et ne prouverait rien.
        """
        grille = self.modele.grille_synthetique(".exemple", valeur, "2rem")
        # Deux panneaux, comme dans les pages : `flex-wrap` ne crée pas d'élément
        # et une grille de deux enfants n'en alignera jamais trois.
        grille.items = 2
        grille.regles.append(
            self.modele.Regle(
                [".exemple"], valeur_palier, None, None, palier_max, None, 2, 1
            )
        )
        return grille

    def test_une_bande_de_changement_dit_ou_et_de_combien(self) -> None:
        """Un compte de largeurs ne dit pas **où** la conversion redessine.

        Le 31 octobre 2026, `.participation-grid` et `.ai-path-panel` avaient des
        comptes voisins (13 et 29 largeurs sur 233) et des conséquences très
        différentes : la première passait de deux colonnes à deux colonnes
        presque partout, la seconde d'**une à deux** sur toute la plage
        720–1 000 px. La plage se lit ; le compte, non.
        """
        grille = self.grille_avec_palier("minmax(0, .9fr) minmax(320px, 1.1fr)", 1000, "minmax(0, 1fr)")
        bandes = self.modele.bandes_de_changement(grille, 320)
        self.assertEqual(len(bandes), 1, bandes)
        self.assertEqual(
            (bandes[0]["debut"], bandes[0]["fin"], bandes[0]["cascade"], bandes[0]["flex"]),
            (720, 1000, 1, 2),
        )

    def test_une_grille_flex_qui_perd_son_rapport_change_de_bande(self) -> None:
        """La bande n'est pas recopiée : elle suit la valeur qu'on lui donne."""
        grille = self.grille_avec_palier("minmax(0, .9fr) minmax(480px, 1.1fr)", 1200, "minmax(0, 1fr)")
        bandes = self.modele.bandes_de_changement(grille, 480)
        self.assertEqual(
            [(b["debut"], b["fin"], b["cascade"], b["flex"]) for b in bandes],
            [(1040, 1200, 1, 2)],
            bandes,
        )

    def test_un_plafond_en_width_sur_un_enfant_de_grille_flex_est_refuse(self) -> None:
        """En flex, `flex-basis` remplace la largeur : le plafond ne décide plus rien.

        C'est le défaut du 31 octobre 2026, trouvé par la mesure navigateur et
        non par le modèle : `.english-promo-art` plafonnait son image avec
        `width: min(100%, 520px)` pour rendre vraie sa déclaration `sizes`.
        Une fois son conteneur passé en `flex-wrap` et ses présentations en
        `flex-basis: 100%`, la largeur venait du `flex-basis` : l'image montait à
        879 px, le navigateur servait la variante de 800 px, densité 0,91.
        Ce banc reproduit la régression — remettre `width` à la place de
        `max-width` — et exige que le modèle, lui aussi, la refuse.
        """
        with tempfile.TemporaryDirectory() as dossier:
            copie = self.copie(dossier)
            banc_mutations.muter(
                copie,
                FEUILLE,
                ".english-promo-art { max-width: 520px; }",
                ".english-promo-art { width: min(100%, 520px); }",
            )
            resultat = banc_mutations.lancer(OUTIL, copie, arguments=("--verifier",))
        self.assertEqual(resultat.returncode, 1, resultat.stdout)
        self.assertIn("plafond en `width`", resultat.stderr)
        self.assertIn("english-promo-art", resultat.stderr)

    def test_declaration_qui_ne_decide_rien_est_refusee(self) -> None:
        """Un `@media` qui réécrit la valeur déjà en vigueur ne protège de rien.

        `.contact-grid` a vécu des mois dans le bloc de 760 px pour y réimposer
        une colonne à une grille déjà à une colonne. Le compteur de règles ne
        pouvait pas le voir : une règle qui perd son effet reste une règle.
        """
        with tempfile.TemporaryDirectory() as dossier:
            copie = self.copie(dossier)
            banc_mutations.muter(
                copie,
                FEUILLE,
                ".principle-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(min(270px, 100%), 1fr)); gap: 1rem; }",
                ".principle-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(min(270px, 100%), 1fr)); gap: 1rem; }\n@media (max-width: 760px) { .principle-grid { grid-template-columns: repeat(auto-fit,minmax(min(270px,100%),1fr)); } }",
            )
            resultat = banc_mutations.lancer(OUTIL, copie, arguments=("--verifier",))
        self.assertEqual(resultat.returncode, 1, resultat.stdout)
        self.assertIn("ne décide rien", resultat.stderr)

    def test_grille_devenue_inegale_est_refusee(self) -> None:
        """Une conversion annulée par une règle inégale ne doit pas passer pour dynamique."""
        with tempfile.TemporaryDirectory() as dossier:
            copie = self.copie(dossier)
            banc_mutations.muter(
                copie,
                FEUILLE,
                ".home-voice-grid { display: grid; grid-template-columns: repeat(auto-fit,minmax(min(370px,100%),1fr)); gap: 1rem; }",
                ".home-voice-grid { display: grid; grid-template-columns: minmax(0, 1fr) auto; gap: 1rem; }",
            )
            resultat = banc_mutations.lancer(OUTIL, copie, arguments=("--verifier",))
        self.assertEqual(resultat.returncode, 1, resultat.stdout)
        self.assertIn("redevenue inégale", resultat.stderr)

    # — le contrôle ------------------------------------------------------------

    def test_copie_intacte_passe(self) -> None:
        with tempfile.TemporaryDirectory() as dossier:
            resultat = banc_mutations.lancer(OUTIL, self.copie(dossier), arguments=("--verifier",))
        self.assertEqual(resultat.returncode, 0, resultat.stdout + resultat.stderr)
        self.assertIn("Grilles dynamiques", resultat.stdout)

    def test_grille_revenue_fixe_est_refusee(self) -> None:
        with tempfile.TemporaryDirectory() as dossier:
            copie = self.copie(dossier)
            banc_mutations.muter(
                copie,
                FEUILLE,
                ".principle-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(min(270px, 100%), 1fr)); gap: 1rem; }",
                ".principle-grid { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 1rem; }",
            )
            resultat = banc_mutations.lancer(OUTIL, copie, arguments=("--verifier",))
        self.assertEqual(resultat.returncode, 1, resultat.stdout)
        self.assertIn("ne déclare pas `auto-fit`", resultat.stderr)

    def test_minimum_de_la_feuille_est_confronte_a_la_regle(self) -> None:
        with tempfile.TemporaryDirectory() as dossier:
            copie = self.copie(dossier)
            banc_mutations.muter(
                copie,
                FEUILLE,
                "minmax(min(370px,100%),1fr)); gap:1rem; margin-block:1.6rem 2.3rem;",
                "minmax(min(300px,100%),1fr)); gap:1rem; margin-block:1.6rem 2.3rem;",
            )
            resultat = banc_mutations.lancer(OUTIL, copie, arguments=("--verifier",))
        self.assertEqual(resultat.returncode, 1, resultat.stdout)
        self.assertIn("la feuille déclare `minmax(min(300px, 100%), 1fr)`", resultat.stderr)

    def test_minimum_du_registre_est_confronte_a_la_regle(self) -> None:
        with tempfile.TemporaryDirectory() as dossier:
            copie = self.copie(dossier)
            chemin = banc_mutations.cible(copie, REGISTRE)
            texte = chemin.read_text(encoding="utf-8")
            self.assertIn("minimum = 270", texte)
            chemin.write_text(texte.replace("minimum = 270", "minimum = 260", 1), encoding="utf-8")
            resultat = banc_mutations.lancer(OUTIL, copie, arguments=("--verifier",))
        self.assertEqual(resultat.returncode, 1, resultat.stdout)
        self.assertIn("minimum déclaré 260px, la règle en donne 270px", resultat.stderr)

    def test_palier_ajoute_apres_coup_est_refuse(self) -> None:
        """Un correctif ultérieur dans un `@media` annulerait la conversion en silence."""
        with tempfile.TemporaryDirectory() as dossier:
            copie = self.copie(dossier)
            with banc_mutations.cible(copie, FEUILLE).open("a", encoding="utf-8") as flux:
                flux.write(
                    "\n@media (max-width: 900px) {\n"
                    "  .home-voice-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }\n"
                    "}\n"
                )
            resultat = banc_mutations.lancer(OUTIL, copie, arguments=("--verifier",))
        self.assertEqual(resultat.returncode, 1, resultat.stdout)
        self.assertIn("un palier de largeur réimpose des colonnes", resultat.stderr)

    def test_selecteur_absent_de_la_feuille_est_nomme(self) -> None:
        with tempfile.TemporaryDirectory() as dossier:
            copie = self.copie(dossier)
            chemin = banc_mutations.cible(copie, REGISTRE)
            chemin.write_text(
                chemin.read_text(encoding="utf-8").replace('.home-voice-grid', '.grille-disparue'),
                encoding="utf-8",
            )
            resultat = banc_mutations.lancer(OUTIL, copie, arguments=("--verifier",))
        self.assertEqual(resultat.returncode, 1, resultat.stdout)
        self.assertIn(".grille-disparue : absent de assets/css/site.css", resultat.stderr)

    def test_registre_sans_grille_ne_prouve_rien(self) -> None:
        with tempfile.TemporaryDirectory() as dossier:
            copie = self.copie(dossier)
            chemin = banc_mutations.cible(copie, REGISTRE)
            texte = chemin.read_text(encoding="utf-8")
            chemin.write_text(texte.split("[[grille]]")[0], encoding="utf-8")
            resultat = banc_mutations.lancer(OUTIL, copie, arguments=("--verifier",))
        self.assertEqual(resultat.returncode, 1, resultat.stdout)
        self.assertIn("ne déclare aucune grille convertie", resultat.stderr)

    def test_feuille_absente_dit_qu_elle_ne_peut_pas_mesurer(self) -> None:
        with tempfile.TemporaryDirectory() as dossier:
            copie = self.copie(dossier)
            banc_mutations.cible(copie, FEUILLE).unlink()
            resultat = banc_mutations.lancer(OUTIL, copie, arguments=("--verifier",))
        self.assertEqual(resultat.returncode, 2, resultat.stdout)
        self.assertIn("Feuille de style introuvable", resultat.stderr)

    def test_registre_absent_dit_qu_il_ne_peut_pas_verifier(self) -> None:
        with tempfile.TemporaryDirectory() as dossier:
            copie = self.copie(dossier)
            banc_mutations.cible(copie, REGISTRE).unlink()
            resultat = banc_mutations.lancer(OUTIL, copie, arguments=("--verifier",))
        self.assertEqual(resultat.returncode, 2, resultat.stdout)
        self.assertIn("registre des grilles introuvable", resultat.stderr)

    def test_le_depot_n_est_pas_modifie(self) -> None:
        avant = {
            FEUILLE: (RACINE / FEUILLE).read_bytes(),
            REGISTRE: (RACINE / REGISTRE).read_bytes(),
        }
        with tempfile.TemporaryDirectory() as dossier:
            copie = self.copie(dossier)
            chemin = banc_mutations.cible(copie, REGISTRE)
            chemin.write_text(chemin.read_text(encoding="utf-8") + "\n", encoding="utf-8")
            with banc_mutations.cible(copie, FEUILLE).open("a", encoding="utf-8") as flux:
                flux.write("\n@media (max-width: 900px) { .home-voice-grid { grid-template-columns: 1fr; } }\n")
            banc_mutations.lancer(OUTIL, copie, arguments=("--verifier",))
            banc_mutations.cible(copie, FEUILLE).unlink()
        for relatif, contenu in avant.items():
            self.assertEqual(contenu, (RACINE / relatif).read_bytes(), f"{relatif} a bougé")


if __name__ == "__main__":
    unittest.main(verbosity=2)
