"""Catalogue et collecte de cotations indicatives des grands indices actions.

Les cours proviennent du flux Yahoo Finance (interface de prototype, données
susceptibles d'être différées et soumises aux conditions du fournisseur). Les
pages des places et propriétaires d'indices sont données séparément pour
vérification. L'application n'invente jamais de cotation lorsque la source ne
répond pas : elle affiche alors « indisponible » ou un cache horodaté.

Les indices sont des repères de marché, pas des titres que l'on peut acheter
comme tels. Les plus/moins-values du simulateur sont des stress-tests bruts sur
une exposition saisie par l'utilisateur, sans dividendes, frais, change,
fiscalité ni tracking error.
"""

from __future__ import annotations

import json
import threading
import urllib.error
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import UTC, datetime
from typing import Any
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

FOURNISSEUR_COTATIONS = "Yahoo Finance (flux tiers; cours éventuellement différés)"
DELAI_RESEAU_SECONDES = 7.0

# Sélection représentative, non exhaustive, des principales places et zones.
# Les symboles sont des identifiants Yahoo Finance; les valeurs ne sont pas
# embarquées dans le dépôt afin d'éviter de transformer un instantané de marché
# sous licence de prototype en jeu de données redistribué.
MARCHES_ACTIONS: tuple[dict[str, str], ...] = (
    {
        "cle": "cac40", "nom": "CAC 40", "symbole": "^FCHI",
        "region": "France", "place": "Euronext Paris", "devise": "EUR",
        "page_officielle": "https://live.euronext.com/en/product/indices/FR0003500008-XPAR",
    },
    {
        "cle": "eurostoxx50", "nom": "EURO STOXX 50", "symbole": "^STOXX50E",
        "region": "Europe", "place": "STOXX / zone euro", "devise": "EUR",
        "page_officielle": "https://www.stoxx.com/index-details?symbol=SX5E",
    },
    {
        "cle": "dax", "nom": "DAX", "symbole": "^GDAXI",
        "region": "Europe", "place": "Xetra / Deutsche Börse", "devise": "EUR",
        "page_officielle": "https://www.stoxx.com/index-details?symbol=DAX",
    },
    {
        "cle": "ftse100", "nom": "FTSE 100", "symbole": "^FTSE",
        "region": "Royaume-Uni", "place": "London Stock Exchange", "devise": "GBP",
        "page_officielle": "https://www.londonstockexchange.com/indices/ftse-100",
    },
    {
        "cle": "sp500", "nom": "S&P 500", "symbole": "^GSPC",
        "region": "Amérique du Nord", "place": "S&P Dow Jones Indices", "devise": "USD",
        "page_officielle": "https://www.spglobal.com/spdji/en/indices/equity/sp-500/",
    },
    {
        "cle": "nasdaq_composite", "nom": "NASDAQ Composite", "symbole": "^IXIC",
        "region": "Amérique du Nord", "place": "Nasdaq", "devise": "USD",
        "page_officielle": "https://www.nasdaq.com/market-activity/indexes/comp",
    },
    {
        "cle": "tsx", "nom": "S&P/TSX Composite", "symbole": "^GSPTSE",
        "region": "Canada", "place": "Toronto Stock Exchange", "devise": "CAD",
        "page_officielle": "https://www.tsx.com/",
    },
    {
        "cle": "ibovespa", "nom": "IBOVESPA", "symbole": "^BVSP",
        "region": "Amérique latine", "place": "B3 São Paulo", "devise": "BRL",
        "page_officielle": "https://www.b3.com.br/en_us/market-data-and-indices/indices/broad-indices/ibovespa.htm",
    },
    {
        "cle": "nikkei225", "nom": "Nikkei 225", "symbole": "^N225",
        "region": "Japon", "place": "Japan Exchange Group / Osaka", "devise": "JPY",
        "page_officielle": "https://indexes.nikkei.co.jp/en/nkave/index/profile?idx=nk225",
    },
    {
        "cle": "hang_seng", "nom": "Hang Seng Index", "symbole": "^HSI",
        "region": "Hong Kong", "place": "Hong Kong Exchanges", "devise": "HKD",
        "page_officielle": "https://www.hsi.com.hk/eng/indexes/all-indexes/hsi",
    },
    {
        "cle": "shanghai_composite", "nom": "Shanghai Composite", "symbole": "000001.SS",
        "region": "Chine continentale", "place": "Shanghai Stock Exchange", "devise": "CNY",
        "page_officielle": "https://english.sse.com.cn/markets/indices/overview/",
    },
    {
        "cle": "nifty50", "nom": "NIFTY 50", "symbole": "^NSEI",
        "region": "Inde", "place": "National Stock Exchange of India", "devise": "INR",
        "page_officielle": "https://www.niftyindices.com/indices/equity/broad-based-indices/nifty-50",
    },
    {
        "cle": "asx200", "nom": "S&P/ASX 200", "symbole": "^AXJO",
        "region": "Australie", "place": "Australian Securities Exchange", "devise": "AUD",
        "page_officielle": "https://www.asx.com.au/markets/indices/price-returns",
    },
)

_CACHE_COTATIONS: dict[str, dict[str, Any]] = {}
_CACHE_VERROU = threading.Lock()


def _url_yahoo(symbole: str) -> str:
    symbole_encode = urllib.parse.quote(symbole, safe="")
    return (
        "https://query1.finance.yahoo.com/v8/finance/chart/"
        f"{symbole_encode}?range=1d&interval=1d"
    )


def _date_utc(timestamp: Any) -> str | None:
    try:
        return datetime.fromtimestamp(float(timestamp), UTC).isoformat(timespec="seconds")
    except (TypeError, ValueError, OverflowError, OSError):
        return None


def _fraicheur_cotation(
    cotation: dict[str, Any], *, maintenant: datetime | None = None, cache: bool = False
) -> dict[str, Any]:
    """Requalifie un cours selon son âge et la date locale de sa place.

    Les calendriers fériés des places ne sont pas embarqués : une date sans
    séance est signalée comme fermeture possible, jamais comme un cours live.
    """
    horodatage = cotation.get("horodatage_cours_utc")
    if not horodatage:
        return {**cotation, "age_heures": None, "date_cours_locale": None,
                "etat_place": "Aucun cours/horodatage retourné par le fournisseur."}
    try:
        instant = datetime.fromisoformat(str(horodatage).replace("Z", "+00:00"))
        if instant.tzinfo is None:
            instant = instant.replace(tzinfo=UTC)
        zone_nom = str(cotation.get("fuseau_horaire_place") or "UTC")
        try:
            zone = ZoneInfo(zone_nom)
        except (ZoneInfoNotFoundError, ValueError):
            zone = UTC
            zone_nom = "UTC (repli; fuseau de place inconnu)"
        maintenant_utc = maintenant or datetime.now(UTC)
        if maintenant_utc.tzinfo is None:
            maintenant_utc = maintenant_utc.replace(tzinfo=UTC)
        maintenant_utc = maintenant_utc.astimezone(UTC)
        age_heures = max(0.0, (maintenant_utc - instant.astimezone(UTC)).total_seconds() / 3600.0)
        date_cours = instant.astimezone(zone).date()
        date_locale = maintenant_utc.astimezone(zone).date()
    except (TypeError, ValueError, OverflowError, OSError):
        return {**cotation, "statut": "ancien", "age_heures": None,
                "date_cours_locale": None,
                "etat_place": "Horodatage illisible : fraîcheur non vérifiable."}

    meme_jour = date_cours == date_locale
    if age_heures <= 72 and meme_jour:
        statut = "cache" if cache else "observé"
        etat = "Cours daté du jour local; le délai éventuel du fournisseur n'est pas mesuré."
    elif age_heures <= 72:
        statut = "cache" if cache else "dernier cours"
        etat = (
            "Pas de cours daté d'aujourd'hui : place possiblement hors séance/fermée "
            "(week-end ou jour férié), ou flux différé; calendrier exact non vérifié."
        )
    else:
        statut = "ancien"
        etat = (
            "Cours âgé de plus de 72 h : fermeture prolongée, retard ou donnée périmée "
            "possible; cause et calendrier exacts non vérifiés."
        )
    return {
        **cotation,
        "statut": statut,
        "age_heures": round(age_heures, 1),
        "fuseau_horaire_place": zone_nom,
        "date_cours_locale": date_cours.isoformat(),
        "etat_place": etat,
    }


def _lire_cotation(marche: dict[str, str], timeout: float = DELAI_RESEAU_SECONDES) -> dict[str, Any]:
    url = _url_yahoo(marche["symbole"])
    requete = urllib.request.Request(
        url,
        headers={"User-Agent": "Mozilla/5.0 (compatible; SimulateurCitoyen/1.0)"},
    )
    with urllib.request.urlopen(requete, timeout=timeout) as reponse:
        charge = json.loads(reponse.read().decode("utf-8"))

    resultat = ((charge.get("chart") or {}).get("result") or [None])[0]
    if not resultat:
        detail = ((charge.get("chart") or {}).get("error") or {}).get("description")
        raise ValueError(detail or "réponse de cotation vide")
    meta = resultat.get("meta") or {}
    cours = meta.get("regularMarketPrice")
    instant_cours = _date_utc(meta.get("regularMarketTime"))
    if cours is None or instant_cours is None:
        raise ValueError("cours ou horodatage de marché absent")

    maintenant = datetime.now(UTC)
    observation = {
        **marche,
        "cours": float(cours),
        "devise": meta.get("currency") or marche["devise"],
        "variation_jour": _nombre(meta.get("regularMarketChange")),
        "variation_jour_pct": _nombre(meta.get("regularMarketChangePercent")),
        "cloture_precedente": _nombre(meta.get("chartPreviousClose")),
        "plus_haut_jour": _nombre(meta.get("regularMarketDayHigh")),
        "plus_bas_jour": _nombre(meta.get("regularMarketDayLow")),
        "volume": _nombre(meta.get("regularMarketVolume")),
        "place_fournisseur": meta.get("fullExchangeName") or meta.get("exchangeName") or marche["place"],
        "nom_fournisseur": meta.get("longName") or meta.get("shortName") or marche["nom"],
        "symbole_fournisseur": meta.get("symbol") or marche["symbole"],
        "horodatage_cours_utc": instant_cours,
        "horodatage_releve_utc": maintenant.isoformat(timespec="seconds"),
        "fuseau_horaire_place": str(meta.get("exchangeTimezoneName") or "UTC"),
        "fournisseur": FOURNISSEUR_COTATIONS,
        "url_cotation": url,
        "url_page_officielle": marche["page_officielle"],
        "frequence": "Interrogation à la demande; fraîcheur et retard propres au flux et à la place.",
        "licence": "Flux tiers Yahoo Finance, usage de prototype; vérifier les conditions avant redistribution commerciale.",
    }
    return _fraicheur_cotation(observation, maintenant=maintenant)


def _nombre(valeur: Any) -> float | None:
    try:
        resultat = float(valeur)
    except (TypeError, ValueError):
        return None
    return resultat if resultat == resultat else None


def obtenir_cotations(*, actualiser: bool = True, timeout: float = DELAI_RESEAU_SECONDES) -> dict[str, Any]:
    """Retourne les indices connus et, si demandé, tente une lecture simultanée.

    Les échecs réseau ne sont jamais remplacés par un faux cours. Un relevé déjà
    obtenu dans le processus peut être retourné comme cache, avec son horodatage
    et un statut explicitement marqué `cache`.
    """
    maintenant = datetime.now(UTC).isoformat(timespec="seconds")
    observations: dict[str, dict[str, Any]] = {}
    erreurs: dict[str, str] = {}
    if actualiser:
        with ThreadPoolExecutor(max_workers=8, thread_name_prefix="cotation") as pool:
            futures = {
                pool.submit(_lire_cotation, marche, timeout): marche
                for marche in MARCHES_ACTIONS
            }
            for futur in as_completed(futures):
                marche = futures[futur]
                try:
                    observations[marche["cle"]] = futur.result()
                except (OSError, urllib.error.URLError, TimeoutError, ValueError, json.JSONDecodeError) as exc:
                    erreurs[marche["cle"]] = f"{type(exc).__name__}: {exc}"

        if observations:
            with _CACHE_VERROU:
                _CACHE_COTATIONS.update(observations)

    with _CACHE_VERROU:
        cache = {cle: dict(valeur) for cle, valeur in _CACHE_COTATIONS.items()}

    resultats = []
    for marche in MARCHES_ACTIONS:
        cotation = observations.get(marche["cle"])
        if cotation is None:
            cotation = cache.get(marche["cle"])
            if cotation is not None:
                cotation = _fraicheur_cotation(cotation, cache=True)
                cotation["erreur_rafraichissement"] = erreurs.get(marche["cle"])
            else:
                cotation = {
                    **marche,
                    "cours": None,
                    "devise": marche["devise"],
                    "variation_jour": None,
                    "variation_jour_pct": None,
                    "horodatage_cours_utc": None,
                    "horodatage_releve_utc": None,
                    "statut": "indisponible",
                    "fournisseur": FOURNISSEUR_COTATIONS,
                    "url_cotation": _url_yahoo(marche["symbole"]),
                    "url_page_officielle": marche["page_officielle"],
                    "frequence": "Interrogation à la demande; aucune période de marché n'a été retournée.",
                    "licence": "Flux tiers Yahoo Finance, usage de prototype; vérifier les conditions avant redistribution commerciale.",
                    "erreur_rafraichissement": erreurs.get(marche["cle"], "aucune cotation disponible dans cette session"),
                }
        resultats.append(cotation)
    return {
        "date_interrogation_utc": maintenant,
        "fournisseur": FOURNISSEUR_COTATIONS,
        "statut_collecte": "partielle" if erreurs else ("ok" if observations else "cache ou non actualisé"),
        "nombre_indices": len(MARCHES_ACTIONS),
        "indices": resultats,
        "avertissement": (
            "Univers représentatif de 13 indices, non exhaustif; les indices ne sont pas des titres "
            "directement détenus. Cours d'un fournisseur tiers, possiblement différés; les simulations "
            "de plus/moins-value sont des chocs bruts, non une prévision et non un conseil financier."
        ),
    }


def catalogue_cotations() -> dict[str, Any]:
    """Métadonnées sans déclencher d'appel réseau (par ex. pour les tests)."""
    return obtenir_cotations(actualiser=False)
