#!/usr/bin/env python3
"""Banc d'essai du collecteur de revenus communaux (FiLoSoFi, API Mélodi INSEE).

Éprouve le vrai script `outils/collecter-revenus.py` contre un serveur HTTP
local qui sert un catalogue Mélodi JSON et une archive ZIP/CSV simulée —
sans réseau externe. Vérifie aussi la construction de `couts-vie-chere.html`
avec et sans collecte de revenus.

Usage :
    python3 outils/test_collecte_revenus.py
"""
from __future__ import annotations

import io
import json
import os
import shutil
import subprocess
import sys
import tempfile
import threading
import unittest
import zipfile
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
COLLECTEUR = RACINE / "outils" / "collecter-revenus.py"
CONSTRUCTEUR = RACINE / "outils" / "construire-page-couts.py"


def fabriquer_zip(csv_texte: str, nom_csv: str = "DS_FILOSOFI_CC_2023_data.csv", ajouter_metadata: bool = True) -> bytes:
    tampon = io.BytesIO()
    with zipfile.ZipFile(tampon, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        if ajouter_metadata:
            zf.writestr("DS_FILOSOFI_CC_2023_metadata.csv", "COD_VAR;LIB_VAR\nGEO;Zone\n")
        zf.writestr(nom_csv, csv_texte.encode("utf-8"))
    return tampon.getvalue()


def lignes_communes_nominales(
    nombre: int = 25_050,
    separateur: str = ";",
    prefixe_geo: bool = False,
    virgule_decimale: bool = False,
) -> str:
    entete = separateur.join([
        "GEO",
        "GEO_OBJECT",
        "FILOSOFI_MEASURE",
        "TIME_PERIOD",
        "OBS_VALUE",
        "UNIT_MEASURE",
        "UNIT_MULT",
        "CONF_STATUS",
        "OBS_STATUS",
    ])
    lignes = [entete]

    def fmt(val: str) -> str:
        return val.replace(".", ",") if virgule_decimale else val

    def geo_str(obj: str, code: str) -> str:
        return f"2026-{obj}-{code}" if prefixe_geo else code

    # Référence nationale France métropolitaine
    lignes.append(separateur.join([geo_str("FRANCE", "FM"), "FRANCE", "MED_SL", "2023", fmt("25920.0"), "EUR_YR", "0", "F", "A"]))
    lignes.append(separateur.join([geo_str("FRANCE", "FM"), "FRANCE", "PR_MD60", "2023", fmt("15.9"), "PT", "0", "F", "A"]))

    # Quelques communes témoins (Lyon, Corse, La Réunion, petite commune à PR_MD60 omis, commune intégrée omise)
    temoins = [
        ("69123", "28290.0", "A", "18.0", "A"),
        ("2A004", "25880.0", "A", "18.0", "A"),
        ("97411", "20410.0", "A", "32.4", "A"),
        ("01001", "28270.0", "A", "", "O"),  # taux de pauvreté omis (secret statistique)
        ("15031", "", "O", "", "O"),  # commune intégrée entièrement omise
        ("75101", "40000.0", "A", "12.0", "A"),  # arrondissement (ARM) ignoré au profit de COM
    ]
    for code, med, st_m, pauv, st_p in temoins:
        obj = "ARM" if code == "75101" else "COM"
        lignes.append(separateur.join([geo_str(obj, code), obj, "MED_SL", "2023", fmt(med), "EUR_YR", "0", "F", st_m]))
        lignes.append(separateur.join([geo_str(obj, code), obj, "PR_MD60", "2023", fmt(pauv), "PT", "0", "F", st_p]))

    # Compléter jusqu'à `nombre` communes valides (codes 02000..74999)
    restant = nombre - 4
    n = 0
    for dep in range(2, 95):
        if dep in (15, 20, 69):
            continue
        for num in range(1, 500):
            if n >= restant:
                break
            code = f"{dep:02d}{num:03d}"
            lignes.append(separateur.join([geo_str("COM", code), "COM", "MED_SL", "2023", fmt("23450.0"), "EUR_YR", "0", "F", "A"]))
            n += 1
        if n >= restant:
            break
    return "\n".join(lignes) + "\n"


def catalogue_nominal(access_url: str = "https://api.insee.fr/melodi/file/DS_FILOSOFI_CC/DS_FILOSOFI_CC_2023_CSV_FR") -> dict:
    return {
        "identifier": "DS_FILOSOFI_CC",
        "modified": "2026-08-06T13:34:40",
        "accessRights": [{"lang": "fr", "content": "Libre"}, {"lang": "en", "content": "Free"}],
        "confidentialityStatus": [{"lang": "fr", "content": "Libre"}],
        "publisher": {"id": "INSEE"},
        "product": [
            {
                "id": "FILOSOFI_CC_2023_FR",
                "format": "XLSX",
                "language": "FR",
                "accessURL": "https://api.insee.fr/melodi/file/DS_FILOSOFI_CC/FILOSOFI_CC_2023_FR",
            },
            {
                "id": "DS_FILOSOFI_CC_2023_CSV_FR",
                "format": "CSV",
                "language": "FR",
                "modified": "2026-08-06T13:29:20",
                "accessURL": access_url,
            },
        ],
    }


def lancer_serveur(routes: dict[str, tuple[int, str, bytes]]) -> tuple[ThreadingHTTPServer, str]:
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self) -> None:
            chemin = self.path.split("?", 1)[0]
            if chemin not in routes:
                self.send_response(404)
                self.end_headers()
                return
            statut, ctype, corps = routes[chemin]
            self.send_response(statut)
            self.send_header("Content-Type", ctype)
            self.send_header("Content-Length", str(len(corps)))
            self.end_headers()
            self.wfile.write(corps)

        def log_message(self, *args) -> None:
            return

    serveur = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    threading.Thread(target=serveur.serve_forever, daemon=True).start()
    return serveur, f"http://127.0.0.1:{serveur.server_address[1]}"


class BancCollecteRevenus(unittest.TestCase):
    def executer(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(COLLECTEUR), *args],
            capture_output=True,
            text=True,
            check=False,
        )

    def test_collecte_nominale_et_verification(self) -> None:
        zip_bytes = fabriquer_zip(lignes_communes_nominales(prefixe_geo=True, virgule_decimale=True))
        cat = json.dumps(catalogue_nominal()).encode("utf-8")
        serveur, base = lancer_serveur({
            "/melodi/catalog/DS_FILOSOFI_CC": (200, "application/json", cat),
            "/melodi/file/DS_FILOSOFI_CC/DS_FILOSOFI_CC_2023_CSV_FR": (200, "application/zip", zip_bytes),
        })
        try:
            with tempfile.TemporaryDirectory(prefix="mrsc-rev-") as tmp:
                sortie = Path(tmp) / "revenus"
                res = self.executer("--base", base, "--sortie", str(sortie))
                self.assertEqual(res.returncode, 0, res.stderr)
                etat = json.loads((sortie / "_etat.json").read_text(encoding="utf-8"))
                self.assertEqual(etat["millesime"], "2023")
                self.assertEqual(etat["reference_nationale"]["mediane"], 25920)
                self.assertEqual(etat["reference_nationale"]["taux_pauvrete"], 15.9)
                self.assertGreaterEqual(etat["couverture"]["communes_mediane"], 25_000)

                r69 = json.loads((sortie / "r-69.json").read_text(encoding="utf-8"))
                self.assertEqual(r69["communes"]["69123"], [28290, 18.0])

                r2a = json.loads((sortie / "r-2A.json").read_text(encoding="utf-8"))
                self.assertEqual(r2a["communes"]["2A004"], [25880, 18.0])

                r974 = json.loads((sortie / "r-974.json").read_text(encoding="utf-8"))
                self.assertEqual(r974["communes"]["97411"], [20410, 32.4])

                # Taux de pauvreté omis (OBS_STATUS=O) -> null, jamais 0
                r01 = json.loads((sortie / "r-01.json").read_text(encoding="utf-8"))
                self.assertEqual(r01["communes"]["01001"], [28270, None])

                # Commune intégrée (15031) entièrement omise -> absente
                self.assertFalse((sortie / "r-15.json").exists())

                # Arrondissement (75101) non mélangé aux communes
                self.assertFalse((sortie / "r-75.json").exists())

                verif = self.executer("--verifier", "--sortie", str(sortie))
                self.assertEqual(verif.returncode, 0, verif.stderr)
        finally:
            serveur.shutdown()
            serveur.server_close()

    def test_separateur_virgule_sans_prefixe(self) -> None:
        zip_bytes = fabriquer_zip(lignes_communes_nominales(separateur=",", prefixe_geo=False))
        cat = json.dumps(catalogue_nominal()).encode("utf-8")
        serveur, base = lancer_serveur({
            "/melodi/catalog/DS_FILOSOFI_CC": (200, "application/json", cat),
            "/melodi/file/DS_FILOSOFI_CC/DS_FILOSOFI_CC_2023_CSV_FR": (200, "application/zip", zip_bytes),
        })
        try:
            with tempfile.TemporaryDirectory(prefix="mrsc-rev-") as tmp:
                sortie = Path(tmp) / "revenus"
                res = self.executer("--base", base, "--sortie", str(sortie))
                self.assertEqual(res.returncode, 0, res.stderr)
                r69 = json.loads((sortie / "r-69.json").read_text(encoding="utf-8"))
                self.assertEqual(r69["communes"]["69123"], [28290, 18.0])
        finally:
            serveur.shutdown()
            serveur.server_close()

    def test_refus_licence_fermee_sans_ecraser(self) -> None:
        cat_ferme = catalogue_nominal()
        cat_ferme["accessRights"] = [{"lang": "fr", "content": "Restreint"}]
        serveur, base = lancer_serveur({
            "/melodi/catalog/DS_FILOSOFI_CC": (200, "application/json", json.dumps(cat_ferme).encode("utf-8")),
        })
        try:
            with tempfile.TemporaryDirectory(prefix="mrsc-rev-") as tmp:
                sortie = Path(tmp) / "revenus"
                sortie.mkdir()
                temoin = sortie / "_etat.json"
                temoin.write_text('{"temoin": true}\n', encoding="utf-8")
                res = self.executer("--base", base, "--sortie", str(sortie))
                self.assertNotEqual(res.returncode, 0)
                self.assertIn("droits d'accès", res.stderr)
                self.assertEqual(temoin.read_text(encoding="utf-8"), '{"temoin": true}\n')
        finally:
            serveur.shutdown()
            serveur.server_close()

    def test_refus_catalogue_html(self) -> None:
        serveur, base = lancer_serveur({
            "/melodi/catalog/DS_FILOSOFI_CC": (200, "text/html", b"<html><body>Maintenance</body></html>"),
        })
        try:
            with tempfile.TemporaryDirectory(prefix="mrsc-rev-") as tmp:
                res = self.executer("--base", base, "--sortie", str(Path(tmp) / "revenus"))
                self.assertNotEqual(res.returncode, 0)
                self.assertIn("illisible", res.stderr)
        finally:
            serveur.shutdown()
            serveur.server_close()

    def test_refus_produit_csv_absent(self) -> None:
        cat = catalogue_nominal()
        cat["product"] = [p for p in cat["product"] if p["format"] != "CSV"]
        serveur, base = lancer_serveur({
            "/melodi/catalog/DS_FILOSOFI_CC": (200, "application/json", json.dumps(cat).encode("utf-8")),
        })
        try:
            with tempfile.TemporaryDirectory(prefix="mrsc-rev-") as tmp:
                res = self.executer("--base", base, "--sortie", str(Path(tmp) / "revenus"))
                self.assertNotEqual(res.returncode, 0)
                self.assertIn("CSV", res.stderr)
        finally:
            serveur.shutdown()
            serveur.server_close()

    def test_refus_zip_corrompu(self) -> None:
        serveur, base = lancer_serveur({
            "/melodi/catalog/DS_FILOSOFI_CC": (200, "application/json", json.dumps(catalogue_nominal()).encode("utf-8")),
            "/melodi/file/DS_FILOSOFI_CC/DS_FILOSOFI_CC_2023_CSV_FR": (200, "application/zip", b"pas-un-zip"),
        })
        try:
            with tempfile.TemporaryDirectory(prefix="mrsc-rev-") as tmp:
                res = self.executer("--base", base, "--sortie", str(Path(tmp) / "revenus"))
                self.assertNotEqual(res.returncode, 0)
                self.assertIn("ZIP", res.stderr)
        finally:
            serveur.shutdown()
            serveur.server_close()

    def test_refus_colonne_absente(self) -> None:
        zip_bytes = fabriquer_zip("GEO;OBS_VALUE\n69123;28290\n")
        serveur, base = lancer_serveur({
            "/melodi/catalog/DS_FILOSOFI_CC": (200, "application/json", json.dumps(catalogue_nominal()).encode("utf-8")),
            "/melodi/file/DS_FILOSOFI_CC/DS_FILOSOFI_CC_2023_CSV_FR": (200, "application/zip", zip_bytes),
        })
        try:
            with tempfile.TemporaryDirectory(prefix="mrsc-rev-") as tmp:
                res = self.executer("--base", base, "--sortie", str(Path(tmp) / "revenus"))
                self.assertNotEqual(res.returncode, 0)
                self.assertIn("colonnes attendues absentes", res.stderr)
        finally:
            serveur.shutdown()
            serveur.server_close()

    def test_refus_archive_tronquee(self) -> None:
        zip_bytes = fabriquer_zip(lignes_communes_nominales(nombre=200))
        serveur, base = lancer_serveur({
            "/melodi/catalog/DS_FILOSOFI_CC": (200, "application/json", json.dumps(catalogue_nominal()).encode("utf-8")),
            "/melodi/file/DS_FILOSOFI_CC/DS_FILOSOFI_CC_2023_CSV_FR": (200, "application/zip", zip_bytes),
        })
        try:
            with tempfile.TemporaryDirectory(prefix="mrsc-rev-") as tmp:
                res = self.executer("--base", base, "--sortie", str(Path(tmp) / "revenus"))
                self.assertNotEqual(res.returncode, 0)
                self.assertIn("commune(s)", res.stderr)
        finally:
            serveur.shutdown()
            serveur.server_close()

    def test_refus_mediane_aberrante(self) -> None:
        csv_texte = lignes_communes_nominales().replace("28290.0", "999999.0")
        zip_bytes = fabriquer_zip(csv_texte)
        serveur, base = lancer_serveur({
            "/melodi/catalog/DS_FILOSOFI_CC": (200, "application/json", json.dumps(catalogue_nominal()).encode("utf-8")),
            "/melodi/file/DS_FILOSOFI_CC/DS_FILOSOFI_CC_2023_CSV_FR": (200, "application/zip", zip_bytes),
        })
        try:
            with tempfile.TemporaryDirectory(prefix="mrsc-rev-") as tmp:
                res = self.executer("--base", base, "--sortie", str(Path(tmp) / "revenus"))
                self.assertNotEqual(res.returncode, 0)
                self.assertIn("invraisemblable", res.stderr)
        finally:
            serveur.shutdown()
            serveur.server_close()

    def test_refus_doublon_commune(self) -> None:
        csv_texte = lignes_communes_nominales() + "69123;COM;MED_SL;2023;28300.0;EUR_YR;0;F;A\n"
        zip_bytes = fabriquer_zip(csv_texte)
        serveur, base = lancer_serveur({
            "/melodi/catalog/DS_FILOSOFI_CC": (200, "application/json", json.dumps(catalogue_nominal()).encode("utf-8")),
            "/melodi/file/DS_FILOSOFI_CC/DS_FILOSOFI_CC_2023_CSV_FR": (200, "application/zip", zip_bytes),
        })
        try:
            with tempfile.TemporaryDirectory(prefix="mrsc-rev-") as tmp:
                res = self.executer("--base", base, "--sortie", str(Path(tmp) / "revenus"))
                self.assertNotEqual(res.returncode, 0)
                self.assertIn("double", res.stderr)
        finally:
            serveur.shutdown()
            serveur.server_close()

    def test_refus_source_injoignable(self) -> None:
        serveur, base = lancer_serveur({})
        try:
            with tempfile.TemporaryDirectory(prefix="mrsc-rev-") as tmp:
                res = self.executer("--base", base, "--sortie", str(Path(tmp) / "revenus"))
                self.assertNotEqual(res.returncode, 0)
                self.assertIn("injoignable", res.stderr)
        finally:
            serveur.shutdown()
            serveur.server_close()

    def test_verifier_refuse_absence_et_date_future_et_zero(self) -> None:
        with tempfile.TemporaryDirectory(prefix="mrsc-rev-") as tmp:
            sortie = Path(tmp) / "revenus"
            self.assertNotEqual(self.executer("--verifier", "--sortie", str(sortie)).returncode, 0)
            sortie.mkdir()
            (sortie / "r-69.json").write_text('{"departement":"69","millesime":"2023","communes":{"69123":[0,18.0]}}\n', encoding="utf-8")
            (sortie / "_etat.json").write_text(json.dumps({
                "collecte_le": "2099-01-01",
                "millesime": "2023",
                "reference_nationale": {"mediane": 25920},
                "couverture": {"communes_mediane": 25000},
                "source": {
                    "producteur": "INSEE",
                    "licence": "Licence Ouverte 2.0",
                    "catalogue": "https://api.insee.fr/melodi/catalog/DS_FILOSOFI_CC",
                    "url": "https://api.insee.fr/melodi/file/DS_FILOSOFI_CC/DS_FILOSOFI_CC_2023_CSV_FR",
                    "sha256": "abc",
                    "octets": 100,
                },
                "fichiers": ["r-69.json"],
            }), encoding="utf-8")
            verif = self.executer("--verifier", "--sortie", str(sortie))
            self.assertNotEqual(verif.returncode, 0)
            self.assertIn("futur", verif.stderr)
            self.assertIn("invraisemblable", verif.stderr)

    def test_page_couts_avec_et_sans_revenus(self) -> None:
        with tempfile.TemporaryDirectory(prefix="mrsc-page-") as tmp:
            racine = Path(tmp)
            (racine / "couts-vie-chere").mkdir()
            for rel in ("localisation.html", "couts-vie-chere/contenu.txt"):
                shutil.copy2(RACINE / rel, racine / rel)
            env = {**os.environ, "MRSC_RACINE": tmp}
            r1 = subprocess.run([sys.executable, str(CONSTRUCTEUR)], capture_output=True, text=True, check=False, env=env)
            self.assertEqual(r1.returncode, 0, r1.stderr)
            page1 = (racine / "couts-vie-chere.html").read_text(encoding="utf-8")
            self.assertIn("aucune collecte de revenus", page1)
            self.assertNotIn("revenus:", page1)
            self.assertEqual(
                subprocess.run([sys.executable, str(CONSTRUCTEUR), "--verifier"], capture_output=True, text=True, check=False, env=env).returncode,
                0,
            )

            rev_dir = racine / "assets" / "data" / "vie-chere" / "revenus"
            rev_dir.mkdir(parents=True)
            (rev_dir / "_etat.json").write_text(json.dumps({
                "collecte_le": "2026-11-16",
                "millesime": "2023",
                "reference_nationale": {"mediane": 25920, "taux_pauvrete": 15.9},
                "couverture": {"communes_mediane": 31000, "departements": 97},
            }), encoding="utf-8")
            r2 = subprocess.run([sys.executable, str(CONSTRUCTEUR)], capture_output=True, text=True, check=False, env=env)
            self.assertEqual(r2.returncode, 0, r2.stderr)
            page2 = (racine / "couts-vie-chere.html").read_text(encoding="utf-8")
            self.assertIn("FiLoSoFi 2023", page2)
            self.assertIn("25\u202f920\u00a0€/an", page2)
            self.assertNotIn("revenus:", page2)
            self.assertEqual(
                subprocess.run([sys.executable, str(CONSTRUCTEUR), "--verifier"], capture_output=True, text=True, check=False, env=env).returncode,
                0,
            )


if __name__ == "__main__":
    unittest.main(verbosity=2)
