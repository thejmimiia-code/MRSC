#!/usr/bin/env python3
"""Vérifie que le plan complet du projet couvre l’arbre réel, sans rien valider.

Le plan `docs/rd/plan-projet-complet-2026-11-11.md` et sa matrice TOML ne sont
pas des sources de vérité : ce sont des cartes. La garde recalcule, à chaque
lancement, le nombre de fichiers de **chaque zone du dépôt** depuis l’arbre
présent, exige qu’aucun fichier ne reste sans zone, confronte les 19 initiatives
au portefeuille, et refuse qu’une action bloquée par une porte humaine soit
présentée comme faite par l’agent.

Ce contrôle ne juge ni une priorité, ni un scénario prospectif, ni une décision
de l’association. Il empêche seulement la carte de perdre un morceau du projet
ou d’embellir un état. La racine peut être surchargée par `MRSC_RACINE` pour le
banc de mutation, qui travaille sur une copie sans historique Git : l’inventaire
est donc lu sur le système de fichiers, jamais dans l’index Git.

Usage :
    python3 outils/verifier-plan-projet.py
"""

from __future__ import annotations

import os
import re
import sys
import tomllib
from pathlib import Path

RACINE = Path(os.environ.get("MRSC_RACINE") or Path(__file__).resolve().parent.parent).resolve()
PLAN = RACINE / "docs" / "rd" / "plan-projet-complet-2026-11-11.md"
MATRICE = RACINE / "docs" / "rd" / "plan-projet-complet-2026-11-11.toml"
PORTEFEUILLE = RACINE / "docs" / "rd" / "portefeuille.toml"
RELECTURES = RACINE / "docs" / "apprentissage" / "relectures.toml"

#: Dossiers et fichiers qui ne font pas partie du projet livré : caches,
#: historique, brouillons de signature. La copie du banc exclut les mêmes.
EXCLUS = frozenset({
    ".git", "__pycache__", "node_modules", "_site", ".pytest_cache",
    ".mypy_cache", ".ruff_cache", ".cache", ".venv", "venv", "dist",
    "build", "out", "target", "coverage", ".next", ".nuxt", ".output",
})

SECTIONS = (
    "## 1. Portée, méthode et demande",
    "## 2. Inventaire exhaustif du projet",
    "## 3. Toute la R&D : initiatives et état mesuré",
    "## 4. Toute l’innovation encadrée",
    "## 5. Toute la prospective",
    "## 6. Matrice d’exécution",
    "## 7. Ordonnancement et dépendances",
    "## 8. Portes de décision et rôles",
    "## 9. Ce que ce lot a réellement fait",
    "## 10. Limites, entretien et prochaine action",
)

REPERES = (
    "31 janvier 2027", "2026-11-19", "docs/apprentissage/relectures.toml",
    "décision", "11 novembre 2026",
)

ETATS = frozenset({"fait-agent", "a-faire-agent", "bloquee-humain", "en-attente-date"})
TYPES = frozenset({"rd", "innovation", "prospective"})
HORIZONS = ("H0", "H1", "H2", "H3", "H4")

INTERDITES = re.compile(
    r"(?i)\b(?:R&D terminée|validation humaine obtenue|tout est relu|projet achevé|"
    r"expertise obtenue|essai réussi|décision prise par l’agent)\b"
)
SCHEMES = ("http" + "://", "https" + "://")
APOSTROPHE = re.compile(r"\b\w'\w")
CHEMIN = re.compile(
    r"`((?:docs|outils|assets|apprendre|simulateur|api|\.github|\.agents|\.claude|\.githooks)/"
    r"[^`]+?\.(?:md|toml|py|js|cjs|mjs|html|css|json|dot|yml|yaml|txt|xml|sh|patch|sha256|avif|webp|png|jpg|svg))`"
)


def fichiers() -> list[str]:
    """Tous les fichiers du projet, triés, hors caches et brouillons."""
    trouves: list[str] = []
    for dossier, sous_dossiers, noms in os.walk(RACINE):
        sous_dossiers[:] = sorted(d for d in sous_dossiers if d not in EXCLUS)
        for nom in sorted(noms):
            if nom.startswith(".a_signer"):
                continue
            chemin = Path(dossier) / nom
            try:
                relatif = chemin.relative_to(RACINE).as_posix()
            except ValueError:
                continue
            if any(part in EXCLUS for part in Path(relatif).parts):
                continue
            trouves.append(relatif)
    return sorted(trouves)


def zones_reelles() -> dict[str, int]:
    comptes: dict[str, int] = {}
    for relatif in fichiers():
        zone = relatif.split("/", 1)[0] if "/" in relatif else "racine"
        comptes[zone] = comptes.get(zone, 0) + 1
    return comptes


def chaines(valeur: object) -> str:
    return "" if valeur is None else str(valeur)


def controler() -> list[str]:
    erreurs: list[str] = []
    if not PLAN.is_file():
        return [f"plan du projet absent : {PLAN.relative_to(RACINE)}"]
    if not MATRICE.is_file():
        return [f"matrice du projet absente : {MATRICE.relative_to(RACINE)}"]
    texte_plan = PLAN.read_text(encoding="utf-8")
    texte_matrice = MATRICE.read_text(encoding="utf-8")
    try:
        matrice = tomllib.loads(texte_matrice)
    except (OSError, tomllib.TOMLDecodeError) as erreur:
        return [f"matrice illisible : {erreur}"]

    # 1. L’arbre réel, zone par zone, sans total recopié à la main.
    reel = zones_reelles()
    total = sum(reel.values())
    meta = matrice.get("meta", {})
    if meta.get("version") != 1 or chaines(meta.get("auteur")) != "agent":
        erreurs.append("matrice : version ou auteur absent — la carte doit être datée et attribuée à l’agent")
    if chaines(meta.get("date")) != "2026-11-11":
        erreurs.append("matrice : date du lot absente ou inexacte")
    if meta.get("total") != total:
        erreurs.append(f"total de fichiers inexact : {meta.get('total')} annoncé, {total} présents")
    for champ, attendu in (
        ("zones", len(reel)), ("initiatives", len(matrice.get("initiative", []))),
        ("actions", len(matrice.get("action", []))), ("portes", len(matrice.get("porte", []))),
        ("horizons", len(matrice.get("horizon", []))),
    ):
        if meta.get(champ) != attendu:
            erreurs.append(f"matrice : compte « {champ} » inexact : {meta.get(champ)} au lieu de {attendu}")

    zones = matrice.get("zone", [])
    vues: set[str] = set()
    for zone in zones:
        identifiant = chaines(zone.get("id"))
        if identifiant in vues:
            erreurs.append(f"zone déclarée deux fois : {identifiant}")
        vues.add(identifiant)
        if identifiant not in reel:
            erreurs.append(f"zone surnuméraire : {identifiant}")
            continue
        if zone.get("nombre") != reel[identifiant]:
            erreurs.append(
                f"nombre de fichiers inexact pour la zone {identifiant} : "
                f"{zone.get('nombre')} annoncé, {reel[identifiant]} présents"
            )
        for champ in ("surface", "source_verite", "garde", "etat", "prochaine_action", "limite"):
            if len(chaines(zone.get(champ))) < 3:
                erreurs.append(f"zone {identifiant} : champ « {champ} » absent")
        for champ in ("source_verite", "garde"):
            cible = chaines(zone.get(champ))
            if cible and not (RACINE / cible).exists():
                erreurs.append(f"zone {identifiant} : {champ} introuvable : {cible}")
    for absente in sorted(set(reel) - vues):
        erreurs.append(f"zone absente du plan du projet : {absente}")
    if sum(int(z.get("nombre", 0)) for z in zones) != total:
        erreurs.append("somme des zones différente du total réel")

    # 2. Les 19 initiatives du portefeuille, sans état embelli.
    try:
        portefeuille = tomllib.loads(PORTEFEUILLE.read_text(encoding="utf-8"))
    except (OSError, tomllib.TOMLDecodeError) as erreur:
        return [f"portefeuille illisible : {erreur}"]
    initiatives = {str(i.get("id")): i for i in portefeuille.get("initiative", []) if i.get("id")}
    declarees: set[str] = set()
    for entree in matrice.get("initiative", []):
        identifiant = chaines(entree.get("id"))
        if identifiant in declarees:
            erreurs.append(f"initiative déclarée deux fois : {identifiant}")
        declarees.add(identifiant)
        if identifiant not in initiatives:
            erreurs.append(f"initiative en trop dans la matrice : {identifiant}")
            continue
        source = initiatives[identifiant]
        if chaines(entree.get("priorite")) != chaines(source.get("priorite")):
            erreurs.append(f"initiative {identifiant} : priorité diverge du portefeuille")
        if chaines(entree.get("etat")) != chaines(source.get("etat")):
            erreurs.append(f"initiative {identifiant} : état diverge du portefeuille")
        if len(chaines(entree.get("chantier"))) < 1:
            erreurs.append(f"initiative {identifiant} : chantier absent")
        for champ in ("action_agent", "preuve"):
            if len(chaines(entree.get(champ))) < 3:
                erreurs.append(f"initiative {identifiant} : champ « {champ} » absent")
        preuve = chaines(entree.get("preuve"))
        if preuve and not (RACINE / preuve).exists():
            erreurs.append(f"initiative {identifiant} : preuve introuvable : {preuve}")
    for absente in sorted(set(initiatives) - declarees):
        erreurs.append(f"initiative absente du plan du projet : {absente}")

    # 3. La matrice d’exécution : chaque action nomme une preuve et une limite.
    actions = matrice.get("action", [])
    ids_actions: set[str] = set()
    compte_etats = {etat: 0 for etat in ETATS}
    for action in actions:
        identifiant = chaines(action.get("id"))
        if identifiant in ids_actions:
            erreurs.append(f"action déclarée deux fois : {identifiant}")
        ids_actions.add(identifiant)
        etat = chaines(action.get("etat"))
        if etat not in ETATS:
            erreurs.append(f"état d’action inconnu : {identifiant} : {etat}")
        else:
            compte_etats[etat] += 1
        if chaines(action.get("type")) not in TYPES:
            erreurs.append(f"type d’action inconnu : {identifiant} : {action.get('type')}")
        if chaines(action.get("initiative")) not in initiatives:
            erreurs.append(f"action sans initiative connue : {identifiant}")
        preuve = chaines(action.get("preuve"))
        if not preuve or not (RACINE / preuve).exists():
            erreurs.append(f"preuve introuvable : {identifiant} : {preuve}")
        dependance = chaines(action.get("dependance", "aucune"))
        if dependance != "aucune" and dependance not in ids_actions:
            erreurs.append(f"dépendance inconnue : {identifiant} → {dependance}")
        if len(chaines(action.get("critere"))) < 20:
            erreurs.append(f"action {identifiant} : critère de sortie trop court")
        if len(chaines(action.get("limite"))) < 30:
            erreurs.append(f"action {identifiant} : limite trop courte")
        porte = chaines(action.get("porte", "aucune"))
        if etat == "fait-agent" and porte != "aucune":
            erreurs.append(f"porte humaine présentée comme franchie : {identifiant} → {porte}")
    for etat, nombre in (
        ("fait_agent", compte_etats["fait-agent"]),
        ("a_faire_agent", compte_etats["a-faire-agent"]),
        ("bloquee_humain", compte_etats["bloquee-humain"]),
        ("en_attente_date", compte_etats["en-attente-date"]),
    ):
        if meta.get(etat) != nombre:
            erreurs.append(f"matrice : compte « {etat} » inexact : {meta.get(etat)} au lieu de {nombre}")
        if nombre == 0:
            erreurs.append(f"matrice : aucun état « {etat} » — la carte masquerait une catégorie de travail")

    # 4. Portes humaines et horizons : aucune ne peut être déclarée franchie.
    portes = matrice.get("porte", [])
    ids_portes: set[str] = set()
    for porte in portes:
        identifiant = chaines(porte.get("id"))
        ids_portes.add(identifiant)
        for champ in ("role", "preuve", "limite"):
            if len(chaines(porte.get(champ))) < 5:
                erreurs.append(f"porte {identifiant} : champ « {champ} » absent")
        if chaines(porte.get("etat")) != "ouverte":
            erreurs.append(f"porte {identifiant} : état doit rester « ouverte »")
    if len(portes) < 5:
        erreurs.append("moins de cinq portes humaines déclarées")
    for horizon in HORIZONS:
        if horizon not in {chaines(h.get("id")) for h in matrice.get("horizon", [])}:
            erreurs.append(f"horizon absent : {horizon}")

    # 5. Le texte du plan : sections, repères, chemins locaux, aucune URL externe.
    for section in SECTIONS:
        if section not in texte_plan:
            erreurs.append(f"section absente du plan du projet : {section}")
    for repere in REPERES:
        if repere not in texte_plan:
            erreurs.append(f"repère absent du plan du projet : {repere}")
    for chemin in sorted(set(CHEMIN.findall(texte_plan))):
        if not (RACINE / chemin).exists():
            erreurs.append(f"chemin local introuvable : {chemin}")
    if str(total) not in texte_plan:
        erreurs.append(f"le plan n’annonce pas le total réel de {total} fichiers")
    for nom, texte in (("plan", texte_plan), ("matrice", texte_matrice)):
        for scheme in SCHEMES:
            if scheme in texte:
                erreurs.append(f"{nom} : URL externe recopiée ({scheme})")
        trouve = INTERDITES.search(texte)
        if trouve:
            erreurs.append(f"{nom} : formulation interdite : {trouve.group(0)}")
        if APOSTROPHE.search(texte):
            erreurs.append(f"{nom} : apostrophe droite — employer l’apostrophe typographique")

    # 6. Aucune relecture humaine fabriquée par l’agent.
    if RELECTURES.is_file():
        try:
            humaines = tomllib.loads(RELECTURES.read_text(encoding="utf-8"))
        except tomllib.TOMLDecodeError as erreur:
            erreurs.append(f"registre humain illisible : {erreur}")
        else:
            if humaines.get("relecture"):
                erreurs.append("registre humain non vide : une carte d’agent ne doit jamais y écrire")
    return erreurs


def main() -> int:
    erreurs = controler()
    if erreurs:
        print("ÉCHEC — plan complet du projet", file=sys.stderr)
        for erreur in erreurs:
            print(f"    {erreur}", file=sys.stderr)
        return 1
    reel = zones_reelles()
    matrice = tomllib.loads(MATRICE.read_text(encoding="utf-8"))
    print(
        f"Plan du projet vérifié : {sum(reel.values())} fichiers en {len(reel)} zones, "
        f"{len(matrice.get('initiative', []))} initiatives, "
        f"{len(matrice.get('action', []))} actions, "
        f"{len(matrice.get('porte', []))} portes humaines ouvertes, "
        f"{len(SECTIONS)} sections, aucune validation inventée."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
