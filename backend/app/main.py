"""FastAPI Application Entry Point"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
import logging

from app.core.config import settings
from app.middleware.tenant import TenantMiddleware
from app.middleware.error_handler import error_handler_middleware
from app.database.connection import connect_to_mongo, close_mongo_connection
from app.api import auth, platform, tenant, subscription, billing

logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Vehicle Rental SaaS API",
    description="Multi-tenant vehicle rental management platform",
    version="1.0.0",
    docs_url="/docs",
    openapi_url="/openapi.json",
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:8000",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8000",
        settings.FRONTEND_URL,
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Trusted Host Middleware
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["localhost", "127.0.0.1", "*.localhost"]
)

# Custom Middleware
app.add_middleware(TenantMiddleware)
app.middleware("http")(error_handler_middleware)


# Database Events
@app.on_event("startup")
async def startup_event():
    """Initialize database connection on startup"""
    await connect_to_mongo()
    logger.info("✅ MongoDB connection established")


@app.on_event("shutdown")
async def shutdown_event():
    """Close database connection on shutdown"""
    await close_mongo_connection()
    logger.info("✅ MongoDB connection closed")


# Health Check Endpoint
@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "environment": settings.FASTAPI_ENV,
        "version": "1.0.0",
    }


# Root Endpoint
@app.get("/", tags=["Root"])
async def root():
    """Root endpoint"""
    return {
        "message": "Welcome to Vehicle Rental SaaS API",
        "docs": "/docs",
        "version": "1.0.0",
    }


# API Routes
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(platform.router, prefix="/api/platform", tags=["Platform Admin"])
app.include_router(tenant.router, prefix="/api/tenant", tags=["Tenant"])
app.include_router(subscription.router, prefix="/api/subscription", tags=["Subscription"])
app.include_router(billing.router, prefix="/api/billing", tags=["Billing"])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.FASTAPI_HOST,
        port=settings.FASTAPI_PORT,
        reload=settings.DEBUG,
        log_level="info",
    )
