#!/usr/bin/env python3
"""Rejoue les mutations des garde-fous d'affichage sur une copie du dépôt.

Depuis le 23 octobre 2026, le journal dit à plusieurs reprises « mutation
rejouée : détectée ». C'était vrai, et c'était fait à la main : la porte
`verifier-affichages.py` n'avait aucun test qui échoue quand on retire la règle
qu'elle prétend protéger. Un garde-fou jamais vu en échec est une affirmation,
pas un contrôle — la leçon du 28 octobre sur `verifier-taux-dates.py` vaut ici
pour seize garde-fous d'un coup.

La copie jetable vient de `outils/banc_mutations.py` : liens symboliques, seuls
les fichiers mutés sont de vraies copies, rien n'est écrit dans l'arbre de
travail. `verifier-affichages.py` lit `MRSC_RACINE`, prévue pour cet usage.

Ce que ce banc ne dit pas : il prouve que chaque garde-fou mord sur la mutation
qu'on lui présente, pas qu'il couvre toutes les façons de casser l'affichage. Un
garde-fou peut être puissant sur ce cas et aveugle sur un autre.

Usage :
    python3 outils/test_mutations_affichages.py
"""

from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RACINE / "outils"))

import banc_mutations  # noqa: E402

OUTIL = "verifier-affichages.py"

#: Chaque entrée : nom, fichier, fragment retiré ou remplacé, message attendu.
#: Les mutations reprennent des décisions datées du journal, pour que le banc
#: garde le lien entre une règle écrite et le contrôle qui la tient.
MUTATIONS = (
    # Le panneau « Personnalisation » n'est plus ancré par un point de rupture :
    # il est placé à la mesure dans `site.js` (30 octobre 2026). Les mutations
    # portent donc sur le calcul — et la dernière sur une règle de format
    # réintroduite, qui contredirait silencieusement la mesure.
    (
        "panneau de personnalisation replacé à chaque changement de fenêtre",
        "assets/js/site.js",
        '      personnalisation.addEventListener("toggle", placerPanneauPersonnalisation);\n',
        "",
        "n'est plus placé à l'ouverture du panneau",
    ),
    (
        "panneau de personnalisation borné à la fenêtre",
        "assets/js/site.js",
        "          largeurFenetre - largeur - MARGE_PANNEAU\n",
        "          largeurFenetre\n",
        "il ne borne plus la position en largeur",
    ),
    (
        "panneau de personnalisation à l'écoute de la fenêtre visuelle",
        "assets/js/site.js",
        "      const vue = window.visualViewport;\n",
        "      const vue = null;\n",
        "il ignore la fenêtre visuelle",
    ),
    (
        "panneau de personnalisation réancré par un point de rupture",
        "assets/css/site.css",
        "html.has-js .site-header .customize-settings-panel .display-settings,\n",
        "html.entete-compacte .customize-settings-panel { left: 0; right: auto; }\n"
        "html.has-js .site-header .customize-settings-panel .display-settings,\n",
        "de nouveau ancré par un point de rupture",
    ),
    (
        "mention d'impression sur sa propre ligne",
        "assets/css/site.css",
        "  display: block;\n  margin-top: .3rem;\n  text-align: start;\n",
        "  margin-top: .3rem;\n  text-align: start;\n",
        "mention d'impression n'ouvre plus sa propre ligne",
    ),
    (
        "note de version non bornée dans le bas de page",
        "assets/css/site.css",
        ".footer-bottom .footer-rd {",
        ".footer-bottom .footer-rd-absent {",
        "note de version est de nouveau bornée",
    ),
    (
        "adresse d'impression sur la page d'accueil",
        "index.html",
        '<html lang="fr" data-print-url="https://thejmimiia-code.github.io/MRSC/">',
        '<html lang="fr">',
        "adresse d'impression",
    ),
    (
        "mention d'impression dans le pied de page de l'accueil",
        "index.html",
        '<span class="footer-rd-print">',
        '<span class="footer-rd-print-absent">',
        "collent la mention d'impression derrière le point",
    ),
    # Le plafond de l'illustration anglaise, ramené à un `width` : depuis que le
    # panneau est en `flex-wrap`, `flex-basis: 100%` remplace la largeur et le
    # plafond ne décide plus rien (densité 0,91 mesurée le 31 octobre 2026).
    (
        "plafond de 520 px de l'illustration anglaise remis en `width`",
        "assets/css/site.css",
        ".english-promo-art { max-width: 520px; }",
        ".english-promo-art { width: min(100%, 520px); }",
        "le plafond de 520 px de .english-promo-art a disparu",
    ),
    # Le 5 novembre 2026, le panneau du menu a reçu le déploiement de
    # « Personnalisation » : même calcul, même classe, une seule géométrie. Ces
    # trois mutations vérifient que le contrôle le voit, et pas seulement que le
    # fichier contient les mots qu'il cherche.
    (
        "panneau du menu placé par un autre calcul que « Personnalisation »",
        "assets/js/site.js",
        "      placerPanneauFlottant(navigation, toggle);\n",
        "      void navigation;\n",
        "le panneau du menu n'est plus placé comme « Personnalisation »",
    ),
    (
        "classe `menu-flottant` plus publiée par le script",
        "assets/js/site.js",
        '      root.classList.toggle("menu-flottant", flottant);\n',
        '      void flottant;\n',
        "la classe `menu-flottant` n'est plus publiée",
    ),
    # Le 5 novembre 2026, après la géométrie, l'habillage. Le panneau du menu est
    # devenu la même carte que « Personnalisation » : même surface, mêmes états,
    # même anneau. Ces cinq mutations vérifient que le contrôle compare vraiment
    # les deux règles, et ne se contente pas de retrouver des mots connus.
    (
        "panneau du menu rendu à sa surface marine",
        "assets/css/site.css",
        "  background: var(--surface);\n"
        "  box-shadow:\n"
        "    0 24px 48px -24px rgba(16, 36, 74, .34),\n"
        "    0 10px 20px -12px rgba(16, 36, 74, .18),\n"
        "    0 1px 2px rgba(16, 36, 74, .08);\n"
        "  animation: panneau-deploiement .16s ease-out both;\n"
        "}\n"
        "html.has-js.menu-flottant .nav-links.is-open { display: flex; }",
        "  background: var(--navy);\n"
        "  box-shadow:\n"
        "    0 24px 48px -24px rgba(16, 36, 74, .34),\n"
        "    0 10px 20px -12px rgba(16, 36, 74, .18),\n"
        "    0 1px 2px rgba(16, 36, 74, .08);\n"
        "  animation: panneau-deploiement .16s ease-out both;\n"
        "}\n"
        "html.has-js.menu-flottant .nav-links.is-open { display: flex; }",
        "diverge de celui de « Personnalisation »",
    ),
    (
        "trait doré de la barre rendu au panneau du menu",
        "assets/css/site.css",
        "html.has-js.menu-flottant .nav-links a::after { content: none; }",
        "html.has-js.menu-flottant .nav-links a::after { width: auto; }",
        "le trait doré de la barre en ligne est revenu dans le panneau",
    ),
    (
        "survol du panneau du menu sans allumage",
        "assets/css/site.css",
        "html.has-js.menu-flottant .nav-links a:hover,\n"
        'html.has-js.menu-flottant .nav-links a[aria-current="page"] {\n'
        "  border-color: var(--border-soft-2);\n"
        "  background: var(--blue-soft);",
        "html.has-js.menu-flottant .nav-links a:hover,\n"
        'html.has-js.menu-flottant .nav-links a[aria-current="page"] {\n'
        "  border-color: var(--border-soft-2);\n"
        "  background: transparent;",
        "n'ont plus l'allumage des lignes de « Personnalisation »",
    ),
    (
        "anneau de focus du panneau rendu à l'or de la barre",
        "assets/css/site.css",
        "html.has-js.menu-flottant .nav-links a:focus-visible {\n"
        "  outline: 2px solid var(--blue);",
        "html.has-js.menu-flottant .nav-links a:focus-visible {\n"
        "  outline: 2px solid var(--gold);",
        "l'anneau de focus d'une entrée du panneau n'est plus celui des",
    ),
    (
        "panneau du menu de nouveau centré verticalement",
        "assets/css/site.css",
        "  justify-content: flex-start;\n  gap: .1rem;",
        "  justify-content: safe center;\n  gap: .1rem;",
        "ne s'aligne plus depuis le haut",
    ),
    (
        "géométrie de panneau réintroduite par un palier",
        "assets/css/site.css",
        "html.has-js.menu-flottant .nav-links.is-open { display: flex; }",
        "html.has-js.menu-flottant .nav-links.is-open { display: flex; }\n"
        ".has-js .nav-links { position: absolute; right: 0; left: 0; width: auto; }",
        "le panneau du menu a de nouveau une géométrie par palier",
    ),
)


class TestMutationsAffichages(unittest.TestCase):
    def test_copie_intacte_passe(self) -> None:
        """Sans mutation, la copie doit être verte : sinon le banc ne prouve rien."""
        with tempfile.TemporaryDirectory() as dossier:
            banc_mutations.copie_jetable(Path(dossier))
            resultat = banc_mutations.lancer(OUTIL, Path(dossier))
        self.assertEqual(resultat.returncode, 0, resultat.stdout + resultat.stderr)
        self.assertIn("garde-fous des formats", resultat.stdout)

    def test_chaque_mutation_est_detectee(self) -> None:
        for nom, relatif, ancien, nouveau, message in MUTATIONS:
            with self.subTest(mutation=nom), tempfile.TemporaryDirectory() as dossier:
                copie = Path(dossier)
                banc_mutations.copie_jetable(copie)
                banc_mutations.muter(copie, relatif, ancien, nouveau)
                resultat = banc_mutations.lancer(OUTIL, copie)
                self.assertEqual(
                    resultat.returncode,
                    1,
                    f"la mutation « {nom} » n'a pas été vue :\n{resultat.stdout}",
                )
                self.assertIn(message, resultat.stderr, resultat.stderr[:900])

    def test_le_depot_n_est_pas_modifie(self) -> None:
        """Le banc écrit dans une copie : un échec ne doit rien laisser derrière lui."""
        avant = (RACINE / "assets" / "css" / "site.css").read_bytes()
        with tempfile.TemporaryDirectory() as dossier:
            copie = Path(dossier)
            banc_mutations.copie_jetable(copie)
            banc_mutations.muter(
                copie,
                "assets/js/site.js",
                # La mutation vise la ligne que le placement partagé écrit pour
                # les deux panneaux : depuis le 5 novembre 2026, il n'y a plus de
                # `panneauPersonnalisation.style` distinct.
                "      panneau.style.maxHeight = ",
                "      panneau.style.heightInutile = ",
            )
            banc_mutations.lancer(OUTIL, copie)
        self.assertEqual(avant, (RACINE / "assets" / "css" / "site.css").read_bytes())


if __name__ == "__main__":
    unittest.main(verbosity=2)
