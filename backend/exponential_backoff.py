#!/usr/bin/env python3
"""
Exponential Backoff Implementation for API Rate Limiting
Includes base delay, backoff factor, maximum retries, maximum delay, and jitter
"""

import time
import random
import logging
from typing import Callable, Any, Optional, Dict
from functools import wraps
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class ExponentialBackoff:
    """
    Exponential backoff implementation with jitter for API rate limiting
    """
    
    def __init__(
        self,
        base_delay: float = 1.0,
        backoff_factor: float = 2.0,
        max_retries: int = 5,
        max_delay: float = 60.0,
        jitter_type: str = "full",  # "full", "equal", "decorrelated"
        rate_limit_codes: list = None,
        timeout_codes: list = None
    ):
        """
        Initialize exponential backoff configuration
        
        Args:
            base_delay: Initial wait time in seconds
            backoff_factor: Multiplier for exponential increase (typically 2)
            max_retries: Maximum number of retry attempts
            max_delay: Maximum wait time cap in seconds
            jitter_type: Type of jitter to apply ("full", "equal", "decorrelated")
            rate_limit_codes: HTTP status codes that indicate rate limiting
            timeout_codes: HTTP status codes that indicate timeouts
        """
        self.base_delay = base_delay
        self.backoff_factor = backoff_factor
        self.max_retries = max_retries
        self.max_delay = max_delay
        self.jitter_type = jitter_type
        self.rate_limit_codes = rate_limit_codes or [429, 503, 502, 504]
        self.timeout_codes = timeout_codes or [408, 504]
        
        # Track retry statistics
        self.retry_stats = {
            'total_calls': 0,
            'total_retries': 0,
            'successful_calls': 0,
            'failed_calls': 0,
            'rate_limited_calls': 0,
            'timeout_calls': 0
        }
    
    def calculate_delay(self, attempt: int, base_delay: Optional[float] = None) -> float:
        """
        Calculate delay with exponential backoff and jitter
        
        Args:
            attempt: Current attempt number (0-based)
            base_delay: Override base delay for this calculation
            
        Returns:
            Delay in seconds with jitter applied
        """
        if base_delay is None:
            base_delay = self.base_delay
        
        # Calculate exponential delay
        exponential_delay = base_delay * (self.backoff_factor ** attempt)
        
        # Apply maximum delay cap
        capped_delay = min(exponential_delay, self.max_delay)
        
        # Apply jitter
        if self.jitter_type == "full":
            # Full jitter: random value between 0 and calculated delay
            jittered_delay = random.uniform(0, capped_delay)
        elif self.jitter_type == "equal":
            # Equal jitter: half fixed delay + half random
            jittered_delay = capped_delay * 0.5 + random.uniform(0, capped_delay * 0.5)
        elif self.jitter_type == "decorrelated":
            # Decorrelated jitter: more sophisticated randomization
            jittered_delay = random.uniform(base_delay, capped_delay * 3)
            jittered_delay = min(jittered_delay, self.max_delay)
        else:
            # No jitter
            jittered_delay = capped_delay
        
        return max(jittered_delay, 0.1)  # Minimum 0.1 second delay
    
    def should_retry(self, exception: Exception, response_code: Optional[int] = None) -> bool:
        """
        Determine if an exception/response should trigger a retry
        
        Args:
            exception: The exception that occurred
            response_code: HTTP response code if available
            
        Returns:
            True if should retry, False otherwise
        """
        # Check HTTP status codes
        if response_code:
            if response_code in self.rate_limit_codes:
                self.retry_stats['rate_limited_calls'] += 1
                return True
            elif response_code in self.timeout_codes:
                self.retry_stats['timeout_calls'] += 1
                return True
        
        # Check exception types
        exception_str = str(exception).lower()
        retry_indicators = [
            'timeout',
            'connection',
            'rate limit',
            'too many requests',
            'service unavailable',
            'bad gateway',
            'gateway timeout',
            'temporary failure',
            'try again'
        ]
        
        return any(indicator in exception_str for indicator in retry_indicators)
    
    def execute_with_backoff(
        self,
        func: Callable,
        *args,
        **kwargs
    ) -> Any:
        """
        Execute a function with exponential backoff retry logic
        
        Args:
            func: Function to execute
            *args: Positional arguments for the function
            **kwargs: Keyword arguments for the function
            
        Returns:
            Function result if successful
            
        Raises:
            Exception: The last exception if all retries failed
        """
        self.retry_stats['total_calls'] += 1
        last_exception = None
        
        for attempt in range(self.max_retries + 1):
            try:
                # Execute the function
                result = func(*args, **kwargs)
                
                # Success
                if attempt > 0:
                    self.retry_stats['total_retries'] += attempt
                    logger.info(f"Function succeeded after {attempt} retries")
                
                self.retry_stats['successful_calls'] += 1
                return result
                
            except Exception as e:
                last_exception = e
                
                # Don't retry on the last attempt
                if attempt == self.max_retries:
                    break
                
                # Check if we should retry
                response_code = getattr(e, 'response', None)
                if hasattr(response_code, 'status_code'):
                    response_code = response_code.status_code
                elif hasattr(e, 'status_code'):
                    response_code = e.status_code
                else:
                    response_code = None
                
                if not self.should_retry(e, response_code):
                    logger.info(f"Not retrying due to exception type: {type(e).__name__}")
                    break
                
                # Calculate delay and wait
                delay = self.calculate_delay(attempt)
                logger.warning(
                    f"Attempt {attempt + 1} failed: {e}. "
                    f"Retrying in {delay:.2f} seconds..."
                )
                
                time.sleep(delay)
        
        # All retries failed
        self.retry_stats['failed_calls'] += 1
        if self.retry_stats['total_calls'] > 0:
            self.retry_stats['total_retries'] += self.max_retries
        
        logger.error(f"All {self.max_retries + 1} attempts failed. Last error: {last_exception}")
        raise last_exception
    
    def get_stats(self) -> Dict:
        """Get retry statistics"""
        stats = self.retry_stats.copy()
        if stats['total_calls'] > 0:
            stats['success_rate'] = stats['successful_calls'] / stats['total_calls']
            stats['avg_retries_per_call'] = stats['total_retries'] / stats['total_calls']
        else:
            stats['success_rate'] = 0.0
            stats['avg_retries_per_call'] = 0.0
        
        return stats
    
    def reset_stats(self):
        """Reset retry statistics"""
        self.retry_stats = {
            'total_calls': 0,
            'total_retries': 0,
            'successful_calls': 0,
            'failed_calls': 0,
            'rate_limited_calls': 0,
            'timeout_calls': 0
        }

def with_exponential_backoff(
    base_delay: float = 1.0,
    backoff_factor: float = 2.0,
    max_retries: int = 5,
    max_delay: float = 60.0,
    jitter_type: str = "full"
):
    """
    Decorator for applying exponential backoff to functions
    
    Args:
        base_delay: Initial wait time in seconds
        backoff_factor: Multiplier for exponential increase
        max_retries: Maximum number of retry attempts
        max_delay: Maximum wait time cap in seconds
        jitter_type: Type of jitter to apply
    """
    def decorator(func):
        backoff = ExponentialBackoff(
            base_delay=base_delay,
            backoff_factor=backoff_factor,
            max_retries=max_retries,
            max_delay=max_delay,
            jitter_type=jitter_type
        )
        
        @wraps(func)
        def wrapper(*args, **kwargs):
            return backoff.execute_with_backoff(func, *args, **kwargs)
        
        # Attach backoff instance for stats access
        wrapper.backoff = backoff
        return wrapper
    
    return decorator

class RateLimitManager:
    """
    Advanced rate limit manager with per-endpoint tracking
    """
    
    def __init__(self):
        self.endpoint_stats = {}
        self.global_backoff = ExponentialBackoff(
            base_delay=0.5,
            backoff_factor=1.5,
            max_retries=3,
            max_delay=30.0,
            jitter_type="equal"
        )
    
    def get_endpoint_backoff(self, endpoint: str) -> ExponentialBackoff:
        """Get or create backoff instance for specific endpoint"""
        if endpoint not in self.endpoint_stats:
            # Different configurations for different endpoint types
            if 'marketstack' in endpoint.lower():
                # Fast backoff for MarketStack (paid API)
                self.endpoint_stats[endpoint] = ExponentialBackoff(
                    base_delay=1.0,
                    backoff_factor=2.0,
                    max_retries=2,
                    max_delay=10.0,
                    jitter_type="full"
                )
            elif 'yahoo' in endpoint.lower() or 'yfinance' in endpoint.lower():
                # Fast-fail backoff for Yahoo Finance (free API, strict limits)
                self.endpoint_stats[endpoint] = ExponentialBackoff(
                    base_delay=1.0,
                    backoff_factor=2.0,
                    max_retries=2,
                    max_delay=8.0,
                    jitter_type="full"
                )
            elif 'finnhub' in endpoint.lower():
                # Fast backoff for Finnhub (free tier with reasonable limits)
                self.endpoint_stats[endpoint] = ExponentialBackoff(
                    base_delay=1.0,
                    backoff_factor=2.0,
                    max_retries=2,
                    max_delay=5.0,
                    jitter_type="full"
                )
            else:
                # Default backoff for other endpoints
                self.endpoint_stats[endpoint] = ExponentialBackoff()
        
        return self.endpoint_stats[endpoint]
    
    def execute_with_rate_limit(
        self,
        func: Callable,
        endpoint: str,
        *args,
        **kwargs
    ) -> Any:
        """Execute function with endpoint-specific rate limiting"""
        backoff = self.get_endpoint_backoff(endpoint)
        return backoff.execute_with_backoff(func, *args, **kwargs)
    
    def get_all_stats(self) -> Dict:
        """Get statistics for all endpoints"""
        stats = {}
        for endpoint, backoff in self.endpoint_stats.items():
            stats[endpoint] = backoff.get_stats()
        
        # Add global stats
        stats['global'] = self.global_backoff.get_stats()
        return stats

# Global rate limit manager instance
rate_limit_manager = RateLimitManager()

# Convenience functions for common use cases
def retry_on_rate_limit(func, endpoint: str = "default", *args, **kwargs):
    """Convenience function for retrying with rate limit handling"""
    return rate_limit_manager.execute_with_rate_limit(func, endpoint, *args, **kwargs)

def marketstack_retry(func, *args, **kwargs):
    """Convenience function for MarketStack API calls"""
    return rate_limit_manager.execute_with_rate_limit(func, "marketstack", *args, **kwargs)

def yahoo_finance_retry(func, *args, **kwargs):
    """Convenience function for Yahoo Finance API calls"""
    return rate_limit_manager.execute_with_rate_limit(func, "yahoo_finance", *args, **kwargs)

def finnhub_retry(func, *args, **kwargs):
    """Convenience function for Finnhub API calls"""
    return rate_limit_manager.execute_with_rate_limit(func, "finnhub", *args, **kwargs)

# Example usage and testing
if __name__ == "__main__":
    import requests
    
    def test_exponential_backoff():
        """Test exponential backoff functionality"""
        print("🧪 Testing Exponential Backoff Implementation")
        print("=" * 60)
        
        # Test basic backoff calculation
        backoff = ExponentialBackoff(
            base_delay=1.0,
            backoff_factor=2.0,
            max_retries=5,
            max_delay=30.0,
            jitter_type="full"
        )
        
        print("📊 Delay Calculation Test:")
        for attempt in range(6):
            delay = backoff.calculate_delay(attempt)
            print(f"  Attempt {attempt}: {delay:.2f} seconds")
        
        print("\n🔄 Retry Logic Test:")
        
        # Test function that fails first few times
        call_count = 0
        def failing_function():
            nonlocal call_count
            call_count += 1
            if call_count <= 3:
                raise requests.exceptions.HTTPError("429 Too Many Requests")
            return f"Success after {call_count} attempts"
        
        try:
            result = backoff.execute_with_backoff(failing_function)
            print(f"  ✅ Result: {result}")
        except Exception as e:
            print(f"  ❌ Failed: {e}")
        
        print(f"\n📈 Statistics:")
        stats = backoff.get_stats()
        for key, value in stats.items():
            print(f"  {key}: {value}")
        
        # Test rate limit manager
        print(f"\n🎯 Rate Limit Manager Test:")
        
        def test_api_call():
            # Simulate API call that might fail
            if random.random() < 0.7:  # 70% chance of failure
                raise requests.exceptions.HTTPError("429 Too Many Requests")
            return "API call successful"
        
        try:
            result = rate_limit_manager.execute_with_rate_limit(
                test_api_call, "test_endpoint"
            )
            print(f"  ✅ API Result: {result}")
        except Exception as e:
            print(f"  ❌ API Failed: {e}")
        
        print(f"\n📊 Rate Limit Manager Stats:")
        all_stats = rate_limit_manager.get_all_stats()
        for endpoint, stats in all_stats.items():
            print(f"  {endpoint}:")
            for key, value in stats.items():
                print(f"    {key}: {value}")
    
    test_exponential_backoff()

