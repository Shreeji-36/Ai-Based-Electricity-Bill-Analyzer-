# Architecture

Browser -> Next.js frontend (Vercel) -> FastAPI backend (Render) -> PostgreSQL
                                              |-> OCR service (Docker, Tesseract)
                                              |-> ai-engine (Python package: forecast, anomaly, recommendations)

## Data flow
1. User picks an industry and uploads a bill.
2. Backend forwards the file to the OCR service, which returns extracted fields.
3. User confirms or edits the values and enters machine hours.
4. Backend runs the energy model (services/energy.py), then ai-engine enrichment.
5. Result is stored in `analyses` and returned to the dashboard.

## Energy model
machine_units = power_kw x hours_per_day x billing_days x load_factor
If the estimate exceeds the real bill it is scaled to 95% of it. The remainder is "Others".

## Design decisions
- One PostgreSQL database with an `industry` column instead of four databases (simpler to run and migrate).
- ai-engine is a separate package so models can be developed and tested without the API.
- OCR is a separate service because it needs system packages (Tesseract, Poppler).