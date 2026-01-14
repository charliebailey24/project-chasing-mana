"""Schemathesis tests for OpenAPI schema validation."""

import pytest
import schemathesis
from unittest.mock import AsyncMock
from datetime import datetime, timezone
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from services import GeocodingService, WeatherProvider
from routers import geocoding_router, weather_router
from models.geocoding import GeoLocation
from models.weather import CurrentWeather, ForecastResponse, DailyForecast, WeatherCondition


# Enable experimental OpenAPI 3.1 support
schemathesis.experimental.OPEN_API_3_1.enable()


def create_schema_test_app():
    """Create a test app with mocked services for schema tests."""
    mock_geocoding = AsyncMock(spec=GeocodingService)
    mock_geocoding.search.return_value = [
        GeoLocation(
            name="Test City",
            lat=40.0,
            lon=-74.0,
            country="US",
            state="Test State",
            display_name="Test City, Test State, US",
        )
    ]

    mock_weather = AsyncMock(spec=WeatherProvider)
    mock_weather.get_current.return_value = CurrentWeather(
        location_name="Test City",
        lat=40.0,
        lon=-74.0,
        timestamp=datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc),
        temp=20.0,
        feels_like=19.0,
        temp_min=18.0,
        temp_max=22.0,
        humidity=60,
        pressure=1013,
        wind_speed=3.0,
        wind_deg=180,
        clouds=10,
        visibility=10000,
        condition=WeatherCondition(id=800, main="Clear", description="clear sky", icon="01d"),
        sunrise=datetime(2024, 1, 1, 7, 0, 0, tzinfo=timezone.utc),
        sunset=datetime(2024, 1, 1, 17, 0, 0, tzinfo=timezone.utc),
    )
    mock_weather.get_forecast.return_value = ForecastResponse(
        lat=40.0,
        lon=-74.0,
        timezone=3600,
        daily=[
            DailyForecast(
                date=datetime(2024, 1, 1, tzinfo=timezone.utc),
                temp_day=20.0,
                temp_min=15.0,
                temp_max=25.0,
                temp_night=16.0,
                feels_like_day=19.0,
                humidity=60,
                wind_speed=3.0,
                wind_deg=180,
                clouds=10,
                pop=0.2,
                condition=WeatherCondition(id=800, main="Clear", description="clear sky", icon="01d"),
            )
        ],
    )

    test_app = FastAPI()

    test_app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    test_app.state.geocoding_service = mock_geocoding
    test_app.state.weather_provider = mock_weather

    @test_app.get("/health")
    async def health_check():
        return {"status": "healthy", "service": "chasingmana-api"}

    test_app.include_router(geocoding_router)
    test_app.include_router(weather_router)

    return test_app


# Create the test app with mocks
schema_test_app = create_schema_test_app()

# Create schema from the test app
schema = schemathesis.from_asgi("/openapi.json", schema_test_app)


@schema.parametrize()
def test_api_schema(case):
    """
    Test that all API endpoints conform to their OpenAPI schema.

    Schemathesis generates test cases from the OpenAPI schema and verifies:
    - Response status codes match documented codes
    - Response bodies conform to documented schemas
    - Required parameters are properly validated
    """
    response = case.call_asgi()
    case.validate_response(response)


@schema.parametrize(endpoint="/health")
def test_health_schema(case):
    """Test health endpoint conforms to schema."""
    response = case.call_asgi()
    case.validate_response(response)


@schema.parametrize(endpoint="/api/geocode")
def test_geocode_schema(case):
    """Test geocode endpoint conforms to schema."""
    response = case.call_asgi()
    case.validate_response(response)


@schema.parametrize(endpoint="/api/weather/current")
def test_current_weather_schema(case):
    """Test current weather endpoint conforms to schema."""
    response = case.call_asgi()
    case.validate_response(response)


@schema.parametrize(endpoint="/api/weather/forecast")
def test_forecast_schema(case):
    """Test forecast endpoint conforms to schema."""
    response = case.call_asgi()
    case.validate_response(response)
