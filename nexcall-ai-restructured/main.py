"""
╔══════════════════════════════════════════════════════════╗
║          NexCall AI v2.0 — Centre d'appels intelligent   ║
║                                                          ║
║  Démarrage :                                             ║
║    Dev  : uvicorn main:app --reload                      ║
║    Prod : gunicorn main:app -k uvicorn.workers.          ║
║           UvicornWorker -w 4 -b 0.0.0.0:8000             ║
║                                                          ║
║  Dashboard  : http://localhost:8000                      ║
║  API docs   : http://localhost:8000/docs                 ║
╚══════════════════════════════════════════════════════════╝
"""
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.config import settings
from app.database import init_db
from app.routers import (
    pages_router,
    calls_router,
    leads_router,
    campaigns_router,
    config_router,
    webhooks_router,
)

# ── Logging ───────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.DEBUG if settings.DEBUG else logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(name)s — %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("nexcall")


# ── Lifespan ──────────────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gestion du cycle de vie de l'application."""
    logger.info("═" * 55)
    logger.info("  NexCall AI v2.0 — Démarrage")
    logger.info("═" * 55)
    await init_db()
    logger.info(f"  Dashboard  → http://{settings.APP_HOST}:{settings.APP_PORT}")
    logger.info(f"  API docs   → http://{settings.APP_HOST}:{settings.APP_PORT}/docs")
    logger.info(f"  Ringover   → {'✓ Configuré' if settings.is_ringover_configured else '✗ Non configuré'}")
    logger.info(f"  OpenAI     → {'✓ Configuré' if settings.is_openai_configured else '✗ Non configuré'}")
    logger.info(f"  Agent      → {settings.AI_AGENT_NAME} @ {settings.AI_COMPANY_NAME}")
    logger.info("═" * 55)
    yield
    logger.info("NexCall AI — Arrêt propre")


# ── Application FastAPI ───────────────────────────────────────────
app = FastAPI(
    title="NexCall AI",
    description=(
        "Plateforme de centre d'appels IA intégrant Ringover pour la téléphonie "
        "et OpenAI pour les conversations intelligentes."
    ),
    version="2.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# ── Middleware CORS ────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Fichiers statiques ────────────────────────────────────────────
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# ── Routeurs ──────────────────────────────────────────────────────
app.include_router(pages_router)
app.include_router(calls_router)
app.include_router(leads_router)
app.include_router(campaigns_router)
app.include_router(config_router)
app.include_router(webhooks_router)


# ── Health Check ──────────────────────────────────────────────────
@app.get("/health", tags=["system"], summary="Vérification de santé")
async def health():
    """Endpoint de health check pour le monitoring."""
    return {
        "status": "ok",
        "app": settings.APP_NAME,
        "version": "2.0.0",
        "integrations": {
            "ringover": settings.is_ringover_configured,
            "openai": settings.is_openai_configured,
        },
    }
