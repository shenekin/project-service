"""
Data Access Object for Vendor entity
"""

from typing import Optional, List
from app.models.entities import Vendor
from app.utils.db_connection import get_db_connection


class VendorDAO:
    """Data Access Object for Vendor operations"""
    
    async def create(self, name: str, display_name: str, description: Optional[str] = None) -> Vendor:
        """Create a new vendor"""
        db = await get_db_connection()
        pool = await db.get_pool()
        
        async with pool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute(
                    "INSERT INTO vendors (name) VALUES (%s)",
                    (name,)
                )
                vendor_id = cursor.lastrowid
                await conn.commit()
                
                await cursor.execute(
                    "SELECT id, name, created_at, updated_at FROM vendors WHERE id = %s",
                    (vendor_id,)
                )
                row = await cursor.fetchone()
                
                return Vendor(
                    id=row[0],
                    name=row[1],
                    display_name=display_name or row[1],
                    description=None,
                    created_at=row[2],
                    updated_at=row[3]
                )
    
    async def get_by_id(self, vendor_id: int) -> Optional[Vendor]:
        """Get vendor by ID"""
        db = await get_db_connection()
        pool = await db.get_pool()
        
        async with pool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute(
                    "SELECT id, name, created_at, updated_at FROM vendors WHERE id = %s",
                    (vendor_id,)
                )
                row = await cursor.fetchone()
                
                if not row:
                    return None
                
                return Vendor(
                    id=row[0],
                    name=row[1],
                    display_name=row[1],
                    description=None,
                    created_at=row[2],
                    updated_at=row[3]
                )
    
    async def get_by_name(self, name: str) -> Optional[Vendor]:
        """Get vendor by name"""
        db = await get_db_connection()
        pool = await db.get_pool()
        
        async with pool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute(
                    "SELECT id, name, created_at, updated_at FROM vendors WHERE name = %s",
                    (name,)
                )
                row = await cursor.fetchone()
                
                if not row:
                    return None
                
                return Vendor(
                    id=row[0],
                    name=row[1],
                    display_name=row[1],
                    description=None,
                    created_at=row[2],
                    updated_at=row[3]
                )
    
    async def list_all(self) -> List[Vendor]:
        """List all vendors"""
        db = await get_db_connection()
        pool = await db.get_pool()
        
        async with pool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute(
                    "SELECT id, name, created_at, updated_at FROM vendors ORDER BY name"
                )
                rows = await cursor.fetchall()
                
                return [
                    Vendor(
                        id=row[0],
                        name=row[1],
                        display_name=row[1],
                        description=None,
                        created_at=row[2],
                        updated_at=row[3]
                    )
                    for row in rows
                ]
    
    async def update(self, vendor_id: int, display_name: Optional[str] = None,
                     description: Optional[str] = None) -> Optional[Vendor]:
        """Update vendor"""
        db = await get_db_connection()
        pool = await db.get_pool()
        
        async with pool.acquire() as conn:
            async with conn.cursor() as cursor:
                updates = []
                params = []
                
                if not updates:
                    return await self.get_by_id(vendor_id)
                
                params.append(vendor_id)
                query = f"UPDATE vendors SET {', '.join(updates)} WHERE id = %s"
                
                await cursor.execute(query, params)
                await conn.commit()
                
                if cursor.rowcount == 0:
                    return None
                
                return await self.get_by_id(vendor_id)

