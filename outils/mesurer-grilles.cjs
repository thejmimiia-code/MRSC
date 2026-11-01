#!/usr/bin/env node
'use strict';
// Mesure, dans un vrai navigateur, le nombre de colonnes des grilles que
// `outils/modele-grilles.py` prétend connaître.
//
// Le 1er novembre 2026, trois grilles converties la veille changeaient de
// nombre de colonnes à 761 px. Le modèle ne pouvait pas le voir : il vérifiait
// sa propre arithmétique. Ce script ne calcule rien — il compte. Il lit la
// prédiction écrite par `modele-grilles.py --releve-json`, la rejoue sur les
// pages réelles, et écrit ce qu'il a vu.
//
// Ce qu'il ne fait pas : il ne juge pas. La comparaison est le travail de
// `outils/rapporter-mesure-grilles.py`, qui n'a pas besoin d'un navigateur et
// se laisse donc éprouver hors ligne.
//
// Codes de sortie :
//   0  tout a été mesuré
//   1  au moins un point n'a pas pu être mesuré (page, sélecteur ou affichage)
//   2  pas de navigateur, pas de modules, ou prédiction illisible — jamais vert
//
// Usage :
//   MRSC_BROWSER_NODE_MODULES=… node outils/mesurer-grilles.cjs releve.json rapport.json

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
  sortir(2, 'Usage : node outils/mesurer-grilles.cjs <prediction.json> <rapport.json>');
}

let prediction;
try {
  prediction = JSON.parse(fs.readFileSync(source, 'utf8'));
} catch (erreur) {
  sortir(2, `Prédiction illisible (${source}) : ${erreur.message}`);
}
if (!Array.isArray(prediction.grilles) || prediction.grilles.length === 0) {
  sortir(2, `Prédiction vide (${source}) : aucune grille à confronter.`);
}

const base = process.env.MRSC_TEST_URL || 'http://127.0.0.1:4181/';

// Le nombre de colonnes se compte différemment selon la forme, et le script le
// lit dans le document plutôt que dans la prédiction : si la feuille servie
// contredit le modèle sur la forme elle-même, c'est un fait à rapporter, pas à
// contourner.
function compter(selecteur) {
  const elements = Array.from(document.querySelectorAll(selecteur));
  const element = elements.find((candidat) => {
    const style = getComputedStyle(candidat);
    return style.display !== 'none' && candidat.getBoundingClientRect().width > 0;
  });
  if (!element) {
    return { trouve: false, raison: elements.length ? 'élément sans largeur affichée' : 'élément absent de la page' };
  }
  const style = getComputedStyle(element);
  const boite = element.getBoundingClientRect();
  // `largeur_element` et non `largeur` : la largeur de la fenêtre est déjà
  // écrite dans l'entrée, et une clé qui s'écrase en silence faisait comparer
  // deux largeurs différentes sous le même nom.
  const base = { trouve: true, display: style.display, largeur_element: Math.round(boite.width * 100) / 100 };

  if (style.display === 'grid' || style.display === 'inline-grid') {
    // Une piste repliée par `auto-fit` vaut 0 px : elle ne compte pas comme
    // colonne, sans quoi une grille de deux cartes sur quatre pistes serait
    // dite « quatre colonnes ».
    const pistes = (style.gridTemplateColumns || '').trim().split(/\s+(?![^(]*\))/);
    const visibles = pistes.filter((piste) => parseFloat(piste) > 0.5);
    return { ...base, colonnes: visibles.length, pistes: visibles.length };
  }

  if (style.display === 'flex' || style.display === 'inline-flex') {
    // Une colonne est une rangée qui a commencé. On repère le retour à la ligne
    // par la position horizontale : dans une rangée, chaque enfant commence plus
    // à droite que le précédent ; au repli, il repart à gauche. Compter par le
    // haut serait faux ici : plusieurs grilles converties sont en
    // `align-items: center`, et deux panneaux de hauteurs différentes n'ont
    // jamais le même bord haut.
    const enfants = Array.from(element.children).filter(
      (enfant) => getComputedStyle(enfant).display !== 'none'
    );
    if (enfants.length === 0) {
      return { ...base, colonnes: 0, raison: 'aucun enfant' };
    }
    let colonnes = enfants.length;
    let precedent = null;
    for (let i = 0; i < enfants.length; i += 1) {
      const rect = enfants[i].getBoundingClientRect();
      if (precedent !== null && rect.left <= precedent + 1) {
        colonnes = i;
        break;
      }
      precedent = rect.left;
    }
    return { ...base, colonnes };
  }

  return { ...base, colonnes: null, raison: `affichage \`${style.display}\`, ni grille ni flex` };
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

  const rapport = {
    navigateur: null,
    base,
    source,
    mesures: [],
    erreurs: [],
    echelles: {},
  };
  try {
    rapport.navigateur = await browser.version();

    // Un point = (grille, largeur, échelle). Les points sont groupés par page
    // puis par échelle : chaque changement de fenêtre coûte un recalcul de mise
    // en page, et 34 grilles × 3 échelles × 20 largeurs ne doivent pas en
    // coûter plus que nécessaire.
    const parPage = new Map();
    for (const grille of prediction.grilles) {
      for (const point of grille.points) {
        const cle = `${grille.page}|${point.echelle}`;
        if (!parPage.has(cle)) parPage.set(cle, { page: grille.page, echelle: point.echelle, cibles: [] });
        parPage.get(cle).cibles.push({ selecteur: grille.selecteur, largeur: point.largeur });
      }
    }

    for (const { page: route, echelle, cibles } of parPage.values()) {
      const page = await browser.newPage();
      const url = new URL(route, base).href;
      try {
        await page.goto(url, { waitUntil: 'networkidle0' });
      } catch (erreur) {
        rapport.erreurs.push({ page: route, raison: `page injoignable : ${erreur.message}` });
        await page.close();
        continue;
      }
      await page.addStyleTag({
        content: '* { animation: none !important; transition: none !important; }',
      });
      await page.evaluate((valeur) => {
        const racine = document.documentElement;
        ['texte-tres-reduit', 'texte-reduit', 'texte-agrandi', 'texte-tres-agrandi'].forEach((classe) =>
          racine.classList.remove(classe)
        );
        const classe = { 0.85: 'texte-reduit', 1.15: 'texte-agrandi', 1.3: 'texte-tres-agrandi' }[String(valeur)];
        if (classe) racine.classList.add(classe);
        // Les présentations remplacent la grille : on mesure celle par défaut,
        // et on l'écrit, pour que « mesuré en Lecture » ne se confonde pas avec
        // « mesuré partout ».
        if (racine.dataset.layout) delete racine.dataset.layout;
      }, echelle);

      const hauteurs = new Map();
      for (const cible of cibles) {
        hauteurs.set(cible.largeur, (hauteurs.get(cible.largeur) || 1000));
      }
      for (const largeur of [...hauteurs.keys()].sort((a, b) => a - b)) {
        // Un ascenseur vertical retire de la largeur utile : la fenêtre est
        // donc élargie de ce que le document perd, jusqu'à ce que la largeur
        // cliente vaille exactement la largeur demandée. Sans cela, chaque
        // mesure serait décalée de la largeur de l'ascenseur, et la comparaison
        // au modèle accuserait la feuille d'un décalage de navigateur.
        let fenetre = largeur;
        for (let essai = 0; essai < 3; essai += 1) {
          await page.setViewport({ width: fenetre, height: 900, deviceScaleFactor: 1 });
          const cliente = await page.evaluate(() => document.documentElement.clientWidth);
          if (cliente === largeur) break;
          fenetre += largeur - cliente;
        }
        const cliente = await page.evaluate(() => document.documentElement.clientWidth);
        for (const cible of cibles.filter((c) => c.largeur === largeur)) {
          let resultat;
          try {
            resultat = await page.evaluate(compter, cible.selecteur);
          } catch (erreur) {
            resultat = { trouve: false, raison: `évaluation impossible : ${erreur.message}` };
          }
          const entree = {
            selecteur: cible.selecteur,
            page: route,
            largeur,
            largeur_cliente: cliente,
            echelle,
            ...resultat,
          };
          rapport.mesures.push(entree);
          if (!entree.trouve || entree.colonnes === null) {
            rapport.erreurs.push({
              selecteur: cible.selecteur,
              page: route,
              largeur,
              raison: entree.raison || 'mesure impossible',
            });
          }
        }
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

  const mesurees = rapport.mesures.filter((m) => m.trouve && m.colonnes !== null).length;
  console.log(
    `Mesure navigateur : ${mesurees} point(s) mesuré(s) sur ${rapport.mesures.length}, ` +
      `${rapport.erreurs.length} erreur(s) — rapport écrit dans ${destination}.`
  );
  if (rapport.erreurs.length) {
    for (const erreur of rapport.erreurs.slice(0, 20)) {
      console.error(
        `  ! ${erreur.selecteur} sur ${erreur.page}` +
          (erreur.largeur ? ` à ${erreur.largeur} px` : '') +
          ` : ${erreur.raison}`
      );
    }
    if (rapport.erreurs.length > 20) {
      console.error(`  … ${rapport.erreurs.length - 20} autre(s) erreur(s) dans le rapport.`);
    }
    process.exit(1);
  }
  process.exit(0);
})();
