import logging

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from sqlalchemy.orm import Session

from db.database import get_db
from models.schemas import EDAResults, RunAnalysisRequest
from services.analysis_service import analysis_service
from services.storage_service import storage_service
from utils.file_utils import load_dataframe

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/{analysis_id}/run", response_model=EDAResults)
def run_analysis(
    analysis_id: str,
    body: RunAnalysisRequest,
    db: Session = Depends(get_db),
):
    record = storage_service.get(db, analysis_id)
    if not record:
        raise HTTPException(status_code=404, detail="Analysis not found.")
    # Allow re-running EDA from any state (handles stuck "analyzing" after crashes)

    storage_service.set_status(db, analysis_id, "analyzing")
    try:
        df = load_dataframe(record.file_path)
        results = analysis_service.run(df, target_column=body.target_column)
        storage_service.save_eda_results(db, analysis_id, results.model_dump())
        logger.info("EDA complete for %s", analysis_id)
        return results
    except Exception as exc:
        logger.exception("EDA failed for %s", analysis_id)
        storage_service.set_status(db, analysis_id, "error", str(exc))
        raise HTTPException(status_code=500, detail=f"Analysis failed: {exc}")


@router.get("/{analysis_id}", response_model=EDAResults)
def get_analysis(analysis_id: str, db: Session = Depends(get_db)):
    record = storage_service.get(db, analysis_id)
    if not record:
        raise HTTPException(status_code=404, detail="Analysis not found.")
    if not record.eda_results:
        raise HTTPException(status_code=404, detail="Analysis has not been run yet.")
    return EDAResults(**record.eda_results)
