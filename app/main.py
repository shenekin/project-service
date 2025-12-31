"""
Main application entry point
"""

import uuid
from fastapi import Request
from fastapi.responses import JSONResponse
from app.bootstrap import create_app
from app.settings import get_settings

# Create application
app = create_app()


@app.middleware("http")
async def request_id_middleware(request: Request, call_next):
    """
    Add request ID to request and response
    
    Args:
        request: FastAPI request object
        call_next: Next middleware or route handler
        
    Returns:
        Response with request ID header
    """
    request_id = str(uuid.uuid4())
    request.state.request_id = request_id
    
    response = await call_next(request)
    response.headers["X-Request-Id"] = request_id
    
    return response


@app.get("/health")
async def health_check() -> dict:
    """
    Health check endpoint
    
    Returns:
        Health status
    """
    return {
        "status": "healthy",
        "service": "project-service"
    }


@app.get("/ready")
async def readiness_check() -> dict:
    """
    Readiness check endpoint
    
    Returns:
        Readiness status
    """
    try:
        # Check database connection
        from app.utils.db_connection import get_db_connection
        db = await get_db_connection()
        pool = await db.get_pool()
        
        # Test connection
        async with pool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute("SELECT 1")
                await cursor.fetchone()
        
        return {
            "status": "ready",
            "service": "project-service",
            "database": "connected"
        }
    except Exception as e:
        return JSONResponse(
            status_code=503,
            content={
                "status": "not_ready",
                "service": "project-service",
                "error": str(e)
            }
        )


@app.get("/metrics")
async def metrics() -> dict:
    """
    Prometheus metrics endpoint
    
    Returns:
        Metrics data
    """
    # In production, this would export Prometheus metrics
    return {
        "requests_total": 0,
        "requests_per_second": 0
    }


if __name__ == "__main__":
    """
    Direct execution of main.py
    """
    import uvicorn
    
    settings = get_settings()
    
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug
    )

