#!/usr/bin/env python3
"""Nomme, dans une annotation GitHub, ce que la mesure navigateur a refusé.

Le job `graphismes` mesure trois visuels dans un vrai navigateur et écrit ses
résultats dans des fichiers JSON ; il échoue ensuite sur un code de sortie. Le
31 octobre 2026, ce job est tombé en rouge et **personne ne pouvait dire
pourquoi** : les journaux et les artefacts vivent sur un stockage que l'atelier
n'atteint pas, et l'étape n'émettait aucune annotation. Un contrôle qui échoue
sans dire ce qu'il a vu oblige à relancer à l'aveugle.

Ce script lit les relevés et imprime une ligne `::error title=...::...` par
constat. GitHub les transforme en annotations, lisibles par l'API — donc par un
mainteneur qui n'a pas les journaux. Il ne juge rien : il recopie ce que les
mesures ont écrit, et dit quand il ne trouve rien.

Usage :
    python3 outils/annoncer-echec-graphismes.py <dossier des relevés>
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

#: Longueur maximale d'une annotation GitHub.
LONGUEUR = 900

#: Ce qui situe un constat : sans ces clés, une erreur ne dit ni où ni quand.
SITUATION = ("page", "largeur", "dpr", "texte", "disposition", "mode")

#: Le motif, et les nombres qui l'expliquent.
MOTIFS = "erreurs"
NOMBRES = ("source", "densite", "distorsion")


def releves(dossier: Path) -> list[Path]:
    """Les relevés JSON du dossier, triés — y compris ceux des passes mutées."""
    if not dossier.is_dir():
        return []
    return sorted(chemin for chemin in dossier.glob("*.json") if chemin.is_file())


def est_mutation(chemin: Path) -> bool:
    """Un relevé de mutation *doit* porter des constats : c'est son travail."""
    return chemin.name.startswith("mutation-")


def _nombre(valeur: object) -> object:
    if isinstance(valeur, float):
        return round(valeur, 2)
    if isinstance(valeur, int) and not isinstance(valeur, bool):
        return valeur
    return None


def decrire(erreur: object) -> str:
    """Décrit un constat : où, dans quel mode, et **pourquoi**.

    La première version de ce script s'arrêtait aux six premières clés du
    relevé. Or `erreurs` vient en dernier, après la situation : l'annotation
    nommait la page, la largeur et le mode, et **taisait le motif** — c'est-à-
    dire exactement ce qui manquait. Un ordre de dictionnaire n'est pas un
    ordre d'importance.
    """
    if not isinstance(erreur, dict):
        return str(erreur)
    morceaux = [f"{cle}={erreur[cle]}" for cle in SITUATION if cle in erreur]
    motifs = erreur.get(MOTIFS)
    if isinstance(motifs, list) and motifs:
        morceaux.append("motif: " + " ; ".join(str(motif) for motif in motifs))
    for cle in NOMBRES:
        valeur = _nombre(erreur.get(cle))
        if valeur is not None:
            morceaux.append(f"{cle}={valeur}")
    return ", ".join(morceaux) if morceaux else json.dumps(erreur, ensure_ascii=False)[:400]


def charger(chemin: Path) -> tuple[list[str], int] | str:
    """Rend les constats d'un relevé et le nombre de constats restants, ou son défaut."""
    try:
        donnees = json.loads(chemin.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as erreur:
        return f"{chemin.name} : illisible ({erreur})"
    if not isinstance(donnees, dict):
        return f"{chemin.name} : forme inattendue (ni objet JSON, ni relevé)"
    erreurs = donnees.get(MOTIFS)
    if not isinstance(erreurs, list):
        return f"{chemin.name} : pas de liste « {MOTIFS} » — relevé d'une autre forme"
    lignes = [f"{chemin.name} : {decrire(erreur)}" for erreur in erreurs[:6]]
    return lignes, max(0, len(erreurs) - 6)


def annoncer(dossier: Path) -> int:
    """Imprime une annotation par constat. Ne juge rien, mais ne se tait sur rien."""
    fichiers = releves(dossier)
    if not fichiers:
        print(
            f"::error title=Graphismes::aucun relevé dans {dossier} — "
            "la mesure n'a pas tourné ou n'a rien écrit"
        )
        return 0

    vides: list[str] = []
    constats_ecrits = False
    for chemin in fichiers:
        resultat = charger(chemin)
        if isinstance(resultat, str):
            print(f"::error title=Graphismes::{resultat[:LONGUEUR]}")
            continue
        lignes, restants = resultat
        if est_mutation(chemin):
            # Une passe mutée réussit quand elle *trouve* ce qu'elle devait
            # trouver. Annoncer ces constats comme des échecs ferait croire à
            # trois pannes de plus, et noierait le vrai constat.
            if lignes:
                print(
                    f"::notice title=Graphismes::{chemin.name} : {len(lignes) + restants} "
                    "constat(s) attendu(s) par la mutation, jugés par verifier-mutation-graphismes.py"
                )
            else:
                print(
                    f"::error title=Graphismes::{chemin.name} : la mutation n'a provoqué "
                    "aucun constat — le contrôle ne mord pas"
                )
            continue
        if not lignes:
            vides.append(chemin.name)
            continue
        constats_ecrits = True
        for ligne in lignes:
            print(f"::error title=Graphismes::{ligne[:LONGUEUR]}")
        if restants:
            print(f"::error title=Graphismes::{chemin.name} : … {restants} autre(s) constat(s)")

    if vides and not constats_ecrits:
        print(
            "::error title=Graphismes::aucun constat nulle part ("
            + ", ".join(vides)
            + ") — l'échec vient d'une assertion du script, pas d'une mesure"
        )
    return 0


def principal(arguments: list[str]) -> int:
    if len(arguments) != 1:
        print(__doc__, file=sys.stderr)
        return 2
    return annoncer(Path(arguments[0]))


if __name__ == "__main__":
    sys.exit(principal(sys.argv[1:]))
