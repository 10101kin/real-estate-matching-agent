# GUIDE.md

## 1. Setup & Run Instructions

### Prerequisites
- Python 3.12+
- Node.js 20+
- npm 10+

### Install dependencies
```bash
# Backend
cd backend
pip install -r requirements.txt

# Frontend
cd ../frontend
npm install
```

### Run locally (dev)
```bash
# Terminal 1
cd backend
uvicorn app.main:app --reload --port 8010

# Terminal 2
cd frontend
VITE_API_BASE=http://localhost:8010/api/v1 npm run dev -- --port 5174
```

### Run locally (prod-like)
```bash
# Backend
cd backend
uvicorn app.main:app --host 0.0.0.0 --port 8000

# Frontend static build
cd frontend
npm run build
npm run preview
```

### Environment variables
Backend (`backend/.env`, optional):
- `SECRET_KEY=change-me`
- `DATABASE_URL=sqlite:///./app.db` (Azure SQL URL can be substituted)
- `BLOB_STORAGE_PATH=./blob_storage`

Frontend (`frontend/.env`, optional):
- `VITE_API_BASE=http://localhost:8010/api/v1`

---

## 2. Feature Walkthrough

### Login
- Route: `/login`
- Email/password login for all roles.
- Seed users:
  - buyer@example.com
  - seller@example.com
  - opsadmin@example.com
  - superadmin@example.com
  - Password: `Password123`

### Buyer Portal
1. **Event Catalog** (`/buyer/events`)
   - View events and sessions.
2. **Event Registration** (`/buyer/register`)
   - Select event and multiple sessions.
   - Backend blocks overlapping session times.
   - Event capacity full -> automatic waitlist registration.
3. **AI Interview** (`/buyer/interview`)
   - Save/resume interview state by registration.
   - Normalized fields always produced: location, budget min/max, property type, timeframe.
   - Low confidence auto-creates AI review queue entry.
4. **Match Results** (`/buyer/matches`)
   - Immediate ranked matching with weighted explainability payload.
5. **Consent Management** (`/buyer/consent`)
   - Consent per-match or per-event for lead sharing.

### Admin Portal (Operations)
1. **Dashboard** (`/admin/dashboard`) – counts for sellers, waitlist, AI queue, audits.
2. **Sellers CRUD** (`/admin/sellers`) – create/update/delete seller records.
3. **Inventory CRUD** (`/admin/inventory`) – manage seller listings.
4. **Events & Sessions** (`/admin/events`) – create events and sessions.
5. **Waitlist Queue** (`/admin/waitlist`) – manual promotion of waitlist entries.
6. **AI Review Queue** (`/admin/ai-review`) – view low-confidence intake queue.
7. **CSV Import** (`/admin/import`) – sellers/inventory import with partial success report.
8. **Matching Weights** (`/admin/weights`) – update matching criterion weights.

### Super Admin-only
- **Users & Roles** (`/admin/users`) – list users and reassign roles.

### Seller Portal (read-only)
1. **Profile** (`/seller/profile`)
2. **Inventory** (`/seller/inventory`)
3. **Leads** (`/seller/leads`) – shows only consented leads.

Navigation flow:
- Login -> role-based landing page -> top-nav links for role pages.

---

## 3. API Reference

Base: `/api/v1`

### Auth
- `POST /auth/register` – create user
  - body: `{ email, password, role, ...profileFields }`
- `POST /auth/login` – OAuth2 password form (`username`, `password`)
- `GET /auth/me` – current user profile
- `GET /auth/users` – super admin only
- `PUT /auth/users/{user_id}/role?role=buyer|seller|operations_admin|super_admin` – super admin only

### Events & Sessions
- `GET /events` – public/authorized event list with sessions
- `POST /events` – admin create event
- `PUT /events/{event_id}` – admin update event
- `DELETE /events/{event_id}` – admin delete event
- `POST /events/{event_id}/sessions` – admin create session

### Registrations / Waitlist
- `POST /registrations` – buyer registration
  - body: `{ event_id, session_ids[] }`
- `GET /registrations/mine` – buyer registrations
- `POST /registrations/waitlist/{entry_id}/promote` – admin manual promotion

### AI Intake
- `POST /buyers/interview` – save/resume + normalize answers
  - body: `{ registration_id, answers: {} }`
- `GET /buyers/interview/{registration_id}` – resume state

### Matching
- `POST /matching/run/{registration_id}` – run matching immediately
- `GET /matching/{registration_id}` – get ranked match list
- `GET /matching/weights/current` – admin fetch weights
- `PUT /matching/weights/current` – admin update weights

### Consents
- `POST /consents`
  - body: `{ consent_scope: per_match|per_event, match_result_id?, event_id? }`
- `GET /consents/mine`

### Seller Read-only
- `GET /sellers/me`
- `GET /sellers/inventory`
- `GET /sellers/leads`

### Admin
- `GET /admin/dashboard`
- `GET /admin/sellers`
- `POST /admin/sellers`
- `PUT /admin/sellers/{seller_id}`
- `DELETE /admin/sellers/{seller_id}`
- `GET /admin/waitlist`
- `GET /admin/ai-review-queue`
- `GET /admin/audit-logs`

### Inventory CRUD
- `GET /inventory`
- `POST /inventory`
- `PUT /inventory/{listing_id}`
- `DELETE /inventory/{listing_id}`

### Imports
- `POST /imports/upload` (multipart: `import_type`, `file`)
- `GET /imports/{job_id}`

Example response (`GET /health`):
```json
{"status":"ok"}
```

---

## 4. Manual QA Test Scenarios

### A. Authentication & RBAC
1. [ ] Login as buyer. **Expected:** Buyer pages visible; admin pages blocked.
2. [ ] Login as seller. **Expected:** Seller read-only pages only.
3. [ ] Login as ops admin. **Expected:** Admin CRUD/import pages visible; user-role page hidden.
4. [ ] Login as super admin. **Expected:** All admin pages including Users & Roles visible.

### B. Buyer Registration + Session Overlap
1. [ ] Open Buyer Register page and pick two overlapping sessions.
   - **Expected:** Backend returns overlap error and registration is blocked.
2. [ ] Pick non-overlapping sessions and submit.
   - **Expected:** Registration created and ID saved in UI/local storage.
3. [ ] Register beyond capacity for same event.
   - **Expected:** Status becomes `waitlisted` and waitlist entry created.

### C. AI Interview Resume + Review Queue
1. [ ] Fill partial answers and save.
   - **Expected:** Session state saved with normalized fields present.
2. [ ] Refresh/login again and open interview.
   - **Expected:** Previous answers reloaded.
3. [ ] Submit low-information answers (missing budget/type).
   - **Expected:** Status `review_required`; entry appears in admin AI review queue.

### D. Matching & Explainability
1. [ ] Run matching after completed interview.
   - **Expected:** Ranked match list with score + criterion breakdown.
2. [ ] Update weights as admin.
   - **Expected:** Subsequent run uses updated weighting.

### E. Consent-Gated Lead Sharing
1. [ ] Seller opens Leads before buyer consent.
   - **Expected:** No lead records shown.
2. [ ] Buyer gives per-match consent.
   - **Expected:** Only that match appears for seller.
3. [ ] Buyer gives per-event consent.
   - **Expected:** Eligible event leads appear.

### F. Admin CRUD + Audit
1. [ ] Create/update/delete seller and inventory records.
   - **Expected:** Changes persist and audit logs are created.
2. [ ] View audit logs.
   - **Expected:** Timestamped actor/action/entity records visible.

### G. CSV Imports (Partial Success)
1. [ ] Upload mixed-validity sellers CSV.
   - **Expected:** Valid rows imported, invalid rows counted as failures.
2. [ ] Open import job status.
   - **Expected:** totals/success/failure + report URL returned.
3. [ ] Upload inventory CSV with duplicate `external_id`.
   - **Expected:** Upsert behavior, conflicts/errors in report.

### H. Waitlist Promotion
1. [ ] Create waitlisted buyer registration.
   - **Expected:** Appears in waitlist queue with position.
2. [ ] Promote via admin queue.
   - **Expected:** Waitlist status `promoted`, registration transitions to `registered`.
