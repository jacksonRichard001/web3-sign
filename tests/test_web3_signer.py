import pytest
from datetime import datetime, timedelta

from web3_signer import sign, verify

@pytest.mark.asyncio
class TestWeb3Signer:
    @pytest.fixture(autouse=True)
    def setup(self, real_address):
        """Setup default options for tests"""
        self.real_address = real_address
        self.default_options = {
            'domain': 'iq.wiki',
            'statement': 'Test',
            'expiration_time': datetime.now() + timedelta(hours=1),
            'not_before': datetime.now() - timedelta(seconds=1)
        }

    async def test_sign_and_verify(self, signer):
        """Test basic token signing and verification"""
        token = await sign(signer, self.default_options)
        result = await verify(token)
        
        assert result['address'] == self.real_address
        assert result['body']['statement'] == self.default_options['statement']
        assert result['body']['domain'] == self.default_options['domain']

    async def test_token_expiration(self, signer):
        """Test token expiration handling"""
        options = {
            **self.default_options,
            'expiration_time': datetime.now() - timedelta(seconds=1)
        }
        token = await sign(signer, options)

        with pytest.raises(ValueError, match='Token expired'):
            await verify(token)

    async def test_token_not_before(self, signer):
        """Test not_before date handling"""
        options = {
            **self.default_options,
            'not_before': datetime.now() + timedelta(hours=1)
        }
        token = await sign(signer, options)

        with pytest.raises(ValueError, match="It's not yet time to use the token"):
            await verify(token)

    async def test_domain_validation(self, signer):
        """Test domain validation"""
        token = await sign(signer, self.default_options)

        with pytest.raises(ValueError, match='Inappropriate token domain'):
            await verify(token, {'domain': 'some-other.domain'})

    async def test_malformed_token(self):
        """Test malformed token handling"""
        with pytest.raises(ValueError, match='Token malformed'):
            await verify('MALFORMED_TOKEN')

    async def test_invalid_parameters(self, signer):
        """Test invalid parameter handling"""
        with pytest.raises(ValueError):
            await sign(signer, {'domain': 'iq.wiki', 'expires_in': 'invalid'})
        
        with pytest.raises(ValueError):
            await sign(signer, {'domain': 'iq.wiki', 'chain_id': 'not-a-number'})
        
        with pytest.raises(ValueError):
            await sign(signer, {'domain': 'iq.wiki', 'uri': 'invalid-url'}) 