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

/* Simulateur macro-politique : l'aperçu embarqué n'est chargé que si l'API du
   moteur répond à cette adresse. Sur un hébergeur sans exécution Python
   (GitHub Pages), l'avis « aperçu indisponible » prend sa place. */
(() => {
  document.querySelectorAll("[data-simulateur-apercu]").forEach((cadre) => {
    const source = cadre.getAttribute("data-src");
    const iframe = cadre.querySelector("iframe");
    const avis = document.querySelector("[data-simulateur-avis]");
    if (!source || !iframe) return;

    const indisponible = (raison) => {
      cadre.classList.add("is-indisponible");
      if (avis) {
        avis.hidden = false;
        const detail = avis.querySelector("[data-simulateur-raison]");
        if (detail && raison) detail.textContent = raison;
      }
    };

    fetch("/api/scenarios", { method: "HEAD" })
      .then((reponse) => {
        if (!reponse.ok) throw new Error("HTTP " + reponse.status);
        iframe.src = source;
      })
      .catch((erreur) => indisponible(String(erreur.message || erreur)));
  });
})();
