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
- `POST /api/v1/customers` - Create customer
- `GET /api/v1/customers` - List customers
- `GET /api/v1/customers/{customer_id}` - Get customer
- `PUT /api/v1/customers/{customer_id}` - Update customer
- `DELETE /api/v1/customers/{customer_id}` - Delete customer

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

