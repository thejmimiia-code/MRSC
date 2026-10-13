/* Historique de navigation M.R.S.C, limité aux pages du site et à l’onglet courant.
   Aucune requête réseau n’est ajoutée ; seuls les chemins et ancres sont conservés
   dans sessionStorage, jamais le texte saisi ni les paramètres de requête. */
(() => {
  const STORAGE_KEY = "mrsc-parcours-navigation-v1";
  const MAX_STEPS = 80;
  const currentUrl = new URL(window.location.href);
  const homeLink = document.querySelector("[data-site-home], .identity > a[href], #mrsc-retour-site a[href]");
  const header = document.querySelector(".site-header");
  const navInner = header?.querySelector(".nav-inner");
  const returnBar = document.getElementById("mrsc-retour-site");
  const homeUrl = homeLink ? new URL(homeLink.href, currentUrl) : new URL("index.html", currentUrl);
  const homePath = normaliser(homeUrl);
  const basePath = homePath.endsWith("index.html")
    ? homePath.slice(0, -"index.html".length)
    : homePath;
  let parentHasSiteHeader = false;
  if (returnBar && window.parent !== window) {
    try {
      parentHasSiteHeader = Boolean(
        window.parent.document.querySelector(".site-header .nav-inner [data-menu-toggle]")
      );
    } catch (error) {
      parentHasSiteHeader = false;
    }
  }

  if (!homePath || !basePath) return;
  if (
    document.querySelector("[data-site-journey]")
    || (!header && !returnBar)
    || (!returnBar && !navInner)
    || parentHasSiteHeader
  ) return;

  let stockageDisponible = true;

  function normaliser(url) {
    if (url.origin !== currentUrl.origin) return "";
    let path = url.pathname;
    if (path.endsWith("index.html")) path = path.slice(0, -"index.html".length);
    if (!path) path = "/";
    return `${path}${url.hash || ""}`;
  }

  function estDansLeSite(path) {
    const sansAncre = path.split("#", 1)[0];
    return sansAncre === basePath.replace(/\/$/, "")
      || sansAncre.startsWith(basePath);
  }

  function estAccueil(path) {
    return path.split("#", 1)[0].replace(/\/$/, "")
      === homePath.split("#", 1)[0].replace(/\/$/, "");
  }

  function cheminValide(value) {
    if (typeof value !== "string" || !value.startsWith("/")) return "";
    try {
      const url = new URL(value, currentUrl.origin);
      const path = normaliser(url);
      return url.origin === currentUrl.origin && estDansLeSite(path) ? path : "";
    } catch (error) {
      return "";
    }
  }

  function lire() {
    try {
      const raw = window.sessionStorage.getItem(STORAGE_KEY);
      if (!raw) return null;
      const parsed = JSON.parse(raw);
      if (!parsed || parsed.version !== 1 || !Array.isArray(parsed.etapes)) return null;
      const etapes = parsed.etapes.map(cheminValide).filter(Boolean).slice(-MAX_STEPS);
      if (!etapes.length) return null;
      const position = Math.max(0, Math.min(etapes.length - 1, Number(parsed.position) || 0));
      const dernierPoint = cheminValide(parsed.dernierPoint);
      return { version: 1, etapes, position, dernierPoint };
    } catch (error) {
      stockageDisponible = false;
      return null;
    }
  }

  function enregistrer() {
    try {
      window.sessionStorage.setItem(STORAGE_KEY, JSON.stringify(etat));
      stockageDisponible = true;
    } catch (error) {
      stockageDisponible = false;
    }
  }

  function hrefPour(path) {
    return new URL(path, currentUrl.origin).href;
  }

  function limiterHistorique() {
    while (etat.etapes.length > MAX_STEPS) {
      etat.etapes.shift();
      etat.position = Math.max(0, etat.position - 1);
    }
    if (etat.dernierPoint && !etat.etapes.includes(etat.dernierPoint)) {
      const precedente = [...etat.etapes].reverse().find((path) => !estAccueil(path));
      etat.dernierPoint = precedente || "";
    }
  }

  function ajouterEtape(path, mettreAJourDernierPoint = true) {
    if (!path || !estDansLeSite(path)) return false;
    const positionActuelle = etat.etapes[etat.position];
    if (path === positionActuelle) return false;
    etat.etapes = etat.etapes.slice(0, etat.position + 1);
    etat.etapes.push(path);
    etat.position = etat.etapes.length - 1;
    if (mettreAJourDernierPoint && !estAccueil(path)) etat.dernierPoint = path;
    limiterHistorique();
    enregistrer();
    actualiser();
    return true;
  }

  let cheminActuel = normaliser(currentUrl);
  let etat = lire();
  if (!etat) {
    etat = {
      version: 1,
      etapes: [cheminActuel],
      position: 0,
      dernierPoint: estAccueil(cheminActuel) ? "" : cheminActuel,
    };
  } else {
    const cheminEnCours = etat.etapes[etat.position];
    if (cheminEnCours !== cheminActuel) {
      const positionConnue = etat.etapes.lastIndexOf(cheminActuel);
      if (positionConnue >= 0) {
        etat.position = positionConnue;
      } else {
        etat.etapes = etat.etapes.slice(0, etat.position + 1);
        etat.etapes.push(cheminActuel);
        etat.position = etat.etapes.length - 1;
        if (!estAccueil(cheminActuel)) etat.dernierPoint = cheminActuel;
      }
    }
    if (!etat.dernierPoint && !estAccueil(cheminActuel)) etat.dernierPoint = cheminActuel;
  }
  limiterHistorique();
  enregistrer();

  const parcours = document.createElement("details");
  parcours.className = "site-journey-settings";
  parcours.dataset.siteJourney = "";

  const declencheur = document.createElement("summary");
  declencheur.className = "site-journey-summary";
  declencheur.textContent = "Parcours";
  declencheur.title = "Afficher ou masquer les commandes de navigation du parcours";
  declencheur.setAttribute("aria-label", "Afficher ou masquer les commandes de navigation du parcours");

  const chevron = document.createElement("span");
  chevron.className = "site-journey-chevron";
  chevron.setAttribute("aria-hidden", "true");
  chevron.textContent = "⌄";
  declencheur.appendChild(chevron);

  const panneau = document.createElement("div");
  panneau.className = "site-journey-panel";
  panneau.id = "site-journey-controls-panel";
  panneau.dataset.siteJourneyPanel = "";
  declencheur.setAttribute("aria-controls", panneau.id);
  parcours.append(declencheur, panneau);

  const barre = document.createElement("div");
  barre.className = "site-journey-navigation";
  barre.setAttribute("role", "group");
  barre.setAttribute("aria-label", "Navigation des pages visitées dans cet onglet");

  const contenuBarre = document.createElement("div");
  contenuBarre.className = "site-journey-inner";

  const commandes = document.createElement("div");
  commandes.className = "site-journey-controls";

  function creerBouton(action, libelle, ariaLabel, symbole) {
    const bouton = document.createElement("button");
    bouton.className = "site-journey-button";
    bouton.type = "button";
    bouton.dataset.journeyAction = action;
    bouton.setAttribute("aria-label", ariaLabel);
    bouton.title = ariaLabel;
    const icone = document.createElement("span");
    icone.className = "site-journey-symbol";
    icone.setAttribute("aria-hidden", "true");
    icone.textContent = symbole;
    const texte = document.createElement("span");
    texte.className = "site-journey-label";
    texte.textContent = libelle;
    bouton.append(icone, texte);
    commandes.appendChild(bouton);
    return bouton;
  }

  const precedent = creerBouton("precedent", "Précédent", "Revenir à l’étape précédente du parcours", "←");
  const suivant = creerBouton("suivant", "Suivant", "Avancer à l’étape suivante du parcours", "→");
  const accueil = creerBouton("accueil", "Accueil", "Revenir à la page d’accueil du site", "⌂");
  const dernier = creerBouton("dernier", "Dernière vue", "Aller directement au dernier point visité avant l’accueil", "↠");

  const statut = document.createElement("p");
  statut.className = "site-journey-status";
  statut.dataset.journeyStatus = "";
  statut.setAttribute("role", "status");
  statut.setAttribute("aria-live", "polite");
  statut.setAttribute("aria-atomic", "true");

  contenuBarre.append(commandes, statut);
  barre.appendChild(contenuBarre);
  panneau.appendChild(barre);

  const menuToggle = document.querySelector("[data-menu-toggle]");
  const navigation = document.querySelector("[data-primary-navigation]");
  const displaySettings = document.querySelector("[data-display-settings]");
  const headerCompactToggle = document.querySelector("[data-header-compact-toggle]");
  const fermerMenu = () => {
    if (!menuToggle || !navigation) return;
    menuToggle.setAttribute("aria-expanded", "false");
    navigation.classList.remove("is-open");
  };

  parcours.addEventListener("toggle", () => {
    if (!parcours.open) return;
    fermerMenu();
    if (displaySettings) displaySettings.open = false;
  });
  displaySettings?.addEventListener("toggle", () => {
    if (!displaySettings.open) return;
    fermerMenu();
    parcours.open = false;
  });
  menuToggle?.addEventListener("click", () => {
    if (menuToggle.getAttribute("aria-expanded") !== "true") return;
    parcours.open = false;
    if (displaySettings) displaySettings.open = false;
  });
  headerCompactToggle?.addEventListener("click", () => {
    parcours.open = false;
  });
  document.addEventListener("click", (event) => {
    if (!parcours.contains(event.target)) parcours.open = false;
  });
  document.addEventListener("keydown", (event) => {
    if (event.key !== "Escape" || !parcours.open) return;
    const focusInside = parcours.contains(document.activeElement);
    parcours.open = false;
    if (focusInside) declencheur.focus();
  });

  if (returnBar) {
    const displayControls = returnBar.querySelector("#mrsc-display-controls");
    if (displayControls) returnBar.insertBefore(parcours, displayControls);
    else returnBar.appendChild(parcours);
  } else {
    const displaySettingsInHeader = navInner.querySelector("[data-display-settings]");
    navInner.insertBefore(parcours, displaySettingsInHeader);
  }

  function actualiser() {
    precedent.disabled = !stockageDisponible || etat.position <= 0;
    suivant.disabled = !stockageDisponible || etat.position >= etat.etapes.length - 1;
    accueil.disabled = cheminActuel === homePath;
    dernier.disabled = !etat.dernierPoint || etat.dernierPoint === cheminActuel;
    const numero = etat.position + 1;
    const total = etat.etapes.length;
    statut.textContent = stockageDisponible
      ? `Étape ${numero}/${total}`
      : "Parcours local indisponible ; utilisez la navigation du navigateur.";
  }

  function naviguerVers(path, ajouterSiAbsent = false) {
    if (!path || path === cheminActuel) return;
    const trouve = etat.etapes.lastIndexOf(path);
    if (trouve >= 0) {
      etat.position = trouve;
    } else if (ajouterSiAbsent) {
      etat.etapes = etat.etapes.slice(0, etat.position + 1);
      etat.etapes.push(path);
      etat.position = etat.etapes.length - 1;
    } else {
      return;
    }
    limiterHistorique();
    enregistrer();
    window.location.assign(hrefPour(path));
  }

  precedent.addEventListener("click", () => {
    if (etat.position > 0) naviguerVers(etat.etapes[etat.position - 1]);
  });

  suivant.addEventListener("click", () => {
    if (etat.position < etat.etapes.length - 1) naviguerVers(etat.etapes[etat.position + 1]);
  });

  accueil.addEventListener("click", () => {
    if (cheminActuel !== homePath) {
      if (!estAccueil(cheminActuel)) etat.dernierPoint = cheminActuel;
      if (ajouterEtape(homePath, false)) window.location.assign(hrefPour(homePath));
    }
  });

  dernier.addEventListener("click", () => {
    if (etat.dernierPoint && etat.dernierPoint !== cheminActuel) {
      naviguerVers(etat.dernierPoint, true);
    }
  });

  document.addEventListener("click", (event) => {
    if (event.defaultPrevented || event.button !== 0 || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
    const lien = event.target.closest?.("a[href]");
    if (!lien || lien.hasAttribute("download") || lien.target && lien.target !== "_self") return;
    if (lien.dataset.noJourney !== undefined || lien.getAttribute("rel")?.split(/\s+/).includes("external")) return;
    let destination;
    try {
      destination = new URL(lien.href, currentUrl);
    } catch (error) {
      return;
    }
    const path = normaliser(destination);
    if (!path || !estDansLeSite(path) || path === cheminActuel) return;
    if (estAccueil(path) && !estAccueil(cheminActuel)) etat.dernierPoint = cheminActuel;
    ajouterEtape(path, !estAccueil(path));
  }, true);

  function synchroniser() {
    etat = lire() || etat;
    cheminActuel = normaliser(new URL(window.location.href));
    const path = cheminActuel;
    const position = etat.etapes.lastIndexOf(path);
    if (position >= 0) etat.position = position;
    else ajouterEtape(path, !estAccueil(path));
    enregistrer();
    actualiser();
  }

  window.addEventListener("popstate", synchroniser);
  window.addEventListener("hashchange", synchroniser);
  window.addEventListener("pageshow", synchroniser);
  window.addEventListener("pagehide", enregistrer);
  actualiser();
})();
