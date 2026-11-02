#!/usr/bin/env node
'use strict';
// Mesure, dans un vrai navigateur, le dessin de chaque page **dans chaque
// cadrage personnalisé** : six présentations × cinq crans de texte × quatre
// largeurs. Deux choses sont relevées, et une seule suffit au contrôle :
//
//   - le débordement horizontal du document, en pixels (tolérance 0,5 px) ;
//   - le nombre de colonnes de chaque grille déclarée.
//
// Ce script ne juge rien : il compte et il écrit. La comparaison au plan est le
// travail de `outils/cadrages.py --controler`, qui n'a pas besoin de navigateur
// et se laisse donc éprouver hors ligne.
//
// Codes de sortie :
//   0  tout a été mesuré
//   1  au moins un cadrage n'a pas pu être mesuré (page, sélecteur, affichage)
//   2  pas de navigateur, pas de modules, ou plan illisible — jamais vert
//
// Usage :
//   MRSC_BROWSER_NODE_MODULES=… node outils/mesurer-cadrages.cjs plan.json rapport.json

const fs = require('node:fs');
const path = require('node:path');

function sortir(code, message) {
  if (message) console.error(message);
  process.exit(code);
}

if (process.env.MRSC_BROWSER_NODE_MODULES) {
  process.env.NODE_PATH = process.env.MRSC_BROWSER_NODE_MODULES;
  require('node:module').Module._initPaths();
}

let puppeteer;
let chromium;
try {
  puppeteer = require('puppeteer-core');
  const pkg = require('@sparticuz/chromium');
  chromium = pkg.default || pkg;
} catch (erreur) {
  sortir(2, `Environnement : navigateur indisponible (${erreur.message}) — aucune mesure, aucun verdict.`);
}

const source = process.argv[2];
const destination = process.argv[3];
if (!source || !destination) {
  sortir(2, 'Usage : node outils/mesurer-cadrages.cjs <plan.json> <rapport.json>');
}

let plan;
try {
  plan = JSON.parse(fs.readFileSync(source, 'utf8'));
} catch (erreur) {
  sortir(2, `Plan illisible (${source}) : ${erreur.message}`);
}
if (!Array.isArray(plan.combinaisons) || plan.combinaisons.length === 0) {
  sortir(2, `Plan vide (${source}) : aucun cadrage à confronter.`);
}

const base = process.env.MRSC_TEST_URL || 'http://127.0.0.1:4183/';

// Le nombre de colonnes se compte dans le document, pas dans la prédiction : si
// la feuille servie contredit le modèle sur la forme elle-même, c'est un fait à
// rapporter, pas à contourner.
function mesurer(selecteurs) {
  const racine = document.documentElement;
  const debordement = Math.round((racine.scrollWidth - racine.clientWidth) * 100) / 100;
  let coupable = null;
  if (debordement > 0) {
    for (const element of document.querySelectorAll('body *')) {
      const boite = element.getBoundingClientRect();
      if (boite.width === 0 || boite.height === 0) continue;
      const depasse = Math.round((boite.right - racine.clientWidth) * 100) / 100;
      if (depasse > 0.5 && (!coupable || depasse > coupable.depasse)) {
        coupable = {
          depasse,
          tag: element.tagName.toLowerCase(),
          classe: String(element.className || '').slice(0, 60),
        };
      }
    }
  }
  const colonnes = {};
  for (const selecteur of selecteurs) {
    const elements = Array.from(document.querySelectorAll(selecteur));
    const element = elements.find((candidat) => {
      const style = getComputedStyle(candidat);
      return style.display !== 'none' && candidat.getBoundingClientRect().width > 0;
    });
    if (!element) continue;
    const style = getComputedStyle(element);
    if (style.display === 'grid' || style.display === 'inline-grid') {
      // Une piste repliée par `auto-fit` vaut 0 px : elle ne compte pas.
      const pistes = (style.gridTemplateColumns || '').trim().split(/\s+(?![^(]*\))/);
      colonnes[selecteur] = pistes.filter((piste) => parseFloat(piste) > 0.5).length;
    } else if (style.display === 'flex' || style.display === 'inline-flex') {
      const enfants = Array.from(element.children).filter(
        (enfant) => getComputedStyle(enfant).display !== 'none'
      );
      if (enfants.length === 0) continue;
      let compte = enfants.length;
      let precedent = null;
      for (let i = 0; i < enfants.length; i += 1) {
        const rect = enfants[i].getBoundingClientRect();
        if (precedent !== null && rect.left <= precedent + 1) {
          compte = i;
          break;
        }
        precedent = rect.left;
      }
      colonnes[selecteur] = compte;
    }
  }
  return { debordement, coupable, colonnes };
}

(async () => {
  let browser;
  try {
    browser = await puppeteer.launch({
      executablePath: await chromium.executablePath(),
      args: chromium.args,
      headless: true,
    });
  } catch (erreur) {
    sortir(2, `Environnement : lancement du navigateur impossible (${erreur.message}) — aucune mesure.`);
  }

  const rapport = { navigateur: null, base, source, mesures: [], erreurs: [] };
  try {
    rapport.navigateur = await browser.version();
    // Un état de page = (page, présentation, cran). On change de largeur sans
    // recharger : la mise en page se recalcule. Les combinaisons d'un même état
    // ne coûtent donc qu'un chargement, et le nombre de chargements vaut le
    // nombre d'états — jamais celui des combinaisons.
    const parEtat = new Map();
    for (const combinaison of plan.combinaisons) {
      const cle = `${combinaison.page}|${combinaison.layout || ''}|${combinaison.cran}`;
      if (!parEtat.has(cle)) parEtat.set(cle, { ...combinaison, largeurs: [] });
      if (!parEtat.get(cle).largeurs.includes(combinaison.largeur)) {
        parEtat.get(cle).largeurs.push(combinaison.largeur);
      }
    }

    for (const etat of parEtat.values()) {
      const page = await browser.newPage();
      try {
        await page.goto(new URL(etat.page, base).href, { waitUntil: 'networkidle0' });
      } catch (erreur) {
        rapport.erreurs.push({ page: etat.page, raison: `page injoignable : ${erreur.message}` });
        await page.close();
        continue;
      }
      await page.addStyleTag({ content: '* { animation: none !important; transition: none !important; }' });
      await page.evaluate(
        (layout, echelle) => {
          const racine = document.documentElement;
          [
            'texte-tres-reduit',
            'texte-reduit',
            'texte-agrandi',
            'texte-tres-agrandi',
          ].forEach((classe) => racine.classList.remove(classe));
          const classe = {
            0.75: 'texte-tres-reduit',
            0.85: 'texte-reduit',
            1.15: 'texte-agrandi',
            1.3: 'texte-tres-agrandi',
          }[String(echelle)];
          if (classe) racine.classList.add(classe);
          if (layout) racine.dataset.layout = layout;
          else delete racine.dataset.layout;
        },
        etat.layout,
        etat.echelle
      );

      const selecteurs = (plan.grilles || {})[etat.page] || [];
      for (const largeur of etat.largeurs.sort((a, b) => a - b)) {
        // Un ascenseur vertical retire de la largeur utile : la fenêtre est
        // élargie de ce que le document perd, jusqu'à ce que la largeur cliente
        // vaille exactement la largeur demandée. Sans cela, chaque mesure serait
        // décalée de la largeur de l'ascenseur et le contrôle accuserait la
        // feuille d'un décalage de navigateur.
        let fenetre = largeur;
        for (let essai = 0; essai < 3; essai += 1) {
          await page.setViewport({ width: fenetre, height: 900, deviceScaleFactor: 1 });
          const cliente = await page.evaluate(() => document.documentElement.clientWidth);
          if (cliente === largeur) break;
          fenetre += largeur - cliente;
        }
        let resultat;
        try {
          resultat = await page.evaluate(mesurer, selecteurs);
        } catch (erreur) {
          rapport.erreurs.push({
            page: etat.page,
            layout: etat.layout,
            cran: etat.cran,
            largeur,
            raison: `évaluation impossible : ${erreur.message}`,
          });
          continue;
        }
        rapport.mesures.push({
          page: etat.page,
          layout: etat.layout,
          cran: etat.cran,
          echelle: etat.echelle,
          largeur,
          ...resultat,
        });
      }
      await page.close();
    }
  } catch (erreur) {
    await browser.close().catch(() => {});
    sortir(2, `Environnement : la mesure s'est interrompue (${erreur.message}) — rapport partiel non écrit.`);
  }
  await browser.close().catch(() => {});

  fs.mkdirSync(path.dirname(path.resolve(destination)), { recursive: true });
  fs.writeFileSync(destination, `${JSON.stringify(rapport, null, 1)}\n`);

  const debordants = rapport.mesures.filter((mesure) => (mesure.debordement || 0) > 0).length;
  console.log(
    `Cadrages mesurés : ${rapport.mesures.length} point(s) sur ${plan.combinaisons.length} attendu(s), ` +
      `${debordants} en débordement, ${rapport.erreurs.length} erreur(s) — rapport écrit dans ${destination}.`
  );
  if (rapport.erreurs.length) {
    for (const erreur of rapport.erreurs.slice(0, 20)) {
      console.error(
        `  ! ${erreur.page}${erreur.layout ? ` · ${erreur.layout}` : ''}` +
          (erreur.largeur ? ` à ${erreur.largeur} px` : '') +
          ` : ${erreur.raison}`
      );
    }
    process.exit(1);
  }
  process.exit(0);
})();
