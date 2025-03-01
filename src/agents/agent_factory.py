"""
Agent Factory Module

This module is responsible for creating and configuring different types of agents
based on the requirements and configuration.
"""

import os
from typing import Dict, Any, Optional

from .interaction_agent import InteractionAgent
from .tool_agent import ToolAgent


class AgentFactory:
    """Factory class for creating different types of agents."""

    @staticmethod
    def create_agent(agent_type: str, config: Optional[Dict[str, Any]] = None) -> Any:
        """
        Create an agent of the specified type with the given configuration.

        Args:
            agent_type: Type of agent to create ('interaction' or 'tool')
            config: Configuration dictionary for the agent

        Returns:
            An instance of the requested agent type
        
        Raises:
            ValueError: If an unsupported agent type is requested
        """
        if config is None:
            config = {}

        # Get LLM API keys from environment variables if not provided in config
        if 'api_key' not in config:
            # Try to get from environment variables based on provider
            provider = config.get('provider', 'openai')
            if provider == 'openai':
                config['api_key'] = os.environ.get('OPENAI_API_KEY')
            elif provider == 'anthropic':
                config['api_key'] = os.environ.get('ANTHROPIC_API_KEY')
            elif provider == 'bedrock':
                # AWS credentials are handled by boto3
                pass
            elif provider == 'groq':
                config['api_key'] = os.environ.get('GROQ_API_KEY')

        if agent_type.lower() == 'interaction':
            return InteractionAgent(**config)
        elif agent_type.lower() == 'tool':
            return ToolAgent(**config)
        else:
            raise ValueError(f"Unsupported agent type: {agent_type}")
