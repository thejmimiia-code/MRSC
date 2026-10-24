# EVA — préparer un calcul réel sur le GPU local

Date : 24 octobre 2026. Statut : **lanceur expérimental préparé ; inférence non exécutée sur le PC utilisateur**.

## Besoin et configuration utile

L'utilisateur demande de créer réellement le personnage, puis indique disposer de Windows 11 x64, d'un i9-9900KF, de 64 Go de RAM et d'une RTX 2070 Super 8 Go. Seules ces caractéristiques utiles sont retenues : aucun nom de PC, identifiant de périphérique ou de produit n'est copié dans les sources, le paquet ou ce journal.

Le sandbox de l'agent n'a pas accès à ce GPU ou au PC. Préparer un lancement local ne signifie pas avoir lancé le calcul ni récupéré son résultat. Le paquet n'installe aucun outil de contrôle distant et n'ouvre aucun port.

## Correction du choix de moteur

Hunyuan3D 2 a d'abord été envisagé pour ses variantes mini. La lecture de sa [licence à révision épinglée](https://github.com/Tencent-Hunyuan/Hunyuan3D-2/blob/f8db63096c8282cb27354314d896feba5ba6ff8a/LICENSE) montre une exclusion de l'Union européenne, du Royaume-Uni et de la Corée du Sud. Cette version n'est donc pas proposée à l'installation pour ce projet en France. Le diagnostic précédent ne devait pas s'arrêter à la VRAM.

Choix pour un **premier essai de reconstruction**, pas pour garantir le réalisme final : [TripoSR, révision 107cefdc244c39106fa830359024f6a2f1c78871](https://github.com/VAST-AI-Research/TripoSR/tree/107cefdc244c39106fa830359024f6a2f1c78871). Son README annonce environ 6 Go de VRAM avec les options par défaut, et une licence MIT couvrant code et modèles. Cela rend un essai plausible sur 8 Go, sans prouver que notre adaptation complète tient sur cette carte. Le service commercial Tripo et ce modèle open source ne sont pas la même offre.

Le moteur est ancien et mono-image ; les doigts, le visage et les zones cachées peuvent être mal reconstruits. Le choix est réversible : si le maillage ne se rapproche pas suffisamment d'EVA, ne pas investir dans un rig qui masquerait les défauts ou annoncer une livraison finie.

## Contenu préparé

`outils/eva-local/` contient un lanceur Windows natif, un environnement Python 3.11 séparé et les étapes de reconstruction. Pas de WSL ou toolkit CUDA nécessaire à cette proposition : PyTorch CUDA utilise le GPU pour le réseau, tandis que l'extraction par marching cubes et la préparation d'atlas UV sont déportées sur CPU. Cela évite la compilation de torchmcubes et les contextes OpenGL de l'outil amont.

Le paquet de livraison est construit par `outils/preparer-eva-local.py --sortie <hors-du-depot.zip>`. Il contient le code, les instructions, un manifeste d'empreintes et la seule référence de face. Il ne contient ni l'ancien mannequin rejeté, ni un nouveau modèle prétendument généré, ni des poids de plusieurs Go.

Étapes visées après exécution volontaire sur le PC :

1. installer les dépendances dans un venv utilisateur (pas de changement de stratégie PowerShell globale) ;
2. vérifier CUDA, capacité et VRAM libre ; ne pas passer silencieusement en calcul CPU ;
3. télécharger la source TripoSR à commit et SHA-256 fixes ; extraction limitée sans liens ni traversée de chemins ;
4. charger les poids officiels publics, résolution/empreinte de la version consignées ; chargement `weights_only=True` ;
5. détourer et préparer l'image localement, sans étirement ;
6. reconstruire la géométrie et sauvegarder un GLB de couleurs de sommets ;
7. déplier les UV, interroger le champ neural pour cuire une texture, exporter un GLB texturé autonome et le recharger ;
8. produire un rapport distinguant réussite, résultat partiel et échec.

Sortie attendue si le calcul réussit : `eva-reconstruction-texturee-non-riggee.glb`, dans `%LOCALAPPDATA%\MRSC-EVA\resultats\run-…`. **Aucun squelette, aucune animation et aucun visage professionnel final ne sont produits ou promis par ce premier lancement.** Le fichier est destiné à l'examen avant retopologie et rig. Une texture cuite 2048² n'ajoute pas les détails que le réseau n'a pas reconstruits.

## Vérifications réellement exécutées ici

- **9 tests CPU/contrats réussis**, `outils/test_eva_local.py` : archive filtrée, empreinte/traversée/liens refusés, paquet reproductible sans ancien GLB, absence d'installateur Hunyuan, rasterisation barycentrique/UV, marges de texture, axes de marching cubes, mise à l'échelle et rechargement GLB. La cuisson UV est éprouvée avec un **champ de couleurs simulé**, pas des poids TripoSR ou une inférence GPU.
- Archive officielle réellement récupérée depuis codeload GitHub : SHA-256 `bcb414550dcfcb9f5ea6a7b9c12f2bbff889f5b4a564a493178393360d9034ec`. Extraction limitée, correction explicite `weights_only=True` et vérification d'un cache existant éprouvées.
- Présence de wheels Windows CPython 3.11 vérifiée dans les métadonnées PyPI pour les dépendances natives xatlas 0.0.9, onnxruntime 1.17.3, scikit-image 0.22.0 et Pillow 11.3.0. Cela ne valide pas toute la résolution des dépendances ou l'installation Windows.
- Tests Windows dédiés ajoutés à la CI : syntaxe PowerShell, propagation des codes d'échec et chemins avec espaces. Pas d'installation ou de GPU dans ce job. Son résultat distant doit être distingué des tests CPU réellement acquis ici.
- Dépendances directes choisies et épinglées ; transitives consignées par `pip freeze` sur le PC cible, pas une garantie d'environnement entièrement verrouillé ou d'absence de vulnérabilités.

## Limites et prochaine action

Pas de Windows, pilote NVIDIA ou RTX 2070 Super accessible depuis cette session ; ni installation du venv Windows, téléchargement des poids, détourage complet U2Net, inférence TripoSR réelle ou qualité finale d'EVA éprouvés ici. Pas de durée d'exécution annoncée. La licence MIT du moteur ne remplace pas les notices des dépendances ni la vérification des droits de la référence.

La seule façon prévue de démarrer ce calcul sur le PC est l'exécution locale volontaire du paquet par l'utilisateur ; l'agent ne peut pas déclencher cette étape à distance. Il faudra récupérer le résultat effectif pour poursuivre sa correction. Ne pas transformer ce prérequis matériel en promesse que le personnage demandé est déjà fini, ni demander à l'utilisateur d'effectuer lui-même la modélisation et le rig.
