"""
simulateur/bulles.py — Bulles explicatives par levier.

Chaque levier du catalogue (93 aujourd'hui) possède une **bulle** : une fiche
calculée qui répond à trois questions, dans cet ordre :

  1. **Que déclenche ce réglage ?** — la chaîne technique réelle, lue dans le
     code : ligne budgétaire ou champ du moteur → médiateurs émis (Md€, points,
     milliers…) → indicateurs des 74 spécifications qui les consomment →
     domaines notés 0-100. Les maillons qu'aucune formule ne consomme sont
     signalés explicitement plutôt que passés sous silence.
  2. **Quelles répercussions, à quelles amplitudes ?** — pour chaque borne du
     réglage (et pour un pas au-delà du défaut), une simulation réelle compare
     le réglage isolé à la trajectoire de référence : score des 20 domaines,
     écart des indicateurs, niveau des 33 garde-fous (tolérable / vigilance /
     risqué / hors-sol), risque population, strates 1 → 5 et journal
     institutionnel (« Alerte censure », « Report forcé sur la taxe foncière »,
     « Sortie de la PDE »…).
  3. **En quoi est-ce une opportunité ou un désagrément ?** — une lecture
     guidée : gains, pertes, points à surveiller, strates alertées et pistes de
     compensation tirées des *effets déclarés* des autres leviers.

Aucune de ces trois couches n'est rédigée à la main levier par levier : tout
est dérivé du catalogue (`parametres.py`), des spécifications d'indicateurs
(`domaines.py`), du moteur (`moteur_parametrique.py`) et du barème
(`seuils.py`). Une bulle reste donc exacte quand un levier, un coefficient ou
un seuil change.

Conventions de mesure
---------------------
* **Réglage isolé** : une seule clé est modifiée, tous les autres leviers
  restent à leur valeur neutre ; la comparaison se fait toujours à la
  trajectoire de référence du modèle (score 50 = aucun effet).
* **Plein régime** : les montants annoncés par la chaîne technique sont ceux de
  la 5ᵉ année (montée en charge achevée).
* **Honnêteté** : quand l'effet d'un levier est porté par l'état interne du
  moteur sans être relayé par une formule d'indicateur, la bulle le dit
  (« maillon non relayé ») et affiche les répercussions institutionnelles
  effectivement journalisées, plutôt que d'inventer un score.
"""

from __future__ import annotations

from collections.abc import Iterable
from typing import Any

from simulateur.domaines import (
    DOMAINES_PAR_CLE,
    LIGNES,
    SPECS,
    UNITES_CHAMPS,
    construire_flux,
)
from simulateur.donnees_live import construire_contexte
from simulateur.moteur_parametrique import SortieSimulation, simuler
from simulateur.parametres import (
    FAMILLES,
    LEVIERS,
    TYPE_INTERRUPTEUR,
)
from simulateur.seuils import LIBELLES_NIVEAUX, LIBELLES_STRATES, NIVEAUX

__all__ = [
    "SEUIL_MOUVEMENT",
    "THEMES_DOMAINES",
    "strates_theme",
    "consommateurs",
    "emissions_levier",
    "champ_moteur",
    "mesures_levier",
    "bulle_levier",
    "bulles_catalogue",
    "phrase_lecture",
    "DETAILS",
]

#: En deçà de cet écart (points de score 0-100), un domaine est considéré comme
#: non touché par le réglage : le bruit d'arrondi du modèle est de cet ordre.
SEUIL_MOUVEMENT = 0.2

#: Ordre de gravité des niveaux de garde-fou (pour détecter une aggravation).
_RANG_NIVEAUX: dict[str, int] = {niveau: rang for rang, niveau in enumerate(NIVEAUX)}

#: Thèmes déclarés dans `Levier.effets_directs` → domaines notés qu'ils nourrissent.
#: Un thème peut alimenter plusieurs domaines (les inégalités pèsent à la fois sur
#: la pauvreté et sur le pouvoir d'achat) ; certains thèmes sont transverses et
#: n'ont pas de domaine dédié (l'inflation, les marchés, le climat…).
THEMES_DOMAINES: dict[str, tuple[str, ...]] = {
    # Thèmes portant le nom d'un domaine.
    "pauvrete": ("pauvrete",),
    "emploi": ("emploi",),
    "pouvoir_achat": ("pouvoir_achat",),
    "budget": ("budget", "fiscalite"),
    "industrie": ("industrie",),
    "sante": ("sante",),
    "democratie": ("democratie",),
    "education": ("education",),
    "logement": ("logement",),
    "defense": ("defense",),
    "securite": ("securite",),
    "resilience": ("resilience",),
    "numerique": ("numerique",),
    "agriculture": ("agriculture",),
    # Thèmes transverses rattachés aux domaines qu'ils font bouger.
    "inégalités": ("pauvrete", "pouvoir_achat"),
    "inegalites": ("pauvrete", "pouvoir_achat"),
    "confiance": ("democratie",),
    "cohesion": ("social",),
    "territoires": ("logement", "economie"),
    "inflation": ("pouvoir_achat", "economie"),
    "energie": ("energie_climat",),
    "souverainete": ("industrie", "defense", "numerique"),
    "croissance": ("economie",),
    "climat": ("energie_climat",),
    "investissement": ("economie", "industrie"),
    "services_publics": ("logement", "education", "sante"),
    "attractivite": ("economie", "industrie"),
    "tension_sociale": ("social", "democratie"),
    "consommation": ("economie", "pouvoir_achat"),
    "demographie": ("social", "sante"),
    "marches": ("budget",),
    "geopolitique": ("defense", "europe_monde"),
    "solidarite": ("social", "pauvrete"),
    "commerce_exterieur": ("economie", "industrie"),
    "emissions": ("energie_climat",),
    "innovation": ("recherche", "industrie"),
    "stabilite_gouvernementale": ("democratie",),
    "europe": ("europe_monde",),
    "verdissement": ("energie_climat",),
    "justice": ("securite",),
    "participation": ("democratie",),
    "international": ("europe_monde",),
    "change": ("economie", "pouvoir_achat"),
    "dette": ("budget",),
}

#: Thèmes → échelons (1 local … 5 géopolitique) que le thème traverse.
#: Sert à situer chaque interaction dans la cascade des 5 strates.
THEMES_STRATES: dict[str, tuple[int, ...]] = {
    "territoires": (1, 2),
    "services_publics": (1, 2),
    "logement": (1, 2),
    "solidarite": (1, 2),
    "budget": (2, 3, 4),
    "dette": (2, 3, 4),
    "marches": (2, 4),
    "inflation": (2, 4),
    "change": (2, 4),
    "commerce_exterieur": (2, 4),
    "europe": (3,),
    "international": (4, 5),
    "geopolitique": (4, 5),
    "souverainete": (2, 5),
    "defense": (2, 5),
    "industrie": (2, 5),
    "numerique": (2, 5),
    "energie": (2, 4),
    "climat": (2, 4),
    "emissions": (2, 4),
    "verdissement": (2, 4),
    "resilience": (2, 4),
}

#: Suffixes d'unité utilisés par les médiateurs de `domaines.py`.
_SUFFIXES: tuple[tuple[str, str], ...] = (
    ("_milliers", "milliers"),
    ("_mde", "Md€"),
    ("_pts", "points"),
    ("_eur_t", "€/tCO2"),
    ("_nb", "nombre"),
    ("_h", "heures"),
    ("_pct", "%"),
)


def strates_theme(theme: str) -> tuple[int, ...]:
    """Échelons traversés par un thème déclaré (défaut : échelon national)."""
    return THEMES_STRATES.get(theme, (2,))


def _unite_mediateur(nom: str) -> str:
    for suffixe, unite in _SUFFIXES:
        if nom.endswith(suffixe):
            return unite
    return ""


def _base_mediateur(nom: str) -> str:
    """« transferts_sociaux_pts » → « transferts_sociaux » (pour les rapprochements)."""
    for suffixe, _ in _SUFFIXES:
        if nom.endswith(suffixe):
            return nom[: -len(suffixe)]
    return nom


# ────────────────────────────────────────────────────────────────────────────
# 1. Chaîne technique : que consomme chaque médiateur ?
# ────────────────────────────────────────────────────────────────────────────

_INDEX_CONSOMMATEURS: dict[str, list[dict[str, Any]]] | None = None


def _index_consommateurs() -> dict[str, list[dict[str, Any]]]:
    """Index (mémoïsé) médiateur → indicateurs qui le lisent, lu dans les SPECS."""
    global _INDEX_CONSOMMATEURS
    if _INDEX_CONSOMMATEURS is not None:
        return _INDEX_CONSOMMATEURS
    index: dict[str, list[dict[str, Any]]] = {}
    for spec in SPECS:
        domaine = DOMAINES_PAR_CLE.get(spec.domaine)
        for terme, coefficient in spec.termes:
            index.setdefault(terme, []).append({
                "indicateur": spec.cle,
                "libelle": spec.libelle,
                "domaine": spec.domaine,
                "domaine_libelle": domaine.libelle if domaine else spec.domaine,
                "coefficient": coefficient,
            })
    _INDEX_CONSOMMATEURS = index
    return index


def consommateurs(mediateur: str) -> list[dict[str, Any]]:
    """Indicateurs qui lisent un médiateur (correspondance exacte puis par base).

    Les flux sont libellés avec leur unité (`_mde`, `_pts`, `_milliers`) tandis
    que les formules d'indicateurs peuvent viser l'une ou l'autre échelle : on
    tente d'abord le nom exact, puis le nom débarrassé de son suffixe.
    """
    index = _index_consommateurs()
    trouves = index.get(mediateur)
    if trouves is None:
        trouves = index.get(_base_mediateur(mediateur), [])
    vus: set[str] = set()
    uniques: list[dict[str, Any]] = []
    for consommateur in trouves:
        if consommateur["indicateur"] in vus:
            continue
        vus.add(consommateur["indicateur"])
        uniques.append(dict(consommateur))
    return uniques


def _domaines_consommes(mediateur: str) -> list[str]:
    domaines: list[str] = []
    for consommateur in consommateurs(mediateur):
        if consommateur["domaine"] not in domaines:
            domaines.append(consommateur["domaine"])
    return domaines


#: Médiateurs agrégés reconstruits par `construire_flux` : utiles à afficher,
#: mais dérivés — on les distingue des émissions directes du levier.
AGREGATS_DERIVES: tuple[str, ...] = (
    "recettes_nouvelles_mde", "depenses_nouvelles_mde", "solde_budgetaire_mde",
    "investissement_public_mde", "transferts_menages_mde", "transferts_sociaux_mde",
    "regalien_mde", "souverainete_mde", "baisse_prelevements_menages_mde",
    "baisse_tva_energie_mde", "reformes_democratiques",
)

#: Médias internes au harnais : jamais présentés comme des interactions.
_IGNORES: tuple[str, ...] = ("effort_defense_ecart_pts", "choc_semi", "cyberattaque_pts", "mobilisation_pts")


def emissions_levier(cle: str, valeur: float, annee_index: int = 4) -> list[dict[str, Any]]:
    """Médiateurs réellement émis par un levier à une valeur donnée.

    La liste est obtenue en comparant deux constructions de flux (levier neutre
    vs levier réglé) à **plein régime** : rien n'est déduit de la documentation,
    tout vient du code qui alimente les formules.
    """
    levier = LEVIERS[cle]
    neutre = construire_flux({}, annee_index)
    regle = construire_flux({cle: valeur}, annee_index)
    direct = None
    if levier.ligne and levier.ligne in LIGNES:
        direct = LIGNES[levier.ligne]
    elif cle in UNITES_CHAMPS:
        direct = UNITES_CHAMPS[cle]

    emissions: list[dict[str, Any]] = []
    for nom, montant in regle.items():
        if nom.startswith("levier:") or nom in _IGNORES:
            continue
        ecart = montant - neutre.get(nom, 0.0)
        if abs(ecart) < 1e-9:
            continue
        base = _base_mediateur(nom)
        est_direct = bool(direct) and base == direct
        lecteurs = consommateurs(nom)
        est_agregat = nom in AGREGATS_DERIVES
        emissions.append({
            "mediateur": nom,
            "unite": _unite_mediateur(nom),
            "montant": round(ecart, 4),
            "sens": "hausse" if ecart > 0 else "baisse",
            "direct": est_direct,
            "agregat": est_agregat,
            "alias": not est_direct and not est_agregat,
            "relaye": bool(lecteurs),
            "consommateurs": lecteurs,
            "domaines": _domaines_consommes(nom),
            "relais": "formules d'indicateurs" if lecteurs else None,
        })

    # Un médiateur peut n'être lu par aucune formule tout en atteignant les
    # indicateurs par une autre échelle du même nom (`_mde` vs `_pts`), ou par
    # l'agrégat budgétaire (recettes / dépenses nouvelles) auquel le levier
    # contribue : on le dit, plutôt que de crier à l'orphelin.
    agregats_relayes = sorted({
        emission["mediateur"] for emission in emissions
        if emission["agregat"] and emission["relaye"]
    })
    for emission in emissions:
        if emission["relaye"]:
            continue
        base = _base_mediateur(emission["mediateur"])
        echelles = [
            base + suffixe for suffixe, _ in _SUFFIXES
            if base + suffixe != emission["mediateur"]
            and consommateurs(base + suffixe)
        ]
        if echelles:
            emission["relais"] = "autre échelle du même médiateur : " + ", ".join(echelles)
            emission["echelles_relayees"] = echelles
        elif agregats_relayes:
            emission["relais"] = "agrégat budgétaire : " + ", ".join(agregats_relayes)

    emissions.sort(key=lambda emission: (
        not emission["direct"],
        not emission["agregat"],
        emission["mediateur"],
    ))
    return emissions


def champ_moteur(cle: str) -> dict[str, Any] | None:
    """Champ de `DecisionPolitique` alimenté par le levier, s'il existe.

    L'effet correspondant vit dans l'état interne du moteur (strates 1 à 5) et
    n'est pas relu par une formule d'indicateur : on le présente séparément.
    """
    levier = LEVIERS[cle]
    if not levier.champ:
        return None
    return {
        "champ": levier.champ,
        "facteur": levier.facteur,
        "note": ("Champ piloté directement par le moteur : l'effet est porté par "
                 "l'état interne des strates 1 à 5 et n'est pas relu par une "
                 "formule d'indicateur. Les répercussions mesurées (scores, "
                 "garde-fous) et journalisées figurent ci-dessous."),
    }


def maillons_non_relayes(emissions: Iterable[dict[str, Any]]) -> list[dict[str, Any]]:
    """Médiateurs émis qui n'atteignent les indicateurs par aucun chemin connu."""
    return [{
        "mediateur": emission["mediateur"],
        "unite": emission["unite"],
        "montant": emission["montant"],
        "note": emission.get("note", (
            "Émis par le levier mais lu par aucune des 74 formules d'indicateurs, "
            "et sans relais connu (ni autre échelle, ni agrégat budgétaire) : la "
            "répercussion n'apparaît donc pas dans les 20 scores de domaine."
        )),
    } for emission in emissions if not emission["relaye"] and not emission.get("relais")]


# ────────────────────────────────────────────────────────────────────────────
# 2. Mesure : ce que le réglage change réellement, borne par borne
# ────────────────────────────────────────────────────────────────────────────

def _valeurs_de_mesure(levier) -> list[dict[str, Any]]:
    """Valeurs testées : les bornes du réglage, plus un pas au-delà du défaut."""
    if levier.type == TYPE_INTERRUPTEUR:
        return [
            {"nom": "désactivé", "valeur": 0.0, "borne": "basse"},
            {"nom": "activé", "valeur": 1.0, "borne": "haute"},
        ]
    minimum, maximum = levier.minimum, levier.maximum
    if minimum is None or maximum is None:
        minimum = 0.0 if minimum is None else minimum
        maximum = 1.0 if maximum is None else maximum
    valeurs = [
        {"nom": f"borne basse ({minimum:g} {levier.unite})", "valeur": minimum, "borne": "basse"},
        {"nom": f"borne haute ({maximum:g} {levier.unite})", "valeur": maximum, "borne": "haute"},
    ]
    pas = levier.pas
    if pas:
        suivant = levier.defaut + pas
        if minimum - 1e-9 <= suivant <= maximum + 1e-9 and abs(suivant - levier.defaut) > 1e-9:
            valeurs.append({
                "nom": f"un pas au-dessus du défaut ({suivant:g} {levier.unite})",
                "valeur": suivant,
                "borne": "pas",
            })
    # Dédoublonnage (une cible peut avoir un défaut égal à une borne).
    vus: set[float] = set()
    uniques: list[dict[str, Any]] = []
    for entree in valeurs:
        marqueur = round(entree["valeur"], 6)
        if marqueur in vus:
            continue
        vus.add(marqueur)
        uniques.append(entree)
    return uniques


def _index_reference(reference: SortieSimulation) -> dict[str, Any]:
    indicateurs: dict[tuple[str, str], float] = {}
    for domaine in reference.domaines:
        for indicateur in domaine["indicateurs"]:
            indicateurs[(domaine["cle"], indicateur["cle"])] = indicateur["valeur_finale"]
    return {
        "domaines": {d["cle"]: d for d in reference.domaines},
        "indicateurs": indicateurs,
        "journal": set(reference.journal),
        "diagnostic": reference.diagnostic,
        "niveaux": {ind["cle"]: ind.get("niveau") for ind in reference.diagnostic.get("indicateurs", [])},
    }


def _seuils(sortie: SortieSimulation, reference: dict[str, Any]) -> dict[str, Any]:
    """Lecture du barème : niveau global, risque population, strates, alertes."""
    diagnostic = sortie.diagnostic or {}
    ref_diagnostic = reference.get("diagnostic") or {}
    population = diagnostic.get("population") or {}
    ref_population = ref_diagnostic.get("population") or {}

    alertes: list[dict[str, Any]] = []
    ref_niveaux = reference.get("niveaux") or {}
    for indicateur in diagnostic.get("indicateurs", []):
        niveau = indicateur.get("niveau")
        if niveau not in _RANG_NIVEAUX:
            continue
        rang = _RANG_NIVEAUX[niveau]
        rang_ref = _RANG_NIVEAUX.get(ref_niveaux.get(indicateur.get("cle")), -1)
        if rang < _RANG_NIVEAUX["vigilance"] or rang <= rang_ref:
            continue
        alertes.append({
            "cle": indicateur.get("cle"),
            "libelle": indicateur.get("libelle"),
            "strate": indicateur.get("strate"),
            "strate_libelle": LIBELLES_STRATES.get(indicateur.get("strate")),
            "niveau": niveau,
            "niveau_libelle": LIBELLES_NIVEAUX.get(niveau, niveau),
            "valeur_texte": indicateur.get("valeur_texte"),
            "unite": indicateur.get("unite"),
            "message": indicateur.get("message"),
        })
    alertes.sort(key=lambda alerte: -_RANG_NIVEAUX.get(alerte["niveau"], -1))

    strates: list[dict[str, Any]] = []
    ref_strates = {strate.get("strate"): strate for strate in ref_diagnostic.get("strates", [])}
    for strate in diagnostic.get("strates", []):
        numero = strate.get("strate")
        niveau = strate.get("niveau")
        ref_niveau = (ref_strates.get(numero) or {}).get("niveau")
        strates.append({
            "strate": numero,
            "libelle": strate.get("libelle") or LIBELLES_STRATES.get(numero),
            "niveau": niveau,
            "niveau_libelle": LIBELLES_NIVEAUX.get(niveau, niveau),
            "reference": ref_niveau,
            "reference_libelle": LIBELLES_NIVEAUX.get(ref_niveau, ref_niveau),
            "aggrave": _RANG_NIVEAUX.get(niveau, -1) > _RANG_NIVEAUX.get(ref_niveau, -1),
        })
    return {
        "niveau_global": diagnostic.get("niveau_global"),
        "niveau_global_libelle": LIBELLES_NIVEAUX.get(diagnostic.get("niveau_global"), diagnostic.get("niveau_global")),
        "verdict": diagnostic.get("verdict"),
        "population": {
            "risque": population.get("valeur"),
            "niveau": population.get("niveau"),
            "niveau_libelle": LIBELLES_NIVEAUX.get(population.get("niveau"), population.get("niveau")),
            "reference": ref_population.get("valeur"),
            "message": population.get("message"),
        },
        "strates": strates,
        "alertes": alertes,
    }


def _journal_nouveau(sortie: SortieSimulation, reference: dict[str, Any]) -> list[dict[str, Any]]:
    """Lignes de journal apparues par rapport à la trajectoire de référence."""
    vues: set[str] = set()
    lignes: list[dict[str, Any]] = []
    for ligne in sortie.journal:
        if ligne in reference["journal"] or ligne in vues:
            continue
        vues.add(ligne)
        entete, _, texte = ligne.partition("] ")
        if texte and entete.startswith("["):
            entete = entete[1:]
        else:
            entete, texte = "", ligne
        lignes.append({"strate": entete, "texte": texte})
    return lignes


def _mesure(cle: str, entree: dict[str, Any], contexte, reference: SortieSimulation,
            index_reference: dict[str, Any]) -> dict[str, Any]:
    """Une simulation réelle pour une valeur du levier, comparée à la référence."""
    sortie = simuler({cle: entree["valeur"]}, contexte, avec_impacts=False)
    domaines = sorted(
        [{
            "cle": domaine["cle"],
            "libelle": domaine["libelle"],
            "delta": round(domaine["score"] - 50.0, 2),
            "score": round(domaine["score"], 2),
        } for domaine in sortie.domaines],
        key=lambda domaine: -abs(domaine["delta"]),
    )
    indicateurs: list[dict[str, Any]] = []
    for domaine in sortie.domaines:
        for indicateur in domaine["indicateurs"]:
            final = indicateur["valeur_finale"]
            base = index_reference["indicateurs"].get((domaine["cle"], indicateur["cle"]))
            if base is None:
                continue
            ecart = final - base
            if abs(ecart) < 1e-9:
                continue
            indicateurs.append({
                "cle": indicateur["cle"],
                "libelle": indicateur["libelle"],
                "domaine": domaine["cle"],
                "domaine_libelle": domaine["libelle"],
                "unite": indicateur["unite"],
                "valeur_reference": round(base, 3),
                "valeur": round(final, 3),
                "ecart": round(ecart, 3),
                "sens": "hausse" if ecart > 0 else "baisse",
                "favorable": (ecart > 0) == (indicateur.get("sens", 1) >= 0),
            })
    indicateurs.sort(key=lambda indicateur: -abs(indicateur["ecart"]))

    return {
        "nom": entree["nom"],
        "borne": entree["borne"],
        "valeur": entree["valeur"],
        "score_moyen": round(sum(d["score"] for d in domaines) / max(len(domaines), 1), 2),
        "domaines_mouvementes": [d for d in domaines if abs(d["delta"]) >= SEUIL_MOUVEMENT],
        # Les 20 domaines sont renvoyés sans libellé (le catalogue les fournit
        # déjà) : c'est la charge la plus lourde de la bulle.
        "domaines": [{"cle": domaine["cle"], "delta": domaine["delta"]} for domaine in domaines],
        "indicateurs": indicateurs[:12],
        "indicateurs_mouvementes": len(indicateurs),
        "seuils": _seuils(sortie, index_reference),
        "journal": _journal_nouveau(sortie, index_reference),
    }


# ────────────────────────────────────────────────────────────────────────────
# 3. Lecture guidée : opportunités, désagréments, surveillance, compensations
# ────────────────────────────────────────────────────────────────────────────

def _index_compensateurs() -> dict[str, list[dict[str, Any]]]:
    """Domaines → leviers dont les effets déclarés vont dans le bon sens."""
    index: dict[str, list[dict[str, Any]]] = {}
    for cle, levier in LEVIERS.items():
        for theme, coefficient in levier.effets_directs.items():
            if coefficient <= 0:
                continue
            for domaine in THEMES_DOMAINES.get(theme, ()):
                index.setdefault(domaine, []).append({
                    "cle": cle,
                    "libelle": levier.libelle,
                    "famille": FAMILLES.get(levier.famille, {}).get("libelle", levier.famille),
                    "theme": theme,
                    "coefficient": coefficient,
                })
    for domaine, leviers in index.items():
        leviers.sort(key=lambda entree: -entree["coefficient"])
        index[domaine] = leviers[:4]
    return index


_INDEX_COMPENSATEURS: dict[str, list[dict[str, Any]]] | None = None


def _compensations(cle: str, domaines_degrades: Iterable[str]) -> list[dict[str, Any]]:
    global _INDEX_COMPENSATEURS
    if _INDEX_COMPENSATEURS is None:
        _INDEX_COMPENSATEURS = _index_compensateurs()
    pistes: list[dict[str, Any]] = []
    for domaine in domaines_degrades:
        candidats = [entree for entree in _INDEX_COMPENSATEURS.get(domaine, [])
                     if entree["cle"] != cle][:3]
        if candidats:
            pistes.append({
                "domaine": domaine,
                "libelle": DOMAINES_PAR_CLE[domaine].libelle if domaine in DOMAINES_PAR_CLE else domaine,
                "leviers": candidats,
            })
    return pistes


def _effets_declares(levier) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Effets déclarés au catalogue, séparés domaines notés / thèmes transverses."""
    dans_domaines: list[dict[str, Any]] = []
    hors_domaines: list[dict[str, Any]] = []
    for theme, coefficient in sorted(levier.effets_directs.items(), key=lambda item: -abs(item[1])):
        domaines = THEMES_DOMAINES.get(theme, ())
        entree = {
            "theme": theme,
            "coefficient": coefficient,
            "sens": "favorable" if coefficient > 0 else "defavorable",
            "strates": list(strates_theme(theme)),
        }
        if domaines:
            entree["domaines"] = list(domaines)
            entree["domaines_libelles"] = [
                DOMAINES_PAR_CLE[domaine].libelle for domaine in domaines
                if domaine in DOMAINES_PAR_CLE
            ]
            dans_domaines.append(entree)
        else:
            entree["note"] = "Thème transverse : pas de domaine noté dédié dans le harnais actuel."
            hors_domaines.append(entree)
    return dans_domaines, hors_domaines


def _libelle_domaine(cle: str) -> str:
    domaine = DOMAINES_PAR_CLE.get(cle)
    return domaine.libelle if domaine else cle


def _lecture(bulle: dict[str, Any]) -> dict[str, Any]:
    """Transforme les mesures en opportunités, désagréments et points de veille."""
    meilleurs: dict[str, dict[str, Any]] = {}
    pires: dict[str, dict[str, Any]] = {}
    for mesure in bulle["mesures"]:
        for domaine in mesure["domaines"]:
            cle = domaine["cle"]
            if domaine["delta"] > 0:
                if cle not in meilleurs or domaine["delta"] > meilleurs[cle]["delta"]:
                    meilleurs[cle] = dict(domaine) | {"mesure": mesure["nom"], "valeur": mesure["valeur"]}
            elif domaine["delta"] < 0:
                if cle not in pires or domaine["delta"] < pires[cle]["delta"]:
                    pires[cle] = dict(domaine) | {"mesure": mesure["nom"], "valeur": mesure["valeur"]}

    relais: dict[str, set[str]] = {}
    for emission in bulle["emissions"]:
        for domaine in emission["domaines"]:
            relais.setdefault(domaine, set()).add(
                f"{emission['mediateur']} → " + ", ".join(
                    consommateur["libelle"] for consommateur in emission["consommateurs"][:3]
                )
            )

    opportunites: list[dict[str, Any]] = []
    for cle, domaine in sorted(meilleurs.items(), key=lambda item: -item[1]["delta"]):
        if domaine["delta"] < SEUIL_MOUVEMENT:
            continue
        opportunites.append({
            "domaine": cle,
            "libelle": _libelle_domaine(cle),
            "gain": domaine["delta"],
            "mesure": domaine["mesure"],
            "valeur": domaine["valeur"],
            "relais": sorted(relais.get(cle, set()))[:2],
        })
    desagrements: list[dict[str, Any]] = []
    for cle, domaine in sorted(pires.items(), key=lambda item: item[1]["delta"]):
        if abs(domaine["delta"]) < SEUIL_MOUVEMENT:
            continue
        desagrements.append({
            "domaine": cle,
            "libelle": _libelle_domaine(cle),
            "perte": domaine["delta"],
            "mesure": domaine["mesure"],
            "valeur": domaine["valeur"],
            "relais": sorted(relais.get(cle, set()))[:2],
        })

    a_surveiller: list[dict[str, Any]] = []
    for mesure in bulle["mesures"]:
        seuils = mesure["seuils"]
        reference_population = seuils["population"].get("reference")
        risque = seuils["population"].get("risque")
        if isinstance(risque, (int, float)) and isinstance(reference_population, (int, float)):
            if risque - reference_population >= 0.5:
                a_surveiller.append({
                    "type": "population",
                    "mesure": mesure["nom"],
                    "libelle": "Risque population",
                    "avant": reference_population,
                    "apres": risque,
                    "niveau": seuils["population"].get("niveau"),
                    "niveau_libelle": seuils["population"].get("niveau_libelle"),
                    "message": seuils["population"].get("message"),
                })
        for alerte in seuils["alertes"]:
            a_surveiller.append({
                "type": "garde_fou",
                "mesure": mesure["nom"],
                "libelle": alerte["libelle"],
                "strate_libelle": alerte["strate_libelle"],
                "niveau": alerte["niveau"],
                "niveau_libelle": alerte["niveau_libelle"],
                "valeur_texte": alerte["valeur_texte"],
                "unite": alerte["unite"],
                "message": alerte["message"],
            })

    strates: list[dict[str, Any]] = []
    for mesure in bulle["mesures"]:
        for ligne in mesure["journal"]:
            strates.append({"mesure": mesure["nom"], "strate": ligne["strate"], "texte": ligne["texte"]})

    degrades = [domaine["domaine"] for domaine in desagrements]
    return {
        "opportunites": opportunites,
        "desagrements": desagrements,
        "a_surveiller": a_surveiller[:12],
        "strates": strates[:12],
        "compensations": _compensations(bulle["cle"], degrades),
        "maillons_non_relayes": bulle["maillons_non_relayes"],
        "phrase": "",
    }


def phrase_lecture(bulle: dict[str, Any]) -> str:
    """Phrase de synthèse « opportunités / désagréments » d'une bulle."""
    lecture = bulle["lecture"]
    morceaux: list[str] = []
    if bulle.get("sans_effet_mesure"):
        morceaux.append(
            "Aucun des 20 domaines notés ne bouge aux bornes de ce réglage : "
            "les répercussions sont institutionnelles (voir le journal des strates)"
        )
    if lecture["opportunites"]:
        gains = ", ".join(
            f"{entree['libelle']} {entree['gain']:+.1f} pt ({entree['mesure']})"
            for entree in lecture["opportunites"][:3]
        )
        morceaux.append(f"Opportunités : {gains}")
    if lecture["desagrements"]:
        pertes = ", ".join(
            f"{entree['libelle']} {entree['perte']:+.1f} pt ({entree['mesure']})"
            for entree in lecture["desagrements"][:3]
        )
        morceaux.append(f"Désagréments : {pertes}")
    if lecture["a_surveiller"]:
        veille = ", ".join(
            f"{entree['libelle']} ({entree.get('niveau_libelle') or entree.get('strate_libelle') or 'seuil'})"
            for entree in lecture["a_surveiller"][:3]
        )
        morceaux.append(f"À surveiller : {veille}")
    if not morceaux:
        morceaux.append(
            "Aucun des 20 domaines notés ne bouge aux bornes de ce réglage : "
            "voir les maillons non relayés et le journal des strates."
        )
    if lecture["compensations"]:
        domaines = ", ".join(entree["libelle"] for entree in lecture["compensations"][:2])
        morceaux.append(f"Pistes de compensation au catalogue : {domaines}")
    return " · ".join(morceaux)


def _bilan_domaines(bulle: dict[str, Any]) -> list[dict[str, Any]]:
    """Amplitude de mouvement de chaque domaine, toutes mesures confondues."""
    bilan: dict[str, dict[str, Any]] = {}
    for mesure in bulle["mesures"]:
        for domaine in mesure["domaines"]:
            entree = bilan.setdefault(domaine["cle"], {
                "cle": domaine["cle"],
                "libelle": _libelle_domaine(domaine["cle"]),
                "minimum": domaine["delta"],
                "maximum": domaine["delta"],
                "touche": False,
                "mesures": {},
            })
            entree["minimum"] = min(entree["minimum"], domaine["delta"])
            entree["maximum"] = max(entree["maximum"], domaine["delta"])
            entree["mesures"][mesure["nom"]] = domaine["delta"]
            if abs(domaine["delta"]) >= SEUIL_MOUVEMENT:
                entree["touche"] = True
    ordonne = sorted(bilan.values(), key=lambda entree: -max(abs(entree["minimum"]), abs(entree["maximum"])))
    return ordonne


# ────────────────────────────────────────────────────────────────────────────
# 4. Assemblage
# ────────────────────────────────────────────────────────────────────────────

_CACHE: dict[tuple, dict[str, Any]] = {}


def _reference_pour(contexte) -> tuple[SortieSimulation, dict[str, Any]]:
    cle = (contexte.horodatage, contexte.mode)
    memo = _CACHE.get(("reference", cle))
    if memo is None:
        reference = simuler({}, contexte, avec_impacts=False)
        memo = {"sortie": reference, "index": _index_reference(reference)}
        _CACHE[("reference", cle)] = memo
    return memo["sortie"], memo["index"]


def mesures_levier(cle: str, contexte=None) -> list[dict[str, Any]]:
    """Mesures borne par borne d'un levier (réglage isolé, autres leviers neutres)."""
    if cle not in LEVIERS:
        raise ValueError(f"levier inconnu : {cle}")
    contexte = contexte or construire_contexte()
    reference, index = _reference_pour(contexte)
    return [
        _mesure(cle, entree, contexte, reference, index)
        for entree in _valeurs_de_mesure(LEVIERS[cle])
    ]


#: Détails disponibles pour une bulle : « complet » (tout) ou « resume »
#: (sans le détail indicateur par indicateur ni le journal, pour l'aperçu global).
DETAILS: tuple[str, ...] = ("complet", "resume")


def bulle_levier(cle: str, contexte=None, avec_mesure: bool = True,
                 detail: str = "complet") -> dict[str, Any]:
    """Bulle explicative complète d'un levier (voir le module pour la structure)."""
    if cle not in LEVIERS:
        raise ValueError(f"levier inconnu : {cle}")
    if detail not in DETAILS:
        raise ValueError(f"détail inconnu : {detail} (attendu : {', '.join(DETAILS)})")
    contexte = contexte or construire_contexte()
    memo_cle = ("bulle", cle, contexte.horodatage, contexte.mode, avec_mesure, detail)
    if memo_cle in _CACHE:
        return _CACHE[memo_cle]

    levier = LEVIERS[cle]
    famille = FAMILLES.get(levier.famille, {})
    mesures = mesures_levier(cle, contexte) if avec_mesure else []
    emissions: list[dict[str, Any]] = []
    vus: set[str] = set()
    for entree in _valeurs_de_mesure(levier):
        for emission in emissions_levier(cle, entree["valeur"]):
            if emission["mediateur"] in vus:
                continue
            vus.add(emission["mediateur"])
            emissions.append(emission)
    effets_domaines, effets_hors_domaines = _effets_declares(levier)

    bulle: dict[str, Any] = {
        "cle": cle,
        "libelle": levier.libelle,
        "famille": levier.famille,
        "famille_libelle": famille.get("libelle", levier.famille),
        "couleur": famille.get("couleur"),
        "type": levier.type,
        "unite": levier.unite,
        "bornes": {
            "minimum": levier.minimum,
            "maximum": levier.maximum,
            "pas": levier.pas,
            "defaut": levier.defaut,
            "precision": levier.precision,
            "profil": list(levier.profil),
        },
        "description": levier.description,
        "source": levier.source,
        "tags": list(levier.tags),
        "rattachement": {
            "mode": "ligne" if levier.ligne else ("champ" if levier.champ else "aucun"),
            "ligne": levier.ligne,
            "champ": levier.champ,
            "facteur": levier.facteur,
        },
        "emissions": emissions,
        "champ_moteur": champ_moteur(cle),
        "maillons_non_relayes": maillons_non_relayes(emissions),
        "effets_directs": effets_domaines,
        "effets_hors_domaine": effets_hors_domaines,
        "mesures": mesures,
        "avertissement": (
            "Bulle calculée par simulation réelle : réglage isolé (tous les autres "
            "leviers restent neutres), comparé à la trajectoire de référence du "
            "modèle ; montants annoncés à plein régime (5ᵉ année)."
        ),
    }
    bulle["bilan_domaines"] = _bilan_domaines(bulle)
    bulle["sans_effet_mesure"] = not any(
        domaine["touche"] for domaine in bulle["bilan_domaines"]
    )
    bulle["lecture"] = _lecture(bulle)
    bulle["lecture"]["phrase"] = phrase_lecture(bulle)
    if detail == "resume":
        bulle["mesures"] = [
            {k: v for k, v in mesure.items() if k not in ("indicateurs", "journal")}
            for mesure in bulle["mesures"]
        ]
        bulle["lecture"].pop("strates", None)
    _CACHE[memo_cle] = bulle
    return bulle


def bulles_catalogue(contexte=None, cles: Iterable[str] | None = None, avec_mesure: bool = True,
                     progression=None, detail: str = "complet") -> dict[str, Any]:
    """Bulles de tout le catalogue (ou d'une sélection de clés)."""
    contexte = contexte or construire_contexte()
    selection = list(cles) if cles is not None else list(LEVIERS)
    bulles: dict[str, Any] = {}
    for rang, cle in enumerate(selection, start=1):
        bulles[cle] = bulle_levier(cle, contexte, avec_mesure=avec_mesure, detail=detail)
        if progression is not None:
            progression(rang, len(selection), cle)
    return {
        "horodatage": contexte.horodatage,
        "mode": contexte.mode,
        "nombre": len(bulles),
        "seuil_mouvement": SEUIL_MOUVEMENT,
        "bulles": bulles,
        "resume": {
            "leviers_avec_effet_mesure": sum(
                1 for bulle in bulles.values()
                if any(domaine["touche"] for domaine in bulle["bilan_domaines"])
            ),
            "leviers_sans_effet_mesure": [
                cle for cle, bulle in bulles.items() if bulle["sans_effet_mesure"]
            ],
            "leviers_avec_maillon_non_relaye": [
                cle for cle, bulle in bulles.items() if bulle["maillons_non_relayes"]
            ],
            "theme_inconnu": sorted({
                theme for levier in LEVIERS.values() for theme in levier.effets_directs
                if theme not in THEMES_DOMAINES
            }),
        },
    }
