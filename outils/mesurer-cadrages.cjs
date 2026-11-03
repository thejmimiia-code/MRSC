#!/usr/bin/env node
'use strict';
// Mesure, dans un vrai navigateur, le dessin de chaque page **dans chaque
// cadrage personnalisé** : six présentations × cinq crans de texte × quatre
// largeurs. Quatre choses sont relevées, et une seule suffit au contrôle :
//
//   - le débordement horizontal du document, en pixels (tolérance 0,5 px) ;
//   - le nombre de colonnes de chaque grille déclarée ;
//   - le **texte coupé** : un mot dont la boîte sort de la zone de découpe d'un
//     ancêtre en `overflow: hidden` ou `clip` ;
//   - les **cartes qui se chevauchent** dans une grille déclarée ;
//   - le **contraste** de chaque texte, quand le fond est une couleur unie.
//
// Le contraste est calculé, pas jugé : le script écrit le rapport WCAG de chaque
// texte dont le rapport descend sous 4,5:1, et `cadrages.py` décide seul du seuil
// applicable — 3:1 pour un grand texte, 4,5:1 sinon. Cette séparation permet
// d'éprouver la règle sans navigateur. Le texte **décoratif** (`aria-hidden`,
// `role="presentation"`) est compté à part, jamais jugé : un glyphe ornemental
// n'a pas à tenir un rapport de lecture.
//
// Le texte coupé se compte sur les nœuds de texte, pas sur `scrollHeight` : un
// conteneur dont un enfant **décoratif** déborde est légitime et n'efface aucun
// mot. Le 2 novembre 2026, la mesure grossière accusait 51 fois pour zéro mot
// réellement coupé — c'est la version précise qui a été gardée.
//
// Ce script ne juge rien : il compte et il écrit. La comparaison au plan est le
// travail de `outils/cadrages.py --controler`, qui n'a pas besoin de navigateur
// et se laisse donc éprouver hors ligne.
//
// Codes de sortie :
//   0  tout a été mesuré
//   1  au moins un cadrage n'a pas pu être mesuré (page, sélecteur, affichage)
//   2  pas de navigateur, pas de modules, ou plan illisible — jamais vert
//
// Usage :
//   MRSC_BROWSER_NODE_MODULES=… node outils/mesurer-cadrages.cjs plan.json rapport.json

const fs = require('node:fs');
const path = require('node:path');

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

const source = process.argv[2];
const destination = process.argv[3];
if (!source || !destination) {
  sortir(2, 'Usage : node outils/mesurer-cadrages.cjs <plan.json> <rapport.json>');
}

let plan;
try {
  plan = JSON.parse(fs.readFileSync(source, 'utf8'));
} catch (erreur) {
  sortir(2, `Plan illisible (${source}) : ${erreur.message}`);
}
if (!Array.isArray(plan.combinaisons) || plan.combinaisons.length === 0) {
  sortir(2, `Plan vide (${source}) : aucun cadrage à confronter.`);
}

const base = process.env.MRSC_TEST_URL || 'http://127.0.0.1:4183/';

//: Ce que chaque point de mesure doit porter. Le 3 novembre 2026, une
//: réécriture du script a effacé le bloc des mots coupés : la mesure a échoué
//: (`coupes is not defined`) et le contrôle a refusé le rapport vide. C'était la
//: bonne fin, mais pour une mauvaise raison — une erreur de code, pas un
//: constat. Cette liste fait échouer la mesure **au premier point** si un
//: relevé perd une famille, et le dit : un script qui oublie de mesurer doit
//: crier, pas imprimer moins.
const FAMILLES = ['debordement', 'grilles', 'coupes', 'masques', 'chevauchements', 'contraste'];

// Le nombre de colonnes se compte dans le document, pas dans la prédiction : si
// la feuille servie contredit le modèle sur la forme elle-même, c'est un fait à
// rapporter, pas à contourner.
function mesurer(selecteurs) {
  const racine = document.documentElement;
  const debordement = Math.round((racine.scrollWidth - racine.clientWidth) * 100) / 100;
  let coupable = null;
  if (debordement > 0) {
    for (const element of document.querySelectorAll('body *')) {
      const boite = element.getBoundingClientRect();
      if (boite.width === 0 || boite.height === 0) continue;
      const depasse = Math.round((boite.right - racine.clientWidth) * 100) / 100;
      if (depasse > 0.5 && (!coupable || depasse > coupable.depasse)) {
        coupable = {
          depasse,
          tag: element.tagName.toLowerCase(),
          classe: String(element.className || '').slice(0, 60),
        };
      }
    }
  }
  // Un sélecteur peut nommer **plusieurs** grilles dans une page :
  // `liens-utiles.html` en porte sept et `transparence.html` deux. Chaque
  // exemplaire est relevé à part. Le 3 novembre 2026, n'en mesurer qu'un seul
  // faisait accuser la feuille de 14 écarts qui n'existaient pas : le registre
  // déclare des listes de tailles possibles (`items = [1, …, 7]`) parce que les
  // exemplaires n'ont pas tous le même nombre de cartes.
  const grilles = {};
  const INSTANCES_MAX = 12;
  for (const selecteur of selecteurs) {
    const elements = Array.from(document.querySelectorAll(selecteur)).filter((candidat) => {
      const style = getComputedStyle(candidat);
      return style.display !== 'none' && candidat.getBoundingClientRect().width > 0;
    });
    if (!elements.length) continue;
    const detail = [];
    for (const element of elements.slice(0, INSTANCES_MAX)) {
      const style = getComputedStyle(element);
      const enfants = Array.from(element.children).filter(
        (enfant) => getComputedStyle(enfant).display !== 'none' && enfant.getBoundingClientRect().width > 0
      );
      const fait = { cartes: enfants.length, colonnes: 0, pistes: 0, rangees: 0, derniere: 0, manque: 0 };
      if (enfants.length > 0) {
        // Les cartes d'une même rangée partagent leur bord haut, à l'arrondi près.
        const parRangee = new Map();
        for (const enfant of enfants) {
          const rect = enfant.getBoundingClientRect();
          const cle = Math.round(rect.top);
          if (!parRangee.has(cle)) parRangee.set(cle, []);
          parRangee.get(cle).push(rect);
        }
        const hauts = Array.from(parRangee.keys()).sort((a, b) => a - b);
        const derniere = parRangee.get(hauts[hauts.length - 1]) || [];
        const occupe = derniere.reduce((total, rect) => total + rect.width, 0);
        const ecart = parseFloat(style.columnGap) || 0;
        fait.rangees = hauts.length;
        fait.derniere = derniere.length;
        fait.manque = Math.round(
          Math.max(0, element.clientWidth - occupe - ecart * Math.max(0, derniere.length - 1)) * 100
        ) / 100;
        // Deux façons de compter une colonne : les pistes **déclarées** (une
        // grille `auto-fit` en déclare qu'elle replie : « 270px … 0px ») et les
        // pistes **occupées**. Le contrôle confronte la capacité à ce que les
        // cartes présentes en font ; le vide qui reste est du ressort de
        // `--orphelins`.
        let compte = enfants.length;
        let precedent = null;
        for (let i = 0; i < enfants.length; i += 1) {
          const rect = enfants[i].getBoundingClientRect();
          if (precedent !== null && rect.left <= precedent + 1) {
            compte = i;
            break;
          }
          precedent = rect.left;
        }
        if (style.display === 'grid' || style.display === 'inline-grid') {
          const liste = (style.gridTemplateColumns || '').trim().split(/\s+(?![^(]*\))/);
          fait.pistes = liste.filter((piste) => piste).length;
          fait.colonnes = liste.filter((piste) => parseFloat(piste) > 0.5).length;
        } else if (style.display === 'flex' || style.display === 'inline-flex') {
          fait.pistes = compte;
          fait.colonnes = compte;
        }
      }
      detail.push(fait);
    }
    grilles[selecteur] = { total: elements.length, instances: detail };
  }

  // --- Texte coupé ---------------------------------------------------------
  // Un conteneur qui découpe et dont un enfant décoratif dépasse est légitime :
  // ce sont les **mots** qui doivent rester lisibles, pas les boîtes.
  const coupes = [];
  let masques = 0;
  // La technique du texte réservé aux lecteurs d'écran : une boîte de 1 × 1 px,
  // souvent avec `clip: rect(0, 0, 0, 0)`. Reconnaître la **technique** et non
  // un nom de classe évite d'exempter une carte mal dessinée qui porterait la
  // même classe par hasard. Ces textes sont comptés à part : un texte caché
  // reste un texte à relire.
  const masqueVolontairement = (element) => {
    if (!element) return false;
    if (element.clientWidth <= 1 || element.clientHeight <= 1) return true;
    return /rect\(0(px)?,? 0(px)?,? 0(px)?,? 0(px)?\)/.test(getComputedStyle(element).clip || '');
  };
  for (const element of document.querySelectorAll('body *')) {
    const style = getComputedStyle(element);
    const coupeX = style.overflowX === 'hidden' || style.overflowX === 'clip';
    const coupeY = style.overflowY === 'hidden' || style.overflowY === 'clip';
    if (!coupeX && !coupeY) continue;
    const boite = element.getBoundingClientRect();
    if (boite.width === 0 || boite.height === 0) continue;
    if (masqueVolontairement(element)) continue;
    const gauche = boite.left + element.clientLeft;
    const haut = boite.top + element.clientTop;
    const droite = gauche + element.clientWidth;
    const bas = haut + element.clientHeight;
    const mots = document.createTreeWalker(element, NodeFilter.SHOW_TEXT);
    let noeud;
    let pire = 0;
    let extrait = '';
    while ((noeud = mots.nextNode())) {
      if (!noeud.textContent || !noeud.textContent.trim()) continue;
      const portee = noeud.parentElement;
      if (!portee || getComputedStyle(portee).display === 'none') continue;
      // Un texte volontairement masqué qui dépasse de son conteneur n'est pas un
      // texte coupé : c'est un intitulé placé hors champ. Le 3 novembre 2026, les
      // 160 « mots coupés » d'`anglais-aventure.html` étaient ce cas, à 1 px près.
      if (masqueVolontairement(portee)) {
        masques += 1;
        continue;
      }
      const rect = portee.getBoundingClientRect();
      if (rect.width === 0 || rect.height === 0) continue;
      const depasse = Math.max(
        coupeX ? rect.right - droite : 0,
        coupeX ? gauche - rect.left : 0,
        coupeY ? rect.bottom - bas : 0,
        coupeY ? haut - rect.top : 0
      );
      if (depasse > 0.5 && depasse > pire) {
        pire = depasse;
        extrait = noeud.textContent.trim().slice(0, 40);
      }
    }
    if (pire > 0) {
      coupes.push({
        tag: element.tagName.toLowerCase(),
        classe: String(element.className || '').slice(0, 60),
        depasse: Math.round(pire * 100) / 100,
        texte: extrait,
      });
    }
  }
  if (coupes.length > 8) coupes.length = 8;

  // Deux cartes d'une même grille ne doivent pas se recouvrir : un recouvrement
  // cache du contenu, et un contenu caché n'est pas un contenu présent.
  const chevauchements = [];
  for (const selecteur of selecteurs) {
    const grille = Array.from(document.querySelectorAll(selecteur)).find(
      (candidat) => candidat.getBoundingClientRect().width > 0
    );
    if (!grille) continue;
    const cartes = Array.from(grille.children)
      .filter((enfant) => getComputedStyle(enfant).display !== 'none')
      .slice(0, 60);
    for (let i = 0; i < cartes.length; i += 1) {
      for (let j = i + 1; j < cartes.length; j += 1) {
        const a = cartes[i].getBoundingClientRect();
        const b = cartes[j].getBoundingClientRect();
        if (a.width === 0 || a.height === 0 || b.width === 0 || b.height === 0) continue;
        const dx = Math.min(a.right, b.right) - Math.max(a.left, b.left);
        const dy = Math.min(a.bottom, b.bottom) - Math.max(a.top, b.top);
        if (dx > 0.5 && dy > 0.5) {
          chevauchements.push({
            selecteur,
            premiere: `${cartes[i].tagName.toLowerCase()}${cartes[i].className ? `.${String(cartes[i].className).split(' ')[0]}` : ''}`,
            seconde: `${cartes[j].tagName.toLowerCase()}${cartes[j].className ? `.${String(cartes[j].className).split(' ')[0]}` : ''}`,
            largeur: Math.round(dx * 100) / 100,
            hauteur: Math.round(dy * 100) / 100,
          });
        }
      }
    }
  }
  if (chevauchements.length > 8) chevauchements.length = 8;

  // --- Contraste -----------------------------------------------------------
  // On ne mesure que ce que le navigateur sait dire : une couleur de texte sur
  // un fond de couleur unie. Un fond en image ou en dégradé n'est pas mesuré —
  // il est compté, et le rapport le dit, plutôt que de le supposer bon.
  const lireCouleur = (texte) => {
    const trouve = String(texte).match(/rgba?\(([^)]+)\)/);
    if (!trouve) return null;
    const parts = trouve[1].split(/[,\s/]+/).filter(Boolean).map(Number);
    return { r: parts[0], g: parts[1], b: parts[2], a: parts.length > 3 ? parts[3] : 1 };
  };
  const luminance = (couleur) => {
    const canal = (valeur) => {
      const v = valeur / 255;
      return v <= 0.03928 ? v / 12.92 : Math.pow((v + 0.055) / 1.055, 2.4);
    };
    return 0.2126 * canal(couleur.r) + 0.7152 * canal(couleur.g) + 0.0722 * canal(couleur.b);
  };
  const poser = (dessus, dessous) => ({
    r: dessus.r * dessus.a + dessous.r * (1 - dessus.a),
    g: dessus.g * dessus.a + dessous.g * (1 - dessus.a),
    b: dessus.b * dessus.a + dessous.b * (1 - dessus.a),
    a: 1,
  });
  const rapport = (a, b) => {
    const la = luminance(a);
    const lb = luminance(b);
    return (Math.max(la, lb) + 0.05) / (Math.min(la, lb) + 0.05);
  };
  const decor = '[aria-hidden="true"],[hidden],[role="presentation"],[role="none"]';
  const sansRendu = 'script,style,noscript,template,title';
  const contraste = {
    mesures: 0,
    decoratifs: 0,
    fond_image: 0,
    sans_texte: 0,
    minimum: null,
    candidats: [],
    decoratifs_selecteurs: [],
    fond_image_selecteurs: [],
  };
  const nommer = (liste, nom) => {
    if (liste.length < 12 && !liste.includes(nom)) liste.push(nom);
  };
  for (const element of document.querySelectorAll('body *')) {
    if (element.matches(sansRendu) || element.closest(sansRendu)) continue;
    if (!Array.from(element.childNodes).some((n) => n.nodeType === 3 && n.textContent.trim())) continue;
    const style = getComputedStyle(element);
    if (style.display === 'none' || style.visibility === 'hidden' || Number(style.opacity) === 0) continue;
    const boite = element.getBoundingClientRect();
    if (boite.width < 1 || boite.height < 1) continue;
    if (element.closest(decor)) {
      contraste.decoratifs += 1;
      const classe = String(element.className || '').split(' ')[0];
      nommer(contraste.decoratifs_selecteurs, `${element.tagName.toLowerCase()}${classe ? `.${classe}` : ''}`);
      continue;
    }
    const taille = parseFloat(style.fontSize);
    const avant = lireCouleur(style.color);
    if (!(taille >= 1) || !avant || avant.a === 0) {
      // `font-size: 0` ou couleur transparente : rien n'est rendu, donc rien
      // n'est à lire. Ce n'est pas une mesure manquée, c'est un texte absent.
      contraste.sans_texte += 1;
      continue;
    }
    let courant = element;
    let fond = { r: 255, g: 255, b: 255, a: 1 };
    const piles = [];
    let image = null;
    while (courant) {
      const st = getComputedStyle(courant);
      if (!image && st.backgroundImage && st.backgroundImage !== 'none') {
        const nom = String(courant.className || '').split(' ')[0];
        image = `${courant.tagName.toLowerCase()}${nom ? `.${nom}` : ''}`;
      }
      const couleur = lireCouleur(st.backgroundColor);
      if (couleur && couleur.a > 0) piles.push(couleur);
      courant = courant.parentElement;
    }
    if (image) {
      contraste.fond_image += 1;
      nommer(contraste.fond_image_selecteurs, image);
      continue;
    }
    for (let i = piles.length - 1; i >= 0; i -= 1) fond = poser(piles[i], fond);
    const premier = avant.a < 1 ? poser(avant, fond) : avant;
    const gras = Number(style.fontWeight) >= 700;
    const ratio = Math.round(rapport(premier, fond) * 1000) / 1000;
    contraste.mesures += 1;
    if (!contraste.minimum || ratio < contraste.minimum.ratio) {
      contraste.minimum = { ratio, taille, gras };
    }
    // Le seuil est décidé par `cadrages.py` : ici on ne garde que ce qui peut
    // poser question, c'est-à-dire tout ce qui descend sous le seuil le plus
    // exigeant (4,5:1). Un texte large à 3,2:1 est donc transmis, et c'est
    // `cadrages.py` qui dira qu'il passe.
    if (ratio < 4.5 && contraste.candidats.length < 12) {
      contraste.candidats.push({
        tag: element.tagName.toLowerCase(),
        classe: String(element.className || '').slice(0, 60),
        ratio,
        taille,
        gras,
        texte: (element.textContent || '').trim().slice(0, 40),
      });
    }
  }

  return { debordement, coupable, grilles, coupes, masques, chevauchements, contraste };
}

(async () => {
  let browser;
  try {
    browser = await puppeteer.launch({
      executablePath: await chromium.executablePath(),
      args: chromium.args,
      headless: true,
    });
  } catch (erreur) {
    sortir(2, `Environnement : lancement du navigateur impossible (${erreur.message}) — aucune mesure.`);
  }

  const rapport = { navigateur: null, base, source, mesures: [], erreurs: [] };
  try {
    rapport.navigateur = await browser.version();
    // Un état de page = (page, présentation, cran). On change de largeur sans
    // recharger : la mise en page se recalcule. Les combinaisons d'un même état
    // ne coûtent donc qu'un chargement, et le nombre de chargements vaut le
    // nombre d'états — jamais celui des combinaisons.
    const parEtat = new Map();
    for (const combinaison of plan.combinaisons) {
      const cle = `${combinaison.page}|${combinaison.layout || ''}|${combinaison.cran}`;
      if (!parEtat.has(cle)) parEtat.set(cle, { ...combinaison, largeurs: [] });
      if (!parEtat.get(cle).largeurs.includes(combinaison.largeur)) {
        parEtat.get(cle).largeurs.push(combinaison.largeur);
      }
    }

    for (const etat of parEtat.values()) {
      const page = await browser.newPage();
      try {
        await page.goto(new URL(etat.page, base).href, { waitUntil: 'networkidle0' });
      } catch (erreur) {
        rapport.erreurs.push({ page: etat.page, raison: `page injoignable : ${erreur.message}` });
        await page.close();
        continue;
      }
      await page.addStyleTag({ content: '* { animation: none !important; transition: none !important; }' });
      await page.evaluate(
        (layout, echelle) => {
          const racine = document.documentElement;
          [
            'texte-tres-reduit',
            'texte-reduit',
            'texte-agrandi',
            'texte-tres-agrandi',
          ].forEach((classe) => racine.classList.remove(classe));
          const classe = {
            0.75: 'texte-tres-reduit',
            0.85: 'texte-reduit',
            1.15: 'texte-agrandi',
            1.3: 'texte-tres-agrandi',
          }[String(echelle)];
          if (classe) racine.classList.add(classe);
          if (layout) racine.dataset.layout = layout;
          else delete racine.dataset.layout;
        },
        etat.layout,
        etat.echelle
      );

      const selecteurs = (plan.grilles || {})[etat.page] || [];
      for (const largeur of etat.largeurs.sort((a, b) => a - b)) {
        // Un ascenseur vertical retire de la largeur utile : la fenêtre est
        // élargie de ce que le document perd, jusqu'à ce que la largeur cliente
        // vaille exactement la largeur demandée. Sans cela, chaque mesure serait
        // décalée de la largeur de l'ascenseur et le contrôle accuserait la
        // feuille d'un décalage de navigateur.
        let fenetre = largeur;
        for (let essai = 0; essai < 3; essai += 1) {
          await page.setViewport({ width: fenetre, height: 900, deviceScaleFactor: 1 });
          const cliente = await page.evaluate(() => document.documentElement.clientWidth);
          if (cliente === largeur) break;
          fenetre += largeur - cliente;
        }
        let resultat;
        try {
          resultat = await page.evaluate(mesurer, selecteurs);
        } catch (erreur) {
          rapport.erreurs.push({
            page: etat.page,
            layout: etat.layout,
            cran: etat.cran,
            largeur,
            raison: `évaluation impossible : ${erreur.message}`,
          });
          continue;
        }
        const manquantes = FAMILLES.filter((famille) => !(famille in resultat));
        if (manquantes.length) {
          sortir(
            2,
            `Relevé incomplet à ${etat.page} · ${largeur} px : ${manquantes.join(', ')} ` +
              'manque(nt) au point de mesure — aucune mesure écrite, aucun verdict.'
          );
        }
        rapport.mesures.push({
          page: etat.page,
          layout: etat.layout,
          cran: etat.cran,
          echelle: etat.echelle,
          largeur,
          ...resultat,
        });
      }
      await page.close();
    }
  } catch (erreur) {
    await browser.close().catch(() => {});
    sortir(2, `Environnement : la mesure s'est interrompue (${erreur.message}) — rapport partiel non écrit.`);
  }
  await browser.close().catch(() => {});

  fs.mkdirSync(path.dirname(path.resolve(destination)), { recursive: true });
  fs.writeFileSync(destination, `${JSON.stringify(rapport, null, 1)}\n`);

  const debordants = rapport.mesures.filter((mesure) => (mesure.debordement || 0) > 0).length;
  const coupes = rapport.mesures.reduce((total, mesure) => total + (mesure.coupes || []).length, 0);
  const chevauchements = rapport.mesures.reduce(
    (total, mesure) => total + (mesure.chevauchements || []).length,
    0
  );
  const textes = rapport.mesures.reduce((total, mesure) => total + ((mesure.contraste || {}).mesures || 0), 0);
  const surImage = rapport.mesures.reduce((total, mesure) => total + ((mesure.contraste || {}).fond_image || 0), 0);
  const decoratifs = rapport.mesures.reduce((total, mesure) => total + ((mesure.contraste || {}).decoratifs || 0), 0);
  const masques = rapport.mesures.reduce((total, mesure) => total + (mesure.masques || 0), 0);
  console.log(
    `Cadrages mesurés : ${rapport.mesures.length} point(s) sur ${plan.combinaisons.length} attendu(s), ` +
      `${debordants} en débordement, ${coupes} texte(s) coupé(s), ${chevauchements} chevauchement(s), ` +
      `${rapport.erreurs.length} erreur(s) — rapport écrit dans ${destination}.`
  );
  console.log(
    `Contraste : ${textes} texte(s) mesuré(s) sur fond uni, ${surImage} sur fond d'image (non mesurable ` +
      `par cette méthode), ${decoratifs} décoratif(s) écarté(s). Textes volontairement masqués : ${masques}.`
  );
  if (rapport.erreurs.length) {
    for (const erreur of rapport.erreurs.slice(0, 20)) {
      console.error(
        `  ! ${erreur.page}${erreur.layout ? ` · ${erreur.layout}` : ''}` +
          (erreur.largeur ? ` à ${erreur.largeur} px` : '') +
          ` : ${erreur.raison}`
      );
    }
    process.exit(1);
  }
  process.exit(0);
})();
