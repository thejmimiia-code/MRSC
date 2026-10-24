# Three.js 0.160.1

- Auteur : three.js authors / mrdoob.
- Source : https://registry.npmjs.org/three/-/three-0.160.1.tgz
- Projet : https://github.com/mrdoob/three.js/tree/r160
- Récupéré le 24 octobre 2026 via `npm pack three@0.160.1`.
- `build/three.module.min.js` copié sans modification sous le nom `three.module.min.mjs` pour identifier explicitement le module ES. Licence MIT jointe, conservée intégralement.
- Chargement local différé après clic dans l'atelier, aucun CDN, télémétrie ou téléchargement de modèle externe. Version épinglée, pas de promesse d'absence de vulnérabilités ; revue avant mise à jour ou extension d'usage.

## Chargeur GLB et outils d'export

`examples/jsm/loaders/GLTFLoader.js` et `utils/BufferGeometryUtils.js` de la même archive 0.160.1 sont conservés dans `addons/` sous extension `.mjs`. Seuls les imports sont adaptés au moteur local et aux chemins relatifs. `GLTFExporter.js` et `TextureUtils.js` sont conservés sous `outils/vendor/three/` avec la même licence MIT, pour la génération hors publication. Aucun changement de logique de ces bibliothèques.
