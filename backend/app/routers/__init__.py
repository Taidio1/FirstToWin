from fastapi import APIRouter
from app.routers.logs_router import router as logs_router
from app.routers.auth_router import router as auth_router
from app.routers.alerts_router import router as alerts_router
from app.routers.dashboard_router import router as dashboard_router

api_router = APIRouter()

api_router.include_router(logs_router, prefix="/logs")
api_router.include_router(auth_router, prefix="/auth")
api_router.include_router(alerts_router, prefix="/alerts")
api_router.include_router(dashboard_router, prefix="/dashboard")
