"""
Data Access Object for Project entity
"""

from typing import Optional, List
from app.models.entities import Project
from app.utils.db_connection import get_db_connection


class ProjectDAO:
    """Data Access Object for Project operations"""
    
    async def create(self, customer_id: int, name: str, description: Optional[str] = None) -> Project:
        """
        Create a new project
        
        Args:
            customer_id: Customer ID
            name: Project name
            description: Project description
            
        Returns:
            Created project entity
            
        Raises:
            ValueError: If project with same name already exists for customer
        """
        db = await get_db_connection()
        pool = await db.get_pool()
        
        async with pool.acquire() as conn:
            async with conn.cursor() as cursor:
                # Check if project with same name exists for customer
                await cursor.execute(
                    "SELECT id FROM projects WHERE customer_id = %s AND name = %s",
                    (customer_id, name)
                )
                existing = await cursor.fetchone()
                if existing:
                    raise ValueError(f"Project with name '{name}' already exists for customer {customer_id}")
                
                # Insert new project
                await cursor.execute(
                    "INSERT INTO projects (customer_id, name, description) VALUES (%s, %s, %s)",
                    (customer_id, name, description)
                )
                project_id = cursor.lastrowid
                await conn.commit()
                
                # Fetch created project
                await cursor.execute(
                    "SELECT id, customer_id, name, description, created_at, updated_at FROM projects WHERE id = %s",
                    (project_id,)
                )
                row = await cursor.fetchone()
                
                return Project(
                    id=row[0],
                    customer_id=row[1],
                    name=row[2],
                    description=row[3],
                    created_at=row[4],
                    updated_at=row[5]
                )
    
    async def get_by_id(self, project_id: int) -> Optional[Project]:
        """Get project by ID"""
        db = await get_db_connection()
        pool = await db.get_pool()
        
        async with pool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute(
                    "SELECT id, customer_id, name, description, created_at, updated_at FROM projects WHERE id = %s",
                    (project_id,)
                )
                row = await cursor.fetchone()
                
                if not row:
                    return None
                
                return Project(
                    id=row[0],
                    customer_id=row[1],
                    name=row[2],
                    description=row[3],
                    created_at=row[4],
                    updated_at=row[5]
                )
    
    async def list_by_customer(self, customer_id: int, skip: int = 0, limit: int = 100) -> List[Project]:
        """List projects by customer ID"""
        db = await get_db_connection()
        pool = await db.get_pool()
        
        async with pool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute(
                    """SELECT id, customer_id, name, description, created_at, updated_at
                       FROM projects WHERE customer_id = %s ORDER BY name LIMIT %s OFFSET %s""",
                    (customer_id, limit, skip)
                )
                rows = await cursor.fetchall()
                
                return [
                    Project(
                        id=row[0],
                        customer_id=row[1],
                        name=row[2],
                        description=row[3],
                        created_at=row[4],
                        updated_at=row[5]
                    )
                    for row in rows
                ]
    
    async def update(self, project_id: int, name: Optional[str] = None,
                     description: Optional[str] = None) -> Optional[Project]:
        """Update project"""
        db = await get_db_connection()
        pool = await db.get_pool()
        
        async with pool.acquire() as conn:
            async with conn.cursor() as cursor:
                updates = []
                params = []
                
                if name is not None:
                    updates.append("name = %s")
                    params.append(name)
                if description is not None:
                    updates.append("description = %s")
                    params.append(description)
                
                if not updates:
                    return await self.get_by_id(project_id)
                
                params.append(project_id)
                query = f"UPDATE projects SET {', '.join(updates)} WHERE id = %s"
                
                await cursor.execute(query, params)
                await conn.commit()
                
                if cursor.rowcount == 0:
                    return None
                
                return await self.get_by_id(project_id)
    
    async def delete(self, project_id: int) -> bool:
        """Delete project"""
        db = await get_db_connection()
        pool = await db.get_pool()
        
        async with pool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute("DELETE FROM projects WHERE id = %s", (project_id,))
                await conn.commit()
                return cursor.rowcount > 0

