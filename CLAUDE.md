# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Backend
```bash
cd backend
uvicorn main:app --reload --port 8000   # start dev server
python -m pytest                         # run tests (if added)
```

### Frontend
```bash
cd frontend
npm run dev      # start Vite dev server on :5173
npm run build    # production build
npm run preview  # preview production build
```

### Docker
```bash
docker-compose up --build   # full stack
docker-compose down         # stop
```

## Architecture

**Request flow**: CSV upload → `POST /api/upload` → `POST /api/analysis/{id}/run` → optional `POST /api/modeling/{id}/run` → `GET /api/report/{id}`

**Backend (FastAPI + SQLite)**
- `backend/main.py` — app entry, router registration
- `backend/config.py` — all settings via `pydantic-settings` (reads `.env`)
- `backend/services/analysis_service.py` — EDA orchestrator; calls `data_utils`, `chart_generator`, then `llm_service`
- `backend/services/ml_service.py` — ML orchestrator; calls `preprocessor`, classifier/regressor modules, `evaluator`, then `llm_service`
- `backend/services/llm_service.py` — OpenAI client wrapper; all LLM calls go through `LLMService._chat()`
- `backend/visualization/chart_generator.py` — Plotly figures returned as JSON strings via `fig.to_json()`
- `backend/db/models.py` — `Analysis` SQLAlchemy model stores all results as JSON columns
- `backend/models/schemas.py` — all Pydantic request/response models

**Frontend (React + Vite + Tailwind + Zustand)**
- `frontend/src/store/analysisStore.js` — single Zustand store; holds upload, EDA, ML, report state
- `frontend/src/services/api.js` — Axios client proxied to `/api` (Vite proxies to `:8000`)
- `frontend/src/pages/Analysis.jsx` — main analysis page; tabs: Overview / Charts / Insights / Modeling / Report
- Charts rendered with `react-plotly.js` — receive `plotly_json` string from API, parsed before passing to `<Plot>`

## Key Conventions

- All chart data is a `ChartData` object with `plotly_json: str` (Plotly JSON). Frontend parses with `JSON.parse(chart.plotly_json)` then passes `data.data` and `data.layout` to `<Plot>`.
- Analysis status lifecycle: `uploaded → analyzing → analyzed → modeling → completed | error`
- LLM is optional — if `OPENAI_API_KEY` is missing, the service returns a placeholder string instead of crashing.
- ML preprocessing mutates `X_df` in-place for high-cardinality categorical columns (lumps tail categories into "Other" before fitting).
- Backend `col_types` dict (values: `"numeric"`, `"categorical"`, `"boolean"`, `"datetime"`, `"text"`) is computed on every request from the CSV; not cached in DB.
