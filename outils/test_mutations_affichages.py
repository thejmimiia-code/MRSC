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
    (
        "panneau de personnalisation ancré à droite",
        "assets/css/site.css",
        "    right: auto;\n    left: 0;\n",
        "",
        "ne bascule plus vers la droite",
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
            banc_mutations.muter(copie, "assets/css/site.css", "    right: auto;\n    left: 0;\n", "")
            banc_mutations.lancer(OUTIL, copie)
        self.assertEqual(avant, (RACINE / "assets" / "css" / "site.css").read_bytes())


if __name__ == "__main__":
    unittest.main(verbosity=2)
