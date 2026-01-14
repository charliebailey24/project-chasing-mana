import { WeatherIcon } from './WeatherIcon';
import type { DailyForecast } from '../types/weather';

interface ForecastCardProps {
  forecast: DailyForecast;
}

export function ForecastCard({ forecast }: ForecastCardProps) {
  const formatDay = (isoString: string) => {
    const date = new Date(isoString);
    const today = new Date();
    const tomorrow = new Date(today);
    tomorrow.setDate(tomorrow.getDate() + 1);

    if (date.toDateString() === today.toDateString()) {
      return 'Today';
    }
    if (date.toDateString() === tomorrow.toDateString()) {
      return 'Tomorrow';
    }
    return date.toLocaleDateString([], { weekday: 'short', month: 'short', day: 'numeric' });
  };

  return (
    <div className="forecast-card">
      <div className="forecast-day">{formatDay(forecast.date)}</div>
      <WeatherIcon
        icon={forecast.condition.icon}
        description={forecast.condition.description}
        size={36}
      />
      <div className="forecast-temps">
        <span className="temp-high">{Math.round(forecast.temp_max)}&deg;</span>
        <span className="temp-low">{Math.round(forecast.temp_min)}&deg;</span>
      </div>
      <div className="forecast-pop">
        {forecast.pop > 0 && (
          <span className="pop-value">\ud83d\udca7 {Math.round(forecast.pop * 100)}%</span>
        )}
      </div>
    </div>
  );
}
