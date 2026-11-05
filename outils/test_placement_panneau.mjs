#!/usr/bin/env node
/**
 * Banc du placement mesuré des panneaux flottants du site (site.js).
 *
 * Depuis le 30 octobre 2026, le panneau « Personnalisation » n'est plus ancré par
 * un point de rupture mais **placé à la mesure** : `placerPanneauFlottant()` lit
 * la largeur de la fenêtre (`visualViewport` quand il existe), la position du
 * bouton et la hauteur de l'en-tête, puis borne le panneau aux deux marges.
 * C'est ce calcul — et non un format nommé — qui décide.
 *
 * Depuis le 5 novembre 2026, le **panneau du menu** passe par la même fonction :
 * le banc l'éprouve donc aussi, avec sa propre largeur voulue et un parent
 * positionné qui n'est pas le bouton (`.nav-inner`), pour que la conversion des
 * coordonnées soit vérifiée et pas seulement supposée.
 *
 * Le défaut d'avant tenait à trois règles successives, chacune laissant passer
 * un format. Une quatrième règle aurait eu le même destin : elle n'aurait été
 * juste que pour les tailles qu'on avait en tête. Aucune règle ne peut plus
 * être juste « en général » ici, donc ce banc vérifie le calcul sur une plage
 * qui ne ressemble pas à une liste de formats : **toutes** les largeurs de 240 à
 * 2 560 px par pas de 40, croisées avec cinq hauteurs et trois positions de
 * bouton — dont celle de l'en-tête compact, collée à gauche.
 *
 * Le vrai code est extrait de `assets/js/site.js` et exécuté dans un contexte
 * simulé (`node:vm`) : aucun navigateur, 300 ms, et c'est bien la fonction
 * livrée qui tourne, pas une copie. Quatre garanties par cas :
 *
 * 1. le panneau ne sort ni par la gauche, ni par la droite, ni en haut, ni en bas ;
 * 2. sa largeur ne dépasse jamais la fenêtre moins deux marges, et ne descend
 *    pas sous 160 px ;
 * 3. sa hauteur visible ne descend pas sous 160 px, même quand l'en-tête mange
 *    presque toute la fenêtre ;
 * 4. son bord droit s'aligne sur celui du bouton quand la place le permet —
 *    sinon il serait collé à une marge sans raison, ce qui se verrait.
 *
 * Limite : ceci éprouve l'arithmétique du placement, pas son rendu. Le banc
 * d'essais navigateur (`outils/test-experience.cjs`) mesure, lui, un vrai
 * Chromium, panneau ouvert, y compris pendant un redimensionnement.
 *
 * Usage : node outils/test_placement_panneau.mjs
 */

import { readFileSync } from 'node:fs';
import path from 'node:path';
import process from 'node:process';
import vm from 'node:vm';
import { fileURLToPath } from 'node:url';

const OUTILS = path.dirname(fileURLToPath(import.meta.url));
const RACINE = path.resolve(OUTILS, '..');
const SCRIPT = path.join(RACINE, 'assets', 'js', 'site.js');

/** Extrait les deux constantes et la fonction, telles qu'elles sont livrées. */
function extrairePlacement(source) {
  const debutConstante = source.indexOf('const MARGE_PANNEAU');
  if (debutConstante < 0) throw new Error('const MARGE_PANNEAU introuvable dans site.js');
  const debutFonction = source.indexOf('function placerPanneauFlottant(');
  if (debutFonction < 0) throw new Error('function placerPanneauFlottant introuvable dans site.js');
  const ouverture = source.indexOf('{', debutFonction);
  let profondeur = 0;
  let fin = ouverture;
  for (; fin < source.length; fin += 1) {
    if (source[fin] === '{') profondeur += 1;
    else if (source[fin] === '}') {
      profondeur -= 1;
      if (profondeur === 0) break;
    }
  }
  if (profondeur !== 0) throw new Error('accolades non équilibrées dans placerPanneauFlottant');
  const constantes = source.slice(debutConstante, debutFonction);
  return `${constantes}\n${source.slice(debutFonction, fin + 1)}`;
}

const placement = extrairePlacement(readFileSync(SCRIPT, 'utf8'));

/**
 * Exécute le placement dans un décor simulé et rend la géométrie obtenue, en
 * pixels de fenêtre (le panneau est positionné relativement à son bouton).
 */
function placer({ largeurFenetre, hauteurFenetre, bouton, hauteurEntete, largeurVoulue, avecVisualViewport, parentLeft = 0, parentTop = 0 }) {
  const cadreBouton = {
    left: bouton.left,
    right: bouton.left + bouton.largeur,
    top: bouton.top ?? 0,
    bottom: (bouton.top ?? 0) + (bouton.hauteur ?? 32),
    width: bouton.largeur,
    height: bouton.hauteur ?? 32,
  };
  const cadreEntete = {
    left: 0,
    right: largeurFenetre,
    top: 0,
    bottom: hauteurEntete,
    width: largeurFenetre,
    height: hauteurEntete,
  };
  const style = {};
  const panneau = {
    style,
    // Le vrai panneau porte le marqueur `data-placement` que pose le placement.
    dataset: {},
    // Les coordonnées sont écrites relativement au parent positionné : pour
    // « Personnalisation » son `<details>`, pour le menu `.nav-inner`.
    offsetParent: { getBoundingClientRect: () => ({ left: parentLeft, top: parentTop }) },
    getBoundingClientRect: () => ({
      width: style.width === '' || style.width === undefined ? largeurVoulue : parseFloat(style.width),
      left: 0, right: 0, top: 0, bottom: 0, height: 0,
    }),
  };
  const contexte = {
    panneau,
    bouton: { getBoundingClientRect: () => cadreBouton },
    header: { getBoundingClientRect: () => cadreEntete },
    document: { documentElement: { clientWidth: largeurFenetre } },
    window: {
      innerWidth: largeurFenetre,
      innerHeight: hauteurFenetre,
      visualViewport: avecVisualViewport
        ? { width: largeurFenetre, height: hauteurFenetre }
        : null,
    },
    Math,
    Number,
  };
  vm.runInNewContext(`${placement}\nplacerPanneauFlottant(panneau, bouton);`, contexte);

  const nombre = (valeur) => Number.parseFloat(String(valeur ?? '0'));
  return {
    marqueur: panneau.dataset.placement,
    gauche: parentLeft + nombre(style.left),
    droite: parentLeft + nombre(style.left) + nombre(style.width),
    haut: parentTop + nombre(style.top),
    bas: parentTop + nombre(style.top) + nombre(style.maxHeight),
    largeur: nombre(style.width),
    hauteurVisible: nombre(style.maxHeight),
    position: style.position,
    droite_auto: style.right,
    relatif: { gauche: nombre(style.left), haut: nombre(style.top) },
  };
}

let echecs = 0;
function verifier(condition, message) {
  if (condition) return;
  echecs += 1;
  if (echecs <= 20) console.error(`  ÉCHEC — ${message}`);
}

const MARGE = 8;
const HAUTEUR_MINIMALE = 160;
const LARGEUR_VOULUE = 352;

// Les deux panneaux du site, avec ce qui les distingue réellement : la largeur
// que la feuille leur souhaite, et le parent positionné qui leur sert de
// référentiel. Pour « Personnalisation », ce parent est le `<details>` qui porte
// le bouton ; pour le menu, c'est `.nav-inner`, qui commence à gauche du bouton
// et sous le haut de l'en-tête. Si la conversion des coordonnées était fausse,
// le panneau du menu sortirait de la fenêtre dans un seul de ces deux cas.
const panneaux = [
  { nom: 'Personnalisation', largeurVoulue: 352, parentLeft: 0, parentTop: 0 },
  { nom: 'menu', largeurVoulue: 380, parentLeft: 24, parentTop: 61 },
];

// Trois positions de bouton : au début de la barre (en-tête compact, celle du
// défaut du 30 octobre), au centre, et tout à droite.
const boutons = [
  { nom: 'début de barre', left: 12, largeur: 160 },
  { nom: 'centre', left: 640, largeur: 160 },
  { nom: 'bord droit', left: 1800, largeur: 160 },
];
const hauteursEntete = [48, 96, 180];

let cas = 0;
for (const panneau of panneaux) {
for (let largeurFenetre = 240; largeurFenetre <= 2560; largeurFenetre += 40) {
  for (const hauteurFenetre of [320, 375, 440, 768, 1000]) {
    for (const hauteurEntete of hauteursEntete) {
      if (hauteurEntete > hauteurFenetre) continue;
      for (const bouton of boutons) {
        if (bouton.left + bouton.largeur > largeurFenetre) continue;
        for (const avecVisualViewport of [true, false]) {
          cas += 1;
          const geographie = `panneau ${panneau.nom}, fenêtre ${largeurFenetre}×${hauteurFenetre}, en-tête ${hauteurEntete}, bouton ${bouton.nom}, visualViewport ${avecVisualViewport ? 'oui' : 'non'}`;
          const mesure = placer({
            largeurFenetre,
            hauteurFenetre,
            bouton,
            hauteurEntete,
            largeurVoulue: panneau.largeurVoulue,
            avecVisualViewport,
            parentLeft: panneau.parentLeft,
            parentTop: panneau.parentTop,
          });
          verifier(mesure.marqueur === 'mesure',
            `le placement n'a pas laissé son marqueur — ${geographie}`);
          verifier(mesure.gauche >= MARGE - 0.51, `sort par la gauche (${mesure.gauche} px) — ${geographie}`);
          verifier(mesure.droite <= largeurFenetre - MARGE + 0.51,
            `sort par la droite (${mesure.droite} > ${largeurFenetre - MARGE}) — ${geographie}`);
          verifier(mesure.haut >= MARGE - 0.51, `sort par le haut (${mesure.haut} px) — ${geographie}`);
          verifier(mesure.bas <= hauteurFenetre - MARGE + 0.51,
            `sort par le bas (${mesure.bas} > ${hauteurFenetre - MARGE}) — ${geographie}`);
          verifier(mesure.largeur <= largeurFenetre - 2 * MARGE + 0.51,
            `largeur ${mesure.largeur} > fenêtre moins marges — ${geographie}`);
          verifier(mesure.largeur >= Math.min(160, largeurFenetre - 2 * MARGE) - 0.51,
            `largeur ${mesure.largeur} trop petite — ${geographie}`);
          verifier(mesure.hauteurVisible >= HAUTEUR_MINIMALE - 0.51,
            `hauteur visible ${mesure.hauteurVisible} < ${HAUTEUR_MINIMALE} — ${geographie}`);
          verifier(mesure.droite_auto === 'auto',
            `le panneau garde « right » posé par la feuille, ce qui étirerait sa largeur — ${geographie}`);
        }
      }
    }
  }
}
}

// Quatrième garantie, sur quatre cas lisibles plutôt que sur toute la plage :
// un bouton au centre ouvre le panneau vers la gauche (bord droit aligné sur le
// sien), un bouton au début de la barre l'ouvre vers la droite — c'est la
// correction du 28 octobre, désormais décidée par la mesure et non par une
// règle de format —, et une fenêtre étroite le borne à la marge droite.
const centre = placer({
  largeurFenetre: 1440, hauteurFenetre: 900, bouton: boutons[1], hauteurEntete: 48,
  largeurVoulue: LARGEUR_VOULUE, avecVisualViewport: true,
});
verifier(Math.abs(centre.droite - (boutons[1].left + boutons[1].largeur)) < 0.51,
  `bouton au centre : le bord droit du panneau devrait suivre le sien : ${JSON.stringify(centre)}`);

const grand = placer({
  largeurFenetre: 1440, hauteurFenetre: 900, bouton: boutons[0], hauteurEntete: 48,
  largeurVoulue: LARGEUR_VOULUE, avecVisualViewport: true,
});
verifier(Math.abs(grand.gauche - boutons[0].left) < 0.51,
  `bouton au début de la barre : le panneau devrait s'ouvrir vers la droite : ${JSON.stringify(grand)}`);

const etroit = placer({
  largeurFenetre: 320, hauteurFenetre: 800, bouton: boutons[0], hauteurEntete: 48,
  largeurVoulue: LARGEUR_VOULUE, avecVisualViewport: true,
});
verifier(Math.abs(etroit.droite - (320 - MARGE)) < 0.51,
  `en fenêtre étroite, le panneau devrait s'arrêter à la marge droite : ${JSON.stringify(etroit)}`);

const bas = placer({
  largeurFenetre: 980, hauteurFenetre: 360, bouton: boutons[0], hauteurEntete: 300,
  largeurVoulue: LARGEUR_VOULUE, avecVisualViewport: true,
});
verifier(bas.hauteurVisible >= HAUTEUR_MINIMALE - 0.51,
  `un en-tête de 300 px dans une fenêtre de 360 ne doit pas écraser le panneau : ${JSON.stringify(bas)}`);

// Le même cadre, deux parents positionnés différents : les coordonnées écrites
// changent, la position dans la fenêtre ne change pas. C'est ce qui permet au
// panneau du menu (dans `.nav-inner`) et à celui de « Personnalisation » (dans
// son `<details>`) d'être placés par le même calcul.
const sansDecalage = placer({
  largeurFenetre: 1440, hauteurFenetre: 900, bouton: boutons[1], hauteurEntete: 48,
  largeurVoulue: 380, avecVisualViewport: true,
});
const avecDecalage = placer({
  largeurFenetre: 1440, hauteurFenetre: 900, bouton: boutons[1], hauteurEntete: 48,
  largeurVoulue: 380, avecVisualViewport: true,
  parentLeft: 24, parentTop: 61,
});
verifier(Math.abs(sansDecalage.gauche - avecDecalage.gauche) < 0.51
  && Math.abs(sansDecalage.haut - avecDecalage.haut) < 0.51,
  `le parent positionné déplace le panneau dans la fenêtre : ${JSON.stringify({ sansDecalage, avecDecalage })}`);
verifier(Math.abs((sansDecalage.relatif.gauche - avecDecalage.relatif.gauche) - 24) < 0.51
  && Math.abs((sansDecalage.relatif.haut - avecDecalage.relatif.haut) - 61) < 0.51,
  `les coordonnées écrites ne sont pas relatives au parent : ${JSON.stringify({ sansDecalage, avecDecalage })}`);

if (echecs) {
  console.error(`\n${echecs} échec(s) sur ${cas} positions — le placement du panneau n'est pas borné.`);
  process.exit(1);
}
console.log(`\nOK — ${cas} positions (deux panneaux, largeurs 240 à 2 560, cinq hauteurs, trois boutons) : les panneaux restent dans la fenêtre, leur hauteur ne descend pas sous ${HAUTEUR_MINIMALE} px, leur bord droit suit le bouton, et les coordonnées écrites sont relatives au parent positionné.`);
