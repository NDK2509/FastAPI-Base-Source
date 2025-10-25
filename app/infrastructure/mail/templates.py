from core.dependencies import get_settings

settings = get_settings()


class BaseMail:
    subject: str
    recipients: list[str]

    def set_recipients(self, recipients: list[str]):
        self.recipients = recipients
        return self


class HTMLMail(BaseMail):
    template_name: str
    body: dict | None = None

    def set_body(self, **body: dict):
        self.body = body
        return self


class PlainMail(BaseMail):
    plain_message: str


# -----------------------------------------------------------------

class OTPMail(HTMLMail):
    subject = "OTP Verification"
    template_name = "otp"
