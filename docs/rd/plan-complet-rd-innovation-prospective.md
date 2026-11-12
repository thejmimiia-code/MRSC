# Plan complet de R&D, d’innovation et de prospective — M.R.S.C.

**Instantané daté du 10 novembre 2026, amendé après la consigne « la relecture c’est toi qui doit la faire », complété le 11 novembre 2026 par la passe de sources, par son complément de seconde passe, par une troisième passe sur l’accueil IGN et par un lot de plan complet sur l’ensemble du projet. État : document de travail, non validé par l’association.** Ce plan rassemble l’ensemble du projet à partir des registres du dépôt ; il ne clôt aucun chantier, ne remplace ni l’expertise compétente, ni la décision associative, ni le regard de la personne sur le rendu, et ne décide à la place de personne. La **relecture de contenu et la vérification des sources incombent à l’agent** (`docs/protocole-editorial.md`, `docs/rd/relecture-automatique.md`) : elles sont exécutées dans ce lot pour les 81 prototypes et consignées dans `docs/rd/relecture-agent-prototypes-2026-11-10.md`, puis poursuivies le 11 novembre 2026 sur les 89 adresses de source encore non ouvertes dans `docs/rd/sources-ouvertes-2026-11-11.md`. Il est gardé par `outils/verifier-plan-complet.py`, `outils/verifier-sources-ouvertes.py` et leurs bancs.

> **Ce que la demande recouvre :** « Fais toute la R et D, l’innovation et la prospective, avec un plan complet sur l’ensemble du projet ». Le livrable demandé est donc une carte complète, ordonnancée et vérifiable de ce qui existe, de ce qui manque et de ce qui reste à décider.
>
> **Ce qu’elle ne peut pas recouvrir en une passe d’agent :** obtenir une expertise compétente sur les 14 fiches de domaines sensibles, mener des essais volontaires, trancher les options prospectives, confirmer le droit applicable, modifier la zone DNS, acheter du matériel pour ÉVA, juger le rendu à l’œil ou déclarer un rendu « professionnel ». Ces actes exigent des rôles, des signatures ou des moyens que le dépôt n’a pas. Le plan les nomme comme des portes, pas comme des cases cochées. Ils ne sont **pas** des lectures de texte à renvoyer à la personne : la lecture du contenu et la vérification des sources sont faites ici par l’agent.

## 1. Portée de la demande et limites

Le projet couvre six surfaces qui ne se remplacent pas : les contenus d’apprentissage, le site public, le simulateur, ÉVA, la gouvernance associative et la prospective. Une R&D « complète » au sens de ce dépôt signifie que chaque surface a une question, une source de vérité, un état, une prochaine action, des critères de sortie et une limite écrite — pas que chaque surface est achevée.

Règles reprises de `AGENTS.md` et de `docs/rd-innovation-continue.md` :

- distinguer le besoin observé, le fait sourcé, l’hypothèse de conception, le prototype, le contrôle automatique, **la relecture de contenu et des sources par l’agent**, l’expertise compétente, le jugement du rendu à l’œil et la décision humaine ;
- ne pas fabriquer de demande d’usager, de citation, d’expertise, de résultat d’essai ou de capacité démontrée ;
- ne pas promouvoir un statut éditorial pour rendre le catalogue plus flatteur ;
- ne pas écrire dans `docs/apprentissage/relectures.toml` à la place d’une personne ;
- ne pas renvoyer à la personne la lecture du contenu ou la vérification des sources : ce travail est à l’agent, consigné et daté dans `docs/rd/relecture-agent-prototypes.toml` ;
- ne pas ajouter de compte obligatoire, de télémétrie individuelle, de média distant automatique, de parcours forcé ni de promesse de prédiction ;
- laisser la publication, les dépenses, le droit, l’expertise de domaine et les priorités à des personnes compétentes ; la personne garde le jugement du rendu à l’œil.

**Hors périmètre de ce lot :** aucune modification de page HTML, de CSS, de JavaScript, du catalogue, du référentiel, du moteur du simulateur, des statuts, du portefeuille ou des workflows. Aucune URL externe nouvelle. Aucune écriture dans `docs/apprentissage/relectures.toml`, aucune promotion de statut éditorial, aucune décision A/B/C prise dans `docs/rd/decision-prospective.md`. Le lot de correction ajoute des fichiers de méthode sous `docs/rd/` et `outils/`, et marque les 81 pages de fiches `relu-par-agent` dans le manifeste d’empreintes, sans toucher aux fiches elles-mêmes.

## 2. Méthode et sources de vérité

| Source | Rôle dans le plan | Commande ou garde associée |
| --- | --- | --- |
| `AGENTS.md` | Consignes communes, distinction des preuves | lecture obligatoire avant chaque tâche |
| `docs/rd-innovation-continue.md` | Cycle de R&D en neuf étapes | `outils/verifier-rd-continue.py` |
| `docs/rd/portefeuille.toml` | 19 initiatives, états, priorités, critères de sortie | `outils/verifier-rd-continue.py`, `outils/etat-rd.py` |
| `docs/rd/journal.md` | Décisions structurantes et passations | `outils/verifier-fusions.py` |
| `docs/rd/avancees.toml` | Apprentissages réutilisables avec preuve, contrôle, limite et suite | `outils/construire-avancees.py`, `outils/verifier-rd-continue.py` |
| `docs/rd/avancees.md` | Rendu lisible des avancées | `outils/construire-avancees.py --verifier` |
| `docs/apprentissage/catalogue.toml` | 107 fiches, 15 domaines, statuts éditoriaux | `outils/auditer-prototypes.py`, `outils/construire-apprentissages.py` |
| `docs/apprentissage/referentiel.toml` | 106 sujets, statuts et exigences de preuve | `outils/construire-carte-lacunes.py` |
| `docs/rd/carte-lacunes.md` | Sujets sans fiche et cartes de sujet | `outils/construire-carte-lacunes.py --verifier` |
| `docs/rd/couverture-sujets.md` | Manques qualifiés sujet par sujet | `outils/construire-couverture-sujets.py --verifier` |
| `docs/rd/prospective-2027-2030.md` | Quatre scénarios, dix décisions sans regret | `outils/verifier-decision-prospective.py` |
| `docs/rd/decision-prospective.md` | Brief A/B/C, trace de décision vide | `outils/verifier-decision-prospective.py` |
| `docs/rd/prospective-lacunes-2027.md` | Scénarios de comblement des lacunes | `outils/construire-couverture-sujets.py --verifier` |
| `docs/rd/eva/plan.toml` | 12 phases d’ÉVA, conditions et hors-portée | `outils/verifier-plan-eva.py` |
| `docs/rd/eva/plan.md` | Rendu du plan ÉVA et de la mémoire | `outils/memoire-eva.py --verifier` |
| `docs/rd/empreintes-contenus.toml` | 519 unités sous empreinte après le lot de plan complet du projet du 11 novembre | `outils/relire-contenus.py` |
| `docs/rd/editions-relecture.toml` | Éditions relues par agent | `outils/relire-contenus.py` |
| `docs/rd/inventaire-controles.md` | Ce qui prouve que chaque contrôle peut échouer | `outils/verifier-inventaire-controles.py` |
| `docs/rd/relecture-agent-prototypes.toml` | 81 relectures de contenu par agent : constat, sources ouvertes, objections, limites | `outils/relecture-agent-prototypes.py --verifier` |
| `docs/rd/relecture-agent-prototypes-2026-11-10.md` | Rapport daté de la passe, 17 pages de source ouvertes | `outils/relecture-agent-prototypes.py --verifier` |
| `docs/rd/sources-ouvertes-2026-11-11.toml` | 89 adresses tentées, 83 contenus, 3 pages d’erreur servies et 3 erreurs de récupération | `outils/verifier-sources-ouvertes.py` |
| `docs/rd/sources-ouvertes-2026-11-11.md` | Rapport daté de la passe de sources et relevé des 89 tentatives | `outils/verifier-sources-ouvertes.py` |
| `docs/rd/sources-complement-2026-11-11.toml` | 6 dossiers, 16 lectures officielles datées et rattachées, 1 adresse sans page lue | `outils/verifier-sources-ouvertes.py` |
| `docs/rd/sources-complement-2026-11-11.md` | Rapport de la seconde passe du 11 novembre 2026 | `outils/verifier-sources-ouvertes.py` |
| `docs/rd/sources-ign-2026-11-11.toml` | Troisième passe : 17 tentatives, 13 HTTP 403, 10 pages officielles lues et datées, 2 confrontations | `outils/verifier-sources-ouvertes.py` |
| `docs/rd/sources-ign-2026-11-11.md` | Rapport de la troisième passe du 11 novembre 2026 | `outils/verifier-sources-ouvertes.py` |
| `docs/rd/plan-projet-complet-2026-11-11.toml` | Matrice : 579 fichiers en 11 zones après le lot site du 17 h 24 UTC, 19 initiatives, 39 actions, 9 portes, 5 horizons | `outils/verifier-plan-projet.py` |
| `docs/rd/plan-site-complet-2026-11-11.toml` | Matrice du plan du site : 19 surfaces, 10 reprises mesurées, 3 options de brainstorming, 6 sections et 4 portes distinctes | `outils/verifier-plan-site.py` |
| `docs/rd/plan-projet-complet-2026-11-11.md` | Plan complet du projet : R&D, innovation, prospective, couverture fichier par fichier | `outils/verifier-plan-projet.py` |
| `docs/rd/relecture-automatique.md` | Portée et limites de la sentinelle | `outils/verifier-relecture-contenus.py` |
| `docs/rd/paliers-affichage.toml` | Dette de format comptée | `outils/compter-paliers.py` |
| `docs/apprentissage/relectures.toml` | Registre des seules relectures humaines | `outils/registre-relecture.py` |

Le plan lui-même est une **sortie de synthèse**, pas une nouvelle source de vérité. En cas de divergence, les registres ci-dessus prévalent et le plan doit être régénéré ou corrigé, jamais invoqué pour les contredire.

## 3. État mesuré au 10 novembre 2026

**Les valeurs ci-dessous sont un instantané produit par `outils/etat-rd.py`, `outils/verifier-decision-prospective.py` et `outils/relire-contenus.py` le 10 novembre 2026.** Elles ne mesurent ni la qualité éditoriale, ni l’effet d’apprentissage, ni l’usage réel, ni la performance réseau.

| Repère | Valeur | Ce que cela ne dit pas |
| --- | --- | --- |
| Commit servi par Pages | `3b76f6d` (PR #288 fusionnée) | Que le rendu plaît à une personne |
| Initiatives R&D | 19 : 5 `a-cadrer`, 4 `a-tester`, 3 `a-valider`, 1 `bloquee`, 6 `en-cours` | Qu’une initiative est validée |
| Priorité P0 | 6 : `relire-les-44-prototypes`, `co-conception-et-essais`, `veille-savoirs-evolutifs`, `coordination-de-tous-les-agents`, `vote-distanciel-verifiable`, `confronter-une-affirmation-a-sa-source` | Que ces six avancent sans moyens humains |
| Prochaine revue du portefeuille | 2026-11-19 | Qu’une revue a déjà eu lieu en novembre |
| Fiches publiées | 107 dans 15 domaines | Qu’elles sont exactes, claires ou suffisantes |
| Prototypes à relire | 81 | Qu’une expertise compétente ou une relecture humaine a été consignée |
| Relectures humaines consignées | 0 dans `docs/apprentissage/relectures.toml` | Qu’une expertise compétente ou une validation humaine a eu lieu |
| Relecture de contenu par agent | 81 fiches lues, 17 pages le 10 novembre puis 89 adresses tentées le 11 novembre : 83 contenus, 6 sans contenu confrontable, 131 rattachements de sources ouvertes, 20 égalités simples sans écart ; seconde passe : 16 pages officielles lues, 1 adresse toujours sans page lue ; troisième passe : 10 pages de l’IGN lues, accueil IGN toujours en HTTP 403 | Que la vérité du monde, les 6 adresses sans contenu ou l’expertise de domaine sont établies |
| Fiches dont la revue est échue | 0 ; prochaine le 2027-01-05 pour `numerique-reagir-fraude` | Que les dates suffisent à garantir l’actualité |
| Sujets du référentiel | 106 ; 6 sans aucune fiche, dont 3 en `revue-experte` | Qu’il faut ouvrir ces six sujets sans relecture |
| Pages mesurées | 121 ; `apprendre.html` à 244,1 Kio mobile et 432,4 Kio grand écran | Le poids réellement servi sur le réseau |
| Unités sous empreinte | 519 : 132 relues par agent, 387 en dette initiale consignée après le lot de plan complet du 11 novembre | Que la dette de relecture de fond est résorbée |
| Avancées R&D | 102 avant le plan, 103 avec le plan, 104 avec la relecture d’agent, 105 avec la passe de sources, 106 avec le complément, 107 avec la troisième passe IGN, 108 avec le plan complet du projet | Qu’une avancée certifie un résultat d’usage |
| Décision prospective | En attente ; initiative `prospective-apprentissages-2030` reste `a-cadrer` | Que l’option B est adoptée |
| Boussole | 10 questions statiques, aucune collecte | Qu’elle aide à trouver une deuxième fiche |
| Essais navigateur | 13/13 et 0 violation axe sur les mesures d’agent | Qu’un lecteur d’écran ou une personne a validé le rendu |
| Dette de format | +2 règles et +1 bloc à 520 px, consignée dans `docs/rd/paliers-affichage.toml` | Que le palier a été adopté |

## 4. Cartographie des 19 initiatives

Chaque identifiant renvoie à une entrée de `docs/rd/portefeuille.toml`. Aucun état n’est modifié par ce plan.

| Initiative | Priorité | Phase / état | Porte qui bloque aujourd’hui |
| --- | --- | --- | --- |
| `relire-les-44-prototypes` | P0 | relecture / `a-valider` | Relecture de contenu faite par l’agent ; expertise compétente restante sur 14 fiches de domaines sensibles |
| `co-conception-et-essais` | P0 | cadrage / `a-cadrer` | Protocole, consentement et rôles à faire relire avant tout volontaire |
| `veille-savoirs-evolutifs` | P0 | maintien / `en-cours` | Relevé externe daté de janvier 2027, sources évolutives |
| `coordination-de-tous-les-agents` | P0 | mise-en-place / `en-cours` | Second agent et premier rapport planifié à examiner |
| `vote-distanciel-verifiable` | P0 | recherche / `a-cadrer` | Droit applicable, statuts, 18 relevés et six rôles de revue |
| `confronter-une-affirmation-a-sa-source` | P0 | prototype / `a-tester` | Indice de maintenance, jamais validation éditoriale |
| `optimisation-du-site` | P1 | essai / `a-tester` | Revue visuelle humaine, six apparences, iframe du simulateur |
| `poids-et-sobriete-numerique` | P1 | essai / `a-tester` | Octets réellement servis et revue visuelle des images |
| `coherence-textes-publics` | P1 | relecture / `a-valider` | Relecture de contenu de l’ouverture, des repères et de la Transparence à consigner par l’agent, puis décision associative |
| `indexation-et-lecteurs-de-contenu` | P1 | prototype / `a-tester` | Vérification dans les outils administrés par l’association |
| `direction-artistique-motion` | P1 | recherche / `en-cours` | Choix d’une des quatre chartes, puis storyboard de l’article 1 |
| `documentation-rd-eva` | P1 | recherche / `en-cours` | Rôle de relecture accepté, cycle cagnotte à faire relire |
| `autres-langues-et-contextes` | P1 | recherche / `a-cadrer` | Relectures locales par langue et région, licences audio |
| `mondes-3d-pluridisciplinaires` | P1 | conception / `a-cadrer` | Objectif pédagogique mesurable avant tout décor 3D |
| `prospective-apprentissages-2030` | P1 | conception / `a-cadrer` | Décision A/B/C à consigner avant le 31 janvier 2027 |
| `raccordement-domaine-www` | P1 | mise-en-place / `bloquee` | CNAME à poser par l’administrateur de la zone DNS |
| `cartographier-les-lacunes` | P1 | veille / `en-cours` | Six sujets sans fiche laissés visibles, pas comblés d’autorité |
| `ecouter-la-page` | P1 | prototype / `a-valider` | Relecture accessibilité et essai avec technologies d’assistance |
| `sources-fermees-et-registre-des-refus` | P1 | maintien / `en-cours` | Arbitrage éditorial sur `arts-composer-formes` : ajouter une page précise ou garder le portail assumé |

## 5. Plan par chantiers

Sept chantiers couvrent l’ensemble du projet. Chacun a un état, des livrables, des dépendances, des portes et un « ne pas faire » explicite. Les rôles sont des fonctions, pas des personnes nommées.

### Chantier A — Fondations de preuve et traçabilité

**Objectif :** que chaque édition, chaque contrôle et chaque apprentissage reste reprenable sans confusion entre un vert mécanique et une validation.

**État :** `outils/relire-contenus.py` garde 519 unités après le lot de plan complet du 11 novembre 2026 ; `docs/rd/inventaire-controles.md` classe 73 outils après le lot site du 17 h 24 UTC ; `outils/verifier-rd-continue.py` tient le portefeuille, le journal, les avancées, les sources refusées et la page de transparence ; `docs/rd/eva/plan.md` et `docs/rd/eva/plan.toml` gardent la mémoire d’ÉVA.

**Livrables à entretenir :** manifeste d’empreintes, registre des éditions, inventaire des contrôles, bancs de mutation, avancées avec limite d’au moins 120 caractères, index ÉVA à trois horizons.

**Portes :** `outils/relire-contenus.py`, `outils/verifier-inventaire-controles.py`, `outils/verifier-rd-continue.py`, `outils/memoire-eva.py --verifier`, `outils/verifier-plan-eva.py`, `outils/test_mutations_plan_complet.py`.

**Dépendances :** toute modification de `docs/rd/journal.md` ou de `docs/rd/avancees.toml` impose `outils/construire-avancees.py` puis `outils/memoire-eva.py --regenerer` en dernier.

**Ne pas faire :** signer une édition sans limite écrite ; transformer un constat en défaut ; déclarer un contrôle éprouvé sans banc ; écrire dans `docs/apprentissage/relectures.toml`.

### Chantier B — Contenus, relecture et lacunes

**Objectif :** rendre les 107 fiches et les 106 sujets vérifiables sans confondre quantité et qualité.

**État :** 81 prototypes à relire, 0 relecture humaine consignée, 6 sujets sans fiche dont 3 en `revue-experte`, 86 sujets à une seule fiche, 87 sans fiche de repère 3 ou 4. Trois fiches de repère 3 ou 4 ont été ajoutées le 6 novembre 2026 sans promotion de statut. **La relecture de contenu des 81 prototypes est désormais exécutée par l’agent** : champs lus, sources confrontées, 40 constats à trancher, registre et rapport au §9. Le 11 novembre 2026, les 89 adresses encore non ouvertes ont toutes été tentées : 83 premières tranches avec contenu, 3 pages d’erreur servies et 3 erreurs de récupération, sans correction de fiche ni promotion de statut.

**Livrables :** `docs/apprentissage/file-relecture.md`, `docs/apprentissage/paquets-relecture.md`, `docs/apprentissage/audit-automatique.md`, `docs/rd/carte-lacunes.md`, `docs/rd/couverture-sujets.md`, `docs/rd/prospective-lacunes-2027.md`, cartes de sujet pour `ecoute-prononciation`, `revenus-salaire-impots`, `securite-sciences` et `systemes-embarques`.

**Portes :** expertise compétente sur 14 fiches des domaines santé, droit et démarches, argent, politique publique ; `outils/relecture-agent-prototypes.py --verifier`, `outils/test_mutations_relecture_agent_prototypes.py`, `outils/verifier-sources-ouvertes.py`, `outils/test_mutations_sources_ouvertes.py`, `outils/file-relecture.py`, `outils/registre-relecture.py`, `outils/auditer-prototypes.py`, `outils/construire-carte-lacunes.py --verifier`, `outils/construire-couverture-sujets.py --verifier`, `outils/verifier-taux-dates.py`.

**Ne pas faire :** ouvrir les six sujets sensibles sans expertise compétente ; marquer « Relu » sans bloc humain dans `docs/apprentissage/relectures.toml` ; citer une page qui n’a pas été ouverte ; raconter une page d’erreur comme un contenu lu ; renvoyer à la personne une lecture de contenu déjà faite par l’agent ; atteindre le cap indicatif de `docs/apprentissage/plan-1000.toml` comme si c’était une preuve.

### Chantier C — Site, accessibilité, robustesse et sobriété

**Objectif :** que les pages restent lisibles, légères et utilisables quand le stockage, le réseau ou une fonction optionnelle échoue.

**État :** `outils/verifier-affichages.py`, `outils/verifier-apparences.py`, `outils/verifier-budgets-visuels.py`, `outils/verifier-graphismes.cjs`, `outils/verifier-accessibilite.cjs`, `outils/test-experience.cjs`, `outils/verifier-fichiers-servis.py`, `outils/verifier-publication.py` et `outils/verifier-securite.py` sont en place. Six apparences ont été mesurées le 7 novembre 2026 ; la dette de format est comptée dans `docs/rd/paliers-affichage.toml` ; sept constats locaux de densité d’image à 768 px / dpr 2 restent antérieurs et non traités.

**Livrables :** relevés datés, captures, en-têtes servis, budgets de poids, paliers déclarés, essais clavier, zoom, contraste renforcé et couleurs forcées.

**Portes :** revue visuelle humaine dans Chrome, lecteur d’écran, zoom natif, tactile sur pages types, iframe du simulateur, bref rendu clair avant application d’un thème sombre, mise à jour disponible du moteur amont examinée avant toute synchronisation, CNAME de `www.mrsc.fr` posé par l’administrateur DNS.

**Ne pas faire :** ajouter un palier non déclaré ; normaliser toutes les apostrophes CSS et JS ; supprimer globalement `main p > strong:first-child` ; confondre 0 débordement mesuré et rendu jugé ; déclarer le site universellement conforme.

### Chantier D — Innovation encadrée

**Objectif :** n’ajouter une forme nouvelle que si elle sert une tâche observable et reste réversible.

**État :** Boussole des savoirs (10 questions), passeport d’un résultat du simulateur, feuille d’impression, écoute de la page sur l’appareil, six apparences, Mondes anglais et trois concepts de mondes pluridisciplinaires, direction artistique à quatre chartes, ÉVA à 12 phases, vote distanciel à 18 relevés.

**Livrables :** briefs d’options, prototypes hors production, critères d’arrêt définis avant l’essai, équivalents texte, solution de repli, condition de retrait.

**Portes :** choix d’une seule charte avant storyboard ; décision A/B/C de `docs/rd/decision-prospective.md` ; relecture éditoriale, accessibilité, confidentialité et droit avant tout pilote ; aucun achat, aucune cagnotte, aucune collecte de bulletin réel sans décision associative et devis daté.

**Ne pas faire :** chatbot omniprésent, compte obligatoire, score de personne, progression forcée, primitive cryptographique locale inventée, monde 3D sans objectif pédagogique, conscience ou parité humaine présentées comme résultats ÉVA.

### Chantier E — Prospective et décision

**Objectif :** éprouver les choix du projet sous quatre futurs plausibles sans les transformer en prévision.

**État :** `docs/rd/prospective-2027-2030.md` décrit les scénarios A à D et dix décisions sans regret ; `docs/rd/decision-prospective.md` compare les options A, B et C ; la trace de décision est vide ; l’échéance de repli est le 31 janvier 2027 ; `outils/verifier-decision-prospective.py` recalcule huit repères internes à la date du brief.

**Livrables :** atelier de cadrage, sources primaires datées sur les thèmes retenus, un seul pilote borné ou l’option de ne rien construire, décision consignée avec date et instance, conditions de réexamen.

**Portes :** aucune probabilité inventée, aucune tendance présentée comme établie, aucun chiffre externe transposé au site sans source lue, aucune promotion publique du prototype avant relecture consignée.

**Ne pas faire :** choisir une option à la place de l’association ; transformer la Boussole en cursus ; instrumenter un pilote en ligne avant qu’un pilote papier ait révélé un besoin que seul le test en ligne peut trancher.

### Chantier F — Gouvernance, droit et essais avec des personnes

**Objectif :** séparer ce qui est techniquement prêt de ce qui est juridiquement ou humainement recevable.

**État :** `docs/rd/protocole-essais-usage.md` reste à faire relire ; `docs/rd/reglement-interieur-projet.md` est un squelette non adopté ; `docs/rd/statuts-revue-juridique.md`, `docs/rd/statuts-risques.toml`, `docs/rd/vote-distanciel-verifiable.md` et `docs/rd/vote-distanciel-dossier-deliberation.md` consignent des questions non tranchées ; `docs/apprentissage/relectures.toml` est vide.

**Livrables :** rôles attribués sans donnée personnelle, consentement et suppression des notes, objections des six rôles de revue du vote, confirmation de la version applicable des statuts, décision d’adoption du règlement intérieur par l’organe compétent.

**Portes :** expertise juridique, accessibilité, confidentialité, arbitrage explicite de l’association. Les essais initiaux du vote n’utilisent que des personnes et bulletins synthétiques.

**Ne pas faire :** transformer une question bloquée en règle par défaut ; recueillir un récit personnel, une réponse d’exercice ou une donnée de santé ; présenter une revue interne comme validation indépendante.

### Chantier G — Maintenance, veille et publication

**Objectif :** que ce qui est servi reste identifiable, daté et réparable après chaque fusion.

**État :** Pages sert `main` à `3b76f6d` ; le workflow de publication, la sonde d’en-têtes, la relecture à chaque édition et la veille éditoriale sont verts après #288 ; `outils/etat-rd.py` imprime l’état daté ; `outils/verifier-fusions.py` garde l’ordre du journal et l’absence de contenu perdu.

**Livrables :** runs de CI consignés, octets servis relus avec paramètre de cache, relevé externe de janvier 2027, revue mensuelle du portefeuille le 2026-11-19, revue des sources sensibles à 90 ou 180 jours.

**Portes :** ne déplacer `derniere_revue` qu’après une revue réellement effectuée et résumée ; ne pas confondre un lien vivant et un contenu à jour ; ne pas déclarer un déploiement réussi sans avoir relu les fichiers servis.

**Ne pas faire :** pousser une branche en croyant redéployer Pages ; fusionner sans avoir attendu les workflows de `main` ; supprimer une branche avant `outils/verifier-fusions.py --branches`.

## 6. Ordonnancement et horizons

| Horizon | Ce qui peut avancer sans nouvelle décision humaine | Ce qui reste bloqué |
| --- | --- | --- |
| **H0 — déjà servi** | `main` à `3b76f6d`, deux retraits de #288 en ligne, 3 repères sur l’accueil | Le jugement visuel du rendu |
| **H1 — immédiat, mécanique** | Relire le contenu et vérifier les sources, consigner la passe des 81 prototypes, tenir ce plan, régénérer `docs/rd/avancees.md` et la mémoire ÉVA, signer les éditions, éprouver `outils/verifier-plan-complet.py`, relancer `outils/etat-rd.py` | Aucune porte humaine n’est franchie pour autant |
| **H2 — portes à réunir** | Préparer les dossiers d’expertise, les planches, les comparatifs avant/après, les devis et les briefs | Expertise compétente sur 14 fiches, essais volontaires, avis juridique, DNS, charte graphique, décision A/B/C |
| **H3 — 2027** | Si l’option B est choisie : pilote papier de la Boussole, veille externe de janvier 2027, revue du portefeuille, revue des sources à 90 jours | Sans décision avant le 31 janvier 2027, rester sur l’option A et garder le prototype signalé |
| **H4 — 2027 à 2030** | Scénarios A à D, langues et contextes, mondes pluridisciplinaires, phases ÉVA conditionnelles, kit autonome | Toute capacité annoncée exige une démonstration datée ; les phases `conscience-et-corps` et `parite-humaine-des-delais` restent hors de portée tant que leur condition n’est pas remplie |

Dépendances structurantes : la relecture des contenus **par l’agent** précède toute promotion de statut, sans la garantir ; le protocole d’essais précède tout volontaire ; la décision prospective précède tout pilote ; le CNAME précède tout changement de canonique ; la comparaison amont du simulateur précède toute mise à jour du moteur ; l’avis juridique précède toute règle de vote ou d’adoption du règlement intérieur.

## 7. Portes de décision et rôles

| Porte | Rôle requis | Preuve attendue | Ce que la porte ne donne pas |
| --- | --- | --- | --- |
| Relecture de contenu et des sources | **Agent** | 81 `[[relecture]]` datées dans `docs/rd/relecture-agent-prototypes.toml`, rapport du 10 novembre 2026, puis 89 ouvertures du 11 novembre 2026 dans `docs/rd/sources-ouvertes-2026-11-11.toml` | Une expertise de domaine, un avis juridique ou une promotion de statut |
| Expertise de domaine et relecture consignée | Personne compétente du domaine | Bloc dans `docs/apprentissage/relectures.toml` | Une validation de tous les droits ou de l’usage |
| Décision éditoriale | Rôle éditorial de l’association | Décision datée dans `docs/rd/journal.md` | Une preuve d’apprentissage |
| Essai d’usage | Volontaires, accessibilité, confidentialité | Protocole relu, notes anonymes, date de suppression | Une mesure représentative |
| Droit et statuts | Personne compétente en droit | Version applicable, quorum, majorité, charte confirmés | Une autorisation de numériser un scrutin |
| Décision prospective | Instance décisionnaire de l’association | Option A, B ou C, date, conditions, réexamen | Un résultat de pilote |
| Domaine et HTTPS | Administrateur de la zone DNS | CNAME, certificat, canoniques, adresse visible | Une validation du contenu servi |
| Publication | Rôle éditorial humain | CI, Pages, octets servis relus | Une certification de qualité ou d’accessibilité |

## 8. Indicateurs de maintenance

Le projet suit des signaux de maintenance, pas des métriques d’audience : nombre d’unités sous empreinte, éditions signées, dette initiale consignée, initiatives par état, avancées avec limite, fiches par statut, sujets sans fiche, dates de revue, paliers déclarés, octets estimés et réellement servis, runs de CI, divergences de rendu au seuil. Aucun clic, aucune durée de visite, aucun profil, aucun score de personne n’est collecté.

Une absence de signal ne prouve pas une absence de besoin. Un contrôle vert ne prouve pas l’exactitude. Un lien vivant ne prouve pas l’actualité de la source. Ces trois phrases sont des garde-fous de lecture, pas des résultats.

## 9. Ce que ce lot fait réellement

Ce lot est un **lot de R&D de méthode et de synthèse**, pas une exécution de tous les chantiers :

1. il produit `docs/rd/plan-complet-rd-innovation-prospective.md`, qui cartographie les 19 initiatives, sept chantiers, cinq horizons et sept portes de décision ;
2. il ajoute `outils/verifier-plan-complet.py`, qui refuse un plan amputé d’une initiative, d’une section, d’un chemin local ou d’une formulation de validation inventée ;
3. il ajoute `outils/test_mutations_plan_complet.py`, qui plante cinq fautes dans une copie jetable et exige l’échec nommé ;
4. il tient `docs/rd/inventaire-controles.md` à jour, avec ses comptes recalculés ;
5. il consigne une entrée datée dans `docs/rd/journal.md` et une 103e avancée dans `docs/rd/avancees.toml`, puis régénère `docs/rd/avancees.md`, `docs/rd/eva/memoire.json`, `docs/rd/eva/graphe.md`, `docs/rd/eva/graphe.dot` et `docs/rd/eva/plan.md` ;
6. il signe chaque fichier modifié par `outils/relire-contenus.py --appliquer`, sans écrire dans `docs/apprentissage/relectures.toml` ;
7. il **exécute la relecture de contenu des 81 prototypes** (`docs/rd/relecture-agent-prototypes-2026-11-10.md`) : 11 champs lus par fiche, 17 pages de source ouvertes, 20 égalités simples recalculées sans écart, 40 constats à trancher ;
8. il ajoute `outils/relecture-agent-prototypes.py` et son banc de 10 mutations, tient `docs/rd/inventaire-controles.md`, `docs/rd/relecture-automatique.md`, `docs/apprentissage/grille-relecture.md` et `docs/rd/journal.md` à jour, et consigne une 104e avancée ;
9. il marque les 81 pages de fiches `relu-par-agent` avec une `[[edition]]` datée, un constat et une limite chacune, sans changer un statut éditorial ;
10. le 11 novembre 2026, il **tente les 89 adresses uniques de source encore non ouvertes** : 83 premières tranches avec contenu, 3 pages d’erreur servies et 3 erreurs de récupération, registre et rapport datés, `outils/verifier-sources-ouvertes.py` et son banc de 7 cas, 105e avancée ;
11. le 11 novembre 2026, en seconde passe, il **retente les 3 erreurs de récupération** et **traite les 3 pages d’erreur servies** : 16 pages officielles lues et datées pour 5 adresses, 1 adresse IGN restée en HTTP 403, aucun extrait consigné après coup, aucune fiche modifiée, garde étendue et banc porté à 9 cas, 106e avancée ;
12. le 11 novembre 2026, en troisième passe, il **retente l’accueil IGN** : 13 réponses HTTP 403, 1 redirection, 1 page d’erreur servie, 2 contenus génériques et **10 pages officielles de l’IGN lues et datées** sur `cartes.gouv.fr` et `data.geopf.fr`, confrontées aux deux fiches de géographie sans les modifier ; banc porté à 11 cas, 107e avancée ;
13. le 11 novembre 2026, en lot de plan complet, il **écrit 4 cartes de cadrage** pour les 4 sujets qui en étaient dépourvus, régénère `docs/rd/carte-lacunes.md`, `docs/rd/couverture-sujets.md` et `docs/rd/prospective-lacunes-2027.md`, produit `docs/rd/plan-projet-complet-2026-11-11.md` et sa matrice (575 fichiers, 11 zones, 19 initiatives, 39 actions, 9 portes), ajoute `outils/verifier-plan-projet.py` et son banc de 12 cas, câble l’étape CI et consigne une 108e avancée ; aucune fiche, aucun statut, aucune porte humaine franchie.

**Ce qu’il ne fait pas :** le lot du 10 novembre n’ouvrait pas les 89 adresses uniques de source restantes ; la passe du 11 les a toutes tentées sans transformer les 6 adresses sans contenu en sources lues. Ce travail ne juge pas la vérité du monde, ne juge pas la vérité du monde, ne remplace pas l’expertise compétente ni le regard de la personne sur le rendu, ne tranche aucune option A/B/C, ne modifie aucune page publique, ne change aucun état du portefeuille, ne déplace pas `derniere_revue`, ne pose pas de CNAME, ne met pas à jour le moteur du simulateur, ne collecte aucune donnée, ne déclare aucune validation humaine et ne transforme pas les scénarios prospectifs en prévision.

## 10. Tenir le plan à jour

Après toute modification d’une source de vérité, relancer dans cet ordre :

```sh
python3 outils/etat-rd.py
python3 outils/verifier-decision-prospective.py
python3 outils/verifier-rd-continue.py
python3 outils/relire-contenus.py
python3 outils/verifier-plan-complet.py
python3 outils/test_mutations_plan_complet.py
python3 outils/verifier-plan-projet.py
python3 outils/test_mutations_plan_projet.py
python3 outils/relecture-agent-prototypes.py --verifier
python3 outils/test_mutations_relecture_agent_prototypes.py
python3 outils/verifier-sources-ouvertes.py
python3 outils/test_mutations_sources_ouvertes.py
python3 outils/construire-avancees.py --verifier
python3 outils/memoire-eva.py --verifier
python3 outils/verifier-inventaire-controles.py
python3 outils/verifier-fusions.py
git diff --check
```

Si `outils/etat-rd.py` annonce de nouveaux comptes, corriger le tableau de la section 3 **en conservant la date de l’instantané**, puis consigner une nouvelle édition. Si une initiative change d’état, modifier d’abord `docs/rd/portefeuille.toml`, puis le journal, puis les avancées, puis régénérer la mémoire ÉVA en dernier. Ne jamais modifier `docs/rd/avancees.md`, `docs/rd/eva/plan.md`, `docs/rd/eva/graphe.md`, `docs/rd/eva/graphe.dot` ou `docs/rd/eva/memoire.json` à la main.

**Prochaine action prise par l’agent :** cette action a été exécutée le 11 novembre 2026 en seconde passe (`docs/rd/sources-complement-2026-11-11.md`) ; une troisième passe du même jour a retenté l’accueil IGN et consigné 10 pages officielles lues (`docs/rd/sources-ign-2026-11-11.md`) sans modifier les fiches. Retenter désormais l’accueil IGN à une date ultérieure et ne consigner un extrait de remplacement qu’après lecture effective, avant de modifier une fiche ; soumettre ensuite à l’association une seule décision à prendre : la revue du 2026-11-19 ou la décision prospective avant le 31 janvier 2027 ; consigner ce choix dans `docs/rd/journal.md`. L’expertise compétente, les essais volontaires et le jugement du rendu restent des actes de personnes, mais aucun d’eux ne consiste à demander à la personne de relire ce texte à la place de l’agent.

## 11. Couverture de l’ensemble du projet, fichier par fichier

Le présent plan cartographiait les 19 initiatives, sept chantiers, cinq horizons et sept portes ; il ne couvrait pas encore la totalité de l’arbre. Le lot du 11 novembre 2026 à 16 h 48 UTC ajoute `docs/rd/plan-projet-complet-2026-11-11.md` et `docs/rd/plan-projet-complet-2026-11-11.toml` : **575 fichiers présents à cet instant**, **579 après le lot site du 17 h 24 UTC**, répartis en **11 zones** (racine, `.agents`, `.claude`, `.github`, `.githooks`, `api`, `apprendre`, `assets`, `docs`, `outils`, `simulateur`), chacune avec sa source de vérité, sa garde, son état, sa prochaine action et sa limite. `outils/verifier-plan-projet.py` recalcule ces comptes à chaque lancement et refuse qu’une zone, une initiative, une section ou une porte disparaisse ; `outils/test_mutations_plan_projet.py` plante 12 fautes dans une copie complète.

Ce complément ne remplace pas le présent plan : il le prolonge. Il ajoute une matrice de **39 actions** en quatre états (`fait-agent`, `a-faire-agent`, `bloquee-humain`, `en-attente-date`), **9 portes humaines** maintenues ouvertes, les 4 cartes de cadrage manquantes et les 10 décisions prospectives sans regret avec leur condition de réexamen. Il ne comble aucun des 6 sujets sans fiche, ne franchit aucune porte et ne transforme pas les scénarios A à D en prévision. La revue du 2026-11-19 et la décision prospective avant le 31 janvier 2027 restent à l’association ; `docs/apprentissage/relectures.toml` reste vide.

Le lot du 17 h 24 UTC ajoute `docs/rd/plan-site-complet-2026-11-11.md`, sa matrice, `outils/verifier-plan-site.py` et son banc de 13 cas : il cartographie les 19 surfaces du site, mesure les 10 reprises de l’accueil et garde la refonte en une seule passe, sans modifier les fiches, les statuts, la feuille CSS, `sitemap.xml` ni `llms.txt`. `outils/verifier-plan-site.py` refuse qu’une redite revienne, qu’une section soit ajoutée, qu’une porte soit détournée ou qu’une classe CSS disparaisse ; les trois options du brainstorming et leurs critères d’arrêt restent écrites dans le plan du site. Les compteurs du projet sont recalculés à 579 fichiers.

Le lot du 11 novembre 2026 à 19 h 45 UTC réécrit l’ouverture et la présentation de l’association d’après `assets/documents/statuts-2020.pdf`, lu en entier (25 pages, empreinte sha256 identique à `docs/rd/statuts-matrice-tracabilite.toml`) : le H1 reprend les trois verbes de l’objet de l’article 2, le site est présenté comme un des outils que cet article prévoit, et les repères statutaires — slogan, territoires de vie, règle de vote, pépinière d’idées, valeurs, phases, format des propositions — sont désormais **exigés** par `outils/verifier-integration.py` et `outils/verifier-plan-site.py`, avec trois mutations nouvelles au banc d’intégration et une au banc du plan du site. Les plafonds d’affichage sont abaissés, jamais relevés : titre 73 → 63 caractères, H1 63/6/4 → 53/5/3.

**Suite :** retenter l’accueil IGN à une date ultérieure, reconfirmer les sources sensibles à 90 ou 180 jours, puis tenir cette carte et celle du site à jour après toute modification d’une source de vérité. Le regard à l’œil sur l’accueil refondu reste à une personne, sans lui renvoyer la lecture du texte. Aucune lecture de contenu n’est renvoyée à la personne.
