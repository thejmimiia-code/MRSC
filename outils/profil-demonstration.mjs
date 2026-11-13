#!/usr/bin/env node
'use strict';
/**
 * Profil de démonstration pour les séances d'essai d'usage.
 *
 * Pendant une séance, il faut pouvoir repartir d'un état connu — « avant le
 * réglage », « tous les modules actifs », « écran étroit » — sans toucher aux
 * données de la personne qui essaye. Ce module fournit cet état : il
 * n'installe rien, n'écrit aucun cookie, n'appelle aucun serveur et ne lit
 * jamais le stockage existant. Il écrit les clés que `assets/js/site.js` sait
 * déjà lire, et rien d'autre.
 *
 * Il sert de deux façons :
 *
 *   1. **En ligne, pendant une séance.** `window.MRSC_PROFIL` expose
 *      `appliquer(nom)`, `etat()` et `noms()`. L'outil appelle donc les mêmes
 *      clés que le site, sans réimplémenter sa logique d'affichage.
 *   2. **En test.** Les bancs importent `ETATS`, `CLES_CONNUES` et
 *      `clesDeLEtat()` sans navigateur, pour vérifier que le profil ne
 *      contient que des clés réelles et des valeurs que le site accepte.
 *
 * Ce que ce profil ne fait pas : il ne remplace pas le consentement, il ne
 * décide pas quelles tâches montrer, et il ne garantit pas qu'un essai a eu
 * lieu. Il rend seulement l'état de départ reproductible.
 *
 * Usage en console de navigateur :
 *
 *     MRSC_PROFIL.appliquer('modules-actifs');
 *     MRSC_PROFIL.etat();
 *     MRSC_PROFIL.reinitialiser();
 *
 * Usage en ligne de commande (affiche la commande à coller) :
 *
 *     node outils/profil-demonstration.mjs modules-actifs
 *     node outils/profil-demonstration.mjs --liste
 */

/**
 * Les clés que le site lit réellement.
 *
 * Chacune est justifiée par l'endroit du script qui la lit. Une clé inventée
 * ici ne serait jamais relue par le site : l'état affiché mentirait, et le banc
 * `test_profil_demonstration` refuse donc toute clé absente de cette liste.
 */
export const CLES_CONNUES = Object.freeze({
  // assets/js/site.js — `keys.text` ; valeurs 75, 85, 100, 115, 130.
  texteCran: 'mrsc-texte-cran',
  // `keys.contrast`, `keys.spacing` : le site compare à la chaîne « oui ».
  contraste: 'mrsc-contraste-renforce',
  espacement: 'mrsc-espacement-renforce',
  // Les trois modules d'accessibilité livrés le 12 novembre 2026.
  lectureAide: 'mrsc-lecture-aide',
  mouvementAttenue: 'mrsc-mouvement-attenue',
  reperesVisibles: 'mrsc-reperes-visibles',
  // `CLE_APPARENCE` : systeme, clair, sombre, bobine, horizon, arcade.
  apparence: 'mrsc-apparence',
  // `layoutPreferenceKey` : equilibree, lecture, vitrine, mosaique, panorama,
  // compacte.
  miseEnPage: 'mrsc-mise-en-page',
  // Bascule manuelle de l'en-tête : « oui » ou « non ».
  enteteCompacte: 'mrsc-entete-compacte',
  // Lue par la lecture vocale ; une vitesse par minute, pas un cran d'affichage.
  lectureVitesse: 'mrsc-lecture-vitesse',
});

/** Valeurs acceptées par le site, pour chaque clé énumérée. */
export const VALEURS_ACCEPTEES = Object.freeze({
  [CLES_CONNUES.texteCran]: ['75', '85', '100', '115', '130'],
  [CLES_CONNUES.contraste]: ['oui', 'non'],
  [CLES_CONNUES.espacement]: ['oui', 'non'],
  [CLES_CONNUES.lectureAide]: ['oui', 'non'],
  [CLES_CONNUES.mouvementAttenue]: ['oui', 'non'],
  [CLES_CONNUES.reperesVisibles]: ['oui', 'non'],
  [CLES_CONNUES.apparence]: ['systeme', 'clair', 'sombre', 'bobine', 'horizon', 'arcade'],
  [CLES_CONNUES.miseEnPage]: ['equilibree', 'lecture', 'vitrine', 'mosaique', 'panorama', 'compacte'],
  [CLES_CONNUES.enteteCompacte]: ['oui', 'non'],
});

/**
 * États de départ. Chacun répond à une tâche du protocole d'essai.
 *
 * La correspondance est écrite dans le champ `pour`, en citant l'identifiant
 * de la tâche : un état sans tâche n'a pas sa place ici.
 */
export const ETATS = Object.freeze({
  'neutre': {
    libelle: 'État neutre — tous les réglages par défaut',
    pour: 'Point de départ de toute séance ; C1, C2, C3, B1, B2, B3',
    cles: {},
  },
  'modules-actifs': {
    libelle: 'Les trois modules d’accessibilité actifs',
    pour: 'C4 — retrouver ses réglages ailleurs, puis les retirer',
    cles: {
      [CLES_CONNUES.lectureAide]: 'oui',
      [CLES_CONNUES.mouvementAttenue]: 'oui',
      [CLES_CONNUES.reperesVisibles]: 'oui',
    },
  },
  'lecture-difficile': {
    libelle: 'Texte petit, interligne serré — avant d’activer la lecture facilitée',
    pour: 'C1 — activer un réglage de lecture et dire s’il aide',
    cles: {
      [CLES_CONNUES.texteCran]: '85',
      [CLES_CONNUES.lectureAide]: 'non',
    },
  },
  'mouvement-actif': {
    libelle: 'Animations du site à leur état normal',
    pour: 'C2 — chercher le réglage qui calme les animations',
    cles: {
      [CLES_CONNUES.mouvementAttenue]: 'non',
    },
  },
  'sombre-contraste': {
    libelle: 'Fond sombre et contraste renforcé',
    pour: 'Vérifier qu’un module ne casse pas un réglage déjà choisi',
    cles: {
      [CLES_CONNUES.apparence]: 'sombre',
      [CLES_CONNUES.contraste]: 'oui',
    },
  },
  'lecture-large': {
    libelle: 'Mise en page « Lecture » et texte agrandi',
    pour: 'B1, B2 — comparer les mises en page et revenir à l’état de départ',
    cles: {
      [CLES_CONNUES.miseEnPage]: 'lecture',
      [CLES_CONNUES.texteCran]: '115',
    },
  },
});

/** Vérifie qu'une clé et sa valeur sont lisibles par le site. */
export function verifierCle(cle, valeur) {
  const connues = Object.values(CLES_CONNUES);
  if (!connues.includes(cle)) {
    throw new Error(`clé inconnue du site : ${cle}`);
  }
  const acceptees = VALEURS_ACCEPTEES[cle];
  if (acceptees && !acceptees.includes(String(valeur))) {
    throw new Error(`valeur refusée par le site pour ${cle} : ${valeur}`);
  }
  return { cle, valeur: String(valeur) };
}

/** Rend l'état sous forme de liste de paires clé/valeur vérifiées. */
export function clesDeLEtat(nom) {
  const etat = ETATS[nom];
  if (!etat) {
    throw new Error(`état inconnu : ${nom} (connus : ${Object.keys(ETATS).join(', ')})`);
  }
  return Object.entries(etat.cles).map(([cle, valeur]) => verifierCle(cle, valeur));
}

/** Le code à coller dans la console du navigateur, pour un état donné. */
export function commandePour(nom) {
  const paires = clesDeLEtat(nom);
  return paires.map(({ cle, valeur }) => `localStorage.setItem(${JSON.stringify(cle)}, ${JSON.stringify(valeur)});`).join('\n');
}

// ── Partie navigateur ───────────────────────────────────────────────────────
// Aucune de ces fonctions ne s'exécute à l'import : le module reste importable
// par Node pour les bancs, sans DOM ni `localStorage`.

function stockage() {
  try {
    const s = globalThis.localStorage;
    if (!s) throw new Error('localStorage absent');
    return s;
  } catch (erreur) {
    throw new Error('stockage indisponible : appliquer le profil par un profil de navigateur dédié, jamais dans la session de la personne');
  }
}

export const MRSC_PROFIL = {
  noms() {
    return Object.keys(ETATS);
  },
  /** Applique un état. Ne lit ni n'écrase aucune autre clé. */
  appliquer(nom) {
    const s = stockage();
    const paires = clesDeLEtat(nom);
    for (const { cle, valeur } of paires) s.setItem(cle, valeur);
    return paires.map(({ cle, valeur }) => `${cle}=${valeur}`);
  },
  /** Relit ce que le site lirait, sans rien modifier. */
  etat() {
    const s = stockage();
    const releve = {};
    for (const cle of Object.values(CLES_CONNUES)) {
      const valeur = s.getItem(cle);
      if (valeur !== null) releve[cle] = valeur;
    }
    return releve;
  },
  /** Retire les seules clés connues du site, pas tout le stockage de l'origine. */
  reinitialiser() {
    const s = stockage();
    const retirees = [];
    for (const cle of Object.values(CLES_CONNUES)) {
      if (s.getItem(cle) !== null) {
        s.removeItem(cle);
        retirees.push(cle);
      }
    }
    return retirees;
  },
};

if (typeof window !== 'undefined') {
  window.MRSC_PROFIL = MRSC_PROFIL;
}

// ── Ligne de commande ───────────────────────────────────────────────────────
const ligneDeCommande = typeof process !== 'undefined'
  && Array.isArray(process.argv)
  && String(process.argv[1] || '').endsWith('profil-demonstration.mjs');

if (ligneDeCommande) {
  const arg = process.argv[2];
  if (!arg || arg === '--liste') {
    console.log('États disponibles :');
    for (const [nom, etat] of Object.entries(ETATS)) {
      console.log(`  ${nom.padEnd(20)} ${etat.libelle}`);
      console.log(`  ${''.padEnd(20)} pour : ${etat.pour}`);
    }
    console.log('\nUsage : node outils/profil-demonstration.mjs <etat>');
    process.exit(arg ? 0 : 0);
  }
  try {
    console.log(commandePour(arg));
  } catch (erreur) {
    console.error(erreur.message);
    process.exit(1);
  }
}
