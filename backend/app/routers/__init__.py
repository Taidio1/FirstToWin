from fastapi import APIRouter
from app.routers.logs import router as logs_router
from app.routers.auth import router as auth_router

api_router = APIRouter()

api_router.include_router(logs_router, prefix="/logs")
api_router.include_router(auth_router, prefix="/auth")