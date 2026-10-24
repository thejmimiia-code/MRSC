# EVA : première étude GLB articulée

Date : 24 octobre 2026. Statut : **ébauche technique et visuelle, pas personnage de production validé**.

## Demande et réponse limitée

L'utilisateur demande un personnage modélisé et articulé en GLB/glTF, avec coiffure, vêtements, textures et animations compatibles, après l'atelier de décor WebGL. Le décor seul ne répondait pas à cette demande.

Le fichier `assets/models/eva/eva-etude-01.glb` est créé dans le dépôt et chargé à la demande dans la page `animations.html`, accessible par Personnalisation. Il ne s'agit pas d'un avatar externe renommé, ni d'une image plane. Géométries, textures et clips sont construits par `outils/modeliser-eva.mjs` puis exportés par `outils/construire-eva-glb.cjs`.

La planche fournie par l'utilisateur sert de direction générale (cheveux châtains, haut sombre, jean évasé, accessoires cuivre). Elle n'est pas incorporée au GLB et aucune fidélité exacte n'est revendiquée. Pas de logo officiel redessiné. La création procédurale permet d'obtenir une chaîne technique vérifiable ; elle ne garantit pas une qualité de sculpture ou de direction artistique comparable à l'illustration.

## Contenu livré

- GLB autonome glTF 2.0, 3 205 048 octets, unité mètre, sans ressource distante.
- 41 os : bassin, colonne, cou/tête, épaules/bras/avant-bras/mains/doigts, cuisses/jambes/pieds/orteils. Les doigts ont des os mais pas de clips individuels.
- 11 maillages regroupés par matériau, 63 436 triangles, 11 matériaux PBR metallic/roughness. Poids interpolés notamment aux coudes, genoux et buste.
- Coiffure en calotte et mèches ondulées ; haut anthracite, jean évasé, ceinture, chaussures, collier, bracelets et boucles d'oreille. Jean continu par union implicite lissée, triangulation tétraédrique et poids de squelette, pour éviter une pièce de bassin flottante.
- Trois textures originales de 512 × 512 embarquées : peau, coton et denim. Motifs procéduraux déterministes, sans texture photographique ou asset tiers.
- Clips intégrés : `Respiration` (4 s), `Salut` (4 s), `Marche_sur_place` (2 s). Rotation d'os en quaternions. Pas de voix, synchronisation labiale, morph targets faciaux ou simulation cheveux/vêtements.

Le lecteur démarre en pose neutre, permet rotation à 360°, distance, choix du clip, lecture/pause, retour en pose neutre et fermeture. Pause hors de la section ou onglet masqué. Mouvement réduit : lecture désactivée, inspection manuelle conservée. Chargement local uniquement après clic ; repli explicite si GLB ou WebGL indisponibles. Géométries, textures, squelettes et renderer libérés à la fermeture.

## Décisions et alternatives

1. Importer un personnage tiers : non retenu sans asset identifié, droits vérifiés et fidélité satisfaisante. Aucun modèle générique présenté comme EVA.
2. Déduire automatiquement une sculpture fidèle de la seule planche : aucun service image-vers-3D utilisé ou disponible dans ce travail, donc aucun résultat fictif revendiqué.
3. Construire une première étude originale avec sources de géométrie et rig : retenu pour éprouver GLB, skinning et lecteur. **Cette décision ne vaut pas validation du style final.**

## Preuves exécutées

- [Validation glTF](validation-eva-glb-2026-10-24.json), Khronos `gltf-validator` 2.0.0-dev.3.10 : **0 erreur, 0 avertissement, 0 information**. SHA-256 du fichier inclus dans le rapport. L'export initial faisait remonter des nœuds skinnés non racines ; export en scène à racines explicites corrigé, pas de message masqué.
- `python3 outils/test_modele_eva.py` : **4 tests réussis**. Contrats du conteneur, autonomie, squelette/clips, valeurs finies, indices, poids normalisés, budgets 4 Mio / 65 000 triangles, textures PNG 512² et matériaux attendus. Ces tests n'analysent pas l'anatomie.
- [Passe navigateur](audit-eva-personnage-2026-10-24.json), `outils/test-eva-personnage.cjs` : **240 configurations** (4 largeurs × 5 tailles × 6 présentations × 2 contrastes), sans débordement horizontal global détecté. Déformation échantillonnée de sommets vérifiée pour chacun des trois clips ; rendu effectivement différent pendant lecture et stable après pause. Chargement différé, mouvement réduit, rotation manuelle, fermeture/réouverture et erreurs GLB/WebGL contrôlés.
- Captures du framebuffer examinées face/profil/dos, salut, marche et mobile. Cela ne remplace ni regard artistique indépendant ni essai sur appareil réel. Le haut de page fixe peut recouvrir une partie du cadre lors du défilement ; les captures du seul framebuffer ne mesurent pas ce chevauchement.
- Tests structurels, validateur et lecteur ajoutés à la CI ; exécution locale réussie, résultat distant non encore acquis pour ce complément.
- Régénération complète du GLB dans le même environnement : résultat identique octet pour octet. Pas de garantie de sortie binaire identique entre versions de navigateur.
- Contrôles statiques, intégration, publication locale et budgets initiaux réussis. Le détecteur de ressources citées prend désormais en compte `.mjs`, nécessaire aux imports entre chargeur et utilitaires ; aucune exclusion spécifique pour cacher une ressource orpheline.

Le moteur et le GLB sont différés : les budgets de poids initiaux ne comprennent pas les 3,2 Mo du personnage ni le chargement du moteur/chargeur après clic. Densité de rendu plafonnée à 2× ; résolution de textures limitée ; pas de FPS ni consommation GPU réels mesurés. Chromium logiciel utilisé pour les tests.

## Compatibilité : ce qui est prouvé

GLB valide et chargé avec Three.js 0.160.1/GLTFLoader ; clips et skinning exécutés. Le modèle utilise glTF standard sans extension propriétaire ou service distant. **Pas d'essai d'import Blender, Unity, Unreal, Godot ni de retargeting Mixamo réalisé** : ne pas promettre cette compatibilité sans essai dans le logiciel cible.

Provenance et licence MIT des outils conservées sous `assets/vendor/three/` et `outils/vendor/three/`. Modèle et textures originaux produits dans le dépôt, notice de périmètre jointe ; aucune licence nouvelle n'est supposée pour la planche utilisateur.

## Critique visuelle et suite

Le modèle reste sensiblement plus simple que la référence : visage peu expressif, raccords et volumes de mains simplifiés, coiffure construite en mèches géométriques, plis/contacts des vêtements et des pieds non naturels. La marche est sur place, sans IK ni garantie d'absence d'interpénétration. Les ombres et le zoom peuvent rendre les limites de triangulation et des textures visibles. La validation structurelle ne constitue donc pas une validation professionnelle de l'apparence.

Priorités : sculpter le visage et la coiffure pour se rapprocher de la référence, améliorer mains et raccords, retoucher la topologie des épaules/hanches, puis corriger poids et contacts de marche et ajouter des expressions faciales. Faire approuver face/profil/dos avant d'étendre les animations. Aucun statut de personnage final, d'identité officielle ou de conformité RGAA/WCAG n'est ajouté.
