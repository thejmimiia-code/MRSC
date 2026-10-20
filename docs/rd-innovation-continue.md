# Manuel de R&D continue — connaissances, site et jeu

**Version de travail : 13 octobre 2026.** Ce manuel décrit une méthode reproductible pour tous les agents et contributeurs : explorer les besoins et les savoirs, étendre le catalogue, conceptualiser des expériences, les intégrer au site et au jeu, vérifier leur qualité, puis les entretenir.

> **Ambition et limite.** « Les connaissances du monde » est un horizon ouvert : aucune équipe, base ou IA ne peut garantir un inventaire universel, neutre, complet et toujours à jour. Le but est d'élargir progressivement une carte plurielle et sourcée, d'expliciter ses absences et de relier chaque contenu à son contexte et à son niveau de preuve — pas d'afficher une exhaustivité fictive.

## 1. Le système de R&D

La R&D est un cycle de travail, pas un document ponctuel ni une génération automatique de pages :

1. **Écouter et observer** — recueillir des questions, difficultés, usages du site, évolutions des connaissances et besoins de la communauté sans inventer de témoignage. Les propositions sont volontaires ; les récits personnels ne sont pas nécessaires.
2. **Cadrer** — écrire une question précise, le public/contextes possibles, le territoire, la langue, la date et les conséquences de l'erreur. Vérifier ce qui existe avant d'ouvrir une nouvelle piste.
3. **Cartographier** — placer la question dans le référentiel, relever prérequis, domaines connexes, divergences, lacunes, ressources déjà publiées et éléments absents.
4. **Documenter** — rechercher des sources primaires, institutionnelles, scientifiques, professionnelles ou locales adaptées; les recouper et consigner leurs limites et leurs droits.
5. **Conceptualiser** — formuler plusieurs réponses ou formats; préciser l'hypothèse, la valeur attendue, l'originalité, le coût, les risques et un critère de décision.
6. **Prototyper** — choisir un changement petit et réversible : fiche autonome, dialogue, monde, outil d'orientation, illustration, simulation, navigation ou aide technique.
7. **Revoir et essayer** — séparer les validations techniques, factuelles, pédagogiques, linguistiques, juridiques et d'accessibilité. Faire des essais d'usage appropriés avant d'interpréter les résultats.
8. **Décider et publier** — intégrer seulement après les contrôles requis, afficher le statut réel et expliquer les limites. Une piste non prête reste documentée, non présentée comme validée.
9. **Observer et entretenir** — noter les retours utiles, liens qui changent, erreurs et effets inattendus; réviser, remplacer ou retirer un contenu si sa preuve, son utilité ou son droit d'usage n'est plus valable.

La carte des lacunes, générée depuis le référentiel, liste les sujets sans fiche et l'exigence de preuve de chacun : [`docs/rd/carte-lacunes.md`](rd/carte-lacunes.md), régénérable par `python3 outils/construire-carte-lacunes.py`. Le portefeuille vivant est [`docs/rd/portefeuille.toml`](rd/portefeuille.toml); son gabarit de décision est [`docs/rd/gabarit-initiative.md`](rd/gabarit-initiative.md) et le [`journal`](rd/journal.md) conserve les décisions et relais importants. Les cartes de compétences partagées et leur routeur résident sous [`.agents/skills/`](../.agents/skills/); le [dossier et les sources de la bibliothèque](rd/bibliotheque-skills.md) recensent les domaines et les limites de sélection. Les skills de projet Claude Code résident sous [`.claude/skills/`](../.claude/skills/) et renvoient, lorsque possible, vers ces cartes communes. Les consignes générales sont dans [`AGENTS.md`](../AGENTS.md). Le vérificateur [`outils/verifier-rd-continue.py`](../outils/verifier-rd-continue.py) contrôle leur cohérence et signale les revues échues. La veille GitHub planifiée fournit un rappel périodique; elle ne cherche pas sur le Web, ne juge pas les sources et ne publie aucun contenu à la place d'une personne.

## 2. Cartographier sans réduire le monde à une liste

### Sources de cartographie

Le catalogue actuel utilise 15 domaines locaux et un référentiel détaillant les sujets actifs, partiels, à créer ou à relire. Le plan de 1 000 fiches est une hypothèse de répartition, pas une couverture du savoir ni un objectif de quantité à atteindre coûte que coûte. Pour l'élargir :

- comparer des taxonomies adaptées à la question — par exemple UNESCO ISCED-F pour les champs d'études, référentiels disciplinaires, vocabulaires professionnels, classifications de métiers, normes, programmes et cadres nationaux ou régionaux;
- compléter ces cartes par les savoirs pratiques, communautaires, linguistiques, artistiques, culturels, autochtones et professionnels qui ne se laissent pas toujours ranger dans une taxonomie scolaire;
- garder les variations par région, langue, époque, juridiction, profession, école de pensée et niveau de preuve; éviter de présenter le contexte français comme une règle mondiale;
- créer des liens transversaux (ex. climat ↔ énergie ↔ économie ↔ santé ↔ politiques publiques) plutôt que de dupliquer une même fiche dans plusieurs matières;
- afficher les sujets absents, les zones peu documentées, les contenus controversés et les besoins de traduction ou de validation locale.

### Modèle de carte d'un sujet

Pour chaque nouveau sujet, documenter au minimum :

| Dimension | Questions à traiter |
| --- | --- |
| Identité | Quel phénomène, savoir-faire, discipline ou pratique? Quel nom dans les langues et contextes concernés? |
| Besoin | Quelle question ou tâche cette ressource aiderait-elle à comprendre ou réaliser? Quelles preuves de ce besoin sont réellement disponibles? |
| Portée | Qu'est-ce qui est dedans/dehors? Quelles régions, dates, juridictions, publics, prérequis et cas particuliers comptent? |
| Relations | Quels concepts sont préalables, voisins, contestés ou utiles au transfert? |
| Preuve | Quelles affirmations reposent sur quelles sources? Quelle incertitude, controverse ou obsolescence? |
| Forme d'apprentissage | Quelle action observable — comprendre, décrire, comparer, calculer, créer, discuter, vérifier ou appliquer — est adaptée? |
| Traduction en expérience | Fiche, exercice, scène, carte, audio, simulation ou ressource de site? La forme ludique facilite-t-elle vraiment l'apprentissage? |
| Statut | À explorer, à documenter, prototype, relu par rôle identifié, essayé, publié ou à réviser. Quelle preuve justifie le statut? |
| Entretien | Qui doit relire (rôle, pas nom public), à quel rythme et à quel signal déclencher une révision? |

Un domaine peut comporter plusieurs perspectives légitimes. Une carte éditoriale aide à repérer les absences; elle ne représente pas toute connaissance humaine, et ne doit ni classer la valeur des cultures ni hiérarchiser les personnes.

## 3. Recherche documentaire et qualité de preuve

1. **Établir une requête de recherche** avec synonymes, termes spécialisés, variantes linguistiques, date, territoire et type de source. Garder une trace des requêtes utiles lorsqu'une revue est importante.
2. **Partir des sources primaires quand elles sont accessibles** : données, texte officiel, protocole, document original, article scientifique, norme, organisme responsable ou personne détentrice du savoir. Les sources secondaires servent à mettre en contexte et à trouver des désaccords.
3. **Recouper au moins les affirmations importantes** par des sources indépendantes et adaptées. La répétition d'une même dépêche ou d'un même communiqué n'est pas un recoupement.
4. **Vérifier l'autorité et le périmètre** : qui publie, avec quelle compétence, quelle population, quelle méthode, quelle version et quels intérêts? Une autorité institutionnelle peut être exacte dans son champ sans être universelle.
5. **Tenir un registre d'affirmations** : fait, source, passage/donnée, date consultée, conclusion permise, limites, corroborations et degré d'incertitude. Séparer faits, estimations, interprétations, recommandations et propositions M.R.S.C.
6. **Vérifier l'actualité** pour les sujets évolutifs (lois, démarches, santé, IA, cybersécurité, prix, données publiques). Si la source n'a pas été directement vérifiée, ne pas prétendre qu'elle est à jour.
7. **Vérifier droits et attribution** avant toute réutilisation. Accès gratuit ≠ domaine public; citer n'autorise pas à reproduire. Rédiger les explications, exemples, exercices, visuels et scénarios de manière originale.
8. **Consigner les désaccords** : présenter leur nature, le périmètre de chaque source et les incertitudes plutôt que les lisser en un consensus inventé.

Aucun agent ne doit compléter une lacune par une citation, un auteur, une statistique ou un résultat qu'il ne peut pas retracer dans la source. Quand une source directe est inaccessible, le point reste en attente ou est formulé comme hypothèse à vérifier.

## 4. Méthode de conceptualisation et d'innovation

Pour chaque demande ou piste :

### A. Découvrir et définir

- Résumer le besoin en une phrase neutre; séparer l'observation de l'interprétation.
- Identifier qui pourrait bénéficier, qui pourrait être oublié ou lésé, et quels contextes changent la réponse.
- Décrire le parcours actuel : entrée, obstacles, solution déjà disponible, sortie et recours si le contenu échoue.
- Écrire ce qui n'est **pas** demandé et ce que la preuve ne permet pas d'affirmer.

### B. Diverger sans copier

- Générer plusieurs options différentes : améliorer une fiche; créer un récit/scénario; améliorer recherche et navigation; changer le rythme ou les aides; fournir un outil ou une représentation; ne rien construire si un lien fiable suffit.
- Examiner les formats avant la technologie : papier/texte, audio, image, animation, dialogue, simulation, monde 3D ou activité collaborative ne sont pas interchangeables.
- Ne pas reprendre personnages, univers, interface distinctive, règle, musique, illustrations, noms ou progression d'un jeu/propriétaire existant. S'inspirer des principes pédagogiques généraux, puis créer une expression originale.
- Prévoir une solution bas débit, un texte équivalent, une option sans animation et un chemin sans compte/service distant.

### C. Converger vers un prototype vérifiable

Rédiger : **problème → hypothèse → concept → tâche de l'apprenant/visiteur → signal de réussite → méthode d'essai → risques → limites → décision attendue**. Construire le plus petit prototype capable d'infirmer l'hypothèse. Chaque effet annoncé doit avoir un indicateur défini avant l'essai; préférer l'accomplissement d'une tâche ou la compréhension à des mesures d'engagement qui pourraient encourager l'addiction.

## 5. Du savoir au jeu et au site

### Chaîne de traçabilité

Pour intégrer un sujet, maintenir un lien lisible entre :

`question / source → notion → objectif d'apprentissage → ressource complète → activité ou monde → retour / aide → preuve d'essai → statut et prochaine revue`.

### Adapter à la bonne forme

- **Fiche** : objectif unique, définition, situation connue, explication autonome, exemple original, démarche, exercice facultatif, indice, correction progressive, transfert et limites.
- **Mission narrative** : but clair, choix compréhensibles, rétroaction descriptive sans punir l'erreur, aide graduelle, possibilité de rejouer et activité représentative de la notion — pas seulement un décor thématique.
- **Monde ou scène 3D** : justifier ce que l'espace ajoute à la compréhension; fournir descriptions, alternatives 2D/texte, commandes clavier/toucher, mouvements réduits et performance faible. La 3D n'est pas un objectif en soi.
- **Outil du site** : bénéfice expliqué, données minimales, état de chargement/erreur, fonctionnement de repli, accessibilité, sécurité et responsable de la maintenance.
- **Langue ou culture** : activer aussi le skill de localisation; préciser langue, variété, région et registre; demander des relectures compétentes/locales avant d'enseigner des usages comme universels.

Ne pas marquer une fiche comme terminée parce qu'elle est ajoutée à un parcours. Ne pas noter une personne à partir de son temps, de son nombre d'erreurs ou de ses retours. L'anglais et les cinq Escales ne définissent pas le périmètre général de l'atlas.

## 6. Relecture, essai et décision de publication

Les portes de validation sont distinctes et cumulatives selon le risque :

1. **Automatique** : schémas, liens locaux, ancres, HTML, JavaScript, génération, tests, poids et contrôles de sécurité.
2. **Factuelle/spécialisée** : exactitude par une personne compétente pour le domaine, méthodes et contre-exemples.
3. **Éditoriale/pédagogique** : objectif, clarté, progressivité, vocabulaire, correction et absence de promesse excessive.
4. **Juridique et droits** : attribution, droit de citation/réutilisation, données personnelles, santé/droit/finance, licences et responsabilités.
5. **Accessibilité** : clavier, zoom/reflow, contraste, lecteurs d'écran, sous-titres/transcriptions, animations et accessibilité cognitive.
6. **Usage** : tâches réalistes avec personnes volontaires et diverses quand cela est pertinent. Consentement, possibilité d'arrêter, données minimales et aucune collecte de réponse personnelle par défaut.
7. **Maintenance** : auteur/rôle responsable, date de revue, signaux de changement, solution de retrait/correction.

Un prototype peut être utilisé pour apprendre ce qu'il faut améliorer, mais il ne doit pas être présenté comme une ressource validée. Le [protocole de préparation aux essais d'usage](rd/protocole-essais-usage.md) fournit des tâches, une invitation à adapter, une fiche de notes minimale et des règles d'arrêt; il n'autorise pas à prétendre qu'un essai a eu lieu. Les erreurs présentant un risque de préjudice, les droits incertains, les chiffres non sourcés et l'absence d'alternative accessible bloquent la publication correspondante.

## 7. Rythme et continuité entre les agents

- **À chaque modification** : lire `AGENTS.md`, choisir les skills utiles, mettre à jour la source de vérité, tester, actualiser le portefeuille si l'état change, puis fournir le rapport de livraison. Consigner dans le [journal](rd/journal.md) les décisions structurantes et les passations qui devront être reprises; ne pas ajouter une ligne pour chaque micro-changement.
- **Chaque semaine** : GitHub Actions exécute hors ligne les contrôles éditoriaux, de structure, de liens et du portefeuille; le résumé de l'exécution et l'issue de veille exposent les alertes. Les agents répondant à une piste doivent reprendre le même identifiant d'initiative ou justifier une nouvelle entrée.
- **Chaque mois** : revoir le portefeuille, les priorités, les statuts, les éléments bloqués et les sujets à fort risque; ajuster la date de revue après examen réel.

### Répartir une piste entre plusieurs agents

Un coordinateur ou agent intégrateur garde la responsabilité du brief, des sources de vérité, des critères d'acceptation et du diff final. Les tâches indépendantes peuvent être distribuées par skill : **cartographie** (domaines, doublons, lacunes), **recherche** (preuves, contre-sources, droits), **conception** (options, objectifs, scénario), **pédagogie / accessibilité** (explication, alternatives, essais), **ingénierie** (code, génération, tests) et **revue indépendante** (chercher erreurs et promesses excessives). Les agents se transmettent l'identifiant du portefeuille, leurs fichiers/références exacts, une courte trace des recherches, les tests lancés, les inconnues, le statut et l'action suivante. Un agent ne marque pas comme relue l'étape exécutée uniquement par lui-même si la règle demande une revue indépendante.

Pour limiter les conflits, attribuer un seul responsable par fichier source; paralléliser la recherche et la critique sur des fichiers distincts; demander à l'intégrateur de fusionner les apports, regénérer les sorties une fois les sources prêtes et exécuter les contrôles finaux. Le résumé de passation ne contient pas de données personnelles ni de réponses d'apprentissage.
- **Au minimum tous les 90 jours ou au signal de changement** : re-vérifier les sources sensibles ou évolutives et les liens déclarés. Une vérification automatique d'URL ou d'échéance ne prouve ni exactitude ni actualité.
- **Avant publication** : faire la revue adaptée, laisser une trace de décision et mettre à jour la visibilité des limites dans le jeu et sur le site.

Les créneaux et alertes automatiques ne prouvent pas qu'une revue humaine a eu lieu. Ne déplacer `derniere_revue` dans le portefeuille que si la revue est vraiment effectuée et résumée.

## 8. Ajouter une piste / demander une amélioration

Utiliser le formulaire GitHub « Proposition de R&D » ou le courriel de contact déjà ouvert à la demande. Décrire un sujet, un besoin général, le domaine et les sources utiles; ne pas envoyer de diagnostic, récit scolaire, réponse d'exercice, donnée de santé, donnée sur un mineur ou autre information personnelle. Une proposition n'est ni une promesse d'acceptation, ni une validation éditoriale. Les fiches du formulaire demandent les éléments nécessaires pour éviter qu'une idée non sourcée soit présentée comme un fait.

## 9. État actuel et limites assumées

- L'atlas **Les Mondes** relie les 76 fiches à 15 domaines; 55 fiches portent le statut « Prototype à relire ». Consulter le référentiel pour les sujets actifs, partiels et à créer.
- Les quatre portes d'entrée sont des filtres, pas des cursus. Le dépôt ne contient pas de formation autonome distincte pour chaque domaine.
- Les scènes 3D jouables sont actuellement les cinq Escales d'anglais; les autres domaines sont des fiches et un atlas, pas 15 mondes 3D achevés.
- Aucune couverture complète des connaissances du monde, essai contrôlé d'efficacité, conformité universelle, validation de tous les droits ou validation de tous les contenus n'est revendiquée.
- La validation humaine, les relectures locales, les langues supplémentaires, la co-conception, l'élargissement progressif du jeu et l'entretien des sources restent des chantiers.

Cette liste doit évoluer quand des preuves, validations et travaux réels changent l'état du projet — pas pour rendre les indicateurs plus flatteurs.
