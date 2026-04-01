from typing import Any, Dict, List, Optional
from datetime import datetime
from pydantic import BaseModel


# ── Column / Upload ────────────────────────────────────────────────────────────

class ColumnInfo(BaseModel):
    name: str
    dtype: str          # numeric | categorical | boolean | datetime | text
    missing_count: int
    missing_pct: float
    unique_count: int
    stats: Dict[str, Any]


class UploadResponse(BaseModel):
    analysis_id: str
    filename: str
    row_count: int
    col_count: int
    preview: List[Dict[str, Any]]
    columns: List[ColumnInfo]
    detected_schema: Dict[str, str]


# ── Analysis Plan ──────────────────────────────────────────────────────────────

class AnalysisPlan(BaseModel):
    steps: List[str]
    target_detected: Optional[str]
    task_type: Optional[str]          # classification | regression | None
    notable_features: List[str]
    rationale: str


# ── Charts ─────────────────────────────────────────────────────────────────────

class ChartData(BaseModel):
    id: str
    type: str
    title: str
    description: str
    plotly_json: str
    column: Optional[str] = None


# ── EDA ────────────────────────────────────────────────────────────────────────

class EDAResults(BaseModel):
    analysis_plan: AnalysisPlan
    summary_stats: Dict[str, Any]
    column_details: List[ColumnInfo]
    correlations: Dict[str, Any]
    outliers: List[Dict[str, Any]]
    missing_analysis: Dict[str, Any]
    patterns: List[str]
    charts: List[ChartData]
    insights: str                    # LLM narrative


# ── ML ─────────────────────────────────────────────────────────────────────────

class ModelResult(BaseModel):
    name: str
    metrics: Dict[str, float]
    feature_importance: Optional[Dict[str, float]] = None
    params: Dict[str, Any]
    train_time_seconds: float


class MLResults(BaseModel):
    task_type: str
    target_column: str
    preprocessing_steps: List[str]
    models: List[ModelResult]
    best_model: str
    best_metrics: Dict[str, float]
    feature_importance: Optional[Dict[str, float]] = None
    explanation: str                 # LLM narrative
    charts: List[ChartData]


# ── Report ─────────────────────────────────────────────────────────────────────

class ReportSection(BaseModel):
    title: str
    content: str
    chart_ids: List[str] = []


class Report(BaseModel):
    analysis_id: str
    title: str
    executive_summary: str
    data_quality: ReportSection
    eda_insights: ReportSection
    modeling_results: Optional[ReportSection] = None
    recommendations: str
    limitations: str
    generated_at: str


# ── History ────────────────────────────────────────────────────────────────────

class AnalysisSummary(BaseModel):
    id: str
    filename: str
    status: str
    row_count: Optional[int]
    col_count: Optional[int]
    created_at: datetime
    has_ml: bool


# ── Requests ───────────────────────────────────────────────────────────────────

class RunAnalysisRequest(BaseModel):
    target_column: Optional[str] = None


class RunModelingRequest(BaseModel):
    target_column: str
