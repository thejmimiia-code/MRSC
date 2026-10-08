"""simulateur/lexique.py — le vocabulaire du simulateur, en français ordinaire.

Pourquoi ce module
------------------

Le simulateur manipule des grandeurs que personne n'emploie dans la vie
courante : « spread », « point de base », « OAT », « procédure de déficit
excessif », « effort structurel ». Un outil démocratique qui n'est lisible que
par ceux qui savent déjà n'est pas un outil démocratique : il devient un
argument d'autorité.

Ce module est donc une pièce du projet, pas une aide en ligne. Chaque terme
technique employé par l'interface reçoit ici :

* **une définition en français ordinaire**, sans jargon renvoyant à un autre
  jargon (définir « spread » par « écart de rendement souverain » ne sert à
  personne) ;
* **un repère chiffré** quand il existe : grandeur réelle, ordre de grandeur,
  ou traduction en euros ;
* **des renvois** vers les termes voisins, pour circuler sans dictionnaire.

Les définitions sont volontairement non normatives : ce lexique explique ce
qu'est une grandeur et à quoi elle sert, il ne dit pas ce qu'il faut en penser.

Portée
------

Le lexique est servi par ``GET /api/lexique`` (avec recherche ``?q=…``) et
utilisé par la page de deux façons : un panneau consultable, et le
soulignement discret des termes techniques dans les textes affichés — au survol
ou au clavier, la définition s'affiche sans quitter la page.

Aucune dépendance externe : bibliothèque standard uniquement.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

#: Catégories, dans l'ordre de lecture de la page. Chacune est introduite par
#: une phrase qui dit de quoi il s'agit — lire une catégorie doit suffire à
#: comprendre si l'on est au bon endroit.
CATEGORIES: dict[str, dict[str, str]] = {
    "budget": {
        "libelle": "Budget de l'État",
        "introduction": "Comment l'État gagne, dépense et emprunte. Ce sont les"
                        " mots des finances publiques, expliqués comme un budget"
                        " de famille — en beaucoup plus grand.",
    },
    "marches": {
        "libelle": "Dette, taux et marchés",
        "introduction": "À qui l'État emprunte, à quel prix, et ce qui fait"
                        " monter ou descendre ce prix. C'est l'échelon qui"
                        " décide du coût de l'argent public.",
    },
    "europe": {
        "libelle": "Règles européennes",
        "introduction": "Les engagements que la France a signés, ce qu'ils"
                        " interdisent, et les marges qu'ils laissent.",
    },
    "geopolitique": {
        "libelle": "Géopolitique et défense",
        "introduction": "Conflits, routes commerciales, approvisionnements :"
                        " ce qui arrive de l'extérieur et que le budget"
                        " national ne décide pas.",
    },
    "quotidien": {
        "libelle": "Vie quotidienne",
        "introduction": "Les grandeurs qui se voient sur un bulletin de paie,"
                        " un loyer ou un ticket de caisse.",
    },
    "simulateur": {
        "libelle": "Lire le simulateur",
        "introduction": "Comment cet outil calcule, ce que veulent dire ses"
                        " scores, et ses limites. À lire avant d'interpréter"
                        " un chiffre.",
    },
}

ORDRE_CATEGORIES = ("budget", "marches", "europe", "geopolitique", "quotidien", "simulateur")


@dataclass(frozen=True)
class Terme:
    """Une entrée du lexique.

    Attributes:
        cle: identifiant technique stable (utilisé par l'interface).
        terme: le mot tel qu'il est écrit dans la page.
        categorie: une clé de :data:`CATEGORIES`.
        definition: une à trois phrases de français ordinaire.
        repere: exemple chiffré ou ordre de grandeur, si pertinent.
        formes: autres écritures du même mot à reconnaître dans un texte.
        voir: clés des termes voisins.
    """

    cle: str
    terme: str
    categorie: str
    definition: str
    repere: str = ""
    formes: tuple[str, ...] = ()
    voir: tuple[str, ...] = field(default=())


#: Le lexique. Ordre : du plus concret au plus abstrait dans chaque catégorie.
TERMES: tuple[Terme, ...] = (
    # ── Budget de l'État ───────────────────────────────────────────────────
    Terme(
        cle="milliard",
        terme="Milliard (Md€)",
        categorie="budget",
        definition="Un milliard d'euros, c'est mille millions. L'État manipule"
                   " des sommes de cette taille : on écrit « Md€ » parce que"
                   " les zéros deviennent illisibles.",
        repere="1 Md€ = 1 000 000 000 €. Le budget de l'État se compte en"
               " centaines de Md€ ; le PIB français, en milliers de Md€.",
        formes=("milliards", "Md€", "md€"),
        voir=("pib",),
    ),
    Terme(
        cle="pib",
        terme="PIB",
        categorie="budget",
        definition="Produit intérieur brut : la valeur de tout ce que le pays a"
                   " produit en une année. C'est l'étalon qui permet de dire"
                   " qu'une dépense est « grosse » ou « petite » quelle que"
                   " soit la taille du pays.",
        repere="Environ 3 000 Md€ pour la France. 1 % du PIB ≈ 30 Md€.",
        formes=("PIB", "produit intérieur brut"),
        voir=("point_pib", "prelevements"),
    ),
    Terme(
        cle="point_pib",
        terme="Point de PIB",
        categorie="budget",
        definition="Un pour-cent de la richesse produite en un an. Les finances"
                   " publiques se mesurent souvent en points de PIB plutôt qu'en"
                   " euros, parce que cela reste comparable d'une année à"
                   " l'autre.",
        repere="1 point de PIB ≈ 30 Md€ aujourd'hui. Un déficit de 5 % du PIB"
               " vaut donc environ 150 Md€ en un an.",
        formes=("points de PIB", "% du PIB"),
        voir=("pib", "deficit"),
    ),
    Terme(
        cle="deficit",
        terme="Déficit public",
        categorie="budget",
        definition="La différence, sur une année, entre ce que l'État et les"
                   " administrations publiques dépensent et ce qu'ils"
                   " encaissent. C'est un manque à gagner annuel, pas une"
                   " somme accumulée.",
        repere="Le déficit se mesure en % du PIB : 3 % est le plafond prévu par"
               " les règles européennes.",
        formes=("déficit", "déficit public"),
        voir=("dette", "solde", "maastricht"),
    ),
    Terme(
        cle="dette",
        terme="Dette publique",
        categorie="budget",
        definition="La somme de tous les déficits passés, moins les années"
                   " d'excédent. C'est un stock, pas un flux : la dette est ce"
                   " que l'État doit, le déficit est ce qu'il a dû emprunter"
                   " dans l'année.",
        repere="Environ 3 500 Md€ pour la France, soit un peu plus de 115 % du"
               " PIB. On rapporte toujours la dette au PIB, jamais en euros"
               " seuls : un pays riche peut porter une dette plus lourde.",
        formes=("dette", "dette publique", "encours"),
        voir=("deficit", "charge_dette", "refinancement"),
    ),
    Terme(
        cle="charge_dette",
        terme="Charge de la dette",
        categorie="budget",
        definition="Les intérêts que l'État paie chaque année sur sa dette."
                   " C'est une dépense obligatoire : on ne peut pas la voter"
                   " ni la reporter, et elle grandit quand les taux montent.",
        repere="De l'ordre de 60 à 70 Md€ par an aujourd'hui — davantage que le"
               " budget de l'Éducation nationale.",
        formes=("charge de la dette", "intérêts de la dette"),
        voir=("dette", "oat", "taux_bce"),
    ),
    Terme(
        cle="recettes",
        terme="Recettes publiques",
        categorie="budget",
        definition="Tout ce que l'État encaisse : impôts, taxes, cotisations,"
                   " revenus de ses participations. Le contraire des dépenses.",
        repere="Les prélèvements obligatoires représentent environ 43 % du PIB"
               " en France ; en comptant l'ensemble des recettes publiques, on"
               " dépasse 50 %.",
        formes=("recettes", "recettes publiques"),
        voir=("depenses", "prelevements"),
    ),
    Terme(
        cle="depenses",
        terme="Dépenses publiques",
        categorie="budget",
        definition="Tout ce que l'État et les administrations publiques"
                   " paient : salaires des fonctionnaires, retraites,"
                   " hôpitaux, routes, armée, aides, intérêts de la dette.",
        repere="Environ 57 % du PIB — l'un des niveaux les plus élevés des pays"
               " développés.",
        formes=("dépenses", "dépenses publiques"),
        voir=("recettes", "deficit"),
    ),
    Terme(
        cle="prelevements",
        terme="Prélèvements obligatoires",
        categorie="budget",
        definition="Les impôts et cotisations que personne ne peut refuser de"
                   " payer : impôt sur le revenu, TVA, CSG, cotisations"
                   " sociales, impôts locaux. On les distingue des recettes"
                   " comme les dividendes d'entreprises publiques.",
        repere="Environ 43 % du PIB en France — le niveau de prélèvements, ce"
               " n'est pas le niveau des impôts sur les ménages.",
        formes=("PO", "prélèvements obligatoires"),
        voir=("recettes", "pib"),
    ),
    Terme(
        cle="solde",
        terme="Solde budgétaire",
        categorie="budget",
        definition="Recettes moins dépenses. Positif, c'est un excédent : l'État"
                   " rembourse. Négatif, c'est un déficit : il emprunte.",
        formes=("solde", "solde public"),
        voir=("deficit", "dette"),
    ),
    Terme(
        cle="exercice",
        terme="Exercice",
        categorie="budget",
        definition="Une année budgétaire. « L'exercice 2027 » désigne l'année"
                   " civile 2027 dans les comptes publics.",
        formes=("exercice", "année budgétaire"),
        voir=("plf",),
    ),
    Terme(
        cle="plf",
        terme="PLF et PLFSS",
        categorie="budget",
        definition="Projet de loi de finances et projet de loi de financement"
                   " de la Sécurité sociale : les deux textes votés chaque"
                   " automne qui fixent recettes et dépenses de l'année"
                   " suivante.",
        formes=("PLF", "PLFSS", "loi de finances"),
        voir=("exercice",),
    ),
    Terme(
        cle="dgf",
        terme="DGF",
        categorie="budget",
        definition="Dotation globale de fonctionnement : la somme que l'État"
                   " verse chaque année aux communes, départements et régions"
                   " pour faire tourner les services publics locaux. Quand"
                   " l'État la baisse, les collectivités doivent trouver"
                   " l'argent ailleurs — souvent en augmentant les impôts"
                   " locaux.",
        formes=("DGF", "dotation globale de fonctionnement", "dotations"),
        voir=("collectivites", "taxe_fonciere"),
    ),
    Terme(
        cle="collectivites",
        terme="Collectivités territoriales",
        categorie="budget",
        definition="Les échelons élus en dessous de l'État : communes,"
                   " intercommunalités, départements, régions. Elles votent"
                   " leur propre budget et gèrent écoles, routes, transports,"
                   " action sociale.",
        formes=("collectivités", "collectivités territoriales", "EPCI",
                "communes", "départements", "régions"),
        voir=("dgf", "regle_or"),
    ),
    Terme(
        cle="regle_or",
        terme="Règle d'or locale",
        categorie="budget",
        definition="L'obligation faite aux collectivités de présenter un budget"
                   " de fonctionnement à l'équilibre : elles ne peuvent"
                   " emprunter que pour investir, jamais pour payer les"
                   " salaires ou l'électricité.",
        formes=("règle d'or", "équilibre de fonctionnement"),
        voir=("collectivites", "dgf"),
    ),
    Terme(
        cle="taxe_fonciere",
        terme="Taxe foncière",
        categorie="budget",
        definition="Impôt local payé par le propriétaire d'un bien immobilier."
                   " Son taux est voté par la commune et le département : c'est"
                   " le levier fiscal le plus visible localement, donc celui"
                   " qui déclenche le plus vite une réaction des habitants.",
        formes=("taxe foncière", "foncier"),
        voir=("dgf", "collectivites"),
    ),
    Terme(
        cle="assiette",
        terme="Assiette fiscale",
        categorie="budget",
        definition="La matière sur laquelle porte un impôt. L'assiette de la"
                   " TVA, c'est la consommation ; celle de l'impôt sur le"
                   " revenu, ce sont les revenus déclarés. Augmenter un taux de"
                   " 1 point rapporte d'autant plus que l'assiette est large.",
        repere="L'assiette au taux normal de TVA est d'environ 780 Md€ : un"
               " point de TVA ≈ 7,8 Md€ de recettes.",
        formes=("assiette",),
        voir=("tva", "niche"),
    ),
    Terme(
        cle="niche",
        terme="Niche fiscale",
        categorie="budget",
        definition="Dispositif qui réduit l'impôt dû : exonération, réduction,"
                   " crédit d'impôt. Chaque niche a une raison d'être, mais"
                   " l'ensemble représente une dépense pour l'État — on parle"
                   " de « dépense fiscale ».",
        formes=("niches", "dépense fiscale", "dépenses fiscales"),
        voir=("assiette",),
    ),
    Terme(
        cle="tva",
        terme="TVA",
        categorie="budget",
        definition="Taxe sur la valeur ajoutée : impôt sur la consommation,"
                   " payé à chaque achat, proportionnellement au prix. Il est"
                   " payé par tout le monde, quel que soit le revenu — c'est"
                   " l'impôt le plus « plat » qui existe.",
        repere="Taux normal 20 %, taux réduit 10 % et 5,5 %. C'est la première"
               " recette de l'État.",
        formes=("TVA", "taxe sur la valeur ajoutée"),
        voir=("assiette", "pouvoir_achat"),
    ),
    Terme(
        cle="ir",
        terme="Impôt sur le revenu",
        categorie="budget",
        definition="Impôt payé sur les revenus d'une année, calculé par"
                   " tranches : chaque part du revenu est taxée à un taux"
                   " différent. Le taux le plus élevé ne s'applique qu'à la"
                   " dernière tranche, jamais à tout le revenu.",
        formes=("IR", "impôt sur le revenu", "tranche marginale"),
        voir=("quotient", "csg"),
    ),
    Terme(
        cle="quotient",
        terme="Quotient familial",
        categorie="budget",
        definition="Le nombre de « parts » d'un foyer : on divise le revenu par"
                   " ce nombre avant d'appliquer le barème, ce qui tient compte"
                   " des personnes à charge. Deux adultes = 2 parts ; chaque"
                   " enfant ajoute une demi-part (ou une part selon le rang).",
        formes=("parts", "quotient familial", "part fiscale"),
        voir=("ir",),
    ),
    Terme(
        cle="csg",
        terme="CSG et CRDS",
        categorie="budget",
        definition="Contributions sociales prélevées sur les revenus"
                   " d'activité, de remplacement et du capital. Contrairement à"
                   " l'impôt sur le revenu, elles ne sont pas calculées par"
                   " foyer : chacun les paie dès le premier euro, ce qui"
                   " explique leur poids politique.",
        repere="La CSG finance principalement la Sécurité sociale ; la CRDS"
               " contribue au remboursement de la dette sociale.",
        formes=("CSG", "CRDS", "contribution sociale généralisée"),
        voir=("ir", "retraite"),
    ),
    Terme(
        cle="flat_tax",
        terme="Flat tax",
        categorie="budget",
        definition="Prélèvement forfaitaire unique : un taux unique (30 %) sur"
                   " les revenus du capital — dividendes, intérêts, plus-values"
                   " — au lieu du barème progressif de l'impôt sur le revenu.",
        formes=("flat tax", "PFU", "prélèvement forfaitaire unique"),
        voir=("ir", "isf"),
    ),
    Terme(
        cle="isf",
        terme="ISF",
        categorie="budget",
        definition="Impôt de solidarité sur la fortune, remplacé en 2018 par"
                   " l'impôt sur la fortune immobilière (IFI), limité aux biens"
                   " immobiliers. Le débat porte sur l'assiette : patrimoine"
                   " total ou immobilier seulement.",
        formes=("ISF", "IFI", "impôt sur la fortune"),
        voir=("flat_tax", "succession"),
    ),
    Terme(
        cle="succession",
        terme="Droits de succession",
        categorie="budget",
        definition="Impôt payé par les héritiers sur ce qu'ils reçoivent, avec"
                   " des abattements par lien de parenté. C'est l'un des impôts"
                   " les plus discutés : il touche la transmission du"
                   " patrimoine entre générations.",
        formes=("succession", "droits de succession", "héritage"),
        voir=("isf",),
    ),
    Terme(
        cle="superprofits",
        terme="Superprofits",
        categorie="budget",
        definition="Bénéfices jugés exceptionnels, sans lien avec un effort"
                   " particulier de l'entreprise — par exemple quand un choc"
                   " mondial fait bondir les prix de l'énergie. Les taxer"
                   " suppose de définir ce qui est « exceptionnel », ce qui est"
                   " le point contesté.",
        formes=("superprofits", "taxe sur les superprofits"),
        voir=("ttf", "brent"),
    ),
    Terme(
        cle="ttf",
        terme="Taxe sur les transactions financières",
        categorie="budget",
        definition="Prélèvement minuscule (une fraction de pour-cent) sur chaque"
                   " achat d'actions. L'assiette est immense, donc le produit"
                   " peut être important ; on la prélève au dépositaire central,"
                   " ce qui rend l'évasion plus difficile.",
        formes=("TTF", "taxe sur les transactions financières"),
        voir=("superprofits", "fraude"),
    ),
    Terme(
        cle="fraude",
        terme="Fraude fiscale",
        categorie="budget",
        definition="Impôt légalement dû mais non payé : dissimulation de"
                   " revenus, fausses factures, optimisation abusive. On la"
                   " distingue de l'optimisation, qui utilise la loi, et de"
                   " l'erreur involontaire.",
        formes=("fraude", "fraude fiscale", "CFIA"),
        voir=("ttf", "niche"),
    ),

    # ── Dette, taux et marchés ─────────────────────────────────────────────
    Terme(
        cle="oat",
        terme="OAT 10 ans",
        categorie="marches",
        definition="Obligation assimilable du Trésor : l'emprunt par lequel"
                   " l'État français lève de l'argent à long terme. Son taux est"
                   " le prix auquel la France emprunte sur dix ans. C'est le"
                   " thermomètre le plus suivi de la confiance qu'accordent les"
                   " prêteurs.",
        repere="Un OAT à 3,35 % signifie que l'État paie environ 33,5 M€ d'inté"
               "rêts par an pour chaque milliard emprunté sur dix ans.",
        formes=("OAT", "obligation assimilable du Trésor", "emprunt d'État"),
        voir=("bund", "spread", "charge_dette"),
    ),
    Terme(
        cle="bund",
        terme="Bund",
        categorie="marches",
        definition="L'emprunt d'État allemand à dix ans, pris comme référence"
                   " européenne parce que l'Allemagne est jugée la plus sûre."
                   " Les autres pays sont comparés à elle.",
        formes=("Bund", "emprunt allemand"),
        voir=("oat", "spread"),
    ),
    Terme(
        cle="spread",
        terme="Spread",
        categorie="marches",
        definition="L'écart entre le taux auquel la France emprunte et celui de"
                   " l'Allemagne. Plus il est grand, plus les prêteurs jugent la"
                   " France risquée par rapport à l'Allemagne — et plus"
                   " l'emprunt coûte cher.",
        repere="Un spread de 50 points de base = 0,50 point de pourcentage de"
               " plus que l'Allemagne. Sur une dette de 3 500 Md€, un écart"
               " durable de 0,5 point se compte en milliards par an.",
        formes=("spread", "écart de taux", "écart OAT-Bund"),
        voir=("oat", "bund", "point_base"),
    ),
    Terme(
        cle="point_base",
        terme="Point de base",
        categorie="marches",
        definition="Un centième de point de pourcentage, noté « bp ». Les"
                   " marchés parlent en points de base parce qu'un centième de"
                   " point, sur des milliards, compte beaucoup.",
        repere="100 bp = 1 point de pourcentage. Un spread de 47 bp = 0,47 %.",
        formes=("bp", "points de base", "point de base", "pb"),
        voir=("spread",),
    ),
    Terme(
        cle="taux_bce",
        terme="Taux de la BCE",
        categorie="marches",
        definition="Le taux auquel la Banque centrale européenne rémunère les"
                   " dépôts des banques. En le montant, elle freine"
                   " l'inflation ; en le baissant, elle rend le crédit moins"
                   " cher. Tous les autres taux suivent, avec un décalage.",
        formes=("taux directeur", "taux de dépôt", "BCE", "banque centrale"),
        voir=("taux_immobilier", "inflation"),
    ),
    Terme(
        cle="taux_immobilier",
        terme="Taux de crédit immobilier",
        categorie="marches",
        definition="Le taux d'intérêt moyen auquel les ménages empruntent pour"
                   " acheter un logement. Il suit les taux longs et la"
                   " politique de la BCE : un point de plus réduit la somme"
                   " qu'un même revenu permet d'emprunter.",
        formes=("taux immobilier", "crédit immobilier"),
        voir=("taux_bce", "oat"),
    ),
    Terme(
        cle="taux_pme",
        terme="Taux de crédit aux PME",
        categorie="marches",
        definition="Le taux auquel les petites et moyennes entreprises"
                   " empruntent pour investir. Il est plus élevé que celui de"
                   " l'État, car le risque de défaut est plus grand.",
        formes=("taux PME", "crédit aux entreprises"),
        voir=("taux_immobilier",),
    ),
    Terme(
        cle="note_souveraine",
        terme="Note souveraine",
        categorie="marches",
        definition="L'appréciation, par une agence privée, de la capacité d'un"
                   " État à rembourser. Une lettre, de AAA (le mieux) à D"
                   " (défaut). Ce n'est ni un jugement politique ni une"
                   " prévision certaine : c'est un avis, qui pèse sur les taux.",
        repere="AA / AA- pour la France selon les agences ; chaque cran"
               " d'écart se traduit par quelques points de base de taux.",
        formes=("note", "notation", "rating"),
        voir=("agence", "oat"),
    ),
    Terme(
        cle="agence",
        terme="Agence de notation",
        categorie="marches",
        definition="Entreprise privée qui évalue le risque de défaut des États"
                   " et des entreprises. Ses notes ne sont pas une opinion"
                   " démocratique : elles orientent les fonds qui ont"
                   " l'interdiction d'acheter des titres mal notés.",
        formes=("agences de notation", "agence"),
        voir=("note_souveraine",),
    ),
    Terme(
        cle="prime_risque",
        terme="Prime de risque",
        categorie="marches",
        definition="Le supplément de taux demandé par les prêteurs quand la"
                   " situation paraît moins sûre — tensions géopolitiques,"
                   " instabilité politique, trajectoire budgétaire mal"
                   " maîtrisée. Elle s'ajoute au taux de base.",
        formes=("prime de risque",),
        voir=("spread", "escalade"),
    ),
    Terme(
        cle="refinancement",
        terme="Refinancement",
        categorie="marches",
        definition="Emprunter pour rembourser un emprunt qui arrive à échéance."
                   " L'État ne rembourse presque jamais sa dette d'un coup : il"
                   " la renouvelle en permanence. Si les taux montent au moment"
                   " du renouvellement, la charge augmente pour longtemps.",
        formes=("refinancement", "renouvellement de la dette"),
        voir=("dette", "charge_dette"),
    ),
    Terme(
        cle="non_residents",
        terme="Non-résidents",
        categorie="marches",
        definition="Investisseurs étrangers qui détiennent de la dette"
                   " française. Leur part mesure la dépendance du pays à"
                   " l'épargne du reste du monde : plus elle est haute, plus"
                   " le pays est exposé à un retournement de confiance.",
        repere="Un peu plus de la moitié de la dette française est détenue hors"
               " de France.",
        formes=("non-résidents", "détenteurs étrangers"),
        voir=("dette", "refinancement"),
    ),
    Terme(
        cle="brent",
        terme="Brent",
        categorie="marches",
        definition="Le pétrole de la mer du Nord, qui sert de référence"
                   " européenne pour le prix du baril. Quand il monte, la"
                   " facture énergétique du pays augmente, l'inflation suit et"
                   " le pouvoir d'achat baisse.",
        formes=("Brent", "baril", "pétrole"),
        voir=("inflation", "hormuz"),
    ),
    Terme(
        cle="eurusd",
        terme="EUR/USD",
        categorie="marches",
        definition="Le prix d'un euro en dollars. Un euro qui baisse rend les"
                   " exportations moins chères, mais renchérit tout ce qui est"
                   " acheté en dollars — dont le pétrole.",
        formes=("EUR/USD", "change", "euro/dollar"),
        voir=("brent",),
    ),

    # ── Europe ─────────────────────────────────────────────────────────────
    Terme(
        cle="maastricht",
        terme="Critère des 3 %",
        categorie="europe",
        definition="La règle héritée du traité de Maastricht : le déficit public"
                   " ne doit pas dépasser 3 % du PIB et la dette 60 % du PIB."
                   " Ces chiffres sont des bornes politiques, pas des lois de la"
                   " physique : plusieurs pays, dont la France, les dépassent"
                   " durablement.",
        formes=("3 %", "critères de Maastricht", "Maastricht"),
        voir=("pde", "pacte"),
    ),
    Terme(
        cle="pde",
        terme="Procédure de déficit excessif",
        categorie="europe",
        definition="La procédure ouverte par la Commission européenne quand un"
                   " pays dépasse les seuils : elle fixe une trajectoire de"
                   " retour et, en théorie, des sanctions. Elle s'étale sur"
                   " plusieurs années, ce qui laisse une marge de négociation"
                   " politique.",
        formes=("PDE", "déficit excessif"),
        voir=("maastricht", "pacte"),
    ),
    Terme(
        cle="pacte",
        terme="Pacte de stabilité",
        categorie="europe",
        definition="L'ensemble des règles qui encadrent les budgets des pays de"
                   " la zone euro. Il prévoit des souplesses — dont une clause"
                   " dérogatoire en cas de circonstances exceptionnelles.",
        formes=("pacte de stabilité", "Pacte de stabilité et de croissance"),
        voir=("pde", "clause_sauvegarde"),
    ),
    Terme(
        cle="clause_sauvegarde",
        terme="Clause de sauvegarde",
        categorie="europe",
        definition="La disposition qui autorise un pays à s'écarter"
                   " temporairement des règles budgétaires en cas de crise"
                   " grave — le réarmement, par exemple. Elle suspend la"
                   " contrainte, elle ne la supprime pas.",
        formes=("clause dérogatoire", "clause de sauvegarde"),
        voir=("pacte", "effort_defense"),
    ),
    Terme(
        cle="tpi",
        terme="Bouclier anti-coercition",
        categorie="europe",
        definition="L'instrument européen qui permet de riposter quand un pays"
                   " tiers utilise le commerce ou les marchés comme une arme"
                   " politique. Le simulateur s'en sert comme indicateur : s'il"
                   " est actif, la contrainte extérieure est forte.",
        formes=("TPI", "anti-coercition", "bouclier"),
        voir=("pacte",),
    ),
    Terme(
        cle="effort_structurel",
        terme="Effort structurel",
        categorie="europe",
        definition="Ce que le budget doit corriger durablement, une fois retirés"
                   " les effets de la conjoncture : une récession creuse"
                   " mécaniquement le déficit, sans que rien n'ait été décidé."
                   " L'effort structurel mesure la part venue des décisions.",
        formes=("effort structurel", "solde structurel"),
        voir=("pde", "deficit"),
    ),

    # ── Géopolitique ───────────────────────────────────────────────────────
    Terme(
        cle="chokepoint",
        terme="Point de passage stratégique",
        categorie="geopolitique",
        definition="Un endroit du globe par où passe une part décisive du"
                   " commerce mondial et qui peut être fermé : un détroit, un"
                   " canal. Le bloquer revient à étrangler une chaîne"
                   " d'approvisionnement entière.",
        repere="Hormuz : environ un cinquième du pétrole mondial.",
        formes=("chokepoint", "détroit", "points de passage"),
        voir=("hormuz", "taiwan"),
    ),
    Terme(
        cle="hormuz",
        terme="Détroit d'Ormuz",
        categorie="geopolitique",
        definition="Le passage maritime entre le golfe Persique et l'océan"
                   " Indien. Une grande partie du pétrole exporté par les pays"
                   " du Golfe y transite : sa fermeture ferait bondir le prix"
                   " de l'énergie dans le monde entier.",
        repere="Environ 20 % du pétrole mondial y passe.",
        formes=("Hormuz", "Ormuz", "détroit d'Hormuz"),
        voir=("chokepoint", "brent"),
    ),
    Terme(
        cle="taiwan",
        terme="Taïwan et semi-conducteurs",
        categorie="geopolitique",
        definition="Taïwan produit une part dominante des puces les plus"
                   " avancées, dont dépendent automobiles, téléphones, hôpitaux"
                   " et armements. Un blocus ne priverait pas seulement"
                   " d'électronique : il arrêterait des chaînes de production"
                   " entières.",
        repere="Environ 60 % des semi-conducteurs avancés.",
        formes=("Taïwan", "semi-conducteurs", "puces"),
        voir=("chokepoint", "bitd"),
    ),
    Terme(
        cle="bitd",
        terme="BITD",
        categorie="geopolitique",
        definition="Base industrielle et technologique de défense : les usines,"
                   " les savoir-faire et les sous-traitants qui permettent de"
                   " produire des armes en France. Elle se reconstruit"
                   " lentement : une commande passée aujourd'hui donne des"
                   " capacités dans cinq ou dix ans.",
        formes=("BITD", "base industrielle de défense", "industrie de défense"),
        voir=("effort_defense", "taiwan"),
    ),
    Terme(
        cle="effort_defense",
        terme="Effort de défense",
        categorie="geopolitique",
        definition="La part de la richesse nationale consacrée à la défense."
                   " Les alliés de l'OTAN se sont fixé une cible ; l'écart"
                   " entre cette cible et la dépense actuelle indique l'effort"
                   " à fournir.",
        repere="Cible OTAN : 3,5 % du PIB pour l'effort de défense, plus 1,5 %"
               " pour la sécurité au sens large, à l'horizon 2035.",
        formes=("effort de défense", "budget de la défense"),
        voir=("otan", "bitd"),
    ),
    Terme(
        cle="otan",
        terme="OTAN",
        categorie="geopolitique",
        definition="L'alliance militaire qui lie l'Europe et l'Amérique du Nord."
                   " Ses engagements chiffrés ne sont pas un traité de droit"
                   " national : ce sont des objectifs politiques, révisés à"
                   " chaque sommet.",
        formes=("OTAN", "Alliance atlantique"),
        voir=("effort_defense", "dissuasion"),
    ),
    Terme(
        cle="dissuasion",
        terme="Dissuasion nucléaire",
        categorie="geopolitique",
        definition="L'idée que la possession de l'arme nucléaire empêche"
                   " l'adversaire d'attaquer, par la crainte des représailles."
                   " Le simulateur suit le nombre d'armes et le degré de"
                   " tension, jamais l'usage : celui-ci n'est pas modélisable.",
        repere="Quelques milliers de têtes opérationnelles dans le monde,"
               " recensées chaque année par le SIPRI.",
        formes=("dissuasion", "arme nucléaire", "têtes nucléaires"),
        voir=("escalade", "sipri"),
    ),
    Terme(
        cle="sipri",
        terme="SIPRI",
        categorie="geopolitique",
        definition="Institut international de recherche sur la paix, basé à"
                   " Stockholm : sa publication annuelle fait référence sur les"
                   " dépenses militaires et les arsenaux nucléaires.",
        formes=("SIPRI",),
        voir=("dissuasion",),
    ),
    Terme(
        cle="aie",
        terme="Stocks stratégiques",
        categorie="geopolitique",
        definition="Les réserves de pétrole que les pays industrialisés"
                   " conservent pour tenir en cas de rupture. Les pays membres"
                   " de l'Agence internationale de l'énergie s'engagent sur"
                   " environ 90 jours de consommation.",
        repere="90 jours : c'est le temps que mettent les gouvernements à"
               " organiser une réponse collective.",
        formes=("stocks stratégiques", "réserves pétrolières", "AIE"),
        voir=("brent", "hormuz"),
    ),
    Terme(
        cle="escalade",
        terme="Escalade",
        categorie="geopolitique",
        definition="L'enchaînement par lequel un incident local devient un"
                   " affrontement plus large, chaque camp ripostant à la"
                   " riposte de l'autre. Le simulateur en mesure la"
                   " probabilité, comme une alerte — pas comme une prédiction.",
        formes=("escalade", "seuil nucléaire", "guerre"),
        voir=("dissuasion", "prime_risque"),
    ),

    # ── Vie quotidienne ────────────────────────────────────────────────────
    Terme(
        cle="pouvoir_achat",
        terme="Pouvoir d'achat",
        categorie="quotidien",
        definition="Ce que permet d'acheter un revenu. Il baisse quand les prix"
                   " montent plus vite que les salaires, même si le salaire"
                   " augmente. Le simulateur le suit sous forme d'indice :"
                   " 100 au départ, et l'on compare.",
        formes=("pouvoir d'achat",),
        voir=("inflation", "tva"),
    ),
    Terme(
        cle="inflation",
        terme="Inflation",
        categorie="quotidien",
        definition="La hausse générale des prix. Une inflation de 2 % par an"
                   " signifie qu'un panier de courses à 100 € en coûte 102 un"
                   " an plus tard : le même billet achète moins.",
        repere="L'indice des prix à la consommation harmonisé (IPCH) est la"
               " mesure européenne de référence.",
        formes=("inflation", "IPCH", "indice des prix", "prix à la consommation"),
        voir=("pouvoir_achat", "taux_bce"),
    ),
    Terme(
        cle="chomage",
        terme="Chômage",
        categorie="quotidien",
        definition="La part des personnes qui cherchent un emploi et n'en"
                   " trouvent pas. Le taux officiel ne compte ni le découragement"
                   " ni le temps partiel subi : il donne un ordre de grandeur,"
                   " pas un décompte.",
        formes=("chômage", "taux de chômage"),
        voir=("pauvrete",),
    ),
    Terme(
        cle="pauvrete",
        terme="Taux de pauvreté",
        categorie="quotidien",
        definition="La part de la population dont le revenu est inférieur à un"
                   " seuil, fixé à 60 % du revenu médian. C'est une mesure"
                   " relative : elle décrit les écarts dans un pays, pas la"
                   " misère absolue.",
        formes=("pauvreté", "taux de pauvreté"),
        voir=("gini", "chomage"),
    ),
    Terme(
        cle="gini",
        terme="Indice de Gini",
        categorie="quotidien",
        definition="Une mesure des inégalités de revenu, de 0 (tout le monde a"
                   " le même revenu) à 1 (une seule personne a tout). Entre"
                   " 0,25 et 0,35 pour la plupart des pays européens.",
        formes=("Gini", "inégalités"),
        voir=("pauvrete",),
    ),
    Terme(
        cle="retraite",
        terme="Retraites",
        categorie="quotidien",
        definition="Les pensions versées après la vie active. Le système"
                   " français fonctionne par répartition : les cotisations des"
                   " actifs paient les pensions des retraités, ce qui rend le"
                   " système directement sensible au rapport entre les deux.",
        formes=("retraite", "retraites", "pensions"),
        voir=("csg", "minima_sociaux"),
    ),
    Terme(
        cle="minima_sociaux",
        terme="Minima sociaux",
        categorie="quotidien",
        definition="Les aides versées à ceux qui n'ont pas ou peu de ressources"
                   " : RSA, allocation adulte handicapé, minimum vieillesse."
                   " Leur revalorisation est le levier le plus direct sur le"
                   " niveau de vie des plus pauvres.",
        formes=("minima sociaux", "RSA", "aides sociales"),
        voir=("pauvrete", "retraite"),
    ),

    # ── Lire le simulateur ─────────────────────────────────────────────────
    Terme(
        cle="levier",
        terme="Levier",
        categorie="simulateur",
        definition="Un réglage. Chaque levier correspond à une décision"
                   " publique possible : un taux, un montant, une règle activée"
                   " ou non. Bouger un levier relance toute la simulation.",
        repere="101 leviers répartis en 14 familles.",
        formes=("levier", "leviers", "réglage", "curseur"),
        voir=("domaine", "preset"),
    ),
    Terme(
        cle="domaine",
        terme="Domaine",
        categorie="simulateur",
        definition="Un secteur de l'action publique : santé, éducation, défense,"
                   " logement, climat… Chaque domaine est évalué par des"
                   " indicateurs chiffrés, dont la formule est publiée dans"
                   " l'audit.",
        repere="20 domaines, 74 indicateurs.",
        formes=("domaine", "domaine d'action publique"),
        voir=("score", "levier"),
    ),
    Terme(
        cle="score",
        terme="Score de domaine",
        categorie="simulateur",
        definition="Une note de 0 à 100 qui mesure l'écart entre la politique"
                   " choisie et la trajectoire de référence. 50 veut dire"
                   " « comme si de rien n'était » : ce n'est ni une bonne note"
                   " ni une moyenne scolaire, c'est le point zéro.",
        formes=("score", "note", "0-100"),
        voir=("reference", "domaine"),
    ),
    Terme(
        cle="reference",
        terme="Trajectoire de référence",
        categorie="simulateur",
        definition="Ce qui se passerait sans aucune politique nouvelle : le"
                   " même moteur, les mêmes données, tous les leviers au neutre."
                   " Tous les écarts affichés dans le simulateur sont mesurés"
                   " par rapport à elle.",
        formes=("référence", "trajectoire de référence", "neutre"),
        voir=("score", "ecart"),
    ),
    Terme(
        cle="ecart",
        terme="Écart (différences finies)",
        categorie="simulateur",
        definition="Le résultat de deux exécutions du moteur : une avec la"
                   " décision, une sans. La différence est l'effet attribué à la"
                   " décision. C'est la méthode la plus honnête ici, parce"
                   " qu'elle ne suppose pas de formule d'à-peu-près.",
        formes=("écart", "différences finies"),
        voir=("reference", "effet_direct"),
    ),
    Terme(
        cle="effet_direct",
        terme="Effet direct",
        categorie="simulateur",
        definition="La conséquence immédiate d'un réglage sur les domaines qu'il"
                   " vise : baisser la TVA touche d'abord le pouvoir d'achat."
                   " S'y ajoutent les effets indirects.",
        formes=("effet direct", "effets directs"),
        voir=("ricochet", "ecart"),
    ),
    Terme(
        cle="ricochet",
        terme="Ricochet",
        categorie="simulateur",
        definition="La conséquence de la conséquence : une dépense de défense"
                   " finance des usines, donc de l'emploi, donc des recettes"
                   " fiscales. Le simulateur les appelle « effet papillon » et"
                   " les sépare toujours des effets directs.",
        formes=("ricochet", "effet papillon", "effet indirect"),
        voir=("effet_direct",),
    ),
    Terme(
        cle="garde_fou",
        terme="Garde-fou",
        categorie="simulateur",
        definition="Un seuil au-delà duquel le modèle prévient : déficit,"
                   " taux, tension sociale, dette locale… Chaque garde-fou est"
                   " gradué en tolérable, vigilance, risqué, hors-sol. Ce sont"
                   " des repères du modèle, pas des seuils officiels, sauf"
                   " mention de la source.",
        repere="31 garde-fous, tous publiés avec leurs bornes et leur source"
               " dans « Audit & traçabilité ».",
        formes=("garde-fou", "garde-fous", "seuil"),
        voir=("niveau", "strate"),
    ),
    Terme(
        cle="niveau",
        terme="Niveaux d'alerte",
        categorie="simulateur",
        definition="La graduation des garde-fous : tolérable (rien à signaler),"
                   " vigilance (à surveiller), risqué (la trajectoire"
                   " s'éloigne), hors-sol (au-delà de ce que les sources"
                   " connues permettent d'étayer).",
        formes=("tolérable", "vigilance", "risqué", "hors-sol"),
        voir=("garde_fou",),
    ),
    Terme(
        cle="strate",
        terme="Strate",
        categorie="simulateur",
        definition="L'un des cinq échelons du modèle : local, national,"
                   " européen, mondial, géopolitique. Ils s'emboîtent comme des"
                   " poupées russes : ce qui se décide en haut se répercute en"
                   " bas, et inversement.",
        formes=("strate", "échelon", "échelons"),
        voir=("levier", "garde_fou"),
    ),
    Terme(
        cle="horizon",
        terme="Horizon",
        categorie="simulateur",
        definition="La durée de la projection : cinq ans (une mandature) ou dix"
                   " ans (deux). Les réformes à effet lent — formation, usines,"
                   " infrastructures — n'apparaissent qu'au-delà de la sixième"
                   " année.",
        formes=("horizon", "5 ans", "10 ans"),
        voir=("mandature",),
    ),
    Terme(
        cle="mandature",
        terme="Mandature",
        categorie="simulateur",
        definition="La durée d'un mandat présidentiel : cinq ans en France. Le"
                   " simulateur raisonne par mandature parce que c'est l'unité"
                   " de temps du débat politique.",
        formes=("mandature", "quinquennat"),
        voir=("horizon",),
    ),
    Terme(
        cle="preset",
        terme="Préréglage",
        categorie="simulateur",
        definition="Un ensemble cohérent de réglages, correspondant à une"
                   " orientation politique. Charger un préréglage n'empêche"
                   " rien : chaque levier reste ajustable à la main.",
        formes=("préréglage", "préréglages", "preset"),
        voir=("levier",),
    ),
    Terme(
        cle="matrice",
        terme="Matrice levier × domaine",
        categorie="simulateur",
        definition="Le tableau qui croise chaque réglage avec chaque domaine,"
                   " et donne l'effet mesuré. Elle se lit par ligne : « si je"
                   " bouge ce levier seul, voilà ce que ça change ».",
        formes=("matrice", "matrice croisée", "impacts croisés"),
        voir=("levier", "domaine"),
    ),
    Terme(
        cle="journal",
        terme="Journal causal",
        categorie="simulateur",
        definition="La liste des enchaînements que le moteur a réellement"
                   " appliqués, dans l'ordre. C'est la trace qui permet de"
                   " vérifier d'où sort chaque chiffre.",
        formes=("journal", "journal causal"),
        voir=("mediateur",),
    ),
    Terme(
        cle="mediateur",
        terme="Médiateur",
        categorie="simulateur",
        definition="Une grandeur intermédiaire par laquelle une décision passe"
                   " avant d'atteindre un domaine : l'investissement public"
                   " agit sur l'emploi, qui agit sur les recettes. Le médiateur"
                   " est le chaînon, pas le résultat.",
        formes=("médiateur", "grandeur intermédiaire"),
        voir=("journal", "ricochet"),
    ),
    Terme(
        cle="intergenerationnel",
        terme="Bilan intergénérationnel",
        categorie="simulateur",
        definition="Ce que la trajectoire laisse aux générations suivantes :"
                   " dette, patrimoine entretenu ou non, investissements"
                   " engagés, dommages climatiques. Le simulateur présente ces"
                   " composantes séparément, sans les additionner en un score"
                   " unique — un tel score cacherait un jugement.",
        formes=("intergénérationnel", "bilan intergénérationnel"),
        voir=("dette",),
    ),
    Terme(
        cle="modele",
        terme="Modèle, pas prophétie",
        categorie="simulateur",
        definition="Le simulateur applique des formules publiées à des données"
                   " publiques. Il explore des conséquences, il ne prévoit pas"
                   " l'avenir : un résultat n'est pas un pronostic, et deux"
                   " hypothèses voisines peuvent donner des trajectoires"
                   " éloignées.",
        formes=("modèle", "simulation", "projection"),
        voir=("reference", "ecart"),
    ),
)

_PAR_CLE = {terme.cle: terme for terme in TERMES}


def _normaliser(texte: str) -> str:
    """Normalise pour une recherche insensible à la casse et aux accents simples."""
    return " ".join((texte or "").lower().split())


def definir(cle: str) -> dict[str, Any] | None:
    """Retourne une entrée du lexique, ou ``None`` si elle n'existe pas."""
    terme = _PAR_CLE.get(cle)
    return asdict(terme) if terme else None


def _correspond(terme: Terme, recherche: str) -> bool:
    if not recherche:
        return True
    champs = (terme.cle, terme.terme, terme.definition, terme.repere, *termes_formes(terme))
    return any(recherche in _normaliser(champ) for champ in champs)


def termes_formes(terme: Terme) -> tuple[str, ...]:
    """Toutes les écritures reconnaissables d'un terme (la sienne + alias)."""
    return (terme.terme, *terme.formes)


def rechercher(recherche: str) -> list[Terme]:
    """Recherche plein texte dans le libellé, la définition et les alias."""
    motif = _normaliser(recherche or "")
    if not motif:
        return list(TERMES)
    return [terme for terme in TERMES if _correspond(terme, motif)]


def lexique_public(recherche: str | None = None) -> dict[str, Any]:
    """Charge utile de ``GET /api/lexique``.

    Contient les catégories (avec leur phrase d'introduction), les termes
    trouvés, et la liste des formes à souligner dans la page — du plus long au
    plus court, pour que « point de PIB » gagne sur « PIB » au moment de
    baliser un texte.
    """
    trouves = rechercher(recherche)
    formes: list[dict[str, str]] = []
    for terme in TERMES:
        for forme in dict.fromkeys(termes_formes(terme)):
            if len(forme) >= 2:
                formes.append({"forme": forme, "cle": terme.cle})
    formes.sort(key=lambda item: len(item["forme"]), reverse=True)
    return {
        "nombre": len(trouves),
        "total": len(TERMES),
        "recherche": recherche or "",
        "categories": [
            {
                "cle": cle,
                **CATEGORIES[cle],
                "nombre": sum(1 for terme in trouves if terme.categorie == cle),
            }
            for cle in ORDRE_CATEGORIES
        ],
        "termes": [asdict(terme) for terme in trouves],
        "formes": formes,
    }


def citer(texte: str) -> list[Terme]:
    """Termes du lexique présents dans un texte quelconque (pour l'interface)."""
    motif = _normaliser(texte or "")
    if not motif:
        return []
    trouves: list[Terme] = []
    for terme in TERMES:
        for forme in termes_formes(terme):
            if _normaliser(forme) in motif:
                trouves.append(terme)
                break
    return trouves
