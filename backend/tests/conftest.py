"""Shared test fixtures and configuration."""

import pytest
from unittest.mock import AsyncMock, patch
from fastapi import FastAPI
from fastapi.testclient import TestClient
from fastapi.middleware.cors import CORSMiddleware

from services import GeocodingService, WeatherProvider
from routers import geocoding_router, weather_router


def create_test_app(mock_geocoding_service, mock_weather_provider):
    """Create a test app with mocked services (no lifespan)."""
    test_app = FastAPI()

    test_app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Set mocked services directly on state
    test_app.state.geocoding_service = mock_geocoding_service
    test_app.state.weather_provider = mock_weather_provider

    @test_app.get("/health")
    async def health_check():
        return {"status": "healthy", "service": "chasingmana-api"}

    test_app.include_router(geocoding_router)
    test_app.include_router(weather_router)

    return test_app


@pytest.fixture
def mock_geocoding_service():
    """Create a mock geocoding service."""
    service = AsyncMock(spec=GeocodingService)
    return service


@pytest.fixture
def mock_weather_provider():
    """Create a mock weather provider."""
    provider = AsyncMock(spec=WeatherProvider)
    return provider


@pytest.fixture
def test_client(mock_geocoding_service, mock_weather_provider):
    """Create a test client with mocked services."""
    test_app = create_test_app(mock_geocoding_service, mock_weather_provider)
    with TestClient(test_app, raise_server_exceptions=False) as client:
        yield client


@pytest.fixture
def sample_geocoding_response():
    """Sample OpenWeatherMap geocoding API response."""
    return [
        {
            "name": "Paris",
            "lat": 48.8566,
            "lon": 2.3522,
            "country": "FR",
            "state": "Ile-de-France",
        },
        {
            "name": "Paris",
            "lat": 33.6609,
            "lon": -95.5555,
            "country": "US",
            "state": "Texas",
        },
    ]


@pytest.fixture
def sample_current_weather_response():
    """Sample OpenWeatherMap current weather API response."""
    return {
        "coord": {"lon": 2.3522, "lat": 48.8566},
        "weather": [
            {
                "id": 800,
                "main": "Clear",
                "description": "clear sky",
                "icon": "01d",
            }
        ],
        "main": {
            "temp": 20.5,
            "feels_like": 19.8,
            "temp_min": 18.0,
            "temp_max": 22.0,
            "pressure": 1015,
            "humidity": 65,
        },
        "visibility": 10000,
        "wind": {"speed": 3.5, "deg": 180},
        "clouds": {"all": 0},
        "dt": 1704067200,
        "sys": {
            "country": "FR",
            "sunrise": 1704093600,
            "sunset": 1704126000,
        },
        "timezone": 3600,
        "name": "Paris",
    }


@pytest.fixture
def sample_forecast_response():
    """Sample OpenWeatherMap 5-day forecast API response."""
    return {
        "city": {
            "coord": {"lat": 48.8566, "lon": 2.3522},
            "timezone": 3600,
            "name": "Paris",
            "country": "FR",
        },
        "list": [
            {
                "dt": 1704067200,
                "main": {
                    "temp": 20.5,
                    "feels_like": 19.8,
                    "temp_min": 18.0,
                    "temp_max": 22.0,
                    "pressure": 1015,
                    "humidity": 65,
                },
                "weather": [
                    {
                        "id": 800,
                        "main": "Clear",
                        "description": "clear sky",
                        "icon": "01d",
                    }
                ],
                "clouds": {"all": 0},
                "wind": {"speed": 3.5, "deg": 180},
                "pop": 0.1,
            },
            {
                "dt": 1704078000,
                "main": {
                    "temp": 18.0,
                    "feels_like": 17.5,
                    "temp_min": 16.0,
                    "temp_max": 19.0,
                    "pressure": 1016,
                    "humidity": 70,
                },
                "weather": [
                    {
                        "id": 801,
                        "main": "Clouds",
                        "description": "few clouds",
                        "icon": "02n",
                    }
                ],
                "clouds": {"all": 20},
                "wind": {"speed": 2.5, "deg": 200},
                "pop": 0.2,
            },
        ],
    }
