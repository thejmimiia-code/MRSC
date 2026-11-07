#!/usr/bin/env python3
"""Banc de mutation des apparences : une porte qui ne mord pas ne protège rien.

Chaque cas plante une faute réelle dans une copie jetable du dépôt et exige que
`verifier-apparences.py` la refuse **en la nommant**. Le premier cas vérifie que
la copie intacte passe : sans lui, une porte toujours rouge semblerait verte.

Fautes plantées : choix dupliqué, jeton oublié, nom d'œuvre réintroduit,
contraste cassé, `color-scheme` retiré, encre des boutons remise en blanc,
animation ajoutée à un décor, décor retiré, couleurs forcées ignorées,
apparence figée dans une page HTML et synchronisation entre onglets coupée.

Usage :
    python3 outils/test_mutations_apparences.py
"""

from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RACINE / "outils"))

import banc_mutations  # noqa: E402

CSS = "assets/css/site.css"
JS = "assets/js/site.js"
OUTIL = "verifier-apparences.py"


def executer(dossier: Path):
    return banc_mutations.lancer(OUTIL, dossier)


class MutationsApparences(unittest.TestCase):
    def refuser(self, preparer, attendu: str) -> None:  # noqa: ANN001
        with tempfile.TemporaryDirectory(prefix="mrsc-apparences-") as tmp:
            dossier = Path(tmp)
            banc_mutations.copie_jetable(dossier)
            preparer(dossier)
            resultat = executer(dossier)
            self.assertNotEqual(resultat.returncode, 0, f"la faute n'a pas été refusée : {resultat.stdout}")
            self.assertIn(attendu, resultat.stderr + resultat.stdout, resultat.stderr[-800:])

    def test_copie_intacte_passe(self) -> None:
        with tempfile.TemporaryDirectory(prefix="mrsc-apparences-") as tmp:
            dossier = Path(tmp)
            banc_mutations.copie_jetable(dossier)
            resultat = executer(dossier)
            self.assertEqual(resultat.returncode, 0, resultat.stderr)

    def test_choix_duplique(self) -> None:
        self.refuser(lambda d: banc_mutations.muter(
            d, JS, 'value: "arcade", label: "Salle d\'arcade"',
            'value: "systeme", label: "Doublon"'), "six apparences")

    def test_jeton_oublie(self) -> None:
        self.refuser(lambda d: banc_mutations.muter(
            d, CSS, "  --blue-soft: #1c2a45;\n", ""), "liste fermée")

    def test_nom_protege(self) -> None:
        self.refuser(lambda d: banc_mutations.muter(
            d, CSS, "/* ===========================================================================\n   Apparences du site",
            "/* Stranger Things\n   ===========================================================================\n   Apparences du site"), "nom protégé")

    def test_contraste_casse(self) -> None:
        self.refuser(lambda d: banc_mutations.muter(
            d, CSS, "  --ink: #eef2fb;", "  --ink: #111827;"), "sous le seuil")

    def test_color_scheme_retire(self) -> None:
        self.refuser(lambda d: banc_mutations.muter(
            d, CSS, "  color-scheme: dark;", "  color-scheme: light;"), "color-scheme")

    def test_encre_bouton_remise_en_blanc(self) -> None:
        self.refuser(lambda d: banc_mutations.muter(
            d, CSS, "  --on-accent: #0b1220;", "  --on-accent: #fff;"), "encre sombre")

    def test_animation_ajoutee_au_decor(self) -> None:
        self.refuser(lambda d: banc_mutations.muter(
            d, CSS, 'html[data-apparence="bobine"] body {\n  background-image:',
            'html[data-apparence="bobine"] body {\n  animation: clignote 2s infinite;\n  background-image:'), "animation")

    def test_decor_retire(self) -> None:
        self.refuser(lambda d: banc_mutations.muter(
            d, CSS, 'html[data-apparence="arcade"] body {',
            'html[data-apparence="arcade"] main {'), "décor statique")

    def test_couleurs_forcees_ignorees(self) -> None:
        self.refuser(lambda d: banc_mutations.muter(
            d, CSS, "html[data-apparence] body { background-image: none !important; }",
            "html[data-apparence] body { color: inherit; }"), "couleurs forcées")

    def test_apparence_figee_dans_une_page(self) -> None:
        self.refuser(lambda d: banc_mutations.muter(
            d, "index.html", '<html lang="fr"',
            '<html lang="fr" data-apparence="clair"'), "figent une apparence")

    def test_synchronisation_coupee(self) -> None:
        self.refuser(lambda d: banc_mutations.muter(
            d, JS, "event.key === CLE_APPARENCE", 'event.key === "autre"'), "synchronisation")


if __name__ == "__main__":
    unittest.main(verbosity=2)
