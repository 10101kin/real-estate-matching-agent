from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.core.security import create_access_token, hash_password, verify_password
from app.core.rbac import get_current_user, require_roles
from app.db.session import get_db
from app.models.entities import BuyerProfile, RoleEnum, Seller, User
from app.schemas.contracts import TokenResponse, UserCreate

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=TokenResponse)
def register(payload: UserCreate, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == payload.email).first():
        raise HTTPException(status_code=400, detail="Email already exists")

    user = User(email=payload.email, password_hash=hash_password(payload.password), role=RoleEnum(payload.role))
    db.add(user)
    db.flush()

    if payload.role == "buyer":
        db.add(BuyerProfile(user_id=user.id, full_name=payload.full_name or payload.email, phone=payload.phone))
    if payload.role == "seller":
        db.add(
            Seller(
                user_id=user.id,
                company_name=payload.company_name or "Seller Co",
                contact_name=payload.contact_name or payload.full_name or payload.email,
                seller_email=payload.email,
            )
        )
    db.commit()
    token = create_access_token(subject=user.id, role=user.role.value)
    return TokenResponse(access_token=token, role=user.role.value)


@router.post("/login", response_model=TokenResponse)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_access_token(subject=user.id, role=user.role.value)
    return TokenResponse(access_token=token, role=user.role.value)


@router.get("/me")
def me(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    profile = None
    if current_user.role == RoleEnum.buyer:
        bp = db.query(BuyerProfile).filter(BuyerProfile.user_id == current_user.id).first()
        profile = {"buyer_id": bp.id, "full_name": bp.full_name} if bp else None
    elif current_user.role == RoleEnum.seller:
        seller = db.query(Seller).filter(Seller.user_id == current_user.id).first()
        profile = {"seller_id": seller.id, "company_name": seller.company_name} if seller else None
    return {"id": current_user.id, "email": current_user.email, "role": current_user.role.value, "profile": profile}


@router.get("/users")
def list_users(_: User = Depends(require_roles("super_admin")), db: Session = Depends(get_db)):
    users = db.query(User).all()
    return [{"id": u.id, "email": u.email, "role": u.role.value, "is_active": u.is_active} for u in users]


@router.put("/users/{user_id}/role")
def update_role(user_id: str, role: RoleEnum, current_user: User = Depends(require_roles("super_admin")), db: Session = Depends(get_db)):
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    old = user.role.value
    user.role = role
    db.commit()
    return {"id": user.id, "old_role": old, "new_role": user.role.value, "updated_by": current_user.id}
