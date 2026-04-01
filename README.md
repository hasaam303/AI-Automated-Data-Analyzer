# AI Data Analyst

A full-stack AI-powered data analysis platform. Upload a CSV and get automated EDA, interactive visualizations, machine learning baselines, and GPT-generated business insights — all in one polished interface.

---

## Features

- **Drag-and-drop CSV upload** with schema preview and column type detection
- **Automated EDA** — summary stats, missing value analysis, outlier detection, correlation analysis
- **Interactive charts** — histograms, boxplots, bar charts, correlation heatmaps, scatter plots (Plotly)
- **AI Insights** — GPT-4o-mini translates raw findings into plain-English business narratives
- **ML Pipeline** — auto-selects classification or regression, trains 3 baseline models, ranks by best metric
- **Feature importance** visualized for tree-based models
- **Agent-style pipeline panel** — shows what analysis steps the system decided to run and why
- **Downloadable Markdown report** with executive summary, findings, and recommendations
- **Analysis history** with delete support (SQLite-backed)

---

## Architecture

```
ai-data-analyst/
├── backend/                  FastAPI Python backend
│   ├── api/routes/           Upload, Analysis, Modeling, Report, History endpoints
│   ├── services/             Analysis, ML, LLM, Report, Storage service classes
│   ├── ml/                   Preprocessor, Classifier, Regressor, Evaluator modules
│   ├── visualization/        Plotly chart generators
│   ├── utils/                Column type detection, file I/O helpers
│   ├── db/                   SQLAlchemy + SQLite models
│   └── models/schemas.py     Pydantic request/response schemas
├── frontend/                 React + Vite + Tailwind frontend
│   └── src/
│       ├── pages/            Home, Analysis, History
│       ├── components/       Upload, DataPreview, Pipeline, Charts, Insights, ModelResults, Report
│       ├── store/            Zustand global state
│       └── services/api.js   Axios API client
├── docker-compose.yml
└── .env.example
```

### Data flow

1. `POST /api/upload` → saves CSV, returns schema preview + `analysis_id`
2. `POST /api/analysis/{id}/run` → runs full EDA + LLM insights, returns `EDAResults`
3. `POST /api/modeling/{id}/run` → trains ML models, returns `MLResults`
4. `GET /api/report/{id}` → generates/caches full LLM report

---

## Quick Start (Local Dev)

### Prerequisites
- Python 3.11+
- Node.js 20+
- OpenAI API key

### Backend

```bash
cd backend
python -m venv venv && source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp ../.env.example .env
# Edit .env — add your OPENAI_API_KEY
uvicorn main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Open [http://localhost:5173](http://localhost:5173).

---

## Docker

```bash
cp .env.example .env
# Edit .env with your OPENAI_API_KEY
docker-compose up --build
```

App is available at [http://localhost](http://localhost).

---

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `OPENAI_API_KEY` | OpenAI API key (required for AI insights) | — |
| `LLM_MODEL` | Model to use | `gpt-4o-mini` |
| `MAX_FILE_SIZE_MB` | Upload size limit | `50` |
| `DEBUG` | Enable debug logging | `false` |

---

## Deployment (Render + Vercel)

GitHub Pages can't run the Python backend, so the recommended free stack is **Render** (backend) + **Vercel** (frontend).

### 1. Push to GitHub

```bash
git init
git add .
git commit -m "initial commit"
git remote add origin https://github.com/your-username/ai-data-analyst.git
git push -u origin main
```

### 2. Deploy Backend → Render.com

1. Go to [render.com](https://render.com) → **New Web Service** → connect your GitHub repo
2. Render will detect `render.yaml` automatically
3. In **Environment Variables**, set:
   - `OPENAI_API_KEY` = your key
   - `CORS_ORIGINS` = `["https://your-app.vercel.app"]` (fill in after Vercel deploy)
4. Deploy — your backend URL will be `https://ai-data-analyst-backend.onrender.com`

> **Note:** Render's free tier has no persistent disk. SQLite and uploaded files reset on each redeploy. For persistent history, upgrade to a paid plan or swap SQLite for a hosted database (e.g. Supabase).

### 3. Deploy Frontend → Vercel

1. Go to [vercel.com](https://vercel.com) → **New Project** → import your GitHub repo
2. Set **Root Directory** to `frontend`
3. Add **Environment Variable**:
   - `VITE_API_URL` = `https://ai-data-analyst-backend.onrender.com/api`
4. Deploy

### 4. Update CORS on Render

Once Vercel gives you your URL (e.g. `https://ai-data-analyst.vercel.app`), go back to Render and update:
```
CORS_ORIGINS=["https://ai-data-analyst.vercel.app"]
```

---

## ML Details

The modeling engine:
- Detects task type from the target column's dtype (numeric → regression, categorical → classification)
- Preprocesses: median imputation + scaling for numerics, one-hot encoding for categoricals
- Trains 3 baselines: Logistic/Ridge Regression, Random Forest, Gradient Boosting
- Ranks by ROC-AUC (classification) or R² (regression)
- Returns feature importance aggregated to original column names
