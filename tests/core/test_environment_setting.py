import pytest
from pydantic import ValidationError

from conftest import build_settings
from core.environment_setting import Settings


class TestSettingsListParsing:
    def test_parses_comma_separated_strings_from_kwargs_and_env(
        self, monkeypatch: pytest.MonkeyPatch
    ):
        settings = build_settings(
            cors_origins=" https://a.example.com/ , https://b.example.com , ",
            cors_allow_methods="get, post , delete",
            allowed_hosts=" api.example.com , internal.local ",
        )
        assert settings.cors_origins == [
            "https://a.example.com",
            "https://b.example.com",
        ]
        assert settings.cors_allow_methods == ["GET", "POST", "DELETE"]
        assert settings.allowed_hosts == ["api.example.com", "internal.local"]

        monkeypatch.setenv(
            "CORS_ORIGINS", "https://env1.example.com/, http://localhost:3000"
        )
        monkeypatch.setenv("CORS_ALLOW_HEADERS", "Authorization, X-Custom-Header")
        env_settings = Settings(_env_file=None)
        assert env_settings.cors_origins == [
            "https://env1.example.com",
            "http://localhost:3000",
        ]
        assert env_settings.cors_allow_headers == [
            "Authorization",
            "X-Custom-Header",
        ]

    def test_parses_json_array_strings_from_kwargs_and_env(
        self, monkeypatch: pytest.MonkeyPatch
    ):
        monkeypatch.setenv(
            "CORS_ORIGINS", '["https://app.example.com/", "http://localhost:5173"]'
        )
        monkeypatch.setenv("CORS_ALLOW_METHODS", '["get", "options"]')
        env_settings = Settings(_env_file=None)
        assert env_settings.cors_origins == [
            "https://app.example.com",
            "http://localhost:5173",
        ]
        assert env_settings.cors_allow_methods == ["GET", "OPTIONS"]

    def test_parses_empty_string_and_none_as_empty_list(self):
        settings = build_settings(cors_origins="", allowed_hosts=None)
        assert settings.cors_origins == []
        assert settings.allowed_hosts == []

        whitespace_settings = build_settings(cors_origins="   ,  , ")
        assert whitespace_settings.cors_origins == []

    @pytest.mark.parametrize(
        "invalid_value",
        [
            "[not-valid-json",
            '{"origin": "https://app.example.com"}',
            "[123, 456]",
            [123],
            12345,
        ],
    )
    def test_rejects_invalid_list_inputs(self, invalid_value):
        with pytest.raises(ValidationError):
            build_settings(cors_origins=invalid_value)


class TestSettingsValidationRules:
    def test_normalizes_trailing_slash_lowercase_origin_and_uppercase_methods(self):
        settings = build_settings(
            cors_origins=["HTTPS://App.Example.com///", "http://LOCALHOST:3000/"],
            cors_allow_methods=["get", "Patch", "options"],
        )
        assert settings.cors_origins == [
            "https://app.example.com",
            "http://localhost:3000",
        ]
        assert settings.cors_allow_methods == ["GET", "PATCH", "OPTIONS"]

    @pytest.mark.parametrize(
        "bad_origin",
        [
            "ftp://app.example.com",
            "app.example.com",
            "https://",
            "http://",
            "https://app.example.com/path",
            "https://app.example.com?a=1",
            "https://app.example.com#top",
            "https://user:pass@app.example.com",
            "https://app.example .com",
        ],
    )
    def test_rejects_invalid_cors_origin(self, bad_origin: str):
        with pytest.raises(ValidationError):
            build_settings(cors_origins=[bad_origin])

    @pytest.mark.parametrize(
        "bad_host",
        [
            "https://api.example.com",
            "http://localhost:8000",
            "api.example.com/v1",
            "*example.com",
            "api.*.example.com",
            "*.",
            "api.example.com:8000",
            "api.example .com",
        ],
    )
    def test_rejects_invalid_allowed_host_entries(self, bad_host: str):
        with pytest.raises(ValidationError):
            build_settings(allowed_hosts=[bad_host])

    def test_normalizes_valid_allowed_hosts_to_lowercase(self):
        settings = build_settings(
            allowed_hosts=["API.Example.com", "*.Example.com", "[::1]"]
        )
        assert settings.allowed_hosts == ["api.example.com", "*.example.com", "[::1]"]

    def test_rejects_wildcard_origin_when_credentials_enabled(self):
        with pytest.raises(ValidationError):
            build_settings(cors_origins=["*"], cors_allow_credentials=True)

        allowed = build_settings(cors_origins=["*"], cors_allow_credentials=False)
        assert allowed.cors_origins == ["*"]

    def test_production_requires_non_empty_non_wildcard_allowed_hosts(self):
        with pytest.raises(ValidationError):
            build_settings(env="production", allowed_hosts=[])

        with pytest.raises(ValidationError):
            build_settings(env="production", allowed_hosts=["*"])

        with pytest.raises(ValidationError):
            build_settings(
                env="production", allowed_hosts=["api.example.com", "*"]
            )

        valid_prod = build_settings(
            env="production", allowed_hosts=["api.example.com"]
        )
        assert valid_prod.allowed_hosts == ["api.example.com"]

    def test_development_allows_empty_allowed_hosts(self):
        dev_settings = build_settings(env="development", allowed_hosts=[])
        assert dev_settings.allowed_hosts == []

    def test_rejects_negative_max_age_values(self):
        with pytest.raises(ValidationError):
            build_settings(cors_max_age=-1)
        with pytest.raises(ValidationError):
            build_settings(hsts_max_age=-1)
