# Sources déclarées : passe du 11 novembre 2026

**Suite de la relecture de contenu par l’agent, sans lecture demandée à la personne.** Le 10 novembre 2026, `docs/rd/relecture-agent-prototypes-2026-11-10.md` consignait 81 prototypes relus et 89 adresses uniques de source encore non ouvertes. Le 11 novembre 2026, ces 89 adresses ont été tentées une à une. Les adresses exactes restent dans `docs/apprentissage/catalogue.toml` ; ce rapport et `docs/rd/sources-ouvertes-2026-11-11.toml` les nomment par une référence sans schéma, pour ne pas recopier une URL externe de plus.

## 1. Ce que la passe ajoute

| Mesure | Valeur | Lecture |
| --- | ---: | --- |
| Adresses uniques du catalogue | 105 | 138 déclarations de source dans les 81 prototypes. |
| Adresses déjà ouvertes le 10 novembre 2026 | 16 | 17 pages de source, dont une source primaire locale de contraste. |
| Adresses tentées le 11 novembre 2026 | 89 | Toutes les adresses encore non ouvertes, sans échantillonnage. |
| Adresses du catalogue désormais tentées | 105 / 105 | 16 + 89 ; cela ne veut pas dire 105 pages de contenu validées. |
| Premières tranches avec contenu confrontable | 83 | Première tranche ; une deuxième tranche a aussi été lue pour la page Éduscol cycle 4. |
| Pages d’erreur servies | 3 | Réponse obtenue, mais corps « page non trouvée » ou 404. |
| Erreurs de récupération | 3 | HTTP 500, HTTP 403 et échec de récupération sans corps lisible. |
| Adresses sans contenu confrontable | 6 | 3 pages d’erreur servies + 3 erreurs de récupération, nommées au §3. |
| Contradictions factuelles corrigées dans les fiches | 0 | Aucune fiche, aucun catalogue, aucun statut, aucun HTML, CSS ou JavaScript modifié. |
| Nouvelles URL externes recopiées | 0 | Aucune URL externe nouvelle ; seules des références sans schéma figurent ici. |

Les 83 pages de contenu ont fourni un repère court, consigné dans le registre ; les 6 adresses sans contenu confrontable restent nommées comme pages d’erreur servies ou erreurs de récupération, sans être présentées comme des sources lues.

Une ouverture de page ne prouve pas la vérité du monde, l’actualité durable d’un chiffre, la titularité des droits, une expertise de domaine ou une validation de personne. Elle permet de confronter un extrait daté au texte d’une fiche.

## 2. Méthode

La liste des 89 adresses a été recalculée depuis `docs/apprentissage/catalogue.toml` et depuis les 21 titres déjà marqués ouverts dans `docs/rd/relecture-agent-prototypes.toml`. Chaque adresse a fait l’objet d’une demande de première tranche. Les PDF ont été lus dans leur première tranche analysable ; les portails qui affichaient d’abord un bandeau cookies ont été notés comme tels. La page Éduscol « Ressources d’accompagnement du programme de technologie au cycle 4 » a aussi été lue en deuxième tranche, parce que sa première tranche ne contenait presque que le bandeau. Aucune page n’a été parcourue en entier lorsque l’outil de lecture en proposait plusieurs tranches.

`outils/verifier-sources-ouvertes.py` confronte le registre des 89 ouvertures au catalogue, au registre des 81 relectures, au rapport, à l’absence d’URL recopiée et au registre humain resté vide. Son banc `outils/test_mutations_sources_ouvertes.py` plante sept situations dans une copie jetable : copie intacte, entrée retirée, statut embelli, source ouverte inventée, compte falsifié, URL recopiée et écriture dans le registre humain.

## 3. Les six adresses sans contenu confrontable

| Référence sans schéma | Fiche | Résultat | Ce qui a été observé |
| --- | --- | --- | --- |
| `developer.mozilla.org/fr/docs/Glossary/Byte` | `info-bits-octets` | page d’erreur servie | « Page non trouvée » ; la variante anglaise du glossaire est également introuvable. Aucune définition du byte n’est validée par cette adresse. |
| `www.assurance-maladie.ameli.fr/index.php/medecin/exercice-liberal/facturation-remuneration/dispositif-medecin-traitant/dispositif-medecin-traitant` | `sante-comprendre-parcours-soins` | page d’erreur servie | Erreur 404 ; aucune présentation du dispositif du médecin traitant lue. Une autre page ameli sur les remboursements en métropole reste ouverte pour la même fiche. |
| `www.hceres.fr/fr/ofis` | `recherche-conserver-reference` | page d’erreur servie | « Oups ! Il n’y a rien ici ! » ; aucune ressource de l’Office français de l’intégrité scientifique lue à cette adresse. |
| `extranet.inao.gouv.fr/fichier/Plaquette-SIQO-francais.pdf` | `sante-reperer-signes-qualite-origine` | échec de récupération | HTTP 500 au premier essai, nouvel échec et deuxième tranche indisponible ; aucun PDF lu. |
| `www.education.gouv.fr/media/199172/download` | `maths-convertir-unites` | échec de récupération | Échec sans corps lisible à la première et à la deuxième tranche ; aucun programme du cycle 3 lu à cette adresse. |
| `www.ign.fr/` | `geo-decrire-paysage`, `geo-lire-legende-carte` | échec de récupération | HTTP 403 à la première et à la deuxième tranche ; aucune page lue. |

Ces six adresses restent **non ouvertes au sens du contenu**, pas « vérifiées » : le registre des 81 relectures porte leurs titres dans `sources_indisponibles`, et `sources_non_ouvertes` compte les déclarations correspondantes. Aucune page de remplacement n’a été inventée.

## 4. Confrontation avec les 81 fiches

- Les 83 premières tranches avec contenu n’ont pas fait apparaître de contradiction factuelle avec les énoncés, aides, corrections, limites et transferts des fiches qui les déclarent. Ce constat porte sur les extraits lus, pas sur la vérité générale des sujets.
- Les titres qui figent « Python 3.15.2 » sont exacts dans les pages de documentation ouvertes le 11 novembre 2026, mais les trois adresses en `docs.python.org/3/` restent des alias mouvants : leur contenu suit la version courante sans que l’adresse change. L’objection du 10 novembre reste écrite.
- Les pages d’accueil et portails désormais ouverts — Banque de France, CNRS, Culture, Cybermalveillance, data.gouv.fr, Éducation nationale, Enseignement supérieur, France services, HAL, INSEE, IPCC, Météo-France, Ministère de la Santé, Santé publique France, Service Public, Vie publique, SPDX et d’autres — donnent un point d’entrée, pas un passage précis pour chaque affirmation. L’objection « source-portail » des 28 fiches reste ouverte ; l’ouverture ne la transforme pas en validation.
- La redirection déjà notée pour `sante-comprendre-depistage-organise`, l’adéquation de la page INRS professionnelle à un circuit simple d’apprentissage et le constat mécanique sur `arts-composer-formes` restent inchangés.
- Les 14 fiches des domaines santé, droit et démarches, argent et politique publique gardent leur porte d’expertise compétente. Aucun avis juridique, aucun essai avec des personnes et aucune promotion de statut ne sont fabriqués par cette passe.
- Les verdicts du 10 novembre restent 40 `a-trancher` et 41 `relue-sans-ecart`. Le second verdict signifie « aucun écart détecté dans le périmètre relu », non « contenu validé ».

## 5. Ce qui change dans les registres

- `docs/rd/sources-ouvertes-2026-11-11.toml` consigne les 89 tentatives, leur référence sans schéma, les titres déclarés, les fiches, le statut, la tranche lue et un repère court.
- `docs/rd/relecture-agent-prototypes.toml` ajoute `passe_sources = 2026-11-11`, rattache les 83 pages de contenu aux fiches par leurs titres déclarés, nomme les adresses sans contenu dans `sources_indisponibles` et recalcule `sources_non_ouvertes`. Les 81 constats, limites et suites portent désormais la trace de cette passe.
- `outils/verifier-sources-ouvertes.py` et son banc de 7 cas gardent ces comptes ; l’inventaire, le journal, la note de méthode, la grille, le plan complet, le rapport du 10 novembre et une 105e avancée sont amendés. Les sorties `docs/rd/avancees.md` et `docs/rd/eva/*` sont régénérées.

## 6. Ce qui ne change pas

Aucune fiche du catalogue, aucune des 107 pages générées, aucun statut éditorial, aucune page publique, aucun CSS, aucun JavaScript, aucun PDF local, aucune URL du Journal officiel, aucun droit déclaré, aucune date de revue du portefeuille et aucune décision A/B/C. Les 81 fiches gardent le statut « Prototype à relire ». `docs/apprentissage/relectures.toml` reste vide : un agent n’y écrit jamais. Les 81 pages de fiches restent `relu-par-agent` dans le manifeste d’empreintes, sans promotion. La dette initiale des 391 autres unités reste consignée. Le jugement du rendu à l’œil reste à la personne, sans texte à relire de sa part. Aucune publication, aucun poussage, aucune fusion, aucun déploiement et aucune certification.

## 7. Action exécutée le 11 novembre 2026, seconde passe, et prochaine action prise par l’agent

**Exécuté le 11 novembre 2026, seconde passe.** Sans renvoyer cette tâche à la personne : les 3 erreurs de récupération ont été retentées à cette date écrite et les 3 pages d’erreur servies ont été traitées par la lecture de pages officielles. **16 pages officielles lues** sont consignées, datées et rattachées dans `docs/rd/sources-complement-2026-11-11.toml` et `docs/rd/sources-complement-2026-11-11.md` **avant toute modification de fiche**. Deux remplacements exacts (Assurance Maladie, Hcéres), deux remplacements partiels (INAO, Éducation nationale), un contexte officiel (MDN) et **1 adresse sans page lue** (IGN, HTTP 403 partout). Aucune adresse de remplacement n’a été ajoutée au catalogue, aucune source-portail n’a été déclarée résolue par simple ouverture d’accueil, aucune fiche ni aucun statut n’a changé. `outils/verifier-sources-ouvertes.py` et son banc porté à 9 cas gardent aussi ce complément.

Une **troisième passe du 11 novembre 2026** a ensuite retenté l’accueil IGN (toujours HTTP 403) et lu 10 pages officielles de l’IGN sur d’autres domaines, consignées dans `docs/rd/sources-ign-2026-11-11.md` et `docs/rd/sources-ign-2026-11-11.toml` avant toute modification de fiche : aucune fiche n’a été modifiée et la source-portail reste indisponible.

**Prochaine action prise par l’agent :** retenter l’accueil IGN à une date ultérieure, puis consigner toute page réellement lue avant de modifier l’une des deux fiches de géographie. Pour la plaquette INAO, le fichier `media/199172` et l’entrée MDN « Byte », ne pas inventer de rattachement : une page de remplacement ne sera ajoutée au catalogue qu’après lecture, datation et confrontation explicites.

## 8. Reproduire

```
python3 outils/relecture-agent-prototypes.py --verifier
python3 outils/verifier-sources-ouvertes.py
python3 outils/test_mutations_sources_ouvertes.py
python3 outils/relire-contenus.py
python3 outils/construire-avancees.py --verifier
python3 outils/memoire-eva.py --verifier
```

## 9. Relevé des 89 tentatives

| N | Référence sans schéma | Fiches | Résultat | Repère lu |
| ---: | --- | --- | --- | --- |
| 1 | `cache.media.eduscol.education.fr/file/HG_Competences/11/4/RA16_C3C4_HIGE_Analyser_comprendre_document_819114.pdf` | histoire-comparer-sources | contenu lu | PDF Éduscol Histoire-géographie : analyser et comprendre un document, contextualisation, point de vue et implicite. |
| 2 | `developer.mozilla.org/en-US/docs/Web/JavaScript/Guide/Loops_and_iteration` | prog-comparer-langages | contenu lu | MDN : boucles for, while, do…while, break et continue. |
| 3 | `developer.mozilla.org/fr/docs/Glossary/Byte` | info-bits-octets | page d’erreur servie | MDN : « Page non trouvée », aucune définition du byte lue ; la variante anglaise du glossaire répond aussi par une page introuvable. |
| 4 | `developer.mozilla.org/fr/docs/Learn_web_development/Extensions/Server-side/First_steps/Client-Server_overview` | info-table-requete-web | contenu lu | MDN : relation client-serveur, HTTP, requête et réponse, GET et POST. |
| 5 | `developer.mozilla.org/fr/docs/Learn_web_development/Howto/Web_mechanics/What_is_a_URL` | info-lire-adresse-web | contenu lu | MDN : schéma, autorité, domaine, port, chemin, paramètres et ancre d’une adresse Web. |
| 6 | `dictionary.cambridge.org/dictionary/english/breath` | langue-anglais-prononcer-th | contenu lu | Cambridge : entrée breath, prononciation /breθ/. |
| 7 | `dictionary.cambridge.org/dictionary/english/breathe` | langue-anglais-prononcer-th | contenu lu | Cambridge : entrée breathe, prononciation /briːð/. |
| 8 | `dictionary.cambridge.org/dictionary/english/mother` | langue-anglais-prononcer-th | contenu lu | Cambridge : entrée mother, prononciation /ˈmʌð.ər/. |
| 9 | `dictionary.cambridge.org/dictionary/english/spell` | langue-anglais-epeler | contenu lu | Cambridge : entrée spell, prononciation /spel/. |
| 10 | `dictionary.cambridge.org/dictionary/english/three` | langue-anglais-prononcer-th | contenu lu | Cambridge : entrée three, prononciation /θriː/. |
| 11 | `dictionary.cambridge.org/help/phonetics.html` | langue-anglais-prononcer-th | contenu lu | Cambridge : symboles phonétiques et phonèmes UK/US. |
| 12 | `doc.hal.science/visualisation-dun-depot/` | recherche-distinguer-resume-citation | contenu lu | HAL : notice, métadonnées, fichier facultatif, accès restreint, littérature citée et GROBID. |
| 13 | `docs.python.org/3/tutorial/controlflow.html` | prog-comparer-langages | contenu lu | Python 3.15.2 : if, for, range, break et continue. |
| 14 | `docs.python.org/3/tutorial/errors.html` | prog-lire-trace-erreur | contenu lu | Python 3.15.2 : erreurs de syntaxe, exceptions, try et except. |
| 15 | `docs.python.org/fr/3/library/unittest.html` | prog-tester-exemples | contenu lu | Documentation Python : unittest, TestCase, assertions, setUp et tearDown. |
| 16 | `eduscol.education.fr/` | histoire-situer-siecle, info-systeme-exploitation, langue-anglais-epeler, maths-equation-simple, maths-lire-echelle-graphique, maths-lire-tableau-croise, maths-reperer-angle-droit, sciences-calculer-vitesse-moyenne, sciences-cycle-vie-plante, sciences-distinguer-melange-changement-etat | contenu lu | Éduscol redirige vers education.gouv.fr : accueil et actualités 2026. |
| 17 | `eduscol.education.fr/document/15199/download` | sciences-distinguer-melange-changement-etat | contenu lu | PDF : matière, 57 g et 62 g, états de la matière et changements d’état. |
| 18 | `eduscol.education.fr/document/16804/download` | geo-decrire-paysage | contenu lu | PDF : récits historiques et géographiques, écrire et pratiquer l’oral. |
| 19 | `eduscol.education.fr/document/16807/download` | geo-lire-legende-carte | contenu lu | PDF : productions graphiques et cartographiques, cartes non neutres. |
| 20 | `eduscol.education.fr/document/16837/download` | sciences-calculer-vitesse-moyenne | contenu lu | PDF : vitesse égale distance divisée par durée. |
| 21 | `eduscol.education.fr/document/23494/download` | info-objet-connecte-local-distant | contenu lu | PDF : programme SNT de seconde, objets connectés et capteurs. |
| 22 | `eduscol.education.fr/document/23560/download` | info-objet-connecte-local-distant | contenu lu | PDF : activité SNT, impact et importance de l’informatisation des objets. |
| 23 | `eduscol.education.fr/document/30046/download` | info-systeme-exploitation | contenu lu | PDF : systèmes UNIX, i-nœuds et processus en NSI première. |
| 24 | `eduscol.education.fr/document/36614/download` | maths-reperer-angle-droit | contenu lu | PDF : angles de 0°, 90°, 180° et 360° au cycle 3. |
| 25 | `eduscol.education.fr/document/58956/download` | maths-lire-tableau-croise | contenu lu | PDF : organiser des données dans un tableau à double entrée. |
| 26 | `eduscol.education.fr/document/58959/download` | maths-lire-echelle-graphique | contenu lu | PDF : résoudre des problèmes en prélevant des informations dans des diagrammes. |
| 27 | `eduscol.education.fr/document/59725/download` | maths-equation-simple | contenu lu | PDF : résolution d’équations du premier degré à une inconnue. |
| 28 | `eduscol.education.gouv.fr/4746/ressources-d-accompagnement-du-programme-de-mathematiques-au-cycle-2` | econ-comparer-prix-unitaires | contenu lu | Éduscol cycle 2 : page de février 2026, programme du BO du 31 octobre 2024, rentrée 2025. |
| 29 | `eduscol.education.gouv.fr/5745/ressources-d-accompagnement-du-programme-de-technologie-au-cycle-4` | tech-circuit-ouvert-ferme, tech-electronique-capteur | contenu lu | Éduscol cycle 4 : première tranche surtout occupée par le bandeau cookies ; deuxième tranche lue, programme du BO n° 9 du 29 février 2024, 5e et 4e applicables, 3e à la rentrée 2026-2027. |
| 30 | `eduscol.education.gouv.fr/sites/default/files/document/ateliercinemaglossaire1277577pdf-81519.pdf` | arts-lire-generique-film | contenu lu | PDF : atelier cinéma, glossaire des métiers et du cadrage. |
| 31 | `eduscol.education.gouv.fr/sites/default/files/document/ra16c3c4mathmathetquotidien600998pdf-77574.pdf` | maths-estimer-calcul | contenu lu | PDF : mathématiques au quotidien, ressources cycles 3 et 4. |
| 32 | `eduscol.education.gouv.fr/sites/default/files/document/ra16c4apevalfiche2708865pdf-78576.pdf` | methode-verbaliser-sa-methode | contenu lu | PDF : évaluation diagnostique, formative, sommative et certificative. |
| 33 | `eduscol.education.gouv.fr/sites/default/files/document/ra20lyceegnsi1-tpourquoi-choisir-nsi1243842pdf-89505.pdf` | info-ordinateur-fonctions | contenu lu | PDF : numérique et sciences informatiques, 25 % de projets en NSI. |
| 34 | `eduscol.education.gouv.fr/sites/default/files/document/ra22c3sciencestechnogriesppreservereaupdf-95295.pdf` | sciences-distinguer-melange-changement-etat | contenu lu | PDF : eau, solubilité, dissolution et séparation. |
| 35 | `eduscol.education.gouv.fr/sites/default/files/document/ra23c2progressionintercyclesvivantpdf-100509.pdf` | sciences-cycle-vie-plante | contenu lu | PDF : monde vivant, progressions intercycles au cycle 2. |
| 36 | `eduscol.education.gouv.fr/sites/default/files/document/vademecum-sciences-numeriques-et-technologie-numerique-et-sciences-informatiques-101937.pdf` | prog-comparer-langages | contenu lu | PDF : vademecum SNT et NSI, août 2023. |
| 37 | `extranet.inao.gouv.fr/fichier/Plaquette-SIQO-francais.pdf` | sante-reperer-signes-qualite-origine | échec de récupération | INAO : HTTP 500 au premier essai, nouvel échec de récupération et deuxième tranche indisponible ; aucun PDF lu. |
| 38 | `fondation-lamap.org/sites/default/files/pdf/La%20re%CC%81cupe%CC%81ration%20en%20me%CC%81moire.pdf` | apprendre-se-tester-plutot-que-relire | contenu lu | PDF La main à la pâte : encodage, stockage, récupération, effet test, quiz plus efficaces que des relectures. |
| 39 | `github.com/python/cpython/blob/v3.14.0/Doc/library/statistics.rst` | maths-moyenne, maths-moyenne-mediane | contenu lu | CPython v3.14.0 statistics.rst : fmean avec pondération optionnelle, module non concurrent de NumPy et SciPy. |
| 40 | `hal.science/` | recherche-distinguer-resume-citation | contenu lu | HAL : archive ouverte, 1 706 363 papers et 4 634 731 références affichés. |
| 41 | `journals.plos.org/ploscompbiol/article?id=10.1371/journal.pcbi.1008032` | recherche-lire-etude | contenu lu | PLOS : Carey, Steiner et Petri 2020, dix règles pour lire un article scientifique, licence CC BY. |
| 42 | `librairie.ademe.fr/index.php?controller=attachment&id_attachment=2645` | sciences-comprendre-isolation-r-et-u | contenu lu | ADEME : exigences réglementaires pour les travaux de rénovation, juillet 2023, R minimal par paroi et zones H1 à H3, arrêté du 3 mai 2007 modifié le 22 mars 2017. |
| 43 | `messervices.cyber.gouv.fr/documents-guides/anssi-guide-securite_des_systemes_objets_connectes_iot-v1.0.pdf` | info-objet-connecte-local-distant | contenu lu | ANSSI-PA-087 du 27 août 2021 : recommandations non normatives, analyse de risques, clés, mises à jour et journalisation. |
| 44 | `meteofrance.com/` | sciences-meteo-climat | contenu lu | Météo-France : accueil, bulletin du 10 novembre 2026, « pluvieux mais doux », actualités du 5 au 10 novembre. |
| 45 | `meteofrance.com/meteo-a-z/les-precipitations-pluie-neige-grele` | sciences-comprendre-pluie-millimetres | contenu lu | Météo-France : pluie, neige et grêle ; 1 mm égale 1 L/m² ; radars. |
| 46 | `opensource.org/osd` | prog-lire-licence-logiciel | contenu lu | Open Source Initiative : définition en dix critères, version 1.9 du 22 mars 2007. |
| 47 | `promenade.imcce.fr/fr/pages2/277.html` | histoire-situer-siecle | contenu lu | IMCCE : chronologie, ères, calendriers julien et grégorien, année 0 astronomique. |
| 48 | `rm.coe.int/chapter-5-communicative-language-competences/1680a084c3` | langue-anglais-prononcer-th | contenu lu | CECR chapitre 5 : Phonological control et grilles A1 à C2. |
| 49 | `sante.gouv.fr/` | sante-reperer-source-publique | contenu lu | Ministère de la Santé : accueil, panneau cookies et actualités 2026. |
| 50 | `signal.conso.gouv.fr/fr` | econ-lire-mention-garantie | contenu lu | SignalConso : quatre étapes, catégories de signalement et rattachement à la DGCCRF. |
| 51 | `spdx.org/licenses/` | prog-lire-licence-logiciel | contenu lu | SPDX License List : identifiants courts, noms complets, texte, URL canonique et version 3.29.0 du 16 septembre 2026. |
| 52 | `transport.data.gouv.fr/datasets/reseau-urbain-et-interurbain-dile-de-france-mobilites` | geographie-preparer-trajet-horaires | contenu lu | transport.data.gouv.fr : GTFS et NeTEx, 75 opérateurs, trois mises à jour par jour, API SIRI Lite et quotas. |
| 53 | `www.archives-nationales.culture.gouv.fr/` | histoire-comparer-sources | contenu lu | Archives nationales : accueil, visiter, rechercher, explorer, 31 300 inventaires et plus de 14 millions d’images en ligne. |
| 54 | `www.archives-nationales.culture.gouv.fr/methodologie-de-recherche-en-salle-de-lecture-virtuelle` | histoire-lire-une-cote | contenu lu | Archives nationales : cote comme identifiant unique, fonds avant et depuis 1789, salle de lecture virtuelle. |
| 55 | `www.assurance-maladie.ameli.fr/index.php/medecin/exercice-liberal/facturation-remuneration/dispositif-medecin-traitant/dispositif-medecin-traitant` | sante-comprendre-parcours-soins | page d’erreur servie | Assurance Maladie : « Page non trouvée », erreur 404 ; aucune présentation du dispositif du médecin traitant lue. |
| 56 | `www.banque-france.fr/` | econ-distinguer-interet-frais | contenu lu | Banque de France : accueil, enquête mensuelle de conjoncture du 9 novembre 2026 et services aux particuliers. |
| 57 | `www.bipm.org/en/measurement-units` | maths-convertir-unites | contenu lu | BIPM : sept unités de base, sept constantes de définition et SI défini par ces constantes depuis le 20 mai 2019. |
| 58 | `www.britannica.com/dictionary/eb/qa/Pronunciation-of-ed-Endings-on-Verbs` | langue-anglais-prononcer-ed | contenu lu | Britannica : -ed se prononce /ɪd/, /d/ ou /t/ selon le dernier son et son voisement. |
| 59 | `www.certificat-clea.fr/employeurs/le-socle/` | methodes-demander-clarification | contenu lu | CléA : sept domaines et 106 critères d’évaluation. |
| 60 | `www.cnrs.fr/fr` | recherche-question-hypothese | contenu lu | CNRS : accueil, actualités du 10 novembre 2026, dossiers climat et transports. |
| 61 | `www.coe.int/en/web/common-european-framework-reference-languages/phonological-competence` | langue-anglais-prononcer-ed | contenu lu | CECR : compétence phonologique, trois sous-échelles, intelligibilité plutôt que modèle du locuteur natif. |
| 62 | `www.coe.int/fr/web/common-european-framework-reference-languages/plurilingualism-in-the-classroom` | langue-reperer-mot-deja-connu | contenu lu | CECR : plurilinguisme, répertoires linguistiques et culturels, approches plurilingues. |
| 63 | `www.commission-des-sondages.fr/oblig/obligations.htm` | civ-lire-un-sondage | contenu lu | Commission des sondages : article 2, huit mentions obligatoires ; article 11, interdiction en période électorale. |
| 64 | `www.culture.gouv.fr/` | arts-lire-cartel, langue-reperer-mot-deja-connu | contenu lu | Ministère de la Culture : accueil, actualités du 10 novembre 2026 et dossiers thématiques. |
| 65 | `www.culture.gouv.fr/thematiques/photographie/gerer-un-fonds-photographique/rediger-des-cartels` | arts-lire-cartel | contenu lu | Ministère de la Culture : cartel simple, auteur, titre, technique ou matériaux, date et lieu de conservation. |
| 66 | `www.cybermalveillance.gouv.fr/` | numerique-organiser-fichiers | contenu lu | Cybermalveillance.gouv.fr : accueil, 17Cyber, prévention, fiches réflexes et panneau cookies. |
| 67 | `www.cybermalveillance.gouv.fr/tous-nos-contenus/fiches-reflexes/hameconnage-phishing` | civ-trouver-service-public | contenu lu | Cybermalveillance : hameçonnage, SMS ou courriel frauduleux, opposition, plainte et signalement. |
| 68 | `www.cybermalveillance.gouv.fr/tous-nos-contenus/fiches-reflexes/rancongiciel-ransomware-particuliers` | numerique-preparer-sauvegarde | contenu lu | Cybermalveillance : rançongiciel pour particuliers, blocage des fichiers et demande de paiement. |
| 69 | `www.cybermalveillance.gouv.fr/tous-nos-contenus/fiches-reflexes/rancongiciels-ransomwares` | numerique-preparer-sauvegarde | contenu lu | Cybermalveillance : rançongiciel pour organisations, définition, prévention, conduite à tenir et droit. |
| 70 | `www.data.gouv.fr/` | civ-choisir-source-publique, info-table-requete-web | contenu lu | data.gouv.fr : 77K jeux de données et API, 397K fichiers, 7K organisations et plateformes thématiques. |
| 71 | `www.data.gouv.fr/pages/legal/licences` | civ-choisir-source-publique | contenu lu | data.gouv.fr : licences de réutilisation, Licence Ouverte 2.0, ODbL, identifiants SPDX et licences homologuées. |
| 72 | `www.education.gouv.fr/` | arts-composer-formes, histoire-reperer-echelle-france-monde, langue-reperer-mot-deja-connu | contenu lu | Éducation nationale : accueil, panneau cookies, journée nationale de lutte contre le harcèlement. |
| 73 | `www.education.gouv.fr/media/199172/download` | maths-convertir-unites | échec de récupération | Éducation nationale media/199172 : échec de récupération à la première et à la deuxième tranche ; aucun PDF lu. |
| 74 | `www.education.gouv.fr/programmes-et-horaires-l-ecole-elementaire-9011` | histoire-lire-frise, langue-anglais-demander-aide | contenu lu | Éducation nationale : 24 heures sur neuf demi-journées, cinq niveaux, 36 semaines et programmes révisés en septembre 2026. |
| 75 | `www.education.gouv.fr/sites/default/files/document/Annexe%202%20%E2%80%93%20Programme%20de%20math%C3%A9matiques%20pour%20le%20cycle%204-480716.pdf` | maths-moyenne, maths-probabilite-tirage | contenu lu | Programme de mathématiques du cycle 4 : résolution de problèmes, définition, propriété, conjecture et énoncé prouvé. |
| 76 | `www.enseignementsup-recherche.gouv.fr/` | recherche-distinguer-resume-citation | contenu lu | Enseignement supérieur : accueil, prix science ouverte 2026 et bulletin officiel n° 42 du 5 novembre 2026. |
| 77 | `www.france-services.gouv.fr/` | civ-trouver-service-public | contenu lu | France services : 2 800 maisons, 144 bus, accompagnement gratuit et sans rendez-vous. |
| 78 | `www.hceres.fr/fr/ofis` | recherche-conserver-reference | page d’erreur servie | Hcéres /fr/ofis : « Oups ! Il n’y a rien ici ! », page 404 ; aucune ressource OFIS lue. |
| 79 | `www.ign.fr/` | geo-decrire-paysage, geo-lire-legende-carte | échec de récupération | IGN : HTTP 403 à la première et à la deuxième tranche ; aucune page lue. |
| 80 | `www.inrs.fr/dam/inrs/CataloguePapier/ED/TI-ED-6197.pdf` | sante-lire-etiquette-produit-menager | contenu lu | INRS ED 6197 : étiquetage des produits chimiques, règlement CLP, symboles, reconditionnement et obligations. |
| 81 | `www.insee.fr/` | civ-choisir-source-publique | contenu lu | INSEE : population 69,08 millions au 1er janvier 2026, chômage 8,2 % au troisième trimestre 2026, publications du 10 novembre. |
| 82 | `www.ipcc.ch/` | sciences-meteo-climat | contenu lu | IPCC : évalue l’état des connaissances, ne mène pas ses propres recherches, rapports utiles aux politiques sans les prescrire, 195 États membres. |
| 83 | `www.santepubliquefrance.fr/` | sante-reperer-source-publique | contenu lu | Santé publique France : accueil, Rencontres 2026 et bulletins du 4 novembre 2026 sur les infections respiratoires aiguës. |
| 84 | `www.santepubliquefrance.fr/a-propos/sante-publique-france-qui-sommes-nous` | sante-reperer-source-publique | contenu lu | Santé publique France : agence créée en 2016, missions anticiper, comprendre et agir, page mise à jour le 16 juillet 2025. |
| 85 | `www.service-public.fr/particuliers/vosdroits/F31144` | demarche-lire-devis-travaux | contenu lu | Service Public F31144 : devis obligatoire, liste des travaux, mentions du devis, page vérifiée le 9 septembre 2022 ; la variante .fr redirige vers .gouv.fr. |
| 86 | `www.service-public.gouv.fr/particuliers/vosdroits/F2451` | econ-distinguer-interet-frais | contenu lu | Service Public F2451 : crédit à la consommation de 200 € à 75 000 €, contrat écrit, publicité encadrée, page vérifiée le 7 août 2024. |
| 87 | `www.vie-publique.fr/` | civ-choisir-source-publique | contenu lu | Vie publique : accueil, questions-réponses, actualités du 10 novembre 2026 et panorama des lois. |
| 88 | `www.vie-publique.fr/fiches` | civ-reperer-echelle-institution, civ-reperer-info-electorale, histoire-reperer-echelle-france-monde | contenu lu | Vie publique : fiches par thèmes, institutions, citoyenneté, collectivités, justice et Union européenne. |
| 89 | `www.visionscarto.net/peut-on-corriger-la-carte-du-monde` | geo-choisir-une-projection | contenu lu | Visionscarto : Mercator, résolution de l’ONU du 4 septembre 2026, Equal Earth, déformations, centrage et orientation. |

*Aucune URL externe nouvelle n’est recopiée ici. Les adresses exactes, leurs titres, leurs droits déclarés et leurs dates de contrôle restent dans `docs/apprentissage/catalogue.toml`.*
