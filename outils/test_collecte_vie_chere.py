#!/usr/bin/env python3
"""Banc de la collecte des coûts : la machine qui refuse les fausses données.

Le collecteur prétend refuser une source muette, une licence fermée, un fichier
tronqué, un prix aberrant et un prix en Alsace-Moselle. Un refus qu'on n'a
jamais vu s'exercer est une affirmation. Chaque cas monte donc un serveur local
qui sert une réponse fautive, lance le vrai collecteur contre lui, et exige le
refus **nommé**.

Ce que le banc ne prouve pas : que les vrais fichiers DVF soient bien lus. Ses
fixtures imitent les colonnes, pas les 47 Mo réels — cette lecture-là ne
s'éprouve que sur la source, et c'est écrit dans le dossier.

Usage :
    python3 outils/test_collecte_vie_chere.py
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
import zipfile
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
OUTIL = RACINE / "outils" / "collecter-vie-chere.py"
COLONNES = [
    "Date mutation", "Nature mutation", "Valeur fonciere", "No voie", "Type de voie",
    "Code postal", "Commune", "Code departement", "Code commune", "Type local",
    "Surface reelle bati", "Nombre pieces principales",
]


def communes_factices(nombre: int = 30_400) -> list[dict]:
    """Assez de communes pour franchir le seuil, réparties sur les départements."""
    communes = []
    departements = [f"{d:02d}" for d in range(1, 96)] + ["2A", "2B"]
    for i in range(nombre):
        departement = departements[i % len(departements)]
        code = f"{departement}{10 + (i // len(departements)):03d}"
        communes.append(
            {
                "nom": f"Commune {i}",
                "code": code,
                "population": 100 + i % 5000,
                "centre": {"type": "Point", "coordinates": [2.0 + (i % 100) / 100, 46.0 + (i % 80) / 100]},
                "departement": {"code": departement, "nom": f"Département {departement}"},
            }
        )
    return communes


def dvf_zip(lignes: list[dict], entete: list[str] | None = None) -> bytes:
    tampon = io.BytesIO()
    with zipfile.ZipFile(tampon, "w", zipfile.ZIP_DEFLATED) as archive:
        texte = io.StringIO()
        ecrivain = csv.DictWriter(texte, fieldnames=entete or COLONNES, delimiter="|", extrasaction="ignore")
        ecrivain.writeheader()
        for ligne in lignes:
            ecrivain.writerow(ligne)
        archive.writestr("valeursfoncieres-2025-s1.txt", texte.getvalue())
    return tampon.getvalue()


def vente(code: str, departement: str, prix: float, surface: float, type_local: str = "Appartement") -> dict:
    return {
        "Nature mutation": "Vente",
        "Valeur fonciere": f"{prix:.2f}",
        "Code departement": departement,
        "Code commune": code[len(departement):],
        "Type local": type_local,
        "Surface reelle bati": f"{surface:.0f}",
    }


class Serveur:
    """Serveur local qui rend les réponses voulues, et rien d'autre."""

    def __init__(self, reponses: dict[str, tuple[int, bytes]]):
        self.reponses = reponses
        serveur = self

        class Gestionnaire(BaseHTTPRequestHandler):
            def do_GET(self) -> None:  # noqa: N802
                chemin = self.path.split("?")[0]
                statut, contenu = serveur.reponses.get(chemin, (404, b"absent"))
                self.send_response(statut)
                self.send_header("Content-Type", "application/octet-stream")
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

    def fiche_dvf(self, chemins: list[str], licence: str = "lov2") -> bytes:
        ressources = [
            {
                "title": f"Valeurs foncières 2025 - Semestre {i + 1}",
                "url": f"{self.base}{chemin}",
                "format": "txt.zip",
                "checksum": {"type": "sha1", "value": "0" * 40},
            }
            for i, chemin in enumerate(chemins)
        ]
        return json.dumps({"license": licence, "resources": ressources}).encode("utf-8")


def communes_et_dvf(lignes: list[dict] | None = None, licence: str = "lov2") -> dict[str, tuple[int, bytes]]:
    lignes = lignes if lignes is not None else [
        vente("01010", "01", 200_000, 50),
        vente("01010", "01", 210_000, 50),
        vente("01010", "01", 220_000, 50),
        vente("01110", "02", 150_000, 60, "Maison"),
    ]
    return {
        "/communes": (200, json.dumps(communes_factices()).encode("utf-8")),
        "/dvf-1.txt.zip": (200, dvf_zip(lignes)),
        "_licence": licence,  # consommé par le lanceur, jamais servi
    }


class CollecteVieChere(unittest.TestCase):
    def executer(self, reponses: dict, tmp: Path) -> tuple[subprocess.CompletedProcess, Path]:
        """Monte le serveur, la fiche DVF et le collecteur ; rend le résultat et la sortie."""
        licence = reponses.pop("_licence", "lov2")
        fichiers = [chemin for chemin in reponses if chemin.startswith("/dvf")]
        with Serveur(reponses) as serveur:
            serveur.reponses["/dataset"] = (200, serveur.fiche_dvf(fichiers, licence=licence))
            sortie = tmp / "donnees"
            resultat = subprocess.run(
                [
                    sys.executable, str(OUTIL),
                    "--sortie", str(sortie),
                    "--base-geo", f"{serveur.base}/communes",
                    "--base-data", f"{serveur.base}/dataset",
                ],
                capture_output=True, text=True, check=False,
            )
        return resultat, sortie

    def refuser(self, reponses: dict, attendu: str) -> None:
        with tempfile.TemporaryDirectory(prefix="mrsc-couts-") as tmp:
            resultat, sortie = self.executer(dict(reponses), Path(tmp))
            self.assertNotEqual(resultat.returncode, 0, f"le refus attendu n'a pas eu lieu : {resultat.stdout}")
            self.assertIn(attendu, resultat.stderr + resultat.stdout, resultat.stderr[-800:])
            self.assertFalse(sortie.exists(), "une collecte refusée a écrit des fichiers")

    def test_collecte_nominale(self) -> None:
        with tempfile.TemporaryDirectory(prefix="mrsc-couts-") as tmp:
            resultat, sortie = self.executer(communes_et_dvf(), Path(tmp))
            self.assertEqual(resultat.returncode, 0, resultat.stderr[-1200:])
            etat = json.loads((sortie / "_etat.json").read_text(encoding="utf-8"))
            self.assertEqual(len(etat["sources"]), 2, "communes + DVF : deux provenances attendues")
            for source in etat["sources"]:
                self.assertEqual(len(source["sha256"]), 64)
                self.assertTrue(source["licence"], "une source sans licence n'est pas publiable")
            fichier = json.loads((sortie / "d-01.json").read_text(encoding="utf-8"))
            commune = next(c for c in fichier["communes"] if c["c"] == "01010")
            self.assertEqual(commune["pa"], 4200, "médiane de 4 000, 4 200 et 4 400 €/m²")
            self.assertEqual(commune["na"], 3)
            self.assertNotIn("pm", commune, "aucune vente de maison : aucun prix de maison")
            self.assertEqual(fichier["collecte"], etat["collecte"])
            verification = subprocess.run(
                [sys.executable, str(OUTIL), "--verifier", "--sortie", str(sortie)],
                capture_output=True, text=True, check=False,
            )
            self.assertEqual(verification.returncode, 0, verification.stderr[-800:])

    def test_communes_tronquees(self) -> None:
        reponses = communes_et_dvf()
        reponses["/communes"] = (200, json.dumps(communes_factices(200)).encode("utf-8"))
        self.refuser(reponses, attendu="attendues")

    def test_source_absente(self) -> None:
        reponses = communes_et_dvf()
        reponses["/dvf-1.txt.zip"] = (404, b"absent")
        self.refuser(reponses, attendu="source injoignable")

    def test_licence_fermee(self) -> None:
        self.refuser(communes_et_dvf(licence="proprietary"), attendu="licence DVF")

    def test_colonne_absente(self) -> None:
        reponses = communes_et_dvf()
        reponses["/dvf-1.txt.zip"] = (200, dvf_zip([vente("01010", "01", 200_000, 50)], entete=COLONNES[:8]))
        self.refuser(reponses, attendu="absente")

    def test_prix_aberrant(self) -> None:
        # 400 €/m² : au-dessus du plancher par transaction, sous la médiane
        # nationale plausible — c'est exactement le cas d'un fichier mal interprété.
        lignes = [vente("01010", "01", 400 * 50, 50) for _ in range(5)]
        self.refuser(communes_et_dvf(lignes), attendu="hors de")

    def test_prix_en_alsace_moselle(self) -> None:
        """Strasbourg est dans la fixture : sinon le prix n'aurait pas de commune."""
        reponses = communes_et_dvf([vente("67482", "67", 250_000, 50), vente("67482", "67", 260_000, 50)])
        communes = json.loads(reponses["/communes"][1].decode("utf-8"))
        communes.append({
            "nom": "Strasbourg", "code": "67482", "population": 290000,
            "centre": {"type": "Point", "coordinates": [7.75, 48.58]},
            "departement": {"code": "67", "nom": "Bas-Rhin"},
        })
        reponses["/communes"] = (200, json.dumps(communes).encode("utf-8"))
        self.refuser(reponses, attendu="hors du champ de DVF")

    def test_verifier_sans_collecte(self) -> None:
        with tempfile.TemporaryDirectory(prefix="mrsc-couts-") as tmp:
            sortie = Path(tmp) / "vide"
            resultat = subprocess.run(
                [sys.executable, str(OUTIL), "--verifier", "--sortie", str(sortie)],
                capture_output=True, text=True, check=False,
            )
            self.assertNotEqual(resultat.returncode, 0)
            self.assertIn("aucune collecte", resultat.stderr)

    def test_verifier_fichier_altere(self) -> None:
        with tempfile.TemporaryDirectory(prefix="mrsc-couts-") as tmp:
            resultat, sortie = self.executer(communes_et_dvf(), Path(tmp))
            self.assertEqual(resultat.returncode, 0, resultat.stderr[-800:])
            fichier = sortie / "d-01.json"
            donnees = json.loads(fichier.read_text(encoding="utf-8"))
            donnees["communes"] = []
            fichier.write_text(json.dumps(donnees), encoding="utf-8")
            verification = subprocess.run(
                [sys.executable, str(OUTIL), "--verifier", "--sortie", str(sortie)],
                capture_output=True, text=True, check=False,
            )
            self.assertNotEqual(verification.returncode, 0)
            self.assertIn("aucune commune", verification.stderr)

    def test_provenance_obligatoire(self) -> None:
        """Un état sans provenance ne se publie pas, même si les fichiers existent."""
        with tempfile.TemporaryDirectory(prefix="mrsc-couts-") as tmp:
            sortie = Path(tmp) / "donnees"
            sortie.mkdir()
            etat = {
                "version": 1,
                "collecte": "2026-11-13",
                "couverture": {"communes": 0, "communes_avec_prix": 0, "departements": 0},
                "sources": [],
            }
            (sortie / "_etat.json").write_text(json.dumps(etat), encoding="utf-8")
            resultat = subprocess.run(
                [sys.executable, str(OUTIL), "--verifier", "--sortie", str(sortie)],
                capture_output=True, text=True, check=False,
            )
            self.assertNotEqual(resultat.returncode, 0)
            self.assertIn("aucune provenance", resultat.stderr)


class FondEtPage(unittest.TestCase):
    """Les deux fabricants de la page : le fond de carte et l'assemblage.

    Un outil qui écrit un fichier publié sans banc peut se tromper sans qu'on le
    voie : un fond à 95 départements, une licence disparue, une page qui garde
    l'`aria-current` de sa coque d'origine. Ces cas les plantent exprès.
    """

    def copier(self, dossier: Path, fichiers: list[str]) -> None:
        import shutil
        for relatif in fichiers:
            source = RACINE / relatif
            cible = dossier / relatif
            cible.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, cible)

    def test_fond_conforme(self) -> None:
        with tempfile.TemporaryDirectory(prefix="mrsc-fond-") as tmp:
            self.copier(Path(tmp), ["assets/data/vie-chere/fond-departements.json"])
            resultat = subprocess.run(
                [sys.executable, str(RACINE / "outils" / "preparer-fond-de-carte.py"), "--verifier"],
                capture_output=True, text=True, check=False,
                env={**__import__("os").environ, "MRSC_RACINE": tmp},
            )
            self.assertEqual(resultat.returncode, 0, resultat.stderr[-800:])

    def test_fond_ampute(self) -> None:
        with tempfile.TemporaryDirectory(prefix="mrsc-fond-") as tmp:
            self.copier(Path(tmp), ["assets/data/vie-chere/fond-departements.json"])
            chemin = Path(tmp) / "assets/data/vie-chere/fond-departements.json"
            contenu = json.loads(chemin.read_text(encoding="utf-8"))
            contenu["departements"] = contenu["departements"][:-1]
            chemin.write_text(json.dumps(contenu), encoding="utf-8")
            resultat = subprocess.run(
                [sys.executable, str(RACINE / "outils" / "preparer-fond-de-carte.py"), "--verifier"],
                capture_output=True, text=True, check=False,
                env={**__import__("os").environ, "MRSC_RACINE": tmp},
            )
            self.assertNotEqual(resultat.returncode, 0)
            self.assertIn("96", resultat.stderr)

    def test_fond_licence_fermee(self) -> None:
        with tempfile.TemporaryDirectory(prefix="mrsc-fond-") as tmp:
            self.copier(Path(tmp), ["assets/data/vie-chere/fond-departements.json"])
            chemin = Path(tmp) / "assets/data/vie-chere/fond-departements.json"
            contenu = json.loads(chemin.read_text(encoding="utf-8"))
            contenu["provenance"]["licence"] = "tous droits réservés"
            chemin.write_text(json.dumps(contenu), encoding="utf-8")
            resultat = subprocess.run(
                [sys.executable, str(RACINE / "outils" / "preparer-fond-de-carte.py"), "--verifier"],
                capture_output=True, text=True, check=False,
                env={**__import__("os").environ, "MRSC_RACINE": tmp},
            )
            self.assertNotEqual(resultat.returncode, 0)
            self.assertIn("Licence Ouverte", resultat.stderr)

    def test_page_a_jour(self) -> None:
        with tempfile.TemporaryDirectory(prefix="mrsc-page-") as tmp:
            self.copier(Path(tmp), ["localisation.html", "couts-vie-chere/contenu.txt", "couts-vie-chere.html"])
            resultat = subprocess.run(
                [sys.executable, str(RACINE / "outils" / "construire-page-couts.py"), "--verifier"],
                capture_output=True, text=True, check=False,
                env={**__import__("os").environ, "MRSC_RACINE": tmp},
            )
            self.assertEqual(resultat.returncode, 0, resultat.stderr[-800:])

    def test_page_derivee_du_fragment(self) -> None:
        """Une page modifiée à la main ne doit plus être « à jour »."""
        with tempfile.TemporaryDirectory(prefix="mrsc-page-") as tmp:
            self.copier(Path(tmp), ["localisation.html", "couts-vie-chere/contenu.txt", "couts-vie-chere.html"])
            page = Path(tmp) / "couts-vie-chere.html"
            page.write_text(page.read_text(encoding="utf-8").replace("La carte", "La carte (retouchée)"), encoding="utf-8")
            resultat = subprocess.run(
                [sys.executable, str(RACINE / "outils" / "construire-page-couts.py"), "--verifier"],
                capture_output=True, text=True, check=False,
                env={**__import__("os").environ, "MRSC_RACINE": tmp},
            )
            self.assertNotEqual(resultat.returncode, 0)
            self.assertIn("plus le rendu du fragment", resultat.stderr)


if __name__ == "__main__":
    unittest.main(verbosity=2)
