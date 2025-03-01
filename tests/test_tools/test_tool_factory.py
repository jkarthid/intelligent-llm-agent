"""
Tests for the Tool Factory Module
"""

import unittest
from unittest.mock import patch, MagicMock

import pytest

from src.tools.tool_factory import ToolFactory
from src.tools.sentiment_analysis import SentimentAnalysisTool
from src.tools.topic_categorization import TopicCategorizationTool
from src.tools.keyword_contextualization import KeywordContextualizationTool
from src.tools.summarization import SummarizationTool


class TestToolFactory:
    """Tests for the ToolFactory class."""

    def setup_method(self):
        """Set up the test environment."""
        # Create the tool factory
        self.tool_factory = ToolFactory(provider='openai', model='gpt-4')

    def test_create_sentiment_analysis_tool(self):
        """Test creating a sentiment analysis tool."""
        # Create the tool
        tool = self.tool_factory.create_tool('sentiment_analysis')
        
        # Check the tool
        assert isinstance(tool, SentimentAnalysisTool)
        assert tool.provider == 'openai'
        assert tool.model == 'gpt-4'

    def test_create_topic_categorization_tool(self):
        """Test creating a topic categorization tool."""
        # Create the tool
        tool = self.tool_factory.create_tool('topic_categorization')
        
        # Check the tool
        assert isinstance(tool, TopicCategorizationTool)
        assert tool.provider == 'openai'
        assert tool.model == 'gpt-4'

    def test_create_keyword_contextualization_tool(self):
        """Test creating a keyword contextualization tool."""
        # Create the tool
        tool = self.tool_factory.create_tool('keyword_contextualization')
        
        # Check the tool
        assert isinstance(tool, KeywordContextualizationTool)
        assert tool.provider == 'openai'
        assert tool.model == 'gpt-4'

    def test_create_summarization_tool(self):
        """Test creating a summarization tool."""
        # Create the tool
        tool = self.tool_factory.create_tool('summarization')
        
        # Check the tool
        assert isinstance(tool, SummarizationTool)
        assert tool.provider == 'openai'
        assert tool.model == 'gpt-4'

    def test_create_unknown_tool(self):
        """Test creating an unknown tool."""
        # Try to create an unknown tool
        with pytest.raises(ValueError) as excinfo:
            self.tool_factory.create_tool('unknown_tool')
        
        # Check the error message
        assert "Unknown tool type: unknown_tool" in str(excinfo.value)

    def test_create_tool_with_custom_config(self):
        """Test creating a tool with custom configuration."""
        # Create custom configuration
        config = {
            'temperature': 0.5,
            'max_tokens': 500
        }
        
        # Create the tool
        tool = self.tool_factory.create_tool('sentiment_analysis', **config)
        
        # Check the tool
        assert isinstance(tool, SentimentAnalysisTool)
        assert tool.provider == 'openai'
        assert tool.model == 'gpt-4'
        assert tool.temperature == 0.5
        assert tool.max_tokens == 500
