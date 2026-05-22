# Assignment 6 - README et guide de recuperation des donnees

## Objectif

Le README a ete modifie pour presenter clairement le projet au debut du depot GitHub.

Il contient :

- une description du projet ;
- le business case ;
- les sources de donnees ;
- la structure du depot ;
- les modeles utilises ;
- les commandes pour regenerer le projet ;
- les fichiers de sortie.

## Description ajoutee

Le projet est intitule :

```text
Pump Price Prediction
```

Il cherche a predire si le prix de l'essence reguliere aux Etats-Unis va augmenter la semaine suivante.

Le projet combine :

- donnees de prix de l'essence ;
- prix du Brent ;
- indice du dollar ;
- trafic maritime tanker autour de chokepoints strategiques.

## Guide de recuperation des donnees

Le README explique que le dataset final est construit avec :

- IMF PortWatch pour les donnees de trafic maritime ;
- FRED pour les series economiques et energetiques.

Les commandes principales sont :

```bash
pip install -r requirements.txt
python scripts/prepare_data.py
python scripts/train_models.py
python scripts/main.py
```

## Fichiers importants

Dataset brut :

```text
data/raw/portwatch_daily_chokepoints.csv
```

Dataset preprocessé :

```text
data/processed/pump_price_dataset.csv
```

Modeles sauvegardes :

```text
models/log_reg.joblib
models/random_forest.joblib
models/gradient_boosting.joblib
```

Application :

```text
src/app.py
```

## Conclusion

Le README permet maintenant a un correcteur de comprendre rapidement le projet, de savoir quelles donnees sont utilisees et de relancer le pipeline complet.
