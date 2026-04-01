from typing import Dict, List, Tuple

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import LabelEncoder, OneHotEncoder, StandardScaler


def build_preprocessor(
    df: pd.DataFrame,
    feature_cols: List[str],
    col_types: Dict[str, str],
) -> Tuple[ColumnTransformer, List[str]]:
    """
    Build a sklearn ColumnTransformer that handles:
      - Numeric columns: median imputation + standard scaling
      - Categorical columns: constant imputation + one-hot encoding
      - Boolean columns: treated as categorical
    Returns (preprocessor, preprocessing_steps_description).
    """
    numeric_cols = [c for c in feature_cols if col_types.get(c) == "numeric"]
    categorical_cols = [
        c for c in feature_cols if col_types.get(c) in ("categorical", "boolean")
    ]

    steps: List[str] = []

    numeric_pipeline = Pipeline(
        [
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
        ]
    )
    if numeric_cols:
        steps.append(f"Numeric ({len(numeric_cols)} cols): median imputation + standard scaling")

    # Limit cardinality to avoid explosion
    safe_cat_cols = []
    for col in categorical_cols:
        n_unique = df[col].nunique()
        if n_unique <= 50:
            safe_cat_cols.append(col)
        else:
            # Keep top-N categories, lump rest as "Other"
            top = df[col].value_counts().head(20).index.tolist()
            df[col] = df[col].where(df[col].isin(top), other="Other")
            safe_cat_cols.append(col)

    cat_pipeline = Pipeline(
        [
            ("imputer", SimpleImputer(strategy="constant", fill_value="missing")),
            ("encoder", OneHotEncoder(handle_unknown="ignore", sparse_output=False)),
        ]
    )
    if safe_cat_cols:
        steps.append(
            f"Categorical ({len(safe_cat_cols)} cols): constant imputation + one-hot encoding"
        )

    transformers = []
    if numeric_cols:
        transformers.append(("num", numeric_pipeline, numeric_cols))
    if safe_cat_cols:
        transformers.append(("cat", cat_pipeline, safe_cat_cols))

    preprocessor = ColumnTransformer(transformers=transformers, remainder="drop")
    return preprocessor, steps


def encode_target(series: pd.Series, task_type: str) -> Tuple[np.ndarray, LabelEncoder | None]:
    """Encode the target column. Returns (encoded_array, encoder_or_None)."""
    if task_type == "classification":
        le = LabelEncoder()
        y = le.fit_transform(series.astype(str).fillna("missing"))
        return y, le
    else:
        y = pd.to_numeric(series, errors="coerce").fillna(series.median())
        return y.to_numpy(), None


def prepare_features(
    df: pd.DataFrame,
    target_col: str,
    col_types: Dict[str, str],
) -> Tuple[pd.DataFrame, List[str]]:
    """Drop non-feature columns and return (X, feature_cols)."""
    exclude_types = {"datetime", "text"}
    feature_cols = [
        c
        for c in df.columns
        if c != target_col and col_types.get(c) not in exclude_types
    ]
    return df[feature_cols].copy(), feature_cols
