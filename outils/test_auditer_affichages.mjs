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
 * Cinq cas :
 *
 * - `nominal` : code 0, chaque mesure annoncée écrite dans le rapport, aucun défaut ;
 * - `affichage-defauts` : code 1, mesure fautive nommée avec son mode, sa page
 *   et son format, six compteurs présents même à zéro ;
 * - `echec-total` : arrêt non nul et **aucun rapport écrit** ;
 * - `texte-fin-decor` : code 0, le chevron décoratif `aria-hidden` à
 *   `font-size: 0` n'est **pas** compté comme texte sous 12 px, et l'écart
 *   laisse une trace chiffrée dans chaque mesure ;
 * - `texte-fin-reel` : code 1, un vrai texte à corps réduit reste compté, le
 *   filtre ne sert pas de congé général.
 *
 * Les deux derniers cas éprouvent un **filtre**, pas un compteur : le faux
 * navigateur, lui, ne simule aucun DOM. Le banc **extrait du script, par
 * ancres exactes, la fonction de mesure réellement envoyée au navigateur**, et
 * l'exécute sur trois DOM témoins écrits ici (un décor `aria-hidden` à
 * `font-size: 0`, un vrai texte à 11 px, un `aria-hidden` visible à 11 px). Ce
 * n'est pas une mesure de navigateur — aucune géométrie n'est calculée — mais
 * c'est bien le code du dépôt qui tranche, octet pour octet. C'est ce que le
 * relevé du 6 novembre 2026 réclamait : la correction est « à faire dans
 * l'outil, pas dans la feuille de style », et elle « demande un banc qui
 * exécute réellement le filtre, alors que le banc actuel remplace le navigateur
 * par un faux qui renvoie directement les compteurs ».
 *
 * Les trois DOM témoins portent chacun un piège : sans le filtre, le décor fait
 * échouer le premier cas ; avec un filtre trop large, le troisième (visible
 * mais masqué aux technologies d'assistance) disparaîtrait à tort.
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
import { existsSync, readFileSync } from 'node:fs';
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

/**
 * Le filtre de « texte sous 12 px », éprouvé sur un DOM témoin.
 *
 * Le script réel n'est pas lancé ici : sa boucle exige un navigateur. Le banc
 * extrait donc du fichier du dépôt la fonction `evaluate` qui **part dans le
 * navigateur** (celle qui reçoit `largeurVue, densiteVue, largeursFichiers`),
 * et la fait tourner dans un interpréteur minimal qui ne calcule aucune
 * géométrie : chaque élément témoin déclare sa boîte et son style à la main.
 *
 * Ce n'est pas une mesure d'affichage. C'est l'exécution du vrai code du dépôt
 * sur des entrées choisies, seule façon de prouver un filtre sans navigateur —
 * le faux `puppeteer-core` renvoie des compteurs déjà calculés et ne peut rien
 * prouver de tel.
 */
function extraireMesure(script) {
  const source = readFileSync(script, 'utf8');
  const debut = source.indexOf('const mesure = await onglet.evaluate((largeurVue, densiteVue, largeursFichiers) => {');
  if (debut === -1) {
    throw new Error('ancre introuvable : la fonction de mesure d’auditer-affichages.mjs a changé de forme');
  }
  const marqueur = '\n      }, largeur, densite, LARGEURS);';
  const fin = source.indexOf(marqueur, debut);
  if (fin === -1) {
    throw new Error('ancre introuvable : la fin de l’appel onglet.evaluate a changé de forme');
  }
  const bloc = source.slice(debut, fin);
  const ouverture = bloc.indexOf('=> {') + '=> {'.length;
  return { bloc, corps: bloc.slice(ouverture) };
}

/**
 * Interprète le corps de la fonction de mesure sur des éléments témoins.
 *
 * Trois écarts assumés, tous écrits ici :
 *   - `getComputedStyle` lit un style déclaré à la main, jamais une cascade ;
 *   - `getBoundingClientRect` lit une boîte déclarée ;
 *   - `parentElement` remonte la liste plate fournie.
 * Tout le reste — noms de défauts, compteurs, `uniques`, seuils — est le code
 * du script, exécuté tel quel. Si une clé manquait dans un témoin, le banc
 * échouerait bruyamment plutôt que de rendre un compteur trompeur.
 */
function executerMesure(corps, temoins, largeurVue = 320, densite = 1) {
  const elements = temoins.map((t) => ({
    tagName: t.tagName,
    className: t.className || '',
    children: t.children || [],
    textContent: t.textContent || '',
    parentElement: null,
    naturalWidth: t.naturalWidth || 0,
    currentSrc: t.currentSrc || '',
    src: t.src || '',
    style: {},
    scrollWidth: t.scrollWidth || 0,
    clientWidth: t.clientWidth || 0,
    getBoundingClientRect: () => t.boite || { left: 0, top: 0, right: 100, bottom: 20, width: 100, height: 20 },
    // Seuls les décors masqués aux technologies d'assistance déclarent un
    // ancêtre `.visually-hidden` : c'est ce que `closest` sert à distinguer.
    closest: (selecteur) => (selecteur === '.visually-hidden' && t.masqueAuxLecteurs ? t : null),
    // `aria-hidden` tel que le DOM le rend : absent, donc `null`, ou « true ».
    getAttribute: (nom) => (nom === 'aria-hidden' && t.ariaHidden ? 'true' : null),
  }));
  const cibles = elements.filter((e) => ['A', 'BUTTON', 'INPUT', 'SELECT', 'SUMMARY'].includes(e.tagName));
  const document_ = {
    documentElement: { scrollWidth: largeurVue, clientWidth: largeurVue },
    body: { querySelectorAll: (selecteur) => (selecteur.startsWith('a,') ? cibles : elements) },
  };
  const getComputedStyle = (element) => {
    const t = temoins[elements.indexOf(element)] || {};
    return {
      display: t.display || 'block',
      visibility: t.visibility || 'visible',
      opacity: t.opacity ?? '1',
      position: t.position || 'static',
      fontSize: `${t.fontSize ?? 16}px`,
      overflowX: t.overflowX || 'visible',
    };
  };
  // Les trois paramètres de la fonction réelle, liés au lieu d'être passés :
  // `new Function` ne reçoit que ce qu'on lui nomme.
  const fonction = new Function('document', 'getComputedStyle', 'Number',
    `const largeurVue = ${largeurVue}; const densiteVue = ${densite};` +
    ' const largeursFichiers = {};' + corps);
  return fonction(document_, getComputedStyle, Number);
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

/** Les trois DOM témoins du filtre « texte sous 12 px ». */
const TEMOINS = {
  // Le défaut réel du relevé du 6 novembre 2026 : le chevron du panneau de
  // personnalisation est un masque SVG (`font-size: 0`) porteur d'un caractère,
  // déclaré `aria-hidden`. Il n'affiche aucun texte : il ne doit pas compter.
  decor: {
    nom: 'chevron décoratif aria-hidden, font-size 0',
    element: {
      tagName: 'SPAN',
      className: 'customize-settings-chevron',
      textContent: '⌄',
      fontSize: 0,
      ariaHidden: true,
    },
    attendu: 0,
  },
  // Même condition de taille, mais aucune raison de l'écarter : 11 px de texte
  // réel restent un défaut de lisibilité, et le filtre ne doit pas le taire.
  texte: {
    nom: 'vrai texte à 11 px',
    element: { tagName: 'P', className: 'note', textContent: 'Une phrase', fontSize: 11 },
    attendu: 1,
  },
  // Un élément qui ne portait aucun texte n'a jamais été un défaut de
  // « texte sous 12 px » : l'écarter ne serait pas une correction, et le
  // compter gonflerait le chiffre d'une non-mesure.
  vide: {
    nom: 'aria-hidden à corps nul et sans texte',
    element: { tagName: 'SPAN', className: 'motif', textContent: '', fontSize: 0, ariaHidden: true },
    attendu: 0,
  },
  // Le piège de l'autre côté : masqué aux lecteurs d'écran, mais visible à
  // l'œil et trop petit. Un filtre qui écarte tout `aria-hidden` le perdrait.
  visibleMasque: {
    nom: 'aria-hidden visible à 11 px',
    element: {
      tagName: 'P',
      className: 'apercu',
      textContent: 'Rendu',
      fontSize: 11,
      ariaHidden: true,
    },
    attendu: 1,
  },
};

cas.push(
  {
    nom: 'filtre : un aria-hidden vide ne gonfle pas le compte des décors écartés',
    async verifier() {
      const { corps } = extraireMesure(path.join(RACINE, 'outils', 'auditer-affichages.mjs'));
      const mesure = executerMesure(corps, [TEMOINS.vide.element]);
      verifier(mesure.nbTexteFin === 0,
        'un élément sans texte ne devrait pas compter comme texte fin', JSON.stringify(mesure.texteFin));
      verifier(mesure.nbDecorsEcartes === 0,
        'un élément sans texte ne devrait pas compter comme décor écarté : l’écart ne mesure pas une non-mesure',
        JSON.stringify(mesure.decorsEcartes));
    },
  },
  {
    nom: 'filtre : le décor aria-hidden à font-size 0 ne compte pas comme texte fin',
    async verifier() {
      const { corps } = extraireMesure(path.join(RACINE, 'outils', 'auditer-affichages.mjs'));
      const mesure = executerMesure(corps, [
        TEMOINS.decor.element,
      ]);
      verifier(mesure.nbTexteFin === TEMOINS.decor.attendu,
        `le décor devrait compter ${TEMOINS.decor.attendu} texte(s) fin(s), il en compte ${mesure.nbTexteFin}`,
        JSON.stringify(mesure.texteFin));
      verifier(mesure.nbDecorsEcartes === 1,
        'le décor écarté devrait laisser une trace chiffrée (`nbDecorsEcartes = 1`), sinon l’écart est invisible',
        JSON.stringify(Object.keys(mesure)));
      verifier(mesure.decorsEcartes?.length === 1 &&
        mesure.decorsEcartes[0].selecteur === 'span.customize-settings-chevron',
        'le décor écarté devrait être nommé, pas seulement compté', JSON.stringify(mesure.decorsEcartes));
    },
  },
  {
    nom: 'filtre : un vrai texte à 11 px reste compté',
    async verifier() {
      const { corps } = extraireMesure(path.join(RACINE, 'outils', 'auditer-affichages.mjs'));
      const mesure = executerMesure(corps, [
        TEMOINS.texte.element,
      ]);
      verifier(mesure.nbTexteFin === TEMOINS.texte.attendu,
        `un texte réel de 11 px devrait compter ${TEMOINS.texte.attendu}, il compte ${mesure.nbTexteFin}`,
        JSON.stringify(mesure.texteFin));
    },
  },
  {
    nom: 'filtre : un aria-hidden visible et trop petit reste compté',
    async verifier() {
      const { corps } = extraireMesure(path.join(RACINE, 'outils', 'auditer-affichages.mjs'));
      const mesure = executerMesure(corps, [
        TEMOINS.visibleMasque.element,
      ]);
      verifier(mesure.nbTexteFin === TEMOINS.visibleMasque.attendu,
        `un texte visible de 11 px ne doit pas être écarté parce qu’il est aria-hidden : ` +
        `attendu ${TEMOINS.visibleMasque.attendu}, obtenu ${mesure.nbTexteFin}`,
        JSON.stringify(mesure.texteFin));
    },
  },
);

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
  console.log(
    `\nOK — ${cas.length} cas : une mesure interrompue ne laisse pas de rapport à demi rempli, ` +
    'et le filtre « texte sous 12 px » écarte le décor sans texte lisible sans taire un vrai texte fin.'
  );
}
