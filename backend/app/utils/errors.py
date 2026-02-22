"""
Comprehensive Error Handling Utilities
Centralized error handling with logging and user-friendly messages
"""
from fastapi import HTTPException, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from pydantic import ValidationError
import logging
import traceback
from typing import Union, Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)


class MindCareException(Exception):
    """Base exception for MindCare AI"""
    def __init__(
        self,
        message: str,
        status_code: int = 500,
        error_code: str = "INTERNAL_ERROR",
        details: Dict[str, Any] = None
    ):
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        self.details = details or {}
        super().__init__(self.message)


class AuthenticationError(MindCareException):
    """Authentication related errors"""
    def __init__(self, message: str = "Authentication failed", details: Dict = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_401_UNAUTHORIZED,
            error_code="AUTH_ERROR",
            details=details
        )


class AuthorizationError(MindCareException):
    """Authorization/Permission errors"""
    def __init__(self, message: str = "Insufficient permissions", details: Dict = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_403_FORBIDDEN,
            error_code="AUTHORIZATION_ERROR",
            details=details
        )


class ValidationException(MindCareException):
    """Data validation errors"""
    def __init__(self, message: str = "Validation failed", details: Dict = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_400_BAD_REQUEST,
            error_code="VALIDATION_ERROR",
            details=details
        )


class DatabaseError(MindCareException):
    """Database operation errors"""
    def __init__(self, message: str = "Database error occurred", details: Dict = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error_code="DATABASE_ERROR",
            details=details
        )


class AIServiceError(MindCareException):
    """AI/LLM service errors"""
    def __init__(self, message: str = "AI service error", details: Dict = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            error_code="AI_SERVICE_ERROR",
            details=details
        )


class ResourceNotFoundError(MindCareException):
    """Resource not found errors"""
    def __init__(self, resource: str = "Resource", details: Dict = None):
        super().__init__(
            message=f"{resource} not found",
            status_code=status.HTTP_404_NOT_FOUND,
            error_code="NOT_FOUND",
            details=details
        )


class RateLimitError(MindCareException):
    """Rate limit exceeded errors"""
    def __init__(self, message: str = "Rate limit exceeded", details: Dict = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            error_code="RATE_LIMIT_EXCEEDED",
            details=details
        )


def create_error_response(
    error: Exception,
    request: Request = None,
    include_trace: bool = False
) -> Dict[str, Any]:
    """
    Create standardized error response
    
    Args:
        error: The exception that occurred
        request: FastAPI request object (optional)
        include_trace: Whether to include stack trace (development only)
    
    Returns:
        Standardized error response dictionary
    """
    response = {
        "status": "error",
        "timestamp": datetime.utcnow().isoformat(),
        "error": {
            "message": str(error),
            "type": error.__class__.__name__,
        }
    }
    
    # Add error code for custom exceptions
    if isinstance(error, MindCareException):
        response["error"]["code"] = error.error_code
        response["error"]["details"] = error.details
    
    # Add request info if available
    if request:
        response["path"] = str(request.url.path)
        response["method"] = request.method
    
    # Add stack trace in development
    if include_trace:
        response["error"]["trace"] = traceback.format_exc()
    
    return response


async def mindcare_exception_handler(request: Request, exc: MindCareException):
    """Handler for custom MindCare exceptions"""
    logger.error(
        f"MindCare Exception: {exc.error_code} - {exc.message}",
        extra={
            "error_code": exc.error_code,
            "status_code": exc.status_code,
            "path": request.url.path,
            "method": request.method,
            "details": exc.details
        }
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content=create_error_response(exc, request)
    )


async def http_exception_handler(request: Request, exc: HTTPException):
    """Handler for FastAPI HTTP exceptions"""
    logger.warning(
        f"HTTP Exception: {exc.status_code} - {exc.detail}",
        extra={
            "status_code": exc.status_code,
            "path": request.url.path,
            "method": request.method
        }
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "status": "error",
            "timestamp": datetime.utcnow().isoformat(),
            "path": str(request.url.path),
            "method": request.method,
            "error": {
                "message": exc.detail,
                "type": "HTTPException",
                "code": f"HTTP_{exc.status_code}"
            }
        }
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handler for Pydantic validation errors"""
    errors = []
    for error in exc.errors():
        errors.append({
            "field": ".".join(str(x) for x in error["loc"]),
            "message": error["msg"],
            "type": error["type"]
        })
    
    logger.warning(
        f"Validation Error: {len(errors)} validation errors",
        extra={
            "path": request.url.path,
            "method": request.method,
            "errors": errors
        }
    )
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "status": "error",
            "timestamp": datetime.utcnow().isoformat(),
            "path": str(request.url.path),
            "method": request.method,
            "error": {
                "message": "Validation failed",
                "type": "ValidationError",
                "code": "VALIDATION_ERROR",
                "errors": errors
            }
        }
    )


async def database_exception_handler(request: Request, exc: SQLAlchemyError):
    """Handler for database errors"""
    error_message = "Database error occurred"
    
    # Specific handling for integrity errors
    if isinstance(exc, IntegrityError):
        error_message = "Data integrity violation. This record may already exist."
    
    logger.error(
        f"Database Error: {str(exc)}",
        extra={
            "path": request.url.path,
            "method": request.method,
            "error_type": exc.__class__.__name__
        },
        exc_info=True
    )
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "status": "error",
            "timestamp": datetime.utcnow().isoformat(),
            "path": str(request.url.path),
            "method": request.method,
            "error": {
                "message": error_message,
                "type": "DatabaseError",
                "code": "DATABASE_ERROR"
            }
        }
    )


async def generic_exception_handler(request: Request, exc: Exception):
    """Handler for unexpected exceptions"""
    logger.critical(
        f"Unexpected Error: {str(exc)}",
        extra={
            "path": request.url.path,
            "method": request.method,
            "error_type": exc.__class__.__name__
        },
        exc_info=True
    )
    
    # Don't expose internal errors in production
    from app.config import settings
    if settings.ENVIRONMENT == "production":
        error_message = "An internal error occurred. Please contact support."
    else:
        error_message = str(exc)
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "status": "error",
            "timestamp": datetime.utcnow().isoformat(),
            "path": str(request.url.path),
            "method": request.method,
            "error": {
                "message": error_message,
                "type": exc.__class__.__name__,
                "code": "INTERNAL_ERROR"
            }
        }
    )


def register_error_handlers(app):
    """
    Register all error handlers with FastAPI app
    
    Usage:
        from app.utils.errors import register_error_handlers
        register_error_handlers(app)
    """
    app.add_exception_handler(MindCareException, mindcare_exception_handler)
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(SQLAlchemyError, database_exception_handler)
    app.add_exception_handler(Exception, generic_exception_handler)
    
    logger.info("Error handlers registered successfully")


# Utility functions for common error scenarios

def handle_database_error(error: Exception, operation: str = "database operation"):
    """
    Convert database errors to user-friendly exceptions
    
    Args:
        error: The database exception
        operation: Description of the operation that failed
    """
    if isinstance(error, IntegrityError):
        raise DatabaseError(
            message=f"Data integrity violation during {operation}",
            details={"operation": operation}
        )
    else:
        raise DatabaseError(
            message=f"Database error during {operation}",
            details={"operation": operation}
        )


def handle_ai_service_error(error: Exception, service: str = "AI service"):
    """
    Convert AI service errors to user-friendly exceptions
    
    Args:
        error: The AI service exception
        service: Name of the AI service
    """
    raise AIServiceError(
        message=f"{service} is currently unavailable. Using fallback.",
        details={"service": service, "error": str(error)}
    )


def require_resource(resource: Any, resource_type: str, resource_id: str = None):
    """
    Raise exception if resource is None
    
    Args:
        resource: The resource to check
        resource_type: Type of resource (e.g., "Patient", "Therapist")
        resource_id: Optional ID of the resource
    
    Raises:
        ResourceNotFoundError if resource is None
    """
    if resource is None:
        details = {"type": resource_type}
        if resource_id:
            details["id"] = resource_id
        raise ResourceNotFoundError(
            resource=resource_type,
            details=details
        )
    return resource


# Context manager for safe database operations
class safe_database_operation:
    """
    Context manager for safe database operations with automatic error handling
    
    Usage:
        with safe_database_operation(db, "creating patient"):
            patient = Patient(**data)
            db.add(patient)
            db.commit()
    """
    def __init__(self, db_session, operation: str):
        self.db_session = db_session
        self.operation = operation
    
    def __enter__(self):
        return self.db_session
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            self.db_session.rollback()
            logger.error(f"Database operation failed: {self.operation}", exc_info=True)
            handle_database_error(exc_val, self.operation)
            return False
        return True


# Decorator for endpoint error handling
def handle_errors(operation: str = "operation"):
    """
    Decorator for automatic error handling in endpoints
    
    Usage:
        @router.post("/patients")
        @handle_errors("creating patient")
        async def create_patient(...):
            ...
    """
    def decorator(func):
        async def wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except MindCareException:
                raise  # Re-raise our custom exceptions
            except HTTPException:
                raise  # Re-raise HTTP exceptions
            except SQLAlchemyError as e:
                handle_database_error(e, operation)
            except Exception as e:
                logger.error(f"Unexpected error in {operation}: {str(e)}", exc_info=True)
                raise MindCareException(
                    message=f"Error during {operation}",
                    status_code=500,
                    error_code="OPERATION_FAILED"
                )
        return wrapper
    return decorator
