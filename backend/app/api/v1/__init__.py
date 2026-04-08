from fastapi import APIRouter

from app.api.v1.endpoints import (
	auth,
	bible_school,
	budgets,
	categories,
	cells,
	events,
	lost_sheep,
	ministries,
	payables,
	receivables,
	reports,
	transaction_attachments,
	roles,
	tenants,
	tenant_invitations,
	transactions,
	upload,
	users,
)

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(categories.router, prefix="/categories", tags=["categories"])
api_router.include_router(ministries.router, prefix="/ministries", tags=["ministries"])
api_router.include_router(cells.router, prefix="/cells", tags=["cells"])
api_router.include_router(bible_school.router, prefix="/bible-school", tags=["bible_school"])
api_router.include_router(events.router, prefix="/events", tags=["events"])
api_router.include_router(lost_sheep.router, prefix="/lost-sheep", tags=["lost_sheep"])
api_router.include_router(transactions.router, prefix="/transactions", tags=["transactions"])
api_router.include_router(transaction_attachments.router, prefix="/transactions", tags=["transactions"])
api_router.include_router(payables.router, prefix="/payables", tags=["payables"])
api_router.include_router(receivables.router, prefix="/receivables", tags=["receivables"])
api_router.include_router(budgets.router, prefix="/budgets", tags=["budgets"])
api_router.include_router(upload.router, prefix="/upload", tags=["upload"])
api_router.include_router(reports.router, prefix="/reports", tags=["reports"])
api_router.include_router(roles.router, prefix="/roles", tags=["roles"])
api_router.include_router(tenants.router, prefix="/tenants", tags=["tenants"])
api_router.include_router(tenant_invitations.router, prefix="/tenant-invitations", tags=["tenant_invitations"])
