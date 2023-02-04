"""
Main start module.
"""
import asyncio

import uvloop
from fastapi import FastAPI
from hypercorn.asyncio import serve
from hypercorn.config import Config
from starlette.middleware.cors import CORSMiddleware

from app.api.api_v1.api import api_router
from app.core.config import settings
from app.db.database import app_init_db, app_dispose_db
from app.db.redis import app_init_redis, app_dispose_redis

OPENAPI_DESCRIPTION = """
**API for bashare app**
"""
OPENAPI_VERSION = "1.0.1"
OPENAPI_TAGS = [
    {
        "name": "Login",
        "description": (
            "Operations for users to register, login, logout or refresh token"
        ),
    },
]

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=OPENAPI_VERSION,
    description=OPENAPI_DESCRIPTION,
    openapi_tags=OPENAPI_TAGS,
    contact={
        "name": settings.API_CONTACT_NAME,
        "url": settings.API_CONTACT_URL,
        "email": settings.API_CONTACT_EMAIL,
    },
    license_info={
        "name": settings.LICENSE_NAME,
        "url": settings.LICENSE_URL,
    },
)


@app.on_event("startup")
async def startup_event() -> None:
    """Startup events function."""
    await app_init_db(app)
    await app_init_redis(app)


@app.on_event("shutdown")
async def shutdown_event() -> None:
    """Shutdown events function."""
    await app_dispose_db(app)
    await app_dispose_redis(app)


if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

app.include_router(api_router, prefix=settings.API_PREFIX)

if __name__ == "__main__":  # pragma: no cover
    hypercorn_config = Config()
    hypercorn_config.bind = [f"{settings.SERVER_HOST}:{settings.SERVER_PORT}"]
    uvloop.install()
    asyncio.run(serve(app, hypercorn_config))  # type: ignore
