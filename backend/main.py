from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from app.core.database import init_db
from app.routers import requirements, testcases, ai, projects, knowledge
from contextlib import asynccontextmanager
import os

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
app.include_router(projects.router, prefix="/api/v1", tags=["projects"])
app.include_router(knowledge.router, prefix="/api/v1", tags=["knowledge"])

# Mount frontend static files
# Assume frontend is at ../frontend relative to backend
frontend_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "frontend")

if os.path.exists(frontend_path):
    # Mount / to serve index.html explicitly or static files
    # However, StaticFiles serves directory content. We want root / to return index.html
    
    @app.get("/")
    async def read_index():
        return FileResponse(os.path.join(frontend_path, "index.html"))

    # Mount other static assets if any (e.g., css, js if separated)
    # Since index.html uses CDN for libs, we mainly just serve the html itself.
    # But if there were local assets:
    app.mount("/", StaticFiles(directory=frontend_path), name="static")
else:
    print(f"Warning: Frontend path {frontend_path} not found. UI will not be served.")
