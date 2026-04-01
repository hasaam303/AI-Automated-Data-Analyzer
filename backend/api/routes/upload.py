import logging

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session

from db.database import get_db
from models.schemas import ColumnInfo, UploadResponse
from services.storage_service import storage_service
from utils.data_utils import compute_column_stats, detect_column_type
from utils.file_utils import load_dataframe, save_upload, validate_csv, validate_file_size

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("", response_model=UploadResponse)
async def upload_csv(file: UploadFile = File(...), db: Session = Depends(get_db)):
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are supported.")

    contents = await file.read()
    try:
        validate_file_size(contents)
        validate_csv(contents)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    analysis_id, file_path = save_upload(contents, file.filename)
    df = load_dataframe(file_path)

    col_types = {col: detect_column_type(df[col]) for col in df.columns}
    columns = [
        ColumnInfo(
            name=col,
            dtype=col_types[col],
            missing_count=int(df[col].isna().sum()),
            missing_pct=round(float(df[col].isna().mean() * 100), 2),
            unique_count=int(df[col].nunique()),
            stats=compute_column_stats(df[col], col_types[col]),
        )
        for col in df.columns
    ]

    storage_service.create(db, analysis_id, file.filename, file_path)
    storage_service.update_upload_info(
        db,
        analysis_id,
        row_count=len(df),
        col_count=len(df.columns),
        column_info=[c.model_dump() for c in columns],
    )

    logger.info("Uploaded %s (%d rows, %d cols) as %s", file.filename, len(df), len(df.columns), analysis_id)

    preview = df.head(8).fillna("").astype(str).to_dict(orient="records")
    return UploadResponse(
        analysis_id=analysis_id,
        filename=file.filename,
        row_count=len(df),
        col_count=len(df.columns),
        preview=preview,
        columns=columns,
        detected_schema={col: col_types[col] for col in df.columns},
    )
