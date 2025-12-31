"""
API router for project management
"""

from typing import Optional
from fastapi import APIRouter, Request, Depends, HTTPException, status
from app.models.schemas import ProjectCreate, ProjectUpdate, ProjectResponse
from app.services.project_service import ProjectService


router = APIRouter(prefix="/api/v1/projects", tags=["projects"])


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


@router.post("", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(
    project_data: ProjectCreate,
    request: Request,
    user_id: str = Depends(get_user_id)
):
    """Create a new project"""
    ip_address, user_agent = get_client_info(request)
    service = ProjectService()
    return await service.create_project(
        project_data=project_data,
        user_id=user_id,
        ip_address=ip_address,
        user_agent=user_agent
    )


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(project_id: int):
    """Get project by ID"""
    service = ProjectService()
    return await service.get_project(project_id)


@router.get("", response_model=dict)
async def list_projects(customer_id: Optional[int] = None, page: int = 1, page_size: int = 20):
    """List projects with pagination"""
    service = ProjectService()
    if customer_id:
        return await service.list_projects_by_customer(customer_id, page=page, page_size=page_size)
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="customer_id parameter is required"
        )


@router.put("/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: int,
    project_data: ProjectUpdate,
    request: Request,
    user_id: str = Depends(get_user_id)
):
    """Update project"""
    ip_address, user_agent = get_client_info(request)
    service = ProjectService()
    return await service.update_project(
        project_id=project_id,
        project_data=project_data,
        user_id=user_id,
        ip_address=ip_address,
        user_agent=user_agent
    )


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(
    project_id: int,
    request: Request,
    user_id: str = Depends(get_user_id)
):
    """Delete project"""
    ip_address, user_agent = get_client_info(request)
    service = ProjectService()
    await service.delete_project(
        project_id=project_id,
        user_id=user_id,
        ip_address=ip_address,
        user_agent=user_agent
    )

