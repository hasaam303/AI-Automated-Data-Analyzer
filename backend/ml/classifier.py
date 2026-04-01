from typing import Any, Dict, List, Tuple

from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline


def get_classifiers() -> List[Tuple[str, Any, Dict[str, Any]]]:
    """Return list of (name, estimator, params) for baseline classifiers."""
    return [
        (
            "Logistic Regression",
            LogisticRegression(max_iter=1000, random_state=42, class_weight="balanced"),
            {"C": 1.0, "solver": "lbfgs", "max_iter": 1000},
        ),
        (
            "Random Forest",
            RandomForestClassifier(n_estimators=200, random_state=42, class_weight="balanced", n_jobs=-1),
            {"n_estimators": 200, "max_depth": None, "class_weight": "balanced"},
        ),
        (
            "Gradient Boosting",
            GradientBoostingClassifier(n_estimators=100, learning_rate=0.1, random_state=42),
            {"n_estimators": 100, "learning_rate": 0.1, "max_depth": 3},
        ),
    ]
