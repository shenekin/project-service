"""
Service layer for Permission & Access Control
"""

from typing import Optional, List
from fastapi import HTTPException, status
from app.dao.user_permission_dao import UserPermissionDAO
from app.dao.audit_log_dao import AuditLogDAO
from app.models.schemas import UserPermissionCreate, UserPermissionUpdate


class PermissionService:
    """Service for permission management operations"""
    
    def __init__(self):
        """Initialize permission service"""
        self.permission_dao = UserPermissionDAO()
        self.audit_log_dao = AuditLogDAO()
    
    async def create_permission(self, permission_data: UserPermissionCreate, user_id: str,
                                ip_address: Optional[str] = None,
                                user_agent: Optional[str] = None) -> dict:
        """Create a new user permission"""
        try:
            permission = await self.permission_dao.create(
                user_id=permission_data.user_id,
                customer_id=permission_data.customer_id,
                project_id=permission_data.project_id,
                permission_type=permission_data.permission_type
            )
            
            # Create audit log
            await self.audit_log_dao.create(
                user_id=user_id,
                action="create_permission",
                resource_type="permission",
                resource_id=permission.id,
                customer_id=permission.customer_id,
                project_id=permission.project_id,
                details=f"Created permission for user {permission.user_id}",
                ip_address=ip_address,
                user_agent=user_agent
            )
            
            return permission.to_dict()
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
    
    async def list_user_permissions(self, user_id: str) -> List[dict]:
        """List permissions for a user"""
        permissions = await self.permission_dao.list_by_user(user_id)
        return [p.to_dict() for p in permissions]
    
    async def check_permission(self, user_id: str, customer_id: Optional[int] = None,
                               project_id: Optional[int] = None) -> bool:
        """Check if user has permission"""
        return await self.permission_dao.check_permission(
            user_id=user_id,
            customer_id=customer_id,
            project_id=project_id
        )
    
    async def update_permission(self, permission_id: int, permission_data: UserPermissionUpdate,
                                user_id: str, ip_address: Optional[str] = None,
                                user_agent: Optional[str] = None) -> dict:
        """Update user permission"""
        permission = await self.permission_dao.update(
            permission_id=permission_id,
            permission_type=permission_data.permission_type
        )
        
        if not permission:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Permission with ID {permission_id} not found"
            )
        
        # Create audit log
        await self.audit_log_dao.create(
            user_id=user_id,
            action="update_permission",
            resource_type="permission",
            resource_id=permission.id,
            customer_id=permission.customer_id,
            project_id=permission.project_id,
            details=f"Updated permission for user {permission.user_id}",
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        return permission.to_dict()
    
    async def delete_permission(self, permission_id: int, user_id: str,
                                ip_address: Optional[str] = None,
                                user_agent: Optional[str] = None) -> bool:
        """Delete user permission"""
        permission = await self.permission_dao.get_by_id(permission_id)
        if not permission:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Permission with ID {permission_id} not found"
            )
        
        deleted = await self.permission_dao.delete(permission_id)
        
        if deleted:
            # Create audit log
            await self.audit_log_dao.create(
                user_id=user_id,
                action="delete_permission",
                resource_type="permission",
                resource_id=permission_id,
                customer_id=permission.customer_id,
                project_id=permission.project_id,
                details=f"Deleted permission for user {permission.user_id}",
                ip_address=ip_address,
                user_agent=user_agent
            )
        
        return deleted

