from fastapi import APIRouter, HTTPException
from sqlalchemy.exc import InterfaceError
from starlette import status
from starlette.requests import Request

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
    :param request:
    :return:
    """
    db = request.app.state.db

    try:
        res = await db.execute("SELECT 1")
        one = res.scalar()
        assert one == 1
        return {"detail": "OK"}
    except (ConnectionRefusedError, InterfaceError, ConnectionError):
        raise HTTPException(
            detail="connection failed", status_code=status.HTTP_503_SERVICE_UNAVAILABLE
        )
