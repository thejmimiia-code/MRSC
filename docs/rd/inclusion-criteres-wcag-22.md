# Initiative R&D — les critères WCAG 2.2 avant le RGAA 5

- Date d'ouverture : `2026-10-23`
- État : `en-cours`
- Phase : `prototype`
- Rôles à mobiliser : `agent / accessibilité` — **aucun audit humain n'a eu lieu**
- Domaine(s) et contexte(s) : `langue-communication`, `methodes-communication`, toutes les pages publiques
- Source de vérité / initiative liée : [`prospective-2027-2030.md`](prospective-2027-2030.md) § 5, décision 10 ; [`portefeuille.toml`](portefeuille.toml) `optimisation-du-site` et `ecouter-la-page`
- Prochaine revue souhaitée : à la publication du RGAA 5, annoncée pour la fin 2026 — pas de date promise

## Signal et question

Le référentiel français en vigueur en 2026 est le RGAA 4.1.2, aligné sur WCAG 2.1 AA. Une version 5 est annoncée pour la fin 2026 et intégrera **WCAG 2.2**, dont deux critères de niveau AA qui n'existaient pas dans la version précédente : la taille des cibles (`2.5.8`) et le focus non masqué (`2.4.11`). Le site a été travaillé jusqu'ici sur WCAG 2.1 : rien ne dit qu'il tienne ces deux-là.

**Question posée :** que produit une mesure honnête de ces deux critères sur les 98 pages du site, et que faut-il corriger avant que la norme ne change — sans transformer un chiffre en promesse de conformité ?

## État existant et limites

- **Déjà disponible :** planchers de cible à 24 px sur cinq familles de commandes (`outils/verifier-affichages.py`, `CIBLES`), plancher de 32 px sur les commandes d'en-tête, focus visible vérifié sur neuf pages, `scroll-padding-top` pour les ancres.
- **Ce qui manquait :** aucune mesure de **toutes** les cibles d'une page, aucune mesure du recouvrement du focus par les bandeaux collants, et un contrôle statique qui ne voyait que les sélecteurs nommés à la main.
- **Incertitudes :** ces deux critères ne disent rien de la compréhension, de la fatigue, ni de l'usage réel d'un doigt ou d'un lecteur d'écran ; ils se mesurent sur une géométrie, pas sur une expérience.

## Sources externes consultées le 23 octobre 2026

| Affirmation | Source directe | Ce que la source permet d'affirmer | Limites |
| --- | --- | --- | --- |
| Le RGAA 5, aligné sur WCAG 2.2, est annoncé pour la fin 2026 ; les travaux sur 4.1.2 restent valables. | DINUM, *Nouvelle version du RGAA*, 4 mars 2026 — <https://www.numerique.gouv.fr/actualites/nouvelle-version-rgaa-2026/> | Le calendrier justifie d'anticiper les critères 2.2, pas de publier une conformité. | Date annoncée, non garantie ; le contenu définitif du RGAA 5 n'est pas connu. |
| Un espace déclaré « totalement conforme » a été mis en demeure en juin 2026 alors qu'un audit mesurait 42,11 %. | Arcom, décision n° 2026-358 du 24 juin 2026 — <https://www.legifrance.gouv.fr/jorf/id/JORFTEXT000054393304> | Une déclaration ne remplace pas une mesure : aucun taux ne sera publié ici. | Cas d'un autre service ; il illustre un risque documentaire. |
| `2.5.8` (AA) exige 24 × 24 px CSS, avec exceptions « en ligne », « espacement », « taille équivalente » et « essentiel ». | W3C, *Understanding SC 2.5.8: Target Size (Minimum)* — <https://www.w3.org/WAI/WCAG22/Understanding/target-size-minimum.html> | Un lien de 19 px dans un paragraphe n'est pas une faute ; un lien de 19 px seul sur sa ligne peut l'être. | La notion de « cible » inclut les zones cliquables invisibles ; la mesure géométrique ne les voit pas toutes. |
| `2.4.11` (AA) exige que l'élément focalisé ne soit pas **entièrement** masqué. | W3C, *Understanding SC 2.4.11: Focus Not Obscured (Minimum)* — <https://www.w3.org/WAI/WCAG22/Understanding/focus-not-obscured-minimum.html> | Un recouvrement partiel toléré ; un recouvrement total ne l'est pas. | Le critère porte sur l'indicateur de focus, pas seulement sur l'élément ; la mesure approche par cinq points. |

## Options de conception

| Option | Valeur attendue | Coût | Pourquoi retenue ou écartée |
| --- | --- | --- | --- |
| **A. Mesurer tout le site, puis corriger ce qui est réel** (retenue) | Un chiffre par critère, et une liste courte de défauts réels. | Un script hors CI, quelques secondes par page. | C'est la seule option qui distingue une exception prévue d'un vrai défaut. |
| B. Étendre le contrôle statique à tous les sélecteurs de lien | Aucune mesure de rendu, aucun navigateur. | Faible. | **Écartée seule** : une règle CSS ne dit pas si la cible mesure 24 px à l'écran, et le contrôle actuel ne voyait pas le pied de page. |
| C. Passer un audit RGAA/WCAG complet | Un taux de conformité. | Expertise externe, jours de travail. | **Hors de portée ici** : le dépôt ne peut pas s'auto-auditer, et aucun taux ne sera publié sans audit réel. |
| D. Ne rien faire avant le RGAA 5 | Aucun travail. | Nul. | **Écartée** : la mesure coûtait une heure et a trouvé un vrai défaut. |

## Prototype retenu

- **Outil :** `outils/auditer-criteres-22.mjs`, hors CI parce qu'il demande Chromium (même famille que `auditer-affichages.mjs`). Il rend trois états : conforme, exception prévue par le critère, à corriger.
- **Taille des cibles :** relève toutes les cibles interactives, écarte celles qui sont dans une phrase (exception « en ligne ») et celles qui sont assez espacées (cercle de 24 px sans recoupement), puis liste le reste.
- **Focus non masqué :** porte le focus sur chaque cible (60 par page dans l'échantillon), fait défiler en `instant`, puis teste cinq points du rectangle contre `elementFromPoint`.
- **Correction apportée :** les liens légaux du pied de page passaient de 19 px à **24 px** de haut (`min-height` + `inline-flex`), l'écart vertical du bloc reprenant la hauteur gagnée pour que le pied de page ne grandisse pas.

## Vérifications et résultat

| Contrôle | Méthode, date | Résultat | À corriger |
| --- | --- | --- | --- |
| Taille des cibles, site entier | `node outils/auditer-criteres-22.mjs`, 98 pages × 390 et 1 280 px, 24 oct. 2026 | **5 654 conformes, 900 en ligne (exception), 2 304 espacées (exception), 0 à corriger.** | — |
| Avant correction | même script sur 10 pages | **12 défauts réels**, tous dans le pied de page à 390 px : « Contact » 49 × 19, « Haut de page » 86 × 19, « Licence » 48 × 19. | Corrigés. |
| Focus non masqué | `--pages` sur huit pages × deux largeurs, 60 cibles par page, 24 oct. 2026 | **825 éléments testés, 0 entièrement masqué.** | — |
| Pied de page après correction | Chromium, 390 et 1 440 px, 100 % et 130 % | Liens à 24 px (25 px à 130 %) ; écart de centrage **0 px** sur chaque ligne ; débordement 0 ; pied de page **430 px** à 1 440 px (425 avant). | — |
| Garde-fou statique | `python3 outils/verifier-affichages.py` | `.footer-legal a` entre dans `CIBLES` : `min-height` retiré ⇒ **contrôle en échec**. | — |
| Lecture à voix haute, contenu replié | `node outils/test-experience.cjs` | La liste de couverture d'`apprendre.html` n'est **pas** lue quand elle est fermée (449 segments, 0 « Fiche(s) ») et l'est quand elle est ouverte (564 segments, 82). | — |

**Défaut trouvé dans le lot précédent.** En mesurant les cibles, le script a buté sur un contenu de `<details>` refermé qui gardait une boîte non nulle : 50 fausses alertes sur `apprendre.html`. Le même piège menaçait la lecture à voix haute livrée le 23 octobre : son filtre s'appuyait sur `getClientRects`, insuffisant pour un `<details>` fermé. La mesure des quatre cas a été refaite :

| Cas | `innerText` | `getClientRects` | `checkVisibility` |
| --- | --- | --- | --- |
| `display: none` | texte présent | **vide** | faux |
| `visibility: hidden` | **vide** | non vide | faux |
| `<details>` refermé | **vide** | non vide | faux |
| `aria-hidden="true"` | texte présent | non vide | **vrai** |

Aucune de ces trois mesures ne suffit seule. Le filtre de la lecture à voix haute vérifie donc maintenant `checkVisibility({ checkVisibilityCSS: true, contentVisibilityAuto: true })`, garde `getClientRects` et `innerText` en secours, et écarte `aria-hidden` séparément.

## Décision et entretien

- **Décision :** `continuer` — mesure publiée, correction livrée, aucune conformité revendiquée.
- **Fichiers touchés :** `outils/auditer-criteres-22.mjs` (nouveau), `assets/css/site.css` (`.footer-legal`), `assets/js/site.js` (`estAffiche`), `outils/verifier-affichages.py` (`CIBLES`, contrôle de lecture), `outils/test-experience.cjs` (essai « contenu replié »), `docs/rd/formats-affichage.md`, `docs/rd/journal.md`, `docs/rd/avancees.toml`, `transparence.html`.
- **Commandes :** `node outils/auditer-criteres-22.mjs` · `python3 outils/verifier-affichages.py` · `node outils/test-experience.cjs`.
- **Prochaine action :** rejouer la mesure à la publication du RGAA 5, puis faire relire les deux critères par un rôle accessibilité ; étendre l'échantillon de focus aux 84 fiches si le coût reste supportable.
- **Indicateur de maintenance :** si un sélecteur de cible change (`.footer-legal a`, `.nav-links a`, `.statute-link`, `.home-action-link`, `.identity-contact`), le contrôle statique échoue ; si un bandeau collant est ajouté, la mesure de focus doit être rejouée.
- **Données personnelles :** `aucune`.

## Ce que ce lot ne prouve pas

1. **Aucune conformité.** Ni WCAG 2.2, ni RGAA 4.1.2 ou 5. Deux critères mesurés ne font pas un audit de 106.
2. **Une géométrie n'est pas un usage.** Une cible de 24 px reste petite pour une main tremblante ; l'exception d'espacement dispense d'agrandir des liens qui restent difficiles à viser.
3. **La mesure du focus est un échantillon.** 60 cibles par page sur huit pages, pas les 414 d'`apprendre.html` ni les 438 des Escales.
4. **Aucune personne n'a relu ces deux critères**, et l'outil lui-même n'est pas audité.
