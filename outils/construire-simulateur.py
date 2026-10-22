#!/usr/bin/env python3
"""Génère `simulateur/index.html`, la page du simulateur, à partir du moteur.

Le moteur sert sa page depuis la constante `HTML_PAGE` de
`simulateur/interface.py`, en remplaçant le repère `===SCENARIOS_JSON===` par
le catalogue des scénarios (`simulateur/dashboard.py`). Ce script fait
exactement la même substitution, mais une fois pour toutes : la page devient
un fichier statique publiable (Vercel, GitHub Pages), sans build à chaque
requête. Le générateur ajoute le retour permanent vers M.R.S.C, des réglages
d’affichage et des adaptations responsives et accessibles aux tableaux. La copie
locale reçoit aussi un correctif versionné pour la sécurité et les commandes de
scénario/préréglage au clavier ; le dépôt amont n’est pas modifié.

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
  /* Habillage M.R.S.C (phase 2, 18 octobre 2026) : valeurs identiques aux
     littéraux remplacés ; préfixe dédié, sans collision avec les jetons du
     moteur. Voir docs/rd/inventaire-couleurs-jetons.md. */
  --mrsc-marine: #1d3268;
  --mrsc-marine-2: #26375f;
  --mrsc-bordure: #526384;
  --mrsc-sur-marine: #fff;
}
header.entete {
  border-color: #344b79;
  background: linear-gradient(135deg, var(--mrsc-marine), var(--mrsc-marine-2));
}
header.entete .site-status-note {
  margin: 0 0 .8rem;
  padding: .5rem .8rem;
  border: 1px solid #c88712;
  border-radius: 9px;
  background: #fff3d2;
  color: #49320a;
  font-size: max(12px, .82rem);
  font-weight: 730;
  line-height: 1.4;
}
html.contraste-renforce header.entete .site-status-note {
  border-color: var(--ambre);
  background: var(--panel);
  color: var(--texte);
}
button.primaire {
  border-color: #456d29;
  background: linear-gradient(135deg, var(--mrsc-marine), #2958a2);
  color: var(--mrsc-sur-marine);
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
  min-height: 0;
  margin: 0;
  padding: 0;
  border: 0;
  background: transparent;
  box-shadow: none;
  backdrop-filter: none;
}
.site-return-bar .site-journey-inner {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: .25rem .7rem;
  width: 100%;
  min-height: 0;
}
.site-return-bar .site-journey-controls {
  display: flex;
  flex-wrap: nowrap;
  align-items: center;
  gap: .25rem;
  width: auto;
  margin: 0;
  padding: 0;
}
.site-return-bar .site-journey-button {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: .3rem;
  min-width: 38px;
  min-height: 38px;
  padding: clamp(6px,.35rem,8px) clamp(8px,.55rem,12px);
  border: 1px solid rgba(255,255,255,.38);
  border-radius: 9px;
  background: var(--mrsc-marine);
  color: var(--mrsc-sur-marine);
  font: inherit;
  font-size: clamp(12px,.76rem,18px);
  font-weight: 700;
  line-height: 1.25;
  cursor: pointer;
}
.site-return-bar .site-journey-button:hover:not(:disabled) {
  border-color: var(--ambre);
  background: var(--mrsc-marine-2);
}
.site-return-bar .site-journey-button[data-journey-action="accueil"] {
  border-color: var(--ambre);
  box-shadow: inset 0 -2px 0 var(--ambre);
}
.site-return-bar .site-journey-button:disabled {
  border-color: var(--mrsc-bordure);
  background: #17274d;
  color: #d2d9e5;
  cursor: not-allowed;
}
.site-return-bar .site-journey-button[data-journey-action="accueil"]:disabled { box-shadow: none; }
.site-return-bar .site-journey-symbol { font-size: max(12px, .95rem); }
.site-return-bar .site-journey-label { white-space: nowrap; }
.site-return-bar .site-journey-status {
  flex: 0 1 auto;
  margin: 0 0 0 auto;
  padding-left: .65rem;
  border-left: 1px solid var(--mrsc-bordure);
  color: var(--texte-dim);
  font-size: clamp(12px,.7rem,16px);
  line-height: 1.35;
  white-space: nowrap;
}
.site-return-bar .site-journey-settings { position: static; flex: 0 0 auto; color: var(--mrsc-sur-marine); }
.site-return-bar .site-journey-settings > summary {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: .3rem;
  min-width: 44px;
  min-height: 44px;
  padding: clamp(6px,.45rem,9px) clamp(8px,.8rem,16px);
  border: 1px solid rgba(255,255,255,.38);
  border-radius: 9px;
  background: var(--mrsc-marine);
  color: var(--mrsc-sur-marine);
  font-size: clamp(12px,.84rem,20px);
  font-weight: 700;
  list-style: none;
  cursor: pointer;
}
.site-return-bar .site-journey-settings > summary::-webkit-details-marker { display: none; }
.site-return-bar .site-journey-settings > summary::marker { content: ""; }
.site-return-bar .site-journey-settings > summary:hover,
.site-return-bar .site-journey-settings[open] > summary { border-color: var(--ambre); background: var(--mrsc-marine-2); }
.site-return-bar .site-journey-chevron { display: inline-block; font-size: clamp(12px,1rem,20px); line-height: 1; transition: transform .18s ease; }
.site-return-bar .site-journey-settings[open] .site-journey-chevron { transform: rotate(180deg); }
.site-return-bar .site-journey-panel {
  position: absolute;
  z-index: 120;
  top: calc(100% + .25rem);
  right: 0;
  width: min(38rem,calc(100vw - 2rem));
  max-height: calc(100vh - 5rem);
  overflow: auto;
  padding: .55rem;
  border: 1px solid var(--mrsc-bordure);
  border-radius: 12px;
  background: rgba(29,50,104,.98);
  box-shadow: 0 8px 22px rgba(0,0,0,.24);
}
.site-return-bar .site-layout-settings { position: static; flex: 0 0 auto; color: var(--mrsc-sur-marine); }
.site-return-bar .site-layout-settings > summary {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: .3rem;
  min-width: 44px;
  min-height: 44px;
  padding: clamp(6px,.45rem,9px) clamp(8px,.8rem,16px);
  border: 1px solid rgba(255,255,255,.38);
  border-radius: 9px;
  background: var(--mrsc-marine);
  color: var(--mrsc-sur-marine);
  font-size: clamp(12px,.84rem,20px);
  font-weight: 700;
  line-height: 1.25;
  list-style: none;
  cursor: pointer;
}
.site-return-bar .site-layout-settings > summary::-webkit-details-marker { display: none; }
.site-return-bar .site-layout-settings > summary::marker { content: ""; }
.site-return-bar .site-layout-settings > summary:hover,
.site-return-bar .site-layout-settings[open] > summary { border-color: var(--ambre); background: var(--mrsc-marine-2); }
.site-return-bar .site-layout-chevron { display: inline-block; margin-left: .25rem; font-size: 1rem; line-height: 1; transition: transform .18s ease; }
.site-return-bar .site-layout-settings[open] .site-layout-chevron { transform: rotate(180deg); }
.site-return-bar .site-layout-panel {
  position: absolute;
  z-index: 121;
  top: calc(100% + .25rem);
  right: 0;
  width: min(28rem,calc(100vw - 1rem));
  max-height: min(34rem,calc(100vh - 1.5rem));
  overflow: auto;
  padding: 12px;
  border: 1px solid var(--mrsc-bordure);
  border-radius: 12px;
  background: rgba(13,21,38,.99);
  color: var(--texte);
  box-shadow: 0 12px 32px rgba(0,0,0,.4);
}
.site-layout-title { margin-bottom: .55rem; color: var(--texte); font-weight: 750; }
.site-layout-options { display: grid; gap: .45rem; margin: 0; padding: 0; border: 0; }
.site-layout-options legend { margin-bottom: .45rem; color: var(--texte); font-size: max(12px, .86rem); font-weight: 700; }
.site-layout-choice {
  display: grid;
  grid-template-columns: 20px 54px minmax(0,1fr);
  align-items: start;
  gap: .6rem;
  min-height: 44px;
  padding: .6rem .7rem;
  border: 1px solid var(--mrsc-bordure);
  border-radius: 9px;
  background: #131c2f;
  color: var(--texte);
  cursor: pointer;
}
.site-layout-preview {
  display: grid;
  gap: 3px;
  width: 54px;
  height: 42px;
  margin-top: .1rem;
  padding: 5px;
  border: 1px solid var(--mrsc-bordure);
  border-radius: 7px;
  background: #0d1526;
}
.site-layout-preview > span { display: block; min-width: 0; min-height: 0; border-radius: 2px; background: #5b74a6; }
.site-layout-choice.is-selected .site-layout-preview { border-color: var(--accent); }
.site-layout-choice.is-selected .site-layout-preview > span { background: var(--accent); }
.site-layout-preview[data-preview="equilibree"] { grid-template-columns: 1.4fr 1fr; grid-template-rows: 1.3fr 1fr 1fr; }
.site-layout-preview[data-preview="equilibree"] > span:nth-child(1) { grid-row: span 3; }
.site-layout-preview[data-preview="equilibree"] > span:nth-child(n+5) { display: none; }
.site-layout-preview[data-preview="lecture"] { grid-template-columns: minmax(0,1fr); grid-template-rows: repeat(4,1fr); padding-inline: 14px; }
.site-layout-preview[data-preview="lecture"] > span:nth-child(n+5) { display: none; }
.site-layout-preview[data-preview="vitrine"] { grid-template-columns: minmax(0,1fr); grid-template-rows: 2.2fr .8fr .8fr; }
.site-layout-preview[data-preview="vitrine"] > span:nth-child(n+4) { display: none; }
.site-layout-preview[data-preview="mosaique"] { grid-template-columns: repeat(3,1fr); grid-template-rows: 1.4fr 1fr; }
.site-layout-preview[data-preview="mosaique"] > span:nth-child(1) { grid-column: span 2; }
.site-layout-preview[data-preview="panorama"] { grid-template-columns: repeat(3,1fr); grid-template-rows: repeat(2,1fr); }
.site-layout-preview[data-preview="compacte"] { grid-template-columns: repeat(3,1fr); grid-template-rows: repeat(2,1fr); gap: 2px; padding: 3px; }
.site-layout-hint { font-weight: 650; }
.site-layout-choice.is-selected { border-color: var(--accent); background: #1a2540; box-shadow: inset 0 0 0 1px var(--accent); }
.site-layout-choice:focus-within { outline: 3px solid var(--accent); outline-offset: 2px; }
.site-layout-choice input { width: 18px; height: 18px; margin: .16rem 0 0; accent-color: var(--accent); }
.site-layout-choice-copy { display: block; min-width: 0; }
.site-layout-choice-copy strong { display: block; color: var(--texte); font-size: max(12px, .87rem); }
.site-layout-choice-copy > span { display: block; margin-top: .1rem; color: var(--texte-dim); font-size: max(12px, .75rem); line-height: 1.4; }
.site-layout-status { min-height: 1.35em; margin: .6rem 0 0; color: var(--texte); font-size: max(12px, .8rem); font-weight: 700; }
.site-layout-note { margin: .35rem 0 0; color: var(--texte-dim); font-size: max(12px, .72rem); line-height: 1.45; }
.site-return-bar .site-layout-reset { width: 100%; min-height: 44px; margin-top: .65rem; }
.site-return-bar .site-layout-panel :focus-visible { outline-color: var(--accent); }
.site-return-bar .site-journey-settings:not([open]) > .site-journey-panel,
.site-return-bar .site-layout-settings:not([open]) > .site-layout-panel { display: none !important; }
.site-return-bar a {
  display: inline-flex;
  flex: 0 1 auto;
  align-items: center;
  gap: .55rem;
  min-height: 44px;
  max-width: 100%;
  padding: clamp(6px,.45rem,9px) clamp(8px,.8rem,16px);
  border: 1px solid rgba(255,255,255,.38);
  border-radius: 9px;
  background: var(--mrsc-marine);
  color: var(--mrsc-sur-marine);
  font-size: clamp(12px,.84rem,20px);
  font-weight: 700;
  line-height: 1.25;
  text-decoration: none;
  overflow-wrap: anywhere;
}
.site-return-bar a:hover {
  border-color: var(--ambre);
  background: var(--mrsc-marine-2);
  color: var(--mrsc-sur-marine);
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
  color: var(--mrsc-sur-marine);
  font-weight: 700;
}
.sim-skip-link:focus {
  transform: translateY(0);
}
.site-return-arrow {
  flex: 0 0 auto;
  color: var(--ambre);
  font-size: max(12px, 1.15rem);
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
  padding: clamp(6px,.4rem,8px) clamp(8px,.65rem,14px);
  border: 1px solid rgba(255,255,255,.38);
  border-radius: 9px;
  background: var(--mrsc-marine);
  color: var(--mrsc-sur-marine);
  font: inherit;
  font-size: clamp(12px,.78rem,18px);
  font-weight: 700;
  line-height: 1.25;
  cursor: pointer;
}
.sim-display-button:hover:not(:disabled) {
  border-color: var(--ambre);
  background: var(--mrsc-marine-2);
}
.sim-display-button:disabled {
  border-color: var(--mrsc-bordure);
  background: #17274d;
  color: #d2d9e5;
  cursor: not-allowed;
}
.sim-display-level {
  min-width: 3.8rem;
  color: var(--texte);
  font-size: clamp(12px,.8rem,18px);
  font-variant-numeric: tabular-nums;
  font-weight: 700;
  text-align: center;
}
.mrsc-scroll-hint {
  margin: 0 0 6px;
  color: var(--texte-dim);
  font-size: max(12px, .78rem);
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
html.texte-tres-reduit { font-size: 75%; }
html.texte-reduit { font-size: 85%; }
html.texte-agrandi { font-size: 115%; }
html.texte-tres-agrandi { font-size: 130%; }
html:is(.texte-tres-reduit,.texte-reduit) :is(button,input,select,textarea) { font-size: max(12px,1em); }
html:is(.texte-agrandi,.texte-tres-agrandi) :is(button,input,select,textarea) { font-size: clamp(12px,1em,20px); }
html:is(.texte-tres-reduit,.texte-reduit,.texte-agrandi,.texte-tres-agrandi) .sim-display-level { font-size: clamp(12px,.8rem,18px); }
html.espacement-renforce body { line-height: 1.8; }
html.espacement-renforce :is(h1, h2, h3, p, li, label, button, th, td, .aide, .nom, .desc, .libelle, .valeur, .ref, .pastille, .console-verdict, .console-titre, .source, .droite, .puce-effect) {
  line-height: 1.65;
  letter-spacing: .12em;
  word-spacing: .16em;
  overflow-wrap: anywhere;
}
html.espacement-renforce th,
html.espacement-renforce td { white-space: normal; }
html.espacement-renforce p { margin-block-end: 2em; }
html.espacement-renforce :is(.pastille, .ruban-titre, .ruban-pop, .console-verdict, .levier .valeur, .bulle-bouton, .source, .droite, .puce-effect) {
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
html.contraste-renforce .site-layout-choice { border-color: var(--border); }
html.contraste-renforce .site-layout-choice.is-selected { border-color: var(--accent); box-shadow: inset 0 0 0 1px var(--accent); }

/* Les mêmes choix de présentation restent disponibles dans l’interface sombre. */
html[data-layout="lecture"] #contenu-principal { max-width: 1160px; }
html[data-layout="lecture"] #contenu-principal :is(.grille.scenarios,.grille.domaines,.leviers-grille,.leviers-grille.compacte,.console-corps,.clair-lignes) {
  grid-template-columns: minmax(0,1fr);
}
html[data-layout="panorama"] #contenu-principal { max-width: 1800px; }
html[data-layout="panorama"] #contenu-principal .grille.metrics { grid-template-columns: repeat(auto-fit,minmax(210px,1fr)); }
html[data-layout="panorama"] #contenu-principal .grille.scenarios { grid-template-columns: repeat(auto-fit,minmax(260px,1fr)); }
html[data-layout="panorama"] #contenu-principal .grille.domaines { grid-template-columns: repeat(auto-fit,minmax(280px,1fr)); }
html[data-layout="panorama"] #contenu-principal .leviers-grille,
html[data-layout="panorama"] #contenu-principal .leviers-grille.compacte { grid-template-columns: repeat(auto-fit,minmax(260px,1fr)); }
html[data-layout="panorama"] #contenu-principal .console-corps,
html[data-layout="panorama"] #contenu-principal .clair-lignes { grid-template-columns: repeat(auto-fit,minmax(min(300px,100%),1fr)); }
/* Vitrine : de grandes tuiles et plus d’air, sans masquer ni réordonner. */
html[data-layout="vitrine"] #contenu-principal { max-width: 1320px; }
html[data-layout="vitrine"] #contenu-principal :is(.grille.metrics,.grille.scenarios,.grille.domaines,.leviers-grille,.leviers-grille.compacte) {
  grid-template-columns: repeat(auto-fit,minmax(min(340px,100%),1fr));
  gap: 18px;
}
html[data-layout="vitrine"] #contenu-principal .console-corps,
html[data-layout="vitrine"] #contenu-principal .clair-lignes { grid-template-columns: repeat(auto-fit,minmax(min(360px,100%),1fr)); gap: 18px; }
/* Mosaïque : portées double largeur à partir de deux colonnes, flux non dense. */
html[data-layout="mosaique"] #contenu-principal { max-width: 1600px; }
html[data-layout="mosaique"] #contenu-principal .grille.metrics { grid-template-columns: repeat(auto-fit,minmax(min(210px,100%),1fr)); }
@media (min-width: 641px) {
  html[data-layout="mosaique"] #contenu-principal :is(.grille.scenarios,.grille.domaines,.leviers-grille,.leviers-grille.compacte) {
    grid-template-columns: repeat(2,minmax(0,1fr));
  }
  html[data-layout="mosaique"] #contenu-principal :is(.grille.scenarios,.grille.domaines,.leviers-grille,.leviers-grille.compacte) > :nth-child(7n+1),
  html[data-layout="mosaique"] #contenu-principal :is(.grille.scenarios,.grille.domaines,.leviers-grille,.leviers-grille.compacte) > :nth-child(7n+4) { grid-column: span 2; }
}
@media (min-width: 1025px) {
  html[data-layout="mosaique"] #contenu-principal :is(.grille.scenarios,.grille.domaines,.leviers-grille,.leviers-grille.compacte) {
    grid-template-columns: repeat(4,minmax(0,1fr));
  }
}
/* En pistes étroites (Panorama, Compacte), la ligne d’un levier reprend le
   repli déjà prévu par le moteur sous 640 px : retour à la ligne et noms
   cassables, au lieu de pousser le bouton de détail hors de la carte. */
html:is([data-layout="panorama"],[data-layout="compacte"]) #contenu-principal .levier .bulle-bouton { white-space: normal; }
html:is([data-layout="panorama"],[data-layout="compacte"]) #contenu-principal .levier .ligne { flex-wrap: wrap; }
html:is([data-layout="panorama"],[data-layout="compacte"]) #contenu-principal .levier .ligne .nom { min-width: 0; overflow-wrap: anywhere; }
/* Les noms de fichiers sources sans espace doivent pouvoir se couper. */
html:is([data-layout="vitrine"],[data-layout="mosaique"],[data-layout="panorama"],[data-layout="compacte"]) #contenu-principal .levier .source { overflow-wrap: anywhere; }
/* Compacte : pistes et écarts resserrés ; texte et cibles inchangés. */
html[data-layout="compacte"] #contenu-principal { max-width: 1800px; }
html[data-layout="compacte"] #contenu-principal :is(.grille.metrics,.grille.scenarios,.grille.domaines,.leviers-grille,.leviers-grille.compacte) {
  grid-template-columns: repeat(auto-fit,minmax(min(200px,100%),1fr));
  gap: 8px;
}
html[data-layout="compacte"] #contenu-principal .console-corps,
html[data-layout="compacte"] #contenu-principal .clair-lignes { grid-template-columns: repeat(auto-fit,minmax(min(240px,100%),1fr)); gap: 8px; }

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
.graduations { font-size: max(12px, .75rem); }
/* Le ruban de veille reste visible sous la barre de retour quand elle tient sur une ligne. */
.conteneur .ruban-veille { top: 54px; }
@media (max-width: 640px) {
  .site-return-bar {
    justify-content: flex-start;
    margin: -10px -10px 10px;
    padding-inline: 10px;
  }
  .site-return-bar .site-journey-panel {
    position: fixed;
    top: .5rem;
    right: .5rem;
    width: calc(100vw - 1rem);
    max-height: calc(100vh - 1rem);
    padding: .45rem;
  }
  .site-return-bar .site-journey-settings > summary,
  .site-return-bar .site-layout-settings > summary { padding-inline: .55rem; font-size: clamp(12px,.78rem,18px); }
  /* La barre sticky utilise backdrop-filter, qui forme un bloc contenant pour
     les descendants fixes : fixer explicitement le panneau au coin du viewport
     évite qu’il reste sous la très haute barre quand le texte est agrandi. */
  .site-return-bar .site-layout-panel {
    position: fixed;
    top: .5rem;
    right: .5rem;
    width: calc(100vw - 1rem);
    max-height: calc(100vh - 1rem);
    padding: .55rem;
  }
  .puce-effect,
  .message-seuil .source,
  .ligne-marge .droite { white-space: normal; overflow-wrap: anywhere; }
  .site-return-bar .site-journey-inner { flex-wrap: wrap; gap: .1rem .2rem; }
  .site-return-bar .site-journey-controls { flex-wrap: wrap; gap: .15rem; }
  .site-return-bar .site-journey-button {
    min-width: 44px;
    min-height: 44px;
    padding: clamp(6px,.25rem,8px) clamp(6px,.38rem,10px);
    font-size: clamp(12px,.75rem,18px);
  }
  .site-return-bar .site-journey-symbol { display: none; }
  .site-return-bar .site-journey-status {
    max-width: 6rem;
    padding-left: .4rem;
    font-size: clamp(12px,.66rem,14px);
    text-align: right;
    white-space: normal;
    overflow-wrap: anywhere;
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
  .site-return-bar .site-layout-settings > summary,
  .site-return-bar .site-layout-choice,
  .site-return-bar .site-layout-reset,
  .levier .bulle-bouton,
  .levier input[type=range] { min-height: 44px; }
  .site-return-bar .site-journey-button { min-width: 44px; }
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
  .site-return-bar { background: var(--mrsc-marine); backdrop-filter: none; }
  .site-return-bar .site-layout-panel { background: #0d1526; backdrop-filter: none; }
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
  .ruban-veille, .site-return-bar, .site-journey-panel, .site-layout-panel, .site-layout-choice, .infobulle {
    background: Canvas !important;
    color: CanvasText !important;
    border-color: CanvasText !important;
    box-shadow: none !important;
    backdrop-filter: none !important;
  }
  header.entete .site-status-note {
    border-color: CanvasText !important;
    background: Canvas !important;
    color: CanvasText !important;
  }
  a { color: LinkText !important; }
  button, .site-return-bar a, .site-return-bar .site-journey-settings > summary,
  .site-return-bar .site-layout-settings > summary, .site-return-bar .site-layout-reset,
  .site-return-bar .site-journey-button, .sim-display-button {
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
    '<nav id="mrsc-retour-site" class="site-return-bar" aria-label="Navigation de retour, vie privée et réglages d’affichage et de présentation">\n'
    '  <a href="../index.html" data-site-home><span class="site-return-arrow" aria-hidden="true">←</span>Retour au site M.R.S.C</a>\n'
    '  <a href="../confidentialite.html">Vie privée et données</a>\n'
    '  <div id="mrsc-display-controls" class="sim-display-controls" role="group" aria-label="Réglages d’affichage du simulateur" hidden>\n'
    '    <button class="sim-display-button" type="button" data-sim-text-decrease aria-label="A− — réduire la taille du texte">A−</button>\n'
    '    <span class="sim-display-level" data-sim-text-level role="status" aria-live="polite" aria-atomic="true">100 %</span>\n'
    '    <button class="sim-display-button" type="button" data-sim-text-increase aria-label="A+ — agrandir la taille du texte">A+</button>\n'
    '    <button class="sim-display-button" type="button" data-sim-contrast aria-pressed="false">Contraste +</button>\n'
    '    <button class="sim-display-button" type="button" data-sim-spacing aria-pressed="false">Interligne +</button>\n'
    '  </div>\n'
    '  <details class="site-layout-settings" data-site-layout-settings hidden>\n'
    '    <summary aria-controls="site-layout-settings-panel" title="Ouvrir ou fermer les choix de présentation">Présentation <span class="site-layout-chevron" aria-hidden="true">⌄</span></summary>\n'
    '    <div class="site-layout-panel" id="site-layout-settings-panel" aria-label="Personnaliser l’expérience de lecture">\n'
    '      <p class="site-layout-title"><strong>Personnaliser l’expérience</strong></p>\n'
    '      <fieldset class="site-layout-options"><legend>Choisissez une mise en page</legend>\n'
    '        <label class="site-layout-choice"><input type="radio" name="mrsc-site-layout" value="equilibree" data-site-layout-option><span class="site-layout-preview" data-preview="equilibree" aria-hidden="true"><span></span><span></span><span></span><span></span><span></span><span></span></span><span class="site-layout-choice-copy"><strong>Équilibrée</strong><span>La présentation de base, entre lecture et blocs visuels.</span><span class="site-layout-hint">Le réglage par défaut du site.</span></span></label>\n'
    '        <label class="site-layout-choice"><input type="radio" name="mrsc-site-layout" value="lecture" data-site-layout-option><span class="site-layout-preview" data-preview="lecture" aria-hidden="true"><span></span><span></span><span></span><span></span><span></span><span></span></span><span class="site-layout-choice-copy"><strong>Lecture</strong><span>Une colonne plus étroite et des blocs empilés pour suivre les textes.</span><span class="site-layout-hint">Idéal pour : les fiches et les textes suivis.</span></span></label>\n'
    '        <label class="site-layout-choice"><input type="radio" name="mrsc-site-layout" value="vitrine" data-site-layout-option><span class="site-layout-preview" data-preview="vitrine" aria-hidden="true"><span></span><span></span><span></span><span></span><span></span><span></span></span><span class="site-layout-choice-copy"><strong>Vitrine</strong><span>De grands titres, beaucoup d’air et une idée à la fois, comme une page de présentation.</span><span class="site-layout-hint">Idéal pour : découvrir l’accueil, le dossier IA ou ÉVA.</span></span></label>\n'
    '        <label class="site-layout-choice"><input type="radio" name="mrsc-site-layout" value="mosaique" data-site-layout-option><span class="site-layout-preview" data-preview="mosaique" aria-hidden="true"><span></span><span></span><span></span><span></span><span></span><span></span></span><span class="site-layout-choice-copy"><strong>Mosaïque</strong><span>Des tuiles de tailles variées ; certaines cartes de chaque collection sont mises en avant, dans le même ordre.</span><span class="site-layout-hint">Idéal pour : explorer les fiches, les Mondes, les liens et les documents.</span></span></label>\n'
    '        <label class="site-layout-choice"><input type="radio" name="mrsc-site-layout" value="panorama" data-site-layout-option><span class="site-layout-preview" data-preview="panorama" aria-hidden="true"><span></span><span></span><span></span><span></span><span></span><span></span></span><span class="site-layout-choice-copy"><strong>Panorama composite</strong><span>Une page plus large, avec un agencement de cartes en plusieurs colonnes.</span><span class="site-layout-hint">Idéal pour : les grands écrans.</span></span></label>\n'
    '        <label class="site-layout-choice"><input type="radio" name="mrsc-site-layout" value="compacte" data-site-layout-option><span class="site-layout-preview" data-preview="compacte" aria-hidden="true"><span></span><span></span><span></span><span></span><span></span><span></span></span><span class="site-layout-choice-copy"><strong>Compacte</strong><span>Des blocs resserrés pour voir davantage de cartes sans faire défiler longtemps.</span><span class="site-layout-hint">Idéal pour : comparer et balayer un catalogue ou un registre.</span></span></label>\n'
    '      </fieldset>\n'
    '      <p class="site-layout-status" data-site-layout-status role="status" aria-live="polite" aria-atomic="true"></p>\n'
    '      <p class="site-layout-note">Le changement est immédiat, sans rechargement. Si le stockage local est autorisé, votre choix est mémorisé sur cet appareil.</p>\n'
    '      <button class="sim-display-button site-layout-reset" type="button" data-site-layout-reset>Réinitialiser la présentation</button>\n'
    '    </div>\n'
    '  </details>\n'
    '</nav>\n'
)
SCRIPT_AFFICHAGE = r"""
<script>
(() => {
  const root = document.documentElement;
  const parentHasSiteHeader = (() => {
    if (window.parent === window) return false;
    try {
      return Boolean(window.parent.document.querySelector(".site-header .nav-inner [data-menu-toggle]"));
    } catch (error) {
      return false;
    }
  })();
  const controls = document.getElementById("mrsc-display-controls");
  const decrease = document.querySelector("[data-sim-text-decrease]");
  const increase = document.querySelector("[data-sim-text-increase]");
  const levelOutput = document.querySelector("[data-sim-text-level]");
  const contrastButton = document.querySelector("[data-sim-contrast]");
  const spacingButton = document.querySelector("[data-sim-spacing]");
  const layoutSettings = document.querySelector("[data-site-layout-settings]");
  const layoutRadios = Array.from(document.querySelectorAll("[data-site-layout-option]"));
  const layoutStatus = document.querySelector("[data-site-layout-status]");
  const layoutReset = document.querySelector("[data-site-layout-reset]");
  const keys = {
    text: "mrsc-texte-cran",
    contrast: "mrsc-contraste-renforce",
    spacing: "mrsc-espacement-renforce",
    layout: "mrsc-mise-en-page",
  };
  // Même échelle que le site : 50 % donnait 8 px de corps, illisible.
  // L'ancienne clé est migrée à la première visite, puis la nouvelle est écrite.
  const textLevels = [75, 85, 100, 115, 130];
  const anciensCrans = { 50: 75, 75: 85, 100: 100, 125: 115, 150: 130 };
  const anciensIndexes = [100, 115, 130];
  const ANCIENNE_CLE = "mrsc-texte-niveau";
  const layoutLabels = new Map([
    ["equilibree", "Équilibrée"],
    ["lecture", "Lecture"],
    ["vitrine", "Vitrine"],
    ["mosaique", "Mosaïque"],
    ["panorama", "Panorama composite"],
    ["compacte", "Compacte"],
  ]);
  let level = 100;
  let contrast = false;
  let spacing = false;
  let layout = "equilibree";

  const read = (key) => {
    try { return window.localStorage.getItem(key); }
    catch (error) { return null; }
  };
  const save = (key, value) => {
    try { window.localStorage.setItem(key, value); }
    catch (error) { /* Le choix reste actif pour la visite courante. */ }
  };
  const niveauTexteEnregistre = (value) => {
    if (value === null) return null;
    const stored = String(value).trim();
    const parsed = Number(stored);
    if (Number.isInteger(parsed) && textLevels.includes(parsed)) return parsed;
    return null;
  };
  const niveauTexteMigre = () => {
    const ancien = read(ANCIENNE_CLE);
    if (ancien !== null) {
      const stored = String(ancien).trim();
      if (/^[0-2]$/.test(stored)) return anciensIndexes[Number(stored)];
      return anciensCrans[Number(stored)] ?? 100;
    }
    return read("mrsc-texte-agrandi") === "oui" ? 115 : 100;
  };
  const applyLevel = (value) => {
    level = textLevels.includes(value) ? value : 100;
    root.classList.toggle("texte-tres-reduit", level === 75);
    root.classList.toggle("texte-reduit", level === 85);
    root.classList.toggle("texte-agrandi", level === 115);
    root.classList.toggle("texte-tres-agrandi", level === 130);
    if (levelOutput) levelOutput.textContent = `${level} %`;
    if (decrease) decrease.disabled = level === textLevels[0];
    if (increase) increase.disabled = level === textLevels[textLevels.length - 1];
  };
  const applyContrast = (value) => {
    contrast = Boolean(value);
    root.classList.toggle("contraste-renforce", contrast);
    if (contrastButton) {
      contrastButton.setAttribute("aria-pressed", String(contrast));
    }
  };
  const applySpacing = (value) => {
    spacing = Boolean(value);
    root.classList.toggle("espacement-renforce", spacing);
    if (spacingButton) {
      spacingButton.setAttribute("aria-pressed", String(spacing));
    }
  };
  const applyLayout = (value) => {
    layout = layoutLabels.has(value) ? value : "equilibree";
    root.dataset.layout = layout;
    layoutRadios.forEach((radio) => {
      radio.checked = radio.value === layout;
      radio.closest("label")?.classList.toggle("is-selected", radio.checked);
    });
    if (layoutStatus) layoutStatus.textContent = `Présentation « ${layoutLabels.get(layout)} » appliquée.`;
  };
  const load = () => {
    const savedLevel = read(keys.text);
    const parsed = savedLevel === null ? niveauTexteMigre() : niveauTexteEnregistre(savedLevel);
    const niveau = parsed ?? 100;
    applyLevel(niveau);
    if (savedLevel === null) save(keys.text, String(niveau));
    applyContrast(read(keys.contrast) === "oui");
    applySpacing(read(keys.spacing) === "oui");
    applyLayout(read(keys.layout));
  };

  load();
  if (controls) controls.hidden = parentHasSiteHeader;
  if (layoutSettings) layoutSettings.hidden = parentHasSiteHeader;
  decrease?.addEventListener("click", () => {
    const index = textLevels.indexOf(level);
    applyLevel(textLevels[Math.max(0, index - 1)]);
    save(keys.text, String(level));
  });
  increase?.addEventListener("click", () => {
    const index = textLevels.indexOf(level);
    applyLevel(textLevels[Math.min(textLevels.length - 1, index + 1)]);
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
  layoutRadios.forEach((radio) => {
    radio.addEventListener("change", () => {
      if (!radio.checked) return;
      applyLayout(radio.value);
      save(keys.layout, layout);
    });
  });
  layoutReset?.addEventListener("click", () => {
    applyLayout("equilibree");
    save(keys.layout, layout);
  });
  layoutSettings?.addEventListener("toggle", () => {
    if (layoutSettings.open) {
      const journeySettings = document.querySelector("[data-site-journey]");
      if (journeySettings) journeySettings.open = false;
    }
  });
  document.addEventListener("click", (event) => {
    if (layoutSettings && !layoutSettings.contains(event.target)) layoutSettings.open = false;
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

    ouverture_entete = re.search(
        r'<header\b(?=[^>]*class="entete")[^>]*>', contenu, re.IGNORECASE
    )
    if not ouverture_entete:
        raise SystemExit("Impossible d’ajouter l’avis de développement à l’entête du simulateur.")
    if 'class="site-status-note"' not in contenu:
        note_developpement = (
            '\n    <p class="site-status-note" role="note">'
            "Version R&amp;D — le site est en cours de développement."
            "</p>"
        )
        contenu = (
            contenu[:ouverture_entete.end()]
            + note_developpement
            + contenu[ouverture_entete.end():]
        )

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
