# R&D — parcours d’apprentissage accessibles du M.R.S.C

**État au 8 octobre 2026 — prototypes partiels, relectures à poursuivre.** Le catalogue de travail contient 35 fiches suivies dans 15 domaines : 26 entrées du corpus initial et 9 fiches explicitement marquées « Prototype à relire ». Ces prototypes comprennent trois nouveaux points d’entrée en mathématiques (conversions, moyenne, estimation), une fiche de lecture critique d’étude, et une première série de cinq fiches sur les fonctions d’un ordinateur, une boucle comparée en Python et JavaScript, les circuits ouverts/fermés, un capteur électronique et le choix d’une source publique. Ce ne sont ni neuf fiches validées ni une couverture complète de ces sujets. Les sujets mathématiques restent partiels, pas des cours complets de mesures ou de statistiques. Cette version ne couvre pas le parcours visé, des bases du CP aux études supérieures, spécialités professionnelles et recherche doctorale. Le corpus reste incomplet, à relire et à tester ; il ne constitue ni un programme officiel ni une formation certifiante. Aucun test avec des personnes apprenantes ni essai visuel complet en navigateur réel n’a encore été documenté.

## 1. Intention

Créer un accès aux savoirs pour les personnes qui ont quitté l’école tôt, sont entrées rapidement dans le travail, ont appris en situation, ont eu une expérience scolaire difficile ou souhaitent simplement reprendre une notion. Le parcours scolaire n’est pas une mesure de la capacité à apprendre. Une expérience professionnelle, familiale, associative ou quotidienne contient déjà des savoir-faire qui peuvent servir de point d’appui.

Le site ne doit pas opposer les personnes aux enseignants ni présenter une opinion politique comme un fait établi. Il peut reconnaître que certains parcours scolaires ne conviennent pas à tout le monde, sans généraliser sur tous les élèves, tous les professeurs ou toutes les écoles. La cible éditoriale est l’autonomie, la compréhension et la possibilité de vérifier — pas le jugement.

## 2. Résultats de la recherche documentaire

- **Le socle scolaire français progresse par cycles.** Le ministère distingue notamment le cycle 2 (apprentissages fondamentaux), le cycle 3 (consolidation, du CM1 à la 6e) et le cycle 4 (approfondissements, de la 5e à la 3e). Le socle inclut aussi des méthodes pour apprendre, l’évaluation des informations et la capacité à raisonner. Ces cycles peuvent aider à ranger les notions ; ils ne sont pas une échelle de valeur des adultes. [Ministère de l’Éducation nationale — socle commun](https://www.education.gouv.fr/bo/15/Hebdo17/MENE1506516D.htm).
- **Des compétences de base s’apprennent aussi en contexte professionnel.** Le référentiel CléA couvre la communication en français, le raisonnement mathématique, le numérique, le travail en équipe, l’autonomie, la capacité à apprendre et les règles élémentaires de santé/sécurité/environnement. Il fournit des thèmes pertinents pour un parcours destiné aux adultes ; M.R.S.C ne délivre pas CléA et ne doit pas laisser entendre que ses fiches préparent à l’obtention du certificat. [Certificat CléA — les domaines du socle](https://www.certificat-clea.fr/employeurs/le-socle/).
- **Les publics adultes ont des besoins variés.** L’ANLCI souligne l’intérêt d’adapter les approches et les outils à la diversité des personnes qui apprennent les compétences de base. Elle présente aussi des démarches qui relient apprentissage et situation de travail. La page M.R.S.C reprend ces orientations sous forme de situations de vie et de travail, sans prétendre remplacer l’accompagnement d’un professionnel. [ANLCI — se former et accompagner](https://www.anlci.gouv.fr/comment-agir/je-me-forme/) et [développer les compétences de base en situation de travail](https://www.anlci.gouv.fr/app/uploads/2025/04/20250910_Prez-webinaire-AFEST.pdf).
- **L’accessibilité ne se réduit pas à la conformité technique.** WCAG 2.2 organise les critères autour de quatre principes — perceptible, utilisable, compréhensible et robuste — et recommande des tests avec des personnes en situation de handicap. Le W3C rappelle qu’une conformité à un niveau donné ne répond pas à tous les besoins cognitifs ou d’apprentissage. [W3C — WCAG 2.2](https://www.w3.org/TR/WCAG22/) et [guide d’interprétation](https://www.w3.org/WAI/WCAG22/Understanding/intro).
- **Les repères français et les domaines de cours ne suffisent pas à couvrir les spécialités internationales.** La classification ISCED de l’Institut de statistique de l’UNESCO distingue des niveaux de programmes et 11 grands domaines d’études (ISCED-F 2013). Elle peut servir de contrôle de périmètre, sans être utilisée pour classer une personne ni comme équivalence directe entre diplômes nationaux. [UNESCO UIS — présentation d’ISCED et d’ISCED-F](https://isced.uis.unesco.org/about/) et [questions-réponses sur la classification](https://isced.uis.unesco.org/q-and-a/).

## 3. Architecture éditoriale retenue

### Deux axes à ne pas confondre : difficulté d’une fiche et horizon de connaissance

Les quatre repères visibles dans le catalogue servent à trouver une explication ou un exercice d’une complexité adaptée. Ils ne représentent ni des classes scolaires, ni des niveaux de diplôme. Une personne peut choisir un repère différent selon la matière et commencer directement par un approfondissement.

| Repère de la fiche | Exemples de capacités | Règle d’usage |
| --- | --- | --- |
| 1 — Reprendre les bases | Comprendre une consigne, lire un nombre, repérer une information | Entrée libre, sans test ni justification. |
| 2 — Consolider | Relier plusieurs étapes, appliquer une méthode à un exemple familier | Chaque compétence reste indépendante des autres. |
| 3 — Raisonner | Comparer, expliquer une démarche, vérifier une source ou un résultat | Le repère peut différer selon la matière. |
| 4 — Approfondir et transférer | Modéliser, examiner les limites, analyser une méthode ou transférer une notion | Accessible à toute personne qui le souhaite ; ce n’est pas une sélection. |

En parallèle, **l’horizon de couverture des contenus visés** va des premières bases enseignées dès le CP, à travers les cycles primaire, collège, lycée général/technologique/professionnel et les formations de spécialité, jusqu’aux études supérieures, aux masters et à la recherche doctorale. Les référentiels varient selon les pays, les disciplines et les voies : les parcours réels ne se réduisent pas à une suite unique. Les repères de difficulté servent l’orientation dans le catalogue ; ils ne définissent jamais le potentiel d’une personne.

L’objectif de couverture est de construire progressivement des fiches et des cours de ces horizons, dans toutes les matières et spécialités identifiées. **Ce n’est pas l’état actuel du catalogue** : les contenus manquants doivent rester visibles, et aucune génération ne doit faire croire que la couverture est complète.

La classification UNESCO ISCED/ISCED-F sert ici de grille de contrôle des niveaux de programmes et des champs disciplinaires, pas de test, de diplôme M.R.S.C ou d’équivalence automatique avec le système français.

### Matières et situations

La carte contient maintenant 15 domaines de travail : les 13 domaines initiaux, un domaine consacré aux études supérieures, aux spécialités et à la recherche, et un domaine d’informatique, algorithmique et programmation. Le domaine supérieur suit les 11 grands champs ISCED-F de l’UNESCO et ajoute des thèmes transversaux de méthodologie, lecture critique et intégrité de la recherche. Ce croisement sert à repérer les champs encore sans fiches avancées ; il ne prétend pas décrire toutes les sous-spécialités d’un seul coup.

### Première couverture informatique, programmation, électricité et électronique

Le référentiel compte désormais 15 domaines de travail, dont un nouveau domaine « Informatique, algorithmique et langages de programmation » doté de dix sujets suivis. Les sujets liés aux circuits, aux systèmes électroniques et aux sources publiques sont rattachés aux domaines de sciences/techniques et de citoyenneté déjà présents, afin de garder une seule entrée par notion et d’éviter les doublons. Le plan répartit maintenant sa cible de travail de 1 000 fiches entre les 15 domaines ; ses quotas totalisent toujours 1 000, mais ne constituent ni un engagement de production ni un indicateur de couverture validée.

Les cinq nouveaux prototypes sont : `info-ordinateur-fonctions` (rôles d’un ordinateur), `prog-comparer-langages` (même boucle représentée en Python et JavaScript), `tech-circuit-ouvert-ferme` (circuit ouvert et fermé), `tech-electronique-capteur` (mesure et capteur), `civ-choisir-source-publique` (choisir un portail selon la question). Chacun porte le statut « Prototype à relire ». Leurs descriptions, exercices, analogies et exemples sont des propositions rédactionnelles indépendantes ; les liens de sources restent facultatifs et les autorisations/licences de réutilisation des pages liées ne sont pas déclarées vérifiées. Aucune fiche ne revendique une propriété de M.R.S.C sur le contenu des sources.

La fiche de programmation contient deux extraits textuels courts, balisés comme exemples de code, échappés lors du rendu et accompagnés d’explications ; ils ne sont pas exécutés dans la page. Le 8 octobre 2026, les versions présentes dans le catalogue ont été lancées séparément avec Python 3 et Node.js ; les deux se sont terminées sans erreur et ont produit les mêmes trois lignes. Ce contrôle ponctuel ne remplace ni la relecture informatique indépendante, ni des vérifications dans d’autres environnements ou versions. Leur affichage accessible doit encore être vérifié au clavier, au lecteur d’écran, en petit écran, au zoom et en contraste forcé. Les essais d’interface restent statiques, sans navigateur réel.

Ces prototypes donnent seulement quelques points d’entrée. Le backlog informatique reste notamment ouvert sur la représentation des données, les systèmes d’exploitation et les fichiers, les réseaux, les bases de données et le Web, le test et le débogage, la conception collective et les licences, ainsi que les systèmes embarqués. En électricité/électronique, la sécurité, les protections, les signaux, les composants, le diagnostic et les interventions réelles nécessitent une progression et des relectures adaptées ; aucune fiche n’invite à manipuler une installation sous tension. La nouvelle page de liens utiles et le registre `docs/apprentissage/sources-utilite-publique.md` proposent une sélection de portails par rôle, avec date de consultation, portée et conditions de réutilisation à vérifier ; elle n’est pas exhaustive et les liens ne sont pas requis pour apprendre.

### Cap éditorial de 1 000 fiches

La priorité de développement est de viser **1 000 fiches distinctes**, autonomes, valorisantes, relues et maintenues à jour. `docs/apprentissage/plan-1000.toml` distribue cette cible entre les 15 domaines, des horizons de contenus allant des premières bases aux études doctorales, et les quatre repères de difficulté. Les tranches cumulées de 100, 250, 500, 750 et 1 000 sont des étapes de planification sans échéance promise. Le générateur maintient le bilan dans `docs/apprentissage/objectif-1000.md`.

Ce cap est un objectif de travail, pas le nombre de cours actuellement publiés et pas une promesse d’exhaustivité. Le catalogue de travail suit 35 entrées : 26 fiches du corpus initial et 9 prototypes explicitement à relire ; le nombre de fiches ayant franchi l’ensemble des contrôles indépendants n’est pas encore suivi. Une fiche ne comptera durablement vers l’objectif que si elle apporte un objectif d’apprentissage distinct, garde son enseignement essentiel sur le site sans lien ou compte tiers obligatoire et franchit les contrôles de fond, de droits, d’accessibilité et d’entretien. Les variantes, traductions et répétitions ne gonflent pas le total. Les retours et l’expertise pourront faire évoluer les quotas.

Le référentiel détaillé (`docs/apprentissage/referentiel.toml`) marque chaque sujet comme fiche disponible, couverture partielle, à créer ou à soumettre à une relecture spécialisée. La carte générée (`docs/couverture-savoirs-base.md`) nomme explicitement les lacunes. Les 26 fiches du corpus initial et les 9 prototypes constituent uniquement un premier corpus incomplet, qui ne couvre ni tous les âges ni tous les domaines. `recherche-lire-etude` est le premier contenu du domaine supérieur/recherche ; son sujet reste partiel. Les trois prototypes mathématiques ne couvrent chacun qu’un point d’entrée en conversions, moyenne ou estimation. Les cinq prototypes informatiques, techniques et civiques sont des points de départ, non des cours complets. Toutes ces fiches demandent une relecture avant toute conclusion sur leur qualité pédagogique ou scientifique.

Chaque ressource est pensée dans le même ordre : **situation connue → objectif annoncé → explication accessible → essai facultatif → correction facultative → possibilité de réutiliser la notion**. La correction reste masquée tant que la personne ne la demande pas. Les exercices utilisent des exemples fictifs lorsqu’ils décrivent une situation.

### Règle éditoriale générale : expliquer par une analogie concrète

Chaque fiche part d’une analogie tirée de la vie réelle — cuisine, trajet, planning, achat, rangement, travail ou autre expérience familière — pour donner une première image de la notion. Elle explique ensuite précisément ce que l’analogie aide à comprendre **et ce qu’elle ne représente pas**, puis revient aux mots, règles ou calculs propres au sujet. L’analogie ne remplace ni la définition, ni la preuve, ni une source fiable ; elle doit rester compréhensible, non stigmatisante et adaptable aux expériences variées. Le générateur refuse une fiche dont l’analogie ou la limite n’est pas renseignée.

### Protocole de création : de l’idée à la fiche publiée

Chaque sujet suit des étapes explicites, qu’il s’agisse d’une fiche très accessible ou d’un cours spécialisé :

1. **Repérer le besoin** : lacune de la carte, question signalée par des personnes, évolution d’un programme ou donnée de veille. Ne pas recueillir de récit personnel inutile.
2. **Définir l’objectif d’apprentissage** : ce que la personne pourra expliquer, calculer, comparer ou réaliser ; prérequis réels et sujets connexes ; situations où le savoir s’applique.
3. **Faire la recherche documentaire** : privilégier programmes et organismes compétents, sources primaires, ressources éducatives ouvertes et publications dont la licence permet explicitement la réutilisation. Croiser les références et noter date, portée, limites, divergences et niveau de preuve.
4. **Construire la progression** : relier les premières bases aux notions intermédiaires puis aux approfondissements de spécialité ; prévoir les transitions et prérequis sans exiger un parcours scolaire linéaire.
5. **Rédiger de manière originale** : apporter une explication, une analogie du quotidien et sa limite, des exemples et exercices nouveaux, des étapes de résolution et plusieurs formes d’entraînement. Ne pas reprendre une structure distinctive ou des exemples propres à une ressource.
6. **Relire le fond et les droits** : contrôle par une personne compétente pour le domaine, relecture éditoriale, vérification des sources et des permissions, puis relecture linguistique et d’accessibilité.
7. **Tester avec des publics variés** : compréhension, charge de lecture, clavier, lecteur d’écran, zoom, affichage mobile et utilité de l’analogie. Corriger à partir des retours volontaires.
8. **Publier et entretenir** : versionner le contenu, indiquer les sources et dates de revue, marquer les limites et la prochaine échéance ; retirer ou corriger une fiche si elle devient trompeuse, périmée ou non autorisée.

La production peut passer par plusieurs formats — fiche courte, cours en étapes, exercice corrigé, glossaire, schéma original ou support audio — après contrôle dédié. Une seule fiche ne doit pas prétendre couvrir tout un champ disciplinaire. La grille opérationnelle de relecture et de validation est conservée dans `docs/apprentissage/grille-relecture.md` ; elle distingue contrôle automatique, expertise humaine, essai d’usage, droits et décision de publication.

### Autonomie pédagogique sans service tiers obligatoire

Chaque fiche doit contenir tout ce qui est nécessaire pour apprendre son objectif et faire l’exercice : explication, mots utiles, exemple, étapes, aide, correction et limites. La personne ne doit pas avoir à ouvrir un autre site, créer un compte, installer un outil ou charger une vidéo distante pour comprendre la leçon. Les liens externes sont des références facultatives pour vérifier une source ou approfondir ; ils ne remplacent jamais le contenu pédagogique M.R.S.C. Pour les règles qui changent — santé, droit, sécurité, démarches ou tarifs — la fiche enseigne un repère durable, date ses indications et précise qu’une consigne officielle à jour doit être vérifiée avant une action réelle.

Le rendu d’une fiche doit dépendre des fichiers et composants du dépôt, pas d’un script, d’une police, d’une image, d’une API, d’une vidéo ou d’un compte hébergé par un tiers. Toute exception doit être justifiée, annoncée, accessible, facultative et examinée du point de vue des données et des droits. Les sources éditoriales peuvent rester externes et cliquer vers leur site, sans charger leur contenu automatiquement.

### Règles de sources, droits et création originale

La recherche peut consulter des sources de tout type pour vérifier des faits, repérer une lacune ou comparer des approches ; **cela n’autorise pas à reprendre leur forme**. Un contenu fermé, payant ou protégé ne doit pas être recopié, traduit de près, paraphrasé ligne par ligne, ni transformé pour contourner ses droits. Une réécriture qui conserve l’expression, la sélection, l’organisation, les exemples ou la progression distinctive d’une œuvre peut encore être une adaptation : en cas de doute, ne pas l’utiliser comme matrice.

Pour produire une ressource M.R.S.C, retenir les connaissances et faits vérifiables, puis élaborer indépendamment l’architecture pédagogique, les formulations, les analogies, les exemples, les données d’exercice, les questions et les corrections. Citer les sources qui étayent les faits et renvoyer vers l’œuvre d’origine lorsque c’est utile ; ne reproduire aucun passage, tableau, figure ou exercice sans permission ou licence qui l’autorise. Respecter les conditions exactes des ressources ouvertes (attribution, partage à l’identique, usage commercial ou autres clauses) et tenir une trace de la licence consultée. L’accès public ou la consultation d’une source ne signifie pas qu’elle est libre de droits.

Enfin, **libre d’accès, licence de réutilisation et propriété intellectuelle sont trois sujets distincts**. La création d’un nouveau texte ne transfère pas automatiquement ses droits à l’association, et une licence existante ne doit pas être présentée comme une cession de droits. Tenir un registre des auteurs et contributions, obtenir les accords nécessaires, aligner la licence du contenu avec `LICENCE` et `transparence.html`, et faire valider toute revendication de propriété ou d’exclusivité par l’association et une personne compétente. Ne jamais attribuer à M.R.S.C une création dont les droits ou la paternité ne sont pas clarifiés.

## 4. Principes d’inclusion, de clarté et de confiance

1. **Ne pas confondre scolarité et capacité.** Dire « reprendre une notion » plutôt que « rattraper son retard » ; valoriser l’expérience sans supposer que chaque métier enseigne les mêmes choses.
2. **Donner le choix du chemin.** Pas de diagnostic, d’examen d’entrée, de note, de limite de temps imposée, de compte obligatoire ni de suivi de progression dans la première version.
3. **Rendre le but concret.** Décrire ce que la personne pourra comprendre ou faire ; définir les mots scolaires ou techniques dès leur première apparition.
4. **Découper sans infantiliser.** Une compétence par exercice, phrases directes, étapes numérotées, espaces lisibles et corrections sans commentaire dévalorisant.
5. **Faire place au doute et aux sources.** Distinguer exemple, fait, avis et hypothèse ; dater les données ; signaler les limites du simulateur et des outils d’IA.
6. **Protéger la vie privée.** Ne pas demander de raconter un abandon scolaire, un handicap, une situation financière ou un problème de santé. La préférence d’agrandissement de texte est conservée localement dans le navigateur ; aucun résultat de parcours n’est collecté par la nouvelle page.
7. **Ne pas revendiquer une certification.** Les fiches M.R.S.C sont des ressources d’apprentissage informelles ; elles ne remplacent ni une formation adaptée, ni un accompagnement, ni une validation officielle.

### Veille récurrente et limites de l’automatisation

Le workflow `.github/workflows/veille-apprentissages.yml` s’exécute chaque semaine, après les modifications du référentiel ou des fiches sur `main`, et peut aussi être lancé manuellement. Il compile le générateur, vérifie que ses sorties sont synchronisées, puis contrôle hors ligne les pages, les liens locaux, les attributs essentiels et l’absence de ressources tierces chargées automatiquement sur les pages d’apprentissage. Le générateur vérifie les métadonnées, la présence d’une analogie et de sa limite, les sources HTTPS déclarées, les dates de revue, l’association entre fiches et domaines, et que les répartitions du plan de 1 000 fiches par domaine, horizon et repère totalisent chacune la cible. Pour les prototypes signalés, il exige aussi une note de statut et, pour chaque source, une licence déclarée ou le statut « non vérifiée », la date de contrôle des droits, le mode d’utilisation et une description de cette utilisation. Il vérifie le format de date, le mode déclaré et qu’une réutilisation sous licence ou permission n’est pas présentée comme vérifiée si elle ne l’est pas ; cela ne prouve ni l’absence de copie, ni l’exactitude des déclarations, ni les droits réels. Il ajoute le rapport à l’exécution GitHub Actions et crée ou actualise une seule issue de suivi des lacunes.

Pour que la veille ne s’arrête pas au corpus actuel — 26 fiches du corpus initial et 9 prototypes à relire —, le travail éditorial doit aussi : examiner chaque mois le backlog et les retours volontaires, réviser chaque trimestre un ou plusieurs domaines avec les sources compétentes, et repasser au moins une fois par an sur les grands champs ISCED-F ainsi que sur les programmes français, les voies professionnelles, les formations supérieures et les spécialités doctorales. Un changement de programme, une source officielle mise à jour, une évolution de pratique ou une demande récurrente déclenche une revue sans attendre l’échéance annuelle. Les sujets à risques (santé, droit, sécurité, finances et cybersécurité) gardent leurs propres dates rapprochées et relectures spécialisées.

Cette veille ne visite pas les sites cités et ne peut confirmer automatiquement qu’une source est disponible, toujours exacte ou bien interprétée. Elle ne publie pas de nouvelle fiche toute seule : mise à jour, jugement pédagogique, relecture spécialisée et validation de l’analogie restent humains. Les retours des apprenants et des professionnels sont nécessaires pour identifier des besoins que la seule carte ne montre pas. Le mot « veille » désigne donc une responsabilité éditoriale régulière, et non une promesse de surveillance exhaustive ni un robot qui produirait seul des cours fiables.

## 5. Cohérence de l’écosystème MRSC, simulateur et EVA

- **M.R.S.C** apporte le cadre citoyen et les sujets de société.
- **Les parcours d’apprentissage** rendent certains concepts et compétences accessibles par niveaux, matières et situations de vie ou de travail.
- **Le simulateur** permet d’examiner des hypothèses de politiques publiques. Son propre descriptif précise déjà qu’il s’agit d’un modèle, pas d’une prédiction ni d’un verdict.
- **EVA** est citée dans la vision du créateur, mais aucune fiche de mission ou spécification n’est présente dans le dépôt consulté. La maquette réserve une place à son intégration sans lui attribuer de fonctions. Avant d’ajouter un lien ou une promesse publique, faire confirmer : le nom et l’objectif, les publics, les fonctions réellement disponibles, les sources, les données traitées, les limites, le statut du projet et les besoins d’accessibilité.

Le fil commun proposé est : **apprendre un concept → l’utiliser pour lire une situation → examiner plusieurs hypothèses → discuter des effets et des limites**. Il ne faut pas faire passer les résultats du simulateur pour des faits certains, ni faire croire qu’EVA est disponible tant que son état n’est pas confirmé.

## 6. Validation à mener avant d’élargir le catalogue

La première version n’a pas encore été testée avec les personnes auxquelles elle s’adresse. Prochaine étape recommandée : organiser de courtes séances volontaires avec des adultes ayant des parcours scolaires et professionnels variés, dont des personnes ayant quitté tôt le cursus, des personnes peu à l’aise avec l’écrit ou le numérique et des personnes en situation de handicap. Ne pas demander de preuve de niveau ou le récit d’une expérience personnelle. Si possible, rémunérer le temps de participation.

### Scénarios de test

- Trouver un exercice de pourcentage et vérifier sa réponse sans aide.
- Choisir un niveau différent en français et en mathématiques.
- Utiliser une fiche sans ouvrir la correction, puis l’ouvrir au clavier.
- Agrandir le texte, changer de page et vérifier que le choix reste actif dans le navigateur.
- Rejoindre la page du simulateur et comprendre ce qu’il calcule et ce qu’il ne prédit pas.

### Points à observer

- La personne trouve-t-elle un point de départ sans se sentir évaluée ?
- Les consignes, exemples, unités et corrections sont-ils compris sans explication orale ?
- Le parcours fonctionne-t-il au clavier, avec lecteur d’écran, à fort zoom et sur petit écran ?
- Les liens, niveaux et boutons sont-ils compréhensibles sans dépendre de la couleur ou d’une animation ?
- Les personnes concernées jugent-elles le ton respectueux et les exercices utiles ?

Compléter ces essais par des vérifications automatiques du HTML, un contrôle des contrastes, un test clavier/lecteur d’écran et une revue de toutes les pages publiques. Aucun score automatique ne remplace le retour de personnes concernées.

## 7. Prochaines étapes proposées

1. Faire relire en priorité les trois prototypes mathématiques (`maths-convertir-unites`, `maths-moyenne`, `maths-estimer-calcul`) par une personne compétente en mathématiques et une personne éditoriale : contrôler unités, calculs, interprétation, vocabulaire et limites, puis documenter les corrections. Les références servent de repères factuels ; leurs licences de réutilisation sont déclarées non vérifiées et aucun texte, exemple ou exercice source n’est revendiqué comme repris.
2. Faire relire `recherche-lire-etude` avec la grille `docs/apprentissage/grille-relecture.md` par une personne compétente en méthodes de recherche et une personne éditoriale ; examiner l’exemple, l’analogie, l’attribution et les droits avant de traiter le sujet comme mieux couvert.
3. Tester les neuf prototypes avec des personnes apprenantes volontaires, par étapes et avec un ordre de priorité explicite, puis vérifier au clavier, au zoom, en contraste forcé et sur petits écrans ; aucun de ces essais n’est revendiqué comme réalisé.
4. Faire relire un échantillon représentatif des 26 fiches initiales et des analogies par des adultes apprenants et des professionnels de la formation de base ; distinguer la rédaction initiale d’une validation indépendante.
5. Utiliser le rapport hebdomadaire et les retours volontaires pour choisir les prochaines lacunes ; faire relire par une personne qualifiée les sujets juridiques, de santé, financiers et de sécurité.
6. Pour chaque nouveau sujet, expliquer la notion, donner une analogie quotidienne avec ses limites, proposer un exercice facultatif et une correction lisible ; ajouter une version audio ou FALC seulement après relecture et test dédiés.
7. Développer les 15 domaines suivis, dont les 11 grands champs ISCED-F et le nouveau domaine d’informatique/programmation, avec des notions liées de façon explicite aux horizons CP, cycles scolaires, voies professionnelles, post-bac, licence, master et doctorat. Conserver les statuts de couverture partielle et les sujets à créer : l’automatisation ne doit jamais donner l’impression que le corpus est complet ni garantir qu’aucune lacune n’existe.
8. Terminer les essais visuels dans de vrais navigateurs et les contrôles clavier, lecteur d’écran, fort zoom et petits écrans ; corriger selon les retours plutôt que déclarer le site « accessible » sans audit.
9. Actualiser régulièrement les repères scolaires et les sources ; faire confirmer toute prise de position attribuée au M.R.S.C.
10. Appliquer le protocole de droits : documenter pour chaque source la licence exacte ou son statut non vérifié, la date de contrôle, le mode d’utilisation et l’usage réellement fait ; ne jamais dériver une fiche d’une œuvre protégée par paraphrase de contournement ; faire valider la paternité, les accords de contribution et l’alignement avec la licence M.R.S.C.
11. Décrire EVA avec son créateur avant d’en afficher un accès, des fonctionnalités ou un traitement de données.

## Sources consultées

- Ministère de l’Éducation nationale, [décret et annexe du socle commun](https://www.education.gouv.fr/bo/15/Hebdo17/MENE1506516D.htm), Bulletin officiel n°17, 23 avril 2015.
- Certificat CléA, [les sept domaines](https://www.certificat-clea.fr/employeurs/le-socle/), référentiel de compétences professionnelles.
- Agence nationale de lutte contre l’illettrisme, [Je me forme](https://www.anlci.gouv.fr/comment-agir/je-me-forme/), page de repères pour les professionnels qui accompagnent les adultes ; [développer les compétences de base en situation de travail](https://www.anlci.gouv.fr/app/uploads/2025/04/20250910_Prez-webinaire-AFEST.pdf).
- W3C, [Web Content Accessibility Guidelines (WCAG) 2.2](https://www.w3.org/TR/WCAG22/), recommandation du 5 octobre 2023.
- W3C, [Understanding WCAG 2.2](https://www.w3.org/WAI/WCAG22/Understanding/intro) et [Making Content Usable for People with Cognitive and Learning Disabilities](https://www.w3.org/TR/coga-usable/).
- UNESCO Institute for Statistics, [About ISCED](https://isced.uis.unesco.org/about/), [Q&A](https://isced.uis.unesco.org/q-and-a/) et [ISCED Fields of Education and Training 2013](https://uis.unesco.org/sites/default/files/documents/isced-fields-of-education-and-training-2013-en.pdf) : repères internationaux sur les niveaux de programmes et les champs d’études.
- Carey MA, Steiner KL, Petri WA Jr, [Ten simple rules for reading a scientific paper](https://journals.plos.org/ploscompbiol/article?id=10.1371/journal.pcbi.1008032), *PLOS Computational Biology* 16(7):e1008032 (2020). PLOS indique une licence Creative Commons Attribution ; l’article est cité comme repère documentaire, sans reprise de son texte ou de ses exercices.
- Ministère de l’Éducation nationale, [programme de mathématiques du cycle 3, version publiée en janvier 2025](https://www.education.gouv.fr/media/199172/download) : repère de programme pour les mesures et conversions ; utilisé pour cadrer le sujet, sans reprise de formulation ni d’activité.
- Ministère de l’Éducation nationale, [annexe — programme de mathématiques du cycle 4](https://www.education.gouv.fr/sites/default/files/document/Annexe%202%20%E2%80%93%20Programme%20de%20math%C3%A9matiques%20pour%20le%20cycle%204-480716.pdf) : repère de programme pour les statistiques et la moyenne, sans reprise de texte ni d’exemple.
- Éduscol, [mathématiques au quotidien — ressources sur les cycles 3 et 4](https://eduscol.education.gouv.fr/sites/default/files/document/ra16c3c4mathmathetquotidien600998pdf-77574.pdf) : repère de programme pour l’estimation et la vérification de la vraisemblance, sans reprise de ses exemples ou activités.
- Bureau international des poids et mesures, [The International System of Units](https://www.bipm.org/en/measurement-units) : référence institutionnelle consultée pour contrôler les unités et symboles. Pour ces quatre sources officielles, la licence applicable à la réutilisation n’a pas été vérifiée ; elles ne sont utilisées ici que pour étayer des faits ou délimiter le programme, sans reprise déclarée de texte, structure, exemple, exercice, figure ou tableau.

### Sources de la première sélection publique et des nouveaux thèmes

- M.R.S.C, [sélection documentée de sources d’utilité publique et citoyenne](docs/apprentissage/sources-utilite-publique.md), contrôle documentaire daté du 8 octobre 2026 : portails administratifs, statistiques, cybersécurité, prévention, énergie, santé, emploi et documentation technique. Les portées, limites et statuts de réutilisation y sont consignés ; disponibilité et licences ne sont pas affirmées comme vérifiées lorsque le registre dit le contraire.
- INRS, [prévention du risque électrique](https://www.inrs.fr/risques/electriques/prevention-risque-electrique.html), référence de prévention ; aucune procédure ni formulation source n’est reprise.
- Éduscol, [programmes et ressources en numérique et sciences informatiques](https://eduscol.education.gouv.fr/5823/programmes-et-ressources-en-numerique-et-sciences-informatiques-voie-g), repère scolaire et de couverture ; les ressources ne remplacent pas une progression autonome destinée à tous les publics.
- Documentation Python, [tutoriel en français](https://docs.python.org/fr/3/tutorial/) et [Histoire et licence](https://docs.python.org/fr/3/license.html) : les conditions publiées distinguent la documentation et les exemples/code. Aucun texte ni exemple de ces pages n’est repris dans les prototypes.
- MDN, [apprendre les boucles JavaScript](https://developer.mozilla.org/fr/docs/Learn_web_development/Core/Scripting/Loops) et [politique de droits](https://developer.mozilla.org/en-US/docs/MDN/Writing_guidelines/Attrib_copyright_license) : source technique facultative ; aucun passage ni exemple n’est repris.
- Les autres sources de la série et leurs rôles sont consignés dans le registre ci-dessus. Les licences ou autorisations non vérifiées restent signalées comme telles ; le code, le contenu pédagogique, les exemples et les analogies des prototypes sont des propositions originales à faire relire, et non des réécritures d’une ressource particulière.
