# Project Service

Project Service for Cloud Resource Management System - Credential Management Service

## Overview

This service provides credential management functionality for third-party cloud providers (HuaweiCloud, AWS, Aliyun, Azure). It handles:

- Credential Management (AK/SK Registration & Storage)
- Credential Selection / Context Retrieval
- Permission & Access Control
- Audit & Logging
- Credential Status Management
- Vendor / Provider Abstraction
- User Interface / Internal UX
- Reporting & Monitoring

## Technology Stack

- **Language**: Python 3.10
- **Framework**: FastAPI 0.104
- **Database**: MySQL 8.0 + asyncmy
- **Cache**: Redis
- **Secret Management**: HashiCorp Vault
- **Service Discovery**: NACOS 2.3.2
- **Monitoring**: Prometheus + Grafana

## Project Structure

```
project-service/
├── app/
│   ├── __init__.py
│   ├── main.py              # Main application entry point
│   ├── bootstrap.py         # Application bootstrap
│   ├── settings.py          # Configuration settings
│   ├── models/              # Data models
│   │   ├── entities.py      # Entity models
│   │   └── schemas.py       # Pydantic schemas
│   ├── dao/                 # Data Access Object layer
│   │   ├── customer_dao.py
│   │   ├── project_dao.py
│   │   ├── vendor_dao.py
│   │   ├── credential_dao.py
│   │   ├── audit_log_dao.py
│   │   └── user_permission_dao.py
│   ├── services/            # Service layer (business logic)
│   │   ├── credential_service.py
│   │   ├── customer_service.py
│   │   ├── project_service.py
│   │   ├── vendor_service.py
│   │   ├── permission_service.py
│   │   └── audit_service.py
│   ├── routers/             # API layer (FastAPI routers)
│   │   ├── credentials.py
│   │   ├── customers.py
│   │   ├── projects.py
│   │   ├── vendors.py
│   │   ├── permissions.py
│   │   └── audit.py
│   └── utils/               # Utility modules
│       ├── db_connection.py
│       ├── vault_util.py
│       └── env_loader.py
├── scripts/
│   └── database/
│       └── init_database.sql
├── .env                     # Default environment configuration
├── .env.dev                 # Development environment
├── .env.prod                # Production environment
├── requirements.txt          # Python dependencies
├── run.py                   # Application entry point
└── README.md                # This file
```

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Initialize database:
```bash
mysql -u root -p < scripts/database/init_database.sql
```

3. Configure environment variables:
- Copy `.env` and modify as needed
- Or use `.env.dev` for development
- Or use `.env.prod` for production

## Running the Service

### Development Mode
```bash
python run.py --env dev --reload
```

### Production Mode
```bash
python run.py --env prod
```

### Direct Execution
```bash
python -m app.main
```

## API Endpoints

### Credentials
- `POST /api/v1/credentials` - Create credential (AK and SK)
- `GET /api/v1/credentials` - List credentials (with masked AK)
- `GET /api/v1/credentials/context/{credential_id}` - Get credential context (without SK)
- `GET /api/v1/credentials/{credential_id}/api-credentials` - Get credential for API calls (with decrypted SK)
- `PUT /api/v1/credentials/{credential_id}` - Update credential (supports AK and SK updates)
- `DELETE /api/v1/credentials/{credential_id}` - Delete credential

### Customers

Customer management functions allow you to create, retrieve, update, and delete customers. Each customer is identified by a unique name.

#### Customer Functions

**Create Customer**
- `POST /api/v1/customers` - Create a new customer
  - **Request Body**: 
    ```json
    {
      "name": "Customer Name",
      "description": "Optional customer description",
      "contact_email": "optional@email.com",
      "contact_phone": "+1234567890"
    }
    ```
  - **Required Fields**: `name` (must be unique, max 255 characters)
  - **Optional Fields**: `description` (max 1000 characters), `contact_email` (max 255 characters), `contact_phone` (max 50 characters)
  - **Response**: Customer object with `id`, `name`, `description`, `contact_email`, `contact_phone`, `created_at`, `updated_at`
  - **Note**: Customer name is required and must be unique. All other fields are optional.
  - **Empty Value Handling**: Empty strings (`""`) and the literal string `"string"` are automatically converted to `null` (NULL in database). Optional fields can be omitted from the request body entirely.

**List Customers**
- `GET /api/v1/customers?page=1&page_size=20` - List all customers with pagination
  - **Query Parameters**: 
    - `page` (optional, default: 1) - Page number
    - `page_size` (optional, default: 20) - Number of items per page
  - **Response**: Paginated list with `total`, `page`, `page_size`, `total_pages`, `items`
  - Each item includes: `id`, `name`, `description`, `contact_email`, `contact_phone`, `created_at`, `updated_at`

**Get Customer**
- `GET /api/v1/customers/{customer_id}` - Get customer by ID
  - **Path Parameter**: `customer_id` - Customer ID
  - **Response**: Customer object with `id`, `name`, `description`, `contact_email`, `contact_phone`, `created_at`, `updated_at`
  - **Error**: Returns 404 if customer not found

**Update Customer**
- `PUT /api/v1/customers/{customer_id}` - Update customer information
  - **Path Parameter**: `customer_id` - Customer ID
  - **Request Body**: 
    ```json
    {
      "name": "Updated Customer Name",
      "description": "Updated description",
      "contact_email": "updated@email.com",
      "contact_phone": "+9876543210"
    }
    ```
  - **All Fields Optional**: You can update any combination of fields (name, description, contact_email, contact_phone)
  - **Response**: Updated customer object with all fields
  - **Note**: Only provided fields will be updated. Omitted fields remain unchanged.
  - **Empty Value Handling**: Empty strings (`""`) and the literal string `"string"` are automatically converted to `null` (NULL in database). To leave a field unchanged, simply omit it from the request body.

**Delete Customer**
- `DELETE /api/v1/customers/{customer_id}` - Delete customer
  - **Path Parameter**: `customer_id` - Customer ID
  - **Response**: 204 No Content
  - **Warning**: Deleting a customer will cascade delete all associated projects and credentials. This action cannot be undone.

#### Customer Data Model

The customer entity contains the following fields:
- `id` (int) - Unique customer identifier (auto-generated, primary key)
- `name` (string) - Customer name (**required**, unique, max 255 characters)
- `description` (string, optional, nullable) - Customer description (max 1000 characters). Empty strings are stored as NULL.
- `contact_email` (string, optional, nullable) - Contact email address (max 255 characters). Empty strings are stored as NULL.
- `contact_phone` (string, optional, nullable) - Contact phone number (max 50 characters). Empty strings are stored as NULL.
- `created_at` (datetime) - Timestamp when customer was created (auto-generated)
- `updated_at` (datetime) - Timestamp when customer was last updated (auto-updated)

**Important Notes:**
- Optional fields (`description`, `contact_email`, `contact_phone`) will be stored as `NULL` in the database if:
  - The field is omitted from the request
  - The field is provided as an empty string (`""`)
  - The field is provided as the literal string `"string"` (treated as placeholder)
- This ensures clean data storage and prevents placeholder values from being stored in the database.

#### Customer API Endpoints Summary
- `POST /api/v1/customers` - Create customer (name required, other fields optional)
- `GET /api/v1/customers` - List customers with pagination
- `GET /api/v1/customers/{customer_id}` - Get customer by ID
- `PUT /api/v1/customers/{customer_id}` - Update customer (all fields optional)
- `DELETE /api/v1/customers/{customer_id}` - Delete customer

#### Customer Function Examples

**Example 1: Create customer with only name (minimum required)**
```bash
curl -X POST "http://localhost:8000/api/v1/customers" \
  -H "Content-Type: application/json" \
  -H "X-User-Id: user123" \
  -d '{"name": "Acme Corporation"}'
```

**Example 2: Create customer with all fields**
```bash
curl -X POST "http://localhost:8000/api/v1/customers" \
  -H "Content-Type: application/json" \
  -H "X-User-Id: user123" \
  -d '{
    "name": "Tech Solutions Inc",
    "description": "Leading technology solutions provider",
    "contact_email": "contact@techsolutions.com",
    "contact_phone": "+1-555-0123"
  }'
```

**Example 3: Create customer with empty optional fields (will be stored as NULL)**
```bash
curl -X POST "http://localhost:8000/api/v1/customers" \
  -H "Content-Type: application/json" \
  -H "X-User-Id: user123" \
  -d '{
    "name": "Simple Corp",
    "description": "",
    "contact_email": "",
    "contact_phone": ""
  }'
```
Note: Empty strings are automatically converted to NULL in the database.

**Example 4: Update customer description only**
```bash
curl -X PUT "http://localhost:8000/api/v1/customers/1" \
  -H "Content-Type: application/json" \
  -H "X-User-Id: user123" \
  -d '{"description": "Updated company description"}'
```

**Example 5: List customers with pagination**
```bash
curl -X GET "http://localhost:8000/api/v1/customers?page=1&page_size=10" \
  -H "X-User-Id: user123"
```

### Projects
- `POST /api/v1/projects` - Create project
- `GET /api/v1/projects?customer_id={id}` - List projects
- `GET /api/v1/projects/{project_id}` - Get project
- `PUT /api/v1/projects/{project_id}` - Update project
- `DELETE /api/v1/projects/{project_id}` - Delete project

### Vendors
- `GET /api/v1/vendors` - List vendors
- `GET /api/v1/vendors/{vendor_id}` - Get vendor

### Permissions
- `POST /api/v1/permissions` - Create permission
- `GET /api/v1/permissions/users/{user_id}` - List user permissions
- `PUT /api/v1/permissions/{permission_id}` - Update permission
- `DELETE /api/v1/permissions/{permission_id}` - Delete permission

### Audit
- `GET /api/v1/audit/users/{user_id}` - List audit logs by user
- `GET /api/v1/audit/credentials/{credential_id}` - List audit logs by credential

### Version
- `GET /api/v1/version` - Get API version information for software iteration

## Health Checks

- `GET /health` - Health check endpoint
- `GET /ready` - Readiness check endpoint
- `GET /metrics` - Prometheus metrics endpoint

## Environment Variables

All configuration is done through environment variables. See `.env`, `.env.dev`, and `.env.prod` for examples.

## Database Schema

The service uses MySQL with the following main tables:
- `customers` - Customer information
- `projects` - Project information
- `vendors` - Vendor/provider information
- `credentials` - Credential metadata (SK stored in Vault)
- `user_permissions` - User access permissions
- `audit_logs` - Audit trail

## Security

- Secret Keys (SK) are encrypted and stored in HashiCorp Vault, never in the database
- Access Keys (AK) are stored in the database for reference
- Access Keys are masked in list responses (only first 4 characters visible)
- All credential operations are logged in audit_logs
- User permissions are checked before credential access
- Encryption uses Fernet (symmetric encryption) for SK protection

## Testing

Run tests with:
```bash
pytest
```

## Code Standards

- Follows PEP 8 style guide
- Uses type hints
- All functions and classes have docstrings
- English comments only (no Chinese)
- Layered architecture: API -> Service -> DAO -> Database

## Dependencies

See `requirements.txt` for full list of dependencies.

## License

Internal use only.

