#!/usr/bin/env python3
"""Confronte le dessin au pixel près dans **tous** les cadrages personnalisés.

La promesse du site est que la mise en page suit l'espace disponible, jamais une
largeur d'écran supposée. Cette promesse n'était vérifiée que dans un seul
cadrage : présentation par défaut, trois tailles de texte, aucune densité. Or le
panneau de personnalisation en propose six présentations (`Lecture`,
`Panorama`, `Vitrine`, `Compacte`, `Mosaïque`) et cinq crans de texte de 75 à
130 %, et `--content` comme les gouttières changent avec eux.

Deux fautes y sont mesurées, et une seule suffit à refuser :

- **le débordement horizontal** — le document doit tenir exactement dans la
  fenêtre, au pixel déclaré près (`tolerance_px`, 0,5 px par défaut : un demi-
  pixel est le plus petit écart qu'un navigateur puisse produire en arrondissant
  une longueur) ;
- **le nombre de colonnes** — chaque grille déclarée dans
  `docs/rd/grilles-dynamiques.toml` doit montrer exactement ce que la feuille
  promet dans ce cadrage-là, pas ce qu'elle montre par défaut.

Le plan est écrit par `--releve-json`, mesuré par `outils/mesurer-cadrages.cjs`,
puis confronté par `--controler`. Un cadrage non mesuré est une **erreur**, pas
un silence : un contrôle incomplet ne vaut pas un contrôle vide.

Usage :
    python3 outils/cadrages.py --releve-json /tmp/plan.json
    node outils/mesurer-cadrages.cjs /tmp/plan.json /tmp/rapport.json
    python3 outils/cadrages.py --controler /tmp/plan.json /tmp/rapport.json
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
import tomllib
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
REGISTRE = "docs/rd/grilles-dynamiques.toml"
# Le registre écrit : dimensions balayées, tolérance, coût. Aucun outil ne
# l'applique — il documente — mais `test_cadrages.py` le confronte au plan,
# sinon il annoncerait éternellement le coût du lot précédent.
REGISTRE_CADRAGES = "docs/rd/cadrages.toml"
FEUILLE = "assets/css/site.css"

#: Les présentations du panneau de personnalisation, avec le nom que le
#: document porte (`data-layout`) et celui que le registre emploie. `None` est la
#: présentation par défaut, celle qui n'écrit aucun `data-layout`.
PRESENTATIONS = (None, "vitrine", "panorama", "compacte", "mosaique", "lecture")

#: Les crans de texte réellement proposés par `site.js` (`textLevels`), ramenés à
#: une échelle. Le cran 100 % vaut 1 : c'est la référence des feuilles.
ECHELLES = {75: 0.75, 85: 0.85, 100: 1.0, 115: 1.15, 130: 1.3}

#: Les pages qui portent le plus de grilles déclarées, une par famille de dessin.
PAGES = ("index.html", "apprendre.html", "ia-societe.html", "simulateur.html")

#: Quatre largeurs qui encadrent les seuils de la feuille : téléphone étroit,
#: téléphone courant, tablette (le seuil de 760 px et sa gouttière) et bureau.
LARGEURS = (320, 390, 768, 1440)


def charger_modele():
    """Importe `modele-grilles.py`, dont le nom porte un tiret."""
    spec = importlib.util.spec_from_file_location("modele_grilles", RACINE / "outils" / "modele-grilles.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules["modele_grilles"] = module
    spec.loader.exec_module(module)
    return module


def lire_registre(chemin: Path) -> dict:
    try:
        return tomllib.loads(chemin.read_text(encoding="utf-8"))
    except (OSError, tomllib.TOMLDecodeError) as erreur:
        raise SystemExit(f"Registre illisible ({chemin}) : {erreur}")


def construire_plan(modele, registre: dict, feuille: str) -> dict:
    """Ce que la feuille promet, cadrage par cadrage, grille par grille."""
    grilles = modele.lire_grilles(feuille)
    capacites = modele.lire_capacites(
        modele.RACINE, [e.get("selecteur") or "" for e in registre.get("grille", [])]
    )
    modele.appliquer_capacites(grilles, capacites)
    trouvees = modele.presentations_lues(grilles, feuille)
    contenus = modele.contenu_des_presentations(feuille)
    pages = modele.pages_des_grilles(modele.RACINE, list(grilles))
    entrees = {e.get("selecteur"): e for e in registre.get("grille", [])}

    defaut = contenus["defaut"]
    combinaisons: list[dict] = []
    for page in PAGES:
        for presentation in PRESENTATIONS:
            for cran, echelle in ECHELLES.items():
                modele.definir_contenu(contenus.get(presentation or "defaut", defaut))
                for largeur in LARGEURS:
                    attendu: dict[str, int] = {}
                    for selecteur, entree in entrees.items():
                        if pages.get(selecteur) != page:
                            continue
                        grille = grilles.get(selecteur)
                        if grille is None or grille.asymetrique:
                            continue
                        ancienne = grille.chaine
                        if pages.get(selecteur):
                            grille.chaine = modele.chaine_d_ancetres(
                                modele.RACINE, pages[selecteur], selecteur
                            )
                        try:
                            regle = (
                                None
                                if presentation is None
                                else modele.regle_applicable(
                                    trouvees, presentation, largeur, selecteur
                                )
                            )
                            nombre = modele.colonnes_attendues(grille, entree, regle, largeur, echelle)
                        finally:
                            grille.chaine = ancienne
                        if nombre:
                            attendu[selecteur] = nombre
                    combinaisons.append(
                        {
                            "page": page,
                            "layout": presentation,
                            "cran": cran,
                            "echelle": echelle,
                            "largeur": largeur,
                            "attendu": attendu,
                        }
                    )
    modele.definir_contenu(defaut)
    grilles_par_page: dict[str, list[str]] = {}
    for combinaison in combinaisons:
        for selecteur in combinaison["attendu"]:
            liste = grilles_par_page.setdefault(combinaison["page"], [])
            if selecteur not in liste:
                liste.append(selecteur)
    return {
        "tolerance_px": 0.5,
        "pages": list(PAGES),
        "grilles": grilles_par_page,
        "combinaisons": combinaisons,
    }


def controler(plan: dict, rapport: dict) -> list[str]:
    """Compare le promis au mesuré. Rend la liste des fautes, jamais un silence."""
    tolerance = float(plan.get("tolerance_px", 0.5))
    mesures = rapport.get("mesures") or []
    if not mesures:
        return [
            "le rapport ne contient aucune mesure — un contrôle incomplet ne vaut pas "
            "un contrôle vide"
        ]
    index = {
        (m.get("page"), m.get("layout"), m.get("cran"), m.get("largeur")): m for m in mesures
    }
    erreurs: list[str] = []
    for combinaison in plan.get("combinaisons", []):
        cle = (
            combinaison["page"],
            combinaison.get("layout"),
            combinaison.get("cran"),
            combinaison["largeur"],
        )
        mesure = index.get(cle)
        libelle = (
            f"{combinaison['page']} · {combinaison.get('layout') or 'défaut'} · "
            f"{combinaison.get('cran')} % · {combinaison['largeur']} px"
        )
        if mesure is None:
            erreurs.append(f"{libelle} : aucune mesure — le cadrage n'a pas été confronté")
            continue
        debordement = mesure.get("debordement")
        if debordement is None:
            erreurs.append(f"{libelle} : débordement non mesuré")
        elif debordement > tolerance:
            coupable = mesure.get("coupable") or {}
            detail = (
                f" — {coupable.get('tag', '?')}"
                + (f".{coupable.get('classe')}" if coupable.get("classe") else "")
                + f" dépasse de {coupable.get('depasse')} px"
                if coupable
                else ""
            )
            erreurs.append(
                f"{libelle} : débordement horizontal de {debordement} px "
                f"(tolérance {tolerance} px){detail}"
            )
        observees = mesure.get("colonnes") or {}
        for selecteur, attendu in (combinaison.get("attendu") or {}).items():
            if selecteur not in observees:
                erreurs.append(f"{libelle} : {selecteur} n'a pas été mesurée")
            elif observees[selecteur] != attendu:
                erreurs.append(
                    f"{libelle} : {selecteur} annonce {attendu} colonne(s), le navigateur "
                    f"en compte {observees[selecteur]}"
                )
    return erreurs


def principal(arguments: list[str] | None = None) -> int:
    analyseur = argparse.ArgumentParser(description="Confronte le dessin dans tous les cadrages personnalisés.")
    analyseur.add_argument("--releve-json", metavar="CHEMIN", help="écrire le plan à mesurer")
    analyseur.add_argument(
        "--controler",
        nargs=2,
        metavar=("PLAN", "RAPPORT"),
        help="confronter un rapport de mesure au plan",
    )
    options = analyseur.parse_args(arguments)

    modele = charger_modele()
    chemin_feuille = RACINE / FEUILLE
    if not chemin_feuille.is_file():
        print(f"Feuille de style introuvable : {FEUILLE}", file=sys.stderr)
        return 2
    feuille = chemin_feuille.read_text(encoding="utf-8")
    modele.definir_gouttiere(feuille)
    modele.definir_feuille(feuille)

    if options.releve_json:
        registre = lire_registre(RACINE / REGISTRE)
        plan = construire_plan(modele, registre, feuille)
        destination = Path(options.releve_json)
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(json.dumps(plan, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
        attendus = sum(len(c["attendu"]) for c in plan["combinaisons"])
        print(
            f"Plan de cadrage écrit : {destination} — {len(plan['combinaisons'])} combinaison(s), "
            f"{attendus} grille(s) à confronter, tolérance {plan['tolerance_px']} px."
        )
        return 0

    if options.controler:
        plan_lu, rapport_lu = options.controler
        try:
            plan = json.loads(Path(plan_lu).read_text(encoding="utf-8"))
            rapport = json.loads(Path(rapport_lu).read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as erreur:
            print(f"Lecture impossible ({erreur}) — aucune confrontation.", file=sys.stderr)
            return 2
        erreurs = controler(plan, rapport)
        if erreurs:
            for erreur in erreurs[:40]:
                print(f"  - {erreur}", file=sys.stderr)
            if len(erreurs) > 40:
                print(f"  … {len(erreurs) - 40} autre(s) écart(s).", file=sys.stderr)
            print(
                f"Refusé : {len(erreurs)} écart(s) entre la feuille et ce que le navigateur "
                f"affiche ({rapport.get('navigateur') or 'navigateur inconnu'}).",
                file=sys.stderr,
            )
            return 1
        combinaisons = len(plan.get("combinaisons", []))
        mesures = len(rapport.get("mesures", []))
        print(
            f"Cadrages : {combinaisons} combinaison(s) mesurée(s) sur {mesures} relevé(s), "
            f"aucun débordement au-delà de {plan.get('tolerance_px')} px, aucun écart de colonnes "
            f"— navigateur {rapport.get('navigateur') or 'inconnu'}."
        )
        return 0

    analyseur.print_help()
    return 2


if __name__ == "__main__":
    sys.exit(principal())
