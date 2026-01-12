# Database Schema Changes

## Overview

The database schema has been updated to match the simplified design document. This is a **breaking change** that requires code updates.

## Changes Made

### 1. customers Table
**Before:**
- `id`, `name`, `description`, `contact_email`, `contact_phone`, `created_at`, `updated_at`

**After:**
- `id`, `name`, `created_at`, `updated_at`

**Removed Fields:**
- `description` (TEXT)
- `contact_email` (VARCHAR(255))
- `contact_phone` (VARCHAR(50))

### 2. vendors Table
**Before:**
- `id`, `name` (VARCHAR(100)), `display_name`, `description`, `created_at`, `updated_at`

**After:**
- `id`, `name` (VARCHAR(255)), `created_at`, `updated_at`

**Removed Fields:**
- `display_name` (VARCHAR(255))
- `description` (TEXT)

**Changed:**
- `name` field length increased from VARCHAR(100) to VARCHAR(255)

### 3. credentials Table
**Before:**
- `id`, `customer_id`, `project_id`, `vendor_id`, `access_key`, `vault_path`, `resource_user`, `labels`, `status`, `created_at`, `updated_at`

**After:**
- `id`, `customer_id`, `vendor_id`, `access_key`, `vault_path`, `resource_user`, `labels`, `status`, `created_at`, `updated_at`

**Removed Fields:**
- `project_id` (INT NOT NULL) - **BREAKING CHANGE**

**Fixed:**
- Column name typo: `abels` → `labels` (if it existed)

**Removed Indexes:**
- `idx_project_id`
- Foreign key constraint on `project_id`

## Migration Instructions

### For New Installations
Use the updated `init_database.sql` script directly.

### For Existing Databases
1. **Backup your database first!**
2. Review the migration script: `migrate_to_simplified_schema.sql`
3. Run the migration script:
   ```bash
   mysql -u root -p project_db < scripts/database/migrate_to_simplified_schema.sql
   ```

### Important Notes

1. **Data Loss Warning:**
   - Removing `project_id` from credentials will lose project association data
   - Removing `description`, `contact_email`, `contact_phone` from customers will lose this data
   - Removing `display_name` and `description` from vendors will lose this data
   
2. **Code Updates Required:**
   - All code that references `project_id` in credentials needs to be updated
   - All code that uses `display_name` or `description` from vendors needs to be updated
   - All code that uses customer `description`, `contact_email`, or `contact_phone` needs to be updated

3. **Breaking Changes:**
   - Credential creation/update no longer requires `project_id`
   - Credential queries that filter by `project_id` will fail
   - Vendor display names will no longer be available
   - Customer contact information will no longer be available

## Code Impact

### Files That Need Updates

1. **app/models/entities.py**
   - Remove `project_id` from `Credential` entity
   - Remove `description`, `contact_email`, `contact_phone` from `Customer` entity
   - Remove `display_name`, `description` from `Vendor` entity

2. **app/models/schemas.py**
   - Remove `project_id` from credential schemas
   - Remove customer contact fields from schemas
   - Remove vendor display fields from schemas

3. **app/dao/credential_dao.py**
   - Remove `project_id` from all credential operations
   - Update queries to remove project joins

4. **app/services/credential_service.py**
   - Remove project validation from credential creation
   - Remove project_id from vault path generation
   - Update all credential operations

5. **app/routers/credentials.py**
   - Remove `project_id` parameter from list endpoint
   - Update credential creation/update endpoints

## Rollback Plan

If you need to rollback:

1. Restore from backup
2. Or manually add back the removed columns:
   ```sql
   ALTER TABLE customers ADD COLUMN description TEXT;
   ALTER TABLE customers ADD COLUMN contact_email VARCHAR(255);
   ALTER TABLE customers ADD COLUMN contact_phone VARCHAR(50);
   
   ALTER TABLE vendors ADD COLUMN display_name VARCHAR(255);
   ALTER TABLE vendors ADD COLUMN description TEXT;
   
   ALTER TABLE credentials ADD COLUMN project_id INT NOT NULL;
   ALTER TABLE credentials ADD FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE;
   ```

## Verification

After migration, verify the schema:

```sql
DESCRIBE customers;
DESCRIBE vendors;
DESCRIBE credentials;
```

Expected results:
- `customers`: id, name, created_at, updated_at
- `vendors`: id, name, created_at, updated_at
- `credentials`: id, customer_id, vendor_id, access_key, vault_path, resource_user, labels, status, created_at, updated_at

