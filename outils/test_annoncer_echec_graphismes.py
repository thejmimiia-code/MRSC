#!/usr/bin/env python3
"""Éprouve `annoncer-echec-graphismes.py` : il dit le motif, et avoue ses angles morts.

Ce banc est né d'un échec réel : la première version du script imprimait les six
premières clés du relevé et **taisait le motif**, qui arrive en dernier. Une
annotation qui nomme la page et la largeur sans dire ce qui est refusé ne vaut
guère mieux que pas d'annotation du tout — d'où le premier cas ci-dessous.

Usage :
    python3 outils/test_annoncer_echec_graphismes.py
"""

from __future__ import annotations

import importlib.util
import io
import json
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent


def charger_module():
    spec = importlib.util.spec_from_file_location(
        "annoncer_echec_graphismes", RACINE / "outils" / "annoncer-echec-graphismes.py"
    )
    module = importlib.util.module_from_spec(spec)
    sys.modules["annoncer_echec_graphismes"] = module
    spec.loader.exec_module(module)
    return module


class TestAnnoncerEchec(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.outil = charger_module()

    def annoncer(self, dossier: Path) -> str:
        sortie = io.StringIO()
        with redirect_stdout(sortie):
            self.outil.annoncer(dossier)
        return sortie.getvalue()

    def ecrire(self, dossier: Path, nom: str, donnees: object) -> None:
        (dossier / nom).write_text(json.dumps(donnees), encoding="utf-8")

    def releve(self, motifs: list[str]) -> dict:
        """Un relevé de la forme écrite par `verifier-graphismes.cjs`."""
        return {
            "page": "apprendre.html",
            "largeur": 1024,
            "dpr": 1,
            "texte": 100,
            "disposition": "lecture",
            "mode": "normal",
            "source": "mondes-savoirs-hero-800.webp",
            "densite": 1.5384615384615385,
            "distorsion": 0.0,
            "erreurs": motifs,
        }

    def test_le_motif_est_dit_et_pas_seulement_la_situation(self) -> None:
        """Le défaut constaté : page, largeur, mode… et pas la raison."""
        with tempfile.TemporaryDirectory() as dossier:
            self.ecrire(Path(dossier), "releve.json", {"erreurs": [self.releve(["densité insuffisante"])]})
            sortie = self.annoncer(Path(dossier))
        self.assertIn("motif: densité insuffisante", sortie)
        self.assertIn("largeur=1024", sortie)
        self.assertIn("densite=1.54", sortie)

    def test_les_mutations_ne_sont_pas_annoncees_comme_des_pannes(self) -> None:
        """Une mutation réussit quand elle trouve ce qu'elle devait trouver."""
        with tempfile.TemporaryDirectory() as dossier:
            chemin = Path(dossier)
            self.ecrire(chemin, "mutation-distorsion.json", {"erreurs": [self.releve(["distorsion"])]})
            self.ecrire(chemin, "releve.json", {"erreurs": []})
            sortie = self.annoncer(chemin)
        self.assertIn("::notice", sortie)
        self.assertNotIn("::error title=Graphismes::mutation-distorsion.json : page", sortie)

    def test_une_mutation_qui_ne_mord_pas_est_un_echec(self) -> None:
        """Le silence d'une mutation est le seul cas où elle doit crier."""
        with tempfile.TemporaryDirectory() as dossier:
            chemin = Path(dossier)
            self.ecrire(chemin, "mutation-ancre.json", {"erreurs": []})
            self.ecrire(chemin, "releve.json", {"erreurs": [self.releve(["hors écran"])]})
            sortie = self.annoncer(chemin)
        self.assertIn("la mutation n'a provoqué aucun constat", sortie)

    def test_un_echec_sans_constat_est_dit_comme_tel(self) -> None:
        """Relevé valide et vide : l'échec vient d'une assertion, pas d'une mesure."""
        with tempfile.TemporaryDirectory() as dossier:
            self.ecrire(Path(dossier), "fiches-statistiques.json", {"erreurs": []})
            sortie = self.annoncer(Path(dossier))
        self.assertIn("aucun constat nulle part", sortie)
        self.assertIn("fiches-statistiques.json", sortie)

    def test_un_dossier_vide_est_nomme(self) -> None:
        with tempfile.TemporaryDirectory() as dossier:
            sortie = self.annoncer(Path(dossier))
        self.assertIn("aucun relevé", sortie)

    def test_un_releve_illisible_est_nomme(self) -> None:
        with tempfile.TemporaryDirectory() as dossier:
            (Path(dossier) / "releve.json").write_text("{ pas du json", encoding="utf-8")
            sortie = self.annoncer(Path(dossier))
        self.assertIn("illisible", sortie)

    def test_un_releve_d_une_autre_forme_est_nomme(self) -> None:
        """Ni liste `erreurs`, ni objet : le script ne devine pas, il le dit."""
        with tempfile.TemporaryDirectory() as dossier:
            self.ecrire(Path(dossier), "releve.json", {"constats": "inconnu"})
            sortie = self.annoncer(Path(dossier))
        self.assertIn("pas de liste", sortie)

    def test_plus_de_six_constats_sont_comptes(self) -> None:
        """Les annotations sont bornées : le reste est compté, pas passé sous silence."""
        with tempfile.TemporaryDirectory() as dossier:
            self.ecrire(
                Path(dossier),
                "releve.json",
                {"erreurs": [self.releve([f"motif {i}"]) for i in range(9)]},
            )
            sortie = self.annoncer(Path(dossier))
        self.assertIn("3 autre(s)", sortie)


if __name__ == "__main__":
    unittest.main()
