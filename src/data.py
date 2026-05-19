from __future__ import annotations

from typing import Any

import pandas as pd

from config import FEATURES, PROCESSED_DATA_PATH, TARGET, TEST_SIZE


def load_dataset_split() -> tuple[Any, Any, Any, Any]:
    df = pd.read_csv(PROCESSED_DATA_PATH, parse_dates=["date"]).sort_values("date")
    available_features = [feature for feature in FEATURES if feature in df.columns]
    X = df[available_features].copy()
    y = df[TARGET].astype(int)

    split_idx = int(len(df) * (1 - TEST_SIZE))
    X_train = X.iloc[:split_idx]
    X_test = X.iloc[split_idx:]
    y_train = y.iloc[:split_idx]
    y_test = y.iloc[split_idx:]
    return X_train, X_test, y_train, y_test
