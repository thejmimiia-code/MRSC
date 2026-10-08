"""
Package simulateur — Moteur macro-politique et systémique.
"""

from simulateur.geopolitique_annuelle import (
    EchelonGeopolitique,
    EffetsGeopolitiques,
    PointDePassageStrategique,
    propager_geopolitique,
)
from simulateur.model import (
    DecisionPolitique,
    EchelonEuropeen,
    EchelonLocal,
    EchelonMondial,
    EchelonNational,
    ResultatEtapeSimulation,
    SousSecteurBlocCommunal,
    SousSecteurChambresConsulaires,
    SousSecteurDepartements,
    SousSecteurEtatCentral,
    SousSecteurInstitutionsRepublique,
    SousSecteurParlement,
    SousSecteurRegions,
    SousSecteurSecuriteSociale,
)
from simulateur.moteur import MoteurSimulationSystemique
from simulateur.reglements_lois import (
    REGISTRE_LEGAL,
    ArticleDeLoi,
    get_corpus_lois,
    rechercher_loi,
)
from simulateur.scenarios import (
    get_scenario_alternance_2032,
    get_scenario_austerite_brutale,
    get_scenario_choc_mondial_stagflation,
    get_scenario_convergence_ww3,
    get_scenario_crise_taiwan,
    get_scenario_double_mandature,
    get_scenario_escalade_nucleaire_tactique,
    get_scenario_fermeture_hormuz,
    get_scenario_mandature_5_ans,
    get_scenario_resilience_republicaine,
    get_scenario_statut_quo,
)

__all__ = [
    "EchelonLocal",
    "EchelonNational",
    "EchelonEuropeen",
    "EchelonMondial",
    "DecisionPolitique",
    "ResultatEtapeSimulation",
    "SousSecteurBlocCommunal",
    "SousSecteurDepartements",
    "SousSecteurRegions",
    "SousSecteurEtatCentral",
    "SousSecteurSecuriteSociale",
    "SousSecteurParlement",
    "SousSecteurChambresConsulaires",
    "SousSecteurInstitutionsRepublique",
    "MoteurSimulationSystemique",
    "get_scenario_mandature_5_ans",
    "get_scenario_statut_quo",
    "get_scenario_austerite_brutale",
    "get_scenario_choc_mondial_stagflation",
    "get_scenario_crise_taiwan",
    "get_scenario_fermeture_hormuz",
    "get_scenario_escalade_nucleaire_tactique",
    "get_scenario_convergence_ww3",
    "get_scenario_resilience_republicaine",
    "get_scenario_double_mandature",
    "get_scenario_alternance_2032",
    "EchelonGeopolitique",
    "PointDePassageStrategique",
    "EffetsGeopolitiques",
    "propager_geopolitique",
    "ArticleDeLoi",
    "REGISTRE_LEGAL",
    "get_corpus_lois",
    "rechercher_loi",
]
