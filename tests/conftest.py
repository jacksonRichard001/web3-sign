import pytest
from eth_account import Account
from eth_account.messages import encode_defunct
from web3 import Web3

# Create a test account
Account.enable_unaudited_hdwallet_features()
MNEMONIC = Account.create().mnemonic
account = Account.from_mnemonic(MNEMONIC)

# Initialize Web3
w3 = Web3()

@pytest.fixture
def test_account():
    return account

@pytest.fixture
def real_address():
    return account.address.lower()

@pytest.fixture
async def signer(test_account):
    async def sign_message(message: str) -> str:
        message_hash = encode_defunct(text=message)
        signed_message = w3.eth.account.sign_message(
            message_hash,
            private_key=test_account.key
        )
        return signed_message.signature.hex()
    return sign_message 