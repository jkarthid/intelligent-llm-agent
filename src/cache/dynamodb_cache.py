"""
DynamoDB Cache Module

This module implements the DynamoDB cache for storing processed
requests and their results.
"""

import json
import logging
import time
from typing import Dict, Any, Optional

import boto3
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)


class DynamoDBCache:
    """
    DynamoDB implementation of the cache.
    
    This class provides an interface for caching and retrieving
    processed requests and their results using DynamoDB.
    """

    def __init__(self, table_name: str = 'LLMAgentCache', 
                 region: str = 'us-east-1', **kwargs):
        """
        Initialize the DynamoDB cache.
        
        Args:
            table_name: Name of the DynamoDB table
            region: AWS region
            **kwargs: Additional configuration options
        """
        self.table_name = table_name
        
        # Initialize the DynamoDB client
        self.dynamodb = boto3.resource('dynamodb', region_name=region)
        self.table = self.dynamodb.Table(self.table_name)

    def get(self, key: str) -> Optional[Dict[str, Any]]:
        """
        Get a value from the cache.
        
        Args:
            key: Cache key
            
        Returns:
            Cached value or None if not found or expired
        """
        try:
            # Get the item from DynamoDB
            response = self.table.get_item(
                Key={
                    'cache_key': key
                }
            )
            
            # Check if the item exists
            if 'Item' in response:
                item = response['Item']
                
                # Check if the item has expired
                if 'expiry' in item and item['expiry'] < int(time.time()):
                    # Item has expired, delete it
                    logger.info(f"Cache entry expired for key: {key}")
                    self.delete(key)
                    return None
                
                # Return the cached result
                return json.loads(item['cached_result'])
            
            # Item not found
            return None
        
        except ClientError as e:
            logger.error(f"Error getting item from DynamoDB: {str(e)}")
            return None

    def set(self, key: str, value: Dict[str, Any], ttl: int = 3600) -> None:
        """
        Set a value in the cache.
        
        Args:
            key: Cache key
            value: Value to cache
            ttl: Time-to-live in seconds
        """
        try:
            # Calculate the expiry time
            expiry = int(time.time()) + ttl
            
            # Extract the feedback_id if present
            feedback_id = value.get('feedback_id', '')
            
            # Store the item in DynamoDB
            self.table.put_item(
                Item={
                    'cache_key': key,
                    'feedback_id': feedback_id,
                    'cached_result': json.dumps(value),
                    'expiry': expiry,
                    'last_updated': int(time.time())
                }
            )
        
        except ClientError as e:
            logger.error(f"Error setting item in DynamoDB: {str(e)}")

    def delete(self, key: str) -> None:
        """
        Delete a value from the cache.
        
        Args:
            key: Cache key
        """
        try:
            # Delete the item from DynamoDB
            self.table.delete_item(
                Key={
                    'cache_key': key
                }
            )
        
        except ClientError as e:
            logger.error(f"Error deleting item from DynamoDB: {str(e)}")

    def clear(self) -> None:
        """Clear all entries from the cache."""
        try:
            # Scan the table to get all items
            response = self.table.scan()
            
            # Delete each item
            with self.table.batch_writer() as batch:
                for item in response.get('Items', []):
                    batch.delete_item(
                        Key={
                            'cache_key': item['cache_key']
                        }
                    )
            
            # Continue scanning and deleting if there are more items
            while 'LastEvaluatedKey' in response:
                response = self.table.scan(
                    ExclusiveStartKey=response['LastEvaluatedKey']
                )
                
                with self.table.batch_writer() as batch:
                    for item in response.get('Items', []):
                        batch.delete_item(
                            Key={
                                'cache_key': item['cache_key']
                            }
                        )
        
        except ClientError as e:
            logger.error(f"Error clearing DynamoDB cache: {str(e)}")
