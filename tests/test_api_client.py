"""Tests for ARES API client."""

import pytest
import json
from unittest.mock import AsyncMock, patch

from ares_mcp_server.api_client import AresAPIClient, RateLimiter


@pytest.mark.asyncio
async def test_rate_limiter():
    """Test rate limiter functionality."""
    limiter = RateLimiter(max_requests=2, time_window=1)
    
    # First two requests should go through immediately
    await limiter.acquire()
    await limiter.acquire()
    
    # Third request should be delayed
    import time
    start = time.time()
    await limiter.acquire()
    elapsed = time.time() - start
    
    # Should have waited approximately 1 second
    assert elapsed >= 0.9


@pytest.mark.asyncio
async def test_search_subject():
    """Test subject search functionality."""
    client = AresAPIClient()
    
    with patch.object(client, '_make_request', new_callable=AsyncMock) as mock_request:
        mock_request.return_value = {
            "ekonomickeSubjekty": [
                {
                    "ico": "12345678",
                    "obchodniJmeno": "Test Company s.r.o.",
                    "sidlo": {
                        "nazevUlice": "Test Street",
                        "cisloDomovni": "123",
                        "nazevObce": "Prague",
                        "psc": "11000"
                    },
                    "pravniForma": "Společnost s ručením omezeným",
                    "stavSubjektu": "AKTIVNI"
                }
            ]
        }
        
        result = await client.search_subject(name="Test Company")
        result_data = json.loads(result)
        
        assert result_data["found"] == 1
        assert result_data["subjects"][0]["ico"] == "12345678"
        assert result_data["subjects"][0]["name"] == "Test Company s.r.o."
        
        mock_request.assert_called_once_with(
            "GET",
            "/ekonomicke-subjekty-vyhledat",
            params={"obchodniJmeno": "Test Company"}
        )


@pytest.mark.asyncio
async def test_validate_ico():
    """Test IČO validation."""
    client = AresAPIClient()
    
    # Test invalid format
    result = await client.validate_ico("123")
    result_data = json.loads(result)
    assert result_data["valid"] == False
    assert "8 digits" in result_data["reason"]
    
    # Test valid format but doesn't exist
    with patch.object(client, '_make_request', new_callable=AsyncMock) as mock_request:
        mock_request.side_effect = Exception("Not found")
        
        result = await client.validate_ico("00000019")  # Valid checksum
        result_data = json.loads(result)
        
        assert result_data["valid_format"] == True
        assert result_data["exists_in_ares"] == False
        assert result_data["valid"] == False


@pytest.mark.asyncio
async def test_get_subject_error_handling():
    """Test error handling in get_subject."""
    client = AresAPIClient()
    
    with patch.object(client, '_make_request', new_callable=AsyncMock) as mock_request:
        mock_request.side_effect = Exception("API Error")
        
        result = await client.get_subject("12345678")
        result_data = json.loads(result)
        
        assert "error" in result_data
        assert "API Error" in result_data["error"]


if __name__ == "__main__":
    pytest.main([__file__])