from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.rbac import require_roles
from app.db.session import get_db
from app.models.entities import AIInterviewSession, BuyerProfile, MatchResult, Registration, User
from app.schemas.contracts import WeightsIn
from app.services.matching_service import run_matching, set_weights, WEIGHT_CONFIG

router = APIRouter(prefix="/matching", tags=["matching"])


@router.post("/run/{registration_id}")
def run(registration_id: str, current_user: User = Depends(require_roles("buyer")), db: Session = Depends(get_db)):
    buyer = db.query(BuyerProfile).filter(BuyerProfile.user_id == current_user.id).first()
    reg = db.get(Registration, registration_id)
    if not reg or reg.buyer_id != buyer.id:
        raise HTTPException(status_code=404, detail="Registration not found")
    interview = (
        db.query(AIInterviewSession)
        .filter(AIInterviewSession.registration_id == registration_id, AIInterviewSession.buyer_id == buyer.id)
        .order_by(AIInterviewSession.last_resumed_at.desc())
        .first()
    )
    if not interview:
        raise HTTPException(status_code=400, detail="Interview required before matching")
    results = run_matching(db, registration_id, interview)
    db.commit()
    return [
        {
            "id": r.id,
            "rank": r.rank,
            "score": r.total_score,
            "seller_id": r.seller_id,
            "listing_id": r.listing_id,
            "breakdown": r.breakdown_json,
        }
        for r in results
    ]


@router.get("/{registration_id}")
def get_results(registration_id: str, current_user: User = Depends(require_roles("buyer", "operations_admin", "super_admin")), db: Session = Depends(get_db)):
    rows = db.query(MatchResult).filter(MatchResult.registration_id == registration_id).order_by(MatchResult.rank).all()
    return [
        {
            "id": r.id,
            "rank": r.rank,
            "score": r.total_score,
            "seller_id": r.seller_id,
            "listing_id": r.listing_id,
            "breakdown": r.breakdown_json,
        }
        for r in rows
    ]


@router.get("/weights/current")
def current_weights(_: User = Depends(require_roles("operations_admin", "super_admin"))):
    return WEIGHT_CONFIG


@router.put("/weights/current")
def update_weights(payload: WeightsIn, _: User = Depends(require_roles("operations_admin", "super_admin"))):
    set_weights(payload.model_dump())
    return WEIGHT_CONFIG
