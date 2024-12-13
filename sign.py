import base64
import json
import random
from datetime import datetime
from typing import Any, Callable, Optional, TypedDict, Union
from urllib.parse import urlparse

from .timespan import timespan
from .utils import is_valid_domain, is_url

class SignBody(TypedDict, total=False):
    web3_token_version: str
    issued_at: datetime
    expiration_time: datetime
    not_before: Optional[datetime]
    chain_id: Optional[int]
    uri: Optional[str]
    nonce: Optional[int]
    request_id: Optional[str]
    domain: Optional[str]
    statement: Optional[str]

class SignOpts(TypedDict, total=False):
    domain: Optional[str]
    uri: Optional[str]
    chain_id: Optional[int]
    expiration_time: Optional[datetime]
    expires_in: Optional[Union[str, int]]
    not_before: Optional[datetime]
    nonce: Optional[bool]
    request_id: Optional[str]
    statement: Optional[str]

Signer = Callable[[str], str]

def validate_params(params: SignOpts) -> None:
    """
    Validate sign parameters.
    
    Args:
        params: Parameters to validate
    
    Raises:
        ValueError: If any parameter is invalid
    """
    for key, value in params.items():
        if isinstance(value, str) and '\n' in value:
            raise ValueError(f'"{key}" option cannot have LF (\\n)')

    if 'domain' in params:
        domain = params['domain']
        if not isinstance(domain, str) or not is_valid_domain(domain):
            raise ValueError('Invalid domain format (must be example.com)')

    if 'uri' in params:
        uri = params['uri']
        if not isinstance(uri, str) or not is_url(uri):
            raise ValueError('Invalid uri format (must be https://example.com/login)')

    if 'chain_id' in params:
        chain_id = params['chain_id']
        if not isinstance(chain_id, (int, float)):
            raise ValueError('chain_id must be an int')

    if 'expiration_time' in params:
        expiration_time = params['expiration_time']
        if not isinstance(expiration_time, datetime):
            raise ValueError('expiration_time must be an instance of datetime')

    if 'not_before' in params:
        not_before = params['not_before']
        if not isinstance(not_before, datetime):
            raise ValueError('not_before must be an instance of datetime')

def process_params(params: SignOpts) -> SignBody:
    """
    Process and prepare parameters for signing.
    
    Args:
        params: Parameters to process
    
    Returns:
        Processed parameters as SignBody
    """
    body: SignBody = {
        'web3_token_version': '2',
        'issued_at': datetime.now(),
        'expiration_time': (
            params.get('expiration_time') or
            (timespan(params.get('expires_in', '1d')) if 'expires_in' in params else timespan('1d'))
        )
    }

    if 'not_before' in params:
        body['not_before'] = params['not_before']

    if 'chain_id' in params:
        body['chain_id'] = int(params['chain_id'])

    if 'uri' in params:
        body['uri'] = params['uri']

    if params.get('nonce'):
        body['nonce'] = int(random.random() * 99999999)

    if 'request_id' in params:
        body['request_id'] = params['request_id']

    if 'domain' in params:
        body['domain'] = params['domain']

    if 'statement' in params:
        body['statement'] = params['statement']

    return body

def build_message(params: SignBody) -> str:
    """
    Build the message to be signed.
    
    Args:
        params: Parameters to include in the message
    
    Returns:
        Formatted message string
    """
    message: list[str] = []

    if params.get('domain'):
        message.append(
            f"{params['domain']} wants you to sign in with your Ethereum account."
        )
        message.append('')

    if params.get('statement'):
        message.append(params['statement'])
        message.append('')

    param_labels = {
        'URI': params.get('uri'),
        'Web3 Token Version': params.get('web3_token_version'),
        'Chain ID': params.get('chain_id'),
        'Nonce': params.get('nonce'),
        'Issued At': params['issued_at'].isoformat(),
        'Expiration Time': params['expiration_time'].isoformat(),
        'Not Before': params.get('not_before').isoformat() if params.get('not_before') else None,
        'Request ID': params.get('request_id')
    }

    for label, value in param_labels.items():
        if value is not None:
            message.append(f'{label}: {value}')

    return '\n'.join(message)

async def sign(
    signer: Signer,
    opts: Union[str, SignOpts] = '1d'
) -> str:
    """
    Sign a token.
    
    Args:
        signer: A function that returns a signature string
        opts: Options to sign the token or a string representing expiration time
    
    Returns:
        A signed token
    
    Raises:
        ValueError: If the signer or parameters are invalid
    
    Example:
        ```python
        from web3_signer import sign

        token = await sign(signer, {
            'domain': 'example.com',
            'expires_in': '1d',
        })
        ```
    """
    params = {'expires_in': opts} if isinstance(opts, str) else opts

    validate_params(params)
    body = process_params(params)
    msg = build_message(body)
    signature = await signer(msg)

    if not isinstance(signature, str):
        raise ValueError(
            '"signer" argument should be a function that returns a signature string'
        )

    token = base64.b64encode(
        json.dumps({'signature': signature, 'body': msg}).encode()
    ).decode()

    return token 