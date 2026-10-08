"""
simulateur/scenarios.py — Catalogue des scénarios types de simulation.

Scénarios quinquennaux (une mandature) et scénarios décennaux
(deux mandatures consécutives : cf. docs/RD_DOUBLE_MANDATURE.md).
"""


from simulateur.model import DecisionPolitique


def get_scenario_mandature_5_ans() -> list[DecisionPolitique]:
    """
    Le scénario du Dossier de Mandature Globale (+60 Md€ en Année 5).
    Répartition graduelle et réaliste sur 5 exercices.
    """
    return [
        DecisionPolitique(
            annee=1,
            description="Année 1 : Urgence pouvoir d'achat, moralisation et premières recettes",
            recettes_fraude_ia_mde=0.0,
            conditionnement_aides_entreprises_mde=0.0,
            taxe_superprofits_rachats_mde=6.0,
            extension_ttf_mde=5.0,
            fusion_doublons_territoriaux_mde=0.0,
            commande_publique_massifiee_mde=0.0,
            extinction_niches_inefficaces_mde=4.0,
            fraude_sociale_criminelle_mde=0.0,
            baisse_tva_energie_5_5_mde=9.0,
            reforme_casier_b2=True,
            reforme_vote_blanc_invalidant=True,
            reforme_ric_souverain=True,
            reforme_fin_regimes_speciaux=True,
            reforme_anti_pantouflage_lobbys=True,
            delta_dotation_dgf_mde=0.0,
        ),
        DecisionPolitique(
            annee=2,
            description="Année 2 : Déploiement IA fraude et premières négociations commande publique",
            recettes_fraude_ia_mde=4.0,
            conditionnement_aides_entreprises_mde=0.0,
            taxe_superprofits_rachats_mde=6.0,
            extension_ttf_mde=5.0,
            fusion_doublons_territoriaux_mde=1.5,
            commande_publique_massifiee_mde=2.0,
            extinction_niches_inefficaces_mde=5.5,
            fraude_sociale_criminelle_mde=1.0,
            baisse_tva_energie_5_5_mde=9.0,
            reforme_non_cumul_mandats=True,
            delta_dotation_dgf_mde=0.0,
        ),
        DecisionPolitique(
            annee=3,
            description="Année 3 : Smart Clearing des aides (DSN) et convergence SI territoriaux",
            recettes_fraude_ia_mde=7.0,
            conditionnement_aides_entreprises_mde=7.0,
            taxe_superprofits_rachats_mde=6.0,
            extension_ttf_mde=5.0,
            fusion_doublons_territoriaux_mde=4.0,
            commande_publique_massifiee_mde=3.5,
            extinction_niches_inefficaces_mde=7.0,
            fraude_sociale_criminelle_mde=2.0,
            baisse_tva_energie_5_5_mde=9.0,
            delta_dotation_dgf_mde=0.0,
        ),
        DecisionPolitique(
            annee=4,
            description="Année 4 : Montée en puissance internationale DAC7/DAC8 et rationalisation foncière",
            recettes_fraude_ia_mde=9.0,
            conditionnement_aides_entreprises_mde=12.0,
            taxe_superprofits_rachats_mde=6.0,
            extension_ttf_mde=5.0,
            fusion_doublons_territoriaux_mde=6.5,
            commande_publique_massifiee_mde=5.0,
            extinction_niches_inefficaces_mde=7.0,
            fraude_sociale_criminelle_mde=2.5,
            baisse_tva_energie_5_5_mde=9.0,
            delta_dotation_dgf_mde=0.0,
        ),
        DecisionPolitique(
            annee=5,
            description="Année 5 : Régime de croisière stabilisé (+60 Md€ / an, déficit < 3 % PIB)",
            recettes_fraude_ia_mde=10.0,
            conditionnement_aides_entreprises_mde=15.0,
            taxe_superprofits_rachats_mde=6.0,
            extension_ttf_mde=5.0,
            fusion_doublons_territoriaux_mde=8.0,
            commande_publique_massifiee_mde=6.0,
            extinction_niches_inefficaces_mde=7.0,
            fraude_sociale_criminelle_mde=3.0,
            baisse_tva_energie_5_5_mde=9.0,
            delta_dotation_dgf_mde=0.0,
        ),
    ]


# =============================================================================
# SCÉNARIOS DÉCENNAUX — DEUX MANDATURES CONSÉCUTIVES (2027-2037)
# (R&D : docs/RD_DOUBLE_MANDATURE.md — points stratégiques systématiques de la
#  période de dix ans : calendrier électoral, verrou constitutionnel, dividende
#  de la dette, investissements à cycle long, usure du capital politique.)
# =============================================================================

#: Marges du plan de mandature à régime de croisière (Année 5 et au-delà).
_REGIME_CROISIERE = {
    "recettes_fraude_ia_mde": 10.0,
    "conditionnement_aides_entreprises_mde": 15.0,
    "taxe_superprofits_rachats_mde": 6.0,
    "extension_ttf_mde": 5.0,
    "fusion_doublons_territoriaux_mde": 8.0,
    "commande_publique_massifiee_mde": 6.0,
    "extinction_niches_inefficaces_mde": 7.0,
    "fraude_sociale_criminelle_mde": 3.0,
    "baisse_tva_energie_5_5_mde": 9.0,
}


def get_scenario_double_mandature() -> list[DecisionPolitique]:
    """
    Scénario « deux mandatures consécutives » (2027-2037, dix exercices).

    * Années 1-5  : plan de mandature quinquennal du dossier global, plus les
      investissements à cycle long déjà engagés à l'instant T (EPR2, LPM
      2024-2030, France 2030, prévention santé) dont le rendement n'arrive
      qu'en fin de période (courbe en J) ; année 5 = année électorale 2032
      (présidentielle + législatives, évaluation de bilan par clauses de
      revoyure) ;
    * Année 6     : investiture de la mandature 2, ancrage constitutionnel
      des réformes de la mandature 1 (verrou d'irréversibilité) ;
    * Années 7-10 : régime de croisière + « second dividende » de la dette
      (le stock, maturité moyenne 8,5 ans, est intégralement refinancé aux
      taux détendus) + poursuite des investissements à cycle long + usure
      croissante du capital politique, maximale en fin de seconde mandature
      (élection 2037).
    """
    premiere = get_scenario_mandature_5_ans()
    # Année 4 : les investissements à cycle long déjà engagés à l'instant T
    # (EPR2, LPM 2024-2030) sont poursuivis ; leur rendement est différé.
    premiere[3].investissements_cycle_long_mde = 4.0
    premiere[3].description = (
        "Année 4 : Montée en puissance internationale DAC7/DAC8, rationalisation foncière "
        "et investissements à cycle long déjà engagés (EPR2, LPM 2024-2030)"
    )
    # Année 5 : année électorale 2032 + investissements France 2030 / prévention.
    premiere[4].annee_electorale_majeure = True
    premiere[4].clause_revoyure_evaluation = True
    premiere[4].investissements_cycle_long_mde = 5.0
    premiere[4].description = (
        "Année 5 : Régime de croisière stabilisé (+60 Md€ / an), investissements à cycle "
        "long (France 2030, prévention santé) et année électorale 2032 "
        "(présidentielle + législatives, évaluation de bilan)"
    )
    seconde = [
        DecisionPolitique(
            annee=6,
            description="Mandature 2, An 1 : investiture 2032, verrou constitutionnel des réformes "
                        "de la mandature 1 et premiers investissements à cycle long (EPR2, LPM)",
            verrouillage_irreversibilite=True,
            clause_revoyure_evaluation=True,
            investissements_cycle_long_mde=4.0,
            **_REGIME_CROISIERE,
        ),
        DecisionPolitique(
            annee=7,
            description="Mandature 2, An 2 : le refinancement de la dette produit ses premiers "
                        "dividendes (3 Md€ réinvestis), poursuite des investissements à cycle long",
            verrouillage_irreversibilite=True,
            clause_revoyure_evaluation=True,
            reinvestissement_dividende_dette_mde=3.0,
            investissements_cycle_long_mde=5.0,
            **_REGIME_CROISIERE,
        ),
        DecisionPolitique(
            annee=8,
            description="Mandature 2, An 3 : dividende de la dette à 5 Md€, usure politique naissante",
            verrouillage_irreversibilite=True,
            clause_revoyure_evaluation=True,
            reinvestissement_dividende_dette_mde=5.0,
            investissements_cycle_long_mde=6.0,
            usure_politique_pts=10.0,
            **_REGIME_CROISIERE,
        ),
        DecisionPolitique(
            annee=9,
            description="Mandature 2, An 4 : maturité des premiers investissements à cycle long, "
                        "dividende à 7 Md€, usure politique croissante",
            verrouillage_irreversibilite=True,
            clause_revoyure_evaluation=True,
            reinvestissement_dividende_dette_mde=7.0,
            investissements_cycle_long_mde=6.0,
            usure_politique_pts=20.0,
            **_REGIME_CROISIERE,
        ),
        DecisionPolitique(
            annee=10,
            description="Mandature 2, An 5 : année électorale 2037 — bilan des deux mandatures, "
                        "réformes verrouillées, dividende à 8 Md€, usure de fin de cycle",
            annee_electorale_majeure=True,
            verrouillage_irreversibilite=True,
            clause_revoyure_evaluation=True,
            reinvestissement_dividende_dette_mde=8.0,
            investissements_cycle_long_mde=6.0,
            usure_politique_pts=30.0,
            **_REGIME_CROISIERE,
        ),
    ]
    trajectoire = premiere + seconde
    for decision in trajectoire:
        decision.horizon_deux_mandatures = True
        decision.entretien_capital_public_mde = 6.0
        decision.effort_adaptation_climat_mde = 1.0
        decision.capital_humain_mde = 2.0
        decision.montee_capacite_defense_mde = 2.0
        decision.reformes_structurelles_actives = 6.0
    return trajectoire


def get_scenario_alternance_2032() -> list[DecisionPolitique]:
    """
    Stress-test « alternance 2032 » : deux mandatures sans verrou.

    La mandature 1 déroule le plan de mandature, mais les réformes ne sont
    jamais ancrées dans la Constitution. En 2032, une majorité hostile
    l'emporte : elle n'abroge pas les recettes fiscales (peu coûteux
    politiquement de les conserver) mais gèle les investissements à cycle
    long, ne réinvestit aucun dividende de la dette et laisse l'usure du
    capital politique monter jusqu'à l'élection de 2037.

    Ce scénario mesure, par comparaison avec `get_scenario_double_mandature`,
    le coût de l'absence de verrouillage constitutionnel (limite assumée du
    prototype : l'abrogation effective des réformes n'est pas encore modélisée,
    cf. docs/RD_DOUBLE_MANDATURE.md §Limites).
    """
    premiere = get_scenario_mandature_5_ans()
    # Les investissements à cycle long engagés en mandature 1 existent dans les
    # deux scénarios : les infrastructures mûrissent quel que soit le vainqueur
    # de 2032 (c'est le réinvestissement de la mandature 2 qui diverge).
    premiere[3].investissements_cycle_long_mde = 4.0
    premiere[4].annee_electorale_majeure = True
    premiere[4].investissements_cycle_long_mde = 5.0
    premiere[4].description = (
        "Année 5 : Régime de croisière et année électorale 2032 — réformes NON verrouillées"
    )
    seconde = [
        DecisionPolitique(
            annee=annee,
            description=(
                f"Mandature d'alternance, An {annee - 5} : réformes révocables, "
                f"investissements à cycle long gelés, aucun dividende réinvesti"
                + (" — année électorale 2037" if annee == 10 else "")
            ),
            annee_electorale_majeure=(annee == 10),
            usure_politique_pts=min(70.0, 30.0 + (annee - 6) * 10.0),
            **_REGIME_CROISIERE,
        )
        for annee in range(6, 11)
    ]
    trajectoire = premiere + seconde
    for decision in trajectoire:
        decision.horizon_deux_mandatures = True
        decision.entretien_capital_public_mde = 6.0
        decision.effort_adaptation_climat_mde = 1.0
        decision.reformes_structurelles_actives = 6.0
        if decision.annee <= 5:
            # Même investissement de départ avant le scrutin de 2032.
            decision.capital_humain_mde = 2.0
            decision.montee_capacite_defense_mde = 2.0
    return trajectoire


def get_scenario_statut_quo() -> list[DecisionPolitique]:
    """Scénario du Statut Quo : aucune réforme d'envergure, immobilisme."""
    return [
        DecisionPolitique(annee=i, description=f"Année {i} : Statut Quo (Immobilisme politique)")
        for i in range(1, 6)
    ]


def get_scenario_austerite_brutale() -> list[DecisionPolitique]:
    """Scénario d'austérité aveugle : coupes dans la DGF et dégradation des services."""
    return [
        DecisionPolitique(
            annee=i,
            description=f"Année {i} : Austérité brutale (-10 Md€ dotations DGF, coupes hôpitaux)",
            delta_dotation_dgf_mde=-8.0,
            fusion_doublons_territoriaux_mde=2.0,
            baisse_tva_energie_5_5_mde=0.0,
        )
        for i in range(1, 6)
    ]


def get_scenario_choc_mondial_stagflation() -> list[DecisionPolitique]:
    """
    Scénario de crise et de stress-test mondial :
    Choc pétrolier exogène (+30 $/bbl), dépréciation de l'euro (-0.08) et resserrement Fed (+75 bps).
    Permet de tester la robustesse des amortisseurs et des stabilisateurs du modèle.
    """
    return [
        DecisionPolitique(
            annee=1,
            description="Année 1 : Choc mondial d'offre (Pétrole 112.5 $/bbl, dépréciation EUR/USD, Fed +75 bps)",
            choc_petrole_brent_usd=30.0,
            choc_change_eur_usd=-0.08,
            choc_taux_fed_bps=75.0,
            baisse_tva_energie_5_5_mde=9.0,  # Bouclier d'urgence activé
            recettes_pilier2_ocde_mde=3.0,
            recettes_macf_carbone_mde=2.0,
            taxe_superprofits_rachats_mde=6.0,
            extension_ttf_mde=5.0,
        ),
        DecisionPolitique(
            annee=2,
            description="Année 2 : Persistance du choc mondial et montée en charge des recettes de régulation",
            choc_petrole_brent_usd=20.0,
            choc_change_eur_usd=-0.05,
            choc_taux_fed_bps=50.0,
            baisse_tva_energie_5_5_mde=9.0,
            recettes_fraude_ia_mde=5.0,
            conditionnement_aides_entreprises_mde=4.0,
            recettes_pilier2_ocde_mde=4.5,
            recettes_macf_carbone_mde=3.0,
            taxe_superprofits_rachats_mde=6.0,
            extension_ttf_mde=5.0,
        ),
        DecisionPolitique(
            annee=3,
            description="Année 3 : Stabilisation des marchés mondiaux et absorption par les réformes structurelles",
            choc_petrole_brent_usd=10.0,
            choc_change_eur_usd=-0.02,
            choc_taux_fed_bps=25.0,
            baisse_tva_energie_5_5_mde=9.0,
            recettes_fraude_ia_mde=8.0,
            conditionnement_aides_entreprises_mde=8.0,
            recettes_pilier2_ocde_mde=5.0,
            recettes_macf_carbone_mde=3.5,
            fusion_doublons_territoriaux_mde=5.0,
            commande_publique_massifiee_mde=4.0,
        ),
    ]


# =============================================================================
# SCÉNARIOS DE LA STRATE 5 — GÉOPOLITIQUE, SÉCURITÉ & CHOKEPOINTS
# (comblent les simulations rendues impossibles avant l'ajout de la strate 5 :
#  cf. docs/ANALYSE_TENSION_GLOBALE_2026.md §5, §7 et §9)
# =============================================================================


def get_scenario_crise_taiwan() -> list[DecisionPolitique]:
    """
    Scénario A — Cascade Taïwan (2027-2028), probabilité 15-25 %.

    Quarantaine maritime de la Garde côtière chinoise (an 1), blocus assumé et
    frappes sur les fonderies (an 2), désescalade partielle et relocalisation
    européenne des capacités de gravure (an 3 à 5).
    """
    return [
        DecisionPolitique(
            annee=1,
            description="Année 1 : Quarantaine maritime chinoise autour de Taïwan (CCG + PLAN en soutien)",
            delta_tension_taiwan=18.0,
            delta_convergence_blocs=8.0,
            blocus_taiwan_intensite=0.35,
            plan_souverainete_semiconducteurs_mde=6.0,
            effort_defense_cible_pct_pib=2.35,
            activation_clause_sauvegarde_nationale_ue=True,
            baisse_tva_energie_5_5_mde=9.0,
            taxe_superprofits_rachats_mde=6.0,
            extension_ttf_mde=5.0,
        ),
        DecisionPolitique(
            annee=2,
            description="Année 2 : Blocus total et frappes sur les fonderies (TSMC Hsinchu/Tainan)",
            delta_tension_taiwan=14.0,
            delta_convergence_blocs=10.0,
            blocus_taiwan_intensite=0.90,
            plan_souverainete_semiconducteurs_mde=10.0,
            effort_defense_cible_pct_pib=2.70,
            mobilisation_economie_de_guerre=True,
            activation_clause_sauvegarde_nationale_ue=True,
            baisse_tva_energie_5_5_mde=9.0,
            recettes_fraude_ia_mde=5.0,
            taxe_superprofits_rachats_mde=6.0,
            extension_ttf_mde=5.0,
            recettes_pilier2_ocde_mde=4.0,
        ),
        DecisionPolitique(
            annee=3,
            description="Année 3 : Rationnement des puces, Chips Act accéléré et redémarrage partiel",
            delta_tension_taiwan=-6.0,
            blocus_taiwan_intensite=0.60,
            plan_souverainete_semiconducteurs_mde=12.0,
            effort_defense_cible_pct_pib=2.95,
            activation_clause_sauvegarde_nationale_ue=True,
            baisse_tva_energie_5_5_mde=9.0,
            recettes_fraude_ia_mde=8.0,
            conditionnement_aides_entreprises_mde=8.0,
            fusion_doublons_territoriaux_mde=5.0,
            commande_publique_massifiee_mde=4.0,
            extinction_niches_inefficaces_mde=7.0,
        ),
        DecisionPolitique(
            annee=4,
            description="Année 4 : Détente négociée, souveraineté industrielle européenne consolidée",
            delta_tension_taiwan=-12.0,
            blocus_taiwan_intensite=0.25,
            plan_souverainete_semiconducteurs_mde=10.0,
            effort_defense_cible_pct_pib=3.20,
            activation_clause_sauvegarde_nationale_ue=True,
            baisse_tva_energie_5_5_mde=9.0,
            recettes_fraude_ia_mde=9.0,
            conditionnement_aides_entreprises_mde=12.0,
            fusion_doublons_territoriaux_mde=6.5,
            commande_publique_massifiee_mde=5.0,
            extinction_niches_inefficaces_mde=7.0,
        ),
        DecisionPolitique(
            annee=5,
            description="Année 5 : Sortie de crise — capacité de gravure souveraine et cible OTAN tenue",
            delta_tension_taiwan=-10.0,
            blocus_taiwan_intensite=0.0,
            plan_souverainete_semiconducteurs_mde=8.0,
            effort_defense_cible_pct_pib=3.50,
            activation_clause_sauvegarde_nationale_ue=True,
            baisse_tva_energie_5_5_mde=9.0,
            recettes_fraude_ia_mde=10.0,
            conditionnement_aides_entreprises_mde=15.0,
            fusion_doublons_territoriaux_mde=8.0,
            commande_publique_massifiee_mde=6.0,
            extinction_niches_inefficaces_mde=7.0,
            fraude_sociale_criminelle_mde=3.0,
        ),
    ]


def get_scenario_fermeture_hormuz() -> list[DecisionPolitique]:
    """
    Scénario C — Guerre régionale Iran-Israël-US et fermeture du détroit d'Hormuz.

    Calibrage : -15 à -20 % d'offre mondiale -> Brent 160 à 195 $, PIB France
    -0,42 % (modélisation PSE 2026), déstockage stratégique AIE en réponse.
    """
    return [
        DecisionPolitique(
            annee=1,
            description="Année 1 : Fermeture quasi totale d'Hormuz (20 % du pétrole mondial), Brent > 150 $",
            delta_tension_iran_hormuz=15.0,
            fermeture_hormuz_intensite=0.90,
            liberation_stocks_strategiques=True,
            baisse_tva_energie_5_5_mde=9.0,
            effort_defense_cible_pct_pib=2.40,
            activation_clause_sauvegarde_nationale_ue=True,
            taxe_superprofits_rachats_mde=6.0,
            extension_ttf_mde=5.0,
            recettes_macf_carbone_mde=2.0,
        ),
        DecisionPolitique(
            annee=2,
            description="Année 2 : Déminage et convois escortés — réouverture partielle du détroit",
            delta_tension_iran_hormuz=-5.0,
            fermeture_hormuz_intensite=0.45,
            liberation_stocks_strategiques=True,
            baisse_tva_energie_5_5_mde=9.0,
            effort_defense_cible_pct_pib=2.55,
            activation_clause_sauvegarde_nationale_ue=True,
            recettes_fraude_ia_mde=5.0,
            taxe_superprofits_rachats_mde=6.0,
            extension_ttf_mde=5.0,
            recettes_pilier2_ocde_mde=4.5,
            recettes_macf_carbone_mde=3.0,
        ),
        DecisionPolitique(
            annee=3,
            description="Année 3 : Normalisation des flux, reconstitution des réserves stratégiques",
            delta_tension_iran_hormuz=-12.0,
            fermeture_hormuz_intensite=0.10,
            baisse_tva_energie_5_5_mde=9.0,
            effort_defense_cible_pct_pib=2.70,
            recettes_fraude_ia_mde=8.0,
            conditionnement_aides_entreprises_mde=8.0,
            fusion_doublons_territoriaux_mde=5.0,
            commande_publique_massifiee_mde=4.0,
            extinction_niches_inefficaces_mde=7.0,
        ),
        DecisionPolitique(
            annee=4,
            description="Année 4 : Sortie de choc énergétique et retour à la trajectoire d'ajustement",
            delta_tension_iran_hormuz=-8.0,
            baisse_tva_energie_5_5_mde=9.0,
            effort_defense_cible_pct_pib=2.85,
            recettes_fraude_ia_mde=9.0,
            conditionnement_aides_entreprises_mde=12.0,
            fusion_doublons_territoriaux_mde=6.5,
            commande_publique_massifiee_mde=5.0,
            extinction_niches_inefficaces_mde=7.0,
            fraude_sociale_criminelle_mde=2.5,
        ),
        DecisionPolitique(
            annee=5,
            description="Année 5 : Souveraineté énergétique renforcée, stocks reconstitués à 98 jours",
            delta_tension_iran_hormuz=-10.0,
            baisse_tva_energie_5_5_mde=9.0,
            effort_defense_cible_pct_pib=3.00,
            recettes_fraude_ia_mde=10.0,
            conditionnement_aides_entreprises_mde=15.0,
            fusion_doublons_territoriaux_mde=8.0,
            commande_publique_massifiee_mde=6.0,
            extinction_niches_inefficaces_mde=7.0,
            fraude_sociale_criminelle_mde=3.0,
        ),
    ]


def get_scenario_escalade_nucleaire_tactique() -> list[DecisionPolitique]:
    """
    Scénario B — Escalade Ukraine-Russie vers l'OTAN et usage d'une arme
    nucléaire tactique en Europe de l'Est (probabilité 10-20 % d'ici fin 2026).

    Stress-test ultime du modèle : il vérifie que les stabilisateurs tiennent et
    que les agrégats restent bornés et finis dans la pire configuration connue.
    """
    return [
        DecisionPolitique(
            annee=1,
            description="Année 1 : Escalade conventionnelle OTAN-Russie, menace nucléaire explicite",
            delta_tension_ukraine_otan=16.0,
            delta_convergence_blocs=12.0,
            cyberattaque_systemique=True,
            effort_defense_cible_pct_pib=3.00,
            mobilisation_economie_de_guerre=True,
            activation_clause_sauvegarde_nationale_ue=True,
            baisse_tva_energie_5_5_mde=9.0,
            taxe_superprofits_rachats_mde=6.0,
            extension_ttf_mde=5.0,
        ),
        DecisionPolitique(
            annee=2,
            description="Année 2 : Franchissement du seuil — frappe nucléaire tactique sur le front",
            delta_tension_ukraine_otan=13.0,
            delta_convergence_blocs=10.0,
            usage_nucleaire_tactique=True,
            fermeture_hormuz_intensite=0.30,
            liberation_stocks_strategiques=True,
            effort_defense_cible_pct_pib=4.00,
            mobilisation_economie_de_guerre=True,
            activation_clause_sauvegarde_nationale_ue=True,
            baisse_tva_energie_5_5_mde=9.0,
            recettes_fraude_ia_mde=5.0,
            taxe_superprofits_rachats_mde=6.0,
            extension_ttf_mde=5.0,
        ),
        DecisionPolitique(
            annee=3,
            description="Année 3 : Sanctuarisation, cessez-le-feu armé et économie de guerre durable",
            delta_tension_ukraine_otan=-8.0,
            effort_defense_cible_pct_pib=4.20,
            mobilisation_economie_de_guerre=True,
            activation_clause_sauvegarde_nationale_ue=True,
            liberation_stocks_strategiques=True,
            baisse_tva_energie_5_5_mde=9.0,
            recettes_fraude_ia_mde=8.0,
            conditionnement_aides_entreprises_mde=8.0,
            fusion_doublons_territoriaux_mde=5.0,
            commande_publique_massifiee_mde=4.0,
            extinction_niches_inefficaces_mde=7.0,
        ),
        DecisionPolitique(
            annee=4,
            description="Année 4 : Reconstruction, défiance persistante des marchés souverains",
            delta_tension_ukraine_otan=-10.0,
            delta_convergence_blocs=-6.0,
            effort_defense_cible_pct_pib=4.00,
            activation_clause_sauvegarde_nationale_ue=True,
            baisse_tva_energie_5_5_mde=9.0,
            recettes_fraude_ia_mde=9.0,
            conditionnement_aides_entreprises_mde=12.0,
            fusion_doublons_territoriaux_mde=6.5,
            commande_publique_massifiee_mde=5.0,
            extinction_niches_inefficaces_mde=7.0,
            fraude_sociale_criminelle_mde=2.5,
        ),
        DecisionPolitique(
            annee=5,
            description="Année 5 : Désescalade négociée, retour progressif des investisseurs",
            delta_tension_ukraine_otan=-14.0,
            delta_convergence_blocs=-8.0,
            effort_defense_cible_pct_pib=3.60,
            activation_clause_sauvegarde_nationale_ue=True,
            baisse_tva_energie_5_5_mde=9.0,
            recettes_fraude_ia_mde=10.0,
            conditionnement_aides_entreprises_mde=15.0,
            fusion_doublons_territoriaux_mde=8.0,
            commande_publique_massifiee_mde=6.0,
            extinction_niches_inefficaces_mde=7.0,
            fraude_sociale_criminelle_mde=3.0,
        ),
    ]


def get_scenario_convergence_ww3() -> list[DecisionPolitique]:
    """
    Scénario D — Convergence Chine-Russie-Iran (probabilité 5-10 %, impact maximal).

    Trois théâtres s'embrasent simultanément : blocus de Taïwan, offensive russe
    en Europe de l'Est avec franchissement nucléaire tactique, fermeture du Golfe.
    C'est le pire cas modélisable : il sert de borne supérieure de risque.
    """
    return [
        DecisionPolitique(
            annee=1,
            description="Année 1 : Embrasement simultané des trois théâtres (Taïwan, Europe, Golfe)",
            delta_tension_taiwan=20.0,
            delta_tension_ukraine_otan=18.0,
            delta_tension_iran_hormuz=14.0,
            delta_convergence_blocs=30.0,
            blocus_taiwan_intensite=0.70,
            fermeture_hormuz_intensite=0.70,
            cyberattaque_systemique=True,
            liberation_stocks_strategiques=True,
            effort_defense_cible_pct_pib=3.50,
            mobilisation_economie_de_guerre=True,
            activation_clause_sauvegarde_nationale_ue=True,
            plan_souverainete_semiconducteurs_mde=10.0,
            baisse_tva_energie_5_5_mde=9.0,
            taxe_superprofits_rachats_mde=6.0,
            extension_ttf_mde=5.0,
        ),
        DecisionPolitique(
            annee=2,
            description="Année 2 : Guerre mondiale ouverte — frappe nucléaire tactique et Golfe fermé",
            delta_tension_taiwan=10.0,
            delta_tension_ukraine_otan=12.0,
            delta_tension_iran_hormuz=8.0,
            delta_convergence_blocs=15.0,
            blocus_taiwan_intensite=1.00,
            fermeture_hormuz_intensite=1.00,
            usage_nucleaire_tactique=True,
            cyberattaque_systemique=True,
            liberation_stocks_strategiques=True,
            effort_defense_cible_pct_pib=5.00,
            mobilisation_economie_de_guerre=True,
            activation_clause_sauvegarde_nationale_ue=True,
            plan_souverainete_semiconducteurs_mde=15.0,
            baisse_tva_energie_5_5_mde=9.0,
            taxe_superprofits_rachats_mde=6.0,
            extension_ttf_mde=5.0,
        ),
        DecisionPolitique(
            annee=3,
            description="Année 3 : Économie de guerre généralisée, rationnement et dirigisme d'urgence",
            blocus_taiwan_intensite=0.80,
            fermeture_hormuz_intensite=0.60,
            liberation_stocks_strategiques=True,
            effort_defense_cible_pct_pib=5.00,
            mobilisation_economie_de_guerre=True,
            activation_clause_sauvegarde_nationale_ue=True,
            plan_souverainete_semiconducteurs_mde=15.0,
            baisse_tva_energie_5_5_mde=9.0,
            recettes_fraude_ia_mde=8.0,
            conditionnement_aides_entreprises_mde=10.0,
            taxe_superprofits_rachats_mde=10.0,
            extension_ttf_mde=6.0,
            fusion_doublons_territoriaux_mde=6.0,
            commande_publique_massifiee_mde=6.0,
            extinction_niches_inefficaces_mde=8.0,
        ),
        DecisionPolitique(
            annee=4,
            description="Année 4 : Armistice fragmenté, reconstruction des chaînes d'approvisionnement",
            delta_tension_taiwan=-15.0,
            delta_tension_ukraine_otan=-15.0,
            delta_tension_iran_hormuz=-12.0,
            delta_convergence_blocs=-15.0,
            blocus_taiwan_intensite=0.35,
            fermeture_hormuz_intensite=0.20,
            effort_defense_cible_pct_pib=4.50,
            activation_clause_sauvegarde_nationale_ue=True,
            plan_souverainete_semiconducteurs_mde=12.0,
            baisse_tva_energie_5_5_mde=9.0,
            recettes_fraude_ia_mde=9.0,
            conditionnement_aides_entreprises_mde=12.0,
            fusion_doublons_territoriaux_mde=7.0,
            commande_publique_massifiee_mde=6.0,
            extinction_niches_inefficaces_mde=8.0,
        ),
        DecisionPolitique(
            annee=5,
            description="Année 5 : Ordre mondial recomposé, souveraineté industrielle et énergétique acquise",
            delta_tension_taiwan=-18.0,
            delta_tension_ukraine_otan=-18.0,
            delta_tension_iran_hormuz=-15.0,
            delta_convergence_blocs=-20.0,
            effort_defense_cible_pct_pib=4.00,
            activation_clause_sauvegarde_nationale_ue=True,
            plan_souverainete_semiconducteurs_mde=10.0,
            baisse_tva_energie_5_5_mde=9.0,
            recettes_fraude_ia_mde=10.0,
            conditionnement_aides_entreprises_mde=15.0,
            taxe_superprofits_rachats_mde=8.0,
            extension_ttf_mde=6.0,
            fusion_doublons_territoriaux_mde=8.0,
            commande_publique_massifiee_mde=6.0,
            extinction_niches_inefficaces_mde=8.0,
            fraude_sociale_criminelle_mde=3.0,
        ),
    ]


def get_scenario_resilience_republicaine() -> list[DecisionPolitique]:
    """
    Scénario de synthèse — « Résilience républicaine » : le Plan de Mandature
    (+60 Md€/an) AUGMENTÉ de la trajectoire OTAN de La Haye (2,10 % -> 3,50 % du
    PIB de défense, soit ~ +0,28 pt/an), de la souveraineté semi-conducteurs et
    de la clause de sauvegarde nationale, SANS choc de guerre déclenché.

    C'est la simulation qui était strictement impossible avant la strate 5 :
    « peut-on réarmer au niveau exigé par l'OTAN tout en sortant de la PDE
    et en restituant du pouvoir d'achat ? »
    """
    base = get_scenario_mandature_5_ans()
    trajectoire_defense = [2.38, 2.66, 2.94, 3.22, 3.50]
    plans_semis = [4.0, 6.0, 8.0, 8.0, 6.0]
    for i, dec in enumerate(base):
        dec.description = f"{dec.description} + réarmement OTAN ({trajectoire_defense[i]:.2f} % PIB)"
        dec.effort_defense_cible_pct_pib = trajectoire_defense[i]
        dec.plan_souverainete_semiconducteurs_mde = plans_semis[i]
        dec.activation_clause_sauvegarde_nationale_ue = True
        dec.recettes_pilier2_ocde_mde = 3.0 + i * 0.5
        dec.recettes_macf_carbone_mde = 2.0 + i * 0.4
    return base
