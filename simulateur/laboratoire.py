"""R&D exploratoire reproductible ; aucune probabilité empirique n'est estimée."""

import argparse
import json
import random
from dataclasses import asdict, dataclass, replace
from pathlib import Path
from statistics import mean

from simulateur.model import DecisionPolitique
from simulateur.moteur import MoteurSimulationSystemique
from simulateur.scenarios import get_scenario_mandature_5_ans, get_scenario_statut_quo

# Réalisation des recettes/économies, pas réduction automatique du coût du bouclier.
LEVIERS = (
    'recettes_fraude_ia_mde', 'conditionnement_aides_entreprises_mde',
    'taxe_superprofits_rachats_mde', 'extension_ttf_mde',
    'fusion_doublons_territoriaux_mde', 'commande_publique_massifiee_mde',
    'extinction_niches_inefficaces_mde', 'fraude_sociale_criminelle_mde',
)


@dataclass(frozen=True)
class Experience:
    realisation: float
    petrole: float
    change: float
    fed: float
    annee_choc: int

    def __post_init__(self) -> None:
        if not (0 <= self.realisation <= 1 and 0 <= self.petrole <= 60
                and -0.2 <= self.change <= 0 and 0 <= self.fed <= 200
                and type(self.annee_choc) is int and 1 <= self.annee_choc <= 5):
            raise ValueError('Expérience hors du domaine exploratoire documenté')


def executer(decisions: list[DecisionPolitique], experience: Experience,
             energie: bool = True, taux: bool = True) -> list[dict]:
    """État neuf à chaque essai, décisions sources non modifiées."""
    moteur = MoteurSimulationSystemique()
    trajectoire = []
    for decision in decisions:
        valeurs = {nom: getattr(decision, nom) * experience.realisation for nom in LEVIERS}
        if decision.annee == experience.annee_choc:
            valeurs.update(
                choc_petrole_brent_usd=decision.choc_petrole_brent_usd + (experience.petrole if energie else 0),
                choc_change_eur_usd=decision.choc_change_eur_usd + (experience.change if energie else 0),
                choc_taux_fed_bps=decision.choc_taux_fed_bps + (experience.fed if taux else 0),
            )
        trajectoire.append(asdict(moteur.appliquer_etape(replace(decision, **valeurs))))
    return trajectoire


def comparer(experience: Experience) -> dict:
    reformes = get_scenario_mandature_5_ans()
    trajectoire = executer(reformes, experience)
    temoin = executer(get_scenario_statut_quo(), experience)
    final, reference = trajectoire[-1], temoin[-1]
    # Plan factoriel : interaction = conjoint - énergie seule - taux seuls + sans choc.
    energie = executer(reformes, experience, taux=False)[-1]['ratio_deficit_pib']
    taux = executer(reformes, experience, energie=False)[-1]['ratio_deficit_pib']
    base = executer(reformes, experience, energie=False, taux=False)[-1]['ratio_deficit_pib']
    return {
        'experience': asdict(experience),
        'deficit_final_pct': final['ratio_deficit_pib'],
        'ecart_deficit_vs_temoin_points': round(final['ratio_deficit_pib'] - reference['ratio_deficit_pib'], 4),
        'ecart_pouvoir_achat_vs_temoin': round(final['pouvoir_achat_index'] - reference['pouvoir_achat_index'], 4),
        'interaction_deficit_points': round(final['ratio_deficit_pib'] - energie - taux + base, 4),
        'trajectoire_reformes': trajectoire,
        'trajectoire_temoin': temoin,
    }


def campagne(nombre: int = 100, graine: int = 20261003) -> dict:
    if type(nombre) is not int or not 1 <= nombre <= 10000:
        raise ValueError('Le nombre doit être un entier entre 1 et 10000')
    rng = random.Random(graine)
    essais = [comparer(Experience(
        rng.uniform(0, 1), rng.uniform(0, 60), rng.uniform(-0.2, 0),
        rng.uniform(0, 200), rng.randint(1, 5),
    )) for _ in range(nombre)]
    pire = max(range(nombre), key=lambda i: essais[i]['deficit_final_pct'])
    interaction = max(range(nombre), key=lambda i: abs(essais[i]['interaction_deficit_points']))
    return {
        'protocole': 'rd-apparie-factoriel-v1', 'graine': graine, 'nombre': nombre,
        'avertissement': 'Exploration de ce modèle, ni prévision, ni probabilité réelle, ni preuve de nouveauté mondiale.',
        'synthese': {
            'part_essais_deficit_final_sous_3_pct': mean(e['deficit_final_pct'] < 3 for e in essais),
            'ecart_deficit_moyen_points': mean(e['ecart_deficit_vs_temoin_points'] for e in essais),
            'pire_deficit_essai_index': pire,
            'plus_forte_interaction_essai_index': interaction,
        },
        'essais': essais,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--nombre', type=int, default=100)
    parser.add_argument('--graine', type=int, default=20261003)
    parser.add_argument('--sortie', type=Path, default=Path('rd-resultats.json'))
    args = parser.parse_args()
    if not 1 <= args.nombre <= 10000:
        parser.error('--nombre doit être compris entre 1 et 10000')
    rapport = campagne(args.nombre, args.graine)
    args.sortie.write_text(json.dumps(rapport, ensure_ascii=False, indent=2, allow_nan=False) + '\n', encoding='utf-8')
    print(json.dumps(rapport['synthese'], ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
