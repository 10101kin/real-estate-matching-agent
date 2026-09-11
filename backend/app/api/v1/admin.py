from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.rbac import require_roles
from app.db.session import get_db
from app.models.entities import AIReviewQueue, AuditLog, Seller, User, WaitlistEntry
from app.schemas.contracts import SellerIn
from app.services.audit_service import log_action

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/dashboard")
def dashboard(_: User = Depends(require_roles("operations_admin", "super_admin")), db: Session = Depends(get_db)):
    return {
        "sellers": db.query(Seller).count(),
        "waitlist_open": db.query(WaitlistEntry).filter(WaitlistEntry.status == "waiting").count(),
        "ai_review_open": db.query(AIReviewQueue).filter(AIReviewQueue.status == "open").count(),
        "audit_logs": db.query(AuditLog).count(),
    }


@router.get("/sellers")
def list_sellers(_: User = Depends(require_roles("operations_admin", "super_admin")), db: Session = Depends(get_db)):
    rows = db.query(Seller).all()
    return [{"id": s.id, "company_name": s.company_name, "contact_name": s.contact_name, "seller_email": s.seller_email} for s in rows]


@router.post("/sellers")
def create_seller(payload: SellerIn, current_user: User = Depends(require_roles("operations_admin", "super_admin")), db: Session = Depends(get_db)):
    seller = Seller(**payload.model_dump())
    db.add(seller)
    db.flush()
    log_action(db, current_user.id, "create", "Seller", seller.id, None, payload.model_dump())
    db.commit()
    return {"id": seller.id}


@router.put("/sellers/{seller_id}")
def update_seller(seller_id: str, payload: SellerIn, current_user: User = Depends(require_roles("operations_admin", "super_admin")), db: Session = Depends(get_db)):
    seller = db.get(Seller, seller_id)
    if not seller:
        raise HTTPException(status_code=404, detail="Seller not found")
    before = {"company_name": seller.company_name, "contact_name": seller.contact_name, "seller_email": seller.seller_email}
    for key, value in payload.model_dump().items():
        setattr(seller, key, value)
    log_action(db, current_user.id, "update", "Seller", seller.id, before, payload.model_dump())
    db.commit()
    return {"id": seller.id}


@router.delete("/sellers/{seller_id}")
def delete_seller(seller_id: str, current_user: User = Depends(require_roles("operations_admin", "super_admin")), db: Session = Depends(get_db)):
    seller = db.get(Seller, seller_id)
    if not seller:
        raise HTTPException(status_code=404, detail="Seller not found")
    db.delete(seller)
    log_action(db, current_user.id, "delete", "Seller", seller_id)
    db.commit()
    return {"deleted": True}


@router.get("/waitlist")
def waitlist(_: User = Depends(require_roles("operations_admin", "super_admin")), db: Session = Depends(get_db)):
    entries = db.query(WaitlistEntry).all()
    return [{"id": e.id, "event_id": e.event_id, "buyer_id": e.buyer_id, "position": e.position, "status": e.status.value} for e in entries]


@router.get("/ai-review-queue")
def ai_review_queue(_: User = Depends(require_roles("operations_admin", "super_admin")), db: Session = Depends(get_db)):
    rows = db.query(AIReviewQueue).all()
    return [
        {
            "id": r.id,
            "interview_session_id": r.interview_session_id,
            "priority": r.priority,
            "target_response_by": r.target_response_by,
            "status": r.status.value,
        }
        for r in rows
    ]


@router.get("/audit-logs")
def audit_logs(_: User = Depends(require_roles("operations_admin", "super_admin")), db: Session = Depends(get_db)):
    rows = db.query(AuditLog).order_by(AuditLog.created_at.desc()).limit(200).all()
    return [
        {
            "id": r.id,
            "actor_user_id": r.actor_user_id,
            "action_type": r.action_type,
            "entity_type": r.entity_type,
            "entity_id": r.entity_id,
            "created_at": r.created_at,
        }
        for r in rows
    ]
