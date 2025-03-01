"""
Tests for the Error Handler Module
"""

import json
import unittest
from unittest.mock import patch

import pytest
from botocore.exceptions import ClientError

from src.utils.error_handler import handle_error, format_error_for_response


class TestErrorHandler:
    """Tests for the error handler functions."""

    def test_handle_error_value_error(self):
        """Test handle_error with a ValueError."""
        # Create a ValueError
        error = ValueError("Invalid value")
        
        # Handle the error
        result = handle_error(error, feedback_id="12345")
        
        # Check the result
        assert result['feedback_id'] == "12345"
        assert result['error'] == "Invalid value"
        assert result['error_type'] == "ValueError"
        assert result['suggestion'] == "Check the input format and values"

    def test_handle_error_key_error(self):
        """Test handle_error with a KeyError."""
        # Create a KeyError
        error = KeyError("missing_key")
        
        # Handle the error
        result = handle_error(error, feedback_id="12345")
        
        # Check the result
        assert result['feedback_id'] == "12345"
        assert "missing_key" in result['error']
        assert result['error_type'] == "KeyError"
        assert result['suggestion'] == "Check that all required fields are present"

    def test_handle_error_client_error(self):
        """Test handle_error with a ClientError."""
        # Create a ClientError
        error = ClientError(
            {'Error': {'Code': 'ResourceNotFoundException', 'Message': 'Resource not found'}},
            'GetItem'
        )
        
        # Handle the error
        result = handle_error(error, feedback_id="12345")
        
        # Check the result
        assert result['feedback_id'] == "12345"
        assert "ResourceNotFoundException" in result['error']
        assert result['error_type'] == "ClientError"
        assert result['suggestion'] == "Check AWS credentials and permissions"

    def test_handle_error_json_decode_error(self):
        """Test handle_error with a JSONDecodeError."""
        # Create a JSONDecodeError
        error = json.JSONDecodeError("Expecting property name enclosed in double quotes", "", 0)
        
        # Handle the error
        result = handle_error(error, feedback_id="12345")
        
        # Check the result
        assert result['feedback_id'] == "12345"
        assert "Expecting property name" in result['error']
        assert result['error_type'] == "JSONDecodeError"
        assert result['suggestion'] == "Check that the input is valid JSON"

    def test_handle_error_generic_exception(self):
        """Test handle_error with a generic Exception."""
        # Create a generic Exception
        error = Exception("Something went wrong")
        
        # Handle the error
        result = handle_error(error, feedback_id="12345")
        
        # Check the result
        assert result['feedback_id'] == "12345"
        assert result['error'] == "Something went wrong"
        assert result['error_type'] == "Exception"
        assert result['suggestion'] == "Check the logs for more information"

    def test_handle_error_unknown_feedback_id(self):
        """Test handle_error with an unknown feedback ID."""
        # Create an error
        error = ValueError("Invalid value")
        
        # Handle the error with the default feedback ID
        result = handle_error(error)
        
        # Check the result
        assert result['feedback_id'] == "unknown"
        assert result['error'] == "Invalid value"
        assert result['error_type'] == "ValueError"

    def test_format_error_for_response(self):
        """Test format_error_for_response."""
        # Create an error
        error = ValueError("Invalid value")
        
        # Format the error for response
        result = format_error_for_response(error, status_code=400)
        
        # Check the result
        assert result['statusCode'] == 400
        assert result['headers']['Content-Type'] == 'application/json'
        assert result['body']['error'] == "Invalid value"
        assert result['body']['error_type'] == "ValueError"

    def test_format_error_for_response_default_status_code(self):
        """Test format_error_for_response with the default status code."""
        # Create an error
        error = ValueError("Invalid value")
        
        # Format the error for response
        result = format_error_for_response(error)
        
        # Check the result
        assert result['statusCode'] == 500
        assert result['headers']['Content-Type'] == 'application/json'
        assert result['body']['error'] == "Invalid value"
        assert result['body']['error_type'] == "ValueError"
