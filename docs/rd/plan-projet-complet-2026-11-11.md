# Plan complet du projet M.R.S.C. — R&D, innovation et prospective

**Lot du 11 novembre 2026, 16 h 48 UTC. Demande reprise mot pour mot : « continues et fais toute la R et D, l’innovation et la prospective, avec un plan complet sur l’ensemble du projet ».** Ce document n’est ni une décision, ni une validation, ni une clôture : c’est une carte datée, attribuée à l’agent, gardée par `outils/verifier-plan-projet.py` et par `outils/test_mutations_plan_projet.py`. Il complète `docs/rd/plan-complet-rd-innovation-prospective.md`, qui cartographiait les 19 initiatives et sept chantiers sans encore couvrir la totalité des fichiers du dépôt.

## 1. Portée, méthode et demande

**Besoin observé :** disposer d’une carte qui ne laisse aucun morceau du projet sans zone, sans source de vérité, sans garde, sans état, sans action et sans limite ; exécuter, sans renvoyer la lecture à la personne, tout ce qui est mécaniquement faisable par l’agent. **Fait mesuré :** l’arbre de travail contenait **575 fichiers** en 11 zones au moment de la rédaction (16 h 48 UTC), dont 552 fichiers suivis par Git au HEAD `3b76f6d` ; après le lot site du 17 h 24 UTC, le même comptage recalcule **579 fichiers** ; le 12 novembre 2026, l’ajout de la fiche sur la déclaration d’une fraude et de ses documents de R&D porte le compte à **589 fichiers**, puis à **590** avec le dossier des modules d’accessibilité. Le présent plan est tenu à jour par `outils/verifier-plan-projet.py`, qui confronte chaque zone à l’arbre réel. **Hypothèse de conception :** une couverture de fichiers est une condition nécessaire, pas suffisante, d’un plan complet. **Proposition :** la matrice `docs/rd/plan-projet-complet-2026-11-11.toml`, recalculée à chaque lancement.

Méthode : `orchestration-taches` pour cadrer et router, `conception-innovation` pour comparer les options et nommer « ne pas construire », `documentation-technique` pour tenir une carte vérifiable. Les sources de vérité restent `AGENTS.md`, `docs/rd/portefeuille.toml`, `docs/apprentissage/catalogue.toml`, `docs/apprentissage/referentiel.toml`, `docs/rd/journal.md`, `docs/rd/avancees.toml`, `docs/rd/empreintes-contenus.toml` et `docs/rd/eva/plan.toml`. Ce plan est une **sortie**, jamais une source : en cas de divergence, les registres prévalent.

**Ce que « toute » ne peut pas dire :** une expertise compétente sur les 14 fiches de domaines sensibles, des essais volontaires, un avis juridique, une décision A/B/C, la pose d’un CNAME, un achat de matériel pour ÉVA, un jugement du rendu à l’œil, une publication ou une certification. Ces actes sont des **portes** (§8), pas des cases cochées. Aucun d’eux ne consiste à demander à la personne de relire ce texte : la lecture de contenu et la vérification des sources sont à l’agent, déjà consignées dans `docs/rd/relecture-agent-prototypes.toml` et les trois registres du 11 novembre.

## 2. Inventaire exhaustif du projet

| Zone | Fichiers | Surface | Source de vérité | Garde | Prochaine action |
| --- | --- | --- | --- | --- | --- |
| `racine` | 22 | Site public et entrées du dépôt | `index.html` | `outils/verifier-site-statique.py` | Tenir les 121 pages servies et les 16 fichiers racine alignés |
| `.agents` | 28 | Bibliothèque de skills méthodologiques | `docs/rd/bibliotheque-skills.md` | `outils/verifier-rd-continue.py` | Ne charger que les cartes utiles, une à trois par tâche |
| `.claude` | 26 | Point d’entrée visuel et skills amont licenciées | `docs/rd/bibliotheque-skills.md` | `outils/verifier-rd-continue.py` | Vérifier les fichiers de provenance et les empreintes des skills amont |
| `.github` | 9 | CI, publication, veille et crochets | `docs/rd/inventaire-controles.md` | `outils/verifier-workflows.py` | Garder la sentinelle câblée sur chaque push et chaque PR |
| `.githooks` | 1 | Crochet local pre-commit | `docs/rd/relecture-automatique.md` | `outils/verifier-relecture-contenus.py` | Refuser toute édition non signée localement |
| `api` | 17 | API du simulateur, servie par Vercel | `api/donnees.py` | `outils/verifier-securite.py` | Séparer paramètres, modèle, calcul et résultat |
| `apprendre` | 107 | 107 pages de fiches générées | `docs/apprentissage/catalogue.toml` | `outils/construire-apprentissages.py` | Ne jamais éditer une page générée à la main |
| `assets` | 33 | CSS, JavaScript, images et documents | `assets/css/site.css` | `outils/verifier-integration.py` | Maintenir les relevés de poids et les variantes d’images |
| `docs` | 164 | R&D, apprentissage, gouvernance et prospective | `docs/rd/portefeuille.toml` | `outils/verifier-rd-continue.py` | Régénérer toute sortie dérivée depuis son générateur |
| `outils` | 141 | Gardes, générateurs et bancs de mutation | `outils/verifier-rd-continue.py` | `outils/verifier-inventaire-controles.py` | Tout nouvel outil doit entrer dans l’inventaire avec son banc |
| `simulateur` | 31 | Moteur embarqué et pages du simulateur | `simulateur/donnees_live.py` | `outils/construire-simulateur.py` | Comparer l’amont avant toute mise à jour du moteur |

**Total recalculé : 590 fichiers présents**, 11 zones, aucune zone sans garde (les 4 fichiers de plus que le relevé initial viennent du lot site du 17 h 24 UTC, les 11 suivants des lots fraude et accessibilité du 12 novembre 2026). Le comptage est fait sur le système de fichiers, hors historique Git, caches et brouillons de signature ; il fonctionne donc aussi dans la copie jetable du banc de mutation. `docs/apprentissage/relectures.toml` reste à 0 relecture humaine : aucun des 590 fichiers n’est une preuve de validation.

Ce que l’inventaire ne dit pas : qu’une ressource est utile, qu’une page est lue, qu’un contrôle est éprouvé sur toutes les fautes possibles, ou qu’un fichier suivi par Git est encore servi tel quel. Les six relevés binaires périmés de `docs/rd/inventaire-controles.md` restent à remesurer après publication.

## 3. Toute la R&D : initiatives et état mesuré

Les 19 initiatives viennent de `docs/rd/portefeuille.toml` ; aucun état, aucune priorité et aucune `derniere_revue` n’est modifié. La garde refuse qu’une initiative disparaisse de la matrice ou que son état y soit embelli.

| Initiative | Priorité | État | Chantier | Action portée par l’agent | Preuve |
| --- | --- | --- | --- | --- | --- |
| `relire-les-44-prototypes` | P0 | a-valider | B | Relire les 81 prototypes et consigner 131 rattachements de sources ouvertes | `docs/rd/relecture-agent-prototypes.toml` |
| `co-conception-et-essais` | P0 | a-cadrer | F | Préparer le protocole et les tâches B1 à B6 sans volontaire | `docs/rd/protocole-essais-usage.md` |
| `autres-langues-et-contextes` | P1 | a-cadrer | D | Cartographier langues, variétés et licences sans universaliser | `docs/rd/portefeuille.toml` |
| `mondes-3d-pluridisciplinaires` | P1 | a-cadrer | D | Poser un objectif pédagogique mesurable avant tout décor | `docs/rd/portefeuille.toml` |
| `veille-savoirs-evolutifs` | P0 | en-cours | G | Tenir le journal, les dates de revue et la veille datée | `docs/rd/journal.md` |
| `optimisation-du-site` | P1 | a-tester | C | Mesurer six apparences et la dette de format sans juger le rendu | `docs/rd/releve-affichages-2026-11-06.md` |
| `indexation-et-lecteurs-de-contenu` | P1 | a-tester | C | Vérifier l’indexation dans les outils administrés par l’association | `docs/rd/portefeuille.toml` |
| `direction-artistique-motion` | P1 | en-cours | D | Comparer quatre chartes sans en imposer une | `docs/rd/ligne-graphique.md` |
| `documentation-rd-eva` | P1 | en-cours | D | Tenir les 12 phases, la mémoire à trois horizons et le cycle de cagnotte | `docs/rd/eva/plan.toml` |
| `coordination-de-tous-les-agents` | P0 | en-cours | A | Garder la sentinelle, le journal, les avancées et les bancs | `AGENTS.md` |
| `coherence-textes-publics` | P1 | a-valider | B | Relire l’ouverture, les repères et la page Transparence | `docs/rd/rapport-coherence-editoriale-2026-10-13.md` |
| `vote-distanciel-verifiable` | P0 | a-cadrer | F | Consigner 18 relevés et six rôles de revue sans règle de droit | `docs/rd/vote-distanciel-accessibilite.toml` |
| `prospective-apprentissages-2030` | P1 | a-cadrer | E | Tenir quatre scénarios, trois options et dix décisions sans regret | `docs/rd/decision-prospective.md` |
| `raccordement-domaine-www` | P1 | bloquee | G | Laisser le CNAME à l’administrateur de la zone DNS | `vercel.json` |
| `poids-et-sobriete-numerique` | P1 | a-tester | C | Compter les octets estimés et les octets réellement servis | `docs/rd/poids-pages.md` |
| `cartographier-les-lacunes` | P1 | en-cours | B | Régénérer carte des lacunes, couverture qualifiée et relevé prospectif | `docs/rd/carte-lacunes.md` |
| `confronter-une-affirmation-a-sa-source` | P0 | a-tester | A | Tenter les 89 adresses, puis consigner trois passes datées | `docs/rd/sources-ouvertes-2026-11-11.toml` |
| `ecouter-la-page` | P1 | a-valider | D | Garder un repli texte et une écoute sur l’appareil | `docs/rd/inclusion-lecture-vocale.md` |
| `sources-fermees-et-registre-des-refus` | P1 | en-cours | B | Tenir sept sources tentées et refusées, arbitrer arts-composer-formes | `docs/apprentissage/sources-refusees.toml` |

Chronologie de la R&D réellement exécutée : le 10 novembre 2026, relecture de contenu des 81 prototypes (17 pages de source, 131 rattachements, 20 égalités sans écart) ; le 11 novembre en première passe, 89 adresses uniques tentées, 83 contenus consignés, 3 pages d’erreur servies et 3 erreurs de récupération ; en seconde passe, 16 pages officielles lues et datées, 2 remplacements exacts, 2 partiels, 1 contexte et 1 adresse sans page lue ; en troisième passe, 17 tentatives dont 13 HTTP 403, 10 pages de l’IGN lues et datées sur `cartes.gouv.fr` et `data.geopf.fr`, 2 confrontations avec les fiches de géographie, **avant toute modification de fiche**. Ce lot ajoute la quatrième brique : 4 cartes de cadrage, la régénération de `docs/rd/carte-lacunes.md`, `docs/rd/couverture-sujets.md` et `docs/rd/prospective-lacunes-2027.md`, puis la matrice et le présent plan.

État mesuré attendu après signature : **519 unités sous empreinte, 132 relues par agent, 387 en dette initiale consignée** au 16 h 48 UTC (les compteurs du lot site sont consignés séparément) ; 107 avancées avant ce lot, 108 après ; 81 prototypes toujours à relire, 40 verdicts `a-trancher`, 0 fiche modifiée, 0 statut promu, 0 URL externe nouvelle dans les livrables. `docs/rd/sources-ign-2026-11-11.md` garde l’accueil IGN en HTTP 403 : la retentative à une date ultérieure reste ouverte, car l’horloge du 11 novembre 2026 n’a pas changé.

## 4. Toute l’innovation encadrée

Chaque concept est une **hypothèse de valeur** avec son coût, son repli et sa porte. Aucun n’est promu, aucun n’est présenté comme un résultat d’usage.

| Concept | Valeur à éprouver | Coût ou risque principal | Repli ou forme bornée | Preuve | Porte |
| --- | --- | --- | --- | --- | --- |
| Boussole des savoirs | Trouver un second point d’entrée sans confondre une piste avec un cursus. | Relations à maintenir ; risque de redoubler les filtres existants. | Dix questions statiques, sans compte ni collecte. | `docs/rd/decision-prospective.md` | `essais-volontaires` |
| Passeport d’un résultat | Distinguer paramètres, version, hypothèses, calcul et limites. | Revue méthodologique non faite ; provenance distante non vérifiée. | Grille de lecture entièrement textuelle. | `docs/rd/prospective-2027-2030.md` | `avis-juridique` |
| Feuille d’impression et kit autonome | Lire ou imprimer une séquence même sans réseau continu. | Copie périmée et multiplication des versions. | Repli texte, aucune police distante. | `docs/rd/poids-et-sobriete-numerique.md` | `jugement-rendu` |
| Six apparences | Adapter l’affichage sans imposer un thème. | Dette de format non mesurée à tous les paliers. | Choix local et réversible, équivalent texte. | `docs/rd/releve-apparences-2026-11-07.md` | `jugement-rendu` |
| Écoute de la page | Entendre une fiche sur l’appareil sans service tiers. | Relecture accessibilité et essai avec technologies d’assistance. | Repli texte intégral. | `docs/rd/inclusion-lecture-vocale.md` | `essais-volontaires` |
| ÉVA, 12 phases | Mémoire à trois horizons et graphe navigable. | Deux phases explicitement hors de portée ; aucun achat de matériel. | Résumé court et pointeur long, aucune copie. | `docs/rd/eva/plan.toml` | `achat-materiel-eva` |
| Mondes anglais et trois concepts pluridisciplinaires | Relier des savoirs par une mécanique de jeu. | Objectif pédagogique mesurable encore absent. | Prototypes hors production, aucun décor 3D imposé. | `docs/rd/portefeuille.toml` | `expertise-domaine` |
| Vote distanciel vérifiable | Délibérer à distance sans bulletin réel. | Droit applicable, statuts et six rôles de revue non tranchés. | 18 relevés, personnes et bulletins synthétiques. | `docs/rd/vote-distanciel-accessibilite.toml` | `avis-juridique` |
| Ne rien construire | Consacrer le temps à la relecture des 81 prototypes. | Un besoin de navigation transversale pourrait rester non traité. | Option de référence, réversible sans action. | `docs/rd/decision-prospective.md` | `decision-prospective` |

Les 12 phases d’ÉVA restent déclarées dans `docs/rd/eva/plan.toml` ; `conscience-et-corps` et `parite-humaine-des-delais` y sont explicitement hors de portée. Les six apparences, la Boussole, le passeport, la feuille d’impression, l’écoute de la page et les mondes anglais existent comme prototypes bornés, sans compte obligatoire, sans télémétrie individuelle, sans média distant automatique et sans parcours forcé. L’option « ne rien construire » reste l’option de référence de `docs/rd/decision-prospective.md`.

## 5. Toute la prospective

`docs/rd/prospective-2027-2030.md` décrit quatre futurs plausibles : **A** le commun vérifiable, **B** l’assistant fluide aux preuves contestées, **C** le réseau intermittent, **D** l’archipel opaque. `docs/rd/decision-prospective.md` compare les options **A** (ne rien construire de plus), **B** (relire puis pilote papier) et **C** (pilote en ligne). La trace de décision est vide ; l’échéance de repli est le **31 janvier 2027** ; la revue du portefeuille est le **2026-11-19**. Aucune probabilité, aucune tendance établie, aucun chiffre externe transposé.

| Décision sans regret | Hypothèse de conception | Condition de réexamen ou d’arrêt | Preuve interne |
| --- | --- | --- | --- |
| Garder un noyau autonome | Une fiche atteint son objectif sans API, compte ou assistant. | Retirer toute amélioration qui rend un service obligatoire. | `docs/rd/prospective-2027-2030.md` |
| Tracer le statut et le contexte | Nature de l’énoncé, source, date, périmètre, statut et revue. | Reconfirmer la page à 90 ou 180 jours. | `docs/rd/relecture-automatique.md` |
| Séparer les couches | Sources, règles, paramètres, calcul et résultat distincts. | Pouvoir retirer la connexion distante sans travestir le résultat local. | `docs/rd/eva/plan.toml` |
| Personnaliser à la demande | Choix réversibles, locaux et compréhensibles. | Aucune inférence de compétence, de handicap ou de préférence. | `docs/rd/paliers-affichage.toml` |
| Ouvrir par petites unités relues | Alternative accessible, repli et retrait définis avant publication. | Une unité new sans porte de relecture est retirée. | `docs/apprentissage/grille-relecture.md` |
| Utiliser la maintenance comme signal | Dates de revue et versions plutôt que métriques d’engagement. | Aucune collecte d’audience ni profil de personne. | `outils/etat-rd.py` |
| Partir de ce que la personne sait déjà | Nommer un geste maîtrisé sans niveau scolaire ni score. | Aucune catégorisation de la personne. | `docs/apprentissage/catalogue.toml` |
| Rester identifiable sans service tiers | Icône servie avec le site, aucune police ni média distant. | Vérifier la provenance et l’empreinte des ressources. | `assets/css/site.css` |
| Servir juste assez, sans dégrader | Images adaptées, repli JPEG, aucun média automatique. | Ne retirer ni texte alternatif, ni clavier, ni zoom, ni repli sans JavaScript. | `docs/rd/poids-pages.md` |
| Ne jamais dépendre d’un seul canal | Fiche consultable et imprimable si le service distant tombe. | Chemin de repli explicite avec adresse et contact réels. | `docs/rd/prospective-2027-2030.md` |

Ces dix lignes sont des propositions de conception cohérentes avec les consignes du dépôt, pas des résultats démontrés auprès de visiteurs. `docs/rd/prospective-lacunes-2027.md` recalcule trois conséquences arithmétiques du catalogue : aucune échéance, aucune recommandation et aucune projection de fréquentation ne s’en déduit. La **décision** A/B/C appartient à l’instance décisionnaire de l’association ; l’agent prépare le dossier, il ne tranche pas.

## 6. Matrice d’exécution

La matrice distingue quatre états : `fait-agent` (exécuté et consigné), `a-faire-agent` (mécanique, encore ouvert), `bloquee-humain` (porte de personne), `en-attente-date` (une échéance réelle doit advenir). Comptes : **21 fait-agent, 3 a-faire-agent, 11 bloquee-humain, 4 en-attente-date**, soit 39 actions.

| Action | Type | État | Initiative | Dépendance | Preuve |
| --- | --- | --- | --- | --- | --- |
| `rd-relecture-81` | rd | fait-agent | `relire-les-44-prototypes` | aucune | `docs/rd/relecture-agent-prototypes.toml` |
| `rd-sources-89` | rd | fait-agent | `confronter-une-affirmation-a-sa-source` | `rd-relecture-81` | `docs/rd/sources-ouvertes-2026-11-11.toml` |
| `rd-sources-complement` | rd | fait-agent | `confronter-une-affirmation-a-sa-source` | `rd-sources-89` | `docs/rd/sources-complement-2026-11-11.toml` |
| `rd-sources-ign` | rd | fait-agent | `confronter-une-affirmation-a-sa-source` | `rd-sources-complement` | `docs/rd/sources-ign-2026-11-11.toml` |
| `rd-cartes-sujet` | rd | fait-agent | `cartographier-les-lacunes` | aucune | `docs/rd/carte-lacunes.md` |
| `rd-couverture-regeneree` | rd | fait-agent | `cartographier-les-lacunes` | `rd-cartes-sujet` | `docs/rd/couverture-sujets.md` |
| `rd-plan-complet` | rd | fait-agent | `coordination-de-tous-les-agents` | aucune | `docs/rd/plan-complet-rd-innovation-prospective.md` |
| `rd-plan-projet` | rd | fait-agent | `coordination-de-tous-les-agents` | `rd-plan-complet` | `docs/rd/plan-projet-complet-2026-11-11.toml` |
| `rd-sentinelle` | rd | fait-agent | `coordination-de-tous-les-agents` | aucune | `docs/rd/empreintes-contenus.toml` |
| `rd-eva` | rd | fait-agent | `documentation-rd-eva` | `rd-sentinelle` | `docs/rd/eva/memoire.json` |
| `rd-inventaire` | rd | fait-agent | `coordination-de-tous-les-agents` | aucune | `docs/rd/inventaire-controles.md` |
| `rd-journal-avancee` | rd | fait-agent | `coordination-de-tous-les-agents` | aucune | `docs/rd/avancees.toml` |
| `rd-veille-interne` | rd | fait-agent | `veille-savoirs-evolutifs` | aucune | `docs/rd/journal.md` |
| `rd-ign-date-ulterieure` | rd | en-attente-date | `confronter-une-affirmation-a-sa-source` | `rd-sources-ign` | `docs/rd/sources-ign-2026-11-11.md` |
| `rd-revue-portefeuille` | rd | en-attente-date | `veille-savoirs-evolutifs` | aucune | `docs/rd/portefeuille.toml` |
| `rd-veille-janvier-2027` | rd | en-attente-date | `veille-savoirs-evolutifs` | aucune | `docs/rd/veille-2026-10-17.md` |
| `rd-revue-sources-90j` | rd | a-faire-agent | `sources-fermees-et-registre-des-refus` | `rd-sources-89` | `docs/rd/sources-ouvertes-2026-11-11.md` |
| `rd-coherence-textes` | rd | a-faire-agent | `coherence-textes-publics` | aucune | `docs/rd/rapport-coherence-editoriale-2026-10-13.md` |
| `rd-expertise-14` | rd | bloquee-humain | `relire-les-44-prototypes` | `rd-relecture-81` | `docs/apprentissage/grille-relecture.md` |
| `rd-essais-volontaires` | rd | bloquee-humain | `co-conception-et-essais` | aucune | `docs/rd/protocole-essais-usage.md` |
| `rd-avis-juridique` | rd | bloquee-humain | `vote-distanciel-verifiable` | aucune | `docs/rd/statuts-revue-juridique.md` |
| `rd-dns` | rd | bloquee-humain | `raccordement-domaine-www` | aucune | `vercel.json` |
| `rd-publication` | rd | bloquee-humain | `coordination-de-tous-les-agents` | aucune | `docs/rd/relecture-automatique.md` |
| `in-boussole` | innovation | fait-agent | `prospective-apprentissages-2030` | aucune | `docs/rd/decision-prospective.md` |
| `in-passeport` | innovation | fait-agent | `confronter-une-affirmation-a-sa-source` | aucune | `docs/rd/prospective-2027-2030.md` |
| `in-six-apparences` | innovation | fait-agent | `optimisation-du-site` | aucune | `docs/rd/releve-apparences-2026-11-07.md` |
| `in-eva-12-phases` | innovation | fait-agent | `documentation-rd-eva` | aucune | `docs/rd/eva/plan.toml` |
| `in-charte-unique` | innovation | bloquee-humain | `direction-artistique-motion` | aucune | `docs/rd/ligne-graphique.md` |
| `in-mondes-3d` | innovation | bloquee-humain | `mondes-3d-pluridisciplinaires` | aucune | `docs/rd/portefeuille.toml` |
| `in-materiel-eva` | innovation | bloquee-humain | `documentation-rd-eva` | aucune | `docs/rd/materiel-spark-serveur-dons.md` |
| `in-rendu-oeil` | innovation | bloquee-humain | `optimisation-du-site` | aucune | `docs/rd/releve-affichages-2026-11-06.md` |
| `pr-scenarios-a-d` | prospective | fait-agent | `prospective-apprentissages-2030` | aucune | `docs/rd/prospective-2027-2030.md` |
| `pr-options-abc` | prospective | fait-agent | `prospective-apprentissages-2030` | `pr-scenarios-a-d` | `docs/rd/decision-prospective.md` |
| `pr-10-decisions` | prospective | fait-agent | `prospective-apprentissages-2030` | aucune | `docs/rd/prospective-2027-2030.md` |
| `pr-lacunes-2027` | prospective | fait-agent | `cartographier-les-lacunes` | `rd-couverture-regeneree` | `docs/rd/prospective-lacunes-2027.md` |
| `pr-decision-abc` | prospective | bloquee-humain | `prospective-apprentissages-2030` | `pr-options-abc` | `docs/rd/decision-prospective.md` |
| `pr-pilote-papier` | prospective | en-attente-date | `prospective-apprentissages-2030` | `pr-decision-abc` | `docs/rd/protocole-essais-usage.md` |
| `pr-langues-contextes` | prospective | bloquee-humain | `autres-langues-et-contextes` | aucune | `docs/rd/portefeuille.toml` |
| `pr-kit-autonome` | prospective | a-faire-agent | `poids-et-sobriete-numerique` | aucune | `docs/rd/poids-et-sobriete-numerique.md` |

Chaque action porte un critère de sortie d’au moins 20 caractères et une limite d’au moins 30 caractères dans `docs/rd/plan-projet-complet-2026-11-11.toml`. Une action `fait-agent` ne peut citer aucune porte humaine : la garde refuse qu’un blocage soit raconté comme franchi. Une action en attente de date ne peut pas être marquée faite sans qu’une date réelle ait changé.

## 7. Ordonnancement et dépendances

| Horizon | Fenêtre | Ce qui peut avancer | Ce qui reste bloqué |
| --- | --- | --- | --- |
| `H0` | déjà servi | main à 3b76f6d, PR #288 fusionnée, 121 pages mesurées | Le jugement visuel du rendu reste ouvert. |
| `H1` | 11 novembre 2026, immédiat et mécanique | Ce lot : 4 cartes de cadrage, matrice exhaustive, garde, banc, plan du projet, signatures et batterie | Aucune porte humaine n’est franchie. |
| `H2` | portes à réunir | Dossiers d’expertise, planches, comparatifs, devis et briefs préparés par l’agent | Expertise, essais, avis juridique, DNS, charte et décision A/B/C restent à des personnes. |
| `H3` | 2027, sous condition de décision | Si l’option B est choisie : pilote papier, veille de janvier 2027, revue des sources à 90 jours | Sans décision avant le 31 janvier 2027, rester sur l’option A. |
| `H4` | 2027 à 2030 | Scénarios A à D, langues et contextes, mondes pluridisciplinaires, phases ÉVA conditionnelles, kit autonome | Toute capacité annoncée exige une démonstration datée. |

Dépendances structurantes : la relecture de contenu **par l’agent** précède toute promotion de statut sans la garantir ; la carte de cadrage précède la fiche ; le protocole d’essais précède tout volontaire ; la **décision** prospective précède tout pilote ; le CNAME précède tout changement de canonique ; la comparaison amont du simulateur précède toute mise à jour du moteur ; l’avis juridique précède toute règle de vote ; la revue du **2026-11-19** précède tout déplacement de `derniere_revue`. Rien dans ce lot ne pousse, ne fusionne, ne déploie ni ne certifie.

## 8. Portes de décision et rôles

| Porte | Rôle requis | Preuve attendue | Ce que la porte ne donne pas |
| --- | --- | --- | --- |
| `expertise-domaine` | Personne compétente du domaine | `docs/apprentissage/relectures.toml` | Une relecture compétente ne vaut ni avis juridique ni preuve d’apprentissage. |
| `essais-volontaires` | Volontaires, accessibilité et confidentialité | `docs/rd/protocole-essais-usage.md` | Cinq volontaires ne donnent pas une mesure représentative. |
| `avis-juridique` | Personne compétente en droit | `docs/rd/statuts-revue-juridique.md` | Un avis ne numérise pas un scrutin et ne confirme pas une version de statuts. |
| `decision-editoriale` | Rôle éditorial de l’association | `docs/rd/journal.md` | Une décision éditoriale n’est pas une preuve de qualité du contenu. |
| `decision-prospective` | Instance décisionnaire de l’association | `docs/rd/decision-prospective.md` | Le choix d’une option n’est pas un résultat de pilote. |
| `dns-www` | Administrateur de la zone DNS | `vercel.json` | Un CNAME posé ne valide pas le contenu servi. |
| `achat-materiel-eva` | Décision associative et devis daté | `docs/rd/materiel-spark-serveur-dons.md` | Aucun achat, aucune cagnotte et aucune collecte sans décision. |
| `jugement-rendu` | Regard de la personne sur le rendu | `docs/rd/releve-affichages-2026-11-06.md` | Zéro débordement mesuré ne dit pas que le rendu est jugé bon. |
| `publication` | Rôle éditorial humain | `docs/rd/relecture-automatique.md` | Un déploiement réussi ne certifie ni la qualité ni l’accessibilité. |

Les neuf portes restent `ouvertes` dans la matrice. `docs/apprentissage/relectures.toml` est le seul registre des relectures humaines : la garde vérifie qu’il est vide et qu’aucune carte d’agent n’y a écrit. Le jugement du rendu à l’œil reste à la personne, sans texte à relire de sa part.

## 9. Ce que ce lot a réellement fait

1. Il écrit **4 cartes de cadrage** pour les 4 sujets encore sans carte (`securite-electricite`, `droits-travail`, `premiers-secours`, `activite-corps-securite`), sans fiche, sans source externe nouvelle, sans consigne de sécurité, de santé ou de droit, sans URL et sans promotion de statut.
2. Il régénère `docs/rd/carte-lacunes.md`, `docs/rd/couverture-sujets.md` et `docs/rd/prospective-lacunes-2027.md` : 8 cartes de sujet, 0 manque `sans-carte-de-sujet`, 6 sujets toujours sans fiche.
3. Il ajoute `outils/verifier-plan-projet.py` et `outils/test_mutations_plan_projet.py` : 12 situations plantées dans une copie complète, dont une zone retirée, un compte falsifié et une porte humaine racontée comme franchie.
4. Il câble ces deux commandes dans `.github/workflows/verification.yml` et tient `docs/rd/inventaire-controles.md` à jour avec ses comptes recalculés.
5. Il produit `docs/rd/plan-projet-complet-2026-11-11.toml` et le présent plan, qui couvrent 590 fichiers, 11 zones, 19 initiatives, 39 actions, 9 portes et 5 horizons.
6. Il amende `docs/rd/plan-complet-rd-innovation-prospective.md`, `docs/rd/relecture-automatique.md`, `docs/rd/journal.md`, `docs/rd/avancees.toml`, `docs/rd/avancees.md` et la mémoire ÉVA, puis signe chaque unité modifiée par `outils/relire-contenus.py --appliquer`.
7. Il relance les gardes concernées, la batterie complète reconstruite depuis le workflow et `git diff --check`, sans commit, sans poussage, sans fusion, sans déploiement et sans certification.

**Ce qu’il ne fait pas :** il ne résout pas `www.ign.fr/`, ne rédige aucune fiche, ne comble aucun des 6 sujets sans fiche, ne réunit aucune expertise, ne mène aucun essai, ne tranche aucune option A/B/C, ne modifiait, à 16 h 48 UTC, aucune page HTML, CSS ou JavaScript — la refonte de `index.html` du 17 h 24 UTC est un lot distinct, consigné dans `docs/rd/plan-site-complet-2026-11-11.md` —, ne touche ni au catalogue, ni au référentiel, ni aux statuts, ni au portefeuille, ni aux workflows existants autres que l’ajout d’une étape de garde. Il ne transforme pas les scénarios en prévision et ne dit pas que la R&D est achevée.

## 10. Limites, entretien et prochaine action

Limites : une carte de 590 fichiers ne couvre ni tous les besoins, ni la vérité du monde, ni l’effet d’apprentissage ; un contrôle vert ne prouve pas l’exactitude ; un lien vivant ne prouve pas l’actualité ; 387 unités restaient en dette initiale consignée au 16 h 48 UTC ; 14 fiches attendent une expertise compétente ; 0 relecture humaine est consignée ; les 4 nouvelles cartes sont des cadrages internes sans source primaire de domaine. Aucune validation humaine, aucun avis juridique, aucun essai volontaire, aucun rendu visuel validé, aucune publication à 16 h 48 UTC : la publication demandée par la personne plus tard le 11 novembre 2026 porte sur le lot site et est consignée dans `docs/rd/journal.md`.

Après toute modification d’une source de vérité, relancer dans cet ordre :

```sh
python3 outils/verifier-plan-projet.py
python3 outils/test_mutations_plan_projet.py
python3 outils/verifier-plan-complet.py
python3 outils/verifier-sources-ouvertes.py
python3 outils/construire-carte-lacunes.py --verifier
python3 outils/construire-couverture-sujets.py --verifier
python3 outils/relire-contenus.py
python3 outils/construire-avancees.py --verifier
python3 outils/memoire-eva.py --verifier
python3 outils/verifier-inventaire-controles.py
git diff --check
```

**Prochaine action prise par l’agent :** retenter `www.ign.fr/` à une date ultérieure, puis consigner toute page de l’Institut réellement lue avec sa date et son repère avant de modifier l’une des deux fiches de géographie ; reconfirmer les sources sensibles à 90 ou 180 jours ; préparer, sans les franchir, les dossiers des neuf portes de la section 8. La revue du **2026-11-19** et la **décision** prospective avant le **31 janvier 2027** restent à l’association. Aucune lecture de contenu ni vérification de source n’est renvoyée à la personne.
