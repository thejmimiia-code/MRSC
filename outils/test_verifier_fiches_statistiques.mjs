#!/usr/bin/env node
/**
 * Banc de `verifier-fiches-statistiques.cjs` : la géométrie de deux fiches.
 *
 * Ce script promène deux fiches d'apprentissage dans 288 configurations
 * (4 largeurs × 3 tailles de texte × 6 dispositions × contraste et espacement
 * renforcés) et cherche trois choses : un élément hors écran, un contenu rogné,
 * et l'absence du statut « Prototype à relire ». Il écrit un relevé JSON et sort
 * en erreur au premier échec.
 *
 * Il n'avait aucun test, et son pire défaut possible est celui qu'on ne voit
 * pas : produire un relevé **vide ou absent** et laisser croire que tout va
 * bien. Un fichier d'audit qui n'existe pas ne dit rien ; un fichier d'audit
 * vide dit « zéro échec ».
 *
 * Le banc remplace `puppeteer-core` et `@sparticuz/chromium` par deux faux
 * (`outils/faux-navigateur/`) et lance **le vrai script**. Quatre cas :
 *
 * 1. nominal : code 0, `288 relevés, 0 échecs`, relevé JSON de 288 entrées ;
 * 2. géométrie fautive : code 1, 288 échecs comptés, l'erreur nommée dans le JSON ;
 * 3. statut absent : code 1, « statut absent » relevé — le contrôle de statut
 *    n'est pas avalé par le contrôle géométrique ;
 * 4. chargement impossible : code 2, et **aucun relevé écrit** — un audit qui
 *    n'a rien pu mesurer ne doit pas laisser un fichier derrière lui.
 *
 * Le relevé est toujours écrit hors du dépôt : le script, lui, écrit par défaut
 * dans `docs/rd/`, et un banc qui écraserait le relevé commité serait un dégât.
 *
 * Usage :
 *   node outils/test_verifier_fiches_statistiques.mjs
 */

import { spawn } from 'node:child_process';
import { cp, mkdtemp, readFile, rm } from 'node:fs/promises';
import { existsSync } from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import process from 'node:process';
import { fileURLToPath } from 'node:url';

const OUTILS = path.dirname(fileURLToPath(import.meta.url));
const RACINE = path.resolve(OUTILS, '..');
const FAUX = path.join(OUTILS, 'faux-navigateur');
const SCRIPT = path.join(OUTILS, 'verifier-fiches-statistiques.cjs');
const RELEVE_COMMITE = path.join(RACINE, 'docs', 'rd', 'audit-fiches-statistiques-2026-10-24.json');

/** `node_modules` jetable contenant les deux faux paquets. */
async function fauxModules() {
  const dossier = await mkdtemp(path.join(os.tmpdir(), 'mrsc-faux-fiches-'));
  const modules = path.join(dossier, 'node_modules');
  await cp(path.join(FAUX, 'puppeteer-core'), path.join(modules, 'puppeteer-core'), { recursive: true });
  await cp(path.join(FAUX, '@sparticuz', 'chromium'), path.join(modules, '@sparticuz', 'chromium'), { recursive: true });
  return { dossier, modules };
}

async function verifierFiches(mode) {
  const { dossier, modules } = await fauxModules();
  const releve = path.join(dossier, 'audit.json');
  const execution = await new Promise((resoudre) => {
    const enfant = spawn(process.execPath, [SCRIPT], {
      cwd: RACINE,
      env: {
        ...process.env,
        MRSC_BROWSER_NODE_MODULES: modules,
        MRSC_FICHES_JSON: releve,
        FAUX_NAVIGATEUR_MODE: mode,
      },
    });
    let sortie = '';
    enfant.stdout.on('data', (morceau) => { sortie += morceau; });
    enfant.stderr.on('data', (morceau) => { sortie += morceau; });
    enfant.on('close', (statut) => resoudre({ statut, sortie }));
  });
  let contenu = null;
  if (existsSync(releve)) contenu = JSON.parse(await readFile(releve, 'utf8'));
  await rm(dossier, { recursive: true, force: true });
  return { ...execution, releve: contenu };
}

let echecs = 0;
function verifier(condition, message, contexte = '') {
  if (condition) return;
  echecs += 1;
  console.error(`  ÉCHEC — ${message}`);
  if (contexte) console.error(contexte.split('\n').map((ligne) => `    | ${ligne}`).join('\n'));
}

// Le relevé commité ne doit pas bouger : c'est un fait daté, pas un fichier de travail.
const empreinteAvant = existsSync(RELEVE_COMMITE) ? await readFile(RELEVE_COMMITE, 'utf8') : null;

const cas = [
  {
    nom: 'nominal : 288 relevés, aucun échec, relevé écrit',
    mode: 'nominal',
    async verifier({ statut, sortie, releve }) {
      verifier(statut === 0, 'le code de sortie devrait être 0', sortie);
      verifier(/288 relevés, 0 échecs/.test(sortie), 'le bilan devrait annoncer 288 relevés sans échec', sortie);
      verifier(releve && releve.releves.length === 288, 'le relevé devrait contenir 288 entrées', JSON.stringify(releve?.releves?.length));
      verifier(releve && releve.erreurs.length === 0, 'le relevé ne devrait contenir aucun échec', JSON.stringify(releve?.erreurs?.length));
      // Le périmètre écrit dans le fichier dit ce qui n'a pas été mesuré : sans
      // cette phrase, un relevé de géométrie se lit comme un audit complet.
      verifier(releve && /ni lecteur d’écran ni compréhension/.test(releve.perimetre), 'le relevé devrait déclarer son périmètre et ses limites', releve?.perimetre);
      const fiche = releve?.releves?.[0] || {};
      verifier(fiche.largeur === 320 && fiche.texte === 100 && fiche.disposition === 'equilibree',
        'chaque relevé devrait nommer sa configuration', JSON.stringify(fiche));
    },
  },
  {
    nom: 'géométrie fautive : chaque configuration est comptée en échec',
    mode: 'fiches-erreurs',
    async verifier({ statut, sortie, releve }) {
      verifier(statut === 1, 'un échec de géométrie devrait sortir en code 1', sortie);
      verifier(/288 relevés, 288 échecs/.test(sortie), 'les 288 configurations devraient être en échec', sortie);
      verifier(releve && releve.erreurs.length === 288, 'le relevé devrait garder les 288 échecs', JSON.stringify(releve?.erreurs?.length));
      verifier(releve && releve.erreurs[0].erreurs.includes('MAIN hors écran'), 'l\'erreur mesurée devrait être nommée', JSON.stringify(releve?.erreurs?.[0]));
    },
  },
  {
    nom: 'statut absent : le contrôle de statut n\'est pas avalé',
    mode: 'fiches-statut-absent',
    async verifier({ statut, sortie, releve }) {
      verifier(statut === 1, 'une fiche sans statut devrait sortir en code 1', sortie);
      verifier(releve && releve.erreurs.every((entree) => entree.erreurs.includes('statut absent')),
        'chaque configuration devrait relever le statut absent', JSON.stringify(releve?.erreurs?.[0]));
    },
  },
  {
    nom: 'chargement impossible : code 2, et aucun relevé trompeur',
    mode: 'echec-total',
    async verifier({ statut, sortie, releve }) {
      verifier(statut === 2, 'un chargement impossible devrait sortir en code 2', sortie);
      verifier(/ERR_CONNECTION_REFUSED/.test(sortie), 'la cause devrait être écrite', sortie);
      verifier(releve === null, 'aucun relevé ne devrait être écrit quand rien n\'a été mesuré', JSON.stringify(releve)?.slice(0, 200));
    },
  },
];

for (const un of cas) {
  const resultat = await verifierFiches(un.mode);
  const avant = echecs;
  await un.verifier(resultat);
  console.log(`${echecs === avant ? 'ok' : 'ÉCHEC'} — ${un.nom}`);
}

// Le script écrit par défaut dans `docs/rd/` : le banc vérifie qu'il n'y a pas touché.
const empreinteApres = existsSync(RELEVE_COMMITE) ? await readFile(RELEVE_COMMITE, 'utf8') : null;
verifier(empreinteApres === empreinteAvant, 'le relevé commité a été modifié par le banc', RELEVE_COMMITE);
console.log(`${empreinteApres === empreinteAvant ? 'ok' : 'ÉCHEC'} — le relevé commité est intact`);

if (echecs) {
  console.error(`\n${echecs} vérification(s) en échec.`);
  process.exitCode = 1;
} else {
  console.log('\nOK — 5 cas : la géométrie peut échouer, et un relevé impossible ne laisse pas de fichier.');
}
