#!/usr/bin/env node
'use strict';

/**
 * Balayage d'accessibilité automatisé (axe-core) sur le site servi localement.
 *
 * Ce script ne remplace ni un audit d'accessibilité, ni une conformité RGAA ou
 * WCAG, ni une revue par une personne experte, ni un essai avec un lecteur
 * d'écran. Il détecte seulement ce qu'axe-core sait tester, dans Chromium, sur
 * les états qu'il visite.
 *
 * Dépendances temporaires, hors dépôt :
 *   npm install --prefix /tmp/mrsc-browser --no-audit --no-fund \
 *     puppeteer-core@25.13.0 @sparticuz/chromium@153.0.0
 *   npm install --prefix /tmp/mrsc-a11y --no-audit --no-fund axe-core@4.14.0
 *
 * Usage :
 *   MRSC_BROWSER_NODE_MODULES=/tmp/mrsc-browser/node_modules \
 *   MRSC_AXE_NODE_MODULES=/tmp/mrsc-a11y/node_modules \
 *   node outils/verifier-accessibilite.cjs
 *
 * Options :
 *   --etendu          balaie toutes les pages HTML du dépôt aux deux largeurs
 *   --rapport <chemin> écrit le détail JSON des résultats
 *
 * Aucun réseau : le site est servi par `outils/serveur-local.py` sur la boucle
 * locale, avec le moteur désactivé.
 */

const { spawn } = require('node:child_process');
const path = require('node:path');
const fs = require('node:fs');
const Module = require('node:module');

function ajouterModules(variable, defaut) {
  const valeur = process.env[variable] || defaut;
  if (!valeur) return;
  process.env.NODE_PATH = [valeur, process.env.NODE_PATH].filter(Boolean).join(path.delimiter);
  Module._initPaths();
}

ajouterModules('MRSC_BROWSER_NODE_MODULES', '');
ajouterModules('MRSC_AXE_NODE_MODULES', '/tmp/mrsc-a11y/node_modules');

let puppeteer;
let chromiumPackage;
let chromium;
try {
  puppeteer = require('puppeteer-core');
  chromiumPackage = require('@sparticuz/chromium');
  chromium = chromiumPackage.default;
} catch (error) {
  console.error(
    'Dépendances navigateur absentes. Installer hors du dépôt :\n'
    + '  npm install --prefix /tmp/mrsc-browser --no-audit --no-fund puppeteer-core@25.13.0 @sparticuz/chromium@153.0.0\n'
    + '  MRSC_BROWSER_NODE_MODULES=/tmp/mrsc-browser/node_modules node outils/verifier-accessibilite.cjs'
  );
  process.exit(2);
}

let axeSource;
try {
  const axePath = require.resolve('axe-core/axe.min.js');
  axeSource = fs.readFileSync(axePath, 'utf8');
} catch (error) {
  console.error(
    'axe-core absent. Installer hors du dépôt :\n'
    + '  npm install --prefix /tmp/mrsc-a11y --no-audit --no-fund axe-core@4.14.0\n'
    + '  MRSC_AXE_NODE_MODULES=/tmp/mrsc-a11y/node_modules node outils/verifier-accessibilite.cjs'
  );
  process.exit(2);
}

const ROOT = path.resolve(__dirname, '..');
const PORT = Number(process.env.MRSC_A11Y_PORT || 4176);
const ETENDU = process.argv.includes('--etendu');
const RAPPORT = (() => {
  const index = process.argv.indexOf('--rapport');
  return index > -1 ? process.argv[index + 1] : null;
})();

const PAGES = [
  ['index.html', 'Accueil'],
  ['apprendre.html', 'Apprendre'],
  ['apprendre/fiches/civ-verifier-information.html', 'Fiche vérifier une information'],
  ['anglais-aventure.html', 'Les Mondes'],
  ['transparence.html', 'Transparence'],
  ['simulateur.html', 'Simulateur (présentation)'],
  ['simulateur/index.html', 'Simulateur (copie locale)'],
  ['eva.html', 'ÉVA'],
  ['documents.html', 'Documents'],
  ['ia-societe.html', 'IA & société'],
  ['confidentialite.html', 'Confidentialité'],
  ['404.html', 'Page introuvable'],
];

function attendre(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

async function analyser(page) {
  await page.evaluate(axeSource);
  return page.evaluate(async () => {
    const resultat = await axe.run(document, { resultTypes: ['violations'] });
    return resultat.violations.map((violation) => ({
      id: violation.id,
      impact: violation.impact,
      help: violation.help,
      nodes: violation.nodes.slice(0, 5).map((noeud) => ({
        target: noeud.target.join(' '),
        summary: (noeud.failureSummary || '').split('\n').slice(0, 3).join(' | '),
      })),
      nombre: violation.nodes.length,
    }));
  });
}

function resume(violations) {
  return violations.map((v) => `${v.id} (${v.nombre} nœud${v.nombre > 1 ? 's' : ''})`).join(', ');
}

async function ouvrir(browser, largeur, chemin) {
  const page = await browser.newPage();
  await page.setViewport({ width: largeur, height: 900 });
  const url = `http://127.0.0.1:${PORT}/${chemin}`;
  if (chemin === 'simulateur.html') {
    // Cette page conserve une iframe et des appels asynchrones : `networkidle0`
    // n'est pas garanti, on laisse simplement les scripts se terminer.
    await page.goto(url, { waitUntil: 'load', timeout: 60000 });
    await attendre(5000);
    return page;
  }
  await page.goto(url, { waitUntil: 'networkidle0', timeout: 30000 });
  return page;
}

function parcourir(dossier, prefixe = '') {
  const entrees = [];
  for (const nom of fs.readdirSync(dossier)) {
    if (nom === '.git' || nom === 'node_modules') continue;
    const chemin = path.join(dossier, nom);
    if (fs.statSync(chemin).isDirectory()) {
      entrees.push(...parcourir(chemin, `${prefixe}${nom}/`));
    } else if (nom.endsWith('.html')) {
      entrees.push(`${prefixe}${nom}`);
    }
  }
  return entrees;
}

function pagesEtendues() {
  return parcourir(ROOT).sort().map((entree) => [entree, entree]);
}

async function main() {
  const serveur = spawn(
    'python3',
    ['outils/serveur-local.py', '--port', String(PORT), '--sans-moteur', '--bind', '127.0.0.1'],
    { cwd: ROOT, stdio: 'ignore' }
  );
  await attendre(1500);

  const packDir = path.resolve(path.dirname(require.resolve('@sparticuz/chromium')), '..');
  const libs = await chromiumPackage.inflate(path.join(packDir, 'bin', 'al2023.tar.br'));
  chromiumPackage.setupLambdaEnvironment(path.join(libs, 'lib'));
  const browser = await puppeteer.launch({
    args: chromium.args,
    executablePath: await chromium.executablePath(),
    headless: true,
  });

  const resultats = {};
  const echecs = [];

  const enregistrer = (cle, violations) => {
    resultats[cle] = violations;
    if (violations.length) {
      echecs.push(cle);
      console.log(`\n=== ${cle} : ${violations.length} règle(s) en échec`);
      for (const v of violations) {
        console.log(`  [${v.impact}] ${v.id} — ${v.help}`);
        for (const n of v.nodes) console.log(`      ${n.target}\n      ${n.summary}`);
      }
    } else {
      console.log(`OK — ${cle}`);
    }
  };

  const pages = ETENDU ? pagesEtendues() : PAGES;
  for (const [chemin, libelle] of pages) {
    for (const largeur of [360, 1280]) {
      const page = await ouvrir(browser, largeur, chemin);
      const violations = await analyser(page);
      enregistrer(`${libelle} @${largeur}`, violations);
      await page.close();
    }
  }

  // États interactifs : sans les ouvrir, le balayage de la page au repos
  // manquerait les panneaux masqués et les composants construits au clic.
  if (!ETENDU) {
    for (const largeur of [360, 1280]) {
      const page = await ouvrir(browser, largeur, 'index.html');
      if (largeur === 360) {
        await page.click('[data-menu-toggle]').catch(() => {});
        await attendre(350);
        enregistrer(`Accueil, menu ouvert @${largeur}`, await analyser(page));
        await page.click('[data-menu-toggle]').catch(() => {});
        await attendre(250);
      }
      await page.evaluate(() => {
        const details = document.querySelector('[data-display-settings]');
        if (details) details.open = true;
      });
      await attendre(250);
      enregistrer(`Accueil, panneau Affichage ouvert @${largeur}`, await analyser(page));
      await page.close();

      const apprendre = await ouvrir(browser, largeur, 'apprendre.html');
      await apprendre.select('#learning-level-filter', '2').catch(() => {});
      await apprendre.type('#learning-search', 'carte').catch(() => {});
      await attendre(400);
      enregistrer(`Apprendre, filtre actif @${largeur}`, await analyser(apprendre));
      await apprendre.close();

      const mondes = await ouvrir(browser, largeur, 'anglais-aventure.html');
      await mondes.click('[data-mission-id="gare"]');
      await attendre(600);
      enregistrer(`Mondes, mission ouverte @${largeur}`, await analyser(mondes));
      await mondes.evaluate(() => {
        const retour = document.querySelector('[data-return-map], #back-to-map, [data-action="retour-carte"]');
        if (retour) retour.click();
      });
      await attendre(400);
      await mondes.evaluate(() => document.querySelector('[data-world-id]')?.click());
      await attendre(500);
      enregistrer(`Mondes, filtre par monde @${largeur}`, await analyser(mondes));
      await mondes.close();

      const simulateur = await ouvrir(browser, largeur, 'simulateur/index.html');
      await simulateur.evaluate(() => {
        const commandes = document.querySelector('#mrsc-display-controls');
        if (commandes) commandes.hidden = false;
      });
      await attendre(250);
      enregistrer(`Simulateur, commandes visibles @${largeur}`, await analyser(simulateur));
      await simulateur.evaluate(() => document.querySelector('[data-sim-text-increase]')?.click());
      await attendre(300);
      enregistrer(`Simulateur, texte agrandi @${largeur}`, await analyser(simulateur));
      await simulateur.close();
    }
  }

  if (RAPPORT) {
    fs.writeFileSync(path.resolve(RAPPORT), JSON.stringify(resultats, null, 1));
  }

  const total = Object.keys(resultats).length;
  console.log(
    `\n${total} exécution${total > 1 ? 's' : ''}, ${echecs.length} avec violation.`
  );
  if (echecs.length) {
    console.log('Réessayer après correction, puis consigner la mesure sans la présenter comme un audit.');
  }

  await browser.close();
  serveur.kill();
  process.exit(echecs.length ? 1 : 0);
}

main().catch((error) => {
  console.error(error);
  process.exit(2);
});
