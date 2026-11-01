#!/usr/bin/env python3
"""Confronte ce que le modèle annonce à ce qu'un navigateur a compté.

Le 1er novembre 2026, trois grilles converties en `flex-wrap` changeaient de
nombre de colonnes à 761 px : une bande d'un seul pixel, que le balayage du
modèle au pas de 10 px n'avait pas vue. Le modèle vérifiait sa propre
arithmétique. Un modèle ne se contredit pas.

Ce rapporteur ne mesure rien et n'invente rien : il lit deux fichiers — la
prédiction de `outils/modele-grilles.py --releve-json` et le relevé de
`outils/mesurer-grilles.cjs` — et dit où les deux divergent, et de combien.

Trois choses qu'il refuse de faire passer pour un succès :

- un rapport vide ou sans navigateur ne prouve rien (code 2) ;
- un point annoncé que le navigateur n'a pas mesuré est compté comme non
  mesuré, jamais comme conforme (code 1) ;
- une divergence est nommée avec sa largeur, son échelle, la valeur annoncée et
  la valeur vue — et, quand l'élément mesuré est plus étroit que le conteneur
  que le modèle présume, la largeur réelle est imprimée à côté : c'est la
  première cause à écarter avant d'accuser la feuille.

Mode `--controler` : une divergence fait sortir en code 1. Sans cette option,
le script reste un relevé — il publie, il ne juge pas encore, et il le dit en
première ligne de sa sortie.

Usage :
    python3 outils/rapporter-mesure-grilles.py --releve releve.json --rapport rapport.json
    python3 outils/rapporter-mesure-grilles.py --releve releve.json --rapport rapport.json --controler
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

RACINE = Path(os.environ.get("MRSC_RACINE") or Path(__file__).resolve().parent.parent).resolve()

#: Contenu que le modèle présume à la largeur d'une fenêtre, pour dire si
#: l'élément mesuré disposait vraiment de cette place. Recopié de
#: `modele-grilles.py` (`conteneur`) à dessein : ce rapporteur ne doit pas
#: dépendre du module qu'il contrôle, sans quoi une erreur du module deviendrait
#: une erreur de mesure. Un écart entre les deux constantes est visible ici.
CONTENU_DEFAUT = 1160
GARNITURE_LATERALE = 48


def conteneur(largeur: int) -> float:
    return min(CONTENU_DEFAUT, largeur - GARNITURE_LATERALE)


class SourceIllisible(Exception):
    """Un des deux fichiers d'entrée manque ou ne se lit pas."""


def lire(chemin: Path, quoi: str) -> dict:
    if not chemin.is_file():
        raise SourceIllisible(f"{quoi} introuvable : {chemin}")
    try:
        contenu = json.loads(chemin.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as erreur:
        raise SourceIllisible(f"{quoi} illisible : {chemin} ({erreur})") from erreur
    if not isinstance(contenu, dict):
        raise SourceIllisible(f"{quoi} n'est pas un objet JSON : {chemin}")
    return contenu


def confronter(releve: dict, rapport: dict) -> dict:
    """Rend les divergences, les points non mesurés et le compte des conformes."""
    mesures = {}
    for entree in rapport.get("mesures", []):
        cle = (entree.get("selecteur"), entree.get("largeur"), entree.get("echelle"))
        if entree.get("trouve") and entree.get("colonnes") is not None:
            mesures[cle] = entree

    resultat: dict = {"grilles": [], "non_mesures": [], "conformes": 0, "total": 0}
    for grille in releve.get("grilles", []):
        selecteur = grille.get("selecteur")
        divergences = []
        manquants = []
        for point in grille.get("points", []):
            resultat["total"] += 1
            cle = (selecteur, point.get("largeur"), point.get("echelle"))
            mesure = mesures.get(cle)
            if mesure is None:
                manquants.append(cle)
                resultat["non_mesures"].append(cle)
                continue
            if mesure["colonnes"] == point.get("attendu"):
                resultat["conformes"] += 1
                continue
            divergences.append(
                {
                    "largeur": point.get("largeur"),
                    "echelle": point.get("echelle"),
                    "attendu": point.get("attendu"),
                    "mesure": mesure["colonnes"],
                    "largeur_element": mesure.get("largeur_element"),
                    "display": mesure.get("display"),
                    "conteneur_presume": round(conteneur(point.get("largeur", 0)), 2),
                    "largeur_cliente": mesure.get("largeur_cliente"),
                }
            )
        resultat["grilles"].append(
            {
                "selecteur": selecteur,
                "page": grille.get("page"),
                "forme": grille.get("forme"),
                "points": len(grille.get("points", [])),
                "divergences": divergences,
                "manquants": manquants,
            }
        )
    return resultat


def principal(arguments: list[str] | None = None) -> int:
    analyseur = argparse.ArgumentParser(
        description="Confronte la prédiction du modèle au relevé d'un navigateur."
    )
    analyseur.add_argument("--releve", required=True, help="prédiction écrite par --releve-json")
    analyseur.add_argument("--rapport", required=True, help="relevé écrit par mesurer-grilles.cjs")
    analyseur.add_argument(
        "--resume",
        action="store_true",
        help="une ligne par grille divergente, lisible telle quelle en annotation",
    )
    analyseur.add_argument(
        "--controler",
        action="store_true",
        help="faire échouer le rapport sur la moindre divergence (sinon : relevé publiable)",
    )
    options = analyseur.parse_args(arguments)

    try:
        releve = lire(Path(options.releve), "prédiction du modèle")
        rapport = lire(Path(options.rapport), "relevé du navigateur")
    except SourceIllisible as erreur:
        print(f"Impossible de confronter : {erreur}", file=sys.stderr)
        return 2

    if not rapport.get("navigateur"):
        print(
            "Impossible de confronter : le rapport ne nomme aucun navigateur — "
            "une mesure sans navigateur ne prouve rien.",
            file=sys.stderr,
        )
        return 2
    if not rapport.get("mesures"):
        print("Impossible de confronter : le rapport ne contient aucune mesure.", file=sys.stderr)
        return 2

    comparaison = confronter(releve, rapport)
    if comparaison["total"] == 0:
        print(
            "Impossible de confronter : la prédiction ne contient aucun point à mesurer.",
            file=sys.stderr,
        )
        return 2

    if options.resume:
        # Une annotation de CI ne garde que quelques lignes : chaque grille doit
        # tenir sur la sienne, avec sa première divergence et la largeur réelle
        # de l'élément mesuré — la première cause à écarter avant d'accuser la
        # feuille.
        for grille in comparaison["grilles"]:
            if not grille["divergences"]:
                continue
            premiere = grille["divergences"][0]
            element = (
                ""
                if premiere["largeur_element"] is None
                else f", élément {premiere['largeur_element']:g} px (présumé "
                f"{premiere['conteneur_presume']:g} px)"
            )
            print(
                f"RESUME {grille['selecteur']} ({grille['page']}) : "
                f"{len(grille['divergences'])} divergence(s) sur {grille['points']} point(s) · "
                f"première à {premiere['largeur']} px (texte ×{premiere['echelle']:g}) : "
                f"annoncé {premiere['attendu']}, vu {premiere['mesure']}{element}"
            )
        return 0

    mode = "CONTRÔLE" if options.controler else "RELEVÉ (pas encore un contrôle)"
    divergentes = [g for g in comparaison["grilles"] if g["divergences"]]
    print(
        f"{mode} — {comparaison['total']} point(s) annoncé(s), "
        f"{comparaison['conformes']} confirmé(s), "
        f"{comparaison['total'] - comparaison['conformes'] - len(comparaison['non_mesures'])} "
        f"divergent(s), {len(comparaison['non_mesures'])} non mesuré(s), "
        f"navigateur {rapport['navigateur']}."
    )

    for grille in comparaison["grilles"]:
        if not grille["divergences"] and not grille["manquants"]:
            continue
        print(
            f"\n{grille['selecteur']} ({grille['page']}, {grille['forme']}) — "
            f"{len(grille['divergences'])} divergence(s) sur {grille['points']} point(s)"
        )
        for divergence in grille["divergences"][:8]:
            indice = (
                ""
                if divergence["largeur_element"] is None
                else (
                    f" · élément {divergence['largeur_element']:g} px, "
                    f"conteneur présumé {divergence['conteneur_presume']:g} px"
                )
            )
            print(
                f"  à {divergence['largeur']} px (texte ×{divergence['echelle']:g}) : "
                f"le modèle annonce {divergence['attendu']} colonne(s), "
                f"le navigateur en compte {divergence['mesure']} ({divergence['display']}){indice}"
                # La grille est répétée sur la ligne : une annotation de CI, un
                # journal filtré ou un extrait collé dans un message doivent se
                # lire seuls. Le 1er novembre 2026, les annotations du premier
                # relevé ne nommaient aucune grille — le titre du groupe était
                # resté en amont du filtre.
                f" · {grille['selecteur']}"
            )
        if len(grille["divergences"]) > 8:
            print(f"  … {len(grille['divergences']) - 8} autre(s) divergence(s) dans le rapport.")
        if grille["manquants"]:
            apercu = ", ".join(f"{largeur}×{echelle:g}" for _, largeur, echelle in grille["manquants"][:6])
            print(
                f"  ! {len(grille['manquants'])} point(s) annoncé(s) sans mesure "
                f"({apercu}{'…' if len(grille['manquants']) > 6 else ''}) — "
                "non mesuré n'est pas conforme"
            )

    if comparaison["non_mesures"]:
        print(
            f"\n{len(comparaison['non_mesures'])} point(s) sur {comparaison['total']} "
            "n'ont pas été mesurés : ce rapport ne dit rien de ces largeurs.",
            file=sys.stderr,
        )

    if not options.controler:
        print(
            "\nRelevé seulement : ces chiffres sont publiés, pas encore jugés. "
            "Passer `--controler` fera échouer le rapport sur la moindre divergence."
        )
        return 0 if not comparaison["non_mesures"] else 1

    if comparaison["non_mesures"]:
        print(
            f"Refusé : {len(comparaison['non_mesures'])} point(s) annoncé(s) sans mesure.",
            file=sys.stderr,
        )
        return 1
    if divergentes:
        print(
            f"Refusé : {sum(len(g['divergences']) for g in divergentes)} divergence(s) "
            f"entre le modèle et le navigateur, sur {len(divergentes)} grille(s).",
            file=sys.stderr,
        )
        return 1
    print("Accord : le navigateur compte les mêmes colonnes que le modèle, à chaque point mesuré.")
    return 0


if __name__ == "__main__":
    raise SystemExit(principal())
