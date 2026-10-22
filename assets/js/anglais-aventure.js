/* Atlas de fiches, parcours personnel local et Escales anglaises déterministes,
   avec voix de synthèse à la demande et scènes WebGL sans bibliothèque distante. */
(() => {
  const data = globalThis.MRSCEnglishAdventureData;
  if (!data || !Array.isArray(data.missions) || typeof document === "undefined") return;
  const learningData = globalThis.MRSCApprentissageData;

  const $ = (selector) => document.querySelector(selector);
  const app = $("#adventure-app");
  const grid = $("#mission-grid");
  const dashboard = $(".adventure-dashboard");
  const playPanel = $("#play-panel");
  const playthrough = $("#mission-playthrough");
  const finishPanel = $("#mission-finish");
  const progressSummary = $("#progress-summary");
  const progressList = $("#progress-list");
  const storageNote = $("#storage-note");
  const helpLevel = $("#help-level");
  const helpLevelNote = $("#help-level-note");
  const translationToggle = $("#translation-toggle");
  const sceneCanvas = $("#world-canvas");
  const sceneFallback = $("#world-fallback");
  const sceneControls = $("#scene-controls");
  const audioNote = $("#audio-note");
  const voiceControl = $("#voice-control");
  const learningAtlasApp = $("#learning-atlas-app");
  const learningSheetList = $("#learning-sheet-grid");
  const learningDomainFilter = $("#learning-domain-filter");
  const learningLevelFilter = $("#learning-level-filter");
  const learningStatusFilter = $("#learning-status-filter");
  const learningSearch = $("#learning-search");
  const learningPathList = $("#learning-path-list");
  const voiceAccent = $("#voice-accent");
  const allMissionIds = new Set(data.missions.map((mission) => mission.id));
  const learningSheets = Array.isArray(learningData?.sheets) ? learningData.sheets : [];
  const learningDomains = Array.isArray(learningData?.domains) ? learningData.domains : [];
  const allLearningSheetIds = new Set(learningSheets.map((sheet) => sheet.id));
  const learningSheetsById = new Map(learningSheets.map((sheet) => [sheet.id, sheet]));
  const learningDomainsById = new Map(learningDomains.map((domain) => [domain.id, domain]));
  const levelNames = {
    discovery: "Pré-A1 / A1 · aides visibles",
    building: "A2 · aides à la demande",
    conversation: "B1 · aides à la demande",
  };
  const storageKey = "mrsc-anglais-aventure-v1";
  const state = { level: "discovery", completed: [], learningPath: [] };
  let currentMission = null;
  let currentTurnIndex = 0;
  let cafeTotal = { english: "six pounds forty", french: "six livres quarante" };
  let previousMissionButton = null;
  let translationsVisible = true;
  let speechAvailable = false;
  let gl = null;
  let shaderProgram = null;
  let vertexBuffer = null;
  let positionLocation = -1;
  let colorLocation = -1;
  let transformLocation = null;
  let cameraYaw = 0.76;
  let currentTheme = "station";
  let resizeObserver = null;

  const text = (element, value) => {
    if (element) element.textContent = String(value ?? "");
  };

  function loadProgress() {
    try {
      const raw = window.localStorage.getItem(storageKey);
      if (!raw) return;
      const saved = JSON.parse(raw);
      if (!saved || saved.version !== 1) return;
      if (levelNames[saved.level]) state.level = saved.level;
      if (Array.isArray(saved.completed)) {
        state.completed = [...new Set(saved.completed.filter((id) => allMissionIds.has(id)))];
      }
      if (Array.isArray(saved.learningPath)) {
        state.learningPath = [...new Set(saved.learningPath.filter((id) => allLearningSheetIds.has(id)))];
      }
    } catch (error) {
      showStorageNote("Le navigateur ne permet pas de lire l’avancement enregistré. Tu peux tout de même jouer sans le conserver.");
    }
  }

  function saveProgress() {
    try {
      window.localStorage.setItem(storageKey, JSON.stringify({
        version: 1,
        level: state.level,
        completed: state.completed,
        learningPath: state.learningPath,
      }));
      if (storageNote) storageNote.hidden = true;
    } catch (error) {
      showStorageNote("Le stockage local est bloqué : tes choix restent utilisables pendant cette visite, mais leur enregistrement échoue. Une ancienne copie peut rester présente ; efface les données du site dans les réglages du navigateur si nécessaire.");
    }
  }

  function showStorageNote(message) {
    if (!storageNote) return;
    text(storageNote, message);
    storageNote.hidden = false;
  }

  function renderProgress() {
    if (!progressSummary || !progressList) return;
    const count = state.completed.length;
    const plural = count > 1 ? "s" : "";
    text(
      progressSummary,
      count === 0
        ? "Aucune escale n’est à terminer : choisis librement parmi les cinq destinations."
        : `${count} escale${plural} découverte${plural} sur ${data.missions.length}. Tu peux toutes les refaire ou t’arrêter ici.`,
    );
    progressList.replaceChildren();
    data.missions.forEach((mission) => {
      const item = document.createElement("li");
      item.dataset.done = String(state.completed.includes(mission.id));
      text(item, mission.title);
      progressList.append(item);
    });
    grid?.querySelectorAll("[data-mission-id]").forEach((button) => {
      const done = state.completed.includes(button.dataset.missionId);
      button.dataset.completed = String(done);
      const status = button.querySelector("[data-quest-status]");
      text(status, done ? "Déjà découverte · recommencer ↗" : "Choisir cette escale ↗");
    });
  }

  function makeElement(tagName, className, content, language) {
    const element = document.createElement(tagName);
    if (className) element.className = className;
    if (content !== undefined) element.textContent = content;
    if (language) element.lang = language;
    return element;
  }

  function buildMissionCards() {
    if (!grid) return;
    grid.replaceChildren();
    data.missions.forEach((mission, index) => {
      const button = document.createElement("button");
      button.type = "button";
      button.className = "button adventure-quest-card";
      button.dataset.missionId = mission.id;
      button.dataset.completed = "false";

      const top = makeElement("span", "adventure-quest-top");
      top.append(
        makeElement("span", "adventure-quest-number", String(index + 1).padStart(2, "0")),
        makeElement("span", "adventure-quest-level", mission.level),
      );
      button.append(
        top,
        makeElement("span", "adventure-quest-title", mission.title),
        makeElement("span", "adventure-quest-copy", mission.brief),
        makeElement("span", "adventure-quest-status", "Choisir cette escale ↗"),
      );
      button.lastElementChild.dataset.questStatus = "";
      button.addEventListener("click", () => startMission(mission, button));
      grid.append(button);
    });
    renderProgress();
    renderLearningPath();
  }

  function normalizedLearningText(value) {
    return String(value ?? "")
      .toLocaleLowerCase("fr")
      .normalize("NFD")
      .replace(/[\u0300-\u036f]/g, "")
      .trim();
  }

  function learningSheetUrl(sheet) {
    if (!/^[a-z0-9-]+$/.test(sheet?.id || "")) return "apprendre.html#catalogue-fiches";
    return `apprendre/fiches/${sheet.id}.html`;
  }

  function renderLearningPath() {
    const count = state.learningPath.length;
    const countLabel = $("#learning-path-count");
    const empty = $("#learning-path-empty");
    if (countLabel) {
      text(countLabel, count === 0
        ? "Aucune fiche ajoutée à ton parcours."
        : `${count} fiche${count > 1 ? "s" : ""} dans ton parcours libre. Ce choix ne marque aucune fiche comme terminée.`);
    }
    if (empty) empty.hidden = count !== 0;
    if (!learningPathList) return;
    learningPathList.replaceChildren();
    state.learningPath.forEach((id, index) => {
      const sheet = learningSheetsById.get(id);
      if (!sheet) return;
      const item = document.createElement("li");
      item.className = "adventure-learning-path-item";
      const link = makeElement("a", "adventure-learning-path-link", sheet.title);
      link.href = learningSheetUrl(sheet);
      const controls = makeElement("div", "adventure-learning-path-controls");
      const earlier = makeElement("button", "button button-secondary", "↑");
      earlier.type = "button";
      earlier.dataset.pathAction = "earlier";
      earlier.dataset.sheetId = id;
      earlier.disabled = index === 0;
      earlier.setAttribute("aria-label", `Monter « ${sheet.title} » dans le parcours`);
      const later = makeElement("button", "button button-secondary", "↓");
      later.type = "button";
      later.dataset.pathAction = "later";
      later.dataset.sheetId = id;
      later.disabled = index === count - 1;
      later.setAttribute("aria-label", `Descendre « ${sheet.title} » dans le parcours`);
      const remove = makeElement("button", "button button-secondary", "Retirer");
      remove.type = "button";
      remove.dataset.pathAction = "remove";
      remove.dataset.sheetId = id;
      remove.setAttribute("aria-label", `Retirer « ${sheet.title} » du parcours`);
      controls.append(earlier, later, remove);
      item.append(link, controls);
      learningPathList.append(item);
    });
  }

  function renderLearningCards() {
    if (!learningSheetList) return;
    const resultCount = $("#learning-result-count");
    const noResults = $("#learning-no-results");
    const query = normalizedLearningText(learningSearch?.value);
    const domainId = learningDomainFilter?.value || "";
    const level = learningLevelFilter?.value || "";
    const editorial = learningStatusFilter?.value || "";
    const visible = learningSheets.filter((sheet) => {
      if (domainId && sheet.domainId !== domainId) return false;
      if (level && String(sheet.level) !== level) return false;
      if (editorial === "initial" && sheet.editorialStatus) return false;
      if (editorial === "prototype" && !sheet.editorialStatus) return false;
      if (!query) return true;
      const domain = learningDomainsById.get(sheet.domainId);
      const haystack = normalizedLearningText([
        sheet.title, sheet.subject, domain?.title, sheet.summary,
        sheet.objective, sheet.situation, sheet.horizon,
      ].join(" "));
      return haystack.includes(query);
    });
    learningSheetList.replaceChildren();
    visible.forEach((sheet) => {
      const item = document.createElement("li");
      item.className = "adventure-learning-sheet-item";
      const card = document.createElement("article");
      card.className = "adventure-learning-sheet-card";
      card.dataset.prototype = String(Boolean(sheet.editorialStatus));
      const domain = learningDomainsById.get(sheet.domainId);
      const meta = makeElement("p", "adventure-learning-sheet-meta");
      meta.append(
        makeElement("span", "", domain?.title || sheet.subject),
        makeElement("span", "", `Repère ${sheet.level} · ${sheet.levelName}`),
        makeElement("span", "", `${sheet.minutes} min environ`),
      );
      const badge = makeElement(
        "span",
        sheet.editorialStatus ? "adventure-learning-editorial adventure-learning-editorial-review" : "adventure-learning-editorial",
        sheet.editorialStatus || "Fiche du catalogue",
      );
      const heading = makeElement("h4", "adventure-learning-sheet-title");
      const openLink = makeElement("a", "", sheet.title);
      openLink.href = learningSheetUrl(sheet);
      heading.append(openLink);
      const summary = makeElement("p", "adventure-learning-sheet-summary", sheet.summary);
      const objective = makeElement("p", "adventure-learning-sheet-objective");
      objective.append(makeElement("strong", "", "Défi : "), document.createTextNode(sheet.objective));
      const actions = makeElement("div", "adventure-learning-sheet-actions");
      const enter = makeElement("a", "button", "Ouvrir la fiche complète");
      enter.href = learningSheetUrl(sheet);
      enter.setAttribute("aria-label", `Ouvrir la fiche complète : ${sheet.title}`);
      const add = makeElement(
        "button",
        state.learningPath.includes(sheet.id) ? "button button-secondary is-in-learning-path" : "button button-secondary",
        state.learningPath.includes(sheet.id) ? "Retirer du parcours" : "Ajouter à mon parcours",
      );
      add.type = "button";
      add.dataset.pathToggle = sheet.id;
      add.setAttribute(
        "aria-label",
        state.learningPath.includes(sheet.id)
          ? `Retirer du parcours : « ${sheet.title} »`
          : `Ajouter à mon parcours : « ${sheet.title} »`,
      );
      actions.append(enter, add);
      card.append(meta, badge, heading, summary, objective);
      if (sheet.horizon) {
        const horizon = makeElement("details", "adventure-learning-horizon");
        horizon.append(
          makeElement("summary", "", "Préciser le contexte et les limites"),
          makeElement("p", "", sheet.horizon),
        );
        card.append(horizon);
      }
      if (sheet.editorialNote) {
        const review = makeElement("details", "adventure-learning-review-note");
        review.append(
          makeElement("summary", "", "Que signifie ce statut ?"),
          makeElement("p", "", sheet.editorialNote),
        );
        card.append(review);
      }
      card.append(actions);
      item.append(card);
      learningSheetList.append(item);
    });
    if (resultCount) {
      const details = domainId ? learningDomainsById.get(domainId)?.title : "tous les mondes";
      text(resultCount, `${visible.length} fiche${visible.length === 1 ? "" : "s"} affichée${visible.length === 1 ? "" : "s"} sur ${learningSheets.length} · ${details || "tous les mondes"}.`);
    }
    if (noResults) noResults.hidden = visible.length !== 0;
    document.querySelectorAll("[data-path-toggle]").forEach((button) => {
      button.addEventListener("click", () => {
        const id = button.dataset.pathToggle;
        if (!allLearningSheetIds.has(id)) return;
        if (state.learningPath.includes(id)) {
          state.learningPath = state.learningPath.filter((sheetId) => sheetId !== id);
        } else {
          state.learningPath.push(id);
        }
        saveProgress();
        renderLearningPath();
        renderLearningCards();
        learningSheetList.querySelector(`[data-path-toggle="${id}"]`)?.focus();
      });
    });
  }

  function setupLearningAtlas() {
    const fallback = $("#learning-atlas-fallback");
    if (!learningAtlasApp) return;
    if (!learningData || learningData.version !== 1 || !learningSheets.length
        || !learningDomains.length || !learningSheetList) {
      if (fallback) fallback.hidden = false;
      return;
    }
    const routeGrid = $("#learning-routes");
    const worldGrid = $("#learning-world-grid");
    const glyphs = ["✒", "◎", "∑", "¤", "⚗", "⌖", "⌛", "◉", "⚖", "⌘", "⌨", "⌕", "♧", "⚙", "✦"];

    if (learningDomainFilter) {
      learningDomainFilter.replaceChildren(makeElement("option", "", "Tous les mondes"));
      learningDomainFilter.options[0].value = "";
    }
    learningDomains.forEach((domain, index) => {
      const option = document.createElement("option");
      option.value = domain.id;
      option.textContent = domain.title;
      learningDomainFilter?.append(option);

      if (worldGrid) {
        const world = document.createElement("article");
        world.className = `adventure-learning-world adventure-learning-world-${(index % 6) + 1}`;
        const choose = document.createElement("button");
        choose.type = "button";
        choose.className = "adventure-learning-world-button";
        choose.dataset.worldId = domain.id;
        choose.setAttribute("aria-pressed", "false");
        const glyph = makeElement("span", "adventure-learning-world-glyph", glyphs[index % glyphs.length]);
        glyph.setAttribute("aria-hidden", "true");
        choose.append(
          glyph,
          makeElement("span", "adventure-learning-world-title", domain.title),
          makeElement("span", "adventure-learning-world-intent", domain.intent),
          makeElement("span", "adventure-learning-world-count", `${domain.sheetCount} fiche${domain.sheetCount === 1 ? "" : "s"} · ${domain.futureCount} sujet${domain.futureCount === 1 ? "" : "s"} à développer`),
          makeElement("span", "visually-hidden", "Filtrer les fiches de ce monde."),
        );
        choose.addEventListener("click", () => {
          if (learningDomainFilter) learningDomainFilter.value = domain.id;
          renderLearningAtlasState();
          $("#learning-library-title")?.focus();
        });
        world.append(choose);
        if (domain.futureCount > 0) {
          const coverage = makeElement("a", "adventure-learning-world-coverage", "Voir les sujets à développer");
          coverage.href = domain.coverageUrl || "apprendre.html#couverture";
          world.append(coverage);
        }
        worldGrid?.append(world);
      }
    });

    learningData.paths.forEach((path) => {
      const button = document.createElement("button");
      button.type = "button";
      button.className = "adventure-learning-route";
      button.dataset.routeLevel = String(path.level);
      button.setAttribute("aria-pressed", "false");
      button.append(
        makeElement("span", "adventure-learning-route-level", `Repère ${path.level}`),
        makeElement("strong", "adventure-learning-route-title", path.title),
        makeElement("span", "adventure-learning-route-copy", path.description),
        makeElement("span", "adventure-learning-route-count", `${path.sheetCount} fiche${path.sheetCount === 1 ? "" : "s"} à explorer`),
      );
      button.addEventListener("click", () => {
        if (learningLevelFilter) learningLevelFilter.value = String(path.level);
        if (learningDomainFilter) learningDomainFilter.value = "";
        renderLearningAtlasState();
        $("#learning-library-title")?.focus();
      });
      routeGrid?.append(button);
    });

    $("#learning-show-all-worlds")?.addEventListener("click", () => {
      if (learningDomainFilter) learningDomainFilter.value = "";
      renderLearningAtlasState();
    });
    $("#learning-filters")?.addEventListener("submit", (event) => event.preventDefault());
    $("#learning-search")?.addEventListener("input", renderLearningAtlasState);
    learningDomainFilter?.addEventListener("change", renderLearningAtlasState);
    learningLevelFilter?.addEventListener("change", renderLearningAtlasState);
    learningStatusFilter?.addEventListener("change", renderLearningAtlasState);
    $("#learning-clear-filters")?.addEventListener("click", () => {
      if (learningSearch) learningSearch.value = "";
      if (learningDomainFilter) learningDomainFilter.value = "";
      if (learningLevelFilter) learningLevelFilter.value = "";
      if (learningStatusFilter) learningStatusFilter.value = "";
      renderLearningAtlasState();
    });
    learningPathList?.addEventListener("click", (event) => {
      const button = event.target.closest("button[data-path-action]");
      if (!button) return;
      const index = state.learningPath.indexOf(button.dataset.sheetId);
      if (index < 0) return;
      const action = button.dataset.pathAction;
      if (action === "remove") {
        state.learningPath.splice(index, 1);
      } else {
        const target = action === "earlier" ? index - 1 : index + 1;
        if (target < 0 || target >= state.learningPath.length) return;
        [state.learningPath[index], state.learningPath[target]] = [state.learningPath[target], state.learningPath[index]];
      }
      saveProgress();
      renderLearningPath();
      renderLearningCards();
      learningPathList.querySelector(`[data-path-action="${action}"][data-sheet-id="${button.dataset.sheetId}"]`)?.focus();
    });
    $("#learning-path-clear")?.addEventListener("click", () => {
      state.learningPath = [];
      saveProgress();
      renderLearningPath();
      renderLearningCards();
    });

    text($("#atlas-sheet-count"), learningData.sheetCount);
    text($("#atlas-world-count"), learningData.domainCount);
    text($("#atlas-prototype-count"), learningData.prototypeCount);
    learningAtlasApp.hidden = false;
    if (fallback) fallback.hidden = true;
    renderLearningPath();
    renderLearningAtlasState();
  }

  function renderLearningAtlasState() {
    renderLearningCards();
    const selectedDomain = learningDomainFilter?.value || "";
    document.querySelectorAll("[data-world-id]").forEach((button) => {
      button.setAttribute("aria-pressed", String(button.dataset.worldId === selectedDomain));
    });
    const showAll = $("#learning-show-all-worlds");
    showAll?.setAttribute("aria-pressed", String(!selectedDomain));
    const selectedLevel = learningLevelFilter?.value || "";
    document.querySelectorAll("[data-route-level]").forEach((button) => {
      button.setAttribute("aria-pressed", String(button.dataset.routeLevel === selectedLevel));
    });
  }

  function updateTranslationControls() {
    if (!translationToggle) return;
    translationToggle.setAttribute("aria-expanded", String(translationsVisible));
    text(translationToggle, translationsVisible ? "Masquer les traductions" : "Afficher les traductions");
    document.querySelectorAll(".phrase-translation").forEach((element) => {
      element.hidden = !translationsVisible;
    });
    document.querySelectorAll(".answer-french").forEach((element) => {
      element.hidden = !translationsVisible;
    });
  }

  function selectHelpLevel(value, save = true) {
    if (!levelNames[value]) value = "discovery";
    state.level = value;
    if (helpLevel) helpLevel.value = value;
    translationsVisible = value === "discovery";
    if (helpLevelNote) {
      const notes = {
        discovery: "Les traductions sont affichées d’emblée. Tu peux les masquer à tout moment.",
        building: "L’anglais apparaît d’abord. Tu peux afficher une traduction quand tu le souhaites.",
        conversation: "L’anglais apparaît d’abord ; la réponse libre est encouragée, sans être notée.",
      };
      text(helpLevelNote, notes[value]);
    }
    updateTranslationControls();
    if (save) saveProgress();
  }

  function setupSpeech() {
    speechAvailable = Boolean(
      window.speechSynthesis
      && typeof window.SpeechSynthesisUtterance === "function",
    );
    if (voiceControl) voiceControl.hidden = !speechAvailable;
    document.querySelectorAll(".adventure-listen-button").forEach((button) => {
      button.hidden = !speechAvailable;
    });
    if (!speechAvailable && audioNote) {
      text(audioNote, "La lecture audio du navigateur n’est pas disponible ici. Toutes les répliques restent lisibles.");
    }
  }

  function speak(phrase) {
    if (!speechAvailable || !phrase) return;
    try {
      window.speechSynthesis.cancel();
      const utterance = new window.SpeechSynthesisUtterance(phrase);
      const language = voiceAccent?.value || "en-GB";
      utterance.lang = language;
      utterance.rate = 0.92;
      utterance.pitch = 1;
      const voices = window.speechSynthesis.getVoices();
      const voice = voices.find((candidate) => candidate.lang.toLowerCase() === language.toLowerCase())
        || voices.find((candidate) => candidate.lang.toLowerCase().startsWith("en-"));
      if (voice) utterance.voice = voice;
      utterance.onerror = () => {
        if (audioNote) text(audioNote, "La voix de synthèse n’a pas pu lire cette phrase sur cet appareil ; tu peux continuer en lisant le texte.");
      };
      window.speechSynthesis.speak(utterance);
    } catch (error) {
      if (audioNote) text(audioNote, "La voix de synthèse n’est pas disponible pour le moment ; le texte reste accessible.");
    }
  }

  function setOptionalAudio(button, phrase) {
    if (!button) return;
    button.hidden = !speechAvailable;
    button.onclick = () => speak(phrase);
  }

  function renderTurn() {
    if (!currentMission) return;
    const turn = currentMission.turns[currentTurnIndex];
    text($("#mission-place"), currentMission.place);
    text($("#play-title"), currentMission.title);
    text($("#mission-outcome"), currentMission.outcome);
    text($("#active-level"), `Repère CECRL indicatif : ${currentMission.level}`);
    text($("#turn-count"), `Échange ${currentTurnIndex + 1} sur ${currentMission.turns.length}`);
    const progress = $("#turn-progress");
    if (progress) {
      progress.max = currentMission.turns.length;
      progress.value = currentTurnIndex + 1;
      progress.setAttribute("aria-label", `Échange ${currentTurnIndex + 1} sur ${currentMission.turns.length}`);
    }
    text($("#character-name"), turn.speaker);
    const lineEnglish = currentMission.id === "cafe" && currentTurnIndex === 2
      ? turn.english.replace("{total}", cafeTotal.english)
      : turn.english;
    const lineFrench = currentMission.id === "cafe" && currentTurnIndex === 2
      ? turn.french.replace("{total}", cafeTotal.french)
      : turn.french;
    text($("#dialogue-line"), lineEnglish);
    text($("#dialogue-translation"), lineFrench);
    text($("#turn-objective"), turn.objective);
    setOptionalAudio($("#listen-dialogue"), lineEnglish);

    const answers = $("#answer-options");
    answers?.replaceChildren();
    turn.options.forEach((option) => {
      const row = makeElement("li", "adventure-answer-option");
      const choose = document.createElement("button");
      choose.type = "button";
      choose.className = "button button-secondary adventure-answer-choice";
      choose.append(
        makeElement("span", "answer-english", option.english, "en"),
        makeElement("span", "answer-french", option.french, "fr"),
      );
      choose.addEventListener("click", () => showOptionOutcome(option));
      row.append(choose);
      if (speechAvailable) {
        const listen = makeElement("button", "button button-secondary adventure-answer-audio", "Écouter", "fr");
        listen.type = "button";
        listen.setAttribute("aria-label", `Écouter : ${option.english}`);
        listen.addEventListener("click", () => speak(option.english));
        row.append(listen);
      }
      answers?.append(row);
    });

    const answerArea = $(".adventure-answer-area");
    if (answerArea) answerArea.hidden = false;
    const practice = $("#free-practice");
    if (practice) {
      practice.hidden = false;
      practice.open = false;
    }
    const form = $("#free-answer-form");
    if (form) form.hidden = false;
    const input = $("#free-answer");
    if (input) input.value = "";
    const freeResult = $("#free-answer-result");
    if (freeResult) freeResult.hidden = true;
    const feedback = $("#turn-feedback");
    if (feedback) feedback.hidden = true;
    updateTranslationControls();
  }

  function showOptionOutcome(option) {
    if (currentMission?.id === "cafe" && currentTurnIndex === 1) {
      cafeTotal = {
        english: option.totalEnglish || "six pounds forty",
        french: option.totalFrench || "six livres quarante",
      };
    }
    const answerArea = $(".adventure-answer-area");
    if (answerArea) answerArea.hidden = true;
    const practice = $("#free-practice");
    if (practice) practice.hidden = true;
    const feedback = $("#turn-feedback");
    if (feedback) feedback.hidden = false;
    text($("#feedback-text"), option.feedback);
    text($("#micro-tip"), currentMission.turns[currentTurnIndex].tip);
    text($("#npc-reply"), option.replyEnglish);
    text($("#npc-reply-translation"), option.replyFrench);
    setOptionalAudio($("#listen-reply"), option.replyEnglish);
    const next = $("#continue-conversation");
    text(next, currentTurnIndex + 1 === currentMission.turns.length ? "Terminer cette escale" : "Continuer l’échange");
    updateTranslationControls();
    next?.focus();
  }

  function showFreePractice(event) {
    event.preventDefault();
    const answer = $("#free-answer");
    if (!answer?.value.trim()) {
      answer?.focus();
      return;
    }
    const turn = currentMission?.turns[currentTurnIndex];
    if (!turn) return;
    text($("#free-model-english"), turn.modelEnglish);
    text($("#free-model-french"), turn.modelFrench);
    text($("#free-answer-note"), "Le personnage ne réagit pas à ta phrase libre : la suite est un dialogue scénarisé, pas une évaluation de ta réponse. Tu peux comparer et continuer, ou revenir choisir une réplique.");
    const form = $("#free-answer-form");
    if (form) form.hidden = true;
    const result = $("#free-answer-result");
    if (result) result.hidden = false;
    updateTranslationControls();
    $("#continue-after-free")?.focus();
  }

  function nextTurn() {
    if (!currentMission) return;
    currentTurnIndex += 1;
    if (currentTurnIndex >= currentMission.turns.length) {
      finishMission();
      return;
    }
    renderTurn();
    $("#dialogue-line")?.focus();
  }

  function renderKeepsake() {
    const list = $("#keepsake-list");
    if (!list || !currentMission) return;
    list.replaceChildren();
    currentMission.keepsake.forEach((phrase) => {
      const item = document.createElement("li");
      item.append(
        makeElement("p", "adventure-keep-english", phrase.english, "en"),
        makeElement("p", "phrase-translation", phrase.french, "fr"),
      );
      if (speechAvailable) {
        const listen = makeElement("button", "button button-secondary adventure-listen-button", "Écouter", "fr");
        listen.type = "button";
        listen.setAttribute("aria-label", `Écouter : ${phrase.english}`);
        listen.addEventListener("click", () => speak(phrase.english));
        item.append(listen);
      }
      list.append(item);
    });
    updateTranslationControls();
  }

  function finishMission() {
    if (!currentMission) return;
    if (!state.completed.includes(currentMission.id)) {
      state.completed.push(currentMission.id);
      saveProgress();
    }
    renderProgress();
    text($("#finish-message"), `Dans « ${currentMission.title} », tu as essayé de ${currentMission.outcome.charAt(0).toLowerCase()}${currentMission.outcome.slice(1)}. Tu peux garder quelques expressions, rejouer ou choisir une autre escale.`);
    renderKeepsake();
    if (playthrough) playthrough.hidden = true;
    if (finishPanel) finishPanel.hidden = false;
    $("#finish-title")?.focus();
  }

  function startMission(mission, button) {
    currentMission = mission;
    currentTurnIndex = 0;
    cafeTotal = { english: "six pounds forty", french: "six livres quarante" };
    cameraYaw = 0.76;
    currentTheme = mission.theme;
    previousMissionButton = button || grid?.querySelector(`[data-mission-id="${mission.id}"]`);
    if (dashboard) dashboard.hidden = true;
    if (playPanel) playPanel.hidden = false;
    if (playthrough) playthrough.hidden = false;
    if (finishPanel) finishPanel.hidden = true;
    const caption = $("#scene-caption");
    text(caption, `Décor 3D original : ${mission.sceneDescription}`);
    renderTurn();
    drawCurrentWorld();
    $("#play-title")?.focus();
  }

  function returnToMap() {
    if (playPanel) playPanel.hidden = true;
    if (dashboard) dashboard.hidden = false;
    currentMission = null;
    previousMissionButton?.focus();
  }

  function clearProgress() {
    state.completed = [];
    state.learningPath = [];
    state.level = "discovery";
    if (helpLevel) helpLevel.value = state.level;
    selectHelpLevel("discovery", false);
    try {
      window.localStorage.removeItem(storageKey);
      if (storageNote) {
        text(storageNote, "Ton avancement a été effacé de cet appareil.");
        storageNote.hidden = false;
      }
    } catch (error) {
      showStorageNote("L’avancement a été réinitialisé pour cette visite. Pour effacer une ancienne copie, supprime les données locales du site dans les réglages du navigateur.");
    }
    renderProgress();
    renderLearningPath();
    renderLearningCards();
  }

  const colorChannels = (hex, factor = 1) => {
    const normalized = hex.replace("#", "");
    return [0, 2, 4].map((index) => {
      const value = Number.parseInt(normalized.slice(index, index + 2), 16) / 255;
      return Math.max(0, Math.min(1, value * factor));
    });
  };

  function makeWorldBuilder() {
    const vertices = [];
    const triangle = (a, b, c, color) => {
      const rgb = colorChannels(color);
      for (const point of [a, b, c]) vertices.push(point[0], point[1], point[2], rgb[0], rgb[1], rgb[2]);
    };
    const quad = (a, b, c, d, color, light = 1) => {
      const rgb = colorChannels(color, light);
      for (const point of [a, b, c, a, c, d]) vertices.push(point[0], point[1], point[2], rgb[0], rgb[1], rgb[2]);
    };
    const box = (x, y, z, width, height, depth, color) => {
      const x0 = x - width / 2; const x1 = x + width / 2;
      const y0 = y - height / 2; const y1 = y + height / 2;
      const z0 = z - depth / 2; const z1 = z + depth / 2;
      const c = [
        [x0, y0, z0], [x1, y0, z0], [x1, y1, z0], [x0, y1, z0],
        [x0, y0, z1], [x1, y0, z1], [x1, y1, z1], [x0, y1, z1],
      ];
      quad(c[4], c[5], c[6], c[7], color, 1.08);
      quad(c[1], c[0], c[3], c[2], color, .77);
      quad(c[0], c[4], c[7], c[3], color, .85);
      quad(c[5], c[1], c[2], c[6], color, .93);
      quad(c[3], c[7], c[6], c[2], color, 1.18);
      quad(c[0], c[1], c[5], c[4], color, .68);
    };
    const cylinder = (x, y, z, radius, height, color, segments = 16) => {
      const bottom = y - height / 2; const top = y + height / 2;
      for (let index = 0; index < segments; index += 1) {
        const a0 = Math.PI * 2 * index / segments;
        const a1 = Math.PI * 2 * (index + 1) / segments;
        const p0 = [x + Math.cos(a0) * radius, bottom, z + Math.sin(a0) * radius];
        const p1 = [x + Math.cos(a1) * radius, bottom, z + Math.sin(a1) * radius];
        const p2 = [p1[0], top, p1[2]];
        const p3 = [p0[0], top, p0[2]];
        quad(p0, p1, p2, p3, color, .84 + .16 * Math.sin(a0 + .8));
        triangle([x, top, z], p3, p2, color);
        triangle([x, bottom, z], p1, p0, color);
      }
    };
    const cone = (x, y, z, radius, height, color, segments = 16) => {
      const bottom = y - height / 2; const tip = [x, y + height / 2, z];
      for (let index = 0; index < segments; index += 1) {
        const a0 = Math.PI * 2 * index / segments;
        const a1 = Math.PI * 2 * (index + 1) / segments;
        const p0 = [x + Math.cos(a0) * radius, bottom, z + Math.sin(a0) * radius];
        const p1 = [x + Math.cos(a1) * radius, bottom, z + Math.sin(a1) * radius];
        triangle(p0, p1, tip, colorChannels(color, .86 + .14 * Math.sin(a0 + .6)).map((value) => `#${Math.round(value * 255).toString(16).padStart(2, "0")}`).join(""));
      }
    };
    const sphere = (x, y, z, radius, color, rings = 8, segments = 12) => {
      const point = (row, column) => {
        const phi = Math.PI * row / rings;
        const theta = Math.PI * 2 * column / segments;
        return [
          x + radius * Math.sin(phi) * Math.cos(theta),
          y + radius * Math.cos(phi),
          z + radius * Math.sin(phi) * Math.sin(theta),
        ];
      };
      for (let row = 0; row < rings; row += 1) {
        for (let column = 0; column < segments; column += 1) {
          const a = point(row, column); const b = point(row + 1, column);
          const c = point(row + 1, column + 1); const d = point(row, column + 1);
          const factor = .78 + .28 * (1 - row / rings);
          const shaded = colorChannels(color, factor).map((value) => `#${Math.round(value * 255).toString(16).padStart(2, "0")}`).join("");
          triangle(a, b, c, shaded); triangle(a, c, d, shaded);
        }
      }
    };
    const beam = (from, to, thickness, color) => {
      const dx = to[0] - from[0]; const dy = to[1] - from[1]; const dz = to[2] - from[2];
      const length = Math.hypot(dx, dy, dz) || 1;
      const direction = [dx / length, dy / length, dz / length];
      const reference = Math.abs(direction[1]) < .92 ? [0, 1, 0] : [0, 0, 1];
      const cross = (a, b) => [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]];
      const normalize = (vector) => { const size = Math.hypot(...vector) || 1; return vector.map((value) => value / size); };
      const u = normalize(cross(direction, reference)); const v = normalize(cross(direction, u));
      const corner = (point, su, sv) => [point[0] + u[0] * su + v[0] * sv, point[1] + u[1] * su + v[1] * sv, point[2] + u[2] * su + v[2] * sv];
      const r = thickness / 2;
      const a = corner(from, -r, -r); const b = corner(from, r, -r); const c = corner(from, r, r); const d = corner(from, -r, r);
      const e = corner(to, -r, -r); const f = corner(to, r, -r); const g = corner(to, r, r); const h = corner(to, -r, r);
      quad(a, b, f, e, color, .86); quad(b, c, g, f, color, 1.05); quad(c, d, h, g, color, .94); quad(d, a, e, h, color, .76);
      quad(a, d, c, b, color, 1.12); quad(e, f, g, h, color, .8);
    };
    const ringZ = (x, y, z, major, minor, color, segments = 20, sides = 6) => {
      const point = (u, v) => {
        const theta = Math.PI * 2 * u / segments;
        const phi = Math.PI * 2 * v / sides;
        const r = major + minor * Math.cos(phi);
        return [x + r * Math.cos(theta), y + r * Math.sin(theta), z + minor * Math.sin(phi)];
      };
      for (let u = 0; u < segments; u += 1) {
        for (let v = 0; v < sides; v += 1) {
          const a = point(u, v); const b = point(u + 1, v);
          const c = point(u + 1, v + 1); const d = point(u, v + 1);
          quad(a, b, c, d, color, .85 + .18 * Math.cos(Math.PI * 2 * v / sides));
        }
      }
    };
    const roof = (x, y, z, width, height, depth, color) => {
      const frontLeft = [x - width / 2, y, z + depth / 2];
      const frontRight = [x + width / 2, y, z + depth / 2];
      const backLeft = [x - width / 2, y, z - depth / 2];
      const backRight = [x + width / 2, y, z - depth / 2];
      const ridgeFront = [x, y + height, z + depth / 2];
      const ridgeBack = [x, y + height, z - depth / 2];
      quad(frontLeft, ridgeFront, ridgeBack, backLeft, color, .86);
      quad(ridgeFront, frontRight, backRight, ridgeBack, color, 1.08);
      triangle(frontLeft, frontRight, ridgeFront, color);
      triangle(backRight, backLeft, ridgeBack, color);
    };
    const tree = (x, z, leaves) => {
      cylinder(x, .53, z, .2, 1.1, "#7c5940", 9);
      sphere(x, 1.48, z, .82, leaves, 7, 10);
      sphere(x - .48, 1.23, z + .1, .48, leaves, 6, 9);
      sphere(x + .42, 1.3, z - .1, .54, leaves, 6, 9);
    };
    const character = (x, z, shirt = "#e58c62", skin = "#d79b72", hair = "#473a36") => {
      box(x - .14, .31, z, .17, .62, .18, "#3a536d");
      box(x + .14, .31, z, .17, .62, .18, "#3a536d");
      box(x, .91, z, .62, .76, .34, shirt);
      beam([x - .29, 1.13, z], [x - .47, .73, z + .05], .14, shirt);
      beam([x + .29, 1.13, z], [x + .46, .76, z - .04], .14, shirt);
      sphere(x, 1.55, z, .31, skin, 7, 10);
      sphere(x, 1.72, z - .05, .32, hair, 6, 9);
      sphere(x + .08, 1.51, z + .28, .035, "#28384a", 4, 6);
    };
    const planter = (x, z, leaves = "#609a67") => {
      box(x, .25, z, .58, .5, .58, "#bb7655");
      tree(x, z, leaves);
    };
    const base = (palette) => {
      box(0, -1.16, 0, 34, .2, 34, palette.water);
      box(0, -.62, 0, 18, 1.0, 12, palette.rock);
      box(0, -.08, 0, 15.4, .16, 9.6, palette.land);
      box(0, -.16, 0, 15.1, .1, 9.4, palette.shore);
      for (let index = 0; index < 9; index += 1) {
        const fraction = index / 8;
        const x = -6.2 + fraction * 11.7;
        const z = 2.75 - fraction * 4.05 + (index % 2 ? .18 : -.12);
        box(x, .015, z, .62, .09, .52, palette.path);
      }
      tree(-6.15, -2.7, palette.leaves);
      tree(6.2, -2.4, palette.leaves);
      tree(-6.55, 2.55, palette.leaves);
      sphere(-5.5, 5.2, -5.2, .72, palette.cloud, 6, 9);
      sphere(-4.65, 5.5, -5.4, .92, palette.cloud, 6, 9);
      sphere(-3.65, 5.2, -5.35, .66, palette.cloud, 6, 9);
      sphere(6.25, 5.5, -4.8, .95, palette.sun, 8, 10);
      sphere(6.25, 5.5, -4.8, .72, palette.sunLight, 8, 10);
    };
    const sign = (x, y, z, width, labelColor, poleColor = "#6e5a44") => {
      cylinder(x, y - .58, z, .075, 1.2, poleColor, 8);
      box(x, y + .18, z, width, .53, .12, labelColor);
      box(x, y + .18, z + .075, width * .72, .055, .025, "#fff1c6");
    };
    const canopy = (x, y, z, width, depth, colors) => {
      const strips = colors.length;
      for (let index = 0; index < strips; index += 1) {
        const stripWidth = width / strips;
        const left = x - width / 2 + index * stripWidth + stripWidth / 2;
        box(left, y, z, stripWidth + .015, .16, depth, colors[index]);
      }
      box(x - width / 2 + .06, y - .72, z + depth / 2 - .02, .1, 1.25, .1, "#735a46");
      box(x + width / 2 - .06, y - .72, z + depth / 2 - .02, .1, 1.25, .1, "#735a46");
    };
    const stall = (x, z, canopyColors, produce) => {
      box(x, .72, z, 2.65, .28, 1.2, "#9a6848");
      box(x, .94, z, 2.82, .12, 1.35, "#e8c48d");
      canopy(x, 2.12, z - .08, 2.95, 1.55, canopyColors);
      produce.forEach((item, index) => {
        const column = index % 5;
        const row = Math.floor(index / 5);
        sphere(x - .88 + column * .43, 1.27 + row * .12, z + .02, .19, item, 6, 8);
      });
    };

    const palettes = {
      station: { sky: "#94cfdf", water: "#438eaa", rock: "#556e78", land: "#86a97b", shore: "#d4b77f", path: "#e4d3ad", leaves: "#50886f", cloud: "#f8efd8", sun: "#e5a451", sunLight: "#f2ca73" },
      cafe: { sky: "#f2caa3", water: "#4f9cac", rock: "#566e72", land: "#849b68", shore: "#dbc28d", path: "#e6d9b5", leaves: "#568561", cloud: "#fff0d5", sun: "#ec9e59", sunLight: "#f4d27d" },
      market: { sky: "#a4d5d0", water: "#4c9b9a", rock: "#5c7271", land: "#82a574", shore: "#d8c28c", path: "#eedeb9", leaves: "#4c8666", cloud: "#f4eedb", sun: "#e5a24a", sunLight: "#f1cf74" },
      workshop: { sky: "#9abbd2", water: "#4c8e9c", rock: "#596f75", land: "#84a277", shore: "#d8bd87", path: "#dfd4b6", leaves: "#527c5c", cloud: "#f4ead5", sun: "#dc9551", sunLight: "#f1c979" },
      club: { sky: "#8dcddc", water: "#3d8fa8", rock: "#5b777a", land: "#7fa06e", shore: "#e4c99a", path: "#e9d7b0", leaves: "#568064", cloud: "#f8efd7", sun: "#e6a253", sunLight: "#f6d47e" },
    };

    function build(theme) {
      vertices.length = 0;
      const palette = palettes[theme] || palettes.station;
      base(palette);
      if (theme === "station") {
        box(-2.2, 1.31, -.95, 5.15, 2.72, 2.75, "#d7bd91");
        roof(-2.2, 2.67, -.95, 5.65, 1.35, 3.12, "#294760");
        box(-2.2, 2.33, .56, 5.3, .16, 1.25, "#c4774f");
        for (const x of [-4.05, -2.25, -.45]) box(x, 1.34, .46, .72, .96, .12, "#82b9bb");
        box(-2.2, .42, .55, 5.25, .14, 1.25, "#785b45");
        sign(-2.2, 2.17, .76, 2.1, "#355b74");
        cylinder(-2.2, 2.5, .77, .25, .09, "#f3dfb5", 16);
        box(-2.1, .09, 2.35, 6.7, .16, 1.15, "#b9aa8c");
        for (let index = 0; index < 9; index += 1) box(-5.2 + index * 1.35, .07, 3.12, .65, .12, .22, "#765943");
        box(-.3, .2, 3.12, 9.5, .16, .1, "#4f5f68");
        box(-.3, .2, 3.52, 9.5, .16, .1, "#4f5f68");
        box(2.25, .79, 3.48, 4.35, 1.2, 1.1, "#44728b");
        box(2.25, 1.44, 3.48, 4.3, .16, 1.15, "#e6b665");
        for (const x of [.65, 1.9, 3.15]) {
          cylinder(x, .25, 4.08, .3, .12, "#293d4d", 12);
          cylinder(x, .25, 4.08, .13, .13, "#c9d4ce", 12);
          box(x, .92, 2.91, .18, .48, .08, "#a9d5d1");
        }
        character(-.15, 1.82, "#db815b", "#c88d68", "#4c3833");
        character(4.65, .8, "#568b85", "#dfad87", "#392f2f");
        planter(-5.3, .85);
      } else if (theme === "cafe") {
        box(-3.15, 1.08, -.95, 4.3, 2.15, 2.65, "#e6c792");
        roof(-3.15, 2.15, -.95, 4.75, 1.18, 2.95, "#315369");
        box(-3.15, .45, .45, 4.45, .13, 1.5, "#d8875c");
        canopy(-3.15, 2.16, .7, 4.55, 1.15, ["#e1795a", "#fff0cd", "#e1795a", "#fff0cd", "#e1795a", "#fff0cd"]);
        for (const x of [-4.2, -2.3]) box(x, 1.18, .42, .8, .9, .12, "#77adb0");
        sign(-3.15, 2.48, .87, 1.8, "#497260");
        for (const x of [.15, 2.2]) {
          cylinder(x, .68, 1.55, .52, .13, "#9a6848", 12);
          cylinder(x, .39, 1.55, .08, .55, "#806047", 9);
          character(x + .72, 1.35, x < 1 ? "#eb9565" : "#5b8c84", "#d9a17a", "#4b3631");
        }
        cylinder(1.2, 1.12, .95, .17, .65, "#f2dfbe", 10);
        cylinder(1.2, 1.25, .95, .18, .08, "#825b43", 10);
        planter(-5.65, 2.25, "#5e8d5c");
      } else if (theme === "market") {
        stall(-3.2, -.6, ["#e68f58", "#fff0cc", "#e68f58", "#fff0cc", "#e68f58"], ["#d85f4d", "#e3af48", "#79a461", "#d85f4d", "#e3af48", "#79a461", "#e59846", "#c64f4d", "#d8b34b", "#79a461"]);
        stall(2.25, -.9, ["#438c94", "#f3e2c1", "#438c94", "#f3e2c1", "#438c94"], ["#df7050", "#e8bd52", "#d65b4f", "#74a45f", "#e4a047", "#d45b4c", "#e5b84d", "#78a55f", "#d65b4f", "#e39a41"]);
        character(-1.1, 1.2, "#527b8b", "#cf9972", "#403632");
        character(4.5, 1.45, "#e38c5c", "#dba47a", "#54423a");
        box(0, .18, 1.85, 1.25, .12, .8, "#b18a55");
        sign(0, 2.03, .05, 1.7, "#3e756d");
      } else if (theme === "workshop") {
        box(-3.05, 1.22, -1.15, 4.55, 2.42, 2.55, "#c8b38c");
        roof(-3.05, 2.43, -1.15, 5.0, 1.13, 2.9, "#3d5970");
        box(-3.05, .8, .18, 1.65, 1.56, .17, "#70563f");
        box(-4.45, .55, .18, .66, .48, .2, "#c9d7d2");
        box(-3.05, 2.08, .29, 2.3, .16, .12, "#d79454");
        sign(-3.05, 2.6, .38, 2.2, "#517568");
        // Vélo dessiné comme un objet 3D simple, avec roues et cadre en volume.
        ringZ(.55, .63, 1.68, .59, .085, "#324e61", 22, 7);
        ringZ(2.0, .63, 1.68, .59, .085, "#324e61", 22, 7);
        for (const x of [.55, 2.0]) {
          beam([x, .63, 1.55], [x, .63, 1.82], .035, "#c7d6d7");
          beam([x - .58, .63, 1.68], [x + .58, .63, 1.68], .035, "#c7d6d7");
        }
        beam([.55, .63, 1.55], [1.18, 1.12, 1.58], .105, "#d9874f");
        beam([1.18, 1.12, 1.58], [2.0, .63, 1.55], .105, "#d9874f");
        beam([2.0, .63, 1.55], [1.12, .63, 1.55], .105, "#d9874f");
        beam([1.12, .63, 1.55], [.55, .63, 1.55], .105, "#d9874f");
        beam([1.12, .63, 1.55], [1.12, 1.0, 1.58], .12, "#5b7180");
        beam([1.0, 1.0, 1.58], [1.35, 1.0, 1.58], .09, "#354858");
        beam([2.0, .63, 1.55], [2.18, 1.18, 1.55], .09, "#5b7180");
        beam([2.05, 1.18, 1.55], [2.48, 1.18, 1.55], .09, "#354858");
        box(-.5, .75, 2.95, 2.0, .16, .78, "#8d6348");
        for (const x of [-1.25, .25]) box(x, .35, 2.95, .12, .75, .12, "#73533f");
        box(-.6, .98, 2.65, .68, .08, .16, "#d7b16e");
        character(3.45, -.15, "#548b83", "#dda681", "#46332d");
        planter(-5.7, 2.3, "#688b59");
      } else if (theme === "club") {
        // Jetée, point de rendez-vous et phare au bout du chemin.
        box(1.95, .13, 2.7, 5.2, .18, 1.1, "#bd9862");
        for (let index = 0; index < 8; index += 1) box(-.5 + index * .68, .24, 2.7, .09, .18, .94, "#795e43");
        cylinder(5.35, 1.45, -1.65, .62, 2.95, "#f0e3c5", 18);
        cylinder(5.35, 1.52, -1.65, .635, .42, "#c65d4b", 18);
        box(5.35, 2.91, -1.65, 1.32, .2, 1.32, "#b85a49");
        cone(5.35, 3.35, -1.65, .76, .7, "#ad5646", 16);
        sphere(5.35, 2.72, -.94, .27, "#f2c96e", 7, 9);
        box(-3.55, .64, -.85, 2.05, .17, .45, "#916849");
        for (const x of [-4.25, -2.85]) box(x, .37, -.85, .14, .56, .14, "#74563f");
        character(-.9, 1.38, "#e08b62", "#dba37b", "#45352e");
        character(.2, 1.7, "#51877e", "#bf8769", "#413532");
        character(2.9, 1.0, "#6c83a0", "#dca27a", "#543a2e");
        sphere(-5.5, .45, 1.8, .38, "#e39a5d", 7, 10);
        box(-5.5, .1, 1.8, .22, .4, .22, "#e39a5d");
      }
      return { vertices, sky: palette.sky };
    }

    return { build };
  }

  const worldBuilder = makeWorldBuilder();

  function compileShader(context, type, source) {
    const shader = context.createShader(type);
    if (!shader) return null;
    context.shaderSource(shader, source);
    context.compileShader(shader);
    if (!context.getShaderParameter(shader, context.COMPILE_STATUS)) {
      context.deleteShader(shader);
      return null;
    }
    return shader;
  }

  function setupRenderer() {
    if (gl && shaderProgram && vertexBuffer) return true;
    if (!sceneCanvas) return false;
    try {
      gl = sceneCanvas.getContext("webgl", { alpha: false, antialias: true, powerPreference: "low-power" })
        || sceneCanvas.getContext("experimental-webgl");
    } catch (error) {
      gl = null;
    }
    if (!gl) return false;
    const vertexSource = `
      attribute vec3 a_position;
      attribute vec3 a_color;
      uniform mat4 u_transform;
      varying vec3 v_color;
      void main(void) {
        gl_Position = u_transform * vec4(a_position, 1.0);
        v_color = a_color;
      }
    `;
    const fragmentSource = `
      precision mediump float;
      varying vec3 v_color;
      void main(void) {
        gl_FragColor = vec4(v_color, 1.0);
      }
    `;
    const vertexShader = compileShader(gl, gl.VERTEX_SHADER, vertexSource);
    const fragmentShader = compileShader(gl, gl.FRAGMENT_SHADER, fragmentSource);
    if (!vertexShader || !fragmentShader) return false;
    shaderProgram = gl.createProgram();
    gl.attachShader(shaderProgram, vertexShader);
    gl.attachShader(shaderProgram, fragmentShader);
    gl.linkProgram(shaderProgram);
    gl.deleteShader(vertexShader);
    gl.deleteShader(fragmentShader);
    if (!gl.getProgramParameter(shaderProgram, gl.LINK_STATUS)) {
      shaderProgram = null;
      gl = null;
      return false;
    }
    positionLocation = gl.getAttribLocation(shaderProgram, "a_position");
    colorLocation = gl.getAttribLocation(shaderProgram, "a_color");
    transformLocation = gl.getUniformLocation(shaderProgram, "u_transform");
    vertexBuffer = gl.createBuffer();
    gl.enable(gl.DEPTH_TEST);
    gl.depthFunc(gl.LEQUAL);
    gl.disable(gl.CULL_FACE);
    sceneCanvas.addEventListener("webglcontextlost", (event) => {
      event.preventDefault();
      useSceneFallback();
    });
    if ("ResizeObserver" in window) {
      resizeObserver = new ResizeObserver(() => resizeAndDraw());
      resizeObserver.observe(sceneCanvas.parentElement);
    } else {
      window.addEventListener("resize", resizeAndDraw, { passive: true });
    }
    return Boolean(vertexBuffer);
  }

  function chargerRepliScene() {
    const picture = sceneFallback?.closest("picture");
    if (!picture || picture.dataset.charge === "oui") return;
    for (const source of picture.querySelectorAll("source[data-srcset]")) {
      source.srcset = source.dataset.srcset;
      source.removeAttribute("data-srcset");
    }
    if (sceneFallback.dataset.src) {
      sceneFallback.src = sceneFallback.dataset.src;
      sceneFallback.removeAttribute("data-src");
    }
    picture.dataset.charge = "oui";
  }

  function useSceneFallback() {
    chargerRepliScene();
    if (sceneCanvas) sceneCanvas.hidden = true;
    if (sceneFallback) sceneFallback.hidden = false;
    if (sceneControls) sceneControls.hidden = true;
    gl = null;
    shaderProgram = null;
    vertexBuffer = null;
  }

  function vectorSubtract(a, b) { return [a[0] - b[0], a[1] - b[1], a[2] - b[2]]; }
  function vectorCross(a, b) { return [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]]; }
  function vectorDot(a, b) { return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]; }
  function vectorNormalize(a) { const length = Math.hypot(...a) || 1; return a.map((value) => value / length); }

  function perspective(fieldOfView, aspect, near, far) {
    const f = 1 / Math.tan(fieldOfView / 2);
    const range = 1 / (near - far);
    return new Float32Array([
      f / aspect, 0, 0, 0,
      0, f, 0, 0,
      0, 0, (near + far) * range, -1,
      0, 0, near * far * 2 * range, 0,
    ]);
  }

  function lookAt(eye, center, up) {
    const z = vectorNormalize(vectorSubtract(eye, center));
    const x = vectorNormalize(vectorCross(up, z));
    const y = vectorCross(z, x);
    return new Float32Array([
      x[0], y[0], z[0], 0,
      x[1], y[1], z[1], 0,
      x[2], y[2], z[2], 0,
      -vectorDot(x, eye), -vectorDot(y, eye), -vectorDot(z, eye), 1,
    ]);
  }

  function multiplyMatrices(a, b) {
    const result = new Float32Array(16);
    for (let column = 0; column < 4; column += 1) {
      for (let row = 0; row < 4; row += 1) {
        let value = 0;
        for (let index = 0; index < 4; index += 1) value += a[index * 4 + row] * b[column * 4 + index];
        result[column * 4 + row] = value;
      }
    }
    return result;
  }

  function resizeAndDraw() {
    if (!gl || !sceneCanvas || !shaderProgram) return;
    const bounds = sceneCanvas.getBoundingClientRect();
    if (!bounds.width || !bounds.height) return;
    // Le décor est dessiné une fois par monde, pas à chaque image : rendre à la
    // densité réelle de l'écran ne coûte donc rien en continu. L'ancien plafond
    // de 1,5 faisait agrandir le tampon par le CSS sur tout écran à 2× ou 3×,
    // ce qui rendait les arêtes des décors floues. Le budget de pixels protège
    // les appareils modestes sur un écran très large, sans jamais descendre
    // sous 1 (un tampon plus petit que la zone d'affichage serait toujours flou).
    const densite = Math.min(window.devicePixelRatio || 1, 2);
    const pixelsDisponibles = 4_000_000;
    const surfaceCss = bounds.width * bounds.height;
    const densiteMax = Math.sqrt(pixelsDisponibles / surfaceCss);
    const pixelRatio = Math.max(1, Math.min(densite, densiteMax));
    const width = Math.max(1, Math.round(bounds.width * pixelRatio));
    const height = Math.max(1, Math.round(bounds.height * pixelRatio));
    if (sceneCanvas.width !== width || sceneCanvas.height !== height) {
      sceneCanvas.width = width;
      sceneCanvas.height = height;
    }
    drawSceneBuffer(worldBuilder.build(currentTheme), width, height);
  }

  function drawSceneBuffer(scene, width, height) {
    if (!gl || !scene || !scene.vertices.length) return;
    gl.viewport(0, 0, width, height);
    const sky = colorChannels(scene.sky);
    gl.clearColor(sky[0], sky[1], sky[2], 1);
    gl.clear(gl.COLOR_BUFFER_BIT | gl.DEPTH_BUFFER_BIT);
    gl.useProgram(shaderProgram);
    gl.bindBuffer(gl.ARRAY_BUFFER, vertexBuffer);
    gl.bufferData(gl.ARRAY_BUFFER, new Float32Array(scene.vertices), gl.STATIC_DRAW);
    gl.enableVertexAttribArray(positionLocation);
    gl.enableVertexAttribArray(colorLocation);
    gl.vertexAttribPointer(positionLocation, 3, gl.FLOAT, false, 24, 0);
    gl.vertexAttribPointer(colorLocation, 3, gl.FLOAT, false, 24, 12);
    const eye = [Math.cos(cameraYaw) * 19, 11.3, Math.sin(cameraYaw) * 19];
    const view = lookAt(eye, [0, .55, 0], [0, 1, 0]);
    const projection = perspective(Math.PI / 3.25, width / height, .1, 90);
    gl.uniformMatrix4fv(transformLocation, false, multiplyMatrices(projection, view));
    gl.drawArrays(gl.TRIANGLES, 0, scene.vertices.length / 6);
  }

  function drawCurrentWorld() {
    if (!setupRenderer()) {
      useSceneFallback();
      return;
    }
    if (sceneCanvas) sceneCanvas.hidden = false;
    if (sceneFallback) sceneFallback.hidden = true;
    if (sceneControls) sceneControls.hidden = false;
    currentTheme = currentMission?.theme || currentTheme;
    window.requestAnimationFrame(resizeAndDraw);
  }

  function updateMissionForScene() {
    if (!currentMission) return;
    text($("#scene-caption"), `Décor 3D original : ${currentMission.sceneDescription}`);
    drawCurrentWorld();
  }

  if (!app || !grid || !dashboard || !playPanel) return;
  loadProgress();
  buildMissionCards();
  selectHelpLevel(state.level, false);
  setupSpeech();
  setupLearningAtlas();
  app.hidden = false;

  helpLevel?.addEventListener("change", () => selectHelpLevel(helpLevel.value));
  translationToggle?.addEventListener("click", () => {
    translationsVisible = !translationsVisible;
    updateTranslationControls();
  });
  $("#clear-progress")?.addEventListener("click", clearProgress);
  $("#back-to-map")?.addEventListener("click", returnToMap);
  $("#finish-to-map")?.addEventListener("click", returnToMap);
  $("#replay-mission")?.addEventListener("click", () => {
    if (currentMission) startMission(currentMission, previousMissionButton);
  });
  $("#continue-conversation")?.addEventListener("click", nextTurn);
  $("#continue-after-free")?.addEventListener("click", nextTurn);
  $("#free-answer-form")?.addEventListener("submit", showFreePractice);
  $("#scene-left")?.addEventListener("click", () => { cameraYaw -= .34; updateMissionForScene(); });
  $("#scene-right")?.addEventListener("click", () => { cameraYaw += .34; updateMissionForScene(); });
  $("#scene-reset")?.addEventListener("click", () => { cameraYaw = .76; updateMissionForScene(); });
  window.addEventListener("pagehide", () => {
    if (window.speechSynthesis) window.speechSynthesis.cancel();
    resizeObserver?.disconnect();
  });
})();
