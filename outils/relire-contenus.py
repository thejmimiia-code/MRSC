#!/usr/bin/env python3
"""Sentinelle de relecture : chaque édition doit passer par l'agent.

Le 9 novembre 2026, la consigne a été de rendre la relecture de contenu et la
vérification des sources **automatiques à toutes les éditions**, sans demander
à la personne de lire des milliers de lignes. La personne garde le rendu à
l'œil (placement, style, construction) ; l'agent porte la lecture.

Ce script n'est pas un juge de vérité : un programme ne peut pas décider qu'une
phrase est exacte, ni fabriquer une expertise humaine. Il rend l'étape
**obligatoire et vérifiable** :

1. chaque fichier texte du dépôt est une « unité » dont l'empreinte SHA-256 est
   consignée dans `docs/rd/empreintes-contenus.toml` ;
2. toute édition qui change une empreinte fait échouer la porte tant qu'une
   `[[edition]]` datée, attribuée à l'agent, avec sources ou mesure interne,
   constat et limites, n'a pas été consignée dans
   `docs/rd/relecture-contenus.toml` ;
3. à chaque lancement — donc à chaque `push`, `pull_request`, ou `commit`
   local — la batterie mécanique est rejouée sur tout le corpus : ancres et
   liens locaux des pages HTML, fichiers TOML lisibles, absence de marqueurs de
   brouillon et de conflit, aucune apostrophe droite nouvelle, extraits de
   sources primaires mis en cache et confrontés à leur ancre, fraîcheur des
   dates de consultation, câblage CI + crochet + inventaire, et porte du lot
   `verifier-relecture-contenus.py` ;
4. `docs/apprentissage/relectures.toml` reste le seul registre des relectures
   **humaines** : rien ici n'y écrit, ne promeut une fiche ni n'embellit un
   statut.

Deux modes d'écriture, réservés à l'agent qui a fait la lecture :

    python3 outils/relire-contenus.py --initialiser
    python3 outils/relire-contenus.py --appliquer FICHIER... \
        --nature fait-source --sources mdn-color-scheme,w3c-luminance \
        --constat "..." --limite "..."

`--appliquer` refuse de signer si la batterie mécanique échoue ailleurs, si une
URL externe nouvelle n'est pas couverte par une source primaire enregistrée, ou
si une apostrophe droite apparaît. La CI et le crochet, eux, ne signent jamais :
ils vérifient. Un `--no-verify` local ne contourne pas la CI.

Usage courant : python3 outils/relire-contenus.py
Banc :         MRSC_RACINE=/tmp/copie python3 outils/relire-contenus.py
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import os
import re
import subprocess
import sys
import tomllib
from collections import Counter
from pathlib import Path
from urllib.parse import unquote, urlparse

RACINE = Path(os.environ.get("MRSC_RACINE") or Path(__file__).resolve().parent.parent).resolve()
MANIFESTE = RACINE / "docs" / "rd" / "empreintes-contenus.toml"
REGISTRE = RACINE / "docs" / "rd" / "relecture-contenus.toml"
EDITIONS = RACINE / "docs" / "rd" / "editions-relecture.toml"
DOSSIER_SOURCES = RACINE / "docs" / "rd" / "sources-primaires"
WORKFLOW = RACINE / ".github" / "workflows" / "relecture-contenus.yml"
CI = RACINE / ".github" / "workflows" / "verification.yml"
CROCHET = RACINE / ".githooks" / "pre-commit"
INVENTAIRE = RACINE / "docs" / "rd" / "inventaire-controles.md"
PORTE_LOT = RACINE / "outils" / "verifier-relecture-contenus.py"
REGISTRE_HUMAIN = RACINE / "docs" / "apprentissage" / "relectures.toml"

DATE_LOT = dt.date(2026, 11, 7)
FENETRE_FRAICHEUR = dt.timedelta(days=366)
ETATS = {"reference-initiale", "relu-par-agent", "exempte"}
NATURES = {"fait-source", "mesure-interne", "proposition"}

EXTENSIONS = {
    ".html", ".md", ".toml", ".py", ".js", ".cjs", ".mjs", ".css",
    ".yml", ".yaml", ".json", ".txt", ".xml", ".dot", ".sh", ".patch",
    ".sha256",
}
NOMS_SANS_EXTENSION = {".gitignore", ".vercelignore"}
DOSSIERS_EXCLUS = {
    ".git", "__pycache__", "node_modules", "_site", ".cache", ".venv",
    "dist", "build", "coverage", "Unselected files",
}
#: Le manifeste ne peut pas se signer lui-même ; les extraits de sources sont
#: vérifiés par leur propre empreinte, pas par le mécanisme général.
CHEMINS_EXCLUS = {"docs/rd/empreintes-contenus.toml", "docs/rd/editions-relecture.toml"}
PREFIXES_EXCLUS = ("docs/rd/sources-primaires/",)

#: Sources primaires admises. Les domaines `.gouv.fr` sont ajoutés le
#: 12 novembre 2026 pour le lot « déclarer » : la déclaration d'une fraude se
#: documente auprès des administrations qui la reçoivent, pas ailleurs. La liste
#: reste close — un domaine n'entre ici que pour une source lue, datée et
#: extraite dans `docs/rd/sources-primaires/`. `signal-spam.fr` et `33700.fr`
#: sont les deux plateformes nationales citées par la fiche réflexe de
#: Cybermalveillance ; elles ne sont ni des blogs ni des revendeurs.
DOMAINES_SURS = {
    "developer.mozilla.org", "www.w3.org", "w3.org", "github.com", "api.github.com",
    "www.service-public.gouv.fr", "service-public.fr", "service-public.gouv.fr",
    "www.cybermalveillance.gouv.fr", "cybermalveillance.gouv.fr",
    "www.signal-spam.fr", "signal-spam.fr", "www.33700.fr", "33700.fr",
    # Portail public des données ouvertes : il publie la fiche de licence des
    # jeux de données de l’État (DVF, ADMIN EXPRESS, découpage administratif),
    # qui n’existe nulle part ailleurs. C’est une métadonnée officielle, pas
    # un commentaire tiers.
    "www.data.gouv.fr", "data.gouv.fr", "geo.api.gouv.fr", "www.geo.api.gouv.fr",
    # Plateforme Opendatasoft de l’État : c’est là que vit l’export réellement
    # téléchargé des prix des carburants, distinct de la fiche de licence data.gouv.
    "data.economie.gouv.fr", "www.data.economie.gouv.fr",
}
DOMAINES_PROPRES = {"thejmimiia-code.github.io"}
#: Domaines réservés aux fixtures des bancs de mutation et aux exemples de fiche :
#: `site-fictif.test` est l'adresse d'exercice de la fiche « lire une adresse web »,
#: reproduite à l'identique dans les données d'aventure ; c'est une URL inventée pour
#: planter une faute n'est pas une affirmation sur le monde.
DOMAINES_FICTIFS = {"exemple.test", "exemple.fr", "example.com", "un-blog.test", "site-fictif.test"}
MOTIF_BROUILLON = re.compile(r"\b(TODO|FIXME|Lorem ipsum|XXX)\b", re.I)
MOTIF_CONFLIT = re.compile(r"^(<<<<<<< |>>>>>>> )", re.M)
MOTIF_APOSTROPHE = re.compile(r"\b\w+'\w+\b")
#: Un nom de domaine réel, pas une classe de caractères d'expression
#: régulière : `https://[^\s` dans le code d'un outil n'est pas une URL.
MOTIF_URL = re.compile(r"https://[A-Za-z0-9.-]+(?:/[^\s)\"'>]*)?")
MOTIF_LIEN_TEMPLATE = re.compile(r"\$\{")


def unites() -> list[str]:
    """Tous les fichiers texte du dépôt, triés, hors manifeste et cache."""
    trouvees: set[str] = set()
    for dossier, sous_dossiers, fichiers in os.walk(RACINE, followlinks=True):
        sous_dossiers[:] = sorted(d for d in sous_dossiers if d not in DOSSIERS_EXCLUS)
        for nom in fichiers:
            chemin = Path(dossier) / nom
            try:
                relatif = chemin.relative_to(RACINE).as_posix()
            except ValueError:
                continue
            if relatif in CHEMINS_EXCLUS or relatif.startswith(PREFIXES_EXCLUS):
                continue
            if chemin.suffix in EXTENSIONS or nom in NOMS_SANS_EXTENSION:
                trouvees.add(relatif)
    return sorted(trouvees)


def empreinte(chemin: Path) -> str:
    return hashlib.sha256(chemin.read_bytes()).hexdigest()


def apostrophes(texte: str) -> int:
    return len(MOTIF_APOSTROPHE.findall(texte))


def nombre_apostrophes(relatif: str) -> int:
    if not relatif.endswith((".html", ".md")):
        return 0
    return apostrophes((RACINE / relatif).read_text(encoding="utf-8"))


#: Empreinte d'une unité qui n'existait pas au manifeste précédent. Elle ne
#: peut pas être confondue avec un SHA-256 réel, et `--appliquer` la remplace
#: aussitôt par l'empreinte du fichier écrit.
EMPREINTE_ABSENT = "(absente : unite nouvelle)"


def lire_toml(chemin: Path) -> dict:
    return tomllib.loads(chemin.read_text(encoding="utf-8"))


def date_reference(donnees: dict) -> dt.date:
    """Date la plus récente du registre : aucune horloge système dans la porte."""
    dates = [DATE_LOT]
    meta = donnees.get("meta", {})
    if isinstance(meta.get("date_relecture"), dt.date):
        dates.append(meta["date_relecture"])
    # `dates_lots` porte les lots postérieurs : la date de référence est la plus
    # récente consultation consignée, pas la date du premier lot.
    for brute in meta.get("dates_lots") or []:
        if isinstance(brute, dt.date):
            dates.append(brute)
    return max(dates)


def editions() -> list[dict]:
    """Les éditions relues sont dans un fichier à part, pour éviter qu'une
    écriture ne change l'empreinte du registre qu'elle est en train de signer."""
    if not EDITIONS.is_file():
        return []
    try:
        return lire_toml(EDITIONS).get("edition", [])
    except (tomllib.TOMLDecodeError, OSError):
        return [{"chemin": "?"}]


# ---------------------------------------------------------------------------
# Batterie mécanique, rejouée à chaque édition
# ---------------------------------------------------------------------------

def batterie_mecanique(reel: list[str]) -> list[str]:
    erreurs: list[str] = []
    for relatif in reel:
        chemin = RACINE / relatif
        try:
            texte = chemin.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError) as erreur:
            erreurs.append(f"{relatif} : illisible — {erreur}")
            continue
        if MOTIF_CONFLIT.search(texte):
            erreurs.append(f"{relatif} : marqueur de conflit laissé dans le fichier")
        if relatif.endswith((".html", ".md")):
            for numero, ligne in enumerate(texte.splitlines(), 1):
                if MOTIF_BROUILLON.search(ligne):
                    erreurs.append(f"{relatif}:{numero} : marqueur de brouillon laissé dans un contenu")
        if relatif.endswith(".toml"):
            try:
                tomllib.loads(texte)
            except tomllib.TOMLDecodeError as erreur:
                erreurs.append(f"{relatif} : TOML illisible — {erreur}")
        if relatif.endswith(".html"):
            erreurs.extend(verifier_html(relatif, texte))
    return erreurs


def verifier_html(relatif: str, texte: str) -> list[str]:
    """Ancres internes et cibles locales des pages réellement servies.

    Les six `href="${…}"` de `simulateur/index.html` sont des liens construits
    à l'exécution par le générateur : ils ne sont pas des fichiers du dépôt. Le
    générateur est vérifié séparément par `construire-simulateur.py --verifier`.
    """
    erreurs: list[str] = []
    ids = set(re.findall(r"\bid=[\"']([^\"']+)[\"']", texte))
    for cible in re.findall(r"href=[\"']#([^\"']+)[\"']", texte):
        if unquote(cible) not in ids:
            erreurs.append(f"{relatif} : ancre interne morte #{cible}")
    for attribut in ("href", "src"):
        for cible in re.findall(attribut + r"=[\"']([^\"']+)[\"']", texte):
            if MOTIF_LIEN_TEMPLATE.search(cible):
                continue
            u = urlparse(cible)
            if u.scheme or cible.startswith(("#", "mailto:", "data:", "tel:", "javascript:")):
                continue
            net = unquote(u.path.split("?")[0].split("#")[0])
            if not net:
                continue
            destination = (RACINE / relatif).parent / net
            if not destination.exists():
                erreurs.append(f"{relatif} : {attribut} local introuvable {cible}")
    return erreurs


def verifier_sources(donnees: dict) -> list[str]:
    """Confronte chaque source primaire à son extrait mis en cache, hors ligne."""
    erreurs: list[str] = []
    reference = date_reference(donnees)
    sources = donnees.get("source", [])
    if len(sources) < 5:
        erreurs.append("registre : moins de cinq sources primaires")
    for source in sources:
        identifiant = str(source.get("id", "?"))
        extrait = source.get("extrait")
        if not extrait:
            erreurs.append(f"source {identifiant} : aucun extrait mis en cache (champ « extrait »)")
            continue
        chemin = RACINE / str(extrait)
        if not chemin.is_file() or not chemin.is_relative_to(DOSSIER_SOURCES):
            erreurs.append(f"source {identifiant} : extrait introuvable ou hors dossier dédié : {extrait}")
            continue
        lignes = chemin.read_text(encoding="utf-8").splitlines()
        if "---" not in lignes:
            erreurs.append(f"source {identifiant} : extrait sans séparateur « --- »")
            continue
        coupure = lignes.index("---")
        entete: dict[str, str] = {}
        for ligne in lignes[:coupure]:
            if " = " in ligne:
                cle, valeur = ligne.split(" = ", 1)
                entete[cle.strip()] = valeur.strip()
        corps = "\n".join(lignes[coupure + 1:]).strip()
        if entete.get("id") != identifiant:
            erreurs.append(f"source {identifiant} : l'extrait porte un autre identifiant")
        if entete.get("url") != str(source.get("url", "")):
            erreurs.append(f"source {identifiant} : l'URL de l'extrait ne correspond pas au registre")
        if entete.get("date") != str(source.get("consulte_le", "")):
            erreurs.append(f"source {identifiant} : la date de l'extrait ne correspond pas au registre")
        if hashlib.sha256(corps.encode("utf-8")).hexdigest() != entete.get("empreinte"):
            erreurs.append(f"source {identifiant} : l'extrait a été modifié depuis sa consultation")
        ancre = str(source.get("ancre", ""))
        if ancre and ancre not in corps:
            erreurs.append(f"source {identifiant} : ancre absente de l'extrait : {ancre!r}")
        if len(corps) < 60 or len(corps) > 2500:
            erreurs.append(f"source {identifiant} : extrait d'une longueur invraisemblable ({len(corps)} caractères)")
        consultee = source.get("consulte_le")
        if not isinstance(consultee, dt.date):
            erreurs.append(f"source {identifiant} : date de consultation absente ou illisible")
        elif consultee > reference or reference - consultee > FENETRE_FRAICHEUR:
            erreurs.append(
                f"source {identifiant} : consultation du {consultee} trop ancienne "
                f"ou postérieure à la dernière relecture du {reference} — reconfirmer la page"
            )
        domaine = urlparse(str(source.get("url", ""))).netloc.lower()
        if domaine not in DOMAINES_SURS:
            erreurs.append(f"source {identifiant} : domaine non retenu comme primaire : {domaine}")
    return erreurs


def verifier_cablage() -> list[str]:
    erreurs: list[str] = []
    if not WORKFLOW.is_file():
        erreurs.append("workflow dédié absent : .github/workflows/relecture-contenus.yml")
    else:
        texte = WORKFLOW.read_text(encoding="utf-8")
        for morceau, raison in (
            ("relire-contenus.py", "la sentinelle doit être lancée"),
            ("push:", "le déclenchement sur chaque push doit exister"),
            ("pull_request:", "le déclenchement sur chaque PR doit exister"),
            ("branches: ['**']", "toutes les branches doivent être couvertes"),
            ("ubuntu-24.04", "le runner doit être épinglé"),
        ):
            if morceau not in texte:
                erreurs.append(f"workflow dédié : {raison} ({morceau!r} absent)")
    if not CI.is_file() or "relire-contenus.py" not in CI.read_text(encoding="utf-8"):
        erreurs.append("CI principale : la sentinelle n'est pas câblée")
    if not CROCHET.is_file():
        erreurs.append("crochet pre-commit absent : .githooks/pre-commit")
    else:
        if not os.access(CROCHET, os.X_OK):
            erreurs.append("crochet pre-commit non exécutable : la relecture locale pourrait être contournée sans le dire")
        if "relire-contenus.py" not in CROCHET.read_text(encoding="utf-8"):
            erreurs.append("crochet pre-commit : la sentinelle n'est pas appelée")
    inventaire = INVENTAIRE.read_text(encoding="utf-8") if INVENTAIRE.is_file() else ""
    for outil in ("relire-contenus.py", "test_mutations_relire_contenus.py"):
        if outil not in inventaire:
            erreurs.append(f"inventaire : {outil} n'est pas recensé")
    if not PORTE_LOT.is_file():
        erreurs.append("porte du lot absente : outils/verifier-relecture-contenus.py")
    if REGISTRE_HUMAIN.is_file():
        try:
            humaines = lire_toml(REGISTRE_HUMAIN)
        except tomllib.TOMLDecodeError as erreur:
            erreurs.append(f"relectures.toml illisible : {erreur}")
        else:
            if humaines.get("relecture"):
                erreurs.append("relectures.toml contient une entrée : une relecture d'agent ne doit jamais y écrire")
    return erreurs


def verifier(exceptions: set[str] | None = None) -> list[str]:
    """Toutes les vérifications. `exceptions` ne sert qu'à `--appliquer`."""
    exceptions = exceptions or set()
    erreurs: list[str] = []
    if not MANIFESTE.is_file():
        return ["manifeste d'empreintes absent : docs/rd/empreintes-contenus.toml — lancer --initialiser"]
    if not REGISTRE.is_file():
        return ["registre de relecture par agent absent : docs/rd/relecture-contenus.toml"]
    try:
        manifeste = lire_toml(MANIFESTE)
        donnees = lire_toml(REGISTRE)
    except (tomllib.TOMLDecodeError, OSError) as erreur:
        return [f"registre ou manifeste illisible : {erreur}"]

    meta = manifeste.get("meta", {})
    if meta.get("version") != 1:
        erreurs.append("manifeste : version attendue : 1")
    if meta.get("auteur") != "agent":
        erreurs.append("manifeste : auteur doit être « agent » (jamais une personne)")
    if not meta.get("limite_reference"):
        erreurs.append("manifeste : la dette de relecture initiale doit être écrite noir sur blanc")

    reel = unites()
    declares: dict[str, dict] = {}
    for unite in manifeste.get("unite", []):
        chemin = str(unite.get("chemin", ""))
        if chemin in declares:
            erreurs.append(f"manifeste : unité déclarée deux fois : {chemin}")
        declares[chemin] = unite

    editions_relues_chemins = {str(e.get("chemin")) for e in editions()}
    # Une unité nouvelle n'est pas une faute : elle n'a simplement pas encore
    # d'empreinte. Elle est refusée seulement si aucune [[edition]] ne la couvre,
    # ce que le contrôle des éditions ci-dessous fait déjà. Le message qui
    # envoyait vers `--initialiser --forcer` était un piège : ce mode réécrit
    # tout le manifeste et remet les 176 relectures consignées en dette.
    for chemin in sorted(set(reel) - set(declares)):
        # `exceptions` porte les chemins que `--appliquer` est en train de
        # signer : ils ne sont pas encore au manifeste, c'est normal.
        if chemin in exceptions:
            continue
        if chemin not in editions_relues_chemins:
            erreurs.append(
                f"unité non enregistrée : {chemin} — la consigner par "
                "--appliquer avec son constat et sa limite"
            )
    for chemin in sorted(set(declares) - set(reel)):
        erreurs.append(f"unité déclarée mais absente du dépôt : {chemin}")

    editions_relues = editions()
    for chemin, unite in declares.items():
        if chemin not in reel:
            continue
        fichier = RACINE / chemin
        actuelle = empreinte(fichier)
        etat = unite.get("etat")
        if etat not in ETATS:
            erreurs.append(f"{chemin} : état inconnu : {etat}")
        if chemin not in exceptions and unite.get("empreinte") != actuelle:
            erreurs.append(
                f"édition non relue : {chemin} — relire le contenu, confronter les sources, "
                "puis consigner avec --appliquer"
            )
        if etat == "relu-par-agent":
            if not unite.get("date_derniere_relecture"):
                erreurs.append(f"{chemin} : relecture d'agent sans date")
            if not any(
                e.get("chemin") == chemin and e.get("empreinte_apres") == unite.get("empreinte")
                for e in editions_relues
            ):
                erreurs.append(f"{chemin} : aucune [[edition]] ne couvre l'empreinte consignée")
        if etat == "reference-initiale" and not unite.get("date_reference"):
            erreurs.append(f"{chemin} : référence initiale sans date")
        if etat == "exempte" and not unite.get("raison"):
            erreurs.append(f"{chemin} : exemption sans raison écrite")
        if chemin not in exceptions and chemin.endswith((".html", ".md")):
            compte = nombre_apostrophes(chemin)
            if compte > int(unite.get("apostrophes", 0)):
                erreurs.append(
                    f"{chemin} : {compte} apostrophes droites contre "
                    f"{unite.get('apostrophes', 0)} à la référence — employer l'apostrophe typographique"
                )

    for edition in editions_relues:
        if edition.get("auteur") != "agent":
            erreurs.append(f"edition {edition.get('chemin', '?')} : auteur doit être « agent »")
        for cle in ("chemin", "date", "empreinte_avant", "empreinte_apres", "nature", "constat", "limite"):
            if not edition.get(cle):
                erreurs.append(f"edition {edition.get('chemin', '?')} : champ « {cle} » absent")
        if edition.get("nature") not in NATURES:
            erreurs.append(f"edition {edition.get('chemin', '?')} : nature inconnue")
        if edition.get("nature") == "fait-source" and not edition.get("sources"):
            erreurs.append(f"edition {edition.get('chemin', '?')} : un fait-source exige une source primaire")
        if edition.get("nature") == "mesure-interne" and not edition.get("mesures"):
            erreurs.append(f"edition {edition.get('chemin', '?')} : une mesure-interne exige un fichier reproductible")

    if not EDITIONS.is_file():
        erreurs.append("registre des éditions absent : docs/rd/editions-relecture.toml")
    erreurs.extend(batterie_mecanique(reel))
    erreurs.extend(verifier_sources(donnees))
    erreurs.extend(verifier_cablage())

    environnement = dict(os.environ, MRSC_RACINE=str(RACINE))
    porte = subprocess.run(
        [sys.executable, str(PORTE_LOT)],
        capture_output=True, text=True, check=False, env=environnement,
    )
    if porte.returncode != 0:
        erreurs.append("porte de relecture du lot en échec : " + (porte.stderr or porte.stdout)[-400:].strip())
    return erreurs


# ---------------------------------------------------------------------------
# Écritures réservées à l'agent qui a fait la lecture
# ---------------------------------------------------------------------------

def ecrire_manifeste(unites_declarees: list[dict], meta: dict) -> None:
    lignes = [
        "# Empreintes de toutes les unités de contenu. Fichier généré :",
        "# ne pas éditer à la main, utiliser `outils/relire-contenus.py --appliquer`.",
        "# Une édition qui change une empreinte fait échouer la CI tant qu'une",
        "# [[edition]] datée n'a pas été consignée dans relecture-contenus.toml.",
        "",
        "[meta]",
        "version = 1",
        'auteur = "agent"',
        f"date_reference = {meta['date_reference']}",
        'regle = "' + meta["regle"].replace('"', '\\"') + '"',
        'limite_reference = "' + meta["limite_reference"].replace('"', '\\"') + '"',
        "",
    ]
    for unite in unites_declarees:
        lignes.append("[[unite]]")
        lignes.append('chemin = "' + unite["chemin"].replace('"', '\\"') + '"')
        lignes.append('empreinte = "' + unite["empreinte"] + '"')
        lignes.append('etat = "' + unite["etat"] + '"')
        lignes.append(f"apostrophes = {unite.get('apostrophes', 0)}")
        if unite.get("date_reference"):
            lignes.append(f"date_reference = {unite['date_reference']}")
        if unite.get("date_derniere_relecture"):
            lignes.append(f"date_derniere_relecture = {unite['date_derniere_relecture']}")
        if unite.get("urls"):
            lignes.append(
                "urls = [" + ", ".join(
                    '"' + str(u).replace("\\", "\\\\").replace('"', '\\"') + '"' for u in unite["urls"]
                ) + "]"
            )
        if unite.get("raison"):
            lignes.append('raison = "' + unite["raison"].replace('"', '\\"') + '"')
        lignes.append("")
    MANIFESTE.write_text("\n".join(lignes), encoding="utf-8")


def initialiser() -> int:
    if MANIFESTE.is_file() and "--forcer" not in sys.argv:
        print("Manifeste déjà présent : --initialiser ne réécrit rien (utiliser --forcer).", file=sys.stderr)
        return 1
    reel = unites()
    date = dt.date.today().isoformat()
    meta = {
        "date_reference": date,
        "regle": "La personne valide le rendu à l'oeil ; l'agent relit chaque édition, confronte les faits à des sources primaires datées et consigne les limites.",
        "limite_reference": (
            "Les empreintes du 9 novembre 2026 sont une référence de départ, pas une relecture de fond : "
            "le corpus existant reste couvert par les contrôles mécaniques déjà en place, et sa relecture "
            "éditoriale par agent reste une dette visible. Seules les éditions postérieures à cette date "
            "sont soumises à une [[edition]] consignée. Aucune écriture dans relectures.toml."
        ),
    }
    ecrire_manifeste(
        [
            {
                "chemin": chemin,
                "empreinte": empreinte(RACINE / chemin),
                "etat": "reference-initiale",
                "date_reference": date,
                "apostrophes": nombre_apostrophes(chemin),
                "urls": urls_du_fichier(chemin),
            }
            for chemin in reel
        ],
        meta,
    )
    print(f"Référence initiale : {len(reel)} unités enregistrées, 0 relecture de fond revendiquée.")
    return 0


def lignes_ajoutees(relatif: str) -> list[str]:
    """Lines nouvelles par rapport à HEAD : seules elles portent de nouveaux faits."""
    ancien = subprocess.run(
        ["git", "show", f"HEAD:{relatif}"],
        cwd=RACINE, capture_output=True, text=True, check=False,
    )
    avant = ancien.stdout if ancien.returncode == 0 else ""
    maintenant = (RACINE / relatif).read_text(encoding="utf-8")
    compteur = Counter(avant.splitlines())
    ajoutees: list[str] = []
    for ligne in maintenant.splitlines():
        if compteur[ligne] > 0:
            compteur[ligne] -= 1
        else:
            ajoutees.append(ligne)
    return ajoutees


def urls_du_fichier(relatif: str) -> list[str]:
    """Les URL externes du fichier, dans l'ordre, débarrassées de la ponctuation."""
    texte = (RACINE / relatif).read_text(encoding="utf-8")
    urls: list[str] = []
    for url in MOTIF_URL.findall(texte):
        # Une URL écrite dans une chaîne Python échappée arrive avec une barre
        # oblique finale : `...localisation.html\"` dans le code source. Sans ce
        # nettoyage, le manifeste recevait une URL fausse et le TOML écrit ne se
        # relisait plus — un fichier corrompu par sa propre ponctuation.
        url = url.rstrip(".,;:)]}|`\\")
        if url not in urls:
            urls.append(url)
    return urls


def urls_connues(relatif: str, declare: dict) -> set[str]:
    """Les URL que la dernière relecture signée connaissait.

    Le manifeste les garde. À défaut — unité jamais signée depuis l'ajout de ce
    champ — la version de `HEAD` fait foi. Si ni l'un ni l'autre n'existe, rien
    n'est connu : toute URL du fichier est alors nouvelle, et la porte refuse.
    """
    gardees = declare.get("urls")
    if isinstance(gardees, list):
        return {str(u).rstrip(".,;:)]}|`\\") for u in gardees}
    ancien = subprocess.run(
        ["git", "show", f"HEAD:{relatif}"],
        cwd=RACINE, capture_output=True, text=True, check=False,
    )
    if ancien.returncode != 0:
        return set()
    return {url.rstrip(".,;:)]}|`\\") for url in MOTIF_URL.findall(ancien.stdout)}


def urls_nouvelles(relatif: str, connues: set[str] | None = None) -> list[str]:
    """URL absentes de la version signée : réécrire une ligne n'invente pas une source.

    La première version comparait les URL des **lignes ajoutées**. Sur ce site,
    où une section entière tient souvent sur une seule ligne, ajouter un attribut
    à une balise rend la ligne neuve : les liens qu'elle portait déjà, et qui
    avaient été vus et signés, redevenaient « nouveaux ». Le 13 novembre 2026,
    la pose de `role="list"` a ainsi produit six refus pour des URL inchangées
    depuis des semaines (ANLCI, W3C, éduscol, ADEME). La comparaison porte donc
    sur les **ensembles d'URL avant et après** : une URL qui était déjà là ne
    demande pas de source nouvelle, une URL qui apparaît en demande une.

    La mémoire de ces URL est le manifeste, pas l'historique Git : un banc de
    mutation travaille sur une copie sans `.git`, et une porte qui ne sait pas
    répondre hors du dépôt ne s'éprouve pas. La mémoire se remplit à chaque
    signature ; les unités signées avant son ajout retombent sur `HEAD`.
    """
    if connues is None:
        connues = urls_connues(relatif, {})
    return [url for url in urls_du_fichier(relatif) if url not in connues]


def appliquer(args: argparse.Namespace) -> int:
    if not MANIFESTE.is_file() or not REGISTRE.is_file():
        print("Registre ou manifeste absent : lancer --initialiser.", file=sys.stderr)
        return 1
    try:
        manifeste = lire_toml(MANIFESTE)
        donnees = lire_toml(REGISTRE)
    except (tomllib.TOMLDecodeError, OSError) as erreur:
        print(f"Lecture impossible : {erreur}", file=sys.stderr)
        return 1
    chemins = sorted(set(args.appliquer))
    reel = set(unites())
    declares = {u["chemin"]: u for u in manifeste.get("unite", [])}
    sources_connues = {s.get("id") for s in donnees.get("source", [])}
    urls_sources = {str(s.get("url", "")).rstrip("/") for s in donnees.get("source", [])}
    ids = [x for x in (args.sources or "").split(",") if x]
    mesures = [x for x in (args.mesures or "").split(",") if x]

    erreurs: list[str] = []
    for chemin in chemins:
        if chemin not in reel:
            erreurs.append(f"--appliquer : unité inconnue : {chemin}")
            continue
        if chemin not in declares:
            # Une unité nouvelle (fichier créé par ce lot) n'a pas d'empreinte
            # antérieure : elle entre au manifeste par la même relecture que les
            # autres, avec l'empreinte du fichier absent comme référence. Refuser
            # ce cas obligeait à `--initialiser --forcer`, qui réécrit tout le
            # manifeste et **efface les relectures déjà consignées** : une
            # nouvelle unité ne doit pas coûter la mémoire des autres.
            declares[chemin] = {
                "chemin": chemin,
                "empreinte": EMPREINTE_ABSENT,
                "etat": "reference-initiale",
                "apostrophes": 0,
            }
        avant = declares[chemin]["empreinte"]
        apres = empreinte(RACINE / chemin)
        if avant == apres:
            erreurs.append(f"--appliquer : aucune édition à relire dans {chemin}")
        compte = nombre_apostrophes(chemin)
        if compte > int(declares[chemin].get("apostrophes", 0)):
            erreurs.append(f"--appliquer : {chemin} gagne des apostrophes droites ({compte})")
        # Les bancs de mutation inventent volontairement de mauvaises URL pour
        # éprouver le refus : ce sont des fixtures, pas des faits à sourcer.
        if chemin.startswith("outils/test_"):
            continue
        for url in urls_nouvelles(chemin, urls_connues(chemin, declares[chemin])):
            try:
                domaine = urlparse(url).netloc.lower()
            except ValueError:
                erreurs.append(f"--appliquer : URL illisible dans {chemin} : {url}")
                continue
            if (domaine in DOMAINES_PROPRES or domaine in DOMAINES_FICTIFS
                    or "/thejmimiia-code/MRSC" in url):
                continue
            if url.rstrip("/") not in urls_sources:
                erreurs.append(
                    f"--appliquer : URL externe nouvelle sans source primaire enregistrée : {url} — "
                    "ajouter une [[source]] datée et son extrait avant de signer"
                )
    for identifiant in ids:
        if identifiant not in sources_connues:
            erreurs.append(f"--sources : identifiant inconnu : {identifiant}")
    for chemin in mesures:
        if not (RACINE / chemin).is_file():
            erreurs.append(f"--mesures : fichier reproductible introuvable : {chemin}")
    if args.nature == "fait-source" and not ids:
        erreurs.append("--nature fait-source exige --sources")
    if args.nature == "mesure-interne" and not mesures:
        erreurs.append("--nature mesure-interne exige --mesures")
    if args.nature == "proposition":
        if ids:
            erreurs.append("--nature proposition n'accepte aucune source externe")
        if "aucun fait externe" not in args.constat.lower():
            erreurs.append("--nature proposition doit dire « aucun fait externe » dans le constat")
    if len(args.constat) < 40:
        erreurs.append("--constat trop court : dire ce qui a été relu")
    if len(args.limite) < 60:
        erreurs.append("--limite trop courte : dire ce que cette relecture ne couvre pas")

    # Aucune signature si le reste du dépôt est en faute : la relecture n'est
    # pas un blanc-seing pour casser une autre porte.
    autres = verifier(exceptions=set(chemins))
    if autres:
        erreurs.extend("porte : " + e for e in autres)
    if erreurs:
        for erreur in erreurs:
            print(f"ERREUR — {erreur}", file=sys.stderr)
        print(f"ÉCHEC — relecture non consignée ({len(erreurs)} écart(s)).", file=sys.stderr)
        return 1

    # Un banc de mutations peut appeler --appliquer sur une copie ; il ne doit
    # jamais pouvoir signer dans le vrai dépôt à travers un lien symbolique.
    if os.environ.get("MRSC_RACINE"):
        print("ÉCHEC — --appliquer refuse d'écrire dans une racine de banc (MRSC_RACINE).", file=sys.stderr)
        return 1

    date = dt.date.today().isoformat()
    blocs: list[str] = []
    for chemin in chemins:
        avant = declares[chemin]["empreinte"]
        apres = empreinte(RACINE / chemin)
        champs = [
            "[[edition]]",
            f'chemin = "{chemin}"',
            f"date = {date}",
            'auteur = "agent"',
            f'empreinte_avant = "{avant}"',
            f'empreinte_apres = "{apres}"',
            f'nature = "{args.nature}"',
            "sources = [" + ", ".join(f'"{i}"' for i in ids) + "]",
            "mesures = [" + ", ".join(f'"{m}"' for m in mesures) + "]",
            'constat = "' + args.constat.replace('"', '\\"') + '"',
            'limite = "' + args.limite.replace('"', '\\"') + '"',
            "",
        ]
        blocs.append("\n".join(champs))
        declares[chemin].update(
            empreinte=apres,
            etat="relu-par-agent",
            date_derniere_relecture=date,
            apostrophes=nombre_apostrophes(chemin),
            urls=urls_du_fichier(chemin),
        )
        declares[chemin].pop("date_reference", None)

    entete = (
        "# Éditions relues par agent. Fichier généré par `outils/relire-contenus.py --appliquer`.\n"
        "# Ne pas éditer à la main : chaque bloc est confronté à l'empreinte du manifeste.\n\n"
    )
    ancien = EDITIONS.read_text(encoding="utf-8") if EDITIONS.is_file() else entete
    if not ancien.startswith("#"):
        print("Registre des éditions illisible : entête absent.", file=sys.stderr)
        return 1
    EDITIONS.write_text(ancien.rstrip() + "\n\n" + "\n".join(blocs), encoding="utf-8")
    ecrire_manifeste(
        sorted(declares.values(), key=lambda u: u["chemin"]),
        {
            "date_reference": str(manifeste["meta"]["date_reference"]),
            "regle": manifeste["meta"]["regle"],
            "limite_reference": manifeste["meta"]["limite_reference"],
        },
    )
    print(f"Relecture consignée : {len(chemins)} unité(s), nature « {args.nature} », sources : {ids or 'aucune'}.")
    return 0


def principal() -> int:
    parseur = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parseur.add_argument("--initialiser", action="store_true", help="créer la référence initiale des empreintes")
    parseur.add_argument("--forcer", action="store_true", help="autoriser --initialiser à réécrire le manifeste")
    parseur.add_argument("--appliquer", nargs="+", metavar="CHEMIN", help="consigner la relecture de ces unités")
    parseur.add_argument("--nature", choices=sorted(NATURES), default="proposition")
    parseur.add_argument("--sources", default="", help="identifiants de sources primaires, séparés par des virgules")
    parseur.add_argument("--mesures", default="", help="fichiers reproductibles pour une mesure interne")
    parseur.add_argument("--constat", default="", help="ce qui a été relu et confronté")
    parseur.add_argument("--limite", default="", help="ce que la relecture ne couvre pas")
    args = parseur.parse_args()
    if args.initialiser:
        return initialiser()
    if args.appliquer:
        return appliquer(args)
    erreurs = verifier()
    if erreurs:
        for erreur in erreurs:
            print(f"ERREUR — {erreur}", file=sys.stderr)
        print(f"ÉCHEC — {len(erreurs)} écart(s) : une édition n'est pas passée par la relecture.", file=sys.stderr)
        return 1
    try:
        manifeste = lire_toml(MANIFESTE)
    except (tomllib.TOMLDecodeError, OSError):
        manifeste = {}
    unites_declarees = manifeste.get("unite", [])
    relus = sum(1 for u in unites_declarees if u.get("etat") == "relu-par-agent")
    dette = sum(1 for u in unites_declarees if u.get("etat") == "reference-initiale")
    print(
        f"OK — {len(unites_declarees)} unités sous empreinte, {relus} relues par agent, "
        f"{dette} en dette initiale consignée ; liens, ancres, TOML, extraits de sources, "
        "fraîcheur et câblage vérifiés à chaque édition."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(principal())
