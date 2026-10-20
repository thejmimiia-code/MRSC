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
import html as html_module
import importlib.util
import re
import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# Statuts éditoriaux : définitions partagées, jamais recopiées en chaîne locale.
sys.path.insert(0, str(ROOT / "outils"))
from statuts_editoriaux import PROTOTYPE, RELU, est_prototype, est_relue, porte_un_statut  # noqa: E402
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


def verifier_carte_lacunes(verificateur: Verificateur) -> None:
    """La carte des lacunes doit rester la sortie du référentiel, jamais une copie à la main."""
    generateur = ROOT / "outils" / "construire-carte-lacunes.py"
    carte = ROOT / "docs" / "rd" / "carte-lacunes.md"
    if not generateur.is_file() or not carte.is_file():
        verificateur.verifier("Carte des lacunes présente et régénérable", False, "générateur ou sortie absent")
        return
    try:
        specification = importlib.util.spec_from_file_location("carte_lacunes", generateur)
        module = importlib.util.module_from_spec(specification)
        specification.loader.exec_module(module)
        fiches, domaines, revue = module.charger()
        attendu = module.construire(fiches, domaines, revue)
    except Exception as erreur:  # noqa: BLE001 - un générateur cassé doit être signalé, pas masqué
        verificateur.verifier("Carte des lacunes présente et régénérable", False, str(erreur))
        return
    actuel = carte.read_text(encoding="utf-8")
    verificateur.verifier(
        "Carte des lacunes synchronisée avec le référentiel",
        actuel == attendu,
        f"référence du {revue}" if actuel == attendu else "régénérer avec python3 outils/construire-carte-lacunes.py",
    )


def _totaux_catalogue() -> tuple[int, int, int]:
    """Fiches, fiches initiales et prototypes, relus depuis le catalogue (jamais recopiés)."""
    try:
        catalogue = tomllib.loads((ROOT / "docs" / "apprentissage" / "catalogue.toml").read_text(encoding="utf-8"))
    except (OSError, UnicodeError, tomllib.TOMLDecodeError):
        return 0, 0, 0
    fiches = catalogue.get("fiche", [])
    prototypes = sum(1 for fiche in fiches if est_prototype(fiche))
    return len(fiches), len(fiches) - prototypes, prototypes



def verifier_paquets_relecture(verificateur: Verificateur) -> None:
    """Les paquets de relecture doivent rester la sortie du catalogue, jamais une copie à la main."""
    generateur = ROOT / "outils" / "construire-paquets-relecture.py"
    sortie = ROOT / "docs" / "apprentissage" / "paquets-relecture.md"
    if not generateur.is_file() or not sortie.is_file():
        verificateur.verifier("Paquets de relecture présents et régénérables", False, "générateur ou sortie absent")
        return
    try:
        specification = importlib.util.spec_from_file_location("paquets_relecture", generateur)
        module = importlib.util.module_from_spec(specification)
        specification.loader.exec_module(module)
        elements, titres = module.enrichir(module.charger_module_file_relecture())
        attendu = module.construire(
            elements, titres, dernieres=module.dernieres_relectures(), automatiques=module.etats_automatiques()
        )
    except Exception as erreur:  # noqa: BLE001 - un générateur cassé doit être signalé, pas masqué
        verificateur.verifier("Paquets de relecture présents et régénérables", False, str(erreur))
        return
    actuel = sortie.read_text(encoding="utf-8")
    prioritaires = sum(1 for element in elements if element["rang"] <= 2)
    verificateur.verifier(
        "Paquets de relecture synchronisés avec le catalogue",
        actuel == attendu,
        f"{len(elements)} prototypes, {prioritaires} paquets détaillés"
        if actuel == attendu
        else "régénérer avec python3 outils/construire-paquets-relecture.py",
    )


def verifier_audit_automatique(verificateur: Verificateur) -> None:
    """L'audit mécanique doit rester la sortie du catalogue, pas une copie à la main."""
    generateur = ROOT / "outils" / "auditer-prototypes.py"
    sortie = ROOT / "docs" / "apprentissage" / "audit-automatique.md"
    if not generateur.is_file() or not sortie.is_file():
        verificateur.verifier("Audit automatique présent et régénérable", False, "générateur ou sortie absent")
        return
    try:
        specification = importlib.util.spec_from_file_location("audit_prototypes", generateur)
        module = importlib.util.module_from_spec(specification)
        specification.loader.exec_module(module)
        fiches, titres, references = module.charger()
        aujourdhui = dt.date.today()
        audits = module.auditer(fiches, references, aujourdhui)
        attendu = module.construire(audits, titres, aujourdhui)
        chiffres = module.resume(audits)
    except Exception as erreur:  # noqa: BLE001 - un générateur cassé doit être signalé, pas masqué
        verificateur.verifier("Audit automatique présent et régénérable", False, str(erreur))
        return
    actuel = sortie.read_text(encoding="utf-8")
    verificateur.verifier(
        "Audit automatique synchronisé avec le catalogue",
        actuel == attendu,
        f"{chiffres['fiches']} prototypes, {chiffres['controles']} contrôles par fiche, {chiffres['echecs']} échec(s)"
        if actuel == attendu
        else "régénérer avec python3 outils/auditer-prototypes.py",
    )


def verifier_registre_relecture(verificateur: Verificateur) -> None:
    """Le registre humain doit rester cohérent avec le catalogue, sans être pré-rempli."""
    script = ROOT / "outils" / "registre-relecture.py"
    if not script.is_file():
        verificateur.verifier("Registre de relecture présent et vérifiable", False, "outils/registre-relecture.py absent")
        return
    try:
        specification = importlib.util.spec_from_file_location("registre_relecture", script)
        module = importlib.util.module_from_spec(specification)
        specification.loader.exec_module(module)
    except Exception as erreur:  # noqa: BLE001 - un contrôle cassé doit être signalé, pas masqué
        verificateur.verifier("Registre de relecture présent et vérifiable", False, str(erreur))
        return
    erreurs: list[str] = []
    entrees = module.charger_registre(erreurs)
    fiches = module.charger_catalogue()
    aujourdhui = dt.date.today()
    for index, entree in enumerate(entrees, start=1):
        module.controler_entree(index, entree, fiches, aujourdhui, erreurs)
    dernieres = module.controler_coherence(entrees, fiches, erreurs)
    verificateur.verifier(
        "Registre de relecture cohérent avec le catalogue",
        not erreurs,
        f"{len(dernieres)} relecture(s) consignée(s), {sum(1 for fiche in fiches.values() if est_prototype(fiche))} prototype(s) en attente"
        if not erreurs
        else " ; ".join(erreurs[:3]),
    )


def etat_registre_relecture() -> tuple[int, str]:
    """Nombre de relectures consignées et phrase que la page publique doit employer.

    La phrase dépend du registre : ajouter une relecture sans mettre la page à
    jour fait échouer la porte, plutôt que de laisser une affirmation périmée.
    """
    chemin = ROOT / "docs" / "apprentissage" / "relectures.toml"
    try:
        with chemin.open("rb") as fichier:
            entrees = tomllib.load(fichier).get("relecture", [])
    except (OSError, tomllib.TOMLDecodeError):
        entrees = []
    nombre = len(entrees)
    if nombre == 0:
        return 0, "Aucune relecture humaine n’est consignée à ce jour dans le"
    return nombre, f"{nombre} relecture(s) humaine(s) consignée(s) dans le"


def etat_audit_automatique() -> str:
    """Phrase publique dérivée de l'audit mécanique, jamais recopiée à la main."""
    try:
        specification = importlib.util.spec_from_file_location("audit_prototypes", ROOT / "outils" / "auditer-prototypes.py")
        module = importlib.util.module_from_spec(specification)
        specification.loader.exec_module(module)
        fiches, _, references = module.charger()
        audits = module.auditer(fiches, references, dt.date.today())
        chiffres = module.resume(audits)
    except Exception:  # noqa: BLE001 - un audit cassé ne doit pas masquer son état
        return "audit automatique indisponible"
    if chiffres["echecs"]:
        return (
            f"les {chiffres['fiches']} prototypes sont soumis aux {chiffres['controles']} contrôles automatiques du dépôt"
            f" ({chiffres['echecs']} défaut(s) mécanique(s) à corriger)"
        )
    return (
        f"les {chiffres['fiches']} prototypes sont soumis aux {chiffres['controles']} contrôles automatiques du dépôt"
    )


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
        and f"{_totaux_catalogue()[0]} fiches" in page_text
        and f"{_totaux_catalogue()[2]} prototypes" in page_text
        and "blob/main/docs/rd/portefeuille.toml" in page_text
        and "blob/main/docs/rd/journal.md" in page_text
        and 'href="https://github.com/thejmimiia-code/MRSC/blob/main/docs/rd/protocole-essais-usage.md"' in page_text
        and "issues/new?template=proposition-rd.yml" in page_text,
    )
    page_lisible = html_module.unescape(page_text)
    phrase_audit = etat_audit_automatique()
    verificateur.verifier(
        "La transparence dit l'état réel des contrôles automatiques",
        phrase_audit in page_lisible,
        phrase_audit,
    )
    _, phrase_registre = etat_registre_relecture()
    verificateur.verifier(
        "La transparence dit l'état réel du registre de relecture",
        phrase_registre in page_lisible
        and "blob/main/docs/apprentissage/relectures.toml" in page_text
        and "refuse un statut qui ne correspondrait pas au registre" in page_lisible,
        phrase_registre,
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
    verifier_carte_lacunes(verificateur)
    verifier_paquets_relecture(verificateur)
    verifier_audit_automatique(verificateur)
    verifier_registre_relecture(verificateur)
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
