# Assignment 3 - Features et target engineering

Une observation ML correspond à un couple `chokepoint x mois`.

Features principales :

- `mean_n_total`
- `cv_n_total`
- `mean_n_tanker`
- `tanker_share`
- `mean_capacity`
- `mean_capacity_tanker`
- `disruption_frequency_total`
- `disruption_frequency_tanker`

La cible `criticality_class` est construite à partir d'un score transparent
combinant volume total, capacité, capacité tanker, part des tankers et fréquence
des perturbations.

