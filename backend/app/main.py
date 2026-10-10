import os
from contextlib import asynccontextmanager
import httpx
from fastapi import BackgroundTasks, FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app import config
from app.db import init_db
from app.routers import analysis, auth, bills, industries, reports


@asynccontextmanager
async def lifespan(_: FastAPI):
    init_db()
    yield


app = FastAPI(title="AI Industrial Energy Intelligence API", version="1.0.0", lifespan=lifespan)

ALLOWED_ORIGINS = [config.FRONTEND_ORIGIN, "http://localhost:3000"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(Exception)
async def unhandled_error(request: Request, exc: Exception):
    # Without this, a crash returns no CORS headers and the browser only says "Failed to fetch".
    origin = request.headers.get("origin")
    headers = {"Access-Control-Allow-Origin": origin, "Vary": "Origin"} if origin in ALLOWED_ORIGINS else {}
    return JSONResponse({"detail": "Something went wrong on the server. Please try again."},
                        status_code=500, headers=headers)


for r in (auth, industries, analysis, reports, bills):
    app.include_router(r.router)


@app.get("/api/health")
def health():
    return {"status": "ok"}


def _wake_ocr():
    try:
        httpx.get(os.getenv("OCR_URL", "http://localhost:8001").rstrip("/") + "/health", timeout=90)
    except Exception:
        pass


@app.get("/api/warmup")
def warmup(background: BackgroundTasks):
    """Called when a visitor opens the site: wakes the OCR service (free servers sleep when idle)."""
    background.add_task(_wake_ocr)
    return {"status": "warming"}