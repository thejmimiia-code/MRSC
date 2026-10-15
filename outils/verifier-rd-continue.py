#!/usr/bin/env python3
"""Vérifie hors ligne les consignes, skills et le portefeuille R&D des agents.

Le contrôle vérifie la présence et la cohérence structurelle des méthodes. Il ne
valide aucune affirmation scientifique, qualité pédagogique, source externe ou
relecture humaine. Une échéance dépassée produit une alerte, pas une fausse
validation ni un échec de publication.
"""
from __future__ import annotations

import argparse
import datetime as dt
import re
import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILLS_ROOT = ROOT / ".agents" / "skills"
TITRES_SKILL = (
    "## Quand l’activer",
    "## Entrées",
    "## Méthode",
    "## Livrables",
    "## Garde-fous",
)
PHASES = {"veille", "cadrage", "recherche", "conception", "prototype", "relecture", "essai", "maintien", "mise-en-place"}
ETATS = {"a-cadrer", "en-cours", "bloquee", "a-valider", "a-tester", "en-maintenance", "reportee"}


class Verificateur:
    def __init__(self) -> None:
        self.erreurs: list[str] = []
        self.alertes: list[str] = []
        self.lignes: list[str] = ["# Veille R&D continue — méthode et portefeuille", ""]

    def verifier(self, libelle: str, condition: bool, detail: str = "") -> None:
        etiquette = "OK" if condition else "ÉCHEC"
        ligne = f"{etiquette} — {libelle}" + (f" : {detail}" if detail else "")
        self.lignes.append(ligne)
        print(ligne)
        if not condition:
            self.erreurs.append(libelle)

    def alerter(self, message: str) -> None:
        ligne = f"ALERTE — {message}"
        self.lignes.append(ligne)
        print(ligne)
        self.alertes.append(message)


def charger_toml(verificateur: Verificateur, chemin: Path) -> dict:
    try:
        return tomllib.loads(chemin.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, tomllib.TOMLDecodeError) as erreur:
        verificateur.verifier(f"Lecture de {chemin.relative_to(ROOT)}", False, str(erreur))
        return {}


def verifier_skills(verificateur: Verificateur) -> set[str]:
    index = SKILLS_ROOT / "README.md"
    verifier_agent = ROOT / "AGENTS.md"
    index_text = index.read_text(encoding="utf-8") if index.is_file() else ""
    agent_text = verifier_agent.read_text(encoding="utf-8") if verifier_agent.is_file() else ""
    playbook = ROOT / "docs" / "rd-innovation-continue.md"
    journal = ROOT / "docs" / "rd" / "journal.md"
    verificateur.verifier(
        "Consignes communes, manuel, skills et journal des agents présents",
        bool(agent_text and playbook.is_file() and index_text and journal.is_file()),
        "AGENTS.md, manuel, index et journal de passation",
    )
    journal_text = journal.read_text(encoding="utf-8") if journal.is_file() else ""
    journal_valide = bool(
        re.search(r"(?m)^## \d{4}-\d{2}-\d{2} — ", journal_text)
        and "**Initiative :**" in journal_text
        and "**Contrôles réellement exécutés" in journal_text
        and "**Prochaine action :**" in journal_text
    )
    verificateur.verifier(
        "Journal R&D daté, relié à une initiative et à une prochaine action",
        journal_valide,
    )
    if not agent_text or not index_text:
        return set()

    skills = sorted(SKILLS_ROOT.glob("*/SKILL.md"))
    slugs: set[str] = set()
    for chemin in skills:
        slug = chemin.parent.name
        texte = chemin.read_text(encoding="utf-8")
        frontmatter = re.match(r"\A---\n(.*?)\n---\n", texte, re.DOTALL)
        nom = re.search(r"(?m)^name:\s*([a-z0-9-]+)\s*$", frontmatter.group(1)) if frontmatter else None
        description = re.search(r"(?m)^description:\s*(.{24,})$", frontmatter.group(1)) if frontmatter else None
        titres_absents = [titre for titre in TITRES_SKILL if titre not in texte]
        valide = bool(
            frontmatter and nom and nom.group(1) == slug and description
            and not titres_absents and len(texte) > 600
        )
        verificateur.verifier(
            f"Skill {slug} exploitable",
            valide,
            "métadonnées, activation, entrées, méthode, livrables et garde-fous"
            if valide else "frontmatter ou sections manquants : " + ", ".join(titres_absents),
        )
        if valide:
            slugs.add(slug)
            if f".agents/skills/{slug}/SKILL.md" not in agent_text:
                verificateur.verifier(f"Skill {slug} référencé par AGENTS.md", False)
            elif f"{slug}" not in index_text:
                verificateur.verifier(f"Skill {slug} référencé dans l'index", False)

    verificateur.verifier("Au moins six skills multidisciplinaires définis", len(slugs) >= 6, f"{len(slugs)} skills")
    form = ROOT / ".github" / "ISSUE_TEMPLATE" / "proposition-rd.yml"
    form_text = form.read_text(encoding="utf-8") if form.is_file() else ""
    champs_formulaire = ("Savoir ou domaine peu couvert", "Sources et éléments de preuve", "Confidentialité")
    verificateur.verifier(
        "Un formulaire de proposition R&D demande besoin, preuve et précautions de confidentialité",
        bool(form_text) and all(champ in form_text for champ in champs_formulaire),
    )
    protocole = ROOT / "docs" / "rd" / "protocole-essais-usage.md"
    protocole_text = protocole.read_text(encoding="utf-8") if protocole.is_file() else ""
    verificateur.verifier(
        "Protocole d'essai préparé sans prétendre qu'un test humain a eu lieu",
        "aucun essai auprès de personnes" in protocole_text
        and "arrêter à tout moment" in protocole_text
        and "sans nom ni données personnelles" in protocole_text
        and "droit d'arrêter" in protocole_text,
    )
    return slugs


def verifier_portefeuille(verificateur: Verificateur, skill_slugs: set[str]) -> None:
    chemin = ROOT / "docs" / "rd" / "portefeuille.toml"
    registre = charger_toml(verificateur, chemin)
    meta = registre.get("meta", {})
    initiatives = registre.get("initiative", [])
    date_revue = meta.get("derniere_revue")
    try:
        cadence = int(meta.get("cadence_revue_jours", 0))
    except (TypeError, ValueError):
        cadence = 0
    carte_rel = meta.get("source_cartographie", "")
    catalogue_rel = meta.get("source_catalogue", "")
    sources_presentes = all(
        isinstance(reference, str) and (ROOT / reference).exists()
        for reference in (carte_rel, catalogue_rel)
    )
    verificateur.verifier(
        "Métadonnées du portefeuille et sources de cartographie présentes",
        meta.get("version") == 1 and isinstance(date_revue, dt.date)
        and 7 <= cadence <= 180 and sources_presentes,
        f"cadence {cadence} jours" if sources_presentes else "source de cartographie/catalogue introuvable",
    )
    if isinstance(date_revue, dt.date) and cadence:
        jours = (dt.date.today() - date_revue).days
        prochaine = date_revue + dt.timedelta(days=cadence)
        if jours > cadence:
            verificateur.alerter(
                f"la revue du portefeuille date de {jours} jours; échéance {prochaine.isoformat()} dépassée. "
                "Mettre la date à jour seulement après une revue réellement effectuée."
            )
        else:
            verificateur.lignes.append(f"Prochaine revue R&D à prévoir avant le {prochaine.isoformat()}.")
            print(f"Prochaine revue R&D à prévoir avant le {prochaine.isoformat()}.")

    referentiel_path = ROOT / "docs" / "apprentissage" / "referentiel.toml"
    referentiel = charger_toml(verificateur, referentiel_path)
    domaines_connus = {domaine.get("id") for domaine in referentiel.get("domaine", [])}
    ids: set[str] = set()
    erreurs_initiatives: list[str] = []
    champs = ("id", "titre", "priorite", "phase", "etat", "question", "prochaine_action", "criteres_sortie", "skills")
    for initiative in initiatives:
        identifiant = initiative.get("id", "")
        if not identifiant or identifiant in ids:
            erreurs_initiatives.append(f"identifiant absent ou dupliqué : {identifiant!r}")
        ids.add(identifiant)
        absents = [champ for champ in champs if not initiative.get(champ)]
        if absents:
            erreurs_initiatives.append(f"{identifiant}: champs manquants {', '.join(absents)}")
        if initiative.get("phase") not in PHASES:
            erreurs_initiatives.append(f"{identifiant}: phase inconnue {initiative.get('phase')!r}")
        if initiative.get("etat") not in ETATS:
            erreurs_initiatives.append(f"{identifiant}: état inconnu {initiative.get('etat')!r}")
        inconnus = set(initiative.get("domaines", [])) - domaines_connus
        if inconnus:
            erreurs_initiatives.append(f"{identifiant}: domaines inconnus {', '.join(sorted(inconnus))}")
        skills_absents = set(initiative.get("skills", [])) - skill_slugs
        if skills_absents:
            erreurs_initiatives.append(f"{identifiant}: skills absents {', '.join(sorted(skills_absents))}")
        preuves = initiative.get("preuves", [])
        manquantes = [ref for ref in preuves if not isinstance(ref, str) or not (ROOT / ref).exists()]
        if manquantes:
            erreurs_initiatives.append(f"{identifiant}: preuves/références locales absentes {', '.join(manquantes)}")
        if isinstance(initiative.get("criteres_sortie"), list) and len(initiative["criteres_sortie"]) < 2:
            erreurs_initiatives.append(f"{identifiant}: préciser au moins deux critères de sortie")
    verificateur.verifier(
        "Initiatives R&D reprenables par un autre agent",
        bool(initiatives) and not erreurs_initiatives,
        f"{len(initiatives)} initiatives avec question, état, preuves, prochaine action, critères et skills"
        if not erreurs_initiatives else "; ".join(erreurs_initiatives),
    )
    for initiative in initiatives:
        ligne = f"- **{initiative.get('id', 'sans-id')}** — {initiative.get('etat', 'état inconnu')} / {initiative.get('phase', 'phase inconnue')} : {initiative.get('prochaine_action', 'prochaine action à définir')}"
        verificateur.lignes.append(ligne)


def verifier_surface_publique(verificateur: Verificateur) -> None:
    page = ROOT / "transparence.html"
    aventure = ROOT / "anglais-aventure.html"
    apprentissage = ROOT / "apprendre.html"
    page_text = page.read_text(encoding="utf-8") if page.is_file() else ""
    aventure_text = aventure.read_text(encoding="utf-8") if aventure.is_file() else ""
    apprentissage_text = apprentissage.read_text(encoding="utf-8") if apprentissage.is_file() else ""
    verificateur.verifier(
        "La R&D continue est visible depuis la transparence, l'atlas et l'apprentissage",
        'id="rd-innovation"' in page_text
        and 'href="transparence.html#rd-innovation"' in aventure_text
        and 'href="transparence.html#rd-innovation"' in apprentissage_text
        and "Aucun site ne peut recenser tout le savoir du monde" in page_text
        and "73 fiches" in page_text and "47 prototypes" in page_text
        and "blob/main/docs/rd/portefeuille.toml" in page_text
        and "blob/main/docs/rd/journal.md" in page_text
        and 'href="https://github.com/thejmimiia-code/MRSC/blob/main/docs/rd/protocole-essais-usage.md"' in page_text
        and "issues/new?template=proposition-rd.yml" in page_text,
    )


def verifier_veille(verificateur: Verificateur) -> None:
    veille_path = ROOT / ".github" / "workflows" / "veille-apprentissages.yml"
    verification_path = ROOT / ".github" / "workflows" / "verification.yml"
    publication_path = ROOT / ".github" / "workflows" / "deploy-pages.yml"
    veille = veille_path.read_text(encoding="utf-8") if veille_path.is_file() else ""
    verification = verification_path.read_text(encoding="utf-8") if verification_path.is_file() else ""
    publication = publication_path.read_text(encoding="utf-8") if publication_path.is_file() else ""
    verificateur.verifier(
        "Veille hebdomadaire, contrôle PR et publication référencent le vérificateur R&D",
        'cron: "20 7 * * 1"' in veille
        and "python3 outils/verifier-rd-continue.py --rapport" in veille
        and "issues: write" in veille
        and "python3 outils/verifier-rd-continue.py" in verification
        and "python3 outils/verifier-rd-continue.py" in publication,
        "rappel hebdomadaire, rapport, revue des changements et validation avant déploiement",
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rapport", type=Path, help="Écrit également un rapport Markdown à ce chemin.")
    args = parser.parse_args()
    verificateur = Verificateur()
    skills = verifier_skills(verificateur)
    verifier_portefeuille(verificateur, skills)
    verifier_surface_publique(verificateur)
    verifier_veille(verificateur)
    if verificateur.alertes:
        verificateur.lignes.append("")
        verificateur.lignes.append("Une alerte de date demande une revue humaine; elle n'est pas une preuve d'obsolescence.")
    verificateur.lignes.append("")
    verificateur.lignes.append(
        "Bilan technique : " + ("échecs structurels à corriger." if verificateur.erreurs else "structure valide; aucune approbation scientifique ou éditoriale n'est implicite.")
    )
    if args.rapport:
        args.rapport.parent.mkdir(parents=True, exist_ok=True)
        args.rapport.write_text("\n".join(verificateur.lignes) + "\n", encoding="utf-8")
    return 1 if verificateur.erreurs else 0


if __name__ == "__main__":
    sys.exit(main())
