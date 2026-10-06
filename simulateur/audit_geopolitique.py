"""Expériences synthétiques de lacunes structurelles ; aucune prévision réelle."""

import argparse
import json
from pathlib import Path

from simulateur.geopolitique import (
    Acteur,
    Evenement,
    Parametres,
    Secteur,
    cas_experimental,
    coupler_macro,
    resumer,
    simuler,
)


def crises_repetees(reconstitution: float, recuperation: float) -> dict:
    """Deux chocs identiques, séparés par six mois explicitement sans blocus."""
    evenements = tuple(Evenement(mois=m, blocus=0.8 if m <= 6 or 13 <= m <= 18 else 0)
                       for m in range(1, 37))
    secteur = Secteur('approvisionnement', part_importee=0.8, exposition_route=0.9,
                      stock_mois=1, capacite_stock_mois=2,
                      reconstitution_mensuelle=reconstitution)
    r = simuler((Acteur('Civil'),), (), (secteur,), evenements, 36,
                Parametres(recuperation_annuelle=recuperation), calendrier_complet=True)
    r['macro'] = coupler_macro(r)
    return r


def auditer() -> dict:
    cas = {}
    for reconstitution in (0.0, 0.25, 0.5):
        for recuperation in (0.0, 0.5, 1.0):
            nom = f'stocks_{reconstitution}_reprise_{recuperation}'
            r = crises_repetees(reconstitution, recuperation)
            cas[nom] = {
                'hypotheses': {'reconstitution_mensuelle': reconstitution,
                              'recuperation_annuelle': recuperation},
                'synthese': {
                    **resumer(r),
                    'penurie_episode_1': sum(m['penurie_ponderee'] for m in r['mois'][:6]),
                    'penurie_episode_2': sum(m['penurie_ponderee'] for m in r['mois'][12:18]),
                    'stock_avant_episode_2': r['mois'][12]['flux']['approvisionnement']['stock_initial'],
                    'offre_additionnelle_cumulee': sum(
                        m['flux']['approvisionnement']['reconstitution'] for m in r['mois']),
                },
                'rapport': r,
            }
    factoriel = {}
    for mediation in (False, True):
        for rupture in (False, True):
            nom = f'mediation_{mediation}_rupture_{rupture}'
            r = cas_experimental(mediation=mediation, rupture_dialogue=rupture)
            factoriel[nom] = {'mediation': mediation, 'rupture_dialogue': rupture,
                             'synthese': resumer(r), 'rapport': r}
    return {
        'protocole': 'audit-lacunes-v1', 'version_modele': 'geo-rd-v2',
        'avertissement': '13 trajectoires synthétiques ; ni calibration ni probabilité de guerre.',
        'crises_repetees': cas, 'factoriel_dialogue_mediation': factoriel,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--sortie', type=Path, default=Path('rd-resultats-audit-geopolitique.json'))
    args = parser.parse_args()
    r = auditer()
    args.sortie.write_text(json.dumps(r, ensure_ascii=False, indent=2, allow_nan=False) + '\n', encoding='utf-8')
    synthese = {groupe: {nom: cas['synthese'] for nom, cas in r[groupe].items()}
                for groupe in ('crises_repetees', 'factoriel_dialogue_mediation')}
    print(json.dumps(synthese, ensure_ascii=False, indent=2, allow_nan=False))


if __name__ == '__main__':
    main()
