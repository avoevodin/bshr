from fastapi import APIRouter

router = APIRouter()


@router.get("/login", name="login")
async def get_login_page():
    return {"msg": "Hi there"}
