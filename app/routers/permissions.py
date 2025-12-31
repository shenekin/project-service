"""
API router for permission management
"""

from typing import Optional
from fastapi import APIRouter, Request, Depends, HTTPException, status
from app.models.schemas import UserPermissionCreate, UserPermissionUpdate, UserPermissionResponse
from app.services.permission_service import PermissionService


router = APIRouter(prefix="/api/v1/permissions", tags=["permissions"])


def get_user_id(request: Request) -> str:
    """
    Extract user ID from request headers (set by gateway)
    
    Note:
        In development mode (DEBUG=true), if X-User-Id is not present,
        it will use a default test user ID. In production, this will raise 401.
    """
    from app.settings import get_settings
    
    user_id = request.headers.get("X-User-Id")
    
    if not user_id:
        settings = get_settings()
        if settings.debug:
            user_id = request.headers.get("X-Test-User-Id", "test-user-dev")
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User ID not found in request headers. Please ensure requests go through gateway with valid authentication."
            )
    
    return user_id


def get_client_info(request: Request) -> tuple[Optional[str], Optional[str]]:
    """Extract client IP and user agent from request"""
    ip_address = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")
    return ip_address, user_agent


@router.post("", response_model=UserPermissionResponse, status_code=status.HTTP_201_CREATED)
async def create_permission(
    permission_data: UserPermissionCreate,
    request: Request,
    user_id: str = Depends(get_user_id)
):
    """Create a new user permission"""
    ip_address, user_agent = get_client_info(request)
    service = PermissionService()
    return await service.create_permission(
        permission_data=permission_data,
        user_id=user_id,
        ip_address=ip_address,
        user_agent=user_agent
    )


@router.get("/users/{user_id}", response_model=list[UserPermissionResponse])
async def list_user_permissions(user_id: str):
    """List permissions for a user"""
    service = PermissionService()
    return await service.list_user_permissions(user_id)


@router.put("/{permission_id}", response_model=UserPermissionResponse)
async def update_permission(
    permission_id: int,
    permission_data: UserPermissionUpdate,
    request: Request,
    user_id: str = Depends(get_user_id)
):
    """Update user permission"""
    ip_address, user_agent = get_client_info(request)
    service = PermissionService()
    return await service.update_permission(
        permission_id=permission_id,
        permission_data=permission_data,
        user_id=user_id,
        ip_address=ip_address,
        user_agent=user_agent
    )


@router.delete("/{permission_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_permission(
    permission_id: int,
    request: Request,
    user_id: str = Depends(get_user_id)
):
    """Delete user permission"""
    ip_address, user_agent = get_client_info(request)
    service = PermissionService()
    await service.delete_permission(
        permission_id=permission_id,
        user_id=user_id,
        ip_address=ip_address,
        user_agent=user_agent
    )

