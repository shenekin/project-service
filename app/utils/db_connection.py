"""
Database connection utility for MySQL with asyncmy
"""

from typing import Optional
import asyncmy
from app.settings import get_settings
from app.utils import log_connection, log_error, log_warning


class DatabaseConnection:
    """Database connection manager"""
    
    def __init__(self):
        """Initialize database connection manager"""
        self.settings = get_settings()
        self._pool: Optional[asyncmy.Pool] = None
    
    async def get_pool(self) -> asyncmy.Pool:
        """
        Get database connection pool
        
        Returns:
            Database connection pool
        """
        if self._pool is None:
            try:
                self._pool = await asyncmy.create_pool(
                    host=self.settings.mysql_host,
                    port=self.settings.mysql_port,
                    user=self.settings.mysql_user,
                    password=self.settings.mysql_password,
                    db=self.settings.mysql_database,
                    minsize=1,
                    maxsize=self.settings.mysql_pool_size,
                    autocommit=True
                )
                log_connection(
                    "MySQL connection pool created",
                    host=self.settings.mysql_host,
                    port=self.settings.mysql_port,
                    database=self.settings.mysql_database,
                )
            except Exception as exc:
                log_error("Failed to create MySQL connection pool", error=str(exc))
                raise
        return self._pool
    
    async def get_connection(self):
        """
        Get database connection from pool
        
        Returns:
            Database connection
        """
        pool = await self.get_pool()
        return await pool.acquire()
    
    async def close(self) -> None:
        """Close database connection pool"""
        if self._pool:
            self._pool.close()
            await self._pool.wait_closed()
            self._pool = None
        else:
            log_warning("Close called but no MySQL pool exists")
    
    async def execute_query(self, query: str, params: Optional[tuple] = None):
        """
        Execute a query
        
        Args:
            query: SQL query
            params: Query parameters
            
        Returns:
            Query result
        """
        pool = await self.get_pool()
        async with pool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute(query, params)
                return await cursor.fetchall()
    
    async def execute_update(self, query: str, params: Optional[tuple] = None) -> int:
        """
        Execute an update/insert/delete query
        
        Args:
            query: SQL query
            params: Query parameters
            
        Returns:
            Number of affected rows
        """
        pool = await self.get_pool()
        async with pool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute(query, params)
                await conn.commit()
                return cursor.rowcount


# Global database connection instance
_db_connection: Optional[DatabaseConnection] = None


async def get_db_connection() -> DatabaseConnection:
    """
    Get global database connection instance
    
    Returns:
        Database connection instance
    """
    global _db_connection
    if _db_connection is None:
        _db_connection = DatabaseConnection()
    return _db_connection


async def close_db_connection() -> None:
    """Close global database connection"""
    global _db_connection
    if _db_connection:
        await _db_connection.close()
        _db_connection = None

