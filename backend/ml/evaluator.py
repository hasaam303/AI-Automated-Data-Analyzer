from typing import Dict, Optional

import numpy as np
from sklearn.metrics import (
    accuracy_score,
    f1_score,
    mean_absolute_error,
    mean_squared_error,
    r2_score,
    roc_auc_score,
)


def classification_metrics(y_true: np.ndarray, y_pred: np.ndarray, y_prob: Optional[np.ndarray] = None) -> Dict[str, float]:
    metrics: Dict[str, float] = {
        "accuracy": round(float(accuracy_score(y_true, y_pred)), 4),
        "f1_weighted": round(float(f1_score(y_true, y_pred, average="weighted", zero_division=0)), 4),
    }
    if y_prob is not None:
        n_classes = y_prob.shape[1] if y_prob.ndim > 1 else 2
        try:
            if n_classes == 2:
                auc = roc_auc_score(y_true, y_prob[:, 1])
            else:
                auc = roc_auc_score(y_true, y_prob, multi_class="ovr", average="weighted")
            metrics["roc_auc"] = round(float(auc), 4)
        except Exception:
            pass
    return metrics


def regression_metrics(y_true: np.ndarray, y_pred: np.ndarray) -> Dict[str, float]:
    rmse = float(np.sqrt(mean_squared_error(y_true, y_pred)))
    return {
        "rmse": round(rmse, 4),
        "mae": round(float(mean_absolute_error(y_true, y_pred)), 4),
        "r2": round(float(r2_score(y_true, y_pred)), 4),
    }


def best_model_key(task_type: str) -> str:
    """Return the metric name used to rank models."""
    return "roc_auc" if task_type == "classification" else "r2"
