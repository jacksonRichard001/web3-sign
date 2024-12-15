import pytest
from datetime import datetime, timedelta
from eth_account import Account
from eth_account.messages import encode_defunct
from web3 import Web3

from web3_signer import sign, verify

# Create a test account
Account.enable_unaudited_hdwallet_features()
MNEMONIC = Account.create().mnemonic
account = Account.from_mnemonic(MNEMONIC)

# Initialize Web3
w3 = Web3()

# Create a signer function that mimics viem's client.signMessage
async def create_signer(account):
    async def signer(message: str) -> str:
        # Sign the message using eth_account
        message_hash = encode_defunct(text=message)
        signed_message = w3.eth.account.sign_message(
            message_hash,
            private_key=account.key
        )
        return signed_message.signature.hex()
    return signer

@pytest.mark.asyncio
class TestVerify:
    def setup_method(self):
        """Setup default options for tests"""
        self.real_address = account.address.lower()
        self.default_options = {
            'domain': 'iq.wiki',
            'statement': 'Test',
            'expiration_time': datetime.now() + timedelta(hours=1),
            'not_before': datetime.now() - timedelta(seconds=1)
        }

    async def test_verify_signature(self):
        """Test basic signature verification"""
        token = await sign(
            await create_signer(account),
            self.default_options
        )

        result = await verify(token)
        address, body = result['address'], result['body']

        assert address == self.real_address
        assert body['statement'] == self.default_options['statement']
        assert body['domain'] == self.default_options['domain']

    async def test_expired_token(self):
        """Test error handling for expired token"""
        options = {
            **self.default_options,
            'expiration_time': datetime.now() - timedelta(seconds=1)
        }
        
        token = await sign(
            await create_signer(account),
            options
        )

        with pytest.raises(ValueError) as exc_info:
            await verify(token)
        assert str(exc_info.value) == 'Token expired'

    async def test_future_not_before_date(self):
        """Test error handling for future not_before date"""
        options = {
            **self.default_options,
            'not_before': datetime.now() + timedelta(hours=1)
        }
        
        token = await sign(
            await create_signer(account),
            options
        )

        with pytest.raises(ValueError) as exc_info:
            await verify(token)
        assert str(exc_info.value) == "It's not yet time to use the token"

    async def test_different_domains(self):
        """Test error handling for domain mismatch"""
        token = await sign(
            await create_signer(account),
            self.default_options
        )

        with pytest.raises(ValueError) as exc_info:
            await verify(token, {'domain': 'some-other.domain'})
        assert str(exc_info.value) == 'Inappropriate token domain'

    async def test_malformed_token(self):
        """Test error handling for malformed token"""
        with pytest.raises(ValueError) as exc_info:
            await verify('MALFORMED_TOKEN')
        assert str(exc_info.value) == 'Token malformed (must be base64 encoded)' 