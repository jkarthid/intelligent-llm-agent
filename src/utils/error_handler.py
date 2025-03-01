"""
Error Handler Module

This module provides functions for handling errors.
"""

import logging
import traceback
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


def handle_error(error: Exception, feedback_id: str = 'unknown') -> Dict[str, Any]:
    """
    Handle an error and return an appropriate response.
    
    Args:
        error: The exception that occurred
        feedback_id: ID of the feedback being processed
        
    Returns:
        Dictionary containing error information
    """
    # Log the error
    logger.error(f"Error processing feedback {feedback_id}: {str(error)}")
    logger.error(traceback.format_exc())
    
    # Determine the error type
    error_type = type(error).__name__
    
    # Create the error response
    error_response = {
        'feedback_id': feedback_id,
        'error': str(error),
        'error_type': error_type
    }
    
    # Add additional information based on the error type
    if error_type == 'ValueError':
        error_response['suggestion'] = 'Check the input format and values'
    elif error_type == 'KeyError':
        error_response['suggestion'] = 'Check that all required fields are present'
    elif error_type == 'ClientError':
        error_response['suggestion'] = 'Check AWS credentials and permissions'
    elif error_type == 'JSONDecodeError':
        error_response['suggestion'] = 'Check that the input is valid JSON'
    else:
        error_response['suggestion'] = 'Check the logs for more information'
    
    return error_response


def format_error_for_response(error: Exception, status_code: int = 500) -> Dict[str, Any]:
    """
    Format an error for an HTTP response.
    
    Args:
        error: The exception that occurred
        status_code: HTTP status code
        
    Returns:
        Dictionary containing the HTTP response
    """
    # Create the error response
    error_response = {
        'error': str(error),
        'error_type': type(error).__name__
    }
    
    # Return the formatted response
    return {
        'statusCode': status_code,
        'headers': {
            'Content-Type': 'application/json'
        },
        'body': error_response
    }
