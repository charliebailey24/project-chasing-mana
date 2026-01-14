from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import settings
from routers import geocoding_router, weather_router
from services import GeocodingService, WeatherProvider


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle - initialize and cleanup services."""
    # Startup: Initialize services
    app.state.geocoding_service = GeocodingService(settings.openweathermap_api_key)
    app.state.weather_provider = WeatherProvider(settings.openweathermap_api_key)

    yield

    # Shutdown: Cleanup services
    await app.state.geocoding_service.close()
    await app.state.weather_provider.close()


app = FastAPI(
    title="ChasingMana Weather API",
    description="Weather and geocoding API for ChasingMana.com",
    version="1.0.0",
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        settings.frontend_url,
        "http://localhost:5173",
        "http://localhost:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "chasingmana-api"}


# Include routers
app.include_router(geocoding_router)
app.include_router(weather_router)
