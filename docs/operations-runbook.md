# Operations Runbook

## Startup
1. Backend: `cd backend && pip install -r requirements.txt && uvicorn app.main:app --reload`
2. Frontend: `cd frontend && npm install && npm run dev`

## Seed Credentials
- buyer@example.com / Password123
- seller@example.com / Password123
- opsadmin@example.com / Password123
- superadmin@example.com / Password123

## Daily Checks
- `/health` returns `{"status":"ok"}`
- Admin dashboard queue counts
- AI review queue SLA target values are present
- Import jobs status + report URL

## Incident Notes
- If DB schema mismatch occurs, delete local `app.db` and restart for clean seed (POC only).
