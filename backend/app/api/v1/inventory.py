from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.rbac import require_roles
from app.db.session import get_db
from app.models.entities import InventoryListing, Seller, User
from app.schemas.contracts import InventoryIn
from app.services.audit_service import log_action

router = APIRouter(prefix="/inventory", tags=["inventory"])


@router.get("")
def list_inventory(_: User = Depends(require_roles("operations_admin", "super_admin")), db: Session = Depends(get_db)):
    rows = db.query(InventoryListing).all()
    return [
        {
            "id": r.id,
            "seller_id": r.seller_id,
            "external_id": r.external_id,
            "location": r.location,
            "property_type": r.property_type,
            "price_min": float(r.price_min),
            "price_max": float(r.price_max),
        }
        for r in rows
    ]


@router.post("")
def create_inventory(payload: InventoryIn, current_user: User = Depends(require_roles("operations_admin", "super_admin")), db: Session = Depends(get_db)):
    if not db.get(Seller, payload.seller_id):
        raise HTTPException(status_code=404, detail="Seller not found")
    listing = InventoryListing(**payload.model_dump())
    db.add(listing)
    db.flush()
    log_action(db, current_user.id, "create", "InventoryListing", listing.id, None, payload.model_dump())
    db.commit()
    return {"id": listing.id}


@router.put("/{listing_id}")
def update_inventory(listing_id: str, payload: InventoryIn, current_user: User = Depends(require_roles("operations_admin", "super_admin")), db: Session = Depends(get_db)):
    listing = db.get(InventoryListing, listing_id)
    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found")
    before = {"location": listing.location, "property_type": listing.property_type, "price_min": float(listing.price_min), "price_max": float(listing.price_max)}
    for key, value in payload.model_dump().items():
        setattr(listing, key, value)
    log_action(db, current_user.id, "update", "InventoryListing", listing.id, before, payload.model_dump())
    db.commit()
    return {"id": listing.id}


@router.delete("/{listing_id}")
def delete_inventory(listing_id: str, current_user: User = Depends(require_roles("operations_admin", "super_admin")), db: Session = Depends(get_db)):
    listing = db.get(InventoryListing, listing_id)
    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found")
    db.delete(listing)
    log_action(db, current_user.id, "delete", "InventoryListing", listing_id)
    db.commit()
    return {"deleted": True}
