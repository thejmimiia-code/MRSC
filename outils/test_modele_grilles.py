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
