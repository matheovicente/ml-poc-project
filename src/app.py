from __future__ import annotations

from pathlib import Path

import joblib
import pandas as pd
import streamlit as st

from config import FEATURES, MODELS, PLOTS_DIR, PROCESSED_DATA_PATH, RESULTS_DIR


def load_csv(path: Path) -> pd.DataFrame:
    if path.exists():
        return pd.read_csv(path, parse_dates=["date"] if "dataset" in path.name else None)
    return pd.DataFrame()


def show_image(path: Path, caption: str) -> None:
    if path.exists():
        st.image(str(path), caption=caption, use_column_width=True)
    else:
        st.info(f"Missing plot: `{path.name}`")


def build_app() -> None:
    st.set_page_config(page_title="Pump Price Prediction", page_icon="⛽", layout="wide")
    st.title("Pump Price Prediction")
    st.caption("Predicting next-week gasoline price direction with Brent and maritime tanker traffic.")

    df = load_csv(PROCESSED_DATA_PATH)
    metrics = load_csv(RESULTS_DIR / "model_metrics.csv")
    training_metrics = load_csv(RESULTS_DIR / "training_model_metrics.csv")
    feature_importance = load_csv(RESULTS_DIR / "feature_importance.csv")

    if df.empty:
        st.warning("Dataset not found. Run `python scripts/prepare_data.py` first.")
        return

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Weekly observations", f"{len(df):,}".replace(",", " "))
    k2.metric("Period", f"{df['date'].min().date()} → {df['date'].max().date()}")
    k3.metric("Target up rate", f"{df['target_price_up_1w'].mean():.1%}")
    k4.metric("Latest pump price", f"${df['pump_price'].iloc[-1]:.2f}/gal")

    tab_overview, tab_models, tab_simulator, tab_data = st.tabs(
        ["Overview", "Models", "Interactive simulator", "Data"]
    )

    with tab_overview:
        st.subheader("Business logic")
        st.markdown(
            """
            The model predicts whether the regular gasoline price will be higher next week.

            The main intuition is:

            - Brent is the strongest direct driver of pump prices.
            - Maritime tanker traffic can provide an additional supply-chain stress signal.
            - The prediction horizon is short because energy markets react quickly.
            """
        )
        c1, c2 = st.columns(2)
        with c1:
            show_image(PLOTS_DIR / "pump_brent_timeseries.png", "Gasoline price and Brent")
        with c2:
            show_image(PLOTS_DIR / "tanker_traffic_timeseries.png", "Tanker traffic around key chokepoints")

        corr_cols = [
            "pump_price",
            "pump_return_1w",
            "brent_price",
            "brent_return_1w",
            "maritime_stress",
            "strait_of_hormuz_n_tanker_ratio12",
            "target_return_1w",
        ]
        available_corr = [col for col in corr_cols if col in df.columns]
        st.subheader("Correlation snapshot")
        st.dataframe(df[available_corr].corr().round(3), use_container_width=True)

    with tab_models:
        st.subheader("Model comparison")
        if metrics.empty:
            st.info("Run `python scripts/main.py` or `python scripts/train_models.py` to generate metrics.")
        else:
            best = metrics.sort_values("f1", ascending=False).iloc[0]
            m1, m2, m3 = st.columns(3)
            m1.metric("Best model", best["model_name"])
            m2.metric("F1 score", f"{best['f1']:.3f}")
            m3.metric("ROC AUC", f"{best.get('roc_auc', 0):.3f}")
            st.dataframe(metrics.round(4), use_container_width=True, hide_index=True)
            show_image(PLOTS_DIR / "model_comparison.png", "Model comparison")

        if not training_metrics.empty:
            with st.expander("Training details"):
                st.dataframe(training_metrics.round(4), use_container_width=True, hide_index=True)

        if not feature_importance.empty:
            st.subheader("Feature importance")
            model_choice = st.selectbox(
                "Model",
                feature_importance["model_key"].drop_duplicates().tolist(),
                index=0,
            )
            fi = (
                feature_importance[feature_importance["model_key"].eq(model_choice)]
                .sort_values("importance", ascending=False)
                .head(15)
            )
            st.dataframe(fi.round(5), use_container_width=True, hide_index=True)
            show_image(PLOTS_DIR / "feature_importance.png", "Gradient Boosting feature importance")

    with tab_simulator:
        st.subheader("Next-week scenario")
        st.markdown("Change the latest observed variables and compare model predictions.")

        latest = df.iloc[-1].copy()
        brent_change = st.slider("Brent weekly return override", -0.15, 0.15, float(latest["brent_return_1w"]), 0.005)
        stress = st.slider("Maritime stress override", -1.0, 1.0, float(latest["maritime_stress"]), 0.02)
        pump_momentum = st.slider("Pump price weekly return override", -0.10, 0.10, float(latest["pump_return_1w"]), 0.005)

        scenario = latest.copy()
        scenario["brent_return_1w"] = brent_change
        scenario["maritime_stress"] = stress
        scenario["pump_return_1w"] = pump_momentum
        X = pd.DataFrame([scenario[[feature for feature in FEATURES if feature in df.columns]]])

        rows = []
        for model_key, model_info in MODELS.items():
            if model_info["path"].exists():
                model = joblib.load(model_info["path"])
                pred = int(model.predict(X)[0])
                proba = model.predict_proba(X)[0, 1] if hasattr(model, "predict_proba") else None
                rows.append(
                    {
                        "model": model_info["name"],
                        "prediction": "UP" if pred == 1 else "DOWN",
                        "probability_up": proba,
                    }
                )
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

    with tab_data:
        st.subheader("Processed dataset")
        st.dataframe(df.tail(250), use_container_width=True, hide_index=True)
        st.download_button(
            "Download processed dataset",
            df.to_csv(index=False).encode("utf-8"),
            "pump_price_dataset.csv",
            "text/csv",
        )


if __name__ == "__main__":
    build_app()
