"""
simulateur/moteur.py — Moteur de simulation systémique à poupées russes (4 strates interconnectées).
Calé rigoureusement sur les données et contraintes à l'instant T (AFT, INSEE, Eurostat, CGCT).
"""

import math

from simulateur.geopolitique_annuelle import (
    EchelonGeopolitique,
    propager_geopolitique,
)
from simulateur.model import (
    DecisionPolitique,
    EchelonEuropeen,
    EchelonLocal,
    EchelonMondial,
    EchelonNational,
    ResultatEtapeSimulation,
)

#: Délai de maturité des investissements à cycle long (années).
#: Hypothèse R&D « deux mandatures consécutives » (docs/RD_DOUBLE_MANDATURE.md,
#: point P6) : EPR2, lois de programmation militaire, prévention santé, recherche…
#: le coût est payé tout de suite, le rendement n'arrive qu'à maturité (courbe en J).
DELAI_MATURITE_INVESTISSEMENTS = 5

#: Rendement annuel d'un investissement à cycle long mature (part de PIB ajoutée
#: par Md€ investi) et plafond par programme, pour éviter toute divergence sur
#: les horizons longs. Calibrage exploratoire, pas une prévision.
RENDEMENT_INVESTISSEMENTS_MATURES = 0.08
PLAFOND_RENDEMENT_PAR_PROGRAMME_MDE = 2.5

#: Phase 2 — hypothèses de scénario (docs/RD_DOUBLE_MANDATURE.md, P16-P21).
#: La Cour des comptes estime à 140-150 Md€ les besoins d'investissement des
#: bâtiments publics à l'horizon 2050. Simple annualisation centrale sur 24 ans
#: (2026-2050), PAS un besoin d'entretien officiel ni une dette observée.
BESOIN_ANNUALISE_CAPITAL_PUBLIC_MDE = 145.0 / 24.0
#: Un délai exploratoire de huit ans rend visibles, à l'horizon de deux
#: mandatures, des investissements d'éducation/formation à cycle long. Il
#: n'encode aucun taux de rendement macroéconomique.
DELAI_MATURITE_CAPITAL_HUMAIN = 8
#: Six ans, fenêtre d'une LPM (2024-2030), utilisée comme proxy de montée en
#: capacité — pas une durée moyenne officielle de tous les programmes BITD.
DELAI_MATURITE_CAPACITES_DEFENSE = 6
#: PNACC-3 estime à 143 Md€ les sinistres climatiques cumulés 2020-2050.
#: Leur annualisation uniforme (143/30) est un repère de scénario, pas une
#: trajectoire annuelle observée ni une dépense des administrations publiques.
DOMMAGES_CLIMAT_ANNUALISES_MDE = 143.0 / 30.0
#: Le PNACC-3 rapporte, pour les projets soutenus par le fonds Barnier, 1 €
#: investi pour 8 € de dommages évités. Annualisation illustrative sur 30 ans ;
#: ce ratio ne se généralise pas à toutes les dépenses d'adaptation.
RENDEMENT_PREVENTION_ANNUALISE = 8.0 / 30.0
#: Seuil de saturation administratif utilisé pour un stress-test, sans valeur
#: officielle universelle : à faire varier en analyse de sensibilité.
SEUIL_SATURATION_ADMINISTRATIVE = 8


class MoteurSimulationSystemique:
    """
    Simulateur de politique macro-économique, institutionnelle et financière.
    Modélise les flux rétroactifs complets :
    Décision -> Local -> Social -> National -> Parlement -> Europe -> Marchés -> Réinjection
    """

    def __init__(
        self,
        local: EchelonLocal = None,
        national: EchelonNational = None,
        europe: EchelonEuropeen = None,
        mondial: EchelonMondial = None,
        geo: EchelonGeopolitique = None,
    ):
        self.local = local or EchelonLocal()
        self.national = national or EchelonNational()
        self.europe = europe or EchelonEuropeen()
        self.mondial = mondial or EchelonMondial()
        self.geo = geo or EchelonGeopolitique()
        self.historique_etapes: list[ResultatEtapeSimulation] = []

        # ── Références de calibrage « instant T » ─────────────────────────────
        # Centralisées ici pour que `moteur_parametrique.calibrer_contexte` puisse
        # recaler le moteur sur des données publiques réelles sans toucher à la
        # logique causale. Les valeurs par défaut reproduisent le calage du projet
        # (septembre 2026) : les tests et scénarios historiques sont inchangés.
        self.reference: dict[str, float] = {
            "brent_usd": 82.5,
            "eur_usd": 1.08,
            "inflation_pct": 2.1,
            "taux_oat_pct": 4.18,
            "taux_bund_pct": 3.30,
            "taux_credit_immobilier_pct": 3.85,
            "spread_bps": 88.0,
            "facture_energetique_mde": 64.5,
            "recettes_base_mde": 1565.0,
            "depenses_primaires_mde": 1718.0,
            "effort_structurel_cible_mde": 50.0,
        }

        # État cumulatif des réformes constitutionnelles et civiques
        self.reforme_casier_b2_active = False
        self.reforme_vote_blanc_active = False
        self.reforme_ric_active = False
        self.reforme_regimes_speciaux_active = False
        self.reforme_anti_pantouflage_active = False
        self.reforme_non_cumul_active = False

        # ── Profondeur temporelle : deux mandatures consécutives ─────────────
        # Registre des investissements à cycle long : (année de maturité, Md€).
        # Le rendement n'est compté qu'à maturité, jamais avant (courbe en J).
        self.investissements_differes: list[tuple[int, float]] = []
        # Phase 2 (points P16-P21) : registres explicites de scénarios longs.
        self.dette_technique_infrastructures_mde: float = 0.0
        self.stock_adaptation_climat_mde: float = 0.0
        self.investissements_capital_humain: list[tuple[int, float]] = []
        self.investissements_capacites_defense: list[tuple[int, float]] = []

    def _capital_humain_mature(self, annee: int) -> float:
        """Investissements éducatifs arrivés à maturité (proxy en Md€), P18."""
        return round(sum(
            montant for annee_maturite, montant in self.investissements_capital_humain
            if annee >= annee_maturite
        ), 2)

    def _capacites_defense_matures(self, annee: int) -> float:
        """Investissements BITD arrivés à maturité (proxy en Md€), P19."""
        return round(sum(
            montant for annee_maturite, montant in self.investissements_capacites_defense
            if annee >= annee_maturite
        ), 2)

    def _investissements_matures(self, annee: int) -> tuple[float, float]:
        """Stock mature (Md€) et rendement annuel (Md€ de PIB) à l'année donnée.

        Chaque programme investi rapporte, une fois mature,
        `RENDEMENT_INVESTISSEMENTS_MATURES` Md€ de PIB par Md€ investi et par an,
        plafonné à `PLAFOND_RENDEMENT_PAR_PROGRAMME_MDE` par programme.
        """
        stock_mature = 0.0
        rendement = 0.0
        for annee_maturite, montant in self.investissements_differes:
            if annee >= annee_maturite:
                stock_mature += montant
                rendement += min(
                    PLAFOND_RENDEMENT_PAR_PROGRAMME_MDE,
                    montant * RENDEMENT_INVESTISSEMENTS_MATURES,
                )
        return round(stock_mature, 2), round(rendement, 2)

    def appliquer_etape(
        self, decision: DecisionPolitique, *, facteur_activite: float = 1.0
    ) -> ResultatEtapeSimulation:
        """
        Exécute la chaîne causale multi-strates pour un exercice fiscal.
        """
        # Pont R&D optionnel : facteur de niveau relatif à la trajectoire de référence.
        # Ne modifie ni le PIB de base ni les décisions politiques ; neutre par défaut.
        if (isinstance(facteur_activite, bool) or not math.isfinite(facteur_activite)
                or not 0 < facteur_activite <= 1):
            raise ValueError("facteur_activite doit être fini et dans ]0, 1]")
        commentaires: list[str] = []

        # =========================================================================
        # 0. CHOCS MONDIAUX (Matières Premières, Devises, Taux Mondiaux) & PIB
        # =========================================================================
        # -------------------------------------------------------------------------
        # 0.a STRATE 5 : GÉOPOLITIQUE (conflits, chokepoints, dissuasion, défense)
        # La strate 5 est résolue EN PREMIER : elle alimente les chocs d'offre
        # (pétrole, semi-conducteurs), la prime de risque souverain et l'effort
        # de défense avant toute propagation vers les strates 4 -> 1.
        # -------------------------------------------------------------------------
        pib_tendanciel = self.national.pib_nominal_mde * (
            (1.0 + self.national.taux_croissance_potentiel) ** (decision.annee - 1)
        )
        pib_tendanciel *= facteur_activite
        effets_geo = propager_geopolitique(self.geo, decision, pib_tendanciel)
        commentaires.extend(effets_geo.commentaires)

        # Prime pétrolière géopolitique appliquée EN NIVEAU (retrait puis réapplication)
        # afin de garantir l'idempotence et la non-divergence des stress-tests longs.
        self.mondial.cours_petrole_brent_usd = max(
            35.0,
            round(
                self.mondial.cours_petrole_brent_usd
                - self.geo.prime_petrole_geopolitique_usd
                + effets_geo.prime_petrole_usd,
                2,
            ),
        )
        self.geo.prime_petrole_geopolitique_usd = effets_geo.prime_petrole_usd

        # Renchérissement du fret maritime conteneurisé en cas de chokepoint fermé
        if self.geo.nombre_chokepoints_sous_tension > 0:
            self.mondial.indice_fret_maritime_scfi = round(
                2450.0 + 850.0 * self.geo.nombre_chokepoints_sous_tension, 1
            )
        else:
            self.mondial.indice_fret_maritime_scfi = 2450.0

        # Prise en compte des chocs exogènes mondiaux (Pétrole Brent, EUR/USD).
        # Les chocs sont appliqués EN NIVEAU : le choc de l'année précédente est
        # d'abord retiré, puis le nouveau est appliqué. Sans ce retrait, un choc
        # maintenu sur 5 ans s'accumulerait (un Brent à +45 $ pendant cinq ans
        # finissait à +225 $) et la trajectoire divergerait.
        memo = getattr(self, "_chocs_appliques", None)
        if memo is None:
            memo = self._chocs_appliques = {}

        choc_petrole = round(decision.choc_petrole_brent_usd, 3)
        if choc_petrole != memo.get("petrole", 0.0):
            self.mondial.cours_petrole_brent_usd = max(
                35.0,
                round(self.mondial.cours_petrole_brent_usd
                      - memo.get("petrole", 0.0) + choc_petrole, 2),
            )
            memo["petrole"] = choc_petrole
            if choc_petrole != 0.0:
                commentaires.append(
                    f"[Strate 4 - Mondial] Choc pétrolier exogène : Brent à {self.mondial.cours_petrole_brent_usd:.1f} $/bbl ({choc_petrole:+.1f} $)."
                )

        choc_change = round(decision.choc_change_eur_usd, 4)
        if choc_change != memo.get("change", 0.0):
            self.mondial.taux_change_eur_usd = max(
                0.75,
                round(self.mondial.taux_change_eur_usd
                      - memo.get("change", 0.0) + choc_change, 4),
            )
            memo["change"] = choc_change
            if choc_change != 0.0:
                commentaires.append(
                    f"[Strate 4 - Forex] Choc de change : Parité EUR/USD à {self.mondial.taux_change_eur_usd:.3f} ({choc_change:+.3f})."
                )

        # Calcul de la facture énergétique nationale nette (importations nettes d'hydrocarbures)
        delta_brent = self.mondial.cours_petrole_brent_usd - self.reference["brent_usd"]
        delta_change = self.mondial.taux_change_eur_usd - self.reference["eur_usd"]
        delta_facture = (delta_brent / 10.0) * 4.50 - (delta_change / 0.05) * 2.80
        self.mondial.facture_energetique_nette_mde = max(
            25.0, round(self.reference["facture_energetique_mde"] + delta_facture, 2)
        )

        # Inflation globale française (IPC) répercutant l'énergie mondiale et le bouclier TVA 5,5%
        surcroit_inflation_energie = (delta_facture / 10.0) * 0.45
        rabais_inflation_tva = (decision.baisse_tva_energie_5_5_mde / 9.0) * 0.35
        self.mondial.inflation_globale_pct = max(
            0.5,
            round(
                self.reference["inflation_pct"]
                + surcroit_inflation_energie
                - rabais_inflation_tva
                + effets_geo.inflation_additionnelle_pct,
                2,
            ),
        )

        # Croissance nominale tendancielle du PIB
        pib_t = self.national.pib_nominal_mde * ((1.0 + self.national.taux_croissance_potentiel) ** (decision.annee - 1)) * facteur_activite

        # Multiplicateurs keynésiens différenciés :
        # - Rentes/Fraude/Superprofits/Pilier2 : multiplicateur récessif très faible (-0.12)
        # - Baisse de TVA énergie : multiplicateur d'expansion de la consommation (+0.75)
        # - Coupes dans les dotations aux collectivités : multiplicateur récessif fort (-0.85)
        # - Choc d'inflation importée sur l'activité : impact récessif (-0.25 par point d'inflation au-dessus de 2%)
        impact_choc_inflation = -max(0.0, (self.mondial.inflation_globale_pct - 2.0) * 3.5)
        stock_investissements_matures, rendement_investissements_matures = (
            self._investissements_matures(decision.annee)
        )
        stock_capital_humain_mature = self._capital_humain_mature(decision.annee)
        stock_capacites_defense_matures = self._capacites_defense_matures(decision.annee)
        impact_multiplicateur = (
            (decision.baisse_tva_energie_5_5_mde * 0.75)
            - ((decision.recettes_fraude_ia_mde + decision.taxe_superprofits_rachats_mde + decision.extension_ttf_mde + decision.recettes_pilier2_ocde_mde + decision.recettes_macf_carbone_mde) * 0.12)
            + (decision.delta_dotation_dgf_mde * 0.85 if decision.delta_dotation_dgf_mde < 0 else 0)
            + impact_choc_inflation
            + effets_geo.choc_pib_mde
            # Leviers libres du simulateur interactif : la dépense publique a un
            # multiplicateur positif (0,55), les recettes nouvelles un effet
            # légèrement récessif (−0,12), comme les prélèvements existants.
            + (decision.depenses_prioritaires_mde * 0.55)
            - (decision.recettes_nouvelles_mde * 0.12)
            # Deux mandatures consécutives : le « second dividende » de la dette
            # (baisse de charge refinancée, réinvestie) agit comme une dépense
            # publique financée sans déficit, et les investissements à cycle
            # long de la mandature 1 arrivent à maturité en mandature 2
            # (rendement différé, courbe en J).
            + (decision.reinvestissement_dividende_dette_mde * 0.55)
            + rendement_investissements_matures
        )
        pib_annee = round(max(500.0, pib_t + impact_multiplicateur), 2)

        # =========================================================================
        # 1. STRATE LOCALE (Règle d'or CGCT art. L. 1612-4 & Fiscalité foncière)
        # =========================================================================
        # Répartition de la DGF versée par l'État
        part_dgf_communes = decision.delta_dotation_dgf_mde * 0.45
        part_dgf_departements = decision.delta_dotation_dgf_mde * 0.37
        part_dgf_regions = decision.delta_dotation_dgf_mde * 0.18

        self.local.bloc_communal.dgf_recue_mde += part_dgf_communes
        self.local.departements.dgf_departementale_mde += part_dgf_departements
        self.local.regions.dgf_regionale_mde += part_dgf_regions

        # Effet direct des leviers libres sur le climat social : lever l'impôt
        # tend la société (+0,012 pt de tension par Md€), dépenser l'apaise
        # (−0,006 pt par Md€), avant les effets propres à chaque politique.
        self.local.tension_sociale_territoriale = min(
            100.0,
            max(
                0.0,
                self.local.tension_sociale_territoriale
                + decision.recettes_nouvelles_mde * 0.012
                - decision.depenses_prioritaires_mde * 0.006,
            ),
        )

        if decision.delta_dotation_dgf_mde < 0:
            # Transfert de charges : les collectivités ont l'interdiction d'emprunter pour fonctionner
            perte_dgf = abs(decision.delta_dotation_dgf_mde)
            hausse_taxe_fonciere = perte_dgf * 0.94
            self.local.bloc_communal.taxe_fonciere_tfpb_mde += hausse_taxe_fonciere
            # La hausse de taxe foncière frappe directement les classes moyennes propriétaires
            self.local.tension_sociale_territoriale += hausse_taxe_fonciere * 1.6
            commentaires.append(
                f"[Strate 1 - Local CGCT] Baisse DGF de {perte_dgf:.1f} Md€ -> Report forcé sur la taxe foncière (+{hausse_taxe_fonciere:.1f} Md€) et grogne locale."
            )

        # Surcoût énergétique pour les collectivités territoriales (chauffage, éclairage, cantines, bus)
        if delta_facture > 0:
            surcout_energie_collectivites = delta_facture * 0.06
            self.local.bloc_communal.depenses_fonctionnement_mde += surcout_energie_collectivites * 0.50
            self.local.departements.depenses_colleges_et_routes_mde += surcout_energie_collectivites * 0.25
            self.local.regions.depenses_transports_ter_mde += surcout_energie_collectivites * 0.25
            self.local.tension_sociale_territoriale += surcout_energie_collectivites * 0.70

        if decision.fusion_doublons_territoriaux_mde > 0:
            # Économie de gestion sur les sièges administratifs sans fermer aucun guichet
            gain_qualite = decision.fusion_doublons_territoriaux_mde * 1.6
            self.local.qualite_services_proximite = min(100.0, 64.0 + gain_qualite)
            commentaires.append(
                f"[Strate 1 - Local] Mutualisation des sièges région/département : redéploiement d'agents vers le terrain (+{gain_qualite:.1f} pts services)."
            )

        # =========================================================================
        # 2. IMPACT SOCIAL & POUVOIR D'ACHAT (Ménages & Probité Républicaine)
        # =========================================================================
        if decision.baisse_tva_energie_5_5_mde > 0:
            gain_pouvoir_achat = decision.baisse_tva_energie_5_5_mde
            self.national.pouvoir_achat_menages_index = 100.0 + (gain_pouvoir_achat / 9.0) * 3.8
            self.local.tension_sociale_territoriale = max(5.0, self.local.tension_sociale_territoriale - 9.5)
            commentaires.append(
                f"[Pouvoir d'Achat] Baisse TVA énergie à 5,5 % -> +{gain_pouvoir_achat:.1f} Md€ de pouvoir d'achat net pour les ménages (Tension -9.5 pts)."
            )

        # Impact négatif de l'inflation sur le pouvoir d'achat
        if self.mondial.inflation_globale_pct > 2.0:
            erosion_inflation = (self.mondial.inflation_globale_pct - 2.0) * 1.4
            self.national.pouvoir_achat_menages_index = max(70.0, self.national.pouvoir_achat_menages_index - erosion_inflation)
            self.local.tension_sociale_territoriale = min(100.0, self.local.tension_sociale_territoriale + erosion_inflation * 1.8)

        # Réformes constitutionnelles et civiques
        if decision.reforme_casier_b2:
            self.reforme_casier_b2_active = True
            commentaires.append("[Démocratie] Casier B2 vierge obligatoire activé pour les candidats.")
        if decision.reforme_vote_blanc_invalidant:
            self.reforme_vote_blanc_active = True
            commentaires.append("[Démocratie] Vote blanc invalidant instauré avec délai de carence 12 mois.")
        if decision.reforme_ric_souverain:
            self.reforme_ric_active = True
            self.local.tension_sociale_territoriale = max(5.0, self.local.tension_sociale_territoriale - 12.0)
            commentaires.append("[Démocratie] RIC souverain en vigueur -> apaisement démocratique profond.")
        if decision.reforme_fin_regimes_speciaux:
            self.reforme_regimes_speciaux_active = True
        if decision.reforme_anti_pantouflage_lobbys:
            self.reforme_anti_pantouflage_active = True
        if decision.reforme_non_cumul_mandats:
            self.reforme_non_cumul_active = True

        gains_civiques = 0.0
        if self.reforme_casier_b2_active:
            gains_civiques += 10.0
        if self.reforme_vote_blanc_active:
            gains_civiques += 8.0
        if self.reforme_ric_active:
            gains_civiques += 14.0
        if self.reforme_regimes_speciaux_active:
            gains_civiques += 6.0
        if self.reforme_anti_pantouflage_active:
            gains_civiques += 7.0
        if self.reforme_non_cumul_active:
            gains_civiques += 5.0

        self.national.confiance_democratique = min(100.0, 27.5 + gains_civiques)

        # Rétroaction de la strate 5 sur le corps social et la confiance institutionnelle
        if effets_geo.tension_sociale_delta != 0.0:
            self.local.tension_sociale_territoriale = min(
                100.0, max(0.0, self.local.tension_sociale_territoriale + effets_geo.tension_sociale_delta)
            )
        if effets_geo.confiance_delta != 0.0:
            self.national.confiance_democratique = min(
                100.0, max(0.0, self.national.confiance_democratique + effets_geo.confiance_delta)
            )

        # ── PROFONDEUR TEMPORELLE : DEUX MANDATURES CONSÉCUTIVES ─────────────
        # Dynamiques propres à la période de dix ans (docs/RD_DOUBLE_MANDATURE.md) :
        # usure du capital politique, année électorale, verrou constitutionnel,
        # clauses de revoyure et « second dividende » de la dette. Tous ces effets
        # sont neutres tant que les champs dédiés de la décision restent à leurs
        # valeurs par défaut (scénarios quinquennaux inchangés).
        usure_politique = max(0.0, min(100.0, decision.usure_politique_pts))
        if usure_politique > 0.0:
            # La réforme de fatigue : l'usure érode la confiance et tend le climat
            # social, même sans nouvelle mesure impopulaire.
            self.national.confiance_democratique = max(
                0.0, self.national.confiance_democratique - usure_politique * 0.08
            )
            self.local.tension_sociale_territoriale = min(
                100.0, self.local.tension_sociale_territoriale + usure_politique * 0.06
            )
            commentaires.append(
                f"[Deux mandatures] Usure du capital politique à {usure_politique:.0f}/100 : "
                f"chaque réforme coûte désormais plus cher politiquement."
            )
        if decision.verrouillage_irreversibilite:
            # L'ancrage constitutionnel crédibilise la trajectoire : les marchés et
            # les citoyens savent qu'une alternance ne défera pas les réformes.
            self.national.confiance_democratique = min(
                100.0, self.national.confiance_democratique + 2.0
            )
            commentaires.append(
                "[Deux mandatures] Ancrage constitutionnel des réformes adopté : "
                "prime de crédibilité (+2 pts de confiance démocratique)."
            )
        if decision.clause_revoyure_evaluation:
            self.national.confiance_democratique = min(
                100.0, self.national.confiance_democratique + 1.0
            )
        if decision.reinvestissement_dividende_dette_mde > 0.0:
            # La baisse de la charge de la dette finance la restitution aux ménages :
            # c'est une dépense gagée, donc sans déficit supplémentaire, et elle
            # apaise le corps social.
            self.local.tension_sociale_territoriale = max(
                0.0,
                self.local.tension_sociale_territoriale
                - decision.reinvestissement_dividende_dette_mde * 0.3,
            )
            commentaires.append(
                f"[Deux mandatures] Second dividende : {decision.reinvestissement_dividende_dette_mde:.1f} Md€ "
                f"d'économies d'intérêts réinvestis en pouvoir d'achat et services publics."
            )

        # ───────────────────────────────────────────────────────────────────────
        # PROFONDEUR TEMPORELLE, PHASE 2 (R&D « deux mandatures », points P16-P21).
        # Chaque dynamique est neutre tant que son champ reste à sa valeur par
        # défaut, afin de préserver strictement les scénarios quinquennaux.
        # ───────────────────────────────────────────────────────────────────────

        # P16 : besoin de rattrapage du capital public (proxy annualisé, cf. doc).
        # Il n'est activé que si l'appel simule une période longue (>5 ans) ; le
        # stock est un besoin d'investissement non couvert, pas une dette comptable.
        entretien_mde = max(0.0, decision.entretien_capital_public_mde)
        if decision.horizon_deux_mandatures:
            self.dette_technique_infrastructures_mde = max(
                0.0,
                self.dette_technique_infrastructures_mde
                + BESOIN_ANNUALISE_CAPITAL_PUBLIC_MDE - entretien_mde,
            )
            if entretien_mde > 0.0 or self.dette_technique_infrastructures_mde > 0.0:
                commentaires.append(
                    f"[Deux mandatures, P16] Besoin annualisé de référence : "
                    f"{BESOIN_ANNUALISE_CAPITAL_PUBLIC_MDE:.2f} Md€ ; effort déclaré "
                    f"{entretien_mde:.1f} Md€ ; besoin non couvert cumulé (proxy) : "
                    f"{self.dette_technique_infrastructures_mde:.1f} Md€."
                )

        # P17 : exposition climatique. Le chiffre annualisé est un proxy de
        # pertes sociétales, distinct des dépenses APU : il n'est jamais ajouté
        # au déficit public. Le rendement du fonds Barnier est annualisé sur
        # 30 ans et constitue une hypothèse de scénario, pas un taux universel.
        dommages_climat_subis_mde = 0.0
        dommages_climat_evites_mde = 0.0
        if decision.horizon_deux_mandatures:
            self.stock_adaptation_climat_mde += max(
                0.0, decision.effort_adaptation_climat_mde
            )
            dommages_climat_subis_mde = DOMMAGES_CLIMAT_ANNUALISES_MDE
            dommages_climat_evites_mde = min(
                dommages_climat_subis_mde,
                self.stock_adaptation_climat_mde * RENDEMENT_PREVENTION_ANNUALISE,
            )
            if decision.effort_adaptation_climat_mde > 0.0:
                commentaires.append(
                    f"[Deux mandatures, P17] Risque annualisé : "
                    f"{dommages_climat_subis_mde:.2f} Md€ ; dommages évités estimés : "
                    f"{dommages_climat_evites_mde:.2f} Md€ (proxy hors déficit APU)."
                )

        # P18 : capital humain. On enregistre les cohortes de dépenses et leur
        # date de maturité exploratoire, sans inventer de rendement PIB.
        if decision.capital_humain_mde > 0.0:
            self.investissements_capital_humain.append(
                (decision.annee + DELAI_MATURITE_CAPITAL_HUMAIN,
                 decision.capital_humain_mde)
            )
        if stock_capital_humain_mature > 0.0:
            commentaires.append(
                f"[Deux mandatures, P18] Stock d'investissements éducatifs arrivé "
                f"à maturité (proxy) : {stock_capital_humain_mature:.1f} Md€."
            )

        # P19 : registre de montée en capacité BITD (délai LPM de référence).
        # Le stock est exposé, mais n'est pas converti arbitrairement en spread.
        if decision.montee_capacite_defense_mde > 0.0:
            self.investissements_capacites_defense.append(
                (decision.annee + DELAI_MATURITE_CAPACITES_DEFENSE,
                 decision.montee_capacite_defense_mde)
            )
        if stock_capacites_defense_matures > 0.0:
            commentaires.append(
                f"[Deux mandatures, P19] Stock d'investissements BITD arrivé "
                f"à maturité (proxy) : {stock_capacites_defense_matures:.1f} Md€."
            )

        # P20 : capacité d'exécution administrative. Le nombre simultané est un
        # paramètre explicite (non inféré de tous les interrupteurs du catalogue).
        # Le seuil et les effets ci-dessous sont des stress-test, non des valeurs
        # institutionnelles universelles.
        reformes_actives = max(0.0, decision.reformes_structurelles_actives)
        if reformes_actives > SEUIL_SATURATION_ADMINISTRATIVE:
            exces = reformes_actives - SEUIL_SATURATION_ADMINISTRATIVE
            self.local.tension_sociale_territoriale = min(
                100.0, self.local.tension_sociale_territoriale + exces * 0.3
            )
            self.national.confiance_democratique = max(
                0.0, self.national.confiance_democratique - exces * 0.15
            )
            commentaires.append(
                f"[Deux mandatures, P20] Charge simultanée : {reformes_actives:.0f} réformes "
                f"(seuil exploratoire : {SEUIL_SATURATION_ADMINISTRATIVE}) ; stress-test "
                "d'une capacité administrative saturée."
            )

        # =========================================================================
        # 3. STRATE NATIONALE (État, Sécurité Sociale, Déficit au sens de Maastricht)
        # =========================================================================
        # Nouvelles recettes fiscales de régulation (Volet 2 + International)
        recettes_volet2 = (
            decision.recettes_fraude_ia_mde
            + decision.conditionnement_aides_entreprises_mde
            + decision.taxe_superprofits_rachats_mde
            + decision.extension_ttf_mde
            + decision.recettes_pilier2_ocde_mde
            + decision.recettes_macf_carbone_mde
        )

        # Économies structurelles récurrentes (Volet 3)
        economies_volet3 = (
            decision.fusion_doublons_territoriaux_mde
            + decision.commande_publique_massifiee_mde
            + decision.extinction_niches_inefficaces_mde
            + decision.fraude_sociale_criminelle_mde
        )

        # Coût net de la baisse de TVA énergie
        cout_tva = decision.baisse_tva_energie_5_5_mde

        # Indexation des recettes fiscales de base sur la croissance du PIB nominal
        # (En réalité, la TVA, l'IR, l'IS et les cotisations suivent l'activité économique)
        pib_base = self.national.pib_nominal_mde
        # L'assiette fiscale suit l'activité réelle : les pertes (ou gains) de PIB induits
        # par la strate 5 (blocus, chokepoints, réarmement) se répercutent sur les recettes.
        indexation_pib = (pib_t + effets_geo.choc_pib_mde) / pib_base
        recettes_base_indexees = round(self.reference["recettes_base_mde"] * indexation_pib, 2)

        # Recettes publiques totales consolidées (APU)
        recettes_totales_apu = round(
            recettes_base_indexees + recettes_volet2 - cout_tva
            + decision.recettes_nouvelles_mde,
            2,
        )

        # Effort structurel net
        effort_structurel_net = (
            recettes_volet2 + economies_volet3 - cout_tva
            + decision.recettes_nouvelles_mde - decision.depenses_prioritaires_mde
        )

        # Stabilité parlementaire et risque de motion de censure
        if self.local.tension_sociale_territoriale > 65.0:
            # Forte contestation civique -> les députés centristes/indépendants basculent vers la censure
            self.national.parlement.probabilite_motion_censure_pct = min(95.0, 52.0 + (self.local.tension_sociale_territoriale - 65.0) * 2.2)
            commentaires.append(
                f"[Parlement] Alerte censure : probabilité de chute du cabinet à {self.national.parlement.probabilite_motion_censure_pct:.1f} %."
            )
        else:
            # Climat pacifié et confiance civique en hausse
            self.national.parlement.probabilite_motion_censure_pct = max(10.0, 52.0 - (self.national.confiance_democratique * 0.4))

        # Deux mandatures consécutives : l'usure du capital politique fragilise
        # la majorité (députés sortants hésitants, fronde interne).
        if usure_politique > 0.0:
            self.national.parlement.probabilite_motion_censure_pct = min(
                95.0,
                self.national.parlement.probabilite_motion_censure_pct + usure_politique * 0.15,
            )

        # =========================================================================
        # 4. STRATE MONDIALE (Agence France Trésor, Spreads, OAT 10 ans, Rating)
        # =========================================================================
        # Resserrement monétaire Fed -> transmission au Bund allemand
        delta_bund_fed = (decision.choc_taux_fed_bps / 100.0) * 0.40

        # Règle d'ajustement du spread souverain OAT-Bund et de la prime de risque
        if effort_structurel_net >= 50.0:
            # Trajectoire de désendettement crédible reconnue par les investisseurs :
            # Détente conjointe du taux sans risque de la Zone Euro (Bund) et contraction du spread français
            detente_bund = (effort_structurel_net / 60.0) * 0.50
            self.mondial.taux_bund_allemagne_10ans = max(
                2.50, round(self.reference["taux_bund_pct"] - detente_bund + delta_bund_fed, 2)
            )
            self.mondial.spread_oat_bund_bps = max(
                38.0, self.reference["spread_bps"] - (effort_structurel_net / 60.0) * 48.0
            )
            # Mémoire du risque : après un franchissement du seuil nucléaire, les agences
            # ne restituent pas immédiatement la catégorie AA (plancher post-choc : A-).
            self.mondial.note_souveraine = "A-" if self.geo.usage_nucleaire_constate else "AA"
            self.mondial.prime_risque_politique_bps = max(5.0, 25.0 - (self.national.confiance_democratique / 4.0))
        elif effort_structurel_net <= 0.0:
            # Dérive budgétaire et défiance
            self.mondial.taux_bund_allemagne_10ans = round(
                self.reference["taux_bund_pct"] + delta_bund_fed, 2
            )
            self.mondial.spread_oat_bund_bps = min(
                135.0, self.reference["spread_bps"] + decision.annee * 8.0
            )
            if self.mondial.spread_oat_bund_bps > 105.0:
                self.mondial.note_souveraine = "A+"
                commentaires.append(
                    "[Strate 4 - Marchés] Dégradation de la note souveraine à 'A+' -> Ventes forcées de fonds indiciels internationaux."
                )
        else:
            self.mondial.taux_bund_allemagne_10ans = round(3.30 + delta_bund_fed, 2)
            self.mondial.spread_oat_bund_bps = max(
                50.0, self.reference["spread_bps"] - (effort_structurel_net / 50.0) * 20.0
            )

        # Prime de risque géopolitique (strate 5) ajoutée AU SPREAD lui-même afin de
        # préserver strictement l'équation de parité OAT = Bund + spread / 100.
        if effets_geo.prime_spread_bps > 0.0:
            self.mondial.spread_oat_bund_bps = min(
                600.0, self.mondial.spread_oat_bund_bps + effets_geo.prime_spread_bps
            )

        # Deux mandatures consécutives : prime de risque électorale. Une année de
        # scrutin national général renchérit le crédit de l'État tant que les
        # réformes ne sont pas ancrées dans la Constitution (risque d'abrogation
        # par une alternance). Le verrou constitutionnel divise la prime par trois.
        if decision.annee_electorale_majeure:
            prime_electorale_bps = 4.0 if decision.verrouillage_irreversibilite else 12.0
            self.mondial.spread_oat_bund_bps = min(
                600.0, self.mondial.spread_oat_bund_bps + prime_electorale_bps
            )
            incertitude_sociale = 0.8 if decision.clause_revoyure_evaluation else 2.0
            self.local.tension_sociale_territoriale = min(
                100.0, self.local.tension_sociale_territoriale + incertitude_sociale
            )
            if not decision.verrouillage_irreversibilite:
                self.national.confiance_democratique = max(
                    0.0, self.national.confiance_democratique - 1.0
                )
            commentaires.append(
                f"[Deux mandatures] Année électorale majeure : prime d'incertitude de "
                f"{prime_electorale_bps:.0f} bps sur le spread souverain"
                + (" (réformes verrouillées)." if decision.verrouillage_irreversibilite
                   else " (réformes révocables : risque d'alternance).")
            )

        if effets_geo.degradation_notation:
            self.mondial.note_souveraine = "BBB+"
            commentaires.append(
                "[Strate 4 - Marchés] Guerre nucléaire tactique : dégradation souveraine à 'BBB+' et "
                "fermeture temporaire du marché primaire long (recours massif aux BTF court terme)."
            )
        elif self.mondial.spread_oat_bund_bps > 180.0 and self.mondial.note_souveraine != "BBB+":
            self.mondial.note_souveraine = "A"
            commentaires.append(
                "[Strate 4 - Marchés] Prime géopolitique > 180 bps : dégradation de la note souveraine à 'A'."
            )

        # Taux souverain OAT à 10 ans rigoureusement articulé au Bund et au spread
        self.mondial.taux_oat_france_10ans = round(self.mondial.taux_bund_allemagne_10ans + (self.mondial.spread_oat_bund_bps / 100.0), 2)

        # Transmission de l'OAT aux taux de crédit bancaire dans l'économie réelle
        self.mondial.taux_credit_pme_entreprises = round(self.mondial.taux_oat_france_10ans + 0.85, 2)
        self.mondial.taux_credit_immobilier_menages = round(
            self.reference["taux_credit_immobilier_pct"]
            + (self.mondial.taux_oat_france_10ans - self.reference["taux_oat_pct"]),
            2,
        )

        # Règle de sensibilité de la charge de la dette (AFT - roll-over de maturité moyenne 8.5 ans)
        # Transmission progressive : seulement ~35 % du changement de taux impacte la
        # charge d'intérêts de l'année courante (le reste est amorti via le roll-over sur 8.5 ans)
        ecart_taux_base = self.mondial.taux_oat_france_10ans - self.reference["taux_oat_pct"]
        ajustement_charge_interets = round(
            (ecart_taux_base * 11.5) * self.mondial.part_dette_refinancement_annuel_pct, 2
        )
        charge_dette_effective = max(48.0, round(self.national.etat.charge_nette_dette_mde + ajustement_charge_interets, 2))
        commentaires.append(
            f"[Strate 4 - Financement] Taux OAT à {self.mondial.taux_oat_france_10ans:.2f} % "
            f"-> charge d'intérêts ajustée de {ajustement_charge_interets:+.2f} Md€ "
            f"(transmission progressive {self.mondial.part_dette_refinancement_annuel_pct * 100:.0f} %, "
            f"maturité moyenne {self.mondial.maturite_moyenne_dette_ans:.1f} a)."
        )

        # Deux mandatures consécutives : les investissements à cycle long
        # (EPR2, lois de programmation militaire, prévention santé, recherche)
        # sont payés MAINTENANT — ils dégradent le solde à court terme (courbe
        # en J) — mais leur rendement n'arrive qu'à maturité, au-delà de cinq
        # ans, c'est-à-dire pendant la mandature suivante.
        if decision.investissements_cycle_long_mde > 0.0:
            annee_maturite = decision.annee + DELAI_MATURITE_INVESTISSEMENTS
            self.investissements_differes.append(
                (annee_maturite, decision.investissements_cycle_long_mde)
            )
            commentaires.append(
                f"[Deux mandatures] Investissement à cycle long de "
                f"{decision.investissements_cycle_long_mde:.1f} Md€ : coût immédiat, "
                f"rendement différé à partir de l'année {annee_maturite} (courbe en J)."
            )

        # Dépenses consolidées effectives des APU
        depenses_primaires_apu = (
            (self.reference["depenses_primaires_mde"] - self.national.etat.charge_nette_dette_mde)
            - economies_volet3
            + effets_geo.surcout_defense_mde
            + decision.depenses_prioritaires_mde
            + decision.investissements_cycle_long_mde
            # Phase 2 (P16-P19) : seuls les décaissements réellement choisis
            # entrent dans le budget APU. Les dommages climatiques évités sont
            # un indicateur sociétal distinct, pas une recette publique.
            + max(0.0, decision.entretien_capital_public_mde)
            + max(0.0, decision.effort_adaptation_climat_mde)
            + max(0.0, decision.capital_humain_mde)
            + max(0.0, decision.montee_capacite_defense_mde)
        )
        depenses_totales_apu = depenses_primaires_apu + charge_dette_effective

        # Déficit public nominal consolidé (au sens de Maastricht)
        deficit_net_consolide = round(depenses_totales_apu - recettes_totales_apu, 2)
        ratio_deficit_pib = round((deficit_net_consolide / pib_annee) * 100.0, 2)

        # Stock de dette publique au sens de Maastricht
        self.national.dette_maastricht_stock_mde += deficit_net_consolide
        ratio_dette_pib = round((self.national.dette_maastricht_stock_mde / pib_annee) * 100.0, 2)

        # =========================================================================
        # 5. STRATE CONTINENTALE / EUROPÉENNE (Pacte de Stabilité, TPI, Sanctions)
        # =========================================================================
        # Déficit retenu par la Commission pour l'évaluation PDE : la clause de sauvegarde
        # nationale (dérogation défense du Pacte de stabilité) en neutralise une fraction.
        ratio_deficit_pde = round(ratio_deficit_pib - effets_geo.derogation_pde_pct_pib, 2)
        if ratio_deficit_pde <= self.europe.seuil_deficit_pde_pct:
            self.europe.statut_pde_actif = False
            self.europe.bouclier_tpi_bce_eligible = True
            self.europe.amende_sanction_semestrielle_mde = 0.0
            commentaires.append(
                f"[Strate 3 - Europe] Déficit PDE à {ratio_deficit_pde:.2f} % <= 3.00 % : Sortie de la PDE et activation pleine du bouclier TPI de la BCE."
            )
        else:
            self.europe.statut_pde_actif = True
            # Sous le nouveau pacte, si l'ajustement structurel annuel est inférieur à 0.5% du PIB
            ajustement_realise_pct = (effort_structurel_net / pib_annee) * 100.0
            if ajustement_realise_pct >= self.europe.effort_structurel_requis_annuel_pct:
                self.europe.bouclier_tpi_bce_eligible = True
                commentaires.append(
                    f"[Strate 3 - Europe] Déficit à {ratio_deficit_pib:.2f} % : Trajectoire d'ajustement respectée (+{ajustement_realise_pct:.2f} % PIB)."
                )
            else:
                self.europe.bouclier_tpi_bce_eligible = False
                commentaires.append(
                    f"[Strate 3 - Europe] Alerte PDE : Ajustement insuffisant ({ajustement_realise_pct:.2f} % < 0.50 %) -> Risque d'astreinte financière."
                )

        # Bornage des indices sociaux : la tension est un indice 0-100, elle ne
        # peut pas « déborder » même sous chocs cumulés (défense en profondeur).
        self.local.tension_sociale_territoriale = min(
            100.0, max(0.0, self.local.tension_sociale_territoriale)
        )
        self.local.qualite_services_proximite = min(
            100.0, max(0.0, self.local.qualite_services_proximite)
        )
        self.national.confiance_democratique = min(
            100.0, max(0.0, self.national.confiance_democratique)
        )

        # =========================================================================
        # 6. INSTANTANÉ DE L'ÉTAPE CONSOLIDÉE
        # =========================================================================
        resultat = ResultatEtapeSimulation(
            annee=decision.annee,
            pib_nominal_mde=pib_annee,
            deficit_nominal_mde=deficit_net_consolide,
            ratio_deficit_pib=ratio_deficit_pib,
            dette_nominale_mde=round(self.national.dette_maastricht_stock_mde, 2),
            ratio_dette_pib=ratio_dette_pib,
            charge_dette_mde=charge_dette_effective,
            recettes_publiques_totales_mde=round(recettes_totales_apu, 2),
            depenses_publiques_totales_mde=round(depenses_totales_apu, 2),
            pouvoir_achat_index=round(self.national.pouvoir_achat_menages_index, 1),
            confiance_democratique=round(self.national.confiance_democratique, 1),
            risque_censure_parlement=round(self.national.parlement.probabilite_motion_censure_pct, 1),
            tension_sociale_locale=round(self.local.tension_sociale_territoriale, 1),
            qualite_services_proximite=round(self.local.qualite_services_proximite, 1),
            produit_taxe_fonciere_mde=round(self.local.bloc_communal.taxe_fonciere_tfpb_mde, 2),
            statut_pde_europe=self.europe.statut_pde_actif,
            bouclier_tpi_actif=self.europe.bouclier_tpi_bce_eligible,
            sanction_financiere_ue=self.europe.amende_sanction_semestrielle_mde > 0,
            taux_oat_pct=round(self.mondial.taux_oat_france_10ans, 2),
            spread_bund_bps=round(self.mondial.spread_oat_bund_bps, 1),
            note_souveraine=self.mondial.note_souveraine,
            taux_credit_pme=round(self.mondial.taux_credit_pme_entreprises, 2),
            taux_credit_immobilier_menages=round(self.mondial.taux_credit_immobilier_menages, 2),
            cours_petrole_usd=round(self.mondial.cours_petrole_brent_usd, 1),
            taux_change_eur_usd=round(self.mondial.taux_change_eur_usd, 3),
            facture_energetique_mde=round(self.mondial.facture_energetique_nette_mde, 1),
            inflation_globale_pct=round(self.mondial.inflation_globale_pct, 2),
            indice_tension_geopolitique=self.geo.indice_tension_globale,
            probabilite_escalade_mondiale_pct=round(self.geo.probabilite_escalade_mondiale_pct, 1),
            risque_nucleaire_tactique_pct=round(self.geo.risque_usage_nucleaire_tactique_pct, 1),
            disponibilite_semiconducteurs_pct=round(self.geo.disponibilite_semiconducteurs_pct, 1),
            effort_defense_pct_pib=round(self.geo.effort_defense_pct_pib, 2),
            depenses_defense_mde=round(self.geo.depenses_defense_mde, 2),
            prime_risque_geopolitique_bps=round(self.geo.prime_risque_geopolitique_bps, 1),
            chokepoints_sous_tension=self.geo.nombre_chokepoints_sous_tension,
            stocks_strategiques_petrole_jours=round(self.geo.stocks_strategiques_petrole_jours, 1),
            usure_politique_pts=round(usure_politique, 1),
            irreversibilite_reformes_active=bool(decision.verrouillage_irreversibilite),
            investissements_matures_mde=stock_investissements_matures,
            dette_technique_infrastructures_mde=round(self.dette_technique_infrastructures_mde, 2),
            entretien_capital_public_mde=round(max(0.0, decision.entretien_capital_public_mde), 2),
            dommages_climat_subis_mde=round(dommages_climat_subis_mde, 2),
            dommages_climat_evites_mde=round(dommages_climat_evites_mde, 2),
            capital_humain_mature_mde=stock_capital_humain_mature,
            capacites_defense_matures_mde=stock_capacites_defense_matures,
            investissements_longs_engages_cumules_mde=round(
                sum(montant for _, montant in self.investissements_differes)
                + sum(montant for _, montant in self.investissements_capital_humain)
                + sum(montant for _, montant in self.investissements_capacites_defense),
                2,
            ),
            reformes_structurelles_actives=reformes_actives,
            commentaires=commentaires,
        )

        self.historique_etapes.append(resultat)
        return resultat
