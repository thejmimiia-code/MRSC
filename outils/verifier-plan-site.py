#!/usr/bin/env python3
"""Vérifie le plan complet du site et la refonte de la page d’accueil.

Le 11 novembre 2026, la personne a signalé que l’accueil « rabâchait
différemment » les mêmes choses à plusieurs reprises. Ce contrôle ne juge ni
le ton, ni le rendu, ni la compréhension réelle : il **compte** les reprises
dans `index.html`, vérifie que chaque information a une place, que l’ordre des
sections suit la logique du visiteur, que les quatre portes de l’orienteur
mènent à leur destination et qu’aucune classe CSS n’a été perdue.

Les seuils viennent de `docs/rd/plan-site-complet-2026-11-11.toml`, mais les
occurrences sont recalculées ici à chaque lancement : un seuil écrit ne suffit
pas, c’est la page qui fait foi. La racine peut être surchargée par
`MRSC_RACINE` pour le banc de mutation.

Usage :
    python3 outils/verifier-plan-site.py
"""

from __future__ import annotations

import os
import re
import sys
import tomllib
from pathlib import Path

RACINE = Path(os.environ.get("MRSC_RACINE") or Path(__file__).resolve().parent.parent).resolve()
ACCUEIL = RACINE / "index.html"
MATRICE = RACINE / "docs" / "rd" / "plan-site-complet-2026-11-11.toml"
PLAN = RACINE / "docs" / "rd" / "plan-site-complet-2026-11-11.md"
RELECTURES = RACINE / "docs" / "apprentissage" / "relectures.toml"

SECTIONS_PLAN = (
    "## 1. Demande et méthode",
    "## 2. Plan complet du site",
    "## 3. Audit des redondances de l’accueil",
    "## 4. Brainstorming : trois options",
    "## 5. Structure retenue, section par section",
    "## 6. Où cliquer : la carte des destinations",
    "## 7. Ce qui a réellement changé",
    "## 8. Limites, contrôles et prochaine action",
)

ANCRE_OBLIGATOIRES = ("contenu", "mission", "actions", "rd-eva", "rejoindre",
                      "home-title", "home-entry-title", "home-hero-facts")
ORDRE_ATTENDU = ("mission", "actions", "rd-eva", "rejoindre")
PAGES_OBLIGATOIRES = ("index.html", "apprendre.html", "simulateur.html",
                      "documents.html", "transparence.html", "nous-contacter.html")

#: Repères exigés par les autres gardes du dépôt : cette porte les nomme pour
#: qu’une future refonte ne les efface pas sans le dire.
REPERES_ACCUEIL = (
    "trois ressources consultables sans compte",
    "Chaque page indique ses sources, ses limites et son statut",
    "Le simulateur ne prédit rien",
    "Nos expériences ont quelque chose à apporter.",
    "ÉVA signifie « Entité Virtuelle Autonome »",
    "Recherche en cours",
    "Matériel et financements nécessaires.",
    "Le budget et les besoins précis restent à définir",
    "proposition de présentation (à relire)",
    'href="documents.html">Découvrir l’association</a>',
    'href="#actions">Explorer les ressources</a>',
    'rel="describedby" href="llms.txt"',
    'data-share-site', 'data-share-fallback',
    'class="trace-list"', 'trace-panel',
    '<dl class="home-hero-facts">',
)

INTERDITES = re.compile(
    r"(?i)\b(?:R&D terminée|validation humaine obtenue|page validée|"
    r"tout est relu|rendu professionnel|projet achevé)\b"
)
SCHEMES = ("http" + "://", "https" + "://")
APOSTROPHE = re.compile(r"\b\w'\w")
CHEMIN = re.compile(
    r"`((?:docs|outils|assets|apprendre|simulateur|api|\.github)/[^`]+?\."
    r"(?:md|toml|py|js|cjs|mjs|html|css|json|dot|yml|yaml|txt|xml|sh|pdf))`"
)
MOTIF_MAIN = re.compile(r'<main id="contenu">.*?\n  </main>', re.S)
MOTIF_SECTION = re.compile(r"<section\b[^>]*>(.*?)</section>", re.S)
MOTIF_LI = re.compile(r"<li\b[^>]*>(.*?)</li>", re.S)


def extraire_main(texte: str) -> str:
    trouve = MOTIF_MAIN.search(texte)
    return trouve.group(0) if trouve else texte


def controler() -> list[str]:
    erreurs: list[str] = []
    for chemin, nom in ((ACCUEIL, "accueil"), (MATRICE, "matrice"), (PLAN, "plan du site")):
        if not chemin.is_file():
            return [f"{nom} absent : {chemin.relative_to(RACINE)}"]
    accueil = ACCUEIL.read_text(encoding="utf-8")
    corps = extraire_main(accueil)
    texte_plan = PLAN.read_text(encoding="utf-8")
    texte_matrice = MATRICE.read_text(encoding="utf-8")
    try:
        matrice = tomllib.loads(texte_matrice)
    except (OSError, tomllib.TOMLDecodeError) as erreur:
        return [f"matrice illisible : {erreur}"]

    meta = matrice.get("meta", {})
    if meta.get("version") != 1 or str(meta.get("auteur")) != "agent":
        erreurs.append("matrice : version ou auteur absent — la carte doit être datée et attribuée à l’agent")
    if str(meta.get("date")) != "2026-11-11":
        erreurs.append("matrice : date du lot absente ou inexacte")
    if str(meta.get("page")) != "index.html":
        erreurs.append("matrice : page d’accueil absente")

    # 1. Les reprises sont recalculées, jamais crues sur parole.
    redondances = matrice.get("redondance", [])
    if len(redondances) < 8:
        erreurs.append("matrice : moins de huit redondances suivies")
    vus: set[str] = set()
    for entree in redondances:
        identifiant = str(entree.get("id", ""))
        if identifiant in vus:
            erreurs.append(f"redondance déclarée deux fois : {identifiant}")
        vus.add(identifiant)
        motif = str(entree.get("motif", ""))
        try:
            compte = len(re.findall(motif, corps))
        except re.error as erreur:
            erreurs.append(f"redondance {identifiant} : motif illisible : {erreur}")
            continue
        seuil = int(entree.get("seuil", -1))
        avant = int(entree.get("avant", 0))
        apres = int(entree.get("apres", 0))
        if compte > seuil:
            erreurs.append(
                f"redondance revenue : {identifiant} compte {compte} occurrence(s), seuil {seuil}"
            )
        if not (avant > apres >= 0):
            erreurs.append(f"redondance {identifiant} : le relevé avant/après n’annonce pas une baisse")
        if apres != compte:
            erreurs.append(
                f"redondance {identifiant} : la matrice annonce {apres}, l’accueil en contient {compte}"
            )
        if len(str(entree.get("decision", ""))) < 20:
            erreurs.append(f"redondance {identifiant} : décision de placement absente")

    # Une seule section doit encore décrire ce que sont les ressources.
    motif_description = next(
        (str(e["motif"]) for e in redondances if e.get("id") == "description_ressource"), ""
    )
    if motif_description:
        sections_qui_decrivent = [
            i for i, bloc in enumerate(MOTIF_SECTION.findall(corps), 1)
            if re.search(motif_description, bloc)
        ]
        if len(sections_qui_decrivent) > 1:
            erreurs.append(
                "description des ressources répétée dans plusieurs sections : "
                + ", ".join(str(i) for i in sections_qui_decrivent)
            )

    # 2. Six sections, dans l’ordre du visiteur.
    nb_sections = len(re.findall(r"<section\b", corps))
    if nb_sections != int(meta.get("sections_apres", -1)):
        erreurs.append(f"nombre de sections inexact : {nb_sections} au lieu de {meta.get('sections_apres')}")
    if int(meta.get("sections_avant", 0)) <= nb_sections:
        erreurs.append("la matrice n’annonce pas une réduction du nombre de sections")
    positions = {ancre: accueil.find(f'id="{ancre}"') for ancre in ORDRE_ATTENDU}
    for ancre, position in positions.items():
        if position < 0:
            erreurs.append(f"ancre absente de l’accueil : {ancre}")
    if all(p >= 0 for p in positions.values()):
        ordre_reel = sorted(ORDRE_ATTENDU, key=lambda a: positions[a])
        if tuple(ordre_reel) != ORDRE_ATTENDU:
            erreurs.append("ordre des sections illogique : " + " → ".join(ordre_reel))
    for ancre in ANCRE_OBLIGATOIRES:
        if f'id="{ancre}"' not in accueil and f'class="{ancre}"' not in accueil:
            # home-hero-facts est une classe, pas une id.
            if ancre != "home-hero-facts":
                erreurs.append(f"repère d’ancre absent : {ancre}")
    for repere in REPERES_ACCUEIL:
        if repere not in accueil:
            erreurs.append(f"repère d’accueil exigé par une autre garde, absent : {repere}")

    # 3. Les quatre portes de l’orienteur : une question, une destination.
    liste = re.search(r'<ul\b[^>]*class="home-entry-list"[^>]*>(.*?)</ul>', corps, re.S)
    portes = matrice.get("porte", [])
    if liste is None:
        erreurs.append("orienteur absent : liste « home-entry-list » introuvable")
    else:
        entrees = MOTIF_LI.findall(liste.group(1))
        if len(entrees) != len(portes) or len(portes) != 4:
            erreurs.append(f"orienteur : {len(entrees)} entrée(s) pour {len(portes)} porte(s) déclarée(s)")
        else:
            for entree, porte in zip(entrees, portes):
                liens = re.findall(r'href="([^"]+)"', entree)
                attendu = str(porte.get("destination"))
                if liens != [attendu]:
                    erreurs.append(
                        f"porte {porte.get('numero')} : destination {liens} au lieu de {attendu}"
                    )
                if str(porte.get("question", "")) not in entree:
                    erreurs.append(f"porte {porte.get('numero')} : question absente de l’accueil")
    destinations = [str(p.get("destination")) for p in portes]
    if len(set(destinations)) != len(destinations):
        erreurs.append("deux portes mènent à la même destination")

    # 4. Le plan couvre toutes les surfaces du site.
    pages = matrice.get("page", [])
    if len(pages) < 15:
        erreurs.append(f"plan du site incomplet : {len(pages)} entrée(s)")
    chemins: set[str] = set()
    for page in pages:
        chemin = str(page.get("chemin", ""))
        if chemin in chemins:
            erreurs.append(f"page déclarée deux fois : {chemin}")
        chemins.add(chemin)
        cible = RACINE / chemin
        if not (cible.is_file() or cible.is_dir()):
            erreurs.append(f"page du plan introuvable : {chemin}")
        for champ in ("role", "public", "entree_depuis", "destination", "statut", "limite"):
            if len(str(page.get(champ, ""))) < 3:
                erreurs.append(f"page {chemin} : champ « {champ} » absent")
    for obligatoire in PAGES_OBLIGATOIRES:
        if obligatoire not in chemins:
            erreurs.append(f"page obligatoire absente du plan du site : {obligatoire}")
    navigation = [str(x) for x in meta.get("navigation", [])]
    if len(navigation) < 9:
        erreurs.append("navigation principale incomplète dans la matrice")
    for cible in navigation:
        if f'href="{cible}"' not in accueil:
            erreurs.append(f"lien de navigation absent de l’accueil : {cible}")

    # 5. Brainstorming : trois options, une seule retenue.
    options = matrice.get("option", [])
    retenues = [o for o in options if o.get("decision") == "retenue"]
    if len(options) != 3 or len(retenues) != 1:
        erreurs.append(f"brainstorming : {len(options)} option(s), {len(retenues)} retenue(s)")
    if not any("ne pas construire" in str(o.get("contenu", "")).lower()
               or "minimale" in str(o.get("titre", "")).lower() for o in options):
        erreurs.append("brainstorming : l’option « ne rien construire » ou minimale est absente")
    for option in options:
        for champ in ("titre", "contenu", "cout", "risque"):
            if len(str(option.get(champ, ""))) < 10:
                erreurs.append(f"option {option.get('id')} : champ « {champ} » trop court")

    # 6. Aucune classe CSS de l’ancienne page n’a été perdue.
    classes = [str(c) for c in meta.get("classes_css", [])]
    if len(classes) < 40:
        erreurs.append("liste des classes CSS conservées incomplète")
    for classe in classes:
        if not re.search(r'class="[^"]*\b' + re.escape(classe) + r'\b', accueil):
            erreurs.append(f"classe CSS perdue lors de la refonte : {classe}")

    # 7. Le plan reste honnête et sans URL externe recopiée.
    for section in SECTIONS_PLAN:
        if section not in texte_plan:
            erreurs.append(f"section absente du plan du site : {section}")
    for chemin in sorted(set(CHEMIN.findall(texte_plan))):
        if not (RACINE / chemin).exists():
            erreurs.append(f"chemin local introuvable : {chemin}")
    for nom, texte in (("plan", texte_plan), ("matrice", texte_matrice)):
        for scheme in SCHEMES:
            if scheme in texte:
                erreurs.append(f"{nom} : URL externe recopiée ({scheme})")
        trouve = INTERDITES.search(texte)
        if trouve:
            erreurs.append(f"{nom} : formulation interdite : {trouve.group(0)}")
        if APOSTROPHE.search(texte):
            erreurs.append(f"{nom} : apostrophe droite — employer l’apostrophe typographique")
    for repere in ("11 novembre 2026", "redondance", "brainstorming", "une seule fois"):
        if repere not in texte_plan:
            erreurs.append(f"repère absent du plan du site : {repere}")

    # 8. Aucune validation humaine fabriquée par l’agent.
    if RELECTURES.is_file():
        try:
            humaines = tomllib.loads(RELECTURES.read_text(encoding="utf-8"))
        except tomllib.TOMLDecodeError as erreur:
            erreurs.append(f"registre humain illisible : {erreur}")
        else:
            if humaines.get("relecture"):
                erreurs.append("registre humain non vide : une refonte d’agent ne doit jamais y écrire")
    return erreurs


def main() -> int:
    erreurs = controler()
    if erreurs:
        print("ÉCHEC — plan complet du site et accueil sans redondance", file=sys.stderr)
        for erreur in erreurs:
            print(f"    {erreur}", file=sys.stderr)
        return 1
    matrice = tomllib.loads(MATRICE.read_text(encoding="utf-8"))
    corps = extraire_main(ACCUEIL.read_text(encoding="utf-8"))
    print(
        f"Plan du site vérifié : {len(matrice['page'])} surfaces, "
        f"{len(re.findall(r'<section', corps))} sections ordonnées, "
        f"{len(matrice['porte'])} portes distinctes, "
        f"{len(matrice['redondance'])} reprises recalculées sous leur seuil, "
        f"{len(matrice['meta']['classes_css'])} classes CSS conservées, "
        "aucune validation inventée."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
