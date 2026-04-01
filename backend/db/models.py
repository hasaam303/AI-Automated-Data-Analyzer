import uuid
from sqlalchemy import Column, DateTime, Integer, JSON, String, Text
from sqlalchemy.sql import func

from db.database import Base


class Analysis(Base):
    __tablename__ = "analyses"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    filename = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    status = Column(String, default="uploaded")
    # Status lifecycle: uploaded → analyzing → analyzed → modeling → completed | error

    row_count = Column(Integer)
    col_count = Column(Integer)

    column_info = Column(JSON)    # List[ColumnInfo dicts]
    eda_results = Column(JSON)    # Full EDA output
    ml_results = Column(JSON)     # ML pipeline output
    report = Column(JSON)         # Generated report

    error_message = Column(Text)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
