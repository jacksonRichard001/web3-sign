import re
from datetime import datetime
from urllib.parse import urlparse
from typing import Any

def is_valid_string(value: Any) -> bool:
    """
    Check if a value is a non-empty string.
    
    Args:
        value: Any value to check
    
    Returns:
        True if value is a non-empty string, False otherwise
    """
    return isinstance(value, str) and len(value.strip()) > 0

def is_valid_domain(value: Any) -> bool:
    """
    Check if a value is a valid domain name.
    
    Args:
        value: Any value to check
    
    Returns:
        True if value is a valid domain name, False otherwise
    """
    if not isinstance(value, str):
        return False
        
    domain_regex = r'^[a-z0-9]+([-.]{1}[a-z0-9]+)*\.[a-z]{2,}$'
    return bool(re.match(domain_regex, value, re.IGNORECASE))

def is_url(value: Any) -> bool:
    """
    Check if a value is a valid URL.
    
    Args:
        value: Any value to check
    
    Returns:
        True if value is a valid URL, False otherwise
    """
    if not isinstance(value, str):
        return False
        
    try:
        result = urlparse(value)
        return all([result.scheme, result.netloc])
    except ValueError:
        return False

def is_number(value: Any) -> bool:
    """
    Check if a value is a valid number.
    
    Args:
        value: Any value to check
    
    Returns:
        True if value is a number (not NaN), False otherwise
    """
    return isinstance(value, (int, float)) and not isinstance(value, bool)

def is_date(value: Any) -> bool:
    """
    Check if a value is a datetime instance.
    
    Args:
        value: Any value to check
    
    Returns:
        True if value is a datetime instance, False otherwise
    """
    return isinstance(value, datetime) 