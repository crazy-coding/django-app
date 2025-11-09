from rest_framework.views import exception_handler
from rest_framework.response import Response
from django.core.exceptions import ValidationError
from django.http import Http404
from rest_framework import status

def custom_exception_handler(exc, context):
    """
    Custom exception handler for REST framework that handles additional exceptions
    and provides more detailed error responses.
    """
    
    # First call REST framework's default exception handler
    response = exception_handler(exc, context)
    
    # If response is None, we need to handle the exception ourselves
    if response is None:
        if isinstance(exc, ValidationError):
            return Response({
                'error': 'Validation Error',
                'detail': exc.message_dict if hasattr(exc, 'message_dict') else str(exc),
                'code': 'validation_error'
            }, status=status.HTTP_400_BAD_REQUEST)
            
        elif isinstance(exc, Http404):
            return Response({
                'error': 'Not Found',
                'detail': str(exc),
                'code': 'not_found'
            }, status=status.HTTP_404_NOT_FOUND)
            
        else:
            # Unhandled exceptions
            return Response({
                'error': 'Internal Server Error',
                'detail': str(exc),
                'code': 'server_error'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    # Add additional information to the error response
    if isinstance(response.data, dict):
        response.data = {
            'error': response.status_text,
            'detail': response.data,
            'code': response.status_code
        }
    
    return response