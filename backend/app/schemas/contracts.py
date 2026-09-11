from datetime import datetime
from typing import Any, Literal, Optional
from pydantic import BaseModel, EmailStr, Field


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6)
    role: Literal["buyer", "seller", "operations_admin", "super_admin"]
    full_name: Optional[str] = None
    phone: Optional[str] = None
    company_name: Optional[str] = None
    contact_name: Optional[str] = None


class EventIn(BaseModel):
    name: str
    description: str
    capacity: int
    registration_open_at: datetime
    registration_close_at: datetime


class SessionIn(BaseModel):
    title: str
    start_time: datetime
    end_time: datetime
    capacity: int = 100


class SellerIn(BaseModel):
    company_name: str
    contact_name: str
    seller_email: EmailStr


class InventoryIn(BaseModel):
    seller_id: str
    external_id: str
    location: str
    property_type: str
    price_min: float
    price_max: float
    metadata_json: dict = {}


class RegistrationIn(BaseModel):
    event_id: str
    session_ids: list[str]


class InterviewUpsertIn(BaseModel):
    registration_id: Optional[str] = None
    answers: dict[str, Any] = {}


class ConsentIn(BaseModel):
    consent_scope: Literal["per_event", "per_match"]
    event_id: Optional[str] = None
    match_result_id: Optional[str] = None


class WeightsIn(BaseModel):
    location: float = 0.4
    budget: float = 0.3
    property_type: float = 0.2
    timeframe: float = 0.1
