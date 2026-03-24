from fastapi import APIRouter

from app.api.v1.endpoints import auth, users, categories, transactions, upload, reports

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(categories.router, prefix="/categories", tags=["categories"])
api_router.include_router(transactions.router, prefix="/transactions", tags=["transactions"])
api_router.include_router(upload.router, prefix="/upload", tags=["upload"])
api_router.include_router(reports.router, prefix="/reports", tags=["reports"])
