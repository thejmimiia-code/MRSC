"""
simulateur/parametres.py — Catalogue des leviers de politique publique.

Chaque levier est un **choix** que l'utilisateur peut régler librement dans
l'interface. Le catalogue est organisé en familles (fiscalité, dépenses
sociales, régalien, énergie, institutions…) et chaque levier déclare :

  * ses bornes et son pas (curseur) ou ses modalités (choix / interrupteur) ;
  * sa **traduction dans le moteur** (`champ` = champ de `DecisionPolitique`)
    ou son rattachement à une **ligne budgétaire** (`ligne` = poste de dépense
    ou de recette suivi par `domaines.py`) ;
  * son **profil de montée en charge** sur 5 ans (une réforme ne produit pas
    ses effets dès la première année) ;
  * sa **provenance documentaire** (`source`) quand le chiffrage s'appuie sur
    un texte, un rapport ou une loi de finances.

Rien n'est caché : l'interface affiche pour chaque levier son bornage, sa
source et le détail de son effet année par année.

Conventions d'unités
--------------------
  * `unite="Md€"`   : montant annuel en milliards d'euros (dépense ou recette) ;
  * `unite="%"`     : taux ou pourcentage de PIB, selon `echelle` ;
  * `unite="pts"`   : points de taux ou d'indice ;
  * `unite="€/tCO2"`, `"$/baril"`, `"€/MWh"`, `"pts de PIB"`, `"milliers"`, `"nb"` ;
  * `unite="bool"`  : réforme activée ou non (0/1).
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass, field
from typing import Any

# ────────────────────────────────────────────────────────────────────────────
# Structures
# ────────────────────────────────────────────────────────────────────────────

#: Types de levier (pilotent le rendu de l'interface).
TYPE_CURSEUR = "curseur"     # valeur numérique continue sur un intervalle
TYPE_CHOIX = "choix"         # liste de modalités discrètes
TYPE_INTERRUPTEUR = "interrupteur"   # activé / désactivé
TYPE_CIBLE = "cible"         # niveau à atteindre (trajectoire), ex. effort défense


@dataclass(frozen=True)
class LigneBudgetaire:
    """Poste de recette ou de dépense auquel un levier est rattaché.

    `sens` = "recette" (entrée d'argent) ou "depense" (sortie).
    `base_mde` = montant annuel de référence (dans la structure actuelle).
    `domaines` = domaines d'action publique directement concernés.
    """

    cle: str
    libelle: str
    sens: str
    base_mde: float
    domaines: tuple[str, ...] = ()
    source: str = ""
    categorie_comptable: str = ""   # ex. "APU", "ODM", "PLF mission"


@dataclass
class Levier:
    """Un choix de politique publique, borné et documenté."""

    cle: str
    libelle: str
    famille: str
    description: str
    unite: str = "Md€"
    type: str = TYPE_CURSEUR
    defaut: float = 0.0
    minimum: float | None = None
    maximum: float | None = None
    pas: float | None = None
    modalites: tuple[tuple[str, float], ...] = ()   # (libellé, valeur) pour TYPE_CHOIX
    #: Champ de `DecisionPolitique` alimenté directement (le cas échéant).
    champ: str | None = None
    #: Facteur de conversion levier → champ (ex. taux de PIB → Md€).
    facteur: float = 1.0
    #: Ligne budgétaire suivie par `domaines.py` (le cas échéant).
    ligne: str | None = None
    #: Profil de montée en charge par année (fractions 1re → 5e année).
    profil: tuple[float, float, float, float, float] = (0.4, 0.7, 0.9, 1.0, 1.0)
    #: Effets directs documentés sur les domaines (identifiant → effet par unité).
    effets_directs: dict[str, float] = field(default_factory=dict)
    source: str = ""
    tags: tuple[str, ...] = ()
    precision: int = 1

    # — commodités d'affichage ————————————————————————————————————————————
    @property
    def bornes(self) -> tuple[float, float]:
        mini = self.minimum if self.minimum is not None else 0.0
        maxi = self.maximum if self.maximum is not None else 1.0
        return mini, maxi

    def modalites_serialisables(self) -> list[dict[str, Any]]:
        return [{"libelle": libelle, "valeur": valeur} for libelle, valeur in self.modalites]

    def en_dict(self) -> dict[str, Any]:
        return {
            "cle": self.cle,
            "libelle": self.libelle,
            "famille": self.famille,
            "description": self.description,
            "unite": self.unite,
            "type": self.type,
            "defaut": self.defaut,
            "minimum": self.minimum,
            "maximum": self.maximum,
            "pas": self.pas,
            "modalites": self.modalites_serialisables(),
            "champ": self.champ,
            "ligne": self.ligne,
            "profil": list(self.profil),
            "effets_directs": dict(self.effets_directs),
            "source": self.source,
            "tags": list(self.tags),
            "precision": self.precision,
        }


#: Familles de leviers (ordre d'affichage dans l'interface).
FAMILLES: dict[str, dict[str, str]] = {
    "fiscalite_menages": {"libelle": "Fiscalité des ménages", "couleur": "#38bdf8"},
    "fiscalite_entreprises": {"libelle": "Fiscalité des entreprises & fraude", "couleur": "#0ea5e9"},
    "depenses_sociales": {"libelle": "Protection sociale & solidarité", "couleur": "#22c55e"},
    "sante": {"libelle": "Santé", "couleur": "#14b8a6"},
    "education_recherche": {"libelle": "Éducation, recherche, jeunesse", "couleur": "#a855f7"},
    "travail_emploi": {"libelle": "Travail, emploi, formation", "couleur": "#f59e0b"},
    "regalien": {"libelle": "Défense, sécurité, justice", "couleur": "#ef4444"},
    "energie_climat": {"libelle": "Énergie & climat", "couleur": "#84cc16"},
    "industrie_souverainete": {"libelle": "Industrie, numérique, souveraineté", "couleur": "#6366f1"},
    "logement_territoires": {"libelle": "Logement, territoires, collectivités", "couleur": "#ec4899"},
    "etat_fonction_publique": {"libelle": "État, fonction publique, simplification", "couleur": "#94a3b8"},
    "institutions_democratie": {"libelle": "Institutions & démocratie", "couleur": "#eab308"},
    "international": {"libelle": "Europe, diplomatie, migration", "couleur": "#f472b6"},
    "exogene_monde": {"libelle": "Chocs mondiaux (exogènes)", "couleur": "#64748b"},
}

LEVIERS: dict[str, Levier] = {}


def _lev(levier: Levier) -> Levier:
    if levier.cle in LEVIERS:
        raise ValueError(f"levier dupliqué : {levier.cle}")
    LEVIERS[levier.cle] = levier
    return levier


# ────────────────────────────────────────────────────────────────────────────
# 1. FISCALITÉ DES MÉNAGES
# ────────────────────────────────────────────────────────────────────────────

_lev(Levier(
    cle="tva_taux_normal",
    libelle="TVA — taux normal",
    famille="fiscalite_menages",
    description="Variation en points du taux normal de TVA (20 % aujourd'hui). "
                "Assiette taxée ≈ 780 Md€ (taux normal) : +1 point ≈ +7,8 Md€ de recettes.",
    unite="pts", defaut=0.0, minimum=-3.0, maximum=5.0, pas=0.5,
    ligne="tva", facteur=7.8,
    profil=(1.0, 1.0, 1.0, 1.0, 1.0),
    effets_directs={"pouvoir_achat": -0.9, "consommation": -0.8, "inflation": 0.35},
    source="Insee, comptes nationaux 2024 : consommation effective des ménages ≈ 1 560 Md€.",
))
_lev(Levier(
    cle="tva_energie_5_5",
    libelle="TVA sur l'énergie à 5,5 %",
    famille="fiscalite_menages",
    description="Bascule le gaz, l'électricité et les carburants au taux réduit de 5,5 %. "
                "Coût estimé ≈ 9 Md€/an (dossier de mandature).",
    unite="bool", type=TYPE_INTERRUPTEUR, defaut=0.0,
    champ="baisse_tva_energie_5_5_mde", facteur=9.0,
    profil=(1.0, 1.0, 1.0, 1.0, 1.0),
    effets_directs={"pouvoir_achat": 3.8, "inflation": -0.35, "pauvrete": -0.4},
    source="Article 278-0 bis CGI ; chiffrage du DOSSIER_DE_MANDATURE_GLOBAL.md.",
))
_lev(Levier(
    cle="csg_crds_hausse",
    libelle="CSG / CRDS — hausse",
    famille="fiscalite_menages",
    description="Hausse en points de la CSG-CRDS sur l'ensemble des revenus. "
                "Assiette ≈ 1 100 Md€ : +1 point ≈ +11 Md€.",
    unite="pts", defaut=0.0, minimum=0.0, maximum=3.0, pas=0.25,
    ligne="csg", facteur=11.0, profil=(1.0, 1.0, 1.0, 1.0, 1.0),
    effets_directs={"pouvoir_achat": -1.6, "consommation": -1.2, "sante": 0.6, "inégalités": -0.3},
    source="URSSAF / PLFSS ; CSG sur revenus d'activité et de remplacement.",
))
_lev(Levier(
    cle="ir_tranche_superieure",
    libelle="Impôt sur le revenu — tranche supérieure",
    famille="fiscalite_menages",
    description="Relèvement en points du taux marginal de la tranche la plus élevée "
                "(45 % aujourd'hui). Rendement ≈ 1,1 Md€ par point (hors effets comportementaux).",
    unite="pts", defaut=0.0, minimum=-5.0, maximum=15.0, pas=1.0,
    ligne="ir", facteur=1.1, profil=(1.0, 1.0, 1.0, 1.0, 1.0),
    effets_directs={"inégalités": -0.45, "pouvoir_achat": -0.15, "attractivite": -0.2},
    source="PLF — évaluation des voies et moyens, tranches hautes du barème.",
))
_lev(Levier(
    cle="isf_retablissement",
    libelle="Impôt sur la fortune (base élargie)",
    famille="fiscalite_menages",
    description="Rétablissement d'un impôt annuel sur les patrimoines, avec abattement "
                "sur la résidence principale. Rendement brut de référence : 5 Md€.",
    unite="bool", type=TYPE_INTERRUPTEUR, defaut=0.0,
    ligne="isf", facteur=5.0, profil=(1.0, 1.0, 1.0, 1.0, 1.0),
    effets_directs={"inégalités": -0.8, "attractivite": -0.6, "investissement": -0.3},
    source="Rapports IGF/Conseil d'analyse économique ; ordres de grandeur IFI 2024 ≈ 2 Md€.",
))
_lev(Levier(
    cle="succession_reforme",
    libelle="Droits de succession — réfaction à 100 000 €",
    famille="fiscalite_menages",
    description="Relèvement de l'abattement et barème simplifié ; rendement net "
                "variable selon le seuil retenu (−2 à +4 Md€).",
    unite="Md€", defaut=0.0, minimum=-2.0, maximum=4.0, pas=0.5,
    ligne="succession", profil=(0.5, 0.8, 1.0, 1.0, 1.0),
    effets_directs={"inégalités": -0.35, "pouvoir_achat": 0.2},
    source="DGFiP, statistiques des droits de mutation à titre gratuit.",
))
_lev(Levier(
    cle="flat_tax_suppression",
    libelle="Flat tax du capital — suppression",
    famille="fiscalite_menages",
    description="Retour au barème progressif pour les revenus du capital "
                "(coût ≈ 4 Md€ de recettes en moins, gain d'équité).",
    unite="bool", type=TYPE_INTERRUPTEUR, defaut=0.0,
    ligne="flat_tax", facteur=-4.0, profil=(1.0, 1.0, 1.0, 1.0, 1.0),
    effets_directs={"inégalités": -0.5, "investissement": -0.2, "attractivite": -0.3},
    source="Rapport du Conseil des prélèvements obligatoires sur la fiscalité du capital.",
))
_lev(Levier(
    cle="niches_fiscales",
    libelle="Niches fiscales inefficaces — extinction",
    famille="fiscalite_menages",
    description="Suppression progressive des niches à faible rendement social ou "
                "environnemental. Gisement total évalué à 90 Md€ ; le curseur porte sur "
                "la fraction supprimée (un montant en Md€ est déduit).",
    unite="%", defaut=0.0, minimum=0.0, maximum=100.0, pas=5.0,
    champ="extinction_niches_inefficaces_mde", facteur=0.09,
    profil=(0.4, 0.7, 0.9, 1.0, 1.0),
    effets_directs={"inégalités": 0.15, "investissement": -0.25},
    source="PLF — annexe « dépenses fiscales » ; DOSSIER_DE_MANDATURE_GLOBAL.md (Volet 3).",
))
_lev(Levier(
    cle="taxe_carbone",
    libelle="Taxe carbone — trajectoire",
    famille="fiscalite_menages",
    description="Prix du carbone sur les énergies fossiles hors ETS. "
                "10 €/t ≈ +3,5 Md€ de recettes ; compensation possible via chèque énergie.",
    unite="€/tCO2", defaut=0.0, minimum=0.0, maximum=150.0, pas=5.0,
    ligne="taxe_carbone", facteur=0.35,
    profil=(0.5, 0.8, 1.0, 1.0, 1.0),
    effets_directs={"emissions": -0.25, "pouvoir_achat": -0.5, "inflation": 0.12,
                    "inégalités": 0.2, "energie": 0.3},
    source="Quatre fois pour un climat ; Conseil d'analyse économique (élasticité -0,25 %/€).",
))
_lev(Levier(
    cle="cheque_energie",
    libelle="Chèque énergie — revalorisation",
    famille="fiscalite_menages",
    description="Relèvement du chèque énergie pour compenser la fiscalité carbone "
                "et la précarité énergétique.",
    unite="Md€", defaut=0.0, minimum=0.0, maximum=6.0, pas=0.25,
    ligne="cheque_energie",
    profil=(1.0, 1.0, 1.0, 1.0, 1.0),
    effets_directs={"pauvrete": -0.35, "pouvoir_achat": 0.3, "energie": 0.2},
    source="~5,7 millions de ménages bénéficiaires ; montant moyen ≈ 150 €.",
))
_lev(Levier(
    cle="lutte_fraude_fiscale_ia",
    libelle="Fraude fiscale — IA et data-mining",
    famille="fiscalite_entreprises",
    description="Croisement automatisé des données (DSN, DAC7/DAC8, facturation) pour "
                "recouvrer la fraude fiscale et sociale. Dossier de mandature : 10 Md€/an.",
    unite="Md€", defaut=0.0, minimum=0.0, maximum=10.0, pas=0.5,
    champ="recettes_fraude_ia_mde",
    profil=(0.2, 0.45, 0.7, 0.9, 1.0),
    effets_directs={"inégalités": -0.4, "confiance": 0.5, "budget": 1.0},
    source="DOSSIER_DE_MANDATURE_GLOBAL.md (Volet 2) ; Cour des comptes 2024.",
))
_lev(Levier(
    cle="fraude_sociale",
    libelle="Fraude sociale criminelle — redressement",
    famille="fiscalite_entreprises",
    description="Ciblage des fraudes organisées (faux droits, trafics) sans viser les "
                "erreurs de bonne foi. Dossier de mandature : 2,5 Md€/an.",
    unite="Md€", defaut=0.0, minimum=0.0, maximum=4.0, pas=0.25,
    champ="fraude_sociale_criminelle_mde",
    profil=(0.2, 0.4, 0.6, 0.8, 1.0),
    effets_directs={"solidarite": -0.2, "confiance": 0.4},
    source="DOSSIER_DE_MANDATURE_GLOBAL.md (Volet 3).",
))
_lev(Levier(
    cle="conditionnement_aides_entreprises",
    libelle="Aides aux entreprises — conditionnalité",
    famille="fiscalite_entreprises",
    description="Ciblage des aides (environnement, emploi local, salaires décents) et "
                "suppression des aides non conditionnées. Gisement 20 Md€.",
    unite="Md€", defaut=0.0, minimum=0.0, maximum=20.0, pas=0.5,
    champ="conditionnement_aides_entreprises_mde",
    profil=(0.1, 0.35, 0.6, 0.85, 1.0),
    effets_directs={"investissement": -0.3, "emploi": -0.15, "climat": 0.4, "inégalités": -0.3},
    source="DOSSIER_DE_MANDATURE_GLOBAL.md (Volet 2) ; Cour des comptes, aides économiques.",
))
_lev(Levier(
    cle="taxe_superprofits",
    libelle="Superprofits — contribution temporaire",
    famille="fiscalite_entreprises",
    description="Contribution sur les bénéfices exceptionnels (énergie, transport "
                "maritime, rachats d'actions) : 6 Md€ par an selon le dossier.",
    unite="Md€", defaut=0.0, minimum=0.0, maximum=15.0, pas=0.5,
    champ="taxe_superprofits_rachats_mde",
    profil=(1.0, 1.0, 1.0, 1.0, 1.0),
    effets_directs={"inégalités": -0.5, "investissement": -0.2},
    source="Règlement UE 2022/1854 (transposition) ; dossier de mandature.",
))
_lev(Levier(
    cle="extension_ttf",
    libelle="Taxe sur les transactions financières — extension",
    famille="fiscalite_entreprises",
    description="Élargissement de l'assiette aux produits dérivés et aux transactions "
                "intra-journalières : +5 Md€/an.",
    unite="Md€", defaut=0.0, minimum=0.0, maximum=8.0, pas=0.5,
    champ="extension_ttf_mde",
    profil=(0.3, 0.6, 0.8, 1.0, 1.0),
    effets_directs={"inégalités": -0.3, "attractivite": -0.25, "budget": 0.8},
    source="DOSSIER_DE_MANDATURE_GLOBAL.md ; étude d'impact Sénat sur la TTF.",
))
_lev(Levier(
    cle="impot_minimum_pilier2",
    libelle="Impôt minimum mondial (OCDE Pilier 2)",
    famille="fiscalite_entreprises",
    description="Application effective du taux plancher de 15 % aux multinationales "
                "(CGI art. 223 VJ) : ~8 Md€ de recettes potentielles.",
    unite="Md€", defaut=0.0, minimum=0.0, maximum=8.0, pas=0.5,
    champ="recettes_pilier2_ocde_mde",
    profil=(0.4, 0.7, 0.9, 1.0, 1.0),
    effets_directs={"inégalités": -0.35, "attractivite": -0.2},
    source="Accord OCDE/G20 ; directive UE 2022/2523.",
))
_lev(Levier(
    cle="macf_carbone_frontiere",
    libelle="Mécanisme d'ajustement carbone aux frontières",
    famille="fiscalite_entreprises",
    description="Application du MACF aux importations à forte intensité carbone "
                "(acier, ciment, aluminium, engrais) : ~6 Md€/an à terme.",
    unite="Md€", defaut=0.0, minimum=0.0, maximum=6.0, pas=0.25,
    champ="recettes_macf_carbone_mde",
    profil=(0.2, 0.5, 0.8, 1.0, 1.0),
    effets_directs={"emissions": -0.2, "industrie": 0.5, "inflation": 0.08},
    source="Règlement UE 2023/956 — MACF en phase transitoire puis définitive.",
))


# ────────────────────────────────────────────────────────────────────────────
# 2. PROTECTION SOCIALE & SOLIDARITÉ
# ────────────────────────────────────────────────────────────────────────────

_lev(Levier(
    cle="revalorisation_retraites",
    libelle="Revalorisation des retraites (au-delà de l'inflation)",
    famille="depenses_sociales",
    description="Point supplémentaire de revalorisation annuelle. "
                "Coût ≈ 4,5 Md€ par point (masse des pensions ≈ 380 Md€).",
    unite="pts", defaut=0.0, minimum=-2.0, maximum=3.0, pas=0.25,
    ligne="retraites", facteur=4.5, profil=(1.0, 1.0, 1.0, 1.0, 1.0),
    effets_directs={"pauvrete": -0.35, "pouvoir_achat": 0.55, "solidarite": 0.8,
                    "consommation": 0.4},
    source="CNAV, rapport annuel ; effet retour consommation ≈ 0,4.",
))
_lev(Levier(
    cle="revalorisation_minima_sociaux",
    libelle="Minima sociaux — coup de pouce",
    famille="depenses_sociales",
    description="Revalorisation coordonnée du RSA, de l'AAH, de l'APA et des minimas "
                "retraite. 1 Md€ ≈ +1,7 % de pouvoir d'achat pour 2 millions de ménages.",
    unite="Md€", defaut=0.0, minimum=0.0, maximum=8.0, pas=0.25,
    ligne="minima_sociaux",
    profil=(1.0, 1.0, 1.0, 1.0, 1.0),
    effets_directs={"pauvrete": -0.5, "pouvoir_achat": 0.5, "inégalités": -0.4,
                    "consommation": 0.5},
    source="DREES, minimum sociaux — 2,1 M foyers au RSA, 1,3 M bénéficiaires AAH.",
))
_lev(Levier(
    cle="aide_logement",
    libelle="Aides personnelles au logement (APL/ALS)",
    famille="depenses_sociales",
    description="Réduction ou hausse des aides au logement. Une baisse de 3 Md€ transfère "
                "la charge sur les locataires modestes (−0,6 pt de pouvoir d'achat).",
    unite="Md€", defaut=0.0, minimum=-4.0, maximum=5.0, pas=0.25,
    ligne="apl", profil=(1.0, 1.0, 1.0, 1.0, 1.0),
    effets_directs={"pauvrete": 0.45, "pouvoir_achat": -0.45, "logement": 0.5},
    source="CNAF ; rapport de la Cour des comptes sur les aides au logement.",
))
_lev(Levier(
    cle="precarite_energetique",
    libelle="Précarité énergétique — bouclier ciblé",
    famille="depenses_sociales",
    description="Extension du chèque énergie et des dispositifs d'effacement de dettes "
                "d'énergie : ciblage des ménages sous le seuil de pauvreté.",
    unite="Md€", defaut=0.0, minimum=0.0, maximum=5.0, pas=0.25,
    ligne="cheque_energie",
    profil=(1.0, 1.0, 1.0, 1.0, 1.0),
    effets_directs={"pauvrete": -0.4, "energie": 0.35, "cohesion": 0.4},
    source="ONPE, rapport annuel sur la précarité énergétique (12 % des ménages).",
))
_lev(Levier(
    cle="aide_alimentaire",
    libelle="Aide alimentaire et lutte contre la pauvreté",
    famille="depenses_sociales",
    description="Renforcement des dispositifs d'aide alimentaire et de première nécessité "
                "(le recours aux distributions a augmenté de 30 % depuis 2022).",
    unite="Md€", defaut=0.0, minimum=0.0, maximum=4.0, pas=0.25,
    ligne="aide_alimentaire",
    profil=(1.0, 1.0, 1.0, 1.0, 1.0),
    effets_directs={"pauvrete": -0.35, "cohesion": 0.6, "sante": 0.25},
    source="Rapports du Secours catholique / Restos du cœur ; crédits mission Solidarité.",
))
_lev(Levier(
    cle="aide_enfance_jeunesse",
    libelle="Protection de l'enfance & jeunesse",
    famille="depenses_sociales",
    description="Moyens supplémentaires pour l'ASE, la PMI et la politique de la jeunesse "
                "(délais de prise en charge, places en crèche).",
    unite="Md€", defaut=0.0, minimum=0.0, maximum=6.0, pas=0.25,
    ligne="enfance",
    profil=(0.6, 0.85, 1.0, 1.0, 1.0),
    effets_directs={"pauvrete": -0.4, "education": 0.5, "cohesion": 0.5, "demographie": 0.3},
    source="Cour des comptes — protection de l'enfance ; convention d'objectifs État/départements.",
))
_lev(Levier(
    cle="dependance_grand_age",
    libelle="Autonomie & grand âge (APA, EHPAD)",
    famille="depenses_sociales",
    description="Réponse à la perte d'autonomie : tarification des EHPAD, aide à domicile, "
                "revalorisation des métiers du care.",
    unite="Md€", defaut=0.0, minimum=0.0, maximum=12.0, pas=0.5,
    ligne="dependance", profil=(0.5, 0.8, 1.0, 1.0, 1.0),
    effets_directs={"sante": 0.6, "pauvrete": -0.3, "emploi": 0.4, "demographie": 0.5,
                    "cohesion": 0.5},
    source="Rapport Libault (grand âge et autonomie) ; branche Autonomie de la Sécu.",
))


# ────────────────────────────────────────────────────────────────────────────
# 3. SANTÉ
# ────────────────────────────────────────────────────────────────────────────

_lev(Levier(
    cle="ondam_variation",
    libelle="ONDAM — évolution de l'objectif de dépenses d'assurance maladie",
    famille="sante",
    description="Variation en points de l'ONDAM (≈ 260 Md€). +1 pt ≈ 2,6 Md€. "
                "Un ONDAM sous 2 %/an dégrade la qualité de prise en charge.",
    unite="pts", defaut=0.0, minimum=-2.0, maximum=3.0, pas=0.25,
    ligne="ondam", facteur=2.6, profil=(1.0, 1.0, 1.0, 1.0, 1.0),
    effets_directs={"sante": 0.9, "inflation": 0.02, "emploi": 0.3},
    source="PLFSS — ONDAM ; Cour des comptes, rapport sur l'application des lois de financement.",
))
_lev(Levier(
    cle="hopital_public",
    libelle="Hôpital public — investissement et emplois",
    famille="sante",
    description="Financement de l'hôpital (lits, urgences, personnels soignants) "
                "et de la reconstruction des bâtiments.",
    unite="Md€", defaut=0.0, minimum=-5.0, maximum=15.0, pas=0.5,
    ligne="hopital", profil=(0.5, 0.75, 0.9, 1.0, 1.0),
    effets_directs={"sante": 1.1, "emploi": 0.5, "territoires": 0.5, "investissement": 0.4},
    source="Fédération hospitalière de France ; Ségur de la santé.",
))
_lev(Levier(
    cle="deserts_medicaux",
    libelle="Lutte contre les déserts médicaux",
    famille="sante",
    description="Financement de maisons de santé, régulation de l'installation des "
                "médecins et télémédecine dans les territoires carencés.",
    unite="Md€", defaut=0.0, minimum=0.0, maximum=8.0, pas=0.25,
    ligne="deserts_medicaux", profil=(0.4, 0.7, 0.9, 1.0, 1.0),
    effets_directs={"sante": 0.7, "territoires": 0.9, "cohesion": 0.5},
    source="DREES — accessibilité aux médecins généralistes ; 6 % de la population en désert.",
))
_lev(Levier(
    cle="prevention_sante",
    libelle="Prévention & santé publique",
    famille="sante",
    description="Vaccination, dépistage, santé mentale, éducation à la santé, "
                "lutte contre les addictions.",
    unite="Md€", defaut=0.0, minimum=0.0, maximum=6.0, pas=0.25,
    ligne="prevention", profil=(0.6, 0.85, 1.0, 1.0, 1.0),
    effets_directs={"sante": 0.8, "solidarite": 0.3, "budget": 0.25},
    source="OCDE, « Panorama de la santé » : 2 % des dépenses de santé en France (prévention).",
))
_lev(Levier(
    cle="taxe_comportements",
    libelle="Taxes comportementales (tabac, alcool, sucre)",
    famille="sante",
    description="Hausse des accises sur les produits nocifs : effet sanitaire différé, "
                "recettes et risque de marché parallèle.",
    unite="Md€", defaut=0.0, minimum=0.0, maximum=5.0, pas=0.25,
    ligne="accises", profil=(0.6, 0.9, 1.0, 1.0, 1.0),
    effets_directs={"sante": 0.5, "inflation": 0.05, "inégalités": 0.25, "pauvrete": 0.15},
    source="OFDT / Santé publique France ; élasticité-prix du tabac ≈ −0,4.",
))
_lev(Levier(
    cle="medicaments_souverainete",
    libelle="Production de médicaments sur le territoire",
    famille="sante",
    description="Plan de relocalisation des principes actifs (pénuries de 2022-2024) "
                "et constitution de stocks stratégiques.",
    unite="Md€", defaut=0.0, minimum=0.0, maximum=7.0, pas=0.25,
    ligne="medicaments", profil=(0.3, 0.6, 0.85, 1.0, 1.0),
    effets_directs={"sante": 0.6, "industrie": 0.5, "souverainete": 0.7},
    source="ANSM/ANEPC — plans de sécurisation ; académie de pharmacie.",
))


# ────────────────────────────────────────────────────────────────────────────
# 4. ÉDUCATION, RECHERCHE, JEUNESSE
# ────────────────────────────────────────────────────────────────────────────

_lev(Levier(
    cle="budget_education",
    libelle="Budget de l'Éducation nationale",
    famille="education_recherche",
    description="Moyens supplémentaires pour l'école primaire et le secondaire "
                "(dédoublement, soutien, remplacement) : priorité documentée du dossier.",
    unite="Md€", defaut=0.0, minimum=-8.0, maximum=20.0, pas=0.5,
    ligne="education", profil=(0.5, 0.8, 0.9, 1.0, 1.0),
    effets_directs={"education": 1.0, "inégalités": -0.5, "emploi": 0.25, "democratie": 0.3},
    source="Loi de finances — mission Enseignement scolaire (≈ 63 Md€).",
))
_lev(Levier(
    cle="revalorisation_enseignants",
    libelle="Revalorisation des enseignants",
    famille="education_recherche",
    description="Hausse indemnitaire et de grille : attraction et fidélisation "
                "des professeurs (1 Md€ ≈ 250 € nets annuels par agent).",
    unite="Md€", defaut=0.0, minimum=0.0, maximum=8.0, pas=0.25,
    ligne="education", profil=(1.0, 1.0, 1.0, 1.0, 1.0),
    effets_directs={"education": 0.6, "emploi": 0.3, "pouvoir_achat": 0.2},
    source="Grenelle de l'éducation ; rapports IGESR sur l'attractivité du métier.",
))
_lev(Levier(
    cle="budget_recherche",
    libelle="Recherche & innovation (ANR, CNRS, universités)",
    famille="education_recherche",
    description="Effort public de recherche visant 1,2 % du PIB (contre ~0,8 % "
                "hors crédit d'impôt). Effet de long terme sur la productivité.",
    unite="Md€", defaut=0.0, minimum=0.0, maximum=15.0, pas=0.5,
    ligne="recherche", profil=(0.4, 0.6, 0.8, 1.0, 1.0),
    effets_directs={"education": 0.5, "innovation": 1.2, "croissance": 0.12,
                    "souverainete": 0.5},
    source="MESR — effort de recherche ; OCDE, taux de retour social de la R&D publique.",
))
_lev(Levier(
    cle="formation_professionnelle",
    libelle="Formation professionnelle & apprentissage",
    famille="education_recherche",
    description="Financement de la requalification des travailleurs exposés aux "
                "transitions (IA, énergie, industrie).",
    unite="Md€", defaut=0.0, minimum=0.0, maximum=12.0, pas=0.5,
    ligne="formation", profil=(0.5, 0.75, 0.9, 1.0, 1.0),
    effets_directs={"emploi": 0.9, "education": 0.4, "industrie": 0.3, "pauvrete": -0.3},
    source="France Compétences ; plan d'investissement dans les compétences (PIC).",
))
_lev(Levier(
    cle="cantine_gratuite",
    libelle="Gratuité de la restauration scolaire",
    famille="education_recherche",
    description="Repas scolaire gratuit ou à tarif très modulé : effet direct sur la "
                "pauvreté des enfants et l'alimentation.",
    unite="Md€", defaut=0.0, minimum=0.0, maximum=5.0, pas=0.25,
    ligne="education", profil=(1.0, 1.0, 1.0, 1.0, 1.0),
    effets_directs={"pauvrete": -0.4, "sante": 0.3, "education": 0.25},
    source="CNAF, évaluation des tarifs de cantine ; collectivités territoriales.",))


# ────────────────────────────────────────────────────────────────────────────
# 5. TRAVAIL, EMPLOI, SALAIRES
# ────────────────────────────────────────────────────────────────────────────

_lev(Levier(
    cle="smic_revalorisation",
    libelle="SMIC — coup de pouce annuel",
    famille="travail_emploi",
    description="Revalorisation annuelle au-delà de l'inflation. Effet double : "
                "pouvoir d'achat des salariés modestes et coût pour les TPE.",
    unite="pts", defaut=0.0, minimum=0.0, maximum=6.0, pas=0.5,
    ligne="smic", facteur=2.4, profil=(1.0, 1.0, 1.0, 1.0, 1.0),
    effets_directs={"pouvoir_achat": 0.8, "emploi": -0.25, "pauvrete": -0.5,
                    "inflation": 0.1, "inegalites": -0.35},
    source="Groupe d'expertise sur le SMIC ; élasticité emploi faible mais non nulle.",
))
_lev(Levier(
    cle="partage_valeur",
    libelle="Partage de la valeur (intéressement, dividendes)",
    famille="travail_emploi",
    description="Accord de partage de la valeur obligatoire et encadrement des rachats "
                "d'actions pour les entreprises aidées : relève la part salariale.",
    unite="Md€", defaut=0.0, minimum=0.0, maximum=8.0, pas=0.25,
    ligne="partage_valeur", profil=(0.5, 0.8, 1.0, 1.0, 1.0),
    effets_directs={"pouvoir_achat": 0.5, "inegalites": -0.5, "consommation": 0.35},
    source="Loi PACTE ; rapports DARES sur l'épargne salariale (≈ 18 Md€ distribués).",
))
_lev(Levier(
    cle="temps_de_travail",
    libelle="Temps de travail (semaine / heures supplémentaires)",
    famille="travail_emploi",
    description="Débat 32 h ↔ 39 h : le curseur retranche ou ajoute des heures "
                "hebdomadaires. Effet simulé sur l'activité et la santé au travail.",
    unite="h", defaut=0.0, minimum=-3.0, maximum=3.0, pas=0.5,
    ligne="temps_travail",
    profil=(0.5, 0.8, 1.0, 1.0, 1.0),
    effets_directs={"emploi": 0.6, "pouvoir_achat": 0.6, "sante": 0.4, "croissance": 0.15,
                    "cohesion": 0.3},
    source="Études OFCE / DARES sur la durée du travail ; conventions collectives.",
))
_lev(Levier(
    cle="cotisations_bas_salaires",
    libelle="Exonérations de cotisations — bas salaires",
    famille="travail_emploi",
    description="Allègement ou suppression des réductions générales sur les bas salaires "
                "(≈ 12 Md€). Effet emploi de premier ordre.",
    unite="Md€", defaut=0.0, minimum=-8.0, maximum=4.0, pas=0.5,
    ligne="exonerations", profil=(0.8, 1.0, 1.0, 1.0, 1.0),
    effets_directs={"emploi": -1.0, "pauvrete": 0.3, "pouvoir_achat": -0.3, "sante": 0.3},
    source="Comité d'évaluation des aides publiques aux entreprises ; études INSEE.",
))
_lev(Levier(
    cle="police_sociale_emploi",
    libelle="Contrôle du travail & lutte contre le travail dissimulé",
    famille="travail_emploi",
    description="Effectifs d'inspection (1 700 agents aujourd'hui) et ciblage des "
                "secteurs à forte fraude : recettes + protection des salariés.",
    unite="Md€", defaut=0.0, minimum=0.0, maximum=3.0, pas=0.25,
    ligne="inspection_travail", profil=(0.4, 0.7, 0.9, 1.0, 1.0),
    effets_directs={"emploi": 0.3, "pauvrete": -0.25, "confiance": 0.35, "budget": 0.5},
    source="DARES, rapports de l'inspection du travail ; plan de lutte contre le travail illégal.",
))


# ────────────────────────────────────────────────────────────────────────────
# 6. DÉFENSE, SÉCURITÉ, JUSTICE
# ────────────────────────────────────────────────────────────────────────────

_lev(Levier(
    cle="effort_defense_pct_pib",
    libelle="Effort de défense (% du PIB)",
    famille="regalien",
    description="Trajectoire de la loi de programmation militaire et cible OTAN de La Haye "
                "(3,5 % du PIB en 2035). Chaque point de PIB ≈ 30 Md€/an.",
    unite="% du PIB", type=TYPE_CIBLE, defaut=2.1, minimum=1.5, maximum=5.0, pas=0.1,
    champ="effort_defense_cible_pct_pib", facteur=30.15,
    profil=(0.3, 0.5, 0.7, 0.85, 1.0),
    effets_directs={"defense": 1.2, "souverainete": 0.8, "industrie": 0.5, "budget": -1.0,
                    "verdissement": -0.15},
    source="LPM 2024-2030 ; sommet OTAN de La Haye (5 % dont 1,5 % d'infrastructures).",
))
_lev(Levier(
    cle="reserve_securite_nationale",
    libelle="Réserve et préparation nationale (sécurité civile)",
    famille="regalien",
    description="Montée en puissance de la réserve opérationnelle et des moyens de "
                "sécurité civile (feux, inondations, pandémies).",
    unite="Md€", defaut=0.0, minimum=0.0, maximum=6.0, pas=0.25,
    ligne="securite_civile", profil=(0.4, 0.65, 0.85, 1.0, 1.0),
    effets_directs={"securite": 0.7, "resilience": 0.9, "territoires": 0.4, "cohesion": 0.4},
    source="Direction générale de la sécurité civile ; SNS (stratégie nationale de résilience).",
))
_lev(Levier(
    cle="effectifs_securite",
    libelle="Effectifs police & gendarmerie",
    famille="regalien",
    description="Création ou suppression de postes (en milliers). "
                "1 000 postes ≈ 60 M€/an ; effet direct sur la présence territoriale.",
    unite="milliers", defaut=0.0, minimum=-20.0, maximum=30.0, pas=1.0,
    ligne="police", facteur=0.06,
    profil=(0.3, 0.6, 0.8, 1.0, 1.0),
    effets_directs={"securite": 0.9, "territoires": 0.5, "confiance": 0.3},
    source="LOPMI 2022-2027 (8 500 créations) ; rapport IGPN/IGGN annuel.",
))
_lev(Levier(
    cle="budget_justice",
    libelle="Budget de la justice",
    famille="regalien",
    description="Moyens judiciaires (magistrats, greffes, numérique) : la France dépense "
                "~0,35 % du PIB, contre 0,5 % en Allemagne.",
    unite="Md€", defaut=0.0, minimum=-2.0, maximum=10.0, pas=0.25,
    ligne="justice", profil=(0.5, 0.75, 0.9, 1.0, 1.0),
    effets_directs={"justice": 1.1, "securite": 0.4, "confiance": 0.5, "democratie": 0.3},
    source="Conseil de l'Europe, CEPEJ ; loi de programmation de la justice 2023-2027.",
))
_lev(Levier(
    cle="lutte_criminalite_organisee",
    libelle="Lutte contre les trafics & criminalité organisée",
    famille="regalien",
    description="Moyens d'enquête contre les trafics de stupéfiants, d'armes et la "
                "cybercriminalité (dont rançongiciels).",
    unite="Md€", defaut=0.0, minimum=0.0, maximum=5.0, pas=0.25,
    ligne="criminalite", profil=(0.4, 0.7, 0.9, 1.0, 1.0),
    effets_directs={"securite": 0.9, "cohesion": 0.4, "budget": 0.3},
    source="OFDT / SSMSI — statistiques de la délinquance ; rapport Sénat sur les trafics.",
))
_lev(Levier(
    cle="cyber_resilience",
    libelle="Cyber-résilience (NIS 2, ANSSI, OIV)",
    famille="regalien",
    description="Mise en conformité des opérateurs d'importance vitale et des communes, "
                "protections anti-rançongiciels.",
    unite="Md€", defaut=0.0, minimum=0.0, maximum=6.0, pas=0.25,
    ligne="cyber", profil=(0.4, 0.7, 0.9, 1.0, 1.0),
    effets_directs={"resilience": 1.0, "numerique": 0.6, "securite": 0.5},
    source="ANSSI — panorama de la cybermenace ; directive NIS 2 (2022/2555).",
))


# ────────────────────────────────────────────────────────────────────────────
# 7. ÉNERGIE & CLIMAT
# ────────────────────────────────────────────────────────────────────────────

_lev(Levier(
    cle="nucleaire_reacteurs",
    libelle="Nouveaux réacteurs nucléaires (EPR2)",
    famille="energie_climat",
    description="Lancement de la construction en série (coût ≈ 3,5 Md€ par paire d'EPR2, "
                "étalé sur 10 ans). Effet climat et prix de l'électricité de long terme.",
    unite="nb", defaut=0.0, minimum=0.0, maximum=8.0, pas=1.0,
    ligne="nucleaire", facteur=1.8,
    profil=(0.15, 0.3, 0.5, 0.7, 0.9),
    effets_directs={"energie": 1.2, "climat": 0.9, "souverainete": 0.8, "industrie": 0.4},
    source="Programme EPR2 (6 réacteurs) ; Cour des comptes, coûts de la filière nucléaire.",
))
_lev(Levier(
    cle="renouvelables",
    libelle="Renouvelables (éolien, solaire, biogaz)",
    famille="energie_climat",
    description="Accélération des appels d'offres et de la planification (loi APER). "
                "1 Md€/an ≈ +1 point de part renouvelable.",
    unite="Md€", defaut=0.0, minimum=0.0, maximum=20.0, pas=0.5,
    ligne="renouvelables", profil=(0.6, 0.85, 1.0, 1.0, 1.0),
    effets_directs={"climat": 1.0, "energie": 0.7, "emploi": 0.5, "industrie": 0.3},
    source="RTE, « Futurs énergétiques 2050 » ; loi APER (2023).",
))
_lev(Levier(
    cle="renovation_thermique",
    libelle="Rénovation thermique des bâtiments",
    famille="energie_climat",
    description="MaPrimeRénov' et rénovation des bâtiments publics : effet JOBS, "
                "facture énergétique et climat. 1 Md€ ≈ 12 000 rénovations complètes.",
    unite="Md€", defaut=0.0, minimum=0.0, maximum=15.0, pas=0.5,
    ligne="renovation", profil=(0.5, 0.8, 1.0, 1.0, 1.0),
    effets_directs={"climat": 0.7, "energie": 0.6, "emploi": 0.6, "pauvrete": -0.2,
                    "logement": 0.5},
    source="ANAH ; 30 % des logements sont des « passoires thermiques » (DPE E-F-G).",
))
_lev(Levier(
    cle="adaptation_climat",
    libelle="Adaptation au changement climatique",
    famille="energie_climat",
    description="Sécheresse, inondations, littoral, forêts, eau : le plan d'adaptation "
                "national est financé à hauteur de ~0,2 % du PIB, le besoin est estimé à 1 %.",
    unite="Md€", defaut=0.0, minimum=0.0, maximum=15.0, pas=0.5,
    ligne="adaptation", profil=(0.4, 0.7, 0.9, 1.0, 1.0),
    effets_directs={"climat": 0.8, "resilience": 1.0, "territoires": 0.7, "agriculture": 0.6},
    source="PNACC-3 ; rapport de la Cour des comptes sur l'adaptation (2024).",
))
_lev(Levier(
    cle="transports_publics",
    libelle="Transports publics & mobilités (TER, RER, vélo)",
    famille="energie_climat",
    description="Investissement dans les réseaux du quotidien et les infrastructures "
                "cyclables ; effet pouvoir d'achat et climat.",
    unite="Md€", defaut=0.0, minimum=0.0, maximum=18.0, pas=0.5,
    ligne="transports", profil=(0.4, 0.65, 0.85, 1.0, 1.0),
    effets_directs={"climat": 0.7, "emploi": 0.5, "territoires": 0.8, "energie": 0.4,
                    "pouvoir_achat": 0.25},
    source="Conseil d'orientation des infrastructures (rapport Duron) ; loi LOM.",
))
_lev(Levier(
    cle="moratoire_artificialisation",
    libelle="Zéro artificialisation nette — mise en œuvre",
    famille="energie_climat",
    description="Application effective du ZAN : protège les sols agricoles et naturels, "
                "contraint la construction neuve en périphérie.",
    unite="bool", type=TYPE_INTERRUPTEUR, defaut=0.0,
    ligne="zan", facteur=1.5,
    profil=(0.5, 0.8, 1.0, 1.0, 1.0),
    effets_directs={"climat": 0.6, "agriculture": 0.7, "logement": -0.25, "territoires": 0.3},
    source="Loi Climat et Résilience (art. 191 à 195) ; rapport ZAN 2024.",
))


# ────────────────────────────────────────────────────────────────────────────
# 8. INDUSTRIE, NUMÉRIQUE, SOUVERAINETÉ
# ────────────────────────────────────────────────────────────────────────────

_lev(Levier(
    cle="plan_semiconducteurs",
    libelle="Plan semi-conducteurs (Chips Act France)",
    famille="industrie_souverainete",
    description="Soutien à la production de puces (Croix, Grenoble, Rousset) : "
                "réduit la vulnérabilité aux blocus de Taïwan.",
    unite="Md€", defaut=0.0, minimum=0.0, maximum=12.0, pas=0.5,
    champ="plan_souverainete_semiconducteurs_mde",
    profil=(0.3, 0.55, 0.8, 0.95, 1.0),
    effets_directs={"souverainete": 1.1, "industrie": 0.8, "resilience": 0.7, "emploi": 0.3},
    source="Chips Act européen (règlement 2023/1781) ; plan France 2030.",
))
_lev(Levier(
    cle="relocalisation_industrie",
    libelle="Relocalisations industrielles",
    famille="industrie_souverainete",
    description="Soutien aux relocalisations (santé, énergie, agroalimentaire, "
                "matériaux) : effet emploi industriel et balance commerciale.",
    unite="Md€", defaut=0.0, minimum=0.0, maximum=20.0, pas=0.5,
    ligne="relocalisation", profil=(0.3, 0.6, 0.8, 1.0, 1.0),
    effets_directs={"industrie": 1.0, "emploi": 0.6, "commerce_exterieur": 0.7,
                    "souverainete": 0.5},
    source="Rapports France Industrie ; indicateur de dépendance importations (INSEE).",
))
_lev(Levier(
    cle="souverainete_numerique_ia",
    libelle="Souveraineté numérique & IA",
    famille="industrie_souverainete",
    description="Cloud souverain, modèles d'IA ouverts, données de santé et calcul "
                "scientifique (effet direct sur l'innovation et la cyberdéfense).",
    unite="Md€", defaut=0.0, minimum=0.0, maximum=12.0, pas=0.5,
    ligne="numerique", profil=(0.5, 0.75, 0.9, 1.0, 1.0),
    effets_directs={"numerique": 1.2, "souverainete": 0.9, "innovation": 0.8, "emploi": 0.3},
    source="Commission de l'IA (rapport 2024) ; stratégie nationale IA.",
))
_lev(Levier(
    cle="service_public_numerique",
    libelle="Services publics numériques (FranceConnect, IA administrative)",
    famille="industrie_souverainete",
    description="Dématérialisation et simplification de bout en bout : gain de temps "
                "pour les usagers et économies de fonctionnement.",
    unite="Md€", defaut=0.0, minimum=0.0, maximum=6.0, pas=0.25,
    ligne="numerique", profil=(0.4, 0.7, 0.9, 1.0, 1.0),
    effets_directs={"numerique": 0.9, "confiance": 0.4, "budget": 0.4, "territoires": 0.3},
    source="DINUM — rapport annuel ; baromètre de la qualité des services publics numériques.",
))
_lev(Levier(
    cle="agriculture_souverainete",
    libelle="Souveraineté agricole & alimentaire",
    famille="industrie_souverainete",
    description="Plan de souveraineté agricole (élevage, fruits et légumes, protéines) "
                "et transition agroécologique.",
    unite="Md€", defaut=0.0, minimum=0.0, maximum=10.0, pas=0.5,
    ligne="agriculture", profil=(0.5, 0.75, 0.9, 1.0, 1.0),
    effets_directs={"agriculture": 1.1, "climat": 0.4, "souverainete": 0.4, "territoires": 0.5},
    source="Rapport Sénat sur la souveraineté alimentaire ; PAC 2023-2027.",
))


# ────────────────────────────────────────────────────────────────────────────
# 9. LOGEMENT, TERRITOIRES, COLLECTIVITÉS
# ────────────────────────────────────────────────────────────────────────────

_lev(Levier(
    cle="dgf_delta",
    libelle="Dotation globale de fonctionnement (DGF)",
    famille="logement_territoires",
    description="Hausse ou baisse de la DGF versée aux communes, départements et régions. "
                "Une baisse se répercute sur la taxe foncière (règle d'or CGCT).",
    unite="Md€", defaut=0.0, minimum=-15.0, maximum=15.0, pas=0.5,
    champ="delta_dotation_dgf_mde",
    profil=(1.0, 1.0, 1.0, 1.0, 1.0),
    effets_directs={"territoires": 0.9, "tension_sociale": -0.8, "services_publics": 0.7,
                    "pauvrete": -0.15},
    source="Comité des finances locales ; CGCT art. L. 1612-4 (règle d'or budgétaire).",
))
_lev(Levier(
    cle="logement_social",
    libelle="Construction de logements sociaux",
    famille="logement_territoires",
    description="Financement de la construction (en milliers de logements). "
                "1 000 logements ≈ 0,15 Md€/an de subventions + prêts HLM.",
    unite="milliers", defaut=0.0, minimum=0.0, maximum=120.0, pas=5.0,
    ligne="logement_social", facteur=0.15,
    profil=(0.4, 0.7, 0.9, 1.0, 1.0),
    effets_directs={"logement": 1.2, "pauvrete": -0.4, "emploi": 0.4, "territoires": 0.5,
                    "inégalités": -0.25},
    source="USH / Sénat — objectif SRU de 25 % de logements sociaux ; demande HLM ≈ 2 M.",
))
_lev(Levier(
    cle="encadrement_loyers",
    libelle="Encadrement des loyers",
    famille="logement_territoires",
    description="Généralisation de l'encadrement (loi ELAN) : effet sur le pouvoir "
                "d'achat des locataires et sur l'offre locative.",
    unite="bool", type=TYPE_INTERRUPTEUR, defaut=0.0,
    ligne="loyers", facteur=2.0,
    profil=(1.0, 1.0, 1.0, 1.0, 1.0),
    effets_directs={"logement": 0.7, "pouvoir_achat": 0.5, "pauvrete": -0.3,
                    "investissement": -0.3},
    source="Évaluations de l'encadrement parisien et lillois ; loi ELAN art. 140.",
))
_lev(Levier(
    cle="decentralisation",
    libelle="Nouvelle étape de décentralisation",
    famille="logement_territoires",
    description="Transfert de compétences et de fiscalité aux collectivités, "
                "différenciation territoriale, fin des doublons d'administration centrale.",
    unite="bool", type=TYPE_INTERRUPTEUR, defaut=0.0,
    ligne="decentralisation", facteur=2.0,
    profil=(0.3, 0.6, 0.85, 1.0, 1.0),
    effets_directs={"territoires": 1.0, "services_publics": 0.6, "confiance": 0.4,
                    "budget": 0.3},
    source="Rapports du Comité d'évaluation des réformes de la décentralisation ; loi 3DS.",
))
_lev(Levier(
    cle="fusion_doublons",
    libelle="Fusion des doublons territoriaux",
    famille="logement_territoires",
    description="Mutualisation des sièges région/département, agences et opérateurs : "
                "économies de structure sans fermer de guichet.",
    unite="Md€", defaut=0.0, minimum=0.0, maximum=10.0, pas=0.5,
    champ="fusion_doublons_territoriaux_mde",
    profil=(0.3, 0.6, 0.8, 1.0, 1.0),
    effets_directs={"budget": 1.0, "territoires": 0.7, "services_publics": 0.6},
    source="DOSSIER_DE_MANDATURE_GLOBAL.md (Volet 3) ; Cour des comptes, opérateurs de l'État.",
))


# ────────────────────────────────────────────────────────────────────────────
# 10. ÉTAT, FONCTION PUBLIQUE, SIMPLIFICATION
# ────────────────────────────────────────────────────────────────────────────

_lev(Levier(
    cle="point_indice",
    libelle="Valeur du point d'indice (fonction publique)",
    famille="etat_fonction_publique",
    description="Gel ou revalorisation du point : 1 % ≈ 2,4 Md€ de masse salariale. "
                "Sans revalorisation, le pouvoir d'achat des agents baisse avec l'inflation.",
    unite="%", defaut=0.0, minimum=-1.0, maximum=4.0, pas=0.25,
    ligne="point_indice", facteur=2.4, profil=(1.0, 1.0, 1.0, 1.0, 1.0),
    effets_directs={"services_publics": 0.7, "pouvoir_achat": 0.4, "tension_sociale": -0.4},
    source="DGAFP — rapport annuel sur l'état de la fonction publique (5,7 M d'agents).",
))
_lev(Levier(
    cle="effectifs_etat",
    libelle="Effectifs de l'État (variation nette)",
    famille="etat_fonction_publique",
    description="Créations ou suppressions nettes de postes (milliers) : "
                "1 000 ETP ≈ 45 M€/an. Les coupes non ciblées dégradent le service.",
    unite="milliers", defaut=0.0, minimum=-60.0, maximum=40.0, pas=1.0,
    ligne="effectifs_etat", facteur=0.045,
    profil=(0.3, 0.6, 0.8, 1.0, 1.0),
    effets_directs={"services_publics": 0.9, "emploi": -0.4, "budget": 0.7,
                    "tension_sociale": 0.5},
    source="PLF — plafonds d'emplois ; Cour des comptes, effectifs de l'État.",
))
_lev(Levier(
    cle="commande_publique",
    libelle="Commande publique massifiée",
    famille="etat_fonction_publique",
    description="Regroupement des achats de l'État et des collectivités, "
                "négociation des prix, clauses sociales et environnementales.",
    unite="Md€", defaut=0.0, minimum=0.0, maximum=8.0, pas=0.5,
    champ="commande_publique_massifiee_mde",
    profil=(0.2, 0.5, 0.7, 0.9, 1.0),
    effets_directs={"budget": 1.0, "climat": 0.3, "industrie": 0.3},
    source="DOSSIER_DE_MANDATURE_GLOBAL.md (Volet 3) ; OECP, achats publics ≈ 110 Md€.",
))
_lev(Levier(
    cle="simplification",
    libelle="Simplification administrative (choc de simplification)",
    famille="etat_fonction_publique",
    description="Suppression des normes redondantes, des commissions et des doublons "
                "de contrôle ; gain de temps pour les agents et les entreprises.",
    unite="Md€", defaut=0.0, minimum=0.0, maximum=8.0, pas=0.25,
    ligne="simplification", profil=(0.3, 0.6, 0.8, 1.0, 1.0),
    effets_directs={"budget": 0.8, "attractivite": 0.6, "confiance": 0.4, "territoires": 0.3},
    source="Rapports du Conseil d'État sur la simplification ; indicateurs de complexité (OCDE).",
))


# ────────────────────────────────────────────────────────────────────────────
# 11. INSTITUTIONS & DÉMOCRATIE
# ────────────────────────────────────────────────────────────────────────────

_lev(Levier(
    cle="reforme_casier_b2",
    libelle="Casier B2 vierge obligatoire pour les candidats",
    famille="institutions_democratie",
    description="Condition d'éligibilité : casier judiciaire vierge pour toute "
                "candidature à un mandat national ou local.",
    unite="bool", type=TYPE_INTERRUPTEUR, defaut=0.0,
    champ="reforme_casier_b2", effets_directs={"democratie": 0.8, "confiance": 0.5},
    source="Proposition du DOSSIER_DE_MANDATURE_GLOBAL.md ; code électoral.",
))
_lev(Levier(
    cle="reforme_vote_blanc",
    libelle="Vote blanc invalidant",
    famille="institutions_democratie",
    description="Le vote blanc compte dans les suffrages exprimés : en cas de majorité "
                "de blancs, l'élection est annulée avec délai de carence de 12 mois.",
    unite="bool", type=TYPE_INTERRUPTEUR, defaut=0.0,
    champ="reforme_vote_blanc_invalidant",
    effets_directs={"democratie": 0.9, "confiance": 0.6, "participation": 0.7},
    source="DOSSIER_DE_MANDATURE_GLOBAL.md ; propositions de loi sur la reconnaissance du vote blanc.",
))
_lev(Levier(
    cle="reforme_ric",
    libelle="Référendum d'initiative citoyenne (RIC)",
    famille="institutions_democratie",
    description="RIC constituant, législatif, abrogatoire et révocatoire dans des "
                "conditions de seuils encadrées : apaisement démocratique documenté.",
    unite="bool", type=TYPE_INTERRUPTEUR, defaut=0.0,
    champ="reforme_ric_souverain",
    effets_directs={"democratie": 1.4, "confiance": 0.9, "tension_sociale": -1.2},
    source="DOSSIER_DE_MANDATURE_GLOBAL.md ; analyse comparative Suisse / Italie.",
))
_lev(Levier(
    cle="reforme_regimes_speciaux",
    libelle="Fin des régimes de retraite spéciaux",
    famille="institutions_democratie",
    description="Alignement progressif des régimes dérogatoires sur le régime général "
                "(équité interprofessionnelle).",
    unite="bool", type=TYPE_INTERRUPTEUR, defaut=0.0,
    champ="reforme_fin_regimes_speciaux",
    effets_directs={"democratie": 0.6, "confiance": 0.6, "inégalités": -0.4, "budget": 0.3},
    source="Rapport Delevoye ; Cour des comptes — régimes spéciaux.",
))
_lev(Levier(
    cle="reforme_anti_pantouflage",
    libelle="Anti-pantouflage & transparence des lobbys",
    famille="institutions_democratie",
    description="Interdiction de pantouflage renforcée, registre public des représentants "
                "d'intérêts, transparence des rendez-vous ministériels.",
    unite="bool", type=TYPE_INTERRUPTEUR, defaut=0.0,
    champ="reforme_anti_pantouflage_lobbys",
    effets_directs={"democratie": 0.7, "confiance": 0.7, "inégalités": -0.3},
    source="HATVP — rapports annuels ; loi Sapin II.",
))
_lev(Levier(
    cle="reforme_non_cumul",
    libelle="Non-cumul des mandats étendu",
    famille="institutions_democratie",
    description="Extension du non-cumul et limitation à trois mandats successifs "
                "pour les fonctions exécutives locales et nationales.",
    unite="bool", type=TYPE_INTERRUPTEUR, defaut=0.0,
    champ="reforme_non_cumul_mandats",
    effets_directs={"democratie": 0.7, "confiance": 0.5, "territoires": 0.3},
    source="Loi organique 2014-125 ; rapports sur le renouvellement démocratique.",
))
_lev(Levier(
    cle="reforme_proportionnelle",
    libelle="Scrutin proportionnel à l'Assemblée",
    famille="institutions_democratie",
    description="Part de proportionnelle dans le mode de scrutin : "
                "représentation des minorités politiques contre stabilité majoritaire.",
    unite="%", defaut=0.0, minimum=0.0, maximum=100.0, pas=10.0,
    ligne="proportionnelle", facteur=0.01,
    profil=(1.0, 1.0, 1.0, 1.0, 1.0),
    effets_directs={"democratie": 1.0, "confiance": 0.4, "stabilite_gouvernementale": -0.6},
    source="Assemblée nationale — rapport sur le mode de scrutin ; comparaisons européennes.",
))
_lev(Levier(
    cle="convention_citoyenne",
    libelle="Convention citoyenne permanente",
    famille="institutions_democratie",
    description="Institutionnalisation d'une convention citoyenne tirée au sort "
                "sur les grandes réformes (climat, fin de vie, dette).",
    unite="bool", type=TYPE_INTERRUPTEUR, defaut=0.0,
    ligne="convention", facteur=0.5,
    effets_directs={"democratie": 1.1, "confiance": 0.7, "cohesion": 0.4},
    source="Convention citoyenne pour le climat (2019-2020) ; CESE.",
))
_lev(Levier(
    cle="usage_49_3",
    libelle="Recours à l'article 49.3",
    famille="institutions_democratie",
    description="Nombre d'utilisations par an : accélère l'adoption des lois mais "
                "nourrit la défiance et le risque de motion de censure.",
    unite="nb", defaut=0.0, minimum=0.0, maximum=10.0, pas=1.0,
    ligne="49_3",
    profil=(1.0, 1.0, 1.0, 1.0, 1.0),
    effets_directs={"democratie": -0.8, "confiance": -0.9, "tension_sociale": 0.9,
                    "stabilite_gouvernementale": 0.5},
    source="Constitution art. 49 al. 3 ; statistiques des censures (1962-2025).",
))
_lev(Levier(
    cle="lutte_contre_la_corruption",
    libelle="Moyens anticorruption & justice financière",
    famille="institutions_democratie",
    description="Renforcement du PNF, de l'AFA et des contrôles sur les marchés publics.",
    unite="Md€", defaut=0.0, minimum=0.0, maximum=3.0, pas=0.25,
    ligne="anticorruption", profil=(0.4, 0.7, 0.9, 1.0, 1.0),
    effets_directs={"confiance": 0.8, "democratie": 0.6, "budget": 0.4, "inégalités": -0.3},
    source="AFA — rapports annuels ; PNF — bilan d'activité.",
))


# ────────────────────────────────────────────────────────────────────────────
# 12. EUROPE, INTERNATIONAL, MIGRATION
# ────────────────────────────────────────────────────────────────────────────

_lev(Levier(
    cle="integration_europeenne",
    libelle="Intégration européenne (budget, dette commune, défense)",
    famille="international",
    description="Position française : de la simple coordination à la mutualisation "
                "des dettes communes et à la défense européenne intégrée.",
    unite="%", defaut=0.0, minimum=0.0, maximum=100.0, pas=10.0,
    ligne="europe", facteur=0.01,
    profil=(0.4, 0.7, 0.9, 1.0, 1.0),
    effets_directs={"europe": 1.1, "souverainete": -0.3, "croissance": 0.1, "defense": 0.4},
    source="Rapports sur la souveraineté européenne ; traité de Lisbonne art. 42-2.",
))
_lev(Levier(
    cle="cooperation_internationale",
    libelle="Aide publique au développement & climat",
    famille="international",
    description="Aide internationale (0,55 % du PIB aujourd'hui, cible ONU 0,7 %) "
                "et financement climat des pays vulnérables.",
    unite="Md€", defaut=0.0, minimum=-3.0, maximum=8.0, pas=0.25,
    ligne="apd", profil=(1.0, 1.0, 1.0, 1.0, 1.0),
    effets_directs={"international": 1.0, "climat": 0.4, "demographie": 0.3},
    source="OCDE-CAD — aide publique au développement française.",
))
_lev(Levier(
    cle="integration_accueil",
    libelle="Intégration des nouveaux arrivants (langue, emploi)",
    famille="international",
    description="Moyens d'apprentissage du français, de reconnaissance des diplômes et "
                "d'accès à l'emploi : accélère l'intégration économique.",
    unite="Md€", defaut=0.0, minimum=0.0, maximum=6.0, pas=0.25,
    ligne="integration", profil=(1.0, 1.0, 1.0, 1.0, 1.0),
    effets_directs={"cohesion": 0.8, "emploi": 0.5, "pauvrete": -0.3, "demographie": 0.3},
    source="Rapports de la Cour des comptes sur l'intégration ; OFII.",
))
_lev(Levier(
    cle="maitrise_flux_migratoires",
    libelle="Maîtrise des flux migratoires",
    famille="international",
    description="Contrôle des frontières, lutte contre les passeurs, accords de retour : "
                "effet sur les flux réguliers comme irréguliers.",
    unite="bool", type=TYPE_INTERRUPTEUR, defaut=0.0,
    ligne="migration", facteur=1.0,
    profil=(0.5, 0.8, 1.0, 1.0, 1.0),
    effets_directs={"demographie": -0.5, "cohesion": 0.3, "services_publics": 0.2,
                    "tension_sociale": -0.3},
    source="Rapports de l'OCDE sur les migrations internationales ; Office français de l'immigration.",
))


# ────────────────────────────────────────────────────────────────────────────
# 13. CHOCS MONDIAUX (exogènes)
# ────────────────────────────────────────────────────────────────────────────

_lev(Levier(
    cle="choc_petrole",
    libelle="Choc pétrolier (variation du Brent)",
    famille="exogene_monde",
    description="Variation exogène du baril de Brent par rapport au cours du jour "
                "(base issue de la donnée live).",
    unite="$/baril", defaut=0.0, minimum=-40.0, maximum=60.0, pas=1.0,
    champ="choc_petrole_brent_usd", profil=(1.0, 1.0, 1.0, 1.0, 1.0),
    effets_directs={"energie": -0.8, "inflation": 0.35, "pouvoir_achat": -0.6, "croissance": -0.3},
    source="Historique des chocs pétroliers (1973, 1979, 2008, 2022).",
))
_lev(Levier(
    cle="choc_taux_fed",
    libelle="Choc de taux (Fed / BCE)",
    famille="exogene_monde",
    description="Variation des taux directeurs mondiaux en points de base : "
                "se transmet aux taux longs, au change et au crédit.",
    unite="bps", defaut=0.0, minimum=-150.0, maximum=250.0, pas=5.0,
    champ="choc_taux_fed_bps", profil=(1.0, 1.0, 1.0, 1.0, 1.0),
    effets_directs={"marches": -1.0, "croissance": -0.4, "change": -0.1, "dette": -0.6},
    source="Cycles monétaires 2008-2025 ; transmission taux directeurs → taux 10 ans.",
))
_lev(Levier(
    cle="choc_change",
    libelle="Choc de change EUR/USD",
    famille="exogene_monde",
    description="Variation exogène de la parité euro-dollar (base = taux du jour).",
    unite="$ par €", defaut=0.0, minimum=-0.25, maximum=0.25, pas=0.01,
    champ="choc_change_eur_usd", profil=(1.0, 1.0, 1.0, 1.0, 1.0),
    effets_directs={"commerce_exterieur": 0.8, "inflation": -0.3, "industrie": -0.4},
    source="Effets de changes sur les importations ; élasticités du commerce extérieur.",
))
_lev(Levier(
    cle="commerce_mondial",
    libelle="Commerce mondial (fragmentation / accord)",
    famille="exogene_monde",
    description="Degré de fragmentation géoéconomique : de la coopération "
                "rétablie au découplage total (blocs fermés).",
    unite="%", defaut=0.0, minimum=-50.0, maximum=100.0, pas=10.0,
    ligne="commerce", facteur=0.06,
    profil=(0.5, 0.8, 1.0, 1.0, 1.0),
    effets_directs={"commerce_exterieur": -0.8, "croissance": -0.35, "inflation": 0.3,
                    "industrie": 0.2},
    source="FMI — « géo-économie fragmentation » ; scénarios OMC.",
))


# ────────────────────────────────────────────────────────────────────────────
# 14. GÉOPOLITIQUE (théâtres de tension et chokepoints)
# ────────────────────────────────────────────────────────────────────────────

_lev(Levier(
    cle="tension_taiwan",
    libelle="Tension autour de Taïwan",
    famille="exogene_monde",
    description="Vivacité du théâtre taïwanais (0-100). Taïwan concentre ~60 % de la "
                "production mondiale de semi-conducteurs avancés.",
    unite="0-100", type=TYPE_CIBLE, defaut=0.0, minimum=-30.0, maximum=60.0, pas=5.0,
    champ="delta_tension_taiwan", profil=(1.0, 1.0, 1.0, 1.0, 1.0),
    effets_directs={"geopolitique": 1.0, "souverainete": 0.4, "industrie": -0.5,
                    "marches": -0.3},
    source="Indices de tension (SIPRI, Atlantic Council) ; dépendance semi-conducteurs.",
))
_lev(Levier(
    cle="tension_ukraine",
    libelle="Guerre en Ukraine / relation OTAN-Russie",
    famille="exogene_monde",
    description="Intensité du conflit ukrainien et de l'affrontement avec la Russie.",
    unite="0-100", type=TYPE_CIBLE, defaut=0.0, minimum=-30.0, maximum=60.0, pas=5.0,
    champ="delta_tension_ukraine_otan", profil=(1.0, 1.0, 1.0, 1.0, 1.0),
    effets_directs={"geopolitique": 1.0, "defense": 0.8, "energie": -0.4, "inflation": 0.2},
    source="SIPRI ; rapports ONU ; dépenses militaires mondiales.",
))
_lev(Levier(
    cle="tension_hormuz",
    libelle="Tension au détroit d'Hormuz",
    famille="exogene_monde",
    description="Le détroit d'Hormuz fait passer ~20 % du pétrole mondial.",
    unite="0-100", type=TYPE_CIBLE, defaut=0.0, minimum=-30.0, maximum=60.0, pas=5.0,
    champ="delta_tension_iran_hormuz", profil=(1.0, 1.0, 1.0, 1.0, 1.0),
    effets_directs={"geopolitique": 1.0, "energie": -0.9, "inflation": 0.35},
    source="AIE — chokepoints pétroliers mondiaux.",
))
_lev(Levier(
    cle="blocus_taiwan",
    libelle="Intensité d'un blocus de Taïwan",
    famille="exogene_monde",
    description="Franchissement de seuil : coupure de la fourniture de composants "
                "(0 = aucune, 1 = blocus total).",
    unite="0-1", type=TYPE_INTERRUPTEUR, defaut=0.0, minimum=0.0, maximum=1.0, pas=0.25,
    champ="blocus_taiwan_intensite", profil=(1.0, 1.0, 1.0, 1.0, 1.0),
    effets_directs={"industrie": -1.5, "numerique": -1.2, "croissance": -0.8, "marches": -1.0},
    source="Scénarios de rupture Enedis/ANSSI ; analyse des chaînes de valeur (OCDE).",
))
_lev(Levier(
    cle="fermeture_hormuz",
    libelle="Fermeture du détroit d'Hormuz",
    famille="exogene_monde",
    description="Franchissement de seuil : coupure ou forte réduction du trafic "
                "(0 = aucune, 1 = fermeture totale).",
    unite="0-1", defaut=0.0, minimum=0.0, maximum=1.0, pas=0.25,
    champ="fermeture_hormuz_intensite", profil=(1.0, 1.0, 1.0, 1.0, 1.0),
    effets_directs={"energie": -1.6, "inflation": 0.8, "croissance": -0.7, "pauvrete": 0.3},
    source="AIE — scenarii de rupture d'approvisionnement pétrolier.",
))
_lev(Levier(
    cle="cyberattaque_systemique",
    libelle="Cyberattaque systémique majeure",
    famille="exogene_monde",
    description="Attaque coordonnée d'opérateurs d'importance vitale "
                "(hôpitaux, énergie, transports, collectivités).",
    unite="bool", type=TYPE_INTERRUPTEUR, defaut=0.0,
    champ="cyberattaque_systemique", profil=(1.0, 1.0, 1.0, 1.0, 1.0),
    effets_directs={"resilience": -1.2, "numerique": -1.0, "services_publics": -0.9,
                    "croissance": -0.4},
    source="ANSSI — panorama 2025 ; NIS 2.",
))
_lev(Levier(
    cle="escalade_nucleaire",
    libelle="Franchissement du seuil nucléaire tactique",
    famille="exogene_monde",
    description="Scénario extrême : usage d'arme nucléaire tactique, dégradation de "
                "notation, fermeture des marchés longs.",
    unite="bool", type=TYPE_INTERRUPTEUR, defaut=0.0,
    champ="usage_nucleaire_tactique", profil=(1.0, 1.0, 1.0, 1.0, 1.0),
    effets_directs={"geopolitique": 3.0, "marches": -3.0, "croissance": -1.5,
                    "cohesion": -1.0},
    source="SIPRI 2026 ; scénarios de dissuasion (revue Défense nationale).",
))
_lev(Levier(
    cle="mobilisation_guerre",
    libelle="Discours de mobilisation / économie de guerre",
    famille="exogene_monde",
    description="Passage à une logique d'économie de guerre : cadences industrielles, "
                "réquisitions, contrôle des chaînes critiques.",
    unite="bool", type=TYPE_INTERRUPTEUR, defaut=0.0,
    champ="mobilisation_economie_de_guerre", profil=(0.5, 0.8, 1.0, 1.0, 1.0),
    effets_directs={"defense": 0.8, "industrie": 0.5, "souverainete": 0.7, "croissance": -0.3},
    source="Revues de programmation militaire ; retour d'expérience 2022-2026.",
))
_lev(Levier(
    cle="clause_sauvegarde_defense",
    libelle="Clause de sauvegarde nationale (défense)",
    famille="exogene_monde",
    description="Activation de la dérogation « défense » du Pacte de stabilité : "
                "les dépenses militaires sortent du calcul du déficit PDE.",
    unite="bool", type=TYPE_INTERRUPTEUR, defaut=0.0,
    champ="activation_clause_sauvegarde_nationale_ue", profil=(1.0, 1.0, 1.0, 1.0, 1.0),
    effets_directs={"defense": 0.6, "europe": 0.5, "budget": 0.8},
    source="Pacte de stabilité réformé (2024) — clause de sauvegarde nationale.",
))


# ────────────────────────────────────────────────────────────────────────────
# API du catalogue
# ────────────────────────────────────────────────────────────────────────────

#: Scénarios-préréglages : des combinaisons de leviers prêtes à charger,
#: pour partir d'une doctrine cohérente plutôt que d'un curseur isolé.
PRESETS: dict[str, dict[str, Any]] = {
    "statut_quo": {
        "libelle": "Statu quo (inertie)",
        "description": "Aucun levier actionné : la trajectoire actuelle se prolonge.",
        "parametres": {},
        "couleur": "#f59e0b",
    },
    "mandature": {
        "libelle": "Plan de mandature républicaine",
        "description": "Dossier de mandature global : fraude, niches, DGF sanctuarisée, "
                       "réformes démocratiques, +60 Md€ de marges récurrentes en année 5.",
        "parametres": {
            "lutte_fraude_fiscale_ia": 10.0,
            "fraude_sociale": 2.5,
            "conditionnement_aides_entreprises": 12.0,
            "taxe_superprofits": 6.0,
            "extension_ttf": 5.0,
            "impot_minimum_pilier2": 6.0,
            "macf_carbone_frontiere": 4.0,
            "niches_fiscales": 40.0,
            "commande_publique": 5.0,
            "fusion_doublons": 6.5,
            "tva_energie_5_5": 1.0,
            "reforme_casier_b2": 1.0,
            "reforme_vote_blanc": 1.0,
            "reforme_ric": 1.0,
            "reforme_regimes_speciaux": 1.0,
            "reforme_anti_pantouflage": 1.0,
            "dgf_delta": 0.0,
        },
        "couleur": "#22c55e",
    },
    "resilience": {
        "libelle": "Résilience républicaine & réarmement",
        "description": "Mandature + effort de défense porté à 3,5 % du PIB et "
                       "souveraineté industrielle.",
        "parametres": {
            "lutte_fraude_fiscale_ia": 10.0,
            "conditionnement_aides_entreprises": 12.0,
            "taxe_superprofits": 6.0,
            "extension_ttf": 5.0,
            "niches_fiscales": 40.0,
            "commande_publique": 5.0,
            "fusion_doublons": 6.5,
            "effort_defense_pct_pib": 3.5,
            "plan_semiconducteurs": 8.0,
            "relocalisation_industrie": 12.0,
            "souverainete_numerique_ia": 8.0,
            "cyber_resilience": 4.0,
            "reforme_ric": 1.0,
            "reforme_non_cumul": 1.0,
            "clause_sauvegarde_defense": 1.0,
        },
        "couleur": "#38bdf8",
    },
    "austerite": {
        "libelle": "Austérité brute",
        "description": "Coupes dans les dotations et les dépenses publiques, "
                       "sans réforme structurelle : fronde fiscale attendue.",
        "parametres": {
            "dgf_delta": -12.0,
            "effectifs_etat": -40.0,
            "point_indice": 0.0,
            "ondam_variation": -1.0,
            "budget_education": -6.0,
            "hopital_public": -4.0,
            "budget_justice": -1.0,
            "revalorisation_retraites": -1.0,
        },
        "couleur": "#ef4444",
    },
    "transition_ecologique": {
        "libelle": "Transition écologique & énergie",
        "description": "Rénovation, renouvelables, nucléaire, transports, "
                       "fiscalité carbone compensée.",
        "parametres": {
            "renovation_thermique": 10.0,
            "renouvelables": 12.0,
            "transports_publics": 10.0,
            "adaptation_climat": 6.0,
            "nucleaire_reacteurs": 6.0,
            "taxe_carbone": 50.0,
            "cheque_energie": 3.0,
            "precarite_energetique": 2.0,
            "moratoire_artificialisation": 1.0,
            "tva_energie_5_5": 1.0,
        },
        "couleur": "#84cc16",
    },
    "justice_sociale": {
        "libelle": "Justice sociale & services publics",
        "description": "Redistribution, santé, école, logement, minima sociaux, "
                       "financés par la fiscalité du capital.",
        "parametres": {
            "isf_retablissement": 1.0,
            "ir_tranche_superieure": 8.0,
            "flat_tax_suppression": 1.0,
            "succession_reforme": 3.0,
            "lutte_fraude_fiscale_ia": 8.0,
            "budget_education": 12.0,
            "revalorisation_enseignants": 4.0,
            "hopital_public": 10.0,
            "deserts_medicaux": 4.0,
            "prevention_sante": 3.0,
            "revalorisation_minima_sociaux": 4.0,
            "logement_social": 60.0,
            "dependance_grand_age": 6.0,
            "budget_recherche": 8.0,
            "formation_professionnelle": 6.0,
            "smic_revalorisation": 2.0,
        },
        "couleur": "#a855f7",
    },
    "choc_mondial": {
        "libelle": "Stress-test : choc mondial",
        "description": "Stagflation importée : pétrole en forte hausse, taux mondiaux "
                       "tendus, commerce fragmenté.",
        "parametres": {
            "choc_petrole": 30.0,
            "choc_taux_fed": 75.0,
            "choc_change": -0.08,
            "commerce_mondial": 60.0,
            "tension_hormuz": 40.0,
        },
        "couleur": "#8b5cf6",
    },
    "crise_geopolitique": {
        "libelle": "Stress-test : crise géopolitique",
        "description": "Blocus de Taïwan et tensions majeures : semi-conducteurs, "
                       "marchés, réarmement d'urgence.",
        "parametres": {
            "tension_taiwan": 50.0,
            "tension_ukraine": 40.0,
            "blocus_taiwan": 1.0,
            "cyberattaque_systemique": 1.0,
            "effort_defense_pct_pib": 3.5,
            "mobilisation_guerre": 1.0,
            "clause_sauvegarde_defense": 1.0,
            "plan_semiconducteurs": 10.0,
        },
        "couleur": "#f97316",
    },
    "crise_taiwan": {
        "libelle": "Crise de Taïwan (blocus)",
        "description": "Blocus de Taïwan : semi-conducteurs coupés, marchés tendus, "
                       "souveraineté industrielle en urgence.",
        "parametres": {
            "tension_taiwan": 50.0,
            "blocus_taiwan": 1.0,
            "plan_semiconducteurs": 10.0,
            "souverainete_numerique_ia": 8.0,
            "cyber_resilience": 5.0,
            "effort_defense_pct_pib": 3.5,
            "mobilisation_guerre": 1.0,
            "clause_sauvegarde_defense": 1.0,
        },
        "couleur": "#fb923c",
    },
    "hormuz": {
        "libelle": "Fermeture du détroit d'Hormuz",
        "description": "20 % du pétrole mondial coupé : Brent au-delà de 150 $, "
                       "inflation importée, facture énergétique explosive.",
        "parametres": {
            "tension_hormuz": 50.0,
            "fermeture_hormuz": 1.0,
            "choc_petrole": 45.0,
            "cheque_energie": 4.0,
            "precarite_energetique": 3.0,
            "nucleaire_reacteurs": 4.0,
            "renouvelables": 10.0,
        },
        "couleur": "#dc2626",
    },
    "escalade_nucleaire": {
        "libelle": "Escalade nucléaire tactique",
        "description": "Franchissement du seuil nucléaire : dégradation souveraine, "
                       "fermeture des marchés longs, économie de guerre.",
        "parametres": {
            "escalade_nucleaire": 1.0,
            "tension_ukraine": 50.0,
            "effort_defense_pct_pib": 4.5,
            "mobilisation_guerre": 1.0,
            "clause_sauvegarde_defense": 1.0,
            "cyber_resilience": 6.0,
            "reserve_securite_nationale": 4.0,
        },
        "couleur": "#7f1d1d",
    },
    "convergence_ww3": {
        "libelle": "Convergence Chine-Russie-Iran",
        "description": "Guerre mondiale par blocs : commerce fragmenté, effort de "
                       "défense maximal, résilience totale à construire.",
        "parametres": {
            "tension_taiwan": 45.0,
            "tension_ukraine": 50.0,
            "tension_hormuz": 45.0,
            "commerce_mondial": 90.0,
            "effort_defense_pct_pib": 5.0,
            "mobilisation_guerre": 1.0,
            "clause_sauvegarde_defense": 1.0,
            "plan_semiconducteurs": 12.0,
            "relocalisation_industrie": 18.0,
            "agriculture_souverainete": 8.0,
        },
        "couleur": "#4c1d95",
    },
    "refondation_democratique": {
        "libelle": "Refondation démocratique",
        "description": "RIC, vote blanc, proportionnelle, conventions citoyennes, "
                       "transparence : la légitimité comme levier de tout le reste.",
        "parametres": {
            "reforme_casier_b2": 1.0,
            "reforme_vote_blanc": 1.0,
            "reforme_ric": 1.0,
            "reforme_regimes_speciaux": 1.0,
            "reforme_anti_pantouflage": 1.0,
            "reforme_non_cumul": 1.0,
            "reforme_proportionnelle": 50.0,
            "convention_citoyenne": 1.0,
            "lutte_contre_la_corruption": 2.0,
            "service_public_numerique": 3.0,
        },
        "couleur": "#eab308",
    },
}


def leviers_par_famille() -> dict[str, list[Levier]]:
    """Regroupe les leviers par famille, dans l'ordre d'affichage."""
    regroupement: dict[str, list[Levier]] = {cle: [] for cle in FAMILLES}
    for levier in LEVIERS.values():
        regroupement.setdefault(levier.famille, []).append(levier)
    return {cle: valeurs for cle, valeurs in regroupement.items() if valeurs}


def valeurs_par_defaut() -> dict[str, float]:
    """Vecteur de paramètres par défaut (pilotage neutre)."""
    return {cle: levier.defaut for cle, levier in LEVIERS.items()}


#: Booléens textuels tolérés à la frontière de l'API (`?params={"reforme_ric": "oui"}`).
_VRAI = frozenset({"oui", "true", "vrai", "1", "on", "yes", "x"})
_FAUX = frozenset({"non", "false", "faux", "0", "off", "no", ""})


def _en_nombre(brut: Any, cle: str, defaut: float) -> float:
    """Convertit une valeur reçue de l'interface en nombre exploitable.

    Tolère les booléens natifs et les booléens textuels (formulaires, URL), afin
    qu'un appel API écrit à la main ne casse pas la simulation.
    """
    if brut is None:
        return float(defaut)
    if isinstance(brut, bool):
        return 1.0 if brut else 0.0
    if isinstance(brut, str):
        texte = brut.strip().lower()
        if texte in _VRAI:
            return 1.0
        if texte in _FAUX:
            return 0.0
    try:
        return float(brut)
    except (TypeError, ValueError) as erreur:
        raise ValueError(f"valeur non numérique pour {cle} : {brut!r}") from erreur


def normaliser(parametres: dict[str, Any] | None) -> dict[str, float]:
    """Valide et borne un vecteur de paramètres reçu de l'interface ou d'un test.

    * clés inconnues → erreur explicite (aucune politique silencieuse) ;
    * valeurs hors bornes → écrêtées aux bornes ;
    * interrupteurs → 0/1 ;
    * champs absents ou `None` → valeur par défaut du levier.
    """
    resultat: dict[str, float] = {}
    inconnues = set(parametres or ()) - set(LEVIERS)
    if inconnues:
        raise ValueError(f"leviers inconnus : {', '.join(sorted(inconnues))}")
    for cle, levier in LEVIERS.items():
        brut = (parametres or {}).get(cle, levier.defaut)
        if levier.type in (TYPE_INTERRUPTEUR,):
            valeur = 1.0 if _en_nombre(brut, cle, levier.defaut) >= 0.5 else 0.0
        elif levier.type == TYPE_CHOIX:
            autorisees = [valeur for _, valeur in levier.modalites]
            valeur = _en_nombre(brut, cle, levier.defaut)
            if valeur not in autorisees:
                raise ValueError(
                    f"modalité invalide pour {cle} : {brut} (attendu : {autorisees})"
                )
        else:
            valeur = _en_nombre(brut, cle, levier.defaut)
        mini, maxi = levier.bornes
        resultat[cle] = min(maxi, max(mini, valeur))
    return resultat


def catalogue_public() -> dict[str, Any]:
    """Vue sérialisable complète : familles, leviers, préréglages."""
    return {
        "familles": [
            {"cle": cle, **meta, "leviers": [lev.en_dict() for lev in leviers_par_famille().get(cle, [])]}
            for cle, meta in FAMILLES.items()
        ],
        "presets": PRESETS,
        "defauts": valeurs_par_defaut(),
    }


def resume_effets_lever(cle: str) -> str:
    """Résumé lisible des rattachements d'un levier (pour la documentation)."""
    levier = LEVIERS[cle]
    morceaux: list[str] = []
    if levier.champ:
        morceaux.append(f"moteur : {levier.champ} (×{levier.facteur:g})")
    if levier.ligne:
        morceaux.append(f"ligne budgétaire : {levier.ligne} (×{levier.facteur:g})")
    if levier.effets_directs:
        morceaux.append(
            "effets directs : " + ", ".join(f"{d} {v:+g}" for d, v in levier.effets_directs.items())
        )
    return " ; ".join(morceaux) if morceaux else "aucun effet déclaré"


def iter_levers(familles: Iterable[str] | None = None) -> Iterable[Levier]:
    """Itère sur les leviers (filtre optionnel par famille)."""
    selection = set(familles) if familles else None
    for levier in LEVIERS.values():
        if selection is None or levier.famille in selection:
            yield levier
