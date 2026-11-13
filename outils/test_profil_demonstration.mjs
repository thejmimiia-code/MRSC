#!/usr/bin/env node
'use strict';
/**
 * Banc du profil de démonstration.
 *
 * Le profil ne vaut que s'il écrit **les clés que le site lit vraiment**, avec
 * les valeurs qu'il accepte. Un profil qui inventerait `mrsc-texte` au lieu de
 * `mrsc-texte-cran` afficherait un état que le site ignorerait au rechargement :
 * la séance d'essai mentirait sans que personne ne s'en aperçoive.
 *
 * Ce banc confronte donc le profil à `assets/js/site.js` lui-même, pas à une
 * copie de la liste. Il vérifie aussi que le profil ne lit jamais le stockage
 * existant et ne propose que des valeurs énumérées.
 *
 * Ce qu'il ne prouve pas : que le rendu est celui attendu, ni qu'un essai a eu
 * lieu. Il prouve que l'état de départ est celui du site.
 *
 * Usage :
 *     node outils/test_profil_demonstration.mjs
 */

import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';

const ICI = dirname(fileURLToPath(import.meta.url));
const RACINE = join(ICI, '..');

const profil = await import('./profil-demonstration.mjs');
const { CLES_CONNUES, VALEURS_ACCEPTEES, ETATS, clesDeLEtat, verifierCle, commandePour } = profil;

const sourceSite = readFileSync(join(RACINE, 'assets', 'js', 'site.js'), 'utf8');

let echecs = 0;
let controles = 0;

function verifier(intitule, condition, detail = '') {
  controles += 1;
  if (condition) {
    console.log(`OK    ${intitule}`);
  } else {
    echecs += 1;
    console.log(`ÉCHEC ${intitule}${detail ? ` — ${detail}` : ''}`);
  }
}

// 1. Chaque clé du profil existe littéralement dans site.js.
for (const [nom, cle] of Object.entries(CLES_CONNUES)) {
  verifier(
    `clé « ${nom} » (${cle}) présente dans assets/js/site.js`,
    sourceSite.includes(`"${cle}"`),
    'le site ne lirait jamais cette clé',
  );
}

// 2. Les valeurs énumérées existent dans le script, une par une.
for (const [cle, valeurs] of Object.entries(VALEURS_ACCEPTEES)) {
  for (const valeur of valeurs) {
    if (/^(75|85|100|115|130)$/.test(valeur)) {
      verifier(
        `valeur « ${valeur} » pour ${cle} dans l’échelle du site`,
        sourceSite.includes('const textLevels = [75, 85, 100, 115, 130]'),
      );
      continue;
    }
    if (valeur === 'oui' || valeur === 'non') {
      // Le site compare à « oui » et écrit « non » ; on vérifie les deux formes.
      verifier(
        `valeur « ${valeur} » pour ${cle} conforme au site`,
        valeur === 'oui' ? sourceSite.includes('=== "oui"') : sourceSite.includes('? "oui" : "non"'),
      );
      continue;
    }
    verifier(
      `valeur « ${valeur} » pour ${cle} présente dans site.js`,
      sourceSite.includes(`"${valeur}"`),
      'le site refuserait cette valeur',
    );
  }
}

// 3. Chaque état est cohérent : ses clés existent, ses valeurs sont acceptées.
for (const [nom, etat] of Object.entries(ETATS)) {
  let valide = true;
  try {
    clesDeLEtat(nom);
  } catch (erreur) {
    valide = false;
    verifier(`état « ${nom} » entièrement valide`, false, erreur.message);
  }
  if (valide) {
    verifier(`état « ${nom} » entièrement valide`, true);
  }
  verifier(
    `état « ${nom} » dit à quelle tâche il sert`,
    typeof etat.pour === 'string' && etat.pour.length > 8,
  );
  verifier(
    `état « ${nom} » a un libellé lisible`,
    typeof etat.libelle === 'string' && etat.libelle.length > 6,
  );
}

// 4. Le profil refuse ce que le site refuserait.
let refuseCle = false;
try {
  verifierCle('mrsc-cle-inventee', 'oui');
} catch {
  refuseCle = true;
}
verifier('une clé inventée est refusée', refuseCle);

let refuseValeur = false;
try {
  verifierCle(CLES_CONNUES.apparence, 'neon-vert');
} catch {
  refuseValeur = true;
}
verifier('une valeur non énumérée est refusée', refuseValeur);

let refuseEtat = false;
try {
  clesDeLEtat('etat-qui-nexiste-pas');
} catch {
  refuseEtat = true;
}
verifier('un état inconnu est refusé', refuseEtat);

// 5. Le profil n'écrit rien hors des clés connues, et ne lit pas l'existant
//    pour décider : `appliquer` ne fait que poser des `setItem`.
const sourceProfil = readFileSync(join(ICI, 'profil-demonstration.mjs'), 'utf8');
const boutEnBout = sourceProfil.slice(sourceProfil.indexOf('export const MRSC_PROFIL'));
verifier(
  'appliquer n’appelle que setItem',
  /appliquer\(nom\)[\s\S]*?s\.setItem\(cle, valeur\)/.test(boutEnBout)
    && !/appliquer\(nom\)[\s\S]*?getItem/.test(boutEnBout.split('etat()')[0]),
);
verifier(
  'reinitialiser ne vide pas tout le stockage',
  boutEnBout.includes('s.removeItem(cle)') && !boutEnBout.includes('s.clear()'),
  'un clear() effacerait les données de la personne',
);

// 6. La commande affichée est exécutable et ne pose que des setItem.
for (const nom of Object.keys(ETATS)) {
  const commande = commandePour(nom);
  const lignes = commande.split('\n').filter(Boolean);
  verifier(
    `commande « ${nom} » : ${lignes.length} ligne(s), toutes en setItem`,
    lignes.every((ligne) => ligne.startsWith('localStorage.setItem(')),
  );
}

// 7. Aucune donnée personnelle : le profil ne nomme ni personne ni appareil.
const interdit = /(nom|adresse|email|téléphone|diagnostic|handicap)\s*[:=]/i;
verifier('aucun champ de donnée personnelle dans les états', !interdit.test(JSON.stringify(ETATS)));

// 8. Un état qui prétendrait concerter un module doit le poser réellement.
const modules = new Set(['mrsc-lecture-aide', 'mrsc-mouvement-attenue', 'mrsc-reperes-visibles']);
const clesModulesActifs = clesDeLEtat('modules-actifs').map(({ cle }) => cle);
verifier(
  'l’état « modules-actifs » pose les trois modules',
  clesModulesActifs.length === 3 && clesModulesActifs.every((cle) => modules.has(cle)),
);

console.log(`\n${controles - echecs}/${controles} contrôle(s) réussi(s).`);
if (echecs > 0) {
  console.error(`${echecs} échec(s).`);
  process.exit(1);
}
