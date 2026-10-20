# Carte de sujet — Écoute, prononciation et ressources audio accessibles

**Statut : à documenter.** Cette carte a ouvert un sujet du référentiel qui n'avait **aucune fiche** ; une première fiche existe désormais à l'état de prototype. Elle ne contient aucune fiche, aucun audio et aucune promesse d'efficacité. Elle rassemble ce que trois sources consultées permettent d'affirmer, ce qu'elles ne permettent pas, et la forme que pourrait prendre un premier contenu.

**Date de consultation des sources : 20 octobre 2026.** Rédigée par un agent, sans relecture experte ni essai avec des personnes.

## 1. Identité

| Dimension | Contenu |
| --- | --- |
| Sujet du référentiel | Langues étrangères et interculturel → « Écoute, prononciation et ressources audio accessibles » (`statut = a-creer`) |
| Ce dont il s'agit | Comprendre à l'oral une langue étrangère, se faire comprendre en la parlant, et rendre ce travail possible sans dépendre d'un son qu'on ne peut ni voir, ni lire, ni arrêter. |
| Ce dont il ne s'agit pas | Ni une méthode de prononciation « sans accent », ni un cours d'anglais complet, ni un service de synthèse vocale. |

## 2. Besoin

La question de départ, formulée sans interprétation : **une personne qui apprend une langue étrangère sur un site écrit peut-elle travailler l'oral sans être bloquée par un audio qu'elle n'entend pas, ne peut pas arrêter ou ne peut pas lire ?**

Deux éléments de contexte rendent la question concrète :

- le Cadre européen commun de référence indique que la phonologie « tend encore à ne pas être enseignée explicitement », une partie des enseignants manquant de confiance faute de formation spécifique, et que la recherche montre que **l'intelligibilité compte davantage pour la communication que l'accent** ;
- une page qui diffuse de l'audio sans alternative exclut une partie des lecteurs : le critère WCAG 1.2.1 (niveau A) exige une alternative pour tout contenu audio préenregistré, et le critère 1.4.2 (niveau A) exige qu'un son de plus de trois secondes puisse être arrêté ou réglé indépendamment du volume système.

Aucun de ces éléments ne prouve un besoin mesuré chez les visiteurs du M.R.S.C. : **aucune observation d'usage n'existe** à ce jour.

## 3. Portée

**Dedans :** le français langue maternelle et l'anglais déjà présent sur le site ; l'écoute de mots et de phrases courtes ; les repères de prononciation décrits par écrit ; l'accessibilité de tout audio ; la possibilité de travailler sans audio du tout.

**Dehors :** l'évaluation de la prononciation d'une personne, l'enregistrement de voix d'apprenants, la reconnaissance vocale, la correction automatique, la transcription de conversations réelles, les variétés régionales autres que celles effectivement documentées.

**Limite de contexte :** les normes citées sont celles du Conseil de l'Europe et du W3C ; elles ne fixent ni quel français ni quel anglais enseigner. Une carte écrite depuis la France ne doit pas être lue comme une règle pour d'autres régions ni pour d'autres langues.

## 4. Relations

| Sujet voisin | Lien |
| --- | --- |
| `fr-lire-consigne` (fiche existante) | Lire une consigne est le prérequis d'un exercice oral décrit par écrit. |
| « Consignes, aides et correction » (fiches existantes) | Une consigne d'exercice oral doit rester compréhensible sans entendre l'audio. |
| `anglais-aventure` (5 scènes jouables) | Les scènes supposent déjà une lecture ; aucun audio n'y est indispensable, ce qui est un acquis à ne pas perdre. |
| Accessibilité du site (`docs/rd/accessibilite-2026-10-17.md`) | Le balayage axe-core couvre les pages, pas le contenu audio : un nouvel objet d'accessibilité à documenter. |

## 5. Preuve — sources consultées

Chaque source est citée avec son éditeur, sa date et ce qu'elle permet d'affirmer. **Aucune n'a été lue intégralement** : les pages citées le sont pour le passage qui les concerne.

### 5.1 Conseil de l'Europe — CEFR, compétence phonologique (page institutionnelle)

Publié par le Conseil de l'Europe, page « Phonological competence » du CEFR, consultée le 20 octobre 2026.
<https://www.coe.int/en/web/common-european-framework-reference-languages/phonological-competence>

- La nouvelle échelle de phonologie comporte **trois sous-échelles** : contrôle phonologique global, articulation des sons, traits prosodiques.
- La page affirme que la phonologie « tend encore à ne pas être enseignée explicitement » et que des enseignants manquent de confiance, faute de formation spécifique.
- Elle affirme que l'échelle de 2001 donnait l'impression d'une progression vers un locuteur natif, alors que **la recherche montre que l'intelligibilité prime sur l'accent**.

**Ce que cela ne prouve pas :** qu'une fiche de site améliore l'intelligibilité ; que les repères de l'échelle soient adaptés à un exercice autonome ; que la présentation de la page suffise à fonder une progression. La page résume des travaux sans les détailler.

L'échelle détaillée elle-même figure dans le *Companion Volume* (Conseil de l'Europe, 2020), que **je n'ai pas ouvert** ; son contenu n'est donc pas cité ici.

### 5.2 W3C — WCAG 2.2, critère 1.2.1 « Audio-only and Video-only (Prerecorded) »

Recommandation du W3C, version 2.2 ; page « Understanding SC 1.2.1 », consultée le 20 octobre 2026.
<https://www.w3.org/WAI/WCAG22/Understanding/audio-only-and-video-only-prerecorded.html>

- Pour tout contenu **audio seul préenregistré**, une **alternative pour les médias temporisés** présentant une information équivalente est exigée (niveau A).
- L'intention de ce critère est de rendre l'information audible disponible à tous : un texte se rend par tout canal, y compris l'écran, la synthèse vocale, le braille.

**Ce que cela ne prouve pas :** que l'alternative textuelle suffise à **apprendre** une prononciation ; que la conformité WCAG rende un exercice oral utilisable. Conformité technique n'est pas utilité pédagogique.

### 5.3 W3C — WCAG 2.2, critère 1.4.2 « Audio Control »

Même recommandation ; page « Understanding SC 1.4.2 », consultée le 20 octobre 2026.
<https://www.w3.org/WAI/WCAG22/Understanding/audio-control.html>

- Tout audio qui se déclenche automatiquement pendant plus de trois secondes doit pouvoir être **arrêté** ou réglé indépendamment du volume système (niveau A).
- La page **déconseille** le démarrage automatique et recommande que le son soit déclenché par une action volontaire de la personne.

**Ce que cela ne prouve pas :** qu'un son déclenché par l'utilisateur soit utilisable avec un lecteur d'écran dans tous les cas ; que la présence d'un bouton suffise à l'accessibilité réelle.

## 6. Forme d'apprentissage visée

| Action observable | Forme candidat | Pourquoi |
| --- | --- | --- |
| Reconnaître un son écrit (graphème) et savoir **quoi faire de sa bouche** pour le produire | Fiche autonome, texte d'abord, sans audio obligatoire | Ne dépend d'aucun fichier son, donc reste utilisable hors ligne, imprimée et avec un lecteur d'écran. |
| Distinguer deux sons proches | Exercice écrit de comparaison, avec transcription | Apprentissage partiel et honnête : on peut comparer des descriptions, pas s'écouter. |
| S'entraîner à l'écoute réelle | **Rien dans un premier temps** | Aucun audio du M.R.S.C. n'existe ; produire une voix synthétique pose des questions de droits et de consentement non tranchées. |

**Contrainte matérielle constatée :** le dépôt ne contient **aucun fichier audio**, aucune voix enregistrée ni autorisation de réutilisation. Toute piste sonore supposerait une décision associative et des droits documentés.

## 7. Statut et entretien

| Élément | État |
| --- | --- |
| Statut du sujet | `partiel` depuis le 20 octobre 2026 |
| Contenu publié | **une fiche**, `langue-anglais-prononcer-ed`, au statut « Prototype à relire » |
| Relecture experte | **non faite** ; à faire par une personne compétente en didactique des langues et en accessibilité |
| Essai avec des personnes | **aucun** |
| Relecture à prévoir | à la prochaine revue de portefeuille, au plus tard le 19 novembre 2026 |

## 8. Critères pour passer à une fiche

1. La source de l'échelle de phonologie (Companion Volume, 2020) est lue directement, et les niveaux cités le sont depuis le texte, pas depuis un résumé.
2. Une personne compétente a relu la description des sons retenus pour la variété de français ou d'anglais choisie, et cette variété est nommée.
3. La fiche reste entièrement utilisable **sans audio** ; si un audio est ajouté, il est déclenché par une action volontaire, arrêtable, et accompagné d'une alternative textuelle.
4. Aucun enregistrement de voix d'apprenant n'est collecté, et aucune correction automatique n'est promise.
5. Les limites sont écrites dans la fiche : absence d'audio, variété non universelle, aucun effet d'apprentissage mesuré.

## 9. Première fiche produite

Le 20 octobre 2026, un premier point a été traité : **la fin -ed des verbes anglais**, dans `apprendre/fiches/langue-anglais-prononcer-ed.html`.

- **Ce qui est couvert :** les trois prononciations /t/, /d/ et /ɪd/ ; la règle du dernier *son* et non de la dernière lettre ; le fait que seul /ɪd/ ajoute une syllabe ; un exercice écrit de classement.
- **Ce qui n'est pas couvert :** aucun son n'est diffusé, aucune prononciation n'est écoutée ni corrigée. La fiche aide à **décider** comment se prononce une forme, pas à l'entendre ni à l'évaluer.
- **Sources :** Britannica Dictionary (règle et exemples) et la page « compétence phonologique » du CEFR (intelligibilité avant accent), consultées le 20 octobre 2026.
- **Statut :** « Prototype à relire ». Une personne compétente en didactique de l'anglais doit vérifier les exemples et la progression ; aucune validation n'est revendiquée.

## 10. Ce qui reste à faire, dans l'ordre

1. Lire l'échelle de phonologie du *Companion Volume* 2020 et en extraire uniquement les descripteurs utilisables en autonomie.
2. Choisir **un** point de prononciation précis (par exemple un contraste de voyelles), écrire la fiche, la garder en « Prototype à relire ».
3. Faire relire par une personne compétente ; consigner les objections.
4. Seulement ensuite, décider s'il faut un audio, et sous quelles conditions de droits.

Régénérer la [carte des lacunes](carte-lacunes.md) après toute modification du référentiel ; cette carte y apparaît comme travail ouvert sur le sujet `ecoute-prononciation`.
