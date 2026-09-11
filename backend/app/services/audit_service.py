from typing import Any
from sqlalchemy.orm import Session
from app.models.entities import AuditLog


def log_action(db: Session, actor_user_id: str | None, action_type: str, entity_type: str, entity_id: str, before: Any = None, after: Any = None):
    db.add(
        AuditLog(
            actor_user_id=actor_user_id,
            action_type=action_type,
            entity_type=entity_type,
            entity_id=str(entity_id),
            before_json=before,
            after_json=after,
        )
    )
