#!/usr/bin/env python3
"""Rejoue, sur une copie jetable, les deux mutations du contrôle des cadrages.

Le 2 novembre 2026, la garde des mots coupés et celle des cartes superposées ont
été éprouvées **à la main** : une copie jetable, une feuille augmentée de deux
règles fautives, un relevé, puis le refus. C'était vrai et c'était consigné,
mais rien ne le rejouait. Un contrôle dont on n'a vu l'échec qu'une fois, dans
une session dont personne ne peut refaire les gestes, vaut une affirmation.

Ce banc refait donc ces gestes, seul, à chaque exécution :

1. une copie du dépôt (`banc_mutations.copie_jetable`), servie par un
   `http.server` éphémère sur un port libre ;
2. une feuille fautive par cas — un mot rogné par une zone de découpe, deux
   cartes déplacées l'une sur l'autre ;
3. le relevé navigateur livré (`outils/mesurer-cadrages.cjs`), sur deux cadrages
   seulement : le banc doit mordre, pas durer ;
4. `outils/cadrages.py --controler` doit alors **échouer**, en nommant ce qu'il
   a vu.

Et une vérification qui n'est pas une mutation : sur la copie **intacte**, le
même relevé doit passer. Sans elle, un contrôle qui refuserait toujours
paraîtrait infaillible.

La mutation est écrite dans la copie par `banc_mutations.cible`, qui refuse de
rendre un chemin sortant de la copie : le 31 octobre 2026, un banc avait modifié
le vrai `assets/css/site.css` en croyant éprouver une copie.

Ce que ce banc ne dit pas : il prouve que ces deux fautes-là sont vues, pas que
le contrôle voit toutes les façons de perdre un mot ou de superposer deux
cartes. Il ne tourne pas sans navigateur — il sort alors en **code 2** et le
dit, parce qu'un banc navigateur muet passerait pour vert.

Usage :
    MRSC_BROWSER_NODE_MODULES=/chemin/node_modules python3 outils/test_mutations_cadrages.py
"""

from __future__ import annotations

import importlib.util
import json
import os
import shutil
import socket
import subprocess
import sys
import tempfile
import threading
import unittest
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RACINE / "outils"))

import banc_mutations  # noqa: E402

FEUILLE = "assets/css/site.css"

#: Deux cadrages suffisent : c'est la faute qu'on éprouve, pas la couverture.
PAGE, CRAN, LARGEURS = "index.html", 100, (390, 1440)

COUPE_UN_MOT = """
/* Banc de mutation : rogne le texte des cartes d'action. */
.home-action-card { max-height: 40px; overflow: hidden; }
"""

SUPERPOSE_DEUX_CARTES = """
/* Banc de mutation : décale une carte sur deux vers le haut. */
.home-action-grid > *:nth-child(even) { position: relative; top: -70px; }
"""


def module_cadrages():
    """Importe `outils/cadrages.py` sans passer par un paquet."""
    spec = importlib.util.spec_from_file_location("cadrages", RACINE / "outils" / "cadrages.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules["cadrages"] = module
    spec.loader.exec_module(module)
    return module


def plan_reduit(destination: Path) -> None:
    """Écrit un plan de deux cadrages, construit depuis la feuille réelle."""
    cadrages = module_cadrages()
    modele = cadrages.charger_modele()
    feuille = (RACINE / cadrages.FEUILLE).read_text(encoding="utf-8")
    modele.definir_gouttiere(feuille)
    modele.definir_feuille(feuille)
    registre = cadrages.lire_registre(RACINE / cadrages.REGISTRE)
    plan = cadrages.construire_plan(modele, registre, feuille)
    plan["combinaisons"] = [
        combinaison
        for combinaison in plan["combinaisons"]
        if combinaison["page"] == PAGE
        and combinaison["cran"] == CRAN
        and combinaison["largeur"] in LARGEURS
        and combinaison.get("layout") is None
    ]
    if not plan["combinaisons"]:
        raise SystemExit(
            "Banc inutilisable : le plan réduit est vide — aucune combinaison pour "
            f"{PAGE} · {CRAN} % · {LARGEURS}."
        )
    plan["grilles"] = {PAGE: plan["grilles"][PAGE]}
    destination.write_text(json.dumps(plan, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")


def port_libre() -> int:
    with socket.socket() as prise:
        prise.bind(("127.0.0.1", 0))
        return int(prise.getsockname()[1])


class ServeurSilencieux(SimpleHTTPRequestHandler):
    """Sert les fichiers sans commenter chaque requête : le banc dit le reste."""

    def log_message(self, *_arguments) -> None:  # noqa: D102 — silence voulu
        pass


class Serveur:
    """Sert un dossier le temps du banc, puis se tait."""

    def __init__(self, dossier: Path) -> None:
        self.port = port_libre()
        gestionnaire = partial(ServeurSilencieux, directory=str(dossier))
        self.serveur = ThreadingHTTPServer(("127.0.0.1", self.port), gestionnaire)
        self.thread = threading.Thread(target=self.serveur.serve_forever, daemon=True)

    def __enter__(self) -> str:
        self.thread.start()
        return f"http://127.0.0.1:{self.port}/"

    def __exit__(self, *_exception) -> None:
        self.serveur.shutdown()
        self.serveur.server_close()
        self.thread.join(timeout=5)


def mesurer(plan: Path, rapport: Path, base: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            shutil.which("node") or "node",
            str(RACINE / "outils" / "mesurer-cadrages.cjs"),
            str(plan),
            str(rapport),
        ],
        cwd=RACINE,
        capture_output=True,
        text=True,
        check=False,
        env=dict(os.environ, MRSC_TEST_URL=base),
    )


def controler(plan: Path, rapport: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            sys.executable,
            str(RACINE / "outils" / "cadrages.py"),
            "--controler",
            str(plan),
            str(rapport),
        ],
        cwd=RACINE,
        capture_output=True,
        text=True,
        check=False,
    )


def raison_sans_navigateur() -> str:
    """Rend le motif de l'impossibilité, ou la chaîne vide si le banc peut tourner."""
    modules = os.environ.get("MRSC_BROWSER_NODE_MODULES")
    if not modules:
        return "MRSC_BROWSER_NODE_MODULES n'est pas défini"
    if not (Path(modules) / "puppeteer-core").is_dir():
        return f"puppeteer-core est absent de {modules}"
    if not (Path(modules) / "@sparticuz" / "chromium").is_dir():
        return f"@sparticuz/chromium est absent de {modules}"
    if shutil.which("node") is None:
        return "node est introuvable"
    return ""


class TestMutationsCadrages(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temporaire = Path(tempfile.mkdtemp(prefix="mrsc-cadrages-"))
        cls.plan = cls.temporaire / "plan.json"
        plan_reduit(cls.plan)

    @classmethod
    def tearDownClass(cls) -> None:
        shutil.rmtree(cls.temporaire, ignore_errors=True)

    def copie(self, suffixe: str, regle: str = "") -> Path:
        dossier = Path(tempfile.mkdtemp(prefix=f"mrsc-{suffixe}-", dir=self.temporaire))
        banc_mutations.copie_jetable(dossier, RACINE)
        if regle:
            feuille = banc_mutations.cible(dossier, FEUILLE, RACINE)
            feuille.write_text(feuille.read_text(encoding="utf-8") + regle, encoding="utf-8")
        return dossier

    def test_une_copie_intacte_passe(self) -> None:
        """Sans cette vérification, un contrôle qui refuserait tout semblerait infaillible."""
        copie = self.copie("intacte")
        rapport = self.temporaire / "rapport-intacte.json"
        with Serveur(copie) as base:
            resultat = mesurer(self.plan, rapport, base)
            self.assertEqual(resultat.returncode, 0, resultat.stdout + resultat.stderr)
            accepte = controler(self.plan, rapport)
            self.assertEqual(accepte.returncode, 0, accepte.stdout + accepte.stderr)
            self.assertIn("aucun mot coupé", accepte.stdout)
        shutil.rmtree(copie, ignore_errors=True)

    def test_un_mot_coupe_est_refuse(self) -> None:
        copie = self.copie("coupe", COUPE_UN_MOT)
        rapport = self.temporaire / "rapport-coupe.json"
        with Serveur(copie) as base:
            resultat = mesurer(self.plan, rapport, base)
            self.assertEqual(resultat.returncode, 0, resultat.stdout + resultat.stderr)
            refus = controler(self.plan, rapport)
            self.assertEqual(refus.returncode, 1, refus.stdout + refus.stderr)
            self.assertIn("coupe un mot de", refus.stderr)
            self.assertIn("home-action-card", refus.stderr)
        shutil.rmtree(copie, ignore_errors=True)

    def test_une_carte_superposee_est_refusee(self) -> None:
        copie = self.copie("superposee", SUPERPOSE_DEUX_CARTES)
        rapport = self.temporaire / "rapport-superposee.json"
        with Serveur(copie) as base:
            resultat = mesurer(self.plan, rapport, base)
            self.assertEqual(resultat.returncode, 0, resultat.stdout + resultat.stderr)
            refus = controler(self.plan, rapport)
            self.assertEqual(refus.returncode, 1, refus.stdout + refus.stderr)
            self.assertIn("se chevauchent de", refus.stderr)
            self.assertIn(".home-action-grid", refus.stderr)
        shutil.rmtree(copie, ignore_errors=True)


if __name__ == "__main__":
    motif = raison_sans_navigateur()
    if motif:
        print(
            f"Navigateur indisponible ({motif}) : aucune mutation éprouvée, aucun "
            "verdict — code 2, jamais vert.",
            file=sys.stderr,
        )
        raise SystemExit(2)
    unittest.main(verbosity=2)
