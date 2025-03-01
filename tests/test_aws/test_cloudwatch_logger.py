"""
Tests for the CloudWatch Logger Module
"""

import json
import time
import unittest
from unittest.mock import patch, MagicMock, call

import boto3
import pytest
from botocore.exceptions import ClientError

from src.aws.cloudwatch_logger import CloudWatchLogger


class TestCloudWatchLogger:
    """Tests for the CloudWatchLogger class."""

    def setup_method(self):
        """Set up the test environment."""
        # Create mock clients
        self.mock_cloudwatch = MagicMock()
        self.mock_logs = MagicMock()
        
        # Create the CloudWatch logger with the mock clients
        with patch('boto3.client') as mock_boto3_client:
            mock_boto3_client.side_effect = lambda service, region_name: {
                'cloudwatch': self.mock_cloudwatch,
                'logs': self.mock_logs
            }.get(service)
            
            self.logger = CloudWatchLogger(namespace='TestNamespace', region='us-east-1')

    def test_ensure_log_group_exists(self):
        """Test the _ensure_log_group_exists method."""
        # Call the method
        self.logger._ensure_log_group_exists()
        
        # Check that the logs client was called
        self.mock_logs.create_log_group.assert_called_once_with(
            logGroupName=self.logger.log_group
        )

    def test_ensure_log_group_exists_already_exists(self):
        """Test the _ensure_log_group_exists method when the log group already exists."""
        # Configure the mock to raise a ResourceAlreadyExistsException
        self.mock_logs.create_log_group.side_effect = ClientError(
            {'Error': {'Code': 'ResourceAlreadyExistsException'}},
            'CreateLogGroup'
        )
        
        # Call the method
        self.logger._ensure_log_group_exists()
        
        # Check that the logs client was called
        self.mock_logs.create_log_group.assert_called_once_with(
            logGroupName=self.logger.log_group
        )

    def test_ensure_log_stream_exists(self):
        """Test the _ensure_log_stream_exists method."""
        # Call the method
        self.logger._ensure_log_stream_exists()
        
        # Check that the logs client was called
        self.mock_logs.create_log_stream.assert_called_once_with(
            logGroupName=self.logger.log_group,
            logStreamName=self.logger.log_stream
        )

    def test_ensure_log_stream_exists_already_exists(self):
        """Test the _ensure_log_stream_exists method when the log stream already exists."""
        # Configure the mock to raise a ResourceAlreadyExistsException
        self.mock_logs.create_log_stream.side_effect = ClientError(
            {'Error': {'Code': 'ResourceAlreadyExistsException'}},
            'CreateLogStream'
        )
        
        # Call the method
        self.logger._ensure_log_stream_exists()
        
        # Check that the logs client was called
        self.mock_logs.create_log_stream.assert_called_once_with(
            logGroupName=self.logger.log_group,
            logStreamName=self.logger.log_stream
        )

    def test_log_metric(self):
        """Test the log_metric method."""
        # Create test data
        metric_name = 'TestMetric'
        value = 42.0
        dimensions = [{'Name': 'TestDimension', 'Value': 'TestValue'}]
        unit = 'Count'
        
        # Call the method
        self.logger.log_metric(metric_name, value, dimensions, unit)
        
        # Check that the CloudWatch client was called
        self.mock_cloudwatch.put_metric_data.assert_called_once()
        
        # Check the arguments
        call_args = self.mock_cloudwatch.put_metric_data.call_args[1]
        assert call_args['Namespace'] == 'TestNamespace'
        assert len(call_args['MetricData']) == 1
        assert call_args['MetricData'][0]['MetricName'] == metric_name
        assert call_args['MetricData'][0]['Value'] == value
        assert call_args['MetricData'][0]['Unit'] == unit
        assert call_args['MetricData'][0]['Dimensions'] == dimensions

    def test_log_event(self):
        """Test the log_event method."""
        # Create test data
        event_data = {'test': 'data'}
        log_level = 'INFO'
        
        # Configure the mock to return a sequence token
        self.mock_logs.describe_log_streams.return_value = {
            'logStreams': [{'uploadSequenceToken': '123456'}]
        }
        
        # Call the method
        self.logger.log_event(event_data, log_level)
        
        # Check that the logs client was called
        self.mock_logs.describe_log_streams.assert_called_once_with(
            logGroupName=self.logger.log_group,
            logStreamNamePrefix=self.logger.log_stream
        )
        
        self.mock_logs.put_log_events.assert_called_once()
        
        # Check the arguments
        call_args = self.mock_logs.put_log_events.call_args[1]
        assert call_args['logGroupName'] == self.logger.log_group
        assert call_args['logStreamName'] == self.logger.log_stream
        assert len(call_args['logEvents']) == 1
        assert call_args['logEvents'][0]['message'] == f"[{log_level}] {json.dumps(event_data)}"
        assert call_args['sequenceToken'] == '123456'

    def test_log_event_no_sequence_token(self):
        """Test the log_event method when there is no sequence token."""
        # Create test data
        event_data = {'test': 'data'}
        log_level = 'INFO'
        
        # Configure the mock to return no sequence token
        self.mock_logs.describe_log_streams.return_value = {
            'logStreams': [{}]
        }
        
        # Call the method
        self.logger.log_event(event_data, log_level)
        
        # Check that the logs client was called
        self.mock_logs.describe_log_streams.assert_called_once_with(
            logGroupName=self.logger.log_group,
            logStreamNamePrefix=self.logger.log_stream
        )
        
        self.mock_logs.put_log_events.assert_called_once()
        
        # Check the arguments
        call_args = self.mock_logs.put_log_events.call_args[1]
        assert call_args['logGroupName'] == self.logger.log_group
        assert call_args['logStreamName'] == self.logger.log_stream
        assert len(call_args['logEvents']) == 1
        assert call_args['logEvents'][0]['message'] == f"[{log_level}] {json.dumps(event_data)}"
        assert 'sequenceToken' not in call_args

    def test_log_cache_metrics(self):
        """Test the log_cache_metrics method."""
        # Create test data
        cache_metrics = {
            'hits': 10,
            'misses': 5,
            'sets': 15,
            'deletes': 3
        }
        
        # Call the method
        self.logger.log_cache_metrics(cache_metrics)
        
        # Check that the CloudWatch client was called
        assert self.mock_cloudwatch.put_metric_data.call_count == 5  # 4 metrics + hit ratio
        
        # Check that the hit ratio was calculated correctly
        hit_ratio_call = self.mock_cloudwatch.put_metric_data.call_args_list[4]
        hit_ratio_args = hit_ratio_call[1]
        assert hit_ratio_args['MetricData'][0]['MetricName'] == 'CacheHitRatio'
        assert hit_ratio_args['MetricData'][0]['Value'] == 10 / (10 + 5)  # hits / (hits + misses)

    def test_log_tool_execution(self):
        """Test the log_tool_execution method."""
        # Create test data
        tool_name = 'TestTool'
        execution_time = 0.5
        success = True
        
        # Call the method
        self.logger.log_tool_execution(tool_name, execution_time, success)
        
        # Check that the CloudWatch client was called
        assert self.mock_cloudwatch.put_metric_data.call_count == 2
        
        # Check the execution time metric
        execution_time_call = self.mock_cloudwatch.put_metric_data.call_args_list[0]
        execution_time_args = execution_time_call[1]
        assert execution_time_args['MetricData'][0]['MetricName'] == 'ToolExecutionTime'
        assert execution_time_args['MetricData'][0]['Value'] == execution_time
        assert execution_time_args['MetricData'][0]['Unit'] == 'Seconds'
        assert execution_time_args['MetricData'][0]['Dimensions'] == [{'Name': 'ToolName', 'Value': tool_name}]
        
        # Check the success metric
        success_call = self.mock_cloudwatch.put_metric_data.call_args_list[1]
        success_args = success_call[1]
        assert success_args['MetricData'][0]['MetricName'] == 'ToolExecutionSuccess'
        assert success_args['MetricData'][0]['Value'] == 1.0
        assert success_args['MetricData'][0]['Dimensions'] == [{'Name': 'ToolName', 'Value': tool_name}]

    def test_log_llm_decision(self):
        """Test the log_llm_decision method."""
        # Create test data
        decision_type = 'ToolSelection'
        decision = 'sentiment_analysis'
        confidence = 0.9
        
        # Call the method
        self.logger.log_llm_decision(decision_type, decision, confidence)
        
        # Check that the logs client was called
        self.mock_logs.describe_log_streams.assert_called_once()
        self.mock_logs.put_log_events.assert_called_once()
        
        # Check that the CloudWatch client was called
        self.mock_cloudwatch.put_metric_data.assert_called_once()
        
        # Check the confidence metric
        confidence_args = self.mock_cloudwatch.put_metric_data.call_args[1]
        assert confidence_args['MetricData'][0]['MetricName'] == 'LLMDecisionConfidence'
        assert confidence_args['MetricData'][0]['Value'] == confidence
        assert confidence_args['MetricData'][0]['Unit'] == 'None'
        assert confidence_args['MetricData'][0]['Dimensions'] == [{'Name': 'DecisionType', 'Value': decision_type}]
