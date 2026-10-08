(() => {
  document.querySelectorAll("[data-year]").forEach((element) => {
    element.textContent = String(new Date().getFullYear());
  });

  const root = document.documentElement;
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
  let textLevel = 0;
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

  const applyTextLevel = (level) => {
    textLevel = Math.max(0, Math.min(2, level));
    root.classList.toggle("texte-agrandi", textLevel === 1);
    root.classList.toggle("texte-tres-agrandi", textLevel === 2);
    if (textLevelOutput) textLevelOutput.textContent = `${[100, 125, 150][textLevel]} %`;
    if (textDecrease) textDecrease.disabled = textLevel === 0;
    if (textIncrease) textIncrease.disabled = textLevel === 2;
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
  };

  const loadPreferences = () => {
    const storedTextLevel = readPreference(keys.text);
    if (storedTextLevel === null) {
      // Migration du réglage binaire A+/A− précédemment proposé sur le site.
      textLevel = readPreference("mrsc-texte-agrandi") === "oui" ? 1 : 0;
    } else {
      const parsedLevel = Number.parseInt(storedTextLevel, 10);
      textLevel = Number.isFinite(parsedLevel) ? parsedLevel : 0;
    }
    applyTextLevel(textLevel);
    applyContrast(readPreference(keys.contrast) === "oui");
    applySpacing(readPreference(keys.spacing) === "oui");
  };

  loadPreferences();

  if (settings) {
    settings.hidden = false;
    textDecrease?.addEventListener("click", () => {
      applyTextLevel(textLevel - 1);
      savePreference(keys.text, String(textLevel));
    });
    textIncrease?.addEventListener("click", () => {
      applyTextLevel(textLevel + 1);
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

    document.addEventListener("click", (event) => {
      if (!settings.contains(event.target)) settings.open = false;
    });
  }

  // L’iframe locale et les pages M.R.S.C partagent ces réglages sur le même domaine.
  window.addEventListener("storage", (event) => {
    if (event.key === null || Object.values(keys).includes(event.key) || event.key === "mrsc-texte-agrandi") {
      loadPreferences();
    }
  });

  const toggle = document.querySelector("[data-menu-toggle]");
  const navigation = document.querySelector("[data-primary-navigation]");

  if (toggle && navigation) {
    root.classList.add("has-js");

    const closeMenu = () => {
      toggle.setAttribute("aria-expanded", "false");
      navigation.classList.remove("is-open");
    };

    toggle.addEventListener("click", () => {
      const isOpen = toggle.getAttribute("aria-expanded") === "true";
      toggle.setAttribute("aria-expanded", String(!isOpen));
      navigation.classList.toggle("is-open", !isOpen);
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
