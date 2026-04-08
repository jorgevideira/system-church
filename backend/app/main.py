from pathlib import Path

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


@app.on_event("startup")
def startup_init() -> None:
    # Run initial setup (create default admin and categories)
    db = SessionLocal()
    try:
        setup(db)
    finally:
        db.close()


@app.get("/health")
def health_check() -> dict:
    return {"status": "healthy"}
