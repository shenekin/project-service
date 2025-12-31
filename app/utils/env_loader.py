"""
Environment file loader utility for multi-environment support
"""

import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv


class EnvironmentLoader:
    """Utility class for loading environment configuration files"""
    
    # Supported environment files
    ENV_FILES = {
        "default": ".env",
        "dev": ".env.dev",
        "development": ".env.dev",
        "prod": ".env.prod",
        "production": ".env.prod"
    }
    
    @classmethod
    def get_env_file_path(cls, env_name: Optional[str] = None, base_path: Optional[str] = None) -> str:
        """
        Get environment file path based on environment name
        
        Args:
            env_name: Environment name (default, dev, prod)
            base_path: Base directory path for .env files
            
        Returns:
            Path to environment file
        """
        if env_name is None:
            env_name = os.getenv("ENVIRONMENT", "default").lower()
        
        env_file = cls.ENV_FILES.get(env_name, ".env")
        
        if base_path:
            return str(Path(base_path) / env_file)
        
        # Try project root directory
        current_dir = Path(__file__).parent.parent.parent
        env_path = current_dir / env_file
        
        if env_path.exists():
            return str(env_path)
        
        # Fallback to current directory
        return env_file
    
    @classmethod
    def load_environment(cls, env_name: Optional[str] = None, base_path: Optional[str] = None) -> bool:
        """
        Load environment variables from specified environment file
        
        Args:
            env_name: Environment name (default, dev, prod)
            base_path: Base directory path for .env files
            
        Returns:
            True if file loaded successfully, False otherwise
        """
        env_file_path = cls.get_env_file_path(env_name, base_path)
        
        if not os.path.exists(env_file_path):
            # If specific env file doesn't exist, try default .env
            if env_name and env_name != "default":
                default_path = cls.get_env_file_path("default", base_path)
                if os.path.exists(default_path):
                    env_file_path = default_path
                else:
                    return False
            else:
                return False
        
        # Load environment variables
        load_dotenv(env_file_path, override=True)
        return True
    
    @classmethod
    def get_available_environments(cls, base_path: Optional[str] = None) -> list[str]:
        """
        Get list of available environment files
        
        Args:
            base_path: Base directory path for .env files
            
        Returns:
            List of available environment names
        """
        available = []
        
        if base_path:
            search_dir = Path(base_path)
        else:
            search_dir = Path(__file__).parent.parent.parent
        
        for env_name, env_file in cls.ENV_FILES.items():
            env_path = search_dir / env_file
            if env_path.exists():
                available.append(env_name)
        
        return list(set(available))  # Remove duplicates

