from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.rbac import require_roles
from app.db.session import get_db
from app.models.entities import (
    BuyerProfile,
    Event,
    EventSession,
    Registration,
    RegistrationSession,
    RegistrationStatus,
    User,
    WaitlistEntry,
)
from app.schemas.contracts import RegistrationIn
from app.services.waitlist_service import next_waitlist_position
from app.services.audit_service import log_action

router = APIRouter(prefix="/registrations", tags=["registrations"])


def overlaps(a_start, a_end, b_start, b_end):
    return a_start < b_end and b_start < a_end


@router.post("")
def register(payload: RegistrationIn, current_user: User = Depends(require_roles("buyer")), db: Session = Depends(get_db)):
    buyer = db.query(BuyerProfile).filter(BuyerProfile.user_id == current_user.id).first()
    event = db.get(Event, payload.event_id)
    if not buyer or not event:
        raise HTTPException(status_code=404, detail="Buyer or event not found")

    sessions = db.query(EventSession).filter(EventSession.id.in_(payload.session_ids), EventSession.event_id == event.id).all()
    if len(sessions) != len(payload.session_ids):
        raise HTTPException(status_code=400, detail="Invalid session selection")

    for i, s1 in enumerate(sessions):
        for s2 in sessions[i + 1 :]:
            if overlaps(s1.start_time, s1.end_time, s2.start_time, s2.end_time):
                raise HTTPException(status_code=400, detail=f"Session overlap detected: {s1.title} and {s2.title}")

    registered_count = db.query(Registration).filter(Registration.event_id == event.id, Registration.status == RegistrationStatus.registered).count()

    status = RegistrationStatus.registered
    reg = Registration(buyer_id=buyer.id, event_id=event.id)
    if registered_count >= event.capacity:
        status = RegistrationStatus.waitlisted
        reg.status = status
    db.add(reg)
    db.flush()

    for session in sessions:
        db.add(RegistrationSession(registration_id=reg.id, session_id=session.id))

    if status == RegistrationStatus.waitlisted:
        db.add(
            WaitlistEntry(
                event_id=event.id,
                buyer_id=buyer.id,
                position=next_waitlist_position(db, event.id),
            )
        )

    db.commit()
    return {"registration_id": reg.id, "status": reg.status.value}


@router.get("/mine")
def my_registrations(current_user: User = Depends(require_roles("buyer")), db: Session = Depends(get_db)):
    buyer = db.query(BuyerProfile).filter(BuyerProfile.user_id == current_user.id).first()
    regs = db.query(Registration).filter(Registration.buyer_id == buyer.id).all()
    out = []
    for r in regs:
        event = db.get(Event, r.event_id)
        session_links = db.query(RegistrationSession).filter(RegistrationSession.registration_id == r.id).all()
        sessions = [db.get(EventSession, sl.session_id) for sl in session_links]
        out.append(
            {
                "id": r.id,
                "status": r.status.value,
                "event": {"id": event.id, "name": event.name},
                "sessions": [{"id": s.id, "title": s.title} for s in sessions if s],
            }
        )
    return out


@router.post("/waitlist/{entry_id}/promote")
def promote_waitlist(entry_id: str, current_user: User = Depends(require_roles("operations_admin", "super_admin")), db: Session = Depends(get_db)):
    entry = db.get(WaitlistEntry, entry_id)
    if not entry:
        raise HTTPException(status_code=404, detail="Waitlist entry not found")
    entry.status = "promoted"
    reg = (
        db.query(Registration)
        .filter(Registration.event_id == entry.event_id, Registration.buyer_id == entry.buyer_id, Registration.status == RegistrationStatus.waitlisted)
        .first()
    )
    if reg:
        reg.status = RegistrationStatus.registered
    entry.reviewed_by_admin_id = current_user.id
    from datetime import datetime

    entry.reviewed_at = datetime.utcnow()
    log_action(db, current_user.id, "promote", "WaitlistEntry", entry.id, None, {"status": "promoted"})
    db.commit()
    return {"promoted": True}
