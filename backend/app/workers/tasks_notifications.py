from datetime import datetime


def notify_ai_review_queue(interview_session_id: str, priority: str) -> dict:
    """Mock notifier for operations review escalation queue."""
    return {
        "interview_session_id": interview_session_id,
        "priority": priority,
        "sent_at": datetime.utcnow().isoformat(),
        "channel": "mock-email",
    }
