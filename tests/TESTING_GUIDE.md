# Testing Guide for Project Service

This guide provides instructions for testing the credential management functionality in the project-service.

## Prerequisites

1. Install test dependencies:
```bash
pip install -r requirements.txt
```

2. Set up test environment variables:
```bash
export DEBUG=true
export MYSQL_HOST=localhost
export MYSQL_PORT=3306
export MYSQL_USER=root
export MYSQL_PASSWORD=your_password
export MYSQL_DATABASE=project_db_test
export VAULT_ENABLED=true
export VAULT_ADDR=http://localhost:8200
export VAULT_AUTH_METHOD=token
export VAULT_TOKEN=your_vault_token
```

## Running Tests

### Run all tests:
```bash
pytest
```

### Run specific test file:
```bash
pytest tests/test_credential_service.py
pytest tests/test_crypto_util.py
```

### Run with coverage:
```bash
pytest --cov=app --cov-report=html
```

## Manual Testing

### 1. Test Credential Creation

**Endpoint:** `POST /api/v1/credentials`

**Request:**
```bash
curl -X POST "http://localhost:8002/api/v1/credentials" \
  -H "Content-Type: application/json" \
  -H "X-User-Id: test-user" \
  -d '{
    "customer_id": 1,
    "project_id": 1,
    "vendor_id": 1,
    "access_key": "TEST_AK_12345",
    "secret_key": "TEST_SK_67890",
    "resource_user": "test_user",
    "labels": "test,development"
  }'
```

**Expected Response:**
- Status: 201 Created
- Response contains credential with masked AK (if listing)
- SK is stored encrypted in Vault

### 2. Test List Credentials (with Masked AK)

**Endpoint:** `GET /api/v1/credentials`

**Request:**
```bash
curl -X GET "http://localhost:8002/api/v1/credentials?page=1&page_size=20" \
  -H "X-User-Id: test-user"
```

**Expected Response:**
- Status: 200 OK
- Access keys are masked (only first 4 characters visible)
- Example: "TEST****" instead of "TEST_AK_12345"

### 3. Test Update Credential (AK and SK)

**Endpoint:** `PUT /api/v1/credentials/{credential_id}`

**Request:**
```bash
curl -X PUT "http://localhost:8002/api/v1/credentials/1" \
  -H "Content-Type: application/json" \
  -H "X-User-Id: test-user" \
  -d '{
    "access_key": "NEW_AK_12345",
    "secret_key": "NEW_SK_67890"
  }'
```

**Expected Response:**
- Status: 200 OK
- Credential updated with new AK
- SK encrypted and stored in Vault

### 4. Test Get Credential for API Call

**Endpoint:** `GET /api/v1/credentials/{credential_id}/api-credentials`

**Request:**
```bash
curl -X GET "http://localhost:8002/api/v1/credentials/1/api-credentials" \
  -H "X-User-Id: test-user"
```

**Expected Response:**
- Status: 200 OK
- Contains both access_key and secret_key (decrypted)
- Used for third-party API calls

### 5. Test Version Endpoint

**Endpoint:** `GET /api/v1/version`

**Request:**
```bash
curl -X GET "http://localhost:8002/api/v1/version"
```

**Expected Response:**
- Status: 200 OK
- Contains API version, service version, and build timestamp

## Test Scenarios

### Scenario 1: Create and List Credentials
1. Create a credential with AK and SK
2. List credentials and verify AK is masked
3. Verify SK is not exposed in list response

### Scenario 2: Update Credential
1. Create a credential
2. Update both AK and SK
3. Verify old vault path is deleted
4. Verify new vault path is created with encrypted SK

### Scenario 3: Retrieve for API Call
1. Create a credential
2. Retrieve credential for API call
3. Verify both AK and SK are returned (decrypted)
4. Verify audit log is created

### Scenario 4: Permission Checks
1. Create credential as user A
2. Try to access as user B (without permission)
3. Verify 403 Forbidden response

## Security Testing

1. **Encryption Test:**
   - Verify SK is encrypted before storing in Vault
   - Verify SK is decrypted when retrieved for API calls
   - Verify encryption key is not exposed

2. **Masking Test:**
   - Verify AK is masked in list responses
   - Verify only first 4 characters are visible
   - Verify full AK is available for API calls

3. **Vault Integration:**
   - Verify SK is stored in Vault, not database
   - Verify vault_path is stored in database
   - Verify old vault paths are cleaned up on update

## Troubleshooting

### Common Issues:

1. **Vault Connection Error:**
   - Ensure Vault is running and accessible
   - Check VAULT_ADDR and VAULT_TOKEN environment variables
   - Verify Vault authentication method

2. **Database Connection Error:**
   - Verify MySQL is running
   - Check database credentials
   - Ensure database exists

3. **Encryption Error:**
   - Check ENCRYPTION_KEY environment variable
   - Verify encryption key format (base64-encoded 32-byte key)

## Test Data Setup

Before running tests, ensure:
1. Database is initialized with `init_database.sql`
2. At least one customer exists
3. At least one project exists
4. At least one vendor exists
5. Vault is configured and accessible

