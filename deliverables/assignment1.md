# Assignment 1 - Explication du projet et des donnees

## Sujet du projet

Le projet cherche a predire si le prix de l'essence reguliere a la pompe aux Etats-Unis va augmenter la semaine suivante.

Il s'agit d'un probleme de classification binaire :

- `1` : le prix de l'essence augmente la semaine suivante ;
- `0` : le prix de l'essence n'augmente pas la semaine suivante.

## Interet business

Le prix de l'essence influence directement les couts de transport, les budgets des entreprises logistiques, les couts des menages et les decisions d'achat de carburant.

L'objectif business est donc de construire un signal d'alerte court terme. Le modele ne donne pas une certitude, mais il aide a anticiper un risque de hausse du prix de l'essence une semaine a l'avance.

Ce type d'outil peut etre utile pour :

- des transporteurs qui veulent anticiper leurs couts ;
- des entreprises dependantes du carburant ;
- des analystes energie ;
- des equipes de gestion des risques.

## Donnees utilisees

Le dataset final combine plusieurs sources publiques :

- IMF PortWatch : trafic quotidien des tankers autour de grands points de passage maritimes ;
- FRED `GASREGW` : prix hebdomadaire de l'essence reguliere aux Etats-Unis ;
- FRED `DCOILBRENTEU` : prix du Brent ;
- FRED `DTWEXBGS` : indice du dollar americain lorsque disponible.

Les points de passage maritimes retenus sont :

- Strait of Hormuz ;
- Bab el-Mandeb Strait ;
- Suez Canal ;
- Malacca Strait.

## Dataset final

Les donnees PortWatch sont agregees a la semaine afin d'etre alignees avec les prix hebdomadaires de l'essence.

Le dataset final se trouve dans :

```text
data/processed/pump_price_dataset.csv
```

Il contient des variables de prix, de rendements, de trafic maritime, de stress maritime, de saisonnalite et la cible de prediction `target_price_up_1w`.

## Approche machine learning

Trois modeles sont compares :

- Logistic Regression ;
- Random Forest ;
- Gradient Boosting.

L'evaluation respecte l'ordre temporel des donnees : les observations les plus anciennes servent a l'entrainement, et les plus recentes servent au test.
