#!/usr/bin/env node
/**
 * Banc de `test-experience.cjs` : le harnais de neuf essais navigateur.
 *
 * C'est le plus gros des trois scripts qui *sont* un test (1 257 lignes, neuf
 * essais : choix immédiat, clavier, en-tête compact, panneaux, contraste et
 * espacement, stockage bloqué, guide, lecture à voix haute, iframe synchronisée).
 * Il ne tourne pas dans la CI : il demande un Chromium et se lance à la main.
 *
 * Ce banc n'essaie pas de rejouer les essais — le faux navigateur ne clique pas
 * et ne mesure pas. Il éprouve **le harnais** : ce qui se passe quand chaque
 * essai échoue. Car le défaut possible n'est pas dans un essai, il est dans le
 * récit : un `executer` qui enregistrerait un succès après une exception, ou un
 * `finally` qui effacerait le code de sortie, afficherait « 9/9 essais réussis »
 * après neuf échecs — et personne ne lirait plus loin.
 *
 * Trois choses sont donc vérifiées sur une exécution réelle :
 *
 * 1. chaque essai est compté **une** fois : autant de lignes « ÉCHEC — » que
 *    d'appels à `executer(` dans la source, et chaque nom d'essai affiché ;
 * 2. le bilan annoncé est `0/N`, pas un autre nombre ;
 * 3. l'échec atteint le code de sortie (1), donc un lanceur de CI le verrait.
 *
 * Puis trois mutations, chacune sur une copie : effacer le `process.exitCode`,
 * enregistrer un succès malgré l'exception, renommer un essai. Si le verdict ne
 * les rejette pas, il ne prouve rien. Enfin deux invariants lus dans la source :
 * aucun essai sans `assert.`, aucun nom d'essai en double.
 *
 * Limite écrite noir sur blanc : la justesse de ce que les essais mesurent dans
 * un vrai Chromium n'est pas éprouvée ici. Ce banc prouve que le harnais ne peut
 * pas raconter un succès qui n'a pas eu lieu.
 *
 * Usage :
 *   node outils/test_test_experience.mjs
 */

import { spawn } from 'node:child_process';
import { cp, mkdtemp, readFile, writeFile, rm } from 'node:fs/promises';
import { createServer } from 'node:http';
import os from 'node:os';
import path from 'node:path';
import process from 'node:process';
import { fileURLToPath } from 'node:url';

const OUTILS = path.dirname(fileURLToPath(import.meta.url));
const FAUX = path.join(OUTILS, 'faux-navigateur');
const SCRIPT = path.join(OUTILS, 'test-experience.cjs');

const source = await readFile(SCRIPT, 'utf8');
const noms = [...source.matchAll(/await executer\('([^']+)'/g)].map((m) => m[1]);
const nombre = noms.length;

if (nombre < 5) {
  console.error(`ÉCHEC — ${nombre} essai(s) reconnu(s) dans la source : le banc ne saurait pas quoi vérifier.`);
  process.exit(1);
}

/** Un serveur qui répond 200 à tout : le script attend une page d'accueil. */
async function serveurFactice() {
  const serveur = createServer((_requete, reponse) => {
    reponse.writeHead(200, { 'content-type': 'text/html; charset=utf-8' });
    reponse.end('<!doctype html><title>stub</title>');
  });
  await new Promise((resoudre) => serveur.listen(0, '127.0.0.1', resoudre));
  return { serveur, url: `http://127.0.0.1:${serveur.address().port}/` };
}

async function lancer(script = source) {
  const dossier = await mkdtemp(path.join(os.tmpdir(), 'mrsc-experience-'));
  const modules = path.join(dossier, 'node_modules');
  await cp(path.join(FAUX, 'puppeteer-core'), path.join(modules, 'puppeteer-core'), { recursive: true });
  await cp(path.join(FAUX, '@sparticuz', 'chromium'), path.join(modules, '@sparticuz', 'chromium'), { recursive: true });
  const chemin = path.join(dossier, 'test-experience.cjs');
  await writeFile(chemin, script);
  const { serveur, url } = await serveurFactice();
  try {
    const execution = await new Promise((resoudre) => {
      const enfant = spawn(process.execPath, [chemin], {
        cwd: dossier,
        env: {
          ...process.env,
          MRSC_BROWSER_NODE_MODULES: modules,
          MRSC_TEST_URL: url,
          FAUX_NAVIGATEUR_MODE: 'echec-total',
        },
      });
      let sortie = '';
      enfant.stdout.on('data', (morceau) => { sortie += morceau; });
      enfant.stderr.on('data', (morceau) => { sortie += morceau; });
      enfant.on('close', (statut) => resoudre({ statut, sortie }));
    });
    return execution;
  } finally {
    await new Promise((resoudre) => serveur.close(resoudre));
    await rm(dossier, { recursive: true, force: true });
  }
}

/**
 * Le verdict du cas nominal, réutilisé pour les mutations : rend la liste de ce
 * qui cloche. Une mutation doit le faire parler ; le script réel doit le laisser
 * muet.
 */
function reproches({ statut, sortie }) {
  const problemes = [];
  const echecs = (sortie.match(/ÉCHEC — /g) || []).length;
  if (echecs !== nombre) problemes.push(`${echecs} ligne(s) « ÉCHEC — » au lieu de ${nombre}`);
  for (const nom of noms) {
    if (!sortie.includes(nom)) problemes.push(`essai jamais nommé dans la sortie : « ${nom} »`);
  }
  const bilan = /(\d+)\/(\d+) essais navigateur réussis/.exec(sortie);
  if (!bilan) problemes.push('aucun bilan « x/y essais navigateur réussis »');
  else {
    if (Number(bilan[2]) !== nombre) problemes.push(`bilan sur ${bilan[2]} essais au lieu de ${nombre}`);
    if (Number(bilan[1]) !== 0) problemes.push(`bilan à ${bilan[1]} réussite(s) alors que tout a échoué`);
  }
  if (statut !== 1) problemes.push(`code de sortie ${statut} au lieu de 1`);
  return problemes;
}

let echecs = 0;
function verifier(condition, message, contexte = '') {
  if (condition) return;
  echecs += 1;
  console.error(`  ÉCHEC — ${message}`);
  if (contexte) console.error(contexte.split('\n').slice(0, 40).map((ligne) => `    | ${ligne}`).join('\n'));
}

const reel = await lancer();
const reprochesReels = reproches(reel);
verifier(reprochesReels.length === 0, `le harnais devrait rapporter ${nombre} échecs et sortir en 1`,
  `${reprochesReels.join(' · ')}\n---\n${reel.sortie}`);
// Le banc ne doit pas se contenter de compter : les neuf essais doivent avoir
// été *tentés*, ce qui se voit à leur nom dans la sortie.
verifier(noms.every((nom) => reel.sortie.includes(nom)), 'chaque essai devrait apparaître dans la sortie',
  reel.sortie);

const mutations = [
  {
    nom: 'code de sortie effacé',
    script: source.replace('  if (echoues.length) process.exitCode = 1;\n', ''),
  },
  {
    nom: 'succès enregistré malgré l’exception',
    script: source.replace('resultats.push({ nom, reussi: false, erreur: error });', 'resultats.push({ nom, reussi: true });'),
  },
  {
    nom: 'essai renommé',
    script: source.replace(`await executer('${noms[0]}'`, "await executer('Essai renommé par le banc'"),
  },
];

for (const mutation of mutations) {
  verifier(mutation.script !== source, `la mutation « ${mutation.nom} » devrait changer la source`);
  const execution = await lancer(mutation.script);
  const reproches2 = reproches(execution);
  verifier(reproches2.length > 0,
    `le verdict devrait rejeter la mutation « ${mutation.nom} » — sinon il ne prouve rien`,
    execution.sortie);
}

// Deux invariants lus dans la source : un essai sans assertion ne peut pas
// échouer autrement que par exception, et deux essais du même nom rendraient le
// bilan ambigu.
const corps = [];
for (const correspondance of source.matchAll(/await executer\('([^']+)'/g)) {
  const debut = source.indexOf('{', correspondance.index);
  let profondeur = 0;
  let fin = debut;
  for (; fin < source.length; fin += 1) {
    if (source[fin] === '{') profondeur += 1;
    else if (source[fin] === '}') {
      profondeur -= 1;
      if (profondeur === 0) break;
    }
  }
  corps.push({ nom: correspondance[1], texte: source.slice(debut, fin) });
}
for (const { nom, texte } of corps) {
  verifier(/(^|[^.\w])assert\./.test(texte), `l’essai « ${nom} » ne contient aucune assertion`,
    texte.split('\n').slice(0, 6).join('\n'));
}
const doublons = noms.filter((nom, index) => noms.indexOf(nom) !== index);
verifier(doublons.length === 0, 'deux essais portent le même nom', doublons.join(' · '));

if (echecs) {
  console.error(`\n${echecs} échec(s) — le harnais des essais navigateur n'inspire pas confiance.`);
  process.exit(1);
}
console.log(`\nOK — ${nombre} essais : chacun est compté, nommé et son échec sort en code 1 ; trois mutations sont rejetées.`);
