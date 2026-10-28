#!/usr/bin/env python3
"""Contrôles hors ligne des pages statiques, liens locaux et scripts JavaScript.

Ce vérificateur n'effectue aucune requête vers un site externe. Il contrôle les
pages déployées (et les fiches autonomes), les références locales, les ancres,
quelques relations d'accessibilité et la syntaxe JS disponible via Node.js.
"""
from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import tomllib
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

#: Racine lue par le contrôle. La surcharge sert un usage précis : rejouer les
#: mutations sur une copie du dépôt (`outils/test_mutations_site_statique.py`)
#: sans toucher aux fichiers réels. Une porte qui modifie l'arbre qu'elle
#: contrôle finit par le laisser modifié après un échec.
ROOT = Path(os.environ.get("MRSC_RACINE") or Path(__file__).resolve().parent.parent).resolve()

# Statuts éditoriaux : définitions partagées, jamais recopiées en chaîne locale.
sys.path.insert(0, str(ROOT / "outils"))
from statuts_editoriaux import PROTOTYPE, RELU, est_prototype, est_relue, porte_un_statut  # noqa: E402

#: Quelques nombres écrits en lettres dans les documents rédigés à la main.
NOMBRES_EN_LETTRES = {
    55: "cinquante-cinq", 56: "cinquante-six", 57: "cinquante-sept", 58: "cinquante-huit",
    80: "quatre-vingts", 81: "quatre-vingt-un", 82: "quatre-vingt-deux",
    83: "quatre-vingt-trois", 84: "quatre-vingt-quatre",
}
SITE_URL = "https://thejmimiia-code.github.io/MRSC/"
PAGES = sorted(ROOT.glob("*.html"))
PAGES.extend(sorted((ROOT / "apprendre" / "fiches").glob("*.html")))
PAGES.append(ROOT / "simulateur" / "index.html")
ERREURS: list[str] = []
LOT_RECENT = (
    "fr-lire-ponctuation",
    "langue-anglais-epeler",
    "maths-lire-tableau-croise",
    "maths-reperer-angle-droit",
    "sciences-cycle-vie-plante",
    "geo-lire-legende-carte",
    "histoire-situer-siecle",
    "info-systeme-exploitation",
    "numerique-formuler-recherche",
    "recherche-conserver-reference",
    "civ-trouver-service-public",
    "info-table-requete-web",
    "prog-lire-licence-logiciel",
    "civ-reperer-echelle-institution",
    "econ-lire-mention-garantie",
    "civ-reperer-info-electorale",
    "econ-distinguer-interet-frais",
    "langue-reperer-mot-deja-connu",
    "recherche-distinguer-resume-citation",
    "histoire-reperer-echelle-france-monde",
    "sante-reperer-source-publique",
)


@dataclass
class PageInfo:
    chemin: Path
    ids: set[str] = field(default_factory=set)
    doublons: set[str] = field(default_factory=set)
    references: list[tuple[str, str, int]] = field(default_factory=list)
    relations: list[tuple[str, str, int]] = field(default_factory=list)
    langues: list[str] = field(default_factory=list)
    titres: int = 0
    texte_titre: str = ""
    descriptions: list[str] = field(default_factory=list)
    canoniques: list[str] = field(default_factory=list)
    directives_robots: list[str] = field(default_factory=list)
    liens_decrits: list[str] = field(default_factory=list)
    donnees_structurees: list[str] = field(default_factory=list)
    mains: int = 0
    scripts: list[tuple[str, str]] = field(default_factory=list)
    images_sans_alt: list[int] = field(default_factory=list)
    iframes_sans_titre: list[int] = field(default_factory=list)


class InspecteurHTML(HTMLParser):
    def __init__(self, chemin: Path) -> None:
        super().__init__(convert_charrefs=True)
        self.info = PageInfo(chemin=chemin)
        self.script_type = ""
        self.script_src = False
        self.script_lines: list[str] = []
        self.script_number = 0
        self.titre_en_cours = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attributs = dict(attrs)
        ligne = self.getpos()[0]
        if tag == "html":
            langue = (attributs.get("lang") or "").strip()
            if langue:
                self.info.langues.append(langue)
        if tag == "meta":
            nom = (attributs.get("name") or "").strip().casefold()
            contenu = (attributs.get("content") or "").strip()
            if nom == "description":
                self.info.descriptions.append(contenu)
            elif nom in {"robots", "googlebot", "bingbot"}:
                self.info.directives_robots.append(contenu)
        if tag == "link":
            relations = set((attributs.get("rel") or "").casefold().split())
            href = (attributs.get("href") or "").strip()
            if "canonical" in relations:
                self.info.canoniques.append(href)
            if "describedby" in relations:
                self.info.liens_decrits.append(href)
        if tag == "title":
            self.info.titres += 1
            self.titre_en_cours = True
        if tag == "main":
            self.info.mains += 1
        identifiant = attributs.get("id")
        if identifiant:
            if identifiant in self.info.ids:
                self.info.doublons.add(identifiant)
            self.info.ids.add(identifiant)
        for relation in ("aria-controls", "aria-labelledby", "aria-describedby", "for"):
            valeur = (attributs.get(relation) or "").strip()
            if valeur:
                self.info.relations.append((relation, valeur, ligne))
        if tag == "img" and "alt" not in attributs:
            self.info.images_sans_alt.append(ligne)
        if tag == "iframe" and not (attributs.get("title") or "").strip():
            self.info.iframes_sans_titre.append(ligne)
        for attribut in ("href", "src", "action", "poster"):
            valeur = (attributs.get(attribut) or "").strip()
            if valeur:
                self.info.references.append((attribut, valeur, ligne))
        if tag == "script":
            self.script_number += 1
            self.script_type = (attributs.get("type") or "text/javascript").lower().split(";", 1)[0].strip()
            self.script_src = bool(attributs.get("src"))
            self.script_lines = []

    def handle_data(self, data: str) -> None:
        if self.titre_en_cours:
            self.info.texte_titre += data
        if self.script_number and not self.script_src:
            self.script_lines.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag == "title":
            self.titre_en_cours = False
        if tag == "script" and self.script_number and not self.script_src:
            contenu = "".join(self.script_lines)
            if self.script_type in ("text/javascript", "application/javascript", "module"):
                self.info.scripts.append((f"{self.info.chemin.relative_to(ROOT)}:script-{self.script_number}", contenu))
            elif self.script_type == "application/ld+json":
                self.info.donnees_structurees.append(contenu)
            self.script_number = 0
            self.script_src = False
            self.script_lines = []


class InspecteurDependances(HTMLParser):
    """Repère les ressources qui chargeraient un service tiers sans action."""

    ATTRIBUTS_DISTANTS = {
        "script": ("src",),
        "img": ("src", "srcset"),
        "iframe": ("src",),
        "video": ("src", "poster"),
        "audio": ("src",),
        "source": ("src", "srcset"),
        "track": ("src",),
        "embed": ("src",),
        "object": ("data",),
        "form": ("action",),
    }
    RELATIONS_CHARGEANTES = {
        "stylesheet", "preload", "modulepreload", "preconnect", "dns-prefetch", "icon", "manifest"
    }

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.ressources: list[tuple[str, str, str]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attributs = dict(attrs)
        for attribut in self.ATTRIBUTS_DISTANTS.get(tag, ()):
            valeur = (attributs.get(attribut) or "").strip()
            if not valeur:
                continue
            candidats = valeur.split(",") if attribut == "srcset" else [valeur]
            for candidat in candidats:
                url = candidat.strip().split()[0] if candidat.strip() else ""
                if url:
                    self.ressources.append((tag, attribut, url))
        if tag == "link":
            relations = set((attributs.get("rel") or "").lower().split())
            cible = (attributs.get("href") or "").strip()
            if cible and relations.intersection(self.RELATIONS_CHARGEANTES):
                self.ressources.append((tag, "href", cible))


def signaler(message: str) -> None:
    ERREURS.append(message)
    print(f"ÉCHEC — {message}")


def totaux_catalogue() -> tuple[int, int, int]:
    """Nombre de fiches, de fiches initiales et de prototypes, relus depuis le catalogue.

    Ces trois nombres ne sont jamais recopiés : un ajout de fiche doit faire
    évoluer les pages et les contrôles ensemble, pas seulement la source.
    """
    try:
        catalogue = tomllib.loads((ROOT / "docs" / "apprentissage" / "catalogue.toml").read_text(encoding="utf-8"))
    except (OSError, UnicodeError, tomllib.TOMLDecodeError):
        return 0, 0, 0
    fiches = catalogue.get("fiche", [])
    prototypes = sum(1 for fiche in fiches if est_prototype(fiche))
    return len(fiches), len(fiches) - prototypes, prototypes


def verifier_catalogue_apprentissage() -> None:
    chemin = ROOT / "docs" / "apprentissage" / "catalogue.toml"
    try:
        catalogue = tomllib.loads(chemin.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, tomllib.TOMLDecodeError) as erreur:
        signaler(f"docs/apprentissage/catalogue.toml : catalogue TOML illisible : {erreur}")
        return
    fiches = catalogue.get("fiche", [])
    ids = [fiche.get("id", "") for fiche in fiches]
    prototypes = [fiche for fiche in fiches if est_prototype(fiche)]
    doublons = sorted(ident for ident in set(ids) if ids.count(ident) > 1)
    if not fiches:
        signaler("catalogue d’apprentissage : aucune fiche")
    if doublons:
        signaler("catalogue d’apprentissage : identifiants dupliqués : " + ", ".join(doublons))
    pages_generees = sorted((ROOT / "apprendre" / "fiches").glob("*.html"))
    if len(pages_generees) != len(fiches):
        signaler(
            f"apprendre/fiches : {len(pages_generees)} pages générées pour {len(fiches)} fiches du catalogue"
        )
    sans_trace = [fiche.get("id", "?") for fiche in prototypes if not fiche.get("note_statut_editorial")]
    if sans_trace:
        signaler("catalogue d’apprentissage : prototypes sans note de statut : " + ", ".join(sans_trace))
    absents = sorted(set(LOT_RECENT) - set(ids))
    if absents:
        signaler("catalogue d’apprentissage : fiches du lot courant absentes : " + ", ".join(absents))
    champs_requis = (
        "titre", "resume", "objectif", "situation", "analogie_titre", "analogie",
        "limite_analogie", "notions", "demarche", "exercice", "aide", "correction",
        "a_retenir", "transferer", "sources",
    )
    par_id = {fiche.get("id"): fiche for fiche in fiches}
    for identifiant in LOT_RECENT:
        fiche = par_id.get(identifiant)
        if fiche is None:
            continue
        if fiche.get("statut_editorial") != "Prototype à relire":
            signaler(f"{identifiant} : statut attendu « Prototype à relire »")
        manquants = [champ for champ in champs_requis if not fiche.get(champ)]
        if manquants:
            signaler(f"{identifiant} : champ(s) de fiche incomplet(s) : {', '.join(manquants)}")
    if not ERREURS:
        print(
            f"Catalogue d’apprentissage : {len(fiches)} fiches sans doublon, {len(prototypes)} prototypes ; "
            "le lot courant et les fiches du 15 octobre 2026 ont leurs champs structurels et restent à relire."
        )


def analyser(chemin: Path) -> PageInfo:
    inspecteur = InspecteurHTML(chemin)
    try:
        inspecteur.feed(chemin.read_text(encoding="utf-8"))
        inspecteur.close()
    except (OSError, UnicodeError, ValueError) as erreur:
        signaler(f"lecture HTML de {chemin.relative_to(ROOT)} : {erreur}")
    info = inspecteur.info
    relatif = chemin.relative_to(ROOT).as_posix()
    if not info.langues:
        signaler(f"{relatif} : attribut lang absent sur <html>")
    if info.titres != 1:
        signaler(f"{relatif} : {info.titres} élément(s) <title>, un seul attendu")
    if info.mains != 1:
        signaler(f"{relatif} : {info.mains} élément(s) <main>, un seul attendu")
    if info.doublons:
        signaler(f"{relatif} : identifiant(s) HTML dupliqué(s) : {', '.join(sorted(info.doublons))}")
    if info.images_sans_alt:
        signaler(f"{relatif} : image(s) sans attribut alt, lignes {info.images_sans_alt}")
    if info.iframes_sans_titre:
        signaler(f"{relatif} : iframe(s) sans titre, lignes {info.iframes_sans_titre}")
    for relation, valeurs, ligne in info.relations:
        inconnus = [valeur for valeur in valeurs.split() if valeur not in info.ids]
        if inconnus:
            signaler(f"{relatif}:{ligne} : {relation} pointe vers un identifiant absent : {', '.join(inconnus)}")
    return info


def cible_locale(page: Path, chemin_url: str) -> Path:
    decodifie = unquote(chemin_url)
    if decodifie.startswith("/"):
        cible = ROOT / decodifie.lstrip("/")
    elif decodifie:
        cible = page.parent / decodifie
    else:
        cible = page
    cible = cible.resolve()
    if ROOT not in cible.parents and cible != ROOT:
        raise ValueError("chemin sortant du dépôt")
    if cible.is_dir():
        cible = cible / "index.html"
    return cible


def verifier_liens(infos: dict[Path, PageInfo]) -> None:
    cache_ancres = {chemin: info.ids for chemin, info in infos.items()}
    for chemin, info in infos.items():
        relatif = chemin.relative_to(ROOT).as_posix()
        for attribut, valeur, ligne in info.references:
            parties = urlsplit(valeur)
            if parties.scheme or parties.netloc:
                continue
            if valeur.startswith(("#", "?")) and not parties.path:
                cible = chemin
            else:
                try:
                    cible = cible_locale(chemin, parties.path)
                except ValueError as erreur:
                    signaler(f"{relatif}:{ligne} : {attribut}={valeur!r} {erreur}")
                    continue
            if not cible.is_file():
                signaler(f"{relatif}:{ligne} : {attribut} local introuvable : {valeur!r}")
                continue
            fragment = unquote(parties.fragment)
            if fragment and cible.suffix.lower() in (".html", ".htm"):
                if cible not in cache_ancres:
                    cache_ancres[cible] = analyser(cible).ids
                if fragment not in cache_ancres[cible]:
                    signaler(f"{relatif}:{ligne} : ancre #{fragment} absente dans {cible.relative_to(ROOT)}")


def verifier_sitemap() -> None:
    chemin = ROOT / "sitemap.xml"
    if not chemin.is_file():
        signaler("sitemap.xml absent")
        return
    try:
        racine = ET.parse(chemin).getroot()
    except (ET.ParseError, OSError) as erreur:
        signaler(f"sitemap.xml invalide : {erreur}")
        return
    ns = "{http://www.sitemaps.org/schemas/sitemap/0.9}"
    emplacements = [element.text or "" for element in racine.findall(f"{ns}url/{ns}loc")]
    publies: set[str] = set()
    for url in emplacements:
        parties = urlsplit(url)
        if parties.scheme != "https" or parties.netloc != "thejmimiia-code.github.io" or not parties.path.startswith("/MRSC/"):
            signaler(f"sitemap.xml : adresse hors du site du projet : {url!r}")
            continue
        relatif = unquote(parties.path.removeprefix("/MRSC/"))
        if not relatif:
            relatif = "index.html"
        elif relatif.endswith("/"):
            relatif += "index.html"
        cible = ROOT / relatif
        if not cible.is_file():
            signaler(f"sitemap.xml : page déclarée introuvable : {url!r}")
        publies.add(relatif)
    attendus = {
        page.relative_to(ROOT).as_posix()
        for page in PAGES
        if page.is_file() and page.name != "404.html"
    }
    doublons = len(emplacements) != len(set(emplacements))
    if doublons:
        signaler("sitemap.xml contient des adresses dupliquées")
    absents = sorted(attendus - publies)
    if absents:
        signaler("sitemap.xml omet des pages publiques : " + ", ".join(absents))
    print(f"Sitemap XML : {len(emplacements)} URL(s), {len(attendus)} page(s) publiques attendues.")


def url_canonique_attendue(chemin: Path) -> str:
    relatif = chemin.relative_to(ROOT).as_posix()
    if relatif == "index.html":
        return SITE_URL
    if relatif == "simulateur/index.html":
        return SITE_URL + "simulateur/"
    return SITE_URL + relatif


def directives_noindex(directives: list[str]) -> bool:
    return any(
        {"noindex", "none"}.intersection(
            terme.strip() for terme in directive.casefold().split(",")
        )
        for directive in directives
    )


def verifier_metadonnees(infos: dict[Path, PageInfo]) -> None:
    """Vérifie les repères d’indexation et les données structurées des pages publiques."""
    publiques = [
        (chemin, info)
        for chemin, info in infos.items()
        if chemin.name != "404.html"
    ]
    titres: list[str] = []
    descriptions: list[str] = []
    canoniques: list[str] = []
    avant = len(ERREURS)
    for chemin, info in publiques:
        relatif = chemin.relative_to(ROOT).as_posix()
        titre = info.texte_titre.strip()
        description = info.descriptions[0].strip() if len(info.descriptions) == 1 else ""
        canonique = info.canoniques[0].strip() if len(info.canoniques) == 1 else ""
        if info.titres != 1 or not titre:
            signaler(f"{relatif} : un titre HTML unique et non vide est requis")
        else:
            titres.append(titre.casefold())
        if len(info.descriptions) != 1 or not description:
            signaler(f"{relatif} : une description meta unique et non vide est requise")
        else:
            descriptions.append(" ".join(description.split()).casefold())
        attendu = url_canonique_attendue(chemin)
        if len(info.canoniques) != 1 or canonique != attendu:
            signaler(f"{relatif} : canonique attendue {attendu!r}, reçue {info.canoniques!r}")
        else:
            canoniques.append(canonique)
        if directives_noindex(info.directives_robots):
            signaler(f"{relatif} : directive noindex inattendue sur une page publique")
        for bloc in info.donnees_structurees:
            try:
                json.loads(bloc)
            except json.JSONDecodeError as erreur:
                signaler(f"{relatif} : données JSON-LD invalides : {erreur}")

    for libelle, valeurs in (
        ("titre HTML", titres),
        ("description meta", descriptions),
        ("URL canonique", canoniques),
    ):
        doublons = sorted({valeur for valeur in valeurs if valeurs.count(valeur) > 1})
        if doublons:
            signaler(f"pages publiques : {libelle} en double : " + "; ".join(doublons))

    page_404 = infos.get(ROOT / "404.html")
    if page_404 is None or not directives_noindex(page_404.directives_robots):
        signaler("404.html : conserver une directive noindex explicite hors du sitemap")

    accueil = infos.get(ROOT / "index.html")
    if accueil is None:
        signaler("index.html : page d’accueil absente de l’analyse des métadonnées")
    else:
        if accueil.liens_decrits != ["llms.txt"]:
            signaler("index.html : un lien rel=describedby vers llms.txt est attendu")
        if len(accueil.donnees_structurees) != 1:
            signaler("index.html : un bloc JSON-LD unique est attendu")
        else:
            try:
                donnees = json.loads(accueil.donnees_structurees[0])
                graphe = donnees.get("@graph", []) if isinstance(donnees, dict) else []
                par_type = {
                    objet.get("@type"): objet
                    for objet in graphe
                    if isinstance(objet, dict) and isinstance(objet.get("@type"), str)
                }
                organisation = par_type.get("Organization", {})
                site = par_type.get("WebSite", {})
                page = par_type.get("WebPage", {})
                description = accueil.descriptions[0] if len(accueil.descriptions) == 1 else ""
                valide = (
                    donnees.get("@context") == "https://schema.org"
                    and organisation.get("name") == "Mouvement Représentatif de la Société Civile"
                    and organisation.get("alternateName") == "M.R.S.C."
                    and organisation.get("url") == SITE_URL
                    and site.get("url") == SITE_URL
                    and site.get("inLanguage") == "fr-FR"
                    and site.get("publisher", {}).get("@id") == organisation.get("@id")
                    and page.get("url") == SITE_URL
                    and page.get("description") == description
                    and page.get("isPartOf", {}).get("@id") == site.get("@id")
                    and page.get("about", {}).get("@id") == organisation.get("@id")
                )
                if not valide:
                    signaler("index.html : le JSON-LD doit décrire seulement l’organisation, le site et la page avec des données cohérentes")
            except (json.JSONDecodeError, AttributeError, TypeError) as erreur:
                signaler(f"index.html : structure JSON-LD inattendue : {erreur}")

    if len(ERREURS) == avant:
        print(
            f"Métadonnées : {len(publiques)} pages avec titre, description et canonique uniques ; "
            "aucune directive noindex inattendue ; JSON-LD d’accueil valide."
        )


def verifier_llms_txt() -> None:
    """Vérifie le sommaire Markdown expérimental et ses liens locaux."""
    avant = len(ERREURS)
    chemin = ROOT / "llms.txt"
    try:
        contenu = chemin.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as erreur:
        signaler(f"llms.txt : fichier absent ou illisible : {erreur}")
        return
    lignes = contenu.splitlines()
    if not lignes or not lignes[0].startswith("# "):
        signaler("llms.txt : un titre Markdown de niveau 1 est requis en première ligne")
    if not any(ligne.startswith("> ") for ligne in lignes[1:]):
        signaler("llms.txt : un résumé en citation Markdown est requis")
    if not any(ligne.startswith("## ") for ligne in lignes[1:]):
        signaler("llms.txt : au moins une section de liens est requise")

    liens = re.findall(r"\[[^\]]+\]\((https?://[^)]+)\)", contenu)
    if len(liens) < 8:
        signaler(f"llms.txt : sommaire trop court ({len(liens)} liens trouvés)")
    for url in liens:
        parties = urlsplit(url)
        if (
            parties.scheme != "https"
            or parties.netloc != "thejmimiia-code.github.io"
            or not parties.path.startswith("/MRSC/")
        ):
            signaler(f"llms.txt : URL hors du site public : {url!r}")
            continue
        relatif = unquote(parties.path.removeprefix("/MRSC/"))
        if not relatif:
            relatif = "index.html"
        elif relatif.endswith("/"):
            relatif += "index.html"
        cible = (ROOT / relatif).resolve()
        try:
            cible.relative_to(ROOT.resolve())
        except ValueError:
            signaler(f"llms.txt : chemin sortant du dépôt : {url!r}")
            continue
        if not cible.is_file():
            signaler(f"llms.txt : page liée introuvable : {url!r}")
            continue
        if parties.fragment and cible.suffix.lower() in (".html", ".htm"):
            if parties.fragment not in analyser(cible).ids:
                signaler(f"llms.txt : ancre absente dans {cible.relative_to(ROOT)} : #{parties.fragment}")
    if len(ERREURS) == avant:
        print(f"llms.txt : structure Markdown et {len(liens)} liens internes vérifiés hors ligne.")


def verifier_javascript(infos: dict[Path, PageInfo]) -> None:
    node = shutil.which("node")
    if not node:
        print("AVERTISSEMENT — Node.js absent : contrôle syntaxique JavaScript ignoré.")
        return
    scripts: list[tuple[str, str]] = []
    for dossier in (ROOT / "assets" / "js",):
        scripts.extend((path.relative_to(ROOT).as_posix(), path.read_text(encoding="utf-8")) for path in sorted(dossier.glob("*.js")))
    for info in infos.values():
        scripts.extend(info.scripts)
    with tempfile.TemporaryDirectory(prefix="mrsc-js-") as repertoire:
        for numero, (nom, contenu) in enumerate(scripts):
            source = Path(repertoire) / f"script-{numero}.js"
            source.write_text(contenu, encoding="utf-8")
            resultat = subprocess.run([node, "--check", str(source)], capture_output=True, text=True, check=False)
            if resultat.returncode:
                detail = (resultat.stderr or resultat.stdout).strip().splitlines()
                signaler(f"syntaxe JavaScript invalide dans {nom}: {detail[-1] if detail else 'erreur inconnue'}")
    print(f"Contrôle JavaScript : {len(scripts)} fichier(s) et script(s) intégré(s).")


def verifier_entrees_accueil() -> None:
    """Chaque proposition de « Par où commencer ? » doit être un vrai lien."""
    contenu = (ROOT / "index.html").read_text(encoding="utf-8")
    liste = re.search(r'<ul\b[^>]*class="home-entry-list"[^>]*>(.*?)</ul>', contenu, re.DOTALL)
    if liste is None:
        signaler("index.html : liste des points d’entrée absente")
        return
    entrees = re.findall(r"<li\b[^>]*>(.*?)</li>", liste.group(1), re.DOTALL)
    destinations = ("apprendre.html", "ia-societe.html", "simulateur.html", "#rd-eva")
    if len(entrees) != len(destinations):
        signaler("index.html : quatre propositions attendues dans Par où commencer")
        return
    avant = len(ERREURS)
    for numero, (entree, destination) in enumerate(zip(entrees, destinations), start=1):
        inspecteur = InspecteurHTML(ROOT / "index.html")
        inspecteur.feed(entree)
        liens = [url for attribut, url, _ in inspecteur.info.references if attribut == "href"]
        if liens != [destination]:
            signaler(f"index.html : proposition {numero} attendue avec un lien vers {destination}")
    if len(ERREURS) == avant:
        print("Accueil : les quatre propositions pointent vers leurs ressources respectives.")


def verifier_dependances_apprentissage() -> None:
    pages = [ROOT / "apprendre.html", ROOT / "anglais-aventure.html", *sorted((ROOT / "apprendre" / "fiches").glob("*.html"))]
    avant = len(ERREURS)
    for chemin in pages:
        relatif = chemin.relative_to(ROOT).as_posix()
        inspecteur = InspecteurDependances()
        try:
            inspecteur.feed(chemin.read_text(encoding="utf-8"))
        except (OSError, UnicodeError) as erreur:
            signaler(f"{relatif} : contrôle des dépendances impossible : {erreur}")
            continue
        for balise, attribut, url in inspecteur.ressources:
            parties = urlsplit(url)
            if parties.scheme in ("http", "https") or parties.netloc:
                signaler(f"{relatif} : dépendance chargée depuis un tiers : <{balise} {attribut}=\"{url}\">")
    motif_css_externe = re.compile(r'''(?:url\(\s*[\"']?|@import\s+(?:url\(\s*)?[\"']?)(?:https?:)?//''', re.IGNORECASE)
    for chemin_css in sorted((ROOT / "assets" / "css").rglob("*.css")):
        try:
            contenu_css = chemin_css.read_text(encoding="utf-8")
        except (OSError, UnicodeError) as erreur:
            signaler(f"{chemin_css.relative_to(ROOT)} : lecture CSS impossible : {erreur}")
            continue
        if motif_css_externe.search(contenu_css):
            signaler(f"{chemin_css.relative_to(ROOT)} : police, image ou import CSS charge une URL externe")
    if len(ERREURS) == avant:
        print(f"Autonomie technique : aucun script, média ou style distant chargé automatiquement sur {len(pages)} pages d’apprentissage.")


def verifier_aventure_anglais() -> None:
    """Contrôle les limites visibles et la structure du prototype de dialogue."""
    page = ROOT / "anglais-aventure.html"
    donnees = ROOT / "assets" / "js" / "anglais-aventure-data.js"
    donnees_atlas = ROOT / "assets" / "js" / "apprentissage-aventure-data.js"
    script = ROOT / "assets" / "js" / "anglais-aventure.js"
    avant = len(ERREURS)
    try:
        contenu_page = page.read_text(encoding="utf-8")
        contenu_script = script.read_text(encoding="utf-8")
        contenu_donnees_atlas = donnees_atlas.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as erreur:
        signaler(f"prototype d’anglais : lecture impossible : {erreur}")
        return
    marqueurs = (
        "Les Mondes", "Les Escales", "pré-A1", "A2", "B1", "sans publicité", "sans compte",
        "Aucun ordre", "minuteur", "évaluation de ton niveau", "reste dans la page",
        "stockage local", "aucun microphone", "réception", "production", "interaction",
        f"{totaux_catalogue()[0]} fiches", "15 domaines", f"{totaux_catalogue()[2]} prototypes",
        "parcours de formation personnel",
        "fiches autonomes, pas des cours distincts", "sans validation indépendante revendiquée",
    )
    absents = [marqueur for marqueur in marqueurs if marqueur.casefold() not in contenu_page.casefold()]
    if absents:
        signaler("anglais-aventure.html : transparence ou objectifs pédagogiques absents : " + ", ".join(absents))
    appels_reseau = re.compile(r"\b(?:fetch|XMLHttpRequest|WebSocket|EventSource)\b")
    if appels_reseau.search(contenu_script):
        signaler("assets/js/anglais-aventure.js : appel réseau inattendu dans le jeu local")
    if appels_reseau.search(contenu_donnees_atlas):
        signaler("assets/js/apprentissage-aventure-data.js : appel réseau inattendu dans le catalogue local")
    try:
        motif_atlas = re.search(
            r"globalThis\.MRSCApprentissageData = Object\.freeze\((\{.*\})\);\s*$",
            contenu_donnees_atlas,
            re.DOTALL,
        )
        atlas = json.loads(motif_atlas.group(1)) if motif_atlas else {}
        fiches_sources = tomllib.loads((ROOT / "docs" / "apprentissage" / "catalogue.toml").read_text(encoding="utf-8"))["fiche"]
        domaines_sources = tomllib.loads((ROOT / "docs" / "apprentissage" / "referentiel.toml").read_text(encoding="utf-8"))["domaine"]
        ids_sources = [fiche["id"] for fiche in fiches_sources]
        ids_atlas = [fiche.get("id") for fiche in atlas.get("sheets", [])]
        domaines_atlas = [domaine.get("id") for domaine in atlas.get("domains", [])]
        feuilles_par_domaine = {
            domaine["id"]: [fiche["id"] for fiche in fiches_sources if fiche["domaine"] == domaine["id"]]
            for domaine in domaines_sources
        }
        atlas_coherent = (
            ids_atlas == ids_sources
            and domaines_atlas == [domaine["id"] for domaine in domaines_sources]
            and atlas.get("sheetCount") == len(fiches_sources)
            and atlas.get("domainCount") == len(domaines_sources)
            and sum(1 for fiche in fiches_sources if est_prototype(fiche)) == atlas.get("prototypeCount")
            and all((ROOT / fiche.get("url", "")).is_file() for fiche in atlas.get("sheets", []))
            and all(domaine.get("sheetIds") == feuilles_par_domaine[domaine["id"]] for domaine in atlas.get("domains", []))
            and all(f'id="couverture-domaine-{domaine["id"]}"' in (ROOT / "apprendre.html").read_text(encoding="utf-8") for domaine in domaines_sources)
            and 'assets/js/apprentissage-aventure-data.js' in contenu_page
            and 'id="learning-path-list"' in contenu_page
        )
        if not atlas_coherent:
            signaler("Les Mondes : fiches, domaines, états éditoriaux, liens et parcours ne correspondent pas aux sources du catalogue")
    except (OSError, KeyError, TypeError, json.JSONDecodeError, tomllib.TOMLDecodeError) as erreur:
        signaler(f"Les Mondes : données de l’atlas illisibles ou incohérentes : {erreur}")
    node = shutil.which("node")
    if node:
        verification = r'''
const fs = require("node:fs");
const vm = require("node:vm");
const assert = require("node:assert/strict");
const context = {};
vm.runInNewContext(fs.readFileSync(process.argv.at(-2), "utf8"), context);
vm.runInNewContext(fs.readFileSync(process.argv.at(-1), "utf8"), context);
const missions = context.MRSCEnglishAdventureData?.missions;
const atlas = context.MRSCApprentissageData;
assert.ok(Array.isArray(missions));
assert.equal(missions.length, 5, "cinq escales originales attendues");
assert.equal(new Set(missions.map((mission) => mission.id)).size, missions.length, "identifiants uniques");
const levels = missions.map((mission) => mission.level).join(" ");
for (const level of ["Pré-A1", "A1", "A2", "B1"]) assert.ok(levels.includes(level), `repère ${level} absent`);
for (const mission of missions) {
  assert.ok(mission.title && mission.brief && mission.outcome && mission.sceneDescription);
  assert.equal(mission.turns.length, 3, `${mission.id}: trois échanges attendus`);
  assert.ok(mission.keepsake.length >= 2, `${mission.id}: expressions à garder absentes`);
  for (const turn of mission.turns) {
    for (const field of ["english", "french", "objective", "modelEnglish", "modelFrench", "tip"]) assert.ok(turn[field], `${mission.id}: ${field} absent`);
    assert.ok(turn.options.length >= 3, `${mission.id}: choix de réponse insuffisants`);
    for (const option of turn.options) {
      for (const field of ["english", "french", "feedback", "replyEnglish", "replyFrench"]) assert.ok(option[field], `${mission.id}: option sans ${field}`);
    }
  }
}
assert.ok(Array.isArray(atlas?.sheets) && Array.isArray(atlas?.domains) && Array.isArray(atlas?.paths));
assert.equal(atlas.sheetCount, atlas.sheets.length);
assert.equal(atlas.domainCount, atlas.domains.length);
assert.equal(new Set(atlas.sheets.map((sheet) => sheet.id)).size, atlas.sheetCount);
assert.equal(new Set(atlas.domains.map((domain) => domain.id)).size, atlas.domainCount);
assert.equal(atlas.prototypeCount, atlas.sheets.filter((sheet) => sheet.editorialStatus).length);
const mappedSheets = [];
for (const domain of atlas.domains) for (const sheetId of domain.sheetIds) mappedSheets.push(sheetId);
assert.equal(new Set(mappedSheets).size, atlas.sheetCount, "chaque fiche doit appartenir à un seul monde principal");
const catalogueSheetIds = [];
for (const sheet of atlas.sheets) catalogueSheetIds.push(sheet.id);
assert.deepEqual([...mappedSheets].sort(), catalogueSheetIds.sort());
const pathLevels = [];
for (const path of atlas.paths) pathLevels.push(path.level);
assert.deepEqual(pathLevels.sort(), [1, 2, 3, 4]);
assert.equal(atlas.paths.reduce((total, path) => total + path.sheetCount, 0), atlas.sheetCount);
for (const sheet of atlas.sheets) {
  assert.ok(sheet.title && sheet.summary && sheet.objective && sheet.url);
  assert.equal(sheet.url, `apprendre/fiches/${sheet.id}.html`);
}
console.log(`${missions.length} escales, ${missions.reduce((n, m) => n + m.turns.length, 0)} échanges et ${missions.reduce((n, m) => n + m.turns.reduce((k, t) => k + t.options.length, 0), 0)} réponses ; ${atlas.sheetCount} fiches dans ${atlas.domainCount} mondes, ${atlas.prototypeCount} à relire.`);
'''
        resultat = subprocess.run(
            [node, "-e", verification, str(donnees), str(donnees_atlas)],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        if resultat.returncode:
            detail = (resultat.stderr or resultat.stdout).strip().splitlines()
            signaler("données de l’aventure : contrôle des dialogues échoué : " + (detail[-1] if detail else "erreur inconnue"))
        elif len(ERREURS) == avant:
            print("Les Mondes : " + (resultat.stdout or "données cohérentes").strip())
    elif len(ERREURS) == avant:
        print("AVERTISSEMENT — Node.js absent : structure détaillée des dialogues non vérifiée.")


def verifier_dossier_apprentissage() -> None:
    total, initiales, prototypes = totaux_catalogue()
    pages_publiques = len([
        chemin for chemin in ROOT.rglob("*.html")
        if ".git" not in chemin.parts and chemin.name != "404.html"
    ])
    pages_depot = len([chemin for chemin in ROOT.rglob("*.html") if ".git" not in chemin.parts])
    controles = {
        ROOT / "README.md": (
            f"{total} fiches dans 15 domaines",
            f"{prototypes} prototypes",
            f"budgets ({pages_publiques} pages)",
        ),
        ROOT / "docs" / "rd-innovation-continue.md": (
            f"relie les {total} fiches à 15 domaines; {prototypes} fiches portent le statut « Prototype à relire »",
        ),
        ROOT / "docs" / "rd-anglais-aventure.md": (
            f"Le jeu relie les **{total} fiches** du catalogue",
            f"(26 fiches du corpus initial et {prototypes} prototypes à relire)",
        ),
        ROOT / "docs" / "rd" / "prospective-2027-2030.md": (
            f"{total} fiches dans 15 domaines, dont {prototypes} prototypes explicitement à relire",
            f"{prototypes} prototypes sont à relire",
        ),
        ROOT / "docs" / "rd" / "poids-et-sobriete-numerique.md": (
            f"parcourt les {pages_publiques} pages publiques",
            f"{total} fiches et la page du simulateur",
            f"Les {pages_publiques} pages restent sous les budgets",
        ),
        ROOT / "transparence.html": (
            "axe-core 4.14.0 a été exécuté sur les 99 pages HTML du dépôt",
            "198 exécutions sur les pages (99 × 2 largeurs)",
        ),
        # Relevé historique du 20 octobre : ne pas inventer une mesure
        # supplémentaire quand le catalogue reçoit une nouvelle fiche.
        ROOT / "docs" / "rd" / "accessibilite-2026-10-17.md": (
            "99 pages HTML × deux largeurs, soit **198 exécutions, aucune violation axe**",
        ),
        ROOT / "docs" / "rd" / "inventaire-couleurs-jetons.md": (
            "Pages HTML et 84 fiches",
        ),
        ROOT / "docs" / "rd" / "portefeuille.toml": (
            f"Faire relire les {prototypes} prototypes d'apprentissage",
            f"répartir les {prototypes} prototypes",
        ),
        ROOT / "apprendre.html": (
            f"{totaux_catalogue()[0]} entrées : {totaux_catalogue()[1]} fiches du corpus initial et {totaux_catalogue()[2]} prototypes explicitement à relire",
            "La relecture indépendante de toutes les fiches du corpus initial n’est pas garantie",
            "Prototype à relire",
            "Ambition éditoriale de long terme",
            "1 000 fiches autonomes",
            "pas l’offre actuelle",
            "les liens de sources sont facultatifs",
        ),
        ROOT / "liens-utiles.html": (
            "services publics, de ressources institutionnelles, pédagogiques et associatives",
            "sommairement le 8 octobre 2026",
            "conditions de réutilisation n’ont pas été contrôlées pour chaque ressource précise",
            "DGCCRF",
            "SignalConso",
            "Élections — ministère de l’Intérieur",
            "ANSSI",
            "RTE éCO2mix",
            "Les organisations citées publient sous leur responsabilité",
        ),
        ROOT / "apprendre" / "fiches" / "recherche-lire-etude.html": (
            "Statut éditorial : Prototype à relire",
            "Une relecture indépendante reste à faire",
            "Creative Commons Attribution License",
            "aucun extrait, figure, exercice ni texte de la source n’est reproduit",
            "Tu peux suivre cette fiche sans ouvrir ces liens",
        ),
        ROOT / "apprendre" / "fiches" / "maths-convertir-unites.html": (
            "Statut éditorial : Prototype à relire",
            "licence source non vérifiée",
            "1 m = 100 cm",
            "1 350 mL",
            "aucun texte, exemple, tableau, figure ou exercice de la source n’est repris",
        ),
        ROOT / "apprendre" / "fiches" / "maths-moyenne.html": (
            "Statut éditorial : Prototype à relire",
            "licence source non vérifiée",
            "20 ÷ 4 = 5",
            "Moyenne = somme des valeurs ÷ nombre de valeurs",
            "aucun texte, exemple, tableau, figure ou exercice de la source n’est repris",
        ),
        ROOT / "apprendre" / "fiches" / "maths-estimer-calcul.html": (
            "Statut éditorial : Prototype à relire",
            "licence source non vérifiée",
            "50 + 40 = 90",
            "26 + 41 = 67",
            "aucun texte, exemple, tableau, figure ou exercice de la source n’est repris",
        ),
        ROOT / "apprendre" / "fiches" / "info-ordinateur-fonctions.html": (
            "Statut éditorial : Prototype à relire",
            "Comprendre les rôles d’un ordinateur",
            "leurs licences de réutilisation n’ont pas été vérifiées",
        ),
        ROOT / "apprendre" / "fiches" / "prog-comparer-langages.html":  (
            "Statut éditorial : Prototype à relire",
            "Lire les exemples, sans rien installer",
            "ne sont pas exécutés par cette page",
            "data-code-examples=\"prog-comparer-langages\"",
            "tabindex=\"0\" role=\"region\" aria-label=\"Extrait 1",
            "Extrait 2 — JavaScript",
        ),
        ROOT / "apprendre" / "fiches" / "tech-circuit-ouvert-ferme.html": (
            "Statut éditorial : Prototype à relire",
            "circuit électrique ouvert ou fermé",
            "aucun essai pratique ni apprenant n’est revendiqué",
        ),
        ROOT / "apprendre" / "fiches" / "tech-electronique-capteur.html": (
            "Statut éditorial : Prototype à relire",
            "capteur, commande et action",
            "aucun montage, essai matériel ou test apprenant n’est revendiqué",
        ),
        ROOT / "apprendre" / "fiches" / "civ-choisir-source-publique.html": (
            "Statut éditorial : Prototype à relire",
            "Choisir une source publique adaptée",
            "leurs licences de réutilisation ne sont pas déclarées vérifiées",
        ),
        ROOT / "apprendre" / "fiches" / "econ-lire-facture.html": (
            "Statut éditorial : Prototype à relire",
            "Lire une facture et repérer une échéance",
            "28 € + 12 € = 40 €",
            "Le 6 septembre est la date d’établissement du document",
            "le 20 septembre est l’échéance affichée",
            "ne décrit ni les mentions légalement obligatoires",
            "DGCCRF — information sur la consommation",
            "licence source non vérifiée",
        ),
        ROOT / "apprendre" / "fiches" / "econ-comparer-prix-unitaires.html": (
            "Statut éditorial : Prototype à relire",
            "Comparer deux prix à quantité égale",
            "4 × 1,50 € = 6,00 €/kg",
            "2 × 2,80 € = 5,60 €/kg",
            "ne constitue pas une recommandation d’achat",
            "DGCCRF — information sur la consommation",
            "licence source non vérifiée",
        ),
        ROOT / "apprendre" / "fiches" / "fr-reperer-idee-texte.html": (
            "Statut éditorial : Prototype à relire",
            "Repérer l’idée principale et les informations utiles",
            "20 juin",
            "sépare ce qui est écrit de ce que tu en déduis",
            "licence source non vérifiée",
        ),
        ROOT / "apprendre" / "fiches" / "langue-anglais-demander-aide.html": (
            "Statut éditorial : Prototype à relire",
            "Demander de l’aide ou une répétition en anglais",
            "Could you say that again, please?",
            "Could you speak more slowly, please?",
            "La fiche ne fournit pas d’audio",
        ),
        ROOT / "apprendre" / "fiches" / "geo-points-cardinaux.html": (
            "Statut éditorial : Prototype à relire",
            "S’orienter avec les points cardinaux",
            "Le jardin se trouve à l’est",
            "ni les rues à suivre",
            "aucun trajet réel",
        ),
        ROOT / "apprendre" / "fiches" / "histoire-lire-frise.html": (
            "Statut éditorial : Prototype à relire",
            "Lire une frise chronologique et ordonner des événements",
            "du 3 au 10 juin, il s’écoule 7 jours",
            "ne prouve pas qu’une étape a causé la suivante",
        ),
        ROOT / "apprendre" / "fiches" / "maths-probabilite-tirage.html": (
            "Statut éditorial : Prototype à relire",
            "Comprendre une chance dans un tirage simple",
            "1/4",
            "2/4",
            "probabilité ne garantit pas",
            "on suppose que chaque jeton a la même chance d’être tiré",
            "licence source non vérifiée",
        ),
        ROOT / "apprendre" / "fiches" / "numerique-organiser-fichiers.html": (
            "Statut éditorial : Prototype à relire",
            "Nommer et retrouver ses fichiers sans exposer ses données",
            "planning-reunion-2026-10-v02",
            "renommer ne convertit pas",
            "aucun fichier réel, partage ou suppression n’est demandé",
        ),
        ROOT / "apprendre" / "fiches" / "methodes-demander-clarification.html": (
            "Statut éditorial : Prototype à relire",
            "Reformuler une demande avant de commencer",
            "Si j’ai bien compris",
            "traiter une absence de réponse comme un accord",
        ),
        ROOT / "apprendre" / "fiches" / "fr-preparer-explication-orale.html": (
            "Statut éditorial : Prototype à relire",
            "Préparer une explication courte",
            "ne suppose pas que parler à voix haute soit possible ou souhaité",
            "pictogrammes",
        ),
        ROOT / "apprendre" / "fiches" / "fr-argumenter-avec-exemple.html": (
            "Statut éditorial : Prototype à relire",
            "Présenter une idée avec une raison et un exemple",
            "Un exemple illustre une idée",
            "75 minutes se terminerait à 15 h 15",
            "pas à forcer l’accord",
        ),
        ROOT / "apprendre" / "fiches" / "maths-equation-simple.html": (
            "Statut éditorial : Prototype à relire",
            "Résoudre une équation simple en gardant l’égalité",
            "x = 8",
            "ne traite pas les équations à plusieurs étapes",
        ),
        ROOT / "apprendre" / "fiches" / "sciences-meteo-climat.html": (
            "Statut éditorial : Prototype à relire",
            "Distinguer météo et climat",
            "Une journée enneigée suffit-elle à établir une tendance",
            "ne suffit pas à établir une tendance climatique",
        ),
        ROOT / "apprendre" / "fiches" / "histoire-comparer-sources.html": (
            "Statut éditorial : Prototype à relire",
            "Comparer deux sources sur un même événement",
            "Les deux documents ne se contredisent pas forcément",
            "documents inventés",
        ),
        ROOT / "apprendre" / "fiches" / "info-bits-octets.html": (
            "Statut éditorial : Prototype à relire",
            "Comprendre les bits et les octets",
            "2 puissance 8 = 256 motifs possibles",
            "n’indique pas à lui seul une lettre",
        ),
        ROOT / "apprendre" / "fiches" / "prog-tester-exemples.html": (
            "Statut éditorial : Prototype à relire",
            "Tester un programme avec des cas simples",
            "Pour 0 : résultat attendu",
            "pseudo-code de cette fiche est fictif",
        ),
        ROOT / "apprendre" / "fiches" / "arts-composer-formes.html": (
            "Statut éditorial : Prototype à relire",
            "Composer une image avec quelques formes",
            "ne demande pas de reproduire une œuvre protégée",
            "description verbale",
        ),
        ROOT / "apprendre" / "fiches" / "fr-comprendre-mot-contexte.html": (
            "Statut éditorial : Prototype à relire",
            "Comprendre un mot grâce à son contexte",
            "Le contexte suggère parfois un sens sans permettre de le confirmer",
            "la feuille jaune est tombée de la branche",
        ),
        ROOT / "apprendre" / "fiches" / "maths-lire-echelle-graphique.html": (
            "Statut éditorial : Prototype à relire",
            "Lire les graduations d’un graphique",
            "graduations régulièrement espacées",
            "un axe qui commence à 4 peut amplifier visuellement une différence",
        ),
        ROOT / "apprendre" / "fiches" / "sciences-calculer-vitesse-moyenne.html": (
            "Statut éditorial : Prototype à relire",
            "Calculer une vitesse moyenne simple",
            "18 m ÷ 3 s = 6 m/s",
            "ne dit pas à quelle vitesse l’objet allait à chaque instant",
        ),
        ROOT / "apprendre" / "fiches" / "sciences-distinguer-melange-changement-etat.html": (
            "Statut éditorial : Prototype à relire",
            "Distinguer fusion et dissolution",
            "La fusion est un changement d’état",
            "Aucun mélange réel n’est demandé",
        ),
        ROOT / "apprendre" / "fiches" / "geo-decrire-paysage.html": (
            "Statut éditorial : Prototype à relire",
            "Décrire un paysage sans lui faire dire trop",
            "ne donne ni le nombre d’habitants",
            "description écrite entièrement fictive",
        ),
        ROOT / "apprendre" / "fiches" / "info-lire-adresse-web.html": (
            "Statut éditorial : Prototype à relire",
            "Repérer les parties d’une adresse Web",
            "https://site-fictif.test/agenda?jour=mardi",
            "HTTPS seul n’atteste pas",
            "Aucun lien réel n’est à ouvrir",
        ),
        ROOT / "apprendre" / "fiches" / "arts-lire-cartel.html": (
            "Statut éditorial : Prototype à relire",
            "Lire une notice d’œuvre en séparant faits et interprétations",
            "La notice indique le titre",
            "l’artiste",
            "notice entièrement fictive",
        ),
        ROOT / "apprendre" / "fiches" / "recherche-question-hypothese.html": (
            "Statut éditorial : Prototype à relire",
            "Formuler une question et une hypothèse de recherche",
            "une prédiction à examiner, pas un résultat établi",
            "Aucun essai réel n’est demandé",
        ),
        ROOT / "apprendre" / "fiches" / "fr-lire-ponctuation.html": (
            "Statut éditorial : Prototype à relire",
            "Lire la ponctuation pour comprendre une phrase",
            "le point d’interrogation invite le plus clairement à répondre",
            "Le signe seul ne permet pas de savoir",
            "ne traite pas la virgule",
        ),
        ROOT / "apprendre" / "fiches" / "langue-anglais-epeler.html": (
            "Statut éditorial : Prototype à relire",
            "Demander comment épeler un mot en anglais",
            "How do you spell Maya?",
            "Could you spell that, please?",
            "ne fournit pas d’audio",
        ),
        ROOT / "apprendre" / "fiches" / "maths-lire-tableau-croise.html": (
            "Statut éditorial : Prototype à relire",
            "Lire une information à l’intersection d’un tableau",
            "salle A l’après-midi",
            "la ligne Mardi croisée avec la colonne Matin",
            "Un tableau organisé ne garantit pas que les données sont exactes ou complètes",
        ),
        ROOT / "apprendre" / "fiches" / "maths-reperer-angle-droit.html": (
            "Statut éditorial : Prototype à relire",
            "Repérer un angle droit",
            "angle de 90 degrés",
            "L’ouverture compte, pas la longueur des côtés",
            "une comparaison visuelle ne remplace pas une mesure précise",
        ),
        ROOT / "apprendre" / "fiches" / "sciences-cycle-vie-plante.html": (
            "Statut éditorial : Prototype à relire",
            "Repérer les grandes étapes de vie d’une plante à fleurs",
            "une graine germe, devient une jeune pousse",
            "Les cycles et modes de reproduction varient selon les espèces",
            "ne s’applique pas à toutes les formes de vie végétale",
        ),
        ROOT / "apprendre" / "fiches" / "geo-lire-legende-carte.html": (
            "Statut éditorial : Prototype à relire",
            "Lire une légende sur une carte",
            "La légende explique les symboles choisis pour une carte donnée",
            "ne donne aucun itinéraire",
            "ni sa sécurité, ni son accessibilité",
        ),
        ROOT / "apprendre" / "fiches" / "histoire-situer-siecle.html": (
            "Statut éditorial : Prototype à relire",
            "Situer une année dans un siècle",
            "1789 est dans le XVIIIe siècle",
            "1900 est la dernière année du XIXe siècle",
            "ne couvre pas les dates avant notre ère",
        ),
        ROOT / "apprendre" / "fiches" / "info-systeme-exploitation.html": (
            "Statut éditorial : Prototype à relire",
            "Comprendre le rôle d’un système d’exploitation",
            "Le système d’exploitation fournit des fonctions de base",
            "ne décrit pas comment installer, mettre à jour, réparer ou modifier un système",
        ),
        ROOT / "apprendre" / "fiches" / "numerique-formuler-recherche.html": (
            "Statut éditorial : Prototype à relire",
            "Formuler une recherche sur le Web",
            "L’ordre des résultats ne prouve ni leur exactitude ni leur indépendance",
            "Ne partage pas une donnée personnelle",
            "ne promet pas une syntaxe universelle",
        ),
        ROOT / "apprendre" / "fiches" / "recherche-conserver-reference.html": (
            "Statut éditorial : Prototype à relire",
            "Garder la trace d’une source pour la retrouver",
            "Observatoire des jardins-exemple",
            "une référence n’est ni une preuve automatique ni une permission de reproduire le contenu",
            "cette fiche ne définit pas de format officiel",
        ),
        ROOT / "apprendre" / "fiches" / "civ-trouver-service-public.html": (
            "Statut éditorial : Prototype à relire",
            "Trouver un service public et préparer un formulaire",
            "maj-adresse-officiel.exemple",
            "cette fiche n’ouvre aucun droit",
            "service-public.gouv.fr",
        ),
        ROOT / "apprendre" / "fiches" / "info-table-requete-web.html": (
            "Statut éditorial : Prototype à relire",
            "Distinguer une table, une requête et une page Web",
            "Atelier des cartes",
            "cette fiche n’enseigne ni langage ni procédure",
            "data.gouv.fr",
        ),
        ROOT / "apprendre" / "fiches" / "prog-lire-licence-logiciel.html": (
            "Statut éditorial : Prototype à relire",
            "Lire une licence avant de réutiliser un programme",
            "horloge-exemple",
            "cette fiche n’est pas un avis juridique",
            "opensource.org/osd",
        ),
        ROOT / "apprendre" / "fiches" / "civ-reperer-echelle-institution.html": (
            "Statut éditorial : Prototype à relire",
            "Repérer l’échelle d’une institution avant de chercher le bon service",
            "médiathèque de quartier",
            "cette fiche n’ouvre aucun droit",
            "vie-publique.fr/fiches",
        ),
        ROOT / "apprendre" / "fiches" / "econ-lire-mention-garantie.html": (
            "Statut éditorial : Prototype à relire",
            "Lire une mention de garantie sur un ticket fictif",
            "Magasin-exemple",
            "cette fiche n’est pas un conseil juridique",
            "signal.conso.gouv.fr",
        ),
        ROOT / "apprendre" / "fiches" / "civ-reperer-info-electorale.html": (
            "Statut éditorial : Prototype à relire",
            "Repérer une information électorale officielle",
            "Votez demain, cliquez ici",
            "cette fiche n’indique pas pour qui voter",
            "vie-publique.fr/fiches",
        ),
        ROOT / "apprendre" / "fiches" / "econ-distinguer-interet-frais.html": (
            "Statut éditorial : Prototype à relire",
            "Distinguer un intérêt d’un frais sur un crédit fictif",
            "Prêt-exemple",
            "cette fiche n’est pas un conseil financier",
            "banque-france.fr",
        ),
        ROOT / "apprendre" / "fiches" / "langue-reperer-mot-deja-connu.html": (
            "Statut éditorial : Prototype à relire",
            "Reconnaître un mot que tu connais déjà sur une affiche bilingue",
            "Affiche-exemple",
            "cette fiche n’enseigne pas une langue entière",
            "culture.gouv.fr",
        ),
        ROOT / "apprendre" / "fiches" / "recherche-distinguer-resume-citation.html": (
            "Statut éditorial : Prototype à relire",
            "Distinguer un résumé et une citation sur une fiche fictive",
            "Carte-exemple",
            "cette fiche n’est pas un cours universitaire",
            "hal.science",
        ),
        ROOT / "apprendre" / "fiches" / "histoire-reperer-echelle-france-monde.html": (
            "Statut éditorial : Prototype à relire",
            "Repérer l’échelle d’un événement : un lieu de France ou plusieurs pays",
            "Frise-exemple",
            "cette fiche n’enseigne pas une histoire de France ni du monde",
            "vie-publique.fr/fiches",
        ),
        ROOT / "apprendre" / "fiches" / "sante-reperer-source-publique.html": (
            "Statut éditorial : Prototype à relire",
            "Repérer une source de santé publique avant d’agir",
            "Message-exemple",
            "cette fiche n’est pas un conseil médical",
            "sante.gouv.fr",
        ),
        ROOT / "docs" / "apprentissage" / "grille-relecture.md": (
            "Dossier en cours — `recherche-lire-etude`",
            "ne pas considérer comme validé ni prêt à la diffusion publique",
            "Dossiers en cours — prototypes de mathématiques",
            "Dossiers en cours — cinq prototypes informatique, techniques et civiques",
            "Dossier en cours — `econ-lire-facture`",
            "Dossier en cours — `econ-comparer-prix-unitaires`",
            "Dossiers en cours — sept prototypes de lecture, langues, repères et autonomie",
            "Dossiers en cours — huit prototypes de communication, sciences, histoire, informatique et arts",
            "Dossiers en cours — huit prototypes de français, mathématiques, sciences, géographie, Web, arts et recherche",
            "Dossiers en cours — dix prototypes de français, anglais, mathématiques, sciences, géographie, informatique et recherche",
            "La couverture de `factures-abonnements` reste partielle",
            f"Pour l’ensemble des {NOMBRES_EN_LETTRES.get(totaux_catalogue()[2], totaux_catalogue()[2])} prototypes décrits ici",
            "consigner une trace de décision séparée dans",
            f"range les {totaux_catalogue()[2]} prototypes par domaine",
            "python3 outils/registre-relecture.py",
            "un statut ne se déclare pas",
            "Une revue interne de cohérence des 26 prototypes alors présents",
            "Les huit fiches ajoutées dans le lot suivant, les dix fiches du lot suivant et les prototypes du 15 octobre 2026 ne sont pas couvertes par cette revue",
            "fr-reperer-idee-texte",
            "langue-anglais-demander-aide",
            "geo-points-cardinaux",
            "histoire-lire-frise",
            "maths-probabilite-tirage",
            "numerique-organiser-fichiers",
            "methodes-demander-clarification",
            "fr-preparer-explication-orale",
            "fr-argumenter-avec-exemple",
            "maths-equation-simple",
            "sciences-meteo-climat",
            "histoire-comparer-sources",
            "info-bits-octets",
            "prog-tester-exemples",
            "arts-composer-formes",
            "fr-comprendre-mot-contexte",
            "maths-lire-echelle-graphique",
            "sciences-calculer-vitesse-moyenne",
            "sciences-distinguer-melange-changement-etat",
            "geo-decrire-paysage",
            "info-lire-adresse-web",
            "arts-lire-cartel",
            "recherche-question-hypothese",
            "fr-lire-ponctuation",
            "langue-anglais-epeler",
            "maths-lire-tableau-croise",
            "maths-reperer-angle-droit",
            "sciences-cycle-vie-plante",
            "geo-lire-legende-carte",
            "histoire-situer-siecle",
            "info-systeme-exploitation",
            "numerique-formuler-recherche",
            "recherche-conserver-reference",
            "prog-comparer-langages",
            "aucun essai apprenant ou contrôle visuel en vrai navigateur n’a encore été réalisé",
        ),
        ROOT / "docs" / "apprentissage" / "objectif-1000.md": (
            "1 000 fiches d’auto-apprentissage",
            f"{totaux_catalogue()[0]} entrées",
            f"{totaux_catalogue()[2]} prototypes explicitement à relire",
            f"{1000 - totaux_catalogue()[0]} entrées",
            "aucun lien, compte ou service externe n’est requis",
        ),
        ROOT / "docs" / "rd-parcours-apprentissage.md": (
            "docs/apprentissage/grille-relecture.md",
            "la date de contrôle des droits, le mode d’utilisation et une description de cette utilisation",
            f"{totaux_catalogue()[0]} fiches suivies dans 15 domaines",
            f"{totaux_catalogue()[2]} prototypes explicitement à relire",
            "33 fiches de développement produites en quatre lots de 7, 8, 8 et 10",
            "ponctuation, épellation, géométrie, biologie, cartographie, repères historiques, systèmes d’exploitation et recherche documentaire",
            "fr-reperer-idee-texte",
            "langue-anglais-demander-aide",
            "geo-points-cardinaux",
            "histoire-lire-frise",
            "maths-probabilite-tirage",
            "numerique-organiser-fichiers",
            "methodes-demander-clarification",
            "fr-preparer-explication-orale",
            "fr-argumenter-avec-exemple",
            "maths-equation-simple",
            "sciences-meteo-climat",
            "histoire-comparer-sources",
            "info-bits-octets",
            "prog-tester-exemples",
            "arts-composer-formes",
            "fr-comprendre-mot-contexte",
            "maths-lire-echelle-graphique",
            "sciences-calculer-vitesse-moyenne",
            "sciences-distinguer-melange-changement-etat",
            "geo-decrire-paysage",
            "info-lire-adresse-web",
            "arts-lire-cartel",
            "recherche-question-hypothese",
            "fr-lire-ponctuation",
            "langue-anglais-epeler",
            "maths-lire-tableau-croise",
            "maths-reperer-angle-droit",
            "sciences-cycle-vie-plante",
            "geo-lire-legende-carte",
            "histoire-situer-siecle",
            "info-systeme-exploitation",
            "numerique-formuler-recherche",
            "recherche-conserver-reference",
            "econ-lire-facture",
            "econ-comparer-prix-unitaires",
            "le budget/prix comme les factures/abonnements sont partiels",
            "Le premier lot de développement (sept fiches",
            "Le lot de huit fiches de communication, sciences, histoire, informatique et arts",
            "Le lot suivant de huit fiches",
            "Les dix fiches du présent lot (`fr-lire-ponctuation`, `langue-anglais-epeler`, `maths-lire-tableau-croise`, `maths-reperer-angle-droit`, `sciences-cycle-vie-plante`, `geo-lire-legende-carte`, `histoire-situer-siecle`, `info-systeme-exploitation`, `numerique-formuler-recherche`, `recherche-conserver-reference`)",
            "Première couverture informatique, programmation, électricité et électronique",
            "docs/apprentissage/sources-utilite-publique.md",
            "les deux se sont terminées sans erreur et ont produit les mêmes trois lignes",
        ),
        ROOT / "docs" / "apprentissage" / "revue-interne-prototypes-2026-10-11.md": (
            "relecture interne de cohérence menée par l’agent",
            "les 26 fiches du catalogue",
            "les 26 fiches restent des prototypes non validés",
            "Les huit fiches ajoutées après cette relecture",
            "fr-comprendre-mot-contexte",
            "maths-lire-echelle-graphique",
            "sciences-calculer-vitesse-moyenne",
            "sciences-distinguer-melange-changement-etat",
            "geo-decrire-paysage",
            "info-lire-adresse-web",
            "arts-lire-cartel",
            "recherche-question-hypothese",
            "Python et JavaScript ont été exécutés séparément",
            "maths-probabilite-tirage",
            "sciences-meteo-climat",
            "arts-composer-formes",
            "Les liens externes n’ont pas été visités ou vérifiés un à un",
            "aucun droit de réutilisation n’est certifié",
            "Les validations visuelles, clavier/lecteur d’écran et essais avec des personnes apprenantes n’ont pas été réalisés",
            "recherche-lire-etude",
            "maths-convertir-unites",
            "maths-moyenne",
            "maths-estimer-calcul",
            "info-ordinateur-fonctions",
            "prog-comparer-langages",
            "tech-circuit-ouvert-ferme",
            "tech-electronique-capteur",
            "civ-choisir-source-publique",
            "econ-lire-facture",
            "econ-comparer-prix-unitaires",
            "fr-reperer-idee-texte",
            "langue-anglais-demander-aide",
            "geo-points-cardinaux",
            "histoire-lire-frise",
            "maths-probabilite-tirage",
            "numerique-organiser-fichiers",
            "methodes-demander-clarification",
            "fr-preparer-explication-orale",
            "fr-argumenter-avec-exemple",
            "maths-equation-simple",
            "sciences-meteo-climat",
            "histoire-comparer-sources",
            "info-bits-octets",
            "prog-tester-exemples",
            "arts-composer-formes",
        ),
        ROOT / "docs" / "rd-coherence-visuelle-editoriale.md": (
            f"{totaux_catalogue()[0]} entrées : {totaux_catalogue()[1]} fiches du corpus initial et {totaux_catalogue()[2]} prototypes explicitement à relire",
            "la relecture indépendante de toutes les fiches initiales n’est pas garantie",
            "33 fiches de développement réparties en quatre lots ouvrent des points d’entrée",
            f"{totaux_catalogue()[0]} pages générées, dont {NOMBRES_EN_LETTRES.get(totaux_catalogue()[2], totaux_catalogue()[2])} prototypes à relire",
        ),
        ROOT / "docs" / "apprentissage" / "sources-utilite-publique.md": (
            "Consultation documentaire : 8 octobre 2026",
            "conditions de réutilisation non vérifiées",
            "aucun texte, visuel, donnée ou extrait n’a été repris",
            "https://docs.python.org/fr/3/tutorial/",
            "[MDN — boucles JavaScript](https://developer.mozilla.org/fr/",
        ),
        ROOT / "assets" / "css" / "site.css": (
            ".site-status-note",
            "html.contraste-renforce .site-status-note",
            ".learning-code-sample pre:focus-visible",
            "overscroll-behavior-inline:contain",
            "@media (forced-colors: active)",
            "background:Canvas !important; color:CanvasText !important",
            "resource-scope-note",
        ),
    }
    for chemin, expressions in controles.items():
        relatif = chemin.relative_to(ROOT).as_posix()
        try:
            contenu = chemin.read_text(encoding="utf-8")
        except (OSError, UnicodeError) as erreur:
            signaler(f"{relatif} : contrôle du prototype impossible : {erreur}")
            continue
        absentes = [expression for expression in expressions if expression.casefold() not in contenu.casefold()]
        if absentes:
            signaler(f"{relatif} : état de relecture/droits absent : {'; '.join(absentes)}")
    catalogue_path = ROOT / "apprendre.html"
    if catalogue_path.is_file():
        catalogue_html = catalogue_path.read_text(encoding="utf-8")
        filtre = re.search(r'<select id="matiere-fiches"[^>]*>(.*?)</select>', catalogue_html, re.DOTALL)
        if not filtre:
            signaler("apprendre.html : filtre des matières absent")
        else:
            valeurs = re.findall(r'<option\s+value="([^"]*)">', filtre.group(1))
            if len(valeurs) != len(set(valeurs)):
                signaler("apprendre.html : une matière apparaît plusieurs fois dans le filtre")
    if not ERREURS:
        print("R&D apprentissages : objectif 1 000, autonomie, statut du prototype et grille de relecture vérifiés.")


def verifier_note_rnd() -> None:
    """Vérifie que chaque page publique signale son statut de développement sans JavaScript."""
    marqueur = re.compile(
        r'<p\b(?=[^>]*\bclass="site-status-note")(?=[^>]*\brole="note")[^>]*>\s*'
        r"Version R&amp;D — le site est en cours de développement\."
        r"\s*</p>",
        flags=re.IGNORECASE | re.DOTALL,
    )
    avant = len(ERREURS)
    for chemin in PAGES:
        if not chemin.is_file():
            signaler(f"{chemin.relative_to(ROOT)} : page requise pour la note R&D absente")
            continue
        try:
            contenu = chemin.read_text(encoding="utf-8")
        except (OSError, UnicodeError) as erreur:
            signaler(f"{chemin.relative_to(ROOT)} : lecture de la note R&D impossible : {erreur}")
            continue
        if not marqueur.search(contenu):
            signaler(f"{chemin.relative_to(ROOT)} : note de version R&D absente de l’entête")
    if len(ERREURS) == avant:
        print(f"Note de version R&D : présente dans les {len(PAGES)} pages publiques, sans dépendre de JavaScript.")


def verifier_registres_sans_references_retirees() -> None:
    """Évite le retour accidentel de références sociales supprimées dans le site et la traçabilité."""
    motif = re.compile(r"face[\s-]?book", re.IGNORECASE)
    candidats = set(PAGES)
    dossier = ROOT / "docs"
    if dossier.exists():
        candidats.update(dossier.rglob("*.md"))
        candidats.update(dossier.rglob("*.toml"))
    avant = len(ERREURS)
    for chemin in sorted(candidats):
        try:
            contenu = chemin.read_text(encoding="utf-8")
        except (OSError, UnicodeError) as erreur:
            signaler(f"{chemin.relative_to(ROOT)} : lecture du registre impossible : {erreur}")
            continue
        if motif.search(contenu):
            signaler(f"{chemin.relative_to(ROOT)} : référence sociale retirée détectée dans le site ou un registre")
    if len(ERREURS) == avant:
        print("Registres éditoriaux : aucune référence sociale retirée dans les pages et documents contrôlés.")


def verifier_espaces_finaux(fichiers: list[Path]) -> None:
    for chemin in fichiers:
        relatif = chemin.relative_to(ROOT).as_posix()
        try:
            lignes = chemin.read_text(encoding="utf-8").splitlines()
        except (OSError, UnicodeError) as erreur:
            signaler(f"{relatif} : contrôle des espaces finaux impossible : {erreur}")
            continue
        for numero, ligne in enumerate(lignes, 1):
            if ligne.endswith((" ", "\t")):
                signaler(f"{relatif}:{numero} : espace final")
    if not ERREURS:
        print(f"Espaces de fin de ligne : aucun espace final sur {len(fichiers)} pages HTML.")


def verifier_collecte_navigateur_bornee() -> None:
    chemin = ROOT / "simulateur" / "interface.py"
    contenu = chemin.read_text(encoding="utf-8")
    marqueurs = (
        "const LIMITE_JSON_SOURCE_NAVIGATEUR = 8_388_608;",
        "const DELAI_SOURCE_NAVIGATEUR_MS = 8_000;",
        "const DELAI_COLLECTE_NAVIGATEUR_MS = 60_000;",
        "async function fetchJsonSourceBorne(",
        "new AbortController()",
        "redirect:'error'",
        "reponse.body.getReader()",
        "await lecteur.cancel()",
        "fetchJsonSourceBorne(\n          source.url",
        "fetchJsonSourceBorne(\n          indicateur.proxy_url",
    )
    sans_fetch_direct_non_borne = (
        "await fetch(source.url" not in contenu
        and "await fetch(indicateur.proxy_url" not in contenu
    )
    if not all(marqueur in contenu for marqueur in marqueurs) or not sans_fetch_direct_non_borne:
        signaler("simulateur/interface.py : collecte navigateur sans limites de taille/durée vérifiables")
    else:
        print("Collecte navigateur : redirections refusées, JSON plafonné à 8 Mio, 8 s par requête et 60 s par cycle.")


def verifier_affichage_provenance_sans_injection() -> None:
    interface = (ROOT / "simulateur" / "interface.py").read_text(encoding="utf-8")
    donnees = (ROOT / "simulateur" / "donnees_live.py").read_text(encoding="utf-8")
    marqueurs_interface = (
        "${echapperTexte(sous)}",
        "Object.prototype.hasOwnProperty.call(libelles, mode)",
        "période ${echapperTexte(info.periode)}",
        "collecté le ${echapperTexte(info.date_collecte)}",
        "qualité : ${echapperTexte(info.qualite)}",
    )
    marqueurs_serveur = (
        "def _periode_sure(valeur: Any)",
        "def _code_qualite_sure(valeur: Any)",
        "_horodatage_sure(lecture.horodatage)[:10]",
    )
    if not all(marqueur in interface for marqueur in marqueurs_interface) or not all(
        marqueur in donnees for marqueur in marqueurs_serveur
    ):
        signaler("simulateur : provenance externe non neutralisée avant affichage HTML")
    else:
        print("Provenance externe : périodes, dates et qualités neutralisées côté serveur et échappées au rendu.")


def verifier_limites_requetes_api() -> None:
    dashboard = (ROOT / "simulateur" / "dashboard.py").read_text(encoding="utf-8")
    wsgi = (ROOT / "simulateur" / "wsgi.py").read_text(encoding="utf-8")
    marqueurs_dashboard = (
        "MAX_REQUEST_TARGET_BYTES = 16_384",
        "MAX_QUERY_FIELDS = 128",
        "parse_qs(parsed.query, max_num_fields=MAX_QUERY_FIELDS)",
        "len(cles_brutes) > MAX_BULLES_PAR_REQUETE",
        "cles = list(dict.fromkeys(cles_brutes)) or None",
        "raise RequetesBullesOccupees",
    )
    marqueurs_wsgi = (
        "longueur_cible = len(chemin) + (1 + len(query) if query else 0)",
        "longueur_cible > MAX_REQUEST_TARGET_BYTES",
    )
    if not all(marqueur in dashboard for marqueur in marqueurs_dashboard) or not all(
        marqueur in wsgi for marqueur in marqueurs_wsgi
    ):
        signaler("simulateur : limites de cible HTTP ou calcul de bulles concurrent absents")
    else:
        print("API simulateur : cible limitée à 16 Kio, 128 champs et calculs de bulles sérialisés par processus.")


def main() -> int:
    fichiers = [chemin for chemin in PAGES if chemin.is_file()]
    if not fichiers:
        signaler("aucune page HTML publique trouvée")
        return 1
    infos = {chemin: analyser(chemin) for chemin in fichiers}
    verifier_espaces_finaux(fichiers)
    verifier_liens(infos)
    verifier_entrees_accueil()
    verifier_dependances_apprentissage()
    verifier_catalogue_apprentissage()
    verifier_dossier_apprentissage()
    verifier_aventure_anglais()
    verifier_note_rnd()
    verifier_registres_sans_references_retirees()
    verifier_collecte_navigateur_bornee()
    verifier_affichage_provenance_sans_injection()
    verifier_limites_requetes_api()
    verifier_metadonnees(infos)
    verifier_llms_txt()
    verifier_sitemap()
    verifier_javascript(infos)
    print(f"Pages contrôlées : {len(fichiers)} (dont {len(list((ROOT / 'apprendre' / 'fiches').glob('*.html')))} fiches autonomes).")
    if ERREURS:
        print(f"{len(ERREURS)} problème(s) détecté(s).")
        return 1
    print("Liens locaux, ancres, attributs essentiels et scripts : contrôles réussis.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
