#!/usr/bin/env python3
"""Prototype borné de confrontation d'affirmations aux pages sources déclarées.

Ce script répond à l'initiative `confronter-une-affirmation-a-sa-source` :
peut-on vérifier mécaniquement qu'une page citée contient encore les termes clés
d'une affirmation de fiche, sans lire à la place d'une personne et sans stocker
d'extrait sous droits ?

Principes et garde-fous :
- Aucune citation longue ni extrait de la source externe n'est enregistré :
  seules des ancres lexicales courtes (1 à 5 mots, 40 caractères au maximum)
  sont comparées.
- Le résultat n'est jamais une validation ni un verdict sur la fiche : quatre
  états de relevé existent (`indice-concordant`, `constat-couverture-partielle`,
  `constat-ancre-absente`, `constat-page-inaccessible`).
- Chaque entrée doit documenter explicitement un mécanisme de faux positif, un
  mécanisme de faux négatif et une limite d'au moins 120 caractères.
- Ce dispositif reste un outil d'exploration R&D, volontairement hors de la
  porte de publication tant que son taux d'erreur n'a pas été mesuré sur un
  échantillon relu par une personne.

Usage :
    python3 outils/confronter-sources.py              # écrit docs/rd/confrontations-sources.md
    python3 outils/confronter-sources.py --verifier   # échoue si le rapport a divergé
    python3 outils/confronter-sources.py --sortie autre.md
"""

from __future__ import annotations

import argparse
import re
import sys
import tomllib
from datetime import date
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
SOURCE = RACINE / "docs" / "rd" / "confrontations-sources.toml"
CATALOGUE = RACINE / "docs" / "apprentissage" / "catalogue.toml"
SORTIE = RACINE / "docs" / "rd" / "confrontations-sources.md"

CHAMPS = (
    "id",
    "fiche",
    "url_source",
    "affirmation_fiche",
    "ancres_attendues",
    "date_releve",
    "etat_releve",
    "faux_positif_possible",
    "faux_negatif_possible",
    "limite",
)
CHAMPS_INTERDITS = ("extrait_source", "citation_source", "texte_source", "contenu_source")
ETATS = {
    "indice-concordant": "Indice concordant — toutes les ancres figuraient dans la page à la date du relevé (ne vaut pas validation)",
    "constat-couverture-partielle": "Constat de couverture partielle — certaines ancres sont absentes de cette source précise, à interpréter par une personne",
    "constat-ancre-absente": "Constat d'ancre absente — aucune ancre repérée, vérifier si la page a changé ou si le vocabulaire diffère",
    "constat-page-inaccessible": "Constat de page inaccessible — la page n'a pas pu être lue au moment du relevé, aucune conclusion sur la fiche",
}
MOTS_ANCRE_MAX = 5
CARACTERES_ANCRE_MAX = 40
ANALYSE_MIN = 80
LIMITE_MIN = 120
FICHES_MIN = 3


def normaliser(texte: str) -> str:
    """Normalise espaces, apostrophes et casse pour la recherche d'ancres courtes."""
    propre = texte.replace("\u2019", "'").replace("\u00a0", " ")
    return " ".join(propre.split()).casefold()


def confronter_texte(texte_page: str | None, ancres: list[str]) -> dict[str, object]:
    """Confronte une liste d'ancres courtes au texte extrait d'une page.

    Une page absente (`None` ou vide) produit toujours `constat-page-inaccessible`,
    jamais un échec silencieux ni une conclusion sur la fiche.
    """
    nettoyees = [str(a).strip() for a in ancres if str(a).strip()]
    if texte_page is None or not str(texte_page).strip():
        return {
            "etat": "constat-page-inaccessible",
            "ancres_reperees": [],
            "ancres_absentes": nettoyees,
            "note": "Page inaccessible ou vide au moment du relevé : constat explicite, aucune conclusion sur la fiche.",
        }
    cible = normaliser(texte_page)
    reperees: list[str] = []
    absentes: list[str] = []
    for ancre in nettoyees:
        if normaliser(ancre) in cible:
            reperees.append(ancre)
        else:
            absentes.append(ancre)
    if not absentes:
        etat = "indice-concordant"
    elif reperees:
        etat = "constat-couverture-partielle"
    else:
        etat = "constat-ancre-absente"
    return {
        "etat": etat,
        "ancres_reperees": reperees,
        "ancres_absentes": absentes,
        "note": ETATS[etat],
    }


def charger(source: Path = SOURCE) -> dict:
    return tomllib.loads(source.read_text(encoding="utf-8"))


def index_catalogue(catalogue_path: Path = CATALOGUE) -> dict[str, set[str]]:
    donnees = tomllib.loads(catalogue_path.read_text(encoding="utf-8"))
    resultat: dict[str, set[str]] = {}
    for fiche in donnees.get("fiche", []):
        identifiant = str(fiche.get("id", "")).strip()
        if not identifiant:
            continue
        urls = {
            str(src.get("url", "")).strip()
            for src in (fiche.get("sources") or [])
            if isinstance(src, dict) and str(src.get("url", "")).strip()
        }
        resultat[identifiant] = urls
    return resultat


def valider(
    registre: dict,
    aujourdhui: date,
    fiches_urls: dict[str, set[str]] | None = None,
    racine: Path = RACINE,
) -> list[str]:
    """Vérifie la structure, l'absence d'extrait sous droits et les garde-fous méthodologiques."""
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

    entrees = registre.get("confrontation")
    if not isinstance(entrees, list) or not entrees:
        return erreurs + ["aucune confrontation déclarée"]

    if fiches_urls is None:
        fiches_urls = index_catalogue()

    vus: set[str] = set()
    fiches_couvertes: set[str] = set()

    for index, entree in enumerate(entrees, start=1):
        if not isinstance(entree, dict):
            erreurs.append(f"entrée {index} : ce n'est pas une table")
            continue
        identifiant = str(entree.get("id", "")).strip()
        etiquette = identifiant or f"entrée {index}"

        interdits = [champ for champ in CHAMPS_INTERDITS if champ in entree]
        if interdits:
            erreurs.append(
                f"{etiquette} : champ(s) interdit(s) {', '.join(interdits)} — ne stocker aucun extrait sous droits"
            )

        absents = [champ for champ in CHAMPS if not entree.get(champ)]
        if absents:
            erreurs.append(f"{etiquette} : champs manquants {', '.join(absents)}")
        if not identifiant:
            continue
        if identifiant in vus:
            erreurs.append(f"{etiquette} : identifiant dupliqué")
        vus.add(identifiant)
        if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)+", identifiant):
            erreurs.append(f"{etiquette} : identifiant non slug")

        fiche = str(entree.get("fiche", "")).strip()
        url_source = str(entree.get("url_source", "")).strip()
        if fiche not in fiches_urls:
            erreurs.append(f"{etiquette} : fiche inconnue du catalogue ({fiche})")
        else:
            fiches_couvertes.add(fiche)
            if url_source and url_source not in fiches_urls[fiche]:
                erreurs.append(
                    f"{etiquette} : url_source ({url_source}) absente des sources de {fiche} dans le catalogue"
                )

        ancres = entree.get("ancres_attendues")
        if not isinstance(ancres, list) or len(ancres) < 2:
            erreurs.append(f"{etiquette} : au moins deux ancres courtes sont exigées dans ancres_attendues")
            ancres = []
        else:
            for ancre in ancres:
                texte_ancre = str(ancre).strip()
                mots = texte_ancre.split()
                if not texte_ancre:
                    erreurs.append(f"{etiquette} : ancre vide dans ancres_attendues")
                elif len(mots) > MOTS_ANCRE_MAX or len(texte_ancre) > CARACTERES_ANCRE_MAX:
                    erreurs.append(
                        f"{etiquette} : ancre trop longue « {texte_ancre} » "
                        f"(max {MOTS_ANCRE_MAX} mots et {CARACTERES_ANCRE_MAX} caractères pour éviter tout extrait sous droits)"
                    )

        reperees = entree.get("ancres_reperees")
        absentes_ancre = entree.get("ancres_absentes")
        if not isinstance(reperees, list) or not isinstance(absentes_ancre, list):
            erreurs.append(f"{etiquette} : ancres_reperees et ancres_absentes doivent être des listes")
        elif ancres:
            attendu_set = [str(a).strip() for a in ancres]
            combine = [str(a).strip() for a in reperees] + [str(a).strip() for a in absentes_ancre]
            if sorted(combine) != sorted(attendu_set):
                erreurs.append(
                    f"{etiquette} : ancres_reperees + ancres_absentes ne correspondent pas à ancres_attendues"
                )

        quand = entree.get("date_releve")
        if not isinstance(quand, date):
            erreurs.append(f"{etiquette} : date_releve absente ou non lue comme une date")
        elif quand > aujourdhui:
            erreurs.append(f"{etiquette} : date_releve dans le futur ({quand.isoformat()})")

        etat = str(entree.get("etat_releve", "")).strip()
        if etat not in ETATS:
            erreurs.append(
                f"{etiquette} : etat_releve inconnu ou interdit ({etat}) — valeurs permises : {', '.join(ETATS)}"
            )
        elif isinstance(reperees, list) and isinstance(absentes_ancre, list) and ancres:
            if etat == "indice-concordant" and absentes_ancre:
                erreurs.append(f"{etiquette} : indice-concordant incohérent avec ancres_absentes non vide")
            elif etat == "constat-couverture-partielle" and (not reperees or not absentes_ancre):
                erreurs.append(
                    f"{etiquette} : constat-couverture-partielle exige au moins une ancre repérée et une absente"
                )
            elif etat == "constat-ancre-absente" and reperees:
                erreurs.append(f"{etiquette} : constat-ancre-absente incohérent avec ancres_reperees non vide")
            elif etat == "constat-page-inaccessible" and reperees:
                erreurs.append(f"{etiquette} : constat-page-inaccessible ne peut pas déclarer d'ancres repérées")

        for champ_analyse in ("faux_positif_possible", "faux_negatif_possible"):
            valeur = str(entree.get(champ_analyse, "")).strip()
            if valeur and len(valeur) < ANALYSE_MIN:
                erreurs.append(
                    f"{etiquette} : {champ_analyse} trop court ({len(valeur)} caractères, {ANALYSE_MIN} exigés)"
                )

        limite = str(entree.get("limite", "")).strip()
        if limite and len(limite) < LIMITE_MIN:
            erreurs.append(f"{etiquette} : limite trop courte ({len(limite)} caractères, {LIMITE_MIN} exigés)")

    if len(fiches_couvertes) < FICHES_MIN:
        erreurs.append(
            f"prototype insuffisant : {len(fiches_couvertes)} fiche(s) couverte(s), au moins {FICHES_MIN} exigées"
        )

    return erreurs


def resumer(registre: dict) -> dict[str, object]:
    entrees = [e for e in registre.get("confrontation", []) if isinstance(e, dict)]
    par_etat: dict[str, int] = {}
    for entree in entrees:
        etat = str(entree.get("etat_releve", ""))
        par_etat[etat] = par_etat.get(etat, 0) + 1
    return {
        "nombre": len(entrees),
        "fiches": sorted({str(e.get("fiche", "")) for e in entrees if e.get("fiche")}),
        "par_etat": par_etat,
    }


def construire(registre: dict) -> str:
    chiffres = resumer(registre)
    revue = registre["meta"]["derniere_revue"]
    lignes: list[str] = [
        "# Prototype de confrontation d'affirmations aux sources déclarées",
        "",
        "**Document de travail R&D généré — hors porte de publication.** Il éprouve l'initiative "
        "`confronter-une-affirmation-a-sa-source` sur un échantillon de fiches déjà pourvues d'une page "
        "précise ouverte et datée. Il ne valide aucune fiche, ne remplace aucune relecture humaine et ne "
        "stocke aucun extrait sous droits.",
        "",
        "**Question testée :** peut-on vérifier mécaniquement qu'une page citée contient encore les repères "
        "clés d'une affirmation de fiche, sans lire à la place d'une personne ? **Réponse observée sur "
        "l'échantillon :** les ancres courtes produisent un **indice de maintenance** utile, mais souffrent "
        "de faux positifs (négation non détectée, chiffre présent dans une autre colonne) et de faux "
        "négatifs (formules coupées dans un PDF, périmètre réparti entre deux sources, synonymes).",
        "",
        f"**Date du relevé :** {revue.isoformat()}.",
        "",
        "## 1. Synthèse de l'échantillon",
        "",
        "| Mesure | Valeur |",
        "| --- | ---: |",
        f"| Confrontations documentées | {chiffres['nombre']} |",
        f"| Fiches distinctes couvertes | {len(chiffres['fiches'])} |",
    ]
    for cle, libelle in ETATS.items():
        if chiffres["par_etat"].get(cle):
            titre_court = libelle.split(" — ")[0]
            lignes.append(f"| {titre_court} (`{cle}`) | {chiffres['par_etat'][cle]} |")
    lignes.extend(
        [
            "",
            "Aucun des états ci-dessus n'est une validation éditoriale ni un verdict d'erreur contre la fiche.",
            "",
            "## 2. Détail par confrontation",
            "",
        ]
    )
    for entree in sorted(registre.get("confrontation", []), key=lambda e: str(e.get("id", ""))):
        reperees = ", ".join(f"`{a}`" for a in entree.get("ancres_reperees", [])) or "aucune"
        absentes = ", ".join(f"`{a}`" for a in entree.get("ancres_absentes", [])) or "aucune"
        lignes.extend(
            [
                f"### `{entree['id']}` (`{entree['fiche']}`)",
                "",
                f"- **Source confrontée :** `{entree['url_source']}`",
                f"- **Affirmation de la fiche (texte M.R.S.C.) :** {entree['affirmation_fiche']}",
                f"- **Ancres cherchées ({len(entree['ancres_attendues'])}) :** "
                + ", ".join(f"`{a}`" for a in entree["ancres_attendues"]),
                f"- **Ancres repérées :** {reperees}",
                f"- **Ancres absentes :** {absentes}",
                f"- **État du relevé ({entree['date_releve'].isoformat()}) :** `{entree['etat_releve']}` — {ETATS[entree['etat_releve']]}",
                f"- **Faux positif documenté :** {entree['faux_positif_possible']}",
                f"- **Faux négatif documenté :** {entree['faux_negatif_possible']}",
                f"- **Limite :** {entree['limite']}",
                "",
            ]
        )
    lignes.extend(
        [
            "## 3. Pourquoi ce dispositif reste hors de la porte de publication",
            "",
            "1. **Faux positifs avérés :** sur `econ-distinguer-interet-frais` (Service-Public F2451), des mots comme « améliore » et « budget » apparaissent dans la liste des mentions publicitaires interdites ; sur `maths-reperer-angle-droit`, « 90° » apparaît aussi dans les bornes des angles aigus et obtus.",
            "2. **Faux négatifs avérés :** sur `sciences-calculer-vitesse-moyenne`, l'extraction du PDF Éduscol découpe « durée » en « dur é e » dans la formule mathématique ; sur `sciences-distinguer-melange-changement-etat`, l'étayage est réparti entre deux documents complémentaires.",
            "3. **Règle de décision :** une page inaccessible ou modifiée produit un constat pour orienter la veille humaine, jamais un échec automatique de publication ni une conclusion sur la vérité de la fiche.",
            "",
            "Généré depuis `docs/rd/confrontations-sources.toml` ; vérifier avec `python3 outils/confronter-sources.py --verifier`.",
            "",
        ]
    )
    return "\n".join(lignes)


def main() -> int:
    analyseur = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    analyseur.add_argument("--verifier", action="store_true", help="échouer si le fichier généré a divergé")
    analyseur.add_argument("--sortie", type=Path, default=SORTIE, help="chemin du rapport Markdown produit")
    arguments = analyseur.parse_args()

    try:
        registre = charger()
        fiches_urls = index_catalogue()
    except (OSError, tomllib.TOMLDecodeError) as erreur:
        print(f"Registre des confrontations illisible : {erreur}", file=sys.stderr)
        return 2

    aujourdhui = date.today()
    erreurs = valider(registre, aujourdhui, fiches_urls)
    if erreurs:
        print("Registre des confrontations invalide :", file=sys.stderr)
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
            f"Prototype de confrontation à jour ({nom}) : {chiffres['nombre']} confrontation(s) "
            f"sur {len(chiffres['fiches'])} fiche(s)."
        )
        return 0

    sortie.parent.mkdir(parents=True, exist_ok=True)
    sortie.write_text(contenu, encoding="utf-8")
    print(f"{nom} écrit : {len(contenu)} caractères — {chiffres['nombre']} confrontation(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
