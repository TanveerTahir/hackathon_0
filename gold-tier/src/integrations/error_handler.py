#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Error Handler - Comprehensive error handling and graceful degradation.

Provides:
- Retry logic with exponential backoff
- Error categorization
- Graceful degradation patterns
- Error reporting and alerting

Usage:
    from integrations.error_handler import ErrorHandler
    
    error_handler = ErrorHandler()
    
    @error_handler.handle
    def risky_operation():
        ...
"""

import asyncio
import logging
import time
import json
from datetime import datetime, timedelta
from functools import wraps
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Type
from enum import Enum


class ErrorSeverity(Enum):
    """Error severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ErrorCategory(Enum):
    """Error categories"""
    NETWORK = "network"
    AUTHENTICATION = "authentication"
    RATE_LIMIT = "rate_limit"
    VALIDATION = "validation"
    SYSTEM = "system"
    UNKNOWN = "unknown"


class ErrorHandler:
    """
    Comprehensive error handler with retry logic and graceful degradation.
    """

    def __init__(
        self,
        max_retries: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 60.0,
        exponential_base: float = 2.0,
        logs_dir: str = None,
        alert_on_critical: bool = True
    ):
        """
        Initialize the error handler.

        Args:
            max_retries: Maximum number of retry attempts
            base_delay: Base delay between retries in seconds
            max_delay: Maximum delay between retries
            exponential_base: Base for exponential backoff
            logs_dir: Directory for error logs
            alert_on_critical: Whether to alert on critical errors
        """
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.exponential_base = exponential_base
        self.alert_on_critical = alert_on_critical

        # Setup logs directory
        if logs_dir:
            self.logs_dir = Path(logs_dir)
        else:
            self.logs_dir = Path.cwd() / 'Logs'

        self.logs_dir.mkdir(parents=True, exist_ok=True)

        # Error tracking
        self.error_counts: Dict[str, int] = {}
        self.last_error_time: Dict[str, datetime] = {}
        self.circuit_breaker_open: Dict[str, datetime] = {}

        # Setup logging
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.setLevel(logging.INFO)

        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)

    def categorize_error(self, error: Exception) -> ErrorCategory:
        """
        Categorize an error based on its type and message.

        Args:
            error: Exception to categorize

        Returns:
            ErrorCategory enum value
        """
        error_name = type(error).__name__
        error_msg = str(error).lower()

        # Network errors
        if error_name in ['ConnectionError', 'Timeout', 'RequestException']:
            return ErrorCategory.NETWORK
        if 'network' in error_msg or 'connection' in error_msg:
            return ErrorCategory.NETWORK

        # Authentication errors
        if error_name in ['AuthenticationError', 'Unauthorized', 'Forbidden']:
            return ErrorCategory.AUTHENTICATION
        if 'auth' in error_msg or 'unauthorized' in error_msg or 'forbidden' in error_msg:
            return ErrorCategory.AUTHENTICATION

        # Rate limit errors
        if error_name in ['RateLimitError', 'TooManyRequests']:
            return ErrorCategory.RATE_LIMIT
        if 'rate limit' in error_msg or '429' in error_msg:
            return ErrorCategory.RATE_LIMIT

        # Validation errors
        if error_name in ['ValidationError', 'ValueError', 'TypeError']:
            return ErrorCategory.VALIDATION

        # System errors
        if error_name in ['SystemError', 'RuntimeError', 'OSError']:
            return ErrorCategory.SYSTEM

        return ErrorCategory.UNKNOWN

    def get_severity(self, error: Exception, category: ErrorCategory) -> ErrorSeverity:
        """
        Determine error severity.

        Args:
            error: Exception
            category: Error category

        Returns:
            ErrorSeverity enum value
        """
        if category == ErrorCategory.AUTHENTICATION:
            return ErrorSeverity.CRITICAL
        elif category == ErrorCategory.RATE_LIMIT:
            return ErrorSeverity.HIGH
        elif category == ErrorCategory.NETWORK:
            return ErrorSeverity.MEDIUM
        elif category == ErrorCategory.VALIDATION:
            return ErrorSeverity.LOW
        else:
            return ErrorSeverity.MEDIUM

    def calculate_delay(self, attempt: int, error: Exception = None) -> float:
        """
        Calculate delay for retry with exponential backoff.

        Args:
            attempt: Current attempt number
            error: Exception that triggered retry

        Returns:
            Delay in seconds
        """
        # Base exponential backoff
        delay = self.base_delay * (self.exponential_base ** attempt)

        # Add jitter (±10%)
        import random
        jitter = delay * 0.1 * (2 * random.random() - 1)
        delay += jitter

        # Cap at max delay
        return min(delay, self.max_delay)

    def should_retry(self, error_key: str, error: Exception) -> bool:
        """
        Determine if operation should be retried.

        Args:
            error_key: Unique key for the operation
            error: Exception that occurred

        Returns:
            True if should retry, False otherwise
        """
        category = self.categorize_error(error)

        # Don't retry authentication errors
        if category == ErrorCategory.AUTHENTICATION:
            return False

        # Check circuit breaker
        if error_key in self.circuit_breaker_open:
            open_time = self.circuit_breaker_open[error_key]
            if datetime.now() - open_time < timedelta(minutes=5):
                return False
            else:
                # Reset circuit breaker
                del self.circuit_breaker_open[error_key]

        # Check error count
        count = self.error_counts.get(error_key, 0)
        return count < self.max_retries

    def record_error(self, error_key: str, error: Exception):
        """
        Record an error for tracking.

        Args:
            error_key: Unique key for the operation
            error: Exception that occurred
        """
        self.error_counts[error_key] = self.error_counts.get(error_key, 0) + 1
        self.last_error_time[error_key] = datetime.now()

        # Open circuit breaker if too many errors
        if self.error_counts[error_key] >= self.max_retries:
            self.circuit_breaker_open[error_key] = datetime.now()
            self.logger.warning(f"Circuit breaker opened for {error_key}")

    def reset_error_count(self, error_key: str):
        """
        Reset error count for successful operation.

        Args:
            error_key: Unique key for the operation
        """
        if error_key in self.error_counts:
            del self.error_counts[error_key]
        if error_key in self.last_error_time:
            del self.last_error_time[error_key]

    def log_error(
        self,
        error: Exception,
        context: str = "",
        operation: str = "",
        attempt: int = 0
    ):
        """
        Log error with comprehensive details.

        Args:
            error: Exception
            context: Additional context
            operation: Operation name
            attempt: Attempt number
        """
        category = self.categorize_error(error)
        severity = self.get_severity(error, category)

        error_details = {
            'timestamp': datetime.now().isoformat(),
            'error_type': type(error).__name__,
            'error_message': str(error),
            'category': category.value,
            'severity': severity.value,
            'operation': operation,
            'context': context,
            'attempt': attempt
        }

        # Log to file
        log_file = self.logs_dir / f"errors_{datetime.now().strftime('%Y-%m-%d')}.jsonl"
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(error_details) + '\n')

        # Log to console
        log_level = {
            ErrorSeverity.LOW: logging.INFO,
            ErrorSeverity.MEDIUM: logging.WARNING,
            ErrorSeverity.HIGH: logging.ERROR,
            ErrorSeverity.CRITICAL: logging.CRITICAL
        }.get(severity, logging.WARNING)

        self.logger.log(
            log_level,
            f"{operation} error (attempt {attempt}): {str(error)}"
        )

        # Alert on critical
        if severity == ErrorSeverity.CRITICAL and self.alert_on_critical:
            self._send_critical_alert(error_details)

    def _send_critical_alert(self, error_details: Dict[str, Any]):
        """
        Send alert for critical error.

        Args:
            error_details: Error details dictionary
        """
        # In production, this would send email/SMS/notification
        alert_file = self.logs_dir / f"critical_alerts_{datetime.now().strftime('%Y-%m-%d')}.md"

        alert_content = f"""---
type: critical_alert
timestamp: {error_details['timestamp']}
operation: {error_details['operation']}
error_type: {error_details['error_type']}
---

# ⚠️ Critical Error Alert

**Operation:** {error_details['operation']}

**Error:** {error_details['error_type']}

**Message:** {error_details['error_message']}

**Context:** {error_details['context']}

**Attempt:** {error_details['attempt']}

---
*Generated by Error Handler*
"""

        with open(alert_file, 'a', encoding='utf-8') as f:
            f.write(alert_content + '\n\n')

    def handle(
        self,
        func: Callable = None,
        error_key: str = None,
        fallback: Any = None,
        retryable_exceptions: List[Type[Exception]] = None
    ):
        """
        Decorator for handling errors with retry logic.

        Args:
            func: Function to decorate
            error_key: Unique key for error tracking
            fallback: Fallback value on failure
            retryable_exceptions: List of exceptions to retry

        Returns:
            Decorated function
        """
        if func is None:
            return lambda f: self.handle(
                f,
                error_key=error_key or f.__name__,
                fallback=fallback,
                retryable_exceptions=retryable_exceptions
            )

        key = error_key or func.__name__
        exceptions = retryable_exceptions or [Exception]

        @wraps(func)
        def wrapper(*args, **kwargs):
            last_error = None

            for attempt in range(self.max_retries + 1):
                try:
                    result = func(*args, **kwargs)
                    self.reset_error_count(key)
                    return result

                except Exception as e:
                    last_error = e

                    # Check if exception is retryable
                    if not any(isinstance(e, exc_type) for exc_type in exceptions):
                        raise

                    # Log error
                    self.log_error(e, operation=key, attempt=attempt + 1)

                    # Check if should retry
                    if not self.should_retry(key, e):
                        break

                    # Record error
                    self.record_error(key, e)

                    # Calculate and wait for delay
                    if attempt < self.max_retries:
                        delay = self.calculate_delay(attempt, e)
                        self.logger.info(f"Retrying {key} in {delay:.2f}s...")
                        time.sleep(delay)

            # All retries exhausted
            error_msg = f"{key} failed after {self.max_retries + 1} attempts"
            self.logger.error(error_msg)

            if fallback is not None:
                return fallback

            raise last_error

        return wrapper

    async def handle_async(
        self,
        func: Callable,
        error_key: str = None,
        fallback: Any = None,
        retryable_exceptions: List[Type[Exception]] = None
    ):
        """
        Async version of error handler.

        Args:
            func: Async function to decorate
            error_key: Unique key for error tracking
            fallback: Fallback value on failure
            retryable_exceptions: List of exceptions to retry

        Returns:
            Decorated async function
        """
        key = error_key or func.__name__
        exceptions = retryable_exceptions or [Exception]

        @wraps(func)
        async def wrapper(*args, **kwargs):
            last_error = None

            for attempt in range(self.max_retries + 1):
                try:
                    result = await func(*args, **kwargs)
                    self.reset_error_count(key)
                    return result

                except Exception as e:
                    last_error = e

                    # Check if exception is retryable
                    if not any(isinstance(e, exc_type) for exc_type in exceptions):
                        raise

                    # Log error
                    self.log_error(e, operation=key, attempt=attempt + 1)

                    # Check if should retry
                    if not self.should_retry(key, e):
                        break

                    # Record error
                    self.record_error(key, e)

                    # Calculate and wait for delay
                    if attempt < self.max_retries:
                        delay = self.calculate_delay(attempt, e)
                        self.logger.info(f"Retrying {key} in {delay:.2f}s...")
                        await asyncio.sleep(delay)

            # All retries exhausted
            error_msg = f"{key} failed after {self.max_retries + 1} attempts"
            self.logger.error(error_msg)

            if fallback is not None:
                return fallback

            raise last_error

        return wrapper

    def get_error_report(self) -> Dict[str, Any]:
        """
        Generate error report.

        Returns:
            Dictionary with error statistics
        """
        return {
            'error_counts': self.error_counts.copy(),
            'circuit_breakers_open': list(self.circuit_breaker_open.keys()),
            'last_error_times': {
                k: v.isoformat() for k, v in self.last_error_time.items()
            }
        }


# Global error handler instance
global_error_handler = ErrorHandler()


def handle_errors(
    func: Callable = None,
    error_key: str = None,
    fallback: Any = None
):
    """
    Convenience decorator using global error handler.

    Usage:
        @handle_errors
        def my_function():
            ...

        @handle_errors(error_key="custom_key", fallback=None)
        def another_function():
            ...
    """
    return global_error_handler.handle(func, error_key, fallback)
