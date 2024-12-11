import base64
import json
import re
from eth_account.messages import encode_defunct
from web3 import Web3
from typing import TypedDict

class DecrypterResult(TypedDict):
    version: int
    address: str
    body: str
    signature: str

def get_version(body: str) -> int:
    """
    Retrieves the version number from the body of a token.

    Args:
        body: The body of the token.

    Returns:
        The version number.

    Raises:
        ValueError: If the token is malformed or the version number is missing.
    """
    match = re.search(r'Web3[\s-]+Token[\s-]+Version: \d', body)
    if not match:
        raise ValueError('Token malformed (missing version)')
    
    return int(match.group().replace(' ', '').split(':')[1])

async def decrypt(token: str) -> DecrypterResult:
    """
    Decrypts a token and returns the result.

    Args:
        token: The token to decrypt.

    Returns:
        A dictionary containing the version, address, body, and signature.

    Raises:
        ValueError: If the token is empty, not base64 encoded, unparsable JSON,
                   or malformed in some other way.
    """
    if not token:
        raise ValueError('Token required.')

    try:
        base64_decoded = base64.b64decode(token).decode('utf-8')
    except Exception:
        raise ValueError('Token malformed (must be base64 encoded)')

    if not base64_decoded:
        raise ValueError('Token malformed (must be base64 encoded)')

    try:
        decoded_dict = json.loads(base64_decoded)
        body = decoded_dict['body']
        signature = decoded_dict['signature']
    except (json.JSONDecodeError, KeyError):
        raise ValueError('Token malformed (unparsable JSON)')

    if not body:
        raise ValueError('Token malformed (empty message)')

    if not signature:
        raise ValueError('Token malformed (empty signature)')

    # Initialize Web3
    w3 = Web3()
    
    # Remove '0x' prefix if present and convert to bytes
    signature_bytes = bytes.fromhex(signature[2:] if signature.startswith('0x') else signature)
    
    # Create the message hash
    message = encode_defunct(text=body)
    
    # Recover the address
    address = w3.eth.account.recover_message(message, signature=signature_bytes)

    version = get_version(body)

    return {
        'version': version,
        'address': address.lower(),
        'body': body,
        'signature': signature
    } 