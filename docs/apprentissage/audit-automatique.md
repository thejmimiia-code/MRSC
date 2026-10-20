# Audit automatique des prototypes

**Document de travail généré.** Il exécute, fiche par fiche, les contrôles qu'un programme peut réellement trancher : présence et forme des champs, adresses et métadonnées de droits, dates de revue, référencement, doublons exacts, longueur des phrases, typographie, page générée, existence d'une page de source précise. Il ne lit aucune source, ne juge aucune formulation et ne relit rien.

**Ce que veut dire « tout est vert » :** aucun défaut mécaniquement détectable n'a été trouvé. Ce n'est ni une relecture, ni une validation, ni une autorisation de publication. La relecture humaine se consigne dans [`relectures.toml`](relectures.toml) et se contrôle avec `python3 outils/registre-relecture.py`.

**Trois états, pas deux.** Un contrôle est `ok`, `à corriger` — le fait est faux et réparable sans jugement — ou `constat` : la machine voit un fait exact, mais elle ne peut pas dire s'il est acceptable. Un constat n'est pas un défaut : il se nomme ici pour qu'une personne tranche, et il n'empêche pas la page publique de dire la vérité, à condition qu'elle le dise.

**Date de l'audit :** 2026-10-20.

## 1. État d'ensemble

| Mesure | Valeur |
| --- | ---: |
| Prototypes audités | 57 |
| Contrôles automatiques par fiche | 17 |
| Fiches sans aucun échec mécanique | 57 |
| Fiches avec au moins un échec | 0 |
| Échecs mécaniques au total | 0 |
| Fiches avec un constat à trancher par une personne | 10 |
| Constats nommés (ni échecs, ni validations) | 10 |

### Constats nommés, à trancher par une personne

Ces contrôles ont vu un fait exact que la machine ne peut pas juger. Rien n'est cassé : la fiche dit ce qu'elle fait, et une personne doit décider si cela suffit.

| Constat | Fiches concernées | Nombre |
| --- | --- | ---: |
| Au moins une source pointe une page précise, pas seulement un portail | arts-composer-formes, arts-lire-cartel, geo-decrire-paysage, geo-lire-legende-carte, histoire-comparer-sources, histoire-situer-siecle, info-systeme-exploitation, maths-equation-simple, maths-lire-echelle-graphique, maths-lire-tableau-croise | 10 |

Pour la ligne « page précise » : ces fiches ne citent que des portails (racine d'un site) et l'annoncent dans le champ `utilisation` — la machine vérifie cette phrase, pas sa pertinence. Sans page précise, la question 1 du §4 ne peut pas être tranchée en l'état : il faut soit ajouter une page consultée et vérifiée, soit garder le portail en connaissance de cause.

## 2. Ce que la machine a vu, sans le juger

| Fait mesuré | Valeur |
| --- | ---: |
| Sources déclarées au total | 99 |
| dont licence déclarée « non vérifiée » | 98 |
| Fiches sans aucune source | 0 |
| Prochaine revue la plus proche | 2027-01-09 (info-lire-adresse-web) |
| Fiches dont la revue de contenu est échue | 0 |

Ces nombres ne disent rien de la qualité d'une fiche. Ils disent ce qui est **déjà fait** et ce qui **reste à faire par une personne** : ouvrir les sources, vérifier les exemples, trancher les droits, éprouver l'analogie et l'usage réel.

## 3. Détail par fiche

| Fiche | Domaine | Contrôles passés | À corriger | Constats | Détail des échecs et des constats |
| --- | --- | ---: | ---: | ---: | --- |
| [Composer une image avec quelques formes](fiches/arts-composer-formes.html) | Arts, musique, création et culture | 16 | 0 | 1 | constat : Au moins une source pointe une page précise, pas seulement un portail (1 portail(s) assumé(s) par écrit : rien à confronter, à trancher par une personne) |
| [Lire une notice d’œuvre en séparant faits et interprétations](fiches/arts-lire-cartel.html) | Arts, musique, création et culture | 16 | 0 | 1 | constat : Au moins une source pointe une page précise, pas seulement un portail (1 portail(s) assumé(s) par écrit : rien à confronter, à trancher par une personne) |
| [Choisir une source publique adaptée à sa question](fiches/civ-choisir-source-publique.html) | Citoyenneté, médias et information | 17 | 0 | 0 | — |
| [Repérer l’échelle d’une institution avant de chercher le bon service](fiches/civ-reperer-echelle-institution.html) | Citoyenneté, médias et information | 17 | 0 | 0 | — |
| [Repérer une information électorale officielle](fiches/civ-reperer-info-electorale.html) | Citoyenneté, médias et information | 17 | 0 | 0 | — |
| [Trouver un service public et préparer un formulaire](fiches/civ-trouver-service-public.html) | Démarches, droits, sécurité et vie professionnelle | 17 | 0 | 0 | — |
| [Comparer deux prix à quantité égale](fiches/econ-comparer-prix-unitaires.html) | Budget, économie, consommation et travail | 17 | 0 | 0 | — |
| [Distinguer un intérêt d’un frais sur un crédit fictif](fiches/econ-distinguer-interet-frais.html) | Budget, économie, consommation et travail | 17 | 0 | 0 | — |
| [Lire une facture et repérer une échéance](fiches/econ-lire-facture.html) | Budget, économie, consommation et travail | 17 | 0 | 0 | — |
| [Lire une mention de garantie sur un ticket fictif](fiches/econ-lire-mention-garantie.html) | Budget, économie, consommation et travail | 17 | 0 | 0 | — |
| [Garder la trace d’une source pour la retrouver](fiches/recherche-conserver-reference.html) | Études supérieures, spécialités et recherche — post-bac au doctorat | 17 | 0 | 0 | — |
| [Distinguer un résumé et une citation sur une fiche fictive](fiches/recherche-distinguer-resume-citation.html) | Études supérieures, spécialités et recherche — post-bac au doctorat | 17 | 0 | 0 | — |
| [Lire une étude sans confondre résultats et certitudes](fiches/recherche-lire-etude.html) | Études supérieures, spécialités et recherche — post-bac au doctorat | 17 | 0 | 0 | — |
| [Formuler une question et une hypothèse de recherche](fiches/recherche-question-hypothese.html) | Études supérieures, spécialités et recherche — post-bac au doctorat | 17 | 0 | 0 | — |
| [Décrire un paysage sans lui faire dire trop](fiches/geo-decrire-paysage.html) | Géographie, territoire et espace | 16 | 0 | 1 | constat : Au moins une source pointe une page précise, pas seulement un portail (1 portail(s) assumé(s) par écrit : rien à confronter, à trancher par une personne) |
| [Lire une légende sur une carte](fiches/geo-lire-legende-carte.html) | Géographie, territoire et espace | 16 | 0 | 1 | constat : Au moins une source pointe une page précise, pas seulement un portail (1 portail(s) assumé(s) par écrit : rien à confronter, à trancher par une personne) |
| [S’orienter avec les points cardinaux](fiches/geo-points-cardinaux.html) | Géographie, territoire et espace | 17 | 0 | 0 | — |
| [Comparer deux sources sur un même événement](fiches/histoire-comparer-sources.html) | Histoire, chronologie et mémoire | 16 | 0 | 1 | constat : Au moins une source pointe une page précise, pas seulement un portail (1 portail(s) assumé(s) par écrit : rien à confronter, à trancher par une personne) |
| [Lire une frise chronologique et ordonner des événements](fiches/histoire-lire-frise.html) | Histoire, chronologie et mémoire | 17 | 0 | 0 | — |
| [Repérer l’échelle d’un événement : un lieu de France ou plusieurs pays](fiches/histoire-reperer-echelle-france-monde.html) | Histoire, chronologie et mémoire | 17 | 0 | 0 | — |
| [Situer une année dans un siècle](fiches/histoire-situer-siecle.html) | Histoire, chronologie et mémoire | 16 | 0 | 1 | constat : Au moins une source pointe une page précise, pas seulement un portail (1 portail(s) assumé(s) par écrit : rien à confronter, à trancher par une personne) |
| [Comprendre les bits et les octets](fiches/info-bits-octets.html) | Informatique, algorithmique et langages de programmation | 17 | 0 | 0 | — |
| [Repérer les parties d’une adresse Web](fiches/info-lire-adresse-web.html) | Informatique, algorithmique et langages de programmation | 17 | 0 | 0 | — |
| [Comprendre les rôles d’un ordinateur](fiches/info-ordinateur-fonctions.html) | Informatique, algorithmique et langages de programmation | 17 | 0 | 0 | — |
| [Comprendre le rôle d’un système d’exploitation](fiches/info-systeme-exploitation.html) | Informatique, algorithmique et langages de programmation | 16 | 0 | 1 | constat : Au moins une source pointe une page précise, pas seulement un portail (1 portail(s) assumé(s) par écrit : rien à confronter, à trancher par une personne) |
| [Distinguer une table, une requête et une page Web](fiches/info-table-requete-web.html) | Informatique, algorithmique et langages de programmation | 17 | 0 | 0 | — |
| [Un même algorithme, plusieurs langages : Python et JavaScript](fiches/prog-comparer-langages.html) | Informatique, algorithmique et langages de programmation | 17 | 0 | 0 | — |
| [Lire une licence avant de réutiliser un programme](fiches/prog-lire-licence-logiciel.html) | Informatique, algorithmique et langages de programmation | 17 | 0 | 0 | — |
| [Tester un programme avec des cas simples](fiches/prog-tester-exemples.html) | Informatique, algorithmique et langages de programmation | 17 | 0 | 0 | — |
| [Présenter une idée avec une raison et un exemple](fiches/fr-argumenter-avec-exemple.html) | Français, lecture, écriture et communication | 17 | 0 | 0 | — |
| [Comprendre un mot grâce à son contexte](fiches/fr-comprendre-mot-contexte.html) | Français, lecture, écriture et communication | 17 | 0 | 0 | — |
| [Lire la ponctuation pour comprendre une phrase](fiches/fr-lire-ponctuation.html) | Français, lecture, écriture et communication | 17 | 0 | 0 | — |
| [Préparer une explication courte](fiches/fr-preparer-explication-orale.html) | Français, lecture, écriture et communication | 17 | 0 | 0 | — |
| [Repérer l’idée principale et les informations utiles](fiches/fr-reperer-idee-texte.html) | Français, lecture, écriture et communication | 17 | 0 | 0 | — |
| [Demander de l’aide ou une répétition en anglais](fiches/langue-anglais-demander-aide.html) | Langues étrangères et interculturel | 17 | 0 | 0 | — |
| [Demander comment épeler un mot en anglais](fiches/langue-anglais-epeler.html) | Langues étrangères et interculturel | 17 | 0 | 0 | — |
| [Prononcer la fin -ed des verbes anglais](fiches/langue-anglais-prononcer-ed.html) | Langues étrangères et interculturel | 17 | 0 | 0 | — |
| [Lire « th » dans un dictionnaire : /θ/ ou /ð/ ?](fiches/langue-anglais-prononcer-th.html) | Langues étrangères et interculturel | 17 | 0 | 0 | — |
| [Reconnaître un mot que tu connais déjà sur une affiche bilingue](fiches/langue-reperer-mot-deja-connu.html) | Langues étrangères et interculturel | 17 | 0 | 0 | — |
| [Convertir des mesures sans changer leur quantité](fiches/maths-convertir-unites.html) | Mathématiques, mesures et données | 17 | 0 | 0 | — |
| [Résoudre une équation simple en gardant l’égalité](fiches/maths-equation-simple.html) | Mathématiques, mesures et données | 16 | 0 | 1 | constat : Au moins une source pointe une page précise, pas seulement un portail (1 portail(s) assumé(s) par écrit : rien à confronter, à trancher par une personne) |
| [Estimer un résultat pour vérifier un calcul](fiches/maths-estimer-calcul.html) | Mathématiques, mesures et données | 17 | 0 | 0 | — |
| [Lire les graduations d’un graphique](fiches/maths-lire-echelle-graphique.html) | Mathématiques, mesures et données | 16 | 0 | 1 | constat : Au moins une source pointe une page précise, pas seulement un portail (1 portail(s) assumé(s) par écrit : rien à confronter, à trancher par une personne) |
| [Lire une information à l’intersection d’un tableau](fiches/maths-lire-tableau-croise.html) | Mathématiques, mesures et données | 16 | 0 | 1 | constat : Au moins une source pointe une page précise, pas seulement un portail (1 portail(s) assumé(s) par écrit : rien à confronter, à trancher par une personne) |
| [Comprendre une moyenne comme un partage égal](fiches/maths-moyenne.html) | Mathématiques, mesures et données | 17 | 0 | 0 | — |
| [Comprendre une chance dans un tirage simple](fiches/maths-probabilite-tirage.html) | Mathématiques, mesures et données | 17 | 0 | 0 | — |
| [Repérer un angle droit](fiches/maths-reperer-angle-droit.html) | Mathématiques, mesures et données | 17 | 0 | 0 | — |
| [Reformuler une demande avant de commencer](fiches/methodes-demander-clarification.html) | Apprendre à apprendre, autonomie et relations | 17 | 0 | 0 | — |
| [Formuler une recherche sur le Web](fiches/numerique-formuler-recherche.html) | Numérique, données, cybersécurité et intelligence artificielle | 17 | 0 | 0 | — |
| [Nommer et retrouver ses fichiers sans exposer ses données](fiches/numerique-organiser-fichiers.html) | Numérique, données, cybersécurité et intelligence artificielle | 17 | 0 | 0 | — |
| [Repérer une source de santé publique avant d’agir](fiches/sante-reperer-source-publique.html) | Santé, alimentation, corps et sécurité | 17 | 0 | 0 | — |
| [Calculer une vitesse moyenne simple](fiches/sciences-calculer-vitesse-moyenne.html) | Sciences, technologie et environnement | 17 | 0 | 0 | — |
| [Repérer les grandes étapes de vie d’une plante à fleurs](fiches/sciences-cycle-vie-plante.html) | Sciences, technologie et environnement | 17 | 0 | 0 | — |
| [Distinguer fusion et dissolution](fiches/sciences-distinguer-melange-changement-etat.html) | Sciences, technologie et environnement | 17 | 0 | 0 | — |
| [Distinguer météo et climat](fiches/sciences-meteo-climat.html) | Sciences, technologie et environnement | 17 | 0 | 0 | — |
| [Comprendre un circuit électrique ouvert ou fermé](fiches/tech-circuit-ouvert-ferme.html) | Sciences, technologie et environnement | 17 | 0 | 0 | — |
| [Distinguer capteur, commande et action dans un objet électronique](fiches/tech-electronique-capteur.html) | Sciences, technologie et environnement | 17 | 0 | 0 | — |

## 4. Ce qu'aucun script ne peut faire

Ces questions restent entières, même quand tous les contrôles ci-dessus sont verts :

- La source dit-elle réellement ce que la fiche affirme, dans sa version consultée ?
- Les exemples et corrections sont-ils exacts pour la variété, le niveau et le public visés ?
- Les droits permettent-ils ce qui est fait du document (citation, reprise, renvoi) ?
- L'analogie éclaire-t-elle sans stigmatiser ni induire en erreur ?
- Une personne réelle peut-elle s'en servir — au clavier, au lecteur d'écran, à fort zoom, sans audio ?
- L'association autorise-t-elle la publication, et sous quelle responsabilité éditoriale ?

Quand un constat « page précise » figure ci-dessus, la première de ces questions ne peut pas être tranchée : il n'y a pas de page à confronter. Le portail peut rester, mais alors la fiche l'assume par écrit, et cette limite se dit dans la page publique.

## 5. Comment s'en servir

1. Corriger d'abord les échecs mécaniques : ils sont objectifs et souvent automatiques à réparer.
2. Trancher les constats : soit ajouter une page précise réellement consultée, soit assumer le portail par écrit dans la fiche. Un constat ne bloque pas, mais il ne s'efface pas tout seul.
3. Une fois une fiche sans échec, ouvrir son paquet de relecture (`python3 outils/construire-paquets-relecture.py --fiche <identifiant>`) : il ne reste que les questions du §4.
4. Consigner la relecture humaine dans `relectures.toml` (`--modele`), puis lancer `python3 outils/registre-relecture.py`.

Régénérer avec `python3 outils/auditer-prototypes.py` ; vérifier avec `--verifier`.
