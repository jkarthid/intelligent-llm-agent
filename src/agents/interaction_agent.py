"""
Interaction Agent Module

This module implements the interaction agent that handles user interactions
and applies guardrails to ensure safe and appropriate responses.
"""

import json
import logging
from typing import Dict, Any, List, Optional

import openai
import anthropic
import boto3
import groq

logger = logging.getLogger(__name__)


class InteractionAgent:
    """
    Agent responsible for handling user interactions and applying guardrails.
    
    This agent acts as the first point of contact for user requests and ensures
    that all interactions adhere to safety guidelines and policies.
    """

    def __init__(self, provider: str = 'openai', model: str = None, 
                 api_key: str = None, **kwargs):
        """
        Initialize the interaction agent.
        
        Args:
            provider: LLM provider ('openai', 'anthropic', 'bedrock', or 'groq')
            model: Model name to use
            api_key: API key for the provider
            **kwargs: Additional configuration options
        """
        self.provider = provider.lower()
        self.model = model
        self.api_key = api_key
        
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
        
        # Load guardrails configuration
        self.guardrails = kwargs.get('guardrails', self._default_guardrails())

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

    def _default_guardrails(self) -> Dict[str, Any]:
        """
        Define default guardrails for the interaction agent.
        
        Returns:
            Dictionary containing default guardrail configurations
        """
        return {
            "content_filtering": True,
            "pii_detection": True,
            "max_tokens": 4096,
            "prohibited_topics": [
                "illegal activities",
                "harmful content",
                "discriminatory content"
            ]
        }

    def process_input(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process the input data and apply guardrails.
        
        Args:
            input_data: Dictionary containing the input data
            
        Returns:
            Processed input data with guardrails applied
        """
        # Log the incoming request
        logger.info(f"Processing input: {json.dumps(input_data, default=str)}")
        
        # Apply guardrails to the input
        sanitized_input = self._apply_guardrails(input_data)
        
        # Extract instructions if present
        instructions = sanitized_input.get('instructions', '')
        
        # Determine which tools to execute based on instructions
        tools_to_execute = self._determine_tools(instructions, sanitized_input)
        
        # Prepare the response
        response = {
            'feedback_id': sanitized_input.get('feedback_id', ''),
            'processed_input': sanitized_input,
            'tools_to_execute': tools_to_execute
        }
        
        return response

    def _apply_guardrails(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apply guardrails to the input data.
        
        Args:
            input_data: Dictionary containing the input data
            
        Returns:
            Sanitized input data
        """
        sanitized_input = input_data.copy()
        
        # Check for PII if enabled
        if self.guardrails.get('pii_detection', False):
            sanitized_input = self._detect_and_redact_pii(sanitized_input)
        
        # Check for prohibited topics if enabled
        if self.guardrails.get('content_filtering', False):
            sanitized_input = self._filter_prohibited_content(sanitized_input)
        
        return sanitized_input

    def _detect_and_redact_pii(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Detect and redact personally identifiable information (PII).
        
        Args:
            input_data: Dictionary containing the input data
            
        Returns:
            Input data with PII redacted
        """
        # In a real implementation, this would use a PII detection service
        # For now, we'll implement a simple placeholder
        
        redacted_data = input_data.copy()
        
        # Simple check for potential PII in feedback text
        if 'feedback_text' in redacted_data:
            # This is a very simplified example - in production, use a proper PII detection service
            pii_patterns = [
                r'\b\d{3}[-.\s]?\d{2}[-.\s]?\d{4}\b',  # SSN
                r'\b\d{16}\b',  # Credit card
                r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'  # Email
            ]
            
            feedback_text = redacted_data['feedback_text']
            
            # In a real implementation, we would use regex or a dedicated service
            # For this example, we'll just check for some keywords
            pii_keywords = ['ssn', 'social security', 'credit card', 'password']
            for keyword in pii_keywords:
                if keyword in feedback_text.lower():
                    logger.warning(f"Potential PII detected in feedback: {keyword}")
        
        return redacted_data

    def _filter_prohibited_content(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Filter out prohibited content.
        
        Args:
            input_data: Dictionary containing the input data
            
        Returns:
            Input data with prohibited content filtered
        """
        filtered_data = input_data.copy()
        
        # Check feedback text for prohibited topics
        if 'feedback_text' in filtered_data:
            feedback_text = filtered_data['feedback_text']
            prohibited_topics = self.guardrails.get('prohibited_topics', [])
            
            for topic in prohibited_topics:
                if topic.lower() in feedback_text.lower():
                    logger.warning(f"Prohibited topic detected: {topic}")
                    # In a real implementation, we might redact or flag this content
        
        return filtered_data

    def _determine_tools(self, instructions: str, input_data: Dict[str, Any]) -> List[str]:
        """
        Determine which tools to execute based on the instructions.
        
        Args:
            instructions: Instructions provided in the input
            input_data: Dictionary containing the input data
            
        Returns:
            List of tools to execute
        """
        # Default tools to execute if no specific instructions
        default_tools = ['sentiment_analysis', 'topic_categorization', 
                        'keyword_contextualization', 'summarization']
        
        # If no instructions, return default tools
        if not instructions:
            return default_tools
        
        # Use LLM to interpret instructions and determine which tools to execute
        prompt = self._create_tool_selection_prompt(instructions, input_data)
        tools = self._query_llm_for_tool_selection(prompt)
        
        # If LLM fails to determine tools, fall back to default
        if not tools:
            logger.warning("Failed to determine tools from instructions, using default tools")
            return default_tools
        
        return tools

    def _create_tool_selection_prompt(self, instructions: str, 
                                     input_data: Dict[str, Any]) -> str:
        """
        Create a prompt for the LLM to determine which tools to execute.
        
        Args:
            instructions: Instructions provided in the input
            input_data: Dictionary containing the input data
            
        Returns:
            Prompt for the LLM
        """
        feedback_text = input_data.get('feedback_text', '')
        
        prompt = f"""
        You are an AI assistant tasked with determining which tools to execute based on the following instructions and feedback text.
        
        Available tools:
        1. sentiment_analysis: Perform sentiment scoring (positive, negative, neutral)
        2. topic_categorization: Categorize feedback into predefined topics (e.g., Product Quality, Delivery, Support)
        3. keyword_contextualization: Extract context-aware keywords with relevance scores
        4. summarization: Generate concise summaries and actionable recommendations
        
        Instructions: "{instructions}"
        
        Feedback text: "{feedback_text}"
        
        Based on the instructions and feedback text, which tools should be executed? Respond with a JSON array containing the tool names, e.g., ["sentiment_analysis", "summarization"].
        If the instructions are unclear or don't specify any tools, include all tools.
        """
        
        return prompt

    def _query_llm_for_tool_selection(self, prompt: str) -> List[str]:
        """
        Query the LLM to determine which tools to execute.
        
        Args:
            prompt: Prompt for the LLM
            
        Returns:
            List of tools to execute
        """
        try:
            if self.provider == 'openai':
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[{"role": "system", "content": "You are a helpful assistant."}, 
                              {"role": "user", "content": prompt}],
                    temperature=0.1
                )
                result = response.choices[0].message.content
            
            elif self.provider == 'anthropic':
                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=1000,
                    temperature=0.1,
                    system="You are a helpful assistant.",
                    messages=[{"role": "user", "content": prompt}]
                )
                result = response.content[0].text
            
            elif self.provider == 'bedrock':
                # For Bedrock, we need to format the request based on the model
                if 'claude' in self.model:
                    # Claude model format
                    payload = {
                        "anthropic_version": "bedrock-2023-05-31",
                        "max_tokens": 1000,
                        "temperature": 0.1,
                        "system": "You are a helpful assistant.",
                        "messages": [{"role": "user", "content": prompt}]
                    }
                else:
                    # Generic format - would need to be adjusted for specific models
                    payload = {
                        "prompt": prompt,
                        "max_tokens": 1000,
                        "temperature": 0.1
                    }
                
                response = self.client.invoke_model(
                    modelId=self.model,
                    body=json.dumps(payload)
                )
                response_body = json.loads(response['body'].read())
                
                # Extract the result based on the model
                if 'claude' in self.model:
                    result = response_body['content'][0]['text']
                else:
                    # Generic extraction - would need to be adjusted for specific models
                    result = response_body.get('completion', '')
            
            elif self.provider == 'groq':
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[{"role": "system", "content": "You are a helpful assistant."}, 
                              {"role": "user", "content": prompt}],
                    temperature=0.1
                )
                result = response.choices[0].message.content
            
            # Parse the result to extract the tools
            try:
                # Try to parse as JSON
                tools = json.loads(result)
                if isinstance(tools, list):
                    return tools
                
                # If the result is a dictionary with a key containing the tools
                for key, value in tools.items():
                    if isinstance(value, list):
                        return value
                
                # If we couldn't find a list, try to extract from text
                return self._extract_tools_from_text(result)
            
            except json.JSONDecodeError:
                # If not valid JSON, try to extract tools from text
                return self._extract_tools_from_text(result)
        
        except Exception as e:
            logger.error(f"Error querying LLM for tool selection: {str(e)}")
            return []

    def _extract_tools_from_text(self, text: str) -> List[str]:
        """
        Extract tool names from text response.
        
        Args:
            text: Text response from the LLM
            
        Returns:
            List of tools extracted from the text
        """
        available_tools = ['sentiment_analysis', 'topic_categorization', 
                          'keyword_contextualization', 'summarization']
        
        found_tools = []
        for tool in available_tools:
            if tool in text.lower():
                found_tools.append(tool)
        
        return found_tools
