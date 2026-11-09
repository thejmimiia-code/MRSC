(() => {
  document.querySelectorAll("[data-year]").forEach((element) => {
    element.textContent = String(new Date().getFullYear());
  });
  document.documentElement.dataset.printUrl = window.location.href;

  const root = document.documentElement;
  const simulatorFrames = Array.from(document.querySelectorAll("[data-simulateur-apercu] iframe"));
  const synchroniserSimulateurs = () => {
    simulatorFrames.forEach((frame) => {
      try {
        if (frame.contentWindow.location.origin !== window.location.origin) return;
        const simulatorRoot = frame.contentDocument?.documentElement;
        if (!simulatorRoot) return;
        [
          "texte-tres-reduit",
          "texte-reduit",
          "texte-agrandi",
          "texte-tres-agrandi",
          "contraste-renforce",
          "espacement-renforce",
        ].forEach((classe) => {
          simulatorRoot.classList.toggle(classe, root.classList.contains(classe));
        });
        simulatorRoot.dataset.layout = root.dataset.layout || "equilibree";
        simulatorRoot.dataset.apparence = root.dataset.apparence || "systeme";
        simulatorRoot.dataset.apparenceFond = root.dataset.apparenceFond || "clair";
      } catch (erreur) {
        // Une page parente ne peut pas modifier une iframe d’une autre origine.
      }
    });
  };
  simulatorFrames.forEach((frame) => frame.addEventListener("load", synchroniserSimulateurs));
  const settings = document.querySelector("[data-display-settings]");
  const textDecrease = document.querySelector("[data-text-decrease]");
  const textIncrease = document.querySelector("[data-text-increase]");
  const textLevelOutput = document.querySelector("[data-text-size-level]");
  const contrastToggle = document.querySelector("[data-contrast-toggle]");
  const spacingToggle = document.querySelector("[data-spacing-toggle]");
  // Les crans sont resserrés : 50/75/100/125/150 donnaient 8 px de corps au
  // plus petit cran, illisible. L'échelle va de 75 à 130 %. La clé de stockage
  // change avec l'échelle : les anciennes valeurs (75 signifiait « réduit »)
  // sont ambiguës avec les nouvelles (75 est le nouveau minimum), d'où une
  // migration explicite depuis l'ancienne clé à la première visite.
  const keys = {
    text: "mrsc-texte-cran",
    contrast: "mrsc-contraste-renforce",
    spacing: "mrsc-espacement-renforce",
  };
  // Réduire l'en-tête est un choix de la personne, pas un effet du format de
  // fenêtre. Le 5 novembre 2026, ce choix n'était pas mémorisé : chaque entrée
  // du menu charge une autre page, et l'en-tête y repartait agrandi — mesuré en
  // navigateur à 1 440 px, de 49 px à 198 px au moment du clic. La préférence
  // est donc lue au chargement, comme celles du texte et du contraste.
  const CLE_ENTETE_COMPACTE = "mrsc-entete-compacte";
  const textLevels = [75, 85, 100, 115, 130];
  // Ancienne échelle en pourcentage, puis anciens crans indexés 0/1/2.
  const anciensCrans = { 50: 75, 75: 85, 100: 100, 125: 115, 150: 130 };
  const anciensIndexes = [100, 115, 130];
  const ANCIENNE_CLE = "mrsc-texte-niveau";
  let textLevel = 100;
  let contrastEnabled = false;
  let spacingEnabled = false;
  // Rappels exécutés après un changement de réglage d'affichage. La taille du
  // texte et l'espacement changent la largeur des entrées de navigation : le
  // panneau du menu doit alors réévaluer s'il est flottant, et se replacer.
  const apresChangementReglages = [];
  // Rappel branché plus bas, quand l'en-tête et sa bascule existent : le
  // chargement des préférences précède leur mise en place dans le script.
  let appliquerPreferenceEntete = null;
  let preferenceCompacte = null;

  const readPreference = (key) => {
    try {
      return window.localStorage.getItem(key);
    } catch (erreur) {
      return null;
    }
  };

  const savePreference = (key, value) => {
    try {
      window.localStorage.setItem(key, value);
    } catch (erreur) {
      // Les contrôles restent utilisables pendant la visite si le stockage est bloqué.
    }
  };

  // `null` = aucun choix explicite : c'est alors le format de fenêtre qui
  // décide. Les deux valeurs acceptées sont écrites par la bascule elle-même ;
  // une valeur inconnue ou un stockage indisponible reviennent à ce défaut.
  const lirePreferenceEnteteCompacte = () => {
    const valeur = readPreference(CLE_ENTETE_COMPACTE);
    if (valeur === "oui") return true;
    if (valeur === "non") return false;
    return null;
  };

  preferenceCompacte = lirePreferenceEnteteCompacte();

  const niveauTexteEnregistre = (value) => {
    if (value === null) return null;
    const stored = String(value).trim();
    const parsed = Number(stored);
    if (Number.isInteger(parsed) && textLevels.includes(parsed)) return parsed;
    return null;
  };

  // Reprise d'une préférence enregistrée avant le changement d'échelle.
  const niveauTexteMigre = () => {
    const ancien = readPreference(ANCIENNE_CLE);
    if (ancien !== null) {
      const stored = String(ancien).trim();
      if (/^[0-2]$/.test(stored)) return anciensIndexes[Number(stored)];
      return anciensCrans[Number(stored)] ?? 100;
    }
    return readPreference("mrsc-texte-agrandi") === "oui" ? 115 : 100;
  };

  const applyTextLevel = (value) => {
    textLevel = textLevels.includes(value) ? value : 100;
    root.classList.toggle("texte-tres-reduit", textLevel === 75);
    root.classList.toggle("texte-reduit", textLevel === 85);
    root.classList.toggle("texte-agrandi", textLevel === 115);
    root.classList.toggle("texte-tres-agrandi", textLevel === 130);
    if (textLevelOutput) textLevelOutput.textContent = `${textLevel} %`;
    if (textDecrease) textDecrease.disabled = textLevel === textLevels[0];
    if (textIncrease) textIncrease.disabled = textLevel === textLevels[textLevels.length - 1];
    synchroniserSimulateurs();
    apresChangementReglages.forEach((rappel) => rappel());
  };

  const applyContrast = (enabled) => {
    contrastEnabled = Boolean(enabled);
    root.classList.toggle("contraste-renforce", contrastEnabled);
    if (contrastToggle) {
      contrastToggle.setAttribute("aria-pressed", String(contrastEnabled));
    }
    synchroniserSimulateurs();
  };

  const applySpacing = (enabled) => {
    spacingEnabled = Boolean(enabled);
    root.classList.toggle("espacement-renforce", spacingEnabled);
    if (spacingToggle) {
      spacingToggle.setAttribute("aria-pressed", String(spacingEnabled));
    }
    synchroniserSimulateurs();
    apresChangementReglages.forEach((rappel) => rappel());
  };

  const loadPreferences = () => {
    const storedTextLevel = readPreference(keys.text);
    if (storedTextLevel === null) {
      textLevel = niveauTexteMigre();
      // La nouvelle échelle est écrite tout de suite : la migration n'a lieu
      // qu'une fois, et le simulateur lit la même clé.
      savePreference(keys.text, String(textLevel));
    } else {
      textLevel = niveauTexteEnregistre(storedTextLevel) ?? 100;
    }
    applyTextLevel(textLevel);
    applyContrast(readPreference(keys.contrast) === "oui");
    applySpacing(readPreference(keys.spacing) === "oui");
  };

  loadPreferences();

  const layoutPreferenceKey = "mrsc-mise-en-page";
  // Six présentations CSS, classées par intention. Elles réorganisent les
  // blocs sans jamais supprimer, réordonner ni réécrire le contenu.
  // Étude et arbitrages : docs/rd/presentations-personnalisees.md.
  const layoutChoices = [
    {
      value: "equilibree",
      label: "Équilibrée",
      description: "La présentation de base, entre lecture et blocs visuels.",
      hint: "Le réglage par défaut du site.",
    },
    {
      value: "lecture",
      label: "Lecture",
      description: "Une colonne plus étroite et des blocs empilés pour suivre les textes.",
      hint: "Idéal pour : les fiches et les textes suivis.",
    },
    {
      value: "vitrine",
      label: "Vitrine",
      description: "De grands titres, beaucoup d’air et une idée à la fois, comme une page de présentation.",
      hint: "Idéal pour : découvrir l’accueil, le dossier IA ou ÉVA.",
    },
    {
      value: "mosaique",
      label: "Mosaïque",
      description: "Des tuiles de tailles variées ; certaines cartes de chaque collection sont mises en avant, dans le même ordre.",
      hint: "Idéal pour : explorer les fiches, les Mondes, les liens et les documents.",
    },
    {
      value: "panorama",
      label: "Panorama composite",
      description: "Une page plus large, avec un agencement de cartes en plusieurs colonnes.",
      hint: "Idéal pour : les grands écrans.",
    },
    {
      value: "compacte",
      label: "Compacte",
      description: "Des blocs resserrés pour voir davantage de cartes sans faire défiler longtemps.",
      hint: "Idéal pour : comparer et balayer un catalogue ou un registre.",
    },
  ];
  const layoutSettings = settings ? document.createElement("details") : null;
  // Panneau « Personnalisation » : déclaré ici pour que les gestionnaires de clic
  // et de clavier, plus bas, puissent le fermer, et pour que le placement
  // mesuré (voir `placerPanneauPersonnalisation`) le retrouve.
  let personnalisation = null;
  let panneauPersonnalisation = null;
  const layoutInputs = [];
  let layoutStatus = null;

  const applyLayout = (value) => {
    const selected = layoutChoices.find((choice) => choice.value === value)
      || layoutChoices[0];
    root.dataset.layout = selected.value;
    synchroniserSimulateurs();
    layoutInputs.forEach(({ input, label }) => {
      input.checked = input.value === selected.value;
      label.classList.toggle("is-selected", input.checked);
    });
    if (layoutStatus) {
      layoutStatus.textContent = `Présentation « ${selected.label} » appliquée.`;
    }
  };

  if (layoutSettings) {
    layoutSettings.className = "layout-settings";
    layoutSettings.dataset.siteLayoutSettings = "";

    const summary = document.createElement("summary");
    summary.className = "layout-settings-summary";
    summary.title = "Ouvrir ou fermer les choix de présentation du site";
    summary.setAttribute("aria-controls", "site-layout-settings-panel");
    summary.append(document.createTextNode("Présentation"));

    const chevron = document.createElement("span");
    chevron.className = "layout-settings-chevron";
    chevron.setAttribute("aria-hidden", "true");
    chevron.textContent = "⌄";
    summary.appendChild(chevron);

    const panel = document.createElement("div");
    panel.className = "layout-settings-panel";
    panel.id = "site-layout-settings-panel";
    panel.setAttribute("aria-label", "Personnaliser l’expérience de lecture");

    const title = document.createElement("p");
    title.className = "layout-settings-title";
    const titleStrong = document.createElement("strong");
    titleStrong.textContent = "Personnaliser l’expérience";
    title.appendChild(titleStrong);

    const options = document.createElement("fieldset");
    options.className = "layout-settings-options";
    const legend = document.createElement("legend");
    legend.textContent = "Choisissez une mise en page";
    options.appendChild(legend);

    layoutChoices.forEach((choice) => {
      const label = document.createElement("label");
      label.className = "layout-choice";

      const input = document.createElement("input");
      input.type = "radio";
      input.name = "mrsc-site-layout";
      input.value = choice.value;
      input.id = `site-layout-${choice.value}`;
      input.addEventListener("change", () => {
        if (!input.checked) return;
        applyLayout(input.value);
        savePreference(layoutPreferenceKey, input.value);
      });

      // Mini-aperçu schématique et décoratif : le nom et la description
      // restent l’information complète pour les technologies d’assistance.
      const preview = document.createElement("span");
      preview.className = "layout-choice-preview";
      preview.dataset.preview = choice.value;
      preview.setAttribute("aria-hidden", "true");
      for (let bloc = 0; bloc < 6; bloc += 1) {
        preview.appendChild(document.createElement("span"));
      }

      const copy = document.createElement("span");
      copy.className = "layout-choice-copy";
      const name = document.createElement("strong");
      name.textContent = choice.label;
      const description = document.createElement("span");
      description.textContent = choice.description;
      const hint = document.createElement("span");
      hint.className = "layout-choice-hint";
      hint.textContent = choice.hint;
      copy.append(name, description, hint);
      label.htmlFor = input.id;
      label.append(input, preview, copy);
      options.appendChild(label);
      layoutInputs.push({ input, label });
    });

    layoutStatus = document.createElement("p");
    layoutStatus.className = "layout-settings-status";
    layoutStatus.setAttribute("role", "status");
    layoutStatus.setAttribute("aria-live", "polite");
    layoutStatus.setAttribute("aria-atomic", "true");

    const note = document.createElement("p");
    note.className = "layout-settings-note";
    note.textContent = "Le changement est immédiat, sans rechargement. Si le stockage local est autorisé, votre choix est mémorisé sur cet appareil.";

    const reset = document.createElement("button");
    reset.type = "button";
    reset.className = "display-control display-control-wide layout-settings-reset";
    reset.textContent = "Réinitialiser la présentation";
    reset.addEventListener("click", () => {
      applyLayout("equilibree");
      savePreference(layoutPreferenceKey, "equilibree");
    });

    panel.append(title, options, layoutStatus, note, reset);
    layoutSettings.append(summary, panel);
    settings.insertAdjacentElement("afterend", layoutSettings);
    applyLayout(readPreference(layoutPreferenceKey));

    layoutSettings.addEventListener("toggle", () => {
      if (!layoutSettings.open) return;
      if (settings) settings.open = false;
      if (apparenceSettings) apparenceSettings.open = false;
      const journeySettings = document.querySelector("[data-site-journey]");
      if (journeySettings) journeySettings.open = false;
      if (toggle && navigation) {
        toggle.setAttribute("aria-expanded", "false");
        navigation.classList.remove("is-open");
      }
    });

    window.addEventListener("storage", (event) => {
      if (event.key === null || event.key === layoutPreferenceKey) {
        applyLayout(readPreference(layoutPreferenceKey));
      }
    });
  }

  // --- Apparences -----------------------------------------------------------
  // Six thèmes d'affichage : les trois réglages les plus courants sur le Web,
  // puis trois palettes originales inspirées d'ambiances de bande magnétique,
  // de tableau de bord rétro-futuriste et de salle d'arcade. Les noms, couleurs
  // et décors sont originaux : aucune œuvre, marque, personnage ni logotype
  // n'est repris et aucune affiliation n'est suggérée. Le choix des noms et des
  // palettes reste une proposition d'agent, à faire relire par l'association ;
  // voir docs/rd/apparences-themes.md.
  const CLE_APPARENCE = "mrsc-apparence";
  const APPAREIL_SOMBRE = window.matchMedia
    ? window.matchMedia("(prefers-color-scheme: dark)")
    : null;
  const APPARENCES = [
    {
      value: "systeme", label: "Suivre l'appareil", fond: "clair", themeColor: "#1d3268",
      description: "Le réglage clair ou sombre choisi sur votre appareil.",
      swatchFond: "#f5f7fa", swatchAccent: "#1d3268",
    },
    {
      value: "clair", label: "Papier clair", fond: "clair", themeColor: "#f5f7fa",
      description: "Fond clair et texte marine : la présentation habituelle.",
      swatchFond: "#ffffff", swatchAccent: "#2958a2",
    },
    {
      value: "sombre", label: "Nuit sobre", fond: "sombre", themeColor: "#111827",
      description: "Fond sombre, même hiérarchie, sans décor ajouté.",
      swatchFond: "#111827", swatchAccent: "#8fbaff",
    },
    {
      value: "bobine", label: "Bobine nocturne", fond: "sombre", themeColor: "#1a1018",
      description: "Bleu nuit, néon rouge et fines lignes de bande magnétique.",
      swatchFond: "#1a1018", swatchAccent: "#ff6b6b",
    },
    {
      value: "horizon", label: "Cap horizon", fond: "sombre", themeColor: "#1b1620",
      description: "Cuivre et ambre, comme un tableau de bord rétro.",
      swatchFond: "#1b1620", swatchAccent: "#ff9e42",
    },
    {
      value: "arcade", label: "Salle d'arcade", fond: "sombre", themeColor: "#0d1424",
      description: "Grille lumineuse cyan et magenta sur fond profond.",
      swatchFond: "#0d1424", swatchAccent: "#6ce4ff",
    },
  ];
  const apparitionConnue = (valeur) =>
    APPARENCES.find((apparence) => apparence.value === valeur) || APPARENCES[0];
  const fondEffectif = (valeur) => {
    const apparence = apparitionConnue(valeur);
    if (apparence.value === "systeme") {
      return APPAREIL_SOMBRE && APPAREIL_SOMBRE.matches ? "sombre" : "clair";
    }
    return apparence.fond;
  };
  const lireApparence = () => apparitionConnue(readPreference(CLE_APPARENCE)).value;

  let apparenceCourante = "systeme";
  let apparenceInputs = [];
  let apparenceStatus = null;
  const apparenceSettings = settings ? document.createElement("details") : null;

  const appliquerApparence = (valeur, options = {}) => {
    const apparence = apparitionConnue(valeur);
    const choix = apparence.value;
    apparenceCourante = choix;
    // Deux attributs distincts : le choix nominal pour les accents et le décor,
    // le fond résolu pour le bloc de jetons sombres. Ainsi « Suivre l'appareil »
    // partage exactement la même palette que « Nuit sobre ».
    root.dataset.apparence = choix;
    root.dataset.apparenceFond = fondEffectif(choix);
    const metaCouleur = document.querySelector('meta[name="theme-color"]');
    if (metaCouleur) metaCouleur.setAttribute("content", apparence.themeColor);
    apparenceInputs.forEach(({ input, label }) => {
      input.checked = input.value === choix;
      label.classList.toggle("is-selected", input.checked);
    });
    if (apparenceStatus) {
      apparenceStatus.textContent = `Apparence « ${apparence.label} » appliquée.`;
    }
    if (options.memoriser) savePreference(CLE_APPARENCE, choix);
    synchroniserSimulateurs();
    apresChangementReglages.forEach((rappel) => rappel());
  };

  if (apparenceSettings) {
    apparenceSettings.className = "apparence-settings";
    apparenceSettings.dataset.apparenceSettings = "";

    const resume = document.createElement("summary");
    resume.className = "apparence-settings-summary";
    resume.title = "Ouvrir ou fermer les thèmes d'affichage";
    resume.append(document.createTextNode("Apparence"));
    const chevron = document.createElement("span");
    chevron.className = "apparence-settings-chevron";
    chevron.setAttribute("aria-hidden", "true");
    chevron.textContent = "⌄";
    resume.append(" ", chevron);

    const panneau = document.createElement("div");
    panneau.className = "apparence-settings-panel";
    panneau.id = "site-apparence-settings-panel";
    panneau.setAttribute("aria-label", "Choisir un thème d'affichage");
    resume.setAttribute("aria-controls", panneau.id);

    const titre = document.createElement("p");
    titre.className = "apparence-settings-title";
    const titreFort = document.createElement("strong");
    titreFort.textContent = "Choisir une apparence";
    titre.appendChild(titreFort);

    const options = document.createElement("fieldset");
    options.className = "apparence-settings-options";
    const legende = document.createElement("legend");
    legende.textContent = "Thème d'affichage";
    options.appendChild(legende);

    APPARENCES.forEach((apparence) => {
      const label = document.createElement("label");
      label.className = "apparence-choice";

      const input = document.createElement("input");
      input.type = "radio";
      input.name = "mrsc-apparence";
      input.value = apparence.value;
      input.id = `site-apparence-${apparence.value}`;
      input.addEventListener("change", () => {
        if (!input.checked) return;
        appliquerApparence(input.value, { memoriser: true });
      });

      // L'aperçu est décoratif : le nom et la description portent l'information.
      const apercu = document.createElement("span");
      apercu.className = "apparence-swatch";
      apercu.setAttribute("aria-hidden", "true");
      apercu.style.setProperty("--swatch-fond", apparence.swatchFond);
      apercu.style.setProperty("--swatch-accent", apparence.swatchAccent);

      const copie = document.createElement("span");
      copie.className = "apparence-choice-copy";
      const nom = document.createElement("strong");
      nom.textContent = apparence.label;
      const description = document.createElement("span");
      description.textContent = apparence.description;
      copie.append(nom, description);

      label.htmlFor = input.id;
      label.append(input, apercu, copie);
      options.appendChild(label);
      apparenceInputs.push({ input, label });
    });

    apparenceStatus = document.createElement("p");
    apparenceStatus.className = "apparence-settings-status";
    apparenceStatus.setAttribute("role", "status");
    apparenceStatus.setAttribute("aria-live", "polite");
    apparenceStatus.setAttribute("aria-atomic", "true");

    const note = document.createElement("p");
    note.className = "apparence-settings-note";
    note.textContent = "Noms et couleurs originaux, sans lien avec une œuvre ou une marque. Le changement est immédiat et, si le stockage local est autorisé, mémorisé sur cet appareil. Aucune donnée n'est envoyée.";

    const retour = document.createElement("button");
    retour.type = "button";
    retour.className = "display-control display-control-wide apparence-settings-reset";
    retour.textContent = "Revenir à « Suivre l'appareil »";
    retour.addEventListener("click", () => appliquerApparence("systeme", { memoriser: true }));

    panneau.append(titre, options, apparenceStatus, note, retour);
    apparenceSettings.append(resume, panneau);
    settings.insertAdjacentElement("afterend", apparenceSettings);
    appliquerApparence(lireApparence());

    // Un seul réglage ouvert à la fois, et le panneau flottant est replacé :
    // ouvrir une section change sa hauteur, donc sa position sous le bouton.
    apparenceSettings.addEventListener("toggle", () => {
      if (!apparenceSettings.open) return;
      if (settings) settings.open = false;
      if (layoutSettings) layoutSettings.open = false;
      const journeySettings = document.querySelector("[data-site-journey]");
      if (journeySettings) journeySettings.open = false;
      ajusterPanneauxFlottants();
    });

    window.addEventListener("storage", (event) => {
      if (event.key === null || event.key === CLE_APPARENCE) {
        appliquerApparence(lireApparence());
      }
    });
    if (APPAREIL_SOMBRE && APPAREIL_SOMBRE.addEventListener) {
      APPAREIL_SOMBRE.addEventListener("change", () => {
        if (apparenceCourante === "systeme") appliquerApparence("systeme");
      });
    }
  } else {
    appliquerApparence(lireApparence());
  }

  // --- Écouter la page -------------------------------------------------------
  // Lecture à voix haute du contenu principal, pour qui lit difficilement, voit
  // peu ou se fatigue. Trois principes : rien n'est lu sans un geste explicite,
  // la voix est celle de l'appareil et rien n'est envoyé à un service distant,
  // et le bloc lu reste marqué à l'écran pour pouvoir suivre. La commande vit
  // dans « Personnalisation » : l'en-tête compact garde deux boutons.
  const syntheseVocaleDisponible = "speechSynthesis" in window
    && typeof window.SpeechSynthesisUtterance === "function";
  const SELECTEUR_LECTURE = "h1,h2,h3,h4,h5,h6,p,li,blockquote,figcaption,summary,td,th,dd,dt";
  const LONGUEUR_MAX_SEGMENT = 220;
  // Débits proposés, du plus lent au plus rapide. 1 correspond au débit par
  // défaut de l'appareil : le site n'impose pas un rythme unique.
  const VITESSES = [0.75, 1, 1.25, 1.5];
  const CLE_VITESSE = "mrsc-lecture-vitesse";

  const normaliserTexte = (texte) => (texte || "").replace(/\s+/g, " ").trim();

  // Un segment trop long est coupé à la fin d'une phrase : certains moteurs
  // interrompent une énonciation au bout d'une quinzaine de secondes.
  const decouperSegment = (texte) => {
    if (texte.length <= LONGUEUR_MAX_SEGMENT) return [texte];
    const segments = [];
    let reste = texte;
    while (reste.length > LONGUEUR_MAX_SEGMENT) {
      // La virgule de continuation ajoutée plus bas compte dans la limite : la
      // coupe se fait donc un caractère avant, pour qu'aucun segment ne dépasse
      // 220. Mesuré le 5 novembre 2026 dans la CI : une coupe à 220 pile donnait
      // un segment de 221, que le moteur interrompt en pleine phrase.
      let coupe = reste.lastIndexOf(" ", LONGUEUR_MAX_SEGMENT - 1);
      // La recherche de ponctuation s'arrête elle aussi un caractère avant la
      // limite : une coupe trouvée à 220 donnait `ponctuation + 1`, soit un
      // segment de 221 caractères terminé par son point. Relevé par la CI le
      // 5 novembre 2026, sur un paragraphe de `transparence.html`.
      const ponctuation = Math.max(
        reste.lastIndexOf(". ", LONGUEUR_MAX_SEGMENT - 1),
        reste.lastIndexOf("? ", LONGUEUR_MAX_SEGMENT - 1),
        reste.lastIndexOf("! ", LONGUEUR_MAX_SEGMENT - 1),
        reste.lastIndexOf("; ", LONGUEUR_MAX_SEGMENT - 1),
      );
      if (ponctuation > LONGUEUR_MAX_SEGMENT / 3) coupe = ponctuation + 1;
      if (coupe <= 0) coupe = LONGUEUR_MAX_SEGMENT - 1;
      // Une coupe tombe le plus souvent sur une espace, donc au milieu d'une
      // phrase : le morceau se terminait sur un mot nu. Mesuré le 24 octobre
      // 2026 sur les 98 pages du site : 41 segments sur 5 485 finissaient sans
      // ponctuation. Un moteur de synthèse enchaîne alors le morceau suivant
      // comme un mot de plus, sans respiration. La virgule dit la continuation
      // sans inventer une phrase qui n'existe pas ; un point, lui, couperait
      // le propos en deux.
      let morceau = reste.slice(0, coupe).trim();
      reste = reste.slice(coupe).trim();
      if (reste && !/[.!?…:;»),]$/.test(morceau)) {
        // La virgule compte dans la limite : si le morceau l'atteint déjà, le
        // dernier mot repasse au morceau suivant plutôt que de dépasser la
        // longueur qu'un moteur interrompt en pleine phrase.
        if (morceau.length >= LONGUEUR_MAX_SEGMENT) {
          const espace = morceau.lastIndexOf(" ");
          if (espace > LONGUEUR_MAX_SEGMENT / 3) {
            reste = `${morceau.slice(espace).trim()} ${reste}`;
            morceau = morceau.slice(0, espace).trimEnd();
          }
        }
        morceau += ",";
      }
      segments.push(morceau);
    }
    if (reste) segments.push(reste);
    return segments;
  };

  // Un bloc qui ne finit pas par une ponctuation s'entendrait collé au suivant.
  const ponctuer = (texte) => (/[.!?…:;»)]$/.test(texte) ? texte : `${texte}.`);

  // La langue se lit sur l'élément ou son plus proche ancêtre : une réplique
  // anglaise des Mondes porte `lang="en"` et doit être prononcée en anglais.
  const langueDe = (element) => {
    const porteur = element.closest("[lang]");
    return (porteur && porteur.getAttribute("lang")) || document.documentElement.lang || "fr";
  };

  // `innerText` plutôt que `textContent` : il rend les sauts de ligne et les
  // espaces de la mise en page, sans quoi deux phrases séparées par un élément
  // mis en bloc s'entendraient collées (« librement.Les Escales »).
  const texteLisible = (element) => {
    const brut = typeof element.innerText === "string" ? element.innerText : element.textContent;
    return normaliserTexte(brut);
  };

  // Quatre façons d'être invisible, mesurées dans Chromium le 24 octobre 2026 :
  //   display: none        → texte lisible, boîte vide ;
  //   visibility: hidden   → boîte non vide, texte vide ;
  //   <details> refermé    → boîte non vide, texte vide ;
  //   aria-hidden="true"   → visible pour l'œil, à écarter à la main.
  // Une seule de ces mesures ne suffit donc pas : `checkVisibility` tranche les
  // trois cas visuels d'un coup, `getClientRects` et `innerText` restent en
  // secours pour les moteurs qui ne l'ont pas.
  const estAffiche = (element) => {
    if (typeof element.checkVisibility === "function"
      && !element.checkVisibility({ checkVisibilityCSS: true, contentVisibilityAuto: true })) {
      return false;
    }
    if (!element.getClientRects().length) return false;
    return normaliserTexte(texteLisible(element)).length > 0;
  };

  const blocsLisibles = () => {
    const racine = document.querySelector("main") || document.body;
    return Array.from(racine.querySelectorAll(SELECTEUR_LECTURE))
      .filter((element) => {
        if (!estAffiche(element)) return false;
        if (element.closest("[aria-hidden='true'], .visually-hidden, script, style, nav, footer")) return false;
        // Un bloc qui en contient d'autres est écarté : sinon son texte serait lu
        // deux fois (une liste qui contient des paragraphes, par exemple).
        return !element.querySelector(SELECTEUR_LECTURE);
      });
  };

  const vitesseEnregistree = () => {
    const valeur = Number(readPreference(CLE_VITESSE));
    return VITESSES.includes(valeur) ? valeur : 1;
  };

  const construireLectureVocale = () => {
    const bloc = document.createElement("div");
    bloc.className = "read-aloud";
    bloc.dataset.readAloud = "";
    if (!syntheseVocaleDisponible) {
      // Sans voix de synthèse, la commande serait un bouton mort : on n'affiche
      // rien plutôt que de promettre une lecture impossible sur cet appareil.
      return null;
    }

    const titre = document.createElement("p");
    titre.className = "read-aloud-title";
    const titreFort = document.createElement("strong");
    titreFort.textContent = "Écouter la page";
    titre.append(titreFort);

    const commandes = document.createElement("div");
    commandes.className = "read-aloud-controls";
    const boutonLecture = document.createElement("button");
    boutonLecture.type = "button";
    boutonLecture.className = "display-control display-control-wide";
    boutonLecture.dataset.readAloudToggle = "";
    boutonLecture.textContent = "Lire à voix haute";
    const boutonPause = document.createElement("button");
    boutonPause.type = "button";
    boutonPause.className = "display-control";
    boutonPause.dataset.readAloudPause = "";
    boutonPause.textContent = "Pause";
    boutonPause.setAttribute("aria-pressed", "false");
    boutonPause.hidden = true;

    // « Reculer » relit le passage précédent : c'est le geste qu'on fait quand
    // on a perdu le fil, et il vaut mieux que recommencer depuis le début.
    const boutonReculer = document.createElement("button");
    boutonReculer.type = "button";
    boutonReculer.className = "display-control";
    boutonReculer.dataset.readAloudBack = "";
    boutonReculer.textContent = "Reculer";
    boutonReculer.setAttribute("aria-label", "Reculer au passage précédent");
    boutonReculer.hidden = true;

    const ligneVitesse = document.createElement("label");
    ligneVitesse.className = "read-aloud-speed";
    const etiquetteVitesse = document.createElement("span");
    etiquetteVitesse.textContent = "Vitesse";
    const choixVitesse = document.createElement("select");
    choixVitesse.dataset.readAloudSpeed = "";
    choixVitesse.setAttribute("aria-label", "Vitesse de lecture");
    const libellesVitesse = { 0.75: "Lente", 1: "Normale", 1.25: "Rapide", 1.5: "Très rapide" };
    VITESSES.forEach((valeur) => {
      const option = document.createElement("option");
      option.value = String(valeur);
      option.textContent = libellesVitesse[valeur];
      choixVitesse.append(option);
    });
    choixVitesse.value = String(vitesseEnregistree());
    ligneVitesse.append(etiquetteVitesse, choixVitesse);

    commandes.append(boutonLecture, boutonPause, boutonReculer, ligneVitesse);

    const etat = document.createElement("p");
    etat.className = "read-aloud-status";
    etat.dataset.readAloudStatus = "";
    etat.setAttribute("role", "status");
    etat.setAttribute("aria-live", "polite");

    const note = document.createElement("p");
    note.className = "read-aloud-note";
    note.textContent = "La voix est celle de l’appareil : elle peut varier, manquer ou mal prononcer un mot. Rien n’est envoyé à un service distant. La vitesse choisie reste sur cet appareil. Cette lecture ne remplace pas un lecteur d’écran.";

    let enLecture = false;
    let enPause = false;
    let file = [];
    let index = 0;
    let blocMarque = null;
    let vitesse = vitesseEnregistree();
    // Chaque énonciation porte le numéro de sa génération. Une énonciation
    // annulée peut rappeler `onend` ou `onerror` après coup : sans ce jeton,
    // « Reculer » ou un changement de vitesse relancerait deux lectures.
    let generation = 0;

    const annoncer = (message) => {
      if (etat.textContent === message) {
        etat.textContent = "";
      }
      etat.textContent = message;
    };

    const demarquer = () => {
      if (blocMarque) blocMarque.classList.remove("lecture-en-cours");
      blocMarque = null;
    };

    const marquer = (element) => {
      demarquer();
      if (!element) return;
      blocMarque = element;
      element.classList.add("lecture-en-cours");
      if (typeof element.scrollIntoView !== "function") return;
      const cadre = element.getBoundingClientRect();
      const mouvementReduit = typeof window.matchMedia === "function"
        && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
      // On ne fait défiler que si le bloc lu n'est pas déjà visible : suivre la
      // lecture sans imposer un défilement à chaque phrase.
      if (cadre.top < 0 || cadre.bottom > window.innerHeight) {
        element.scrollIntoView({ block: "center", behavior: mouvementReduit ? "auto" : "smooth" });
      }
    };

    const arreter = (motif) => {
      enLecture = false;
      enPause = false;
      file = [];
      index = 0;
      try {
        window.speechSynthesis.cancel();
      } catch (erreur) {
        // Un moteur absent ou bloqué ne doit pas laisser la commande bloquée.
      }
      generation += 1;
      demarquer();
      boutonLecture.textContent = "Lire à voix haute";
      boutonLecture.removeAttribute("aria-label");
      boutonPause.hidden = true;
      boutonPause.textContent = "Pause";
      boutonPause.setAttribute("aria-pressed", "false");
      boutonReculer.hidden = true;
      if (motif === "erreur") {
        annoncer("La lecture s’est arrêtée : la voix de cet appareil n’a pas répondu.");
      } else if (motif === "fin") {
        annoncer("Lecture terminée.");
      } else {
        annoncer("Lecture arrêtée.");
      }
    };

    const lire = () => {
      if (!enLecture) return;
      if (index >= file.length) {
        arreter("fin");
        return;
      }
      const segment = file[index];
      index += 1;
      marquer(segment.bloc);
      const jeton = generation;
      const enonce = new window.SpeechSynthesisUtterance(segment.texte);
      enonce.lang = segment.langue;
      enonce.rate = vitesse;
      enonce.onend = () => {
        if (jeton !== generation) return;
        if (enLecture && !enPause) lire();
      };
      enonce.onerror = (evenement) => {
        if (jeton !== generation) return;
        // Un arrêt volontaire interrompt l'énonciation en cours : Chromium le
        // signale comme une erreur. Ce n'est pas une panne, il ne faut pas
        // l'annoncer comme telle.
        const cause = evenement && evenement.error;
        if (!enLecture || cause === "interrupted" || cause === "canceled") return;
        arreter("erreur");
      };
      window.speechSynthesis.speak(enonce);
    };

    const demarrer = () => {
      const blocs = blocsLisibles();
      file = [];
      blocs.forEach((element) => {
        decouperSegment(ponctuer(texteLisible(element)))
          .forEach((texte) => file.push({ texte, bloc: element, langue: langueDe(element) }));
      });
      if (!file.length) {
        annoncer("Aucun texte à lire sur cette page.");
        return;
      }
      try {
        window.speechSynthesis.cancel();
      } catch (erreur) {
        // Rien à annuler : le moteur repart de zéro.
      }
      generation += 1;
      enLecture = true;
      enPause = false;
      index = 0;
      // Libellé court : « Arrêter la lecture » et « Reprendre » côte à côte
      // débordaient du panneau sous 360 px. Le nom accessible reste complet.
      boutonLecture.textContent = "Arrêter";
      // Le nom accessible contient le texte visible, comme l'exige la règle
      // `label-content-name-mismatch` d'axe.
      boutonLecture.setAttribute("aria-label", "Arrêter la lecture à voix haute");
      boutonPause.hidden = false;
      boutonPause.textContent = "Pause";
      boutonPause.setAttribute("aria-pressed", "false");
      boutonReculer.hidden = false;
      annoncer("Lecture à voix haute commencée.");
      // `cancel()` puis `speak()` dans le même tour est parfois ignoré par
      // Chromium : la première énonciation part au tour suivant.
      setTimeout(() => {
        if (enLecture && !enPause) lire();
      }, 0);
    };

    boutonLecture.addEventListener("click", () => {
      if (enLecture) {
        arreter("arret");
      } else {
        demarrer();
      }
    });

    const relancer = () => {
      generation += 1;
      enPause = false;
      boutonPause.textContent = "Pause";
      boutonPause.setAttribute("aria-pressed", "false");
      try {
        window.speechSynthesis.cancel();
      } catch (erreur) {
        // Un moteur absent ne doit pas bloquer la relance.
      }
      // Même précaution qu'au démarrage : `cancel()` puis `speak()` dans le
      // même tour peut être perdu.
      setTimeout(() => {
        if (enLecture && !enPause) lire();
      }, 0);
    };

    boutonReculer.addEventListener("click", () => {
      if (!enLecture) return;
      // `index` désigne le segment suivant : le segment courant est `index - 1`
      // et le précédent `index - 2`. Au tout début, il n'y a rien à relire.
      if (index <= 1) {
        annoncer("Début de la page.");
        return;
      }
      index -= 2;
      relancer();
      annoncer("Passage précédent.");
    });

    choixVitesse.addEventListener("change", () => {
      const valeur = Number(choixVitesse.value);
      if (!VITESSES.includes(valeur)) return;
      vitesse = valeur;
      savePreference(CLE_VITESSE, String(valeur));
      const libelle = libellesVitesse[valeur];
      if (!enLecture) {
        annoncer(`Vitesse de lecture : ${libelle.toLowerCase()}.`);
        return;
      }
      // Le débit d'une énonciation ne se modifie pas en cours de route : on
      // reprend le passage courant à la nouvelle vitesse.
      index = Math.max(0, index - 1);
      relancer();
      annoncer(`Vitesse de lecture : ${libelle.toLowerCase()}.`);
    });

    boutonPause.addEventListener("click", () => {
      if (!enLecture) return;
      if (enPause) {
        try {
          window.speechSynthesis.resume();
        } catch (erreur) {
          // Le moteur reprend au prochain segment de toute façon.
        }
        enPause = false;
        boutonPause.textContent = "Pause";
        boutonPause.setAttribute("aria-pressed", "false");
        annoncer("Lecture reprise.");
        // Si le moteur a terminé le segment pendant la pause, la file doit
        // repartir ; sinon, `resume()` suffit et relancer lirait deux fois.
        if (!window.speechSynthesis.speaking && !window.speechSynthesis.pending) lire();
      } else {
        try {
          window.speechSynthesis.pause();
        } catch (erreur) {
          // Sans pause possible, le bouton reste sans effet visible.
        }
        enPause = true;
        boutonPause.textContent = "Reprendre";
        boutonPause.setAttribute("aria-pressed", "true");
        annoncer("Lecture en pause.");
      }
    });

    // Quitter la page ou la mettre en arrière-plan coupe la voix : une lecture
    // qui continue sur une autre page serait impossible à arrêter.
    window.addEventListener("pagehide", () => {
      if (enLecture) arreter("arret");
    });

    bloc.append(titre, commandes, etat, note);
    return bloc;
  };

  if (settings) {
    settings.hidden = false;
    textDecrease?.addEventListener("click", () => {
      const index = textLevels.indexOf(textLevel);
      applyTextLevel(textLevels[Math.max(0, index - 1)]);
      savePreference(keys.text, String(textLevel));
    });
    textIncrease?.addEventListener("click", () => {
      const index = textLevels.indexOf(textLevel);
      applyTextLevel(textLevels[Math.min(textLevels.length - 1, index + 1)]);
      savePreference(keys.text, String(textLevel));
    });
    contrastToggle?.addEventListener("click", () => {
      applyContrast(!contrastEnabled);
      savePreference(keys.contrast, contrastEnabled ? "oui" : "non");
    });
    spacingToggle?.addEventListener("click", () => {
      applySpacing(!spacingEnabled);
      savePreference(keys.spacing, spacingEnabled ? "oui" : "non");
    });

  }

  document.addEventListener("click", (event) => {
    if (settings && !settings.contains(event.target)) settings.open = false;
    if (layoutSettings && !layoutSettings.contains(event.target)) layoutSettings.open = false;
    if (apparenceSettings && !apparenceSettings.contains(event.target)) apparenceSettings.open = false;
    if (personnalisation && !personnalisation.contains(event.target)) personnalisation.open = false;
  });

  // L’iframe locale et les pages M.R.S.C partagent ces réglages sur le même domaine.
  window.addEventListener("storage", (event) => {
    if (
      event.key === null ||
      Object.values(keys).includes(event.key) ||
      event.key === ANCIENNE_CLE ||
      event.key === "mrsc-texte-agrandi"
    ) {
      loadPreferences();
    }
    // Un autre onglet a réduit ou agrandi l'en-tête : cette page suit, au lieu
    // de garder une image qui contredit la préférence lue au prochain clic.
    if (event.key === null || event.key === CLE_ENTETE_COMPACTE) {
      preferenceCompacte = lirePreferenceEnteteCompacte();
      appliquerPreferenceEntete?.();
    }
  });

  const toggle = document.querySelector("[data-menu-toggle]");
  const navigation = document.querySelector("[data-primary-navigation]");
  const header = document.querySelector(".site-header");
  const headerCompactToggle = document.querySelector("[data-header-compact-toggle]");

  if (toggle && navigation) {
    root.classList.add("has-js");

    // --- Placement mesuré des panneaux flottants ---------------------------
    // Personne ne garde plus une fenêtre à une taille fixe : on la redimensionne,
    // on la coupe en deux, on zoome, on passe du portrait au paysage, et sur
    // téléphone la barre d'adresse change la hauteur utile. Un point de rupture
    // ne connaît aucun de ces états, et deux règles successives l'ont prouvé :
    // celle du 28 octobre 2026 (`min-width: 761px and min-height: 561px`) puis
    // sa correction du 30 (ajout de `min-width: 921px`) laissaient encore
    // passer un format — 980 × 4xx, large et bas — où le panneau ressortait par
    // la gauche, libellés rognés. Empiler des points de rupture, c'est courir
    // après les formats ; mesurer, c'est n'en avoir aucun à courir après.
    //
    // Un panneau est donc placé **à la mesure**, à chaque ouverture et à chaque
    // changement de fenêtre :
    //   1. la largeur voulue par la feuille de style est relue, puis bornée à
    //      la fenêtre moins deux marges ;
    //   2. son bord droit est aligné sur celui du bouton ; si cela le fait
    //      sortir par la gauche, c'est le bord gauche qui est aligné ; puis sa
    //      position est bornée à la fenêtre — c'est cette borne qui remplace
    //      les points de rupture ;
    //   3. sa hauteur descend sous l'en-tête, bornée pour laisser au moins
    //      160 px de panneau visible, avec défilement interne au-delà.
    //
    // Depuis le 5 novembre 2026, **les deux panneaux du site passent par ce même
    // calcul** : « Personnalisation » et le menu. Le menu était le dernier à
    // s'ouvrir par une cascade de points de rupture — pleine largeur sous
    // 1260 px, gouttières négatives sous 760 et 520, plafond de hauteur dans une
    // troisième règle. Il se déploie désormais comme l'autre : ancré à son
    // bouton, borné aux deux marges, défilable, avec la même animation. Une
    // seule différence reste voulue : sa couleur, qui est celle de la barre de
    // navigation.
    //
    // Le positionnement reste `absolute` dans le parent positionné du panneau
    // (`.customize-settings` ou `.nav-inner`) : les coordonnées calculées sont
    // donc ramenées à ce parent. On évite ainsi `position: fixed` dans l'en-tête,
    // dont le `backdrop-filter` fait de lui le référentiel des descendants
    // fixes — un piège qui rendrait les coordonnées fausses sans que rien ne le
    // signale.
    const MARGE_PANNEAU = 8;
    const HAUTEUR_MINIMALE_PANNEAU = 160;

    function placerPanneauFlottant(panneau, bouton) {
      if (!panneau || !bouton) return false;
      // Marqueur lisible par les essais : sans lui, un placement qui ne
      // s'exécute pas ressemble à un placement juste. C'est exactement ce qui
      // s'est produit le 30 octobre 2026 — le panneau gardait la géométrie de
      // la feuille de style, et rien ne le disait.
      panneau.dataset.placement = "mesure";
      const vue = window.visualViewport;
      const largeurFenetre = Math.round(vue ? vue.width : document.documentElement.clientWidth);
      const hauteurFenetre = Math.round(vue ? vue.height : window.innerHeight);
      // Largeur voulue : celle de la feuille de style, relue à chaque fois
      // plutôt que devinée — une largeur fixe ici contredirait le CSS.
      panneau.style.width = "";
      const voulue = panneau.getBoundingClientRect().width || 352;
      const largeur = Math.round(
        Math.max(160, Math.min(voulue, largeurFenetre - 2 * MARGE_PANNEAU))
      );
      const cadreBouton = bouton.getBoundingClientRect();
      const cadreEntete = header ? header.getBoundingClientRect() : cadreBouton;
      const aligneADroite = cadreBouton.right - largeur;
      const gauche = Math.max(
        MARGE_PANNEAU,
        Math.min(
          aligneADroite < MARGE_PANNEAU ? cadreBouton.left : aligneADroite,
          largeurFenetre - largeur - MARGE_PANNEAU
        )
      );
      // La borne de hauteur réserve la marge du bas : un en-tête de 180 px dans
      // une fenêtre de 320 laissait sinon 152 px de panneau pour 160 demandés,
      // et le panneau dépassait de 8 px. Trouvé par `test_placement_panneau.mjs`
      // avant tout navigateur.
      const haut = Math.max(
        MARGE_PANNEAU,
        Math.min(
          cadreEntete.bottom + MARGE_PANNEAU,
          hauteurFenetre - HAUTEUR_MINIMALE_PANNEAU - MARGE_PANNEAU
        )
      );
      const hauteurDisponible = Math.max(
        HAUTEUR_MINIMALE_PANNEAU,
        hauteurFenetre - haut - MARGE_PANNEAU
      );
      // Les coordonnées sont relatives au parent positionné du panneau, pas au
      // bouton : c'est lui qui sert de référentiel à `left` et `top`. Le panneau
      // du menu vit dans `.nav-inner`, celui de « Personnalisation » dans son
      // propre `<details>` ; les deux n'ont pas le même parent.
      const parent = panneau.offsetParent;
      const cadreParent = parent ? parent.getBoundingClientRect() : { left: 0, top: 0 };
      panneau.style.right = "auto";
      panneau.style.width = `${largeur}px`;
      panneau.style.left = `${Math.round(gauche - cadreParent.left)}px`;
      panneau.style.top = `${Math.round(haut - cadreParent.top)}px`;
      panneau.style.maxHeight = `${Math.round(hauteurDisponible)}px`;
      return true;
    }

    // Fermer un panneau, c'est aussi lui rendre ses coordonnées : laissées en
    // place, elles s'appliqueraient telles quelles à la réouverture, dans un
    // format qui a pu changer entre-temps — une image du panneau au mauvais
    // endroit, puis son replacement. Deux fois la même liste écrite à deux
    // endroits finirait par diverger : elle est ici, une seule fois.
    const PROPRIETES_PLACEES = ["left", "top", "right", "width", "max-height"];
    function rendreCoordonnees(panneau) {
      if (!panneau) return;
      PROPRIETES_PLACEES.forEach((propriete) => {
        panneau.style.removeProperty(propriete);
      });
      delete panneau.dataset.placement;
    }

    function placerPanneauPersonnalisation() {
      if (!personnalisation || !panneauPersonnalisation || !personnalisation.open) return;
      placerPanneauFlottant(panneauPersonnalisation, personnalisation.querySelector("summary"));
    }

    // Le panneau du menu n'est pas un `<details>` : sa bascule est un bouton et
    // son ouverture une classe. Le placement, lui, ne le sait pas.
    function placerPanneauMenu() {
      if (!navigation || !navigation.classList.contains("is-open")) return;
      placerPanneauFlottant(navigation, toggle);
    }

    function placerPanneauxFlottants() {
      placerPanneauPersonnalisation();
      placerPanneauMenu();
    }

    // La feuille de style a besoin de savoir si la navigation est repliée
    // derrière « Menu » : sous 1260 px, et aussi au-delà à 115 et 130 % de
    // taille de texte. Ces deux conditions vivent dans le CSS, sous forme de
    // paliers et de classes ; les réécrire ici en JavaScript serait une seconde
    // vérité. On demande donc au bouton s'il est affiché — c'est exactement la
    // question à laquelle la feuille a déjà répondu — et on publie la réponse
    // sous forme de classe.
    function synchroniserMenuFlottant() {
      const flottant = window.getComputedStyle(toggle).display !== "none";
      root.classList.toggle("menu-flottant", flottant);
      // Un panneau ouvert qui n'a plus de bouton — fenêtre élargie, texte ramené
      // à 100 % — n'a plus rien à montrer : il se referme, et rend au passage
      // les coordonnées qu'il tenait du calcul, sans quoi elles
      // s'appliqueraient à la navigation en ligne.
      if (!flottant && navigation.classList.contains("is-open")) {
        toggle.setAttribute("aria-expanded", "false");
        navigation.classList.remove("is-open");
        rendreCoordonnees(navigation);
      }
      return flottant;
    }

    // Ce que fait un redimensionnement : d'abord la classe, puis le placement.
    // L'ordre compte — placer avant de savoir si le panneau est flottant
    // donnerait des coordonnées que la feuille n'utilise pas encore.
    function ajusterPanneauxFlottants() {
      synchroniserMenuFlottant();
      placerPanneauxFlottants();
    }

    // La hauteur de l'en-tête dépend du logo, du cran de texte et du mode
    // compact : les deux panneaux s'y accrochent pour ne jamais dépasser le bas
    // de l'écran, même en paysage ou en texte très agrandi.
    if (header && typeof ResizeObserver === "function") {
      const publierHauteurEntete = () => {
        root.style.setProperty("--hauteur-entete", `${Math.round(header.getBoundingClientRect().height)}px`);
        ajusterPanneauxFlottants();
      };
      publierHauteurEntete();
      new ResizeObserver(publierHauteurEntete).observe(header);
    }

    // Le placement suit tous les changements qui déplacent un bouton ou
    // réduisent la place : fenêtre redimensionnée, rotation, barre d'adresse du
    // téléphone, clavier virtuel, changement de taille de texte ou d'en-tête.
    // Rien de tout cela n'est un format nommé. Le défilement de la fenêtre
    // visuelle ne déplace pas le bouton : il replace, sans resynchroniser.
    window.addEventListener("resize", ajusterPanneauxFlottants, { passive: true });
    window.addEventListener("orientationchange", ajusterPanneauxFlottants);
    if (window.visualViewport) {
      window.visualViewport.addEventListener("resize", ajusterPanneauxFlottants, { passive: true });
      window.visualViewport.addEventListener("scroll", placerPanneauxFlottants, { passive: true });
    }
    if (document.readyState !== "complete") {
      window.addEventListener("load", ajusterPanneauxFlottants, { once: true });
    }
    apresChangementReglages.push(ajusterPanneauxFlottants);
    ajusterPanneauxFlottants();

    // Un seul bouton « Personnalisation » regroupe les commandes de préférence :
    // taille de l'en-tête, parcours, affichage et présentation. L'en-tête ne garde
    // ainsi que « Menu » et « Personnalisation ». Le déplacement se fait ici plutôt
    // que dans les 98 pages statiques : une seule source à tenir.
    const outilsEntete = header ? header.querySelector(".header-compact-tools") : null;
    if (outilsEntete && headerCompactToggle && settings) {
      personnalisation = document.createElement("details");
      personnalisation.className = "customize-settings";
      personnalisation.dataset.customizeSettings = "";

      const resume = document.createElement("summary");
      resume.className = "customize-settings-summary";
      resume.title = "Personnalisation : taille de l’en-tête, parcours, affichage et présentation";
      resume.textContent = "Personnalisation";
      const chevronPersonnalisation = document.createElement("span");
      chevronPersonnalisation.className = "customize-settings-chevron";
      chevronPersonnalisation.setAttribute("aria-hidden", "true");
      chevronPersonnalisation.textContent = "⌄";
      resume.append(" ", chevronPersonnalisation);

      panneauPersonnalisation = document.createElement("div");
      panneauPersonnalisation.className = "customize-settings-panel";
      panneauPersonnalisation.id = "site-customize-panel";
      resume.setAttribute("aria-controls", panneauPersonnalisation.id);

      personnalisation.append(resume, panneauPersonnalisation);
      // Ordre voulu : agrandir/réduire, parcours (inséré ensuite par
      // navigation-parcours.js devant l'affichage), affichage, présentation.
      const lectureVocale = construireLectureVocale();
      // L'écoute vient en dernier : elle ne fait pas partie des réglages de
      // présentation, et l'intercaler coupait le groupe en deux.
      [headerCompactToggle, settings, apparenceSettings, layoutSettings, lectureVocale].forEach((element) => {
        if (element) panneauPersonnalisation.append(element);
      });
      outilsEntete.append(personnalisation);

      // Le placement suit tous les changements qui déplacent le bouton ou
      // réduisent la place : ouverture du panneau, fenêtre redimensionnée,
      // rotation, barre d'adresse du téléphone, clavier virtuel, changement de
      // taille de texte ou d'en-tête. Rien de tout cela n'est un format nommé.
      personnalisation.addEventListener("toggle", placerPanneauPersonnalisation);
      // Chromium restaure l'état ouvert d'un `<details>` au rechargement, et le
      // fait **après** l'événement `load` : ni `toggle` ni `load` ne passent
      // alors. Observer l'attribut `open` attrape cette restauration comme un
      // clic de l'utilisateur — mesuré le 30 octobre 2026 par l'essai à
      // 800 × 500, panneau ouvert avec un style en ligne nul.
      new MutationObserver(placerPanneauPersonnalisation)
        .observe(personnalisation, { attributeFilter: ["open"] });
      // Les écoutes de fenêtre, de fenêtre visuelle et d'en-tête sont posées
      // une seule fois plus haut, pour les deux panneaux : un panneau qui
      // n'écoute pas les mêmes changements se replace moins bien que l'autre,
      // et la différence ne se voit qu'au moment du défaut.
      //
      // Le navigateur peut aussi restaurer `<details open>` au chargement
      // (rechargement, retour arrière) : le panneau est alors ouvert sans
      // qu'aucun événement `toggle` n'ait eu lieu. Constaté le 30 octobre 2026
      // par l'essai à 667 × 375 : panneau ouvert, style en ligne nul. On place
      // donc aussi ici, tout de suite.
      placerPanneauPersonnalisation();
    }

    const closeMenu = () => {
      toggle.setAttribute("aria-expanded", "false");
      navigation.classList.remove("is-open");
      rendreCoordonnees(navigation);
    };

    // Ouverture : les mêmes règles que « Personnalisation ». Un seul panneau
    // flottant à la fois — fermer l'autre évite deux panneaux superposés, dont
    // le second masque le premier sans qu'on sache lequel répond. Et le panneau
    // est placé dans le même geste : attendre le prochain redimensionnement
    // laisserait la géométrie de repli de la feuille de style.
    const openMenu = () => {
      toggle.setAttribute("aria-expanded", "true");
      navigation.classList.add("is-open");
      if (personnalisation && personnalisation.open) personnalisation.open = false;
      if (settings) settings.open = false;
      if (apparenceSettings) apparenceSettings.open = false;
      if (layoutSettings) layoutSettings.open = false;
      const journeySettings = document.querySelector("[data-site-journey]");
      if (journeySettings) journeySettings.open = false;
      // La synchronisation passe avant le placement : ouvrir dans un format où
      // le panneau n'est pas encore flottant poserait des coordonnées que la
      // feuille de style n'applique pas.
      ajusterPanneauxFlottants();
    };

    if (header && headerCompactToggle) {
      const compactViewport = typeof window.matchMedia === "function"
        ? window.matchMedia(
          "(max-width: 760px), (orientation: landscape) and (max-height: 560px) and (max-width: 920px)"
        )
        : null;
      const narrowViewport = typeof window.matchMedia === "function"
        ? window.matchMedia("(max-width: 520px)")
        : null;
      const headerDetails = [
        header.querySelector("#site-header-status"),
        header.querySelector("#site-header-identity"),
      ];

      // Une préférence explicite gagne sur le format de fenêtre : sinon un
      // redimensionnement, une rotation ou la barre d'adresse d'un téléphone
      // referaient « sauter » le mode réduit sans que la personne ait rien
      // demandé. Sans préférence, le format reste le seul décideur, comme avant.
      const etatCompactVoulu = () => preferenceCompacte ?? Boolean(compactViewport?.matches);

      const setHeaderCompact = (compact) => {
        const label = compact ? "Agrandir" : "Réduire";
        const expanded = String(!compact);
        if (
          header.classList.contains("is-compact") === compact
          && root.classList.contains("entete-compacte") === compact
          && headerCompactToggle.getAttribute("aria-expanded") === expanded
          && headerCompactToggle.textContent === label
        ) return;

        const focusWouldBeHidden = compact
          && headerDetails.some((element) => element?.contains(document.activeElement));
        header.classList.toggle("is-compact", compact);
        root.classList.toggle("entete-compacte", compact);
        headerCompactToggle.setAttribute("aria-expanded", expanded);
        const description = compact
          ? "Agrandir l’en-tête pour afficher le logo et les informations du M.R.S.C."
          : "Réduire l’en-tête pour libérer de la place à l’écran.";
        headerCompactToggle.textContent = label;
        headerCompactToggle.setAttribute("aria-label", description);
        headerCompactToggle.title = description;
        if (focusWouldBeHidden) headerCompactToggle.focus();
        // L'en-tête compact ne change pas seulement de hauteur : il range ses
        // deux commandes au début de la barre, donc le bouton se déplace de
        // plusieurs centaines de pixels. Le panneau doit être replacé ici,
        // explicitement — s'en remettre au seul ResizeObserver laissait le
        // panneau aux coordonnées de l'en-tête agrandi (mesuré le 30 octobre
        // 2026 : left = −203 px pour un bouton désormais à 169 px).
        ajusterPanneauxFlottants();
      };

      headerCompactToggle.hidden = false;
      setHeaderCompact(etatCompactVoulu());
      appliquerPreferenceEntete = () => setHeaderCompact(etatCompactVoulu());
      headerCompactToggle.addEventListener("click", () => {
        closeMenu();
        // Ne pas fermer « Personnalisation » : le bouton est dans son panneau, et
        // le refermer rendrait « Réduire » inatteignable une fois l'en-tête
        // agrandi.
        if (settings) settings.open = false;
        if (apparenceSettings) apparenceSettings.open = false;
        if (layoutSettings) layoutSettings.open = false;
        const journeySettings = document.querySelector("[data-site-journey]");
        if (journeySettings) journeySettings.open = false;
        const compact = !header.classList.contains("is-compact");
        preferenceCompacte = compact;
        savePreference(CLE_ENTETE_COMPACTE, compact ? "oui" : "non");
        setHeaderCompact(compact);
      });

      if (compactViewport) {
        const onViewportModeChange = () => {
          closeMenu();
          setHeaderCompact(etatCompactVoulu());
        };
        if (typeof compactViewport.addEventListener === "function") {
          compactViewport.addEventListener("change", onViewportModeChange);
        } else {
          compactViewport.addListener?.(onViewportModeChange);
        }
      }

      // Sous 520 px, une réduction de fenêtre rétablit le format compact après
      // un agrandissement manuel. Une fois compact, ne pas réécrire son libellé
      // à chaque pixel de redimensionnement. Ce rattrapage ne vaut que sans
      // choix explicite : une personne qui a demandé l'en-tête agrandi ne doit
      // pas le voir refermer sous ses doigts au premier pixel gagné.
      if (narrowViewport) {
        let previousViewportWidth = window.innerWidth;
        window.addEventListener("resize", () => {
          const widthIsShrinking = window.innerWidth < previousViewportWidth;
          previousViewportWidth = window.innerWidth;
          if (!widthIsShrinking || !narrowViewport.matches || header.classList.contains("is-compact")) return;
          if (preferenceCompacte !== null) return;
          closeMenu();
          setHeaderCompact(true);
        });
      }
    }

    toggle.addEventListener("click", () => {
      const isOpen = toggle.getAttribute("aria-expanded") === "true";
      if (isOpen) closeMenu();
      else openMenu();
    });

    // Fermeture au clic extérieur, comme « Personnalisation ». Le menu restait
    // ouvert quand on cliquait ailleurs dans la page : il fallait retrouver le
    // bouton pour le refermer, alors que l'autre panneau se fermait seul.
    document.addEventListener("click", (event) => {
      if (!navigation.classList.contains("is-open")) return;
      if (toggle.contains(event.target) || navigation.contains(event.target)) return;
      closeMenu();
    });

    navigation.addEventListener("click", (event) => {
      if (event.target.closest("a")) closeMenu();
    });

    // Échap referme d'abord le réglage ouvert dans « Personnalisation » : le
    // panneau ne doit pas disparaître sous les doigts de qui ferme un seul
    // réglage. Le drapeau est posé en phase de capture, donc avant que les
    // réglages ne se referment eux-mêmes et ne vident `details[open]`.
    document.addEventListener("keydown", (event) => {
      if (event.key !== "Escape" || !personnalisation?.open) return;
      if (personnalisation.querySelector(".customize-settings-panel details[open]")) {
        event.mrscEchapImbrique = true;
      }
    }, true);

    document.addEventListener("keydown", (event) => {
      if (event.key !== "Escape") return;
      const menuWasOpen = navigation.classList.contains("is-open");
      closeMenu();
      if (menuWasOpen) toggle.focus();
      if (personnalisation?.open && !event.mrscEchapImbrique) {
        const focusDansPersonnalisation = personnalisation.contains(document.activeElement);
        personnalisation.open = false;
        if (focusDansPersonnalisation) personnalisation.querySelector("summary")?.focus();
      }
      if (settings?.open) {
        const focusInsideSettings = settings.contains(document.activeElement);
        settings.open = false;
        if (focusInsideSettings) settings.querySelector("summary")?.focus();
      }
      if (layoutSettings?.open) {
        const focusInsideLayoutSettings = layoutSettings.contains(document.activeElement);
        layoutSettings.open = false;
        if (focusInsideLayoutSettings) layoutSettings.querySelector("summary")?.focus();
      }
      if (apparenceSettings?.open) {
        const focusDansApparence = apparenceSettings.contains(document.activeElement);
        apparenceSettings.open = false;
        if (focusDansApparence) apparenceSettings.querySelector("summary")?.focus();
      }
    });
  }
})();

/* Simulateur macro-politique : quelle source afficher ?

   Le simulateur se développe en continu dans son propre dépôt. Trois sources
   sont possibles, par ordre de préférence :

   1. la *source distante* hébergée sur Vercel, si le site est servi par
      un hébergeur qui exécute du Python : `/api/verifier-source` l'a vérifiée
      côté serveur (page + API de calcul) et dit si elle est utilisable ;
   2. la *copie embarquée* du moteur dans ce dépôt, si sa propre API répond ;
   3. sinon (hébergement purement statique, GitHub Pages), l'avis
      « aperçu indisponible » prend la place du cadre, avec le lien vers la
      version en ligne.

   La vérification de la source distante se fait côté serveur, car le navigateur
   ne peut pas lire une réponse d'une autre origine : sans cette étape, on
   afficherait parfois une simple page de présentation en croyant au moteur. */
(() => {
  document.querySelectorAll("[data-simulateur-apercu]").forEach((cadre) => {
    const sourceLocale = cadre.getAttribute("data-src");
    const sourceDistante = cadre.getAttribute("data-source-distante");
    const iframe = cadre.querySelector("iframe");
    const avis = document.querySelector("[data-simulateur-avis]");
    const origine = document.querySelector("[data-simulateur-origine]");
    if (!sourceLocale || !iframe) return;

    const indisponible = (raison) => {
      cadre.classList.add("is-indisponible");
      if (avis) {
        avis.hidden = false;
        const detail = avis.querySelector("[data-simulateur-raison]");
        if (detail && raison) detail.textContent = raison;
      }
    };

    const afficher = (source, quoi) => {
      iframe.src = source;
      if (origine && quoi) origine.textContent = quoi;
    };

    const repond = async (url, methode) => {
      const reponse = await fetch(url, { method: methode, cache: "no-store" });
      if (!reponse.ok) throw new Error("HTTP " + reponse.status);
      return reponse;
    };

    const choisir = async () => {
      // 1. La version Vercel est-elle utilisable (vérifiée par le serveur) ?
      if (sourceDistante) {
        try {
          const reponse = await repond("/api/verifier-source", "GET");
          const etat = await reponse.json();
          if (etat && etat.disponible === true) {
            afficher(sourceDistante, "Source affichée : simulateur hébergé sur Vercel.");
            return;
          }
        } catch (erreur) {
          /* pas de fonction de vérification : hébergement statique, ou source absente */
        }
      }

      // 2. La copie embarquée du moteur répond-elle sur cette adresse ?
      try {
        await repond("/api/scenarios", "HEAD");
        afficher(sourceLocale, "Source affichée : copie embarquée du moteur.");
        return;
      } catch (erreur) {
        /* pas d'API locale non plus */
      }

      // 3. Ni l'une ni l'autre : on explique, avec les deux portes de sortie.
      indisponible("Aucune API de calcul disponible à cette adresse.");
    };

    // Repli : si la source affichée échoue en cours de route, on rebascule sur la copie locale.
    iframe.addEventListener("error", () => {
      if (iframe.src.indexOf(sourceLocale) !== -1) {
        indisponible("La copie embarquée du moteur n'a pas répondu.");
        return;
      }
      repond("/api/scenarios", "HEAD")
        .then(() => afficher(sourceLocale, "Repli : copie embarquée du moteur."))
        .catch(() => indisponible("Le simulateur n'a pas répondu."));
    });

    choisir();
  });

  /* Révision du moteur embarqué, affichée à côté du lien vers le dépôt. */
  const revision = document.querySelector("[data-simulateur-revision]");
  if (revision) {
    fetch("simulateur/PROVENANCE.json", { cache: "no-store" })
      .then((reponse) => (reponse.ok ? reponse.json() : null))
      .then((provenance) => {
        if (!provenance) return;
        const courte = provenance.revision_courte || "révision inconnue";
        const date = (provenance.copie_le || provenance.date_revision || "").slice(0, 10);
        revision.textContent = date ? `${courte} (copiée le ${date})` : courte;
      })
      .catch(() => undefined);
  }
})();

/* La carte Google est chargée seulement après une action explicite.
   Sans clic, aucun iframe ni requête vers le fournisseur de la carte n'est créé. */
(() => {
  document.querySelectorAll("[data-map-load]").forEach((button) => {
    const figure = button.closest("figure");
    const iframe = figure?.querySelector("iframe[data-map-src]");
    const status = figure?.querySelector("[data-map-status]");
    if (!iframe) return;

    button.addEventListener("click", () => {
      if (!iframe.src) iframe.src = iframe.dataset.mapSrc;
      iframe.hidden = false;
      button.hidden = true;
      if (status) {
        status.textContent = "La carte Google est chargée. Le fournisseur a été contacté et peut recevoir des données techniques de connexion. Pour ne pas conserver la carte dans cette page, actualisez-la.";
      }
    }, { once: true });
  });
})();

/* Partage facultatif de l’adresse publique, sans compte social imposé ni suivi. */
(() => {
  const button = document.querySelector("[data-share-site]");
  if (!button) return;

  const status = document.querySelector("[data-share-status]");
  const fallback = document.querySelector("[data-share-fallback]");
  const address = document.querySelector("[data-share-url]");
  const publicUrl = "https://thejmimiia-code.github.io/MRSC/";
  if (address) address.value = publicUrl;
  button.hidden = false;

  const announce = (message) => {
    if (!status) return;
    status.hidden = false;
    status.textContent = message;
  };

  const selectAddress = () => {
    if (fallback) fallback.hidden = false;
    if (address) {
      address.focus();
      address.select();
    }
    announce("L’adresse publique est sélectionnée. Copiez-la avec le clavier ou les commandes de votre appareil.");
  };

  button.addEventListener("click", async () => {
    if (typeof navigator.share === "function") {
      try {
        await navigator.share({
          title: "M.R.S.C — La force citoyenne",
          text: "Découvrir les ressources, les réflexions et les possibilités de participation du M.R.S.C.",
          url: publicUrl,
        });
        announce("Le menu de partage de votre appareil a été ouvert.");
        return;
      } catch (error) {
        if (error && error.name === "AbortError") {
          announce("Le partage a été annulé.");
          return;
        }
      }
    }

    try {
      if (!window.isSecureContext || !navigator.clipboard?.writeText) throw new Error("Copie indisponible");
      await navigator.clipboard.writeText(publicUrl);
      announce("L’adresse publique du site a été copiée.");
    } catch (error) {
      selectAddress();
    }
  });
})();

/* Chaque phrase de contenu commence en début de ligne, sur toutes les mises en page. */
(() => {
  // Seul le contenu principal est découpé : le pied de page porte des mentions
  // légales, qui se lisent d'un tenant et non phrase par phrase.
  const racines = [document.querySelector("main")].filter(Boolean);
  if (!racines.length) return;

  const protections = [
    [/M\.R\.S\.C\./g, "¶MRSC¶"],
    [/\bÉVA\./g, "¶EVA¶"],
    [/\betc\./gi, "¶ETC¶"],
    [/\bex\./gi, "¶EX¶"],
    [/\bcf\./gi, "¶CF¶"],
    [/\bn°\./gi, "¶N¶"],
    [/\bMme\./g, "¶MME¶"],
    [/\bMlle\./g, "¶MLLE¶"],
    [/\bDr\./g, "¶DR¶"],
    [/\bM\.\s(?=[A-ZÉÈÊ])/g, "¶M¶ "],
  ];

  const proteger = (texte) => {
    let sortie = texte;
    protections.forEach(([motif, jeton]) => {
      sortie = sortie.replace(motif, jeton);
    });
    return sortie;
  };

  const restaurer = (texte) => texte
    .replaceAll("¶MRSC¶", "M.R.S.C.")
    .replaceAll("¶EVA¶", "ÉVA.")
    .replaceAll("¶ETC¶", "etc.")
    .replaceAll("¶EX¶", "ex.")
    .replaceAll("¶CF¶", "cf.")
    .replaceAll("¶N¶", "n°.")
    .replaceAll("¶MME¶", "Mme.")
    .replaceAll("¶MLLE¶", "Mlle.")
    .replaceAll("¶DR¶", "Dr.")
    .replaceAll("¶M¶", "M.");

  const envelopperPhrases = (noeud) => {
    const brut = noeud.nodeValue;
    if (!brut || !/[.!?…]/.test(brut)) return;
    const protege = proteger(brut);
    const morceaux = protege
      .split(/(?<=[.!?…]["»”’']*)\s+(?=\S)/)
      .map((partie) => restaurer(partie).trim())
      .filter(Boolean);
    // Une ponctuation seule n'est pas une phrase : après un lien, le point final
    // formait un fragment « . » qui, mis en bloc, s'affichait sur sa propre
    // ligne (23 octobre 2026). Il rejoint la phrase qui le précède. S'il ouvre le
    // texte, il appartient au contenu en ligne qui précède ce nœud : on ne
    // découpe pas, plutôt que d'accrocher un point devant la phrase suivante.
    const phrases = [];
    for (const morceau of morceaux) {
      if (!/[\p{L}\p{N}]/u.test(morceau)) {
        if (!phrases.length) return;
        phrases[phrases.length - 1] += morceau;
        continue;
      }
      phrases.push(morceau);
    }
    if (phrases.length < 2) return;
    const fragment = document.createDocumentFragment();
    phrases.forEach((texte) => {
      const phrase = document.createElement("span");
      phrase.className = "phrase";
      phrase.textContent = texte;
      fragment.append(phrase);
    });
    noeud.parentNode.replaceChild(fragment, noeud);
  };

  racines.forEach((racine) => {
    racine.querySelectorAll("p, li, dd, dt, td, th, figcaption, blockquote, small").forEach((bloc) => {
      if (bloc.closest("nav, pre, code, button, label, summary, form")) return;
      // L’ouverture de l’accueil reste un texte suivi : le découpage en blocs
      // `.phrase` y collait les phrases à la copie et isolait les mots en gras.
      // Le reste du site garde sa présentation phrase par phrase.
      if (bloc.closest(".home-hero-civic")) return;
      if (bloc.querySelector(".phrase")) return;
      const parcours = document.createTreeWalker(bloc, NodeFilter.SHOW_TEXT, {
        acceptNode(noeud) {
          const parent = noeud.parentElement;
          if (!parent) return NodeFilter.FILTER_REJECT;
          if (parent.closest("a, button, code, pre, kbd, svg, label, .phrase")) return NodeFilter.FILTER_REJECT;
          if (!noeud.nodeValue || !noeud.nodeValue.trim()) return NodeFilter.FILTER_REJECT;
          return NodeFilter.FILTER_ACCEPT;
        },
      });
      const noeuds = [];
      while (parcours.nextNode()) noeuds.push(parcours.currentNode);
      noeuds.forEach(envelopperPhrases);
    });
  });
})();
