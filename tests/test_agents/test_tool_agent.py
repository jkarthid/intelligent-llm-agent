"""
Tests for the Tool Agent Module
"""

import json
import unittest
from unittest.mock import patch, MagicMock

import pytest

from src.agents.tool_agent import ToolAgent


class TestToolAgent:
    """Tests for the ToolAgent class."""

    def setup_method(self):
        """Set up the test environment."""
        # Create mock objects
        self.mock_tool_factory = MagicMock()
        self.mock_cache_manager = MagicMock()
        self.mock_sentiment_tool = MagicMock()
        self.mock_summarization_tool = MagicMock()
        
        # Configure the mock tool factory
        self.mock_tool_factory.create_tool.side_effect = lambda tool_type: {
            'sentiment_analysis': self.mock_sentiment_tool,
            'summarization': self.mock_summarization_tool
        }.get(tool_type)
        
        # Configure the mock tools
        self.mock_sentiment_tool.execute.return_value = {
            'overall_sentiment': 'positive',
            'scores': {
                'positive': 0.8,
                'negative': 0.1,
                'neutral': 0.1
            },
            'explanation': 'The text expresses satisfaction with the product but mentions a minor issue.'
        }
        
        self.mock_summarization_tool.execute.return_value = {
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
        
        # Create the tool agent with the mock objects
        with patch('src.tools.tool_factory.ToolFactory', return_value=self.mock_tool_factory):
            with patch('src.cache.cache_manager.CacheManager', return_value=self.mock_cache_manager):
                self.agent = ToolAgent(provider='openai', model='gpt-4')
                self.agent.tool_factory = self.mock_tool_factory
                self.agent.cache_manager = self.mock_cache_manager

    def test_process_request_without_cache(self):
        """Test the process_request method without cache."""
        # Configure the cache manager to return None (cache miss)
        self.mock_cache_manager.get.return_value = None
        
        # Create a test input
        input_data = {
            'feedback_id': '12345',
            'customer_name': 'John Doe',
            'feedback_text': 'The product is great, but the delivery was delayed.',
            'timestamp': '2025-01-10T10:30:00Z',
            'instructions': 'Focus on identifying the sentiment and summarizing actionable insights.'
        }
        
        # Process the request
        result = self.agent.process_request(input_data, ['sentiment_analysis', 'summarization'])
        
        # Check the result
        assert result['feedback_id'] == '12345'
        assert 'results' in result
        assert 'sentiment_analysis' in result['results']
        assert 'summarization' in result['results']
        assert result['results']['sentiment_analysis']['overall_sentiment'] == 'positive'
        assert 'summary' in result['results']['summarization']
        
        # Check that the tools were called
        self.mock_sentiment_tool.execute.assert_called_once_with(input_data)
        self.mock_summarization_tool.execute.assert_called_once_with(input_data)
        
        # Check that the cache was checked and set
        self.mock_cache_manager.get.assert_called_once()
        self.mock_cache_manager.set.assert_called_once()

    def test_process_request_with_cache(self):
        """Test the process_request method with cache."""
        # Configure the cache manager to return a cached result
        cached_result = {
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
        self.mock_cache_manager.get.return_value = cached_result
        
        # Create a test input
        input_data = {
            'feedback_id': '12345',
            'customer_name': 'John Doe',
            'feedback_text': 'The product is great, but the delivery was delayed.',
            'timestamp': '2025-01-10T10:30:00Z',
            'instructions': 'Focus on identifying the sentiment and summarizing actionable insights.'
        }
        
        # Process the request
        result = self.agent.process_request(input_data, ['sentiment_analysis', 'summarization'])
        
        # Check the result
        assert result == cached_result
        
        # Check that the tools were not called
        self.mock_sentiment_tool.execute.assert_not_called()
        self.mock_summarization_tool.execute.assert_not_called()
        
        # Check that the cache was checked but not set
        self.mock_cache_manager.get.assert_called_once()
        self.mock_cache_manager.set.assert_not_called()

    def test_generate_cache_key(self):
        """Test the _generate_cache_key method."""
        # Create a test input
        input_data = {
            'feedback_id': '12345',
            'customer_name': 'John Doe',
            'feedback_text': 'The product is great, but the delivery was delayed.',
            'timestamp': '2025-01-10T10:30:00Z',
            'instructions': 'Focus on identifying the sentiment and summarizing actionable insights.'
        }
        
        # Generate a cache key
        key1 = self.agent._generate_cache_key(input_data, ['sentiment_analysis', 'summarization'])
        
        # Check that the key is a string
        assert isinstance(key1, str)
        
        # Generate another key with the same input but different tool order
        key2 = self.agent._generate_cache_key(input_data, ['summarization', 'sentiment_analysis'])
        
        # Check that the keys are the same (tool order should not matter)
        assert key1 == key2
        
        # Generate another key with different input
        input_data2 = input_data.copy()
        input_data2['feedback_text'] = 'Different feedback text'
        key3 = self.agent._generate_cache_key(input_data2, ['sentiment_analysis', 'summarization'])
        
        # Check that the keys are different
        assert key1 != key3
