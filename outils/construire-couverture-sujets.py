#!/usr/bin/env python3
"""Qualifie les manques du catalogue, sujet par sujet, sans juger les contenus.

La carte des lacunes (`docs/rd/carte-lacunes.md`) nomme les sujets sans fiche
et dit, d'elle-même, que « leur manque est à qualifier sujet par sujet » pour
les sujets `partiel`. Ce générateur fait ce travail mécanique : pour chacun des
sujets du référentiel, il relève le nombre de fiches, les repères de difficulté
couverts, le statut déclaré, l'existence d'une carte de sujet et l'exigence de
relecture spécialisée, puis il nomme les manques mesurables.

Il produit deux sorties, toutes deux relues par `--verifier` :

* `docs/rd/couverture-sujets.md` — la carte complète, générée ;
* un bloc délimité dans `docs/rd/prospective-lacunes-2027.md` — le relevé
  chiffré sur lequel la note prospective s'appuie. Un chiffre de prospective
  qui dérive du catalogue doit faire échouer une porte, pas rester une phrase
  datée que personne ne relit.

Ce que le générateur ne fait pas : il ne cherche aucune source, ne juge ni la
qualité ni l'exactitude d'une fiche, ne décide d'aucune priorité éditoriale et
ne remplace aucune relecture humaine. L'ordre de la « file de travail » est un
tri sur le nombre de manques mesurés, pas sur l'importance d'un domaine ou
d'une personne.

Usage :
    python3 outils/construire-couverture-sujets.py
    python3 outils/construire-couverture-sujets.py --verifier
"""

from __future__ import annotations

import argparse
import os
import re
import sys
import tomllib
from collections import Counter
from pathlib import Path

RACINE = Path(os.environ.get("MRSC_RACINE") or Path(__file__).resolve().parent.parent).resolve()

# Statuts éditoriaux : définitions partagées, jamais recopiées en chaîne locale.
sys.path.insert(0, str(Path(__file__).resolve().parent))
from statuts_editoriaux import est_prototype, est_relue  # noqa: E402

DATA = RACINE / "docs" / "apprentissage"
RD = RACINE / "docs" / "rd"
CATALOGUE = DATA / "catalogue.toml"
REFERENTIEL = DATA / "referentiel.toml"
RELECTURES = DATA / "relectures.toml"
PLAN = DATA / "plan-1000.toml"
PORTEFEUILLE = RD / "portefeuille.toml"
CARTE = RD / "couverture-sujets.md"
PROSPECTIVE = RD / "prospective-lacunes-2027.md"
DOSSIER_CARTES = RD

DEBUT = "<!-- DEBUT RELEVE COUVERTURE -->"
FIN = "<!-- FIN RELEVE COUVERTURE -->"
MOTIF_BLOC = re.compile(re.escape(DEBUT) + r".*?" + re.escape(FIN) + r"\n?", re.S)

#: Domaines dont les contenus exigent, selon AGENTS.md, une relecture par une
#: personne compétente avant diffusion publique.
DOMAINES_SENSIBLES = {
    "sante-securite-corps": "santé et sécurité",
    "demarches-droits-travail": "droit, démarches et travail",
    "economie-finances": "argent, budget et finances",
    "citoyennete-medias": "politique publique, médias et information",
}
STATUTS = ("actif", "partiel", "a-creer", "revue-experte")
STATUTS_AVEC_FICHE = ("actif", "partiel")
LIBELLES_MANQUES = {
    "aucune-fiche": "aucune fiche",
    "sans-carte-de-sujet": "sujet à créer sans carte de sujet",
    "une-seule-fiche": "une seule fiche",
    "aucun-repere-1": "aucun point d'entrée de repère 1",
    "aucun-repere-3-ou-4": "aucune fiche de repère 3 ou 4",
    "relecture-specialisee": "relecture spécialisée exigée",
}


def lire(chemin: Path) -> dict:
    with chemin.open("rb") as fichier:
        return tomllib.load(fichier)


def charger() -> tuple[list[dict], list[dict], dict, dict, str, int, int]:
    catalogue = lire(CATALOGUE)
    referentiel = lire(REFERENTIEL)
    relectures = lire(RELECTURES)
    plan = lire(PLAN)
    portefeuille = lire(PORTEFEUILLE)
    revue = str(portefeuille.get("meta", {}).get("derniere_revue", "date inconnue"))
    cible = int(plan.get("objectif_fiches", 0))
    nb_relectures = len(relectures.get("relecture", []))
    return catalogue["fiche"], referentiel["domaine"], plan, portefeuille, revue, cible, nb_relectures


def controler(fiches: list[dict], domaines: list[dict]) -> list[str]:
    """Intégrité minimale : une carte générée depuis des sources cassées mentirait."""
    erreurs: list[str] = []
    ids = [fiche.get("id", "") for fiche in fiches]
    doublons = [ident for ident, compte in Counter(ids).items() if compte > 1]
    if doublons:
        erreurs.append("identifiants de fiches dupliqués : " + ", ".join(doublons))
    par_id = {fiche["id"]: fiche for fiche in fiches if fiche.get("id")}
    sujets_vus: set[str] = set()
    utilises: set[str] = set()
    for domaine in domaines:
        for sujet in domaine.get("sujet", []):
            ident = sujet.get("id", "")
            if ident in sujets_vus:
                erreurs.append(f"sujet cartographié plusieurs fois : {ident}")
            sujets_vus.add(ident)
            statut = sujet.get("statut")
            if statut not in STATUTS:
                erreurs.append(f"statut inconnu pour {ident} : {statut}")
            references = sujet.get("fiches") or []
            if statut in STATUTS and bool(references) != (statut in STATUTS_AVEC_FICHE):
                erreurs.append(f"statut et fiches associés incohérents : {ident}")
            for reference in references:
                if reference not in par_id:
                    erreurs.append(f"fiche inconnue référencée par {ident} : {reference}")
                else:
                    utilises.add(reference)
    for fiche in fiches:
        ident = fiche.get("id", "")
        if fiche.get("niveau") not in (1, 2, 3, 4):
            erreurs.append(f"repère de difficulté hors 1–4 pour {ident} : {fiche.get('niveau')}")
        if ident not in utilises:
            erreurs.append(f"fiche non reliée à la cartographie : {ident}")
    return erreurs


def mesurer(fiches: list[dict], domaines: list[dict]) -> dict:
    par_id = {fiche["id"]: fiche for fiche in fiches}
    prototypes = sum(1 for fiche in fiches if est_prototype(fiche))
    relues = sum(1 for fiche in fiches if est_relue(fiche))
    niveaux = Counter(fiche["niveau"] for fiche in fiches)
    sujets: list[dict] = []
    for domaine in domaines:
        for sujet in domaine.get("sujet", []):
            references = sujet.get("fiches") or []
            liees = [par_id[ident] for ident in references if ident in par_id]
            repaires = sorted({fiche["niveau"] for fiche in liees})
            manques: list[str] = []
            if not liees:
                manques.append("aucune-fiche")
            if sujet.get("statut") in ("a-creer", "revue-experte") and not (
                DOSSIER_CARTES / f"sujet-{sujet['id']}.md"
            ).is_file():
                manques.append("sans-carte-de-sujet")
            if len(liees) == 1:
                manques.append("une-seule-fiche")
            if 1 not in repaires:
                manques.append("aucun-repere-1")
            if not any(niveau >= 3 for niveau in repaires):
                manques.append("aucun-repere-3-ou-4")
            if domaine["id"] in DOMAINES_SENSIBLES:
                manques.append("relecture-specialisee")
            sujets.append(
                {
                    "domaine": domaine["titre"],
                    "domaine_id": domaine["id"],
                    "id": sujet["id"],
                    "titre": sujet["titre"],
                    "statut": sujet.get("statut", "inconnu"),
                    "fiches": liees,
                    "repaires": repaires,
                    "manques": manques,
                }
            )
    return {
        "sujets": sujets,
        "fiches": fiches,
        "prototypes": prototypes,
        "relues": relues,
        "niveaux": niveaux,
        "par_domaine": {
            domaine["titre"]: [sujet for sujet in sujets if sujet["domaine_id"] == domaine["id"]]
            for domaine in domaines
        },
    }


def ligne(cellules: list[str]) -> str:
    return "| " + " | ".join(cellules) + " |"


def construire_carte(mesures: dict, revue: str, nb_relectures: int) -> str:
    sujets = mesures["sujets"]
    fiches = mesures["fiches"]
    niveaux = mesures["niveaux"]
    sans_fiche = [sujet for sujet in sujets if not sujet["fiches"]]
    une_fiche = [sujet for sujet in sujets if len(sujet["fiches"]) == 1]
    sans_repere_34 = [sujet for sujet in sujets if "aucun-repere-3-ou-4" in sujet["manques"]]
    sensibles = [sujet for sujet in sujets if "relecture-specialisee" in sujet["manques"]]
    compte_manques = Counter(manque for sujet in sujets for manque in sujet["manques"])
    texte: list[str] = [
        "# Couverture des sujets, qualifiée par le catalogue",
        "",
        "**Nature :** carte de travail générée depuis `docs/apprentissage/catalogue.toml`, "
        "`docs/apprentissage/referentiel.toml`, `docs/apprentissage/relectures.toml`, "
        "`docs/apprentissage/plan-1000.toml` et `docs/rd/portefeuille.toml`. Elle compte, "
        "elle ne lit pas les fiches : elle ne juge ni leur exactitude, ni leur clarté, ni "
        "leur accessibilité, et elle ne fournit aucune source externe.",
        "",
        f"**Date de référence :** celle de la revue de portefeuille, `{revue}`. "
        "Aucune date du jour n'entre dans ce document : seule une revue réellement "
        "consignée peut la faire changer.",
        "",
        "## 1. Mesures de couverture",
        "",
        ligne(["Mesure", "Valeur"]),
        ligne(["---", "---:"]),
        ligne(["Fiches du catalogue", str(len(fiches))]),
        ligne(["dont prototypes à relire", str(mesures["prototypes"])]),
        ligne(["dont fiches marquées relues", str(mesures["relues"])]),
        ligne(["Relectures humaines consignées", str(nb_relectures)]),
        ligne(["Domaines", str(len(mesures["par_domaine"]))]),
        ligne(["Sujets du référentiel", str(len(sujets))]),
        ligne(["Sujets sans aucune fiche", str(len(sans_fiche))]),
        ligne(["Sujets à une seule fiche", str(len(une_fiche))]),
        ligne(["Sujets sans fiche de repère 3 ou 4", str(len(sans_repere_34))]),
        ligne(["Sujets d'un domaine à relecture spécialisée", str(len(sensibles))]),
    ]
    for niveau in (1, 2, 3, 4):
        texte.append(ligne([f"Fiches de repère {niveau}", str(niveaux.get(niveau, 0))]))
    for manque, nombre in sorted(compte_manques.items(), key=lambda item: (-item[1], item[0])):
        texte.append(ligne([f"Sujets avec le manque `{manque}`", str(nombre)]))
    texte.extend(
        [
            "",
            "Le repère 4 (« Approfondir ») est le plus mince du corpus. Ce n'est pas un "
            "défaut en soi : c'est un fait mesuré, à rapprocher du cap indicatif de "
            "`docs/apprentissage/plan-1000.toml`, qui n'est ni une obligation ni une promesse.",
            "",
            "## 2. Répartition par domaine",
            "",
            ligne(["Domaine", "Sujets", "Fiches", "Repères couverts", "Sans fiche", "Une seule fiche", "Sans repère 3 ou 4"]),
            ligne(["---", "---:", "---:", "---", "---:", "---:", "---:"]),
        ]
    )
    for titre, bloc in mesures["par_domaine"].items():
        repaires = sorted({niveau for sujet in bloc for niveau in sujet["repaires"]})
        texte.append(
            ligne(
                [
                    titre,
                    str(len(bloc)),
                    str(sum(len(sujet["fiches"]) for sujet in bloc)),
                    ", ".join(str(niveau) for niveau in repaires) or "—",
                    str(sum(not sujet["fiches"] for sujet in bloc)),
                    str(sum(len(sujet["fiches"]) == 1 for sujet in bloc)),
                    str(sum("aucun-repere-3-ou-4" in sujet["manques"] for sujet in bloc)),
                ]
            )
        )
    texte.extend(
        [
            "",
            "## 3. Manques qualifiés, sujet par sujet",
            "",
            "Un manque est une case mesurable, pas un jugement de qualité. La colonne "
            "« Repères » donne les repères de difficulté réellement présents dans les "
            "fiches reliées au sujet.",
            "",
            ligne(["Domaine", "Sujet", "Statut", "Fiches", "Repères", "Manques mesurés"]),
            ligne(["---", "---", "---", "---:", "---", "---"]),
        ]
    )
    for sujet in sorted(sujets, key=lambda item: (item["domaine_id"], item["id"])):
        texte.append(
            ligne(
                [
                    sujet["domaine"],
                    f"`{sujet['id']}` — {sujet['titre']}",
                    f"`{sujet['statut']}`",
                    str(len(sujet["fiches"])),
                    ", ".join(str(niveau) for niveau in sujet["repaires"]) or "—",
                    ", ".join(f"`{manque}`" for manque in sujet["manques"]) or "—",
                ]
            )
        )
    texte.extend(
        [
            "",
            "## 4. File de travail : un tri, pas une priorité",
            "",
            "Les douze premières lignes du tri par **nombre de manques mesurés**, puis "
            "par identifiant pour rendre l'ordre stable. Ce tri ne dit pas qu'un domaine "
            "est plus important qu'un autre, ni qu'une personne devrait commencer par là : "
            "la décision éditoriale reste humaine.",
            "",
            ligne(["Sujet", "Manques", "Détail"]),
            ligne(["---", "---:", "---"]),
        ]
    )
    tries = sorted(sujets, key=lambda item: (-len(item["manques"]), item["id"]))[:12]
    for sujet in tries:
        texte.append(
            ligne(
                [
                    f"`{sujet['id']}` — {sujet['titre']}",
                    str(len(sujet["manques"])),
                    ", ".join(LIBELLES_MANQUES[manque] for manque in sujet["manques"]),
                ]
            )
        )
    texte.extend(
        [
            "",
            "## 5. Ce que cette carte ne dit pas",
            "",
            "- Elle ne dit pas qu'un sujet absent du référentiel n'existe pas : le référentiel est une carte de travail, pas un inventaire du savoir.",
            f"- Elle ne dit rien de la qualité des {len(fiches)} fiches publiées ni de l'exactitude de leur contenu.",
            "- Elle ne fournit aucune source : chaque sujet à documenter exige encore des sources primaires datées, avec leur périmètre et leurs droits.",
            "- Elle ne transforme aucun statut : un sujet `partiel` reste `partiel` même si une fiche de plus le rend moins mince. Elle ne peut pas davantage juger si un statut `actif` est mérité ; elle vérifie seulement qu'un changement de statut ne passe pas inaperçu.",
            "- Elle ne compte aucune relecture comme acquise : une fiche marquée « Prototype à relire » le reste tant qu'une personne n'a pas consigné sa revue.",
            "- Elle ne hiérarchise ni les domaines, ni les langues, ni les personnes : le tri de la section 4 porte sur des cases vides, pas sur des personnes.",
            "- Elle ne remplace ni `carte-lacunes.md` (qui nomme l'exigence de preuve des sujets sans fiche), ni `prospective-lacunes-2027.md` (qui discute trois scénarios sans les trancher).",
            "",
            "## 6. Entretenir cette carte",
            "",
            "Toute modification du catalogue, du référentiel, du registre des relectures "
            "ou du plan doit être suivie d'une régénération. La porte CI vérifie les deux "
            "sorties et plante des fautes dans une copie du dépôt pour prouver qu'elle "
            "refuse une carte périmée, une fiche non reliée et un relevé prospectif "
            "désynchronisé.",
            "",
            "Régénérer avec `python3 outils/construire-couverture-sujets.py` ; vérifier avec `--verifier`.",
            "",
        ]
    )
    return "\n".join(texte)


def construire_releve(mesures: dict, revue: str, cible: int, nb_relectures: int) -> str:
    """Bloc chiffré injecté dans la note prospective, entre deux bornes stables."""
    fiches = mesures["fiches"]
    sujets = mesures["sujets"]
    total = len(fiches)
    prototypes = mesures["prototypes"]
    sans_fiche = sum(not sujet["fiches"] for sujet in sujets)
    une_fiche = sum(len(sujet["fiches"]) == 1 for sujet in sujets)
    sans_repere_34 = sum("aucun-repere-3-ou-4" in sujet["manques"] for sujet in sujets)
    cartes_manquantes = sum("sans-carte-de-sujet" in sujet["manques"] for sujet in sujets)
    repere_4 = mesures["niveaux"].get(4, 0)
    manquant_cap = max(0, cible - total)
    lots_de_trois = -(-manquant_cap // 3)  # arrondi au lot entier supérieur
    dette_si_cap = prototypes + manquant_cap
    lignes = [
        DEBUT,
        "",
        f"Relevé généré depuis le catalogue, le référentiel, le registre des relectures et le plan indicatif. "
        f"Date de référence : revue de portefeuille du `{revue}`. Aucune donnée d'usage, aucune source externe, "
        "aucune projection de fréquentation.",
        "",
        ligne(["Mesure", "Valeur", "D'où vient le nombre"]),
        ligne(["---", "---:", "---"]),
        ligne(["Fiches du catalogue", str(total), "`catalogue.toml`"]),
        ligne(["Prototypes à relire", str(prototypes), "statut éditorial partagé"]),
        ligne(["Relectures humaines consignées", str(nb_relectures), "`relectures.toml`"]),
        ligne(["Sujets du référentiel", str(len(sujets)), "`referentiel.toml`"]),
        ligne(["Sujets sans aucune fiche", str(sans_fiche), "référentiel"]),
        ligne(["Sujets à une seule fiche", str(une_fiche), "référentiel × catalogue"]),
        ligne(["Sujets sans repère 3 ou 4", str(sans_repere_34), "référentiel × catalogue"]),
        ligne(["Sujets à créer sans carte de sujet", str(cartes_manquantes), "fichiers `sujet-*.md`"]),
        ligne(["Fiches de repère 4", str(repere_4), "`catalogue.toml`"]),
        ligne(["Cap indicatif de fiches", str(cible), "`plan-1000.toml`"]),
        ligne(["Écart arithmétique au cap", str(manquant_cap), "cap moins fiches"]),
        "",
        "### Trois conséquences arithmétiques, pas trois prévisions",
        "",
        ligne(["Scénario de calcul", "Ce que donne le relevé", "Ce que le calcul ne dit pas"]),
        ligne(["---", "---", "---"]),
        ligne(
            [
                "A — Tenir le cap du nombre",
                f"{manquant_cap} fiches manquantes ; à 3 fiches par lot, {lots_de_trois} lots ; "
                f"si chaque nouvelle fiche reste un prototype, {dette_si_cap} prototypes à relire.",
                "Ni le rythme réel, ni la disponibilité des relecteurs, ni l'utilité des fiches.",
            ]
        ),
        ligne(
            [
                "B — Relire d'abord",
                f"{prototypes} prototypes en attente pour {nb_relectures} relecture(s) consignée(s) ; "
                "le cap reste inchangé et aucune fiche nouvelle n'est nécessaire au calcul.",
                "Le temps nécessaire, la compétence requise par domaine ni l'ordre des fiches.",
            ]
        ),
        ligne(
            [
                "C — Combler les manques mesurés",
                f"{sans_fiche} sujets sans fiche, {une_fiche} sujets à une seule fiche, "
                f"{sans_repere_34} sujets sans repère 3 ou 4, {cartes_manquantes} carte(s) de sujet manquante(s).",
                "Qu'un sujet est plus important qu'un autre, ni qu'une fiche comble son manque.",
            ]
        ),
        "",
        "Ces trois lignes sont des conséquences des seuls nombres du dépôt. Aucune "
        "probabilité, aucune échéance et aucune recommandation ne s'en déduit ; "
        "l'arbitrage reste à l'association.",
        "",
        FIN,
        "",
    ]
    return "\n".join(lignes)


def verifier_et_ecrire(verifier: bool, contenu_carte: str, bloc: str) -> int:
    problemes: list[str] = []
    if not CARTE.is_file() or CARTE.read_text(encoding="utf-8") != contenu_carte:
        problemes.append(f"{CARTE.relative_to(RACINE)} a divergé du catalogue : régénérez-le.")
    if not PROSPECTIVE.is_file():
        problemes.append(f"{PROSPECTIVE.relative_to(RACINE)} absent.")
    else:
        note = PROSPECTIVE.read_text(encoding="utf-8")
        trouve = MOTIF_BLOC.search(note)
        if DEBUT not in note or FIN not in note or trouve is None:
            problemes.append("bornes du relevé prospectif absentes ou mal placées : impossible de vérifier les chiffres.")
        elif trouve.group(0) != bloc:
            problemes.append("le relevé prospectif a divergé du catalogue : régénérez-le.")
    if verifier:
        if problemes:
            for probleme in problemes:
                print(probleme, file=sys.stderr)
            return 1
        print("Couverture des sujets et relevé prospectif à jour.")
        return 0
    if not PROSPECTIVE.is_file():
        print(f"{PROSPECTIVE.relative_to(RACINE)} absent : créez la note avec les deux bornes.", file=sys.stderr)
        return 1
    note = PROSPECTIVE.read_text(encoding="utf-8")
    if DEBUT not in note or FIN not in note:
        print("bornes du relevé prospectif absentes : ajoutez-les avant de régénérer.", file=sys.stderr)
        return 1
    CARTE.write_text(contenu_carte, encoding="utf-8")
    PROSPECTIVE.write_text(MOTIF_BLOC.sub(lambda _: bloc, note, count=1), encoding="utf-8")
    print(f"{CARTE.relative_to(RACINE)} écrit et relevé prospectif synchronisé ({len(contenu_carte)} caractères).")
    return 0


def main() -> int:
    parseur = argparse.ArgumentParser(description=__doc__)
    parseur.add_argument("--verifier", action="store_true", help="échouer si une sortie a divergé")
    arguments = parseur.parse_args()
    fiches, domaines, _plan, _portefeuille, revue, cible, nb_relectures = charger()
    erreurs = controler(fiches, domaines)
    if erreurs:
        for erreur in erreurs:
            print(f"Source de vérité incohérente : {erreur}", file=sys.stderr)
        return 1
    mesures = mesurer(fiches, domaines)
    return verifier_et_ecrire(
        arguments.verifier,
        construire_carte(mesures, revue, nb_relectures),
        construire_releve(mesures, revue, cible, nb_relectures),
    )


if __name__ == "__main__":
    raise SystemExit(main())
