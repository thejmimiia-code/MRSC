"""
simulateur/moteur_parametrique.py — Orchestrateur du simulateur interactif.

Rôle : faire tourner le moteur systémique (`moteur.py`) sur des **choix libres**
(dossier `parametres.py`) et un **contexte réel daté** (`donnees_live.py`), puis
produire trois lectures complémentaires :

  1. `etapes`      : les 5 échelons du moteur, année par année (cascade causale) ;
  2. `domaines`    : les 20 domaines d'action publique (`domaines.py`) avec leurs
                     indicateurs, leur trajectoire et leur score ;
  3. `impacts`     : la **matrice croisée levier × domaine**, calculée par
                     différences finies sur le modèle lui-même (aucun coefficient
                     saisi à la main : l'impact affiché est celui du moteur).

Deux trajectoires sont systématiquement calculées :

  * la **trajectoire de référence** (tous leviers neutres) : ce qui se passerait
    si l'on ne changeait rien, avec les données réelles du jour ;
  * la **trajectoire choisie**, qui permet d'afficher des ÉCARTS plutôt que des
    niveaux — la question posée étant « qu'est-ce que mes choix changent ? ».
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass, field
from typing import Any

from simulateur.domaines import (
    DOMAINES,
    SPECS,
    MediateursAnnee,
    catalogue_domaines,
    construire_flux,
    decision_moteur,
    evaluer_domaines,
    evaluer_indicateur,
)
from simulateur.donnees_live import ContexteInstant, construire_contexte
from simulateur.model import ResultatEtapeSimulation
from simulateur.moteur import MoteurSimulationSystemique
from simulateur.parametres import (
    FAMILLES,
    LEVIERS,
    PRESETS,
    normaliser,
)
from simulateur.parametres import (
    catalogue_public as catalogue_parametres,
)
from simulateur.seuils import evaluer_sortie, resume_court

#: Nombre de passes de la boucle de médiateurs (les écarts d'un domaine
#: alimentent les domaines suivants : chômage → pauvreté → cohésion…).
PASSES_MEDIATEURS = 4

#: Cache mémoire des analyses de sensibilité (clé = empreinte des paramètres).
_CACHE_IMPACTS: dict[str, list[dict[str, Any]]] = {}


# ────────────────────────────────────────────────────────────────────────────
# 1. Calibrage du moteur sur les données réelles
# ────────────────────────────────────────────────────────────────────────────

def calibrer_contexte(moteur: MoteurSimulationSystemique,
                      contexte: ContexteInstant) -> MoteurSimulationSystemique:
    """Recale les 5 échelons du moteur sur l'instantané de données publiques.

    Les grandeurs de référence du moteur (`moteur.reference`) sont réécrites :
    les écarts (taux, pétrole, change, recettes, dépenses) sont donc mesurés
    **par rapport à l'instant T réel**, et non par rapport au calage du projet.
    """
    pib = contexte.pib_nominal_mde
    dette = contexte.dette_publique_pct_pib / 100.0 * pib
    charge = contexte.charge_dette_estimee_mde

    # Strate 2 — nationale
    moteur.national.pib_nominal_mde = pib
    moteur.national.dette_maastricht_stock_mde = dette
    # Croissance nominale tendancielle = croissance réelle potentielle (~1,1 %)
    # + inflation observée : la base nominale suit les prix.
    moteur.national.taux_croissance_potentiel = round(
        0.011 + max(0.0, contexte.inflation_pct) / 100.0, 4
    )
    moteur.national.etat.charge_nette_dette_mde = charge
    moteur.national.confiance_democratique = 27.5  # baromètre CEVIPOF (base de comparaison)

    # Strate 3 — européenne
    moteur.europe.taux_depot_bce_pct = contexte.taux_bce_depot
    moteur.europe.statut_pde_actif = contexte.deficit_public_pct_pib > 3.0

    # Strate 4 — mondiale
    moteur.mondial.taux_oat_france_10ans = contexte.taux_oat_10ans
    moteur.mondial.taux_bund_allemagne_10ans = contexte.taux_bund_10ans
    moteur.mondial.taux_credit_immobilier_menages = contexte.taux_credit_immobilier_menages_pct
    moteur.mondial.spread_oat_bund_bps = contexte.spread_oat_bund_bps
    moteur.mondial.cours_petrole_brent_usd = contexte.brent_usd
    moteur.mondial.taux_change_eur_usd = contexte.eur_usd
    moteur.mondial.inflation_globale_pct = contexte.inflation_pct
    moteur.mondial.note_souveraine = "AA-"

    # Recettes publiques : recettes = dépenses − déficit (identité comptable),
    # avec le ratio de dépenses publiques du projet (57 % du PIB, doc. de mandature).
    ratio_depenses = 57.0
    recettes_pct = ratio_depenses - contexte.deficit_public_pct_pib
    moteur.reference.update({
        "brent_usd": contexte.brent_usd,
        "eur_usd": contexte.eur_usd,
        "inflation_pct": contexte.inflation_pct,
        "taux_oat_pct": contexte.taux_oat_10ans,
        "taux_bund_pct": contexte.taux_bund_10ans,
        "taux_credit_immobilier_pct": contexte.taux_credit_immobilier_menages_pct,
        "spread_bps": contexte.spread_oat_bund_bps,
        "facture_energetique_mde": round(pib * 0.022, 1),
        "recettes_base_mde": round(pib * recettes_pct / 100.0, 1),
        # Le moteur retire puis rajoute la charge de la dette : la référence est
        # donc la dépense publique TOTALE (57 % du PIB), charge incluse.
        "depenses_primaires_mde": round(pib * ratio_depenses / 100.0, 1),
    })

    # Strate 5 — géopolitique : les théâtres partent de l'état documenté du projet.
    moteur.geo.depenses_defense_mde = round(
        contexte.depenses_defense_pct_pib / 100.0 * pib, 1
    )
    return moteur


def moteur_calibre(contexte: ContexteInstant) -> MoteurSimulationSystemique:
    """Instancie un moteur neuf, recalé sur le contexte réel."""
    return calibrer_contexte(MoteurSimulationSystemique(), contexte)


# ────────────────────────────────────────────────────────────────────────────
# 2. Exécution d'une série annuelle
# ────────────────────────────────────────────────────────────────────────────

def _executer_serie(parametres: dict[str, float], contexte: ContexteInstant,
                    horizon: int) -> tuple[MoteurSimulationSystemique, list[dict[str, float]]]:
    """Déroule les `horizon` années et retourne (moteur, flux annuels)."""
    moteur = moteur_calibre(contexte)
    flux_par_annee: list[dict[str, float]] = []
    for annee in range(1, horizon + 1):
        decision = decision_moteur(parametres, annee, horizon=horizon)
        moteur.appliquer_etape(decision)
        flux_par_annee.append(construire_flux(parametres, annee - 1))
    return moteur, flux_par_annee


def _ecart_relatif(valeur: float, reference: float) -> float:
    if abs(reference) < 1e-9:
        return 0.0
    return (valeur - reference) / abs(reference)


def _mediteurs_annee(resultat: ResultatEtapeSimulation, flux: dict[str, float],
                     contexte: ContexteInstant, annee_index: int,
                     cumul_solde_mde: float,
                     reference: MediateursAnnee | None) -> MediateursAnnee:
    """Assemble les médiateurs d'une année : moteur + flux de leviers."""
    mediateurs = MediateursAnnee(annee=resultat.annee)
    mediateurs.pib_initial_mde = contexte.pib_nominal_mde
    mediateurs.pib_nominal_mde = resultat.pib_nominal_mde
    mediateurs.inflation_pct = resultat.inflation_globale_pct
    mediateurs.deficit_pct_pib = resultat.ratio_deficit_pib
    mediateurs.dette_pct_pib = resultat.ratio_dette_pib
    mediateurs.charge_dette_mde = resultat.charge_dette_mde
    mediateurs.taux_oat = resultat.taux_oat_pct
    mediateurs.spread_bps = resultat.spread_bund_bps
    mediateurs.tension_sociale = resultat.tension_sociale_locale
    mediateurs.confiance_democratique = resultat.confiance_democratique
    mediateurs.risque_censure_pct = resultat.risque_censure_parlement
    mediateurs.effort_defense_pts = resultat.effort_defense_pct_pib
    mediateurs.indice_geo = resultat.indice_tension_geopolitique
    mediateurs.brent_usd = resultat.cours_petrole_usd
    mediateurs.eur_usd = resultat.taux_change_eur_usd
    mediateurs.pouvoir_achat_index = resultat.pouvoir_achat_index
    mediateurs.disponibilite_semiconducteurs_pct = resultat.disponibilite_semiconducteurs_pct

    flux = dict(flux)
    # ── Grandeurs dérivées du résultat moteur ──────────────────────────────
    flux["prix_energie_ecart_pct"] = round(
        (resultat.cours_petrole_usd - contexte.brent_usd) / contexte.brent_usd * 100.0, 2
    )
    flux["choc_petrole_pct"] = flux["prix_energie_ecart_pct"]
    flux["change_impact_pct"] = round(
        (resultat.taux_change_eur_usd - contexte.eur_usd) / contexte.eur_usd * 100.0, 2
    )
    flux["taux_oat_ecart_pts"] = round(resultat.taux_oat_pct - contexte.taux_oat_10ans, 3)
    flux["spread_oat_ecart_bps"] = round(resultat.spread_bund_bps - contexte.spread_oat_bund_bps, 1)
    flux["taux_credit_ecart_pts"] = round(
        resultat.taux_credit_pme - (contexte.taux_oat_10ans + 0.85), 3
    )
    taux_immobilier_reference = contexte.taux_credit_immobilier_menages_pct
    flux["taux_credit_immobilier_ecart_pts"] = round(
        resultat.taux_credit_immobilier_menages - taux_immobilier_reference, 3
    )
    flux["chokepoints_nb"] = float(resultat.chokepoints_sous_tension)
    flux["choc_semi"] = 1.0 - float(resultat.disponibilite_semiconducteurs_pct) / 100.0
    flux["solde_budgetaire_mde"] = round(cumul_solde_mde, 2)
    flux["effort_structurel_mde"] = round(max(0.0, cumul_solde_mde), 2)
    flux["effort_defense_ecart_pts"] = round(
        resultat.effort_defense_pct_pib - contexte.depenses_defense_pct_pib, 3
    )
    flux["defense_mde"] = round(resultat.depenses_defense_mde, 2)
    flux["activite_ecart_pct"] = 0.0  # renseigné par comparaison ci-dessous
    flux["pollution_ecart_pts"] = 0.0
    flux["climat_choc_pts"] = 0.0
    flux["incertitude_geo"] = max(0.0, (resultat.indice_tension_geopolitique - 63.0) / 20.0)
    flux["choc_monde"] = flux.get("choc_monde", 0.0)
    flux["stabilite_pts"] = 0.0
    flux["lien_social_ecart_pts"] = 0.0
    flux["politique_penale_mde"] = flux.get("justice_mde", 0.0)

    mediateurs.flux = flux
    if reference is not None:
        mediateurs.ecarts = {
            "deficit_ecart_pts": round(resultat.ratio_deficit_pib - reference.deficit_pct_pib, 4),
            "dette_ecart_pts": round(resultat.ratio_dette_pib - reference.dette_pct_pib, 4),
            "tension_ecart_pts": round(
                resultat.tension_sociale_locale - reference.tension_sociale, 3
            ),
            "confiance_ecart_pts": round(
                resultat.confiance_democratique - reference.confiance_democratique, 3
            ),
            "activite_ecart_pct": round(
                (resultat.pib_nominal_mde - reference.pib_nominal_mde)
                / max(reference.pib_nominal_mde, 1.0) * 100.0,
                3,
            ),
            "pouvoir_achat_ecart_pct": round(
                resultat.pouvoir_achat_index - reference.pouvoir_achat_index, 3
            ),
        }
        mediateurs.ecarts["chomage_ecart_pts"] = 0.0  # renseigné par la boucle
        mediateurs.ecarts["pauvrete_ecart_pts"] = 0.0
        mediateurs.ecarts["inegalites_ecart_pts"] = 0.0
        mediateurs.ecarts["criminalite_ecart_pts"] = 0.0
        mediateurs.ecarts["marches_ecart_pts"] = round(
            -(resultat.spread_bund_bps - reference.spread_bps) / 10.0, 3
        )
        mediateurs.ecarts["pollution_ecart_pts"] = 0.0
        mediateurs.ecarts["climat_choc_pts"] = 0.0
        mediateurs.ecarts["stabilite_ecart_pts"] = round(
            reference.risque_censure_pct - resultat.risque_censure_parlement, 3
        )
        mediateurs.ecarts["lien_social_ecart_pts"] = round(
            (resultat.tension_sociale_locale - reference.tension_sociale) * -0.3, 3
        )
    else:
        mediateurs.ecarts = {
            "deficit_ecart_pts": 0.0,
            "dette_ecart_pts": 0.0,
            "tension_ecart_pts": 0.0,
            "confiance_ecart_pts": 0.0,
            "activite_ecart_pct": 0.0,
            "pouvoir_achat_ecart_pct": 0.0,
            "marches_ecart_pts": 0.0,
            "stabilite_ecart_pts": 0.0,
            "lien_social_ecart_pts": 0.0,
        }
    # Grandeurs dérivées « chaînées » (complétées par la boucle de convergence).
    mediateurs.flux["inflation_ecart_pts"] = round(
        resultat.inflation_globale_pct - contexte.inflation_pct, 3
    )
    mediateurs.flux["choc_semi_pct"] = round(
        (1.0 - resultat.disponibilite_semiconducteurs_pct / 100.0) * 100.0, 2
    )
    mediateurs.flux["services_proximite_ecart_pts"] = round(
        resultat.qualite_services_proximite - 64.0, 3
    )
    mediateurs.flux["tension_moteur_ecart_pts"] = round(
        resultat.tension_sociale_locale - 36.0, 3
    )
    mediateurs.flux["pouvoir_achat_ecart_pct"] = round(
        resultat.pouvoir_achat_index - 100.0, 3
    )
    mediateurs.flux["competitivite_pts"] = round(
        flux.get("relocalisations_mde", 0.0) / 10.0
        + flux.get("simplification_mde", 0.0) / 5.0
        - flux.get("taxe_carbone_eur_t", 0.0) / 25.0,
        3,
    )
    mediateurs.flux["dependance_import_pts"] = round(
        -flux.get("relocalisations_mde", 0.0) / 5.0
        - flux.get("souverainete_mde", 0.0) / 5.0
        + flux.get("choc_monde", 0.0) * 5.0,
        3,
    )
    # Recettes nouvelles rapportées au PIB de l'année (points de PIB).
    mediateurs.flux["recettes_nouvelles_pts"] = round(
        flux.get("recettes_nouvelles_mde", 0.0) / max(resultat.pib_nominal_mde, 1.0) * 100.0, 4
    )
    # Confiance des marchés : un spread qui s'écarte de la référence détend ou
    # crispe les investisseurs (10 bps d'écart = 1 point d'indice).
    mediateurs.flux["confiance_marche_delta_pts"] = round(
        -(resultat.spread_bund_bps - contexte.spread_oat_bund_bps) / 10.0, 3
    )
    if reference is not None:
        # Écart annuel moyen de croissance nominale (points de %/an).
        ratio = resultat.pib_nominal_mde / max(reference.pib_nominal_mde, 1.0)
        mediateurs.ecarts["croissance_nominale_ecart_pts"] = round(
            (ratio ** (1.0 / max(resultat.annee, 1)) - 1.0) * 100.0, 3
        )
        # Écart d'activité : cumulé puis ramené en moyenne annuelle.
        mediateurs.ecarts["pib_ecart_croissance_pts"] = round(
            mediateurs.ecarts.get("activite_ecart_pct", 0.0) / max(resultat.annee, 1), 3
        )
        # Loi d'Okun : 1 point de croissance soutenue ≈ 150 000 emplois.
        mediateurs.ecarts["creations_emplois_milliers"] = round(
            150.0 * mediateurs.ecarts["pib_ecart_croissance_pts"], 2
        )
        mediateurs.ecarts["progressivite_ecart_pts"] = round(
            flux.get("progressivite_pts", 0.0), 3
        ) if reference is None else round(
            flux.get("progressivite_pts", 0.0) - reference.flux.get("progressivite_pts", 0.0), 3
        )
    return mediateurs


# ────────────────────────────────────────────────────────────────────────────
# 3. Boucle de convergence des médiateurs
# ────────────────────────────────────────────────────────────────────────────

def _valeurs_indicateurs(mediateurs: list[MediateursAnnee],
                         contexte: ContexteInstant) -> dict[str, list[float]]:
    return {
        spec.cle: [evaluer_indicateur(spec, m, contexte) for m in mediateurs]
        for spec in SPECS
    }


#: Indicateurs dont l'écart alimente les autres domaines.
#: La colonne de droite donne le médiateur alimenté et le **facteur d'échelle**
#: appliqué, pour que chaque coefficient garde un sens physique (un point
#: d'indice, un million de tonnes, dix points de sentiment de sécurité…).
_REACTIONS: dict[str, tuple[str, float]] = {
    "chomage": ("chomage_ecart_pts", 1.0),              # points de taux de chômage
    "pauvrete": ("pauvrete_ecart_pts", 1.0),            # points de taux de pauvreté
    "gini": ("inegalites_ecart_pts", 1.0),              # points de Gini
    "sentiment_securite": ("criminalite_ecart_pts", -0.1),  # −10 pts de sentiment = +1
    "emissions_co2": ("pollution_ecart_pts", 1.0),      # Mt de CO₂
}


def _boucle_mediateurs(mediateurs: list[MediateursAnnee], valeurs_reference: dict[str, list[float]],
                       contexte: ContexteInstant,
                       passes: int = PASSES_MEDIATEURS) -> tuple[list[MediateursAnnee],
                                                                 dict[str, list[float]]]:
    """Itère : les écarts d'un domaine nourrissent les formules des suivants."""
    valeurs = _valeurs_indicateurs(mediateurs, contexte)
    for _ in range(passes):
        for annee, mediateurs_annee in enumerate(mediateurs):
            for indicateur, (mediateur, facteur) in _REACTIONS.items():
                serie_ref = valeurs_reference.get(indicateur)
                serie = valeurs.get(indicateur)
                if not serie_ref or not serie:
                    continue
                mediateurs_annee.ecarts[mediateur] = round(
                    (serie[annee] - serie_ref[annee]) * facteur, 3
                )
            # Effets croisés sur la confiance et la tension (déjà portés par le moteur)
            mediateurs_annee.flux["lien_social_ecart_pts"] = round(
                -0.30 * mediateurs_annee.ecarts.get("tension_ecart_pts", 0.0), 3
            )
            mediateurs_annee.flux["stabilite_pts"] = round(
                mediateurs_annee.ecarts.get("stabilite_ecart_pts", 0.0), 3
            )
            # Dommages climatiques : adossés à l'effort d'adaptation (− 1 point de
            # dommage par 10 Md€ investis) ; aucun retour sur lui-même.
            mediateurs_annee.flux["climat_choc_pts"] = round(
                -mediateurs_annee.flux.get("adaptation_mde", 0.0) / 10.0, 3
            )
        valeurs = _valeurs_indicateurs(mediateurs, contexte)
    return mediateurs, valeurs


# ────────────────────────────────────────────────────────────────────────────
# 4. Simulation complète
# ────────────────────────────────────────────────────────────────────────────

@dataclass
class SortieSimulation:
    """Charge utile complète renvoyée à l'interface ou à un test."""

    horodatage: str
    contexte: dict[str, Any]
    parametres: dict[str, float]
    etapes: list[dict[str, Any]]
    domaines: list[dict[str, Any]]
    synthese: dict[str, Any]
    impact_bandeau: dict[str, float]
    journal: list[str]
    avertissements: list[str] = field(default_factory=list)
    impacts: list[dict[str, Any]] = field(default_factory=list)
    diagnostic: dict[str, Any] = field(default_factory=dict)
    horizon: int = 5
    #: Trajectoire sans levier, mêmes années et mêmes données de départ.
    etapes_reference: list[dict[str, Any]] = field(default_factory=list)
    #: Flux annuels du scénario et de la référence, dont les clés `levier:*`.
    flux_annuels: list[dict[str, Any]] = field(default_factory=list)
    flux_reference: list[dict[str, Any]] = field(default_factory=list)
    domaines_reference: list[dict[str, Any]] = field(default_factory=list)

    def en_dict(self) -> dict[str, Any]:
        return asdict(self)


def simuler(parametres: dict[str, float] | None = None,
            contexte: ContexteInstant | None = None,
            *,
            horizon: int = 5,
            avec_impacts: bool = True,
            max_leviers_impacts: int = 24) -> SortieSimulation:
    """Exécute une simulation complète : moteur + domaines + matrice d'impacts."""
    if not 1 <= horizon <= 10:
        raise ValueError("L'horizon de simulation doit être compris entre 1 et 10 ans.")
    parametres_normalises = normaliser(parametres)
    contexte = contexte or construire_contexte()
    avertissements: list[str] = []
    if contexte.mode != "live":
        avertissements.append(
            "Données de contexte non entièrement rafraîchies (mode "
            f"« {contexte.mode} ») : chaque valeur de référence conserve sa propre "
            "période et sa date de vérification dans la provenance. Utilisez « Rafraîchir "
            "les données » pour tenter une collecte auprès des API publiques."
        )
    avertissements.append(
        "Trajectoire de référence = moteur inchangé, leviers neutres. Elle inclut la "
        "consolidation budgétaire automatique du modèle (indexation des recettes sur le "
        "PIB nominal). Les impacts affichés sont donc des ÉCARTS par rapport à cette "
        "référence, et non des niveaux absolus."
    )

    # 1) Trajectoire de référence (tous leviers neutres)
    moteur_ref, flux_ref = _executer_serie({}, contexte, horizon)
    mediateurs_ref = [
        _mediteurs_annee(resultat, flux_ref[i], contexte, i, 0.0, None)
        for i, resultat in enumerate(moteur_ref.historique_etapes)
    ]
    valeurs_ref = _valeurs_indicateurs(mediateurs_ref, contexte)

    # 2) Trajectoire choisie
    moteur, flux_annee = _executer_serie(parametres_normalises, contexte, horizon)
    mediateurs: list[MediateursAnnee] = []
    cumul = 0.0
    for i, resultat in enumerate(moteur.historique_etapes):
        flux = flux_annee[i]
        cumul += flux.get("recettes_nouvelles_mde", 0.0) - flux.get("depenses_nouvelles_mde", 0.0)
        mediateurs.append(_mediteurs_annee(resultat, flux, contexte, i, cumul, mediateurs_ref[i]))
    mediateurs, valeurs = _boucle_mediateurs(mediateurs, valeurs_ref, contexte)

    # 3) Domaines — deux lectures complémentaires :
    #    * `tendances` : ce qui se passerait sans aucune politique (année 1 → 5) ;
    #    * `domaines`  : l'impact de la politique choisie, mesuré par écart à la
    #      trajectoire de référence (50 = aucun effet sur le domaine).
    domaines_ref = evaluer_domaines(mediateurs_ref, contexte)
    tendances = {d.cle: d.score for d in domaines_ref}
    domaines = evaluer_domaines(mediateurs, contexte, references=valeurs_ref,
                                tendances=tendances)
    scores_ref = {d.cle: 50.0 for d in domaines}
    scores_base = {d.cle: d.score for d in domaines}

    # 4) Impacts croisés levier → domaines
    impacts: list[dict[str, Any]] = []
    if avec_impacts:
        impacts = _impacts_par_levier(parametres_normalises, contexte, horizon,
                                      scores_base, max_leviers_impacts,
                                      references=valeurs_ref)

    # 5) Synthèse
    final = moteur.historique_etapes[-1]
    reference_final = moteur_ref.historique_etapes[-1]
    dernier_flux = flux_annee[-1] if flux_annee else {}
    synthese = {
        "deficit_final_pct": final.ratio_deficit_pib,
        "deficit_reference_pct": reference_final.ratio_deficit_pib,
        "deficit_ecart_pts": round(final.ratio_deficit_pib - reference_final.ratio_deficit_pib, 2),
        "dette_finale_pct": final.ratio_dette_pib,
        "dette_reference_pct": reference_final.ratio_dette_pib,
        "dette_ecart_pts": round(final.ratio_dette_pib - reference_final.ratio_dette_pib, 2),
        "pib_final_mde": final.pib_nominal_mde,
        "croissance_supplementaire_pts": round(
            (final.pib_nominal_mde - reference_final.pib_nominal_mde)
            / max(reference_final.pib_nominal_mde, 1.0) * 100.0,
            2,
        ),
        "taux_oat_final": final.taux_oat_pct,
        "spread_final_bps": final.spread_bund_bps,
        "taux_credit_pme_final": final.taux_credit_pme,
        "taux_credit_immobilier_final": final.taux_credit_immobilier_menages,
        "taux_credit_immobilier_reference": reference_final.taux_credit_immobilier_menages,
        "taux_credit_immobilier_ecart_pts": round(
            final.taux_credit_immobilier_menages - reference_final.taux_credit_immobilier_menages, 2
        ),
        "note_souveraine": final.note_souveraine,
        "tension_finale": final.tension_sociale_locale,
        "confiance_finale": final.confiance_democratique,
        "risque_censure_final_pct": final.risque_censure_parlement,
        "statut_pde": final.statut_pde_europe,
        "bouclier_tpi": final.bouclier_tpi_actif,
        "charge_dette_finale_mde": final.charge_dette_mde,
        "effort_defense_final_pct": final.effort_defense_pct_pib,
        "recettes_nouvelles_mde": round(dernier_flux.get("recettes_nouvelles_mde", 0.0), 2),
        "depenses_nouvelles_mde": round(dernier_flux.get("depenses_nouvelles_mde", 0.0), 2),
        "solde_mesures_mde": round(
            dernier_flux.get("recettes_nouvelles_mde", 0.0)
            - dernier_flux.get("depenses_nouvelles_mde", 0.0), 2
        ),
        "score_moyen_domaines": round(sum(d.score for d in domaines) / max(len(domaines), 1), 1),
        "score_moyen_reference": round(
            sum(scores_ref.values()) / max(len(scores_ref), 1), 1
        ),
        "nombre_domaines_en_hausse": sum(1 for d in domaines if d.score > 50.5),
        "nombre_domaines_en_baisse": sum(1 for d in domaines if d.score < 49.5),
        # P21 : un tableau de bord intergénérationnel en composantes physiques,
        # sans indice composite ni pondération normative cachée.
        "bilan_intergenerationnel": {
            "annee_terminal": final.annee,
            "dette_publique_mde": final.dette_nominale_mde,
            "dette_publique_pct_pib": final.ratio_dette_pib,
            "besoin_non_couvert_capital_public_mde": final.dette_technique_infrastructures_mde,
            "investissements_longs_engages_cumules_mde": final.investissements_longs_engages_cumules_mde,
            "actifs_arrives_a_maturite_mde": {
                "cycle_long": final.investissements_matures_mde,
                "capital_humain_proxy": final.capital_humain_mature_mde,
                "capacites_bitd_proxy": final.capacites_defense_matures_mde,
            },
            "risque_climat_annualise_hors_budget_mde": final.dommages_climat_subis_mde,
            "dommages_climat_evites_annualises_hors_budget_mde": final.dommages_climat_evites_mde,
            "note_methodologique": (
                "Composantes séparées, pas de score synthétique : les actifs mûrs, "
                "la dette publique, le besoin de patrimoine non couvert et le risque "
                "climatique n'ont ni la même unité ni la même incidence."
            ),
        },
    }

    journal: list[str] = []
    for resultat in moteur.historique_etapes:
        journal.extend(resultat.commentaires)

    # 6) Garde-fous : seuils tolérables, risqués et hors-sol, strate par strate.
    #    Le diagnostic voyage avec chaque simulation : l'interface affiche donc
    #    en permanence les conséquences d'un réglage, sans aller-retour réseau.
    return SortieSimulation(
        horodatage=contexte.horodatage,
        contexte=contexte.en_dict(),
        parametres=parametres_normalises,
        etapes=[asdict(r) for r in moteur.historique_etapes],
        domaines=[d.en_dict() | {"score_reference": scores_ref.get(d.cle, 50.0)}
                  for d in domaines],
        synthese=synthese,
        impact_bandeau={
            "recettes_nouvelles_mde": synthese["recettes_nouvelles_mde"],
            "depenses_nouvelles_mde": synthese["depenses_nouvelles_mde"],
            "solde_mesures_mde": synthese["solde_mesures_mde"],
            "score_moyen": synthese["score_moyen_domaines"],
            "score_reference": synthese["score_moyen_reference"],
        },
        journal=journal,
        avertissements=avertissements,
        impacts=impacts,
        diagnostic=evaluer_sortie({
            "etapes": [asdict(r) for r in moteur.historique_etapes],
            "domaines": [d.en_dict() for d in domaines],
            "synthese": synthese,
        }),
        horizon=horizon,
        etapes_reference=[asdict(r) for r in moteur_ref.historique_etapes],
        flux_annuels=[{"annee": i + 1, **flux} for i, flux in enumerate(flux_annee)],
        flux_reference=[{"annee": i + 1, **flux} for i, flux in enumerate(flux_ref)],
        domaines_reference=[d.en_dict() for d in domaines_ref],
    )


# ────────────────────────────────────────────────────────────────────────────
# 5. Impacts croisés levier × domaine
# ────────────────────────────────────────────────────────────────────────────

def _scores_domaines(parametres: dict[str, float], contexte: ContexteInstant,
                     horizon: int,
                     references: dict[str, list[float]] | None = None) -> dict[str, float]:
    """Scores de domaine d'un jeu de paramètres, mesurés par écart à la référence."""
    moteur, flux = _executer_serie(parametres, contexte, horizon)
    mediateurs = [
        _mediteurs_annee(r, flux[i], contexte, i, 0.0, None)
        for i, r in enumerate(moteur.historique_etapes)
    ]
    mediateurs, _ = _boucle_mediateurs(mediateurs, {}, contexte, passes=2)
    domaines = evaluer_domaine_depuis_mediateurs(mediateurs, contexte, references=references)
    return {d.cle: d.score for d in domaines}


def evaluer_domaine_depuis_mediateurs(mediateurs: list[MediateursAnnee],
                                      contexte: ContexteInstant,
                                      references: dict[str, list[float]] | None = None):
    """Évaluation légère des domaines, avec ou sans trajectoire de référence."""
    return evaluer_domaines(mediateurs, contexte, references=references)


def _empreinte(parametres: dict[str, float], contexte: ContexteInstant, horizon: int) -> str:
    charge = json.dumps(
        {"p": parametres, "h": horizon, "c": contexte.horodatage, "m": contexte.mode},
        sort_keys=True, default=str,
    )
    return hashlib.sha256(charge.encode("utf-8")).hexdigest()[:24]


def _impacts_par_levier(parametres: dict[str, float], contexte: ContexteInstant,
                        horizon: int, scores_base: dict[str, float],
                        maximum: int,
                        references: dict[str, list[float]] | None = None) -> list[dict[str, Any]]:
    """Matrice des effets marginaux : chaque levier actif, domaine par domaine.

    L'effet est calculé par **différence finie sur le modèle** : on rejoue la
    simulation avec ce seul levier ramené à sa valeur neutre, et l'on mesure la
    variation de score de chaque domaine. Aucun coefficient n'est saisi à la main.
    """
    actifs = [
        cle for cle in LEVIERS
        if abs(parametres.get(cle, 0.0) - LEVIERS[cle].defaut) > 1e-9
    ]
    if not actifs:
        return []
    # Priorité : leviers dont l'impact budgétaire est le plus important.
    actifs.sort(
        key=lambda cle: abs(
            (parametres.get(cle, 0.0) - LEVIERS[cle].defaut) * LEVIERS[cle].facteur
        ),
        reverse=True,
    )
    actifs = actifs[:maximum]
    empreinte = _empreinte({k: parametres[k] for k in actifs}, contexte, horizon)
    if empreinte in _CACHE_IMPACTS:
        return _CACHE_IMPACTS[empreinte]

    impacts: list[dict[str, Any]] = []
    for cle in actifs:
        sans = dict(parametres)
        sans[cle] = LEVIERS[cle].defaut
        scores = _scores_domaines(sans, contexte, horizon, references=references)
        effets = []
        for domaine in DOMAINES:
            ecart = round(scores_base.get(domaine.cle, 50.0) - scores.get(domaine.cle, 50.0), 1)
            if abs(ecart) >= 0.1:
                effets.append({
                    "domaine": domaine.cle,
                    "libelle": domaine.libelle,
                    "effet_score": ecart,
                })
        effets.sort(key=lambda item: abs(item["effet_score"]), reverse=True)
        if effets:
            impacts.append({
                "levier": cle,
                "libelle": LEVIERS[cle].libelle,
                "famille": LEVIERS[cle].famille,
                "valeur": parametres.get(cle, 0.0),
                "effets": effets,
            })
    impacts.sort(key=lambda item: max(abs(e["effet_score"]) for e in item["effets"]), reverse=True)
    _CACHE_IMPACTS[empreinte] = impacts
    return impacts


def tableau_croise(impacts: list[dict[str, Any]]) -> dict[str, Any]:
    """Met la matrice d'impacts en forme pour un affichage croisé."""
    domaines = [d.cle for d in DOMAINES]
    lignes = []
    for impact in impacts:
        ligne = {"levier": impact["levier"], "libelle": impact["libelle"],
                 "famille": impact["famille"], "effets": {}}
        for effet in impact["effets"]:
            ligne["effets"][effet["domaine"]] = effet["effet_score"]
        lignes.append(ligne)
    return {"domaines": [{"cle": d.cle, "libelle": d.libelle, "couleur": d.couleur}
                         for d in DOMAINES],
            "colonnes_domaines": domaines, "lignes": lignes}


# ────────────────────────────────────────────────────────────────────────────
# 6. Comparaison de scénarios et API
# ────────────────────────────────────────────────────────────────────────────

def comparer(scenarios: dict[str, dict[str, float]] | None = None,
             contexte: ContexteInstant | None = None,
             horizon: int = 5) -> dict[str, Any]:
    """Compare plusieurs jeux de paramètres (préréglages par défaut)."""
    contexte = contexte or construire_contexte()
    if scenarios is None:
        scenarios = {cle: preset["parametres"] for cle, preset in PRESETS.items()}
    resultats = []
    for cle, parametres in scenarios.items():
        sortie = simuler(parametres, contexte, horizon=horizon, avec_impacts=False)
        resultats.append({
            "cle": cle,
            "libelle": PRESETS.get(cle, {}).get("libelle", cle),
            "synthese": sortie.synthese,
            "scores": {d["cle"]: d["score"] for d in sortie.domaines},
            # Verdict des garde-fous, en version courte : un préréglage peut être
            # efficace et dangereux, les deux informations doivent coexister.
            "diagnostic": resume_court(sortie.diagnostic),
        })
    return {"horodatage": contexte.horodatage, "contexte": contexte.en_dict(),
            "comparaison": resultats}


def catalogue_complet() -> dict[str, Any]:
    """Catalogue complet (leviers, familles, domaines) pour l'interface."""
    return {
        "parametres": catalogue_parametres(),
        "domaines": catalogue_domaines(),
        "familles": [{"cle": cle, **meta} for cle, meta in FAMILLES.items()],
    }


if __name__ == "__main__":  # pragma: no cover - outil de ligne de commande
    import argparse

    analyseur = argparse.ArgumentParser(description="Simulateur interactif — ligne de commande")
    analyseur.add_argument("--preset", default=None, help="clé d'un préréglage")
    analyseur.add_argument("--levier", action="append", default=[],
                           help="levier=valeur (répétable), ex. --levier effort_defense_pct_pib=3.5")
    analyseur.add_argument("--json", action="store_true")
    arguments = analyseur.parse_args()

    jeu: dict[str, float] = {}
    if arguments.preset:
        jeu.update(PRESETS[arguments.preset]["parametres"])
    for brut in arguments.levier:
        cle, _, valeur = brut.partition("=")
        if cle not in LEVIERS:
            raise SystemExit(f"levier inconnu : {cle}")
        jeu[cle] = float(valeur)

    sortie = simuler(jeu)
    if arguments.json:
        print(json.dumps(sortie.en_dict(), ensure_ascii=False, indent=2))
    else:
        print(f"Contexte : {sortie.contexte['mode']} — {sortie.horodatage}")
        for resultat in sortie.etapes:
            print(
                f"  Année {resultat['annee']} : déficit {resultat['ratio_deficit_pib']:.2f} % PIB | "
                f"dette {resultat['ratio_dette_pib']:.1f} % | OAT {resultat['taux_oat_pct']:.2f} % | "
                f"tension {resultat['tension_sociale_locale']:.1f} | "
                f"confiance {resultat['confiance_democratique']:.1f}"
            )
        print("\nDomaines (score 0-100, référence entre parenthèses) :")
        for domaine in sortie.domaines:
            fleche = "▲" if domaine["score"] > domaine["score_reference"] else (
                "▼" if domaine["score"] < domaine["score_reference"] else "="
            )
            print(f"  {fleche} {domaine['libelle']:<38} {domaine['score']:>5.1f} "
                  f"({domaine['score_reference']:.1f})")
