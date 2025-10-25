from typing import Literal

from pydantic import EmailStr, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "FastAPI Example API"
    tz: str = "Asia/Ho_Chi_Minh"
    env: Literal["development", "production"] = "development"

    # Database Settings
    db_username: str
    db_password: str
    db_host: str
    db_port: int
    db_name: str
    
    # JWT Settings
    jwt_access_secret: str
    jwt_access_expiration: int
    jwt_refresh_secret: str
    jwt_refresh_expiration: int
    jwt_algorithm: str

    # Google SSO Settings
    google_client_id: str | None = None
    google_client_secret: str | None = None
    google_redirect_url: str | None = None

    # Mail configs
    mail_from: EmailStr | None = None
    mail_username: str = ''
    mail_password: SecretStr = ''
    mail_server: str = ''
    mail_port: int | None = None
    mail_ssl_tls: bool = True
    mail_starttls: bool = False

    model_config = SettingsConfigDict(env_file=".env")
