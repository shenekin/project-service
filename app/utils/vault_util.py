"""
HashiCorp Vault utility for secret management
"""

import os
from typing import Optional, Dict, Any
import hvac
from app.settings import get_settings
from app.utils import log_warning


class VaultUtil:
    """Utility class for interacting with HashiCorp Vault"""
    
    def __init__(self):
        """Initialize Vault client"""
        self.settings = get_settings()
        self.client: Optional[hvac.Client] = None
        if self.settings.vault_enabled:
            self._connect()
    
    def _connect(self) -> None:
        """Connect to Vault and authenticate"""
        try:
            vault_addr = self.settings.vault_addr
            vault_auth_method = self.settings.vault_auth_method
            vault_timeout = self.settings.vault_timeout
            vault_verify = self.settings.vault_verify

            if not vault_addr:
                raise ValueError("Missing Vault configuration in .env: VAULT_ADDR")

            if vault_addr.startswith("http://"):
                # No TLS on HTTP; SSL verification is not applicable.
                vault_verify = None

            client_kwargs = {"url": vault_addr}
            if vault_timeout is not None:
                client_kwargs["timeout"] = vault_timeout
            if vault_verify is not None:
                client_kwargs["verify"] = vault_verify

            # Create Vault client with optional timeout and SSL verification
            self.client = hvac.Client(**client_kwargs)
            
            # Authenticate based on method
            role_id = self.settings.vault_role_id
            secret_id = self.settings.vault_secret_id
            vault_token = self.settings.vault_token
            role_id_file = self.settings.vault_role_id_file
            secret_id_file = self.settings.vault_secret_id_file

            if not role_id and role_id_file and os.path.exists(role_id_file):
                try:
                    with open(role_id_file, "r", encoding="utf-8") as handle:
                        role_id = handle.read().strip() or None
                except OSError as exc:
                    log_warning(
                        "Unable to read Vault role_id file",
                        action="vault_connect",
                        file_path=role_id_file,
                        error=str(exc),
                    )
                    role_id = None
            if not secret_id and secret_id_file and os.path.exists(secret_id_file):
                try:
                    with open(secret_id_file, "r", encoding="utf-8") as handle:
                        secret_id = handle.read().strip() or None
                except OSError as exc:
                    log_warning(
                        "Unable to read Vault secret_id file",
                        action="vault_connect",
                        file_path=secret_id_file,
                        error=str(exc),
                    )
                    secret_id = None

            if not vault_auth_method:
                if vault_token:
                    vault_auth_method = "token"
                elif role_id and secret_id:
                    vault_auth_method = "approle"
                else:
                    self.client = None
                    return

            if vault_auth_method == "approle":
                if not role_id or not secret_id:
                    if vault_token:
                        vault_auth_method = "token"
                    else:
                        self.client = None
                        return

            if vault_auth_method == "token":
                if not vault_token:
                    if role_id and secret_id:
                        vault_auth_method = "approle"
                    else:
                        self.client = None
                        return

            if vault_auth_method == "approle":
                response = self.client.auth.approle.login(
                    role_id=role_id,
                    secret_id=secret_id
                )
                self.client.token = response['auth']['client_token']
            elif vault_auth_method == "token":
                self.client.token = vault_token
            
            else:
                raise ValueError(f"Unsupported Vault auth method: {vault_auth_method}")
            
            # Verify connection
            if not self.client.is_authenticated():
                raise ConnectionError("Failed to authenticate with Vault")
                
        except Exception as e:
            self.client = None
            error_msg = str(e)
            if "sealed" in error_msg.lower():
                raise ConnectionError(f"Vault is sealed. Please unseal Vault first: {error_msg}")
            raise ConnectionError(f"Failed to connect to Vault: {error_msg}")
    
    def write_secret(self, path: str, data: Dict[str, Any]) -> bool:
        """
        Write secret to Vault
        
        Args:
            path: Secret path in Vault
            data: Secret data dictionary
            
        Returns:
            True if successful
        """
        if not self.client:
            raise ConnectionError("Vault client not initialized")
        
        try:
            # For KV v2, if path starts with "secret/", remove it
            if path.startswith("secret/"):
                path = path[len("secret/"):]
            
            # Write to KV v2 secrets engine
            self.client.secrets.kv.v2.create_or_update_secret(
                path=path,
                secret=data
            )
            return True
        except Exception as e:
            raise ValueError(f"Failed to write secret to path '{path}': {str(e)}")
    
    def read_secret(self, path: str) -> Dict[str, Any]:
        """
        Read secret from Vault
        
        Args:
            path: Secret path in Vault
            
        Returns:
            Secret data dictionary
        """
        if not self.client:
            raise ConnectionError("Vault client not initialized")
        
        try:
            # For KV v2, if path starts with "secret/", remove it
            if path.startswith("secret/"):
                path = path[len("secret/"):]
            
            # Read from KV v2 secrets engine
            response = self.client.secrets.kv.v2.read_secret_version(path=path)
            return response['data']['data']
        except Exception as e:
            raise ValueError(f"Failed to read secret from path '{path}': {str(e)}")
    
    def delete_secret(self, path: str) -> bool:
        """
        Delete secret from Vault
        
        Args:
            path: Secret path in Vault
            
        Returns:
            True if successful
        """
        if not self.client:
            raise ConnectionError("Vault client not initialized")
        
        try:
            # For KV v2, if path starts with "secret/", remove it
            if path.startswith("secret/"):
                path = path[len("secret/"):]
            
            # Delete from KV v2 secrets engine
            self.client.secrets.kv.v2.delete_metadata_and_all_versions(path=path)
            return True
        except Exception as e:
            raise ValueError(f"Failed to delete secret from path '{path}': {str(e)}")
    
    def is_connected(self) -> bool:
        """Check if Vault client is connected and authenticated"""
        return self.client is not None and self.client.is_authenticated()
    
    def health_check(self) -> Dict[str, Any]:
        """
        Check Vault health
        
        Returns:
            Health status dictionary
        """
        if not self.client:
            return {
                "status": "disconnected",
                "error": "Vault client not initialized"
            }
        
        try:
            health = self.client.sys.read_health_status()
            return {
                "status": "healthy" if health.get("initialized") else "uninitialized",
                "sealed": health.get("sealed", False),
                "standby": health.get("standby", False),
                "version": health.get("version", "unknown")
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }

