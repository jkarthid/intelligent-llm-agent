"""
Tests for the Lambda Handler Module
"""

import json
import unittest
from unittest.mock import patch, MagicMock

import pytest

from src.aws.lambda_handler import lambda_handler


class TestLambdaHandler:
    """Tests for the lambda_handler function."""

    def setup_method(self):
        """Set up the test environment."""
        # Create mock objects
        self.mock_agent_factory = MagicMock()
        self.mock_interaction_agent = MagicMock()
        self.mock_tool_agent = MagicMock()
        
        # Configure the mock agent factory
        self.mock_agent_factory.create_agent.side_effect = lambda agent_type, **kwargs: {
            'interaction': self.mock_interaction_agent,
            'tool': self.mock_tool_agent
        }.get(agent_type)
        
        # Configure the mock interaction agent
        self.mock_interaction_agent.process_input.return_value = {
            'feedback_id': '12345',
            'processed_input': {
                'feedback_id': '12345',
                'feedback_text': 'The product is great, but the delivery was delayed.',
                'customer_name': 'John Doe',
                'timestamp': '2025-01-10T10:30:00Z'
            },
            'tools_to_execute': ['sentiment_analysis', 'summarization']
        }
        
        # Configure the mock tool agent
        self.mock_tool_agent.process_request.return_value = {
            'feedback_id': '12345',
            'results': {
                'sentiment_analysis': {
                    'overall_sentiment': 'positive',
                    'scores': {
                        'positive': 0.8,
                        'negative': 0.1,
                        'neutral': 0.1
                    },
                    'explanation': 'The text expresses satisfaction with the product but mentions a minor issue.'
                },
                'summarization': {
                    'summary': 'Customer is satisfied with the product quality but experienced delivery delays, which caused frustration.',
                    'recommendations': [
                        'Improve delivery logistics to reduce delays',
                        'Proactively communicate shipping status to customers'
                    ],
                    'key_points': [
                        'Product quality is good',
                        'Delivery was delayed',
                        'Customer experienced frustration'
                    ]
                }
            }
        }
        
        # Create the patch for the agent factory
        self.agent_factory_patch = patch('src.agents.agent_factory.AgentFactory', return_value=self.mock_agent_factory)
        self.agent_factory_patch.start()

    def teardown_method(self):
        """Tear down the test environment."""
        # Stop the patch
        self.agent_factory_patch.stop()

    def test_lambda_handler_single_feedback(self):
        """Test the lambda_handler function with a single feedback entry."""
        # Create a test event
        event = {
            'feedback_id': '12345',
            'customer_name': 'John Doe',
            'feedback_text': 'The product is great, but the delivery was delayed.',
            'timestamp': '2025-01-10T10:30:00Z',
            'instructions': 'Focus on identifying the sentiment and summarizing actionable insights.'
        }
        
        # Call the lambda handler
        response = lambda_handler(event, {})
        
        # Check the response
        assert response['statusCode'] == 200
        
        # Parse the response body
        body = json.loads(response['body'])
        
        # Check the body
        assert body['feedback_id'] == '12345'
        assert 'results' in body
        assert 'sentiment_analysis' in body['results']
        assert 'summarization' in body['results']
        
        # Check that the agents were called
        self.mock_interaction_agent.process_input.assert_called_once()
        self.mock_tool_agent.process_request.assert_called_once()

    def test_lambda_handler_batch_feedback(self):
        """Test the lambda_handler function with a batch of feedback entries."""
        # Create a test event
        event = {
            'feedback': [
                {
                    'feedback_id': '12345',
                    'customer_name': 'John Doe',
                    'feedback_text': 'The product is great, but the delivery was delayed.',
                    'timestamp': '2025-01-10T10:30:00Z',
                    'instructions': 'Focus on identifying the sentiment and summarizing actionable insights.'
                },
                {
                    'feedback_id': '67890',
                    'customer_name': 'Jane Smith',
                    'feedback_text': 'I love the product, it works perfectly.',
                    'timestamp': '2025-01-11T14:20:00Z'
                }
            ]
        }
        
        # Call the lambda handler
        response = lambda_handler(event, {})
        
        # Check the response
        assert response['statusCode'] == 200
        
        # Parse the response body
        body = json.loads(response['body'])
        
        # Check the body
        assert 'results' in body
        assert len(body['results']) == 2
        assert body['results'][0]['feedback_id'] == '12345'
        assert body['results'][1]['feedback_id'] == '12345'  # Mock returns the same ID
        
        # Check that the agents were called twice
        assert self.mock_interaction_agent.process_input.call_count == 2
        assert self.mock_tool_agent.process_request.call_count == 2

    def test_lambda_handler_invalid_input(self):
        """Test the lambda_handler function with invalid input."""
        # Create a test event with missing required fields
        event = {
            'customer_name': 'John Doe',
            'timestamp': '2025-01-10T10:30:00Z'
        }
        
        # Call the lambda handler
        response = lambda_handler(event, {})
        
        # Check the response
        assert response['statusCode'] == 400
        
        # Parse the response body
        body = json.loads(response['body'])
        
        # Check the body
        assert 'error' in body
        
        # Check that the agents were not called
        self.mock_interaction_agent.process_input.assert_not_called()
        self.mock_tool_agent.process_request.assert_not_called()

    def test_lambda_handler_exception(self):
        """Test the lambda_handler function when an exception occurs."""
        # Configure the mock interaction agent to raise an exception
        self.mock_interaction_agent.process_input.side_effect = Exception('Test exception')
        
        # Create a test event
        event = {
            'feedback_id': '12345',
            'customer_name': 'John Doe',
            'feedback_text': 'The product is great, but the delivery was delayed.',
            'timestamp': '2025-01-10T10:30:00Z'
        }
        
        # Call the lambda handler
        response = lambda_handler(event, {})
        
        # Check the response
        assert response['statusCode'] == 500
        
        # Parse the response body
        body = json.loads(response['body'])
        
        # Check the body
        assert 'error' in body
        assert body['error'] == 'Test exception'
        
        # Check that the interaction agent was called but not the tool agent
        self.mock_interaction_agent.process_input.assert_called_once()
        self.mock_tool_agent.process_request.assert_not_called()
