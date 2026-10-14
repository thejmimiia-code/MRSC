(() => {
  document.querySelectorAll("[data-year]").forEach((element) => {
    element.textContent = String(new Date().getFullYear());
  });

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
  const keys = {
    text: "mrsc-texte-niveau",
    contrast: "mrsc-contraste-renforce",
    spacing: "mrsc-espacement-renforce",
  };
  const textLevels = [50, 75, 100, 125, 150];
  const legacyTextLevels = [100, 125, 150];
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
    if (/^[0-2]$/.test(stored)) return legacyTextLevels[parsed];
    return 100;
  };

  const applyTextLevel = (value) => {
    textLevel = textLevels.includes(value) ? value : 100;
    root.classList.toggle("texte-tres-reduit", textLevel === 50);
    root.classList.toggle("texte-reduit", textLevel === 75);
    root.classList.toggle("texte-agrandi", textLevel === 125);
    root.classList.toggle("texte-tres-agrandi", textLevel === 150);
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
      contrastToggle.setAttribute(
        "aria-label",
        contrastEnabled ? "Désactiver le contraste renforcé" : "Activer le contraste renforcé"
      );
    }
    synchroniserSimulateurs();
  };

  const applySpacing = (enabled) => {
    spacingEnabled = Boolean(enabled);
    root.classList.toggle("espacement-renforce", spacingEnabled);
    if (spacingToggle) {
      spacingToggle.setAttribute("aria-pressed", String(spacingEnabled));
      spacingToggle.setAttribute(
        "aria-label",
        spacingEnabled ? "Désactiver l’espacement renforcé" : "Activer l’espacement renforcé"
      );
    }
    synchroniserSimulateurs();
  };

  const loadPreferences = () => {
    const storedTextLevel = readPreference(keys.text);
    if (storedTextLevel === null) {
      // Migration du réglage binaire A+/A− précédemment proposé sur le site.
      textLevel = readPreference("mrsc-texte-agrandi") === "oui" ? 125 : 100;
    } else {
      textLevel = niveauTexteEnregistre(storedTextLevel) ?? 100;
    }
    applyTextLevel(textLevel);
    applyContrast(readPreference(keys.contrast) === "oui");
    applySpacing(readPreference(keys.spacing) === "oui");
  };

  loadPreferences();

  const layoutPreferenceKey = "mrsc-mise-en-page";
  const layoutChoices = [
    {
      value: "equilibree",
      label: "Équilibrée",
      description: "La présentation de base, entre lecture et blocs visuels.",
    },
    {
      value: "lecture",
      label: "Lecture",
      description: "Une colonne plus étroite et des blocs empilés pour suivre les textes.",
    },
    {
      value: "panorama",
      label: "Panorama composite",
      description: "Une page plus large, avec un agencement de cartes en plusieurs colonnes.",
    },
  ];
  const layoutSettings = settings ? document.createElement("details") : null;
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

      const copy = document.createElement("span");
      copy.className = "layout-choice-copy";
      const name = document.createElement("strong");
      name.textContent = choice.label;
      const description = document.createElement("span");
      description.textContent = choice.description;
      copy.append(name, description);
      label.htmlFor = input.id;
      label.append(input, copy);
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
  });

  // L’iframe locale et les pages M.R.S.C partagent ces réglages sur le même domaine.
  window.addEventListener("storage", (event) => {
    if (event.key === null || Object.values(keys).includes(event.key) || event.key === "mrsc-texte-agrandi") {
      loadPreferences();
    }
  });

  const toggle = document.querySelector("[data-menu-toggle]");
  const navigation = document.querySelector("[data-primary-navigation]");
  const header = document.querySelector(".site-header");
  const headerCompactToggle = document.querySelector("[data-header-compact-toggle]");

  if (toggle && navigation) {
    root.classList.add("has-js");

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
      const headerDetails = [
        header.querySelector("#site-header-status"),
        header.querySelector("#site-header-identity"),
      ];

      const setHeaderCompact = (compact) => {
        const focusWouldBeHidden = compact
          && headerDetails.some((element) => element?.contains(document.activeElement));
        header.classList.toggle("is-compact", compact);
        root.classList.toggle("entete-compacte", compact);
        headerCompactToggle.setAttribute("aria-expanded", String(!compact));
        const label = compact ? "Agrandir" : "Réduire";
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

    document.addEventListener("keydown", (event) => {
      if (event.key !== "Escape") return;
      const menuWasOpen = navigation.classList.contains("is-open");
      closeMenu();
      if (menuWasOpen) toggle.focus();
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

   1. la *source distante* hébergée sur Render, si le site est servi par
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
      // 1. La version Render est-elle utilisable (vérifiée par le serveur) ?
      if (sourceDistante) {
        try {
          const reponse = await repond("/api/verifier-source", "GET");
          const etat = await reponse.json();
          if (etat && etat.disponible === true) {
            afficher(sourceDistante, "Source affichée : simulateur hébergé sur Render.");
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
