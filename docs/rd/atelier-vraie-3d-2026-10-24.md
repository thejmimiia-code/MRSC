# Atelier : première scène réellement 3D

Date : 24 octobre 2026. Statut : prototype technique, direction esthétique non validée.

## Besoin

Après la page 2,5D, l'utilisateur exige de trouver un moyen d'obtenir de la 3D. La parallaxe ne répond pas à cette exigence. Ajouter une vraie scène à la page existante, sans présenter une image plane ou un mannequin générique comme EVA modélisée.

## Réalisation

Three.js 0.160.1 (MIT, source et licence conservées dans `assets/vendor/three/`) chargé localement par import dynamique après clic explicite. Pas de CDN ni de service de génération externe. Géométries procédurales originales : bureau et pieds, carnet avec couverture/tranche/élastique, tasse ouverte à profil tourné, anse, lampe cuivre avec abat-jour, éclairage et ombres. Caméra perspective avec orbite, hauteur et distance ; animation de caméra optionnelle.

Ce sont des maillages 3D, mais pas des assets artistiques de production ni une reproduction photoréaliste de la planche. La tasse et le bureau constituent une preuve de moteur, pas un substitut au personnage demandé. Aucun modèle articulé d'EVA créé ou chargé dans ce lot.

## Options

- Continuer exclusivement en CSS 2,5D : écarté, ne satisfait pas la demande de vraie 3D.
- Importer immédiatement un personnage gratuit quelconque : écarté, fidélité à EVA et droits non vérifiés.
- Valider d'abord rendu et contrôles sur une scène originale simple : retenu pour cette étape, sans prétendre achever le personnage.

## Mouvement et ressources

Aucun moteur chargé avant clic. Moteur minifié : 670 681 octets bruts, téléchargé une fois après activation (hors coût initial de page). Ce surcoût n'est pas inclus dans les budgets initiaux estimés par le vérificateur de poids. Taille des buffers au maximum 2× la taille CSS : limite explicite, pas promesse de netteté illimitée à 3×/zoom. Ombres 1024² susceptibles de présenter des limites visuelles. Aucun FPS ni consommation GPU mesurés.

Pas de boucle au repos. Pause à la sortie du cadre ou au masquage de l'onglet ; pas de reprise automatique. Préférence système de mouvement réduit bloque l'animation mais laisse les curseurs manuels actifs. Fermeture libère géométries, matériaux et renderer ; perte de contexte arrête la scène et propose de réessayer. Sans WebGL : message explicite et études 2,5D conservées. Les commandes 3D sont distinctes de celles des études CSS pour ne pas laisser croire à un contrôle global.

## Vérifications réellement exécutées

`outils/test-atelier-3d.cjs`, Chromium/Puppeteer avec rendu logiciel dans le sandbox :
- 240 configurations (4 largeurs × 5 tailles de texte × 6 présentations × 2 contrastes) : pas de débordement horizontal global détecté ; pas un test exhaustif de chaque boîte ni une validation des matières dans tous les modes.
- Pas de requête moteur avant clic ; ouverture WebGL et caméra effectivement animée ; pause ; mouvement réduit ; curseur manuel utilisable avec cette préférence ; fermeture/réouverture ; repli avec getContext indisponible : réussis.
- Capture grand écran inspectée ; aucun essai sur GPU/téléphone physique ni lecteur d'écran.
- Contrôles statiques, publication locale, intégration et budgets initiaux : réussis. Licence et provenance liées depuis la page.

Ces contrôles ne constituent ni certification RGAA/WCAG ni validation esthétique humaine.

## Suite pour EVA

Obtenir un asset GLB/glTF articulé, fidèle à la planche : modèle, coiffure, vêtements, matériaux, textures et squelette. Vérifier les droits de chaque asset et les contraintes de licence avant intégration. Valider le personnage en pose neutre (face/profil/dos), puis les gestes et expressions, avec un budget de triangles, de textures et de téléchargement défini après mesure. Aucun service image-vers-3D ni résultat de génération de personnage n'a été utilisé ou revendiqué ici.

Décision à prendre : valider la base de rendu et la direction de matière, puis passer au personnage — ne pas confondre l'approbation d'un décor avec celle d'EVA. Revue avant import d'asset et avant extension hors atelier.
