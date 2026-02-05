from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.database import init_db
from app.routers import requirements, testcases, ai
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield

app = FastAPI(title="QAI API", lifespan=lifespan)

# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For dev only
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(requirements.router, prefix="/api/v1", tags=["requirements"])
app.include_router(testcases.router, prefix="/api/v1", tags=["testcases"])
app.include_router(ai.router, prefix="/api/v1/ai", tags=["ai"])

@app.get("/")
def read_root():
    return {"message": "Welcome to QAI API"}
