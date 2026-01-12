"""
API router for credential management
"""

from typing import Optional
from fastapi import APIRouter, Request, Depends, HTTPException, status
from app.models.schemas import (
    CredentialCreate, CredentialUpdate, CredentialContextResponse,
    CredentialListResponse, PaginationParams
)
from app.services.credential_service import CredentialService


router = APIRouter(prefix="/api/v1/credentials", tags=["credentials"])


def get_user_id(request: Request) -> str:
    """
    Extract user ID from request headers (set by gateway)
    
    Args:
        request: FastAPI request object
        
    Returns:
        User ID
        
    Note:
        In development mode (DEBUG=true), if X-User-Id is not present,
        it will use a default test user ID. In production, this will raise 401.
    """
    from app.settings import get_settings
    
    user_id = request.headers.get("X-User-Id")
    
    if not user_id:
        settings = get_settings()
        # In development mode, allow requests without X-User-Id header
        # Use a default test user ID for development/testing
        if settings.debug:
            user_id = request.headers.get("X-Test-User-Id", "test-user-dev")
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User ID not found in request headers. Please ensure requests go through gateway with valid authentication."
            )
    
    return user_id


def get_client_info(request: Request) -> tuple[Optional[str], Optional[str]]:
    """
    Extract client IP and user agent from request
    
    Args:
        request: FastAPI request object
        
    Returns:
        Tuple of (ip_address, user_agent)
    """
    ip_address = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")
    return ip_address, user_agent


@router.post("", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_credential(
    credential_data: CredentialCreate,
    request: Request,
    user_id: str = Depends(get_user_id)
):
    """
    Create a new credential (AK/SK registration)
    
    Args:
        credential_data: Credential creation data
        request: FastAPI request object
        user_id: User ID from request headers
        
    Returns:
        Created credential
    """
    ip_address, user_agent = get_client_info(request)
    service = CredentialService()
    return await service.create_credential(
        credential_data=credential_data,
        user_id=user_id,
        ip_address=ip_address,
        user_agent=user_agent
    )


@router.get("/context/{credential_id}", response_model=CredentialContextResponse)
async def get_credential_context(
    credential_id: int,
    request: Request,
    user_id: str = Depends(get_user_id)
):
    """
    Get credential context for internal services (without exposing SK)
    
    Args:
        credential_id: Credential ID
        request: FastAPI request object
        user_id: User ID from request headers
        
    Returns:
        Credential context
    """
    ip_address, user_agent = get_client_info(request)
    service = CredentialService()
    return await service.get_credential_context(
        credential_id=credential_id,
        user_id=user_id,
        ip_address=ip_address,
        user_agent=user_agent
    )


@router.get("", response_model=dict)
async def list_credentials(
    customer_id: Optional[int] = None,
    project_id: Optional[int] = None,
    page: int = 1,
    page_size: int = 20,
    request: Request = None,
    user_id: str = Depends(get_user_id)
):
    """
    List credentials available to user
    
    Args:
        customer_id: Optional customer ID filter
        project_id: Optional project ID filter
        page: Page number
        page_size: Page size
        request: FastAPI request object
        user_id: User ID from request headers
        
    Returns:
        Paginated list of credentials
    """
    service = CredentialService()
    return await service.list_credentials(
        user_id=user_id,
        customer_id=customer_id,
        project_id=project_id,
        page=page,
        page_size=page_size
    )


@router.put("/{credential_id}", response_model=dict)
async def update_credential(
    credential_id: int,
    credential_data: CredentialUpdate,
    request: Request,
    user_id: str = Depends(get_user_id)
):
    """
    Update credential
    
    Args:
        credential_id: Credential ID
        credential_data: Credential update data
        request: FastAPI request object
        user_id: User ID from request headers
        
    Returns:
        Updated credential
    """
    ip_address, user_agent = get_client_info(request)
    service = CredentialService()
    return await service.update_credential(
        credential_id=credential_id,
        credential_data=credential_data,
        user_id=user_id,
        ip_address=ip_address,
        user_agent=user_agent
    )


@router.get("/{credential_id}/api-credentials", response_model=dict)
async def get_credential_for_api_call(
    credential_id: int,
    request: Request,
    user_id: str = Depends(get_user_id)
):
    """
    Get full credential (AK and decrypted SK) for third-party API calls
    
    Args:
        credential_id: Credential ID
        request: FastAPI request object
        user_id: User ID from request headers
        
    Returns:
        Dictionary containing access_key and secret_key (decrypted)
    """
    ip_address, user_agent = get_client_info(request)
    service = CredentialService()
    return await service.get_credential_for_api_call(
        credential_id=credential_id,
        user_id=user_id,
        ip_address=ip_address,
        user_agent=user_agent
    )


@router.delete("/{credential_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_credential(
    credential_id: int,
    request: Request,
    user_id: str = Depends(get_user_id)
):
    """
    Delete credential (soft delete)
    
    Args:
        credential_id: Credential ID
        request: FastAPI request object
        user_id: User ID from request headers
    """
    ip_address, user_agent = get_client_info(request)
    service = CredentialService()
    await service.delete_credential(
        credential_id=credential_id,
        user_id=user_id,
        ip_address=ip_address,
        user_agent=user_agent
    )

