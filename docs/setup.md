# Setup Guide

## Option A: Docker (everything)
1. `cp .env.example .env` and edit the values
2. Set `NEXT_PUBLIC_API_URL=http://localhost` in `.env`
3. `docker compose up --build`, then open http://localhost

## Option B: Local development
Backend: `cd backend && pip install -r requirements.txt && pip install -e ../ai-engine && uvicorn app.main:app --reload`
Frontend: `cd frontend && npm install && npm run dev`
OCR: `cd ocr && pip install -r requirements.txt && uvicorn ocr_service.main:app --port 8001` (needs Tesseract and Poppler installed)

## Free deployment
- Frontend on Vercel: import the repo, set Root Directory to `frontend`, add `NEXT_PUBLIC_API_URL`.
- Backend on Render using `backend/render.yaml`, with a free Neon or Supabase Postgres as `DATABASE_URL`.
- OCR on Render using a Docker web service pointed at `ocr/`. Set `OCR_URL` on the backend.
- Change `FRONTEND_ORIGIN` on the backend to your Vercel URL.

## Tests
`pip install -r tests/requirements.txt && pytest tests`