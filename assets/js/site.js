(() => {
  document.querySelectorAll("[data-year]").forEach((element) => {
    element.textContent = String(new Date().getFullYear());
  });

  const toggle = document.querySelector("[data-menu-toggle]");
  const navigation = document.querySelector("[data-primary-navigation]");

  if (!toggle || !navigation) return;

  document.documentElement.classList.add("has-js");

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
    if (event.key === "Escape") closeMenu();
  });
})();

/* Simulateur macro-politique : quelle source afficher ?

   Le simulateur se développe en continu dans son propre dépôt. Trois sources
   sont possibles, par ordre de préférence :

   1. la *source distante* (version en développement), si le site est servi par
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
      // 1. La version en développement est-elle utilisable (vérifiée par le serveur) ?
      if (sourceDistante) {
        try {
          const reponse = await repond("/api/verifier-source", "GET");
          const etat = await reponse.json();
          if (etat && etat.disponible === true) {
            afficher(sourceDistante, "Source affichée : version en développement du simulateur.");
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
