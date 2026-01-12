"""
Unit tests for credential service
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi import HTTPException, status
from app.services.credential_service import CredentialService
from app.models.schemas import CredentialCreate, CredentialUpdate
from app.models.entities import Credential, Customer, Project, Vendor
from datetime import datetime


@pytest.mark.asyncio
async def test_create_credential_success():
    """Test successful credential creation with encryption"""
    service = CredentialService()
    
    # Mock dependencies
    customer = Customer(id=1, name="Test Customer")
    project = Project(id=1, customer_id=1, name="Test Project")
    vendor = Vendor(id=1, name="huaweicloud", display_name="Huawei Cloud")
    credential = Credential(
        id=1, customer_id=1, project_id=1, vendor_id=1,
        access_key="TEST_AK_12345", vault_path="/test/path",
        created_at=datetime.utcnow(), updated_at=datetime.utcnow()
    )
    
    with patch.object(service.customer_dao, 'get_by_id', return_value=customer), \
         patch.object(service.project_dao, 'get_by_id', return_value=project), \
         patch.object(service.vendor_dao, 'get_by_id', return_value=vendor), \
         patch.object(service.vault_util, 'is_connected', return_value=True), \
         patch.object(service.vault_util, 'write_secret', return_value=True), \
         patch.object(service.crypto_util, 'encrypt', return_value="encrypted_sk"), \
         patch.object(service.credential_dao, 'create', return_value=credential), \
         patch.object(service.audit_log_dao, 'create', return_value=None):
        
        credential_data = CredentialCreate(
            customer_id=1,
            project_id=1,
            vendor_id=1,
            access_key="TEST_AK_12345",
            secret_key="TEST_SK_67890"
        )
        
        result = await service.create_credential(
            credential_data=credential_data,
            user_id="test-user"
        )
        
        assert result["id"] == 1
        assert result["access_key"] == "TEST_AK_12345"
        assert "secret_key" not in result


@pytest.mark.asyncio
async def test_create_credential_customer_not_found():
    """Test credential creation with non-existent customer"""
    service = CredentialService()
    
    with patch.object(service.customer_dao, 'get_by_id', return_value=None):
        credential_data = CredentialCreate(
            customer_id=999,
            project_id=1,
            vendor_id=1,
            access_key="TEST_AK",
            secret_key="TEST_SK"
        )
        
        with pytest.raises(HTTPException) as exc_info:
            await service.create_credential(
                credential_data=credential_data,
                user_id="test-user"
            )
        
        assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.asyncio
async def test_get_credential_context_success():
    """Test successful credential context retrieval"""
    service = CredentialService()
    
    credential = Credential(
        id=1, customer_id=1, project_id=1, vendor_id=1,
        access_key="TEST_AK_12345", status="active",
        created_at=datetime.utcnow(), updated_at=datetime.utcnow()
    )
    customer = Customer(id=1, name="Test Customer")
    project = Project(id=1, customer_id=1, name="Test Project")
    vendor = Vendor(id=1, name="huaweicloud", display_name="Huawei Cloud")
    
    with patch.object(service.credential_dao, 'get_by_id', return_value=credential), \
         patch.object(service.user_permission_dao, 'check_permission', return_value=True), \
         patch.object(service.customer_dao, 'get_by_id', return_value=customer), \
         patch.object(service.project_dao, 'get_by_id', return_value=project), \
         patch.object(service.vendor_dao, 'get_by_id', return_value=vendor), \
         patch.object(service.audit_log_dao, 'create', return_value=None):
        
        result = await service.get_credential_context(
            credential_id=1,
            user_id="test-user"
        )
        
        assert result.credential_id == 1
        assert result.access_key == "TEST_AK_12345"


@pytest.mark.asyncio
async def test_get_credential_context_no_permission():
    """Test credential context retrieval without permission"""
    service = CredentialService()
    
    credential = Credential(
        id=1, customer_id=1, project_id=1, vendor_id=1,
        access_key="TEST_AK_12345", status="active",
        created_at=datetime.utcnow(), updated_at=datetime.utcnow()
    )
    
    with patch.object(service.credential_dao, 'get_by_id', return_value=credential), \
         patch.object(service.user_permission_dao, 'check_permission', return_value=False):
        
        with pytest.raises(HTTPException) as exc_info:
            await service.get_credential_context(
                credential_id=1,
                user_id="test-user"
            )
        
        assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.asyncio
async def test_list_credentials_with_masked_ak():
    """Test listing credentials with masked access keys"""
    service = CredentialService()
    
    credentials_list = [
        {
            "id": 1,
            "customer_name": "Test Customer",
            "project_name": "Test Project",
            "vendor_name": "huaweicloud",
            "vendor_display_name": "Huawei Cloud",
            "access_key": "TEST_AK_12345",
            "status": "active"
        }
    ]
    
    with patch.object(service.credential_dao, 'list_by_user_permissions', return_value=credentials_list), \
         patch.object(service.crypto_util, 'mask_access_key', return_value="TEST****"):
        
        result = await service.list_credentials(
            user_id="test-user",
            page=1,
            page_size=20
        )
        
        assert result["total"] == 1
        assert result["items"][0]["access_key"] == "TEST****"


@pytest.mark.asyncio
async def test_update_credential_ak_sk():
    """Test updating credential with new AK and SK"""
    service = CredentialService()
    
    credential = Credential(
        id=1, customer_id=1, project_id=1, vendor_id=1,
        access_key="OLD_AK", vault_path="/old/path", status="active",
        created_at=datetime.utcnow(), updated_at=datetime.utcnow()
    )
    updated_credential = Credential(
        id=1, customer_id=1, project_id=1, vendor_id=1,
        access_key="NEW_AK", vault_path="/new/path", status="active",
        created_at=datetime.utcnow(), updated_at=datetime.utcnow()
    )
    
    with patch.object(service.credential_dao, 'get_by_id', return_value=credential), \
         patch.object(service.user_permission_dao, 'check_permission', return_value=True), \
         patch.object(service.vault_util, 'is_connected', return_value=True), \
         patch.object(service.crypto_util, 'encrypt', return_value="encrypted_new_sk"), \
         patch.object(service.vault_util, 'write_secret', return_value=True), \
         patch.object(service.vault_util, 'delete_secret', return_value=True), \
         patch.object(service.credential_dao, 'update', return_value=updated_credential), \
         patch.object(service.audit_log_dao, 'create', return_value=None):
        
        update_data = CredentialUpdate(
            access_key="NEW_AK",
            secret_key="NEW_SK"
        )
        
        result = await service.update_credential(
            credential_id=1,
            credential_data=update_data,
            user_id="test-user"
        )
        
        assert result["access_key"] == "NEW_AK"
        assert "secret_key" not in result


@pytest.mark.asyncio
async def test_get_credential_for_api_call():
    """Test retrieving credential for third-party API calls with decrypted SK"""
    service = CredentialService()
    
    credential = Credential(
        id=1, customer_id=1, project_id=1, vendor_id=1,
        access_key="TEST_AK_12345", vault_path="/test/path", status="active",
        created_at=datetime.utcnow(), updated_at=datetime.utcnow()
    )
    
    vault_data = {"secret_key": "encrypted_sk"}
    
    with patch.object(service.credential_dao, 'get_by_id', return_value=credential), \
         patch.object(service.user_permission_dao, 'check_permission', return_value=True), \
         patch.object(service.vault_util, 'is_connected', return_value=True), \
         patch.object(service.vault_util, 'read_secret', return_value=vault_data), \
         patch.object(service.crypto_util, 'decrypt', return_value="decrypted_sk"), \
         patch.object(service.audit_log_dao, 'create', return_value=None):
        
        result = await service.get_credential_for_api_call(
            credential_id=1,
            user_id="test-user"
        )
        
        assert result["access_key"] == "TEST_AK_12345"
        assert result["secret_key"] == "decrypted_sk"
        assert result["credential_id"] == 1
