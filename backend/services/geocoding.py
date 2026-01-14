import httpx
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from models.geocoding import GeoLocation


class GeocodingService:
    """Service for geocoding location queries using OpenWeatherMap Geocoding API."""

    BASE_URL = "https://api.openweathermap.org/geo/1.0"
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
    async def search(self, query: str, limit: int = 5) -> list[GeoLocation]:
        """
        Search for locations by name.

        Args:
            query: Location name to search for
            limit: Maximum number of results (1-5)

        Returns:
            List of matching GeoLocation objects
        """
        if not query or not query.strip():
            return []

        client = await self._get_client()
        response = await client.get(
            f"{self.BASE_URL}/direct",
            params={
                "q": query.strip(),
                "limit": min(max(limit, 1), 5),
                "appid": self.api_key,
            },
        )
        response.raise_for_status()
        data = response.json()

        return [GeoLocation.from_openweathermap(item) for item in data]
