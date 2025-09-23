#!/usr/bin/env python3
"""
Cache Manager for API responses and automation workflow
"""

import os
import json
import time
from datetime import datetime
from typing import Optional, Dict, Any

class CacheManager:
    """Manages caching for API responses and automation data."""

    def __init__(self, cache_dir: str = None):
        """
        Initialize cache manager.

        Args:
            cache_dir: Directory to store cache files. Defaults to ./cache/
        """
        if cache_dir is None:
            # Set cache directory at project level
            current_dir = os.path.dirname(os.path.abspath(__file__))
            project_dir = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))
            cache_dir = os.path.join(project_dir, "cache")

        self.cache_dir = cache_dir
        self.ensure_cache_dir()

    def ensure_cache_dir(self):
        """Create cache directory if it doesn't exist."""
        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir)
            print(f"📁 Created cache directory: {self.cache_dir}")

    def _get_cache_file_path(self, cache_key: str) -> str:
        """Get full path for cache file."""
        safe_key = "".join(c for c in cache_key if c.isalnum() or c in ('-', '_', '.'))
        return os.path.join(self.cache_dir, f"{safe_key}.json")

    def save_api_response(self, api_type: str, response_data: str, metadata: Dict[str, Any] = None) -> str:
        """
        Save API response to cache.

        Args:
            api_type: Type of API (e.g., 'text_generation', 'tts')
            response_data: The actual response content
            metadata: Additional metadata about the response

        Returns:
            str: Cache key for retrieval
        """
        try:
            timestamp = int(time.time())
            cache_key = f"{api_type}_{timestamp}"

            cache_data = {
                "cache_key": cache_key,
                "api_type": api_type,
                "response_data": response_data,
                "metadata": metadata or {},
                "created_at": datetime.now().isoformat(),
                "timestamp": timestamp,
                "content_length": len(response_data) if response_data else 0
            }

            cache_file = self._get_cache_file_path(cache_key)

            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, ensure_ascii=False, indent=2)

            print(f"💾 Saved API response to cache: {cache_key}")
            print(f"   File: {cache_file}")
            print(f"   Content length: {cache_data['content_length']} chars")

            return cache_key

        except Exception as e:
            print(f"❌ Error saving to cache: {e}")
            return None

    def get_latest_response(self, api_type: str = None) -> Optional[Dict[str, Any]]:
        """
        Get the most recent cached response.

        Args:
            api_type: Filter by API type. If None, gets latest regardless of type.

        Returns:
            Dict containing cached data or None if not found
        """
        try:
            cache_files = []

            # Find all cache files
            for file in os.listdir(self.cache_dir):
                if file.endswith('.json'):
                    file_path = os.path.join(self.cache_dir, file)
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            data = json.load(f)

                        # Filter by API type if specified
                        if api_type is None or data.get('api_type') == api_type:
                            cache_files.append((data.get('timestamp', 0), file_path, data))
                    except:
                        continue

            if not cache_files:
                print(f"📭 No cached responses found" + (f" for {api_type}" if api_type else ""))
                return None

            # Sort by timestamp and get latest
            cache_files.sort(key=lambda x: x[0], reverse=True)
            latest_data = cache_files[0][2]

            print(f"📤 Retrieved latest cached response:")
            print(f"   Cache key: {latest_data.get('cache_key')}")
            print(f"   API type: {latest_data.get('api_type')}")
            print(f"   Created: {latest_data.get('created_at')}")
            print(f"   Content length: {latest_data.get('content_length')} chars")

            return latest_data

        except Exception as e:
            print(f"❌ Error reading from cache: {e}")
            return None

    def get_response_by_key(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """
        Get cached response by specific cache key.

        Args:
            cache_key: The cache key to retrieve

        Returns:
            Dict containing cached data or None if not found
        """
        try:
            cache_file = self._get_cache_file_path(cache_key)

            if not os.path.exists(cache_file):
                print(f"📭 Cache file not found: {cache_key}")
                return None

            with open(cache_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            print(f"📤 Retrieved cached response: {cache_key}")
            print(f"   Content length: {data.get('content_length')} chars")

            return data

        except Exception as e:
            print(f"❌ Error reading cache key {cache_key}: {e}")
            return None

    def list_cached_responses(self, api_type: str = None) -> list:
        """
        List all cached responses.

        Args:
            api_type: Filter by API type. If None, lists all.

        Returns:
            List of cache metadata
        """
        try:
            responses = []

            for file in os.listdir(self.cache_dir):
                if file.endswith('.json'):
                    file_path = os.path.join(self.cache_dir, file)
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            data = json.load(f)

                        # Filter by API type if specified
                        if api_type is None or data.get('api_type') == api_type:
                            responses.append({
                                'cache_key': data.get('cache_key'),
                                'api_type': data.get('api_type'),
                                'created_at': data.get('created_at'),
                                'content_length': data.get('content_length'),
                                'file_path': file_path
                            })
                    except:
                        continue

            # Sort by timestamp (newest first)
            responses.sort(key=lambda x: x.get('created_at', ''), reverse=True)

            print(f"📋 Found {len(responses)} cached responses" + (f" for {api_type}" if api_type else ""))
            for resp in responses[:5]:  # Show first 5
                print(f"   {resp['cache_key']} - {resp['api_type']} - {resp['content_length']} chars")

            return responses

        except Exception as e:
            print(f"❌ Error listing cache: {e}")
            return []

    def clear_cache(self, api_type: str = None, older_than_hours: int = None):
        """
        Clear cached responses.

        Args:
            api_type: Clear only specific API type. If None, clears all.
            older_than_hours: Clear only files older than X hours. If None, clears all.
        """
        try:
            deleted_count = 0
            current_time = time.time()

            for file in os.listdir(self.cache_dir):
                if file.endswith('.json'):
                    file_path = os.path.join(self.cache_dir, file)

                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            data = json.load(f)

                        should_delete = True

                        # Check API type filter
                        if api_type and data.get('api_type') != api_type:
                            should_delete = False

                        # Check age filter
                        if older_than_hours and should_delete:
                            file_timestamp = data.get('timestamp', 0)
                            age_hours = (current_time - file_timestamp) / 3600
                            if age_hours < older_than_hours:
                                should_delete = False

                        if should_delete:
                            os.remove(file_path)
                            deleted_count += 1
                            print(f"🗑️ Deleted cache: {data.get('cache_key')}")

                    except:
                        continue

            print(f"✅ Cleared {deleted_count} cached responses")

        except Exception as e:
            print(f"❌ Error clearing cache: {e}")

# Global cache manager instance
cache_manager = CacheManager()

def save_api_response(api_type: str, response_data: str, metadata: Dict[str, Any] = None) -> str:
    """Convenient function to save API response to cache."""
    return cache_manager.save_api_response(api_type, response_data, metadata)

def get_latest_text_generation() -> Optional[str]:
    """Get the latest text generation response content."""
    data = cache_manager.get_latest_response('text_generation')
    return data.get('response_data') if data else None

def get_latest_response_data(api_type: str = None) -> Optional[str]:
    """Get the latest response data for any API type."""
    data = cache_manager.get_latest_response(api_type)
    return data.get('response_data') if data else None