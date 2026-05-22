# Assignment 4 - Visualisations

## Objectif

Ce rendu presente les principales visualisations poussees sur GitHub. Elles permettent de comprendre les donnees, les variables explicatives et les performances des modeles.

## Plot 1 - Prix essence et Brent

Fichier :

```text
plots/pump_brent_timeseries.png
```

Ce graphique compare l'evolution du prix de l'essence a la pompe et du prix du Brent. Il montre que les deux series sont fortement liees, ce qui confirme l'importance du Brent dans la prediction.

## Plot 2 - Trafic tanker par chokepoint

Fichier :

```text
plots/tanker_traffic_timeseries.png
```

Ce graphique montre le trafic tanker autour des grands points de passage maritimes : Ormuz, Bab el-Mandeb, Suez et Malacca. Il sert a visualiser les variations et anomalies de flux maritime.

## Plot 3 - Comparaison des modeles

Fichier :

```text
plots/model_comparison.png
```

Ce graphique compare les performances des trois modeles sur plusieurs metriques. Il permet de voir rapidement que la Logistic Regression est le meilleur compromis global.

## Plot 4 - Importance des variables

Fichier :

```text
plots/feature_importance.png
```

Ce graphique montre quelles variables contribuent le plus a la prediction. Les variables liees au Brent et a la dynamique du prix de l'essence ressortent fortement.

## Plot 5 - Tableau des metriques

Fichier :

```text
plots/model_metrics_table_white.png
```

Ce tableau synthetise les metriques de chaque modele sur fond blanc afin de pouvoir etre utilise directement dans une presentation.

## Conclusion

Les visualisations montrent que :

- le Brent est une variable centrale ;
- le trafic maritime ajoute un signal de contexte logistique ;
- la Logistic Regression est le modele le plus coherent globalement ;
- les performances sont correctes mais pas parfaites, ce qui est normal pour une prediction court terme sur des prix energetiques.
