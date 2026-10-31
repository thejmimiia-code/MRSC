#!/usr/bin/env python3
"""Plante des fautes dans le registre des paliers, sur une copie du dépôt.

`outils/compter-paliers.py` ne vaut que s'il refuse. Ce banc l'éprouve : chaque
cas casse une chose précise dans une copie jetable (`outils/banc_mutations.py`,
liens symboliques) et exige le code de sortie **et** le message qui nomme la
faute.

Deux familles de cas, et la distinction compte :

- **refus** (code 1) : un palier non déclaré, une dette qui augmente ou qui
  diminue, une raison vide, courte ou en attente, une décision inventée, une
  écriture non canonique, une inscription orpheline ;
- **source illisible** (code 2) : feuille absente, accolades déséquilibrées,
  registre absent. Un contrôle qui n'a pas pu compter ne doit jamais rendre vert.

Un dernier cas éprouve la régénération : `--mettre-a-jour` inscrit un palier
inconnu avec une raison vide, et la vérification **échoue ensuite**. C'est la
preuve que le script ne peut pas blanchir un palier qu'il vient de découvrir.

**Leçon du 31 octobre 2026, apprise en cassant le dépôt.** Toutes les écritures
de ce banc passent par `banc_mutations.cible()` : la copie est faite de liens
symboliques, donc `(copie / "assets/css/site.css").unlink()` supprimait le
fichier **réel**. La première version de ce banc l'a fait, deux fois, avant que
la garde n'existe. Un banc qui mutile ce qu'il prétend protéger est pire qu'un
banc absent : il laisse croire que le dépôt est intact.

Ce que ce banc ne dit pas : il prouve que le contrôle mord sur ces quinze
situations, pas qu'il voit toutes les façons de faire grossir une dette
d'affichage. Une condition écrite sous `@supports` ne serait pas comptée.

Usage :
    python3 outils/test_paliers_affichage.py
"""

from __future__ import annotations

import re
import sys
import tempfile
import unittest
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RACINE / "outils"))

import banc_mutations  # noqa: E402

OUTIL = "compter-paliers.py"
FEUILLE = "assets/css/site.css"
REGISTRE = "docs/rd/paliers-affichage.toml"

#: Un bloc de plus à 760 px : la dette augmente sans qu'aucune condition neuve
#: n'apparaisse, donc seul le comptage peut le voir.
BLOC_EN_TROP = "\n@media (max-width: 760px) {\n  .palier-en-trop { color: red; }\n}\n"
BLOC_NEUF = "\n@media (max-width: 700px) {\n  .palier-neuf { color: red; }\n}\n"


def remplacer_champ(copie: Path, condition: str, champ: str, valeur: str) -> None:
    """Réécrit un champ d'une entrée `[[condition]]` dans la copie du registre.

    Fait à la main plutôt qu'avec un analyseur TOML : le banc doit produire un
    registre **invalide ou mensonger**, pas un registre réécrit proprement par une
    bibliothèque qui refuserait justement ce qu'on veut éprouver.
    """
    chemin = banc_mutations.cible(copie, REGISTRE)
    lignes = chemin.read_text(encoding="utf-8").splitlines()
    dedans = False
    for position, ligne in enumerate(lignes):
        if re.match(r'^condition\s*=\s*"', ligne):
            dedans = condition in ligne
            continue
        if dedans and re.match(rf"^{re.escape(champ)}\s*=", ligne):
            lignes[position] = f'{champ} = "{valeur}"'
            chemin.write_text("\n".join(lignes) + "\n", encoding="utf-8")
            return
    raise AssertionError(f"champ {champ} de {condition} introuvable : la mutation ne mordrait pas")


def ajouter_entree(copie: Path, condition: str) -> None:
    chemin = banc_mutations.cible(copie, REGISTRE)
    chemin.write_text(
        chemin.read_text(encoding="utf-8")
        + "\n[[condition]]\n"
        + f'condition = "{condition}"\n'
        + 'classe = "format"\n'
        + "occurrences = 1\n"
        + 'presume = "Une inscription ajoutée par le banc pour éprouver les entrées orphelines."\n'
        + 'decision = "dette"\n',
        encoding="utf-8",
    )


def substituer_partout(copie: Path, ancien: str, nouveau: str) -> None:
    """Remplace **toutes** les occurrences : une condition réécrite partout, pas une seule."""
    chemin = banc_mutations.cible(copie, FEUILLE)
    texte = chemin.read_text(encoding="utf-8")
    if ancien not in texte:
        raise AssertionError(f"fragment absent de {FEUILLE} : la mutation ne mordrait pas")
    chemin.write_text(texte.replace(ancien, nouveau), encoding="utf-8")


def ajouter_a_la_feuille(copie: Path, texte: str) -> None:
    with banc_mutations.cible(copie, FEUILLE).open("a", encoding="utf-8") as flux:
        flux.write(texte)


class TestPaliersAffichage(unittest.TestCase):
    def copie(self, dossier: str) -> Path:
        copie = Path(dossier)
        banc_mutations.copie_jetable(copie)
        return copie

    def test_une_cible_reste_dans_la_copie(self) -> None:
        """La copie est faite de liens : écrire « copie/assets/... » toucherait le dépôt.

        Ce cas est né d'un vrai dégât : la feuille réelle a été supprimée par ce
        banc même, en croyant éprouver une copie. La garde doit être vérifiée,
        pas supposée.
        """
        with tempfile.TemporaryDirectory() as dossier:
            copie = self.copie(dossier)
            chemin = banc_mutations.cible(copie, FEUILLE)
            self.assertFalse(chemin.is_symlink(), "la cible doit être un fichier réel")
            self.assertTrue(chemin.resolve().is_relative_to(copie.resolve()))
            self.assertEqual(chemin.resolve(), (copie / FEUILLE).resolve())

    def test_copie_intacte_passe(self) -> None:
        """Sans mutation, la copie doit être verte : sinon le banc ne prouve rien."""
        with tempfile.TemporaryDirectory() as dossier:
            resultat = banc_mutations.lancer(OUTIL, self.copie(dossier))
        self.assertEqual(resultat.returncode, 0, resultat.stdout + resultat.stderr)
        self.assertIn("Paliers déclarés", resultat.stdout)

    def test_palier_non_declare_est_refuse(self) -> None:
        with tempfile.TemporaryDirectory() as dossier:
            copie = self.copie(dossier)
            ajouter_a_la_feuille(copie, BLOC_NEUF)
            resultat = banc_mutations.lancer(OUTIL, copie)
        self.assertEqual(resultat.returncode, 1, resultat.stdout)
        self.assertIn("palier non déclaré : (max-width: 700px)", resultat.stderr)

    def test_dette_qui_augmente_est_refusee(self) -> None:
        with tempfile.TemporaryDirectory() as dossier:
            copie = self.copie(dossier)
            ajouter_a_la_feuille(copie, BLOC_EN_TROP)
            resultat = banc_mutations.lancer(OUTIL, copie)
        self.assertEqual(resultat.returncode, 1, resultat.stdout)
        self.assertIn("la dette a augmenté", resultat.stderr)

    def test_dette_qui_diminue_est_signalee(self) -> None:
        """Une dette qui baisse est une avancée : elle doit être datée, pas avalée.

        Le bloc de 920 px passe à 910 px : la condition connue perd ses sept
        règles, une autre en gagne sept. Le banc exige le message de la baisse —
        c'est celui qu'on pourrait être tenté de ne pas écrire.

        La première version visait le bloc de 1000 px et sa grille `.ai-metric-grid` ;
        le 31 octobre 2026, cette grille est sortie du palier et le fragment a
        disparu. Un banc ne doit pas mourir parce que le contenu qu'il cite a
        changé : il vise désormais une condition stable du dépôt.
        """
        with tempfile.TemporaryDirectory() as dossier:
            copie = self.copie(dossier)
            banc_mutations.muter(
                copie,
                FEUILLE,
                "  .identity-contact {\n    display: none;\n  }\n\n",
                "",
            )
            resultat = banc_mutations.lancer(OUTIL, copie)
        self.assertEqual(resultat.returncode, 1, resultat.stdout)
        self.assertIn("la dette a diminué", resultat.stderr)

    def test_une_regle_de_plus_dans_un_palier_est_refusee(self) -> None:
        """Une règle ajoutée sous une largeur donnée est une dette de plus, même sans bloc neuf."""
        with tempfile.TemporaryDirectory() as dossier:
            copie = self.copie(dossier)
            banc_mutations.muter(
                copie,
                FEUILLE,
                "  .identity-contact {\n    display: none;\n  }\n",
                "  .identity-contact {\n    display: none;\n  }\n  .regle-de-plus { color: red; }\n",
            )
            resultat = banc_mutations.lancer(OUTIL, copie)
        self.assertEqual(resultat.returncode, 1, resultat.stdout)
        self.assertIn("la dette a augmenté", resultat.stderr)

    def test_raison_vide_est_refusee(self) -> None:
        with tempfile.TemporaryDirectory() as dossier:
            copie = self.copie(dossier)
            remplacer_champ(copie, "(max-width: 300px)", "presume", "")
            resultat = banc_mutations.lancer(OUTIL, copie)
        self.assertEqual(resultat.returncode, 1, resultat.stdout)
        self.assertIn("la raison est vide", resultat.stderr)

    def test_raison_trop_courte_est_refusee(self) -> None:
        with tempfile.TemporaryDirectory() as dossier:
            copie = self.copie(dossier)
            remplacer_champ(copie, "(max-width: 420px)", "presume", "Petit écran.")
            resultat = banc_mutations.lancer(OUTIL, copie)
        self.assertEqual(resultat.returncode, 1, resultat.stdout)
        self.assertIn("raison trop courte", resultat.stderr)

    def test_raison_en_attente_est_refusee(self) -> None:
        with tempfile.TemporaryDirectory() as dossier:
            copie = self.copie(dossier)
            remplacer_champ(
                copie,
                "(max-width: 380px)",
                "presume",
                "Raison à compléter plus tard, quand quelqu'un aura regardé la constellation.",
            )
            resultat = banc_mutations.lancer(OUTIL, copie)
        self.assertEqual(resultat.returncode, 1, resultat.stdout)
        self.assertIn("travail à faire", resultat.stderr)

    def test_decision_inconnue_est_refusee(self) -> None:
        with tempfile.TemporaryDirectory() as dossier:
            copie = self.copie(dossier)
            remplacer_champ(copie, "(max-width: 340px)", "decision", "peut-etre")
            resultat = banc_mutations.lancer(OUTIL, copie)
        self.assertEqual(resultat.returncode, 1, resultat.stdout)
        self.assertIn("décision « peut-etre » inconnue", resultat.stderr)

    def test_classe_incoherente_est_refusee(self) -> None:
        with tempfile.TemporaryDirectory() as dossier:
            copie = self.copie(dossier)
            remplacer_champ(copie, "(max-width: 520px)", "classe", "preference")
            resultat = banc_mutations.lancer(OUTIL, copie)
        self.assertEqual(resultat.returncode, 1, resultat.stdout)
        self.assertIn("classée « preference »", resultat.stderr)

    def test_ecriture_non_canonique_est_refusee(self) -> None:
        """Une condition écrite partout sans espace reste lisible, mais pas comptable."""
        with tempfile.TemporaryDirectory() as dossier:
            copie = self.copie(dossier)
            substituer_partout(copie, "(max-width: 340px)", "(max-width:340px)")
            resultat = banc_mutations.lancer(OUTIL, copie)
        self.assertEqual(resultat.returncode, 1, resultat.stdout)
        self.assertIn("écriture non canonique", resultat.stderr)

    def test_deux_ecritures_de_la_meme_condition_sont_refusees(self) -> None:
        """Deux écritures d'une même condition feraient mentir le comptage."""
        with tempfile.TemporaryDirectory() as dossier:
            copie = self.copie(dossier)
            banc_mutations.muter(
                copie,
                FEUILLE,
                "@media (max-width: 1000px) {",
                "@media (max-width:1000px) {",
            )
            resultat = banc_mutations.lancer(OUTIL, copie)
        self.assertEqual(resultat.returncode, 1, resultat.stdout)
        self.assertIn("deux écritures de la même condition", resultat.stderr)

    def test_inscription_orpheline_est_refusee(self) -> None:
        with tempfile.TemporaryDirectory() as dossier:
            copie = self.copie(dossier)
            ajouter_entree(copie, "(max-width: 640px)")
            resultat = banc_mutations.lancer(OUTIL, copie)
        self.assertEqual(resultat.returncode, 1, resultat.stdout)
        self.assertIn("absent de la feuille", resultat.stderr)

    def test_feuille_absente_dit_qu_elle_ne_peut_pas_compter(self) -> None:
        with tempfile.TemporaryDirectory() as dossier:
            copie = self.copie(dossier)
            banc_mutations.cible(copie, FEUILLE).unlink()
            resultat = banc_mutations.lancer(OUTIL, copie)
        self.assertEqual(resultat.returncode, 2, resultat.stdout)
        self.assertIn("feuille de style introuvable", resultat.stderr)

    def test_accolades_desequilibrees_disent_pourquoi(self) -> None:
        with tempfile.TemporaryDirectory() as dossier:
            copie = self.copie(dossier)
            ajouter_a_la_feuille(copie, "\n@media (max-width: 700px) {\n  .jamais-ferme { color: red; }\n")
            resultat = banc_mutations.lancer(OUTIL, copie)
        self.assertEqual(resultat.returncode, 2, resultat.stdout)
        self.assertIn("accolades déséquilibrées", resultat.stderr)

    def test_registre_absent_dit_qu_il_ne_peut_pas_verifier(self) -> None:
        with tempfile.TemporaryDirectory() as dossier:
            copie = self.copie(dossier)
            banc_mutations.cible(copie, REGISTRE).unlink()
            resultat = banc_mutations.lancer(OUTIL, copie)
        self.assertEqual(resultat.returncode, 2, resultat.stdout)
        self.assertIn("registre des paliers introuvable", resultat.stderr)

    def test_ecrire_a_travers_un_lien_est_refuse(self) -> None:
        """`--mettre-a-jour` ne doit jamais écrire hors de la racine qu'il lit.

        Le 31 octobre 2026, ce cas n'existait pas : la copie du banc liait le
        registre au vrai fichier, et régénérer la copie écrivait dans le dépôt.
        """
        with tempfile.TemporaryDirectory() as dossier:
            copie = self.copie(dossier)
            ajouter_a_la_feuille(copie, BLOC_NEUF)
            resultat = banc_mutations.lancer(OUTIL, copie, arguments=("--mettre-a-jour",))
        self.assertEqual(resultat.returncode, 2, resultat.stdout)
        self.assertIn("pointe hors de la racine lue", resultat.stderr)
        self.assertNotIn('condition = "(max-width: 700px)"', (RACINE / REGISTRE).read_text(encoding="utf-8"))

    def test_mettre_a_jour_n_innocente_pas_un_palier_neuf(self) -> None:
        """La régénération inscrit le palier, laisse la raison vide, et échoue ensuite."""
        with tempfile.TemporaryDirectory() as dossier:
            copie = self.copie(dossier)
            ajouter_a_la_feuille(copie, BLOC_NEUF)
            # La copie est faite de liens : le registre doit être un vrai fichier
            # de la copie avant qu'un outil n'ait le droit d'y écrire.
            banc_mutations.cible(copie, REGISTRE)
            mise_a_jour = banc_mutations.lancer(OUTIL, copie, arguments=("--mettre-a-jour",))
            self.assertIn("raison à écrire : (max-width: 700px)", mise_a_jour.stderr)
            registre = banc_mutations.cible(copie, REGISTRE).read_text(encoding="utf-8")
            self.assertIn('condition = "(max-width: 700px)"', registre)
            verification = banc_mutations.lancer(OUTIL, copie)
        self.assertEqual(verification.returncode, 1, verification.stdout)
        self.assertIn("la raison est vide", verification.stderr)

    def test_le_depot_n_est_pas_modifie(self) -> None:
        """Après un banc complet, feuille et registre du dépôt sont intacts.

        La feuille compte autant que le registre : c'est elle qui a été perdue le
        31 octobre 2026, et le `git checkout` qui l'a restaurée n'est pas une
        garantie de banc.
        """
        avant = {
            FEUILLE: (RACINE / FEUILLE).read_bytes(),
            REGISTRE: (RACINE / REGISTRE).read_bytes(),
        }
        with tempfile.TemporaryDirectory() as dossier:
            copie = self.copie(dossier)
            remplacer_champ(copie, "(max-width: 300px)", "presume", "")
            banc_mutations.lancer(OUTIL, copie)
            ajouter_a_la_feuille(copie, BLOC_EN_TROP)
            banc_mutations.cible(copie, FEUILLE).unlink()
            banc_mutations.cible(copie, REGISTRE).unlink()
            banc_mutations.lancer(OUTIL, copie)
        for relatif, contenu in avant.items():
            self.assertEqual(contenu, (RACINE / relatif).read_bytes(), f"{relatif} a bougé")


if __name__ == "__main__":
    unittest.main(verbosity=2)
