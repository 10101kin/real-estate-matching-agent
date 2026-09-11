from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.rbac import require_roles
from app.db.session import get_db
from app.models.entities import AIInterviewSession, AIReviewQueue, BuyerProfile, User
from app.schemas.contracts import InterviewUpsertIn
from app.services.ai_intake_service import maybe_create_review_queue_item, normalize_answers

router = APIRouter(prefix="/buyers", tags=["buyers"])


@router.post("/interview")
def upsert_interview(payload: InterviewUpsertIn, current_user: User = Depends(require_roles("buyer")), db: Session = Depends(get_db)):
    buyer = db.query(BuyerProfile).filter(BuyerProfile.user_id == current_user.id).first()
    if not buyer:
        raise HTTPException(status_code=404, detail="Buyer profile missing")

    session = (
        db.query(AIInterviewSession)
        .filter(AIInterviewSession.buyer_id == buyer.id, AIInterviewSession.registration_id == payload.registration_id)
        .first()
    )
    if not session:
        session = AIInterviewSession(buyer_id=buyer.id, registration_id=payload.registration_id, state_json={})
        db.add(session)
        db.flush()

    existing = dict(session.state_json or {})
    existing.update(payload.answers)
    session.state_json = existing

    normalized = normalize_answers(existing)
    for key, value in normalized.items():
        setattr(session, key, value)

    from datetime import datetime

    session.last_resumed_at = datetime.utcnow()

    queue_item = db.query(AIReviewQueue).filter(AIReviewQueue.interview_session_id == session.id).first()
    if queue_item:
        db.delete(queue_item)

    maybe_q = maybe_create_review_queue_item(session)
    if maybe_q:
        db.add(maybe_q)

    db.commit()
    return {
        "interview_session_id": session.id,
        "status": session.status.value,
        "confidence_score": session.confidence_score,
        "normalized": {
            "location": session.normalized_location,
            "budget_min": float(session.normalized_budget_min or 0),
            "budget_max": float(session.normalized_budget_max or 0),
            "property_type": session.normalized_property_type,
            "timeframe": session.normalized_timeframe,
        },
    }


@router.get("/interview/{registration_id}")
def get_interview(registration_id: str, current_user: User = Depends(require_roles("buyer")), db: Session = Depends(get_db)):
    buyer = db.query(BuyerProfile).filter(BuyerProfile.user_id == current_user.id).first()
    session = (
        db.query(AIInterviewSession)
        .filter(AIInterviewSession.buyer_id == buyer.id, AIInterviewSession.registration_id == registration_id)
        .first()
    )
    if not session:
        raise HTTPException(status_code=404, detail="Interview not found")
    return {
        "id": session.id,
        "status": session.status.value,
        "answers": session.state_json,
        "normalized": {
            "location": session.normalized_location,
            "budget_min": float(session.normalized_budget_min or 0),
            "budget_max": float(session.normalized_budget_max or 0),
            "property_type": session.normalized_property_type,
            "timeframe": session.normalized_timeframe,
        },
        "confidence": session.confidence_score,
    }
