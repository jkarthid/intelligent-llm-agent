"""
Tests for the DynamoDB Cache Module
"""

import json
import time
import unittest
from unittest.mock import patch, MagicMock

import boto3
import pytest
from botocore.exceptions import ClientError

from src.cache.dynamodb_cache import DynamoDBCache


class TestDynamoDBCache:
    """Tests for the DynamoDBCache class."""

    def setup_method(self):
        """Set up the test environment."""
        # Create a mock DynamoDB client
        self.mock_dynamodb = MagicMock()
        
        # Create a mock response for get_item
        self.mock_get_response = {
            'Item': {
                'cache_key': {'S': 'test_key'},
                'value': {'S': json.dumps({'test': 'data'})},
                'feedback_id': {'S': '12345'},
                'created_at': {'N': str(int(time.time()))},
                'expiry': {'N': str(int(time.time()) + 3600)}
            }
        }
        
        # Create a mock response for scan
        self.mock_scan_response = {
            'Items': [
                {
                    'cache_key': {'S': 'test_key1'},
                    'value': {'S': json.dumps({'test': 'data1'})},
                    'feedback_id': {'S': '12345'},
                    'created_at': {'N': str(int(time.time()))},
                    'expiry': {'N': str(int(time.time()) + 3600)}
                },
                {
                    'cache_key': {'S': 'test_key2'},
                    'value': {'S': json.dumps({'test': 'data2'})},
                    'feedback_id': {'S': '67890'},
                    'created_at': {'N': str(int(time.time()))},
                    'expiry': {'N': str(int(time.time()) + 3600)}
                }
            ]
        }
        
        # Configure the mock client
        self.mock_dynamodb.get_item.return_value = self.mock_get_response
        self.mock_dynamodb.scan.return_value = self.mock_scan_response
        
        # Create the DynamoDB cache with the mock client
        with patch('boto3.resource', return_value=MagicMock(Table=lambda x: self.mock_dynamodb)):
            self.cache = DynamoDBCache(table_name='test-table')
            self.cache.table = self.mock_dynamodb

    def test_set(self):
        """Test setting an item in the cache."""
        # Create test data
        key = 'test_key'
        value = {'test': 'data'}
        feedback_id = '12345'
        
        # Set the data in the cache
        self.cache.set(key, value, feedback_id=feedback_id)
        
        # Check that the DynamoDB client was called
        self.mock_dynamodb.put_item.assert_called_once()
        
        # Check the arguments
        call_args = self.mock_dynamodb.put_item.call_args[1]
        assert 'Item' in call_args
        assert call_args['Item']['cache_key']['S'] == key
        assert json.loads(call_args['Item']['value']['S']) == value
        assert call_args['Item']['feedback_id']['S'] == feedback_id

    def test_get_existing(self):
        """Test getting an existing item from the cache."""
        # Create test data
        key = 'test_key'
        expected_value = {'test': 'data'}
        
        # Get the data from the cache
        result = self.cache.get(key)
        
        # Check the result
        assert result == expected_value
        
        # Check that the DynamoDB client was called
        self.mock_dynamodb.get_item.assert_called_once_with(
            Key={'cache_key': {'S': key}}
        )

    def test_get_nonexistent(self):
        """Test getting a nonexistent item from the cache."""
        # Configure the mock to return no item
        self.mock_dynamodb.get_item.return_value = {}
        
        # Get a nonexistent key from the cache
        result = self.cache.get('nonexistent_key')
        
        # Check the result
        assert result is None

    def test_get_expired(self):
        """Test getting an expired item from the cache."""
        # Configure the mock to return an expired item
        expired_response = {
            'Item': {
                'cache_key': {'S': 'test_key'},
                'value': {'S': json.dumps({'test': 'data'})},
                'feedback_id': {'S': '12345'},
                'created_at': {'N': str(int(time.time()) - 7200)},
                'expiry': {'N': str(int(time.time()) - 3600)}
            }
        }
        self.mock_dynamodb.get_item.return_value = expired_response
        
        # Get the expired key from the cache
        result = self.cache.get('expired_key')
        
        # Check the result
        assert result is None
        
        # Check that the item was deleted
        self.mock_dynamodb.delete_item.assert_called_once_with(
            Key={'cache_key': {'S': 'expired_key'}}
        )

    def test_delete(self):
        """Test deleting an item from the cache."""
        # Create test data
        key = 'test_key'
        
        # Delete the data from the cache
        self.cache.delete(key)
        
        # Check that the DynamoDB client was called
        self.mock_dynamodb.delete_item.assert_called_once_with(
            Key={'cache_key': {'S': key}}
        )

    def test_clear(self):
        """Test clearing the cache."""
        # Clear the cache
        self.cache.clear()
        
        # Check that the DynamoDB client was called
        self.mock_dynamodb.scan.assert_called_once()
        assert self.mock_dynamodb.delete_item.call_count == 2

    def test_get_by_feedback_id(self):
        """Test getting items by feedback ID."""
        # Create test data
        feedback_id = '12345'
        
        # Configure the mock to return items for the feedback ID
        self.mock_dynamodb.query.return_value = {
            'Items': [
                {
                    'cache_key': {'S': 'test_key1'},
                    'value': {'S': json.dumps({'test': 'data1'})},
                    'feedback_id': {'S': '12345'},
                    'created_at': {'N': str(int(time.time()))},
                    'expiry': {'N': str(int(time.time()) + 3600)}
                }
            ]
        }
        
        # Get the items by feedback ID
        results = self.cache.get_by_feedback_id(feedback_id)
        
        # Check the results
        assert len(results) == 1
        assert results[0] == {'test': 'data1'}
        
        # Check that the DynamoDB client was called
        self.mock_dynamodb.query.assert_called_once()
        call_args = self.mock_dynamodb.query.call_args[1]
        assert call_args['IndexName'] == 'FeedbackIdIndex'
        assert call_args['KeyConditionExpression'] == 'feedback_id = :feedback_id'
        assert call_args['ExpressionAttributeValues'] == {':feedback_id': {'S': feedback_id}}
