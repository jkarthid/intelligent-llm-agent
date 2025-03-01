"""
Cache Manager Module

This module implements the cache manager that handles caching of
processed requests and their results.
"""

import json
import logging
import time
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class CacheManager:
    """
    Manager for caching processed requests and their results.
    
    This class provides an interface for caching and retrieving
    processed requests and their results.
    """

    def __init__(self, cache_type: str = 'memory', ttl: int = 3600, **kwargs):
        """
        Initialize the cache manager.
        
        Args:
            cache_type: Type of cache to use ('memory' or 'dynamodb')
            ttl: Time-to-live for cache entries in seconds
            **kwargs: Additional configuration options
        """
        self.cache_type = cache_type.lower()
        self.ttl = ttl
        
        # Initialize the appropriate cache based on the type
        if self.cache_type == 'memory':
            self.cache = {}
        elif self.cache_type == 'dynamodb':
            # Import here to avoid dependency if not using DynamoDB
            from .dynamodb_cache import DynamoDBCache
            self.cache = DynamoDBCache(**kwargs)
        else:
            raise ValueError(f"Unsupported cache type: {self.cache_type}")
        
        # Initialize cache metrics
        self.metrics = {
            'hits': 0,
            'misses': 0,
            'sets': 0
        }

    def get(self, key: str) -> Optional[Dict[str, Any]]:
        """
        Get a value from the cache.
        
        Args:
            key: Cache key
            
        Returns:
            Cached value or None if not found or expired
        """
        # Log the cache request
        logger.debug(f"Cache get request for key: {key}")
        
        # Handle based on cache type
        if self.cache_type == 'memory':
            # Check if the key exists in the cache
            if key in self.cache:
                entry = self.cache[key]
                
                # Check if the entry has expired
                if time.time() < entry['expiry']:
                    # Cache hit
                    self.metrics['hits'] += 1
                    logger.info(f"Cache hit for key: {key}")
                    return entry['value']
                else:
                    # Entry has expired
                    logger.info(f"Cache entry expired for key: {key}")
                    del self.cache[key]
            
            # Cache miss
            self.metrics['misses'] += 1
            logger.info(f"Cache miss for key: {key}")
            return None
        
        elif self.cache_type == 'dynamodb':
            # Use the DynamoDB cache implementation
            result = self.cache.get(key)
            
            if result:
                # Cache hit
                self.metrics['hits'] += 1
                logger.info(f"Cache hit for key: {key}")
            else:
                # Cache miss
                self.metrics['misses'] += 1
                logger.info(f"Cache miss for key: {key}")
            
            return result

    def set(self, key: str, value: Dict[str, Any]) -> None:
        """
        Set a value in the cache.
        
        Args:
            key: Cache key
            value: Value to cache
        """
        # Log the cache set
        logger.debug(f"Cache set request for key: {key}")
        
        # Handle based on cache type
        if self.cache_type == 'memory':
            # Calculate the expiry time
            expiry = time.time() + self.ttl
            
            # Store the value in the cache
            self.cache[key] = {
                'value': value,
                'expiry': expiry
            }
        
        elif self.cache_type == 'dynamodb':
            # Use the DynamoDB cache implementation
            self.cache.set(key, value, self.ttl)
        
        # Update metrics
        self.metrics['sets'] += 1
        logger.info(f"Cache set for key: {key}")

    def delete(self, key: str) -> None:
        """
        Delete a value from the cache.
        
        Args:
            key: Cache key
        """
        # Log the cache delete
        logger.debug(f"Cache delete request for key: {key}")
        
        # Handle based on cache type
        if self.cache_type == 'memory':
            # Delete the key from the cache if it exists
            if key in self.cache:
                del self.cache[key]
                logger.info(f"Cache entry deleted for key: {key}")
            else:
                logger.info(f"Cache entry not found for delete key: {key}")
        
        elif self.cache_type == 'dynamodb':
            # Use the DynamoDB cache implementation
            self.cache.delete(key)
            logger.info(f"Cache entry deleted for key: {key}")

    def clear(self) -> None:
        """Clear all entries from the cache."""
        # Log the cache clear
        logger.debug("Cache clear request")
        
        # Handle based on cache type
        if self.cache_type == 'memory':
            # Clear the in-memory cache
            self.cache = {}
            logger.info("In-memory cache cleared")
        
        elif self.cache_type == 'dynamodb':
            # Use the DynamoDB cache implementation
            self.cache.clear()
            logger.info("DynamoDB cache cleared")
        
        # Reset metrics
        self.metrics = {
            'hits': 0,
            'misses': 0,
            'sets': 0
        }

    def get_metrics(self) -> Dict[str, int]:
        """
        Get cache metrics.
        
        Returns:
            Dictionary containing cache metrics
        """
        return self.metrics
