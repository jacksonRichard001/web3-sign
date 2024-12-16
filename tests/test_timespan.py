import pytest
from datetime import datetime, timedelta
from web3_signer.timespan import ms, timespan

class TestTimespan:
    def test_ms_conversion_days(self):
        """Test conversion of days to milliseconds"""
        assert ms("1d") == 86400000  # 24 * 60 * 60 * 1000
        assert ms("2d") == 172800000  # 2 * 24 * 60 * 60 * 1000

    def test_ms_conversion_hours(self):
        """Test conversion of hours to milliseconds"""
        assert ms("1h") == 3600000  # 60 * 60 * 1000
        assert ms("24h") == 86400000  # 24 * 60 * 60 * 1000

    def test_ms_conversion_minutes(self):
        """Test conversion of minutes to milliseconds"""
        assert ms("1m") == 60000  # 60 * 1000
        assert ms("60m") == 3600000  # 60 * 60 * 1000

    def test_ms_conversion_seconds(self):
        """Test conversion of seconds to milliseconds"""
        assert ms("1s") == 1000
        assert ms("60s") == 60000  # 60 * 1000

    def test_ms_conversion_milliseconds(self):
        """Test conversion of explicit milliseconds"""
        assert ms("1ms") == 1
        assert ms("1000ms") == 1000

    def test_ms_invalid_format(self):
        """Test handling of invalid formats"""
        assert ms("invalid") is None
        assert ms("1y") is None  # invalid unit
        assert ms("d") is None  # missing number
        assert ms("1.5d") is None  # no decimal numbers
        assert ms("-1d") is None  # no negative numbers

    def test_timespan_with_string(self):
        """Test timespan conversion with string input"""
        now = datetime.now()
        result = timespan("1d")
        expected = now + timedelta(days=1)
        
        # Allow 1 second tolerance for test execution time
        assert abs((result - expected).total_seconds()) < 1

    def test_timespan_with_milliseconds(self):
        """Test timespan conversion with millisecond input"""
        now = datetime.now()
        result = timespan(3600000)  # 1 hour in milliseconds
        expected = now + timedelta(hours=1)
        
        assert abs((result - expected).total_seconds()) < 1

    def test_timespan_invalid_string(self):
        """Test timespan with invalid string input"""
        with pytest.raises(ValueError) as exc_info:
            timespan("invalid")
        assert '"expires_in" argument should be' in str(exc_info.value)

    def test_timespan_invalid_type(self):
        """Test timespan with invalid type input"""
        with pytest.raises(ValueError) as exc_info:
            timespan({"invalid": "type"})
        assert '"expires_in" argument should be' in str(exc_info.value)

    def test_timespan_zero_milliseconds(self):
        """Test timespan with zero milliseconds"""
        now = datetime.now()
        result = timespan(0)
        
        assert abs((result - now).total_seconds()) < 1

    def test_timespan_large_values(self):
        """Test timespan with large values"""
        now = datetime.now()
        result = timespan("365d")  # one year
        expected = now + timedelta(days=365)
        
        assert abs((result - expected).total_seconds()) < 1 