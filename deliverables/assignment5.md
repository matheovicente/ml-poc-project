# Assignment 5 - Application Streamlit

## Objectif de l'application

L'application Streamlit sert a presenter le projet de maniere interactive. Elle permet de visualiser les donnees, de comparer les modeles et de tester un scenario simple de prediction.

Le fichier principal est :

```text
src/app.py
```

La fonction attendue par le template est conservee :

```python
def build_app() -> None:
```

## Onglet Overview

Cet onglet presente :

- le nombre d'observations hebdomadaires ;
- la periode couverte ;
- le taux de semaines avec hausse du prix ;
- le dernier prix de l'essence disponible.

Il affiche aussi les graphiques :

- prix essence vs Brent ;
- trafic tanker autour des chokepoints.

Un tableau de correlation permet d'identifier les relations principales entre les variables.

## Onglet Models

Cet onglet compare les trois modeles :

- Logistic Regression ;
- Random Forest ;
- Gradient Boosting.

Il affiche :

- le meilleur modele selon le F1-score ;
- les metriques principales ;
- le graphique de comparaison des modeles ;
- les importances de variables.

## Onglet Interactive simulator

Cet onglet permet de modifier manuellement certains signaux :

- variation hebdomadaire du Brent ;
- niveau de stress maritime ;
- momentum du prix de l'essence.

L'application affiche ensuite la prediction de chaque modele : hausse ou non-hausse du prix de l'essence la semaine suivante.

## Onglet Data

Cet onglet permet de consulter le dataset preprocessé et de le telecharger en CSV.

## Lancement

Depuis la racine du projet :

```bash
python scripts/main.py
```

ou directement :

```bash
python -m streamlit run src/app.py
```

L'application est disponible localement sur :

```text
http://localhost:8501
```
