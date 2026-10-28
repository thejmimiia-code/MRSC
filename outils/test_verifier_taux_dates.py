#!/usr/bin/env python3
"""Tests du contrôle « une règle chiffrée porte sa date ».

Le contrôle est préventif : le catalogue du 28 octobre 2026 n'enfreint aucune de
ses règles. Un contrôle qui ne trouve rien doit donc prouver qu'il mord encore,
sinon il ne protège de rien. Ces tests plantent les phrases fautives dans une
copie du catalogue et vérifient qu'elles sont refusées.
"""

from __future__ import annotations

import importlib.util
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
OUTIL = RACINE / "outils" / "verifier-taux-dates.py"
SPEC = importlib.util.spec_from_file_location("verifier_taux_dates", OUTIL)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def fiche(situation: str, source_datee: str | None = "2026-10-28", **autres: str) -> dict:
    """Construit une fiche minimale ; seule la `situation` porte le texte testé."""
    source: dict = {"titre": "Page officielle", "url": "https://exemple.gouv.fr/"}
    if source_datee:
        source["droits_controles_le"] = source_datee
    return {"id": "test-fiche", "situation": situation, "sources": [source], **autres}


class TestRegleChiffree(unittest.TestCase):
    def test_chiffre_seul_n_est_pas_une_regle(self) -> None:
        self.assertFalse(MODULE.regle_chiffree("Une étiquette annonce une réduction de 20 %."))
        self.assertFalse(MODULE.regle_chiffree("Le total est de 40 €."))

    def test_terme_de_regle_seul_n_est_pas_une_regle(self) -> None:
        self.assertFalse(MODULE.regle_chiffree("Les cotisations sociales ne sont pas un impôt."))

    def test_chiffre_et_terme_de_regle_forment_une_regle(self) -> None:
        self.assertTrue(MODULE.regle_chiffree("La CSG est de 9,2 % du salaire brut."))
        self.assertTrue(MODULE.regle_chiffree("Le plafond atteint 4 005 € par mois."))
        self.assertTrue(MODULE.regle_chiffree("Une amende de 450 € par fiche est prévue."))

    def test_annee_et_marqueur_d_exemple_sont_reconnus(self) -> None:
        self.assertTrue(MODULE.ANNEE.search("En 2026, la CSG est de 9,2 %."))
        self.assertTrue(MODULE.MARQUEUR_EXEMPLE.search("Sur notre facture fictive, l'acompte est de 15 %."))


class TestControler(unittest.TestCase):
    def test_taux_sans_annee_refuse(self) -> None:
        defauts, _ = MODULE.controler([fiche("La CSG est de 9,2 % du salaire brut.")])
        self.assertEqual(len(defauts), 1)
        self.assertIn("sans son année", defauts[0])

    def test_montant_legal_sans_annee_refuse(self) -> None:
        defauts, _ = MODULE.controler([fiche("Le plafond est fixé à 4 005 € par mois.")])
        self.assertEqual(len(defauts), 1)

    def test_taux_date_accepte(self) -> None:
        defauts, compteurs = MODULE.controler(
            [fiche("En 2026, la CSG est de 9,2 % du salaire brut.")]
        )
        self.assertEqual(defauts, [])
        self.assertEqual(compteurs["regles_datées"], 1)

    def test_exemple_invente_accepte(self) -> None:
        defauts, _ = MODULE.controler(
            [fiche("Dans l'exemple fictif de cette fiche, le taux retenu est de 4 %.")]
        )
        self.assertEqual(defauts, [])

    def test_exemple_de_mathematiques_accepte(self) -> None:
        defauts, _ = MODULE.controler(
            [fiche("Sur une grille de cent cases, 20 % correspondraient à vingt cases.")]
        )
        self.assertEqual(defauts, [])

    def test_regle_datee_sans_source_datee_refusee(self) -> None:
        defauts, _ = MODULE.controler(
            [fiche("Depuis 2023, le plafond est de 4 005 € par mois.", source_datee=None)]
        )
        self.assertEqual(len(defauts), 1)
        self.assertIn("droits_controles_le", defauts[0])

    def test_champs_de_liste_sont_lus(self) -> None:
        fiche_liste = fiche("Un exemple sans chiffre.")
        fiche_liste["correction"] = ["La cotisation représente 9,2 % du brut."]
        defauts, _ = MODULE.controler([fiche_liste])
        self.assertEqual(len(defauts), 1)
        self.assertIn("correction[0]", defauts[0])

    def test_phrase_longue_est_tronquee_dans_le_message(self) -> None:
        longue = "La cotisation " + "est décrite longuement " * 20 + "et vaut 9,2 %."
        defauts, _ = MODULE.controler([fiche(longue)])
        self.assertEqual(len(defauts), 1)
        self.assertIn("…", defauts[0])
        self.assertLess(len(defauts[0]), 260)


class TestCatalogueReel(unittest.TestCase):
    def test_catalogue_actuel_ne_porte_aucune_regle_non_datee(self) -> None:
        defauts, _ = MODULE.controler(MODULE.charger())
        self.assertEqual(defauts, [], "une fiche du catalogue porte une règle chiffrée sans date")

    def test_copie_mutee_est_refusee_par_la_ligne_de_commande(self) -> None:
        """La sortie en erreur est vérifiée par sous-processus, pas seulement en mémoire."""
        catalogue = MODULE.charger()
        cible = next(f for f in catalogue if f.get("id") == "econ-lire-facture")
        cible["situation"] = "La cotisation salariale retenue atteint 9,2 % du brut."
        texte = tomllib_dumps({"fiche": catalogue})
        with tempfile.TemporaryDirectory() as dossier:
            chemin = Path(dossier) / "catalogue.toml"
            chemin.write_text(texte, encoding="utf-8")
            resultat = subprocess.run(
                [sys.executable, str(OUTIL), "--catalogue", str(chemin)],
                capture_output=True,
                text=True,
                check=False,
            )
        self.assertEqual(resultat.returncode, 1, resultat.stdout + resultat.stderr)
        self.assertIn("sans son année", resultat.stderr)


def tomllib_dumps(donnees: dict) -> str:
    """Sérialise le strict nécessaire en TOML : ce fichier n'a pas besoin de plus."""
    import json

    def serialiser(contenu: object) -> str:
        if isinstance(contenu, bool):
            return "true" if contenu else "false"
        if isinstance(contenu, (int, float)):
            return repr(contenu)
        if isinstance(contenu, str):
            return json.dumps(contenu, ensure_ascii=False)
        if isinstance(contenu, list):
            return "[" + ", ".join(serialiser(element) for element in contenu) + "]"
        if isinstance(contenu, dict):
            return "{ " + ", ".join(f"{cle} = {serialiser(item)}" for cle, item in contenu.items()) + " }"
        raise TypeError(f"type non géré : {type(contenu)!r}")

    lignes = []
    for fiche_ in donnees["fiche"]:
        lignes.append("[[fiche]]")
        for cle, contenu in fiche_.items():
            lignes.append(f"{cle} = {serialiser(contenu)}")
        lignes.append("")
    return "\n".join(lignes)


if __name__ == "__main__":
    unittest.main()
