import re
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd


NUMERIC_DTYPES = {"int8", "int16", "int32", "int64", "float16", "float32", "float64"}
_BOOL_KEYWORDS = {"yes", "no", "true", "false", "y", "n", "0", "1"}


def detect_column_type(series: pd.Series) -> str:
    """Infer a semantic column type from a pandas Series."""
    if pd.api.types.is_bool_dtype(series):
        return "boolean"

    if pd.api.types.is_datetime64_any_dtype(series):
        return "datetime"

    if pd.api.types.is_numeric_dtype(series):
        unique_vals = series.dropna().unique()
        if set(unique_vals).issubset({0, 1, 0.0, 1.0}):
            return "boolean"
        return "numeric"

    # Object / string columns
    sample = series.dropna().astype(str).str.lower().unique()
    if len(sample) <= 2 and set(sample).issubset(_BOOL_KEYWORDS):
        return "boolean"

    # Try parsing as datetime
    if len(series) > 0:
        sample_str = series.dropna().astype(str).head(50)
        try:
            parsed = pd.to_datetime(sample_str, errors="coerce")
            if parsed.notna().mean() > 0.8:
                return "datetime"
        except Exception:
            pass

    # High-cardinality text vs categorical
    n_unique = series.nunique()
    n_total = len(series.dropna())
    if n_total == 0:
        return "categorical"

    avg_len = series.dropna().astype(str).str.len().mean()
    if avg_len > 50 or n_unique / max(n_total, 1) > 0.8:
        return "text"

    return "categorical"


def compute_column_stats(series: pd.Series, col_type: str) -> Dict[str, Any]:
    """Return type-appropriate summary statistics."""
    stats: Dict[str, Any] = {
        "count": int(series.count()),
        "missing": int(series.isna().sum()),
        "missing_pct": round(float(series.isna().mean() * 100), 2),
        "unique": int(series.nunique()),
    }

    if col_type == "numeric":
        desc = series.describe()
        stats.update(
            {
                "mean": round(float(desc["mean"]), 4),
                "std": round(float(desc["std"]), 4),
                "min": round(float(desc["min"]), 4),
                "q25": round(float(desc["25%"]), 4),
                "median": round(float(desc["50%"]), 4),
                "q75": round(float(desc["75%"]), 4),
                "max": round(float(desc["max"]), 4),
                "skewness": round(float(series.skew()), 4),
                "kurtosis": round(float(series.kurtosis()), 4),
            }
        )
    elif col_type == "categorical":
        vc = series.value_counts()
        stats["top_values"] = {str(k): int(v) for k, v in vc.head(10).items()}
        stats["mode"] = str(vc.index[0]) if len(vc) > 0 else None
        stats["entropy"] = round(float(_entropy(vc / vc.sum())), 4)
    elif col_type == "boolean":
        vc = series.value_counts(normalize=True)
        stats["true_pct"] = round(float(vc.get(True, vc.get(1, vc.get("true", vc.get("yes", 0)))) * 100), 2)
    elif col_type == "datetime":
        dt = pd.to_datetime(series, errors="coerce")
        stats["min_date"] = str(dt.min()) if dt.notna().any() else None
        stats["max_date"] = str(dt.max()) if dt.notna().any() else None
        stats["range_days"] = int((dt.max() - dt.min()).days) if dt.notna().any() else None

    return stats


def _entropy(probs: pd.Series) -> float:
    p = probs[probs > 0]
    return float(-np.sum(p * np.log2(p)))


def detect_outliers_iqr(series: pd.Series) -> Tuple[int, float, float]:
    """Return (outlier_count, lower_fence, upper_fence) using IQR method."""
    q1 = series.quantile(0.25)
    q3 = series.quantile(0.75)
    iqr = q3 - q1
    lower = q1 - 1.5 * iqr
    upper = q3 + 1.5 * iqr
    n_outliers = int(((series < lower) | (series > upper)).sum())
    return n_outliers, float(lower), float(upper)


def compute_correlations(df: pd.DataFrame, numeric_cols: List[str]) -> Dict[str, Any]:
    """Compute Pearson correlation matrix for numeric columns."""
    if len(numeric_cols) < 2:
        return {"columns": numeric_cols, "matrix": {}}

    corr = df[numeric_cols].corr(method="pearson")

    # Find strong correlations (|r| > 0.7, excluding self)
    strong_pairs = []
    cols = corr.columns.tolist()
    for i, c1 in enumerate(cols):
        for c2 in cols[i + 1 :]:
            val = float(corr.loc[c1, c2])
            if abs(val) >= 0.7 and not np.isnan(val):
                strong_pairs.append({"col1": c1, "col2": c2, "r": round(val, 3)})

    return {
        "columns": cols,
        "matrix": {c: {r: round(float(corr.loc[c, r]), 4) for r in cols} for c in cols},
        "strong_pairs": sorted(strong_pairs, key=lambda x: abs(x["r"]), reverse=True),
    }


def infer_target_column(df: pd.DataFrame, col_types: Dict[str, str]) -> Tuple[Optional[str], Optional[str]]:
    """
    Heuristically guess a target column.
    Returns (column_name, task_type) or (None, None).
    """
    import re

    target_keywords = re.compile(
        r"(target|label|class|outcome|churn|price|salary|revenue|survived|default|fraud|result|y$)",
        re.IGNORECASE,
    )

    for col in df.columns:
        if target_keywords.search(col):
            ctype = col_types.get(col)
            if ctype == "numeric":
                return col, "regression"
            elif ctype in ("categorical", "boolean"):
                return col, "classification"

    return None, None
