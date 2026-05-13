from __future__ import annotations
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from loguru import logger
import time
import app.settings as settings
from app.routers import api_router


@asynccontextmanager
async def lifespan(_: FastAPI):
    logger.info(
        f"Listening @ {settings.SERVER_HOST}:{settings.SERVER_PORT}")
    yield
    logger.info("Shutting down...")


async def logging_middleware(request: Request, call_next):
    start = time.perf_counter()
    response = await call_next(request)
    elapsed = time.perf_counter() - start
    logger.info(f"{request.method} {request.url.path} - {response.status_code} ({elapsed:.3f}s)")
    return response


def init_api() -> FastAPI:
    asgi_app = FastAPI(
        lifespan=lifespan,
        title="FirstToWin API",
        version="0.0.1-dev",
    )
    asgi_app.middleware("http")(logging_middleware)
    asgi_app.include_router(api_router, prefix="/api")
    return asgi_app


app = init_api()