"""
ShieldRun Backend — Phase 2
============================
AI-powered parametric income insurance for Zomato/Swiggy gig workers.

Run locally:
    uvicorn app.main:app --reload

Swagger UI (test all APIs):
    http://localhost:8000/docs
"""
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app.core.database import create_tables, check_db_connection
from app.core.config import ENVIRONMENT
from app.api.routes import workers, policies, claims
from app.services.trigger_engine import run_trigger_check

# ─── Logging ──────────────────────────────────────────────────────────────────
logging.basicConfig(
    level   = logging.INFO,
    format  = "%(asctime)s  %(levelname)-8s  %(name)s — %(message)s",
    datefmt = "%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("shieldrun")

# ─── Scheduler ────────────────────────────────────────────────────────────────
scheduler = AsyncIOScheduler(timezone="Asia/Kolkata")


# ─── Lifespan (startup + shutdown) ────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    # ── Startup ─────────────────────────────────────────────
    logger.info("🚀 ShieldRun starting up...")

    # Create DB tables
    create_tables()

    # Verify DB connection
    if check_db_connection():
        logger.info("✅ Database connected successfully")
    else:
        logger.error("❌ Database connection FAILED — check DATABASE_URL in .env")

    # Start trigger engine (runs every 15 minutes)
    scheduler.add_job(
        run_trigger_check,
        trigger   = "interval",
        minutes   = 15,
        id        = "weather_trigger_check",
        max_instances = 1,          # never run two at the same time
        coalesce      = True,       # skip missed runs if server was down
    )
    scheduler.start()
    logger.info("⚡ Trigger engine started — checking weather every 15 minutes")
    logger.info(f"🌍 Environment: {ENVIRONMENT}")
    logger.info("📖 API docs: http://localhost:8000/docs")

    yield  # ← app is running here

    # ── Shutdown ────────────────────────────────────────────
    scheduler.shutdown(wait=False)
    logger.info("🛑 ShieldRun shutting down cleanly")


# ─── App ──────────────────────────────────────────────────────────────────────
app = FastAPI(
    title       = "ShieldRun API",
    description = (
        "AI-powered parametric income insurance for India's gig workers.\n\n"
        "**Phase 2 — Automation & Protection**\n\n"
        "Covers: Registration → Policy → Dynamic Premium → Auto Claims → Payouts"
    ),
    version     = "2.0.0",
    lifespan    = lifespan,
    docs_url    = "/docs",
    redoc_url   = "/redoc",
)


# ─── CORS ─────────────────────────────────────────────────────────────────────
# Allows Saniya's and Chandini's React apps to call this API
app.add_middleware(
    CORSMiddleware,
    allow_origins     = ["*"],   # tighten to specific URLs before production
    allow_credentials = True,
    allow_methods     = ["*"],
    allow_headers     = ["*"],
)


# ─── Routes ───────────────────────────────────────────────────────────────────
app.include_router(workers.router,  prefix="/api/v1")
app.include_router(policies.router, prefix="/api/v1")
app.include_router(claims.router,   prefix="/api/v1")


# ─── Root Endpoints ───────────────────────────────────────────────────────────
@app.get("/", tags=["🏠 Root"], summary="Welcome")
def root():
    return {
        "app":       "ShieldRun",
        "version":   "2.0.0",
        "phase":     "Phase 2 — Automation & Protection",
        "status":    "running 🛡️",
        "docs":      "/docs",
        "endpoints": {
            "register_worker":     "POST /api/v1/workers/register",
            "worker_login":        "GET  /api/v1/workers/login/{phone}",
            "worker_dashboard":    "GET  /api/v1/workers/{id}/dashboard",
            "get_all_quotes":      "GET  /api/v1/policies/quote/all/{worker_id}",
            "purchase_policy":     "POST /api/v1/policies/purchase",
            "worker_claims":       "GET  /api/v1/claims/worker/{worker_id}",
            "demo_fire_trigger":   "POST /api/v1/claims/demo/trigger",
            "admin_stats":         "GET  /api/v1/claims/admin/stats",
            "admin_all_claims":    "GET  /api/v1/claims/admin/all",
        },
    }


@app.get("/health", tags=["🏠 Root"], summary="Health check")
def health():
    db_ok = check_db_connection()
    return {
        "status":       "healthy" if db_ok else "degraded",
        "db_connected": db_ok,
        "environment":  ENVIRONMENT,
        "version":      "2.0.0",
    }
