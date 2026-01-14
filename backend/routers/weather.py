from fastapi import APIRouter, HTTPException, Query, Request

from models.weather import CurrentWeather, ForecastResponse

router = APIRouter(prefix="/api/weather", tags=["weather"])


@router.get("/current", response_model=CurrentWeather)
async def get_current_weather(
    request: Request,
    lat: float = Query(..., ge=-90, le=90, description="Latitude"),
    lon: float = Query(..., ge=-180, le=180, description="Longitude"),
    units: str = Query("metric", description="Units: metric, imperial, standard"),
) -> CurrentWeather:
    """
    Get current weather for a location.

    Returns temperature, humidity, wind, and weather conditions.
    """
    weather_provider = request.app.state.weather_provider

    try:
        return await weather_provider.get_current(lat, lon, units=units)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Weather service error: {str(e)}")


@router.get("/forecast", response_model=ForecastResponse)
async def get_forecast(
    request: Request,
    lat: float = Query(..., ge=-90, le=90, description="Latitude"),
    lon: float = Query(..., ge=-180, le=180, description="Longitude"),
    days: int = Query(5, ge=1, le=5, description="Number of days"),
    units: str = Query("metric", description="Units: metric, imperial, standard"),
) -> ForecastResponse:
    """
    Get weather forecast for a location.

    Returns daily forecasts for the specified number of days.
    """
    weather_provider = request.app.state.weather_provider

    try:
        return await weather_provider.get_forecast(lat, lon, days=days, units=units)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Weather service error: {str(e)}")
