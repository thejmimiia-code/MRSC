#!/usr/bin/env python3
"""Vérifie et génère le registre des sources tentées et refusées.

Ce script ne visite aucune adresse Web et ne juge aucune source. Il vérifie
hors ligne que chaque refus consigné dans `docs/apprentissage/sources-refusees.toml`
porte :
- un identifiant unique, une fiche existante du catalogue, une adresse HTTPS et
  une date réelle non future ;
- une catégorie de motif connue, un motif explicite sans recopie de contenu sous
  droits et une limite d'interprétation ;
- une décision cohérente avec `docs/apprentissage/catalogue.toml` : une adresse
  refusée ne doit jamais figurer parmi les sources actives du catalogue, et une
  source dite « remplacée » doit désigner une adresse réellement présente sur la
  fiche concernée.

Il produit `docs/apprentissage/sources-refusees.md` à partir de
`docs/apprentissage/sources-refusees.toml`.

Usage :
    python3 outils/construire-sources-refusees.py              # écrit docs/apprentissage/sources-refusees.md
    python3 outils/construire-sources-refusees.py --verifier   # échoue si le fichier a divergé
    python3 outils/construire-sources-refusees.py --sortie autre.md
"""

from __future__ import annotations

import argparse
import re
import sys
import tomllib
from datetime import date
from pathlib import Path
from urllib.parse import urlparse

RACINE = Path(__file__).resolve().parent.parent
SOURCE = RACINE / "docs" / "apprentissage" / "sources-refusees.toml"
CATALOGUE = RACINE / "docs" / "apprentissage" / "catalogue.toml"
SORTIE = RACINE / "docs" / "apprentissage" / "sources-refusees.md"

CHAMPS = (
    "id",
    "fiche",
    "titre_pressenti",
    "url",
    "date",
    "categorie_motif",
    "motif",
    "decision",
    "limite",
)
CATEGORIES = {
    "acces-refuse-403": "Accès refusé (HTTP 403)",
    "acces-payant": "Accès payant ou réservé aux abonnés",
    "page-introuvable": "Page introuvable ou retirée (HTTP 404/410)",
    "hors-perimetre": "Contenu hors du périmètre cherché après lecture",
    "portail-sans-page": "Racine ou portail sans page précise à confronter",
}
DECISIONS = {
    "remplacee": "Remplacée par une autre page ouverte et lue",
    "portail-conserve": "Portail conservé par écrit en l'attente d'une page précise",
    "en-attente": "En attente d'une autre source primaire accessible",
}
MOTIF_MIN = 80
LIMITE_MIN = 100
CITATION_MAX = 60


def charger(source: Path = SOURCE) -> dict:
    return tomllib.loads(source.read_text(encoding="utf-8"))


def index_catalogue(catalogue_path: Path = CATALOGUE) -> dict[str, set[str]]:
    """Associe chaque identifiant de fiche à l'ensemble des URL déclarées."""
    donnees = tomllib.loads(catalogue_path.read_text(encoding="utf-8"))
    resultat: dict[str, set[str]] = {}
    for fiche in donnees.get("fiche", []):
        identifiant = str(fiche.get("id", "")).strip()
        if not identifiant:
            continue
        urls = {
            str(source.get("url", "")).strip()
            for source in (fiche.get("sources") or [])
            if isinstance(source, dict) and str(source.get("url", "")).strip()
        }
        resultat[identifiant] = urls
    return resultat


def valider(
    registre: dict,
    aujourdhui: date,
    fiches_urls: dict[str, set[str]] | None = None,
    racine: Path = RACINE,
) -> list[str]:
    """Retourne les erreurs de structure et de cohérence avec le catalogue."""
    erreurs: list[str] = []
    meta = registre.get("meta")
    if not isinstance(meta, dict):
        return ["section [meta] absente"]
    if meta.get("version") != 1:
        erreurs.append("meta.version doit valoir 1")
    revue = meta.get("derniere_revue")
    if not isinstance(revue, date):
        erreurs.append("meta.derniere_revue absente ou non lue comme une date")
    elif revue > aujourdhui:
        erreurs.append(f"meta.derniere_revue dans le futur ({revue.isoformat()})")
    source_cat = str(meta.get("source_catalogue", "")).strip()
    if not source_cat or not (racine / source_cat).is_file():
        erreurs.append("meta.source_catalogue absente ou introuvable")

    refus_liste = registre.get("refus")
    if not isinstance(refus_liste, list) or not refus_liste:
        return erreurs + ["aucun refus déclaré"]

    if fiches_urls is None:
        fiches_urls = index_catalogue()
    toutes_urls_actives = {url for urls in fiches_urls.values() for url in urls}

    vus_ids: set[str] = set()
    vus_couples: set[tuple[str, str]] = set()

    for index, entree in enumerate(refus_liste, start=1):
        if not isinstance(entree, dict):
            erreurs.append(f"entrée {index} : ce n'est pas une table")
            continue
        identifiant = str(entree.get("id", "")).strip()
        etiquette = identifiant or f"entrée {index}"
        absents = [champ for champ in CHAMPS if not entree.get(champ)]
        if absents:
            erreurs.append(f"{etiquette} : champs manquants {', '.join(absents)}")
        if not identifiant:
            continue
        if identifiant in vus_ids:
            erreurs.append(f"{etiquette} : identifiant dupliqué")
        vus_ids.add(identifiant)
        if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)+", identifiant):
            erreurs.append(f"{etiquette} : identifiant non slug (minuscules, chiffres et tirets)")

        fiche = str(entree.get("fiche", "")).strip()
        if fiche and fiche not in fiches_urls:
            erreurs.append(f"{etiquette} : fiche inconnue du catalogue ({fiche})")

        url = str(entree.get("url", "")).strip()
        if url:
            analyse = urlparse(url)
            if not url.startswith("https://") or not analyse.netloc or analyse.path in ("", "/"):
                if entree.get("categorie_motif") != "portail-sans-page":
                    erreurs.append(f"{etiquette} : l'URL refusée doit être une page HTTPS précise ({url})")
            if url in toutes_urls_actives:
                erreurs.append(
                    f"{etiquette} : l'URL refusée {url} est encore citée comme source active dans le catalogue"
                )
            couple = (fiche, url)
            if couple in vus_couples:
                erreurs.append(f"{etiquette} : couple (fiche, url) déjà consigné")
            vus_couples.add(couple)

        quand = entree.get("date")
        if not isinstance(quand, date):
            erreurs.append(f"{etiquette} : date absente ou non lue comme une date")
        elif quand > aujourdhui:
            erreurs.append(f"{etiquette} : date dans le futur ({quand.isoformat()})")

        categorie = str(entree.get("categorie_motif", "")).strip()
        if categorie and categorie not in CATEGORIES:
            erreurs.append(f"{etiquette} : categorie_motif inconnue ({categorie})")

        motif = str(entree.get("motif", "")).strip()
        if motif:
            if len(motif) < MOTIF_MIN:
                erreurs.append(f"{etiquette} : motif trop court ({len(motif)} caractères, {MOTIF_MIN} exigés)")
            for citation in re.findall(r"«([^»]+)»", motif):
                if len(citation.strip()) > CITATION_MAX:
                    erreurs.append(
                        f"{etiquette} : extrait entre guillemets trop long dans motif "
                        f"({len(citation.strip())} caractères > {CITATION_MAX}) — ne stocker aucun passage sous droits"
                    )

        decision = str(entree.get("decision", "")).strip()
        if decision and decision not in DECISIONS:
            erreurs.append(f"{etiquette} : décision inconnue ({decision})")
        elif decision == "remplacee":
            remplacement = str(entree.get("url_remplacement", "")).strip()
            if not remplacement:
                erreurs.append(f"{etiquette} : decision = 'remplacee' exige url_remplacement")
            elif fiche in fiches_urls and remplacement not in fiches_urls[fiche]:
                erreurs.append(
                    f"{etiquette} : url_remplacement ({remplacement}) absente des sources de {fiche} dans le catalogue"
                )

        limite = str(entree.get("limite", "")).strip()
        if limite and len(limite) < LIMITE_MIN:
            erreurs.append(f"{etiquette} : limite trop courte ({len(limite)} caractères, {LIMITE_MIN} exigés)")

    return erreurs


def resumer(registre: dict) -> dict[str, object]:
    entrees = [e for e in registre.get("refus", []) if isinstance(e, dict)]
    par_categorie: dict[str, int] = {}
    for entree in entrees:
        cat = str(entree.get("categorie_motif", ""))
        par_categorie[cat] = par_categorie.get(cat, 0) + 1
    dates = sorted(e["date"] for e in entrees if isinstance(e.get("date"), date))
    return {
        "nombre": len(entrees),
        "fiches": sorted({str(e.get("fiche", "")) for e in entrees if e.get("fiche")}),
        "remplacees": sum(1 for e in entrees if e.get("decision") == "remplacee"),
        "par_categorie": par_categorie,
        "premiere": dates[0] if dates else None,
        "derniere": dates[-1] if dates else None,
    }


def construire(registre: dict) -> str:
    chiffres = resumer(registre)
    revue = registre["meta"]["derniere_revue"]
    lignes: list[str] = [
        "# Registre des sources tentées et refusées",
        "",
        "**Document de travail généré.** Il recense les pages qui ont été tentées pour étayer une fiche du "
        "catalogue mais qui ont été écartées après vérification : accès refusé (HTTP 403), accès payant, "
        "page introuvable ou contenu hors du périmètre cherché après lecture.",
        "",
        "**Ce que ce registre empêche :** qu'un autre agent ne retente puis ne cite une page illisible ou "
        "hors sujet pour faire baisser le nombre de constats sans preuve réelle. **Ce qu'il ne prouve pas :** "
        "qu'une fiche est relue, ni que toutes les sources possibles d'un sujet ont été explorées.",
        "",
        f"**Date de révision du registre :** {revue.isoformat()}.",
        "",
        "## 1. Vue d'ensemble",
        "",
        "| Mesure | Valeur |",
        "| --- | ---: |",
        f"| Sources refusées consignées | {chiffres['nombre']} |",
        f"| Fiches du catalogue concernées | {len(chiffres['fiches'])} |",
        f"| Refus suivis d'une page de remplacement ouverte et lue | {chiffres['remplacees']} |",
    ]
    for cle, libelle in CATEGORIES.items():
        if chiffres["par_categorie"].get(cle):
            lignes.append(f"| Motif : {libelle} | {chiffres['par_categorie'][cle]} |")
    lignes.extend(
        [
            "",
            "Un refus consigné ne valide jamais la fiche associée : le statut éditorial dépend uniquement "
            "du registre des relectures humaines (`docs/apprentissage/relectures.toml`).",
            "",
            "## 2. Détail des refus consignés",
            "",
        ]
    )
    entrees = sorted(
        registre.get("refus", []),
        key=lambda e: (e.get("date") or revue, str(e.get("id", ""))),
    )
    for entree in entrees:
        cat = CATEGORIES.get(str(entree["categorie_motif"]), str(entree["categorie_motif"]))
        dec = DECISIONS.get(str(entree["decision"]), str(entree["decision"]))
        lignes.extend(
            [
                f"### `{entree['id']}` — {entree['titre_pressenti']}",
                "",
                f"- **Fiche concernée :** `{entree['fiche']}`",
                f"- **Adresse écartée :** `{entree['url']}`",
                f"- **Date de la tentative :** {entree['date'].isoformat()}",
                f"- **Catégorie de refus :** {cat} (`{entree['categorie_motif']}`)",
                f"- **Motif constaté :** {entree['motif']}",
                f"- **Décision retenue :** {dec} (`{entree['decision']}`)",
            ]
        )
        if entree.get("url_remplacement"):
            lignes.append(f"- **Source de remplacement dans le catalogue :** `{entree['url_remplacement']}`")
        lignes.extend(
            [
                f"- **Limite — ce que ce refus ne dit pas :** {entree['limite']}",
                "",
            ]
        )
    lignes.extend(
        [
            "## 3. Garde-fous vérifiés par la porte",
            "",
            "- Une adresse inscrite dans ce registre ne peut pas figurer simultanément parmi les sources actives de `docs/apprentissage/catalogue.toml`.",
            "- Lorsqu'un refus est marqué `remplacee`, l'adresse `url_remplacement` doit être présente sur la fiche concernée dans le catalogue.",
            "- Aucun extrait long sous droits n'est stocké dans le champ `motif` : seule la raison factuelle du refus est consignée.",
            "- Toute entrée sans date réelle, sans motif explicite ou sans limite écrite fait échouer le contrôle.",
            "",
            "Généré depuis `docs/apprentissage/sources-refusees.toml` ; vérifier avec `python3 outils/construire-sources-refusees.py --verifier`.",
            "",
        ]
    )
    return "\n".join(lignes)


def main() -> int:
    analyseur = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    analyseur.add_argument("--verifier", action="store_true", help="échouer si le fichier généré a divergé")
    analyseur.add_argument("--sortie", type=Path, default=SORTIE, help="chemin du fichier Markdown produit")
    arguments = analyseur.parse_args()

    try:
        registre = charger()
        fiches_urls = index_catalogue()
    except (OSError, tomllib.TOMLDecodeError) as erreur:
        print(f"Registre des sources refusées illisible : {erreur}", file=sys.stderr)
        return 2

    aujourdhui = date.today()
    erreurs = valider(registre, aujourdhui, fiches_urls)
    if erreurs:
        print("Registre des sources refusées invalide :", file=sys.stderr)
        for erreur in erreurs:
            print(f"  - {erreur}", file=sys.stderr)
        return 1

    contenu = construire(registre)
    sortie = arguments.sortie if arguments.sortie.is_absolute() else RACINE / arguments.sortie
    nom = str(sortie.relative_to(RACINE)) if sortie.is_relative_to(RACINE) else str(sortie)
    chiffres = resumer(registre)

    if arguments.verifier:
        if not sortie.exists():
            print(f"{nom} absent : lancez le script sans --verifier.", file=sys.stderr)
            return 1
        if sortie.read_text(encoding="utf-8") != contenu:
            print(f"{nom} a divergé du registre : régénérez-le.", file=sys.stderr)
            return 1
        print(
            f"Registre des sources refusées à jour ({nom}) : {chiffres['nombre']} refus traçable(s) "
            f"sur {len(chiffres['fiches'])} fiche(s)."
        )
        return 0

    sortie.parent.mkdir(parents=True, exist_ok=True)
    sortie.write_text(contenu, encoding="utf-8")
    print(f"{nom} écrit : {len(contenu)} caractères — {chiffres['nombre']} refus traçable(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
