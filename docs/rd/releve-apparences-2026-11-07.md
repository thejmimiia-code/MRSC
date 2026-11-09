# Relevé navigateur des six apparences — 7 novembre 2026

**Mesure datée, dans un vrai Chromium, sur le serveur local du dépôt.** Elle dit ce qui a été observé, pas ce qu'une personne a validé. Le résumé machine est dans [`releve-apparences-2026-11-07.json`](releve-apparences-2026-11-07.json). Les relevés antérieurs gardent leur date.

## 1. Environnement

- `HeadlessChrome/153.0.8010.0` (`@sparticuz/chromium` 153.0.0), `puppeteer-core` 25.16.0, bibliothèques `al2023.tar.br` extraites pour `LD_LIBRARY_PATH`.
- `outils/serveur-local.py` sur `127.0.0.1:4180` : pages réelles, moteur `/api` monté.
- Sonde locale `verifier-themes.mjs` (hors dépôt), deux largeurs (320 et 1 440 px), six thèmes, soit **12 relevés**.
- Contraste calculé selon WCAG 2.2 à partir des styles calculés (`getComputedStyle`), sans approximation de palette.

## 2. Résultats

| Apparence | Fond résolu | Corps | Lien | Bouton | Défilement horizontal |
| --- | --- | ---: | ---: | ---: | ---: |
| Suivre l'appareil (système clair) | clair | 15,51:1 | 6,97:1 | 6,97:1 | 0 px |
| Papier clair | clair | 15,51:1 | 6,97:1 | 6,97:1 | 0 px |
| Nuit sobre | sombre | 15,82:1 | 8,98:1 | 9,48:1 | 0 px |
| Bobine nocturne | sombre | 15,82:1 | 8,72:1 | 9,20:1 | 0 px |
| Cap horizon | sombre | 15,82:1 | 10,76:1 | 11,36:1 | 0 px |
| Salle d'arcade | sombre | 15,82:1 | 11,98:1 | 12,64:1 | 0 px |

Identiques à 320 px et à 1 440 px. **Aucun débordement**, aucune paire sous 4,5:1 ; le minimum mesuré est 6,97:1.

Six captures réelles de l'accueil et une du panneau ouvert ont été prises dans le même navigateur ; les deux premières (« Suivre l'appareil » et « Papier clair ») sont identiques ici, l'appareil de mesure étant en préférence claire. Les trois palettes inspirées se distinguent par la surface de navigation, les accents et un décor discret, sans image ni animation ajoutée.

### Un défaut trouvé puis corrigé dans le même lot

Le premier passage donnait **1,97:1** (Nuit sobre), **2,03:1** (Bobine nocturne), **1,65:1** (Cap horizon) et **1,48:1** (Salle d'arcade) sur le texte des boutons : le bloc de jetons généré réécrivait `--on-accent` en blanc après la surcharge destinée à le passer en encre sombre. La surcharge a été déplacée en fin de bloc et trois règles qui écrivaient du blanc sur fond bleu ont été reprises. Le second passage donne les valeurs du tableau ci-dessus. `verifier-apparences.py` garde cette correction sous contrôle.

## 3. Comportements observés

| Scénario | Résultat |
| --- | --- |
| Six choix dans le panneau | `systeme`, `clair`, `sombre`, `bobine`, `horizon`, `arcade` — 6 boutons radio, libellé et statut `role="status"` |
| Clic sur « Salle d'arcade » | `data-apparence="arcade"`, `data-apparence-fond="sombre"`, statut « Apparence « Salle d'arcade » appliquée. », clé `mrsc-apparence=arcade` |
| Rechargement | Le choix `arcade` est toujours appliqué |
| Échap | La section « Apparence » se referme et le focus revient à son résumé |
| Stockage local bloqué | Le thème « Cap horizon » s'applique pour la visite, sans erreur ni donnée envoyée |
| `prefers-color-scheme` | « Suivre l'appareil » passe à `sombre` (fond `rgb(17, 24, 39)`) en préférence sombre, puis revient à `clair` (fond blanc) sans rechargement |
| `theme-color` | Mis à jour pour chaque thème |
| Suite navigateur du dépôt | `outils/test-experience.cjs` : **13/13**, avec le panneau passé de quatre à cinq réglages |

## 4. Ce que ce relevé ne prouve pas

- Un seul navigateur, une seule page pour les contrastes calculés, aucun lecteur d'écran, aucune personne, aucun essai d'usage.
- Les états de survol, de focus et de panneau ouvert ne sont pas mesurés thème par thème ; la porte hors ligne vérifie les paires de jetons déclarées, pas toutes les combinaisons rendues.
- L'iframe du simulateur reçoit les attributs mais garde sa propre feuille générée : elle ne suit pas les thèmes.
- `site.js` est chargé en `defer` : un thème sombre mémorisé peut s'appliquer après un bref rendu clair.
- Aucune validation humaine des noms, des palettes, de leur ordre ou de leur intérêt. La relecture de contenu et des sources a été prise en charge par l'agent le 7 novembre 2026 (`relecture-apparences-2026-11-07.md`) ; elle n'est pas une validation humaine et n'écrit rien dans `relectures.toml`. Ce relevé ne transforme aucune proposition en décision de l'association.
