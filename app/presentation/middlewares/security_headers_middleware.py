from starlette.datastructures import MutableHeaders
from starlette.types import ASGIApp, Message, Receive, Scope, Send


class SecurityHeadersMiddleware:
    """Pure ASGI middleware that attaches defensive HTTP security headers to all HTTP responses."""

    def __init__(
        self,
        app: ASGIApp,
        *,
        is_production: bool = False,
        hsts_max_age: int = 31536000,
    ) -> None:
        self.app = app
        self.is_production = is_production
        self.hsts_max_age = hsts_max_age

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        async def send_wrapper(message: Message) -> None:
            if message["type"] == "http.response.start":
                message.setdefault("headers", [])
                headers = MutableHeaders(scope=message)
                headers.setdefault("X-Content-Type-Options", "nosniff")
                headers.setdefault("X-Frame-Options", "DENY")
                headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
                headers.setdefault(
                    "Permissions-Policy",
                    "geolocation=(), microphone=(), camera=()",
                )
                if self.is_production and self.hsts_max_age > 0:
                    headers.setdefault(
                        "Strict-Transport-Security",
                        f"max-age={self.hsts_max_age}; includeSubDomains",
                    )
            await send(message)

        await self.app(scope, receive, send_wrapper)
