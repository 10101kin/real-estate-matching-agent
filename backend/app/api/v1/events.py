from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.rbac import get_current_user, require_roles
from app.db.session import get_db
from app.models.entities import Event, EventSession, User
from app.schemas.contracts import EventIn, SessionIn
from app.services.audit_service import log_action

router = APIRouter(prefix="/events", tags=["events"])


@router.get("")
def list_events(db: Session = Depends(get_db)):
    events = db.query(Event).all()
    out = []
    for e in events:
        sessions = db.query(EventSession).filter(EventSession.event_id == e.id).all()
        out.append(
            {
                "id": e.id,
                "name": e.name,
                "description": e.description,
                "capacity": e.capacity,
                "registration_open_at": e.registration_open_at,
                "registration_close_at": e.registration_close_at,
                "sessions": [
                    {"id": s.id, "title": s.title, "start_time": s.start_time, "end_time": s.end_time, "capacity": s.capacity}
                    for s in sessions
                ],
            }
        )
    return out


@router.post("")
def create_event(payload: EventIn, current_user: User = Depends(require_roles("operations_admin", "super_admin")), db: Session = Depends(get_db)):
    event = Event(**payload.model_dump())
    db.add(event)
    db.flush()
    log_action(db, current_user.id, "create", "Event", event.id, None, payload.model_dump(mode="json"))
    db.commit()
    return {"id": event.id}


@router.post("/{event_id}/sessions")
def create_session(event_id: str, payload: SessionIn, current_user: User = Depends(require_roles("operations_admin", "super_admin")), db: Session = Depends(get_db)):
    event = db.get(Event, event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    if payload.end_time <= payload.start_time:
        raise HTTPException(status_code=400, detail="Session end must be after start")
    session = EventSession(event_id=event_id, **payload.model_dump())
    db.add(session)
    db.flush()
    log_action(db, current_user.id, "create", "EventSession", session.id, None, payload.model_dump(mode="json"))
    db.commit()
    return {"id": session.id}


@router.put("/{event_id}")
def update_event(event_id: str, payload: EventIn, current_user: User = Depends(require_roles("operations_admin", "super_admin")), db: Session = Depends(get_db)):
    event = db.get(Event, event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    before = {"name": event.name, "description": event.description, "capacity": event.capacity}
    for key, value in payload.model_dump().items():
        setattr(event, key, value)
    log_action(db, current_user.id, "update", "Event", event.id, before, payload.model_dump(mode="json"))
    db.commit()
    return {"id": event.id}


@router.delete("/{event_id}")
def delete_event(event_id: str, current_user: User = Depends(require_roles("operations_admin", "super_admin")), db: Session = Depends(get_db)):
    event = db.get(Event, event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    db.delete(event)
    log_action(db, current_user.id, "delete", "Event", event_id)
    db.commit()
    return {"deleted": True}
