from collections import defaultdict
from datetime import datetime, timezone, timedelta

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from models.weather import CurrentWeather, DailyForecast, ForecastResponse


class WeatherProvider:
    """Service for fetching weather data from OpenWeatherMap API."""

    BASE_URL = "https://api.openweathermap.org/data/2.5"
    TIMEOUT = 10.0

    def __init__(self, api_key: str):
        self.api_key = api_key
        self._client: httpx.AsyncClient | None = None

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(timeout=self.TIMEOUT)
        return self._client

    async def close(self) -> None:
        if self._client and not self._client.is_closed:
            await self._client.aclose()

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=4),
        retry=retry_if_exception_type((httpx.TimeoutException, httpx.NetworkError)),
        reraise=True,
    )
    async def get_current(self, lat: float, lon: float, units: str = "metric") -> CurrentWeather:
        """
        Get current weather for a location.

        Args:
            lat: Latitude
            lon: Longitude
            units: Temperature units (metric, imperial, standard)

        Returns:
            CurrentWeather object with normalized data
        """
        client = await self._get_client()
        response = await client.get(
            f"{self.BASE_URL}/weather",
            params={
                "lat": lat,
                "lon": lon,
                "units": units,
                "appid": self.api_key,
            },
        )
        response.raise_for_status()
        data = response.json()

        return CurrentWeather.from_openweathermap(data)

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=4),
        retry=retry_if_exception_type((httpx.TimeoutException, httpx.NetworkError)),
        reraise=True,
    )
    async def get_forecast(
        self, lat: float, lon: float, days: int = 5, units: str = "metric"
    ) -> ForecastResponse:
        """
        Get weather forecast for a location.

        Uses the free 5-day/3-hour forecast API and aggregates into daily forecasts.

        Args:
            lat: Latitude
            lon: Longitude
            days: Number of days (1-5)
            units: Temperature units (metric, imperial, standard)

        Returns:
            ForecastResponse with daily forecasts
        """
        client = await self._get_client()
        response = await client.get(
            f"{self.BASE_URL}/forecast",
            params={
                "lat": lat,
                "lon": lon,
                "units": units,
                "appid": self.api_key,
            },
        )
        response.raise_for_status()
        data = response.json()

        # Get timezone offset from API (seconds from UTC)
        tz_offset_seconds = data["city"].get("timezone", 0)
        location_tz = timezone(timedelta(seconds=tz_offset_seconds))

        # Group 3-hour forecasts by date in the location's timezone
        daily_items: dict[str, list[dict]] = defaultdict(list)
        for item in data["list"]:
            # Convert UTC timestamp to location's local time for grouping
            dt_utc = datetime.fromtimestamp(item["dt"], tz=timezone.utc)
            dt_local = dt_utc.astimezone(location_tz)
            date_key = dt_local.strftime("%Y-%m-%d")
            daily_items[date_key].append(item)

        # Convert to daily forecasts
        daily_forecasts: list[DailyForecast] = []
        sorted_dates = sorted(daily_items.keys())[:days]

        for date_key in sorted_dates:
            items = daily_items[date_key]
            date = datetime.strptime(date_key, "%Y-%m-%d").replace(tzinfo=location_tz)
            daily_forecasts.append(DailyForecast.from_openweathermap_3h(items, date))

        return ForecastResponse(
            lat=data["city"]["coord"]["lat"],
            lon=data["city"]["coord"]["lon"],
            timezone=data["city"].get("timezone"),
            daily=daily_forecasts,
        )
