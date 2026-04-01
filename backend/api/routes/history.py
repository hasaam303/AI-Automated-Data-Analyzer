import os
import logging
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from db.database import get_db
from models.schemas import AnalysisSummary
from services.storage_service import storage_service

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("", response_model=List[AnalysisSummary])
def list_analyses(db: Session = Depends(get_db)):
    records = storage_service.list_all(db)
    return [
        AnalysisSummary(
            id=r.id,
            filename=r.filename,
            status=r.status,
            row_count=r.row_count,
            col_count=r.col_count,
            created_at=r.created_at,
            has_ml=r.ml_results is not None,
        )
        for r in records
    ]


@router.delete("/{analysis_id}")
def delete_analysis(analysis_id: str, db: Session = Depends(get_db)):
    record = storage_service.get(db, analysis_id)
    if not record:
        raise HTTPException(status_code=404, detail="Analysis not found.")

    # Remove uploaded file
    if record.file_path and os.path.exists(record.file_path):
        try:
            os.remove(record.file_path)
        except OSError:
            pass

    storage_service.delete(db, analysis_id)
    return {"deleted": analysis_id}
