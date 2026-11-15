#!/usr/bin/env python3
"""Collecte les loyers observés, agglomération par agglomération.

Pourquoi les loyers, et pas « le coût de la vie » : après le prix d'achat et le
carburant, le loyer est le troisième poste qu'un foyer paie tous les mois, et le
seul des trois dont la donnée publique soit **observée** plutôt que déclarée.
Le réseau des observatoires locaux des loyers (OLL), animé par l'ANIL, publie
chaque année une base nationale sous Licence Ouverte 2.0 : pour chaque
agglomération observée, le loyer médian au mètre carré, le loyer médian mensuel,
la surface moyenne et le nombre de logements qui fondent ces médianes.

La source ne publie pas par commune. Cette collecte ne fabrique donc aucune
ligne communale : elle publie ce que la source dit, à la maille où elle le dit,
et la page l'écrit.

Comment la source est lue, et pourquoi ainsi : la fiche du jeu de données est
interrogée par son API publique pour trouver la ressource de l'année la plus
récente — l'URL du fichier change chaque année, et une URL écrite en dur
vieillirait en silence. Les lignes sont ensuite lues par l'API tabulaire de
data.gouv.fr, qui sert le même fichier en JSON : le format des champs est alors
donné par la source elle-même, au lieu d'être deviné dans un CSV dont le
séparateur et la virgule décimale dépendent de la langue de l'export. Un
analyseur écrit contre un format supposé est exactement la faute qui a laissé
Paris, Lyon et Marseille vides lors de la première collecte DVF.

Ce que l'outil refuse, et pourquoi :

- une licence qui n'est pas ouverte : rien n'est publié ;
- aucune ressource « Loyers AAAA dans les agglomérations » : la fiche a changé,
  et deviner quelle ressource lire reviendrait à choisir un chiffre ;
- un total de lignes hors de 30 à 200 : le filtre qui isole l'ensemble des
  logements d'une agglomération ne sélectionne plus ce qu'il croit ;
- un code d'observatoire qui n'a pas la forme publiée (`B1300`, `B2B00`) ;
- une année de données qui n'est pas celle annoncée par la ressource ;
- une médiane hors de 3 à 40 €/m², une médiane mensuelle hors de 100 à
  4 000 €, une surface moyenne hors de 10 à 200 m² : un fichier mal lu produit
  des valeurs aberrantes, pas des loyers ;
- deux lignes pour le même territoire : une médiane en double est une médiane
  dont on ne sait plus laquelle est la bonne ;
- une source injoignable, un JSON illisible, une provenance incomplète.

Ce que l'outil ne dit pas : le loyer d'un logement précis, le loyer d'une
commune à l'intérieur de l'agglomération, les charges, ni ce qu'un ménage
donné peut se permettre. Un loyer médian observé n'est pas un budget.

Usage :
    python3 outils/collecter-loyers.py
    python3 outils/collecter-loyers.py --base http://127.0.0.1:8000
    python3 outils/collecter-loyers.py --verifier
"""
from __future__ import annotations

import argparse
import hashlib
import http.client
import json
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import date, datetime
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
# Les URL tiennent sur une seule ligne, sans concaténation : la sentinelle de
# relecture lit le texte du fichier, et deux fragments collés y apparaissent
# comme deux URL tronquées — une source fantôme qu'elle refuserait de signer.
JEU = "https://www.data.gouv.fr/api/1/datasets/resultats-nationaux-des-observatoires-locaux-des-loyers/"
FICHE = "https://www.data.gouv.fr/datasets/resultats-nationaux-des-observatoires-locaux-des-loyers"
TABULAIRE = "https://tabular-api.data.gouv.fr/api/resources/{ressource}/data/"
CHEMIN_JEU = "/api/1/datasets/resultats-nationaux-des-observatoires-locaux-des-loyers/"
CHEMIN_TABULAIRE = "/tabular/{ressource}/data/"
PRODUCTEUR = "Réseau des observatoires locaux des loyers (OLL), animé par l’ANIL"
LICENCE = "Licence Ouverte 2.0 (lov2)"
LICENCES_OUVERTES = {"lov2", "fr-lo"}
SORTIE = RACINE / "assets" / "data" / "vie-chere" / "loyers.json"
MOTIF_RESSOURCE = re.compile(r"^Loyers (?P<annee>\d{4}) dans les agglom")
MOTIF_OBSERVATOIRE = re.compile(r"^B(?:\d{2}|2A|2B)\d{2}$")
#: Un nom de territoire qui n'a pas une seule minuscule est un code : la base
#: nationale contient au moins une ligne dont l'agglomération s'appelle `L7500`.
#: La publier telle quelle donnerait un tableau avec une ligne qui n'est pas un
#: lieu. Elle est écartée, et son nombre déclaré.
MOTIF_NOM_DE_CODE = re.compile(r"^[A-Z0-9 ]+$")
MINIMUM_TERRITOIRES = 30
MAXIMUM_LIGNES = 200
LOYER_PLAUSIBLE = (3.0, 40.0)
MENSUEL_PLAUSIBLE = (100, 4_000)
SURFACE_PLAUSIBLE = (10, 200)
NOMBRE_PLAUSIBLE = (1, 10_000_000)
COLONNES = (
    "Observatory",
    "agglomeration",
    "Data_year",
    "loyer_median",
    "loyer_mensuel_median",
    "surface_moyenne",
    "nombre_observations",
    "methodologie_production",
)
#: Les cinq colonnes qui découpent une agglomération en sous-populations. Quand
#: elles sont toutes vides, la ligne décrit l'ensemble des logements observés :
#: c'est la seule que la page publie, pour ne pas comparer un studio à un T5.
FILTRE_ENSEMBLE = {
    "Zone_complementaire__isnull": "true",
    "Type_habitat__isnull": "true",
    "epoque_construction_homogene__isnull": "true",
    "anciennete_locataire_homogene__isnull": "true",
    "nombre_pieces_homogene__isnull": "true",
}


class Refus(Exception):
    """Une source ne permet pas de publier : rien n'est écrit."""


def lire(url: str, essais: int = 3) -> bytes:
    derniere: Exception | None = None
    demande = urllib.request.Request(url, headers={"Accept-Encoding": "identity"})
    for _ in range(essais):
        try:
            with urllib.request.urlopen(demande, timeout=120) as reponse:  # noqa: S310
                return reponse.read()
        # Le 14 novembre 2026, la collecte de DVF est tombée sur un
        # `RemoteDisconnected` : le serveur a fermé la connexion sans répondre.
        # Ce n'est pas une `URLError` — c'est une `OSError` de bas niveau —, donc
        # elle échappait aux trois essais et sortait en traceback au lieu d'un
        # refus nommé. Une connexion coupée est une panne passagère : elle mérite
        # un essai de plus, et un refus lisible si elle persiste.
        except (OSError, http.client.HTTPException) as erreur:
            derniere = erreur
    raise Refus(f"source injoignable : {url} ({derniere})")


def lire_json(url: str) -> dict:
    contenu = lire(url)
    try:
        return json.loads(contenu.decode("utf-8-sig"))
    except (ValueError, UnicodeDecodeError) as erreur:
        raise Refus(f"réponse illisible : {url} ({erreur})") from erreur


def url_jeu(base: str) -> str:
    return f"{base}{CHEMIN_JEU}" if base else JEU


def url_tabulaire(base: str, ressource: str) -> str:
    if base:
        return f"{base}{CHEMIN_TABULAIRE.format(ressource=ressource)}"
    return TABULAIRE.format(ressource=ressource)


def resoudre_ressource(fiche: dict) -> tuple[str, int, str, str]:
    """La ressource de l'année la plus récente, et rien d'autre.

    La fiche liste une ressource par année, avec leur date de dernière
    modification. Choisir « la première » publierait un millésime périmé le jour
    où la source ajoute une année en fin de liste.
    """
    licence = str(fiche.get("license") or "").strip()
    if licence not in LICENCES_OUVERTES:
        raise Refus(f"licence non ouverte : {licence!r} — rien n'est publié")
    candidates: list[tuple[int, dict]] = []
    for ressource in fiche.get("resources") or []:
        titre = str(ressource.get("title") or "")
        format_lu = str(ressource.get("format") or "")
        trouve = MOTIF_RESSOURCE.match(titre)
        if not trouve or "csv" not in format_lu.lower():
            continue
        candidates.append((int(trouve.group("annee")), ressource))
    if not candidates:
        raise Refus(
            "aucune ressource « Loyers AAAA dans les agglomérations » au format csv : "
            "la fiche a changé, et choisir une autre ressource reviendrait à choisir un chiffre"
        )
    annee, ressource = max(candidates, key=lambda couple: couple[0])
    identifiant = str(ressource.get("id") or "").strip()
    if not identifiant:
        raise Refus(f"ressource {annee} sans identifiant")
    return identifiant, annee, str(ressource.get("title") or ""), str(ressource.get("last_modified") or "")


def pages(base: str, ressource: str) -> tuple[list[dict], int]:
    """Lit toutes les pages du filtre, et refuse une pagination qui déraille."""
    url = url_tabulaire(base, ressource)
    parametres = dict(FILTRE_ENSEMBLE)
    parametres["columns"] = ",".join(COLONNES)
    parametres["page_size"] = "100"
    lignes: list[dict] = []
    total: int | None = None
    page = 1
    while True:
        parametres["page"] = str(page)
        reponse = lire_json(f"{url}?{urllib.parse.urlencode(parametres)}")
        paquet = reponse.get("data")
        if not isinstance(paquet, list):
            raise Refus(f"page {page} sans champ « data » : format de l’API tabulaire inattendu")
        lignes.extend(paquet)
        meta = reponse.get("meta") or {}
        annonce = meta.get("total")
        if total is None:
            if not isinstance(annonce, int):
                raise Refus("l’API tabulaire ne dit pas combien de lignes elle sert")
            total = annonce
            if total > MAXIMUM_LIGNES:
                raise Refus(
                    f"{total} ligne(s) pour le filtre « ensemble des logements », au plus "
                    f"{MAXIMUM_LIGNES} attendues : le filtre ne sélectionne plus une agglomération "
                    "mais des sous-populations, et comparer des Studios à des T5 serait un contresens"
                )
            if total < MINIMUM_TERRITOIRES:
                raise Refus(
                    f"{total} territoire(s) observé(s), au moins {MINIMUM_TERRITOIRES} attendus : "
                    "une réponse tronquée ne doit pas devenir une liste à moitié vide"
                )
        if not paquet or len(lignes) >= total:
            break
        page += 1
        if page > 20:
            raise Refus(f"pagination interminable : plus de 20 pages pour {total} ligne(s)")
    if len(lignes) < total:
        raise Refus(f"{len(lignes)} ligne(s) reçue(s) pour {total} annoncée(s) : réponse tronquée")
    return lignes, total


#: Le 15 novembre 2026, la page a affiché « Grand Chambéry et Cur de Savoie » :
#: la source publie ce nom avec le caractère U+009C à la place du « œ ». U+009C
#: est l’octet 0x9C de la page de codes Windows, celle qui encode précisément
#: cette ligature ; le nom a donc été écrit en Windows puis relu comme de
#: l’Unicode. Rétablir la lettre que l’octet désigne n’invente rien — c’est le
#: seul sens que cet octet ait jamais eu —, à condition de le dire : le nombre
#: de noms réparés est publié dans la provenance, et la page l’écrit. Un
#: caractère qu’aucune lettre ne désigne (0x81, 0x8D, 0x8F, 0x90, 0x9D) fait
#: refuser la collecte : un nom illisible ne se publie pas.
WINDOWS: dict[int, str] = {}
for _octet in range(0x80, 0xA0):
    try:
        WINDOWS[_octet] = bytes([_octet]).decode("cp1252")
    except UnicodeDecodeError:
        continue
del _octet


def reparer_nom(nom: str) -> tuple[str, bool]:
    """Rétablit les lettres qu’une page de codes Windows a laissées en caractères de contrôle."""
    sortie: list[str] = []
    repare = False
    for caractere in nom:
        point = ord(caractere)
        if 0x80 <= point <= 0x9F:
            if point not in WINDOWS:
                raise Refus(
                    f"{nom!r} — caractère de contrôle U+{point:04X} sans lettre connue : nom illisible"
                )
            sortie.append(WINDOWS[point])
            repare = True
        else:
            sortie.append(caractere)
    return "".join(sortie), repare


def nombre(valeur: object, borne: tuple[float, float], etiquette: str, territoire: str) -> float:
    if isinstance(valeur, bool) or not isinstance(valeur, (int, float)):
        raise Refus(f"{territoire} — {etiquette} absente ou non numérique : {valeur!r}")
    if not borne[0] <= float(valeur) <= borne[1]:
        raise Refus(
            f"{territoire} — {etiquette} {valeur} hors de {borne[0]} à {borne[1]}, fichier suspect"
        )
    return float(valeur)


def territoires(lignes: list[dict], annee: int) -> tuple[list[dict], list[str], list[str]]:
    resultat: list[dict] = []
    vus: set[tuple[str, str]] = set()
    ecartes: list[str] = []
    repares: list[str] = []
    for ligne in lignes:
        observatoire = str(ligne.get("Observatory") or "").strip()
        nom = str(ligne.get("agglomeration") or "").strip()
        nom, repare = reparer_nom(nom)
        if repare:
            repares.append(nom)
        if not MOTIF_OBSERVATOIRE.match(observatoire):
            raise Refus(f"code d’observatoire inattendu : {observatoire!r} pour {nom!r}")
        if not nom:
            raise Refus(f"agglomération sans nom pour l’observatoire {observatoire}")
        if MOTIF_NOM_DE_CODE.match(nom):
            # Ni refus global, ni publication d'une ligne qui n'est pas un lieu :
            # la ligne est écartée et comptée.
            ecartes.append(nom)
            continue
        if ligne.get("Data_year") != annee:
            raise Refus(
                f"{nom} — année {ligne.get('Data_year')!r} dans une ressource annoncée {annee} : "
                "un millésime mélangé n’est plus un millésime"
            )
        cle = (observatoire, nom)
        if cle in vus:
            raise Refus(f"deux lignes pour le même territoire : {nom} ({observatoire})")
        vus.add(cle)
        resultat.append(
            {
                "observatoire": observatoire,
                "nom": nom,
                "loyer_median": round(nombre(ligne.get("loyer_median"), LOYER_PLAUSIBLE, "loyer médian", nom), 2),
                "loyer_mensuel_median": int(
                    nombre(ligne.get("loyer_mensuel_median"), MENSUEL_PLAUSIBLE, "loyer mensuel médian", nom)
                ),
                "surface_moyenne": int(
                    nombre(ligne.get("surface_moyenne"), SURFACE_PLAUSIBLE, "surface moyenne", nom)
                ),
                # `nombre_logements` n'est **pas** publié : la relecture des
                # données du 14 novembre 2026 a trouvé `4` pour les quatre lignes
                # parisiennes, alors que leurs observations valent de 3 879 à
                # 10 817. Un champ dont le sens n'est pas établi ne devient pas
                # une colonne « logements observés » : ce serait notre chiffre,
                # pas celui de la source. Seul le nombre d'observations est
                # publié, et l'absence s'y écrit `null`, jamais zéro.
                "observations": (
                    int(nombre(ligne.get("nombre_observations"), NOMBRE_PLAUSIBLE, "nombre d’observations", nom))
                    if ligne.get("nombre_observations") is not None
                    else None
                ),
                "methode_production": str(ligne.get("methodologie_production") or "").strip() or "non précisée",
            }
        )
    if len(resultat) < MINIMUM_TERRITOIRES:
        raise Refus(
            f"{len(resultat)} territoire(s) retenu(s), au moins {MINIMUM_TERRITOIRES} attendus"
        )
    resultat.sort(key=lambda territoire: (territoire["nom"].lower(), territoire["observatoire"]))
    return resultat, ecartes, repares


def collecter(base: str) -> dict:
    fiche = lire_json(url_jeu(base))
    ressource, annee, titre, modifiee = resoudre_ressource(fiche)
    lignes, total = pages(base, ressource)
    donnees, ecartes, repares = territoires(lignes, annee)
    return {
        "collecte_le": date.today().isoformat(),
        "annee": annee,
        "unite": "€/m² de surface habitable et par mois",
        "methode": (
            "médiane des loyers observés par l’observatoire local des loyers, "
            "échelle de l’agglomération, ensemble des logements sans découpage par "
            "époque, ancienneté, type ni nombre de pièces"
        ),
        "ne_dit_pas": (
            "Ni le loyer d’un logement précis, ni celui d’une commune à l’intérieur de "
            "l’agglomération, ni les charges, ni ce qu’un ménage donné peut se permettre. "
            "Le nombre de logements publié par la source n’est pas repris : il vaut 4 pour "
            "les quatre lignes parisiennes, ce qui n’est pas un compte de logements."
        ),
        "source": {
            "producteur": PRODUCTEUR,
            "licence": LICENCE,
            "jeu": JEU,
            "fiche": FICHE,
            "api": TABULAIRE.format(ressource=ressource),
            "ressource_id": ressource,
            "ressource_titre": titre,
            "date_ressource": modifiee,
            "lignes": total,
            "lignes_ecartees": ecartes,
            "noms_repares": repares,
            "sha256": hashlib.sha256(json.dumps(lignes, sort_keys=True).encode("utf-8")).hexdigest(),
        },
        "territoires": donnees,
    }


def verifier(chemin: Path) -> int:
    if not chemin.is_file():
        print(f"ERREUR — aucune collecte dans {chemin} : la page doit le dire, pas l'inventer.", file=sys.stderr)
        return 1
    try:
        donnees = json.loads(chemin.read_text(encoding="utf-8"))
    except json.JSONDecodeError as erreur:
        print(f"ERREUR — fichier illisible : {erreur}", file=sys.stderr)
        return 1
    erreurs: list[str] = []
    source = donnees.get("source") or {}
    for cle in ("producteur", "licence", "jeu", "fiche", "ressource_id", "ressource_titre", "date_ressource", "sha256"):
        if not source.get(cle):
            erreurs.append(f"provenance incomplète : « {cle} » absent")
    if "Ouverte" not in str(source.get("licence", "")):
        erreurs.append(f"licence non ouverte : {source.get('licence')!r}")
    annee = donnees.get("annee")
    if not isinstance(annee, int) or not 2010 <= annee <= 2100:
        erreurs.append(f"année de données invraisemblable : {annee!r}")
    collecte = str(donnees.get("collecte_le", ""))
    try:
        if datetime.strptime(collecte, "%Y-%m-%d").date() > date.today():
            erreurs.append(f"date de collecte dans le futur : {collecte}")
    except ValueError:
        erreurs.append(f"date de collecte illisible : {collecte!r}")
    liste = donnees.get("territoires") or []
    if len(liste) < MINIMUM_TERRITOIRES:
        erreurs.append(f"{len(liste)} territoire(s) au lieu de {MINIMUM_TERRITOIRES}")
    vus: set[tuple[str, str]] = set()
    for territoire in liste:
        nom = str(territoire.get("nom") or "")
        code = str(territoire.get("observatoire") or "")
        if not nom:
            erreurs.append("territoire sans nom")
        if not MOTIF_OBSERVATOIRE.match(code):
            erreurs.append(f"{nom} : code d’observatoire inattendu {code!r}")
        if (code, nom) in vus:
            erreurs.append(f"{nom} ({code}) : territoire en double")
        vus.add((code, nom))
        for cle, borne in (
            ("loyer_median", LOYER_PLAUSIBLE),
            ("loyer_mensuel_median", MENSUEL_PLAUSIBLE),
            ("surface_moyenne", SURFACE_PLAUSIBLE),
        ):
            valeur = territoire.get(cle)
            if not isinstance(valeur, (int, float)) or not borne[0] <= float(valeur) <= borne[1]:
                erreurs.append(f"{nom} : {cle} invraisemblable {valeur!r}")
        if "logements" in territoire:
            erreurs.append(f"{nom} : un nombre de logements est publié alors que la source ne le permet pas")
        if "observations" not in territoire:
            erreurs.append(f"{nom} : le nombre d’observations n’est pas déclaré du tout")
        elif territoire["observations"] is not None and (
            not isinstance(territoire["observations"], int) or territoire["observations"] < 1
        ):
            erreurs.append(f"{nom} : nombre d’observations invraisemblable {territoire['observations']!r}")
        if MOTIF_NOM_DE_CODE.match(nom):
            erreurs.append(f"{nom} : nom de territoire qui est un code")
        if any(0x80 <= ord(caractere) <= 0x9F for caractere in nom):
            erreurs.append(f"{nom!r} : nom de territoire avec un caractère de contrôle non réparé")
    if erreurs:
        print("ÉCHEC — collecte des loyers", file=sys.stderr)
        for erreur in erreurs:
            print(f"    {erreur}", file=sys.stderr)
        return 1
    ecartees = source.get("lignes_ecartees") or []
    print(
        f"Loyers conformes : {len(liste)} territoires observés en {annee}, collecte du {collecte}, "
        f"licence {source.get('licence')}, ressource « {source.get('ressource_titre')} »"
        + (f", {len(ecartees)} ligne(s) écartée(s) pour nom de territoire remplacé par un code." if ecartees else ".")
        + (
            f" {len(repares)} nom(s) réparé(s) depuis la page de codes Windows : {', '.join(repares)}."
            if (repares := source.get("noms_repares") or [])
            else ""
        )
    )
    return 0


def principal() -> int:
    analyseur = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    analyseur.add_argument("--sortie", type=Path, default=SORTIE)
    analyseur.add_argument("--base", default="", help="racine de test (banc HTTP local)")
    analyseur.add_argument("--verifier", action="store_true")
    arguments = analyseur.parse_args()
    if arguments.verifier:
        return verifier(arguments.sortie)
    try:
        donnees = collecter(arguments.base.rstrip("/"))
    except Refus as erreur:
        print(f"ERREUR — {erreur}", file=sys.stderr)
        print("Rien n'a été écrit : les données précédentes restent en place.", file=sys.stderr)
        return 1
    arguments.sortie.parent.mkdir(parents=True, exist_ok=True)
    arguments.sortie.write_text(
        json.dumps(donnees, ensure_ascii=False, indent=1, sort_keys=True) + "\n", encoding="utf-8"
    )
    try:
        nom = arguments.sortie.relative_to(RACINE).as_posix()
    except ValueError:
        nom = str(arguments.sortie)  # banc : sortie hors du dépôt
    print(
        f"Collecte écrite : {nom} — {len(donnees['territoires'])} territoires, millésime "
        f"{donnees['annee']}, {arguments.sortie.stat().st_size // 1024} Kio."
    )
    return 0


if __name__ == "__main__":
    sys.exit(principal())
