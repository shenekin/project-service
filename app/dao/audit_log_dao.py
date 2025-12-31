"""
Data Access Object for AuditLog entity
"""

from typing import Optional, List
from app.models.entities import AuditLog
from app.utils.db_connection import get_db_connection


class AuditLogDAO:
    """Data Access Object for AuditLog operations"""
    
    async def create(self, user_id: str, action: str, resource_type: str,
                     resource_id: Optional[int] = None,
                     customer_id: Optional[int] = None,
                     project_id: Optional[int] = None,
                     vendor_id: Optional[int] = None,
                     credential_id: Optional[int] = None,
                     details: Optional[str] = None,
                     ip_address: Optional[str] = None,
                     user_agent: Optional[str] = None) -> AuditLog:
        """Create a new audit log entry"""
        db = await get_db_connection()
        pool = await db.get_pool()
        
        async with pool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute(
                    """INSERT INTO audit_logs (user_id, action, resource_type, resource_id, customer_id, project_id, vendor_id, credential_id, details, ip_address, user_agent)
                       VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                    (user_id, action, resource_type, resource_id, customer_id, project_id, vendor_id, credential_id, details, ip_address, user_agent)
                )
                log_id = cursor.lastrowid
                await conn.commit()
                
                await cursor.execute(
                    """SELECT id, user_id, action, resource_type, resource_id, customer_id, project_id, vendor_id, credential_id, details, ip_address, user_agent, created_at
                       FROM audit_logs WHERE id = %s""",
                    (log_id,)
                )
                row = await cursor.fetchone()
                
                return AuditLog(
                    id=row[0],
                    user_id=row[1],
                    action=row[2],
                    resource_type=row[3],
                    resource_id=row[4],
                    customer_id=row[5],
                    project_id=row[6],
                    vendor_id=row[7],
                    credential_id=row[8],
                    details=row[9],
                    ip_address=row[10],
                    user_agent=row[11],
                    created_at=row[12]
                )
    
    async def list_by_user(self, user_id: str, skip: int = 0, limit: int = 100) -> List[AuditLog]:
        """List audit logs by user ID"""
        db = await get_db_connection()
        pool = await db.get_pool()
        
        async with pool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute(
                    """SELECT id, user_id, action, resource_type, resource_id, customer_id, project_id, vendor_id, credential_id, details, ip_address, user_agent, created_at
                       FROM audit_logs WHERE user_id = %s ORDER BY created_at DESC LIMIT %s OFFSET %s""",
                    (user_id, limit, skip)
                )
                rows = await cursor.fetchall()
                
                return [
                    AuditLog(
                        id=row[0],
                        user_id=row[1],
                        action=row[2],
                        resource_type=row[3],
                        resource_id=row[4],
                        customer_id=row[5],
                        project_id=row[6],
                        vendor_id=row[7],
                        credential_id=row[8],
                        details=row[9],
                        ip_address=row[10],
                        user_agent=row[11],
                        created_at=row[12]
                    )
                    for row in rows
                ]
    
    async def list_by_credential(self, credential_id: int, skip: int = 0, limit: int = 100) -> List[AuditLog]:
        """List audit logs by credential ID"""
        db = await get_db_connection()
        pool = await db.get_pool()
        
        async with pool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute(
                    """SELECT id, user_id, action, resource_type, resource_id, customer_id, project_id, vendor_id, credential_id, details, ip_address, user_agent, created_at
                       FROM audit_logs WHERE credential_id = %s ORDER BY created_at DESC LIMIT %s OFFSET %s""",
                    (credential_id, limit, skip)
                )
                rows = await cursor.fetchall()
                
                return [
                    AuditLog(
                        id=row[0],
                        user_id=row[1],
                        action=row[2],
                        resource_type=row[3],
                        resource_id=row[4],
                        customer_id=row[5],
                        project_id=row[6],
                        vendor_id=row[7],
                        credential_id=row[8],
                        details=row[9],
                        ip_address=row[10],
                        user_agent=row[11],
                        created_at=row[12]
                    )
                    for row in rows
                ]

