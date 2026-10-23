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
  const textLevels = [75, 85, 100, 115, 130];
  // Ancienne échelle en pourcentage, puis anciens crans indexés 0/1/2.
  const anciensCrans = { 50: 75, 75: 85, 100: 100, 125: 115, 150: 130 };
  const anciensIndexes = [100, 115, 130];
  const ANCIENNE_CLE = "mrsc-texte-niveau";
  let textLevel = 100;
  let contrastEnabled = false;
  let spacingEnabled = false;

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
  // et de clavier, plus bas, puissent le fermer.
  let personnalisation = null;
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
  });

  const toggle = document.querySelector("[data-menu-toggle]");
  const navigation = document.querySelector("[data-primary-navigation]");
  const header = document.querySelector(".site-header");
  const headerCompactToggle = document.querySelector("[data-header-compact-toggle]");

  if (toggle && navigation) {
    root.classList.add("has-js");

    // La hauteur de l'en-tête dépend du logo, du cran de texte et du mode
    // compact : le panneau du menu s'y accroche pour ne jamais dépasser le bas
    // de l'écran, même en paysage ou en texte très agrandi.
    if (header && typeof ResizeObserver === "function") {
      const publierHauteurEntete = () => {
        root.style.setProperty("--hauteur-entete", `${Math.round(header.getBoundingClientRect().height)}px`);
      };
      publierHauteurEntete();
      new ResizeObserver(publierHauteurEntete).observe(header);
    }

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

      const panneauPersonnalisation = document.createElement("div");
      panneauPersonnalisation.className = "customize-settings-panel";
      panneauPersonnalisation.id = "site-customize-panel";
      resume.setAttribute("aria-controls", panneauPersonnalisation.id);

      personnalisation.append(resume, panneauPersonnalisation);
      // Ordre voulu : agrandir/réduire, parcours (inséré ensuite par
      // navigation-parcours.js devant l'affichage), affichage, présentation.
      [headerCompactToggle, settings, layoutSettings].forEach((element) => {
        if (element) panneauPersonnalisation.append(element);
      });
      outilsEntete.append(personnalisation);
    }

    const closeMenu = () => {
      toggle.setAttribute("aria-expanded", "false");
      navigation.classList.remove("is-open");
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
      };

      headerCompactToggle.hidden = false;
      setHeaderCompact(Boolean(compactViewport?.matches));
      headerCompactToggle.addEventListener("click", () => {
        closeMenu();
        // Ne pas fermer « Personnalisation » : le bouton est dans son panneau, et
        // le refermer rendrait « Réduire » inatteignable une fois l'en-tête
        // agrandi.
        if (settings) settings.open = false;
        if (layoutSettings) layoutSettings.open = false;
        const journeySettings = document.querySelector("[data-site-journey]");
        if (journeySettings) journeySettings.open = false;
        setHeaderCompact(!header.classList.contains("is-compact"));
      });

      if (compactViewport) {
        const onViewportModeChange = () => {
          closeMenu();
          setHeaderCompact(compactViewport.matches);
        };
        if (typeof compactViewport.addEventListener === "function") {
          compactViewport.addEventListener("change", onViewportModeChange);
        } else {
          compactViewport.addListener?.(onViewportModeChange);
        }
      }

      // Sous 520 px, une réduction de fenêtre rétablit le format compact après
      // un agrandissement manuel. Une fois compact, ne pas réécrire son libellé
      // à chaque pixel de redimensionnement.
      if (narrowViewport) {
        let previousViewportWidth = window.innerWidth;
        window.addEventListener("resize", () => {
          const widthIsShrinking = window.innerWidth < previousViewportWidth;
          previousViewportWidth = window.innerWidth;
          if (!widthIsShrinking || !narrowViewport.matches || header.classList.contains("is-compact")) return;
          closeMenu();
          setHeaderCompact(true);
        });
      }
    }

    toggle.addEventListener("click", () => {
      const isOpen = toggle.getAttribute("aria-expanded") === "true";
      toggle.setAttribute("aria-expanded", String(!isOpen));
      navigation.classList.toggle("is-open", !isOpen);
      if (!isOpen) {
        if (settings) settings.open = false;
        if (layoutSettings) layoutSettings.open = false;
        const journeySettings = document.querySelector("[data-site-journey]");
        if (journeySettings) journeySettings.open = false;
      }
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
