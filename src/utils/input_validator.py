"""
Input Validator Module

This module provides functions for validating input data.
"""

import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)


def validate_input(input_data: Dict[str, Any]) -> bool:
    """
    Validate the input data.
    
    Args:
        input_data: Input data to validate
        
    Returns:
        True if the input is valid, False otherwise
    """
    # Check if the input is a dictionary
    if not isinstance(input_data, dict):
        logger.error("Input data is not a dictionary")
        return False
    
    # Check if the required fields are present
    required_fields = ['feedback_id', 'feedback_text']
    for field in required_fields:
        if field not in input_data:
            logger.error(f"Required field '{field}' is missing")
            return False
    
    # Check if the feedback_id is a string
    if not isinstance(input_data['feedback_id'], str):
        logger.error("feedback_id must be a string")
        return False
    
    # Check if the feedback_text is a string
    if not isinstance(input_data['feedback_text'], str):
        logger.error("feedback_text must be a string")
        return False
    
    # Check if the feedback_text is not empty
    if not input_data['feedback_text'].strip():
        logger.error("feedback_text cannot be empty")
        return False
    
    # Check if the optional fields have the correct types
    if 'customer_name' in input_data and not isinstance(input_data['customer_name'], str):
        logger.error("customer_name must be a string")
        return False
    
    if 'timestamp' in input_data and not isinstance(input_data['timestamp'], str):
        logger.error("timestamp must be a string")
        return False
    
    if 'instructions' in input_data and not isinstance(input_data['instructions'], str):
        logger.error("instructions must be a string")
        return False
    
    # All checks passed
    return True


def validate_batch_input(input_data: Dict[str, Any]) -> bool:
    """
    Validate a batch of input data.
    
    Args:
        input_data: Batch input data to validate
        
    Returns:
        True if the input is valid, False otherwise
    """
    # Check if the input is a dictionary
    if not isinstance(input_data, dict):
        logger.error("Batch input data is not a dictionary")
        return False
    
    # Check if the feedback field is present
    if 'feedback' not in input_data:
        logger.error("Required field 'feedback' is missing")
        return False
    
    # Check if the feedback field is a list
    if not isinstance(input_data['feedback'], list):
        logger.error("feedback must be a list")
        return False
    
    # Check if the feedback list is not empty
    if not input_data['feedback']:
        logger.error("feedback list cannot be empty")
        return False
    
    # Validate each feedback entry
    for i, feedback in enumerate(input_data['feedback']):
        if not validate_input(feedback):
            logger.error(f"Invalid feedback entry at index {i}")
            return False
    
    # All checks passed
    return True
