import json
from pathlib import Path
from typing import Annotated, Any, Literal
from urllib.parse import urlparse

from pydantic import EmailStr, Field, SecretStr, field_validator, model_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict

CommaOrJsonList = Annotated[list[str], NoDecode]


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

    # Redis configs
    redis_host: str
    redis_port: int = 6379
    redis_username: str | None = None
    redis_password: str | None = None
    redis_db: int = 0

    # Initial Admin Settings
    admin_username: str | None = None
    admin_password: SecretStr | None = None

    # Security & CORS Settings
    cors_origins: CommaOrJsonList = []
    cors_allow_credentials: bool = True
    cors_allow_methods: CommaOrJsonList = [
        "GET",
        "POST",
        "PUT",
        "PATCH",
        "DELETE",
        "OPTIONS",
    ]
    cors_allow_headers: CommaOrJsonList = [
        "Authorization",
        "Content-Type",
        "X-Request-ID",
    ]
    cors_max_age: int = Field(default=600, ge=0)
    allowed_hosts: CommaOrJsonList = []
    hsts_max_age: int = Field(default=31536000, ge=0)

    model_config = SettingsConfigDict(
        env_file=(str(Path(__file__).resolve().parents[2] / ".env"), ".env")
    )

    @field_validator(
        "cors_origins",
        "cors_allow_methods",
        "cors_allow_headers",
        "allowed_hosts",
        mode="before",
    )
    @classmethod
    def _parse_str_list(cls, value: Any) -> list[str]:
        """Parse None, lists, JSON array strings, or comma-separated strings into clean string lists."""
        if value is None:
            return []

        if isinstance(value, list):
            if not all(isinstance(item, str) for item in value):
                raise ValueError("List entries must be strings")
            return [item.strip() for item in value if item.strip()]

        if isinstance(value, str):
            stripped = value.strip()
            if not stripped:
                return []
            if stripped.startswith("["):
                try:
                    parsed = json.loads(stripped)
                except json.JSONDecodeError as exc:
                    raise ValueError("Invalid JSON array string") from exc
                if not isinstance(parsed, list) or not all(
                    isinstance(item, str) for item in parsed
                ):
                    raise ValueError("JSON value must be a list of strings")
                return [item.strip() for item in parsed if item.strip()]
            return [item.strip() for item in stripped.split(",") if item.strip()]

        raise ValueError(
            f"Expected list or comma-separated/JSON string, got {type(value).__name__}"
        )

    @field_validator("cors_origins", mode="after")
    @classmethod
    def _validate_cors_origins(cls, value: list[str]) -> list[str]:
        """Normalize origins and enforce strict http(s)://host[:port] format."""
        normalized_origins: list[str] = []
        for origin in value:
            if any(ch.isspace() for ch in origin):
                raise ValueError(
                    f"Invalid CORS origin '{origin}': must not contain whitespace"
                )
            if origin == "*":
                normalized_origins.append(origin)
                continue

            normalized = origin.rstrip("/")
            parsed = urlparse(normalized)
            if parsed.scheme not in {"http", "https"} or not parsed.netloc:
                raise ValueError(
                    f"Invalid CORS origin '{origin}': must start with http:// or https://"
                )
            if any((parsed.path, parsed.params, parsed.query, parsed.fragment)):
                raise ValueError(
                    f"Invalid CORS origin '{origin}': must not include path, query, or fragment"
                )
            if parsed.username is not None or parsed.password is not None:
                raise ValueError(
                    f"Invalid CORS origin '{origin}': must not include userinfo"
                )
            normalized_origins.append(f"{parsed.scheme}://{parsed.netloc.lower()}")
        return normalized_origins

    @field_validator("cors_allow_methods", mode="after")
    @classmethod
    def _normalize_cors_methods(cls, value: list[str]) -> list[str]:
        """Normalize allowed CORS HTTP methods to uppercase."""
        return [method.upper() for method in value]

    @field_validator("allowed_hosts", mode="after")
    @classmethod
    def _validate_allowed_hosts(cls, value: list[str]) -> list[str]:
        """Validate host patterns against Starlette TrustedHostMiddleware rules and normalize lowercase."""
        normalized_hosts: list[str] = []
        for host in value:
            if not host or "://" in host or "/" in host or any(ch.isspace() for ch in host):
                raise ValueError(
                    f"Invalid allowed host '{host}': must be a non-empty hostname without scheme, slash, or whitespace"
                )
            if host != "*":
                if (
                    "*" in host[1:]
                    or (host.startswith("*") and not host.startswith("*."))
                    or host == "*."
                ):
                    raise ValueError(
                        f"Invalid allowed host '{host}': wildcard must be '*' or '*.domain'"
                    )
                if ":" in host and not (host.startswith("[") and host.endswith("]")):
                    raise ValueError(
                        f"Invalid allowed host '{host}': must not include a port"
                    )
            normalized_hosts.append(host.lower())
        return normalized_hosts

    @model_validator(mode="after")
    def _validate_security_policy(self) -> "Settings":
        """Enforce safe CORS wildcard and production trusted-host invariants."""
        if self.cors_allow_credentials and "*" in self.cors_origins:
            raise ValueError(
                "cors_origins cannot contain '*' when cors_allow_credentials is True"
            )
        if self.env == "production" and (
            not self.allowed_hosts or "*" in self.allowed_hosts
        ):
            raise ValueError(
                "allowed_hosts must be non-empty and must not contain '*' when env is 'production'"
            )
        return self
