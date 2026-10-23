/*
  Décor 3D du héros « Les Mondes », rendu par le navigateur.

  Cette illustration était une image : elle avait une résolution finie, donc un
  plafond de netteté. Sur un téléphone à 3×, la dalle demandait 1 170 pixels de
  large pour une source qui n'en fournissait jamais plus de 1 672, et l'image
  restait lisse à l'échelle où on la regarde le plus. Une image ne peut pas
  s'améliorer : elle a la définition qu'on lui a donnée.

  Ce fichier remplace l'image par de la géométrie. Le décor est dessiné à la
  densité exacte de l'écran, sans plafond : il est net par construction, à 1×
  comme à 4×, et le restera sur du matériel qui n'existe pas encore. Le fichier
  envoyé ne dépend plus de la taille d'affichage — quelques kilo-octets de code
  au lieu de 300 Kio d'image.

  Le `<picture>` reste dans le document : si WebGL est indisponible, refusé ou
  perdu en cours de route, l'image d'origine reprend sa place. C'est un repli,
  pas une seconde version à maintenir.

  Le dessin n'a lieu qu'une fois par taille d'affichage, puis au redimensionnement
  ou au changement de densité : pas de boucle d'animation, pas de batterie
  consommée à ne rien faire.
*/
(() => {
  "use strict";

  const canvas = document.querySelector("[data-decor-atlas]");
  if (!canvas) return;
  const heros = canvas.closest(".adventure-hero") || canvas.parentElement;
  const image = heros ? heros.querySelector(".adventure-hero-art:not([data-decor-atlas])") : null;

  // Reculer plutôt que de rendre un decor flou : si le navigateur ne sait pas
  // faire de 3D, l'image d'origine est déjà là et ne demande rien.
  const echouer = () => {
    canvas.hidden = true;
    if (!image) return;
    // Le repli n'est téléchargé qu'ici : tant que la 3D fonctionne, l'image
    // n'est jamais demandée. C'est le même mécanisme que la scène des missions.
    const picture = image.closest("picture");
    if (picture && picture.dataset.charge !== "oui") {
      for (const source of picture.querySelectorAll("source[data-srcset]")) {
        source.srcset = source.dataset.srcset;
        source.removeAttribute("data-srcset");
      }
      if (image.dataset.src) {
        image.src = image.dataset.src;
        image.removeAttribute("data-src");
      }
      picture.dataset.charge = "oui";
    }
    image.hidden = false;
  };

  let gl = null;
  let programme = null;
  let tampon = null;
  let attributPosition = 0;
  let attributCouleur = 0;
  let uniformeTransformation = null;
  let observateur = null;

  function canaux(couleur, lumiere = 1) {
    const valeur = couleur.replace("#", "");
    const entier = parseInt(valeur, 16);
    return [
      Math.min(1, ((entier >> 16) & 255) / 255 * lumiere),
      Math.min(1, ((entier >> 8) & 255) / 255 * lumiere),
      Math.min(1, (entier & 255) / 255 * lumiere),
    ];
  }

  /*
    Le décor : un archipel de savoirs. Une grande île porte la bibliothèque et
    ses livres-monuments, un pont de pierre la relie à l'observatoire, une serre
    occupe l'île de gauche, un phare la pointe arrière. Tout est construit avec
    des volumes simples — boîtes, cylindres, sphères — pour que les arêtes
    restent franches à n'importe quelle résolution.
  */
  function construireAtlas() {
    const sommets = [];
    const triangle = (a, b, c, couleur) => {
      const rgb = canaux(couleur);
      for (const point of [a, b, c]) sommets.push(point[0], point[1], point[2], rgb[0], rgb[1], rgb[2]);
    };
    const quad = (a, b, c, d, couleur, lumiere = 1) => {
      const rgb = canaux(couleur, lumiere);
      for (const point of [a, b, c, a, c, d]) sommets.push(point[0], point[1], point[2], rgb[0], rgb[1], rgb[2]);
    };
    const boite = (x, y, z, largeur, hauteur, profondeur, couleur) => {
      const x0 = x - largeur / 2; const x1 = x + largeur / 2;
      const y0 = y - hauteur / 2; const y1 = y + hauteur / 2;
      const z0 = z - profondeur / 2; const z1 = z + profondeur / 2;
      const c = [
        [x0, y0, z0], [x1, y0, z0], [x1, y1, z0], [x0, y1, z0],
        [x0, y0, z1], [x1, y0, z1], [x1, y1, z1], [x0, y1, z1],
      ];
      quad(c[4], c[5], c[6], c[7], couleur, 1.1);
      quad(c[1], c[0], c[3], c[2], couleur, .74);
      quad(c[0], c[4], c[7], c[3], couleur, .86);
      quad(c[5], c[1], c[2], c[6], couleur, .95);
      quad(c[3], c[7], c[6], c[2], couleur, 1.2);
      quad(c[0], c[1], c[5], c[4], couleur, .66);
    };
    const cylindre = (x, y, z, rayon, hauteur, couleur, segments = 16) => {
      const bas = y - hauteur / 2; const haut = y + hauteur / 2;
      for (let index = 0; index < segments; index += 1) {
        const a0 = Math.PI * 2 * index / segments;
        const a1 = Math.PI * 2 * (index + 1) / segments;
        const p0 = [x + Math.cos(a0) * rayon, bas, z + Math.sin(a0) * rayon];
        const p1 = [x + Math.cos(a1) * rayon, bas, z + Math.sin(a1) * rayon];
        const p2 = [p1[0], haut, p1[2]];
        const p3 = [p0[0], haut, p0[2]];
        quad(p0, p1, p2, p3, couleur, .86 + .16 * Math.sin(a0 + .8));
        triangle([x, haut, z], p3, p2, couleur);
      }
    };
    const cone = (x, y, z, rayon, hauteur, couleur, segments = 16) => {
      const bas = y - hauteur / 2; const pointe = [x, y + hauteur / 2, z];
      for (let index = 0; index < segments; index += 1) {
        const a0 = Math.PI * 2 * index / segments;
        const a1 = Math.PI * 2 * (index + 1) / segments;
        const p0 = [x + Math.cos(a0) * rayon, bas, z + Math.sin(a0) * rayon];
        const p1 = [x + Math.cos(a1) * rayon, bas, z + Math.sin(a1) * rayon];
        const lumiere = .84 + .16 * Math.sin(a0 + .6);
        const rgb = canaux(couleur, lumiere);
        for (const point of [p0, p1, pointe]) sommets.push(point[0], point[1], point[2], rgb[0], rgb[1], rgb[2]);
      }
    };
    const sphere = (x, y, z, rayon, couleur, anneaux = 8, segments = 12) => {
      const point = (anneau, colonne) => {
        const phi = Math.PI * anneau / anneaux;
        const theta = Math.PI * 2 * colonne / segments;
        return [
          x + rayon * Math.sin(phi) * Math.cos(theta),
          y + rayon * Math.cos(phi),
          z + rayon * Math.sin(phi) * Math.sin(theta),
        ];
      };
      for (let anneau = 0; anneau < anneaux; anneau += 1) {
        for (let colonne = 0; colonne < segments; colonne += 1) {
          const a = point(anneau, colonne); const b = point(anneau + 1, colonne);
          const c = point(anneau + 1, colonne + 1); const d = point(anneau, colonne + 1);
          const lumiere = .78 + .3 * (1 - anneau / anneaux);
          const rgb = canaux(couleur, lumiere);
          for (const sommet of [a, b, c, a, c, d]) sommets.push(sommet[0], sommet[1], sommet[2], rgb[0], rgb[1], rgb[2]);
        }
      }
    };
    const poutre = (depart, arrivee, epaisseur, couleur) => {
      const dx = arrivee[0] - depart[0]; const dy = arrivee[1] - depart[1]; const dz = arrivee[2] - depart[2];
      const longueur = Math.hypot(dx, dy, dz) || 1;
      const direction = [dx / longueur, dy / longueur, dz / longueur];
      const reference = Math.abs(direction[1]) < .92 ? [0, 1, 0] : [0, 0, 1];
      const produit = (a, b) => [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]];
      const norme = (v) => { const taille = Math.hypot(...v) || 1; return v.map((valeur) => valeur / taille); };
      const u = norme(produit(direction, reference)); const v = norme(produit(direction, u));
      const coin = (p, su, sv) => [p[0] + u[0] * su + v[0] * sv, p[1] + u[1] * su + v[1] * sv, p[2] + u[2] * su + v[2] * sv];
      const r = epaisseur / 2;
      const a = coin(depart, -r, -r); const b = coin(depart, r, -r); const c = coin(depart, r, r); const d = coin(depart, -r, r);
      const e = coin(arrivee, -r, -r); const f = coin(arrivee, r, -r); const g = coin(arrivee, r, r); const h = coin(arrivee, -r, r);
      quad(a, b, f, e, couleur, .88); quad(b, c, g, f, couleur, 1.06); quad(c, d, h, g, couleur, .96); quad(d, a, e, h, couleur, .78);
      quad(a, d, c, b, couleur, 1.12); quad(e, f, g, h, couleur, .82);
    };
    const toit = (x, y, z, largeur, hauteur, profondeur, couleur) => {
      const avantGauche = [x - largeur / 2, y, z + profondeur / 2];
      const avantDroit = [x + largeur / 2, y, z + profondeur / 2];
      const arriereGauche = [x - largeur / 2, y, z - profondeur / 2];
      const arriereDroit = [x + largeur / 2, y, z - profondeur / 2];
      const faitageAvant = [x, y + hauteur, z + profondeur / 2];
      const faitageArriere = [x, y + hauteur, z - profondeur / 2];
      quad(avantGauche, faitageAvant, faitageArriere, arriereGauche, couleur, .88);
      quad(faitageAvant, avantDroit, arriereDroit, faitageArriere, couleur, 1.1);
      triangle(avantGauche, avantDroit, faitageAvant, couleur);
      triangle(arriereDroit, arriereGauche, faitageArriere, couleur);
    };
    const arbre = (x, z, feuilles, echelle = 1) => {
      cylindre(x, .5 * echelle, z, .18 * echelle, 1.1 * echelle, "#7c5940", 9);
      sphere(x, 1.5 * echelle, z, .8 * echelle, feuilles, 7, 10);
      sphere(x - .46 * echelle, 1.24 * echelle, z + .1, .46 * echelle, feuilles, 6, 9);
      sphere(x + .4 * echelle, 1.3 * echelle, z - .1, .52 * echelle, feuilles, 6, 9);
    };
    const livre = (x, y, z, largeur, profondeur, couverture, epaisseur = .42) => {
      boite(x, y, z, largeur, epaisseur, profondeur, couverture);
      boite(x, y + epaisseur / 2 + .07, z, largeur - .16, .16, profondeur - .16, "#f7ecd0");
      boite(x, y + epaisseur / 2 + .14, z - profondeur / 2 + .1, largeur - .16, .2, .12, "#e2d3ae");
    };

    // Mer : une étendue qui va jusqu'à l'horizon, coupée par le plan lointain.
    // Les lames sont de simples dalles très plates, décalées : à cette échelle
    // elles suffisent à donner le mouvement sans coûter de géométrie.
    boite(0, -1.55, 0, 400, .4, 400, "#2f7f9e");
    boite(0, -1.32, 0, 400, .04, 400, "#3f95b4");
    for (let index = 0; index < 40; index += 1) {
      const angle = index * 2.399;
      const distance = 8 + (index % 9) * 3.2;
      const x = Math.cos(angle) * distance;
      const z = Math.sin(angle) * distance;
      boite(x, -1.28, z, 3.2 - (index % 4) * .5, .05, .34, index % 2 ? "#63b0c8" : "#4ea1bd");
    }

    const finMer = sommets.length;

    // Franges claires autour des îles : sans elles, la mer est un aplat et les
    // îles semblent posées dessus plutôt que sorties de l'eau.
    for (const [x, z, rayon] of [[0, 0, 9.4], [13.6, -1.8, 6.0], [-13.6, 2.6, 5.6], [1.4, -11.6, 5.0]]) {
      cylindre(x, -1.24, z, rayon, .06, "#5fb0c9", 20);
      cylindre(x, -1.22, z, rayon * .78, .05, "#78c1d4", 18);
    }

    // Socle rocheux commun : un cylindre large surmonté d'une plage, puis la
    // terre. Les falaises descendent sous l'eau pour que les îles ne flottent
    // pas comme des galettes.
    const ile = (x, z, rayon, largeur, profondeur, teinteTerre = "#9dba78") => {
      cylindre(x, -.85, z, rayon, 2.4, "#5e7680", 14);
      cylindre(x, -.18, z, rayon + .25, .36, "#d6c193", 14);
      boite(x, .08, z, largeur, .4, profondeur, teinteTerre);
      boite(x, .05, z, largeur - .5, .36, profondeur - .5, "#b2cc8c");
    };

    // Île principale.
    ile(0, 0, 7.6, 13.4, 8.6);

    // Chemin de dalles du pont jusqu'à la bibliothèque.
    for (let index = 0; index < 8; index += 1) {
      boite(-3.4 + index * 1.15, .26, 2.4 - index * .14, .84, .14, .66, "#eee2c6");
    }

    // La bibliothèque : large, basse, à colonnes, coiffée de bleu nuit.
    boite(-2.2, 1.5, -1.5, 7.0, 2.6, 3.4, "#e8d6b4");
    boite(-2.2, 2.82, -1.5, 7.3, .22, 3.7, "#d5c19c");
    toit(-2.2, 2.92, -1.5, 7.8, 1.15, 4.1, "#2f4f66");
    boite(-2.2, .32, .55, 7.4, .3, 1.2, "#cdbb97");
    for (const x of [-5.0, -3.6, -2.2, -.8, .6]) cylindre(x, 1.4, .4, .18, 2.2, "#f4e7ca", 10);
    boite(-2.2, 1.5, .02, 6.6, .24, .12, "#c4774f");
    boite(-3.8, 1.5, .52, .8, 1.1, .1, "#93c8cc");
    boite(-.7, 1.5, .52, .8, 1.1, .1, "#93c8cc");
    // Deux livres-monuments, à l'échelle du bâtiment.
    livre(2.9, .6, 1.9, 3.2, 2.2, "#b5483f");
    livre(2.9, 1.06, 1.9, 2.7, 1.9, "#3f6b8a", .34);
    livre(-5.9, .6, 2.9, 2.3, 1.7, "#c88a3e");
    // Pupitre et lanterne.
    cylindre(-.1, 1.0, 2.9, .07, 1.6, "#6e5a44", 8);
    boite(-.1, 1.88, 2.9, .64, .52, .52, "#ffd98a");

    // Le pont de pierre vers l'observatoire.
    const departPont = 6.6; const arriveePont = 9.6; const zPont = 1.2;
    for (let index = 0; index < 8; index += 1) {
      const fraction = index / 7;
      const x = departPont + (arriveePont - departPont) * fraction;
      const hauteur = .5 + Math.sin(Math.PI * fraction) * .22;
      boite(x, hauteur, zPont, .44, .18, 1.6, "#d2bf9b");
      boite(x, hauteur + .3, zPont - .7, .46, .32, .12, "#bda98a");
      boite(x, hauteur + .3, zPont + .7, .46, .32, .12, "#bda98a");
    }
    poutre([departPont, .86, zPont - .7], [arriveePont, .86, zPont - .7], .1, "#ae9b7b");
    poutre([departPont, .86, zPont + .7], [arriveePont, .86, zPont + .7], .1, "#ae9b7b");
    for (const fraction of [.2, .5, .8]) {
      const x = departPont + (arriveePont - departPont) * fraction;
      cylindre(x, -.1, zPont, .3, 1.5, "#5d747d", 10);
    }

    // Île de l'observatoire.
    ile(13.6, -1.8, 4.6, 8.2, 6.4);
    cylindre(13.0, 1.4, -2.4, 1.45, 2.9, "#efe2c5", 18);
    sphere(13.0, 2.85, -2.4, 1.47, "#dacdac", 8, 16);
    cone(13.0, 3.9, -2.4, 1.12, .72, "#5d7f8e", 16);
    boite(13.0, 1.5, -.75, .58, 1.1, .12, "#6f523c");
    cylindre(13.9, .55, -.4, .5, 1.1, "#4a6172", 12);
    poutre([13.6, 1.4, -.5], [13.95, 1.95, -.45], .44, "#e8dcc0");
    poutre([13.9, 1.85, -.47], [14.15, 2.05, -.44], .52, "#cbb98f");
    poutre([13.6, .85, -.6], [13.6, .1, -.6], .16, "#4a6172");

    // Île de la serre.
    ile(-13.6, 2.6, 4.3, 7.6, 5.9);
    boite(-13.6, 1.25, 2.6, 4.8, 2.0, 3.4, "#b6dcd8");
    boite(-13.6, .55, 2.6, 5.0, .3, 3.6, "#eef6f3");
    for (const x of [-15.4, -14.5, -13.6, -12.7, -11.8]) boite(x, 1.28, 4.3, .1, 1.9, .1, "#f4fbf8");
    for (const [x, z] of [[-15.1, 2.0], [-13.9, 1.7], [-12.6, 2.1], [-14.6, 3.2], [-12.9, 3.3]]) sphere(x, .8, z, .42, "#6ea863", 6, 9);
    toit(-13.6, 2.25, 2.6, 5.1, .9, 3.7, "#93bfbc");
    for (const x of [-15.7, -13.6, -11.5]) poutre([x, .3, 4.1], [x, 2.2, 4.1], .08, "#dcece8");
    arbre(-16.0, 4.8, "#4f8a5f", .8);
    arbre(-11.4, 4.6, "#4f8a5f", .7);

    // Île arrière : le phare, repère du voyage.
    ile(1.4, -11.6, 3.8, 6.6, 5.4);
    cylindre(1.4, 2.0, -11.6, .95, 3.8, "#f3e7cb", 18);
    cylindre(1.4, 2.2, -11.6, .97, .55, "#c65d4b", 18);
    cylindre(1.4, 3.6, -11.6, .97, .42, "#c65d4b", 18);
    boite(1.4, 4.0, -11.6, 1.75, .3, 1.75, "#b85a49");
    cone(1.4, 4.5, -11.6, .98, .85, "#ad5646", 16);
    sphere(1.4, 3.75, -11.6, .42, "#ffdf9a", 7, 10);

    // Végétation de l'île principale.
    arbre(-6.6, -3.3, "#4f8a5f", 1.15);
    arbre(5.4, -3.1, "#568f62", 1.0);
    arbre(6.6, 3.5, "#4f8a5f", .85);
    arbre(-6.8, 3.7, "#5d9366", .9);
    arbre(-.2, -4.1, "#4a8259", .95);
    arbre(3.8, -3.6, "#5d9366", .75);
    arbre(-4.6, 4.0, "#568f62", .8);

    // Rochers affleurants et une bouée : la mer a besoin de repères pour ne pas
    // se lire comme un fond uni.
    for (const [x, z, r] of [[-3.6, 6.2, .55], [4.8, 5.4, .45], [-11.4, -2.4, .6], [8.4, -4.2, .5], [-4.2, -7.4, .65]]) {
      sphere(x, -1.0, z, r, "#7d8b8c", 6, 9);
      sphere(x + .2, -.86, z - .1, r * .7, "#93a09f", 6, 9);
    }
    cylindre(12.4, -1.05, 5.2, .22, .5, "#d9584b", 10);
    cylindre(12.4, -.72, 5.2, .16, .22, "#f2e7cd", 10);

    // Petits îlots d'avant-plan : ils remplissent la mer et donnent la
    // profondeur du cadre, sans masquer la bibliothèque.
    ile(-7.0, 9.6, 2.2, 3.6, 2.8);
    arbre(-7.4, 9.4, "#4f8a5f", .9);
    arbre(-6.4, 10.2, "#568f62", .7);
    arbre(9.0, 5.4, "#4a8259", .55);

    // Détail de l'île principale : buissons, lampes et billots le long du chemin.
    for (const [x, z, echelle] of [[-1.8, 3.7, .55], [1.2, 3.9, .5], [4.4, 2.6, .6], [-4.8, -3.9, .6], [2.2, -3.3, .55]]) {
      sphere(x, .55, z, echelle, "#5d9a63", 6, 9);
      sphere(x + .3, .45, z - .1, echelle * .7, "#6aa76d", 6, 9);
    }
    for (const x of [-2.2, 1.0, 4.0]) {
      cylindre(x, .75, 3.1, .06, 1.1, "#6e5a44", 8);
      boite(x, 1.35, 3.1, .26, .3, .26, "#ffdf9a");
    }

    // Le cadrage s'arrête ici : le soleil et les nuages sont hauts et lointains,
    // et les inclure reculerait la caméra jusqu'à rendre les îles petites.
    const finCadrage = sommets.length;

    // Ciel : soleil bas et nuages, au-dessus de la ligne d'horizon.
    sphere(13.0, 13.5, -30.0, 1.5, "#ffe3a6", 8, 12);
    sphere(13.0, 13.5, -30.0, 2.2, "#fff1d2", 6, 12);
    sphere(-12.0, 8.2, -14.0, 1.9, "#fdf7e8", 6, 10);
    sphere(-9.8, 8.7, -14.6, 2.4, "#fdf7e8", 6, 10);
    sphere(-7.4, 8.2, -14.2, 1.7, "#f8efdc", 6, 10);
    sphere(-13.6, 8.0, -15.6, 1.3, "#f8efdc", 6, 10);

    // La mer n'entre pas dans le cadrage : elle est immense (400 unités) et
    // ferait reculer la caméra jusqu'à rendre les îles invisibles. Elle est
    // dessinée à part, avant la scène.
    return {
      sommets: sommets.slice(finMer),
      mer: sommets.slice(0, finMer),
      cadrage: sommets.slice(finMer, finCadrage),
      ciel: "#a8d8e4",
    };
  }

  /*
    Fond de ciel. Un panneau plat placé dans le monde laissait voir son arête
    comme une diagonale : dès que la caméra pique, le bord du panneau entre dans
    le cadre. Le fond est donc construit pour la caméra : un quadrilatère dressé
    perpendiculairement à l'axe de vue, à distance fixe, assez grand pour
    couvrir tout le champ, avec deux couleurs interpolées du haut vers le bas.
    Il est ainsi impossible qu'un bord apparaisse, quelle que soit la taille du
    cadre.
  */
  function sommetsCiel(oeil, cible, ratio) {
    const direction = normaliser(soustraire(cible, oeil));
    const droite = normaliser(produitVectoriel([0, 1, 0], direction));
    const haut = produitVectoriel(direction, droite);
    const distance = 90;
    const demiHauteur = distance * Math.tan(Math.PI / 2.55 / 2 / Math.max(ratio, 1)) * 2.2 + 40;
    const demiLargeur = demiHauteur * Math.max(ratio, 1) * 3;
    const centre = [oeil[0] + direction[0] * distance, oeil[1] + direction[1] * distance, oeil[2] + direction[2] * distance];
    const point = (du, dv) => [
      centre[0] + droite[0] * demiLargeur * du + haut[0] * demiHauteur * dv,
      centre[1] + droite[1] * demiLargeur * du + haut[1] * demiHauteur * dv,
      centre[2] + droite[2] * demiLargeur * du + haut[2] * demiHauteur * dv,
    ];
    const basDroite = canaux("#f7f1e2");
    const hautGauche = canaux("#bfe2ec");
    const sommets = [];
    const coinBasGauche = point(-1, -1); const coinBasDroit = point(1, -1);
    const coinHautDroit = point(1, 1); const coinHautGauche = point(-1, 1);
    for (const [p, rgb] of [
      [coinBasGauche, basDroite], [coinBasDroit, basDroite], [coinHautDroit, hautGauche],
      [coinBasGauche, basDroite], [coinHautDroit, hautGauche], [coinHautGauche, hautGauche],
    ]) {
      sommets.push(p[0], p[1], p[2], rgb[0], rgb[1], rgb[2]);
    }
    return sommets;
  }

  /*
    Cadrage exact. La caméra regarde la scène le long d'un axe fixe ; sa distance
    se déduit de tous les sommets visibles, dans son propre repère : un point de
    coordonnées (droite, haut, profondeur) tient dans le champ si la distance
    dépasse |droite| / tan(champ/2) + profondeur. On prend le maximum, plus une
    marge. Le décor occupe donc le cadre entier, que la boîte soit un bandeau de
    téléphone, un carré ou un 16:9, sans réglage manuel à refaire.
  */
  // Calculé à la demande : `normaliser` est défini plus bas dans le fichier, et
  // une constante de module l'évaluerait avant sa définition.
  let axeVue = null;
  const axeDeVue = () => {
    if (!axeVue) axeVue = normaliser([Math.cos(.82), .46, Math.sin(.82)]);
    return axeVue;
  };

  let cadrageCache = null;
  function cadreDecor(champHorizontal, champVertical, placeHorizontale = 1) {
    const clef = `${champHorizontal.toFixed(4)}x${champVertical.toFixed(4)}x${placeHorizontale.toFixed(3)}`;
    if (cadrageCache && cadrageCache.clef === clef) return cadrageCache;
    const sommets = decor.cadrage;
    const min = [Infinity, Infinity, Infinity];
    const max = [-Infinity, -Infinity, -Infinity];
    for (let index = 0; index < sommets.length; index += 6) {
      for (let axe = 0; axe < 3; axe += 1) {
        const valeur = sommets[index + axe];
        if (valeur < min[axe]) min[axe] = valeur;
        if (valeur > max[axe]) max[axe] = valeur;
      }
    }
    const centre = [(min[0] + max[0]) / 2, (min[1] + max[1]) / 2, (min[2] + max[2]) / 2];
    const z = axeDeVue();
    const x = normaliser(produitVectoriel([0, 1, 0], z));
    const y = produitVectoriel(z, x);
    const tanHorizontal = Math.tan(champHorizontal / 2) * Math.max(.2, Math.min(1, placeHorizontale));
    const tanVertical = Math.tan(champVertical / 2);
    let distance = 0;
    for (let index = 0; index < sommets.length; index += 6) {
      const q = [sommets[index] - centre[0], sommets[index + 1] - centre[1], sommets[index + 2] - centre[2]];
      const profondeur = produitScalaire(q, z);
      distance = Math.max(
        distance,
        Math.abs(produitScalaire(q, x)) / tanHorizontal + profondeur,
        Math.abs(produitScalaire(q, y)) / tanVertical + profondeur,
      );
    }
    cadrageCache = { clef, centre, distance: distance * 1.06 };
    return cadrageCache;
  }

  function compiler(type, source) {
    const shader = gl.createShader(type);
    if (!shader) return null;
    gl.shaderSource(shader, source);
    gl.compileShader(shader);
    if (!gl.getShaderParameter(shader, gl.COMPILE_STATUS)) {
      gl.deleteShader(shader);
      return null;
    }
    return shader;
  }

  function preparer() {
    if (gl && programme) return true;
    try {
      gl = canvas.getContext("webgl", { alpha: false, antialias: true, powerPreference: "low-power" })
        || canvas.getContext("experimental-webgl");
    } catch (erreur) {
      gl = null;
    }
    if (!gl) return false;
    const sommetSource = `
      attribute vec3 a_position;
      attribute vec3 a_couleur;
      uniform mat4 u_transformation;
      varying vec3 v_couleur;
      void main(void) {
        gl_Position = u_transformation * vec4(a_position, 1.0);
        v_couleur = a_couleur;
      }
    `;
    const fragmentSource = `
      precision mediump float;
      varying vec3 v_couleur;
      void main(void) { gl_FragColor = vec4(v_couleur, 1.0); }
    `;
    const sommet = compiler(gl.VERTEX_SHADER, sommetSource);
    const fragment = compiler(gl.FRAGMENT_SHADER, fragmentSource);
    if (!sommet || !fragment) return false;
    programme = gl.createProgram();
    gl.attachShader(programme, sommet);
    gl.attachShader(programme, fragment);
    gl.linkProgram(programme);
    gl.deleteShader(sommet);
    gl.deleteShader(fragment);
    if (!gl.getProgramParameter(programme, gl.LINK_STATUS)) {
      programme = null;
      gl = null;
      return false;
    }
    attributPosition = gl.getAttribLocation(programme, "a_position");
    attributCouleur = gl.getAttribLocation(programme, "a_couleur");
    uniformeTransformation = gl.getUniformLocation(programme, "u_transformation");
    tampon = gl.createBuffer();
    gl.enable(gl.DEPTH_TEST);
    gl.depthFunc(gl.LEQUAL);
    gl.disable(gl.CULL_FACE);
    canvas.addEventListener("webglcontextlost", (evenement) => {
      evenement.preventDefault();
      gl = null;
      programme = null;
      tampon = null;
      echouer();
    });
    return Boolean(tampon);
  }

  const soustraire = (a, b) => [a[0] - b[0], a[1] - b[1], a[2] - b[2]];
  const produitVectoriel = (a, b) => [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]];
  const produitScalaire = (a, b) => a[0] * b[0] + a[1] * b[1] + a[2] * b[2];
  const normaliser = (v) => { const n = Math.hypot(...v) || 1; return v.map((valeur) => valeur / n); };

  function perspective(champ, ratio, proche, lointain) {
    const f = 1 / Math.tan(champ / 2);
    const portee = 1 / (proche - lointain);
    return new Float32Array([
      f / ratio, 0, 0, 0,
      0, f, 0, 0,
      0, 0, (proche + lointain) * portee, -1,
      0, 0, proche * lointain * 2 * portee, 0,
    ]);
  }

  function regarder(oeil, cible, haut) {
    const z = normaliser(soustraire(oeil, cible));
    const x = normaliser(produitVectoriel(haut, z));
    const y = produitVectoriel(z, x);
    return new Float32Array([
      x[0], y[0], z[0], 0,
      x[1], y[1], z[1], 0,
      x[2], y[2], z[2], 0,
      -produitScalaire(x, oeil), -produitScalaire(y, oeil), -produitScalaire(z, oeil), 1,
    ]);
  }

  function multiplier(a, b) {
    const resultat = new Float32Array(16);
    for (let colonne = 0; colonne < 4; colonne += 1) {
      for (let ligne = 0; ligne < 4; ligne += 1) {
        let valeur = 0;
        for (let index = 0; index < 4; index += 1) valeur += a[index * 4 + ligne] * b[colonne * 4 + index];
        resultat[colonne * 4 + ligne] = valeur;
      }
    }
    return resultat;
  }

  const decor = construireAtlas();

  function dessiner() {
    if (!gl || !programme || !tampon) return;
    // Un élément `hidden` mesure 0 × 0 : on le révèle pour connaître sa place,
    // et tout se fait dans le même passage — révéler, mesurer, dessiner, retirer
    // l'image. Le navigateur ne peint qu'après, donc aucun saut n'est visible.
    const etaitCache = canvas.hidden;
    if (etaitCache) canvas.hidden = false;
    const cadre = canvas.getBoundingClientRect();
    if (!cadre.width || !cadre.height) {
      if (etaitCache) canvas.hidden = true;
      return;
    }
    // Densité réelle de l'écran, sans plafond arbitraire : un décor vectoriel
    // n'a aucune raison d'être rendu plus petit que la dalle. Seul le budget de
    // pixels limite, et il ne descend jamais sous 1 — un tampon plus petit que
    // la zone d'affichage serait toujours flou.
    const DENSITE_MAX = 4;
    const BUDGET_PIXELS = 6_000_000;
    const densite = Math.min(window.devicePixelRatio || 1, DENSITE_MAX);
    const densiteMax = Math.sqrt(BUDGET_PIXELS / (cadre.width * cadre.height));
    const ratio = Math.max(1, Math.min(densite, densiteMax));
    const largeur = Math.max(1, Math.round(cadre.width * ratio));
    const hauteur = Math.max(1, Math.round(cadre.height * ratio));
    if (canvas.width !== largeur || canvas.height !== hauteur) {
      canvas.width = largeur;
      canvas.height = hauteur;
    }
    gl.viewport(0, 0, largeur, hauteur);
    const ciel = canaux(decor.ciel);
    gl.clearColor(ciel[0], ciel[1], ciel[2], 1);
    gl.clear(gl.COLOR_BUFFER_BIT | gl.DEPTH_BUFFER_BIT);
    gl.useProgram(programme);
    gl.bindBuffer(gl.ARRAY_BUFFER, tampon);
    gl.enableVertexAttribArray(attributPosition);
    gl.enableVertexAttribArray(attributCouleur);
    gl.vertexAttribPointer(attributPosition, 3, gl.FLOAT, false, 24, 0);
    gl.vertexAttribPointer(attributCouleur, 3, gl.FLOAT, false, 24, 12);
    // Champ horizontal constant : la composition ne dépend pas de la hauteur de
    // la boîte. Avec un champ vertical fixe, un cadre 4:3 ou un bandeau de
    // téléphone recadraient les îles latérales, alors que le décor est le même.
    const rapport = largeur / hauteur;
    const champHorizontal = Math.PI / 2.55;
    const champVertical = 2 * Math.atan(Math.tan(champHorizontal / 2) / rapport);

    // Plein cadre : le texte occupe la moitié gauche par-dessus le décor. La
    // scène est donc décalée à droite, sinon elle vit derrière le titre. En
    // bandeau et en panneau, le texte passe dessous : le décor reste centré.
    const contenu = heros?.querySelector(".adventure-hero-content");
    const cadreContenu = contenu?.getBoundingClientRect();
    const superposition = Boolean(cadreContenu
      && cadreContenu.top < cadre.bottom - 24
      && cadreContenu.bottom > cadre.top + 24);
    const position = superposition ? .72 : .5;
    const cadrage = cadreDecor(champHorizontal, champVertical, Math.min(position, 1 - position) * 2);
    const cible = cadrage.centre;
    const axe = axeDeVue();
    const oeil = [
      cible[0] + axe[0] * cadrage.distance,
      cible[1] + axe[1] * cadrage.distance,
      cible[2] + axe[2] * cadrage.distance,
    ];
    const vue = regarder(oeil, cible, [0, 1, 0]);
    const projection = perspective(champVertical, rapport, .1, 200);
    // Décalage horizontal appliqué dans l'espace de clip : la scène entière, fond
    // compris, se décale sans que la géométrie bouge.
    if (superposition) projection[12] = position * 2 - 1;
    gl.uniformMatrix4fv(uniformeTransformation, false, multiplier(projection, vue));
    // Le fond d'abord, sans test ni écriture de profondeur : il ne peut alors ni
    // clignoter contre la géométrie, ni laisser voir la diagonale de ses deux
    // triangles. Le décor est dessiné ensuite par-dessus.
    gl.disable(gl.DEPTH_TEST);
    gl.depthMask(false);
    gl.bufferData(gl.ARRAY_BUFFER, new Float32Array(sommetsCiel(oeil, cible, largeur / hauteur)), gl.STATIC_DRAW);
    gl.drawArrays(gl.TRIANGLES, 0, 6);
    // La mer vient ensuite, sans écrire de profondeur : elle est immense et
    // passerait devant les îles si elle participait au test.
    gl.bufferData(gl.ARRAY_BUFFER, new Float32Array(decor.mer), gl.STATIC_DRAW);
    gl.drawArrays(gl.TRIANGLES, 0, decor.mer.length / 6);
    gl.depthMask(true);
    gl.enable(gl.DEPTH_TEST);
    gl.bufferData(gl.ARRAY_BUFFER, new Float32Array(decor.sommets), gl.STATIC_DRAW);
    gl.drawArrays(gl.TRIANGLES, 0, decor.sommets.length / 6);
    canvas.dataset.rendu = "oui";
    canvas.hidden = false;
    if (image) image.hidden = true;
  }

  function demarrer() {
    if (!preparer()) {
      echouer();
      return;
    }
    try {
      dessiner();
    } catch (erreur) {
      echouer();
      return;
    }
    if ("ResizeObserver" in window) {
      observateur = new ResizeObserver(() => dessiner());
      observateur.observe(canvas);
    } else {
      window.addEventListener("resize", dessiner, { passive: true });
    }
    window.addEventListener("pagehide", () => observateur?.disconnect(), { once: true });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", demarrer, { once: true });
  } else {
    demarrer();
  }
})();
