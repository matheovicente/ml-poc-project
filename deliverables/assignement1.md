# Assignment 1 - Projet de validation de concept ML

## Sujet du projet

Mon projet porte sur l'analyse de l'importance stratégique des détroits maritimes mondiaux et sur la simulation de l'impact potentiel d'une fermeture temporaire de certains passages critiques.

L'objectif est d'étudier comment une fermeture de détroit, par exemple le détroit d'Ormuz, le détroit de Malacca ou le détroit de Taïwan, pourrait affecter le trafic maritime observé sur les autres grands chokepoints mondiaux.

## Business case

Le transport maritime est essentiel au commerce international. Certains détroits concentrent une part importante des flux de marchandises, d'énergie et de matières premières. Une perturbation sur ces zones peut donc avoir des conséquences économiques importantes : ralentissement des chaînes logistiques, hausse des coûts de transport, tension sur l'approvisionnement énergétique ou réorganisation temporaire des routes maritimes.

Le business case du projet est de construire un outil d'aide à l'analyse permettant de :

- classer les détroits selon leur criticité ;
- identifier les détroits les plus sensibles en cas de fermeture ;
- simuler des scénarios de fermeture sur 14, 30 et 90 jours ;
- observer quels autres détroits pourraient voir leur trafic augmenter ou diminuer ;
- comparer plusieurs modèles de prévision du trafic normal.

Ce projet peut être utile pour une entreprise de transport maritime, un assureur, un analyste risque, un acteur de la logistique ou une institution qui souhaite mieux comprendre les risques liés aux chokepoints maritimes.

## Dataset utilisé

Le projet utilise des données publiques issues de PortWatch, une plateforme qui fournit des indicateurs de trafic maritime à partir de données AIS.

Le dataset contient des observations journalières par détroit maritime. Il inclut notamment :

- la date d'observation ;
- le nom du chokepoint maritime ;
- le nombre total de navires observés ;
- le nombre de tankers ;
- le nombre de cargos ;
- le nombre de navires passagers ;
- d'autres indicateurs liés au trafic maritime.

Dans la version actuelle du projet, le dataset contient environ 74 000 observations et couvre 28 détroits ou chokepoints mondiaux, dont le détroit d'Ormuz, le détroit de Malacca, le détroit de Taïwan, le détroit de Corée et le détroit de Bohai.

## Approche ML envisagée

Le projet combine plusieurs approches :

1. Construction d'un score de criticité des détroits à partir de variables comme le volume moyen de trafic, la part de tankers et la volatilité du trafic.
2. Classification des détroits selon leur niveau de criticité.
3. Entraînement de modèles de machine learning pour comparer leur capacité à reproduire cette classification.
4. Modélisation de séries temporelles avec SARIMAX pour prévoir le trafic normal.
5. Simulation de scénarios de fermeture afin d'observer les effets potentiels sur les autres détroits.
