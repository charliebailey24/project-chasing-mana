"""Unit tests for the geocoding service."""

import pytest
import httpx
import respx
from httpx import Response

from services.geocoding import GeocodingService
from models.geocoding import GeoLocation


class TestGeoLocationModel:
    """Tests for GeoLocation.from_openweathermap parsing."""

    def test_parse_complete_response(self):
        """Test parsing a complete geocoding response with all fields."""
        data = {
            "name": "Paris",
            "lat": 48.8566,
            "lon": 2.3522,
            "country": "FR",
            "state": "Ile-de-France",
        }
        result = GeoLocation.from_openweathermap(data)

        assert result.name == "Paris"
        assert result.lat == 48.8566
        assert result.lon == 2.3522
        assert result.country == "FR"
        assert result.state == "Ile-de-France"
        assert result.display_name == "Paris, Ile-de-France, FR"

    def test_parse_minimal_response(self):
        """Test parsing response with only required fields."""
        data = {
            "name": "Unknown City",
            "lat": 0.0,
            "lon": 0.0,
            "country": "XX",
        }
        result = GeoLocation.from_openweathermap(data)

        assert result.name == "Unknown City"
        assert result.state is None
        assert result.display_name == "Unknown City, XX"

    def test_parse_missing_name(self):
        """Test parsing response with missing name defaults to Unknown."""
        data = {
            "lat": 48.8566,
            "lon": 2.3522,
            "country": "FR",
        }
        result = GeoLocation.from_openweathermap(data)

        assert result.name == "Unknown"

    def test_parse_us_location_with_state(self):
        """Test parsing US location includes state in display name."""
        data = {
            "name": "San Francisco",
            "lat": 37.7749,
            "lon": -122.4194,
            "country": "US",
            "state": "California",
        }
        result = GeoLocation.from_openweathermap(data)

        assert result.display_name == "San Francisco, California, US"


class TestGeocodingService:
    """Tests for GeocodingService methods."""

    @pytest.fixture
    def service(self):
        """Create a geocoding service with test API key."""
        return GeocodingService(api_key="test-api-key")

    @respx.mock
    @pytest.mark.asyncio
    async def test_search_returns_locations(self, service, sample_geocoding_response):
        """Test search returns parsed locations."""
        respx.get("https://api.openweathermap.org/geo/1.0/direct").mock(
            return_value=Response(200, json=sample_geocoding_response)
        )

        results = await service.search("Paris")

        assert len(results) == 2
        assert results[0].name == "Paris"
        assert results[0].country == "FR"
        assert results[1].country == "US"

    @respx.mock
    @pytest.mark.asyncio
    async def test_search_empty_query_returns_empty(self, service):
        """Test search with empty query returns empty list without API call."""
        results = await service.search("")
        assert results == []

        results = await service.search("   ")
        assert results == []

    @respx.mock
    @pytest.mark.asyncio
    async def test_search_respects_limit(self, service):
        """Test search passes limit parameter to API."""
        route = respx.get("https://api.openweathermap.org/geo/1.0/direct").mock(
            return_value=Response(200, json=[])
        )

        await service.search("Paris", limit=3)

        assert route.calls[0].request.url.params["limit"] == "3"

    @respx.mock
    @pytest.mark.asyncio
    async def test_search_clamps_limit(self, service):
        """Test search clamps limit to valid range (1-5)."""
        route = respx.get("https://api.openweathermap.org/geo/1.0/direct").mock(
            return_value=Response(200, json=[])
        )

        await service.search("Paris", limit=10)
        assert route.calls[0].request.url.params["limit"] == "5"

        await service.search("Paris", limit=0)
        assert route.calls[1].request.url.params["limit"] == "1"

    @respx.mock
    @pytest.mark.asyncio
    async def test_search_http_error(self, service):
        """Test search raises on HTTP error."""
        respx.get("https://api.openweathermap.org/geo/1.0/direct").mock(
            return_value=Response(401, json={"message": "Invalid API key"})
        )

        with pytest.raises(httpx.HTTPStatusError):
            await service.search("Paris")

    @pytest.mark.asyncio
    async def test_close_client(self, service):
        """Test closing the HTTP client."""
        # Create client by making internal call
        client = await service._get_client()
        assert not client.is_closed

        await service.close()
        assert client.is_closed

    @pytest.mark.asyncio
    async def test_close_without_client(self, service):
        """Test closing when no client exists doesn't raise."""
        await service.close()  # Should not raise
