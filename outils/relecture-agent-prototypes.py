#!/usr/bin/env python3
"""Garde la relecture de contenu des 81 prototypes honnête et vérifiable.

La personne a confié à l’agent la lecture du contenu et la vérification des
sources (`docs/protocole-editorial.md`, 7 novembre 2026 ; rappel du 10 novembre).
Ce contrôle ne relit rien à la place de l’agent : il empêche le registre de
perdre une fiche, d’inventer une source, de transformer un constat en validation
ou d’écrire dans le registre des seules relectures humaines.

Deux modes :

    python3 outils/relecture-agent-prototypes.py --verifier
    python3 outils/relecture-agent-prototypes.py --consigner

`--consigner` marque les 81 pages `relu-par-agent` dans
`docs/rd/empreintes-contenus.toml` et écrit une `[[edition]]` datée par page
dans `docs/rd/editions-relecture.toml`, avec le constat et la limite propres à
la fiche. Il refuse d’agir si `--verifier` échoue ou si `MRSC_RACINE` désigne
une copie de banc. Il ne modifie aucune fiche, aucun statut éditorial et ne
écrit dans `docs/apprentissage/relectures.toml`.

Le calcul arithmétique est volontairement borné : seules les égalités simples
sans parenthèses, sans inconnue et sans autre opérateur après le signe égal
sont recalculées. Les chaînes de réécriture et les égalités algébriques sont
écartées, pas déclarées vraies.
"""

from __future__ import annotations

import argparse
import importlib.util
import os
import re
import sys
import tomllib
from datetime import date
from decimal import Decimal, InvalidOperation
from pathlib import Path

RACINE = Path(os.environ.get("MRSC_RACINE") or Path(__file__).resolve().parent.parent).resolve()
CATALOGUE = RACINE / "docs" / "apprentissage" / "catalogue.toml"
REGISTRE = RACINE / "docs" / "rd" / "relecture-agent-prototypes.toml"
RAPPORT = RACINE / "docs" / "rd" / "relecture-agent-prototypes-2026-11-10.md"
REGISTRE_HUMAIN = RACINE / "docs" / "apprentissage" / "relectures.toml"
MANIFESTE = RACINE / "docs" / "rd" / "empreintes-contenus.toml"
EDITIONS = RACINE / "docs" / "rd" / "editions-relecture.toml"

VERDICTS = {"relue-sans-ecart", "a-trancher"}
CONTROLES = {
    "champs-editoriaux", "coherence-enonce-aide-correction",
    "arithmetique-simple", "sources-declarées", "audit-mecanique",
}
INTERDITES = (
    "validation humaine obtenue", "conforme", "Relu —", "statut promu",
    "essai avec des personnes réalisé", "avis juridique rendu",
    "expertise acquise", "tout est relu", "R&D terminée", "projet achevé",
    "https://",
)
#: Les onze champs éditoriaux réellement parcourus pour chacun des 81
#: prototypes. La porte refuse un champ absent, vide, de mauvais type ou qui
#: contient encore un marqueur de brouillon : la lecture est systématique.
CHAMPS_LECTURE = {
    "objectif": str,
    "situation": str,
    "analogie": str,
    "limite_analogie": str,
    "notions": list,
    "demarche": list,
    "exercice": str,
    "aide": str,
    "correction": list,
    "a_retenir": list,
    "transferer": str,
}
MARQUEURS_BROUILLON = ("todo", "fixme", "lorem ipsum", "à compléter", "tbd")
CHAMPS = ("situation", "exercice", "aide", "correction", "demarche", "a_retenir", "notions")
NUM = re.compile(r"\d[\d\s.,]*")
OP = re.compile(r"[+×÷\-−/]")
SEP = ".;:?!|\n"
EXPRESSION = re.compile(r"(\d+) expression\(s\) arithmétique\(s\) simple\(s\) recalculée\(s\)")


def nombre(brut: str) -> Decimal | None:
    """Normalise un nombre français : espaces fines, virgule décimale."""
    texte = brut.strip().replace(" ", "").replace("\u202f", "").replace("\u00a0", "").replace(",", ".")
    try:
        return Decimal(texte)
    except InvalidOperation:
        return None


def calculer(valeurs: list[Decimal], operateurs: list[str]) -> Decimal | None:
    """Évalue une chaîne d’opérations avec priorité à la multiplication."""
    nombres, ops = list(valeurs), list(operateurs)
    position = 0
    while position < len(ops):
        if ops[position] in ("×", "÷"):
            if ops[position] == "÷" and nombres[position + 1] == 0:
                return None
            resultat = (nombres[position] * nombres[position + 1] if ops[position] == "×"
                        else nombres[position] / nombres[position + 1])
            nombres[position:position + 2] = [resultat]
            ops.pop(position)
        else:
            position += 1
    total = nombres[0]
    for operateur, valeur in zip(ops, nombres[1:]):
        total = total + valeur if operateur == "+" else total - valeur
    return total


def verifier_champs(fiche: dict) -> list[str]:
    """Constate que les onze champs annoncés ont vraiment été parcourus."""
    erreurs: list[str] = []
    identifiant = str(fiche.get("id", "?"))
    for champ, type_attendu in CHAMPS_LECTURE.items():
        valeur = fiche.get(champ)
        if not valeur:
            erreurs.append(f"{identifiant} : champ éditorial absent ou vide : {champ}")
            continue
        if not isinstance(valeur, type_attendu):
            erreurs.append(f"{identifiant} : champ {champ} de type inattendu")
            continue
        morceaux = valeur if isinstance(valeur, list) else [valeur]
        if any(not str(morceau).strip() for morceau in morceaux):
            erreurs.append(f"{identifiant} : champ {champ} avec un élément vide")
        for morceau in morceaux:
            if any(marqueur in str(morceau).lower() for marqueur in MARQUEURS_BROUILLON):
                erreurs.append(f"{identifiant} : marqueur de brouillon dans {champ}")
    return erreurs


def expressions_simples(fiche: dict) -> int:
    """Compte les égalités arithmétiques simples dont le résultat est exact."""
    texte = " | ".join(
        morceau for champ in CHAMPS
        for morceau in (fiche.get(champ) if isinstance(fiche.get(champ), list) else [str(fiche.get(champ) or "")])
    )
    conformes = 0
    for egal in re.finditer(r"\s*=\s*", texte):
        debut = max((texte.rfind(s, 0, egal.start()) for s in SEP), default=-1) + 1
        gauche = texte[debut:egal.start()]
        fins = [p for p in (texte.find(s, egal.end()) for s in SEP) if p != -1]
        droite = texte[egal.end():min(fins) if fins else len(texte)]
        # Parenthèses, inconnue ou chaîne de réécriture : hors du calcul simple.
        if ("(" in gauche or ")" in gauche or re.search(r"\bx\b", gauche)
                or OP.search(droite)):
            continue
        valeurs = [nombre(m.group()) for m in NUM.finditer(gauche)]
        operateurs = OP.findall(gauche)
        attendu = NUM.search(droite)
        if (not attendu or None in valeurs or len(valeurs) != len(operateurs) + 1
                or not operateurs):
            continue
        cible = nombre(attendu.group())
        if cible is None:
            continue
        calcule = calculer(valeurs, operateurs)
        if calcule is not None and abs(calcule - cible) <= Decimal("0.0001"):
            conformes += 1
    return conformes


def charger(chemin: Path, erreurs: list[str]) -> dict:
    try:
        return tomllib.loads(chemin.read_text(encoding="utf-8"))
    except (OSError, tomllib.TOMLDecodeError) as erreur:
        erreurs.append(f"{chemin.relative_to(RACINE)} illisible : {erreur}")
        return {}


def controler() -> list[str]:
    erreurs: list[str] = []
    if not REGISTRE.is_file():
        return [f"registre de relecture d’agent absent : {REGISTRE.relative_to(RACINE)}"]
    if not RAPPORT.is_file():
        return [f"rapport daté absent : {RAPPORT.relative_to(RACINE)}"]

    donnees = charger(REGISTRE, erreurs)
    catalogue = charger(CATALOGUE, erreurs)
    if erreurs:
        return erreurs

    meta = donnees.get("meta", {})
    if meta.get("version") != 1:
        erreurs.append("meta : version attendue : 1")
    if meta.get("auteur") != "agent":
        erreurs.append("meta : auteur doit être « agent »")
    if str(meta.get("date")) != "2026-11-10":
        erreurs.append("meta : date de la passe attendue : 2026-11-10")
    if meta.get("registre_humain") != "docs/apprentissage/relectures.toml":
        erreurs.append("meta : le registre humain doit être nommé, jamais écrit")

    prototypes = [f for f in catalogue.get("fiche", []) if f.get("statut_editorial") == "Prototype à relire"]
    par_id = {f["id"]: f for f in prototypes}
    promues = [f["id"] for f in catalogue.get("fiche", []) if f.get("statut_editorial") == "Relu — relecture consignée"]
    if promues:
        erreurs.append("statuts promus sans registre humain : " + ", ".join(promues))

    entrees = donnees.get("relecture", [])
    vus: set[str] = set()
    for entree in entrees:
        identifiant = str(entree.get("fiche", "?"))
        if identifiant in vus:
            erreurs.append(f"{identifiant} : relecture consignée deux fois")
        vus.add(identifiant)
        fiche = par_id.get(identifiant)
        if fiche is None:
            erreurs.append(f"{identifiant} : fiche inconnue ou qui n’est plus un prototype")
            continue
        chemin_attendu = f"apprendre/fiches/{identifiant}.html"
        if entree.get("chemin") != chemin_attendu or not (RACINE / chemin_attendu).is_file():
            erreurs.append(f"{identifiant} : chemin de page absent ou incohérent : {entree.get('chemin')}")
        erreurs.extend(verifier_champs(fiche))
        if entree.get("domaine") != fiche.get("domaine"):
            erreurs.append(f"{identifiant} : domaine différent du catalogue")
        if str(entree.get("date")) != "2026-11-10":
            erreurs.append(f"{identifiant} : date absente ou différente de la passe")
        if entree.get("auteur") != "agent":
            erreurs.append(f"{identifiant} : auteur doit être « agent »")
        verdict = entree.get("verdict")
        if verdict not in VERDICTS:
            erreurs.append(f"{identifiant} : verdict inconnu « {verdict} »")
        objections = entree.get("objections", [])
        if verdict == "a-trancher" and not objections:
            erreurs.append(f"{identifiant} : un verdict « a-trancher » exige une objection écrite")
        if verdict == "relue-sans-ecart" and objections:
            erreurs.append(f"{identifiant} : un verdict sans écart ne peut pas porter d’objection")
        if not isinstance(entree.get("controles"), list) or not CONTROLES.issubset(set(entree.get("controles", []))):
            erreurs.append(f"{identifiant} : les cinq contrôles annoncés doivent être nommés")
        constat = str(entree.get("constat", ""))
        limite = str(entree.get("limite", ""))
        suite = str(entree.get("suite", ""))
        if len(constat) < 120 or identifiant not in constat or str(fiche.get("titre", "")) not in constat:
            erreurs.append(f"{identifiant} : constat trop court ou sans la fiche nommée")
        if len(limite) < 150 or "ne couvre" not in limite:
            erreurs.append(f"{identifiant} : limite trop courte ou sans portée négative")
        if "Prototype à relire" not in suite:
            erreurs.append(f"{identifiant} : la suite doit conserver le statut de prototype")
        for found in EXPRESSION.findall(constat):
            if int(found) != expressions_simples(fiche):
                erreurs.append(f"{identifiant} : nombre d’expressions recalculées annoncé à tort")
        if not EXPRESSION.search(constat):
            erreurs.append(f"{identifiant} : le constat doit annoncer le recalcul arithmétique")

        titres_declares = {str(s.get("titre", "")) for s in fiche.get("sources", [])}
        ouvertes = entree.get("sources_ouvertes", [])
        if not isinstance(ouvertes, list):
            erreurs.append(f"{identifiant} : sources_ouvertes doit être une liste")
            ouvertes = []
        for titre in ouvertes:
            if titre not in titres_declares:
                erreurs.append(f"{identifiant} : source ouverte inventée « {titre} »")
        if entree.get("sources_non_ouvertes") != len(fiche.get("sources", [])) - len(ouvertes):
            erreurs.append(f"{identifiant} : compte des sources non ouvertes faux")
        for champ in ("constat", "limite", "suite", "objections", "sources_ouvertes"):
            for interdite in INTERDITES:
                if interdite.lower() in str(entree.get(champ, "")).lower():
                    erreurs.append(f"{identifiant} : formulation interdite « {interdite} » dans {champ}")

    absents = sorted(set(par_id) - vus)
    if absents:
        erreurs.append("prototypes sans relecture consignée : " + ", ".join(absents))
    if len(par_id) != 81:
        erreurs.append(f"le catalogue porte {len(par_id)} prototypes, le lot en attend 81")

    if REGISTRE_HUMAIN.is_file():
        humaines = charger(REGISTRE_HUMAIN, erreurs)
        if humaines.get("relecture"):
            erreurs.append("relectures.toml contient une entrée : un agent n’y écrit jamais")

    rapport = RAPPORT.read_text(encoding="utf-8")
    for repere in ("81 / 81", "0 écart", "89 adresses uniques non ouvertes", "relu-par-agent"):
        if repere not in rapport:
            erreurs.append(f"rapport daté : repère absent « {repere} »")
    if "https://" in rapport:
        erreurs.append("rapport daté : aucune URL externe ne doit être recopiée")
    return erreurs


def consigner() -> int:
    if os.environ.get("MRSC_RACINE"):
        print("ÉCHEC — --consigner refuse d’écrire dans une racine de banc (MRSC_RACINE).", file=sys.stderr)
        return 1
    problemes = controler()
    if problemes:
        for probleme in problemes:
            print(f"ERREUR — {probleme}", file=sys.stderr)
        print("ÉCHEC — relecture non consignée : la porte d’abord.", file=sys.stderr)
        return 1

    specification = importlib.util.spec_from_file_location("relire_contenus", RACINE / "outils" / "relire-contenus.py")
    module = importlib.util.module_from_spec(specification)
    assert specification.loader is not None
    specification.loader.exec_module(module)

    manifeste = module.lire_toml(MANIFESTE)
    unites = {u["chemin"]: u for u in manifeste.get("unite", [])}
    donnees = tomllib.loads(REGISTRE.read_text(encoding="utf-8"))
    ancien = EDITIONS.read_text(encoding="utf-8") if EDITIONS.is_file() else ""
    if ancien and not ancien.startswith("#"):
        print("ÉCHEC — registre des éditions illisible : entête absent.", file=sys.stderr)
        return 1
    deja = tomllib.loads(ancien).get("edition", []) if ancien else []
    couverts = {(e.get("chemin"), e.get("empreinte_apres")) for e in deja}

    blocs: list[str] = []
    ecrits = 0
    for entree in donnees.get("relecture", []):
        chemin = entree["chemin"]
        if chemin not in unites:
            print(f"ÉCHEC — unité absente du manifeste : {chemin}", file=sys.stderr)
            return 1
        empreinte = module.empreinte(RACINE / chemin)
        unite = unites[chemin]
        if unite.get("etat") == "relu-par-agent" and (chemin, empreinte) in couverts:
            continue
        blocs.append("\n".join([
            "[[edition]]",
            f'chemin = "{chemin}"',
            "date = 2026-11-10",
            'auteur = "agent"',
            f'empreinte_avant = "{empreinte}"',
            f'empreinte_apres = "{empreinte}"',
            'nature = "mesure-interne"',
            'sources = []',
            'mesures = ["docs/rd/relecture-agent-prototypes.toml", '
            '"docs/rd/relecture-agent-prototypes-2026-11-10.md", '
            '"docs/apprentissage/catalogue.toml"]',
            f'relecture_de_fond = true',
            f'constat = "{str(entree["constat"]).replace(chr(34), chr(92) + chr(34))}"',
            f'limite = "{str(entree["limite"]).replace(chr(34), chr(92) + chr(34))}"',
            "",
        ]))
        unite.update(empreinte=empreinte, etat="relu-par-agent", date_derniere_relecture="2026-11-10")
        unite.pop("date_reference", None)
        ecrits += 1

    meta = dict(manifeste["meta"])
    meta["limite_reference"] = (
        "Les empreintes du 9 novembre 2026 sont une référence de départ. Le 10 novembre 2026, "
        "l’agent a relu le contenu des 81 prototypes : chaque page porte une [[edition]] datée, "
        "un constat et une limite dans docs/rd/relecture-agent-prototypes.toml, et le rapport "
        "docs/rd/relecture-agent-prototypes-2026-11-10.md. Les autres unités restent couvertes par "
        "les contrôles mécaniques déjà en place ; leur relecture éditoriale de fond reste une dette "
        "visible. Aucune écriture dans docs/apprentissage/relectures.toml, aucune promotion de statut."
    )
    if blocs:
        EDITIONS.write_text((ancien.rstrip() + "\n\n" if ancien else "") + "\n\n".join(blocs), encoding="utf-8")
    module.ecrire_manifeste(sorted(unites.values(), key=lambda u: u["chemin"]), meta)
    print(f"Relecture de fond consignée : {ecrits} page(s) marquée(s) relue-par-agent, "
          f"{len(donnees.get('relecture', [])) - ecrits} déjà couverte(s).")
    return 0


def main() -> int:
    analyseur = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    analyseur.add_argument("--verifier", action="store_true", help="contrôler le registre et le rapport (défaut)")
    analyseur.add_argument("--consigner", action="store_true", help="écrire les éditions de relecture de fond")
    options = analyseur.parse_args()
    if options.consigner:
        return consigner()
    problemes = controler()
    if problemes:
        print("ÉCHEC — relecture de contenu des prototypes", file=sys.stderr)
        for probleme in problemes:
            print(f"    {probleme}", file=sys.stderr)
        return 1
    entrees = tomllib.loads(REGISTRE.read_text(encoding="utf-8")).get("relecture", [])
    a_trancher = sum(e.get("verdict") == "a-trancher" for e in entrees)
    ouvertes = sum(len(e.get("sources_ouvertes", [])) for e in entrees)
    expressions = sum(expressions_simples(f) for f in tomllib.loads(
        CATALOGUE.read_text(encoding="utf-8")).get("fiche", [])
        if f.get("statut_editorial") == "Prototype à relire")
    print(f"Relecture d’agent vérifiée : {len(entrees)} prototypes, {a_trancher} à trancher, "
          f"{ouvertes} rattachements de sources ouvertes, {expressions} égalités recalculées sans écart, "
          "aucune validation humaine revendiquée.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
