from datetime import datetime
from pydantic import BaseModel


class WeatherCondition(BaseModel):
    """Weather condition details."""

    id: int
    main: str
    description: str
    icon: str


class CurrentWeather(BaseModel):
    """Normalized current weather data."""

    location_name: str
    lat: float
    lon: float
    timestamp: datetime
    temp: float
    feels_like: float
    temp_min: float
    temp_max: float
    humidity: int
    pressure: int
    wind_speed: float
    wind_deg: int
    clouds: int
    visibility: int | None = None
    condition: WeatherCondition
    sunrise: datetime | None = None
    sunset: datetime | None = None

    @classmethod
    def from_openweathermap(cls, data: dict) -> "CurrentWeather":
        """Create from OpenWeatherMap current weather API response."""
        weather = data["weather"][0]
        main = data["main"]
        wind = data.get("wind", {})
        sys = data.get("sys", {})

        return cls(
            location_name=data.get("name", "Unknown"),
            lat=data["coord"]["lat"],
            lon=data["coord"]["lon"],
            timestamp=datetime.fromtimestamp(data["dt"]),
            temp=main["temp"],
            feels_like=main["feels_like"],
            temp_min=main["temp_min"],
            temp_max=main["temp_max"],
            humidity=main["humidity"],
            pressure=main["pressure"],
            wind_speed=wind.get("speed", 0),
            wind_deg=wind.get("deg", 0),
            clouds=data.get("clouds", {}).get("all", 0),
            visibility=data.get("visibility"),
            condition=WeatherCondition(
                id=weather["id"],
                main=weather["main"],
                description=weather["description"],
                icon=weather["icon"],
            ),
            sunrise=datetime.fromtimestamp(sys["sunrise"]) if "sunrise" in sys else None,
            sunset=datetime.fromtimestamp(sys["sunset"]) if "sunset" in sys else None,
        )


class DailyForecast(BaseModel):
    """Single day forecast data."""

    date: datetime
    temp_day: float
    temp_min: float
    temp_max: float
    temp_night: float
    feels_like_day: float
    humidity: int
    wind_speed: float
    wind_deg: int
    clouds: int
    pop: float  # Probability of precipitation
    rain: float | None = None
    snow: float | None = None
    condition: WeatherCondition

    @classmethod
    def from_openweathermap_daily(cls, data: dict) -> "DailyForecast":
        """Create from OpenWeatherMap One Call API daily forecast."""
        weather = data["weather"][0]
        temp = data["temp"]

        return cls(
            date=datetime.fromtimestamp(data["dt"]),
            temp_day=temp["day"],
            temp_min=temp["min"],
            temp_max=temp["max"],
            temp_night=temp["night"],
            feels_like_day=data["feels_like"]["day"],
            humidity=data["humidity"],
            wind_speed=data["wind_speed"],
            wind_deg=data.get("wind_deg", 0),
            clouds=data.get("clouds", 0),
            pop=data.get("pop", 0),
            rain=data.get("rain"),
            snow=data.get("snow"),
            condition=WeatherCondition(
                id=weather["id"],
                main=weather["main"],
                description=weather["description"],
                icon=weather["icon"],
            ),
        )

    @classmethod
    def from_openweathermap_3h(cls, items: list[dict], date: datetime) -> "DailyForecast":
        """Aggregate 3-hour forecast items into a daily forecast."""
        temps = [item["main"]["temp"] for item in items]
        feels_likes = [item["main"]["feels_like"] for item in items]
        humidities = [item["main"]["humidity"] for item in items]
        wind_speeds = [item["wind"]["speed"] for item in items]
        wind_degs = [item["wind"].get("deg", 0) for item in items]
        clouds_list = [item["clouds"]["all"] for item in items]
        pops = [item.get("pop", 0) for item in items]
        rains = [item.get("rain", {}).get("3h", 0) for item in items]
        snows = [item.get("snow", {}).get("3h", 0) for item in items]

        # Find midday item for condition (or first item)
        midday_item = items[len(items) // 2] if items else items[0]
        weather = midday_item["weather"][0]

        return cls(
            date=date,
            temp_day=sum(temps) / len(temps),
            temp_min=min(temps),
            temp_max=max(temps),
            temp_night=temps[-1] if temps else temps[0],
            feels_like_day=sum(feels_likes) / len(feels_likes),
            humidity=int(sum(humidities) / len(humidities)),
            wind_speed=sum(wind_speeds) / len(wind_speeds),
            wind_deg=int(sum(wind_degs) / len(wind_degs)),
            clouds=int(sum(clouds_list) / len(clouds_list)),
            pop=max(pops),
            rain=sum(rains) if any(rains) else None,
            snow=sum(snows) if any(snows) else None,
            condition=WeatherCondition(
                id=weather["id"],
                main=weather["main"],
                description=weather["description"],
                icon=weather["icon"],
            ),
        )


class ForecastResponse(BaseModel):
    """Response for forecast endpoint."""

    lat: float
    lon: float
    timezone: int | None = None
    daily: list[DailyForecast]
