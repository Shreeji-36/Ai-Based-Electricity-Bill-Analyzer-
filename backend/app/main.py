from app.db import init_db
...
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

for r in (auth, industries, analysis, reports):
    app.include_router(r.router)


@app.get("/api/health")
def health():
    return {"status": "ok"}