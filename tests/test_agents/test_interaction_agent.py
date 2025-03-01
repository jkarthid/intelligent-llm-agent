"""
Tests for the Interaction Agent Module
"""

import json
import unittest
from unittest.mock import patch, MagicMock

import pytest

from src.agents.interaction_agent import InteractionAgent


class TestInteractionAgent:
    """Tests for the InteractionAgent class."""

    def setup_method(self):
        """Set up the test environment."""
        # Create a mock client for the LLM
        self.mock_client = MagicMock()
        
        # Create a mock response for the LLM
        self.mock_response = MagicMock()
        self.mock_response.choices = [MagicMock()]
        self.mock_response.choices[0].message.content = json.dumps(["sentiment_analysis", "summarization"])
        
        # Create the interaction agent with the mock client
        with patch('openai.OpenAI', return_value=self.mock_client):
            self.agent = InteractionAgent(provider='openai', model='gpt-4')
            self.agent.client = self.mock_client
            self.agent.client.chat.completions.create.return_value = self.mock_response

    def test_process_input(self):
        """Test the process_input method."""
        # Create a test input
        input_data = {
            'feedback_id': '12345',
            'customer_name': 'John Doe',
            'feedback_text': 'The product is great, but the delivery was delayed.',
            'timestamp': '2025-01-10T10:30:00Z',
            'instructions': 'Focus on identifying the sentiment and summarizing actionable insights.'
        }
        
        # Process the input
        result = self.agent.process_input(input_data)
        
        # Check the result
        assert result['feedback_id'] == '12345'
        assert 'processed_input' in result
        assert 'tools_to_execute' in result
        assert len(result['tools_to_execute']) > 0

    def test_apply_guardrails(self):
        """Test the _apply_guardrails method."""
        # Create a test input
        input_data = {
            'feedback_id': '12345',
            'customer_name': 'John Doe',
            'feedback_text': 'The product is great, but the delivery was delayed.',
            'timestamp': '2025-01-10T10:30:00Z',
            'instructions': 'Focus on identifying the sentiment and summarizing actionable insights.'
        }
        
        # Apply guardrails
        result = self.agent._apply_guardrails(input_data)
        
        # Check the result
        assert result == input_data  # Guardrails should not modify the input in this case

    def test_determine_tools_with_instructions(self):
        """Test the _determine_tools method with instructions."""
        # Create a test input
        input_data = {
            'feedback_id': '12345',
            'customer_name': 'John Doe',
            'feedback_text': 'The product is great, but the delivery was delayed.',
            'timestamp': '2025-01-10T10:30:00Z'
        }
        
        # Set up the mock response
        self.mock_response.choices[0].message.content = json.dumps(["sentiment_analysis", "summarization"])
        
        # Determine tools with instructions
        tools = self.agent._determine_tools('Focus on identifying the sentiment and summarizing actionable insights.', input_data)
        
        # Check the result
        assert len(tools) == 2
        assert 'sentiment_analysis' in tools
        assert 'summarization' in tools

    def test_determine_tools_without_instructions(self):
        """Test the _determine_tools method without instructions."""
        # Create a test input
        input_data = {
            'feedback_id': '12345',
            'customer_name': 'John Doe',
            'feedback_text': 'The product is great, but the delivery was delayed.',
            'timestamp': '2025-01-10T10:30:00Z'
        }
        
        # Determine tools without instructions
        tools = self.agent._determine_tools('', input_data)
        
        # Check the result
        assert len(tools) == 4
        assert 'sentiment_analysis' in tools
        assert 'topic_categorization' in tools
        assert 'keyword_contextualization' in tools
        assert 'summarization' in tools

    def test_query_llm_for_tool_selection(self):
        """Test the _query_llm_for_tool_selection method."""
        # Set up the mock response
        self.mock_response.choices[0].message.content = json.dumps(["sentiment_analysis", "summarization"])
        
        # Query the LLM for tool selection
        tools = self.agent._query_llm_for_tool_selection('Test prompt')
        
        # Check the result
        assert len(tools) == 2
        assert 'sentiment_analysis' in tools
        assert 'summarization' in tools
        
        # Check that the LLM was called with the correct arguments
        self.agent.client.chat.completions.create.assert_called_once()
        call_args = self.agent.client.chat.completions.create.call_args[1]
        assert call_args['model'] == 'gpt-4'
        assert len(call_args['messages']) == 2
        assert call_args['messages'][0]['role'] == 'system'
        assert call_args['messages'][1]['role'] == 'user'
        assert call_args['messages'][1]['content'] == 'Test prompt'
