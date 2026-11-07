# Relecture par agent des apparences du 7 novembre 2026

**Date : 2026-11-07. Auteur : agent. Statut : relu par agent, sources confrontées.**
Ce document n'est ni une validation humaine, ni une expertise, ni un avis juridique,
ni un essai avec des personnes. Il est la trace d'une étape de vérification
exécutable : `outils/verifier-relecture-contenus.py`, câblée dans la CI et
éprouvée par `outils/test_mutations_relecture_contenus.py`.

## 1. Pourquoi cette étape existe

Le 7 novembre 2026, après la mise en ligne des six apparences, la consigne a été
explicite : la relecture est à faire par une **nouvelle étape de vérification**,
avec vérifications des sources sûres, parce que la personne ne va pas « se cogner
la lecture de millier de lignes ». Elle peut en revanche « voir un rendu à l'œil
pour valider un placement, un style, une construction ».

La frontière est donc celle-ci, et elle est gardée par le contrôle :

| Qui | Quoi | Ce que ça ne fait pas |
| --- | --- | --- |
| Agent | Relit les libellés, les descriptions, la note, les affirmations de méthode ; confronte chaque fait à une source primaire datée ; corrige ou retire ce qui n'est pas étayé ; consigne les limites. | Ne valide pas le rendu, ne fabrique pas d'expertise, n'écrit pas dans le registre humain. |
| Personne | Valide à l'œil un placement, un style, une construction. | N'a pas à lire des milliers de lignes ni à valider le contenu texte ligne par ligne. |

Le registre `docs/apprentissage/relectures.toml` reste le **seul** endroit des
relectures humaines. Il contient zéro entrée après cette étape et l'agent n'y a
rien écrit. `outils/registre-relecture.py` continue de rappeler qu'il « ne relit
rien, ne note rien, ne valide rien » : la nouvelle étape ne s'y substitue pas.
`outils/confronter-sources.py` reste un prototype d'exploration hors porte de
publication ; il n'a pas été promu en validation automatique.

## 2. Périmètre exact

Le lot des six apparences de « Personnalisation », déjà publié (PR n° 283,
`92aeac5`) : les **20 chaînes visibles** extraites du bloc « Apparences » de
`assets/js/site.js` (six noms, six descriptions, note, titres, légende, libellés
accessibles, statut vocal, bouton de retour, infobulle) et **cinq affirmations de
méthode** (ordre des réglages, seuils de contraste, formule de luminance, noms
protégés, absence d'animation).

Hors périmètre, et donc **non relus** ici : les 107 fiches d'apprentissage, les
81 prototypes, le texte de fond de `transparence.html`, la prospective S1/S2/S3,
la décision de charte de l'association et la citation signée. Aucun statut de
fiche n'a été modifié. Les six thèmes n'ont subi aucun changement de texte
public : la relecture les a confirmés.

## 3. Sources primaires consultées le 7 novembre 2026

Huit pages d'éditeurs primaires, lues à la date indiquée. Les URL sont celles
des pages effectivement ouvertes ; l'ancre est un repère bref observé dans la
page, pas un extrait recopié. Aucun moteur de recherche, aucun blog, aucun
agrégateur et aucune page de forum ne figure dans le registre.


| Id | Éditeur | Page et URL | Ancre observée | Ce que la source permet | Limites |
| --- | --- | --- | --- | --- | --- |
| `mdn-color-scheme` | MDN Web Docs (Mozilla) | color-scheme CSS property — https://developer.mozilla.org/en-US/docs/Web/CSS/Reference/Properties/color-scheme | `"light" and "dark"` | Confirmer que light et dark sont les deux schémas de couleur courants des systèmes, que color-scheme les déclare et qu'une balise meta placée avant le CSS aide à éviter un éclair de thème au chargement. | Page de référence maintenue par Mozilla, documentation et non texte normatif ; elle décrit les schémas du système d'exploitation, pas la fréquence des réglages proposés par les sites Web. Elle ne fournit aucune statistique d'usage et ne valide aucun choix éditorial du M.R.S.C. |
| `mdn-prefers-color-scheme` | MDN Web Docs (Mozilla) | prefers-color-scheme CSS media feature — https://developer.mozilla.org/en-US/docs/Web/CSS/Reference/At-rules/@media/prefers-color-scheme | `light or dark color themes` | Confirmer que la préférence clair/sombre est exprimée par un réglage du système ou du navigateur, et que la valeur light couvre aussi l'absence de préférence active. | Documentation de référence, non spécification normative ; le comportement exact dépend du navigateur et du système. Elle n'atteste pas que le script du site suit effectivement cette préférence : cette vérification-là est une mesure interne. |
| `mdn-forced-colors` | MDN Web Docs (Mozilla) | forced-colors CSS media feature — https://developer.mozilla.org/en-US/docs/Web/CSS/Reference/At-rules/@media/forced-colors | `forced to 'none'` | Confirmer qu'en mode couleurs forcées le navigateur remplace les couleurs auteur et force background-image à none pour les valeurs non-URL, et que la fonction sert à de petits ajustements, pas à un second design. | Le comportement varie selon le navigateur et la plateforme ; MDN recommande de ne pas créer un design séparé. La règle du dépôt qui neutralise les décors reste donc un ajustement prudent, pas une garantie de conformité. |
| `mdn-prefers-reduced-motion` | MDN Web Docs (Mozilla) | prefers-reduced-motion CSS media feature — https://developer.mozilla.org/en-US/docs/Web/CSS/Reference/At-rules/@media/prefers-reduced-motion | `non-essential motion` | Confirmer que reduce demande à réduire ou remplacer les animations non essentielles, et qu'aucune animation ajoutée est la réponse la plus sûre. | La page documente la préférence, pas son application dans ce dépôt ; l'absence d'animation dans les décors est vérifiée séparément par une porte locale. Elle ne dit rien des transitions déjà présentes sur le site. |
| `mdn-theme-color` | MDN Web Docs (Mozilla) | meta name=theme-color — https://developer.mozilla.org/en-US/docs/Web/HTML/Reference/Elements/meta/name/theme-color | `a suggested color` | Confirmer que theme-color est une couleur suggérée à l'agent utilisateur pour l'interface autour de la page, définie par l'attribut content. | MDN classe cette fonctionnalité en disponibilité limitée : Firefox bureau et plusieurs navigateurs ne la prennent pas en charge. La mise à jour de la balise par le script est donc une suggestion, jamais un rendu garanti. |
| `w3c-contrast-minimum` | W3C / Web Accessibility Initiative | Understanding SC 1.4.3 Contrast (Minimum), WCAG 2.2 — https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum.html | `at least 4.5:1` | Confirmer le seuil de 4,5:1 pour le texte normal, 3:1 pour le grand texte, l'absence d'arrondi des seuils (4,499:1 échoue) et l'usage des couleurs déclarées plutôt que du rendu à l'écran. | Document d'accompagnement (Understanding), non texte normatif ; il ne couvre pas les états de survol, de focus, les dégradés ni les combinaisons particulières du site. Le contrôle local mesure des paires de jetons déclarées. |
| `w3c-non-text-contrast` | W3C / Web Accessibility Initiative | Understanding SC 1.4.11 Non-text Contrast, WCAG 2.2 — https://www.w3.org/WAI/WCAG22/Understanding/non-text-contrast.html | `at least 3:1` | Confirmer le seuil de 3:1 pour les composants d'interface et les objets graphiques porteurs d'information, là aussi sans arrondi. | Le document précise que le seuil porte sur les couleurs adjacentes et que certains éléments (composants inactifs, décoration) en sont exclus ; appliquer 3:1 à une paire de jetons ne prouve pas la conformité de tous les états d'interface. |
| `w3c-luminance` | W3C / groupe de travail WCAG (dépôt w3c/wcag) | Définition de relative luminance, WCAG 2.2 — https://github.com/w3c/wcag/blob/main/guidelines/terms/20/relative-luminance.html | `0.04045` | Confirmer la formule L = 0,2126 R + 0,7152 G + 0,0722 B et le seuil de linéarisation 0,04045, qui remplace 0,03928 depuis mai 2021. | Fichier source du glossaire WCAG lu le 7 novembre 2026 ; la note du W3C précise que le changement de seuil n'a pas d'effet pratique sur les calculs dans le contexte de ces règles. La correction faite ici aligne la porte sur la définition actuelle, elle ne change aucun résultat mesuré. |

Le registre machine correspondant est `docs/rd/relecture-contenus.toml`. La porte
vérifie la **discipline** de cette relecture (éditeur primaire, https, domaine
autorisé, date, ancre courte, portée et limites explicites) : elle ne relit pas
le Web et ne juge pas la vérité des pages. La lecture, elle, est consignée ici,
datée, avec ses limites. C'est la distinction entre un fait-source et une
validation : cette étape produit des **faits sourcés et des propositions d'agent**,
pas une décision de l'association.

## 4. Résultat des 25 affirmations

| Nature | Nombre | Rattachement exigé |
| --- | --- | --- |
| `fait-source` | 5 | Au moins une source primaire du registre. |
| `mesure-interne` | 5 | Au moins un fichier du dépôt réellement vérifié. |
| `proposition` | 15 | Aucune source externe, et la limite dit « aucun fait externe ». |

Verdicts : **22 concordant**, **3 corrige**, 0 retiré, 0 sans-objet. Aucune
chaîne publique du lot n'est sortie sans entrée, et chaque entrée de chaîne
publique a été recherchée littéralement dans le fichier cité : si un libellé
change sans que le registre soit relu, la CI échoue.

Les faits retenus après confrontation :

- Le réglage « Suivre l'appareil » repose bien sur une préférence exprimée par le
  système ou le navigateur (`prefers-color-scheme` ; `light` couvre aussi
  l'absence de préférence active). L'application effective côté site a été
  mesurée en navigateur le 7 novembre, pas déduite de la documentation.
- Les seuils 4,5:1 (texte) et 3:1 (repères d'interface) sont ceux du W3C/WAI
  pour WCAG 2.2, et ils **ne s'arrondissent pas** : 4,499:1 échoue.
- La formule de luminance relative de WCAG 2.2 utilise désormais **0,04045**.
- `forced-colors` force déjà `background-image` à `none` pour les dégradés, et
  `prefers-reduced-motion: reduce` demande à supprimer les animations non
  essentielles : ne rien animer dans les décors est cohérent.
- `theme-color` est une **suggestion** à l'agent utilisateur, en disponibilité
  limitée (pas de prise en charge par Firefox bureau) : le site ne doit pas
  promettre un rendu de la barre du navigateur.

## 5. Trois corrections réelles issues des sources

Ce n'est pas une relecture décorative : la confrontation a trouvé trois écarts,
tous corrigés et gardés par la porte.

1. **Constante de luminance périmée.** `outils/verifier-apparences.py` calculait
   la luminance avec le seuil `0,03928`. La définition W3C lue le 7 novembre 2026
   (`w3c-luminance`) donne **0,04045** depuis mai 2021. La porte est alignée. Le
   W3C précise lui-même que ce changement n'a pas d'effet pratique sur les
   calculs de WCAG : les contrastes mesurés (6,97:1 à 15,82:1) ne bougent pas.
   C'est la méthode qui est corrigée, pas un résultat.
2. **Tolérance sur les seuils de contraste.** La porte acceptait
   `mesure < seuil - 0,01`, ce qui laissait passer 4,49:1 alors que le W3C dit
   explicitement que 4,499:1 échoue. Elle compare désormais avec une marge de
   calcul à virgule flottante de `1e-9`, sans arrondi éditorial.
3. **Allégation de fréquence non sourcée.** Les documents du lot reprenaient
   « les plus utilisés sur le net », expression venue de la demande, en précisant
   déjà qu'aucune source de fréquence n'avait été consultée. MDN documente
   `light` et `dark` comme schémas **de système d'exploitation**, pas comme un
   classement des réglages offerts par les sites Web. Cette allégation est retirée
   **en tant qu'affirmation** de la note de conception, du portefeuille et des
   traces du lot — elle ne subsiste que citée comme signal de la demande — et
   remplacée par : « les trois réglages documentés par MDN (suivre l'appareil,
   clair, sombre) sont placés en tête, sans allégation de fréquence ». L'ordre
   reste une décision de conception, pas une statistique.

Aucun texte public des six thèmes n'a été modifié. Aucune feuille CSS ni aucun
script n'a été reversionné : `versionner-css-ia.py` n'avait pas lieu d'être
lancé. Le site servi reste donc strictement celui de la PR n° 283.

## 6. Ce que cette relecture n'est pas

- **Pas une validation humaine.** Le registre des relectures humaines reste vide ;
  aucune fiche n'est promue « Relue », aucun statut éditorial n'est embelli.
- **Pas une expertise de domaine.** L'agent n'est ni juriste, ni designer, ni
  spécialiste de l'accessibilité, ni représentant de l'association. Il a lu des
  références primaires et du code, et il le dit.
- **Pas un avis juridique.** Trois recherches Web datées du 7 novembre 2026
  n'ont pas trouvé d'œuvre portant exactement les noms « Bobine nocturne »,
  « Cap horizon », « Salle d'arcade ». Une recherche Web n'est **pas** une
  consultation de l'INPI ou de l'EUIPO ; « Salle d'arcade » est aussi une
  expression courante du français. Aucun dégagement de responsabilité n'est
  revendiqué.
- **Pas un essai avec des personnes.** Aucun lecteur d'écran, aucun autre
  navigateur que Chromium 153, aucune personne sensible au mouvement, aucun
  test de compréhension. La mesure de contraste porte sur les jetons déclarés,
  comme le demande le W3C, pas sur le rendu anti-aliasé à l'écran.
- **Pas une validation visuelle.** Le placement, le style et la construction
  restent du ressort de la personne, à l'œil. L'agent ne lui demande pas de lire
  ce rapport pour « valider le contenu ».

## 7. Ce qui reste ouvert

Le bref rendu clair avant l'application d'un thème sombre, dû à `site.js` chargé
en `defer` : MDN recommande une balise `<meta name="color-scheme">` placée avant
le CSS pour éviter ces éclairs, ce qui donne une piste sourcée mais non
appliquée (un script de démarrage dans l'en-tête reste un arbitrage de l'atelier).
La feuille générée de l'iframe du simulateur, la sonde `auditer-affichages.mjs`
et son faux positif de chevron décoratif, la décision de charte, la citation
signée, et les 81 prototypes en attente d'une relecture compétente restent
inchangés. Les scénarios prospectifs S1/S2/S3 ne sont pas tranchés.

## 8. Reproduire

```
python3 outils/verifier-relecture-contenus.py
python3 outils/test_mutations_relecture_contenus.py
python3 outils/verifier-apparences.py
python3 outils/registre-relecture.py
```

La première commande échoue si une source n'est pas primaire ou datée, si une
affirmation n'est pas rattachée, si une chaîne publique n'est pas couverte, si
l'une des trois corrections régresse, si une entrée apparaît dans le registre
humain, ou si l'étape disparaît de la CI ou de l'inventaire des contrôles.

