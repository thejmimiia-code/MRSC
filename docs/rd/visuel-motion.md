# R&D — direction artistique, rendu visuel et animation web du site M.R.S.C.

**Recherche documentaire consultée le 13 octobre 2026.** Cette note propose une méthode et une courte sélection de skills Claude/Claude Code pour explorer une identité graphique plus ludique et distinctive et des animations utiles au site. Elle ne fige pas une direction visuelle, ne décrit pas un prototype livré et ne prouve pas d’amélioration de l’apprentissage.

## 1. Besoin, signal et limites de preuve

**Signal reçu :** rendre le site plus ludique, attirant et reconnaissable, avec une sensation de découverte lors des visites répétées, pour favoriser l’apprentissage et la formation.

**Ce qui est observé dans le dépôt :** le site est réalisé principalement en HTML/CSS/JavaScript ; ses pages d’apprentissage sont générées depuis le catalogue et les styles communs sont dans `assets/css/site.css`. Les règles d’adaptation et de mouvement réduit, les couleurs et l’identité éditoriale sont documentées dans [`rd-affichage-adaptatif.md`](../rd-affichage-adaptatif.md) et [`rd-coherence-visuelle-editoriale.md`](../rd-coherence-visuelle-editoriale.md). Une planche locale [`pistes-visuelles-ia.html`](../pistes-visuelles-ia.html) présente déjà trois pistes pour la page IA ; elles sont exploratoires, thématiques et non validées comme identité générale.

**Hypothèses à tester, pas résultats établis :** une signature graphique liée aux contenus réels du M.R.S.C., des liens visibles entre domaines et une découverte éditoriale facultative pourraient rendre l’exploration plus plaisante et aider à trouver une prochaine ressource. Aucun essai utilisateur ou résultat pédagogique ne prouve encore ces effets. « Original pour le M.R.S.C. » est un objectif de conception ; l’absence de tout équivalent ailleurs n’est pas vérifiable et ne sera pas promise.

**Décision de départ :** conserver la pile HTML/CSS/JavaScript du site et ne retenir que des ressources pertinentes, licenciées et auditables. Deux skills complémentaires ont été importés comme références Markdown depuis des commits épinglés, avec licences, provenance et empreintes ; aucun paquet ou code d’exécution n’a été ajouté. Les autres candidats restent écartés ou en attente de vérification. Commencer par trois directions concurrentes et un prototype autonome, réversible, limité à une surface à choisir ; préserver toutes les pages, ressources et fonctions.

## 2. Skills et ressources évalués

| Ressource | Apport le plus pertinent | Licence / format vérifié à la source | Recommandation pour le M.R.S.C. |
|---|---|---|---|
| [`anthropics/skills` — `frontend-design`](https://github.com/anthropics/skills/tree/dbd4588f9e1033efb41dad4bef2f7947c8993d44/skills/frontend-design) | Direction visuelle fondée sur le sujet réel, choix intentionnels de typographie/mise en page, propositions divergentes, critique contre les défauts génériques, captures et qualité responsive. Le skill limite aussi les animations non sollicitées. | Licence propre au skill : Apache 2.0. Snapshot Git épinglé `dbd4588f9e1033efb41dad4bef2f7947c8993d44` (9 octobre 2026). Format Markdown. | **Importé** sous `.claude/skills/frontend-design/` avec `LICENSE.txt`, `SOURCE.md` et `SHA256SUMS`. Utiliser sa démarche, puis vérifier les choix au regard de l’identité du M.R.S.C. et de ses pages existantes. |
| [`LottieFiles/motion-design-skill`](https://github.com/LottieFiles/motion-design-skill/tree/f9a8a041b85185ee4881b3471d3415e939aac772/skills/motion-design) | Intention émotionnelle, timing, easing, chorégraphie, micro-interactions et langage de mouvement ; annoncé comme indépendant de CSS, GSAP, Lottie et autres outils. Sa note d’adaptation traite du mouvement réduit, des alternatives, de l’accessibilité et de la performance. | Licence MIT. Snapshot Git épinglé `f9a8a041b85185ee4881b3471d3415e939aac772` (18 mai 2026). Format Markdown. | **Importé** sous `.claude/skills/motion-design/` : `SKILL.md` est une entrée locale avec garde-fous ; le skill amont non modifié est conservé sous `UPSTREAM-SKILL.md`, avec `LICENSE`, `SOURCE.md` et `SHA256SUMS`. Utiliser le contenu amont comme boîte à idées, pas comme norme : ses prescriptions comme « toujours trois couches de mouvement » ou l’ajout de mouvement ambiant peuvent être trop chargées pour ce site. |
| [`anthropics/skills` — `algorithmic-art`](https://github.com/anthropics/skills/blob/main/skills/algorithmic-art/SKILL.md) | Création d’une esthétique générative et d’esquisses codées, notamment avec p5.js. | Licence Apache 2.0. Le skill examiné demande notamment p5.js depuis un CDN et un viewer portant la marque Anthropic. | **Écarté tel quel** : marque tierce et chargement de code distant incompatibles avec l’identité et la sobriété du M.R.S.C. Des formes génératives peuvent rester une piste de recherche indépendante, sans reprendre son viewer ni ajouter p5.js au site. |
| [`vercel-labs/agent-skills` — `web-design-guidelines`](https://github.com/vercel-labs/agent-skills/tree/main/skills/web-design-guidelines) et le dépôt séparé [`web-interface-guidelines`](https://github.com/vercel-labs/web-interface-guidelines) | Revue de conformité aux règles d’interface : clavier, focus, cibles, zoom, interactions et comportements Web. Le skill récupère le corpus de règles à jour pour chaque revue ; il n’est pas une méthode de direction créative. | Le dépôt de règles `web-interface-guidelines` déclare MIT. Le dépôt `agent-skills` consulté ne présentait pas de licence à sa racine ; le wrapper exact n’est donc pas copié ni redistribué ici. | **Audit facultatif après la conception**, en complément des contrôles du dépôt. Conserver un lien vers les règles et leur date de consultation ; ne pas traiter une liste de bonnes pratiques comme une validation WCAG complète. |
| [`anthropics/skills` — `webapp-testing`](https://github.com/anthropics/skills/tree/main/skills/webapp-testing) | Parcours locaux, captures, inspection du DOM et journaux de navigateur au moyen de Playwright, y compris pour du HTML statique. | Licence Apache 2.0 dans le dossier du skill ; procédure fondée sur Python Playwright. | **Complément de test, pas de design.** À envisager seulement si une suite de captures automatisées est utile ; ne pas installer une dépendance maintenant, le présent travail étant documentaire. |

### Candidats écartés ou différés

Cette sélection n’est pas un inventaire exhaustif de tout Internet : le nombre de skills publics est ouvert. Elle couvre les ressources officielles Anthropic pertinentes et des candidats communautaires repérés pendant la recherche ; seuls les deux imports ci-dessus sont jugés prêts à être gardés localement.

- Anthropic [`canvas-design`](https://github.com/anthropics/skills/tree/main/skills/canvas-design) vise surtout les PDF/PNG statiques et recommande de télécharger des polices : hors du besoin d’interface web, avec gestion de licence supplémentaire.
- Anthropic [`brand-guidelines`](https://github.com/anthropics/skills/tree/main/skills/brand-guidelines) impose l’identité de marque Anthropic ; [`theme-factory`](https://github.com/anthropics/skills/tree/main/skills/theme-factory) est centré sur les thèmes de présentations ; [`web-artifacts-builder`](https://github.com/anthropics/skills/tree/main/skills/web-artifacts-builder) cible une pile React/TypeScript/Tailwind/Parcel et des scripts de construction. Ces compétences ne sont pas adaptées telles quelles à la pile et à la marque M.R.S.C.
- [`ui-ux-pro-max-skill`](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill) a une licence MIT, mais embarque un vaste corpus de styles et lance un utilitaire Python de recherche. C’est plus lourd que nécessaire pour cette R&D ciblée ; le code de l’utilitaire n’a pas fait l’objet d’un audit complet et rien n’en a été importé.
- [`design-motion-principles`](https://github.com/kylezantos/design-motion-principles) déclare MIT et propose des audits HTML avec démonstrations en boucle. C’est redondant avec le complément motion retenu et son mode de démonstration peut introduire des boucles décoratives ; non importé.
- [`motion-ref-skill`](https://github.com/joepUI/motion-ref-skill) déclare MIT, mais le fichier principal du skill n’a pas pu être récupéré depuis GitHub pendant l’audit (« Unicorn »). Licence seule insuffisante pour valider son contenu : non importé.
- [`delphi-ai/animate-skill`](https://github.com/delphi-ai/animate-skill) cible Next.js/React, Framer Motion et `.tsx` ; aucune licence claire n’a été trouvée à la racine consultée. Non retenu pour cette pile.
- [`css-animation-skill`](https://github.com/neonwatty/css-animation-skill) dépend de Claude-in-Chrome MCP et oriente vers des démonstrations autonomes, non vers une intégration directe au site ; non importé.
- [`iart-ai/web-animation-skills`](https://github.com/iart-ai/web-animation-skills) regroupe plusieurs spécialisations et exemples/outils orientés GSAP, Next.js et autres piles. Le lot dépasse le besoin ; ne pas importer le bundle sans audit individuel de chaque sous-skill, script et licence.

Le dépôt conserve donc un petit choix ciblé, pas une collection de tous les dépôts découverts. Réévaluer un candidat seulement si un besoin concret le justifie et après lecture de son contenu, de ses scripts, de ses licences et de ses dépendances.

La documentation Claude Code indique qu’un skill propre au projet peut être placé dans `.claude/skills/<nom>/SKILL.md`, avec une description YAML et un corps Markdown chargé à la demande ([documentation Claude Code — Skills](https://code.claude.com/docs/en/slash-commands)). Le dépôt contient un point d’entrée et une carte méthodologique écrits pour le M.R.S.C. : [`direction-artistique-motion`](../../.claude/skills/direction-artistique-motion/SKILL.md) et [sa carte interne](../../.agents/skills/direction-artistique-motion/SKILL.md). Les deux skills amont retenus sont vendoriés séparément avec leur licence, source épinglée et empreintes : [`frontend-design`](../../.claude/skills/frontend-design/) et [`motion-design`](../../.claude/skills/motion-design/). La carte locale et `AGENTS.md` restent prioritaires.

**Contrôle de l’import :** les deux snapshots amont et leurs références ont été relus ; l’entrée motion locale a été ajoutée pour empêcher l’application automatique des recettes à risque de surcharge. Les fichiers importés sont du Markdown et des licences texte, accompagnés de manifests ; aucun script, binaire, installateur, dépendance, police ou média n’a été importé ou exécuté. Les manifests `SHA256SUMS` ont été générés puis validés avec `sha256sum -c`. Une recherche statique de motifs de commande/réseau n’a pas trouvé d’instruction d’installation ou d’appel distant dans les skills ; elle a seulement rencontré des faux positifs liés aux « design tokens », aux captures d’écran et aux URL de provenance. Ce contrôle réduit le risque, sans certifier l’absence de toute consigne malveillante.

## 3. Directions à prototyper — aucune n’est choisie

Ces axes sont des hypothèses de travail, à différencier visuellement et à confronter aux besoins éditoriaux. La planche IA existante reste une référence locale utile mais ne remplace pas cette divergence à l’échelle du site.

1. **L’atelier des savoirs** — compositions éditoriales qui évoquent le fait de relier, fabriquer et transmettre des idées ; tracés, repères et fragments graphiques originaux, avec une hiérarchie de lecture nette. À vérifier : éviter le décor de « bureau » générique et ne pas faire passer une illustration pour une contribution réelle.
2. **La carte des liens** — relations facultatives entre notions, fiches et domaines, présentées comme des pistes de navigation plutôt qu’un classement total des savoirs. Chaque lien doit avoir un libellé texte, une destination intelligible et un équivalent sans mouvement. À vérifier : lisibilité des liens, absence de surcharge et exactitude des relations.
3. **Le carnet de découvertes** — une ressource ou question courte mise en avant, avec une commande explicite « Une autre piste » et une composition renouvelée. À vérifier : le contrôle reste facultatif, tout le catalogue demeure accessible, la variation n’altère ni le sens ni les liens et ne crée pas de progression punitive.

Une planche de comparaison pourra montrer la palette, la typographie, la mise en page, les illustrations et une seule micro-interaction représentative par option. La signature peut être une composition, un motif éditorial, une illustration ou un rythme cohérent : elle n’a pas besoin d’être une animation permanente.

## 4. Mouvement et accessibilité : règles de travail

Pour chaque effet candidat, consigner son intention, son déclencheur, le changement compris, le réglage temporel à essayer, l’équivalent immobile, le comportement sous mouvement réduit, les entrées clavier/tactile et son coût. Les valeurs de durée/easing des skills sont des points de départ à vérifier, pas des seuils universels.

- Préférer les mouvements initiés par la personne ou utiles à comprendre un changement d’état ; limiter les animations de chargement et d’arrivée non demandées.
- Suivre `prefers-reduced-motion` et conserver une version statique qui exprime toutes les mêmes informations. Ne pas faire dépendre la navigation, la correction ou une consigne d’un mouvement.
- Éviter les boucles décoratives, les révélations répétées, le défilement forcé, le parallaxe et les transitions couvrant l’écran. Une animation continue éventuelle doit avoir un contrôle d’arrêt et une justification précise.
- Garder un focus visible, une navigation clavier complète et des libellés explicites. Une commande ne doit pas être activable au survol seulement ; préserver le zoom natif et viser des cibles tactiles de 44 px.
- Privilégier les styles CSS et transformations simples. Réexaminer la performance sur téléphone et faible puissance ; ne pas supposer qu’un effet est gratuit parce qu’il est court ou en GPU.
- Pour le contenu renouvelé, proposer le contrôle et le prochain choix sans déplacer le focus, cacher des pages, compter les visites ou mémoriser un profil. Aucune requête de télémétrie ni donnée personnelle n’est nécessaire à ce prototype.

Les références d’accessibilité déjà intégrées au projet sont réunies dans [`rd-affichage-adaptatif.md`](../rd-affichage-adaptatif.md), dont les références WCAG 2.2 et W3C COGA. Les règles de ce document ne déclarent pas une conformité globale.

## 5. Plan d’essai et critères de décision

### Étape A — divergence hors production

- Faire un inventaire ciblé de l’accueil, du catalogue, d’une fiche, d’une page d’information et des composants partagés ; noter les formes et animations déjà présentes avant de les toucher.
- Réaliser trois planches ou maquettes statiques, sans recopier un site existant ; demander au M.R.S.C. de choisir ou combiner un axe avant une refonte plus large.
- Choisir ensuite une page pilote où l’objectif d’apprentissage et les critères de réussite sont explicités. Ne pas refaire toutes les pages en une seule passe.

### Étape B — prototype réversible

- Garder le contenu, les parcours, les générateurs et le repli sans script. Encapsuler les règles du prototype et éviter les modifications de cascade globales jusqu’à ce que leur portée soit démontrée.
- Comparer une version stable et une version avec, au plus, une expérience de découverte facultative ; conserver les voies d’accès existantes.
- Envisager un ensemble de ressources curées choisi en mémoire pendant la page ou la visite, avec une commande « Une autre piste ». Ce n’est qu’une hypothèse : mesurer aussi la clarté, le sentiment de contrôle et le risque de confusion avant d’en faire un comportement commun.

### Étape C — vérifications et essais

- Contrôles techniques automatisés adaptés : intégrité des liens, générations, responsive, clavier, focus, contraste, mouvement réduit et erreurs console/captures lorsque l’outil est disponible.
- Revue visuelle humaine à plusieurs largeurs et états, dont zoom, petit écran, préférence de réduction du mouvement et affichage sans JavaScript.
- Si utile, essais volontaires prévus par [`protocole-essais-usage.md`](protocole-essais-usage.md), après les relectures requises : demander à une personne de trouver une ressource, de comprendre ce qu’une animation indique et de choisir une seconde piste. Consentement, droit d’arrêter, notes minimales et aucune identité/réponse personnelle.
- Comparer la réussite de tâche, la compréhension, la lisibilité et le ressenti déclaré ; ne pas prendre le temps passé, la fréquence de retour ou les clics pour preuves d’apprentissage. N’ajouter aucune analytique individuelle pour répondre à cette question.

**Critères de sortie de R&D :** plusieurs directions réellement distinctes ; une sélection tracée ; un prototype limité ; les parcours et contenus restent atteignables ; les états statiques et mouvement réduit sont compréhensibles ; sources/licences des références consignées ; tests automatisés distingués des revues humaines et des essais avec volontaires ; décision d’itérer, de garder ou de retirer argumentée.

## 6. État, changements et prochaine action

- **État :** recherche documentaire terminée pour cette étape ; l’initiative demeure en cours. Les options visuelles ne sont pas encore prototypées ou choisies.
- **Changements de cette étape :** deux skills amont ciblés, leurs licences et manifests d’intégrité ont été importés dans `.claude/skills/` depuis des commits épinglés ; provenance, exclusions, méthode locale, shortlist et plan d’essai sont documentés ; initiative et journal actualisés.
- **Non réalisé :** aucun installateur ou code externe n’a été exécuté, aucune dépendance, police ou média n’a été ajoutée, aucun code public, style de production ou prototype d’animation n’a été modifié ; aucune capture, inspection visuelle humaine, analyse WCAG complète ou session utilisateur n’a été réalisée dans cette étape.
- **Prochaine action :** préparer les trois maquettes comparatives non publiées, puis demander au M.R.S.C. de sélectionner une direction et une page pilote avant toute intégration au site.

## 7. Sources primaires consultées le 13 octobre 2026

- Anthropic, snapshot [`frontend-design/SKILL.md`](https://github.com/anthropics/skills/blob/dbd4588f9e1033efb41dad4bef2f7947c8993d44/skills/frontend-design/SKILL.md), [licence Apache 2.0](https://github.com/anthropics/skills/blob/dbd4588f9e1033efb41dad4bef2f7947c8993d44/skills/frontend-design/LICENSE.txt) et [copie locale avec provenance et sommes](../../.claude/skills/frontend-design/).
- LottieFiles, snapshot [`SKILL.md`](https://github.com/LottieFiles/motion-design-skill/blob/f9a8a041b85185ee4881b3471d3415e939aac772/skills/motion-design/SKILL.md), [adaptation contexte/accessibilité/performance](https://github.com/LottieFiles/motion-design-skill/blob/f9a8a041b85185ee4881b3471d3415e939aac772/skills/motion-design/director/context-adaptation.md), [licence MIT](https://github.com/LottieFiles/motion-design-skill/blob/f9a8a041b85185ee4881b3471d3415e939aac772/LICENSE) et [copie locale avec provenance et sommes](../../.claude/skills/motion-design/).
- Anthropic, [`algorithmic-art/SKILL.md`](https://github.com/anthropics/skills/blob/main/skills/algorithmic-art/SKILL.md) et [licence du skill](https://github.com/anthropics/skills/blob/main/skills/algorithmic-art/LICENSE.txt).
- Vercel Labs, [skill `web-design-guidelines`](https://github.com/vercel-labs/agent-skills/blob/main/skills/web-design-guidelines/SKILL.md), [règles d’interface](https://github.com/vercel-labs/web-interface-guidelines) et [licence MIT de ce dépôt de règles](https://github.com/vercel-labs/web-interface-guidelines/blob/main/LICENSE).
- Anthropic, [skill `webapp-testing`](https://github.com/anthropics/skills/blob/main/skills/webapp-testing/SKILL.md) et [licence Apache 2.0 du skill](https://github.com/anthropics/skills/blob/main/skills/webapp-testing/LICENSE.txt).
- Delphi AI, [README et périmètre de `animate-skill`](https://github.com/delphi-ai/animate-skill) et [`SKILL.md`](https://github.com/delphi-ai/animate-skill/blob/main/SKILL.md).
- Anthropic, [documentation Claude Code — création, découverte et emplacement des skills projet](https://code.claude.com/docs/en/slash-commands).
