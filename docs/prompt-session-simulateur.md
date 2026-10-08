# Consignes de maintenance du simulateur hébergé séparément

Ce document s’adresse aux personnes qui travaillent dans le dépôt du simulateur :
[`thejmimiia-code/D-mocratie-et-politique-du-peuple-pour-le-peuple-par-le-peuple`](https://github.com/thejmimiia-code/D-mocratie-et-politique-du-peuple-pour-le-peuple-par-le-peuple).

## Adresse publique à utiliser

L’adresse active communiquée pour le simulateur est :

**<https://simulateur-macro-politique.onrender.com/>**

Ne pas la remplacer par l’ancienne adresse Vercel du simulateur. Les mentions de Vercel dans le diagnostic `docs/diagnostic-404-vercel.md` sont historiques ; elles ne désignent pas l’hébergement actif de l’outil.

Le site public M.R.S.C est <https://thejmimiia-code.github.io/MRSC/>. Depuis le simulateur, conserver un moyen visible de revenir au site M.R.S.C, y compris sur petit écran.

## Contrat de fonctionnement

1. `GET /` sert l’application interactive complète, et non une page de présentation.
2. Les routes `/api/...` du moteur répondent à la même origine que la page. Celle-ci les appelle en chemins absolus : page et API doivent donc rester à la racine du même domaine.
3. La page peut être intégrée dans un `<iframe>` du site M.R.S.C : ne pas envoyer d’en-tête `X-Frame-Options` ni de directive `Content-Security-Policy: frame-ancestors` qui en interdirait l’intégration.
4. Préserver le retour visible vers le site M.R.S.C, l’usage au clavier, les commandes de parcours, l’adaptation aux petits écrans et les réglages de lisibilité/contraste.
5. Distinguer les résultats du modèle des prévisions : expliquer les hypothèses et la provenance des données sans présenter les simulations comme des certitudes.

Les routes connues comprennent `/api/catalogue`, `/api/contexte`, `/api/simuler`, `/api/bulles`, `/api/run`, `/api/scenarios`, `/api/export`, `/api/presets`, `/api/comparer`, `/api/bulle`, `/api/donnees` et `/api/proxy`. Vérifier le code du moteur pour repérer d’éventuelles routes plus récentes plutôt que de s’en tenir à cette liste.

## Vérifications avant de déclarer un changement publié

Depuis un réseau qui autorise les requêtes vers Render, vérifier au minimum :

- que `GET https://simulateur-macro-politique.onrender.com/` retourne la vraie page interactive ;
- que `/api/scenarios` et `/api/catalogue` retournent des réponses JSON valides ;
- qu’une requête de simulation valide à `/api/simuler` produit un résultat ;
- que l’application peut être affichée depuis la page `simulateur.html` du site M.R.S.C et que le lien de retour reste visible.

Un service Render peut avoir besoin d’un démarrage à froid. Si le site M.R.S.C choisit sa copie embarquée après une sonde trop lente, le lien Render reste disponible sur `simulateur.html` ; un tel repli ne prouve pas à lui seul que l’adresse publique a changé.

## Prompt à reprendre dans une session du dépôt du simulateur

```text
Dépôt concerné : thejmimiia-code/D-mocratie-et-politique-du-peuple-pour-le-peuple-par-le-peuple
Adresse publique active à préserver : https://simulateur-macro-politique.onrender.com/
Site M.R.S.C auquel l’outil est relié : https://thejmimiia-code.github.io/MRSC/

Maintiens l’application interactive et son API à la racine de cette adresse Render. Vérifie
que GET / sert le véritable simulateur et que les routes /api/... requises répondent sur la
même origine. Garde l’intégration en iframe possible, sans en-tête ni politique de sécurité
qui la bloque. Conserve un lien de retour M.R.S.C visible, ainsi que l’accessibilité clavier,
les commandes de parcours, l’adaptation mobile et les réglages de lisibilité. Ne présente pas
les résultats du modèle comme des prévisions certaines.

Avant de conclure, teste la page, /api/scenarios, /api/catalogue, une simulation valide sur
/api/simuler et l’intégration depuis simulateur.html du site M.R.S.C. Signale clairement tout
test qui n’a pas pu être réalisé. N’utilise pas l’ancienne adresse Vercel du simulateur.
```
