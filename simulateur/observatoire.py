"""Repères statistiques publics pour les vues territoriales et ménages.

Les observations sont embarquées comme références datées, jamais comme
trajectoires futures. Les profils de foyer, eux, sont calculés exclusivement
côté navigateur et ne sont pas transmis par l'API.
"""

from __future__ import annotations

from copy import deepcopy
from typing import Any

DATE_COLLECTE = "2026-10-07"

_URL_OFGL = (
    "https://www.collectivites-locales.gouv.fr/files/files/Etudes-et-statistiques/"
    "OFGL/2026/Rapport%20OFGL%202026%20complet%20V24ao%C3%BBt2026.pdf"
)
_PAGE_OFGL = (
    "https://www.collectivites-locales.gouv.fr/etudes-et-statistiques/"
    "rapports-de-lobservatoire-des-finances-et-de-la-gestion-publique-locales-ofgl"
)
_URL_INSEE_CONSO = "https://www.insee.fr/fr/statistiques/2830276"
_URL_INSEE_RDB = "https://www.insee.fr/fr/statistiques/9006503?sommaire=8071406"
_URL_INSEE_LOGEMENT = "https://www.insee.fr/fr/statistiques/9053584"
_URL_EUROSTAT_FLASH = "https://ec.europa.eu/eurostat/web/products-euro-indicators/w/2-02102026-ap"
_URL_CNAF = (
    "https://www.caf.fr/sites/default/files/medias/cnaf/Professionnels/Nous_connaitre/"
    "textes_de_reference/Rapport%20d'activit%C3%A9/"
    "260081_Rapport%20d'activit%C3%A9%20de%20la%20branche%20Famille%202025_v5_B.pdf"
)
_URL_DREES = "https://drees.solidarites-sante.gouv.fr/sites/default/files/2025-12/Drees-Pano-MS%202025.pdf"
_PAGE_DREES = "https://drees.solidarites-sante.gouv.fr/communique-de-presse/communique-de-presse/251204-nombre-allocataires-minima-sociaux"
_URL_CHEQUE = "https://www.ecologie.gouv.fr/presse/debut-denvoi-cheques-energie-lannee-2023-aux-56-millions-menages-beneficiaires"
_URL_COMPTES_INSEE = "https://www.insee.fr/fr/statistiques/8997691"

_OBSERVATOIRE: dict[str, Any] = {
    "collecte_le": DATE_COLLECTE,
    "finances_locales": {
        "libelle": "Finances des collectivités locales",
        "periode": "2025",
        "publication_le": "2026-07-08",
        "collecte_le": DATE_COLLECTE,
        "frequence": "Annuelle; premiers résultats publiés l'année suivante, puis révisés.",
        "statut": "Premiers résultats 2025, non définitifs.",
        "perimetre": "Budgets principaux, hors consolidation, sauf mention contraire.",
        "source": "OFGL / DGCL, Rapport sur les finances des collectivités locales — édition 2026",
        "url": _URL_OFGL,
        "page_source": _PAGE_OFGL,
        "licence": "Source publique DGCL/DGFiP/INSEE; attribution OFGL et DGCL.",
        "croissance_fonctionnement_pct": [
            {"cle": "communes", "libelle": "Communes", "depenses": 1.5, "recettes": 1.7},
            {"cle": "epci", "libelle": "EPCI à fiscalité propre (GFP)", "depenses": 1.8, "recettes": 1.6},
            {"cle": "departements", "libelle": "Départements", "depenses": 1.2, "recettes": 3.4},
            {"cle": "regions", "libelle": "Régions et CTU", "depenses": -0.7, "recettes": 0.9},
        ],
        "croissance_consolidee_depenses_pct": 1.6,
        "note": (
            "Variations nominales annuelles. Les séries par niveau décrivent les budgets "
            "principaux; le +1,6 % consolidé corrige les flux croisés et ne doit pas être "
            "additionné aux quatre niveaux. Ces taux observés ne sont pas des projections "
            "de la commune ou du département de l'utilisateur."
        ),
    },
    "comptes_nationaux": {
        "libelle": "Comptes publics et croissance de la France",
        "periode": "2025",
        "publication": "INSEE, comptes des administrations publiques 2025, publié le 29 mai 2026; OFGL/DGCL pour les budgets locaux.",
        "publication_le": "2026-05-29",
        "collecte_le": DATE_COLLECTE,
        "frequence": "Annuelle, avec révisions des comptes nationaux.",
        "statut": "Comptes annuels 2025 publiés; certaines séries et ratios sont révisables.",
        "source": "INSEE, Le compte des administrations publiques en 2025; comptes nationaux base 2020.",
        "url": _URL_COMPTES_INSEE,
        "page_source": _URL_COMPTES_INSEE,
        "licence": "INSEE — réutilisation avec mention de la source; OFGL/DGCL — attribution.",
        "croissance_pib_volume_pct": 0.8,
        "deficit_public_pct_pib": 5.1,
        "dette_publique_fin_annee_mde": 3460.5,
        "dette_publique_pct_pib": 115.7,
        "deficit_apul_mde": 15.6,
        "deficit_collectivites_locales_mde": 9.3,
        "note": (
            "Les APUL incluent les collectivités locales et les organismes divers "
            "d'administration locale (ODAL); elles ne se confondent pas avec les seules "
            "collectivités territoriales. Le déficit des collectivités locales est ici "
            "présenté en valeur absolue."
        ),
    },
    "ipch_europe": {
        "libelle": "Inflation harmonisée — estimation flash",
        "periode": "2026-09",
        "publication_le": "2026-10-02",
        "collecte_le": DATE_COLLECTE,
        "frequence": "Mensuelle; estimation flash en fin de mois, série complète vers le 16 du mois suivant.",
        "statut": "Estimations provisoires marquées e; données complètes de septembre annoncées le 16 octobre 2026.",
        "source": "Eurostat, IPCH mensuel (jeu prc_hicp_minr et publication flash).",
        "url": _URL_EUROSTAT_FLASH,
        "page_source": "https://ec.europa.eu/eurostat/databrowser/product/view/prc_hicp_minr",
        "licence": "Eurostat — réutilisation libre avec attribution (décision 2011/833/UE).",
        "france_pct": 3.4,
        "zone_euro_21_pct": 3.8,
        "qualite_code": "e",
        "note": (
            "Glissement annuel IPCH. À compter de janvier 2026, la zone euro comprend "
            "21 pays (EA21); les observations de septembre sont estimées. Les valeurs "
            "peuvent être révisées lors de la publication complète."
        ),
    },
    "menages": {
        "bareme_ir_2026": {
            "libelle": "Barème progressif de l'impôt sur le revenu 2026",
            "periode": "Revenus 2025, déclarés en 2026",
            "publication_le": "2026-04-15",
            "collecte_le": DATE_COLLECTE,
            "frequence": "Annuelle; barème fixé par la loi de finances et révisé chaque année.",
            "statut": "Barème 2026, par part de quotient familial.",
            "source": "Service-Public.fr / Direction de l'information légale et administrative.",
            "url": "https://www.service-public.gouv.fr/particuliers/vosdroits/F1419",
            "licence": "Information officielle de l'administration française.",
            "tranches": [
                {"cle": "ir_0", "borne_basse": 0, "borne_haute": 11600, "taux_pct": 0, "libelle": "Jusqu'à 11 600 €"},
                {"cle": "ir_11", "borne_basse": 11600, "borne_haute": 29579, "taux_pct": 11, "libelle": "11 601 € à 29 579 €"},
                {"cle": "ir_30", "borne_basse": 29579, "borne_haute": 84577, "taux_pct": 30, "libelle": "29 580 € à 84 577 €"},
                {"cle": "ir_41", "borne_basse": 84577, "borne_haute": 181917, "taux_pct": 41, "libelle": "84 578 € à 181 917 €"},
                {"cle": "ir_45", "borne_basse": 181917, "borne_haute": None, "taux_pct": 45, "libelle": "Plus de 181 917 €"},
            ],
            "note": (
                "Taux marginaux appliqués par tranche après quotient familial; ce n'est ni le taux moyen "
                "ni l'impôt total d'un foyer. Plafonnement du quotient familial, décotes, crédits/réductions, "
                "revenus de capitaux, prélèvements sociaux et régimes particuliers non calculés ici."
            ),
        },
        "consommation_2025": {
            "libelle": "Consommation et pouvoir d'achat des ménages",
            "periode": "2025",
            "publication_le": "2026-06-16",
            "collecte_le": DATE_COLLECTE,
            "frequence": "Annuelle; comptes nationaux susceptibles de révision.",
            "statut": "Données annuelles 2025; certains tableaux de consommation sont provisoires.",
            "source": "INSEE, La consommation des ménages en 2025 — Insee Première n° 2110.",
            "url": _URL_INSEE_RDB,
            "page_source": _URL_INSEE_RDB,
            "licence": "INSEE — réutilisation avec mention de la source.",
            "depense_finale_mde": 1545.9,
            "variation_volume_pct": 0.4,
            "variation_prix_pct": 0.8,
            "variation_rdb_nominal_pct": 0.5,
            "variation_pouvoir_achat_pct": -0.4,
            "variation_pouvoir_achat_par_uc_pct": -0.7,
            "taux_epargne_pct": 17.9,
            "note": (
                "Indicateurs nationaux agrégés, pas le budget d'un foyer particulier. "
                "Le pouvoir d'achat du RDB baisse de 0,4 % (-0,7 % par unité de consommation)."
            ),
        },
        "panier_national_2025": {
            "libelle": "Consommation effective par fonction — repère de structure",
            "periode": "2025",
            "publication_le": "2026-05-29",
            "collecte_le": DATE_COLLECTE,
            "frequence": "Annuelle; comptes nationaux susceptibles de révision.",
            "statut": "Données provisoires.",
            "source": "INSEE, Consommation effective des ménages par fonction.",
            "url": _URL_INSEE_CONSO,
            "page_source": _URL_INSEE_CONSO,
            "licence": "INSEE — réutilisation avec mention de la source.",
            "part_depense_finale_pct": [
                {"cle": "alimentation", "libelle": "Alimentation et boissons non alcoolisées", "part": 12.5},
                {"cle": "alcool_tabac", "libelle": "Boissons alcoolisées, tabac et stupéfiants", "part": 3.2},
                {"cle": "habillement", "libelle": "Habillement et chaussures", "part": 2.8},
                {"cle": "logement_energie", "libelle": "Logement, eau, gaz, électricité et combustibles", "part": 28.0},
                {"cle": "equipement", "libelle": "Meubles et entretien courant du foyer", "part": 3.7},
                {"cle": "sante", "libelle": "Santé", "part": 3.9},
                {"cle": "transport", "libelle": "Transports", "part": 12.6},
                {"cle": "communication", "libelle": "Information et communication", "part": 3.6},
                {"cle": "loisirs", "libelle": "Loisirs, sport et culture", "part": 7.0},
                {"cle": "education", "libelle": "Services de l'enseignement", "part": 0.8},
                {"cle": "restaurants", "libelle": "Restaurants et hébergement", "part": 9.1},
                {"cle": "autres", "libelle": "Autres biens et services", "part": 14.1},
                {"cle": "correction_tourisme", "libelle": "Correction territoriale (tourisme)", "part": -1.3},
            ],
            "note": (
                "Repère macroéconomique de la dépense finale des ménages, non panier individuel. "
                "Il inclut une correction territoriale tourisme de -1,3 point et des services "
                "de logement imputés; les postes ne représentent pas nécessairement des sorties "
                "de trésorerie comparables à celles d'un foyer."
            ),
        },
        "effort_logement_2024": {
            "libelle": "Taux d'effort net pour le logement",
            "periode": "2024 (début d'année)",
            "publication_le": "2026-09-23",
            "collecte_le": DATE_COLLECTE,
            "frequence": "Enquête périodique; pas de mise à jour mensuelle.",
            "statut": "Mesure observée; France hors Mayotte, logements ordinaires.",
            "source": "INSEE Première n° 2128 — Le logement pèse moins sur le budget en 2024.",
            "url": _URL_INSEE_LOGEMENT,
            "page_source": _URL_INSEE_LOGEMENT,
            "licence": "INSEE — réutilisation avec mention de la source.",
            "effort_net_ensemble_pct": 16.8,
            "effort_net_quartile_modeste_pct": 32.1,
            "effort_net_locataire_prive_pct": 25.4,
            "effort_net_locataire_social_pct": 24.0,
            "effort_net_proprietaire_accédant_pct": 23.3,
            "effort_net_proprietaire_non_accédant_pct": 7.4,
            "note": (
                "Taux d'effort net = dépenses de résidence principale, déduction faite des aides au logement, "
                "rapportées au revenu selon la définition INSEE; ce n'est ni un budget complet ni un barème."
            ),
        },
        "transferts": {
            "aides_logement": {
                "libelle": "Aides personnelles au logement (APL/ALS/ALF)",
                "periode": "2025",
                "publication": "Rapport d'activité CNAF 2025",
                "collecte_le": DATE_COLLECTE,
                "frequence": "Annuelle; effectifs et montants publiés avec le rapport annuel.",
                "statut": "Montant et effectifs agrégés, sans barème individuel.",
                "source": "CNAF, Rapport d'activité 2025 de la branche Famille.",
                "url": _URL_CNAF,
                "page_source": _URL_CNAF,
                "licence": "CNAF — attribution de la source; montants agrégés.",
                "montant_total_mde": 16.1,
                "beneficiaires_millions": 5.6,
                "note": (
                    "Valeur de dénominateur pour un calcul de répartition proportionnelle uniquement. "
                    "Les montants réellement versés dépendent des ressources, de la composition, du loyer "
                    "et de la localisation; aucune éligibilité n'est calculée ici."
                ),
            },
            "minima_sociaux": {
                "libelle": "Allocataires et dépenses des minima sociaux",
                "periode": "2024 (effectifs au 31 décembre)",
                "publication": "Panorama DREES 2025, publié le 4 décembre 2025.",
                "publication_le": "2025-12-04",
                "collecte_le": DATE_COLLECTE,
                "frequence": "Annuelle; effectifs de fin d'année et dépenses publiés avec décalage.",
                "statut": "Effectif estimé et provisoire; dépenses annuelles agrégées.",
                "source": "DREES, Minima sociaux et prestations de solidarité — édition 2025.",
                "url": _URL_DREES,
                "page_source": _PAGE_DREES,
                "licence": "DREES — réutilisation avec mention de la source.",
                "montant_total_mde": 33.3,
                "beneficiaires_millions": 4.252,
                "allocations_versees_millions": 4.4168,
                "note": (
                    "La DREES estime à 4,252 millions le nombre de personnes allocataires après "
                    "correction des doubles comptes; 4,4168 millions d'allocations ont été versées. "
                    "Les 33,3 Md€ correspondent aux dépenses 2024 (les 31,625 Md€ du tableau de "
                    "dépenses détaillées concernent 2023). Ces agrégats ne permettent pas de calculer "
                    "le droit individuel d'un foyer."
                ),
            },
            "cheque_energie": {
                "libelle": "Chèque énergie",
                "periode": "2023 (dernier effectif national indiqué par la page consultée)",
                "publication": "Ministère de la Transition écologique, campagne 2023 (communiqué du 21 avril 2023).",
                "publication_le": "2023-04-21",
                "collecte_le": DATE_COLLECTE,
                "frequence": "Campagne annuelle; effectifs susceptibles de varier selon les règles d'éligibilité.",
                "statut": "Repère ancien, utilisé uniquement si l'utilisateur coche l'éligibilité.",
                "source": "Ministère de la Transition écologique, lancement de la campagne 2023.",
                "url": _URL_CHEQUE,
                "page_source": _URL_CHEQUE,
                "licence": "Données publiques; attribution du ministère.",
                "beneficiaires_millions": 5.6,
                "note": (
                    "Le dénominateur de bénéficiaires est un repère 2023, pas une estimation du nombre "
                    "de bénéficiaires en 2025 ou 2026. Aucune éligibilité automatique."
                ),
            },
        },
        "note": (
            "Le profil de foyer est une saisie locale au navigateur, pas un échantillon statistique. "
            "Les valeurs de ce bloc sont des références nationales agrégées et ne doivent pas être "
            "interprétées comme le budget réel de chaque ménage."
        ),
    },
    "acteurs_et_territoires": {
        "libelle": "Repères de strates et acteurs budgétaires français",
        "collecte_le": DATE_COLLECTE,
        "sources": [
            {"libelle": "INSEE — administrations publiques en 2025, secteurs S.1311/S.1313/S.1314", "url": "https://www.insee.fr/fr/statistiques/8988833"},
            {"libelle": "Code général des collectivités territoriales", "url": "https://www.legifrance.gouv.fr/codes/id/LEGITEXT000006070633/"},
            {"libelle": "Associations — loi du 1er juillet 1901", "url": "https://www.legifrance.gouv.fr/loda/id/JORFTEXT000000497458/"},
            {"libelle": "Impôt sur les sociétés — Service-Public.fr", "url": "https://www.service-public.gouv.fr/professionnels-entreprises/vosdroits/F23575"},
        ],
        "territoires": [
            {"cle": "infra_communal", "libelle": "Hameau, quartier, village (échelle infra-communale; pas de budget public autonome)"},
            {"cle": "commune", "libelle": "Commune / commune nouvelle"},
            {"cle": "epci", "libelle": "EPCI, métropole, syndicat ou groupement"},
            {"cle": "departement", "libelle": "Département / collectivité à compétence départementale"},
            {"cle": "region", "libelle": "Région / collectivité territoriale unique"},
            {"cle": "france_metropolitaine", "libelle": "France métropolitaine (agrégats nationaux; pas une collectivité unique)"},
            {"cle": "drom", "libelle": "DROM et collectivités régies par l'article 73"},
            {"cle": "com", "libelle": "COM, Nouvelle-Calédonie et statuts particuliers"},
            {"cle": "etat", "libelle": "État et administrations centrales"},
        ],
        "couverture_territoriale": [
            {"niveau": "Hameau, quartier, village", "couverture": "Taxonomie seulement; les comptes OFGL utilisés ne publient pas de budget public autonome à cette échelle."},
            {"niveau": "Commune", "couverture": "Observations OFGL agrégées par niveau; aucun budget communal individuel raccordé au moteur."},
            {"niveau": "EPCI et métropoles", "couverture": "Observations agrégées par catégorie EPCI; pas de ventilation de chaque métropole."},
            {"niveau": "Département / collectivité départementale", "couverture": "Observations agrégées; trajectoire de scénario locale non distincte."},
            {"niveau": "Région / CTU", "couverture": "Observations agrégées; trajectoire de scénario locale non distincte."},
            {"niveau": "France métropolitaine", "couverture": "Comptes nationaux agrégés, sans découpage fin par commune ou département."},
            {"niveau": "DROM / COM / Nouvelle-Calédonie", "couverture": "Périmètres identifiés dans la taxonomie, mais non chiffrés séparément dans cette simulation."},
        ],
        "organisations": [
            {"cle": "foyers", "libelle": "Personnes et foyers fiscaux (barème IR par part)"},
            {"cle": "entreprises", "libelle": "Entreprises et indépendants (cotés / non cotés; régimes fiscaux différents)"},
            {"cle": "associations", "libelle": "Associations et organismes sans but lucratif"},
            {"cle": "collectivites", "libelle": "Collectivités et groupements locaux"},
            {"cle": "etat_et_operateurs", "libelle": "État, opérateurs et organismes publics"},
            {"cle": "etablissements_publics", "libelle": "Établissements publics (dont hôpitaux et enseignement selon leur classement)"},
            {"cle": "etablissements_prives", "libelle": "Établissements et institutions privés"},
            {"cle": "elus", "libelle": "Élus : personne physique et mandat public à distinguer"},
        ],
        "note": (
            "Cette taxonomie distingue territoire, secteur comptable, personnalité juridique et régime fiscal : "
            "ces catégories ne se recouvrent pas. Une association peut être non imposable à l'IS dans certaines "
            "conditions ou fiscalisée pour des activités lucratives; un établissement public peut être classé "
            "dans un sous-secteur différent selon son activité. Les élus ne constituent pas un secteur budgétaire "
            "autonome. Liste de travail structurante, non inventaire exhaustif de toutes les personnes morales, "
            "régimes dérogatoires ou règles locales. Les profils de portefeuille saisis par utilisateur ne sont "
            "pas des statistiques de détention observées."
        ),
    },
    "methode": {
        "simulation": (
            "Les résultats de chaque strate comparent une trajectoire paramétrée à la trajectoire de "
            "référence (leviers neutres) calculées avec le même moteur. Ce sont des écarts de scénario, "
            "pas une prévision certaine."
        ),
        "local": (
            "Le moteur restitue un indicateur local agrégé; il ne calcule pas de projection séparée "
            "pour la commune, l'EPCI, le département et la région. Les observations par niveau restent "
            "séparées des grandeurs simulées."
        ),
        "menages": (
            "Les effets directs sont calculés à partir des postes déclarés (et des hypothèses cochées). "
            "Les effets indirects de prix, taux et revenus sont transmis selon les règles affichées dans "
            "l'onglet Ménages. Les prestations dont le barème ou la répartition n'est pas modélisé sont "
            "signalées comme non imputables."
        ),
    },
}


def observatoire_public() -> dict[str, Any]:
    """Renvoie une copie JSON-sérialisable des références publiques datées."""
    return deepcopy(_OBSERVATOIRE)
