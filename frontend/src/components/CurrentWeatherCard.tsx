import { WeatherIcon } from './WeatherIcon';
import type { CurrentWeather } from '../types/weather';

interface CurrentWeatherCardProps {
  weather: CurrentWeather;
}

export function CurrentWeatherCard({ weather }: CurrentWeatherCardProps) {
  const formatTime = (isoString: string | null) => {
    if (!isoString) return '--';
    return new Date(isoString).toLocaleTimeString([], {
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  return (
    <div className="current-weather-card weather-card" data-testid="current-weather-card">
      <div className="weather-header">
        <h2>{weather.location_name}</h2>
        <p className="weather-description">{weather.condition.description}</p>
      </div>

      <div className="weather-main">
        <WeatherIcon
          icon={weather.condition.icon}
          description={weather.condition.description}
          size={72}
        />
        <div className="temperature">
          <span className="temp-value">{Math.round(weather.temp)}</span>
          <span className="temp-unit">&deg;C</span>
        </div>
      </div>

      <div className="weather-details">
        <div className="detail-item">
          <span className="detail-label">Feels like</span>
          <span className="detail-value">{Math.round(weather.feels_like)}&deg;C</span>
        </div>
        <div className="detail-item">
          <span className="detail-label">High / Low</span>
          <span className="detail-value">
            {Math.round(weather.temp_max)}&deg; / {Math.round(weather.temp_min)}&deg;
          </span>
        </div>
        <div className="detail-item">
          <span className="detail-label">Humidity</span>
          <span className="detail-value">{weather.humidity}%</span>
        </div>
        <div className="detail-item">
          <span className="detail-label">Wind</span>
          <span className="detail-value">{weather.wind_speed} m/s</span>
        </div>
        <div className="detail-item">
          <span className="detail-label">Pressure</span>
          <span className="detail-value">{weather.pressure} hPa</span>
        </div>
        <div className="detail-item">
          <span className="detail-label">Clouds</span>
          <span className="detail-value">{weather.clouds}%</span>
        </div>
        <div className="detail-item">
          <span className="detail-label">Sunrise</span>
          <span className="detail-value">{formatTime(weather.sunrise)}</span>
        </div>
        <div className="detail-item">
          <span className="detail-label">Sunset</span>
          <span className="detail-value">{formatTime(weather.sunset)}</span>
        </div>
      </div>
    </div>
  );
}
