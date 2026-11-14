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
import socket
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


def vente(code: str, departement: str, prix: float, surface: float, type_local: str = "Appartement",
          code_dvf: str | None = None) -> dict:
    """Une vente DVF. `code_dvf` permet d'imiter l'écriture réelle du fichier.

    DVF livre le code commune sans ses zéros de tête : 01001 arrive en `1`. Les
    fixtures d'origine écrivaient `001`, une forme que le fichier réel n'a pas —
    elles ne pouvaient donc pas voir que la collecte perdait les cent premières
    communes de chaque département.
    """
    return {
        "Nature mutation": "Vente",
        "Valeur fonciere": f"{prix:.2f}",
        "Code departement": departement,
        "Code commune": code_dvf if code_dvf is not None else str(int(code[len(departement):])),
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


class ServeurCoupe:
    """Accepte la connexion, puis la ferme sans répondre.

    C'est ce que la collecte DVF a rencontré le 14 novembre 2026 : un
    `RemoteDisconnected`, c'est-à-dire une `OSError`, qui n'était pas une
    `URLError` et échappait donc aux essais. Le collecteur doit en sortir par un
    refus nommé, pas par une traceback.
    """

    def __init__(self) -> None:
        self.actif = True
        self.ecoute = socket.socket()
        self.ecoute.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.ecoute.bind(("127.0.0.1", 0))
        self.ecoute.listen(8)
        self.port = self.ecoute.getsockname()[1]

    def __enter__(self) -> "ServeurCoupe":
        def boucle() -> None:
            while self.actif:
                try:
                    connexion, _ = self.ecoute.accept()
                except OSError:
                    return
                connexion.close()

        threading.Thread(target=boucle, daemon=True).start()
        return self

    def __exit__(self, *args) -> None:
        self.actif = False
        self.ecoute.close()

    @property
    def base(self) -> str:
        return f"http://127.0.0.1:{self.port}"


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

    def test_code_commune_sans_zero_initial(self) -> None:
        """La commune 01001 arrive en `1` dans DVF : elle doit être reconnue."""
        communes = communes_factices()
        communes[0] = {
            "nom": "Première commune", "code": "01001", "population": 500,
            "centre": {"type": "Point", "coordinates": [5.0, 46.0]},
            "departement": {"code": "01", "nom": "Ain"},
        }
        reponses = communes_et_dvf([
            vente("01001", "01", 200_000, 50, code_dvf="1"),
            vente("01001", "01", 220_000, 50, code_dvf="1"),
            vente("01001", "01", 240_000, 50, code_dvf="1"),
        ])
        reponses["/communes"] = (200, json.dumps(communes).encode("utf-8"))
        with tempfile.TemporaryDirectory(prefix="mrsc-couts-") as tmp:
            resultat, sortie = self.executer(reponses, Path(tmp))
            self.assertEqual(resultat.returncode, 0, resultat.stderr[-1200:])
            fichier = json.loads((sortie / "d-01.json").read_text(encoding="utf-8"))
            commune = next(c for c in fichier["communes"] if c["c"] == "01001")
            self.assertEqual(commune["pa"], 4400, "médiane de 4 000, 4 400 et 4 800 €/m²")

    def test_code_commune_padde_tolere(self) -> None:
        """Les deux écritures sont lues : `1` comme `001`."""
        communes = communes_factices()
        communes[0] = {
            "nom": "Première commune", "code": "01001", "population": 500,
            "centre": {"type": "Point", "coordinates": [5.0, 46.0]},
            "departement": {"code": "01", "nom": "Ain"},
        }
        reponses = communes_et_dvf([vente("01001", "01", 200_000, 50, code_dvf="001")])
        reponses["/communes"] = (200, json.dumps(communes).encode("utf-8"))
        with tempfile.TemporaryDirectory(prefix="mrsc-couts-") as tmp:
            resultat, sortie = self.executer(reponses, Path(tmp))
            self.assertEqual(resultat.returncode, 0, resultat.stderr[-1200:])
            fichier = json.loads((sortie / "d-01.json").read_text(encoding="utf-8"))
            self.assertTrue(any(c["c"] == "01001" and c.get("pa") for c in fichier["communes"]))

    def test_arrondissements_regroupes(self) -> None:
        """Paris arrive par arrondissement : ses ventes vont à la commune 75056."""
        communes = communes_factices()
        communes[0] = {
            "nom": "Paris", "code": "75056", "population": 2_103_778,
            "centre": {"type": "Point", "coordinates": [2.347, 48.8589]},
            "departement": {"code": "75", "nom": "Paris"},
        }
        reponses = communes_et_dvf([
            vente("75101", "75", 400_000, 50),
            vente("75101", "75", 450_000, 50),
            vente("75102", "75", 500_000, 50),
        ])
        reponses["/communes"] = (200, json.dumps(communes).encode("utf-8"))
        with tempfile.TemporaryDirectory(prefix="mrsc-couts-") as tmp:
            resultat, sortie = self.executer(reponses, Path(tmp))
            self.assertEqual(resultat.returncode, 0, resultat.stderr[-1200:])
            fichier = json.loads((sortie / "d-75.json").read_text(encoding="utf-8"))
            paris = next(c for c in fichier["communes"] if c["c"] == "75056")
            self.assertEqual(paris["na"], 3, "trois ventes d'arrondissement, une seule commune")
            self.assertEqual(paris["pa"], 9000, "médiane de 8 000, 9 000 et 10 000 €/m²")
            etat = json.loads((sortie / "_etat.json").read_text(encoding="utf-8"))
            self.assertIn("arrondissements_regroupes", etat["regles"], "la règle doit être écrite")

    def test_communes_tronquees(self) -> None:
        reponses = communes_et_dvf()
        reponses["/communes"] = (200, json.dumps(communes_factices(200)).encode("utf-8"))
        self.refuser(reponses, attendu="attendues")

    def test_connexion_coupee(self) -> None:
        """La panne réelle du 14 novembre 2026 : connexion fermée sans réponse."""
        with tempfile.TemporaryDirectory(prefix="mrsc-couts-") as tmp:
            with ServeurCoupe() as serveur:
                sortie = Path(tmp) / "donnees"
                resultat = subprocess.run(
                    [
                        sys.executable, str(OUTIL),
                        "--sortie", str(sortie),
                        "--base-geo", f"{serveur.base}/communes",
                        "--base-data", f"{serveur.base}/dataset",
                    ],
                    capture_output=True, text=True, check=False,
                )
            self.assertNotEqual(resultat.returncode, 0)
            self.assertIn("source injoignable", resultat.stderr)
            self.assertNotIn("Traceback", resultat.stderr)
            self.assertFalse(sortie.exists())

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

    #: La page dépend maintenant de la collecte des loyers : sans le fichier, elle
    #: doit dire que la collecte n'a pas eu lieu ; avec, elle doit porter le
    #: tableau. Les copies du banc emportent donc le fichier quand il existe dans
    #: le dépôt, sinon elles éprouveraient un état que le dépôt n'a pas.
    FICHIERS_PAGE = ["localisation.html", "couts-vie-chere/contenu.txt", "couts-vie-chere.html"]

    def copier_page(self, dossier: Path, loyers: dict | None = None) -> None:
        self.copier(dossier, self.FICHIERS_PAGE)
        chemin = dossier / "assets/data/vie-chere/loyers.json"
        chemin.parent.mkdir(parents=True, exist_ok=True)
        if loyers is not None:
            chemin.write_text(json.dumps(loyers, ensure_ascii=False), encoding="utf-8")
        elif (RACINE / "assets/data/vie-chere/loyers.json").is_file():
            self.copier(dossier, ["assets/data/vie-chere/loyers.json"])

    def construire(self, dossier: Path, verifier: bool = True) -> subprocess.CompletedProcess:
        commande = [sys.executable, str(RACINE / "outils" / "construire-page-couts.py")]
        if verifier:
            commande.append("--verifier")
        return subprocess.run(
            commande, capture_output=True, text=True, check=False,
            env={**__import__("os").environ, "MRSC_RACINE": str(dossier)},
        )

    def loyers_fictifs(self, territoires: list[dict] | None = None) -> dict:
        if territoires is None:
            territoires = [
                {
                    "observatoire": "B6900",
                    "nom": "Agglomération de Lyon",
                    "loyer_median": 13.3,
                    "loyer_mensuel_median": 700,
                    "surface_moyenne": 60,
                    "logements": 37_900,
                    "observations": 4_120,
                    "methode_production": "Estimation directe",
                },
                {
                    "observatoire": "B2B00",
                    "nom": "Agglomération de Bastia",
                    "loyer_median": 9.1,
                    "loyer_mensuel_median": 540,
                    "surface_moyenne": 55,
                    "logements": 2_100,
                    "observations": 610,
                    "methode_production": "Estimation directe",
                },
            ]
        return {
            "collecte_le": "2026-11-15",
            "annee": 2025,
            "source": {
                "producteur": "Réseau des observatoires locaux des loyers (OLL), animé par l’ANIL",
                "licence": "Licence Ouverte 2.0 (lov2)",
                "jeu": "https://www.data.gouv.fr/api/1/datasets/resultats-nationaux-des-observatoires-locaux-des-loyers/",
                "fiche": "https://www.data.gouv.fr/datasets/resultats-nationaux-des-observatoires-locaux-des-loyers",
                "ressource_id": "aaaaaaaa-0000-0000-0000-000000000025",
                "ressource_titre": "Loyers 2025 dans les agglomérations observées par les observatoires du réseau",
                "date_ressource": "2026-10-28T15:13:11+00:00",
            },
            "territoires": territoires,
        }

    def test_page_sans_collecte_de_loyers(self) -> None:
        """Sans fichier de loyers, la page doit l'avouer, et pas se taire."""
        with tempfile.TemporaryDirectory(prefix="mrsc-page-") as tmp:
            self.copier(Path(tmp), self.FICHIERS_PAGE)
            resultat = self.construire(Path(tmp), verifier=False)
            self.assertEqual(resultat.returncode, 0, resultat.stderr[-800:])
            page = (Path(tmp) / "couts-vie-chere.html").read_text(encoding="utf-8")
            self.assertIn("Aucune collecte de loyers", page)
            self.assertIn("la collecte des loyers par agglomération n’a pas encore eu lieu", page)
            self.assertNotIn("loyers:", page)
            self.assertEqual(self.construire(Path(tmp)).returncode, 0)

    def test_page_avec_loyers_collectes(self) -> None:
        """Avec un fichier, la page porte le tableau, à la française et sans marque."""
        with tempfile.TemporaryDirectory(prefix="mrsc-page-") as tmp:
            self.copier_page(Path(tmp), loyers=self.loyers_fictifs())
            resultat = self.construire(Path(tmp), verifier=False)
            self.assertEqual(resultat.returncode, 0, resultat.stderr[-800:])
            page = (Path(tmp) / "couts-vie-chere.html").read_text(encoding="utf-8")
            self.assertIn("Loyer médian mensuel", page)
            self.assertIn("13,30&nbsp;€/m²", page)
            self.assertIn("Affiché : loyer médian", page)
            self.assertNotIn("Aucune collecte de loyers", page)
            self.assertNotIn("loyers:", page)
            self.assertIn("B2B00", page)
            self.assertEqual(self.construire(Path(tmp)).returncode, 0)

    def test_page_refuse_des_loyers_sans_territoire(self) -> None:
        """Une collecte vide ne doit pas produire une section muette."""
        with tempfile.TemporaryDirectory(prefix="mrsc-page-") as tmp:
            self.copier_page(Path(tmp), loyers=self.loyers_fictifs(territoires=[]))
            resultat = self.construire(Path(tmp), verifier=False)
            self.assertNotEqual(resultat.returncode, 0)
            self.assertIn("aucun territoire", resultat.stderr)

    def test_page_signale_une_collecte_non_regenerée(self) -> None:
        """La donnée arrive, la page ne bouge pas : c'est un écart, pas un détail."""
        with tempfile.TemporaryDirectory(prefix="mrsc-page-") as tmp:
            self.copier(Path(tmp), self.FICHIERS_PAGE)
            self.assertEqual(self.construire(Path(tmp), verifier=False).returncode, 0)
            chemin = Path(tmp) / "assets/data/vie-chere/loyers.json"
            chemin.parent.mkdir(parents=True, exist_ok=True)
            chemin.write_text(json.dumps(self.loyers_fictifs(), ensure_ascii=False), encoding="utf-8")
            resultat = self.construire(Path(tmp))
            self.assertNotEqual(resultat.returncode, 0)
            # La comparaison octet à octet tombe la première ; le contrôle de
            # présence du tableau la doublerait si la page était reconstruite
            # depuis un autre fragment.
            self.assertIn("plus le rendu du fragment", resultat.stderr)

    def test_page_a_jour(self) -> None:
        with tempfile.TemporaryDirectory(prefix="mrsc-page-") as tmp:
            self.copier_page(Path(tmp))
            resultat = subprocess.run(
                [sys.executable, str(RACINE / "outils" / "construire-page-couts.py"), "--verifier"],
                capture_output=True, text=True, check=False,
                env={**__import__("os").environ, "MRSC_RACINE": tmp},
            )
            self.assertEqual(resultat.returncode, 0, resultat.stderr[-800:])

    def test_page_derivee_du_fragment(self) -> None:
        """Une page modifiée à la main ne doit plus être « à jour »."""
        with tempfile.TemporaryDirectory(prefix="mrsc-page-") as tmp:
            self.copier_page(Path(tmp))
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
