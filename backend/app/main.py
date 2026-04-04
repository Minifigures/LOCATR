"""
PATHFINDER — FastAPI Entry Point
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from app.api import router as api_router
from app.core.config import settings

limiter = Limiter(key_func=get_remote_address, default_limits=["100/minute"])

app = FastAPI(
    title="PATHFINDER API",
    description="Intelligent, vibe-aware group activity and venue planning.",
    version="0.1.0",
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS — allow the Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PATCH", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
)

app.include_router(api_router, prefix="/api")


@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "pathfinder"}


@app.get("/debug/imports")
async def debug_imports():
    """Debug endpoint to check if all imports work on Vercel."""
    errors = []
    try:
        from app.graph import pathfinder_graph
    except Exception as e:
        errors.append(f"graph: {type(e).__name__}: {e}")
    try:
        from app.core.auth import require_auth, optional_auth
    except Exception as e:
        errors.append(f"auth: {type(e).__name__}: {e}")
    try:
        from app.services.snowflake import _get_connection
    except Exception as e:
        errors.append(f"snowflake: {type(e).__name__}: {e}")
    try:
        from app.services.gemini import generate_text
    except Exception as e:
        errors.append(f"gemini: {type(e).__name__}: {e}")
    try:
        import langgraph
    except Exception as e:
        errors.append(f"langgraph: {type(e).__name__}: {e}")
    try:
        import langchain
    except Exception as e:
        errors.append(f"langchain: {type(e).__name__}: {e}")

    if errors:
        return {"status": "errors", "errors": errors}
    return {"status": "all_imports_ok"}
