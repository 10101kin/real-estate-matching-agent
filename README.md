# Real Estate Event Registration Platform (POC)

This repository delivers a functional v1 proof-of-concept for:
- Buyer portal
- Admin backend (operations + super admin)
- Seller read-only portal

## Structure
- `backend/` FastAPI API, SQLite local runtime (Azure SQL compatible ORM design)
- `frontend/` React SPA with role-based navigation
- `infra/azure/` Azure infrastructure placeholders
- `docs/` API, matching, imports, runbook

## Quick start
### Backend
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

Frontend defaults to `http://localhost:8000/api/v1`.
