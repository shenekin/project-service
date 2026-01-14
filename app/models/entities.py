"""
Database entity models
"""

from datetime import datetime
from typing import Optional


class Customer:
    """Customer entity model"""
    
    def __init__(
        self,
        id: int,
        name: str,
        description: Optional[str] = None,
        contact_email: Optional[str] = None,
        contact_phone: Optional[str] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None
    ):
        """Initialize customer entity"""
        self.id = id
        self.name = name
        self.description = description
        self.contact_email = contact_email
        self.contact_phone = contact_phone
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()
    
    def to_dict(self) -> dict:
        """Convert entity to dictionary"""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "contact_email": self.contact_email,
            "contact_phone": self.contact_phone,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }


class Project:
    """Project entity model"""
    
    def __init__(
        self,
        id: int,
        customer_id: int,
        name: str,
        description: Optional[str] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None
    ):
        """Initialize project entity"""
        self.id = id
        self.customer_id = customer_id
        self.name = name
        self.description = description
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()
    
    def to_dict(self) -> dict:
        """Convert entity to dictionary"""
        return {
            "id": self.id,
            "customer_id": self.customer_id,
            "name": self.name,
            "description": self.description,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }


class Vendor:
    """Vendor entity model"""
    
    def __init__(
        self,
        id: int,
        name: str,
        display_name: str,
        description: Optional[str] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None
    ):
        """Initialize vendor entity"""
        self.id = id
        self.name = name
        self.display_name = display_name
        self.description = description
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()
    
    def to_dict(self) -> dict:
        """Convert entity to dictionary"""
        return {
            "id": self.id,
            "name": self.name,
            "display_name": self.display_name,
            "description": self.description,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }


class Credential:
    """Credential entity model"""
    
    def __init__(
        self,
        id: int,
        customer_id: int,
        project_id: int,
        vendor_id: int,
        access_key: str,
        secret_key: Optional[str] = None,
        resource_user: Optional[str] = None,
        labels: Optional[str] = None,
        status: str = "active",
        vault_path: Optional[str] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None
    ):
        """Initialize credential entity"""
        self.id = id
        self.customer_id = customer_id
        self.project_id = project_id
        self.vendor_id = vendor_id
        self.access_key = access_key
        self.secret_key = secret_key
        self.resource_user = resource_user
        self.labels = labels
        self.status = status
        self.vault_path = vault_path
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()
    
    def to_dict(self, include_secret: bool = False) -> dict:
        """Convert entity to dictionary"""
        result = {
            "id": self.id,
            "customer_id": self.customer_id,
            "project_id": self.project_id,
            "vendor_id": self.vendor_id,
            "access_key": self.access_key,
            "resource_user": self.resource_user,
            "labels": self.labels,
            "status": self.status,
            "vault_path": self.vault_path,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }
        if include_secret:
            result["secret_key"] = self.secret_key
        return result


class AuditLog:
    """Audit log entity model"""
    
    def __init__(
        self,
        id: int,
        user_id: str,
        action: str,
        resource_type: str,
        resource_id: Optional[int] = None,
        customer_id: Optional[int] = None,
        project_id: Optional[int] = None,
        vendor_id: Optional[int] = None,
        credential_id: Optional[int] = None,
        details: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        created_at: Optional[datetime] = None
    ):
        """Initialize audit log entity"""
        self.id = id
        self.user_id = user_id
        self.action = action
        self.resource_type = resource_type
        self.resource_id = resource_id
        self.customer_id = customer_id
        self.project_id = project_id
        self.vendor_id = vendor_id
        self.credential_id = credential_id
        self.details = details
        self.ip_address = ip_address
        self.user_agent = user_agent
        self.created_at = created_at or datetime.utcnow()
    
    def to_dict(self) -> dict:
        """Convert entity to dictionary"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "action": self.action,
            "resource_type": self.resource_type,
            "resource_id": self.resource_id,
            "customer_id": self.customer_id,
            "project_id": self.project_id,
            "vendor_id": self.vendor_id,
            "credential_id": self.credential_id,
            "details": self.details,
            "ip_address": self.ip_address,
            "user_agent": self.user_agent,
            "created_at": self.created_at
        }


class UserPermission:
    """User permission entity model"""
    
    def __init__(
        self,
        id: int,
        user_id: str,
        customer_id: Optional[int] = None,
        project_id: Optional[int] = None,
        permission_type: str = "read",
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None
    ):
        """Initialize user permission entity"""
        self.id = id
        self.user_id = user_id
        self.customer_id = customer_id
        self.project_id = project_id
        self.permission_type = permission_type
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()
    
    def to_dict(self) -> dict:
        """Convert entity to dictionary"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "customer_id": self.customer_id,
            "project_id": self.project_id,
            "permission_type": self.permission_type,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }

