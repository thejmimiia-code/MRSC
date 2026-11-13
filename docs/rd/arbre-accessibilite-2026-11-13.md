# Arbre d’accessibilité : ce que le navigateur expose, mesuré le 13 novembre 2026

Statut : **relevé technique par l’agent**, pas un audit d’accessibilité, ni une
conformité RGAA ou WCAG, ni une validation par une personne experte, ni un essai
avec un lecteur d’écran. Aucun essai avec des personnes n’a eu lieu.

## Pourquoi ce relevé

Le dépôt mesurait déjà quatre couches d’accessibilité, chacune avec son outil :
les contrastes (`mesurer-cadrages.cjs`, `cadrages.py`), l’indicateur de focus
(`mesurer-focus.cjs`, `focus.py`), la taille des cibles et l’espacement du texte
(`auditer-criteres-22.mjs`), et les violations que `axe-core` sait voir
(`verifier-accessibilite.cjs`). Aucune de ces mesures ne dit ce qu’un lecteur
d’écran **reçoit**. Une page peut nommer une cible dans son HTML et l’annoncer
sans nom ; une image peut porter `alt=""` et rester exposée ; une liste peut
perdre sa sémantique sans qu’aucun contrôle ne s’en aperçoive.

Ce relevé comble ce trou, et rien de plus : il lit l’arbre d’accessibilité de
Chromium, rôle par rôle, nom par nom.

## Méthode

- Sonde : `outils/mesurer-arbre-accessibilite.cjs` — protocole CDP
  `Accessibility.getFullAXTree` et `DOM.getDocument`, dans un vrai Chromium
  (`HeadlessChrome/153.0.8010.0`).
- Verdict : `outils/arbre-accessibilite.py` — les règles, les refus, les constats.
- Banc : `outils/test_arbre_accessibilite.py` — 24 cas sans navigateur.
- Périmètre : **122 pages publiées**, mesurées à 1 280 px, après exécution des
  scripts et stabilisation du chargement. 0 erreur de mesure.
- Serveur local (`python3 -m http.server`), aucun réseau, aucune donnée
  personnelle.

L’ordre des titres est **relu dans le DOM**, par identifiant de nœud :
`getFullAXTree` rend ses nœuds dans l’ordre de son arbre interne, pas dans celui
du document. La première version s’en est fiée à l’ordre rendu et a accusé deux
« niveaux sautés » sur `anglais-aventure.html` et `ia-societe.html` — les titres
de niveau 2 y arrivaient avant le titre de niveau 1. Les deux accusations ont
disparu une fois l’ordre corrigé. C’est le seul faux positif de ce lot, et il a
été trouvé avant d’être publié.

## Ce que le relevé a trouvé

| Ce qui est mesuré | Avant | Après | Ce que le nombre vaut |
| --- | --- | --- | --- |
| Listes sans puces et sans `role="list"` | **397** sur 121 pages | **0** | WebKit retire la sémantique de liste d’un `ul { list-style: none }` ; Chromium la garde, donc le défaut était invisible ici |
| Titres exposés | 1 501 | 1 501 | Un seul `h1` par page (maximum mesuré : 1) ; aucun niveau sauté |
| Repères exposés | 1 767 | 1 767 | Un `main` par page ; aucun repère de même rôle et de même nom |
| Cibles interactives | 5 649 | 5 649 | **0 sans nom accessible** |
| Images du document | 367 | 367 | 123 déclarées décoratives (`alt=""`), **toutes hors de l’arbre** ; 246 exposées, toutes nommées ; **0 sans `alt`** |
| Listes au document | 1 079 | 1 079 | 953 exposées ; les autres sont dans des `<details>` fermés, donc hors de l’arbre — ce n’est pas une perte |
| Zones vivantes | 740 | 740 | 244 vides au repos (deux par page : réglages d’accessibilité, lecture à voix haute) — voir plus bas |
| Cadres exposés | 0 | 0 | **angle mort déclaré** : l’iframe du simulateur n’était pas montée au moment de la mesure |

### La seule correction de fond : 397 listes muettes

`assets/css/site.css` retire les puces de nombreuses listes (`list-style: none`).
Dans Chromium, un `ul` reste un `ul` : la structure survit. Dans WebKit — donc
Safari et VoiceOver — la sémantique de liste **disparaît** : le lecteur
n’annonce plus « liste de 10 éléments », il énumère des liens. Le 13 novembre
2026, 397 listes du site étaient dans ce cas sur 121 pages, dont les trois
listes du pied de page présentes sur toutes les pages (navigation, documents,
mentions légales).

Correction appliquée : `role="list"` sur **1 085 balises** `ul`/`ol` du site,
y compris celles qui gardent leurs puces. Une règle unique vaut mieux qu’une
règle qui dépend du style calculé : celui-ci change avec la présentation, la
taille du texte et le mode d’affichage, et une liste qui perd sa puce dans un
mode perdrait sa sémantique dans le même geste. Une seule liste reste sans
attribut, celle des sources d’`apprendre.html` : elle garde ses puces à toutes
les largeurs et dans tous les modes, sa sémantique n’est jamais retirée.

Le relevé compte **1 078 listes** portant l’attribut dans les documents. L’écart
avec les 1 085 balises vient de sept listes placées dans des contenus de gabarit
que la sonde DOM ne traverse pas — elles ne sont pas mesurées, seulement
corrigées.

Trois sources produisent ces balises, et les trois ont été corrigées pour que la
régénération ne défasse rien :

- `outils/construire-apprentissages.py` (la page Apprendre et les 108 fiches) ;
- `simulateur/interface.py` (le simulateur bâti) ;
- les 13 pages écrites à la main.

Deux contrôles lisaient la balise d’ouverture **mot pour mot** et refusaient
l’attribut ajouté : `verifier-affichages.py` (`<ul class="footer-legal">`) et
`verifier-decision-prospective.py` (`<ol class="knowledge-compass">`). Tous deux
lisent désormais la classe par expression régulière — ce qu’ils comptent est la
présence de la liste, pas l’écriture d’un attribut.

### Deux constats qui ne sont pas des fautes

**Les zones vivantes vides.** 244 zones `role="status"` sont vides au repos,
deux par page. C’est légitime — elles servent à annoncer un changement — mais
« légitime » se vérifie. Les trois modules d’accessibilité ont donc été
actionnés dans un vrai Chromium : la zone annonce « Lecture facilitée :
activé. », puis « Réduire les mouvements : activé. », puis « Repères clavier
visibles : activé. ». Les boutons portent `aria-pressed` et leur nom ne change
pas. Mesuré, pas supposé.

**Les passages en langue étrangère.** La page `anglais-aventure.html` déclare des
passages en `en` et en `fr`. Ce relevé ne juge pas la langue du texte : il les
nomme sans les trancher.

## Ce que ce relevé ne dit pas

- Il mesure **Chromium** seulement. La règle des listes est **préventive** : elle
  protège WebKit, que ce dépôt ne peut pas mesurer. Firefox n’est pas mesuré non
  plus.
- Il ne dit rien de l’**ordre de lecture** réel, de la qualité des noms
  accessibles (un nom présent peut être incompréhensible), de la compréhension,
  ni du rendu sonore d’un lecteur d’écran.
- Une seule largeur (1 280 px) et un seul état par page : panneaux fermés,
  menus fermés, `<details>` fermés. Les états interactifs ne sont pas balayés
  ici — `verifier-accessibilite.cjs` en couvre une partie, avec `axe-core`.
- L’iframe du simulateur n’a pas été exposée au moment de la mesure : la règle
  « cadre nommé » n’a rien eu à juger. Elle existe et reste à éprouver.
- Aucune revue par une personne experte, aucune navigation au lecteur d’écran,
  aucune personne utilisatrice. Les chiffres sont ceux de l’agent.

## Décisions et suite

1. Le refus des listes sans `role="list"` est **actif** : le site est à zéro, et
   une liste ajoutée sans l’attribut fera échouer la CI. C’est un choix
   préventif assumé, écrit dans l’outil.
2. Le relevé est **câblé** dans le job `graphismes`, seul job qui installe
   Chromium ; les échecs y sortent en annotations lisibles par l’API, le journal
   complet de l’exécution n’étant pas accessible depuis l’atelier.
3. Ce qui reste à faire, et qui n’est pas mécanisable ici : faire relire
   l’ensemble par une personne compétente en accessibilité ; faire une passe au
   lecteur d’écran avec une personne qui l’utilise ; mesurer les états
   interactifs dans l’arbre ; éprouver l’iframe du simulateur ; Firefox.
