"""
simulateur/conseil.py — Conseiller spécialisé en temps réel (« effet papillon »).

Chaque mouvement de réglage est une **décision** : la position du levier à
l'instant T par rapport à sa position avant le dernier mouvement. Ce module
compare deux exécutions réelles du moteur (toutes choses égales par ailleurs)
et en tire une lecture de conseiller spécialisé, pour **tous** les leviers du
catalogue, dans tous les domaines touchés directement **et par ricochets** :

  1. le mouvement lui-même (formulation humaine : « vous avez monté X de a à b ») ;
  2. la chaîne technique (champ ou ligne budgétaire → médiateurs → domaines) ;
  3. les effets **directs** (thèmes déclarés au catalogue) et les effets
     **par ricochet** (domaines qui bougent sans être déclarés : l'effet
     papillon mesuré par le modèle, pas supposé) ;
  4. les grandeurs macro qui basculent (déficit, dette, OAT, tension…) ;
  5. les garde-fous dont le niveau change, avec la marge restante ;
  6. le journal institutionnel nouveau (« Report forcé sur la taxe foncière »…) ;
  7. une piste de compensation tirée des effets déclarés des autres leviers.

Rien n'est rédigé à la main levier par levier : tout est dérivé du catalogue
(`parametres.py`), du moteur (`moteur_parametrique.py`) et du barème
(`seuils.py`). Le conseil reste donc exact quand le modèle change.
"""

from __future__ import annotations

from typing import Any

from simulateur.bulles import THEMES_DOMAINES, _index_compensateurs
from simulateur.donnees_live import ContexteInstant
from simulateur.moteur_parametrique import simuler
from simulateur.parametres import LEVIERS, TYPE_INTERRUPTEUR
from simulateur.seuils import NIVEAUX

#: Grandeurs de synthèse surveillées par le conseiller : (clé, libellé,
#: unité, sens favorable (+1 = hausse favorable, -1 = baisse favorable),
#: précision d'affichage).
GRANDEURS: tuple[tuple[str, str, str, int, int], ...] = (
    ("deficit_final_pct", "Déficit final", "% PIB", -1, 2),
    ("dette_finale_pct", "Dette finale", "% PIB", -1, 1),
    ("taux_oat_final", "Taux OAT 10 ans", "%", -1, 2),
    ("spread_final_bps", "Spread OAT-Bund", "bps", -1, 0),
    ("tension_finale", "Tension sociale", "/100", -1, 1),
    ("confiance_finale", "Confiance démocratique", "/100", 1, 1),
    ("risque_censure_final_pct", "Risque de censure", "%", -1, 0),
    ("croissance_supplementaire_pts", "Croissance cumulée vs référence", "pt", 1, 2),
    ("score_moyen_domaines", "Score moyen des 20 domaines", "/100", 1, 1),
)

#: Seuil (pt de score domaine) au-dessous duquel un mouvement est tu.
SEUIL_DOMAINE = 0.15

#: Seuil au-dessous duquel une grandeur macro est tue.
SEUIL_GRANDEUR_FACTOR = 0.5

#: Chiffres clefs des sources officielles qui ancrent le calcul (traçabilité :
#: chaque coût/gain affiché descend de ces valeurs de référence).
SOURCES_CLES: tuple[str, ...] = (
    "pib_nominal_mde", "deficit_public_pct_pib", "dette_publique_pct_pib",
    "taux_oat_10ans", "taux_bund_10ans", "spread_oat_bund_bps",
    "taux_bce_depot", "inflation_pct", "inflation_zone_euro_pct",
    "chomage_pct", "brent_usd", "eur_usd",
)


def _format(valeur: float, precision: int) -> str:
    texte = f"{valeur:,.{precision}f}"
    return texte.replace(",", " ").replace(".", ",")


def _format_signe(valeur: float, precision: int) -> str:
    """Même convention française que `_format`, avec le signe explicite."""
    texte = f"{valeur:+,.{precision}f}"
    return texte.replace(",", " ").replace(".", ",")


def _formuler_mouvement(levier, avant: float, apres: float) -> str:
    """Phrase humaine décrivant la décision (le mouvement du réglage)."""
    if levier is None:
        return f"réglage {_format(avant, 2)} → {_format(apres, 2)}"
    if levier.type == TYPE_INTERRUPTEUR:
        if apres >= 0.5 and avant < 0.5:
            return f"vous avez **activé** « {levier.libelle} »"
        if apres < 0.5 and avant >= 0.5:
            return f"vous avez **désactivé** « {levier.libelle} »"
        return f"« {levier.libelle} » reste {('activé' if apres >= 0.5 else 'désactivé')}"
    delta = apres - avant
    verbe = "monté" if delta > 0 else ("baissé" if delta < 0 else "maintenu")
    unite = "" if levier.unite in ("bool", "") else f" {levier.unite}"
    if abs(delta) < 1e-9:
        return (f"vous avez maintenu « {levier.libelle} » à "
                f"{_format(apres, levier.precision)}{unite}")
    return (f"vous avez {verbe} « {levier.libelle} » de "
            f"{_format(avant, levier.precision)}{unite} à "
            f"{_format(apres, levier.precision)}{unite} "
            f"({_format_signe(delta, levier.precision)}{unite})")


def _domaines_directs(levier) -> set[str]:
    """Domaines déclarés (effets_directs → thèmes → domaines du modèle)."""
    directs: set[str] = set()
    if levier is None:
        return directs
    for theme in (levier.effets_directs or {}):
        for domaine in THEMES_DOMAINES.get(theme, (theme,)):
            directs.add(domaine)
    return directs


def _compensations_possibles(domaine_degrade: str, parametres: dict[str, float]) -> list[dict[str, Any]]:
    """Leviers non actifs dont l'effet déclaré soutient le domaine dégradé."""
    index = _index_compensateurs()
    propositions: list[dict[str, Any]] = []
    for entree in index.get(domaine_degrade, []):
        cle = entree["cle"]
        levier = LEVIERS.get(cle)
        if levier is None:
            continue
        if abs(parametres.get(cle, levier.defaut) - levier.defaut) > 1e-9:
            continue  # déjà actionné : inutile de le proposer
        if any(p["cle"] == cle for p in propositions):
            continue
        propositions.append({
            "cle": cle,
            "libelle": levier.libelle,
            "coefficient": entree.get("coefficient", 0.0),
        })
        if len(propositions) >= 3:
            break
    return propositions


def conseil_mouvement(
    parametres: dict[str, float],
    cle: str,
    valeur_avant: float,
    valeur_apres: float,
    contexte: ContexteInstant,
    horizon: int = 5,
) -> dict[str, Any]:
    """Le conseil complet pour un mouvement de réglage, dans l'état courant.

    `parametres` est l'état **après** le mouvement (tous leviers confondus) ;
    le moteur est rejoué une fois avec le levier à `valeur_avant` et une fois
    à `valeur_apres`, toutes choses égales par ailleurs : la différence est
    donc exactement celle de la décision, y compris ses ricochets.
    """
    levier = LEVIERS.get(cle)
    params_avant = dict(parametres)
    params_avant[cle] = valeur_avant
    params_apres = dict(parametres)
    params_apres[cle] = valeur_apres

    sortie_avant = simuler(params_avant, contexte, avec_impacts=False, horizon=horizon)
    sortie_apres = simuler(params_apres, contexte, avec_impacts=False, horizon=horizon)

    # ── Domaines : directs vs ricochets ────────────────────────────────────
    directs = _domaines_directs(levier)
    scores_avant = {d["cle"]: d["score"] for d in sortie_avant.domaines}
    domaines: list[dict[str, Any]] = []
    for domaine in sortie_apres.domaines:
        delta = round(domaine["score"] - scores_avant.get(domaine["cle"], 50.0), 2)
        if abs(delta) < SEUIL_DOMAINE:
            continue
        domaines.append({
            "cle": domaine["cle"],
            "libelle": domaine["libelle"],
            "delta": delta,
            "direct": domaine["cle"] in directs,
            "favorable": delta > 0,
            "phrase": (f"{domaine['libelle']} {'amélioré' if delta > 0 else 'dégradé'} "
                       f"de {_format(abs(delta), 1)} pt"
                       + ("" if domaine["cle"] in directs else " (ricochet)")),
        })
    domaines.sort(key=lambda d: -abs(d["delta"]))
    domaines = domaines[:8]
    # Invariant : les ricochets sont exactement le sous-ensemble non déclaré
    # des domaines rendus — l'interface peut compter sur cette égalité.
    ricochets = [d for d in domaines if not d["direct"]]

    # ── Grandeurs macro ────────────────────────────────────────────────────
    grandeurs: list[dict[str, Any]] = []
    for cle_syn, libelle, unite, sens, precision in GRANDEURS:
        avant = sortie_avant.synthese.get(cle_syn)
        apres = sortie_apres.synthese.get(cle_syn)
        if avant is None or apres is None:
            continue
        delta = apres - avant
        if abs(delta) < (10 ** -precision) * SEUIL_GRANDEUR_FACTOR:
            continue
        grandeurs.append({
            "cle": cle_syn,
            "libelle": libelle,
            "unite": unite,
            "avant": round(avant, precision + 1),
            "apres": round(apres, precision + 1),
            "delta": round(delta, precision + 1),
            "precision": precision,
            "favorable": sens * delta > 0,
        })

    # ── Budget réel du mouvement : coût / gain en Md€ (année finale) ──────
    budget = {
        "recettes_delta_mde": round(
            sortie_apres.synthese.get("recettes_nouvelles_mde", 0.0)
            - sortie_avant.synthese.get("recettes_nouvelles_mde", 0.0), 2),
        "depenses_delta_mde": round(
            sortie_apres.synthese.get("depenses_nouvelles_mde", 0.0)
            - sortie_avant.synthese.get("depenses_nouvelles_mde", 0.0), 2),
        "solde_delta_mde": round(
            sortie_apres.synthese.get("solde_mesures_mde", 0.0)
            - sortie_avant.synthese.get("solde_mesures_mde", 0.0), 2),
        "charge_dette_delta_mde": round(
            sortie_apres.synthese.get("charge_dette_finale_mde", 0.0)
            - sortie_avant.synthese.get("charge_dette_finale_mde", 0.0), 2),
        "deficit_delta_pt_pib": round(
            sortie_apres.synthese.get("deficit_final_pct", 0.0)
            - sortie_avant.synthese.get("deficit_final_pct", 0.0), 3),
        "horizon": horizon,
    }

    # ── Traçabilité : chiffres clefs des sources officielles ───────────────
    contexte_dict = contexte.en_dict()
    provenance = contexte_dict.get("provenance", {})
    sources = [
        {"cle": cle,
         "valeur": contexte_dict.get(cle),
         **{champ: provenance[cle].get(champ)
            for champ in ("libelle", "unite", "periode", "source", "url", "statut")}}
        for cle in SOURCES_CLES if cle in provenance
    ]

    # ── Garde-fous dont le niveau change ───────────────────────────────────
    rang = {niveau: index for index, niveau in enumerate(NIVEAUX)}
    ind_avant = {e["cle"]: e for e in sortie_avant.diagnostic["indicateurs"]}
    garde_fous: list[dict[str, Any]] = []
    for ecart in sortie_apres.diagnostic["indicateurs"]:
        precedent = ind_avant.get(ecart["cle"])
        if precedent is None:
            continue
        if precedent["niveau"] != ecart["niveau"]:
            aggrave = rang.get(ecart["niveau"], 0) > rang.get(precedent["niveau"], 0)
            garde_fous.append({
                "cle": ecart["cle"],
                "libelle": ecart["libelle"],
                "strate": ecart["strate"],
                "niveau_avant": precedent["niveau"],
                "niveau_apres": ecart["niveau"],
                "valeur": ecart["valeur_texte"],
                "message": ecart["message"],
                "aggrave": aggrave,
            })
    garde_fous.sort(key=lambda g: -rang.get(g["niveau_apres"], 0))

    # ── Journal institutionnel nouveau ─────────────────────────────────────
    journal_avant = [c for etape in sortie_avant.etapes for c in etape["commentaires"]]
    journal_apres = [c for etape in sortie_apres.etapes for c in etape["commentaires"]]
    ensemble_avant = set(journal_avant)
    journal_nouveau: list[str] = []
    for message in journal_apres:
        if message not in ensemble_avant and message not in journal_nouveau:
            journal_nouveau.append(message)

    # ── Lecture du conseiller ──────────────────────────────────────────────
    mouvements = _formuler_mouvement(levier, valeur_avant, valeur_apres)
    phrases: list[str] = [mouvements.replace("**", "") + "."]
    if abs(budget["solde_delta_mde"]) >= 0.01:
        if budget["solde_delta_mde"] >= 0:
            phrases.append(f"Gain budgétaire net : {_format(budget['solde_delta_mde'], 2)} Md€ "
                           f"par an (recettes {_format_signe(budget['recettes_delta_mde'], 2)}, "
                           f"dépenses {_format_signe(budget['depenses_delta_mde'], 2)}).")
        else:
            phrases.append(f"Coût budgétaire net : {_format(abs(budget['solde_delta_mde']), 2)} Md€ "
                           f"par an (recettes {_format_signe(budget['recettes_delta_mde'], 2)}, "
                           f"dépenses {_format_signe(budget['depenses_delta_mde'], 2)}).")
    gains = [d for d in domaines if d["favorable"]]
    pertes = [d for d in domaines if not d["favorable"]]
    if gains:
        phrases.append("Bénéfice principal : " + gains[0]["phrase"] + ".")
    if pertes:
        phrases.append("Coût principal : " + pertes[0]["phrase"] + ".")
    if ricochets:
        premiers = ", ".join(f"{r['libelle']} ({_format_signe(r['delta'], 1)})"
                             for r in ricochets[:3])
        phrases.append("Par ricochet, loin du réglage lui-même, le modèle fait bouger : "
                       + premiers + " — c'est l'effet papillon mesuré par le moteur.")
    for garde in garde_fous[:2]:
        verbe = "dégrade" if garde["aggrave"] else "améliore"
        phrases.append(f"Le garde-fou « {garde['libelle']} » passe de "
                       f"{garde['niveau_avant']} à {garde['niveau_apres']} ({verbe}) : "
                       f"{garde['message']}")
    if journal_nouveau:
        phrases.append("Signal institutionnel nouveau : « " + journal_nouveau[-1] + " »")

    pire = pertes[0]["cle"] if pertes else None
    compensations: list[dict[str, Any]] = []
    if pire:
        compensations = _compensations_possibles(pire, parametres)
        if compensations:
            noms = ", ".join(f"« {c['libelle']} »" for c in compensations)
            phrases.append(f"Piste de compensation pour {pertes[0]['libelle'].lower()} : "
                           f"{noms} (effets déclarés au catalogue).")

    # Verdict global du mouvement : pire niveau atteint par un garde-fou changé,
    # sinon lecture des domaines (pertes → vigilance/risque selon leur nombre).
    if garde_fous:
        verdict_niveau = max((g["niveau_apres"] for g in garde_fous),
                             key=lambda n: rang.get(n, 0))
    elif len(pertes) >= 3:
        verdict_niveau = "risque"
    elif pertes:
        verdict_niveau = "vigilance"
    elif domaines or grandeurs:
        verdict_niveau = "favorable"
    else:
        verdict_niveau = "inconnu"

    return {
        "cle": cle,
        "libelle": levier.libelle if levier else cle,
        "famille": levier.famille if levier else "",
        "mouvement": {
            "avant": valeur_avant,
            "apres": valeur_apres,
            "phrase": mouvements,
            "type": levier.type if levier else "curseur",
            "unite": levier.unite if levier else "",
        },
        "verdict_niveau": verdict_niveau,
        "domaines": domaines,
        "ricochets": ricochets,
        "grandeurs": grandeurs,
        "garde_fous": garde_fous[:6],
        "journal": journal_nouveau[:6],
        "compensations": compensations,
        "budget": budget,
        "sources": sources,
        "lecture": " ".join(phrases),
    }
