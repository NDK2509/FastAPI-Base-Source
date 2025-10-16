from fastapi import FastAPI, APIRouter
from presentation.api.v1.auth.auth_router import auth_router
from presentation.api.v1.users.user_router import user_router

app = FastAPI()

# Setting v1 APIs
v1_router = APIRouter(prefix="/v1", tags=["v1"])
v1_router.include_router(auth_router, prefix="/auth", tags=["auth"])
v1_router.include_router(user_router, prefix="/users", tags=["users"])

app.include_router(v1_router, prefix="/api")
