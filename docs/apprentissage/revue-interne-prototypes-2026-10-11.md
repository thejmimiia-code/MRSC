# Revue interne de cohérence des prototypes — 11 octobre 2026

## Portée et décision

Cette note consigne une **relecture interne de cohérence menée par l’agent** sur les 26 fiches du catalogue qui portaient le statut `Prototype à relire` avant le lot ajouté ensuite. Elle porte sur la logique du texte, les exemples et corrections, les limites annoncées, les calculs simples et, lorsqu’il y en a, les extraits de programme. Ce n’est pas une validation indépendante par une personne experte ni une approbation de publication. Les huit fiches ajoutées après cette relecture (`fr-comprendre-mot-contexte`, `maths-lire-echelle-graphique`, `sciences-calculer-vitesse-moyenne`, `sciences-distinguer-melange-changement-etat`, `geo-decrire-paysage`, `info-lire-adresse-web`, `arts-lire-cartel`, `recherche-question-hypothese`) n’en font pas partie.

Deux précisions ont été apportées pendant cette lecture : le scénario de `fr-argumenter-avec-exemple` indique maintenant une activité de 75 minutes et une salle qui ferme à 16 h, de sorte que la raison proposée pour 14 h est vérifiable ; `maths-probabilite-tirage` précise dans son énoncé que l’équiprobabilité est une hypothèse, et pas une conséquence du seul mélange des jetons.

Les extraits Python et JavaScript de `prog-comparer-langages` ont été exécutés séparément le 11 octobre 2026 : les deux commandes ont terminé avec le code 0 et produit les trois mêmes lignes attendues. Le pseudo-code de `prog-tester-exemples` reste une simulation papier et n’est pas exécuté.

**Décision commune : les 26 fiches restent des prototypes non validés.** Aucune n’est déclarée prête à la diffusion sur la seule base de cette relecture. Avant une validation finale, il reste à faire une revue indépendante adaptée à chaque domaine, à vérifier directement les sources et les droits, puis à conduire les essais d’accessibilité et d’usage indiqués dans la grille de relecture. Les vérifications automatiques du site ne remplacent pas ces étapes.

## Notes de lecture par fiche

| Fiche | Contrôle interne effectué et résultat de cohérence | Validation encore nécessaire |
| --- | --- | --- |
| `recherche-lire-etude` | Le scénario distingue déclarations et résultats et ne conclut pas à une causalité lorsque les personnes choisissent leur groupe. | Relecture en méthodes de recherche, portée des sources, droits et essais d’usage. |
| `maths-convertir-unites` | Recalculs : 1 m 35 cm = 135 cm ; 2 L − 650 mL = 1 350 mL. Les unités restent visibles. | Relecture mathématique et pédagogique indépendante ; sources et accessibilité. |
| `maths-moyenne` | Recalculs : 20 ÷ 4 = 5 et (3 + 6 + 9) ÷ 3 = 6. La moyenne est distinguée d’une valeur nécessairement observée. | Relecture mathématique indépendante et essais apprenants. |
| `maths-estimer-calcul` | Recalculs : 26 + 41 = 67 ; l’arrondi à la dizaine donne environ 70. Estimation et résultat exact sont séparés. | Vérifier la formulation avec des personnes apprenantes et une personne compétente en mathématiques. |
| `info-ordinateur-fonctions` | Le parcours clavier → logiciel/processeur → écran et enregistrement distingue entrée, traitement, sortie, mémoire vive et stockage. | Relecture informatique et vérification des sources et droits. |
| `prog-comparer-langages` | Python et JavaScript ont été exécutés séparément ; sorties identiques : trois étapes, dans le même ordre. La page explique que les extraits ne s’exécutent pas dans le navigateur. | Relecture de programmation et essais d’accessibilité du rendu du code. |
| `tech-circuit-ouvert-ferme` | L’explication reste un modèle de circuit simple et n’incite pas à manipuler un équipement réel. | Relecture spécialisée en électricité et vérification des consignes de sécurité. |
| `tech-electronique-capteur` | Le scénario distingue entrée mesurée, règle de commande et sortie ; les limites de mesure et de panne sont mentionnées. | Relecture spécialisée en électronique et essais d’usage. |
| `civ-choisir-source-publique` | La fiche différencie démarche, texte juridique, donnée et explication, sans promettre qu’une page officielle suffit à chaque cas. | Vérifier la portée actuelle de chaque portail et faire relire les exemples civiques. |
| `econ-lire-facture` | Recalcul : 28 € + 12 € = 40 €. Date d’établissement et échéance sont distinguées ; aucun statut de paiement n’est inventé. | Relecture en information du consommateur ; aucune validation juridique ou conseil personnalisé. |
| `econ-comparer-prix-unitaires` | Recalculs : 1,50 € / 250 g = 6,00 €/kg ; 2,80 € / 500 g = 5,60 €/kg ; exercice : 6,00 €/kg contre 5,50 €/kg, avec 3,00 € contre 5,50 € à payer par paquet. | Relecture mathématique et en information du consommateur ; pas de recommandation d’achat. |
| `fr-reperer-idee-texte` | Les réponses distinguent idée principale, détails explicites et ce qui n’est pas obligatoire dans l’exemple. | Relecture en français et compréhension avec des adultes apprenant la lecture. |
| `langue-anglais-demander-aide` | Les expressions correspondent aux demandes visées ; le texte signale qu’il ne fournit pas d’audio et ne garantit pas la compréhension. | Relecture linguistique indépendante, notamment registre et naturel des traductions. |
| `geo-points-cardinaux` | Pour un plan dont le nord pointe vers le haut, est à droite et sud en bas ; la correction ne prétend pas donner d’itinéraire. | Relecture en géographie et tests d’accessibilité d’un plan décrit verbalement. |
| `histoire-lire-frise` | Recalcul de l’intervalle : du 3 au 10 juin, 7 jours. La fiche sépare date, durée et causalité. | Relecture en histoire et vérification pédagogique des calendriers et échelles. |
| `maths-probabilite-tirage` | Recalculs : 1 résultat favorable sur 4 = 1/4 ; 2 sur 4 = 1/2. L’équiprobabilité est désormais énoncée comme hypothèse. | Relecture mathématique indépendante et essais de compréhension de l’hypothèse. |
| `numerique-organiser-fichiers` | La distinction nom/extension/format est cohérente ; renommer une extension n’est pas présenté comme une conversion. Aucun fichier réel n’est demandé. | Relecture numérique, vérification des conseils selon les outils et essais d’accessibilité. |
| `methodes-demander-clarification` | La reformulation vérifie action, échéance et limite ; l’absence de réponse n’est pas traitée comme un accord. | Tester plusieurs modes de communication et contextes avec des personnes concernées. |
| `fr-preparer-explication-orale` | La progression sujet → repères → vérification est cohérente ; une réponse écrite ou assistée est explicitement possible. | Relecture en communication et tests de compréhension avec des personnes ayant des modes de communication variés. |
| `fr-argumenter-avec-exemple` | Le scénario corrigé rend la raison vérifiable : 75 minutes depuis 14 h finissent à 15 h 15, avant la fermeture à 16 h. Proposition, raison, exemple fictif et nuance sont séparés. | Relecture en français/argumentation et contrôle des formulations avec différents publics. |
| `maths-equation-simple` | Recalcul : x + 6 = 17 donne x = 11 ; 11 + 6 = 17. La même soustraction est appliquée aux deux membres. | Relecture mathématique indépendante et vérification de l’analogie de balance. |
| `sciences-meteo-climat` | L’échelle d’un bulletin ponctuel est distinguée de celle d’observations sur une longue période ; aucun jour isolé ne sert à établir une tendance. | Relecture par une personne compétente en climatologie et vérification directe des références. |
| `histoire-comparer-sources` | Les documents fictifs décrivent une annonce et une arrivée observée ; la conclusion n’invente pas l’heure réelle du début. | Relecture en histoire et éducation aux médias, avec attention au traitement des témoignages. |
| `info-bits-octets` | Recalculs : 2³ = 8 motifs et 2⁸ = 256 ; le texte ne confond pas un motif binaire avec une lettre. | Relecture informatique sur les unités, encodages et conventions. |
| `prog-tester-exemples` | Le cas limite zéro expose l’écart entre « supérieur ou égal à zéro » et « strictement supérieur à zéro » ; les trois tests sont à rejouer après correction. | Relecture en programmation ; tests plus larges pour tout logiciel réel. |
| `arts-composer-formes` | L’exercice admet plusieurs formes de réponse et ne présente pas une composition comme universellement correcte. | Relecture en pratique artistique et tests d’accès pour différentes capacités visuelles. |

## Limites de la revue

- Les liens externes n’ont pas été visités ou vérifiés un à un pendant cette revue ; le générateur contrôle leur forme HTTPS, pas leur disponibilité ni l’exactitude de leur contenu.
- La présence d’une mention de licence dans le catalogue ne confirme pas que la licence a été vérifiée auprès de l’ayant droit. Aucun droit de réutilisation n’est certifié par cette note.
- Les validations spécialisées et indépendantes ne peuvent pas être remplacées par une auto-relecture de l’agent.
- Les validations visuelles, clavier/lecteur d’écran et essais avec des personnes apprenantes n’ont pas été réalisés dans cette revue.
- Les résultats `py_compile`, `--verifier` et du vérificateur statique établissent uniquement les contrôles techniques listés ; ils ne constituent pas une approbation pédagogique ou scientifique.
