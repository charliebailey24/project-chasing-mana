import type {
  GeocodingResponse,
  CurrentWeather,
  ForecastResponse,
} from '../types/weather';

const API_BASE = import.meta.env.VITE_API_URL ?? '';

export async function searchLocations(query: string, signal?: AbortSignal): Promise<GeocodingResponse> {
  const response = await fetch(
    `${API_BASE}/api/geocode?q=${encodeURIComponent(query)}`,
    { signal }
  );
  if (!response.ok) {
    throw new Error(`Geocoding failed: ${response.statusText}`);
  }
  return response.json();
}

export async function getCurrentWeather(
  lat: number,
  lon: number
): Promise<CurrentWeather> {
  const response = await fetch(
    `${API_BASE}/api/weather/current?lat=${lat}&lon=${lon}&units=imperial`
  );
  if (!response.ok) {
    throw new Error(`Weather fetch failed: ${response.statusText}`);
  }
  return response.json();
}

export async function getForecast(
  lat: number,
  lon: number,
  days: number = 5
): Promise<ForecastResponse> {
  const response = await fetch(
    `${API_BASE}/api/weather/forecast?lat=${lat}&lon=${lon}&days=${days}&units=imperial`
  );
  if (!response.ok) {
    throw new Error(`Forecast fetch failed: ${response.statusText}`);
  }
  return response.json();
}
