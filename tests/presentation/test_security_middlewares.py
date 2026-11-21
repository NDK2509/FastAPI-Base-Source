import asyncio

from fastapi import Response
from fastapi.testclient import TestClient

from conftest import build_settings
from main import create_app
from presentation.middlewares.security_headers_middleware import (
    SecurityHeadersMiddleware,
)

EXPECTED_BASELINE_HEADERS = {
    "x-content-type-options": "nosniff",
    "x-frame-options": "DENY",
    "referrer-policy": "strict-origin-when-cross-origin",
    "permissions-policy": "geolocation=(), microphone=(), camera=()",
}


def _assert_baseline_headers(headers, *, skip: set[str] | None = None) -> None:
    skip_keys = skip or set()
    for name, value in EXPECTED_BASELINE_HEADERS.items():
        if name in skip_keys:
            continue
        assert headers.get(name) == value


class TestSecurityHeadersMiddleware:
    def test_baseline_headers_on_normal_response_and_no_hsts_in_dev(self, client):
        response = client.get("/openapi.json")
        assert response.status_code == 200
        _assert_baseline_headers(response.headers)
        assert "strict-transport-security" not in response.headers

    def test_baseline_headers_on_401_from_auth_middleware(self, client):
        response = client.get("/api/v1/test/hash-pwd", params={"pwd": "secret"})
        assert response.status_code == 401
        _assert_baseline_headers(response.headers)
        assert "strict-transport-security" not in response.headers

    def test_baseline_headers_on_500_from_exception_middleware(self):
        app = create_app(build_settings(env="development"))

        @app.get("/docs/boom")
        async def boom():
            raise RuntimeError("boom")

        with TestClient(app) as c:
            response = c.get("/docs/boom")

        assert response.status_code == 500
        _assert_baseline_headers(response.headers)

    def test_preserves_custom_response_headers_with_setdefault(self):
        app = create_app(build_settings(env="development"))

        @app.get("/docs/custom-headers")
        async def custom_headers():
            return Response(
                content="ok",
                headers={"X-Frame-Options": "SAMEORIGIN"},
            )

        with TestClient(app) as c:
            response = c.get("/docs/custom-headers")

        assert response.status_code == 200
        assert response.headers.get("x-frame-options") == "SAMEORIGIN"
        _assert_baseline_headers(response.headers, skip={"x-frame-options"})

    def test_hsts_present_in_production_and_omitted_when_zero(self, prod_client):
        response = prod_client.get("/openapi.json")
        assert response.status_code == 200
        _assert_baseline_headers(response.headers)
        assert (
            response.headers.get("strict-transport-security")
            == "max-age=31536000; includeSubDomains"
        )

        app_no_hsts = create_app(
            build_settings(
                env="production",
                allowed_hosts=["testserver"],
                hsts_max_age=0,
            )
        )
        with TestClient(app_no_hsts) as c:
            no_hsts_response = c.get("/openapi.json")

        assert no_hsts_response.status_code == 200
        _assert_baseline_headers(no_hsts_response.headers)
        assert "strict-transport-security" not in no_hsts_response.headers

    def test_non_http_scope_passes_through_directly(self):
        called_with = {}

        async def dummy_app(scope, receive, send):
            called_with["scope"] = scope
            called_with["send"] = send

        middleware = SecurityHeadersMiddleware(dummy_app, is_production=True)

        async def dummy_receive():
            return {"type": "websocket.connect"}

        async def dummy_send(message):
            return None

        ws_scope = {"type": "websocket", "path": "/ws"}
        asyncio.run(middleware(ws_scope, dummy_receive, dummy_send))

        assert called_with["scope"] is ws_scope
        assert called_with["send"] is dummy_send

    def test_handles_response_start_message_missing_headers_key(self):
        sent_messages = []

        async def dummy_app(scope, receive, send):
            await send({"type": "http.response.start", "status": 200})
            await send({"type": "http.response.body", "body": b"ok"})

        middleware = SecurityHeadersMiddleware(dummy_app, is_production=True)

        async def dummy_receive():
            return {"type": "http.request"}

        async def capture_send(message):
            sent_messages.append(message)

        asyncio.run(
            middleware({"type": "http", "path": "/"}, dummy_receive, capture_send)
        )

        start_msg = sent_messages[0]
        header_map = {
            k.decode("latin-1").lower(): v.decode("latin-1")
            for k, v in start_msg["headers"]
        }
        assert header_map["x-content-type-options"] == "nosniff"
        assert header_map["x-frame-options"] == "DENY"
        assert (
            header_map["strict-transport-security"]
            == "max-age=31536000; includeSubDomains"
        )


class TestCORSMiddleware:
    def test_preflight_allowed_origin_bypasses_auth_and_has_security_headers(
        self, client
    ):
        response = client.options(
            "/api/v1/test/hash-pwd",
            headers={
                "Origin": "https://app.example.com",
                "Access-Control-Request-Method": "GET",
                "Access-Control-Request-Headers": "Authorization, Content-Type",
            },
        )
        assert response.status_code == 200
        assert (
            response.headers.get("access-control-allow-origin")
            == "https://app.example.com"
        )
        assert response.headers.get("access-control-allow-credentials") == "true"
        _assert_baseline_headers(response.headers)

    def test_preflight_disallowed_origin_rejected_with_security_headers(
        self, client
    ):
        response = client.options(
            "/api/v1/test/hash-pwd",
            headers={
                "Origin": "https://evil.example.com",
                "Access-Control-Request-Method": "GET",
            },
        )
        assert response.status_code == 400
        assert "access-control-allow-origin" not in response.headers
        _assert_baseline_headers(response.headers)

    def test_cors_headers_present_on_401_response_for_allowed_origin(self, client):
        allowed_resp = client.get(
            "/api/v1/test/hash-pwd",
            params={"pwd": "secret"},
            headers={"Origin": "https://app.example.com"},
        )
        assert allowed_resp.status_code == 401
        assert (
            allowed_resp.headers.get("access-control-allow-origin")
            == "https://app.example.com"
        )
        assert allowed_resp.headers.get("access-control-allow-credentials") == "true"
        _assert_baseline_headers(allowed_resp.headers)

        disallowed_resp = client.get(
            "/api/v1/test/hash-pwd",
            params={"pwd": "secret"},
            headers={"Origin": "https://evil.example.com"},
        )
        assert disallowed_resp.status_code == 401
        assert "access-control-allow-origin" not in disallowed_resp.headers
        _assert_baseline_headers(disallowed_resp.headers)

    def test_cors_headers_present_on_500_response_for_allowed_origin(self):
        app = create_app(
            build_settings(
                env="development",
                cors_origins=["https://app.example.com"],
            )
        )

        @app.get("/docs/boom-cors")
        async def boom_cors():
            raise RuntimeError("boom")

        with TestClient(app) as c:
            allowed_resp = c.get(
                "/docs/boom-cors",
                headers={"Origin": "https://app.example.com"},
            )
            disallowed_resp = c.get(
                "/docs/boom-cors",
                headers={"Origin": "https://evil.example.com"},
            )

        assert allowed_resp.status_code == 500
        assert (
            allowed_resp.headers.get("access-control-allow-origin")
            == "https://app.example.com"
        )
        assert allowed_resp.headers.get("access-control-allow-credentials") == "true"
        _assert_baseline_headers(allowed_resp.headers)

        assert disallowed_resp.status_code == 500
        assert "access-control-allow-origin" not in disallowed_resp.headers
        _assert_baseline_headers(disallowed_resp.headers)


class TestTrustedHostMiddleware:
    def test_inactive_in_development_allows_any_host(self, client):
        docs_resp = client.get("/openapi.json", headers={"Host": "evil.com"})
        assert docs_resp.status_code == 200

        protected_resp = client.get(
            "/api/v1/test/hash-pwd",
            params={"pwd": "secret"},
            headers={"Host": "evil.com"},
        )
        assert protected_resp.status_code == 401

    def test_active_in_production_blocks_untrusted_and_allows_trusted_hosts(
        self, prod_client
    ):
        blocked = prod_client.get("/openapi.json", headers={"Host": "evil.com"})
        assert blocked.status_code == 400

        allowed = prod_client.get(
            "/api/v1/test/hash-pwd",
            headers={"Host": "api.example.com"},
        )
        assert allowed.status_code == 401

        allowed_with_port = prod_client.get(
            "/openapi.json",
            headers={"Host": "api.example.com:8443"},
        )
        assert allowed_with_port.status_code == 200
        _assert_baseline_headers(allowed_with_port.headers)
        assert (
            allowed_with_port.headers.get("strict-transport-security")
            == "max-age=31536000; includeSubDomains"
        )

    def test_active_in_production_allows_wildcard_subdomain_and_rejects_evil_host(
        self,
    ):
        wildcard_app = create_app(
            build_settings(
                env="production",
                allowed_hosts=["testserver", "*.example.com"],
            )
        )
        with TestClient(wildcard_app) as c:
            sub_resp = c.get(
                "/openapi.json", headers={"Host": "sub.example.com"}
            )
            evil_resp = c.get("/openapi.json", headers={"Host": "evil.com"})

        assert sub_resp.status_code == 200
        _assert_baseline_headers(sub_resp.headers)
        assert evil_resp.status_code == 400
