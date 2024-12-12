from datetime import datetime, timedelta
import re
from typing import Union

def ms(val: str) -> int:
    """
    Convert a string time span to milliseconds.
    Supports: d (days), h (hours), m (minutes), s (seconds), ms (milliseconds)
    
    Args:
        val: String representing a timespan (e.g., "1d", "20h", "30s")
    
    Returns:
        Number of milliseconds
    
    Raises:
        ValueError: If the format is invalid
    """
    # Regular expression to match number and unit
    pattern = r'^(\d+)([dhms]{1,2})$'
    match = re.match(pattern, val.lower())
    
    if not match:
        return None
        
    number, unit = match.groups()
    number = int(number)
    
    # Convert to milliseconds
    multipliers = {
        'd': 86400000,    # days to ms
        'h': 3600000,     # hours to ms
        'm': 60000,       # minutes to ms
        's': 1000,        # seconds to ms
        'ms': 1           # milliseconds
    }
    
    return number * multipliers.get(unit, 0)

def timespan(val: Union[str, int]) -> datetime:
    """
    Convert a timespan to a future datetime.
    
    Args:
        val: Either a number of milliseconds or a string representing a timespan
             (e.g., "1d", "20h", "30s")
    
    Returns:
        datetime object representing the future time
    
    Raises:
        ValueError: If the input format is invalid
        
    Example:
        >>> timespan("1d")  # returns datetime 24 hours from now
        >>> timespan(3600000)  # returns datetime 1 hour from now
    """
    err_str = (
        '"expires_in" argument should be a number of milliseconds or a '
        'string representing a timespan eg: "1d", "20h", 60'
    )

    if isinstance(val, str):
        milliseconds = ms(val)
        
        if milliseconds is None:
            raise ValueError(err_str)
            
        return datetime.now() + timedelta(milliseconds=milliseconds)
        
    elif isinstance(val, (int, float)):
        return datetime.now() + timedelta(milliseconds=val)
        
    else:
        raise ValueError(err_str) 