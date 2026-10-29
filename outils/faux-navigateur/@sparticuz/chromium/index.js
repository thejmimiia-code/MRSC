// Faux `@sparticuz/chromium` : aucun binaire n'existe ici, et c'est le but —
// le faux `puppeteer-core` ne lance rien.
//
// Trois surfaces sont imitées, parce que trois scripts les appellent :
//   `args` et `executablePath()` (les trois),
//   `inflate()` et `setupLambdaEnvironment()` (`verifier-accessibilite.cjs`,
//   qui décompresse le paquet AL2023 avant de lancer Chromium).
'use strict';

const faux = {
  args: ['--faux-navigateur'],

  async executablePath() {
    return '/faux/chromium-qui-n-existe-pas';
  },

  async inflate() {
    return '/faux/bibliotheques-decompressees';
  },

  setupLambdaEnvironment() {
    // Le vrai paquet exporte ici des variables que Chromium lit au démarrage.
    // Rien à faire : aucun processus ne sera lancé.
  },
};

// Le vrai paquet expose ses fonctions sous `default` une fois chargé en
// CommonJS : `verifier-accessibilite.cjs` lit `chromiumPackage.default` sans
// repli, contrairement aux deux autres scripts.
faux.default = faux;
module.exports = faux;
