from datetime import datetime, timedelta
from app.models.entities import AIInterviewSession, AIReviewQueue, InterviewStatus


def normalize_answers(answers: dict) -> dict:
    location = answers.get("location") or answers.get("preferred_location") or "unspecified"
    budget_min = float(answers.get("budget_min", 0) or 0)
    budget_max = float(answers.get("budget_max", 0) or 0)
    property_type = answers.get("property_type") or "any"
    timeframe = answers.get("timeframe") or "flexible"

    missing = sum(1 for v in [location, property_type, timeframe] if v in ["unspecified", "any", "flexible"]) + (1 if budget_max <= 0 else 0)
    confidence = max(0.2, 1 - (missing * 0.2))
    status = InterviewStatus.completed if confidence >= 0.7 else InterviewStatus.review_required

    return {
        "normalized_location": location,
        "normalized_budget_min": budget_min,
        "normalized_budget_max": budget_max,
        "normalized_property_type": property_type,
        "normalized_timeframe": timeframe,
        "confidence_score": confidence,
        "status": status,
    }


def maybe_create_review_queue_item(session: AIInterviewSession) -> AIReviewQueue | None:
    if session.status != InterviewStatus.review_required:
        return None
    return AIReviewQueue(
        interview_session_id=session.id,
        priority="high" if session.confidence_score < 0.5 else "medium",
        target_response_by=datetime.utcnow() + timedelta(days=1),
    )
