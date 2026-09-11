from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.rbac import require_roles
from app.db.session import get_db
from app.models.entities import (
    BuyerProfile,
    LeadConsent,
    MatchResult,
    Registration,
    Seller,
    User,
    InventoryListing,
)

router = APIRouter(prefix="/sellers", tags=["sellers"])


@router.get("/me")
def seller_me(current_user: User = Depends(require_roles("seller")), db: Session = Depends(get_db)):
    seller = db.query(Seller).filter(Seller.user_id == current_user.id).first()
    if not seller:
        raise HTTPException(status_code=404, detail="Seller profile missing")
    return {"id": seller.id, "company_name": seller.company_name, "contact_name": seller.contact_name, "seller_email": seller.seller_email}


@router.get("/inventory")
def seller_inventory(current_user: User = Depends(require_roles("seller")), db: Session = Depends(get_db)):
    seller = db.query(Seller).filter(Seller.user_id == current_user.id).first()
    items = db.query(InventoryListing).filter(InventoryListing.seller_id == seller.id).all()
    return [
        {
            "id": i.id,
            "external_id": i.external_id,
            "location": i.location,
            "property_type": i.property_type,
            "price_min": float(i.price_min),
            "price_max": float(i.price_max),
        }
        for i in items
    ]


@router.get("/leads")
def seller_leads(current_user: User = Depends(require_roles("seller")), db: Session = Depends(get_db)):
    seller = db.query(Seller).filter(Seller.user_id == current_user.id).first()
    matches = db.query(MatchResult).filter(MatchResult.seller_id == seller.id).all()

    lead_payload = []
    for m in matches:
        reg = db.get(Registration, m.registration_id)
        if not reg:
            continue
        per_match = (
            db.query(LeadConsent)
            .filter(LeadConsent.match_result_id == m.id, LeadConsent.revoked_at.is_(None))
            .first()
        )
        per_event = (
            db.query(LeadConsent)
            .filter(LeadConsent.event_id == reg.event_id, LeadConsent.revoked_at.is_(None))
            .first()
        )
        if not (per_match or per_event):
            continue
        buyer = db.get(BuyerProfile, reg.buyer_id)
        lead_payload.append(
            {
                "match_result_id": m.id,
                "registration_id": reg.id,
                "event_id": reg.event_id,
                "buyer": {"id": buyer.id, "full_name": buyer.full_name, "phone": buyer.phone},
                "score": m.total_score,
            }
        )
    return lead_payload
