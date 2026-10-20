#!/usr/bin/env python3
"""Construit la carte des lacunes du catalogue d'apprentissage.

Ce script ne recherche rien et ne relit rien. Il rend lisible, à une date
donnée, ce que le référentiel déclare déjà : combien de sujets sont actifs,
partiels, à créer ou à faire relire par une personne experte, lesquels n'ont
encore aucune fiche, et quelle exigence de preuve s'applique à chacun.

La carte est dérivée uniquement de `docs/apprentissage/referentiel.toml`,
`docs/apprentissage/catalogue.toml` et de la date de revue du portefeuille.
Elle ne contient aucune source externe, aucun chiffre d'usage et aucune note
de qualité : une case vide n'est pas un défaut, c'est une case à travailler.

Les domaines sensibles reprennent la liste de `AGENTS.md` (santé, droit et
démarches, argent, politique publique). Un sujet marqué `revue-experte` exige
une relecture experte même hors de ces domaines.

Usage :
    python3 outils/construire-carte-lacunes.py             # écrit docs/rd/carte-lacunes.md
    python3 outils/construire-carte-lacunes.py --verifier  # échoue si le fichier a divergé
    python3 outils/construire-carte-lacunes.py --sortie autre.md
"""

from __future__ import annotations

import argparse
import sys
import tomllib
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent

# Statuts éditoriaux : définitions partagées, jamais recopiées en chaîne locale.
sys.path.insert(0, str(RACINE / "outils"))
from statuts_editoriaux import PROTOTYPE, RELU, est_prototype, est_relue, porte_un_statut  # noqa: E402
CATALOGUE = RACINE / "docs" / "apprentissage" / "catalogue.toml"
REFERENTIEL = RACINE / "docs" / "apprentissage" / "referentiel.toml"
PORTEFEUILLE = RACINE / "docs" / "rd" / "portefeuille.toml"
SORTIE = RACINE / "docs" / "rd" / "carte-lacunes.md"
DOSSIER_CARTES = RACINE / "docs" / "rd"

#: Domaines dont les contenus exigent, selon AGENTS.md, une relecture par une
#: personne compétente avant diffusion publique.
DOMAINES_SENSIBLES = {
    "sante-securite-corps": "santé et sécurité",
    "demarches-droits-travail": "droit, démarches et travail",
    "economie-finances": "argent, budget et finances",
    "citoyennete-medias": "politique publique, médias et information",
}

ORDRE_STATUTS = ("actif", "partiel", "a-creer", "revue-experte")


def charger() -> tuple[list[dict], dict[str, str], str]:
    catalogue = tomllib.loads(CATALOGUE.read_text(encoding="utf-8"))
    referentiel = tomllib.loads(REFERENTIEL.read_text(encoding="utf-8"))
    portefeuille = tomllib.loads(PORTEFEUILLE.read_text(encoding="utf-8"))
    revue = str(portefeuille.get("meta", {}).get("derniere_revue", "date inconnue"))
    return catalogue["fiche"], referentiel["domaine"], revue


def exigence(domaine_id: str, statut: str) -> str:
    if statut == "revue-experte":
        return "Relecture par une personne experte du sujet, puis sources primaires datées"
    if domaine_id in DOMAINES_SENSIBLES:
        return f"Relecture par une personne compétente en {DOMAINES_SENSIBLES[domaine_id]}, puis sources primaires datées"
    return "Sources primaires datées, relecture éditoriale, puis contrôle d'accessibilité"


def ligne(cellules: list[str]) -> str:
    return "| " + " | ".join(cellules) + " |"


def construire(fiches: list[dict], domaines: list[dict], revue: str) -> str:
    ids_fiches = {fiche["id"] for fiche in fiches}
    prototypes = sum(1 for fiche in fiches if est_prototype(fiche))
    totaux = {statut: 0 for statut in ORDRE_STATUTS}
    sans_fiche: list[tuple[str, str, str, str, str]] = []
    references_absentes: list[str] = []
    par_domaine: list[dict] = []
    sujets_avec_carte: list[str] = []
    for domaine in domaines:
        compte = {statut: 0 for statut in ORDRE_STATUTS}
        sans = 0
        for sujet in domaine.get("sujet", []):
            if (DOSSIER_CARTES / f"sujet-{sujet['id']}.md").is_file():
                sujets_avec_carte.append(sujet["id"])
            statut = sujet.get("statut", "inconnu")
            compte[statut] = compte.get(statut, 0) + 1
            totaux[statut] = totaux.get(statut, 0) + 1
            fiches_sujet = sujet.get("fiches") or []
            for reference in fiches_sujet:
                if reference not in ids_fiches:
                    references_absentes.append(f"{sujet['id']} → {reference}")
            if not fiches_sujet:
                sans += 1
                carte = DOSSIER_CARTES / f"sujet-{sujet['id']}.md"
                sans_fiche.append(
                    (
                        domaine["titre"],
                        sujet["titre"],
                        statut,
                        exigence(domaine["id"], statut),
                        f"[carte de sujet]({carte.name})" if carte.is_file() else "—",
                    )
                )
        par_domaine.append({"titre": domaine["titre"], "sujets": len(domaine.get("sujet", [])), "compte": compte, "sans": sans})

    total_sujets = sum(totaux.values())
    textes: list[str] = []
    textes.append("# Carte des lacunes du catalogue d'apprentissage")
    textes.append("")
    textes.append(
        "**Nature :** carte de travail générée depuis `docs/apprentissage/referentiel.toml`, "
        "`docs/apprentissage/catalogue.toml` et `docs/rd/portefeuille.toml`. Elle ne recherche "
        "rien, ne relit rien et ne valide rien. Une case vide est une case à travailler, pas "
        "un défaut établi."
    )
    textes.append("")
    textes.append(f"**Date de référence :** celle de la revue de portefeuille, `{revue}`.")
    textes.append("")
    textes.append("## 1. Où en est la carte")
    textes.append("")
    textes.append(ligne(["Mesure", "Valeur"]))
    textes.append(ligne(["---", "---:"]))
    textes.append(ligne(["Sujets du référentiel", str(total_sujets)]))
    for statut in ORDRE_STATUTS:
        textes.append(ligne([f"dont `{statut}`", str(totaux.get(statut, 0))]))
    textes.append(ligne(["Domaines", str(len(domaines))]))
    textes.append(ligne(["Fiches publiées", str(len(fiches))]))
    textes.append(ligne(["dont prototypes à relire", str(prototypes)]))
    textes.append(ligne(["Sujets sans aucune fiche", str(len(sans_fiche))]))
    textes.append(ligne(["Sujets ouverts par une carte de sujet", str(len(sujets_avec_carte))]))
    if sujets_avec_carte:
        textes.append(ligne(["Lesquels", ", ".join(f"`{sujet}`" for sujet in sujets_avec_carte)]))
    if references_absentes:
        textes.append(ligne(["Références de fiches introuvables", str(len(references_absentes))]))
    textes.append("")
    textes.append("## 2. Répartition par domaine")
    textes.append("")
    textes.append(ligne(["Domaine", "Sujets", "actif", "partiel", "à créer", "revue experte", "sans fiche"]))
    textes.append(ligne(["---", "---:", "---:", "---:", "---:", "---:", "---:"]))
    for bloc in par_domaine:
        compte = bloc["compte"]
        textes.append(
            ligne(
                [
                    bloc["titre"],
                    str(bloc["sujets"]),
                    str(compte.get("actif", 0)),
                    str(compte.get("partiel", 0)),
                    str(compte.get("a-creer", 0)),
                    str(compte.get("revue-experte", 0)),
                    str(bloc["sans"]),
                ]
            )
        )
    textes.append("")
    textes.append(f"## 3. Les {len(sans_fiche)} sujets sans aucune fiche")
    textes.append("")
    textes.append(
        f"Ce sont les seuls sujets dont l'absence est déclarée dans le référentiel. Les {totaux.get('partiel', 0)} sujets `partiel` "
        "ont déjà au moins une fiche : leur manque est à qualifier sujet par sujet, il n'est pas listé ici."
    )
    textes.append("")
    textes.append(ligne(["Domaine", "Sujet", "Statut", "Exigence de preuve avant publication", "Travail ouvert"]))
    textes.append(ligne(["---", "---", "---", "---", "---"]))
    for titre_domaine, titre_sujet, statut, exigence_sujet, carte_sujet in sans_fiche:
        textes.append(ligne([titre_domaine, titre_sujet, f"`{statut}`", exigence_sujet, carte_sujet]))
    textes.append("")
    textes.append("## 4. Ce que cette carte ne dit pas")
    textes.append("")
    textes.append("- Elle ne dit pas qu'un sujet absent du référentiel n'existe pas : le référentiel est une carte de travail, pas un inventaire du savoir.")
    textes.append(f"- Elle ne dit rien de la qualité des {len(fiches)} fiches publiées ni de l'exactitude de leur contenu.")
    textes.append("- Elle ne fournit aucune source : chaque sujet ouvert doit encore être documenté auprès de sources primaires, avec leur date, leur périmètre et leurs droits.")
    textes.append("- Elle ne hiérarchise pas les domaines : un domaine à onze sujets à créer n'est pas « plus important » qu'un domaine à un sujet.")
    textes.append("- Elle applique l'exigence de preuve du domaine déclaré : un sujet de santé rangé sous « études supérieures » (ISCED-F 09) reçoit l'exigence générale. Ce classement est à corriger au cas par cas, pas à lire comme une règle de risque.")
    if references_absentes:
        textes.append("- Elle signale des références de fiches absentes du catalogue : " + ", ".join(references_absentes) + ". À corriger dans le référentiel ou dans le catalogue.")
    textes.append("")
    textes.append("## 5. Comment avancer")
    textes.append("")
    textes.append("1. Choisir un sujet de la section 3 et écrire sa carte de sujet (identité, portée, relations, preuve, forme d'apprentissage, statut, entretien) selon `docs/rd-innovation-continue.md`.")
    textes.append("2. Rechercher des sources primaires datées ; si aucune n'est accessible, laisser le sujet ouvert plutôt que de le remplir par une affirmation non traçable.")
    textes.append("3. Fabriquer une fiche seulement après la relecture exigée dans la dernière colonne ; conserver le statut « Prototype à relire » tant que la preuve humaine manque.")
    textes.append("4. Régénérer cette carte après toute modification du référentiel et vérifier qu'aucun sujet n'a disparu par accident.")
    textes.append("")
    textes.append("Régénérer avec `python3 outils/construire-carte-lacunes.py` ; vérifier avec `--verifier`.")
    textes.append("")
    return "\n".join(textes)


def main() -> int:
    parseur = argparse.ArgumentParser(description=__doc__)
    parseur.add_argument("--verifier", action="store_true", help="échouer si le fichier a divergé")
    parseur.add_argument("--sortie", type=Path, default=SORTIE, help="chemin du fichier produit")
    arguments = parseur.parse_args()

    fiches, domaines, revue = charger()
    contenu = construire(fiches, domaines, revue)
    sortie = arguments.sortie if arguments.sortie.is_absolute() else RACINE / arguments.sortie

    if arguments.verifier:
        if not sortie.exists():
            print(f"{sortie.relative_to(RACINE)} absent : lancez le script sans --verifier.", file=sys.stderr)
            return 1
        if sortie.read_text(encoding="utf-8") != contenu:
            print(
                f"{sortie.relative_to(RACINE)} a divergé du référentiel : régénérez-le.",
                file=sys.stderr,
            )
            return 1
        print(f"La carte des lacunes est à jour ({sortie.relative_to(RACINE)}).")
        return 0

    sortie.parent.mkdir(parents=True, exist_ok=True)
    sortie.write_text(contenu, encoding="utf-8")
    print(f"{sortie.relative_to(RACINE)} écrit : {len(contenu)} caractères")
    return 0


if __name__ == "__main__":
    sys.exit(main())
