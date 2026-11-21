import os

import pytest
from fastapi.testclient import TestClient

_TEST_ENV_DEFAULTS = {
    "ENV": "development",
    "DB_USERNAME": "postgres",
    "DB_PASSWORD": "password",
    "DB_HOST": "localhost",
    "DB_PORT": "5432",
    "DB_NAME": "fastapi_db_test",
    "JWT_ACCESS_SECRET": "test-access-secret",
    "JWT_ACCESS_EXPIRATION": "3600",
    "JWT_REFRESH_SECRET": "test-refresh-secret",
    "JWT_REFRESH_EXPIRATION": "86400",
    "JWT_ALGORITHM": "HS256",
    "MAIL_FROM": "test@example.com",
    "MAIL_PORT": "465",
    "REDIS_HOST": "localhost",
}

for _key, _value in _TEST_ENV_DEFAULTS.items():
    os.environ.setdefault(_key, _value)

from core.environment_setting import Settings  # noqa: E402
from main import create_app  # noqa: E402


def build_settings(**overrides) -> Settings:
    """Build an isolated Settings instance without reading a .env file."""
    defaults = {
        "env": "development",
        "db_username": "postgres",
        "db_password": "password",
        "db_host": "localhost",
        "db_port": 5432,
        "db_name": "fastapi_db_test",
        "jwt_access_secret": "test-access-secret",
        "jwt_access_expiration": 3600,
        "jwt_refresh_secret": "test-refresh-secret",
        "jwt_refresh_expiration": 86400,
        "jwt_algorithm": "HS256",
        "mail_from": "test@example.com",
        "mail_port": 465,
        "redis_host": "localhost",
    }
    defaults.update(overrides)
    return Settings(_env_file=None, **defaults)


@pytest.fixture(scope="module")
def client():
    """TestClient configured with development settings."""
    dev_settings = build_settings(
        env="development",
        cors_origins=["https://app.example.com"],
    )
    app = create_app(dev_settings)
    with TestClient(app) as c:
        yield c


@pytest.fixture(scope="module")
def prod_client():
    """TestClient configured with production settings and strict hosts."""
    prod_settings = build_settings(
        env="production",
        allowed_hosts=["testserver", "api.example.com"],
        cors_origins=["https://app.example.com"],
    )
    app = create_app(prod_settings)
    with TestClient(app) as c:
        yield c
