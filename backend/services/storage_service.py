import logging
from typing import List, Optional

from sqlalchemy.orm import Session

from db.models import Analysis

logger = logging.getLogger(__name__)


class StorageService:
    def create(self, db: Session, analysis_id: str, filename: str, file_path: str) -> Analysis:
        record = Analysis(id=analysis_id, filename=filename, file_path=file_path, status="uploaded")
        db.add(record)
        db.commit()
        db.refresh(record)
        return record

    def get(self, db: Session, analysis_id: str) -> Optional[Analysis]:
        return db.query(Analysis).filter(Analysis.id == analysis_id).first()

    def list_all(self, db: Session, limit: int = 50) -> List[Analysis]:
        return db.query(Analysis).order_by(Analysis.created_at.desc()).limit(limit).all()

    def update_upload_info(self, db: Session, analysis_id: str, row_count: int, col_count: int, column_info: list) -> None:
        record = self.get(db, analysis_id)
        if record:
            record.row_count = row_count
            record.col_count = col_count
            record.column_info = column_info
            db.commit()

    def set_status(self, db: Session, analysis_id: str, status: str, error: str = None) -> None:
        record = self.get(db, analysis_id)
        if record:
            record.status = status
            if error:
                record.error_message = error
            db.commit()

    def save_eda_results(self, db: Session, analysis_id: str, eda_results: dict) -> None:
        record = self.get(db, analysis_id)
        if record:
            record.eda_results = eda_results
            record.status = "analyzed"
            db.commit()

    def save_ml_results(self, db: Session, analysis_id: str, ml_results: dict) -> None:
        record = self.get(db, analysis_id)
        if record:
            record.ml_results = ml_results
            record.status = "completed"
            db.commit()

    def save_report(self, db: Session, analysis_id: str, report: dict) -> None:
        record = self.get(db, analysis_id)
        if record:
            record.report = report
            db.commit()

    def delete(self, db: Session, analysis_id: str) -> bool:
        record = self.get(db, analysis_id)
        if record:
            db.delete(record)
            db.commit()
            return True
        return False


storage_service = StorageService()
