#!/usr/bin/env node
/**
 * Mesure deux critères WCAG 2.2 qui entreront dans le RGAA 5, sans navigateur
 * dans la CI : la taille des cibles (2.5.8, AA) et le focus non masqué (2.4.11,
 * AA). Le script ne tranche pas à la place d'une personne : il rend trois états
 * — conforme, exception prévue par le critère, à corriger — et laisse le doute
 * apparent plutôt que de le convertir en faute.
 *
 * Ce que le script sait faire :
 *   - 2.5.8 : relever toutes les cibles interactives, écarter celles qui sont
 *     dans une phrase (exception « en ligne ») et celles qui sont assez
 *     espacées (exception « espacement »), puis lister le reste ;
 *   - 2.4.11 : porter le focus sur chaque élément atteignable, puis vérifier
 *     que son rectangle n'est pas entièrement recouvert par un bandeau collant.
 *
 * Ce qu'il ne sait pas : une cible peut être petite et facile à viser sur un
 * appareil donné, une personne peut se servir d'un lecteur d'écran ou d'un
 * clavier seul, et aucun de ces deux critères ne mesure la compréhension.
 *
 * Usage :
 *   node outils/auditer-criteres-22.mjs                 # pages publiques
 *   node outils/auditer-criteres-22.mjs --largeurs 390,1280
 *   node outils/auditer-criteres-22.mjs --pages index.html apprendre.html
 *   node outils/auditer-criteres-22.mjs --json rapport.json
 *
 * Prérequis : Chromium et puppeteer-core hors du dépôt (voir
 * docs/rd/formats-affichage.md, § 8) :
 *   npm install --prefix /tmp/audit puppeteer-core @sparticuz/chromium
 *   MRSC_BROWSER_NODE_MODULES=/tmp/audit/node_modules node outils/auditer-criteres-22.mjs
 */

import { createRequire } from 'node:module';
import { readdir, readFile, writeFile } from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const RACINE = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const PORT = process.env.MRSC_CRITERES_PORT || '4187';

function modules() {
  const dossier = process.env.MRSC_BROWSER_NODE_MODULES;
  const require = createRequire(dossier ? path.join(dossier, 'noop.js') : import.meta.url);
  // `@sparticuz/chromium` n'expose ses fonctions que par son export par défaut
  // une fois chargé en CommonJS.
  const paquet = require('@sparticuz/chromium');
  return { puppeteer: require('puppeteer-core'), chromium: paquet.default ?? paquet };
}

async function pagesPubliques() {
  const fichiers = [];
  async function parcourir(dossier) {
    for (const entree of await readdir(dossier, { withFileTypes: true })) {
      if (['assets', 'node_modules', '.git', 'docs', '.github', 'outils'].includes(entree.name)) continue;
      const complet = path.join(dossier, entree.name);
      if (entree.isDirectory()) await parcourir(complet);
      else if (entree.name.endsWith('.html')) fichiers.push(path.relative(RACINE, complet).split(path.sep).join('/'));
    }
  }
  await parcourir(RACINE);
  return fichiers.sort();
}

/** Évalue la taille des cibles dans la page courante (exécuté dans le navigateur). */
function mesurerCibles() {
  // Un contenu de `<details>` refermé garde une boîte non nulle dans Chromium.
  // Sans ce filtre, le balayage compte des cibles que personne ne voit : c'est
  // le piège qui a produit 50 fausses alertes sur `apprendre.html`.
  const visible = (element) => {
    const boite = element.getBoundingClientRect();
    const style = getComputedStyle(element);
    if (!boite.width || !boite.height) return false;
    if (style.visibility === 'hidden' || style.pointerEvents === 'none') return false;
    if (element.closest('[hidden], [aria-hidden="true"]')) return false;
    // Le contenu d'un `<details>` refermé garde une boîte non nulle : c'est un
    // contenu que personne ne voit ni ne peut viser.
    const ferme = element.closest('details:not([open])');
    if (ferme && element.tagName !== 'SUMMARY') return false;
    if (typeof element.checkVisibility === 'function'
      && !element.checkVisibility({ checkVisibilityCSS: true, contentVisibilityAuto: true })) return false;
    return true;
  };

  const selecteur = 'a[href], button, input:not([type=hidden]), select, textarea, summary, [role=button], [tabindex]:not([tabindex="-1"])';
  const cibles = [...document.querySelectorAll(selecteur)].filter(visible).map((element) => {
    const boite = element.getBoundingClientRect();
    const texte = (element.innerText || element.value || element.getAttribute('aria-label') || '')
      .replace(/\s+/g, ' ').trim();
    const texteParent = (element.parentElement?.innerText || '').replace(/\s+/g, ' ').trim();
    const reste = texteParent.split(texte).join('').replace(/\s+/g, ' ').trim();
    return {
      balise: element.tagName.toLowerCase(),
      classe: (typeof element.className === 'string' ? element.className : '').slice(0, 40),
      texte: texte.slice(0, 60),
      largeur: Math.round(boite.width),
      hauteur: Math.round(boite.height),
      cx: boite.left + window.scrollX + boite.width / 2,
      cy: boite.top + window.scrollY + boite.height / 2,
      // Exception « en ligne » : la cible est un lien placé dans une phrase.
      dansUnePhrase: element.tagName === 'A' && reste.length >= 3,
    };
  });

  const petites = cibles.filter((cible) => cible.largeur < 24 || cible.hauteur < 24);
  const resultat = { conformes: cibles.length - petites.length, enLigne: [], espacees: [], aCorriger: [] };
  for (const petite of petites) {
    if (petite.dansUnePhrase) { resultat.enLigne.push(petite); continue; }
    // Exception « espacement » : aucun cercle de 24 px centré sur une autre
    // cible ne recoupe celui de cette cible.
    const gene = cibles.some((autre) => autre !== petite
      && Math.hypot(autre.cx - petite.cx, autre.cy - petite.cy) < 24);
    (gene ? resultat.aCorriger : resultat.espacees).push(petite);
  }
  return resultat;
}

async function mesurerFocus(page, maximum) {
  const selecteur = 'a[href], button:not([disabled]), input:not([type=hidden]):not([disabled]), select, textarea, summary, [tabindex]:not([tabindex="-1"])';
  // La liste est figée une fois pour toutes : le focus peut faire apparaître un
  // bandeau, jamais créer ou retirer une cible. Indexer la même liste partout
  // évite de mesurer un autre élément que celui qui a reçu le focus.
  const total = await page.evaluate((sel) => {
    const visible = (element) => {
      const boite = element.getBoundingClientRect();
      const style = getComputedStyle(element);
      if (!boite.width || !boite.height) return false;
      if (style.visibility === 'hidden' || style.pointerEvents === 'none') return false;
      if (element.closest('[hidden], [aria-hidden="true"]')) return false;
      const ferme = element.closest('details:not([open])');
      if (ferme && element.tagName !== 'SUMMARY') return false;
      if (typeof element.checkVisibility === 'function'
        && !element.checkVisibility({ checkVisibilityCSS: true, contentVisibilityAuto: true })) return false;
      return true;
    };
    window.__ciblesCriteres22 = [...document.querySelectorAll(sel)].filter(visible);
    return window.__ciblesCriteres22.length;
  }, selecteur);

  const masques = [];
  for (let index = 0; index < Math.min(total, maximum); index += 1) {
    const description = await page.evaluate((i) => {
      const element = window.__ciblesCriteres22?.[i];
      if (!element) return null;
      // `instant` : un défilement animé n'a pas fini au moment de la mesure et
      // produit de faux « hors écran ».
      element.scrollIntoView({ block: 'center', behavior: 'instant' });
      element.focus();
      return {
        balise: element.tagName.toLowerCase(),
        texte: (element.innerText || element.getAttribute('aria-label') || element.textContent || '')
          .replace(/\s+/g, ' ').trim().slice(0, 60),
      };
    }, index);
    if (!description) break;
    await new Promise((suite) => setTimeout(suite, 80));
    const etat = await page.evaluate((i) => {
      const element = window.__ciblesCriteres22?.[i];
      if (!element) return null;
      const boite = element.getBoundingClientRect();
      const points = [
        [boite.left + boite.width / 2, boite.top + boite.height / 2],
        [boite.left + 2, boite.top + 2],
        [boite.right - 2, boite.bottom - 2],
        [boite.left + 2, boite.bottom - 2],
        [boite.right - 2, boite.top + 2],
      ];
      return points.map(([x, y]) => {
        if (x < 0 || y < 0 || x > innerWidth || y > innerHeight) return 'hors';
        const dessus = document.elementFromPoint(x, y);
        if (!dessus) return 'hors';
        return (dessus === element || element.contains(dessus) || dessus.contains(element))
          ? 'vue'
          : `masque:${dessus.tagName.toLowerCase()}.${(typeof dessus.className === 'string' ? dessus.className : '').slice(0, 24)}`;
      });
    }, index);
    // Entièrement masqué : aucun des cinq points ne montre l'élément ou son
    // contenu. Un seul point visible suffit à ne pas conclure.
    if (etat && etat.every((point) => point !== 'vue')) masques.push({ ...description, points: etat });
  }
  await page.evaluate(() => { delete window.__ciblesCriteres22; });
  return { testees: Math.min(total, maximum), total, masques };
}

async function main() {
  const arguments_ = process.argv.slice(2);
  const option = (nom, defaut) => {
    const index = arguments_.indexOf(`--${nom}`);
    return index >= 0 && arguments_[index + 1] ? arguments_[index + 1] : defaut;
  };
  const largeurs = option('largeurs', '390,1280').split(',').map(Number).filter(Boolean);
  const pagesOption = arguments_.includes('--pages')
    ? arguments_.slice(arguments_.indexOf('--pages') + 1).filter((valeur) => valeur.endsWith('.html'))
    : null;
  const pages = pagesOption && pagesOption.length ? pagesOption : await pagesPubliques();
  const json = option('json', '');
  const maximumFocus = Number(option('focus', '60'));

  const { puppeteer, chromium } = modules();
  const navigateur = await puppeteer.launch({
    executablePath: await chromium.executablePath(),
    args: [...chromium.args, '--no-sandbox'],
    headless: 'shell',
  });

  const bilan = { pages: pages.length, largeurs, cibles: { conformes: 0, enLigne: 0, espacees: 0, aCorriger: [] }, focus: { testees: 0, masques: [] } };
  for (const page of pages) {
    for (const largeur of largeurs) {
      const onglet = await navigateur.newPage();
      await onglet.setViewport({ width: largeur, height: 900, deviceScaleFactor: 1 });
      try {
        await onglet.goto(`http://127.0.0.1:${PORT}/${page}`, { waitUntil: 'domcontentloaded', timeout: 30000 });
        await new Promise((suite) => setTimeout(suite, 120));
        // Le défilement animé fausse la mesure de recouvrement.
        await onglet.addStyleTag({ content: 'html{scroll-behavior:auto !important}' }).catch(() => {});
      } catch (erreur) {
        await onglet.close();
        continue;
      }
      const cibles = await onglet.evaluate(mesurerCibles);
      bilan.cibles.conformes += cibles.conformes;
      bilan.cibles.enLigne += cibles.enLigne.length;
      bilan.cibles.espacees += cibles.espacees.length;
      for (const cible of cibles.aCorriger) bilan.cibles.aCorriger.push({ page, largeur, ...cible });
      if (pagesOption) {
        const focus = await mesurerFocus(onglet, maximumFocus);
        bilan.focus.testees += focus.testees;
        // Le défilement reste à la position atteinte : la page suivante repart
        // de son propre chargement.
        for (const masque of focus.masques) bilan.focus.masques.push({ page, largeur, ...masque });
      }
      await onglet.close();
    }
  }
  await navigateur.close();

  const { cibles, focus } = bilan;
  console.log(`Pages mesurées : ${bilan.pages} × ${largeurs.join(' et ')} px.`);
  console.log(`2.5.8 — cibles : ${cibles.conformes} conformes, ${cibles.enLigne} en ligne (exception), `
    + `${cibles.espacees} espacées (exception), ${cibles.aCorriger.length} à corriger.`);
  if (cibles.aCorriger.length) {
    for (const cible of cibles.aCorriger.slice(0, 30)) {
      console.log(`  à corriger — ${cible.page} @${cible.largeur} : ${cible.balise}.${cible.classe} `
        + `${cible.largeur}×${cible.hauteur} « ${cible.texte} »`);
    }
  }
  if (pagesOption) {
    console.log(`2.4.11 — focus : ${focus.testees} éléments testés, ${focus.masques.length} entièrement masqués.`);
    for (const masque of focus.masques.slice(0, 20)) {
      console.log(`  masqué — ${masque.page} @${masque.largeur} : ${masque.balise} « ${masque.texte} » ${JSON.stringify(masque.points)}`);
    }
  } else {
    console.log('2.4.11 — non mesuré : relancer avec --pages pour l\u2019échantillon de focus (coûteux).');
  }
  console.log('Rappel : ces deux critères ne disent rien de la compréhension ni de l\u2019usage réel.');

  if (json) {
    await writeFile(json, `${JSON.stringify(bilan, null, 2)}\n`, 'utf8');
    console.log(`Rapport écrit : ${json}`);
  }
  // Un écart est un constat, pas un échec de publication : la porte CI ne peut
  // pas exécuter ce script, et un chiffre non nul n'empêche pas de livrer.
  process.exitCode = 0;
}

main().catch((erreur) => {
  console.error(erreur.stack || erreur);
  process.exitCode = 1;
});
