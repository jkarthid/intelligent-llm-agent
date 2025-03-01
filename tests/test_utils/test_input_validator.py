"""
Tests for the Input Validator Module
"""

import unittest

import pytest

from src.utils.input_validator import validate_input, validate_batch_input


class TestInputValidator:
    """Tests for the input validator functions."""

    def test_validate_input_valid(self):
        """Test validate_input with valid input."""
        # Create valid input data
        input_data = {
            'feedback_id': '12345',
            'feedback_text': 'This is a valid feedback text.',
            'customer_name': 'John Doe',
            'timestamp': '2025-01-10T10:30:00Z',
            'instructions': 'Focus on sentiment analysis.'
        }
        
        # Validate the input
        result = validate_input(input_data)
        
        # Check the result
        assert result is True

    def test_validate_input_not_dict(self):
        """Test validate_input with input that is not a dictionary."""
        # Create invalid input data
        input_data = 'not a dictionary'
        
        # Validate the input
        result = validate_input(input_data)
        
        # Check the result
        assert result is False

    def test_validate_input_missing_required_field(self):
        """Test validate_input with input missing a required field."""
        # Create input data missing a required field
        input_data = {
            'feedback_id': '12345',
            # missing feedback_text
            'customer_name': 'John Doe',
            'timestamp': '2025-01-10T10:30:00Z'
        }
        
        # Validate the input
        result = validate_input(input_data)
        
        # Check the result
        assert result is False

    def test_validate_input_invalid_feedback_id_type(self):
        """Test validate_input with invalid feedback_id type."""
        # Create input data with invalid feedback_id type
        input_data = {
            'feedback_id': 12345,  # should be a string
            'feedback_text': 'This is a valid feedback text.',
            'customer_name': 'John Doe',
            'timestamp': '2025-01-10T10:30:00Z'
        }
        
        # Validate the input
        result = validate_input(input_data)
        
        # Check the result
        assert result is False

    def test_validate_input_invalid_feedback_text_type(self):
        """Test validate_input with invalid feedback_text type."""
        # Create input data with invalid feedback_text type
        input_data = {
            'feedback_id': '12345',
            'feedback_text': 12345,  # should be a string
            'customer_name': 'John Doe',
            'timestamp': '2025-01-10T10:30:00Z'
        }
        
        # Validate the input
        result = validate_input(input_data)
        
        # Check the result
        assert result is False

    def test_validate_input_empty_feedback_text(self):
        """Test validate_input with empty feedback_text."""
        # Create input data with empty feedback_text
        input_data = {
            'feedback_id': '12345',
            'feedback_text': '',  # empty string
            'customer_name': 'John Doe',
            'timestamp': '2025-01-10T10:30:00Z'
        }
        
        # Validate the input
        result = validate_input(input_data)
        
        # Check the result
        assert result is False

    def test_validate_input_invalid_customer_name_type(self):
        """Test validate_input with invalid customer_name type."""
        # Create input data with invalid customer_name type
        input_data = {
            'feedback_id': '12345',
            'feedback_text': 'This is a valid feedback text.',
            'customer_name': 12345,  # should be a string
            'timestamp': '2025-01-10T10:30:00Z'
        }
        
        # Validate the input
        result = validate_input(input_data)
        
        # Check the result
        assert result is False

    def test_validate_input_invalid_timestamp_type(self):
        """Test validate_input with invalid timestamp type."""
        # Create input data with invalid timestamp type
        input_data = {
            'feedback_id': '12345',
            'feedback_text': 'This is a valid feedback text.',
            'customer_name': 'John Doe',
            'timestamp': 12345  # should be a string
        }
        
        # Validate the input
        result = validate_input(input_data)
        
        # Check the result
        assert result is False

    def test_validate_input_invalid_instructions_type(self):
        """Test validate_input with invalid instructions type."""
        # Create input data with invalid instructions type
        input_data = {
            'feedback_id': '12345',
            'feedback_text': 'This is a valid feedback text.',
            'customer_name': 'John Doe',
            'timestamp': '2025-01-10T10:30:00Z',
            'instructions': 12345  # should be a string
        }
        
        # Validate the input
        result = validate_input(input_data)
        
        # Check the result
        assert result is False

    def test_validate_batch_input_valid(self):
        """Test validate_batch_input with valid input."""
        # Create valid batch input data
        input_data = {
            'feedback': [
                {
                    'feedback_id': '12345',
                    'feedback_text': 'This is a valid feedback text.',
                    'customer_name': 'John Doe',
                    'timestamp': '2025-01-10T10:30:00Z'
                },
                {
                    'feedback_id': '67890',
                    'feedback_text': 'This is another valid feedback text.',
                    'customer_name': 'Jane Smith',
                    'timestamp': '2025-01-11T14:20:00Z'
                }
            ]
        }
        
        # Validate the batch input
        result = validate_batch_input(input_data)
        
        # Check the result
        assert result is True

    def test_validate_batch_input_not_dict(self):
        """Test validate_batch_input with input that is not a dictionary."""
        # Create invalid batch input data
        input_data = 'not a dictionary'
        
        # Validate the batch input
        result = validate_batch_input(input_data)
        
        # Check the result
        assert result is False

    def test_validate_batch_input_missing_feedback_field(self):
        """Test validate_batch_input with input missing the feedback field."""
        # Create batch input data missing the feedback field
        input_data = {
            'not_feedback': []
        }
        
        # Validate the batch input
        result = validate_batch_input(input_data)
        
        # Check the result
        assert result is False

    def test_validate_batch_input_feedback_not_list(self):
        """Test validate_batch_input with feedback that is not a list."""
        # Create batch input data with feedback that is not a list
        input_data = {
            'feedback': 'not a list'
        }
        
        # Validate the batch input
        result = validate_batch_input(input_data)
        
        # Check the result
        assert result is False

    def test_validate_batch_input_empty_feedback_list(self):
        """Test validate_batch_input with an empty feedback list."""
        # Create batch input data with an empty feedback list
        input_data = {
            'feedback': []
        }
        
        # Validate the batch input
        result = validate_batch_input(input_data)
        
        # Check the result
        assert result is False

    def test_validate_batch_input_invalid_feedback_entry(self):
        """Test validate_batch_input with an invalid feedback entry."""
        # Create batch input data with an invalid feedback entry
        input_data = {
            'feedback': [
                {
                    'feedback_id': '12345',
                    'feedback_text': 'This is a valid feedback text.',
                    'customer_name': 'John Doe',
                    'timestamp': '2025-01-10T10:30:00Z'
                },
                {
                    'feedback_id': '67890',
                    # missing feedback_text
                    'customer_name': 'Jane Smith',
                    'timestamp': '2025-01-11T14:20:00Z'
                }
            ]
        }
        
        # Validate the batch input
        result = validate_batch_input(input_data)
        
        # Check the result
        assert result is False
