"""
Cache Manager using Redis for caching API responses and model outputs
"""
import json
import time
from typing import Optional, Dict, Any

import redis

from .config import get_settings


class CacheManager:
    """Redis-based cache manager"""
    
    def __init__(self):
        self.settings = get_settings()
        try:
            self.redis_client = redis.Redis(
                host=self.settings.redis_host,
                port=self.settings.redis_port,
                db=self.settings.redis_db,
                decode_responses=True
            )
            # Test connection
            self.redis_client.ping()
            print("[SUCCESS] Redis cache connected")
        except redis.ConnectionError:
            print("[WARNING] Redis not available, using memory cache")
            self.redis_client = None
            self._memory_cache = {}
    
    def _serialize_value(self, value: Any) -> str:
        """Serialize value for storage"""
        return json.dumps(value, default=str)
    
    def _deserialize_value(self, value: str) -> Any:
        """Deserialize value from storage"""
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            return value
    
    def set(self, key: str, value: Any, ttl: int = 3600) -> bool:
        """Set a cache value with TTL"""
        try:
            serialized = self._serialize_value(value)
            
            if self.redis_client:
                return self.redis_client.setex(key, ttl, serialized)
            else:
                # Fallback to memory cache
                self._memory_cache[key] = {
                    'value': serialized,
                    'expires': time.time() + ttl
                }
                return True
        except Exception as e:
            print(f"Cache set error: {e}")
            return False
    
    def get(self, key: str) -> Optional[Any]:
        """Get a cache value"""
        try:
            if self.redis_client:
                value = self.redis_client.get(key)
                if value:
                    return self._deserialize_value(value)
            else:
                # Fallback to memory cache
                if key in self._memory_cache:
                    cache_item = self._memory_cache[key]
                    if time.time() < cache_item['expires']:
                        return self._deserialize_value(cache_item['value'])
                    else:
                        del self._memory_cache[key]
            
            return None
        except Exception as e:
            print(f"Cache get error: {e}")
            return None
    
    def delete(self, key: str) -> bool:
        """Delete a cache value"""
        try:
            if self.redis_client:
                return bool(self.redis_client.delete(key))
            else:
                if key in self._memory_cache:
                    del self._memory_cache[key]
                    return True
            return False
        except Exception as e:
            print(f"Cache delete error: {e}")
            return False
    
    def exists(self, key: str) -> bool:
        """Check if key exists in cache"""
        try:
            if self.redis_client:
                return bool(self.redis_client.exists(key))
            else:
                if key in self._memory_cache:
                    cache_item = self._memory_cache[key]
                    if time.time() < cache_item['expires']:
                        return True
                    else:
                        del self._memory_cache[key]
            return False
        except Exception as e:
            print(f"Cache exists error: {e}")
            return False
    
    # Specialized cache methods
    def cache_api_response(self, api_name: str, endpoint: str, params: Dict, response: Any, ttl: int = 900):
        """Cache API response for 15 minutes by default"""
        cache_key = f"api:{api_name}:{endpoint}:{hash(str(sorted(params.items())))}"
        return self.set(cache_key, response, ttl)
    
    def get_api_response(self, api_name: str, endpoint: str, params: Dict) -> Optional[Any]:
        """Get cached API response"""
        cache_key = f"api:{api_name}:{endpoint}:{hash(str(sorted(params.items())))}"
        return self.get(cache_key)
    
    def cache_model_output(self, content_hash: str, result: Any, ttl: int = 3600):
        """Cache AI model output for 1 hour by default"""
        cache_key = f"model_output:{content_hash}"
        return self.set(cache_key, result, ttl)
    
    def get_model_output(self, content_hash: str) -> Optional[Any]:
        """Get cached AI model output"""
        cache_key = f"model_output:{content_hash}"
        return self.get(cache_key)
    
    def cache_user_token(self, user_id: str, token_data: Dict, ttl: int = 3600):
        """Cache user authentication token"""
        cache_key = f"token:{user_id}"
        return self.set(cache_key, token_data, ttl)
    
    def get_user_token(self, user_id: str) -> Optional[Dict]:
        """Get cached user token"""
        cache_key = f"token:{user_id}"
        return self.get(cache_key)
    
    def check_rate_limit(self, api_name: str, identifier: str, limit: int, window: int) -> tuple[bool, int]:
        """Check and update rate limit"""
        current_time = int(time.time())
        window_start = current_time - (current_time % window)
        key = f"rate_limit:{api_name}:{identifier}:{window_start}"
        
        try:
            if self.redis_client:
                current_count = self.redis_client.incr(key)
                self.redis_client.expire(key, window)
            else:
                # Memory-based rate limiting
                if key not in self._memory_cache:
                    self._memory_cache[key] = {
                        'value': 1,
                        'expires': time.time() + window
                    }
                    current_count = 1
                else:
                    cache_item = self._memory_cache[key]
                    if time.time() < cache_item['expires']:
                        cache_item['value'] += 1
                        current_count = cache_item['value']
                    else:
                        self._memory_cache[key] = {
                            'value': 1,
                            'expires': time.time() + window
                        }
                        current_count = 1
            
            return current_count <= limit, current_count
            
        except Exception as e:
            print(f"Rate limit check error: {e}")
            return True, 0  # Allow request on error
    
    def clear_pattern(self, pattern: str):
        """Clear all keys matching pattern (Redis only)"""
        if self.redis_client:
            try:
                keys = self.redis_client.keys(pattern)
                if keys:
                    self.redis_client.delete(*keys)
                    return len(keys)
            except Exception as e:
                print(f"Clear pattern error: {e}")
        return 0
    
    def flush_all(self):
        """Clear all cache"""
        try:
            if self.redis_client:
                self.redis_client.flushdb()
            else:
                self._memory_cache.clear()
            return True
        except Exception as e:
            print(f"Flush all error: {e}")
            return False