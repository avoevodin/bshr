"""
Main start module
"""
import hypercorn
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from bshr.bshr.api.api_v1.api import api_router
from bshr.bshr.core.config import settings

import asyncio
import uvloop
from hypercorn.config import Config
from hypercorn.asyncio import serve

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
        "name": "Andrey Voevodin",
        "url": "https://github.com/avoevodin",
        "email": "avoevodin8888@gmail.com",
    },
    license_info={
        "name": "MIT License",
        "url": "https://github.com/avoevodin/bshr/blob/master/LICENSE",
    },
)


@app.on_event("startup")
async def startup_event() -> None:
    """Startup events function."""
    pass


@app.on_event("shutdown")
async def shutdown_event() -> None:
    """Shutdown events function."""
    pass


if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

app.include_router(api_router, prefix=settings.API_V1_STR)

if __name__ == "__main__":  # pragma: no cover
    hypercorn_config = Config()
    hypercorn_config.bind = [f"{settings.SERVER_HOST}:{settings.SERVER_PORT}"]
    uvloop.install()
    asyncio.run(serve(app, hypercorn_config))  # type: ignore
