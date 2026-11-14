#!/usr/bin/env python3
"""Banc de la collecte des carburants : les refus, un par un.

Le collecteur affirme refuser un flux trop court, un format inattendu, une
médiane invraisemblable, un fichier sans provenance et une licence fermée. Un
refus qu'on n'a jamais vu s'exercer reste une intention. Chaque cas monte donc un
serveur local qui sert la faute, lance le vrai collecteur ou le vrai vérificateur,
et exige le refus **nommé**.

Ce que le banc ne prouve pas : que le flux réel de la DGCCRF soit bien lu. Les
fixtures imitent ses colonnes, pas ses 9 800 stations ; cette lecture-là ne
s'éprouve que sur la source, et c'est écrit dans le dossier.

Usage :
    python3 outils/test_collecte_carburants.py
"""

from __future__ import annotations

import csv
import io
import json
import subprocess
import sys
import tempfile
import threading
import unittest
from datetime import date, timedelta
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
OUTIL = RACINE / "outils" / "collecter-carburants.py"
COLONNES = [
    "code_departement", "ville", "gazole_prix", "sp95_prix", "sp98_prix",
    "e10_prix", "e85_prix", "gplc_prix",
]
DEPARTEMENTS = [f"{n:02d}" for n in range(1, 20)] + ["2A", "2B"] + [f"{n:02d}" for n in range(21, 96)]


def flux(nombre: int = 3_100, departements: int = 60, prix: float = 1.85) -> bytes:
    """Un flux plausible : assez de stations et de départements pour publier."""
    tampon = io.StringIO()
    ecrivain = csv.DictWriter(tampon, fieldnames=COLONNES)
    ecrivain.writeheader()
    for i in range(nombre):
        departement = DEPARTEMENTS[i % departements]
        ecrivain.writerow(
            {
                "code_departement": departement,
                "ville": f"Commune {i}",
                "gazole_prix": f"{prix + (i % 7) / 100:.3f}",
                "sp95_prix": f"{prix + 0.10 + (i % 5) / 100:.3f}",
                "sp98_prix": "",
                "e10_prix": f"{prix + 0.05:.3f}",
                "e85_prix": "",
                "gplc_prix": "",
            }
        )
    return tampon.getvalue().encode("utf-8")


class Serveur:
    """Serveur local qui rend la réponse voulue, et rien d'autre."""

    def __init__(self, reponses: dict[str, tuple[int, bytes]]):
        self.reponses = reponses
        serveur = self

        class Gestionnaire(BaseHTTPRequestHandler):
            def do_GET(self) -> None:  # noqa: N802
                chemin = self.path.split("?")[0]
                statut, contenu = serveur.reponses.get(chemin, (404, b"absent"))
                self.send_response(statut)
                self.send_header("Content-Type", "text/csv")
                self.send_header("Content-Length", str(len(contenu)))
                self.end_headers()
                self.wfile.write(contenu)

            def log_message(self, *args) -> None:  # noqa: D102
                return

        self.serveur = ThreadingHTTPServer(("127.0.0.1", 0), Gestionnaire)
        self.port = self.serveur.server_address[1]

    def __enter__(self) -> "Serveur":
        threading.Thread(target=self.serveur.serve_forever, daemon=True).start()
        return self

    def __exit__(self, *args) -> None:
        self.serveur.shutdown()
        self.serveur.server_close()

    @property
    def base(self) -> str:
        return f"http://127.0.0.1:{self.port}"


class CollecteCarburants(unittest.TestCase):
    def collecter(self, contenu: bytes, tmp: Path) -> tuple[subprocess.CompletedProcess, Path]:
        with Serveur({"/flux.csv": (200, contenu)}) as serveur:
            sortie = tmp / "carburants.json"
            resultat = subprocess.run(
                [sys.executable, str(OUTIL), "--sortie", str(sortie), "--base", f"{serveur.base}/flux.csv"],
                capture_output=True, text=True, check=False,
            )
        return resultat, sortie

    def refuser(self, contenu: bytes, attendu: str) -> None:
        with tempfile.TemporaryDirectory(prefix="mrsc-carburants-") as tmp:
            resultat, sortie = self.collecter(contenu, Path(tmp))
            self.assertNotEqual(resultat.returncode, 0, f"le refus attendu n'a pas eu lieu : {resultat.stdout}")
            self.assertIn(attendu, resultat.stderr + resultat.stdout, resultat.stderr[-600:])
            self.assertFalse(sortie.exists(), "une collecte refusée a écrit un fichier")

    def test_collecte_nominale(self) -> None:
        with tempfile.TemporaryDirectory(prefix="mrsc-carburants-") as tmp:
            resultat, sortie = self.collecter(flux(), Path(tmp))
            self.assertEqual(resultat.returncode, 0, resultat.stderr[-1000:])
            donnees = json.loads(sortie.read_text(encoding="utf-8"))
            self.assertEqual(len(donnees["departements"]), 60)
            self.assertEqual(donnees["source"]["stations"], 3_100)
            self.assertEqual(len(donnees["source"]["sha256"]), 64)
            self.assertIn("Ouverte", donnees["source"]["licence"])
            self.assertNotIn("sp98", donnees["departements"]["01"], "aucun prix sp98 : aucune entrée")
            self.assertEqual(donnees["departements"]["01"]["gazole"]["stations"], 52)
            verification = subprocess.run(
                [sys.executable, str(OUTIL), "--verifier", "--sortie", str(sortie)],
                capture_output=True, text=True, check=False,
            )
            self.assertEqual(verification.returncode, 0, verification.stderr[-800:])

    def test_flux_tronque(self) -> None:
        self.refuser(flux(nombre=2_500), "au moins 3000 attendues")

    def test_format_inattendu(self) -> None:
        self.refuser(b"code_departement\n01\n", "au moins 3000 attendues")
        self.refuser(b"a,b,c\n1,2,3\n", "code_departement")

    def test_prix_invraisemblable(self) -> None:
        self.refuser(flux(prix=18.5), "fichier suspect")

    def test_couverture_trop_faible(self) -> None:
        self.refuser(flux(departements=20), "au moins 50 attendus")

    def test_verificateur_refuse_un_fichier_sans_provenance(self) -> None:
        with tempfile.TemporaryDirectory(prefix="mrsc-carburants-") as tmp:
            chemin = Path(tmp) / "carburants.json"
            chemin.write_text(
                json.dumps({"collecte_le": date.today().isoformat(), "source": {}, "departements": {"01": {}}}),
                encoding="utf-8",
            )
            resultat = subprocess.run(
                [sys.executable, str(OUTIL), "--verifier", "--sortie", str(chemin)],
                capture_output=True, text=True, check=False,
            )
            self.assertNotEqual(resultat.returncode, 0)
            self.assertIn("provenance incomplète", resultat.stderr)

    def test_verificateur_refuse_une_licence_fermee(self) -> None:
        with tempfile.TemporaryDirectory(prefix="mrsc-carburants-") as tmp:
            resultat, sortie = self.collecter(flux(), Path(tmp))
            self.assertEqual(resultat.returncode, 0, resultat.stderr[-600:])
            donnees = json.loads(sortie.read_text(encoding="utf-8"))
            donnees["source"]["licence"] = "tous droits réservés"
            sortie.write_text(json.dumps(donnees), encoding="utf-8")
            resultat = subprocess.run(
                [sys.executable, str(OUTIL), "--verifier", "--sortie", str(sortie)],
                capture_output=True, text=True, check=False,
            )
            self.assertNotEqual(resultat.returncode, 0)
            self.assertIn("licence non ouverte", resultat.stderr)

    def test_verificateur_refuse_une_date_future(self) -> None:
        with tempfile.TemporaryDirectory(prefix="mrsc-carburants-") as tmp:
            resultat, sortie = self.collecter(flux(), Path(tmp))
            self.assertEqual(resultat.returncode, 0, resultat.stderr[-600:])
            donnees = json.loads(sortie.read_text(encoding="utf-8"))
            donnees["collecte_le"] = (date.today() + timedelta(days=2)).isoformat()
            sortie.write_text(json.dumps(donnees), encoding="utf-8")
            resultat = subprocess.run(
                [sys.executable, str(OUTIL), "--verifier", "--sortie", str(sortie)],
                capture_output=True, text=True, check=False,
            )
            self.assertNotEqual(resultat.returncode, 0)
            self.assertIn("futur", resultat.stderr)

    def test_verificateur_refuse_une_mediane_aberrante(self) -> None:
        with tempfile.TemporaryDirectory(prefix="mrsc-carburants-") as tmp:
            resultat, sortie = self.collecter(flux(), Path(tmp))
            self.assertEqual(resultat.returncode, 0, resultat.stderr[-600:])
            donnees = json.loads(sortie.read_text(encoding="utf-8"))
            donnees["departements"]["01"]["gazole"]["mediane"] = 0.01
            sortie.write_text(json.dumps(donnees), encoding="utf-8")
            resultat = subprocess.run(
                [sys.executable, str(OUTIL), "--verifier", "--sortie", str(sortie)],
                capture_output=True, text=True, check=False,
            )
            self.assertNotEqual(resultat.returncode, 0)
            self.assertIn("invraisemblable", resultat.stderr)

    def test_verificateur_sans_collecte(self) -> None:
        with tempfile.TemporaryDirectory(prefix="mrsc-carburants-") as tmp:
            resultat = subprocess.run(
                [sys.executable, str(OUTIL), "--verifier", "--sortie", str(Path(tmp) / "absent.json")],
                capture_output=True, text=True, check=False,
            )
            self.assertNotEqual(resultat.returncode, 0)
            self.assertIn("aucune collecte", resultat.stderr)


if __name__ == "__main__":
    unittest.main(verbosity=2)
