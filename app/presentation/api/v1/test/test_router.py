from fastapi.routing import APIRouter

from core.dependencies import get_settings
from infrastructure.mail.email_helper import get_mail_helper
from infrastructure.mail.templates import OTPMail
from infrastructure.security.password_hasher import PasswordHasher

test_router = APIRouter()
mail_helper = get_mail_helper()
settings = get_settings()


@test_router.get("/hash-pwd")
async def test(pwd: str):
    return {"hashed": PasswordHasher.hash(pwd)}


@test_router.get("/send-otp-mail")
async def send_otp_mail():
    otp_mail = (OTPMail()
    .set_recipients(['cukecute@cuke.com'])
    .set_body(
        username="CuKe",
        otp=123456,
        app_name=settings.app_name,
    ))

    result = await mail_helper.use_mail(otp_mail).send()
    return {"result": result}
