"""
simulateur/reglements_lois.py — Registre programmatique intégral des textes de lois et règlements.
Permet d'interroger les articles de lois et leurs contraintes mathématiques dans le simulateur.
"""

from dataclasses import dataclass


@dataclass
class ArticleDeLoi:
    identifiant: str
    code_ou_traite: str
    article: str
    titre: str
    texte_integral: str
    strate_impactee: str  # "Local", "National", "Europe", "Mondial", "Transversal"
    effet_simulation: str


REGISTRE_LEGAL: dict[str, ArticleDeLoi] = {
    # -------------------------------------------------------------------------
    # BLOC CONSTITUTIONNEL
    # -------------------------------------------------------------------------
    "CONST_ART_2": ArticleDeLoi(
        identifiant="CONST_ART_2",
        code_ou_traite="Constitution du 4 octobre 1958",
        article="Article 2, alinéa 5",
        titre="Principe républicain fondamental",
        texte_integral="Son principe est : gouvernement du peuple, par le peuple et pour le peuple.",
        strate_impactee="Transversal",
        effet_simulation="Légitime la souveraineté citoyenne directe, l'usage du RIC et la transparence des comptes.",
    ),
    "CONST_ART_3": ArticleDeLoi(
        identifiant="CONST_ART_3",
        code_ou_traite="Constitution du 4 octobre 1958",
        article="Article 3",
        titre="Souveraineté nationale et voies d'exercice",
        texte_integral="La souveraineté nationale appartient au peuple qui l'exerce par ses représentants et par la voie du référendum. Aucune section du peuple ni aucun individu ne peut s'en attribuer l'exercice.",
        strate_impactee="National",
        effet_simulation="Interdit la confiscation du pouvoir législatif par des oligarchies ou lobbies financiers.",
    ),
    "CONST_ART_11": ArticleDeLoi(
        identifiant="CONST_ART_11",
        code_ou_traite="Constitution du 4 octobre 1958",
        article="Article 11",
        titre="Référendum législatif direct",
        texte_integral="Le Président de la République peut soumettre au référendum tout projet de loi portant sur l'organisation des pouvoirs publics, sur des réformes relatives à la politique économique ou sociale de la nation et aux services publics qui y concourent.",
        strate_impactee="National",
        effet_simulation="Permet l'adoption directe par le peuple des réformes de fiscalité de l'énergie et de probité.",
    ),
    "CONST_ART_49_2": ArticleDeLoi(
        identifiant="CONST_ART_49_2",
        code_ou_traite="Constitution du 4 octobre 1958",
        article="Article 49, alinéa 2",
        titre="Motion de censure de l'Assemblée nationale",
        texte_integral="L'Assemblée nationale met en cause la responsabilité du Gouvernement par le vote d'une motion de censure. Une telle motion n'est recevable que si elle est signée par un dixième au moins des membres de l'Assemblée nationale. Seuls sont recensés les votes favorables à la motion de censure qui ne peut être adoptée qu'à la majorité des membres composant l'Assemblée.",
        strate_impactee="National",
        effet_simulation="Chute du gouvernement si 289 députés votent la censure, modélisée par le basculement des indépendants sous forte tension locale.",
    ),
    "CONST_ART_49_3": ArticleDeLoi(
        identifiant="CONST_ART_49_3",
        code_ou_traite="Constitution du 4 octobre 1958",
        article="Article 49, alinéa 3",
        titre="Engagement de responsabilité gouvernementale sans vote",
        texte_integral="Le Premier ministre peut engager la responsabilité du Gouvernement devant l'Assemblée nationale sur le vote d'un projet de loi de finances ou de financement de la sécurité sociale. Le projet est considéré comme adopté sauf si une motion de censure est votée.",
        strate_impactee="National",
        effet_simulation="En l'absence de majorité absolue, son déclenchement augmente le risque de censure si la tension sociale locale > 65/100.",
    ),
    "DDHC_ART_6": ArticleDeLoi(
        identifiant="DDHC_ART_6",
        code_ou_traite="Déclaration des Droits de l'Homme et du Citoyen de 1789",
        article="Article 6",
        titre="Égalité d'accès aux dignités et emplois publics selon les vertus",
        texte_integral="Tous les Citoyens étant égaux à ses yeux sont également admissibles à toutes dignités, places et emplois publics, selon leur capacité, et sans autre distinction que celle de leurs vertus et de leurs talents.",
        strate_impactee="National",
        effet_simulation="Fonde constitutionnellement l'exigence d'un casier judiciaire B2 vierge pour concourir à un mandat.",
    ),
    "CC_2017_752_DC": ArticleDeLoi(
        identifiant="CC_2017_752_DC",
        code_ou_traite="Jurisprudence du Conseil constitutionnel",
        article="Décision n° 2017-752 DC du 8 septembre 2017",
        titre="Conformité des peines d'inéligibilité obligatoire avec dispense motivée du juge",
        texte_integral="Le législateur peut instaurer une peine d'inéligibilité obligatoire liée à des infractions à la probité, dès lors que le juge conserve le pouvoir d'exonération par décision motivée.",
        strate_impactee="National",
        effet_simulation="Sécurise à 100 % le filtre automatisé du casier B2 contre tout risque d'annulation constitutionnelle.",
    ),

    # -------------------------------------------------------------------------
    # PROBITÉ & CODE PÉNAL
    # -------------------------------------------------------------------------
    "CP_432_10": ArticleDeLoi(
        identifiant="CP_432_10",
        code_ou_traite="Code pénal",
        article="Article 432-10",
        titre="De la concussion publique",
        texte_integral="Le fait, par une personne dépositaire de l'autorité publique, d'ordonner de percevoir des droits indus est puni de cinq ans d'emprisonnement et 500 000 € d'amende.",
        strate_impactee="National",
        effet_simulation="Inéligibilité automatique du candidat en cas de condamnation inscrite au B2.",
    ),
    "CP_432_11": ArticleDeLoi(
        identifiant="CP_432_11",
        code_ou_traite="Code pénal",
        article="Article 432-11",
        titre="De la corruption passive et du trafic d'influence",
        texte_integral="Le fait, par une personne investie d'un mandat électif public, de solliciter ou d'agréer des avantages pour accomplir ou s'abstenir d'accomplir un acte de sa fonction est puni de dix ans d'emprisonnement et 1 000 000 € d'amende.",
        strate_impactee="National",
        effet_simulation="Inéligibilité automatique et inconditionnelle.",
    ),
    "CP_432_12": ArticleDeLoi(
        identifiant="CP_432_12",
        code_ou_traite="Code pénal",
        article="Article 432-12",
        titre="De la prise illégale d'intérêts",
        texte_integral="Le fait de prendre un intérêt quelconque dans une entreprise sous sa surveillance ou liquidation est puni de cinq ans d'emprisonnement et 500 000 € d'amende.",
        strate_impactee="National",
        effet_simulation="Exclusion des fonctions exécutives et électives.",
    ),
    "CP_131_26_2": ArticleDeLoi(
        identifiant="CP_131_26_2",
        code_ou_traite="Code pénal",
        article="Article 131-26-2",
        titre="Peine complémentaire obligatoire d'inéligibilité",
        texte_integral="Le prononcé de la peine complémentaire d'inéligibilité est obligatoire à l'encontre de toute personne coupable d'un délit de concussion, corruption, prise illégale d'intérêts, favoritisme ou détournement de fonds publics.",
        strate_impactee="National",
        effet_simulation="Filtre automatisé du casier B2 écartant impérativement les candidats condamnés pour manquement à la probité.",
    ),
    "CGI_1741": ArticleDeLoi(
        identifiant="CGI_1741",
        code_ou_traite="Code général des impôts",
        article="Article 1741",
        titre="Délit général de fraude fiscale aggravée",
        texte_integral="Quiconque s'est frauduleusement soustrait au paiement total ou partiel de l'impôt est puni de cinq ans d'emprisonnement et 500 000 € d'amende (sept ans et 3 000 000 € en bande organisée).",
        strate_impactee="National",
        effet_simulation="Gisement récupéré par les algorithmes GNN (+10 Md€/an) et inéligibilité des fraudeurs fiscaux.",
    ),

    # -------------------------------------------------------------------------
    # FINANCES LOCALES & RÈGLE D'OR (CGCT)
    # -------------------------------------------------------------------------
    "CGCT_L1612_4": ArticleDeLoi(
        identifiant="CGCT_L1612_4",
        code_ou_traite="Code général des collectivités territoriales",
        article="Article L. 1612-4",
        titre="Règle d'or de l'équilibre réel budgétaire des collectivités",
        texte_integral="Le budget de la collectivité territoriale est en équilibre réel lorsque la section de fonctionnement et la section d'investissement sont respectivement votées en équilibre, l'emprunt étant interdit pour financer le fonctionnement.",
        strate_impactee="Local",
        effet_simulation="Toute baisse de DGF de l'État force une hausse de taxe foncière de 94 % de la perte subie.",
    ),
    "CGCT_L2334_1": ArticleDeLoi(
        identifiant="CGCT_L2334_1",
        code_ou_traite="Code général des collectivités territoriales",
        article="Article L. 2334-1 et suivants",
        titre="Dotation Globale de Fonctionnement (DGF)",
        texte_integral="Fixe les critères de répartition des 27,2 milliards d'euros de DGF versée par l'État aux communes et EPCI.",
        strate_impactee="Local",
        effet_simulation="Sanctuarisée dans le plan de mandature pour préserver les services de proximité ruraux.",
    ),

    # -------------------------------------------------------------------------
    # FISCALITÉ, AIDES & MARCHÉS FINANCIERS
    # -------------------------------------------------------------------------
    "LPF_L81": ArticleDeLoi(
        identifiant="LPF_L81",
        code_ou_traite="Livre des procédures fiscales",
        article="Article L. 81",
        titre="Droit de communication de l'administration fiscale",
        texte_integral="Permet aux agents du fisc d'obtenir les relevés de comptes et données auprès des banques et organismes tiers.",
        strate_impactee="National",
        effet_simulation="Étendu aux passerelles de paiement (PSP) pour les transactions transfrontalières > 50 000 €.",
    ),
    "CGI_235_TER_ZD": ArticleDeLoi(
        identifiant="CGI_235_TER_ZD",
        code_ou_traite="Code général des impôts",
        article="Article 235 ter ZD",
        titre="Taxe sur les Transactions Financières (TTF)",
        texte_integral="Taxe de 0,3 % sur les acquisitions de titres de sociétés françaises cotées de plus d'1 Md€ de capitalisation.",
        strate_impactee="Mondial",
        effet_simulation="Étendue au trading haute fréquence (>80% d'annulations) et prélevée au dépositaire Euroclear (+5 Md€/an).",
    ),
    "ENV_L229_25": ArticleDeLoi(
        identifiant="ENV_L229_25",
        code_ou_traite="Code de l'environnement",
        article="Article L. 229-25",
        titre="Bilan d'émissions de gaz à effet de serre (BEGES)",
        texte_integral="Obligation légale pour les entreprises de plus de 500 salariés de publier leur bilan carbone et plan de transition.",
        strate_impactee="National",
        effet_simulation="Condition d'éligibilité automatisée par API pour maintenir le versement des aides publiques.",
    ),

    # -------------------------------------------------------------------------
    # COMMANDE PUBLIQUE & CONSOMMATION
    # -------------------------------------------------------------------------
    "CCP_L2113_10": ArticleDeLoi(
        identifiant="CCP_L2113_10",
        code_ou_traite="Code de la commande publique",
        article="Article L. 2113-10",
        titre="Obligation légale d'allotissement des marchés publics",
        texte_integral="Les marchés sont obligatoirement passés en lots séparés pour susciter la plus large concurrence.",
        strate_impactee="Local",
        effet_simulation="Empêche les monopoles multinationaux et réserve au moins 30 % des lots aux PME locales.",
    ),
    "CCP_L2112_2": ArticleDeLoi(
        identifiant="CCP_L2112_2",
        code_ou_traite="Code de la commande publique",
        article="Article L. 2112-2",
        titre="Critères environnementaux et circuits courts",
        texte_integral="Permet d'imposer des conditions d'exécution fondées sur la réduction de l'empreinte carbone de transport.",
        strate_impactee="Local",
        effet_simulation="Protège légalement les artisans et agriculteurs de proximité dans les cantines et chantiers publics.",
    ),
    "CONSO_L470_2": ArticleDeLoi(
        identifiant="CONSO_L470_2",
        code_ou_traite="Code de la consommation",
        article="Article L. 470-2",
        titre="Sanction administrative pour marge indue et non-répercussion fiscale",
        texte_integral="Amende administrative prononcée par la DGCCRF égale à 150 % des sommes indûment perçues.",
        strate_impactee="National",
        effet_simulation="Verrouille la baisse de TVA énergie pour qu'elle profite à 100 % aux ménages sans captation par les fournisseurs.",
    ),

    # -------------------------------------------------------------------------
    # DROIT EUROPÉEN & SOUVERAINETÉ NUMÉRIQUE
    # -------------------------------------------------------------------------
    "DIR_TVA_2022_542": ArticleDeLoi(
        identifiant="DIR_TVA_2022_542",
        code_ou_traite="Union Européenne — Directive (UE) 2022/542 du Conseil",
        article="Annexe III, Point 22",
        titre="Taux réduit de TVA jusqu'à 5,5 % sur l'électricité et le gaz naturel",
        texte_integral="Autorise expressément chaque État membre de l'UE à appliquer un taux réduit de TVA jusqu'à 5,5 % sur la livraison d'électricité, de gaz naturel et de chaleur urbaine.",
        strate_impactee="Européen",
        effet_simulation="Garantit la conformité européenne totale de la baisse de TVA de 20 % à 5,5 % (-9 Md€/an).",
    ),
    "TFUE_ART_126": ArticleDeLoi(
        identifiant="TFUE_ART_126",
        code_ou_traite="Traité sur le Fonctionnement de l'Union Européenne",
        article="Article 126 & Protocole n° 12",
        titre="Procédure concernant les déficits excessifs (PDE)",
        texte_integral="Fixe le plafond de déficit public à 3,0 % du PIB et le ratio de dette à 60,0 % du PIB.",
        strate_impactee="Européen",
        effet_simulation="Sous le pacte 2024, déclenche une astreinte semestrielle de 0,05 % du PIB si l'effort annuel < 0,5 pt.",
    ),
    "REG_EIDAS_910_2014": ArticleDeLoi(
        identifiant="REG_EIDAS_910_2014",
        code_ou_traite="Règlement (UE) n° 910/2014 (eIDAS)",
        article="Articles 8 et 9",
        titre="Niveaux de garantie de l'identification électronique sécurisée",
        texte_integral="Définit les exigences du niveau de garantie 'Élevé' pour l'authentification numérique étatique.",
        strate_impactee="National",
        effet_simulation="Garantit l'immunité et l'inviolabilité des votes du RIC via FranceConnect+.",
    ),
    "OCDE_PILIER_2_CGI_223_VJ": ArticleDeLoi(
        identifiant="OCDE_PILIER_2_CGI_223_VJ",
        code_ou_traite="Code Général des Impôts & Directive (UE) 2022/2523",
        article="Art. 223 VJ et suiv. du CGI",
        titre="Imposition minimale mondiale des groupes multinationaux (Pilier 2 de l'OCDE)",
        texte_integral="Instaure un impôt complémentaire garantissant un niveau minimum effectif d'imposition de 15 % sur les bénéfices des groupes multinationaux et nationaux de grande envergure réalisant plus de 750 M€ de CA.",
        strate_impactee="Mondial",
        effet_simulation="Alimente les recettes fiscales internationales de régulation et assainit la concurrence avec les PME territoriales.",
    ),
    "REG_UE_2023_956_MACF": ArticleDeLoi(
        identifiant="REG_UE_2023_956_MACF",
        code_ou_traite="Règlement (UE) 2023/956 du Parlement européen et du Conseil",
        article="Règlement (UE) 2023/956",
        titre="Mécanisme d'Ajustement Carbone aux Frontières (MACF / CBAM)",
        texte_integral="Met en place un mécanisme d'égalisation du coût du carbone entre la production industrielle européenne soumise à l'ETS et les importations en provenance de pays tiers sans tarification carbone.",
        strate_impactee="Mondial",
        effet_simulation="Protège les filières industrielles nationales, stimule la décarbonation et génère des recettes de certificats carbone.",
    ),
    "BALE_III_REG_575_2013": ArticleDeLoi(
        identifiant="BALE_III_REG_575_2013",
        code_ou_traite="Règlement (UE) n° 575/2013 (CRR) - Accords de Bâle III / Bâle IV",
        article="Règlement CRR art. 92 & 114",
        titre="Exigences prudentielles et pondération des risques souverains bancaires",
        texte_integral="Fixe les ratios de fonds propres CET1 (Common Equity Tier 1) et encadre l'exposition des bilans bancaires aux titres de dette souveraine.",
        strate_impactee="Mondial",
        effet_simulation="Sensibilise le refinancement bancaire et le crédit aux PME au spread des obligations souveraines (OAT).",
    ),
    "OMC_GATT_ART_XX": ArticleDeLoi(
        identifiant="OMC_GATT_ART_XX",
        code_ou_traite="Accord général sur les tarifs douaniers et le commerce (GATT / OMC)",
        article="Article XX (Exceptions générales)",
        titre="Exceptions environnementales et de protection des ressources naturelles épuisables",
        texte_integral="Autorise des mesures dérogeant au libre-échange strict si elles sont nécessaires à la protection de la santé et de la vie des personnes ou à la conservation des ressources naturelles.",
        strate_impactee="Mondial",
        effet_simulation="Sécurise juridiquement l'allotissement écologique et les critères de proximité dans la commande publique.",
    ),
    "CONST_ART_24": ArticleDeLoi(
        identifiant="CONST_ART_24",
        code_ou_traite="Constitution du 4 octobre 1958",
        article="Article 24",
        titre="Attributions du Parlement et représentation des collectivités par le Sénat",
        texte_integral="Le Parlement vote la loi. Il contrôle l'action du Gouvernement. Il évalue les politiques publiques. Le Sénat assure la représentation des collectivités territoriales de la République.",
        strate_impactee="National",
        effet_simulation="Fonde le bicamérisme et le rôle protecteur du Sénat envers les finances locales des communes et départements.",
    ),
    "CONST_ART_47_2": ArticleDeLoi(
        identifiant="CONST_ART_47_2",
        code_ou_traite="Constitution du 4 octobre 1958",
        article="Article 47-2",
        titre="Mission constitutionnelle de la Cour des comptes",
        texte_integral="La Cour des comptes assiste le Parlement et le Gouvernement dans le contrôle de l'action du Gouvernement et l'exécution des lois de finances et de financement de la sécurité sociale.",
        strate_impactee="National",
        effet_simulation="Fournit les audits indépendants fondant les 24 Md€ d'économies structurelles sur les doublons et niches inefficaces.",
    ),
    "CONST_ART_61_1": ArticleDeLoi(
        identifiant="CONST_ART_61_1",
        code_ou_traite="Constitution du 4 octobre 1958",
        article="Article 61-1",
        titre="Question Prioritaire de Constitutionnalité (QPC)",
        texte_integral="Lorsque, à l'occasion d'une instance en cours devant une juridiction, il est soutenu qu'une disposition législative porte atteinte aux droits et libertés que la Constitution garantit, le Conseil constitutionnel peut être saisi.",
        strate_impactee="National",
        effet_simulation="Permet aux citoyens et entreprises de purger toute loi attentatoire aux droits fondamentaux ou libertés publiques.",
    ),
    "CONST_ART_71_1": ArticleDeLoi(
        identifiant="CONST_ART_71_1",
        code_ou_traite="Constitution du 4 octobre 1958",
        article="Article 71-1",
        titre="Statut et attributions du Défenseur des droits",
        texte_integral="Le Défenseur des droits veille au respect des droits et libertés par les administrations de l'État, les collectivités territoriales, les établissements publics et tout organisme investi d'une mission de service public.",
        strate_impactee="National",
        effet_simulation="Protège les administrés contre les dysfonctionnements des caisses sociales et services publics de proximité.",
    ),
    "DDHC_ART_14": ArticleDeLoi(
        identifiant="DDHC_ART_14",
        code_ou_traite="Déclaration des Droits de l'Homme et du Citoyen de 1789",
        article="Article 14",
        titre="Consentement démocratique à l'impôt et contrôle de son emploi",
        texte_integral="Tous les Citoyens ont le droit de constater, par eux-mêmes ou par leurs représentants, la nécessité de la contribution publique, de la consentir librement, d'en suivre l'emploi, et d'en déterminer la quotité, l'assiette, le recouvrement et la durée.",
        strate_impactee="Transversal",
        effet_simulation="Légitime la transparence budgétaire absolue et l'affectation prioritaire des impôts au service public.",
    ),
    "CHARTE_ENV_ART_1": ArticleDeLoi(
        identifiant="CHARTE_ENV_ART_1",
        code_ou_traite="Charte de l'environnement de 2004",
        article="Article 1er",
        titre="Droit à un environnement équilibré et respectueux de la santé",
        texte_integral="Chacun a le droit de vivre dans un environnement équilibré et respectueux de la santé.",
        strate_impactee="National",
        effet_simulation="Conditionne le versement des aides publiques aux entreprises à leur bilan carbone certifié (Smart Clearing BEGES).",
    ),
    "CRPA_L123_1": ArticleDeLoi(
        identifiant="CRPA_L123_1",
        code_ou_traite="Code des relations entre le public et l'administration",
        article="Article L. 123-1 (Loi ESSOC)",
        titre="Droit à l'erreur des usagers et contribuables de bonne foi",
        texte_integral="Une personne ayant méconnu pour la première fois une règle applicable à sa situation ne peut faire l'objet d'une sanction pécuniaire si elle a régularisé sa situation de bonne foi.",
        strate_impactee="National",
        effet_simulation="Distingue la simple erreur administrative des ménages/artisans de la grande fraude fiscale organisée délibérée.",
    ),
    "CCOM_L710_1": ArticleDeLoi(
        identifiant="CCOM_L710_1",
        code_ou_traite="Code de commerce",
        article="Article L. 710-1",
        titre="Statut d'établissement public des Chambres de Commerce et d'Industrie (CCI)",
        texte_integral="Les chambres de commerce et d'industrie sont des établissements publics administratifs de l'État animés par des commerçants et industriels élus, chargés de représenter les intérêts généraux de l'industrie, du commerce et des services.",
        strate_impactee="Local",
        effet_simulation="Appuie le tissu des 3,8 millions d'entreprises, gère les infrastructures (ports/aéroports) et facilite l'export des PME.",
    ),
    # -------------------------------------------------------------------------
    # BLOC DÉFENSE, SÉCURITÉ ET GÉOPOLITIQUE (STRATE 5)
    # -------------------------------------------------------------------------
    "CONST_ART_15": ArticleDeLoi(
        identifiant="CONST_ART_15",
        code_ou_traite="Constitution du 4 octobre 1958",
        article="Article 15",
        titre="Le Président de la République, chef des armées",
        texte_integral="Le Président de la République est le chef des armées. Il préside les conseils et les comités supérieurs de la défense nationale.",
        strate_impactee="National",
        effet_simulation="Fonde la chaîne de décision de la dissuasion et l'engagement des forces dans les scénarios de la strate 5.",
    ),
    "CONST_ART_35": ArticleDeLoi(
        identifiant="CONST_ART_35",
        code_ou_traite="Constitution du 4 octobre 1958",
        article="Article 35",
        titre="Contrôle parlementaire de l'engagement des forces",
        texte_integral="La déclaration de guerre est autorisée par le Parlement. Le Gouvernement informe le Parlement de sa décision de faire intervenir les forces armées à l'étranger, au plus tard trois jours après le début de l'intervention. Lorsque la durée de l'intervention excède quatre mois, le Gouvernement soumet sa prolongation à l'autorisation du Parlement.",
        strate_impactee="National",
        effet_simulation="Conditionne les scénarios d'escalade à un vote parlementaire : relie l'engagement militaire au risque de censure.",
    ),
    "LPM_2023_703": ArticleDeLoi(
        identifiant="LPM_2023_703",
        code_ou_traite="Loi n° 2023-703 du 1er août 2023 de programmation militaire 2024-2030",
        article="Article 3 et rapport annexé",
        titre="Trajectoire financière de l'effort de défense",
        texte_integral="La présente loi fixe une trajectoire de besoins programmés des armées de 413,3 milliards d'euros sur la période 2024-2030, avec des marches annuelles d'augmentation des crédits de la mission Défense, complétées par les surmarches décidées en 2025 pour les exercices 2026 et 2027.",
        strate_impactee="National",
        effet_simulation="Calibre le levier `effort_defense_cible_pct_pib` et le surcoût budgétaire annuel injecté dans les dépenses des APU.",
    ),
    "OTAN_ART_3": ArticleDeLoi(
        identifiant="OTAN_ART_3",
        code_ou_traite="Traité de l'Atlantique Nord (4 avril 1949) & Déclaration du sommet de La Haye (25 juin 2025)",
        article="Article 3",
        titre="Capacité de résistance et engagement d'investissement de défense (3,5 % + 1,5 % = 5 % du PIB)",
        texte_integral="Les parties, agissant individuellement et conjointement, maintiendront et accroîtront leur capacité individuelle et collective de résistance à une attaque armée. Les Alliés se sont engagés à La Haye à investir 5 % de leur PIB annuel d'ici 2035, dont au moins 3,5 % au titre des besoins de défense essentiels et 1,5 % au titre de la sécurité et de la résilience au sens large.",
        strate_impactee="Mondial",
        effet_simulation="Fixe la cible de 3,50 % du PIB du scénario de réarmement et la trajectoire de ~+0,15 à +0,28 pt de PIB par an.",
    ),
    "OTAN_ART_5": ArticleDeLoi(
        identifiant="OTAN_ART_5",
        code_ou_traite="Traité de l'Atlantique Nord (4 avril 1949)",
        article="Article 5",
        titre="Clause de défense collective",
        texte_integral="Les parties conviennent qu'une attaque armée contre l'une ou plusieurs d'entre elles survenant en Europe ou en Amérique du Nord sera considérée comme une attaque dirigée contre toutes les parties.",
        strate_impactee="Mondial",
        effet_simulation="Déclenche les cascades d'escalade des scénarios B et D (Ukraine-OTAN, convergence Chine-Russie-Iran).",
    ),
    "TFUE_ART_42_7_TUE": ArticleDeLoi(
        identifiant="TFUE_ART_42_7_TUE",
        code_ou_traite="Traité sur l'Union européenne",
        article="Article 42, paragraphe 7",
        titre="Clause d'assistance mutuelle de l'Union européenne",
        texte_integral="Au cas où un État membre serait l'objet d'une agression armée sur son territoire, les autres États membres lui doivent aide et assistance par tous les moyens en leur pouvoir.",
        strate_impactee="Europe",
        effet_simulation="Solidarise le coût budgétaire de la défense européenne dans les scénarios d'agression sur le flanc est.",
    ),
    "REG_UE_2024_1263_CLAUSE": ArticleDeLoi(
        identifiant="REG_UE_2024_1263_CLAUSE",
        code_ou_traite="Règlement (UE) 2024/1263 — volet préventif du Pacte de stabilité et de croissance réformé",
        article="Articles 25 et 26 (clauses de sauvegarde nationale et générale)",
        titre="Clause de sauvegarde nationale pour l'effort de défense",
        texte_integral="Le Conseil peut, sur recommandation de la Commission, autoriser un État membre à s'écarter de sa trajectoire de dépenses nettes lorsque des circonstances exceptionnelles indépendantes de sa volonté ont des effets majeurs sur ses finances publiques, pour autant que cet écart ne compromette pas la soutenabilité budgétaire à moyen terme.",
        strate_impactee="Europe",
        effet_simulation="Neutralise jusqu'à 1,5 point de PIB de dépenses de défense dans l'évaluation du déficit au titre de la PDE.",
    ),
    "REG_UE_2023_1781_CHIPS": ArticleDeLoi(
        identifiant="REG_UE_2023_1781_CHIPS",
        code_ou_traite="Règlement (UE) 2023/1781 établissant un cadre de mesures pour renforcer l'écosystème européen des semi-conducteurs (Chips Act)",
        article="Articles 1er et 22 à 25",
        titre="Souveraineté européenne sur les semi-conducteurs et mécanisme de crise",
        texte_integral="Le présent règlement établit un cadre visant à renforcer l'écosystème des semi-conducteurs au niveau de l'Union, à garantir la sécurité de l'approvisionnement et la résilience, et institue un mécanisme de suivi et de réaction aux crises de pénurie, y compris des commandes prioritaires et des achats communs.",
        strate_impactee="Europe",
        effet_simulation="Paramètre `plan_souverainete_semiconducteurs_mde` : amortit jusqu'à 50 % du choc d'un blocus du détroit de Taïwan.",
    ),
    "DIR_UE_2022_2555_NIS2": ArticleDeLoi(
        identifiant="DIR_UE_2022_2555_NIS2",
        code_ou_traite="Directive (UE) 2022/2555 concernant des mesures destinées à assurer un niveau élevé commun de cybersécurité (NIS 2)",
        article="Articles 20 à 23",
        titre="Cyber-résilience des entités essentielles et importantes",
        texte_integral="Les États membres veillent à ce que les entités essentielles et importantes prennent les mesures techniques, opérationnelles et organisationnelles appropriées et proportionnées pour gérer les risques menaçant la sécurité des réseaux et des systèmes d'information, et notifient tout incident important.",
        strate_impactee="Europe",
        effet_simulation="Indice de cyber-résilience : atténue jusqu'à 60 % le coût en PIB d'une attaque systémique sur les OIV.",
    ),
    "CENERGIE_L642_2": ArticleDeLoi(
        identifiant="CENERGIE_L642_2",
        code_ou_traite="Code de l'énergie (obligations AIE / accord de 1974)",
        article="Article L. 642-2",
        titre="Stocks stratégiques pétroliers de sécurité",
        texte_integral="Les opérateurs pétroliers sont tenus de constituer et de conserver en permanence des stocks stratégiques correspondant à une fraction des quantités mises à la consommation, permettant de couvrir au minimum quatre-vingt-dix jours d'importations nettes.",
        strate_impactee="National",
        effet_simulation="Levier `liberation_stocks_strategiques` : amortit 30 % du choc pétrolier d'une fermeture d'Hormuz, dans la limite du plancher de 60 jours.",
    ),
    "CNUDM_ART_38": ArticleDeLoi(
        identifiant="CNUDM_ART_38",
        code_ou_traite="Convention des Nations unies sur le droit de la mer (Montego Bay, 1982)",
        article="Articles 37 et 38",
        titre="Droit de passage en transit dans les détroits internationaux",
        texte_integral="Dans les détroits servant à la navigation internationale entre une partie de la haute mer ou une zone économique exclusive et une autre partie de la haute mer ou une zone économique exclusive, tous les navires et aéronefs jouissent du droit de passage en transit sans entrave.",
        strate_impactee="Mondial",
        effet_simulation="Qualifie juridiquement la fermeture d'Hormuz, de Bab el-Mandeb ou du détroit de Taïwan comme illicite et fonde les opérations d'escorte.",
    ),
    "TNP_ART_6": ArticleDeLoi(
        identifiant="TNP_ART_6",
        code_ou_traite="Traité sur la non-prolifération des armes nucléaires (1968)",
        article="Article VI",
        titre="Obligation de désarmement nucléaire négocié",
        texte_integral="Chacune des parties au traité s'engage à poursuivre de bonne foi des négociations sur des mesures efficaces relatives à la cessation de la course aux armements nucléaires à une date rapprochée et au désarmement nucléaire.",
        strate_impactee="Mondial",
        effet_simulation="Référentiel du suivi des arsenaux (SIPRI 2026 : 12 187 têtes) et du paramètre `risque_usage_nucleaire_tactique_pct`.",
    ),
    "CART_L711_1": ArticleDeLoi(
        identifiant="CART_L711_1",
        code_ou_traite="Code de l'artisanat & Code de commerce",
        article="Article L. 711-1",
        titre="Statut et missions des Chambres de Métiers et de l'Artisanat (CMA)",
        texte_integral="Les chambres de métiers et de l'artisanat sont des établissements publics administratifs représentant les intérêts généraux de l'artisanat, tenant le Registre national des entreprises et organisant l'apprentissage artisanal.",
        strate_impactee="Local",
        effet_simulation="Garantit l'excellence des 250 métiers manuels, la transmission des ateliers et le label Maître Artisan.",
    ),
    "CRURAL_L510_1": ArticleDeLoi(
        identifiant="CRURAL_L510_1",
        code_ou_traite="Code rural et de la pêche maritime",
        article="Article L. 510-1",
        titre="Statut et missions des Chambres d'Agriculture (CA)",
        texte_integral="Les chambres d'agriculture sont des établissements publics représentant auprès de l'État et des collectivités l'ensemble des intérêts agricoles, forestiers et du monde rural, et concourant à la transition agroécologique et à la souveraineté alimentaire.",
        strate_impactee="Local",
        effet_simulation="Protège les terres agricoles contre l'artificialisation (CDPENAF), installe les jeunes paysans et soutient les circuits courts.",
    ),
}


def get_corpus_lois() -> dict[str, ArticleDeLoi]:
    """Retourne l'intégralité du registre légal."""
    return REGISTRE_LEGAL


def rechercher_loi(mot_cle: str) -> list[ArticleDeLoi]:
    """Recherche des textes par mot-clé dans le titre, le code ou l'effet."""
    mot_cle_lower = mot_cle.lower()
    resultats = []
    for art in REGISTRE_LEGAL.values():
        if (
            mot_cle_lower in art.titre.lower()
            or mot_cle_lower in art.code_ou_traite.lower()
            or mot_cle_lower in art.effet_simulation.lower()
            or mot_cle_lower in art.article.lower()
        ):
            resultats.append(art)
    return resultats
