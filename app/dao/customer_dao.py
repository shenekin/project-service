"""
Data Access Object for Customer entity
"""

from typing import Optional, List
from datetime import datetime
from app.models.entities import Customer
from app.utils.db_connection import get_db_connection


class CustomerDAO:
    """Data Access Object for Customer operations"""
    
    async def create(self, name: str, description: Optional[str] = None,
                     contact_email: Optional[str] = None,
                     contact_phone: Optional[str] = None) -> Customer:
        """
        Create a new customer
        
        Args:
            name: Customer name
            description: Customer description
            contact_email: Contact email
            contact_phone: Contact phone
            
        Returns:
            Created customer entity
            
        Raises:
            ValueError: If customer with same name already exists
        """
        db = await get_db_connection()
        pool = await db.get_pool()
        
        async with pool.acquire() as conn:
            async with conn.cursor() as cursor:
                # Check if customer with same name exists
                await cursor.execute(
                    "SELECT id FROM customers WHERE name = %s",
                    (name,)
                )
                existing = await cursor.fetchone()
                if existing:
                    raise ValueError(f"Customer with name '{name}' already exists")
                
                # Insert new customer
                await cursor.execute(
                    """INSERT INTO customers (name, description, contact_email, contact_phone)
                       VALUES (%s, %s, %s, %s)""",
                    (name, description, contact_email, contact_phone)
                )
                customer_id = cursor.lastrowid
                await conn.commit()
                
                # Fetch created customer
                await cursor.execute(
                    "SELECT id, name, description, contact_email, contact_phone, created_at, updated_at FROM customers WHERE id = %s",
                    (customer_id,)
                )
                row = await cursor.fetchone()
                
                return Customer(
                    id=row[0],
                    name=row[1],
                    description=row[2],
                    contact_email=row[3],
                    contact_phone=row[4],
                    created_at=row[5],
                    updated_at=row[6]
                )
    
    async def get_by_id(self, customer_id: int) -> Optional[Customer]:
        """
        Get customer by ID
        
        Args:
            customer_id: Customer ID
            
        Returns:
            Customer entity or None if not found
        """
        db = await get_db_connection()
        pool = await db.get_pool()
        
        async with pool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute(
                    "SELECT id, name, description, contact_email, contact_phone, created_at, updated_at FROM customers WHERE id = %s",
                    (customer_id,)
                )
                row = await cursor.fetchone()
                
                if not row:
                    return None
                
                return Customer(
                    id=row[0],
                    name=row[1],
                    description=row[2],
                    contact_email=row[3],
                    contact_phone=row[4],
                    created_at=row[5],
                    updated_at=row[6]
                )
    
    async def get_by_name(self, name: str) -> Optional[Customer]:
        """
        Get customer by name
        
        Args:
            name: Customer name
            
        Returns:
            Customer entity or None if not found
        """
        db = await get_db_connection()
        pool = await db.get_pool()
        
        async with pool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute(
                    "SELECT id, name, description, contact_email, contact_phone, created_at, updated_at FROM customers WHERE name = %s",
                    (name,)
                )
                row = await cursor.fetchone()
                
                if not row:
                    return None
                
                return Customer(
                    id=row[0],
                    name=row[1],
                    description=row[2],
                    contact_email=row[3],
                    contact_phone=row[4],
                    created_at=row[5],
                    updated_at=row[6]
                )
    
    async def list_all(self, skip: int = 0, limit: int = 100) -> List[Customer]:
        """
        List all customers with pagination
        
        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of customer entities
        """
        db = await get_db_connection()
        pool = await db.get_pool()
        
        async with pool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute(
                    """SELECT id, name, description, contact_email, contact_phone, created_at, updated_at
                       FROM customers ORDER BY name LIMIT %s OFFSET %s""",
                    (limit, skip)
                )
                rows = await cursor.fetchall()
                
                return [
                    Customer(
                        id=row[0],
                        name=row[1],
                        description=row[2],
                        contact_email=row[3],
                        contact_phone=row[4],
                        created_at=row[5],
                        updated_at=row[6]
                    )
                    for row in rows
                ]
    
    async def update(self, customer_id: int, name: Optional[str] = None,
                     description: Optional[str] = None,
                     contact_email: Optional[str] = None,
                     contact_phone: Optional[str] = None) -> Optional[Customer]:
        """
        Update customer
        
        Args:
            customer_id: Customer ID
            name: Customer name
            description: Customer description
            contact_email: Contact email
            contact_phone: Contact phone
            
        Returns:
            Updated customer entity or None if not found
        """
        db = await get_db_connection()
        pool = await db.get_pool()
        
        async with pool.acquire() as conn:
            async with conn.cursor() as cursor:
                # Build update query dynamically
                updates = []
                params = []
                
                if name is not None:
                    updates.append("name = %s")
                    params.append(name)
                if description is not None:
                    updates.append("description = %s")
                    params.append(description)
                if contact_email is not None:
                    updates.append("contact_email = %s")
                    params.append(contact_email)
                if contact_phone is not None:
                    updates.append("contact_phone = %s")
                    params.append(contact_phone)
                
                if not updates:
                    # No updates, just return existing customer
                    return await self.get_by_id(customer_id)
                
                params.append(customer_id)
                query = f"UPDATE customers SET {', '.join(updates)} WHERE id = %s"
                
                await cursor.execute(query, params)
                await conn.commit()
                
                if cursor.rowcount == 0:
                    return None
                
                return await self.get_by_id(customer_id)
    
    async def delete(self, customer_id: int) -> bool:
        """
        Delete customer
        
        Args:
            customer_id: Customer ID
            
        Returns:
            True if deleted, False if not found
        """
        db = await get_db_connection()
        pool = await db.get_pool()
        
        async with pool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute("DELETE FROM customers WHERE id = %s", (customer_id,))
                await conn.commit()
                return cursor.rowcount > 0
    
    async def count(self) -> int:
        """
        Get total count of customers
        
        Returns:
            Total count
        """
        db = await get_db_connection()
        pool = await db.get_pool()
        
        async with pool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute("SELECT COUNT(*) FROM customers")
                row = await cursor.fetchone()
                return row[0] if row else 0

