#!/usr/bin/env node
/**
 * Banc de `auditer-affichages.mjs` : la mesure d'affichage, tous formats.
 *
 * Le script promène 13 pages dans 19 formats (du pliable 280 px au 4k 3840) et
 * 10 modes d'affichage enregistrés par le site (mise en page, taille de texte,
 * contraste, espacement), soit 2 470 mesures. Il cherche six défauts :
 * défilement horizontal, élément hors cadre, texte sous 12 px, image agrandie
 * par le navigateur, texte rogné, cible sous 24 px.
 *
 * Il n'avait aucun test. Deux mensonges sont possibles, et le second est le plus
 * grave :
 *
 * 1. ne pas voir un défaut — c'est le risque ordinaire d'une mesure ;
 * 2. **écrire un rapport à demi rempli** — le script écrit après la boucle ; si
 *    un chargement échoue, l'exception remonte et rien n'est écrit. Ce
 *    comportement n'était vérifié par personne, et c'est lui qui protège le
 *    rapport d'un contenu partiel présenté comme complet.
 *
 * Le banc remplace `puppeteer-core` et `@sparticuz/chromium` par les deux faux
 * de `outils/faux-navigateur/` et lance le script du dépôt, octet pour octet.
 * Particularité : contrairement aux trois autres scripts navigateur, celui-ci ne
 * lit aucune variable pour trouver ses dépendances — il les importe en modules
 * ES, donc Node les cherche dans un `node_modules` voisin. Le banc monte donc
 * une arborescence jetable : `outils/` copié (le script y est), toutes les
 * autres entrées liées symboliquement au dépôt, et les faux paquets dans
 * `node_modules`.
 *
 * **Le périmètre est réduit dans la copie jetable**, et c'est écrit ici parce
 * que cela change ce que le banc prouve. 2 470 mesures, chacune suivie d'une
 * pause de 120 ms dans le script, font **dix minutes par exécution** : mesuré
 * le 29 octobre 2026, avant cette réduction. La copie ne garde donc qu'une
 * page, un format et deux modes — 2 mesures, 0,3 s. Ce qui est éprouvé est le
 * **traitement** d'une mesure et le code de sortie, pas la couverture des
 * formats. La réduction se fait par ancres exactes : si le script était
 * reformaté, le banc échouerait bruyamment plutôt que de tester autre chose.
 *
 * Trois cas :
 *
 * - `nominal` : code 0, chaque mesure annoncée écrite dans le rapport, aucun défaut ;
 * - `affichage-defauts` : code 1, mesure fautive nommée avec son mode, sa page
 *   et son format, six compteurs présents même à zéro ;
 * - `echec-total` : arrêt non nul et **aucun rapport écrit**.
 *
 * La mesure de netteté d'image dépend d'ImageMagick (`convert`) pour connaître
 * la largeur réelle des fichiers ; sans lui, le script met 0 et ne signale rien.
 * Le banc ne suppose donc pas cette vérification faite, et ne la teste pas.
 *
 * Usage :
 *   node outils/test_auditer_affichages.mjs
 */

import { spawn } from 'node:child_process';
import { cp, mkdtemp, readdir, readFile, rm, symlink, writeFile } from 'node:fs/promises';
import { existsSync } from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import process from 'node:process';
import { fileURLToPath } from 'node:url';

const OUTILS = path.dirname(fileURLToPath(import.meta.url));
const RACINE = path.resolve(OUTILS, '..');
const FAUX = path.join(OUTILS, 'faux-navigateur');

/**
 * Réduit le périmètre de la copie jetable : une page, un format, deux modes.
 * Chaque remplacement vérifie son ancre et échoue si elle a bougé.
 */
async function reduirePerimetre(script) {
  const source = await readFile(script, 'utf8');
  const reductions = [
    [/const PAGES = \[[\s\S]*?\n\];/, "const PAGES = [\n  'index.html',\n];"],
    [/const FORMATS = \[[\s\S]*?\n\];/, "const FORMATS = [\n  ['pliable 280', 280, 653, 3, true],\n];"],
    [/const MODES = \[[\s\S]*?\n\];/, "const MODES = [\n  ['équilibrée', {}],\n  ['lecture', { 'mrsc-mise-en-page': 'lecture' }],\n];"],
  ];
  let reduit = source;
  for (const [motif, remplacement] of reductions) {
    if (!motif.test(reduit)) {
      throw new Error(`ancre introuvable dans auditer-affichages.mjs (${motif}) : le périmètre n'a pas pu être réduit`);
    }
    reduit = reduit.replace(motif, remplacement);
  }
  await writeFile(script, reduit, 'utf8');
}

/**
 * Arborescence jetable où le script peut importer les faux paquets.
 *
 * `outils/` est copié — c'est là que vit le script, et Node résout les modules
 * depuis son emplacement ; le reste est lié symboliquement, pour que
 * `assets/images` et les pages existent sans dupliquer le dépôt.
 */
async function arborescence() {
  const dossier = await mkdtemp(path.join(os.tmpdir(), 'mrsc-faux-affichages-'));
  const modules = path.join(dossier, 'node_modules');
  for (const paquet of ['puppeteer-core', path.join('@sparticuz', 'chromium')]) {
    await cp(path.join(FAUX, paquet), path.join(modules, paquet), { recursive: true });
  }
  for (const entree of await readdir(RACINE)) {
    if (['.git', 'node_modules', 'outils', '_site'].includes(entree)) continue;
    await symlink(path.join(RACINE, entree), path.join(dossier, entree));
  }
  await cp(path.join(RACINE, 'outils'), path.join(dossier, 'outils'), { recursive: true });
  const script = path.join(dossier, 'outils', 'auditer-affichages.mjs');
  await reduirePerimetre(script);
  return { dossier, script };
}

async function mesurer(mode) {
  const { dossier, script } = await arborescence();
  const rapport = path.join(dossier, 'affichages.json');
  const execution = await new Promise((resoudre) => {
    const enfant = spawn(process.execPath, [script], {
      cwd: dossier,
      env: { ...process.env, RAPPORT: rapport, FAUX_NAVIGATEUR_MODE: mode },
    });
    let sortie = '';
    enfant.stdout.on('data', (morceau) => { sortie += morceau; });
    enfant.stderr.on('data', (morceau) => { sortie += morceau; });
    enfant.on('close', (statut) => resoudre({ statut, sortie }));
  });
  let contenu = null;
  if (existsSync(rapport)) contenu = JSON.parse(await readFile(rapport, 'utf8'));
  await rm(dossier, { recursive: true, force: true });
  return { ...execution, rapport: contenu };
}

let echecs = 0;
function verifier(condition, message, contexte = '') {
  if (condition) return;
  echecs += 1;
  console.error(`  ÉCHEC — ${message}`);
  if (contexte) console.error(contexte.split('\n').slice(0, 30).map((ligne) => `    | ${ligne}`).join('\n'));
}

/** Le script annonce « N mesures · M avec défaut » : le banc lit ce décompte. */
function decompte(sortie) {
  const annonce = sortie.match(/\n(\d+) mesures · (\d+) avec défaut/);
  return {
    mesures: annonce ? Number(annonce[1]) : null,
    defauts: annonce ? Number(annonce[2]) : null,
  };
}

const cas = [
  {
    nom: 'nominal : chaque mesure annoncée est écrite, aucun défaut',
    mode: 'nominal',
    async verifier({ statut, sortie, rapport }) {
      verifier(statut === 0, 'le code de sortie devrait être 0', sortie);
      const { mesures, defauts } = decompte(sortie);
      // Deux modes × une page × un format : le total vient de la réduction
      // appliquée à la copie, pas d'un chiffre recopié du script d'origine.
      verifier(mesures === 2, 'la copie réduite devrait produire deux mesures', sortie.slice(-600));
      verifier(defauts === 0, 'aucun défaut ne devrait être compté', sortie.slice(-600));
      verifier(rapport && rapport.length === mesures, 'le rapport devrait contenir une entrée par mesure', String(rapport?.length));
      const premiere = rapport?.[0] || {};
      verifier(premiere.mode === 'équilibrée' && premiere.page === 'index.html' && premiere.format === 'pliable 280',
        'la première mesure devrait nommer son mode, sa page et son format', JSON.stringify(premiere).slice(0, 300));
      // Six compteurs, présents même à zéro : une clé absente se lirait comme
      // une non-mesure, alors que le script les écrit toujours.
      for (const cle of ['defilementHorizontal', 'nbDehors', 'nbTexteFin', 'nbImagesAgrandies', 'nbTextesCoupes', 'nbCiblesPetites']) {
        verifier(cle in premiere, `le compteur « ${cle} » devrait figurer dans chaque mesure`, JSON.stringify(Object.keys(premiere)));
      }
    },
  },
  {
    nom: 'défauts : chaque mesure fautive est nommée avec sa configuration',
    mode: 'affichage-defauts',
    async verifier({ statut, sortie, rapport }) {
      verifier(statut === 1, 'un défaut d\'affichage devrait sortir en code 1', sortie);
      const { mesures, defauts } = decompte(sortie);
      verifier(defauts === mesures, 'chaque mesure devrait compter comme fautive', `défauts ${defauts} / mesures ${mesures}`);
      verifier(/équilibrée \/ index\.html @ pliable 280 :: débordement 12px \| 2 hors cadre \| 1 cible<24px/.test(sortie),
        'le défaut devrait être nommé avec son mode, sa page, son format et ses compteurs', sortie.slice(-800));
      verifier(rapport && rapport.every((entree) => entree.nbDehors === 2 && entree.nbCiblesPetites === 1),
        'le rapport devrait garder les compteurs mesurés', JSON.stringify(rapport?.[0]));
    },
  },
  {
    nom: 'chargement impossible : arrêt non nul, aucun rapport partiel',
    mode: 'echec-total',
    async verifier({ statut, sortie, rapport }) {
      verifier(statut !== 0, 'un chargement impossible ne doit pas sortir en succès', sortie);
      verifier(/ERR_CONNECTION_REFUSED/.test(sortie), 'la cause devrait être écrite', sortie);
      verifier(rapport === null, 'aucun rapport ne devrait être écrit quand la boucle est interrompue', JSON.stringify(rapport)?.slice(0, 200));
    },
  },
];

for (const un of cas) {
  const resultat = await mesurer(un.mode);
  const avant = echecs;
  await un.verifier(resultat);
  console.log(`${echecs === avant ? 'ok' : 'ÉCHEC'} — ${un.nom}`);
}

if (echecs) {
  console.error(`\n${echecs} vérification(s) en échec.`);
  process.exitCode = 1;
} else {
  console.log('\nOK — 3 cas : une mesure interrompue ne laisse pas de rapport à demi rempli.');
}
