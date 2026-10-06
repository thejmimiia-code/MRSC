"""
simulateur/model.py — Modélisation des 4 strates systémiques interconnectées :
Local (Communes/Dép/Rég), National (État/Sécu/Parlement), Continental (UE/BCE/PDE), Mondial (AFT/Marchés/Spreads).
Données réelles calées à l'instant T (septembre 2026).
"""

from dataclasses import dataclass, field

# =============================================================================
# STRATE 1 : ÉCHELON LOCAL (La Cellule de Base Territoriale)
# =============================================================================

@dataclass
class SousSecteurBlocCommunal:
    """Communes et Intercommunalités (EPCI)."""
    depenses_fonctionnement_mde: float = 85.0   # Salaires, crèches, voirie, police municipale
    depenses_investissement_mde: float = 42.0   # Bâtiments scolaires, transition, eau
    dgf_recue_mde: float = 12.2                 # Dotation globale de fonctionnement
    taxe_fonciere_tfpb_mde: float = 39.5        # Produit de la taxe foncière sur les propriétés bâties
    cfe_et_autres_impots_mde: float = 35.0      # Cotisation Foncière des Entreprises, taxe de séjour


@dataclass
class SousSecteurDepartements:
    """Conseils Départementaux (Action sociale et solidarité)."""
    depenses_sociales_obligatoires_mde: float = 44.5  # RSA, APA (aînés), PCH (handicap), ASE (enfance)
    depenses_colleges_et_routes_mde: float = 18.0
    recettes_dmto_droits_mutation_mde: float = 12.5   # "Frais de notaire" (extrêmement volatils)
    fraction_tva_nationale_mde: float = 16.5          # Part de TVA transférée en compensation
    dgf_departementale_mde: float = 10.0


@dataclass
class SousSecteurRegions:
    """Conseils Régionaux (Développement économique, TER, Lycées)."""
    depenses_transports_ter_mde: float = 14.5
    depenses_lycees_formation_mde: float = 18.5
    fraction_tva_regionale_mde: float = 12.0
    fraction_ticpe_mde: float = 8.0
    dgf_regionale_mde: float = 5.0


@dataclass
class SousSecteurChambresConsulaires:
    """Réseau consulaire territorial (CCI, CMA, Chambres d'Agriculture - Établissements Publics Administratifs)."""
    ressortissants_entreprises_milliers: float = 6900.0   # 3,8M CCI + 1,9M CMA + 1,2M CA
    taxe_frais_de_chambres_mde: float = 1.35              # TFC assise sur CFE et taxe additionnelle TFPNB
    taux_survie_pme_locales_pct: float = 68.5             # Taux de pérennité des PME après 5 ans
    taux_insertion_apprentissage_pct: float = 78.0        # Apprentis formés par les CFA et écoles consulaires
    surfaces_agricoles_preservees_pct: float = 98.2       # Rôle CA / CDPENAF contre l'artificialisation des sols


@dataclass
class EchelonLocal:
    """Strate consolidée des Collectivités Territoriales et Acteurs Économiques de Terroir."""
    bloc_communal: SousSecteurBlocCommunal = field(default_factory=SousSecteurBlocCommunal)
    departements: SousSecteurDepartements = field(default_factory=SousSecteurDepartements)
    regions: SousSecteurRegions = field(default_factory=SousSecteurRegions)
    chambres_consulaires: SousSecteurChambresConsulaires = field(default_factory=SousSecteurChambresConsulaires)

    # Indicateurs consolidés de la strate locale
    dette_locale_totale_mde: float = 252.0
    tension_sociale_territoriale: float = 36.0        # Indice 0-100 (grogne des contribuables et usagers)
    qualite_services_proximite: float = 64.0          # Indice 0-100 (santé de proximité, guichets, transports)


# =============================================================================
# STRATE 2 : ÉCHELON NATIONAL (Le Moteur Institutionnel & Budgétaire)
# =============================================================================

@dataclass
class SousSecteurEtatCentral:
    """Budget général de l'État (APUC)."""
    recettes_fiscales_nettes_mde: float = 345.0       # TVA nette d'État, IR, IS, TICPE résiduelle
    depenses_ministeres_primaires_mde: float = 465.0  # Masse salariale fonctionnaires, Éducation, Défense, Justice
    charge_nette_dette_mde: float = 66.5              # Charge annuelle des intérêts des titres d'État
    deficit_budgetaire_etat_mde: float = 145.0        # Déficit propre du budget de l'État


@dataclass
class SousSecteurSecuriteSociale:
    """Administrations de Sécurité Sociale (ASSO - CNAM, CNAV, CNAF, CNSA)."""
    recettes_cotisations_et_csg_mde: float = 650.0   # Cotisations patronales/salariales, CSG, CRDS
    depenses_prestations_mde: float = 662.0          # Assurance maladie (ONDAM), Retraites, Famille
    deficit_securite_sociale_mde: float = 12.0       # Déficit structurel des régimes de base


@dataclass
class SousSecteurParlement:
    """Climat politique et équilibre des forces à l'Assemblée nationale."""
    sieges_coalition_gouvernementale: int = 210       # Majorité relative (sur 577 sièges)
    seuil_censure_absolue: int = 289                  # Majorité requise pour renverser le gouvernement
    probabilite_motion_censure_pct: float = 52.0      # Risque de censure calculé
    recours_article_49_3_count: int = 0               # Nombre d'utilisations du 49.3


@dataclass
class SousSecteurInstitutionsRepublique:
    """Garanties constitutionnelles, juridictions suprêmes et corps de contrôle républicains."""
    conseil_constitutionnel_conformite_pct: float = 100.0 # Conformité aux décisions DC et QPC (art. 61 et 61-1)
    cour_des_comptes_evaluation_efficience: float = 72.0  # Indice d'efficience et audit des comptes publics (art. 47-2)
    conseil_etat_securite_juridique_pct: float = 96.0     # Taux de validation préalable des projets de lois (art. 39)
    defenseur_des_droits_recours_regles_pct: float = 84.0 # Taux de médiation réussie des usagers (art. 71-1)


@dataclass
class EchelonNational:
    """Strate consolidée de la Nation et de ses Institutions républicaines."""
    pib_nominal_mde: float = 3015.0                   # PIB nominal français à l'instant T
    taux_croissance_potentiel: float = 0.019          # 1,9 % de croissance nominale tendancielle
    etat: SousSecteurEtatCentral = field(default_factory=SousSecteurEtatCentral)
    securite_sociale: SousSecteurSecuriteSociale = field(default_factory=SousSecteurSecuriteSociale)
    parlement: SousSecteurParlement = field(default_factory=SousSecteurParlement)
    institutions: SousSecteurInstitutionsRepublique = field(default_factory=SousSecteurInstitutionsRepublique)

    # Indicateurs civiques et macro-sociaux
    dette_maastricht_stock_mde: float = 3568.0        # Dette publique consolidée au sens de Maastricht
    confiance_democratique: float = 27.5              # Indice 0-100 (confiance dans les institutions)
    pouvoir_achat_menages_index: float = 100.0        # Base 100


# =============================================================================
# STRATE 3 : ÉCHELON CONTINENTAL / EUROPÉEN (Le Cadre de Contrainte)
# =============================================================================

@dataclass
class EchelonEuropeen:
    """Strate de l'Union Européenne et de la Zone Euro."""
    # Règles budgétaires du Pacte de Stabilité réformé (avril 2024)
    seuil_deficit_pde_pct: float = 3.00               # Plafond de 3.0 % du PIB
    seuil_dette_pacte_pct: float = 60.0               # Plafond de 60.0 % du PIB
    effort_structurel_requis_annuel_pct: float = 0.50 # 0.5 pt de PIB d'effort annuel sous PDE
    statut_pde_actif: bool = True                     # La France est sous procédure de déficit excessif
    amende_sanction_semestrielle_mde: float = 1.50    # 0,05 % du PIB d'astreinte financière

    # Politique Monétaire de la Banque Centrale Européenne (BCE)
    taux_depot_bce_pct: float = 2.50                  # Taux de référence de la BCE
    quantitative_tightening_actif: bool = True        # La BCE ne réinvestit plus les OAT échues
    bouclier_tpi_bce_eligible: bool = False           # TPI actif UNIQUEMENT si discipline budgétaire respectée

    # Compétitivité et Marché Unique
    competitivite_fiscale_relative: float = 46.0      # Indice 0-100 face à l'Allemagne/Espagne/Italie


# =============================================================================
# STRATE 4 : ÉCHELON MONDIAL (Marchés Financiers, Matières Premières & Géopolitique)
# =============================================================================

@dataclass
class EchelonMondial:
    """Strate des Marchés Financiers Internationaux, Matières Premières, Banques Centrales et AFT."""
    # Structure de détention et refinancement de la dette d'État
    part_dette_detenue_non_residents: float = 0.558   # 55,8 % de la dette d'État entre les mains de non-résidents
    maturite_moyenne_dette_ans: float = 8.5           # Durée de vie moyenne du portefeuille de l'AFT
    part_dette_refinancement_annuel_pct: float = 0.35 # ~35 % de la dette est refinancée chaque année (1/maturité≈11.8%)
    besoin_financement_brut_annuel_mde: float = 435.0 # ~285 Md€ dette échue à renouveler + ~150 Md€ déficit

    # Taux, Spreads et Notation financière souveraine
    taux_oat_france_10ans: float = 4.18               # Taux souverain à 10 ans de la France
    taux_bund_allemagne_10ans: float = 3.30           # Taux sans risque allemand
    spread_oat_bund_bps: float = 88.0                 # Écart de taux en points de base (88 bps)
    note_souveraine: str = "AA-"                      # Notation financière S&P / Fitch / Moody's (Aa3)
    prime_risque_politique_bps: float = 25.0          # Prime de risque spécifique liée aux incertitudes

    # Marchés Mondiaux de l'Énergie & Matières Premières (Commodities)
    cours_petrole_brent_usd: float = 82.5             # Prix du baril de Brent (USD/baril)
    cours_gaz_naturel_ttf_eur_mwh: float = 38.0       # Gaz TTF de référence européen (€/MWh)
    prix_tonne_carbone_ets_eur: float = 72.0          # Quota Système d'échange de quotas d'émission UE (€/t CO2)
    facture_energetique_nette_mde: float = 64.5       # Solde déficitaire des importations nettes d'énergie (Md€/an)

    # Système Monétaire International & Banques Centrales
    taux_directeur_fed_pct: float = 5.33              # Taux Fed Funds target aux États-Unis (%)
    taux_directeur_bce_depot_pct: float = 3.75         # Taux de facilité de dépôt BCE (%)
    taux_change_eur_usd: float = 1.08                 # Parité de change EUR/USD ($ par €)
    indice_fret_maritime_scfi: float = 2450.0         # Shanghai Containerized Freight Index (SCFI)

    # Commerce International & Réglementations Globales
    taux_imposition_pilier2_ocde_pct: float = 15.0    # Accord OCDE Pilier 2 - Impôt minimum mondial (CGI art. 223 VJ)
    croissance_commerce_mondial_pct: float = 2.8      # Croissance en volume du commerce mondial (%)

    # Transmission à l'économie réelle
    taux_credit_immobilier_menages: float = 3.85      # Impact direct de l'OAT sur le crédit aux particuliers
    taux_credit_pme_entreprises: float = 4.90         # Coût d'emprunt des PME françaises
    inflation_globale_pct: float = 2.1                # Taux d'inflation globale répercuté (IPC France)


# =============================================================================
# VECTEUR DE DÉCISION & RÉSULTAT CONSOLIDÉ
# =============================================================================

@dataclass
class DecisionPolitique:
    """Vecteur de politique publique appliqué pour une année donnée."""
    annee: int = 1
    description: str = "Décision annuelle"

    # Nouvelles recettes fiscales de régulation (Md€)
    recettes_fraude_ia_mde: float = 0.0
    conditionnement_aides_entreprises_mde: float = 0.0
    taxe_superprofits_rachats_mde: float = 0.0
    extension_ttf_mde: float = 0.0
    recettes_pilier2_ocde_mde: float = 0.0            # Recette fiscale : impôt minimum mondial 15% (CGI 223 VJ)
    recettes_macf_carbone_mde: float = 0.0            # Recette : Mécanisme d'ajustement carbone aux frontières (UE)

    # Économies structurelles & fonctionnement (Md€)
    fusion_doublons_territoriaux_mde: float = 0.0
    commande_publique_massifiee_mde: float = 0.0
    extinction_niches_inefficaces_mde: float = 0.0
    fraude_sociale_criminelle_mde: float = 0.0

    # Restitution pouvoir d'achat (Md€)
    baisse_tva_energie_5_5_mde: float = 0.0

    # Réformes institutionnelles & démocratiques (bool)
    reforme_casier_b2: bool = False
    reforme_vote_blanc_invalidant: bool = False
    reforme_ric_souverain: bool = False
    reforme_fin_regimes_speciaux: bool = False
    reforme_anti_pantouflage_lobbys: bool = False
    reforme_non_cumul_mandats: bool = False

    # Transferts financiers aux collectivités (DGF)
    delta_dotation_dgf_mde: float = 0.0

    # Agrégats « leviers libres » du simulateur interactif (simulateur/domaines.py).
    # Les recettes nouvelles hors champs dédiés et les dépenses prioritaires nettes
    # sont injectées telles quelles dans la mécanique budgétaire du moteur.
    recettes_nouvelles_mde: float = 0.0
    depenses_prioritaires_mde: float = 0.0

    # Chocs et variables macro-financières exogènes mondiales
    choc_petrole_brent_usd: float = 0.0               # Exogène : variation du baril (ex: +25 $/bbl)
    choc_taux_fed_bps: float = 0.0                    # Exogène : resserrement Fed en bps (ex: +50 bps)
    choc_change_eur_usd: float = 0.0                  # Exogène : variation de la parité (ex: -0.08)

    # --- STRATE 5 : GÉOPOLITIQUE, SÉCURITÉ & CHAÎNES D'APPROVISIONNEMENT -----
    # Variations annuelles des indices de tension des 4 théâtres (points d'indice)
    delta_tension_taiwan: float = 0.0
    delta_tension_ukraine_otan: float = 0.0
    delta_tension_iran_hormuz: float = 0.0
    delta_convergence_blocs: float = 0.0              # Axe Chine-Russie-Iran (exercices conjoints)

    # Chocs d'approvisionnement et franchissement de seuils (0.0 = rien, 1.0 = total)
    fermeture_hormuz_intensite: float = 0.0           # Chokepoint Hormuz (20 % du pétrole mondial)
    blocus_taiwan_intensite: float = 0.0              # Chokepoint Taïwan (60 % des semi-conducteurs)
    usage_nucleaire_tactique: bool = False            # Franchissement du seuil nucléaire tactique
    cyberattaque_systemique: bool = False             # Attaque majeure sur les OIV (NIS2 / ANSSI)

    # Leviers de réponse souveraine
    effort_defense_cible_pct_pib: float = 0.0         # 0 = inchangé ; cible OTAN La Haye : 3,50 %
    mobilisation_economie_de_guerre: bool = False     # Cadences industrielles & commandes pluriannuelles
    liberation_stocks_strategiques: bool = False      # Déstockage coordonné AIE (90 j minimum)
    plan_souverainete_semiconducteurs_mde: float = 0.0  # Chips Act / relocalisation (Md€/an)
    activation_clause_sauvegarde_nationale_ue: bool = False  # Dérogation défense du Pacte de stabilité


@dataclass
class ResultatEtapeSimulation:
    """Instantané complet des 4 strates après propagation systémique."""
    annee: int
    pib_nominal_mde: float

    # Échelon National
    deficit_nominal_mde: float
    ratio_deficit_pib: float
    dette_nominale_mde: float
    ratio_dette_pib: float
    charge_dette_mde: float
    recettes_publiques_totales_mde: float
    depenses_publiques_totales_mde: float
    pouvoir_achat_index: float
    confiance_democratique: float
    risque_censure_parlement: float

    # Échelon Local
    tension_sociale_locale: float
    qualite_services_proximite: float
    produit_taxe_fonciere_mde: float

    # Échelon Européen
    statut_pde_europe: bool
    bouclier_tpi_actif: bool
    sanction_financiere_ue: bool

    # Échelon Mondial
    taux_oat_pct: float
    spread_bund_bps: float
    note_souveraine: str
    taux_credit_pme: float
    cours_petrole_usd: float = 82.5
    taux_change_eur_usd: float = 1.08
    facture_energetique_mde: float = 64.5
    inflation_globale_pct: float = 2.1

    # Échelon Géopolitique (strate 5)
    indice_tension_geopolitique: float = 63.0
    probabilite_escalade_mondiale_pct: float = 0.0
    risque_nucleaire_tactique_pct: float = 12.0
    disponibilite_semiconducteurs_pct: float = 100.0
    effort_defense_pct_pib: float = 2.10
    depenses_defense_mde: float = 63.3
    prime_risque_geopolitique_bps: float = 12.0
    chokepoints_sous_tension: int = 0
    stocks_strategiques_petrole_jours: float = 98.0

    commentaires: list[str] = field(default_factory=list)
