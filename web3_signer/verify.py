from typing import TypedDict, Optional
from datetime import datetime

from .decrypt import decrypt
from .message_parser import split_sections, extract_token_domain, extract_token_statement
from .header_parser import parse_headers, normalize_header_keys

class DecryptedBody(TypedDict, total=False):
    domain: Optional[str]
    statement: Optional[str]
    issued_at: str
    expiration_time: str
    web3_token_version: str
    not_before: Optional[str]

class VerifyOpts(TypedDict, total=False):
    domain: Optional[str]

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
    parsed_headers = parse_headers(main_body_section)
    normalized_headers = normalize_header_keys(parsed_headers)

    token_domain = extract_token_domain(body_sections)
    token_statement = extract_token_statement(body_sections)

    required_fields = ['issued-at', 'expiration-time', 'web3-token-version']
    if not all(field in normalized_headers for field in required_fields):
        raise ValueError('Decrypted body is damaged')

    # Convert hyphenated keys to snake_case for Python
    result = {
        key.replace('-', '_'): value
        for key, value in normalized_headers.items()
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