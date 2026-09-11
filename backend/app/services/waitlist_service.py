from sqlalchemy.orm import Session
from app.models.entities import WaitlistEntry


def next_waitlist_position(db: Session, event_id: str) -> int:
    max_pos = db.query(WaitlistEntry.position).filter(WaitlistEntry.event_id == event_id).order_by(WaitlistEntry.position.desc()).first()
    return (max_pos[0] if max_pos else 0) + 1
