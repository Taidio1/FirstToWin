from fastapi import APIRouter
from app.routers.logs import router as logs_router

api_router = APIRouter()
api_router.include_router(logs_router, prefix="/logs")
