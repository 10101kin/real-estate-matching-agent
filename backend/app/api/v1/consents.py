from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.rbac import require_roles
from app.db.session import get_db
from app.models.entities import BuyerProfile, ConsentScope, LeadConsent, MatchResult, User
from app.schemas.contracts import ConsentIn

router = APIRouter(prefix="/consents", tags=["consents"])


@router.post("")
def provide_consent(payload: ConsentIn, current_user: User = Depends(require_roles("buyer")), db: Session = Depends(get_db)):
    buyer = db.query(BuyerProfile).filter(BuyerProfile.user_id == current_user.id).first()
    if payload.consent_scope == ConsentScope.per_event and not payload.event_id:
        raise HTTPException(status_code=400, detail="event_id required")
    if payload.consent_scope == ConsentScope.per_match and not payload.match_result_id:
        raise HTTPException(status_code=400, detail="match_result_id required")
    consent = LeadConsent(
        buyer_id=buyer.id,
        event_id=payload.event_id,
        match_result_id=payload.match_result_id,
        consent_scope=payload.consent_scope,
    )
    db.add(consent)
    db.commit()
    return {"id": consent.id, "scope": consent.consent_scope.value}


@router.get("/mine")
def my_consents(current_user: User = Depends(require_roles("buyer")), db: Session = Depends(get_db)):
    buyer = db.query(BuyerProfile).filter(BuyerProfile.user_id == current_user.id).first()
    consents = db.query(LeadConsent).filter(LeadConsent.buyer_id == buyer.id, LeadConsent.revoked_at.is_(None)).all()
    return [{"id": c.id, "scope": c.consent_scope.value, "event_id": c.event_id, "match_result_id": c.match_result_id} for c in consents]
