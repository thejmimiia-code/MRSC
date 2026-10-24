# Initiative R&D — écouter la page

- Date d'ouverture : `2026-10-23`
- État : `a-valider`
- Phase : `prototype`
- Rôles à mobiliser : `agent / accessibilité / éditorial` — **aucun essai avec des personnes n'a eu lieu**
- Domaine(s) et contexte(s) : `langue-communication`, `methodes-communication`, `langues-etrangeres` ; toutes les pages du site
- Source de vérité / initiative liée : [`prospective-2027-2030.md`](prospective-2027-2030.md) § 5, décisions 4 et 10 ; [`portefeuille.toml`](portefeuille.toml) `ecouter-la-page`
- Prochaine revue souhaitée : à la première relecture par un rôle accessibilité — pas de date promise

## Signal et question

Le site est lisible au clavier, au zoom et sous contraste renforcé, et un balayage automatique de 49 états de pages n'y trouve aucune violation détectable. Ce constat mesure des **règles** ; il ne dit rien de la difficulté réelle d'une personne qui décode lentement, qui voit peu, ou dont la fatigue visuelle arrive au bout de deux paragraphes.

**Question posée :** peut-on rendre le contenu principal *audible* sur l'appareil de la personne, sans compte, sans envoi de texte et sans dépendre d'un service distant — et à quelles conditions cela reste-t-il une aide plutôt qu'une fausse promesse ?

Trois faits externes donnent le cadre, aucun ne prouve l'utilité **de ce site** :

| Fait | Source directe | Ce que cela permet d'affirmer | Ce que cela ne dit pas |
| --- | --- | --- | --- |
| En 2025, 7 % des 16-74 ans sont en situation d'illectronisme et 27 % ont des compétences numériques faibles ; chez les 60-74 ans, 17 % et 38 %. | Insee Focus n° 376, *Une personne sur trois manque de compétences numériques*, 2025 — <https://www.insee.fr/fr/statistiques/8739245> | Une part importante du public visé n'est pas à l'aise avec un service en ligne, et les 60 ans et plus sont les plus concernés. | Rien sur la lecture à voix haute : ces chiffres mesurent l'usage des outils, pas les besoins de lecture. |
| Une méta-analyse de 22 études (2 942 participants, primaire à supérieur) trouve un effet moyen pondéré de `d = 0,35` (IC 95 % : 0,14–0,56) de la synthèse vocale et de la lecture à voix haute sur la compréhension en lecture d'élèves ayant des difficultés de lecture. | Wood, Moxley, Tighe & Wagner, *Does Use of Text-to-Speech and Related Read-Aloud Tools Improve Reading Comprehension for Students With Reading Disabilities? A Meta-Analysis*, Journal of Learning Disabilities 51(1), 2018, p. 73-84 — <https://doi.org/10.1177/0022219416688170> | L'effet est positif, **modéré**, et les auteurs signalent une grande variabilité entre études (0,61 en inter-sujets, 0,15 non significatif en intra-sujet). | Population scolaire en anglais, mesures de compréhension, contextes d'accompagnement explicite. Rien n'autorise à transposer le chiffre à un site adulte francophone. |
| Une méta-analyse de 15 études (688 participants) sur les polices dites « pour dyslexiques » trouve un effet négligeable (`g = -0,04`, IC 95 % : -0,15–0,07). | *Does font improve reading in dyslexic children?*, Annals of Dyslexia, 2026 — <https://link.springer.com/article/10.1007/s11881-026-00389-8> | Un réglage « police spéciale » n'aurait probablement pas tenu la promesse qu'on lui prête. | Ne dit rien de l'espacement, de la taille ou du contraste, qui restent réglables séparément sur le site. |

Ces trois références ont été ouvertes ou lues le 23 octobre 2026 ; elles servent de **repères de décision**, pas de preuve d'efficacité locale.

## État existant et limites

- **Déjà disponible :** crans de texte 75/85/100/115/130 %, contraste renforcé, espacement renforcé, quatre présentations de page, navigation clavier vérifiée, aucune police distante, aucune lecture automatique.
- **Personnes et contextes concernés, sans persona inventé :** toute personne qui lit lentement, qui fatigue vite, qui écoute mieux qu'elle ne lit, ou qui consulte en marchant. Aucune d'entre elles n'a été interrogée.
- **Contexte pertinent :** français principal, quelques répliques anglaises dans les Escales, appareils modestes, réseaux parfois faibles.
- **Exclusions, prérequis, inconnues :** la voix est celle du système ; elle peut manquer entièrement (poste sans voix installée, navigateur sans moteur) ; la prononciation des sigles et des noms propres n'est pas maîtrisée ; aucune mesure de compréhension n'existe ici.

## Recherche et registre d'affirmations

| Affirmation ou question | Source directe | Consultée le | Ce que la source permet d'affirmer | Limites, contre-sources |
| --- | --- | --- | --- | --- |
| Une déclaration de conformité ne vaut pas mesure. L'Arcom a mis en demeure un service public en juin 2026 pour un espace déclaré « totalement conforme » alors qu'un audit mesurait 42,11 %. | Arcom, décision n° 2026-358 du 24 juin 2026 — <https://www.legifrance.gouv.fr/jorf/id/JORFTEXT000054393304> | 23 oct. 2026 | Le site ne doit publier **aucun** taux de conformité RGAA/WCAG qu'il n'a pas audité. | Le cas concerne un autre service ; il illustre un risque documentaire, pas une faute du M.R.S.C. |
| Le référentiel applicable en France en 2026 reste le RGAA 4.1.2, aligné sur WCAG 2.1 AA ; une version 5 est annoncée pour fin 2026. | DINUM, *Nouvelle version du RGAA*, 4 mars 2026 — <https://www.numerique.gouv.fr/actualites/nouvelle-version-rgaa-2026/> | 23 oct. 2026 | Toute revendication de conformité exigerait un audit externe sur 106 critères ; ce n'est pas le cas ici. | Rien n'indique qu'un audit soit prévu par l'association. |
| Une aide technique peut être annoncée par `aria-live` sans interrompre une personne déjà en train de lire. | Spécification WAI-ARIA (`aria-live="polite"`), pratique déjà employée sur le site pour les autres réglages | 23 oct. 2026 | L'état de la lecture peut être annoncé aux aides techniques sans voler le focus. | Aucun lecteur d'écran réel n'a été testé sur cette commande. |

## Options de conception

| Option | Valeur attendue / hypothèse | Coût et dépendances | Accessibilité / confidentialité / droits | Pourquoi garder ou écarter |
| --- | --- | --- | --- | --- |
| **A. Lecture à voix haute locale** (retenue) | Écouter `main` avec la voix de l'appareil, segment par segment, avec arrêt et pause. | ~150 lignes de JS, aucune dépendance, aucun fichier audio, aucun coût d'hébergement. | Aucun envoi réseau ; pas de stockage ; dépend d'une voix installée. | Tenable dans les quatre scénarios de la note prospective, y compris réseau coupé après chargement. |
| **B. Fichiers audio enregistrés** | Voix humaine maîtrisée, prononciation correcte, écoute hors ligne complète. | 84 fiches × plusieurs minutes : octets, droits, relecture, remise à jour à chaque correction de texte. | Excellente accessibilité ; risque de dérive de version entre texte et audio. | **Écartée** : coût de maintenance incompatible avec un dépôt statique et une rédaction encore mouvante. |
| **C. Service de synthèse distant** | Voix naturelles, multilingue, réglages fins. | Clé d'API, coût par caractère, disponibilité, confidentialité du texte lu. | Le texte de la personne quitte l'appareil ; dépendance à un tiers. | **Écartée** : contredit frontalement la décision 4 de la note prospective (pas de service tiers obligatoire). |
| **D. Compter sur les lecteurs d'écran seuls** | Aucun code ajouté ; la personne utilise déjà son outil. | Nul. | Les lecteurs d'écran restent l'outil de référence des personnes aveugles. | **Écartée comme réponse unique** : elle ne sert pas la personne qui voit mais lit lentement, et suppose un équipement et un apprentissage que rien n'indique ici. |
| **E. Ne rien construire** | Consacrer le temps à la relecture de contenu. | Nul. | — | Option de repli si le prototype s'avère inutilisable en relecture. |

## Prototype retenu

- **Tâche de la personne :** faire lire le contenu principal, suivre où la voix en est, arrêter net, reprendre.
- **Objectif observable :** la page parle sans quitter l'appareil, et chaque bloc lu est désigné visuellement.
- **Rendu original à produire :** aucun — la voix est celle du système, il n'y a pas d'enregistrement à publier.
- **Critères de réussite définis avant l'essai :** la commande n'existe que si le moteur existe ; aucun caractère n'est émis avant un geste ; aucune requête réseau pendant la lecture ; la langue de chaque bloc est respectée ; l'arrêt coupe vraiment la voix ; le texte n'est lu qu'une fois.
- **Critères d'arrêt ou de retrait :** si la commande s'affiche sans moteur, si un bloc est lu deux fois ou si le texte collé entre deux blocs rend l'écoute incompréhensible, le lot est retiré avant relecture.
- **Solution de repli :** le texte reste intégralement lisible et imprimable, les crans de taille et le contraste restent disponibles ; rien n'est conditionné à l'écoute.

### Ce qui est construit

- Une commande **« Écouter la page »** dans le panneau *Personnalisation*, en dernier, après les réglages de présentation. L'en-tête compact garde exactement deux boutons.
- Elle n'est créée que si `speechSynthesis` **et** `SpeechSynthesisUtterance` existent : sur un appareil sans moteur, le panneau n'affiche rien plutôt qu'un bouton mort.
- Lecture du seul contenu `main`, par blocs (`h1`–`h6`, `p`, `li`, `blockquote`, `figcaption`, `summary`, `td`, `th`, `dt`, `dd`), en écartant ce qui est masqué, replié, `aria-hidden` ou `visually-hidden`, et tout bloc qui en contient un autre pour éviter la double lecture.
- Chaque bloc est découpé à 220 caractères au plus, de préférence après une ponctuation forte au-delà du premier tiers. Un bloc sans ponctuation finale reçoit un point, sinon deux blocs s'entendent collés.
- La langue est lue sur le bloc ou son plus proche ancêtre : une réplique anglaise des Escales est prononcée par une voix anglaise.
- **Deux gestes ajoutés le 23 octobre 2026, après la première mise en ligne** : un bouton « Reculer » qui rejoue le passage précédent, et un choix de vitesse à quatre crans (lente, normale, rapide, très rapide). Le débit s'applique immédiatement en reprenant le passage courant, sans repartir du début. La vitesse choisie est conservée sous la clé `mrsc-lecture-vitesse` ; rien d'autre n'est stocké.
- **Pourquoi ces deux gestes.** Une revue des travaux sur le débit de parole montre deux choses : le contrôle du débit par la personne améliore la compréhension dans plusieurs contextes, et le rythme préféré est très variable d'une personne à l'autre — un débit imposé sert mal tout le monde. Les études sur l'aphasie (25 adultes, 113/154/200 mots par minute) ne trouvent pas d'effet significatif de la vitesse sur la compréhension *en groupe*, mais concluent explicitement à la nécessité de respecter les préférences individuelles ([PubMed 31689376](https://pubmed.ncbi.nlm.nih.gov/31689376/)) ; une étude de 1997 avec contrôle du débit par l'auditeur trouve un gain de compréhension ([Applied Linguistics 18(1)](https://academic.oup.com/applij/article-abstract/18/1/49/233475)). Rien de tout cela ne mesure ce site : ces sources justifient de **donner le choix**, pas d'affirmer un gain.
- Boutons « Lire à voix haute » → « Arrêter » (nom accessible complet), plus « Pause » / « Reprendre » avec `aria-pressed`. Au repos, le bouton n'a pas de nom redondant ; le nom accessible contient toujours le texte visible, ce qu'axe contrôle (`label-content-name-mismatch`) et qu'une personne dictant à la voix exige. Un état `role="status" aria-live="polite"` annonce le début, la pause, la reprise, la fin, l'échec du moteur et l'absence de texte.
- Le bloc en cours est marqué par un contour de 3 px (et `Highlight` en mode contraste forcé), jamais par un changement de taille : rien ne doit sauter sous les yeux. Le défilement vers le bloc n'est animé que hors `prefers-reduced-motion`.
- Quitter la page annule la lecture (`pagehide`) : la voix ne survit pas à la navigation.
- **Trois pièges de moteur traités explicitement.** Sur Chromium, une annulation volontaire remonte comme une erreur `interrupted` : elle est filtrée, sinon « Arrêter » annoncerait une panne. `cancel()` suivi d'un `speak()` dans le même tour est parfois perdu : la première énonciation part au tour suivant. Et « Reprendre » ne relance pas le segment suivant — il ne relance la file que si le moteur n'a plus rien en cours, faute de quoi un segment serait lu deux fois.
- Aucun `localStorage`, aucune requête, aucun tiers.

## Vérifications et résultat

| Contrôle | Qui / rôle | Méthode, date | Résultat / preuve | À corriger |
| --- | --- | --- | --- | --- |
| Technique | agent | `python3 outils/verifier-affichages.py` — 23 oct. 2026 | **15 garde-fous verts**, dont le nouveau : quatorze mutations du code ont été introduites une à une, en deux lots : langue ignorée, arrêt sans annulation, contenus masqués lus, `fetch` ajouté, marque visuelle supprimée, commande jamais ajoutée au panneau, nom accessible sans le texte visible, vitesses supprimées, débit ignoré, jeton de génération retiré des deux rappels puis d'un seul, retour arrière retiré, vitesse non conservée, cible du sélecteur abaissée ; puis virgule de continuation retirée, rendue inconditionnelle et longueur non décomptée ; **17 détectées sur 17**. | — |
| Enchaînement fonctionnel | agent | `node outils/test-experience.cjs` — 23 oct. 2026 | **9/9 essais**, dont un nouvel essai dédié : rien lu sans geste, libellés et états corrects, `lang` respecté, zéro requête réseau, arrêt effectif, réplique anglaise prononcée en `en`. | — |
| Accessibilité automatique | agent | `node outils/verifier-accessibilite.cjs` (axe-core 4.14.0) — 23 oct. 2026 | **49 exécutions, 0 violation** (47 auparavant ; deux états ajoutés pour le panneau avec écoute, à 360 et 1280 px). | — |
| Affichage | agent | captures Chromium à 320, 390, 430, 667×375, 844×390, 768 et 1440 px, à 100 % et 130 % — 23 oct. 2026 | Aucun débordement horizontal ; les deux commandes tiennent côte à côte à 320 px et 130 % ; le panneau défile et reste entièrement dans l'écran. | — |
| Lecture réelle | **personne** | — | **Non faite.** Aucune voix réelle n'a été écoutée : le banc remplace `speechSynthesis` par un double qui enregistre les énoncés. | Écoute réelle par une personne, sur au moins deux appareils. |
| Compréhension | **personne** | — | **Non faite.** Aucun essai d'usage, aucune mesure de compréhension. | À rattacher à `co-conception-et-essais`. |
| Lecteur d'écran | **personne** | — | **Non fait** ; aucun lecteur d'écran n'a été utilisé. | NVDA ou VoiceOver, au moins une passe. |

**Chiffres mesurés le 23 octobre 2026, à conserver :**

- Fiche type (`fr-lire-consigne`) : **49 segments** pour une lecture complète, 0 doublon, 0 phrase collée, tous en `fr`, aucun réseau.
- Escale anglaise (`anglais-aventure.html`, mission ouverte) : **534 segments**, dont la réplique `Hi there! Where would you like to go?` émise en `lang="en"`.
- Panneau à 320 px et 130 %, quatre commandes visibles : « Arrêter » 283 × 53, « Pause » 127 × 53, « Reculer » 145 × 53, sélecteur 153 × 44, toutes dans le panneau, débordement 0 px.
- Comportement vérifié : débit de départ 1 ; choix « très rapide » ⇒ prochaines énonciations à `rate = 1.5` et clé `mrsc-lecture-vitesse` = `1.5`, valeur restituée après rechargement ; « Reculer » rejoue **un seul** passage précédent ; un rappel tardif d'une énonciation annulée ne relance pas la file (jeton de génération).

## Décision et entretien

- **Décision :** `conserver en prototype` — publié, mesuré, **non validé par des personnes**.
- **Justification et limites affichées :** l'écoute est utile quand elle marche et silencieuse quand le moteur manque ; elle ne remplace ni un lecteur d'écran, ni une relecture éditoriale. La note affichée sous le bouton dit exactement cela : « La voix est celle de l'appareil : elle peut varier, manquer ou mal prononcer un mot. Rien n'est envoyé à un service distant. Cette lecture ne remplace pas un lecteur d'écran. »
- **Fichiers / identifiants touchés :** `assets/js/site.js` (module `construireLectureVocale`), `assets/css/site.css` (`.read-aloud*`, `.lecture-en-cours`), `outils/verifier-affichages.py` (contrôle `controler_lecture_a_voix_haute`), `outils/test-experience.cjs` (essai dédié), `outils/verifier-accessibilite.cjs` (deux états), `docs/rd/avancees.toml`, `docs/rd/portefeuille.toml`, `docs/rd/prospective-2027-2030.md`, `transparence.html`.
- **Commandes de test :** `python3 outils/verifier-affichages.py` · `node outils/test-experience.cjs` · `node outils/verifier-accessibilite.cjs` · `python3 outils/verifier-rd-continue.py`.
- **Prochaine action, rôle requis :** faire écouter la fonction à une personne qui lit difficilement et à une personne utilisant un lecteur d'écran ; noter les mots mal prononcés et les endroits où la voix perd le fil. Rôle : accessibilité. Aucune échéance promise.
- **Indicateur de maintenance / signal d'actualisation :** si le sélecteur de blocs, la liste des réglages du panneau ou le mécanisme `pagehide` change, le contrôle des 15 garde-fous et l'essai navigateur doivent être rejoués ; un échec de l'un ou de l'autre suffit à retirer la commande.
- **Données personnelles collectées :** `aucune`. Pas de stockage, pas de mesure d'écoute, pas d'envoi du texte.

## Ce que ce lot ne prouve pas

1. **Aucune conformité.** Ni RGAA 4.1.2, ni WCAG 2.1 AA. Aucun des 106 critères n'a été audité ; un balayage axe-core sans violation ne vaut pas audit.
2. **Aucun effet mesuré sur la compréhension.** L'effet `d = 0,35` vient d'études scolaires en anglais sur des outils de lecture à voix haute ; il ne se transporte pas ici.
3. **Aucune voix éprouvée.** Le banc de test ne fait pas de son. Qu'une voix manque, qu'elle bute sur « M.R.S.C. » ou qu'elle lise « 1 200 » de travers reste possible et visible seulement à l'oreille.
4. **Aucun essai avec des personnes.** Le registre des relectures humaines reste vide ; ce prototype est une hypothèse instruite, pas un résultat.
