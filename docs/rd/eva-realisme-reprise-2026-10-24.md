# EVA : reprise après rejet du prototype procédural

Date : 24 octobre 2026. Statut : **références IA de travail ; reconstruction réaliste non exécutée**.

## Correction de trajectoire

L'utilisateur a explicitement rejeté le GLB procédural, jugé laid et très éloigné d'EVA. La validité glTF, le squelette et les clips ne répondent pas au besoin de réalisme et de ressemblance. Le modèle n'est donc plus présenté comme une direction à valider : il est conservé dans une archive repliée de l'atelier, avec mention explicite du rejet. Aucun nouveau maillage rudimentaire n'a été fabriqué pour donner l'impression de progresser vers le réalisme.

## Travail effectivement réalisé

Trois images originales de travail, générées à partir de la planche fournie : face, profil gauche et dos. La face a été créée en premier, puis utilisée comme référence supplémentaire pour le profil et le dos. Direction : adulte aux proportions naturelles, cheveux châtains ondulés, haut anthracite marqué EVA, jean évasé, ceinture et accessoires sobres, fond neutre.

Les PNG sont sous `assets/images/eva-references/`, **848 × 1264 pixels chacun**, sans agrandissement artificiel. Aperçus WebP de mêmes dimensions, 150 134 octets cumulés ; les PNG ne sont téléchargés qu'en suivant leur lien. Les détails reconstruits par IA ne constituent pas une preuve de ce que contient exactement l'illustration source. Les images ne proviennent pas d'un modèle 3D existant et n'ont pas servi à exporter un nouveau GLB.

[Dimensions et empreintes des fichiers](eva-references-2026-10-24.json). Les aperçus sont plafonnés à 424 CSS px : leur définition native suffit à cette largeur à 2×, pas à tout zoom ou densité. Les PNG et WebP sont distingués ; aucune recompression n'est présentée comme un gain de résolution.

## Critique des références

Amélioration visible du visage, de la matière des cheveux et des vêtements par rapport au prototype procédural. **Pas de validation artistique de l'utilisateur acquise.** Le visage reste une interprétation ; le réalisme demandé n'autorise pas à changer silencieusement l'identité du personnage.

Les vues sont produites séparément, non calibrées : pose des bras, longueur et volume des cheveux, bijoux, plis, hauteur apparente et détails du jean varient. La vue de profil n'est pas une mesure orthographique de la même surface que la face. Elles ne doivent pas être annoncées comme des entrées multivues parfaitement cohérentes. Étape suivante sur ces images : aligner les repères corporels et corriger les divergences avant de tenter un mode de génération exigeant des vues calibrées. Ne pas étirer les images pour masquer des différences de proportions.

La planche utilisateur est une référence d'identité ; aucune permission commerciale générale ni droit indépendant sur son contenu n'a été vérifié. Aucun logo officiel M.R.S.C ou information personnelle de la planche n'est recopié dans les nouvelles images.

## Piste de reconstruction vérifiée, mais bloquée

Documentation effectivement lue le 24 octobre 2026 : Tencent Hunyuan3D 2.1, README et `hy3dshape/hy3dshape/pipelines.py`, à la révision GitHub `82920d643c0dc2f7bfd7255f45f62d386edfe60c`.

- [README épinglé](https://github.com/Tencent-Hunyuan/Hunyuan3D-2.1/blob/82920d643c0dc2f7bfd7255f45f62d386edfe60c/README.md) : annonce 10 Go de VRAM pour la géométrie, 21 Go pour les textures et 29 Go pour l'ensemble ; installation avec PyTorch CUDA et compilation de composants de rendu. Le mode `--low_vram_mode` ne démontre pas que cette chaîne convient à ce sandbox sans GPU.
- [Pipeline épinglé](https://github.com/Tencent-Hunyuan/Hunyuan3D-2.1/blob/82920d643c0dc2f7bfd7255f45f62d386edfe60c/hy3dshape/hy3dshape/pipelines.py) : paramètres de périphérique CUDA par défaut et fonctions d'offload CPU. Un offload ne constitue pas une validation d'exécution intégrale en CPU avec peu de mémoire.
- Environnement réellement inspecté : pas de commande `nvidia-smi`, pas de périphérique `/dev/nvidia*`, environ 3,8 Gio de RAM. Cette piste n'est pas exécutable ici telle que documentée. Aucune installation lourde, aucun téléchargement de poids ou génération de maillage n'a été prétendu.
- Vérification précédente des outils connectables : Tripo et Meshy non pris en charge par les connecteurs de cette session. Aucun compte, envoi d'image ou appel à ces services effectué. Aucun crédit acheté et aucune donnée d'authentification demandée.

Cette recherche ne prouve pas qu'aucune méthode de reconstruction CPU n'existe ; elle indique pourquoi la piste citée dans le conseil de l'utilisateur n'a pas été exécutée ici. Pas de prédiction de durée ou de qualité inventée.

## Vérifications du site

Deux tests d'intégrité des références : dimensions et SHA-256 des PNG, taille et signature WebP des aperçus, originaux séparés des sources d'images de page. Test navigateur du lecteur archivé rejoué sur 240 configurations : préserve les essais techniques et l'absence de chargement GLB avant clic ; cela ne valide pas artistiquement le modèle rejeté.

Statique, publication locale et budgets : réussis ; atelier autour de 270 Kio initiaux estimés, proche du budget mobile 300 Kio. PNG originaux et ancien GLB restent des téléchargements après action. Les anciens rapports de tests ne sont pas gonflés pour devenir des preuves de réalisme.

## Prochaine étape et critère de livraison

Accéder réellement à un moteur image-vers-3D adapté, puis corriger le maillage et les matériaux, produire un rig exploitable et contrôler visage, mains, coiffure, articulations et contacts. Ne livrer comme « EVA réaliste finalisée » qu'un modèle examiné sous tous les angles et en mouvement, avec source éditable et droits identifiés. **Aucun fichier fini de ce niveau n'est encore livré.** L'utilisateur n'a pas à être chargé de toutes ces étapes sous prétexte qu'un script ou des références ont été préparés.
