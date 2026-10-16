# Prospective R&D et innovation — apprendre, vérifier, délibérer (2027–2030)

**Note de travail datée du 15 octobre 2026. État : scénarios exploratoires et concept candidat, non validés.** Cette note n'est ni une prévision, ni une étude de marché, ni une promesse de produit. Elle part des sources déjà présentes dans le dépôt et de questions de conception. Aucun balayage externe d'actualité, atelier avec l'association, test avec des personnes ou avis expert n'a été réalisé dans cette passe. Les futurs décrits ci-dessous sont des situations possibles conçues pour éprouver les choix du projet ; aucune probabilité ne leur est attribuée.

## 1. Question de prospective et périmètre

**Question :** comment le M.R.S.C. peut-il maintenir des ressources d'apprentissage et de réflexion civique compréhensibles, accessibles et vérifiables si l'accès aux services numériques, la médiation par des outils d'IA, les langues de travail et la capacité de relecture évoluent de façons différentes d'ici 2030 ?

- **Horizon de travail :** 2027–2030, choisi pour organiser une réflexion proche; ce n'est pas une date de changement annoncé.
- **Contexte :** site aujourd'hui principalement francophone, ancré dans des repères français, catalogue ouvert et simulateur. Ce cadre ne représente pas toutes les régions, langues ou associations.
- **Publics possibles :** personnes qui apprennent, transmettent, animent ou utilisent des ressources citoyennes; aucun profil ni besoin individuel n'est supposé.
- **Hors périmètre :** prédire le rythme d'adoption de l'IA, le marché, l'évolution juridique ou l'avenir du travail; noter des opinions comme des faits; décider d'une stratégie à la place de l'association; développer un assistant qui répondrait librement à partir de données non revues.

Le sujet prospectif n'est donc pas « quelle technologie gagnera ? », mais **quelles capacités resteront utiles sous plusieurs futurs plausibles** et quelles dépendances le M.R.S.C. doit rendre visibles.

## 2. Base de départ vérifiable dans le dépôt

| Point de départ | Élément observé dans les fichiers | Limite de ce constat |
|---|---|---|
| Corpus d'apprentissage | 81 fiches dans 15 domaines, dont 55 prototypes explicitement à relire; les statuts et lacunes sont portés par le catalogue et le référentiel. | Un compte de fiches ne mesure ni qualité, ni couverture suffisante, ni effet d'apprentissage. |
| Usages de l'IA et information | Des ressources couvrent déjà la vérification d'une information, d'une réponse d'IA, d'un média et d'une demande inhabituelle. Elles sont présentées comme partielles. | La carte n'est pas une liste exhaustive des risques; elle ne prédit pas les fraudes futures. |
| Interface et autonomie | Le site propose cinq niveaux de texte, trois présentations et des réglages locaux; les contenus centraux sont conçus pour rester accessibles sans compte obligatoire. | Le protocole d'essais d'usage reste à faire relire; aucune validation par des personnes n'est revendiquée. |
| Services externes | Le site conserve une copie locale du simulateur et désigne Vercel pour la version distante. | Les réponses HTTP actuelles, l'API distante, l'iframe et les paramètres de confidentialité du fournisseur ne sont pas vérifiés ici. |
| Langues et formes | Les Mondes comprend cinq Escales en anglais; le portefeuille garde les autres langues et contextes locaux comme chantier. | La présence d'une traduction ou d'une scène ne prouverait pas sa pertinence culturelle ni sa qualité pédagogique. |
| Gouvernance et vie privée | La R&D distingue contrôle automatique, relecture spécialisée, décision éditoriale et essai d'usage; les préférences de présentation sont décrites comme locales. | Les informations sur les fournisseurs, les journaux et plusieurs choix juridiques restent à confirmer par l'association. |

Les références de ces constats sont le [portefeuille R&D](portefeuille.toml), le [référentiel](../apprentissage/referentiel.toml), le [parcours d'apprentissage](../rd-parcours-apprentissage.md), la [recherche sur les usages de l'IA et les fraudes](../rd-ia-usages-fraudes.md), l'[affichage adaptatif](../rd-affichage-adaptatif.md) et l'[inventaire de confidentialité](../rd-confidentialite-rgpd.md). Ce sont des documents de travail du dépôt, pas des audits indépendants.

## 3. Incertitudes à surveiller — sans les transformer en tendances établies

| Incertitude | Ce que le dépôt montre aujourd'hui | Question qui reste ouverte | Signal utile à suivre sans profiler les personnes |
|---|---|---|---|
| Médiation par l'IA | Des fiches apprennent à vérifier des résultats et à garder la main; ÉVA n'a pas de capacité démontrée dans le dépôt. | Les outils futurs aideront-ils à retrouver des ressources, ou rendront-ils plus difficile de distinguer source, résumé, hypothèse et décision ? | Nouvelles fonctionnalités réellement documentées, changements de sources et retours généraux transmis volontairement. |
| Continuité des services | Le simulateur a une version locale et une cible distante; plusieurs fournisseurs sont cités dans les inventaires. | Quelles fonctions seront encore disponibles, publiques et compatibles au moment où elles seront consultées ? | Version de la copie, tests directs de disponibilité avant publication, erreurs reproductibles et changements documentés d'hébergeur. |
| Capacité de relecture | 55 prototypes sont à relire; les contenus à risque ont besoin de personnes compétentes. | Le volume de propositions et de contenus pourra-t-il être entretenu avec des rôles de relecture clairement attribués ? | Échéances de revue, sources à recontrôler, décisions de retrait ou de report; pas le nombre de clics. |
| Langues et contextes | Le français domine; les autres langues et variétés demandent des relectures locales. | Comment ouvrir des parcours plurilingues sans publier une traduction automatique comme ressource validée ? | Disponibilité de relectures par langue/région et propositions non identifiantes, sans déduire l'origine des visiteurs. |
| Personnalisation et vie privée | Les préférences de lecture sont optionnelles et locales; l'association doit encore confirmer certains traitements et fournisseurs. | Comment adapter l'expérience sans compte, profil de compétence ou collecte individuelle implicite ? | Évolutions documentées des fonctions, du stockage ou des prestataires; revue du code et de la notice. |

Ces signaux ne sont pas des indicateurs d'audience. Une absence de demandes ne prouve pas l'absence de besoin, et une disponibilité technique ne prouve pas la qualité d'une ressource.

## 4. Quatre futurs pour éprouver les choix

Deux axes servent ici de **stress-test**, pas de prévision : continuité des services externes (plutôt stable ou souvent interrompue) et capacité à maintenir la provenance et la relecture humaine (forte ou limitée). La médiation par l’IA est une incertitude distincte, pas un synonyme de manque de contrôle : elle peut exister avec des pratiques de vérification robustes. Les combinaisons ci-dessous sont volontairement contrastées.

### A. Le commun vérifiable — services disponibles, contenus relus

Les ressources externes restent accessibles et les personnes responsables peuvent maintenir un corpus limité, daté et relu. Le risque est de prendre la stabilité technique pour une garantie de fond. **Réponse robuste :** afficher les sources, leur portée, le statut de chaque fiche et les lacunes; laisser l'accès aux contenus complets simple, sans imposer un parcours unique.

### B. L'assistant fluide, preuves contestées — services disponibles, traçabilité fragile

Des outils de synthèse ou d'assistance peuvent devenir une voie parmi d'autres pour consulter l'information, alors que le lien entre affirmation, source, date et relecture est difficile à suivre. C'est une hypothèse de scénario, pas une évolution mesurée dans ce travail; l'IA n'est qu'une manifestation possible de ce contexte. Le risque pour le site serait de présenter une réponse fluide comme une source ou une validation. **Réponse robuste :** relier chaque affirmation importante à une source vérifiable, séparer fait, exemple, interprétation et proposition, maintenir une rédaction humaine pour les contenus publics et permettre de continuer sans assistant.

### C. Le réseau intermittent — services fragiles, contenus principalement relus

Une page distante, une API ou un média tiers devient indisponible, lent ou soumis à une nouvelle condition d'accès. Le risque est qu'une fonctionnalité optionnelle bloque le cœur de la ressource. **Réponse robuste :** conserver un parcours local ou imprimable, indiquer la date/version d'une copie, isoler les fonctions distantes et afficher un repli compréhensible plutôt qu'un chargement infini.

### D. L'archipel opaque — services fragiles, médiation automatisée forte

Les outils et leurs sources changent d'un fournisseur à l'autre tandis que des contenus générés sont difficiles à rattacher à une preuve. C'est le scénario de stress le plus contraignant, sans probabilité supposée. **Réponse robuste :** ne pas courir après chaque service; garder un socle autonome, afficher ce qui a été vérifié et ce qui ne l'a pas été, suspendre les fonctions sans provenance exploitable et offrir un chemin de retour humain.

## 5. Décisions « sans regret » valables dans plusieurs futurs

1. **Garder un noyau autonome.** Une fiche doit pouvoir atteindre son objectif sans API, compte, média ou assistant obligatoire; les améliorations numériques restent facultatives.
2. **Tracer le statut et le contexte.** Pour les affirmations qui le nécessitent : nature de l'énoncé, source directe, date de consultation, périmètre, limites, statut éditorial et prochaine revue. Un lien vivant seul ne prouve pas que le contenu est à jour.
3. **Séparer les couches.** Distinguer sources, règles du modèle, paramètres de la personne, calcul et résultat du simulateur; pouvoir retirer la connexion distante sans faire passer un résultat local pour actuel.
4. **Personnaliser à la demande, pas par profilage.** Maintenir des choix réversibles, locaux et compréhensibles; ne pas inférer une compétence, un handicap ou une préférence depuis un comportement.
5. **Ouvrir par petites unités relues.** Ajouter une langue, un domaine ou une fonctionnalité avec les personnes compétentes, l'alternative accessible, une solution de repli et une condition de retrait définies avant publication.
6. **Utiliser la maintenance comme signal.** Les dates de revue, versions et sources à confirmer sont plus utiles pour la décision que des métriques d'engagement individuelles.
7. **Partir de ce que la personne sait déjà.** Une fiche peut nommer un geste déjà maîtrisé (un mot connu, une lecture ligne par ligne, une question déjà posée) sans le transformer en niveau scolaire ni en score. Cette capacité reste utile dans les quatre scénarios : elle n'exige ni assistant, ni profil, ni service distant.
8. **Rester identifiable sans service tiers.** Une icône dérivée du logo, servie avec le site, aide à reconnaître un onglet, un favori ou un raccourci lorsque plusieurs services se ressemblent ou se coupent. Ce n'est pas une preuve de qualité du contenu.

Ce sont des propositions de conception cohérentes avec les consignes actuelles du dépôt, pas des résultats démontrés auprès de visiteurs.

## 6. Options d'innovation comparées

| Concept | Ce que la personne pourrait faire | Valeur à éprouver | Coût/risque principal | Décision de cette note |
|---|---|---|---|---|
| **Boussole des savoirs** | Partir d'une question choisie dans une liste, puis suivre une ou plusieurs pistes vers des fiches existantes, leurs statuts, leurs sources et leurs limites. | Trouver un second point d'entrée sans confondre une piste avec un cursus ou une réponse complète. | Relations à maintenir; risque de redoubler la recherche et les filtres déjà présents dans Les Mondes. | **Premier prototype HTML** (16 oct. 2026) sur `apprendre.html#boussole-savoirs` : dix questions statiques issues du catalogue, sans API ni profil. Reste à relire par l’association ; ce n’est pas un essai d’usage. |
| **Passeport d'un résultat du simulateur** | Distinguer paramètres, version du moteur, hypothèses, sources de données, résultat calculé et limites. | Comprendre ce qui a produit un résultat et ce qui n'est ni prévision ni fait observé. | Besoin d'une revue méthodologique; la provenance et l'API distantes ne sont pas vérifiées ici. | Garder comme piste séparée; ne pas fabriquer un passeport tant que les champs de provenance et le modèle n'ont pas été revus. |
| **Kit autonome à emporter** | Lire ou imprimer une courte séquence de fiches avec les mêmes objectifs, sources et dates, même sans réseau continu. | Continuer l'apprentissage lorsque l'accès à un service distant échoue. | Risque de copie périmée et de multiplication des versions. | **Premier pas** (16 oct. 2026) : feuille d’impression du site (masque l’en-tête et les commandes). Pas encore un kit de fiches versionnées. |
| **Ne rien construire** | Continuer avec les fiches, l'atlas, les filtres et le simulateur existants; corriger uniquement des obstacles observés. | Préserver la simplicité et consacrer le temps à la relecture de contenu. | Un besoin de navigation transversale pourrait rester non traité. | Option de référence; à retenir si le prototype n'apporte pas de bénéfice observable au-delà de l'existant. |

## 7. Prototype de travail proposé : une Boussole locale, sans IA

### Question pilote

« Comment vérifier une information avant de la partager ? » Cette question existe déjà dans le catalogue; elle n'est pas ici présentée comme une demande d'usager observée.

### Parcours de papier

- **Entrée :** une question choisie parmi des formulations éditées; pas de champ libre.
- **Repère de départ :** `civ-verifier-information` — sujet « Vérification de l’information », statut `partiel` dans le référentiel.
- **Pistes facultatives :** source publique (`civ-choisir-source-publique`), comparaison historique (`histoire-comparer-sources`), réponse d'IA (`numerique-verifier-ia`), image/voix/vidéo (`numerique-verifier-media`), conservation de référence (`recherche-conserver-reference`), distinction résumé/citation (`recherche-distinguer-resume-citation`) ou source de santé publique (`sante-reperer-source-publique`). Le référentiel marque actuellement chacun des sujets correspondants `partiel`.
- **Affichage :** des lignes et boutons texte d'abord; une carte ou un graphe visuel peut compléter, jamais remplacer, la liste accessible. Chaque piste donne une raison simple d'ouvrir la fiche et une voie pour revenir à la question.
- **Limite visible :** les statuts décrivent la couverture éditoriale des sujets, pas la fiabilité d'une source, la compétence de la personne ou le niveau atteint. Toutes les pistes restent partielles; aucune ne doit être appelée « parcours complet ».
- **Dépendances :** lire les identifiants et statuts depuis le catalogue/référentiel déjà maintenu; aucun classement par IA, appel réseau, compte, profil, sauvegarde de choix ou score.

### Hypothèse et possibilité de l'infirmer

**Hypothèse :** une liste courte de pistes reliées à la question peut aider à découvrir une deuxième fiche pertinente tout en rendant visibles les limites du corpus.

La proposition serait affaiblie ou rejetée si :

- les relations entre fiches ne peuvent pas être justifiées par une relecture éditoriale;
- les personnes comprennent le statut `partiel` comme une note de qualité, ou la Boussole comme une réponse faisant autorité;
- la même tâche est déjà aussi simple avec les filtres et la recherche de l'atlas;
- la maintenance des relations crée une deuxième source de vérité ou augmente le risque de lien obsolète;
- l'équivalent texte, le clavier ou le retour ne fonctionnent pas aussi bien que la présentation visuelle.

### Portes avant construction ou essai

1. L'association choisit ou écarte le concept et confirme le périmètre éditorial.
2. Une personne éditoriale vérifie chaque relation, la formulation, le statut et les sources; les éléments non relus restent marqués.
3. Une première représentation sur papier permet de modifier ou retirer une piste sans changer le site.
4. Avant tout essai avec des personnes, faire approuver le protocole et les modalités de consentement/données selon l'initiative `co-conception-et-essais`; aucun recrutement n'est lancé par cette note.
5. Définir avant le test des observations de tâche et des critères d'arrêt avec les rôles concernés. Ne pas annoncer d'amélioration d'apprentissage sur la base d'un essai de navigation.

## 8. Feuille de route à décider, sans échéance promise

| Étape | Livrable | Porte de décision |
|---|---|---|
| 1. Cadrer les incertitudes | Atelier interne autour des quatre scénarios, faits de départ et inconnues | L'association confirme que la question et l'horizon sont utiles; sinon, fermer ou reformuler l'initiative. |
| 2. Vérifier les signaux externes | Sources primaires datées sur les thèmes effectivement retenus (accessibilité, IA, infrastructure, règles applicables, langues) et registre de portée/limites | Aucun chiffre ou tendance publique sans source lue directement et recoupée si nécessaire. |
| 3. Comparer les concepts | Boussole, passeport du simulateur, kit autonome, ne rien construire | Choisir un seul pilote avec rôle de maintenance et critère de retrait. |
| 4. Prototyper hors production | Carte papier puis éventuellement une page statique non reliée à la navigation | Aucune modification de la source de vérité avant d'avoir démontré la valeur du prototype. |
| 5. Revoir et essayer | Relectures éditoriale, accessibilité, vie privée/droit et essai volontaire seulement s'il est utile et autorisé | Distinguer correction structurelle, compréhension, préférence et efficacité; conserver les limites. |
| 6. Décider | Itérer, intégrer sous contrôle, conserver en prototype ou retirer | Laisser les validations manquantes et la prochaine revue visibles. |

## 9. Sources de départ, limites et suite

Les faits de départ sont issus des fichiers du dépôt :

- [`docs/apprentissage/catalogue.toml`](../apprentissage/catalogue.toml) et [`referentiel.toml`](../apprentissage/referentiel.toml) — fiches et statuts éditoriaux;
- [`docs/rd-parcours-apprentissage.md`](../rd-parcours-apprentissage.md) et [`docs/rd-ia-usages-fraudes.md`](../rd-ia-usages-fraudes.md) — objectifs, recherches documentaires antérieures et limites de couverture;
- [`docs/rd-affichage-adaptatif.md`](../rd-affichage-adaptatif.md) et [`docs/rd-confidentialite-rgpd.md`](../rd-confidentialite-rgpd.md) — contrôles existants, stockage, dépendances et validations encore ouvertes;
- [`docs/rd/protocole-essais-usage.md`](protocole-essais-usage.md) et [`portefeuille.toml`](portefeuille.toml) — état du protocole et initiatives en cours.

Cette première passe ne prétend pas avoir consulté les sources externes actuelles sur l'avenir de l'IA, les politiques publiques, l'accessibilité, le droit ou les infrastructures. Les références externes présentes dans les notes antérieures sont des repères documentaires à réouvrir avant toute affirmation nouvelle; elles ne suffisent pas à établir une tendance future. Aucune probabilité, préférence collective, expérience d'usager ou décision de l'association n'est inventée.

**Prochaine action :** faire examiner le cadrage et le concept « Boussole des savoirs » par le M.R.S.C.; décider si un atelier de prospective et une recherche primaire complémentaire valent le coût avant de fabriquer le prototype. L'initiative `prospective-apprentissages-2030` reste `a-cadrer` jusque-là.
