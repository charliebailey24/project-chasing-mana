from pydantic import BaseModel


class GeoLocation(BaseModel):
    """Normalized geocoding result."""

    name: str
    lat: float
    lon: float
    country: str
    state: str | None = None
    display_name: str

    @classmethod
    def from_openweathermap(cls, data: dict) -> "GeoLocation":
        """Create from OpenWeatherMap geocoding API response."""
        parts = [data.get("name", "")]
        if state := data.get("state"):
            parts.append(state)
        if country := data.get("country"):
            parts.append(country)

        return cls(
            name=data.get("name", "Unknown"),
            lat=data["lat"],
            lon=data["lon"],
            country=data.get("country", ""),
            state=data.get("state"),
            display_name=", ".join(parts),
        )


class GeocodingResponse(BaseModel):
    """Response for geocoding endpoint."""

    results: list[GeoLocation]
