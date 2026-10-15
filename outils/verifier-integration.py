#!/usr/bin/env python3
"""Vérifie l'intégration du simulateur au site M.R.S.C, sans navigateur.

Contrôles effectués :

1. la page publiée `simulateur/index.html` est à jour par rapport au moteur ;
2. les fonctions de `api/` correspondent exactement aux routes du moteur ;
3. **chaque fonction sert bien sa route** : le gestionnaire de `api/*.py` est
   monté dans un serveur local, comme le fait Vercel, puis interrogé ;
4. les pages du site, `404.html`, `assets/` et les liens de navigation sont
   présents ;
5. la fonction `api/verifier-source.py` (source distante du simulateur) répond
   correctement, sur une source simulée puis sur une source injoignable ;
6. les consignes, skills, portefeuille et veille R&D continue restent cohérents.

Usage :
    python3 outils/verifier-integration.py
"""

from __future__ import annotations

import contextlib
import importlib.util
import io
import json
import os
import re
import subprocess
import sys
import threading
import tomllib
import urllib.error
import urllib.request
from html import unescape
from http.server import ThreadingHTTPServer
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RACINE))
from simulateur.dashboard import SCENARIOS as SCENARIOS_MOTEUR  # noqa: E402
from simulateur.donnees_live import INDICATEURS as INDICATEURS_MOTEUR  # noqa: E402
from simulateur.domaines import DOMAINES as DOMAINES_MOTEUR  # noqa: E402
from simulateur.parametres import LEVIERS as LEVIERS_MOTEUR  # noqa: E402

#: Sortie réelle : le moteur est bavard, ses impressions sont mises de côté.
SORTIE = sys.stdout


def dire(message: str) -> None:
    SORTIE.write(message + "\n")
    SORTIE.flush()


def charger_module(chemin: Path, nom: str):  # noqa: ANN201 - module dynamique
    """Charge un script par son chemin (les noms des outils contiennent des tirets)."""
    specification = importlib.util.spec_from_file_location(nom, chemin)
    module = importlib.util.module_from_spec(specification)
    specification.loader.exec_module(module)
    return module


#: Routes exposées dans api/, telles que les connaît le générateur de fonctions.
ROUTES: tuple[str, ...] = charger_module(
    RACINE / "outils" / "generer-fonctions-api.py", "generer_fonctions_api"
).ROUTES

PAGES = (
    "index.html",
    "apprendre.html",
    "anglais-aventure.html",
    "ia-societe.html",
    "eva.html",
    "simulateur.html",
    "documents.html",
    "liens-utiles.html",
    "localisation.html",
    "nous-contacter.html",
    "transparence.html",
    "confidentialite.html",
    "404.html",
)

#: Statuts acceptés par route : une route paramétrée sans paramètre répond 400,
#: c'est le comportement voulu, pas une panne.
STATUTS_ACCEPTES: dict[str, tuple[int, ...]] = {
    "bulle": (200, 400),
    "donnees": (200, 400),
    "proxy": (200, 400),
}

#: Routes interrogées telles que la page publiée le fait, et statut attendu.
ROUTES_TESTS: dict[str, tuple[str, int]] = {
    "/api/catalogue": ("", 200),
    "/api/contexte": ("?refresh=0", 200),
    "/api/marches": ("", 200),
    "/api/presets": ("", 200),
    "/api/scenarios": ("", 200),
    "/api/simuler": ("", 200),
    "/api/comparer": ("", 200),
    "/api/garde_fous": ("", 200),
    "/api/lexique": ("", 200),
    "/api/run?scenario=mandature": ("", 200),
    "/api/bulle?levier=tva_taux_normal": ("", 200),
}

echecs: list[str] = []


def verifier(libelle: str, condition: bool, detail: str = "") -> None:
    dire(f"{'OK   ' if condition else 'ÉCHEC'} {libelle}" + (f" — {detail}" if detail else ""))
    if not condition:
        echecs.append(libelle)


def rapport_contraste(couleur_texte: str, couleur_fond: str) -> float:
    """Calcule le rapport WCAG d’une paire hexadécimale sRGB opaque."""
    def luminance(couleur: str) -> float:
        valeurs = [int(couleur[index:index + 2], 16) / 255 for index in (1, 3, 5)]
        composantes = [
            valeur / 12.92 if valeur <= 0.04045 else ((valeur + 0.055) / 1.055) ** 2.4
            for valeur in valeurs
        ]
        return 0.2126 * composantes[0] + 0.7152 * composantes[1] + 0.0722 * composantes[2]

    claire, sombre = sorted((luminance(couleur_texte), luminance(couleur_fond)), reverse=True)
    return (claire + 0.05) / (sombre + 0.05)


def lancer(script: str, *arguments: str) -> tuple[int, str]:
    resultat = subprocess.run(
        [sys.executable, str(RACINE / "outils" / script), *arguments],
        cwd=RACINE,
        capture_output=True,
        text=True,
        timeout=600,
        check=False,
    )
    return resultat.returncode, (resultat.stdout or resultat.stderr).strip()


def page_a_jour() -> None:
    code, sortie = lancer("construire-simulateur.py", "--verifier")
    verifier("Page du simulateur à jour", code == 0, sortie.splitlines()[-1] if sortie else "")


def fonctions_conformes() -> None:
    code, sortie = lancer("generer-fonctions-api.py", "--verifier")
    verifier("Fonctions api/ conformes au moteur", code == 0, sortie.splitlines()[-1] if sortie else "")


def liens_et_scripts_statiques() -> None:
    code, sortie = lancer("verifier-site-statique.py")
    verifier("Liens locaux, ancres, repères HTML et syntaxe JavaScript", code == 0, sortie.splitlines()[-1] if sortie else "")


def recherche_developpement_continue() -> None:
    code, sortie = lancer("verifier-rd-continue.py")
    verifier(
        "Consignes, skills, portefeuille et veille R&D continue",
        code == 0,
        sortie.splitlines()[-1] if sortie else "",
    )


def fichiers_du_site() -> None:
    for page in PAGES:
        chemin = RACINE / page
        verifier(f"Page présente : {page}", chemin.is_file() and chemin.stat().st_size > 500)
    for ressource in ("assets/css/site.css", "assets/js/site.js", "assets/js/navigation-parcours.js", "assets/js/apprentissage.js", "assets/css/anglais-aventure.css", "assets/js/anglais-aventure-data.js", "assets/js/apprentissage-aventure-data.js", "assets/js/anglais-aventure.js", "assets/images/escales-anglais-hero.jpg", "assets/images/mondes-savoirs-hero.jpg", "assets/images/logo-mrsc.jpg", "assets/images/accueil-logo-mrsc-3d.jpg", "assets/images/favicon-32.png", "assets/images/apple-touch-icon.png", "favicon.ico", "llms.txt"):
        verifier(f"Ressource présente : {ressource}", (RACINE / ressource).is_file())
    catalogue_apprentissage = (RACINE / "apprendre.html").read_text(encoding="utf-8")
    page_aventure = (RACINE / "anglais-aventure.html").read_text(encoding="utf-8")
    donnees_apprentissage = (RACINE / "assets" / "js" / "apprentissage-aventure-data.js").read_text(encoding="utf-8")
    serveur_local = (RACINE / "outils" / "serveur-local.py").read_text(encoding="utf-8")
    publication = (RACINE / ".github" / "workflows" / "deploy-pages.yml").read_text(encoding="utf-8")
    sitemap = (RACINE / "sitemap.xml").read_text(encoding="utf-8")
    llms_txt = RACINE / "llms.txt"
    confidentialite = (RACINE / "confidentialite.html").read_text(encoding="utf-8")
    verifier(
        "Le jeu est relié au catalogue, au serveur local, au sitemap et à la publication",
        'href="anglais-aventure.html"' in catalogue_apprentissage
        and '"anglais-aventure.html"' in serveur_local
        and "cp index.html apprendre.html anglais-aventure.html" in publication
        and "/MRSC/anglais-aventure.html" in sitemap,
    )
    accueil = (RACINE / "index.html").read_text(encoding="utf-8")
    verifier(
        "Le sommaire llms.txt est lié depuis l’accueil, servi localement et publié",
        llms_txt.is_file()
        and '"llms.txt"' in serveur_local
        and "llms.txt" in publication
        and 'rel="describedby" href="llms.txt"' in accueil,
    )
    try:
        sources_fiches = tomllib.loads((RACINE / "docs" / "apprentissage" / "catalogue.toml").read_text(encoding="utf-8"))["fiche"]
        sources_domaines = tomllib.loads((RACINE / "docs" / "apprentissage" / "referentiel.toml").read_text(encoding="utf-8"))["domaine"]
        bloc_atlas = re.search(r"globalThis\.MRSCApprentissageData = Object\.freeze\((\{.*\})\);", donnees_apprentissage, re.DOTALL)
        atlas = json.loads(bloc_atlas.group(1)) if bloc_atlas else {}
        atlas_ids = [fiche.get("id") for fiche in atlas.get("sheets", [])]
        source_ids = [fiche.get("id") for fiche in sources_fiches]
        atlas_domain_ids = [domaine.get("id") for domaine in atlas.get("domains", [])]
        source_domain_ids = [domaine.get("id") for domaine in sources_domaines]
        atlas_fiches_valides = (
            atlas_ids == source_ids
            and atlas_domain_ids == source_domain_ids
            and atlas.get("sheetCount") == len(sources_fiches)
            and atlas.get("domainCount") == len(sources_domaines)
            and all((RACINE / fiche["url"]).is_file() for fiche in atlas.get("sheets", []))
            and sum(bool(fiche.get("editorialStatus")) for fiche in atlas.get("sheets", [])) == atlas.get("prototypeCount")
        )
    except (OSError, KeyError, TypeError, tomllib.TOMLDecodeError, json.JSONDecodeError):
        atlas_fiches_valides = False
        atlas = {}
    verifier(
        "L’atlas inclut toutes les fiches, tous les domaines et les statuts éditoriaux du catalogue",
        atlas_fiches_valides
        and 'assets/js/apprentissage-aventure-data.js' in page_aventure
        and 'id="learning-path-list"' in page_aventure,
        f"{atlas.get('sheetCount', 0)} fiches · {atlas.get('domainCount', 0)} mondes · {atlas.get('prototypeCount', 0)} prototypes à relire",
    )
    verifier(
        "La notice décrit le parcours local, sa suppression et l’absence de transmission des réponses libres",
        all(terme in confidentialite for terme in ("mrsc-anglais-aventure-v1", "identifiants des fiches ajoutées", "saisies librement"))
        and all(
            libelle in page_aventure and libelle in confidentialite
            for libelle in ("Effacer mon parcours local", "Effacer mon avancement local")
        ),
    )
    pages_avec_parcours = [RACINE / page for page in PAGES]
    pages_avec_parcours.append(RACINE / "simulateur" / "index.html")
    pages_avec_parcours.extend(sorted((RACINE / "apprendre" / "fiches").glob("*.html")))
    verifier(
        "Les commandes de parcours sont intégrées au site, aux fiches et au simulateur",
        all("navigation-parcours.js" in page.read_text(encoding="utf-8") for page in pages_avec_parcours if page.is_file()),
        f"{len(pages_avec_parcours)} pages contrôlées",
    )
    publiques = [page for page in PAGES if page != "404.html"]
    verifier(
        "Le simulateur est dans la navigation des pages",
        all('href="simulateur.html"' in (RACINE / page).read_text(encoding="utf-8") for page in publiques),
        f"{len(publiques)} pages publiques vérifiées",
    )
    verifier(
        "La page d’apprentissage est dans la navigation des pages",
        all('href="apprendre.html"' in (RACINE / page).read_text(encoding="utf-8") for page in publiques),
        f"{len(publiques)} pages publiques vérifiées",
    )
    verifier(
        "La notice vie privée est trouvable depuis chaque page publique",
        all('href="confidentialite.html"' in (RACINE / page).read_text(encoding="utf-8") for page in publiques),
        f"{len(publiques)} pages publiques vérifiées",
    )
    vie_privee = (RACINE / "confidentialite.html").read_text(encoding="utf-8")
    categories_rgpd = (
        "localStorage",
        "sessionStorage",
        "parcours de navigation",
        "adresse IP",
        "Google My Maps",
        "courriel",
        "base juridique",
        "durée de conservation",
        "Vercel",
    )
    verifier(
        "La notice distingue préférences locales, contact, hébergement et tiers",
        all(terme.casefold() in vie_privee.casefold() for terme in categories_rgpd),
        "9 catégories et réserves documentées",
    )
    localisation = (RACINE / "localisation.html").read_text(encoding="utf-8")
    iframe_carte = re.search(r"<iframe\b[^>]*>", localisation, flags=re.IGNORECASE)
    verifier(
        "La carte Google n’est pas chargée avant une action explicite",
        bool(iframe_carte)
        and "data-map-src=" in iframe_carte.group(0)
        and not re.search(r"(?:^|\s)src\s*=", iframe_carte.group(0), flags=re.IGNORECASE)
        and 'data-map-load' in localisation,
    )
    verifier(
        "Toutes les pages déclarent un viewport mobile sans bloquer le zoom",
        all(
            'name="viewport"' in (RACINE / page).read_text(encoding="utf-8")
            and "user-scalable=no" not in (RACINE / page).read_text(encoding="utf-8").lower()
            for page in PAGES
        ),
        f"{len(PAGES)} pages contrôlées",
    )
    attributs_affichage = (
        'data-display-settings',
        'data-text-decrease',
        'data-text-increase',
        'data-text-size-level',
        'data-contrast-toggle',
        'data-spacing-toggle',
    )
    verifier(
        "Les réglages d’affichage complets sont présents sur toutes les pages publiques",
        all(
            all(attribut in (RACINE / page).read_text(encoding="utf-8") for attribut in attributs_affichage)
            for page in PAGES
        ),
        f"{len(PAGES)} pages contrôlées, 404 comprise",
    )
    pages_avec_entete = [RACINE / page for page in PAGES] + sorted((RACINE / "apprendre" / "fiches").glob("*.html"))
    controles_entete = ("data-menu-toggle", "data-header-compact-toggle", "data-display-settings")
    entetes_adaptatives = True
    for chemin in pages_avec_entete:
        contenu = chemin.read_text(encoding="utf-8")
        positions = [contenu.find(attribut) for attribut in controles_entete]
        script_site_ref = os.path.relpath(RACINE / "assets" / "js" / "site.js", chemin.parent).replace(os.sep, "/")
        feuille_site_ref = os.path.relpath(RACINE / "assets" / "css" / "site.css", chemin.parent).replace(os.sep, "/")
        entetes_adaptatives = entetes_adaptatives and all(position >= 0 for position in positions)
        entetes_adaptatives = entetes_adaptatives and positions[0] < positions[1] < positions[2]
        entetes_adaptatives = entetes_adaptatives and f'<script src="{script_site_ref}" defer></script>' in contenu
        entetes_adaptatives = entetes_adaptatives and f'<link rel="stylesheet" href="{feuille_site_ref}">' in contenu
        entetes_adaptatives = entetes_adaptatives and all(
            marqueur in contenu
            for marqueur in (
                'id="site-header-status"',
                'id="site-header-identity"',
                'aria-controls="site-header-status site-header-identity"',
            )
        )
    verifier(
        "Le bouton Réduire/Agrandir est placé entre Menu et Affichage sur les pages et fiches",
        entetes_adaptatives,
        f"{len(pages_avec_entete)} pages/fiches contrôlées",
    )
    styles = (RACINE / "assets" / "css" / "site.css").read_text(encoding="utf-8")
    verifier(
        "Les flèches Affichage et Présentation changent de sens à l’ouverture",
        all(
            marqueur in styles
            for marqueur in (
                ".display-settings-chevron {\n  display: inline-block;",
                ".display-settings[open] > summary .display-settings-chevron { transform: rotate(180deg); }",
                ".layout-settings-chevron {\n  display: inline-block;",
                ".layout-settings[open] > summary .layout-settings-chevron { transform: rotate(180deg); }",
            )
        ),
    )
    medias_adaptatifs = (
        "@media (prefers-contrast: more)",
        "@media (forced-colors: active)",
        "@media (prefers-reduced-motion: reduce)",
        "@media (prefers-reduced-transparency: reduce)",
        "@media (orientation: landscape)",
        "@media (any-pointer: coarse)",
    )
    verifier(
        "Le CSS commun traite les principales préférences système et entrées",
        all(regle in styles for regle in medias_adaptatifs),
    )
    verifier(
        "Le CSS commun couvre les cinq niveaux de taille du texte de 50 % à 150 %",
        all(
            marqueur in styles
            for marqueur in (
                "html.texte-tres-reduit { font-size: 50%; }",
                "html.texte-reduit { font-size: 75%; }",
                "html.texte-agrandi { font-size: 125%; }",
                "html.texte-tres-agrandi { font-size: 150%; }",
                "font-size: max(12px,1em)",
                ".display-settings-panel .display-control",
            )
        ),
    )
    verifier(
        "Le panneau Affichage reste visible et défilable à largeur smartphone",
        "@media (max-width: 760px) {\n  html { scroll-padding-top: 13rem; }\n  .nav-inner { gap: clamp(6px,.5rem,10px); }\n  .display-settings { position: static; margin-left: 0; }\n  .display-settings-panel {\n    left: 0;\n    right: auto;" in styles
        and all(
            marqueur in styles
            for marqueur in (
                "width: min(24rem,calc(100vw - 1rem));",
                "max-height: min(32rem,calc(100dvh - 220px));",
                ".display-settings-panel { width: min(clamp(320px,24rem,400px),calc(100vw - 1rem)); }",
            )
        ),
    )
    verifier(
        "Le mode d’espacement atteint les repères WCAG 1.4.12",
        all(valeur in styles for valeur in ("line-height: 1.65", "margin-block-end: 2em", "letter-spacing: .12em", "word-spacing: .16em")),
    )
    parcours = (RACINE / "assets" / "js" / "navigation-parcours.js").read_text(encoding="utf-8")
    script_site = (RACINE / "assets" / "js" / "site.js").read_text(encoding="utf-8")
    test_experience = (RACINE / "outils" / "test-experience.cjs").read_text(encoding="utf-8")
    verifier(
        "Le réglage mémorise les cinq paliers et conserve les préférences historiques",
        "const textLevels = [50, 75, 100, 125, 150]" in script_site
        and "const legacyTextLevels = [100, 125, 150]" in script_site
        and "legacyTextLevels[parsed]" in script_site
        and 'readPreference("mrsc-texte-agrandi") === "oui" ? 125 : 100' in script_site
        and "savePreference(keys.text, String(textLevel))" in script_site,
    )
    verifier(
        "La navigation de bureau se replie à 125/150 % sans masquer les libellés",
        all(
            marqueur in styles
            for marqueur in (
                "@media (min-width: 1261px)",
                "html.has-js:is(.texte-agrandi,.texte-tres-agrandi) .nav-inner",
                "html.has-js:is(.texte-agrandi,.texte-tres-agrandi) .nav-toggle",
                "html.has-js:is(.texte-agrandi,.texte-tres-agrandi) .nav-links.is-open { display: flex; }",
                "min-height: 45px",
                "padding: clamp(6px,.4rem,8px) clamp(10px,.65rem,14px)",
                "white-space: normal",
            )
        ),
    )
    verifier(
        "La barre Menu/Réduire/Parcours/Affichage/Présentation forme un groupe centré et cohérent",
        ".nav-inner { justify-content: center; gap: clamp(6px,.5rem,10px); }" in styles
        and all(
            marqueur in styles
            for marqueur in (
                ".nav-toggle {\n  display: none;\n  flex: 0 0 auto;",
                ".header-compact-toggle {",
                ".site-journey-settings > summary {",
                ".display-settings > summary {",
                ".layout-settings > summary {",
                "padding: clamp(6px,.4rem,8px) clamp(10px,.65rem,14px)",
                "font-size: clamp(13px,.875rem,18px)",
                "background: rgba(255,255,255,.055)",
                "border-color: var(--gold)",
            )
        )
        and styles.count("font-size: clamp(13px,.875rem,18px)") >= 5,
    )
    verifier(
        "La personnalisation de présentation offre trois choix CSS immédiats sur le site",
        all(
            marqueur in script_site
            for marqueur in (
                'layoutSettings.className = "layout-settings"',
                'layoutSettings.dataset.siteLayoutSettings = ""',
                'layoutSettings.append(summary, panel)',
                'settings.insertAdjacentElement("afterend", layoutSettings)',
                'root.dataset.layout = selected.value',
                'const layoutPreferenceKey = "mrsc-mise-en-page"',
                'savePreference(layoutPreferenceKey, input.value)',
                'savePreference(layoutPreferenceKey, "equilibree")',
                'layoutSettings.querySelector("summary")?.focus()',
                'layoutSettings.contains(event.target)',
                'aria-live',
            )
        )
        and all(option in script_site for option in ('"equilibree"', '"lecture"', '"panorama"'))
        and all(label in script_site for label in ('label: "Équilibrée"', 'label: "Lecture"', 'label: "Panorama composite"'))
        and all(
            marqueur in script_site
            for marqueur in (
                '[data-simulateur-apercu] iframe',
                'frame.contentWindow.location.origin !== window.location.origin',
                'simulatorRoot.classList.toggle(classe, root.classList.contains(classe))',
                'simulatorRoot.dataset.layout = root.dataset.layout || "equilibree"',
                'frame.addEventListener("load", synchroniserSimulateurs)',
            )
        )
        and all(
            marqueur in styles
            for marqueur in (
                ".layout-settings > summary {",
                ".layout-settings-panel {",
                ".layout-settings:not([open]) > .layout-settings-panel",
                ".display-settings:not([open]) > .display-settings-panel",
                ".layout-choice {",
                'html[data-layout="lecture"] { --content: 940px; }',
                'html[data-layout="panorama"] { --content: 1480px; }',
                '@media (forced-colors: active)',
            )
        )
        and 'layoutSettings?.addEventListener("toggle"' in parcours
        and 'layoutSettings.querySelector("summary")?.focus()' in parcours,
    )
    verifier(
        "L’en-tête se compacte automatiquement selon l’espace et garde un contrôle réversible",
        all(
            marqueur in styles
            for marqueur in (
                ".site-header.is-compact .site-status-note",
                ".site-header.is-compact .identity",
                ".header-compact-toggle[hidden]",
                ".header-compact-toggle {\n  --header-compact-width: 6.25rem;\n  display: none;\n  flex: 0 0 min(var(--header-compact-width),calc(100vw - 1rem));",
                "width: min(var(--header-compact-width),calc(100vw - 1rem));",
                "max-width: min(var(--header-compact-width),calc(100vw - 1rem));",
                "overflow-wrap: anywhere;",
                "@media (max-width: 1260px)",
                "@media (max-width: 520px)",
                "@media (orientation: landscape) and (max-height: 560px) and (max-width: 920px)",
                "@media (any-pointer: coarse)",
                "html.entete-compacte",
            )
        )
        and "window.matchMedia" in script_site
        and "(max-width: 760px)" in script_site
        and "(max-width: 520px)" in script_site
        and "(orientation: landscape) and (max-height: 560px) and (max-width: 920px)" in script_site
        and 'header.classList.toggle("is-compact", compact)' in script_site
        and 'headerCompactToggle.setAttribute("aria-expanded", expanded)' in script_site
        and 'headerCompactToggle.addEventListener("click"' in script_site
        and "let previousViewportWidth = window.innerWidth;" in script_site
        and 'if (!widthIsShrinking || !narrowViewport.matches || header.classList.contains("is-compact")) return;' in script_site
        and 'header.classList.contains("is-compact") === compact' in script_site
        and "&& headerCompactToggle.textContent === label" in script_site
        and "setHeaderCompact(true);" in script_site
        and "headerDetails.some(" in script_site
        and "if (focusWouldBeHidden) headerCompactToggle.focus();" in script_site
        and "Mode compact réactivé au rétrécissement" in test_experience
        and "MutationObserver" in test_experience
        and "assert.equal(cadreAgrandir720, cadreReduire720" in test_experience
        and "controlesBarre.every((element) => element.flexShrink === '0')" in test_experience
        and "assert.equal(etat.cadreLargeur, 100" in test_experience
        and "assert.equal(etat.lignes, 1" in test_experience
        and "cadreEtTexte.lignesTexte.every" in test_experience
        and "cadreEtTexte.scrollWidth <= cadreEtTexte.largeur" in test_experience,
    )
    verifier(
        "La navigation permet retour, avance, accueil et reprise du dernier point",
        all(marqueur in parcours for marqueur in ('"precedent"', '"suivant"', '"accueil"', '"dernier"', "sessionStorage")),
    )
    verifier(
        "Les quatre commandes sont regroupées derrière une seule bascule Parcours dans l’en-tête",
        all(
            marqueur in styles
            for marqueur in (
                ".site-journey-settings > summary",
                ".site-journey-settings[open] > summary",
                ".site-journey-panel[hidden]",
                ".site-journey-settings:not([open]) > .site-journey-panel",
                ".site-journey-button:disabled",
            )
        )
        and 'document.createElement("details")' in parcours
        and 'parcours.className = "site-journey-settings"' in parcours
        and 'declencheur.textContent = "Parcours"' in parcours
        and 'declencheur.setAttribute("aria-controls", panneau.id)' in parcours
        and 'panneau.appendChild(barre)' in parcours
        and 'navInner.insertBefore(parcours, displaySettingsInHeader)' in parcours
        and "header.after(barre)" not in parcours,
    )
    verifier(
        "Le panneau Parcours se replie au clavier, à l’extérieur et à l’ouverture des autres menus",
        'if (event.key !== "Escape") return;' in parcours
        and 'if (parcours.open) {' in parcours
        and 'if (focusInside) declencheur.focus();' in parcours
        and 'if (focusInside) layoutSettings.querySelector("summary")?.focus();' in parcours
        and 'if (!parcours.contains(event.target)) parcours.open = false;' in parcours
        and 'parcours.addEventListener("toggle"' in parcours
        and 'displaySettings?.addEventListener("toggle"' in parcours
        and 'layoutSettings?.addEventListener("toggle"' in parcours
        and 'menuToggle?.addEventListener("click"' in parcours,
    )
    verifier(
        "Les commandes Parcours restent compactes et tactiles sur mobile",
        ".site-journey-inner" in styles
        and "min-height: 38px" in styles
        and ".site-journey-symbol { display: none; }" in styles
        and "@media (any-pointer: coarse)" in styles
        and ".site-journey-button { min-width: 44px; min-height: 44px; }" in styles,
    )
    verifier(
        "Les boutons gardent leurs libellés et leur nom accessible sur petit écran",
        'texte.className = "site-journey-label"' in parcours
        and 'texte.textContent = libelle' in parcours
        and 'bouton.setAttribute("aria-label", ariaLabel)' in parcours
        and '.site-journey-symbol { display: none; }' in styles
        and 'statut.textContent = stockageDisponible' in parcours,
    )
    bloc_racine = styles.split(":root", 1)[1].split("}", 1)[0] if ":root" in styles else ""
    vert_marque = re.search(r"--green:\s*(#[0-9a-fA-F]{6})", bloc_racine)
    ratio_vert = rapport_contraste(vert_marque.group(1), "#ffffff") if vert_marque else 0.0
    verifier(
        "Le vert de marque utilisé en texte atteint 4,5:1 sur blanc",
        ratio_vert >= 4.5,
        f"{ratio_vert:.2f}:1",
    )
    verifier(
        "La page de transparence explique le défilement local du tableau large",
        'class="table-scroll-hint"' in (RACINE / "transparence.html").read_text(encoding="utf-8"),
    )
    apprentissage = (RACINE / "apprendre.html").read_text(encoding="utf-8")
    verifier(
        "La page d’apprentissage propose quatre repères et plusieurs matières",
        all(rep in apprentissage for rep in ("Premiers pas", "Consolider", "Raisonner", "Approfondir", "Mathématiques", "Numérique et intelligence artificielle")),
    )
    fiches = sorted((RACINE / "apprendre" / "fiches").glob("*.html"))
    blocs_correction = sum(fiche.read_text(encoding="utf-8").count('<details class="learning-answer">') for fiche in fiches)
    verifier(
        "Les fiches autonomes proposent une aide et une correction progressives",
        len(fiches) >= 1 and blocs_correction >= 2 * len(fiches),
        f"{len(fiches)} fiches, {blocs_correction} blocs de correction",
    )
    fiches_autonomes = all(
        '<aside class="learning-analogy"' in fiche.read_text(encoding="utf-8")
        and "Limite de l’image" in fiche.read_text(encoding="utf-8")
        and "Sources facultatives et limites" in fiche.read_text(encoding="utf-8")
        and "Tu peux suivre cette fiche sans ouvrir ces liens" in fiche.read_text(encoding="utf-8")
        for fiche in fiches
    )
    verifier(
        "Chaque fiche autonome est autoportante, avec analogie, limite et sources facultatives",
        len(fiches) >= 1 and fiches_autonomes,
        f"{len(fiches)} fiche(s) contrôlée(s)",
    )
    verifier(
        "La présentation d’EVA n’invente pas de fonctionnalités",
        "Aucune fonction d’EVA n’est annoncée" in apprentissage,
    )
    accueil = (RACINE / "index.html").read_text(encoding="utf-8")
    verifier(
        "L’accueil présente clairement ce que propose le M.R.S.C",
        all(
            terme in accueil
            for terme in (
                "Comprendre les sujets",
                "des fiches",
                "un dossier sur l’intelligence artificielle",
                "un simulateur",
                "poser une question",
                "proposer une idée",
            )
        ),
    )
    verifier(
        "L’accueil relie la présentation de l’association aux statuts et aux trois repères de réflexion",
        all(
            terme in accueil
            for terme in (
                "Nos expériences ont quelque chose à apporter.",
                "a pour vocation de préserver, défendre et représenter les intérêts",
                "Ses statuts placent au cœur de cette démarche le lien social",
                "Partir de ce que nous vivons",
                "Mettre les savoirs en commun",
                "Rendre les propositions compréhensibles",
                'href="assets/documents/statuts-2020.pdf"',
                'href="documents.html">Découvrir l’association</a>',
                'href="#actions">Explorer les ressources</a>',
            )
        ),
    )
    verifier(
        "L’accueil présente la recherche sur ÉVA comme un travail en cours, sans confondre objectifs et fonctions",
        all(
            terme in accueil
            for terme in (
                'id="rd-eva"',
                "ÉVA signifie « Entité Virtuelle Autonome »",
                "Recherche en cours",
                "Matériel et financements nécessaires.",
                "Le budget et les besoins précis restent à définir",
                "Ce résumé n’est pas un appel aux dons",
                "ne constitue pas une position officielle de l’association",
                'href="eva.html"',
                "proposition de présentation (à relire)",
                "href=\"transparence.html#rd-innovation\"",
            )
        ),
    )
    eva = (RACINE / "eva.html").read_text(encoding="utf-8")
    eva_texte = unescape(eva)
    verifier(
        "La page ÉVA reste une proposition générale, non technique et non validée",
        all(
            terme in eva_texte
            for terme in (
                "proposition de rédaction préparée avec l’aide d’une IA",
                "à relire et à valider avant toute communication officielle",
                "Aucune conscience acquise n’est revendiquée",
                "Cette proposition ne constitue pas une position officielle de l’association",
                "la proposition prévoit du matériel adapté",
                "des financements pour l’acquérir",
                "ne publie pas de données personnelles",
                "procédés internes détaillés",
                "Cette proposition ne présente aucun budget",
            )
        )
        and not re.search(r"\b\d+\s*(?:Go|To|jetons?|milliards?\s+de\s+paramètres)\b", eva_texte, re.IGNORECASE),
    )
    verifier(
        "La page ÉVA est liée, indexée, publiée et servie en aperçu local",
        'href="eva.html"' in accueil
        and "/MRSC/eva.html" in sitemap
        and "/MRSC/eva.html" in llms_txt.read_text(encoding="utf-8")
        and "cp index.html apprendre.html anglais-aventure.html ia-societe.html eva.html simulateur.html" in publication
        and '"eva.html"' in serveur_local,
    )
    transparence = (RACINE / "transparence.html").read_text(encoding="utf-8")
    transparence_texte = unescape(transparence)
    verifier(
        "Le registre de transparence identifie ÉVA comme proposition IA à relire",
        all(
            terme in transparence_texte
            for terme in (
                "Proposition de présentation du projet, de ses limites et des moyens nécessaires",
                "Texte préparé avec l’aide d’une IA et à relire",
                "Besoins, budget et détails techniques non validés pour publication",
                "Proposition à valider",
            )
        )
        and 'href="eva.html"' in transparence,
    )
    documents_html = (RACINE / "documents.html").read_text(encoding="utf-8")
    fichiers_locaux_documents = (
        "assets/documents/statuts-2020.pdf",
        "assets/documents/bulletin-adhesion-2020.pdf",
        "assets/documents/bulletin-don-2020.pdf",
    )
    ligne_copies_locales = re.search(
        r'<tr><th scope="row">Documents</th><td>Statuts, bulletins d’adhésion et de don</td>.*?</tr>',
        transparence,
        flags=re.DOTALL,
    )
    ligne_journal_officiel = re.search(
        r'<tr><th scope="row">Documents</th><td>Parution Journal officiel</td>.*?</tr>',
        transparence,
        flags=re.DOTALL,
    )
    url_journal_officiel = "https://www.journal-officiel.gouv.fr/publications/assoc/pdf/2016/0015/JOAFE_PDF_Unitaire_20160015_01361.pdf"
    verifier(
        "Les copies PDF locales et la source externe du Journal officiel sont distinguées",
        all(f'href="{fichier}"' in documents_html for fichier in fichiers_locaux_documents)
        and all(f'href="{fichier}"' in transparence for fichier in fichiers_locaux_documents)
        and bool(ligne_copies_locales)
        and "Documents officiels, copies locales" in unescape(ligne_copies_locales.group(0))
        and bool(ligne_journal_officiel)
        and url_journal_officiel in documents_html
        and url_journal_officiel in transparence
        and "Source externe" in unescape(ligne_journal_officiel.group(0)),
    )
    verifier(
        "Les chiffres et le statut des fiches restent nuancés dans la page de transparence",
        all(
            terme in transparence_texte
            for terme in (
                "81 fiches dans 15 domaines",
                "26 fiches du corpus initial",
                "55 prototypes explicitement à relire",
                "La relecture indépendante de toutes les fiches initiales n’est pas garantie",
            )
        ),
    )
    verifier(
        "La prospective publique distingue scénarios, proposition et limites",
        all(
            terme in transparence_texte
            for terme in (
                'id="prospective-2030"',
                "quatre situations possibles",
                "sans probabilité ni prévision",
                "décision ou position officielle de l’association",
                "Aucun balayage externe récent",
                "aucun atelier avec l’association ni test avec des personnes",
                "concept candidat, non une fonction construite",
                "Aucune fonction issue de la Boussole n’est intégrée au site.",
                "Boussole des savoirs",
                "Hypothèses, non validées",
            )
        )
        and 'href="https://github.com/thejmimiia-code/MRSC/blob/main/docs/rd/prospective-2027-2030.md"' in transparence,
    )
    verifier(
        "Les titres et le repère de statut de la note ressortent sur l’encadré bleu",
        ".creator-note h3,\n.creator-note h4 { color: var(--white); }" in styles
        and ".creator-note .eyebrow { color: #bae6fd; }" in styles,
    )
    verifier(
        "Le registre renvoie vers la présentation d’ÉVA et distingue objectifs, essais et résultats",
        'href="index.html#rd-eva"' in transparence
        and "objectifs, essais, r&eacute;sultats et fonctions disponibles sont distingu&eacute;s" in transparence,
    )
    verifier(
        "L’accueil relie apprentissages, débat, simulateur, documents et participation",
        all(terme in accueil for terme in ('href="apprendre.html"', 'href="ia-societe.html"', 'href="simulateur.html"', 'href="documents.html"', 'href="nous-contacter.html"')),
    )
    partage = (RACINE / "assets" / "js" / "site.js").read_text(encoding="utf-8")
    verifier(
        "Le partage de l’accueil propose une action et des replis accessibles",
        'data-share-site' in accueil and 'data-share-fallback' in accueil
        and "navigator.share" in partage and "navigator.clipboard" in partage,
    )
    verifier(
        "Les boutons d’action et de parcours suivent les rayons et les couleurs du site",
        "--button-radius: 9px" in styles
        and "border-radius: var(--button-radius)" in styles
        and ".site-journey-button[data-journey-action=\"accueil\"]" in styles,
    )
    pages_ui = [RACINE / page for page in PAGES] + sorted((RACINE / "apprendre" / "fiches").glob("*.html"))
    classes_autorisees = {"button", "nav-toggle", "display-control", "header-compact-toggle"}
    boutons_coherents = True
    for page in pages_ui:
        contenu = page.read_text(encoding="utf-8")
        for attributs in re.findall(r"<button\b([^>]*)>", contenu, flags=re.IGNORECASE):
            classe = re.search(r"\bclass=[\"']([^\"']+)[\"']", attributs, flags=re.IGNORECASE)
            if not classe or not (classes_autorisees & set(classe.group(1).split())):
                boutons_coherents = False
                break
        if not boutons_coherents:
            break
    verifier(
        "Les boutons HTML des pages et fiches utilisent les composants de marque",
        boutons_coherents and all(regle in styles for regle in (".button {", ".nav-toggle {", ".display-control {", ".header-compact-toggle {")),
        f"{len(pages_ui)} pages inspectées",
    )
    simulateur_styles = (RACINE / "outils" / "construire-simulateur.py").read_text(encoding="utf-8")
    verifier(
        "Les commandes du simulateur reprennent les accents bleu, vert et or du M.R.S.C",
        "--accent: #91b2e6" in simulateur_styles
        and "--ambre: #f2c15f" in simulateur_styles
        and "linear-gradient(135deg, #1d3268, #2958a2)" in simulateur_styles,
    )
    verifier(
        "Les flèches des panneaux du simulateur changent de sens à l’ouverture",
        all(
            marqueur in simulateur_styles
            for marqueur in (
                ".site-layout-chevron { display: inline-block;",
                ".site-layout-settings[open] .site-layout-chevron { transform: rotate(180deg); }",
            )
        ),
    )
    verifier(
        "La R&D de cohérence visuelle et éditoriale est documentée",
        (RACINE / "docs" / "rd-coherence-visuelle-editoriale.md").is_file(),
    )
    verifier(
        "L’accueil conserve les documents officiels et le registre de traçabilité",
        'class="trace-list"' in accueil and 'trace-panel' in accueil,
    )
    workflow_pages = (RACINE / ".github" / "workflows" / "deploy-pages.yml").read_text(encoding="utf-8")
    verifier(
        "La page d’apprentissage est incluse dans la publication GitHub Pages",
        "cp index.html apprendre.html" in workflow_pages,
    )
    verifier(
        "Les fiches autonomes et la notice vie privée sont publiées",
        "confidentialite.html" in workflow_pages
        and "cp -R apprendre/fiches _site/apprendre/fiches" in workflow_pages
        and "sitemap.xml" in workflow_pages,
    )
    readme = (RACINE / "README.md").read_text(encoding="utf-8")
    verifier(
        "Le README distingue l’adresse GitHub Pages actuelle du domaine personnalisé souhaité",
        "Adresse actuellement publiée par GitHub Pages" in readme
        and "https://thejmimiia-code.github.io/MRSC/" in readme
        and "`www.mrsc.fr`" in readme
        and "n’est pas encore configuré dans GitHub Pages" in readme
        and "sans redirection vers `github.io`" in readme
        and "Adresse publique durable du projet" not in readme,
    )
    verifier(
        "Le README décrit correctement les copies PDF locales et le lien externe officiel",
        "copies locales dans `assets/documents/`" in readme
        and "reste un lien externe vers sa source officielle" in readme
        and "L’intégration de Google My Maps n’est chargée qu’après une action volontaire" in readme,
    )
    verifier(
        "La page d’accueil renvoie vers la présentation du simulateur",
        'href="simulateur.html"' in (RACINE / "index.html").read_text(encoding="utf-8"),
    )
    page_simulateur = RACINE / "simulateur" / "index.html"
    presentation_simulateur = (RACINE / "simulateur.html").read_text(encoding="utf-8")
    scenarios_annonces = re.search(
        r"<dt>\s*(\d+)\s*</dt>\s*<dd>\s*scénarios types",
        presentation_simulateur,
        flags=re.IGNORECASE,
    )
    verifier(
        "Le nombre annoncé de scénarios correspond au moteur",
        bool(scenarios_annonces) and int(scenarios_annonces.group(1)) == len(SCENARIOS_MOTEUR),
        f"{len(SCENARIOS_MOTEUR)} scénarios présents",
    )
    levier_annonce = re.search(
        r"<dt>\s*100\+\s*</dt>\s*<dd>\s*leviers de politique publique réglables",
        presentation_simulateur,
        flags=re.IGNORECASE,
    )
    verifier(
        "La présentation annonce prudemment plus de 100 leviers",
        bool(levier_annonce) and len(LEVIERS_MOTEUR) > 100,
        f"{len(LEVIERS_MOTEUR)} leviers dans la copie embarquée",
    )
    domaines_annonces = re.search(
        r"<dt>\s*(\d+)\s*</dt>\s*<dd>\s*domaines d’impact notés de 0 à 100",
        presentation_simulateur,
        flags=re.IGNORECASE,
    )
    verifier(
        "Le nombre annoncé de domaines correspond au moteur",
        bool(domaines_annonces) and int(domaines_annonces.group(1)) == len(DOMAINES_MOTEUR),
        f"{len(DOMAINES_MOTEUR)} domaines présents",
    )
    indicateurs_annonces = re.search(
        r"<dt>\s*(\d+)\s*</dt>\s*<dd>\s*indicateurs de contexte référencés avec leur source et leur période",
        presentation_simulateur,
        flags=re.IGNORECASE,
    )
    verifier(
        "Le nombre annoncé d’indicateurs correspond au registre de données",
        bool(indicateurs_annonces)
        and int(indicateurs_annonces.group(1)) == len(INDICATEURS_MOTEUR),
        f"{len(INDICATEURS_MOTEUR)} indicateurs référencés",
    )
    verifier(
        "La page avertit qu’une copie embarquée peut différer de la version hébergée",
        "La copie embarquée peut différer de la version hébergée" in presentation_simulateur
        and 'data-simulateur-revision' in presentation_simulateur,
    )
    verifier(
        "La page du simulateur est publiée",
        page_simulateur.is_file(),
    )
    if page_simulateur.is_file():
        simulateur_html = page_simulateur.read_text(encoding="utf-8")
        simulateur_source = (RACINE / "simulateur" / "interface.py").read_text(encoding="utf-8")
        verifier(
            "Le simulateur offre un retour permanent vers le site M.R.S.C",
            'id="mrsc-retour-site"' in simulateur_html
            and 'href="../index.html"' in simulateur_html
            and 'href="../confidentialite.html"' in simulateur_html
            and 'id="contenu-principal"' in simulateur_html
            and 'class="sim-skip-link"' in simulateur_html
            and "position: sticky" in simulateur_html,
        )
        verifier(
            "Le parcours du simulateur autonome est repliable et conserve les commandes tactiles",
            'contenuBarre.className = "site-journey-inner"' in parcours
            and ".site-return-bar .site-journey-settings > summary {" in simulateur_html
            and ".site-return-bar .site-journey-panel {" in simulateur_html
            and ".site-return-bar .site-journey-settings:not([open]) > .site-journey-panel" in simulateur_html
            and ".site-return-bar .site-journey-inner" in simulateur_html
            and ".site-return-bar .site-journey-button {" in simulateur_html
            and "@media (max-width: 640px)" in simulateur_html
            and ".site-return-bar .site-journey-symbol { display: none; }" in simulateur_html
            and ".site-return-bar .site-journey-button { min-width: 44px; }" in simulateur_html
            and "parentHasSiteHeader" in parcours,
        )
        verifier(
            "Le simulateur propose les réglages texte, contraste et interligne",
            all(
                marqueur in simulateur_html
                for marqueur in (
                    'id="mrsc-display-controls"',
                    'data-sim-text-decrease',
                    'data-sim-text-increase',
                    'data-sim-contrast',
                    'data-sim-spacing',
                    'mrsc-texte-niveau',
                )
            ),
        )
        verifier(
            "Le simulateur autonome propose les trois mises en page et partage le choix local du site",
            all(
                marqueur in simulateur_html
                for marqueur in (
                    'class="site-layout-settings" data-site-layout-settings hidden',
                    'aria-controls="site-layout-settings-panel"',
                    'value="equilibree" data-site-layout-option',
                    'value="lecture" data-site-layout-option',
                    'value="panorama" data-site-layout-option',
                    '<strong>Panorama composite</strong><span>Une page plus large, avec un agencement de cartes en plusieurs colonnes.</span>',
                    'data-site-layout-status role="status" aria-live="polite"',
                    'data-site-layout-reset',
                    'layout: "mrsc-mise-en-page"',
                    'applyLayout(read(keys.layout))',
                    'root.dataset.layout = layout',
                    'html[data-layout="lecture"] #contenu-principal { max-width: 1160px; }',
                    'html[data-layout="panorama"] #contenu-principal { max-width: 1800px; }',
                    '.site-return-bar .site-layout-panel {',
                    '.site-return-bar .site-layout-settings:not([open]) > .site-layout-panel',
                    '.site-return-bar .site-layout-settings > summary {',
                    'minmax(min(300px,100%),1fr)',
                    '.message-seuil .source,',
                    '@media (forced-colors: active)',
                    '.site-return-bar .site-layout-panel {\n    position: fixed;\n    top: .5rem;',
                )
            )
            and 'layoutRadios.forEach((radio)' in simulateur_html
            and 'window.parent.document.querySelector(".site-header .nav-inner [data-menu-toggle]")' in simulateur_html
            and 'controls.hidden = parentHasSiteHeader' in simulateur_html
            and 'layoutSettings.hidden = parentHasSiteHeader' in simulateur_html
            and 'layoutSettings?.addEventListener("toggle"' in simulateur_html,
        )
        verifier(
            "Le simulateur autonome reprend les cinq paliers et leur reflow typographique",
            "const textLevels = [50, 75, 100, 125, 150]" in simulateur_html
            and "const legacyTextLevels = [100, 125, 150]" in simulateur_html
            and "html.texte-tres-reduit { font-size: 50%; }" in simulateur_html
            and "html.texte-reduit { font-size: 75%; }" in simulateur_html
            and "font-size: max(12px,1em)" in simulateur_html
            and "font-size: clamp(12px,1em,20px)" in simulateur_html
            and "padding: clamp(6px,.4rem,8px) clamp(8px,.65rem,14px)" in simulateur_html,
        )
        verifier(
            "Les tableaux larges initiaux et le journal sont nommés, annoncés et accessibles au clavier",
            simulateur_html.count('class="defilable mrsc-scroll-region" role="region" tabindex="0"') == 2
            and simulateur_html.count('class="mrsc-scroll-hint"') == 2
            and 'class="journal mrsc-scroll-region" id="journal" role="region" tabindex="0" aria-label="Journal causal du moteur"' in simulateur_html
            and ".journal:focus-visible" in simulateur_source,
        )
        verifier(
            "Les tableaux des vues dynamiques sont défilables, focusables et nommés",
            "panneau.querySelectorAll('.tableau-strate')" in simulateur_source
            and "zone.classList.add('mrsc-scroll-region')" in simulateur_source
            and "zone.setAttribute('role', 'region')" in simulateur_source
            and "zone.setAttribute('tabindex', '0')" in simulateur_source
            and "zone.setAttribute('aria-label'" in simulateur_source
            and "const libelleOnglet = (document.getElementById(`tab-strate-${cle}`)?.textContent || cle)" in simulateur_source
            and ".tableau-strate:focus-visible" in simulateur_source,
        )
        verifier(
            "Les tableaux d’audit sont isolés du débordement de page et nommés",
            "function tableauAuditDefilant(tableau, libelle)" in simulateur_source
            and 'class="audit-table-scroll mrsc-scroll-region" role="region" tabindex="0" aria-label="${echapperAttribut(libelle)}"' in simulateur_source
            and ".audit-table-scroll:focus-visible" in simulateur_source
            and ".audit-table-scroll{width:100%;max-width:100%;overflow-x:auto" in simulateur_source,
        )
        verifier(
            "Les textes secondaires et titres de familles du simulateur utilisent des couleurs lisibles",
            "#7b8aa5" not in simulateur_source
            and ".message-seuil .source{font-size:.66rem;color:var(--texte-dim)" in simulateur_source
            and ".famille h3{font-size:.84rem" in simulateur_source
            and "color:var(--texte)" in simulateur_source
            and "function couleurHexSure(couleur" in simulateur_source
            and "return /^#[0-9a-f]{6}$/i.test(valeur)" in simulateur_source
            and 'style="--famille-accent:${couleurHexSure(famille.couleur)}"' in simulateur_source,
        )
        verifier(
            "Le simulateur replie ses grilles et curseurs compacts sous 640 px",
            "@media (max-width: 640px)" in simulateur_html
            and ".leviers-grille.compacte" in simulateur_html
            and "minmax(0, 1fr)" in simulateur_html
            and ".clair-lignes{grid-template-columns:minmax(0,1fr)}" in simulateur_html
            and ".levier .ligne{flex-wrap:wrap}" in simulateur_html,
        )
        verifier(
            "Le simulateur prend en compte contraste forcé et mouvements réduits",
            "@media (forced-colors: active)" in simulateur_html
            and "@media (prefers-reduced-motion: reduce)" in simulateur_html,
        )
        verifier(
            "Les scénarios et préréglages du simulateur sont des boutons clavier avec état annoncé",
            simulateur_html.count("const card = document.createElement('button');") == 2
            and "card.dataset.cardType = 'scenario';" in simulateur_html
            and "card.dataset.cardType = 'preset';" in simulateur_html
            and simulateur_html.count("card.setAttribute('aria-pressed', 'false');") == 2
            and "marquerCarteActive(ev, scenario, '#scenario-grid');" in simulateur_html
            and "element.setAttribute('aria-pressed', String(active));" in simulateur_html
            and "button.scenario-card" in simulateur_html
            and ".scenario-card-title" in simulateur_html
            and ".scenario-card-copy" in simulateur_html,
        )


def demander(fichier: Path, chemin: str, methode: str, corps: bytes | None) -> tuple[int, bytes]:
    """Monte une fonction de api/ comme Vercel, l'interroge, puis l'arrête."""
    module = charger_module(fichier, f"api_{fichier.stem}_{methode}")
    module.handler.log_message = lambda *arguments: None  # sortie de test silencieuse
    with ThreadingHTTPServer(("127.0.0.1", 0), module.handler) as serveur:
        threading.Thread(target=serveur.serve_forever, daemon=True).start()
        requete = urllib.request.Request(
            f"http://127.0.0.1:{serveur.server_address[1]}{chemin}", data=corps, method=methode
        )
        if corps:
            requete.add_header("Content-Type", "application/json")
        try:
            with urllib.request.urlopen(requete, timeout=180) as reponse:
                statut, contenu = reponse.status, reponse.read()
        except urllib.error.HTTPError as erreur:
            statut, contenu = erreur.code, erreur.read()
        except (urllib.error.URLError, OSError) as erreur:
            statut, contenu = 0, str(erreur).encode()
        finally:
            serveur.shutdown()
    return statut, contenu


def routes_servies() -> None:
    for route in ROUTES:
        if route in ("simuler", "donnees"):
            methode = "POST"
            corps = json.dumps({"parametres": {}, "horizon": 5}).encode()
        elif route == "conseil":
            # Conseiller « effet papillon » : un mouvement complet de levier.
            methode = "POST"
            corps = json.dumps(
                {"cle": "tva_taux_normal", "avant": 20.0, "apres": 19.0}
            ).encode()
        else:
            methode = "GET"
            corps = None
        statut, contenu = demander(RACINE / "api" / f"{route}.py", f"/api/{route}", methode, corps)
        acceptes = STATUTS_ACCEPTES.get(route, (200,))
        verifier(
            f"Fonction api/{route}.py sert /api/{route}",
            statut in acceptes,
            f"statut {statut}, {len(contenu)} octets",
        )

    for chemin, (requete, attendu) in ROUTES_TESTS.items():
        nom = chemin.split("?")[0].split("/")[-1]
        statut, contenu = demander(RACINE / "api" / f"{nom}.py", chemin + requete, "GET", None)
        verifier(
            f"Réponse exploitable : {chemin}{requete}",
            statut == attendu and contenu.lstrip()[:1] in (b"{", b"<"),
            f"statut {statut}, {len(contenu)} octets",
        )


def source_distante() -> None:
    """Vérifie la cible de production et la bascule, sans réseau externe."""
    from http.server import BaseHTTPRequestHandler

    sonde = charger_module(RACINE / "api" / "verifier-source.py", "verifier_source_integration")
    page_simulateur = (RACINE / "simulateur.html").read_text(encoding="utf-8")
    source_attendue = "https://d-mocratie-et-politique-du-peuple-p.vercel.app/"
    source_html = re.search(r'data-source-distante="([^"]+)"', page_simulateur)
    verifier(
        "La page et la sonde utilisent l’alias Vercel déclaré",
        source_html is not None
        and source_html.group(1) == source_attendue
        and f'href="{source_attendue}"' in page_simulateur
        and "simulateur-macro-politique.onrender.com" not in page_simulateur,
    )
    verifier(
        "La sonde autorise l’alias Vercel déclaré",
        sonde._source_autorisee(source_attendue)
        and sonde._source_autorisee("https://simulateur-macro-politique.onrender.com/"),
    )

    class Stub(BaseHTTPRequestHandler):
        """Fausse source distante, pour un contrôle sans réseau externe."""

        def do_GET(self) -> None:  # noqa: N802 - API stdlib
            _repondre_stub(self)

        def log_message(self, *arguments: object) -> None:  # noqa: N802 - API stdlib
            """Silencieux : c'est un serveur de test."""

    ancienne_source = os.environ.get("SIMULATEUR_SOURCE_DISTANTE")
    ancien_mode_test = os.environ.get("SIMULATEUR_SOURCE_DISTANTE_TEST_LOCALE")
    os.environ["SIMULATEUR_SOURCE_DISTANTE_TEST_LOCALE"] = "1"
    with ThreadingHTTPServer(("127.0.0.1", 0), Stub) as stub:
        threading.Thread(target=stub.serve_forever, daemon=True).start()
        adresse = f"http://127.0.0.1:{stub.server_address[1]}/"

        os.environ["SIMULATEUR_SOURCE_DISTANTE"] = adresse
        statut, contenu = demander(RACINE / "api" / "verifier-source.py", "/api/verifier-source", "GET", None)
        charge = json.loads(contenu or b"{}")
        verifier(
            "Source distante fonctionnelle : la bascule est autorisée",
            statut == 200 and charge.get("disponible") is True and charge.get("page", {}).get("indice_simulateur"),
            f"statut {statut}, disponible={charge.get('disponible')}, "
            f"page={charge.get('page')}, api={charge.get('api')}, message={charge.get('message')}",
        )

        stub.shutdown()

    os.environ["SIMULATEUR_SOURCE_DISTANTE"] = "http://127.0.0.1:9/"
    statut, contenu = demander(RACINE / "api" / "verifier-source.py", "/api/verifier-source", "GET", None)
    charge = json.loads(contenu or b"{}")
    verifier(
        "Source distante injoignable : bascule refusée sans erreur",
        statut == 200 and charge.get("disponible") is False and bool(charge.get("message")),
        f"statut {statut}, disponible={charge.get('disponible')}",
    )
    if ancienne_source is None:
        os.environ.pop("SIMULATEUR_SOURCE_DISTANTE", None)
    else:
        os.environ["SIMULATEUR_SOURCE_DISTANTE"] = ancienne_source
    if ancien_mode_test is None:
        os.environ.pop("SIMULATEUR_SOURCE_DISTANTE_TEST_LOCALE", None)
    else:
        os.environ["SIMULATEUR_SOURCE_DISTANTE_TEST_LOCALE"] = ancien_mode_test


def _repondre_stub(soi) -> None:  # noqa: ANN001 - handler HTTP minimal
    """Fausse source distante : une page du moteur et une API qui répond."""
    chemin = soi.path.split("?")[0]
    if chemin in ("/", "/index.html"):
        corps = (
            "<!DOCTYPE html><html lang='fr'><head><title>Simulateur Macro-Politique</title></head>"
            "<body><div id='console-pilotage'></div><p>leviers de politique publique</p></body></html>"
        ).encode("utf-8")
        type_mime = "text/html; charset=utf-8"
    elif chemin == "/api/scenarios":
        corps = json.dumps({"scenarios": {"mandature": {"nom": "Plan de mandature"}}}).encode("utf-8")
        type_mime = "application/json; charset=utf-8"
    else:
        soi.send_response(404)
        soi.send_header("Content-Length", "0")
        soi.end_headers()
        return
    soi.send_response(200)
    soi.send_header("Content-Type", type_mime)
    soi.send_header("Content-Length", str(len(corps)))
    soi.end_headers()
    soi.wfile.write(corps)


def main() -> int:
    dire("── Intégration du simulateur au site M.R.S.C ──")
    page_a_jour()
    fonctions_conformes()
    fichiers_du_site()
    liens_et_scripts_statiques()
    recherche_developpement_continue()
    # Le moteur écrit des tableaux de simulation : on garde la sortie du test lisible.
    with contextlib.redirect_stdout(io.StringIO()):
        routes_servies()
        source_distante()
    dire("")
    if echecs:
        dire(f"{len(echecs)} contrôle(s) en échec : {', '.join(echecs)}")
        return 1
    dire("Tous les contrôles passent.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
