#!/usr/bin/env python3
"""Génère `simulateur/index.html`, la page du simulateur, à partir du moteur.

Le moteur sert sa page depuis la constante `HTML_PAGE` de
`simulateur/interface.py`, en remplaçant le repère `===SCENARIOS_JSON===` par
le catalogue des scénarios (`simulateur/dashboard.py`). Ce script fait
exactement la même substitution, mais une fois pour toutes : la page devient
un fichier statique publiable (Vercel, GitHub Pages), sans build à chaque
requête. Le générateur ajoute le retour permanent vers M.R.S.C, des réglages
d’affichage et des adaptations responsives et accessibles aux tableaux ; le moteur
amont reste inchangé.

Usage :
    python3 outils/construire-simulateur.py [--verifier]

`--verifier` ne réécrit rien : il signale si le fichier publié a divergé du
moteur (utilisable en CI, ou après une mise à jour du moteur).
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RACINE))

from simulateur.dashboard import SCENARIOS  # noqa: E402
from simulateur.interface import HTML_PAGE  # noqa: E402

SORTIE = RACINE / "simulateur" / "index.html"
PROVENANCE = RACINE / "simulateur" / "PROVENANCE.json"
REPERE = "===SCENARIOS_JSON==="

# Ajouts propres au site : navigation de retour et réglages d’affichage.
# Le moteur amont reste inchangé ; ses règles spécifiques sont surchargées ici.
CSS_RETOUR = """
/* Intégration M.R.S.C : retour permanent et adaptations locales d’affichage. */
:root {
  --accent: #91b2e6;
  --vert: #9bc77a;
  --rouge: #ff9295;
  --ambre: #f2c15f;
  --violet: #b49bd8;
  --rose: #e89ac8;
}
header.entete {
  border-color: #344b79;
  background: linear-gradient(135deg, #1d3268, #26375f);
}
button.primaire {
  border-color: #456d29;
  background: linear-gradient(135deg, #1d3268, #2958a2);
  color: #fff;
}
.site-return-bar {
  position: sticky;
  z-index: 110;
  top: 0;
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: .5rem;
  min-height: 54px;
  margin: -18px -18px 12px;
  padding: 6px 18px;
  border-bottom: 2px solid var(--ambre);
  background: rgba(29, 50, 104, .98);
  box-shadow: 0 8px 22px rgba(0, 0, 0, .24);
  backdrop-filter: blur(12px);
}
.site-return-bar .site-journey-navigation {
  position: static;
  display: flex;
  flex: 1 1 100%;
  align-items: center;
  justify-content: flex-start;
  flex-wrap: wrap;
  gap: .25rem .7rem;
  min-height: 0;
  margin: 0;
  padding: .15rem 0;
  border: 0;
  background: transparent;
  box-shadow: none;
  backdrop-filter: none;
}
.site-return-bar .site-journey-controls {
  display: flex;
  flex-wrap: wrap;
  gap: .35rem;
  width: auto;
  margin: 0;
  padding: 0;
}
.site-return-bar .site-journey-button {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: .3rem;
  min-width: 44px;
  min-height: 44px;
  padding: .4rem .65rem;
  border: 1px solid rgba(255,255,255,.38);
  border-radius: 9px;
  background: #1d3268;
  color: #fff;
  font: inherit;
  font-size: .8rem;
  font-weight: 700;
  line-height: 1.25;
  cursor: pointer;
}
.site-return-bar .site-journey-button:hover:not(:disabled) {
  border-color: var(--ambre);
  background: #26375f;
}
.site-return-bar .site-journey-button[data-journey-action="accueil"] {
  border-color: var(--ambre);
  box-shadow: inset 0 -2px 0 var(--ambre);
}
.site-return-bar .site-journey-button:disabled {
  border-color: #526384;
  background: #17274d;
  color: #d2d9e5;
  cursor: not-allowed;
}
.site-return-bar .site-journey-button[data-journey-action="accueil"]:disabled { box-shadow: none; }
.site-return-bar .site-journey-symbol { font-size: 1rem; }
.site-return-bar .site-journey-status {
  width: auto;
  margin: 0;
  padding: 0;
  color: var(--texte-dim);
  font-size: .72rem;
  line-height: 1.35;
}
.site-return-bar a {
  display: inline-flex;
  flex: 0 1 auto;
  align-items: center;
  gap: .55rem;
  min-height: 44px;
  max-width: 100%;
  padding: .45rem .8rem;
  border: 1px solid rgba(255,255,255,.38);
  border-radius: 9px;
  background: #1d3268;
  color: #fff;
  font-size: .84rem;
  font-weight: 700;
  line-height: 1.25;
  text-decoration: none;
  overflow-wrap: anywhere;
}
.site-return-bar a:hover {
  border-color: var(--ambre);
  background: #26375f;
  color: #fff;
}
.site-return-bar a:focus-visible,
.site-return-bar .site-journey-button:focus-visible,
.sim-display-button:focus-visible {
  outline: 3px solid var(--ambre);
  outline-offset: 3px;
}
.sim-skip-link {
  position: absolute;
  z-index: 1000;
  top: .5rem;
  left: .5rem;
  transform: translateY(-180%);
  padding: .65rem .9rem;
  border: 2px solid var(--ambre);
  border-radius: 8px;
  background: #000;
  color: #fff;
  font-weight: 700;
}
.sim-skip-link:focus {
  transform: translateY(0);
}
.site-return-arrow {
  flex: 0 0 auto;
  color: var(--ambre);
  font-size: 1.15rem;
  line-height: 1;
}
.sim-display-controls {
  display: flex;
  flex: 0 1 auto;
  align-items: center;
  justify-content: flex-end;
  flex-wrap: wrap;
  gap: .35rem;
  margin-left: auto;
}
.sim-display-controls[hidden] {
  display: none;
}
.sim-display-button {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 44px;
  min-height: 44px;
  padding: .4rem .65rem;
  border: 1px solid rgba(255,255,255,.38);
  border-radius: 9px;
  background: #1d3268;
  color: #fff;
  font: inherit;
  font-size: .78rem;
  font-weight: 700;
  line-height: 1.25;
  cursor: pointer;
}
.sim-display-button:hover:not(:disabled) {
  border-color: var(--ambre);
  background: #26375f;
}
.sim-display-button:disabled {
  border-color: #526384;
  background: #17274d;
  color: #d2d9e5;
  cursor: not-allowed;
}
.sim-display-level {
  min-width: 3.8rem;
  color: var(--texte);
  font-size: .8rem;
  font-variant-numeric: tabular-nums;
  font-weight: 700;
  text-align: center;
}
.mrsc-scroll-hint {
  margin: 0 0 6px;
  color: var(--texte-dim);
  font-size: .78rem;
  line-height: 1.5;
}
.mrsc-scroll-region:focus-visible {
  outline: 3px solid var(--accent);
  outline-offset: 3px;
}
.infobulle {
  max-width: min(352px, calc(100vw - 16px));
  max-height: min(60vh, 32rem);
  overflow: auto;
  overflow-wrap: anywhere;
}
html.texte-agrandi { font-size: 125%; }
html.texte-tres-agrandi { font-size: 150%; }
html.espacement-renforce body { line-height: 1.8; }
html.espacement-renforce :is(h1, h2, h3, p, li, label, button, th, td, .aide, .nom, .desc, .libelle, .valeur, .ref, .pastille, .console-verdict, .console-titre) {
  line-height: 1.65;
  letter-spacing: .12em;
  word-spacing: .16em;
  overflow-wrap: anywhere;
}
html.espacement-renforce th,
html.espacement-renforce td { white-space: normal; }
html.espacement-renforce p { margin-block-end: 2em; }
html.espacement-renforce :is(.pastille, .ruban-titre, .ruban-pop, .console-verdict, .levier .valeur, .bulle-bouton) {
  white-space: normal;
  overflow-wrap: anywhere;
}
html.contraste-renforce {
  --bg: #000;
  --panel: #070707;
  --panel-2: #121212;
  --border: #c8d4e5;
  --texte: #fff;
  --texte-dim: #f1f4f8;
  --accent: #7dd3fc;
  --vert: #86efac;
  --rouge: #fca5a5;
  --ambre: #fde68a;
}
html.contraste-renforce a { text-decoration: underline; text-underline-offset: .18em; }
html.contraste-renforce :focus-visible { outline-width: 4px; }
/* Le texte secondaire ne descend pas sous 12 px à la taille de base. */
.metric .libelle,
.infobulle,
.levier .desc,
.levier .source,
.levier .bulle-bouton,
.bulle-levier,
.bulle-levier .bulle-titre,
.pied,
.provenance,
.ruban-veille .ruban-titre,
.ruban-strate,
.ruban-pop,
.ruban-veille button,
.levier.compact .nom,
.levier.compact .valeur,
.puce-effect,
.message-seuil .etiquette,
.message-seuil .source,
.graduations { font-size: .75rem; }
/* Le ruban de veille reste visible sous la barre de retour quand elle tient sur une ligne. */
.conteneur .ruban-veille { top: 54px; }
@media (max-width: 640px) {
  .site-return-bar {
    justify-content: flex-start;
    margin: -10px -10px 10px;
    padding-inline: 10px;
  }
  .sim-display-controls {
    flex: 1 1 100%;
    justify-content: flex-start;
    margin-left: 0;
  }
  .ruban-veille { top: 0; }
  .ruban-veille .console-verdict {
    flex: 1 1 100%;
    max-width: 100%;
    overflow: visible;
    text-overflow: clip;
    white-space: normal;
  }
  .ruban-pop { white-space: normal; }
  .ruban-veille .ruban-actions { width: 100%; margin-left: 0; }
  .ruban-veille button { min-height: 44px; }
  .grille.domaines,
  .leviers-grille,
  .leviers-grille.compacte,
  .console-corps { grid-template-columns: minmax(0, 1fr); }
  .barre-leviers .recherche { flex: 1 1 100%; min-width: 0; min-height: 44px; }
  .barre-leviers label { min-height: 44px; }
  .levier.compact {
    grid-template-columns: minmax(0, 1fr) auto;
    gap: 6px 10px;
  }
  .levier.compact > .nom { grid-column: 1; grid-row: 1; min-width: 0; overflow-wrap: anywhere; }
  .levier.compact > input[type=range] { grid-column: 1 / -1; grid-row: 2; min-height: 44px; }
  .levier.compact > .valeur { grid-column: 2; grid-row: 1; }
  .levier.compact > .bascule { grid-column: 1; grid-row: 2; min-height: 44px; }
  .levier.compact > .bulle-bouton { grid-column: 1 / -1; justify-self: start; min-height: 44px; }
  .levier.compact > .puces,
  .levier.compact > .bulle-levier { grid-column: 1 / -1; }
  .strate { align-items: flex-start; flex-direction: column; gap: .3rem; }
  .strate .valeurs { gap: 8px; }
  .ligne-marge { align-items: flex-start; flex-direction: column; }
  .ligne-marge .droite { white-space: normal; text-align: left; }
  .delta-mesure { flex-wrap: wrap; }
  .domaine .tete { align-items: flex-start; }
  .domaine .indic { min-width: 0; overflow-wrap: anywhere; }
  button { min-height: 44px; }
}
@media (max-width: 380px) {
  header.entete { padding: 14px; }
  section.bloc { padding: 12px; }
  .pastille { white-space: normal; }
  .ruban-strates { flex-wrap: wrap; }
}
@media (any-pointer: coarse) {
  button,
  .site-return-bar a,
  .sim-display-button,
  .levier .bulle-bouton,
  .levier input[type=range] { min-height: 44px; }
  .bascule input { width: 24px; height: 24px; }
}
@media (orientation: landscape) and (max-height: 520px) {
  .ruban-veille { position: static; }
}
@media (prefers-contrast: more) {
  :root {
    --border: #aebbd0;
    --texte-dim: #dbe6f5;
    --accent: #7dd3fc;
  }
  a { text-decoration: underline; text-underline-offset: .18em; }
  button:focus-visible, a:focus-visible { outline-width: 4px; }
}
@media (prefers-reduced-motion: reduce) {
  html { scroll-behavior: auto; }
  *, *::before, *::after {
    scroll-behavior: auto !important;
    animation-duration: .01ms !important;
    transition-duration: .01ms !important;
  }
}
@media (prefers-reduced-transparency: reduce) {
  .site-return-bar { background: #1d3268; backdrop-filter: none; }
}
@media (forced-colors: active) {
  :root {
    color-scheme: light dark;
    --bg: Canvas;
    --panel: Canvas;
    --panel-2: Canvas;
    --border: CanvasText;
    --texte: CanvasText;
    --texte-dim: CanvasText;
    --accent: LinkText;
    --vert: CanvasText;
    --rouge: CanvasText;
    --ambre: CanvasText;
  }
  html.contraste-renforce {
    --bg: Canvas;
    --panel: Canvas;
    --panel-2: Canvas;
    --border: CanvasText;
    --texte: CanvasText;
    --texte-dim: CanvasText;
    --accent: LinkText;
    --vert: CanvasText;
    --rouge: CanvasText;
    --ambre: CanvasText;
  }
  :focus-visible { outline-color: Highlight !important; }
  body, header.entete, section.bloc, .carte, .domaine, .famille,
  .ruban-veille, .site-return-bar, .infobulle {
    background: Canvas !important;
    color: CanvasText !important;
    border-color: CanvasText !important;
    box-shadow: none !important;
    backdrop-filter: none !important;
  }
  a { color: LinkText !important; }
  button, .site-return-bar a, .site-return-bar .site-journey-button, .sim-display-button {
    border: 1px solid ButtonText !important;
    background: ButtonFace !important;
    color: ButtonText !important;
    box-shadow: none !important;
  }
  * { text-shadow: none !important; }
}
"""
LIEN_RETOUR = (
    "\n"
    '<a class="sim-skip-link" href="#contenu-principal">Aller au simulateur</a>\n'
    '<nav id="mrsc-retour-site" class="site-return-bar" aria-label="Navigation de retour, vie privée et réglages d’affichage">\n'
    '  <a href="../index.html" data-site-home><span class="site-return-arrow" aria-hidden="true">←</span>Retour au site M.R.S.C</a>\n'
    '  <a href="../confidentialite.html">Vie privée et données</a>\n'
    '  <div id="mrsc-display-controls" class="sim-display-controls" role="group" aria-label="Réglages d’affichage du simulateur" hidden>\n'
    '    <button class="sim-display-button" type="button" data-sim-text-decrease aria-label="Réduire la taille du texte">A−</button>\n'
    '    <span class="sim-display-level" data-sim-text-level role="status" aria-live="polite" aria-atomic="true">100 %</span>\n'
    '    <button class="sim-display-button" type="button" data-sim-text-increase aria-label="Agrandir la taille du texte">A+</button>\n'
    '    <button class="sim-display-button" type="button" data-sim-contrast aria-pressed="false">Contraste +</button>\n'
    '    <button class="sim-display-button" type="button" data-sim-spacing aria-pressed="false">Interligne +</button>\n'
    '  </div>\n'
    '</nav>\n'
)
SCRIPT_AFFICHAGE = r"""
<script>
(() => {
  const root = document.documentElement;
  const controls = document.getElementById("mrsc-display-controls");
  const decrease = document.querySelector("[data-sim-text-decrease]");
  const increase = document.querySelector("[data-sim-text-increase]");
  const levelOutput = document.querySelector("[data-sim-text-level]");
  const contrastButton = document.querySelector("[data-sim-contrast]");
  const spacingButton = document.querySelector("[data-sim-spacing]");
  const keys = {
    text: "mrsc-texte-niveau",
    contrast: "mrsc-contraste-renforce",
    spacing: "mrsc-espacement-renforce",
  };
  let level = 0;
  let contrast = false;
  let spacing = false;

  const read = (key) => {
    try { return window.localStorage.getItem(key); }
    catch (error) { return null; }
  };
  const save = (key, value) => {
    try { window.localStorage.setItem(key, value); }
    catch (error) { /* Le choix reste actif pour la visite courante. */ }
  };
  const applyLevel = (value) => {
    level = Math.max(0, Math.min(2, value));
    root.classList.toggle("texte-agrandi", level === 1);
    root.classList.toggle("texte-tres-agrandi", level === 2);
    if (levelOutput) levelOutput.textContent = `${[100, 125, 150][level]} %`;
    if (decrease) decrease.disabled = level === 0;
    if (increase) increase.disabled = level === 2;
  };
  const applyContrast = (value) => {
    contrast = Boolean(value);
    root.classList.toggle("contraste-renforce", contrast);
    if (contrastButton) {
      contrastButton.setAttribute("aria-pressed", String(contrast));
      contrastButton.setAttribute("aria-label", contrast
        ? "Désactiver le contraste renforcé" : "Activer le contraste renforcé");
    }
  };
  const applySpacing = (value) => {
    spacing = Boolean(value);
    root.classList.toggle("espacement-renforce", spacing);
    if (spacingButton) {
      spacingButton.setAttribute("aria-pressed", String(spacing));
      spacingButton.setAttribute("aria-label", spacing
        ? "Désactiver l’espacement renforcé" : "Activer l’espacement renforcé");
    }
  };
  const load = () => {
    const savedLevel = read(keys.text);
    const legacy = read("mrsc-texte-agrandi");
    const parsed = savedLevel === null
      ? (legacy === "oui" ? 1 : 0)
      : Number.parseInt(savedLevel, 10);
    applyLevel(Number.isFinite(parsed) ? parsed : 0);
    applyContrast(read(keys.contrast) === "oui");
    applySpacing(read(keys.spacing) === "oui");
  };

  load();
  if (controls) controls.hidden = false;
  decrease?.addEventListener("click", () => {
    applyLevel(level - 1);
    save(keys.text, String(level));
  });
  increase?.addEventListener("click", () => {
    applyLevel(level + 1);
    save(keys.text, String(level));
  });
  contrastButton?.addEventListener("click", () => {
    applyContrast(!contrast);
    save(keys.contrast, contrast ? "oui" : "non");
  });
  spacingButton?.addEventListener("click", () => {
    applySpacing(!spacing);
    save(keys.spacing, spacing ? "oui" : "non");
  });
  window.addEventListener("storage", (event) => {
    if (event.key === null || Object.values(keys).includes(event.key)
        || event.key === "mrsc-texte-agrandi") load();
  });
})();
</script>
"""


def ajouter_zones_defilantes_accessibles(contenu: str) -> str:
    """Nomme et rend clavier-parcourables les tableaux intrinsèquement larges."""
    remplacements = (
        (
            '<div class="defilable"><table id="results-table">',
            '<p class="mrsc-scroll-hint" id="mrsc-hint-resultats">Sur petit écran ou avec un fort zoom, faites défiler ce tableau horizontalement pour lire toutes ses colonnes.</p>\n'
            '    <div class="defilable mrsc-scroll-region" role="region" tabindex="0" aria-label="Tableau des résultats année par année" aria-describedby="mrsc-hint-resultats"><table id="results-table">',
        ),
        (
            '<div class="defilable"><table class="matrice" id="matrice-impacts">',
            '<p class="mrsc-scroll-hint" id="mrsc-hint-matrice">Sur petit écran ou avec un fort zoom, faites défiler la matrice horizontalement pour voir les colonnes de domaines.</p>\n'
            '    <div class="defilable mrsc-scroll-region" role="region" tabindex="0" aria-label="Matrice croisée des impacts par levier et domaine" aria-describedby="mrsc-hint-matrice"><table class="matrice" id="matrice-impacts">',
        ),
    )
    for ancien, nouveau in remplacements:
        if contenu.count(ancien) != 1:
            raise SystemExit(f"Impossible d’adapter une zone de tableau du simulateur ({ancien[:55]}).")
        contenu = contenu.replace(ancien, nouveau, 1)
    return contenu


def provenance() -> dict[str, str]:
    """Provenance du moteur embarqué (dépôt amont, révision, date)."""
    try:
        return json.loads(PROVENANCE.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def ajouter_zone_principale_accessible(contenu: str) -> str:
    """Donne au simulateur une zone principale et une cible de saut clavier."""
    repere_script = """<script>
const SCENARIOS ="""
    page, separateur, suite = contenu.partition(repere_script)
    ouverture = '<div class="conteneur">'
    if not separateur or page.count(ouverture) != 1:
        raise SystemExit("Impossible d’ajouter le repère principal accessible au simulateur.")
    index_fermeture = page.rfind("</div>")
    if index_fermeture < page.find(ouverture):
        raise SystemExit("La zone principale du simulateur n’a pas de fermeture repérable.")
    page = page.replace(ouverture, '<main class="conteneur" id="contenu-principal">', 1)
    page = page[:index_fermeture] + "</main>" + page[index_fermeture + len("</div>"):]
    return page + separateur + suite


def page_complete() -> str:
    scenarios_json = json.dumps(
        {
            cle: {k: v for k, v in valeur.items() if k != "fn"}
            for cle, valeur in SCENARIOS.items()
        },
        ensure_ascii=False,
    )
    contenu = HTML_PAGE.replace(REPERE, scenarios_json)
    if REPERE in contenu:
        raise SystemExit(
            f"Le repère {REPERE} n'a pas été remplacé : la page serait inutilisable."
        )
    contenu = ajouter_zones_defilantes_accessibles(contenu)
    contenu = ajouter_zone_principale_accessible(contenu)

    # L'interface du moteur est autonome et ne connaît pas le site qui l'embarque.
    # Ces ajouts restent dans la couche d'intégration ; le moteur amont est intact.
    if 'id="mrsc-retour-site"' not in contenu:
        fermeture_style = re.search(r"</style\s*>", contenu, re.IGNORECASE)
        ouverture_body = re.search(r"<body\b[^>]*>", contenu, re.IGNORECASE)
        fermeture_body = re.search(r"</body\s*>", contenu, re.IGNORECASE)
        if not fermeture_style or not ouverture_body or not fermeture_body:
            raise SystemExit("Impossible d'ajouter les adaptations du site : balises <style> ou <body> absentes.")
        contenu = contenu[:fermeture_style.start()] + "\n" + CSS_RETOUR + contenu[fermeture_style.start():]
        ouverture_body = re.search(r"<body\b[^>]*>", contenu, re.IGNORECASE)
        fermeture_body = re.search(r"</body\s*>", contenu, re.IGNORECASE)
        assert ouverture_body is not None and fermeture_body is not None
        contenu = contenu[:ouverture_body.end()] + LIEN_RETOUR + contenu[ouverture_body.end():]
        fermeture_body = re.search(r"</body\s*>", contenu, re.IGNORECASE)
        assert fermeture_body is not None
        scripts_parcours = '<script src="../assets/js/navigation-parcours.js" defer></script>\n'
        contenu = (
            contenu[:fermeture_body.start()]
            + SCRIPT_AFFICHAGE
            + "\n"
            + scripts_parcours
            + contenu[fermeture_body.start():]
        )

    origine = provenance()
    reference = origine.get("revision_courte", "révision inconnue")
    date = origine.get("date_revision", "")[:10]
    entete = (
        "<!DOCTYPE html>\n<!--\n"
        "  Page du simulateur macro-politique, générée pour le site M.R.S.C par\n"
        "  outils/construire-simulateur.py — ne pas modifier à la main.\n"
        f"  Moteur : {origine.get('depot_amont', 'dépôt du simulateur')}\n"
        f"  révision {reference}{f' ({date})' if date else ''}, "
        f"copiée le {origine.get('copie_le', 'date inconnue')}.\n"
        "  Source de la page : simulateur/interface.py, constante HTML_PAGE.\n"
        "  Navigation de retour vers le site : ajoutée par ce générateur.\n-->"
    )
    return contenu.replace("<!DOCTYPE html>", entete, 1)


def main() -> int:
    analyseur = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    analyseur.add_argument("--verifier", action="store_true", help="ne rien écrire, signaler une divergence")
    options = analyseur.parse_args()

    page = page_complete()
    if options.verifier:
        if not SORTIE.is_file():
            print(f"{SORTIE.relative_to(RACINE)} est absent : lancez le script sans --verifier.")
            return 1
        if SORTIE.read_text(encoding="utf-8") != page:
            print(f"{SORTIE.relative_to(RACINE)} a divergé du moteur : régénérez-le.")
            return 1
        print("La page du simulateur est à jour.")
        return 0

    SORTIE.parent.mkdir(parents=True, exist_ok=True)
    SORTIE.write_text(page, encoding="utf-8")
    print(f"{SORTIE.relative_to(RACINE)} écrit : {len(page):,} caractères".replace(",", " "))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
