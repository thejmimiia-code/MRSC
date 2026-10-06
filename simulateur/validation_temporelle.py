"""Registre versionné et références mensuelles évaluées sans accès au futur.

Aucune conversion de l'indice géopolitique en probabilité. Voir le protocole R&D v3.
"""

import argparse
import hashlib
import json
import math
import re
from dataclasses import asdict, dataclass
from datetime import date, timedelta
from pathlib import Path
from statistics import mean

from simulateur.fichiers import verifier_chemins_distincts

CIBLE = 'presence_affrontement_organise_v1'
CIBLE_UCDP = 'presence_evenement_letal_ucdp_v1'
CIBLES = (CIBLE, CIBLE_UCDP)
MODELES = ('frequence_lissee', 'dernier_etat_lisse')


def date_iso(texte: str) -> date:
    if not isinstance(texte, str) or not re.fullmatch(r'\d{4}-\d{2}-\d{2}', texte):
        raise ValueError('Date attendue au format AAAA-MM-JJ')
    return date.fromisoformat(texte)


def mois_iso(texte: str) -> date:
    if not isinstance(texte, str) or not re.fullmatch(r'\d{4}-\d{2}', texte):
        raise ValueError('Mois attendu au format AAAA-MM')
    return date_iso(texte + '-01')


def mois_suivant(mois: date) -> date:
    return date(mois.year + (mois.month == 12), mois.month % 12 + 1, 1)


@dataclass(frozen=True)
class Observation:
    identifiant: str
    unite: str
    mois: str
    revision: int
    cible: str
    valeur: int | None
    couverture: str
    nature: str
    source: str
    version_source: str
    licence: str
    preuve_disponibilite: str
    publication: str
    disponibilite: str
    ingestion: str

    def __post_init__(self) -> None:
        for champ in ('identifiant', 'unite', 'source', 'version_source', 'licence',
                      'preuve_disponibilite'):
            v = getattr(self, champ)
            if not isinstance(v, str) or not v.strip():
                raise ValueError(f'{champ} doit être un texte non vide')
        if self.cible not in CIBLES:
            raise ValueError('Cible non prise en charge')
        if type(self.revision) is not int or self.revision < 1:
            raise ValueError('Révision entière positive requise')
        if self.nature not in ('synthetique', 'observee'):
            raise ValueError('Nature synthetique ou observee requise')
        if self.couverture not in ('complete', 'incomplete'):
            raise ValueError('Couverture complete ou incomplete requise')
        if self.couverture == 'complete':
            if type(self.valeur) is not int or self.valeur not in (0, 1):
                raise ValueError('Une couverture complète exige une étiquette binaire 0/1')
        elif self.valeur is not None:
            raise ValueError('Une couverture incomplète doit rester inconnue (null)')
        fin = mois_suivant(mois_iso(self.mois))
        publication, disponibilite, ingestion = map(
            date_iso, (self.publication, self.disponibilite, self.ingestion))
        if not fin <= publication <= disponibilite <= ingestion:
            raise ValueError('Clôture mensuelle <= publication <= disponibilité <= ingestion requise')


class Registre:
    def __init__(self, observations: tuple[Observation, ...]):
        if not observations:
            raise ValueError('Registre vide')
        if len({o.cible for o in observations}) != 1:
            raise ValueError('Ne pas mélanger des cibles différentes')
        if len({o.nature for o in observations}) != 1:
            raise ValueError('Ne pas mélanger observations réelles et synthétiques')
        revisions = set()
        identites: dict[str, tuple[str, str]] = {}
        cellules: dict[tuple[str, str], str] = {}
        groupes: dict[str, list[Observation]] = {}
        for o in observations:
            cle = (o.identifiant, o.revision)
            cellule = (o.unite, o.mois)
            if cle in revisions:
                raise ValueError('Révision dupliquée')
            revisions.add(cle)
            if identites.setdefault(o.identifiant, cellule) != cellule:
                raise ValueError('Une identité ne peut changer de territoire/mois')
            if cellules.setdefault(cellule, o.identifiant) != o.identifiant:
                raise ValueError('Plusieurs identités pour la même cellule ; arbitrage requis')
            groupes.setdefault(o.identifiant, []).append(o)
        for groupe in groupes.values():
            ordre = sorted(groupe, key=lambda o: o.revision)
            for avant, apres in zip(ordre, ordre[1:], strict=False):
                if (apres.publication < avant.publication
                        or apres.disponibilite < avant.disponibilite):
                    raise ValueError('Une révision ne peut être antidatée')
        self.observations = tuple(sorted(observations, key=lambda o: (o.unite, o.mois, o.revision)))

    def instantane(self, au: str, mode: str = 'locale') -> dict[tuple[str, str], Observation]:
        """Dernière révision connue ; un retrait null remplace bien l'ancienne valeur."""
        limite = date_iso(au)
        if mode not in ('locale', 'publique'):
            raise ValueError('Mode de connaissance locale ou publique requis')
        resultat = {}
        for o in self.observations:
            connue = o.ingestion if mode == 'locale' else o.disponibilite
            if date_iso(connue) <= limite:
                resultat[(o.unite, o.mois)] = o
        return resultat

    def empreinte(self) -> str:
        contenu = json.dumps([asdict(o) for o in self.observations], sort_keys=True,
                             ensure_ascii=False, separators=(',', ':'))
        return hashlib.sha256(contenu.encode()).hexdigest()


def _objet_unique(paires: list[tuple]) -> dict:
    resultat = {}
    for cle, valeur in paires:
        if cle in resultat:
            raise ValueError(f'Clé JSON dupliquée : {cle}')
        resultat[cle] = valeur
    return resultat


def importer_jsonl(chemin: Path) -> Registre:
    observations = []
    for numero, ligne in enumerate(chemin.read_text(encoding='utf-8').splitlines(), start=1):
        if not ligne.strip():
            continue
        try:
            donnees = json.loads(ligne, object_pairs_hook=_objet_unique)
            if not isinstance(donnees, dict):
                raise ValueError('Objet JSON requis')
            observations.append(Observation(**donnees))
        except (TypeError, ValueError) as erreur:
            raise ValueError(f'{chemin.name}, ligne {numero} : {erreur}') from erreur
    return Registre(tuple(observations))


def prevoir(registre: Registre, origine: str, unites: tuple[str, ...],
            minimum: int = 6, mode: str = 'locale') -> dict:
    """Au premier jour, prévoir le mois qui débute. Aucun hyperparamètre ajusté."""
    jour = date_iso(origine)
    if jour.day != 1:
        raise ValueError('Une origine doit être le premier jour du mois')
    if type(minimum) is not int or minimum < 1:
        raise ValueError('Minimum historique entier positif requis')
    if (not unites or len(set(unites)) != len(unites)
            or any(not isinstance(u, str) or not u.strip() for u in unites)):
        raise ValueError('Unités explicites, non vides et uniques requises')
    # Dates sans heure : une publication du jour d'émission n'est pas présumée
    # connue à l'ouverture. Clôture de la veille comme borne conservatrice.
    connaissance_au = (jour - timedelta(days=1)).isoformat()
    instantane = registre.instantane(connaissance_au, mode)
    predictions, abstentions = [], []
    for unite in sorted(unites):
        passe = sorted((o for o in instantane.values()
                        if o.unite == unite and mois_iso(o.mois) < jour
                        and o.couverture == 'complete'), key=lambda o: o.mois)
        if len(passe) < minimum:
            abstentions.append({'unite': unite, 'origine': origine, 'mois_cible': origine[:7],
                                'motif': 'historique_insuffisant', 'n': len(passe)})
            continue
        # Lissage de Laplace : jamais d'assurance 0/1 pour ces références simples.
        probabilites = {'frequence_lissee': (sum(o.valeur for o in passe) + 1) / (len(passe) + 2),
                       'dernier_etat_lisse': (passe[-1].valeur + 1) / 3}
        for modele, probabilite in probabilites.items():
            predictions.append({
                'modele': modele, 'unite': unite, 'origine': origine,
                'mois_cible': origine[:7], 'probabilite': probabilite,
                'connaissance_au': connaissance_au,
                'n_historique': len(passe), 'dernier_mois_connu': passe[-1].mois,
                'revisions_utilisees': [[o.identifiant, o.revision] for o in passe],
            })
    return {'predictions': predictions, 'abstentions': abstentions}


def metriques(paires: list[tuple[float, int]]) -> dict:
    """Scores sur le même échantillon : bas = meilleur ; alerte si p >= 0,5."""
    for p, y in paires:
        if (isinstance(p, bool) or not isinstance(p, (int, float))
                or not math.isfinite(p) or not 0 <= p <= 1
                or type(y) is not int or y not in (0, 1)):
            raise ValueError('Probabilité finie [0,1] et étiquette entière 0/1 requises')
    calibration = []
    for i in range(5):
        groupe = [(p, y) for p, y in paires if min(int(p * 5), 4) == i]
        calibration.append({'borne_basse': i / 5, 'borne_haute': (i + 1) / 5,
                            'n': len(groupe),
                            'probabilite_moyenne': mean(p for p, _ in groupe) if groupe else None,
                            'frequence_observee': mean(y for _, y in groupe) if groupe else None})
    epsilon = 1e-15  # convention déclarée pour les prévisions extrêmes 0/1
    return {
        'n': len(paires),
        'brier': mean((p - y) ** 2 for p, y in paires) if paires else None,
        'log_loss': mean(-math.log(max(epsilon, min(1 - epsilon, p if y else 1 - p)))
                         for p, y in paires) if paires else None,
        'vrais_positifs': sum(p >= 0.5 and y == 1 for p, y in paires),
        'fausses_alertes': sum(p >= 0.5 and y == 0 for p, y in paires),
        'evenements_manques': sum(p < 0.5 and y == 1 for p, y in paires),
        'vrais_negatifs': sum(p < 0.5 and y == 0 for p, y in paires),
        'calibration_descriptive': calibration,
    }


def evaluer(registre: Registre, debut: str, fin: str, au: str,
            unites: tuple[str, ...], minimum: int = 6, mode: str = 'locale') -> dict:
    premier, dernier, evaluation = date_iso(debut), date_iso(fin), date_iso(au)
    if premier.day != 1 or dernier.day != 1 or not premier <= dernier:
        raise ValueError('Période de prévision mensuelle invalide')
    if evaluation < mois_suivant(dernier):
        raise ValueError('Évaluer après la clôture du dernier mois cible')
    verite = registre.instantane(au, mode)
    predictions, abstentions, exclusions = [], [], []
    scores: dict[str, list[tuple[float, int]]] = {nom: [] for nom in MODELES}
    origine = premier
    while origine <= dernier:
        lot = prevoir(registre, origine.isoformat(), unites, minimum, mode)
        abstentions.extend(lot['abstentions'])
        for prediction in lot['predictions']:
            observation = verite.get((prediction['unite'], prediction['mois_cible']))
            if observation is None or observation.couverture != 'complete':
                exclusions.append({'modele': prediction['modele'], 'unite': prediction['unite'],
                                   'mois_cible': prediction['mois_cible'],
                                   'motif': 'etiquette_indisponible_ou_incomplete'})
                valeur = revision = None
            else:
                valeur, revision = observation.valeur, observation.revision
                scores[prediction['modele']].append((prediction['probabilite'], valeur))
            predictions.append({**prediction, 'valeur_evaluation': valeur,
                                'revision_evaluation': revision})
        origine = mois_suivant(origine)
    return {
        'protocole': 'validation-mensuelle-v1', 'nature': registre.observations[0].nature,
        'cible': registre.observations[0].cible, 'mode_connaissance': mode, 'empreinte_registre_sha256': registre.empreinte(),
        'empreinte_code_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'configuration': {'debut': debut, 'fin': fin, 'evaluation_au': au,
                          'unites': list(unites), 'minimum_historique': minimum,
                          'seuil_alerte': 0.5, 'epsilon_log_loss': 1e-15},
        'avertissement': 'Références statistiques seulement ; aucun score de guerre mondiale ou nucléaire.',
        'scores': {nom: metriques(paires) for nom, paires in scores.items()},
        'predictions': predictions, 'abstentions': abstentions, 'exclusions': exclusions,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--observations', type=Path, required=True)
    parser.add_argument('--debut', required=True, help='Premier jour du premier mois prédit')
    parser.add_argument('--fin', required=True, help='Premier jour du dernier mois prédit')
    parser.add_argument('--evaluation-au', required=True)
    parser.add_argument('--unites', nargs='+', required=True, help='Univers choisi avant le test')
    parser.add_argument('--minimum', type=int, default=6)
    parser.add_argument('--mode', choices=('locale', 'publique'), default='locale')
    parser.add_argument('--sortie', type=Path, default=Path('rd-resultats-validation.json'))
    args = parser.parse_args()
    try:
        verifier_chemins_distincts(args.observations, args.sortie)
        registre = importer_jsonl(args.observations)
        resultat = evaluer(registre, args.debut, args.fin, args.evaluation_au,
                           tuple(args.unites), args.minimum, args.mode)
        args.sortie.write_text(json.dumps(resultat, ensure_ascii=False, indent=2, allow_nan=False) + '\n', encoding='utf-8')
    except (ValueError, OSError) as erreur:
        parser.error(str(erreur))
    print(json.dumps({'nature': resultat['nature'], 'scores': resultat['scores'],
                      'abstentions': len(resultat['abstentions']),
                      'exclusions': len(resultat['exclusions'])}, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
