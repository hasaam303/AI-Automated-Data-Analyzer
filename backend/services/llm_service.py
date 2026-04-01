import json
import logging
from typing import Any, Dict, Optional

from openai import OpenAI

from config import settings

logger = logging.getLogger(__name__)


class LLMService:
    def __init__(self):
        self._client: Optional[OpenAI] = None

    @property
    def client(self) -> OpenAI:
        if self._client is None:
            if not settings.openai_api_key:
                raise ValueError("OPENAI_API_KEY is not configured.")
            self._client = OpenAI(api_key=settings.openai_api_key)
        return self._client

    def _chat(self, system_prompt: str, user_content: str, max_tokens: int = 1200) -> str:
        try:
            resp = self.client.chat.completions.create(
                model=settings.llm_model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_content},
                ],
                temperature=0.3,
                max_tokens=max_tokens,
            )
            return resp.choices[0].message.content.strip()
        except Exception as exc:
            logger.warning("LLM call failed: %s", exc)
            return f"[AI insights unavailable: {exc}]"

    # ── EDA Insights ──────────────────────────────────────────────────────────

    def generate_eda_insights(self, eda_summary: Dict[str, Any]) -> str:
        system = (
            "You are a senior data analyst writing a business-style briefing. "
            "Write clear, concise prose — no bullet headers, no markdown. "
            "Describe only what the data supports. Avoid hallucinating."
        )
        payload = json.dumps(eda_summary, default=str)[:4000]
        prompt = (
            f"Here is a summary of an exploratory data analysis:\n{payload}\n\n"
            "Write 3–4 paragraphs of polished insights a business stakeholder would find valuable. "
            "Mention the most important patterns, distributions, correlations, and data quality issues."
        )
        return self._chat(system, prompt, max_tokens=800)

    # ── ML Explanation ────────────────────────────────────────────────────────

    def generate_ml_explanation(self, ml_summary: Dict[str, Any]) -> str:
        system = (
            "You are a machine learning engineer explaining results to a non-technical product manager. "
            "Be direct, clear, and specific. No bullet lists — write prose."
        )
        payload = json.dumps(ml_summary, default=str)[:3000]
        prompt = (
            f"Here are the machine learning results:\n{payload}\n\n"
            "Explain: which model performed best and why, what the key metrics mean in plain English, "
            "which features drove the predictions, and any caveats or limitations."
        )
        return self._chat(system, prompt, max_tokens=700)

    # ── Analysis Plan ─────────────────────────────────────────────────────────

    def generate_analysis_plan_rationale(self, plan_summary: Dict[str, Any]) -> str:
        system = "You are a data science lead describing an analysis plan in one concise paragraph."
        payload = json.dumps(plan_summary, default=str)[:1500]
        prompt = (
            f"Given this dataset summary and planned steps:\n{payload}\n\n"
            "Write one paragraph explaining what the analysis will focus on and why."
        )
        return self._chat(system, prompt, max_tokens=200)

    # ── Final Report ──────────────────────────────────────────────────────────

    def generate_report_sections(
        self,
        eda_results: Dict[str, Any],
        ml_results: Optional[Dict[str, Any]],
        filename: str,
    ) -> Dict[str, str]:
        system = (
            "You are a senior data scientist writing a professional analytical report. "
            "Write in clear, formal prose. Each section should be 2–4 sentences. "
            "Only describe what the data and models actually show."
        )
        payload = {
            "filename": filename,
            "eda_summary": {
                "rows": eda_results.get("summary_stats", {}).get("row_count"),
                "cols": eda_results.get("summary_stats", {}).get("col_count"),
                "patterns": eda_results.get("patterns", [])[:5],
                "strong_correlations": eda_results.get("correlations", {}).get("strong_pairs", [])[:3],
                "missing": eda_results.get("missing_analysis", {}),
            },
            "ml_summary": ml_results,
        }
        user_msg = (
            f"Data:\n{json.dumps(payload, default=str)[:4000]}\n\n"
            "Return a JSON object with these keys: executive_summary, data_quality_text, "
            "eda_text, modeling_text (null if no ML), recommendations, limitations."
        )
        raw = self._chat(system, user_msg, max_tokens=1500)

        # Parse JSON response, falling back to raw text in each field
        try:
            cleaned = raw.strip().lstrip("```json").rstrip("```").strip()
            return json.loads(cleaned)
        except Exception:
            return {
                "executive_summary": raw,
                "data_quality_text": "See EDA results.",
                "eda_text": "See charts and statistics.",
                "modeling_text": None,
                "recommendations": "Review data quality and model performance.",
                "limitations": "Results are based on the uploaded dataset only.",
            }


llm_service = LLMService()
