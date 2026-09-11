import csv
import io
from datetime import datetime
from sqlalchemy.orm import Session
from app.models.entities import ImportJob, ImportStatus, ImportType, InventoryListing, Seller
from app.services.blob_storage_service import write_blob


def process_import(db: Session, job: ImportJob, csv_content: str) -> ImportJob:
    job.status = ImportStatus.processing
    job.started_at = datetime.utcnow()
    db.flush()

    reader = csv.DictReader(io.StringIO(csv_content))
    errors = []
    success = 0
    total = 0
    for idx, row in enumerate(reader, start=2):
        total += 1
        try:
            if job.import_type == ImportType.sellers:
                email = (row.get("seller_email") or "").strip()
                if not email:
                    raise ValueError("seller_email is required")
                existing = db.query(Seller).filter(Seller.seller_email == email).first()
                if existing:
                    existing.company_name = row.get("company_name") or existing.company_name
                    existing.contact_name = row.get("contact_name") or existing.contact_name
                else:
                    db.add(Seller(company_name=row.get("company_name") or "Unknown", contact_name=row.get("contact_name") or "Unknown", seller_email=email))
            elif job.import_type == ImportType.inventory:
                external_id = (row.get("external_id") or "").strip()
                seller_email = (row.get("seller_email") or "").strip()
                seller = db.query(Seller).filter(Seller.seller_email == seller_email).first()
                if not seller:
                    raise ValueError("seller_email does not exist")
                existing = db.query(InventoryListing).filter(InventoryListing.external_id == external_id).first()
                payload = {
                    "seller_id": seller.id,
                    "external_id": external_id,
                    "location": row.get("location") or "Unknown",
                    "property_type": row.get("property_type") or "Unknown",
                    "price_min": float(row.get("price_min") or 0),
                    "price_max": float(row.get("price_max") or 0),
                    "metadata_json": {"source": "csv_import"},
                }
                if existing:
                    for key, value in payload.items():
                        setattr(existing, key, value)
                else:
                    db.add(InventoryListing(**payload))
            success += 1
        except Exception as exc:  # noqa: BLE001
            errors.append({"row": idx, "error": str(exc), "data": row})

    failed = len(errors)
    report_lines = ["row,error,data"] + [f'{e["row"]},"{e["error"].replace('"', "'")}","{e["data"]}"' for e in errors]
    report_path = write_blob(f"reports/{job.id}.csv", "\n".join(report_lines))

    job.total_rows = total
    job.success_rows = success
    job.failed_rows = failed
    job.report_blob_path = report_path
    job.completed_at = datetime.utcnow()
    job.status = ImportStatus.completed if failed == 0 else (ImportStatus.partial if success > 0 else ImportStatus.failed)
    db.flush()
    return job
