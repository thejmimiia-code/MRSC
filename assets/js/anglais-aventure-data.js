/* Dialogues originaux du prototype « Les Escales ». Les missions et leurs
   réponses sont des données locales : aucune récupération réseau ni IA. */
globalThis.MRSCEnglishAdventureData = Object.freeze({
  version: 1,
  missions: [
    {
      id: "gare",
      title: "La gare des marées",
      place: "Le guichet des départs",
      level: "Pré-A1 · A1",
      theme: "station",
      time: "5 à 8 min, à ton rythme",
      brief: "Tu rejoins une amie au musée. Trouve le bon train et demande un renseignement si tu en as besoin.",
      outcome: "Demander un billet, comprendre une indication simple et vérifier une information.",
      sceneDescription: "Une gare miniature au bord de l’eau, avec un train, des panneaux bleus et un chemin vers le musée.",
      turns: [
        {
          speaker: "L’agent·e",
          english: "Hi there! Where would you like to go?",
          french: "Bonjour ! Où aimerais-tu aller ?",
          objective: "Dire que tu veux aller au musée.",
          modelEnglish: "A ticket to the museum, please.",
          modelFrench: "Un billet pour le musée, s’il vous plaît.",
          tip: "« The museum » donne la destination. « Please » adoucit la demande.",
          options: [
            { english: "A ticket to the museum, please.", french: "Un billet pour le musée, s’il vous plaît.", feedback: "La destination et la demande de billet sont claires.", replyEnglish: "Of course. The museum train leaves from platform two.", replyFrench: "Bien sûr. Le train pour le musée part du quai numéro deux." },
            { english: "I’d like to visit the museum.", french: "J’aimerais visiter le musée.", feedback: "Tu exprimes ton projet avec une phrase complète ; l’agent peut te proposer le billet adapté.", replyEnglish: "Lovely choice. The museum train leaves from platform two.", replyFrench: "Très bon choix. Le train pour le musée part du quai numéro deux." },
            { english: "The museum, please.", french: "Le musée, s’il vous plaît.", feedback: "Quelques mots bien choisis peuvent suffire pour commencer. Tu peux compléter ensuite si besoin.", replyEnglish: "Sure. Platform two is just over there.", replyFrench: "Bien sûr. Le quai numéro deux est juste là-bas." }
          ]
        },
        {
          speaker: "L’agent·e",
          english: "Would you like me to show you on the map?",
          french: "Veux-tu que je te montre sur le plan ?",
          objective: "Accepter le plan, demander de l’aide ou décliner poliment.",
          modelEnglish: "Yes, please. That would be helpful.",
          modelFrench: "Oui, s’il vous plaît. Ce serait utile.",
          tip: "« Could you show me…? » est une autre façon polie de demander de l’aide.",
          options: [
            { english: "Yes, please. That would be helpful.", french: "Oui, s’il vous plaît. Ce serait utile.", feedback: "Tu acceptes le coup de main ; « helpful » signifie « utile ».", replyEnglish: "Follow the blue signs. The platform is on your left.", replyFrench: "Suis les panneaux bleus. Le quai est sur ta gauche." },
            { english: "Could you show me, please?", french: "Pourriez-vous me montrer, s’il vous plaît ?", feedback: "Tu demandes directement une indication, avec une formule polie.", replyEnglish: "Certainly. Follow the blue signs to platform two.", replyFrench: "Bien sûr. Suis les panneaux bleus jusqu’au quai numéro deux." },
            { english: "No, thanks. I can find it.", french: "Non merci. Je peux trouver.", feedback: "Tu peux aussi décliner et poursuivre par toi-même.", replyEnglish: "All right. The blue signs will guide you.", replyFrench: "D’accord. Les panneaux bleus te guideront." }
          ]
        },
        {
          speaker: "L’agent·e",
          english: "The train leaves in ten minutes. Is that all right?",
          french: "Le train part dans dix minutes. Cela te convient ?",
          objective: "Confirmer, remercier ou demander de répéter.",
          modelEnglish: "Yes, thank you. I’m ready.",
          modelFrench: "Oui, merci. Je suis prêt·e.",
          tip: "Faire répéter une information est une stratégie de communication normale, pas une erreur.",
          options: [
            { english: "Yes, thank you. I’m ready.", french: "Oui, merci. Je suis prêt·e.", feedback: "Tu confirmes et tu remercies : l’échange peut se terminer naturellement.", replyEnglish: "Have a lovely visit at the museum!", replyFrench: "Bonne visite au musée !" },
            { english: "Could you say that again, please?", french: "Pourriez-vous répéter, s’il vous plaît ?", feedback: "Tu demandes une répétition claire et polie.", replyEnglish: "The train leaves in ten minutes. You have plenty of time.", replyFrench: "Le train part dans dix minutes. Tu as largement le temps." },
            { english: "Where is platform two?", french: "Où se trouve le quai numéro deux ?", feedback: "Tu vérifies le lieu avant de partir ; c’est une bonne façon d’éviter un malentendu.", replyEnglish: "It’s on your left, beside the blue sign.", replyFrench: "Il est sur ta gauche, près du panneau bleu." }
          ]
        }
      ],
      keepsake: [
        { english: "Where would you like to go?", french: "Où aimerais-tu aller ?" },
        { english: "Could you show me, please?", french: "Pourriez-vous me montrer, s’il vous plaît ?" },
        { english: "Could you say that again, please?", french: "Pourriez-vous répéter, s’il vous plaît ?" }
      ]
    },
    {
      id: "cafe",
      title: "Le café des nuages",
      place: "La terrasse aux voiles corail",
      level: "A1",
      theme: "cafe",
      time: "5 à 8 min, à ton rythme",
      brief: "Après le voyage, tu fais une pause dans un petit café. Choisis une boisson, puis règle l’addition comme tu le souhaites.",
      outcome: "Commander, répondre à une proposition et poser une question simple sur le paiement.",
      sceneDescription: "Un café de bord de mer avec une terrasse, des tables rondes et une grande voile corail.",
      turns: [
        {
          speaker: "La personne au comptoir",
          english: "Good morning! What can I get you?",
          french: "Bonjour ! Que puis-je te servir ?",
          objective: "Commander une boisson avec une formule simple.",
          modelEnglish: "Could I have a tea, please?",
          modelFrench: "Pourrais-je avoir un thé, s’il vous plaît ?",
          tip: "« Could I have…? » est une formule courante pour commander poliment.",
          options: [
            { english: "Could I have a tea, please?", french: "Pourrais-je avoir un thé, s’il vous plaît ?", feedback: "Ta demande est polie et précise.", replyEnglish: "Of course. Would you like anything to eat?", replyFrench: "Bien sûr. Désires-tu quelque chose à manger ?" },
            { english: "A coffee, please.", french: "Un café, s’il vous plaît.", feedback: "Une phrase courte avec « please » fonctionne très bien dans ce contexte.", replyEnglish: "Sure. Would you like anything to eat?", replyFrench: "Bien sûr. Désires-tu quelque chose à manger ?" },
            { english: "May I have a hot chocolate, please?", french: "Puis-je avoir un chocolat chaud, s’il vous plaît ?", feedback: "Tu choisis une autre boisson et gardes la même intention polie.", replyEnglish: "Certainly. Would you like anything to eat?", replyFrench: "Bien sûr. Désires-tu quelque chose à manger ?" }
          ]
        },
        {
          speaker: "La personne au comptoir",
          english: "Would you like something to eat?",
          french: "Aimerais-tu manger quelque chose ?",
          objective: "Accepter, demander un conseil ou décliner.",
          modelEnglish: "No, thanks. Just a tea.",
          modelFrench: "Non merci. Juste un thé.",
          tip: "« No, thanks » permet de décliner poliment ; « just » signifie ici « seulement ».",
          options: [
            { english: "A sandwich, please.", french: "Un sandwich, s’il vous plaît.", feedback: "Tu ajoutes quelque chose à ta commande.", replyEnglish: "Good choice. I’ll add that to your order.", replyFrench: "Bon choix. Je l’ajoute à ta commande.", totalEnglish: "six pounds forty", totalFrench: "six livres quarante" },
            { english: "No, thanks. Just my drink.", french: "Non merci. Seulement ma boisson.", feedback: "Tu déclines simplement et précises que tu gardes seulement ta boisson.", replyEnglish: "No problem. I’ll get that for you.", replyFrench: "Pas de problème. Je te prépare cela.", totalEnglish: "three pounds twenty", totalFrench: "trois livres vingt" },
            { english: "What do you recommend?", french: "Que recommandez-vous ?", feedback: "Tu demandes conseil avant de choisir ; c’est une vraie stratégie d’échange.", replyEnglish: "The vegetable soup is popular. I’ll add that to your order.", replyFrench: "La soupe de légumes est appréciée. Je l’ajoute à ta commande.", totalEnglish: "six pounds forty", totalFrench: "six livres quarante" }
          ]
        },
        {
          speaker: "La personne au comptoir",
          english: "That’s {total}, please. How would you like to pay?",
          french: "Cela fait {total}. Comment voudrais-tu payer ?",
          objective: "Payer, vérifier si la carte est acceptée ou demander un reçu.",
          modelEnglish: "Can I pay by card?",
          modelFrench: "Puis-je payer par carte ?",
          tip: "Dans cet exemple fictif, le prix est en livres sterling ; les moyens de paiement varient selon les lieux.",
          options: [
            { english: "Here you are. Thank you.", french: "Tenez. Merci.", feedback: "Tu remets le paiement et tu conclus l’échange.", replyEnglish: "Thank you. Enjoy your drink!", replyFrench: "Merci. Profite bien de ta boisson !" },
            { english: "Can I pay by card?", french: "Puis-je payer par carte ?", feedback: "Tu poses une question pratique avant de payer.", replyEnglish: "Yes, of course. The card reader is here.", replyFrench: "Oui, bien sûr. Le terminal est ici." },
            { english: "Could I have a receipt, please?", french: "Pourrais-je avoir un reçu, s’il vous plaît ?", feedback: "Tu demandes un justificatif du paiement.", replyEnglish: "Of course. Here’s your receipt.", replyFrench: "Bien sûr. Voici ton reçu." }
          ]
        }
      ],
      keepsake: [
        { english: "Could I have a tea, please?", french: "Pourrais-je avoir un thé, s’il vous plaît ?" },
        { english: "No, thanks. Just a tea.", french: "Non merci. Juste un thé." },
        { english: "Can I pay by card?", french: "Puis-je payer par carte ?" }
      ]
    },
    {
      id: "marche",
      title: "Le marché aux couleurs",
      place: "Les étals du petit port",
      level: "A1 · A2",
      theme: "market",
      time: "6 à 9 min, à ton rythme",
      brief: "Tu prépares un pique-nique pour le lendemain. Compare les produits, précise une quantité et demande ce qu’il te faut.",
      outcome: "Poser une question, exprimer une quantité et confirmer un achat.",
      sceneDescription: "Un marché en plein air, avec des auvents turquoise, des caisses de fruits et un chemin pavé.",
      turns: [
        {
          speaker: "La marchande",
          english: "Hello! What are you looking for today?",
          french: "Bonjour ! Que cherches-tu aujourd’hui ?",
          objective: "Dire ce que tu cherches ou demander une précision sur les produits.",
          modelEnglish: "I’m looking for some apples.",
          modelFrench: "Je cherche des pommes.",
          tip: "« I’m looking for… » signifie « Je cherche… » et peut introduire un produit ou un lieu.",
          options: [
            { english: "I’m looking for some apples.", french: "Je cherche des pommes.", feedback: "Tu annonces directement le produit qui t’intéresse.", replyEnglish: "These apples are from the farm across the bay.", replyFrench: "Ces pommes viennent de la ferme de l’autre côté de la baie." },
            { english: "Do you have any green apples?", french: "Avez-vous des pommes vertes ?", feedback: "Tu précises la variété ou la couleur que tu cherches.", replyEnglish: "Yes, they’re right here beside the red ones.", replyFrench: "Oui, elles sont juste ici, à côté des rouges." },
            { english: "Are these apples local?", french: "Ces pommes sont-elles locales ?", feedback: "Tu poses une question utile avant de choisir.", replyEnglish: "Yes, they’re from the farm across the bay.", replyFrench: "Oui, elles viennent de la ferme de l’autre côté de la baie." }
          ]
        },
        {
          speaker: "La marchande",
          english: "How many would you like?",
          french: "Combien en voudrais-tu ?",
          objective: "Indiquer une quantité compréhensible.",
          modelEnglish: "Six apples, please.",
          modelFrench: "Six pommes, s’il vous plaît.",
          tip: "Pour parler d’objets que l’on compte : un nombre + le nom au pluriel, par exemple « six apples ».",
          options: [
            { english: "Six apples, please.", french: "Six pommes, s’il vous plaît.", feedback: "Le nombre et le produit sont tous les deux précisés.", replyEnglish: "Here you are. Anything else?", replyFrench: "Les voici. Autre chose ?" },
            { english: "Just two, thanks.", french: "Juste deux, merci.", feedback: "La quantité est claire dans ce contexte ; tu peux préciser le produit si nécessaire.", replyEnglish: "Two apples, then. Anything else?", replyFrench: "Deux pommes, alors. Autre chose ?" },
            { english: "Could I have half a kilo, please?", french: "Pourrais-je avoir un demi-kilo, s’il vous plaît ?", feedback: "Tu choisis une quantité exprimée en poids.", replyEnglish: "Of course. Anything else?", replyFrench: "Bien sûr. Autre chose ?" }
          ]
        },
        {
          speaker: "La marchande",
          english: "Would you like a bag?",
          french: "Veux-tu un sac ?",
          objective: "Répondre à la proposition ou demander le prix.",
          modelEnglish: "No, thank you. I have my own bag.",
          modelFrench: "Non merci. J’ai mon propre sac.",
          tip: "« I have my own… » signifie « J’ai mon propre… ».",
          options: [
            { english: "No, thank you. I have my own bag.", french: "Non merci. J’ai mon propre sac.", feedback: "Tu déclines la proposition et expliques brièvement pourquoi.", replyEnglish: "Perfect. That’s four pounds altogether.", replyFrench: "Parfait. Cela fait quatre livres en tout." },
            { english: "Yes, please. How much is it?", french: "Oui, s’il vous plaît. Combien cela coûte-t-il ?", feedback: "Tu acceptes et vérifies le prix du sac.", replyEnglish: "The bag is free today. That’s four pounds altogether.", replyFrench: "Le sac est gratuit aujourd’hui. Cela fait quatre livres en tout." },
            { english: "That’s all, thank you.", french: "C’est tout, merci.", feedback: "Tu indiques que tu as terminé tes achats.", replyEnglish: "Lovely. Have a good picnic!", replyFrench: "Très bien. Bon pique-nique !" }
          ]
        }
      ],
      keepsake: [
        { english: "I’m looking for some apples.", french: "Je cherche des pommes." },
        { english: "How many would you like?", french: "Combien en voudrais-tu ?" },
        { english: "How much is it?", french: "Combien cela coûte-t-il ?" }
      ]
    },
    {
      id: "atelier",
      title: "L’atelier du phare",
      place: "La boutique des vélos",
      level: "A2",
      theme: "workshop",
      time: "6 à 9 min, à ton rythme",
      brief: "Ton vélo fait un bruit inhabituel avant une promenade. Explique le problème et entends-toi sur la suite.",
      outcome: "Décrire un souci, préciser quand il a commencé et s’accorder sur une solution.",
      sceneDescription: "Un petit atelier de réparation près du phare, avec un établi, des outils et un vélo bleu.",
      turns: [
        {
          speaker: "Le mécanicien",
          english: "Hi! What seems to be the problem with your bike?",
          french: "Bonjour ! Quel semble être le problème avec ton vélo ?",
          objective: "Décrire un problème simple ou demander au mécanicien de regarder.",
          modelEnglish: "The chain keeps coming off.",
          modelFrench: "La chaîne continue de dérailler.",
          tip: "« Keeps coming off » décrit quelque chose qui se détache à répétition.",
          options: [
            { english: "The chain keeps coming off.", french: "La chaîne continue de dérailler.", feedback: "Tu décris le problème avec un détail concret.", replyEnglish: "I see. When did it start?", replyFrench: "Je vois. Quand cela a-t-il commencé ?" },
            { english: "The brakes don’t feel right.", french: "Les freins ne me semblent pas normaux.", feedback: "Tu signales un autre souci courant et compréhensible.", replyEnglish: "Thanks for telling me. When did you notice it?", replyFrench: "Merci de me le dire. Quand l’as-tu remarqué ?" },
            { english: "Could you take a look, please?", french: "Pourriez-vous regarder, s’il vous plaît ?", feedback: "Tu demandes une aide concrète même si tu ne connais pas le nom de la pièce.", replyEnglish: "Of course. When did you first notice the problem?", replyFrench: "Bien sûr. Quand as-tu remarqué le problème pour la première fois ?" }
          ]
        },
        {
          speaker: "Le mécanicien",
          english: "When did you first notice it?",
          french: "Quand l’as-tu remarqué pour la première fois ?",
          objective: "Situer le début du problème ou signaler que tu n’es pas certain·e.",
          modelEnglish: "I noticed it yesterday, on my way home.",
          modelFrench: "Je l’ai remarqué hier, en rentrant chez moi.",
          tip: "Pour situer un événement passé, « yesterday » et « this morning » donnent un repère temporel simple.",
          options: [
            { english: "I noticed it yesterday, on my way home.", french: "Je l’ai remarqué hier, en rentrant chez moi.", feedback: "Tu ajoutes un moment et un contexte pour aider la personne à comprendre.", replyEnglish: "That helps. I’ll check the chain and the gears.", replyFrench: "Cela m’aide. Je vais vérifier la chaîne et les vitesses." },
            { english: "It started this morning.", french: "Cela a commencé ce matin.", feedback: "Un repère de temps court peut déjà suffire.", replyEnglish: "All right. I’ll check it carefully.", replyFrench: "D’accord. Je vais vérifier cela attentivement." },
            { english: "I’m not sure, but it happens on hills.", french: "Je ne suis pas sûr·e, mais cela arrive dans les montées.", feedback: "Tu peux exprimer une incertitude et ajouter ce que tu as observé.", replyEnglish: "That’s useful to know. I’ll test it on the stand.", replyFrench: "C’est utile à savoir. Je vais le tester sur le support." }
          ]
        },
        {
          speaker: "Le mécanicien",
          english: "I can have it ready tomorrow afternoon. Does that work for you?",
          french: "Je peux le terminer demain après-midi. Est-ce que cela te convient ?",
          objective: "Confirmer le délai, demander un appel ou poser une question sur le coût.",
          modelEnglish: "That works for me. Could you call me when it’s ready?",
          modelFrench: "Cela me convient. Pourriez-vous m’appeler quand ce sera prêt ?",
          tip: "« That works for me » signifie « Cela me convient » ; « when it’s ready » veut dire « quand ce sera prêt ».",
          options: [
            { english: "That works for me. Thank you.", french: "Cela me convient. Merci.", feedback: "Tu confirmes le délai et conclus l’échange.", replyEnglish: "Great. See you tomorrow afternoon.", replyFrench: "Très bien. À demain après-midi." },
            { english: "Could you call me when it’s ready?", french: "Pourriez-vous m’appeler quand ce sera prêt ?", feedback: "Tu demandes comment être prévenu·e, sans avoir à revenir vérifier.", replyEnglish: "Of course. I’ll give you a call.", replyFrench: "Bien sûr. Je t’appellerai." },
            { english: "How much will it cost?", french: "Combien cela coûtera-t-il ?", feedback: "Tu vérifies le prix avant de donner ton accord.", replyEnglish: "I’ll call you with an estimate before I start.", replyFrench: "Je t’appellerai avec une estimation avant de commencer." }
          ]
        }
      ],
      keepsake: [
        { english: "What seems to be the problem?", french: "Quel semble être le problème ?" },
        { english: "I’m not sure, but…", french: "Je ne suis pas sûr·e, mais…" },
        { english: "That works for me.", french: "Cela me convient." }
      ]
    },
    {
      id: "club",
      title: "Le club des promenades",
      place: "Le rendez-vous près du phare",
      level: "B1 · conversation quotidienne",
      theme: "club",
      time: "7 à 10 min, à ton rythme",
      brief: "Tu rencontres une nouvelle personne du club. Parle de ton week-end, réponds à une invitation et trouve un horaire qui vous convient.",
      outcome: "Partager une expérience, relancer la conversation et négocier un petit changement de programme.",
      sceneDescription: "Un rendez-vous au bord de la mer, près d’un phare, avec une jetée et deux voyageurs qui discutent.",
      turns: [
        {
          speaker: "Alex, du club",
          english: "How was your weekend? Did you get out anywhere?",
          french: "Comment s’est passé ton week-end ? Es-tu allé·e quelque part ?",
          objective: "Raconter brièvement une activité ou dire que tu t’es reposé·e.",
          modelEnglish: "It was good. I went for a long walk along the coast.",
          modelFrench: "C’était bien. J’ai fait une longue promenade sur la côte.",
          tip: "« I went… » parle d’une activité passée ; « along the coast » signifie « le long de la côte ».",
          options: [
            { english: "It was good. I went for a long walk along the coast.", french: "C’était bien. J’ai fait une longue promenade sur la côte.", feedback: "Tu réponds à la question et ajoutes un détail qui peut relancer l’échange.", replyEnglish: "That sounds lovely. I’m thinking of going there next Saturday.", replyFrench: "Cela a l’air agréable. Je pense y aller samedi prochain." },
            { english: "I mostly relaxed, but I tried a new café.", french: "Je me suis surtout reposé·e, mais j’ai essayé un nouveau café.", feedback: "Tu partages une autre expérience ; « mostly » signifie « surtout ».", replyEnglish: "Oh, nice. I’m thinking of going to the coast next Saturday.", replyFrench: "Ah, sympa. Je pense aller sur la côte samedi prochain." },
            { english: "Not really. I had a quiet weekend at home.", french: "Pas vraiment. J’ai passé un week-end tranquille à la maison.", feedback: "Une réponse brève reste naturelle. Tu peux ajouter une question à ton tour.", replyEnglish: "That sounds relaxing. Would you like to join our walk next Saturday?", replyFrench: "Cela a l’air reposant. Veux-tu te joindre à notre promenade samedi prochain ?" }
          ]
        },
        {
          speaker: "Alex, du club",
          english: "Would you like to join our walk next Saturday?",
          french: "Veux-tu te joindre à notre promenade samedi prochain ?",
          objective: "Accepter, décliner avec tact ou demander un détail avant de décider.",
          modelEnglish: "I’d love to. Where are you meeting?",
          modelFrench: "Avec plaisir. Où avez-vous rendez-vous ?",
          tip: "« I’d love to » accepte chaleureusement ; une question complémentaire aide à organiser la suite.",
          options: [
            { english: "I’d love to. Where are you meeting?", french: "Avec plaisir. Où avez-vous rendez-vous ?", feedback: "Tu acceptes et demandes le lieu : la conversation avance.", replyEnglish: "At the lighthouse, around ten. Does that work for you?", replyFrench: "Au phare, vers dix heures. Cela te convient ?" },
            { english: "That sounds great. What time are you meeting?", french: "Cela a l’air super. À quelle heure avez-vous rendez-vous ?", feedback: "Tu montres ton intérêt et précises l’horaire.", replyEnglish: "At the lighthouse, around ten. Does that work for you?", replyFrench: "Au phare, vers dix heures. Cela te convient ?" },
            { english: "I think I can. Where exactly are you meeting?", french: "Je pense pouvoir venir. Où avez-vous rendez-vous exactement ?", feedback: "Tu montres ton intérêt et demandes une précision concrète.", replyEnglish: "At the lighthouse, around ten. Does that work for you?", replyFrench: "Au phare, vers dix heures. Cela te convient ?" }
          ]
        },
        {
          speaker: "Alex, du club",
          english: "At the lighthouse, around ten. Does that work for you?",
          french: "Au phare, vers dix heures. Cela te convient ?",
          objective: "Confirmer, proposer un autre horaire ou demander une précision.",
          modelEnglish: "Ten works for me. I’ll see you there!",
          modelFrench: "Dix heures me conviennent. On se retrouve là-bas !",
          tip: "« Around ten » indique une heure approximative ; tu peux proposer un autre moment si nécessaire.",
          options: [
            { english: "Ten works for me. I’ll see you there!", french: "Dix heures me conviennent. On se retrouve là-bas !", feedback: "Tu confirmes clairement le lieu et l’heure.", replyEnglish: "Brilliant. See you on Saturday!", replyFrench: "Parfait. À samedi !" },
            { english: "Could we meet a little later, maybe at eleven?", french: "Pourrions-nous nous retrouver un peu plus tard, vers onze heures ?", feedback: "Tu proposes un changement tout en laissant une marge de discussion.", replyEnglish: "Eleven works for me too. See you then!", replyFrench: "Onze heures me conviennent aussi. À tout à l’heure !" },
            { english: "Is that ten in the morning?", french: "C’est bien dix heures du matin ?", feedback: "Tu vérifies un détail important avant de confirmer.", replyEnglish: "Yes, ten in the morning. See you Saturday!", replyFrench: "Oui, dix heures du matin. À samedi !" }
          ]
        }
      ],
      keepsake: [
        { english: "How was your weekend?", french: "Comment s’est passé ton week-end ?" },
        { english: "I’d love to. Where are you meeting?", french: "Avec plaisir. Où avez-vous rendez-vous ?" },
        { english: "Could we meet a little later?", french: "Pourrions-nous nous retrouver un peu plus tard ?" }
      ]
    }
  ]
});
