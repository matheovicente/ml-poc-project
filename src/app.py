from __future__ import annotations

import pandas as pd
import streamlit as st

from config import MONTHLY_FEATURES_PATH, PLOTS_DIR, RESULTS_DIR, SUMMARY_FEATURES_PATH


def _load_csv(path):
    if path.exists():
        return pd.read_csv(path)
    return pd.DataFrame()


def build_app() -> None:
    st.set_page_config(page_title="Criticité des détroits maritimes", layout="wide")
    st.title("Criticité des chokepoints maritimes mondiaux")

    st.markdown(
        """
        Ce projet classe les grands détroits et chokepoints maritimes selon leur
        criticité potentielle en cas de fermeture. L'analyse utilise les données
        journalières PortWatch : trafic total, tankers, capacités et perturbations
        détectées automatiquement.
        """
    )

    summary = _load_csv(SUMMARY_FEATURES_PATH)
    monthly = _load_csv(MONTHLY_FEATURES_PATH)
    metrics = _load_csv(RESULTS_DIR / "model_metrics.csv")
    simulation_summary = _load_csv(RESULTS_DIR / "closure_simulation_summary.csv")
    ts_metrics = _load_csv(RESULTS_DIR / "time_series_backtest_metrics_aggregated.csv")

    if summary.empty:
        st.warning("Les fichiers traités ne sont pas encore disponibles. Lancez `python scripts/main.py`.")
        return

    st.subheader("Classement des chokepoints")
    ranking_cols = [
        "portname",
        "criticality_score",
        "criticality_class",
        "mean_n_total",
        "mean_n_tanker",
        "tanker_share",
        "mean_capacity",
        "mean_capacity_tanker",
        "disruption_frequency_total",
    ]
    st.dataframe(
        summary[ranking_cols].sort_values("criticality_score", ascending=False),
        use_container_width=True,
    )

    col1, col2 = st.columns(2)
    with col1:
        path = PLOTS_DIR / "criticality_ranking.png"
        if path.exists():
            st.image(str(path), caption="Score de criticité par chokepoint")
    with col2:
        path = PLOTS_DIR / "tanker_capacity_by_chokepoint.png"
        if path.exists():
            st.image(str(path), caption="Capacité tanker moyenne")

    col3, col4 = st.columns(2)
    with col3:
        path = PLOTS_DIR / "traffic_by_chokepoint.png"
        if path.exists():
            st.image(str(path), caption="Trafic moyen")
    with col4:
        path = PLOTS_DIR / "disruption_frequency.png"
        if path.exists():
            st.image(str(path), caption="Fréquence de perturbation")

    st.subheader("Comparaison des modèles")
    if not metrics.empty:
        st.dataframe(metrics, use_container_width=True)
        path = PLOTS_DIR / "model_comparison.png"
        if path.exists():
            st.image(str(path), caption="F1 macro par modèle")
    else:
        st.info("Aucune métrique de modèle trouvée pour le moment.")

    st.subheader("Simulation de fermeture")
    selected = st.selectbox(
        "Choisir un chokepoint",
        summary.sort_values("portname")["portname"].tolist(),
        index=summary.sort_values("portname")["portname"].tolist().index("Strait of Hormuz")
        if "Strait of Hormuz" in summary["portname"].tolist()
        else 0,
    )
    duration = st.select_slider("Durée de fermeture", options=[7, 14, 30], value=14)
    row = summary.loc[summary["portname"] == selected].iloc[0]

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Navires affectés", f"{row[f'estimated_{duration}d_lost_vessels']:.0f}")
    c2.metric("Tankers affectés", f"{row[f'estimated_{duration}d_lost_tankers']:.0f}")
    c3.metric("Capacité totale affectée", f"{row[f'estimated_{duration}d_lost_capacity']:,.0f}")
    c4.metric("Capacité tanker affectée", f"{row[f'estimated_{duration}d_lost_tanker_capacity']:,.0f}")

    st.subheader("Scénarios de fermeture avec report partiel")
    if simulation_summary.empty:
        st.info("Lancez `python scripts/simulate_closures.py` pour générer les scénarios détaillés.")
    else:
        st.caption(
            "Hypothèse V1 : le détroit fermé passe à zéro trafic. Une part du trafic perdu "
            "est redistribuée vers des routes alternatives plausibles ; ce taux dépend du chokepoint fermé."
        )
        st.dataframe(
            simulation_summary.sort_values(
                ["duration_days", "lost_vessels_closed"],
                ascending=[True, False],
            ),
            use_container_width=True,
        )
        sim_closed = st.selectbox(
            "Graphique de scénario",
            simulation_summary["closed_chokepoint"].drop_duplicates().tolist(),
        )
        sim_duration = st.select_slider("Durée du scénario", options=[14, 30, 90], value=30)
        safe_name = sim_closed.lower().replace(" ", "_").replace("/", "_").replace("-", "_")
        sim_plot = PLOTS_DIR / "closure_simulations" / f"{safe_name}_{sim_duration}d_n_total_focus.png"
        if sim_plot.exists():
            st.image(str(sim_plot), caption=f"Fermeture de {sim_closed} pendant {sim_duration} jours")
        else:
            st.warning("Graphique de simulation introuvable pour cette combinaison.")

    st.subheader("Fiabilité des séries temporelles")
    if ts_metrics.empty:
        st.info("Lancez `python scripts/backtest_timeseries.py` pour générer les métriques de backtest.")
    else:
        st.caption(
            "Le backtest compare une prévision de trafic normal aux observations réelles passées. "
            "La fermeture reste un scénario contrefactuel, mais les modèles analog et SARIMAX sont testables."
        )
        st.dataframe(ts_metrics, use_container_width=True)
        selected_bt = st.selectbox(
            "Exemple de backtest",
            ts_metrics["portname"].drop_duplicates().tolist(),
        )
        bt_horizon = st.select_slider("Horizon backtest", options=[14, 30, 90], value=30)
        safe_bt = selected_bt.lower().replace(" ", "_").replace("/", "_").replace("-", "_")
        bt_plot = PLOTS_DIR / "backtests" / f"{safe_bt}_{bt_horizon}d_backtest.png"
        if bt_plot.exists():
            st.image(str(bt_plot), caption=f"Backtest {selected_bt}, horizon {bt_horizon} jours")

    st.subheader("Focus Ormuz")
    hormuz = summary[summary["portname"] == "Strait of Hormuz"]
    if not hormuz.empty:
        h = hormuz.iloc[0]
        st.markdown(
            f"""
            Le détroit d'Ormuz obtient un score de criticité de
            **{h['criticality_score']:.1f}/100**. Son importance vient surtout de
            son exposition aux tankers : **{h['mean_n_tanker']:.1f} tankers par jour**
            en moyenne et une capacité tanker moyenne de
            **{h['mean_capacity_tanker']:,.0f}**.
            """
        )

    with st.expander("Aperçu du dataset mensuel utilisé par le ML"):
        st.dataframe(monthly.head(200), use_container_width=True)


if __name__ == "__main__":
    build_app()
