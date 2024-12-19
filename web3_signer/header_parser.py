def parse_headers(text: str) -> dict:
    """
    Parse headers from text into a dictionary.
    
    Args:
        text: Text containing headers in key: value format
        
    Returns:
        Dictionary of parsed headers
    """
    headers = {}
    for line in text.split('\n'):
        if ':' in line:
            key, value = line.split(':', 1)
            headers[key.strip()] = value.strip()
    return headers

def normalize_header_keys(headers: dict) -> dict:
    """
    Convert space-separated keys to hyphenated keys.
    
    Args:
        headers: Dictionary of headers
        
    Returns:
        Dictionary with normalized keys
    """
    normalized = {}
    for key, value in headers.items():
        normalized_key = key.replace(' ', '-')
        normalized[normalized_key] = value
    return normalized 