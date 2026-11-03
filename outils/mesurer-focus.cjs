#!/usr/bin/env node
'use strict';
// Mesure, dans un vrai navigateur, ce que **devient** un élément quand il reçoit
// le focus au clavier — et si cet indicateur est lisible.
//
// Le dépôt mesurait déjà le contraste des textes (`mesurer-cadrages.cjs`) et le
// focus « non masqué » (WCAG 2.2, 2.4.11, dans `auditer-criteres-22.mjs`). Rien
// ne mesurait la **visibilité** de l'indicateur lui-même : un contour de la même
// couleur que le fond rend le focus invisible, et une page parfaitement lisible
// peut être impossible à parcourir au clavier sans se perdre.
//
// La méthode, et pourquoi elle passe par le clavier réel :
//   - la touche Tab est réellement pressée : `element.focus()` ne déclenche pas
//     `:focus-visible` de façon fiable dans Chromium, et mesurer un style qui ne
//     s'applique pas à une personne qui navigue au clavier serait une mesure
//     fausse — une faute de sonde déguisée en conformité ;
//   - l'apparence **au focus** est celle que la touche vient de produire ; le
//     **repos** est obtenu en défocalisant, puis le focus est rendu pour que la
//     touche suivante reprenne le parcours. Le script vérifie que l'apparence
//     rendue est identique à celle du focus réel, et refuse de conclure sinon.
//
// Ce script ne juge pas : il écrit l'indicateur, sa couleur, le fond adjacent et
// le rapport WCAG calculé. Le seuil (3:1 pour un élément non textuel, WCAG 2.2
// 1.4.11) et le refus appartiennent à `outils/focus.py`, qui se laisse éprouver
// sans navigateur.
//
// Codes de sortie :
//   0  tout a été mesuré
//   1  une page n'a pas pu être mesurée (le rapport dit laquelle et pourquoi)
//   2  pas de navigateur, pas de modules, plan illisible — jamais vert
//
// Usage :
//   MRSC_BROWSER_NODE_MODULES=… node outils/mesurer-focus.cjs plan.json rapport.json

const fs = require('node:fs');

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

const [cheminPlan, cheminRapport] = process.argv.slice(2);
if (!cheminPlan || !cheminRapport) {
  sortir(2, 'Usage : node outils/mesurer-focus.cjs plan.json rapport.json');
}

let plan;
try {
  plan = JSON.parse(fs.readFileSync(cheminPlan, 'utf8'));
} catch (erreur) {
  sortir(2, `Plan illisible (${cheminPlan}) : ${erreur.message}`);
}
if (!Array.isArray(plan.pages) || plan.pages.length === 0) {
  sortir(2, `Plan sans page : rien à mesurer dans ${cheminPlan}.`);
}
if (!Array.isArray(plan.largeurs) || plan.largeurs.length === 0) {
  sortir(2, `Plan sans largeur : ${cheminPlan} ne dit pas dans quel cadrage mesurer.`);
}

const base = process.env.MRSC_TEST_URL || 'http://127.0.0.1:4183/';

// --- Ce qui tourne dans la page ------------------------------------------------

//: Mesure l'élément qui a le focus. Les seuils ne sont pas ici : le rapport WCAG
//: est calculé, jamais comparé.
function mesurerActif(position) {
  const lireCouleur = (texte) => {
    const trouve = String(texte).match(/rgba?\(([^)]+)\)/);
    if (!trouve) return null;
    const parts = trouve[1].split(',').map((valeur) => parseFloat(valeur.trim()));
    if (parts.length < 3) return null;
    return { r: parts[0], g: parts[1], b: parts[2], a: parts.length > 3 ? parts[3] : 1 };
  };
  const canal = (valeur) => {
    const normalisee = valeur / 255;
    return normalisee <= 0.03928 ? normalisee / 12.92 : ((normalisee + 0.055) / 1.055) ** 2.4;
  };
  const luminance = (couleur) => 0.2126 * canal(couleur.r) + 0.7152 * canal(couleur.g) + 0.0722 * canal(couleur.b);
  const rapport = (une, autre) => {
    if (!une || !autre) return null;
    const l1 = luminance(une);
    const l2 = luminance(autre);
    return Math.round(((Math.max(l1, l2) + 0.05) / (Math.min(l1, l2) + 0.05)) * 100) / 100;
  };
  // Le fond réellement vu derrière un point : les couches sont composées du bas
  // vers le haut, jamais arrêtées à la première couleur non nulle. Le 3 novembre
  // 2026, une première version s'arrêtait à `rgba(255,255,255,0.055)` — un blanc
  // à 5,5 % sur un bandeau marine — et accusait un contour doré d'être à 2,21:1
  // contre du blanc. La couleur d'un pixel n'est pas la couleur d'une déclaration.
  const composer = (dessus, dessous) => ({
    r: dessus.r * dessus.a + dessous.r * (1 - dessus.a),
    g: dessus.g * dessus.a + dessous.g * (1 - dessus.a),
    b: dessus.b * dessus.a + dessous.b * (1 - dessus.a),
    a: 1,
  });
  const fondVu = (depart) => {
    const couches = [];
    let courant = depart;
    while (courant && courant !== document.documentElement.parentElement) {
      const style = getComputedStyle(courant);
      if (style.backgroundImage && style.backgroundImage !== 'none') {
        return { couleur: null, image: true };
      }
      const couleur = lireCouleur(style.backgroundColor);
      if (couleur && couleur.a > 0) couches.push(couleur);
      courant = courant.parentElement;
    }
    let fond = { r: 255, g: 255, b: 255, a: 1 };
    for (let rang = couches.length - 1; rang >= 0; rang -= 1) fond = composer(couches[rang], fond);
    return { couleur: fond, image: false };
  };
  const nom = (element) => {
    const classes = String(element.className || '')
      .split(/\s+/)
      .filter(Boolean)
      .slice(0, 2)
      .join('.');
    return `${element.tagName.toLowerCase()}${classes ? `.${classes}` : ''}`;
  };
  const apparence = (element) => {
    const style = getComputedStyle(element);
    return {
      contour: `${style.outlineStyle}|${style.outlineWidth}|${style.outlineColor}`,
      ombre: style.boxShadow,
      fond: style.backgroundColor,
      bordure: `${style.borderTopWidth}|${style.borderTopStyle}|${style.borderTopColor}`,
      decoration: `${style.textDecorationLine}|${style.textDecorationColor}`,
      couleur: style.color,
    };
  };

  const actif = document.activeElement;
  // La traversée clavier revient au document après le dernier élément : c'est la
  // fin du parcours, pas une mesure vide.
  if (!actif || actif === document.body) return { fin: true };
  if (!window.__mrscVus) window.__mrscVus = new WeakSet();
  if (window.__mrscVus.has(actif)) return { deja_vu: true };
  window.__mrscVus.add(actif);

  const libelle = (actif.textContent || actif.getAttribute('aria-label') || '').trim().slice(0, 40);

  // L'apparence au focus est celle que la touche Tab vient de produire : la
  // seule qui compte, parce que c'est celle que voit une personne au clavier.
  const auFocus = apparence(actif);
  // Le repos est obtenu en défocalisant l'élément, puis le focus est rendu pour
  // que la touche Tab suivante reprenne où elle en était. Un `element.focus()`
  // ne déclenche pas `:focus-visible` de façon fiable : le script vérifie donc
  // que l'apparence rendue est identique à celle du focus réel, et refuse de
  // conclure sinon.
  actif.blur();
  const auRepos = apparence(actif);
  actif.focus({ preventScroll: true });
  const apresRetour = apparence(actif);
  const retabli = JSON.stringify(apresRetour) === JSON.stringify(auFocus);

  const exterieur = fondVu(actif.parentElement);
  const interieur = fondVu(actif);
  const style = getComputedStyle(actif);

  const mesure = {
    position,
    selecteur: nom(actif),
    libelle,
    retabli,
    fond: exterieur.couleur,
    fond_image: exterieur.image || interieur.image,
    changement: null,
    indicateur: 'aucun',
    couleur: null,
    epaisseur: null,
    contraste: null,
  };

  if (auFocus.contour !== auRepos.contour) {
    const couleur = lireCouleur(style.outlineColor);
    const epaisseur = parseFloat(style.outlineWidth) || 0;
    mesure.changement = 'contour';
    mesure.epaisseur = epaisseur;
    mesure.couleur = couleur;
    if (style.outlineStyle === 'none' || epaisseur === 0) {
      // Un contour effacé au focus est un changement, pas un indicateur.
      mesure.indicateur = 'aucun';
    } else {
      mesure.indicateur = 'contour';
      mesure.contraste = rapport(couleur, exterieur.couleur);
    }
  } else if (auFocus.ombre !== auRepos.ombre) {
    const couleur = lireCouleur(style.boxShadow.replace(/inset/g, ''));
    mesure.changement = 'ombre';
    mesure.couleur = couleur;
    mesure.indicateur = couleur ? 'ombre' : 'aucun';
    mesure.contraste = rapport(couleur, exterieur.couleur);
  } else if (auFocus.fond !== auRepos.fond) {
    const couleur = lireCouleur(style.backgroundColor);
    mesure.changement = 'fond';
    mesure.couleur = couleur;
    mesure.indicateur = 'fond';
    mesure.contraste = rapport(couleur, exterieur.couleur);
  } else if (auFocus.bordure !== auRepos.bordure) {
    const couleur = lireCouleur(style.borderTopColor);
    mesure.changement = 'bordure';
    mesure.couleur = couleur;
    mesure.indicateur = 'bordure';
    mesure.contraste = rapport(couleur, interieur.couleur);
  } else if (auFocus.decoration !== auRepos.decoration || auFocus.couleur !== auRepos.couleur) {
    const couleur = lireCouleur(style.textDecorationColor) || lireCouleur(style.color);
    mesure.changement = 'texte';
    mesure.couleur = couleur;
    mesure.indicateur = 'texte';
    mesure.contraste = rapport(couleur, interieur.couleur);
  }
  return mesure;
}

// --- La traversée ---------------------------------------------------------------

(async () => {
  let browser;
  try {
    browser = await puppeteer.launch({
      executablePath: await chromium.executablePath(),
      args: chromium.args,
      headless: true,
    });
  } catch (erreur) {
    const message = String(erreur.message || '');
    const aide = /shared libraries/.test(message)
      ? ' — les bibliothèques système de Chromium manquent : extraire `al2023.tar.br` du paquet et exporter LD_LIBRARY_PATH vers son dossier `lib`'
      : '';
    sortir(2, `Environnement : lancement du navigateur impossible${aide} (${message.split('\n')[0]}) — aucune mesure.`);
  }

  const limite = Number(plan.limite || 60);
  const rapport = { navigateur: null, base, limite, pages: [], erreurs: [] };
  try {
    rapport.navigateur = await browser.version();
    for (const nomPage of plan.pages) {
      for (const largeur of plan.largeurs) {
        const page = await browser.newPage();
        try {
          await page.goto(new URL(nomPage, base).href, { waitUntil: 'networkidle0' });
        } catch (erreur) {
          rapport.erreurs.push({ page: nomPage, largeur, raison: `page injoignable : ${erreur.message}` });
          await page.close();
          continue;
        }
        await page.addStyleTag({ content: '* { animation: none !important; transition: none !important; }' });
        // Même précaution que pour les cadrages : l'ascenseur vertical retire de
        // la largeur utile, et une fenêtre trop étroite déplacerait le seuil.
        let fenetre = largeur;
        for (let essai = 0; essai < 3; essai += 1) {
          await page.setViewport({ width: fenetre, height: 900, deviceScaleFactor: 1 });
          const cliente = await page.evaluate(() => document.documentElement.clientWidth);
          if (cliente === largeur) break;
          fenetre += largeur - cliente;
        }
        try {
          const elements = [];
          // Le premier Tab installe le mode clavier : `:focus-visible` ne
          // s'applique pas à un focus programmatique.
          for (let pas = 0; pas < limite; pas += 1) {
            await page.keyboard.press('Tab');
            const mesure = await page.evaluate(mesurerActif, pas + 1);
            if (!mesure || mesure.fin || mesure.deja_vu) break;
            elements.push(mesure);
          }
          rapport.pages.push({
            page: nomPage,
            largeur,
            // `borne` : la traversée s'est arrêtée au plafond, pas à la fin du
            // document. C'est la seule chose honnête à dire d'une couverture —
            // un dénominateur estimé par un sélecteur compte aussi des cibles
            // qu'aucune touche Tab n'atteint (boutons désactivés, sections
            // fermées), et annoncerait un manque qui n'existe pas.
            borne: elements.length >= limite,
            parcourus: elements.length,
            elements,
          });
        } catch (erreur) {
          rapport.erreurs.push({ page: nomPage, largeur, raison: `évaluation impossible : ${erreur.message}` });
        }
        await page.close();
      }
    }
  } finally {
    await browser.close();
  }

  fs.writeFileSync(cheminRapport, JSON.stringify(rapport, null, 1));
  const elements = rapport.pages.reduce((total, page) => total + (page.elements || []).length, 0);
  console.log(
    `Focus : ${rapport.pages.length} page(s) mesurée(s), ${elements} élément(s) portés au focus, ` +
      `${rapport.erreurs.length} erreur(s). Rapport : ${cheminRapport}`
  );
  if (rapport.erreurs.length > 0) {
    for (const erreur of rapport.erreurs) {
      console.error(`  - ${erreur.page} (${erreur.largeur} px) : ${erreur.raison}`);
    }
    process.exit(1);
  }
})();
