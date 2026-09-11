from fastapi import APIRouter

router = APIRouter(prefix="/sessions", tags=["sessions"])


@router.get("/health")
def sessions_health():
    return {"ok": True}
