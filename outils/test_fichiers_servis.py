#!/usr/bin/env python3
"""Tests du contrôle des fichiers servis par l'hébergement.

Le contrôle confronte un relevé d'en-têtes enregistré aux fichiers du dépôt. Ces
tests vérifient qu'il mord : binaire dont la taille a changé, texte annoncé non
compressé, cible de la sonde oubliée, relevé daté du futur. Et qu'il ne crie pas
pour un écart normal : un texte compressé plus petit que sa version locale.
"""

from __future__ import annotations

import copy
import importlib.util
import tempfile
import tomllib
import unittest
from datetime import date
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent


def charger_module():
    specification = importlib.util.spec_from_file_location("fichiers_servis", RACINE / "outils" / "verifier-fichiers-servis.py")
    module = importlib.util.module_from_spec(specification)
    specification.loader.exec_module(module)
    return module


MODULE = charger_module()
AUJOURDHUI = date(2026, 10, 20)


def base() -> dict:
    return {
        "meta": {
            "version": 1,
            "mesure_le": date(2026, 10, 20),
            "base_url": "https://exemple.test/",
            "rapport": "https://exemple.test/issues/1",
            "outil": "outils/verifier-publication.py",
            "regle": "un binaire servi fait la taille du dépôt",
        },
        "fichier": [
            {
                "chemin": "outils/verifier-fichiers-servis.py",
                "url": "outils/verifier-fichiers-servis.py",
                "nature": "texte",
                "type_mime": "text/plain",
                "encodage": "gzip",
                "octets_servis": 100,
                "cache": "max-age=600",
            },
            {
                "chemin": "docs/rd/avancees.toml",
                "url": "docs/rd/avancees.toml",
                "nature": "texte",
                "type_mime": "text/plain",
                "encodage": "gzip",
                "octets_servis": 100,
                "cache": "max-age=600",
            },
        ],
    }


def erreurs(registre: dict, cibles: set[str] | None = None) -> list[str]:
    return MODULE.valider(registre, RACINE, cibles, AUJOURDHUI)[0]


class TestReleveReel(unittest.TestCase):
    def test_le_releve_du_depot_concorde(self):
        chemin = MODULE.dernier_releve()
        registre = MODULE.charger(chemin)
        erreurs_reelles, _ = MODULE.valider(registre, RACINE, MODULE.cibles_sonde(), AUJOURDHUI)
        self.assertEqual(erreurs_reelles, [])

    def test_le_releve_couvre_les_cibles_de_la_sonde(self):
        registre = MODULE.charger(MODULE.dernier_releve())
        cibles = MODULE.cibles_sonde()
        self.assertEqual({entree["chemin"] for entree in registre["fichier"]}, cibles)
        self.assertIn("index.html", cibles)


class TestCeQueLeControleRefuse(unittest.TestCase):
    def test_accepte_une_base_valide(self):
        self.assertEqual(erreurs(base()), [])

    def test_refuse_une_cible_de_la_sonde_sans_releve(self):
        resultat = erreurs(base(), {"outils/verifier-fichiers-servis.py", "docs/rd/avancees.toml", "sitemap.xml"})
        self.assertTrue(any("sans relevé" in erreur and "sitemap.xml" in erreur for erreur in resultat), resultat)

    def test_refuse_un_releve_hors_des_cibles(self):
        resultat = erreurs(base(), {"outils/verifier-fichiers-servis.py"})
        self.assertTrue(any("ne contrôle pas" in erreur for erreur in resultat), resultat)

    def test_refuse_un_binaire_dont_la_taille_a_change(self):
        registre = base()
        registre["fichier"][0].update(nature="binaire", encodage="aucun", octets_servis=1)
        resultat = erreurs(registre)
        self.assertTrue(any("le fichier a changé depuis le relevé" in erreur for erreur in resultat), resultat)

    def test_refuse_un_binaire_annonce_compresse(self):
        registre = base()
        registre["fichier"][0].update(nature="binaire", octets_servis=1)
        self.assertTrue(any("encodage" in erreur for erreur in erreurs(registre)))

    def test_refuse_un_texte_annonce_sans_compression(self):
        registre = base()
        registre["fichier"][0]["encodage"] = "aucun"
        self.assertTrue(any("encodage de transfert" in erreur for erreur in erreurs(registre)))

    def test_refuse_un_texte_plus_gros_que_sa_version_locale(self):
        taille = (RACINE / "docs/rd/avancees.toml").stat().st_size
        registre = base()
        registre["fichier"][1]["octets_servis"] = taille
        self.assertTrue(any("compression annoncée n'est pas plausible" in erreur for erreur in erreurs(registre)))

    def test_refuse_un_fichier_absent_du_depot(self):
        registre = base()
        registre["fichier"][0]["chemin"] = "outils/nexiste-pas.py"
        self.assertTrue(any("absent du dépôt" in erreur for erreur in erreurs(registre)))

    def test_refuse_un_chemin_duplique(self):
        registre = base()
        registre["fichier"].append(copy.deepcopy(registre["fichier"][0]))
        self.assertTrue(any("dupliqué" in erreur for erreur in erreurs(registre)))

    def test_refuse_un_champ_manquant(self):
        registre = base()
        del registre["fichier"][0]["octets_servis"]
        self.assertTrue(any("champs manquants" in erreur for erreur in erreurs(registre)))

    def test_refuse_une_date_de_mesure_future(self):
        registre = base()
        registre["meta"]["mesure_le"] = date(2027, 1, 1)
        self.assertTrue(any("futur" in erreur for erreur in erreurs(registre)))

    def test_refuse_un_releve_sans_fichier(self):
        registre = base()
        registre["fichier"] = []
        self.assertTrue(any("aucun fichier relevé" in erreur for erreur in erreurs(registre)))

    def test_refuse_un_outil_inconnu_du_depot(self):
        registre = base()
        registre["meta"]["outil"] = "outils/outil-fantome.py"
        self.assertTrue(any("meta.outil" in erreur for erreur in erreurs(registre)))

    def test_refuse_une_base_url_non_https(self):
        registre = base()
        registre["meta"]["base_url"] = "http://exemple.test/"
        self.assertTrue(any("base_url" in erreur for erreur in erreurs(registre)))


class TestCeQueLeControleSignaleSansBloquer(unittest.TestCase):
    def test_une_compression_marginale_est_un_avertissement(self):
        taille = (RACINE / "docs/rd/avancees.toml").stat().st_size
        registre = base()
        registre["fichier"][1]["octets_servis"] = int(taille * 0.97)
        erreurs_reelles, avertissements = MODULE.valider(registre, RACINE, None, AUJOURDHUI)
        self.assertEqual(erreurs_reelles, [])
        self.assertTrue(any("marginale" in avertissement for avertissement in avertissements), avertissements)

    def test_un_ecart_de_compression_normal_ne_declenche_rien(self):
        _, avertissements = MODULE.valider(base(), RACINE, None, AUJOURDHUI)
        self.assertFalse([avertissement for avertissement in avertissements if "marginale" in avertissement])

    def test_le_poids_theorique_est_annonce_comme_tel(self):
        _, avertissements = MODULE.valider(base(), RACINE, None, AUJOURDHUI)
        self.assertTrue(any("poids théorique" in avertissement for avertissement in avertissements))


class TestLectureDuReleve(unittest.TestCase):
    def test_un_toml_illisible_est_une_erreur_de_lecture(self):
        with tempfile.TemporaryDirectory() as dossier:
            chemin = Path(dossier) / "en-tetes-servis-casse.toml"
            chemin.write_text("[[fichier\n", encoding="utf-8")
            with self.assertRaises(tomllib.TOMLDecodeError):
                MODULE.charger(chemin)

    def test_le_dernier_releve_est_le_plus_recent(self):
        with tempfile.TemporaryDirectory() as dossier:
            for nom in ("en-tetes-servis-2026-01-05.toml", "en-tetes-servis-2026-10-20.toml"):
                (Path(dossier) / nom).write_text("[meta]\n", encoding="utf-8")
            self.assertEqual(MODULE.dernier_releve(Path(dossier)).name, "en-tetes-servis-2026-10-20.toml")


if __name__ == "__main__":
    unittest.main()
