"""
Application settings and configuration management
"""

import os
from pathlib import Path
from typing import List, Optional
from dotenv import dotenv_values
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application configuration settings"""
    
    # Environment
    environment: str = os.getenv("ENVIRONMENT", "default")
    debug: bool = os.getenv("DEBUG", "false").lower() == "true"
    host: str = os.getenv("HOST", "0.0.0.0")
    port: int = int(os.getenv("PORT", "8002"))
    
    # SSL/TLS
    ssl_enabled: bool = os.getenv("SSL_ENABLED", "false").lower() == "true"
    ssl_cert_path: str = os.getenv("SSL_CERT_PATH", "/app/certs/cert.pem")
    ssl_key_path: str = os.getenv("SSL_KEY_PATH", "/app/certs/key.pem")
    
    # Database
    mysql_host: str = os.getenv("MYSQL_HOST", "localhost")
    mysql_port: int = int(os.getenv("MYSQL_PORT", "3306"))
    mysql_user: str = os.getenv("MYSQL_USER", "root")
    mysql_password: str = os.getenv("MYSQL_PASSWORD", "")
    mysql_database: str = os.getenv("MYSQL_DATABASE", "project_db")
    mysql_pool_size: int = int(os.getenv("MYSQL_POOL_SIZE", "10"))
    mysql_max_overflow: int = int(os.getenv("MYSQL_MAX_OVERFLOW", "20"))
    
    # Redis
    redis_host: str = os.getenv("REDIS_HOST", "localhost")
    redis_port: int = int(os.getenv("REDIS_PORT", "6379"))
    redis_password: Optional[str] = os.getenv("REDIS_PASSWORD")
    redis_db: int = int(os.getenv("REDIS_DB", "0"))
    redis_pool_size: int = int(os.getenv("REDIS_POOL_SIZE", "10"))
    
    # Service Discovery
    service_discovery_type: str = os.getenv("SERVICE_DISCOVERY_TYPE", "nacos")
    nacos_server_addresses: str = os.getenv("NACOS_SERVER_ADDRESSES", "localhost:8848")
    nacos_namespace: str = os.getenv("NACOS_NAMESPACE", "public")
    nacos_group: str = os.getenv("NACOS_GROUP", "DEFAULT_GROUP")
    nacos_service_name: str = os.getenv("NACOS_SERVICE_NAME", "project-service")
    nacos_service_port: int = int(os.getenv("NACOS_SERVICE_PORT", "8002"))
    nacos_service_ip: str = os.getenv("NACOS_SERVICE_IP", "localhost")
    
    # Vault Configuration (loaded only from .env)
    vault_enabled: bool = False
    vault_addr: Optional[str] = None
    vault_auth_method: Optional[str] = None
    vault_role_id: Optional[str] = None
    vault_secret_id: Optional[str] = None
    vault_token: Optional[str] = None
    vault_role_id_file: Optional[str] = None
    vault_secret_id_file: Optional[str] = None
    vault_timeout: Optional[int] = None
    vault_verify: Optional[bool] = None
    
    # Vault Secret Paths (loaded only from .env)
    vault_credential_path: Optional[str] = None
    
    # Logging Configuration
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    log_format: str = os.getenv("LOG_FORMAT", "json")
    _default_log_dir = os.path.join(os.getcwd(), "logs") if os.path.exists(os.getcwd()) else "/app/logs"
    log_file_path: str = os.getenv("LOG_FILE_PATH", os.path.join(_default_log_dir, "project-service.log"))
    log_directory: str = os.getenv("LOG_DIRECTORY", _default_log_dir)
    log_request_file: str = os.getenv("LOG_REQUEST_FILE", os.path.join(_default_log_dir, "request.log"))
    log_error_file: str = os.getenv("LOG_ERROR_FILE", os.path.join(_default_log_dir, "error.log"))
    log_access_file: str = os.getenv("LOG_ACCESS_FILE", os.path.join(_default_log_dir, "access.log"))
    log_audit_file: str = os.getenv("LOG_AUDIT_FILE", os.path.join(_default_log_dir, "audit.log"))
    log_application_file: str = os.getenv("LOG_APPLICATION_FILE", os.path.join(_default_log_dir, "application.log"))
    
    # Log rotation configuration
    log_max_bytes: int = int(os.getenv("LOG_MAX_BYTES", "10485760"))  # 10MB
    log_backup_count: int = int(os.getenv("LOG_BACKUP_COUNT", "5"))
    
    # Monitoring
    prometheus_enabled: bool = os.getenv("PROMETHEUS_ENABLED", "true").lower() == "true"
    metrics_port: int = int(os.getenv("METRICS_PORT", "9091"))
    
    # Security
    trusted_proxies: str = os.getenv("TRUSTED_PROXIES", "127.0.0.1,localhost")
    allowed_origins: str = os.getenv("ALLOWED_ORIGINS", "*")
    cors_enabled: bool = os.getenv("CORS_ENABLED", "true").lower() == "true"
    
    # JWT Configuration (for extracting user context from gateway)
    jwt_public_key_path: Optional[str] = os.getenv("JWT_PUBLIC_KEY_PATH")
    
    @property
    def trusted_proxy_list(self) -> List[str]:
        """Get list of trusted proxy IPs"""
        return [ip.strip() for ip in self.trusted_proxies.split(",")]
    
    @property
    def allowed_origins_list(self) -> List[str]:
        """Get list of allowed CORS origins"""
        if self.allowed_origins == "*":
            return ["*"]
        return [origin.strip() for origin in self.allowed_origins.split(",")]
    
    class Config:
        """Pydantic configuration"""
        env_file = ".env"
        case_sensitive = False
        extra = "ignore"

    def __init__(self, **values):
        super().__init__(**values)
        self._apply_vault_env()

    def _apply_vault_env(self) -> None:
        """Load Vault settings strictly from .env"""
        env_path = Path(__file__).parent.parent / ".env"
        vault_env = dotenv_values(env_path) if env_path.exists() else {}

        def _clean(value: Optional[str]) -> Optional[str]:
            if value is None:
                return None
            value = value.strip()
            return value if value else None

        def _parse_bool(value: Optional[str], default: Optional[bool] = None) -> Optional[bool]:
            if value is None:
                return default
            normalized = value.strip().lower()
            if normalized in {"1", "true", "yes", "on"}:
                return True
            if normalized in {"0", "false", "no", "off"}:
                return False
            raise ValueError(f"Invalid boolean value for Vault setting: {value}")

        self.vault_enabled = _parse_bool(vault_env.get("VAULT_ENABLED"), default=False)
        self.vault_addr = _clean(vault_env.get("VAULT_ADDR"))
        self.vault_auth_method = _clean(vault_env.get("VAULT_AUTH_METHOD"))
        self.vault_role_id = _clean(vault_env.get("VAULT_ROLE_ID"))
        self.vault_secret_id = _clean(vault_env.get("VAULT_SECRET_ID"))
        self.vault_token = _clean(vault_env.get("VAULT_TOKEN"))
        self.vault_role_id_file = _clean(vault_env.get("VAULT_ROLE_ID_FILE"))
        self.vault_secret_id_file = _clean(vault_env.get("VAULT_SECRET_ID_FILE"))
        self.vault_credential_path = _clean(vault_env.get("VAULT_CREDENTIAL_PATH"))

        timeout_value = _clean(vault_env.get("VAULT_TIMEOUT"))
        if timeout_value is not None:
            try:
                self.vault_timeout = int(timeout_value)
            except ValueError as exc:
                raise ValueError(f"Invalid VAULT_TIMEOUT in .env: {timeout_value}") from exc
        else:
            self.vault_timeout = None

        verify_value = _clean(vault_env.get("VAULT_VERIFY"))
        self.vault_verify = _parse_bool(verify_value, default=None)


@lru_cache()
def get_settings(env_name: Optional[str] = None, env_file_path: Optional[str] = None) -> Settings:
    """
    Get cached settings instance with optional environment file loading
    
    Args:
        env_name: Environment name (default, dev, prod)
        env_file_path: Custom path to .env file
        
    Returns:
        Settings instance
    """
    # Load environment file if specified
    if env_file_path:
        from app.utils.env_loader import EnvironmentLoader
        EnvironmentLoader.load_environment(base_path=os.path.dirname(env_file_path))
        Settings.Config.env_file = os.path.basename(env_file_path)
    elif env_name:
        from app.utils.env_loader import EnvironmentLoader
        EnvironmentLoader.load_environment(env_name=env_name)
        env_file = EnvironmentLoader.get_env_file_path(env_name)
        Settings.Config.env_file = env_file
    
    return Settings()


def reload_settings(env_name: Optional[str] = None, env_file_path: Optional[str] = None) -> Settings:
    """
    Reload settings with new environment configuration
    
    Args:
        env_name: Environment name (default, dev, prod)
        env_file_path: Custom path to .env file
        
    Returns:
        New Settings instance
    """
    from app.utils.env_loader import EnvironmentLoader
    
    # Clear cache to force reload
    get_settings.cache_clear()
    
    # Load new environment
    if env_file_path:
        EnvironmentLoader.load_environment(base_path=os.path.dirname(env_file_path))
    elif env_name:
        EnvironmentLoader.load_environment(env_name=env_name)
    
    return get_settings(env_name, env_file_path)


