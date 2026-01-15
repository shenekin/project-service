"""
Utility modules for project service
"""

from __future__ import annotations

import json
import logging
import os
import re
from logging.handlers import RotatingFileHandler
from typing import Any, Dict

_LOGGING_CONFIGURED = False

_SECRET_KEY_PATTERN = re.compile(
    r"(access_key|secret_key|ak|sk|token|password|secret|vault_token)",
    re.IGNORECASE,
)


class RedactFilter(logging.Filter):
    """Redact sensitive values from log records."""

    def filter(self, record: logging.LogRecord) -> bool:
        record.msg = _redact_message(str(record.msg))
        if record.args:
            record.args = _redact_args(record.args)
        return True


class JsonFormatter(logging.Formatter):
    """Minimal JSON formatter for structured logs."""

    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "level": record.levelname,
            "logger": record.name,
            "message": _redact_message(record.getMessage()),
        }
        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)
        return json.dumps(payload, ensure_ascii=True)


def configure_logging(settings) -> None:
    """Configure centralized logging based on settings."""
    global _LOGGING_CONFIGURED
    if _LOGGING_CONFIGURED:
        return

    os.makedirs(settings.log_directory, exist_ok=True)

    formatter: logging.Formatter
    if settings.log_format.lower() == "json":
        formatter = JsonFormatter()
    else:
        formatter = logging.Formatter(
            "%(asctime)s %(levelname)s %(name)s %(message)s"
        )

    def _handler(path: str, level: int) -> RotatingFileHandler:
        handler = RotatingFileHandler(
            path,
            maxBytes=settings.log_max_bytes,
            backupCount=settings.log_backup_count,
        )
        handler.setLevel(level)
        handler.setFormatter(formatter)
        handler.addFilter(RedactFilter())
        return handler

    log_level = getattr(logging, settings.log_level.upper(), logging.INFO)

    _configure_logger(
        "project-service.connection",
        log_level,
        _handler(settings.log_access_file, log_level),
    )
    _configure_logger(
        "project-service.warning",
        max(logging.WARNING, log_level),
        _handler(settings.log_application_file, max(logging.WARNING, log_level)),
    )
    _configure_logger(
        "project-service.error",
        max(logging.ERROR, log_level),
        _handler(settings.log_error_file, max(logging.ERROR, log_level)),
    )

    _LOGGING_CONFIGURED = True


def _configure_logger(name: str, level: int, handler: logging.Handler) -> None:
    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.propagate = False
    if not logger.handlers:
        logger.addHandler(handler)


def get_logger(name: str) -> logging.Logger:
    """Get a logger with redaction support."""
    logger = logging.getLogger(name)
    if not any(isinstance(f, RedactFilter) for f in logger.filters):
        logger.addFilter(RedactFilter())
    if not logger.handlers:
        logger.addHandler(logging.NullHandler())
    return logger


def log_connection(message: str, **context: Any) -> None:
    """Log connection-related events safely."""
    _log_with_context("project-service.connection", logging.INFO, message, context)


def log_warning(message: str, **context: Any) -> None:
    """Log warnings safely."""
    _log_with_context("project-service.warning", logging.WARNING, message, context)


def log_error(message: str, **context: Any) -> None:
    """Log errors safely."""
    _log_with_context("project-service.error", logging.ERROR, message, context)


def _log_with_context(logger_name: str, level: int, message: str, context: Dict[str, Any]) -> None:
    logger = get_logger(logger_name)
    safe_context = _sanitize_context(context)
    if safe_context:
        logger.log(level, "%s | context=%s", message, json.dumps(safe_context))
    else:
        logger.log(level, "%s", message)


def _sanitize_context(context: Dict[str, Any]) -> Dict[str, Any]:
    safe: Dict[str, Any] = {}
    for key, value in context.items():
        if _SECRET_KEY_PATTERN.search(key):
            safe[key] = "***redacted***"
        else:
            safe[key] = value
    return safe


def _redact_message(message: str) -> str:
    return _SECRET_KEY_PATTERN.sub("***redacted***", message)


def _redact_args(args: Any) -> Any:
    if isinstance(args, dict):
        return _sanitize_context(args)
    if isinstance(args, tuple):
        return tuple(_redact_message(str(item)) for item in args)
    return _redact_message(str(args))
