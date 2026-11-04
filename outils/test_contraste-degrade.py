#!/usr/bin/env python3
"""Éprouve la lecture d'un dégradé : la découpe des couches et la zone du texte.

Le 3 novembre 2026, le relevé a lu les dégradés pendant un lot entier avec une
découpe fausse : la virgule entre deux **arrêts** d'un même dégradé ressemble
exactement à celle entre deux **couches**, et le découpage les confondait. Un
dégradé clair→sombre devenait donc deux calques unis — et le pire contraste
d'une plage était calculé sur des aplats qui n'existent nulle part. Les chiffres
du lot étaient justes dans leur forme et faux dans leur objet.

Ce banc rejoue trois choses, sur une page de banc écrite pour lui, dans une
copie jetable du dépôt :

1. **la découpe** : un dégradé à deux arrêts doit ressortir comme **une** couche
   à deux arrêts, jamais comme deux couches à un arrêt ;
2. **la zone linéaire** : un texte étroit posé à gauche d'un dégradé
   horizontal doit garder une portion de plage proche de 0, celui posé à droite
   une portion proche de 1 — et les deux rapports doivent en découler. Sans
   cela, le relevé juge un texte contre une couleur qui n'est pas sous lui ;
3. **la zone radiale** : un halo de 100 px de rayon ne colore que son disque. Un
   texte dans le rayon voit le début de l'interpolation, un texte au-delà ne voit
   que le dernier arrêt — et la zone doit le dire (`[1, 1]`).

Ce que ce banc ne dit pas : il éprouve un `linear-gradient` à arrêts en
pourcentage et un `radial-gradient` **circulaire** à arrêt en pixels, sur une
page de banc. Il ne dit rien des formes `ellipse`, des tailles en mots-clés, des
arrêts radiaux en pourcentage ni des dégradés répétés : ces cas-là retombent sur
la plage entière, et aucun cas ne chiffre ici ce que ce majorant coûte. Il ne tourne pas sans navigateur — il sort alors en **code 2**
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
  /* Halo de 100 px de rayon, centré à gauche : le second texte est loin du
     rayon, donc sur le dernier arrêt — noir — et non sur l'interpolation. */
  .banc-halo { width: 1000px; height: 200px; margin: 0; display: flex; align-items: center;
    background-image: radial-gradient(circle at 0% 50%, rgb(255, 255, 255), rgb(0, 0, 0) 100px); }
  .banc-halo p { margin: 0; width: 40px; color: rgb(17, 17, 17); font-size: 16px; }
  div.banc-halo p.banc-loin { margin-left: 800px; }
  /* Halo **ambigu** : un arrêt en pourcentage, donc aucun rayon en pixels. La
     mesure ne sait pas où passe la limite du disque et retombe sur la plage
     entière. C'est ce majorant que le 4 novembre 2026 on a cessé de taire. */
  .banc-halo-ambigu { width: 1000px; height: 200px; margin: 0; display: flex; align-items: center;
    background-image: radial-gradient(circle at 50% 50%, rgb(255, 255, 255), rgb(0, 0, 0) 60%); }
  .banc-halo-ambigu p { margin: 0; width: 200px; color: rgb(17, 17, 17); font-size: 16px; }
</style>
</head>
<body>
  <div class="banc-bande"><p id="gauche">Texte à gauche</p></div>
  <div class="banc-bande"><p id="droite" class="banc-a-droite">Texte à droite</p></div>
  <div class="banc-halo"><p id="pres">Près</p><p id="loin" class="banc-loin">Loin</p></div>
  <div class="banc-halo-ambigu"><p id="ambigu">Halo ambigu</p></div>
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
            identifiant = str(candidat.get("id") or "")
            if identifiant in {"gauche", "droite"}:
                par_classe[identifiant] = candidat
        self.assertEqual(set(par_classe), {"gauche", "droite"}, "les deux textes de banc doivent être relevés par leur identifiant")
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


    def test_la_zone_radiale_sort_du_rayon(self) -> None:
        """Un halo de 100 px : près du centre il compte, au-delà il n'existe plus.

        Sans cette vérification, la zone radiale pourrait valoir la plage
        entière sans que rien ne le dise — et le héros du site, qui pose quatre
        halos, serait jugé contre des couleurs qu'il ne montre pas sous son
        texte.
        """
        par_identifiant = {}
        for candidat in self.candidats():
            identifiant = str(candidat.get("id") or "")
            if identifiant in {"pres", "loin"}:
                par_identifiant[identifiant] = candidat
        if set(par_identifiant) != {"pres", "loin"}:
            self.fail(
                "le relevé ne nomme pas les deux textes du halo : "
                f"{sorted(par_identifiant)} — le banc ne peut pas conclure"
            )
        pres = par_identifiant["pres"]["couches"][0]
        loin = par_identifiant["loin"]["couches"][0]
        self.assertEqual(pres["type"], "radial", "la couche doit être lue comme radiale")
        self.assertLess(
            pres["zone"][1],
            0.5,
            f"le texte près du centre reste dans la moitié intérieure du halo, zone {pres['zone']}",
        )
        self.assertEqual(loin["zone"], [1, 1], f"au-delà du rayon, le texte ne voit que le dernier arrêt, zone {loin['zone']}")
        pire_pres, _ = self.cadrages.pire_contraste_degrade(par_identifiant["pres"])
        pire_loin, _ = self.cadrages.pire_contraste_degrade(par_identifiant["loin"])
        self.assertGreaterEqual(
            pire_pres,
            self.cadrages.seuil_de_contraste(16, False),
            "dans la moitié intérieure du halo, le texte presque noir garde son contraste",
        )
        self.assertLess(pire_loin, 1.5, "au-delà du rayon, le même texte est sur du noir")

    def test_un_halo_sans_rayon_est_compte_comme_non_situe(self) -> None:
        """Le majorant cesse d'être tu : la couche dit qu'elle n'est pas située.

        Un `radial-gradient` dont l'arrêt est en pourcentage n'a pas de rayon en
        pixels : la zone ne peut pas être projetée, et la mesure retombait sur la
        plage entière **sans le dire**. Elle le dit maintenant — motif compris —
        et la page le compte pour **tous** ses textes, pas seulement pour ceux
        joints au rapport.
        """
        ambigu = None
        for candidat in self.candidats():
            if str(candidat.get("id") or "") == "ambigu":
                ambigu = candidat
        if ambigu is None:
            self.fail("le relevé ne nomme pas le texte du halo ambigu : le banc ne peut pas conclure")
        couche = ambigu["couches"][0]
        self.assertEqual(couche["type"], "radial", "la couche du halo ambigu est radiale")
        self.assertIs(
            couche.get("situe"),
            False,
            f"un halo sans rayon en pixels n'est pas situé, couche relevée {couche}",
        )
        self.assertEqual(couche.get("motif"), "rayon-absent-ou-en-pourcentage")
        self.assertEqual(couche["zone"], [0, 1], "non située, la zone vaut la plage entière — majorant assumé")

        contraste = (self.donnees.get("mesures") or [{}])[0].get("contraste") or {}
        self.assertEqual(
            contraste.get("degrades_radiaux_non_situes"),
            1,
            "la page compte un texte jugé contre une plage qu'il ne voit pas — "
            f"compteur relevé : {contraste.get('degrades_radiaux_non_situes')}, "
            f"textes radiaux : {contraste.get('degrades_radiaux')}",
        )
        self.assertEqual(
            (contraste.get("couches_radiales_non_situees") or {}),
            {"rayon-absent-ou-en-pourcentage": 1},
            "le motif du majorant doit être compté, pas seulement le total — "
            f"compteurs relevés : {contraste.get('couches_radiales_non_situees')}",
        )

    def test_le_diagnostic_chiffre_le_majorant_du_banc(self) -> None:
        """Le chiffrage lit le vrai rapport du banc : il ne peut pas mentir sur zéro."""
        bilan = self.cadrages.majorant_radial(self.donnees)
        self.assertTrue(bilan.get("lisible"), f"le rapport du banc doit être lisible : {bilan.get('raison')}")
        self.assertEqual(bilan["textes_non_situes"], 1, f"bilan relevé : {bilan}")
        self.assertEqual(bilan["couches_par_motif"], {"rayon-absent-ou-en-pourcentage": 1}, f"bilan relevé : {bilan}")
        self.assertEqual(bilan["echantillon"], 1, f"le texte du halo ambigu est joint au rapport — bilan relevé : {bilan}")


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
