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
    ax.barh(data["portname"], data["criticality_score"], color="#1f77b4")
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
    data = metrics.sort_values("f1_macro", ascending=True)
    label_col = "model_name" if "model_name" in data.columns else "model_key"
    fig, ax = plt.subplots()
    ax.barh(data[label_col], data["f1_macro"], color="#ff7f0e")
    ax.set_title("Comparaison des modèles")
    ax.set_xlabel("F1 macro")
    ax.set_xlim(0, 1)
    fig.tight_layout()
    fig.savefig(output)
    plt.close(fig)

