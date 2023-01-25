"""
Endpoints of arbitrary utilities.

Attrs:
    health_check: check connections to databases.
"""
import uuid

from fastapi import APIRouter, HTTPException
from sqlalchemy.exc import InterfaceError
from starlette import status
from starlette.requests import Request

from app.db.redis import get_redis_key

router = APIRouter()


@router.get(
    "/health",
    name="health-check",
    summary="check application health status",
    description=(
        "check connections with databases: performing simple query and responds if"
        " it's ok"
    ),
)
async def health_check(request: Request) -> dict:
    """
    Check connections to databases.

    Args:
        request: request instance

    Returns:
        dict with key detail and value OK if success, otherwise None
    """
    db = request.app.state.db
    redis = request.app.state.redis
    try:
        res = await db.execute("SELECT 1")
        one = res.scalar()
        assert one == 1
        await get_redis_key(redis, uuid.uuid4().hex)
        return {"detail": "OK"}
    except (ConnectionRefusedError, InterfaceError, ConnectionError):
        raise HTTPException(
            detail="connection failed", status_code=status.HTTP_503_SERVICE_UNAVAILABLE
        )
