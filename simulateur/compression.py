"""simulateur/compression.py — compression HTTP négociée, sans dépendance.

Pourquoi ce module existe
-------------------------

Le simulateur sert des charges JSON volumineuses : environ 240 Kio pour une
simulation complète, 100 Kio pour le catalogue des 101 leviers, 100 Kio pour le
contexte « instant T ». Sur une connexion ordinaire, c'est le transfert — et non
le calcul (35 ms côté serveur) — qui donne l'impression d'une page lente :
chaque mouvement de curseur déclenche une simulation dont la réponse traverse
le réseau.

La bibliothèque standard sait déjà compresser. Ce module fait deux choses, et
rien de plus :

  1. **négocier** l'encodage à partir de l'en-tête ``Accept-Encoding`` du
     navigateur, en respectant les qualités (``q=``) et les refus (``q=0``) ;
  2. **compresser** la charge si l'encodage retenu est disponible, et seulement
     si la compression fait réellement gagner de la place.

Aucune dépendance externe : ``gzip`` et ``zlib`` viennent de la bibliothèque
standard. Brotli et Zstandard sont utilisés **s'ils sont importables** (CPython
≥ 3.14 ou module tiers), jamais requis — leur absence n'est pas une erreur.

Sécurité et limites
-------------------

* Aucune compression sur des réponses déjà chiffrées ou déjà compressées
  (images, archives) : le serveur ne compresse que ce qu'il produit lui-même
  (HTML et JSON).
* Le seuil :math:`\\geq 512` octets évite de dépenser du processeur pour un
  gain nul, et supprime la classe de bug « réponse compressée plus grosse que
  la réponse brute ».
* ``Vary: Accept-Encoding`` est **obligatoire** : sans lui, un proxy pourrait
  servir une réponse gzip à un client qui ne le décode pas.
"""

from __future__ import annotations

import gzip
import zlib
from collections.abc import Callable

#: Taille minimale (octets) en dessous de laquelle compresser ne sert à rien :
#: l'en-tête gzip et son contrôle coûtent eux-mêmes une centaine d'octets.
SEUIL_COMPRESSION = 512

#: Niveau de compression : 6 est le compromis de la bibliothèque standard
#: (bon ratio, coût CPU faible). Monter à 9 double le temps de compression pour
#: quelques pour-cent de gain — mauvais calcul sur un serveur qui répond à
#: chaque mouvement de curseur.
NIVEAU_GZIP = 6

#: Ordre de préférence du serveur, du meilleur ratio au plus coûteux.
PREFERENCE = ("br", "zstd", "gzip", "deflate")

_COMPRESSEURS: dict[str, Callable[[bytes], bytes]] = {}


def _gzip(charge: bytes) -> bytes:
    return gzip.compress(charge, compresslevel=NIVEAU_GZIP)


def _deflate(charge: bytes) -> bytes:
    # `wbits=-15` : flux zlib brut, sans en-tête ni somme de contrôle — c'est
    # ce que les navigateurs entendent par « deflate ».
    compresseur = zlib.compressobj(NIVEAU_GZIP, zlib.DEFLATED, -15)
    return compresseur.compress(charge) + compresseur.flush()


def _enregistrer_defauts() -> None:
    _COMPRESSEURS["gzip"] = _gzip
    _COMPRESSEURS["deflate"] = _deflate
    try:  # CPython ≥ 3.14 fournit `brotli` ; sinon module tiers éventuel.
        import brotli  # type: ignore[import-not-found]

        _COMPRESSEURS["br"] = lambda charge: brotli.compress(charge)
    except Exception:  # pragma: no cover - dépend de l'interpréteur
        pass
    try:
        import compression.zstd  # type: ignore[import-not-found]  # noqa: PLC0415

        _COMPRESSEURS["zstd"] = lambda charge: compression.zstd.compress(charge)
    except Exception:  # pragma: no cover - dépend de l'interpréteur
        pass


_enregistrer_defauts()


def encodages_disponibles() -> tuple[str, ...]:
    """Encodages réellement utilisables sur cet interpréteur."""
    return tuple(encodage for encodage in PREFERENCE if encodage in _COMPRESSEURS)


def _qualites(accepte: str) -> list[tuple[str, float]]:
    """Analyse un en-tête ``Accept-Encoding`` en paires (encodage, qualité).

    Tolérant : un en-tête malformé ne doit jamais faire échouer une réponse —
    on retombe alors sur « aucune compression », qui est toujours correcte.
    """
    propositions: list[tuple[str, float]] = []
    for morceau in (accepte or "").split(","):
        partie = morceau.strip()
        if not partie:
            continue
        nom, _, parametres = partie.partition(";")
        nom = nom.strip().lower()
        if not nom:
            continue
        qualite = 1.0
        for parametre in parametres.split(";"):
            cle, _, valeur = parametre.partition("=")
            if cle.strip().lower() == "q":
                try:
                    qualite = float(valeur.strip().strip('"'))
                except ValueError:
                    qualite = 1.0
        propositions.append((nom, max(0.0, min(1.0, qualite))))
    return propositions


def negocier(accepte: str | None) -> str | None:
    """Retourne l'encodage à utiliser, ou ``None`` si le client n'en veut aucun.

    Règles appliquées, dans l'ordre :

    * ``identity`` explicite à ``q=1`` et ``*;q=0`` désactivent tout ;
    * un encodage refusé (``q=0``) n'est jamais retenu ;
    * à qualité égale, la préférence du **serveur** départage (meilleur ratio
      d'abord) : c'est le contraire de la négociation de type MIME classique,
      mais ici le serveur connaît le coût de chaque algorithme.
    """
    if not accepte:
        return None
    propositions = _qualites(accepte)
    if not propositions:
        return None
    disponibles = encodages_disponibles()
    scores: dict[str, float] = {}
    for nom, qualite in propositions:
        if qualite <= 0.0:
            continue
        if nom == "*":
            # « * » ne fixe que les encodages non cités explicitement :
            # `setdefault` empêche d'écraser une qualité nominative.
            for encodage in disponibles:
                scores.setdefault(encodage, qualite)
        elif nom in disponibles:
            scores[nom] = max(scores.get(nom, 0.0), qualite)
    # Un refus nominatif (q=0) l'emporte toujours sur un « * » acceptant.
    for nom, qualite in propositions:
        if qualite == 0.0:
            scores.pop(nom, None)
    if not scores:
        return None
    # À qualité égale, la préférence du serveur départage (meilleur ratio
    # d'abord) : c'est lui qui connaît le coût de chaque algorithme.
    meilleur = max(scores.values())
    for encodage in PREFERENCE:
        if scores.get(encodage, 0.0) == meilleur:
            return encodage
    return None


def compresser(charge: bytes, encodage: str | None) -> tuple[bytes, str | None]:
    """Compresse ``charge`` ; renvoie ``(charge, encodage retenu ou None)``.

    La compression n'est appliquée que si elle est utile : en dessous du seuil,
    ou si le résultat n'est pas plus petit, la charge brute est renvoyée telle
    quelle. Un serveur ne doit jamais renvoyer une réponse compressée plus
    lourde que l'originale.
    """
    if not encodage or encodage not in _COMPRESSEURS:
        return charge, None
    if len(charge) < SEUIL_COMPRESSION:
        return charge, None
    try:
        compressee = _COMPRESSEURS[encodage](charge)
    except Exception:  # pragma: no cover - filet de sécurité réseau
        return charge, None
    if len(compressee) >= len(charge):
        return charge, None
    return compressee, encodage


def repondre(accepte: str | None, charge: bytes) -> tuple[bytes, str | None]:
    """Raccourci : négocie puis compresse. ``(charge, encodage retenu)``."""
    return compresser(charge, negocier(accepte))


#: En-tête à renvoyer avec toute réponse compressible, compressée ou non : il
#: interdit à un intermédiaire de réutiliser la réponse d'un autre client.
EN_TETE_VARY = "Accept-Encoding"
