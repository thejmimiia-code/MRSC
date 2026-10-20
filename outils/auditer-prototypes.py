#!/usr/bin/env python3
"""Passe les contrôles mécaniques que l'on peut réellement automatiser sur chaque fiche.

Ce script ne relit **rien**. Il exécute une liste finie de vérifications qui ne
demandent aucun jugement : présence et forme des champs, HTTPS et métadonnées de
droits, dates de revue, cohérence avec le référentiel et la page générée,
doublons exacts, longueur des phrases, typographie. Il produit un constat par
fiche et par contrôle : `ok`, `a-corriger`, ou `non-automatisable` quand seul un
être humain peut trancher.

Le total « tout est vert » ne veut pas dire « fiche relue ». Il veut dire : rien
de mécaniquement faux n'a été détecté. La relecture humaine reste consignée
séparément, dans `docs/apprentissage/relectures.toml`
(`outils/registre-relecture.py`).

Usage :
    python3 outils/auditer-prototypes.py              # écrit docs/apprentissage/audit-automatique.md
    python3 outils/auditer-prototypes.py --verifier   # échoue si le fichier a divergé
    python3 outils/auditer-prototypes.py --fiche maths-budget
    python3 outils/auditer-prototypes.py --sortie autre.md
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

# Statuts éditoriaux : définitions partagées, jamais recopiées en chaîne locale.
sys.path.insert(0, str(RACINE / "outils"))
from statuts_editoriaux import PROTOTYPE, RELU, porte_un_statut  # noqa: E402

DATA = RACINE / "docs" / "apprentissage"
CATALOGUE = DATA / "catalogue.toml"
REFERENTIEL = DATA / "referentiel.toml"
PAGES = RACINE / "apprendre" / "fiches"
SORTIE = DATA / "audit-automatique.md"

CHAMPS_REQUIS = (
    "titre", "resume", "objectif", "situation", "analogie_titre", "analogie",
    "limite_analogie", "notions", "demarche", "exercice", "aide", "correction",
    "a_retenir", "transferer",
)
MODES = ("reference-factuelle", "reutilisation-sous-licence", "permission-expressee", "permission-expresse")
LONGUEUR_PHRASE_MAX = 45
LONGUEUR_LIMITE_MIN = 120

# Troisième état possible d'un contrôle : la machine constate un fait exact, mais
# ce fait n'est pas un défaut mécanique — elle ne peut pas décider s'il est
# acceptable. Ici : une fiche qui ne cite que des portails n'offre aucune page à
# confronter. Le fait se nomme, la décision revient à une personne.
ETAT_A_VERIFIER = "a-verifier"

# Les questions qu'aucun script ne peut trancher. Elles sont affichées telles
# quelles, à côté des contrôles automatiques, pour que la frontière soit lisible.
HUMAIN_ONLY = (
    "La source dit-elle réellement ce que la fiche affirme, dans sa version consultée ?",
    "Les exemples et corrections sont-ils exacts pour la variété, le niveau et le public visés ?",
    "Les droits permettent-ils ce qui est fait du document (citation, reprise, renvoi) ?",
    "L'analogie éclaire-t-elle sans stigmatiser ni induire en erreur ?",
    "Une personne réelle peut-elle s'en servir — au clavier, au lecteur d'écran, à fort zoom, sans audio ?",
    "L'association autorise-t-elle la publication, et sous quelle responsabilité éditoriale ?",
)


def ligne(cellules: list[str]) -> str:
    return "| " + " | ".join(cellules) + " |"


def charger() -> tuple[list[dict], dict[str, str], dict[str, list[str]]]:
    catalogue = tomllib.loads(CATALOGUE.read_text(encoding="utf-8"))
    referentiel = tomllib.loads(REFERENTIEL.read_text(encoding="utf-8"))
    titres: dict[str, str] = {}
    references: dict[str, list[str]] = {}
    for domaine in referentiel["domaine"]:
        titres[domaine["id"]] = domaine["titre"]
        for sujet in domaine.get("sujet", []):
            for identifiant in sujet.get("fiches", []) or []:
                references.setdefault(identifiant, []).append(domaine["id"])
    return catalogue["fiche"], titres, references


def controler(fiche: dict, fiches: dict[str, dict], references: dict[str, list[str]], aujourdhui: date) -> list[dict]:
    identifiant = fiche["id"]
    resultats: list[dict] = []

    def ajouter(cle: str, libelle: str, etat: str, detail: str = "") -> None:
        resultats.append({"cle": cle, "libelle": libelle, "etat": etat, "detail": detail})

    # 1. Champs obligatoires
    manquants = [
        champ for champ in CHAMPS_REQUIS
        if not fiche.get(champ) or (isinstance(fiche[champ], str) and not fiche[champ].strip())
    ]
    ajouter(
        "champs", "Tous les champs éditoriaux requis sont remplis",
        "a-corriger" if manquants else "ok",
        ", ".join(manquants) if manquants else f"{len(CHAMPS_REQUIS)} champs",
    )
    for champ in ("notions", "demarche", "correction", "a_retenir"):
        valeur = fiche.get(champ)
        if valeur is not None and (not isinstance(valeur, list) or not all(str(e).strip() for e in valeur)):
            ajouter("champs_listes", f"« {champ} » est une liste de textes non vides", "a-corriger", champ)

    # 2. Référencement dans le référentiel
    domaines = references.get(identifiant, [])
    ajouter(
        "referencement", "La fiche est reliée à un sujet de son domaine principal",
        "ok" if fiche.get("domaine") in domaines else "a-corriger",
        fiche.get("domaine") if fiche.get("domaine") in domaines else f"référencée sous : {', '.join(domaines) or 'aucun sujet'}",
    )

    # 3. Statut explicite et expliqué
    statut = fiche.get("statut_editorial")
    ajouter(
        "statut", "Un statut éditorial connu et une note existent",
        "ok" if porte_un_statut(fiche) and fiche.get("note_statut_editorial") else "a-corriger",
        statut or "aucun statut (corpus initial)",
    )

    # 4. Sources : présence et adresse
    sources = fiche.get("sources") or []
    adresses_fautives = []
    for source in sources:
        url = str(source.get("url", ""))
        if not url.startswith("https://") or "/" not in url[8:]:
            adresses_fautives.append(url or "sans URL")
    if not sources:
        ajouter("sources", "Au moins une source est déclarée et toutes sont en HTTPS", "a-corriger", "aucune source")
    else:
        ajouter(
            "sources", "Au moins une source est déclarée et toutes sont en HTTPS",
            "a-corriger" if adresses_fautives else "ok",
            ", ".join(adresses_fautives) if adresses_fautives else f"{len(sources)} source(s)",
        )

    # 5. Métadonnées de droits complètes et cohérentes
    droits_incomplets = []
    for source in sources:
        for champ in ("licence_source", "droits_controles_le", "mode_utilisation", "utilisation"):
            if not source.get(champ):
                droits_incomplets.append(f"{source.get('titre', 'source')} : {champ}")
        mode = source.get("mode_utilisation")
        if mode and mode not in MODES:
            droits_incomplets.append(f"{source.get('titre', 'source')} : mode inconnu « {mode} »")
        if mode == "reference-factuelle":
            utilisation = str(source.get("utilisation", "")).casefold()
            if not any(terme in utilisation for terme in ("aucun", "aucune", "sans reprise", "non reproduit", "pas repris")):
                droits_incomplets.append(f"{source.get('titre', 'source')} : reprise non écartée explicitement")
    non_verifiees = sum(1 for source in sources if "non vérifiée" in str(source.get("licence_source", "")).casefold())
    ajouter(
        "droits", "Les métadonnées de droits sont complètes et cohérentes",
        "a-corriger" if droits_incomplets else "ok",
        "; ".join(droits_incomplets) if droits_incomplets else f"{non_verifiees}/{len(sources)} licence(s) déclarée(s) non vérifiée(s)",
    )

    # 6. Dates de revue
    brute = fiche.get("revue_le")
    try:
        revue = brute if isinstance(brute, date) else date.fromisoformat(str(brute))
    except ValueError:
        revue = None
    intervalle = fiche.get("intervalle_revue_jours")
    souci = ""
    if revue is None:
        souci = "revue_le absente ou non datée"
    elif revue > aujourdhui:
        souci = "revue_le dans le futur"
    elif not isinstance(intervalle, int) or isinstance(intervalle, bool) or not 30 <= intervalle <= 365:
        souci = "intervalle de revue hors de 30–365 jours"
    if souci:
        ajouter("dates", "La date de revue est passée et l'intervalle tient entre 30 et 365 jours", "a-corriger", souci)
    else:
        prochaine = revue.toordinal() + intervalle
        ajouter(
            "dates", "La date de revue est passée et l'intervalle tient entre 30 et 365 jours", "ok",
            f"revue le {revue.isoformat()}, prochaine au {date.fromordinal(prochaine).isoformat()}",
        )

    # 7. Analogie et sa limite
    analogie = str(fiche.get("analogie", "")).strip()
    limite = str(fiche.get("limite_analogie", "")).strip()
    if not analogie or not limite:
        ajouter("analogie", "L'analogie est accompagnée d'une limite explicite", "a-corriger", "analogie ou limite vide")
    elif len(limite) < LONGUEUR_LIMITE_MIN:
        ajouter("analogie", "L'analogie est accompagnée d'une limite explicite", "a-corriger", f"limite trop courte ({len(limite)} caractères)")
    else:
        ajouter("analogie", "L'analogie est accompagnée d'une limite explicite", "ok", f"limite de {len(limite)} caractères")

    # 8. Exercice, aide et correction
    correction = fiche.get("correction") or []
    if not fiche.get("exercice") or not fiche.get("aide") or len(correction) < 2:
        ajouter("exercice", "L'exercice a une aide et une correction développée", "a-corriger", f"{len(correction)} élément(s) de correction")
    else:
        ajouter("exercice", "L'exercice a une aide et une correction développée", "ok", f"{len(correction)} éléments de correction")

    # 9. Doublons exacts entre fiches
    doublons = []
    for champ in ("titre", "resume", "analogie"):
        valeur = " ".join(str(fiche.get(champ, "")).split()).casefold()
        if not valeur:
            continue
        for autre_id, autre in fiches.items():
            if autre_id == identifiant:
                continue
            if " ".join(str(autre.get(champ, "")).split()).casefold() == valeur:
                doublons.append(f"{champ} identique à {autre_id}")
    ajouter(
        "doublons", "Aucun champ éditorial n'est copié d'une autre fiche", "a-corriger" if doublons else "ok",
        "; ".join(doublons) if doublons else "titre, résumé et analogie distincts",
    )

    # 10. Longueur des phrases des champs lus en continu
    textes = [str(fiche.get(champ, "")) for champ in ("resume", "objectif", "situation", "analogie", "exercice", "aide", "transferer")]
    textes += [str(element) for element in (fiche.get("demarche") or [])]
    phrases = [phrase.strip() for texte in textes for phrase in re.split(r"(?<=[.!?…])\s+", texte) if phrase.strip()]
    longueurs = [len(phrase.split()) for phrase in phrases]
    trop_longues = [phrase for phrase in phrases if len(phrase.split()) > LONGUEUR_PHRASE_MAX]
    ajouter(
        "phrases", f"Aucune phrase ne dépasse {LONGUEUR_PHRASE_MAX} mots",
        "a-corriger" if trop_longues else "ok",
        (f"{len(trop_longues)} phrase(s) trop longue(s), max {max(longueurs)} mots — « {trop_longues[0][:80]}… »")
        if trop_longues else f"{len(phrases)} phrase(s), max {max(longueurs) if longueurs else 0} mots",
    )

    # 11. Typographie française
    defauts = []
    tous_textes = list(textes) + [str(fiche.get(champ, "")) for champ in ("titre", "analogie_titre")]
    tous_textes += [str(element) for champ in ("notions", "correction", "a_retenir") for element in (fiche.get(champ) or [])]
    for texte in tous_textes:
        # « comme .pdf » est une extension citée, pas une faute de ponctuation : on
        # ne signale l'espace devant un point que s'il ne précède pas une extension.
        if re.search(r"\s+,", texte) or re.search(r"\s+\.(?!\w)", texte):
            defauts.append("espace avant une virgule ou un point")
        if "  " in texte:
            defauts.append("double espace")
        if '"' in texte:
            defauts.append("guillemet droit au lieu de « »")
    defauts = sorted(set(defauts))
    ajouter(
        "typographie", "La typographie française est homogène", "a-corriger" if defauts else "ok",
        "; ".join(defauts) if defauts else "espaces, guillemets et ponctuation conformes",
    )

    # 12. Identifiant et repères lisibles
    motif = re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)+", identifiant)
    ajouter(
        "identifiant", "L'identifiant est un slug stable en minuscules",
        "ok" if motif else "a-corriger", identifiant,
    )
    niveau = fiche.get("niveau")
    ajouter(
        "niveau", "Le repère de difficulté est l'un des quatre connus",
        "ok" if isinstance(niveau, int) and not isinstance(niveau, bool) and 1 <= niveau <= 4 else "a-corriger",
        str(niveau),
    )
    titre = str(fiche.get("titre", ""))
    resume_texte = str(fiche.get("resume", ""))
    soucis_longueur = []
    if len(titre) > 90:
        soucis_longueur.append(f"titre de {len(titre)} caractères")
    if len(resume_texte) > 200:
        soucis_longueur.append(f"résumé de {len(resume_texte)} caractères")
    ajouter(
        "longueurs", "Le titre tient en 90 caractères et le résumé en 200",
        "a-corriger" if soucis_longueur else "ok",
        " ; ".join(soucis_longueur) if soucis_longueur else f"titre {len(titre)}, résumé {len(resume_texte)}",
    )

    # 13. Sources uniques et dates de droits
    urls = [str(source.get("url", "")).strip() for source in sources]
    doublons_urls = sorted({url for url in urls if urls.count(url) > 1})
    dates_fautives = []
    for source in sources:
        brute_droits = source.get("droits_controles_le")
        try:
            droits = brute_droits if isinstance(brute_droits, date) else date.fromisoformat(str(brute_droits))
        except ValueError:
            dates_fautives.append(f"{source.get('titre', 'source')} : date de droits illisible")
            continue
        if droits > aujourdhui:
            dates_fautives.append(f"{source.get('titre', 'source')} : contrôle des droits dans le futur")
    problemes = [f"URL déclarée deux fois : {url}" for url in doublons_urls] + dates_fautives
    ajouter(
        "sources_dates", "Aucune source n'est déclarée deux fois et les dates de droits sont réelles",
        "a-corriger" if problemes else "ok",
        " ; ".join(problemes) if problemes else f"{len(sources)} source(s), dates de contrôle au plus tard le {aujourdhui.isoformat()}",
    )

    # 14. Sources confrontables : une page d'accueil ne permet de vérifier aucune
    # affirmation. Citer un portail n'est pas une faute — beaucoup de fiches
    # l'assument et l'écrivent — mais il n'y a alors rien à confronter : le fait
    # est nommé, la décision (garder le portail ou viser une page) revient à une
    # personne. C'est donc un constat, pas un échec mécanique.
    portails = []
    for source in sources:
        adresse = urlparse(str(source.get("url", "")))
        if adresse.path in ("", "/"):
            portails.append(source)
    if not sources:
        ajouter(
            "precision",
            "Au moins une source pointe une page précise, pas seulement un portail",
            ETAT_A_VERIFIER,
            "aucune source déclarée : rien à confronter",
        )
    elif len(portails) < len(sources):
        ajouter(
            "precision",
            "Au moins une source pointe une page précise, pas seulement un portail",
            "ok",
            f"{len(sources) - len(portails)}/{len(sources)} source(s) précise(s)",
        )
    else:
        ajouter(
            "precision",
            "Au moins une source pointe une page précise, pas seulement un portail",
            ETAT_A_VERIFIER,
            f"{len(portails)} portail(s) seulement : rien à confronter, à trancher par une personne",
        )

    # 15. Page publiée
    page = PAGES / f"{identifiant}.html"
    if not page.is_file():
        ajouter("page", "La page générée existe et affiche le statut", "a-corriger", "page absente")
    else:
        contenu = page.read_text(encoding="utf-8")
        titre = str(fiche.get("titre", ""))
        present = titre in contenu and (not statut or statut in contenu)
        ajouter(
            "page", "La page générée existe et affiche le statut", "ok" if present else "a-corriger",
            f"{page.stat().st_size // 1024} Kio, titre et statut présents" if present else "titre ou statut absent de la page",
        )

    return resultats


def auditer(fiches: list[dict], references: dict[str, list[str]], aujourdhui: date, seulement_prototypes: bool = True) -> list[dict]:
    par_id = {fiche["id"]: fiche for fiche in fiches}
    audits = []
    for fiche in fiches:
        if seulement_prototypes and fiche.get("statut_editorial") != PROTOTYPE:
            continue
        resultats = controler(fiche, par_id, references, aujourdhui)
        echecs = [resultat for resultat in resultats if resultat["etat"] == "a-corriger"]
        constats = [resultat for resultat in resultats if resultat["etat"] == ETAT_A_VERIFIER]
        audits.append({"fiche": fiche, "resultats": resultats, "echecs": echecs, "constats": constats})
    audits.sort(key=lambda audit: (-len(audit["echecs"]), audit["fiche"]["domain" if False else "domaine"], audit["fiche"]["id"]))
    return audits


def resume(audits: list[dict]) -> dict[str, int]:
    return {
        "fiches": len(audits),
        "controles": len(audits[0]["resultats"]) if audits else 0,
        "sans_echec": sum(1 for audit in audits if not audit["echecs"]),
        "avec_echec": sum(1 for audit in audits if audit["echecs"]),
        "echecs": sum(len(audit["echecs"]) for audit in audits),
        "fiches_a_verifier": sum(1 for audit in audits if audit["constats"]),
        "constats": sum(len(audit["constats"]) for audit in audits),
    }


def construire(audits: list[dict], titres: dict[str, str], aujourdhui: date) -> str:
    chiffres = resume(audits)
    lignes: list[str] = [
        "# Audit automatique des prototypes",
        "",
        "**Document de travail généré.** Il exécute, fiche par fiche, les contrôles qu'un programme peut "
        "réellement trancher : présence et forme des champs, adresses et métadonnées de droits, dates de revue, "
        "référencement, doublons exacts, longueur des phrases, typographie, page générée, existence d'une page "
        "de source précise. Il ne lit aucune source, ne juge aucune formulation et ne relit rien.",
        "",
        "**Ce que veut dire « tout est vert » :** aucun défaut mécaniquement détectable n'a été trouvé. "
        "Ce n'est ni une relecture, ni une validation, ni une autorisation de publication. La relecture humaine "
        "se consigne dans [`relectures.toml`](relectures.toml) et se contrôle avec `python3 outils/registre-relecture.py`.",
        "",
        "**Trois états, pas deux.** Un contrôle est `ok`, `à corriger` — le fait est faux et réparable sans "
        "jugement — ou `constat` : la machine voit un fait exact, mais elle ne peut pas dire s'il est "
        "acceptable. Un constat n'est pas un défaut : il se nomme ici pour qu'une personne tranche, et il "
        "n'empêche pas la page publique de dire la vérité, à condition qu'elle le dise.",
        "",
        f"**Date de l'audit :** {aujourdhui.isoformat()}.",
        "",
        "## 1. État d'ensemble",
        "",
        ligne(["Mesure", "Valeur"]),
        ligne(["---", "---:"]),
        ligne(["Prototypes audités", str(chiffres["fiches"])]),
        ligne(["Contrôles automatiques par fiche", str(chiffres["controles"])]),
        ligne(["Fiches sans aucun échec mécanique", str(chiffres["sans_echec"])]),
        ligne(["Fiches avec au moins un échec", str(chiffres["avec_echec"])]),
        ligne(["Échecs mécaniques au total", str(chiffres["echecs"])]),
        ligne(["Fiches avec un constat à trancher par une personne", str(chiffres["fiches_a_verifier"])]),
        ligne(["Constats nommés (ni échecs, ni validations)", str(chiffres["constats"])]),
        "",
    ]
    if chiffres["echecs"]:
        par_controle: dict[str, list[str]] = {}
        for audit in audits:
            for echec in audit["echecs"]:
                par_controle.setdefault(echec["libelle"], []).append(audit["fiche"]["id"])
        lignes.append("### Échecs par contrôle")
        lignes.append("")
        lignes.append(ligne(["Contrôle", "Fiches concernées", "Nombre"]))
        lignes.append(ligne(["---", "---", "---:"]))
        for libelle, concernées in sorted(par_controle.items(), key=lambda paire: -len(paire[1])):
            lignes.append(ligne([libelle, ", ".join(sorted(concernées)), str(len(concernées))]))
        lignes.append("")

    if chiffres["constats"]:
        par_constat: dict[str, list[str]] = {}
        for audit in audits:
            for constat in audit["constats"]:
                par_constat.setdefault(constat["libelle"], []).append(audit["fiche"]["id"])
        lignes.append("### Constats nommés, à trancher par une personne")
        lignes.append("")
        lignes.append(
            "Ces contrôles ont vu un fait exact que la machine ne peut pas juger. Rien n'est cassé : "
            "la fiche dit ce qu'elle fait, et une personne doit décider si cela suffit."
        )
        lignes.append("")
        lignes.append(ligne(["Constat", "Fiches concernées", "Nombre"]))
        lignes.append(ligne(["---", "---", "---:"]))
        for libelle, concernees in sorted(par_constat.items(), key=lambda paire: -len(paire[1])):
            lignes.append(ligne([libelle, ", ".join(sorted(concernees)), str(len(concernees))]))
        lignes.append("")
        lignes.append(
            "Pour la ligne « page précise » : ces fiches ne citent que des portails (racine d'un site). "
            "Elles déclarent souvent ce choix dans `utilisation`. Sans page précise, la question 1 du §4 "
            "ne peut pas être tranchée en l'état : il faut soit ajouter une page consultée et vérifiée, "
            "soit assumer le portail par écrit dans la fiche."
        )
        lignes.append("")

    lignes.append("## 2. Ce que la machine a vu, sans le juger")
    lignes.append("")
    sources_totales = sum(len(audit["fiche"].get("sources") or []) for audit in audits)
    licences_non_verifiees = sum(
        1
        for audit in audits
        for source in (audit["fiche"].get("sources") or [])
        if "non vérifiée" in str(source.get("licence_source", "")).casefold()
    )
    fiches_sans_source = [audit["fiche"]["id"] for audit in audits if not audit["fiche"].get("sources")]
    echeances = []
    for audit in audits:
        brute = audit["fiche"].get("revue_le")
        try:
            revue = brute if isinstance(brute, date) else date.fromisoformat(str(brute))
        except ValueError:
            continue
        intervalle = audit["fiche"].get("intervalle_revue_jours")
        if isinstance(intervalle, int) and not isinstance(intervalle, bool):
            echeances.append((date.fromordinal(revue.toordinal() + intervalle), audit["fiche"]["id"]))
    echeances.sort()
    lignes.append(ligne(["Fait mesuré", "Valeur"]))
    lignes.append(ligne(["---", "---:"]))
    lignes.append(ligne(["Sources déclarées au total", str(sources_totales)]))
    lignes.append(ligne(["dont licence déclarée « non vérifiée »", str(licences_non_verifiees)]))
    lignes.append(ligne(["Fiches sans aucune source", str(len(fiches_sans_source))]))
    if echeances:
        lignes.append(ligne(["Prochaine revue la plus proche", f"{echeances[0][0].isoformat()} ({echeances[0][1]})"]))
        lignes.append(ligne(["Fiches dont la revue de contenu est échue", str(sum(1 for echeance, _ in echeances if echeance < aujourdhui))]))
    lignes.append("")
    lignes.append(
        "Ces nombres ne disent rien de la qualité d'une fiche. Ils disent ce qui est **déjà fait** et ce qui "
        "**reste à faire par une personne** : ouvrir les sources, vérifier les exemples, trancher les droits, "
        "éprouver l'analogie et l'usage réel."
    )
    lignes.append("")
    lignes.append("## 3. Détail par fiche")
    lignes.append("")
    lignes.append(ligne(["Fiche", "Domaine", "Contrôles passés", "À corriger", "Constats", "Détail des échecs et des constats"]))
    lignes.append(ligne(["---", "---", "---:", "---:", "---:", "---"]))
    for audit in audits:
        fiche = audit["fiche"]
        total = len(audit["resultats"])
        details = [f"à corriger : {echec['libelle']} ({echec['detail']})" for echec in audit["echecs"]]
        details += [f"constat : {constat['libelle']} ({constat['detail']})" for constat in audit["constats"]]
        lignes.append(
            ligne([
                f"[{fiche['titre']}](fiches/{fiche['id']}.html)",
                titres.get(fiche["domaine"], fiche["domaine"]),
                str(total - len(audit["echecs"]) - len(audit["constats"])),
                str(len(audit["echecs"])),
                str(len(audit["constats"])),
                " ; ".join(details) or "—",
            ])
        )
    lignes.append("")

    lignes.append("## 4. Ce qu'aucun script ne peut faire")
    lignes.append("")
    lignes.append("Ces questions restent entières, même quand tous les contrôles ci-dessus sont verts :")
    lignes.append("")
    for question in HUMAIN_ONLY:
        lignes.append(f"- {question}")
    lignes.append("")
    lignes.append(
        "Quand un constat « page précise » figure ci-dessus, la première de ces questions ne peut pas être "
        "tranchée : il n'y a pas de page à confronter. Le portail peut rester, mais alors la fiche l'assume "
        "par écrit, et cette limite se dit dans la page publique."
    )
    lignes.append("")
    lignes.append("## 5. Comment s'en servir")
    lignes.append("")
    lignes.append("1. Corriger d'abord les échecs mécaniques : ils sont objectifs et souvent automatiques à réparer.")
    lignes.append("2. Trancher les constats : soit ajouter une page précise réellement consultée, soit assumer le portail par écrit dans la fiche. Un constat ne bloque pas, mais il ne s'efface pas tout seul.")
    lignes.append("3. Une fois une fiche sans échec, ouvrir son paquet de relecture (`python3 outils/construire-paquets-relecture.py --fiche <identifiant>`) : il ne reste que les questions du §4.")
    lignes.append("4. Consigner la relecture humaine dans `relectures.toml` (`--modele`), puis lancer `python3 outils/registre-relecture.py`.")
    lignes.append("")
    lignes.append("Régénérer avec `python3 outils/auditer-prototypes.py` ; vérifier avec `--verifier`.")
    lignes.append("")
    return "\n".join(lignes)


def main() -> int:
    analyseur = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    analyseur.add_argument("--verifier", action="store_true", help="échouer si le fichier a divergé")
    analyseur.add_argument("--fiche", help="n'afficher que le constat d'une fiche")
    analyseur.add_argument("--sortie", type=Path, default=SORTIE, help="chemin du fichier produit")
    analysis = analyseur.parse_args()

    try:
        fiches, titres, references = charger()
    except (OSError, KeyError, tomllib.TOMLDecodeError) as erreur:
        print(f"Catalogue ou référentiel illisible : {erreur}", file=sys.stderr)
        return 2

    aujourdhui = date.today()
    audits = auditer(fiches, references, aujourdhui)

    if analysis.fiche:
        trouves = [audit for audit in audits if audit["fiche"]["id"] == analysis.fiche]
        if not trouves:
            print(f"Fiche inconnue ou non prototype : {analysis.fiche}", file=sys.stderr)
            return 2
        audit = trouves[0]
        print(f"# {audit['fiche']['id']} — {audit['fiche']['titre']}")
        for resultat in audit["resultats"]:
            marque = {
                "ok": "OK  ",
                "a-corriger": "À CORRIGER",
                ETAT_A_VERIFIER: "CONSTAT",
            }.get(resultat["etat"], resultat["etat"].upper())
            print(f"{marque:11} {resultat['libelle']} — {resultat['detail']}")
        print(f"\nReste à trancher par une personne : {len(HUMAIN_ONLY)} questions (voir l'audit complet).")
        return 0

    contenu = construire(audits, titres, aujourdhui)
    sortie = analysis.sortie if analysis.sortie.is_absolute() else RACINE / analysis.sortie
    # Une sortie écrite hors du dépôt (--sortie /tmp/…) reste un cas normal.
    nom_sortie = str(sortie.relative_to(RACINE)) if sortie.is_relative_to(RACINE) else str(sortie)
    if analysis.verifier:
        if not sortie.exists():
            print(f"{nom_sortie} absent : lancez le script sans --verifier.", file=sys.stderr)
            return 1
        if sortie.read_text(encoding="utf-8") != contenu:
            print(f"{nom_sortie} a divergé du catalogue : régénérez-le.", file=sys.stderr)
            return 1
        chiffres = resume(audits)
        print(
            f"L'audit automatique est à jour ({nom_sortie}) : "
            f"{chiffres['fiches']} prototypes, {chiffres['sans_echec']} sans échec mécanique, "
            f"{chiffres['echecs']} échec(s), {chiffres['constats']} constat(s) à trancher."
        )
        return 0

    sortie.parent.mkdir(parents=True, exist_ok=True)
    sortie.write_text(contenu, encoding="utf-8")
    chiffres = resume(audits)
    print(
        f"{nom_sortie} écrit : {len(contenu)} caractères — "
        f"{chiffres['fiches']} prototypes, {chiffres['sans_echec']} sans échec, {chiffres['echecs']} échec(s)."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
