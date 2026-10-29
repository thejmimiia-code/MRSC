// Faux `puppeteer-core`, écrit pour éprouver ce que fait `auditer-criteres-22.mjs`
// de ses mesures — pas pour mesurer.
//
// Aucun navigateur n'est lancé : `launch()` rend un objet qui imite trois choses
// seulement (`newPage`, `close` et la page elle-même). Les valeurs rendues par
// `page.evaluate` sont choisies par la variable d'environnement
// `FAUX_NAVIGATEUR_MODE`, et `goto` échoue selon le mode et le nom de page.
//
// Pourquoi ce faux : le défaut historique de l'auditeur n'est pas dans la
// géométrie, il est dans ce qu'il fait d'un chargement qui échoue. Le
// 24 octobre 2026, sans serveur local, il avait rendu « 0 cible, 0 élément
// testé » — c'est-à-dire une page parfaite. Un faux navigateur suffit à
// reproduire ça, et coûte zéro seconde au lieu de vingt minutes.
//
// Les modes (le nom dit ce qui doit arriver, pas qui l'utilise) :
//   nominal       — tout charge, aucune cible à corriger, aucun défaut ;
//   echec-total   — aucun chargement n'aboutit ;
//   echec-partiel — une page sur deux échoue ;
//   defauts       — une cible trop petite non espacée, du texte rogné, un
//                   débordement horizontal, un focus entièrement masqué et une
//                   passe de focus coupée par le plafond ;
//   fiches-erreurs        — la mesure de géométrie d'une fiche rend une erreur ;
//   fiches-statut-absent  — la fiche n'affiche pas son statut « Prototype à relire » ;
//   a11y-violations       — le balayage axe-core rend deux règles en échec ;
//   affichage-defauts    — chaque mesure d'affichage rend un débordement et une
//                          cible trop petite.
//
// Le faux sait aussi **rejouer une interception de requêtes**, ce dont
// `test-cache-css-ia.cjs` a besoin : il ne connaît pas le réseau, il rejoue les
// deux requêtes de la page qu'il simule — le document, puis la feuille qu'il
// référence — et rend au script ce que celui-ci répond. La distance entre les
// pastilles et leurs points est alors tirée du CSS **réellement servi** : si le
// CSS porte encore les positions de f3c4ddf, les pastilles sont loin de leurs
// points ; sinon elles sont dessus. C'est la seule règle de géométrie que le
// faux encode, et elle est écrite ici pour que personne ne la prenne pour une
// mesure.
//
// Les modes qui ne concernent pas un script ne le perturbent pas : c'est le
// **type d'argument** quand il suffit (chaîne courte = sélecteur, chaîne de plus
// de mille caractères = source injectée, nombre = description ou points d'une
// cible), et le **texte de la fonction** quand deux scripts partagent la même
// signature (géométrie d'une fiche, `axe.run`).

'use strict';

const MODE = process.env.FAUX_NAVIGATEUR_MODE || 'nominal';

class FauxOnglet {
  constructor(page) {
    this.page = page;
    this.largeur = 0;
    this.appelsFocus = 0;
    this.gestes = [];
    this.ferme = false;
    this.interception = false;
    this.ecouteurs = {};
    this.reponses = [];
  }

  async setViewport({ width, height, deviceScaleFactor, isMobile, hasTouch } = {}) {
    this.largeur = width;
    this.reglage = { width, height, deviceScaleFactor, isMobile, hasTouch };
  }

  async addStyleTag() {}

  async setRequestInterception(actif) {
    this.interception = Boolean(actif);
  }

  async on(evenement, ecouteur) {
    (this.ecouteurs[evenement] ||= []).push(ecouteur);
  }

  // Rejoue le chargement d'une page quand un écouteur `request` est branché :
  // le document, puis la feuille de style qu'il référence. Chaque requête passe
  // par l'écouteur du script, qui répond ou poursuit ; le faux retient ce qui a
  // été servi, jamais ce qu'il aurait fallu servir.
  rejouerRequetes(url) {
    const ecouteurs = this.ecouteurs.request || [];
    if (!ecouteurs.length) return;
    const jouer = (adresse) => {
      const requete = {
        url: () => String(adresse),
        respond: (reponse) => this.reponses.push({ url: String(adresse), ...reponse }),
        continue: () => this.reponses.push({ url: String(adresse), poursuivi: true }),
      };
      for (const ecouteur of ecouteurs) ecouteur(requete);
    };
    jouer(url);
    const document_ = this.reponses.find((r) => String(r.contentType || '').includes('html'));
    if (!document_) return;
    const reference = /(assets\/css\/[^"'\s>]+)/.exec(String(document_.body));
    if (reference) jouer(new URL(reference[1], url).href);
  }

  // La feuille que le script a réellement servie, ou `null` s'il n'a rien
  // intercepté — ce `null` est ce qui fait échouer un script qui aurait perdu
  // son interception au lieu de le laisser passer.
  get cssServi() {
    const feuille = this.reponses.find((r) => String(r.contentType || '').includes('css'));
    return feuille ? String(feuille.body) : null;
  }

  async goto(url) {
    const nom = String(url).split('/').pop();
    const index = Number(process.env.FAUX_NAVIGATEUR_INDEX || 0);
    if (MODE === 'echec-total') throw new Error(`net::ERR_CONNECTION_REFUSED sur ${nom}`);
    if (MODE === 'echec-partiel' && index % 2 === 1) {
      throw new Error(`net::ERR_CONNECTION_REFUSED sur ${nom}`);
    }
    if (this.interception) this.rejouerRequetes(String(url));
  }

  async close() {
    this.ferme = true;
  }

  // Gestes d'interface : le vrai onglet clique, choisit, saisit. Le faux les
  // enregistre sans rien faire — c'est au script, pas au faux, de décider ce
  // qu'un état interactif doit produire.
  async click(selecteur) {
    this.gestes.push(`click ${selecteur}`);
  }

  async evaluateOnNewDocument() {
    this.gestes.push('evaluateOnNewDocument');
  }

  async select(selecteur, valeur) {
    this.gestes.push(`select ${selecteur}=${valeur}`);
  }

  async type(selecteur, texte) {
    this.gestes.push(`type ${selecteur}=${texte}`);
  }

  async evaluate(fonction, argument) {
    // 1. Taille des cibles : la fonction porte un nom.
    if (fonction.name === 'mesurerCibles') {
      if (MODE === 'defauts') {
        return {
          conformes: 4,
          enLigne: [{ balise: 'a', texte: 'en phrase' }],
          espacees: [],
          aCorriger: [{ balise: 'button', classe: 'fermer', texte: 'Fermer', largeur: 16, hauteur: 16 }],
        };
      }
      return { conformes: 6, enLigne: [], espacees: [], aCorriger: [] };
    }

    // 2. Espacement : la fonction porte aussi un nom.
    if (fonction.name === 'MESURER_ESPACEMENT') {
      if (MODE === 'defauts') {
        return {
          debordement: 12,
          rognes: [{ texte: 'un titre coupé', balise: 'h2', rogneur: 'div.cadre' }],
          nombreRognes: 1,
        };
      }
      return { debordement: 0, rognes: [], nombreRognes: 0 };
    }

    // 2 bis. Alignement des pastilles de la constellation
    //        (`test-cache-css-ia.cjs`) : la fonction lit `.ai-node` et les
    //        cercles de `.ai-constellation-lines`, et rend une distance par
    //        pastille. Le faux ne mesure rien : il rend la distance que le CSS
    //        servi implique, telle que décrite en tête de fichier.
    if (typeof argument === 'undefined' && /ai-constellation-lines/.test(String(fonction))) {
      const feuille = this.cssServi;
      if (feuille === null) return [Number.NaN, Number.NaN, Number.NaN, Number.NaN, Number.NaN];
      const anciennes = /\.ai-node-info\s*\{[^}]*left:\s*12\.4%/.test(feuille);
      const ecart = anciennes ? 12.4 : 0.4;
      return [ecart, ecart, ecart, ecart, ecart];
    }

    // 3. Géométrie d'une fiche (`verifier-fiches-statistiques.cjs`). Cette
    //    fonction-là ne prend **aucun** argument : c'est son texte qui la
    //    distingue, et c'est fragile — d'où cette note. Elle cherche un élément
    //    hors écran, un contenu rogné et la présence du statut « Prototype à
    //    relire » ; le faux reconnaît la seconde de ces recherches.
    const source = String(fonction);
    if (/Prototype à relire/.test(source)) {
      if (MODE === 'fiches-erreurs') return ['MAIN hors écran'];
      if (MODE === 'fiches-statut-absent') return ['statut absent'];
      return [];
    }
    // 3 bis. La préparation de page (ouvrir les `<details>`) ne rend rien.
    if (/main details/.test(source)) return undefined;

    // 3 quater. Mesure d'affichage (`auditer-affichages.mjs`) : elle prend
    //            plusieurs arguments positionnels, donc c'est encore son texte
    //            qui la désigne.
    if (/defilementHorizontal/.test(source)) {
      if (MODE === 'affichage-defauts') {
        return {
          defilementHorizontal: 12,
          dehors: [{ selecteur: 'div.cadre', gauche: -8, droite: 398 }],
          nbDehors: 2,
          texteFin: [],
          nbTexteFin: 0,
          ciblesPetites: [{ selecteur: 'button.fermer', largeur: 16, hauteur: 16 }],
          nbCiblesPetites: 1,
          imagesAgrandies: [],
          nbImagesAgrandies: 0,
          textesCoupes: [],
          nbTextesCoupes: 0,
        };
      }
      return {
        defilementHorizontal: 0,
        dehors: [], nbDehors: 0,
        texteFin: [], nbTexteFin: 0,
        ciblesPetites: [], nbCiblesPetites: 0,
        imagesAgrandies: [], nbImagesAgrandies: 0,
        textesCoupes: [], nbTextesCoupes: 0,
      };
    }

    // 3 ter. Balayage axe-core (`verifier-accessibilite.cjs`) : c'est `axe.run`
    //        qui signe la fonction, et elle rend les violations.
    if (/axe\.run/.test(source)) {
      if (MODE === 'a11y-violations') {
        return [
          {
            id: 'image-alt',
            impact: 'critical',
            help: 'Les images doivent avoir un attribut alt',
            nodes: [{ target: 'main > img', summary: 'Élément img sans attribut alt | ' }],
            nombre: 3,
          },
          {
            id: 'link-name',
            impact: 'serious',
            help: 'Les liens doivent avoir un texte discernable',
            nodes: [{ target: 'footer > a', summary: "Le lien n'a pas de texte | " }],
            nombre: 1,
          },
        ];
      }
      return [];
    }

    // Les modes qui ne concernent pas ce script restent neutres : un objet en
    // argument ne déclenche plus rien de particulier.

    // 4. Focus : trois appels anonymes, dans cet ordre par onglet — le total
    //    (une chaîne en argument), puis pour chaque cible une description (un
    //    nombre), puis ses points (le même nombre). Le rang de l'appel départage
    //    description et points ; c'est fragile, et c'est écrit ici pour que
    //    personne ne le découvre par surprise.
    // Une chaîne longue est du code injecté (la source d'axe-core) : elle ne
    // rend rien. Une chaîne courte est le sélecteur du comptage de focus.
    // Le sélecteur du comptage de focus fait une centaine de caractères ; la
    // source d'axe-core en fait des milliers. Le seuil départage les deux.
    if (typeof argument === 'string') return argument.length > 1000 ? undefined : 7;
    if (typeof argument === 'number') {
      this.appelsFocus += 1;
      if (this.appelsFocus % 2 === 1) return { balise: 'a', texte: 'un lien' };
      if (MODE === 'defauts') return ['masque:div.bandeau', 'masque:div.bandeau', 'masque:div.bandeau', 'masque:div.bandeau', 'masque:div.bandeau'];
      return ['vue', 'vue', 'vue', 'vue', 'vue'];
    }
    return undefined;
  }
}

class FauxNavigateur {
  constructor() {
    this.onglets = [];
    this.compteur = 0;
  }

  async newPage() {
    const onglet = new FauxOnglet(`page-${this.compteur}`);
    process.env.FAUX_NAVIGATEUR_INDEX = String(this.compteur);
    this.compteur += 1;
    this.onglets.push(onglet);
    return onglet;
  }

  async close() {}
}

module.exports = {
  async launch() {
    return new FauxNavigateur();
  },
};
