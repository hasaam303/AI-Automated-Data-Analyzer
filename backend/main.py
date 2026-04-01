import logging
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import settings
from db.database import init_db
from api.routes import analysis, history, modeling, report, upload

logging.basicConfig(
    level=logging.DEBUG if settings.debug else logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(name)s — %(message)s",
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="AI Data Analyst API",
    version="1.0.0",
    description="Automated data analysis, visualization, and ML pipeline powered by AI.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ensure required directories exist at startup
Path(settings.upload_dir).mkdir(parents=True, exist_ok=True)
Path(settings.data_dir).mkdir(parents=True, exist_ok=True)


@app.on_event("startup")
def startup():
    init_db()
    logger.info("AI Data Analyst API ready — model: %s", settings.llm_model)


app.include_router(upload.router,   prefix="/api/upload",   tags=["upload"])
app.include_router(analysis.router, prefix="/api/analysis", tags=["analysis"])
app.include_router(modeling.router, prefix="/api/modeling", tags=["modeling"])
app.include_router(report.router,   prefix="/api/report",   tags=["report"])
app.include_router(history.router,  prefix="/api/history",  tags=["history"])


@app.get("/health", tags=["system"])
def health():
    return {"status": "ok", "model": settings.llm_model}
