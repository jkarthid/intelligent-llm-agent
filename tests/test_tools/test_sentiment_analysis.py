"""
Tests for the Sentiment Analysis Tool Module
"""

import json
import unittest
from unittest.mock import patch, MagicMock

import pytest

from src.tools.sentiment_analysis import SentimentAnalysisTool


class TestSentimentAnalysisTool:
    """Tests for the SentimentAnalysisTool class."""

    def setup_method(self):
        """Set up the test environment."""
        # Create a mock client for the LLM
        self.mock_client = MagicMock()
        
        # Create a mock response for the LLM
        self.mock_response = MagicMock()
        self.mock_response.choices = [MagicMock()]
        self.mock_response.choices[0].message.content = json.dumps({
            "overall_sentiment": "positive",
            "scores": {
                "positive": 0.8,
                "negative": 0.1,
                "neutral": 0.1
            },
            "explanation": "The text expresses satisfaction with the product but mentions a minor issue."
        })
        
        # Create the sentiment analysis tool with the mock client
        with patch('openai.OpenAI', return_value=self.mock_client):
            self.tool = SentimentAnalysisTool(provider='openai', model='gpt-4')
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
        assert result['overall_sentiment'] == 'positive'
        assert result['scores']['positive'] == 0.8
        assert result['scores']['negative'] == 0.1
        assert result['scores']['neutral'] == 0.1
        assert result['explanation'] == 'The text expresses satisfaction with the product but mentions a minor issue.'
        
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
            "overall_sentiment": "positive",
            # missing scores
            "explanation": "The text expresses satisfaction with the product but mentions a minor issue."
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

    def test_execute_with_anthropic(self):
        """Test the execute method with Anthropic provider."""
        # Create a mock client for Anthropic
        mock_anthropic = MagicMock()
        
        # Create a mock response for Anthropic
        mock_anthropic.messages.create.return_value = MagicMock(
            content=[MagicMock(text=json.dumps({
                "overall_sentiment": "positive",
                "scores": {
                    "positive": 0.8,
                    "negative": 0.1,
                    "neutral": 0.1
                },
                "explanation": "The text expresses satisfaction with the product but mentions a minor issue."
            }))]
        )
        
        # Create the sentiment analysis tool with the mock client
        with patch('anthropic.Anthropic', return_value=mock_anthropic):
            tool = SentimentAnalysisTool(provider='anthropic', model='claude-3-opus')
            tool.client = mock_anthropic
        
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
        assert result['overall_sentiment'] == 'positive'
        assert result['scores']['positive'] == 0.8
        assert result['scores']['negative'] == 0.1
        assert result['scores']['neutral'] == 0.1
        assert result['explanation'] == 'The text expresses satisfaction with the product but mentions a minor issue.'
