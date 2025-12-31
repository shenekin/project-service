"""
API router for customer management
"""

from typing import Optional
from fastapi import APIRouter, Request, Depends, HTTPException, status
from app.models.schemas import CustomerCreate, CustomerUpdate, CustomerResponse
from app.services.customer_service import CustomerService


router = APIRouter(prefix="/api/v1/customers", tags=["customers"])


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


@router.post("", response_model=CustomerResponse, status_code=status.HTTP_201_CREATED)
async def create_customer(
    customer_data: CustomerCreate,
    request: Request,
    user_id: str = Depends(get_user_id)
):
    """Create a new customer"""
    ip_address, user_agent = get_client_info(request)
    service = CustomerService()
    return await service.create_customer(
        customer_data=customer_data,
        user_id=user_id,
        ip_address=ip_address,
        user_agent=user_agent
    )


@router.get("/{customer_id}", response_model=CustomerResponse)
async def get_customer(customer_id: int):
    """Get customer by ID"""
    service = CustomerService()
    return await service.get_customer(customer_id)


@router.get("", response_model=dict)
async def list_customers(page: int = 1, page_size: int = 20):
    """List all customers with pagination"""
    service = CustomerService()
    return await service.list_customers(page=page, page_size=page_size)


@router.put("/{customer_id}", response_model=CustomerResponse)
async def update_customer(
    customer_id: int,
    customer_data: CustomerUpdate,
    request: Request,
    user_id: str = Depends(get_user_id)
):
    """Update customer"""
    ip_address, user_agent = get_client_info(request)
    service = CustomerService()
    return await service.update_customer(
        customer_id=customer_id,
        customer_data=customer_data,
        user_id=user_id,
        ip_address=ip_address,
        user_agent=user_agent
    )


@router.delete("/{customer_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_customer(
    customer_id: int,
    request: Request,
    user_id: str = Depends(get_user_id)
):
    """Delete customer"""
    ip_address, user_agent = get_client_info(request)
    service = CustomerService()
    await service.delete_customer(
        customer_id=customer_id,
        user_id=user_id,
        ip_address=ip_address,
        user_agent=user_agent
    )

