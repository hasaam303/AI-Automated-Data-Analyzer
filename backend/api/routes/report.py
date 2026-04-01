import logging

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from db.database import get_db
from models.schemas import Report
from services.report_service import report_service
from services.storage_service import storage_service

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/{analysis_id}", response_model=Report)
def get_report(analysis_id: str, db: Session = Depends(get_db)):
    record = storage_service.get(db, analysis_id)
    if not record:
        raise HTTPException(status_code=404, detail="Analysis not found.")
    if not record.eda_results:
        raise HTTPException(status_code=404, detail="Run EDA first.")

    # Return cached report if available
    if record.report:
        return Report(**record.report)

    try:
        report = report_service.generate(
            analysis_id=analysis_id,
            filename=record.filename,
            eda_results=record.eda_results,
            ml_results=record.ml_results,
        )
        storage_service.save_report(db, analysis_id, report.model_dump())
        return report
    except Exception as exc:
        logger.exception("Report generation failed for %s", analysis_id)
        raise HTTPException(status_code=500, detail=f"Report generation failed: {exc}")
