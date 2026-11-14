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

  var racine = document.querySelector("[data-couts-vue]");
  if (!racine) return;

  var svg = racine.querySelector("[data-couts-svg]");
  var groupe = racine.querySelector("[data-couts-departements]");
  var message = racine.querySelector("[data-couts-message]");
  var etatCollecte = document.querySelector("[data-etat-collecte]");
  var choix = document.querySelector("[data-couts-departement]");
  var recherche = document.querySelector("[data-couts-recherche]");
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
    vue.largeur = besoin * 1.12;
    vue.x = (a[0] + b[0]) / 2 - vue.largeur / 2;
    vue.y = (a[1] + b[1]) / 2 - (vue.largeur * ratio) / 2;
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

  function ouvrirDepartement(code) {
    if (!code || !fond) return;
    var departement = fond.departements.filter(function (d) { return d.c === code; })[0];
    if (!departement) return;
    departementOuvert = code;
    donneesDepartement = null;
    communeChoisie = null;
    choix.value = code;
    colorer();
    viderFiche();
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
    var echelle = vue.largeur / 100;
    communes.forEach(function (commune) {
      var point = projeter(commune.x, commune.y);
      var cercle = document.createElementNS("http://www.w3.org/2000/svg", "circle");
      cercle.setAttribute("cx", point[0]);
      cercle.setAttribute("cy", point[1]);
      cercle.setAttribute("r", (0.16 * echelle).toFixed(3));
      cercle.setAttribute("class", "couts-commune" + (commune.pa || commune.pm ? " a-un-prix" : ""));
      var titre = document.createElementNS("http://www.w3.org/2000/svg", "title");
      titre.textContent = commune.n + (commune.pa || commune.pm ? " — prix publié" : " — sans prix publié");
      cercle.appendChild(titre);
      cercle.addEventListener("click", function () {
        choisirCommune(commune);
      });
      groupeCommunes.appendChild(cercle);
    });
    svg.appendChild(groupeCommunes);
  }

  function viderFiche() {
    fiche.hidden = true;
    vide.hidden = false;
    resultat.textContent = "—";
  }

  function choisirCommune(commune) {
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

  function filtrerRecherche() {
    if (!donneesDepartement) return;
    var terme = (recherche.value || "").trim().toLowerCase();
    var trouvees = donneesDepartement.communes.filter(function (commune) {
      return !terme || commune.n.toLowerCase().indexOf(terme) !== -1;
    });
    if (terme && trouvees.length === 1) {
      choisirCommune(trouvees[0]);
      return;
    }
    if (terme && !trouvees.length) {
      viderFiche();
      dire("Aucune commune de ce département ne correspond à « " + recherche.value + " ».");
      return;
    }
    if (terme) {
      dire(trouvees.length + " commune(s) correspondent dans ce département.");
    }
  }

  function zoomer(facteur) {
    var centreX = vue.x + vue.largeur / 2;
    var ratio = racine.clientHeight / Math.max(racine.clientWidth, 1);
    var centreY = vue.y + (vue.largeur * ratio) / 2;
    vue.largeur = Math.min(Math.max(vue.largeur * facteur, 1.5), 140);
    vue.x = centreX - vue.largeur / 2;
    vue.y = centreY - (vue.largeur * ratio) / 2;
    appliquerVue();
  }

  function brancher() {
    choix.addEventListener("change", function () { ouvrirDepartement(choix.value); });
    recherche.addEventListener("input", filtrerRecherche);
    mensualite.addEventListener("input", calculerSurface);
    Array.prototype.forEach.call(document.querySelectorAll("[data-couts-zoom]"), function (bouton) {
      bouton.addEventListener("click", function () {
        zoomer(bouton.getAttribute("data-couts-zoom") === "plus" ? 0.7 : 1.45);
      });
    });
    document.querySelector("[data-couts-recentrer]").addEventListener("click", function () {
      departementOuvert = null;
      choix.value = "";
      colorer();
      cadrerFrance();
      dire("Vue d’ensemble de la métropole. Choisissez un département.");
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
      appliquerVue();
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
      dire("Carte de la métropole prête. Choisissez un département pour voir ses communes.");
      return etatDeLaCollecte();
    })
    .catch(function () {
      dire("Le fond de carte n’a pas pu être chargé : aucune carte n’est affichée plutôt qu’une carte fausse.");
      if (etatCollecte) {
        etatCollecte.textContent = "Fond de carte indisponible : " + DOSSIER + "fond-departements.json";
      }
    });
})();
