#!/usr/bin/env python3
"""Banc de `construire-index-communes.py` : chaque refus est exercé.

Ce que le banc prouve : l'index est bien le rendu des fichiers de département,
qu'il refuse un code qui désigne un autre département, un code en double, un nom
qui est un code, une collecte absente, un index périmé et un index trop petit
pour couvrir la France. Ce qu'il ne prouve pas : que les noms de communes
collectés sont justes — cela se lit dans la collecte, pas ici.

Usage :
    python3 outils/test_construire_index_communes.py
"""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

OUTIL = Path(__file__).resolve().parent / "construire-index-communes.py"


def commune(nom: str, code: str, prix: int | None = None) -> dict:
    entree = {"c": code, "n": nom, "x": 2.0, "y": 47.0, "p": 1000}
    if prix is not None:
        entree["pm"] = prix
    return entree


def ecrire_donnees(
    dossier: Path,
    departements: dict[str, list[dict]],
    collecte: str = "2026-11-15",
) -> None:
    dossier.mkdir(parents=True, exist_ok=True)
    (dossier / "_etat.json").write_text(
        json.dumps({"collecte": collecte, "fichiers": sorted(f"d-{c}.json" for c in departements)}),
        encoding="utf-8",
    )
    for code, communes in departements.items():
        (dossier / f"d-{code}.json").write_text(
            json.dumps({"d": code, "collecte": collecte, "communes": communes}, ensure_ascii=False),
            encoding="utf-8",
        )


class IndexCommunes(unittest.TestCase):
    def lancer(self, *arguments: str) -> subprocess.CompletedProcess:
        return subprocess.run(
            [sys.executable, str(OUTIL), *arguments],
            capture_output=True,
            text=True,
            check=False,
        )

    def test_index_nominal(self) -> None:
        """Deux départements, cinq communes : l'index est écrit, trié et vérifié."""
        with tempfile.TemporaryDirectory(prefix="mrsc-index-") as tmp:
            donnees = Path(tmp) / "donnees"
            ecrire_donnees(
                donnees,
                {
                    "69": [commune("Villeurbanne", "69266"), commune("Lyon", "69123"), commune("Y", "69001")],
                    "42": [commune("Saint-Étienne", "42218"), commune("Roanne", "42159", prix=2100)],
                },
            )
            sortie = Path(tmp) / "index.json"
            resultat = self.lancer("--donnees", str(donnees), "--sortie", str(sortie), "--minimum", "3")
            self.assertEqual(resultat.returncode, 0, resultat.stderr[-800:])
            index = json.loads(sortie.read_text(encoding="utf-8"))
            self.assertEqual(index["collecte"], "2026-11-15")
            self.assertEqual(
                [entree[0] for entree in index["communes"]],
                ["Lyon", "Roanne", "Saint-Étienne", "Villeurbanne", "Y"],
            )
            # Le drapeau suit la collecte : Lyon n'a pas de prix dans ce jeu,
            # Roanne en a un. La suggestion peut donc prévenir avant le clic.
            drapeaux = {entree[0]: entree[2] for entree in index["communes"]}
            self.assertEqual(drapeaux, {"Lyon": 0, "Roanne": 1, "Saint-Étienne": 0, "Villeurbanne": 0, "Y": 0})
            verification = self.lancer("--donnees", str(donnees), "--sortie", str(sortie), "--minimum", "3", "--verifier")
            self.assertEqual(verification.returncode, 0, verification.stderr[-800:])
            self.assertIn("5 communes", verification.stdout)

    def test_code_hors_departement(self) -> None:
        """Un code 75056 rangé dans le Rhône enverrait la recherche au mauvais endroit."""
        with tempfile.TemporaryDirectory(prefix="mrsc-index-") as tmp:
            donnees = Path(tmp) / "donnees"
            ecrire_donnees(donnees, {"69": [commune("Lyon", "75056")]})
            resultat = self.lancer("--donnees", str(donnees), "--sortie", str(Path(tmp) / "i.json"), "--minimum", "1")
            self.assertNotEqual(resultat.returncode, 0)
            self.assertIn("ne commence pas par le département", resultat.stderr)

    def test_code_en_double(self) -> None:
        """Deux communes du même code : l'une des deux n'existe pas."""
        with tempfile.TemporaryDirectory(prefix="mrsc-index-") as tmp:
            donnees = Path(tmp) / "donnees"
            ecrire_donnees(
                donnees,
                {"69": [commune("Lyon", "69123")], "42": [commune("Lyon bis", "69123")]},
            )
            resultat = self.lancer("--donnees", str(donnees), "--sortie", str(Path(tmp) / "i.json"), "--minimum", "1")
            self.assertNotEqual(resultat.returncode, 0)
            # Le second fichier porte un code d'un autre département : c'est ce
            # refus-là qui tombe d'abord, et les deux disent la même chose.
            self.assertRegex(resultat.stderr, "ne commence pas par le département|présent deux fois")

    def test_nom_qui_est_un_code(self) -> None:
        """« 69123 » à la place de « Lyon » afficherait un lieu qui n'existe pas."""
        with tempfile.TemporaryDirectory(prefix="mrsc-index-") as tmp:
            donnees = Path(tmp) / "donnees"
            ecrire_donnees(donnees, {"69": [commune("69123", "69123")]})
            resultat = self.lancer("--donnees", str(donnees), "--sortie", str(Path(tmp) / "i.json"), "--minimum", "1")
            self.assertNotEqual(resultat.returncode, 0)
            self.assertIn("est un code, pas un lieu", resultat.stderr)

    def test_nom_d_une_lettre_en_capitale(self) -> None:
        """« Y », commune de la Somme : un nom d'une lettre n'est pas un code.

        La première version du refus la rejetait, et une commune réelle aurait
        disparu de la recherche sans que rien ne le dise.
        """
        with tempfile.TemporaryDirectory(prefix="mrsc-index-") as tmp:
            donnees = Path(tmp) / "donnees"
            ecrire_donnees(donnees, {"80": [commune("Y", "80829")]})
            sortie = Path(tmp) / "i.json"
            resultat = self.lancer("--donnees", str(donnees), "--sortie", str(sortie), "--minimum", "1")
            self.assertEqual(resultat.returncode, 0, resultat.stderr[-800:])
            self.assertEqual(json.loads(sortie.read_text(encoding="utf-8"))["communes"], [["Y", "80829", 0]])

    def test_collecte_absente(self) -> None:
        """Sans `_etat.json`, il n'y a rien à indexer : un index vide mentirait."""
        with tempfile.TemporaryDirectory(prefix="mrsc-index-") as tmp:
            donnees = Path(tmp) / "donnees"
            donnees.mkdir()
            (donnees / "d-69.json").write_text(json.dumps({"d": "69", "communes": []}), encoding="utf-8")
            resultat = self.lancer("--donnees", str(donnees), "--sortie", str(Path(tmp) / "i.json"), "--minimum", "1")
            self.assertNotEqual(resultat.returncode, 0)
            self.assertIn("aucune collecte", resultat.stderr)

    def test_index_perime(self) -> None:
        """La collecte change, l'index ne bouge pas : c'est un écart, pas un détail."""
        with tempfile.TemporaryDirectory(prefix="mrsc-index-") as tmp:
            donnees = Path(tmp) / "donnees"
            ecrire_donnees(donnees, {"69": [commune("Lyon", "69123")]})
            sortie = Path(tmp) / "i.json"
            self.assertEqual(
                self.lancer("--donnees", str(donnees), "--sortie", str(sortie), "--minimum", "1").returncode, 0
            )
            ecrire_donnees(donnees, {"69": [commune("Lyon", "69123"), commune("Vénissieux", "69259")]})
            resultat = self.lancer("--donnees", str(donnees), "--sortie", str(sortie), "--minimum", "1", "--verifier")
            self.assertNotEqual(resultat.returncode, 0)
            self.assertIn("n'est plus le rendu de la collecte", resultat.stderr)

    def test_seuil_par_defaut(self) -> None:
        """Trois communes ne couvrent pas la France : le seuil réel refuse."""
        with tempfile.TemporaryDirectory(prefix="mrsc-index-") as tmp:
            donnees = Path(tmp) / "donnees"
            ecrire_donnees(donnees, {"69": [commune("Lyon", "69123"), commune("Y", "69001")]})
            resultat = self.lancer("--donnees", str(donnees), "--sortie", str(Path(tmp) / "i.json"))
            self.assertNotEqual(resultat.returncode, 0)
            self.assertIn("au moins 30000 attendues", resultat.stderr)

    def test_verificateur_sans_index(self) -> None:
        """Pas d'index : la recherche nationale répondrait « aucune commune »."""
        with tempfile.TemporaryDirectory(prefix="mrsc-index-") as tmp:
            donnees = Path(tmp) / "donnees"
            ecrire_donnees(donnees, {"69": [commune("Lyon", "69123")]})
            resultat = self.lancer(
                "--donnees", str(donnees), "--sortie", str(Path(tmp) / "absent.json"), "--minimum", "1", "--verifier"
            )
            self.assertNotEqual(resultat.returncode, 0)
            self.assertIn("aucun index de recherche", resultat.stderr)


if __name__ == "__main__":
    unittest.main(verbosity=2)
