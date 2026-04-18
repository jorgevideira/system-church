from pathlib import Path
import threading

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import logging

from app.core.config import settings
from app.api.v1 import api_router
from app.initial_setup import setup
from app.db.session import SessionLocal
from app.middleware.error_handler import add_exception_handlers

logger = logging.getLogger(__name__)

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

add_exception_handlers(app)

app.include_router(api_router, prefix=settings.API_V1_STR)
Path(settings.UPLOAD_DIR).mkdir(parents=True, exist_ok=True)
Path(settings.TENANT_LOGO_DIR).mkdir(parents=True, exist_ok=True)
app.mount("/media/tenant-logos", StaticFiles(directory=settings.TENANT_LOGO_DIR), name="tenant-logos")
app.mount("/media/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")


def _run_startup_setup() -> None:
    db = SessionLocal()
    try:
        setup(db)
    except Exception:  # pragma: no cover - defensive startup guard
        logger.exception("Startup setup failed and was skipped.")
    finally:
        db.close()


@app.on_event("startup")
def startup_init() -> None:
    # Avoid blocking the full API startup if schema inspection or bootstrap data hangs.
    threading.Thread(target=_run_startup_setup, daemon=True).start()


@app.get("/health")
def health_check() -> dict:
    return {"status": "healthy"}
