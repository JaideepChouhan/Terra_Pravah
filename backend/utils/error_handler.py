"""
Terra Pravah - Comprehensive Error Handling Utilities
======================================================
Provides error handling, logging, and user-friendly error messages for the entire pipeline.
"""

import logging
import traceback
import sys
from functools import wraps
from typing import Any, Callable, Dict, Optional, Type
from datetime import datetime
from flask import jsonify, current_app
import json

logger = logging.getLogger(__name__)


class TerraPravahError(Exception):
    """Base exception for Terra Pravah."""
    
    def __init__(
        self,
        message: str,
        error_code: str = "UNKNOWN_ERROR",
        http_status: int = 500,
        details: Optional[Dict[str, Any]] = None,
        user_message: Optional[str] = None
    ):
        """
        Initialize Terra Pravah error.
        
        Args:
            message: Internal error message (logged)
            error_code: Machine-readable error code
            http_status: HTTP status code
            details: Additional diagnostic details
            user_message: User-friendly message (shown to frontend)
        """
        self.message = message
        self.error_code = error_code
        self.http_status = http_status
        self.details = details or {}
        self.user_message = user_message or message
        self.timestamp = datetime.utcnow().isoformat()
        super().__init__(message)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert error to dictionary for JSON response."""
        return {
            'error': self.error_code,
            'message': self.user_message,
            'details': self.details,
            'timestamp': self.timestamp
        }


class FileUploadError(TerraPravahError):
    """File upload validation and processing errors."""
    
    def __init__(
        self,
        message: str,
        file_name: str = "",
        file_size_mb: float = 0,
        max_size_mb: float = 5000,
        user_message: Optional[str] = None
    ):
        details = {
            'file_name': file_name,
            'file_size_mb': file_size_mb,
            'max_size_mb': max_size_mb,
            'error_type': 'file_upload'
        }
        
        user_msg = user_message or (
            f"File upload failed: {message}. "
            f"Maximum file size is {max_size_mb}MB."
        )
        
        super().__init__(
            message=message,
            error_code='FILE_UPLOAD_ERROR',
            http_status=400,
            details=details,
            user_message=user_msg
        )


class DTMBuildError(TerraPravahError):
    """DTM generation and AI model errors."""
    
    def __init__(
        self,
        message: str,
        stage: str = "unknown",
        file_name: str = "",
        user_message: Optional[str] = None
    ):
        details = {
            'stage': stage,
            'file_name': file_name,
            'error_type': 'dtm_build'
        }
        
        stage_names = {
            'ai_classification': 'AI ground classification',
            'interpolation': 'DTM interpolation',
            'conditioning': 'Hydrological conditioning',
            'validation': 'DTM validation',
            'cog_conversion': 'Cloud Optimized GeoTIFF conversion'
        }
        
        stage_msg = stage_names.get(stage, stage)
        user_msg = user_message or (
            f"DTM generation failed during {stage_msg}: {message}. "
            f"Please check your input file and try again."
        )
        
        super().__init__(
            message=message,
            error_code='DTM_BUILD_ERROR',
            http_status=500,
            details=details,
            user_message=user_msg
        )


class DrainageAnalysisError(TerraPravahError):
    """Drainage analysis and processing errors."""
    
    def __init__(
        self,
        message: str,
        stage: str = "unknown",
        user_message: Optional[str] = None
    ):
        details = {
            'stage': stage,
            'error_type': 'drainage_analysis'
        }
        
        stage_names = {
            'terrain_load': 'terrain loading',
            'hydrology': 'hydrological analysis',
            'network_extraction': 'drainage network extraction',
            'outlet_identification': 'outlet identification',
            'visualization': 'visualization creation',
            'export': 'data export'
        }
        
        stage_msg = stage_names.get(stage, stage)
        user_msg = user_message or (
            f"Drainage analysis failed during {stage_msg}: {message}"
        )
        
        super().__init__(
            message=message,
            error_code='DRAINAGE_ANALYSIS_ERROR',
            http_status=500,
            details=details,
            user_message=user_msg
        )


class ValidationError(TerraPravahError):
    """Data validation errors."""
    
    def __init__(
        self,
        message: str,
        field: str = "",
        invalid_value: Any = None,
        user_message: Optional[str] = None
    ):
        details = {
            'field': field,
            'invalid_value': str(invalid_value) if invalid_value is not None else None,
            'error_type': 'validation'
        }
        
        user_msg = user_message or f"Validation error: {message}"
        
        super().__init__(
            message=message,
            error_code='VALIDATION_ERROR',
            http_status=400,
            details=details,
            user_message=user_msg
        )


class ResourceNotFoundError(TerraPravahError):
    """Resource not found errors."""
    
    def __init__(
        self,
        resource_type: str,
        resource_id: str,
        user_message: Optional[str] = None
    ):
        details = {
            'resource_type': resource_type,
            'resource_id': resource_id,
            'error_type': 'not_found'
        }
        
        user_msg = user_message or f"{resource_type} '{resource_id}' not found."
        
        super().__init__(
            message=f"{resource_type} not found: {resource_id}",
            error_code='RESOURCE_NOT_FOUND',
            http_status=404,
            details=details,
            user_message=user_msg
        )


class PermissionError(TerraPravahError):
    """Permission and authorization errors."""
    
    def __init__(
        self,
        message: str = "Access denied",
        resource_type: str = "resource",
        user_message: Optional[str] = None
    ):
        details = {
            'error_type': 'permission',
            'resource_type': resource_type
        }
        
        user_msg = user_message or f"You don't have permission to access this {resource_type}."
        
        super().__init__(
            message=message,
            error_code='PERMISSION_DENIED',
            http_status=403,
            details=details,
            user_message=user_msg
        )


def handle_errors(
    error_stage: str = "request_processing",
    log_traceback: bool = True,
    return_json: bool = True
):
    """
    Decorator for comprehensive error handling in Flask routes.
    
    Args:
        error_stage: Description of what was being done (for error reporting)
        log_traceback: Whether to log full traceback
        return_json: Whether to return JSON error response
        
    Example:
        @handle_errors(error_stage="DTM generation", log_traceback=True)
        def build_dtm():
            ...
    """
    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def wrapper(*args, **kwargs) -> Any:
            try:
                return f(*args, **kwargs)
                
            except TerraPravahError as e:
                # Custom Terra Pravah errors
                logger.error(
                    f"{error_stage} - {e.error_code}: {e.message}",
                    extra={'error_code': e.error_code}
                )
                
                if log_traceback:
                    logger.debug(f"Traceback: {traceback.format_exc()}")
                
                if return_json:
                    response = e.to_dict()
                    return jsonify(response), e.http_status
                raise
                
            except FileNotFoundError as e:
                error = TerraPravahError(
                    message=f"File not found: {str(e)}",
                    error_code='FILE_NOT_FOUND',
                    http_status=404,
                    user_message="The requested file was not found. Please check the file path."
                )
                
                logger.error(f"{error_stage} - FILE_NOT_FOUND: {str(e)}")
                if log_traceback:
                    logger.debug(f"Traceback: {traceback.format_exc()}")
                
                if return_json:
                    return jsonify(error.to_dict()), 404
                raise error
                
            except ValueError as e:
                error = ValidationError(
                    message=f"Invalid value: {str(e)}",
                    user_message="Invalid input data. Please check your parameters."
                )
                
                logger.error(f"{error_stage} - VALIDATION_ERROR: {str(e)}")
                
                if return_json:
                    return jsonify(error.to_dict()), 400
                raise error
                
            except MemoryError as e:
                error = TerraPravahError(
                    message=f"Out of memory: {str(e)}",
                    error_code='OUT_OF_MEMORY',
                    http_status=503,
                    user_message="The processing exceeded available memory. Try with smaller files or lower resolution."
                )
                
                logger.error(f"{error_stage} - OUT_OF_MEMORY: {str(e)}")
                
                if return_json:
                    return jsonify(error.to_dict()), 503
                raise error
                
            except Exception as e:
                # Unexpected errors
                error_type = type(e).__name__
                error = TerraPravahError(
                    message=f"{error_type}: {str(e)}",
                    error_code='INTERNAL_ERROR',
                    http_status=500,
                    details={'exception_type': error_type},
                    user_message="An unexpected error occurred. Our team has been notified. Please try again later."
                )
                
                logger.error(
                    f"{error_stage} - INTERNAL_ERROR: {error_type}: {str(e)}",
                    exc_info=True
                )
                
                if return_json:
                    # Don't expose internal details in production
                    response = {
                        'error': error.error_code,
                        'message': error.user_message,
                        'timestamp': error.timestamp
                    }
                    return jsonify(response), 500
                raise error
                
        return wrapper
    return decorator


def log_operation(operation_name: str, log_level: int = logging.INFO):
    """
    Decorator for logging operation start/completion.
    
    Args:
        operation_name: Name of the operation
        log_level: Logging level
    """
    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def wrapper(*args, **kwargs) -> Any:
            logger.log(log_level, f"Starting: {operation_name}")
            start_time = datetime.utcnow()
            
            try:
                result = f(*args, **kwargs)
                elapsed = (datetime.utcnow() - start_time).total_seconds()
                logger.log(log_level, f"Completed: {operation_name} ({elapsed:.2f}s)")
                return result
                
            except Exception as e:
                elapsed = (datetime.utcnow() - start_time).total_seconds()
                logger.error(
                    f"Failed: {operation_name} ({elapsed:.2f}s) - {type(e).__name__}: {str(e)}",
                    exc_info=True
                )
                raise
                
        return wrapper
    return decorator


class ErrorLogger:
    """Context manager for logging operation details."""
    
    def __init__(
        self,
        operation: str,
        user_id: Optional[str] = None,
        resource_id: Optional[str] = None
    ):
        """
        Initialize error logger.
        
        Args:
            operation: Description of operation
            user_id: User performing operation
            resource_id: Resource being operated on
        """
        self.operation = operation
        self.user_id = user_id
        self.resource_id = resource_id
        self.start_time = None
        
    def __enter__(self):
        self.start_time = datetime.utcnow()
        logger.info(
            f"Starting: {self.operation}",
            extra={
                'user_id': self.user_id,
                'resource_id': self.resource_id
            }
        )
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        elapsed = (datetime.utcnow() - self.start_time).total_seconds()
        
        if exc_type is None:
            logger.info(
                f"Completed: {self.operation} ({elapsed:.2f}s)",
                extra={
                    'user_id': self.user_id,
                    'resource_id': self.resource_id,
                    'elapsed_seconds': elapsed
                }
            )
        else:
            logger.error(
                f"Failed: {self.operation} ({elapsed:.2f}s) - {exc_type.__name__}: {str(exc_val)}",
                extra={
                    'user_id': self.user_id,
                    'resource_id': self.resource_id,
                    'elapsed_seconds': elapsed,
                    'exception_type': exc_type.__name__
                },
                exc_info=True
            )
        
        return False  # Don't suppress exceptions


def configure_logging(app):
    """
    Configure comprehensive logging for the application.
    
    Args:
        app: Flask application instance
    """
    # Remove default handlers
    app.logger.handlers.clear()
    
    # Log level from config
    log_level = getattr(app.config, 'LOG_LEVEL', 'INFO')
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, log_level))
    
    formatter = logging.Formatter(
        '%(asctime)s [%(levelname)s] %(name)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(formatter)
    
    # Add handlers to app logger and root logger
    app.logger.addHandler(console_handler)
    app.logger.setLevel(getattr(logging, log_level))
    
    logging.getLogger().addHandler(console_handler)
    logging.getLogger().setLevel(getattr(logging, log_level))
    
    app.logger.info(f"Logging configured at level {log_level}")
