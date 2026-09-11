from app.db.session import SessionLocal
from app.models.entities import ImportJob
from app.services.import_service import process_import


def run_import_job(job_id: str, csv_content: str) -> None:
    db = SessionLocal()
    try:
        job = db.get(ImportJob, job_id)
        if not job:
            return
        process_import(db, job, csv_content)
        db.commit()
    finally:
        db.close()
