#!/usr/bin/env node
/**
 * Banc de `verifier-accessibilite.cjs` : ce que le balayage axe fait d'une page.
 *
 * Le script visite 12 pages à deux largeurs, puis une vingtaine d'états
 * interactifs (menu ouvert, panneau Affichage, contraste renforcé, lecture à
 * voix haute, filtres d'Apprendre, aides dépliées, mission des Mondes,
 * commandes du simulateur) et passe axe-core sur chacun. Il n'avait aucun test.
 *
 * Trois choses peuvent le faire mentir, et c'est cela que le banc éprouve :
 *
 * 1. **ne rien analyser et se taire** — un balayage sans page rend « 0 violation »
 *    exactement comme un site parfait ;
 * 2. **perdre le lien entre une violation et l'état qui la porte** — un compte
 *    total ne dit pas où regarder ;
 * 3. **sortir en succès alors qu'une règle a échoué**.
 *
 * Le faux navigateur de `outils/faux-navigateur/` remplace `puppeteer-core`,
 * `@sparticuz/chromium` et `axe-core` ; le vrai script est lancé **sans être
 * modifié**, avec `MRSC_A11Y_BASE` pour qu'il n'essaie pas de démarrer le
 * serveur local. Quatre cas :
 *
 * - `nominal` : code 0, aucune violation, et autant de lignes « OK — » que
 *   d'exécutions annoncées (le contrat est vérifié contre lui-même, sans
 *   recopier le nombre d'états visités) ;
 * - `a11y-violations` : code 1, les deux règles nommées avec leur état et leur
 *   largeur, le message de repli affiché ;
 * - `--rapport` : le détail JSON contient autant de clés que d'exécutions ;
 * - chargement impossible : code 2, et **aucun rapport écrit**.
 *
 * Usage :
 *   node outils/test_verifier_accessibilite.mjs
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
const SCRIPT = path.join(OUTILS, 'verifier-accessibilite.cjs');

async function fauxModules() {
  const dossier = await mkdtemp(path.join(os.tmpdir(), 'mrsc-faux-a11y-'));
  const modules = path.join(dossier, 'node_modules');
  for (const paquet of ['puppeteer-core', 'axe-core', path.join('@sparticuz', 'chromium')]) {
    await cp(path.join(FAUX, paquet), path.join(modules, paquet), { recursive: true });
  }
  return { dossier, modules };
}

async function balayer(mode, options = []) {
  const { dossier, modules } = await fauxModules();
  const rapport = path.join(dossier, 'rapport.json');
  const execution = await new Promise((resoudre) => {
    const enfant = spawn(process.execPath, [SCRIPT, ...options, '--rapport', rapport], {
      cwd: RACINE,
      env: {
        ...process.env,
        MRSC_BROWSER_NODE_MODULES: modules,
        MRSC_AXE_NODE_MODULES: modules,
        // Évite de lancer `outils/serveur-local.py` : le faux ne charge rien.
        MRSC_A11Y_BASE: 'http://faux.local',
        FAUX_NAVIGATEUR_MODE: mode,
      },
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
  if (contexte) console.error(contexte.split('\n').slice(0, 40).map((ligne) => `    | ${ligne}`).join('\n'));
}

/** Nombre d'exécutions annoncées par le script lui-même, et lignes « OK — ». */
function decompte(sortie) {
  const annonce = sortie.match(/\n(\d+) exécutions?, (\d+) avec violation\./);
  return {
    executions: annonce ? Number(annonce[1]) : null,
    violations: annonce ? Number(annonce[2]) : null,
    ok: (sortie.match(/^OK — /gm) || []).length,
  };
}

const cas = [
  {
    nom: 'nominal : chaque exécution annoncée a son verdict',
    mode: 'nominal',
    async verifier({ statut, sortie, rapport }) {
      verifier(statut === 0, 'le code de sortie devrait être 0', sortie);
      const { executions, violations, ok } = decompte(sortie);
      verifier(executions !== null, 'le bilan final devrait annoncer un nombre d\'exécutions', sortie);
      verifier(violations === 0, 'aucune violation ne devrait être comptée', sortie);
      // Le script visite 12 pages + une vingtaine d'états : le banc ne recopie
      // pas ce total, il vérifie que chaque exécution annoncée a bien un verdict.
      verifier(executions >= 40, 'le balayage devrait couvrir au moins les 12 pages aux deux largeurs', String(executions));
      verifier(ok === executions, 'chaque exécution annoncée devrait avoir sa ligne « OK — »', `OK: ${ok}, annoncées: ${executions}`);
      verifier(rapport && Object.keys(rapport).length === executions, 'le rapport devrait avoir une entrée par exécution', Object.keys(rapport || {}).length);
      // Les états interactifs sont nommés : un total agrégé ne dirait pas où regarder.
      for (const etat of ['Accueil, menu ouvert @360', 'Accueil, contraste renforcé @1280',
        'Apprendre, filtre actif @360', 'Fiche, aides dépliées @1280',
        'Mondes, mission ouverte @360', 'Simulateur, commandes visibles @1280']) {
        verifier(rapport && etat in rapport, `l'état « ${etat} » devrait être relevé séparément`, JSON.stringify(Object.keys(rapport || {})).slice(0, 300));
      }
    },
  },
  {
    nom: 'violations : code 1, règle nommée, état et largeur conservés',
    mode: 'a11y-violations',
    async verifier({ statut, sortie, rapport }) {
      verifier(statut === 1, 'une violation devrait sortir en code 1', sortie);
      const { executions, violations } = decompte(sortie);
      // Le faux rend deux règles pour chaque analyse : le compte doit suivre,
      // sinon le script perd des états en route.
      verifier(violations === executions, 'chaque exécution devrait compter comme en violation', `violations: ${violations}, exécutions: ${executions}`);
      verifier(/image-alt — Les images doivent avoir un attribut alt/.test(sortie), 'la règle en échec devrait être nommée', sortie);
      verifier(/link-name — Les liens doivent avoir un texte discernable/.test(sortie), 'la seconde règle devrait être nommée', sortie);
      verifier(/main > img/.test(sortie), 'le nœud fautif devrait être désigné', sortie);
      verifier(/Réessayer après correction, puis consigner la mesure sans la présenter comme un audit/.test(sortie),
        'le message de repli devrait rappeler qu\'une mesure n\'est pas un audit', sortie);
      verifier(rapport && rapport['Accueil @360']?.length === 2, 'le rapport devrait garder les deux règles de l\'accueil', JSON.stringify(rapport?.['Accueil @360']));
      verifier(rapport && rapport['Accueil @360'][0].nombre === 3, 'le rapport devrait garder le nombre de nœuds', JSON.stringify(rapport?.['Accueil @360']?.[0]));
    },
  },
  {
    nom: 'chargement impossible : code 2, aucun rapport trompeur',
    mode: 'echec-total',
    async verifier({ statut, sortie, rapport }) {
      verifier(statut === 2, 'un chargement impossible devrait sortir en code 2', sortie);
      verifier(/ERR_CONNECTION_REFUSED/.test(sortie), 'la cause devrait être écrite', sortie);
      verifier(rapport === null, 'aucun rapport ne devrait être écrit quand rien n\'a été analysé', JSON.stringify(rapport)?.slice(0, 200));
    },
  },
];

for (const un of cas) {
  const resultat = await balayer(un.mode);
  const avant = echecs;
  await un.verifier(resultat);
  console.log(`${echecs === avant ? 'ok' : 'ÉCHEC'} — ${un.nom}`);
}

if (echecs) {
  console.error(`\n${echecs} vérification(s) en échec.`);
  process.exitCode = 1;
} else {
  console.log('\nOK — 3 cas : un balayage vide ne se confond pas avec un site sans violation.');
}
