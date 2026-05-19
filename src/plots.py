from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


def _style() -> None:
    plt.style.use("seaborn-v0_8-whitegrid")
    plt.rcParams.update(
        {
            "figure.figsize": (11, 6),
            "axes.titlesize": 14,
            "axes.labelsize": 10,
            "savefig.dpi": 160,
        }
    )


def plot_pump_brent_timeseries(df: pd.DataFrame, output: Path) -> None:
    _style()
    fig, ax1 = plt.subplots()
    ax1.plot(df["date"], df["pump_price"], color="#dc2626", label="Pump price")
    ax1.set_ylabel("Gasoline price ($/gallon)")
    ax2 = ax1.twinx()
    ax2.plot(df["date"], df["brent_price"], color="#2563eb", alpha=0.75, label="Brent")
    ax2.set_ylabel("Brent ($/barrel)")
    ax1.set_title("Gasoline price and Brent crude oil")
    fig.tight_layout()
    fig.savefig(output)
    plt.close(fig)


def plot_tanker_traffic(df: pd.DataFrame, output: Path) -> None:
    _style()
    cols = [
        "strait_of_hormuz_n_tanker",
        "bab_el_mandeb_strait_n_tanker",
        "suez_canal_n_tanker",
        "malacca_strait_n_tanker",
    ]
    labels = ["Hormuz", "Bab el-Mandeb", "Suez", "Malacca"]
    fig, ax = plt.subplots()
    for col, label in zip(cols, labels):
        if col in df.columns:
            ax.plot(df["date"], df[col].rolling(4).mean(), label=label)
    ax.set_title("Weekly tanker traffic around strategic chokepoints")
    ax.set_ylabel("Tankers per week")
    ax.legend()
    fig.tight_layout()
    fig.savefig(output)
    plt.close(fig)


def plot_model_comparison(metrics: pd.DataFrame, output: Path) -> None:
    if metrics.empty:
        return
    _style()
    cols = [col for col in ["accuracy", "balanced_accuracy", "f1", "roc_auc"] if col in metrics.columns]
    data = metrics.set_index("model_name")[cols].sort_values("f1")
    fig, ax = plt.subplots(figsize=(10, 5))
    data.plot(kind="barh", ax=ax)
    ax.set_xlim(0, 1)
    ax.set_title("Model comparison")
    ax.set_xlabel("Score")
    fig.tight_layout()
    fig.savefig(output)
    plt.close(fig)


def plot_feature_importance(importances: pd.DataFrame, output: Path, model_key: str = "gradient_boosting") -> None:
    if importances.empty:
        return
    data = (
        importances[importances["model_key"].eq(model_key)]
        .sort_values("importance", ascending=True)
        .tail(15)
    )
    if data.empty:
        return
    _style()
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.barh(data["feature"], data["importance"], color="#0f766e")
    ax.set_title("Top feature importance")
    ax.set_xlabel("Importance")
    fig.tight_layout()
    fig.savefig(output)
    plt.close(fig)
