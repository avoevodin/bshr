"""
FastAPI api router initialization package.
"""
from fastapi import APIRouter

from app.api.api_v1.views import auth, utils, users

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(utils.router, prefix="/utils", tags=["utils"])
