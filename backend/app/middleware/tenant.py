"""Tenant middleware for multi-tenant data isolation"""

from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
import jwt
from app.core.config import settings
from app.core.security import decode_token
from typing import Optional


class TenantMiddleware(BaseHTTPMiddleware):
    """Middleware to extract and validate tenant context from JWT"""

    EXCLUDED_PATHS = {
        "/health",
        "/docs",
        "/openapi.json",
        "/api/auth/register",
        "/api/auth/login",
        "/api/auth/refresh",
    }

    async def dispatch(self, request: Request, call_next):
        # Skip middleware for excluded paths
        if request.url.path in self.EXCLUDED_PATHS:
            return await call_next(request)

        # Extract token from header
        token = self._extract_token(request)

        if token:
            # Decode token and add tenant context
            payload = decode_token(token)
            if payload:
                # Add tenant and user info to request state
                request.state.tenant_id = payload.get("tenant_id")
                request.state.user_id = payload.get("sub")
                request.state.user_role = payload.get("role")
                request.state.is_authenticated = True
            else:
                request.state.is_authenticated = False
        else:
            request.state.is_authenticated = False

        response = await call_next(request)
        return response

    @staticmethod
    def _extract_token(request: Request) -> Optional[str]:
        """Extract JWT token from Authorization header"""
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            return None

        try:
            scheme, token = auth_header.split()
            if scheme.lower() != "bearer":
                return None
            return token
        except ValueError:
            return None
