# Assignment 1 - Pump Price Prediction

## Project Topic

The project predicts whether the US regular gasoline price will increase the following week.

The goal is to test whether maritime tanker traffic around strategic chokepoints, especially the Strait of Hormuz, can add predictive signal to oil-market variables such as Brent crude oil prices.

## Business Case

Gasoline prices are important for households, logistics companies, retailers and public institutions. Short-term movements in pump prices can affect budgets, operating costs and pricing decisions.

The business case is to build a decision-support model that can:

- predict whether pump prices are likely to increase next week;
- compare the predictive power of Brent, gasoline momentum and maritime tanker traffic;
- identify whether chokepoint stress adds useful information;
- provide interpretable metrics and visualizations for non-technical users.

This project is relevant for energy analysts, logistics companies, transport operators and risk teams monitoring the impact of energy supply-chain stress.

## Dataset

The project combines public data sources:

- IMF PortWatch daily chokepoint traffic data;
- FRED weekly US regular gasoline price (`GASREGW`);
- FRED Brent crude oil price (`DCOILBRENTEU`);
- optional macro variables from FRED when available.

PortWatch is aggregated from daily to weekly frequency. The final dataset contains weekly observations with:

- pump price;
- Brent price and returns;
- tanker traffic around Hormuz, Bab el-Mandeb, Suez and Malacca;
- rolling averages and lagged features;
- a maritime stress indicator;
- the target variable: whether pump price increases the following week.

## ML Approach

The project uses three model families:

1. Logistic Regression.
2. Random Forest.
3. Gradient Boosting.

The train/test split is chronological to respect the time-series nature of the problem. Models are evaluated with accuracy, balanced accuracy, F1 score, precision, recall and ROC AUC.
