"""
Application bootstrap and initialization
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.settings import get_settings
from app.utils import configure_logging
from app.routers import credentials, customers, projects, vendors, permissions, audit, version
from app.utils.db_connection import close_db_connection


def create_app() -> FastAPI:
    """
    Create and configure FastAPI application
    
    Returns:
        Configured FastAPI application
    """
    settings = get_settings()
    configure_logging(settings)
    
    app = FastAPI(
        title="Project Service",
        description="Project Service for Cloud Resource Management System - Credential Management",
        version="1.0.0",
        debug=settings.debug
    )
    
    # Configure CORS
    if settings.cors_enabled:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=settings.allowed_origins_list,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"]
        )
    
    # Include routers
    app.include_router(credentials.router)
    app.include_router(customers.router)
    app.include_router(projects.router)
    app.include_router(vendors.router)
    app.include_router(permissions.router)
    app.include_router(audit.router)
    app.include_router(version.router)
    
    # Startup event
    @app.on_event("startup")
    async def startup_event():
        """Initialize services on startup"""
        # Database connection will be created on first use
        pass
    
    # Shutdown event
    @app.on_event("shutdown")
    async def shutdown_event():
        """Cleanup on shutdown"""
        await close_db_connection()
    
    return app

