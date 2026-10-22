#!/usr/bin/env node
/**
 * Mesure d'affichage, tous formats, dans un vrai Chromium sans interface.
 *
 * Outil **facultatif**, hors de la chaîne d'intégration : il demande un
 * navigateur, que la CI n'installe pas. La porte automatique correspondante est
 * `outils/verifier-affichages.py`, qui vérifie les mêmes appuis sans navigateur.
 *
 * Préparation :
 *
 *     npm init -y
 *     npm install @sparticuz/chromium puppeteer-core
 *     python3 outils/serveur-local.py --port 4180 --bind 127.0.0.1
 *
 * Puis, dans un autre terminal :
 *
 *     node outils/auditer-affichages.mjs
 *
 * Sur une machine où Chromium est fourni par le système, `@sparticuz/chromium`
 * et la variable `LD_LIBRARY_PATH` ne sont pas nécessaires : passer le chemin
 * du binaire suffit.
 *
 * Ce que la mesure contrôle, par page et par format :
 *
 * - défilement latéral de la page ;
 * - élément qui sort du cadre ;
 * - texte dont le corps descend sous 12 px ;
 * - cible tactile sous 24 × 24 px (WCAG 2.2, 2.5.8) ;
 * - image agrandie par le navigateur, comparée à la largeur réelle du fichier ;
 * - texte rogné par `overflow: hidden`.
 */

import { readdirSync, writeFileSync } from 'node:fs';
import { execFileSync } from 'node:child_process';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const RACINE = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const BASE = process.env.BASE_URL || 'http://127.0.0.1:4180';
const RAPPORT = process.env.RAPPORT || '/tmp/audit-affichages.json';

let chromium;
let puppeteer;
try {
  chromium = (await import('@sparticuz/chromium')).default;
  puppeteer = (await import('puppeteer-core')).default;
} catch (erreur) {
  console.error(
    'Chromium et puppeteer-core sont requis : npm install @sparticuz/chromium puppeteer-core'
  );
  process.exit(2);
}

const PAGES = [
  'index.html', 'apprendre.html', 'anglais-aventure.html', 'eva.html',
  'ia-societe.html', 'documents.html', 'simulateur.html', 'localisation.html',
  'liens-utiles.html', 'nous-contacter.html', 'transparence.html',
  'confidentialite.html', '404.html',
];

/** nom, largeur CSS, hauteur CSS, densité, tactile */
const FORMATS = [
  ['pliable 280', 280, 653, 3, true],
  ['tel 320', 320, 568, 2, true],
  ['tel 360', 360, 640, 3, true],
  ['tel 390', 390, 844, 3, true],
  ['tel 414', 414, 896, 2, true],
  ['tel 430', 430, 932, 3, true],
  ['tel paysage 568', 568, 320, 2, true],
  ['tel paysage 844', 844, 390, 3, true],
  ['tablette 768', 768, 1024, 2, true],
  ['tablette 820', 820, 1180, 2, true],
  ['tablette paysage 1024', 1024, 768, 2, true],
  ['portable 1280', 1280, 720, 1, false],
  ['portable 1366', 1366, 768, 1, false],
  ['portable 1440', 1440, 900, 2, false],
  ['bureau 1680', 1680, 1050, 1, false],
  ['bureau 1920', 1920, 1080, 1, false],
  ['qhd 2560', 2560, 1440, 1, false],
  ['ultra-large 3440', 3440, 1440, 1, false],
  ['4k 3840', 3840, 2160, 1, false],
];

/** nom, préférences enregistrées par les réglages d'affichage du site */
const MODES = [
  ['équilibrée', {}],
  ['lecture', { 'mrsc-mise-en-page': 'lecture' }],
  ['vitrine', { 'mrsc-mise-en-page': 'vitrine' }],
  ['mosaïque', { 'mrsc-mise-en-page': 'mosaique' }],
  ['panorama', { 'mrsc-mise-en-page': 'panorama' }],
  ['compacte', { 'mrsc-mise-en-page': 'compacte' }],
  ['texte 150 %', { 'mrsc-texte-niveau': '150' }],
  ['texte 50 %', { 'mrsc-texte-niveau': '50' }],
  ['contraste renforcé', { 'mrsc-contraste-renforce': 'oui' }],
  ['espacement renforcé', { 'mrsc-espacement-renforce': 'oui' }],
];

function largeursReelles() {
  // La vérification de netteté compare l'affichage à la largeur réelle du
  // fichier : `naturalWidth` est corrigé par la densité dès qu'un `srcset` en
  // `w` est présent, et ne peut donc pas servir de référence.
  const dossier = path.join(RACINE, 'assets', 'images');
  const largeurs = {};
  for (const nom of readdirSync(dossier)) {
    try {
      largeurs[nom] = Number(
        execFileSync('convert', [path.join(dossier, nom), '-format', '%w', 'info:'], {
          encoding: 'utf8',
        }).trim()
      );
    } catch (erreur) {
      largeurs[nom] = 0;
    }
  }
  return largeurs;
}

const browser = await puppeteer.launch({
  args: [...chromium.args, '--force-color-profile=srgb'],
  executablePath: await chromium.executablePath(),
  headless: true,
});

const LARGEURS = largeursReelles();
const resultats = [];

for (const [mode, preferences] of MODES) {
  for (const page of PAGES) {
    for (const [nom, largeur, hauteur, densite, tactile] of FORMATS) {
      const onglet = await browser.newPage();
      await onglet.setViewport({
        width: largeur,
        height: hauteur,
        deviceScaleFactor: densite,
        isMobile: tactile,
        hasTouch: tactile,
      });
      await onglet.evaluateOnNewDocument((prefs) => {
        try {
          localStorage.clear();
          for (const [cle, valeur] of Object.entries(prefs)) localStorage.setItem(cle, valeur);
        } catch (erreur) {
          // stockage bloqué : le mode par défaut s'applique
        }
      }, preferences);
      await onglet.goto(`${BASE}/${page}`, { waitUntil: 'load', timeout: 30000 });
      await onglet.evaluate(() => document.fonts.ready);
      await new Promise((suite) => setTimeout(suite, 120));

      const mesure = await onglet.evaluate((largeurVue, densiteVue, largeursFichiers) => {
        const racine = document.documentElement;
        const dehors = [];
        const texteFin = [];
        const ciblesPetites = [];
        const imagesAgrandies = [];
        const textesCoupes = [];

        const visible = (element) => {
          const style = getComputedStyle(element);
          if (style.display === 'none' || style.visibility === 'hidden' || Number(style.opacity) === 0) {
            return false;
          }
          const boite = element.getBoundingClientRect();
          return !(boite.width === 0 && boite.height === 0);
        };
        const dansDefilement = (element) => {
          for (let parent = element.parentElement; parent; parent = parent.parentElement) {
            if (['auto', 'scroll'].includes(getComputedStyle(parent).overflowX)) return true;
          }
          return false;
        };
        const nommer = (element) =>
          element.tagName.toLowerCase() +
          (typeof element.className === 'string' && element.className
            ? '.' + element.className.trim().split(/\s+/).slice(0, 2).join('.')
            : '');

        for (const element of document.body.querySelectorAll('*')) {
          if (!visible(element)) continue;
          const boite = element.getBoundingClientRect();
          const style = getComputedStyle(element);

          if (!dansDefilement(element) && style.position !== 'fixed' &&
              (boite.right > largeurVue + 1 || boite.left < -1)) {
            dehors.push({ selecteur: nommer(element), gauche: Math.round(boite.left), droite: Math.round(boite.right) });
          }

          const corps = parseFloat(style.fontSize);
          const texte = (element.textContent || '').trim();
          if (texte && element.children.length === 0 && corps < 12 && style.position !== 'fixed') {
            texteFin.push({ selecteur: nommer(element), corps });
          }

          if (element.tagName === 'IMG' && element.naturalWidth > 0) {
            const fichier = decodeURIComponent((element.currentSrc || element.src || '').split('/').pop());
            const reelle = largeursFichiers[fichier] || 0;
            const besoin = Math.round(boite.width * densiteVue);
            if (reelle && besoin > reelle + 1) {
              imagesAgrandies.push({ fichier, reelle, besoin, facteur: +(besoin / reelle).toFixed(2) });
            }
          }

          if (element.children.length === 0 && !element.closest('.visually-hidden') &&
              element.scrollWidth > element.clientWidth + 2 &&
              ['hidden', 'clip'].includes(style.overflowX) && texte) {
            textesCoupes.push({ selecteur: nommer(element), visible: element.clientWidth, reel: element.scrollWidth });
          }
        }

        for (const element of document.body.querySelectorAll('a, button, input, select, summary, [role="button"]')) {
          if (!visible(element)) continue;
          const style = getComputedStyle(element);
          if (style.display === 'inline' && element.tagName === 'A') continue; // exempté par WCAG 2.5.8
          const boite = element.getBoundingClientRect();
          if (boite.height < 23.9 || boite.width < 23.9) {
            ciblesPetites.push({ selecteur: nommer(element), largeur: Math.round(boite.width), hauteur: Math.round(boite.height) });
          }
        }

        const uniques = (liste) => {
          const vues = new Set();
          const sortie = [];
          for (const entree of liste) {
            const cle = JSON.stringify(entree);
            if (!vues.has(cle)) {
              vues.add(cle);
              sortie.push(entree);
            }
          }
          return sortie.slice(0, 8);
        };

        return {
          defilementHorizontal: racine.scrollWidth - racine.clientWidth,
          dehors: uniques(dehors), nbDehors: dehors.length,
          texteFin: uniques(texteFin), nbTexteFin: texteFin.length,
          ciblesPetites: uniques(ciblesPetites), nbCiblesPetites: ciblesPetites.length,
          imagesAgrandies: uniques(imagesAgrandies), nbImagesAgrandies: imagesAgrandies.length,
          textesCoupes: uniques(textesCoupes), nbTextesCoupes: textesCoupes.length,
        };
      }, largeur, densite, LARGEURS);

      resultats.push({ mode, page, format: nom, largeur, ...mesure });
      await onglet.close();
    }
    process.stderr.write(`· ${mode} / ${page}\n`);
  }
}

await browser.close();
writeFileSync(RAPPORT, JSON.stringify(resultats, null, 1));

const defauts = resultats.filter((mesure) =>
  mesure.defilementHorizontal > 1 || mesure.nbDehors || mesure.nbTexteFin ||
  mesure.nbImagesAgrandies || mesure.nbTextesCoupes || mesure.nbCiblesPetites
);
console.log(`\n${resultats.length} mesures · ${defauts.length} avec défaut`);
for (const mesure of defauts) {
  const details = [];
  if (mesure.defilementHorizontal > 1) details.push(`débordement ${mesure.defilementHorizontal}px`);
  if (mesure.nbDehors) details.push(`${mesure.nbDehors} hors cadre`);
  if (mesure.nbTexteFin) details.push(`${mesure.nbTexteFin} texte<12px`);
  if (mesure.nbImagesAgrandies) details.push(`${mesure.nbImagesAgrandies} image agrandie`);
  if (mesure.nbTextesCoupes) details.push(`${mesure.nbTextesCoupes} texte rogné`);
  if (mesure.nbCiblesPetites) details.push(`${mesure.nbCiblesPetites} cible<24px`);
  console.log(`${mesure.mode} / ${mesure.page} @ ${mesure.format} :: ${details.join(' | ')}`);
}
process.exit(defauts.length ? 1 : 0);
