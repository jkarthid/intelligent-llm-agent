"""
Summarization Tool Module

This module implements the summarization tool that generates concise
summaries and actionable recommendations from text data.
"""

import json
import logging
from typing import Dict, Any, List

import openai
import anthropic
import boto3
import groq

logger = logging.getLogger(__name__)


class SummarizationTool:
    """
    Tool for generating concise summaries and actionable recommendations.
    
    This tool uses LLMs to generate summaries and actionable recommendations
    from text data.
    """

    def __init__(self, provider: str = 'openai', model: str = None, 
                 api_key: str = None, **kwargs):
        """
        Initialize the summarization tool.
        
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
        
        # Set the maximum summary length
        self.max_summary_length = kwargs.get('max_summary_length', 200)
        self.max_recommendations = kwargs.get('max_recommendations', 3)

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
        Execute the summarization tool on the input data.
        
        Args:
            input_data: Dictionary containing the input data
            
        Returns:
            Dictionary containing the summarization results
        """
        # Extract the text to summarize
        text = input_data.get('feedback_text', '')
        
        if not text:
            logger.warning("No text provided for summarization")
            return {'error': 'No text provided for summarization'}
        
        # Create the prompt for summarization
        prompt = self._create_summarization_prompt(text)
        
        # Query the LLM for summarization
        summary_result = self._query_llm_for_summary(prompt)
        
        return summary_result

    def _create_summarization_prompt(self, text: str) -> str:
        """
        Create a prompt for summarization.
        
        Args:
            text: Text to summarize
            
        Returns:
            Prompt for the LLM
        """
        prompt = f"""
        Summarize the following text and provide actionable recommendations. Keep the summary concise (maximum {self.max_summary_length} characters) and provide at most {self.max_recommendations} actionable recommendations.
        
        Text: "{text}"
        
        Respond with a JSON object containing:
        1. summary: A concise summary of the text
        2. recommendations: An array of actionable recommendations
        3. key_points: An array of key points from the text
        
        Example response format:
        {{
            "summary": "Customer is satisfied with the product quality but experienced delivery delays, which caused frustration.",
            "recommendations": [
                "Improve delivery logistics to reduce delays",
                "Proactively communicate shipping status to customers"
            ],
            "key_points": [
                "Product quality is good",
                "Delivery was delayed",
                "Customer experienced frustration"
            ]
        }}
        """
        
        return prompt

    def _query_llm_for_summary(self, prompt: str) -> Dict[str, Any]:
        """
        Query the LLM for summarization.
        
        Args:
            prompt: Prompt for the LLM
            
        Returns:
            Dictionary containing the summarization results
        """
        try:
            if self.provider == 'openai':
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[{"role": "system", "content": "You are a summarization assistant."}, 
                              {"role": "user", "content": prompt}],
                    temperature=0.1
                )
                result = response.choices[0].message.content
            
            elif self.provider == 'anthropic':
                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=1000,
                    temperature=0.1,
                    system="You are a summarization assistant.",
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
                        "system": "You are a summarization assistant.",
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
                    messages=[{"role": "system", "content": "You are a summarization assistant."}, 
                              {"role": "user", "content": prompt}],
                    temperature=0.1
                )
                result = response.choices[0].message.content
            
            # Parse the result to extract the summary
            try:
                # Try to parse as JSON
                summary_data = json.loads(result)
                return summary_data
            
            except json.JSONDecodeError:
                # If not valid JSON, try to extract summary from text
                logger.warning("Failed to parse summarization result as JSON")
                return self._extract_summary_from_text(result)
        
        except Exception as e:
            logger.error(f"Error querying LLM for summarization: {str(e)}")
            return {
                'error': str(e),
                'summary': 'Failed to generate summary due to an error.',
                'recommendations': [],
                'key_points': []
            }

    def _extract_summary_from_text(self, text: str) -> Dict[str, Any]:
        """
        Extract summary from text response.
        
        Args:
            text: Text response from the LLM
            
        Returns:
            Dictionary containing the summarization results
        """
        # This is a fallback method if JSON parsing fails
        # In a real implementation, this would be more sophisticated
        
        # Default values
        summary_data = {
            'summary': '',
            'recommendations': [],
            'key_points': []
        }
        
        # Try to extract summary
        summary_start = text.lower().find('summary:')
        if summary_start != -1:
            summary_end = text.find('\n', summary_start)
            if summary_end == -1:
                summary_end = len(text)
            
            summary_data['summary'] = text[summary_start+8:summary_end].strip()
        
        # Try to extract recommendations
        recommendations_start = text.lower().find('recommendations:')
        if recommendations_start != -1:
            recommendations_end = text.lower().find('key points:')
            if recommendations_end == -1:
                recommendations_end = len(text)
            
            recommendations_text = text[recommendations_start+16:recommendations_end].strip()
            recommendations_lines = recommendations_text.split('\n')
            
            for line in recommendations_lines:
                line = line.strip()
                if line and (line.startswith('-') or line.startswith('*') or line[0].isdigit()):
                    recommendation = line[1:].strip() if line[0] in '-*' else line[2:].strip() if line[0].isdigit() else line
                    summary_data['recommendations'].append(recommendation)
        
        # Try to extract key points
        key_points_start = text.lower().find('key points:')
        if key_points_start != -1:
            key_points_text = text[key_points_start+11:].strip()
            key_points_lines = key_points_text.split('\n')
            
            for line in key_points_lines:
                line = line.strip()
                if line and (line.startswith('-') or line.startswith('*') or line[0].isdigit()):
                    key_point = line[1:].strip() if line[0] in '-*' else line[2:].strip() if line[0].isdigit() else line
                    summary_data['key_points'].append(key_point)
        
        return summary_data
