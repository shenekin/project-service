"""
API router for version information
"""

from fastapi import APIRouter
from datetime import datetime
from app.settings import get_settings


router = APIRouter(prefix="/api/v1/version", tags=["version"])


@router.get("", response_model=dict)
async def get_version():
    """
    Get API version information for software iteration tracking
    
    Returns:
        Version information including API version, service version, and build timestamp
    """
    settings = get_settings()
    
    return {
        "api_version": "v1",
        "service_version": "1.0.0",
        "service_name": "project-service",
        "build_timestamp": datetime.utcnow().isoformat(),
        "environment": settings.environment
    }

