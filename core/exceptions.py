"""Custom exception handler for standardized API error responses."""
import logging
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
from django.core.exceptions import ValidationError as DjangoValidationError
from django.http import Http404

logger = logging.getLogger(__name__)


def custom_exception_handler(exc, context):
    """Standardize error responses and log with context."""
    # Get the standard DRF error response
    response = exception_handler(exc, context)

    # If DRF didn't handle it, handle Django exceptions
    if response is None:
        if isinstance(exc, DjangoValidationError):
            response = Response(
                {'detail': str(exc)},
                status=status.HTTP_400_BAD_REQUEST
            )
        elif isinstance(exc, Http404):
            response = Response(
                {'detail': 'Not found.'},
                status=status.HTTP_404_NOT_FOUND
            )

    # Log the error with context
    if response is not None:
        request = context.get('request')
        view = context.get('view')

        log_data = {
            'status_code': response.status_code,
            'error_type': exc.__class__.__name__,
            'error_message': str(exc),
            'path': request.path if request else None,
            'method': request.method if request else None,
            'view': view.__class__.__name__ if view else None,
        }

        # Add user context if available
        if request and hasattr(request, 'user') and request.user.is_authenticated:
            log_data['user_id'] = request.user.id

        # Log at appropriate level based on status code
        if 400 <= response.status_code < 500:
            # Client errors - log as warning (not our fault)
            logger.warning(
                f"Client error: {exc.__class__.__name__}",
                extra=log_data
            )
        elif response.status_code >= 500:
            # Server errors - log as error (our fault)
            logger.error(
                f"Server error: {exc.__class__.__name__}",
                extra=log_data,
                exc_info=True  # Include stack trace
            )

        # Standardize error response format
        error_data = {
            'error': {
                'message': _get_error_message(exc, response),
                'code': _get_error_code(exc),
                'status': response.status_code,
            }
        }

        # Include field-specific errors if available (validation errors)
        if isinstance(response.data, dict) and len(response.data) > 1:
            error_data['error']['details'] = response.data

        response.data = error_data

    return response


def _get_error_message(exc, response):
    """
    Extract user-friendly error message from exception.

    Args:
        exc: The exception
        response: The DRF response object

    Returns:
        User-friendly error message string
    """
    # For validation errors, use the first error message
    if hasattr(response, 'data') and isinstance(response.data, dict):
        if 'detail' in response.data:
            return str(response.data['detail'])
        # Get first field error
        for field, errors in response.data.items():
            if isinstance(errors, list) and len(errors) > 0:
                return f"{field}: {errors[0]}"

    return str(exc)


def _get_error_code(exc):
    """
    Get error code from exception.

    This allows clients to programmatically handle specific errors.

    Args:
        exc: The exception

    Returns:
        String error code
    """
    # Map exception types to error codes
    error_codes = {
        'ValidationError': 'VALIDATION_ERROR',
        'PermissionDenied': 'PERMISSION_DENIED',
        'NotAuthenticated': 'NOT_AUTHENTICATED',
        'AuthenticationFailed': 'AUTHENTICATION_FAILED',
        'NotFound': 'NOT_FOUND',
        'MethodNotAllowed': 'METHOD_NOT_ALLOWED',
        'Throttled': 'RATE_LIMIT_EXCEEDED',
        'ParseError': 'PARSE_ERROR',
    }

    exc_class_name = exc.__class__.__name__
    return error_codes.get(exc_class_name, 'INTERNAL_ERROR')
