"""
Lambda Handler Module

This module implements the AWS Lambda handler for the intelligent LLM agent.
"""

import json
import logging
import os
import time
from typing import Dict, Any, List, Union

from aws_lambda_powertools import Logger
from aws_lambda_powertools.utilities.typing import LambdaContext

from ..agents.agent_factory import AgentFactory
from ..cache.cache_manager import CacheManager
from ..utils.input_validator import validate_input
from ..utils.error_handler import handle_error

# Configure logging
logger = Logger(service="intelligent-llm-agent")


def process_single_feedback(feedback: Dict[str, Any], config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Process a single feedback entry.
    
    Args:
        feedback: Feedback entry to process
        config: Configuration for processing
        
    Returns:
        Processing results
    """
    try:
        # Validate the input
        if not validate_input(feedback):
            return {
                'feedback_id': feedback.get('feedback_id', 'unknown'),
                'error': 'Invalid input format'
            }
        
        # Create the interaction agent
        interaction_agent = AgentFactory.create_agent('interaction', config.get('agent_config', {}))
        
        # Process the input with the interaction agent
        interaction_result = interaction_agent.process_input(feedback)
        
        # Extract the tools to execute
        tools_to_execute = interaction_result.get('tools_to_execute', [])
        
        # Create the tool agent
        tool_agent = AgentFactory.create_agent('tool', config.get('agent_config', {}))
        
        # Process the request with the tool agent
        tool_result = tool_agent.process_request(feedback, tools_to_execute)
        
        # Combine the results
        result = {
            'feedback_id': feedback.get('feedback_id', 'unknown'),
            'processed_at': int(time.time()),
            'tools_executed': tools_to_execute,
            'results': tool_result.get('results', {})
        }
        
        return result
    
    except Exception as e:
        # Handle the error
        error_result = handle_error(e, feedback.get('feedback_id', 'unknown'))
        logger.error(f"Error processing feedback: {str(e)}")
        return error_result


def lambda_handler(event: Dict[str, Any], context: LambdaContext) -> Dict[str, Any]:
    """
    AWS Lambda handler for the intelligent LLM agent.
    
    Args:
        event: Lambda event
        context: Lambda context
        
    Returns:
        Lambda response
    """
    # Log the incoming event
    logger.info(f"Received event: {json.dumps(event)}")
    
    # Extract the configuration
    config = {
        'agent_config': {
            'provider': os.environ.get('LLM_PROVIDER', 'openai'),
            'model': os.environ.get('LLM_MODEL', None),
            'api_key': os.environ.get('LLM_API_KEY', None),
            'use_cache': os.environ.get('USE_CACHE', 'true').lower() == 'true',
            'cache_config': {
                'cache_type': os.environ.get('CACHE_TYPE', 'memory'),
                'ttl': int(os.environ.get('CACHE_TTL', '3600')),
                'table_name': os.environ.get('DYNAMODB_TABLE', 'LLMAgentCache'),
                'region': os.environ.get('AWS_REGION', 'us-east-1')
            }
        }
    }
    
    # Check if the event is a batch of feedback entries or a single entry
    if 'Records' in event:
        # Process a batch of feedback entries
        results = []
        
        for record in event['Records']:
            # Extract the feedback from the record
            if 'body' in record:
                try:
                    feedback = json.loads(record['body'])
                    result = process_single_feedback(feedback, config)
                    results.append(result)
                except json.JSONDecodeError:
                    logger.error(f"Invalid JSON in record: {record['body']}")
                    results.append({
                        'error': 'Invalid JSON in record'
                    })
            else:
                logger.error(f"Invalid record format: {record}")
                results.append({
                    'error': 'Invalid record format'
                })
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'results': results
            })
        }
    
    elif 'feedback' in event:
        # Check if this is a batch of feedback entries
        feedback_entries = event['feedback']
        
        if isinstance(feedback_entries, list):
            # Process a batch of feedback entries
            results = []
            
            for feedback in feedback_entries:
                result = process_single_feedback(feedback, config)
                results.append(result)
            
            return {
                'statusCode': 200,
                'body': json.dumps({
                    'results': results
                })
            }
        else:
            # Process a single feedback entry
            result = process_single_feedback(feedback_entries, config)
            
            return {
                'statusCode': 200,
                'body': json.dumps(result)
            }
    
    elif 'feedback_id' in event:
        # Process a single feedback entry
        result = process_single_feedback(event, config)
        
        return {
            'statusCode': 200,
            'body': json.dumps(result)
        }
    
    else:
        # Invalid event format
        logger.error(f"Invalid event format: {event}")
        
        return {
            'statusCode': 400,
            'body': json.dumps({
                'error': 'Invalid event format'
            })
        }


def lambda_url_handler(event: Dict[str, Any], context: LambdaContext) -> Dict[str, Any]:
    """
    AWS Lambda URL handler for the intelligent LLM agent.
    
    This handler is designed to be used with Lambda Function URLs.
    
    Args:
        event: Lambda event
        context: Lambda context
        
    Returns:
        Lambda response
    """
    # Log the incoming event
    logger.info(f"Received Lambda URL event")
    
    try:
        # Extract the body from the event
        if 'body' in event:
            try:
                body = json.loads(event['body'])
            except json.JSONDecodeError:
                logger.error(f"Invalid JSON in request body: {event['body']}")
                return {
                    'statusCode': 400,
                    'headers': {
                        'Content-Type': 'application/json'
                    },
                    'body': json.dumps({
                        'error': 'Invalid JSON in request body'
                    })
                }
        else:
            logger.error(f"No body in request: {event}")
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/json'
                },
                'body': json.dumps({
                    'error': 'No body in request'
                })
            }
        
        # Process the request using the main lambda handler
        result = lambda_handler(body, context)
        
        # Return the result
        return {
            'statusCode': result.get('statusCode', 200),
            'headers': {
                'Content-Type': 'application/json'
            },
            'body': result.get('body', json.dumps({'error': 'Unknown error'}))
        }
    
    except Exception as e:
        # Handle the error
        logger.error(f"Error processing Lambda URL request: {str(e)}")
        
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json'
            },
            'body': json.dumps({
                'error': f'Error processing request: {str(e)}'
            })
        }
