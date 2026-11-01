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

import json
import re
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
    resume: bool = False,
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
        if resume:
            arguments.append("--resume")
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
            prediction([{"largeur": 761, "echelle": 1.0, "attendu": 2, "conteneur": 713.0}]),
            rapport([mesure(761, 1, largeur_element=640.0)]),
        )
        self.assertEqual(resultat.returncode, 0, resultat.stdout + resultat.stderr)
        self.assertIn("élément 640 px", resultat.stdout)
        self.assertIn("(présumé 713 px)", resultat.stdout)

    def test_le_resume_tient_sur_une_ligne_par_grille(self) -> None:
        """Une annotation de CI ne garde que quelques lignes, et doit se lire seule.

        Le premier relevé publié le 1er novembre 2026 ne nommait aucune grille
        dans ses annotations : le nom restait dans un titre de groupe, en amont
        du filtre. Une ligne de résumé doit donc porter le sélecteur, la page, la
        première divergence et la largeur de l'élément mesuré.
        """
        resultat = executer(
            prediction(
                [
                    {"largeur": 760, "echelle": 1.0, "attendu": 1},
                    {"largeur": 761, "echelle": 1.0, "attendu": 2},
                ]
            ),
            rapport([mesure(760, 1), mesure(761, 1, largeur_element=712.0)]),
            resume=True,
        )
        self.assertEqual(resultat.returncode, 0, resultat.stdout + resultat.stderr)
        lignes = [
            ligne
            for ligne in resultat.stdout.splitlines()
            if ligne.startswith("RESUME ") and not ligne.startswith("RESUME TOTAL")
        ]
        self.assertEqual(len(lignes), 1, resultat.stdout)
        self.assertIn(".hero-grid", lignes[0])
        self.assertIn("index.html", lignes[0])
        self.assertIn("première à 761 px", lignes[0])
        self.assertIn("annoncé 2, vu 1", lignes[0])
        self.assertIn("élément 712 px", lignes[0])
        # Le total, lui, doit égaler celui de la synthèse : deux modes qui
        # compteraient différemment feraient croire à une mesure incomplète.
        total = [ligne for ligne in resultat.stdout.splitlines() if ligne.startswith("RESUME TOTAL")]
        self.assertEqual(len(total), 1, resultat.stdout)
        self.assertIn("1 grille(s), 1 divergence(s) dont 0 au seuil, sur 2 point(s)", total[0])

    def test_une_divergence_au_seuil_est_comptee_pas_refusee(self) -> None:
        """Une prédiction à 0,28 px de la bascule n'est pas une erreur de colonne.

        Le 1er novembre 2026, `.hero-grid` prédisait une colonne à 743 px et le
        navigateur en comptait deux : 0,28 px d'écart, la largeur d'une barre de
        défilement. Le contrôle refuse les divergences qui changent réellement le
        dessin, et **compte** celles qui tombent à moins d'un pixel du seuil —
        sans quoi on élargirait les bases jusqu'à ce que le hasard soit d'accord.
        """
        point = {"largeur": 743, "echelle": 1.0, "attendu": 1, "conteneur": 711.0, "marge": 0.28}
        resultat = executer(prediction([point]), rapport([mesure(743, 2)]), controler=True)
        self.assertEqual(resultat.returncode, 0, resultat.stdout + resultat.stderr)
        self.assertIn("1 divergent(s) dont 1 au seuil", resultat.stdout)
        self.assertIn("Accord hors seuil", resultat.stdout)
        self.assertIn("à 0.28 px du seuil", resultat.stdout)
        self.assertNotIn("Refusé", resultat.stderr)

    def test_une_divergence_hors_du_seuil_est_refusee_et_nommee(self) -> None:
        point = {"largeur": 743, "echelle": 1.0, "attendu": 1, "conteneur": 711.0, "marge": 42.5}
        resultat = executer(prediction([point]), rapport([mesure(743, 2)]), controler=True)
        self.assertEqual(resultat.returncode, 1, resultat.stdout)
        self.assertIn("Refusé", resultat.stderr)
        self.assertIn("hors du seuil", resultat.stderr)
        self.assertIn(".hero-grid", resultat.stderr)

    def test_le_total_du_resume_separe_les_seuils(self) -> None:
        points = [
            {"largeur": 743, "echelle": 1.0, "attendu": 1, "conteneur": 711.0, "marge": 0.28},
            {"largeur": 900, "echelle": 1.0, "attendu": 2, "conteneur": 852.0, "marge": 30.0},
        ]
        resultat = executer(prediction(points), rapport([mesure(743, 2), mesure(900, 1)]), resume=True)
        self.assertEqual(resultat.returncode, 0, resultat.stdout + resultat.stderr)
        self.assertIn("2 divergence(s) dont 1 au seuil", resultat.stdout)

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

    def test_le_conteneur_vient_de_la_prediction(self) -> None:
        """Le rapporteur ne recalcule aucune largeur : il lit celle du modèle.

        Le 1er novembre 2026, le rapporteur présumait lui aussi 48 px de gouttière,
        et aurait donc validé une prédiction fausse en la comparant à sa propre
        erreur. La largeur présumée est désormais écrite point par point dans la
        prédiction ; ce banc vérifie qu'elle est bien celle qui s'affiche, et
        qu'une prédiction sans conteneur est dite « non déclarée » au lieu d'être
        comblée par une valeur maison.
        """
        points = [{"largeur": 761, "echelle": 1.0, "attendu": 2, "conteneur": 713.0}]
        resultat = executer(
            prediction(points), rapport([mesure(761, 1, largeur_element=713.0)])
        )
        self.assertEqual(resultat.returncode, 0, resultat.stdout + resultat.stderr)
        self.assertIn("(présumé 713 px)", resultat.stdout)

        sans = [{"largeur": 761, "echelle": 1.0, "attendu": 2}]
        resultat = executer(prediction(sans), rapport([mesure(761, 1, largeur_element=713.0)]))
        self.assertEqual(resultat.returncode, 0, resultat.stdout + resultat.stderr)
        self.assertIn("conteneur non déclaré", resultat.stdout)

    def test_le_rapporteur_n_importe_pas_le_modele(self) -> None:
        """Il ne doit pas dépendre du module qu'il contrôle.

        Un rapporteur qui importerait `modele-grilles.py` hériterait de ses
        erreurs : une faute de calcul du modèle deviendrait un accord parfait.
        Le banc le lit donc : le fichier ne doit citer ni `import` du modèle, ni
        constante de largeur de contenu.
        """
        texte = (RACINE / "outils" / OUTIL).read_text(encoding="utf-8")
        code = "\n".join(
            ligne for ligne in texte.splitlines() if not ligne.lstrip().startswith("#")
        )
        self.assertIsNone(
            re.search(r"^\s*(?:import|from)\s+modele", code, flags=re.M),
            "le rapporteur importe le modèle qu'il contrôle",
        )
        self.assertNotIn("spec_from_file_location", code)
        self.assertNotIn("GARNITURE_LATERALE", code)
        self.assertNotIn("CONTENU_DEFAUT", code)


if __name__ == "__main__":
    unittest.main(verbosity=2)
