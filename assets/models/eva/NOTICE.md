# EVA — étude procédurale 01

Date : 24 octobre 2026. Fichier : `eva-etude-01.glb` (glTF 2.0 binaire autonome, unité mètre).

**Prototype rejeté par l’utilisateur pour son apparence trop rudimentaire et éloignée d’EVA. Conservé comme archive technique, pas comme direction artistique acceptable ni personnage de production.**

## Création et contenu

Géométries, textures et mouvements originaux générés par `outils/modeliser-eva.mjs`. Aucun modèle humain, texture photographique ou animation externe importé. La planche EVA fournie par l'utilisateur sert de référence générale (cheveux bruns, haut sombre, jean évasé, accessoires cuivre), sans être incorporée au GLB. Aucun logo officiel redessiné ou texture de marque copiée.

Squelette avec bassin, colonne, tête, bras, mains/doigts et jambes. Maillages à attributs JOINTS_0/WEIGHTS_0 ; interpolation des poids aux coudes, genoux et buste. Coiffure modélisée en calotte et mèches ondulées ; t-shirt, jean, ceinture, chaussures, collier, bracelets et boucles d'oreille. Trois textures originales embarquées de 512 × 512 : peau, coton et denim. Matériaux PBR metallic/roughness.

Clips glTF intégrés : `Respiration` (4 s), `Salut` (4 s), `Marche_sur_place` (2 s). Les clips animent les rotations de certains os ; les doigts ne disposent pas de clips individuels. Pas de synchronisation labiale, morph targets, expressions faciales ni simulation physique de cheveux/vêtements.

## Limites

Visage et corps procéduraux simplifiés, sans prétention de ressemblance exacte. Pièces de maillage séparées, topologie non conçue pour une sculpture de production ; risques d'interpénétration et plis peu naturels. Cheveux attachés à l'os tête, pas de mouvement secondaire. Marche cyclique sur place, sans contacts de pied ou locomotion garantis. Pas de certification de compatibilité universelle : tester le GLB dans le logiciel cible (Blender, moteur de jeu…) avant utilisation.

Version d'étude, à revoir sur vues face/profil/dos et en mouvement. Densité de rendu web plafonnée à 2× ; textures limitées à 512². Aucune netteté illimitée, validation artistique humaine ou conformité accessibilité revendiquée.

## Outils et droits

Modèle original produit dans le dépôt M.R.S.C ; pas de licence d'asset tiers supposée. Consulter la licence générale du dépôt avant redistribution ; cette notice ne réattribue pas les droits de la planche de référence. Génération et export via Three.js 0.160.1 / GLTFExporter (MIT), licence conservée dans `assets/vendor/three/LICENSE`. Pas de service externe, compte ou collecte.

Reconstruction : servir la racine du dépôt en HTTP, installer Puppeteer/Chromium hors dépôt, puis exécuter `outils/construire-eva-glb.cjs` avec `MRSC_BROWSER_NODE_MODULES` et, si nécessaire, `LD_LIBRARY_PATH`. L'exporteur utilise le canvas du navigateur pour les textures. Les sources sous `outils/` ne sont pas nécessaires à la visualisation publique.
