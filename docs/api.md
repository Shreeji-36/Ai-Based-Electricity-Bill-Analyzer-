# API Reference

Interactive docs: `/docs` (Swagger) on the running backend.

| Method | Path | Auth | Purpose |
|---|---|---|---|
| POST | /api/auth/register | none | Create account (role: analyst) |
| POST | /api/auth/login | none | Get JWT (form fields: username, password) |
| GET | /api/auth/me | any | Current user |
| GET | /api/industries | none | List industries |
| GET | /api/industries/{id}/machines | none | Machines and default rate |
| POST | /api/bills/upload | admin, analyst | OCR a bill file (jpg/png/pdf, max 8 MB) |
| GET | /api/bills?industry= | any | Bill history |
| POST | /api/analysis | admin, analyst | Run analysis and save it |
| POST | /api/reports/{pdf|xlsx|csv} | any | Download a report |

Send the token as `Authorization: Bearer <token>`.