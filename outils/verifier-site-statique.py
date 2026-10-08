#!/usr/bin/env python3
"""Contrôles hors ligne des pages statiques, liens locaux et scripts JavaScript.

Ce vérificateur n'effectue aucune requête vers un site externe. Il contrôle les
pages déployées (et les fiches autonomes), les références locales, les ancres,
quelques relations d'accessibilité et la syntaxe JS disponible via Node.js.
"""
from __future__ import annotations

import re
import shutil
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parent.parent
PAGES = sorted(ROOT.glob("*.html"))
PAGES.extend(sorted((ROOT / "apprendre" / "fiches").glob("*.html")))
PAGES.append(ROOT / "simulateur" / "index.html")
ERREURS: list[str] = []


@dataclass
class PageInfo:
    chemin: Path
    ids: set[str] = field(default_factory=set)
    doublons: set[str] = field(default_factory=set)
    references: list[tuple[str, str, int]] = field(default_factory=list)
    relations: list[tuple[str, str, int]] = field(default_factory=list)
    langues: list[str] = field(default_factory=list)
    titres: int = 0
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

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attributs = dict(attrs)
        ligne = self.getpos()[0]
        if tag == "html":
            langue = (attributs.get("lang") or "").strip()
            if langue:
                self.info.langues.append(langue)
        if tag == "title":
            self.info.titres += 1
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
            self.script_type = (attributs.get("type") or "text/javascript").lower()
            self.script_src = bool(attributs.get("src"))
            self.script_lines = []

    def handle_data(self, data: str) -> None:
        if self.script_number and not self.script_src:
            self.script_lines.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag == "script" and self.script_number and not self.script_src:
            if self.script_type in ("text/javascript", "application/javascript", "module"):
                self.info.scripts.append((f"{self.info.chemin.relative_to(ROOT)}:script-{self.script_number}", "".join(self.script_lines)))
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


def verifier_dependances_apprentissage() -> None:
    pages = [ROOT / "apprendre.html", *sorted((ROOT / "apprendre" / "fiches").glob("*.html"))]
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


def verifier_dossier_apprentissage() -> None:
    controles = {
        ROOT / "apprendre.html": (
            "26 fiches et 9 prototypes à relire",
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
        ROOT / "docs" / "apprentissage" / "grille-relecture.md": (
            "Dossier en cours — `recherche-lire-etude`",
            "ne pas considérer comme validé ni prêt à la diffusion publique",
            "Dossiers en cours — prototypes de mathématiques",
            "Dossiers en cours — cinq prototypes informatique, techniques et civiques",
            "prog-comparer-langages",
            "aucun essai apprenant ou contrôle visuel en vrai navigateur n’a encore été réalisé",
        ),
        ROOT / "docs" / "apprentissage" / "objectif-1000.md": (
            "1 000 fiches d’auto-apprentissage",
            "cible, pas catalogue disponible",
            "aucun lien, compte ou service externe n’est requis",
        ),
        ROOT / "docs" / "rd-parcours-apprentissage.md": (
            "docs/apprentissage/grille-relecture.md",
            "la date de contrôle des droits, le mode d’utilisation et une description de cette utilisation",
            "35 fiches suivies dans 15 domaines",
            "9 fiches explicitement marquées",
            "Première couverture informatique, programmation, électricité et électronique",
            "docs/apprentissage/sources-utilite-publique.md",
            "les deux se sont terminées sans erreur et ont produit les mêmes trois lignes",
        ),
        ROOT / "docs" / "apprentissage" / "sources-utilite-publique.md": (
            "Consultation documentaire : 8 octobre 2026",
            "conditions de réutilisation non vérifiées",
            "aucun texte, visuel, donnée ou extrait n’a été repris",
            "https://docs.python.org/fr/3/tutorial/",
            "[MDN — boucles JavaScript](https://developer.mozilla.org/fr/",
        ),
        ROOT / "assets" / "css" / "site.css": (
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
    if not ERREURS:
        print("R&D apprentissages : objectif 1 000, autonomie, statut du prototype et grille de relecture vérifiés.")


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


def main() -> int:
    fichiers = [chemin for chemin in PAGES if chemin.is_file()]
    if not fichiers:
        signaler("aucune page HTML publique trouvée")
        return 1
    infos = {chemin: analyser(chemin) for chemin in fichiers}
    verifier_espaces_finaux(fichiers)
    verifier_liens(infos)
    verifier_dependances_apprentissage()
    verifier_dossier_apprentissage()
    verifier_registres_sans_references_retirees()
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
