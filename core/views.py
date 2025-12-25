"""Site pages for Dr Bronstein."""

from django.http import Http404, JsonResponse
from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.views.decorators.csrf import csrf_exempt
import json
import unicodedata
import difflib
from .forms import ContactForm
from .rag_utils import load_pdf_content


EXAMS = [
	{
		"slug": "gastroscopie",
		"title": "Gastroscopie",
		"image": "/static/img/exams/gastroscopie.jpg",
		"description": "Explorations oeso-gastriques et duodénales.",
		"indications": ["Brûlures, reflux, douleurs hautes", "Anémie, vomissements, suspicion d'ulcère"],
		"preparation": "Jeûne de 6h pour les solides et 2h pour les liquides clairs, selon consignes de l'anesthésie.",
		"procedure": "Examen endoscopique sous anesthésie ou sédation courte, durée environ 10 minutes.",
		"aftercare": "Repos court, reprise alimentaire légère après avis médical; ne pas conduire en cas de sédation.",
		"duration": "Environ 10 minutes (hors préparation et réveil).",
		"risks": [
			"Sédation : somnolence transitoire (ne pas conduire le jour même)",
			"Très rares complications : saignement, perforation (expliquées avant l'examen)",
		],
		"documents": [
			{"label": "Consignes fibroscopie (en ligne)", "url": "/guides/#deroulement-fibroscopie"},
		],
		"video": "https://monhepatogastro.net/wp-content/uploads/2022/04/Gastroscopie_Int.mp4",
	},
	{
		"slug": "coloscopie",
		"title": "Coloscopie",
		"image": "/static/img/exams/coloscopie.jpg",
		"description": "Prévention et diagnostic des maladies du côlon.",
		"indications": ["Dépistage colorectal", "Sang dans les selles, diarrhée chronique, douleurs abdominales"],
		"preparation": "Régime pauvre en résidus et laxatif la veille selon l'ordonnance.",
		"procedure": "Examen endoscopique sous anesthésie courte; polypes retirés si besoin.",
		"aftercare": "Surveillance courte, ballonnements possibles; signes d'alerte expliqués avant la sortie.",
		"duration": "Environ 20 à 30 minutes (hors préparation et réveil).",
		"risks": [
			"Ballonnements transitoires après l'examen",
			"Risque faible de saignement ou perforation (notamment si polype retiré)",
		],
		"documents": [
			{"label": "Préparation coloscopie (en ligne)", "url": "/guides/#preparation-coloscopie"},
		],
		"video": "https://monhepatogastro.net/wp-content/uploads/2022/04/Coloscopie.mp4",
	},
	{
		"slug": "echographie",
		"title": "Échographie",
		"image": "/static/img/exams/echographie.jpg",
		"description": "Échographie abdominale et pelvienne.",
		"indications": ["Bilan hépatique", "Douleurs abdominales", "Surveillance biliaire ou pancréatique"],
		"preparation": "À jeun selon l'organe exploré; consignes précisées lors du rendez-vous.",
		"procedure": "Examen indolore avec sonde sur l'abdomen, gel posé sur la peau.",
		"aftercare": "Reprise immédiate des activités; compte-rendu oral puis écrit.",
		"duration": "Environ 10 à 20 minutes selon l'organe exploré.",
		"risks": ["Aucun risque connu, examen non irradiant."],
		"documents": [],
	},
	{
		"slug": "hepatologie",
		"title": "Hépatologie",
		"image": "/static/img/exams/hepatologie.jpg",
		"description": "Suivi des maladies du foie et bilan hépatique.",
		"indications": ["Bilan enzymes hépatiques", "Foie gras non alcoolique", "Surveillance hépatite"],
		"preparation": "Bilan sanguin préalable selon prescription.",
		"procedure": "Consultation spécialisée, éventuel complément échographique ou fibroscan.",
		"aftercare": "Plan de suivi personnalisé (biologie, imagerie, hygiène de vie).",
		"duration": "Consultation de 20 minutes environ; examens complémentaires selon indication.",
		"risks": ["Aucun risque spécifique en consultation; risques propres aux examens complémentaires expliqués le cas échéant."],
		"documents": [],
	},
	{
		"slug": "echo-endoscopie",
		"title": "Echo-endoscopie",
		"image": "/static/img/exams/echo-endoscopie.jpg",
		"description": "Explorations écho-endoscopiques haute et basse.",
		"indications": ["Exploration biliaire/pancréatique", "Kystes, masses digestives"],
		"preparation": "Jeûne et préparation digestive selon indication.",
		"procedure": "Endoscope équipé d'une sonde d'échographie pour visualiser les organes de voisinage.",
		"aftercare": "Surveillance post-anesthésie; reprise progressive de l'alimentation.",
		"duration": "Variable selon le geste, souvent 20-40 minutes (hors réveil).",
		"risks": ["Risques liés à l'anesthésie", "Risque faible de saignement ou perforation selon le geste"],
		"documents": [],
	},
	{
		"slug": "catheterisme-biliaire",
		"title": "Cathétérisme biliaire",
		"image": "/static/img/exams/catheterisme-biliaire.jpg",
		"description": "Interventions endoscopiques de la voie biliaire.",
		"indications": ["Calculs biliaires", "Sténoses biliaires"],
		"preparation": "Jeûne strict; bilan sanguin de coagulation selon protocole.",
		"procedure": "Geste endoscopique (type CPRE) pour extraire calculs ou poser une prothèse.",
		"aftercare": "Surveillance hospitalière courte; consignes de reprise alimentaire.",
		"duration": "30 à 60 minutes selon complexité (hors surveillance).",
		"risks": ["Pancréatite post-CPRE (rare mais surveillée)", "Saignement ou infection (faible fréquence)"],
		"documents": [],
		"video": "https://monhepatogastro.net/wp-content/uploads/2022/04/CPRE.mp4",
	},
	{
		"slug": "maladies-anus",
		"title": "Maladies de l'anus",
		"image": "/static/img/exams/maladies-anus.jpg",
		"description": "Prise en charge proctologique.",
		"indications": ["Douleurs, saignements, fissure, hémorroïdes"],
		"preparation": "Souvent sans préparation; lavement possible selon l'examen.",
		"procedure": "Consultation et examen proctologique; gestes simples si indiqué.",
		"aftercare": "Hygiène locale, soins prescrits, surveillance des symptômes.",
		"duration": "Consultation de 15-20 minutes; gestes simples immédiatement réalisables.",
		"risks": ["Inconfort transitoire local", "Risques minimes pour les gestes simples (saignement local)"],
		"documents": [],
	},
	{
		"slug": "nutrition",
		"title": "Nutrition",
		"image": "/static/img/exams/nutrition.jpg",
		"description": "Conseils nutritionnels adaptés.",
		"indications": ["Surpoids, diabète, syndrome métabolique", "Troubles digestifs fonctionnels"],
		"preparation": "Carnet alimentaire ou bilan biologique utile selon le motif.",
		"procedure": "Consultation dédiée avec plan alimentaire personnalisé.",
		"aftercare": "Suivi régulier pour adapter les objectifs et surveiller les bilans.",
		"duration": "Consultation de 20-30 minutes.",
		"risks": ["Aucun risque spécifique"],
		"documents": [],
	},
	{
		"slug": "explorations-fonctionnelles",
		"title": "Explorations fonctionnelles",
		"image": "/static/img/exams/explorations-fonctionnelles.jpg",
		"description": "Bilans digestifs et fonctionnels.",
		"indications": ["Troubles du transit", "Suspicion de malabsorption", "pH-métrie, manométrie"],
		"preparation": "Consignes spécifiques selon l'examen (jeûne, arrêt de traitements).",
		"procedure": "Tests fonctionnels ciblés (pH-métrie, manométrie, tests respiratoires).",
		"aftercare": "Reprise normale sauf consigne contraire; résultats expliqués en consultation.",
		"duration": "Variable selon le test (15 à 60 minutes).",
		"risks": ["Gêne transitoire selon le test (sonde nasale, etc.)"],
		"documents": [],
	},
]


BLOG_POSTS = [
	{
		"slug": "choix-preparation-coloscopie",
		"title": "Pour une coloscopie, quel produit choisir ?",
		"date": "24 décembre 2025",
		"author": "Jean-Ariel Bronstein",
		"excerpt": "Comparatif des différentes préparations pour coloscopie : PEG, CitraFleet, Picoprep, Izinova... Lequel choisir ?",
		"content": """La coloscopie est un examen d’endoscopie digestive qui permet d’étudier la paroi interne du colon. Il s’agit actuellement du seul examen qui permet d’analyser, de façon fiable, l’aspect de la muqueuse afin de rechercher des atteintes inflammatoires (maladie de Crohn, rectocolite hémorragique, colite ischémique etc…). La coloscopie permet de réaliser des biopsies, l’ablation de polypes et de dépister le cancer du colon et du rectum.
La préparation est donc indispensable pour un examen de qualité. Le côlon doit être parfaitement propre, pour permettre un examen précis et réaliser les gestes thérapeutiques utiles. Mais il faut bien être objectif : la plupart de temps la préparation colique n’est pas agréable et favorise les « grimaces », même aux médecins les plus connus…

De nombreuses préparations coliques sont actuellement commercialisées en pharmacie. Nous allons vous présenter sur cette page une synthèse descriptive de ces préparations. Nous détaillerons à chaque fois les éléments suivants : Le nom commercial, le prix, le taux de remboursement, les substances actives (DCI), les excipients, les contre-indications, le principe de la préparation et notre avis pratique.

Les préparations à base de PEG :
Ces préparations sont constituées par du poly-éthylène-glycol ou PEG. Ils existent en pharmacie sous les noms commerciaux de COLOPEG®, FORTRANS®, KLEAN PREP® ou MOVIPREP®. Ce liquide n’est pas réabsorbé par l’intestin ou le côlon et est donc évacué avec les selles.

KLEAN PREP® :
Taux de remboursement : 65 %.
Substance active (DCI) : macrogol 3350 (59 g), sulfate de sodium anhydre (5,68 g), bicarbonate de sodium (1,68 g), chlorure de sodium (1,46 g), chlorure de potassium (0,74 g) + un sachet saveur Vanille.
Contre-indications particulières : phénylcétonurie (présence d’aspartam).

FORTRANS® :
Taux de remboursement : 65 %.
Substance active (DCI) : macrogol 4000 (64 g), sulfate de sodium anhydre (5.7 g), bicarbonate de sodium (1.68 g), chlorure de potassium (0.75g), chlorure de sodium (1.46 g).
Contre-indications particulières : Non

COLOPEG® :
Taux de remboursement : 65 %.
Substance active (DCI): macrogol 3350 (59 g), sulfate de sodium anhydre (5,68 g), bicarbonate de sodium (1,68 g), chlorure de sodium (1,46 g), chlorure de potassium (0,74 g).
Contre-indications particulières: Non

Pour ces trois produits très proches :
Principe de la préparation : Il faut prendre un sachet à reconstituer dans un litre d’eau en mélangeant bien. Il faut boire en tout 4 litres (4 sachets) soit en 1 fois dans la soirée précédant l’examen, soit en 2 fois, à raison de 2 litres la veille au soir et 2 litres le matin avant l’examen. Dans ce cas, la dernière prise devra avoir lieu au moins 3 heures avant l’examen. Le volume de 2 litres doit être pris en moins de 2 heures pour avoir l’efficacité escomptée.
Avis pratique : Le volume de la préparation reste important avec un goût peu agréable surtout pour le KLEAN PREP® qui a un goût de vanille très prononcé (sauf pour les « fous de vanille »). On peut éviter de mettre le sachet de vanille dans cette dernière et utiliser un liquide aromatique comme le « Pulco Citron ». L’efficacité n’est plus à démontrer pour ces produits mais la quantité à boire est importante.

MOVIPREP® :
Taux de remboursement : 65 %
Substance active (DCI) : Macrogol (polyéthylèneglycol) 3 350 (100 g), Sulfate de sodium anhydre (7,5 g) Chlorure de sodium (2,691 g), Chlorure de potassium (1,015 g), Acide ascorbique (4,7 g), Ascorbate de sodium (5,9 g) +Aspartam
Contre-indications particulières : déficit en G6PD, phénylcétonurie (présence d’aspartam).
Le principe de la préparation : La préparation consiste à boire deux litres de solution et de boire également, en plus, un litre de liquide clair incluant eau, soupe claire, jus de fruit sans pulpe, boisson non alcoolisée, thé et/ou café sans lait. On obtient un litre de Moviprep® en faisant dissoudre ensemble 1 sachet A et 1 sachet B dans un litre d’eau. Cette solution reconstituée doit être bue sur une période d’une à deux heures. Cette préparation peut être prise des façons suivantes : soit en deux fois avec un litre de Moviprep® ingéré la veille au soir de l’examen et un litre ingéré tôt dans la matinée le jour de l’examen, soit en une fois avec les deux litres de Moviprep® ingérés la veille au soir de l’examen.
Notre avis : Le médicament a l’avantage théorique de comporter seulement 2 litres de préparation + 1 litre d’eau ou de liquide clair. Le goût de la préparation n’est pas très agréable.

Les nouvelles préparations à base de laxatifs :
Elles sont constituées par l’association de picosulfate de sodium (laxatif stimulant) et de citrate de magnésium (laxatif osmotique) pour le PICOPREP® et CITRAFLEET® ou par du phosphate de sodium (laxatif osmotique) en solution pour le FLEET PHOSPHO SODA® et en comprimés pour le COLOKIT® ou une association de laxatifs osmotiques (sulfate de sodium, sulfate de magnésium et sulfate de potassium pour L’IZINOVA®

FLEET PHOSPHO SODA® :
Taux de remboursement : 65 %.
Substance active (DCI) : Hydrogénophosphate de sodium (10,8 g), Dihydrogénophosphate de sodium (24,4 g), Sodium (5 g)
Contre-indications particulières : insuffisance cardiaque grave et insuffisance rénale. Cette préparation est à éviter en cas de poussée inflammatoire évolutive du colon.
Principe de la préparation : Le contenu d’un flacon doit être dilué dans un demi-verre d’eau. La prise du médicament se fait la veille de l’examen. il faut prendre aux repas uniquement une boisson (eau, bouillon, jus de fruits sans pulpe, thé, café, sodas) et le contenu d’un flacon.
Notre avis : Le volume est identique mais avec le choix dans le type de liquides à prendre. Le flacon à un goût peu agréable qui peut-être difficile à prendre le matin avec des nausées. L’efficacité est lié à la quantité de liquide pris par le patient. Si l’on suit les indications il faut rester sans prise d’aliments solides la veille ce qui est assez gênant. Il existe des effets indésirables à prendre en considération et surtout l’apparition de lésions aphtoïdes pouvant gêner l’interprétation de l’examen.

COLOKIT® :
Taux de remboursement : 65 %.
Substance active (DCI) : Phosphate monosodique monohydraté (1102 mg), Phosphate disodique anhydre (398 mg) Pour un comprimé. Excipients : macrogol 8000, stéarate de magnésium. Teneur en sodium : 313 mg/cp
Contre-indications particulières : Hypersensibilité aux principes actifs ou à l’un des excipients, insuffisance cardiaque congestive, insuffisance rénale cliniquement significative, une hyperparathyroidie primitive associée à une hypercalcémie. Cette préparation est à éviter en cas de poussée inflammatoire évolutive du colon.
Principe de la préparation : Le soir précédent l’examen il faut prendre 4 comprimés avec 250 ml d’eau (ou un autre liquide clair), Puis recommencer 4 fois de suite dans les mêmes conditions en espaçant les prises de 15 minutes, soit au total 20 comprimés à avaler. Le jour de l’examen (en commençant 4 à 5 heures avant l’examen) il faut prendre 4 comprimés avec 250 ml d’eau (ou un autre liquide clair), puis recommencer 2 fois de suite dans les mêmes conditions en espaçant les prises de 15 minutes soit au total 12 comprimés à avaler.
Notre avis : Le médicament a l’avantage théorique de n’utiliser que le liquide que l’on prend pour avaler les comprimés. Il y a en tout 32 cp à prendre. Cela peut gêner certains patients mais être un avantage pour d’autres car il n’y a pas vraiment de préparations à avaler.

CITRAFLEET® :
Taux de remboursement : 65 %.
Substance active (DCI) : Picosulfate de sodium (10 mg), Oxyde de magnésium léger (3,5 g), Acide citrique anhydre (10,97 g). Excipients : bicarbonate de potassium, saccharine sodique, arôme citron (arôme citron, maltodextrine, tocophérol [E 307]).
Contre-indications particulières : Hypersensibilité aux principes actifs ou à l’un des excipients, insuffisance cardiaque congestive, insuffisance rénale cliniquement significative, déshydratation sévère, hypermagnésémie. Cette préparation est à éviter en cas de poussée inflammatoire évolutive du colon.
Principe de la préparation : Reconstituer le contenu d’un sachet dans une verre d’eau (environ 150 ml). La solution obtenue a un aspect trouble. Remuer pendant 2 à 3 minutes et boire la solution. Si elle est trop chaude, attendre qu’elle ait suffisamment refroidi pour la boire.
Le protocole le plus simple pour une préparation la veille est la suivante : Prendre un sachet reconstitué dans de l’eau avant 20h00. Boire au moins deux litres de liquides claires sur deux heures dès l’apparition de l’effet du produit la veille de l’examen. Prendre le deuxième sachet à 3h du matin en buvant bien deux litres de liquides claires sur deux heures. Il faut être jeun solide à partir de minuit et a jeun liquide à 5h du matin.
Notre avis : Le médicament a l’avantage d’être de bon goût et permet de n’utiliser que le liquide que l’on veut. Il faut en revanche bien boire au moins deux litres de boissons claires pour avoir une bonne efficacité.

PICOPREP® :
Taux de remboursement : 65 %.
Substance active (DCI) : Picosulfate de sodium (10 mg), Oxyde de magnésium (3,5 g), Acide citrique anhydre (12 g). Excipients : bicarbonate de potassium, saccharine sodique, orange arôme naturel (gomme arabique, lactose, acide ascorbique, butylhydroxyanisole).
Contre-indications particulières : Hypersensibilité aux principes actifs ou à l’un des excipients, insuffisance cardiaque congestive, insuffisance rénale cliniquement significative, déshydratation sévère, hypermagnésémie. Cette préparation est à éviter en cas de poussée inflammatoire évolutive du colon.
Principe de la préparation : Il faut reconstituer le contenu d’un sachet dans un verre d’eau (environ 150 ml). Remuez pendant 2-3 minutes, la solution obtenue doit être un liquide opaque blanc cassé avec une légère odeur d’orange. Si la solution est trop chaude, attendez qu’elle ait suffisamment refroidi pour la boire.
Le protocole le plus simple pour une préparation la veille est la suivante : Prendre un sachet reconstitué dans de l’eau avant 20h00. Boire au moins deux litres de liquides claires sur deux heures dès l’apparition de l’effet du produit la veille de l’examen. Prendre le deuxième sachet à 3h du matin en buvant bien deux litres de liquides claires sur deux heures. Il faut être jeun solide à partir de minuit et a jeun liquide à 5h du matin.
Notre avis : Le médicament a l’avantage d’être de bon goût et permet de n’utiliser que le liquide que l’on veut. Il faut en revanche bien boire au moins deux litres de boissons claires pour avoir une bonne efficacité.

IZINOVA® :
Taux de remboursement : 65 %.
Substance active (DCI) : Sulfate de sodium anhydre (17,510 g) Sulfate de magnésium heptahydraté (3,276 g) Sulfate de potassium (3,130 g). Excipients : Benzoate de sodium (E211), Acide citrique anhydre, Acide malique, Sucralose, Eau purifiée, Arôme cocktail de fruits.
Contre-indications particulières : Hypersensibilité aux principes actifs ou à l’un des excipients, insuffisance cardiaque congestive, insuffisance rénale sévère, déshydratation sévère, iléus, vomissements abondants, occlusion gastro-intestinale connue ou suspectée, perforation intestinale, troubles de la vidange gastrique (par exemple : gastroparésie). Cette préparation est à éviter en cas de poussée inflammatoire évolutive du colon
Principe de la préparation : Deux flacons sont nécessaires pour effectuer un lavage colique correct. Avant administration, le contenu de chaque flacon doit être dilué dans de l’eau, à l’aide du godet fourni, pour obtenir un volume total d’environ 0,5 litres. Pour chaque flacon, la prise doit être accompagnée, au cours des 2 heures suivantes, par l’ingestion supplémentaire de 1 litre d’eau ou de liquide clair. Si le délai avant l’intervention le permet, le schéma d’administration en prise fractionnée sur 2 jours doit être privilégié par rapport au schéma de prise sur une journée.
Schéma en prises fractionnés : Au début de la soirée précédant l’intervention (par exemple vers 18 h), le contenu d’un flacon d’IZINOVA doit être versé dans le godet fourni dans la boite et doit être dilué avec de l’eau jusqu’à la ligne de remplissage (environ 0,5 litre) et être bu. Par la suite il faut boire au cours des deux heures suivantes, deux godets supplémentaires, remplis jusqu’à la ligne de remplissage avec de l’eau ou un liquide clair (soit environ 1 litre).
Le matin de l’intervention (10 à 12 heures après la dose du soir), la prise d’un flacon comme décrit précédemment doit être répétée.
Les liquides clairs autorisés sont : l’eau, le thé ou le café (pas de lait ou de crème), les sodas gazeux ou non, les jus de fruit sans pulpe (sauf ceux de couleur rouge ou violette), le bouillon ou la soupe moulinée pour éliminer les morceaux solides.
Notre avis : Le médicament a montré sa supériorité par rapport à PICOPREP selon un schéma fractionné. Il a l’avantage d’être de bon goût et permet de n’utiliser que les liquides que l’on veut. La dose totale de liquide ingérée est plus faible par rapport aux autres préparations.""",
		"image": "/static/img/exams/coloscopie.jpg",
		"video": "https://monhepatogastro.net/wp-content/uploads/2022/04/Coloscopie.mp4",
	},
	{
		"slug": "fibres-et-microbiote",
		"title": "Fibres et microbiote : pourquoi en manger ?",
		"date": "15 décembre 2025",
		"author": "Jean-Ariel Bronstein",
		"excerpt": "Les fibres nourrissent votre microbiote et régulent le transit. Comment les intégrer progressivement ?",
		"content": "Les fibres solubles et insolubles soutiennent la flore, limitent le pic glycémique et régulent le transit. Augmentez-les progressivement, buvez suffisamment, et consultez si douleurs ou ballonnements persistants.",
		"image": "/static/img/pathologies/constipation.jpg",
	},
	{
		"slug": "diarrhee-chronique",
		"title": "Diarrhée chronique : quand consulter ?",
		"date": "30 novembre 2025",
		"author": "Jean-Ariel Bronstein",
		"excerpt": "Plus de 3 semaines de diarrhée : signes d'alerte, bilans et examens utiles.",
		"content": "Une diarrhée qui dure nécessite un avis médical. Signes d'alerte : fièvre, sang dans les selles, amaigrissement, douleurs abdominales. Bilan sanguin, coproculture, calprotectine ou coloscopie peuvent être proposés selon le contexte.",
		"image": "/static/img/pathologies/diarrhee-chronique.jpg",
	},
	{
		"slug": "reflux-enceinte",
		"title": "Reflux chez la femme enceinte : gestes simples",
		"date": "12 novembre 2025",
		"author": "Jean-Ariel Bronstein",
		"excerpt": "Adapter les repas, surélever la tête du lit, traitements compatibles : les bons réflexes.",
		"content": "Fractionnez les repas, évitez les aliments acides, café, épices fortes. Surélevez la tête du lit et attendez 2-3h avant de vous allonger. Un traitement peut être proposé si les mesures hygiéno-diététiques ne suffisent pas.",
		"image": "/static/img/pathologies/reflux-enceinte.jpg",
	},
	{
		"slug": "foie-gras",
		"title": "Foie gras non alcoolique : prévenir et suivre",
		"date": "20 octobre 2025",
		"author": "Jean-Ariel Bronstein",
		"excerpt": "Alimentation, activité physique et suivi biologique pour limiter la progression.",
		"content": "Le foie gras non alcoolique repose sur une alimentation équilibrée, une perte de poids progressive, l'activité physique et le suivi des enzymes hépatiques. Consultez pour adapter les examens (fibroscan, échographie).",
		"image": "/static/img/pathologies/foie-gras.jpg",
	},
	{
		"slug": "hydratation-digestion",
		"title": "L'eau, alliée de votre digestion",
		"date": "10 octobre 2025",
		"author": "Jean-Ariel Bronstein",
		"excerpt": "Boire suffisamment d'eau facilite le transit et l'absorption des nutriments. Visez 1,5L par jour.",
		"content": "L'eau aide à dissoudre les graisses et les fibres solubles, permettant un passage plus facile des selles. En cas de constipation, les eaux riches en magnésium peuvent aider.",
		"image": "/static/img/pathologies/constipation.jpg",
	},
	{
		"slug": "manger-lentement",
		"title": "Pourquoi faut-il manger lentement ?",
		"date": "05 octobre 2025",
		"author": "Jean-Ariel Bronstein",
		"excerpt": "La digestion commence dans la bouche. Mâcher réduit le travail de l'estomac et les ballonnements.",
		"content": "Prenez le temps de mastiquer. Cela permet de mieux imprégner les aliments de salive (enzymes), d'envoyer des signaux de satiété au cerveau et d'éviter d'avaler de l'air (aérophagie).",
		"image": "/static/img/pathologies/dyspepsie.jpg",
	},
	{
		"slug": "probiotiques-naturels",
		"title": "Les meilleures sources de probiotiques",
		"date": "28 septembre 2025",
		"author": "Jean-Ariel Bronstein",
		"excerpt": "Yaourts, choucroute, kéfir : ces aliments fermentés enrichissent votre flore intestinale.",
		"content": "Les probiotiques sont des bactéries vivantes bénéfiques. Intégrez régulièrement des aliments fermentés comme le yaourt, le kéfir, la choucroute ou le miso pour diversifier votre microbiote.",
		"image": "/static/img/pathologies/sibo.jpg",
	},
	{
		"slug": "aliments-ultra-transformes",
		"title": "Évitez les aliments ultra-transformés",
		"date": "20 septembre 2025",
		"author": "Jean-Ariel Bronstein",
		"excerpt": "Additifs, sucres cachés et mauvaises graisses perturbent l'équilibre digestif.",
		"content": "Ces aliments contiennent souvent des émulsifiants et des conservateurs qui peuvent altérer la barrière intestinale et favoriser l'inflammation. Privilégiez les produits bruts et cuisinez maison.",
		"image": "/static/img/pathologies/gastrite.jpg",
	},
	{
		"slug": "sommeil-microbiote",
		"title": "Le sommeil influence votre ventre",
		"date": "15 septembre 2025",
		"author": "Jean-Ariel Bronstein",
		"excerpt": "Un manque de sommeil peut perturber le microbiote et augmenter les envies de sucre.",
		"content": "Le rythme circadien régule aussi la digestion. Un sommeil irrégulier ou insuffisant peut modifier la composition de la flore intestinale et favoriser la prise de poids ou les troubles fonctionnels.",
		"image": "/static/img/pathologies/syndrome-intestin-irritable.jpg",
	},
	{
		"slug": "stress-ventre",
		"title": "Le stress et vos intestins",
		"date": "10 septembre 2025",
		"author": "Jean-Ariel Bronstein",
		"excerpt": "Le cerveau et le ventre sont connectés. Le stress peut déclencher douleurs et troubles du transit.",
		"content": "L'axe intestin-cerveau est bidirectionnel. Le stress chronique peut accélérer ou ralentir le transit et augmenter la sensibilité viscérale. La relaxation, le yoga ou la sophrologie peuvent aider.",
		"image": "/static/img/pathologies/syndrome-intestin-irritable.jpg",
	},
	{
		"slug": "gingembre-digestion",
		"title": "Le gingembre contre les nausées",
		"date": "05 septembre 2025",
		"author": "Jean-Ariel Bronstein",
		"excerpt": "Une racine reconnue pour apaiser l'estomac et stimuler la digestion.",
		"content": "Le gingembre est efficace contre les nausées (grossesse, mal des transports) et aide à la vidange gastrique. Consommez-le frais, en infusion ou râpé dans vos plats.",
		"image": "/static/img/pathologies/dyspepsie.jpg",
	},
	{
		"slug": "activite-physique",
		"title": "Bouger pour mieux digérer",
		"date": "01 septembre 2025",
		"author": "Jean-Ariel Bronstein",
		"excerpt": "La marche et le sport stimulent la motricité de l'intestin et réduisent la constipation.",
		"content": "L'activité physique régulière renforce la sangle abdominale et masse naturellement les intestins, favorisant un transit régulier. Évitez cependant le sport intense juste après un repas copieux.",
		"image": "/static/img/pathologies/constipation.jpg",
	},
	{
		"slug": "sel-sante",
		"title": "Réduire le sel pour votre santé",
		"date": "25 août 2025",
		"author": "Jean-Ariel Bronstein",
		"excerpt": "L'excès de sel favorise l'hypertension et peut irriter la muqueuse gastrique.",
		"content": "Une consommation excessive de sel est un facteur de risque pour l'estomac et le système cardiovasculaire. Utilisez des herbes, des épices et des aromates pour donner du goût sans saler.",
		"image": "/static/img/pathologies/ascite.jpg",
	},
	{
		"slug": "fodmaps-intro",
		"title": "Comprendre les FODMAPs",
		"date": "20 août 2025",
		"author": "Jean-Ariel Bronstein",
		"excerpt": "Ces sucres fermentescibles peuvent causer ballonnements et douleurs chez les personnes sensibles.",
		"content": "FODMAPs signifie Fermentable Oligo-, Di-, Mono-saccharides And Polyols. En cas de syndrome de l'intestin irritable, un régime pauvre en FODMAPs (sous suivi diététique) peut soulager les symptômes.",
		"image": "/static/img/pathologies/syndrome-intestin-irritable.jpg",
	},
	{
		"slug": "alcool-foie",
		"title": "L'alcool et votre foie",
		"date": "15 août 2025",
		"author": "Jean-Ariel Bronstein",
		"excerpt": "Même une consommation modérée peut impacter le foie. Des jours sans alcool sont essentiels.",
		"content": "Le foie métabolise l'alcool mais cela produit des substances toxiques. Pour préserver votre foie, respectez les recommandations (max 2 verres/jour, pas tous les jours) et faites des pauses.",
		"image": "/static/img/pathologies/cirrhose.jpg",
	},
	{
		"slug": "tabac-estomac",
		"title": "Le tabac et l'estomac",
		"date": "10 août 2025",
		"author": "Jean-Ariel Bronstein",
		"excerpt": "Fumer augmente le risque de reflux, d'ulcères et de cancers digestifs.",
		"content": "Le tabac affaiblit le sphincter œsophagien (reflux), diminue la production de mucus protecteur dans l'estomac et retarde la cicatrisation des ulcères. L'arrêt est toujours bénéfique.",
		"image": "/static/img/pathologies/ulcere-gastrique.jpg",
	},
	{
		"slug": "fibres-types",
		"title": "Fibres solubles vs insolubles",
		"date": "05 août 2025",
		"author": "Jean-Ariel Bronstein",
		"excerpt": "Connaître la différence pour adapter son alimentation selon son transit.",
		"content": "Les fibres solubles (avoine, fruits, légumineuses) forment un gel doux, bon pour la diarrhée et le cholestérol. Les insolubles (blé complet, son) accélèrent le transit mais peuvent irriter les intestins sensibles.",
		"image": "/static/img/pathologies/diverticulose.jpg",
	},
	{
		"slug": "repas-soir",
		"title": "Dîner léger pour mieux dormir",
		"date": "01 août 2025",
		"author": "Jean-Ariel Bronstein",
		"excerpt": "Un repas trop riche le soir peut perturber le sommeil et favoriser le reflux.",
		"content": "La digestion demande de l'énergie et augmente la température corporelle. Manger gras ou copieux tardivement retarde l'endormissement et favorise les remontées acides nocturnes.",
		"image": "/static/img/pathologies/brulure-estomac.jpg",
	},
	{
		"slug": "cafe-digestion",
		"title": "Le café : ami ou ennemi ?",
		"date": "25 juillet 2025",
		"author": "Jean-Ariel Bronstein",
		"excerpt": "Il stimule le transit mais peut irriter l'estomac et favoriser le reflux.",
		"content": "La caféine stimule la motricité colique (effet laxatif) mais aussi la sécrétion acide de l'estomac. À limiter en cas de brûlures d'estomac ou de diarrhée.",
		"image": "/static/img/pathologies/brulure-estomac.jpg",
	},
	{
		"slug": "legumineuses-digestion",
		"title": "Mieux digérer les légumineuses",
		"date": "20 juillet 2025",
		"author": "Jean-Ariel Bronstein",
		"excerpt": "Trempage et cuisson adaptée pour profiter de leurs bienfaits sans les gaz.",
		"content": "Lentilles, pois chiches et haricots sont excellents pour la santé. Pour limiter les flatulences, faites-les tremper longtemps, rincez-les bien et cuisez-les avec du bicarbonate ou de la sarriette.",
		"image": "/static/img/pathologies/sibo.jpg",
	},
	{
		"slug": "intolerance-lactose",
		"title": "Intolérance au lactose : que faire ?",
		"date": "15 juillet 2025",
		"author": "Jean-Ariel Bronstein",
		"excerpt": "Pas besoin de tout supprimer. Les fromages affinés et les yaourts sont souvent tolérés.",
		"content": "L'intolérance est due au manque de lactase. Testez votre tolérance : souvent, de petites quantités ou des produits laitiers fermentés (yaourts, fromages durs) passent très bien.",
		"image": "/static/img/pathologies/syndrome-intestin-irritable.jpg",
	},
	{
		"slug": "gluten-verite",
		"title": "Le gluten : faut-il l'arrêter ?",
		"date": "10 juillet 2025",
		"author": "Jean-Ariel Bronstein",
		"excerpt": "Inutile de l'exclure sans diagnostic de maladie cœliaque ou de sensibilité avérée.",
		"content": "Le régime sans gluten est contraignant et peut être carencé. Si vous suspectez un problème, consultez pour un dépistage de la maladie cœliaque avant d'arrêter le gluten.",
		"image": "/static/img/pathologies/maladie-coeliaque.jpg",
	},
	{
		"slug": "couleurs-assiette",
		"title": "Mettez de la couleur dans l'assiette",
		"date": "05 juillet 2025",
		"author": "Jean-Ariel Bronstein",
		"excerpt": "La variété des végétaux garantit un apport diversifié en antioxydants et vitamines.",
		"content": "Chaque couleur de fruit ou légume correspond souvent à des nutriments spécifiques (lycopène rouge, bêta-carotène orange...). Varier les couleurs protège votre système digestif et votre santé globale.",
		"image": "/static/img/exams/nutrition.jpg",
	},
	{
		"slug": "ecouter-faim",
		"title": "Écouter sa faim et sa satiété",
		"date": "01 juillet 2025",
		"author": "Jean-Ariel Bronstein",
		"excerpt": "Manger selon ses besoins évite la surcharge pondérale et digestive.",
		"content": "Apprenez à reconnaître la vraie faim (creux à l'estomac) de l'envie de manger (émotionnelle). Arrêtez-vous quand vous n'avez plus faim pour ne pas surcharger votre estomac.",
		"image": "/static/img/pathologies/dyspepsie.jpg",
	},
]


PATHOLOGIES = [
	{
		"slug": "gastro-enterite",
		"title": "Gastro-entérite",
		"image": "/static/img/pathologies/gastro-enterite.jpg",
		"summary": "Nausées, vomissements, diarrhée : comment se réhydrater et surveiller ?",
		"symptoms": ["Nausées, vomissements", "Diarrhée aiguë", "Crampes abdominales"],
		"emergency": "Consultez en urgence si fièvre élevée, sang dans les selles, signes de déshydratation ou douleurs importantes.",
		"exams": ["Bilan sanguin si fièvre ou terrain fragile", "Coproculture selon contexte"],
		"treatments": ["Réhydratation orale fractionnée", "Régime pauvre en fibres et gras", "Antalgiques adaptés"],
		"advice": ["Boire en petites quantités régulières", "Surveiller la fièvre", "Consulter si symptômes > 48h"],
		"prevention": ["Hygiène des mains", "Cuisson suffisante des aliments"],
		"tags": ["diarrhee", "vomissements", "fièvre"],
	},
	{
		"slug": "brulure-estomac",
		"title": "Brûlures d'estomac / reflux",
		"image": "/static/img/pathologies/brulure-estomac.jpg",
		"summary": "Sensation de brûlure rétro-sternale, remontées acides, gêne après les repas.",
		"symptoms": ["Brûlures rétro-sternales", "Remontées acides", "Toux nocturne", "Gêne en position allongée"],
		"emergency": "Consultez rapidement si douleurs thoraciques atypiques, dysphagie, amaigrissement, anémie.",
		"exams": ["Gastroscopie si signes d'alarme", "pH-métrie selon indications"],
		"treatments": ["Mesures hygiéno-diététiques", "Inhibiteurs de pompe à protons si besoin"],
		"advice": ["Surélever la tête du lit", "Éviter repas copieux et tardifs", "Limiter alcool, café, tabac"],
		"prevention": ["Poids stable", "Repas fractionnés"],
		"tags": ["brulure", "reflux", "nausées"],
	},
	{
		"slug": "gastrite",
		"title": "Gastrite",
		"image": "/static/img/pathologies/gastrite.jpg",
		"summary": "Inflammation de la muqueuse de l'estomac : douleurs, brûlures, inconfort post-prandial.",
		"symptoms": ["Douleurs épigastriques", "Brûlures", "Nausées"],
		"emergency": "Consultez si vomissements sanglants, méléna, anémie ou perte de poids.",
		"exams": ["Gastroscopie si symptômes persistants", "Recherche H. pylori"],
		"treatments": ["Traitement de l'acidité", "Éradication H. pylori si présent"],
		"advice": ["Éviter AINS/aspirine sans avis", "Limiter alcool et tabac"],
		"prevention": ["Prudence AINS", "Repas légers"],
		"tags": ["douleur estomac", "nausées"],
	},
	{
		"slug": "cancer-estomac",
		"title": "Cancer de l'estomac",
		"image": "/static/img/pathologies/cancer-estomac.jpg",
		"summary": "Signes d'alerte et examens de diagnostic.",
		"symptoms": ["Douleurs hautes", "Perte de poids", "Anémie", "Difficultés à avaler"],
		"emergency": "Consultez rapidement pour amaigrissement, vomissements sanglants, méléna.",
		"exams": ["Gastroscopie avec biopsies", "Scanner/IRM selon bilan"],
		"treatments": ["Prise en charge multidisciplinaire", "Chirurgie, endoscopie, oncologie"],
		"advice": ["Arrêt tabac", "Suivi régulier"],
		"prevention": ["Surveillance si facteurs de risque"],
		"tags": ["amaigrissement", "douleur estomac"],
	},
	{
		"slug": "diarrhee-chronique",
		"title": "Diarrhée chronique",
		"image": "/static/img/pathologies/diarrhee-chronique.jpg",
		"summary": "Plus de 3 semaines de diarrhée : bilan adapté, signes d'alerte.",
		"symptoms": ["Selles liquides > 3 semaines", "Ballonnements", "Crampes"],
		"emergency": "Consultez si sang dans les selles, fièvre, amaigrissement, douleurs importantes.",
		"exams": ["Bilan sanguin", "Coproculture", "Coloscopie selon contexte"],
		"treatments": ["Réhydratation", "Adaptation alimentaire", "Traitement étiologique"],
		"advice": ["Surveiller les signes de déshydratation", "Noter le lien avec aliments/medicaments"],
		"prevention": ["Hygiène alimentaire", "Suivi médical"],
		"tags": ["diarrhee", "fièvre", "sang selles"],
	},
	{
		"slug": "reflux-enceinte",
		"title": "Reflux de la femme enceinte",
		"image": "/static/img/pathologies/reflux-enceinte.jpg",
		"summary": "Adapter l'alimentation et la position pour limiter les reflux pendant la grossesse.",
		"symptoms": ["Brûlures", "Regurgitations", "Gêne nocturne"],
		"emergency": "Consultez si douleurs thoraciques atypiques ou perte de poids.",
		"exams": ["Examens limités pendant la grossesse; avis médical"],
		"treatments": ["Mesures hygiéno-diététiques", "Traitement compatible grossesse si besoin"],
		"advice": ["Petits repas fréquents", "Surélever la tête du lit", "Éviter allongement post-repas"],
		"prevention": ["Alimentation fractionnée"],
		"tags": ["reflux", "grossesse"],
	},
	{
		"slug": "foie-gras",
		"title": "Foie gras non alcoolique",
		"image": "/static/img/pathologies/foie-gras.jpg",
		"summary": "Prévention de la progression vers la fibrose : mode de vie et suivi.",
		"symptoms": ["Souvent asymptomatique", "Fatigue", "Inconfort abdominal"],
		"emergency": "Consultez si douleurs importantes, ictère ou bilan hépatique très perturbé.",
		"exams": ["Bilan hépatique", "Échographie", "Fibroscan selon indications"],
		"treatments": ["Perte de poids progressive", "Activité physique", "Suivi médical"],
		"advice": ["Alimentation équilibrée", "Limiter sucres et alcool"],
		"prevention": ["Activité physique régulière", "Suivi biologique"],
		"tags": ["foie", "bilan hepatique"],
	},
	{
		"slug": "lithiase-biliaire",
		"title": "Calculs biliaires",
		"image": "/static/img/pathologies/lithiase-biliaire.jpg",
		"summary": "Présence de calculs dans la vésicule : colique hépatique et complications.",
		"symptoms": ["Douleur brutale sous les côtes à droite", "Irradiation vers l'épaule ou le dos", "Nausées ou vomissements"],
		"emergency": "Consultez en urgence si fièvre, frissons, jaunisse ou douleur persistante > 6h.",
		"exams": ["Échographie abdominale", "Bilan hépatique"],
		"treatments": ["Antalgiques et antispasmodiques", "Chirurgie (cholécystectomie) si symptomatique"],
		"advice": ["Éviter les repas très gras", "Consulter si récidive"],
		"prevention": ["Alimentation équilibrée", "Éviter le jeûne prolongé"],
		"tags": ["douleur abdominale", "vésicule", "colique"],
	},
	{
		"slug": "maladie-crohn",
		"title": "Maladie de Crohn",
		"image": "/static/img/pathologies/maladie-crohn.jpg",
		"summary": "Maladie inflammatoire chronique pouvant toucher tout le tube digestif.",
		"symptoms": ["Douleurs abdominales", "Diarrhée chronique", "Perte de poids", "Fatigue"],
		"emergency": "Consultez si douleurs intenses, fièvre, arrêt du transit ou sang abondant.",
		"exams": ["Coloscopie avec biopsies", "Entéro-IRM", "Bilan sanguin (CRP)"],
		"treatments": ["Anti-inflammatoires", "Immunosuppresseurs", "Biothérapies"],
		"advice": ["Arrêt strict du tabac", "Suivi régulier même en rémission"],
		"prevention": ["Arrêt du tabac"],
		"tags": ["diarrhee", "douleur abdominale", "MICI"],
	},
	{
		"slug": "rch",
		"title": "Rectocolite hémorragique (RCH)",
		"image": "/static/img/pathologies/rch.jpg",
		"summary": "Inflammation chronique du rectum et du côlon.",
		"symptoms": ["Diarrhée sanglante", "Faux besoins", "Douleurs rectales"],
		"emergency": "Consultez si fièvre, selles très fréquentes (>6/j) ou saignements importants.",
		"exams": ["Rectosigmoïdoscopie ou coloscopie", "Calprotectine fécale"],
		"treatments": ["5-ASA (suppositoires/comprimés)", "Corticoïdes", "Biothérapies"],
		"advice": ["Suivre le traitement d'entretien", "Surveiller les selles"],
		"prevention": ["Suivi médical régulier"],
		"tags": ["sang selles", "diarrhee", "MICI"],
	},
	{
		"slug": "syndrome-intestin-irritable",
		"title": "Syndrome de l'intestin irritable",
		"image": "/static/img/pathologies/syndrome-intestin-irritable.jpg",
		"summary": "Trouble fonctionnel fréquent associant douleurs et troubles du transit.",
		"symptoms": ["Ballonnements", "Douleurs soulagées par les selles", "Alternance diarrhée/constipation"],
		"emergency": "Pas d'urgence vitale, mais consultez si symptômes nouveaux après 50 ans.",
		"exams": ["Bilan sanguin pour éliminer autre cause", "Coloscopie si signes d'alarme"],
		"treatments": ["Antispasmodiques", "Régime pauvre en FODMAPs", "Probiotiques"],
		"advice": ["Identifier les aliments déclencheurs", "Gestion du stress"],
		"prevention": ["Alimentation équilibrée", "Activité physique"],
		"tags": ["douleur abdominale", "ballonnements", "constipation"],
	},
	{
		"slug": "ulcere-gastrique",
		"title": "Ulcère gastrique",
		"image": "/static/img/pathologies/ulcere-gastrique.jpg",
		"summary": "Plaie profonde dans la paroi de l'estomac.",
		"symptoms": ["Douleur type crampe à l'estomac", "Calmée ou aggravée par les repas"],
		"emergency": "Consultez en urgence si vomissements de sang ou selles noires.",
		"exams": ["Gastroscopie (indispensable)", "Biopsies"],
		"treatments": ["IPP (Inhibiteurs de la pompe à protons)", "Éradication H. pylori"],
		"advice": ["Arrêt tabac et alcool", "Éviter l'automédication par anti-inflammatoires"],
		"prevention": ["Prudence avec les AINS"],
		"tags": ["douleur estomac", "ulcere"],
	},
	{
		"slug": "pancreatite-aigue",
		"title": "Pancréatite aiguë",
		"image": "/static/img/pathologies/pancreatite-aigue.jpg",
		"summary": "Inflammation brutale du pancréas, souvent liée à un calcul ou à l'alcool.",
		"symptoms": ["Douleur violente en barre au creux de l'estomac", "Irradiation dans le dos", "Vomissements"],
		"emergency": "Urgence médicale : hospitalisation nécessaire.",
		"exams": ["Prise de sang (Lipase)", "Scanner abdominal"],
		"treatments": ["Jeûne", "Perfusion", "Antalgiques puissants"],
		"advice": ["Arrêt alcool", "Traitement des calculs biliaires ensuite"],
		"prevention": ["Modération alcool", "Surveillance lithiase"],
		"tags": ["douleur abdominale", "pancreas", "urgence"],
	},
	{
		"slug": "cirrhose",
		"title": "Cirrhose du foie",
		"image": "/static/img/pathologies/cirrhose.jpg",
		"summary": "Stade avancé de fibrose hépatique, irréversible mais stabilisable.",
		"symptoms": ["Souvent asymptomatique au début", "Puis fatigue, jaunisse, ascite"],
		"emergency": "Consultez si vomissements de sang, confusion ou fièvre.",
		"exams": ["Bilan hépatique", "Échographie", "Fibroscan"],
		"treatments": ["Traitement de la cause (alcool, virus)", "Surveillance complications"],
		"advice": ["Arrêt total alcool", "Vaccination hépatites"],
		"prevention": ["Dépistage hépatites", "Lutte contre l'alcoolisme"],
		"tags": ["foie", "jaunisse", "fatigue"],
	},
	{
		"slug": "hepatite-b",
		"title": "Hépatite B",
		"image": "/static/img/pathologies/hepatite-b.jpg",
		"summary": "Infection virale du foie, transmissible par le sang et les rapports sexuels.",
		"symptoms": ["Souvent silencieuse", "Parfois fatigue, nausées, jaunisse"],
		"emergency": "Consultez pour dépistage ou suivi.",
		"exams": ["Sérologie virale", "Bilan hépatique"],
		"treatments": ["Antiviraux si nécessaire", "Vaccination de l'entourage"],
		"advice": ["Protection rapports sexuels", "Ne pas partager rasoirs/brosses à dents"],
		"prevention": ["Vaccination (très efficace)"],
		"tags": ["foie", "virus", "MST"],
	},
	{
		"slug": "hepatite-c",
		"title": "Hépatite C",
		"date": "10 août 2025",
		"author": "Jean-Ariel Bronstein",
		"excerpt": "Infection virale du foie, transmissible par le sang, guérissable aujourd'hui.",
		"content": "Infection virale du foie, transmissible par le sang, guérissable aujourd'hui.",
		"image": "/static/img/pathologies/hepatite-c.jpg",
		"summary": "Infection virale du foie, transmissible par le sang, guérissable aujourd'hui.",
		"symptoms": ["Asymptomatique le plus souvent", "Fatigue chronique"],
		"emergency": "Pas d'urgence, mais nécessite un traitement pour éviter la cirrhose.",
		"exams": ["Sérologie VHC", "PCR virale"],
		"treatments": ["Antiviraux directs (guérison > 95%)"],
		"advice": ["Dépistage si facteurs de risque (transfusion avant 1992, toxicomanie)"],
		"prevention": ["Matériel à usage unique"],
		"tags": ["foie", "virus"],
	},
	{
		"slug": "hemochromatose",
		"title": "Hémochromatose",
		"image": "/static/img/pathologies/hemochromatose.jpg",
		"summary": "Maladie génétique entraînant une surcharge en fer dans l'organisme.",
		"symptoms": ["Fatigue", "Douleurs articulaires", "Teint grisâtre"],
		"emergency": "Non, mais diagnostic précoce important.",
		"exams": ["Ferritine", "Coefficient de saturation de la transferrine", "Test génétique"],
		"treatments": ["Saignées régulières (phlébotomies)"],
		"advice": ["Éviter compléments en fer et vitamine C", "Limiter alcool"],
		"prevention": ["Dépistage familial"],
		"tags": ["foie", "fatigue", "genetique"],
	},
	{
		"slug": "maladie-coeliaque",
		"title": "Maladie cœliaque",
		"image": "/static/img/pathologies/maladie-coeliaque.jpg",
		"summary": "Intolérance immunitaire au gluten (blé, orge, seigle).",
		"symptoms": ["Diarrhée", "Ballonnements", "Anémie", "Amaigrissement"],
		"emergency": "Non, mais nécessite un régime strict à vie.",
		"exams": ["Anticorps anti-transglutaminase", "Gastroscopie avec biopsies duodénales"],
		"treatments": ["Régime sans gluten strict et à vie"],
		"advice": ["Apprendre à lire les étiquettes", "Attention aux contaminations croisées"],
		"prevention": ["Aucune (prédisposition génétique)"],
		"tags": ["diarrhee", "anemie", "gluten"],
	},
	{
		"slug": "diverticulose",
		"title": "Diverticulose colique",
		"image": "/static/img/pathologies/diverticulose.jpg",
		"summary": "Présence de petites poches (diverticules) sur la paroi du côlon.",
		"symptoms": ["Asymptomatique le plus souvent", "Parfois troubles du transit"],
		"emergency": "Non, sauf complication (diverticulite).",
		"exams": ["Coloscopie (découverte souvent fortuite)", "Scanner si douleur"],
		"treatments": ["Régime riche en fibres", "Hydratation"],
		"advice": ["Lutter contre la constipation"],
		"prevention": ["Manger des fibres"],
		"tags": ["colon", "constipation"],
	},
	{
		"slug": "diverticulite",
		"title": "Diverticulite",
		"image": "/static/img/pathologies/diverticulite.jpg",
		"summary": "Infection d'un diverticule : la 'sigmoïdite'.",
		"symptoms": ["Douleur en bas à gauche du ventre", "Fièvre", "Troubles du transit"],
		"emergency": "Consultez rapidement (risque d'abcès ou péritonite).",
		"exams": ["Scanner abdominal (examen de référence)", "Bilan sanguin"],
		"treatments": ["Antibiotiques", "Régime sans résidus", "Parfois hospitalisation"],
		"advice": ["Reprise progressive des fibres après guérison"],
		"prevention": ["Traiter la constipation"],
		"tags": ["douleur abdominale", "fievre", "colon"],
	},
	{
		"slug": "polypes-colon",
		"title": "Polypes du côlon",
		"image": "/static/img/pathologies/polypes-colon.jpg",
		"summary": "Excroissances sur la paroi du côlon, précurseurs possibles du cancer.",
		"symptoms": ["Généralement aucun", "Parfois sang dans les selles"],
		"emergency": "Non, mais doivent être retirés par prévention.",
		"exams": ["Coloscopie (diagnostic et traitement)"],
		"treatments": ["Ablation endoscopique (polypectomie)"],
		"advice": ["Suivre le rythme des coloscopies de contrôle"],
		"prevention": ["Dépistage organisé (test immunologique)"],
		"tags": ["colon", "prevention", "sang selles"],
	},
	{
		"slug": "cancer-colon",
		"title": "Cancer colorectal",
		"image": "/static/img/pathologies/cancer-colon.jpg",
		"summary": "Tumeur maligne du côlon ou du rectum.",
		"symptoms": ["Sang dans les selles", "Modification du transit récente", "Anémie"],
		"emergency": "Consultez rapidement pour diagnostic.",
		"exams": ["Coloscopie avec biopsies", "Scanner TAP"],
		"treatments": ["Chirurgie", "Chimiothérapie", "Radiothérapie (rectum)"],
		"advice": ["Dépistage dès 50 ans ou avant si antécédents"],
		"prevention": ["Test immunologique tous les 2 ans (50-74 ans)"],
		"tags": ["sang selles", "cancer", "colon"],
	},
	{
		"slug": "cancer-pancreas",
		"title": "Cancer du pancréas",
		"image": "/static/img/pathologies/cancer-pancreas.jpg",
		"summary": "Tumeur du pancréas, souvent diagnostiquée tardivement.",
		"symptoms": ["Jaunisse indolore", "Amaigrissement rapide", "Douleur solaire"],
		"emergency": "Consultez rapidement devant ces signes.",
		"exams": ["Scanner abdominal", "Echo-endoscopie"],
		"treatments": ["Chirurgie (si possible)", "Chimiothérapie"],
		"advice": ["Arrêt tabac (facteur de risque majeur)"],
		"prevention": ["Surveillance si pancréatite chronique ou génétique"],
		"tags": ["jaunisse", "amaigrissement", "pancreas"],
	},
	{
		"slug": "cancer-oesophage",
		"title": "Cancer de l'œsophage",
		"image": "/static/img/pathologies/cancer-oesophage.jpg",
		"summary": "Tumeur de l'œsophage liée souvent au tabac/alcool ou au reflux.",
		"symptoms": ["Blocage alimentaire (dysphagie)", "Amaigrissement"],
		"emergency": "Consultez dès l'apparition d'une gêne à la déglutition.",
		"exams": ["Gastroscopie", "Scanner"],
		"treatments": ["Radio-chimiothérapie", "Chirurgie"],
		"advice": ["Arrêt tabac et alcool"],
		"prevention": ["Surveillance endobrachyoesophage (EBO)"],
		"tags": ["dysphagie", "amaigrissement", "oesophage"],
	},
	{
		"slug": "achalasie",
		"title": "Achalasie",
		"image": "/static/img/pathologies/achalasie.jpg",
		"summary": "Trouble moteur de l'œsophage empêchant l'ouverture du sphincter inférieur.",
		"symptoms": ["Blocage des aliments et liquides", "Régurgitations non acides"],
		"emergency": "Non, mais altère la qualité de vie et la nutrition.",
		"exams": ["Manométrie œsophagienne", "Gastroscopie"],
		"treatments": ["Dilatation pneumatique", "Chirurgie (myotomie)"],
		"advice": ["Manger lentement, bien mâcher"],
		"prevention": ["Aucune connue"],
		"tags": ["dysphagie", "oesophage"],
	},
	{
		"slug": "hernie-hiatale",
		"title": "Hernie hiatale",
		"image": "/static/img/pathologies/hernie-hiatale.jpg",
		"summary": "Remontée d'une partie de l'estomac dans le thorax.",
		"symptoms": ["Favorise le reflux (RGO)", "Parfois asymptomatique"],
		"emergency": "Rarement (étranglement exceptionnel).",
		"exams": ["Gastroscopie"],
		"treatments": ["IPP si reflux gênant", "Chirurgie si volumineuse et symptomatique"],
		"advice": ["Éviter de se coucher après le repas"],
		"prevention": ["Éviter le surpoids"],
		"tags": ["reflux", "estomac"],
	},
	{
		"slug": "hemorroides",
		"title": "Hémorroïdes",
		"image": "/static/img/pathologies/hemorroides.jpg",
		"summary": "Dilatation des veines de la zone anale.",
		"symptoms": ["Saignement rouge vif", "Douleur", "Boule à l'anus"],
		"emergency": "Consultez si douleur insupportable (thrombose) ou saignement abondant.",
		"exams": ["Examen proctologique", "Anuscopie"],
		"treatments": ["Crèmes/suppositoires", "Traitements instrumentaux", "Chirurgie"],
		"advice": ["Lutter contre la constipation", "Éviter les épices"],
		"prevention": ["Régime riche en fibres"],
		"tags": ["anus", "douleur", "sang"],
	},
	{
		"slug": "fissure-anale",
		"title": "Fissure anale",
		"image": "/static/img/pathologies/fissure-anale.jpg",
		"summary": "Petite déchirure de la peau de l'anus, très douloureuse.",
		"symptoms": ["Douleur intense pendant et après la selle", "Saignement sur le papier"],
		"emergency": "Non, mais très invalidant.",
		"exams": ["Examen proctologique doux"],
		"treatments": ["Laxatifs", "Crèmes cicatrisantes", "Chirurgie si chronique"],
		"advice": ["Ne pas se retenir d'aller à la selle"],
		"prevention": ["Éviter la constipation"],
		"tags": ["anus", "douleur"],
	},
	{
		"slug": "abces-anal",
		"title": "Abcès et fistule anale",
		"image": "/static/img/pathologies/abces-anal.jpg",
		"summary": "Infection d'une glande anale créant une collection de pus.",
		"symptoms": ["Douleur pulsatile", "Gonflement rouge et chaud", "Fièvre"],
		"emergency": "Oui, nécessite une incision chirurgicale rapide.",
		"exams": ["Examen clinique", "IRM périnéale parfois"],
		"treatments": ["Chirurgie (mise à plat ou drainage)"],
		"advice": ["Consulter dès l'apparition d'une boule douloureuse"],
		"prevention": ["Aucune spécifique"],
		"tags": ["anus", "douleur", "urgence"],
	},
	{
		"slug": "condylomes",
		"title": "Condylomes anaux",
		"image": "/static/img/pathologies/condylomes.jpg",
		"summary": "Verrues génitales dues au virus HPV (Papillomavirus).",
		"symptoms": ["Petites excroissances indolores", "Démangeaisons"],
		"emergency": "Non, mais contagieux.",
		"exams": ["Anuscopie haute résolution"],
		"treatments": ["Destruction locale (laser, électrocoagulation)"],
		"advice": ["Dépistage des partenaires", "Surveillance régulière"],
		"prevention": ["Vaccination HPV", "Préservatif"],
		"tags": ["anus", "MST", "virus"],
	},
	{
		"slug": "constipation",
		"title": "Constipation chronique",
		"image": "/static/img/pathologies/constipation.jpg",
		"summary": "Selles rares (<3/semaine) ou difficiles à évacuer.",
		"symptoms": ["Efforts de poussée", "Sensation d'évacuation incomplète", "Ballonnements"],
		"emergency": "Consultez si arrêt total des gaz (occlusion) ou douleur brutale.",
		"exams": ["Coloscopie (éliminer un obstacle)", "Temps de transit"],
		"treatments": ["Fibres +++", "Hydratation", "Laxatifs osmotiques"],
		"advice": ["Activité physique", "Aller à la selle à heure fixe"],
		"prevention": ["Boire 1,5L d'eau par jour"],
		"tags": ["constipation", "ventre"],
	},
	{
		"slug": "incontinence-fecale",
		"title": "Incontinence fécale",
		"image": "/static/img/pathologies/incontinence-fecale.jpg",
		"summary": "Perte involontaire de gaz ou de selles.",
		"symptoms": ["Fuites incontrôlées", "Urgenturie fécale"],
		"emergency": "Non, mais impact social majeur.",
		"exams": ["Manométrie anorectale", "Echo-endoscopie anale"],
		"treatments": ["Rééducation périnéale", "Régularisation du transit", "Neuromodulation"],
		"advice": ["Oser en parler au médecin"],
		"prevention": ["Protection du périnée (accouchement)"],
		"tags": ["anus", "incontinence"],
	},
	{
		"slug": "dyspepsie",
		"title": "Dyspepsie fonctionnelle",
		"image": "/static/img/pathologies/dyspepsie.jpg",
		"summary": "Inconfort ou douleur chronique au creux de l'estomac sans lésion visible.",
		"symptoms": ["Lourdeur après repas", "Satiété précoce", "Douleur épigastrique"],
		"emergency": "Non.",
		"exams": ["Gastroscopie (normale)"],
		"treatments": ["IPP", "Prokinétiques", "Relaxation"],
		"advice": ["Manger lentement", "Fractionner les repas"],
		"prevention": ["Éviter repas trop gras"],
		"tags": ["estomac", "digestion"],
	},
	{
		"slug": "sibo",
		"title": "SIBO (Pullulation microbienne)",
		"image": "/static/img/pathologies/sibo.jpg",
		"summary": "Excès de bactéries dans l'intestin grêle (Small Intestinal Bacterial Overgrowth).",
		"symptoms": ["Ballonnements précoces après repas", "Gaz", "Diarrhée"],
		"emergency": "Non.",
		"exams": ["Test respiratoire au glucose/lactulose"],
		"treatments": ["Antibiotiques ciblés", "Régime pauvre en fermentescibles"],
		"advice": ["Éviter le grignotage (laisser le complexe moteur migrant agir)"],
		"prevention": ["Traiter les causes de ralentissement du transit"],
		"tags": ["ballonnements", "intestin"],
	},
	{
		"slug": "ascite",
		"title": "Ascite",
		"image": "/static/img/pathologies/ascite.jpg",
		"summary": "Accumulation de liquide dans l'abdomen, souvent liée à une cirrhose.",
		"symptoms": ["Augmentation du volume du ventre", "Prise de poids rapide"],
		"emergency": "Consultez rapidement, surtout si fièvre ou douleur.",
		"exams": ["Ponction d'ascite", "Échographie"],
		"treatments": ["Régime sans sel", "Diurétiques", "Ponctions évacuatrices"],
		"advice": ["Pesée régulière", "Respect strict du régime sans sel"],
		"prevention": ["Traitement de la maladie du foie"],
		"tags": ["foie", "ventre"],
	},
	{
		"slug": "kyste-biliiare",
		"title": "Kyste biliaire",
		"image": "/static/img/pathologies/kyste-biliaire.jpg",
		"summary": "Poche de liquide dans le foie, souvent bénigne.",
		"symptoms": ["Généralement aucun", "Découverte fortuite"],
		"emergency": "Non.",
		"exams": ["Échographie", "Scanner ou IRM pour caractériser"],
		"treatments": ["Abstention thérapeutique le plus souvent", "Surveillance"],
		"advice": ["Pas d'inquiétude si kyste simple typique"],
		"prevention": ["Aucune"],
		"tags": ["foie", "kyste"],
	},
	{
		"slug": "angiome-foie",
		"title": "Angiome du foie",
		"image": "/static/img/pathologies/angiome-foie.jpg",
		"summary": "Tumeur bénigne du foie constituée de vaisseaux sanguins.",
		"symptoms": ["Asymptomatique", "Très fréquent"],
		"emergency": "Non.",
		"exams": ["Échographie (aspect typique)", "IRM si doute"],
		"treatments": ["Aucun traitement nécessaire"],
		"advice": ["Aucun suivi particulier si typique"],
		"prevention": ["Aucune"],
		"tags": ["foie", "tumeur benigne"],
	},
]


GUIDES = [
	{
		"slug": "preparation-coloscopie",
		"title": "Comment se préparer à une coloscopie",
		"summary": "Étapes la veille et le jour J, diète et laxatif.",
		"steps": [
			"Régime pauvre en résidus la veille (précisions sur l'ordonnance).",
			"Boire le laxatif aux horaires indiqués, en fractionnant si besoin.",
			"Hydratation par liquides clairs jusqu'à l'horaire autorisé.",
			"Arriver accompagné si anesthésie; ne pas conduire après l'examen.",
		],
		"pdf": "",
	},
	{
		"slug": "deroulement-fibroscopie",
		"title": "Comment se déroule une fibroscopie",
		"summary": "Durée de l'examen, anesthésie et reprise alimentaire.",
		"steps": [
			"Jeûne de 6h pour solides et 2h pour liquides clairs, sauf consigne différente.",
			"Sédation courte ou anesthésie selon indication; durée d'examen environ 10 minutes.",
			"Surveillance en salle de réveil; reprise alimentaire légère après accord médical.",
			"Ne pas conduire le jour même en cas de sédation/anesthésie.",
		],
		"pdf": "",
	},
	{
		"slug": "anesthesie-endoscopie",
		"title": "Anesthésie pour endoscopie : questions fréquentes",
		"summary": "Sécurité, jeûne, reprise des traitements habituels.",
		"steps": [
			"Respecter le jeûne indiqué; signaler tout traitement (anticoagulant, antiagrégant).",
			"Prendre les traitements autorisés avec une petite gorgée d'eau si prescrit.",
			"Prévoir un accompagnant; ne pas conduire ni signer de documents importants le jour même.",
			"En cas de fièvre ou symptômes la veille, prévenir le secrétariat/anesthésiste.",
		],
		"pdf": "",
	},
	{
		"slug": "apres-examen",
		"title": "Recommandations après l'examen",
		"summary": "Surveillance à domicile, reprise alimentaire, signes d'alerte.",
		"steps": [
			"Repos le jour même en cas d'anesthésie; ne pas conduire.",
			"Reprise alimentaire progressive selon consignes du médecin.",
			"Surveiller l'apparition de douleurs importantes, fièvre, vomissements ou saignements.",
			"Contacter le cabinet ou les urgences en cas de signe d'alerte.",
		],
		"pdf": "",
	},
	{
		"slug": "regime-sans-residu",
		"title": "Régime sans résidu",
		"summary": "Repères dans la prescription d'un régime sans résidu (strict ou élargi).",
		"steps": [
			"Principe : Diminuer les fibres végétales et résidus animaux pour réduire le volume des selles et le transit.",
			"Aliments exclus : Légumes et fruits (crus et cuits), céréales complètes, viandes tendineuses, graisses cuites.",
			"Éviter : Pommes de terre, pain blanc et lait (sauf préparation colique) pour limiter la fermentation et l'accélération du transit.",
			"Durée avant coloscopie : 3 jours de régime sans résidus élargi (yaourts autorisés).",
			"Durée avant chirurgie colique : 3-4 jours élargi puis 3 jours strict.",
			"Après diverticulite/colite : 2-3 semaines strict puis 2 semaines élargi.",
			"Réintroduction : Légumes pauvres en fibres (betteraves, carottes, courgettes pelées), compotes, laitages.",
			"En dernier : Crudités et fruits pelés.",
		],
		"pdf": "",
	},
]


FAQS_FR = [
	{"q": "Comment prendre rendez-vous ?", "a": "Vous pouvez prendre rendez-vous par téléphone au 40 81 48 48, sur Maiia, ou via le formulaire de contact sur le site."},
	{"q": "Dois-je être à jeun avant une endoscopie ?", "a": "Oui, en général 6h sans manger et 2h sans boire de liquide clair, sauf consigne différente."},
	{"q": "Puis-je conduire après une anesthésie ?", "a": "Non, prévoyez un accompagnant. Ne conduisez pas ni ne signez de documents importants le jour même."},
	{"q": "C'est quoi une coloscopie ?", "a": "C'est un examen qui permet d'explorer l'intérieur du côlon à l'aide d'une caméra souple, pour dépister des polypes ou des maladies."},
	{"q": "Quels traitements dois-je arrêter avant une coloscopie ?", "a": "Aspirine, anticoagulants ou antiagrégants peuvent nécessiter un ajustement : demandez un avis personnalisé."},
	{"q": "Combien de temps dure une coloscopie ?", "a": "Environ 20 à 30 minutes, plus le temps de préparation et de réveil."},
	{"q": "Quand consulter en urgence ?", "a": "Fièvre élevée, sang dans les selles, douleurs abdominales intenses, vomissements répétés : appelez ou rendez-vous aux urgences."},
	{"q": "Faut-il une ordonnance pour consulter ?", "a": "Il est préférable d'avoir un courrier de votre médecin traitant pour respecter le parcours de soins et être mieux remboursé."},
	{"q": "Le médecin est-il conventionné ?", "a": "Oui, le Dr Bronstein est conventionné et accepte le tiers payant."},
	{"q": "Quels sont les horaires d'ouverture et de consultation du cabinet ?", "a": "Le cabinet est ouvert du lundi au vendredi de 7h00 à 17h00, et le samedi de 8h30 à 12h00."},
	{"q": "Quelle est l'adresse du cabinet ?", "a": "Le cabinet est situé à Papeete, immeuble Air France. Des parkings sont disponibles à proximité (Tarahoi)."},
	{"q": "Comment contacter le cabinet ?", "a": "Vous pouvez nous joindre par téléphone au 40 81 48 48 ou via le formulaire de contact du site."},
	{"q": "Comment se passe le paiement ?", "a": "Le règlement se fait sur place par chèque, espèces ou carte bancaire. Le tiers payant est possible selon votre couverture."},
	{"q": "Où se garer pour venir au cabinet ?", "a": "Des parkings publics sont disponibles à proximité de l'immeuble Air France (parking Tarahoi ou front de mer)."},
	{"q": "Les enfants sont-ils pris en charge ?", "a": "Le Dr Bronstein reçoit les adultes et adolescents. Pour les jeunes enfants, un pédiatre gastro-entérologue est recommandé."},
	{"q": "Puis-je avoir un arrêt de travail ?", "a": "Un arrêt de travail peut être délivré le jour de l'examen (coloscopie/fibroscopie) si nécessaire."},
	{"q": "Combien de temps avant d'avoir les résultats ?", "a": "Le compte-rendu est remis immédiatement après l'examen. Les résultats de biopsies prennent environ 10 à 15 jours."},
	{"q": "Que faire si j'ai oublié ma préparation ?", "a": "Contactez le secrétariat au plus vite. Une mauvaise préparation peut obliger à annuler et reporter l'examen."},
	{"q": "Le cabinet est-il accessible aux PMR ?", "a": "Oui, l'immeuble dispose d'ascenseurs et est accessible aux personnes à mobilité réduite."},
	{"q": "Puis-je venir accompagné ?", "a": "Oui, c'est même obligatoire pour repartir après une anesthésie générale ou une sédation."},
	{"q": "En quoi consiste une pH-métrie ?", "a": "C'est un examen qui mesure l'acidité dans l'œsophage pendant 24h à l'aide d'une fine sonde nasale, pour diagnostiquer un reflux."},
	{"q": "La pH-métrie est-elle douloureuse ?", "a": "L'examen est peu agréable lors de la pose de la sonde, mais n'est pas douloureux. On s'habitue rapidement à la présence de la sonde."},
	{"q": "Qu'est-ce qu'une vidéocapsule ?", "a": "C'est une gélule contenant une caméra que l'on avale pour explorer l'intestin grêle, zone inaccessible aux endoscopes classiques."},
	{"q": "Peut-on faire une gastroscopie et une coloscopie en même temps ?", "a": "Oui, c'est fréquent. Cela permet de réaliser les deux examens sous la même anesthésie."},
	{"q": "Qu'est-ce que l'Helicobacter pylori ?", "a": "C'est une bactérie présente dans l'estomac qui peut causer gastrites et ulcères. Elle se traite par antibiotiques."},
	{"q": "Le stress peut-il causer des maux de ventre ?", "a": "Oui, le stress influence le système digestif et peut aggraver le syndrome de l'intestin irritable ou les brûlures d'estomac."},
	{"q": "Quels sont les symptômes d'un polype au côlon ?", "a": "La plupart des polypes ne donnent aucun symptôme, d'où l'importance du dépistage par coloscopie avant qu'ils ne dégénèrent."},
	{"q": "Y a-t-il des risques à passer une coloscopie ?", "a": "Les risques (perforation, hémorragie) sont très rares. Le bénéfice du dépistage du cancer colorectal est largement supérieur."},
	{"q": "Quelle alimentation en cas de diverticules ?", "a": "En dehors des crises, une alimentation riche en fibres est recommandée. En cas de crise (diverticulite), un régime sans résidus est prescrit."},
	{"q": "Dois-je arrêter de boire de l'eau avant l'examen ?", "a": "L'arrêt des liquides clairs (eau, thé, café sans lait) est généralement demandé 2 heures avant l'anesthésie."},
	{"q": "C'est quoi des hémorroïdes ?", "a": "Ce sont des veines dilatées au niveau de l'anus. Elles peuvent saigner ou être douloureuses. Le traitement est souvent médical (crèmes, veinotoniques) ou instrumental."},
	{"q": "Quelle différence entre fissure et hémorroïdes ?", "a": "La fissure est une petite coupure très douloureuse au passage des selles, alors que les hémorroïdes sont des gonflements veineux qui peuvent saigner mais sont moins souvent douloureux."},
	{"q": "C'est quoi le syndrome de l'intestin irritable ?", "a": "C'est un trouble fonctionnel fréquent associant douleurs abdominales et troubles du transit (diarrhée/constipation), sans gravité mais gênant."},
	{"q": "Faut-il manger sans gluten ?", "a": "Uniquement si vous avez une maladie coeliaque prouvée ou une sensibilité. Un régime sans gluten strict est contraignant et ne doit pas être fait sans avis médical."},
	{"q": "Comment savoir si je suis intolérant au lactose ?", "a": "Les symptômes sont ballonnements et diarrhée après avoir bu du lait. Un test respiratoire peut confirmer le diagnostic."},
	{"q": "Sang rouge ou noir dans les selles ?", "a": "Du sang rouge vient souvent de l'anus (hémorroïdes). Du sang noir (méléna) signale un saignement plus haut (estomac) et est une urgence."},
	{"q": "Quels aliments éviter pour le reflux ?", "a": "Évitez le café, l'alcool, les épices, les graisses, le chocolat et les boissons gazeuses. Ne vous couchez pas juste après le repas."},
	{"q": "A quoi sert le Fibroscan ?", "a": "C'est un appareil qui mesure l'élasticité du foie pour évaluer la fibrose (cicatrices) sans faire de biopsie. C'est indolore et rapide."},
	{"q": "Les probiotiques sont-ils utiles ?", "a": "Ils peuvent aider dans certaines situations (après antibiotiques, intestin irritable) mais leur efficacité dépend des souches et des personnes."},
	{"q": "Comment attrape-t-on l'hépatite B ou C ?", "a": "Principalement par le sang (matériel non stérile) ou les rapports sexuels non protégés (surtout hépatite B). Il existe un vaccin efficace contre l'hépatite B."},
	{"q": "C'est quoi la maladie de Crohn ?", "a": "C'est une maladie inflammatoire chronique de l'intestin (MICI) qui peut toucher tout le tube digestif. Elle se manifeste par des douleurs, diarrhées et fatigue."},
	{"q": "C'est quoi la rectocolite hémorragique (RCH) ?", "a": "C'est une maladie inflammatoire chronique qui ne touche que le rectum et le côlon. Elle provoque souvent des diarrhées sanglantes."},
	{"q": "Qu'est-ce qu'une cirrhose ?", "a": "C'est une maladie du foie où le tissu sain est remplacé par du tissu cicatriciel (fibrose), empêchant le foie de fonctionner. Les causes principales sont l'alcool et les virus."},
	{"q": "C'est quoi une manométrie anorectale ?", "a": "C'est un examen qui mesure les pressions au niveau de l'anus et du rectum pour explorer la constipation ou l'incontinence. C'est indolore."},
	{"q": "A quoi sert une entéroscopie ?", "a": "C'est une endoscopie profonde de l'intestin grêle, réalisée sous anesthésie générale, pour explorer ou traiter des lésions inaccessibles aux endoscopes classiques."},
	{"q": "Qu'est-ce qu'un ulcère à l'estomac ?", "a": "C'est une plaie dans la paroi de l'estomac ou du duodénum, souvent causée par la bactérie Helicobacter pylori ou la prise d'anti-inflammatoires."},
	{"q": "Le cancer du côlon est-il héréditaire ?", "a": "Il existe des formes héréditaires (syndrome de Lynch, polypose), mais la plupart sont sporadiques. Le dépistage est crucial dès 50 ans ou avant en cas d'antécédents."},
]

FAQS_EN = [
    {"q": "How to make an appointment?", "a": "You can make an appointment by phone at 40 81 48 48, on Maiia, or via the contact form on the website."},
    {"q": "Do I need to be fasting before an endoscopy?", "a": "Yes, usually 6 hours without eating and 2 hours without drinking clear liquids, unless otherwise instructed."},
    {"q": "Can I drive after anesthesia?", "a": "No, bring a companion. Do not drive or sign important documents on the same day."},
    {"q": "What is a colonoscopy?", "a": "It is an exam to explore the inside of the colon using a flexible camera, to screen for polyps or diseases."},
    {"q": "What treatments should I stop before a colonoscopy?", "a": "Aspirin, anticoagulants, or antiplatelet agents may need adjustment: ask for personalized advice."},
    {"q": "How long does a colonoscopy take?", "a": "About 20 to 30 minutes, plus preparation and recovery time."},
    {"q": "When to consult in an emergency?", "a": "High fever, blood in stool, intense abdominal pain, repeated vomiting: call or go to the emergency room."},
    {"q": "Do I need a prescription to consult?", "a": "It is preferable to have a referral letter from your GP to respect the care pathway and be better reimbursed."},
    {"q": "Is the doctor contracted?", "a": "Yes, Dr. Bronstein is contracted and accepts third-party payment."},
    {"q": "What are the consultation hours?", "a": "The office is open Monday to Friday from 7:00 AM to 5:00 PM, and Saturday from 8:30 AM to 12:00 PM."},
    {"q": "How does payment work?", "a": "Payment is made on-site by check, cash, or credit card. Third-party payment is possible depending on your coverage."},
    {"q": "Where to park to come to the office?", "a": "Public parking lots are available near the Air France building (Tarahoi or waterfront parking)."},
    {"q": "Are children treated?", "a": "Dr. Bronstein treats adults and adolescents. For young children, a pediatric gastroenterologist is recommended."},
    {"q": "Can I get a sick note?", "a": "A sick note can be issued on the day of the exam (colonoscopy/gastroscopy) if necessary."},
    {"q": "How long before getting the results?", "a": "The report is given immediately after the exam. Biopsy results take about 10 to 15 days."},
    {"q": "What if I forgot my preparation?", "a": "Contact the secretariat as soon as possible. Poor preparation may require cancelling and rescheduling the exam."},
    {"q": "Is the office accessible to people with reduced mobility?", "a": "Yes, the building has elevators and is accessible to people with reduced mobility."},
    {"q": "Can I come accompanied?", "a": "Yes, it is even mandatory to leave after general anesthesia or sedation."},
    {"q": "What is pH-metry?", "a": "It is an exam that measures acidity in the esophagus for 24 hours using a thin nasal probe to diagnose reflux."},
    {"q": "Is pH-metry painful?", "a": "The exam is uncomfortable during probe placement but not painful. You quickly get used to the probe."},
    {"q": "What is a video capsule?", "a": "It is a pill containing a camera that you swallow to explore the small intestine, an area inaccessible to standard endoscopes."},
    {"q": "Can I have a gastroscopy and colonoscopy at the same time?", "a": "Yes, it is common. This allows both exams to be performed under the same anesthesia."},
    {"q": "What is Helicobacter pylori?", "a": "It is a bacterium present in the stomach that can cause gastritis and ulcers. It is treated with antibiotics."},
    {"q": "Can stress cause stomach pain?", "a": "Yes, stress influences the digestive system and can aggravate irritable bowel syndrome or heartburn."},
    {"q": "What are the symptoms of a colon polyp?", "a": "Most polyps cause no symptoms, hence the importance of screening by colonoscopy before they degenerate."},
    {"q": "Are there risks to having a colonoscopy?", "a": "Risks (perforation, bleeding) are very rare. The benefit of colorectal cancer screening far outweighs them."},
    {"q": "What diet for diverticula?", "a": "Outside of flare-ups, a high-fiber diet is recommended. During a flare-up (diverticulitis), a low-residue diet is prescribed."},
    {"q": "Should I stop drinking water before the exam?", "a": "Stopping clear liquids (water, tea, coffee without milk) is generally required 2 hours before anesthesia."},
    {"q": "What are hemorrhoids?", "a": "They are dilated veins in the anus. They can bleed or be painful. Treatment is often medical (creams, venotonics) or instrumental."},
    {"q": "What is the difference between a fissure and hemorrhoids?", "a": "A fissure is a very painful small cut during bowel movements, while hemorrhoids are venous swellings that may bleed but are less often painful."},
    {"q": "What is irritable bowel syndrome?", "a": "It is a frequent functional disorder associating abdominal pain and transit disorders (diarrhea/constipation), not serious but bothersome."},
    {"q": "Should I eat gluten-free?", "a": "Only if you have proven celiac disease or sensitivity. A strict gluten-free diet is restrictive and should not be done without medical advice."},
    {"q": "How do I know if I am lactose intolerant?", "a": "Symptoms are bloating and diarrhea after drinking milk. A breath test can confirm the diagnosis."},
    {"q": "Red or black blood in stool?", "a": "Red blood often comes from the anus (hemorrhoids). Black blood (melena) signals bleeding higher up (stomach) and is an emergency."},
    {"q": "What foods to avoid for reflux?", "a": "Avoid coffee, alcohol, spices, fats, chocolate, and carbonated drinks. Do not lie down right after a meal."},
    {"q": "What is Fibroscan used for?", "a": "It is a device that measures liver elasticity to assess fibrosis (scarring) without a biopsy. It is painless and fast."},
    {"q": "Are probiotics useful?", "a": "They can help in certain situations (after antibiotics, irritable bowel) but their effectiveness depends on the strains and individuals."},
    {"q": "How do you catch hepatitis B or C?", "a": "Mainly through blood (non-sterile equipment) or unprotected sex (especially hepatitis B). There is an effective vaccine against hepatitis B."},
    {"q": "What is Crohn's disease?", "a": "It is a chronic inflammatory bowel disease (IBD) that can affect the entire digestive tract. It manifests as pain, diarrhea, and fatigue."},
    {"q": "What is ulcerative colitis?", "a": "It is a chronic inflammatory disease that affects only the rectum and colon. It often causes bloody diarrhea."},
    {"q": "What is cirrhosis?", "a": "It is a liver disease where healthy tissue is replaced by scar tissue (fibrosis), preventing the liver from functioning. Main causes are alcohol and viruses."},
    {"q": "What is anorectal manometry?", "a": "It is an exam that measures pressures in the anus and rectum to explore constipation or incontinence. It is painless."},
    {"q": "What is enteroscopy used for?", "a": "It is a deep endoscopy of the small intestine, performed under general anesthesia, to explore or treat lesions inaccessible to standard endoscopes."},
    {"q": "What is a stomach ulcer?", "a": "It is a sore in the lining of the stomach or duodenum, often caused by the bacterium Helicobacter pylori or anti-inflammatory drugs."},
    {"q": "Is colon cancer hereditary?", "a": "There are hereditary forms (Lynch syndrome, polyposis), but most are sporadic. Screening is crucial from age 50 or earlier if there is a family history."},
]

FAQS_ES = [
    {"q": "¿Cómo pedir cita?", "a": "Puede pedir cita por teléfono al 40 81 48 48, en Maiia, o a través del formulario de contacto en el sitio web."},
    {"q": "¿Debo estar en ayunas antes de una endoscopia?", "a": "Sí, generalmente 6 horas sin comer y 2 horas sin beber líquidos claros, salvo indicación contraria."},
    {"q": "¿Puedo conducir después de la anestesia?", "a": "No, traiga un acompañante. No conduzca ni firme documentos importantes el mismo día."},
    {"q": "¿Qué es una colonoscopia?", "a": "Es un examen para explorar el interior del colon con una cámara flexible, para detectar pólipos o enfermedades."},
    {"q": "¿Qué tratamientos debo suspender antes de una colonoscopia?", "a": "Aspirina, anticoagulantes o antiagregantes pueden requerir ajuste: pida consejo personalizado."},
    {"q": "¿Cuánto dura una colonoscopia?", "a": "Unos 20 a 30 minutos, más el tiempo de preparación y recuperación."},
    {"q": "¿Cuándo consultar de urgencia?", "a": "Fiebre alta, sangre en las heces, dolor abdominal intenso, vómitos repetidos: llame o vaya a urgencias."},
    {"q": "¿Necesito una receta para consultar?", "a": "Es preferible tener una carta de derivación de su médico de cabecera para respetar el recorrido de atención y obtener un mejor reembolso."},
    {"q": "¿El médico está conveniado?", "a": "Sí, el Dr. Bronstein está conveniado y acepta el pago de terceros."},
    {"q": "¿Cuáles son los horarios de consulta?", "a": "El consultorio está abierto de lunes a viernes de 7:00 a 17:00, y el sábado de 8:30 a 12:00."},
    {"q": "¿Cómo funciona el pago?", "a": "El pago se realiza en el lugar con cheque, efectivo o tarjeta bancaria. El pago de terceros es posible según su cobertura."},
    {"q": "¿Dónde aparcar para venir al consultorio?", "a": "Hay aparcamientos públicos disponibles cerca del edificio Air France (aparcamiento Tarahoi o frente al mar)."},
    {"q": "¿Se atiende a niños?", "a": "El Dr. Bronstein atiende a adultos y adolescentes. Para niños pequeños, se recomienda un gastroenterólogo pediatra."},
    {"q": "¿Puedo obtener una baja laboral?", "a": "Se puede emitir una baja laboral el día del examen (colonoscopia/gastroscopia) si es necesario."},
    {"q": "¿Cuánto tiempo tardan los resultados?", "a": "El informe se entrega inmediatamente después del examen. Los resultados de las biopsias tardan unos 10 a 15 días."},
    {"q": "¿Qué pasa si olvidé mi preparación?", "a": "Contacte a la secretaría lo antes posible. Una mala preparación puede obligar a cancelar y reprogramar el examen."},
    {"q": "¿El consultorio es accesible para personas con movilidad reducida?", "a": "Sí, el edificio dispone de ascensores y es accesible para personas con movilidad reducida."},
    {"q": "¿Puedo venir acompañado?", "a": "Sí, es incluso obligatorio para salir después de una anestesia general o sedación."},
    {"q": "¿En qué consiste una pH-metría?", "a": "Es un examen que mide la acidez en el esófago durante 24h mediante una fina sonda nasal, para diagnosticar reflujo."},
    {"q": "¿Es dolorosa la pH-metría?", "a": "El examen es poco agradable durante la colocación de la sonda, pero no es doloroso. Uno se acostumbra rápidamente a la presencia de la sonda."},
    {"q": "¿Qué es una videocápsula?", "a": "Es una cápsula que contiene una cámara que se traga para explorar el intestino delgado, zona inaccesible a los endoscopios clásicos."},
    {"q": "¿Se pueden hacer una gastroscopia y una colonoscopia al mismo tiempo?", "a": "Sí, es frecuente. Esto permite realizar ambos exámenes bajo la misma anestesia."},
    {"q": "¿Qué es el Helicobacter pylori?", "a": "Es una bacteria presente en el estómago que puede causar gastritis y úlceras. Se trata con antibióticos."},
    {"q": "¿El estrés puede causar dolor de estómago?", "a": "Sí, el estrés influye en el sistema digestivo y puede agravar el síndrome del intestino irritable o la acidez estomacal."},
    {"q": "¿Cuáles son los síntomas de un pólipo en el colon?", "a": "La mayoría de los pólipos no dan síntomas, de ahí la importancia del cribado por colonoscopia antes de que degeneren."},
    {"q": "¿Hay riesgos al hacerse una colonoscopia?", "a": "Los riesgos (perforación, hemorragia) son muy raros. El beneficio del cribado del cáncer colorrectal es muy superior."},
    {"q": "¿Qué dieta en caso de divertículos?", "a": "Fuera de las crisis, se recomienda una dieta rica en fibra. En caso de crisis (diverticulitis), se prescribe una dieta sin residuos."},
    {"q": "¿Debo dejar de beber agua antes del examen?", "a": "Generalmente se pide dejar los líquidos claros (agua, té, café sin leche) 2 horas antes de la anestesia."},
    {"q": "¿Qué son las hemorroides?", "a": "Son venas dilatadas en el ano. Pueden sangrar o ser dolorosas. El tratamiento suele ser médico (cremas, venotónicos) o instrumental."},
    {"q": "¿Qué diferencia hay entre fisura y hemorroides?", "a": "La fisura es un pequeño corte muy doloroso al defecar, mientras que las hemorroides son hinchazones venosas que pueden sangrar pero son menos dolorosas."},
    {"q": "¿Qué es el síndrome del intestino irritable?", "a": "Es un trastorno funcional frecuente que asocia dolor abdominal y trastornos del tránsito (diarrea/estreñimiento), sin gravedad pero molesto."},
    {"q": "¿Debo comer sin gluten?", "a": "Solo si tiene enfermedad celíaca probada o sensibilidad. Una dieta estricta sin gluten es restrictiva y no debe hacerse sin consejo médico."},
    {"q": "¿Cómo saber si soy intolerante a la lactosa?", "a": "Los síntomas son hinchazón y diarrea después de beber leche. Una prueba de aliento puede confirmar el diagnóstico."},
    {"q": "¿Sangre roja o negra en las heces?", "a": "La sangre roja suele venir del ano (hemorroides). La sangre negra (melena) indica un sangrado más arriba (estómago) y es una urgencia."},
    {"q": "¿Qué alimentos evitar para el reflujo?", "a": "Evite café, alcohol, especias, grasas, chocolate y bebidas gaseosas. No se acueste justo después de comer."},
    {"q": "¿Para qué sirve el Fibroscan?", "a": "Es un aparato que mide la elasticidad del hígado para evaluar la fibrosis (cicatrices) sin hacer biopsia. Es indoloro y rápido."},
    {"q": "¿Son útiles los probióticos?", "a": "Pueden ayudar en ciertas situaciones (después de antibióticos, intestino irritable) pero su eficacia depende de las cepas y las personas."},
    {"q": "¿Cómo se contrae la hepatitis B o C?", "a": "Principalmente por sangre (material no estéril) o relaciones sexuales sin protección (sobre todo hepatitis B). Existe una vacuna eficaz contra la hepatitis B."},
    {"q": "¿Qué es la enfermedad de Crohn?", "a": "Es una enfermedad inflamatoria crónica del intestino (EII) que puede afectar todo el tubo digestivo. Se manifiesta por dolor, diarrea y fatiga."},
    {"q": "¿Qué es la colitis ulcerosa?", "a": "Es una enfermedad inflamatoria crónica que solo afecta el recto y el colon. A menudo provoca diarrea con sangre."},
    {"q": "¿Qué es una cirrosis?", "a": "Es una enfermedad del hígado donde el tejido sano es reemplazado por tejido cicatricial (fibrosis), impidiendo que el hígado funcione. Las causas principales son el alcohol y los virus."},
    {"q": "¿Qué es una manometría anorrectal?", "a": "Es un examen que mide las presiones en el ano y el recto para explorar el estreñimiento o la incontinencia. Es indoloro."},
    {"q": "¿Para qué sirve una enteroscopia?", "a": "Es una endoscopia profunda del intestino delgado, realizada bajo anestesia general, para explorar o tratar lesiones inaccesibles a los endoscopios clásicos."},
    {"q": "¿Qué es una úlcera de estómago?", "a": "Es una llaga en la pared del estómago o del duodeno, a menudo causada por la bacteria Helicobacter pylori o la toma de antiinflamatorios."},
    {"q": "¿El cáncer de colon es hereditario?", "a": "Existen formas hereditarias (síndrome de Lynch, poliposis), pero la mayoría son esporádicos. El cribado es crucial desde los 50 años o antes si hay antecedentes."},
]

FAQS = FAQS_FR

SYMPTOM_TAGS = {
	"brûlures / reflux": ["brulure-estomac", "reflux-enceinte"],
	"diarrhée": ["gastro-enterite", "diarrhee-chronique"],
	"douleurs hautes": ["gastrite", "brulure-estomac", "cancer-estomac"],
	"foie / bilan hépatique": ["foie-gras"],
	"sang dans les selles": ["diarrhee-chronique"],
}


TEAM = [
	{
		"name": "Dr Jean-Ariel Bronstein",
		"role": _("Professeur agrégé du Val-de-Grâce"),
		"focus": _("Gastro-entérologue, Oncologie digestive, endoscopies interventionnelles, échographie abdominale"),
		"contact": "docteur@bronstein.fr",
		"photo": "img/dr-bronstein.jpg",
	},
	{
		"name": "Tania Mauri",
		"role": _("Secrétaire médicale"),
		"focus": _("Accueil, rendez-vous, préparation des examens"),
		"contact": "secretaire@bronstein.fr",
		"photo": "img/tania-mauri.jpg",
	},
]


CONTACT = {
	"phones": ["40 81 48 48", "87 37 87 50", "87 345 372"],
	"doctor_email": "docteur@bronstein.fr",
	"secretary_email": "secretaire@bronstein.fr",
	"hospital": {
		"title": "Clinique PAOFAI",
		"address": "BP 40149 — 98713 Papeete, Tahiti",
		"phone": "40 46 18 18",
		"maps": "https://maps.google.com/?q=Clinique+Paofai+Tahiti",
	},
	"consult": {
		"title": _("Consultations"),
		"address": "Immeuble Air France — rue LAGARDE — 4e étage (en face de GEMO), Papeete",
		"phone": "40 81 48 48 / 87 345 372",
		"maps": "https://maps.google.com/?q=Immeuble+Air+France+Papeete",
	},
	"hours": "Lundi-Vendredi 07:00-17:00 · Samedi 08:30-12:00",
}


HOME_TILES = [
	{
		"title": _("Prendre rendez-vous"),
		"text": _("Téléphone ou formulaire rapide pour planifier une consultation ou une endoscopie."),
		"action": _("Appeler le cabinet"),
		"link": "tel:+68940814848",
		"variant": "primary",
	},
	{
		"title": _("Préparer mon examen"),
		"text": _("Consignes claires pour coloscopie, fibroscopie et examens digestifs."),
		"action": _("Consignes coloscopie"),
		"link": "/guides/#preparation-coloscopie",
		"variant": "outline",
	},
	{
		"title": _("Conseils digestifs"),
		"text": _("Reflux, diarrhée chronique, foie gras : que faire avant de consulter ?"),
		"action": _("Voir les articles"),
		"link": "/blog/",
		"variant": "ghost",
	},
]


def home(request):
	context = {
		"hero": {
			"title": _("Je viens consulter, comment ça se passe ?"),
			"subtitle": "",
			"cta_call": "tel:+68940814848",
			"cta_message": "mailto:bronstein@mail.pf",
		},
		"tiles": HOME_TILES,
		"specialties": EXAMS,
		"blog_posts": BLOG_POSTS,
		"contact": CONTACT,
		"pathologies": PATHOLOGIES,
		"guides": GUIDES,
		"faqs": FAQS[:4],
		"team": TEAM,
	}
	return render(request, "core/home.html", context)


def exam_list(request):
	return render(request, "core/exams.html", {"exams": EXAMS})


def exam_detail(request, slug):
	try:
		exam = next(e for e in EXAMS if e["slug"] == slug)
	except StopIteration as exc:
		raise Http404 from exc

	return render(request, "core/exam_detail.html", {"exam": exam, "exams": EXAMS})


def consultations(request):
	context = {"contact": CONTACT, "team": TEAM}
	return render(request, "core/consultations.html", context)


def pathology_list(request):
	return render(request, "core/pathologies.html", {"pathologies": PATHOLOGIES})


def pathology_detail(request, slug):
	try:
		pathology = next(p for p in PATHOLOGIES if p["slug"] == slug)
	except StopIteration as exc:
		raise Http404 from exc

	return render(
		request,
		"core/pathology_detail.html",
		{"pathology": pathology, "pathologies": PATHOLOGIES},
	)


def guides(request):
	return render(request, "core/guides.html", {"guides": GUIDES})


def symptom_index(request):
	enriched = []
	for label, slugs in SYMPTOM_TAGS.items():
		items = [p for p in PATHOLOGIES if p["slug"] in slugs]
		enriched.append({"label": label, "items": items})
	return render(request, "core/symptoms.html", {"groups": enriched})


def faq(request):
	return render(request, "core/faq.html", {"faqs": FAQS})


def appointment(request):
	context = {
		"contact": CONTACT,
		"cta": {
			"call": "tel:+68940814848",
			"message": f"mailto:{CONTACT['secretary_email']}",
			"doctolib": "https://www.maiia.com/gastro-enterologue-et-hepatologue/98714-papeete/bronstein-jean-ariel",
		},
		"team": TEAM,
	}
	return render(request, "core/appointment.html", context)


def blog_list(request):
	return render(request, "core/blog_list.html", {"posts": BLOG_POSTS})


def blog_detail(request, slug):
	try:
		post = next(p for p in BLOG_POSTS if p["slug"] == slug)
	except StopIteration as exc:
		raise Http404 from exc

	return render(request, "core/blog_detail.html", {"post": post, "posts": BLOG_POSTS})


def contact_view(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            # Ici, on pourrait envoyer un email
            # send_mail(...)
            messages.success(request, "Votre message a bien été envoyé. Nous vous répondrons dans les meilleurs délais.")
            return redirect('contact')
    else:
        form = ContactForm()

    context = {
        "form": form,
        "contact": CONTACT,
    }
    return render(request, "core/contact.html", context)


import re
import difflib

def normalize_text(text):
    """Normalize text to remove accents, lowercase, and remove punctuation."""
    # Remove accents
    text = ''.join(c for c in unicodedata.normalize('NFD', text)
                  if unicodedata.category(c) != 'Mn')
    # Lowercase
    text = text.lower()
    # Replace punctuation with space
    text = re.sub(r'[^\w\s]', ' ', text)
    return text

@csrf_exempt
def chatbot_api(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            raw_message = data.get('message', '')
            user_message = normalize_text(raw_message)
            request_type = data.get('type', 'normal') # 'normal' or 'openevidence'
            
            if request_type == 'openevidence':
                # Simulation of OpenEvidence API call
                # In a real scenario, you would call the OpenEvidence API here
                
                response_text = "D'après les recommandations actuelles, ce sujet nécessite une évaluation clinique approfondie."
                
                if any(w in user_message for w in ['risque', 'danger', 'complication', 'risk', 'perforation', 'hemorragie']):
                     response_text = "Les études montrent une incidence très faible de complications majeures (< 0.1%). Le rapport bénéfice/risque reste très favorable pour le dépistage."
                elif any(w in user_message for w in ['traitement', 'soigner', 'medicament', 'treatment', 'guerir', 'aspirine', 'anticoagulant']):
                     response_text = "Les protocoles actuels préconisent une approche graduelle. Pour les traitements anticoagulants, un avis médical est indispensable avant tout acte endoscopique."
                elif any(w in user_message for w in ['coloscopie', 'gastroscopie', 'endoscopie', 'examen', 'camera', 'polype']):
                     response_text = "L'endoscopie est l'examen de référence pour explorer le tube digestif. Elle permet un diagnostic précis (visuel et biopsies) et parfois un traitement immédiat (ex: ablation de polypes)."
                elif any(w in user_message for w in ['symptome', 'douleur', 'signe', 'symptom', 'mal', 'ventre']):
                     response_text = "La présentation clinique peut être variable. L'examen clinique et l'endoscopie sont souvent nécessaires pour confirmer le diagnostic et exclure d'autres pathologies."
                elif any(w in user_message for w in ['prepa', 'boire', 'manger', 'regime']):
                     response_text = "La qualité de la préparation est le facteur prédictif le plus important pour la réussite de l'examen. Il est crucial de suivre le protocole à la lettre."

                return JsonResponse({
                    'response': f"Voici des informations complémentaires : \n\n{response_text}\n\n(Ceci est une réponse générée automatiquement, veuillez consulter votre médecin pour un avis personnalisé.)"
                })
            
            print(f"Chatbot received: {raw_message} -> {user_message}")

            if not user_message:
                return JsonResponse({'response': "Je n'ai pas compris votre message."})

            # Language detection
            words = user_message.split()
            
            # Markers
            en_markers = {
                'the', 'this', 'that', 'these', 'those', 'with', 'for', 'from', 'about', 
                'you', 'your', 'my', 'mine', 'we', 'our', 'they', 'their',
                'have', 'has', 'had', 'are', 'was', 'were', 'will', 'would', 'can', 'could', 'should',
                'what', 'where', 'when', 'how', 'why', 'who', 'which',
                'hello', 'hi', 'thanks', 'please', 'appointment', 'pain', 'doctor', 'help', 'morning', 'evening',
                'do', 'does', 'did', 'is', 'am', 'need', 'want'
            }
            
            es_markers = {
                'el', 'los', 'las', 'un', 'una', 'unos', 'unas', 
                'es', 'son', 'fue', 'fueron', 'estoy', 'estas', 'esta', 'estamos', 'estan',
                'yo', 'usted', 'nosotros', 'vosotros', 'ellos', 'ellas',
                'que', 'como', 'donde', 'cuando', 'porque', 'quien', 'cual',
                'por', 'para', 'con', 'del', 'al', 'sin',
                'hola', 'gracias', 'cita', 'dolor', 'medico', 'ayuda', 'buenos', 'dias', 'tarde', 'noche',
                'tengo', 'necesito', 'quiero'
            }
            
            fr_markers = {
                'le', 'les', 'des', 'du', 'au', 'aux', 
                'est', 'sont', 'suis', 'etes', 'etait', 'etaient',
                'je', 'nous', 'vous', 'ils', 'elles', 'mon', 'ma', 'mes', 'ton', 'ta', 'tes', 'son', 'sa', 'ses', 'notre', 'votre',
                'quoi', 'comment', 'quand', 'pourquoi', 'quel', 'quelle', 'quels', 'quelles',
                'dans', 'sur', 'sous', 'avec', 'sans', 'pour', 'par',
                'bonjour', 'bonsoir', 'merci', 'rendez-vous', 'rdv', 'douleur', 'medecin', 'aide',
                'ai', 'besoin', 'veux', 'voudrais'
            }

            score_en = sum(1 for w in words if w in en_markers)
            score_es = sum(1 for w in words if w in es_markers)
            score_fr = sum(1 for w in words if w in fr_markers)

            # Default to FR
            lang = 'fr'
            if score_en > score_fr and score_en > score_es:
                lang = 'en'
            elif score_es > score_fr and score_es > score_en:
                lang = 'es'
            
            print(f"Detected language: {lang} (FR:{score_fr}, EN:{score_en}, ES:{score_es})")

            # Select data based on language
            if lang == 'en':
                current_faqs = FAQS_EN
                greeting_response = "Hello! How can I help you?"
                fallback_response = "I'm not sure I understand. You can contact us at 40 81 48 48 or check our FAQ page."
                stop_words = {
                    'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'from', 'up', 'about', 'into', 'over', 'after',
                    'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'shall', 'should', 'can', 'could', 'may', 'might', 'must',
                    'i', 'you', 'he', 'she', 'it', 'we', 'they', 'my', 'your', 'his', 'her', 'its', 'our', 'their', 'me', 'him', 'us', 'them',
                    'what', 'which', 'who', 'whom', 'whose', 'where', 'when', 'why', 'how',
                    'this', 'that', 'these', 'those', 'here', 'there',
                    'please', 'thanks', 'thank', 'hello', 'hi'
                }
                # English Synonyms
                synonyms = {
                    "rdv": "appointment",
                    "dr": "doctor",
                    "cost": "payment",
                    "price": "payment",
                    "pay": "payment",
                    "eat": "fasting",
                    "drink": "fasting",
                    "food": "fasting",
                    "meal": "fasting",
                    "hurt": "pain",
                    "ache": "pain",
                    "stomach": "abdominal",
                    "belly": "abdominal",
                    "location": "park",
                    "address": "park",
                    "parking": "park",
                    "result": "results",
                    "poop": "stool",
                    "burn": "reflux",
                    "acid": "reflux",
                    "virus": "hepatitis",
                    "alcohol": "cirrhosis",
                    "hours": "hours",
                    "open": "hours",
                    "close": "hours",
                    "time": "hours",
                }
            elif lang == 'es':
                current_faqs = FAQS_ES
                greeting_response = "¡Hola! ¿En qué puedo ayudarle?"
                fallback_response = "No estoy seguro de entender. Puede contactarnos al 40 81 48 48 o consultar nuestra página de preguntas frecuentes."
                stop_words = {
                    'el', 'la', 'los', 'las', 'un', 'una', 'unos', 'unas', 'y', 'o', 'pero', 'si', 'no', 'en', 'a', 'de', 'del', 'al', 'por', 'para', 'con', 'sin', 'sobre',
                    'es', 'son', 'fue', 'fueron', 'ser', 'estar', 'estoy', 'estas', 'esta', 'estamos', 'estan', 'haber', 'hay', 'tener', 'tengo', 'tienes', 'tiene', 'tenemos', 'tienen',
                    'yo', 'tu', 'el', 'ella', 'nosotros', 'vosotros', 'ellos', 'ellas', 'mi', 'tu', 'su', 'nuestro', 'vuestro', 'me', 'te', 'le', 'nos', 'os', 'les',
                    'que', 'quien', 'donde', 'cuando', 'como', 'porque', 'cual', 'cuales',
                    'este', 'esta', 'estos', 'estas', 'ese', 'esa', 'esos', 'esas', 'aquel', 'aquella', 'aquellos', 'aquellas',
                    'hola', 'gracias', 'por favor'
                }
                # Spanish Synonyms
                synonyms = {
                    "cita": "consulta",
                    "dr": "medico",
                    "doctor": "medico",
                    "precio": "pago",
                    "costo": "pago",
                    "pagar": "pago",
                    "comer": "ayunas",
                    "beber": "ayunas",
                    "comida": "ayunas",
                    "alimentos": "ayunas",
                    "doler": "dolor",
                    "estomago": "abdominal",
                    "barriga": "abdominal",
                    "direccion": "aparcar",
                    "ubicacion": "aparcar",
                    "estacionamiento": "aparcar",
                    "parking": "aparcar",
                    "resultado": "resultados",
                    "caca": "heces",
                    "ardor": "reflujo",
                    "acidez": "reflujo",
                    "virus": "hepatitis",
                    "alcohol": "cirrosis",
                    "horas": "horarios",
                    "abierto": "horarios",
                    "cerrado": "horarios",
                    "tiempo": "horarios",
                }
            else: # FR
                current_faqs = FAQS_FR
                greeting_response = "Bonjour ! Comment puis-je vous aider ?"
                fallback_response = "Je ne suis pas sûr de comprendre. Vous pouvez nous contacter au 40 81 48 48 ou consulter notre page FAQ."
                stop_words = {
                    'le', 'la', 'les', 'de', 'du', 'des', 'un', 'une', 'est', 'il', 'elle', 'je', 'tu', 'nous', 'vous', 'ils', 'elles', 
                    'a', 'au', 'aux', 'ce', 'cette', 'ces', 'mon', 'ma', 'mes', 'ton', 'ta', 'tes', 'son', 'sa', 'ses', 'notre', 'votre', 
                    'leur', 'leurs', 'que', 'qui', 'quoi', 'ou', 'quand', 'comment', 'pourquoi', 'quel', 'quelle', 'quels', 'quelles', 
                    'sur', 'sous', 'dans', 'par', 'pour', 'en', 'vers', 'avec', 'sans', 'y', 't', 'me', 'se', 'c', 'qu', 'j', 'l', 'n', 'd', 's', 'm',
                    'cest', 'quest', 'qu est', 'c est', 'sont', 'suis', 'es', 'sommes', 'etes', 'ete', 'etait', 'etaient',
                    'donne', 'moi', 'toi', 'lui', 'eux', 'ca', 'ceci', 'cela', 'faire', 'avoir', 'etre', 'aller', 'voir', 'savoir', 'pouvoir', 'vouloir', 'devoir', 'falloir',
                    'bonjour', 'merci', 'svp', 'plait', 'sil', 'te', 'se', 'nous', 'vous', 'ils', 'elles', 'on', 'en', 'y',
                    'numero', 'num', 'info', 'infos', 'information', 'informations', 'renseignement', 'renseignements',
                }
                synonyms = {
                    "rdv": "rendez-vous",
                    "docteur": "medecin",
                    "dr": "medecin",
                    "prix": "paiement",
                    "tarif": "paiement",
                    "cout": "paiement",
                    "argent": "paiement",
                    "reglement": "paiement",
                    "manger": "jeun",
                    "boire": "jeun",
                    "repas": "jeun",
                    "nourriture": "jeun",
                    "alcool": "jeun",
                    "mal": "douleurs",
                    "bide": "abdominale",
                    "ventre": "abdominale",
                    "estomac": "abdominale",
                    "parking": "garer",
                    "stationnement": "garer",
                    "resultat": "resultats",
                    "biopsie": "biopsies",
                    "lait": "lactose",
                    "caca": "selles",
                    "popo": "selles",
                    "toilette": "selles",
                    "fesses": "anus",
                    "derriere": "anus",
                    "brulure": "reflux",
                    "remontee": "reflux",
                    "acide": "reflux",
                    "virus": "hepatite",
                    "contamination": "hepatite",
                    "mici": "crohn",
                    "rch": "rectocolite",
                    "alcool": "cirrhose",
                    "fibrose": "cirrhose",
                    "constipation": "manometrie",
                    "incontinence": "manometrie",
                    "heures": "horaires",
                    "heure": "horaires",
                    "ouverture": "horaires",
                    "fermeture": "horaires",
                    "telephone": "contacter",
                    "tel": "contacter",
                    "mail": "contacter",
                    "mails": "contacter",
                    "email": "contacter",
                    "emails": "contacter",
                    "joindre": "contacter",
                    "appeler": "contacter",
                    # Anatomy
                    "intestin": "abdominale",
                    "colon": "abdominale",
                    "foie": "hepatique",
                    "oesophage": "abdominale",
                    "gorge": "oesophage",
                    "rectum": "anus",
                    "bouche": "abdominale",
                    # Symptoms - Pain/Discomfort
                    "douleur": "douleurs",
                    "souffrance": "douleurs",
                    "bobo": "douleurs",
                    "crampe": "douleurs",
                    "spasme": "douleurs",
                    "picotement": "douleurs",
                    "lance": "douleurs",
                    "aigreur": "reflux",
                    "pyrosis": "reflux",
                    "regurgitation": "reflux",
                    "amer": "reflux",
                    # Symptoms - Digestive
                    "vomi": "vomissements",
                    "vomir": "vomissements",
                    "gerber": "vomissements",
                    "nausee": "vomissements",
                    "ecoeurement": "vomissements",
                    "sang": "saignement",
                    "saigne": "saignement",
                    "hemorragie": "saignement",
                    "rouge": "saignement",
                    "noir": "melena",
                    "goudron": "melena",
                    "diarrhee": "transit",
                    "chiasse": "transit",
                    "courante": "transit",
                    "liquide": "transit",
                    "eau": "transit",
                    "dur": "constipation",
                    "bloque": "constipation",
                    "coince": "constipation",
                    "bouche": "constipation",
                    "gaz": "ballonnements",
                    "pet": "ballonnements",
                    "rot": "ballonnements",
                    "ballonne": "ballonnements",
                    "gonfle": "ballonnements",
                    "air": "ballonnements",
                    "glouglou": "ballonnements",
                    # General State
                    "fatigue": "asthenie",
                    "epuise": "asthenie",
                    "creve": "asthenie",
                    "fievre": "temperature",
                    "chaud": "temperature",
                    "frisson": "temperature",
                    "maigrir": "poids",
                    "grossir": "poids",
                    "appetit": "faim",
                    # Procedures
                    "colo": "coloscopie",
                    "gastro": "gastroscopie",
                    "endo": "endoscopie",
                    "camera": "endoscopie",
                    "tuyau": "endoscopie",
                    "fibro": "gastroscopie",
                    "echo": "echographie",
                    "scan": "scanner",
                    "irm": "scanner",
                    "operation": "intervention",
                    "chirurgie": "intervention",
                    "bloc": "intervention",
                    "anesthesie": "dodo",
                    "dormir": "anesthesie",
                    "reveil": "anesthesie",
                    "sedation": "anesthesie",
                    # Preparation
                    "preparation": "prepa",
                    "purge": "prepa",
                    "sachet": "prepa",
                    "picoprep": "prepa",
                    "citrafleet": "prepa",
                    "moviprep": "prepa",
                    "colokit": "prepa",
                    "izinova": "prepa",
                    "kleanprep": "prepa",
                    # Conditions
                    "ulcere": "pathologie",
                    "tumeur": "pathologie",
                    "polype": "pathologie",
                    "kyste": "pathologie",
                    "diverticule": "pathologie",
                    "hernie": "pathologie",
                    "calcul": "lithiase",
                    "caillou": "lithiase",
                    "pierre": "lithiase",
                    "vesicule": "lithiase",
                    "gluten": "coeliaque",
                    "ble": "coeliaque",
                    "sucre": "intolerance",
                    # Administrative
                    "carte": "vitale",
                    "vitale": "assurance",
                    "mutuelle": "assurance",
                    "remboursement": "paiement",
                    "secu": "assurance",
                    "cps": "assurance",
                    "feuille": "papier",
                    "ordonnance": "prescription",
                    "papier": "document",
                    "arret": "travail",
                    "certificat": "document",
                    "lettre": "courrier",
                    "dossier": "document",
                    # Urgency/Feelings
                    "peur": "anxiete",
                    "stress": "anxiete",
                    "inquiet": "anxiete",
                    "angoisse": "anxiete",
                    "grave": "urgence",
                    "urgent": "urgence",
                    "vite": "urgence",
                    "maintenant": "urgence",
                    "secours": "urgence",
                    "aide": "urgence",
                }

            # Basic greetings
            if any(word in user_message.split() for word in ['bonjour', 'salut', 'hello', 'bonsoir', 'hi', 'hola', 'buenos', 'dias']):
                 return JsonResponse({'response': greeting_response})

            # Simple keyword matching
            best_match = None
            max_score = 0

            for item in current_faqs:
                question = normalize_text(item['q'])
                
                user_words = user_message.split()
                # Apply synonyms
                user_words = [synonyms.get(w, w) for w in user_words]
                user_words_set = set(user_words)
                
                question_words = set(question.split())
                
                # 1. Exact matches
                common_words = user_words_set.intersection(question_words)
                meaningful_matches = [w for w in common_words if w not in stop_words and len(w) > 2]
                score = len(meaningful_matches) * 30  # FAQs are prioritized (30pts per word)
                
                # 2. Fuzzy matches (handle typos)
                for u_word in user_words_set:
                    if u_word in stop_words or u_word in common_words or len(u_word) < 3:
                        continue
                    # Find close matches in question words
                    matches = difflib.get_close_matches(u_word, question_words, n=1, cutoff=0.85)
                    if matches:
                        score += 15 # Fuzzy match bonus

                # 3. Coverage bonus (prioritize questions where a larger portion of the question is matched)
                question_meaningful_words = [w for w in question_words if w not in stop_words and len(w) > 2]
                if question_meaningful_words:
                    coverage = len(meaningful_matches) / len(question_meaningful_words)
                    score += coverage * 10

                # 4. Sequence Matcher (Sentence similarity)
                # This helps when the user asks a question very similar to the FAQ title
                seq_ratio = difflib.SequenceMatcher(None, normalize_text(user_message), question).ratio()
                if seq_ratio > 0.5:
                    score += seq_ratio * 30  # Big bonus for sentence similarity
                
                if score > max_score:
                    max_score = score
                    best_match = item['a']
            
            # Search in site content (Exams, Pathologies, Guides, Blog) - Mainly for French context or universal terms
            site_content = []
            for exam in EXAMS:
                keywords = [
                    exam['title'],
                    exam.get('description', ''),
                    " ".join(exam.get('indications', [])),
                    exam.get('preparation', ''),
                    exam.get('procedure', ''),
                    exam.get('aftercare', ''),
                    " ".join(exam.get('risks', []))
                ]
                site_content.append({'type': 'examen', 'title': exam['title'], 'url': f"/examens/{exam['slug']}", 'keywords': " ".join(keywords)})
            
            for path in PATHOLOGIES:
                keywords = [
                    path['title'],
                    path.get('summary', ''),
                    " ".join(path.get('symptoms', [])),
                    " ".join(path.get('tags', [])),
                    " ".join(path.get('treatments', [])),
                    " ".join(path.get('advice', [])),
                    " ".join(path.get('prevention', [])),
                    " ".join(path.get('exams', []))
                ]
                site_content.append({'type': 'pathologie', 'title': path['title'], 'url': f"/pathologies/{path['slug']}", 'keywords': " ".join(keywords)})
            
            for guide in GUIDES:
                keywords = [
                    guide['title'],
                    guide.get('summary', ''),
                    " ".join(guide.get('steps', []))
                ]
                site_content.append({'type': 'guide', 'title': guide['title'], 'url': f"/guides/#{guide['slug']}", 'keywords': " ".join(keywords)})
            
            for post in BLOG_POSTS:
                site_content.append({'type': 'article', 'title': post['title'], 'url': f"/blog/{post['slug']}", 'keywords': post['title'] + " " + post.get('excerpt', '') + " " + post.get('content', '')})

            # Add PDF documents from RAG folder
            pdf_docs = load_pdf_content()
            site_content.extend(pdf_docs)

            for item in site_content:
                content_text = normalize_text(item['keywords'])
                
                # Reuse scoring logic (simplified)
                user_words = user_message.split()
                # Expand synonyms instead of replacing
                expanded_words = set(user_words)
                for w in user_words:
                    if w in synonyms:
                        expanded_words.add(synonyms[w])
                user_words_set = expanded_words
                
                content_words = set(content_text.split())
                
                common_words = user_words_set.intersection(content_words)
                meaningful_matches = [w for w in common_words if w not in stop_words and len(w) > 2]
                score = len(meaningful_matches) * 10
                
                # Sequence match on title
                seq_ratio = difflib.SequenceMatcher(None, normalize_text(user_message), normalize_text(item['title'])).ratio()
                if seq_ratio > 0.6:
                    score += seq_ratio * 25

                if score > max_score:
                    max_score = score
                    best_match = f"Je vous suggère de consulter notre fiche {item['type']} sur '{item['title']}'. <br><a href='{item['url']}'>Cliquez ici pour voir la page</a>."

            print(f"Best match score: {max_score}")

            response_data = {}
            
            if best_match and max_score >= 5: # Minimum score threshold
                response_data['response'] = best_match
            elif best_match and max_score > 0:
                 response_data['response'] = best_match
            else:
                # Fallback to contact info if no match
                response_data['response'] = fallback_response

            # Check if medical query to suggest OpenEvidence
            medical_keywords = {
                'maladie', 'traitement', 'symptome', 'douleur', 'cancer', 'examen', 'medicament', 'effets', 'risques',
                'disease', 'treatment', 'symptom', 'pain', 'exam', 'drug', 'risk',
                'enfermedad', 'tratamiento', 'sintoma', 'dolor', 'examen', 'riesgo',
                'crohn', 'rch', 'rectocolite', 'hepatite', 'cirrhose', 'ulcere', 'polype', 'diverticule',
                'coloscopie', 'gastroscopie', 'endoscopie'
            }
            
            # Always suggest OpenEvidence for medical queries to allow complementary info
            if any(kw in user_message for kw in medical_keywords):
                response_data['suggest_openevidence'] = True
                
            return JsonResponse(response_data)

        except Exception as e:
            print(e)
            return JsonResponse({'response': "Une erreur est survenue."}, status=500)
    
    return JsonResponse({'error': 'Invalid request'}, status=400)

