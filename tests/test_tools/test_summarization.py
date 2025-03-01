"""
Tests for the Summarization Tool Module
"""

import json
import unittest
from unittest.mock import patch, MagicMock

import pytest

from src.tools.summarization import SummarizationTool


class TestSummarizationTool:
    """Tests for the SummarizationTool class."""

    def setup_method(self):
        """Set up the test environment."""
        # Create a mock client for the LLM
        self.mock_client = MagicMock()
        
        # Create a mock response for the LLM
        self.mock_response = MagicMock()
        self.mock_response.choices = [MagicMock()]
        self.mock_response.choices[0].message.content = json.dumps({
            "summary": "Customer is satisfied with the product quality but experienced delivery delays, which caused frustration.",
            "recommendations": [
                "Improve delivery logistics to reduce delays",
                "Proactively communicate shipping status to customers"
            ],
            "key_points": [
                "Product quality is good",
                "Delivery was delayed",
                "Customer experienced frustration"
            ]
        })
        
        # Create the summarization tool with the mock client
        with patch('openai.OpenAI', return_value=self.mock_client):
            self.tool = SummarizationTool(provider='openai', model='gpt-4')
            self.tool.client = self.mock_client
            self.tool.client.chat.completions.create.return_value = self.mock_response

    def test_execute(self):
        """Test the execute method."""
        # Create a test input
        input_data = {
            'feedback_id': '12345',
            'customer_name': 'John Doe',
            'feedback_text': 'The product is great, but the delivery was delayed.',
            'timestamp': '2025-01-10T10:30:00Z'
        }
        
        # Execute the tool
        result = self.tool.execute(input_data)
        
        # Check the result
        assert result['summary'] == 'Customer is satisfied with the product quality but experienced delivery delays, which caused frustration.'
        assert len(result['recommendations']) == 2
        assert result['recommendations'][0] == 'Improve delivery logistics to reduce delays'
        assert len(result['key_points']) == 3
        assert result['key_points'][0] == 'Product quality is good'
        
        # Check that the LLM was called with the correct arguments
        self.tool.client.chat.completions.create.assert_called_once()
        call_args = self.tool.client.chat.completions.create.call_args[1]
        assert call_args['model'] == 'gpt-4'
        assert len(call_args['messages']) == 2
        assert call_args['messages'][0]['role'] == 'system'
        assert call_args['messages'][1]['role'] == 'user'
        assert 'The product is great, but the delivery was delayed.' in call_args['messages'][1]['content']

    def test_execute_with_empty_feedback(self):
        """Test the execute method with empty feedback."""
        # Create a test input with empty feedback
        input_data = {
            'feedback_id': '12345',
            'customer_name': 'John Doe',
            'feedback_text': '',
            'timestamp': '2025-01-10T10:30:00Z'
        }
        
        # Execute the tool
        with pytest.raises(ValueError) as excinfo:
            self.tool.execute(input_data)
        
        # Check the error message
        assert "Feedback text cannot be empty" in str(excinfo.value)

    def test_execute_with_invalid_response(self):
        """Test the execute method with an invalid response from the LLM."""
        # Configure the mock to return an invalid response
        self.mock_response.choices[0].message.content = "Invalid JSON"
        
        # Create a test input
        input_data = {
            'feedback_id': '12345',
            'customer_name': 'John Doe',
            'feedback_text': 'The product is great, but the delivery was delayed.',
            'timestamp': '2025-01-10T10:30:00Z'
        }
        
        # Execute the tool
        with pytest.raises(ValueError) as excinfo:
            self.tool.execute(input_data)
        
        # Check the error message
        assert "Failed to parse LLM response" in str(excinfo.value)

    def test_execute_with_missing_fields(self):
        """Test the execute method with a response missing required fields."""
        # Configure the mock to return a response missing required fields
        self.mock_response.choices[0].message.content = json.dumps({
            "summary": "Customer is satisfied with the product quality but experienced delivery delays, which caused frustration.",
            # missing recommendations
            "key_points": [
                "Product quality is good",
                "Delivery was delayed",
                "Customer experienced frustration"
            ]
        })
        
        # Create a test input
        input_data = {
            'feedback_id': '12345',
            'customer_name': 'John Doe',
            'feedback_text': 'The product is great, but the delivery was delayed.',
            'timestamp': '2025-01-10T10:30:00Z'
        }
        
        # Execute the tool
        with pytest.raises(ValueError) as excinfo:
            self.tool.execute(input_data)
        
        # Check the error message
        assert "LLM response is missing required fields" in str(excinfo.value)

    def test_execute_with_groq(self):
        """Test the execute method with Groq provider."""
        # Create a mock client for Groq
        mock_groq = MagicMock()
        
        # Create a mock response for Groq
        mock_groq.chat.completions.create.return_value = MagicMock(
            choices=[MagicMock(
                message=MagicMock(
                    content=json.dumps({
                        "summary": "Customer is satisfied with the product quality but experienced delivery delays, which caused frustration.",
                        "recommendations": [
                            "Improve delivery logistics to reduce delays",
                            "Proactively communicate shipping status to customers"
                        ],
                        "key_points": [
                            "Product quality is good",
                            "Delivery was delayed",
                            "Customer experienced frustration"
                        ]
                    })
                )
            )]
        )
        
        # Create the summarization tool with the mock client
        with patch('groq.Groq', return_value=mock_groq):
            tool = SummarizationTool(provider='groq', model='llama3-70b-8192')
            tool.client = mock_groq
        
        # Create a test input
        input_data = {
            'feedback_id': '12345',
            'customer_name': 'John Doe',
            'feedback_text': 'The product is great, but the delivery was delayed.',
            'timestamp': '2025-01-10T10:30:00Z'
        }
        
        # Execute the tool
        result = tool.execute(input_data)
        
        # Check the result
        assert result['summary'] == 'Customer is satisfied with the product quality but experienced delivery delays, which caused frustration.'
        assert len(result['recommendations']) == 2
        assert result['recommendations'][0] == 'Improve delivery logistics to reduce delays'
        assert len(result['key_points']) == 3
        assert result['key_points'][0] == 'Product quality is good'
