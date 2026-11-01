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

#: Distance, en pixels, sous laquelle une prédiction n'en est plus une.
#:
#: À 0,3 px du point de bascule, la largeur d'une barre de défilement, l'arrondi
#: de `vw` ou le sous-pixel de la mise en page décident à la place du modèle. Le
#: 1er novembre 2026, `.hero-grid` prédisait une colonne à 743 px et le navigateur
#: en comptait deux : l'écart valait 0,28 px. Sans ce seuil nommé, cette
#: divergence se lirait comme une erreur de 700 px, et un `--controler` la
#: refuserait — donc on élargirait les bases jusqu'à ce que le hasard soit
#: d'accord, ce qui n'apprend rien. La tolérance est **plus petite qu'une colonne**
#: (une colonne fait au moins 145 px ici) : elle ne peut masquer aucune erreur
#: réelle, et elle est comptée, jamais absorbée.
SEUIL_PX = 1.0

#: Ce rapporteur ne calcule **aucune** largeur. La largeur que le modèle présume
#: par largeur pour les enfants d'une grille est écrite dans la prédiction
#: (`conteneur`), point par point. La recalculer ici aurait deux défauts d'un
#: coup : deux arithmétiques capables de diverger, et une accusation portée
#: contre la feuille pour un désaccord entre deux constantes. Le 1er novembre
#: 2026, cette valeur valait 48 px de gouttière partout, alors que la feuille en
#: écrit 32 sous 760 px : c'est précisément l'erreur qu'il fallait voir, pas
#: reproduire.


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


def contexte(divergence: dict) -> str:
    """« , élément 728 px (présumé 712 px) » — ou rien quand rien n'est mesuré.

    Deux largeurs différentes sous le même nom feraient accuser la feuille d'un
    artefact du navigateur. Quand la prédiction ne porte pas de conteneur, le
    rapport dit « non déclaré » plutôt que de laisser croire à un accord.
    """
    if divergence.get("largeur_element") is None:
        return ""
    presume = divergence.get("conteneur_presume")
    marge = divergence.get("marge")
    ou = (
        f", élément {divergence['largeur_element']:g} px (conteneur non déclaré)"
        if presume is None
        else f", élément {divergence['largeur_element']:g} px (présumé {presume:g} px)"
    )
    if marge is not None:
        ou += f", à {float(marge):.2f} px du seuil"
    return ou


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
                    "conteneur_presume": point.get("conteneur"),
                    "largeur_cliente": mesure.get("largeur_cliente"),
                    "marge": point.get("marge"),
                    "au_seuil": (
                        point.get("marge") is not None and float(point["marge"]) < SEUIL_PX
                    ),
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
            element = contexte(premiere)
            print(
                f"RESUME {grille['selecteur']} ({grille['page']}) : "
                f"{len(grille['divergences'])} divergence(s) sur {grille['points']} point(s) · "
                f"première à {premiere['largeur']} px (texte ×{premiere['echelle']:g}) : "
                f"annoncé {premiere['attendu']}, vu {premiere['mesure']}{element}"
            )
        # Le total est imprimé à part : un canal d'annotations qui ne garde que
        # dix lignes doit pouvoir montrer qu'on lui en a coupé. Le 1er novembre
        # 2026, le premier relevé publié annonçait 70 divergences et n'en nommait
        # que 23 : GitHub plafonne les annotations d'une étape, et rien dans la
        # sortie ne disait combien de lignes avaient été perdues.
        total_seuil = sum(
            1
            for g in comparaison["grilles"]
            for d in g["divergences"]
            if d.get("au_seuil")
        )
        print(
            f"RESUME TOTAL {sum(1 for g in comparaison['grilles'] if g['divergences'])} "
            f"grille(s), {comparaison['total'] - comparaison['conformes'] - len(comparaison['non_mesures'])} "
            f"divergence(s) dont {total_seuil} au seuil, sur {comparaison['total']} point(s) "
            f"annoncé(s), {len(comparaison['non_mesures'])} non mesuré(s)"
        )
        return 0

    mode = "CONTRÔLE" if options.controler else "RELEVÉ (pas encore un contrôle)"
    divergentes = [g for g in comparaison["grilles"] if g["divergences"]]
    toutes = [d for g in divergentes for d in g["divergences"]]
    au_seuil = [d for d in toutes if d["au_seuil"]]
    ailleurs = [d for d in toutes if not d["au_seuil"]]
    print(
        f"{mode} — {comparaison['total']} point(s) annoncé(s), "
        f"{comparaison['conformes']} confirmé(s), {len(toutes)} divergent(s) "
        f"dont {len(au_seuil)} au seuil (moins de {SEUIL_PX:g} px), "
        f"{len(comparaison['non_mesures'])} non mesuré(s), "
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
            indice = contexte(divergence)
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
    if ailleurs:
        grilles_ailleurs = {
            g["selecteur"] for g in divergentes if any(not d["au_seuil"] for d in g["divergences"])
        }
        print(
            f"Refusé : {len(ailleurs)} divergence(s) hors du seuil de {SEUIL_PX:g} px, "
            f"sur {len(grilles_ailleurs)} grille(s) — "
            + ", ".join(sorted(grilles_ailleurs)[:8]),
            file=sys.stderr,
        )
        return 1
    if au_seuil:
        print(
            f"Accord hors seuil : {len(au_seuil)} divergence(s) à moins de {SEUIL_PX:g} px "
            "de la bascule — comptées, non absorbées, et sans effet sur le nombre de "
            "colonnes d'une largeur voisine."
        )
    else:
        print("Accord : le navigateur compte les mêmes colonnes que le modèle, à chaque point mesuré.")
    return 0


if __name__ == "__main__":
    raise SystemExit(principal())
