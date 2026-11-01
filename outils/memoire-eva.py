#!/usr/bin/env python3
"""La mémoire d'ÉVA : trois horizons, un pointeur par fait, un graphe dérivé.

Le 1er novembre 2026, le projet savait mesurer ses grilles et vérifier ses
contrôles, mais rien ne répondait à la question la plus simple : « où est écrit
ce que je sais ? ». Un dépôt de 78 documents, un journal de plusieurs dizaines de
décisions et 65 avancées ne se relisent pas à chaque tour — et les relire coûte
exactement ce que ce projet reproche ailleurs : charger beaucoup pour peu.

Trois horizons, et une seule règle : **chaque fait a un seul domicile**.

- **court terme** — ce qui est chaud : les trois dernières décisions du journal,
  les trois dernières avancées, les phases en cours du plan. Recalculé à chaque
  exécution, jamais stocké, donc jamais périmé ; ce sont des renvois (`cache_de`)
  vers les entrées de moyen terme, pas des copies ;
- **moyen terme** — ce qui est décidé : le journal daté, les avancées, les
  dix-neuf initiatives du portefeuille ;
- **long terme** — ce qui est durable : les documents de fond de `docs/rd/`.

Aucune entrée ne recopie un document : elle porte un titre, un résumé de
160 caractères au plus et un **pointeur** (chemin + ligne). La recherche imprime
ce qu'elle a lu — l'index, quelques dizaines de kilo-octets — à côté de la taille
du corpus. C'est la méthode dite « ponytail » dans le dépôt : la queue la plus
courte qui tienne le poisson.

Le graphe est **dérivé**, jamais saisi : Mermaid pour Obsidian et Graphify, DOT
pour les outils de graphe, et les deux disent la même chose.

Ce que ce fichier ne fait pas : il ne comprend pas une question, il retrouve des
mots ; il ne résume pas, il cite la première phrase ; il ne mesure pas la
pertinence, il mesure des millisecondes. Ces refus sont écrits dans la sortie des
commandes, pas seulement ici.

Usage :
    python3 outils/memoire-eva.py --regenerer
    python3 outils/memoire-eva.py --chercher "économie de contexte"
    python3 outils/memoire-eva.py --evaluer
    python3 outils/memoire-eva.py --verifier
"""

from __future__ import annotations

import argparse
import json
import os
import re
import statistics
import sys
import time
import tomllib
import unicodedata
from pathlib import Path

RACINE = Path(os.environ.get("MRSC_RACINE") or Path(__file__).resolve().parent.parent).resolve()
DOSSIER = Path("docs/rd/eva")
INDEX = DOSSIER / "memoire.json"
PLAN = DOSSIER / "plan.toml"
PLAN_MD = DOSSIER / "plan.md"
GRAPHE_MD = DOSSIER / "graphe.md"
GRAPHE_DOT = DOSSIER / "graphe.dot"
JOURNAL = Path("docs/rd/journal.md")
AVANCEES = Path("docs/rd/avancees.toml")
PORTEFEUILLE = Path("docs/rd/portefeuille.toml")
DOCS = Path("docs/rd")

#: Fichiers engendrés depuis une autre source : les indexer dupliquerait le fait
#: et ferait répondre deux fois la même chose, avec deux dates différentes.
ENGENDRES = {"avancees.md", "plan.md", "graphe.md", "journal.md"}

#: Longueur maximale d'un résumé. Au-delà, ce n'est plus un renvoi, c'est une
#: copie — et une copie se désynchronise.
RESUME_MAX = 160

#: Budget déclaré pour une recherche. Il ne compare rien à un humain : il attrape
#: une régression de l'index (une recherche qui passerait de 3 ms à 3 s).
BUDGET_MS = 1500.0

MOTS_VIDES = frozenset(
    """les des une pour que qui dans avec sur par est sont pas plus mais son ses
    cette tout tous ces aux ont été être avoir fait faire aussi comme dont entre
    deux trois chaque sans sous vers lors donc ici elle lui nous vous ils elles
    the and for with that from this not are was""".split()
)


class SourceIllisible(Exception):
    """Une source de la mémoire manque ou ne se lit pas : on ne devine pas."""


def sans_accent(texte: str) -> str:
    decompose = unicodedata.normalize("NFD", texte)
    return "".join(c for c in decompose if unicodedata.category(c) != "Mn")


def mots(texte: str) -> list[str]:
    """Les mots significatifs, sans accent, en minuscules, dédoublonnés et triés.

    Triés pour que deux exécutions rendent le même fichier : un index qui change
    d'ordre à chaque passage rendrait tout contrôle de fraîcheur inutile.
    """
    trouves = re.findall(r"[a-z0-9]+", sans_accent(texte).lower())
    return sorted({mot for mot in trouves if len(mot) >= 4 and mot not in MOTS_VIDES})


def premiere_phrase(texte: str, maxi: int = RESUME_MAX) -> str:
    """La première phrase d'un paragraphe, bornée — jamais une phrase inventée."""
    propre = re.sub(r"\s+", " ", texte).strip()
    if not propre:
        return ""
    fin = re.search(r"(?<=[.!?])\s", propre)
    phrase = propre[: fin.start()] if fin else propre
    if len(phrase) > maxi:
        coupe = phrase[: maxi - 1].rsplit(" ", 1)[0]
        phrase = coupe + "…"
    return phrase


def lire(chemin: Path) -> str:
    try:
        return chemin.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as erreur:
        raise SourceIllisible(f"{chemin} illisible ({erreur})") from erreur


def charger_toml(chemin: Path) -> dict:
    if not chemin.is_file():
        raise SourceIllisible(f"{chemin} introuvable")
    try:
        with chemin.open("rb") as fichier:
            return tomllib.load(fichier)
    except (OSError, tomllib.TOMLDecodeError) as erreur:
        raise SourceIllisible(f"{chemin} illisible ({erreur})") from erreur


def ligne_de(texte: str, motif: str, depuis: int = 0) -> int | None:
    for numero, contenu in enumerate(texte.splitlines()[depuis:], start=depuis + 1):
        if motif in contenu:
            return numero
    return None


# — les trois horizons -------------------------------------------------------


def entrees_long_terme(racine: Path) -> list[dict]:
    """Les documents de fond : un titre, la première phrase, un pointeur."""
    entrees = []
    for chemin in sorted((racine / DOCS).glob("*.md")):
        if chemin.name in ENGENDRES:
            continue
        texte = lire(chemin)
        lignes = texte.splitlines()
        titre, numero_titre = chemin.stem, 1
        for numero, ligne in enumerate(lignes, start=1):
            if ligne.startswith("# "):
                titre, numero_titre = ligne[2:].strip(), numero
                break
        corps = ""
        for ligne in lignes[numero_titre:]:
            if not ligne.strip() or ligne.lstrip().startswith(("#", "|", "-", "*", ">")):
                continue
            corps = ligne
            break
        if not corps:
            # Un document sans phrase liminaire n'a pas de résumé : l'index le dit
            # au lieu d'emprunter le titre et de faire croire à un résumé.
            corps = "(document sans phrase liminaire : ouvrir le fichier)"
        relatif = chemin.relative_to(racine).as_posix()
        entrees.append(
            {
                "id": f"long:{chemin.stem}",
                "horizon": "long",
                "titre": titre,
                "resume": premiere_phrase(corps),
                "source": relatif,
                "ligne": numero_titre,
            }
        )
    return entrees


def _lignes_des_blocs(texte: str, entete: str) -> dict[str, int]:
    """`{identifiant: ligne du [[bloc]]}` — la ligne du bloc, pas celle de l'id."""
    trouves: dict[str, int] = {}
    debut = None
    for numero, ligne in enumerate(texte.splitlines(), start=1):
        if ligne.strip() == entete:
            debut = numero
        elif debut is not None and ligne.startswith("id = "):
            trouves[ligne.split('"')[1]] = debut
            debut = None
    return trouves


def entrees_moyen_terme(racine: Path) -> list[dict]:
    """Le journal, les avancées et les initiatives : ce qui est **décidé**."""
    entrees = []
    texte_journal = lire(racine / JOURNAL)
    for numero, ligne in enumerate(texte_journal.splitlines(), start=1):
        trouve = re.match(r"^## (\d{4}-\d{2}-\d{2}) — (.+)$", ligne)
        if not trouve:
            continue
        date, titre = trouve.group(1), trouve.group(2).strip()
        suite = ""
        for suivante in texte_journal.splitlines()[numero:]:
            if suivante.startswith("#"):
                break
            if not suivante.startswith("- "):
                continue
            # Les puces de gabarit (« **Initiative :** … ») sont identiques d'une
            # entrée à l'autre : les prendre pour résumé donnait soixante résumés
            # égaux, et un index qui répondait toujours la même chose.
            if re.match(r"-\s*\*\*(Initiative|Date|Statut|Preuves?|Contrôles?|Version|Lot|Fichiers?)\b", suivante):
                continue
            suite = suivante[2:]
            break
        propre = re.sub(r"[*`]", "", suite)
        entrees.append(
            {
                "id": f"moyen:journal:{date}:{sans_accent(titre).lower().replace(' ', '-')[:48]}",
                "horizon": "moyen",
                "titre": f"{date} — {titre}",
                "resume": premiere_phrase(propre) or "(entrée sans première puce)",
                "source": JOURNAL.as_posix(),
                "ligne": numero,
            }
        )

    texte_avancees = lire(racine / AVANCEES)
    avancees = charger_toml(racine / AVANCEES).get("avancee", [])
    lignes = _lignes_des_blocs(texte_avancees, "[[avancee]]")
    for avancee in avancees:
        identifiant = str(avancee.get("id") or "")
        if not identifiant:
            continue
        entrees.append(
            {
                "id": f"moyen:avancee:{identifiant}",
                "horizon": "moyen",
                "titre": str(avancee.get("titre") or identifiant),
                "resume": premiere_phrase(str(avancee.get("constat") or "")),
                "source": AVANCEES.as_posix(),
                "ligne": lignes.get(identifiant, 1),
                "date": str(avancee.get("date") or ""),
            }
        )

    texte_portefeuille = lire(racine / PORTEFEUILLE)
    initiatives = charger_toml(racine / PORTEFEUILLE).get("initiative", [])
    lignes_initiatives = _lignes_des_blocs(texte_portefeuille, "[[initiative]]")
    for initiative in initiatives:
        identifiant = str(initiative.get("id") or "")
        if not identifiant:
            continue
        entrees.append(
            {
                "id": f"moyen:branche:{identifiant}",
                "horizon": "moyen",
                "titre": str(initiative.get("titre") or identifiant),
                "resume": premiere_phrase(str(initiative.get("question") or "")),
                "source": PORTEFEUILLE.as_posix(),
                "ligne": lignes_initiatives.get(identifiant, 1),
                "etat": str(initiative.get("etat") or ""),
            }
        )
    return entrees


def entrees_court_terme(moyen: list[dict], plan: dict) -> list[dict]:
    """Ce qui est chaud — des **renvois**, jamais des copies.

    Le cache porte `cache_de` : l'identifiant de l'entrée de moyen terme qu'il
    cite. Un contrôle refuse un renvoi qui ne résout pas, et le compte des
    doublons ignore ces entrées-là, puisqu'elles sont une vue et non un domicile.
    """
    chaudes = []
    journal = sorted(
        (e for e in moyen if e["id"].startswith("moyen:journal:")), key=lambda e: e["titre"]
    )[-3:]
    avancees = sorted(
        (e for e in moyen if e["id"].startswith("moyen:avancee:")),
        key=lambda e: e.get("date", ""),
    )[-3:]
    for rang, cible in enumerate(list(reversed(journal)) + list(reversed(avancees)), start=1):
        chaudes.append(
            {
                "id": f"court:{rang}",
                "horizon": "court",
                "titre": cible["titre"],
                "resume": cible["resume"],
                "source": cible["source"],
                "ligne": cible["ligne"],
                "cache_de": cible["id"],
            }
        )
    for phase in plan.get("phase", []):
        if phase.get("statut") not in {"en-cours", "en-attente"}:
            continue
        chaudes.append(
            {
                "id": f"court:phase:{phase.get('id')}",
                "horizon": "court",
                "titre": f"Phase {phase.get('id')} — {phase.get('titre')}",
                "resume": premiere_phrase(str(phase.get("objectif") or "")),
                "source": PLAN.as_posix(),
                "ligne": ligne_de(lire(RACINE / PLAN), f'id = "{phase.get("id")}"') or 1,
                "cache_de": f"phase:{phase.get('id')}",
            }
        )
    return chaudes


def construire_index(racine: Path) -> dict:
    plan = charger_toml(racine / PLAN)
    moyen = entrees_moyen_terme(racine)
    court = entrees_court_terme(moyen, plan)
    long_terme = entrees_long_terme(racine)
    entrees = court + moyen + long_terme

    corpus = 0
    for source in {entree["source"] for entree in entrees}:
        chemin = racine / source
        if chemin.is_file():
            corpus += chemin.stat().st_size

    index = {
        "version": 1,
        "regle": {
            "court": "les trois dernières décisions, les trois dernières avancées, "
            "les phases en cours — des renvois, recalculés à chaque exécution",
            "moyen": "le journal daté, les avancées, les initiatives du portefeuille",
            "long": "les documents de fond de docs/rd/",
            "resume_max": RESUME_MAX,
            "methode": "ponytail — un résumé court, un pointeur long, aucune copie",
        },
        "entrees": sorted(entrees, key=lambda e: e["id"]),
        "compte": {
            horizon: sum(1 for e in entrees if e["horizon"] == horizon)
            for horizon in ("court", "moyen", "long")
        },
        "poids_corpus": corpus,
    }
    return index


def rendre_index(index: dict) -> str:
    return json.dumps(index, ensure_ascii=False, indent=1) + "\n"


# — le graphe ----------------------------------------------------------------


def construire_graphe(racine: Path) -> dict:
    plan = charger_toml(racine / PLAN)
    portefeuille = charger_toml(racine / PORTEFEUILLE)
    avancees = charger_toml(racine / AVANCEES).get("avancee", [])

    noeuds: dict[str, dict] = {}
    aretes: set[tuple[str, str, str]] = set()

    def noeud(identifiant: str, genre: str) -> None:
        noeuds.setdefault(identifiant, {"id": identifiant, "genre": genre})

    for phase in plan.get("phase", []):
        identifiant = f"phase:{phase.get('id')}"
        noeud(identifiant, "phase")
        for dependance in phase.get("depends_on", []):
            aretes.add((f"phase:{dependance}", identifiant, "prépare"))
        for cle in ("preuve", "test"):
            valeur = phase.get(cle)
            if valeur:
                noeud(valeur, "fichier")
                aretes.add((identifiant, valeur, "prouvée par" if cle == "preuve" else "éprouvée par"))
        for branche in phase.get("branches", []):
            aretes.add((f"branche:{branche}", identifiant, "servie par"))

    for initiative in portefeuille.get("initiative", []):
        noeud(f"branche:{initiative.get('id')}", "branche")
    for avancee in avancees:
        identifiant = f"avancee:{avancee.get('id')}"
        noeud(identifiant, "avancee")
        for preuve in avancee.get("preuves", [])[:4]:
            noeud(preuve, "fichier")
            aretes.add((identifiant, preuve, "prouvée par"))
        for branche in avancee.get("initiatives", []):
            aretes.add((f"branche:{branche}", identifiant, "a produit"))

    return {
        "noeuds": [noeuds[cle] for cle in sorted(noeuds)],
        "aretes": [{"de": a, "vers": b, "genre": g} for a, b, g in sorted(aretes)],
    }


def rendre_dot(graphe: dict) -> str:
    formes = {"phase": "box", "branche": "ellipse", "avancee": "note", "fichier": "plaintext"}
    lignes = [
        "// Graphe de la mémoire d'ÉVA — dérivé de plan.toml, portefeuille.toml et avancees.toml.",
        "// Ne rien éditer ici : régénérer par `python3 outils/memoire-eva.py --regenerer`.",
        "digraph memoire {",
        '  rankdir="LR";',
        '  node [fontname="Helvetica", fontsize=10];',
        '  edge [fontsize=8, color="#8899aa"];',
    ]
    for noeud in graphe["noeuds"]:
        etiquette = noeud["id"].replace('"', "'")
        lignes.append(f'  "{noeud["id"]}" [shape={formes.get(noeud["genre"], "box")}, label="{etiquette}"];')
    for arete in graphe["aretes"]:
        lignes.append(f'  "{arete["de"]}" -> "{arete["vers"]}" [label="{arete["genre"]}"];')
    lignes.append("}")
    return "\n".join(lignes) + "\n"


def rendre_mermaid(graphe: dict) -> str:
    """Une carte lisible dans Obsidian : branches et phases.

    Les avancées et les fichiers restent dans le DOT. Les faire figurer ici
    donnait 96 nœuds et un diagramme que personne n'ouvre ; or une carte qu'on
    n'ouvre pas ne sert à rien, et le détail est déjà dans le plan.
    """
    gardes = {"phase", "branche"}
    retenues = [n for n in graphe["noeuds"] if n["genre"] in gardes]
    gardees = {n["id"] for n in retenues}
    lignes = [
        "# Graphe de la mémoire d'ÉVA",
        "",
        "Dérivé de `plan.toml`, `portefeuille.toml` et `avancees.toml` par",
        "`python3 outils/memoire-eva.py --regenerer`. Ne rien éditer ici.",
        "",
        "```mermaid",
        "flowchart LR",
    ]
    defident = {n["id"]: "n_" + re.sub(r"[^a-z0-9]+", "_", sans_accent(n["id"]).lower()) for n in retenues}
    for noeud in retenues:
        etiquette = noeud["id"].replace('"', "'")
        lignes.append(f'  {defident[noeud["id"]]}["{etiquette}"]')
    identifiants = defident
    for arete in graphe["aretes"]:
        if arete["de"] in gardees and arete["vers"] in gardees:
            lignes.append(f'  {identifiants[arete["de"]]} -->|{arete["genre"]}| {identifiants[arete["vers"]]}')
    lignes += ["```", "", "Le détail fichier par fichier est dans `graphe.dot`.", ""]
    return "\n".join(lignes)


# — le rendu du plan ---------------------------------------------------------


def rendre_plan_md(plan: dict, graphe: dict) -> str:
    meta = plan.get("meta", {})
    phases = plan.get("phase", [])
    statuts: dict[str, int] = {}
    for phase in phases:
        statuts[phase.get("statut", "?")] = statuts.get(phase.get("statut", "?"), 0) + 1
    lignes = [
        "# Plan complet de R&D, d'innovation et de prospective — mémoire et continuité d'ÉVA",
        "",
        f"**Note de travail datée du {meta.get('date')}. Rendu depuis `plan.toml` — ne pas éditer.**",
        "",
        meta.get("cadre", ""),
        "",
        f"**Statuts :** {len(phases)} phases — "
        + ", ".join(f"{nombre} {statut}" for statut, nombre in sorted(statuts.items()))
        + ".",
        "",
        "## Ce qui est une fiction de conception",
        "",
        meta.get("fiction", ""),
        "",
        "## Ce que ce plan ne décide pas",
        "",
        meta.get("hors_plan", ""),
        "",
        "## Les phases",
        "",
        "| Phase | Horizon | Statut | Test | Branches servies |",
        "| --- | --- | --- | --- | --- |",
    ]
    for phase in phases:
        branches = ", ".join(f"`{b}`" for b in phase.get("branches", [])) or "—"
        lignes.append(
            f"| [`{phase.get('id')}`](#{phase.get('id')}) | {phase.get('horizon')} | "
            f"{phase.get('statut')} | `{phase.get('test')}` | {branches} |"
        )
    for phase in phases:
        lignes += [
            "",
            f"### {phase.get('id')}",
            "",
            f"**{phase.get('titre')}** — horizon {phase.get('horizon')}, statut "
            f"`{phase.get('statut')}`.",
            "",
            phase.get("objectif", ""),
            "",
            f"- **Preuve :** `{phase.get('preuve')}`",
            f"- **Test :** `{phase.get('test')}`",
            f"- **Dépend de :** "
            + (", ".join(f"`{d}`" for d in phase.get("depends_on", [])) or "rien"),
            f"- **Limite :** {phase.get('limite', '')}",
        ]
        if phase.get("condition"):
            lignes.append(f"- **Condition de révision :** {phase['condition']}")
    lignes += [
        "",
        "## Le graphe",
        "",
        f"{len(graphe['noeuds'])} nœuds et {len(graphe['aretes'])} arêtes, dérivés de ce plan, "
        "du portefeuille et des avancées.",
        "",
        "- `graphe.md` — diagramme Mermaid, lisible dans Obsidian ou Graphify ;",
        "- `graphe.dot` — même graphe, fichiers compris, pour les outils de graphe ;",
        "- `memoire.json` — l'index à trois horizons, un résumé court et un pointeur par fait.",
        "",
        "## Comment s'en servir",
        "",
        "```sh",
        "python3 outils/memoire-eva.py --chercher \"gouttière conteneur\"",
        "python3 outils/memoire-eva.py --evaluer",
        "python3 outils/memoire-eva.py --verifier",
        "python3 outils/verifier-plan-eva.py",
        "```",
        "",
        "## Limites",
        "",
        "- L'index retrouve des **mots**, pas un sens : une question mal formulée ne trouve rien.",
        "- Le résumé est la première phrase de la source, pas un résumé écrit pour le sujet.",
        "- Le graphe ne porte aucune information qui ne soit déjà écrite ailleurs.",
        "- Rien ici ne démontre une conscience, un corps ou une parité de délai avec une personne : "
        "les phases correspondantes sont `hors-portee` ou `en-attente`, avec leur condition.",
        "",
    ]
    return "\n".join(lignes)


def rendre_plan_md_seul(racine: Path) -> str:
    return rendre_plan_md(charger_toml(racine / PLAN), construire_graphe(racine))


# — recherche, mesure, contrôle ----------------------------------------------


def chercher(index: dict, requete: str, limite: int = 5) -> list[dict]:
    """Le score est grossier et assumé : titre, puis mots, puis résumé."""
    jetons = mots(requete)
    if not jetons:
        return []
    resultats = []
    for entree in index["entrees"]:
        dans_titre = sum(1 for j in jetons if j in sans_accent(entree["titre"]).lower())
        dans_mots = sum(1 for j in jetons if j in mots(entree["titre"] + " " + entree["resume"]))
        dans_resume = sum(1 for j in jetons if j in sans_accent(entree["resume"]).lower())
        score = 3 * dans_titre + 2 * dans_mots + dans_resume
        if score:
            resultats.append({"score": score, "entree": entree})
    # À score égal, le **domicile** passe avant son renvoi : afficher deux fois le
    # même fait, une fois en court terme et une fois en moyen, gaspille la place
    # qu'on cherchait à économiser.
    resultats.sort(key=lambda r: (-r["score"], r["entree"].get("cache_de") is not None, r["entree"]["id"]))
    vus: set[tuple] = set()
    gardes = []
    for resultat in resultats:
        cle = (resultat["entree"]["source"], resultat["entree"]["ligne"])
        if cle in vus:
            continue
        vus.add(cle)
        gardes.append(resultat)
    return gardes[:limite]


def poids_index(index: dict) -> int:
    return len(rendre_index(index).encode("utf-8"))


def evaluer(index: dict) -> dict:
    """Chronomètre dix recherches et rend la médiane, le maximum et le budget."""
    frequences: dict[str, int] = {}
    for entree in index["entrees"]:
        for mot in set(mots(entree["titre"] + " " + entree["resume"])):
            frequences[mot] = frequences.get(mot, 0) + 1
    requetes = [mot for mot, _ in sorted(frequences.items(), key=lambda kv: (-kv[1], kv[0]))[:10]]
    durees = []
    trouves = 0
    for requete in requetes:
        debut = time.perf_counter()
        resultats = chercher(index, requete, limite=10)
        durees.append((time.perf_counter() - debut) * 1000)
        trouves += 1 if resultats else 0
    return {
        "requetes": requetes,
        "median_ms": round(statistics.median(durees), 3) if durees else 0.0,
        "max_ms": round(max(durees), 3) if durees else 0.0,
        "budget_ms": BUDGET_MS,
        "sans_resultat": len(requetes) - trouves,
    }


def verifier(racine: Path, index: dict) -> list[str]:
    erreurs: list[str] = []
    vus: dict[str, int] = {}
    for entree in index["entrees"]:
        identifiant = entree["id"]
        vus[identifiant] = vus.get(identifiant, 0) + 1
        if not entree.get("titre"):
            erreurs.append(f"{identifiant} : entrée sans titre")
        resume = entree.get("resume") or ""
        if not resume:
            erreurs.append(f"{identifiant} : entrée sans résumé")
        if len(resume) > RESUME_MAX + 1:
            erreurs.append(f"{identifiant} : résumé de {len(resume)} caractères (max {RESUME_MAX})")
        if "\n" in resume:
            erreurs.append(f"{identifiant} : résumé sur plusieurs lignes")
        source = racine / str(entree.get("source") or "")
        if not source.is_file():
            erreurs.append(f"{identifiant} : pointeur mort vers {entree.get('source')}")
            continue
        nombre = len(lire(source).splitlines())
        if not isinstance(entree.get("ligne"), int) or not 1 <= entree["ligne"] <= max(nombre, 1):
            erreurs.append(
                f"{identifiant} : ligne {entree.get('ligne')} hors de {entree.get('source')} "
                f"({nombre} lignes)"
            )
        if entree.get("cache_de"):
            cible = entree["cache_de"]
            if cible.startswith("phase:"):
                if cible.split(":", 1)[1] not in {
                    p.get("id") for p in charger_toml(racine / PLAN).get("phase", [])
                }:
                    erreurs.append(f"{identifiant} : renvoi vers une phase inconnue ({cible})")
            elif not any(e["id"] == cible for e in index["entrees"]):
                erreurs.append(f"{identifiant} : renvoi vers une entrée inconnue ({cible})")

    for identifiant, nombre in sorted(vus.items()):
        if nombre > 1:
            erreurs.append(f"{identifiant} : {nombre} entrées portent le même identifiant")

    # Deux entrées de même horizon, même source et même résumé : le fait est écrit
    # deux fois. Les renvois de court terme sont exclus — ce sont des vues.
    # Le journal est une suite datée : deux entrées peuvent commencer par la même
    # phrase de gabarit sans que le fait soit écrit deux fois. Ce sont les
    # documents de fond et les avancées qui promettent un fait par domicile.
    vues: dict[tuple, str] = {}
    for entree in index["entrees"]:
        if entree.get("cache_de") or entree["id"].startswith("moyen:journal:"):
            continue
        cle = (entree["horizon"], entree["source"], entree["resume"])
        if cle in vues:
            erreurs.append(
                f"{entree['id']} et {vues[cle]} : même fait écrit deux fois "
                f"({entree['source']}, même résumé)"
            )
        else:
            vues[cle] = entree["id"]

    for horizon in ("court", "moyen", "long"):
        if not index["compte"].get(horizon):
            erreurs.append(f"horizon « {horizon} » vide — un des trois n'a rien à dire")

    regenere = construire_index(racine)
    for chemin, attendu in (
        (INDEX, rendre_index(regenere)),
        (GRAPHE_MD, rendre_mermaid(construire_graphe(racine))),
        (GRAPHE_DOT, rendre_dot(construire_graphe(racine))),
        (PLAN_MD, rendre_plan_md_seul(racine)),
    ):
        disque = racine / chemin
        if not disque.is_file():
            erreurs.append(f"{chemin} absent — lancer `--regenerer`")
        elif disque.read_text(encoding="utf-8") != attendu:
            erreurs.append(
                f"{chemin} n'est plus le rendu de ses sources — lancer `--regenerer` "
                "et relire la différence"
            )
    return erreurs


def ecrire(racine: Path, chemin: Path, contenu: str) -> None:
    complet = racine / chemin
    complet.parent.mkdir(parents=True, exist_ok=True)
    complet.write_text(contenu, encoding="utf-8")


def principal(arguments: list[str] | None = None) -> int:
    analyseur = argparse.ArgumentParser(
        description="Mémoire à trois horizons d'ÉVA : index, recherche, graphe, contrôle."
    )
    action = analyseur.add_mutually_exclusive_group(required=True)
    action.add_argument("--regenerer", action="store_true", help="écrire l'index, le graphe et le plan rendu")
    action.add_argument("--chercher", metavar="MOTS", help="retrouver un fait par ses mots")
    action.add_argument("--evaluer", action="store_true", help="chronométrer dix recherches")
    action.add_argument("--verifier", action="store_true", help="contrôler l'index et les rendus")
    analyseur.add_argument("--limite", type=int, default=5, help="nombre de résultats (défaut : 5)")
    options = analyseur.parse_args(arguments)

    try:
        if options.verifier:
            # On contrôle **l'index écrit**, pas celui qu'on vient de recalculer :
            # c'est celui-là qu'un lecteur ouvrirait. Le comparer à sa
            # régénération dit ensuite s'il est encore le rendu de ses sources —
            # deux questions différentes, deux messages différents.
            chemin_index = RACINE / INDEX
            if not chemin_index.is_file():
                print(
                    f"Index absent ({INDEX}) — lancer `--regenerer` : un contrôle sans "
                    "index ne contrôle rien.",
                    file=sys.stderr,
                )
                return 1
            try:
                index = json.loads(chemin_index.read_text(encoding="utf-8"))
            except (OSError, UnicodeDecodeError, json.JSONDecodeError) as erreur:
                print(f"Index illisible ({INDEX}) : {erreur}", file=sys.stderr)
                return 1
            erreurs = verifier(RACINE, index)
            if erreurs:
                for erreur in erreurs:
                    print(f"  - {erreur}", file=sys.stderr)
                print(f"Refusé : {len(erreurs)} écart(s) dans la mémoire.", file=sys.stderr)
                return 1
            print(
                f"Mémoire cohérente : {len(index['entrees'])} entrées "
                f"({index['compte']['court']} court, {index['compte']['moyen']} moyen, "
                f"{index['compte']['long']} long), index de {poids_index(index)} octets "
                f"pour un corpus de {index['poids_corpus']} octets."
            )
            return 0

        if options.regenerer:
            index = construire_index(RACINE)
            graphe = construire_graphe(RACINE)
            ecrire(RACINE, INDEX, rendre_index(index))
            ecrire(RACINE, GRAPHE_MD, rendre_mermaid(graphe))
            ecrire(RACINE, GRAPHE_DOT, rendre_dot(graphe))
            ecrire(RACINE, PLAN_MD, rendre_plan_md(charger_toml(RACINE / PLAN), graphe))
            print(
                f"Mémoire régénérée : {len(index['entrees'])} entrées, "
                f"{len(graphe['noeuds'])} nœuds, {len(graphe['aretes'])} arêtes — "
                f"index {poids_index(index)} octets pour un corpus de "
                f"{index['poids_corpus']} octets "
                f"({100 * poids_index(index) / max(index['poids_corpus'], 1):.1f} %)."
            )
            return 0

        if not (RACINE / INDEX).is_file():
            print(
                f"Index absent ({INDEX}) : lancer `--regenerer`. Aucune recherche "
                "n'est inventée sans index.",
                file=sys.stderr,
            )
            return 2
        index = construire_index(RACINE)

        if options.evaluer:
            mesure = evaluer(index)
            verdict = "dans le budget" if mesure["median_ms"] <= mesure["budget_ms"] else "hors budget"
            print(
                f"Rappel mesuré : médiane {mesure['median_ms']} ms, maximum {mesure['max_ms']} ms "
                f"sur {len(mesure['requetes'])} requêtes, {verdict} (budget déclaré "
                f"{mesure['budget_ms']} ms, {mesure['sans_resultat']} sans résultat)."
            )
            print(
                "  Ce chiffre mesure l'index, pas la pensée : aucune comparaison avec un "
                "temps de réponse humain n'est revendiquée (phase `parite-humaine-des-delais`)."
            )
            return 0 if mesure["median_ms"] <= mesure["budget_ms"] else 1

        resultats = chercher(index, options.chercher, options.limite)
        if not resultats:
            print(
                f"Aucun résultat pour « {options.chercher} » parmi "
                f"{len(index['entrees'])} entrées : le fait n'est peut-être écrit nulle part."
            )
            return 0
        lus = poids_index(index)
        print(
            f"{len(resultats)} résultat(s) — index de {lus} octets sur un corpus de "
            f"{index['poids_corpus']} octets "
            f"({100 * lus / max(index['poids_corpus'], 1):.1f} % lus, {len(index['entrees'])} entrées)."
        )
        for rang, resultat in enumerate(resultats, start=1):
            entree = resultat["entree"]
            print(f"  {rang}. [{entree['horizon']}] {entree['titre']}")
            print(f"     {entree['source']}:{entree['ligne']} — {entree['resume']}")
        return 0
    except SourceIllisible as erreur:
        print(f"Mémoire illisible : {erreur}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(principal())
