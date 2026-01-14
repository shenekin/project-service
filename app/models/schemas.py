"""
Pydantic schemas for request/response validation
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, field_validator


class CustomerCreate(BaseModel):
    """Schema for creating a customer"""
    name: str = Field(..., description="Customer name (required)", min_length=1, max_length=255)
    description: Optional[str] = Field(None, description="Customer description (optional)", max_length=1000)
    contact_email: Optional[str] = Field(None, description="Contact email (optional)", max_length=255)
    contact_phone: Optional[str] = Field(None, description="Contact phone (optional)", max_length=50)
    
    @field_validator('description', 'contact_email', 'contact_phone', mode='before')
    @classmethod
    def normalize_empty_strings(cls, v):
        """Convert empty strings and 'string' literal to None"""
        if v is None:
            return None
        if isinstance(v, str):
            v = v.strip()
            if v == '' or v.lower() == 'string':
                return None
        return v


class CustomerUpdate(BaseModel):
    """Schema for updating a customer"""
    name: Optional[str] = Field(None, description="Customer name (optional)", min_length=1, max_length=255)
    description: Optional[str] = Field(None, description="Customer description (optional)", max_length=1000)
    contact_email: Optional[str] = Field(None, description="Contact email (optional)", max_length=255)
    contact_phone: Optional[str] = Field(None, description="Contact phone (optional)", max_length=50)
    
    @field_validator('name', 'description', 'contact_email', 'contact_phone', mode='before')
    @classmethod
    def normalize_empty_strings(cls, v):
        """Convert empty strings and 'string' literal to None"""
        if v is None:
            return None
        if isinstance(v, str):
            v = v.strip()
            if v == '' or v.lower() == 'string':
                return None
        return v


class CustomerResponse(BaseModel):
    """Schema for customer response"""
    id: int
    name: str
    description: Optional[str]
    contact_email: Optional[str]
    contact_phone: Optional[str]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class ProjectCreate(BaseModel):
    """Schema for creating a project"""
    customer_id: int = Field(..., description="Customer ID", gt=0)
    name: str = Field(..., description="Project name", min_length=1, max_length=255)
    description: Optional[str] = Field(None, description="Project description", max_length=1000)


class ProjectUpdate(BaseModel):
    """Schema for updating a project"""
    name: Optional[str] = Field(None, description="Project name", min_length=1, max_length=255)
    description: Optional[str] = Field(None, description="Project description", max_length=1000)


class ProjectResponse(BaseModel):
    """Schema for project response"""
    id: int
    customer_id: int
    name: str
    description: Optional[str]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class VendorCreate(BaseModel):
    """Schema for creating a vendor"""
    name: str = Field(..., description="Vendor name", min_length=1, max_length=100)
    display_name: str = Field(..., description="Vendor display name", min_length=1, max_length=255)
    description: Optional[str] = Field(None, description="Vendor description", max_length=1000)


class VendorUpdate(BaseModel):
    """Schema for updating a vendor"""
    display_name: Optional[str] = Field(None, description="Vendor display name", min_length=1, max_length=255)
    description: Optional[str] = Field(None, description="Vendor description", max_length=1000)


class VendorResponse(BaseModel):
    """Schema for vendor response"""
    id: int
    name: str
    display_name: str
    description: Optional[str]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class CredentialCreate(BaseModel):
    """Schema for creating a credential"""
    customer_id: int = Field(..., description="Customer ID", gt=0)
    project_id: int = Field(..., description="Project ID", gt=0)
    vendor_id: int = Field(..., description="Vendor ID", gt=0)
    access_key: str = Field(..., description="Access Key (AK)", min_length=1, max_length=255)
    secret_key: str = Field(..., description="Secret Key (SK)", min_length=1)
    resource_user: Optional[str] = Field(None, description="Associated resource user", max_length=255)
    labels: Optional[str] = Field(None, description="Friendly labels or tags", max_length=500)
    status: str = Field("active", description="Credential status", pattern="^(active|disabled|deleted)$")


class CredentialUpdate(BaseModel):
    """Schema for updating a credential"""
    access_key: Optional[str] = Field(None, description="Access Key (AK)", min_length=1, max_length=255)
    secret_key: Optional[str] = Field(None, description="Secret Key (SK)", min_length=1)
    resource_user: Optional[str] = Field(None, description="Associated resource user", max_length=255)
    labels: Optional[str] = Field(None, description="Friendly labels or tags", max_length=500)
    status: Optional[str] = Field(None, description="Credential status", pattern="^(active|disabled|deleted)$")


class CredentialResponse(BaseModel):
    """Schema for credential response (without SK)"""
    id: int
    customer_id: int
    project_id: int
    vendor_id: int
    access_key: str
    resource_user: Optional[str]
    labels: Optional[str]
    status: str
    vault_path: Optional[str]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class CredentialContextResponse(BaseModel):
    """Schema for credential context response (for internal services)"""
    credential_id: int
    customer_name: str
    project_name: str
    vendor_name: str
    vendor_display_name: str
    access_key: str
    vault_path: str
    resource_user: Optional[str]
    status: str
    labels: Optional[str]


class CredentialListResponse(BaseModel):
    """Schema for listing credentials (with masked AK)"""
    id: int
    customer_name: str
    project_name: str
    vendor_name: str
    vendor_display_name: str
    access_key: str  # Masked access key (first 4 characters visible)
    resource_user: Optional[str]
    status: str
    labels: Optional[str]
    created_at: datetime
    updated_at: datetime


class AuditLogResponse(BaseModel):
    """Schema for audit log response"""
    id: int
    user_id: str
    action: str
    resource_type: str
    resource_id: Optional[int]
    customer_id: Optional[int]
    project_id: Optional[int]
    vendor_id: Optional[int]
    credential_id: Optional[int]
    details: Optional[str]
    ip_address: Optional[str]
    user_agent: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True


class UserPermissionCreate(BaseModel):
    """Schema for creating user permission"""
    user_id: str = Field(..., description="User ID", min_length=1, max_length=255)
    customer_id: Optional[int] = Field(None, description="Customer ID (None for all customers)", gt=0)
    project_id: Optional[int] = Field(None, description="Project ID (None for all projects)", gt=0)
    permission_type: str = Field(..., description="Permission type", pattern="^(read|write|admin)$")


class UserPermissionUpdate(BaseModel):
    """Schema for updating user permission"""
    permission_type: Optional[str] = Field(None, description="Permission type", pattern="^(read|write|admin)$")


class UserPermissionResponse(BaseModel):
    """Schema for user permission response"""
    id: int
    user_id: str
    customer_id: Optional[int]
    project_id: Optional[int]
    permission_type: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class CredentialUsageRequest(BaseModel):
    """Schema for credential usage request"""
    credential_id: int = Field(..., description="Credential ID", gt=0)
    action: str = Field(..., description="Action being performed", min_length=1, max_length=255)


class PaginationParams(BaseModel):
    """Schema for pagination parameters"""
    page: int = Field(1, description="Page number", ge=1)
    page_size: int = Field(20, description="Page size", ge=1, le=100)


class PaginatedResponse(BaseModel):
    """Schema for paginated response"""
    total: int
    page: int
    page_size: int
    total_pages: int
    items: List[dict]

