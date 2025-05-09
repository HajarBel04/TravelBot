import os
import json
import hashlib
import time
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class CacheEntry:
    """Represents a single cache entry with metadata."""
    
    def __init__(self, key: str, data: Any, ttl_seconds: int = 86400):
        """
        Initialize a cache entry.
        
        Args:
            key: Cache key
            data: Cached data
            ttl_seconds: Time-to-live in seconds (default: 1 day)
        """
        self.key = key
        self.data = data
        self.created_at = datetime.now()
        self.expires_at = self.created_at + timedelta(seconds=ttl_seconds)
        self.access_count = 0
        self.last_accessed = self.created_at
    
    def is_expired(self) -> bool:
        """Check if this cache entry has expired."""
        return datetime.now() > self.expires_at
    
    def access(self):
        """Record an access to this cache entry."""
        self.access_count += 1
        self.last_accessed = datetime.now()
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization."""
        return {
            "key": self.key,
            "data": self.data,
            "created_at": self.created_at.isoformat(),
            "expires_at": self.expires_at.isoformat(),
            "access_count": self.access_count,
            "last_accessed": self.last_accessed.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'CacheEntry':
        """Create a CacheEntry from a dictionary."""
        entry = cls(data["key"], data["data"])
        entry.created_at = datetime.fromisoformat(data["created_at"])
        entry.expires_at = datetime.fromisoformat(data["expires_at"])
        entry.access_count = data["access_count"]
        entry.last_accessed = datetime.fromisoformat(data["last_accessed"])
        return entry


class ResponseCache:
    """Caching system for travel proposal responses."""
    
    def __init__(self, cache_dir: str = "cache", max_size: int = 1000, 
                ttl_seconds: int = 86400 * 7):  # Default 7 days TTL
        """
        Initialize the response cache.
        
        Args:
            cache_dir: Directory to store cache files
            max_size: Maximum number of items in the cache
            ttl_seconds: Default time-to-live for cache entries
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        self.max_size = max_size
        self.ttl_seconds = ttl_seconds
        
        # Memory cache for fast access
        self.cache = {}
        
        # Load cache from disk
        self.load_cache()
    
    def generate_key(self, email_text: str, parameters: Optional[Dict] = None) -> str:
        """
        Generate a unique cache key for the query.
        
        Args:
            email_text: The email text to create a key for
            parameters: Additional parameters that affect the response
            
        Returns:
            str: A cache key
        """
        # Normalize email text (remove extra whitespace, lowercase)
        normalized_text = ' '.join(email_text.lower().split())
        
        # Create a string representation of parameters
        params_str = ''
        if parameters:
            # Sort keys for deterministic key generation
            params_str = json.dumps(parameters, sort_keys=True)
        
        # Combine and hash
        key_str = f"{normalized_text}|{params_str}"
        return hashlib.md5(key_str.encode('utf-8')).hexdigest()
    
    def get(self, email_text: str, parameters: Optional[Dict] = None) -> Optional[Dict]:
        """
        Get a cached response if available.
        
        Args:
            email_text: The email text to get the response for
            parameters: Additional parameters that affect the response
            
        Returns:
            Optional[Dict]: The cached response or None if not found
        """
        key = self.generate_key(email_text, parameters)
        
        # Check memory cache first
        entry = self.cache.get(key)
        
        if entry is None:
            # Try to load from disk
            entry = self._load_entry_from_disk(key)
            if entry:
                # Add to memory cache
                self.cache[key] = entry
        
        if entry and not entry.is_expired():
            # Record access
            entry.access()
            return entry.data
        
        # Remove expired entry if found
        if entry and entry.is_expired():
            self.remove(key)
        
        return None
    
    def put(self, email_text: str, response_data: Dict, 
           parameters: Optional[Dict] = None, ttl_seconds: Optional[int] = None) -> str:
        """
        Cache a response.
        
        Args:
            email_text: The email text to cache the response for
            response_data: The response data to cache
            parameters: Additional parameters that affect the response
            ttl_seconds: Optional custom TTL in seconds
            
        Returns:
            str: The cache key used
        """
        key = self.generate_key(email_text, parameters)
        ttl = ttl_seconds if ttl_seconds is not None else self.ttl_seconds
        
        # Create cache entry
        entry = CacheEntry(key, response_data, ttl)
        
        # Add to memory cache
        self.cache[key] = entry
        
        # Save to disk
        self._save_entry_to_disk(entry)
        
        # Check cache size
        if len(self.cache) > self.max_size:
            self._evict_entries()
        
        return key
    
    def remove(self, key: str) -> bool:
        """
        Remove a cache entry.
        
        Args:
            key: The cache key to remove
            
        Returns:
            bool: True if removed, False if not found
        """
        # Remove from memory cache
        if key in self.cache:
            del self.cache[key]
            
            # Remove from disk
            cache_file = self.cache_dir / f"{key}.json"
            if cache_file.exists():
                os.remove(cache_file)
            
            return True
        
        return False
    
    def clear(self) -> int:
        """
        Clear all cache entries.
        
        Returns:
            int: Number of entries cleared
        """
        count = len(self.cache)
        
        # Clear memory cache
        self.cache = {}
        
        # Clear disk cache
        for cache_file in self.cache_dir.glob("*.json"):
            os.remove(cache_file)
        
        return count
    
    def _load_entry_from_disk(self, key: str) -> Optional[CacheEntry]:
        """Load a cache entry from disk."""
        cache_file = self.cache_dir / f"{key}.json"
        
        if cache_file.exists():
            try:
                with open(cache_file, 'r') as f:
                    data = json.load(f)
                return CacheEntry.from_dict(data)
            except Exception as e:
                logger.error(f"Error loading cache entry {key}: {e}")
        
        return None
    

    def _save_entry_to_disk(self, entry: CacheEntry) -> bool:
        """Save a cache entry to disk."""
        cache_file = self.cache_dir / f"{entry.key}.json"
        
        try:
            # Create a custom JSON encoder to handle datetime objects
            class DateTimeEncoder(json.JSONEncoder):
                def default(self, obj):
                    if isinstance(obj, datetime.datetime):
                        return obj.isoformat()
                    return super().default(obj)
            
            with open(cache_file, 'w') as f:
                json.dump(entry.to_dict(), f, cls=DateTimeEncoder)
            return True
        except Exception as e:
            logger.error(f"Error saving cache entry {entry.key}: {e}")
            return False

    def _evict_entries(self, count: int = 10) -> int:
        """
        Evict the least recently used entries.
        
        Args:
            count: Number of entries to evict
            
        Returns:
            int: Number of entries evicted
        """
        if not self.cache:
            return 0
        
        # Sort by last access time (oldest first)
        entries_to_evict = sorted(
            self.cache.items(),
            key=lambda x: x[1].last_accessed
        )[:count]
        
        # Remove entries
        for key, _ in entries_to_evict:
            self.remove(key)
        
        return len(entries_to_evict)
    
    def load_cache(self) -> int:
        """
        Load the cache from disk.
        
        Returns:
            int: Number of entries loaded
        """
        # Clear memory cache first
        self.cache = {}
        
        # Load all cache files
        count = 0
        for cache_file in self.cache_dir.glob("*.json"):
            try:
                with open(cache_file, 'r') as f:
                    data = json.load(f)
                
                entry = CacheEntry.from_dict(data)
                
                # Skip expired entries
                if not entry.is_expired():
                    self.cache[entry.key] = entry
                    count += 1
                else:
                    # Remove expired cache file
                    os.remove(cache_file)
            except Exception as e:
                logger.error(f"Error loading cache file {cache_file}: {e}")
        
        logger.info(f"Loaded {count} cache entries from disk")
        return count
    
    def get_statistics(self) -> Dict:
        """Get cache statistics."""
        # Count expired entries
        expired_count = sum(1 for entry in self.cache.values() if entry.is_expired())
        
        # Count entries by access count
        access_counts = {}
        for entry in self.cache.values():
            count_range = f"{(entry.access_count // 10) * 10}-{(entry.access_count // 10 + 1) * 10 - 1}"
            access_counts[count_range] = access_counts.get(count_range, 0) + 1
        
        # Calculate average TTL
        avg_ttl = sum((entry.expires_at - entry.created_at).total_seconds() 
                     for entry in self.cache.values()) / max(1, len(self.cache))
        
        return {
            "total_entries": len(self.cache),
            "expired_entries": expired_count,
            "average_ttl_seconds": avg_ttl,
            "access_counts": access_counts,
        }


class DestinationCache:
    """Special cache for destination-specific data."""
    
    def __init__(self, cache_dir: str = "destination_cache", ttl_days: int = 30):
        """
        Initialize the destination cache.
        
        Args:
            cache_dir: Directory to store destination cache
            ttl_days: Time-to-live in days for destination data
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        self.ttl_seconds = ttl_days * 86400
        
        # Memory cache of destination data
        self.destinations = {}
        
        # Load destination data
        self.load_destinations()
    
    def normalize_destination(self, destination: str) -> str:
        """Normalize a destination name for caching."""
        return destination.lower().strip().replace(" ", "_")
    
    def get_destination_data(self, destination: str) -> Optional[Dict]:
        """
        Get cached data for a destination.
        
        Args:
            destination: The destination name
            
        Returns:
            Optional[Dict]: The cached destination data or None
        """
        normalized = self.normalize_destination(destination)
        
        # Check memory cache
        entry = self.destinations.get(normalized)
        
        if entry is None:
            # Try to load from disk
            entry = self._load_destination_from_disk(normalized)
            if entry:
                # Add to memory cache
                self.destinations[normalized] = entry
        
        if entry and not entry.is_expired():
            # Record access
            entry.access()
            return entry.data
        
        return None
    
    def cache_destination_data(self, destination: str, data: Dict) -> bool:
        """
        Cache data for a destination.
        
        Args:
            destination: The destination name
            data: The destination data to cache
            
        Returns:
            bool: True if cached successfully
        """
        normalized = self.normalize_destination(destination)
        
        # Create cache entry
        entry = CacheEntry(normalized, data, self.ttl_seconds)
        
        # Add to memory cache
        self.destinations[normalized] = entry
        
        # Save to disk
        return self._save_destination_to_disk(entry)
    
    def _load_destination_from_disk(self, normalized_destination: str) -> Optional[CacheEntry]:
        """Load destination data from disk."""
        cache_file = self.cache_dir / f"{normalized_destination}.json"
        
        if cache_file.exists():
            try:
                with open(cache_file, 'r') as f:
                    data = json.load(f)
                return CacheEntry.from_dict(data)
            except Exception as e:
                logger.error(f"Error loading destination {normalized_destination}: {e}")
        
        return None
    
    def _save_destination_to_disk(self, entry: CacheEntry) -> bool:
        """Save destination data to disk."""
        cache_file = self.cache_dir / f"{entry.key}.json"
        
        try:
            with open(cache_file, 'w') as f:
                json.dump(entry.to_dict(), f)
            return True
        except Exception as e:
            logger.error(f"Error saving destination {entry.key}: {e}")
            return False
    
    def load_destinations(self) -> int:
        """
        Load all destinations from disk.
        
        Returns:
            int: Number of destinations loaded
        """
        # Clear memory cache
        self.destinations = {}
        
        # Load all destination files
        count = 0
        for cache_file in self.cache_dir.glob("*.json"):
            try:
                with open(cache_file, 'r') as f:
                    data = json.load(f)
                
                entry = CacheEntry.from_dict(data)
                
                # Skip expired entries
                if not entry.is_expired():
                    self.destinations[entry.key] = entry
                    count += 1
                else:
                    # Remove expired cache file
                    os.remove(cache_file)
            except Exception as e:
                logger.error(f"Error loading destination file {cache_file}: {e}")
        
        logger.info(f"Loaded {count} destinations from disk")
        return count
    
    def get_all_destinations(self) -> List[str]:
        """Get a list of all cached destinations."""
        return [dest.replace("_", " ").title() for dest in self.destinations.keys()]


# Helper function to integrate caching with the RAG pipeline
def process_with_cache(response_cache: ResponseCache, 
                      destination_cache: DestinationCache,
                      email_text: str,
                      process_function: callable,
                      force_refresh: bool = False) -> Tuple[Dict, bool]:
    """
    Process an email with caching support.
    
    Args:
        response_cache: The response cache
        destination_cache: The destination cache
        email_text: The email text to process
        process_function: Function to call if cache miss
        force_refresh: Force processing even if cached
        
    Returns:
        Tuple[Dict, bool]: (response data, was_cached)
    """
    # Try to get from cache if not forcing refresh
    if not force_refresh:
        cached_response = response_cache.get(email_text)
        if cached_response:
            logger.info("Using cached response")
            return cached_response, True
    
    # Process the email
    start_time = time.time()
    response_data = process_function(email_text)
    processing_time = time.time() - start_time
    
    # Add timing information
    response_data['processing_time'] = processing_time
    
    # Cache the response
    response_cache.put(email_text, response_data)
    
    # Try to extract and cache destination data
    if 'extracted_info' in response_data and 'destination' in response_data['extracted_info']:
        destination = response_data['extracted_info']['destination']
        if destination:
            # Check if we already have cached data for this destination
            existing_data = destination_cache.get_destination_data(destination)
            
            if not existing_data:
                # Create destination data from the packages
                if 'recommended_packages' in response_data:
                    destination_data = {
                        'name': destination,
                        'packages': response_data['recommended_packages'],
                        'proposal_excerpt': response_data.get('proposal', '')[:500]
                    }
                    destination_cache.cache_destination_data(destination, destination_data)
    
    return response_data, False