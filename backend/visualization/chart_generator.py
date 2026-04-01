import uuid
from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from models.schemas import ChartData

# Brand palette
PALETTE = ["#6366f1", "#8b5cf6", "#06b6d4", "#10b981", "#f59e0b", "#ef4444", "#ec4899", "#14b8a6"]
LAYOUT_DEFAULTS = dict(
    paper_bgcolor="#1e293b",
    plot_bgcolor="#1e293b",
    font=dict(color="#cbd5e1", family="Inter, sans-serif"),
    margin=dict(l=40, r=20, t=50, b=40),
    colorway=PALETTE,
)


def _chart(fig: go.Figure, chart_type: str, title: str, description: str, column: Optional[str] = None) -> ChartData:
    fig.update_layout(
        **LAYOUT_DEFAULTS,
        title=dict(text=title, font=dict(size=14, color="#f1f5f9")),
        xaxis=dict(gridcolor="#334155", zerolinecolor="#334155"),
        yaxis=dict(gridcolor="#334155", zerolinecolor="#334155"),
    )
    return ChartData(
        id=str(uuid.uuid4()),
        type=chart_type,
        title=title,
        description=description,
        plotly_json=fig.to_json(),
        column=column,
    )


def histogram(df: pd.DataFrame, col: str) -> ChartData:
    fig = go.Figure()
    fig.add_trace(
        go.Histogram(
            x=df[col].dropna(),
            nbinsx=40,
            marker_color=PALETTE[0],
            opacity=0.85,
            name=col,
        )
    )
    fig.update_layout(bargap=0.05)
    return _chart(fig, "histogram", f"Distribution of {col}", f"Frequency distribution showing the spread and shape of {col}.", col)


def boxplot(df: pd.DataFrame, col: str) -> ChartData:
    fig = go.Figure(
        go.Box(
            y=df[col].dropna(),
            name=col,
            marker_color=PALETTE[1],
            boxmean="sd",
            line_color=PALETTE[1],
        )
    )
    return _chart(fig, "boxplot", f"Box Plot — {col}", f"Shows median, IQR, and outliers for {col}.", col)


def bar_chart(df: pd.DataFrame, col: str, top_n: int = 15) -> ChartData:
    vc = df[col].value_counts().head(top_n)
    fig = go.Figure(
        go.Bar(
            x=vc.values,
            y=vc.index.astype(str),
            orientation="h",
            marker_color=PALETTE[2],
            text=vc.values,
            textposition="auto",
        )
    )
    fig.update_layout(yaxis=dict(autorange="reversed"))
    return _chart(fig, "bar", f"Top Categories — {col}", f"Most frequent values in {col}.", col)


def correlation_heatmap(df: pd.DataFrame, numeric_cols: List[str]) -> ChartData:
    corr = df[numeric_cols].corr()
    fig = go.Figure(
        go.Heatmap(
            z=corr.values,
            x=corr.columns.tolist(),
            y=corr.columns.tolist(),
            colorscale="RdBu",
            zmid=0,
            text=corr.round(2).values.astype(str),
            texttemplate="%{text}",
            colorbar=dict(tickfont=dict(color="#cbd5e1")),
        )
    )
    fig.update_layout(
        **LAYOUT_DEFAULTS,
        title=dict(text="Correlation Heatmap", font=dict(size=14, color="#f1f5f9")),
        xaxis=dict(tickangle=-45, gridcolor="#334155"),
        yaxis=dict(gridcolor="#334155"),
    )
    return ChartData(
        id=str(uuid.uuid4()),
        type="heatmap",
        title="Correlation Heatmap",
        description="Pearson correlation coefficients between all numeric features. Red = positive, Blue = negative.",
        plotly_json=fig.to_json(),
    )


def missing_values_chart(df: pd.DataFrame) -> Optional[ChartData]:
    missing = df.isnull().sum()
    missing = missing[missing > 0].sort_values(ascending=True)
    if missing.empty:
        return None

    pct = (missing / len(df) * 100).round(2)
    fig = go.Figure(
        go.Bar(
            x=pct.values,
            y=pct.index.tolist(),
            orientation="h",
            marker=dict(
                color=pct.values,
                colorscale=[[0, "#10b981"], [0.5, "#f59e0b"], [1, "#ef4444"]],
                showscale=True,
                colorbar=dict(title="% Missing", tickfont=dict(color="#cbd5e1")),
            ),
            text=[f"{v:.1f}%" for v in pct.values],
            textposition="auto",
        )
    )
    return _chart(fig, "missing", "Missing Values by Column", "Percentage of missing values per column.")


def target_distribution(df: pd.DataFrame, target_col: str, col_type: str) -> ChartData:
    if col_type == "numeric":
        fig = go.Figure(go.Histogram(x=df[target_col].dropna(), nbinsx=30, marker_color=PALETTE[3]))
    else:
        vc = df[target_col].value_counts()
        fig = go.Figure(
            go.Bar(x=vc.index.astype(str), y=vc.values, marker_color=PALETTE[3])
        )
    return _chart(fig, "target_dist", f"Target Distribution — {target_col}", f"Distribution of the target variable {target_col}.", target_col)


def feature_importance_chart(importance: Dict[str, float], title: str = "Feature Importance") -> ChartData:
    sorted_imp = dict(sorted(importance.items(), key=lambda x: x[1]))
    top = dict(list(sorted_imp.items())[-20:])  # top 20
    fig = go.Figure(
        go.Bar(
            x=list(top.values()),
            y=list(top.keys()),
            orientation="h",
            marker=dict(
                color=list(top.values()),
                colorscale=[[0, "#334155"], [1, "#6366f1"]],
                showscale=False,
            ),
        )
    )
    return _chart(fig, "feature_importance", title, "Feature importance scores from the best model.")


def scatter_with_target(df: pd.DataFrame, col1: str, col2: str, target_col: Optional[str] = None) -> ChartData:
    color = df[target_col].astype(str) if target_col else None
    fig = px.scatter(
        df.dropna(subset=[col1, col2]),
        x=col1,
        y=col2,
        color=color,
        color_discrete_sequence=PALETTE,
        opacity=0.6,
    )
    label = f" colored by {target_col}" if target_col else ""
    return _chart(fig, "scatter", f"{col1} vs {col2}{label}", f"Scatter plot showing relationship between {col1} and {col2}.", col1)


def generate_all_charts(
    df: pd.DataFrame,
    col_types: Dict[str, str],
    numeric_cols: List[str],
    categorical_cols: List[str],
    target_col: Optional[str] = None,
    max_numeric_charts: int = 6,
    max_cat_charts: int = 4,
) -> List[ChartData]:
    charts: List[ChartData] = []

    # Histograms for numeric columns
    for col in numeric_cols[:max_numeric_charts]:
        if col != target_col:
            charts.append(histogram(df, col))

    # Box plots for numeric columns (subset)
    for col in numeric_cols[:4]:
        if col != target_col:
            charts.append(boxplot(df, col))

    # Bar charts for categorical columns
    for col in categorical_cols[:max_cat_charts]:
        if col != target_col:
            charts.append(bar_chart(df, col))

    # Correlation heatmap
    if len(numeric_cols) >= 2:
        charts.append(correlation_heatmap(df, numeric_cols[:15]))

    # Missing values
    mv_chart = missing_values_chart(df)
    if mv_chart:
        charts.append(mv_chart)

    # Target distribution
    if target_col and target_col in df.columns:
        charts.append(target_distribution(df, target_col, col_types.get(target_col, "categorical")))

    # Scatter of top-2 correlated numeric cols
    if len(numeric_cols) >= 2:
        charts.append(scatter_with_target(df, numeric_cols[0], numeric_cols[1], target_col))

    return charts
