# EVA — essai de reconstruction sur votre PC Windows

**État : lanceur préparé, pas encore essayé sur votre RTX 2070 Super. Aucun nouveau personnage réaliste fini n’a été généré par ce paquet.**

Configuration visée : Windows 11 x64, RTX 2070 Super 8 Go, 64 Go de RAM. Aucun nom d’appareil, identifiant de périphérique ou de produit n’est enregistré dans les fichiers de ce projet.

## Le lancement

1. Installez **Python 3.11 x64 avec Python Launcher**, si ce n’est pas déjà fait : [python.org](https://www.python.org/downloads/). Option Windows possible : `winget install -e --id Python.Python.3.11 --scope user`. Relancez ensuite votre terminal. Le lanceur ne remplace pas un Python existant et n’installe pas de pilote graphique.
2. Extrayez entièrement le ZIP dans un dossier local. Ne lancez pas les fichiers à l’intérieur de l’archive.
3. Lisez les précautions ci-dessous, puis double-cliquez sur **`Demarrer.cmd`** et confirmez. Ce fichier appelle PowerShell avec une autorisation limitée à ce processus ; aucune stratégie d’exécution globale n’est modifiée.

Le pilote NVIDIA doit être à jour et compatible avec le runtime CUDA 11.8. Fermez les logiciels qui utilisent beaucoup de VRAM. L’installation télécharge plusieurs Go ; prévoyez une connexion Internet et suffisamment d’espace disque, environ 25 Go libres de marge. Ne lancez pas plusieurs générations en parallèle.

**Pas besoin de WSL, de Blender, de toolkit CUDA, de compilateur C++ ni de clé API pour cet essai.** Le réseau neural tourne sur le GPU ; l’extraction de surface, le détourage et la préparation des UV sont effectués sur CPU pour éviter les extensions CUDA compilées et les contextes OpenGL fragiles sous Windows. Cette adaptation doit encore être éprouvée dans votre environnement réel.

## Ce qui est automatisé

- environnement Python séparé dans `%LOCALAPPDATA%\MRSC-EVA\venv-py311` ;
- installation des versions directes choisies, vérification `pip check` et consignation des versions résolues ;
- contrôle de CUDA et de la VRAM, sans repli silencieux sur un long calcul CPU ;
- téléchargement du code TripoSR à une révision et une empreinte contrôlées, extraction limitée sans liens ni traversée de répertoires ;
- téléchargement des poids officiels publics, résolution et consignation de leur révision ;
- chargement `torch.load` en mode `weights_only=True`, sans désactivation de cette précaution en cas d’échec ;
- détourage de la référence de face, préservation des proportions et préparation sur fond gris ;
- reconstruction de la géométrie par TripoSR ;
- atlas UV et texture neurale embarquée dans un GLB ;
- mise à l’échelle cible 1,80 m et conversion du repère Z-up de TripoSR en Y-up pour glTF ; ce n’est pas un contrôle anthropométrique ;
- rechargement du GLB exporté et rapport de succès partiel, d’échec ou de reconstruction à examiner.

La référence de **face uniquement** est utilisée. Les images profil/dos actuelles ne sont pas parfaitement calibrées et TripoSR est ici un moteur mono-image. Les passer comme entrées indépendantes ne construirait pas automatiquement un seul personnage multivue cohérent.

## Où récupérer le résultat

Dans `%LOCALAPPDATA%\MRSC-EVA\resultats\run-…\` :

- `entree-detouree.png` : entrée réellement utilisée ;
- `eva-geometrie-couleurs-non-riggee.glb` : étape géométrie avec couleurs de sommets ;
- `texture-neurale.png` : atlas si la cuisson réussit ;
- `eva-reconstruction-texturee-non-riggee.glb` : modèle texturé autonome si toutes ces étapes réussissent ;
- `rapport.json` : révision, empreintes, étapes réellement réussies et limites.

Un dossier ou une géométrie partielle ne signifie pas que la texturation a réussi. Le rapport distingue les cas. Le programme n’écrit pas « personnage fini » et ne remplace pas les fichiers du site par un résultat non examiné.

**Pour que l’agent poursuive le travail après ce calcul, transmettez le GLB obtenu et son rapport ici.** L’agent de cette session ne peut pas déclencher un processus directement sur votre PC ni en récupérer automatiquement les fichiers. Les erreurs locales peuvent mentionner des chemins utilisateur : vérifiez-les avant de partager des journaux. Aucun accès distant, ouverture de port ou envoi automatique d’image n’est installé.

## Ce que cet essai ne fait pas

- Pas de squelette, retopologie d’animation, expressions faciales ou animations générés à ce stade.
- Pas de garantie de ressemblance du visage ou de qualité des mains/cheveux. TripoSR est un moteur de reconstruction rapide ancien, pas un sculpteur spécialisé de personnages réalistes.
- Le dos et les zones invisibles sont inférés depuis une seule image.
- Un atlas 2048² ne crée pas les détails que le réseau n’a pas reconstruits ; ce n’est pas une promesse de réalisme.
- Les textures produites ne sont pas un ensemble complet de cartes PBR peau/cheveux/vêtements séparées. Le GLB utilise la couleur cuite et un matériau simple.
- Aucune durée, consommation GPU, performance ou compatibilité rig universelle n’a été mesurée sur votre PC.

Le but de ce lancement est d’obtenir le **véritable maillage de reconstruction à examiner**, avant d’investir dans la retopologie et le rig. Ce n’est pas une façon de présenter un autre prototype médiocre comme EVA finalisée.

## Choix du moteur et licences

- **TripoSR**, code et modèles annoncés sous MIT par le dépôt officiel : [README](https://github.com/VAST-AI-Research/TripoSR/blob/107cefdc244c39106fa830359024f6a2f1c78871/README.md), [licence](https://github.com/VAST-AI-Research/TripoSR/blob/107cefdc244c39106fa830359024f6a2f1c78871/LICENSE). Le README indique environ 6 Go de VRAM pour ses options par défaut ; ce n’est pas une certification de ce lanceur sur votre matériel. Les modifications d’intégration sont celles de M.R.S.C., non des fonctionnalités garanties par l’amont.
- Détourage local par rembg/U2Net ; [licence du dépôt U2Net](https://github.com/xuebinqin/U-2-Net/blob/master/LICENSE) Apache-2.0 consultée. Les dépendances Python et leurs notices restent distinctes. Ne pas interpréter la MIT de TripoSR comme une licence unique pour toute la chaîne ou la planche utilisateur.
- **Hunyuan3D 2 n’est pas installé** : la [licence consultée](https://github.com/Tencent-Hunyuan/Hunyuan3D-2/blob/f8db63096c8282cb27354314d896feba5ba6ff8a/LICENSE) exclut l’Union européenne. La seule mémoire GPU n’était donc pas le bon critère pour ce projet situé en France.

Les téléchargements concernent le code et les modèles ; les images restent traitées sur votre PC. Le lanceur désactive la télémétrie Hugging Face prévue par variable d’environnement, mais ne constitue pas un audit de trafic réseau de toutes les dépendances. Aucune souscription, crédit payant ou permission commerciale générale n’est supposée.

## Réutiliser sans réinstaller

Dans PowerShell ouvert dans le dossier du paquet :

```powershell
.\Lancer-Eva.ps1 -Generer -AccepterLicence
```

Pour un diagnostic seul : `powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\Lancer-Eva.ps1`.

En cas de mémoire insuffisante, relancer **après examen du message** avec `-Resolution 192 -Texture 1024` réduit le coût, mais aussi la définition du résultat. Aucun basculement automatique de qualité n’est caché.

Les caches et poids restent hors Git dans `%LOCALAPPDATA%\MRSC-EVA`. Le lanceur ne supprime pas vos fichiers ou des logiciels existants. Les dépendances directes sont épinglées ; les dépendances transitives et les versions de pilotes restent à contrôler, sans promesse d’absence de vulnérabilités.
