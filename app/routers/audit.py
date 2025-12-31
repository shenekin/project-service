"""
API router for audit logging
"""

from fastapi import APIRouter
from app.services.audit_service import AuditService


router = APIRouter(prefix="/api/v1/audit", tags=["audit"])


@router.get("/users/{user_id}", response_model=dict)
async def list_audit_logs_by_user(user_id: str, page: int = 1, page_size: int = 20):
    """List audit logs by user ID"""
    service = AuditService()
    return await service.list_audit_logs_by_user(user_id, page=page, page_size=page_size)


@router.get("/credentials/{credential_id}", response_model=dict)
async def list_audit_logs_by_credential(credential_id: int, page: int = 1, page_size: int = 20):
    """List audit logs by credential ID"""
    service = AuditService()
    return await service.list_audit_logs_by_credential(credential_id, page=page, page_size=page_size)

