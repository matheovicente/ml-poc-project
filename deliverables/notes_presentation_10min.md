# Notes orales - Présentation 10 minutes

## Slide 1 - Titre
Présenter le projet comme un outil de simulation : on ne cherche pas à prédire la bourse ou le prix du pétrole, mais à comprendre l'impact opérationnel d'une fermeture de détroit maritime.

## Slide 2 - Problématique
Insister sur la question concrète : si un grand détroit ferme, quels autres détroits voient leur trafic changer ? L'objectif est de comparer plusieurs scénarios de fermeture de façon lisible.

## Slide 3 - Données
Expliquer que PortWatch fournit des données AIS journalières. Le dataset contient 28 chokepoints et plus de 74 000 observations. C'est une donnée opérationnelle, donc adaptée au sujet maritime.

## Slide 4 - Pipeline
Décrire le flux : nettoyage, création de variables, score de criticité, modèles ML, SARIMAX, puis simulation. Préciser que le projet travaille à un niveau agrégé par jour et par détroit.

## Slide 5 - Classement
Commenter les cinq premiers. Malacca domine par le volume et les tankers. Taiwan et Korea sont très fréquentés. Ormuz est moins élevé en volume total mais très stratégique à cause des tankers.

## Slide 6 - Fiabilité temporelle
Dire que SARIMAX sert à prévoir le trafic normal. Le résultat important est que SARIMAX réduit l'erreur moyenne d'environ 27 % par rapport à la baseline. Cela rend la baseline plus crédible pour simuler ensuite un choc.

## Slide 7 - Fermeture de Malacca
Lire le graphique : avant fermeture, trafic normal ; à la fermeture, le détroit tombe à zéro ; après, certaines routes alternatives augmentent. Malacca est un bon exemple de choc logistique majeur.

## Slide 8 - Fermeture d'Ormuz
Insister sur la différence avec Malacca : Ormuz a peu d'alternatives maritimes crédibles. La simulation ne montre donc pas une redistribution massive, mais plutôt un blocage très sensible sur le trafic énergétique.

## Slide 9 - Fermeture de Taiwan
Utiliser ce cas pour montrer que les effets sont surtout régionaux. Les détroits proches ou connectés sont les plus susceptibles de changer.

## Slide 10 - Conclusion
Conclusion principale : le projet produit un outil tangible, avec données, modèles, métriques, graphiques et application Streamlit. Limite principale : la redistribution repose sur des hypothèses métier simplifiées. Amélioration possible : intégrer les routes AIS réelles et les distances de détour.
