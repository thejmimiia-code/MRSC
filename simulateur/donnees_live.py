"""
simulateur/donnees_live.py — Couche de données publiques « à l'instant T ».

Objectif
--------
Alimenter le simulateur avec les **véritables chiffres** disponibles gratuitement
en ligne (Eurostat, BCE, Frankfurter, World Bank, Opendatasoft, Yahoo Finance…)
au lieu de constantes figées dans le code.

Trois niveaux, utilisés dans cet ordre par le moteur :

  1. `collecter()`   : lecture réseau **côté serveur** (urllib) — fonctionne dès
                       que le processus Python a accès à Internet (poste local,
                       serveur dédié, CI ouverte).
  2. `browser_payload()` : descriptif transmis au navigateur pour que **le
                       front-end** rafraîchisse lui-même les séries via `fetch`
                       (utile quand le serveur vit dans un bac à sable fermé :
                       c'est le navigateur de l'utilisateur qui atteint le net).
  3. `SNAPSHOT`      : valeurs de référence datées, embarquées dans le dépôt,
                       utilisées hors ligne. Chaque valeur est estampillée
                       (source, période, date de vérification).

Règles de rigueur (héritées de l'esprit `import_ucdp.ContratImport`)
-------------------------------------------------------------------
  * Aucune valeur inventée : une case sans donnée vaut `None` et l'interface
    l'affiche comme « non collectée », jamais comme un zéro.
  * Toute valeur porte sa provenance (fournisseur, URL, licence, période).
  * Le mode « référence » (hors ligne) est **toujours** signalé à l'écran.
  * Aucune écriture implicite : le cache est explicite et supprimable.

Licences des fournisseurs (réutilisation libre avec attribution) :
  Eurostat (politique de réutilisation de la Commission), BCE (reproduction
  autorisée avec mention de la source), Frankfurter (données BCE, MIT),
  Opendatasoft / data.economie.gouv.fr (Licence Ouverte 2.0), World Bank
  (CC-BY 4.0), Yahoo Finance (usage de prototype, non redistribuable).
"""

from __future__ import annotations

import csv
import io
import json
import os
import time
import urllib.error
import urllib.parse
import urllib.request
from collections.abc import Callable
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

# ────────────────────────────────────────────────────────────────────────────
# Réseau
# ────────────────────────────────────────────────────────────────────────────

USER_AGENT = "simulateur-macro-politique/2.0 (projet citoyen open-source)"
CACHE_DIR = Path(os.environ.get("SIMULATEUR_CACHE", ".simulateur_cache"))
CACHE_FICHIER = CACHE_DIR / "donnees_live.json"

#: Fournisseurs écartés tant qu'une lecture a échoué récemment (anti-rafale).
_BLACKLIST: dict[str, float] = {}
DUREE_BLACKLIST_S = 300.0


class ErreurSource(RuntimeError):
    """Erreur de lecture d'une source de données publiques."""


def _http_texte(url: str, timeout: float = 12.0, entetes: dict[str, str] | None = None) -> str:
    """Lecture HTTP brute (stdlib uniquement, aucun téléchargement implicite)."""
    requete = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, **(entetes or {})})
    try:
        with urllib.request.urlopen(requete, timeout=timeout) as reponse:
            return reponse.read().decode("utf-8", errors="replace")
    except (TimeoutError, urllib.error.URLError, OSError) as exc:  # pragma: no cover - réseau
        raise ErreurSource(f"{type(exc).__name__}: {exc}") from exc


def _http_json(url: str, timeout: float = 12.0) -> Any:
    return json.loads(_http_texte(url, timeout=timeout, entetes={"Accept": "application/json"}))


# ────────────────────────────────────────────────────────────────────────────
# Adaptateurs (un par famille d'API) — partagés avec le navigateur
# ────────────────────────────────────────────────────────────────────────────
#
# Chaque adaptateur reçoit la charge utile brute et un « chemin » éventuel
# (ex. le champ à extraire dans un enregistrement Opendatasoft) puis renvoie
# un couple (valeur, période).

def ad_eurostat(payload: Any, chemin: str | None = None) -> tuple[float | None, str | None]:
    """Eurostat dissemination API (JSON-stat 2.0)."""
    if isinstance(payload, dict) and "error" in payload:
        raise ErreurSource(str(payload["error"])[:200])
    valeur = payload.get("value") or {}
    if chemin and chemin in valeur:
        cle = chemin
    elif not valeur:
        raise ErreurSource("réponse Eurostat sans observation (value vide)")
    else:
        # Avec lastTimePeriod>1, les indices JSON-stat vont du plus ancien au
        # plus récent. Certains derniers mois sont absents (ex. séries par
        # catégorie avant la publication complète) : retenir le dernier point
        # effectivement publié plutôt que le premier ou un zéro artificiel.
        cles_numeriques = [cle_valeur for cle_valeur in valeur if str(cle_valeur).isdigit()]
        cle = max(cles_numeriques, key=int) if cles_numeriques else next(iter(valeur))
    valeur_observee = valeur[cle]
    if valeur_observee is None:
        raise ErreurSource("dernière observation Eurostat manquante")
    periode = None
    try:
        index_temps = payload["dimension"]["time"]["category"]["index"]
        indice = int(cle)
        periode = next(
            (code for code, position in index_temps.items() if int(position) == indice),
            None,
        )
    except (KeyError, TypeError, ValueError):
        periode = None
    return float(valeur_observee), periode


def qualite_eurostat(payload: Any, cle: str | None) -> str | None:
    """Renvoie le code de statut de l'observation JSON-stat, s'il existe.

    Eurostat stocke les marqueurs (e = estimé, p = provisoire, f = prévision,
    i = imputé, etc.) dans un objet `status` parallèle à `value`. Le code brut
    est conservé afin de ne pas perdre les statuts moins courants.
    """
    if not isinstance(payload, dict) or cle is None:
        return None
    statuts = payload.get("status") or {}
    if isinstance(statuts, dict):
        statut = statuts.get(str(cle))
    elif isinstance(statuts, list):
        try:
            statut = statuts[int(cle)]
        except (IndexError, TypeError, ValueError):
            statut = None
    else:
        statut = None
    return str(statut) if statut not in (None, "") else None


_LIBELLES_QUALITE = {
    "b": "rupture de série",
    "c": "confidentielle",
    "d": "définition différente",
    "e": "estimée",
    "f": "prévision",
    "i": "imputée",
    "m": "valeur manquante",
    "p": "provisoire",
    "s": "valeur supprimée",
    "u": "fiabilité limitée",
}


def libelle_qualite(code: str | None) -> str:
    """Traduit les marqueurs connus en conservant le code source ailleurs."""
    if not code:
        return "aucun marqueur fourni par la source"
    libelle = _LIBELLES_QUALITE.get(code.lower())
    return f"{libelle} (code {code})" if libelle else f"marqueur source {code}"


def ad_sdmx(payload: Any, chemin: str | None = None) -> tuple[float | None, str | None]:
    """BCE — SDMX-JSON (data-api.ecb.europa.eu)."""
    jeux = payload.get("dataSets") or []
    if not jeux:
        raise ErreurSource("réponse SDMX sans dataSet")
    series = jeux[0].get("series") or {}
    if not series:
        raise ErreurSource("réponse SDMX sans série")
    observations = next(iter(series.values())).get("observations") or {}
    if not observations:
        raise ErreurSource("réponse SDMX sans observation")
    cle = "0" if "0" in observations else next(iter(observations))
    periode = None
    try:
        for dimension in payload["structure"]["dimensions"].get("observation", []):
            if dimension.get("role") == "time":
                valeurs = dimension.get("values") or []
                position = int(cle) if "0" in observations else 0
                periode = valeurs[position]["id"] if position < len(valeurs) else None
    except (KeyError, IndexError, TypeError, ValueError):
        periode = None
    brut = observations[cle]
    valeur = brut[0] if isinstance(brut, list) else brut
    return (float(valeur) if valeur is not None else None), periode


def ad_frankfurter(payload: Any, chemin: str | None = None) -> tuple[float | None, str | None]:
    """Frankfurter (taux de change BCE). `chemin` = code devise (USD, CNY…)."""
    taux = payload.get("rates") or {}
    if not taux:
        raise ErreurSource("réponse Frankfurter sans taux")
    devise = chemin or next(iter(taux))
    if devise not in taux:
        raise ErreurSource(f"devise absente de la réponse : {devise}")
    return float(taux[devise]), payload.get("date")


def ad_opendatasoft(payload: Any, chemin: str | None = None) -> tuple[float | None, str | None]:
    """API Opendatasoft v2.1 (data.economie.gouv.fr, data.gouv.fr…)."""
    resultats = payload.get("results")
    if resultats is None and payload.get("total_count") == 0:
        raise ErreurSource("jeu de données vide")
    if not resultats:
        raise ErreurSource("réponse Opendatasoft sans enregistrement")
    enregistrement = resultats[0]
    champ = chemin or ""
    brut = enregistrement
    for morceau in champ.split("."):
        if isinstance(brut, dict) and morceau in brut:
            brut = brut[morceau]
        else:
            raise ErreurSource(f"champ absent : {champ}")
    for cle_periode in ("date", "period", "annee", "annee_publication", "mois"):
        if isinstance(enregistrement, dict) and cle_periode in enregistrement:
            return float(brut), str(enregistrement[cle_periode])
    return float(brut), None


def ad_worldbank(payload: Any, chemin: str | None = None) -> tuple[float | None, str | None]:
    """World Bank Indicators API v2 : [meta, [observations…]]."""
    if not isinstance(payload, list) or len(payload) < 2 or not payload[1]:
        raise ErreurSource("réponse World Bank vide")
    observation = payload[1][0]
    if observation.get("value") is None:
        raise ErreurSource("valeur World Bank nulle")
    return float(observation["value"]), observation.get("date")


def ad_yahoo(payload: Any, chemin: str | None = None) -> tuple[float | None, str | None]:
    """Yahoo Finance chart API (cours de clôture / dernier prix)."""
    resultats = ((payload.get("chart") or {}).get("result")) or []
    if not resultats:
        raise ErreurSource("réponse Yahoo sans résultat")
    premier = resultats[0]
    prix = (premier.get("meta") or {}).get("regularMarketPrice")
    horodatage = (premier.get("meta") or {}).get("regularMarketTime")
    if prix is None:
        raise ErreurSource("prix Yahoo indisponible")
    periode = (
        datetime.fromtimestamp(int(horodatage), tz=UTC).strftime("%Y-%m-%d")
        if horodatage
        else None
    )
    return float(prix), periode


def ad_stooq(texte: str, chemin: str | None = None) -> tuple[float | None, str | None]:
    """Stooq — CSV « Symbole,Date,Heure,Ouv.,Haut,Bas,Clôt.,Vol. »."""
    lignes = [ligne for ligne in texte.splitlines() if ligne.strip()]
    if len(lignes) < 2:
        raise ErreurSource("CSV Stooq vide")
    lecteur = csv.DictReader(io.StringIO("\n".join(lignes)))
    for ligne in lecteur:
        for champ in ("Close", "Zamkniecie", "Kurs"):
            if champ in ligne and ligne[champ] not in ("", "N/D"):
                return float(ligne[champ]), ligne.get("Data") or ligne.get("Date")
    raise ErreurSource("aucun cours exploitable dans le CSV Stooq")


ADAPTATEURS_SERVEUR: dict[str, Callable[[Any, str | None], tuple[float | None, str | None]]] = {
    "eurostat": ad_eurostat,
    "sdmx": ad_sdmx,
    "frankfurter": ad_frankfurter,
    "opendatasoft": ad_opendatasoft,
    "worldbank": ad_worldbank,
    "yahoo": ad_yahoo,
    # `stooq` renvoie du CSV et non du JSON : le corps brut lui est transmis.
    "stooq": lambda charge, chemin=None: ad_stooq(charge, chemin),
}


# ────────────────────────────────────────────────────────────────────────────
# Descripteurs de sources et d'indicateurs
# ────────────────────────────────────────────────────────────────────────────

@dataclass(frozen=True)
class Source:
    """Une source publique interrogeable pour un indicateur."""

    fournisseur: str
    url: str
    adaptateur: str          # clé d'ADAPTATEURS_SERVEUR (également implémentée en JS)
    chemin: str | None = None
    licence: str = "Réutilisation libre avec attribution"
    url_page: str = ""
    navigateur: bool = True  # source utilisable en `fetch` direct depuis le navigateur

    def url_complete(self) -> str:
        return self.url


@dataclass
class Indicateur:
    """Une grandeur macro-sociale utilisée par le simulateur."""

    cle: str
    libelle: str
    unite: str
    categorie: str
    precision: int = 2
    sources: tuple[Source, ...] = ()
    #: Valeur de repli embarquée : (valeur, période, fournisseur, date de vérification)
    reference: tuple[float, str, str, str] | None = None
    note: str = ""
    #: Facteur appliqué aux valeurs lues et de référence (conversion d'unité,
    #: ex. l'API Eurostat publie des millions d'euros, le modèle raisonne en Md€).
    conversion: float = 1.0
    #: Cadence réelle de publication; ne signifie pas que la donnée est quotidienne.
    frequence: str = ""
    #: Marqueur éventuel attaché à une valeur de référence embarquée.
    qualite_reference: str | None = None

    @property
    def valeur_reference(self) -> float | None:
        return self.reference[0] if self.reference else None


@dataclass
class Lecture:
    """Résultat d'une tentative de lecture d'un indicateur."""

    cle: str
    valeur: float | None
    periode: str | None
    fournisseur: str
    url: str
    statut: str              # "live" | "reference" | "indisponible"
    detail: str = ""
    qualite_code: str | None = None  # statut brut de l'observation (ex. Eurostat: e, p, f)
    horodatage: str = field(
        default_factory=lambda: datetime.now(UTC).isoformat(timespec="seconds")
    )

    def en_dict(self) -> dict[str, Any]:
        return asdict(self)


# ─── Aides de construction (gardent le registre lisible) ───────────────────

EUROSTAT = "https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data"
EUROSTAT_LICENCE = "Eurostat — réutilisation libre (décision 2011/833/UE)"
BCE_LICENCE = "BCE — reproduction autorisée avec attribution"
ODS_LICENCE = "Licence Ouverte 2.0 (Etalab)"

def src_eurostat(dataset: str, **params: str) -> Source:
    # `lastTimePeriod=1` par défaut : on veut la dernière période publiée, pas
    # toute l'histoire de la série (payloads de plusieurs centaines de Ko).
    params.setdefault("lastTimePeriod", "1")
    requete = urllib.parse.urlencode({"format": "JSON", **params})
    return Source(
        fournisseur=f"Eurostat · {dataset.upper()}",
        url=f"{EUROSTAT}/{dataset}?{requete}",
        adaptateur="eurostat",
        licence=EUROSTAT_LICENCE,
        url_page=f"https://ec.europa.eu/eurostat/databrowser/view/{dataset.upper()}/default/table",
    )


def src_sdmx(flux: str, cle_serie: str, **params: str) -> Source:
    requete = urllib.parse.urlencode({"format": "jsondata", **params})
    return Source(
        fournisseur=f"BCE · {flux} {cle_serie}",
        url=f"https://data-api.ecb.europa.eu/service/data/{flux}/{cle_serie}?{requete}",
        adaptateur="sdmx",
        licence=BCE_LICENCE,
        url_page="https://data.ecb.europa.eu/",
    )


def src_frankfurter(devise: str) -> Source:
    return Source(
        fournisseur=f"BCE via Frankfurter · EUR/{devise}",
        url=f"https://api.frankfurter.dev/v1/latest?from=EUR&to={devise}",
        adaptateur="frankfurter",
        chemin=devise,
        licence="Frankfurter — données BCE (MIT)",
        url_page="https://frankfurter.dev/",
    )


def src_worldbank(indicateur: str, pays: str = "FR") -> Source:
    return Source(
        fournisseur=f"Banque mondiale · {indicateur}",
        url=(
            "https://api.worldbank.org/v2/country/"
            f"{pays}/indicator/{indicateur}?format=json&per_page=1&date=2024"
        ),
        adaptateur="worldbank",
        licence="Banque mondiale — CC-BY 4.0",
        url_page=f"https://data.worldbank.org/indicator/{indicateur}",
    )


def src_yahoo(symbole: str, libelle: str) -> Source:
    return Source(
        fournisseur=f"Yahoo Finance · {libelle}",
        url=f"https://query1.finance.yahoo.com/v8/finance/chart/{urllib.parse.quote(symbole)}?range=1d&interval=1d",
        adaptateur="yahoo",
        licence="Yahoo Finance — usage de prototype, non redistribuable",
        url_page=f"https://finance.yahoo.com/quote/{urllib.parse.quote(symbole)}",
        # L'API Yahoo n'autorise pas les requêtes cross-origin : elle n'est
        # interrogeable que par le serveur (ou via le proxy du projet).
        navigateur=False,
    )


def src_stooq(symbole: str, libelle: str) -> Source:
    return Source(
        fournisseur=f"Stooq · {libelle}",
        url=f"https://stooq.com/q/l/?s={symbole}&f=sd2t2ohlcv&h&e=csv",
        adaptateur="stooq",
        licence="Stooq — usage personnel / prototype",
        url_page=f"https://stooq.com/q/?s={symbole}",
        navigateur=False,
    )


#: Date de vérification des valeurs embarquées (lecture réseau réelle).
DATE_VERIFICATION = "2026-10-07"

# ─── Registre des indicateurs ──────────────────────────────────────────────
#: Toute clé du registre peut alimenter la calibration du moteur
#: (`moteur_parametrique.calibrer_contexte`) ou l'affichage du contexte.

INDICATEURS: dict[str, Indicateur] = {}

_FREQUENCES_PAR_CLE = {
    "pib_nominal_mde": "Annuelle; comptes nationaux publiés avec révisions.",
    "dette_publique_pct_pib": "Annuelle; comptes publics notifiés et révisés.",
    "deficit_public_pct_pib": "Annuelle; comptes publics notifiés et révisés.",
    "depenses_publiques_pct_pib": "Annuelle; comptes nationaux des administrations publiques.",
    "dette_souveraine_negociable_mde": "Mise à jour selon les enregistrements du portail AFT.",
    "taux_oat_france_10ans": "Mensuelle (série BCE des taux à long terme).",
    "taux_bund_allemagne_10ans": "Mensuelle (série BCE des taux à long terme).",
    "taux_bce_depot": "À chaque décision de politique monétaire de la BCE.",
    "eur_usd": "Quotidienne les jours ouvrés (taux de référence BCE).",
    "eur_cny": "Quotidienne les jours ouvrés (taux de référence BCE).",
    "eur_gbp": "Quotidienne les jours ouvrés (taux de référence BCE).",
    "eur_chf": "Quotidienne les jours ouvrés (taux de référence BCE).",
    "brent_usd": "Quotidienne les jours de marché; cours volatil.",
    "gaz_ttf_eur_mwh": "Intra-journalière / quotidienne selon la série Energy-Charts.",
    "prix_carbone_ets": "Quotidienne les jours de marché; collecte manuelle ou portail.",
    "taux_chomage_pct": "Mensuelle; série désaisonnalisée, révisions possibles.",
    "taux_chomage_jeunes_pct": "Mensuelle; série désaisonnalisée, révisions possibles.",
    "inflation_france_pct": "Mensuelle; flash en fin de mois puis données complètes vers le 16 du mois suivant.",
    "inflation_zone_euro_pct": "Mensuelle; flash en fin de mois puis données complètes vers le 16 du mois suivant.",
    "taux_pauvrete_pct": "Annuelle; publication avec décalage et révisions possibles.",
    "indice_gini": "Annuelle; publication avec décalage et révisions possibles.",
    "emissions_co2_mt": "Annuelle; inventaire publié avec environ 18 mois de décalage.",
    "depenses_sante_pct_pib": "Annuelle; comptes des administrations publiques.",
    "depenses_education_pct_pib": "Annuelle; comptes des administrations publiques.",
    "depenses_defense_pct_pib": "Annuelle; comptes publics, publication avec décalage.",
    "depenses_protection_sociale_pct_pib": "Annuelle; comptes des administrations publiques.",
    "depenses_justice_pct_pib": "Annuelle; comptes des administrations publiques.",
    "depenses_ordre_securite_pct_pib": "Annuelle; comptes des administrations publiques.",
    "depenses_investissement_public_pct_pib": "Annuelle; comptes des administrations publiques.",
    "recettes_publiques_pct_pib": "Annuelle; comptes des administrations publiques.",
    "taux_prelevement_obligatoire_pct_pib": "Annuelle; comptes nationaux et documents budgétaires.",
    "part_energie_importee_pct": "Annuelle; bilan énergétique publié avec décalage.",
    "demographie_65plus_pct": "Annuelle; statistiques démographiques.",
    "population_france": "Annuelle; estimations de population révisables.",
    "dette_locale_mde": "Annuelle; comptes locaux publiés avec décalage.",
    "solde_commercial_mde": "Mensuelle; statistiques du commerce extérieur.",
    "production_industrielle_indice": "Mensuelle; indice corrigé des variations saisonnières et calendaires.",
    "taux_emploi_pct": "Annuelle; enquête Emploi et comptes du marché du travail.",
}


def _declarer(indicateur: Indicateur) -> Indicateur:
    """Enregistre un indicateur ; un indicateur sans snapshot le dit lui-même.

    Le registre doit être lisible sans lire le code : si aucune valeur de
    référence datée n'est embarquée, la note le précise explicitement, pour que
    l'interface et l'utilisateur sachent qu'il faut interroger l'API en ligne.
    """
    if indicateur.reference is None and "collecter" not in indicateur.note.lower():
        indicateur.note = (
            indicateur.note.strip()
            + " Valeur de référence non embarquée : à collecter en ligne via l'API."
        ).strip()
    indicateur.frequence = indicateur.frequence or _FREQUENCES_PAR_CLE.get(
        indicateur.cle,
        "Fréquence propre au jeu de données; consulter le calendrier officiel de la source.",
    )
    INDICATEURS[indicateur.cle] = indicateur
    return indicateur


# — Comptes nationaux / finances publiques ---------------------------------
_declarer(Indicateur(
    cle="pib_nominal_mde",
    libelle="PIB nominal de la France",
    unite="Md€", categorie="Économie", precision=1,
    sources=(
        src_eurostat("nama_10_gdp", geo="FR", na_item="B1GQ", unit="CP_MEUR", lastTimePeriod="1"),
        src_worldbank("NY.GDP.MKTP.CN"),
    ),
    reference=(2991055.9, "2025 (provisoire)", "Eurostat NAMA_10_GDP", DATE_VERIFICATION),
    conversion=0.001,  # l'API publie 2 991 056 M€ ; le modèle raisonne en milliards d'euros
    qualite_reference="p",
    note="PIB aux prix courants (Eurostat publie 2 991 056 M€, soit 2 991 Md€) ; "
         "écart avec la comptabilité nationale INSEE < 1 %.",
))
_declarer(Indicateur(
    cle="dette_publique_pct_pib",
    libelle="Dette publique (Maastricht)",
    unite="% du PIB", categorie="Finances publiques",
    sources=(src_eurostat("gov_10dd_edpt1", geo="FR", unit="PC_GDP", na_item="GD",
                          sector="S13", lastTimePeriod="1"),),
    reference=(115.6, "2025", "Eurostat GOV_10DD_EDPT1", DATE_VERIFICATION),
))
_declarer(Indicateur(
    cle="deficit_public_pct_pib",
    libelle="Déficit public (capacité/besoin de financement)",
    unite="% du PIB", categorie="Finances publiques",
    sources=(src_eurostat("gov_10dd_edpt1", geo="FR", unit="PC_GDP", na_item="B9",
                          sector="S13", lastTimePeriod="1"),),
    reference=(-5.1, "2025", "Eurostat GOV_10DD_EDPT1", DATE_VERIFICATION),
    conversion=-1.0,  # Eurostat publie B9 négatif en cas de déficit; le moteur affiche le taux positif
    note="Eurostat publie le solde B9 négatif en cas de déficit; conversion de signe pour exposer le taux de déficit en valeur positive.",
))
_declarer(Indicateur(
    cle="depenses_publiques_pct_pib",
    libelle="Dépenses publiques totales",
    unite="% du PIB", categorie="Finances publiques",
    sources=(src_eurostat("gov_10a_exp", geo="FR", unit="PC_GDP", sector="S13",
                          na_item="TE", cofog99="TOTAL", lastTimePeriod="1"),),
    note="Nécessite `cofog99=TOTAL` ; à défaut, la valeur documentaire du projet est utilisée.",
))
_declarer(Indicateur(
    cle="dette_souveraine_negociable_mde",
    libelle="Dette négociable de l'État (AFT)",
    unite="Md€", categorie="Finances publiques",
    sources=(
        Source(
            fournisseur="Agence France Trésor (data.economie.gouv.fr)",
            url=("https://data.economie.gouv.fr/api/explore/v2.1/catalog/datasets/"
                 "dette-negociable-de-letat/records?limit=1"),
            adaptateur="opendatasoft",
            chemin="encours",
            licence=ODS_LICENCE,
            url_page="https://data.economie.gouv.fr/explore/dataset/dette-negociable-de-letat/",
        ),
    ),
    note="En cours de trésorerie ; la dette Maastricht consolidée reste la référence budgétaire.",
))

# — Marchés financiers / taux ----------------------------------------------
_declarer(Indicateur(
    cle="taux_oat_france_10ans",
    libelle="Taux souverain France à 10 ans (OAT de référence)",
    unite="%", categorie="Marchés financiers",
    sources=(src_sdmx("IRS", "M.FR.L.L40.CI.0000.EUR.N.Z", lastNObservations="1"),),
    reference=(4.0, "2026-08", "BCE IRS", DATE_VERIFICATION),
    note="Taux long terme pour la convergence (dette d'État émise, 10 ans).",
))
_declarer(Indicateur(
    cle="taux_bund_allemagne_10ans",
    libelle="Taux souverain Allemagne à 10 ans (Bund)",
    unite="%", categorie="Marchés financiers", precision=3,
    sources=(src_sdmx("IRS", "M.DE.L.L40.CI.0000.EUR.N.Z", lastNObservations="1"),),
    reference=(3.185, "2026-08", "BCE IRS", DATE_VERIFICATION),
))
_declarer(Indicateur(
    cle="taux_credit_immobilier_menages_pct",
    libelle="Taux moyen des nouveaux crédits à l'habitat des ménages (toutes durées)",
    unite="%/an", categorie="Logement et marchés financiers", precision=2,
    sources=(src_sdmx(
        "MIR", "M.FR.B.A2C.A.R.A.2250.EUR.N", lastNObservations="1"
    ),),
    reference=(3.2, "2026-08", "BCE MIR / Banque de France", DATE_VERIFICATION),
    note=(
        "Moyenne mensuelle des nouveaux prêts à l'habitat, secteur ménages, toutes durées; "
        "référence nationale de marché, non offre personnalisée et hors assurance/frais. "
        "La variation simulée suit l'écart d'OAT selon une transmission de 1 pour 1, "
        "hypothèse simplificatrice explicitée dans le moteur."
    ),
    frequence="Mensuelle; dernière période complète publiée avec décalage, révisable.",
))
_declarer(Indicateur(
    cle="taux_bce_depot",
    libelle="Taux de la facilité de dépôt de la BCE",
    unite="%", categorie="Politique monétaire",
    sources=(src_sdmx("FM", "D.U2.EUR.4F.KR.DFR.LEV", lastNObservations="1"),),
    reference=(2.5, "2026-10-05", "BCE FM", DATE_VERIFICATION),
))
_declarer(Indicateur(
    cle="eur_usd",
    libelle="Parité EUR/USD",
    unite="$ par €", categorie="Marchés financiers", precision=4,
    sources=(src_frankfurter("USD"),),
    reference=(1.1204, "2026-10-05", "BCE via Frankfurter", DATE_VERIFICATION),
))
_declarer(Indicateur(
    cle="eur_cny",
    libelle="Parité EUR/CNY",
    unite="¥ par €", categorie="Marchés financiers", precision=4,
    sources=(src_frankfurter("CNY"),),
    reference=(7.5118, "2026-10-05", "BCE via Frankfurter", DATE_VERIFICATION),
))
_declarer(Indicateur(
    cle="eur_gbp",
    libelle="Parité EUR/GBP",
    unite="£ par €", categorie="Marchés financiers", precision=4,
    sources=(src_frankfurter("GBP"),),
    reference=(0.8472, "2026-10-05", "BCE via Frankfurter", DATE_VERIFICATION),
))
_declarer(Indicateur(
    cle="eur_chf",
    libelle="Parité EUR/CHF",
    unite="CHF par €", categorie="Marchés financiers", precision=4,
    sources=(src_frankfurter("CHF"),),
    reference=(0.9311, "2026-10-05", "BCE via Frankfurter", DATE_VERIFICATION),
))

# — Énergie / matières premières -------------------------------------------
_declarer(Indicateur(
    cle="brent_usd",
    libelle="Pétrole Brent (dernier jour, USD/baril)",
    unite="$/baril", categorie="Énergie",
    sources=(
        src_yahoo("BZ=F", "Brent Crude Oil Last Day Financial Futures"),
        src_stooq("cb.f", "Brent Crude Oil"),
    ),
    reference=(101.69, "2026-10-05", "Yahoo Finance BZ=F", DATE_VERIFICATION),
    note="Cours de clôture du contrat à échéance rapprochée ; volatilité quotidienne élevée.",
))
_declarer(Indicateur(
    cle="gaz_ttf_eur_mwh",
    libelle="Gaz naturel TTF (Europe)",
    unite="€/MWh", categorie="Énergie",
    sources=(
        Source(
            fournisseur="Energy-Charts (Fraunhofer ISE) · prix de gros",
            url="https://api.energy-charts.info/price?bzn=FR&start=2026-01-01",
            adaptateur="eurostat",  # structure JSON propre, extraite par le même adaptateur JSON-stat
            licence="Fraunhofer ISE — CC-BY 4.0",
            url_page="https://www.energy-charts.info/",
        ),
    ),
    note="Prix de gros de l'électricité/énergie ; le TTF gaz reste une référence documentaire.",
))
_declarer(Indicateur(
    cle="prix_carbone_ets",
    libelle="Quota CO₂ européen (EU ETS)",
    unite="€/tCO₂", categorie="Énergie",
    sources=(
        Source(
            fournisseur="ICE Endex / EEX via portail carbone public",
            url="https://www.eex.com/en/market-data/environmental-markets/spot-market",
            adaptateur="eurostat",
            licence="EEX — usage documentaire",
            url_page="https://www.eex.com/en/market-data/environmental-markets",
            navigateur=False,
        ),
    ),
    note="Pas d'API ouverte gratuite stable : valeur documentaire à saisir/mettre à jour à la main.",
))

# — Social / emploi / inégalités -------------------------------------------
_declarer(Indicateur(
    cle="taux_chomage_pct",
    libelle="Taux de chômage France (CVS)",
    unite="% de la population active", categorie="Emploi", precision=1,
    sources=(src_eurostat("une_rt_m", geo="FR", sex="T", age="TOTAL", unit="PC_ACT",
                          s_adj="SA", lastTimePeriod="1"),),
    reference=(8.2, "2026-08", "Eurostat UNE_RT_M", DATE_VERIFICATION),
))
_declarer(Indicateur(
    cle="taux_chomage_jeunes_pct",
    libelle="Taux de chômage des 15-24 ans",
    unite="% de la population active", categorie="Emploi", precision=1,
    sources=(src_eurostat("une_rt_m", geo="FR", sex="T", age="Y15-24", unit="PC_ACT",
                          s_adj="SA", lastTimePeriod="1"),),
))
_declarer(Indicateur(
    cle="inflation_france_pct",
    libelle="Inflation France (IPCH, glissement annuel)",
    unite="%", categorie="Pouvoir d'achat", precision=1,
    sources=(src_eurostat(
        "prc_hicp_minr", freq="M", geo="FR", unit="RCH_A", coicop18="TOTAL",
        lastTimePeriod="1",
    ),),
    reference=(3.4, "2026-09 (estimé)", "Eurostat PRC_HICP_MINR", DATE_VERIFICATION),
    qualite_reference="e",
    note=(
        "Estimation flash Eurostat pour septembre 2026 (code qualité e); les données "
        "complètes sont annoncées vers le 16 octobre et peuvent réviser cette valeur."
    ),
))
_declarer(Indicateur(
    cle="inflation_zone_euro_pct",
    libelle="Inflation zone euro EA21 (IPCH, glissement annuel)",
    unite="%", categorie="Pouvoir d'achat", precision=1,
    sources=(src_eurostat(
        "prc_hicp_minr", freq="M", geo="EA21", unit="RCH_A", coicop18="TOTAL",
        lastTimePeriod="1",
    ),),
    reference=(3.8, "2026-09 (estimé, EA21)", "Eurostat PRC_HICP_MINR", DATE_VERIFICATION),
    qualite_reference="e",
    note=(
        "Estimation flash Eurostat pour septembre 2026 (code qualité e); l'agrégat "
        "EA21 comprend la Bulgarie à partir de janvier 2026."
    ),
))
# IPCH mensuel par poste de consommation. Les séries servent de repère de prix
# au panier du foyer; les codes de qualité Eurostat (estimé/provisoire/prévision)
# sont conservés dans `Lecture` et transmis jusqu'à l'interface.
_CATEGORIES_IPCH = (
    ("CP01", "Produits alimentaires et boissons non alcoolisées"),
    ("CP02", "Boissons alcoolisées, tabac et stupéfiants"),
    ("CP03", "Habillement et chaussures"),
    ("CP04", "Logement, eau et services liés au logement"),
    ("CP045", "Électricité, gaz et autres combustibles"),
    ("CP05", "Meubles et entretien du foyer"),
    ("CP06", "Santé"),
    ("CP07", "Transports"),
    ("CP08", "Information et communication"),
    ("CP09", "Loisirs, sport et culture"),
    ("CP10", "Enseignement"),
    ("CP11", "Restaurants et hébergement"),
    ("CP12", "Autres biens et services"),
)
_VALEURS_IPCH_REFERENCE = {
    "CP01": 1.1,
    "CP02": 1.9,
    "CP03": -1.5,
    "CP04": 3.6,
    "CP045": 7.7,
    "CP05": 0.0,
    "CP06": 0.8,
    "CP07": 7.2,
    "CP08": 4.9,
    "CP09": -1.0,
    "CP10": 4.5,
    "CP11": 1.9,
    "CP12": 3.2,
}
for _code_ipch, _libelle_ipch in _CATEGORIES_IPCH:
    _declarer(Indicateur(
        cle=f"inflation_ipch_{_code_ipch.lower()}",
        libelle=f"IPCH France — {_libelle_ipch} (glissement annuel)",
        unite="%", categorie="Pouvoir d'achat", precision=1,
        sources=(src_eurostat(
            "prc_hicp_minr", freq="M", geo="FR", unit="RCH_A", coicop18=_code_ipch,
            lastTimePeriod="12",
        ),),
        reference=(
            _VALEURS_IPCH_REFERENCE[_code_ipch], "2026-08",
            "Eurostat PRC_HICP_MINR", DATE_VERIFICATION,
        ),
        note=(
            "Repère de prix mensuel par catégorie pour le panier du ménage. Snapshot "
            "de la période 2026-08 vérifié le 2026-10-07; les nouvelles lectures "
            "affichent le statut Eurostat de chaque observation lorsqu'il existe."
        ),
        frequence=(
            "Mensuelle; la dernière période peut être une estimation flash révisable "
            "au milieu du mois suivant."
        ),
    ))

_declarer(Indicateur(
    cle="taux_pauvrete_pct",
    libelle="Taux de pauvreté monétaire (seuil 60 % du revenu médian)",
    unite="% de la population", categorie="Cohésion sociale", precision=1,
    sources=(src_eurostat("ilc_li02", geo="FR", unit="PC", age="TOTAL", sex="T",
                          rskpovth="B_60", lastTimePeriod="1"),),
    reference=(14.6, "2025", "Eurostat ILC_LI02", DATE_VERIFICATION),
))
_declarer(Indicateur(
    cle="indice_gini",
    libelle="Indice de Gini (inégalités de revenu disponible)",
    unite="0-100", categorie="Cohésion sociale", precision=1,
    sources=(src_eurostat("ilc_di12", geo="FR", age="TOTAL", lastTimePeriod="1"),),
    reference=(30.4, "2025", "Eurostat ILC_DI12", DATE_VERIFICATION),
))
_declarer(Indicateur(
    cle="emissions_co2_mt",
    libelle="Émissions de CO₂ (hors UTCATF, hors soutes)",
    unite="Mt CO₂", categorie="Climat", precision=1,
    sources=(src_eurostat("env_air_gge", geo="FR", airpol="CO2", src_crf="TOTXMEMO",
                          unit="MIO_T", lastTimePeriod="1"),),
    note="Inventaire UNFCCC ; la dernière année publiée a ~18 mois de retard.",
))
_declarer(Indicateur(
    cle="depenses_sante_pct_pib",
    libelle="Dépenses publiques de santé",
    unite="% du PIB", categorie="Santé", precision=2,
    sources=(src_eurostat("gov_10a_exp", geo="FR", unit="PC_GDP", sector="S13",
                          na_item="TE", cofog99="GF07", lastTimePeriod="1"),),
    note="COFOG GF07 ; Eurostat peut renvoyer une cellule vide selon la ventilation disponible.",
))
_declarer(Indicateur(
    cle="depenses_education_pct_pib",
    libelle="Dépenses publiques d'éducation",
    unite="% du PIB", categorie="Éducation", precision=2,
    sources=(src_eurostat("gov_10a_exp", geo="FR", unit="PC_GDP", sector="S13",
                          na_item="TE", cofog99="GF09", lastTimePeriod="1"),),
))
_declarer(Indicateur(
    cle="depenses_defense_pct_pib",
    libelle="Dépenses de défense",
    unite="% du PIB", categorie="Défense", precision=2,
    sources=(src_eurostat("gov_10a_exp", geo="FR", unit="PC_GDP", sector="S13",
                          na_item="TE", cofog99="GF02", lastTimePeriod="1"),),
    reference=(2.1, "2025 (référence projet)", "LPM / OTAN", DATE_VERIFICATION),
))
_declarer(Indicateur(
    cle="depenses_protection_sociale_pct_pib",
    libelle="Dépenses de protection sociale",
    unite="% du PIB", categorie="Cohésion sociale", precision=2,
    sources=(src_eurostat("gov_10a_exp", geo="FR", unit="PC_GDP", sector="S13",
                          na_item="TE", cofog99="GF10", lastTimePeriod="1"),),
))
_declarer(Indicateur(
    cle="depenses_justice_pct_pib",
    libelle="Dépenses publiques de justice",
    unite="% du PIB", categorie="Justice", precision=2,
    sources=(src_eurostat("gov_10a_exp", geo="FR", unit="PC_GDP", sector="S13",
                          na_item="TE", cofog99="GF03", lastTimePeriod="1"),),
))
_declarer(Indicateur(
    cle="depenses_ordre_securite_pct_pib",
    libelle="Dépenses d'ordre et de sécurité publics",
    unite="% du PIB", categorie="Sécurité", precision=2,
    sources=(src_eurostat("gov_10a_exp", geo="FR", unit="PC_GDP", sector="S13",
                          na_item="TE", cofog99="GF03", lastTimePeriod="1"),),
    note="Fonction COFOG « Ordre et sécurité publics » (police, gendarmerie, secours).",
))
_declarer(Indicateur(
    cle="depenses_investissement_public_pct_pib",
    libelle="Investissement public (formation brute de capital fixe)",
    unite="% du PIB", categorie="Économie", precision=2,
    sources=(src_eurostat("gov_10a_exp", geo="FR", unit="PC_GDP", sector="S13",
                          na_item="P51G", cofog99="TOTAL", lastTimePeriod="1"),),
))
_declarer(Indicateur(
    cle="recettes_publiques_pct_pib",
    libelle="Recettes publiques totales",
    unite="% du PIB", categorie="Finances publiques", precision=2,
    sources=(src_eurostat("gov_10a_main", geo="FR", unit="PC_GDP", sector="S13",
                          na_item="TR", lastTimePeriod="1"),),
))
_declarer(Indicateur(
    cle="taux_prelevement_obligatoire_pct_pib",
    libelle="Prélèvements obligatoires",
    unite="% du PIB", categorie="Fiscalité", precision=2,
    sources=(src_eurostat("gov_10a_taxag", geo="FR", unit="PC_GDP", sector="S13",
                          na_item="D2", lastTimePeriod="1"),),
    reference=(43.6, "2025 (référence projet)", "PLF / INSEE", DATE_VERIFICATION),
))
_declarer(Indicateur(
    cle="part_energie_importee_pct",
    libelle="Part de l'énergie primaire importée",
    unite="%", categorie="Énergie", precision=1,
    sources=(src_eurostat("nrg_ind_id", geo="FR", unit="PC", lastTimePeriod="1"),),
    note="Indicateur de dépendance énergétique (taux d'importation nette).",
))
_declarer(Indicateur(
    cle="demographie_65plus_pct",
    libelle="Part de la population de 65 ans et plus",
    unite="%", categorie="Démographie", precision=1,
    sources=(src_eurostat("demo_pjanind", geo="FR", indic_de="PC_Y65_GE", lastTimePeriod="1"),),
))
_declarer(Indicateur(
    cle="population_france",
    libelle="Population de la France",
    unite="personnes", categorie="Démographie", precision=0,
    sources=(src_eurostat("demo_pjan", geo="FR", sex="T", age="TOTAL", unit="NR",
                          lastTimePeriod="1"),),
    reference=(68600000.0, "2025 (référence projet)", "INSEE", DATE_VERIFICATION),
))
_declarer(Indicateur(
    cle="dette_locale_mde",
    libelle="Encours de dette des collectivités locales",
    unite="Md€", categorie="Territoires", precision=1,
    sources=(
        Source(
            fournisseur="OFGL / DGCL (data.economie.gouv.fr)",
            url=("https://data.economie.gouv.fr/api/explore/v2.1/catalog/datasets/"
                 "dette-des-collectivites-locales/records?limit=1"),
            adaptateur="opendatasoft",
            chemin="encours",
            licence=ODS_LICENCE,
            url_page="https://data.economie.gouv.fr/",
        ),
    ),
    reference=(252.0, "2025 (référence projet)", "OFGL", DATE_VERIFICATION),
))
_declarer(Indicateur(
    cle="solde_commercial_mde",
    libelle="Solde commercial de la France",
    unite="Md€", categorie="Commerce extérieur", precision=1,
    sources=(src_eurostat("ext_st_eu27_2020sitc", geo="FR", partner="WORLD",
                          sitc06="TOTAL", indic="BAL_RT", lastTimePeriod="1"),),
))
_declarer(Indicateur(
    cle="production_industrielle_indice",
    libelle="Indice de production industrielle",
    unite="indice", categorie="Industrie", precision=1,
    sources=(src_eurostat("sts_inpr_m", geo="FR", s_adj="SCA", indic_bt="PRD",
                          nace_r2="B-D", unit="I21", lastTimePeriod="1"),),
))
_declarer(Indicateur(
    cle="taux_emploi_pct",
    libelle="Taux d'emploi des 15-64 ans",
    unite="%", categorie="Emploi", precision=1,
    sources=(src_eurostat("lfsi_emp_a", geo="FR", sex="T", age="Y15-64", unit="PC_POP",
                          indic_em="EMP_LFS", lastTimePeriod="1"),),
))


# ────────────────────────────────────────────────────────────────────────────
# Collecte
# ────────────────────────────────────────────────────────────────────────────

def _lire_source(source: Source, timeout: float = 12.0) -> Lecture:
    """Interroge une source unique ; toute erreur réseau est encapsulée."""
    if source.fournisseur in _BLACKLIST:
        if time.monotonic() - _BLACKLIST[source.fournisseur] < DUREE_BLACKLIST_S:
            raise ErreurSource("source temporairement écartée après échec réseau")
    qualite_code = None
    try:
        brut = _http_texte(source.url, timeout=timeout)
        if source.adaptateur == "stooq":
            valeur, periode = ad_stooq(brut, source.chemin)
        else:
            charge = json.loads(brut)
            adaptateur = ADAPTATEURS_SERVEUR.get(source.adaptateur)
            if adaptateur is None:
                raise ErreurSource(f"adaptateur inconnu : {source.adaptateur}")
            valeur, periode = adaptateur(charge, source.chemin)
            if source.adaptateur == "eurostat":
                observations = charge.get("value") or {}
                cle_observation = (
                    source.chemin
                    if source.chemin and source.chemin in observations
                    else next(iter(observations), None)
                )
                qualite_code = qualite_eurostat(charge, cle_observation)
    except ErreurSource:
        raise
    except (json.JSONDecodeError, KeyError, TypeError, ValueError) as exc:
        raise ErreurSource(f"charge utile illisible ({type(exc).__name__})") from exc
    if valeur is None:
        raise ErreurSource("aucune valeur retournée")
    return Lecture(
        cle="", valeur=float(valeur), periode=periode, fournisseur=source.fournisseur,
        url=source.url, statut="live", qualite_code=qualite_code,
    )


def interroger(cle: str, timeout: float = 12.0) -> Lecture:
    """Retourne la meilleure lecture disponible pour un indicateur.

    Ordre : live (source 1..n) puis valeur de référence embarquée.
    """
    if cle not in INDICATEURS:
        raise KeyError(f"indicateur inconnu : {cle}")
    indicateur = INDICATEURS[cle]
    erreurs: list[str] = []
    for source in indicateur.sources:
        try:
            lecture = _lire_source(source, timeout=timeout)
        except ErreurSource as exc:
            erreurs.append(f"{source.fournisseur} → {exc}")
            if "réseau" in str(exc) or "Name or service" in str(exc):
                _BLACKLIST[source.fournisseur] = time.monotonic()
            continue
        lecture.cle = cle
        lecture.valeur = round(lecture.valeur * indicateur.conversion, 6)
        return lecture
    if indicateur.reference is not None:
        valeur, periode, fournisseur, verifie = indicateur.reference
        valeur = valeur * indicateur.conversion
        return Lecture(
            cle=cle, valeur=valeur, periode=periode, fournisseur=fournisseur,
            url=indicateur.sources[0].url if indicateur.sources else "",
            statut="reference",
            detail=f"référence embarquée vérifiée le {verifie}"
                   + (f" · échecs : {'; '.join(erreurs)}" if erreurs else ""),
            qualite_code=indicateur.qualite_reference,
        )
    return Lecture(
        cle=cle, valeur=None, periode=None,
        fournisseur=indicateur.sources[0].fournisseur if indicateur.sources else "—",
        url=indicateur.sources[0].url if indicateur.sources else "",
        statut="indisponible", detail="; ".join(erreurs) or "aucune source configurée",
    )


def collecter(cles: list[str] | None = None, timeout: float = 12.0) -> dict[str, Lecture]:
    """Interroge un ensemble d'indicateurs (tous par défaut)."""
    return {cle: interroger(cle, timeout=timeout) for cle in (cles or list(INDICATEURS))}


def reseau_disponible(timeout: float = 2.5) -> bool:
    """Teste l'accès sortant réel vers une source publique (sans effet de bord)."""
    try:
        _http_texte("https://api.frankfurter.dev/v1/latest?from=EUR&to=USD", timeout=timeout)
        return True
    except ErreurSource:
        return False


# ────────────────────────────────────────────────────────────────────────────
# Cache explicite (jamais écrit sans appel explicite)
# ────────────────────────────────────────────────────────────────────────────

def sauver_cache(lectures: dict[str, Lecture], chemin: Path | None = None) -> Path:
    """Écrit le dernier relevé dans un fichier JSON lisible et supprimable."""
    chemin = chemin or CACHE_FICHIER
    chemin.parent.mkdir(parents=True, exist_ok=True)
    charge = {
        "horodatage": datetime.now(UTC).isoformat(timespec="seconds"),
        "lectures": {cle: lecture.en_dict() for cle, lecture in lectures.items()},
    }
    chemin.write_text(json.dumps(charge, ensure_ascii=False, indent=2), encoding="utf-8")
    return chemin


def charger_cache(chemin: Path | None = None) -> dict[str, Lecture]:
    """Relit le cache s'il existe (sinon dictionnaire vide)."""
    chemin = chemin or CACHE_FICHIER
    if not chemin.exists():
        return {}
    try:
        charge = json.loads(chemin.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}
    lectures: dict[str, Lecture] = {}
    for cle, brut in (charge.get("lectures") or {}).items():
        try:
            lectures[cle] = Lecture(**brut)
        except TypeError:
            continue
    return lectures


# ────────────────────────────────────────────────────────────────────────────
# Contexte « instant T » : ce que le moteur consomme
# ────────────────────────────────────────────────────────────────────────────

def _licence_indicateur(cle: str) -> str:
    """Licence de la première source déclarée pour un indicateur."""
    sources = INDICATEURS[cle].sources
    return sources[0].licence if sources else ""


def _valeur(lectures: dict[str, Lecture], cle: str) -> float | None:
    lecture = lectures.get(cle)
    return lecture.valeur if lecture else None


@dataclass
class ContexteInstant:
    """Instantané macro-économique daté, prêt à calibrer les 5 échelons."""

    horodatage: str
    mode: str                              # "live" | "reference" | "mixte"
    pib_nominal_mde: float
    dette_publique_pct_pib: float
    deficit_public_pct_pib: float
    taux_oat_10ans: float
    taux_bund_10ans: float
    taux_bce_depot: float
    taux_credit_immobilier_menages_pct: float
    inflation_pct: float
    inflation_zone_euro_pct: float
    chomage_pct: float
    eur_usd: float
    brent_usd: float
    taux_pauvrete_pct: float
    indice_gini: float
    dette_locale_mde: float
    population: float
    depenses_publiques_pct_pib: float
    prelevements_obligatoires_pct_pib: float
    depenses_defense_pct_pib: float
    provenance: dict[str, dict[str, Any]] = field(default_factory=dict)
    #: Séries publiques collectées mais non consommées par le calibrage :
    #: elles restent affichées et traçables (aucune donnée n'est jetée).
    series_complementaires: dict[str, dict[str, Any]] = field(default_factory=dict)

    @property
    def spread_oat_bund_bps(self) -> float:
        return round((self.taux_oat_10ans - self.taux_bund_10ans) * 100.0, 1)

    @property
    def charge_dette_estimee_mde(self) -> float:
        """Charge d'intérêts approchée : encours × taux moyen de refinancement."""
        encours = self.dette_publique_pct_pib / 100.0 * self.pib_nominal_mde
        taux_moyen = (self.taux_oat_10ans + self.taux_bce_depot) / 2.0
        return round(encours * taux_moyen / 100.0 * 0.62, 1)  # 0,62 ≈ part à taux de marché

    def en_dict(self) -> dict[str, Any]:
        charge = asdict(self)
        charge["spread_oat_bund_bps"] = self.spread_oat_bund_bps
        charge["charge_dette_estimee_mde"] = self.charge_dette_estimee_mde
        return charge


#: Valeurs de repli documentaires, alignées sur `model.py` (projet), quand ni
#: le réseau ni le snapshot ne fournissent la donnée.
#: Repli documentaire, champ par champ. Les valeurs ci-dessous sont
#: **recalées automatiquement** sur le snapshot daté du registre `INDICATEURS`
#: (bloc de réconciliation après `_CORRESPONDANCE`) : il ne doit jamais y avoir
#: deux vérités pour un même champ selon que l'on est en ligne ou hors ligne.
#: Seuls les champs sans indicateur enregistré gardent la valeur écrite ici.
_REPLI = {
    "pib_nominal_mde": 3015.0,
    "dette_publique_pct_pib": 118.3,
    "deficit_public_pct_pib": 5.1,
    "taux_oat_10ans": 4.18,
    "taux_bund_10ans": 3.30,
    "taux_bce_depot": 2.50,
    "taux_credit_immobilier_menages_pct": 3.20,
    "inflation_pct": 2.1,
    "inflation_zone_euro_pct": 2.0,
    "chomage_pct": 8.2,
    "eur_usd": 1.08,
    "brent_usd": 82.5,
    "taux_pauvrete_pct": 14.6,
    "indice_gini": 30.4,
    "dette_locale_mde": 252.0,
    "population": 68600000.0,
    "depenses_publiques_pct_pib": 57.0,
    "prelevements_obligatoires_pct_pib": 43.6,
    "depenses_defense_pct_pib": 2.10,
}

#: Correspondance cl du contexte → clé d'indicateur du registre.
_CORRESPONDANCE = {
    "pib_nominal_mde": "pib_nominal_mde",
    "dette_publique_pct_pib": "dette_publique_pct_pib",
    "deficit_public_pct_pib": "deficit_public_pct_pib",
    "taux_oat_10ans": "taux_oat_france_10ans",
    "taux_bund_10ans": "taux_bund_allemagne_10ans",
    "taux_bce_depot": "taux_bce_depot",
    "taux_credit_immobilier_menages_pct": "taux_credit_immobilier_menages_pct",
    "inflation_pct": "inflation_france_pct",
    "inflation_zone_euro_pct": "inflation_zone_euro_pct",
    "chomage_pct": "taux_chomage_pct",
    "eur_usd": "eur_usd",
    "brent_usd": "brent_usd",
    "taux_pauvrete_pct": "taux_pauvrete_pct",
    "indice_gini": "indice_gini",
    "dette_locale_mde": "dette_locale_mde",
    "population": "population_france",
    "depenses_publiques_pct_pib": "depenses_publiques_pct_pib",
    "prelevements_obligatoires_pct_pib": "taux_prelevement_obligatoire_pct_pib",
    "depenses_defense_pct_pib": "depenses_defense_pct_pib",
}

# ── Réconciliation repli ↔ snapshot daté ──────────────────────────────────────
# Le registre `INDICATEURS` porte un snapshot vérifié et daté (DATE_VERIFICATION)
# pour chaque indicateur publié. On l'impose au repli : hors ligne, le simulateur
# affiche donc le dernier chiffre vérifié, et non une constante historique plus
# ancienne. Toute divergence entre les deux tables est ainsi impossible.
#
# ⚠️ La conversion d'unité est indispensable ici : `reference` est publié dans
# l'unité de la source (Eurostat donne le PIB en **millions** d'euros) alors que
# le modèle raisonne en **milliards** (`indicateur.conversion = 0,001`). Sans
# elle, le repli hors ligne valait 1 000 fois la réalité — et le bug restait
# masqué tant que la collecte tournait, car le collecteur, lui, convertissait.
for _champ, _cle_indicateur in _CORRESPONDANCE.items():
    _indicateur = INDICATEURS.get(_cle_indicateur)
    _reference = getattr(_indicateur, "reference", None)
    if _reference and _reference[0] is not None:
        _conversion = getattr(_indicateur, "conversion", 1.0) or 1.0
        _REPLI[_champ] = round(float(_reference[0]) * _conversion, 6)


#: Variable d'environnement qui force le mode hors ligne (aucune API publiques).
VARIABLE_HORS_LIGNE = "SIMULATEUR_HORS_LIGNE"


def hors_ligne_force() -> bool:
    """Vrai si l'environnement interdit la collecte réseau.

    Utile aux tests et aux exécutions sans réseau : le contexte est alors
    assemblé du cache et du snapshot daté, jamais des API publiques.
    """
    return os.environ.get(VARIABLE_HORS_LIGNE, "").strip().lower() in {
        "1", "true", "oui", "vrai", "yes", "on",
    }


def construire_contexte(
    lectures: dict[str, Lecture] | None = None,
    *,
    rafraichir: bool = False,
    utiliser_cache: bool = True,
    timeout: float = 12.0,
    hors_ligne: bool | None = None,
) -> ContexteInstant:
    """Assemble le contexte « instant T » à partir du live, du cache ou du snapshot.

    `lectures` permet d'injecter un relevé déjà effectué (tests, mode navigateur).
    `hors_ligne=True` (ou la variable d'environnement `SIMULATEUR_HORS_LIGNE=1`)
    interdit toute requête réseau : le contexte vient du cache et du snapshot
    daté. Les tests s'en servent pour être déterministes qu'ils tournent sur une
    machine connectée ou non.
    """
    if hors_ligne is None:
        hors_ligne = hors_ligne_force()
    if lectures is None:
        lectures = charger_cache() if utiliser_cache else {}
        if not hors_ligne and (rafraichir or not lectures):
            collecte = collecter(list(_CORRESPONDANCE.values()), timeout=timeout)
            lectures = {**lectures, **collecte}
            if rafraichir and any(lec.statut != "indisponible" for lec in collecte.values()):
                try:
                    sauver_cache(lectures)
                except OSError:  # disque non inscriptible : on continue sans cache
                    pass

    valeurs: dict[str, float] = {}
    provenance: dict[str, dict[str, Any]] = {}
    statuts: set[str] = set()
    for champ, cle_indicateur in _CORRESPONDANCE.items():
        lecture = lectures.get(cle_indicateur)
        indicateur = INDICATEURS[cle_indicateur]
        reference = indicateur.reference
        lecture_valide = lecture is not None and lecture.valeur is not None
        valeur = _valeur(lectures, cle_indicateur)
        if valeur is None:
            valeur = _REPLI[champ]
        statut = lecture.statut if lecture_valide else "reference"
        source_txt = (
            lecture.fournisseur if lecture_valide
            else (reference[2] if reference else "référence documentaire du projet")
        )
        periode = lecture.periode if lecture_valide else (reference[1] if reference else None)
        date_collecte = (
            lecture.horodatage[:10] if lecture_valide
            else (reference[3] if reference else None)
        )
        qualite_code = (
            lecture.qualite_code if lecture_valide else indicateur.qualite_reference
        )
        url_source = (
            lecture.url if lecture_valide
            else (indicateur.sources[0].url if indicateur.sources else "")
        )
        valeurs[champ] = float(valeur)
        statuts.add(statut)
        provenance[champ] = {
            "indicateur": cle_indicateur,
            "libelle": indicateur.libelle,
            "unite": indicateur.unite,
            "statut": statut,
            "source": source_txt,
            "periode": periode,
            "date_collecte": date_collecte,
            "frequence": indicateur.frequence,
            "qualite_code": qualite_code,
            "qualite": libelle_qualite(qualite_code),
            "detail": lecture.detail if lecture and lecture.detail else indicateur.note,
            "url": url_source,
            "licence": (
                indicateur.sources[0].licence if indicateur.sources else ""
            ),
            "note": indicateur.note,
        }

    # Séries collectées qui ne calibrent pas le moteur (santé, CO2, emploi…)
    # : on les expose quand même, avec leur provenance, pour l'utilisateur.
    complementaires: dict[str, dict[str, Any]] = {}
    for cle_indicateur, indicateur in INDICATEURS.items():
        if cle_indicateur in _CORRESPONDANCE.values():
            continue
        lecture = lectures.get(cle_indicateur)
        if lecture is not None and lecture.valeur is not None:
            # Les `Lecture` sont déjà converties dans l'unité canonique par
            # `interroger` (ou par le client avant son POST au serveur).
            valeur = lecture.valeur
            periode = lecture.periode
            date_collecte = lecture.horodatage[:10]
            fournisseur = lecture.fournisseur
            statut = lecture.statut
            qualite_code = lecture.qualite_code
            url = lecture.url
        elif indicateur.reference is not None:
            valeur = indicateur.reference[0] * indicateur.conversion
            periode = indicateur.reference[1]
            date_collecte = indicateur.reference[3]
            fournisseur = indicateur.reference[2]
            statut = "reference"
            qualite_code = indicateur.qualite_reference
            url = indicateur.sources[0].url if indicateur.sources else ""
        else:
            continue
        complementaires[cle_indicateur] = {
            "libelle": indicateur.libelle,
            "unite": indicateur.unite,
            "categorie": indicateur.categorie,
            "valeur": round(valeur, 4),
            "periode": periode,
            "date_collecte": date_collecte,
            "frequence": indicateur.frequence,
            "fournisseur": fournisseur,
            "statut": statut,
            "qualite_code": qualite_code,
            "qualite": libelle_qualite(qualite_code),
            "note": indicateur.note,
            "url": url,
            "licence": _licence_indicateur(cle_indicateur),
        }

    if statuts == {"live"}:
        mode = "live"
    elif statuts == {"reference"}:
        mode = "reference"
    else:
        mode = "mixte"

    return ContexteInstant(
        horodatage=datetime.now(UTC).isoformat(timespec="seconds"),
        mode=mode,
        provenance=provenance,
        series_complementaires=complementaires,
        **valeurs,
    )


# ────────────────────────────────────────────────────────────────────────────
# Charge utile pour le navigateur
# ────────────────────────────────────────────────────────────────────────────

def browser_payload(cles: list[str] | None = None) -> dict[str, Any]:
    """Descriptif des sources que le **navigateur** peut interroger directement.

    Le front-end applique les mêmes adaptateurs (implémentés en JS) : si le
    serveur n'a pas accès au réseau, c'est le poste de l'utilisateur qui
    rafraîchit les séries « à l'instant T ».
    """
    charge: dict[str, Any] = {}
    for cle in (cles or list(INDICATEURS)):
        indicateur = INDICATEURS[cle]
        sources = [
            {
                "fournisseur": source.fournisseur,
                "url": source.url,
                "adaptateur": source.adaptateur,
                "chemin": source.chemin,
                "licence": source.licence,
                "url_page": source.url_page,
            }
            for source in indicateur.sources
            if source.navigateur
        ]
        charge[cle] = {
            "libelle": indicateur.libelle,
            "unite": indicateur.unite,
            "categorie": indicateur.categorie,
            "precision": indicateur.precision,
            "note": indicateur.note,
            "frequence": indicateur.frequence,
            "qualite_reference": indicateur.qualite_reference,
            "conversion": indicateur.conversion,
            # Repli même-origine : le serveur relaie la source quand le
            # navigateur est bloqué par CORS (Yahoo, Stooq, ICE/EEX…).
            "proxy_url": f"/api/proxy?indicateur={cle}",
            "tableau_moteur": cle in _CORRESPONDANCE.values(),
            "sources": sources,
            "reference": (
                {
                    "valeur": indicateur.reference[0],
                    "periode": indicateur.reference[1],
                    "fournisseur": indicateur.reference[2],
                    "verifie_le": indicateur.reference[3],
                    "qualite_code": indicateur.qualite_reference,
                    "qualite": libelle_qualite(indicateur.qualite_reference),
                }
                if indicateur.reference else None
            ),
        }
    return charge


def catalogue_public() -> list[dict[str, Any]]:
    """Vue sérialisable du registre (pour l'API et la documentation)."""
    return [
        {
            "cle": indicateur.cle,
            "libelle": indicateur.libelle,
            "unite": indicateur.unite,
            "categorie": indicateur.categorie,
            "sources": [source.fournisseur for source in indicateur.sources],
            "licences": sorted({source.licence for source in indicateur.sources}),
            "frequence": indicateur.frequence,
            "qualite_reference": indicateur.qualite_reference,
            "reference": (
                {
                    "valeur": indicateur.reference[0],
                    "periode": indicateur.reference[1],
                    "fournisseur": indicateur.reference[2],
                    "verifie_le": indicateur.reference[3],
                    "qualite_code": indicateur.qualite_reference,
                    "qualite": libelle_qualite(indicateur.qualite_reference),
                }
                if indicateur.reference else None
            ),
            "note": indicateur.note,
        }
        for indicateur in INDICATEURS.values()
    ]


if __name__ == "__main__":  # pragma: no cover - outil en ligne de commande
    import argparse

    analyseur = argparse.ArgumentParser(description="Relevé des données publiques du simulateur")
    analyseur.add_argument("--indicateur", action="append", help="clé à relever (répétable)")
    analyseur.add_argument("--json", action="store_true", help="sortie JSON complète")
    analyseur.add_argument("--cache", action="store_true", help="écrit le cache local")
    arguments = analyseur.parse_args()

    releve = collecter(arguments.indicateur)
    if arguments.json:
        print(json.dumps({cle: lec.en_dict() for cle, lec in releve.items()}, ensure_ascii=False, indent=2))
    else:
        for cle, lecture in releve.items():
            valeur = "—" if lecture.valeur is None else f"{lecture.valeur:g} {INDICATEURS[cle].unite}"
            print(f"{lecture.statut:>12} | {cle:<38} | {valeur:>18} | {lecture.fournisseur}")
    if arguments.cache:
        print(f"cache écrit : {sauver_cache(releve)}")
