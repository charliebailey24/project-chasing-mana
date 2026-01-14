"""Unit tests for the weather provider service."""

import pytest
import httpx
import respx
from httpx import Response
from datetime import datetime

from services.weather_provider import WeatherProvider
from models.weather import CurrentWeather, DailyForecast, ForecastResponse, WeatherCondition


class TestCurrentWeatherModel:
    """Tests for CurrentWeather.from_openweathermap parsing."""

    def test_parse_complete_response(self, sample_current_weather_response):
        """Test parsing a complete current weather response."""
        result = CurrentWeather.from_openweathermap(sample_current_weather_response)

        assert result.location_name == "Paris"
        assert result.lat == 48.8566
        assert result.lon == 2.3522
        assert result.temp == 20.5
        assert result.feels_like == 19.8
        assert result.humidity == 65
        assert result.pressure == 1015
        assert result.wind_speed == 3.5
        assert result.wind_deg == 180
        assert result.clouds == 0
        assert result.visibility == 10000
        assert result.condition.main == "Clear"
        assert result.condition.description == "clear sky"

    def test_parse_missing_optional_fields(self):
        """Test parsing response with missing optional fields."""
        data = {
            "coord": {"lon": 0.0, "lat": 0.0},
            "weather": [{"id": 800, "main": "Clear", "description": "clear", "icon": "01d"}],
            "main": {
                "temp": 20.0,
                "feels_like": 20.0,
                "temp_min": 20.0,
                "temp_max": 20.0,
                "pressure": 1013,
                "humidity": 50,
            },
            "dt": 1704067200,
            "sys": {},
        }
        result = CurrentWeather.from_openweathermap(data)

        assert result.wind_speed == 0
        assert result.wind_deg == 0
        assert result.visibility is None
        assert result.sunrise is None
        assert result.sunset is None


class TestDailyForecastModel:
    """Tests for DailyForecast.from_openweathermap_3h parsing."""

    def test_aggregate_3h_forecasts(self, sample_forecast_response):
        """Test aggregating 3-hour forecasts into daily forecast."""
        items = sample_forecast_response["list"]
        date = datetime(2024, 1, 1)

        result = DailyForecast.from_openweathermap_3h(items, date)

        assert result.date == date
        # Average of 20.5 and 18.0
        assert result.temp_day == pytest.approx(19.25)
        assert result.temp_min == 18.0
        assert result.temp_max == 20.5
        # Average humidity of 65 and 70
        assert result.humidity == 67
        # Max pop of 0.1 and 0.2
        assert result.pop == 0.2

    def test_aggregate_single_item(self):
        """Test aggregating a single 3-hour forecast item."""
        items = [
            {
                "dt": 1704067200,
                "main": {
                    "temp": 15.0,
                    "feels_like": 14.0,
                    "humidity": 60,
                },
                "weather": [{"id": 800, "main": "Clear", "description": "clear", "icon": "01d"}],
                "clouds": {"all": 10},
                "wind": {"speed": 5.0, "deg": 90},
                "pop": 0.0,
            }
        ]
        date = datetime(2024, 1, 1)

        result = DailyForecast.from_openweathermap_3h(items, date)

        assert result.temp_day == 15.0
        assert result.temp_min == 15.0
        assert result.temp_max == 15.0


class TestForecastResponseModel:
    """Tests for ForecastResponse model."""

    def test_timezone_as_int(self):
        """Test that timezone accepts integer (seconds offset)."""
        response = ForecastResponse(
            lat=48.8566,
            lon=2.3522,
            timezone=3600,
            daily=[],
        )
        assert response.timezone == 3600

    def test_timezone_optional(self):
        """Test that timezone is optional."""
        response = ForecastResponse(
            lat=48.8566,
            lon=2.3522,
            daily=[],
        )
        assert response.timezone is None


class TestWeatherProvider:
    """Tests for WeatherProvider methods."""

    @pytest.fixture
    def provider(self):
        """Create a weather provider with test API key."""
        return WeatherProvider(api_key="test-api-key")

    @respx.mock
    @pytest.mark.asyncio
    async def test_get_current_weather(self, provider, sample_current_weather_response):
        """Test getting current weather."""
        respx.get("https://api.openweathermap.org/data/2.5/weather").mock(
            return_value=Response(200, json=sample_current_weather_response)
        )

        result = await provider.get_current(48.8566, 2.3522)

        assert result.location_name == "Paris"
        assert result.temp == 20.5

    @respx.mock
    @pytest.mark.asyncio
    async def test_get_current_passes_units(self, provider, sample_current_weather_response):
        """Test that units parameter is passed to API."""
        route = respx.get("https://api.openweathermap.org/data/2.5/weather").mock(
            return_value=Response(200, json=sample_current_weather_response)
        )

        await provider.get_current(48.8566, 2.3522, units="imperial")

        assert route.calls[0].request.url.params["units"] == "imperial"

    @respx.mock
    @pytest.mark.asyncio
    async def test_get_current_http_error(self, provider):
        """Test get_current raises on HTTP error."""
        respx.get("https://api.openweathermap.org/data/2.5/weather").mock(
            return_value=Response(401, json={"message": "Invalid API key"})
        )

        with pytest.raises(httpx.HTTPStatusError):
            await provider.get_current(48.8566, 2.3522)

    @respx.mock
    @pytest.mark.asyncio
    async def test_get_forecast(self, provider, sample_forecast_response):
        """Test getting weather forecast."""
        respx.get("https://api.openweathermap.org/data/2.5/forecast").mock(
            return_value=Response(200, json=sample_forecast_response)
        )

        result = await provider.get_forecast(48.8566, 2.3522, days=5)

        assert result.lat == 48.8566
        assert result.lon == 2.3522
        assert result.timezone == 3600
        assert len(result.daily) > 0

    @respx.mock
    @pytest.mark.asyncio
    async def test_get_forecast_limits_days(self, provider, sample_forecast_response):
        """Test forecast respects days parameter."""
        respx.get("https://api.openweathermap.org/data/2.5/forecast").mock(
            return_value=Response(200, json=sample_forecast_response)
        )

        result = await provider.get_forecast(48.8566, 2.3522, days=1)

        # Should only return 1 day of forecasts
        assert len(result.daily) <= 1

    @respx.mock
    @pytest.mark.asyncio
    async def test_get_forecast_http_error(self, provider):
        """Test get_forecast raises on HTTP error."""
        respx.get("https://api.openweathermap.org/data/2.5/forecast").mock(
            return_value=Response(500, json={"message": "Server error"})
        )

        with pytest.raises(httpx.HTTPStatusError):
            await provider.get_forecast(48.8566, 2.3522)

    @pytest.mark.asyncio
    async def test_close_client(self, provider):
        """Test closing the HTTP client."""
        client = await provider._get_client()
        assert not client.is_closed

        await provider.close()
        assert client.is_closed
