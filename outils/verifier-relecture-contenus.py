#!/usr/bin/env python3
"""Nouvelle étape de relecture : l'agent relit les contenus, pas la personne.

Le 7 novembre 2026, la personne a demandé que la relecture de contenu et la
vérification des sources sûres soient prises en charge par une étape dédiée ;
elle garde la validation du rendu à l'œil (placement, style, construction).
Ce script rend cette étape exécutable et vérifiable.

Ce qu'il vérifie, mécaniquement :
  - le registre `docs/rd/relecture-contenus.toml` est daté, attribué à un agent
    et ne se présente pas comme une relecture humaine ;
  - chaque source est un éditeur primaire (MDN, W3C, dépôt W3C, administrations
    et plateformes nationales françaises), avec une URL,
    une date de consultation, une ancre courte, ce qu'elle permet d'affirmer et
    ses limites ;
  - chaque affirmation est rattachée à des sources primaires existantes ou à une
    mesure interne reproductible, avec un verdict et une limite explicite ;
  - chaque chaîne publique du lot des apparences est couverte par une entrée, et
    chaque entrée de chaîne publique existe réellement dans le fichier cité ;
  - les corrections issues des sources sont encore en place (seuil 0,04045 de la
    luminance WCAG 2.2, comparaison sans arrondi des seuils de contraste) ;
  - les rapports datés existent, citent toutes les sources et distinguent relecture
    d'agent, validation humaine, expertise et avis juridique ;
  - le registre des relectures HUMAINES reste vide : cette étape ne promeut
    aucune fiche, n'écrit aucune entrée et n'embellit aucun statut ;
  - l'étape est bien câblée dans la CI et dans l'inventaire des contrôles.

Ce qu'il ne fait PAS : il ne lit pas le Web, ne juge pas la vérité d'une page
source, ne remplace pas une relecture humaine, ne donne pas d'avis juridique et
ne valide pas un rendu visuel. La lecture effective des sources primaires est
consignée, datée, dans `docs/rd/relecture-apparences-2026-11-07.md`. La porte
éprouve la discipline de cette relecture, pas l'exactitude du Web.

Lancer : python3 outils/verifier-relecture-contenus.py
Banc    : MRSC_RACINE=/tmp/copie python3 outils/verifier-relecture-contenus.py
"""
from __future__ import annotations

import datetime as dt
import os
import re
import sys
import tomllib
from pathlib import Path
from urllib.parse import urlparse

#: Surcharge pour le banc de mutations : la copie jetable est lue à la place
#: du dépôt, comme pour les autres portes (banc_mutations.lancer).
RACINE = Path(os.environ.get("MRSC_RACINE") or Path(__file__).resolve().parent.parent).resolve()
REGISTRE = RACINE / "docs" / "rd" / "relecture-contenus.toml"
REGISTRE_HUMAIN = RACINE / "docs" / "apprentissage" / "relectures.toml"
OUTIL_HUMAIN = RACINE / "outils" / "registre-relecture.py"
RAPPORT = RACINE / "docs" / "rd" / "relecture-apparences-2026-11-07.md"
#: Rapports de relecture par agent. Le premier est celui du lot des apparences,
#: dont les passages attendus ci-dessous sont vérifiés mot pour mot. Les suivants
#: couvrent d'autres lots : la porte exige qu'ils citent **toutes** les sources du
#: registre, y compris les leurs, plutôt que de faire grossir indéfiniment un
#: rapport unique. Un lot sans rapport daté ne passe donc pas en silence : au
#: moins un des rapports doit citer chaque source et chaque URL.
RAPPORTS = (
    RAPPORT,
    RACINE / "docs" / "rd" / "relecture-fraudes-declaration-2026-11-12.md",
    RACINE / "docs" / "rd" / "relecture-couts-vie-chere-2026-11-14.md",
)
JS = RACINE / "assets" / "js" / "site.js"
CSS = RACINE / "assets" / "css" / "site.css"
PORTE_APPARENCES = RACINE / "outils" / "verifier-apparences.py"
WORKFLOW = RACINE / ".github" / "workflows" / "verification.yml"
INVENTAIRE = RACINE / "docs" / "rd" / "inventaire-controles.md"

#: Domaines admis comme éditeurs primaires. Élargi le 12 novembre 2026 au lot
#: « déclarer » : une procédure de déclaration de fraude ne se documente pas
#: ailleurs que sur les sites des administrations qui la reçoivent. L'élargissement
#: ne dispense d'aucun contrôle : extrait daté, ancre de cinq mots au plus,
#: « permet » et « limites » explicites restent exigés pour chaque source.
DOMAINES_SURS = {
    "developer.mozilla.org", "www.w3.org", "w3.org", "github.com", "api.github.com",
    "www.service-public.gouv.fr", "service-public.fr", "service-public.gouv.fr",
    "www.cybermalveillance.gouv.fr", "cybermalveillance.gouv.fr",
    "www.signal-spam.fr", "signal-spam.fr", "www.33700.fr", "33700.fr",
    # Élargi le 14 novembre 2026 au lot « coût de la vie » : les fiches de licence
    # de DVF, d’ADMIN EXPRESS et du découpage administratif n’existent que sur ce
    # portail public. La source citée est une métadonnée officielle, pas la donnée
    # elle-même, et chaque extrait garde son empreinte et ses limites écrites.
    "www.data.gouv.fr", "data.gouv.fr", "geo.api.gouv.fr", "www.geo.api.gouv.fr",
    # Plateforme Opendatasoft de l’État : c’est là que vit l’export réellement
    # téléchargé des prix des carburants, distinct de la fiche de licence data.gouv.
    "data.economie.gouv.fr", "www.data.economie.gouv.fr",
}
EDITEURS_ATTENDUS = (
    "MDN Web Docs", "W3C",
    "Service-Public.gouv.fr", "Cybermalveillance.gouv.fr",
    "Signal Spam", "33700",
    # Éditeurs publics du lot « coût de la vie », ajoutés avec leur domaine et
    # leur extrait daté comme les précédents.
    "DGFiP", "Etalab", "data.gouv.fr", "IGN", "INSEE", "gregoiredavid", "DGCCRF",
)
NATURES = {"fait-source", "mesure-interne", "proposition"}
VERDICTS = {"concordant", "corrige", "retire", "sans-objet"}
DATE_ATTENDUE = dt.date(2026, 11, 7)

# Deuxième garde indépendante : aucune œuvre citée dans la demande ne doit
# réapparaître dans le produit, sous quelque casse que ce soit.
# Même liste que outils/verifier-apparences.py, mais éprouvée ici avec des
# frontières de mots : une garde indépendante, pas un simple copier-coller.
NOMS_PROTEGES = (
    "stranger things", "retour vers le futur", "back to the future",
    "ready player one", "player one", "oasis", "eleven", "marty mcfly",
)

MOTIFS_CHAINES = (
    r'\blabel:\s*"([^"]+)"',
    r'\bdescription:\s*"([^"]+)"',
    r'\.textContent\s*=\s*"([^"]+)"',
    r'\.title\s*=\s*"([^"]+)"',
    r'createTextNode\("([^"]+)"\)',
    r'\.setAttribute\("(?:title|aria-label)",\s*"([^"]+)"\)',
)


def chaines_publiques(texte: str) -> list[str]:
    """Extrait les chaînes visibles du seul bloc « Apparences » du script."""
    debut = texte.find("  // --- Apparences")
    fin = texte.find("  // --- Écouter la page", debut)
    if debut < 0 or fin < 0:
        raise ValueError("bloc « Apparences » introuvable dans site.js")
    bloc = texte[debut:fin]
    trouvees: list[str] = []
    for motif in MOTIFS_CHAINES:
        for chaine in re.findall(motif, bloc):
            if len(chaine.strip()) >= 2 and chaine not in trouvees:
                trouvees.append(chaine)
    statut = "Apparence « ${apparence.label} » appliquée."
    if statut not in bloc:
        raise ValueError("chaîne du statut vocal introuvable dans site.js")
    trouvees.append(statut)
    return trouvees


def verifier() -> list[str]:
    erreurs: list[str] = []

    if not REGISTRE.is_file():
        return ["registre de relecture par agent absent : docs/rd/relecture-contenus.toml"]
    try:
        donnees = tomllib.loads(REGISTRE.read_text(encoding="utf-8"))
    except (tomllib.TOMLDecodeError, OSError) as erreur:
        return [f"registre illisible : {erreur}"]

    meta = donnees.get("meta", {})
    if meta.get("version") != 1:
        erreurs.append("meta : version attendue : 1")
    if meta.get("auteur") != "agent":
        erreurs.append("meta : auteur doit être « agent » (jamais une personne)")
    # Le lot du 7 novembre 2026 garde sa date : elle date la lecture des
    # apparences, pas la dernière édition du registre. Les lots postérieurs
    # ajoutent leur date dans `dates_lots` et ne réécrivent pas l'histoire.
    dates_lots = [DATE_ATTENDUE]
    for brute in meta.get("dates_lots") or []:
        if isinstance(brute, dt.date):
            dates_lots.append(brute)
        else:
            erreurs.append(f"meta : dates_lots illisible : {brute!r}")
    if meta.get("date_relecture") != DATE_ATTENDUE:
        erreurs.append("meta : date_relecture attendue : 2026-11-07")
    statut = str(meta.get("statut", ""))
    if "humain" in statut or "valide" in statut:
        erreurs.append("meta : le statut d'une relecture d'agent ne doit pas revendiquer une validation humaine")
    if not statut.startswith("relu-par-agent"):
        erreurs.append("meta : statut doit commencer par « relu-par-agent »")
    regle = str(meta.get("regle", ""))
    for morceau in ("rendu à l'oeil", "l'agent relit", "source primaire"):
        if morceau not in regle:
            erreurs.append(f"meta : la règle doit préciser « {morceau} »")
    rapport = str(meta.get("rapport", ""))
    if not (RACINE / rapport).is_file():
        erreurs.append(f"meta : rapport daté introuvable : {rapport}")

    sources = donnees.get("source", [])
    affirmations = donnees.get("affirmation", [])
    if not isinstance(sources, list) or not isinstance(affirmations, list):
        return ["registre : « source » et « affirmation » doivent être des listes"]
    if len(sources) < 5:
        erreurs.append("registre : au moins cinq sources primaires sont attendues")
    ids_sources: set[str] = set()
    urls: set[str] = set()
    for source in sources:
        identifiant = source.get("id", "?")
        for cle in ("id", "editeur", "titre", "url", "consulte_le", "ancre", "permet", "limites"):
            if not source.get(cle):
                erreurs.append(f"source {identifiant} : champ « {cle} » absent ou vide")
        if identifiant in ids_sources:
            erreurs.append(f"source {identifiant} : identifiant en double")
        ids_sources.add(identifiant)
        url = str(source.get("url", ""))
        if url in urls:
            erreurs.append(f"source {identifiant} : URL en double")
        urls.add(url)
        domaine = urlparse(url).netloc.lower()
        if domaine not in DOMAINES_SURS:
            erreurs.append(f"source {identifiant} : domaine non retenu comme primaire : {domaine}")
        if urlparse(url).scheme != "https":
            erreurs.append(f"source {identifiant} : URL doit être en https")
        if not any(str(source.get("editeur", "")).startswith(e) for e in EDITEURS_ATTENDUS):
            erreurs.append(f"source {identifiant} : éditeur primaire attendu (MDN ou W3C)")
        # Une source ajoutée après le lot du 7 novembre 2026 peut être datée du
        # jour de sa consultation. Ce qui est refusé : une source non datée, une
        # date antérieure au lot, ou une date qui n'a pas encore eu lieu (la
        # fraîcheur et la fenêtre sont vérifiées par `relire-contenus.py`).
        consultee = source.get("consulte_le")
        if (not isinstance(consultee, dt.date) or consultee < DATE_ATTENDUE
                or consultee > dt.date.today() + dt.timedelta(days=1)):
            erreurs.append(
                f"source {identifiant} : date de consultation absente ou hors fenêtre : {consultee}"
            )
        ancre = str(source.get("ancre", ""))
        if len(ancre) > 40 or len(ancre.split()) > 5:
            erreurs.append(f"source {identifiant} : ancre trop longue (extrait bref, 5 mots au plus)")
        if len(str(source.get("permet", ""))) < 60:
            erreurs.append(f"source {identifiant} : « permet » doit dire précisément ce que la source autorise")
        if len(str(source.get("limites", ""))) < 120:
            erreurs.append(f"source {identifiant} : « limites » doit être explicite (120 caractères au moins)")

    ids_affirmations: set[str] = set()
    textes_publiques: list[str] = []
    for affirmation in affirmations:
        identifiant = affirmation.get("id", "?")
        for cle in ("id", "texte", "ou", "nature", "verdict", "ce_qui_est_verifie", "limite"):
            if not affirmation.get(cle):
                erreurs.append(f"affirmation {identifiant} : champ « {cle} » absent ou vide")
        if identifiant in ids_affirmations:
            erreurs.append(f"affirmation {identifiant} : identifiant en double")
        ids_affirmations.add(identifiant)
        nature = affirmation.get("nature")
        if nature not in NATURES:
            erreurs.append(f"affirmation {identifiant} : nature inconnue : {nature}")
        if affirmation.get("verdict") not in VERDICTS:
            erreurs.append(f"affirmation {identifiant} : verdict inconnu")
        refs = affirmation.get("sources", [])
        mesures = affirmation.get("mesures", [])
        if not isinstance(refs, list) or not isinstance(mesures, list):
            erreurs.append(f"affirmation {identifiant} : « sources » et « mesures » doivent être des listes")
            refs, mesures = [], []
        for reference in refs:
            if reference not in ids_sources:
                erreurs.append(f"affirmation {identifiant} : source inconnue : {reference}")
        for chemin in mesures:
            if not (RACINE / chemin).is_file():
                erreurs.append(f"affirmation {identifiant} : mesure interne introuvable : {chemin}")
        if nature == "fait-source" and not refs:
            erreurs.append(f"affirmation {identifiant} : un fait-source exige au moins une source primaire")
        if nature == "mesure-interne" and not mesures:
            erreurs.append(f"affirmation {identifiant} : une mesure-interne exige un fichier reproductible")
        if nature == "proposition" and refs:
            erreurs.append(f"affirmation {identifiant} : une proposition ne doit pas s'appuyer sur une source externe")
        if nature == "proposition" and "aucun fait externe" not in str(affirmation.get("limite", "")).lower():
            erreurs.append(f"affirmation {identifiant} : une proposition doit dire « aucun fait externe »")
        if len(str(affirmation.get("ce_qui_est_verifie", ""))) < 40:
            erreurs.append(f"affirmation {identifiant} : décrire ce qui a été vérifié")
        if len(str(affirmation.get("limite", ""))) < 60:
            erreurs.append(f"affirmation {identifiant} : limite trop courte")
        chemin = str(affirmation.get("ou", ""))
        if not (RACINE / chemin).is_file():
            erreurs.append(f"affirmation {identifiant} : fichier « ou » introuvable : {chemin}")
        elif identifiant.startswith("chaine-"):
            contenu = (RACINE / chemin).read_text(encoding="utf-8")
            texte = str(affirmation.get("texte", ""))
            if texte not in contenu:
                erreurs.append(f"affirmation {identifiant} : la chaîne publique n'existe plus dans {chemin}")
            if chemin == "assets/js/site.js":
                textes_publiques.append(texte)

    try:
        chaines = chaines_publiques(JS.read_text(encoding="utf-8"))
    except (OSError, ValueError) as erreur:
        return [f"site.js : {erreur}"]
    for chaine in chaines:
        if chaine not in textes_publiques:
            erreurs.append(f"chaîne publique non relue : {chaine[:60]!r}")
    for texte in textes_publiques:
        if texte not in chaines:
            erreurs.append(f"entrée de chaîne publique devenue orpheline : {texte[:60]!r}")

    # Les corrections tirées des sources primaires ne doivent pas régresser.
    porte = PORTE_APPARENCES.read_text(encoding="utf-8")
    if "valeur <= 0.04045" not in porte:
        erreurs.append("la porte d'apparences doit employer le seuil WCAG 2.2 actuel : 0.04045")
    if "mesure + 1e-9 < seuil" not in porte:
        erreurs.append("la porte d'apparences doit comparer les seuils sans arrondi tolérant")
    if re.search(r"if mesure < seuil - 0\.01", porte):
        erreurs.append("tolérance de 0,01 sur les seuils de contraste revenue : W3C interdit l'arrondi")

    # Aucun nom d'œuvre repris dans le produit (garde indépendante).
    for fichier in (CSS, JS):
        contenu = fichier.read_text(encoding="utf-8").lower()
        for nom in NOMS_PROTEGES:
            # Frontières de mot : « tron » ne doit pas se confondre avec
            # « contraste », « contrôles » ou « électronique ».
            if re.search(r"(?<!\w)" + re.escape(nom) + r"(?!\w)", contenu):
                erreurs.append(f"{fichier.name} : nom protégé réapparu : {nom}")

    # Aucune promotion en relecture humaine : on lit les ENTRÉES, pas les
    # commentaires du fichier (qui expliquent justement la syntaxe d'un bloc).
    if not REGISTRE_HUMAIN.is_file():
        erreurs.append("registre des relectures humaines absent")
    else:
        try:
            donnees_humaines = tomllib.loads(REGISTRE_HUMAIN.read_text(encoding="utf-8"))
        except tomllib.TOMLDecodeError as erreur:
            erreurs.append(f"relectures.toml illisible : {erreur}")
        else:
            if donnees_humaines.get("relecture"):
                erreurs.append("relectures.toml contient une entrée : une relecture d'agent ne doit jamais y écrire")
    outil_humain = OUTIL_HUMAIN.read_text(encoding="utf-8") if OUTIL_HUMAIN.is_file() else ""
    if "ne relit rien, ne note rien" not in outil_humain:
        erreurs.append("la séparation avec le registre humain doit rester documentée")

    # Le rapport daté porte la lecture effective et ses limites.
    if not RAPPORT.is_file():
        erreurs.append("rapport de relecture daté absent")
    else:
        contenu = RAPPORT.read_text(encoding="utf-8")
        for morceau in ("Relecture par agent", "rendu à l'œil", "2026-11-07",
                        "0,03928", "0,04045", "les plus utilisés",
                        "validation humaine", "avis juridique", "expertise",
                        "essai avec des personnes"):
            if morceau not in contenu:
                erreurs.append(f"rapport : passage attendu absent : {morceau!r}")
        if "validé par une personne" in contenu:
            erreurs.append("rapport : ne pas revendiquer une validation par une personne")

    # Chaque source du registre doit être citée, identifiant ET URL, dans au moins
    # un rapport daté. C'est ce qui relie une source à la lecture qui l'a faite.
    textes_rapports = []
    for chemin in RAPPORTS:
        if not chemin.is_file():
            erreurs.append(f"rapport de relecture daté absent : {chemin.name}")
            continue
        textes_rapports.append(chemin.read_text(encoding="utf-8"))
    for source in sources:
        if not any(str(source.get("id", "")) in texte for texte in textes_rapports):
            erreurs.append(f"rapport : source non citée : {source.get('id')}")
        if not any(str(source.get("url", "")) in texte for texte in textes_rapports):
            erreurs.append(f"rapport : URL non citée : {source.get('id')}")

    # L'étape est câblée et inventoriée : elle ne peut pas disparaître en silence.
    workflow = WORKFLOW.read_text(encoding="utf-8") if WORKFLOW.is_file() else ""
    if "verifier-relecture-contenus.py" not in workflow:
        erreurs.append("workflow : l'étape de relecture par agent n'est pas câblée")
    inventaire = INVENTAIRE.read_text(encoding="utf-8") if INVENTAIRE.is_file() else ""
    if "verifier-relecture-contenus.py" not in inventaire:
        erreurs.append("inventaire : l'étape de relecture par agent n'est pas recensée")

    return erreurs


def main() -> int:
    erreurs = verifier()
    if erreurs:
        for erreur in erreurs:
            print(f"ERREUR — {erreur}", file=sys.stderr)
        print(f"ÉCHEC — {len(erreurs)} écart(s) dans l'étape de relecture par agent.", file=sys.stderr)
        return 1
    print("OK — relecture par agent : sources primaires datées, affirmations rattachées, "
          "chaînes publiques couvertes, corrections tenues, aucune promotion humaine.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
