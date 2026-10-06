"""
simulateur/domaines.py — Domaines d'action publique et indicateurs d'impact.

Le moteur (`moteur.py`) calcule les 5 échelons systémiques (local, national,
européen, mondial, géopolitique). Ce module traduit ces résultats en **effets
concrets, domaine par domaine**, pour répondre à la question : « ce choix,
qu'est-ce qu'il change dans la vie réelle ? ».

Méthode (transparente et auditable)
-----------------------------------
1. Les leviers choisis sont convertis en **médiateurs** (`MediateursAnnee`) :
   dépenses et recettes nouvelles par destination, en milliards d'euros (Md€),
   effort de défense, prix de l'énergie, tension sociale, confiance, trajectoire
   de dette, etc.
2. Chaque indicateur de domaine est une fonction **linéaire documentée** des
   médiateurs :

       valeur = base × (1 + Σ coefficient × médiateur)      (unités en %)
       valeur = base + Σ coefficient × médiateur            (unités en points)

   Les coefficients sont exprimés **par milliard d'euros** ou **par point de
   PIB** selon le cas, affichés dans l'interface (`formule`) et sourcés
   (`source`) : ordres de grandeur issus d'élasticités publiées (loi d'Okun,
   multiplicateurs de dépense publique, élasticité-prix de l'énergie,
   rendements scolaires, effets de la pauvreté sur la santé…).
3. Un **score de domaine** (0-100, base 50) résume la trajectoire :
   `score = 50 + 50 × tanh(16 × Δ_relatif_signe)` (une variation relative moyenne
   de 3 % déplace le score d'environ 20 points, de 0,3 % d'environ 2 points).

Aucune valeur n'est inventée : toute base provient de `donnees_live` (valeur
réelle datée) ou d'une constante documentée ci-dessous.
"""

from __future__ import annotations

import math
from collections.abc import Iterable
from dataclasses import asdict, dataclass, field
from typing import Any

from simulateur.donnees_live import ContexteInstant
from simulateur.model import DecisionPolitique
from simulateur.parametres import LEVIERS, TYPE_CIBLE, TYPE_INTERRUPTEUR

# ────────────────────────────────────────────────────────────────────────────
# 1. Domaines
# ────────────────────────────────────────────────────────────────────────────

@dataclass(frozen=True)
class Domaine:
    cle: str
    libelle: str
    description: str
    couleur: str
    priorite: int = 50


DOMAINES: tuple[Domaine, ...] = (
    Domaine("economie", "Économie & croissance",
            "Activité, investissement, productivité, balance commerciale.", "#38bdf8", 90),
    Domaine("budget", "Budget, dette & marchés",
            "Déficit, dette, charge d'intérêts, notation, spread OAT-Bund.", "#60a5fa", 95),
    Domaine("fiscalite", "Fiscalité & prélèvements",
            "Niveau et progressivité des prélèvements, recettes nouvelles.", "#818cf8", 80),
    Domaine("emploi", "Emploi & travail",
            "Chômage, emplois, qualité de l'emploi, salaires.", "#f59e0b", 90),
    Domaine("pouvoir_achat", "Pouvoir d'achat & niveau de vie",
            "Pouvoir d'achat des ménages, par décile, inflation subie.", "#fbbf24", 92),
    Domaine("pauvrete", "Pauvreté & inégalités",
            "Taux de pauvreté, Gini, recours aux minima sociaux.", "#22c55e", 88),
    Domaine("sante", "Santé",
            "Moyens, accès aux soins, prévention, espérance de vie.", "#14b8a6", 85),
    Domaine("education", "Éducation & jeunesse",
            "Moyens par élève, réussite, précarité des jeunes, petite enfance.", "#a855f7", 85),
    Domaine("recherche", "Recherche & innovation",
            "Effort de R&D, brevets, diffusion technologique.", "#c084fc", 70),
    Domaine("securite", "Sécurité & justice",
            "Effectifs, taux d'élucidation, délais judiciaires, sentiment de sécurité.", "#ef4444", 82),
    Domaine("defense", "Défense & souveraineté",
            "Effort de défense, industrie d'armement, dépendances critiques.", "#f97316", 84),
    Domaine("energie_climat", "Énergie & climat",
            "Émissions, production décarbonée, facture énergétique, adaptation.", "#84cc16", 86),
    Domaine("industrie", "Industrie & commerce extérieur",
            "Part industrielle, relocalisations, solde commercial, dépendances.", "#6366f1", 78),
    Domaine("numerique", "Numérique & IA",
            "Souveraineté numérique, cyber-résilience, administration numérique.", "#0ea5e9", 72),
    Domaine("logement", "Logement & territoires",
            "Construction, logement social, loyers, services de proximité.", "#ec4899", 80),
    Domaine("agriculture", "Agriculture & alimentation",
            "Souveraineté alimentaire, revenus agricoles, agroécologie.", "#65a30d", 65),
    Domaine("democratie", "Démocratie & institutions",
            "Confiance, participation, transparence, réformes institutionnelles.", "#eab308", 93),
    Domaine("social", "Solidarité & cohésion",
            "Protection sociale, dépendance, intégration, cohésion nationale.", "#4ade80", 83),
    Domaine("europe_monde", "Europe & monde",
            "Intégration européenne, aide internationale, migrations, alliances.", "#f472b6", 68),
    Domaine("resilience", "Résilience & risques systémiques",
            "Capacité à encaisser les chocs : énergie, alimentation, santé, cyber.", "#94a3b8", 76),
)

DOMAINES_PAR_CLE: dict[str, Domaine] = {d.cle: d for d in DOMAINES}


# ────────────────────────────────────────────────────────────────────────────
# 2. Spécifications d'indicateurs
# ────────────────────────────────────────────────────────────────────────────

@dataclass(frozen=True)
class SpecIndicateur:
    """Un indicateur d'impact : base « instant T » + termes d'élasticité."""

    cle: str
    domaine: str
    libelle: str
    unite: str
    base: str | float
    termes: tuple[tuple[str, float], ...] = ()
    sens: int = 1
    formule: str = ""
    source: str = ""
    precision: int = 1
    plancher: float | None = None
    plafond: float | None = None

    def en_dict(self) -> dict[str, Any]:
        charge = asdict(self)
        charge["termes"] = [list(t) for t in self.termes]
        return charge


def _spec(cle: str, domaine: str, libelle: str, unite: str, base: str | float,
          termes: Iterable[tuple[str, float]] = (), sens: int = 1,
          formule: str = "", source: str = "", precision: int = 1,
          plancher: float | None = None, plafond: float | None = None) -> SpecIndicateur:
    return SpecIndicateur(cle, domaine, libelle, unite, base, tuple(termes), sens,
                          formule, source, precision, plancher, plafond)


# Rappels de calibrage (pour lire les coefficients) :
#   1 point de PIB ≈ 30 Md€ ; dépense Éducation ≈ 170 Md€ ; Santé ≈ 277 Md€ ;
#   Régalien ≈ 75 Md€ ; Protection sociale ≈ 960 Md€ ; Population 68,6 M.

SPECS: tuple[SpecIndicateur, ...] = (
    # ── Économie ───────────────────────────────────────────────────────────
    _spec("croissance_reelle", "economie", "Croissance réelle du PIB", "%/an", 0.9,
          (("depenses_nouvelles_mde", 0.030), ("recettes_nouvelles_mde", -0.025),
           ("investissement_public_mde", 0.055), ("choc_petrole_pct", -0.020),
           ("choc_monde", -1.50), ("recherche_mde", 0.020), ("incertitude_geo", -0.80)),
          formule="tendance + 0,030 × Md€ de dépense nouvelle − 0,025 × Md€ de recette + "
                  "0,055 × Md€ d'investissement public − 0,020 × % de hausse du pétrole",
          source="Multiplicateurs OFCE/FMI : dépense courante 0,5-0,9 ; investissement 0,8-1,2 ; "
                 "recettes 0,2-0,5. Chocs pétroliers 1973/2008 : −0,2 pt de croissance par +10 %."),
    _spec("investissement", "economie", "Investissement des entreprises", "indice base 100",
          100.0,
          (("confiance_marche_delta_pts", 0.35), ("taux_credit_ecart_pts", -2.20),
           ("investissement_public_mde", 0.35), ("incertitude_geo", -2.00),
           ("choc_monde", -6.0)),
          formule="100 + 0,35 × (confiance − 50) − 2,2 × (taux PME − taux initial) "
                  "+ 0,35 × Md€ d'investissement public",
          source="INSEE — déterminants de l'investissement (coût du capital, demande anticipée).",
          plancher=70.0, plafond=140.0),
    _spec("balance_commerciale", "economie", "Solde commercial", "Md€", "solde_commercial_mde",
          (("competitivite_pts", 0.45), ("prix_energie_ecart_pct", -0.55),
           ("change_impact_pct", 0.25), ("relocalisations_mde", 0.40)),
          formule="solde de base + 0,45 × points de compétitivité − 0,55 × % de hausse des prix "
                  "importés + 0,40 × Md€ relocalisés",
          source="Douanes françaises ; élasticité-prix des importations énergétiques (≈ −0,3)."),

    # ── Budget, dette & marchés ────────────────────────────────────────────
    _spec("deficit_pct_pib", "budget", "Déficit public", "% du PIB", "deficit_pct_pib",
          (("solde_budgetaire_mde", -0.033),), sens=-1,
          formule="déficit = déficit de l'année précédente + solde des mesures nouvelles / PIB",
          source="Solde Maastricht (Eurostat) ; règle du Pacte de stabilité à 3 % du PIB.",
          plancher=0.0, plafond=20.0),
    _spec("dette_pct_pib", "budget", "Dette publique", "% du PIB", "dette_publique_pct_pib",
          (("deficit_ecart_pts", 1.0), ("croissance_nominale_ecart_pts", -0.85)),
          sens=-1,
          formule="accumulation du déficit, corrigée par la croissance nominale (effet dénominateur)",
          source="Équation d'accumulation de la dette ; Eurostat GOV_10DD_EDPT1.",
          plancher=40.0, plafond=250.0),
    _spec("charge_dette", "budget", "Charge de la dette", "Md€/an", "charge_dette_base",
          (("taux_oat_ecart_pts", 11.5),),
          sens=-1,
          formule="charge de base + 11,5 Md€ par point de taux long "
                  "(maturité moyenne 8,5 ans, 35 % de la dette refinancée par an)",
          source="AFT — structure de refinancement ; moteur : transmission progressive du taux.",
          plancher=20.0, plafond=250.0),
    _spec("spread_oat", "budget", "Spread OAT-Bund", "bps", "spread_base",
          (("effort_structurel_mde", -0.30), ("incertitude_geo", 22.0),
           ("confiance_marche_delta_pts", -6.0)),
          sens=-1,
          formule="spread de base − 0,30 bp par Md€ d'effort structurel + prime géopolitique",
          source="Écart France-Allemagne 2024-2026 : 70-90 bps en régime normal.",
          plancher=20.0, plafond=600.0),
    _spec("note_souveraine", "budget", "Notation souveraine (échelle 0-100)", "note", 72.0,
          (("spread_oat_ecart_bps", -0.08), ("deficit_ecart_pts", -2.5),
           ("dette_ecart_pts", -0.30)),
          formule="échelle 100 = AAA ; chaque 10 bps de spread coûte ≈ 0,8 point de notation",
          source="Grilles S&P / Moody's : spread, trajectoire de dette, croissance.",
          plancher=5.0, plafond=100.0),

    # ── Fiscalité ──────────────────────────────────────────────────────────
    _spec("prelevements_obligatoires", "fiscalite", "Prélèvements obligatoires", "% du PIB",
          "prelevements_obligatoires_pct_pib",
          (("recettes_nouvelles_pts", 1.0),),
          formule="taux de base + recettes nouvelles rapportées au PIB",
          source="Eurostat — taux de prélèvements obligatoires ; PLF.",
          plancher=25.0, plafond=60.0),
    _spec("progressivite", "fiscalite", "Progressivité du système fiscal", "indice 0-100", 52.0,
          (("isf_pts", 6.0), ("ir_haut_pts", 2.2), ("flat_tax_suppression_pts", -6.0),
           ("succession_pts", 3.0), ("tva_hausse_pts", -4.5), ("csg_pts", -2.0),
           ("niches_pts", 1.5)),
          formule="+ ISF/rétablissement, IR haut, succession ; − TVA, CSG, flat tax",
          source="Conseil des prélèvements obligatoires — structure des prélèvements.",
          plancher=20.0, plafond=95.0),
    _spec("restitution_menages", "fiscalite", "Restitution directe aux ménages", "Md€", 0.0,
          (("transferts_menages_mde", 1.0), ("baisse_tva_energie_mde", 1.0),
           ("transferts_sociaux_mde", 1.0)),
          formule="somme des transferts, baisses de prélèvements et prestations ciblant les ménages",
          source="PLF/PLFSS — mesures de pouvoir d'achat (13 Md€ en 2023-2024)."),

    # ── Emploi & travail ───────────────────────────────────────────────────
    _spec("chomage", "emploi", "Taux de chômage", "% de la population active",
          "chomage_pct",
          (("pib_ecart_croissance_pts", -0.35), ("formation_mde", -0.150),
           ("exonerations_delta_mde", -0.080), ("smic_pts", 0.16),
           ("temps_travail_h", 0.22), ("choc_monde", 0.35)),
          sens=-1,
          formule="loi d'Okun : − 0,35 pt par point de croissance au-dessus de la tendance ; "
                  "− 0,15 pt par Md€ de formation ; − 0,08 pt par Md€ d'exonérations",
          source="Loi d'Okun (0,3-0,5 selon les pays) ; évaluations France Compétences.",
          plancher=3.0, plafond=25.0),
    _spec("taux_emploi", "emploi", "Taux d'emploi des 15-64 ans", "%", 68.4,
          (("chomage_ecart_pts", -0.75), ("formation_mde", 0.05), ("creations_emplois_milliers", 0.02)),
          formule="taux d'emploi de base − 0,75 × variation du chômage + effets formation",
          source="Eurostat — taux d'emploi (68,4 % en France, objectif européen 78 %).",
          plancher=45.0, plafond=90.0),
    _spec("emplois_crees", "emploi", "Emplois créés (cumul sur 5 ans)", "milliers", 0.0,
          (("pib_ecart_croissance_pts", 210.0), ("investissement_public_mde", 14.0),
           ("formation_mde", 6.0), ("relocalisations_mde", 9.0)),
          formule="≈ 210 000 emplois par point de croissance au-dessus de la tendance "
                  "+ 14 000 par Md€ d'investissement public",
          source="Élasticité emploi/PIB ≈ 0,6 (INSEE) sur 30 M d'actifs occupés.",
          plancher=-1500.0, plafond=2500.0),
    _spec("salaire_reel", "emploi", "Salaire moyen réel", "indice base 100", 100.0,
          (("pouvoir_achat_ecart_pct", 0.75), ("smic_pts", 0.90),
           ("partage_valeur_mde", 0.25), ("chomage_ecart_pts", 0.35)),
          formule="100 + 0,75 × pouvoir d'achat + 0,90 × point de SMIC + 0,25 × Md€ de partage "
                  "de la valeur − effet du chômage",
          source="DARES — salaire moyen par tête ; rapports sur le partage de la valeur.",
          plancher=85.0, plafond=130.0),
    _spec("qualite_emploi", "emploi", "Qualité de l'emploi (stabilité)", "indice 0-100", 58.0,
          (("temps_travail_h", -3.0), ("formation_mde", 0.35),
           ("protection_sociale_mde", 0.25), ("chomage_ecart_pts", 1.20)),
          formule="stabilité des contrats : + formation et protection sociale, − chômage",
          source="DARES — part des contrats courts (≈ 12 %) et du temps partiel subi.",
          plancher=20.0, plafond=95.0),

    # ── Pouvoir d'achat ────────────────────────────────────────────────────
    _spec("pouvoir_achat", "pouvoir_achat", "Pouvoir d'achat des ménages", "indice base 100",
          100.0,
          (("pouvoir_achat_ecart_pct", 1.0), ("transferts_menages_mde", 0.030),
           ("inflation_ecart_pts", -0.90), ("chomage_ecart_pts", -0.60),
           ("smic_pts", 0.35)),
          formule="100 + 0,030 % par Md€ de transfert + baisses de prélèvements "
                  "− 0,90 × point d'inflation au-dessus de la tendance − effet chômage",
          source="INSEE — pouvoir d'achat du RDB par unité de consommation (base 100).",
          plancher=85.0, plafond=120.0),
    _spec("pouvoir_achat_d1", "pouvoir_achat", "Pouvoir d'achat — 10 % les plus modestes",
          "indice base 100", 100.0,
          (("transferts_sociaux_mde", 0.045), ("minima_sociaux_mde", 0.060),
           ("tva_hausse_pts", -0.80), ("inflation_ecart_pts", -1.00)),
          formule="les transferts ciblés pèsent 1,5 fois plus sur le premier décile que la moyenne",
          source="INSEE — niveau de vie des déciles ; DREES (effet redistributif des prestations).",
          plancher=80.0, plafond=120.0),
    _spec("pouvoir_achat_d9", "pouvoir_achat", "Pouvoir d'achat — 10 % les plus aisés",
          "indice base 100", 100.0,
          (("isf_pts", -0.30), ("ir_haut_pts", -0.35), ("flat_tax_suppression_pts", -0.25),
           ("marches_ecart_pts", 0.20)),
          formule="fiscalité du capital et des hauts revenus, plus effet des marchés financiers",
          source="INSEE — variation différenciée des niveaux de vie par décile.",
          plancher=80.0, plafond=120.0),
    _spec("inflation", "pouvoir_achat", "Inflation", "%", "inflation_pct",
          (("choc_petrole_pct", 0.045), ("tva_hausse_pts", 0.22), ("smic_pts", 0.10),
           ("change_impact_pct", -0.25), ("taxe_carbone_eur_t", 0.012)),
          sens=-1,
          formule="inflation de base + 0,045 × % de hausse du pétrole + TVA − effet du change "
                  "+ 0,012 × €/t de taxe carbone",
          source="INSEE/Eurostat — élasticité de l'IPC à l'énergie (≈ 0,05) et au change.",
          plancher=-1.0, plafond=15.0),

    # ── Pauvreté & inégalités ──────────────────────────────────────────────
    _spec("pauvrete", "pauvrete", "Taux de pauvreté (seuil 60 %)", "% de la population",
          "taux_pauvrete_pct",
          (("minima_sociaux_mde", -0.055), ("transferts_sociaux_mde", -0.035),
           ("chomage_ecart_pts", 0.32), ("apl_delta_mde", 0.040),
           ("inflation_ecart_pts", 0.18), ("logement_social_milliers", -0.004)),
          sens=-1,
          formule="pauvreté − 0,055 pt par Md€ de minima sociaux − 0,035 par Md€ de transferts "
                  "+ 0,32 par point de chômage + effet des coupes d'APL",
          source="DREES/INSEE — élasticités de la pauvreté aux transferts et à l'emploi (0,4-0,6).",
          plancher=3.0, plafond=30.0),
    _spec("gini", "pauvrete", "Indice de Gini", "0-100", "indice_gini",
          (("progressivite_ecart_pts", -0.06), ("chomage_ecart_pts", 0.35),
           ("transferts_sociaux_mde", -0.010), ("isf_pts", -0.25)),
          sens=-1,
          formule="Gini − 0,06 par point de progressivité + 0,35 par point de chômage",
          source="INSEE/Eurostat — décomposition des inégalités ; effet redistributif des transferts.",
          plancher=20.0, plafond=55.0),
    _spec("beneficiaires_minima", "pauvrete", "Bénéficiaires des minima sociaux", "millions", 4.3,
          (("chomage_ecart_pts", 0.12), ("minima_sociaux_mde", 0.02)),
          sens=-1,
          formule="effet mécanique du chômage, corrigé par les revalorisations",
          source="DREES — allocataires du RSA, de l'AAH et de l'ASS (≈ 4,3 M).",
          plancher=1.0, plafond=8.0),
    _spec("recours_aide_alimentaire", "pauvrete", "Recours à l'aide alimentaire", "millions", 3.2,
          (("pauvrete_ecart_pts", 0.18), ("aide_alimentaire_mde", -0.10),
           ("chomage_ecart_pts", 0.08)),
          sens=-1,
          formule="effet de la pauvreté et des dispositifs d'aide directe",
          source="Secours catholique / Restos du cœur (≈ 3,2 M de personnes aidées).",
          plancher=0.5, plafond=10.0),

    # ── Santé ──────────────────────────────────────────────────────────────
    _spec("depenses_sante_pct_pib", "sante", "Dépenses de santé", "% du PIB", 9.2,
          (("sante_mde", 0.0033),),
          formule="9,2 % du PIB de base + 0,0033 pt par Md€ de dépenses de santé",
          source="Eurostat COFOG GF07 ; PLFSS — ONDAM (≈ 275 Md€).",
          plancher=6.0, plafond=16.0),
    _spec("esperance_vie", "sante", "Espérance de vie à la naissance", "années", 83.2,
          (("sante_mde", 0.010), ("prevention_mde", 0.020),
           ("pauvrete_ecart_pts", -0.12), ("pollution_ecart_pts", -0.08)),
          formule="+ 0,010 an par Md€ de dépenses de santé (effet différé de 3 à 5 ans)",
          source="OCDE — déterminants de l'espérance de vie ; Santé publique France.",
          plancher=75.0, plafond=90.0),
    _spec("acces_soins", "sante", "Accès aux soins dans les territoires", "indice 0-100", 61.0,
          (("sante_mde", 0.100), ("deserts_medicaux_mde", 0.600),
           ("prevention_mde", 0.150), ("territoires_mde", 0.050)),
          sens=1,
          formule="+ 0,6 pt par Md€ dédié à la lutte contre les déserts médicaux",
          source="DREES — accessibilité potentielle localisée (APL) aux médecins.",
          plancher=30.0, plafond=100.0),
    _spec("sante_mentale", "sante", "Prise en charge de la santé mentale", "indice 0-100", 52.0,
          (("sante_mde", 0.060), ("prevention_mde", 0.200),
           ("tension_ecart_pts", -0.25), ("chomage_ecart_pts", -0.20)),
          formule="moyens dédiés, moins la tension sociale et le chômage",
          source="Cour des comptes — santé mentale ; IGAS (≈ 2 M de personnes suivies).",
          plancher=20.0, plafond=100.0),

    # ── Éducation, jeunesse, recherche ─────────────────────────────────────
    _spec("depenses_education_pct_pib", "education", "Dépenses d'éducation", "% du PIB", 5.6,
          (("education_mde", 0.0033),),
          formule="5,6 % du PIB de base + 0,0033 pt par Md€ d'éducation (≈ 170 Md€ au total)",
          source="Eurostat COFOG GF09 ; mission Enseignement scolaire du PLF.",
          plancher=4.0, plafond=12.0),
    _spec("depense_par_eleve", "education", "Dépense annuelle par élève", "€", 9500.0,
          (("education_mde", 0.59),),
          formule="+ 0,59 % par Md€ : 30 Md€ sur 12 M d'élèves ≈ +17 % de moyens par élève",
          source="DEPP — coût moyen d'un élève (≈ 9 500 €/an).",
          plancher=6000.0, plafond=25000.0),
    _spec("reussite_scolaire", "education", "Réussite scolaire (indice)", "indice 0-100", 62.0,
          (("education_mde", 0.100), ("enseignants_mde", 0.150),
           ("pauvrete_ecart_pts", -0.18), ("formation_mde", 0.080)),
          formule="effet des moyens (+ 0,10/Md€, rendements décroissants) et de l'encadrement",
          source="DEPP / PISA — effet des moyens et de l'encadrement sur les acquis (modéré).",
          plancher=35.0, plafond=100.0),
    _spec("neet", "education", "Jeunes ni en emploi ni en formation (NEET)", "%", 12.3,
          (("formation_mde", -0.35), ("education_mde", -0.020), ("chomage_ecart_pts", 0.42)),
          sens=-1,
          formule="− 0,35 pt par Md€ de formation des jeunes ; + effet du chômage",
          source="Eurostat — NEET 15-29 ans (≈ 12 % en France, 9 % en Allemagne).",
          plancher=4.0, plafond=30.0),
    _spec("recherche_pct_pib", "recherche", "Dépense de R&D", "% du PIB", 2.2,
          (("recherche_mde", 0.0040),),
          formule="+ 0,004 pt de PIB par Md€ de recherche publique (effet de levier privé inclus)",
          source="MESR — dépense intérieure de R&D (2,2 % du PIB, dont 1,4 % privé).",
          plancher=1.0, plafond=5.0),
    _spec("brevets", "recherche", "Brevets déposés (indice)", "indice base 100", 100.0,
          (("recherche_mde", 0.35), ("numerique_mde", 0.15), ("formation_mde", 0.10)),
          formule="+ 0,35 % par Md€ de recherche, effet différé de 2 à 4 ans",
          source="INPI / OEB — demandes de brevets ; décalage temporel documenté.",
          plancher=50.0, plafond=200.0),

    # ── Sécurité & justice ─────────────────────────────────────────────────
    _spec("delits_elucides", "securite", "Taux d'élucidation des infractions", "%", 45.0,
          (("regalien_mde", 0.30), ("lien_social_ecart_pts", 0.40),
           ("effectifs_securite_milliers", 0.30)),
          formule="+ 0,30 pt par Md€ de moyens de sécurité ; + présence de terrain",
          source="SSMSI — statistiques de la délinquance ; police technique et scientifique.",
          plancher=20.0, plafond=85.0),
    _spec("delais_justice", "securite", "Délai moyen de jugement", "mois", 16.0,
          (("justice_mde", -0.300), ("criminalite_ecart_pts", 0.50)),
          sens=-1,
          formule="− 0,30 mois par Md€ de moyens judiciaires ; + effet du contentieux",
          source="CEPEJ — délais civils et pénaux (France ≈ 16 mois) ; loi de programmation.",
          plancher=4.0, plafond=45.0),
    _spec("sentiment_securite", "securite", "Sentiment de sécurité", "indice 0-100", 54.0,
          (("regalien_mde", 0.150), ("tension_ecart_pts", -0.35),
           ("chomage_ecart_pts", -0.20), ("lien_social_ecart_pts", 0.50)),
          formule="+ présence publique ; − tension sociale, chômage et clivages",
          source="SSMSI — indicateurs de victimation et de sentiment d'insécurité.",
          plancher=20.0, plafond=100.0),
    _spec("emprisonnement", "securite", "Population carcérale", "détenus", 78000.0,
          (("justice_mde", -350.0), ("criminalite_ecart_pts", 900.0),
           ("alternatives_penales_mde", -600.0)),
          sens=-1,
          formule="surpopulation = peines prononcées − places nouvelles et alternatives",
          source="Administration pénitentiaire (≈ 79 000 détenus pour 62 000 places en 2025).",
          plancher=40000.0, plafond=130000.0),

    # ── Défense & souveraineté ─────────────────────────────────────────────
    _spec("effort_defense", "defense", "Effort de défense", "% du PIB", "effort_defense_base",
          (("effort_defense_ecart_pts", 1.0),),
          formule="niveau cible atteint selon le profil de montée en charge",
          source="LPM 2024-2030 ; cible OTAN de 3,5 % du PIB (sommet de La Haye).",
          plancher=1.0, plafond=6.0),
    _spec("capacite_industrielle_defense", "defense",
          "Base industrielle et technologique de défense", "indice 0-100", 68.0,
          (("defense_mde", 0.200), ("mobilisation_pts", 1.60), ("relocalisations_mde", 0.05)),
          formule="+ 0,20 pt par Md€ de commandes ; effet d'échelle de l'économie de guerre",
          source="DGA — base industrielle ; Cour des comptes — programmes d'armement.",
          plancher=30.0, plafond=100.0),
    _spec("dependance_critique", "defense", "Dépendance aux importations critiques",
          "indice 0-100", 66.0,
          (("souverainete_mde", -0.150), ("relocalisations_mde", -0.120), ("choc_monde", 25.0)),
          sens=-1,
          formule="dépendances (semi-conducteurs, médicaments, énergie, terres rares) réévaluées",
          source="OCDE / DG Trésor — vulnérabilités des chaînes d'approvisionnement.",
          plancher=10.0, plafond=100.0),

    # ── Énergie & climat ───────────────────────────────────────────────────
    _spec("emissions_co2", "energie_climat", "Émissions de CO₂", "Mt CO₂", "emissions_base",
          (("climat_mde", -0.060), ("taxe_carbone_eur_t", -0.22),
           ("activite_ecart_pct", 0.30), ("effort_defense_ecart_pts", 0.10)),
          sens=-1,
          formule="− 0,060 Mt par Md€ investi dans la transition − 0,22 Mt par €/t de taxe carbone "
                  "(élasticité −0,25 %/€) + effet d'activité",
          source="CITEPA — inventaire d'émissions ; élasticité-prix des ménages (≈ −0,25).",
          plancher=50.0, plafond=400.0),
    _spec("part_decarbonee", "energie_climat", "Électricité décarbonée", "% de la production", 92.0,
          (("nucleaire_mde", 0.020), ("renouvelables_mde", 0.015)),
          formule="nucléaire et renouvelables : + 0,02 pt par Md€ investi (avec délai de mise en service)",
          source="RTE — mix électrique français (≈ 92 % décarboné) ; « Futurs énergétiques 2050 ».",
          plancher=60.0, plafond=100.0),
    _spec("facture_energetique", "energie_climat", "Facture énergétique", "% du PIB", 2.2,
          (("prix_energie_ecart_pct", 0.075), ("climat_mde", -0.0015), ("choc_monde", 6.0)),
          sens=-1,
          formule="facture de base + 0,075 pt de PIB par % de hausse du prix de l'énergie",
          source="DGEC / Douanes — facture énergétique (≈ 2,2 % du PIB en 2025).",
          plancher=0.5, plafond=8.0),
    _spec("adaptation_climat", "energie_climat", "Préparation à l'adaptation climatique",
          "indice 0-100", 42.0,
          (("adaptation_mde", 0.900), ("climat_mde", 0.050), ("territoires_mde", 0.030)),
          formule="+ 0,9 pt par Md€ dédié à l'eau, aux forêts, au littoral et aux canicules",
          source="PNACC-3 ; Cour des comptes — adaptation au changement climatique (2024).",
          plancher=10.0, plafond=100.0),

    # ── Industrie & commerce ───────────────────────────────────────────────
    _spec("part_industrie", "industrie", "Part de l'industrie dans la valeur ajoutée", "%", 12.1,
          (("relocalisations_mde", 0.100), ("souverainete_mde", 0.060),
           ("prix_energie_ecart_pct", -0.020), ("choc_monde", -2.50)),
          formule="+ 0,10 pt par Md€ relocalisé − 0,02 pt par % de hausse du coût de l'énergie",
          source="INSEE — valeur ajoutée industrielle (12,1 % en France, ≈ 20 % en Allemagne).",
          plancher=6.0, plafond=25.0),
    _spec("relocalisations", "industrie", "Projets de relocalisation aboutis", "indice 0-100", 38.0,
          (("relocalisations_mde", 1.800), ("souverainete_mde", 0.900),
           ("simplification_mde", 0.700)),
          formule="+ financement direct, souveraineté industrielle et simplification des normes",
          source="Observatoire des relocalisations (Bpifrance) ; rapports France Industrie.",
          plancher=10.0, plafond=100.0),
    _spec("exportations", "industrie", "Exportations (hors énergie)", "indice base 100", 100.0,
          (("competitivite_pts", 0.35), ("relocalisations_mde", 0.40),
           ("choc_monde", -15.0), ("change_impact_pct", 0.25)),
          formule="+ compétitivité hors prix, relocalisations ; − fragmentation mondiale",
          source="Douanes — exportations françaises ; élasticité au taux de change (≈ 0,2).",
          plancher=60.0, plafond=160.0),

    # ── Numérique & IA ─────────────────────────────────────────────────────
    _spec("souverainete_numerique", "numerique", "Souveraineté numérique", "indice 0-100", 44.0,
          (("numerique_mde", 1.500), ("cyber_mde", 0.700), ("choc_semi_pct", -0.55)),
          formule="+ cloud souverain, IA et cyber − dépendance aux composants importés",
          source="DINUM / ANSSI — indicateurs de dépendance technologique.",
          plancher=10.0, plafond=100.0),
    _spec("admin_numerique", "numerique", "Qualité des services publics numériques",
          "indice 0-100", 66.0,
          (("numerique_mde", 1.200), ("simplification_mde", 0.900),
           ("territoires_mde", 0.300)),
          formule="dématérialisation, simplification, inclusion numérique des territoires",
          source="Baromètre DINUM de la qualité des démarches en ligne.",
          plancher=20.0, plafond=100.0),
    _spec("cyber_resilience", "numerique", "Cyber-résilience des opérateurs vitaux",
          "indice 0-100", 58.0,
          (("cyber_mde", 2.200), ("numerique_mde", 0.300), ("cyberattaque_pts", -18.0)),
          formule="+ 2,2 pts par Md€ de moyens cyber ; − 18 pts en cas d'attaque systémique réussie",
          source="ANSSI — maturité NIS 2 des opérateurs d'importance vitale.",
          plancher=5.0, plafond=100.0),

    # ── Logement & territoires ─────────────────────────────────────────────
    _spec("construction_logements", "logement", "Logements construits par an", "milliers", 260.0,
          (("logement_social_milliers", 1.0), ("territoires_mde", 0.60),
           ("taux_credit_ecart_pts", -7.0), ("zan_pts", -25.0)),
          formule="+ 1 logement social par logement social financé − coût du crédit − contrainte foncière",
          source="SDES — mises en chantier (≈ 260 000/an contre 400 000 en 2017).",
          plancher=80.0, plafond=600.0),
    _spec("attente_logement_social", "logement", "Demandeurs de logement social en attente",
          "millions", 2.2,
          (("logement_social_milliers", -0.0008), ("pauvrete_ecart_pts", 0.10)),
          sens=-1,
          formule="file d'attente : construction neuve − dégradation sociale",
          source="USH / ministère — ≈ 2,2 M de demandes en attente.",
          plancher=0.3, plafond=5.0),
    _spec("services_proximite", "logement", "Services publics de proximité", "indice 0-100",
          64.0,
          (("services_proximite_ecart_pts", 1.0), ("territoires_mde", 0.900),
           ("sante_mde", 0.020), ("territoires_pts", 0.90), ("education_mde", 0.020)),
          formule="+ DGF, décentralisation et services de terrain − coupes indifférenciées",
          source="Cour des comptes — maillage des services publics ; comité des finances locales.",
          plancher=20.0, plafond=100.0),
    _spec("loyers", "logement", "Loyer moyen (indice base 100)", "indice base 100", 100.0,
          (("encadrement_loyers_pts", -3.0), ("logement_social_milliers", -0.02),
           ("taux_credit_ecart_pts", 1.5)),
          sens=-1,
          formule="loyers : − encadrement et construction sociale, + coût du crédit et rareté",
          source="ONRE / INSEE — indices de loyers (IRL) et tension des marchés.",
          plancher=70.0, plafond=160.0),

    # ── Agriculture & alimentation ─────────────────────────────────────────
    _spec("souverainete_alimentaire", "agriculture", "Souveraineté alimentaire",
          "indice 0-100", 62.0,
          (("agriculture_mde", 1.800), ("zan_pts", 8.0),
           ("choc_monde", -20.0), ("adaptation_mde", 0.100)),
          formule="+ soutien à la production et préservation des terres − fragmentation mondiale",
          source="Rapport Sénat sur la souveraineté alimentaire ; Agreste.",
          plancher=20.0, plafond=100.0),
    _spec("revenu_agricole", "agriculture", "Revenu des agriculteurs", "indice base 100", 100.0,
          (("agriculture_mde", 0.900), ("adaptation_mde", 0.200), ("climat_choc_pts", -0.60)),
          formule="+ soutien aux filières et adaptation (eau, sécheresse) ; − aléas climatiques",
          source="Agreste / MSA — revenu net par exploitation ; aléas climatiques 2022-2025.",
          plancher=50.0, plafond=200.0),
    _spec("bio_agroecologie", "agriculture", "Part de l'agriculture bio ou raisonnée", "%", 12.0,
          (("agriculture_mde", 0.300), ("climat_mde", 0.020), ("zan_pts", 4.0)),
          formule="+ 0,3 pt par Md€ dédié à la transition agroécologique",
          source="Agence Bio — part de la surface agricole utile en bio (≈ 12 %).",
          plancher=3.0, plafond=60.0),

    # ── Démocratie & institutions ──────────────────────────────────────────
    _spec("confiance_institutions", "democratie", "Confiance dans les institutions",
          "indice 0-100", 27.5,
          (("reformes_democratiques", 4.5), ("usage_49_3_nb", -2.4),
           ("anticorruption_mde", 1.8), ("tension_ecart_pts", -0.22)),
          formule="+ 4,5 pts par paquet de réformes démocratiques activées ; − 2,4 par 49.3",
          source="CEVIPOF — baromètre de la confiance politique (27,5 % de confiance en 2025).",
          plancher=5.0, plafond=100.0),
    _spec("participation", "democratie", "Participation électorale et civique", "%", 66.0,
          (("reformes_democratiques", 1.9), ("proportionnelle_pts", 0.35),
           ("vote_blanc_pts", 1.6), ("tension_ecart_pts", -0.10)),
          formule="+ reconnaissance du vote blanc, RIC et proportionnelle ; − défiance",
          source="Ministère de l'Intérieur — participation par scrutin (66 % aux législatives 2024).",
          plancher=30.0, plafond=95.0),
    _spec("risque_censure", "democratie", "Risque de censure du gouvernement", "%",
          "risque_censure_base",
          (("tension_ecart_pts", 1.8), ("confiance_ecart_pts", -0.9),
           ("usage_49_3_nb", 3.2), ("stabilite_ecart_pts", -2.0)),
          sens=-1,
          formule="probabilité de motion de censure issue du moteur, réévaluée par la tension",
          source="Moteur (strate nationale) ; historique des censures de 1962 à 2025.",
          plancher=0.0, plafond=100.0),
    _spec("tension_sociale", "democratie", "Tension sociale", "indice 0-100", 36.0,
          (("tension_moteur_ecart_pts", 1.0), ("tension_ecart_pts", 1.0), ("pauvrete_ecart_pts", 2.4),
           ("chomage_ecart_pts", 2.0), ("inflation_ecart_pts", 1.6),
           ("reformes_democratiques", -2.2)),
          sens=-1,
          formule="tension mesurée par le moteur, amplifiée par pauvreté, chômage et inflation",
          source="Moteur (strate locale) ; baromètres de conflictualité sociale.",
          plancher=0.0, plafond=100.0),
    _spec("qualite_democratique", "democratie", "Qualité démocratique (indice composite)",
          "indice 0-100", 55.0,
          (("reformes_democratiques", 3.2), ("usage_49_3_nb", -1.8),
           ("anticorruption_mde", 1.5), ("proportionnelle_pts", 0.25)),
          formule="RIC, vote blanc, transparence, proportionnelle, convention citoyenne",
          source="Indices V-Dem / Economist Intelligence Unit adaptés au contexte français.",
          plancher=10.0, plafond=100.0),

    # ── Solidarité & cohésion ──────────────────────────────────────────────
    _spec("protection_sociale", "social", "Protection sociale", "% du PIB", 32.0,
          (("protection_sociale_mde", 0.0033),),
          formule="base + variation des dépenses de protection sociale rapportée au PIB",
          source="Eurostat COFOG GF10 ; comptes de la protection sociale (≈ 32 % du PIB).",
          plancher=25.0, plafond=45.0),
    _spec("prise_en_charge_dependance", "social", "Prise en charge de la dépendance",
          "indice 0-100", 46.0,
          (("dependance_mde", 1.500), ("sante_mde", 0.020), ("territoires_mde", 0.030)),
          formule="+ 1,5 pt par Md€ pour les EHPAD, l'aide à domicile et les métiers du grand âge",
          source="Rapport Libault ; branche Autonomie de la Sécurité sociale (≈ 40 Md€).",
          plancher=10.0, plafond=100.0),
    _spec("integration", "social", "Intégration des nouveaux arrivants", "indice 0-100", 50.0,
          (("integration_mde", 2.200), ("chomage_ecart_pts", -0.30),
           ("tension_ecart_pts", -0.30)),
          formule="+ 2,2 pts par Md€ d'intégration (langue, emploi, diplômes)",
          source="Cour des comptes — intégration des étrangers ; OFII.",
          plancher=10.0, plafond=100.0),
    _spec("cohesion_nationale", "social", "Cohésion nationale", "indice 0-100", 48.0,
          (("tension_ecart_pts", -0.80), ("pauvrete_ecart_pts", -1.20),
           ("inegalites_ecart_pts", -1.00), ("reformes_democratiques", 1.5),
           ("integration_mde", 0.700)),
          formule="tension et inégalités pèsent ; les réformes démocratiques apaisent",
          source="Fractures françaises (CEVIPOF / Destin commun) ; observatoire des inégalités.",
          plancher=5.0, plafond=100.0),

    # ── Europe & monde ─────────────────────────────────────────────────────
    _spec("integration_europeenne", "europe_monde", "Intégration européenne", "indice 0-100", 60.0,
          (("europe_pts", 1.600), ("defense_mde", 0.010), ("choc_monde", -6.0)),
          formule="+ coopération budgétaire, défense commune et projets industriels partagés",
          source="Commission européenne ; rapports Draghi et Letta sur la compétitivité.",
          plancher=20.0, plafond=100.0),
    _spec("aide_internationale", "europe_monde", "Effort d'aide au développement", "% du PIB", 0.55,
          (("apd_mde", 0.012),),
          formule="base + effort d'aide (0,55 % aujourd'hui, cible ONU de 0,7 %)",
          source="OCDE-CAD — aide publique au développement française.",
          plancher=0.1, plafond=1.5),
    _spec("maitrise_migratoire", "europe_monde", "Maîtrise des flux migratoires", "indice 0-100",
          50.0,
          (("migration_pts", 1.800), ("integration_mde", 0.600), ("europe_pts", 0.400)),
          formule="+ contrôle des frontières, accords de retour, coopération avec les pays d'origine",
          source="OCDE — migrations internationales ; OFPRA / OFII.",
          plancher=10.0, plafond=100.0),

    # ── Résilience & risques systémiques ───────────────────────────────────
    _spec("resilience_energetique", "resilience", "Résilience énergétique", "indice 0-100", 58.0,
          (("nucleaire_mde", 0.800), ("renouvelables_mde", 0.600), ("climat_mde", 0.200),
           ("chokepoints_nb", -6.0), ("dependance_import_pts", -1.0)),
          formule="+ production nationale décarbonée et stocks − chokepoints et importations",
          source="AIE — sécurité énergétique ; RTE — capacité de production nationale.",
          plancher=10.0, plafond=100.0),
    _spec("resilience_alimentaire", "resilience", "Résilience alimentaire", "indice 0-100", 62.0,
          (("agriculture_mde", 1.300), ("zan_pts", 6.0), ("adaptation_mde", 0.300),
           ("choc_monde", -20.0)),
          formule="+ production et foncier protégés − dépendance aux importations",
          source="Agreste / FAO — autosuffisance alimentaire et dépendances ciblées.",
          plancher=15.0, plafond=100.0),
    _spec("resilience_sanitaire", "resilience", "Résilience sanitaire", "indice 0-100", 54.0,
          (("medicaments_mde", 2.200), ("sante_mde", 0.050), ("prevention_mde", 0.200)),
          formule="+ production de médicaments, stocks stratégiques, prévention et lits",
          source="ANSM — rapports sur les pénuries de médicaments ; OMS.",
          plancher=10.0, plafond=100.0),
    _spec("resilience_cyber", "resilience", "Résilience cyber & hybride", "indice 0-100", 55.0,
          (("cyber_mde", 1.900), ("numerique_mde", 0.500), ("cyberattaque_pts", -20.0),
           ("securite_civile_mde", 0.400)),
          formule="+ moyens ANSSI/OIV et plans de continuité − attaques subies",
          source="ANSSI — maturité cyber des opérateurs vitaux ; directive NIS 2.",
          plancher=5.0, plafond=100.0),
)


# ────────────────────────────────────────────────────────────────────────────
# 3. Lignes budgétaires et médiateurs
# ────────────────────────────────────────────────────────────────────────────

#: ligne du levier → (médiateur en Md€, préfixe « points » éventuel)
LIGNES: dict[str, str] = {
    "education": "education", "recherche": "recherche", "formation": "formation",
    "ondam": "sante", "hopital": "sante", "deserts_medicaux": "deserts_medicaux",
    "prevention": "prevention", "medicaments": "medicaments", "dependance": "dependance",
    "retraites": "transferts_sociaux", "minima_sociaux": "minima_sociaux", "apl": "apl",
    "aide_alimentaire": "aide_alimentaire", "enfance": "protection_sociale",
    "police": "effectifs_securite", "justice": "justice", "criminalite": "criminalite",
    "cyber": "cyber", "securite_civile": "securite_civile",
    "nucleaire": "nucleaire", "renouvelables": "renouvelables", "renovation": "climat",
    "adaptation": "adaptation", "transports": "climat", "zan": "zan",
    "relocalisation": "relocalisations", "numerique": "numerique", "agriculture": "agriculture",
    "logement_social": "logement_social", "loyers": "encadrement_loyers",
    "decentralisation": "territoires", "simplification": "simplification",
    "europe": "europe", "apd": "apd", "integration": "integration", "migration": "migration",
    "convention": "convention", "anticorruption": "anticorruption",
    "proportionnelle": "proportionnelle", "49_3": "usage_49_3", "commerce": "commerce",
    "temps_travail": "temps_travail", "partage_valeur": "partage_valeur", "smic": "smic",
    "exonerations": "exonerations", "inspection_travail": "police_travail",
    "point_indice": "point_indice", "effectifs_etat": "effectifs_etat",
    # recettes
    "ir": "ir_haut", "csg": "csg", "tva": "tva_hausse", "isf": "isf",
    "flat_tax": "flat_tax_suppression", "succession": "succession", "niches": "niches",
    "taxe_carbone": "taxe_carbone", "accises": "accises",
}

#: Leviers pilotés par un **champ** du moteur (`DecisionPolitique`) mais dont la
#: valeur doit aussi être exposée en unité physique aux formules d'indicateurs.
#: La clé est le levier, la valeur le nom du médiateur (`<nom>_pts`, `rec_<nom>_mde`).
UNITES_CHAMPS: dict[str, str] = {
    "niches_fiscales": "niches",
}

#: Leviers dont le montant est un transfert direct aux ménages.
LEVIERS_TRANSFERT_MENAGES = (
    "cheque_energie", "precarite_energetique", "aide_alimentaire",
    "revalorisation_minima_sociaux", "revalorisation_retraites", "aide_logement",
)

#: Leviers comptés comme transferts sociaux (prestations).
LEVIERS_TRANSFERTS_SOCIAUX = (
    "revalorisation_retraites", "revalorisation_minima_sociaux", "aide_logement",
    "dependance_grand_age", "aide_enfance_jeunesse",
)

#: Réformes institutionnelles et démocratiques (comptées dans le médiateur dédié).
LEVIERS_DEMOCRATIQUES = (
    "reforme_casier_b2", "reforme_vote_blanc", "reforme_ric",
    "reforme_regimes_speciaux", "reforme_anti_pantouflage", "reforme_non_cumul",
)

FAMILLES_RECETTES = ("fiscalite_menages", "fiscalite_entreprises")


@dataclass
class MediateursAnnee:
    """Variables intermédiaires d'une année : moteur + leviers."""

    annee: int = 1
    pib_initial_mde: float = 3015.0
    pib_nominal_mde: float = 3015.0
    inflation_pct: float = 2.1
    deficit_pct_pib: float = 5.1
    dette_pct_pib: float = 115.6
    charge_dette_mde: float = 66.5
    taux_oat: float = 4.0
    spread_bps: float = 80.0
    tension_sociale: float = 36.0
    confiance_democratique: float = 27.5
    risque_censure_pct: float = 52.0
    effort_defense_pts: float = 2.1
    indice_geo: float = 63.0
    brent_usd: float = 82.5
    eur_usd: float = 1.08
    pouvoir_achat_index: float = 100.0
    disponibilite_semiconducteurs_pct: float = 100.0
    #: Médiateurs quantitatifs « en Md€ » ou « en points » produits par les leviers.
    flux: dict[str, float] = field(default_factory=dict)
    #: Écarts calculés vis-à-vis de la trajectoire de référence (tous leviers neutres).
    ecarts: dict[str, float] = field(default_factory=dict)

    def lire(self, nom: str) -> float:
        """Lecture unifiée : flux/écarts des leviers, puis attributs directs."""
        if nom in self.flux:
            return self.flux[nom]
        if nom in self.ecarts:
            return self.ecarts[nom]
        return float(getattr(self, nom, 0.0))


def _montant_levier(levier, valeur: float, annee_index: int) -> float:
    """Montant annuel d'un levier (Md€), avec montée en charge.

    * interrupteur : le facteur est un montant forfaitaire ;
    * curseur      : valeur × facteur ;
    * cible        : écart à la valeur par défaut × facteur (on ne « dépense »
                     que la trajectoire supplémentaire, jamais le niveau de base).
    """
    if levier.type == TYPE_INTERRUPTEUR:
        if valeur < 0.5:
            return 0.0
        montant = levier.facteur
    elif levier.type == TYPE_CIBLE:
        if abs(valeur - levier.defaut) < 1e-9:
            return 0.0
        montant = (valeur - levier.defaut) * levier.facteur
    else:
        if valeur == 0.0:
            return 0.0
        montant = valeur * levier.facteur
    profil = levier.profil[min(annee_index, len(levier.profil) - 1)]
    return montant * profil


def _poids_reformes_democratiques(parametres: dict[str, float]) -> float:
    poids = 0.0
    for cle in LEVIERS_DEMOCRATIQUES:
        levier = LEVIERS[cle]
        if levier.type == TYPE_INTERRUPTEUR:
            poids += 1.0 if parametres.get(cle, 0.0) >= 0.5 else 0.0
        else:
            poids += min(1.0, abs(parametres.get(cle, 0.0)) / 2.0)
    # Proportionnelle : jusqu'à +1 point selon la part retenue (50 % = +1).
    poids += min(1.0, parametres.get("reforme_proportionnelle", 0.0) / 50.0)
    # Convention citoyenne permanente.
    poids += 0.5 if parametres.get("convention_citoyenne", 0.0) >= 0.5 else 0.0
    return round(poids, 3)


def construire_flux(parametres: dict[str, float], annee_index: int) -> dict[str, float]:
    """Convertit les leviers en flux budgétaires et médiateurs quantitatifs."""
    flux: dict[str, float] = {}
    for cle, levier in LEVIERS.items():
        valeur = parametres.get(cle, levier.defaut)
        montant = _montant_levier(levier, valeur, annee_index)
        if montant == 0.0 and levier.ligne is None:
            continue

        # Médiateur « levier:xxx » utile aux formules spécifiques.
        flux[f"levier:{cle}"] = montant

        est_recette = levier.famille in FAMILLES_RECETTES
        if levier.ligne and levier.ligne in LIGNES:
            mediateur = LIGNES[levier.ligne]
            prefixe = "rec_" if est_recette else ""
            flux[f"{prefixe}{mediateur}_mde"] = (
                flux.get(f"{prefixe}{mediateur}_mde", 0.0) + montant
            )
            # Médiateur exprimé dans l'unité **physique** du levier (points de
            # taux, milliers de postes, nombre de réformes…) : montant en Md€
            # divisé par la valeur unitaire du levier (`facteur`, en Md€/unité).
            # Les formules d'indicateurs utilisent beaucoup cette échelle : sans
            # elle, un point de TVA ou un millier de policiers serait invisible.
            if levier.facteur:
                unites = montant / levier.facteur
                flux[f"{mediateur}_pts"] = flux.get(f"{mediateur}_pts", 0.0) + unites
                if "millier" in levier.unite or "poste" in levier.unite:
                    flux[f"{mediateur}_milliers"] = (
                        flux.get(f"{mediateur}_milliers", 0.0) + unites
                    )
        if est_recette:
            flux["recettes_nouvelles_mde"] = flux.get("recettes_nouvelles_mde", 0.0) + montant
        else:
            flux["depenses_nouvelles_mde"] = flux.get("depenses_nouvelles_mde", 0.0) + montant

    # Agrégats et conversions utiles aux formules.
    flux["recettes_nouvelles_mde"] = round(flux.get("recettes_nouvelles_mde", 0.0), 3)
    flux["depenses_nouvelles_mde"] = round(flux.get("depenses_nouvelles_mde", 0.0), 3)
    flux["baisse_tva_energie_mde"] = flux.get("levier:tva_energie_5_5", 0.0)
    flux["transferts_menages_mde"] = round(
        sum(flux.get(f"levier:{c}", 0.0) for c in LEVIERS_TRANSFERT_MENAGES), 3
    )
    flux["transferts_sociaux_mde"] = round(
        sum(flux.get(f"levier:{c}", 0.0) for c in LEVIERS_TRANSFERTS_SOCIAUX), 3
    )
    flux["baisse_prelevements_menages_mde"] = flux.get("baisse_tva_energie_mde", 0.0)
    # Investissement public : énergie/climat, logement, industrie (60 %), recherche.
    flux["investissement_public_mde"] = round(
        flux.get("climat_mde", 0.0)
        + flux.get("logement_social_mde", 0.0)
        + 0.6 * flux.get("relocalisations_mde", 0.0)
        + flux.get("recherche_mde", 0.0),
        3,
    )
    # Effort de défense : variation en points de PIB.
    flux["effort_defense_ecart_pts"] = 0.0  # renseigné par le moteur (niveau atteint)
    flux["effort_defense_mde"] = flux.get("levier:effort_defense_pct_pib", 0.0)
    # Réformes institutionnelles.
    flux["reformes_democratiques"] = _poids_reformes_democratiques(parametres)
    flux["usage_49_3_nb"] = parametres.get("usage_49_3", 0.0)
    flux["vote_blanc_pts"] = 1.0 if parametres.get("reforme_vote_blanc", 0.0) >= 0.5 else 0.0
    flux["temps_travail_h"] = parametres.get("temps_de_travail", 0.0)
    flux["smic_pts"] = parametres.get("smic_revalorisation", 0.0)
    flux["taxe_carbone_eur_t"] = parametres.get("taxe_carbone", 0.0)
    flux["mobilisation_pts"] = 1.0 if parametres.get("mobilisation_guerre", 0.0) >= 0.5 else 0.0
    flux["cyberattaque_pts"] = 1.0 if parametres.get("cyberattaque_systemique", 0.0) >= 0.5 else 0.0
    flux["choc_monde"] = parametres.get("commerce_mondial", 0.0) / 100.0
    flux["choc_semi"] = 0.0  # renseigné après le moteur (disponibilité des semi-conducteurs)

    # ── Agrégats et alias attendus par les formules d'indicateurs ─────────────
    # Chaque alias est la somme de lignes budgétaires existantes : aucun montant
    # n'est inventé, seule la présentation change (montants en Md€).
    def _somme(*mediateurs: str) -> float:
        return round(sum(flux.get(f"{nom}_mde", 0.0) for nom in mediateurs), 3)

    flux["regalien_mde"] = _somme("effectifs_securite", "justice", "criminalite",
                                  "cyber", "securite_civile")
    flux["souverainete_mde"] = _somme("relocalisations", "numerique", "agriculture")
    # Masse salariale enseignante ≈ 60 % de la dépense d'éducation.
    flux["enseignants_mde"] = round(0.6 * flux.get("education_mde", 0.0), 3)
    flux["alternatives_penales_mde"] = round(flux.get("criminalite_mde", 0.0), 3)
    flux["apl_delta_mde"] = round(flux.get("apl_mde", 0.0), 3)
    flux["exonerations_delta_mde"] = round(flux.get("exonerations_mde", 0.0), 3)
    flux["logement_social_milliers"] = round(flux.get("logement_social_milliers", 0.0), 3)
    for cle, mediateur in UNITES_CHAMPS.items():
        levier = LEVIERS[cle]
        montant = _montant_levier(levier, parametres.get(cle, levier.defaut), annee_index)
        if montant and levier.facteur:
            flux[f"{mediateur}_pts"] = flux.get(f"{mediateur}_pts", 0.0) + montant / levier.facteur
            flux[f"rec_{mediateur}_mde"] = flux.get(f"rec_{mediateur}_mde", 0.0) + montant
    return flux


# ────────────────────────────────────────────────────────────────────────────
# 4. Évaluation
# ────────────────────────────────────────────────────────────────────────────

def _base_indicateur(spec: SpecIndicateur, contexte: ContexteInstant) -> float:
    """Valeur « instant T » (réelle, datée) servant de point de départ."""
    base = spec.base
    if not isinstance(base, str):
        return float(base)
    correspondances = {
        "pib_par_habitant": lambda c: c.pib_nominal_mde * 1_000_000 / max(c.population, 1.0),
        "solde_commercial_mde": lambda c: -55.0,
        "deficit_pct_pib": lambda c: c.deficit_public_pct_pib,
        "dette_publique_pct_pib": lambda c: c.dette_publique_pct_pib,
        "charge_dette_base": lambda c: c.charge_dette_estimee_mde,
        "spread_base": lambda c: c.spread_oat_bund_bps,
        "prelevements_obligatoires_pct_pib": lambda c: c.prelevements_obligatoires_pct_pib,
        "chomage_pct": lambda c: c.chomage_pct,
        "inflation_pct": lambda c: c.inflation_pct,
        "taux_pauvrete_pct": lambda c: c.taux_pauvrete_pct,
        "indice_gini": lambda c: c.indice_gini,
        "effort_defense_base": lambda c: c.depenses_defense_pct_pib,
        "emissions_base": lambda c: 227.0,
        "risque_censure_base": lambda c: 52.0,
    }
    fabrique = correspondances.get(base)
    if fabrique is None:
        raise KeyError(f"base inconnue pour {spec.cle} : {base}")
    return float(fabrique(contexte))


def evaluer_indicateur(spec: SpecIndicateur, mediateurs: MediateursAnnee,
                       contexte: ContexteInstant) -> float:
    """Applique la fonction linéaire documentée de l'indicateur.

    Les coefficients sont exprimés :
      * en % de variation quand l'unité est relative (%, indice) ;
      * en unité absolue quand l'unité est absolue (Md€, mois, milliers…).
    """
    base = _base_indicateur(spec, contexte)
    unite = spec.unite
    relative = unite.startswith("%") or unite.startswith("indice")
    ecart = 0.0
    for mediateur, coefficient in spec.termes:
        ecart += coefficient * mediateurs.lire(mediateur)
    valeur = base * (1.0 + ecart / 100.0) if relative else base + ecart
    if spec.plancher is not None:
        valeur = max(spec.plancher, valeur)
    if spec.plafond is not None:
        valeur = min(spec.plafond, valeur)
    return round(valeur, spec.precision)


#: Sensibilité des scores de domaine : Δ relatif moyen × 16 → points de score.
SENSIBILITE_SCORE = 16.0
#: Plafond de contribution d'un indicateur isolé au score de son domaine : sans
#: ce garde-fou, un indicateur très volatil (chômage, spread) sature le domaine.
ECART_MAX_INDICATEUR = 0.15


def _score_domaine(series: list[tuple[SpecIndicateur, list[float]]],
                   references: dict[str, list[float]] | None = None) -> float:
    """Score 0-100 : écart relatif moyen signé, borné par une tangente hyperbolique.

    * avec `references`, le score mesure l'**impact de la politique** : écart entre
      la valeur finale simulée et la valeur finale de la trajectoire de référence
      (tous leviers neutres). 50 = politique sans effet sur le domaine ;
    * sans `references`, le score mesure la **tendance interne** de la trajectoire
      (année 1 → année 5) : c'est ainsi qu'est notée la référence elle-même
      (« ce qui se passerait si l'on ne décidait rien »).

    Le facteur 16 est calibré pour qu'une politique produisant +3 % d'amélioration
    moyenne des indicateurs d'un domaine gagne environ 20 points de score, tandis
    qu'un effet marginal de 0,3 % reste visible (+2 points).
    """
    ecarts: list[float] = []
    for spec, serie in series:
        if references and references.get(spec.cle):
            base, finale = references[spec.cle][-1], serie[-1]
        else:
            base, finale = serie[0], serie[-1]
        if abs(base) < 1e-9:
            continue
        ecart = spec.sens * (finale - base) / abs(base)
        ecarts.append(max(-ECART_MAX_INDICATEUR, min(ECART_MAX_INDICATEUR, ecart)))
    if not ecarts:
        return 50.0
    return round(50.0 + 50.0 * math.tanh(SENSIBILITE_SCORE * (sum(ecarts) / len(ecarts))), 1)


@dataclass
class ResultatDomaine:
    cle: str
    libelle: str
    description: str
    couleur: str
    score: float
    indicateurs: list[dict[str, Any]]
    #: Score de tendance de la trajectoire de référence (sans politique).
    tendance_reference: float | None = None

    def en_dict(self) -> dict[str, Any]:
        return asdict(self)


def evaluer_domaines(mediateurs_par_annee: list[MediateursAnnee],
                     contexte: ContexteInstant,
                     references: dict[str, list[float]] | None = None,
                     tendances: dict[str, float] | None = None) -> list[ResultatDomaine]:
    """Évalue les 20 domaines sur l'horizon simulé.

    `references` : séries d'indicateurs de la trajectoire de référence (leviers
    neutres). Fournies, elles transforment le score en **impact de la politique**
    (50 = aucune politique) et la tendance de référence est reportée à part.
    """
    resultats: list[ResultatDomaine] = []
    for domaine in DOMAINES:
        specs = [s for s in SPECS if s.domaine == domaine.cle]
        indicateurs: list[dict[str, Any]] = []
        series_pour_score: list[tuple[SpecIndicateur, list[float]]] = []
        for spec in specs:
            serie = [evaluer_indicateur(spec, m, contexte) for m in mediateurs_par_annee]
            series_pour_score.append((spec, serie))
            indicateurs.append({
                "cle": spec.cle,
                "libelle": spec.libelle,
                "unite": spec.unite,
                "sens": spec.sens,
                "valeur_initiale": serie[0],
                "valeur_finale": serie[-1],
                "variation": round(serie[-1] - serie[0], spec.precision),
                "variation_relative_pct": round(
                    (serie[-1] - serie[0]) / abs(serie[0]) * 100.0, 1
                ) if abs(serie[0]) > 1e-9 else 0.0,
                "serie": serie,
                "formule": spec.formule,
                "source": spec.source,
            })
        resultats.append(ResultatDomaine(
            cle=domaine.cle, libelle=domaine.libelle, description=domaine.description,
            couleur=domaine.couleur,
            score=_score_domaine(series_pour_score, references),
            indicateurs=indicateurs,
            tendance_reference=(tendances or {}).get(domaine.cle),
        ))
    return resultats


# ────────────────────────────────────────────────────────────────────────────
# 5. API publiques
# ────────────────────────────────────────────────────────────────────────────

def catalogue_domaines() -> list[dict[str, Any]]:
    """Description sérialisable des domaines et de leurs indicateurs."""
    return [
        {
            "cle": domaine.cle,
            "libelle": domaine.libelle,
            "description": domaine.description,
            "couleur": domaine.couleur,
            "priorite": domaine.priorite,
            "indicateurs": [
                {
                    "cle": spec.cle, "libelle": spec.libelle, "unite": spec.unite,
                    "sens": spec.sens, "formule": spec.formule, "source": spec.source,
                }
                for spec in SPECS if spec.domaine == domaine.cle
            ],
        }
        for domaine in DOMAINES
    ]


def decisions_depuis_flux(flux: dict[str, float]) -> dict[str, float]:
    """Agrégats affichés dans le bandeau d'impact."""
    recettes = flux.get("recettes_nouvelles_mde", 0.0)
    depenses = flux.get("depenses_nouvelles_mde", 0.0)
    return {
        "recettes_nouvelles_mde": round(recettes, 2),
        "depenses_nouvelles_mde": round(depenses, 2),
        "solde_annuel_mde": round(recettes - depenses, 2),
        "transferts_menages_mde": round(flux.get("transferts_menages_mde", 0.0), 2),
    }


def decision_moteur(parametres: dict[str, float], annee: int) -> DecisionPolitique:
    """Construit la `DecisionPolitique` transmise au moteur pour une année.

    * les leviers rattachés à un champ du moteur y sont écrits directement ;
    * les autres passent par les agrégats `recettes_nouvelles_mde` et
      `depenses_prioritaires_mde` (voir `model.py` et `moteur.py`).
    """
    index = max(0, annee - 1)
    decision = DecisionPolitique(annee=annee, description=f"Année {annee} — leviers libres")
    recettes_libres = 0.0
    depenses_libres = 0.0
    for cle, levier in LEVIERS.items():
        valeur = parametres.get(cle, levier.defaut)
        montant = _montant_levier(levier, valeur, index)
        if montant == 0.0 and levier.champ is None:
            continue
        if levier.champ:
            actuel = getattr(decision, levier.champ, None)
            if isinstance(actuel, bool):
                if valeur >= 0.5:
                    setattr(decision, levier.champ, True)
            elif levier.type == TYPE_CIBLE:
                # Le champ moteur attend un **niveau** (ex. % du PIB), pas un montant.
                setattr(decision, levier.champ, valeur)
            else:
                setattr(decision, levier.champ, (actuel or 0.0) + montant)
        elif levier.famille in FAMILLES_RECETTES:
            recettes_libres += montant
        elif levier.ligne in ("proportionnelle", "49_3", "convention", "anticorruption",
                              "decentralisation", "loyers", "temps_travail", "commerce"):
            # Réformes sans coût budgétaire direct modélisé.
            continue
        else:
            depenses_libres += montant
    decision.recettes_nouvelles_mde = round(recettes_libres, 2)
    decision.depenses_prioritaires_mde = round(depenses_libres, 2)
    return decision


def mediateurs_en_dict(mediateurs: MediateursAnnee) -> dict[str, Any]:
    return asdict(mediateurs)
