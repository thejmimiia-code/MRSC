#!/usr/bin/env python3
"""Banc de la collecte des loyers : les refus, un par un.

Le collecteur affirme refuser une licence fermée, une fiche sans ressource
d'agglomérations, un filtre qui ne sélectionne plus l'ensemble des logements,
un trop petit nombre de territoires, une année mélangée, un code d'observatoire
inattendu, un territoire en double, une médiane invraisemblable et une réponse
tronquée. Un refus qu'on n'a jamais vu s'exercer reste une intention : chaque
cas monte un serveur local qui sert la faute, lance le vrai collecteur, et exige
le refus **nommé**.

Les fixtures imitent le format réel, relevé le 14 novembre 2026 sur l'API
publique : une fiche de jeu de données avec sa licence et ses ressources
annuelles, puis des pages de l'API tabulaire (`data`, `links`, `meta.total`)
dont les valeurs ont les types et les formes servis par la source — `13.3` pour
un loyer au mètre carré, `700` pour un loyer mensuel, `B1300` et `B2B00` pour
les codes d'observatoire. Ce que le banc ne prouve pas : que la source réponde
ainsi le jour où la collecte tourne. Cette lecture-là ne s'éprouve que sur la
source, et c'est écrit dans le dossier.

Usage :
    python3 outils/test_collecte_loyers.py
"""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import threading
import unittest
from datetime import date, timedelta
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

RACINE = Path(__file__).resolve().parent.parent
OUTIL = RACINE / "outils" / "collecter-loyers.py"
CHEMIN_JEU = "/api/1/datasets/resultats-nationaux-des-observatoires-locaux-des-loyers/"
#: Des couples (code d'observatoire, agglomération) réels, pour que les fixtures
#: ne racontent pas un territoire qui n'existe pas.
TERRITOIRES = [
    ("B1300", "Agglomérations d'Aix-Marseille et Arles"),
    ("B2B00", "Agglomération de Bastia"),
    ("B2500", "Agglomération de Besançon"),
    ("B2500", "Agglomération de Montbéliard"),
    ("B3300", "Agglomération de Bordeaux"),
    ("B6900", "Agglomération de Lyon"),
    ("B7500", "Agglomération de Paris"),
    ("B3100", "Agglomération de Toulouse"),
    ("B4400", "Agglomération de Nantes"),
    ("B3500", "Agglomération de Rennes"),
]


def ligne(observatoire: str, nom: str, annee: int = 2025, loyer: float = 12.4,
          mensuel: int = 640, surface: int = 58, logements: int = 12_000,
          observations: int = 3_000, methode: str = "Estimation directe") -> dict:
    """Une ligne telle que l'API tabulaire la sert : types réels, pas des chaînes."""
    return {
        "Observatory": observatoire,
        "agglomeration": nom,
        "Data_year": annee,
        "loyer_median": loyer,
        "loyer_mensuel_median": mensuel,
        "surface_moyenne": surface,
        "nombre_logements": logements,
        "nombre_observations": observations,
        "methodologie_production": methode,
    }


def lignes(nombre: int = 40, annee: int = 2025) -> list[dict]:
    """Assez de territoires pour publier, et tous distincts."""
    resultat: list[dict] = []
    for i in range(nombre):
        observatoire, nom = TERRITOIRES[i % len(TERRITOIRES)]
        suffixe = f" ({i})" if i >= len(TERRITOIRES) else ""
        resultat.append(
            ligne(
                observatoire,
                nom + suffixe,
                annee=annee,
                loyer=round(8.0 + (i % 17) * 0.7, 1),
                mensuel=500 + (i % 23) * 25,
                surface=42 + (i % 13),
                logements=900 + i * 37,
                observations=200 + i * 11,
            )
        )
    return resultat


def fiche(ressources: list[dict] | None = None, licence: str = "lov2") -> dict:
    if ressources is None:
        ressources = [
            {
                "id": "aaaaaaaa-0000-0000-0000-000000000025",
                "title": "Loyers 2025 dans les agglomérations observées par les observatoires du réseau",
                "format": "csv",
                "type": "main",
                "last_modified": "2026-10-28T15:13:11+00:00",
                "url": "https://www.observatoires-des-loyers.org/datagouv/2025/Base_OP_2025_Nationale.csv",
            },
            {
                "id": "aaaaaaaa-0000-0000-0000-000000000024",
                "title": "Loyers 2024 dans les agglomérations observées par les observatoires du réseau",
                "format": "csv",
                "type": "main",
                "last_modified": "2026-10-14T17:17:16+00:00",
                "url": "https://www.observatoires-des-loyers.org/datagouv/2024/Base_OP_2024_Nationale.csv",
            },
        ]
    return {
        "id": "56fd8e8788ee387079c352f7",
        "title": "Résultats nationaux des observatoires locaux des loyers",
        "license": licence,
        "organization": {"name": "Observatoires Locaux des Loyers"},
        "resources": ressources,
    }


class Serveur:
    """Serveur local : la fiche, puis les pages, et rien d'autre."""

    def __init__(self, fiche_servie: dict, rangees: list[dict], total_annonce: int | None = None,
                 page_size: int = 100):
        self.fiche = fiche_servie
        self.rangees = rangees
        self.total_annonce = len(rangees) if total_annonce is None else total_annonce
        self.page_size = page_size
        serveur = self

        class Gestionnaire(BaseHTTPRequestHandler):
            def do_GET(self) -> None:  # noqa: N802
                url = urlparse(self.path)
                if url.path == CHEMIN_JEU:
                    corps = json.dumps(serveur.fiche, ensure_ascii=False).encode("utf-8")
                    self.repondre(200, corps)
                    return
                if url.path.startswith("/tabular/") and url.path.endswith("/data/"):
                    page = int(parse_qs(url.query).get("page", ["1"])[0])
                    debut = (page - 1) * serveur.page_size
                    paquet = serveur.rangees[debut:debut + serveur.page_size]
                    reste = debut + serveur.page_size < serveur.total_annonce
                    charge = {
                        "data": paquet,
                        "links": {
                            "next": f"{url.path}?page={page + 1}" if reste else None,
                            "prev": None,
                            "profile": f"{url.path.replace('/data/', '/profile/')}",
                        },
                        "meta": {"page": page, "page_size": serveur.page_size, "total": serveur.total_annonce},
                    }
                    self.repondre(200, json.dumps(charge, ensure_ascii=False).encode("utf-8"))
                    return
                self.repondre(404, b"absent")

            def repondre(self, statut: int, corps: bytes) -> None:
                self.send_response(statut)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(corps)))
                self.end_headers()
                self.wfile.write(corps)

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


class CollecteLoyers(unittest.TestCase):
    def collecter(self, fiche_servie: dict, rangees: list[dict], tmp: Path,
                  total_annonce: int | None = None):
        with Serveur(fiche_servie, rangees, total_annonce=total_annonce) as serveur:
            sortie = tmp / "loyers.json"
            resultat = subprocess.run(
                [sys.executable, str(OUTIL), "--sortie", str(sortie), "--base", serveur.base],
                capture_output=True, text=True, check=False,
            )
        return resultat, sortie

    def refuser(self, fiche_servie: dict, rangees: list[dict], attendu: str,
                total_annonce: int | None = None) -> None:
        with tempfile.TemporaryDirectory(prefix="mrsc-loyers-") as tmp:
            resultat, sortie = self.collecter(fiche_servie, rangees, Path(tmp), total_annonce=total_annonce)
            self.assertNotEqual(resultat.returncode, 0, f"le refus attendu n'a pas eu lieu : {resultat.stdout}")
            self.assertIn(attendu, resultat.stderr + resultat.stdout, resultat.stderr[-800:])
            self.assertFalse(sortie.exists(), "une collecte refusée a écrit un fichier")

    def test_collecte_nominale(self) -> None:
        with tempfile.TemporaryDirectory(prefix="mrsc-loyers-") as tmp:
            resultat, sortie = self.collecter(fiche(), lignes(), Path(tmp))
            self.assertEqual(resultat.returncode, 0, resultat.stderr[-1200:])
            donnees = json.loads(sortie.read_text(encoding="utf-8"))
            self.assertEqual(len(donnees["territoires"]), 40)
            self.assertEqual(donnees["annee"], 2025)
            self.assertIn("Ouverte", donnees["source"]["licence"])
            self.assertEqual(len(donnees["source"]["sha256"]), 64)
            self.assertEqual(donnees["source"]["ressource_id"], "aaaaaaaa-0000-0000-0000-000000000025")
            self.assertEqual(donnees["source"]["lignes"], 40)
            premier = donnees["territoires"][0]
            self.assertLessEqual(premier["nom"].lower(), donnees["territoires"][1]["nom"].lower())
            self.assertIsInstance(premier["loyer_median"], float)
            self.assertIsInstance(premier["loyer_mensuel_median"], int)
            verification = subprocess.run(
                [sys.executable, str(OUTIL), "--verifier", "--sortie", str(sortie)],
                capture_output=True, text=True, check=False,
            )
            self.assertEqual(verification.returncode, 0, verification.stderr[-800:])

    def test_millesime_le_plus_recent(self) -> None:
        """Deux années dans la fiche : la plus récente gagne, pas la première."""
        ressources = list(reversed(fiche()["resources"]))
        with tempfile.TemporaryDirectory(prefix="mrsc-loyers-") as tmp:
            resultat, sortie = self.collecter(fiche(ressources=ressources), lignes(), Path(tmp))
            self.assertEqual(resultat.returncode, 0, resultat.stderr[-800:])
            donnees = json.loads(sortie.read_text(encoding="utf-8"))
            self.assertEqual(donnees["annee"], 2025)
            self.assertIn("2025", donnees["source"]["ressource_titre"])

    def test_licence_fermee(self) -> None:
        self.refuser(fiche(licence="tous droits réservés"), lignes(), "licence non ouverte")

    def test_aucune_ressource_agglomerations(self) -> None:
        autre = [{"id": "b", "title": "Résultats par zone élémentaire", "format": "zip"}]
        self.refuser(fiche(ressources=autre), lignes(), "aucune ressource")

    def test_trop_peu_de_territoires(self) -> None:
        self.refuser(fiche(), lignes(nombre=20), "au moins 30")

    def test_filtre_trop_large(self) -> None:
        """Le filtre de l'ensemble ne sélectionne plus : sous-populations servies."""
        self.refuser(fiche(), lignes(nombre=250), "ne sélectionne plus")

    def test_annee_melangee(self) -> None:
        rangees = lignes()
        rangees[3]["Data_year"] = 2024
        self.refuser(fiche(), rangees, "millésime mélangé")

    def test_code_observatoire_inattendu(self) -> None:
        rangees = lignes()
        rangees[0]["Observatory"] = "X1300"
        self.refuser(fiche(), rangees, "code d’observatoire inattendu")

    def test_territoire_en_double(self) -> None:
        rangees = lignes()
        rangees[1] = dict(rangees[0])
        self.refuser(fiche(), rangees, "deux lignes pour le même territoire")

    def test_loyer_aberrant(self) -> None:
        rangees = lignes()
        rangees[2]["loyer_median"] = 45.0
        self.refuser(fiche(), rangees, "fichier suspect")

    def test_loyer_mensuel_absent(self) -> None:
        rangees = lignes()
        del rangees[2]["loyer_mensuel_median"]
        self.refuser(fiche(), rangees, "absente ou non numérique")

    def test_reponse_tronquee(self) -> None:
        self.refuser(fiche(), lignes(nombre=40), "réponse tronquée", total_annonce=60)

    def test_verificateur_refuse_un_fichier_sans_provenance(self) -> None:
        with tempfile.TemporaryDirectory(prefix="mrsc-loyers-") as tmp:
            chemin = Path(tmp) / "loyers.json"
            chemin.write_text(
                json.dumps({"collecte_le": date.today().isoformat(), "source": {}, "territoires": []}),
                encoding="utf-8",
            )
            resultat = subprocess.run(
                [sys.executable, str(OUTIL), "--verifier", "--sortie", str(chemin)],
                capture_output=True, text=True, check=False,
            )
            self.assertNotEqual(resultat.returncode, 0)
            self.assertIn("provenance incomplète", resultat.stderr)

    def test_verificateur_refuse_une_licence_fermee(self) -> None:
        with tempfile.TemporaryDirectory(prefix="mrsc-loyers-") as tmp:
            resultat, sortie = self.collecter(fiche(), lignes(), Path(tmp))
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
        with tempfile.TemporaryDirectory(prefix="mrsc-loyers-") as tmp:
            resultat, sortie = self.collecter(fiche(), lignes(), Path(tmp))
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
        with tempfile.TemporaryDirectory(prefix="mrsc-loyers-") as tmp:
            resultat, sortie = self.collecter(fiche(), lignes(), Path(tmp))
            self.assertEqual(resultat.returncode, 0, resultat.stderr[-600:])
            donnees = json.loads(sortie.read_text(encoding="utf-8"))
            donnees["territoires"][0]["loyer_median"] = 0.1
            sortie.write_text(json.dumps(donnees), encoding="utf-8")
            resultat = subprocess.run(
                [sys.executable, str(OUTIL), "--verifier", "--sortie", str(sortie)],
                capture_output=True, text=True, check=False,
            )
            self.assertNotEqual(resultat.returncode, 0)
            self.assertIn("invraisemblable", resultat.stderr)

    def test_verificateur_sans_collecte(self) -> None:
        with tempfile.TemporaryDirectory(prefix="mrsc-loyers-") as tmp:
            resultat = subprocess.run(
                [sys.executable, str(OUTIL), "--verifier", "--sortie", str(Path(tmp) / "absent.json")],
                capture_output=True, text=True, check=False,
            )
            self.assertNotEqual(resultat.returncode, 0)
            self.assertIn("aucune collecte", resultat.stderr)


if __name__ == "__main__":
    unittest.main(verbosity=2)
