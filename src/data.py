from __future__ import annotations

from typing import Any

import pandas as pd
from sklearn.model_selection import train_test_split

from config import MONTHLY_FEATURES_PATH, NUMERIC_FEATURES, RANDOM_STATE, TEST_SIZE


def load_dataset_split() -> tuple[Any, Any, Any, Any]:
    df = pd.read_csv(MONTHLY_FEATURES_PATH)
    available_features = [column for column in NUMERIC_FEATURES if column in df.columns]
    X = df[available_features].copy()
    y = df["criticality_class"].astype(int)

    return train_test_split(
        X,
        y,
        test_size=TEST_SIZE,
        random_state=RANDOM_STATE,
        stratify=y,
    )

