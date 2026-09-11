from __future__ import annotations
import enum
import uuid
from datetime import datetime
from sqlalchemy import Boolean, DateTime, Enum, Float, ForeignKey, Integer, Numeric, String, Text, JSON, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


def uuid_str() -> str:
    return str(uuid.uuid4())


class RoleEnum(str, enum.Enum):
    buyer = "buyer"
    seller = "seller"
    operations_admin = "operations_admin"
    super_admin = "super_admin"


class RegistrationStatus(str, enum.Enum):
    registered = "registered"
    waitlisted = "waitlisted"
    cancelled = "cancelled"


class WaitlistStatus(str, enum.Enum):
    waiting = "waiting"
    promoted = "promoted"
    rejected = "rejected"


class InterviewStatus(str, enum.Enum):
    in_progress = "in_progress"
    completed = "completed"
    review_required = "review_required"


class ReviewStatus(str, enum.Enum):
    open = "open"
    in_review = "in_review"
    resolved = "resolved"


class ConsentScope(str, enum.Enum):
    per_event = "per_event"
    per_match = "per_match"


class ImportType(str, enum.Enum):
    sellers = "sellers"
    inventory = "inventory"


class ImportStatus(str, enum.Enum):
    queued = "queued"
    processing = "processing"
    completed = "completed"
    failed = "failed"
    partial = "partial"


class User(Base):
    __tablename__ = "users"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=uuid_str)
    email: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String, nullable=False)
    role: Mapped[RoleEnum] = mapped_column(Enum(RoleEnum), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class BuyerProfile(Base):
    __tablename__ = "buyer_profiles"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=uuid_str)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), unique=True)
    full_name: Mapped[str] = mapped_column(String)
    phone: Mapped[str | None] = mapped_column(String, nullable=True)


class Seller(Base):
    __tablename__ = "sellers"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=uuid_str)
    user_id: Mapped[str | None] = mapped_column(ForeignKey("users.id"), nullable=True, unique=True)
    company_name: Mapped[str] = mapped_column(String)
    contact_name: Mapped[str] = mapped_column(String)
    seller_email: Mapped[str] = mapped_column(String, unique=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class InventoryListing(Base):
    __tablename__ = "inventory_listings"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=uuid_str)
    seller_id: Mapped[str] = mapped_column(ForeignKey("sellers.id"))
    external_id: Mapped[str] = mapped_column(String, unique=True)
    location: Mapped[str] = mapped_column(String)
    property_type: Mapped[str] = mapped_column(String)
    price_min: Mapped[float] = mapped_column(Numeric(12, 2))
    price_max: Mapped[float] = mapped_column(Numeric(12, 2))
    metadata_json: Mapped[dict] = mapped_column(JSON, default=dict)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Event(Base):
    __tablename__ = "events"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=uuid_str)
    name: Mapped[str] = mapped_column(String)
    description: Mapped[str] = mapped_column(Text)
    capacity: Mapped[int] = mapped_column(Integer)
    registration_open_at: Mapped[datetime] = mapped_column(DateTime)
    registration_close_at: Mapped[datetime] = mapped_column(DateTime)


class EventSession(Base):
    __tablename__ = "event_sessions"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=uuid_str)
    event_id: Mapped[str] = mapped_column(ForeignKey("events.id"))
    title: Mapped[str] = mapped_column(String)
    start_time: Mapped[datetime] = mapped_column(DateTime)
    end_time: Mapped[datetime] = mapped_column(DateTime)
    capacity: Mapped[int] = mapped_column(Integer, default=100)


class Registration(Base):
    __tablename__ = "registrations"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=uuid_str)
    buyer_id: Mapped[str] = mapped_column(ForeignKey("buyer_profiles.id"))
    event_id: Mapped[str] = mapped_column(ForeignKey("events.id"))
    status: Mapped[RegistrationStatus] = mapped_column(Enum(RegistrationStatus), default=RegistrationStatus.registered)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class RegistrationSession(Base):
    __tablename__ = "registration_sessions"
    registration_id: Mapped[str] = mapped_column(ForeignKey("registrations.id"), primary_key=True)
    session_id: Mapped[str] = mapped_column(ForeignKey("event_sessions.id"), primary_key=True)


class WaitlistEntry(Base):
    __tablename__ = "waitlist_entries"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=uuid_str)
    event_id: Mapped[str] = mapped_column(ForeignKey("events.id"))
    buyer_id: Mapped[str] = mapped_column(ForeignKey("buyer_profiles.id"))
    position: Mapped[int] = mapped_column(Integer)
    status: Mapped[WaitlistStatus] = mapped_column(Enum(WaitlistStatus), default=WaitlistStatus.waiting)
    reviewed_by_admin_id: Mapped[str | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)


class AIInterviewSession(Base):
    __tablename__ = "ai_interview_sessions"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=uuid_str)
    buyer_id: Mapped[str] = mapped_column(ForeignKey("buyer_profiles.id"))
    registration_id: Mapped[str | None] = mapped_column(ForeignKey("registrations.id"), nullable=True)
    state_json: Mapped[dict] = mapped_column(JSON, default=dict)
    normalized_location: Mapped[str | None] = mapped_column(String, nullable=True)
    normalized_budget_min: Mapped[float | None] = mapped_column(Numeric(12, 2), nullable=True)
    normalized_budget_max: Mapped[float | None] = mapped_column(Numeric(12, 2), nullable=True)
    normalized_property_type: Mapped[str | None] = mapped_column(String, nullable=True)
    normalized_timeframe: Mapped[str | None] = mapped_column(String, nullable=True)
    confidence_score: Mapped[float] = mapped_column(Float, default=0.0)
    status: Mapped[InterviewStatus] = mapped_column(Enum(InterviewStatus), default=InterviewStatus.in_progress)
    last_resumed_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class AIReviewQueue(Base):
    __tablename__ = "ai_review_queue"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=uuid_str)
    interview_session_id: Mapped[str] = mapped_column(ForeignKey("ai_interview_sessions.id"), unique=True)
    assigned_role: Mapped[str] = mapped_column(String, default="operations_admin")
    priority: Mapped[str] = mapped_column(String, default="medium")
    target_response_by: Mapped[datetime] = mapped_column(DateTime)
    status: Mapped[ReviewStatus] = mapped_column(Enum(ReviewStatus), default=ReviewStatus.open)


class MatchResult(Base):
    __tablename__ = "match_results"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=uuid_str)
    registration_id: Mapped[str] = mapped_column(ForeignKey("registrations.id"))
    seller_id: Mapped[str] = mapped_column(ForeignKey("sellers.id"))
    listing_id: Mapped[str] = mapped_column(ForeignKey("inventory_listings.id"))
    total_score: Mapped[float] = mapped_column(Float)
    breakdown_json: Mapped[dict] = mapped_column(JSON, default=dict)
    rank: Mapped[int] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class LeadConsent(Base):
    __tablename__ = "lead_consents"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=uuid_str)
    buyer_id: Mapped[str] = mapped_column(ForeignKey("buyer_profiles.id"))
    event_id: Mapped[str | None] = mapped_column(ForeignKey("events.id"), nullable=True)
    match_result_id: Mapped[str | None] = mapped_column(ForeignKey("match_results.id"), nullable=True)
    consent_scope: Mapped[ConsentScope] = mapped_column(Enum(ConsentScope))
    consented_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)


class ImportJob(Base):
    __tablename__ = "import_jobs"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=uuid_str)
    import_type: Mapped[ImportType] = mapped_column(Enum(ImportType))
    uploaded_blob_path: Mapped[str] = mapped_column(String)
    status: Mapped[ImportStatus] = mapped_column(Enum(ImportStatus), default=ImportStatus.queued)
    total_rows: Mapped[int] = mapped_column(Integer, default=0)
    success_rows: Mapped[int] = mapped_column(Integer, default=0)
    failed_rows: Mapped[int] = mapped_column(Integer, default=0)
    report_blob_path: Mapped[str | None] = mapped_column(String, nullable=True)
    started_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)


class AuditLog(Base):
    __tablename__ = "audit_logs"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=uuid_str)
    actor_user_id: Mapped[str | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    action_type: Mapped[str] = mapped_column(String)
    entity_type: Mapped[str] = mapped_column(String)
    entity_id: Mapped[str] = mapped_column(String)
    before_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    after_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
