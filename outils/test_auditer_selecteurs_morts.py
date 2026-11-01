#!/usr/bin/env python3
"""Tests du relevé des classes mortes.

`auditer-selecteurs-morts.py` a servi, le 1er novembre 2026, à retirer 25 classes
qu'aucune page n'ouvrait — dont deux des quatre grilles dites « proportion ».
Un relevé qui n'a jamais désigné une faute ne prouve rien : ce banc plante donc
chaque cas dans une **vraie copie** du dépôt, jamais par lien symbolique, et
exige le verdict attendu, avec son message.

Les cas qui comptent :

- une classe ajoutée à la feuille et nulle part ailleurs doit être nommée ;
- la même classe, présente dans une page, ne doit plus l'être ;
- une classe **construite à l'exécution** doit rester indécidable, pas morte :
  c'est l'erreur qui aurait fait supprimer `adventure-learning-world-1..6` ;
- un nom cité seulement dans `docs/` reste mort : une trace n'est pas un usage ;
- une feuille absente ou un corpus trop mince doit sortir en **code 2**, en le
  disant — un relevé qui n'a pas lu sa source n'a pas le droit d'être vert.

Usage :
    python3 outils/test_auditer_selecteurs_morts.py
"""

from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RACINE / "outils"))

import banc_mutations  # noqa: E402

OUTIL = "auditer-selecteurs-morts.py"
FEUILLE = "assets/css/site.css"
PAGE = "index.html"
JOURNAL = "docs/rd/journal.md"


class TestSelecteursMorts(unittest.TestCase):
    def test_copie_intacte_ne_trouve_rien(self) -> None:
        with tempfile.TemporaryDirectory() as dossier:
            copie = Path(dossier) / "copie"
            banc_mutations.copie_complete(copie)
            resultat = banc_mutations.lancer(OUTIL, copie, arguments=("--verifier",))
        self.assertEqual(resultat.returncode, 0, resultat.stdout + resultat.stderr)
        self.assertIn("0 morte(s)", resultat.stdout)

    def test_classe_sans_instance_est_nommee(self) -> None:
        with tempfile.TemporaryDirectory() as dossier:
            copie = Path(dossier) / "copie"
            banc_mutations.copie_complete(copie)
            with (copie / FEUILLE).open("a", encoding="utf-8") as flux:
                flux.write("\n.panneau-fantome { color: red; }\n")
            resultat = banc_mutations.lancer(OUTIL, copie, arguments=("--verifier",))
        self.assertEqual(resultat.returncode, 1, resultat.stdout)
        self.assertIn("panneau-fantome", resultat.stdout)
        self.assertIn("morte", resultat.stdout)

    def test_classe_presente_dans_une_page_n_est_pas_morte(self) -> None:
        with tempfile.TemporaryDirectory() as dossier:
            copie = Path(dossier) / "copie"
            banc_mutations.copie_complete(copie)
            with (copie / FEUILLE).open("a", encoding="utf-8") as flux:
                flux.write("\n.panneau-reel { color: red; }\n")
            banc_mutations.muter(
                copie,
                PAGE,
                "</body>",
                '<div class="panneau-reel"></div>\n</body>',
            )
            resultat = banc_mutations.lancer(OUTIL, copie, arguments=("--verifier",))
        self.assertEqual(resultat.returncode, 0, resultat.stdout)
        self.assertNotIn("panneau-reel", resultat.stdout)

    def test_classe_construite_a_l_execution_reste_indecidable(self) -> None:
        """Le cas qui a failli coûter six règles vivantes.

        `assets/js/anglais-aventure.js` écrit
        `adventure-learning-world-${(index % 6) + 1}` : ces noms n'existent
        nulle part en toutes lettres. Un relevé naïf les aurait dits morts.
        """
        with tempfile.TemporaryDirectory() as dossier:
            copie = Path(dossier) / "copie"
            banc_mutations.copie_complete(copie)
            with (copie / FEUILLE).open("a", encoding="utf-8") as flux:
                flux.write("\n.carte-fantome-1 { color: red; }\n")
            banc_mutations.muter(
                copie,
                "assets/js/site.js",
                "(() => {",
                "(() => {\n  const pose = (element, rang) => { element.className = `carte-fantome-${rang}`; };",
            )
            resultat = banc_mutations.lancer(OUTIL, copie, arguments=("--verifier",))
        self.assertEqual(resultat.returncode, 0, resultat.stdout)
        self.assertIn("construite(s) à l'exécution", resultat.stdout)
        self.assertIn("carte-fantome-1", resultat.stdout)

    def test_nom_cite_seulement_dans_les_documents_reste_mort(self) -> None:
        with tempfile.TemporaryDirectory() as dossier:
            copie = Path(dossier) / "copie"
            banc_mutations.copie_complete(copie)
            with (copie / FEUILLE).open("a", encoding="utf-8") as flux:
                flux.write("\n.regle-racontee { color: red; }\n")
            with (copie / JOURNAL).open("a", encoding="utf-8") as flux:
                flux.write("\nUne note qui parle de `.regle-racontee` sans l'employer.\n")
            resultat = banc_mutations.lancer(OUTIL, copie, arguments=("--verifier",))
        self.assertEqual(resultat.returncode, 1, resultat.stdout)
        self.assertIn("regle-racontee", resultat.stdout)

    def test_commentaire_ne_fait_pas_une_instance(self) -> None:
        with tempfile.TemporaryDirectory() as dossier:
            copie = Path(dossier) / "copie"
            banc_mutations.copie_complete(copie)
            with (copie / FEUILLE).open("a", encoding="utf-8") as flux:
                flux.write("\n/* `.regle-commentee` n'existe pas. */\n.regle-commentee { color: red; }\n")
            resultat = banc_mutations.lancer(OUTIL, copie, arguments=("--verifier",))
        self.assertEqual(resultat.returncode, 1, resultat.stdout)
        self.assertIn("regle-commentee", resultat.stdout)

    def test_feuille_absente_sort_en_code_2(self) -> None:
        with tempfile.TemporaryDirectory() as dossier:
            copie = Path(dossier) / "copie"
            banc_mutations.copie_complete(copie)
            for feuille in ("assets/css/site.css", "assets/css/anglais-aventure.css"):
                (copie / feuille).unlink()
            resultat = banc_mutations.lancer(OUTIL, copie, arguments=("--verifier",))
        self.assertEqual(resultat.returncode, 2, resultat.stdout)
        self.assertIn("aucune feuille", resultat.stderr)

    def test_corpus_trop_mince_sort_en_code_2(self) -> None:
        """Un corpus vidé ne doit pas rendre toutes les classes mortes : il doit refuser."""
        with tempfile.TemporaryDirectory() as dossier:
            copie = Path(dossier) / "copie"
            banc_mutations.copie_complete(copie)
            for chemin in sorted(copie.rglob("*")):
                if not chemin.is_file():
                    continue
                if chemin.suffix.lower() in {".html", ".js", ".mjs", ".cjs", ".py", ".json", ".svg"}:
                    chemin.unlink()
            resultat = banc_mutations.lancer(OUTIL, copie, arguments=("--verifier",))
        self.assertEqual(resultat.returncode, 2, resultat.stdout)
        self.assertIn("source(s) lue(s)", resultat.stderr)


if __name__ == "__main__":
    unittest.main(verbosity=2)
