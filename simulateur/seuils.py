"""
simulateur/seuils.py — garde-fous : seuils tolérables, risqués et hors-sol.

Le simulateur sait calculer l'effet d'une mesure ; il ne disait pas encore si
cet effet est **acceptable**. Ce module comble ce vide : chaque grandeur
surveillée est reliée à des bornes documentées — tolérable, vigilance, risqué,
hors-sol — et à un message qui explique ce qui se passe si on les franchit.

Trois idées :

1. **Plusieurs strates.** Un même paquet de mesures n'a pas le même effet à
   l'échelle locale, nationale, européenne, mondiale ou géopolitique : chaque
   garde-fou est rattaché à une strate, et le diagnostic est rendu strate par
   strate.

2. **Deux lectures, jamais confondues.** Les garde-fous « absolus » comparent la
   situation projetée aux seuils institutionnels (3 % de déficit, 90 jours de
   stocks pétroliers de l'AIE, 3,5 % de PIB de défense…) ; les garde-fous
   « écart » mesurent ce que **vos** mesures ajoutent ou retirent par rapport à
   la trajectoire de référence. Une politique peut être bonne en écart et
   insuffisante en absolu : les deux messages cohabitent.

3. **Le hors-sol n'est pas une opinion.** Chaque borne haute porte un message
   concret : ce qui casse, et ce qu'il faudrait faire pour revenir en deçà.
   `evaluer_sortie()` renvoie aussi les **marges** (ce qu'il reste avant le
   prochain seuil) et les **progrès possibles** (ce qu'on peut encore oser),
   pour régler finement sans mettre la population en danger.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any

# ────────────────────────────────────────────────────────────────────────────
# Niveaux
# ────────────────────────────────────────────────────────────────────────────

NIVEAUX: tuple[str, ...] = ("favorable", "tolerable", "vigilance", "risque", "hors_sol")

LIBELLES_NIVEAUX: dict[str, str] = {
    "favorable": "favorable",
    "tolerable": "tolérable",
    "vigilance": "vigilance",
    "risque": "risqué",
    "hors_sol": "hors-sol",
    "inconnu": "non mesuré",
}

#: Seuil à partir duquel on considère que la population est exposée.
NIVEAU_ALERTE = "vigilance"

LIBELLES_STRATES: dict[int, str] = {
    1: "Échelon local",
    2: "Échelon national",
    3: "Échelon européen",
    4: "Échelon mondial",
    5: "Échelon géopolitique",
}

#: Notes souveraines → rang (1 = meilleure). Toute note absente retombe sur 12.
RANG_NOTES: dict[str, int] = {
    "AAA": 1, "AA+": 2, "AA": 3, "AA-": 4, "A+": 5, "A": 6, "A-": 7,
    "BBB+": 8, "BBB": 9, "BBB-": 10, "BB+": 11, "BB": 12, "BB-": 13,
    "B+": 14, "B": 15, "B-": 16, "CCC": 17, "CC": 18, "C": 19, "D": 20,
}

#: Domaines qui composent le risque population (strate 1 et 2).
DOMAINES_POPULATION: tuple[str, ...] = (
    "pouvoir_achat", "pauvrete", "sante", "education", "emploi",
    "logement", "social", "securite",
)


# ────────────────────────────────────────────────────────────────────────────
# Structures
# ────────────────────────────────────────────────────────────────────────────

@dataclass(frozen=True)
class Borne:
    """Seuil franchi à partir duquel le niveau indiqué s'applique.

    `message` est formaté avec `valeur`, `seuil`, `marge` et `unite`, ce qui
    permet d'écrire « le déficit atteint {valeur} % du PIB, au-delà du seuil de
    rupture ({seuil} %) : il manque {marge} point pour revenir en deçà ».
    """

    seuil: float
    niveau: str
    message: str


@dataclass(frozen=True)
class GardeFou:
    """Grandeur surveillée, ses bornes et sa strate."""

    cle: str
    libelle: str
    strate: int
    sens: str  # "max" (au-dessus = pire), "min" (en-dessous = pire), "note", "booleen"
    bornes: tuple[Borne, ...]
    unite: str = ""
    precision: int = 1
    source: str = ""
    ou: str = "etape"  # "etape" = dernier exercice, "synthese" = synthèse
    famille: str = "general"
    cible: tuple[float, str] | None = None  # seuil souhaitable non encore atteint


def _g(*, cle: str, libelle: str, strate: int, sens: str, bornes: list[tuple[float, str, str]],
       unite: str = "", precision: int = 1, source: str = "", ou: str = "etape",
       famille: str = "general", cible: tuple[float, str] | None = None) -> GardeFou:
    return GardeFou(
        cle=cle, libelle=libelle, strate=strate, sens=sens,
        bornes=tuple(Borne(seuil, niveau, message) for seuil, niveau, message in bornes),
        unite=unite, precision=precision, source=source, ou=ou, famille=famille, cible=cible,
    )


# ────────────────────────────────────────────────────────────────────────────
# Garde-fous absolus : la situation projetée face aux seuils institutionnels
# ────────────────────────────────────────────────────────────────────────────

GARDE_FOUS: tuple[GardeFou, ...] = (
    # ── Strate 2 : budget, dette, marchés ──────────────────────────────────
    _g(cle="deficit_final_pct", libelle="Déficit public (% du PIB)", strate=2, sens="max",
       unite="% du PIB", famille="budget", ou="synthese",
       source="Traité de Maastricht (3 %), Pacte de stabilité, valeur de rupture 5,5 %",
       bornes=[
           (3.0, "tolerable",
            "Déficit à {valeur} % du PIB : sous la barre des 3 %, la dette se stabilise "
            "d'elle-même et la marge budgétaire se reconstitue."),
           (4.5, "vigilance",
            "Déficit à {valeur} % du PIB (seuil de vigilance 3 %). Chaque point de déficit en "
            "plus, c'est {marge} point avant la zone de rupture : privilégiez les mesures gagées."),
           (5.5, "risque",
            "Déficit à {valeur} % du PIB : au-delà de 5 %, la charge d'intérêts devient un poste "
            "budgétaire supérieur à l'Éducation nationale, financé par la dette et non par des recettes."),
           (float("inf"), "hors_sol",
            "Déficit à {valeur} % du PIB : hors-sol. À ce niveau, ni les marchés ni Bruxelles ne "
            "laissent passer : la correction se fera par la dépense publique — donc sur la population. "
            "Il faut retrouver {marge} point de déficit en moins."),
       ]),
    _g(cle="dette_finale_pct", libelle="Dette publique (% du PIB)", strate=2, sens="max",
       unite="% du PIB", famille="budget", ou="synthese",
       source="Critère de Maastricht 60 %, vigilance FMI 90 %, zone critique observée 125 %, "
              "restructurations au-delà de 145 %",
       bornes=[
           (90.0, "tolerable",
            "Dette à {valeur} % du PIB : sous 90 %, l'effet boule de neige reste maîtrisé."),
           (125.0, "vigilance",
            "Dette à {valeur} % du PIB : au-delà de 90 %, chaque point de taux coûte cher ; la "
            "trajectoire reste tenable mais tout dérapage du déficit se paie comptant."),
           (145.0, "risque",
            "Dette à {valeur} % du PIB : au niveau des pays qui ont dû restructurer (Grèce 2011). "
            "La prime de risque devient auto-réalisatrice : elle renchérit la dette qui la justifie."),
           (float("inf"), "hors_sol",
            "Dette à {valeur} % du PIB : hors-sol. La soutenabilité n'est plus une affaire de "
            "décision budgétaire mais de refinancement forcé. Il faut {marge} point de PIB en moins."),
       ]),
    _g(cle="charge_dette_pib", libelle="Charge de la dette (% du PIB)", strate=2, sens="max",
       unite="% du PIB", precision=2, famille="budget", ou="synthese",
       source="Loi de finances ; 4 % du PIB = premier budget de l'État",
       bornes=[
           (2.0, "tolerable",
            "Charge de la dette à {valeur} % du PIB : le premier poste budgétaire reste sous contrôle."),
           (3.0, "vigilance",
            "Charge de la dette à {valeur} % du PIB : l'intérêt passe devant la plupart des missions "
            "régaliennes. Chaque point de marge est pris sur les services publics."),
           (4.0, "risque",
            "Charge de la dette à {valeur} % du PIB : le remboursement des créanciers devient le "
            "premier budget de l'État, devant l'École et la Santé réunies."),
           (float("inf"), "hors_sol",
            "Charge de la dette à {valeur} % du PIB : hors-sol. L'État emprunte pour payer ses "
            "intérêts — spirale de Ponzi budgétaire. Toute mesure nouvelle doit être gagée à l'euro."),
       ]),
    _g(cle="taux_oat_final", libelle="Taux OAT 10 ans (%)", strate=4, sens="max",
       unite="%", precision=2, famille="marches", ou="synthese",
       source="BCE (taux souverains), moyenne 2010-2025 ≈ 2 %",
       bornes=[
           (3.5, "tolerable",
            "OAT à {valeur} % : le financement de l'État reste bon marché."),
           (4.5, "vigilance",
            "OAT à {valeur} % : la charge future augmente mécaniquement (≈ 11,5 Md€ par point). "
            "Il reste {marge} point avant la zone de rigueur."),
           (5.5, "risque",
            "OAT à {valeur} % : les investisseurs exigent une prime de défiance ; le crédit aux "
            "PME et aux ménages se renchérit dans la foulée (OAT + 0,85 pt)."),
           (float("inf"), "hors_sol",
            "OAT à {valeur} % : hors-sol. À ce niveau, le refinancement devient une variable "
            "politique étrangère. Il faut {marge} point de taux en moins pour revenir sous 5,5 %."),
       ]),
    _g(cle="spread_final_bps", libelle="Spread face au Bund (bps)", strate=3, sens="max",
       unite="bps", precision=0, famille="marches", ou="synthese",
       source="Écart France-Allemagne ; crise de la zone euro 2011-2012 ≈ 190 bps",
       bornes=[
           (80.0, "tolerable",
            "Spread à {valeur} bps : la France se finance presque au prix de l'Allemagne."),
           (150.0, "vigilance",
            "Spread à {valeur} bps : la prime de risque commence à coûter plus cher que le gain "
            "espéré des mesures non gagées."),
           (250.0, "risque",
            "Spread à {valeur} bps : niveau atteint par les pays sous programme. Le bouclier TPI "
            "de la BCE devient l'unique recours."),
           (float("inf"), "hors_sol",
            "Spread à {valeur} bps : hors-sol — prime de décrochage. La politique budgétaire "
            "nationale passe sous tutelle de fait."),
       ]),
    _g(cle="note_souveraine", libelle="Note souveraine", strate=4, sens="note",
       famille="marches", ou="synthese",
       source="Échelle des agences ; seuil de perte d'éligibilité des investisseurs prudents : A-",
       bornes=[
           (5.0, "tolerable", "Note {valeur} : la signature française reste solide."),
           (7.0, "vigilance",
            "Note {valeur} : la France sort du club des signatures de première qualité, "
            "les investisseurs prudents (fonds de pension, banques centrales) décrochent."),
           (10.0, "risque",
            "Note {valeur} : catégorie « speculative » proche ; les marchés exigent un coupon "
            "de rupture et le crédit intérieur se durcit."),
           (float("inf"), "hors_sol",
            "Note {valeur} : hors-sol. La signature française n'est plus un placement, la dette "
            "devient un problème de stabilité financière internationale."),
       ]),
    _g(cle="taux_credit_pme", libelle="Crédit aux PME (%)", strate=2, sens="max",
       unite="%", precision=2, famille="marches",
       source="OAT + 0,85 pt (marge bancaire observée)",
       bornes=[
           (4.5, "tolerable", "Crédit PME à {valeur} % : l'investissement des petites entreprises n'est pas étouffé."),
           (5.5, "vigilance", "Crédit PME à {valeur} % : l'investissement faiblit, l'emploi s'en ressent 6 à 12 mois plus tard."),
           (7.0, "risque", "Crédit PME à {valeur} % : les entreprises fragiles coupent dans l'embauche et l'outil de production."),
           (float("inf"), "hors_sol",
            "Crédit PME à {valeur} % : hors-sol — rationnement du crédit, vagues de faillites, "
            "chômage en hausse de plusieurs points de PIB potentiel."),
       ]),
    _g(cle="inflation_globale_pct", libelle="Inflation (%)", strate=2, sens="max",
       unite="%", precision=2, famille="population",
       source="Cible BCE 2 % ; IPCH Eurostat",
       bornes=[
           (2.5, "tolerable", "Inflation à {valeur} % : les prix sont contenus, le pouvoir d'achat ne s'érode pas."),
           (3.5, "vigilance", "Inflation à {valeur} % : les salaires courent après les prix, l'écart se creuse pour les revenus fixes."),
           (5.0, "risque", "Inflation à {valeur} % : boucle prix-salaires, la BCE durcit et l'activité cale."),
           (float("inf"), "hors_sol",
            "Inflation à {valeur} % : hors-sol. Épargne réelle détruite, indexation générale des "
            "salaires, perte de confiance dans la monnaie."),
       ]),
    _g(cle="inflation_globale_pct", libelle="Inflation trop faible (%)", strate=2, sens="min",
       unite="%", precision=2, famille="population", cible=(2.0, "La cible de la BCE est de 2 %."),
       source="Cible BCE 2 %",
       bornes=[
           (1.0, "tolerable", "Inflation à {valeur} % : pas de menace déflationniste immédiate."),
           (0.5, "vigilance", "Inflation à {valeur} % : trop faible pour faire baisser la dette en valeur réelle, assez basse pour que les ménages reportent leurs achats."),
           (0.0, "risque", "Inflation à {valeur} % : déflation installée, salaires et rentrées fiscales suivent vers le bas, la dette explose en ratio."),
           (float("-inf"), "hors_sol",
            "Inflation à {valeur} % : hors-sol — la monnaie s'envole en valeur réelle, les revenus "
            "du travail et les recettes publiques s'effondrent."),
       ]),

    # ── Strate 1 et 2 : la population ──────────────────────────────────────
    _g(cle="pouvoir_achat_index", libelle="Pouvoir d'achat (base 100)", strate=1, sens="min",
       unite="indice", precision=1, famille="population",
       source="INSEE (revenu réel des ménages, ancrage) ; bornes de stress propres au simulateur, non officielles",
       cible=(102.0, "Objectif d'une mandature : +2 % de pouvoir d'achat."),
       bornes=[
           (99.0, "tolerable", "Pouvoir d'achat à {valeur} : les ménages ne perdent pas de terrain."),
           (97.5, "vigilance",
            "Pouvoir d'achat à {valeur} : la perte devient perceptible — c'est le premier motif de "
            "colère sociale, bien avant les agrégats budgétaires."),
           (95.5, "risque",
            "Pouvoir d'achat à {valeur} : recul supérieur à 4,5 %, les ménages modestes arbitrent "
            "entre l'alimentaire, le chauffage et le logement."),
           (85.0, "risque",
            "Pouvoir d'achat à {valeur} : recul supérieur à 15 %, appauvrissement très sévère "
            "simulé; il manque {marge} point pour revenir dans la zone de risque élevé."),
           (float("-inf"), "hors_sol",
            "Pouvoir d'achat à {valeur} : hors-sol — recul supérieur à 15 %, paupérisation "
            "mesurable; il manque {marge} point pour revenir sous le seuil de rupture."),
       ]),
    _g(cle="tension_finale", libelle="Tension sociale locale (/100)", strate=1, sens="max",
       unite="/100", precision=1, famille="population", ou="synthese",
       source="Indice du modèle (manifestations, blocages, incidents) ; 70 = niveau de crise",
       bornes=[
           (45.0, "tolerable", "Tension locale à {valeur}/100 : le pays encaisse les réformes."),
           (60.0, "vigilance",
            "Tension locale à {valeur}/100 : blocages sectoriels, exécution des politiques publiques "
            "dégradée. Il reste {marge} point avant le seuil de crise."),
           (75.0, "risque",
            "Tension locale à {valeur}/100 : confrontations et paralysie ; les mesures finissent "
            "retirées, donc votées pour rien."),
           (float("inf"), "hors_sol",
            "Tension locale à {valeur}/100 : hors-sol — crise sociale ouverte, l'ordre public "
            "devient la priorité et la population paie deux fois."),
       ]),
    _g(cle="confiance_democratique", libelle="Confiance démocratique (/100)", strate=1, sens="min",
       unite="/100", precision=1, famille="democratie",
       source="Baromètres CEVIPOF ; le socle observe vit autour de 25-30",
       cible=(45.0, "Une confiance durablement au-dessus de 45 rend les réformes suivantes possibles."),
       bornes=[
           (30.0, "tolerable", "Confiance à {valeur}/100 : socle fragile mais stable."),
           (22.0, "vigilance",
            "Confiance à {valeur}/100 : la défiance s'installe ; même les mesures justes sont lues "
            "comme des coups de force."),
           (15.0, "risque",
            "Confiance à {valeur}/100 : le consentement fiscal se rompt, la contestation devient "
            "structurelle."),
           (float("-inf"), "hors_sol",
            "Confiance à {valeur}/100 : hors-sol — plus aucun arbitrage n'est perçu comme légitime."),
       ]),
    _g(cle="risque_censure_final_pct", libelle="Risque de censure (%)", strate=2, sens="max",
       unite="%", precision=0, famille="democratie", ou="synthese",
       source="Arithmétique parlementaire (majorité 210 sièges)",
       bornes=[
           (30.0, "tolerable", "Risque de censure à {valeur} % : le gouvernement tient sa majorité."),
           (55.0, "vigilance",
            "Risque de censure à {valeur} % : il suffit d'un groupe qui bascule pour que tout "
            "s'arrête ; les réformes perdent leur crédibilité temporelle."),
           (70.0, "risque",
            "Risque de censure à {valeur} % : résultat probablement fatal à la mandature — donc aux "
            "mesures déjà votées."),
           (float("inf"), "hors_sol",
            "Risque de censure à {valeur} % : hors-sol. Le texte ne survivra pas au vote ; "
            "inutile d'aller plus loin sans majorité."),
       ]),
    _g(cle="qualite_services_proximite", libelle="Services de proximité (/100)", strate=1, sens="min",
       unite="/100", precision=1, famille="population",
       source="Indice du modèle (écoles, santé de proximité, guichets, transports)",
       bornes=[
           (55.0, "tolerable", "Services de proximité à {valeur}/100 : la vie quotidienne tient."),
           (45.0, "vigilance",
            "Services de proximité à {valeur}/100 : fermetures, délais, déserts qui s'élargissent."),
           (35.0, "risque",
            "Services de proximité à {valeur}/100 : territoires décrochés, coût caché reporté sur "
            "les ménages (déplacements, santé privée)."),
           (float("-inf"), "hors_sol",
            "Services de proximité à {valeur}/100 : hors-sol — l'État n'assure plus le service "
            "public de base là où vivent les gens."),
       ]),

    # ── Strate 3 : Europe ──────────────────────────────────────────────────
    _g(cle="statut_pde", libelle="Procédure pour déficit excessif", strate=3, sens="booleen",
       famille="europe", ou="synthese",
       source="Article 126 TFUE ; recommandations du Conseil",
       bornes=[
           (1.0, "risque",
            "Une procédure pour déficit excessif est ouverte : la France est sous surveillance "
            "européenne renforcée, avec trajectoire de correction imposée (2 à 4 ans)."),
           (0.0, "tolerable", "Pas de procédure pour déficit excessif ouverte à l'encontre de la France."),
       ]),
    _g(cle="bouclier_tpi", libelle="Bouclier anti-fragmentation de la BCE", strate=3, sens="booleen",
       famille="europe", ou="synthese",
       source="TPI de la BCE (juillet 2022)",
       bornes=[
           (0.0, "vigilance",
            "Le bouclier anti-fragmentation de la BCE est suspendu : en cas de tension, le pays "
            "français se défend seul face aux marchés."),
           (1.0, "tolerable", "Le bouclier de la BCE est disponible : les hausses de taux restent absorbables."),
       ]),

    # ── Strate 4 : énergie, industrie, monnaie ────────────────────────────
    _g(cle="cours_petrole_usd", libelle="Prix du Brent ($/baril)", strate=4, sens="max",
       unite="$/baril", precision=0, famille="energie",
       source="AIE ; au-delà de 110 $, l'effet sur l'inflation importée est mesuré à −3,5 pt de pouvoir d'achat",
       bornes=[
           (95.0, "tolerable", "Brent à {valeur} $ : facture énergétique supportable."),
           (115.0, "vigilance",
            "Brent à {valeur} $ : l'inflation importée ronge le pouvoir d'achat, "
            "il reste {marge} $ avant la zone de crise."),
           (135.0, "risque",
            "Brent à {valeur} $ : récession importée, déficit commercial et budget des ménages "
            "dégradés simultanément."),
           (float("inf"), "hors_sol",
            "Brent à {valeur} $ : hors-sol — choc de récession mondiale, la fiscalité carbone et "
            "les hausses d'accises deviennent politiquement intenables."),
       ]),
    _g(cle="disponibilite_semiconducteurs_pct", libelle="Disponibilité des semi-conducteurs (%)",
       strate=4, sens="min", unite="%", precision=0, famille="industrie",
       source="Indice du modèle (approvisionnement industriel)",
       bornes=[
           (95.0, "tolerable", "Semi-conducteurs à {valeur} % : l'industrie tourne sans bridage."),
           (85.0, "vigilance", "Semi-conducteurs à {valeur} % : allongement des délais, arbitrages de production."),
           (70.0, "risque", "Semi-conducteurs à {valeur} % : arrêts de chaînes (automobile, électronique, défense)."),
           (float("-inf"), "hors_sol",
            "Semi-conducteurs à {valeur} % : hors-sol — l'appareil productif et la défense sont "
            "à l'arrêt, avec pertes d'emplois en cascade."),
       ]),
    _g(cle="stocks_strategiques_petrole_jours", libelle="Stocks pétroliers stratégiques (jours)",
       strate=5, sens="min", unite="jours", precision=0, famille="energie",
       source="Obligation AIE : 90 jours de consommation nette",
       cible=(90.0, "Le niveau de conformité AIE est de 90 jours."),
       bornes=[
           (90.0, "tolerable", "Stocks à {valeur} jours : conformité AIE, l'État tient un blocus de quelques semaines."),
           (75.0, "vigilance", "Stocks à {valeur} jours : sous la norme AIE, la marge de manœuvre en cas de crise se réduit."),
           (60.0, "risque", "Stocks à {valeur} jours : plus d'un mois et demi d'autonomie — les prix intérieurs deviennent spéculatifs."),
           (float("-inf"), "hors_sol",
            "Stocks à {valeur} jours : hors-sol — plus de quoi alimenter le pays, "
            "le rationnement devient la seule politique énergétique possible."),
       ]),

    # ── Strate 5 : géopolitique ───────────────────────────────────────────
    _g(cle="indice_tension_geopolitique", libelle="Tension géopolitique (/100)", strate=5, sens="max",
       unite="/100", precision=1, famille="geopolitique",
       source="Indice du modèle (chokepoints, conflits, escalade)",
       bornes=[
           (50.0, "tolerable", "Tension géopolitique à {valeur}/100 : environnement de crise ordinaire."),
           (68.0, "vigilance", "Tension à {valeur}/100 : les chaînes d'approvisionnement et les marchés de l'énergie commencent à réagir."),
           (80.0, "risque", "Tension à {valeur}/100 : les scénarios de rupture deviennent des hypothèses de travail."),
           (float("inf"), "hors_sol",
            "Tension à {valeur}/100 : hors-sol — la politique intérieure est dictée par l'extérieur."),
       ]),
    _g(cle="chokepoints_sous_tension", libelle="Chokepoints sous tension (/7)", strate=5, sens="max",
       unite="/7", precision=0, famille="geopolitique",
       source="7 points de passage stratégiques suivis (Hormuz, Bab el-Mandeb, Malacca, Suez, Bosphore, Panama, Taïwan)",
       bornes=[
           (1.0, "tolerable", "{valeur} chokepoint sous tension : trafic mondial normal."),
           (3.0, "vigilance", "{valeur} chokepoints perturbés : les délais et les primes de fret augmentent."),
           (4.0, "risque", "{valeur} chokepoints sous tension : le commerce mondial se réorganise en contournements coûteux."),
           (float("inf"), "hors_sol",
            "{valeur} chokepoints bloqués : hors-sol — l'économie mondiale fonctionne au ralenti, "
            "avec effet immédiat sur les prix et l'emploi."),
       ]),
    _g(cle="probabilite_escalade_mondiale_pct", libelle="Probabilité d'escalade mondiale (%)",
       strate=5, sens="max", unite="%", precision=0, famille="geopolitique",
       source="Modèle d'escalade documenté dans docs/08_STRATE_GEOPOLITIQUE",
       bornes=[
           (10.0, "tolerable", "Escalade mondiale estimée à {valeur} % : risque de queue maîtrisé."),
           (25.0, "vigilance", "Escalade estimée à {valeur} % : le risque devient un paramètre d'arbitrage des investisseurs."),
           (45.0, "risque", "Escalade estimée à {valeur} % : les plans de continuité deviennent le cœur de la politique publique."),
           (float("inf"), "hors_sol",
            "Escalade estimée à {valeur} % : hors-sol — la projection budgétaire perd son sens, "
            "les décisions se prennent en mode crise."),
       ]),
    _g(cle="risque_nucleaire_tactique_pct", libelle="Risque nucléaire tactique (%)", strate=5,
       sens="max", unite="%", precision=0, famille="geopolitique",
       source="Modèle d'escalade ; seuils issus de la doctrine publiée",
       bornes=[
           (8.0, "tolerable", "Risque nucléaire tactique estimé à {valeur} %."),
           (20.0, "vigilance", "Risque nucléaire tactique à {valeur} % : dissuasion affaiblie, négociations sous chantage."),
           (35.0, "risque", "Risque nucléaire tactique à {valeur} % : seuil de rupture du tabou, l'Europe entière bascule."),
           (float("inf"), "hors_sol",
            "Risque nucléaire tactique à {valeur} % : hors-sol — plus aucune hypothèse économique "
            "n'est valable, seule la survie compte."),
       ]),
    _g(cle="effort_defense_pct_pib", libelle="Effort de défense (% du PIB)", strate=5, sens="min",
       unite="% du PIB", precision=2, famille="defense",
       source="Engagement OTAN (2 %), sommet de La Haye (5 % à horizon 2035), cible de travail 3,5 %",
       cible=(3.5, "Objectif de résilience : 3,5 % du PIB."),
       bornes=[
           (2.5, "tolerable", "Défense à {valeur} % du PIB : au-dessus de l'engagement OTAN, dissuasion crédible."),
           (2.0, "vigilance", "Défense à {valeur} % du PIB : tout juste au niveau OTAN, insuffisant face à une guerre d'usure."),
           (1.5, "risque", "Défense à {valeur} % du PIB : sous l'engagement pris, dépendance aux alliés et perte de souveraineté."),
           (float("-inf"), "hors_sol",
            "Défense à {valeur} % du PIB : hors-sol — désarmement de fait, la sécurité du pays "
            "dépend entièrement de choix étrangers."),
       ]),
    # ── Profondeur temporelle : deux mandatures consécutives (2027-2037) ────
    _g(cle="usure_politique_pts", libelle="Usure du capital politique", strate=2, sens="max",
       unite="pts", precision=0, famille="general",
       source="R&D deux mandatures consécutives (docs/RD_DOUBLE_MANDATURE.md, point P4) ; "
              "baromètre de la confiance politique CEVIPOF.",
       cible=(20.0, "Objectif sur dix ans : préserver le capital politique sous 20 pts."),
       bornes=[
           (20.0, "favorable",
            "Usure à {valeur}/100 : le capital politique est intact, les réformes passent au calendrier prévu."),
           (35.0, "tolerable",
            "Usure à {valeur}/100 : fatigue normale de mi-parcours, séquencer les réformes et soigner l'évaluation."),
           (55.0, "vigilance",
            "Usure à {valeur}/100 : réforme de fatigue — chaque réforme coûte désormais plus cher politiquement qu'elle ne rapporte."),
           (75.0, "risque",
            "Usure à {valeur}/100 : fin de cycle, risque élevé de censure et de blocage parlementaire."),
           (float("inf"), "hors_sol",
            "Usure à {valeur}/100 : hors-sol — capital politique épuisé, plus aucune réforme n'est adoptable avant l'élection suivante."),
       ]),
    _g(cle="irreversibilite_reformes_active", libelle="Verrou constitutionnel des réformes",
       strate=2, sens="booleen", famille="general",
       source="Constitution de 1958, art. 89 (Congrès, majorité des 3/5) et art. 11 ; "
              "R&D deux mandatures (docs/RD_DOUBLE_MANDATURE.md, points P3 et P7).",
       cible=(1.0, "Objectif de la deuxième mandature : ancrer les réformes structurelles dans la Constitution."),
       bornes=[
           (1.0, "tolerable",
            "Réformes ancrées dans la Constitution : une alternance ne peut plus les abroger d'un trait de plume, "
            "les marchés et les citoyens anticipent dans la durée."),
           (0.0, "vigilance",
            "Réformes non verrouillées : sur deux mandatures, le risque d'abrogation par une alternance est systémique — "
            "chaque année électorale renchérit le crédit de l'État."),
       ]),
)


# ────────────────────────────────────────────────────────────────────────────
# Garde-fous « écart » : ce que vos mesures ajoutent à la trajectoire de référence
# ────────────────────────────────────────────────────────────────────────────

GARDE_FOUS_ECART: tuple[GardeFou, ...] = (
    _g(cle="deficit_ecart_pts", libelle="Déficit : écart à la référence (pt)", strate=2, sens="max",
       unite="pt", precision=2, famille="budget", ou="synthese",
       source="Différence entre la trajectoire choisie et la trajectoire sans aucune politique",
       bornes=[
           (0.25, "tolerable", "Vos mesures coûtent {valeur} pt de déficit par rapport à la trajectoire neutre."),
           (1.0, "vigilance",
            "Vos mesures creusent le déficit de {valeur} pt par rapport à la trajectoire neutre : "
            "il faudrait {marge} pt de recettes ou d'économies pour rester à l'équilibre des mesures."),
           (2.0, "risque",
            "Vos mesures ajoutent {valeur} pt de déficit à la trajectoire neutre : c'est ce qui "
            "transforme une consolidation en dérapage."),
           (float("inf"), "hors_sol",
            "Vos mesures ajoutent {valeur} pt de déficit : hors-sol. Aucune majorité ne financera "
            "un tel écart sans crise."),
       ]),
    _g(cle="dette_ecart_pts", libelle="Dette : écart à la référence (pt)", strate=2, sens="max",
       unite="pt", precision=1, famille="budget", ou="synthese",
       source="Différence entre la trajectoire choisie et la trajectoire neutre",
       bornes=[
           (0.5, "tolerable", "Vos mesures ajoutent {valeur} pt de dette."),
           (3.0, "vigilance", "Vos mesures ajoutent {valeur} pt de dette : il reste {marge} pt avant la zone de rupture."),
           (6.0, "risque", "Vos mesures ajoutent {valeur} pt de dette : le surcoût d'intérêts est définitif, la dette ne redescend pas seule."),
           (float("inf"), "hors_sol",
            "Vos mesures ajoutent {valeur} pt de dette : hors-sol, le stock devient incontrôlable "
            "sans décision de correction majeure."),
       ]),
    _g(cle="croissance_supplementaire_pts", libelle="Croissance : écart à la référence (pt)",
       strate=2, sens="min", unite="pt", precision=2, famille="economie", ou="synthese",
       source="PIB final de la trajectoire choisie ÷ PIB final de la trajectoire neutre "
              "(multiplicateurs du moteur : TVA +0,75, DGF +0,85, rentes −0,12)",
       cible=(0.5, "Une politique qui fait croître le PIB de 0,5 pt de plus que la référence."),
       bornes=[
           (0.0, "tolerable", "Vos mesures ne pèsent pas sur l'activité ({valeur} pt par rapport à la référence)."),
           (-0.5, "vigilance", "Vos mesures retirent {valeur} pt de PIB : les recettes attendues n'arriveront qu'en partie."),
           (-1.5, "risque", "Vos mesures retirent {valeur} pt de PIB : récession induite, le déficit se creuse malgré les économies."),
           (float("-inf"), "hors_sol",
            "Vos mesures retirent {valeur} pt de PIB : hors-sol — l'effet récessif annule "
            "l'objectif budgétaire poursuivi."),
       ]),
    _g(cle="solde_mesures_mde", libelle="Équilibre des mesures (Md€)", strate=2, sens="min",
       unite="Md€", precision=1, famille="budget", ou="synthese",
       source="Recettes nouvelles − dépenses nouvelles de l'année 5 (bouclage des mesures)",
       cible=(0.0, "Des mesures gagées, recettes ≥ dépenses nouvelles."),
       bornes=[
           (0.0, "favorable", "Vos mesures s'autofinancent : {valeur} Md€ de marge annuelle."),
           (-10.0, "vigilance", "Vos mesures coûtent {valeur} Md€ par an : c'est un choix d'endettement assumé."),
           (-25.0, "risque", "Vos mesures coûtent {valeur} Md€ par an : l'effort d'économies devra porter sur les services publics."),
           (float("-inf"), "hors_sol",
            "Vos mesures coûtent {valeur} Md€ par an : hors-sol financier, "
            "il faudra {marge} Md€ de recettes ou d'économies pour équilibrer."),
       ]),
    _g(cle="score_moyen_domaines", libelle="Score moyen des 20 domaines (/100)", strate=2,
       sens="min", unite="/100", precision=1, famille="general", ou="synthese",
       source="Moyenne des scores de domaine (50 = aucune politique)",
       cible=(55.0, "Une politique qui améliore l'ensemble des domaines de 5 points."),
       bornes=[
           (48.0, "tolerable", "Score moyen {valeur}/100 : vos mesures dégradent peu l'ensemble."),
           (44.0, "vigilance", "Score moyen {valeur}/100 : les pertes l'emportent sur les gains dans plusieurs domaines."),
           (38.0, "risque", "Score moyen {valeur}/100 : politique globalement coûteuse pour le pays."),
           (float("-inf"), "hors_sol",
            "Score moyen {valeur}/100 : hors-sol — presque tous les domaines se dégradent."),
       ]),
)


# ────────────────────────────────────────────────────────────────────────────
# Évaluation
# ────────────────────────────────────────────────────────────────────────────

def _niveau_du_pire(*niveaux: str) -> str:
    """Retourne le niveau le plus grave de la liste."""
    meilleurs = [n for n in niveaux if n in NIVEAUX]
    if not meilleurs:
        return "inconnu"
    return max(meilleurs, key=NIVEAUX.index)


def _valeur_numerique(garde_fou: GardeFou, valeur: Any) -> float | None:
    if isinstance(valeur, bool):
        return 1.0 if valeur else 0.0
    if isinstance(valeur, (int, float)):
        return float(valeur)
    if isinstance(valeur, str):
        return float(RANG_NOTES.get(valeur.strip().upper(), 12))
    return None


def _lire(donnees: dict[str, Any], garde_fou: GardeFou) -> Any:
    if garde_fou.ou == "synthese":
        if garde_fou.cle == "charge_dette_pib":
            charge = donnees.get("synthese", {}).get("charge_dette_finale_mde")
            pib = donnees.get("synthese", {}).get("pib_final_mde")
            if not charge or not pib:
                return None
            return charge / pib * 100.0
        return donnees.get("synthese", {}).get(garde_fou.cle)
    etapes = donnees.get("etapes") or []
    if not etapes:
        return None
    return etapes[-1].get(garde_fou.cle)


def _formater(valeur: float | str, garde_fou: GardeFou) -> str:
    if isinstance(valeur, str):
        return valeur
    if valeur is None or not math.isfinite(float(valeur)):
        return "—"
    if garde_fou.sens == "note":
        for note, rang in RANG_NOTES.items():
            if rang == int(round(valeur)):
                return note
        return f"rang {valeur:.0f}"
    if float(valeur).is_integer() and garde_fou.precision == 0:
        return f"{valeur:,.0f}".replace(",", " ")
    texte = f"{valeur:,.{garde_fou.precision}f}"
    return texte.replace(",", " ").replace(".", ",")


def evaluer_garde_fou(garde_fou: GardeFou, valeur_brute: Any) -> dict[str, Any] | None:
    """Applique un garde-fou à une valeur et retourne son diagnostic.

    Retourne `None` si la grandeur n'est pas mesurable (donnée absente).
    """
    valeur = _valeur_numerique(garde_fou, valeur_brute)
    if valeur is None:
        return None
    est_booleen = garde_fou.sens == "booleen"
    valeur_texte = _formater(valeur_brute if not est_booleen else valeur, garde_fou)

    def _correspond(borne: Borne) -> bool:
        if est_booleen:
            return (valeur >= 0.5) == (borne.seuil >= 0.5)
        if garde_fou.sens in ("max", "note"):
            return valeur <= borne.seuil
        return valeur >= borne.seuil

    index_actif: int | None = None
    for index, borne in enumerate(garde_fou.bornes):
        if _correspond(borne):
            index_actif = index
            break
    if index_actif is None:  # aucune borne ne matche : on retient la plus grave
        index_actif = len(garde_fou.bornes) - 1
    borne_active = garde_fou.bornes[index_actif]
    prochaine = garde_fou.bornes[index_actif + 1] if index_actif + 1 < len(garde_fou.bornes) else None

    # `{marge}` : distance au prochain seuil plus grave ; si l'on est déjà dans
    # le dernier palier (hors-sol), distance à franchir **en sens inverse**
    # pour revenir sous le seuil d'entrée du hors-sol.
    marge: float | None = None
    seuil_reference: float | None = None
    if prochaine is not None and math.isfinite(prochaine.seuil):
        # Le prochain palier est chiffré : marge avant de le franchir.
        seuil_reference = prochaine.seuil
        marge = abs(prochaine.seuil - valeur)
    elif math.isfinite(borne_active.seuil):
        # Palier courant chiffré, palier suivant hors-sol (borne infinie) : le
        # seuil de bascule est celui de la zone où l'on se trouve.
        seuil_reference = borne_active.seuil
        marge = abs(borne_active.seuil - valeur)
    elif index_actif > 0:
        # Déjà hors-sol : distance à franchir en sens inverse pour revenir sous
        # le seuil d'entrée du hors-sol.
        seuil_reference = garde_fou.bornes[index_actif - 1].seuil
        marge = abs(valeur - seuil_reference)

    champs = {
        "valeur": valeur_texte,
        "seuil": _formater(seuil_reference, garde_fou) if seuil_reference is not None else "—",
        "marge": _formater(marge, garde_fou) if marge is not None else "—",
        "unite": garde_fou.unite,
    }
    message = borne_active.message.format(**champs)

    progression = None
    if garde_fou.cible is not None:
        seuil_cible, message_cible = garde_fou.cible
        ecart_cible = (seuil_cible - valeur) if garde_fou.sens in ("min", "note") else (valeur - seuil_cible)
        if ecart_cible > 0:
            progression = {
                "seuil_cible": seuil_cible,
                "ecart": round(ecart_cible, 3),
                "message_cible": message_cible,
                "valeur_cible": _formater(seuil_cible, garde_fou),
            }

    return {
        "cle": garde_fou.cle,
        "libelle": garde_fou.libelle,
        "strate": garde_fou.strate,
        "sens": garde_fou.sens,
        "famille": garde_fou.famille,
        "niveau": borne_active.niveau,
        "valeur": round(valeur, 4),
        "valeur_texte": valeur_texte,
        "unite": garde_fou.unite,
        "precision": garde_fou.precision,
        "message": message,
        "source": garde_fou.source,
        "marge": None if marge is None else round(marge, 3),
        # `prochain_seuil` est le seuil de bascule chiffré (entrée de la zone
        # suivante, y compris quand cette zone suivante est le hors-sol).
        "prochain_seuil": None if seuil_reference is None else round(seuil_reference, 3),
        "prochain_niveau": None if prochaine is None else prochaine.niveau,
        "progression": progression,
    }


def evaluer_sortie(donnees: dict[str, Any]) -> dict[str, Any]:
    """Diagnostic complet d'une simulation : strates, alertes, marges, population.

    `donnees` est la charge utile sérialisée d'une `SortieSimulation`
    (`moteur_parametrique.SortieSimulation.en_dict()`).
    """
    evaluations: list[dict[str, Any]] = []
    for garde_fou in GARDE_FOUS + GARDE_FOUS_ECART:
        resultat = evaluer_garde_fou(garde_fou, _lire(donnees, garde_fou))
        if resultat is not None:
            evaluations.append(resultat)

    # ── Risque population : moyenne des domaines qui touchent les ménages ──
    scores = {d.get("cle"): d.get("score", 50.0) for d in donnees.get("domaines", [])}
    piliers = [scores[cle] for cle in DOMAINES_POPULATION if cle in scores]
    moyenne_population = sum(piliers) / len(piliers) if piliers else 50.0
    risque_population = max(0.0, min(100.0, 100.0 - moyenne_population))
    if risque_population <= 50.0:
        niveau_population = "tolerable"
    elif risque_population <= 58.0:
        niveau_population = "vigilance"
    elif risque_population <= 68.0:
        niveau_population = "risque"
    else:
        niveau_population = "hors_sol"
    population = {
        "valeur": round(risque_population, 1),
        "niveau": niveau_population,
        "score_moyen": round(moyenne_population, 1),
        "piliers": [
            {"cle": cle, "score": round(scores[cle], 1)} for cle in DOMAINES_POPULATION if cle in scores
        ],
        "message": {
            "tolerable": "Le risque population reste contenu : aucune mesure n'expose directement "
                         "les ménages dans cette simulation.",
            "vigilance": "Effet perceptible sur les ménages : à ce niveau, il faut accompagner la "
                         "mesure (compensation, étalement) pour qu'elle passe.",
            "risque": "La population est mise en danger : les pertes de pouvoir d'achat et de "
                      "services l'emportent sur les gains. Corrigez avant d'avancer.",
            "hors_sol": "STOP : les mesures exposent la population (pouvoir d'achat, santé, "
                        "logement, cohésion). Aucune réforme de cette ampleur ne survit sans "
                        "mesures de protection.",
        }[niveau_population],
    }

    # ── Regroupement par strate ───────────────────────────────────────────
    strates: dict[int, dict[str, Any]] = {}
    for strate, libelle in LIBELLES_STRATES.items():
        membres = [e for e in evaluations if e["strate"] == strate]
        if not membres:
            continue
        niveau = _niveau_du_pire(*(m["niveau"] for m in membres))
        strates[strate] = {
            "strate": strate,
            "libelle": libelle,
            "niveau": niveau,
            "familles": sorted({m["famille"] for m in membres}),
            "indicateurs": membres,
            "alertes": [m for m in membres if NIVEAUX.index(m["niveau"]) >= NIVEAUX.index(NIVEAU_ALERTE)],
        }

    # ── Alertes triées par gravité ────────────────────────────────────────
    alertes = sorted(
        (e for e in evaluations if NIVEAUX.index(e["niveau"]) >= NIVEAUX.index(NIVEAU_ALERTE)),
        key=lambda e: (-NIVEAUX.index(e["niveau"]), e["strate"], e["libelle"]),
    )
    # Déduplication des garde-fous symétriques (inflation trop haute / trop basse).
    vues: set[str] = set()
    alertes_uniques: list[dict[str, Any]] = []
    for alerte in alertes:
        marqueur = f"{alerte['cle']}"
        if marqueur in vues:
            continue
        vues.add(marqueur)
        alertes_uniques.append(alerte)

    # ── Marges de manœuvre et progrès possibles ───────────────────────────
    marges = []
    for e in evaluations:
        if (e["marge"] is not None and e["niveau"] != "hors_sol"
                and e["sens"] not in ("note", "booleen")):
            marges.append({
                "cle": e["cle"],
                "libelle": e["libelle"],
                "strate": e["strate"],
                "niveau": e["niveau"],
                "valeur_texte": e["valeur_texte"],
                "unite": e["unite"],
                "marge": e["marge"],
                "marge_texte": _formater(e["marge"], GardeFou(
                    cle=e["cle"], libelle=e["libelle"], strate=e["strate"], sens="max",
                    bornes=(), precision=e["precision"], unite=e["unite"])),
                "prochain_seuil": e["prochain_seuil"],
                "prochain_niveau": e["prochain_niveau"],
            })
    marges.sort(key=lambda m: m["marge"])
    progres = [e["progression"] | {"cle": e["cle"], "libelle": e["libelle"], "strate": e["strate"]}
               for e in evaluations if e["progression"] and e["niveau"] != "hors_sol"]
    progres.sort(key=lambda p: p["ecart"])

    niveau_global = _niveau_du_pire(
        *(s["niveau"] for s in strates.values()),
        population["niveau"],
    )
    verdicts = {
        "favorable": "Feu vert : trajectoire favorable, les garde-fous sont respectés.",
        "tolerable": "Feu vert : la trajectoire tient, rien d'irréversible n'est engagé.",
        "vigilance": "Feu orange : ça passe, mais il faut surveiller et accompagner.",
        "risque": "Feu rouge : les seuils de rupture approchent — corrigez les mesures signalées.",
        "hors_sol": "Hors-sol : STOP. Les mesures signalées mettent la population ou l'État en danger.",
        "inconnu": "Diagnostic indisponible : données manquantes.",
    }
    hors_sol = [e for e in evaluations if e["niveau"] == "hors_sol"]
    verdict = {
        "niveau": niveau_global,
        "libelle": LIBELLES_NIVEAUX.get(niveau_global, niveau_global),
        "message": verdicts[niveau_global],
        "nombre_alertes": len(alertes_uniques),
        "nombre_hors_sol": len(hors_sol),
        "strates_en_alerte": sorted({e["strate"] for e in alertes_uniques}),
    }

    return {
        "niveau_global": niveau_global,
        "verdict": verdict,
        "population": population,
        "strates": [strates[s] for s in sorted(strates)],
        "alertes": alertes_uniques,
        "marges": marges[:12],
        "progres": progres[:8],
        "indicateurs": evaluations,
        "barème": list(NIVEAUX),
        "libelles_niveaux": LIBELLES_NIVEAUX,
    }


def bareme_public() -> dict[str, Any]:
    """Barème complet des garde-fous, pour la section « audit et traçabilité ».

    Chaque entrée livre la grandeur surveillée, sa strate, ses bornes
    (seuil → niveau → message) et la source institutionnelle : la veille
    n'est pas une boîte noire, tout seuil est vérifiable à la source.
    """
    def borne(b: Borne) -> dict[str, Any]:
        # Une borne infinie (ex. « au-delà de… ») devient nulle : JSON ne
        # connaît pas Infinity et le navigateur doit pouvoir tout relire.
        seuil = b.seuil if math.isfinite(b.seuil) else None
        return {"seuil": seuil, "niveau": b.niveau, "message": b.message}

    def entree(garde_fou: GardeFou, en_ecart: bool) -> dict[str, Any]:
        return {
            "cle": garde_fou.cle,
            "libelle": garde_fou.libelle,
            "strate": garde_fou.strate,
            "strate_libelle": LIBELLES_STRATES.get(garde_fou.strate, ""),
            "sens": garde_fou.sens,
            "unite": garde_fou.unite,
            "precision": garde_fou.precision,
            "source": garde_fou.source,
            "famille": garde_fou.famille,
            "en_ecart": en_ecart,
            "bornes": [borne(b) for b in garde_fou.bornes],
        }

    return {
        "niveaux": list(NIVEAUX),
        "libelles_niveaux": LIBELLES_NIVEAUX,
        "libelles_strates": {str(cle): libelle for cle, libelle in LIBELLES_STRATES.items()},
        "garde_fous": ([entree(g, en_ecart=False) for g in GARDE_FOUS]
                       + [entree(g, en_ecart=True) for g in GARDE_FOUS_ECART]),
    }


def resume_court(diagnostic: dict[str, Any]) -> dict[str, Any]:
    """Version condensée (comparateur de préréglages, tableau de bord)."""
    verdict = diagnostic.get("verdict", {})
    population = diagnostic.get("population", {})
    return {
        "niveau_global": diagnostic.get("niveau_global"),
        "libelle": verdict.get("libelle"),
        "risque_population": population.get("valeur"),
        "niveau_population": population.get("niveau"),
        "nombre_alertes": verdict.get("nombre_alertes"),
        "nombre_hors_sol": verdict.get("nombre_hors_sol"),
        "premieres_alertes": [
            {"libelle": alerte["libelle"], "niveau": alerte["niveau"], "message": alerte["message"]}
            for alerte in diagnostic.get("alertes", [])[:3]
        ],
    }
