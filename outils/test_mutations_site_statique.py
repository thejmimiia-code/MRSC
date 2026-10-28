#!/usr/bin/env python3
"""Rejoue des mutations de la porte des pages statiques sur une copie du dépôt.

`verifier-site-statique.py` est la porte qui voit le plus de choses : les 99
pages, leurs liens locaux, leurs ancres, leurs titres, leurs canoniques, le
sitemap, `llms.txt` et la syntaxe des scripts. Elle n'avait aucun test qui
échoue quand on casse une de ces propriétés — seulement la lecture du code et la
confiance dans un vert quotidien.

La leçon du 28 octobre 2026 s'applique telle quelle : un contrôle jamais vu en
échec est une affirmation. Ce banc plante cinq fautes que cette porte prétend
détecter et exige, pour chacune, un échec **avec le message attendu**.

Ici la copie est **complète** et non faite de liens symboliques : la porte
compare des chemins résolus pour refuser une cible qui sortirait du dépôt, et un
lien vers l'original sortirait de la copie par construction. Le dépôt pèse moins
de 30 Mio ; la copie prend moins d'une seconde.

Ce que ce banc ne dit pas : il prouve que ces cinq fautes sont vues, pas que la
porte couvre toutes les façons de casser une page.

Usage :
    python3 outils/test_mutations_site_statique.py
"""

from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RACINE / "outils"))

import banc_mutations  # noqa: E402

OUTIL = "verifier-site-statique.py"

#: Chaque entrée : nom, fichier, fragment remplacé, message attendu.
#: Les cinq fautes sont celles qu'un git merge ou une édition rapide produisent
#: réellement : un lien qui suit un fichier renommé, une canonique recopiée d'une
#: autre page, un `alt` perdu, une ancre qui suit un titre modifié, une page
#: oubliée au sitemap.
MUTATIONS = (
    (
        "lien local vers une page absente",
        "index.html",
        '<a href="apprendre.html">Apprendre</a>',
        '<a href="apprendre-absente.html">Apprendre</a>',
        "href local introuvable : 'apprendre-absente.html'",
    ),
    (
        "canonique recopiée d'une autre adresse",
        "index.html",
        '<link rel="canonical" href="https://thejmimiia-code.github.io/MRSC/">',
        '<link rel="canonical" href="https://thejmimiia-code.github.io/MRSC/index.html">',
        "canonique attendue",
    ),
    (
        "image sans attribut alt",
        "index.html",
        ' alt="Logo M.R.S.C — Mouvement Représentatif de la Société Civile"',
        "",
        "image(s) sans attribut alt",
    ),
    (
        "ancre qui ne correspond à aucun identifiant",
        "index.html",
        'href="transparence.html#licence"',
        'href="transparence.html#licence-absente"',
        "ancre #licence-absente absente dans transparence.html",
    ),
    (
        "page publique oubliée au sitemap",
        "sitemap.xml",
        "  <url><loc>https://thejmimiia-code.github.io/MRSC/eva.html</loc></url>\n",
        "",
        "sitemap.xml omet des pages publiques : eva.html",
    ),
)


class TestMutationsSiteStatique(unittest.TestCase):
    def test_copie_intacte_passe(self) -> None:
        """Sans mutation, la copie doit être verte : sinon le banc ne prouve rien."""
        with tempfile.TemporaryDirectory() as dossier:
            copie = Path(dossier) / "copie"
            banc_mutations.copie_complete(copie)
            resultat = banc_mutations.lancer(OUTIL, copie)
        self.assertEqual(resultat.returncode, 0, resultat.stdout + resultat.stderr)
        self.assertIn("contrôles réussis", resultat.stdout)

    def test_chaque_mutation_est_detectee(self) -> None:
        for nom, relatif, ancien, nouveau, message in MUTATIONS:
            with self.subTest(mutation=nom), tempfile.TemporaryDirectory() as dossier:
                copie = Path(dossier) / "copie"
                banc_mutations.copie_complete(copie)
                banc_mutations.muter(copie, relatif, ancien, nouveau)
                resultat = banc_mutations.lancer(OUTIL, copie)
                self.assertEqual(
                    resultat.returncode,
                    1,
                    f"la mutation « {nom} » n'a pas été vue :\n{resultat.stdout}",
                )
                self.assertIn(message, resultat.stderr + resultat.stdout)

    def test_le_depot_n_est_pas_modifie(self) -> None:
        """Le banc écrit dans une copie : un échec ne doit rien laisser derrière lui."""
        avant = (RACINE / "index.html").read_bytes()
        with tempfile.TemporaryDirectory() as dossier:
            copie = Path(dossier) / "copie"
            banc_mutations.copie_complete(copie)
            banc_mutations.muter(copie, "index.html", 'href="apprendre.html"', 'href="absente.html"')
            banc_mutations.lancer(OUTIL, copie)
        self.assertEqual(avant, (RACINE / "index.html").read_bytes())


if __name__ == "__main__":
    unittest.main(verbosity=2)
