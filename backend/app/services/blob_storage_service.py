from pathlib import Path
from datetime import datetime, timedelta
from app.core.config import settings


def write_blob(relative_path: str, content: str) -> str:
    path = Path(settings.blob_storage_path) / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return str(path)


def signed_url_for_path(path: str, expires_minutes: int = 30) -> str:
    expires = datetime.utcnow() + timedelta(minutes=expires_minutes)
    return f"file://{path}?expires={expires.isoformat()}"
