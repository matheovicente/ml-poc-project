from __future__ import annotations

from pathlib import Path

import pandas as pd
import streamlit as st

from config import MONTHLY_FEATURES_PATH, PLOTS_DIR, RESULTS_DIR, SUMMARY_FEATURES_PATH


CLASS_LABELS = {
    0: "Faible",
    1: "Moyenne",
    2: "Élevée",
    3: "Extrême",
}


def _load_csv(path: Path) -> pd.DataFrame:
    if path.exists():
        return pd.read_csv(path)
    return pd.DataFrame()


def _safe_name(name: str) -> str:
    return name.lower().replace(" ", "_").replace("/", "_").replace("-", "_")


def _metric_card(label: str, value: str, help_text: str | None = None) -> None:
    st.metric(label, value, help=help_text)


def _show_image(path: Path, caption: str) -> None:
    if path.exists():
        st.image(str(path), caption=caption, use_column_width=True)
    else:
        st.info(f"Graphique non trouvé : `{path.name}`")


def _format_summary(summary: pd.DataFrame) -> pd.DataFrame:
    cols = [
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
    available = [col for col in cols if col in summary.columns]
    frame = summary[available].copy()
    if "criticality_class" in frame.columns:
        frame["criticality_label"] = frame["criticality_class"].map(CLASS_LABELS)
    for col in frame.select_dtypes("number").columns:
        frame[col] = frame[col].round(3)
    return frame


def build_app() -> None:
    st.set_page_config(
        page_title="Maritime Chokepoint Risk",
        page_icon="🌊",
        layout="wide",
    )

    st.markdown(
        """
        <style>
        .block-container {padding-top: 1.6rem; padding-bottom: 2rem;}
        .small-note {color: #64748b; font-size: 0.92rem;}
        .section-title {font-size: 1.35rem; font-weight: 700; margin-top: 0.4rem;}
        </style>
        """,
        unsafe_allow_html=True,
    )

    summary = _load_csv(SUMMARY_FEATURES_PATH)
    monthly = _load_csv(MONTHLY_FEATURES_PATH)
    metrics = _load_csv(RESULTS_DIR / "model_metrics.csv")
    training_metrics = _load_csv(RESULTS_DIR / "training_model_metrics.csv")
    cv_results = _load_csv(RESULTS_DIR / "training_cv_results.csv")
    feature_importance = _load_csv(RESULTS_DIR / "feature_importance.csv")
    simulation_summary = _load_csv(RESULTS_DIR / "closure_simulation_summary.csv")
    ts_metrics = _load_csv(RESULTS_DIR / "time_series_backtest_metrics_aggregated.csv")

    st.title("Maritime Chokepoint Risk")
    st.caption(
        "Classement de criticité, modèles ML et simulations de fermeture sur les grands détroits maritimes."
    )

    if summary.empty:
        st.warning(
            "Les données préparées ne sont pas disponibles. Lance `python scripts/prepare_data.py`, "
            "puis `python scripts/train_models.py`."
        )
        return

    top_summary = summary.sort_values("criticality_score", ascending=False).reset_index(drop=True)
    top_row = top_summary.iloc[0]
    hormuz = summary[summary["portname"].eq("Strait of Hormuz")]

    k1, k2, k3, k4 = st.columns(4)
    with k1:
        _metric_card("Chokepoints analysés", f"{summary['portname'].nunique():.0f}")
    with k2:
        _metric_card("Observations ML", f"{len(monthly):,}".replace(",", " "))
    with k3:
        _metric_card("Plus critique", str(top_row["portname"]), f"Score : {top_row['criticality_score']:.1f}/100")
    with k4:
        if not hormuz.empty:
            h = hormuz.iloc[0]
            _metric_card("Ormuz", f"{h['criticality_score']:.1f}/100", "Score de criticité")
        else:
            _metric_card("Ormuz", "Absent")

    tab_overview, tab_models, tab_scenarios, tab_timeseries, tab_data = st.tabs(
        [
            "Vue d'ensemble",
            "Modèles",
            "Scénarios",
            "Séries temporelles",
            "Données",
        ]
    )

    with tab_overview:
        left, right = st.columns([1.25, 1])
        with left:
            st.markdown('<div class="section-title">Classement de criticité</div>', unsafe_allow_html=True)
            class_filter = st.multiselect(
                "Filtrer par classe de criticité",
                options=[0, 1, 2, 3],
                default=[0, 1, 2, 3],
                format_func=lambda value: f"{value} - {CLASS_LABELS[value]}",
            )
            table = _format_summary(top_summary[top_summary["criticality_class"].isin(class_filter)])
            st.dataframe(table, use_container_width=True, hide_index=True)

        with right:
            st.markdown('<div class="section-title">Lecture business</div>', unsafe_allow_html=True)
            st.markdown(
                """
                - Le score combine volume, capacité, exposition tanker et perturbations.
                - Malacca ressort par son volume et son exposition tanker.
                - Ormuz reste stratégique même avec moins de trafic total, car il concentre des flux énergétiques.
                - Les classes sont utiles pour comparer les détroits, pas pour affirmer une vérité géopolitique absolue.
                """
            )

        c1, c2 = st.columns(2)
        with c1:
            _show_image(PLOTS_DIR / "criticality_ranking.png", "Score de criticité par chokepoint")
        with c2:
            _show_image(PLOTS_DIR / "traffic_by_chokepoint.png", "Trafic moyen journalier")

        c3, c4 = st.columns(2)
        with c3:
            _show_image(PLOTS_DIR / "tanker_capacity_by_chokepoint.png", "Capacité tanker moyenne")
        with c4:
            _show_image(PLOTS_DIR / "disruption_frequency.png", "Fréquence de perturbation détectée")

    with tab_models:
        st.markdown('<div class="section-title">Performance des modèles</div>', unsafe_allow_html=True)
        if metrics.empty:
            st.info("Aucune métrique disponible. Lance `python scripts/main.py` pour régénérer les évaluations.")
        else:
            best = metrics.sort_values("f1_macro", ascending=False).iloc[0]
            m1, m2, m3 = st.columns(3)
            with m1:
                _metric_card("Meilleur modèle", str(best["model_name"]))
            with m2:
                _metric_card("F1 macro", f"{best['f1_macro']:.3f}")
            with m3:
                _metric_card("Balanced accuracy", f"{best['balanced_accuracy']:.3f}")

            display_metrics = metrics.copy()
            numeric_cols = display_metrics.select_dtypes("number").columns
            display_metrics[numeric_cols] = display_metrics[numeric_cols].round(4)
            st.dataframe(display_metrics, use_container_width=True, hide_index=True)
            _show_image(PLOTS_DIR / "model_comparison.png", "Comparaison multi-métriques des modèles")

        if not training_metrics.empty:
            with st.expander("Détails de l'entraînement optimisé"):
                tm = training_metrics.copy()
                numeric_cols = tm.select_dtypes("number").columns
                tm[numeric_cols] = tm[numeric_cols].round(4)
                st.dataframe(tm, use_container_width=True, hide_index=True)

        if not cv_results.empty:
            with st.expander("Top configurations de validation croisée"):
                cv = cv_results.copy()
                numeric_cols = cv.select_dtypes("number").columns
                cv[numeric_cols] = cv[numeric_cols].round(4)
                st.dataframe(cv, use_container_width=True, hide_index=True)

        if not feature_importance.empty:
            st.markdown('<div class="section-title">Variables les plus utiles</div>', unsafe_allow_html=True)
            model_options = feature_importance["model_key"].drop_duplicates().tolist()
            selected_model = st.selectbox(
                "Modèle pour l'importance des variables",
                model_options,
                index=model_options.index("gradient_boosting") if "gradient_boosting" in model_options else 0,
            )
            fi = (
                feature_importance[feature_importance["model_key"].eq(selected_model)]
                .sort_values("importance", ascending=False)
                .head(15)
                .copy()
            )
            fi["importance"] = fi["importance"].round(5)
            st.dataframe(fi, use_container_width=True, hide_index=True)
            _show_image(PLOTS_DIR / "feature_importance.png", "Importance des variables du Gradient Boosting")

    with tab_scenarios:
        st.markdown('<div class="section-title">Simulation de fermeture</div>', unsafe_allow_html=True)
        st.markdown(
            '<p class="small-note">La simulation est contrefactuelle : elle compare une trajectoire normale à un choc de fermeture.</p>',
            unsafe_allow_html=True,
        )

        if simulation_summary.empty:
            st.info("Lance `python scripts/simulate_closures.py --top-n 5 --durations 14 30 90`.")
        else:
            closed_options = simulation_summary["closed_chokepoint"].drop_duplicates().tolist()
            duration_options = sorted(simulation_summary["duration_days"].drop_duplicates().tolist())
            c1, c2 = st.columns([2, 1])
            with c1:
                closed = st.selectbox("Détroit fermé", closed_options)
            with c2:
                duration = st.selectbox("Durée", duration_options, index=duration_options.index(90) if 90 in duration_options else 0)

            row = simulation_summary[
                simulation_summary["closed_chokepoint"].eq(closed)
                & simulation_summary["duration_days"].eq(duration)
            ]
            if not row.empty:
                r = row.iloc[0]
                s1, s2, s3, s4 = st.columns(4)
                with s1:
                    _metric_card("Navires perdus", f"{r['lost_vessels_closed']:.0f}")
                with s2:
                    _metric_card("Tankers perdus", f"{r['lost_tankers_closed']:.0f}")
                with s3:
                    _metric_card("Redistribution", f"{r['redistributed_vessels_to_others']:.0f}")
                with s4:
                    _metric_card("Taux redistribué", f"{r['redistribution_rate']:.0%}")

            safe = _safe_name(closed)
            _show_image(
                PLOTS_DIR / "closure_simulations" / f"{safe}_{duration}d_n_total_focus.png",
                f"Scénario focus : fermeture de {closed} pendant {duration} jours",
            )

            with st.expander("Table complète des scénarios"):
                ss = simulation_summary.copy()
                numeric_cols = ss.select_dtypes("number").columns
                ss[numeric_cols] = ss[numeric_cols].round(3)
                st.dataframe(ss, use_container_width=True, hide_index=True)

    with tab_timeseries:
        st.markdown('<div class="section-title">Fiabilité des prévisions de trafic normal</div>', unsafe_allow_html=True)
        if ts_metrics.empty:
            st.info("Lance `python scripts/backtest_timeseries.py --top-n 5 --horizons 14 30 90 --models analog sarimax`.")
        else:
            ts = ts_metrics.copy()
            numeric_cols = ts.select_dtypes("number").columns
            ts[numeric_cols] = ts[numeric_cols].round(3)
            st.dataframe(ts, use_container_width=True, hide_index=True)

            port_options = ts["portname"].drop_duplicates().tolist()
            horizon_options = sorted(ts["horizon_days"].drop_duplicates().tolist())
            c1, c2 = st.columns([2, 1])
            with c1:
                port = st.selectbox("Détroit à afficher", port_options)
            with c2:
                horizon = st.selectbox("Horizon", horizon_options, index=horizon_options.index(90) if 90 in horizon_options else 0)

            _show_image(
                PLOTS_DIR / "backtests" / f"{_safe_name(port)}_{horizon}d_backtest.png",
                f"Backtest {port}, horizon {horizon} jours",
            )

            if {"model", "mae"}.issubset(ts_metrics.columns):
                pivot = ts_metrics.pivot_table(index="model", values="mae", aggfunc="mean").sort_values("mae")
                best_ts = pivot.index[0]
                st.success(
                    f"Sur les backtests disponibles, le modèle temporel avec la MAE moyenne la plus faible est `{best_ts}`."
                )

    with tab_data:
        st.markdown('<div class="section-title">Données et contrat du template</div>', unsafe_allow_html=True)
        st.markdown(
            """
            Le projet respecte les signatures attendues par le template :

            - `src/data.py` expose `load_dataset_split()`
            - `src/metrics.py` expose `compute_metrics(y_true, y_pred)`
            - `src/app.py` expose `build_app()`
            - `scripts/main.py` évalue les modèles et lance Streamlit
            """
        )
        st.write("Dataset mensuel utilisé par le ML")
        st.dataframe(monthly.head(250), use_container_width=True, hide_index=True)


if __name__ == "__main__":
    build_app()
