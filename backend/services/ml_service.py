import logging
import time
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline

from ml.classifier import get_classifiers
from ml.evaluator import best_model_key, classification_metrics, regression_metrics
from ml.preprocessor import build_preprocessor, encode_target, prepare_features
from ml.regressor import get_regressors
from models.schemas import ChartData, MLResults, ModelResult
from services.llm_service import llm_service
from utils.data_utils import detect_column_type
from visualization.chart_generator import feature_importance_chart, target_distribution

logger = logging.getLogger(__name__)


class MLService:
    def run(
        self,
        df: pd.DataFrame,
        target_col: str,
        col_types: Optional[Dict[str, str]] = None,
    ) -> MLResults:
        logger.info("Starting ML pipeline. Target: %s, Shape: %s", target_col, df.shape)

        if col_types is None:
            col_types = {c: detect_column_type(df[c]) for c in df.columns}

        # ── Determine task type ───────────────────────────────────────────────
        target_type = col_types.get(target_col, "categorical")
        task_type = "regression" if target_type == "numeric" else "classification"
        logger.info("Task type: %s", task_type)

        # ── Prepare features / target ─────────────────────────────────────────
        X_df, feature_cols = prepare_features(df, target_col, col_types)
        y_raw = df[target_col].copy()

        # Drop rows where target is null
        valid_mask = y_raw.notna()
        X_df = X_df[valid_mask]
        y_raw = y_raw[valid_mask]

        y, label_encoder = encode_target(y_raw, task_type)

        # ── Build preprocessor ────────────────────────────────────────────────
        preprocessor, prep_steps = build_preprocessor(X_df, feature_cols, col_types)

        # ── Train / test split ────────────────────────────────────────────────
        X_train, X_test, y_train, y_test = train_test_split(
            X_df, y, test_size=0.2, random_state=42
        )

        # ── Train models ──────────────────────────────────────────────────────
        candidates = get_classifiers() if task_type == "classification" else get_regressors()
        model_results: List[ModelResult] = []

        for name, estimator, params in candidates:
            logger.info("Training %s ...", name)
            t0 = time.time()
            try:
                pipeline = Pipeline([("preprocessor", preprocessor), ("model", estimator)])
                pipeline.fit(X_train, y_train)
                y_pred = pipeline.predict(X_test)

                if task_type == "classification":
                    y_prob = None
                    if hasattr(pipeline.named_steps["model"], "predict_proba"):
                        y_prob = pipeline.predict_proba(X_test)
                    metrics = classification_metrics(y_test, y_pred, y_prob)
                else:
                    metrics = regression_metrics(y_test, y_pred)

                elapsed = round(time.time() - t0, 2)

                # Feature importance
                imp = self._extract_importance(pipeline, feature_cols, col_types, X_df)

                model_results.append(
                    ModelResult(
                        name=name,
                        metrics=metrics,
                        feature_importance=imp,
                        params=params,
                        train_time_seconds=elapsed,
                    )
                )
            except Exception as exc:
                logger.warning("Model %s failed: %s", name, exc)

        if not model_results:
            raise RuntimeError("All models failed to train.")

        # ── Select best model ─────────────────────────────────────────────────
        rank_key = best_model_key(task_type)
        best = max(model_results, key=lambda m: m.metrics.get(rank_key, float("-inf")))
        logger.info("Best model: %s (%s=%.4f)", best.name, rank_key, best.metrics.get(rank_key, 0))

        # ── Charts ────────────────────────────────────────────────────────────
        charts: List[ChartData] = []
        if best.feature_importance:
            charts.append(feature_importance_chart(best.feature_importance, f"Feature Importance — {best.name}"))
        charts.append(target_distribution(df[valid_mask], target_col, target_type))

        # ── LLM explanation ───────────────────────────────────────────────────
        ml_summary = {
            "task_type": task_type,
            "target_column": target_col,
            "models": [
                {"name": m.name, "metrics": m.metrics, "train_seconds": m.train_time_seconds}
                for m in model_results
            ],
            "best_model": best.name,
            "best_metrics": best.metrics,
            "top_features": (
                sorted(best.feature_importance.items(), key=lambda x: x[1], reverse=True)[:5]
                if best.feature_importance else []
            ),
            "preprocessing": prep_steps,
        }
        explanation = llm_service.generate_ml_explanation(ml_summary)

        return MLResults(
            task_type=task_type,
            target_column=target_col,
            preprocessing_steps=prep_steps,
            models=model_results,
            best_model=best.name,
            best_metrics=best.metrics,
            feature_importance=best.feature_importance,
            explanation=explanation,
            charts=charts,
        )

    def _extract_importance(
        self,
        pipeline: Pipeline,
        feature_cols: List[str],
        col_types: Dict[str, str],
        X_df: pd.DataFrame,
    ) -> Optional[Dict[str, float]]:
        model = pipeline.named_steps["model"]
        preprocessor = pipeline.named_steps["preprocessor"]

        if not (hasattr(model, "feature_importances_") or hasattr(model, "coef_")):
            return None

        try:
            # Get transformed feature names
            feature_names = preprocessor.get_feature_names_out()
        except Exception:
            return None

        try:
            if hasattr(model, "feature_importances_"):
                raw = model.feature_importances_
            else:
                coef = model.coef_
                raw = np.abs(coef).mean(axis=0) if coef.ndim > 1 else np.abs(coef)

            if len(raw) != len(feature_names):
                return None

            # Aggregate back to original column names
            importance: Dict[str, float] = {}
            for fname, val in zip(feature_names, raw):
                # sklearn naming: "num__col" or "cat__col_value"
                parts = fname.split("__", 1)
                orig_col = parts[1].split("_")[0] if len(parts) > 1 else fname
                importance[orig_col] = importance.get(orig_col, 0.0) + float(val)

            total = sum(importance.values())
            if total > 0:
                importance = {k: round(v / total, 4) for k, v in importance.items()}

            return dict(sorted(importance.items(), key=lambda x: x[1], reverse=True))
        except Exception:
            return None


ml_service = MLService()
