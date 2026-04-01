import logging
from typing import Dict, List, Optional

import pandas as pd

from models.schemas import AnalysisPlan, ChartData, ColumnInfo, EDAResults
from services.llm_service import llm_service
from utils.data_utils import (
    compute_column_stats,
    compute_correlations,
    detect_column_type,
    detect_outliers_iqr,
    infer_target_column,
)
from visualization.chart_generator import generate_all_charts

logger = logging.getLogger(__name__)


class AnalysisService:
    def run(
        self,
        df: pd.DataFrame,
        target_column: Optional[str] = None,
    ) -> EDAResults:
        logger.info("Starting EDA on dataset with shape %s", df.shape)

        # ── 1. Detect column types ────────────────────────────────────────────
        col_types: Dict[str, str] = {col: detect_column_type(df[col]) for col in df.columns}

        # ── 2. Build ColumnInfo list ──────────────────────────────────────────
        column_details: List[ColumnInfo] = []
        for col in df.columns:
            ctype = col_types[col]
            stats = compute_column_stats(df[col], ctype)
            column_details.append(
                ColumnInfo(
                    name=col,
                    dtype=ctype,
                    missing_count=int(df[col].isna().sum()),
                    missing_pct=round(float(df[col].isna().mean() * 100), 2),
                    unique_count=int(df[col].nunique()),
                    stats=stats,
                )
            )

        # ── 3. Infer target column if not provided ────────────────────────────
        inferred_target, inferred_task = infer_target_column(df, col_types)
        if not target_column:
            target_column = inferred_target

        # ── 4. Summary stats ──────────────────────────────────────────────────
        numeric_cols = [c for c, t in col_types.items() if t == "numeric"]
        categorical_cols = [c for c, t in col_types.items() if t == "categorical"]
        boolean_cols = [c for c, t in col_types.items() if t == "boolean"]
        datetime_cols = [c for c, t in col_types.items() if t == "datetime"]

        summary_stats = {
            "row_count": len(df),
            "col_count": len(df.columns),
            "numeric_cols": len(numeric_cols),
            "categorical_cols": len(categorical_cols),
            "boolean_cols": len(boolean_cols),
            "datetime_cols": len(datetime_cols),
            "total_missing_cells": int(df.isna().sum().sum()),
            "total_missing_pct": round(float(df.isna().mean().mean() * 100), 2),
            "duplicate_rows": int(df.duplicated().sum()),
            "memory_mb": round(df.memory_usage(deep=True).sum() / 1_048_576, 2),
        }

        # ── 5. Correlations ───────────────────────────────────────────────────
        correlations = compute_correlations(df, numeric_cols)

        # ── 6. Outlier analysis ───────────────────────────────────────────────
        outliers = []
        for col in numeric_cols:
            n_out, lower, upper = detect_outliers_iqr(df[col].dropna())
            if n_out > 0:
                outliers.append(
                    {
                        "column": col,
                        "count": n_out,
                        "pct": round(n_out / len(df) * 100, 2),
                        "lower_fence": lower,
                        "upper_fence": upper,
                    }
                )
        outliers.sort(key=lambda x: x["pct"], reverse=True)

        # ── 7. Missing values analysis ────────────────────────────────────────
        missing_per_col = df.isna().sum()
        missing_analysis = {
            "columns_with_missing": int((missing_per_col > 0).sum()),
            "worst_columns": {
                col: {"count": int(cnt), "pct": round(cnt / len(df) * 100, 2)}
                for col, cnt in missing_per_col[missing_per_col > 0].sort_values(ascending=False).head(5).items()
            },
        }

        # ── 8. Pattern detection ──────────────────────────────────────────────
        patterns = self._detect_patterns(df, col_types, correlations, outliers, summary_stats)

        # ── 9. Build analysis plan ────────────────────────────────────────────
        task_type = None
        if target_column:
            ttype = col_types.get(target_column)
            task_type = "regression" if ttype == "numeric" else "classification"

        plan_steps = self._build_plan_steps(df, col_types, target_column, task_type)
        plan_rationale = llm_service.generate_analysis_plan_rationale(
            {"steps": plan_steps, "summary": summary_stats, "target": target_column}
        )
        analysis_plan = AnalysisPlan(
            steps=plan_steps,
            target_detected=target_column,
            task_type=task_type,
            notable_features=numeric_cols[:5] + categorical_cols[:3],
            rationale=plan_rationale,
        )

        # ── 10. Generate charts ───────────────────────────────────────────────
        charts: List[ChartData] = generate_all_charts(
            df, col_types, numeric_cols, categorical_cols, target_column
        )

        # ── 11. LLM insights ──────────────────────────────────────────────────
        eda_summary_for_llm = {
            "shape": f"{len(df)} rows × {len(df.columns)} cols",
            "numeric_cols": numeric_cols[:8],
            "categorical_cols": categorical_cols[:5],
            "missing_analysis": missing_analysis,
            "strong_correlations": correlations.get("strong_pairs", [])[:5],
            "top_outlier_cols": [o["column"] for o in outliers[:3]],
            "patterns": patterns,
            "duplicate_rows": summary_stats["duplicate_rows"],
            "target_column": target_column,
            "task_type": task_type,
        }
        insights = llm_service.generate_eda_insights(eda_summary_for_llm)

        return EDAResults(
            analysis_plan=analysis_plan,
            summary_stats=summary_stats,
            column_details=column_details,
            correlations=correlations,
            outliers=outliers,
            missing_analysis=missing_analysis,
            patterns=patterns,
            charts=charts,
            insights=insights,
        )

    def _detect_patterns(self, df, col_types, correlations, outliers, summary_stats) -> List[str]:
        patterns = []
        if summary_stats["duplicate_rows"] > 0:
            patterns.append(f"{summary_stats['duplicate_rows']} duplicate rows detected ({round(summary_stats['duplicate_rows']/summary_stats['row_count']*100,1)}%).")
        if summary_stats["total_missing_pct"] > 5:
            patterns.append(f"Dataset has {summary_stats['total_missing_pct']:.1f}% missing values overall.")
        for pair in correlations.get("strong_pairs", [])[:3]:
            dir_ = "positively" if pair["r"] > 0 else "negatively"
            patterns.append(f"'{pair['col1']}' and '{pair['col2']}' are strongly {dir_} correlated (r={pair['r']}).")
        for out in outliers[:2]:
            patterns.append(f"'{out['column']}' has {out['count']} outliers ({out['pct']}% of rows).")
        high_missing = [c for c, t in col_types.items() if df[c].isna().mean() > 0.3]
        if high_missing:
            patterns.append(f"Columns with >30% missing data: {', '.join(high_missing[:3])}.")
        return patterns

    def _build_plan_steps(self, df, col_types, target_col, task_type) -> List[str]:
        steps = [
            "Detect and classify column types (numeric, categorical, boolean, datetime, text)",
            "Compute summary statistics per column",
            "Analyze missing values and data quality",
            "Compute Pearson correlations between numeric features",
            "Identify outliers using IQR method",
            "Generate distribution charts for numeric features",
            "Generate frequency charts for categorical features",
            "Generate correlation heatmap",
        ]
        if target_col:
            steps.append(f"Analyze target variable distribution: '{target_col}'")
        if task_type:
            steps.append(f"Prepare for {task_type} modeling (target: '{target_col}')")
        steps.append("Generate AI-powered insights and narrative summary")
        return steps


analysis_service = AnalysisService()
