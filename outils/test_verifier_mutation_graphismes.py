#!/usr/bin/env python3
"""Banc de `verifier-mutation-graphismes.py`, sans navigateur.

Le contrôle qu'il garde tourne dans le job `graphismes` : trois mutations
internes, trois échecs attendus. La CI vérifiait le **code de sortie** — jamais
la raison. Un contrôle qui céderait pour une panne sans rapport aurait passé.

Six cas, tous hors ligne :

1. le rapport d'une passe `distorsion` porte « distorsion » → accepté ;
2. le même rapport jugé pour `ancre` → refusé, et le message dit ce qui a été
   constaté à la place ;
3. un rapport sans aucune erreur → refusé (l'échec venait d'ailleurs) ;
4. un rapport absent → refusé, avec la raison : une mutation non mesurée ne
   prouve rien ;
5. un rapport illisible → refusé, sans trace d'exception ;
6. les chaînes attendues existent bien dans `verifier-graphismes.cjs` — le banc
   **lit le script** au lieu de recopier ses messages, pour qu'une reformulation
   fasse échouer ce test plutôt que de le rendre faux.

Usage :
    python3 outils/test_verifier_mutation_graphismes.py
"""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RACINE / "outils"))

import banc_mutations  # noqa: E402

OUTIL = "verifier-mutation-graphismes.py"
SCRIPT_GRAPHISMES = "verifier-graphismes.cjs"


def rapport(*erreurs: str) -> dict:
    """Rapport minimal au format de `verifier-graphismes.cjs`."""
    return {
        "perimetre": "banc",
        "mutation": "banc",
        "releves": [{"page": "index.html", "erreurs": list(erreurs)}],
        "erreurs": [{"page": "index.html", "erreurs": list(erreurs)}] if erreurs else [],
    }


def executer(mutation: str, contenu: dict | None = None, brut: str | None = None, absent: bool = False):
    with tempfile.TemporaryDirectory(prefix="mrsc-mutation-graphismes-") as dossier:
        chemin = Path(dossier) / "mutation.json"
        copie = Path(dossier) / "copie"
        banc_mutations.copie_complete(copie)
        if brut is not None:
            chemin.write_text(brut, encoding="utf-8")
        elif contenu is not None:
            chemin.write_text(json.dumps(contenu), encoding="utf-8")
        if absent:
            chemin.unlink(missing_ok=True)
        return banc_mutations.lancer(OUTIL, copie, arguments=(str(chemin), mutation))


class TestMutationGraphismes(unittest.TestCase):
    def test_erreur_attendue_acceptee(self) -> None:
        resultat = executer("distorsion", rapport("ratio de boîte différent de la source", "distorsion"))
        self.assertEqual(resultat.returncode, 0, resultat.stdout + resultat.stderr)
        self.assertIn("OK — mutation « distorsion »", resultat.stdout)
        self.assertIn("2 erreur(s) au total", resultat.stdout)

    def test_erreur_d_une_autre_mutation_refusee(self) -> None:
        """Le contrôle a échoué, mais pas pour la raison plantée."""
        resultat = executer("ancre", rapport("distorsion"))
        self.assertEqual(resultat.returncode, 1, resultat.stdout)
        self.assertIn("sans constater « ancre »", resultat.stdout)
        self.assertIn("distorsion", resultat.stdout)

    def test_rapport_sans_erreur_refuse(self) -> None:
        resultat = executer("densite", rapport())
        self.assertEqual(resultat.returncode, 1, resultat.stdout)
        self.assertIn("aucune erreur", resultat.stdout)

    def test_rapport_absent_refuse(self) -> None:
        resultat = executer("densite", absent=True)
        self.assertEqual(resultat.returncode, 1, resultat.stdout)
        self.assertIn("rapport absent", resultat.stdout)
        self.assertIn("ne prouve rien", resultat.stdout)

    def test_rapport_illisible_refuse_sans_trace(self) -> None:
        resultat = executer("densite", brut="{ ceci n'est pas du JSON")
        self.assertEqual(resultat.returncode, 1, resultat.stdout)
        self.assertIn("rapport illisible", resultat.stdout)
        self.assertNotIn("Traceback", resultat.stderr)

    def test_les_chaines_attendues_existent_dans_le_script(self) -> None:
        """Le banc lit le contrôle, il ne recopie pas ses messages."""
        texte = (RACINE / "outils" / SCRIPT_GRAPHISMES).read_text(encoding="utf-8")
        import importlib.util

        specification = importlib.util.spec_from_file_location(
            "verifier_mutation_graphismes", RACINE / "outils" / OUTIL
        )
        module = importlib.util.module_from_spec(specification)
        specification.loader.exec_module(module)
        for mutation, attendu in module.ATTENDU.items():
            self.assertIn(
                attendu,
                texte,
                f"« {attendu} » n'existe plus dans {SCRIPT_GRAPHISMES} : "
                f"la mutation « {mutation} » ne peut plus être vérifiée",
            )


if __name__ == "__main__":
    unittest.main(verbosity=2)
