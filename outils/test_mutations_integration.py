#!/usr/bin/env python3
"""Banc de mutation de `verifier-integration.py`, la dernière porte sans preuve.

Mille six cents lignes, seize routes exercées en montant les fonctions de `api/`
comme le fait Vercel, un contrôle qui compare les nombres écrits en prose au
catalogue réel, et un autre qui refuse une ressource publiée que plus rien
n'appelle. Rien n'éprouvait cette porte ailleurs que par son propre vert.

Trois fautes sont plantées dans une copie complète du dépôt :

1. une ressource ajoutée à `assets/` que rien ne cite — le cas d'un fichier livré
   que le site ne demande jamais ;
2. un nombre annoncé dans `apprendre.html` qui ne correspond plus au catalogue ;
3. une page publique supprimée du dépôt.

Trois autres fautes plantent le retour de l'ancienne formule de la page
Transparence, la disparition du titre qui nomme les citoyennes et les citoyens,
et celle de la phrase ancrée dans la vie de tous les jours : le 6 novembre 2026,
cette page a été réécrite à la demande de la personne utilisatrice, et un
contrôle qui ne mord pas sur sa propre formulation ne protège rien.

Quatre fautes de plus éprouvent la restructuration du 6 novembre 2026, après le
retour « la page mélange tous les sujets » : sommaire retiré, registre des
sources à nouveau enterré sous la R&D, repère de partie effacé et ancre du
sommaire morte. Sans elles, une page qui redeviendrait illisible resterait verte.

Ce banc est le plus lent du dépôt : `verifier-integration.py` lance lui-même
quatre outils et monte un serveur, soit une vingtaine de secondes par exécution.
Treize cas couvrent les familles que la porte vérifie elle-même : le périmètre
publié, les chiffres recalculés, la présence des pages, les trois clauses du
contrôle éditorial et l'ordre de lecture. Deux fautes de plus, plantées le
10 novembre 2026, éprouvent le retrait demandé de « Ce résumé n’est pas un
appel aux dons » et de la carte du siège social ; la copie intacte doit rester
verte. Les routes HTTP, elles, ont déjà leur propre contrôle
(`verifier-securite.py`).

Usage :
    python3 outils/test_mutations_integration.py
"""

from __future__ import annotations

import subprocess
import sys
import tempfile
import tomllib
import unittest
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RACINE / "outils"))

import banc_mutations  # noqa: E402

OUTIL = "verifier-integration.py"


def executer(mutation) -> subprocess.CompletedProcess[str]:  # noqa: ANN001 - fonction de préparation
    """Copie complète, une faute préparée dans la copie, puis la porte réelle."""
    with tempfile.TemporaryDirectory(prefix="mrsc-integration-") as dossier:
        copie = Path(dossier) / "copie"
        banc_mutations.copie_complete(copie)
        mutation(copie)
        return banc_mutations.lancer(OUTIL, copie)


class TestIntegration(unittest.TestCase):
    def test_copie_intacte_passe(self) -> None:
        resultat = executer(lambda copie: None)
        self.assertEqual(resultat.returncode, 0, resultat.stdout[-2000:] + resultat.stderr[-2000:])
        self.assertIn("Tous les contrôles passent", resultat.stdout)

    def test_ressource_orpheline_refusee(self) -> None:
        """Un fichier livré que rien ne cite : la panne est silencieuse, donc à voir."""

        def ajouter(copie: Path) -> None:
            (copie / "assets" / "images" / "orpheline.png").write_bytes(b"\x89PNG orpheline")

        resultat = executer(ajouter)
        self.assertEqual(resultat.returncode, 1, resultat.stdout[-2000:])
        self.assertIn("orphelines : assets/images/orpheline.png", resultat.stdout)

    def test_chiffre_annonce_faux_refuse(self) -> None:
        """Le total est recalculé depuis `catalogue.toml`, jamais recopié : il doit mordre."""

        def mentir(copie: Path) -> None:
            # Le total et le nombre d'univers se recalculent depuis les sources :
            # recopier le compte ici ferait de ce banc un contrôle qui se cite lui-même.
            donnees = copie / "docs" / "apprentissage"
            with (donnees / "catalogue.toml").open("rb") as source:
                total = len(tomllib.load(source)["fiche"])
            with (donnees / "referentiel.toml").open("rb") as source:
                univers = len(tomllib.load(source)["domaine"])
            banc_mutations.muter(
                copie,
                "apprendre.html",
                f"{total} fiches du catalogue à {univers} univers",
                f"{total + 1} fiches du catalogue à {univers} univers",
            )

        resultat = executer(mentir)
        self.assertEqual(resultat.returncode, 1, resultat.stdout[-2000:])
        self.assertIn("Les nombres annoncés dans apprendre.html", resultat.stdout)
        self.assertIn("ÉCHEC", resultat.stdout)

    def test_page_publique_absente_refusee(self) -> None:
        resultat = executer(lambda copie: (copie / "eva.html").unlink())
        self.assertEqual(resultat.returncode, 1, resultat.stdout[-2000:])
        self.assertIn("ÉCHEC Page présente : eva.html", resultat.stdout)

    def test_ancienne_formule_refusee(self) -> None:
        """Remettre « Un outil du peuple, pour le peuple » doit faire échouer la porte."""

        def revenir(copie: Path) -> None:
            banc_mutations.muter(
                copie,
                "transparence.html",
                "<h2>Un outil au service des citoyennes et des citoyens</h2>",
                "<h2>Un outil du peuple, pour le peuple</h2>",
            )

        resultat = executer(revenir)
        self.assertEqual(resultat.returncode, 1, resultat.stdout[-2000:])
        self.assertIn(
            "ÉCHEC La page Transparence parle aux citoyennes et aux citoyens sans ancienne formule",
            resultat.stdout,
        )

    def test_formule_signee_reintroduite_refusee(self) -> None:
        """L'ancienne formule ne doit pas revenir non plus dans l'encadré mis en avant."""

        def citer(copie: Path) -> None:
            banc_mutations.muter(
                copie,
                "transparence.html",
                "Pas de formule &agrave; reprendre :",
                "&laquo; Nous portons cet outil pour une gestion de la nation "
                "r&eacute;ellement faite &ldquo;par le peuple et pour le peuple&rdquo;. &raquo;",
            )

        resultat = executer(citer)
        self.assertEqual(resultat.returncode, 1, resultat.stdout[-2000:])
        self.assertIn(
            "ÉCHEC La page Transparence parle aux citoyennes et aux citoyens sans ancienne formule",
            resultat.stdout,
        )

    def test_ancrage_quotidien_retire_refuse(self) -> None:
        """Un titre juste ne suffit pas : la phrase d'ancrage concret doit rester."""

        def generaliser(copie: Path) -> None:
            banc_mutations.muter(
                copie,
                "transparence.html",
                "la vie de tous les jours",
                "les grandes orientations",
            )

        resultat = executer(generaliser)
        self.assertEqual(resultat.returncode, 1, resultat.stdout[-2000:])
        self.assertIn(
            "ÉCHEC La page Transparence parle aux citoyennes et aux citoyens sans ancienne formule",
            resultat.stdout,
        )

    def test_sommaire_retire_refuse(self) -> None:
        """Sans le sommaire, la page n'a plus de fil : la porte doit le dire."""

        def retirer(copie: Path) -> None:
            banc_mutations.muter(copie, "transparence.html", 'id="lire-cette-page"', 'id="sans-sommaire"')

        resultat = executer(retirer)
        self.assertEqual(resultat.returncode, 1, resultat.stdout[-2000:])
        self.assertIn("La page Transparence remet chaque sujet", resultat.stdout)

    def test_registre_a_nouveau_enterre_refuse(self) -> None:
        """Le registre des sources ne doit plus être une section anonyme en fin de page."""

        def enterrer(copie: Path) -> None:
            banc_mutations.muter(copie, "transparence.html", 'id="registre-tracabilite"', 'id="registre-decale"')

        resultat = executer(enterrer)
        self.assertEqual(resultat.returncode, 1, resultat.stdout[-2000:])
        self.assertIn("ancre(s) morte(s)", resultat.stdout)

    def test_repere_de_partie_efface_refuse(self) -> None:
        """Une partie sans son repère « Partie n / 7 » redevient un bloc sans contexte."""

        def effacer(copie: Path) -> None:
            banc_mutations.muter(copie, "transparence.html", "Partie 6 / 7 &middot;", "Prospective &middot;")

        resultat = executer(effacer)
        self.assertEqual(resultat.returncode, 1, resultat.stdout[-2000:])
        self.assertIn("parties numérotées", resultat.stdout)

    def test_ancre_du_sommaire_morte_refusee(self) -> None:
        """Un lien du sommaire qui ne mène nulle part est un sommaire qui ment."""

        def casser(copie: Path) -> None:
            banc_mutations.muter(copie, "transparence.html", 'href="#signaler"', 'href="#signalement-absent"')

        resultat = executer(casser)
        self.assertEqual(resultat.returncode, 1, resultat.stdout[-2000:])
        self.assertIn("ancre(s) morte(s)", resultat.stdout)


    def test_appel_aux_dons_reintroduit_refuse(self) -> None:
        """Remettre la phrase retirée doit faire échouer la porte."""

        def revenir(copie: Path) -> None:
            banc_mutations.muter(
                copie,
                "index.html",
                "Le budget et les besoins précis restent à définir.</p>",
                "Le budget et les besoins précis restent à définir. Ce résumé n’est pas un appel aux dons.</p>",
            )

        resultat = executer(revenir)
        self.assertEqual(resultat.returncode, 1, resultat.stdout[-2000:])
        self.assertIn("L’accueil ne remet ni l’appel aux dons ni la carte du siège social", resultat.stdout)

    def test_slogan_des_statuts_retire_refuse(self) -> None:
        """Retirer « La force citoyenne » de l’article 1 doit faire échouer la porte.

        Le 11 novembre 2026 à 19 h 45 UTC, la personne a jugé que l’ouverture ne
        représentait pas l’association. Le slogan écrit à l’article 1 des statuts
        est un des repères qui l’ancre dans le document officiel.
        """

        def retirer(copie: Path) -> None:
            banc_mutations.muter(
                copie,
                "index.html",
                "« La force citoyenne » : le M.R.S.C. est un mouvement représentatif de la société civile",
                "Le M.R.S.C. est un mouvement représentatif de la société civile",
            )

        resultat = executer(retirer)
        self.assertEqual(resultat.returncode, 1, resultat.stdout[-2000:])
        self.assertIn(
            "ÉCHEC L’accueil représente l’association d’après ses statuts avant de présenter ses ressources",
            resultat.stdout,
        )

    def test_objet_des_statuts_tronque_refuse(self) -> None:
        """Réduire l’objet de l’article 2 aux seuls « intérêts » doit être refusé.

        C’était la faute réelle de la page avant ce lot : l’objet était coupé de
        l’histoire, des traditions, de la culture et de l’avenir.
        """

        def tronquer(copie: Path) -> None:
            # Deux endroits portent l’objet depuis le 13 novembre 2026 : le
            # paragraphe « Notre but » de l’ouverture et la lede de la
            # présentation. Les deux sont tronqués, sinon la porte trouverait
            # encore l’objet entier à l’autre endroit et le banc ne prouverait rien.
            texte = (copie / "index.html").read_text(encoding="utf-8")
            tronque = texte.replace(
                "les intérêts, l’histoire, les traditions, la culture et l’avenir des femmes et des hommes "
                "qui participent à la vie économique, sociale et environnementale.",
                "les intérêts des personnes qui participent à la vie économique, sociale et environnementale.",
            )
            assert tronque != texte, "la mutation de l’objet n’a rien changé"
            (copie / "index.html").write_text(tronque, encoding="utf-8")

        resultat = executer(tronquer)
        self.assertEqual(resultat.returncode, 1, resultat.stdout[-2000:])
        self.assertIn(
            "ÉCHEC L’accueil relie la présentation de l’association aux statuts et aux trois repères de réflexion",
            resultat.stdout,
        )

    def test_regle_de_vote_retiree_refusee(self) -> None:
        """Effacer la règle des articles 3 et 5 — seuls les concernés ou impactés votent."""

        def retirer(copie: Path) -> None:
            banc_mutations.muter(
                copie,
                "index.html",
                "seuls les membres concernés ou impactés votent",
                "les membres votent",
            )

        resultat = executer(retirer)
        self.assertEqual(resultat.returncode, 1, resultat.stdout[-2000:])
        self.assertIn(
            "ÉCHEC L’accueil représente l’association d’après ses statuts avant de présenter ses ressources",
            resultat.stdout,
        )

    def test_carte_siege_reintroduite_refuse(self) -> None:
        """Remettre la carte du siège doit faire échouer la porte."""

        def revenir(copie: Path) -> None:
            banc_mutations.muter(
                copie,
                "index.html",
                "            <dt>Réutilisation</dt>",
                "            <dt>Siège</dt>\n            <dd>Siège social fixé à Beaurepaire — article 1.3 des statuts.</dd>\n          </div>\n          <div>\n            <dt>Réutilisation</dt>",
            )

        resultat = executer(revenir)
        self.assertEqual(resultat.returncode, 1, resultat.stdout[-2000:])
        self.assertIn("L’accueil ne remet ni l’appel aux dons ni la carte du siège social", resultat.stdout)


if __name__ == "__main__":
    unittest.main(verbosity=2)
