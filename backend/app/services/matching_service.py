from sqlalchemy.orm import Session
from app.models.entities import AIInterviewSession, InventoryListing, MatchResult

DEFAULT_WEIGHTS = {
    "location": 0.4,
    "budget": 0.3,
    "property_type": 0.2,
    "timeframe": 0.1,
}

WEIGHT_CONFIG = DEFAULT_WEIGHTS.copy()


def set_weights(new_weights: dict):
    WEIGHT_CONFIG.update(new_weights)


def run_matching(db: Session, registration_id: str, interview: AIInterviewSession) -> list[MatchResult]:
    db.query(MatchResult).filter(MatchResult.registration_id == registration_id).delete()
    listings = db.query(InventoryListing).all()
    scored: list[tuple[float, InventoryListing, dict]] = []

    for l in listings:
        location_score = 1.0 if (interview.normalized_location or "").lower() in l.location.lower() else 0.3
        budget_target_min = float(interview.normalized_budget_min or 0)
        budget_target_max = float(interview.normalized_budget_max or 0)
        overlap = max(0.0, min(float(l.price_max), budget_target_max) - max(float(l.price_min), budget_target_min))
        width = max(1.0, budget_target_max - budget_target_min)
        budget_score = min(1.0, overlap / width)
        property_score = 1.0 if (interview.normalized_property_type or "any").lower() in ["any", l.property_type.lower()] else 0.2
        timeframe_score = 1.0 if (interview.normalized_timeframe or "flexible").lower() != "urgent" else 0.8

        breakdown = {
            "location": round(location_score * WEIGHT_CONFIG["location"], 3),
            "budget": round(budget_score * WEIGHT_CONFIG["budget"], 3),
            "property_type": round(property_score * WEIGHT_CONFIG["property_type"], 3),
            "timeframe": round(timeframe_score * WEIGHT_CONFIG["timeframe"], 3),
        }
        total = round(sum(breakdown.values()), 3)
        breakdown["raw"] = {
            "location_match": location_score,
            "budget_overlap": budget_score,
            "property_type_match": property_score,
            "timeframe_fit": timeframe_score,
        }
        scored.append((total, l, breakdown))

    scored.sort(key=lambda x: x[0], reverse=True)
    results = []
    for rank, (score, listing, breakdown) in enumerate(scored[:10], start=1):
        mr = MatchResult(
            registration_id=registration_id,
            seller_id=listing.seller_id,
            listing_id=listing.id,
            total_score=score,
            breakdown_json=breakdown,
            rank=rank,
        )
        db.add(mr)
        results.append(mr)
    db.flush()
    return results
