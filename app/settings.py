"""
Application settings and configuration management
"""

import os
from typing import List, Optional
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
    mysql_password: str = os.getenv("MYSQL_PASSWORD", "1qaz@WSX")
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
    
    # Vault Configuration
    vault_enabled: bool = os.getenv("VAULT_ENABLED", "false").lower() == "true"
    vault_addr: str = os.getenv("VAULT_ADDR", "http://127.0.0.1:8200")
    vault_auth_method: str = os.getenv("VAULT_AUTH_METHOD", "approle")
    vault_role_id: Optional[str] = os.getenv("VAULT_ROLE_ID")
    vault_secret_id: Optional[str] = os.getenv("VAULT_SECRET_ID")
    vault_token: Optional[str] = os.getenv("VAULT_TOKEN")
    vault_timeout: int = int(os.getenv("VAULT_TIMEOUT", "5"))
    vault_verify: bool = os.getenv("VAULT_VERIFY", "true").lower() == "true"
    
    # Vault Secret Paths
    vault_credential_path: str = os.getenv("VAULT_CREDENTIAL_PATH", "secret/credentials")
    
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

