#!/usr/bin/env python3
"""Éprouve la lecture d'un dégradé : la découpe des couches et la zone du texte.

Le 3 novembre 2026, le relevé a lu les dégradés pendant un lot entier avec une
découpe fausse : la virgule entre deux **arrêts** d'un même dégradé ressemble
exactement à celle entre deux **couches**, et le découpage les confondait. Un
dégradé clair→sombre devenait donc deux calques unis — et le pire contraste
d'une plage était calculé sur des aplats qui n'existent nulle part. Les chiffres
du lot étaient justes dans leur forme et faux dans leur objet.

Ce banc rejoue deux choses, sur une page de banc écrite pour lui, dans une copie
jetable du dépôt :

1. **la découpe** : un dégradé à deux arrêts doit ressortir comme **une** couche
   à deux arrêts, jamais comme deux couches à un arrêt ;
2. **la zone** : un texte étroit posé à gauche d'un dégradé horizontal doit
   garder une portion de plage proche de 0, celui posé à droite une portion
   proche de 1 — et les deux rapports doivent en découler. Sans cela, le relevé
   juge un texte contre une couleur qui n'est pas sous lui.

Ce que ce banc ne dit pas : il éprouve des dégradés `linear-gradient` à arrêts
en pourcentage, sur une page de banc. Il ne prouve rien des dégradés radiaux du
site (la zone radiale y est calculée, mais aucun cas ne la vérifie ici) ni des
arrêts en pixels. Il ne tourne pas sans navigateur — il sort alors en **code 2**
et le dit, parce qu'un banc navigateur muet passerait pour vert.

Usage :
    MRSC_BROWSER_NODE_MODULES=/chemin/node_modules python3 outils/test_contraste-degrade.py
"""

from __future__ import annotations

import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RACINE / "outils"))

import banc_mutations  # noqa: E402
from test_mutations_cadrages import (  # noqa: E402
    Serveur,
    mesurer,
    module_cadrages,
    raison_sans_navigateur,
)

PAGE = "banc-degrade.html"

#: Un dégradé horizontal du blanc au noir, deux textes étroits : l'un collé au
#: bord clair, l'autre au bord sombre. La couleur du texte ne change pas — seul
#: son emplacement change, et c'est bien cela que la mesure doit voir.
PAGE_DE_BANC = """<!doctype html>
<html lang="fr">
<head>
<meta charset="utf-8">
<title>Banc des dégradés</title>
<link rel="stylesheet" href="assets/css/site.css">
<style>
  .banc-bande { width: 1000px; height: 200px; margin: 0;
    background-image: linear-gradient(90deg, rgb(255, 255, 255), rgb(0, 0, 0)); }
  .banc-bande p { margin: 0; width: 100px; color: rgb(17, 17, 17); font-size: 16px; }
  /* Spécificité supérieure à `.banc-bande p`, qui remet les marges à zéro. */
  div.banc-bande p.banc-a-droite { margin-left: 900px; }
</style>
</head>
<body>
  <div class="banc-bande"><p id="gauche">Texte à gauche</p></div>
  <div class="banc-bande"><p id="droite" class="banc-a-droite">Texte à droite</p></div>
</body>
</html>
"""


def plan_de_banc(destination: Path) -> Path:
    """Un plan d'un seul cadrage : la page de banc, en 1 440 px."""
    plan = {
        "tolerance_px": 0.5,
        "grilles": {},
        "combinaisons": [
            {
                "page": PAGE,
                "layout": None,
                "cran": 100,
                "largeur": 1440,
                "attendu": {},
            }
        ],
    }
    destination.write_text(json.dumps(plan, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    return destination


class TestContrasteDegrade(unittest.TestCase):
    """Deux affirmations, chacune avec son échec possible."""

    @classmethod
    def setUpClass(cls) -> None:
        motif = raison_sans_navigateur()
        if motif:
            raise unittest.SkipTest(motif)
        cls.temporaire = Path(tempfile.mkdtemp(prefix="mrsc-degrade-"))
        cls.copie = cls.temporaire / "copie"
        cls.copie.mkdir()
        banc_mutations.copie_jetable(cls.copie, RACINE)
        (cls.copie / PAGE).write_text(PAGE_DE_BANC, encoding="utf-8")
        cls.plan = plan_de_banc(cls.temporaire / "plan.json")
        cls.rapport = cls.temporaire / "rapport.json"
        with Serveur(cls.copie) as base:
            cls.resultat = mesurer(cls.plan, cls.rapport, base)
        cls.cadrages = module_cadrages()
        cls.donnees = json.loads(cls.rapport.read_text(encoding="utf-8")) if cls.rapport.is_file() else {}

    @classmethod
    def tearDownClass(cls) -> None:
        if hasattr(cls, "temporaire"):
            shutil.rmtree(cls.temporaire, ignore_errors=True)

    def candidats(self) -> list[dict]:
        mesures = self.donnees.get("mesures") or []
        self.assertTrue(mesures, "le relevé n'a rendu aucune mesure : " + (self.resultat.stdout + self.resultat.stderr)[-800:])
        contraste = mesures[0].get("contraste") or {}
        candidats = contraste.get("candidats_degrade") or []
        self.assertTrue(candidats, "aucun texte sur dégradé relevé sur la page de banc")
        return candidats

    def test_un_degrade_a_deux_arrets_reste_une_couche(self) -> None:
        """La découpe d'hier séparait les arrêts d'un même dégradé en calques."""
        for candidat in self.candidats():
            couches = candidat.get("couches") or []
            self.assertEqual(
                len(couches),
                1,
                f"un dégradé à deux arrêts doit être une couche, "
                f"{len(couches)} relevée(s) pour {candidat.get('tag')}",
            )
            self.assertEqual(
                len(couches[0].get("arrets") or []),
                2,
                "les deux arrêts du dégradé doivent être conservés dans la même couche",
            )

    def test_la_zone_suit_l_emplacement_du_texte(self) -> None:
        """À gauche le texte est sur le blanc, à droite sur le noir : la mesure le dit."""
        par_classe = {}
        for candidat in self.candidats():
            classes = str(candidat.get("classe") or "").split()
            cle = "droite" if "banc-a-droite" in classes else "gauche"
            par_classe[cle] = candidat
        self.assertEqual(set(par_classe), {"gauche", "droite"}, "les deux textes de banc doivent être relevés")
        gauche = par_classe["gauche"]["couches"][0]["zone"]
        droite = par_classe["droite"]["couches"][0]["zone"]
        self.assertLess(gauche[1], 0.2, f"le texte de gauche occupe le début du dégradé, zone relevée {gauche}")
        self.assertGreater(droite[0], 0.8, f"le texte de droite occupe la fin du dégradé, zone relevée {droite}")
        self.assertLess(droite[0], 1.0, "la zone du texte de droite ne doit pas être réduite à un point")
        pire_gauche, _ = self.cadrages.pire_contraste_degrade(par_classe["gauche"])
        pire_droite, _ = self.cadrages.pire_contraste_degrade(par_classe["droite"])
        self.assertGreater(pire_gauche, 10.0, "sur le blanc, un texte presque noir garde un grand contraste")
        self.assertLess(pire_droite, 1.5, "sur le noir, le même texte n'a presque plus de contraste")
        self.assertLess(pire_droite, self.cadrages.seuil_de_contraste(16, False))


def raison_d_un_banc_muet() -> int:
    """Sans navigateur, ce banc sort en code 2 et le dit — jamais en vert."""
    motif = raison_sans_navigateur()
    if motif:
        print(f"Banc de contraste des dégradés : non exécuté — {motif}.", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    if raison_d_un_banc_muet():
        raise SystemExit(2)
    programme = unittest.main(verbosity=2, exit=False)
    raise SystemExit(0 if programme.result.wasSuccessful() else 1)
