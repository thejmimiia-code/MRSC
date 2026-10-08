/* Filtres facultatifs du catalogue : toutes les fiches restent accessibles
   dans le HTML si JavaScript est désactivé ou indisponible. Aucun choix n'est
   enregistré et aucune requête réseau n'est déclenchée par ce script. */
(() => {
  const form = document.querySelector("[data-learning-filters]");
  const list = document.querySelector("[data-fiche-list]");
  if (!form || !list) return;

  const search = form.querySelector("[data-filter-search]");
  const subject = form.querySelector("[data-filter-subject]");
  const level = form.querySelector("[data-filter-level]");
  const count = document.querySelector("[data-filter-count]");
  const empty = document.querySelector("[data-filter-empty]");
  const cards = [...list.querySelectorAll("[data-fiche-card]")];

  const normaliser = (value) => String(value || "")
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .toLocaleLowerCase("fr");

  const filtrer = () => {
    const terme = normaliser(search?.value.trim());
    const matiere = subject?.value || "";
    const niveau = level?.value || "";
    let visibles = 0;

    for (const card of cards) {
      const correspond = (!matiere || card.dataset.matiere === matiere)
        && (!niveau || card.dataset.niveau === niveau)
        && (!terme || normaliser(card.dataset.recherche).includes(terme));
      card.hidden = !correspond;
      if (correspond) visibles += 1;
    }

    if (count) {
      count.textContent = `${visibles} entrée${visibles === 1 ? "" : "s"} affichée${visibles === 1 ? "" : "s"} sur ${cards.length}.`;
    }
    if (empty) empty.hidden = visibles !== 0;
  };

  form.addEventListener("submit", (event) => event.preventDefault());
  form.addEventListener("input", filtrer);
  form.addEventListener("change", filtrer);
  form.addEventListener("reset", () => window.setTimeout(filtrer, 0));
  filtrer();
})();
