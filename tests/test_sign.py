import pytest
from datetime import datetime
from eth_account import Account
from web3 import Web3

from web3_signer import sign

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
        signed_message = w3.eth.account.sign_message(
            signable_message=w3.eth.account.sign_message(
                encode_defunct(text=message)
            ),
            private_key=account.key
        )
        return signed_message.signature.hex()
    return signer

@pytest.mark.asyncio
class TestSign:
    async def test_generate_token(self):
        """Test basic token generation"""
        token = await sign(
            await create_signer(account),
            {
                'domain': 'iq.wiki'
            }
        )
        assert token is not None
        assert len(token) > 0

    async def test_generate_token_with_expires_in(self):
        """Test token generation with expires_in parameter"""
        token = await sign(
            await create_signer(account),
            {
                'expires_in': '1d'
            }
        )
        assert token is not None
        assert len(token) > 0

    async def test_invalid_expires_in(self):
        """Test error handling for invalid expires_in"""
        with pytest.raises(ValueError):
            await sign(
                await create_signer(account),
                {
                    'domain': 'iq.wiki',
                    'expires_in': 'asd'
                }
            )

    async def test_invalid_chain_id(self):
        """Test error handling for invalid chain_id"""
        with pytest.raises(ValueError):
            await sign(
                await create_signer(account),
                {
                    'domain': 'iq.wiki',
                    'chain_id': 'ssssa23dsa'
                }
            )

    async def test_invalid_uri(self):
        """Test error handling for invalid URI"""
        with pytest.raises(ValueError):
            await sign(
                await create_signer(account),
                {
                    'domain': 'iq.wiki',
                    'uri': 'local.com'
                }
            )

    async def test_expiration_time_overwrites_expires_in(self):
        """Test expiration_time overwriting expires_in parameter"""
        token = await sign(
            await create_signer(account),
            {
                'domain': 'iq.wiki',
                'expiration_time': datetime.now(),
                'expires_in': '1d'
            }
        )
        assert token is not None
        assert len(token) > 0

    async def test_generate_token_with_statement_and_domain(self):
        """Test token generation with statement and domain"""
        token = await sign(
            await create_signer(account),
            {
                'domain': 'iq.wiki',
                'statement': 'Test',
                'expiration_time': datetime.now(),
                'expires_in': '1d',
                'not_before': datetime.now()
            }
        )
        assert token is not None
        assert len(token) > 0

    async def test_generate_token_with_statement_without_domain(self):
        """Test token generation with statement but without domain"""
        token = await sign(
            await create_signer(account),
            {
                'expiration_time': datetime.now(),
                'expires_in': '1d',
                'statement': 'Test',
                'not_before': datetime.now()
            }
        )
        assert token is not None
        assert len(token) > 0

    async def test_invalid_signer(self):
        """Test error handling for invalid signer"""
        with pytest.raises(TypeError):
            await sign("not_a_function") 