import os
import uuid
from pathlib import Path
from typing import Tuple

import pandas as pd

from config import settings


def save_upload(file_bytes: bytes, filename: str) -> Tuple[str, str]:
    """Save uploaded bytes to disk. Returns (analysis_id, file_path)."""
    os.makedirs(settings.upload_dir, exist_ok=True)
    analysis_id = str(uuid.uuid4())
    safe_name = f"{analysis_id}_{Path(filename).name}"
    file_path = os.path.join(settings.upload_dir, safe_name)
    with open(file_path, "wb") as f:
        f.write(file_bytes)
    return analysis_id, file_path


def load_dataframe(file_path: str) -> pd.DataFrame:
    """Load CSV into a DataFrame with sensible defaults."""
    df = pd.read_csv(file_path, low_memory=False)
    # Strip whitespace from column names
    df.columns = [c.strip() for c in df.columns]
    return df


def validate_file_size(file_bytes: bytes) -> None:
    max_bytes = settings.max_file_size_mb * 1024 * 1024
    if len(file_bytes) > max_bytes:
        raise ValueError(
            f"File exceeds maximum size of {settings.max_file_size_mb} MB."
        )


def validate_csv(file_bytes: bytes) -> None:
    """Quick sanity check that the bytes look like a CSV."""
    try:
        import io
        pd.read_csv(io.BytesIO(file_bytes), nrows=5)
    except Exception as exc:
        raise ValueError(f"Could not parse file as CSV: {exc}") from exc
