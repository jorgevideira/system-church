from fastapi import APIRouter

from app.api.v1.endpoints import (
	auth,
	categories,
	ministries,
	payables,
	reports,
	transaction_attachments,
	transactions,
	upload,
	users,
)

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(categories.router, prefix="/categories", tags=["categories"])
api_router.include_router(ministries.router, prefix="/ministries", tags=["ministries"])
api_router.include_router(transactions.router, prefix="/transactions", tags=["transactions"])
api_router.include_router(transaction_attachments.router, prefix="/transactions", tags=["transactions"])
api_router.include_router(payables.router, prefix="/payables", tags=["payables"])
api_router.include_router(upload.router, prefix="/upload", tags=["upload"])
api_router.include_router(reports.router, prefix="/reports", tags=["reports"])
