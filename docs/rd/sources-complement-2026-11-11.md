# Complément du 11 novembre 2026, seconde passe — sources déclarées

**Complément du 11 novembre 2026, seconde passe.** La première passe du 11 novembre 2026 avait laissé 6 adresses sans contenu confrontable : 3 pages d’erreur servies et 3 erreurs de récupération. Sans rien renvoyer à la personne, l’agent a **retenté les 3 erreurs de récupération** et **traité les 3 pages d’erreur servies** en cherchant puis en lisant des pages officielles. Ce complément consigne **16 pages officielles lues**, **1 adresse sans page lue**, **aucune fiche modifiée**, **aucune URL externe nouvelle** et **aucun statut promu**.

Les références sont écrites sans schéma, comme dans `docs/rd/sources-ouvertes-2026-11-11.toml` ; le relevé de la première passe reste dans `docs/rd/sources-ouvertes-2026-11-11.md`, et les adresses exactes dans `docs/apprentissage/catalogue.toml`. Les fiches gardent le statut « Prototype à relire » et les pages de fiches restent `relu-par-agent` dans le manifeste d’empreintes.

## 1. Bilan des six adresses

| Référence sans schéma | Fiches | Nouveau résultat | Pages lues | Repère |
| --- | --- | --- | ---: | --- |
| `extranet.inao.gouv.fr/fichier/Plaquette-SIQO-francais.pdf` | sante-reperer-signes-qualite-origine | remplacement-partiel | 4 | HTTP 500 sur trois tentatives, dont deux tranches avec paramètre de relecture ; aucun PDF lu. Le portail officiel INAO et trois pages de signes ont été lus à la place. |
| `www.education.gouv.fr/media/199172/download` | maths-convertir-unites | remplacement-partiel | 2 | Échec de récupération sur trois tentatives ; la variante éduscol du même identifiant affiche un bandeau cookies puis « Page non trouvée ». La page de ressources d’octobre 2026 et le PDF officiel du programme ont été lus. |
| `www.ign.fr/` | geo-decrire-paysage, geo-lire-legende-carte | aucune-page-lue | 0 | HTTP 403 sur toutes les variantes tentées : racine, deux tranches avec paramètre de relecture, variantes avec et sans www, chemins internes et page de presse. Les résultats de recherche signalent des pages officielles, mais aucune n’a pu être lue. |
| `developer.mozilla.org/fr/docs/Glossary/Byte` | info-bits-octets | contexte-officiel | 3 | La page 404 est celle déjà consignée dans la passe principale ; aucune entrée de glossaire « Byte » lue. Trois pages MDN officielles donnent le repère : chaque octet stocke un nombre de 8 bits, 3 octets de 8 bits font 24 bits, Int8Array et Uint8Array occupent 1 octet. |
| `www.assurance-maladie.ameli.fr/index.php/medecin/exercice-liberal/facturation-remuneration/dispositif-medecin-traitant/dispositif-medecin-traitant` | sante-comprendre-parcours-soins | remplacement-exact | 2 | 404 sur l’ancien domaine ; le même chemin sous www.ameli.fr répond avec le titre déclaré, daté du 21 février 2025. Une page assuré du 23 avril 2026 précise le remboursement à 70 % du tarif de base moins 2 euros dans le parcours et 8,40 euros hors parcours. |
| `www.hceres.fr/fr/ofis` | recherche-conserver-reference | remplacement-exact | 5 | 404 sur l’ancienne adresse ; le plan du site renvoie vers la page courante de l’Ofis. Celle-ci cite l’article L. 211-2 du code de la recherche et la loi de programmation du 24 décembre 2020 ; le dossier de 2017 détaille la triple mission expertise, observation, animation. |

Deux adresses ont une **page officielle de remplacement exacte** lue : l’ancienne page Assurance Maladie existe sous un autre domaine avec le même titre, et l’ancienne adresse Hcéres `/fr/ofis` est remplacée par la page courante de l’Ofis. Deux autres ont des **pages officielles de remplacement lues sans que l’adresse d’origine devienne lisible** : la plaquette INAO et le fichier `media/199172` de l’Éducation nationale. L’entrée MDN « Byte » a des **pages de contexte officiel lues**, mais aucune entrée de glossaire équivalente. **L’accueil IGN reste sans aucune page lue** : toutes les variantes tentées ont répondu HTTP 403.

## 2. Les trois erreurs de récupération, retentées

| Référence sans schéma | Ce qui a été tenté | Ce qui a été lu à la place |
| --- | --- | --- |
| `extranet.inao.gouv.fr/fichier/Plaquette-SIQO-francais.pdf` | Chunk 0 et chunk 1 avec paramètre de relecture, puis chunk 0 sans paramètre : HTTP 500 à chaque fois. | Portail INAO, pages AOP/AOC, Label Rouge et IGP. |
| `www.education.gouv.fr/media/199172/download` | Chunk 0 et chunk 1 avec paramètre de relecture, puis chunk 0 sans paramètre ; la variante `eduscol.education.gouv.fr/media/199172/download` affiche un bandeau cookies puis « Page non trouvée ». | Page Éduscol 5712 et PDF officiel du programme de mathématiques du cycle 3. |
| `www.ign.fr/` | Racine, deux tranches avec paramètre de relecture, variantes avec et sans `www`, chemins internes et page de presse : HTTP 403 partout. | Aucune page. Les résultats de recherche signalent des pages de l’Institut, mais la lecture reste bloquée. |

Un résultat de recherche qui décrit une page ne vaut pas une page lue : seul ce qui est passé par `fetch_page` figure dans le registre `docs/rd/sources-complement-2026-11-11.toml`.

## 3. Les trois pages d’erreur servies, traitées

| Référence sans schéma | Traitement | Ce qui reste écrit |
| --- | --- | --- |
| `developer.mozilla.org/fr/docs/Glossary/Byte` | 404 déjà consignée ; MDN « Endianness », « Base64 » et « TypedArray » lus. | Le titre déclaré « MDN — définition du byte et notions du Web » reste dans `sources_indisponibles` de la fiche `info-bits-octets`. Ces pages donnent un contexte, pas l’entrée de glossaire manquante. |
| `www.assurance-maladie.ameli.fr/index.php/medecin/exercice-liberal/facturation-remuneration/dispositif-medecin-traitant/dispositif-medecin-traitant` | 404 sur l’ancien domaine ; le même chemin sous `www.ameli.fr` répond avec le titre déclaré. | Alias de domaine consigné ; aucune fiche modifiée. |
| `www.hceres.fr/fr/ofis` | 404 ; le plan du site renvoie vers `www.hceres.fr/fr/office-francais-de-lintegrite-scientifique`. | Une piste « Des jalons fondateurs » a aussi répondu 404 et n’est pas comptée comme lecture. |

## 4. Les 16 pages officielles lues

| N | Référence sans schéma | Organisme | Date relevée | Pour | Tranche | Repère lu |
| ---: | --- | --- | --- | --- | --- | --- |
| 1 | `www.inao.gouv.fr/` | INAO | actualités du 12/10/2026 | retentative | 0,1 | Portail des signes officiels : AOP, IGP, STG, agriculture biologique, Label Rouge ; plus de 1200 produits sous SIQO ; recherche par signe et par territoire. |
| 2 | `www.inao.gouv.fr/aop-appellation-origine-protegee` | INAO | page sans date affichée | retentative | 0 | Toutes les étapes de production dans une même aire géographique, savoir-faire reconnu, cahier des charges homologué par l’Union européenne, contrôles par organisme certifié par l’État. |
| 3 | `www.inao.gouv.fr/label-rouge` | INAO | page sans date affichée | retentative | 0 | Signe national désignant un niveau de qualité supérieur ; cahier des charges validé par l’INAO, homologué par arrêté interministériel, contrôles indépendants et analyses sensorielles régulières. |
| 4 | `www.inao.gouv.fr/igp-indication-geographique-protegee` | INAO | page sans date affichée | retentative | 0 | Au moins une étape de production, transformation ou élaboration dans l’aire géographique délimitée ; signe européen, cahier des charges, contrôles rigoureux. |
| 5 | `eduscol.education.gouv.fr/5712/ressources-d-accompagnement-du-programme-de-mathematiques-au-cycle-3` | Éduscol | octobre 2026 | retentative | 0,1 | Programme publié au Bulletin officiel n° 16 du 17 avril 2025, application à tous les niveaux à la rentrée 2026-2027 ; transcription « Regards sur le programme » sur progressivité structurée, erreur comme axe d’apprentissage et adaptation à la diversité des élèves. |
| 6 | `www.education.gouv.fr/sites/default/files/programme-de-math-matiques-pour-le-cycle-3-439827.pdf` | Ministère de l’Éducation nationale | sans date propre ; BO n° 16 du 17 avril 2025 (Éduscol 5712) | retentative | 0,1 | Sommaire par cours moyen première année, cours moyen deuxième année et sixième ; principes, résolution de problèmes, mémorisation et automatismes, place de l’oral, écrits, évaluation, initiation à la pensée algébrique et à la pensée informatique. |
| 7 | `www.ameli.fr/medecin/exercice-liberal/facturation-remuneration/dispositif-medecin-traitant/dispositif-medecin-traitant` | Assurance Maladie | 21 février 2025 | remplacement | 0,1 | Le médecin traitant tient à jour le dossier médical, coordonne le parcours de soins, centralise les avis, oriente vers le médecin correspondant ; refus, changement et libre choix, sans durée imposée ; code MTO sur la feuille de soins électronique. |
| 8 | `www.ameli.fr/assure/remboursements/etre-bien-rembourse/medecin-traitant-parcours-soins-coordonnes` | Assurance Maladie | 23 avril 2026 | remplacement | 0,1 | Consultation à 30 euros : 70 % du tarif moins 2 euros de participation forfaitaire, soit 19 euros remboursés dans le parcours contre 8,40 euros hors parcours ; dossier médical, prévention personnalisée, médecin correspondant et cas de remboursement normal hors parcours. |
| 9 | `www.hceres.fr/fr/office-francais-de-lintegrite-scientifique` | Hcéres | page sans date affichée | remplacement | 0,1 | Intégrité scientifique définie à l’article L. 211-2 du code de la recherche ; missions confiées au Hcéres par la loi de programmation de la recherche du 24 décembre 2020 ; renvoi vers le site de l’Ofis. |
| 10 | `www.hceres.fr/fr/integrite-scientifique` | Hcéres | page sans date affichée | remplacement | 0,1 | Page carrefour du site Hcéres qui renvoie vers la page courante de l’Office français de l’intégrité scientifique. |
| 11 | `www.hceres.fr/fr/dossiers-et-communiques/le-college-du-hceres-valide-la-creation-de-loffice-francais-dintegrite` | Hcéres | communiqué du 20 mars 2017 ; page sans date propre | remplacement | 0 | Le collège du Hcéres valide la création de l’OFIS ; communiqué de presse du 20 mars 2017 joint ; première conférence annuelle des signataires à Paris le 22 mars 2017 ; triple mission expertise, observation, animation ; Conseil de l’intégrité scientifique de 12 experts. |
| 12 | `www.hceres.fr/fr/sitemap` | Hcéres | page sans date affichée | remplacement | 0,1 | Le plan du site nomme la rubrique « Intégrité scientifique » et la page courante « Office Français de l’intégrité scientifique (Ofis) », ce qui remplace l’ancienne adresse /fr/ofis. |
| 13 | `www.ofis-france.fr/` | Ofis | actualités du 8 octobre 2026, 18 septembre 2026, 30 juin 2026 | remplacement | 0 | Annuaire des référents, textes de référence, FAQ ; actualités sur la formation des référents, l’intelligence artificielle pour la recherche et le colloque 2026 ; agendas 2026. |
| 14 | `developer.mozilla.org/en-US/docs/Glossary/Endianness` | MDN Web Docs | dernière modification le 11 juillet 2025 | contexte | 0 | Chaque octet peut stocker un nombre de 8 bits, entre 0x00 et 0xff ; plusieurs octets sont nécessaires pour un nombre plus grand ; little-endian et big-endian. |
| 15 | `developer.mozilla.org/en-US/docs/Glossary/Base64` | MDN Web Docs | page sans date affichée | contexte | 0 | Trois octets de 8 bits font 24 bits, représentés par quatre chiffres Base64 de 6 bits ; le dernier bloc de 2 caractères code 1 octet de 8 bits. |
| 16 | `developer.mozilla.org/fr/docs/Web/JavaScript/Reference/Global_Objects/TypedArray` | MDN Web Docs | disponible depuis juillet 2015 | contexte | 0 | Le tableau des objets TypedArray donne 1 octet pour Int8Array, Uint8Array et Uint8ClampedArray, avec des entiers sur 8 bits ; la fonctionnalité est disponible depuis juillet 2015. |

Les pages Hcéres et Éduscol commencent par un panneau cookies ; le contenu utile a été lu dans la même tranche ou la suivante. Les pages longues n’ont pas été parcourues en entier lorsque l’outil de lecture proposait plusieurs tranches : seules les tranches indiquées sont consignées.

## 5. Ce qui ne change pas

Aucune des 81 fiches du catalogue, aucune des 107 pages générées, aucun statut éditorial, aucune page HTML, CSS ou JavaScript, aucun PDF local, aucune URL du Journal officiel, aucun droit déclaré, aucune date de revue du portefeuille et aucune décision A/B/C. `docs/apprentissage/relectures.toml` reste vide. Les 81 relectures d’agent gardent leurs 40 `a-trancher`, 41 `relue-sans-ecart`, 131 rattachements de sources ouvertes, 20 égalités simples sans écart et leurs `sources_indisponibles` inchangées. La dette initiale des 391 autres unités reste consignée. Le jugement du rendu à l’œil reste à la personne, sans texte à relire de sa part. Aucune publication, aucun poussage, aucune fusion, aucun déploiement et aucune certification.

## 6. Prochaine action prise par l’agent

**Suite du 11 novembre 2026, troisième passe.** Une troisième passe a retenté l’accueil IGN le même jour (encore HTTP 403) et lu 10 pages officielles de l’IGN sur `cartes.gouv.fr` et `data.geopf.fr`, consignées dans `docs/rd/sources-ign-2026-11-11.md` avant toute modification de fiche. Aucune fiche n’a été modifiée et la source-portail reste indisponible.

Sans renvoyer cette tâche à la personne : retenter l’accueil IGN à une date ultérieure, puis consigner toute page de remplacement réellement lue avant de modifier l’une des deux fiches de géographie. Pour la plaquette INAO, le fichier `media/199172` et l’entrée MDN « Byte », ne pas inventer de rattachement : une page de remplacement ne sera ajoutée au catalogue qu’après lecture, datation et confrontation explicites. Les 14 fiches de domaines sensibles gardent leur porte d’expertise compétente.

## 7. Reproduire

```
python3 outils/verifier-sources-ouvertes.py
python3 outils/test_mutations_sources_ouvertes.py
python3 outils/relecture-agent-prototypes.py --verifier
python3 outils/relire-contenus.py
python3 outils/construire-avancees.py --verifier
python3 outils/memoire-eva.py --verifier
git diff --check
```

`outils/verifier-sources-ouvertes.py` garde désormais aussi ce complément ; son banc `outils/test_mutations_sources_ouvertes.py` plante 9 situations dans une copie jetable, portées à 11 par la troisième passe du même jour, dont une lecture de complément retirée et une page d’accueil IGN déclarée résolue.

*Aucune URL externe nouvelle n’est recopiée ici. Les références sans schéma et les titres déclarés suffisent à retrouver les passages ; les adresses exactes restent dans le catalogue.*
