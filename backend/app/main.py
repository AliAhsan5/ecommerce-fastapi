from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router
from app.core.config import get_settings
from app.core.exceptions import register_exception_handlers
from app.core.hardening import SecurityHardeningMiddleware


settings = get_settings()


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.add_middleware(
    SecurityHardeningMiddleware,
    environment=settings.app_env,
)


register_exception_handlers(app)


app.include_router(
    api_router,
    prefix="/api/v1",
)


@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "environment": settings.app_env,
    }