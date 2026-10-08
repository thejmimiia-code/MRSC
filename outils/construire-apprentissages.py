#!/usr/bin/env python3
"""Génère et vérifie le catalogue de fiches autonomes M.R.S.C.

Les sources éditoriales sont dans docs/apprentissage/*.toml. Les pages HTML
publiées et la cartographie lisible sont des sorties générées : modifier les
sources puis lancer ce script, plutôt que modifier les fichiers générés à la main.

    python3 outils/construire-apprentissages.py
    python3 outils/construire-apprentissages.py --verifier
    python3 outils/construire-apprentissages.py --verifier --rapport rapport.md

Le contrôle hebdomadaire est volontairement hors ligne : il vérifie le
catalogue, ses analogies, ses sources déclarées et ses dates de revue. Il ne
prétend pas vérifier automatiquement la vérité d’un contenu ni la disponibilité
ou l’actualité d’une source externe.
"""

from __future__ import annotations

import argparse
import html
import re
import sys
import tomllib
from collections import Counter
from datetime import date, timedelta
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "docs" / "apprentissage"
CATALOGUE = DATA / "catalogue.toml"
REFERENTIEL = DATA / "referentiel.toml"
PUBLIC_DIR = ROOT / "apprendre" / "fiches"
MATRIX = ROOT / "docs" / "couverture-savoirs-base.md"
PLAN_1000 = DATA / "plan-1000.toml"
ROADMAP_1000 = DATA / "objectif-1000.md"
BASE_URL = "https://thejmimiia-code.github.io/MRSC/"

NIVEAUX = {
    1: ("Reprendre les bases", "On peut commencer ici sans test ni prérequis."),
    2: ("Consolider", "Relier des notions et s’entraîner dans de nouveaux exemples."),
    3: ("Raisonner", "Comparer, expliquer une démarche et examiner les limites."),
    4: ("Approfondir", "Transférer une notion et construire un raisonnement plus complet."),
}
STATUTS = {
    "actif": "Fiche disponible",
    "partiel": "Début de couverture — à approfondir",
    "a-creer": "À créer",
    "revue-experte": "À créer avec une relecture spécialisée",
}
MODES_UTILISATION_SOURCE = {
    "reference-factuelle": "référence factuelle uniquement, sans reprise de contenu",
    "reutilisation-sous-licence": "réutilisation sous licence déclarée",
    "permission-expresse": "réutilisation avec permission documentée",
}
ERREURS: list[str] = []


def e(texte: object) -> str:
    """Échappement HTML commun, y compris pour les attributs."""
    return html.escape(str(texte), quote=True)


def lire_toml(chemin: Path) -> dict:
    with chemin.open("rb") as source:
        return tomllib.load(source)


def classes_entete(prefixe: str = "", page: str = "apprendre") -> str:
    """Navigation partagée. Le préfixe adapte les liens aux fiches profondes."""
    liens = [
        ("index.html", "Accueil", "accueil"),
        ("ia-societe.html", "IA &amp; société", "ia"),
        ("apprendre.html", "Apprendre", "apprendre"),
        ("simulateur.html", "Simulateur", "simulateur"),
        ("documents.html", "Documents", "documents"),
        ("liens-utiles.html", "Liens utiles", "liens"),
        ("localisation.html", "Localisation", "localisation"),
        ("transparence.html", "Transparence", "transparence"),
        ("confidentialite.html", "Vie privée et données", "confidentialite"),
        ("nous-contacter.html", "Nous contacter", "contact"),
    ]
    navigation = "\n".join(
        '          <a href="' + prefixe + href + '"'
        + (' aria-current="page"' if marqueur == page else "")
        + f'>{libelle}</a>'
        for href, libelle, marqueur in liens
    )
    return f'''  <a class="skip-link" href="#contenu">Aller au contenu principal</a>
  <header class="site-header">
    <div class="identity">
      <a href="{prefixe}index.html" data-site-home aria-label="M.R.S.C — Accueil">
        <img class="brand-logo" src="{prefixe}assets/images/logo-mrsc.jpg" alt="Logo M.R.S.C — Mouvement Représentatif de la Société Civile">
      </a>
      <div class="brand-copy">
        <p class="brand-kicker">Association loi 1901</p>
        <p class="brand-name">Mouvement Représentatif de la Société Civile</p>
        <p class="brand-tagline">La force citoyenne</p>
      </div>
      <a class="identity-contact" href="mailto:assomrsc@gmail.com" aria-label="Écrire à assomrsc@gmail.com">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" aria-hidden="true" focusable="false"><rect x="3" y="5" width="18" height="14" rx="2"></rect><path d="m4 7 8 6 8-6"></path></svg>
        assomrsc@gmail.com
      </a>
    </div>
    <nav class="main-nav" aria-label="Navigation principale">
      <div class="nav-inner">
        <button class="nav-toggle" type="button" data-menu-toggle aria-expanded="false" aria-controls="navigation-principale">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true" focusable="false"><path d="M4 6h16M4 12h16M4 18h16"></path></svg>
          Menu
        </button>
        <div class="nav-links" id="navigation-principale" data-primary-navigation>
{navigation}
        </div>
        <details class="display-settings" data-display-settings hidden>
          <summary title="Options d’affichage">Affichage <span class="display-settings-chevron" aria-hidden="true">⌄</span></summary>
          <div class="display-settings-panel">
            <p class="display-settings-title"><strong>Ajuster la lisibilité</strong></p>
            <div class="display-settings-row" role="group" aria-label="Taille du texte">
              <button class="display-control" type="button" data-text-decrease aria-label="Réduire la taille du texte" title="Réduire le texte">A−</button>
              <span class="display-text-level" data-text-size-level role="status" aria-live="polite" aria-atomic="true">100 %</span>
              <button class="display-control" type="button" data-text-increase aria-label="Agrandir la taille du texte" title="Agrandir le texte">A+</button>
            </div>
            <div class="display-settings-actions">
              <button class="display-control display-control-wide" type="button" data-contrast-toggle aria-pressed="false">Contraste renforcé</button>
              <button class="display-control display-control-wide" type="button" data-spacing-toggle aria-pressed="false">Espacement du texte</button>
            </div>
            <p class="display-settings-note">Ces choix restent enregistrés sur cet appareil. Le zoom du navigateur reste disponible.</p>
          </div>
        </details>
      </div>
    </nav>
  </header>'''


def pied_de_page(prefixe: str = "") -> str:
    return f'''  <footer class="site-footer">
    <div class="container">
      <div class="footer-grid">
        <div class="footer-brand">
          <img class="footer-logo" src="{prefixe}assets/images/logo-mrsc.jpg" alt="Logo M.R.S.C — Mouvement Représentatif de la Société Civile">
          <div><strong>Mouvement Représentatif de la Société Civile (M.R.S.C)</strong><p class="footer-tagline">La force citoyenne · Association loi 1901</p></div>
        </div>
        <nav class="footer-nav" aria-label="Navigation de pied de page">
          <p class="footer-heading">Naviguer</p>
          <ul>
            <li><a href="{prefixe}index.html">Accueil</a></li>
            <li><a href="{prefixe}ia-societe.html">IA &amp; société</a></li>
            <li><a href="{prefixe}apprendre.html">Apprendre</a></li>
            <li><a href="{prefixe}simulateur.html">Simulateur</a></li>
            <li><a href="{prefixe}documents.html">Documents</a></li>
            <li><a href="{prefixe}transparence.html">Transparence</a></li>
            <li><a href="{prefixe}confidentialite.html">Vie privée et données</a></li>
          </ul>
        </nav>
        <div class="footer-contact">
          <p class="footer-heading">Nous contacter</p>
          <address>995 route de Jarcieu<br>38270 Beaurepaire</address>
          <a class="footer-mail" href="mailto:assomrsc@gmail.com">assomrsc@gmail.com</a>
        </div>
        <div class="footer-docs">
          <p class="footer-heading">Documents</p>
          <ul>
            <li><a href="https://www.mrsc.fr/assets/nos-statuts-mrsc-du-02-10-2020.pdf" target="_blank" rel="noopener noreferrer">Nos statuts</a></li>
            <li><a href="{prefixe}documents.html">Tous les documents</a></li>
          </ul>
        </div>
      </div>
      <div class="footer-bottom">
        <p>&copy; <span data-year>2026</span> Mouvement Représentatif de la Société Civile (M.R.S.C).</p>
        <p class="footer-legal"><a href="{prefixe}confidentialite.html">Vie privée et données</a> &middot; <a href="{prefixe}nous-contacter.html">Contact</a> &middot; <a href="{prefixe}transparence.html#licence">Licence</a> &middot; <a href="#contenu">Haut de page</a></p>
      </div>
    </div>
  </footer>'''


def page_enveloppe(titre: str, description: str, contenu: str, prefixe: str = "", page: str = "apprendre", canonique: str = "") -> str:
    canonical = f'\n  <link rel="canonical" href="{e(canonique)}">' if canonique else ""
    return f'''<!doctype html>
<html lang="fr">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="description" content="{e(description)}">
  <meta name="theme-color" content="#1d3268">
  <title>{e(titre)}</title>{canonical}
  <link rel="stylesheet" href="{prefixe}assets/css/site.css">
  <script src="{prefixe}assets/js/site.js" defer></script>
  <script src="{prefixe}assets/js/navigation-parcours.js" defer></script>
</head>
<body>
{classes_entete(prefixe, page)}
  <main id="contenu">
{contenu}
  </main>
{pied_de_page(prefixe)}
</body>
</html>
'''


def liste_html(elements: list[str], balise: str = "ul", classe: str = "") -> str:
    classe_attr = f' class="{e(classe)}"' if classe else ""
    return f"<{balise}{classe_attr}>" + "".join(f"<li>{element}</li>" for element in elements) + f"</{balise}>"


def mots_cles_html(mots: list[str]) -> str:
    resultats = []
    for mot in mots:
        if " — " in mot:
            terme, definition = mot.split(" — ", 1)
            resultats.append(f"<li><strong>{e(terme)}</strong> — {e(definition)}</li>")
        else:
            resultats.append(f"<li>{e(mot)}</li>")
    return '<ul class="learning-vocabulary">' + "".join(resultats) + "</ul>"


def exemples_code_html(exemples: list[dict], identifiant: str) -> str:
    if not exemples:
        return ""
    blocs = []
    for index, exemple in enumerate(exemples, 1):
        titre = e(exemple["titre"])
        langue = e(exemple["langage"])
        contenu = e(exemple["contenu"])
        explication = e(exemple["explication"])
        etiquette = e(f'Extrait {index} — {exemple["langage"]}, {exemple["titre"]}')
        blocs.append(
            f'<figure class="learning-code-sample">'
            f'<figcaption>{titre} <span>({langue})</span></figcaption>'
            f'<pre tabindex="0" role="region" aria-label="{etiquette}"><code>{contenu}</code></pre>'
            f'<p>{explication}</p></figure>'
        )
    return (
        '<section class="learning-code-examples" aria-labelledby="exemples-code-fiche">'
        '<h2 id="exemples-code-fiche">Lire les exemples, sans rien installer</h2>'
        '<p>Ces extraits sont présentés comme du texte à examiner ; ils ne sont pas exécutés par cette page et aucun service externe n’est nécessaire.</p>'
        f'<div class="learning-code-grid" data-code-examples="{e(identifiant)}">{"".join(blocs)}</div>'
        '</section>'
    )


def render_fiche(fiche: dict) -> str:
    titre, niveau_desc = NIVEAUX[fiche["niveau"]]
    meta = (
        f'<span>{e(fiche["matiere"])}</span>'
        f'<span>Repère {fiche["niveau"]} · {e(titre.lower())}</span>'
        f'<span>{fiche["minutes"]} minutes environ</span>'
    )
    if fiche.get("horizon_contenu"):
        meta += f'<span>Horizon du contenu : {e(fiche["horizon_contenu"])}</span>'
    if fiche.get("statut_editorial"):
        meta += f'<span>Statut éditorial : {e(fiche["statut_editorial"])}</span>'
    note_statut = ""
    if fiche.get("note_statut_editorial"):
        note_statut = f'        <p class="learning-level-note"><strong>État éditorial :</strong> {e(fiche["note_statut_editorial"])}</p>\n'
    if fiche.get("statut_editorial"):
        note_revue = f'<p class="learning-review-note">Date du contrôle initial indiqué : {e(fiche["revue_le"])}. Une relecture indépendante reste à faire ; cette date ne garantit pas l’actualité future.</p>'
    else:
        note_revue = f'<p class="learning-review-note">Revue éditoriale indiquée : {e(fiche["revue_le"])}. Cette date n’est pas une garantie d’actualité future.</p>'
    demarche = liste_html([e(etape) for etape in fiche["demarche"]], "ol", "learning-steps")
    correction = liste_html([e(etape) for etape in fiche["correction"]], "ol", "learning-answer-list")
    a_retenir = liste_html([e(item) for item in fiche["a_retenir"]], "ul", "learning-takeaways")
    vocabulaire = mots_cles_html(fiche["notions"])
    exemples_code = exemples_code_html(fiche.get("exemples_code", []), fiche["id"])
    def note_source(source: dict) -> str:
        notes = []
        mode = source.get("mode_utilisation")
        date_controle = source.get("droits_controles_le")
        licence = source.get("licence_source", "")
        if date_controle and licence:
            if "non vérifiée" in licence.casefold():
                notes.append(f'Droits examinés le {e(date_controle)} : licence source non vérifiée')
            else:
                notes.append(f'Licence source consultée le {e(date_controle)} : {e(licence)}')
        if mode in MODES_UTILISATION_SOURCE:
            notes.append(f'Mode d’utilisation : {e(MODES_UTILISATION_SOURCE[mode])}')
        if source.get("utilisation"):
            notes.append(e(source["utilisation"]))
        return f' — {". ".join(notes)}' if notes else ""

    sources = "".join(
        f'<li><a href="{e(source["url"])}" target="_blank" rel="noopener noreferrer">{e(source["titre"])}</a>'
        f'{note_source(source)}</li>'
        for source in fiche["sources"]
    )
    contenu = f'''    <section class="learning-lesson-hero">
      <div class="container">
        <nav class="learning-breadcrumb" aria-label="Fil d’Ariane"><a href="../../index.html">Accueil</a><span aria-hidden="true">›</span><a href="../../apprendre.html">Apprendre</a><span aria-hidden="true">›</span><span aria-current="page">Fiche</span></nav>
        <p class="eyebrow">Fiche autonome · {e(fiche["matiere"])}</p>
        <h1>{e(fiche["titre"])}</h1>
        <p class="learning-lesson-lead">{e(fiche["resume"])}</p>
        <div class="learning-lesson-meta" aria-label="Repères de la fiche">{meta}</div>
{note_statut}        <p class="learning-level-note"><strong>Repère, pas étiquette :</strong> {e(niveau_desc)} Tu peux essayer la fiche sans prérequis, demander de l’aide ou choisir une autre matière.</p>
      </div>
    </section>
    <section class="section">
      <div class="container learning-article-layout">
        <article class="learning-lesson-article">
          <section aria-labelledby="objectif-fiche"><h2 id="objectif-fiche">Ce que tu vas essayer</h2><p>{e(fiche["objectif"])}</p></section>
          <section aria-labelledby="situation-fiche"><h2 id="situation-fiche">Une situation de départ</h2><p class="learning-example">{e(fiche["situation"])}</p></section>
          <aside class="learning-analogy" data-analogie aria-labelledby="analogie-fiche"><p class="eyebrow">Analogie du quotidien</p><h2 id="analogie-fiche">{e(fiche["analogie_titre"])}</h2><p>{e(fiche["analogie"])}</p><p class="learning-analogy-limit"><strong>Limite de l’image :</strong> {e(fiche["limite_analogie"])}</p></aside>
          <section aria-labelledby="notions-fiche"><h2 id="notions-fiche">Quelques mots utiles</h2>{vocabulaire}</section>
          <section aria-labelledby="methode-fiche"><h2 id="methode-fiche">Une méthode possible</h2>{demarche}</section>
{exemples_code}
          <section aria-labelledby="exercice-fiche"><h2 id="exercice-fiche">À toi d’essayer</h2><p>{e(fiche["exercice"])}</p><details class="learning-answer"><summary>Afficher une aide</summary><p>{e(fiche["aide"])}</p></details><details class="learning-answer"><summary>Afficher une correction possible</summary>{correction}<p>La correction montre un chemin possible. Pour un calcul, vérifie aussi chaque étape et le résultat.</p></details></section>
          <section aria-labelledby="retenir-fiche"><h2 id="retenir-fiche">Pour retenir</h2>{a_retenir}<p><strong>Et dans une autre situation :</strong> {e(fiche["transferer"])}</p></section>
          <section class="learning-sources" aria-labelledby="sources-fiche"><h2 id="sources-fiche">Sources facultatives et limites</h2><p>Tu peux suivre cette fiche sans ouvrir ces liens : les notions, les exemples, la démarche, l’aide et la correction sont présentés sur cette page. Les sources facultatives servent à vérifier ou approfondir. Pour une décision ou une démarche réelle où les règles peuvent changer, vérifie les consignes actuelles d’un service compétent avant d’agir.</p><ul>{sources}</ul>{note_revue}</section>
        </article>
        <aside class="learning-lesson-aside" aria-label="Poursuivre l’apprentissage"><p class="eyebrow">Tu choisis la suite</p><h2>Un autre point de départ ?</h2><p>Change de matière, de repère ou de format quand tu le souhaites. La page ne note pas et ne suit pas ta progression.</p><a class="button" href="../../apprendre.html">Parcourir toutes les fiches</a><p><a href="../../simulateur.html">Découvrir le simulateur M.R.S.C</a></p></aside>
      </div>
    </section>'''
    return page_enveloppe(
        f'{fiche["titre"]} — Fiche d’apprentissage | M.R.S.C',
        fiche["resume"],
        contenu,
        prefixe="../../",
        page="apprendre",
        canonique=f'{BASE_URL}apprendre/fiches/{fiche["id"]}.html',
    ).replace(
        '<head>',
        f'<head>\n  <meta name="mrsc-fiche-id" content="{e(fiche["id"])}">\n'
        f'  <meta name="mrsc-matiere" content="{e(fiche["matiere_id"])}">\n'
        f'  <meta name="mrsc-niveau" content="{fiche["niveau"]}">\n'
        f'  <meta name="mrsc-revue" content="{e(fiche["revue_le"])}">',
        1,
    )


def render_filters(fiches: list[dict]) -> str:
    matieres = sorted({(fiche["matiere_id"], fiche["matiere"]) for fiche in fiches}, key=lambda item: item[1].casefold())
    options = '<option value="">Toutes les matières</option>' + "".join(
        f'<option value="{e(identifiant)}">{e(libelle)}</option>' for identifiant, libelle in matieres
    )
    return f'''      <form class="learning-filters" data-learning-filters aria-label="Filtrer les fiches d’apprentissage">
        <div class="learning-filter-field"><label for="recherche-fiches">Rechercher un sujet</label><input type="search" id="recherche-fiches" name="q" placeholder="Ex. budget, durée, image" data-filter-search></div>
        <div class="learning-filter-field"><label for="matiere-fiches">Matière</label><select id="matiere-fiches" name="matiere" data-filter-subject>{options}</select></div>
        <div class="learning-filter-field"><label for="niveau-fiches">Repère de difficulté</label><select id="niveau-fiches" name="niveau" data-filter-level><option value="">Tous les repères</option><option value="1">1 — Reprendre les bases</option><option value="2">2 — Consolider</option><option value="3">3 — Raisonner</option><option value="4">4 — Approfondir</option></select></div>
        <button class="button button-secondary learning-filter-reset" type="reset" data-filter-reset>Effacer les filtres</button>
      </form>'''


def render_fiche_card(fiche: dict) -> str:
    niveau_label = NIVEAUX[fiche["niveau"]][0]
    sources = fiche.get("sources", [])
    source_principale = sources[0] if sources else {"titre": "Sources indiquées dans la fiche"}
    autres_sources = len(sources) - 1
    complement = f' · + {autres_sources} autre(s)' if autres_sources > 0 else ""
    horizon = fiche.get("horizon_contenu", "")
    horizon_meta = f'<span>Horizon du contenu : {e(horizon)}</span>' if horizon else ""
    statut = fiche.get("statut_editorial", "")
    statut_meta = f'<span>Statut : {e(statut)}</span>' if statut else ""
    mots = " ".join((
        fiche["titre"], fiche["resume"], fiche["matiere"], fiche["analogie_titre"],
        fiche["analogie"], horizon, statut, fiche.get("note_statut_editorial", ""),
        *(source.get("titre", "") for source in sources),
    ))
    return f'''        <li class="learning-catalogue-item" data-fiche-card data-matiere="{e(fiche["matiere_id"])}" data-niveau="{fiche["niveau"]}" data-recherche="{e(mots.casefold())}">
          <article class="learning-catalogue-card">
            <div class="learning-lesson-meta"><span>{e(fiche["matiere"])}</span>{horizon_meta}{statut_meta}<span>Repère {fiche["niveau"]} · {e(niveau_label)}</span><span>{fiche["minutes"]} min</span></div>
            <h3><a href="apprendre/fiches/{e(fiche["id"])}.html">{e(fiche["titre"])}</a></h3>
            <p>{e(fiche["resume"])}</p>
            <p class="learning-card-analogy"><strong>Analogie :</strong> {e(fiche["analogie_titre"])}</p>
            <p class="learning-card-source"><strong>Source :</strong> <a href="apprendre/fiches/{e(fiche["id"])}.html#sources-fiche">{e(source_principale["titre"])}</a>{e(complement)}</p>
            <a class="learning-card-link" href="apprendre/fiches/{e(fiche["id"])}.html">Ouvrir la fiche complète</a>
          </article>
        </li>'''


def render_coverage(domains: list[dict], fiches_by_id: dict[str, dict]) -> tuple[str, list[str]]:
    sorties = []
    compte_rendus = []
    for domain in domains:
        topics = domain["sujet"]
        counts = Counter(topic["statut"] for topic in topics)
        titre_statut = f'{counts["actif"] + counts["partiel"]} repère(s) commencé(s) sur {len(topics)} · {counts["a-creer"] + counts["revue-experte"]} à développer'
        lignes = []
        for topic in topics:
            statut = topic["statut"]
            state = STATUTS[statut]
            lien_fiches = ""
            if topic["fiches"]:
                liens = " · ".join(
                    f'<a href="apprendre/fiches/{e(fid)}.html">{e(fiches_by_id[fid]["titre"])}</a>'
                    for fid in topic["fiches"]
                )
                lien_fiches = f'<p class="learning-coverage-links">Fiche(s) : {liens}</p>'
            lignes.append(
                f'<li class="learning-coverage-topic learning-coverage-topic-{e(statut)}">'
                f'<span class="learning-coverage-status">{e(state)}</span>'
                f'<strong>{e(topic["titre"])}</strong>{lien_fiches}</li>'
            )
        contenu_lignes = "".join(lignes)
        sorties.append(
            f'<details class="learning-coverage-domain"><summary><span><strong>{e(domain["titre"])}</strong>'
            f'<small>{e(titre_statut)}</small></span></summary>'
            f'<p>{e(domain["intention"])}</p><ul>{contenu_lignes}</ul></details>'
        )
        compte_rendus.append(f'- **{domain["titre"]}** — {titre_statut}.')
    return "\n".join(sorties), compte_rendus


def render_catalogue(fiches: list[dict], domains: list[dict], objectif_fiches: int) -> str:
    by_id = {fiche["id"]: fiche for fiche in fiches}
    couverture, _ = render_coverage(domains, by_id)
    cartes = "\n".join(render_fiche_card(fiche) for fiche in fiches)
    prototypes = sum(bool(fiche.get("statut_editorial")) for fiche in fiches)
    fiches_sans_prototype = len(fiches) - prototypes
    resume_catalogue = f'{fiches_sans_prototype} fiche{"s" if fiches_sans_prototype != 1 else ""}'
    objectif_libelle = f"{objectif_fiches:,}".replace(",", " ")
    if prototypes:
        resume_catalogue += f' et {prototypes} prototype{"s" if prototypes != 1 else ""} à relire'
    hero = f'''    <section class="learning-hero learning-catalogue-hero">
      <div class="container learning-hero-grid">
        <div class="learning-hero-copy">
          <p class="eyebrow">Apprendre · comprendre · pratiquer</p>
          <h1>Des fiches autonomes pour la vie d’aujourd’hui.</h1>
          <p class="learning-intro">Tu peux commencer par un sujet utile, sans compte, sans note et sans prérequis. Chaque fiche tient debout seule, part d’une situation concrète et utilise une analogie du quotidien pour éclairer la notion. L’explication, l’essai, l’aide et la correction sont sur le site M.R.S.C ; les liens de sources sont facultatifs.</p>
          <p class="learning-level-note"><strong>Cap visé :</strong> construire peu à peu des ressources des bases du CP jusqu’aux spécialités et à la recherche doctorale, dans les différentes matières. Le catalogue recense {resume_catalogue}. Il reste un premier ensemble incomplet ; la carte ci-dessous nomme les sujets qui restent à créer.</p>
          <p class="learning-level-note"><strong>Ambition éditoriale de long terme :</strong> viser {objectif_libelle} fiches autonomes, distinctes, relues et entretenues. Ce nombre est un objectif de travail, pas l’offre actuelle ni une promesse de couverture exhaustive.</p>
          <div class="hero-actions"><a class="button" href="#catalogue-fiches">Choisir une fiche</a><a class="button button-secondary" href="#couverture">Voir les sujets à développer</a></div>
          <p class="learning-reassurance"><strong>Ton parcours ne te définit pas.</strong> Les repères de difficulté sont des indications, pas des niveaux à réussir. Tu peux avancer différemment en français, en mathématiques ou dans une autre matière.</p>
        </div>
        <aside class="learning-principles" aria-labelledby="principes-apprentissage"><p class="eyebrow">Une règle éditoriale durable</p><h2 id="principes-apprentissage">Partir du réel, puis revenir au réel.</h2><ul><li>Une analogie concrète dans chaque fiche, avec ses limites expliquées.</li><li>Des notions définies, une méthode découpée et un essai facultatif.</li><li>Des corrections masquées : tu les ouvres quand tu le souhaites.</li><li>Des repères par matière et difficulté, sans test ni étiquette.</li></ul></aside>
      </div>
    </section>'''
    grille = f'''    <section class="section" id="catalogue-fiches" aria-labelledby="titre-catalogue-fiches">
      <div class="container">
        <div class="section-heading"><p class="eyebrow">Catalogue de départ · {resume_catalogue}</p><h2 id="titre-catalogue-fiches">Choisir une fiche selon son besoin</h2><p>Les exemples sont fictifs lorsqu’ils décrivent une situation. Chaque carte indique une source à consulter ; la fiche complète donne toutes ses sources, ses limites et sa date de revue. Une correction possible n’est pas une note : plusieurs chemins peuvent fonctionner.</p></div>
{render_filters(fiches)}
        <p class="learning-filter-count" data-filter-count role="status" aria-live="polite" aria-atomic="true">{resume_catalogue}. Les filtres interactifs nécessitent JavaScript ; les liens restent accessibles ci-dessous.</p>
        <p class="learning-no-results" data-filter-empty hidden>Aucune entrée du catalogue ne correspond à ces critères. Essaie un autre mot ou efface les filtres.</p>
        <ul class="learning-catalogue-grid" data-fiche-list>
{cartes}
        </ul>
      </div>
    </section>'''
    domains_html = f'''    <section class="section section-muted" id="couverture" aria-labelledby="titre-couverture">
      <div class="container">
        <div class="section-heading"><p class="eyebrow">Carte des apprentissages à construire</p><h2 id="titre-couverture">Ce catalogue a des trous, et nous les nommons.</h2><p>Les thèmes marqués « à créer » ne sont pas encore couverts par une fiche publique. « Partiel » signale qu’une première entrée existe mais qu’elle ne suffit pas à couvrir le sujet. Pour la santé, les premiers secours et les règles de droit, une relecture spécialisée est nécessaire avant publication.</p></div>
        <div class="learning-coverage-list">{couverture}</div>
        <p class="learning-level-note"><strong>Comment lire la carte :</strong> « fiche disponible » signifie qu’une première fiche existe ; « début de couverture » indique un contenu incomplet ; « à créer » et « relecture spécialisée » désignent du travail restant. Aucun statut ne signifie que l’ensemble des savoirs est couvert.</p>
      </div>
    </section>'''
    how_to = '''    <section class="section" id="reperes" aria-labelledby="titre-reperes">
      <div class="container">
        <div class="section-heading"><p class="eyebrow">Choisir son point de départ</p><h2 id="titre-reperes">Des repères de difficulté, jamais des étiquettes.</h2><p>Les cycles de l’école française inspirent certains repères ; ils ne mesurent ni la valeur ni les capacités d’une personne adulte. Le repère peut changer selon la matière.</p></div>
        <ol class="learning-level-grid">
          <li><article class="learning-level-card"><span class="learning-level-number">Repère 1</span><p class="learning-school-reference">Départ libre</p><h3>Reprendre les bases</h3><p>Lire une consigne, repérer une information, compter et faire un premier calcul.</p></article></li>
          <li><article class="learning-level-card"><span class="learning-level-number">Repère 2</span><p class="learning-school-reference">Consolider</p><h3>Relier des étapes</h3><p>Comprendre un document, combiner des calculs et s’exercer dans une situation familière.</p></article></li>
          <li><article class="learning-level-card"><span class="learning-level-number">Repère 3</span><p class="learning-school-reference">Raisonner</p><h3>Comparer et expliquer</h3><p>Examiner une source, lire des données et expliquer comment on arrive à une réponse.</p></article></li>
          <li><article class="learning-level-card"><span class="learning-level-number">Repère 4</span><p class="learning-school-reference">Approfondir</p><h3>Transférer et nuancer</h3><p>Réutiliser une notion dans un contexte nouveau, en tenant compte des limites et de l’incertitude.</p></article></li>
        </ol>
        <p class="learning-level-note"><strong>Pas de parcours imposé :</strong> tu peux commencer au repère qui t’est utile, ouvrir ou laisser fermée la correction, changer de sujet et revenir en arrière.</p>
      </div>
    </section>'''
    contexte = '''    <section class="section section-muted" id="experiences" aria-labelledby="titre-experiences">
      <div class="container learning-work-panel">
        <div><p class="eyebrow">Apprendre depuis son expérience</p><h2 id="titre-experiences">Le quotidien et le travail sont aussi des lieux d’apprentissage.</h2><p>Un horaire, une recette, un trajet, une tâche d’équipe ou une démarche peut servir de point d’appui. On relie une notion à ce que l’on sait déjà, puis on essaie de la réutiliser ailleurs.</p><p>Les ressources sont gratuites et non certifiantes. Elles ne remplacent ni une formation adaptée ni un accompagnement si tu en as besoin.</p></div>
        <ol class="learning-work-steps"><li><span>1</span><div><strong>Choisir une situation connue</strong><p>Un document, un calcul ou une question du quotidien.</p></div></li><li><span>2</span><div><strong>Nommer un petit objectif</strong><p>Une action ou une notion à comprendre.</p></div></li><li><span>3</span><div><strong>Essayer et vérifier</strong><p>Sans note : la correction est là si tu la demandes.</p></div></li></ol>
      </div>
    </section>'''
    ecosysteme = '''    <section class="section" id="ecosysteme" aria-labelledby="titre-ecosysteme">
      <div class="container"><div class="section-heading"><p class="eyebrow">Un écosystème cohérent</p><h2 id="titre-ecosysteme">Comprendre, apprendre et examiner des choix.</h2><p>Chaque outil doit montrer ce qu’il permet de faire et ce qu’il ne permet pas de conclure.</p></div>
        <div class="learning-ecosystem-grid"><article class="learning-ecosystem-card"><p class="learning-subject-label">Le cadre citoyen</p><h3>M.R.S.C</h3><p>Découvrir l’association et ses ressources.</p><a href="index.html">Voir l’accueil</a></article><article class="learning-ecosystem-card"><p class="learning-subject-label">Les apprentissages</p><h3>Fiches autonomes</h3><p>Comprendre une notion et essayer à son rythme.</p><a href="#catalogue-fiches">Parcourir les fiches</a></article><article class="learning-ecosystem-card"><p class="learning-subject-label">L’outil de réflexion</p><h3>Simulateur</h3><p>Explorer des hypothèses. Un modèle n’est pas une prédiction ni un verdict.</p><a href="simulateur.html">Comprendre le simulateur</a></article><article class="learning-ecosystem-card learning-ecosystem-card-pending"><p class="learning-subject-label">À documenter</p><h3>EVA</h3><p>Sa mission, ses fonctions et ses conditions d’usage restent à confirmer.</p><p class="learning-pending-note">Aucune fonction d’EVA n’est annoncée ici.</p></article></div>
      </div>
    </section>'''
    contribution = '''    <section class="section learning-feedback" aria-labelledby="titre-contribution"><div class="container"><div class="learning-feedback-panel"><div><p class="eyebrow">Améliorer les ressources</p><h2 id="titre-contribution">Une analogie ne fonctionne pas pour toi ?</h2><p>Tu peux proposer un autre exemple ou signaler un sujet manquant à <a href="mailto:assomrsc@gmail.com?subject=Ressources%20d%E2%80%99apprentissage">assomrsc@gmail.com</a>. N’envoie pas de donnée sensible ni de détail personnel : un message volontaire est transmis à l’adresse de contact et n’est pas anonyme. Aucune réponse immédiate n’est promise.</p></div><a class="button button-secondary" href="mailto:assomrsc@gmail.com?subject=Ressources%20d%E2%80%99apprentissage">Écrire au M.R.S.C</a></div></div></section>'''
    sources = '''    <section class="trace-section"><div class="container trace-panel"><div><p class="eyebrow">Sources et méthode</p><h2>Une première carte, à relire et à compléter</h2><ul class="trace-list"><li>Les repères de cycle sont des indications, non une orientation ou une certification : <a href="https://www.education.gouv.fr/le-socle-commun-de-connaissances-de-competences-et-de-culture-12512" target="_blank" rel="noopener noreferrer">Ministère de l’Éducation nationale — socle commun</a>.</li><li>Les champs d’études et niveaux de programmes sont comparés à la classification internationale de l’<a href="https://isced.uis.unesco.org/about/" target="_blank" rel="noopener noreferrer">UNESCO UIS — ISCED/ISCED-F</a> ; ce repère n’est ni un diplôme M.R.S.C ni un classement des personnes.</li><li>Les apprentissages peuvent partir de situations concrètes et du travail : <a href="https://www.anlci.gouv.fr/nos-piliers/lillettrisme-au-travail/" target="_blank" rel="noopener noreferrer">ANLCI — compétences de base et travail</a>.</li><li>La clarté et l’accessibilité restent à tester avec des personnes concernées : <a href="https://www.w3.org/TR/WCAG22/" target="_blank" rel="noopener noreferrer">W3C — WCAG 2.2</a>.</li><li>La cartographie complète des domaines, des sujets commencés et des lacunes est suivie dans la veille éditoriale du dépôt.</li></ul></div><a class="button button-secondary" href="transparence.html">Voir la méthode et les sources</a></div></section>'''
    contenu = hero + grille + how_to + domains_html + contexte + ecosysteme + contribution + sources
    page = page_enveloppe(
        "Apprendre à son rythme — fiches autonomes | M.R.S.C",
        "Fiches d’apprentissage gratuites et autonomes, par matière et difficulté, avec des analogies du quotidien et une carte explicite des sujets à créer.",
        contenu,
        page="apprendre",
        canonique=f"{BASE_URL}apprendre.html",
    )
    page = page.replace(
        '</head>',
        '  <script src="assets/js/apprentissage.js" defer></script>\n</head>',
        1,
    )
    return page


def render_matrix(fiches: list[dict], domains: list[dict]) -> str:
    derniere_revue = max(date.fromisoformat(fiche["revue_le"]) for fiche in fiches).isoformat()
    output = [
        "# Couverture des savoirs de base — carte éditoriale vivante",
        "",
        f"**Dernière revue éditoriale déclarée : {derniere_revue}.** Ce document est généré depuis `docs/apprentissage/referentiel.toml` et `catalogue.toml`. Il distingue les fiches publiées des thèmes qui restent à créer. Il ne présente pas le catalogue comme complet, officiel ou certifiant.",
        "",
        "L’objectif de couverture est de progresser des bases du CP vers les matières générales et professionnelles, les études supérieures, les spécialisations et la recherche doctorale. Cet objectif n’est pas l’état actuel du catalogue : les lacunes sont indiquées et la carte reste évolutive.",
        "",
        "Les repères de difficulté servent à choisir un point de départ, jamais à classer les personnes. Une situation de travail, de famille, de loisir ou de vie citoyenne peut servir d’entrée. Chaque fiche publiée doit comporter une analogie concrète, son point de correspondance et la limite de l’image.",
        "",
        "",
        "## Lecture des statuts",
        "",
        "- **Fiche disponible** : une première ressource existe ; cela ne signifie pas que le domaine est complet.",
        "- **Début de couverture — à approfondir** : une fiche ouvre le sujet mais plusieurs notions, publics ou contextes restent à traiter.",
        "- **À créer** : aucune fiche correspondante n’est encore publiée.",
        "- **À créer avec une relecture spécialisée** : préparation et contrôle par une personne compétente requis avant publication, notamment pour les informations de santé et de sécurité.",
        "",
        "## Domaines, fiches et lacunes",
        "",
    ]
    for domain in domains:
        topics = domain["sujet"]
        counts = Counter(topic["statut"] for topic in topics)
        output.extend([f'### {domain["titre"]}', "", domain["intention"], ""])
        output.append("| Sujet | Statut | Fiches de première version / suite à donner |")
        output.append("| --- | --- | --- |")
        for topic in topics:
            if topic["fiches"]:
                ressources = "<br>".join(
                    f'[`{fid}`](../apprendre/fiches/{fid}.html)' for fid in topic["fiches"]
                )
            elif topic["statut"] == "revue-experte":
                ressources = "À cadrer avec une personne compétente, puis rechercher des sources officielles à jour."
            else:
                ressources = "Lacune identifiée ; fiche à définir et à relire avant publication."
            output.append(f'| {topic["titre"]} | {STATUTS[topic["statut"]]} | {ressources} |')
        output.extend(
            [
                "",
                f'**Bilan indicatif :** {counts["actif"]} sujet(s) avec une fiche signalée comme disponible, '
                f'{counts["partiel"]} sujet(s) commencés mais incomplets, '
                f'{counts["a-creer"]} sujet(s) à créer, '
                f'{counts["revue-experte"]} sujet(s) demandant une relecture spécialisée sur {len(topics)} sujets suivis. '
                "Ces comptes décrivent la carte éditoriale, pas une mesure du niveau d’apprentissage.",
                "",
            ]
        )
    output.extend(
        [
            "## Règles de suivi et de publication",
            "",
            "1. Le script `outils/construire-apprentissages.py` vérifie les métadonnées, les sources HTTPS, la présence d’une analogie et de sa limite, la correspondance entre fiches et thèmes, les sorties HTML et les échéances de revue.",
            "2. Le workflow `.github/workflows/veille-apprentissages.yml` exécute un contrôle hebdomadaire et sur les modifications du catalogue. Il produit un rapport dans les Actions et crée ou met à jour une seule issue de veille afin de garder les lacunes visibles sans en ouvrir une par sujet.",
            "3. L’automatisation signale les dates de revue échues et les trous de couverture ; elle ne modifie pas un contenu pédagogique sans relecture humaine. Une source accessible n’est pas automatiquement actuelle ou suffisante.",
            "4. Les sujets de droit, de santé, de sécurité, de finances et d’actualité sont priorisés pour une vérification plus fréquente et une relecture spécialisée quand le risque l’exige.",
            "5. Les fiches restent gratuites, sans compte, note, test d’entrée ni suivi des réponses. Les retours volontaires ne demandent pas de raconter une situation personnelle.",
            "6. Les formulations, analogies et exercices sont conçus pour les fiches M.R.S.C ; une source protégée ne sert pas de texte à paraphraser. Réutiliser une œuvre seulement si sa permission ou sa licence l’autorise, en respectant ses conditions.",
            "",
            "## Sources de cadrage",
            "",
            "- [UNESCO UIS — ISCED et domaines d’études ISCED-F](https://isced.uis.unesco.org/about/) et [FAQ sur les niveaux](https://isced.uis.unesco.org/q-and-a/) : grille internationale de périmètre, pas classement des personnes ni équivalence automatique des diplômes.",
            "- [Ministère de l’Éducation nationale — socle commun](https://www.education.gouv.fr/le-socle-commun-de-connaissances-de-competences-et-de-culture-12512) et [programmes scolaires](https://www.education.gouv.fr/programmes-et-horaires-l-ecole-elementaire-9011). Les cycles aident à ranger des notions ; ils ne sont pas un test d’adulte.",
            "- [ANLCI — compétences de base et travail](https://www.anlci.gouv.fr/nos-piliers/lillettrisme-au-travail/) et [apprendre en situation de travail](https://www.anlci.gouv.fr/app/uploads/2025/04/20250910_Prez-webinaire-AFEST.pdf).",
            "- [CléA — domaines du socle professionnel](https://www.certificat-clea.fr/employeurs/le-socle/). Référence de cartographie uniquement : M.R.S.C ne délivre pas cette certification.",
            "- [W3C — WCAG 2.2](https://www.w3.org/TR/WCAG22/) et [contenus utilisables pour les besoins cognitifs et d’apprentissage](https://www.w3.org/TR/coga-usable/). Les contrôles techniques ne remplacent pas les essais avec des personnes concernées.",
            "- [CNIL — données personnelles et transparence](https://www.cnil.fr/fr/passer-laction/rgpd-les-premieres-etapes).",
            "",
        ]
    )
    return "\n".join(output)


def render_sitemap(fiches: list[dict]) -> str:
    """Déclare les pages publiques et fiches au moteur d’indexation."""
    pages = (
        "",
        "apprendre.html",
        "ia-societe.html",
        "simulateur.html",
        "simulateur/",
        "documents.html",
        "liens-utiles.html",
        "localisation.html",
        "nous-contacter.html",
        "transparence.html",
        "confidentialite.html",
    )
    urls = [BASE_URL + page for page in pages]
    urls.extend(f'{BASE_URL}apprendre/fiches/{fiche["id"]}.html' for fiche in fiches)
    entrees = "\n".join(f"  <url><loc>{html.escape(url)}</loc></url>" for url in urls)
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        f"{entrees}\n"
        "</urlset>\n"
    )


def valider_sources(fiches: list[dict], domains: list[dict]) -> None:
    erreurs: list[str] = []
    ids = [fiche.get("id", "") for fiche in fiches]
    doublons = [ident for ident, compte in Counter(ids).items() if compte > 1]
    if doublons:
        erreurs.append("identifiants de fiches dupliqués : " + ", ".join(doublons))
    domaines = {domain["id"]: domain for domain in domains}
    if len(domaines) != len(domains):
        erreurs.append("identifiants de domaines dupliqués")
    fiche_ids = set(ids)
    utilises: set[str] = set()
    domaines_de_reference: dict[str, set[str]] = {}
    sujets_vus: set[str] = set()
    for domain in domains:
        for topic in domain.get("sujet", []):
            if topic["id"] in sujets_vus:
                erreurs.append(f'sujet cartographié plusieurs fois : {topic["id"]}')
            sujets_vus.add(topic["id"])
            statut = topic.get("statut")
            if statut not in STATUTS:
                erreurs.append(f'statut inconnu pour {topic["id"]} : {statut}')
            doit_avoir_fiche = statut in ("actif", "partiel")
            if bool(topic.get("fiches")) != doit_avoir_fiche:
                erreurs.append(f"statut et fiches associés incohérents : {topic['id']}")
            for fid in topic.get("fiches", []):
                if fid not in fiche_ids:
                    erreurs.append(f"fiche inconnue référencée par {topic['id']} : {fid}")
                else:
                    utilises.add(fid)
                    domaines_de_reference.setdefault(fid, set()).add(domain["id"])
    for fiche in fiches:
        if fiche["domaine"] not in domaines:
            erreurs.append(f'domaine absent du référentiel pour {fiche["id"]} : {fiche["domaine"]}')
        if fiche["id"] not in utilises:
            erreurs.append(f'fiche non reliée à la cartographie : {fiche["id"]}')
        if fiche["domaine"] not in domaines_de_reference.get(fiche["id"], set()):
            erreurs.append(f'fiche non reliée à son domaine principal : {fiche["id"]}')
        if fiche.get("niveau") not in NIVEAUX:
            erreurs.append(f'niveau hors repère 1–4 pour {fiche["id"]}')
        if not fiche.get("analogie", "").strip() or not fiche.get("limite_analogie", "").strip():
            erreurs.append(f'analogie ou limite manquante pour {fiche["id"]}')
        if not fiche.get("sources"):
            erreurs.append(f'aucune source déclarée pour {fiche["id"]}')
        if fiche.get("statut_editorial") and not fiche.get("note_statut_editorial"):
            erreurs.append(f'statut éditorial sans explication pour {fiche["id"]}')
        if fiche.get("note_statut_editorial") and not fiche.get("statut_editorial"):
            erreurs.append(f'note éditoriale sans statut pour {fiche["id"]}')
        exemples_code = fiche.get("exemples_code", [])
        if not isinstance(exemples_code, list):
            erreurs.append(f'exemples de code non valides pour {fiche["id"]}')
        else:
            for index, exemple in enumerate(exemples_code, 1):
                champs_code = ("titre", "langage", "contenu", "explication")
                if not isinstance(exemple, dict) or any(not isinstance(exemple.get(champ), str) or not exemple[champ].strip() for champ in champs_code):
                    erreurs.append(f'exemple de code {index} incomplet pour {fiche["id"]}')
                    continue
                if not re.fullmatch(r"[A-Za-z0-9_+#.-]{1,32}", exemple["langage"]):
                    erreurs.append(f'étiquette de langage de code non valide pour {fiche["id"]} : {exemple["langage"]}')
                if len(exemple["contenu"]) > 4_000:
                    erreurs.append(f'exemple de code trop long pour {fiche["id"]}')
        for source in fiche.get("sources", []):
            url = source.get("url", "")
            if urlparse(url).scheme != "https" or not urlparse(url).netloc:
                erreurs.append(f'URL de source non HTTPS pour {fiche["id"]} : {url}')
            if fiche.get("statut_editorial"):
                for champ_source in ("licence_source", "droits_controles_le", "mode_utilisation", "utilisation"):
                    if not source.get(champ_source):
                        erreurs.append(f'métadonnée de droits {champ_source} absente pour {fiche["id"]} : {source.get("titre", url)}')
            mode = source.get("mode_utilisation")
            if mode and mode not in MODES_UTILISATION_SOURCE:
                erreurs.append(f'mode d’utilisation de source inconnu pour {fiche["id"]} : {mode}')
            licence_source = source.get("licence_source", "")
            utilisation = source.get("utilisation", "").casefold()
            if mode == "reference-factuelle" and not any(
                terme in utilisation for terme in ("aucun", "aucune", "sans reprise", "non reproduit")
            ):
                erreurs.append(f'usage factuel sans confirmation d’absence de reprise pour {fiche["id"]} : {source.get("titre", url)}')
            if mode in ("reutilisation-sous-licence", "permission-expresse") and "non vérifiée" in licence_source.casefold():
                erreurs.append(f'droits de réutilisation non vérifiés pour {fiche["id"]} : {source.get("titre", url)}')
            if source.get("droits_controles_le"):
                try:
                    date_controle = date.fromisoformat(source["droits_controles_le"])
                    if date_controle > date.today():
                        erreurs.append(f'date de contrôle des droits dans le futur pour {fiche["id"]}')
                except (ValueError, TypeError):
                    erreurs.append(f'date de contrôle des droits invalide pour {fiche["id"]}')
        for champ in ("resume", "objectif", "situation", "demarche", "exercice", "aide", "correction", "a_retenir", "transferer"):
            if not fiche.get(champ):
                erreurs.append(f'contenu requis absent pour {fiche["id"]} : {champ}')
        try:
            revue = date.fromisoformat(fiche["revue_le"])
            if revue > date.today():
                erreurs.append(f'date de revue dans le futur pour {fiche["id"]}')
        except (ValueError, TypeError, KeyError):
            erreurs.append(f'date de revue invalide pour {fiche.get("id", "fiche inconnue")}')
        if int(fiche.get("intervalle_revue_jours", 0)) < 1:
            erreurs.append(f'intervalle de revue invalide pour {fiche["id"]}')
    if erreurs:
        ERREURS.extend(erreurs)


def render_rapport(fiches: list[dict], domains: list[dict]) -> str:
    aujourd_hui = date.today()
    a_revoir: list[tuple[date, dict]] = []
    for fiche in fiches:
        revue = date.fromisoformat(fiche["revue_le"])
        echeance = revue + timedelta(days=int(fiche["intervalle_revue_jours"]))
        if aujourd_hui > echeance:
            a_revoir.append((echeance, fiche))
    lignes = [
        f"# Veille éditoriale des apprentissages — {aujourd_hui.isoformat()}",
        "",
        f"**Fiches suivies : {len(fiches)}. Domaines cartographiés : {len(domains)}.**",
        "",
        "Cette veille automatique contrôle les dates de relecture, les métadonnées, les analogies, les liens HTTPS déclarés et la cohérence entre le catalogue et la carte des lacunes. Pour les prototypes marqués, elle exige aussi un statut expliqué et, pour chaque source, une licence déclarée ou explicitement non vérifiée, une date de contrôle, un mode d’utilisation et sa description. Elle vérifie les formats et quelques incohérences déclaratives, mais ne visite pas les pages externes, n’interprète pas les licences, ne confirme pas l’absence de reprise ni la justesse d’une explication : ces vérifications demandent une relecture humaine. Les fiches de sécurité numérique sont à revoir au plus tard tous les 90 jours.",
        "",
        "## Fiches dont la date de revue est échue",
        "",
    ]
    if a_revoir:
        for echeance, fiche in sorted(a_revoir, key=lambda item: item[0]):
            sources = "; ".join(
                f'[{source["titre"]}]({source["url"]})'
                for source in fiche.get("sources", [])
            )
            suite = f" Sources à ouvrir : {sources}." if sources else " Sources à rechercher et à valider."
            lignes.append(
                f'- **{fiche["titre"]}** (`{fiche["id"]}`) — échéance de revue : '
                f'{echeance.isoformat()} ; vérifier les exemples et les conduites à tenir.' + suite
            )
    else:
        lignes.append("Aucune échéance de revue éditoriale n’est dépassée à cette date.")
    lignes.extend(["", "## Couverture et sujets à développer", ""])
    manques = 0
    approfondir = 0
    for domain in domains:
        backlog = [topic for topic in domain["sujet"] if topic["statut"] in ("a-creer", "revue-experte")]
        incomplets = [topic for topic in domain["sujet"] if topic["statut"] == "partiel"]
        total = len(domain["sujet"])
        commencés = sum(topic["statut"] in ("actif", "partiel") for topic in domain["sujet"])
        lignes.append(f'### {domain["titre"]} — {commencés} sujet(s) commencé(s) sur {total}')
        lignes.append("")
        if incomplets:
            lignes.append("À approfondir : " + "; ".join(topic["titre"] for topic in incomplets) + ".")
            approfondir += len(incomplets)
        if backlog:
            lignes.append("Lacunes identifiées : " + "; ".join(f'{topic["titre"]} ({STATUTS[topic["statut"]].lower()})' for topic in backlog) + ".")
            manques += len(backlog)
        if not backlog and not incomplets:
            lignes.append("Aucun manque explicite dans cette carte ; continuer la revue des sources et des retours.")
        lignes.append("")
    lignes.extend(
        [
            "## Prochaine vérification humaine recommandée",
            "",
            "1. Ouvrir les sources des fiches à revoir et confirmer leur date, leur portée et les éventuelles mises à jour.",
            "2. Choisir un ou deux sujets du backlog selon les besoins signalés par les personnes apprenantes ; demander une relecture spécialisée lorsque le sujet l’exige.",
            "3. Vérifier l’analogie avec plusieurs personnes : est-elle familière, culturellement située, non stigmatisante et précise sur ses limites ?",
            "4. Contrôler clavier, lecteur d’écran, fort zoom, affichage étroit et compréhension des corrections avec des personnes concernées.",
            "",
            f"**Bilan du robot :** {len(a_revoir)} fiche(s) à relire selon la date, {approfondir} sujet(s) à approfondir, {manques} sujet(s) sans fiche ou demandant une expertise. Ces nombres sont des repères de travail, pas un score de qualité.",
            "",
        ]
    )
    return "\n".join(lignes)


def valider_plan_1000(plan: dict, fiches: list[dict], domains: list[dict]) -> None:
    erreurs: list[str] = []
    objectif = plan.get("objectif_fiches")
    if not isinstance(objectif, int) or isinstance(objectif, bool) or objectif < 1:
        erreurs.append("objectif_fiches doit être un entier positif")
        objectif = 0

    def verifier_quota(cle: str) -> list[dict]:
        lignes = plan.get(cle, [])
        if not isinstance(lignes, list):
            erreurs.append(f"{cle} doit être une liste de quotas")
            return []
        identifiants = []
        total = 0
        for ligne in lignes:
            if not isinstance(ligne, dict):
                erreurs.append(f"entrée invalide dans {cle}")
                continue
            identifiant = ligne.get("id")
            quota = ligne.get("quota")
            if identifiant is None:
                erreurs.append(f"identifiant absent dans {cle}")
            else:
                identifiants.append(identifiant)
            if not isinstance(quota, int) or isinstance(quota, bool) or quota < 0:
                erreurs.append(f"quota invalide dans {cle} pour {identifiant}")
            else:
                total += quota
        doublons = [ident for ident, nombre in Counter(identifiants).items() if nombre > 1]
        if doublons:
            erreurs.append(f"identifiants dupliqués dans {cle} : " + ", ".join(map(str, doublons)))
        if objectif and total != objectif:
            erreurs.append(f"les quotas de {cle} totalisent {total}, objectif attendu : {objectif}")
        return lignes

    quotas_domaines = verifier_quota("domaine")
    quotas_horizons = verifier_quota("horizon")
    quotas_reperes = verifier_quota("repere")
    ids_domaines = {domaine["id"] for domaine in domains}
    ids_plan = {ligne.get("id") for ligne in quotas_domaines if isinstance(ligne, dict)}
    if ids_plan != ids_domaines:
        erreurs.append(
            "domaines du plan et du référentiel différents ; absents du plan : "
            + ", ".join(sorted(ids_domaines - ids_plan))
            + "; inconnus : "
            + ", ".join(sorted(ids_plan - ids_domaines))
        )
    compte_fiches = Counter(fiche.get("domaine", "") for fiche in fiches)
    for ligne in quotas_domaines:
        if isinstance(ligne, dict) and isinstance(ligne.get("quota"), int):
            deja = compte_fiches.get(ligne.get("id"), 0)
            if ligne["quota"] < deja:
                erreurs.append(f"quota inférieur au nombre d’entrées du catalogue pour {ligne.get('id')}")
            if not ligne.get("intention"):
                erreurs.append(f"intention manquante pour le domaine planifié {ligne.get('id')}")
    reperes_plan = {ligne.get("id") for ligne in quotas_reperes if isinstance(ligne, dict)}
    if reperes_plan != set(NIVEAUX):
        erreurs.append("le plan doit répartir les quatre repères de difficulté existants")
    horizons = [ligne for ligne in quotas_horizons if isinstance(ligne, dict)]
    if any(not ligne.get("libelle") for ligne in horizons):
        erreurs.append("libellé absent pour un horizon du plan")
    tranches = plan.get("tranche", [])
    if not isinstance(tranches, list) or not tranches:
        erreurs.append("au moins une tranche de progression est nécessaire")
    else:
        cibles = [ligne.get("cible_cumulee") for ligne in tranches if isinstance(ligne, dict)]
        if len(cibles) != len(tranches) or any(not isinstance(cible, int) or cible < 1 for cible in cibles):
            erreurs.append("cible cumulative invalide dans les tranches")
        elif cibles != sorted(set(cibles)) or cibles[-1] != objectif:
            erreurs.append("les tranches doivent progresser sans doublon et se terminer à l’objectif")
        if any(not ligne.get("intention") or not ligne.get("libelle") for ligne in tranches if isinstance(ligne, dict)):
            erreurs.append("intention ou libellé manquant dans une tranche")
    autonomie = plan.get("autonomie", {})
    if (
        autonomie.get("lecon_autonome") is not True
        or autonomie.get("liens_externes_obligatoires") is not False
        or autonomie.get("comptes_externes_obligatoires") is not False
        or autonomie.get("ressources_chargees_depuis_un_tiers") is not False
    ):
        erreurs.append("le plan doit garder les leçons autonomes et sans dépendance de rendu à un tiers")
    qualite = plan.get("qualite", {})
    if not all(qualite.get(cle) is True for cle in (
        "quotas_non_exhaustifs",
        "une_fiche_egale_un_objectif_distinct",
        "les_versions_et_traductions_ne_comptent_pas_comme_nouvelles_fiches",
        "publication_conditionnee_aux_relectures_et_aux_droits",
        "les_comptages_ne_sont_pas_un_score_de_qualite",
    )):
        erreurs.append("les garde-fous de qualité et de décompte doivent rester actifs")
    if erreurs:
        ERREURS.extend("plan des 1 000 fiches : " + erreur for erreur in erreurs)


def render_plan_1000(plan: dict, fiches: list[dict], domains: list[dict]) -> str:
    objectif = plan["objectif_fiches"]
    objectif_libelle = f"{objectif:,}".replace(",", " ")
    total = len(fiches)
    prototypes = sum(bool(fiche.get("statut_editorial")) for fiche in fiches)
    prototypes_libelle = f'{prototypes} prototype{"s" if prototypes != 1 else ""}'
    sans_marqueur = total - prototypes
    ecart_brut = max(0, objectif - total)
    fiches_par_domaine = Counter(fiche["domaine"] for fiche in fiches)
    prototypes_par_domaine = Counter(
        fiche["domaine"] for fiche in fiches if fiche.get("statut_editorial")
    )
    domaines = {domaine["id"]: domaine for domaine in domains}
    lignes = [
        f"# Cap éditorial : viser {objectif_libelle} fiches d’auto-apprentissage",
        "",
        f"**Plan de travail au {date.today().isoformat()} — cible, pas catalogue disponible.**",
        "",
        f"L’ambition est de construire progressivement {objectif_libelle} fiches distinctes, autonomes et valorisantes. Le catalogue de travail compte actuellement {total} entrées : {sans_marqueur} entrées du corpus initial sans marqueur de prototype et {prototypes_libelle} explicitement à relire. L’écart arithmétique à la cible est de {ecart_brut} entrées ; le nombre de fiches ayant franchi tous les contrôles de publication n’est pas encore suivi.",
        "",
        "Ces nombres décrivent le catalogue et un objectif de planification ; ils ne prouvent ni qu’une fiche a passé toutes les relectures, ni que les sujets proposés sont exhaustifs. L’absence de statut de prototype sur une fiche initiale ne vaut pas validation indépendante. Les versions, traductions et variantes d’un même objectif ne gonflent pas le compte.",
        "",
        "## Répartition indicative par domaine",
        "",
        "Les quotas sont des hypothèses de travail à corriger selon les besoins signalés, les programmes et les avis de spécialistes. Chaque fiche reçoit un domaine principal, même si elle peut créer des liens avec d’autres matières.",
        "",
        "| Domaine | Cible | Entrées actuelles | Prototypes à relire | Écart brut |",
        "| --- | ---: | ---: | ---: | ---: |",
    ]
    for ligne in plan["domaine"]:
        identifiant = ligne["id"]
        deja = fiches_par_domaine.get(identifiant, 0)
        quota = ligne["quota"]
        lignes.append(
            f'| {domaines[identifiant]["titre"]} | {quota} | {deja} | '
            f'{prototypes_par_domaine.get(identifiant, 0)} | {max(0, quota - deja)} |'
        )
    lignes.extend([
        f"| **Total planifié** | **{objectif_libelle}** | **{total}** | **{prototypes}** | **{ecart_brut}** |",
        "",
        "## Horizon principal des contenus",
        "",
        "Chaque fiche reçoit un horizon principal pour équilibrer le programme ; cela ne décrit pas l’âge, la scolarité ni la capacité de la personne qui l’apprend. Les horizons sont des points d’entrée, pas des marches obligatoires.",
        "",
        "| Horizon de contenu | Cible indicative |",
        "| --- | ---: |",
    ])
    for ligne in plan["horizon"]:
        lignes.append(f'| {ligne["libelle"]} | {ligne["quota"]} |')
    lignes.extend([
        f"| **Total** | **{objectif_libelle}** |",
        "",
        "## Répartition indicative des repères de difficulté",
        "",
        "Le repère classe la complexité de la fiche, pas la personne. Il est indépendant de l’horizon scolaire ou professionnel.",
        "",
        "| Repère | Cible indicative |",
        "| --- | ---: |",
    ])
    for ligne in plan["repere"]:
        lignes.append(f'| {ligne["id"]} — {NIVEAUX[ligne["id"]][0]} | {ligne["quota"]} |')
    lignes.extend([
        f"| **Total** | **{objectif_libelle}** |",
        "",
        "## Tranches de construction — sans échéance imposée",
        "",
        "Ces tranches organisent les priorités ; elles ne promettent ni date de livraison ni rythme de production. On ne passe pas à une publication en masse pour atteindre un chiffre.",
        "",
        "| Tranche | Nouveaux emplacements indicatifs | Cible cumulée | Intention |",
        "| --- | ---: | ---: | --- |",
    ])
    precedente = 0
    for ligne in plan["tranche"]:
        nouveaux = ligne["cible_cumulee"] - precedente
        cible_libelle = f'{ligne["cible_cumulee"]:,}'.replace(",", " ")
        lignes.append(f'| {ligne["numero"]} — {ligne["libelle"]} | {nouveaux} | {cible_libelle} | {ligne["intention"]} |')
        precedente = ligne["cible_cumulee"]
    lignes.extend([
        "",
        "## Contrat d’autonomie et de qualité",
        "",
        "- Une fiche contient sa leçon, son exemple original, l’analogie et ses limites, la démarche, l’exercice facultatif, l’aide, la correction et le transfert ; aucun lien, compte ou service externe n’est requis pour apprendre l’objectif.",
        "- Les références externes sont facultatives et documentent la vérification éditoriale ; aucun script, média, police ou contenu tiers n’est chargé automatiquement sur les pages d’apprentissage.",
        "- Chaque fiche ajoute une capacité valorisante : comprendre, faire, décider, créer, coopérer, transmettre ou demander de l’aide, sans dévaloriser les acquis déjà présents.",
        "- Les sujets à risque sont relus par une personne compétente ; l’accessibilité est testée avec des personnes concernées avant de présenter le contenu comme prêt.",
        "- Un objectif d’apprentissage distinct compte pour une fiche ; une correction, une traduction ou une reformulation ne crée pas artificiellement une nouvelle unité.",
        "- Avant diffusion, vérifier originalité, sources et licences, attribution, droits des contributions, compréhension, clavier, lecteur d’écran, zoom, mobile et calendrier de maintenance.",
        f"- Les lacunes restent visibles même à {objectif_libelle} fiches : le chiffre est un cap de développement, jamais une garantie de couvrir tous les savoirs ou toutes les spécialités.",
        "",
        "### Prochaine priorité de réalisation",
        "",
        "Développer une première tranche de fiches courtes et indépendantes pour les bases de lecture, écriture, calcul, données, démarches, vie numérique et autonomie quotidienne. Pour chaque fiche, la relecture de fond, des droits, de l’accessibilité et des essais d’usage reste un passage distinct de la rédaction.",
        "",
    ])
    return "\n".join(lignes)


def generer(fiches: list[dict], domains: list[dict], plan: dict) -> dict[Path, str]:
    produits: dict[Path, str] = {
        ROOT / "apprendre.html": render_catalogue(fiches, domains, plan["objectif_fiches"]),
        MATRIX: render_matrix(fiches, domains),
        ROADMAP_1000: render_plan_1000(plan, fiches, domains),
        ROOT / "sitemap.xml": render_sitemap(fiches),
    }
    for fiche in fiches:
        produits[PUBLIC_DIR / f'{fiche["id"]}.html'] = render_fiche(fiche)
    return produits


def appliquer(produits: dict[Path, str], verifier: bool) -> None:
    changements = []
    for chemin, texte in produits.items():
        if verifier:
            if not chemin.is_file() or chemin.read_text(encoding="utf-8") != texte:
                changements.append(str(chemin.relative_to(ROOT)))
        else:
            chemin.parent.mkdir(parents=True, exist_ok=True)
            chemin.write_text(texte, encoding="utf-8")
    if verifier and changements:
        ERREURS.append("sorties générées absentes ou modifiées : " + ", ".join(changements))
    elif not verifier:
        print(f"{len(produits)} fichier(s) généré(s) ou actualisé(s).")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--verifier", action="store_true", help="vérifier les sorties sans les réécrire")
    parser.add_argument("--rapport", type=Path, help="écrire le rapport de veille à ce chemin")
    args = parser.parse_args()

    try:
        catalogue = lire_toml(CATALOGUE)
        referentiel = lire_toml(REFERENTIEL)
        plan = lire_toml(PLAN_1000)
    except (OSError, tomllib.TOMLDecodeError) as erreur:
        print(f"Impossible de lire les sources éditoriales : {erreur}", file=sys.stderr)
        return 2

    fiches = catalogue.get("fiche", [])
    domains = referentiel.get("domaine", [])
    valider_sources(fiches, domains)
    valider_plan_1000(plan, fiches, domains)
    appliquer(generer(fiches, domains, plan), args.verifier)
    rapport = render_rapport(fiches, domains)
    if args.rapport:
        destination = args.rapport if args.rapport.is_absolute() else ROOT / args.rapport
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(rapport, encoding="utf-8")
    else:
        print(rapport)
    if ERREURS:
        print("\nÉCHECS :", file=sys.stderr)
        for erreur in ERREURS:
            print(f"- {erreur}", file=sys.stderr)
        return 1
    print(f"Contrôle réussi : {len(fiches)} fiches, {len(domains)} domaines, aucune date de revue échue." if not args.verifier else f"Contrôle réussi : {len(fiches)} fiches, {len(domains)} domaines, sorties synchronisées.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
