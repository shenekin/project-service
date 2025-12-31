# Fix: 401 Unauthorized Error for Project Service

**Date:** 2024-12-30  
**Issue:** Getting `401 Unauthorized` errors when accessing project-service endpoints

## Problem Description

When making requests to project-service endpoints, the following error occurs:

```
INFO:     127.0.0.1:54864 - "POST /api/v1/projects HTTP/1.1" 401 Unauthorized
INFO:     127.0.0.1:54102 - "POST /api/v1/credentials HTTP/1.1" 401 Unauthorized
INFO:     127.0.0.1:43518 - "POST /api/v1/credentials HTTP/1.1" 401 Unauthorized
```

## Root Cause Analysis

The 401 error occurs because:

1. **Missing X-User-Id Header**: Project-service expects `X-User-Id` header in requests, which is set by the gateway after authentication
2. **Path Mismatch**: Gateway route configuration was set to `/projects` but project-service API uses `/api/v1/projects`
3. **Direct Access**: When accessing project-service directly (bypassing gateway), the `X-User-Id` header is not present
4. **Missing Authentication**: Requests without valid JWT token through gateway will not have user context

## Solution Overview

Two solutions were implemented:

1. **Updated Gateway Route Configuration**: Added proper routes for all project-service endpoints
2. **Development Mode Authentication Bypass**: Added optional authentication bypass for development/testing

## Solution 1: Gateway Route Configuration

### Changes Made

**File:** `gateway-service/config/routes.yaml`

Added comprehensive route configurations for all project-service endpoints:

```yaml
routes:
  # Project Service Routes
  - path: /api/v1/projects/**
    service: project-service
    methods: [GET, POST, PUT, DELETE, PATCH]
    auth_required: true
    rate_limit: 100
    timeout: 30
    strip_prefix: false
    
  - path: /api/v1/customers/**
    service: project-service
    methods: [GET, POST, PUT, DELETE, PATCH]
    auth_required: true
    rate_limit: 100
    timeout: 30
    strip_prefix: false
    
  - path: /api/v1/credentials/**
    service: project-service
    methods: [GET, POST, PUT, DELETE, PATCH]
    auth_required: true
    rate_limit: 100
    timeout: 30
    strip_prefix: false
    
  - path: /api/v1/vendors/**
    service: project-service
    methods: [GET]
    auth_required: false
    rate_limit: 100
    timeout: 30
    strip_prefix: false
    
  - path: /api/v1/permissions/**
    service: project-service
    methods: [GET, POST, PUT, DELETE]
    auth_required: true
    rate_limit: 100
    timeout: 30
    strip_prefix: false
    
  - path: /api/v1/audit/**
    service: project-service
    methods: [GET]
    auth_required: true
    rate_limit: 100
    timeout: 30
    strip_prefix: false
```

### How Gateway Authentication Works

1. **Client Request**: Client sends request with JWT token in `Authorization` header
2. **Gateway Validation**: Gateway validates JWT token and extracts user context
3. **Header Forwarding**: Gateway forwards `X-User-Id` header to backend services
4. **Backend Trust**: Backend services trust gateway and use `X-User-Id` for authorization

**Flow Diagram:**
```
Client → Gateway (validates JWT) → Project-Service (uses X-User-Id)
         [Sets X-User-Id header]
```

## Solution 2: Development Mode Authentication Bypass

### Changes Made

Modified `get_user_id()` function in all routers to support development mode:

**Files Modified:**
- `app/routers/credentials.py`
- `app/routers/customers.py`
- `app/routers/projects.py`
- `app/routers/permissions.py`

### Code Changes

**Before:**
```python
def get_user_id(request: Request) -> str:
    """Extract user ID from request headers"""
    user_id = request.headers.get("X-User-Id")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User ID not found in request headers"
        )
    return user_id
```

**After:**
```python
def get_user_id(request: Request) -> str:
    """
    Extract user ID from request headers (set by gateway)
    
    Note:
        In development mode (DEBUG=true), if X-User-Id is not present,
        it will use a default test user ID. In production, this will raise 401.
    """
    from app.settings import get_settings
    
    user_id = request.headers.get("X-User-Id")
    
    if not user_id:
        settings = get_settings()
        # In development mode, allow requests without X-User-Id header
        # Use a default test user ID for development/testing
        if settings.debug:
            user_id = request.headers.get("X-Test-User-Id", "test-user-dev")
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User ID not found in request headers. Please ensure requests go through gateway with valid authentication."
            )
    
    return user_id
```

### Behavior

- **Development Mode (`DEBUG=true`)**:
  - If `X-User-Id` is missing, uses default `test-user-dev`
  - Can override with `X-Test-User-Id` header
  - Allows direct access to project-service for testing

- **Production Mode (`DEBUG=false`)**:
  - Requires `X-User-Id` header (set by gateway)
  - Raises 401 if header is missing
  - Enforces proper authentication flow

## Usage Instructions

### Method 1: Through Gateway (Recommended for Production)

**Step 1: Login to get JWT token**
```bash
curl -X POST http://localhost:8001/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "your_username",
    "password": "your_password"
  }'
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**Step 2: Use token to access project-service**
```bash
# Create a project
curl -X POST http://localhost:8001/api/v1/projects \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "customer_id": 1,
    "name": "My Project",
    "description": "Project description"
  }'

# Create a credential
curl -X POST http://localhost:8001/api/v1/credentials \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "customer_id": 1,
    "project_id": 1,
    "vendor_id": 1,
    "access_key": "AK123456",
    "secret_key": "SK789012",
    "status": "active"
  }'

# List credentials
curl -X GET http://localhost:8001/api/v1/credentials \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### Method 2: Direct Access (Development Mode Only)

**Prerequisites:**
- Set `DEBUG=true` in `.env` or `.env.dev`
- Restart project-service

**Direct Access Examples:**
```bash
# Create a project (uses default test-user-dev)
curl -X POST http://localhost:8002/api/v1/projects \
  -H "Content-Type: application/json" \
  -d '{
    "customer_id": 1,
    "name": "Test Project",
    "description": "Test description"
  }'

# Create a project with custom test user ID
curl -X POST http://localhost:8002/api/v1/projects \
  -H "X-Test-User-Id: my-custom-user" \
  -H "Content-Type: application/json" \
  -d '{
    "customer_id": 1,
    "name": "Test Project",
    "description": "Test description"
  }'

# Create a credential
curl -X POST http://localhost:8002/api/v1/credentials \
  -H "Content-Type: application/json" \
  -d '{
    "customer_id": 1,
    "project_id": 1,
    "vendor_id": 1,
    "access_key": "AK123456",
    "secret_key": "SK789012",
    "status": "active"
  }'
```

## Verification Steps

### 1. Check Gateway Route Configuration

```bash
# Verify routes.yaml has been updated
cat gateway-service/config/routes.yaml | grep -A 5 "api/v1/projects"
```

### 2. Check Project-Service Debug Mode

```bash
# Check .env file
cat project-service/.env | grep DEBUG

# Should show: DEBUG=true for development
```

### 3. Test Direct Access (Development Mode)

```bash
# Test health endpoint (should work)
curl http://localhost:8002/health

# Test project creation (should work in DEBUG mode)
curl -X POST http://localhost:8002/api/v1/projects \
  -H "Content-Type: application/json" \
  -d '{"customer_id": 1, "name": "Test"}'
```

### 4. Test Through Gateway

```bash
# First, get a token
TOKEN=$(curl -s -X POST http://localhost:8001/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"user","password":"pass"}' | jq -r '.access_token')

# Then use token
curl -X POST http://localhost:8001/api/v1/projects \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"customer_id": 1, "name": "Test"}'
```

## Environment Configuration

### Development Environment (`.env.dev`)

```bash
ENVIRONMENT=dev
DEBUG=true  # Enables authentication bypass
HOST=0.0.0.0
PORT=8002
```

### Production Environment (`.env.prod`)

```bash
ENVIRONMENT=prod
DEBUG=false  # Enforces authentication
HOST=0.0.0.0
PORT=8002
```

## Important Notes

### Security Considerations

1. **Development Mode**: 
   - Only use `DEBUG=true` in development/testing environments
   - Never enable debug mode in production
   - Default test user `test-user-dev` should not have production permissions

2. **Production Mode**:
   - Always access through gateway with valid JWT token
   - Gateway validates authentication before forwarding requests
   - Backend services trust gateway's `X-User-Id` header

3. **Gateway Requirements**:
   - Gateway must be running and accessible
   - Gateway must have valid route configuration
   - Gateway must validate JWT tokens before forwarding

### Path Matching

- **Gateway Routes**: `/api/v1/projects/**` (with wildcard)
- **Project-Service Routes**: `/api/v1/projects` (exact match)
- Gateway strips prefix if `strip_prefix: true`, but we set it to `false`

### Service Discovery

Ensure project-service is registered with service discovery (NACOS):

```bash
# Check if service is registered
# Gateway should be able to discover project-service instances
```

## Troubleshooting

### Issue: Still Getting 401 After Fix

**Checklist:**
1. ✅ Gateway route configuration updated
2. ✅ Gateway service restarted
3. ✅ Project-service DEBUG mode enabled (for direct access)
4. ✅ Valid JWT token (for gateway access)
5. ✅ Correct API path (`/api/v1/projects` not `/projects`)

### Issue: Gateway Returns 404

**Possible Causes:**
- Route not configured in `routes.yaml`
- Service discovery not finding project-service
- Path mismatch between gateway route and service endpoint

**Solution:**
```bash
# Check gateway logs
tail -f gateway-service/logs/gateway.log

# Check service discovery
# Verify project-service is registered with NACOS
```

### Issue: Direct Access Works But Gateway Doesn't

**Possible Causes:**
- Gateway route configuration incorrect
- Service discovery issue
- Gateway not forwarding headers correctly

**Solution:**
1. Verify gateway route configuration
2. Check gateway logs for routing errors
3. Verify service discovery registration
4. Test gateway health endpoint

## API Endpoints Reference

### Project Service Endpoints

| Endpoint | Method | Auth Required | Description |
|----------|--------|---------------|-------------|
| `/api/v1/projects` | POST | Yes | Create project |
| `/api/v1/projects` | GET | Yes | List projects |
| `/api/v1/projects/{id}` | GET | Yes | Get project |
| `/api/v1/projects/{id}` | PUT | Yes | Update project |
| `/api/v1/projects/{id}` | DELETE | Yes | Delete project |
| `/api/v1/credentials` | POST | Yes | Create credential |
| `/api/v1/credentials` | GET | Yes | List credentials |
| `/api/v1/credentials/context/{id}` | GET | Yes | Get credential context |
| `/api/v1/credentials/{id}` | PUT | Yes | Update credential |
| `/api/v1/credentials/{id}` | DELETE | Yes | Delete credential |
| `/api/v1/customers` | POST | Yes | Create customer |
| `/api/v1/customers` | GET | No | List customers |
| `/api/v1/customers/{id}` | GET | No | Get customer |
| `/api/v1/vendors` | GET | No | List vendors |
| `/api/v1/vendors/{id}` | GET | No | Get vendor |
| `/api/v1/permissions` | POST | Yes | Create permission |
| `/api/v1/permissions/users/{user_id}` | GET | Yes | List user permissions |
| `/api/v1/audit/users/{user_id}` | GET | Yes | List audit logs |

## Summary

The 401 Unauthorized error has been fixed by:

1. ✅ **Updated Gateway Routes**: Added proper route configurations for all project-service endpoints
2. ✅ **Development Mode Support**: Added authentication bypass for development/testing
3. ✅ **Better Error Messages**: Improved error messages to guide users

**Next Steps:**
- Use gateway for production access (with JWT tokens)
- Use direct access for development (with DEBUG=true)
- Ensure gateway is properly configured and running
- Verify service discovery registration

## Related Files

- `gateway-service/config/routes.yaml` - Gateway route configuration
- `project-service/app/routers/credentials.py` - Credential router
- `project-service/app/routers/customers.py` - Customer router
- `project-service/app/routers/projects.py` - Project router
- `project-service/app/routers/permissions.py` - Permission router
- `project-service/app/settings.py` - Application settings
- `project-service/.env` - Default environment configuration
- `project-service/.env.dev` - Development environment
- `project-service/.env.prod` - Production environment

