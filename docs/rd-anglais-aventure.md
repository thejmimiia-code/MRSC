# R&D — « Les Mondes », un atlas d’apprentissage et des Escales en 3D

**Recherche initiale sur l’anglais : 11 octobre 2026 · prototype élargi : 12 octobre 2026.** Le jeu relie les **81 fiches** du catalogue — réparties dans **15 domaines** — à un atlas de mondes et à un parcours de formation que la personne compose elle-même. Les fiches demeurent des ressources complètes et autonomes, ouvertes dans leur page dédiée ; l’atlas ne recopie pas leur leçon. **55 entrées portent le statut « Prototype à relire »** et restent identifiées comme telles. L’expérience comprend aussi cinq dialogues anglais en 3D. Aucun cursus certifiant ni effet d’apprentissage n’est revendiqué.

## 1. Question de conception

Comment rendre les ressources du site plus faciles à explorer sans imposer une matière, une méthode, un ordre, un rythme ou un profil ? L’atlas transforme les domaines et fiches existants en mondes et quêtes accessibles par recherche, repère de difficulté ou intérêt. La personne peut composer, réordonner et effacer un parcours local à partir de fiches autonomes. Les Escales en anglais restent une zone interactive distincte : les explications sont en français et les répliques à pratiquer sont en anglais.

Principes retenus : accès gratuit, aucun compte ni publicité, progression sans verrouillage, pas de vies, série obligatoire, pénalité, note ou compte à rebours ; aides disponibles ; repères présentés comme indications ; statut éditorial et lacunes visibles ; aucun service d’IA ni microphone.

## 2. Ce que la recherche a changé dans le prototype

- **CECRL et approche orientée vers l’action.** Le volume complémentaire du Conseil de l’Europe décrit l’apprenant comme un acteur social qui mobilise la réception, la production, l’interaction et la médiation pour atteindre des résultats dans des situations. Le prototype transforme donc chaque petite scène en but concret (obtenir un billet, commander, expliquer un souci, convenir d’un rendez-vous), plutôt qu’en quiz isolé. Les repères pré-A1, A1, A2 et B1 sont indicatifs : ils ne constituent ni un test ni une mesure officielle du niveau d’une personne. [Conseil de l’Europe — CEFR Companion Volume (2020)](https://rm.coe.int/common-european-framework-of-reference-for-languages-learning-teaching/16809ea0d4) ; [recherche de descripteurs CECRL](https://www.coe.int/en/web/common-european-framework-reference-languages/cefr-descriptors-search).
- **Parcours guidés par situations et niveaux.** Les ressources de British Council et de BBC Learning English proposent des activités par niveau et des scènes d’expression orale. Elles servent de repère d’organisation, pas de modèle à copier : les lieux, personnages, dialogues, objectifs, illustrations et interactions du prototype ont été créés séparément. [British Council — commencer et choisir un niveau](https://learnenglish.britishcouncil.org/getting-started) ; [British Council — speaking](https://learnenglish.britishcouncil.org/free-resources/speaking) ; [BBC Learning English — cours débutant](https://www.bbc.co.uk/learningenglish/easy_course).
- **Jeux mobiles et apprentissages de langues.** Une méta-analyse de 2025 rapporte des résultats encourageants dans plusieurs travaux, notamment pour le vocabulaire et la prononciation, mais les effets et les mécanismes varient. Une méta-analyse de jeux numériques en vocabulaire L2 relève également une hétérogénéité des études. Ces résultats ne démontrent pas qu’un jeu de quelques minutes rende autonome dans une conversation ordinaire ; le prototype ne fait donc aucune promesse de maîtrise. [Méta-analyse 2025 sur les jeux mobiles et l’apprentissage des langues](https://doi.org/10.1080/09588221.2025.2528786) ; [Tsai & Tsai — jeux numériques et vocabulaire L2](https://doi.org/10.1016/j.compedu.2018.06.020).
- **Réactivation sans calendrier coercitif.** Les synthèses sur la pratique espacée et la récupération espacée soutiennent l’intérêt de revoir une information après un intervalle, sans justifier un calendrier unique ni une sanction en cas d’absence. La première version fournit un carnet de phrases et permet de rejouer librement ; une planification de révision personnalisée reste à tester. [Kim & Webb — pratique espacée en L2](https://doi.org/10.1111/lang.12479) ; [Latimier et al. — pratique de récupération espacée](https://doi.org/10.1007/s10648-020-09572-8).
- **Motivation et autonomie.** Une synthèse d’interventions éducatives associées à la théorie de l’autodétermination souligne l’intérêt de soutenir l’autonomie et le sentiment de compétence. Le choix libre des missions, la possibilité de demander de l’aide, les réponses sans score et le droit de quitter ou de recommencer sont des hypothèses de conception inspirées par ces principes ; leur effet n’a pas été mesuré ici. [Wang et al. — synthèse et méta-analyse (2024)](https://selfdeterminationtheory.org/wp-content/uploads/2024/06/2024_WangWangEtAl_MetaEdu.pdf).
- **Accessibilité.** La scène 3D est décorative et ses commandes sont séparées du dialogue en HTML. Les missions sont aussi utilisables sans voix de synthèse, avec clavier et toucher ; un rendu illustré remplace WebGL si le navigateur ne le prend pas en charge. Ces choix ne prouvent pas la conformité ni l’utilisabilité : essais avec des personnes concernées, lecteurs d’écran, zoom et appareils réels restent à faire. [W3C — adaptations d’accessibilité pour les jeux Web](https://www.w3.org/2018/12/games-workshop/papers/web-games-adaptive-accessibility.html).

## 3. Atlas des savoirs et scènes interactives

La section **Les Mondes** réunit les 76 entrées du catalogue (26 fiches du corpus initial et 55 prototypes à relire), organisées en 15 mondes issus directement du référentiel éditorial. Les cartes affichent matière, domaine, repère 1 à 4, durée indicative, objectif et statut éditorial. La recherche porte sur les objectifs et situations ; filtres par monde, repère et statut permettent d’ouvrir les fiches publiques correspondantes. Les lacunes et sujets à relire restent accessibles depuis chaque monde. Le fichier du jeu est généré depuis les sources TOML du catalogue : il n’y a pas de deuxième saisie manuelle des 81 fiches.

Quatre **portes de formation libres** filtrent les fiches par repère : reprendre les bases, consolider, raisonner et approfondir. Elles ne constituent pas une progression obligatoire ni une certification. Un constructeur de parcours permet d’ajouter, retirer et réordonner des fiches. Seuls les identifiants choisis sont mémorisés localement ; la fiche elle-même reste la source complète de l’exercice et l’atlas ne déduit pas qu’elle a été terminée.

### Les Escales en anglais : cinq missions jouables

La page `anglais-aventure.html` contient cinq scènes ouvertes au choix :

| Escale | Repère indicatif | Situation et objectif de communication |
| --- | --- | --- |
| La gare des marées | Pré-A1 · A1 | Demander un billet, comprendre une indication et vérifier une information. |
| Le café des nuages | A1 | Commander, décliner ou accepter une proposition, poser une question sur le paiement. |
| Le marché aux couleurs | A1 · A2 | Chercher un produit, préciser une quantité et terminer un achat. |
| L’atelier du phare | A2 | Décrire un problème, préciser quand il a commencé et se mettre d’accord sur la suite. |
| Le club des promenades | B1 · conversation quotidienne | Raconter une activité, relancer un échange et négocier un changement de programme. |

Chaque mission comporte trois tours de dialogue, plusieurs réponses écrites à l’avance et un exemple de réponse libre à comparer. Au total, les données locales décrivent 15 échanges et 45 choix de réponse scénarisés. Une réplique choisie entraîne une réponse cohérente pré-écrite. La phrase saisie librement n’est pas analysée : elle n’est ni corrigée, ni transmise, ni enregistrée comme progression. Cette distinction est visible dans l’interface.

La lecture audio est facultative et déclenchée par un bouton. Elle utilise la synthèse vocale que fournit le navigateur ou l’appareil, si elle existe ; la qualité, l’accent et l’éventuelle dépendance de certaines voix à un service système ne sont pas contrôlés par M.R.S.C. Aucun enregistrement vocal ni reconnaissance automatique de la parole n’est proposé.

Les scènes jouables sont dessinées en WebGL natif, sans bibliothèque ou modèle distant, puis basculent vers une illustration si WebGL est indisponible. L’image de présentation et les dialogues sont des créations originales locales. Le projet ne reprend ni univers, ni personnages, ni formulations, ni interface d’un jeu ou d’une application existante.

### Progression et données

La clé `mrsc-anglais-aventure-v1` peut garder le niveau d’aide, les identifiants des Escales terminées et la liste ordonnée des fiches ajoutées volontairement au parcours. Elle ne contient ni réponses, ni texte libre, ni score. L’ensemble est conservé uniquement dans le `localStorage` du navigateur ; il est effaçable par le bouton global ou par le bouton du parcours. Si le stockage est bloqué, le jeu reste accessible pendant la visite, sans reprise locale. La notice `confidentialite.html` décrit ces données et précise que leur qualification juridique doit être confirmée par l’association.

## 4. Ce que le prototype ne prouve pas encore

- L’atlas relie et organise les fiches existantes ; il ne transforme pas encore chaque fiche en activité 3D distincte. Il n’existe pas dans le dépôt de cursus formel ou certifiant : les parcours composés sont des sélections personnelles de fiches autonomes.
- Les 50 prototypes doivent encore être relus ; les 26 entrées du corpus initial ne sont pas toutes garanties par une relecture indépendante. Le nombre d’entrées ne signifie ni couverture exhaustive ni validation pédagogique.
- Les cinq Escales ne couvrent pas tout le pré-A1, tous les descripteurs A1–B1, le B2, tous les accents, les différences culturelles, la compréhension d’un interlocuteur imprévisible ou l’ensemble des situations de la vie quotidienne.
- Les interactions sont en partie à choix multiples et le dialogue reste déterministe. Écrire une réponse libre entraîne à produire une phrase, mais le jeu ne comprend pas si elle convient.
- Les cartes et les traductions en français sont un soutien provisoire ; leur naturalité et leurs variantes doivent être relues par des personnes compétentes en anglais.
- Les résultats de la recherche sur les jeux ne permettent pas d’attribuer à cette maquette un bénéfice causal, une progression CECRL ou une autonomie conversationnelle.
- Aucune observation avec apprenants, expertise linguistique indépendante, session de navigateur réel, essai de charge ou test multi-appareil n’est revendiqué à cette date.

## 5. Suite de R&D proposée

1. Faire relire les dialogues, variantes, traductions, niveaux CECRL et registres par des personnes compétentes en anglais et en enseignement des langues ; consigner les corrections et leur date.
2. Évaluer l’accessibilité et la compréhension en conditions réelles : navigation clavier, zoom, contraste forcé, lecteur d’écran, commandes tactiles, voix installées ou absentes, petits écrans et faible puissance graphique.
3. Organiser, avec participation volontaire et information adaptée, des essais de compréhension et de scénarios réels auprès de personnes débutantes et de personnes ayant déjà une pratique quotidienne. Ne pas collecter les phrases privées ; recueillir uniquement les retours nécessaires avec un cadre de conservation défini.
4. Si les premiers essais le justifient, élargir progressivement les actes de communication et les niveaux, jusqu’aux situations quotidiennes B2 à concevoir ; proposer une révision espacée choisie et expliquer son fonctionnement sans pénalité. Développer les conversations autonomes comme objectif mesurable de recherche, pas comme bénéfice garanti.
5. Avant toute revendication d’efficacité, comparer une tâche de communication annoncée à l’avance, définir un protocole, publier les limites et distinguer les acquis immédiats de la rétention et du transfert vers une conversation réelle.
6. Revoir la notice de confidentialité et le périmètre technique si apparaissent un compte, une synchronisation, une analyse des réponses, un microphone, une reconnaissance vocale, une voix distante ou un outil d’audience.
