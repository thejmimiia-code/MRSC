"""
simulateur/interface.py — Interface web du simulateur interactif.

Le module expose `HTML_PAGE` : une page unique (aucune dépendance externe,
aucun CDN) qui contient :

  * la barre de contexte « instant T » (données réelles, provenance, licences) ;
  * la **console de veille permanente** (`console-pilotage`) : verdict par strate,
    messages de seuil (tolérable → vigilance → risqué → hors-sol), risque pour la
    population, marges de manœuvre restantes et effet de la dernière modification ;
  * la cascade des 5 échelons systémiques, recalculée à chaque simulation ;
  * la grille des scénarios types (9 situations historiques du dépôt) ;
  * les préréglages doctrinaux additionnels ;
  * 93 leviers de politique publique réglables (curseurs, interrupteurs), chacun
    annoté d'une **aide au survol** (plage, défaut, valeur courante, effets
    déclarés, mesures en direct) et d'une **bulle explicative** dépliable ;
  * des infobulles instantanées sur les boutons, cases à cocher, cartes de
    domaine, préréglages et scénarios (couche passive : aucun clic capté) ;
  * les 20 domaines d'action publique avec leurs indicateurs et mini-graphes ;
  * la matrice croisée levier × domaine (impacts calculés par le modèle) ;
  * le journal causal du moteur et les exports JSON/CSV ;
  * un bouton « Rafraîchir les données » qui interroge les API publiques
    directement depuis le navigateur (Eurostat, BCE, Frankfurter, World Bank…)
    puis renvoie les valeurs au serveur via `POST /api/donnees`.

Le JavaScript est volontairement sans framework : la page doit rester lisible
et auditables par des non-informaticiens, conformément à l'esprit du projet.
"""

from __future__ import annotations

#: ⚠️ Le placeholder `===SCENARIOS_JSON===` est remplacé à la volée par le
#: catalogue des scénarios historiques (nom, description, couleur) — il doit
#: rester littéral dans ce fichier.
HTML_PAGE = r"""<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Simulateur Macro-Politique — Démocratie et politique du peuple</title>
<style>
:root{
  --bg:#0b1220; --panel:#131c2f; --panel-2:#1a2540; --border:#26324d;
  --texte:#e6edf7; --texte-dim:#93a3bd; --accent:#38bdf8; --vert:#22c55e;
  --rouge:#ef4444; --ambre:#f59e0b; --violet:#a855f7; --rose:#ec4899;
}
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:'Segoe UI',Roboto,system-ui,sans-serif;background:
  radial-gradient(1200px 600px at 50% -10%,#16233d 0%,var(--bg) 60%);
  color:var(--texte);min-height:100vh;padding:18px;line-height:1.45}
.conteneur{max-width:1560px;margin:0 auto}
a{color:var(--accent)}
header.entete{background:linear-gradient(135deg,#12305c,#2b1e56);border:1px solid var(--border);
  border-radius:14px;padding:18px 22px;margin-bottom:14px;box-shadow:0 10px 30px rgba(0,0,0,.35)}
header.entete h1{font-size:1.45rem;letter-spacing:.2px}
header.entete p{color:var(--texte-dim);font-size:.88rem;margin-top:4px}
.barre-contexte{display:flex;flex-wrap:wrap;gap:10px;align-items:center;margin-top:12px}
.pastille{border-radius:999px;padding:4px 12px;font-size:.75rem;border:1px solid var(--border);
  background:var(--panel);color:var(--texte-dim);white-space:nowrap}
.pastille.live{border-color:var(--vert);color:#bbf7d0;background:rgba(34,197,94,.12)}
.pastille.reference{border-color:var(--ambre);color:#fde68a;background:rgba(245,158,11,.12)}
.pastille.mixte{border-color:var(--accent);color:#bae6fd;background:rgba(56,189,248,.12)}
button{font-family:inherit;font-size:.82rem;cursor:pointer;border-radius:9px;border:1px solid var(--border);
  background:var(--panel-2);color:var(--texte);padding:8px 13px;transition:.15s}
button:hover:not(:disabled){border-color:var(--accent);transform:translateY(-1px)}
button:disabled{opacity:.45;cursor:not-allowed}
button.primaire{background:linear-gradient(135deg,#0284c7,#2563eb);border-color:#1d4ed8}
button.discret{background:transparent}
section.bloc{background:var(--panel);border:1px solid var(--border);border-radius:14px;
  padding:16px;margin-bottom:14px}
section.bloc > h2{font-size:1rem;margin-bottom:4px;display:flex;align-items:center;gap:8px}
section.bloc > h2 .aide{font-size:.75rem;color:var(--texte-dim);font-weight:400}
.grille{display:grid;gap:12px}
.grille.metrics{grid-template-columns:repeat(auto-fit,minmax(158px,1fr))}
.grille.scenarios{grid-template-columns:repeat(auto-fit,minmax(232px,1fr))}
.grille.domaines{grid-template-columns:repeat(auto-fit,minmax(330px,1fr))}
.carte{background:var(--panel-2);border:1px solid var(--border);border-radius:11px;padding:12px}
.metric .valeur{font-size:1.32rem;font-weight:600}
.metric .libelle{font-size:.74rem;color:var(--texte-dim);text-transform:uppercase;letter-spacing:.4px}
.metric .delta{font-size:.75rem;margin-top:2px}
.delta.hausse{color:var(--vert)} .delta.baisse{color:var(--rouge)} .delta.neutre{color:var(--texte-dim)}
.scenario-card{cursor:pointer;border-left:4px solid var(--accent);transition:.15s}
.scenario-card:hover{background:#22304f;transform:translateY(-2px)}
.scenario-card.actif{box-shadow:0 0 0 2px var(--accent) inset;background:#22304f}
.scenario-card h3{font-size:.9rem;margin-bottom:3px}
.scenario-card p{font-size:.76rem;color:var(--texte-dim)}
.strates-cascade{display:flex;flex-direction:column;gap:6px}
.strate{display:flex;justify-content:space-between;gap:14px;align-items:center;
  background:var(--panel-2);border:1px solid var(--border);border-left-width:4px;border-radius:10px;
  padding:9px 13px;font-size:.83rem}
.strate .titre{font-weight:600}
.strate .valeurs{display:flex;gap:14px;flex-wrap:wrap;color:var(--texte-dim);font-size:.79rem}
.strate .valeurs b{color:var(--texte)}
.leviers-grille{display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:12px}
.famille{background:var(--panel-2);border:1px solid var(--border);border-radius:11px;padding:12px}
.famille h3{font-size:.84rem;margin-bottom:8px;border-bottom:1px solid var(--border);padding-bottom:6px}
.levier{margin-bottom:11px}
.levier .ligne{display:flex;justify-content:space-between;gap:8px;font-size:.79rem;align-items:baseline}
.levier .nom{font-weight:500}
.levier .valeur{color:var(--accent);font-variant-numeric:tabular-nums;white-space:nowrap}
.levier .desc{font-size:.7rem;color:var(--texte-dim);margin-top:2px}
.levier input[type=range]{width:100%;margin-top:5px;accent-color:var(--accent)}
.levier .source{font-size:.66rem;color:#7b8aa5;font-style:italic;margin-top:3px}
.levier .ligne .bascule{margin-bottom:0}
/* Infobulle instantanée : tout réglage ou bouton annoté s'explique au survol
   (et au focus clavier), sans jamais recouvrir les leviers durablement. */
.infobulle{position:fixed;z-index:120;max-width:352px;background:#0d1526;border:1px solid var(--accent);
  border-radius:11px;padding:9px 11px;font-size:.74rem;line-height:1.5;color:var(--texte);
  box-shadow:0 16px 38px rgba(2,6,23,.6);pointer-events:none;opacity:0;transition:opacity .08s}
.infobulle.visible{opacity:1}
.infobulle b{color:var(--accent)}
.infobulle .aide-titre{display:block;margin-bottom:3px;font-weight:600;color:var(--texte)}
[data-aide],[data-aide-levier]{cursor:help}
.levier .bulle-bouton{margin-left:auto;background:transparent;border:1px solid var(--border);border-radius:999px;
  color:var(--texte-dim);font-size:.64rem;padding:1px 8px;line-height:1.5;white-space:nowrap}
.levier .bulle-bouton:hover{border-color:var(--accent);color:var(--accent);transform:none}
.levier .bulle-bouton.actif{border-color:var(--accent);color:var(--accent);background:rgba(56,189,248,.12)}
.bulle-levier{grid-column:1/-1;margin-top:9px;border-top:1px dashed var(--border);padding-top:9px;
  font-size:.72rem;line-height:1.5;color:var(--texte-dim)}
.bulle-levier b{color:var(--texte)}
.bulle-levier .bulle-titre{font-size:.67rem;text-transform:uppercase;letter-spacing:.5px;color:var(--texte-dim)}
.bulle-levier .bulle-section{margin-top:8px}
.bulle-levier ul{margin:4px 0 0 14px;padding:0}
.bulle-levier li{margin-bottom:2px}
.bulle-levier .bulle-med{color:var(--texte);font-variant-numeric:tabular-nums}
.bulle-levier .bulle-mesure{border-left:3px solid var(--border);padding-left:8px;margin:7px 0}
.bulle-levier .bulle-mesure.bulle-aggrave{border-left-color:var(--rouge)}
.bulle-levier .bulle-mesure.bulle-favorable{border-left-color:var(--vert)}
.bulle-levier .bulle-domaine{display:inline-block;margin:1px 4px 1px 0;padding:1px 7px;border-radius:999px;
  border:1px solid var(--border);font-variant-numeric:tabular-nums}
.bulle-levier .bulle-domaine.pos{border-color:rgba(34,197,94,.6);color:#86efac}
.bulle-levier .bulle-domaine.neg{border-color:rgba(239,68,68,.6);color:#fca5a5}
.bulle-levier .bulle-alerte{color:#fca5a5}
.bulle-levier .bulle-alerte.vigilance{color:#fcd34d}
.bulle-levier .bulle-journal li{font-style:italic}
.bulle-levier .bulle-note{margin-top:8px;font-style:italic;color:#7b8aa5}
.bulle-levier .bulle-chargement{font-style:italic}
.bascule{display:flex;align-items:center;gap:8px;font-size:.79rem;margin-bottom:9px}
.bascule input{width:18px;height:18px;accent-color:var(--vert)}
.recherche{width:100%;padding:9px 12px;border-radius:9px;border:1px solid var(--border);
  background:var(--panel-2);color:var(--texte);margin-bottom:10px}
.domaine{background:var(--panel-2);border:1px solid var(--border);border-radius:11px;padding:12px}
.domaine .tete{display:flex;justify-content:space-between;align-items:center;gap:10px}
.domaine .score{font-size:1.25rem;font-weight:700;font-variant-numeric:tabular-nums}
.domaine .ref{font-size:.7rem;color:var(--texte-dim)}
.domaine ul{list-style:none;margin-top:9px;font-size:.78rem}
.domaine li{display:flex;justify-content:space-between;gap:10px;padding:3px 0;
  border-bottom:1px dashed rgba(147,163,189,.18)}
.domaine li:last-child{border-bottom:none}
.domaine .indic{color:var(--texte-dim)}
table{width:100%;border-collapse:collapse;font-size:.78rem}
th,td{padding:6px 8px;text-align:right;border-bottom:1px solid var(--border);white-space:nowrap}
th:first-child,td:first-child{text-align:left}
thead th{color:var(--texte-dim);font-weight:600;position:sticky;top:0;background:var(--panel)}
.defilable{overflow:auto;max-height:430px;border-radius:9px;border:1px solid var(--border)}
.matrice td,.matrice th{text-align:center}
.matrice td.pos{background:rgba(34,197,94,.18);color:#bbf7d0}
.matrice td.neg{background:rgba(239,68,68,.16);color:#fecaca}
.matrice td.vide{color:#42506b}
.journal{max-height:260px;overflow:auto;font-size:.78rem;color:var(--texte-dim)}
.journal div{padding:3px 0;border-bottom:1px dashed rgba(147,163,189,.15)}
.alerte{background:rgba(245,158,11,.1);border:1px solid var(--ambre);color:#fde68a;
  border-radius:10px;padding:9px 12px;font-size:.78rem;margin-bottom:10px}
.svg-chart{width:100%;height:210px;background:var(--panel-2);border-radius:10px;border:1px solid var(--border)}
.pied{color:var(--texte-dim);font-size:.72rem;text-align:center;padding:14px 0 26px}
.provenance{font-size:.73rem;color:var(--texte-dim);max-height:210px;overflow:auto}
.provenance div{padding:3px 0;border-bottom:1px dashed rgba(147,163,189,.15)}
.onglets{display:flex;gap:8px;flex-wrap:wrap;margin-bottom:12px}
.onglets button.actif{background:linear-gradient(135deg,#0284c7,#2563eb);border-color:#1d4ed8}
/* ── Console de veille permanente ─────────────────────────────────────── */
.console{border-width:2px}
/* Ruban de veille : une seule ligne collante, jamais devant les leviers. */
.ruban-veille{position:sticky;top:0;z-index:60;display:flex;align-items:center;gap:10px;
  flex-wrap:wrap;background:linear-gradient(135deg,#0e1a30,#141b33);border:1px solid var(--border);
  border-radius:12px;padding:7px 12px;margin-bottom:12px;box-shadow:0 8px 22px rgba(0,0,0,.45)}
.ruban-veille .ruban-titre{font-size:.68rem;text-transform:uppercase;letter-spacing:.6px;
  color:var(--texte-dim);white-space:nowrap}
.ruban-veille .console-verdict{font-size:.78rem;padding:4px 12px;max-width:520px;
  overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.ruban-veille.niveau-vigilance{border-color:rgba(245,158,11,.65)}
.ruban-veille.niveau-risque{border-color:rgba(239,68,68,.7)}
.ruban-veille.niveau-hors_sol{border-color:var(--rouge);
  box-shadow:0 0 0 3px rgba(239,68,68,.25),0 8px 22px rgba(0,0,0,.5)}
.ruban-strates{display:flex;gap:5px;align-items:center}
.ruban-strate{width:26px;height:22px;border-radius:6px;border:1px solid var(--border);
  font-size:.62rem;display:flex;align-items:center;justify-content:center;cursor:help;
  background:var(--panel-2);color:var(--texte-dim);font-weight:700}
.ruban-strate.niveau-favorable,.ruban-strate.niveau-tolerable{background:rgba(34,197,94,.22);color:#bbf7d0;border-color:rgba(34,197,94,.5)}
.ruban-strate.niveau-vigilance{background:rgba(245,158,11,.22);color:#fde68a;border-color:rgba(245,158,11,.55)}
.ruban-strate.niveau-risque{background:rgba(239,68,68,.24);color:#fecaca;border-color:rgba(239,68,68,.6)}
.ruban-strate.niveau-hors_sol{background:var(--rouge);color:#fff;border-color:#fff}
.ruban-pop{font-size:.72rem;color:var(--texte-dim);white-space:nowrap}
.ruban-pop b{font-variant-numeric:tabular-nums}
.ruban-veille .ruban-actions{margin-left:auto;display:flex;gap:6px;flex-wrap:wrap}
.ruban-veille button{padding:5px 10px;font-size:.74rem}
/* Barre d'outils des leviers et vues */
.barre-leviers{display:flex;gap:10px;align-items:center;flex-wrap:wrap;margin-bottom:10px}
.barre-leviers .recherche{flex:1;min-width:240px;margin-bottom:0}
.barre-leviers label{display:flex;align-items:center;gap:6px;font-size:.76rem;color:var(--texte-dim)}
.leviers-grille.compacte{grid-template-columns:repeat(auto-fit,minmax(330px,1fr));gap:10px}
.famille.compacte{padding:9px 10px}
.famille.compacte h3{font-size:.76rem;margin-bottom:6px;padding-bottom:4px}
.levier.compact{margin-bottom:6px;display:grid;grid-template-columns:1fr 96px 74px auto;
  gap:6px;align-items:center;padding-bottom:5px;border-bottom:1px dashed rgba(147,163,189,.14)}
.levier.compact .nom{font-size:.73rem}
.levier.compact input[type=range]{margin-top:0}
.levier.compact .valeur{font-size:.72rem;text-align:right}
.levier.compact .desc,.levier.compact .source{display:none}
.levier.modifie{border-left:3px solid var(--accent);padding-left:8px;background:rgba(56,189,248,.06);
  border-radius:0 8px 8px 0}
.levier.modifie .nom{font-weight:700}
.puces{display:flex;gap:4px;flex-wrap:wrap;margin-top:4px}
.puce-effect{font-size:.66rem;border-radius:6px;padding:1px 6px;border:1px solid var(--border);
  white-space:nowrap}
.puce-effect.pos{background:rgba(34,197,94,.16);color:#bbf7d0;border-color:rgba(34,197,94,.45)}
.puce-effect.neg{background:rgba(239,68,68,.16);color:#fecaca;border-color:rgba(239,68,68,.45)}
.console-corps.replie{display:none}
.console.niveau-favorable,.console.niveau-tolerable{border-color:rgba(34,197,94,.55)}
.console.niveau-vigilance{border-color:rgba(245,158,11,.65)}
.console.niveau-risque{border-color:rgba(239,68,68,.7)}
.console.niveau-hors_sol{border-color:var(--rouge);
  box-shadow:0 0 0 3px rgba(239,68,68,.28),0 12px 34px rgba(0,0,0,.5)}
.console-entete{display:flex;justify-content:space-between;gap:12px;align-items:center;flex-wrap:wrap}
.console-verdict{font-weight:700;font-size:.85rem;padding:7px 14px;border-radius:999px;
  border:1px solid var(--border);max-width:720px}
.console-strates{display:grid;grid-template-columns:repeat(auto-fit,minmax(148px,1fr));gap:8px;margin:12px 0}
.strate-puce{border:1px solid var(--border);border-left-width:5px;border-radius:9px;padding:7px 10px;
  background:var(--panel-2);font-size:.74rem}
.strate-puce b{display:block;font-size:.78rem;margin-bottom:2px}
.console-corps{display:grid;grid-template-columns:repeat(auto-fit,minmax(330px,1fr));gap:14px}
.console-titre{font-size:.78rem;text-transform:uppercase;letter-spacing:.5px;color:var(--texte-dim);
  margin:8px 0 6px}
.niveau-favorable{color:#bbf7d0}.niveau-tolerable{color:#bbf7d0}.niveau-vigilance{color:#fde68a}
.niveau-risque{color:#fecaca}.niveau-hors_sol{color:#fff;background:rgba(239,68,68,.22)}
.strate-puce.niveau-hors_sol{border-color:var(--rouge)}
.message-seuil{border-left:3px solid var(--border);padding:6px 10px;margin-bottom:7px;
  font-size:.76rem;background:var(--panel-2);border-radius:0 8px 8px 0}
.message-seuil .tete{display:flex;justify-content:space-between;gap:8px;align-items:baseline}
.message-seuil .etiquette{font-size:.68rem;text-transform:uppercase;letter-spacing:.4px;font-weight:700}
.message-seuil p{color:var(--texte-dim);margin-top:3px}
.message-seuil .source{font-size:.66rem;color:#7b8aa5;font-style:italic;margin-top:3px;display:block}
.jauge{height:11px;border-radius:7px;background:#22304f;overflow:hidden;border:1px solid var(--border)}
.jauge > span{display:block;height:100%;transition:width .25s}
.graduations{display:flex;justify-content:space-between;font-size:.64rem;color:var(--texte-dim);margin-top:3px}
.ligne-marge{display:flex;justify-content:space-between;gap:10px;font-size:.75rem;padding:4px 0;
  border-bottom:1px dashed rgba(147,163,189,.18)}
.ligne-marge .droite{color:var(--texte-dim);white-space:nowrap}
.bandeau-hors-sol{background:linear-gradient(90deg,rgba(239,68,68,.35),rgba(239,68,68,.06));
  border:1px solid var(--rouge);border-radius:10px;padding:9px 12px;font-size:.79rem;margin-top:10px}
.bandeau-hors-sol b{font-size:.82rem;letter-spacing:.3px}
.delta-mesure{font-size:.75rem;padding:4px 0;border-bottom:1px dashed rgba(147,163,189,.18);
  display:flex;justify-content:space-between;gap:10px}
.delta-mesure .valeur{font-variant-numeric:tabular-nums;white-space:nowrap}
@media(max-width:640px){body{padding:10px}header.entete h1{font-size:1.15rem}
  .ruban-veille{position:static}.console-corps{grid-template-columns:1fr}
  .levier.compact{grid-template-columns:1fr 70px auto}}
</style>
</head>
<body>
<div class="conteneur">

  <header class="entete">
    <h1>Simulateur Macro-Politique — Démocratie et politique, du peuple, pour le peuple, par le peuple</h1>
    <p>Choisissez vos politiques : le modèle à 5 échelons propage les effets, domaine par domaine, avec les données publiques réelles du jour.</p>
    <div class="barre-contexte">
      <span class="pastille" id="badge-contexte">contexte : chargement…</span>
      <span class="pastille" id="badge-date">—</span>
      <span class="pastille" id="badge-leviers">—</span>
      <button class="primaire" id="btn-rafraichir" onclick="rafraichirDonnees()" data-aide="<b>Rafraîchir les données</b>Interroge Eurostat, la BCE, la Banque mondiale, le change et le pétrole depuis votre navigateur ; les sources sans en-tête CORS passent par le relais du serveur. Le contexte « instant T » et les scores sont ensuite recalculés.">Rafraîchir les données (API publiques)</button>
      <button class="discret" onclick="reinitialiser()" data-aide="<b>Réinitialiser</b>Ramène les 93 réglages à leur valeur neutre (aucune politique nouvelle) : la référence de comparaison.">Réinitialiser les leviers</button>
      <button class="primaire" id="btn-simuler" onclick="simuler(true)" data-aide="<b>Simuler avec impacts croisés</b>Recalcule les 5 années, les 20 domaines et la matrice levier × domaine (un réglage isolé à la fois). Compter moins d'une seconde.">Simuler avec impacts croisés</button>
      <button id="btn-export-json" disabled onclick="exporter('json')" data-aide="<b>Export JSON</b>Télécharge la simulation affichée : 5 étapes annuelles, 20 domaines, indicateurs, garde-fous et journal causal.">Export JSON</button>
      <button id="btn-export-csv" disabled onclick="exporter('csv')" data-aide="<b>Export CSV</b>Même contenu que l'export JSON, en tableau — pour retravailler les chiffres dans un tableur.">Export CSV</button>
    </div>
  </header>

  <div class="ruban-veille" id="ruban-veille">
    <span class="ruban-titre">Veille permanente</span>
    <span class="console-verdict" id="ruban-verdict">en attente de la première simulation…</span>
    <span class="ruban-strates" id="ruban-strates"></span>
    <span class="ruban-pop" id="ruban-population">risque population —</span>
    <span class="ruban-actions">
      <button class="discret" id="btn-console-details" onclick="basculerDetailsConsole()" data-aide="<b>Détail des seuils</b>Replie ou déplie le corps de la console de veille pour libérer l'écran : le verdict et les cinq strates restent affichés.">Masquer le détail des seuils</button>
      <button class="discret" id="btn-densite" onclick="basculerDensite()" data-aide="<b>Vue compacte</b>Une ligne par levier : les 93 paramètres tiennent à l'écran, tous réglables en direct.">Vue compacte</button>
      <button class="primaire" onclick="allerAuxLeviers()" data-aide="<b>Régler les 93 leviers</b>Fait défiler jusqu'à la grille des paramètres, où chaque geste relance la simulation en direct.">Régler les 93 leviers</button>
    </span>
  </div>

  <div id="zone-alertes"></div>

  <div class="infobulle" id="infobulle" role="tooltip" aria-hidden="true"></div>

  <section class="bloc">
    <h2>Contexte « instant T » <span class="aide">données publiques réellement collectées, avec provenance et licence</span></h2>
    <div class="grille metrics" id="grid-metrics"></div>
  </section>

  <section class="bloc console" id="console-pilotage">
    <div class="console-entete">
      <h2>Console de veille permanente <span class="aide">seuils tolérables → hors-sol, strate par strate, mis à jour à chaque réglage</span></h2>
      <div class="console-verdict" id="console-verdict">en attente de la première simulation…</div>
    </div>
    <div id="console-danger"></div>
    <div class="console-strates" id="console-strates"></div>
    <div class="console-corps" id="console-corps">
      <div>
        <h3 class="console-titre">Risque pour la population</h3>
        <div id="console-population"></div>
        <h3 class="console-titre">Effet de votre dernière modification</h3>
        <div id="console-derniere-modification"></div>
      </div>
      <div>
        <h3 class="console-titre">Messages de seuil</h3>
        <div id="console-alertes"></div>
        <h3 class="console-titre">Marges de manœuvre et audaces possibles</h3>
        <div id="console-marges"></div>
      </div>
    </div>
  </section>

  <section class="bloc">
    <h2>Surface d'impact de vos choix <span class="aide">recettes, dépenses et solde des mesures activées (année 5)</span></h2>
    <div class="grille metrics" id="grid-impact"></div>
  </section>

  <section class="bloc">
    <h2>Cascade systémique des 5 échelons <span class="aide">locale → nationale → européenne → mondiale → géopolitique</span></h2>
    <div class="strates-cascade" id="strates-cascade"></div>
  </section>

  <section class="bloc">
    <h2>Scénarios types du dépôt <span class="aide">9 situations rejouées par le moteur d'origine, année par année — pour comparaison</span></h2>
    <div class="grille scenarios" id="scenario-grid"></div>
  </section>

  <section class="bloc">
    <h2>Préréglages doctrinaux <span class="aide">des combinaisons cohérentes de leviers, chargées dans le simulateur puis ajustables curseur par curseur</span></h2>
    <div class="grille scenarios" id="preset-grid"></div>
  </section>

  <section class="bloc" id="section-leviers">
    <h2>Vos leviers <span class="aide">les 93 paramètres, tous visibles et actionnables — chaque geste se répercute en direct</span></h2>
    <div class="barre-leviers">
      <input class="recherche" id="recherche-levier" placeholder="Rechercher un levier (ex. TVA, défense, RIC, retraites…)" oninput="filtrerLeviers(this.value)" data-aide="<b>Rechercher un réglage</b>Filtre les 93 leviers par libellé, description ou clé technique. Le compteur affiche le nombre de leviers visibles et modifiés.">
      <span class="pastille" id="compteur-leviers">—</span>
      <label data-aide="<b>Vue compacte</b>Une ligne par levier, sans description : les 93 paramètres tiennent à l'écran tout en restant actionnables en direct.">
        <input type="checkbox" id="case-densite" onchange="basculerDensite(this.checked)"> Vue compacte (une ligne par levier)
      </label>
    </div>
    <div class="leviers-grille" id="leviers-grille"></div>
  </section>

  <section class="bloc">
    <h2>Résultats année par année <span class="aide">tableau détaillé des 5 échelons</span></h2>
    <div class="defilable"><table id="results-table"></table></div>
  </section>

  <section class="bloc">
    <h2>Trajectoires clés <span class="aide">déficit, dette, taux OAT, tension sociale et confiance</span></h2>
    <svg class="svg-chart" id="svg-chart" viewBox="0 0 900 210" preserveAspectRatio="none"></svg>
  </section>

  <section class="bloc">
    <h2>Domaines d'action publique <span class="aide">score 0-100 (50 = situation de départ) et indicateurs concrets</span></h2>
    <div class="grille domaines" id="domaines-grille"></div>
  </section>

  <section class="bloc">
    <h2>Matrice croisée levier × domaine <span class="aide">effet marginal de chaque levier actif, calculé par le modèle (différences finies)</span></h2>
    <div class="defilable"><table class="matrice" id="matrice-impacts"></table></div>
  </section>

  <section class="bloc">
    <h2>Journal causal du moteur <span class="aide">rétroactions générées année par année</span></h2>
    <div class="journal" id="journal"></div>
  </section>

  <section class="bloc">
    <h2>Sources, licences et fraîcheur <span class="aide">ce que le simulateur sait, et ce qu'il ne sait pas</span></h2>
    <div class="provenance" id="provenance"></div>
  </section>

  <p class="pied">
    Projet citoyen open-source — « gouvernement du peuple, par le peuple et pour le peuple »
    (Constitution du 4 octobre 1958, article 2). Les chiffres publics sont cités avec leur source ;
    les coefficients d'impact sont documentés dans chaque formule et modifiables.
  </p>
</div>

<script>
const SCENARIOS = ===SCENARIOS_JSON===;
const LIBELLES_NIVEAUX = {favorable:'favorable', tolerable:'tolérable', vigilance:'vigilance',
                          risque:'risqué', hors_sol:'hors-sol', inconnu:'non mesuré'};
//: Ce que la console surveille pour juger une modification (−1 : plus bas = mieux).
const EFFETS_SURVEILLES = [
  ['deficit_final_pct','Déficit (% du PIB)', -1, 2],
  ['dette_finale_pct','Dette (% du PIB)', -1, 1],
  ['taux_oat_final','OAT 10 ans (%)', -1, 2],
  ['spread_final_bps','Spread face au Bund (bps)', -1, 0],
  ['charge_dette_finale_mde','Charge de la dette (Md€/an)', -1, 1],
  ['tension_finale','Tension sociale', -1, 1],
  ['confiance_finale','Confiance démocratique', 1, 1],
  ['risque_censure_final_pct','Risque de censure (%)', -1, 0],
  ['solde_mesures_mde','Solde des mesures (Md€)', 1, 1],
  ['score_moyen_domaines','Score moyen des domaines', 1, 1]
];
let CATALOGUE = null;
let CONTEXTE = null;
let SORTIE = null;
let PARAMS = {};
//: Simulation précédente (paramètres envoyés + sortie) : c'est elle qui permet
//: d'afficher la conséquence de la DERNIÈRE modification, en direct.
let SIMULATION_PRECEDENTE = null;
//: Effets mesurés, par levier : affichés sous chaque curseur concerné.
let DERNIERES_PUCES = {};
//: Leviers touchés par la dernière modification (mis en évidence).
let LEVIERS_MODIFIES = new Set();
//: Vue compacte : une ligne par levier, pour que les 93 tiennent à l'écran.
let VUE_COMPACTE = false;
//: Vrai pendant qu'un curseur est manipulé : on ne reconstruit alors pas la
//: grille, sinon le curseur serait remplacé sous les doigts de l'utilisateur.
let REGLAGE_EN_COURS = false;
//: Bulles explicatives chargées depuis /api/bulle (une par levier, à la demande).
let BULLES = {};
//: Levier dont la bulle est dépliée : elle s'ouvre **dans** la carte du levier,
//: jamais par-dessus, pour que les 93 réglages restent visibles et actionnables.
let BULLE_OUVERTE = null;
//: Leviers déjà demandés au serveur (évite les appels répétés).
let BULLES_DEMANDEES = new Set();
//: Libellés des 20 domaines, repris du catalogue pour les bulles.
let LIBELLES_DOMAINES = {};

function fmt(valeur, precision){
  if (valeur === null || valeur === undefined || Number.isNaN(valeur)) return '—';
  const p = (precision === undefined) ? 1 : precision;
  return Number(valeur).toLocaleString('fr-FR', {minimumFractionDigits:p, maximumFractionDigits:p});
}
function couleurDelta(valeur){
  if (Math.abs(valeur) < 0.05) return 'neutre';
  return valeur > 0 ? 'hausse' : 'baisse';
}
function pastille(mode){
  const libelles = {live:'données live', reference:'référence datée 2026-10-05', mixte:'données mixtes'};
  return `<span class="pastille ${mode}">${libelles[mode] || mode}</span>`;
}

/* ── Chargement du catalogue (leviers + domaines) ───────────────────────── */
async function chargerCatalogue(){
  const reponse = await fetch('/api/catalogue');
  CATALOGUE = await reponse.json();
  PARAMS = Object.assign({}, CATALOGUE.parametres.defauts);
  renderLeviers('');
  renderPresets();
}

/* ── Contexte « instant T » ─────────────────────────────────────────────── */
async function chargerContexte(rafraichir){
  const reponse = await fetch(`/api/contexte?refresh=${rafraichir ? '1' : '0'}`);
  CONTEXTE = await reponse.json();
  renderContexte();
}
function renderContexte(){
  const c = CONTEXTE.contexte;
  document.getElementById('badge-contexte').outerHTML = pastille(c.mode).replace('<span', '<span id="badge-contexte"');
  document.getElementById('badge-date').textContent = `horodatage : ${c.horodatage.replace('T',' ').slice(0,16)} UTC`;
  const metriques = [
    ['PIB nominal', fmt(c.pib_nominal_mde, 0) + ' Md€', ''],
    ['Dette publique', fmt(c.dette_publique_pct_pib, 1) + ' % PIB', ''],
    ['Déficit public', fmt(c.deficit_public_pct_pib, 1) + ' % PIB', ''],
    ['OAT 10 ans', fmt(c.taux_oat_10ans, 2) + ' %', 'spread ' + fmt(c.spread_oat_bund_bps, 0) + ' bps vs Bund'],
    ['Taux BCE (dépôt)', fmt(c.taux_bce_depot, 2) + ' %', ''],
    ['Inflation France', fmt(c.inflation_pct, 1) + ' %', 'zone euro ' + fmt(c.inflation_zone_euro_pct, 1) + ' %'],
    ['Chômage', fmt(c.chomage_pct, 1) + ' %', ''],
    ['Pétrole Brent', fmt(c.brent_usd, 2) + ' $/baril', ''],
    ['Change EUR/USD', fmt(c.eur_usd, 4), ''],
    ['Pauvreté (60 % médian)', fmt(c.taux_pauvrete_pct, 1) + ' %', 'Gini ' + fmt(c.indice_gini, 1)],
    ['Charge de la dette estimée', fmt(c.charge_dette_estimee_mde, 1) + ' Md€/an', ''],
    ['Prélèvements obligatoires', fmt(c.prelevements_obligatoires_pct_pib, 1) + ' % PIB', ''],
  ];
  document.getElementById('grid-metrics').innerHTML = metriques.map(([libelle, valeur, sous]) =>
    `<div class="carte metric"><div class="libelle">${libelle}</div>
      <div class="valeur">${valeur}</div><div class="delta neutre">${sous}</div></div>`).join('');
  const provenance = (CONTEXTE.contexte && CONTEXTE.contexte.provenance) || CONTEXTE.provenance || {};
  const lignes = Object.entries(provenance).map(([champ, info]) => {
    const statut = info.statut === 'live' ? '🟢 live' : (info.statut === 'reference' ? '🟠 référence' : '⚪ non collectée');
    const periode = info.periode ? ` · ${info.periode}` : '';
    return `<div><b>${info.libelle}</b> : ${statut}${periode} · ${info.source}
      ${info.url ? ` · <a href="${info.url}" target="_blank" rel="noopener">source</a>` : ''}
      ${info.licence ? ` · <i>${info.licence}</i>` : ''}</div>`;
  }).join('');
  const complementaires = Object.values((CONTEXTE.contexte && CONTEXTE.contexte.series_complementaires) || {});
  const blocComplementaire = complementaires.length
    ? '<div style="margin-top:10px"><b>Séries complémentaires collectées</b> (non utilisées pour le calibrage,'
      + ' conservées pour information) :<br>' + complementaires.map(info =>
        `${info.libelle} : ${fmt(info.valeur, 2)} ${info.unite} (${info.periode || '—'}) — <i>${info.licence}</i>`
      ).join('<br>') + '</div>'
    : '';
  document.getElementById('provenance').innerHTML = lignes + blocComplementaire
    + '<div style="margin-top:8px">Rappel : le mode « référence » signifie que le serveur n\'a pas pu (ou pas encore)'
    + ' interroger les API publiques. Le bouton « Rafraîchir les données » interroge directement vos API'
    + ' depuis le navigateur (puis relaie par le serveur les sources sans CORS), et transmet les valeurs au simulateur.</div>'
    + '<div style="margin-top:8px"><b>Comment lire les scores :</b> chaque domaine est noté de 0 à 100 par rapport à la'
    + ' <b>trajectoire de référence modélisée</b> (aucun levier activé) : 50 = référence, au-dessus = amélioration attendue,'
    + ' en dessous = dégradation. Les écarts affichés sont donc des <b>écarts de politique publique</b>, jamais des niveaux absolus.</div>';
}

/* ── Rafraîchissement navigateur → serveur (adapte les mêmes API) ───────── */
function extraireEurostat(charge, chemin){
  const valeur = charge.value || {};
  const cles = Object.keys(valeur);
  if (!cles.length) return null;
  let cle = chemin && valeur[chemin] !== undefined ? chemin : cles[cles.length - 1];
  let periode = null;
  try {
    const temps = charge.dimension.time.category.index;
    const codes = Object.keys(temps);
    periode = codes[Number(cle)] || codes[codes.length - 1];
  } catch (erreur) { periode = null; }
  return {valeur: Number(valeur[cle]), periode: periode};
}
function extraireSdmx(charge, chemin){
  const jeux = charge.dataSets || [];
  if (!jeux.length) return null;
  const series = jeux[0].series || {};
  const premiere = series[Object.keys(series)[0]];
  const observations = (premiere && premiere.observations) || {};
  const cles = Object.keys(observations);
  if (!cles.length) return null;
  const brut = observations[cles[0]];
  const valeur = Array.isArray(brut) ? brut[0] : brut;
  let periode = null;
  try {
    const dims = charge.structure.dimensions.observation || [];
    const temps = dims.find(d => d.role === 'time');
    if (temps && temps.values.length) periode = temps.values[0].id;
  } catch (erreur) { periode = null; }
  return {valeur: Number(valeur), periode: periode};
}
function extraireGenerique(adaptateur, charge, chemin){
  if (adaptateur === 'eurostat') return extraireEurostat(charge, chemin);
  if (adaptateur === 'sdmx') return extraireSdmx(charge, chemin);
  if (adaptateur === 'frankfurter'){
    const taux = charge.rates || {};
    const devise = chemin || Object.keys(taux)[0];
    if (taux[devise] === undefined) return null;
    return {valeur: Number(taux[devise]), periode: charge.date || null};
  }
  if (adaptateur === 'opendatasoft'){
    const resultats = charge.results || [];
    if (!resultats.length) return null;
    let brut = resultats[0];
    (chemin || '').split('.').forEach(morceau => { if (brut && brut[morceau] !== undefined) brut = brut[morceau]; });
    return {valeur: Number(brut), periode: resultats[0].date || null};
  }
  if (adaptateur === 'worldbank'){
    const obs = (charge[1] || [])[0];
    if (!obs || obs.value === null) return null;
    return {valeur: Number(obs.value), periode: obs.date || null};
  }
  if (adaptateur === 'yahoo'){
    const resultats = (charge.chart && charge.chart.result) || [];
    if (!resultats.length) return null;
    const meta = resultats[0].meta || {};
    if (meta.regularMarketPrice === undefined) return null;
    const date = meta.regularMarketTime ? new Date(meta.regularMarketTime * 1000).toISOString().slice(0,10) : null;
    return {valeur: Number(meta.regularMarketPrice), periode: date};
  }
  return null;
}
async function rafraichirDonnees(){
  const bouton = document.getElementById('btn-rafraichir');
  bouton.disabled = true; bouton.textContent = 'Interrogation des API publiques…';
  const spec = CONTEXTE.browser || {};
  const lectures = {};
  let succes = 0;
  for (const [cle, indicateur] of Object.entries(spec)){
    for (const source of indicateur.sources){
      try {
        const reponse = await fetch(source.url, {mode:'cors'});
        if (!reponse.ok) continue;
        const charge = await reponse.json();
        const lecture = extraireGenerique(source.adaptateur, charge, source.chemin);
        if (!lecture || !Number.isFinite(lecture.valeur)) continue;
        lectures[cle] = {cle: cle, valeur: lecture.valeur, periode: lecture.periode,
                         fournisseur: source.fournisseur, url: source.url, statut: 'live'};
        succes += 1;
        break;
      } catch (erreur) { /* source suivante */ }
    }
    if (!lectures[cle] && indicateur.proxy_url){
      // Repli même-origine : le serveur relaie les sources sans CORS
      // (Yahoo, Stooq, ICE/EEX). Le serveur n'accepte que les sources
      // déclarées au registre : ce n'est pas un proxy ouvert.
      try {
        const reponse = await fetch(indicateur.proxy_url);
        if (reponse.ok){
          const charge = await reponse.json();
          const lecture = charge.lecture;
          if (lecture && Number.isFinite(Number(lecture.valeur))){
            lectures[cle] = {cle: cle, valeur: Number(lecture.valeur), periode: lecture.periode,
                             fournisseur: lecture.fournisseur, url: lecture.url,
                             statut: lecture.statut === 'live' ? 'live' : 'reference'};
            if (lecture.statut === 'live') succes += 1;
          }
        }
      } catch (erreur) { /* le serveur garde ses valeurs */ }
    }
  }
  if (succes > 0){
    try {
      await fetch('/api/donnees', {method:'POST', headers:{'Content-Type':'application/json'},
                                   body: JSON.stringify({lectures: lectures})});
    } catch (erreur) { /* le serveur reste sur ses valeurs */ }
  }
  await chargerContexte(false);
  bouton.disabled = false;
  bouton.textContent = succes > 0
    ? `Rafraîchir les données (${succes} séries mises à jour)`
    : 'Rafraîchir les données (aucune source joignable)';
  if (SORTIE) simuler(false);
}

/* ── Leviers : les 93 paramètres, tous visibles et actionnables ────────── */
function filtreCourant(){
  const champ = document.getElementById('recherche-levier');
  return (champ && champ.value) || '';
}
function basculerDensite(force){
  VUE_COMPACTE = (force === undefined) ? !VUE_COMPACTE : !!force;
  const case_ = document.getElementById('case-densite');
  if (case_) case_.checked = VUE_COMPACTE;
  const bouton = document.getElementById('btn-densite');
  if (bouton) bouton.textContent = VUE_COMPACTE ? 'Vue confort' : 'Vue compacte';
  renderLeviers(filtreCourant());
}
function basculerDetailsConsole(){
  const corps = document.getElementById('console-corps');
  if (!corps) return;
  corps.classList.toggle('replie');
  const bouton = document.getElementById('btn-console-details');
  if (bouton) bouton.textContent = corps.classList.contains('replie')
    ? 'Afficher le détail des seuils' : 'Masquer le détail des seuils';
}
function allerAuxLeviers(){
  const section = document.getElementById('section-leviers');
  if (section && section.scrollIntoView) section.scrollIntoView({behavior:'smooth', block:'start'});
}
/* ── Aides au survol (infobulles) ─────────────────────────────────────────
   Tout élément portant `data-aide` (bouton, case à cocher, champ) ou
   `data-aide-levier` (réglage : curseur, interrupteur, étiquette de valeur)
   s'explique au survol et au focus clavier. L'infobulle est une couche fixe
   qui ne capte aucun clic (`pointer-events:none`) et disparaît au départ de
   la souris : les leviers restent visibles et actionnables.                    */
function elementInfobulle(){ return document.getElementById('infobulle'); }
function levierParCle(cle){
  if (!CATALOGUE) return null;
  return CATALOGUE.parametres.familles.flatMap(f => f.leviers).find(l => l.cle === cle) || null;
}
function texteAideLevier(cle){
  const levier = levierParCle(cle);
  if (!levier) return '';
  const valeur = PARAMS[cle];
  const famille = (CATALOGUE.familles || []).find(f => f.cle === levier.famille);
  const actif = levier.type === 'interrupteur' ? (valeur >= 0.5 ? 'activé' : 'désactivé')
    : `${fmt(valeur, levier.precision)} ${levier.unite === 'bool' ? '' : levier.unite}`.trim();
  const defaut = levier.type === 'interrupteur'
    ? (levier.defaut >= 0.5 ? 'activé' : 'désactivé')
    : `${fmt(levier.defaut, levier.precision)} ${levier.unite === 'bool' ? '' : levier.unite}`.trim();
  const lignes = [`<span class="aide-titre">${levier.libelle}</span>`];
  lignes.push(`${famille ? famille.libelle : levier.famille} · ${levier.type}`
    + (levier.unite && levier.unite !== 'bool' ? ` · unité : ${levier.unite}` : ''));
  lignes.push(`valeur actuelle <b>${actif}</b> (défaut ${defaut})`);
  if (levier.type === 'interrupteur'){
    lignes.push('interrupteur : activé ou désactivé');
  } else {
    lignes.push(`plage ${fmt(levier.minimum, levier.precision)} → `
      + `${fmt(levier.maximum, levier.precision)} ${levier.unite} · pas ${fmt(levier.pas, 2)}`);
  }
  if (levier.description) lignes.push(levier.description);
  const declares = Object.entries(levier.effets_directs || {}).slice(0, 4).map(([theme, coefficient]) =>
    `${theme} ${coefficient > 0 ? '+' : ''}${fmt(coefficient, 2)}`);
  if (declares.length) lignes.push(`Effets déclarés : ${declares.join(' ; ')}`);
  const puces = (DERNIERES_PUCES[cle] || []).slice(0, 3).map(puce =>
    `${puce.libelle} ${puce.effet_score > 0 ? '+' : ''}${fmt(puce.effet_score, 1)} pt`);
  if (puces.length) lignes.push(`Mesuré à l'instant sur ce réglage : ${puces.join(' ; ')}`);
  const bulle = BULLES[cle];
  if (bulle && bulle.bilan_domaines){
    const mouvements = bulle.bilan_domaines.filter(domaine => domaine.touche).slice(0, 3).map(domaine => {
      const ecart = Math.abs(domaine.maximum) >= Math.abs(domaine.minimum) ? domaine.maximum : domaine.minimum;
      return `${domaine.libelle} ${ecart > 0 ? '+' : ''}${fmt(ecart, 1)} pt`;
    });
    if (mouvements.length) lignes.push(`Aux bornes du réglage : ${mouvements.join(' ; ')}`);
    if (bulle.lecture && bulle.lecture.phrase){
      lignes.push(bulle.lecture.phrase.slice(0, 190) + (bulle.lecture.phrase.length > 190 ? '…' : ''));
    }
  } else {
    lignes.push('Cliquez sur « interactions » pour la chaîne complète : médiateurs touchés, '
      + 'répercussions par domaine, garde-fous et strates.');
  }
  return lignes.join('<br>');
}
function texteAideElement(cible){
  if (!cible || !cible.getAttribute) return '';
  if (cible.getAttribute('data-aide-levier')) return texteAideLevier(cible.getAttribute('data-aide-levier'));
  return cible.getAttribute('data-aide') || '';
}
function positionnerInfobulle(cible){
  const bulle = elementInfobulle();
  if (!bulle) return;
  const rect = (cible && typeof cible.getBoundingClientRect === 'function')
    ? cible.getBoundingClientRect() : null;
  if (!rect || (!rect.width && !rect.height)) return;
  const largeur = (typeof innerWidth === 'number') ? innerWidth : 1200;
  const hauteur = (typeof innerHeight === 'number') ? innerHeight : 900;
  const gauche = Math.max(8, Math.min(rect.left, largeur - 364));
  const enBas = rect.bottom + 12;
  bulle.style.left = `${gauche}px`;
  bulle.style.top = `${(enBas + 220 > hauteur ? Math.max(8, rect.top - 12) : enBas)}px`;
}
function afficherInfobulle(html, cible){
  const bulle = elementInfobulle();
  if (!bulle || !html) return;
  bulle.innerHTML = html;
  bulle.classList.add('visible');
  bulle.setAttribute('aria-hidden', 'false');
  positionnerInfobulle(cible);
}
function masquerInfobulle(){
  const bulle = elementInfobulle();
  if (!bulle) return;
  bulle.classList.remove('visible');
  bulle.setAttribute('aria-hidden', 'true');
}
function survoler(cible){
  const texte = texteAideElement(cible);
  if (!texte){ masquerInfobulle(); return; }
  afficherInfobulle(texte, cible);
}
function initialiserInfobulles(){
  if (!document.addEventListener) return;
  const cherche = (noeud) => {
    if (!noeud || !noeud.closest) return null;
    // La bulle dépliée reste lisible : pas d'infobulle par-dessus son contenu.
    if (noeud.closest('.bulle-levier')) return null;
    return noeud.closest('[data-aide], [data-aide-levier]');
  };
  document.addEventListener('mouseover', (evenement) => {
    const cible = cherche(evenement.target);
    if (cible) survoler(cible);
  });
  document.addEventListener('mouseout', (evenement) => {
    if (cherche(evenement.relatedTarget)) return;
    masquerInfobulle();
  });
  document.addEventListener('focusin', (evenement) => {
    const cible = cherche(evenement.target);
    if (cible) survoler(cible);
  });
  document.addEventListener('focusout', () => masquerInfobulle());
  document.addEventListener('mousedown', () => masquerInfobulle());
  document.addEventListener('scroll', () => masquerInfobulle(), true);
}

/* ── Bulles explicatives par levier ────────────────────────────────────────
   Chaque réglage porte un bouton « interactions » : la bulle s'ouvre dans la
   carte du levier (jamais par-dessus), avec la chaîne technique, les
   répercussions mesurées borne par borne et la lecture opportunités /
   désagréments. Le contenu vient du serveur (/api/bulle), calculé par
   simulateur/bulles.py sur les formules réelles du modèle.                    */
function libelleDomaine(cle){
  if (CATALOGUE && CATALOGUE.domaines && !Object.keys(LIBELLES_DOMAINES).length){
    for (const domaine of CATALOGUE.domaines){ LIBELLES_DOMAINES[domaine.cle] = domaine.libelle; }
  }
  return LIBELLES_DOMAINES[cle] || cle;
}
function montantTexte(emission){
  if (emission.montant === null || emission.montant === undefined) return 'champ du moteur';
  const signe = emission.montant > 0 ? '+' : '';
  return `${signe}${fmt(emission.montant, 2)} ${emission.unite || ''}`.trim();
}
function pucesDomaines(domaines, maximum){
  return (domaines || []).slice(0, maximum || 20).map(domaine => {
    const delta = domaine.delta;
    return `<span class="bulle-domaine ${delta >= 0 ? 'pos' : 'neg'}">${libelleDomaine(domaine.cle)} `
      + `${delta > 0 ? '+' : ''}${fmt(delta, 1)} pt</span>`;
  }).join('');
}
function chaineHtml(bulle){
  const lignes = (bulle.emissions || []).map(emission => {
    let relais;
    if (emission.relaye){
      const lecteurs = (emission.consommateurs || []).slice(0, 3).map(consommateur =>
        `${consommateur.libelle} (${libelleDomaine(consommateur.domaine)}, ×${fmt(consommateur.coefficient, 2)})`
      ).join(' ; ');
      relais = `lu par : ${lecteurs}`;
    } else if (emission.relais){
      relais = `relais : ${emission.relais}`;
    } else {
      relais = 'aucun relais identifié dans les formules actuelles';
    }
    return `<li><span class="bulle-med">${emission.mediateur}</span> ${montantTexte(emission)} → ${relais}</li>`;
  }).join('');
  const moteur = bulle.champ_moteur
    ? `<li><span class="bulle-med">${bulle.champ_moteur.champ}</span> état du moteur → `
      + "l'effet vit dans les strates 1 à 5 (journal ci-dessous)</li>" : '';
  const maillons = (bulle.maillons_non_relayes || []).map(maillon =>
    `<li class="bulle-alerte">⚠ ${maillon.mediateur} : ${maillon.note}</li>`).join('');
  const vide = (!lignes && !moteur) ? '<li>Aucun médiateur propre : le levier agit par le champ du moteur.</li>' : '';
  return `<div class="bulle-section"><span class="bulle-titre">Chaîne d'interaction (plein régime)</span>`
    + `<ul>${lignes}${moteur}${vide}${maillons}</ul></div>`;
}
function effetsDeclaresHtml(bulle){
  const jetons = [...(bulle.effets_directs || []), ...(bulle.effets_hors_domaine || [])].map(effet => {
    const domaines = (effet.domaines || []).map(cle => libelleDomaine(cle)).join(', ');
    const precision = domaines ? ` → ${domaines}` : ' (thème transverse)';
    return `<span class="bulle-domaine ${effet.coefficient >= 0 ? 'pos' : 'neg'}">`
      + `${effet.theme} ${effet.coefficient > 0 ? '+' : ''}${fmt(effet.coefficient, 2)}${precision}</span>`;
  }).join('');
  return `<div class="bulle-section"><span class="bulle-titre">Effets déclarés au catalogue</span>`
    + `<div>${jetons || 'aucun'}</div></div>`;
}
function mesuresHtml(bulle){
  const blocs = (bulle.mesures || []).map(mesure => {
    const seuils = mesure.seuils || {};
    const population = seuils.population || {};
    const mouvementes = mesure.domaines_mouvementes || [];
    const negatifs = mouvementes.filter(domaine => domaine.delta < 0).length;
    const classes = [];
    if (negatifs) classes.push('bulle-aggrave');
    if (mouvementes.length - negatifs) classes.push('bulle-favorable');
    const domaines = mouvementes.length
      ? pucesDomaines(mouvementes, 20)
      : '<i>aucun des 20 domaines ne bouge au-delà de 0,2 pt</i>';
    const indicateurs = (mesure.indicateurs || []).slice(0, 4).map(indicateur =>
      `<li>${indicateur.libelle} : ${fmt(indicateur.valeur_reference, 2)} → ${fmt(indicateur.valeur, 2)} `
      + `${indicateur.unite || ''} (${indicateur.ecart > 0 ? '+' : ''}${fmt(indicateur.ecart, 2)})</li>`
    ).join('');
    const alertes = (seuils.alertes || []).slice(0, 4).map(alerte =>
      `<li class="bulle-alerte ${alerte.niveau}">${alerte.libelle} : ${alerte.valeur_texte} `
      + `${alerte.unite || ''} — ${alerte.message || ''} (${alerte.strate_libelle || ''})</li>`
    ).join('');
    const journal = (mesure.journal || []).slice(0, 4).map(ligne =>
      `<li>${ligne.strate ? `[${ligne.strate}] ` : ''}${ligne.texte}</li>`).join('');
    const risque = (population.risque === null || population.risque === undefined) ? ''
      : ` · risque population ${fmt(population.risque, 1)} (${population.niveau_libelle || '—'})`;
    return `<div class="bulle-mesure ${classes.join(' ')}">`
      + `<div><b>${mesure.nom}</b> · score moyen ${fmt(mesure.score_moyen, 1)} · `
      + `niveau ${seuils.niveau_global_libelle || '—'}${risque}</div>`
      + `<div>${domaines}</div>`
      + (indicateurs ? `<ul>${indicateurs}</ul>` : '')
      + (alertes ? `<ul>${alertes}</ul>` : '')
      + (journal ? `<ul class="bulle-journal">${journal}</ul>` : '')
      + `</div>`;
  }).join('');
  return `<div class="bulle-section"><span class="bulle-titre">Répercussions mesurées `
    + `(réglage isolé, autres leviers neutres)</span>${blocs}</div>`;
}
function lectureHtml(bulle){
  const lecture = bulle.lecture || {};
  const liste = (entrees, gabarit) => (entrees || []).map(gabarit).join('');
  const opportunites = liste(lecture.opportunites, entree =>
    `<li><b>${entree.libelle}</b> +${fmt(entree.gain, 1)} pt à « ${entree.mesure} »`
    + (entree.relais && entree.relais.length ? ` — via ${entree.relais.join(' ; ')}` : '') + '</li>');
  const desagrements = liste(lecture.desagrements, entree =>
    `<li><b>${entree.libelle}</b> ${fmt(entree.perte, 1)} pt à « ${entree.mesure} »`
    + (entree.relais && entree.relais.length ? ` — via ${entree.relais.join(' ; ')}` : '') + '</li>');
  const surveillance = liste(lecture.a_surveiller, entree =>
    `<li class="bulle-alerte ${entree.niveau || ''}">${entree.libelle}`
    + (entree.niveau_libelle ? ` — ${entree.niveau_libelle}` : '')
    + (entree.strate_libelle ? ` (${entree.strate_libelle})` : '')
    + ((entree.valeur_texte === undefined || entree.valeur_texte === null)
       ? '' : ` : ${entree.valeur_texte} ${entree.unite || ''}`)
    + ((entree.avant === undefined || entree.avant === null)
       ? '' : ` — ${fmt(entree.avant, 1)} → ${fmt(entree.apres, 1)}`) + '</li>');
  const compensations = liste(lecture.compensations, entree =>
    `<li>${entree.libelle} : ${(entree.leviers || []).map(levier => levier.libelle).join(', ')}</li>`);
  const bloc = (titre, contenu) => contenu
    ? `<div class="bulle-section"><span class="bulle-titre">${titre}</span><ul>${contenu}</ul></div>` : '';
  const bouge = (lecture.opportunites || []).length + (lecture.desagrements || []).length;
  return bloc('Opportunités', opportunites) + bloc('Désagréments', desagrements)
    + bloc('À surveiller (garde-fous et strates)', surveillance)
    + bloc('Pistes de compensation déclarées au catalogue', compensations)
    + (bouge ? '' : '<div class="bulle-section">Aucun domaine noté ne bouge aux bornes de ce '
        + 'réglage : voir la chaîne d\'interaction et le journal des strates.</div>');
}
function htmlBulle(bulle){
  return `<div class="bulle-levier">`
    + `<div class="bulle-titre">Bulle explicative — ${bulle.libelle} `
    + `(${bulle.famille_libelle}, ${bulle.type})</div>`
    + chaineHtml(bulle) + effetsDeclaresHtml(bulle) + mesuresHtml(bulle) + lectureHtml(bulle)
    + (bulle.sans_effet_mesure
       ? '<div class="bulle-section bulle-alerte">Aucun des 20 domaines notés ne bouge : les '
         + 'répercussions listées ci-dessus sont institutionnelles (strates 1 à 5).</div>' : '')
    + `<div class="bulle-note">${bulle.avertissement || ''}</div></div>`;
}
function bulleHtml(cle){
  if (BULLE_OUVERTE !== cle) return '';
  if (Object.prototype.hasOwnProperty.call(BULLES, cle)){
    return BULLES[cle]
      ? htmlBulle(BULLES[cle])
      : '<div class="bulle-levier bulle-chargement">Bulle indisponible : le serveur n\'a pas répondu.</div>';
  }
  return '<div class="bulle-levier bulle-chargement">Calcul des interactions en cours…</div>';
}
function bulleBoutonHtml(cle){
  const actif = BULLE_OUVERTE === cle;
  return `<button class="bulle-bouton${actif ? ' actif' : ''}" data-bulle="${cle}" `
    + `data-aide="<b>Bulle explicative</b>Ouvre la fiche du réglage : chaîne d'interaction `
    + '(médiateurs → indicateurs → domaines), répercussions mesurées à chaque borne, '
    + 'garde-fous et strates concernées, puis opportunités, désagréments et pistes de '
    + 'compensation. La fiche s\'ouvre dans la carte, sans recouvrir les leviers." '
    + `onclick="ouvrirBulle('${cle}')">`
    + `${actif ? '▾ interactions' : '▸ interactions'}</button>`;
}
async function chargerBulle(cle){
  if (Object.prototype.hasOwnProperty.call(BULLES, cle) || BULLES_DEMANDEES.has(cle)) return;
  BULLES_DEMANDEES.add(cle);
  try {
    const reponse = await fetch(`/api/bulle?levier=${encodeURIComponent(cle)}&detail=complet`);
    const donnees = await reponse.json();
    BULLES[cle] = (donnees && donnees.cle === cle) ? donnees : null;
  } catch (erreur){
    BULLES[cle] = null;
  }
  if (BULLE_OUVERTE === cle) renderLeviers(filtreCourant());
}
async function ouvrirBulle(cle){
  if (BULLE_OUVERTE === cle){
    BULLE_OUVERTE = null;
    renderLeviers(filtreCourant());
    return;
  }
  BULLE_OUVERTE = cle;
  renderLeviers(filtreCourant());
  await chargerBulle(cle);
}
function puceHtml(effet){
  const sens = effet.effet_score > 0 ? 'amélioration' : 'dégradation';
  const texteAide = `<b>${effet.libelle}</b>Effet mesuré après votre dernière modification : ${sens} de `
    + `${fmt(Math.abs(effet.effet_score), 1)} pt de score (différences finies, réglage isolé, `
    + 'comparaison à la trajectoire neutre).';
  return `<span class="puce-effect ${effet.effet_score > 0 ? 'pos' : 'neg'}" data-aide="${texteAide}">`
    + `${effet.libelle} ${effet.effet_score > 0 ? '+' : ''}${fmt(effet.effet_score, 1)}</span>`;
}
function pucesHtml(cle){
  const effets = DERNIERES_PUCES[cle] || [];
  if (!effets.length) return '';
  return '<div class="puces">' + effets.map(puceHtml).join('') + '</div>';
}
function renderLeviers(filtre){
  const recherche = (filtre || '').toLowerCase();
  const zones = CATALOGUE.parametres.familles.map(famille => {
    const leviers = famille.leviers.filter(levier =>
      !recherche || levier.libelle.toLowerCase().includes(recherche)
      || levier.description.toLowerCase().includes(recherche)
      || levier.cle.includes(recherche));
    if (!leviers.length) return '';
    const contenu = leviers.map(levier => {
      const valeur = PARAMS[levier.cle];
      const modifie = LEVIERS_MODIFIES.has(levier.cle);
      const valeurTexte = levier.type === 'interrupteur'
        ? (valeur >= 0.5 ? 'activé' : 'désactivé')
        : `${fmt(valeur, levier.precision)} ${levier.unite === 'bool' ? '' : levier.unite}`;
      const bouton = bulleBoutonHtml(levier.cle);
      const bascule = `<div class="ligne" data-aide-levier="${levier.cle}"><label class="bascule"><input type="checkbox" aria-label="${levier.libelle}" ${valeur >= 0.5 ? 'checked' : ''}
             onchange="majLevier('${levier.cle}', this.checked ? 1 : 0)"> ${levier.libelle}
             <span class="valeur" data-aide-levier="${levier.cle}">${valeurTexte}</span></label>${bouton}</div>`;
      const curseur = `<div class="ligne" data-aide-levier="${levier.cle}"><span class="nom" data-aide-levier="${levier.cle}">${levier.libelle}</span>
             <span class="valeur" data-aide-levier="${levier.cle}">${valeurTexte}</span>${bouton}</div>
           <input type="range" data-aide-levier="${levier.cle}" aria-label="${levier.libelle}" min="${levier.minimum}" max="${levier.maximum}" step="${levier.pas}"
                  value="${valeur}" oninput="majLevier('${levier.cle}', parseFloat(this.value))"
                  onchange="terminerReglage()">`;
      const curseurCompact = `<span class="nom" data-aide-levier="${levier.cle}">${levier.libelle}</span>
           <input type="range" data-aide-levier="${levier.cle}" aria-label="${levier.libelle}" min="${levier.minimum}" max="${levier.maximum}" step="${levier.pas}"
                  value="${valeur}" oninput="majLevier('${levier.cle}', parseFloat(this.value))"
                  onchange="terminerReglage()">
           <span class="valeur" data-aide-levier="${levier.cle}">${valeurTexte}</span>${bouton}`;
      if (VUE_COMPACTE){
        const contenuLevier = levier.type === 'interrupteur'
          ? `<span class="nom" data-aide-levier="${levier.cle}">${levier.libelle}</span>
             <label class="bascule" data-aide-levier="${levier.cle}"><input type="checkbox" data-aide-levier="${levier.cle}" aria-label="${levier.libelle}" ${valeur >= 0.5 ? 'checked' : ''}
               onchange="majLevier('${levier.cle}', this.checked ? 1 : 0); terminerReglage()"></label>
             <span class="valeur" data-aide-levier="${levier.cle}">${valeurTexte}</span>${bouton}`
          : curseurCompact;
        return `<div class="levier compact${modifie ? ' modifie' : ''}" data-cle="${levier.cle}" data-aide-levier="${levier.cle}">
          ${contenuLevier}${pucesHtml(levier.cle)}${bulleHtml(levier.cle)}</div>`;
      }
      const commande = levier.type === 'interrupteur' ? bascule : curseur;
      return `<div class="levier${modifie ? ' modifie' : ''}" data-cle="${levier.cle}" data-aide-levier="${levier.cle}">
        ${commande}
        <div class="desc">${levier.description}</div>
        ${levier.source ? `<div class="source">Source : ${levier.source}</div>` : ''}
        ${pucesHtml(levier.cle)}${bulleHtml(levier.cle)}
      </div>`;
    }).join('');
    return `<div class="famille${VUE_COMPACTE ? ' compacte' : ''}">
      <h3 style="color:${famille.couleur}">${famille.libelle}</h3>${contenu}</div>`;
  }).join('');
  document.getElementById('leviers-grille').innerHTML = zones
    || '<div class="carte">Aucun levier ne correspond à cette recherche.</div>';
  const grille = document.getElementById('leviers-grille');
  grille.className = 'leviers-grille' + (VUE_COMPACTE ? ' compacte' : '');
  const affiches = (grille.innerHTML.match(/class="levier/g) || []).length;
  const compteur = document.getElementById('compteur-leviers');
  if (compteur){
    compteur.textContent = `${affiches} levier(s) affiché(s)`
      + (LEVIERS_MODIFIES.size ? ` · ${LEVIERS_MODIFIES.size} modifié(s)` : '')
      + (VUE_COMPACTE ? ' · vue compacte' : '');
  }
}
function filtrerLeviers(valeur){ renderLeviers(valeur); }
function terminerReglage(){
  // Le curseur vient d'être relâché : on peut reconstruire la grille sans
  // interrompre la manipulation, pour afficher les puces d'impact à jour.
  REGLAGE_EN_COURS = false;
  renderLeviers(filtreCourant());
}
function majLevier(cle, valeur){
  REGLAGE_EN_COURS = true;
  PARAMS[cle] = valeur;
  const carte = document.querySelector(`.levier[data-cle="${cle}"]`);
  if (carte){
    const levier = CATALOGUE.parametres.familles.flatMap(f => f.leviers).find(l => l.cle === cle);
    const cible = carte.querySelector('.valeur');
    if (cible && levier){
      cible.textContent = levier.type === 'interrupteur'
        ? (valeur >= 0.5 ? 'activé' : 'désactivé')
        : `${fmt(valeur, levier.precision)} ${levier.unite}`;
    }
  }
  planifierSimulation();
}
let minuteur = null;
function planifierSimulation(){
  document.getElementById('badge-leviers').textContent =
    `${nombreLeviersActifs()} leviers actifs — calcul en cours…`;
  if (minuteur) clearTimeout(minuteur);
  minuteur = setTimeout(() => simuler(false), 180);
}
function nombreLeviersActifs(){
  if (!CATALOGUE) return 0;
  const defauts = CATALOGUE.parametres.defauts;
  return Object.entries(PARAMS).filter(([cle, valeur]) =>
    Math.abs(valeur - defauts[cle]) > 1e-9).length;
}

/* ── Scénarios et préréglages ───────────────────────────────────────────── */
function renderScenarios(){
  const grid = document.getElementById('scenario-grid');
  grid.innerHTML = '';
  Object.entries(SCENARIOS).forEach(([key, scenario]) => {
    const card = document.createElement('div');
    card.className = 'scenario-card carte';
    card.style.borderLeftColor = scenario.couleur || '#38bdf8';
    card.dataset.key = key;
    card.setAttribute('data-aide', `<b>${scenario.nom}</b>${scenario.description}`
      + '<br>Cliquez pour rejouer ce scénario historique du dépôt (moteur d\'origine).');
    card.innerHTML = `<h3>${scenario.nom}</h3><p>${scenario.description}</p>`;
    card.onclick = (ev) => runScenario(key, ev);
    grid.appendChild(card);
  });
}
function renderPresets(){
  const grid = document.getElementById('preset-grid');
  grid.innerHTML = '';
  Object.entries(CATALOGUE.parametres.presets).forEach(([key, preset]) => {
    const card = document.createElement('div');
    card.className = 'scenario-card carte';
    card.style.borderLeftColor = preset.couleur || '#38bdf8';
    card.setAttribute('data-aide', `<b>${preset.libelle}</b>${preset.description}`
      + '<br>Cliquez pour charger ces réglages dans la console : chacun reste ensuite ajustable au curseur.');
    card.innerHTML = `<h3>${preset.libelle}</h3><p>${preset.description}</p>`;
    card.onclick = (ev) => chargerPreset(key, ev);
    grid.appendChild(card);
  });
}
function chargerPreset(cle, ev){
  const preset = CATALOGUE.parametres.presets[cle];
  if (!preset) return;
  PARAMS = Object.assign({}, CATALOGUE.parametres.defauts, preset.parametres);
  // Les leviers du préréglage sont marqués comme modifiés : on voit d'un coup
  // d'œil ce que le programme change, et où il faut ajuster.
  LEVIERS_MODIFIES = new Set(Object.keys(preset.parametres).filter(nom =>
    Math.abs((preset.parametres[nom] || 0) - (CATALOGUE.parametres.defauts[nom] || 0)) > 1e-9));
  renderLeviers(filtreCourant());
  marquerCarteActive(ev, cle);
  simuler(true);
}
async function runScenario(scenario, ev){
  // Chemin « moteur d'origine » : les 9 scénarios du dépôt sont calculés par
  // les fabriques de scénarios, pas par le simulateur paramétrable. Le
  // bouton d'export reste celui de la dernière simulation paramétrique.
  const carte = ev?.target?.closest?.('.scenario-card')
    || document.querySelector(`.scenario-card[data-key="${scenario}"]`);
  if (carte) carte.classList.add('actif');
  const reponse = await fetch(`/api/run?scenario=${scenario}`);
  const donnees = await reponse.json();
  if (donnees.error){ alert('Erreur : ' + donnees.error); return; }
  afficherScenarioHistorique(donnees);
  activerExports();
}
function marquerCarteActive(ev, cle){
  document.querySelectorAll('.scenario-card').forEach(carte => carte.classList.remove('actif'));
  const carte = ev?.target?.closest?.('.scenario-card') || document.querySelector(`.scenario-card[data-key="${cle}"]`);
  if (carte) carte.classList.add('actif');
}
function afficherScenarioHistorique(donnees){
  const final = donnees.resultats[donnees.resultats.length - 1];
  document.getElementById('grid-impact').innerHTML = `
    <div class="carte metric"><div class="libelle">Scénario historique</div>
      <div class="valeur">${donnees.nom}</div>
      <div class="delta neutre">résultats du moteur d'origine (5 ans)</div></div>
    <div class="carte metric"><div class="libelle">Déficit année 5</div>
      <div class="valeur">${fmt(final.ratio_deficit_pib, 2)} % PIB</div>
      <div class="delta ${couleurDelta(-final.ratio_deficit_pib)}">dette ${fmt(final.ratio_dette_pib, 1)} % PIB</div></div>
    <div class="carte metric"><div class="libelle">OAT 10 ans</div>
      <div class="valeur">${fmt(final.taux_oat_pct, 2)} %</div>
      <div class="delta neutre">spread ${fmt(final.spread_bund_bps, 0)} bps</div></div>
    <div class="carte metric"><div class="libelle">Tension sociale</div>
      <div class="valeur">${fmt(final.tension_sociale_locale, 1)}/100</div>
      <div class="delta neutre">confiance ${fmt(final.confiance_democratique, 1)}/100</div></div>`;
  renderTableau(donnees.resultats);
  document.getElementById('badge-leviers').textContent =
    `scénario « ${donnees.nom} » — 5 exercices simulés`;
  activerExports();
}

/* ── Simulation paramétrique ────────────────────────────────────────────── */
async function simuler(avecImpacts){
  const bouton = document.getElementById('btn-simuler');
  bouton.disabled = true;
  const parametresEnvoyes = Object.assign({}, PARAMS);
  try {
    const reponse = await fetch('/api/simuler', {
      method:'POST', headers:{'Content-Type':'application/json'},
      body: JSON.stringify({parametres: parametresEnvoyes, avec_impacts: !!avecImpacts, max_impacts: 16})
    });
    const donnees = await reponse.json();
    if (donnees.error){ alert('Erreur de simulation : ' + donnees.error); return; }
    SORTIE = donnees;
    renderImpact(donnees);
    renderStrates(donnees);
    renderTableau(donnees.etapes);
    renderGraphique(donnees.etapes);
    renderDomaines(donnees);
    renderMatrice(donnees);
    renderJournal(donnees);
    renderAlertes(donnees);
    renderConsole(donnees);
    renderDerniereModification(SIMULATION_PRECEDENTE,
                               {parametres: parametresEnvoyes, sortie: donnees});
    majEffetsParLevier(donnees, SIMULATION_PRECEDENTE, parametresEnvoyes);
    SIMULATION_PRECEDENTE = {parametres: parametresEnvoyes, sortie: donnees};
    // La grille est reconstruite avec ses puces d'impact — sauf pendant qu'un
    // curseur est manipulé, pour ne pas le remplacer sous les doigts.
    if (!REGLAGE_EN_COURS) renderLeviers(filtreCourant());
    document.getElementById('badge-leviers').textContent =
      `${nombreLeviersActifs()} leviers actifs · score moyen ${fmt(donnees.synthese.score_moyen_domaines,1)} (référence ${fmt(donnees.synthese.score_moyen_reference,1)})`;
    activerExports();
  } catch (erreur){
    alert('Le serveur n\'a pas répondu : ' + erreur);
  } finally {
    bouton.disabled = false;
  }
}
function renderAlertes(donnees){
  const alertes = (donnees.avertissements || []).map(texte => `<div class="alerte">${texte}</div>`).join('');
  document.getElementById('zone-alertes').innerHTML = alertes;
}


/* ── Console de veille permanente ───────────────────────────────────────── */
function classeNiveau(niveau){ return 'niveau-' + (niveau || 'inconnu'); }
function etiquetteNiveau(niveau){ return LIBELLES_NIVEAUX[niveau] || niveau || 'non mesuré'; }

function renderConsole(donnees){
  const diagnostic = donnees.diagnostic;
  const verdictBoite = document.getElementById('console-verdict');
  const bloc = document.getElementById('console-pilotage');
  if (!diagnostic){
    bloc.className = 'bloc console';
    verdictBoite.className = 'console-verdict';
    verdictBoite.textContent = 'Diagnostic indisponible (serveur antérieur ?).';
    return;
  }
  const verdict = diagnostic.verdict || {};
  bloc.className = 'bloc console ' + classeNiveau(diagnostic.niveau_global);
  verdictBoite.className = 'console-verdict ' + classeNiveau(diagnostic.niveau_global);
  verdictBoite.textContent = `${etiquetteNiveau(diagnostic.niveau_global).toUpperCase()} — ${verdict.message || ''}`;

  // Ruban collant : la même information en une ligne, pour que les leviers
  // restent visibles et cliquables pendant tout le réglage.
  const ruban = document.getElementById('ruban-veille');
  if (ruban){
    ruban.className = 'ruban-veille ' + classeNiveau(diagnostic.niveau_global);
    document.getElementById('ruban-verdict').textContent =
      `${etiquetteNiveau(diagnostic.niveau_global).toUpperCase()} · ${verdict.nombre_alertes || 0} alerte(s)`
      + (verdict.nombre_hors_sol ? ` · ${verdict.nombre_hors_sol} HORS-SOL` : '');
    document.getElementById('ruban-strates').innerHTML = (diagnostic.strates || []).map(strate =>
      `<span class="ruban-strate ${classeNiveau(strate.niveau)}"
             data-aide="<b>${strate.libelle}</b>${etiquetteNiveau(strate.niveau)} — ${strate.alertes.length} seuil(s) en alerte. Cliquez sur « détails » pour le détail des seuils.">S${strate.strate}</span>`
    ).join('');
    const risque = (diagnostic.population || {}).valeur;
    document.getElementById('ruban-population').innerHTML =
      `risque population <b class="${classeNiveau((diagnostic.population || {}).niveau)}">${fmt(risque, 0)}/100</b>`;
  }

  // Bandeau d'alerte rouge : ce qui est déjà hors-sol.
  const horsSol = (diagnostic.indicateurs || []).filter(ind => ind.niveau === 'hors_sol');
  document.getElementById('console-danger').innerHTML = horsSol.length
    ? `<div class="bandeau-hors-sol"><b>⚠ HORS-SOL (${horsSol.length}) — la population ou l'État est exposé :</b><br>`
      + horsSol.map(ind => `${ind.libelle} : ${ind.valeur_texte} ${ind.unite} — strate ${ind.strate}`).join('<br>')
      + '</div>'
    : '';

  // Les cinq strates, du local au géopolitique.
  document.getElementById('console-strates').innerHTML = (diagnostic.strates || []).map(strate =>
    `<div class="strate-puce ${classeNiveau(strate.niveau)}">
       <b>${strate.libelle}</b>
       <span class="${classeNiveau(strate.niveau)}">${etiquetteNiveau(strate.niveau)}</span>
       <div class="aide">${strate.alertes.length} seuil(s) en alerte sur ${strate.indicateurs.length}</div>
     </div>`).join('');

  // Risque pour la population : jauge + piliers + consigne.
  const population = diagnostic.population || {};
  const risque = Number(population.valeur || 0);
  const couleur = risque <= 50 ? 'var(--vert)' : (risque <= 58 ? 'var(--ambre)'
    : (risque <= 68 ? '#fb923c' : 'var(--rouge)'));
  const piliers = (population.piliers || []).map(pilier => {
    const ecart = pilier.score - 50;
    return `<span class="delta ${couleurDelta(ecart)}">${pilier.cle.replace(/_/g,' ')} ${fmt(pilier.score,0)}</span>`;
  }).join(' · ');
  document.getElementById('console-population').innerHTML =
    `<div class="ligne-marge"><span>Indice de risque (0 = aucun, 100 = maximal)</span>
       <span class="droite ${classeNiveau(population.niveau)}">${fmt(risque,1)}/100 — ${etiquetteNiveau(population.niveau)}</span></div>
     <div class="jauge"><span style="width:${Math.max(2, Math.min(100, risque))}%;background:${couleur}"></span></div>
     <div class="graduations"><span>0</span><span>50 vigilance</span><span>58 risque</span><span>68 hors-sol</span><span>100</span></div>
     <div class="message-seuil ${classeNiveau(population.niveau)}"><p>${population.message || ''}</p></div>
     <div class="aide">Domaines suivis : ${piliers}</div>`;

  // Messages de seuil, du plus grave au plus doux.
  const alertes = (diagnostic.alertes || []);
  document.getElementById('console-alertes').innerHTML = alertes.length
    ? alertes.slice(0, 8).map(alerte =>
        `<div class="message-seuil ${classeNiveau(alerte.niveau)}">
           <div class="tete"><span>${alerte.libelle} · strate ${alerte.strate}</span>
             <span class="etiquette ${classeNiveau(alerte.niveau)}">${etiquetteNiveau(alerte.niveau)}</span></div>
           <p>${alerte.message}</p>
           ${alerte.source ? `<span class="source">Seuil : ${alerte.source}</span>` : ''}
         </div>`).join('')
    : '<div class="message-seuil"><p>Aucun seuil franchi : tous les garde-fous sont respectés.</p></div>';

  // Marges de manœuvre (ce qu'il reste avant le prochain seuil) et audaces.
  const marges = (diagnostic.marges || []).slice(0, 6).map(marge =>
    `<div class="ligne-marge"><span>${marge.libelle}</span>
       <span class="droite">${marge.valeur_texte} ${marge.unite} ·
         <b class="${classeNiveau(marge.prochain_niveau)}">${fmt(marge.marge, 2)} ${marge.unite}</b>
         avant « ${etiquetteNiveau(marge.prochain_niveau)} »</span></div>`).join('');
  const progres = (diagnostic.progres || []).slice(0, 4).map(progres =>
    `<div class="ligne-marge"><span>${progres.libelle}</span>
       <span class="droite">encore <b>${fmt(progres.ecart, 2)}</b> ${progres.unite} possibles avant ${progres.valeur_cible}</span></div>
     <div class="aide" style="margin:-2px 0 6px">${progres.message_cible || ''}</div>`).join('');
  document.getElementById('console-marges').innerHTML =
    (marges || '<div class="ligne-marge"><span>Aucune marge mesurable.</span></div>')
    + (progres ? `<h3 class="console-titre">Ce que vous pouvez encore oser</h3>${progres}` : '');
}

function majEffetsParLevier(donnees, precedente, parametresEnvoyes){
  const puces = {};
  const modifies = new Set();
  if (precedente){
    Object.keys(parametresEnvoyes).forEach(cle => {
      if (Math.abs((parametresEnvoyes[cle] || 0) - (precedente.parametres[cle] || 0)) > 1e-9){
        modifies.add(cle);
      }
    });
    // Un seul levier touché : la variation de chaque domaine lui est
    // directement imputable, on peut donc la chiffrer sous son curseur.
    if (modifies.size === 1){
      const cle = [...modifies][0];
      const avantScores = {};
      (precedente.sortie.domaines || []).forEach(domaine => { avantScores[domaine.cle] = domaine.score; });
      const effets = (donnees.domaines || [])
        .map(domaine => ({libelle: domaine.libelle,
                          effet_score: domaine.score - (avantScores[domaine.cle] === undefined
                            ? 50 : avantScores[domaine.cle])}))
        .filter(effet => Math.abs(effet.effet_score) >= 0.1)
        .sort((a, b) => Math.abs(b.effet_score) - Math.abs(a.effet_score))
        .slice(0, 3);
      if (effets.length) puces[cle] = effets;
    }
  }
  // « Simuler avec impacts croisés » : le modèle fournit l'effet marginal de
  // chaque levier actif, domaine par domaine — on l'affiche sous le curseur.
  (donnees.impacts || []).forEach(impact => {
    const effets = (impact.effets || [])
      .filter(effet => Math.abs(effet.effet_score) >= 0.1)
      .sort((a, b) => Math.abs(b.effet_score) - Math.abs(a.effet_score))
      .slice(0, 3)
      .map(effet => ({libelle: effet.libelle, effet_score: effet.effet_score}));
    if (effets.length){
      puces[impact.levier] = effets;
      modifies.add(impact.levier);
    }
  });
  DERNIERES_PUCES = puces;
  LEVIERS_MODIFIES = modifies;
}

function renderDerniereModification(avant, apres){
  const zone = document.getElementById('console-derniere-modification');
  if (!avant || !apres){ zone.innerHTML = '<div class="aide">Chargez un préréglage ou bougez un curseur pour voir l\'effet d\'une mesure.</div>'; return; }
  const defauts = (CATALOGUE && CATALOGUE.parametres.defauts) || {};
  const leviers = Object.keys(apres.parametres).filter(cle =>
    Math.abs((apres.parametres[cle] || 0) - (avant.parametres[cle] || 0)) > 1e-9);
  const libelles = leviers.slice(0, 4).map(cle => {
    const levier = CATALOGUE.parametres.familles.flatMap(f => f.leviers).find(l => l.cle === cle);
    const valeur = apres.parametres[cle];
    const texte = (levier && levier.type === 'interrupteur')
      ? (valeur >= 0.5 ? 'activé' : 'désactivé')
      : `${fmt(valeur, levier ? levier.precision : 2)} ${levier && levier.unite !== 'bool' ? levier.unite : ''}`;
    const retour = defauts[cle] !== undefined && Math.abs(valeur - defauts[cle]) < 1e-9 ? ' (retour au neutre)' : '';
    return `${levier ? levier.libelle : cle} → ${texte}${retour}`;
  });
  const effets = [];
  EFFETS_SURVEILLES.forEach(([cle, libelle, sens, precision]) => {
    const a = avant.sortie.synthese[cle], b = apres.sortie.synthese[cle];
    if (a === undefined || b === undefined) return;
    const delta = b - a;
    if (Math.abs(delta) < Math.pow(10, -precision) / 2) return;
    const favorable = sens * delta > 0;
    effets.push({libelle: libelle, avant: a, apres: b, delta: delta,
                 sens: sens, precision: precision, favorable: favorable});
  });
  // Un domaine qui décroche est plus parlant qu'un agrégat : on signale le pire.
  let pireDomaine = null;
  const domainesAvant = {};
  (avant.sortie.domaines || []).forEach(d => { domainesAvant[d.cle] = d.score; });
  (apres.sortie.domaines || []).forEach(d => {
    const avantScore = domainesAvant[d.cle];
    if (avantScore === undefined) return;
    const delta = d.score - avantScore;
    if (Math.abs(delta) < 0.15) return;
    if (!pireDomaine || delta < pireDomaine.delta) pireDomaine = {libelle: d.libelle, delta: delta};
  });
  const favorables = effets.filter(e => e.favorable).length;
  const defavorables = effets.length - favorables;
  const verdict = effets.length === 0
    ? 'aucun effet mesurable sur les grandeurs surveillées'
    : (defavorables === 0 ? 'jugée favorable'
      : (favorables === 0 ? 'jugée défavorable' : `${favorables} effet(s) favorable(s), ${defavorables} défavorable(s)`));
  const niveauVerdict = effets.length === 0 ? 'inconnu'
    : (defavorables === 0 ? 'favorable' : (favorables === 0 ? 'risque' : 'vigilance'));

  zone.innerHTML =
    `<div class="message-seuil ${classeNiveau(niveauVerdict)}">
       <div class="tete"><span>${leviers.length ? leviers.length + ' levier(s) modifié(s)' : 'Aucun levier modifié'}</span>
         <span class="etiquette ${classeNiveau(niveauVerdict)}">${verdict}</span></div>
       ${libelles.length ? `<p>${libelles.join(' · ')}${leviers.length > libelles.length ? ` (+${leviers.length - libelles.length} autre(s))` : ''}</p>` : ''}
     </div>`
    + effets.map(effet =>
        `<div class="delta-mesure"><span>${effet.libelle} : ${fmt(effet.avant, effet.precision)} → ${fmt(effet.apres, effet.precision)}</span>
           <span class="valeur ${effet.favorable ? 'delta hausse' : 'delta baisse'}">
             ${effet.delta > 0 ? '+' : ''}${fmt(effet.delta, effet.precision)} ${effet.favorable ? '✓' : '✗'}</span></div>`).join('')
    + (pireDomaine ? `<div class="aide">Domaine le plus touché : <b>${pireDomaine.libelle}</b>
         (${pireDomaine.delta > 0 ? '+' : ''}${fmt(pireDomaine.delta, 1)} pt de score).</div>` : '');
}

function renderImpact(donnees){
  const s = donnees.synthese;
  const cartes = [
    ['Recettes nouvelles (an 5)', fmt(s.recettes_nouvelles_mde, 1) + ' Md€', 'mesures activées'],
    ['Dépenses nouvelles (an 5)', fmt(s.depenses_nouvelles_mde, 1) + ' Md€', 'mesures activées'],
    ['Solde des mesures', fmt(s.solde_mesures_mde, 1) + ' Md€',
      s.solde_mesures_mde >= 0 ? 'excédent de mesures' : 'coût net des mesures'],
    ['Déficit final', fmt(s.deficit_final_pct, 2) + ' % PIB',
      `référence ${fmt(s.deficit_reference_pct, 2)} % (écart ${fmt(s.deficit_ecart_pts, 2)} pt)`],
    ['Dette finale', fmt(s.dette_finale_pct, 1) + ' % PIB',
      `référence ${fmt(s.dette_reference_pct, 1)} %`],
    ['OAT 10 ans', fmt(s.taux_oat_final, 2) + ' %',
      `spread ${fmt(s.spread_final_bps, 0)} bps · note ${s.note_souveraine}`],
    ['Tension sociale', fmt(s.tension_finale, 1) + '/100',
      `confiance ${fmt(s.confiance_finale, 1)}/100`],
    ['Risque de censure', fmt(s.risque_censure_final_pct, 0) + ' %',
      s.statut_pde ? 'PDE active' : 'PDE : conforme'],
    ['Croissance cumulée', (s.croissance_supplementaire_pts >= 0 ? '+' : '') + fmt(s.croissance_supplementaire_pts, 2) + ' %',
      'PIB année 5 vs référence'],
    ['Domaines en hausse', String(s.nombre_domaines_en_hausse), `${s.nombre_domaines_en_baisse} en baisse`],
  ];
  document.getElementById('grid-impact').innerHTML = cartes.map(([libelle, valeur, sous]) =>
    `<div class="carte metric"><div class="libelle">${libelle}</div><div class="valeur">${valeur}</div>
      <div class="delta neutre">${sous}</div></div>`).join('');
}
function renderStrates(donnees){
  const dernier = donnees.etapes[donnees.etapes.length - 1];
  const strates = [
    ['Échelon 1 — Local', '#22c55e', [
      ['Tension sociale', fmt(dernier.tension_sociale_locale,1)+'/100'],
      ['Services de proximité', fmt(dernier.qualite_services_proximite,1)+'/100'],
      ['Taxe foncière', fmt(dernier.produit_taxe_fonciere_mde,1)+' Md€']]],
    ['Échelon 2 — National', '#38bdf8', [
      ['PIB', fmt(dernier.pib_nominal_mde,0)+' Md€'],
      ['Déficit', fmt(dernier.ratio_deficit_pib,2)+' % PIB'],
      ['Dette', fmt(dernier.ratio_dette_pib,1)+' % PIB'],
      ['Charge dette', fmt(dernier.charge_dette_mde,1)+' Md€'],
      ['Censure', fmt(dernier.risque_censure_parlement,0)+' %']]],
    ['Échelon 3 — Européen', '#a855f7', [
      ['PDE', dernier.statut_pde_europe ? 'ACTIVE' : 'conforme'],
      ['Bouclier TPI', dernier.bouclier_tpi_actif ? 'éligible' : 'suspendu']]],
    ['Échelon 4 — Mondial', '#f59e0b', [
      ['OAT 10 ans', fmt(dernier.taux_oat_pct,2)+' %'],
      ['Spread Bund', fmt(dernier.spread_bund_bps,0)+' bps'],
      ['Note', dernier.note_souveraine],
      ['Brent', fmt(dernier.cours_petrole_usd,1)+' $'],
      ['Inflation', fmt(dernier.inflation_globale_pct,2)+' %']]],
    ['Échelon 5 — Géopolitique', '#ef4444', [
      ['Tension géo', fmt(dernier.indice_tension_geopolitique,1)+'/100'],
      ['Chokepoints', dernier.chokepoints_sous_tension+'/7'],
      ['Défense', fmt(dernier.effort_defense_pct_pib,2)+' % PIB'],
      ['Semi-conducteurs', fmt(dernier.disponibilite_semiconducteurs_pct,0)+' %']]],
  ];
  document.getElementById('strates-cascade').innerHTML = strates.map(([titre, couleur, valeurs]) =>
    `<div class="strate" style="border-left-color:${couleur}">
       <span class="titre">${titre}</span>
       <span class="valeurs">${valeurs.map(([k,v]) => `<span>${k} : <b>${v}</b></span>`).join('')}</span>
     </div>`).join('');
}
function renderTableau(etapes){
  const colonnes = [
    ['annee','Année'],['pib_nominal_mde','PIB (Md€)'],['ratio_deficit_pib','Déficit (% PIB)'],
    ['ratio_dette_pib','Dette (% PIB)'],['charge_dette_mde','Charge dette (Md€)'],
    ['taux_oat_pct','OAT (%)'],['spread_bund_bps','Spread (bps)'],['note_souveraine','Note'],
    ['tension_sociale_locale','Tension'],['confiance_democratique','Confiance'],
    ['risque_censure_parlement','Censure (%)'],['effort_defense_pct_pib','Défense (% PIB)'],
    ['cours_petrole_usd','Brent ($)'],['inflation_globale_pct','Inflation (%)'],
    ['pouvoir_achat_index','Pouvoir achat'],['qualite_services_proximite','Services']
  ];
  const entete = colonnes.map(([, libelle]) => `<th>${libelle}</th>`).join('');
  const lignes = etapes.map(etape => `<tr>${colonnes.map(([cle]) =>
    `<td>${typeof etape[cle] === 'number' ? fmt(etape[cle], 2) : (etape[cle] ?? '—')}</td>`).join('')}</tr>`).join('');
  document.getElementById('results-table').innerHTML = `<thead><tr>${entete}</tr></thead><tbody>${lignes}</tbody>`;
}
function renderGraphique(etapes){
  const series = [
    ['Déficit (% PIB)','ratio_deficit_pib','#ef4444'],
    ['Dette (% PIB)','ratio_dette_pib','#f59e0b'],
    ['OAT (%)','taux_oat_pct','#38bdf8'],
    ['Tension','tension_sociale_locale','#a855f7'],
    ['Confiance','confiance_democratique','#22c55e'],
  ];
  const largeur = 900, hauteur = 210, marge = 30;
  const toutes = series.flatMap(([, cle]) => etapes.map(e => e[cle]));
  const maxi = Math.max(...toutes, 1), mini = Math.min(...toutes, 0);
  const x = index => marge + index * ((largeur - 2*marge) / Math.max(etapes.length - 1, 1));
  const y = valeur => hauteur - marge - ((valeur - mini) / Math.max(maxi - mini, 1)) * (hauteur - 2*marge);
  let svg = `<line x1="${marge}" y1="${hauteur-marge}" x2="${largeur-marge}" y2="${hauteur-marge}" stroke="#26324d"/>`;
  series.forEach(([libelle, cle, couleur]) => {
    const points = etapes.map((e, i) => `${x(i)},${y(e[cle])}`).join(' ');
    svg += `<polyline points="${points}" fill="none" stroke="${couleur}" stroke-width="2.5"/>`;
    etapes.forEach((e, i) => { svg += `<circle cx="${x(i)}" cy="${y(e[cle])}" r="3" fill="${couleur}"/>`; });
    svg += `<text x="${marge}" y="${18 + series.findIndex(s => s[1] === cle) * 15}" fill="${couleur}" font-size="12">${libelle}</text>`;
  });
  etapes.forEach((e, i) => {
    svg += `<text x="${x(i)}" y="${hauteur-10}" fill="#93a3bd" font-size="11" text-anchor="middle">Année ${e.annee}</text>`;
  });
  document.getElementById('svg-chart').innerHTML = svg;
}
function renderDomaines(donnees){
  document.getElementById('domaines-grille').innerHTML = donnees.domaines.map(domaine => {
    const ecart = domaine.score - domaine.score_reference;
    const deltaClasse = couleurDelta(ecart);
    const indicateurs = domaine.indicateurs.map(indicateur => {
      const variation = indicateur.variation_relative_pct;
      const favorable = indicateur.sens * variation >= 0;
      return `<li><span class="indic">${indicateur.libelle}</span>
        <span>${fmt(indicateur.valeur_finale, 1)} ${indicateur.unite}
        <span class="delta ${favorable ? 'hausse' : 'baisse'}">(${variation >= 0 ? '+' : ''}${fmt(variation,1)} %)</span></span></li>`;
    }).join('');
    const texteAide = `<b>${domaine.libelle}</b>${domaine.description}<br>`
      + `score ${fmt(domaine.score, 1)}/100 — écart à la référence ${ecart >= 0 ? '+' : ''}${fmt(ecart, 1)} pt `
      + `(50 = aucune politique ; « sans politique » = tendance spontanée du modèle).<br>`
      + `${domaine.indicateurs.length} indicateur(s) chiffré(s), chacun avec sa source.`;
    return `<div class="domaine" data-aide="${texteAide}" style="border-top:3px solid ${domaine.couleur}">
      <div class="tete">
        <div><b>${domaine.libelle}</b><div class="ref">${domaine.description}</div></div>
        <div style="text-align:right">
          <div class="score" style="color:${domaine.couleur}">${fmt(domaine.score, 1)}</div>
          <div class="ref delta ${deltaClasse}">écart à la référence : ${ecart >= 0 ? '+' : ''}${fmt(ecart, 1)} pt</div>
          <div class="ref">sans politique : ${domaine.tendance_reference === null || domaine.tendance_reference === undefined ? '—' : fmt(domaine.tendance_reference, 1)}</div>
        </div>
      </div>
      <ul>${indicateurs}</ul>
    </div>`;
  }).join('');
}
function renderMatrice(donnees){
  const impacts = donnees.impacts || [];
  if (!impacts.length){
    document.getElementById('matrice-impacts').innerHTML =
      '<tbody><tr><td>Aucun levier actif : activez des leviers puis lancez « Simuler avec impacts croisés ».</td></tr></tbody>';
    return;
  }
  const domaines = donnees.domaines.map(d => d.cle);
  const libelles = donnees.domaines.map(d => d.libelle.split(' ')[0]);
  let html = '<thead><tr><th>Levier actif</th>' + libelles.map(l => `<th>${l}</th>`).join('') + '</tr></thead><tbody>';
  impacts.forEach(impact => {
    const effets = {};
    impact.effets.forEach(effet => { effets[effet.domaine] = effet.effet_score; });
    const cellules = domaines.map(cle => {
      const valeur = effets[cle];
      if (valeur === undefined) return '<td class="vide">·</td>';
      const classe = valeur > 0 ? 'pos' : 'neg';
      return `<td class="${classe}">${valeur > 0 ? '+' : ''}${fmt(valeur, 1)}</td>`;
    }).join('');
    html += `<tr><td>${impact.libelle}</td>${cellules}</tr>`;
  });
  document.getElementById('matrice-impacts').innerHTML = html + '</tbody>';
}
function renderJournal(donnees){
  const lignes = (donnees.journal || []).map(texte => `<div>${texte}</div>`).join('');
  document.getElementById('journal').innerHTML = lignes || '<div>Journal vide.</div>';
}

/* ── Actions ────────────────────────────────────────────────────────────── */
function reinitialiser(){
  PARAMS = Object.assign({}, CATALOGUE.parametres.defauts);
  DERNIERES_PUCES = {};
  LEVIERS_MODIFIES = new Set();
  renderLeviers(filtreCourant());
  simuler(false);
}
function activerExports(){
  document.getElementById('btn-export-json').disabled = false;
  document.getElementById('btn-export-csv').disabled = false;
}
function exporter(format){
  if (!SORTIE) return;
  if (format === 'json'){
    telecharger(JSON.stringify(SORTIE, null, 2), 'simulation_parametrique.json', 'application/json');
    return;
  }
  const etapes = SORTIE.etapes;
  const colonnes = Object.keys(etapes[0]);
  const lignes = [colonnes.join(';')].concat(etapes.map(etape =>
    colonnes.map(cle => {
      const valeur = etape[cle];
      if (Array.isArray(valeur)) return '"' + valeur.join(' | ').replace(/"/g,'') + '"';
      if (typeof valeur === 'object' && valeur !== null) return '"' + JSON.stringify(valeur).replace(/"/g,'') + '"';
      return String(valeur).replace(';', ',');
    }).join(';')));
  telecharger(lignes.join('\n'), 'simulation_parametrique.csv', 'text/csv');
}
function telecharger(contenu, nom, type){
  const lien = document.createElement('a');
  lien.href = URL.createObjectURL(new Blob([contenu], {type: type + ';charset=utf-8'}));
  lien.download = nom;
  lien.click();
}

/* ── Démarrage ──────────────────────────────────────────────────────────── */
(async function demarrer(){
  await chargerCatalogue();
  initialiserInfobulles();
  renderScenarios();
  await chargerContexte(false);
  chargerPreset('mandature', null);
  activerExports();
})();
</script>
</body>
</html>
"""
