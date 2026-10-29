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
//   a11y-violations       — le balayage axe-core rend deux règles en échec.
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
  }

  async setViewport({ width }) {
    this.largeur = width;
  }

  async addStyleTag() {}

  async goto(url) {
    const nom = String(url).split('/').pop();
    const index = Number(process.env.FAUX_NAVIGATEUR_INDEX || 0);
    if (MODE === 'echec-total') throw new Error(`net::ERR_CONNECTION_REFUSED sur ${nom}`);
    if (MODE === 'echec-partiel' && index % 2 === 1) {
      throw new Error(`net::ERR_CONNECTION_REFUSED sur ${nom}`);
    }
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
