from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app import config
from app.db import init_db
from app.routers import analysis, auth, bills, industries, reports


@asynccontextmanager
async def lifespan(_: FastAPI):
    init_db()
    yield


app = FastAPI(title="AI Industrial Energy Intelligence API", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[config.FRONTEND_ORIGIN, "http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

for r in (auth, industries, analysis, reports, bills):
    app.include_router(r.router)


@app.get("/api/health")
def health():
    return {"status": "ok"}