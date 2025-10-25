import traceback
from functools import lru_cache
from pathlib import Path
from typing import Optional

from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType, NameEmail
from jinja2 import Environment, FileSystemLoader

from core.dependencies import get_settings
from infrastructure.mail.templates import BaseMail, HTMLMail, PlainMail

settings = get_settings()


@lru_cache
def get_mail_config() -> ConnectionConfig:
    return ConnectionConfig(
        MAIL_FROM=settings.mail_from,
        MAIL_USERNAME=settings.mail_username,
        MAIL_PASSWORD=settings.mail_password,
        MAIL_PORT=settings.mail_port,
        MAIL_SERVER=settings.mail_server,
        MAIL_SSL_TLS=settings.mail_ssl_tls,
        MAIL_STARTTLS=settings.mail_starttls,
        TEMPLATE_FOLDER=Path(__file__).parent / "templates",
        USE_CREDENTIALS=settings.env == "production"
    )


class MailHelper:
    fm: FastMail
    jinja_env: Environment
    mail: Optional[BaseMail] = None

    def __init__(self):
        self.fm = FastMail(get_mail_config())
        self.jinja_env = Environment(loader=FileSystemLoader(get_mail_config().TEMPLATE_FOLDER))

    def use_mail(self, mail: BaseMail) -> "MailHelper":
        self.mail = mail
        return self

    async def send(self) -> bool:
        if not self.mail:
            raise Exception("No template provided.")

        if isinstance(self.mail, HTMLMail):
            template = self.jinja_env.get_template(f"{self.mail.template_name}.html")
            html_body = template.render(**(self.mail.body or {}))
        elif isinstance(self.mail, PlainMail):
            html_body = self.mail.plain_message or "No content provided."
        else:
            raise Exception("Unsupported template.")

        if not self.mail.recipients:
            raise Exception("No recipients provided.")

        recipients = [NameEmail("", e) for e in self.mail.recipients]
        message = MessageSchema(
            subject=self.mail.subject,
            recipients=recipients,
            body=html_body,
            subtype=MessageType.html,
        )

        try:
            await self.fm.send_message(message)
            return True
        except Exception as e:
            traceback.print_exc()
            return False


# ✅ Singleton dependency
@lru_cache
def get_mail_helper() -> MailHelper:
    return MailHelper()
