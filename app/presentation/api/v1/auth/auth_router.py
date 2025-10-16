from fastapi.routing import APIRouter

auth_router  = APIRouter()

@auth_router.get("/login")
async def login():
    return {"message": "Login here"}

@auth_router.get("/logout")
async def logout():
    return {"message": "Logout here"}