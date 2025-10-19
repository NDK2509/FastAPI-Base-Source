from fastapi.routing import APIRouter

from infrastructure.security.password_hasher import PasswordHasher

test_router = APIRouter()

@test_router.get("/hash-pwd")
async def test(pwd: str):
    return {"hashed": PasswordHasher.hash(pwd)}