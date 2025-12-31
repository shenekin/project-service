"""
Data Access Object for Credential entity
"""

from typing import Optional, List
from app.models.entities import Credential
from app.utils.db_connection import get_db_connection


class CredentialDAO:
    """Data Access Object for Credential operations"""
    
    async def create(self, customer_id: int, project_id: int, vendor_id: int,
                     access_key: str, vault_path: Optional[str] = None,
                     resource_user: Optional[str] = None,
                     labels: Optional[str] = None,
                     status: str = "active") -> Credential:
        """Create a new credential"""
        db = await get_db_connection()
        pool = await db.get_pool()
        
        async with pool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute(
                    """INSERT INTO credentials (customer_id, project_id, vendor_id, access_key, vault_path, resource_user, labels, status)
                       VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""",
                    (customer_id, project_id, vendor_id, access_key, vault_path, resource_user, labels, status)
                )
                credential_id = cursor.lastrowid
                await conn.commit()
                
                await cursor.execute(
                    """SELECT id, customer_id, project_id, vendor_id, access_key, vault_path, resource_user, labels, status, created_at, updated_at
                       FROM credentials WHERE id = %s""",
                    (credential_id,)
                )
                row = await cursor.fetchone()
                
                return Credential(
                    id=row[0],
                    customer_id=row[1],
                    project_id=row[2],
                    vendor_id=row[3],
                    access_key=row[4],
                    vault_path=row[5],
                    resource_user=row[6],
                    labels=row[7],
                    status=row[8],
                    created_at=row[9],
                    updated_at=row[10]
                )
    
    async def get_by_id(self, credential_id: int) -> Optional[Credential]:
        """Get credential by ID"""
        db = await get_db_connection()
        pool = await db.get_pool()
        
        async with pool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute(
                    """SELECT id, customer_id, project_id, vendor_id, access_key, vault_path, resource_user, labels, status, created_at, updated_at
                       FROM credentials WHERE id = %s""",
                    (credential_id,)
                )
                row = await cursor.fetchone()
                
                if not row:
                    return None
                
                return Credential(
                    id=row[0],
                    customer_id=row[1],
                    project_id=row[2],
                    vendor_id=row[3],
                    access_key=row[4],
                    vault_path=row[5],
                    resource_user=row[6],
                    labels=row[7],
                    status=row[8],
                    created_at=row[9],
                    updated_at=row[10]
                )
    
    async def list_by_user_permissions(self, user_id: str, customer_id: Optional[int] = None,
                                       project_id: Optional[int] = None,
                                       skip: int = 0, limit: int = 100) -> List[dict]:
        """
        List credentials filtered by user permissions
        
        Args:
            user_id: User ID
            customer_id: Optional customer ID filter
            project_id: Optional project ID filter
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of credential dictionaries with customer/project/vendor names
        """
        db = await get_db_connection()
        pool = await db.get_pool()
        
        async with pool.acquire() as conn:
            async with conn.cursor() as cursor:
                # Build query with permission check
                query = """
                    SELECT c.id, c.customer_id, c.project_id, c.vendor_id, c.access_key, c.vault_path,
                           c.resource_user, c.labels, c.status, c.created_at, c.updated_at,
                           cust.name as customer_name, p.name as project_name,
                           v.name as vendor_name, v.display_name as vendor_display_name
                    FROM credentials c
                    INNER JOIN customers cust ON c.customer_id = cust.id
                    INNER JOIN projects p ON c.project_id = p.id
                    INNER JOIN vendors v ON c.vendor_id = v.id
                    WHERE c.status != 'deleted'
                """
                params = []
                
                # Add permission filter
                query += """
                    AND (
                        EXISTS (
                            SELECT 1 FROM user_permissions up
                            WHERE up.user_id = %s
                            AND (up.customer_id IS NULL OR up.customer_id = c.customer_id)
                            AND (up.project_id IS NULL OR up.project_id = c.project_id)
                        )
                    )
                """
                params.append(user_id)
                
                # Add optional filters
                if customer_id:
                    query += " AND c.customer_id = %s"
                    params.append(customer_id)
                if project_id:
                    query += " AND c.project_id = %s"
                    params.append(project_id)
                
                query += " ORDER BY c.created_at DESC LIMIT %s OFFSET %s"
                params.extend([limit, skip])
                
                await cursor.execute(query, params)
                rows = await cursor.fetchall()
                
                return [
                    {
                        "id": row[0],
                        "customer_id": row[1],
                        "project_id": row[2],
                        "vendor_id": row[3],
                        "access_key": row[4],
                        "vault_path": row[5],
                        "resource_user": row[6],
                        "labels": row[7],
                        "status": row[8],
                        "created_at": row[9],
                        "updated_at": row[10],
                        "customer_name": row[11],
                        "project_name": row[12],
                        "vendor_name": row[13],
                        "vendor_display_name": row[14]
                    }
                    for row in rows
                ]
    
    async def update(self, credential_id: int, resource_user: Optional[str] = None,
                     labels: Optional[str] = None, status: Optional[str] = None) -> Optional[Credential]:
        """Update credential"""
        db = await get_db_connection()
        pool = await db.get_pool()
        
        async with pool.acquire() as conn:
            async with conn.cursor() as cursor:
                updates = []
                params = []
                
                if resource_user is not None:
                    updates.append("resource_user = %s")
                    params.append(resource_user)
                if labels is not None:
                    updates.append("labels = %s")
                    params.append(labels)
                if status is not None:
                    updates.append("status = %s")
                    params.append(status)
                
                if not updates:
                    return await self.get_by_id(credential_id)
                
                params.append(credential_id)
                query = f"UPDATE credentials SET {', '.join(updates)} WHERE id = %s"
                
                await cursor.execute(query, params)
                await conn.commit()
                
                if cursor.rowcount == 0:
                    return None
                
                return await self.get_by_id(credential_id)
    
    async def delete(self, credential_id: int) -> bool:
        """Delete credential (soft delete by setting status to 'deleted')"""
        db = await get_db_connection()
        pool = await db.get_pool()
        
        async with pool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute(
                    "UPDATE credentials SET status = 'deleted' WHERE id = %s",
                    (credential_id,)
                )
                await conn.commit()
                return cursor.rowcount > 0

