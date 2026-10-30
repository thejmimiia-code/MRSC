#!/usr/bin/env node
/**
 * Banc de `verifier-graphismes.cjs` — non pas ce qu'il fait d'un rapport, mais
 * **ce qu'il mesure**.
 *
 * Le 29 octobre 2026, deux bancs voisins éprouvaient déjà ce script : ses trois
 * mutations internes doivent produire l'erreur annoncée (`verifier-mutation-graphismes.py`,
 * six cas hors ligne). Mais aucun ne disait que la géométrie relevée est la
 * bonne. Un `getBoundingClientRect` mal interprété, un `naturalWidth` recopié au
 * lieu des dimensions décodées, une densité calculée à l'envers : tout cela
 * resterait vert, puisque les mutations sont plantées par le script lui-même.
 *
 * Ce banc mesure donc une **page de contrôle** aux dimensions connues, servie
 * depuis un dossier temporaire, avec un vrai Chromium :
 *
 * - `conforme` : image 600 × 300 dans une boîte 200 × 100 (rapport 2 de part et
 *   d'autre) → aucune erreur, densité 3 à chaque densité d'écran ;
 * - `distordu` : la même image dans une boîte 200 × 200 → « distorsion » et
 *   « ratio de boîte différent de la source » ;
 * - `basse-densite` : image 60 × 30 dans une boîte 200 × 100 → « densité
 *   insuffisante » à 1 comme à 2 pixels par point ;
 * - `perimetre` : le rapport réduit doit le dire, sinon un relevé de quatre
 *   lignes se lirait comme l'audit complet.
 *
 * Les nombres du rapport sont confrontés à l'arithmétique, pas à des constantes
 * recopiées : `densite = largeur native / largeur rendue`, `distorsion =
 * |rapport de boîte − rapport natif|`. Et les dimensions attendues viennent du
 * CSS écrit par le banc, pas d'une supposition.
 *
 * Limite : ceci éprouve la mesure sur une image **PNG simple**, à une seule
 * disposition, une seule taille de texte et un seul mode de contraste — le
 * périmètre réduit (`MRSC_PERIMETRE_REDUIT=1`). Les trois pages réelles, les
 * `srcset` et la constellation ne sont pas couvertes ici.
 *
 * Usage : node outils/test_mesure_graphismes.mjs
 * (demande Chromium : `MRSC_BROWSER_NODE_MODULES` en CI, rien en local.)
 */

import { spawn } from 'node:child_process';
import { mkdtemp, writeFile, readFile, rm } from 'node:fs/promises';
import { existsSync } from 'node:fs';
import { createServer } from 'node:http';
import { deflateSync } from 'node:zlib';
import os from 'node:os';
import path from 'node:path';
import process from 'node:process';
import { fileURLToPath } from 'node:url';

const OUTILS = path.dirname(fileURLToPath(import.meta.url));
const RACINE = path.resolve(OUTILS, '..');
const SCRIPT = path.join(OUTILS, 'verifier-graphismes.cjs');

/* ── Un PNG unicolore, sans dépendance ─────────────────────────────────────── */

const TABLE_CRC = Array.from({ length: 256 }, (_, n) => {
  let c = n;
  for (let k = 0; k < 8; k += 1) c = c & 1 ? 0xedb88320 ^ (c >>> 1) : c >>> 1;
  return c >>> 0;
});

function crc32(tampon) {
  let c = 0xffffffff;
  for (const octet of tampon) c = TABLE_CRC[(c ^ octet) & 0xff] ^ (c >>> 8);
  return (c ^ 0xffffffff) >>> 0;
}

function bloc(type, donnees) {
  const longueur = Buffer.alloc(4);
  longueur.writeUInt32BE(donnees.length);
  const corps = Buffer.concat([Buffer.from(type, 'latin1'), donnees]);
  const controle = Buffer.alloc(4);
  controle.writeUInt32BE(crc32(corps));
  return Buffer.concat([longueur, corps, controle]);
}

/** PNG RGB 8 bits : une couleur unie suffit, aucune compression à écrire à la main. */
function png(largeur, hauteur, [r, v, b] = [30, 60, 120]) {
  const entete = Buffer.alloc(13);
  entete.writeUInt32BE(largeur, 0);
  entete.writeUInt32BE(hauteur, 4);
  entete[8] = 8; // profondeur
  entete[9] = 2; // couleur RVB
  const ligne = Buffer.alloc(1 + largeur * 3);
  for (let x = 0; x < largeur; x += 1) {
    ligne[1 + x * 3] = r;
    ligne[2 + x * 3] = v;
    ligne[3 + x * 3] = b;
  }
  const brut = Buffer.concat(Array.from({ length: hauteur }, () => ligne));
  return Buffer.concat([
    Buffer.from([0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a]),
    bloc('IHDR', entete),
    bloc('IDAT', deflateSync(brut)),
    bloc('IEND', Buffer.alloc(0)),
  ]);
}

/* ── Les pages de contrôle ─────────────────────────────────────────────────── */

/**
 * La page ressemble à ce que le script attend : `index.html`, et un
 * `.home-hero-visual` qui contient une image. Le reste — la boîte — est écrit
 * ici, en pixels, pour que l'attendu ne soit pas une supposition.
 */
function pageControle({ image, largeurBoite, hauteurBoite }) {
  return `<!doctype html>
<html lang="fr"><head><meta charset="utf-8"><title>Page de contrôle</title>
<style>
  html, body { margin: 0; padding: 0; background: #fff; }
  .home-hero-visual { display: block; width: 900px; height: 600px; }
  .home-hero-visual img { display: block; width: ${largeurBoite}px; height: ${hauteurBoite}px; }
</style></head>
<body><div class="home-hero-visual"><img src="${image}" alt=""></div></body></html>
`;
}

const CAS = [
  {
    nom: 'conforme : image 600 × 300 dans une boîte 200 × 100, aucune erreur',
    natif: [600, 300],
    boite: [200, 100],
    erreurs: [],
    densite: 3,
    distorsion: 0,
  },
  {
    nom: 'distordu : boîte 200 × 200 pour une image 600 × 300, deux erreurs nommées',
    natif: [600, 300],
    boite: [200, 200],
    erreurs: ['ratio de boîte différent de la source', 'distorsion'],
    densite: 3,
    distorsion: 0.5,
  },
  {
    nom: 'basse densité : image 60 × 30 dans une boîte 200 × 100, insuffisante aux deux densités',
    natif: [60, 30],
    boite: [200, 100],
    erreurs: ['densité insuffisante'],
    densite: 0.3,
    distorsion: 0,
  },
];

/* ── Le harnais ────────────────────────────────────────────────────────────── */

function servir(dossier) {
  const serveur = createServer(async (requete, reponse) => {
    const chemin = path.join(dossier, decodeURIComponent(new URL(requete.url, 'http://x').pathname));
    if (!chemin.startsWith(dossier) || !existsSync(chemin)) {
      reponse.writeHead(404).end('absent');
      return;
    }
    const type = chemin.endsWith('.png') ? 'image/png' : 'text/html; charset=utf-8';
    reponse.writeHead(200, { 'content-type': type, 'cache-control': 'no-store' });
    reponse.end(await readFile(chemin));
  });
  return new Promise((resoudre) => {
    serveur.listen(0, '127.0.0.1', () => resoudre({ serveur, port: serveur.address().port }));
  });
}

async function mesurer(cas) {
  const dossier = await mkdtemp(path.join(os.tmpdir(), 'mrsc-mesure-graphismes-'));
  await writeFile(path.join(dossier, 'figure.png'), png(...cas.natif));
  await writeFile(path.join(dossier, 'index.html'), pageControle({
    image: 'figure.png', largeurBoite: cas.boite[0], hauteurBoite: cas.boite[1],
  }));
  const releve = path.join(dossier, 'releve.json');
  const { serveur, port } = await servir(dossier);
  try {
    const execution = await new Promise((resoudre) => {
      const enfant = spawn(process.execPath, [SCRIPT], {
        cwd: RACINE,
        env: {
          ...process.env,
          MRSC_TEST_URL: `http://127.0.0.1:${port}/`,
          MRSC_GRAPHISMES_JSON: releve,
          MRSC_PAGES: 'index.html',
          MRSC_PERIMETRE_REDUIT: '1',
          MRSC_MUTATION: '',
        },
      });
      let sortie = '';
      enfant.stdout.on('data', (morceau) => { sortie += morceau; });
      enfant.stderr.on('data', (morceau) => { sortie += morceau; });
      enfant.on('close', (statut) => resoudre({ statut, sortie }));
    });
    const rapport = existsSync(releve) ? JSON.parse(await readFile(releve, 'utf8')) : null;
    return { ...execution, rapport };
  } finally {
    await new Promise((resoudre) => serveur.close(resoudre));
    await rm(dossier, { recursive: true, force: true });
  }
}

let echecs = 0;
function verifier(condition, message, contexte = '') {
  if (condition) return;
  echecs += 1;
  console.error(`  ÉCHEC — ${message}`);
  if (contexte) console.error(contexte.split('\n').slice(0, 30).map((ligne) => `    | ${ligne}`).join('\n'));
}

// Le script est lancé tel quel : sans Chromium, il sort en 2 avant d'avoir rien
// mesuré, et le banc doit le dire plutôt que d'afficher un succès vide.
for (const cas of CAS) {
  process.stdout.write(`— ${cas.nom}\n`);
  const { statut, sortie, rapport } = await mesurer(cas);
  // Sans les paquets navigateur, il n'y a rien à mesurer : le dire avec un code
  // distinct (2) plutôt que d'aligner des échecs qui accuseraient le contrôle.
  if (/Cannot find module 'puppeteer-core'/.test(sortie) || /Cannot find module '@sparticuz\//.test(sortie)) {
    console.error('Environnement : ni Chromium ni les faux paquets ne sont installés. Banc non exécuté — ce n\'est pas un succès.');
    console.error('  npm install --prefix /tmp/mrsc-browser puppeteer-core@25.16.0 @sparticuz/chromium@153.0.0');
    console.error('  MRSC_BROWSER_NODE_MODULES=/tmp/mrsc-browser/node_modules node outils/test_mesure_graphismes.mjs');
    process.exit(2);
  }
  if (statut === 2) {
    verifier(false, 'le script n’a pas pu démarrer Chromium — aucune mesure n’a eu lieu', sortie);
    continue;
  }
  verifier(rapport !== null, 'le rapport devrait être écrit même en échec', sortie);
  if (!rapport) continue;

  // Un relevé réduit doit se déclarer réduit : quatre lignes ne sont pas l'audit.
  verifier(rapport.reduit === true && /Périmètre réduit/.test(rapport.perimetre || ''),
    'le rapport devrait déclarer son périmètre réduit', JSON.stringify(rapport.perimetre));

  const lignes = rapport.releves ?? [];
  verifier(lignes.length === 4, 'quatre relevés attendus (deux largeurs × deux densités d’écran)',
    String(lignes.length));

  for (const ligne of lignes) {
    const ou = `${ligne.page} ${ligne.largeur}px dpr${ligne.dpr}`;
    // Les dimensions natives sont celles du fichier écrit par le banc, pas
    // celles qu'une image d'exemple porterait : si le script recopiait
    // `naturalWidth`, ce contrôle le verrait à la première divergence.
    verifier(ligne.native?.w === cas.natif[0] && ligne.native?.h === cas.natif[1],
      `${ou} : dimensions natives ${JSON.stringify(ligne.native)} au lieu de ${cas.natif.join('×')}`);
    verifier(Math.abs(ligne.rendu?.w - cas.boite[0]) < 0.5 && Math.abs(ligne.rendu?.h - cas.boite[1]) < 0.5,
      `${ou} : boîte rendue ${JSON.stringify(ligne.rendu)} au lieu de ${cas.boite.join('×')}`);
    // L'arithmétique, pas une constante : densité et distorsion sont recalculées
    // à partir du relevé et comparées à ce que le script annonce.
    const densiteAttendue = cas.natif[0] / ligne.rendu.w;
    verifier(Math.abs(ligne.densite - densiteAttendue) < 0.01,
      `${ou} : densité ${ligne.densite} au lieu de ${densiteAttendue.toFixed(2)}`);
    const distorsionAttendue = Math.abs((ligne.rendu.w / ligne.rendu.h) - (cas.natif[0] / cas.natif[1]));
    verifier(Math.abs(ligne.distorsion - distorsionAttendue) < 0.001,
      `${ou} : distorsion ${ligne.distorsion} au lieu de ${distorsionAttendue.toFixed(3)}`);
    const erreurs = new Set(ligne.erreurs || []);
    for (const attendue of cas.erreurs) {
      verifier(erreurs.has(attendue), `${ou} : erreur « ${attendue} » absente`, JSON.stringify([...erreurs]));
    }
    if (!cas.erreurs.length) {
      verifier(erreurs.size === 0, `${ou} : erreurs inattendues`, JSON.stringify([...erreurs]));
    }
  }

  const erreurs = (rapport.erreurs ?? []).length;
  verifier(erreurs === (cas.erreurs.length ? lignes.length : 0),
    `${cas.erreurs.length ? `${lignes.length} relevés en échec attendus` : 'aucun échec attendu'}, ${erreurs} constaté(s)`);
  verifier(statut === (cas.erreurs.length ? 1 : 0), `code de sortie ${statut}`, sortie.split('\n').slice(-6).join('\n'));
}

if (echecs) {
  console.error(`\n${echecs} échec(s) — la mesure des graphismes ne dit pas ce qu'elle prétend.`);
  process.exit(1);
}
console.log(`\nOK — ${CAS.length} pages de contrôle : dimensions natives, boîte rendue, densité et distorsion correspondent à l'arithmétique ; un relevé réduit le déclare.`);
