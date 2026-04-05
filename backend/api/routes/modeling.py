import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from db.database import get_db
from models.schemas import MLResults, RunModelingRequest
from services.ml_service import ml_service
from services.storage_service import storage_service
from utils.data_utils import detect_column_type
from utils.file_utils import load_dataframe

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/{analysis_id}/run", response_model=MLResults)
def run_modeling(
    analysis_id: str,
    body: RunModelingRequest,
    db: Session = Depends(get_db),
):
    record = storage_service.get(db, analysis_id)
    if not record:
        raise HTTPException(status_code=404, detail="Analysis not found.")
    # Require EDA results to exist, regardless of status field (handles stuck states)
    if not record.eda_results:
        raise HTTPException(status_code=409, detail="Run EDA before modeling.")

    storage_service.set_status(db, analysis_id, "modeling")
    try:
        df = load_dataframe(record.file_path)
        if body.target_column not in df.columns:
            raise ValueError(f"Target column '{body.target_column}' not found.")

        col_types = {c: detect_column_type(df[c]) for c in df.columns}
        results = ml_service.run(df, body.target_column, col_types)
        storage_service.save_ml_results(db, analysis_id, results.model_dump())
        logger.info("ML complete for %s (best: %s)", analysis_id, results.best_model)
        return results
    except Exception as exc:
        logger.exception("ML failed for %s", analysis_id)
        storage_service.set_status(db, analysis_id, "error", str(exc))
        raise HTTPException(status_code=500, detail=f"Modeling failed: {exc}")


@router.get("/{analysis_id}", response_model=MLResults)
def get_modeling(analysis_id: str, db: Session = Depends(get_db)):
    record = storage_service.get(db, analysis_id)
    if not record:
        raise HTTPException(status_code=404, detail="Analysis not found.")
    if not record.ml_results:
        raise HTTPException(status_code=404, detail="Modeling has not been run yet.")
    return MLResults(**record.ml_results)
