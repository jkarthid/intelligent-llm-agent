"""
Tool Agent Module

This module implements the tool agent that is responsible for executing
various tools based on the instructions and input data.
"""

import json
import logging
from typing import Dict, Any, List, Optional

import openai
import anthropic
import boto3
import groq

from ..tools.tool_factory import ToolFactory
from ..cache.cache_manager import CacheManager

logger = logging.getLogger(__name__)


class ToolAgent:
    """
    Agent responsible for executing various tools based on instructions.
    
    This agent receives instructions from the interaction agent and
    executes the appropriate tools to process the input data.
    """

    def __init__(self, provider: str = 'openai', model: str = None, 
                 api_key: str = None, use_cache: bool = True, **kwargs):
        """
        Initialize the tool agent.
        
        Args:
            provider: LLM provider ('openai', 'anthropic', 'bedrock', or 'groq')
            model: Model name to use
            api_key: API key for the provider
            use_cache: Whether to use caching
            **kwargs: Additional configuration options
        """
        self.provider = provider.lower()
        self.model = model
        self.api_key = api_key
        self.use_cache = use_cache
        
        # Set default models based on provider
        if not self.model:
            if self.provider == 'openai':
                self.model = 'gpt-4'
            elif self.provider == 'anthropic':
                self.model = 'claude-3-opus-20240229'
            elif self.provider == 'bedrock':
                self.model = 'anthropic.claude-3-sonnet-20240229'
            elif self.provider == 'groq':
                self.model = 'llama3-70b-8192'
        
        # Initialize the client based on the provider
        self._initialize_client()
        
        # Initialize the tool factory
        self.tool_factory = ToolFactory(provider=self.provider, model=self.model, 
                                       api_key=self.api_key)
        
        # Initialize the cache manager if caching is enabled
        if self.use_cache:
            self.cache_manager = CacheManager(**kwargs.get('cache_config', {}))

    def _initialize_client(self):
        """Initialize the appropriate LLM client based on the provider."""
        if self.provider == 'openai':
            if self.api_key:
                self.client = openai.OpenAI(api_key=self.api_key)
            else:
                self.client = openai.OpenAI()
        elif self.provider == 'anthropic':
            if self.api_key:
                self.client = anthropic.Anthropic(api_key=self.api_key)
            else:
                self.client = anthropic.Anthropic()
        elif self.provider == 'bedrock':
            self.client = boto3.client('bedrock-runtime')
        elif self.provider == 'groq':
            if self.api_key:
                self.client = groq.Groq(api_key=self.api_key)
            else:
                self.client = groq.Groq()
        else:
            raise ValueError(f"Unsupported provider: {self.provider}")

    def process_request(self, input_data: Dict[str, Any], 
                       tools_to_execute: List[str]) -> Dict[str, Any]:
        """
        Process the request by executing the specified tools.
        
        Args:
            input_data: Dictionary containing the input data
            tools_to_execute: List of tools to execute
            
        Returns:
            Dictionary containing the results of the tool executions
        """
        # Log the incoming request
        logger.info(f"Processing request with tools: {tools_to_execute}")
        
        # Check cache if enabled
        if self.use_cache:
            cache_key = self._generate_cache_key(input_data, tools_to_execute)
            cached_result = self.cache_manager.get(cache_key)
            
            if cached_result:
                logger.info(f"Cache hit for key: {cache_key}")
                return cached_result
            
            logger.info(f"Cache miss for key: {cache_key}")
        
        # Initialize results dictionary
        results = {
            'feedback_id': input_data.get('feedback_id', ''),
            'results': {}
        }
        
        # Execute each tool
        for tool_name in tools_to_execute:
            try:
                tool = self.tool_factory.create_tool(tool_name)
                tool_result = tool.execute(input_data)
                results['results'][tool_name] = tool_result
            except Exception as e:
                logger.error(f"Error executing tool {tool_name}: {str(e)}")
                results['results'][tool_name] = {'error': str(e)}
        
        # Cache the results if caching is enabled
        if self.use_cache:
            self.cache_manager.set(cache_key, results)
        
        return results

    def _generate_cache_key(self, input_data: Dict[str, Any], 
                           tools_to_execute: List[str]) -> str:
        """
        Generate a cache key based on the input data and tools to execute.
        
        Args:
            input_data: Dictionary containing the input data
            tools_to_execute: List of tools to execute
            
        Returns:
            Cache key as a string
        """
        # Extract the relevant parts of the input data for the cache key
        cache_data = {
            'feedback_text': input_data.get('feedback_text', ''),
            'instructions': input_data.get('instructions', ''),
            'tools': sorted(tools_to_execute)
        }
        
        # Convert to JSON string and generate hash
        cache_json = json.dumps(cache_data, sort_keys=True)
        
        # In a real implementation, we would use a proper hashing function
        # For simplicity, we'll just return the JSON string
        # In production, use something like:
        # import hashlib
        # return hashlib.sha256(cache_json.encode()).hexdigest()
        
        import hashlib
        return hashlib.sha256(cache_json.encode()).hexdigest()
