import { useState } from 'react';
import { LocationSearch } from '../components/LocationSearch';
import { CurrentWeatherCard } from '../components/CurrentWeatherCard';
import { ForecastCard } from '../components/ForecastCard';
import { getCurrentWeather, getForecast } from '../services/api';
import type { GeoLocation, CurrentWeather, ForecastResponse } from '../types/weather';

export function WeatherPage() {
  const [currentWeather, setCurrentWeather] = useState<CurrentWeather | null>(null);
  const [forecast, setForecast] = useState<ForecastResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [isLoadingLocation, setIsLoadingLocation] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function fetchWeatherData(lat: number, lon: number, displayName?: string) {
    setIsLoading(true);
    setError(null);

    try {
      const [weather, forecastData] = await Promise.all([
        getCurrentWeather(lat, lon),
        getForecast(lat, lon, 5),
      ]);
      // Use the selected location's display name if provided,
      // otherwise fall back to the API's returned location name
      if (displayName) {
        weather.location_name = displayName;
      }
      setCurrentWeather(weather);
      setForecast(forecastData);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch weather data');
      setCurrentWeather(null);
      setForecast(null);
    } finally {
      setIsLoading(false);
    }
  }

  function handleLocationSelect(location: GeoLocation) {
    fetchWeatherData(location.lat, location.lon, location.display_name);
  }

  function handleUseMyLocation() {
    if (!navigator.geolocation) {
      setError('Geolocation is not supported by your browser');
      return;
    }

    setIsLoadingLocation(true);
    setError(null);

    navigator.geolocation.getCurrentPosition(
      (position) => {
        setIsLoadingLocation(false);
        fetchWeatherData(position.coords.latitude, position.coords.longitude);
      },
      (err) => {
        setIsLoadingLocation(false);
        setError(`Location error: ${err.message}`);
      },
      { enableHighAccuracy: true, timeout: 10000, maximumAge: 300000 }
    );
  }

  return (
    <div className="weather-page">
      <header className="page-header">
        <h1>ChasingMana Weather</h1>
      </header>

      <main className="page-content">
        <LocationSearch
          onSelect={handleLocationSelect}
          onUseMyLocation={handleUseMyLocation}
          isLoadingLocation={isLoadingLocation}
        />

        {error && <div className="error-message">{error}</div>}

        {isLoading && (
          <div className="loading-state">
            <div className="spinner" />
            <p>Loading weather data...</p>
          </div>
        )}

        {!isLoading && currentWeather && (
          <section className="weather-section">
            <CurrentWeatherCard weather={currentWeather} />
          </section>
        )}

        {!isLoading && forecast && forecast.daily.length > 0 && (
          <section className="forecast-section">
            <h3>5-Day Forecast</h3>
            <div className="forecast-grid">
              {forecast.daily.map((day, index) => (
                <ForecastCard key={index} forecast={day} />
              ))}
            </div>
          </section>
        )}

        {!isLoading && !currentWeather && !error && (
          <div className="empty-state">
            <p>Search for a location or use your current location to see weather data.</p>
          </div>
        )}
      </main>
    </div>
  );
}
