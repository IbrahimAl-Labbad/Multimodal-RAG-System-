from __future__ import annotations

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from auth.jwt import decode_access_token, CREDENTIALS_EXCEPTION

# Paths excluded from JWT enforcement
PUBLIC_PATHS = {"/api/v1/health", "/docs", "/openapi.json", "/redoc"}


class JWTMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        path = request.url.path

        # Skip auth for public paths and non-api paths
        if path in PUBLIC_PATHS or not path.startswith("/api/v1/"):
            return await call_next(request)

        authorization: str = request.headers.get("Authorization", "")
        if not authorization.startswith("Bearer "):
            return JSONResponse(
                {"detail": "Not authenticated"}, status_code=401,
                headers={"WWW-Authenticate": "Bearer"},
            )

        token = authorization.removeprefix("Bearer ").strip()
        try:
            payload = decode_access_token(token)
            request.state.user = payload.get("sub")
        except Exception:
            return JSONResponse(
                {"detail": "Could not validate credentials"}, status_code=401,
                headers={"WWW-Authenticate": "Bearer"},
            )

        return await call_next(request)
