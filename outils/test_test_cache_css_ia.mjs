#!/usr/bin/env node
/**
 * Banc de `test-cache-css-ia.cjs` : ce que ce test-là fait de ce qu'il sert.
 *
 * Le script simule un téléphone qui aurait gardé l'ancienne feuille de style
 * sous l'URL non versionnée : il sert lui-même le vieux CSS au premier cas, le
 * CSS courant au second, et exige que l'écart entre pastilles et points soit
 * grand dans le premier, nul dans le second. Douze essais, trois largeurs, deux
 * dispositions.
 *
 * Il n'avait aucun test, et sa panne la plus discrète n'est pas un écart de
 * géométrie : c'est de **ne plus servir l'ancienne feuille**. Si l'interception
 * de requêtes disparaît, le cas « ancienne-url » ne mesure plus l'ancien CSS ;
 * si les deux cas servaient la même feuille, la « reproduction » du défaut ne
 * reproduirait rien. Dans les deux cas le test peut continuer d'afficher un
 * bilan vert en ne prouvant plus rien.
 *
 * Le faux `puppeteer-core` de `outils/faux-navigateur/` rejoue l'interception et
 * tire la distance pastille/point du CSS **réellement servi** — voir l'en-tête
 * de ce faux, qui dit que c'est la seule géométrie qu'il encode. Le vrai script
 * est lancé sans être modifié ; seuls ses fichiers d'entrée, ou le script
 * lui-même, sont mutés dans une copie jetable.
 *
 * Cinq cas :
 *
 * 1. `nominal` : code 0, le nombre d'essais annoncé est celui qui a été
 *    exécuté, et les deux cas servent bien deux URL différentes (`''` puis
 *    `?v=…`) — l'annonce est confrontée au relevé, pas recopiée ;
 * 2. `version-perimee` : l'URL versionnée de la page ne correspond plus au CSS →
 *    code 1, le message nomme la version, **et aucun relevé n'est écrit** ;
 * 3. `attente-inversee` : l'attente des deux cas est échangée dans une copie du
 *    script → code 1 (donc les assertions mordent) ;
 * 4. `sans-interception` : l'`setRequestInterception(true)` est retiré
 *    → code 1 : sans interception, le test ne peut plus rien servir ;
 * 5. `ancien-css-identique` : `MRSC_ANCIEN_CSS` reçoit le CSS courant → code 1 :
 *    le décalage constaté vient bien des anciennes règles, pas du seul fait
 *    d'avoir changé d'URL.
 *
 * Usage :
 *   node outils/test_test_cache_css_ia.mjs
 */

import { spawn } from 'node:child_process';
import { cp, mkdtemp, readFile, writeFile, mkdir, rm } from 'node:fs/promises';
import { existsSync } from 'node:fs';
import crypto from 'node:crypto';
import os from 'node:os';
import path from 'node:path';
import process from 'node:process';
import { fileURLToPath } from 'node:url';

const OUTILS = path.dirname(fileURLToPath(import.meta.url));
const RACINE = path.resolve(OUTILS, '..');
const FAUX = path.join(OUTILS, 'faux-navigateur');
const SCRIPT = path.join(OUTILS, 'test-cache-css-ia.cjs');
const CSS = path.join(RACINE, 'assets', 'css', 'site.css');
const PAGE = path.join(RACINE, 'ia-societe.html');

/** Racine factice : le script y lit ses deux fichiers, et rien du dépôt n'est touché. */
async function racineFactice({ html, script, ancienCss } = {}) {
  const dossier = await mkdtemp(path.join(os.tmpdir(), 'mrsc-cache-css-'));
  await mkdir(path.join(dossier, 'outils'), { recursive: true });
  await mkdir(path.join(dossier, 'assets', 'css'), { recursive: true });
  const modules = path.join(dossier, 'node_modules');
  await cp(path.join(FAUX, 'puppeteer-core'), path.join(modules, 'puppeteer-core'), { recursive: true });
  await cp(path.join(FAUX, '@sparticuz', 'chromium'), path.join(modules, '@sparticuz', 'chromium'), { recursive: true });
  await cp(CSS, path.join(dossier, 'assets', 'css', 'site.css'));
  await writeFile(path.join(dossier, 'ia-societe.html'), html ?? await readFile(PAGE, 'utf8'));
  await writeFile(path.join(dossier, 'outils', 'test-cache-css-ia.cjs'), script ?? await readFile(SCRIPT, 'utf8'));
  if (ancienCss !== undefined) {
    await writeFile(path.join(dossier, 'ancien.css'), ancienCss ?? await readFile(CSS, 'utf8'));
  }
  return { dossier, relevé: path.join(dossier, 'cache.json') };
}

async function lancer({ html, script, ancien } = {}) {
  const { dossier, relevé } = await racineFactice({ html, script, ancienCss: ancien });
  const env = {
    ...process.env,
    MRSC_TEST_URL: 'http://127.0.0.1:4181/',
    MRSC_CACHE_JSON: relevé,
  };
  delete env.MRSC_BROWSER_NODE_MODULES;
  delete env.MRSC_CAPTURES;
  delete env.MRSC_ANCIEN_CSS;
  if (ancien !== undefined) env.MRSC_ANCIEN_CSS = path.join(dossier, 'ancien.css');
  const execution = await new Promise((resoudre) => {
    const enfant = spawn(process.execPath, [path.join(dossier, 'outils', 'test-cache-css-ia.cjs')], {
      cwd: dossier,
      env,
    });
    let sortie = '';
    enfant.stdout.on('data', (morceau) => { sortie += morceau; });
    enfant.stderr.on('data', (morceau) => { sortie += morceau; });
    enfant.on('close', (statut) => resoudre({ statut, sortie }));
  });
  let contenu = null;
  if (existsSync(relevé)) contenu = JSON.parse(await readFile(relevé, 'utf8'));
  await rm(dossier, { recursive: true, force: true });
  return { ...execution, relevé: contenu };
}

const htmlReel = await readFile(PAGE, 'utf8');
const cssReel = await readFile(CSS, 'utf8');
const versionReelle = crypto.createHash('sha256').update(cssReel).digest('hex').slice(0, 16);

let echecs = 0;
function verifier(condition, message, contexte = '') {
  if (condition) return;
  echecs += 1;
  console.error(`  ÉCHEC — ${message}`);
  if (contexte) console.error(contexte.split('\n').map((ligne) => `    | ${ligne}`).join('\n'));
}

// Les mutations portent sur une copie, jamais sur le dépôt — et elles sont
// construites à partir du script réel : si l'attente ou l'interception changent
// de forme, le banc le dit au lieu de muter du vide.
const scriptReel = await readFile(SCRIPT, 'utf8');
const assertion = "cas==='ancienne-url' ? maximum>2 : maximum<=2";
const interception = 'await page.setRequestInterception(true);';
if (!scriptReel.includes(assertion)) {
  console.error('ÉCHEC — l\'attente des deux cas n\'est plus reconnaissable dans le script : le banc ne saurait plus quoi muter.');
  process.exit(1);
}
const appels = scriptReel.split(interception).length - 1;
if (appels !== 1) {
  console.error(`ÉCHEC — ${appels} appel(s) à setRequestInterception au lieu de 1 : le cas « sans interception » ne prouverait rien.`);
  process.exit(1);
}

const cas = [
  {
    nom: 'nominal : douze essais, deux URL distinctes, annonce conforme au relevé',
    entree: {},
    async verifier({ statut, sortie, relevé }) {
      verifier(statut === 0, 'le code de sortie devrait être 0', sortie);
      verifier(relevé !== null, 'le relevé devrait être écrit', sortie);
      const resultats = relevé?.resultats ?? [];
      verifier(resultats.length === 12, 'le relevé devrait contenir douze essais', String(resultats.length));
      // Le nombre annoncé n'est pas recopié : il est relu dans la sortie et
      // confronté au relevé. Un script qui annoncerait douze essais pour six
      // exécutés se lirait comme complet.
      const annonce = /(\d+) essais/.exec(sortie);
      verifier(annonce !== null && Number(annonce[1]) === resultats.length,
        "le nombre d'essais annoncé devrait être celui des essais exécutés", sortie);
      verifier(relevé?.version === versionReelle, 'la version relevée devrait être celle du CSS du dépôt',
        `${relevé?.version} ≠ ${versionReelle}`);
      const anciens = resultats.filter((r) => r.cas === 'ancienne-url');
      const versionnes = resultats.filter((r) => r.cas === 'url-versionnee');
      verifier(anciens.length === 6 && versionnes.length === 6, 'chaque cas devrait couvrir six essais',
        `${anciens.length} / ${versionnes.length}`);
      verifier(anciens.every((r) => r.requetes.includes('') && !r.requetes.includes(`?v=${versionReelle}`)),
        'le cas « ancienne-url » devrait demander la feuille sans version',
        JSON.stringify(anciens.map((r) => r.requetes)));
      verifier(versionnes.every((r) => r.requetes.includes(`?v=${versionReelle}`)),
        'le cas « url-versionnee » devrait demander la feuille versionnée',
        JSON.stringify(versionnes.map((r) => r.requetes)));
      verifier(anciens.every((r) => r.ecartMax > 2) && versionnes.every((r) => r.ecartMax <= 2),
        "les deux cas devraient se distinguer par l'écart mesuré",
        JSON.stringify(resultats.map((r) => [r.cas, r.largeur, r.disposition, r.ecartMax])));
      const configurations = new Set(resultats.map((r) => `${r.largeur}/${r.disposition}`));
      verifier(configurations.size === 6, 'les six configurations devraient être visitées', [...configurations].join(' '));
      verifier(resultats.every((r) => r.texte === 130), "chaque essai devrait déclarer son texte à 130 %",
        JSON.stringify(resultats[0]));
    },
  },
  {
    nom: 'version périmée : le refus tombe avant toute mesure, et n\'écrit rien',
    entree: { html: htmlReel.replace(`site.css?v=${versionReelle}`, 'site.css?v=0000000000000000') },
    async verifier({ statut, sortie, relevé }) {
      verifier(statut === 1, 'une version de CSS périmée devrait sortir en code 1', sortie);
      verifier(/Version CSS absente ou périmée/.test(sortie), 'le message devrait nommer le défaut', sortie);
      verifier(relevé === null, "aucun relevé ne devrait être écrit quand rien n'a été mesuré", sortie);
    },
  },
  {
    nom: 'attente inversée : les assertions mordent',
    entree: { script: scriptReel.replace(assertion, "cas==='ancienne-url' ? maximum<=2 : maximum>2") },
    async verifier({ statut, sortie }) {
      verifier(statut === 1, "échanger l'attente des deux cas devrait faire échouer le test", sortie);
      verifier(/ancienne-url|url-versionnee/.test(sortie), "l'échec devrait nommer le cas fautif", sortie);
    },
  },
  {
    nom: 'sans interception : le test ne peut plus servir, donc il échoue',
    entree: { script: scriptReel.split(interception).join('') },
    async verifier({ statut, sortie }) {
      verifier(statut === 1, "un test qui n'intercepte plus rien devrait échouer", sortie);
    },
  },
  {
    nom: 'ancien CSS identique au courant : le décalage ne vient pas de l\'URL',
    entree: { ancien: cssReel },
    async verifier({ statut, sortie }) {
      verifier(statut === 1, 'servir le CSS courant comme « ancien » devrait faire échouer le test', sortie);
    },
  },
];

for (const un of cas) {
  process.stdout.write(`— ${un.nom}\n`);
  const resultat = await lancer(un.entree);
  verifier(resultat.statut !== 2, 'le script ne devrait pas manquer de dépendances', resultat.sortie);
  await un.verifier(resultat);
}

if (echecs) {
  console.error(`\n${echecs} échec(s) — le banc n'a pas vérifié ce qu'il annonce.`);
  process.exit(1);
}
console.log(`\nOK — ${cas.length} cas : le test du cache CSS sert bien deux feuilles, et ses assertions mordent.`);
