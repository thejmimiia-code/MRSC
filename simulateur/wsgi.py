"""simulateur/wsgi.py — le simulateur derrière n'importe quel hébergeur.

Pourquoi ce module
------------------

``python3 -m simulateur.dashboard`` lance son propre serveur
(``ThreadingHTTPServer``) : parfait sur un poste, inutilisable tel quel chez un
hébergeur. Un hébergeur ne vous demande pas « quel port veux-tu ? », il impose
le sien (variable d'environnement ``PORT``), place souvent un **reverse proxy**
devant l'application, et s'attend à une application **WSGI** — l'interface
standard entre un serveur web Python (gunicorn, uWSGI, waitress) et le code.

Plutôt que de réécrire un routeur pour ces plateformes — au prix d'un double
entretien où les deux versions finiraient par diverger — ce module **branche le
handler existant sur une requête WSGI**. Il n'y a donc qu'un seul routeur, un
seul jeu de routes, un seul comportement : ce que l'on vérifie en local est
exactement ce qui tourne en ligne.

Comment ça marche
-----------------

``DashboardHandler`` dérive de ``BaseHTTPRequestHandler`` : il lit une requête
sur ``self.rfile`` et écrit sa réponse sur ``self.wfile``. Rien ne l'oblige à
parler à une vraie socket. On lui donne donc :

* un ``rfile`` rempli avec la requête reconstituée depuis l'``environ`` WSGI
  (ligne de requête, en-têtes, corps) ;
* un ``wfile`` en mémoire (``BytesIO``) où l'on récupère le corps ;
* une réécriture de ``flush_headers`` qui intercepte la ligne de statut et les
  en-têtes que le handler croyait écrire sur le réseau.

Un seul ``handle_one_request()`` suffit : WSGI appelle l'application une fois
par requête, contrairement au serveur qui enchaîne les requêtes sur une
connexion persistante.

Utilisation
-----------

::

    gunicorn --bind 0.0.0.0:$PORT --workers 2 simulateur.wsgi:application

Ou, sans rien installer de plus (``wsgiref`` fait partie de la bibliothèque
standard, mais il est mono-thread et réservé au développement) ::

    python3 -c "from wsgiref.simple_server import make_server; \
                from simulateur.wsgi import application; \
                make_server('0.0.0.0', 8080, application).serve_forever()"

Limites assumées
----------------

* Ce module est un **pont**, pas un serveur : il n'ajoute ni route, ni
  en-tête, ni logique métier. Tout ce qu'il renvoie vient du handler.
* Les en-têtes hop-by-hop que le serveur doit fixer lui-même (``Connection``,
  ``Transfer-Encoding``, ``Date``, ``Server``) sont écartés : les laisser
  passer produirait des doublons et, pour ``Connection``, une réponse
  illégale derrière un proxy.
"""

from __future__ import annotations

import io
import sys
import traceback
from collections.abc import Callable
from typing import Any

from .dashboard import DashboardHandler

#: En-têtes que le serveur WSGI (ou le proxy devant lui) doit fixer lui-même.
#: ``Connection`` doit disparaître : laisser « Connection: close » remonter
#: ferait croire au proxy qu'il doit fermer la connexion à chaque requête.
_ENTETES_HOP_BY_HOP = frozenset({"connection", "transfer-encoding", "server", "date"})

#: Corps renvoyé lorsqu'une exception échappe au handler. Volontairement muet :
#: le détail va dans les journaux de la plateforme, jamais au visiteur.
_MESSAGE_ERREUR = b"Erreur interne du simulateur (voir logs)"


def _requete_brute(environ: dict[str, Any]) -> bytes:
    """Reconstruit la requête HTTP telle que ``rfile`` l'attend.

    WSGI livre la requête émiettée dans un dictionnaire (``REQUEST_METHOD``,
    ``PATH_INFO``, ``HTTP_ACCEPT``…) ; le handler, lui, veut du texte brut. On
    refait le chemin inverse.
    """
    methode = environ.get("REQUEST_METHOD", "GET")
    # WSGI découpe l'URL en deux : SCRIPT_NAME (le préfixe sous lequel
    # l'application est montée, « /simulateur ») et PATH_INFO (le reste). Le
    # handler route sur PATH_INFO seul : y recoller SCRIPT_NAME donnerait
    # « /simulateur/api/lexique », une route qu'il ne connaît pas — donc un 404
    # chez l'hébergeur alors que tout marche en local.
    chemin = environ.get("PATH_INFO") or "/"
    query = environ.get("QUERY_STRING") or ""
    lignes = [f"{methode} {chemin}{f'?{query}' if query else ''} HTTP/1.1"]

    for cle, valeur in environ.items():
        if valeur in (None, ""):
            continue
        if cle.startswith("HTTP_"):
            nom = cle[5:].replace("_", "-").title()
            lignes.append(f"{nom}: {valeur}")
        elif cle in ("CONTENT_TYPE", "CONTENT_LENGTH"):
            lignes.append(f"{cle.replace('_', '-').title()}: {valeur}")

    entetes = "\r\n".join(lignes).encode("iso-8859-1", "replace")
    return entetes + b"\r\n\r\n" + _corps(environ)


def _corps(environ: dict[str, Any]) -> bytes:
    """Lit le corps de la requête dans ``wsgi.input``, sans jamais bloquer."""
    brut = environ.get("CONTENT_LENGTH") or environ.get("HTTP_CONTENT_LENGTH") or "0"
    try:
        longueur = max(0, int(brut))
    except ValueError:
        longueur = 0
    if longueur == 0:
        return b""
    flux = environ.get("wsgi.input")
    if flux is None:
        return b""
    return flux.read(longueur)


class _RequeteWSGI(DashboardHandler):
    """Une requête WSGI présentée au handler comme si elle arrivait du réseau.

    On n'appelle **pas** ``BaseHTTPRequestHandler.__init__`` : celui-ci
    construit ses flux depuis une socket et boucle sur ``handle()``. Ici les
    flux sont déjà prêts et il n'y a qu'une requête à traiter.
    """

    def __init__(self, environ: dict[str, Any]) -> None:
        self.environ = environ
        # Attributs que ``__init__`` d'origine aurait posés ou qui sont lus
        # avant ``parse_request`` : on les initialise pour qu'aucun chemin
        # d'erreur (requête malformée) ne tombe sur un attribut manquant.
        self.command = environ.get("REQUEST_METHOD", "GET")
        self.request_version = "HTTP/1.1"
        self.requestline = ""
        self.close_connection = True
        self.rfile = io.BytesIO(_requete_brute(environ))
        self.wfile = io.BytesIO()
        self._statut = "500 Internal Server Error"
        self._entetes: list[tuple[str, str]] = []

    # ── interception des en-têtes ──────────────────────────────────────────
    def flush_headers(self) -> None:
        """Capture ce que le handler croyait écrire sur le réseau.

        ``BaseHTTPRequestHandler`` sérialise statut et en-têtes dans
        ``_headers_buffer`` puis les pousse vers ``wfile``. On vide ce tampon
        avant qu'il n'atteigne le corps : sinon la ligne « HTTP/1.1 200 OK »
        se retrouverait collée au début du HTML.
        """
        tampon = getattr(self, "_headers_buffer", None)
        if not tampon:
            return
        self._headers_buffer = []
        texte = b"".join(tampon).decode("iso-8859-1", "replace")
        lignes = [ligne for ligne in texte.split("\r\n") if ligne]
        if lignes and lignes[0].upper().startswith("HTTP/"):
            # « HTTP/1.1 200 OK » → statut « 200 OK » au format WSGI, c'est-à-dire
            # le code *et* le libellé, le protocole en moins.
            parties = lignes[0].split(None, 1)
            if len(parties) == 2 and parties[1].strip():
                self._statut = parties[1].strip()
            lignes = lignes[1:]
        self._entetes = [
            (nom.strip(), valeur.strip())
            for nom, _, valeur in (ligne.partition(":") for ligne in lignes)
            if nom.strip()
        ]

    def end_headers(self) -> None:
        """Même rôle que la méthode d'origine, sans la ligne vide finale."""
        if self.request_version != "HTTP/0.9":
            if not hasattr(self, "_headers_buffer"):
                self._headers_buffer = []
            self.flush_headers()

    # ── habillage minimal ──────────────────────────────────────────────────
    @property
    def client_address(self) -> tuple[str, int]:
        return (str(self.environ.get("REMOTE_ADDR", "")), 0)

    def address_string(self) -> str:
        return str(self.environ.get("REMOTE_ADDR", "-"))


def creer_application() -> Callable[[dict[str, Any], Any], list[bytes]]:
    """Fabrique l'application WSGI (une seule instance suffit par processus)."""

    def application(environ: dict[str, Any], start_response: Any) -> list[bytes]:
        requete = _RequeteWSGI(environ)
        try:
            requete.handle_one_request()
        except Exception:  # noqa: BLE001 - on doit répondre, pas propager
            # Le serveur WSGI doit toujours recevoir une réponse ; sans quoi
            # l'hébergeur renvoie un 502 opaque. La trace part dans les
            # journaux de la plateforme, jamais dans la réponse.
            traceback.print_exc(file=sys.stderr)
            start_response("500 Internal Server Error",
                           [("Content-Type", "text/plain; charset=utf-8"),
                            ("Content-Length", str(len(_MESSAGE_ERREUR)))])
            return [_MESSAGE_ERREUR]

        entetes = [(nom, valeur) for nom, valeur in requete._entetes
                   if nom.lower() not in _ENTETES_HOP_BY_HOP]
        corps = requete.wfile.getvalue()
        # Un corps présent sans Content-Length est illégal en HTTP/1.1 : le
        # handler le fixe toujours, mais on garantit le cas d'un handler tiers.
        if corps and not any(nom.lower() == "content-length" for nom, _ in entetes):
            entetes.append(("Content-Length", str(len(corps))))
        start_response(requete._statut, entetes)
        return [corps]

    return application


#: Point d'entrée attendu par gunicorn / uWSGI / waitress :
#: ``gunicorn simulateur.wsgi:application``.
application = creer_application()
