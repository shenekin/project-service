"""
Application entry point with environment configuration support
"""

import argparse
import sys
from pathlib import Path
from app.utils.env_loader import EnvironmentLoader
from app.settings import get_settings
import uvicorn


def parse_arguments() -> argparse.Namespace:
    """
    Parse command line arguments
    
    Returns:
        Parsed arguments
    """
    parser = argparse.ArgumentParser(description="Project Service")
    parser.add_argument(
        "--env",
        type=str,
        choices=["default", "dev", "prod"],
        help="Environment name (default, dev, prod)"
    )
    parser.add_argument(
        "--host",
        type=str,
        help="Host to bind to (overrides environment variable)"
    )
    parser.add_argument(
        "--port",
        type=int,
        help="Port to bind to (overrides environment variable)"
    )
    parser.add_argument(
        "--reload",
        action="store_true",
        help="Enable auto-reload (development mode)"
    )
    
    return parser.parse_args()


def initialize_environment(args: argparse.Namespace) -> None:
    """
    Initialize environment configuration
    
    Args:
        args: Parsed command line arguments
    """
    if args.env:
        EnvironmentLoader.load_environment(env_name=args.env)
    else:
        EnvironmentLoader.load_environment()


def main():
    """Main entry point"""
    args = parse_arguments()
    
    # Initialize environment
    initialize_environment(args)
    
    # Get settings
    settings = get_settings()
    
    # Override with command line arguments if provided
    host = args.host or settings.host
    port = args.port or settings.port
    reload = args.reload or settings.debug
    
    # Run application
    uvicorn.run(
        "app.main:app",
        host=host,
        port=port,
        reload=reload
    )


if __name__ == "__main__":
    main()

