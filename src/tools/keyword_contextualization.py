"""
Keyword Contextualization Tool Module

This module implements the keyword contextualization tool that extracts
context-aware keywords from text data with relevance scores.
"""

import json
import logging
from typing import Dict, Any, List

import openai
import anthropic
import boto3
import groq

logger = logging.getLogger(__name__)


class KeywordContextualizationTool:
    """
    Tool for extracting context-aware keywords from text data.
    
    This tool uses LLMs to extract keywords from text data and
    provide relevance scores and contextual information.
    """

    def __init__(self, provider: str = 'openai', model: str = None, 
                 api_key: str = None, **kwargs):
        """
        Initialize the keyword contextualization tool.
        
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
        
        # Set the maximum number of keywords to extract
        self.max_keywords = kwargs.get('max_keywords', 10)

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
        Execute the keyword contextualization tool on the input data.
        
        Args:
            input_data: Dictionary containing the input data
            
        Returns:
            Dictionary containing the keyword contextualization results
        """
        # Extract the text to analyze
        text = input_data.get('feedback_text', '')
        
        if not text:
            logger.warning("No text provided for keyword contextualization")
            return {'error': 'No text provided for keyword contextualization'}
        
        # Create the prompt for keyword contextualization
        prompt = self._create_keyword_contextualization_prompt(text)
        
        # Query the LLM for keyword contextualization
        keyword_result = self._query_llm_for_keywords(prompt)
        
        return keyword_result

    def _create_keyword_contextualization_prompt(self, text: str) -> str:
        """
        Create a prompt for keyword contextualization.
        
        Args:
            text: Text to analyze
            
        Returns:
            Prompt for the LLM
        """
        prompt = f"""
        Extract the most important keywords or phrases from the following text. For each keyword, provide a relevance score between 0.0 and 1.0, where 1.0 means highly relevant, and a brief contextual explanation.
        
        Extract at most {self.max_keywords} keywords.
        
        Text: "{text}"
        
        Respond with a JSON object containing:
        1. keywords: An array of objects, each with:
           - keyword: The extracted keyword or phrase
           - relevance: A relevance score between 0.0 and 1.0
           - context: A brief explanation of why this keyword is relevant in the context
        
        Example response format:
        {{
            "keywords": [
                {{
                    "keyword": "delivery delay",
                    "relevance": 0.9,
                    "context": "The customer specifically mentioned issues with delivery timing."
                }},
                {{
                    "keyword": "product quality",
                    "relevance": 0.7,
                    "context": "The customer expressed satisfaction with the product itself."
                }}
            ]
        }}
        """
        
        return prompt

    def _query_llm_for_keywords(self, prompt: str) -> Dict[str, Any]:
        """
        Query the LLM for keyword contextualization.
        
        Args:
            prompt: Prompt for the LLM
            
        Returns:
            Dictionary containing the keyword contextualization results
        """
        try:
            if self.provider == 'openai':
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[{"role": "system", "content": "You are a keyword extraction assistant."}, 
                              {"role": "user", "content": prompt}],
                    temperature=0.1
                )
                result = response.choices[0].message.content
            
            elif self.provider == 'anthropic':
                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=1000,
                    temperature=0.1,
                    system="You are a keyword extraction assistant.",
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
                        "system": "You are a keyword extraction assistant.",
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
                    messages=[{"role": "system", "content": "You are a keyword extraction assistant."}, 
                              {"role": "user", "content": prompt}],
                    temperature=0.1
                )
                result = response.choices[0].message.content
            
            # Parse the result to extract the keywords
            try:
                # Try to parse as JSON
                keyword_data = json.loads(result)
                return keyword_data
            
            except json.JSONDecodeError:
                # If not valid JSON, try to extract keywords from text
                logger.warning("Failed to parse keyword contextualization result as JSON")
                return self._extract_keywords_from_text(result)
        
        except Exception as e:
            logger.error(f"Error querying LLM for keyword contextualization: {str(e)}")
            return {
                'error': str(e),
                'keywords': []
            }

    def _extract_keywords_from_text(self, text: str) -> Dict[str, Any]:
        """
        Extract keywords from text response.
        
        Args:
            text: Text response from the LLM
            
        Returns:
            Dictionary containing the keyword contextualization results
        """
        # This is a fallback method if JSON parsing fails
        # In a real implementation, this would be more sophisticated
        
        # Default values
        keyword_data = {
            'keywords': []
        }
        
        # Try to extract keywords
        lines = text.split('\n')
        current_keyword = None
        current_relevance = None
        current_context = None
        
        for line in lines:
            line = line.strip()
            
            # Check if this line contains a keyword
            if line.lower().startswith('keyword:') or line.lower().startswith('- keyword:'):
                # If we have a complete keyword entry, add it to the list
                if current_keyword and current_relevance is not None:
                    keyword_data['keywords'].append({
                        'keyword': current_keyword,
                        'relevance': current_relevance,
                        'context': current_context or 'No context provided'
                    })
                
                # Start a new keyword entry
                keyword_part = line.split(':', 1)[1].strip()
                current_keyword = keyword_part
                current_relevance = None
                current_context = None
            
            # Check if this line contains a relevance score
            elif line.lower().startswith('relevance:') or line.lower().startswith('- relevance:'):
                relevance_part = line.split(':', 1)[1].strip()
                try:
                    current_relevance = float(relevance_part)
                except ValueError:
                    current_relevance = 0.5  # Default if we can't parse
            
            # Check if this line contains context
            elif line.lower().startswith('context:') or line.lower().startswith('- context:'):
                context_part = line.split(':', 1)[1].strip()
                current_context = context_part
        
        # Add the last keyword if we have one
        if current_keyword and current_relevance is not None:
            keyword_data['keywords'].append({
                'keyword': current_keyword,
                'relevance': current_relevance,
                'context': current_context or 'No context provided'
            })
        
        return keyword_data
