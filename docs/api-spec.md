# API Specification (v1 POC)

Base URL: `/api/v1`

Key endpoints:
- Auth: `POST /auth/login`, `POST /auth/register`, `GET /auth/me`
- Events/Sessions: `GET /events`, `POST /events`, `POST /events/{event_id}/sessions`
- Registration/Waitlist: `POST /registrations`, `GET /registrations/mine`, `POST /registrations/waitlist/{entry_id}/promote`
- AI Interview: `POST /buyers/interview`, `GET /buyers/interview/{registration_id}`
- Matching: `POST /matching/run/{registration_id}`, `GET /matching/{registration_id}`
- Consents: `POST /consents`, `GET /consents/mine`
- Seller read-only: `GET /sellers/me`, `GET /sellers/inventory`, `GET /sellers/leads`
- Admin CRUD: `GET/POST/PUT/DELETE /admin/sellers`, `GET/POST/PUT/DELETE /inventory`
- Imports: `POST /imports/upload`, `GET /imports/{job_id}`
- Super admin: `GET /auth/users`, `PUT /auth/users/{id}/role`
