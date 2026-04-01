from typing import Any, Dict, List, Tuple

from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor
from sklearn.linear_model import Ridge


def get_regressors() -> List[Tuple[str, Any, Dict[str, Any]]]:
    """Return list of (name, estimator, params) for baseline regressors."""
    return [
        (
            "Ridge Regression",
            Ridge(alpha=1.0),
            {"alpha": 1.0},
        ),
        (
            "Random Forest",
            RandomForestRegressor(n_estimators=200, random_state=42, n_jobs=-1),
            {"n_estimators": 200, "max_depth": None},
        ),
        (
            "Gradient Boosting",
            GradientBoostingRegressor(n_estimators=100, learning_rate=0.1, random_state=42),
            {"n_estimators": 100, "learning_rate": 0.1, "max_depth": 3},
        ),
    ]
