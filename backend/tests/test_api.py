"""Integration tests for API endpoints using FastAPI TestClient."""

import pytest
from datetime import datetime

from models.geocoding import GeoLocation
from models.weather import CurrentWeather, ForecastResponse, DailyForecast, WeatherCondition


class TestHealthEndpoint:
    """Tests for the /health endpoint."""

    def test_health_returns_healthy(self, test_client):
        """Test health endpoint returns healthy status."""
        response = test_client.get("/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "chasingmana-api"


class TestGeocodeEndpoint:
    """Tests for the /api/geocode endpoint."""

    def test_geocode_returns_results(self, test_client, mock_geocoding_service):
        """Test geocode endpoint returns location results."""
        mock_geocoding_service.search.return_value = [
            GeoLocation(
                name="Paris",
                lat=48.8566,
                lon=2.3522,
                country="FR",
                state="Ile-de-France",
                display_name="Paris, Ile-de-France, FR",
            )
        ]

        response = test_client.get("/api/geocode", params={"q": "Paris"})

        assert response.status_code == 200
        data = response.json()
        assert len(data["results"]) == 1
        assert data["results"][0]["name"] == "Paris"
        assert data["results"][0]["lat"] == 48.8566

    def test_geocode_empty_results(self, test_client, mock_geocoding_service):
        """Test geocode endpoint handles empty results."""
        mock_geocoding_service.search.return_value = []

        response = test_client.get("/api/geocode", params={"q": "nonexistent"})

        assert response.status_code == 200
        data = response.json()
        assert data["results"] == []

    def test_geocode_missing_query(self, test_client):
        """Test geocode endpoint requires query parameter."""
        response = test_client.get("/api/geocode")

        assert response.status_code == 422  # Validation error

    def test_geocode_service_error(self, test_client, mock_geocoding_service):
        """Test geocode endpoint handles service errors."""
        mock_geocoding_service.search.side_effect = Exception("API error")

        response = test_client.get("/api/geocode", params={"q": "Paris"})

        assert response.status_code == 502
        assert "Geocoding service error" in response.json()["detail"]

    def test_geocode_respects_limit(self, test_client, mock_geocoding_service):
        """Test geocode endpoint passes limit parameter."""
        mock_geocoding_service.search.return_value = []

        test_client.get("/api/geocode", params={"q": "Paris", "limit": 3})

        mock_geocoding_service.search.assert_called_once_with("Paris", limit=3)


class TestCurrentWeatherEndpoint:
    """Tests for the /api/weather/current endpoint."""

    @pytest.fixture
    def sample_current_weather(self):
        """Sample CurrentWeather object."""
        return CurrentWeather(
            location_name="Paris",
            lat=48.8566,
            lon=2.3522,
            timestamp=datetime(2024, 1, 1, 12, 0, 0),
            temp=20.5,
            feels_like=19.8,
            temp_min=18.0,
            temp_max=22.0,
            humidity=65,
            pressure=1015,
            wind_speed=3.5,
            wind_deg=180,
            clouds=0,
            visibility=10000,
            condition=WeatherCondition(
                id=800,
                main="Clear",
                description="clear sky",
                icon="01d",
            ),
        )

    def test_current_weather_returns_data(
        self, test_client, mock_weather_provider, sample_current_weather
    ):
        """Test current weather endpoint returns weather data."""
        mock_weather_provider.get_current.return_value = sample_current_weather

        response = test_client.get(
            "/api/weather/current",
            params={"lat": 48.8566, "lon": 2.3522},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["location_name"] == "Paris"
        assert data["temp"] == 20.5
        assert data["condition"]["main"] == "Clear"

    def test_current_weather_missing_params(self, test_client):
        """Test current weather endpoint requires lat/lon."""
        response = test_client.get("/api/weather/current")
        assert response.status_code == 422

        response = test_client.get("/api/weather/current", params={"lat": 48.8566})
        assert response.status_code == 422

    def test_current_weather_invalid_coords(self, test_client):
        """Test current weather endpoint validates coordinate ranges."""
        response = test_client.get(
            "/api/weather/current",
            params={"lat": 100, "lon": 2.3522},  # Invalid latitude
        )
        assert response.status_code == 422

        response = test_client.get(
            "/api/weather/current",
            params={"lat": 48.8566, "lon": 200},  # Invalid longitude
        )
        assert response.status_code == 422

    def test_current_weather_service_error(self, test_client, mock_weather_provider):
        """Test current weather endpoint handles service errors."""
        mock_weather_provider.get_current.side_effect = Exception("API error")

        response = test_client.get(
            "/api/weather/current",
            params={"lat": 48.8566, "lon": 2.3522},
        )

        assert response.status_code == 502
        assert "Weather service error" in response.json()["detail"]


class TestForecastEndpoint:
    """Tests for the /api/weather/forecast endpoint."""

    @pytest.fixture
    def sample_forecast(self):
        """Sample ForecastResponse object."""
        return ForecastResponse(
            lat=48.8566,
            lon=2.3522,
            timezone=3600,
            daily=[
                DailyForecast(
                    date=datetime(2024, 1, 1),
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
                    condition=WeatherCondition(
                        id=800,
                        main="Clear",
                        description="clear sky",
                        icon="01d",
                    ),
                )
            ],
        )

    def test_forecast_returns_data(
        self, test_client, mock_weather_provider, sample_forecast
    ):
        """Test forecast endpoint returns forecast data."""
        mock_weather_provider.get_forecast.return_value = sample_forecast

        response = test_client.get(
            "/api/weather/forecast",
            params={"lat": 48.8566, "lon": 2.3522},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["lat"] == 48.8566
        assert data["timezone"] == 3600
        assert len(data["daily"]) == 1

    def test_forecast_respects_days_param(self, test_client, mock_weather_provider, sample_forecast):
        """Test forecast endpoint passes days parameter."""
        mock_weather_provider.get_forecast.return_value = sample_forecast

        test_client.get(
            "/api/weather/forecast",
            params={"lat": 48.8566, "lon": 2.3522, "days": 3},
        )

        mock_weather_provider.get_forecast.assert_called_once()
        call_kwargs = mock_weather_provider.get_forecast.call_args.kwargs
        assert call_kwargs.get("days") == 3

    def test_forecast_service_error(self, test_client, mock_weather_provider):
        """Test forecast endpoint handles service errors."""
        mock_weather_provider.get_forecast.side_effect = Exception("API error")

        response = test_client.get(
            "/api/weather/forecast",
            params={"lat": 48.8566, "lon": 2.3522},
        )

        assert response.status_code == 502
        assert "Weather service error" in response.json()["detail"]
