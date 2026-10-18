# Protocole éditorial commun du M.R.S.C.

**Référence interne pour les contenus nouveaux et les révisions — version du 14 octobre 2026.** Ce protocole fixe une méthode commune pour le site, les fiches, les dossiers, les outils et les activités. Il guide la rédaction ; il ne certifie pas les informations et ne signifie pas que toutes les pages existantes ont déjà été relues.

## 1. Intention et voix éditoriale

Le site doit aider une personne à comprendre **ce qu’elle peut trouver, apprendre, examiner ou proposer**. Commencer par ce qui rapproche les expériences et ce que les ressources apportent, plutôt que par une liste de ce que l’association ou le site exclut.

La tonalité retenue est :

- **accueillante et positive**, sans déclaration solennelle ni promesse grandiose ;
- **concrète et accessible**, avec des mots courants, des paragraphes courts et une idée principale par paragraphe ;
- **ouverte aux expériences diverses**, sans supposer qu’un parcours, un territoire ou un point de vue représente tout le monde ;
- **précise sur les rôles et les preuves** : association, réflexion, hypothèse, expérience testée et résultat documenté ne sont pas interchangeables.

Le repère éditorial approuvé pour l’accueil est : **« Nos expériences ont quelque chose à apporter. »** Les trois angles de lecture sont **« Partir de ce que nous vivons »**, **« Mettre les savoirs en commun »** et **« Rendre les propositions compréhensibles »**. Ils inspirent les autres pages sans devenir des slogans à répéter mécaniquement.

Ne pas attribuer une position, une action, un résultat ou une décision officielle à l’association sans document ou validation qui l’atteste. Les propositions de rédaction, les pistes de débat et les travaux d’ÉVA restent identifiés comme tels.

## 2. Une trame commune, adaptée à chaque page

La cohérence vient d’un même parcours de compréhension et de composants partagés, **pas de pages toutes identiques**. Garder les fonctions propres à chaque page et réordonner ou omettre une étape lorsqu’elle n’est pas utile.

Pour une page de contenu, vérifier si le parcours suivant est adapté :

1. **Se repérer** — titre explicite et phrase d’ouverture qui dit de quoi il s’agit.
2. **Comprendre** — explication autonome, contexte et termes nécessaires.
3. **Voir un exemple** — situation originale et délimitée, reliée à la notion.
4. **Essayer si on le souhaite** — activité ou exploration facultative, avec aide et retour compréhensible.
5. **Retenir l’essentiel** — courte synthèse ou prochaine question.
6. **Vérifier et approfondir** — sources affichées, limites, date et liens utiles.

### Adaptations par type de page

| Type de page | Parcours à privilégier |
| --- | --- |
| Accueil | Présenter l’association et ses ressources, proposer quelques portes d’entrée et des actions explicites ; garder visibles les statuts et distinguer l’association de ses travaux de recherche. |
| Dossier ou page de réflexion | Poser une question, décrire le contexte et les points de vue utiles, séparer faits, analyses et propositions, puis indiquer ce qui reste à examiner. |
| Fiche d’apprentissage | Annoncer un objectif observable, expliquer la notion, donner un exemple original, proposer une activité facultative, un indice et une correction expliquée, puis les limites et les sources. |
| Outil ou simulateur | Dire ce que l’outil fait et ne fait pas, préciser ses entrées, sa méthode, les sources/dates, les hypothèses, les limites et le recours en cas d’échec. |
| Page pratique ou contact | Donner les étapes dans l’ordre, les prérequis, les délais ou dates vérifiés, les coordonnées utiles et une solution de repli. |

## 3. Mise en page et cohérence de l’ensemble du site

Réutiliser les composants communs définis dans `assets/css/site.css` et les sources maîtresses des pages générées. Garder une hiérarchie reconnaissable — titre, introduction, sections, exemples ou repères, sources et suite possible — avec les mêmes repères de boutons, cartes, couleurs, liens, focus et espaces.

- Respecter les composants, générateurs et règles propres aux fiches, pages d’information et simulateur ; ne pas modifier à la main une sortie générée.
- Préserver le contenu, les commandes, les réglages d’affichage, le zoom natif, le clavier et les solutions de repli sans JavaScript.
- Concevoir le reflow pour les téléphones et les agrandissements : aucun texte ou contrôle ne doit être rendu inaccessible par une colonne fixe, un panneau hors écran ou un défilement horizontal non signalé.
- Les modes « Équilibrée », « Lecture », « Vitrine », « Mosaïque », « Panorama composite » et « Compacte » réorganisent la présentation ; ils ne suppriment, ne réordonnent ni ne réécrivent le contenu (voir [`rd/presentations-personnalisees.md`](rd/presentations-personnalisees.md)).
- Employer des titres hiérarchisés, des libellés de liens explicites, des listes et tableaux uniquement lorsqu’ils aident réellement la lecture. Ne pas transmettre une information par la couleur seule.

La même logique éditoriale n’autorise pas à fusionner des pages dont les tâches diffèrent. Une activité ludique, une commande ou une carte n’est ajoutée que si elle aide la compréhension ou l’action proposée.

## 4. Contenus ludiques : utiles, facultatifs et accessibles

Un jeu, défi, comparaison, mini-scénario ou quiz doit servir un objectif identifiable. Il ne remplace pas l’explication centrale et ne doit pas être un décor ajouté pour rendre une page « ludique » en apparence.

Pour chaque activité :

- expliquer la consigne et le résultat attendu avant l’action ;
- permettre d’essayer sans note, classement, pénalité, minuterie obligatoire ou parcours imposé ;
- proposer un indice, une correction ou une rétroaction qui explique le raisonnement, pas seulement « juste/faux » ;
- offrir une commande au clavier et au toucher, un texte équivalent lorsque nécessaire et le respect de `prefers-reduced-motion` ;
- distinguer un exemple inventé, une simulation et un fait observé ; ne pas transformer le jeu en diagnostic ou en promesse d’apprentissage démontrée. Un résultat de jeu ne constitue pas, à lui seul, une preuve d’apprentissage ou d’efficacité pédagogique.

## 5. Informations, sources et limites

### Relier chaque affirmation importante à une preuve

Avant publication, dresser pour les affirmations factuelles importantes un petit registre interne : affirmation, source directe, passage ou donnée consultée, date de consultation, portée, limites et éventuel recoupement. Commencer par une source primaire ou officielle adaptée à la question, puis recouper les points sensibles avec des sources indépendantes lorsque c’est possible.

Pour chaque référence, vérifier et noter selon le cas :

- auteur ou organisme responsable ;
- titre exact, date ou version ;
- URL, passage/page/table utilisé et date de consultation ;
- territoire, population, période ou juridiction couverts ;
- limites, incertitudes, désaccords, qualité des données et droits de réutilisation.

Afficher les sources **à proximité de l’affirmation ou dans une rubrique clairement nommée**, avec un lien descriptif et les éléments qui permettent de retrouver la référence. Pour une donnée évolutive, afficher la date ou la période réellement couverte. Pour un document officiel, préciser s’il s’agit d’une copie locale ou d’une source externe.

Une source consultée ne rend pas automatiquement une affirmation exacte, actuelle, universelle ou libre de droits. Ne pas inventer de référence, de citation, de statistique ou de résultat. Si la preuve manque, retirer l’affirmation, la présenter explicitement comme hypothèse ou maintenir le contenu au statut « à vérifier ».

### Séparer les statuts de preuve

Dans les brouillons et revues, distinguer au minimum : **proposition**, **fait sourcé**, **interprétation**, **hypothèse**, **essai effectué**, **résultat observé** et **validation humaine**. Une vérification de lien ou un test automatique ne vaut ni expertise de domaine, ni validation juridique, ni relecture associative, ni essai auprès de personnes.

Les sujets sensibles ou évolutifs (santé, droits, sécurité, finances, politique publique, sciences controversées, démarches locales) exigent des sources adaptées au risque et une relecture compétente. Si elle n’a pas eu lieu, afficher la limite et ne pas prétendre que le contenu est validé.

## 6. Méthode de production et d’entretien

Suivre les étapes ci-dessous et consigner les décisions importantes dans le portefeuille ou le journal R&D, plutôt que d’ajouter une procédure différente à chaque page.

1. **Cadrer** — préciser la question, le public et les contextes possibles, le territoire, la langue, la tâche de lecture et les conséquences d’une erreur ; distinguer observations et hypothèses.
2. **Examiner l’existant** — repérer la page ou le générateur propriétaire, le contenu déjà présent, le statut éditorial, les composants réutilisables et les lacunes ; conserver les éléments utiles.
3. **Rechercher** — consulter les sources nécessaires, recouper les affirmations importantes, vérifier les dates, la portée, les droits et les limites.
4. **Conceptualiser** — comparer plusieurs formes possibles ; expliciter l’utilité, les risques, les coûts et le critère de choix. Choisir la solution la plus simple qui répond au besoin.
5. **Rédiger et mettre en forme** — utiliser le gabarit, adapter la trame au type de page, privilégier exemples originaux et activités facultatives, relier les affirmations à leurs sources.
6. **Vérifier** — relire le sens, les faits, les liens, les droits, les sorties générées, la mise en page, le mobile, le clavier, le zoom, le contraste et les technologies d’assistance pertinentes.
7. **Faire valider au bon niveau** — demander une relecture compétente ou associative lorsqu’elle est requise. Noter le rôle, la portée et le résultat, sans présenter un contrôle automatisé comme validation humaine.
8. **Publier et entretenir** — enregistrer le statut réel, la date de revue, les limites, le rôle de maintenance et le signal de mise à jour ; corriger, dater ou retirer un contenu devenu incertain ou périmé.

## 7. Liste de contrôle avant livraison

- [ ] La page répond à une tâche ou question définie et ne répète pas une information sans raison.
- [ ] Le ton est accessible, concret, accueillant et non solennel ; les faits, hypothèses et propositions sont distincts.
- [ ] L’ordre de lecture convient au type de page et les composants communs sont réutilisés sans effacer les spécificités.
- [ ] Chaque affirmation importante a une source traçable ou est explicitement présentée avec son incertitude.
- [ ] Les sources sont visibles, datées si nécessaire, adaptées au territoire et reliées au bon passage.
- [ ] Toute activité ludique est utile, facultative, explicable et accessible ; son résultat n’est pas présenté comme une preuve d’apprentissage.
- [ ] Le rendu garde le contenu, les commandes, les états clavier, le zoom, le reflow mobile et les alternatives utiles.
- [ ] Les générateurs et tests concernés ont été exécutés ; les sorties et limites sont examinées.
- [ ] Les relectures humaines non réalisées restent signalées comme telles ; le statut et la prochaine action sont explicites.

## 8. Portée et documents liés

Le protocole s’applique aux nouveaux contenus et à chaque lot de révision. Il **ne permet pas d’affirmer que tout le site est déjà harmonisé ou que toutes ses informations sont vérifiées**. Les lots, écarts connus et validations encore requises sont suivis dans [`docs/rd-coherence-visuelle-editoriale.md`](rd-coherence-visuelle-editoriale.md), [`docs/rd/portefeuille.toml`](rd/portefeuille.toml) et [`docs/rd/journal.md`](rd/journal.md).

Pour préparer une page, copier et adapter [`docs/gabarits/contenu-editorial.md`](gabarits/contenu-editorial.md). Les consignes communes sont dans [`AGENTS.md`](../AGENTS.md), la méthode de R&D dans [`docs/rd-innovation-continue.md`](rd-innovation-continue.md) et les essais d’usage dans [`docs/rd/protocole-essais-usage.md`](rd/protocole-essais-usage.md). Les contrôles automatiques de présence et de cohérence se lancent avec `python3 outils/test_protocole_editorial.py` ; ils vérifient le cadre documentaire, jamais l’exactitude de toutes les pages.
