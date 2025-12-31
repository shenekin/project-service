# Fix: GitHub Secret Scanning Alert

**Date:** 2024-12-30  
**Issue:** GitHub Secret Scanning detected a hardcoded password in the codebase  
**Alert ID:** 37bwNR38VpC8OvJxhBx2lqZyNwX

## Problem Description

GitHub's Secret Scanning feature detected a hardcoded password in the codebase:

```
app/settings.py:29
mysql_password: str = os.getenv("MYSQL_PASSWORD", "1qaz@WSX")
```

The default password `1qaz@WSX` was hardcoded in the source code, which is a security risk.

## Security Risk

1. **Exposed Credentials**: Hardcoded passwords in source code are visible to anyone with access to the repository
2. **Version Control**: Even if removed later, the password remains in git history
3. **Secret Scanning**: GitHub's secret scanning detects and alerts on such patterns
4. **Compliance**: Violates security best practices and compliance requirements

## Solution

### Changes Made

**File:** `app/settings.py`

**Before:**
```python
mysql_password: str = os.getenv("MYSQL_PASSWORD", "1qaz@WSX")
```

**After:**
```python
mysql_password: str = os.getenv("MYSQL_PASSWORD", "")
```

### Rationale

1. **Removed Hardcoded Password**: Changed default value from `"1qaz@WSX"` to empty string `""`
2. **Environment Variable Required**: Users must set `MYSQL_PASSWORD` environment variable
3. **No Default Fallback**: Empty string ensures users are aware they must configure the password
4. **Security Best Practice**: Follows the principle of "no secrets in code"

## Implementation Details

The change requires that `MYSQL_PASSWORD` environment variable **must be set** in the environment configuration files (`.env`, `.env.dev`, `.env.prod`).

### Configuration in .env Files

All environment files (`.env`, `.env.dev`, `.env.prod`) should include:

```bash
# MySQL Configuration
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=your_actual_password_here  # Must be set!
MYSQL_DATABASE=project_db
```

### Validation (Optional Enhancement)

For better security, you can add validation in the `Settings` class:

```python
from pydantic import field_validator

@field_validator('mysql_password')
@classmethod
def validate_mysql_password(cls, v: str) -> str:
    if not v:
        raise ValueError("MYSQL_PASSWORD environment variable must be set")
    return v
```

## Steps to Resolve GitHub Alert

### 1. Fix the Code (Already Done)

✅ Removed hardcoded password from `app/settings.py`

### 2. Rotate the Exposed Password

**CRITICAL**: If this password was ever used in production:

1. **Change the MySQL password immediately**:
   ```sql
   ALTER USER 'root'@'localhost' IDENTIFIED BY 'new_secure_password';
   FLUSH PRIVILEGES;
   ```

2. **Update all environment files**:
   - Update `.env`, `.env.dev`, `.env.prod` with new password
   - Ensure `.env*` files are in `.gitignore`

3. **Rotate in all environments**:
   - Development
   - Staging
   - Production

### 3. Update Git History (If Repository is Private)

If this is a private repository and you want to remove the password from git history:

**Warning**: Only do this if:
- Repository is private
- You have approval from your team
- You understand the implications of rewriting git history

```bash
# Use git-filter-repo (recommended) or BFG Repo-Cleaner
# This will rewrite git history to remove the password

# Example with git-filter-repo
git filter-repo --replace-text passwords.txt

# passwords.txt content:
# 1qaz@WSX==>REPLACED_WITH_ENV_VAR
```

**Alternative**: If repository is public or shared:
- Consider the password compromised
- Change the password immediately
- Accept that it exists in git history
- Focus on preventing future occurrences

### 4. Mark GitHub Alert as Resolved

1. Go to GitHub repository
2. Navigate to **Security** → **Secret scanning**
3. Find the alert with ID: `37bwNR38VpC8OvJxhBx2lqZyNwX`
4. Mark as **Resolved** (after fixing and rotating password)

### 5. Prevent Future Occurrences

#### Add .gitignore Rules

✅ **Already Created**: `.gitignore` file with proper rules

Ensure sensitive files are ignored:

```gitignore
# Environment files
.env
.env.*
!.env.example
*.env
```

# Secrets
secrets/
*.pem
*.key
*.p12
*.jks

# Configuration with secrets
config/secrets.yaml
config/secrets.json
```

#### Add Pre-commit Hook

Create `.pre-commit-config.yaml`:

```yaml
repos:
  - repo: https://github.com/Yelp/detect-secrets
    rev: v1.4.0
    hooks:
      - id: detect-secrets
        args: ['--baseline', '.secrets.baseline']
```

#### Add GitHub Actions Secret Scanning

Ensure GitHub Secret Scanning is enabled:
- Go to repository **Settings** → **Security** → **Code security and analysis**
- Enable **Secret scanning**

## Best Practices Going Forward

### 1. Never Hardcode Secrets

❌ **Bad:**
```python
password = "my_secret_password"
api_key = "sk-1234567890"
```

✅ **Good:**
```python
password = os.getenv("MYSQL_PASSWORD", "")
if not password:
    raise ValueError("MYSQL_PASSWORD must be set")
```

### 2. Use Environment Variables

- Store secrets in environment variables
- Use `.env` files for local development (never commit them)
- Use secret management tools for production (Vault, AWS Secrets Manager, etc.)

### 3. Use Secret Management

For production environments:
- **HashiCorp Vault** (already integrated in project-service)
- **AWS Secrets Manager**
- **Azure Key Vault**
- **Google Secret Manager**
- **Kubernetes Secrets**

### 4. Code Review Guidelines

- Always review for hardcoded secrets
- Use automated tools (detect-secrets, git-secrets)
- Require approval for secret-related changes

### 5. Documentation

- Document which secrets are required
- Provide `.env.example` files with placeholder values
- Include setup instructions in README

## Verification

### Check for Other Hardcoded Secrets

```bash
# Search for common secret patterns
grep -r "password.*=" app/ --include="*.py" | grep -v "os.getenv"
grep -r "secret.*=" app/ --include="*.py" | grep -v "os.getenv"
grep -r "api_key.*=" app/ --include="*.py" | grep -v "os.getenv"
grep -r "token.*=" app/ --include="*.py" | grep -v "os.getenv"

# Search for specific patterns
grep -r "1qaz@WSX" . --exclude-dir=.git
```

### Test Configuration

```bash
# Test without password (should fail gracefully or use empty string)
unset MYSQL_PASSWORD
python -c "from app.settings import get_settings; s = get_settings(); print('Password set:', bool(s.mysql_password))"

# Test with password
export MYSQL_PASSWORD="test_password"
python -c "from app.settings import get_settings; s = get_settings(); print('Password set:', bool(s.mysql_password))"
```

## Summary

✅ **Fixed**: Removed hardcoded password from `app/settings.py`  
✅ **Action Required**: Set `MYSQL_PASSWORD` in environment files  
⚠️ **Critical**: Rotate password if it was used in production  
✅ **Prevention**: Follow best practices to prevent future occurrences

## Related Files

- `app/settings.py` - Settings configuration (fixed)
- `.env` - Environment configuration (user must set password)
- `.env.dev` - Development environment (user must set password)
- `.env.prod` - Production environment (user must set password)
- `.gitignore` - Should exclude `.env*` files

## References

- [GitHub Secret Scanning Documentation](https://docs.github.com/en/code-security/secret-scanning)
- [OWASP: Use of Hard-coded Cryptographic Key](https://owasp.org/www-community/vulnerabilities/Use_of_hard-coded_cryptographic_key)
- [12 Factor App: Config](https://12factor.net/config)

