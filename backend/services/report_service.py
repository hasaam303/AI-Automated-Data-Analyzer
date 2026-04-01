from datetime import datetime
from typing import Any, Dict, Optional

from models.schemas import Report, ReportSection
from services.llm_service import llm_service


class ReportService:
    def generate(
        self,
        analysis_id: str,
        filename: str,
        eda_results: Dict[str, Any],
        ml_results: Optional[Dict[str, Any]],
    ) -> Report:
        sections = llm_service.generate_report_sections(eda_results, ml_results, filename)

        eda_chart_ids = [c["id"] for c in eda_results.get("charts", [])]
        ml_chart_ids = [c["id"] for c in (ml_results or {}).get("charts", [])]

        return Report(
            analysis_id=analysis_id,
            title=f"Analysis Report — {filename}",
            executive_summary=sections.get("executive_summary", ""),
            data_quality=ReportSection(
                title="Data Quality",
                content=sections.get("data_quality_text", ""),
                chart_ids=[c for c in eda_chart_ids if "missing" in c][:2],
            ),
            eda_insights=ReportSection(
                title="Exploratory Insights",
                content=sections.get("eda_text", ""),
                chart_ids=eda_chart_ids[:6],
            ),
            modeling_results=(
                ReportSection(
                    title="Modeling Results",
                    content=sections.get("modeling_text") or "",
                    chart_ids=ml_chart_ids,
                )
                if ml_results and sections.get("modeling_text")
                else None
            ),
            recommendations=sections.get("recommendations", ""),
            limitations=sections.get("limitations", ""),
            generated_at=datetime.utcnow().isoformat() + "Z",
        )


report_service = ReportService()
