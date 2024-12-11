from typing import List, TypedDict, Optional, Any
from datetime import datetime
import re

from .decrypt import decrypt

class DecryptedBody(TypedDict, total=False):
    domain: Optional[str]
    statement: Optional[str]
    issued_at: str
    expiration_time: str
    web3_token_version: str
    not_before: Optional[str]

class VerifyOpts(TypedDict, total=False):
    domain: Optional[str]

MessageSections = List[List[str]]

def parse_as_headers(text: str) -> dict:
    """
    Parse headers from text into a dictionary.
    """
    headers = {}
    for line in text.split('\n'):
        if ':' in line:
            key, value = line.split(':', 1)
            headers[key.strip()] = value.strip()
    return headers

def split_sections(lines: List[str]) -> MessageSections:
    """
    Parses the lines of a message into an array of message sections.
    
    Args:
        lines: The lines of the message.
    
    Returns:
        An array of message sections.
    """
    sections: MessageSections = [[]]
    for line in lines:
        if line == '':
            sections.append([])
        else:
            sections[len(sections) - 1].append(line)
    return sections

def extract_token_domain(sections: MessageSections) -> Optional[str]:
    """
    Extracts the domain from an array of message sections.
    
    Args:
        sections: An array of message sections.
    
    Returns:
        The domain, or None if it cannot be extracted.
    """
    if not sections[0]:
        return None
    last_line = sections[0][-1]
    if last_line.endswith(' wants you to sign in with your Ethereum account.'):
        return last_line.replace(
            ' wants you to sign in with your Ethereum account.', ''
        ).strip()
    return None

def extract_token_statement(sections: MessageSections) -> Optional[str]:
    """
    Extracts the statement from an array of message sections.
    
    Args:
        sections: An array of message sections.
    
    Returns:
        The statement, or None if it cannot be extracted.
    """
    if len(sections) == 2 and not extract_token_domain(sections):
        return sections[0][0]
    if len(sections) == 3:
        return sections[1][0]
    return None

def parse_body(lines: List[str]) -> DecryptedBody:
    """
    Parses the decrypted body of a token.
    
    Args:
        lines: The lines of the decrypted body.
    
    Returns:
        The parsed decrypted body.
    
    Raises:
        ValueError: If the decrypted body is damaged.
    """
    body_sections = split_sections(lines)
    main_body_section = '\n'.join(body_sections[-1])
    parsed_headers = parse_as_headers(main_body_section)

    # Convert space-separated keys to hyphenated keys
    for key in list(parsed_headers.keys()):
        hyphenated_key = key.replace(' ', '-')
        if hyphenated_key != key:
            parsed_headers[hyphenated_key] = parsed_headers[key]
            del parsed_headers[key]

    token_domain = extract_token_domain(body_sections)
    token_statement = extract_token_statement(body_sections)

    required_fields = ['issued-at', 'expiration-time', 'web3-token-version']
    if not all(field in parsed_headers for field in required_fields):
        raise ValueError('Decrypted body is damaged')

    # Convert hyphenated keys to snake_case for Python
    result = {
        key.replace('-', '_'): value
        for key, value in parsed_headers.items()
    }

    if token_domain:
        result['domain'] = token_domain
    if token_statement:
        result['statement'] = token_statement

    return result

async def verify(token: str, opts: VerifyOpts = None) -> dict:
    """
    Verifies a token.
    
    Args:
        token: The token to verify.
        opts: The options for verifying the token.
    
    Returns:
        The verified token.
    
    Raises:
        ValueError: If the token is expired, not yet valid, has an inappropriate domain,
                   or is version 1.
    
    Example:
        ```python
        from web3_signer import verify

        try:
            result = await verify(token)
            address, body = result['address'], result['body']
            # if you get address and body, the token is valid
        except Exception as error:
            # if you get an error, the token is invalid
            pass
        ```
    """
    opts = opts or {}
    decrypted = await decrypt(token)
    version, address, body = decrypted['version'], decrypted['address'], decrypted['body']

    if version == 1:
        raise ValueError(
            'Tokens version 1 are not supported by the current version of module'
        )

    lines = body.split('\n')
    parsed_body = parse_body(lines)

    expiration_time = datetime.fromisoformat(parsed_body['expiration_time'].replace('Z', '+00:00'))
    if expiration_time < datetime.now():
        raise ValueError('Token expired')

    if parsed_body.get('not_before'):
        not_before = datetime.fromisoformat(parsed_body['not_before'].replace('Z', '+00:00'))
        if not_before > datetime.now():
            raise ValueError("It's not yet time to use the token")

    if opts.get('domain') and opts['domain'] != parsed_body.get('domain'):
        raise ValueError('Inappropriate token domain')

    return {'address': address, 'body': parsed_body} 