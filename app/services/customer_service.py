"""
Service layer for Customer Management
"""

from typing import Optional, List
from fastapi import HTTPException, status
from app.dao.customer_dao import CustomerDAO
from app.dao.audit_log_dao import AuditLogDAO
from app.models.schemas import CustomerCreate, CustomerUpdate


class CustomerService:
    """Service for customer management operations"""
    
    def __init__(self):
        """Initialize customer service"""
        self.customer_dao = CustomerDAO()
        self.audit_log_dao = AuditLogDAO()
    
    async def create_customer(self, customer_data: CustomerCreate, user_id: str,
                              ip_address: Optional[str] = None,
                              user_agent: Optional[str] = None) -> dict:
        """Create a new customer"""
        try:
            customer = await self.customer_dao.create(
                name=customer_data.name
            )
            
            # Create audit log
            await self.audit_log_dao.create(
                user_id=user_id,
                action="create_customer",
                resource_type="customer",
                resource_id=customer.id,
                customer_id=customer.id,
                details=f"Created customer: {customer.name}",
                ip_address=ip_address,
                user_agent=user_agent
            )
            
            return customer.to_dict()
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
    
    async def get_customer(self, customer_id: int) -> dict:
        """Get customer by ID"""
        customer = await self.customer_dao.get_by_id(customer_id)
        if not customer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Customer with ID {customer_id} not found"
            )
        return customer.to_dict()
    
    async def list_customers(self, page: int = 1, page_size: int = 20) -> dict:
        """List all customers with pagination"""
        skip = (page - 1) * page_size
        customers = await self.customer_dao.list_all(skip=skip, limit=page_size)
        total = await self.customer_dao.count()
        
        return {
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size,
            "items": [c.to_dict() for c in customers]
        }
    
    async def update_customer(self, customer_id: int, customer_data: CustomerUpdate,
                              user_id: str, ip_address: Optional[str] = None,
                              user_agent: Optional[str] = None) -> dict:
        """Update customer"""
        customer = await self.customer_dao.update(
            customer_id=customer_id,
            name=customer_data.name
        )
        
        if not customer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Customer with ID {customer_id} not found"
            )
        
        # Create audit log
        await self.audit_log_dao.create(
            user_id=user_id,
            action="update_customer",
            resource_type="customer",
            resource_id=customer.id,
            customer_id=customer.id,
            details=f"Updated customer: {customer.name}",
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        return customer.to_dict()
    
    async def delete_customer(self, customer_id: int, user_id: str,
                             ip_address: Optional[str] = None,
                             user_agent: Optional[str] = None) -> bool:
        """Delete customer"""
        customer = await self.customer_dao.get_by_id(customer_id)
        if not customer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Customer with ID {customer_id} not found"
            )
        
        deleted = await self.customer_dao.delete(customer_id)
        
        if deleted:
            # Create audit log
            await self.audit_log_dao.create(
                user_id=user_id,
                action="delete_customer",
                resource_type="customer",
                resource_id=customer_id,
                customer_id=customer_id,
                details=f"Deleted customer: {customer.name}",
                ip_address=ip_address,
                user_agent=user_agent
            )
        
        return deleted

