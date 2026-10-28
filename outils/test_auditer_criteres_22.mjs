#!/usr/bin/env node
/**
 * Banc de `auditer-criteres-22.mjs` : ce qu'il fait d'un chargement qui échoue.
 *
 * L'auditeur mesure trois critères WCAG dans un vrai Chromium et n'a aucun test.
 * Sa géométrie ne se teste pas sans navigateur ; son **contrat de sortie**, si —
 * et c'est là qu'il a menti une fois. Le 24 octobre 2026, lancé sans serveur
 * local, il avait rendu « 0 cible, 0 élément testé » : la même chose qu'une page
 * parfaite. Le défaut a été corrigé (les chargements en échec sont comptés, et
 * l'échec total sort en code 1), mais rien ne l'empêchait de revenir.
 *
 * Ce banc remplace `puppeteer-core` et `@sparticuz/chromium` par deux faux
 * (`outils/faux-navigateur/`) copiés dans un `node_modules` temporaire, puis
 * lance **le vrai script**, sans modification. Il vérifie :
 *
 * 1. mode nominal : code 0, bilan chiffré, rapport JSON écrit, aucun échec ;
 * 2. tous les chargements en échec : code 1, message « Toutes les pages ont
 *    échoué », et **aucune ligne de bilan** — on ne conclut pas sans mesure ;
 * 3. un chargement en échec sur deux : code 0, mais « aucune conclusion ne peut
 *    en sortir » et l'échec est nommé et présent dans le JSON ;
 * 4. mode « defauts » : la cible trop petite est nommée avec sa page et sa
 *    largeur, le débordement et le texte rogné sont comptés, le focus masqué
 *    est listé, et la passe coupée par le plafond est déclarée.
 *
 * Ce que ce banc ne prouve pas : que la géométrie mesurée soit juste. Il ne
 * mesure rien — il regarde ce que le script fait des mesures qu'on lui donne.
 *
 * Usage :
 *   node outils/test_auditer_criteres_22.mjs
 */

import { spawn } from 'node:child_process';
import { cp, mkdtemp, readFile, rm } from 'node:fs/promises';
import os from 'node:os';
import path from 'node:path';
import process from 'node:process';
import { fileURLToPath } from 'node:url';

const OUTILS = path.dirname(fileURLToPath(import.meta.url));
const RACINE = path.resolve(OUTILS, '..');
const FAUX = path.join(OUTILS, 'faux-navigateur');
const AUDITEUR = path.join(OUTILS, 'auditer-criteres-22.mjs');

/** Prépare un `node_modules` jetable qui contient les deux faux paquets. */
async function fauxModules() {
  const dossier = await mkdtemp(path.join(os.tmpdir(), 'mrsc-faux-navigateur-'));
  const modules = path.join(dossier, 'node_modules');
  await cp(path.join(FAUX, 'puppeteer-core'), path.join(modules, 'puppeteer-core'), { recursive: true });
  await cp(path.join(FAUX, '@sparticuz', 'chromium'), path.join(modules, '@sparticuz', 'chromium'), { recursive: true });
  return { dossier, modules };
}

/** Lance l'auditeur réel avec le faux navigateur et rend code + sorties. */
async function auditer(mode, { pages = ['index.html', 'apprendre.html'], options = [] } = {}) {
  const { dossier, modules } = await fauxModules();
  const rapport = path.join(dossier, 'rapport.json');
  const code = await new Promise((resoudre) => {
    const enfant = spawn(
      process.execPath,
      [AUDITEUR, '--largeurs', '390', '--pages', ...pages, '--json', rapport, ...options],
      {
        cwd: RACINE,
        env: { ...process.env, MRSC_BROWSER_NODE_MODULES: modules, FAUX_NAVIGATEUR_MODE: mode },
      },
    );
    let sortie = '';
    enfant.stdout.on('data', (morceau) => { sortie += morceau; });
    enfant.stderr.on('data', (morceau) => { sortie += morceau; });
    enfant.on('close', (statut) => resoudre({ statut, sortie }));
  });
  let contenu = null;
  try {
    contenu = JSON.parse(await readFile(rapport, 'utf8'));
  } catch { /* l'absence de rapport est un résultat, pas une erreur du banc */ }
  await rm(dossier, { recursive: true, force: true });
  return { ...code, rapport: contenu };
}

let echecs = 0;
function verifier(condition, message, contexte = '') {
  if (condition) return;
  echecs += 1;
  console.error(`  ÉCHEC — ${message}`);
  if (contexte) console.error(contexte.split('\n').map((l) => `    | ${l}`).join('\n'));
}

const cas = [
  {
    nom: 'nominal : bilan chiffré, aucun échec, rapport écrit',
    mode: 'nominal',
    async verifier({ statut, sortie, rapport }) {
      verifier(statut === 0, 'le code de sortie devrait être 0', sortie);
      verifier(/Pages mesurées : 2 × 390 px/.test(sortie), 'les pages mesurées devraient être annoncées', sortie);
      verifier(/2\.5\.8 — cibles : 12 conformes/.test(sortie), 'le bilan des cibles devrait être chiffré', sortie);
      verifier(/0 à corriger/.test(sortie), 'aucune cible ne devrait être à corriger', sortie);
      verifier(!/aucune conclusion ne peut en sortir/.test(sortie), 'aucun échec ne devrait être annoncé', sortie);
      verifier(rapport && rapport.echecs.length === 0, 'le rapport devrait ne contenir aucun échec', JSON.stringify(rapport));
      verifier(rapport && rapport.pages === 2 && rapport.largeurs[0] === 390, 'le rapport devrait décrire le périmètre mesuré', JSON.stringify(rapport));
    },
  },
  {
    nom: 'échec total : code 1, et aucune conclusion',
    mode: 'echec-total',
    async verifier({ statut, sortie }) {
      verifier(statut === 1, 'un échec total devrait sortir en code 1', sortie);
      verifier(/Toutes les pages ont échoué/.test(sortie), 'le message d\'échec total devrait être explicite', sortie);
      verifier(/python3 -m http\.server/.test(sortie), 'la sortie devrait dire quoi lancer', sortie);
      verifier(!/2\.5\.8 — cibles/.test(sortie), 'aucun bilan de cibles ne devrait être imprimé sans mesure', sortie);
      verifier(!/0 à corriger/.test(sortie), 'un échec ne doit jamais se lire « 0 défaut »', sortie);
    },
  },
  {
    nom: 'échec partiel : le doute est dit, pas converti en bilan',
    mode: 'echec-partiel',
    async verifier({ statut, sortie, rapport }) {
      verifier(statut === 0, 'un échec partiel reste un constat, pas un échec de sortie', sortie);
      verifier(/Chargements en échec : 1 relevé/.test(sortie), 'l\'échec partiel devrait être compté', sortie);
      verifier(/aucune conclusion ne peut en sortir/.test(sortie), 'le doute devrait être écrit', sortie);
      verifier(/échec — apprendre\.html @390/.test(sortie), 'l\'échec devrait nommer la page', sortie);
      verifier(rapport && rapport.echecs.length === 1, 'le rapport devrait isoler l\'échec', JSON.stringify(rapport));
      verifier(rapport && rapport.echecs[0].page === 'apprendre.html', 'le rapport devrait nommer la page en échec', JSON.stringify(rapport));
    },
  },
  {
    nom: 'défauts : cibles, débordement, rognage et focus masqué sont nommés',
    mode: 'defauts',
    // Plafond de focus à 5 pour que la passe soit réellement coupée : sans lui,
    // le faux navigateur annonce 7 cibles atteignables et rien ne serait coupé.
    options: ['--focus', '5'],
    async verifier({ statut, sortie, rapport }) {
      verifier(statut === 0, 'des défauts ne changent pas le code de sortie (constat, pas porte)', sortie);
      // Deux pages × une cible : la page et la largeur de fenêtre doivent
      // survivre à côté des dimensions de la cible, qui portaient le même nom.
      verifier(/2 à corriger/.test(sortie), 'la cible trop petite devrait être comptée deux fois', sortie);
      verifier(/à corriger — index\.html @390 : button\.fermer 16×16/.test(sortie), 'la cible devrait être nommée avec sa page et la largeur de fenêtre, pas sa propre largeur', sortie);
      verifier(/2 page\(s\) qui défilent horizontalement/.test(sortie), 'le débordement devrait être compté par page', sortie);
      verifier(/2 page\(s\) avec du texte rogné/.test(sortie), 'le rognage devrait être compté par page', sortie);
      verifier(/10 entièrement masqués/.test(sortie), 'le focus masqué devrait être compté', sortie);
      verifier(/masqué — index\.html @390/.test(sortie), 'le focus masqué devrait être nommé', sortie);
      verifier(/2 page\(s\) coupée\(s\) par le plafond/.test(sortie), 'une passe coupée doit être déclarée, jamais silencieuse', sortie);
      verifier(rapport && rapport.cibles.aCorriger.length === 2, 'le rapport devrait garder les cibles à corriger', JSON.stringify(rapport));
      verifier(rapport && rapport.cibles.aCorriger[0].largeur === 390, 'le rapport devrait garder la largeur de fenêtre', JSON.stringify(rapport.cibles.aCorriger));
      verifier(rapport && rapport.cibles.aCorriger[0].largeurCible === 16, 'le rapport devrait garder la largeur de la cible', JSON.stringify(rapport.cibles.aCorriger));
      verifier(rapport && rapport.espacement.debordements.length === 2, 'le rapport devrait garder le débordement', JSON.stringify(rapport));
      verifier(rapport && rapport.focus.coupees.length === 2, 'le rapport devrait dire les passes coupées', JSON.stringify(rapport.focus));
    },
  },
];

for (const un of cas) {
  const resultat = await auditer(un.mode, { options: un.options || [] });
  const avant = echecs;
  await un.verifier(resultat);
  console.log(`${echecs === avant ? 'ok' : 'ÉCHEC'} — ${un.nom}`);
}

if (echecs) {
  console.error(`\n${echecs} vérification(s) en échec.`);
  process.exitCode = 1;
} else {
  console.log('\nOK — 4 cas : le bilan ne se confond plus avec un succès.');
}
