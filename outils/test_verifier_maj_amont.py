#!/usr/bin/env python3
"""Tests de `outils/verifier-maj-amont.py`, la sentinelle du moteur embarqué.

Cet outil ne vérifie rien dans le dépôt : il compare la révision copiée dans
`simulateur/PROVENANCE.json` à celle de la branche `main` du dépôt amont, et
sort en erreur quand une mise à jour est disponible — c'est le signal que le
workflow `maj-simulateur.yml` transforme en alerte. Sa seule preuve était son
vert (ou son rouge) quotidien.

Le réseau n'est jamais joint ici : `revision_amont` est remplacé dans le module
chargé, et la provenance est lue dans une copie du dépôt où elle est réécrite.
Quatre cas sont éprouvés :

1. amont identique à la copie → code 0 et « à jour » ;
2. amont plus récent → code 1, « Mise à jour disponible » et la commande à lancer ;
3. amont injoignable → l'outil s'arrête sans jamais dire « à jour » ;
4. `--json` → la structure attendue, avec `a_jour` à faux.

Limite écrite : l'appel `git ls-remote` lui-même n'est pas éprouvé — un dépôt
injoignable est simulé, pas réellement injoignable. Ce fichier ne classe donc
pas l'outil en `banc` mais en `faute-en-memoire` : les données sont cassées en
mémoire et dans une copie, la sonde réseau est simulée.

Usage :
    python3 outils/test_verifier_maj_amont.py
"""

from __future__ import annotations

import contextlib
import importlib.util
import io
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RACINE / "outils"))

import banc_mutations  # noqa: E402

OUTIL = "verifier-maj-amont.py"
PROVENANCE = "simulateur/PROVENANCE.json"
COPIE = "99491d872f1fb2716041aeb4733f5921359ec7c6"
AMONT_IDENTIQUE = COPIE
AMONT_PLUS_RECENT = "88079be54448ac15c4d1144a8268efd2f1aeb82f"


def charger_module(racine: Path):
    """Charge l'outil avec `MRSC_RACINE` pointant sur la copie à lire."""
    os.environ["MRSC_RACINE"] = str(racine)
    specification = importlib.util.spec_from_file_location(
        "verifier_maj_amont_banc", RACINE / "outils" / OUTIL
    )
    module = importlib.util.module_from_spec(specification)
    specification.loader.exec_module(module)
    return module


def executer(revision_amont, *arguments: str, muter=None) -> tuple[int, str, str]:
    """Copie du dépôt, provenance éventuellement réécrite, puis `main()` en mémoire.

    Rend (code de sortie, sortie standard, sortie d'erreur). Une sortie de
    `SystemExit` est ramenée à son code pour que les tests restent lisibles.
    """
    with tempfile.TemporaryDirectory(prefix="mrsc-maj-amont-") as dossier:
        copie = Path(dossier) / "copie"
        banc_mutations.copie_complete(copie)
        if muter is not None:
            muter(copie)
        module = charger_module(copie)
        module.revision_amont = lambda *_, **__: revision_amont() if callable(
            revision_amont
        ) else revision_amont
        ancien_argv, ancien_cwd = sys.argv, os.getcwd()
        sys.argv = [OUTIL, *arguments]
        sortie, erreur = io.StringIO(), io.StringIO()
        code = 0
        try:
            with contextlib.redirect_stdout(sortie), contextlib.redirect_stderr(erreur):
                code = module.main()
        except SystemExit as arret:
            # `SystemExit("message")` : l'interpréteur écrit le message sur la
            # sortie d'erreur et sort avec le code 1. Le banc fait de même, pour
            # que l'assertion porte sur ce qu'une personne verrait vraiment.
            if isinstance(arret.code, int):
                code = arret.code
            else:
                code = 1
                erreur.write(str(arret.code or ""))
        finally:
            sys.argv, _ = ancien_argv, os.chdir(ancien_cwd)
        return code, sortie.getvalue(), erreur.getvalue()


def provenance_avec(revision: str):  # noqa: ANN202 - fabrique de mutation
    def muter(copie: Path) -> None:
        chemin = copie / PROVENANCE
        contenu = json.loads(chemin.read_text(encoding="utf-8"))
        contenu["revision"] = revision
        chemin.write_text(json.dumps(contenu, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    return muter


class TestVerifierMajAmont(unittest.TestCase):
    def test_moteur_a_jour_sort_zero(self) -> None:
        code, sortie, _ = executer(AMONT_IDENTIQUE, muter=provenance_avec(AMONT_IDENTIQUE))
        self.assertEqual(code, 0, sortie)
        self.assertIn("Le moteur embarqué est à jour", sortie)

    def test_moteur_en_retard_sort_un(self) -> None:
        """Le cas réel du 28 octobre 2026 : la copie a trois semaines de retard."""
        code, sortie, _ = executer(AMONT_PLUS_RECENT)
        self.assertEqual(code, 1, sortie)
        self.assertIn("Mise à jour disponible", sortie)
        self.assertIn("mettre-a-jour-simulateur.py", sortie)

    def test_amont_injoignable_ne_dit_jamais_a_jour(self) -> None:
        """Une panne réseau ne doit pas se lire « rien à signaler »."""

        def injoignable():
            raise SystemExit("Impossible d'interroger le dépôt amont (main)")

        code, sortie, erreur = executer(injoignable)
        self.assertNotEqual(code, 0, sortie)
        self.assertNotIn("à jour", sortie)
        self.assertIn("Impossible d'interroger", erreur)

    def test_json_decrit_l_ecart(self) -> None:
        code, sortie, _ = executer(AMONT_PLUS_RECENT, "--json")
        self.assertEqual(code, 1, sortie)
        etat = json.loads(sortie)
        self.assertIs(etat["a_jour"], False)
        self.assertEqual(etat["revision_amont"], AMONT_PLUS_RECENT)
        self.assertEqual(etat["revision_copiee"], COPIE)
        self.assertTrue(etat["depot_amont"].startswith("https://github.com/"))


if __name__ == "__main__":
    unittest.main(verbosity=2)
