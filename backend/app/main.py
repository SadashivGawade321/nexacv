from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from app.routes import resume, ats, ai_suggestions, auth, chatbot
import os

app = FastAPI(
    title="Resume Builder API",
    description="API for building resumes, checking ATS scores, and AI suggestions",
    version="1.0.0"
)

# Allow all origins so the frontend works when opened as a local file or via localhost
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router,            prefix="/api/auth",   tags=["Auth"])
app.include_router(resume.router,          prefix="/api/resume", tags=["Resume"])
app.include_router(ats.router,             prefix="/api/ats",    tags=["ATS Score"])
app.include_router(ai_suggestions.router,  prefix="/api/ai",     tags=["AI Suggestions"])
app.include_router(chatbot.router,          prefix="/api/chat",   tags=["Chatbot"])

# Serve the frontend statically at /app
FRONTEND_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "frontend")
if os.path.isdir(FRONTEND_DIR):
    app.mount("/app", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")


@app.on_event("startup")
async def startup():
    """Ensure MongoDB indexes exist on startup."""
    try:
        from app.services.auth_service import ensure_indexes
        await ensure_indexes()
        print("[OK] MongoDB connected and indexes ready.")
    except Exception as e:
        print(f"[WARN] MongoDB startup warning: {e}")


@app.get("/")
async def root():
    return RedirectResponse(url="/app/login.html")


@app.get("/health")
async def health_check():
    return {"status": "healthy"}
