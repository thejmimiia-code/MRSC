// Faux `@sparticuz/chromium` : l'auditeur appelle `executablePath()` et étale
// `args` dans ses options de lancement. Aucun binaire n'existe ici, et c'est le
// but — le faux `puppeteer-core` ne lance rien.
'use strict';

module.exports = {
  args: ['--faux-navigateur'],
  async executablePath() {
    return '/faux/chromium-qui-n-existe-pas';
  },
};
