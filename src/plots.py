from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


def _style() -> None:
    plt.style.use("seaborn-v0_8-whitegrid")
    plt.rcParams.update(
        {
            "figure.figsize": (12, 7),
            "axes.titlesize": 14,
            "axes.labelsize": 10,
            "savefig.dpi": 160,
        }
    )


def plot_criticality_ranking(summary: pd.DataFrame, output: Path, top_n: int = 15) -> None:
    _style()
    data = summary.sort_values("criticality_score", ascending=True).tail(top_n)
    fig, ax = plt.subplots()
    colors = data["criticality_class"].map({0: "#94a3b8", 1: "#38bdf8", 2: "#f59e0b", 3: "#ef4444"})
    ax.barh(data["portname"], data["criticality_score"], color=colors)
    ax.set_title("Classement de criticité des chokepoints")
    ax.set_xlabel("Score de criticité (0-100)")
    fig.tight_layout()
    fig.savefig(output)
    plt.close(fig)


def plot_traffic_by_chokepoint(summary: pd.DataFrame, output: Path, top_n: int = 15) -> None:
    _style()
    data = summary.sort_values("mean_n_total", ascending=True).tail(top_n)
    fig, ax = plt.subplots()
    ax.barh(data["portname"], data["mean_n_total"], color="#2ca02c")
    ax.set_title("Trafic moyen journalier par chokepoint")
    ax.set_xlabel("Nombre moyen de navires par jour")
    fig.tight_layout()
    fig.savefig(output)
    plt.close(fig)


def plot_tanker_capacity(summary: pd.DataFrame, output: Path, top_n: int = 15) -> None:
    _style()
    data = summary.sort_values("mean_capacity_tanker", ascending=True).tail(top_n)
    fig, ax = plt.subplots()
    ax.barh(data["portname"], data["mean_capacity_tanker"], color="#d62728")
    ax.set_title("Capacité tanker moyenne par chokepoint")
    ax.set_xlabel("Capacité tanker moyenne journalière")
    fig.tight_layout()
    fig.savefig(output)
    plt.close(fig)


def plot_disruption_frequency(summary: pd.DataFrame, output: Path, top_n: int = 15) -> None:
    _style()
    data = summary.sort_values("disruption_frequency_total", ascending=True).tail(top_n)
    fig, ax = plt.subplots()
    ax.barh(data["portname"], data["disruption_frequency_total"], color="#9467bd")
    ax.set_title("Fréquence des perturbations détectées")
    ax.set_xlabel("Part des jours avec z-score trafic < -2")
    fig.tight_layout()
    fig.savefig(output)
    plt.close(fig)


def plot_model_comparison(metrics: pd.DataFrame, output: Path) -> None:
    _style()
    if metrics.empty or "f1_macro" not in metrics.columns:
        return
    label_col = "model_name" if "model_name" in metrics.columns else "model_key"
    metric_columns = [
        column
        for column in ["accuracy", "balanced_accuracy", "f1_macro", "f1_weighted"]
        if column in metrics.columns
    ]
    data = metrics.sort_values("f1_macro", ascending=True).set_index(label_col)[metric_columns]
    fig, ax = plt.subplots(figsize=(10, 5.5))
    data.plot(kind="barh", ax=ax, width=0.78)
    ax.set_title("Comparaison des modèles")
    ax.set_xlabel("Score")
    ax.set_xlim(0, 1)
    ax.legend(loc="lower right")
    fig.tight_layout()
    fig.savefig(output)
    plt.close(fig)


def plot_feature_importance(
    importances: pd.DataFrame,
    output: Path,
    model_key: str = "gradient_boosting",
    top_n: int = 12,
) -> None:
    if importances.empty or "model_key" not in importances.columns:
        return
    _style()
    data = (
        importances[importances["model_key"].eq(model_key)]
        .sort_values("importance", ascending=True)
        .tail(top_n)
    )
    if data.empty:
        return
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.barh(data["feature"], data["importance"], color="#0f766e")
    ax.set_title("Variables les plus importantes")
    ax.set_xlabel("Importance relative")
    fig.tight_layout()
    fig.savefig(output)
    plt.close(fig)
