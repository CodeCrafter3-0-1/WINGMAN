from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

from .routers.api import router as api_router
from .routers.web import router as web_router

BASE_DIR = Path(__file__).resolve().parent

app = FastAPI(
    title="HealthBot",
    version="1.0.0",
    description="AI-powered health assistant for risk assessment, personalized care plans, and wellness guidance.",
)

app.add_middleware(
    SessionMiddleware,
    secret_key="change-this-secret-in-production",
    same_site="lax",
    https_only=False,
)
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")

app.include_router(web_router)
app.include_router(api_router)

