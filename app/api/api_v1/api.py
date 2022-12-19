from fastapi import APIRouter

from api.api_v1.views import login

api_router = APIRouter()
api_router.include_router(login.router, tags=["login"])
