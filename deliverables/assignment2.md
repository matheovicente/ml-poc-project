# Assignment 2 - Feature engineering et dataset preprocessé

## Objectif du feature engineering

L'objectif du feature engineering est de transformer des series brutes en signaux exploitables par les modeles.

Le projet ne se limite pas a utiliser les niveaux bruts des prix ou du trafic. Il cree aussi des variations, des moyennes mobiles, des lags et des indicateurs de saisonnalite pour representer la dynamique du marche.

## Construction du dataset final

Les donnees PortWatch sont quotidiennes, alors que le prix de l'essence FRED est hebdomadaire. La premiere transformation consiste donc a agreger le trafic maritime a la semaine avec une frequence `W-MON`.

Les donnees sont ensuite fusionnees sur la colonne `date` :

- trafic tanker hebdomadaire ;
- prix de l'essence ;
- prix du Brent ;
- indice du dollar lorsque disponible.

Le dataset final est sauvegarde dans :

```text
data/processed/pump_price_dataset.csv
```

## Features sur le Brent et le prix a la pompe

Les variables de prix sont transformees en rendements afin de capturer les mouvements recents :

- `brent_return_1w` : variation du Brent sur 1 semaine ;
- `brent_return_4w` : variation du Brent sur 4 semaines ;
- `brent_vol_4w` : volatilite du Brent sur 4 semaines ;
- `pump_return_1w` : variation du prix de l'essence sur 1 semaine ;
- `pump_return_4w` : variation du prix de l'essence sur 4 semaines.

Des lags sont ajoutes pour donner de la memoire au modele :

- `brent_return_1w_lag1` ;
- `brent_return_1w_lag2` ;
- `pump_return_1w_lag1` ;
- `pump_return_1w_lag2`.

Ces variables permettent de tester si les mouvements passes du Brent et de l'essence aident a predire la hausse future du prix a la pompe.

## Features de trafic maritime

Pour chaque chokepoint maritime, le dataset conserve le nombre de tankers :

- `strait_of_hormuz_n_tanker` ;
- `bab_el_mandeb_strait_n_tanker` ;
- `suez_canal_n_tanker` ;
- `malacca_strait_n_tanker`.

Pour chaque serie de trafic, plusieurs transformations sont creees :

- `ma4` : moyenne mobile sur 4 semaines ;
- `ma12` : moyenne mobile sur 12 semaines ;
- `std4` : ecart-type sur 4 semaines ;
- `ratio12` : trafic actuel divise par la moyenne mobile 12 semaines ;
- `lag1`, `lag2`, `lag4` : valeurs retardees du trafic.

Le `ratio12` sert a detecter si le trafic actuel est normal ou anormal par rapport a la tendance recente.

## Indice de stress maritime

L'indice `maritime_stress` est construit a partir des ratios de trafic des grands points de passage.

Pour chaque detroit :

```text
ratio12 = trafic actuel / moyenne mobile 12 semaines
stress = 1 - ratio12
```

Les ratios sont limites entre 0 et 2 pour eviter que des valeurs extremes dominent trop l'indice. Ensuite, le stress maritime est la moyenne des stress par detroit.

Un stress positif signifie que le trafic tanker est plus faible que sa tendance recente, ce qui peut signaler une tension logistique.

## Features temporelles

Des variables calendaires sont ajoutees :

- `month` : mois de l'annee ;
- `week_of_year` : numero de semaine ;
- `is_driving_season` : periode mai-aout, ou la demande routiere peut etre plus forte ;
- `is_winter` : periode decembre-fevrier.

Ces variables permettent de capturer la saisonnalite du prix de l'essence.

## Target

La cible finale est :

```text
target_price_up_1w
```

Elle vaut `1` si le prix de l'essence augmente la semaine suivante, et `0` sinon.

Le dataset contient aussi `target_return_1w`, qui correspond a la variation future du prix de l'essence sur une semaine.
