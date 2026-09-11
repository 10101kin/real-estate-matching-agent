from datetime import datetime, timedelta
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from app.api.v1 import admin, auth, buyers, consents, events, imports, inventory, matching, registrations, sellers, sessions
from app.core.security import hash_password
from app.db.session import SessionLocal, engine
from app.models.entities import Base, BuyerProfile, Event, EventSession, InventoryListing, RoleEnum, Seller, User

app = FastAPI(title="Real Estate Event Registration API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/v1")
app.include_router(events.router, prefix="/api/v1")
app.include_router(registrations.router, prefix="/api/v1")
app.include_router(buyers.router, prefix="/api/v1")
app.include_router(matching.router, prefix="/api/v1")
app.include_router(consents.router, prefix="/api/v1")
app.include_router(sellers.router, prefix="/api/v1")
app.include_router(inventory.router, prefix="/api/v1")
app.include_router(admin.router, prefix="/api/v1")
app.include_router(imports.router, prefix="/api/v1")
app.include_router(sessions.router, prefix="/api/v1")


@app.get("/health")
def health():
    return {"status": "ok"}


def seed(db: Session):
    if db.query(User).count() > 0:
        return

    super_admin = User(email="superadmin@example.com", password_hash=hash_password("Password123"), role=RoleEnum.super_admin)
    ops_admin = User(email="opsadmin@example.com", password_hash=hash_password("Password123"), role=RoleEnum.operations_admin)
    buyer_user = User(email="buyer@example.com", password_hash=hash_password("Password123"), role=RoleEnum.buyer)
    seller_user = User(email="seller@example.com", password_hash=hash_password("Password123"), role=RoleEnum.seller)
    db.add_all([super_admin, ops_admin, buyer_user, seller_user])
    db.flush()

    buyer = BuyerProfile(user_id=buyer_user.id, full_name="Default Buyer", phone="555-0100")
    seller = Seller(user_id=seller_user.id, company_name="Acme Realty", contact_name="Alice Agent", seller_email="seller@example.com")
    db.add_all([buyer, seller])
    db.flush()

    db.add_all(
        [
            InventoryListing(
                seller_id=seller.id,
                external_id="ACME-100",
                location="Austin",
                property_type="condo",
                price_min=250000,
                price_max=400000,
                metadata_json={"beds": 2},
            ),
            InventoryListing(
                seller_id=seller.id,
                external_id="ACME-200",
                location="Dallas",
                property_type="single_family",
                price_min=300000,
                price_max=550000,
                metadata_json={"beds": 3},
            ),
        ]
    )

    now = datetime.utcnow()
    event = Event(
        name="Texas Buyer Connect",
        description="Meet curated sellers and attend focused sessions",
        capacity=1,
        registration_open_at=now - timedelta(days=1),
        registration_close_at=now + timedelta(days=7),
    )
    db.add(event)
    db.flush()
    db.add_all(
        [
            EventSession(event_id=event.id, title="First Time Buyer Tips", start_time=now + timedelta(days=1, hours=9), end_time=now + timedelta(days=1, hours=10), capacity=30),
            EventSession(event_id=event.id, title="Investor Panel", start_time=now + timedelta(days=1, hours=9, minutes=30), end_time=now + timedelta(days=1, hours=10, minutes=30), capacity=30),
            EventSession(event_id=event.id, title="Financing 101", start_time=now + timedelta(days=1, hours=11), end_time=now + timedelta(days=1, hours=12), capacity=30),
        ]
    )

    db.commit()


@app.on_event("startup")
def startup_event():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed(db)
    finally:
        db.close()
