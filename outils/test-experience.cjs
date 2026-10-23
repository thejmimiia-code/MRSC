#!/usr/bin/env node
'use strict';

/**
 * Essais navigateur ciblés du panneau de présentation et de ses interactions.
 *
 * Dépendances temporaires, hors dépôt : Puppeteer Core et Chromium Sparticuz.
 * Ce script ne vérifie pas toutes les pages, tous les navigateurs ni un lecteur
 * d'écran ; il complète les contrôles structurels et ne vaut pas essai humain.
 */
const assert = require('node:assert/strict');
const { spawn } = require('node:child_process');
const path = require('node:path');
const Module = require('node:module');

if (process.env.MRSC_BROWSER_NODE_MODULES) {
  process.env.NODE_PATH = [process.env.MRSC_BROWSER_NODE_MODULES, process.env.NODE_PATH]
    .filter(Boolean)
    .join(path.delimiter);
  Module._initPaths();
}

let puppeteer;
let chromium;
let chromiumPackage;
try {
  puppeteer = require('puppeteer-core');
  chromiumPackage = require('@sparticuz/chromium');
  chromium = chromiumPackage.default;
} catch (error) {
  console.error(
    'Dépendances navigateur absentes. Installer hors du dépôt :\n'
    + '  npm install --prefix /tmp/mrsc-browser puppeteer-core@25.13.0 @sparticuz/chromium@153.0.0\n'
    + '  MRSC_BROWSER_NODE_MODULES=/tmp/mrsc-browser/node_modules node outils/test-experience.cjs'
  );
  process.exit(2);
}

const ROOT = path.resolve(__dirname, '..');
const port = Number(process.env.MRSC_TEST_PORT || 4173);
const baseURL = (process.env.MRSC_TEST_URL || `http://127.0.0.1:${port}/`).replace(/\/?$/, '/');
const origin = new URL(baseURL).origin;
const resultats = [];
let serveurLocal = null;

function adresse(route) {
  return new URL(String(route).replace(/^\//, ''), baseURL).href;
}

async function httpRepond(url) {
  try {
    const reponse = await fetch(url, { signal: AbortSignal.timeout(1500) });
    return reponse.status < 500;
  } catch (_error) {
    return false;
  }
}

async function attendreServeur(url, processus = null) {
  const fin = Date.now() + 30000;
  while (Date.now() < fin) {
    if (await httpRepond(url)) return;
    if (processus && processus.exitCode !== null) {
      throw new Error(`Le serveur local s’est arrêté prématurément (code ${processus.exitCode}).`);
    }
    await new Promise((resolve) => setTimeout(resolve, 200));
  }
  throw new Error(`Le serveur de test ne répond pas : ${url}`);
}

async function preparerServeur() {
  if (process.env.MRSC_TEST_URL) {
    await attendreServeur(adresse('index.html'));
    return;
  }
  if (await httpRepond(adresse('index.html'))) return;
  serveurLocal = spawn(
    process.env.PYTHON || 'python3',
    ['outils/serveur-local.py', '--bind', '127.0.0.1', '--port', String(port)],
    { cwd: ROOT, stdio: ['ignore', 'pipe', 'pipe'] }
  );
  const journaux = [];
  serveurLocal.stdout.on('data', (bloc) => journaux.push(String(bloc)));
  serveurLocal.stderr.on('data', (bloc) => journaux.push(String(bloc)));
  try {
    await attendreServeur(adresse('index.html'), serveurLocal);
  } catch (error) {
    throw new Error(`${error.message}\n${journaux.join('').slice(-5000)}`);
  }
}

async function creerPage(viewport = { width: 1280, height: 900 }, options = {}) {
  // Sparticuz démarre en --single-process : les BrowserContext incognito ne
  // peuvent pas créer d’onglet dans ce mode. Un onglet neuf isole chaque essai;
  // window.name évite de vider le stockage lors des navigations de l’essai.
  const page = await puppeteerBrowser.newPage();
  await page.setViewport({ ...viewport, deviceScaleFactor: 1 });
  await page.evaluateOnNewDocument((stockageBloque) => {
    if (window.name !== '__mrsc_test_experience__') {
      try { localStorage.clear(); sessionStorage.clear(); } catch (_error) { /* stockage refusé */ }
      window.name = '__mrsc_test_experience__';
    }
    if (stockageBloque) {
      Object.defineProperty(window, 'localStorage', {
        configurable: false,
        get() { throw new DOMException('Stockage bloqué pour le test', 'SecurityError'); },
      });
    }
  }, Boolean(options.stockageBloque));
  if (options.forcerSimulateurLocal) {
    await page.setRequestInterception(true);
    page.on('request', (requete) => {
      const url = new URL(requete.url());
      if (url.origin !== origin) {
        void requete.abort();
      } else if (url.pathname === '/api/verifier-source') {
        void requete.respond({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({ disponible: false }),
        });
      } else {
        void requete.continue();
      }
    });
  } else if (options.bloquerExterne) {
    await page.setRequestInterception(true);
    page.on('request', (requete) => {
      if (new URL(requete.url()).origin === origin) void requete.continue();
      else void requete.abort();
    });
  }
  return page;
}

async function ouvrirPageSite(page, route) {
  await page.goto(adresse(route), { waitUntil: 'domcontentloaded', timeout: 60000 });
  await page.waitForFunction(() => {
    const reglage = document.querySelector('[data-site-layout-settings]');
    return Boolean(reglage && !reglage.hidden && reglage.querySelector('summary'));
  }, { timeout: 30000 });
}

async function ouvrirSimulateur(page) {
  await page.goto(adresse('simulateur/'), { waitUntil: 'domcontentloaded', timeout: 60000 });
  await page.waitForSelector('#overlay.visible', { timeout: 90000 });
  const titre = await page.$eval('#modale-titre', (element) => element.textContent || '');
  assert.match(titre, /Comment lire ce simulateur/);
  // Le guide de première visite fait partie du parcours : le test le ferme avec
  // sa commande visible, au lieu de le contourner en préremplissant le stockage.
  await page.click('#modale .guide-actions button.primaire');
  await page.waitForFunction(() => !document.getElementById('overlay')?.classList.contains('visible'));
  await page.waitForFunction(() => {
    const reglage = document.querySelector('[data-site-layout-settings]');
    return Boolean(reglage && !reglage.hidden);
  }, { timeout: 15000 });
}

async function ouvrirPanneau(page) {
  const ouvert = await page.$eval('[data-site-layout-settings]', (element) => element.open);
  if (!ouvert) await page.click('[data-site-layout-settings] > summary');
  await page.waitForFunction(() => document.querySelector('[data-site-layout-settings]')?.open === true);
}

async function verifierPanneauDansViewport(page, selecteur) {
  const mesure = await page.$eval(selecteur, (element) => {
    const rectangle = element.getBoundingClientRect();
    return {
      left: rectangle.left,
      right: rectangle.right,
      top: rectangle.top,
      bottom: rectangle.bottom,
      width: rectangle.width,
      height: rectangle.height,
      viewportWidth: window.innerWidth,
      viewportHeight: window.innerHeight,
    };
  });
  assert.ok(mesure.width > 0 && mesure.height > 0, `${selecteur} doit être visible`);
  assert.ok(mesure.left >= -1, `${selecteur} sort à gauche : ${JSON.stringify(mesure)}`);
  assert.ok(mesure.right <= mesure.viewportWidth + 1, `${selecteur} sort à droite : ${JSON.stringify(mesure)}`);
  assert.ok(mesure.top >= -1, `${selecteur} sort en haut : ${JSON.stringify(mesure)}`);
  assert.ok(mesure.bottom <= mesure.viewportHeight + 1, `${selecteur} sort en bas : ${JSON.stringify(mesure)}`);
  const auPremierPlan = await page.$eval(selecteur, (element) => {
    const rectangle = element.getBoundingClientRect();
    const cible = document.elementFromPoint(rectangle.left + rectangle.width / 2, rectangle.top + rectangle.height / 2);
    return Boolean(cible && (cible === element || element.contains(cible)));
  });
  assert.equal(auPremierPlan, true, `${selecteur} doit rester au premier plan, sans être masqué par son ancêtre ou un autre panneau`);
}

async function verifierPanneauReplie(page, selecteur) {
  const etat = await page.$eval(selecteur, (element) => ({
    display: getComputedStyle(element).display,
    rectangles: element.getClientRects().length,
  }));
  assert.deepEqual(etat, { display: 'none', rectangles: 0 }, `${selecteur} doit être réellement masqué quand son panneau est fermé`);
}

async function executer(nom, action) {
  try {
    await action();
    resultats.push({ nom, reussi: true });
    console.log(`OK — ${nom}`);
  } catch (error) {
    resultats.push({ nom, reussi: false, erreur: error });
    console.error(`ÉCHEC — ${nom}\n${error.stack || error}`);
  }
}

let puppeteerBrowser;

async function main() {
  const cheminPaquetChromium = path.resolve(path.dirname(require.resolve('@sparticuz/chromium')), '..');
  const cheminLibrairies = await chromiumPackage.inflate(
    path.join(cheminPaquetChromium, 'bin', 'al2023.tar.br')
  );
  chromiumPackage.setupLambdaEnvironment(path.join(cheminLibrairies, 'lib'));
  await preparerServeur();
  puppeteerBrowser = await puppeteer.launch({
    args: chromium.args,
    defaultViewport: chromium.defaultViewport,
    executablePath: await chromium.executablePath(),
    headless: true,
  });

  await executer('Choix immédiat, contenu préservé, réglages existants et persistance entre pages', async () => {
    const page = await creerPage({ width: 1280, height: 900 });
    try {
      await ouvrirPageSite(page, 'index.html');
      const contenuAvant = await page.$eval('main', (element) => element.innerText);
      const navigationsAvant = await page.evaluate(() => performance.getEntriesByType('navigation').length);

      await page.click('[data-display-settings] > summary');
      await page.click('[data-text-increase]');
      await page.click('[data-contrast-toggle]');
      await page.click('[data-spacing-toggle]');
      await ouvrirPanneau(page);
      await page.click('[data-site-layout-settings] input[name="mrsc-site-layout"][value="panorama"]');
      await page.waitForFunction(() => document.documentElement.dataset.layout === 'panorama');

      const etat = await page.evaluate(() => ({
        texte: document.documentElement.classList.contains('texte-agrandi'),
        contraste: document.documentElement.classList.contains('contraste-renforce'),
        espacement: document.documentElement.classList.contains('espacement-renforce'),
        choix: localStorage.getItem('mrsc-mise-en-page'),
        annonces: document.querySelector('[data-site-layout-settings] [role="status"]')?.textContent,
        navigations: performance.getEntriesByType('navigation').length,
      }));
      assert.equal(etat.texte, true);
      assert.equal(etat.contraste, true);
      assert.equal(etat.espacement, true);
      assert.equal(etat.choix, 'panorama');
      assert.match(etat.annonces, /Panorama composite/);
      assert.equal(etat.navigations, navigationsAvant, 'le choix ne doit pas recharger la page');
      assert.equal(await page.$eval('main', (element) => element.innerText), contenuAvant);

      await page.goto(adresse('apprendre.html'), { waitUntil: 'domcontentloaded' });
      await page.waitForFunction(() => document.documentElement.dataset.layout === 'panorama');
      await ouvrirPageSite(page, 'apprendre.html');
      await ouvrirPanneau(page);

      // Les trois présentations ajoutées le 18 octobre 2026 s’appliquent
      // sans rechargement, sans perdre le texte et sans débordement général.
      const contenuCatalogue = await page.$eval('main', (element) => element.innerText);
      const libellesNeufs = { vitrine: 'Vitrine', mosaique: 'Mosaïque', compacte: 'Compacte' };
      for (const [valeur, libelle] of Object.entries(libellesNeufs)) {
        await page.click(`[data-site-layout-settings] input[name="mrsc-site-layout"][value="${valeur}"]`);
        await page.waitForFunction((attendue) => document.documentElement.dataset.layout === attendue, {}, valeur);
        const etatMode = await page.evaluate(() => ({
          choix: localStorage.getItem('mrsc-mise-en-page'),
          annonces: document.querySelector('[data-site-layout-settings] [role="status"]')?.textContent,
          debordement: document.documentElement.scrollWidth - window.innerWidth,
          apercu: Boolean(document.querySelector(`.layout-choice-preview[data-preview="${document.documentElement.dataset.layout}"]`)),
          navigations: performance.getEntriesByType('navigation').length,
        }));
        assert.equal(etatMode.choix, valeur);
        assert.match(etatMode.annonces, new RegExp(libelle));
        assert.ok(etatMode.debordement <= 1, `débordement horizontal en « ${libelle} » : ${etatMode.debordement}px`);
        assert.equal(etatMode.apercu, true, `mini-aperçu absent pour « ${libelle} »`);
        assert.equal(await page.$eval('main', (element) => element.innerText), contenuCatalogue);
      }

      await page.click('.layout-settings-reset');
      await page.waitForFunction(() => document.documentElement.dataset.layout === 'equilibree');
      assert.equal(await page.evaluate(() => localStorage.getItem('mrsc-mise-en-page')), 'equilibree');
    } finally {
      await page.close();
    }
  });

  await executer('Clavier, chevron et fermeture avec retour du focus', async () => {
    const page = await creerPage({ width: 1280, height: 900 });
    try {
      await ouvrirPageSite(page, 'index.html');
      const summary = '[data-site-layout-settings] > summary';
      await page.focus(summary);
      await page.keyboard.press('Enter');
      await page.waitForFunction(() => document.querySelector('[data-site-layout-settings]')?.open === true);
      const transformOuvert = await page.$eval('.layout-settings-chevron', (element) => getComputedStyle(element).transform);
      assert.notEqual(transformOuvert, 'none', 'le chevron doit pivoter à l’ouverture');

      await page.focus('[data-site-layout-settings] input[name="mrsc-site-layout"][value="equilibree"]');
      await page.keyboard.press('ArrowDown');
      await page.waitForFunction(() => document.documentElement.dataset.layout === 'lecture');
      await page.keyboard.press('Escape');
      await page.waitForFunction(() => document.querySelector('[data-site-layout-settings]')?.open === false);
      await page.waitForFunction(() => getComputedStyle(document.querySelector('.layout-settings-chevron')).transform === 'none');
      const retour = await page.evaluate(() => ({
        actif: document.activeElement?.matches('[data-site-layout-settings] > summary'),
        transform: getComputedStyle(document.querySelector('.layout-settings-chevron')).transform,
      }));
      assert.equal(retour.actif, true);
      assert.equal(retour.transform, 'none', 'le chevron de Présentation doit reprendre son sens fermé');

      const summaryAffichage = '[data-display-settings] > summary';
      await page.focus(summaryAffichage);
      await page.keyboard.press('Enter');
      await page.waitForFunction(() => document.querySelector('[data-display-settings]')?.open === true);
      const transformAffichageOuvert = await page.$eval('.display-settings-chevron', (element) => getComputedStyle(element).transform);
      assert.notEqual(transformAffichageOuvert, 'none', 'le chevron Affichage doit pivoter à l’ouverture');
      await page.keyboard.press('Escape');
      await page.waitForFunction(() => document.querySelector('[data-display-settings]')?.open === false);
      await page.waitForFunction(() => getComputedStyle(document.querySelector('.display-settings-chevron')).transform === 'none');
      assert.equal(await page.evaluate(() => document.activeElement?.matches('[data-display-settings] > summary')), true);
    } finally {
      await page.close();
    }
  });

  await executer('Mode compact réactivé au rétrécissement et bouton Agrandir lisible en fenêtre étroite', async () => {
    const page = await creerPage({ width: 720, height: 800 });
    try {
      await ouvrirPageSite(page, 'index.html');
      const bouton = '[data-header-compact-toggle]';
      const mesurerCadre = () => page.$eval(bouton, (element) => element.getBoundingClientRect().width);
      assert.equal(
        await page.$eval('.site-header', (element) => element.classList.contains('is-compact')),
        true,
        'à 720 px l’en-tête démarre compact'
      );
      const cadreAgrandir720 = await mesurerCadre();
      await page.click(bouton);
      await page.waitForFunction(() => !document.querySelector('.site-header')?.classList.contains('is-compact'));
      const cadreReduire720 = await mesurerCadre();
      assert.equal(cadreAgrandir720, cadreReduire720, 'le cadre ne doit pas changer quand le libellé bascule');

      await page.setViewport({ width: 500, height: 800, deviceScaleFactor: 1 });
      await page.waitForFunction(() => window.matchMedia('(max-width: 520px)').matches);
      await page.waitForFunction(() => document.querySelector('.site-header')?.classList.contains('is-compact'), { timeout: 2500 });
      await page.waitForFunction(() => document.querySelector('[data-header-compact-toggle]')?.textContent.trim() === 'Agrandir');
      // Sous 520 px, l'en-tête compact range ses cinq commandes dans une grille de
      // deux colonnes : leur largeur vient de la colonne, jamais du libellé. La
      // bascule change donc légitimement de disposition (c'est le sens même
      // d'« Agrandir ») ; ce qui doit rester stable, c'est le retour à la grille,
      // et l'égalité des deux commandes de la première rangée.
      const cadreAgrandir500 = await mesurerCadre();
      const largeursRangee1 = await page.evaluate(() => {
        const mesurer = (selecteur) => document.querySelector(selecteur).getBoundingClientRect().width;
        return [mesurer('.nav-toggle'), mesurer('[data-header-compact-toggle]')];
      });
      assert.equal(
        Math.round(largeursRangee1[0]),
        Math.round(largeursRangee1[1]),
        'les deux commandes de la première rangée partagent la même largeur'
      );
      await page.click(bouton);
      await page.waitForFunction(() => !document.querySelector('.site-header')?.classList.contains('is-compact'));
      await page.click(bouton);
      await page.waitForFunction(() => document.querySelector('.site-header')?.classList.contains('is-compact'));
      await page.waitForFunction(() => document.querySelector('[data-header-compact-toggle]')?.textContent.trim() === 'Agrandir');
      const cadreReduire500 = await mesurerCadre();
      assert.equal(cadreAgrandir500, cadreReduire500, 'le cadre compact revient identique après un aller-retour');

      await page.setViewport({ width: 480, height: 800, deviceScaleFactor: 1 });
      await page.waitForFunction(() => document.querySelector('.site-header')?.classList.contains('is-compact'), { timeout: 2500 });
      await page.waitForFunction(() => document.querySelector('[data-header-compact-toggle]')?.textContent.trim() === 'Agrandir');
      await page.evaluate(() => {
        const boutonCompact = document.querySelector('[data-header-compact-toggle]');
        window.__mutationsLibelleCompact = 0;
        window.__observateurLibelleCompact = new MutationObserver((mutations) => {
          window.__mutationsLibelleCompact += mutations.length;
        });
        window.__observateurLibelleCompact.observe(boutonCompact, { childList: true, characterData: true, subtree: true });
      });
      await page.setViewport({ width: 460, height: 800, deviceScaleFactor: 1 });
      await page.evaluate(() => new Promise((resolve) => requestAnimationFrame(() => requestAnimationFrame(resolve))));
      const mutationsAuRedimensionnement = await page.evaluate(() => {
        window.__observateurLibelleCompact.disconnect();
        return window.__mutationsLibelleCompact;
      });
      assert.equal(mutationsAuRedimensionnement, 0, 'un bouton déjà compact ne doit pas réécrire son libellé à chaque réduction');
      const cadreAgrandir460 = await mesurerCadre();
      await page.click(bouton);
      await page.waitForFunction(() => !document.querySelector('.site-header')?.classList.contains('is-compact'));
      await page.click(bouton);
      await page.waitForFunction(() => document.querySelector('.site-header')?.classList.contains('is-compact'));
      await page.waitForFunction(() => document.querySelector('[data-header-compact-toggle]')?.textContent.trim() === 'Agrandir');
      const cadreReduire460 = await mesurerCadre();
      assert.equal(cadreAgrandir460, cadreReduire460, 'le cadre compact revient identique après un aller-retour à 460 px');
      await page.setViewport({ width: 320, height: 800, deviceScaleFactor: 1 });
      await page.waitForFunction(() => document.querySelector('.site-header')?.classList.contains('is-compact'), { timeout: 2500 });
      const largeur320 = await page.evaluate(() => ({ document: document.documentElement.scrollWidth, viewport: innerWidth }));
      assert.ok(largeur320.document <= largeur320.viewport + 1, JSON.stringify(largeur320));
      const controlesBarre = await page.evaluate(() => Array.from(document.querySelectorAll(
        '.nav-toggle, .header-compact-toggle, .site-journey-settings, .display-settings, .layout-settings'
      )).filter((element) => !element.hidden && getComputedStyle(element).display !== 'none').map((element) => ({
        controle: element.className,
        flexShrink: getComputedStyle(element).flexShrink,
      })));
      assert.ok(controlesBarre.length >= 4, JSON.stringify(controlesBarre));
      assert.ok(controlesBarre.every((element) => element.flexShrink === '0'), JSON.stringify(controlesBarre));
      await page.click(bouton);
      await page.waitForFunction(() => !document.querySelector('.site-header')?.classList.contains('is-compact'));
      await page.setViewport({ width: 240, height: 800, deviceScaleFactor: 1 });
      await page.waitForFunction(() => document.querySelector('.site-header')?.classList.contains('is-compact'), { timeout: 2500 });
      const etat = await page.$eval(bouton, (element) => {
        const rectangle = element.getBoundingClientRect();
        const texte = document.createRange();
        texte.selectNodeContents(element);
        return {
          label: element.textContent.trim(),
          hidden: element.hidden,
          left: rectangle.left,
          right: rectangle.right,
          cadreLargeur: rectangle.width,
          width: element.clientWidth,
          scrollWidth: element.scrollWidth,
          lignes: texte.getClientRects().length,
          whiteSpace: getComputedStyle(element).whiteSpace,
          overflowWrap: getComputedStyle(element).overflowWrap,
          enteteCompacte: document.querySelector('.site-header').classList.contains('is-compact'),
          identiteMasquee: getComputedStyle(document.querySelector('.identity')).display === 'none',
        };
      });
      assert.equal(etat.label, 'Agrandir');
      assert.equal(etat.hidden, false);
      assert.equal(etat.enteteCompacte, true);
      assert.equal(etat.identiteMasquee, true);
      // Sous 520 px, la grille de l'en-tête compact fixe la largeur des commandes
      // (deux colonnes pleines) : « Agrandir » et « Réduire » occupent la même
      // cellule, donc la bascule de libellé ne peut plus déplacer le cadre.
      const largeurMenue240 = await page.$eval('.nav-toggle', (element) => element.getBoundingClientRect().width);
      assert.equal(
        Math.round(etat.cadreLargeur),
        Math.round(largeurMenue240),
        'chaque commande occupe une demi-largeur de la grille, indépendamment de son libellé'
      );
      assert.equal(etat.whiteSpace, 'normal');
      assert.equal(etat.overflowWrap, 'normal', 'les libellés ne se coupent plus en plein mot');
      assert.equal(etat.lignes, 1, 'à 240 px CSS, le libellé tient naturellement sur une ligne');
      assert.ok(etat.width >= 32 && etat.scrollWidth <= etat.width, JSON.stringify(etat));
      assert.ok(etat.left >= 0 && etat.right <= 240, JSON.stringify(etat));

      await page.setViewport({ width: 70, height: 800, deviceScaleFactor: 1 });
      const cadreEtTexte = await page.$eval(bouton, (element) => {
        const cadre = element.getBoundingClientRect();
        const style = getComputedStyle(element);
        const gaucheTexte = cadre.left + parseFloat(style.borderLeftWidth) + parseFloat(style.paddingLeft);
        const droiteTexte = cadre.right - parseFloat(style.borderRightWidth) - parseFloat(style.paddingRight);
        const range = document.createRange();
        range.selectNodeContents(element);
        return {
          left: cadre.left,
          right: cadre.right,
          viewport: innerWidth,
          cadreLargeur: cadre.width,
          largeur: element.clientWidth,
          scrollWidth: element.scrollWidth,
          hauteur: cadre.height,
          gaucheTexte,
          droiteTexte,
          lignesTexte: Array.from(range.getClientRects()).map((rect) => ({ left: rect.left, right: rect.right })),
          largeurOutils: document.querySelector('.header-compact-tools').getBoundingClientRect().width,
        };
      });
      assert.ok(cadreEtTexte.left >= 0 && cadreEtTexte.right <= cadreEtTexte.viewport, JSON.stringify(cadreEtTexte));
      // Grille `auto-fit` : la commande remplit sa colonne, et la colonne se réduit
      // avec la fenêtre au lieu de forcer un débordement (à 70 px, une colonne).
      assert.equal(
        Math.round(cadreEtTexte.cadreLargeur),
        Math.round(cadreEtTexte.largeurOutils),
        JSON.stringify(cadreEtTexte)
      );
      assert.ok(cadreEtTexte.hauteur >= 32, JSON.stringify(cadreEtTexte));
      assert.ok(cadreEtTexte.scrollWidth <= cadreEtTexte.largeur, JSON.stringify(cadreEtTexte));
      // Le libellé doit tenir dans le cadre : replié si besoin, sur une ligne quand
      // la place suffit. Ce qui compte, c'est qu'aucune ligne ne sorte.
      assert.ok(cadreEtTexte.lignesTexte.length >= 1, JSON.stringify(cadreEtTexte));
      assert.ok(
        cadreEtTexte.lignesTexte.every((ligne) => ligne.left >= cadreEtTexte.gaucheTexte - 1 && ligne.right <= cadreEtTexte.droiteTexte + 1),
        JSON.stringify(cadreEtTexte)
      );
    } finally {
      await page.close();
    }
  });

  await executer('Panneaux Affichage et Présentation visibles aux largeurs 320 et 1440 px', async () => {
    const page = await creerPage({ width: 320, height: 800 });
    try {
      const pages = [
        'index.html',
        'apprendre.html',
        'apprendre/fiches/maths-budget.html',
        'ia-societe.html',
        'transparence.html',
        '404.html',
      ];
      for (const route of pages) {
        for (const width of [320, 1440]) {
          await page.setViewport({ width, height: 850, deviceScaleFactor: 1 });
          await ouvrirPageSite(page, route);
          await verifierPanneauReplie(page, '.display-settings-panel');
          await verifierPanneauReplie(page, '.layout-settings-panel');
          await verifierPanneauReplie(page, '.site-journey-panel');
          const debordement = await page.evaluate(() => ({
            viewport: window.innerWidth,
            document: document.documentElement.scrollWidth,
          }));
          assert.ok(
            debordement.document <= debordement.viewport + 1,
            `${route} déborde à ${width}px : ${JSON.stringify(debordement)}`
          );
          if (width !== 320) continue;

          await page.click('[data-display-settings] > summary');
          await page.waitForFunction(() => document.querySelector('[data-display-settings]')?.open === true);
          await verifierPanneauDansViewport(page, '.display-settings-panel');
          await ouvrirPanneau(page);
          await verifierPanneauDansViewport(page, '.layout-settings-panel');
        }
      }
      await page.setViewport({ width: 667, height: 375, deviceScaleFactor: 1 });
      await ouvrirPageSite(page, 'index.html');
      const paysage = await page.evaluate(() => ({ viewport: innerWidth, document: document.documentElement.scrollWidth }));
      assert.ok(paysage.document <= paysage.viewport + 1, `débordement en paysage court : ${JSON.stringify(paysage)}`);
      await page.click('[data-display-settings] > summary');
      await page.waitForFunction(() => document.querySelector('[data-display-settings]')?.open === true);
      await verifierPanneauDansViewport(page, '.display-settings-panel');
      await ouvrirPanneau(page);
      await verifierPanneauDansViewport(page, '.layout-settings-panel');
    } finally {
      await page.close();
    }
  });

  await executer('320 px à 130 % avec contraste et espacement renforcés sur le site et le simulateur', async () => {
    const pageSite = await creerPage({ width: 320, height: 800 });
    try {
      await ouvrirPageSite(pageSite, 'index.html');
      await pageSite.click('[data-display-settings] > summary');
      await pageSite.click('[data-text-increase]');
      await pageSite.click('[data-text-increase]');
      await pageSite.click('[data-contrast-toggle]');
      await pageSite.click('[data-spacing-toggle]');
      const niveauSite = await pageSite.$eval('[data-text-size-level]', (element) => element.textContent.trim());
      assert.match(niveauSite, /130/);
      await verifierPanneauDansViewport(pageSite, '.display-settings-panel');
      await ouvrirPanneau(pageSite);
      await verifierPanneauDansViewport(pageSite, '.layout-settings-panel');
      await pageSite.click('[data-site-layout-settings] input[name="mrsc-site-layout"][value="panorama"]');
      await pageSite.waitForFunction(() => document.documentElement.dataset.layout === 'panorama');
      const etatSite = await pageSite.evaluate(() => ({
        largeurDocument: document.documentElement.scrollWidth,
        largeurFenetre: innerWidth,
        contraste: document.documentElement.classList.contains('contraste-renforce'),
        espacement: document.documentElement.classList.contains('espacement-renforce'),
      }));
      assert.equal(etatSite.contraste, true);
      assert.equal(etatSite.espacement, true);
      assert.ok(etatSite.largeurDocument <= etatSite.largeurFenetre + 1, JSON.stringify(etatSite));
    } finally {
      await pageSite.close();
    }

    const pageSimulateur = await creerPage({ width: 320, height: 800 }, { bloquerExterne: true });
    try {
      await ouvrirSimulateur(pageSimulateur);
      await pageSimulateur.click('[data-sim-text-increase]');
      await pageSimulateur.click('[data-sim-text-increase]');
      await pageSimulateur.click('[data-sim-contrast]');
      await pageSimulateur.click('[data-sim-spacing]');
      const niveauSimulateur = await pageSimulateur.$eval('[data-sim-text-level]', (element) => element.textContent.trim());
      assert.match(niveauSimulateur, /130/);
      await ouvrirPanneau(pageSimulateur);
      await verifierPanneauDansViewport(pageSimulateur, '.site-layout-panel');
      await pageSimulateur.click('[data-site-layout-settings] input[name="mrsc-site-layout"][value="panorama"]');
      await pageSimulateur.waitForFunction(() => document.documentElement.dataset.layout === 'panorama');
      const etatSimulateur = await pageSimulateur.evaluate(() => ({
        largeurDocument: document.documentElement.scrollWidth,
        largeurFenetre: innerWidth,
        contraste: document.documentElement.classList.contains('contraste-renforce'),
        espacement: document.documentElement.classList.contains('espacement-renforce'),
        parcours: (() => {
          const d = document.querySelector('[data-site-journey]');
          const b = document.querySelector('.site-return-bar');
          const rect = (element) => { const r = element?.getBoundingClientRect(); return r && { left: Math.round(r.left), right: Math.round(r.right), top: Math.round(r.top), bottom: Math.round(r.bottom), width: Math.round(r.width) }; };
          return { tag: d?.tagName, open: d?.open, display: d && getComputedStyle(d).display, bar: rect(b), details: rect(d), panel: rect(d?.querySelector('.site-journey-panel')) };
        })(),
        scrollsInternes: Array.from(document.querySelectorAll('body *'))
          .filter((element) => !element.closest('table') && element.scrollWidth > element.clientWidth + 1)
          .slice(0, 12)
          .map((element) => ({ tag: element.tagName, id: element.id, classes: typeof element.className === 'string' ? element.className : '', client: element.clientWidth, scroll: element.scrollWidth, text: (element.textContent || '').trim().slice(0, 120) })),
        debordements: Array.from(document.querySelectorAll('body *'))
          .map((element) => ({ element, rectangle: element.getBoundingClientRect() }))
          .filter(({ element, rectangle }) => !element.closest('table') && (rectangle.right > innerWidth + 1 || rectangle.left < -1))
          .sort((a, b) => b.rectangle.right - a.rectangle.right)
          .slice(0, 12)
          .map(({ element, rectangle }) => ({
            tag: element.tagName,
            id: element.id,
            classes: typeof element.className === 'string' ? element.className : '',
            left: Math.round(rectangle.left),
            right: Math.round(rectangle.right),
            width: Math.round(rectangle.width),
            scrollWidth: element.scrollWidth,
          })),
      }));
      assert.equal(etatSimulateur.contraste, true);
      assert.equal(etatSimulateur.espacement, true);
      assert.ok(etatSimulateur.largeurDocument <= etatSimulateur.largeurFenetre + 1, JSON.stringify(etatSimulateur));
      await pageSimulateur.keyboard.press('Escape');
      await pageSimulateur.waitForFunction(() => document.querySelector('[data-site-layout-settings]')?.open === false);
      await verifierPanneauReplie(pageSimulateur, '.site-layout-panel');
      await pageSimulateur.click('[data-site-journey] > summary');
      await pageSimulateur.waitForFunction(() => document.querySelector('[data-site-journey]')?.open === true);
      await verifierPanneauDansViewport(pageSimulateur, '.site-journey-panel');
      await pageSimulateur.keyboard.press('Escape');
      await pageSimulateur.waitForFunction(() => document.querySelector('[data-site-journey]')?.open === false);
      await verifierPanneauReplie(pageSimulateur, '.site-journey-panel');
      await ouvrirPanneau(pageSimulateur);
      await pageSimulateur.setViewport({ width: 320, height: 375, deviceScaleFactor: 1 });
      await verifierPanneauDansViewport(pageSimulateur, '.site-layout-panel');
      const paysageSimulateur = await pageSimulateur.evaluate(() => ({ viewport: innerWidth, document: document.documentElement.scrollWidth }));
      assert.ok(paysageSimulateur.document <= paysageSimulateur.viewport + 1, JSON.stringify(paysageSimulateur));
    } finally {
      await pageSimulateur.close();
    }
  });

  await executer('Choix utilisable pendant la visite quand localStorage est bloqué', async () => {
    const page = await creerPage({ width: 320, height: 800 }, { stockageBloque: true });
    const erreursPage = [];
    page.on('pageerror', (error) => erreursPage.push(error.message));
    try {
      await ouvrirPageSite(page, 'index.html');
      await ouvrirPanneau(page);
      await page.click('[data-site-layout-settings] input[name="mrsc-site-layout"][value="lecture"]');
      await page.waitForFunction(() => document.documentElement.dataset.layout === 'lecture');
      const acces = await page.evaluate(() => {
        try { localStorage.getItem('mrsc-mise-en-page'); return false; }
        catch (_error) { return true; }
      });
      assert.equal(acces, true, 'le navigateur doit bien simuler un stockage refusé');
      assert.deepEqual(erreursPage, [], 'le blocage ne doit pas casser le script de la page');
    } finally {
      await page.close();
    }

    const pageSimulateur = await creerPage(
      { width: 320, height: 800 },
      { stockageBloque: true, bloquerExterne: true }
    );
    const erreursSimulateur = [];
    pageSimulateur.on('pageerror', (error) => erreursSimulateur.push(error.message));
    try {
      await ouvrirSimulateur(pageSimulateur);
      await ouvrirPanneau(pageSimulateur);
      await pageSimulateur.click('[data-site-layout-settings] input[name="mrsc-site-layout"][value="lecture"]');
      await pageSimulateur.waitForFunction(() => document.documentElement.dataset.layout === 'lecture');
      const stockageRefuse = await pageSimulateur.evaluate(() => {
        try { localStorage.getItem('mrsc-mise-en-page'); return false; }
        catch (_error) { return true; }
      });
      assert.equal(stockageRefuse, true);
      assert.deepEqual(erreursSimulateur, [], 'le simulateur autonome doit rester utilisable sans stockage local');
    } finally {
      await pageSimulateur.close();
    }
  });

  await executer('Guide de première visite, commande de présentation et panneau du simulateur à 320 px', async () => {
    const page = await creerPage(
      { width: 320, height: 800 },
      { bloquerExterne: true }
    );
    try {
      await ouvrirSimulateur(page);
      await verifierPanneauReplie(page, '.site-layout-panel');
      await verifierPanneauReplie(page, '.site-journey-panel');
      await ouvrirPanneau(page);
      await verifierPanneauDansViewport(page, '.site-layout-panel');
      const chevronOuvert = await page.$eval('.site-layout-chevron', (element) => getComputedStyle(element).transform);
      assert.notEqual(chevronOuvert, 'none', 'le chevron du simulateur doit pivoter à l’ouverture');
      await page.click('[data-site-layout-settings] input[name="mrsc-site-layout"][value="panorama"]');
      await page.waitForFunction(() => document.documentElement.dataset.layout === 'panorama');
      assert.equal(await page.evaluate(() => localStorage.getItem('mrsc-mise-en-page')), 'panorama');
      const etat = await page.evaluate(() => ({
        guideFerme: !document.getElementById('overlay').classList.contains('visible'),
        contenu: Boolean(document.querySelector('#contenu-principal h1')),
        largeurDocument: document.documentElement.scrollWidth,
        largeurFenetre: window.innerWidth,
      }));
      assert.equal(etat.guideFerme, true);
      assert.equal(etat.contenu, true);
      assert.ok(etat.largeurDocument <= etat.largeurFenetre + 1, JSON.stringify(etat, null, 2));
      await page.keyboard.press('Escape');
      await page.waitForFunction(() => document.querySelector('[data-site-layout-settings]')?.open === false);
      await page.waitForFunction(() => getComputedStyle(document.querySelector('.site-layout-chevron')).transform === 'none');
      await verifierPanneauReplie(page, '.site-layout-panel');
    } finally {
      await page.close();
    }
  });

  await executer('Synchronisation du choix et des réglages vers l’iframe locale de même origine', async () => {
    const page = await creerPage(
      { width: 1440, height: 1000 },
      { forcerSimulateurLocal: true }
    );
    try {
      await page.goto(adresse('simulateur.html'), { waitUntil: 'domcontentloaded', timeout: 60000 });
      await page.waitForFunction(() => {
        const iframe = document.querySelector('iframe.simulateur-frame');
        if (!iframe) return false;
        try {
          return iframe.contentWindow.location.origin === window.location.origin
            && Boolean(iframe.contentDocument?.querySelector('#contenu-principal'));
        } catch (_error) {
          return false;
        }
      }, { timeout: 90000 });
      await page.waitForFunction(() => {
        const reglage = document.querySelector('[data-site-layout-settings]');
        return Boolean(reglage && !reglage.hidden);
      }, { timeout: 30000 });
      const frame = page.frames().find((element) => element.url().includes('/simulateur/'));
      assert.ok(frame, 'la copie locale doit être chargée dans une iframe de même origine');

      // Le guide est exercé avec son vrai bouton dans le test du simulateur
      // autonome ; ici l’iframe peut rester à sa place dans la page hôte.
      const controlesMasques = await frame.evaluate(() => ({
        affichage: document.getElementById('mrsc-display-controls')?.hidden,
        presentation: document.querySelector('[data-site-layout-settings]')?.hidden,
      }));
      assert.equal(controlesMasques.affichage, true);
      assert.equal(controlesMasques.presentation, true);

      await page.click('[data-display-settings] > summary');
      await page.click('[data-text-increase]');
      await page.click('[data-contrast-toggle]');
      await page.click('[data-spacing-toggle]');
      await ouvrirPanneau(page);
      await page.click('[data-site-layout-settings] input[name="mrsc-site-layout"][value="panorama"]');
      await frame.waitForFunction(() => document.documentElement.dataset.layout === 'panorama');
      const synchronisation = await frame.evaluate(() => ({
        texte: document.documentElement.classList.contains('texte-agrandi'),
        contraste: document.documentElement.classList.contains('contraste-renforce'),
        espacement: document.documentElement.classList.contains('espacement-renforce'),
        layout: document.documentElement.dataset.layout,
      }));
      assert.deepEqual(synchronisation, {
        texte: true,
        contraste: true,
        espacement: true,
        layout: 'panorama',
      });
    } finally {
      await page.close();
    }
  });

  const echoues = resultats.filter((resultat) => !resultat.reussi);
  console.log(`\n${resultats.length - echoues.length}/${resultats.length} essais navigateur réussis.`);
  if (echoues.length) process.exitCode = 1;
}

main()
  .catch((error) => {
    console.error(error.stack || error);
    process.exitCode = 1;
  })
  .finally(async () => {
    if (puppeteerBrowser) await puppeteerBrowser.close().catch(() => undefined);
    if (serveurLocal && serveurLocal.exitCode === null) {
      serveurLocal.kill('SIGTERM');
      await new Promise((resolve) => {
        const fin = setTimeout(resolve, 2000);
        serveurLocal.once('exit', () => { clearTimeout(fin); resolve(); });
      });
      if (serveurLocal.exitCode === null) serveurLocal.kill('SIGKILL');
    }
  });
