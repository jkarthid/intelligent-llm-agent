"""
Tests for the Agent Factory Module
"""

import unittest
from unittest.mock import patch, MagicMock

import pytest

from src.agents.agent_factory import AgentFactory
from src.agents.interaction_agent import InteractionAgent
from src.agents.tool_agent import ToolAgent


class TestAgentFactory:
    """Tests for the AgentFactory class."""

    def setup_method(self):
        """Set up the test environment."""
        # Create the agent factory
        self.agent_factory = AgentFactory(provider='openai', model='gpt-4')

    def test_create_interaction_agent(self):
        """Test creating an interaction agent."""
        # Create the agent
        agent = self.agent_factory.create_agent('interaction')
        
        # Check the agent
        assert isinstance(agent, InteractionAgent)
        assert agent.provider == 'openai'
        assert agent.model == 'gpt-4'

    def test_create_tool_agent(self):
        """Test creating a tool agent."""
        # Create the agent
        agent = self.agent_factory.create_agent('tool')
        
        # Check the agent
        assert isinstance(agent, ToolAgent)
        assert agent.provider == 'openai'
        assert agent.model == 'gpt-4'

    def test_create_unknown_agent(self):
        """Test creating an unknown agent."""
        # Try to create an unknown agent
        with pytest.raises(ValueError) as excinfo:
            self.agent_factory.create_agent('unknown_agent')
        
        # Check the error message
        assert "Unknown agent type: unknown_agent" in str(excinfo.value)

    def test_create_agent_with_custom_config(self):
        """Test creating an agent with custom configuration."""
        # Create custom configuration
        config = {
            'temperature': 0.5,
            'max_tokens': 500
        }
        
        # Create the agent
        agent = self.agent_factory.create_agent('interaction', **config)
        
        # Check the agent
        assert isinstance(agent, InteractionAgent)
        assert agent.provider == 'openai'
        assert agent.model == 'gpt-4'
        assert agent.temperature == 0.5
        assert agent.max_tokens == 500

    def test_create_agent_with_different_provider(self):
        """Test creating an agent with a different provider."""
        # Create the agent factory with a different provider
        agent_factory = AgentFactory(provider='anthropic', model='claude-3-opus')
        
        # Create the agent
        agent = agent_factory.create_agent('interaction')
        
        # Check the agent
        assert isinstance(agent, InteractionAgent)
        assert agent.provider == 'anthropic'
        assert agent.model == 'claude-3-opus'
