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

async function ouvrirPersonnalisation(page) {
  const etat = await page.evaluate(() => {
    const panneau = document.querySelector('[data-customize-settings]');
    return { present: Boolean(panneau), ouvert: panneau?.open === true };
  });
  // Certaines pages (simulateur) n'ont pas d'en-tête compact : leurs réglages
  // sont directement accessibles, sans panneau intermédiaire.
  if (!etat.present || etat.ouvert) return;
  await page.click('.customize-settings > summary');
  await page.waitForFunction(() => document.querySelector('[data-customize-settings]')?.open === true);
}

async function ouvrirPanneau(page) {
  // Les réglages sont désormais des lignes du panneau « Personnalisation » :
  // il faut l'ouvrir avant de pouvoir atteindre « Présentation ».
  await ouvrirPersonnalisation(page);
  const ouvert = await page.$eval('[data-site-layout-settings]', (element) => element.open);
  if (ouvert) return;
  const resume = '[data-site-layout-settings] > summary';
  await page.click(resume);
  try {
    await page.waitForFunction(() => document.querySelector('[data-site-layout-settings]')?.open === true, { timeout: 2000 });
  } catch (_erreur) {
    // Sur le simulateur, la barre de retour est collante : au clic suivant, un
    // élément peut recouvrir le résumé et avaler le clic. L'activation au
    // clavier vise le contrôle, pas ses coordonnées.
    await page.focus(resume);
    await page.keyboard.press('Enter');
    await page.waitForFunction(() => document.querySelector('[data-site-layout-settings]')?.open === true);
  }
}

async function verifierPanneauDansViewport(page, selecteur) {
  const mesure = await page.$eval(selecteur, (element) => {
    const rectangle = element.getBoundingClientRect();
    // Un réglage ouvert vit désormais dans le panneau « Personnalisation », qui
    // défile : sa hauteur totale peut dépasser l'écran, et c'est le défilement qui
    // le rend atteignable. Ce qui doit tenir, c'est sa largeur et son entrée en
    // haut, plus un conteneur qui défile vraiment.
    let defilant = null;
    for (let parent = element.parentElement; parent; parent = parent.parentElement) {
      const style = getComputedStyle(parent);
      if (
        /(auto|scroll)/.test(style.overflowY)
        && parent.scrollHeight > parent.clientHeight + 1
      ) {
        const cadre = parent.getBoundingClientRect();
        defilant = {
          left: cadre.left,
          right: cadre.right,
          top: cadre.top,
          bottom: cadre.bottom,
        };
        break;
      }
    }
    return {
      left: rectangle.left,
      right: rectangle.right,
      top: rectangle.top,
      bottom: rectangle.bottom,
      width: rectangle.width,
      height: rectangle.height,
      viewportWidth: window.innerWidth,
      viewportHeight: window.innerHeight,
      defilant,
    };
  });
  assert.ok(mesure.width > 0 && mesure.height > 0, `${selecteur} doit être visible`);
  assert.ok(mesure.left >= -1, `${selecteur} sort à gauche : ${JSON.stringify(mesure)}`);
  assert.ok(mesure.right <= mesure.viewportWidth + 1, `${selecteur} sort à droite : ${JSON.stringify(mesure)}`);
  assert.ok(mesure.top >= -1, `${selecteur} sort en haut : ${JSON.stringify(mesure)}`);
  if (mesure.defilant) {
    assert.ok(mesure.bottom > mesure.top, `${selecteur} : hauteur nulle`);
    assert.ok(
      mesure.defilant.top >= -1 && mesure.defilant.bottom <= mesure.viewportHeight + 1,
      `${selecteur} : son panneau défilable sort de l'écran ${JSON.stringify(mesure.defilant)}`
    );
    assert.ok(
      mesure.top <= mesure.defilant.bottom + 1,
      `${selecteur} commence sous le panneau qui doit le faire défiler : ${JSON.stringify(mesure)}`
    );
  } else {
    assert.ok(mesure.bottom <= mesure.viewportHeight + 1, `${selecteur} sort en bas : ${JSON.stringify(mesure)}`);
  }
  const auPremierPlan = await page.$eval(selecteur, (element) => {
    const rectangle = element.getBoundingClientRect();
    const x = Math.min(Math.max(rectangle.left + rectangle.width / 2, 0), window.innerWidth - 1);
    const y = Math.min(Math.max(rectangle.top + 4, 0), window.innerHeight - 1);
    const cible = document.elementFromPoint(x, y);
    return Boolean(
      cible && (cible === element || element.contains(cible) || cible.contains(element))
    );
  });
  assert.equal(auPremierPlan, true, `${selecteur} doit rester au premier plan, sans être masqué par un ancêtre ou un autre panneau`);
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

      await ouvrirPersonnalisation(page);
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
      await ouvrirPersonnalisation(page);
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

  await executer('En-tête compact : deux commandes, réglages groupés et bascule réversible', async () => {
    const page = await creerPage({ width: 720, height: 800 });
    try {
      await ouvrirPageSite(page, 'index.html');
      const bascule = '[data-header-compact-toggle]';
      const etatEntete = () => page.evaluate(() => {
        const rect = (element) => element.getBoundingClientRect();
        const outils = document.querySelector('.header-compact-tools');
        return {
          compact: document.querySelector('.site-header').classList.contains('is-compact'),
          commandes: Array.from(outils.children)
            .filter((element) => rect(element).height > 0)
            .map((element) => ({
              texte: (element.textContent || '').trim().replace(/\s+/g, ' '),
              largeur: Math.round(rect(element).width),
              hauteur: Math.round(rect(element).height),
              panneau: element.matches('[data-customize-settings]'),
            })),
        };
      });

      assert.equal((await etatEntete()).compact, true, 'à 720 px l’en-tête démarre compact');
      const entete = await etatEntete();
      // Une seule commande de réglage : « Personnalisation ». « Réduire », « Parcours »,
      // « Affichage » et « Présentation » en sont devenus les lignes.
      assert.equal(
        entete.commandes.length,
        2,
        `l’en-tête doit garder deux commandes : ${JSON.stringify(entete.commandes)}`
      );
      assert.match(entete.commandes[0].texte, /^Menu$/);
      assert.match(entete.commandes[1].texte, /^Personnalisation/);
      assert.equal(entete.commandes[1].panneau, true, 'la seconde commande est le panneau Personnalisation');
      assert.ok(
        entete.commandes.every((commande) => commande.hauteur >= 32),
        JSON.stringify(entete.commandes)
      );

      // Clavier : Entrée ouvre le panneau ; les quatre réglages y sont des lignes
      // pleine largeur, contenues dans le cadre, plus la commande « Écouter la
      // page » ajoutée le 23 octobre 2026 (cinq blocs, dont quatre réglages).
      await page.focus('.customize-settings > summary');
      await page.keyboard.press('Enter');
      await page.waitForFunction(() => document.querySelector('[data-customize-settings]')?.open === true);
      const lignes = await page.evaluate(() => {
        const panneau = document.querySelector('.customize-settings-panel');
        const cadre = panneau.getBoundingClientRect();
        const style = getComputedStyle(panneau);
        const interieur = cadre.width - parseFloat(style.paddingLeft) - parseFloat(style.paddingRight);
        return Array.from(panneau.children)
          .filter((element) => element.getBoundingClientRect().height > 0)
          .map((element) => {
            const boite = element.getBoundingClientRect();
            return {
              nom: (typeof element.className === 'string' ? element.className : element.tagName) || element.tagName,
              hauteur: Math.round(boite.height),
              largeur: Math.round(boite.width),
              dansPanneau: boite.left >= cadre.left - 1 && boite.right <= cadre.right + 1,
            };
          })
          .concat([{ interieur: Math.round(interieur) }]);
      });
      const mesureLignes = lignes.slice(0, -1);
      const largeurInterieure = lignes[lignes.length - 1].interieur;
      assert.equal(
        mesureLignes.length,
        5,
        `les quatre réglages et la lecture à voix haute doivent être dans le panneau : ${JSON.stringify(mesureLignes)}`
      );
      assert.equal(
        mesureLignes.filter((ligne) => ligne.nom.includes('read-aloud')).length,
        1,
        'la commande « Écouter la page » doit être présente une seule fois'
      );
      assert.ok(mesureLignes.every((ligne) => ligne.hauteur >= 32), JSON.stringify(mesureLignes));
      // Chaque réglage porte un repère visuel dessiné : une icône en masque, pas
      // un glyphe de police dont le rendu dépend de la machine.
      const icones = await page.evaluate(() => {
        const panneau = document.querySelector('.customize-settings-panel');
        return Array.from(panneau.querySelectorAll(':scope > details > summary, :scope > button'))
          .filter((element) => element.getBoundingClientRect().height > 0)
          .map((element) => ({
            libelle: (element.textContent || '').trim().slice(0, 18),
            masque: getComputedStyle(element, '::before').maskImage || getComputedStyle(element, '::before').webkitMaskImage,
          }));
      });
      assert.equal(icones.length, 4, JSON.stringify(icones));
      assert.ok(
        icones.every((icone) => icone.masque && icone.masque !== 'none'),
        `chaque réglage doit porter une icône : ${JSON.stringify(icones)}`
      );
      assert.ok(mesureLignes.every((ligne) => ligne.dansPanneau), JSON.stringify(mesureLignes));
      assert.ok(
        mesureLignes.every((ligne) => ligne.largeur >= largeurInterieure - 2),
        `${JSON.stringify(mesureLignes)} pour ${largeurInterieure}px utiles : un réglage n'occupe plus la ligne entière`
      );

      // « Agrandir » bascule l'en-tête sans refermer le panneau : sinon « Réduire »
      // deviendrait inatteignable, le bouton vivant dans ce panneau.
      const largeurAvant = await page.$eval(bascule, (element) => Math.round(element.getBoundingClientRect().width));
      await page.click(bascule);
      await page.waitForFunction(() => !document.querySelector('.site-header').classList.contains('is-compact'));
      assert.equal(
        await page.evaluate(() => document.querySelector('[data-customize-settings]')?.open),
        true,
        'le panneau ne doit pas se refermer sur son propre bouton'
      );
      assert.equal(await page.$eval(bascule, (element) => element.textContent.trim()), 'Réduire');
      assert.equal(
        await page.$eval(bascule, (element) => Math.round(element.getBoundingClientRect().width)),
        largeurAvant,
        'le cadre de la commande ne change pas quand le libellé bascule'
      );
      await page.click(bascule);
      await page.waitForFunction(() => document.querySelector('.site-header').classList.contains('is-compact'));
      assert.equal(await page.$eval(bascule, (element) => element.textContent.trim()), 'Agrandir');

      // Échap referme d'abord le réglage ouvert, puis le panneau.
      await page.click('[data-site-layout-settings] > summary');
      await page.waitForFunction(() => document.querySelector('[data-site-layout-settings]')?.open === true);
      await page.keyboard.press('Escape');
      await page.waitForFunction(() => document.querySelector('[data-site-layout-settings]')?.open === false);
      assert.equal(
        await page.evaluate(() => document.querySelector('[data-customize-settings]')?.open),
        true,
        'le premier Échap ne referme que le réglage ouvert'
      );
      await page.keyboard.press('Escape');
      await page.waitForFunction(() => document.querySelector('[data-customize-settings]')?.open === false);
      assert.equal(
        await page.evaluate(() => document.activeElement?.matches('.customize-settings > summary')),
        true,
        'le focus revient sur la commande « Personnalisation »'
      );

      // Sous 520 px, les deux commandes partagent la grille à parts égales : 32 px
      // de haut, même largeur, quel que soit le libellé.
      await page.setViewport({ width: 500, height: 800, deviceScaleFactor: 1 });
      await page.waitForFunction(() => document.querySelector('.site-header')?.classList.contains('is-compact'), { timeout: 2500 });
      await page.waitForFunction(
        () => document.querySelector('[data-header-compact-toggle]')?.textContent.trim() === 'Agrandir'
      );
      const rangee = await page.evaluate(() => {
        const rect = (selecteur) => document.querySelector(selecteur).getBoundingClientRect();
        return ['.nav-toggle', '.customize-settings > summary'].map((selecteur) => ({
          largeur: Math.round(rect(selecteur).width),
          hauteur: Math.round(rect(selecteur).height),
        }));
      });
      assert.equal(rangee[0].largeur, rangee[1].largeur, JSON.stringify(rangee));
      assert.equal(rangee[0].hauteur, 32, JSON.stringify(rangee));
      assert.equal(rangee[1].hauteur, 32, JSON.stringify(rangee));

      // À 320 px, les deux libellés tiennent entiers dans leur bouton : aucune
      // commande n'est rognée, et les deux gardent la même largeur.
      await page.setViewport({ width: 320, height: 800, deviceScaleFactor: 1 });
      await page.waitForFunction(() => document.querySelector('.site-header')?.classList.contains('is-compact'), { timeout: 2500 });
      const commandes320 = await page.evaluate(() => {
        const mesurer = (selecteur) => {
          const element = document.querySelector(selecteur);
          const cadre = element.getBoundingClientRect();
          return {
            largeur: Math.round(cadre.width),
            hauteur: Math.round(cadre.height),
            scrollWidth: element.scrollWidth,
            clientWidth: element.clientWidth,
          };
        };
        return ['.nav-toggle', '.customize-settings > summary'].map(mesurer);
      });
      assert.ok(
        commandes320.every((commande) => commande.scrollWidth <= commande.clientWidth + 1),
        `les deux commandes gardent leur libellé entier à 320 px : ${JSON.stringify(commandes320)}`
      );
      assert.ok(commandes320.every((commande) => commande.hauteur === 32), JSON.stringify(commandes320));
      assert.equal(commandes320[0].largeur, commandes320[1].largeur, JSON.stringify(commandes320));

      // Jusqu'à 240 px, le panneau reste dans l'écran et ses lignes restent dans
      // le panneau, sans débordement horizontal de la page.
      for (const largeur of [240]) {
        await page.setViewport({ width: largeur, height: 800, deviceScaleFactor: 1 });
        await ouvrirPersonnalisation(page);
        const etat = await page.evaluate(() => {
          const panneau = document.querySelector('.customize-settings-panel');
          const cadre = panneau.getBoundingClientRect();
          const debordement = document.documentElement.scrollWidth - document.documentElement.clientWidth;
          const lignes = Array.from(panneau.children)
            .filter((element) => element.getBoundingClientRect().height > 0)
            .map((element) => {
              const boite = element.getBoundingClientRect();
              return {
                nom: typeof element.className === 'string' ? element.className : element.tagName,
                left: Math.round(boite.left),
                right: Math.round(boite.right),
                hauteur: Math.round(boite.height),
              };
            });
          return {
            viewport: window.innerWidth,
            gauche: Math.round(cadre.left),
            droite: Math.round(cadre.right),
            debordement,
            lignes,
          };
        });
        assert.ok(etat.gauche >= -1 && etat.droite <= etat.viewport + 1, `${largeur}px : ${JSON.stringify(etat)}`);
        // Quatre réglages et la lecture à voix haute, ajoutée le 23 octobre 2026.
        assert.ok(etat.lignes.length === 5, `${largeur}px : ${JSON.stringify(etat.lignes)}`);
        assert.ok(
          etat.lignes.every((ligne) => ligne.left >= etat.gauche - 1 && ligne.right <= etat.droite + 1),
          `${largeur}px : une ligne sort du panneau ${JSON.stringify(etat.lignes)}`
        );
        assert.ok(
          etat.lignes.every((ligne) => ligne.hauteur >= 32),
          `${largeur}px : une ligne descend sous 32 px ${JSON.stringify(etat.lignes)}`
        );
        assert.ok(etat.debordement <= 1, `${largeur}px : débordement de ${etat.debordement}px`);
      }
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

          await ouvrirPersonnalisation(page);
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
      await ouvrirPersonnalisation(page);
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
      await ouvrirPersonnalisation(pageSite);
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

  await executer('Lecture à voix haute : commande unique, arrêt net, rien envoyé', async () => {
    const page = await creerPage({ width: 390, height: 820 });
    try {
      await ouvrirPageSite(page, 'apprendre/fiches/fr-lire-consigne.html');
      // La synthèse vocale du navigateur est remplacée par un double : l'essai
      // vérifie l'enchaînement, la langue et les libellés, pas la voix réelle,
      // qu'aucun banc sans interface ne peut écouter.
      await page.evaluate(() => {
        window.__lus = [];
        const fausse = {
          speaking: false,
          pending: false,
          speak(e) {
            window.__lus.push({ texte: e.text, langue: e.lang });
            window.__courante = e;
            setTimeout(() => e.onend && e.onend(), 0);
          },
          cancel() {
            window.__annulations = (window.__annulations || 0) + 1;
            // Chromium signale une annulation volontaire par un `onerror`
            // « interrupted » : le double fait de même, pour vérifier que ce
            // n'est pas annoncé comme une panne.
            const courante = window.__courante;
            window.__courante = null;
            if (courante) setTimeout(() => courante.onerror && courante.onerror({ error: 'interrupted' }), 0);
          },
          pause() { window.__pauses = (window.__pauses || 0) + 1; },
          resume() { window.__reprises = (window.__reprises || 0) + 1; },
        };
        Object.defineProperty(window, 'speechSynthesis', { value: fausse, configurable: true });
      });

      const avant = await page.evaluate(() => ({
        requetes: performance.getEntriesByType('resource').length,
        lus: window.__lus.length,
      }));
      assert.equal(avant.lus, 0, 'rien ne doit être lu sans un geste explicite');

      await ouvrirPersonnalisation(page);
      const commande = await page.$eval('[data-read-aloud-toggle]', (element) => element.textContent.trim());
      assert.equal(commande, 'Lire à voix haute');

      await page.click('[data-read-aloud-toggle]');
      await page.waitForFunction(() => window.__lus.length > 5, { timeout: 15000 });
      const pendant = await page.evaluate(() => ({
        commande: document.querySelector('[data-read-aloud-toggle]').textContent.trim(),
        nomComplet: document.querySelector('[data-read-aloud-toggle]').getAttribute('aria-label'),
        largeurs: [...document.querySelectorAll('[data-read-aloud] button')]
          .filter((bouton) => !bouton.hidden)
          .map((bouton) => Math.round(bouton.getBoundingClientRect().height)),
        pause: document.querySelector('[data-read-aloud-pause]').hidden,
        marques: document.querySelectorAll('.lecture-en-cours').length,
        statut: document.querySelector('[data-read-aloud-status]').textContent,
      }));
      assert.equal(pendant.commande, 'Arrêter');
      assert.equal(pendant.nomComplet, 'Arrêter la lecture à voix haute');
      // Le texte visible doit rester contenu dans le nom accessible.
      assert.ok(pendant.nomComplet.includes(pendant.commande));
      assert.ok(
        pendant.largeurs.every((largeur) => largeur >= 32),
        `les deux commandes de lecture doivent rester cliquables : ${JSON.stringify(pendant.largeurs)}`
      );
      assert.equal(pendant.pause, false, 'la pause doit apparaître pendant la lecture');
      assert.equal(pendant.marques, 1, 'un seul bloc en cours de lecture doit être marqué');
      assert.match(pendant.statut, /Lecture à voix haute commencée/);

      await page.waitForFunction(() => document.querySelector('[data-read-aloud-status]').textContent.includes('terminée'), { timeout: 60000 });
      const apres = await page.evaluate(() => ({
        commande: document.querySelector('[data-read-aloud-toggle]').textContent.trim(),
        pause: document.querySelector('[data-read-aloud-pause]').hidden,
        marques: document.querySelectorAll('.lecture-en-cours').length,
        total: window.__lus.length,
        langues: [...new Set(window.__lus.map((entree) => entree.langue))],
        colles: window.__lus.filter((entree) => /[a-zà-ÿ]\.[A-ZÀ-Ý]/.test(entree.texte)).length,
        requetes: performance.getEntriesByType('resource').length,
        premier: window.__lus[0].texte,
      }));
      assert.equal(apres.commande, 'Lire à voix haute');
      assert.equal(apres.pause, true, 'la commande de pause disparaît quand la lecture est finie');
      assert.equal(apres.marques, 0, 'plus aucun bloc ne reste marqué');
      assert.ok(apres.total > 10, `la fiche doit produire plusieurs segments : ${apres.total}`);
      assert.deepEqual(apres.langues, ['fr']);
      assert.equal(apres.colles, 0, 'deux phrases mises en blocs ne doivent pas s’entendre collées');
      assert.equal(apres.requetes, avant.requetes, 'la lecture ne doit émettre aucune requête réseau');
      assert.ok(apres.premier.length > 0);

      // Arrêt net : le bouton coupe la voix et remet la commande à zéro.
      await page.click('[data-read-aloud-toggle]');
      await page.waitForFunction(() => document.querySelector('[data-read-aloud-status]').textContent.includes('commencée'), { timeout: 15000 });
      await page.click('[data-read-aloud-toggle]');
      await page.waitForFunction(() => document.querySelector('[data-read-aloud-status]').textContent.includes('arrêtée'), { timeout: 15000 });
      const arret = await page.evaluate(() => ({
        annulations: window.__annulations,
        marques: document.querySelectorAll('.lecture-en-cours').length,
        commande: document.querySelector('[data-read-aloud-toggle]').textContent.trim(),
        statut: document.querySelector('[data-read-aloud-status]').textContent,
      }));
      assert.ok(arret.annulations >= 1, 'arrêter doit annuler la synthèse en cours');
      assert.equal(arret.marques, 0);
      assert.equal(arret.commande, 'Lire à voix haute');
      // L'annulation déclenche un `onerror` « interrupted » : ce n'est pas une
      // panne, l'état ne doit pas basculer sur le message d'échec.
      assert.equal(arret.statut, 'Lecture arrêtée.');

      // La langue des répliques anglaises des Mondes est respectée.
      await ouvrirPageSite(page, 'anglais-aventure.html');
      await page.waitForSelector('[data-mission-id="gare"]');
      await page.click('[data-mission-id="gare"]');
      await page.waitForFunction(() => document.querySelector('#dialogue-line')?.textContent.trim().length > 0);
      await page.evaluate(() => {
        window.__lus = [];
        const fausse = {
          speak(e) {
            window.__lus.push({ texte: e.text, langue: e.lang });
            setTimeout(() => e.onend && e.onend(), 0);
          },
          cancel() {}, pause() {}, resume() {},
        };
        Object.defineProperty(window, 'speechSynthesis', { value: fausse, configurable: true });
      });
      await ouvrirPersonnalisation(page);
      await page.click('[data-read-aloud-toggle]');
      await page.waitForFunction(() => window.__lus.some((entree) => entree.langue === 'en'), { timeout: 60000 });
      const anglais = await page.evaluate(() => window.__lus.filter((entree) => entree.langue === 'en'));
      assert.ok(anglais.length >= 1);
      assert.match(anglais[0].texte, /^[A-Za-z]/);
      await page.click('[data-read-aloud-toggle]');
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

      await ouvrirPersonnalisation(page);
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
