"""
Service layer for Project Management
"""

from typing import Optional, List
from fastapi import HTTPException, status
from app.dao.project_dao import ProjectDAO
from app.dao.customer_dao import CustomerDAO
from app.dao.audit_log_dao import AuditLogDAO
from app.models.schemas import ProjectCreate, ProjectUpdate


class ProjectService:
    """Service for project management operations"""
    
    def __init__(self):
        """Initialize project service"""
        self.project_dao = ProjectDAO()
        self.customer_dao = CustomerDAO()
        self.audit_log_dao = AuditLogDAO()
    
    async def create_project(self, project_data: ProjectCreate, user_id: str,
                             ip_address: Optional[str] = None,
                             user_agent: Optional[str] = None) -> dict:
        """Create a new project"""
        # Validate customer exists
        customer = await self.customer_dao.get_by_id(project_data.customer_id)
        if not customer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Customer with ID {project_data.customer_id} not found"
            )
        
        try:
            project = await self.project_dao.create(
                customer_id=project_data.customer_id,
                name=project_data.name,
                description=project_data.description
            )
            
            # Create audit log
            await self.audit_log_dao.create(
                user_id=user_id,
                action="create_project",
                resource_type="project",
                resource_id=project.id,
                customer_id=project.customer_id,
                project_id=project.id,
                details=f"Created project: {project.name} for customer: {customer.name}",
                ip_address=ip_address,
                user_agent=user_agent
            )
            
            return project.to_dict()
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
    
    async def get_project(self, project_id: int) -> dict:
        """Get project by ID"""
        project = await self.project_dao.get_by_id(project_id)
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Project with ID {project_id} not found"
            )
        return project.to_dict()
    
    async def list_projects_by_customer(self, customer_id: int, page: int = 1, page_size: int = 20) -> dict:
        """List projects by customer ID"""
        skip = (page - 1) * page_size
        projects = await self.project_dao.list_by_customer(customer_id, skip=skip, limit=page_size)
        
        return {
            "total": len(projects),
            "page": page,
            "page_size": page_size,
            "total_pages": (len(projects) + page_size - 1) // page_size,
            "items": [p.to_dict() for p in projects]
        }
    
    async def update_project(self, project_id: int, project_data: ProjectUpdate,
                            user_id: str, ip_address: Optional[str] = None,
                            user_agent: Optional[str] = None) -> dict:
        """Update project"""
        project = await self.project_dao.update(
            project_id=project_id,
            name=project_data.name,
            description=project_data.description
        )
        
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Project with ID {project_id} not found"
            )
        
        # Create audit log
        await self.audit_log_dao.create(
            user_id=user_id,
            action="update_project",
            resource_type="project",
            resource_id=project.id,
            customer_id=project.customer_id,
            project_id=project.id,
            details=f"Updated project: {project.name}",
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        return project.to_dict()
    
    async def delete_project(self, project_id: int, user_id: str,
                             ip_address: Optional[str] = None,
                             user_agent: Optional[str] = None) -> bool:
        """Delete project"""
        project = await self.project_dao.get_by_id(project_id)
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Project with ID {project_id} not found"
            )
        
        deleted = await self.project_dao.delete(project_id)
        
        if deleted:
            # Create audit log
            await self.audit_log_dao.create(
                user_id=user_id,
                action="delete_project",
                resource_type="project",
                resource_id=project_id,
                customer_id=project.customer_id,
                project_id=project_id,
                details=f"Deleted project: {project.name}",
                ip_address=ip_address,
                user_agent=user_agent
            )
        
        return deleted

