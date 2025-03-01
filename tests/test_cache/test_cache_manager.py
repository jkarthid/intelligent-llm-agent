"""
Tests for the Cache Manager Module
"""

import json
import unittest
from unittest.mock import patch, MagicMock

import pytest

from src.cache.cache_manager import CacheManager


class TestCacheManager:
    """Tests for the CacheManager class."""

    def setup_method(self):
        """Set up the test environment."""
        # Create a mock DynamoDB cache
        self.mock_dynamodb_cache = MagicMock()
        self.mock_dynamodb_cache.get.return_value = None
        
        # Create the cache manager with memory cache
        with patch('src.cache.dynamodb_cache.DynamoDBCache', return_value=self.mock_dynamodb_cache):
            self.memory_cache_manager = CacheManager(cache_type='memory')
            self.dynamodb_cache_manager = CacheManager(cache_type='dynamodb')
            self.dynamodb_cache_manager.cache = self.mock_dynamodb_cache

    def test_memory_cache_set_and_get(self):
        """Test setting and getting from the memory cache."""
        # Create test data
        key = 'test_key'
        value = {'test': 'data'}
        
        # Set the data in the cache
        self.memory_cache_manager.set(key, value)
        
        # Get the data from the cache
        result = self.memory_cache_manager.get(key)
        
        # Check the result
        assert result == value

    def test_memory_cache_get_nonexistent(self):
        """Test getting a nonexistent key from the memory cache."""
        # Get a nonexistent key from the cache
        result = self.memory_cache_manager.get('nonexistent_key')
        
        # Check the result
        assert result is None

    def test_memory_cache_delete(self):
        """Test deleting from the memory cache."""
        # Create test data
        key = 'test_key'
        value = {'test': 'data'}
        
        # Set the data in the cache
        self.memory_cache_manager.set(key, value)
        
        # Delete the data from the cache
        self.memory_cache_manager.delete(key)
        
        # Get the data from the cache
        result = self.memory_cache_manager.get(key)
        
        # Check the result
        assert result is None

    def test_memory_cache_clear(self):
        """Test clearing the memory cache."""
        # Create test data
        key1 = 'test_key1'
        value1 = {'test': 'data1'}
        key2 = 'test_key2'
        value2 = {'test': 'data2'}
        
        # Set the data in the cache
        self.memory_cache_manager.set(key1, value1)
        self.memory_cache_manager.set(key2, value2)
        
        # Clear the cache
        self.memory_cache_manager.clear()
        
        # Get the data from the cache
        result1 = self.memory_cache_manager.get(key1)
        result2 = self.memory_cache_manager.get(key2)
        
        # Check the results
        assert result1 is None
        assert result2 is None

    def test_dynamodb_cache_set(self):
        """Test setting in the DynamoDB cache."""
        # Create test data
        key = 'test_key'
        value = {'test': 'data'}
        
        # Set the data in the cache
        self.dynamodb_cache_manager.set(key, value)
        
        # Check that the DynamoDB cache was called
        self.mock_dynamodb_cache.set.assert_called_once_with(key, value)

    def test_dynamodb_cache_get(self):
        """Test getting from the DynamoDB cache."""
        # Create test data
        key = 'test_key'
        value = {'test': 'data'}
        
        # Configure the mock to return the value
        self.mock_dynamodb_cache.get.return_value = value
        
        # Get the data from the cache
        result = self.dynamodb_cache_manager.get(key)
        
        # Check the result
        assert result == value
        
        # Check that the DynamoDB cache was called
        self.mock_dynamodb_cache.get.assert_called_once_with(key)

    def test_dynamodb_cache_delete(self):
        """Test deleting from the DynamoDB cache."""
        # Create test data
        key = 'test_key'
        
        # Delete the data from the cache
        self.dynamodb_cache_manager.delete(key)
        
        # Check that the DynamoDB cache was called
        self.mock_dynamodb_cache.delete.assert_called_once_with(key)

    def test_dynamodb_cache_clear(self):
        """Test clearing the DynamoDB cache."""
        # Clear the cache
        self.dynamodb_cache_manager.clear()
        
        # Check that the DynamoDB cache was called
        self.mock_dynamodb_cache.clear.assert_called_once()

    def test_get_metrics(self):
        """Test getting cache metrics."""
        # Create a cache manager with some activity
        cache_manager = CacheManager(cache_type='memory')
        
        # Set some data
        cache_manager.set('key1', 'value1')
        cache_manager.set('key2', 'value2')
        
        # Get some data (hits)
        cache_manager.get('key1')
        cache_manager.get('key2')
        
        # Get some data (misses)
        cache_manager.get('key3')
        
        # Get the metrics
        metrics = cache_manager.get_metrics()
        
        # Check the metrics
        assert metrics['hits'] == 2
        assert metrics['misses'] == 1
        assert metrics['sets'] == 2
        assert metrics['deletes'] == 0
