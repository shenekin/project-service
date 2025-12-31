"""
Service layer for Audit & Logging
"""

from typing import Optional, List
from app.dao.audit_log_dao import AuditLogDAO
from app.models.schemas import AuditLogResponse


class AuditService:
    """Service for audit logging operations"""
    
    def __init__(self):
        """Initialize audit service"""
        self.audit_log_dao = AuditLogDAO()
    
    async def list_audit_logs_by_user(self, user_id: str, page: int = 1, page_size: int = 20) -> dict:
        """List audit logs by user ID"""
        skip = (page - 1) * page_size
        logs = await self.audit_log_dao.list_by_user(user_id, skip=skip, limit=page_size)
        
        return {
            "total": len(logs),
            "page": page,
            "page_size": page_size,
            "total_pages": (len(logs) + page_size - 1) // page_size,
            "items": [log.to_dict() for log in logs]
        }
    
    async def list_audit_logs_by_credential(self, credential_id: int, page: int = 1, page_size: int = 20) -> dict:
        """List audit logs by credential ID"""
        skip = (page - 1) * page_size
        logs = await self.audit_log_dao.list_by_credential(credential_id, skip=skip, limit=page_size)
        
        return {
            "total": len(logs),
            "page": page,
            "page_size": page_size,
            "total_pages": (len(logs) + page_size - 1) // page_size,
            "items": [log.to_dict() for log in logs]
        }

