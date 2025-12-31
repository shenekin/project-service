"""
Data Access Object for UserPermission entity
"""

from typing import Optional, List
from app.models.entities import UserPermission
from app.utils.db_connection import get_db_connection


class UserPermissionDAO:
    """Data Access Object for UserPermission operations"""
    
    async def create(self, user_id: str, customer_id: Optional[int] = None,
                     project_id: Optional[int] = None,
                     permission_type: str = "read") -> UserPermission:
        """Create a new user permission"""
        db = await get_db_connection()
        pool = await db.get_pool()
        
        async with pool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute(
                    """INSERT INTO user_permissions (user_id, customer_id, project_id, permission_type)
                       VALUES (%s, %s, %s, %s)""",
                    (user_id, customer_id, project_id, permission_type)
                )
                permission_id = cursor.lastrowid
                await conn.commit()
                
                await cursor.execute(
                    "SELECT id, user_id, customer_id, project_id, permission_type, created_at, updated_at FROM user_permissions WHERE id = %s",
                    (permission_id,)
                )
                row = await cursor.fetchone()
                
                return UserPermission(
                    id=row[0],
                    user_id=row[1],
                    customer_id=row[2],
                    project_id=row[3],
                    permission_type=row[4],
                    created_at=row[5],
                    updated_at=row[6]
                )
    
    async def get_by_id(self, permission_id: int) -> Optional[UserPermission]:
        """Get user permission by ID"""
        db = await get_db_connection()
        pool = await db.get_pool()
        
        async with pool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute(
                    "SELECT id, user_id, customer_id, project_id, permission_type, created_at, updated_at FROM user_permissions WHERE id = %s",
                    (permission_id,)
                )
                row = await cursor.fetchone()
                
                if not row:
                    return None
                
                return UserPermission(
                    id=row[0],
                    user_id=row[1],
                    customer_id=row[2],
                    project_id=row[3],
                    permission_type=row[4],
                    created_at=row[5],
                    updated_at=row[6]
                )
    
    async def list_by_user(self, user_id: str) -> List[UserPermission]:
        """List permissions by user ID"""
        db = await get_db_connection()
        pool = await db.get_pool()
        
        async with pool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute(
                    "SELECT id, user_id, customer_id, project_id, permission_type, created_at, updated_at FROM user_permissions WHERE user_id = %s",
                    (user_id,)
                )
                rows = await cursor.fetchall()
                
                return [
                    UserPermission(
                        id=row[0],
                        user_id=row[1],
                        customer_id=row[2],
                        project_id=row[3],
                        permission_type=row[4],
                        created_at=row[5],
                        updated_at=row[6]
                    )
                    for row in rows
                ]
    
    async def check_permission(self, user_id: str, customer_id: Optional[int] = None,
                               project_id: Optional[int] = None) -> bool:
        """
        Check if user has permission for customer/project
        
        Args:
            user_id: User ID
            customer_id: Customer ID (None for all customers)
            project_id: Project ID (None for all projects)
            
        Returns:
            True if user has permission
        """
        db = await get_db_connection()
        pool = await db.get_pool()
        
        async with pool.acquire() as conn:
            async with conn.cursor() as cursor:
                query = """
                    SELECT COUNT(*) FROM user_permissions
                    WHERE user_id = %s
                    AND (customer_id IS NULL OR customer_id = %s)
                    AND (project_id IS NULL OR project_id = %s)
                """
                await cursor.execute(query, (user_id, customer_id, project_id))
                row = await cursor.fetchone()
                return row[0] > 0 if row else False
    
    async def update(self, permission_id: int, permission_type: Optional[str] = None) -> Optional[UserPermission]:
        """Update user permission"""
        db = await get_db_connection()
        pool = await db.get_pool()
        
        async with pool.acquire() as conn:
            async with conn.cursor() as cursor:
                if permission_type is None:
                    return await self.get_by_id(permission_id)
                
                await cursor.execute(
                    "UPDATE user_permissions SET permission_type = %s WHERE id = %s",
                    (permission_type, permission_id)
                )
                await conn.commit()
                
                if cursor.rowcount == 0:
                    return None
                
                return await self.get_by_id(permission_id)
    
    async def delete(self, permission_id: int) -> bool:
        """Delete user permission"""
        db = await get_db_connection()
        pool = await db.get_pool()
        
        async with pool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute("DELETE FROM user_permissions WHERE id = %s", (permission_id,))
                await conn.commit()
                return cursor.rowcount > 0

