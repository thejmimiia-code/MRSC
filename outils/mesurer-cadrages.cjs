#!/usr/bin/env node
'use strict';
// Mesure, dans un vrai navigateur, le dessin de chaque page **dans chaque
// cadrage personnalisé** : six présentations × cinq crans de texte × quatre
// largeurs. Quatre choses sont relevées, et une seule suffit au contrôle :
//
//   - le débordement horizontal du document, en pixels (tolérance 0,5 px) ;
//   - le nombre de colonnes de chaque grille déclarée ;
//   - le **texte coupé** : un mot dont la boîte sort de la zone de découpe d'un
//     ancêtre en `overflow: hidden` ou `clip` ;
//   - les **cartes qui se chevauchent** dans une grille déclarée.
//
// Le texte coupé se compte sur les nœuds de texte, pas sur `scrollHeight` : un
// conteneur dont un enfant **décoratif** déborde est légitime et n'efface aucun
// mot. Le 2 novembre 2026, la mesure grossière accusait 51 fois pour zéro mot
// réellement coupé — c'est la version précise qui a été gardée.
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
  // Une rangée incomplète n'est pas une faute en soi : c'est un fait de dessin
  // (« cinq cartes en deux colonnes laissent une carte seule »). Le relevé le
  // compte, `cadrages.py --orphelins` le nomme, et la décision reste humaine.
  const rangees = {};
  for (const selecteur of selecteurs) {
    const elements = Array.from(document.querySelectorAll(selecteur));
    const element = elements.find((candidat) => {
      const style = getComputedStyle(candidat);
      return style.display !== 'none' && candidat.getBoundingClientRect().width > 0;
    });
    if (!element) continue;
    const style = getComputedStyle(element);
    const enfants = Array.from(element.children).filter(
      (enfant) => getComputedStyle(enfant).display !== 'none' && enfant.getBoundingClientRect().width > 0
    );
    if (enfants.length > 0 && (style.display === 'grid' || style.display === 'inline-grid' || style.display === 'flex')) {
      const boite = element.getBoundingClientRect();
      const interieur = boite.left + element.clientLeft;
      const largeurUtile = element.clientWidth;
      const ecart = parseFloat(style.columnGap) || 0;
      // Les cartes d'une même rangée partagent leur bord haut, à l'arrondi près.
      const parRangee = new Map();
      for (const enfant of enfants) {
        const rect = enfant.getBoundingClientRect();
        const cle = Math.round(rect.top);
        if (!parRangee.has(cle)) parRangee.set(cle, []);
        parRangee.get(cle).push(rect);
      }
      const hauts = Array.from(parRangee.keys()).sort((a, b) => a - b);
      const derniere = parRangee.get(hauts[hauts.length - 1]) || [];
      const occupe = derniere.reduce((total, rect) => total + rect.width, 0);
      const manque = Math.max(0, largeurUtile - occupe - ecart * Math.max(0, derniere.length - 1));
      rangees[selecteur] = {
        cartes: enfants.length,
        rangees: hauts.length,
        cartes_derniere_rangee: derniere.length,
        manque: Math.round(manque * 100) / 100,
        interieur: Math.round(interieur * 100) / 100,
      };
    }
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
  // Un conteneur qui découpe et dont un enfant décoratif dépasse est légitime :
  // ce sont les **mots** qui doivent rester lisibles, pas les boîtes.
  const coupes = [];
  for (const element of document.querySelectorAll('body *')) {
    const style = getComputedStyle(element);
    const coupeX = style.overflowX === 'hidden' || style.overflowX === 'clip';
    const coupeY = style.overflowY === 'hidden' || style.overflowY === 'clip';
    if (!coupeX && !coupeY) continue;
    const boite = element.getBoundingClientRect();
    if (boite.width === 0 || boite.height === 0) continue;
    const gauche = boite.left + element.clientLeft;
    const haut = boite.top + element.clientTop;
    const droite = gauche + element.clientWidth;
    const bas = haut + element.clientHeight;
    const mots = document.createTreeWalker(element, NodeFilter.SHOW_TEXT);
    let noeud;
    let pire = 0;
    let extrait = '';
    while ((noeud = mots.nextNode())) {
      if (!noeud.textContent || !noeud.textContent.trim()) continue;
      const portee = noeud.parentElement;
      if (!portee || getComputedStyle(portee).display === 'none') continue;
      const rect = portee.getBoundingClientRect();
      if (rect.width === 0 || rect.height === 0) continue;
      const depasse = Math.max(
        coupeX ? rect.right - droite : 0,
        coupeX ? gauche - rect.left : 0,
        coupeY ? rect.bottom - bas : 0,
        coupeY ? haut - rect.top : 0
      );
      if (depasse > 0.5 && depasse > pire) {
        pire = depasse;
        extrait = noeud.textContent.trim().slice(0, 40);
      }
    }
    if (pire > 0) {
      coupes.push({
        tag: element.tagName.toLowerCase(),
        classe: String(element.className || '').slice(0, 60),
        depasse: Math.round(pire * 100) / 100,
        texte: extrait,
      });
    }
  }
  if (coupes.length > 8) coupes.length = 8;

  // Deux cartes d'une même grille ne doivent pas se recouvrir : un recouvrement
  // cache du contenu, et un contenu caché n'est pas un contenu présent.
  const chevauchements = [];
  for (const selecteur of selecteurs) {
    const grille = Array.from(document.querySelectorAll(selecteur)).find(
      (candidat) => candidat.getBoundingClientRect().width > 0
    );
    if (!grille) continue;
    const cartes = Array.from(grille.children)
      .filter((enfant) => getComputedStyle(enfant).display !== 'none')
      .slice(0, 60);
    for (let i = 0; i < cartes.length; i += 1) {
      for (let j = i + 1; j < cartes.length; j += 1) {
        const a = cartes[i].getBoundingClientRect();
        const b = cartes[j].getBoundingClientRect();
        if (a.width === 0 || a.height === 0 || b.width === 0 || b.height === 0) continue;
        const dx = Math.min(a.right, b.right) - Math.max(a.left, b.left);
        const dy = Math.min(a.bottom, b.bottom) - Math.max(a.top, b.top);
        if (dx > 0.5 && dy > 0.5) {
          chevauchements.push({
            selecteur,
            premiere: `${cartes[i].tagName.toLowerCase()}${cartes[i].className ? `.${String(cartes[i].className).split(' ')[0]}` : ''}`,
            seconde: `${cartes[j].tagName.toLowerCase()}${cartes[j].className ? `.${String(cartes[j].className).split(' ')[0]}` : ''}`,
            largeur: Math.round(dx * 100) / 100,
            hauteur: Math.round(dy * 100) / 100,
          });
        }
      }
    }
  }
  if (chevauchements.length > 8) chevauchements.length = 8;

  return { debordement, coupable, colonnes, rangees, coupes, chevauchements };
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
  const coupes = rapport.mesures.reduce((total, mesure) => total + (mesure.coupes || []).length, 0);
  const chevauchements = rapport.mesures.reduce(
    (total, mesure) => total + (mesure.chevauchements || []).length,
    0
  );
  console.log(
    `Cadrages mesurés : ${rapport.mesures.length} point(s) sur ${plan.combinaisons.length} attendu(s), ` +
      `${debordants} en débordement, ${coupes} texte(s) coupé(s), ${chevauchements} chevauchement(s), ` +
      `${rapport.erreurs.length} erreur(s) — rapport écrit dans ${destination}.`
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
