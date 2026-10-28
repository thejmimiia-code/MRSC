#!/usr/bin/env python3
"""Construit la file de relecture des prototypes du catalogue.

Ce script ne relit rien. Il produit une file de travail ordonnée pour une
personne : quels prototypes existent, dans quel domaine, avec quel repère,
combien de sources déclarées, et lesquels touchent des sujets à relecture
spécialisée (santé, droit et démarches, argent, politique publique).

Le repérage des sujets sensibles combine deux règles explicites :

1. le domaine du catalogue (`sante-securite-corps`, `demarches-droits-travail`,
   `economie-finances`, `citoyennete-medias`) ;
2. une liste de mots-clés observés dans le titre, le résumé, l'objectif, les
   notions, l'exercice et la correction.

Les deux règles sont des heuristiques de triage : elles peuvent manquer un
sujet sensible ou en signaler un par excès. Le tableau des motifs affiche les
termes trouvés pour qu'une personne puisse corriger le classement. Aucun des
champs produits n'est une note de qualité, et rien ici ne vaut validation.

Usage :
    python3 outils/file-relecture.py             # écrit docs/apprentissage/file-relecture.md
    python3 outils/file-relecture.py --verifier  # échoue si le fichier a divergé
    python3 outils/file-relecture.py --sortie autre.md
"""

from __future__ import annotations

import argparse
import os
import re
import sys
import tomllib
from pathlib import Path

#: Racine lue par l'outil. La surcharge sert au banc de mutation
#: (`outils/test_mutations_files_relecture.py`), qui ajoute une fiche au
#: catalogue ou le laisse diverger dans une copie du dépôt.
RACINE = Path(os.environ.get("MRSC_RACINE") or Path(__file__).resolve().parent.parent).resolve()

# Statuts éditoriaux : définitions partagées, jamais recopiées en chaîne locale.
sys.path.insert(0, str(RACINE / "outils"))
from statuts_editoriaux import PROTOTYPE, RELU, est_prototype, est_relue, porte_un_statut  # noqa: E402
CATALOGUE = RACINE / "docs" / "apprentissage" / "catalogue.toml"
REFERENTIEL = RACINE / "docs" / "apprentissage" / "referentiel.toml"
SORTIE = RACINE / "docs" / "apprentissage" / "file-relecture.md"

# Domaines dont les contenus exigent, selon AGENTS.md, une relecture par une
# personne compétente dans le domaine avant diffusion publique.
DOMAINES_SENSIBLES = {
    "sante-securite-corps": "santé et sécurité",
    "demarches-droits-travail": "droit, démarches et travail",
    "economie-finances": "argent, budget et finances",
    "citoyennete-medias": "politique publique, médias et information",
}

# Termes observés dans les champs éditoriaux. Chaque terme est rattaché à une
# famille de risque pour que la file reste lisible.
MOTS_CLES: dict[str, tuple[str, ...]] = {
    "santé": (
        "médecin", "médicament", "ordonnance", "vaccin", "symptôme", "diagnostic",
        "traitement", "urgence vitale", "dépistage", "pharmacie", "allergie",
        "grossesse", "handicap", "soins",
    ),
    "argent": (
        "impôt", "salaire", "smic", "prêt", "crédit", "dette", "assurance",
        "épargne", "intérêts", "amende", "allocation", "prestation", "cotisation",
        "taux d’intérêt", "découvert",
    ),
    "droit et démarches": (
        "litige", "recours", "tribunal", "avocat", "licenciement", "contrat de travail",
        "bail", "loyer", "caution", "héritage", "succession", "testament", "pension",
        "retraite", "aide sociale", "préfecture", "code du travail", "juridique",
        "droit du travail",
    ),
    "politique publique": (
        "élection", "vote", "élu", "assemblée nationale", "parlement", "constitution",
        "politique publique", "collectivité", "référendum", "démocratie", "scrutin",
        "mandat électoral", "service public",
    ),
    "données personnelles": (
        "donnée personnelle", "données personnelles", "rgpd", "consentement",
        "mot de passe", "phishing", "hameçonnage", "usurpation", "carte bancaire",
        "identité numérique", "fuite de données",
    ),
}

CHAMPS_ANALYSES = ("titre", "resume", "objectif", "situation", "exercice", "aide", "a_retenir")
CHAMPS_LISTES = ("notions", "demarche", "correction", "transferer")


def charger() -> tuple[list[dict], dict[str, str]]:
    catalogue = tomllib.loads(CATALOGUE.read_text(encoding="utf-8"))
    referentiel = tomllib.loads(REFERENTIEL.read_text(encoding="utf-8"))
    titres = {domaine["id"]: domaine["titre"] for domaine in referentiel["domaine"]}
    return catalogue["fiche"], titres


def texte_analysable(fiche: dict) -> str:
    morceaux = [str(fiche.get(champ, "")) for champ in CHAMPS_ANALYSES]
    for champ in CHAMPS_LISTES:
        valeur = fiche.get(champ)
        if isinstance(valeur, list):
            morceaux.extend(str(element) for element in valeur)
        elif valeur:
            morceaux.append(str(valeur))
    for notion in fiche.get("notions", []) or []:
        morceaux.append(str(notion))
    return " ".join(morceaux).lower()


def motifs(fiche: dict) -> list[str]:
    """Termes repérés par mots-clés entiers, hors motif de domaine."""
    texte = texte_analysable(fiche)
    trouves: list[str] = []
    for famille, termes in MOTS_CLES.items():
        hits = sorted({terme for terme in termes if re.search(rf"(?<![\w-]){re.escape(terme)}(?![\w-])", texte)})
        if hits:
            trouves.append(f"{famille} : " + ", ".join(hits[:4]))
    return trouves


def ligne_tableau(cellules: list[str]) -> str:
    return "| " + " | ".join(cellules) + " |"


def construire(fiches: list[dict], titres: dict[str, str]) -> str:
    prototypes = [fiche for fiche in fiches if est_prototype(fiche)]
    enrichis = []
    for fiche in prototypes:
        famille = DOMAINES_SENSIBLES.get(fiche["domaine"])
        enrichis.append(
            {
                "fiche": fiche,
                "famille": famille,
                "motifs": motifs(fiche),
                "sources": len(fiche.get("sources", []) or []),
            }
        )
    enrichis.sort(
        key=lambda item: (
            0 if item["famille"] else 1,
            -len(item["motifs"]),
            item["sources"],
            item["fiche"]["domaine"],
            item["fiche"]["id"],
        )
    )
    par_domaine_sensible = sum(1 for item in enrichis if item["famille"])
    signalees_hors_domaine = sum(1 for item in enrichis if not item["famille"] and item["motifs"])

    lignes: list[str] = []
    lignes.append("# File de relecture des prototypes")
    lignes.append("")
    lignes.append(
        "**Document de travail généré.** Cette file ne relit rien et ne valide rien : "
        "elle range les prototypes du catalogue pour qu’une personne puisse organiser "
        "les relectures exigées par la [grille de relecture](grille-relecture.md). "
        "Aucun champ n’est une note de qualité."
    )
    lignes.append("")
    lignes.append(
        "Deux règles explicites servent au tri. La première reprend le domaine déclaré au "
        "catalogue : santé et sécurité, droit et démarches, argent et finances, politique "
        "publique et médias exigent une relecture par une personne compétente. La seconde "
        "signale des mots-clés présents dans les champs éditoriaux ; c’est une heuristique, "
        "qui peut manquer un sujet ou en signaler un par excès, et les termes trouvés sont "
        "affichés pour qu’une personne corrige le classement. Un prototype sans aucun "
        "signal reste un prototype à relire."
    )
    lignes.append("")
    lignes.append("## État")
    lignes.append("")
    lignes.append(ligne_tableau(["Indicateur", "Valeur"]))
    lignes.append(ligne_tableau(["---", "---"]))
    lignes.append(ligne_tableau(["Prototypes (statut « Prototype à relire »)", str(len(prototypes))]))
    lignes.append(
        ligne_tableau(
            ["Dont domaines à relecture spécialisée (règle 1)", f"{par_domaine_sensible}"]
        )
    )
    lignes.append(
        ligne_tableau(
            ["Dont hors domaines sensibles mais signalés par mots-clés (règle 2)", f"{signalees_hors_domaine}"]
        )
    )
    lignes.append(
        ligne_tableau(
            ["Sans aucun signal automatique", f"{len(prototypes) - par_domaine_sensible - signalees_hors_domaine}"]
        )
    )
    lignes.append(ligne_tableau(["Domaines concernés", str(len({item['fiche']['domaine'] for item in enrichis}))]))
    lignes.append("")

    lignes.append("## Répartition par domaine")
    lignes.append("")
    lignes.append(
        ligne_tableau(["Domaine", "Prototypes", "Relecture spécialisée", "Signalés par mots-clés"])
    )
    lignes.append(ligne_tableau(["---", "---:", "---:", "---:"]))
    par_domaine: dict[str, list[dict]] = {}
    for item in enrichis:
        par_domaine.setdefault(item["fiche"]["domaine"], []).append(item)
    for domaine, items in sorted(par_domaine.items(), key=lambda paire: (-len(paire[1]), paire[0])):
        lignes.append(
            ligne_tableau(
                [
                    titres.get(domaine, domaine),
                    str(len(items)),
                    str(sum(1 for i in items if i["famille"])),
                    str(sum(1 for i in items if not i["famille"] and i["motifs"])),
                ]
            )
        )
    lignes.append("")

    lignes.append("## Ordre proposé")
    lignes.append("")
    lignes.append(
        "Tri : domaines à relecture spécialisée d’abord, puis fiches signalées par mots-clés, "
        "puis celles à peu de sources déclarées, puis domaine et identifiant. Cet ordre est "
        "une proposition de travail, pas un jugement sur la difficulté ou la qualité."
    )
    lignes.append("")
    lignes.append(
        ligne_tableau(["#", "Fiche", "Domaine", "Repère", "Sources", "Relecture spécialisée", "Termes repérés"])
    )
    lignes.append(ligne_tableau(["---:", "---", "---", "---:", "---:", "---", "---"]))
    for index, item in enumerate(enrichis, start=1):
        fiche = item["fiche"]
        fiche_lien = f"[{fiche['titre']}](fiches/{fiche['id']}.html)"
        lignes.append(
            ligne_tableau(
                [
                    str(index),
                    fiche_lien,
                    titres.get(fiche["domaine"], fiche["domaine"]),
                    str(fiche.get("niveau", "")),
                    str(item["sources"]),
                    item["famille"] or "—",
                    " ; ".join(item["motifs"]) if item["motifs"] else "—",
                ]
            )
        )
    lignes.append("")

    lignes.append("## Ce que cette file ne remplace pas")
    lignes.append("")
    lignes.append("- L’examen du contenu par une personne compétente dans le domaine.")
    lignes.append("- Le contrôle des sources, de leur date, de leur périmètre et de leurs droits.")
    lignes.append("- Les essais avec des personnes apprenantes et la revue d’accessibilité humaine.")
    lignes.append("- La décision de publier, qui reste celle de l’association.")
    lignes.append("")
    lignes.append("Régénérer avec `python3 outils/file-relecture.py` ; vérifier avec `--verifier`.")
    lignes.append("")
    return "\n".join(lignes)


def main() -> int:
    parseur = argparse.ArgumentParser(description=__doc__)
    parseur.add_argument("--verifier", action="store_true", help="échouer si le fichier a divergé")
    parseur.add_argument("--sortie", type=Path, default=SORTIE, help="chemin du fichier produit")
    arguments = parseur.parse_args()

    fiches, titres = charger()
    contenu = construire(fiches, titres)
    sortie = arguments.sortie if arguments.sortie.is_absolute() else RACINE / arguments.sortie

    if arguments.verifier:
        if not sortie.exists():
            print(f"{sortie.relative_to(RACINE)} absent : lancez le script sans --verifier.", file=sys.stderr)
            return 1
        if sortie.read_text(encoding="utf-8") != contenu:
            print(
                f"{sortie.relative_to(RACINE)} a divergé du catalogue : régénérez-le.",
                file=sys.stderr,
            )
            return 1
        print(f"La file de relecture est à jour ({sortie.relative_to(RACINE)}).")
        return 0

    sortie.write_text(contenu, encoding="utf-8")
    print(f"{sortie.relative_to(RACINE)} écrit : {len(contenu)} caractères")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
