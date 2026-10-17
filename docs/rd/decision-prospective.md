# Brief de décision — Boussole des savoirs et pilote d'apprentissage

**Date : 17 octobre 2026. Statut : à décider par l'association. Rédigé par un agent, sans mandat pour trancher.** Ce brief ne remplace ni une délibération, ni une revue de contenu, ni un essai avec des personnes. Il rassemble ce qui est établi, ce qui manque et trois options bornées, pour que la décision soit prise sur des faits vérifiables plutôt que sur une impression.

## 1. Décision à prendre

**Faut-il consacrer du temps à un pilote de la « Boussole des savoirs » en 2027, ou concentrer les moyens sur la relecture des fiches existantes et laisser le prototype en l'état ?**

La décision porte sur l'allocation du temps de relecture, pas sur l'ajout d'une fonctionnalité. Le prototype existe déjà ; il n'est pas nécessaire de construire pour décider.

## 2. Ce qui est établi

| Fait vérifiable | Valeur au 17 octobre 2026 | Où le vérifier |
| --- | --- | --- |
| Fiches d'apprentissage publiées | 81 dans 15 domaines | `docs/apprentissage/catalogue.toml` |
| Fiches explicitement « prototypes à relire » | **55** | Statuts du catalogue |
| Fiches dont la date de revue est échue | **0** | `python3 outils/construire-apprentissages.py --verifier` |
| Prochaine revue du portefeuille R&D | **2026-11-12** | `docs/rd/portefeuille.toml` |
| Initiatives R&D suivies | 14, dont 4 en priorité P0 | Portefeuille |
| Boussole publiée | 10 questions statiques, liens édités à la main, aucune collecte | `apprendre.html#boussole-savoirs` |
| Poids estimé de la page Apprendre | 159 Kio mobile / 309 Kio grand écran (gzip estimé) | `docs/rd/poids-pages.md` |
| En-têtes servis par GitHub Pages | types AVIF/WebP corrects, gzip sur le texte, cache 600 s | Issue #90 |
| Essais navigateur | 8/8, dont 320 px, zoom 150 %, contraste renforcé | `outils/test-experience.cjs` |

Reproduire l'essentiel : `python3 outils/etat-rd.py`.

## 3. Ce qui n'est pas établi

- **Aucun essai avec des personnes** n'a eu lieu. Personne n'a été observé utilisant la Boussole.
- **Aucune relecture experte** des dix questions, de leur ordre ou des fiches reliées.
- **Aucun bénéfice mesuré** : on ne sait pas si la Boussole aide à trouver une deuxième fiche pertinente.
- **Aucune validation juridique** des mentions d'IA ni de la situation du site au regard de l'article 50 du règlement européen.
- **Aucune donnée d'audience** : le site ne collecte pas de mesure d'usage, et ce n'est pas prévu.

## 4. Trois options

| | Option A — Ne rien construire de plus | Option B — Relire, puis pilote papier | Option C — Pilote en ligne |
| --- | --- | --- | --- |
| **Contenu** | Garder la Boussole telle quelle, sans la promouvoir. Consacrer le temps disponible à la relecture des 55 prototypes. | Faire relire les 10 questions et 3 fiches reliées, puis tester la Boussole sur papier avec 5 personnes volontaires, sans compte ni collecte. | Ouvrir un parcours mesuré (temps, clics, chemins), avec consentement, journal minimal et suppression planifiée. |
| **Coût** | Nul en développement ; concentré sur la relecture. | Faible : une relecture éditoriale, une impression, une séance. | Moyen : instrumentation, notice de confidentialité, analyse, correctifs. |
| **Risque principal** | Laisser une fonction visible que personne n'a validée. | Confondre une séance de 5 personnes avec une preuve d'utilité. | Collecter des données personnelles pour un bénéfice non démontré. |
| **Preuve apportée** | Aucune nouvelle ; le corpus reste le seul actif. | Des obstacles concrets, des formulations incomprises, des questions de méthode. | Des comportements agrégés, mais pas nécessairement une amélioration de la compréhension. |
| **Réversible ?** | Oui, sans action. | Oui : rien n'est publié. | Difficilement : une fois collectées, les données existent. |
| **Ce que l'option n'apporte pas** | Une réponse à « la Boussole aide-t-elle ? ». | Une mesure représentative ni une validation experte. | Une preuve d'apprentissage, ni une validation du contenu. |

## 5. Recommandation de travail

**Option B, sous conditions, ou Option A si les relecteurs ne sont pas disponibles.**

Raisonnement : le besoin le plus documenté n'est pas « ajouter un parcours », c'est **relire et rendre vérifiable ce qui existe déjà**. Un pilote papier coûte peu, ne collecte aucune donnée et peut infirmer l'hypothèse. L'option C ne se justifie pas avant que B ait montré un obstacle réel et qu'une notice de confidentialité ait été relue.

Conditions minimales avant toute séance :

1. Les 10 questions et les fiches reliées sont relues par une personne compétente ; les erreurs factuelles sont corrigées avant le test.
2. Le protocole d'essai (`docs/rd/protocole-essais-usage.md`) est relu pour l'accessibilité, l'éditorial et la confidentialité.
3. Les personnes sont volontaires, majeures ou accompagnées, informées du caractère non certifié du contenu, et peuvent arrêter à tout moment.
4. Aucune réponse d'exercice, aucun diagnostic, aucune donnée de santé ou de situation personnelle n'est noté.
5. Les notes sont anonymes, conservées le temps de l'analyse, puis supprimées ; une date de suppression est fixée avant la séance.

## 6. Critères d'arrêt et de décision

- **Arrêt immédiat** si une fiche contient une erreur susceptible de causer un préjudice, ou si les droits d'une source ne sont pas établis.
- **Retour à l'option A** si aucun relecteur n'est disponible avant le **31 janvier 2027** : la Boussole reste un prototype signalé, sans promotion.
- **Révision de la Boussole** si, sur 5 personnes, plus de 2 ne trouvent pas la fiche visée sans aide : le problème est la formulation ou l'ordre, pas l'utilisateur.
- **Pas de passage à l'option C** sans une preuve écrite que le pilote papier a révélé un besoin que seul un test en ligne peut trancher.
- **Aucune promotion publique** du prototype tant que la relecture n'est pas consignée.

## 7. Ce qui ferait changer la recommandation

- Une augmentation nette et vérifiée de la demande d'**évaluation de source** auprès d'un outil d'IA (33 % des utilisateurs de chatbots dans le Digital News Report 2026) rendrait la Boussole plus pertinente — mais ne prouverait pas son efficacité.
- Un retrait supplémentaire du canal humain dans les services publics renforcerait l'intérêt d'un parcours **imprimable et autonome**, pas nécessairement d'un parcours en ligne.
- Une obligation juridique nouvelle sur l'étiquetage des contenus générés pourrait déplacer l'effort vers la traçabilité des pages existantes.

## 8. Questions à trancher par l'association

1. Qui peut relire les 10 questions et les 3 fiches reliées, et à quelle date ?
2. Le pilote papier est-il acceptable, ou faut-il attendre une relecture experte complète ?
3. Combien de temps de relecture l'association peut-elle réellement consacrer d'ici janvier 2027 ?
4. La Boussole doit-elle rester visible sur `apprendre.html` en attendant la décision ?
5. Qui décide, et comment la décision sera-t-elle consignée dans le journal ?

## 9. Trace de décision

| Champ | À remplir par l'association |
| --- | --- |
| Option retenue | |
| Date | |
| Personne ou instance qui décide | |
| Conditions ajoutées | |
| Date de réexamen | |

**Tant que ce tableau est vide, la décision n'est pas prise et le prototype reste un prototype à relire.**
