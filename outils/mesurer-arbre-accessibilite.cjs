#!/usr/bin/env node
'use strict';
// Mesure, dans un vrai Chromium, ce que la page **expose** aux technologies
// d'assistance : rôles, noms accessibles, niveaux de titres, repères, zones
// vivantes, cadres. La source est l'arbre d'accessibilité du navigateur
// (`Accessibility.getFullAXTree`, protocole CDP), pas le HTML.
//
// Pourquoi l'arbre et non le HTML : une page peut porter `alt` sans que l'image
// soit exposée, un `aria-label` sans que le nom arrive, un `ul` sans sémantique
// de liste. Le HTML décrit une intention ; l'arbre dit ce qu'un lecteur
// d'écran reçoit. Le dépôt mesurait déjà les contrastes, le focus et la taille
// des cibles ; il ne mesurait pas cette couche-là.
//
// Ce que le script ne dit pas : si la page se comprend, si un lecteur d'écran
// la lit bien, ni l'ordre de lecture réel. Il relève ce que Chromium expose ;
// un autre moteur peut exposer autre chose — WebKit, en particulier, retire la
// sémantique de liste d'un `ul { list-style: none }`, ce que ce relevé ne peut
// pas voir puisqu'il ne mesure que Chromium. C'est écrit ici pour que la règle
// correspondante ne soit jamais lue comme une mesure.
//
// Codes de sortie :
//   0  tout a été mesuré
//   1  une page n'a pas pu être mesurée (le rapport dit laquelle et pourquoi)
//   2  pas de navigateur, plan illisible — jamais vert
//
// Usage :
//   MRSC_BROWSER_NODE_MODULES=… node outils/mesurer-arbre-accessibilite.cjs plan.json rapport.json

const fs = require('node:fs');

function sortir(code, message) {
  if (message) console.error(message);
  process.exit(code);
}

if (process.env.MRSC_BROWSER_NODE_MODULES) {
  process.env.NODE_PATH = process.env.MRSC_BROWSER_NODE_MODULES;
  require('node:module').Module._initPaths();
}

let puppeteer;
let chromium;
try {
  puppeteer = require('puppeteer-core');
  const pkg = require('@sparticuz/chromium');
  chromium = pkg.default || pkg;
} catch (erreur) {
  sortir(2, `Environnement : navigateur indisponible (${erreur.message}) — aucune mesure, aucun verdict.`);
}

const [cheminPlan, cheminRapport] = process.argv.slice(2);
if (!cheminPlan || !cheminRapport) {
  sortir(2, 'Usage : node outils/mesurer-arbre-accessibilite.cjs plan.json rapport.json');
}

let plan;
try {
  plan = JSON.parse(fs.readFileSync(cheminPlan, 'utf8'));
} catch (erreur) {
  sortir(2, `Plan illisible (${cheminPlan}) : ${erreur.message}`);
}
if (!Array.isArray(plan.pages) || plan.pages.length === 0) {
  sortir(2, `Plan sans page : rien à mesurer dans ${cheminPlan}.`);
}

const base = process.env.MRSC_TEST_URL || 'http://127.0.0.1:4186/';
const largeur = Number(plan.largeur || 1280);

//: Les rôles qui attendent un nom accessible. Une cible sans nom n'est pas
//: « mal nommée » : elle est annoncée comme « bouton », sans plus.
const ROLES_INTERACTIFS = new Set([
  'button',
  'link',
  'checkbox',
  'radio',
  'textbox',
  'searchbox',
  'combobox',
  'listbox',
  'option',
  'tab',
  'menuitem',
  'menuitemcheckbox',
  'menuitemradio',
  'switch',
  'slider',
  'spinbutton',
  'treeitem',
  'disclosure triangle',
]);

//: Les repères de page. Un repère du même rôle deux fois sans nom distinct est
//: une ambiguïté de navigation (« navigation » et « navigation »).
const ROLES_REPERES = new Set([
  'banner',
  'main',
  'contentinfo',
  'navigation',
  'complementary',
  'search',
  'form',
  'region',
]);

// --- Ce qui tourne dans la page ------------------------------------------------

//: Ce que l'arbre seul ne dit pas : la langue du document, l'écriture des
//: listes, et combien d'images existent réellement dans le document — sans quoi
//: « aucune image exposée » se confondrait avec « aucune image ».
function releverDansLaPage() {
  const valeur = (element) => `${element.tagName.toLowerCase()}${element.className && typeof element.className === 'string'
    ? `.${element.className.trim().split(/\s+/).filter(Boolean).slice(0, 2).join('.')}`
    : ''}`;
  const listes = Array.from(document.querySelectorAll('ul, ol')).map((liste) => ({
    element: valeur(liste),
    role: liste.getAttribute('role'),
    style: getComputedStyle(liste).listStyleType,
    // Un `ul` en `flex` ou `grid` perd aussi sa sémantique dans WebKit, même
    // avec des puces : la forme de la boîte compte autant que la puce.
    affichage: getComputedStyle(liste).display,
    entrees: liste.querySelectorAll(':scope > li').length,
  }));
  const zonesVivantes = Array.from(
    document.querySelectorAll('[aria-live], [role="status"], [role="alert"], [role="log"]')
  ).map((zone) => ({
    element: valeur(zone),
    politesse: zone.getAttribute('aria-live') || zone.getAttribute('role') || 'aucune',
    role: zone.getAttribute('role'),
    vide: !(zone.textContent || '').trim(),
    masquee: zone.getAttribute('aria-hidden') === 'true',
  }));
  const images = Array.from(document.querySelectorAll('img')).map((image) => ({
    element: valeur(image),
    alt: image.getAttribute('alt'),
    decoratif: image.getAttribute('alt') === '',
  }));
  return {
    langue: document.documentElement.getAttribute('lang'),
    langues_declarees: Array.from(document.querySelectorAll('[lang]'))
      .filter((element) => element !== document.documentElement)
      .map((element) => ({ element: valeur(element), langue: element.getAttribute('lang') })),
    listes,
    zones_vivantes: zonesVivantes,
    images,
  };
}

// --- La mesure ------------------------------------------------------------------

(async () => {
  let browser;
  try {
    browser = await puppeteer.launch({
      executablePath: await chromium.executablePath(),
      args: chromium.args,
      headless: true,
    });
  } catch (erreur) {
    const message = String(erreur.message || '');
    const aide = /shared libraries/.test(message)
      ? ' — les bibliothèques système de Chromium manquent : extraire `al2023.tar.br` du paquet et exporter LD_LIBRARY_PATH vers son dossier `lib`'
      : '';
    sortir(2, `Environnement : lancement du navigateur impossible${aide} (${message.split('\n')[0]}) — aucune mesure.`);
  }

  const rapport = { navigateur: null, base, largeur, pages: [], erreurs: [] };
  try {
    rapport.navigateur = await browser.version();
    for (const nomPage of plan.pages) {
      const page = await browser.newPage();
      try {
        await page.goto(new URL(nomPage, base).href, { waitUntil: 'networkidle0', timeout: 45000 });
      } catch (erreur) {
        // `simulateur.html` ne se stabilise pas sur `networkidle0` : une iframe
        // et des appels asynchrones le tiennent ouvert. La page est alors lue
        // telle qu'elle est, et le relevé dit qu'il a fallu attendre.
        if (!/timeout/i.test(erreur.message || '')) {
          rapport.erreurs.push({ page: nomPage, raison: `page injoignable : ${erreur.message.split('\n')[0]}` });
          await page.close();
          continue;
        }
      }
      try {
        await page.setViewport({ width: largeur, height: 900, deviceScaleFactor: 1 });
        // Les composants construits par JavaScript (menu, panneau, cartes)
        // arrivent après le chargement : les figer évite de mesurer un arbre
        // à moitié construit.
        await page.addStyleTag({ content: '* { animation: none !important; transition: none !important; }' });
        await page.evaluate(() => new Promise((suite) => setTimeout(suite, 300)));

        const cliente = await page.target().createCDPSession();
        await cliente.send('Accessibility.enable');
        const { nodes } = await cliente.send('Accessibility.getFullAXTree');
        // `getFullAXTree` rend les nœuds dans l'ordre de son arbre interne, pas
        // dans l'ordre du document : le 13 novembre 2026, la première version a
        // accusé deux « niveaux sautés » qui n'existaient pas, les titres de
        // niveau 2 arrivant avant le titre de niveau 1. L'ordre est donc relu
        // dans le DOM, par identifiant de nœud — une sonde qui ne sait pas
        // dans quel ordre elle lit ne peut pas juger une séquence.
        const { root } = await cliente.send('DOM.getDocument', { depth: -1, pierce: true });
        const ordre = new Map();
        let rang = 0;
        const parcourir = (noeud) => {
          if (!noeud) return;
          if (noeud.backendNodeId) ordre.set(noeud.backendNodeId, rang);
          rang += 1;
          for (const enfant of noeud.children || []) parcourir(enfant);
          if (noeud.contentDocument) parcourir(noeud.contentDocument);
        };
        parcourir(root);
        await cliente.detach();

        const faits = await page.evaluate(releverDansLaPage);

        const propriete = (noeud, nom) => {
          const trouvee = (noeud.properties || []).find((entree) => entree.name === nom);
          return trouvee ? trouvee.value.value : null;
        };
        const vivants = nodes.filter((noeud) => !noeud.ignored);
        const texte = (noeud) => String((noeud.name && noeud.name.value) || '').trim();

        const titres = vivants
          .filter((noeud) => noeud.role && noeud.role.value === 'heading')
          .map((noeud) => ({
            niveau: Number(propriete(noeud, 'level')) || null,
            texte: texte(noeud).slice(0, 90),
            ordre: ordre.has(noeud.backendDOMNodeId) ? ordre.get(noeud.backendDOMNodeId) : Number.MAX_SAFE_INTEGER,
          }))
          .sort((un, autre) => un.ordre - autre.ordre)
          .map(({ niveau, texte: contenu }) => ({ niveau, texte: contenu }));
        const reperes = vivants
          .filter((noeud) => noeud.role && ROLES_REPERES.has(noeud.role.value))
          .map((noeud) => ({ role: noeud.role.value, nom: texte(noeud) }));
        const interactifs = vivants.filter((noeud) => noeud.role && ROLES_INTERACTIFS.has(noeud.role.value));
        // Un refus doit nommer l'élément, pas seulement son rôle : « link sans
        // nom » sur une page de 448 cibles ne se corrige pas. `DOM.describeNode`
        // rend la balise, la classe et l'identifiant du nœud fautif.
        const decrire = async (noeud) => {
          const base = { role: String(noeud.role && noeud.role.value) };
          if (!noeud.backendDOMNodeId) return { ...base, element: null };
          try {
            const { node } = await cliente.send('DOM.describeNode', { backendNodeId: noeud.backendDOMNodeId });
            const attributs = {};
            const brut = node.attributes || [];
            for (let rang = 0; rang < brut.length; rang += 2) attributs[brut[rang]] = brut[rang + 1];
            const classe = String(attributs.class || '').trim().split(/\s+/).filter(Boolean).slice(0, 2).join('.');
            return { ...base, element: `${node.nodeName.toLowerCase()}${classe ? `.${classe}` : ''}${attributs.id ? `#${attributs.id}` : ''}` };
          } catch (erreur) {
            return { ...base, element: null };
          }
        };
        const noms_vides = [];
        for (const noeud of interactifs.filter((candidat) => !texte(candidat)).slice(0, 40)) {
          noms_vides.push(await decrire(noeud));
        }
        const images_exposees = vivants
          .filter((noeud) => noeud.role && noeud.role.value === 'image')
          .map((noeud) => texte(noeud).slice(0, 90));
        const cadres = vivants
          .filter((noeud) => noeud.role && /iframe|frame/i.test(noeud.role.value))
          .map((noeud) => texte(noeud).slice(0, 90));
        const listes_exposees = vivants.filter((noeud) => noeud.role && noeud.role.value === 'list').length;
        const entrees_exposees = vivants.filter((noeud) => noeud.role && noeud.role.value === 'listitem').length;

        rapport.pages.push({
          page: nomPage,
          largeur,
          langue: faits.langue,
          titres,
          reperes,
          noms_vides,
          interactifs: interactifs.length,
          images: {
            document: faits.images.length,
            decoratives: faits.images.filter((image) => image.decoratif).length,
            sans_alt: faits.images.filter((image) => image.alt === null).length,
            exposees: images_exposees,
          },
          listes: {
            document: faits.listes.length,
            sans_puce: faits.listes.filter((liste) => liste.style === 'none').length,
            avec_role: faits.listes.filter((liste) => liste.role === 'list').length,
            sans_role: faits.listes.filter((liste) => liste.style === 'none' && liste.role !== 'list').length,
            elements_sans_role: faits.listes
              .filter((liste) => liste.style === 'none' && liste.role !== 'list')
              .map((liste) => `${liste.element} (${liste.entrees} entrées)`)
              .slice(0, 8),
            exposees: listes_exposees,
            entrees_exposees,
          },
          zones_vivantes: faits.zones_vivantes,
          langues_declarees: faits.langues_declarees,
          cadres,
        });
      } catch (erreur) {
        rapport.erreurs.push({ page: nomPage, raison: `évaluation impossible : ${erreur.message.split('\n')[0]}` });
      }
      await page.close();
    }
  } finally {
    await browser.close();
  }

  fs.writeFileSync(cheminRapport, JSON.stringify(rapport, null, 1));
  console.log(
    `Arbre d'accessibilité : ${rapport.pages.length} page(s) mesurée(s) à ${largeur} px, ` +
      `${rapport.erreurs.length} erreur(s). Rapport : ${cheminRapport}`
  );
  if (rapport.erreurs.length > 0) {
    for (const erreur of rapport.erreurs) {
      console.error(`  - ${erreur.page} : ${erreur.raison}`);
    }
    process.exit(1);
  }
})();
