# Carte de sujet — Microcontrôleurs, objets connectés et systèmes embarqués

**Statut : à documenter.** Cette carte ouvre un sujet du référentiel qui n'a **aucune fiche** (`informatique-programmation` → `systemes-embarques`, `statut = a-creer`). Elle ne contient aucune fiche, aucun programme exécutable sur matériel et aucune promesse de sécurité. Elle rassemble ce que trois sources institutionnelles ouvertes et lues le 20 octobre 2026 permettent d'affirmer, ce qu'elles ne permettent pas, et la forme que pourrait prendre un premier prototype écrit.

**Date de consultation des sources : 20 octobre 2026.** Rédigée par un agent, sans relecture experte ni essai avec des personnes.

## 1. Identité

| Dimension | Contenu |
| --- | --- |
| Sujet du référentiel | Informatique, algorithmique et langages de programmation → « Microcontrôleurs, objets connectés et systèmes embarqués » (`statut = a-creer`) |
| Ce dont il s'agit | Comprendre comment un programme enfoui dans un objet relie des mesures physiques (capteurs), une règle de décision (algorithme), une interface (IHM) et une action matérielle (actionneur), ainsi que ce que change l'ajout d'une liaison réseau (collecte, commande à distance, mise à jour, exposition aux pannes et aux attaques). |
| Ce dont il ne s'agit pas | Ni un guide de câblage électrique ou d'intervention sur le secteur, ni un manuel de sécurisation industrielle certifiée, ni un banc de programmation nécessitant d'acheter une carte électronique. |

## 2. Besoin

La question de départ, formulée sans interprétation d'usage : **comment distinguer ce qu'un objet informatisé mesure, décide localement ou transmet sur un réseau, sans posséder de matériel électronique ni confondre automatisme local et objet connecté ?**

Trois constats issus des sources consultées rendent la question utile :

- le programme de Sciences numériques et technologie (SNT) de seconde souligne que l'informatique embarquée interagit directement avec le monde physique via des **capteurs**, des **algorithmes de contrôle**, une **interface homme-machine (IHM)** et des **actionneurs**, avec une distinction entre **sûreté** (absence d'erreurs face aux risques physiques) et **sécurité** (résistance aux attaques) ;
- la ressource pédagogique Éduscol associée distingue un **périphérique**, une **interface connectée** et un objet relevant de l'**Internet des objets** (qui traite et génère lui-même des informations), et rappelle les trois motifs d'adoption des technologies d'Internet : collecter des données, envoyer des consignes à distance et mettre à jour le logiciel embarqué (*firmware*) ;
- le guide `ANSSI-PA-087` rappelle que les dispositifs connectés combinent effets physiques, autonomie élevée, ressources matérielles et énergétiques limitées, et manipulation de données d'apparence anodine (consommation électrique, allumage d'ampoules, positions instantanées) qui renseignent pourtant sur la présence ou les habitudes des personnes.

Aucun de ces éléments ne prouve un besoin mesuré chez les visiteurs du M.R.S.C. : **aucune observation d'usage n'existe** à ce jour.

## 3. Portée

**Dedans :** la boucle fonctionnelle `capteur → traitement / programme → actionneur` et le rôle de l'IHM ; la différence entre système embarqué autonome et objet connecté à Internet ; les enjeux de confidentialité des données mesurées, de dépendance réseau et de mise à jour logicielle ; des exercices faisables entièrement par écrit à partir de situations fictives.

**Dehors :** tout branchement sur le réseau électrique domestique (`securite-electricite` relève d'une relecture experte distincte) ; le diagnostic d'un appareil réel ou médical ; l'administration de systèmes industriels ; l'obligation de disposer d'un microcontrôleur physique ou d'un simulateur tiers en ligne.

**Limite de contexte :** les documents consultés émanent du ministère de l'Éducation nationale et de l'ANSSI (France). Ils posent des repères conceptuels et d'analyse de risque, pas des normes universelles ni une conformité réglementaire.

## 4. Relations

| Sujet voisin | Lien |
| --- | --- |
| `sci-capteur-signal-actionneur` (fiche existante, `sciences-techniques-environnement`) | Pose déjà la chaîne capteur → signal → actionneur côté sciences ; une fiche informatique devra se concentrer sur le programme embarqué, l'IHM et la connexion réseau sans dupliquer cette fiche. |
| `info-entree-traitement-sortie` et `info-condition-si-sinon` (fiches existantes) | Fournissent le modèle entrée → traitement → sortie et le branchement conditionnel utilisés par un algorithme de contrôle. |
| `info-systeme-exploitation` et `info-adresse-ip-dns` (fiches existantes) | Éclairent la différence entre un système complet et un micrologiciel contraint, ainsi que la liaison réseau d'un objet connecté. |
| `securite-electricite` (`revue-experte`, sans fiche) | Frontière stricte : aucune manipulation électrique réelle ne doit être proposée dans `systemes-embarques`. |

## 5. Preuve — sources consultées

Chaque source a été ouverte et lue le 20 octobre 2026 pour les passages cités. Aucun texte n'en est recopié dans le catalogue.

### 5.1 Ministère de l'Éducation nationale — Programme de SNT de seconde générale et technologique (PDF)

Annexe publiée au BO spécial n° 1 du 22 janvier 2019, section « Informatique embarquée et objets connectés », consultée le 20 octobre 2026.
<https://eduscol.education.fr/document/23494/download>

- Capacités attendues : identifier des algorithmes de contrôle des comportements physiques à travers les données des **capteurs**, l'**IHM** et les actions des **actionneurs** dans des systèmes courants ; réaliser une IHM simple ; écrire des programmes simples d'acquisition de données ou de commande d'un actionneur (ex. table de correspondance entre chaîne reçue `"A50"` et commande d'un moteur à 50 %).
- Distinction explicite entre **sûreté** (absence d'erreurs lorsque le système interagit avec le monde physique) et **sécurité** (résistance aux attaques), avec le constat que dans de nombreux objets connectés moins critiques, la sécurité reste souvent un point faible.

**Ce que cela ne prouve pas :** qu'un exercice papier suffise à programmer un microcontrôleur réel, ni que l'exemple d'une table de correspondance couvre les pannes matérielles ou les délais temps réel.

### 5.2 Éduscol — SNT 2de : « Informatique embarquée et objets connectés — Activité 2 : Impact et importance de l'informatisation des objets » (PDF)

Ressource d'accompagnement Éduscol (juin 2019), ouverte et lue intégralement le 20 octobre 2026.
<https://eduscol.education.fr/document/23560/download>

- Énonce trois motifs d'emploi des technologies génériques d'Internet pour les objets connectés : collecter des données pour les analyser, envoyer des consignes et commandes depuis un terminal, et mettre à jour le logiciel embarqué (*firmware*).
- Propose une distinction pratique entre **périphérique** (ex. imprimante reliée à un ordinateur), **interface connectée** (ex. tablette réglant un chauffage) et **Internet des objets** (objet qui traite et génère lui-même des informations).

**Ce que cela ne prouve pas :** les catégories de l'activité scolaire (« périphérique », « interface connectée », « internet des objets ») se chevauchent selon les usages (le document le note lui-même pour le smartphone) ; elles servent à questionner le rôle d'un objet, pas à établir une taxonomie normative.

### 5.3 ANSSI — *Recommandations relatives à la sécurité des (systèmes d')objets connectés* (`ANSSI-PA-087`, PDF)

Guide technique de l'Agence nationale de la sécurité des systèmes d'information, version 1.0 du 27 août 2021, publié sous **Licence Ouverte v2.0** (Etalab), consulté le 20 octobre 2026 (chapitres 1 et 2).
<https://messervices.cyber.gouv.fr/documents-guides/anssi-guide-securite_des_systemes_objets_connectes_iot-v1.0.pdf>

- Définit un *dispositif connecté* par une liaison numérique supportant plusieurs rôles (transfert de données, commande, mise à jour), une interaction physique fréquente via des capteurs et/ou des actionneurs, une capacité d'intervention humaine réduite et des ressources de calcul, de stockage et d'énergie limitées.
- Souligne deux risques spécifiques : d'une part, des données d'apparence anodine (positions successives, consommation électrique, fonctionnement d'ampoules connectées) permettent de déduire la présence ou les habitudes des personnes ; d'autre part, la fiabilité du signal physique en amont du capteur ne relève pas de la seule sécurité logicielle et appelle une analyse de risque (dont la redondance de capteurs).

**Ce que cela ne prouve pas :** ce guide s'adresse aux concepteurs et administrateurs de systèmes connectés ; il ne constitue ni une liste de gestes suffisants pour un particulier, ni une certification de sécurité.

## 6. Forme d'apprentissage visée

| Action observable | Forme candidate | Pourquoi |
| --- | --- | --- |
| Distinguer dans un objet décrit par écrit ce qui relève du capteur, de la règle programmée, de l'actionneur, de l'IHM et de la liaison réseau éventuelle | Fiche autonome, texte d'abord, sans matériel ni simulateur externe | Utilisable hors ligne, au clavier et avec un lecteur d'écran ; évite toute manipulation électrique. |
| Identifier ce qui continue ou cesse de fonctionner si la liaison réseau tombe (commande distante vs règle locale) | Exercice écrit de comparaison sur un cas fictif (ex. programmateur d'arrosage ou de chauffage fictif) | Rend concret l'écart entre automatisme embarqué local et dépendance à un service distant. |

**Garde-fou vis-à-vis de `sci-capteur-signal-actionneur` :** avant de rédiger une fiche, vérifier phrase par phrase qu'elle ne répète pas la fiche de sciences existante, mais porte spécifiquement sur la **règle logicielle embarquée, l'IHM et l'écart entre fonctionnement local et objet connecté**.

## 7. Statut et entretien

- **Statut du sujet dans `referentiel.toml` :** reste `a-creer` tant qu'aucune fiche n'est rédigée et inscrite au catalogue.
- **Exigence avant publication d'une fiche :** sources primaires datées (présentes ci-dessus), rédaction au statut « Prototype à relire », contrôle mécanique (`auditer-prototypes.py`), puis relecture éditoriale et contrôle d'accessibilité.
- **Prochaine action :** rédiger une première fiche prototype centrée sur la distinction entre automatisme embarqué local, interface homme-machine et liaison réseau d'un objet connecté (en vérifiant l'absence de doublon avec `sci-capteur-signal-actionneur`), ou faire d'abord relire cette carte de sujet.
