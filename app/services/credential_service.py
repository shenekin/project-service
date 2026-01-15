"""
Service layer for Credential Management
"""

from typing import Optional, List
from fastapi import HTTPException, status
from app.dao.credential_dao import CredentialDAO
from app.dao.customer_dao import CustomerDAO
from app.dao.project_dao import ProjectDAO
from app.dao.vendor_dao import VendorDAO
from app.dao.audit_log_dao import AuditLogDAO
from app.dao.user_permission_dao import UserPermissionDAO
from app.models.schemas import CredentialCreate, CredentialUpdate, CredentialContextResponse
from app.utils.vault_util import VaultUtil
from app.utils import log_error
from app.utils.crypto_util import CryptoUtil
from app.settings import get_settings


class CredentialService:
    """Service for credential management operations"""
    
    def __init__(self):
        """Initialize credential service"""
        self.credential_dao = CredentialDAO()
        self.customer_dao = CustomerDAO()
        self.project_dao = ProjectDAO()
        self.vendor_dao = VendorDAO()
        self.audit_log_dao = AuditLogDAO()
        self.user_permission_dao = UserPermissionDAO()
        self.settings = get_settings()
        if self.settings.vault_enabled and not self.settings.vault_credential_path:
            raise ValueError("VAULT_CREDENTIAL_PATH must be set in .env when Vault is enabled")
        self.vault_util = VaultUtil() if self.settings.vault_enabled else None
        self.crypto_util = CryptoUtil()
    
    async def create_credential(self, credential_data: CredentialCreate, user_id: str,
                                ip_address: Optional[str] = None,
                                user_agent: Optional[str] = None) -> dict:
        """
        Create a new credential
        
        Args:
            credential_data: Credential creation data
            user_id: User ID performing the action
            ip_address: IP address of the request
            user_agent: User agent of the request
            
        Returns:
            Created credential dictionary
            
        Raises:
            HTTPException: If validation fails or creation fails
        """
        # Validate customer exists
        customer = await self.customer_dao.get_by_id(credential_data.customer_id)
        if not customer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Customer with ID {credential_data.customer_id} not found"
            )
        
        project = None
        
        # Validate vendor exists
        vendor = await self.vendor_dao.get_by_id(credential_data.vendor_id)
        if not vendor:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Vendor with ID {credential_data.vendor_id} not found"
            )
        
        # Encrypt and store SK in Vault
        vault_path = None
        if self.vault_util and self.vault_util.is_connected():
            vault_path = f"{self.settings.vault_credential_path}/{credential_data.customer_id}/no-project/{credential_data.vendor_id}/{credential_data.access_key}"
            try:
                # Encrypt secret key before storing in Vault
                encrypted_sk = self.crypto_util.encrypt(credential_data.secret_key)
                vault_payload = {
                    "secret_key": encrypted_sk,  # Store encrypted SK
                    "access_key": credential_data.access_key,
                    "customer_id": credential_data.customer_id,
                    "vendor_id": credential_data.vendor_id
                }
                self.vault_util.write_secret(vault_path, vault_payload)
            except Exception as e:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Failed to store secret in Vault: {str(e)}"
                )
        else:
            log_error(
                "Vault is not available. Cannot store credentials securely.",
                action="create_credential",
                customer_id=credential_data.customer_id,
                vendor_id=credential_data.vendor_id,
            )
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Vault is not available. Cannot store credentials securely."
            )
        
        # Create credential in database
        try:
            credential = await self.credential_dao.create(
                customer_id=credential_data.customer_id,
                vendor_id=credential_data.vendor_id,
                access_key=credential_data.access_key,
                vault_path=vault_path,
                resource_user=credential_data.resource_user,
                labels=credential_data.labels,
                status=credential_data.status
            )
            
            # Create audit log
            await self.audit_log_dao.create(
                user_id=user_id,
                action="create_credential",
                resource_type="credential",
                resource_id=credential.id,
                customer_id=credential.customer_id,
                project_id=credential.project_id,
                vendor_id=credential.vendor_id,
                credential_id=credential.id,
                details=f"Created credential for customer {customer.name}, project no-project, vendor {vendor.display_name}",
                ip_address=ip_address,
                user_agent=user_agent
            )
            
            return credential.to_dict(include_secret=False)
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
    
    async def get_credential_context(self, credential_id: int, user_id: str,
                                     ip_address: Optional[str] = None,
                                     user_agent: Optional[str] = None) -> CredentialContextResponse:
        """
        Get credential context for internal services (without exposing SK)
        
        Args:
            credential_id: Credential ID
            user_id: User ID requesting the context
            ip_address: IP address of the request
            user_agent: User agent of the request
            
        Returns:
            Credential context response
            
        Raises:
            HTTPException: If credential not found or user doesn't have permission
        """
        # Get credential
        credential = await self.credential_dao.get_by_id(credential_id)
        if not credential:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Credential with ID {credential_id} not found"
            )
        
        # Check if credential is active
        if credential.status != "active":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Credential is not active (status: {credential.status})"
            )
        
        # Check user permission
        has_permission = await self.user_permission_dao.check_permission(
            user_id=user_id,
            customer_id=credential.customer_id,
            project_id=credential.project_id
        )
        if not has_permission:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User does not have permission to access this credential"
            )
        
        # Get related entities
        customer = await self.customer_dao.get_by_id(credential.customer_id)
        vendor = await self.vendor_dao.get_by_id(credential.vendor_id)
        project_name = "no-project"
        if credential.project_id is not None:
            project = await self.project_dao.get_by_id(credential.project_id)
            if project:
                project_name = project.name
        
        if not customer or not vendor:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Related entities not found"
            )
        
        # Create audit log
        await self.audit_log_dao.create(
            user_id=user_id,
            action="use_credential",
            resource_type="credential",
            resource_id=credential.id,
            customer_id=credential.customer_id,
            project_id=credential.project_id,
            vendor_id=credential.vendor_id,
            credential_id=credential.id,
            details=f"User {user_id} accessed credential context",
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        return CredentialContextResponse(
            credential_id=credential.id,
            customer_name=customer.name,
            project_name=project_name,
            vendor_name=vendor.name,
            vendor_display_name=vendor.display_name,
            access_key=credential.access_key,
            vault_path=credential.vault_path or "",
            resource_user=credential.resource_user,
            status=credential.status,
            labels=credential.labels
        )
    
    async def get_credential_for_api_call(self, credential_id: int, user_id: str,
                                          ip_address: Optional[str] = None,
                                          user_agent: Optional[str] = None) -> dict:
        """
        Get full credential (AK and decrypted SK) for third-party API calls
        
        Args:
            credential_id: Credential ID
            user_id: User ID requesting the credential
            ip_address: IP address of the request
            user_agent: User agent of the request
            
        Returns:
            Dictionary containing access_key and secret_key (decrypted)
            
        Raises:
            HTTPException: If credential not found, not active, or user doesn't have permission
        """
        # Get credential
        credential = await self.credential_dao.get_by_id(credential_id)
        if not credential:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Credential with ID {credential_id} not found"
            )
        
        # Check if credential is active
        if credential.status != "active":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Credential is not active (status: {credential.status})"
            )
        
        # Check user permission
        has_permission = await self.user_permission_dao.check_permission(
            user_id=user_id,
            customer_id=credential.customer_id,
            project_id=credential.project_id
        )
        if not has_permission:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User does not have permission to access this credential"
            )
        
        # Retrieve and decrypt SK from Vault
        secret_key = None
        if credential.vault_path and self.vault_util and self.vault_util.is_connected():
            try:
                vault_data = self.vault_util.read_secret(credential.vault_path)
                encrypted_sk = vault_data.get("secret_key")
                if encrypted_sk:
                    secret_key = self.crypto_util.decrypt(encrypted_sk)
            except Exception as e:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Failed to retrieve secret from Vault: {str(e)}"
                )
        else:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Vault is not available. Cannot retrieve credentials securely."
            )
        
        # Create audit log
        await self.audit_log_dao.create(
            user_id=user_id,
            action="retrieve_credential_for_api",
            resource_type="credential",
            resource_id=credential.id,
            customer_id=credential.customer_id,
            project_id=credential.project_id,
            vendor_id=credential.vendor_id,
            credential_id=credential.id,
            details=f"User {user_id} retrieved credential for third-party API call",
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        return {
            "credential_id": credential.id,
            "access_key": credential.access_key,
            "secret_key": secret_key,
            "vendor_id": credential.vendor_id,
            "customer_id": credential.customer_id,
            "project_id": credential.project_id
        }
    
    async def list_credentials(self, user_id: str, customer_id: Optional[int] = None,
                               project_id: Optional[int] = None,
                               page: int = 1, page_size: int = 20) -> dict:
        """
        List credentials available to user
        
        Args:
            user_id: User ID
            customer_id: Optional customer ID filter
            project_id: Optional project ID filter
            page: Page number
            page_size: Page size
            
        Returns:
            Paginated list of credentials
        """
        skip = (page - 1) * page_size
        
        credentials = await self.credential_dao.list_by_user_permissions(
            user_id=user_id,
            customer_id=customer_id,
            project_id=project_id,
            skip=skip,
            limit=page_size
        )
        
        # Mask access keys in list response (show only first 4 characters)
        for cred in credentials:
            if "access_key" in cred:
                cred["access_key"] = self.crypto_util.mask_access_key(cred["access_key"], visible_chars=4)
        
        # Get total count (simplified - in production, use a separate count query)
        total = len(credentials)  # This is approximate
        
        return {
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size,
            "items": credentials
        }
    
    async def update_credential(self, credential_id: int, credential_data: CredentialUpdate,
                               user_id: str, ip_address: Optional[str] = None,
                               user_agent: Optional[str] = None) -> dict:
        """
        Update credential (supports AK and SK updates)
        
        Args:
            credential_id: Credential ID to update
            credential_data: Credential update data (may include AK and SK)
            user_id: User ID performing the action
            ip_address: IP address of the request
            user_agent: User agent of the request
            
        Returns:
            Updated credential dictionary
            
        Raises:
            HTTPException: If validation fails or update fails
        """
        # Get credential
        credential = await self.credential_dao.get_by_id(credential_id)
        if not credential:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Credential with ID {credential_id} not found"
            )
        
        # Check user permission
        has_permission = await self.user_permission_dao.check_permission(
            user_id=user_id,
            customer_id=credential.customer_id,
            project_id=credential.project_id
        )
        if not has_permission:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User does not have permission to update this credential"
            )
        
        # Handle SK update (if provided)
        new_vault_path = None
        if credential_data.secret_key:
            if not self.vault_util or not self.vault_util.is_connected():
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail="Vault is not available. Cannot update secret key securely."
                )
            
            # Determine new access key (use updated AK if provided, otherwise use existing)
            new_access_key = credential_data.access_key if credential_data.access_key else credential.access_key
            
            # Generate new vault path
            new_vault_path = f"{self.settings.vault_credential_path}/{credential.customer_id}/no-project/{credential.vendor_id}/{new_access_key}"
            
            try:
                # Encrypt secret key before storing in Vault
                encrypted_sk = self.crypto_util.encrypt(credential_data.secret_key)
                self.vault_util.write_secret(new_vault_path, {
                    "secret_key": encrypted_sk,  # Store encrypted SK
                    "access_key": new_access_key,
                    "customer_id": credential.customer_id,
                    "vendor_id": credential.vendor_id
                })
                
                # Delete old vault path if AK changed
                if credential_data.access_key and credential.vault_path and credential.vault_path != new_vault_path:
                    try:
                        self.vault_util.delete_secret(credential.vault_path)
                    except Exception:
                        pass  # Ignore errors when deleting old path
            except Exception as e:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Failed to update secret in Vault: {str(e)}"
                )
        
        # Update credential in database
        updated = await self.credential_dao.update(
            credential_id=credential_id,
            access_key=credential_data.access_key,
            vault_path=new_vault_path if new_vault_path else None,
            resource_user=credential_data.resource_user,
            labels=credential_data.labels,
            status=credential_data.status
        )
        
        if not updated:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Credential with ID {credential_id} not found"
            )
        
        # Create audit log
        update_details = []
        if credential_data.access_key:
            update_details.append("access_key")
        if credential_data.secret_key:
            update_details.append("secret_key")
        if credential_data.resource_user is not None:
            update_details.append("resource_user")
        if credential_data.labels is not None:
            update_details.append("labels")
        if credential_data.status:
            update_details.append("status")
        
        await self.audit_log_dao.create(
            user_id=user_id,
            action="update_credential",
            resource_type="credential",
            resource_id=credential.id,
            customer_id=credential.customer_id,
            project_id=credential.project_id,
            vendor_id=credential.vendor_id,
            credential_id=credential.id,
            details=f"Updated credential fields: {', '.join(update_details) if update_details else 'none'}",
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        return updated.to_dict(include_secret=False)
    
    async def delete_credential(self, credential_id: int, user_id: str,
                                ip_address: Optional[str] = None,
                                user_agent: Optional[str] = None) -> bool:
        """Delete credential (soft delete)"""
        # Get credential
        credential = await self.credential_dao.get_by_id(credential_id)
        if not credential:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Credential with ID {credential_id} not found"
            )
        
        # Check user permission
        has_permission = await self.user_permission_dao.check_permission(
            user_id=user_id,
            customer_id=credential.customer_id,
            project_id=credential.project_id
        )
        if not has_permission:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User does not have permission to delete this credential"
            )
        
        # Delete credential (soft delete)
        deleted = await self.credential_dao.delete(credential_id)
        
        if deleted:
            # Create audit log
            await self.audit_log_dao.create(
                user_id=user_id,
                action="delete_credential",
                resource_type="credential",
                resource_id=credential.id,
                customer_id=credential.customer_id,
                project_id=credential.project_id,
                vendor_id=credential.vendor_id,
                credential_id=credential.id,
                details=f"Deleted credential",
                ip_address=ip_address,
                user_agent=user_agent
            )
        
        return deleted

