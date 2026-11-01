#!/usr/bin/env python3
"""Banc de `rapporter-mesure-grilles.py`, sans navigateur.

Le rapporteur tourne dans le job `graphismes`, à côté d'une mesure qui coûte
des minutes et d'un Chromium que l'atelier n'a pas. Il fallait donc pouvoir
l'éprouver ici : ce banc fabrique une prédiction et un relevé, et regarde ce que
le rapporteur en dit.

Huit cas, tous hors ligne :

1. accord parfait → code 0, tout confirmé ;
2. divergence en mode relevé → code 0 (il publie), mais la divergence est nommée
   avec sa largeur, son échelle et les deux valeurs ;
3. la même divergence en mode `--controler` → code 1 et « Refusé » ;
4. un point annoncé que le navigateur n'a pas mesuré → code 1 même sans
   divergence : non mesuré n'est pas conforme ;
5. la largeur de l'élément mesuré est imprimée à côté de celle que le modèle
   présume — sans quoi on accuserait la feuille d'un remplissage de panneau ;
6. un rapport sans navigateur → code 2 : une mesure sans navigateur ne prouve
   rien ;
7. un rapport absent et un rapport illisible → code 2, sans trace d'exception ;
8. le rapporteur ne recopie pas les constantes du modèle : `conteneur` est
   comparé à `modele-grilles.py`, et le désaccord échoue ici.

Usage :
    python3 outils/test_rapporter_mesure_grilles.py
"""

from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RACINE / "outils"))

import banc_mutations  # noqa: E402

OUTIL = "rapporter-mesure-grilles.py"
MODELE = "modele-grilles.py"


def prediction(points: list[dict]) -> dict:
    return {
        "feuille": "assets/css/site.css",
        "avertissement": "banc",
        "grilles": [
            {
                "selecteur": ".hero-grid",
                "page": "index.html",
                "forme": "flex",
                "pts": len(points),
                "points": points,
            }
        ],
        "non_mesurables": [],
    }


def rapport(mesures: list[dict], navigateur: str | None = "HeadlessChrome/153") -> dict:
    return {
        "navigateur": navigateur,
        "base": "http://127.0.0.1:4181/",
        "mesures": mesures,
        "erreurs": [],
    }


def mesure(largeur: int, colonnes: int, echelle: float = 1.0, largeur_element: float = 706.0) -> dict:
    return {
        "selecteur": ".hero-grid",
        "page": "index.html",
        "largeur": largeur,
        "largeur_cliente": largeur,
        "echelle": echelle,
        "trouve": True,
        "display": "flex",
        "colonnes": colonnes,
        "largeur_element": largeur_element,
    }


def executer(
    releve: dict | None = None,
    sortie: dict | None = None,
    *,
    controler: bool = False,
    brut_releve: str | None = None,
    brut_rapport: str | None = None,
    sans_rapport: bool = False,
):
    with tempfile.TemporaryDirectory(prefix="mrsc-mesure-grilles-") as dossier:
        chemin_releve = Path(dossier) / "releve.json"
        chemin_rapport = Path(dossier) / "rapport.json"
        if brut_releve is not None:
            chemin_releve.write_text(brut_releve, encoding="utf-8")
        elif releve is not None:
            chemin_releve.write_text(json.dumps(releve), encoding="utf-8")
        if brut_rapport is not None:
            chemin_rapport.write_text(brut_rapport, encoding="utf-8")
        elif sortie is not None:
            chemin_rapport.write_text(json.dumps(sortie), encoding="utf-8")
        if sans_rapport:
            chemin_rapport.unlink(missing_ok=True)
        arguments = ["--releve", str(chemin_releve), "--rapport", str(chemin_rapport)]
        if controler:
            arguments.append("--controler")
        return banc_mutations.lancer(OUTIL, RACINE, arguments=tuple(arguments))


class TestRapporterMesureGrilles(unittest.TestCase):
    def test_accord_parfait(self) -> None:
        resultat = executer(
            prediction([{"largeur": 760, "echelle": 1.0, "attendu": 1}, {"largeur": 761, "echelle": 1.0, "attendu": 2}]),
            rapport([mesure(760, 1), mesure(761, 2)]),
        )
        self.assertEqual(resultat.returncode, 0, resultat.stdout + resultat.stderr)
        self.assertIn("2 confirmé(s)", resultat.stdout)
        self.assertIn("RELEVÉ", resultat.stdout)

    def test_divergence_publiee_en_mode_releve(self) -> None:
        """Un relevé publie ce qu'il voit, et le nomme assez pour être réparé."""
        resultat = executer(
            prediction([{"largeur": 760, "echelle": 1.0, "attendu": 1}, {"largeur": 761, "echelle": 1.0, "attendu": 2}]),
            rapport([mesure(760, 1), mesure(761, 1)]),
        )
        self.assertEqual(resultat.returncode, 0, resultat.stdout + resultat.stderr)
        self.assertIn("1 divergence(s)", resultat.stdout)
        self.assertIn("à 761 px (texte ×1)", resultat.stdout)
        self.assertIn("le modèle annonce 2 colonne(s), le navigateur en compte 1", resultat.stdout)

    def test_divergence_refusee_en_mode_controle(self) -> None:
        resultat = executer(
            prediction([{"largeur": 761, "echelle": 1.3, "attendu": 2}]),
            rapport([mesure(761, 3, echelle=1.3)]),
            controler=True,
        )
        self.assertEqual(resultat.returncode, 1, resultat.stdout)
        self.assertIn("CONTRÔLE", resultat.stdout)
        self.assertIn("Refusé", resultat.stderr)
        self.assertIn("texte ×1.3", resultat.stdout)

    def test_point_sans_mesure_n_est_pas_conforme(self) -> None:
        resultat = executer(
            prediction([{"largeur": 760, "echelle": 1.0, "attendu": 1}, {"largeur": 1440, "echelle": 1.0, "attendu": 2}]),
            rapport([mesure(760, 1)]),
            controler=True,
        )
        self.assertEqual(resultat.returncode, 1, resultat.stdout)
        self.assertIn("sans mesure", resultat.stdout)
        self.assertIn("non mesuré n'est pas conforme", resultat.stdout)
        self.assertIn("sans mesure", resultat.stderr)

    def test_la_largeur_de_l_element_est_imprimee(self) -> None:
        """La première cause d'un écart est le remplissage du panneau, pas la feuille."""
        resultat = executer(
            prediction([{"largeur": 761, "echelle": 1.0, "attendu": 2}]),
            rapport([mesure(761, 1, largeur_element=640.0)]),
        )
        self.assertEqual(resultat.returncode, 0, resultat.stdout + resultat.stderr)
        self.assertIn("élément 640 px", resultat.stdout)
        self.assertIn("conteneur présumé 713 px", resultat.stdout)

    def test_rapport_sans_navigateur_refuse(self) -> None:
        resultat = executer(
            prediction([{"largeur": 760, "echelle": 1.0, "attendu": 1}]),
            rapport([mesure(760, 1)], navigateur=None),
        )
        self.assertEqual(resultat.returncode, 2, resultat.stdout)
        self.assertIn("aucun navigateur", resultat.stderr)
        self.assertIn("ne prouve rien", resultat.stderr)

    def test_rapport_absent_et_illisible(self) -> None:
        releve = prediction([{"largeur": 760, "echelle": 1.0, "attendu": 1}])
        absent = executer(releve, sans_rapport=True)
        self.assertEqual(absent.returncode, 2, absent.stdout)
        self.assertIn("introuvable", absent.stderr)
        illisible = executer(releve, brut_rapport="{ ceci n'est pas du JSON")
        self.assertEqual(illisible.returncode, 2, illisible.stdout)
        self.assertIn("illisible", illisible.stderr)
        self.assertNotIn("Traceback", illisible.stderr)

    def test_les_constantes_du_modele_sont_les_memes(self) -> None:
        """Le rapporteur ne doit pas juger avec une autre arithmétique que le modèle.

        Il recopie `conteneur` pour ne pas dépendre du module qu'il contrôle ;
        encore faut-il que la copie soit fidèle. Le jour où le modèle changera sa
        largeur de contenu, ce test le dira — plutôt que de laisser le rapporteur
        accuser la feuille d'un désaccord entre deux constantes.
        """
        specification = importlib.util.spec_from_file_location(
            "rapporter_mesure_grilles", RACINE / "outils" / OUTIL
        )
        rapporteur = importlib.util.module_from_spec(specification)
        specification.loader.exec_module(rapporteur)
        modele = importlib.util.spec_from_file_location("modele_grilles", RACINE / "outils" / MODELE)
        module = importlib.util.module_from_spec(modele)
        # `modele-grilles.py` déclare des `dataclass` : leur création relit
        # `sys.modules[cls.__module__]`, qui n'existe pas tant que le module n'y
        # est pas inscrit. Sans cette ligne, le banc échoue sur une
        # `AttributeError` sans rapport avec ce qu'il éprouve.
        sys.modules["modele_grilles"] = module
        modele.loader.exec_module(module)
        self.assertEqual(rapporteur.CONTENU_DEFAUT, module.CONTENU_DEFAUT)
        self.assertEqual(rapporteur.GARNITURE_LATERALE, module.GARNITURE_LATERALE)
        for largeur in (240, 760, 1160, 2560):
            self.assertEqual(rapporteur.conteneur(largeur), module.conteneur(largeur))


if __name__ == "__main__":
    unittest.main(verbosity=2)
