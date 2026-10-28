#!/usr/bin/env python3
"""Tests du contrôle de l'inventaire des contrôles.

`verifier-inventaire-controles.py` garde `docs/rd/inventaire-controles.md` : un
outil ajouté sans ligne, un fichier de test annoncé qui n'existe pas, un chemin
cité qui a bougé. Ce contrôle-là aussi doit prouver qu'il mord — sinon il
protège l'inventaire exactement comme un cadenas sans pêne.

Les fautes sont plantées dans une copie complète du dépôt, comme pour la porte
des pages statiques : l'outil lit des chemins réels.

Usage :
    python3 outils/test_verifier_inventaire_controles.py
"""

from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RACINE / "outils"))

import banc_mutations  # noqa: E402

OUTIL = "verifier-inventaire-controles.py"
DOC = "docs/rd/inventaire-controles.md"


class TestInventaireControles(unittest.TestCase):
    def test_copie_intacte_passe(self) -> None:
        with tempfile.TemporaryDirectory() as dossier:
            copie = Path(dossier) / "copie"
            banc_mutations.copie_complete(copie)
            resultat = banc_mutations.lancer(OUTIL, copie)
        self.assertEqual(resultat.returncode, 0, resultat.stdout + resultat.stderr)
        self.assertIn("Inventaire des contrôles", resultat.stdout)

    def test_outil_ajoute_sans_ligne_refuse(self) -> None:
        """Le cas qui compte : un nouvel outil ne peut pas entrer sans décision écrite."""
        with tempfile.TemporaryDirectory() as dossier:
            copie = Path(dossier) / "copie"
            banc_mutations.copie_complete(copie)
            (copie / "outils" / "verifier-nouveaute.py").write_text(
                "#!/usr/bin/env python3\n", encoding="utf-8"
            )
            resultat = banc_mutations.lancer(OUTIL, copie)
        self.assertEqual(resultat.returncode, 1, resultat.stdout)
        self.assertIn("outils/verifier-nouveaute.py", resultat.stderr)
        self.assertIn("absents de l'inventaire", resultat.stderr)

    def test_ligne_retiree_refuse(self) -> None:
        """Retirer une ligne de l'inventaire doit être vu, pas silencieux."""
        with tempfile.TemporaryDirectory() as dossier:
            copie = Path(dossier) / "copie"
            banc_mutations.copie_complete(copie)
            banc_mutations.muter(
                copie,
                DOC,
                "| `outils/verifier-fusions.py` | Fusion et suppression de branche sans perte | Vert de CI seulement | `aucun-test` |\n",
                "",
            )
            resultat = banc_mutations.lancer(OUTIL, copie)
        self.assertEqual(resultat.returncode, 1, resultat.stdout)
        self.assertIn("outils/verifier-fusions.py", resultat.stderr)

    def test_test_annonce_absent_refuse(self) -> None:
        """Un statut qui prétend s'appuyer sur un test doit citer un test réel."""
        with tempfile.TemporaryDirectory() as dossier:
            copie = Path(dossier) / "copie"
            banc_mutations.copie_complete(copie)
            banc_mutations.muter(
                copie,
                DOC,
                "| `test_mutations_affichages.py` (5 mutations) | `banc` |",
                "| `test_qui_n_existe_pas.py` (5 mutations) | `banc` |",
            )
            resultat = banc_mutations.lancer(OUTIL, copie)
        self.assertEqual(resultat.returncode, 1, resultat.stdout)
        self.assertIn("test_qui_n_existe_pas.py", resultat.stderr)

    def test_statut_inconnu_refuse(self) -> None:
        with tempfile.TemporaryDirectory() as dossier:
            copie = Path(dossier) / "copie"
            banc_mutations.copie_complete(copie)
            banc_mutations.muter(
                copie,
                DOC,
                "| `outils/verifier-maj-amont.py` | Retard du moteur embarqué sur l'amont | Vert de CI seulement | `aucun-test` |",
                "| `outils/verifier-maj-amont.py` | Retard du moteur embarqué sur l'amont | Vert de CI seulement | `peut-etre` |",
            )
            resultat = banc_mutations.lancer(OUTIL, copie)
        self.assertEqual(resultat.returncode, 1, resultat.stdout)
        self.assertIn("statut inconnu", resultat.stderr)


if __name__ == "__main__":
    unittest.main(verbosity=2)
