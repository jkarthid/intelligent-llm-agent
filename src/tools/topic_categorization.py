"""
Topic Categorization Tool Module

This module implements the topic categorization tool that categorizes
text data into predefined topics.
"""

import json
import logging
from typing import Dict, Any, List

import openai
import anthropic
import boto3
import groq

logger = logging.getLogger(__name__)


class TopicCategorizationTool:
    """
    Tool for categorizing text data into predefined topics.
    
    This tool uses LLMs to categorize text data into predefined topics
    such as Product Quality, Delivery, Support, etc.
    """

    def __init__(self, provider: str = 'openai', model: str = None, 
                 api_key: str = None, **kwargs):
        """
        Initialize the topic categorization tool.
        
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
        
        # Define predefined topics
        self.predefined_topics = kwargs.get('predefined_topics', [
            'Product Quality',
            'Delivery',
            'Customer Support',
            'User Experience',
            'Pricing',
            'Features',
            'Reliability',
            'Documentation',
            'Billing',
            'Other'
        ])

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

    def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the topic categorization tool on the input data.
        
        Args:
            input_data: Dictionary containing the input data
            
        Returns:
            Dictionary containing the topic categorization results
        """
        # Extract the text to categorize
        text = input_data.get('feedback_text', '')
        
        if not text:
            logger.warning("No text provided for topic categorization")
            return {'error': 'No text provided for topic categorization'}
        
        # Create the prompt for topic categorization
        prompt = self._create_topic_categorization_prompt(text)
        
        # Query the LLM for topic categorization
        topic_result = self._query_llm_for_topics(prompt)
        
        return topic_result

    def _create_topic_categorization_prompt(self, text: str) -> str:
        """
        Create a prompt for topic categorization.
        
        Args:
            text: Text to categorize
            
        Returns:
            Prompt for the LLM
        """
        topics_str = ', '.join(self.predefined_topics)
        
        prompt = f"""
        Categorize the following text into one or more of these predefined topics: {topics_str}.
        
        For each relevant topic, provide a relevance score between 0.0 and 1.0, where 1.0 means highly relevant.
        
        Text: "{text}"
        
        Respond with a JSON object containing:
        1. primary_topic: The most relevant topic
        2. topics: An object with topics as keys and relevance scores as values (only include topics with non-zero relevance)
        3. explanation: A brief explanation of the categorization
        
        Example response format:
        {{
            "primary_topic": "Delivery",
            "topics": {{
                "Delivery": 0.9,
                "Customer Support": 0.3,
                "Product Quality": 0.1
            }},
            "explanation": "The text primarily discusses delivery issues with some mention of customer support interactions."
        }}
        """
        
        return prompt

    def _query_llm_for_topics(self, prompt: str) -> Dict[str, Any]:
        """
        Query the LLM for topic categorization.
        
        Args:
            prompt: Prompt for the LLM
            
        Returns:
            Dictionary containing the topic categorization results
        """
        try:
            if self.provider == 'openai':
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[{"role": "system", "content": "You are a topic categorization assistant."}, 
                              {"role": "user", "content": prompt}],
                    temperature=0.1
                )
                result = response.choices[0].message.content
            
            elif self.provider == 'anthropic':
                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=1000,
                    temperature=0.1,
                    system="You are a topic categorization assistant.",
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
                        "system": "You are a topic categorization assistant.",
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
                    messages=[{"role": "system", "content": "You are a topic categorization assistant."}, 
                              {"role": "user", "content": prompt}],
                    temperature=0.1
                )
                result = response.choices[0].message.content
            
            # Parse the result to extract the topic categorization
            try:
                # Try to parse as JSON
                topic_data = json.loads(result)
                return topic_data
            
            except json.JSONDecodeError:
                # If not valid JSON, try to extract topics from text
                logger.warning("Failed to parse topic categorization result as JSON")
                return self._extract_topics_from_text(result)
        
        except Exception as e:
            logger.error(f"Error querying LLM for topic categorization: {str(e)}")
            return {
                'error': str(e),
                'primary_topic': 'Unknown',
                'topics': {},
                'explanation': 'Failed to categorize topics due to an error.'
            }

    def _extract_topics_from_text(self, text: str) -> Dict[str, Any]:
        """
        Extract topic categorization from text response.
        
        Args:
            text: Text response from the LLM
            
        Returns:
            Dictionary containing the topic categorization results
        """
        # This is a fallback method if JSON parsing fails
        # In a real implementation, this would be more sophisticated
        
        # Default values
        topic_data = {
            'primary_topic': 'Unknown',
            'topics': {},
            'explanation': 'Failed to parse topic categorization result.'
        }
        
        # Try to find topics and their scores
        for topic in self.predefined_topics:
            if topic.lower() in text.lower():
                # Try to find a score near the topic mention
                topic_index = text.lower().find(topic.lower())
                score_start = text.find(':', topic_index)
                if score_start != -1:
                    score_end = text.find('\n', score_start)
                    if score_end == -1:
                        score_end = len(text)
                    
                    score_text = text[score_start+1:score_end].strip()
                    try:
                        score = float(score_text)
                        topic_data['topics'][topic] = score
                    except ValueError:
                        # If we can't parse a score, assign a default
                        topic_data['topics'][topic] = 0.5
                else:
                    # If we can't find a score, assign a default
                    topic_data['topics'][topic] = 0.5
        
        # Determine the primary topic
        if topic_data['topics']:
            primary_topic = max(topic_data['topics'].items(), key=lambda x: x[1])[0]
            topic_data['primary_topic'] = primary_topic
        
        # Try to extract explanation
        explanation_start = text.lower().find('explanation')
        if explanation_start != -1:
            explanation_end = text.find('\n', explanation_start)
            if explanation_end != -1:
                topic_data['explanation'] = text[explanation_start:explanation_end].strip()
        
        return topic_data
