#!/usr/bin/env python3
"""Prépare les paquets de relecture des prototypes, sans relire à la place de personne.

Ce script ne relit rien, ne note rien et ne valide rien. Il rassemble, pour chaque
prototype du catalogue, ce qu'une personne doit avoir sous les yeux pour trancher :
le besoin déclaré, les sources réellement enregistrées avec leur licence et leur
date de contrôle, les limites que la fiche affirme déjà, et une trace de décision
à remplir.

Le tri reprend exactement les deux règles de `outils/file-relecture.py` — domaine
à relecture spécialisée, puis mots-clés repérés — importées du même module pour
qu'il n'existe pas deux classements différents. Un paquet détaillé est produit
pour les prototypes prioritaires ; les autres restent dans le tableau et peuvent
être demandés par `--fiche`.

Usage :
    python3 outils/construire-paquets-relecture.py             # écrit docs/apprentissage/paquets-relecture.md
    python3 outils/construire-paquets-relecture.py --verifier  # échoue si le fichier a divergé
    python3 outils/construire-paquets-relecture.py --fiche maths-budget   # affiche un paquet
    python3 outils/construire-paquets-relecture.py --sortie autre.md
"""

from __future__ import annotations

import argparse
import importlib.util
import os
import sys
import tomllib
from datetime import date
from pathlib import Path

#: Racine lue par l'outil. La surcharge sert au banc de mutation
#: (`outils/test_mutations_files_relecture.py`), qui ajoute une fiche au
#: catalogue ou le laisse diverger dans une copie du dépôt.
RACINE = Path(os.environ.get("MRSC_RACINE") or Path(__file__).resolve().parent.parent).resolve()
SORTIE = RACINE / "docs" / "apprentissage" / "paquets-relecture.md"
REGISTRE = RACINE / "docs" / "apprentissage" / "relectures.toml"


def charger_module_file_relecture():
    """Charge `outils/file-relecture.py` pour partager son tri, sans en recopier un second."""
    chemin = RACINE / "outils" / "file-relecture.py"
    specification = importlib.util.spec_from_file_location("file_relecture", chemin)
    module = importlib.util.module_from_spec(specification)
    specification.loader.exec_module(module)
    return module


def priorite(item: dict) -> tuple[int, str]:
    if item["famille"]:
        return 1, f"domaine à relecture spécialisée — {item['famille']}"
    if item["motifs"]:
        return 2, "hors domaine sensible, signalé par mots-clés"
    return 3, "aucun signal automatique : reste un prototype à relire"


def enrichir(module) -> tuple[list[dict], dict[str, str]]:
    fiches, titres = module.charger()
    elements = []
    for fiche in fiches:
        if not fiche.get("statut_editorial"):
            continue
        item = {
            "fiche": fiche,
            "famille": module.DOMAINES_SENSIBLES.get(fiche["domaine"]),
            "motifs": module.motifs(fiche),
            "sources": fiche.get("sources", []) or [],
        }
        item["rang"], item["motif_rang"] = priorite(item)
        elements.append(item)
    elements.sort(key=lambda item: (item["rang"], item["fiche"]["domaine"], item["fiche"]["id"]))
    return elements, titres


def ligne(cellules: list[str]) -> str:
    return "| " + " | ".join(cellules) + " |"


def charger_module_audit():
    """Charge `outils/auditer-prototypes.py` pour ne pas recopier ses contrôles ici."""
    chemin = RACINE / "outils" / "auditer-prototypes.py"
    specification = importlib.util.spec_from_file_location("audit_prototypes", chemin)
    module = importlib.util.module_from_spec(specification)
    specification.loader.exec_module(module)
    return module


def etats_automatiques() -> dict[str, str]:
    """Résumé, par fiche, des contrôles mécaniques déjà passés.

    Le détail vit dans `docs/apprentissage/audit-automatique.md` ; ici on
    reprend seulement le compte, pour qu'une personne voie d'un coup d'œil ce
    qui est déjà vérifié et ce qui reste de son ressort.
    """
    try:
        module = charger_module_audit()
        fiches, _, references = module.charger()
        audits = module.auditer(fiches, references, date.today())
    except Exception:  # noqa: BLE001 - un audit cassé ne doit pas casser les paquets
        return {}
    etats: dict[str, str] = {}
    for audit in audits:
        total = len(audit["resultats"])
        echecs = len(audit["echecs"])
        constats = len(audit.get("constats") or [])
        if echecs:
            detail = " ; ".join(echec["detail"] for echec in audit["echecs"])
            etats[audit["fiche"]["id"]] = f"{total - echecs - constats}/{total} — à corriger : {detail}"
        elif constats:
            detail = " ; ".join(constat["detail"] for constat in audit["constats"])
            etats[audit["fiche"]["id"]] = (
                f"{total - constats}/{total} — aucun défaut mécanique détecté ; "
                f"constat à trancher par une personne : {detail}"
            )
        else:
            etats[audit["fiche"]["id"]] = f"{total}/{total} — aucun défaut mécanique détecté"
    return etats


def dernieres_relectures() -> dict[str, dict]:
    """Dernière relecture consignée par fiche, lue dans le registre humain.

    Un registre absent ou vide n'est pas une erreur ici : le contrôle de
    cohérence appartient à `outils/registre-relecture.py`.
    """
    try:
        with REGISTRE.open("rb") as fichier:
            entrees = tomllib.load(fichier).get("relecture", [])
    except (OSError, tomllib.TOMLDecodeError):
        return {}
    dernieres: dict[str, dict] = {}
    for entree in entrees:
        if not isinstance(entree, dict):
            continue
        identifiant = entree.get("fiche")
        date_entree = entree.get("date")
        if not isinstance(identifiant, str) or date_entree is None:
            continue
        actuelle = dernieres.get(identifiant)
        if actuelle is None or str(date_entree) > str(actuelle.get("date")):
            dernieres[identifiant] = entree
    return dernieres


def paquet(item: dict, titres: dict[str, str], relecture: dict | None = None, automatiques: dict[str, str] | None = None) -> list[str]:
    automatiques = automatiques or {}
    fiche = item["fiche"]
    lignes = [
        f"### `{fiche['id']}` — {fiche['titre']}",
        "",
        ligne(["Élément", "Valeur"]),
        ligne(["---", "---"]),
        ligne(["Domaine", titres.get(fiche["domaine"], fiche["domaine"])]),
        ligne(["Repère de difficulté", str(fiche.get("niveau", ""))]),
        ligne(["Horizon du contenu", fiche.get("horizon_contenu", "—")]),
        ligne(["Priorité de tri", f"{item['rang']} — {item['motif_rang']}"]),
        ligne(["Termes repérés", " ; ".join(item["motifs"]) if item["motifs"] else "—"]),
        ligne(["Fiche publiée", f"[lire la fiche](fiches/{fiche['id']}.html)"]),
        ligne(["Contrôles automatiques", automatiques.get(fiche["id"], "non exécutés — voir [l'audit automatique](audit-automatique.md)")]),
        ligne(["Relecture consignée",
              f"{relecture.get('date')} — {relecture.get('verdict')}" if relecture else "aucune à ce jour"]),
        "",
        "**Sources enregistrées dans le catalogue**",
        "",
    ]
    if item["sources"]:
        lignes.append(ligne(["Source", "Licence déclarée", "Mode", "Droits contrôlés le"]))
        lignes.append(ligne(["---", "---", "---", "---"]))
        for source in item["sources"]:
            titre = source.get("titre", "sans titre")
            url = source.get("url", "")
            lignes.append(
                ligne(
                    [
                        f"[{titre}]({url})" if url else titre,
                        source.get("licence_source", "non déclarée"),
                        source.get("mode_utilisation", "non déclaré"),
                        source.get("droits_controles_le", "non déclaré"),
                    ]
                )
            )
        lignes.append("")
    else:
        lignes.append("Aucune source déclarée : le point bloquant est la documentation, pas la formulation.")
        lignes.append("")

    lignes.append("**Ce que la fiche dit déjà de ses limites**")
    lignes.append("")
    lignes.append(f"> {fiche.get('limite_analogie', 'Aucune limite d’analogie déclarée : à vérifier.')}")
    lignes.append("")
    lignes.append("**Points à trancher par une personne**")
    lignes.append("")
    if item["sources"]:
        non_verifiees = sum(
            1
            for source in item["sources"]
            if "non vérifiée" in str(source.get("licence_source", "")).casefold()
        )
        lignes.append(
            f"- [ ] Ouvrir les {len(item['sources'])} source(s) et vérifier que chacune étaye réellement l’affirmation citée."
        )
        if non_verifiees:
            lignes.append(
                f"- [ ] Trancher les droits : {non_verifiees} source(s) déclarent une licence « non vérifiée ». "
                "Référence factuelle ou reprise autorisée, la décision doit être écrite."
            )
    else:
        lignes.append("- [ ] Documenter au moins une source primaire, ou laisser la fiche en l’état sans prétendre couvrir le sujet.")
    lignes.append("- [ ] Vérifier l’exemple et la correction : aucun exemple ne doit induire en erreur si l’énoncé est mal lu.")
    lignes.append("- [ ] Vérifier l’accessibilité réelle (lecture d’écran, zoom, clavier) : les contrôles automatiques ne la remplacent pas.")
    if fiche["domaine"] in ("sante-securite-corps", "demarches-droits-travail", "economie-finances", "citoyennete-medias"):
        lignes.append(
            "- [ ] Faire relire par une personne compétente du domaine : la fiche ne doit contenir ni conseil personnalisé, ni procédure présentée comme universelle."
        )
    lignes.append("- [ ] Décider : conserver en prototype, corriger puis relire, ou retirer. Écrire la raison, pas une note.")
    lignes.append("")
    lignes.append("**Relecture à consigner dans `relectures.toml`**")
    lignes.append("")
    lignes.append("```toml")
    lignes.append("[[relecture]]")
    lignes.append(f'fiche = "{fiche["id"]}"')
    lignes.append("date = AAAA-MM-JJ")
    lignes.append('role = "expertise du domaine — préciser lequel"')
    lignes.append('perimetre = ["exemples et corrections", "sources et droits", "accessibilité"]')
    lignes.append('verdict = "conforme"          # conforme | a-corriger | insuffisant')
    lignes.append("sources_ouvertes = []")
    lignes.append("droits_verifies_le = AAAA-MM-JJ")
    lignes.append("objections = []")
    lignes.append("points_bloquants = []")
    lignes.append('suite = "ce qui est décidé ensuite, et par qui"')
    lignes.append("```")
    lignes.append("")
    lignes.append(
        "Puis `python3 outils/registre-relecture.py` : un verdict « conforme » exige que la fiche passe au "
        "statut « Relu — relecture consignée » ; un verdict « à corriger » laisse le prototype en place et "
        "exige une objection écrite. Aucun des deux n'autorise une publication : cette décision reste à l'association."
    )
    lignes.append("")
    return lignes


def construire(elements: list[dict], titres: dict[str, str], detail: int = 2, dernieres: dict[str, dict] | None = None, automatiques: dict[str, str] | None = None) -> str:
    dernieres = dernieres or {}
    automatiques = automatiques or {}
    par_rang = {rang: sum(1 for item in elements if item["rang"] == rang) for rang in (1, 2, 3)}
    retenus = [item for item in elements if item["rang"] <= detail]
    lignes: list[str] = []
    lignes.append("# Paquets de relecture des prototypes")
    lignes.append("")
    lignes.append(
        "**Document de travail généré.** Il rassemble ce qu’une personne doit avoir sous les yeux pour "
        "trancher un prototype : ses sources telles qu’elles sont enregistrées, les droits déclarés, les "
        "limites que la fiche affirme déjà, et une trace de décision à remplir. Il ne relit rien, ne note "
        "rien et ne valide rien : aucun champ n’est une évaluation."
    )
    lignes.append("")
    lignes.append(
        "Le tri reprend les deux règles de la [file de relecture](file-relecture.md) : domaine à relecture "
        "spécialisée, puis mots-clés repérés dans les champs éditoriaux. Ces signaux restent une "
        "heuristique, corrigeable par une personne."
    )
    lignes.append("")
    lignes.append("## 0. Comment enregistrer une relecture, en trois gestes")
    lignes.append("")
    lignes.append("1. Ouvrir le paquet de la fiche, lire ses sources et ses limites, puis trancher avec la [grille de relecture](grille-relecture.md).")
    lignes.append("2. Coller le bloc `[[relecture]]` du paquet à la fin de [`relectures.toml`](relectures.toml) et le compléter (date réelle, rôle, périmètre, verdict, objections).")
    lignes.append("3. Lancer `python3 outils/registre-relecture.py`. Le contrôle refuse une date future, un verdict inconnu, un verdict négatif sans objection, et tout statut du catalogue qui ne correspondrait pas au registre.")
    lignes.append("")
    lignes.append(
        "Un verdict « conforme » fait passer la fiche au statut « Relu — relecture consignée » — à condition de le faire "
        "dans `catalogue.toml`, sinon le contrôle échoue. Ni le script ni ce document ne relisent : ils enregistrent."
    )
    lignes.append("")
    lignes.append("## 1. Ordre de passage proposé")
    lignes.append("")
    lignes.append(ligne(["Priorité", "Signification", "Prototypes"]))
    lignes.append(ligne(["---:", "---", "---:"]))
    lignes.append(ligne(["1", "domaine exigeant une personne compétente du domaine", str(par_rang[1])]))
    lignes.append(ligne(["2", "hors domaine sensible, mais mots-clés à vérifier", str(par_rang[2])]))
    lignes.append(ligne(["3", "aucun signal automatique — reste à relire", str(par_rang[3])]))
    lignes.append(ligne(["", "**Total des prototypes**", f"**{len(elements)}**"]))
    lignes.append("")
    lignes.append(f"Les {len(retenus)} paquets détaillés ci-dessous couvrent les priorités 1 et 2. Les autres prototypes apparaissent dans le tableau et se détaillent avec `--fiche <identifiant>`.")
    lignes.append("")
    lignes.append("## 2. Tableau de suivi")
    lignes.append("")
    lignes.append(ligne(["#", "Fiche", "Domaine", "Priorité", "Sources", "Droits déclarés", "Revue prévue le", "Relecture consignée"]))
    lignes.append(ligne(["---:", "---", "---", "---:", "---:", "---", "---", "---"]))
    for index, item in enumerate(elements, start=1):
        fiche = item["fiche"]
        non_verifiees = sum(
            1 for source in item["sources"] if "non vérifiée" in str(source.get("licence_source", "")).casefold()
        )
        droits = f"{non_verifiees} non vérifiée(s)" if non_verifiees else "aucune à vérifier"
        lignes.append(
            ligne(
                [
                    str(index),
                    f"[{fiche['titre']}](fiches/{fiche['id']}.html)",
                    titres.get(fiche["domaine"], fiche["domaine"]),
                    str(item["rang"]),
                    str(len(item["sources"])),
                    droits,
                    str(fiche.get("revue_le", "—")),
                    (
                        f"{dernieres[fiche['id']].get('date')} — {dernieres[fiche['id']].get('verdict')}"
                        if fiche["id"] in dernieres
                        else "aucune"
                    ),
                ]
            )
        )
    lignes.append("")
    lignes.append("## 3. Paquets détaillés")
    lignes.append("")
    for item in retenus:
        lignes.extend(paquet(item, titres, dernieres.get(item["fiche"]["id"]), automatiques))
    lignes.append("## 4. Ce que ces paquets ne font pas")
    lignes.append("")
    lignes.append("- Ils ne remplacent ni la [grille de relecture](grille-relecture.md) ni l’expertise du domaine : les questions communes y restent.")
    lignes.append("- Ils ne vérifient aucun contenu de source et ne disent pas qu’une licence est valide ; ils montrent seulement ce qui est déclaré.")
    lignes.append("- Ils n’attribuent aucune note, aucun score et aucun ordre de valeur entre fiches.")
    lignes.append("- Ils n’autorisent aucune publication : la décision reste celle de l’association.")
    lignes.append("- Ils ne remplacent pas le registre : la seule trace opposable est l’entrée de `relectures.toml` vérifiée par `outils/registre-relecture.py`.")
    lignes.append("")
    lignes.append("Régénérer avec `python3 outils/construire-paquets-relecture.py` ; vérifier avec `--verifier`.")
    lignes.append("")
    return "\n".join(lignes)


def main() -> int:
    analyseur = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    analyseur.add_argument("--verifier", action="store_true", help="échouer si le fichier a divergé")
    analyseur.add_argument("--fiche", help="afficher le paquet détaillé d’une seule fiche")
    analyseur.add_argument("--sortie", type=Path, default=SORTIE, help="chemin du fichier produit")
    arguments = analyseur.parse_args()

    module = charger_module_file_relecture()
    elements, titres = enrichir(module)
    sortie = arguments.sortie if arguments.sortie.is_absolute() else RACINE / arguments.sortie

    if arguments.fiche:
        trouves = [item for item in elements if item["fiche"]["id"] == arguments.fiche]
        if not trouves:
            print(f"Fiche inconnue ou non prototype : {arguments.fiche}", file=sys.stderr)
            return 2
        print("\n".join(paquet(trouves[0], titres, dernieres_relectures().get(arguments.fiche), etats_automatiques())))
        return 0

    contenu = construire(elements, titres, dernieres=dernieres_relectures(), automatiques=etats_automatiques())
    if arguments.verifier:
        if not sortie.exists():
            print(f"{sortie.relative_to(RACINE)} absent : lancez le script sans --verifier.", file=sys.stderr)
            return 1
        if sortie.read_text(encoding="utf-8") != contenu:
            print(f"{sortie.relative_to(RACINE)} a divergé du catalogue : régénérez-le.", file=sys.stderr)
            return 1
        print(f"Les paquets de relecture sont à jour ({sortie.relative_to(RACINE)}).")
        return 0

    sortie.parent.mkdir(parents=True, exist_ok=True)
    sortie.write_text(contenu, encoding="utf-8")
    print(f"{sortie.relative_to(RACINE)} écrit : {len(contenu)} caractères")
    return 0


if __name__ == "__main__":
    sys.exit(main())
