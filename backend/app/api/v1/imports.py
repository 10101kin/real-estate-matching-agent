from fastapi import APIRouter, BackgroundTasks, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session
from app.core.rbac import require_roles
from app.db.session import SessionLocal, get_db
from app.models.entities import ImportJob, ImportType, User
from app.services.audit_service import log_action
from app.services.blob_storage_service import signed_url_for_path, write_blob
from app.services.import_service import process_import

router = APIRouter(prefix="/imports", tags=["imports"])


def _run_import_job(job_id: str, csv_content: str):
    db = SessionLocal()
    try:
        job = db.get(ImportJob, job_id)
        if not job:
            return
        process_import(db, job, csv_content)
        db.commit()
    finally:
        db.close()


@router.post("/upload")
async def upload_csv(
    background_tasks: BackgroundTasks,
    import_type: ImportType = Form(...),
    file: UploadFile = File(...),
    current_user: User = Depends(require_roles("operations_admin", "super_admin")),
    db: Session = Depends(get_db),
):
    content = (await file.read()).decode("utf-8")
    blob_path = write_blob(f"imports/{file.filename}", content)
    job = ImportJob(import_type=import_type, uploaded_blob_path=blob_path)
    db.add(job)
    db.flush()
    log_action(db, current_user.id, "create", "ImportJob", job.id, None, {"type": import_type.value, "file": file.filename})
    db.commit()
    background_tasks.add_task(_run_import_job, job.id, content)
    return {"job_id": job.id}


@router.get("/{job_id}")
def import_status(job_id: str, _: User = Depends(require_roles("operations_admin", "super_admin")), db: Session = Depends(get_db)):
    job = db.get(ImportJob, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Import job not found")
    return {
        "id": job.id,
        "status": job.status.value,
        "total_rows": job.total_rows,
        "success_rows": job.success_rows,
        "failed_rows": job.failed_rows,
        "report_url": signed_url_for_path(job.report_blob_path) if job.report_blob_path else None,
    }
