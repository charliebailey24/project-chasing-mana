export interface GeoLocation {
  name: string;
  lat: number;
  lon: number;
  country: string;
  state: string | null;
  display_name: string;
}

export interface GeocodingResponse {
  results: GeoLocation[];
}

export interface WeatherCondition {
  id: number;
  main: string;
  description: string;
  icon: string;
}

export interface CurrentWeather {
  location_name: string;
  lat: number;
  lon: number;
  timestamp: string;
  temp: number;
  feels_like: number;
  temp_min: number;
  temp_max: number;
  humidity: number;
  pressure: number;
  wind_speed: number;
  wind_deg: number;
  clouds: number;
  visibility: number | null;
  condition: WeatherCondition;
  sunrise: string | null;
  sunset: string | null;
}

export interface DailyForecast {
  date: string;
  temp_day: number;
  temp_min: number;
  temp_max: number;
  temp_night: number;
  feels_like_day: number;
  humidity: number;
  wind_speed: number;
  wind_deg: number;
  clouds: number;
  pop: number;
  rain: number | null;
  snow: number | null;
  condition: WeatherCondition;
}

export interface ForecastResponse {
  lat: number;
  lon: number;
  timezone: string | null;
  daily: DailyForecast[];
}
