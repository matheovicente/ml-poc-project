# Assignment 3 - Description et comparaison des modeles

## Objectif de modelisation

Le projet est un probleme de classification binaire. Le modele doit predire si le prix de l'essence reguliere aux Etats-Unis va augmenter la semaine suivante.

La cible est :

```text
target_price_up_1w
```

## Split temporel

Les donnees sont separees chronologiquement. Les observations anciennes servent a entrainer les modeles, et les observations recentes servent a les tester.

Ce choix est important car le projet utilise des series temporelles. Un split aleatoire pourrait melanger le passe et le futur et donner une evaluation trop optimiste.

## Modele 1 - Logistic Regression

La Logistic Regression est le modele lineaire de reference.

Elle est utile car :

- elle est interpretable ;
- elle fonctionne bien avec peu de donnees ;
- elle donne un bon baseline ;
- elle permet de comprendre quelles variables poussent la prediction vers une hausse.

Dans ce projet, elle obtient le meilleur compromis global.

## Modele 2 - Random Forest

Le Random Forest est un ensemble d'arbres de decision.

Il est utile car :

- il peut capturer des relations non lineaires ;
- il gere bien les interactions entre variables ;
- il est robuste aux variables bruitees.

Sa limite principale est qu'il peut etre moins stable lorsque le dataset est relativement petit.

## Modele 3 - Gradient Boosting

Le Gradient Boosting est aussi base sur des arbres, mais les arbres sont ajoutes progressivement pour corriger les erreurs precedentes.

Il est utile car :

- il capte des relations non lineaires ;
- il peut fournir de bonnes performances predictives ;
- il obtient ici le meilleur ROC AUC.

Sa limite est le risque de sur-apprentissage lorsque le nombre d'observations est limite.

## Metriques utilisees

Les metriques calculees sont :

- accuracy ;
- balanced accuracy ;
- F1-score ;
- precision ;
- recall ;
- ROC AUC.

Le F1-score et la balanced accuracy sont privilegies car ils evaluent l'equilibre entre les deux classes. La precision est aussi importante car une alerte de hausse doit etre suffisamment fiable.

## Resultats

| Modele | Accuracy | Balanced accuracy | F1-score | Precision | Recall | ROC AUC |
|---|---:|---:|---:|---:|---:|---:|
| Logistic Regression | 0.658 | 0.661 | 0.618 | 0.724 | 0.538 | 0.728 |
| Random Forest | 0.632 | 0.635 | 0.588 | 0.690 | 0.513 | 0.719 |
| Gradient Boosting | 0.645 | 0.648 | 0.609 | 0.700 | 0.538 | 0.730 |

## Conclusion

La Logistic Regression est retenue comme meilleur modele principal car elle obtient les meilleurs scores sur l'accuracy, la balanced accuracy, le F1-score et la precision.

Le Gradient Boosting obtient un ROC AUC legerement superieur, mais la Logistic Regression est plus lisible, plus stable et mieux adaptee a un dataset hebdomadaire de taille limitee.

## Modeles sauvegardes

Les modeles entraines sont disponibles dans le dossier :

```text
models/
```

Fichiers :

- `models/log_reg.joblib` ;
- `models/random_forest.joblib` ;
- `models/gradient_boosting.joblib`.
