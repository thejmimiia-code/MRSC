/**
 * Carte des coûts : un fond départemental réel, des communes réelles, et des
 * chiffres seulement là où une collecte les a mesurés.
 *
 * Règles tenues par ce script :
 *  - aucun chiffre inventé : une commune sans prix n'affiche pas de prix, et la
 *    page dit pourquoi (département non collecté, hors champ de DVF, aucune
 *    vente enregistrée, ou moins de cinq ventes) ;
 *  - aucune requête vers un service tiers : tout vient de fichiers du dépôt ;
 *  - la carte se pilote au clavier autant qu'à la souris.
 */
(function () {
  "use strict";

  var DOSSIER = "assets/data/vie-chere/";
  var SEUIL_VENTES = 5;
  var COULEUR_VIDE = "#dbe2ec";
  var ECHELLE_X = Math.cos((46.5 * Math.PI) / 180);
  // Le zoom s'arrêtait à 1,5 degré, soit environ 165 km : la carte ne pouvait
  // pas descendre jusqu'à une ville, alors que la page promet « qu'on agrandit
  // jusqu'à la ville ». Le plancher est maintenant de 0,03 degré, environ 3 km,
  // et la vue ne peut plus sortir de la France.
  var LARGEUR_MIN = 0.03;
  var LARGEUR_MAX = 140;
  var LARGEUR_COMMUNE = 0.09;
  var LARGEUR_PREMIER_CLIC = 0.35;
  // Rayons en pixels d'écran, convertis à chaque vue : un point doit rester
  // cliquable au fond de zoom comme sur la carte de France.
  var RAYON_POINT_PX = 3.5;
  var RAYON_ACTIF_PX = 8;

  var racine = document.querySelector("[data-couts-vue]");
  if (!racine) return;

  var svg = racine.querySelector("[data-couts-svg]");
  var groupe = racine.querySelector("[data-couts-departements]");
  var message = racine.querySelector("[data-couts-message]");
  var etatCollecte = document.querySelector("[data-etat-collecte]");
  var choix = document.querySelector("[data-couts-departement]");
  var recherche = document.querySelector("[data-couts-recherche]");
  var listeResultats = document.querySelector("[data-couts-resultats]");
  var etatRecherche = document.querySelector("[data-couts-recherche-etat]");
  var panneau = document.querySelector("[data-couts-panneau]");
  var fiche = panneau.querySelector("[data-couts-fiche]");
  var vide = panneau.querySelector("[data-couts-vide]");
  var mensualite = document.querySelector("[data-couts-mensualite]");
  var resultat = document.querySelector("[data-couts-surface]");
  var blocCarburants = panneau.querySelector("[data-couts-carburants]");

  var fond = null;
  var carburants = null;
  var carburantsDemande = null;
  var departementOuvert = null;
  var donneesDepartement = null;
  var communeChoisie = null;
  var vue = { x: 0, y: 0, largeur: 100 };
  var bornes = null;
  var indexNational = null;
  var indexDemande = null;
  var indexIndisponible = false;
  var resultats = [];
  var actif = -1;

  function dire(texte) {
    if (message) message.textContent = texte;
  }

  function euros(valeur) {
    return valeur.toLocaleString("fr-FR") + " €";
  }

  function nombre(valeur) {
    return valeur.toLocaleString("fr-FR");
  }

  /// Projection équirectangulaire corrigée en longitude : sans le cosinus de la
  /// latitude moyenne, la France paraît étirée d'un tiers vers l'est.
  function projeter(lon, lat) {
    return [lon * ECHELLE_X, -lat];
  }

  function chemin(anneaux) {
    var morceaux = [];
    for (var i = 0; i < anneaux.length; i++) {
      var anneau = anneaux[i];
      for (var j = 0; j < anneau.length; j++) {
        var point = projeter(anneau[j][0], anneau[j][1]);
        morceaux.push((j === 0 ? "M" : "L") + point[0].toFixed(3) + " " + point[1].toFixed(3));
      }
      morceaux.push("Z");
    }
    return morceaux.join("");
  }

  function appliquerVue() {
    var hauteur = vue.largeur * (racine.clientHeight / Math.max(racine.clientWidth, 1));
    svg.setAttribute("viewBox", vue.x + " " + vue.y + " " + vue.largeur + " " + hauteur);
    ajusterRayons();
  }

  /// Un rayon exprimé en pixels d'écran, ramené aux unités de la vue.
  function rayonPx(pixels) {
    return (pixels * vue.largeur) / Math.max(racine.clientWidth, 1);
  }

  function ajusterRayons() {
    var points = svg.querySelectorAll("[data-couts-communes] circle");
    var rayon = rayonPx(RAYON_POINT_PX);
    for (var i = 0; i < points.length; i++) {
      points[i].setAttribute("r", rayon.toFixed(4));
    }
    var anneau = svg.querySelector("[data-couts-choisie]");
    if (anneau) {
      anneau.setAttribute("r", rayonPx(RAYON_ACTIF_PX).toFixed(4));
      anneau.setAttribute("stroke-width", rayonPx(2).toFixed(4));
    }
    ajusterEtiquette();
  }

  /// La vue ne sort pas de la France : sans cette borne, deux flèches et l'on
  /// regardait l'Atlantique sans comprendre où l'on était.
  function bornerVue() {
    if (!bornes) return;
    var ratio = racine.clientHeight / Math.max(racine.clientWidth, 1);
    var demiX = vue.largeur / 2;
    var demiY = (vue.largeur * ratio) / 2;
    var marge = vue.largeur * 0.25;
    var centreX = vue.x + demiX;
    var centreY = vue.y + demiY;
    centreX = Math.min(Math.max(centreX, bornes.x1 - marge), bornes.x2 + marge);
    centreY = Math.min(Math.max(centreY, bornes.y1 - marge), bornes.y2 + marge);
    vue.x = centreX - demiX;
    vue.y = centreY - demiY;
  }

  function dessinerDepartements() {
    var morceau = document.createDocumentFragment();
    fond.departements.forEach(function (departement) {
      var trace = document.createElementNS("http://www.w3.org/2000/svg", "path");
      trace.setAttribute("d", departement.p.map(chemin).join(""));
      trace.setAttribute("class", "couts-departement");
      trace.setAttribute("data-dep", departement.c);
      trace.setAttribute("fill", COULEUR_VIDE);
      trace.setAttribute("stroke", "#ffffff");
      trace.setAttribute("stroke-width", "0.6");
      trace.setAttribute("vector-effect", "non-scaling-stroke");
      var titre = document.createElementNS("http://www.w3.org/2000/svg", "title");
      titre.textContent = departement.n + " (" + departement.c + ")";
      trace.appendChild(titre);
      trace.addEventListener("click", function () {
        ouvrirDepartement(departement.c);
      });
      morceau.appendChild(trace);
    });
    groupe.appendChild(morceau);
    fond.departements.forEach(function (departement) {
      var option = document.createElement("option");
      option.value = departement.c;
      option.textContent = departement.c + " — " + departement.n;
      choix.appendChild(option);
    });
  }

  function cadrer(x1, y1, x2, y2) {
    var a = projeter(x1, y1);
    var b = projeter(x2, y2);
    var largeur = Math.abs(b[0] - a[0]);
    var hauteur = Math.abs(b[1] - a[1]);
    var ratio = racine.clientHeight / Math.max(racine.clientWidth, 1);
    var besoin = Math.max(largeur, hauteur / Math.max(ratio, 0.0001));
    vue.largeur = Math.min(Math.max(besoin * 1.12, LARGEUR_MIN), LARGEUR_MAX);
    vue.x = (a[0] + b[0]) / 2 - vue.largeur / 2;
    vue.y = (a[1] + b[1]) / 2 - (vue.largeur * ratio) / 2;
    appliquerVue();
  }

  /// Cadre la carte sur une commune, sans jamais dépasser le plancher de zoom.
  function cadrerCommune(commune, largeur) {
    if (!commune) return;
    var point = projeter(commune.x, commune.y);
    var ratio = racine.clientHeight / Math.max(racine.clientWidth, 1);
    vue.largeur = Math.min(Math.max(largeur || LARGEUR_COMMUNE, LARGEUR_MIN), LARGEUR_MAX);
    vue.x = point[0] - vue.largeur / 2;
    vue.y = point[1] - (vue.largeur * ratio) / 2;
    bornerVue();
    appliquerVue();
  }

  function cadrerFrance() {
    if (!fond) return;
    var x1 = Infinity, y1 = Infinity, x2 = -Infinity, y2 = -Infinity;
    fond.departements.forEach(function (departement) {
      departement.p.forEach(function (polygone) {
        polygone.forEach(function (anneau) {
          anneau.forEach(function (point) {
            x1 = Math.min(x1, point[0]); x2 = Math.max(x2, point[0]);
            y1 = Math.min(y1, point[1]); y2 = Math.max(y2, point[1]);
          });
        });
      });
    });
    bornes = { x1: projeter(x1, y1)[0], y1: projeter(x1, y2)[1], x2: projeter(x2, y1)[0], y2: projeter(x1, y1)[1] };
    cadrer(x1, y1, x2, y2);
  }

  function colorer() {
    var traces = groupe.querySelectorAll(".couts-departement");
    for (var i = 0; i < traces.length; i++) {
      var actif = traces[i].getAttribute("data-dep") === departementOuvert;
      traces[i].classList.toggle("est-ouvert", actif);
      traces[i].setAttribute("fill", actif ? "#b9cdec" : COULEUR_VIDE);
    }
  }

  function dateFr(iso) {
    if (!iso || iso.length < 10) return "date inconnue";
    return iso.slice(8, 10) + "/" + iso.slice(5, 7) + "/" + iso.slice(0, 4);
  }

  var LIBELLES_CARBURANTS = {
    gazole: "Gazole", sp95: "SP95", sp98: "SP98", e10: "SP95-E10", e85: "E85", gplc: "GPLc"
  };

  function chargerCarburants() {
    if (!carburantsDemande) {
      carburantsDemande = charger(DOSSIER + "carburants.json")
        .then(function (donnees) { carburants = donnees; })
        .catch(function () { carburants = null; });
    }
    return carburantsDemande;
  }

  function afficherCarburants() {
    if (!blocCarburants) return;
    var liste = blocCarburants.querySelector("[data-couts-carburants-liste]");
    var note = blocCarburants.querySelector("[data-couts-carburants-source]");
    blocCarburants.hidden = false;
    liste.textContent = "";
    var parDepartement = carburants && carburants.departements ? carburants.departements[departementOuvert] : null;
    if (!parDepartement) {
      note.textContent =
        "Aucun prix de carburant collecté pour ce département : la page ne l’estime pas et ne le remplace par aucune moyenne nationale.";
      return;
    }
    Object.keys(LIBELLES_CARBURANTS).forEach(function (cle) {
      if (!parDepartement[cle]) return;
      var ligne = document.createElement("div");
      var terme = document.createElement("dt");
      terme.textContent = LIBELLES_CARBURANTS[cle];
      var valeur = document.createElement("dd");
      valeur.textContent =
        parDepartement[cle].mediane.toFixed(3).replace(".", ",") + " €/L (" +
        nombre(parDepartement[cle].stations) + " stations)";
      ligne.appendChild(terme);
      ligne.appendChild(valeur);
      liste.appendChild(ligne);
    });
    note.textContent =
      "Médiane des prix affichés par les stations du département (DGCCRF, Licence Ouverte 2.0), collecte du " +
      dateFr(carburants.collecte_le) + ". Le prix payé dépend de la station choisie, pas du département.";
  }

  function charger(chemin) {
    return fetch(chemin).then(function (reponse) {
      if (!reponse.ok) throw new Error(String(reponse.status));
      return reponse.json();
    });
  }

  function ouvrirDepartement(code, communeVisee) {
    if (!code || !fond) return;
    var departement = fond.departements.filter(function (d) { return d.c === code; })[0];
    if (!departement) return;
    departementOuvert = code;
    donneesDepartement = null;
    communeChoisie = null;
    choix.value = code;
    colorer();
    viderFiche();
    if (!communeVisee) adressePartageable(null, code);
    var x1 = Infinity, y1 = Infinity, x2 = -Infinity, y2 = -Infinity;
    departement.p.forEach(function (polygone) {
      polygone.forEach(function (anneau) {
        anneau.forEach(function (point) {
          x1 = Math.min(x1, point[0]); x2 = Math.max(x2, point[0]);
          y1 = Math.min(y1, point[1]); y2 = Math.max(y2, point[1]);
        });
      });
    });
    cadrer(x1, y1, x2, y2);
    dessinerCommunes([]);
    dire("Département " + departement.n + " : chargement des communes…");
    charger(DOSSIER + "d-" + code + ".json")
      .then(function (donnees) {
        donneesDepartement = donnees;
        dessinerCommunes(donnees.communes);
        var avecPrix = donnees.communes.filter(function (c) { return c.pa || c.pm; }).length;
        dire(
          departement.n + " : " + nombre(donnees.communes.length) + " commune(s), " +
          nombre(avecPrix) + " avec un prix de vente publié."
        );
        if (!avecPrix) {
          dire(
            departement.n + " : " + nombre(donnees.communes.length) + " commune(s), aucune avec un prix publié. " +
            (code === "67" || code === "68" || code === "57"
              ? "Ce département est hors du champ de DVF (livre foncier d’Alsace-Moselle)."
              : "Aucune vente exploitable dans la collecte.")
          );
        }
        if (communeVisee) {
          var visee = donnees.communes.filter(function (c) { return c.c === communeVisee; })[0];
          if (visee) {
            choisirCommune(visee, { cadrer: true, largeur: LARGEUR_COMMUNE, focus: true });
            dire(visee.n + " (" + departement.n + ") : " + (visee.pa || visee.pm
              ? "prix publié, fiche à droite."
              : "aucun prix publié pour cette commune — la fiche dit pourquoi."));
          } else {
            dire(
              "La commune " + communeVisee + " n’est pas dans la collecte du département " +
              departement.n + " : la carte n’invente pas sa fiche."
            );
          }
        }
      })
      .catch(function () {
        dire(
          departement.n + " : aucune donnée collectée pour ce département. " +
          "La page n’affiche donc aucun chiffre — il faut lancer la collecte décrite dans « D’où viennent les chiffres »."
        );
      });
  }

  function dessinerCommunes(communes) {
    var ancien = svg.querySelector("[data-couts-communes]");
    if (ancien) ancien.remove();
    if (!communes || !communes.length) return;
    var groupeCommunes = document.createElementNS("http://www.w3.org/2000/svg", "g");
    groupeCommunes.setAttribute("data-couts-communes", "");
    communes.forEach(function (commune) {
      var point = projeter(commune.x, commune.y);
      var cercle = document.createElementNS("http://www.w3.org/2000/svg", "circle");
      cercle.setAttribute("cx", point[0]);
      cercle.setAttribute("cy", point[1]);
      cercle.setAttribute("r", rayonPx(RAYON_POINT_PX).toFixed(4));
      cercle.setAttribute("class", "couts-commune" + (commune.pa || commune.pm ? " a-un-prix" : ""));
      var titre = document.createElementNS("http://www.w3.org/2000/svg", "title");
      titre.textContent = commune.n + (commune.pa || commune.pm ? " — prix publié" : " — sans prix publié");
      cercle.appendChild(titre);
      cercle.addEventListener("click", function () {
        // Le premier clic sur un point cadre déjà sur la ville : c'est ce que
        // « agrandir jusqu'à la ville » veut dire, sans avoir à chercher le
        // bouton « + » une dizaine de fois.
        choisirCommune(commune, { cadrer: true, largeur: LARGEUR_PREMIER_CLIC });
      });
      groupeCommunes.appendChild(cercle);
    });
    svg.appendChild(groupeCommunes);
    dessinerChoix();
  }

  /// L'anneau de la commune choisie. Sans lui, au fond de zoom, rien ne dit
  /// laquelle des dizaines de points est celle dont la fiche parle.
  function dessinerChoix() {
    var ancien = svg.querySelector("[data-couts-choisie]");
    if (ancien) ancien.remove();
    if (!communeChoisie) return;
    var point = projeter(communeChoisie.x, communeChoisie.y);
    var anneau = document.createElementNS("http://www.w3.org/2000/svg", "circle");
    anneau.setAttribute("data-couts-choisie", "");
    anneau.setAttribute("class", "couts-choisie");
    anneau.setAttribute("aria-hidden", "true");
    anneau.setAttribute("cx", point[0]);
    anneau.setAttribute("cy", point[1]);
    anneau.setAttribute("r", rayonPx(RAYON_ACTIF_PX).toFixed(4));
    anneau.setAttribute("stroke-width", rayonPx(2).toFixed(4));
    svg.appendChild(anneau);
    var etiquette = document.createElementNS("http://www.w3.org/2000/svg", "text");
    etiquette.setAttribute("data-couts-etiquette", "");
    etiquette.setAttribute("class", "couts-etiquette");
    etiquette.setAttribute("aria-hidden", "true");
    etiquette.setAttribute("x", point[0] + rayonPx(RAYON_ACTIF_PX) * 1.4);
    etiquette.setAttribute("y", point[1] + rayonPx(4));
    etiquette.textContent = communeChoisie.n;
    // Sans cette remise à l'échelle immédiate, le texte garde la taille par
    // défaut du SVG — 16 unités de carte, soit plusieurs milliers de pixels à
    // ce niveau de zoom — et son liseré blanc recouvre la carte entière.
    // Constaté à l'écran : la carte devenait blanche dès qu'on choisissait une
    // ville.
    rendreEtiquetteLisible(etiquette);
    svg.appendChild(etiquette);
  }

  function rendreEtiquetteLisible(etiquette) {
    var visible = vue.largeur <= 0.6;
    etiquette.style.display = visible ? "" : "none";
    if (!visible) return;
    etiquette.setAttribute("font-size", rayonPx(13).toFixed(5));
    etiquette.setAttribute("stroke-width", rayonPx(3).toFixed(5));
  }

  /// Au fond de zoom, le nom de la commune choisie est écrit à côté d'elle :
  /// des points sans nom ne disent pas où l'on est. Le nom disparaît quand la
  /// vue s'élargit, où il masquerait les autres communes.
  function ajusterEtiquette() {
    var etiquette = svg.querySelector("[data-couts-etiquette]");
    if (etiquette) rendreEtiquetteLisible(etiquette);
  }

  function viderFiche() {
    fiche.hidden = true;
    vide.hidden = false;
    resultat.textContent = "—";
  }

  function choisirCommune(commune, options) {
    var reglages = options || {};
    communeChoisie = commune;
    vide.hidden = true;
    fiche.hidden = false;
    panneau.querySelector("[data-couts-nom]").textContent = commune.n + " (" + commune.c + ")";
    panneau.querySelector("[data-couts-population]").textContent =
      commune.p ? nombre(commune.p) + " habitants" : "non communiquée";
    panneau.querySelector("[data-couts-appartements]").textContent =
      commune.pa ? euros(commune.pa) + " (" + nombre(commune.na) + " ventes)" : "aucune donnée publiée";
    panneau.querySelector("[data-couts-maisons]").textContent =
      commune.pm ? euros(commune.pm) + " (" + nombre(commune.nm) + " ventes)" : "aucune donnée publiée";
    panneau.querySelector("[data-couts-ventes]").textContent =
      nombre((commune.na || 0) + (commune.nm || 0)) + " vente(s) de logement";
    var source = panneau.querySelector("[data-couts-source]");
    if (!commune.pa && !commune.pm) {
      source.textContent =
        "Aucun prix publié pour cette commune : aucune vente exploitable dans la collecte, " +
        "ou département hors du champ de DVF. Le site ne comble pas ce trou par une estimation.";
    } else {
      source.textContent =
        "Médiane des ventes enregistrées (DVF, DGFiP), arrondie à l’euro. " +
        "Sous " + SEUIL_VENTES + " ventes, une médiane ne décrit pas une commune : elle est alors signalée par son nombre de ventes.";
    }
    calculerSurface();
    chargerCarburants().then(afficherCarburants);
    if (reglages.cadrer !== false && commune.x != null && commune.y != null) {
      cadrerCommune(commune, reglages.largeur);
    }
    dessinerChoix();
    adressePartageable(commune.c);
    viderResultats();
    if (reglages.focus) {
      // Le panneau est la réponse : un lecteur d'écran doit l'annoncer sans
      // que la personne ait à chercher où le texte a changé.
      panneau.setAttribute("tabindex", "-1");
      panneau.focus({ preventScroll: false });
    }
  }

  /// L'adresse garde la commune ou le département choisi : « ?commune=69123 »
  /// ou « ?dep=69 » se partage, se met en favori et se rouvre sur la bonne vue.
  function adressePartageable(code, departement) {
    if (!window.history || !window.history.replaceState) return;
    var url = new URL(window.location.href);
    if (code) {
      url.searchParams.set("commune", code);
      url.searchParams.delete("dep");
    } else if (departement) {
      url.searchParams.delete("commune");
      url.searchParams.set("dep", departement);
    } else {
      url.searchParams.delete("commune");
      url.searchParams.delete("dep");
    }
    window.history.replaceState(null, "", url.pathname + (url.search || "") + url.hash);
  }

  function calculerSurface() {
    if (!communeChoisie) return;
    var prix = communeChoisie.pa || communeChoisie.pm;
    var budget = Number(mensualite.value);
    if (!prix || !budget || budget <= 0) {
      resultat.textContent = prix
        ? "Saisissez une mensualité pour obtenir une surface."
        : "Pas de prix publié ici : aucune surface ne peut être calculée sans inventer un prix.";
      return;
    }
    var surface = Math.floor(budget / prix);
    var type = communeChoisie.pa ? "appartements" : "maisons";
    resultat.textContent =
      budget.toLocaleString("fr-FR") + " € par mois correspondent à environ " +
      surface + " m² au prix médian des " + type + " (" + euros(prix) + " le m²), " +
      "avant frais, charges et intérêts.";
  }

  /// « Saint-Étienne », « saint etienne » et « SAINT-ETIENNE » désignent la même
  /// commune. La première version comparait les chaînes telles quelles : une
  /// majuscule, un accent ou une apostrophe suffisaient à répondre « aucune
  /// commune », alors que la commune existait et que la carte savait la montrer.
  function normaliser(texte) {
    var plie = String(texte == null ? "" : texte);
    if (plie.normalize) {
      plie = plie.normalize("NFD").replace(/[\u0300-\u036f]/g, "");
    }
    return plie
      .toLowerCase()
      .replace(/['’‘`´\-–—_.]/g, " ")
      .replace(/\s+/g, " ")
      .trim();
  }

  function direRecherche(texte) {
    if (etatRecherche) etatRecherche.textContent = texte;
  }

  /// L'index national n'est pas chargé avec la page : il pèse plus que la page
  /// elle-même. Il arrive au premier besoin réel, une fois pour la visite, et
  /// son coût est annoncé dans l'état de la recherche avant qu'il ne parte.
  function chargerIndex() {
    if (indexNational) return Promise.resolve(indexNational);
    if (indexIndisponible) return Promise.resolve(null);
    if (!indexDemande) {
      direRecherche("Recherche dans toute la France : chargement de l’index des noms de communes…");
      indexDemande = charger(DOSSIER + "communes-index.json")
        .then(function (donnees) {
          indexNational = donnees.communes || [];
          return indexNational;
        })
        .catch(function () {
          indexIndisponible = true;
          indexDemande = null;
          direRecherche(
            "L’index de recherche n’a pas pu être chargé : la recherche reste limitée au " +
            "département ouvert, et la page le dit plutôt que de répondre « aucune commune »."
          );
          return null;
        });
    }
    return indexDemande;
  }

  function viderResultats() {
    resultats = [];
    actif = -1;
    if (listeResultats) {
      listeResultats.textContent = "";
      listeResultats.hidden = true;
    }
    if (recherche) recherche.setAttribute("aria-expanded", "false");
    if (recherche) recherche.removeAttribute("aria-activedescendant");
  }

  /// Le classement compte : en tapant « lyon », sept communes contiennent ces
  /// lettres, et la première version les rendait par ordre alphabétique —
  /// « Beauficel-en-Lyons » arrivait avant « Lyon ». Le code exact ou le nom
  /// exact d'abord, puis ce qui commence par le terme, puis le reste.
  function rangDe(candidat, plie) {
    var code = candidat.code.toLowerCase();
    if (code === plie) return 0;
    var plieNom = normaliser(candidat.nom);
    if (plieNom === plie) return 0;
    if (code.indexOf(plie) === 0 || plieNom.indexOf(plie) === 0) return 1;
    return 2;
  }

  function trier(candidats, plie) {
    return candidats
      .map(function (candidat, ordre) {
        return { candidat: candidat, rang: rangDe(candidat, plie), code: candidat.code, ordre: ordre };
      })
      .sort(function (a, b) {
        if (a.rang !== b.rang) return a.rang - b.rang;
        if (a.candidat.nom.toLowerCase() !== b.candidat.nom.toLowerCase()) {
          return a.candidat.nom.toLowerCase() < b.candidat.nom.toLowerCase() ? -1 : 1;
        }
        return a.ordre - b.ordre;
      })
      .map(function (entree) { return entree.candidat; });
  }

  function libelleDepartement(code) {
    var trouve = fond && fond.departements.filter(function (d) { return d.c === code; })[0];
    return trouve ? trouve.n : code;
  }

  function afficherResultats(liste, portee) {
    resultats = liste;
    actif = -1;
    if (!listeResultats) return;
    listeResultats.textContent = "";
    if (!liste.length) {
      listeResultats.hidden = true;
      recherche.setAttribute("aria-expanded", "false");
      return;
    }
    liste.slice(0, 12).forEach(function (candidat, position) {
      // Un `li` sous `role="option"` aurait gardé la puce d'une liste dont le
      // rôle est ailleurs : la mesure de l'arbre d'accessibilité refusait cette
      // liste sans puces, et elle avait raison de se méfier de `ul` sans
      // `role="list"` (WebKit retire alors la sémantique). Une liste de
      // suggestions n'est pas une liste de lecture : des `div` portent le rôle.
      var ligne = document.createElement("div");
      ligne.setAttribute("role", "option");
      ligne.id = "couts-resultat-" + candidat.code;
      ligne.setAttribute("aria-selected", "false");
      ligne.className = "couts-suggestion";
      ligne.setAttribute("data-position", String(position));
      var nom = document.createElement("span");
      nom.className = "couts-resultat-nom";
      nom.textContent = candidat.nom;
      var complement = document.createElement("span");
      complement.className = "couts-resultat-complement";
      complement.textContent = (candidat.departement ? libelleDepartement(candidat.departement) + " — " : "") + candidat.code;
      var prix = document.createElement("span");
      prix.className = "couts-suggestion-prix";
      prix.textContent = candidat.prix ? "prix publié" : "sans prix publié";
      ligne.appendChild(nom);
      ligne.appendChild(complement);
      ligne.appendChild(prix);
      ligne.addEventListener("mousedown", function (evenement) {
        evenement.preventDefault();
        choisirResultat(position);
      });
      listeResultats.appendChild(ligne);
    });
    listeResultats.hidden = false;
    recherche.setAttribute("aria-expanded", "true");
    var annonce = liste.length === 1
      ? "1 commune trouvée"
      : Math.min(liste.length, 12) + " communes trouvées";
    direRecherche(
      annonce + (portee === "france" ? " dans toute la France" : " dans ce département") +
      ". Flèches pour choisir, Entrée pour ouvrir."
    );
  }

  function choisirResultat(position) {
    var candidat = resultats[position];
    if (!candidat) return;
    recherche.value = candidat.nom;
    viderResultats();
    // Pas de `dire()` ici : le message de la carte et le déplacement du focus
    // sur la fiche disent déjà ce qui vient de se passer. Deux zones vivantes
    // qui annoncent la même chose font répéter le lecteur d'écran.
    if (candidat.commune) {
      choisirCommune(candidat.commune, { cadrer: true, focus: true });
      return;
    }
    if (candidat.departement === departementOuvert && donneesDepartement) {
      var locale = donneesDepartement.communes.filter(function (c) { return c.c === candidat.code; })[0];
      if (locale) {
        choisirCommune(locale, { cadrer: true, focus: true });
        return;
      }
    }
    ouvrirDepartement(candidat.departement, candidat.code);
  }

  function surlignerResultat(position) {
    if (!listeResultats) return;
    actif = position;
    var lignes = listeResultats.querySelectorAll(".couts-suggestion");
    for (var i = 0; i < lignes.length; i++) {
      var choisi = i === position;
      lignes[i].setAttribute("aria-selected", choisi ? "true" : "false");
      lignes[i].classList.toggle("est-actif", choisi);
      if (choisi) {
        recherche.setAttribute("aria-activedescendant", lignes[i].id);
        if (lignes[i].scrollIntoView) lignes[i].scrollIntoView({ block: "nearest" });
      }
    }
    if (position < 0) recherche.removeAttribute("aria-activedescendant");
  }

  function chercher(terme) {
    var plie = normaliser(terme);
    if (!plie) {
      viderResultats();
      direRecherche("");
      return;
    }
    var locaux = [];
    if (donneesDepartement && donneesDepartement.communes) {
      // Le tri précède le découpage à 40 : sinon, dans un département riche en
      // noms composés (« Ville » dans l'Oise, « Y » dans la Somme), le nom
      // exact est rejeté au-delà de la quarantième place avant même d'être classé.
      locaux = donneesDepartement.communes
        .filter(function (commune) {
          return normaliser(commune.n).indexOf(plie) !== -1 || commune.c.toLowerCase().indexOf(plie) === 0;
        })
        .map(function (commune) {
          return {
            nom: commune.n,
            code: commune.c,
            departement: departementOuvert,
            commune: commune,
            prix: Boolean(commune.pa || commune.pm)
          };
        });
    }
    if (locaux.length) {
      afficherResultats(trier(locaux, plie).slice(0, 40), "departement");
      return;
    }
    direRecherche("Aucune commune du département ouvert ne correspond. Recherche dans toute la France…");
    chargerIndex().then(function (index) {
      if (!index) return;
      if (normaliser(recherche.value) !== plie) return; // la frappe a continué
      var trouves = [];
      var parCode = /^(\d|2[ab])/.test(plie) && plie.length >= 2;
      // L'index entier est parcouru, sans arrêt au quarantième résultat : un
      // arrêt sur l'ordre alphabétique ferait manquer le nom exact (« Saint-
      // Étienne » derrière quarante « Saint-… »).
      for (var i = 0; i < index.length; i++) {
        var nom = index[i][0];
        var code = index[i][1];
        var codePlie = code.toLowerCase();
        var entree = {
          nom: nom,
          code: code,
          departement: code.slice(0, 2),
          commune: null,
          prix: index[i][2] === 1
        };
        if (codePlie === plie || (parCode && codePlie.indexOf(plie) === 0)) {
          trouves.unshift(entree);
          continue;
        }
        if (normaliser(nom).indexOf(plie) === -1) continue;
        trouves.push(entree);
      }
      trouves = trier(trouves, plie).slice(0, 40);
      if (!trouves.length) {
        viderResultats();
        direRecherche(
          "Aucune commune de France métropolitaine ne commence par « " + recherche.value +
          " ». La carte ne s’étend pas aux départements d’outre-mer."
        );
        return;
      }
      afficherResultats(trouves, "france");
    });
  }

  /// Ouvre une commune depuis son code seul : c'est le chemin du lien partagé
  /// et de la recherche par code INSEE.
  function ouvrirCommuneParCode(code) {
    var normalise = String(code || "").trim().toUpperCase();
    if (!/^(\d{2}|2[AB])\d{3}$/.test(normalise)) {
      dire("Le code « " + code + " » n’est pas un code de commune : la carte n’ouvre rien.");
      return;
    }
    var departement = normalise.slice(0, 2);
    var connu = fond && fond.departements.filter(function (d) { return d.c === departement; })[0];
    if (!connu) {
      dire(
        "La commune " + normalise + " appartient au département " + departement +
        ", absent de cette carte : elle ne couvre que la métropole."
      );
      return;
    }
    ouvrirDepartement(departement, normalise);
  }

  /// Ouvre un département depuis un lien partagé « ?dep=75 ».
  function ouvrirDepartementParCode(code) {
    var normalise = String(code || "").trim().toUpperCase();
    var connu = fond && fond.departements.filter(function (d) { return d.c === normalise; })[0];
    if (!connu) {
      dire(
        "Le département « " + code + " » est absent de cette carte : elle ne couvre que la métropole."
      );
      return;
    }
    ouvrirDepartement(normalise);
  }

  function zoomer(facteur) {
    var centreX = vue.x + vue.largeur / 2;
    var ratio = racine.clientHeight / Math.max(racine.clientWidth, 1);
    var centreY = vue.y + (vue.largeur * ratio) / 2;
    vue.largeur = Math.min(Math.max(vue.largeur * facteur, LARGEUR_MIN), LARGEUR_MAX);
    vue.x = centreX - vue.largeur / 2;
    vue.y = centreY - (vue.largeur * ratio) / 2;
    bornerVue();
    appliquerVue();
  }

  function brancher() {
    choix.addEventListener("change", function () { ouvrirDepartement(choix.value); });
    recherche.addEventListener("input", function () { chercher(recherche.value); });
    recherche.addEventListener("keydown", function (evenement) {
      if (evenement.key === "ArrowDown") {
        if (!resultats.length) return;
        evenement.preventDefault();
        surlignerResultat(Math.min(actif + 1, resultats.length - 1));
      } else if (evenement.key === "ArrowUp") {
        if (!resultats.length) return;
        evenement.preventDefault();
        surlignerResultat(Math.max(actif - 1, 0));
      } else if (evenement.key === "Enter") {
        if (!resultats.length) return;
        evenement.preventDefault();
        choisirResultat(actif >= 0 ? actif : 0);
      } else if (evenement.key === "Escape") {
        recherche.value = "";
        viderResultats();
        direRecherche("");
      } else if (evenement.key === "Tab") {
        // Fermer la liste avant le déplacement du focus : sinon, la boîte
        // défilante de suggestions capte Tab dans Chromium et aria-expanded
        // reste à true alors qu'on a quitté la recherche.
        viderResultats();
      }
    });
    var zoneRecherche = recherche.closest ? recherche.closest(".couts-recherche-zone") : null;
    if (zoneRecherche) {
      zoneRecherche.addEventListener("focusout", function (evenement) {
        if (evenement.relatedTarget && zoneRecherche.contains(evenement.relatedTarget)) return;
        viderResultats();
      });
    }
    mensualite.addEventListener("input", calculerSurface);
    Array.prototype.forEach.call(document.querySelectorAll("[data-couts-zoom]"), function (bouton) {
      bouton.addEventListener("click", function () {
        zoomer(bouton.getAttribute("data-couts-zoom") === "plus" ? 0.7 : 1.45);
      });
    });
    document.querySelector("[data-couts-recentrer]").addEventListener("click", function () {
      departementOuvert = null;
      donneesDepartement = null;
      communeChoisie = null;
      choix.value = "";
      recherche.value = "";
      viderResultats();
      direRecherche("");
      colorer();
      dessinerCommunes([]);
      viderFiche();
      adressePartageable(null);
      cadrerFrance();
      dire("Vue d’ensemble de la métropole. Choisissez un département ou cherchez une commune.");
    });
    racine.addEventListener("keydown", function (evenement) {
      var pas = vue.largeur / 12;
      if (evenement.key === "ArrowLeft") { vue.x -= pas; }
      else if (evenement.key === "ArrowRight") { vue.x += pas; }
      else if (evenement.key === "ArrowUp") { vue.y -= pas; }
      else if (evenement.key === "ArrowDown") { vue.y += pas; }
      else if (evenement.key === "+" || evenement.key === "=") { zoomer(0.7); }
      else if (evenement.key === "-") { zoomer(1.45); }
      else { return; }
      evenement.preventDefault();
      bornerVue();
      appliquerVue();
    });
    var glissement = null;
    var ignorerProchainClic = false;
    svg.addEventListener("pointerdown", function (evenement) {
      if (evenement.button !== 0 || (evenement.isPrimary === false)) return;
      glissement = {
        id: evenement.pointerId,
        x: evenement.clientX,
        y: evenement.clientY,
        vueX: vue.x,
        vueY: vue.y,
        glisse: false
      };
    });
    window.addEventListener("pointermove", function (evenement) {
      if (!glissement || evenement.pointerId !== glissement.id) return;
      var dx = evenement.clientX - glissement.x;
      var dy = evenement.clientY - glissement.y;
      if (!glissement.glisse && (dx * dx + dy * dy) > 25) glissement.glisse = true;
      if (!glissement.glisse) return;
      var echelle = vue.largeur / Math.max(racine.clientWidth, 1);
      vue.x = glissement.vueX - dx * echelle;
      vue.y = glissement.vueY - dy * echelle;
      bornerVue();
      appliquerVue();
    });
    function terminerGlissement(evenement) {
      if (!glissement || evenement.pointerId !== glissement.id) return;
      if (glissement.glisse) {
        ignorerProchainClic = true;
        setTimeout(function () { ignorerProchainClic = false; }, 0);
      }
      glissement = null;
    }
    window.addEventListener("pointerup", terminerGlissement);
    window.addEventListener("pointercancel", terminerGlissement);
    svg.addEventListener("dragstart", function (evenement) {
      evenement.preventDefault();
    });
    svg.addEventListener("click", function (evenement) {
      if (!ignorerProchainClic) return;
      ignorerProchainClic = false;
      evenement.stopPropagation();
      evenement.preventDefault();
    }, true);
    svg.addEventListener("dblclick", function (evenement) {
      if (evenement.target && evenement.target.closest && evenement.target.closest(".couts-departement")) return;
      // Le double-clic complète le clavier et la molette : agrandir sans viser
      // le bouton « + », qui reste le chemin accessible.
      zoomer(0.6);
    });
    racine.addEventListener("wheel", function (evenement) {
      if (!evenement.ctrlKey) return; // le zoom natif de la page reste prioritaire
      evenement.preventDefault();
      zoomer(evenement.deltaY > 0 ? 1.2 : 0.85);
    }, { passive: false });
  }

  function etatDeLaCollecte() {
    return charger(DOSSIER + "_etat.json")
      .then(function (etat) {
        var couverture = etat.couverture || {};
        etatCollecte.textContent =
          "Collecte du " + etat.collecte + " : " + nombre(couverture.communes || 0) +
          " communes, dont " + nombre(couverture.communes_avec_prix || 0) +
          " avec un prix de vente publié. Sources : DVF (DGFiP) et découpage administratif de l’État.";
      })
      .catch(function () {
        etatCollecte.textContent =
          "Aucune collecte n’a encore été faite : la carte se dessine, mais aucun prix n’est publié. " +
          "Le site préfère ne rien afficher plutôt qu’un chiffre inventé.";
      });
  }

  charger(DOSSIER + "fond-departements.json")
    .then(function (contenu) {
      fond = contenu;
      dessinerDepartements();
      brancher();
      cadrerFrance();
      dire("Carte de la métropole prête. Choisissez un département ou cherchez une commune.");
      var vise = null;
      var depVise = null;
      try {
        var params = new URL(window.location.href).searchParams;
        vise = params.get("commune");
        depVise = params.get("dep");
      } catch (_erreur) {
        vise = null;
        depVise = null;
      }
      if (vise) ouvrirCommuneParCode(vise);
      else if (depVise) ouvrirDepartementParCode(depVise);
      return etatDeLaCollecte();
    })
    .catch(function () {
      dire("Le fond de carte n’a pas pu être chargé : aucune carte n’est affichée plutôt qu’une carte fausse.");
      if (etatCollecte) {
        etatCollecte.textContent = "Fond de carte indisponible : " + DOSSIER + "fond-departements.json";
      }
    });
})();
