# Vote distanciel — protocole d’un banc d’essai entièrement synthétique

**Date : 17 octobre 2026. Statut : protocole à faire expertiser, aucun banc n’est construit.** Ce document définit comment un futur exercice pourrait invalider une architecture candidate sans identité, adhérent, bulletin ou décision réelle. Il ne donne aucune autorisation de développement ou de scrutin.

## 1. Question d’essai

Une solution existante candidate peut-elle produire des artefacts vérifiables, détecter les altérations prévues par le modèle de menace et préserver la séparation des rôles sur un jeu entièrement synthétique ?

L’exercice ne cherche pas à prouver qu’un système est « sûr ». Il cherche d’abord des raisons de l’écarter.

## 2. Données autorisées

Uniquement des données générées pour l’exercice :

- identifiants `electeur-synthetique-001` à `electeur-synthetique-N` sans correspondance humaine ;
- questions fictives sans enjeu associatif ou politique réel ;
- choix neutres tels que « option alpha », « option bêta » et « blanc » ;
- clés créées pour l’exercice et détruites à sa clôture ;
- horodatages et adresses réseau simulés lorsque le scénario l’exige ;
- journaux isolés du site public et supprimés selon un plan fixé avant l’exercice.

Sont interdits : nom, courriel, numéro d’adhérent, adresse, vote réel, opinion personnelle, donnée de terminal d’une personne, liste de membres ou copie de production.

## 3. Préconditions

Le banc reste bloqué tant que les éléments suivants ne sont pas réunis :

1. un seul profil de scrutin statutaire est choisi et relu ;
2. la solution candidate, sa version, sa licence et ses audits connus sont documentés ;
3. le diagramme des flux et la liste des journaux sont disponibles ;
4. les rôles d’émission, d’urne, de tableau public et de dépouillement sont séparés ;
5. les critères d’arrêt et les artefacts à conserver sont approuvés ;
6. aucun service public, compte réel ou secret de production n’est utilisé ;
7. les rôles cryptographie, droit, protection des données, opérations et accessibilité ont pu signaler leurs objections.

## 4. Méthode

Pour chaque cas du registre [`vote-distanciel-cas-essai.toml`](vote-distanciel-cas-essai.toml) :

1. figer la version de la solution et l’empreinte des artefacts ;
2. générer le jeu synthétique depuis une graine publiée pour permettre la répétition ;
3. exécuter d’abord le parcours nominal ;
4. injecter une seule altération définie, puis les combinaisons explicitement prévues ;
5. exécuter deux vérificateurs indépendants lorsque la propriété s’y prête ;
6. conserver résultat attendu, résultat observé, journaux minimisés et divergences ;
7. classer `détecté`, `non détecté`, `non testable` ou `test invalide` ;
8. arrêter l’exercice dès qu’une condition d’arrêt du modèle de menace est atteinte.

Aucun résultat ne doit être reformulé en certification. « Altération détectée dans ce cas » ne signifie pas « fraude impossible ».

## 5. Familles de cas

Le registre couvre au minimum :

- suppression, substitution, duplication et réordonnancement de bulletin ;
- bulletin chiffré différent de l’intention simulée ;
- tentative de corrélation par métadonnées ;
- collusion sous et au niveau du seuil ;
- perte de part de clé et récupération ;
- interruption réseau et reprise ;
- droit de vote dupliqué ou refusé ;
- artefact de construction différent du code annoncé ;
- conservation indue d’une donnée corrélable ;
- procuration synthétique au-delà du plafond statutaire choisi ;
- quorum et délai incohérents avec le profil choisi.

## 6. Verdicts et critères d’arrêt

- **Détecté :** l’altération produit une preuve vérifiable et les deux vérificateurs concordent.
- **Non détecté :** arrêt de la solution candidate pour la menace concernée.
- **Non testable :** aucune conclusion ; le manque de moyen ou de spécification reste bloquant.
- **Test invalide :** corriger le protocole et recommencer, sans réinterpréter le résultat.

Arrêt global si une identité réelle apparaît, si un secret sort de l’environnement isolé, si le vérificateur dépend du serveur principal, si une substitution passe inaperçue ou si la destruction des données synthétiques ne peut pas être démontrée.

## 7. Sorties attendues

- manifeste des versions et empreintes ;
- graine et générateur du jeu synthétique ;
- artefacts chiffrés fictifs ;
- résultats des vérificateurs ;
- tableau des écarts, sans score global ;
- journal d’incidents minimisé ;
- preuve de destruction des secrets et données transitoires ;
- décision humaine : écarter, corriger et retester, ou demander une expertise plus poussée.

## 8. Ce que le banc ne prouvera pas

Il ne reproduit pas la coercition réelle, la diversité des appareils, une attaque inconnue, la capacité opérationnelle sur la durée, la conformité juridique, l’accessibilité auprès de personnes, ni la sécurité d’une version future. Il ne remplace pas un audit indépendant ni une élection papier ou présentielle de secours.
