-- Migration Script: Migrate to Simplified Schema
-- This script migrates existing database to the simplified schema design
-- WARNING: This is a breaking change that removes project_id from credentials table
-- Make sure to backup your database before running this migration

USE project_db;

-- Step 1: Backup existing data (optional, recommended)
-- CREATE TABLE credentials_backup AS SELECT * FROM credentials;

-- Step 2: Remove project_id foreign key constraint
ALTER TABLE credentials DROP FOREIGN KEY IF EXISTS credentials_ibfk_2;
ALTER TABLE credentials DROP INDEX IF EXISTS idx_project_id;

-- Step 3: Remove project_id column from credentials
-- Note: This will lose project_id data. If you need to preserve it, 
-- consider adding it to labels or creating a migration mapping table first
ALTER TABLE credentials DROP COLUMN IF EXISTS project_id;

-- Step 4: Simplify customers table (remove optional fields)
-- Note: This will remove description, contact_email, contact_phone
-- If you need to preserve this data, export it first
ALTER TABLE customers 
    DROP COLUMN IF EXISTS description,
    DROP COLUMN IF EXISTS contact_email,
    DROP COLUMN IF EXISTS contact_phone;

-- Step 5: Simplify vendors table (remove display_name and description)
-- Note: This will remove display_name and description
-- If you need to preserve this data, export it first
ALTER TABLE vendors 
    DROP COLUMN IF EXISTS display_name,
    DROP COLUMN IF EXISTS description;

-- Step 6: Fix labels column name if it was created as "abels" (typo fix)
ALTER TABLE credentials CHANGE COLUMN abels labels VARCHAR(500);

-- Step 7: Update vendors table name column length to match new schema
ALTER TABLE vendors MODIFY COLUMN name VARCHAR(255) NOT NULL UNIQUE;

-- Verification queries (run these to verify migration)
-- SELECT * FROM customers LIMIT 5;
-- SELECT * FROM vendors LIMIT 5;
-- SELECT * FROM credentials LIMIT 5;
-- DESCRIBE customers;
-- DESCRIBE vendors;
-- DESCRIBE credentials;

