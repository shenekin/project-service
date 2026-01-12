# Functions and API Documentation

This document describes all functions and API endpoints in the project-service.

## Overview

The project-service provides credential management functionality for third-party cloud providers (HuaweiCloud, AWS, Aliyun, Azure). It handles Access Key (AK) and Secret Key (SK) management with encryption and secure storage.

## Key Features

- **Credential Management**: Create, read, update, and delete credentials (AK/SK)
- **Encryption**: Secret keys are encrypted before storing in Vault
- **Security**: Access keys are masked in list responses (only first 4 characters visible)
- **Vault Integration**: Secret keys are stored in HashiCorp Vault, only paths stored in database
- **Permission Control**: User-based access control for credential operations
- **Audit Logging**: All credential operations are logged for audit purposes
- **Version API**: API version information for software iteration tracking

## API Endpoints

### Credentials

#### 1. Create Credential
- **Endpoint**: `POST /api/v1/credentials`
- **Description**: Create a new credential with AK and SK
- **Request Body**:
  ```json
  {
    "customer_id": 1,
    "project_id": 1,
    "vendor_id": 1,
    "access_key": "AK_12345",
    "secret_key": "SK_67890",
    "resource_user": "optional_user",
    "labels": "optional,labels",
    "status": "active"
  }
  ```
- **Response**: Created credential (without SK)
- **Security**: SK is encrypted and stored in Vault, AK is stored in database

#### 2. List Credentials
- **Endpoint**: `GET /api/v1/credentials`
- **Description**: List credentials available to the user
- **Query Parameters**:
  - `customer_id` (optional): Filter by customer ID
  - `project_id` (optional): Filter by project ID
  - `page` (default: 1): Page number
  - `page_size` (default: 20): Page size
- **Response**: Paginated list of credentials with masked AK (first 4 characters visible)
- **Security**: Access keys are masked (e.g., "AK_1****" instead of "AK_12345")

#### 3. Get Credential Context
- **Endpoint**: `GET /api/v1/credentials/context/{credential_id}`
- **Description**: Get credential context for internal services (without SK)
- **Response**: Credential context with vault path (no SK exposed)
- **Use Case**: For internal service communication without exposing secrets

#### 4. Get Credential for API Call
- **Endpoint**: `GET /api/v1/credentials/{credential_id}/api-credentials`
- **Description**: Get full credential (AK and decrypted SK) for third-party API calls
- **Response**: 
  ```json
  {
    "credential_id": 1,
    "access_key": "AK_12345",
    "secret_key": "SK_67890",
    "vendor_id": 1,
    "customer_id": 1,
    "project_id": 1
  }
  ```
- **Security**: SK is decrypted from Vault, audit log is created
- **Use Case**: When frontend needs to call third-party cloud vendor APIs

#### 5. Update Credential
- **Endpoint**: `PUT /api/v1/credentials/{credential_id}`
- **Description**: Update credential (supports AK and SK updates)
- **Request Body**:
  ```json
  {
    "access_key": "NEW_AK_12345",
    "secret_key": "NEW_SK_67890",
    "resource_user": "updated_user",
    "labels": "updated,labels",
    "status": "active"
  }
  ```
- **Response**: Updated credential (without SK)
- **Security**: 
  - If SK is updated, old vault path is deleted and new encrypted SK is stored
  - If AK is updated, new vault path is created
  - All updates are logged in audit trail

#### 6. Delete Credential
- **Endpoint**: `DELETE /api/v1/credentials/{credential_id}`
- **Description**: Soft delete credential (sets status to 'deleted')
- **Response**: 204 No Content
- **Security**: Soft delete preserves data for audit purposes

### Version

#### 1. Get Version
- **Endpoint**: `GET /api/v1/version`
- **Description**: Get API version information for software iteration tracking
- **Response**:
  ```json
  {
    "api_version": "v1",
    "service_version": "1.0.0",
    "service_name": "project-service",
    "build_timestamp": "2024-01-01T00:00:00",
    "environment": "default"
  }
  ```
- **Use Case**: For version tracking and software iteration management

### Customers

#### 1. Create Customer
- **Endpoint**: `POST /api/v1/customers`
- **Description**: Create a new customer

#### 2. List Customers
- **Endpoint**: `GET /api/v1/customers`
- **Description**: List all customers

#### 3. Get Customer
- **Endpoint**: `GET /api/v1/customers/{customer_id}`
- **Description**: Get customer by ID

#### 4. Update Customer
- **Endpoint**: `PUT /api/v1/customers/{customer_id}`
- **Description**: Update customer information

#### 5. Delete Customer
- **Endpoint**: `DELETE /api/v1/customers/{customer_id}`
- **Description**: Delete customer

### Projects

#### 1. Create Project
- **Endpoint**: `POST /api/v1/projects`
- **Description**: Create a new project

#### 2. List Projects
- **Endpoint**: `GET /api/v1/projects?customer_id={id}`
- **Description**: List projects (optionally filtered by customer)

#### 3. Get Project
- **Endpoint**: `GET /api/v1/projects/{project_id}`
- **Description**: Get project by ID

#### 4. Update Project
- **Endpoint**: `PUT /api/v1/projects/{project_id}`
- **Description**: Update project information

#### 5. Delete Project
- **Endpoint**: `DELETE /api/v1/projects/{project_id}`
- **Description**: Delete project

### Vendors

#### 1. List Vendors
- **Endpoint**: `GET /api/v1/vendors`
- **Description**: List all cloud vendors

#### 2. Get Vendor
- **Endpoint**: `GET /api/v1/vendors/{vendor_id}`
- **Description**: Get vendor by ID

### Permissions

#### 1. Create Permission
- **Endpoint**: `POST /api/v1/permissions`
- **Description**: Create user permission

#### 2. List User Permissions
- **Endpoint**: `GET /api/v1/permissions/users/{user_id}`
- **Description**: List permissions for a user

#### 3. Update Permission
- **Endpoint**: `PUT /api/v1/permissions/{permission_id}`
- **Description**: Update user permission

#### 4. Delete Permission
- **Endpoint**: `DELETE /api/v1/permissions/{permission_id}`
- **Description**: Delete user permission

### Audit

#### 1. List Audit Logs by User
- **Endpoint**: `GET /api/v1/audit/users/{user_id}`
- **Description**: List audit logs for a user

#### 2. List Audit Logs by Credential
- **Endpoint**: `GET /api/v1/audit/credentials/{credential_id}`
- **Description**: List audit logs for a credential

## Service Layer Functions

### CredentialService

#### `create_credential(credential_data, user_id, ip_address, user_agent)`
- **Description**: Create a new credential with encrypted SK storage
- **Process**:
  1. Validate customer, project, and vendor exist
  2. Encrypt secret key
  3. Store encrypted SK in Vault
  4. Store credential metadata (AK and vault path) in database
  5. Create audit log

#### `list_credentials(user_id, customer_id, project_id, page, page_size)`
- **Description**: List credentials with masked access keys
- **Process**:
  1. Get credentials based on user permissions
  2. Mask access keys (show only first 4 characters)
  3. Return paginated results

#### `get_credential_context(credential_id, user_id, ip_address, user_agent)`
- **Description**: Get credential context without exposing SK
- **Process**:
  1. Validate credential exists and is active
  2. Check user permissions
  3. Return context with vault path (no SK)

#### `get_credential_for_api_call(credential_id, user_id, ip_address, user_agent)`
- **Description**: Get full credential (AK and decrypted SK) for API calls
- **Process**:
  1. Validate credential exists and is active
  2. Check user permissions
  3. Retrieve encrypted SK from Vault
  4. Decrypt SK
  5. Return both AK and SK
  6. Create audit log

#### `update_credential(credential_id, credential_data, user_id, ip_address, user_agent)`
- **Description**: Update credential (supports AK and SK updates)
- **Process**:
  1. Validate credential exists
  2. Check user permissions
  3. If SK is updated:
     - Encrypt new SK
     - Store in Vault at new path
     - Delete old vault path if AK changed
  4. Update credential in database
  5. Create audit log

#### `delete_credential(credential_id, user_id, ip_address, user_agent)`
- **Description**: Soft delete credential
- **Process**:
  1. Validate credential exists
  2. Check user permissions
  3. Set status to 'deleted'
  4. Create audit log

## Utility Functions

### CryptoUtil

#### `encrypt(plaintext)`
- **Description**: Encrypt plaintext string using Fernet encryption
- **Returns**: Base64-encoded encrypted string

#### `decrypt(ciphertext)`
- **Description**: Decrypt encrypted string
- **Returns**: Decrypted plaintext string

#### `mask_access_key(access_key, visible_chars=4)`
- **Description**: Mask access key to show only first N characters
- **Returns**: Masked access key (e.g., "AK_1****")

### VaultUtil

#### `write_secret(path, data)`
- **Description**: Write encrypted secret to Vault
- **Process**: Stores data at specified path in Vault KV v2 engine

#### `read_secret(path)`
- **Description**: Read secret from Vault
- **Returns**: Secret data dictionary

#### `delete_secret(path)`
- **Description**: Delete secret from Vault
- **Process**: Deletes metadata and all versions

## Data Access Layer Functions

### CredentialDAO

#### `create(customer_id, project_id, vendor_id, access_key, vault_path, ...)`
- **Description**: Create credential record in database
- **Returns**: Credential entity

#### `get_by_id(credential_id)`
- **Description**: Get credential by ID
- **Returns**: Credential entity or None

#### `list_by_user_permissions(user_id, customer_id, project_id, skip, limit)`
- **Description**: List credentials filtered by user permissions
- **Returns**: List of credential dictionaries with related entity names

#### `update(credential_id, access_key, vault_path, ...)`
- **Description**: Update credential fields
- **Returns**: Updated credential entity or None

#### `delete(credential_id)`
- **Description**: Soft delete credential (set status to 'deleted')
- **Returns**: True if successful

## Security Features

1. **Encryption**: All secret keys are encrypted using Fernet (symmetric encryption) before storing in Vault
2. **Masking**: Access keys are masked in list responses (only first 4 characters visible)
3. **Vault Storage**: Secret keys are never stored in database, only vault paths
4. **Permission Control**: All operations check user permissions before execution
5. **Audit Logging**: All credential operations are logged with user ID, IP address, and timestamp
6. **Soft Delete**: Credentials are soft-deleted to preserve audit trail

## Database Schema

### credentials Table
- `id`: Primary key
- `customer_id`: Foreign key to customers
- `project_id`: Foreign key to projects
- `vendor_id`: Foreign key to vendors
- `access_key`: Access key (stored in database)
- `vault_path`: Path to secret in Vault (stored in database)
- `resource_user`: Optional resource user
- `labels`: Optional labels/tags
- `status`: Status (active, disabled, deleted)
- `created_at`: Creation timestamp
- `updated_at`: Update timestamp

## Environment Variables

- `ENCRYPTION_KEY`: Base64-encoded 32-byte encryption key (optional, will generate if not provided)
- `ENCRYPTION_SALT`: Salt for key derivation (optional)
- `ENCRYPTION_PASSWORD`: Password for key derivation (optional, for development only)
- `VAULT_ENABLED`: Enable Vault integration (true/false)
- `VAULT_ADDR`: Vault server address
- `VAULT_AUTH_METHOD`: Authentication method (approle/token)
- `VAULT_TOKEN`: Vault token (for token auth)
- `VAULT_ROLE_ID`: Vault role ID (for approle auth)
- `VAULT_SECRET_ID`: Vault secret ID (for approle auth)
- `VAULT_CREDENTIAL_PATH`: Base path for credentials in Vault

## Version History

### Version 1.0.0
- Initial implementation of credential management
- AK/SK creation, update, and deletion
- Encryption support for SK
- Masking support for AK in list responses
- Vault integration for secure SK storage
- Version API endpoint for software iteration tracking

