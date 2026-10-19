# Vote distanciel — premiers écarts et inconnues des candidats

**Relevé du 17 octobre 2026. Statut : lecture documentaire partielle, à expertiser.** Cette note examine uniquement quelques fichiers épinglés des trois dépôts candidats. Elle ne constitue ni audit, ni comparaison complète, ni recommandation.

## Méthode

Les fichiers ont été lus à leurs commits consignés dans [`vote-distanciel-sources.toml`](vote-distanciel-sources.toml), via l’API GitHub. Les formulations ci-dessous décrivent ce que les projets annoncent eux-mêmes. Aucune propriété n’a été reproduite, aucun logiciel n’a été installé et aucun bulletin n’a été créé.

## Belenios

### Éléments observés

- Le [README épinglé](https://github.com/glondu/belenios/blob/8888045a7650df5241a76ae75128ebde61e83904/README.md) décrit quatre rôles principaux et indique que leur séparation renforce la configuration.
- Le [guide de l’outil](https://github.com/glondu/belenios/blob/8888045a7650df5241a76ae75128ebde61e83904/doc/tool.md) décrit un fichier d’élection évoluant de façon append-only et une commande de vérification. Il indique aussi que l’autorité d’identifiants peut conserver un fichier reliant identité et justificatif privé afin de renvoyer celui-ci.
- La [spécification épinglée](https://github.com/glondu/belenios/blob/8888045a7650df5241a76ae75128ebde61e83904/doc/specification.tex) annonce une preuve portant sur confidentialité du bulletin et vérifiabilité du protocole, sous hypothèse de sécurité des primitives. Elle décrit une structure de justificatifs publics comprenant justificatif public, poids et identité du votant, ainsi qu’une chaîne de données publiques.

### Écarts ou inconnues à résoudre

- Déterminer exactement quelles identités ou alias deviennent publics selon la configuration et si cela respecte la séparation exigée par le M.R.S.C.
- Examiner le compromis entre récupération d’un justificatif perdu et destruction du lien identité–justificatif privé.
- Retrouver et faire lire les preuves et audits indépendants correspondant exactement à la version candidate et à ses primitives.
- Vérifier l’amont GitLab : le dépôt GitHub observé se présente comme miroir.

Aucun de ces points ne démontre une vulnérabilité. Ils empêchent seulement de classer Belenios comme adapté sans travail supplémentaire.

## Helios

### Éléments observés

- Le [README épinglé](https://github.com/benadida/helios-server/blob/88621e3196961ec03fe54bbd3a1c2196e715e9a2/README.md) se limite essentiellement à présenter Helios comme système vérifiable de bout en bout.
- Le [modèle de page de confidentialité épinglé](https://github.com/benadida/helios-server/blob/88621e3196961ec03fe54bbd3a1c2196e715e9a2/server_ui/templates/privacy.html) annonce la conservation du nom, du courriel et d’informations d’éligibilité. Il annonce aussi la conservation des métadonnées complètes du vote — lieu, heure et fréquence — accessibles aux administrateurs, et parfois la publication du fait d’avoir voté, de l’heure et du numéro de suivi.
- Ce même fichier décrit plusieurs fournisseurs d’authentification externes possibles.

### Écarts ou inconnues à résoudre

- Les pratiques annoncées de journalisation et de publication ne satisfont pas, en l’état de cette lecture, l’objectif de minimisation du M.R.S.C. Il faut vérifier ce qui est configurable, supprimable et effectivement journalisé dans une version candidate.
- Définir un parcours sans fournisseur social tiers et vérifier tous les flux d’identité, de réseau et d’administration.
- Retrouver la spécification, le modèle de menace, les audits indépendants et une version déployable maintenue.

Cette lecture d’un modèle HTML n’est pas une mesure d’un service en production. Elle suffit toutefois à maintenir le critère métadonnées comme bloquant.

## ElectionGuard

### Éléments observés

- Le [README épinglé](https://github.com/Election-Tech-Initiative/electionguard/blob/c6786d8bab5c15f33181dadf91b919541aae0ffd/README.md) décrit un SDK, un cœur C++ et des composants liés pour chiffrement, cérémonies et artefacts d’élection.
- Le [fichier SECURITY épinglé](https://github.com/Election-Tech-Initiative/electionguard/blob/c6786d8bab5c15f33181dadf91b919541aae0ffd/SECURITY.md) fournit un canal générique de signalement coordonné. Ce n’est pas un rapport d’audit du protocole ou d’une intégration.
- La dernière release retournée par l’API GitHub est `v2.1` du 15 août 2024, tandis que le commit de branche relevé date du 10 juin 2026.

### Écarts ou inconnues à résoudre

- Choisir une version cohérente de chaque composant et documenter leur compatibilité.
- Définir l’application complète autour du SDK : identité, éligibilité, urne, exploitation, journaux, interface accessible, reprise et contestation.
- Retrouver les spécifications et audits indépendants couvrant à la fois le protocole, les bibliothèques et l’intégration candidate.

ElectionGuard ne peut pas être comparé comme un service prêt à l’emploi sans définir l’architecture qui l’entoure.

## Décision de cette passe

Aucun candidat ne franchit encore un critère bloquant. Cela ne signifie pas qu’ils échouent : les preuves adaptées n’ont pas été rassemblées. La prochaine recherche doit partir du profil statutaire choisi, puis examiner seulement les candidats compatibles avec la voie B ou C retenue.
