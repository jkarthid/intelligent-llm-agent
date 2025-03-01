"""
Tool Factory Module

This module is responsible for creating and configuring different tools
based on the requirements and configuration.
"""

from typing import Dict, Any, Optional

from .sentiment_analysis import SentimentAnalysisTool
from .topic_categorization import TopicCategorizationTool
from .keyword_contextualization import KeywordContextualizationTool
from .summarization import SummarizationTool


class ToolFactory:
    """Factory class for creating different types of tools."""

    def __init__(self, provider: str = 'openai', model: str = None, 
                 api_key: str = None, **kwargs):
        """
        Initialize the tool factory.
        
        Args:
            provider: LLM provider ('openai', 'anthropic', 'bedrock', or 'groq')
            model: Model name to use
            api_key: API key for the provider
            **kwargs: Additional configuration options
        """
        self.provider = provider
        self.model = model
        self.api_key = api_key
        self.kwargs = kwargs

    def create_tool(self, tool_type: str) -> Any:
        """
        Create a tool of the specified type.

        Args:
            tool_type: Type of tool to create

        Returns:
            An instance of the requested tool type
        
        Raises:
            ValueError: If an unsupported tool type is requested
        """
        # Common configuration for all tools
        config = {
            'provider': self.provider,
            'model': self.model,
            'api_key': self.api_key,
            **self.kwargs
        }
        
        # Create the appropriate tool based on the type
        if tool_type == 'sentiment_analysis':
            return SentimentAnalysisTool(**config)
        elif tool_type == 'topic_categorization':
            return TopicCategorizationTool(**config)
        elif tool_type == 'keyword_contextualization':
            return KeywordContextualizationTool(**config)
        elif tool_type == 'summarization':
            return SummarizationTool(**config)
        else:
            raise ValueError(f"Unsupported tool type: {tool_type}")
