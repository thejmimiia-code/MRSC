"""
simulateur/geopolitique_annuelle.py — STRATE 5 : GÉOPOLITIQUE, SÉCURITÉ & CHAÎNES D'APPROVISIONNEMENT.

Cette strate comble les éléments manquants identifiés par le document de R&D
`docs/ANALYSE_TENSION_GLOBALE_2026.md` (§9 « Recommandations de suivi EVA ») :

  1. `tension_strait_taiwan` -> impact semi-conducteurs & production industrielle ;
  2. `risque_nucleaire`      -> coût économique massif en cas de déclenchement ;
  3. métriques de convergence Chine-Russie-Iran (exercices conjoints, axe anti-OTAN).

Elle ajoute également les dimensions qui rendaient certaines simulations
**impossibles** jusqu'ici :

  * points de passage stratégiques (Hormuz, Malacca, Taïwan, Suez, Bab el-Mandeb,
    Gibraltar, Panama) et fermeture partielle/totale ;
  * effort de défense et trajectoire OTAN de La Haye (3,5 % + 1,5 % = 5 % du PIB
    à horizon 2035, soit ~ +0,15 pt de PIB/an pour la France) ;
  * clause de sauvegarde nationale du Pacte de stabilité (dérogation défense) ;
  * souveraineté semi-conducteurs (Chips Act / relocalisation) ;
  * guerre cyber-systémique et réserves stratégiques pétrolières (AIE, 90 j mini).

Calibrages sourcés :
  * SIPRI 2026 : 12 187 têtes nucléaires, 4 012 déployées, 83 % USA+Russie.
  * Sommet OTAN de La Haye (24-25 juin 2025) : 3,5 % PIB « défense dure »
    + 1,5 % « sécurité élargie » d'ici 2035 (France ~2,1 % à l'instant T).
  * Blocage d'Hormuz : -15 % d'offre mondiale -> ~160 $/bbl ; -20 % -> ~195 $/bbl
    (élasticité-prix de la demande de pétrole = -0,1).
  * PSE/CEPII-Fontagné (2026) : fermeture d'Hormuz -> commerce mondial -3,1 %,
    PIB mondial -0,54 %, PIB France -0,42 %.
  * Taïwan : ~60 % des semi-conducteurs mondiaux, 85-90 % des nœuds < 7 nm,
    blocus -> choc d'offre > 1 pt de PIB pour les économies avancées.
  * Multiplicateur budgétaire de défense : 0,6 à 1,0 (Ramey 2019, Ilzetzki 2025,
    OCDE 2026) ; 1,27 à 1,68 selon le MinArm pour la France (borne haute retenue
    uniquement en économie de guerre assumée).
"""

from dataclasses import dataclass, field

AVERTISSEMENT_GEOPOLITIQUE = (
    "Modèle exploratoire : les scores d'escalade et de risque nucléaire sont des indices "
    "heuristiques non calibrés, pas des probabilités mesurées. Les coefficients post-nucléaires "
    "du scénario annuel sont conventionnels ; le laboratoire mensuel arrête ses projections "
    "à un emploi imposé. Les règles PDE sont simplifiées, sans décision juridique automatique."
)

# =============================================================================
# CONSTANTES DE CALIBRAGE (instant T : octobre 2026)
# =============================================================================

BRENT_REFERENCE_USD = 82.5          # Référence du modèle (strate mondiale)
PART_PETROLE_HORMUZ_PCT = 20.0      # 20 % du pétrole + GNL mondial transite par Hormuz
PRIME_PETROLE_HORMUZ_TOTALE = 78.0  # $/bbl ajoutés par une fermeture totale et durable
PART_SEMICONDUCTEURS_TAIWAN = 60.0  # % de la production mondiale
PERTE_PIB_BLOCUS_TOTAL_PCT = 1.25   # Perte de PIB France pour une rupture totale des semis
PERTE_PIB_NUCLEAIRE_TACTIQUE = 4.20 # Perte de PIB France (an 1) après usage nucléaire tactique
EFFORT_DEFENSE_INSTANT_T_PCT = 2.10 # Effort de défense français à l'instant T (% du PIB)
CIBLE_OTAN_DEFENSE_PCT = 3.50       # Plancher « défense dure » de La Haye (2035)
CIBLE_OTAN_SECURITE_ELARGIE_PCT = 5.00
PLAFOND_CLAUSE_SAUVEGARDE_PCT = 1.50  # Dérogation PSC maximale pour l'effort de défense


# =============================================================================
# POINTS DE PASSAGE STRATÉGIQUES (CHOKEPOINTS)
# =============================================================================

@dataclass
class PointDePassageStrategique:
    """Détroit ou canal dont la fermeture déstabilise les chaînes mondiales."""
    nom: str
    part_commerce_mondial_pct: float
    criticite: float                       # Pondération de l'impact macro (1.0 = référence)
    taux_ouverture_pct: float = 100.0      # 100 = trafic normal, 0 = fermeture totale

    @property
    def sous_tension(self) -> bool:
        return self.taux_ouverture_pct < 95.0


def chokepoints_par_defaut() -> list[PointDePassageStrategique]:
    """Cartographie des 7 verrous mondiaux (cf. §4 de l'analyse de tension 2026)."""
    return [
        PointDePassageStrategique("Détroit d'Hormuz", 20.0, 1.00),
        PointDePassageStrategique("Détroit de Malacca", 25.0, 0.55),
        PointDePassageStrategique("Détroit de Taïwan", 50.0, 0.90),
        PointDePassageStrategique("Canal de Suez", 12.0, 0.45),
        PointDePassageStrategique("Bab el-Mandeb", 5.0, 0.30),
        PointDePassageStrategique("Détroit de Gibraltar", 32.0, 0.35),
        PointDePassageStrategique("Canal de Panama", 4.0, 0.15),
    ]


# =============================================================================
# STRATE 5 : ÉCHELON GÉOPOLITIQUE
# =============================================================================

@dataclass
class EchelonGeopolitique:
    """Strate des conflits, de la dissuasion, des chokepoints et de l'effort de défense."""

    # --- Indices de tension des 4 théâtres majeurs (0-100) -------------------
    tension_taiwan: float = 62.0                 # Risque Janes 7 % / fenêtre 2027 (centenaire APL)
    tension_ukraine_otan: float = 71.0           # Doctrine russe abaissée + tactiques en Biélorussie
    tension_iran_israel_us: float = 78.0         # Cessez-le-feu de juin 2026 non consolidé
    convergence_chine_russie_iran: float = 45.0  # Exercices conjoints, accord stratégique 2025

    # --- Dissuasion nucléaire (SIPRI, janvier 2026) --------------------------
    tetes_nucleaires_mondiales: int = 12187
    tetes_nucleaires_deployees: int = 4012
    tetes_nucleaires_france: int = 290
    risque_usage_nucleaire_tactique_pct: float = 12.0
    usage_nucleaire_constate: bool = False

    # --- Chaînes d'approvisionnement -----------------------------------------
    chokepoints: list[PointDePassageStrategique] = field(default_factory=chokepoints_par_defaut)
    disponibilite_semiconducteurs_pct: float = 100.0
    capacite_souveraine_semiconducteurs_mde: float = 0.0   # Cumul des plans de relocalisation
    stocks_strategiques_petrole_jours: float = 98.0        # Obligation AIE : 90 jours minimum

    # --- Défense & résilience nationale --------------------------------------
    effort_defense_pct_pib: float = EFFORT_DEFENSE_INSTANT_T_PCT
    depenses_defense_mde: float = 63.3                     # 2,10 % de 3 015 Md€
    economie_de_guerre_active: bool = False
    indice_cyber_resilience: float = 61.0                  # 0-100 (ANSSI / NIS2)
    clause_sauvegarde_nationale_active: bool = False       # Dérogation défense du PSC

    # --- Agrégats de sortie ---------------------------------------------------
    prime_risque_geopolitique_bps: float = 12.0
    # Prime déjà incorporée dans le spread OAT-Bund de 88 bps à l'instant T : seule la
    # fraction EXCÉDENTAIRE est réinjectée dans la strate 4 (pas de double comptage).
    prime_risque_geopolitique_reference_bps: float = 0.0
    probabilite_escalade_mondiale_pct: float = 0.0
    prime_petrole_geopolitique_usd: float = 0.0            # Prime courante retirée/réappliquée

    def __post_init__(self) -> None:
        if self.prime_risque_geopolitique_reference_bps <= 0.0:
            self.prime_risque_geopolitique_reference_bps = round(
                12.0 + max(0.0, (self.indice_tension_globale - 55.0) * 1.35), 2
            )

    # ------------------------------------------------------------------ #
    @property
    def indice_tension_globale(self) -> float:
        """Indice composite 0-100 pondéré par la capacité d'escalade de chaque théâtre."""
        brut = (
            self.tension_taiwan * 0.30
            + self.tension_ukraine_otan * 0.28
            + self.tension_iran_israel_us * 0.22
            + self.convergence_chine_russie_iran * 0.20
        )
        return round(min(100.0, max(0.0, brut)), 1)

    @property
    def nombre_chokepoints_sous_tension(self) -> int:
        return sum(1 for c in self.chokepoints if c.sous_tension)

    def get_chokepoint(self, nom_partiel: str) -> PointDePassageStrategique | None:
        cible = nom_partiel.casefold()
        for c in self.chokepoints:
            if cible in c.nom.casefold():
                return c
        return None


# =============================================================================
# RÉSULTAT DE PROPAGATION DE LA STRATE 5 VERS LES STRATES 1 À 4
# =============================================================================

@dataclass
class EffetsGeopolitiques:
    """Vecteur d'impacts transmis par la strate 5 au reste du modèle."""
    prime_petrole_usd: float = 0.0            # Ajout au Brent ($/bbl)
    choc_pib_mde: float = 0.0                 # Perte (<0) ou gain (>0) de PIB nominal
    inflation_additionnelle_pct: float = 0.0  # Points d'IPC importés supplémentaires
    prime_spread_bps: float = 0.0             # Prime de risque souverain géopolitique
    surcout_defense_mde: float = 0.0          # Dépense publique supplémentaire (hors base)
    tension_sociale_delta: float = 0.0        # Points d'indice de tension territoriale
    confiance_delta: float = 0.0              # Points de confiance démocratique
    derogation_pde_pct_pib: float = 0.0       # Déficit neutralisé au titre de la clause défense
    degradation_notation: bool = False
    commentaires: list[str] = field(default_factory=list)


def _clip(valeur: float, mini: float = 0.0, maxi: float = 100.0) -> float:
    return max(mini, min(maxi, valeur))


def propager_geopolitique(geo: EchelonGeopolitique, decision, pib_tendanciel_mde: float) -> EffetsGeopolitiques:
    """
    Applique une décision/un choc géopolitique annuel à la strate 5 et
    renvoie le vecteur d'effets à injecter dans les strates 1 à 4.

    La fonction est **déterministe mais modifie son état** : la prime
    pétrolière géopolitique courante est recalculée en niveau (et non cumulée),
    ce qui garantit la non-divergence des stress-tests longs.
    """
    eff = EffetsGeopolitiques()
    eff.commentaires.append(AVERTISSEMENT_GEOPOLITIQUE)

    # ------------------------------------------------------------------ #
    # 1. Mise à jour des indices de tension des théâtres
    # ------------------------------------------------------------------ #
    geo.tension_taiwan = _clip(geo.tension_taiwan + decision.delta_tension_taiwan)
    geo.tension_ukraine_otan = _clip(geo.tension_ukraine_otan + decision.delta_tension_ukraine_otan)
    geo.tension_iran_israel_us = _clip(geo.tension_iran_israel_us + decision.delta_tension_iran_hormuz)
    geo.convergence_chine_russie_iran = _clip(
        geo.convergence_chine_russie_iran + decision.delta_convergence_blocs
    )

    # ------------------------------------------------------------------ #
    # 2. Chokepoint d'Hormuz : choc d'offre pétrolière et gazière
    # ------------------------------------------------------------------ #
    intensite_hormuz = _clip(decision.fermeture_hormuz_intensite, 0.0, 1.0)
    hormuz = geo.get_chokepoint("Hormuz")
    if hormuz is not None:
        hormuz.taux_ouverture_pct = round(100.0 * (1.0 - intensite_hormuz), 1)

    if intensite_hormuz > 0.0:
        prime = PRIME_PETROLE_HORMUZ_TOTALE * intensite_hormuz
        if decision.liberation_stocks_strategiques and geo.stocks_strategiques_petrole_jours > 60.0:
            # Déstockage coordonné AIE : absorbe ~30 % du choc initial, au prix des réserves
            jours_consommes = min(25.0, geo.stocks_strategiques_petrole_jours - 60.0)
            geo.stocks_strategiques_petrole_jours = round(
                geo.stocks_strategiques_petrole_jours - jours_consommes, 1
            )
            prime *= 0.70
            eff.commentaires.append(
                f"[Strate 5 - Énergie] Libération des réserves stratégiques (-{jours_consommes:.0f} j, "
                f"stock à {geo.stocks_strategiques_petrole_jours:.0f} j) : choc pétrolier amorti de 30 %."
            )
        eff.prime_petrole_usd += prime
        # Effet volume PSE/CEPII : -0,42 % de PIB France pour une fermeture totale
        eff.choc_pib_mde -= pib_tendanciel_mde * 0.0042 * intensite_hormuz
        eff.tension_sociale_delta += 6.0 * intensite_hormuz
        eff.commentaires.append(
            f"[Strate 5 - Chokepoint] Détroit d'Hormuz ouvert à {hormuz.taux_ouverture_pct:.0f} % "
            f"({PART_PETROLE_HORMUZ_PCT:.0f} % du pétrole mondial) -> prime de {prime:+.1f} $/bbl sur le Brent."
        )
    else:
        geo.stocks_strategiques_petrole_jours = min(98.0, geo.stocks_strategiques_petrole_jours + 6.0)

    # ------------------------------------------------------------------ #
    # 3. Blocus de Taïwan : choc semi-conducteurs et fret maritime
    # ------------------------------------------------------------------ #
    intensite_taiwan = _clip(decision.blocus_taiwan_intensite, 0.0, 1.0)
    detroit_taiwan = geo.get_chokepoint("Taïwan")
    if detroit_taiwan is not None:
        detroit_taiwan.taux_ouverture_pct = round(100.0 * (1.0 - intensite_taiwan), 1)

    geo.capacite_souveraine_semiconducteurs_mde += decision.plan_souverainete_semiconducteurs_mde
    # Chips Act : 40 Md€ cumulés amortissent au mieux 50 % du choc d'approvisionnement
    attenuation_souverainete = min(0.50, geo.capacite_souveraine_semiconducteurs_mde / 80.0)

    if intensite_taiwan > 0.0:
        perte_appro = 70.0 * intensite_taiwan * (1.0 - attenuation_souverainete)
        geo.disponibilite_semiconducteurs_pct = round(_clip(100.0 - perte_appro), 1)
        eff.choc_pib_mde -= pib_tendanciel_mde * (PERTE_PIB_BLOCUS_TOTAL_PCT / 100.0) * (perte_appro / 70.0)
        eff.inflation_additionnelle_pct += 0.030 * perte_appro
        eff.tension_sociale_delta += 4.0 * intensite_taiwan
        eff.commentaires.append(
            f"[Strate 5 - Taïwan] Blocus à {intensite_taiwan * 100:.0f} % : disponibilité des semi-conducteurs "
            f"à {geo.disponibilite_semiconducteurs_pct:.0f} % (Taïwan = {PART_SEMICONDUCTEURS_TAIWAN:.0f} % de l'offre mondiale), "
            f"amortissement souverain {attenuation_souverainete * 100:.0f} %."
        )
    else:
        geo.disponibilite_semiconducteurs_pct = 100.0
        if decision.plan_souverainete_semiconducteurs_mde > 0:
            eff.commentaires.append(
                f"[Strate 5 - Souveraineté] Plan semi-conducteurs : {geo.capacite_souveraine_semiconducteurs_mde:.1f} Md€ "
                f"cumulés -> résilience de {attenuation_souverainete * 100:.0f} % face à un blocus du détroit."
            )

    # ------------------------------------------------------------------ #
    # 4. Franchissement du seuil nucléaire tactique
    # ------------------------------------------------------------------ #
    composite = geo.indice_tension_globale
    geo.risque_usage_nucleaire_tactique_pct = round(
        _clip(2.0 + (composite - 50.0) * 0.55 + geo.convergence_chine_russie_iran * 0.12), 1
    )

    if decision.usage_nucleaire_tactique:
        geo.usage_nucleaire_constate = True
        geo.risque_usage_nucleaire_tactique_pct = 100.0
        eff.prime_petrole_usd += 55.0
        eff.choc_pib_mde -= pib_tendanciel_mde * (PERTE_PIB_NUCLEAIRE_TACTIQUE / 100.0)
        eff.inflation_additionnelle_pct += 3.20
        eff.prime_spread_bps += 180.0
        eff.tension_sociale_delta += 30.0
        eff.confiance_delta -= 18.0
        eff.degradation_notation = True
        eff.commentaires.append(
            "[Strate 5 - NUCLÉAIRE] Franchissement du seuil : usage d'une arme nucléaire tactique en Europe. "
            "Choc d'offre énergétique majeur, fuite vers la qualité, effondrement de la prime de risque européenne."
        )
    elif geo.usage_nucleaire_constate:
        # Rémanence du choc les années suivantes (reconstruction, défiance durable)
        eff.choc_pib_mde -= pib_tendanciel_mde * 0.012
        eff.prime_spread_bps += 60.0
        eff.tension_sociale_delta += 8.0

    # ------------------------------------------------------------------ #
    # 5. Guerre cyber-systémique
    # ------------------------------------------------------------------ #
    if decision.cyberattaque_systemique:
        attenuation_cyber = geo.indice_cyber_resilience / 100.0
        perte = pib_tendanciel_mde * 0.0075 * (1.0 - attenuation_cyber * 0.6)
        eff.choc_pib_mde -= perte
        eff.prime_spread_bps += 18.0
        eff.tension_sociale_delta += 5.0
        eff.confiance_delta -= 4.0
        eff.commentaires.append(
            f"[Strate 5 - Cyber] Attaque systémique sur les OIV (énergie, santé, paiements) : "
            f"-{perte:.1f} Md€ de PIB, résilience ANSSI/NIS2 à {geo.indice_cyber_resilience:.0f}/100."
        )

    # ------------------------------------------------------------------ #
    # 6. Effort de défense & trajectoire OTAN de La Haye
    # ------------------------------------------------------------------ #
    if decision.effort_defense_cible_pct_pib > 0.0:
        geo.effort_defense_pct_pib = round(decision.effort_defense_cible_pct_pib, 2)
    geo.depenses_defense_mde = round(pib_tendanciel_mde * geo.effort_defense_pct_pib / 100.0, 2)
    depense_base = pib_tendanciel_mde * EFFORT_DEFENSE_INSTANT_T_PCT / 100.0
    eff.surcout_defense_mde = round(max(0.0, geo.depenses_defense_mde - depense_base), 2)

    geo.economie_de_guerre_active = bool(decision.mobilisation_economie_de_guerre)
    if eff.surcout_defense_mde > 0.0:
        # Multiplicateur budgétaire de défense : 0,75 en régime normal (Ramey/Ilzetzki/OCDE),
        # 1,10 en économie de guerre assumée (cadences industrielles, commandes pluriannuelles).
        multiplicateur = 1.10 if geo.economie_de_guerre_active else 0.75
        eff.choc_pib_mde += eff.surcout_defense_mde * multiplicateur
        eff.confiance_delta += min(5.0, eff.surcout_defense_mde * 0.08)
        if geo.economie_de_guerre_active:
            eff.inflation_additionnelle_pct += 0.20
        eff.commentaires.append(
            f"[Strate 5 - Défense] Effort porté à {geo.effort_defense_pct_pib:.2f} % du PIB "
            f"({geo.depenses_defense_mde:.1f} Md€, +{eff.surcout_defense_mde:.1f} Md€) — trajectoire de La Haye "
            f"{CIBLE_OTAN_DEFENSE_PCT:.1f} % d'ici 2035 ; multiplicateur budgétaire retenu {multiplicateur:.2f}."
        )

    # ------------------------------------------------------------------ #
    # 7. Clause de sauvegarde nationale du Pacte de stabilité (dérogation défense)
    # ------------------------------------------------------------------ #
    geo.clause_sauvegarde_nationale_active = bool(decision.activation_clause_sauvegarde_nationale_ue)
    if geo.clause_sauvegarde_nationale_active and pib_tendanciel_mde > 0:
        eff.derogation_pde_pct_pib = round(
            min(PLAFOND_CLAUSE_SAUVEGARDE_PCT, (eff.surcout_defense_mde / pib_tendanciel_mde) * 100.0), 3
        )
        eff.commentaires.append(
            f"[Strate 3/5 - Europe] Clause de sauvegarde nationale activée : "
            f"{eff.derogation_pde_pct_pib:.2f} pt de PIB de dépenses de défense exclus de l'évaluation PDE "
            f"(plafond {PLAFOND_CLAUSE_SAUVEGARDE_PCT:.1f} pt)."
        )

    # ------------------------------------------------------------------ #
    # 8. Prime de risque souverain géopolitique & probabilité d'escalade mondiale
    # ------------------------------------------------------------------ #
    prime_tension = max(0.0, (composite - 55.0) * 1.35)
    prime_chokepoints = geo.nombre_chokepoints_sous_tension * 6.0
    geo.prime_risque_geopolitique_bps = round(
        min(260.0, 12.0 + prime_tension + prime_chokepoints + eff.prime_spread_bps), 1
    )
    eff.prime_spread_bps = round(
        max(0.0, geo.prime_risque_geopolitique_bps - geo.prime_risque_geopolitique_reference_bps), 1
    )

    # Probabilité d'escalade mondiale (scénario D : convergence multi-théâtres)
    theatres_chauds = sum(
        1 for t in (geo.tension_taiwan, geo.tension_ukraine_otan, geo.tension_iran_israel_us) if t >= 80.0
    )
    geo.probabilite_escalade_mondiale_pct = round(
        _clip(
            0.35 * max(0.0, composite - 45.0)
            + 6.0 * theatres_chauds
            + 0.22 * geo.convergence_chine_russie_iran
            + (35.0 if geo.usage_nucleaire_constate else 0.0)
        ),
        1,
    )
    eff.commentaires.append(
        f"[Strate 5 - Risque global] Indice de tension composite {composite:.1f}/100 "
        f"(Taïwan {geo.tension_taiwan:.0f} | Ukraine-OTAN {geo.tension_ukraine_otan:.0f} | "
        f"Iran-Israël-US {geo.tension_iran_israel_us:.0f} | Convergence {geo.convergence_chine_russie_iran:.0f}) "
        f"-> indice heuristique d'escalade {geo.probabilite_escalade_mondiale_pct:.1f}/100, "
        f"indice nucléaire {geo.risque_usage_nucleaire_tactique_pct:.1f}/100, "
        f"prime souveraine géopolitique {geo.prime_risque_geopolitique_bps:.0f} bps."
    )

    return eff
