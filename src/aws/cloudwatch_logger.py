"""
CloudWatch Logger Module

This module implements the CloudWatch logger for monitoring and logging.
"""

import json
import logging
import time
from typing import Dict, Any, List, Optional

import boto3
from botocore.exceptions import ClientError

# Configure logging
logger = logging.getLogger(__name__)


class CloudWatchLogger:
    """
    Logger for CloudWatch metrics and logs.
    
    This class provides an interface for logging metrics and events
    to CloudWatch for monitoring and analysis.
    """

    def __init__(self, namespace: str = 'IntelligentLLMAgent', 
                 region: str = 'us-east-1', **kwargs):
        """
        Initialize the CloudWatch logger.
        
        Args:
            namespace: CloudWatch namespace
            region: AWS region
            **kwargs: Additional configuration options
        """
        self.namespace = namespace
        
        # Initialize the CloudWatch clients
        self.cloudwatch = boto3.client('cloudwatch', region_name=region)
        self.logs = boto3.client('logs', region_name=region)
        
        # Set the log group and stream
        self.log_group = kwargs.get('log_group', '/aws/lambda/intelligent-llm-agent')
        self.log_stream = kwargs.get('log_stream', f'agent-logs-{int(time.time())}')
        
        # Ensure the log group and stream exist
        self._ensure_log_group_exists()
        self._ensure_log_stream_exists()

    def _ensure_log_group_exists(self) -> None:
        """Ensure that the log group exists."""
        try:
            self.logs.create_log_group(
                logGroupName=self.log_group
            )
            logger.info(f"Created log group: {self.log_group}")
        except ClientError as e:
            # If the log group already exists, ignore the error
            if e.response['Error']['Code'] != 'ResourceAlreadyExistsException':
                logger.error(f"Error creating log group: {str(e)}")

    def _ensure_log_stream_exists(self) -> None:
        """Ensure that the log stream exists."""
        try:
            self.logs.create_log_stream(
                logGroupName=self.log_group,
                logStreamName=self.log_stream
            )
            logger.info(f"Created log stream: {self.log_stream}")
        except ClientError as e:
            # If the log stream already exists, ignore the error
            if e.response['Error']['Code'] != 'ResourceAlreadyExistsException':
                logger.error(f"Error creating log stream: {str(e)}")

    def log_metric(self, metric_name: str, value: float, 
                  dimensions: Optional[List[Dict[str, str]]] = None, 
                  unit: str = 'Count') -> None:
        """
        Log a metric to CloudWatch.
        
        Args:
            metric_name: Name of the metric
            value: Value of the metric
            dimensions: Dimensions for the metric
            unit: Unit of the metric
        """
        try:
            # Create the metric data
            metric_data = {
                'MetricName': metric_name,
                'Value': value,
                'Unit': unit,
                'Timestamp': time.time()
            }
            
            # Add dimensions if provided
            if dimensions:
                metric_data['Dimensions'] = dimensions
            
            # Put the metric data
            self.cloudwatch.put_metric_data(
                Namespace=self.namespace,
                MetricData=[metric_data]
            )
            
            logger.debug(f"Logged metric: {metric_name}={value} {unit}")
        
        except ClientError as e:
            logger.error(f"Error logging metric: {str(e)}")

    def log_event(self, event_data: Dict[str, Any], log_level: str = 'INFO') -> None:
        """
        Log an event to CloudWatch Logs.
        
        Args:
            event_data: Event data to log
            log_level: Log level (INFO, WARNING, ERROR, etc.)
        """
        try:
            # Format the event data
            event_message = json.dumps(event_data)
            
            # Get the sequence token for the log stream
            try:
                response = self.logs.describe_log_streams(
                    logGroupName=self.log_group,
                    logStreamNamePrefix=self.log_stream
                )
                
                sequence_token = response['logStreams'][0].get('uploadSequenceToken')
            except (ClientError, IndexError):
                # If there's an error or the stream doesn't exist, create it
                self._ensure_log_stream_exists()
                sequence_token = None
            
            # Put the log event
            log_event = {
                'timestamp': int(time.time() * 1000),
                'message': f"[{log_level}] {event_message}"
            }
            
            if sequence_token:
                self.logs.put_log_events(
                    logGroupName=self.log_group,
                    logStreamName=self.log_stream,
                    logEvents=[log_event],
                    sequenceToken=sequence_token
                )
            else:
                self.logs.put_log_events(
                    logGroupName=self.log_group,
                    logStreamName=self.log_stream,
                    logEvents=[log_event]
                )
            
            logger.debug(f"Logged event: {event_message}")
        
        except ClientError as e:
            logger.error(f"Error logging event: {str(e)}")

    def log_cache_metrics(self, cache_metrics: Dict[str, int]) -> None:
        """
        Log cache metrics to CloudWatch.
        
        Args:
            cache_metrics: Dictionary containing cache metrics
        """
        # Log each cache metric
        for metric_name, value in cache_metrics.items():
            self.log_metric(
                metric_name=f"Cache{metric_name.capitalize()}",
                value=float(value),
                dimensions=[
                    {
                        'Name': 'MetricType',
                        'Value': 'Cache'
                    }
                ]
            )
        
        # Calculate and log the cache hit ratio
        hits = cache_metrics.get('hits', 0)
        misses = cache_metrics.get('misses', 0)
        total = hits + misses
        
        if total > 0:
            hit_ratio = hits / total
            self.log_metric(
                metric_name='CacheHitRatio',
                value=hit_ratio,
                dimensions=[
                    {
                        'Name': 'MetricType',
                        'Value': 'Cache'
                    }
                ],
                unit='None'
            )

    def log_tool_execution(self, tool_name: str, execution_time: float, 
                          success: bool) -> None:
        """
        Log tool execution metrics to CloudWatch.
        
        Args:
            tool_name: Name of the tool
            execution_time: Execution time in seconds
            success: Whether the execution was successful
        """
        # Log the execution time
        self.log_metric(
            metric_name='ToolExecutionTime',
            value=execution_time,
            dimensions=[
                {
                    'Name': 'ToolName',
                    'Value': tool_name
                }
            ],
            unit='Seconds'
        )
        
        # Log the success/failure
        self.log_metric(
            metric_name='ToolExecutionSuccess',
            value=1.0 if success else 0.0,
            dimensions=[
                {
                    'Name': 'ToolName',
                    'Value': tool_name
                }
            ]
        )

    def log_llm_decision(self, decision_type: str, decision: str, 
                        confidence: float = 1.0) -> None:
        """
        Log LLM decision metrics to CloudWatch.
        
        Args:
            decision_type: Type of decision
            decision: The decision made
            confidence: Confidence in the decision (0.0 to 1.0)
        """
        # Log the decision
        self.log_event(
            event_data={
                'type': 'llm_decision',
                'decision_type': decision_type,
                'decision': decision,
                'confidence': confidence
            }
        )
        
        # Log the confidence as a metric
        self.log_metric(
            metric_name='LLMDecisionConfidence',
            value=confidence,
            dimensions=[
                {
                    'Name': 'DecisionType',
                    'Value': decision_type
                }
            ],
            unit='None'
        )
