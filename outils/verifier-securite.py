#!/usr/bin/env python3
"""Tests de non-régression ciblés pour les frontières de sécurité du simulateur.

Contrôles déterministes, sans accès réseau externe : provenance navigateur,
absence de mutation du cache commun, limites HTTP/WSGI et whitelist statique.

Usage : python3 outils/verifier-securite.py
"""
from __future__ import annotations

import http.client
import importlib.util
import io
import json
import os
import shutil
import subprocess
import sys
import tempfile
import threading
import time
from functools import partial
import urllib.error
import urllib.request
from http.server import ThreadingHTTPServer
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RACINE))

from simulateur import dashboard, donnees_live, marches  # noqa: E402
from simulateur.donnees_live import INDICATEURS, construire_contexte  # noqa: E402
from simulateur.wsgi import application as application_wsgi  # noqa: E402


class EchecVerification(AssertionError):
    pass


def verifier(condition: bool, message: str) -> None:
    if not condition:
        raise EchecVerification(message)
    print(f"OK  {message}")


def demander(url: str, methode: str = "GET", corps: bytes | None = None) -> tuple[int, bytes, dict[str, str]]:
    derniere_erreur: Exception | None = None
    for tentative in range(2):
        requete = urllib.request.Request(url, data=corps, method=methode)
        if corps is not None:
            requete.add_header("Content-Type", "application/json")
        try:
            with urllib.request.urlopen(requete, timeout=10) as reponse:
                return reponse.status, reponse.read(), dict(reponse.headers.items())
        except urllib.error.HTTPError as erreur:
            return erreur.code, erreur.read(), dict(erreur.headers.items())
        except (urllib.error.URLError, OSError) as erreur:
            derniere_erreur = erreur
            if tentative == 0:
                continue
    return 0, str(derniere_erreur or "erreur HTTP locale").encode("utf-8"), {}


def test_configuration_vercel() -> None:
    configuration = json.loads((RACINE / "vercel.json").read_text(encoding="utf-8"))
    regles = configuration.get("headers", [])
    en_tetes = {
        entree["key"]: entree["value"]
        for regle in regles
        for entree in regle.get("headers", [])
    }
    attendus = {
        "X-Content-Type-Options": "nosniff",
        "Referrer-Policy": "strict-origin-when-cross-origin",
        "Strict-Transport-Security": "max-age=31536000",
        "X-Frame-Options": "SAMEORIGIN",
        "Permissions-Policy": "camera=(), microphone=(), geolocation=()",
        "Content-Security-Policy": "base-uri 'self'; object-src 'none'; frame-ancestors 'self'; form-action 'self'",
    }
    verifier(
        en_tetes == attendus and len(regles) == 1 and regles[0].get("source") == "/(.*)",
        "les en-têtes globaux Vercel correspondent à la configuration auditée",
    )
    limites = configuration.get("functions", {}).get("api/*.py", {})
    verifier(
        limites == {"maxDuration": 60, "memory": 1024}
        and "script-src" not in en_tetes["Content-Security-Policy"],
        "durée/mémoire Vercel et limite CSP inline conformes aux réserves du rapport",
    )


def test_workflows_ci() -> None:
    repertoire = RACINE / ".github" / "workflows"
    references = [
        ligne.split("uses:", 1)[1].strip().split()[0]
        for chemin in sorted(repertoire.glob("*.yml"))
        for ligne in chemin.read_text(encoding="utf-8").splitlines()
        if "uses:" in ligne
    ]
    verifier(
        bool(references) and all(
            len(reference.rsplit("@", 1)[-1]) == 40
            and all(caractere in "0123456789abcdef" for caractere in reference.rsplit("@", 1)[-1].lower())
            for reference in references
        ),
        "les actions GitHub sont épinglées sur des révisions immuables",
    )
    ci = (repertoire / "verification.yml").read_text(encoding="utf-8")
    verifier(
        "pull_request:" in ci
        and "python3 outils/verifier-securite.py" in ci
        and "python3 outils/verifier-integration.py" in ci
        and "permissions:\n  contents: read" in ci,
        "la CI en lecture seule vérifie sécurité et intégration sur chaque pull request",
    )


def test_source_externe_bornee() -> None:
    ancienne_opener = donnees_live._OPENER

    class Reponse:
        def __init__(self, contenu: bytes, entetes: dict[str, str]) -> None:
            self.contenu = contenu
            self.headers = entetes
            self.limite_lue = None

        def __enter__(self):
            return self

        def __exit__(self, *_args) -> None:
            return None

        def read(self, limite: int) -> bytes:
            self.limite_lue = limite
            return self.contenu[:limite]

    class Opener:
        def __init__(self, reponse: Reponse) -> None:
            self.reponse = reponse

        def open(self, *_args, **_kwargs) -> Reponse:
            return self.reponse

    try:
        reponse_annoncee = Reponse(
            b"ne pas lire", {"Content-Length": str(donnees_live.MAX_SOURCE_RESPONSE_BYTES + 1)}
        )
        donnees_live._OPENER = Opener(reponse_annoncee)
        try:
            donnees_live._http_texte("https://source.example/test")
            refuse_annonce = False
        except donnees_live.ErreurSource:
            refuse_annonce = True
        verifier(refuse_annonce and reponse_annoncee.limite_lue is None,
                 "une réponse source trop grande annoncée est refusée avant lecture")

        reponse_reelle = Reponse(
            b"x" * (donnees_live.MAX_SOURCE_RESPONSE_BYTES + 100), {}
        )
        donnees_live._OPENER = Opener(reponse_reelle)
        try:
            donnees_live._http_texte("https://source.example/test")
            refuse_flux = False
        except donnees_live.ErreurSource:
            refuse_flux = True
        verifier(
            refuse_flux and reponse_reelle.limite_lue == donnees_live.MAX_SOURCE_RESPONSE_BYTES + 1,
            "une réponse source sans longueur fiable reste bornée à 8 Mio + 1 octet de détection",
        )

        reponse_valide = Reponse(b"{}", {"Content-Length": "2"})
        donnees_live._OPENER = Opener(reponse_valide)
        verifier(
            donnees_live._http_texte("https://source.example/test") == "{}",
            "une réponse source courte valide reste lisible",
        )
    finally:
        donnees_live._OPENER = ancienne_opener

    redirecteur = next(
        (handler for handler in ancienne_opener.handlers
         if isinstance(handler, donnees_live._SansRedirection)),
        None,
    )
    verifier(
        redirecteur is not None
        and redirecteur.redirect_request(None, None, 302, "Found", {}, "http://127.0.0.1/") is None,
        "le client de données publiques refuse les redirections vers une cible arbitraire",
    )


def test_cotations_bornees() -> None:
    ancien_opener = marches._OPENER

    class Reponse:
        def __init__(self, contenu: bytes, entetes: dict[str, str]) -> None:
            self.contenu = contenu
            self.headers = entetes
            self.limite_lue = None

        def __enter__(self):
            return self

        def __exit__(self, *_args) -> None:
            return None

        def read(self, limite: int) -> bytes:
            self.limite_lue = limite
            return self.contenu[:limite]

    class Opener:
        def __init__(self, reponse: Reponse) -> None:
            self.reponse = reponse

        def open(self, *_args, **_kwargs) -> Reponse:
            return self.reponse

    try:
        annoncee = Reponse(
            b"ne pas lire", {"Content-Length": str(marches.MAX_COTATION_RESPONSE_BYTES + 1)}
        )
        marches._OPENER = Opener(annoncee)
        try:
            marches._lire_cotation(marches.MARCHES_ACTIONS[0])
            refuse_annonce = False
        except ValueError:
            refuse_annonce = True
        verifier(refuse_annonce and annoncee.limite_lue is None,
                 "une réponse Yahoo trop volumineuse annoncée est refusée avant lecture")

        sans_taille = Reponse(b"x" * (marches.MAX_COTATION_RESPONSE_BYTES + 100), {})
        marches._OPENER = Opener(sans_taille)
        try:
            marches._lire_cotation(marches.MARCHES_ACTIONS[0])
            refuse_flux = False
        except ValueError:
            refuse_flux = True
        verifier(
            refuse_flux and sans_taille.limite_lue == marches.MAX_COTATION_RESPONSE_BYTES + 1,
            "le flux de cotations reste borné à un Mio + 1 octet de détection",
        )

        payload = json.dumps({"chart": {"result": [{"meta": {
            "regularMarketPrice": 100.5,
            "regularMarketTime": int(time.time()),
            "currency": "EUR",
            "exchangeTimezoneName": "Europe/Paris",
        }}]}}).encode("utf-8")
        valide = Reponse(payload, {"Content-Length": str(len(payload))})
        marches._OPENER = Opener(valide)
        cotation = marches._lire_cotation(marches.MARCHES_ACTIONS[0])
        verifier(cotation["cours"] == 100.5 and cotation["nom"] == "CAC 40",
                 "une cotation courte et correctement formée reste exploitable")
    finally:
        marches._OPENER = ancien_opener

    redirecteur = next(
        (handler for handler in ancien_opener.handlers
         if isinstance(handler, marches._SansRedirection)),
        None,
    )
    verifier(
        redirecteur is not None
        and redirecteur.redirect_request(None, None, 302, "Found", {}, "http://127.0.0.1/") is None,
        "le flux de marché refuse les redirections HTTP",
    )
    verifier(marches._nombre(float("inf")) is None,
             "les nombres non finis reçus du fournisseur sont rejetés")


def test_donnees_navigateur() -> None:
    ancienne_valeur = dashboard._CONTEXTE_CACHE.get("contexte")
    contexte_base = construire_contexte(lectures={})
    dashboard._CONTEXTE_CACHE["contexte"] = contexte_base
    indicateur = INDICATEURS["eur_usd"]
    source = indicateur.sources[0]
    marqueurs = ("<img src=x onerror=alert(1)>", "<svg/onload=alert(2)>", "<script>alert(3)</script>")
    lecture_brute = {
        "valeur": 1.2345,
        "url": source.url,
        "fournisseur": marqueurs[0],
        "periode": marqueurs[1],
        "detail": marqueurs[2],
        "statut": "live",
        "qualite_code": marqueurs[1],
    }
    try:
        lectures = dashboard._lectures_navigateur_sures({"eur_usd": lecture_brute})
        lecture = lectures["eur_usd"]
        verifier(lecture.fournisseur == source.fournisseur, "la provenance fournisseur vient du registre")
        verifier(lecture.url == source.url, "l’URL doit correspondre exactement à une source déclarée")
        verifier(lecture.periode is None, "les périodes contenant du balisage sont rejetées")
        verifier(lecture.detail == "lecture navigateur — provenance déclarée au registre",
                 "les détails libres du client ne sont pas conservés")
        verifier(lecture.qualite_code is None, "les marqueurs qualité invalides sont écartés")
        verifier(not dashboard._lectures_navigateur_sures({
            "eur_usd": {**lecture_brute, "url": "javascript:alert(1)"},
            "indicateur_inconnu": lecture_brute,
            "inflation_france_pct": {**lecture_brute, "valeur": "NaN"},
        }), "URL non déclarée, clé inconnue et valeur non finie sont refusées")

        resultat = dashboard.enregistrer_donnees_navigateur({"eur_usd": lecture_brute})
        provenance = resultat["contexte"]["provenance"]["eur_usd"]
        verifier(resultat["contexte"]["eur_usd"] == 1.2345, "la valeur validée ne s’applique qu’au contexte retourné")
        verifier(provenance["source"] == source.fournisseur and provenance["url"] == source.url,
                 "la provenance retournée ne reprend pas les métadonnées du client")
        charge = json.dumps(resultat, ensure_ascii=False)
        verifier(all(marqueur not in charge for marqueur in marqueurs),
                 "aucune chaîne XSS fournie par le client ne ressort dans la réponse")
        verifier(dashboard._CONTEXTE_CACHE["contexte"] is contexte_base,
                 "la requête ne remplace pas le contexte partagé entre visiteurs")
        verifier(dashboard._CONTEXTE_CACHE["contexte"].eur_usd != 1.2345,
                 "la valeur navigateur n’empoisonne pas la session suivante")
    finally:
        dashboard._CONTEXTE_CACHE["contexte"] = ancienne_valeur


def test_provenance_externe_sure() -> None:
    marqueurs = ("<img src=x onerror=alert(1)>", "<svg/onload=alert(2)>", "<script>alert(3)</script>")
    verifier(donnees_live._periode_sure("2026-Q3") == "2026-Q3"
             and donnees_live._periode_sure(marqueurs[0]) is None,
             "les périodes externes gardent leur forme simple et rejettent le balisage")
    verifier(donnees_live._code_qualite_sure("p") == "p"
             and donnees_live._code_qualite_sure(marqueurs[2]) is None
             and donnees_live.libelle_qualite(marqueurs[2]) == "aucun marqueur fourni par la source",
             "les codes qualité externes sont courts, validés et inertes")
    verifier(donnees_live.qualite_eurostat({"status": {"0": "e"}}, "0") == "e"
             and donnees_live.qualite_eurostat({"status": {"0": marqueurs[1]}}, "0") is None,
             "l'adaptateur Eurostat n'accepte pas de balisage dans le marqueur qualité")

    source = INDICATEURS["eur_usd"].sources[0]
    verifier(donnees_live._plage_valeur_sure(INDICATEURS["eur_usd"], 1.1)
             and not donnees_live._plage_valeur_sure(INDICATEURS["eur_usd"], float("inf"))
             and not donnees_live._plage_valeur_sure(INDICATEURS["eur_usd"], 1e20),
             "les valeurs source et cache doivent rester finies et dans une plage plausible")
    ancienne_lecture_source = donnees_live._lire_source
    try:
        donnees_live._lire_source = lambda *_args, **_kwargs: donnees_live.Lecture(
            cle="eur_usd", valeur=float("inf"), periode="2026-10",
            fournisseur=source.fournisseur, url=source.url, statut="live",
        )
        repli = donnees_live.interroger("eur_usd")
    finally:
        donnees_live._lire_source = ancienne_lecture_source
    verifier(repli.statut == "reference" and repli.valeur is not None
             and donnees_live._plage_valeur_sure(INDICATEURS["eur_usd"], repli.valeur),
             "une valeur fournisseur non finie est écartée au profit de la référence datée")
    lecture_brute = {
        "cle": "eur_usd",
        "valeur": 1.1,
        "periode": marqueurs[0],
        "fournisseur": marqueurs[2],
        "url": source.url,
        "statut": "live",
        "detail": "cache historique",
        "qualite_code": marqueurs[1],
        "horodatage": marqueurs[0],
    }
    with tempfile.TemporaryDirectory(prefix="mrsc-cache-provenance-") as temporaire:
        chemin = Path(temporaire) / "cache.json"
        chemin.write_text(json.dumps({"lectures": {"eur_usd": lecture_brute}}), encoding="utf-8")
        lectures = donnees_live.charger_cache(chemin)
    lecture = lectures["eur_usd"]
    verifier(lecture.periode is None and lecture.qualite_code is None,
             "les métadonnées dangereuses d'un cache ancien sont neutralisées")
    verifier(lecture.fournisseur == source.fournisseur and lecture.url == source.url
             and all(marqueur not in lecture.horodatage for marqueur in marqueurs),
             "le cache reprend la provenance du registre et normalise ses dates")
    contexte = construire_contexte(lectures=lectures)
    provenance = contexte.provenance["eur_usd"]
    verifier(provenance["periode"] is None and provenance["qualite_code"] is None
             and all(marqueur not in json.dumps(provenance, ensure_ascii=False) for marqueur in marqueurs),
             "le contexte public ne relaie pas de période ou qualité de cache non fiable")


def test_http_et_erreurs() -> None:
    ancien_contexte = dashboard._CONTEXTE_CACHE.get("contexte")
    ancienne_collecte = donnees_live.collecter
    ancienne_lecture_cache = dashboard.charger_cache
    ancienne_interrogation = dashboard.interroger
    anciennes_cotations = dashboard.obtenir_cotations
    ancienne_catalogue_bulles = dashboard.catalogue_bulles
    ancien_cache_bulles = dict(dashboard._CACHE_BULLES)
    ancien_bulles_en_cours = dashboard._BULLES_EN_COURS
    ancien_cache_proxy = dict(dashboard._CACHE_PROXY)
    ancien_cache_marches = dashboard._CACHE_MARCHES_API
    ancienne_variable = os.environ.pop("SIMULATEUR_LOG_ERREURS", None)
    dashboard._CONTEXTE_CACHE["contexte"] = None
    serveur = dashboard.create_server("127.0.0.1", 0)
    fil = threading.Thread(target=serveur.serve_forever, daemon=True)
    fil.start()
    base = f"http://127.0.0.1:{serveur.server_address[1]}"
    try:
        def collecte_interdite(*_args, **_kwargs):
            raise AssertionError("collecte réseau inattendue")

        dashboard.charger_cache = lambda: {}
        donnees_live.collecter = collecte_interdite
        statut, contenu, _ = demander(base + "/api/contexte?refresh=1")
        verifier(statut == 200, "un refresh GET à froid ne déclenche aucune collecte réseau")
        query_surchargee = "&".join(f"champ{i}=1" for i in range(dashboard.MAX_QUERY_FIELDS + 1))
        statut_query, _, _ = demander(base + "/?" + query_surchargee)
        verifier(statut_query == 400, "une URL avec trop de champs de requête est refusée")
        cible_trop_longue = "/?q=" + ("x" * dashboard.MAX_REQUEST_TARGET_BYTES)
        statut_cible, _, _ = demander(base + cible_trop_longue)
        verifier(statut_cible == 414, "une cible HTTP trop longue est refusée avant le routage")
        dashboard.charger_cache = ancienne_lecture_cache
        donnees_live.collecter = ancienne_collecte

        indicateur = INDICATEURS["eur_usd"]
        source = indicateur.sources[0]
        charge = json.dumps({"lectures": {"eur_usd": {
            "valeur": 1.2345,
            "url": source.url,
            "fournisseur": "<script>forged</script>",
            "periode": "<svg/onload=alert(1)>",
        }}}).encode("utf-8")
        statut, contenu, _ = demander(base + "/api/donnees", "POST", charge)
        resultat = json.loads(contenu)
        verifier(statut == 200 and resultat["lectures"]["eur_usd"]["fournisseur"] == source.fournisseur,
                 "la route POST /api/donnees applique la validation serveur")
        statut, contenu, _ = demander(base + "/api/contexte")
        contexte_suivant = json.loads(contenu)["contexte"]
        verifier(statut == 200 and contexte_suivant["eur_usd"] != 1.2345,
                 "une lecture POST ne modifie pas le contexte servi au visiteur suivant")

        statut, contenu, entetes = demander(
            base + "/api/donnees", "POST",
            b"x" * (dashboard.MAX_REQUEST_BODY_BYTES + 1),
        )
        verifier(statut == 413 and b"trop volumineux" in contenu.lower(),
                 "le serveur HTTP refuse un corps de plus de 1 Mio")
        verifier(entetes.get("X-Content-Type-Options") == "nosniff",
                 "les réponses API déclarent X-Content-Type-Options")

        def requete_malveillante(entetes: list[tuple[str, str]], corps: bytes) -> int:
            connexion = http.client.HTTPConnection("127.0.0.1", serveur.server_address[1], timeout=10)
            try:
                connexion.putrequest("POST", "/api/donnees")
                for nom, valeur in entetes:
                    connexion.putheader(nom, valeur)
                connexion.endheaders(corps)
                reponse = connexion.getresponse()
                reponse.read()
                return reponse.status
            finally:
                connexion.close()

        statut_cl = requete_malveillante(
            [("Content-Length", "2"), ("Content-Length", "2")], b"{}"
        )
        statut_te = requete_malveillante([("Transfer-Encoding", "chunked")], b"0\r\n\r\n")
        verifier(statut_cl == statut_te == 400,
                 "les longueurs dupliquées et Transfer-Encoding sont rejetés")

        indicateur = INDICATEURS["eur_usd"]
        source = indicateur.sources[0]
        appels_proxy = []
        dashboard._CACHE_PROXY.clear()
        dashboard.interroger = lambda cle, timeout=12.0: (
            appels_proxy.append(cle) or dashboard.Lecture(
                cle=cle, valeur=1.2345, periode="2026-10", fournisseur=source.fournisseur,
                url=source.url, statut="live",
            )
        )
        statut1, _, _ = demander(base + "/api/proxy?indicateur=eur_usd")
        statut2, _, _ = demander(base + "/api/proxy?indicateur=eur_usd")
        verifier(statut1 == statut2 == 200 and appels_proxy == ["eur_usd"],
                 "le relais externe met chaque indicateur en cache et évite les appels redondants")
        dashboard._CACHE_PROXY.clear()
        dashboard._VERROU_PROXY.acquire()
        try:
            statut_occupe, _, _ = demander(base + "/api/proxy?indicateur=eur_usd")
        finally:
            dashboard._VERROU_PROXY.release()
        verifier(statut_occupe == 503 and appels_proxy == ["eur_usd"],
                 "un relais déjà occupé refuse une nouvelle collecte sans bloquer un thread")

        cle_bulle = next(iter(dashboard.LEVIERS))
        appels_bulles = []
        dashboard.catalogue_bulles = lambda _contexte, *, cles=None, avec_mesure=True, detail="resume": (
            appels_bulles.append(cles) or {"bulles": {}}
        )
        statut_bulles, _, _ = demander(
            base + f"/api/bulles?levier={cle_bulle},{cle_bulle}&mesure=0"
        )
        verifier(statut_bulles == 200 and appels_bulles == [[cle_bulle]],
                 "les clés répétées du catalogue de bulles sont dédupliquées")
        dashboard.catalogue_bulles = ancienne_catalogue_bulles
        dashboard._CACHE_BULLES.clear()
        dashboard._BULLES_EN_COURS = True
        try:
            statut_bulles_occupe, _, _ = demander(
                base + f"/api/bulles?levier={cle_bulle}&mesure=0"
            )
        finally:
            dashboard._BULLES_EN_COURS = ancien_bulles_en_cours
            dashboard._CACHE_BULLES.clear()
            dashboard._CACHE_BULLES.update(ancien_cache_bulles)
        verifier(statut_bulles_occupe == 503,
                 "un calcul de bulles concurrent est refusé rapidement avec HTTP 503")

        appels_marches = []
        dashboard._CACHE_MARCHES_API = None
        dashboard.obtenir_cotations = lambda *, actualiser=True: (
            appels_marches.append(actualiser) or {"indices": [], "date_interrogation_utc": "test"}
        )
        statut1, _, _ = demander(base + "/api/marches?refresh=1")
        statut2, corps2, _ = demander(base + "/api/marches?refresh=1")
        verifier(statut1 == statut2 == 200 and appels_marches == [True]
                 and json.loads(corps2).get("rafraichissement_limite") is True,
                 "les rafraîchissements répétés des marchés sont limités à une minute")
        dashboard._CACHE_MARCHES_API = None
        dashboard._VERROU_MARCHES_API.acquire()
        try:
            statut_marches_occupe, _, _ = demander(base + "/api/marches?refresh=1")
        finally:
            dashboard._VERROU_MARCHES_API.release()
        verifier(statut_marches_occupe == 503 and appels_marches == [True],
                 "un rafraîchissement marché concurrent échoue vite au lieu d’empiler des threads")

        dashboard._CACHE_PROXY.clear()
        def erreur_privee(*_args, **_kwargs):
            raise RuntimeError("TRACE_PRIVEE_NE_PAS_EXPOSER")

        dashboard.interroger = erreur_privee
        statut, contenu, _ = demander(base + "/api/proxy?indicateur=eur_usd")
        verifier(statut == 500 and b"TRACE_PRIVEE_NE_PAS_EXPOSER" not in contenu
                 and b"Traceback" not in contenu,
                 "une exception serveur renvoie une erreur générique, sans traceback")
    finally:
        dashboard.interroger = ancienne_interrogation
        dashboard.obtenir_cotations = anciennes_cotations
        dashboard.catalogue_bulles = ancienne_catalogue_bulles
        dashboard._CACHE_BULLES.clear()
        dashboard._CACHE_BULLES.update(ancien_cache_bulles)
        dashboard._BULLES_EN_COURS = ancien_bulles_en_cours
        dashboard._CACHE_PROXY.clear()
        dashboard._CACHE_PROXY.update(ancien_cache_proxy)
        dashboard._CACHE_MARCHES_API = ancien_cache_marches
        dashboard.charger_cache = ancienne_lecture_cache
        donnees_live.collecter = ancienne_collecte
        serveur.shutdown()
        serveur.server_close()
        fil.join(timeout=5)
        dashboard._CONTEXTE_CACHE["contexte"] = ancien_contexte
        if ancienne_variable is not None:
            os.environ["SIMULATEUR_LOG_ERREURS"] = ancienne_variable


def test_wsgi() -> None:
    statut_reponse: list[str] = []
    entetes_reponse: list[list[tuple[str, str]]] = []

    def start_response(statut: str, entetes: list[tuple[str, str]]) -> None:
        statut_reponse.append(statut)
        entetes_reponse.append(entetes)

    maximum = dashboard.MAX_REQUEST_BODY_BYTES
    environ = {
        "REQUEST_METHOD": "POST",
        "SCRIPT_NAME": "",
        "PATH_INFO": "/api/donnees",
        "QUERY_STRING": "",
        "SERVER_NAME": "localhost",
        "SERVER_PORT": "8080",
        "SERVER_PROTOCOL": "HTTP/1.1",
        "REMOTE_ADDR": "127.0.0.1",
        "CONTENT_TYPE": "application/json",
        "CONTENT_LENGTH": str(maximum + 1),
        "wsgi.version": (1, 0),
        "wsgi.url_scheme": "http",
        "wsgi.input": io.BytesIO(b"x" * (maximum + 1)),
        "wsgi.errors": io.StringIO(),
        "wsgi.multithread": True,
        "wsgi.multiprocess": False,
        "wsgi.run_once": False,
    }
    corps = b"".join(application_wsgi(environ, start_response))
    verifier(statut_reponse == ["413 Payload Too Large"] and b"1 Mio" in corps,
             "le pont WSGI applique la même limite de corps HTTP")
    headers = dict(entetes_reponse[0])
    verifier(headers.get("X-Content-Type-Options") == "nosniff",
             "la réponse WSGI trop volumineuse porte les en-têtes de sécurité")

    statut_reponse.clear()
    entetes_reponse.clear()
    environ_chunked = dict(environ)
    environ_chunked.update({
        "CONTENT_LENGTH": "0",
        "HTTP_TRANSFER_ENCODING": "chunked",
        "wsgi.input": io.BytesIO(b"0\r\n\r\n"),
    })
    application_wsgi(environ_chunked, start_response)
    verifier(statut_reponse == ["400 Bad Request"],
             "le pont WSGI refuse aussi Transfer-Encoding non pris en charge")

    statut_reponse.clear()
    entetes_reponse.clear()
    environ_cible_longue = dict(environ)
    environ_cible_longue.update({
        "PATH_INFO": "/api/catalogue",
        "QUERY_STRING": "q=" + "x" * dashboard.MAX_REQUEST_TARGET_BYTES,
        "CONTENT_LENGTH": "0",
        "wsgi.input": io.BytesIO(b""),
    })
    corps_cible_longue = b"".join(application_wsgi(environ_cible_longue, start_response))
    verifier(statut_reponse == ["414 URI Too Long"]
             and b"trop longue" in corps_cible_longue.lower()
             and dict(entetes_reponse[0]).get("X-Content-Type-Options") == "nosniff",
             "le pont WSGI borne la cible avant de reconstruire la requête HTTP")


def test_source_distante() -> None:
    chemin = RACINE / "api" / "verifier-source.py"
    specification = importlib.util.spec_from_file_location("verifier_source_securite", chemin)
    if specification is None or specification.loader is None:
        raise EchecVerification("impossible de charger la sonde de source distante")
    module = importlib.util.module_from_spec(specification)
    specification.loader.exec_module(module)

    ancienne_source = os.environ.get("SIMULATEUR_SOURCE_DISTANTE")
    ancien_mode_test = os.environ.pop("SIMULATEUR_SOURCE_DISTANTE_TEST_LOCALE", None)
    ancienne_lecture = module._lire
    try:
        os.environ["SIMULATEUR_SOURCE_DISTANTE"] = "http://127.0.0.1:9/"
        module._lire = lambda *_args, **_kwargs: (_ for _ in ()).throw(
            AssertionError("la sonde ne doit pas joindre localhost")
        )
        resultat = module.verifier(os.environ["SIMULATEUR_SOURCE_DISTANTE"])
        verifier(resultat["disponible"] is False and resultat["source"] == "",
                 "une cible localhost est refusée sans révéler son adresse")
    finally:
        module._lire = ancienne_lecture
        if ancienne_source is None:
            os.environ.pop("SIMULATEUR_SOURCE_DISTANTE", None)
        else:
            os.environ["SIMULATEUR_SOURCE_DISTANTE"] = ancienne_source
        if ancien_mode_test is not None:
            os.environ["SIMULATEUR_SOURCE_DISTANTE_TEST_LOCALE"] = ancien_mode_test


def test_patch_durabilite() -> None:
    chemin = RACINE / "outils" / "mettre-a-jour-simulateur.py"
    specification = importlib.util.spec_from_file_location("maj_simulateur_securite", chemin)
    if specification is None or specification.loader is None:
        raise EchecVerification("impossible de charger l'outil de mise à jour")
    module = importlib.util.module_from_spec(specification)
    specification.loader.exec_module(module)

    fichiers = ("dashboard.py", "donnees_live.py", "interface.py", "marches.py", "wsgi.py")
    provenance = json.loads((RACINE / "simulateur" / "PROVENANCE.json").read_text(encoding="utf-8"))
    etat_patch = provenance.get("correctif_local", {}).get("etat")
    with tempfile.TemporaryDirectory(prefix="mrsc-test-patch-") as temporaire:
        paquet = Path(temporaire) / "simulateur"
        paquet.mkdir()
        for nom in fichiers:
            shutil.copy2(RACINE / "simulateur" / nom, paquet / nom)

        if etat_patch == "appliqué":
            retrait = subprocess.run(
                ["git", "apply", "--reverse", "--check", str(module.CORRECTIF)],
                cwd=paquet.parent,
                capture_output=True,
                text=True,
                check=False,
            )
            if retrait.returncode != 0:
                raise EchecVerification(
                    "le patch déclaré appliqué ne correspond pas aux sources embarquées : "
                    + retrait.stderr.strip()
                )
            subprocess.run(
                ["git", "apply", "--reverse", str(module.CORRECTIF)],
                cwd=paquet.parent,
                capture_output=True,
                text=True,
                check=True,
            )
            applique = module.appliquer_correctif(paquet)
            verifier(applique is True, "le patch local se réapplique proprement après retrait temporaire")
        elif etat_patch == "déjà intégré à l’amont":
            applique = module.appliquer_correctif(paquet)
            verifier(applique is False, "l’outil détecte le correctif déjà intégré à l’amont")
        else:
            raise EchecVerification(f"état de correctif inconnu dans PROVENANCE.json : {etat_patch!r}")

        verifier(
            all((paquet / nom).read_bytes() == (RACINE / "simulateur" / nom).read_bytes()
                for nom in fichiers),
            "le résultat de mise à jour correspond exactement aux sources moteur conservées",
        )


def test_liste_statique() -> None:
    chemin = RACINE / "outils" / "serveur-local.py"
    specification = importlib.util.spec_from_file_location("serveur_local_securite", chemin)
    if specification is None or specification.loader is None:
        raise EchecVerification("impossible de charger le serveur local")
    module = importlib.util.module_from_spec(specification)
    specification.loader.exec_module(module)
    autorises = (
        RACINE / "index.html",
        RACINE / "assets" / "css" / "site.css",
        RACINE / "apprendre" / "fiches" / "arts-composer-formes.html",
        RACINE / "simulateur" / "index.html",
    )
    interdits = (
        RACINE / "README.md",
        RACINE / "simulateur" / "dashboard.py",
        RACINE / "docs" / "integration-simulateur.md",
        RACINE / ".git" / "HEAD",
    )
    verifier(all(module.ServeurSite._chemin_public(path) for path in autorises),
             "les pages et ressources statiques prévues restent publiables")
    verifier(not any(module.ServeurSite._chemin_public(path) for path in interdits),
             "le serveur local refuse le dépôt, les sources et les fichiers internes")

    class ReponseFausse:
        headers = {"Content-Length": str(module.MAX_RELAY_RESPONSE_BYTES + 1)}

        def read(self, _maximum: int) -> bytes:
            raise AssertionError("une réponse déjà déclarée trop grande ne doit pas être lue")

    try:
        module.lire_reponse_bornee(ReponseFausse())
    except module.ReponseTropVolumineuse:
        trop_grande = True
    else:
        trop_grande = False
    verifier(trop_grande, "le relais local rejette les réponses API supérieures à 16 Mio")

    module.ServeurSite.moteur = None
    module.ServeurSite.fonctions_site = {}
    module.ServeurSite.log_message = lambda *args: None
    serveur = ThreadingHTTPServer(
        ("127.0.0.1", 0), partial(module.ServeurSite, directory=str(RACINE))
    )
    fil = threading.Thread(target=serveur.serve_forever, daemon=True)
    fil.start()
    base = f"http://127.0.0.1:{serveur.server_address[1]}"
    try:
        statut_accueil, accueil, _ = demander(base + "/")
        statut_sim, page_sim, _ = demander(base + "/simulateur/")
        statut_source, source, _ = demander(base + "/simulateur/dashboard.py")
        verifier(statut_accueil == statut_sim == 200 and b"M.R.S.C" in accueil
                 and b"console-pilotage" in page_sim,
                 "le serveur local sert l’accueil et la page intégrée du simulateur")
        verifier(statut_source == 404 and b"from simulateur" not in source,
                 "une requête HTTP ne peut pas lire le code Python du moteur")
    finally:
        serveur.shutdown()
        serveur.server_close()
        fil.join(timeout=5)


def main() -> int:
    print("── Tests de sécurité ciblés (sans réseau externe) ──")
    try:
        test_configuration_vercel()
        test_workflows_ci()
        test_source_externe_bornee()
        test_cotations_bornees()
        test_donnees_navigateur()
        test_provenance_externe_sure()
        test_http_et_erreurs()
        test_wsgi()
        test_source_distante()
        test_patch_durabilite()
        test_liste_statique()
    except Exception as erreur:  # le script doit sortir en erreur lisible pour la CI
        message = f"ÉCHEC {type(erreur).__name__}: {erreur}"
        if os.environ.get("GITHUB_ACTIONS") == "true":
            annotation = message.replace("%", "%25").replace("\r", "%0D").replace("\n", "%0A")
            print(f"::error title=Tests de sécurité::{annotation}", file=sys.stderr)
        print(message, file=sys.stderr)
        return 1
    print("Tous les tests de sécurité ciblés passent.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
