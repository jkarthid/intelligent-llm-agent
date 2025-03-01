"""
Sentiment Analysis Tool Module

This module implements the sentiment analysis tool that analyzes the
sentiment of text data.
"""

import json
import logging
from typing import Dict, Any

import openai
import anthropic
import boto3
import groq

logger = logging.getLogger(__name__)


class SentimentAnalysisTool:
    """
    Tool for analyzing sentiment in text data.
    
    This tool uses LLMs to analyze the sentiment of text data and
    categorize it as positive, negative, or neutral with confidence scores.
    """

    def __init__(self, provider: str = 'openai', model: str = None, 
                 api_key: str = None, **kwargs):
        """
        Initialize the sentiment analysis tool.
        
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
        Execute the sentiment analysis tool on the input data.
        
        Args:
            input_data: Dictionary containing the input data
            
        Returns:
            Dictionary containing the sentiment analysis results
        """
        # Extract the text to analyze
        text = input_data.get('feedback_text', '')
        
        if not text:
            logger.warning("No text provided for sentiment analysis")
            return {'error': 'No text provided for sentiment analysis'}
        
        # Create the prompt for sentiment analysis
        prompt = self._create_sentiment_analysis_prompt(text)
        
        # Query the LLM for sentiment analysis
        sentiment_result = self._query_llm_for_sentiment(prompt)
        
        return sentiment_result

    def _create_sentiment_analysis_prompt(self, text: str) -> str:
        """
        Create a prompt for sentiment analysis.
        
        Args:
            text: Text to analyze
            
        Returns:
            Prompt for the LLM
        """
        prompt = f"""
        Analyze the sentiment of the following text and provide scores for positive, negative, and neutral sentiments. The scores should add up to 1.0.
        
        Text: "{text}"
        
        Respond with a JSON object containing:
        1. overall_sentiment: The dominant sentiment (positive, negative, or neutral)
        2. scores: An object with scores for positive, negative, and neutral sentiments
        3. explanation: A brief explanation of the sentiment analysis
        
        Example response format:
        {{
            "overall_sentiment": "positive",
            "scores": {{
                "positive": 0.8,
                "negative": 0.1,
                "neutral": 0.1
            }},
            "explanation": "The text expresses satisfaction with the product but mentions a minor issue."
        }}
        """
        
        return prompt

    def _query_llm_for_sentiment(self, prompt: str) -> Dict[str, Any]:
        """
        Query the LLM for sentiment analysis.
        
        Args:
            prompt: Prompt for the LLM
            
        Returns:
            Dictionary containing the sentiment analysis results
        """
        try:
            if self.provider == 'openai':
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[{"role": "system", "content": "You are a sentiment analysis assistant."}, 
                              {"role": "user", "content": prompt}],
                    temperature=0.1
                )
                result = response.choices[0].message.content
            
            elif self.provider == 'anthropic':
                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=1000,
                    temperature=0.1,
                    system="You are a sentiment analysis assistant.",
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
                        "system": "You are a sentiment analysis assistant.",
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
                    messages=[{"role": "system", "content": "You are a sentiment analysis assistant."}, 
                              {"role": "user", "content": prompt}],
                    temperature=0.1
                )
                result = response.choices[0].message.content
            
            # Parse the result to extract the sentiment analysis
            try:
                # Try to parse as JSON
                sentiment_data = json.loads(result)
                return sentiment_data
            
            except json.JSONDecodeError:
                # If not valid JSON, try to extract sentiment from text
                logger.warning("Failed to parse sentiment analysis result as JSON")
                return self._extract_sentiment_from_text(result)
        
        except Exception as e:
            logger.error(f"Error querying LLM for sentiment analysis: {str(e)}")
            return {
                'error': str(e),
                'overall_sentiment': 'unknown',
                'scores': {
                    'positive': 0.0,
                    'negative': 0.0,
                    'neutral': 0.0
                },
                'explanation': 'Failed to analyze sentiment due to an error.'
            }

    def _extract_sentiment_from_text(self, text: str) -> Dict[str, Any]:
        """
        Extract sentiment analysis from text response.
        
        Args:
            text: Text response from the LLM
            
        Returns:
            Dictionary containing the sentiment analysis results
        """
        # This is a fallback method if JSON parsing fails
        # In a real implementation, this would be more sophisticated
        
        # Default values
        sentiment_data = {
            'overall_sentiment': 'unknown',
            'scores': {
                'positive': 0.0,
                'negative': 0.0,
                'neutral': 0.0
            },
            'explanation': 'Failed to parse sentiment analysis result.'
        }
        
        # Try to extract overall sentiment
        if 'positive' in text.lower():
            sentiment_data['overall_sentiment'] = 'positive'
            sentiment_data['scores']['positive'] = 0.7
            sentiment_data['scores']['negative'] = 0.1
            sentiment_data['scores']['neutral'] = 0.2
        elif 'negative' in text.lower():
            sentiment_data['overall_sentiment'] = 'negative'
            sentiment_data['scores']['positive'] = 0.1
            sentiment_data['scores']['negative'] = 0.7
            sentiment_data['scores']['neutral'] = 0.2
        elif 'neutral' in text.lower():
            sentiment_data['overall_sentiment'] = 'neutral'
            sentiment_data['scores']['positive'] = 0.3
            sentiment_data['scores']['negative'] = 0.3
            sentiment_data['scores']['neutral'] = 0.4
        
        # Try to extract explanation
        explanation_start = text.lower().find('explanation')
        if explanation_start != -1:
            explanation_end = text.find('\n', explanation_start)
            if explanation_end != -1:
                sentiment_data['explanation'] = text[explanation_start:explanation_end].strip()
        
        return sentiment_data
