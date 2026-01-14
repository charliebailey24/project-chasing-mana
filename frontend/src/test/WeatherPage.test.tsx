import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { WeatherPage } from '../pages/WeatherPage';

// Mock the API module
vi.mock('../services/api', () => ({
  searchLocations: vi.fn(),
  getCurrentWeather: vi.fn(),
  getForecast: vi.fn(),
}));

function renderWeatherPage() {
  return render(
    <BrowserRouter>
      <WeatherPage />
    </BrowserRouter>
  );
}

describe('WeatherPage', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders the weather page', () => {
    renderWeatherPage();

    expect(screen.getByText('ChasingMana Weather')).toBeInTheDocument();
  });

  it('shows "Use my location" button', () => {
    renderWeatherPage();

    const locationButton = screen.getByRole('button', { name: /use my location/i });
    expect(locationButton).toBeInTheDocument();
  });

  it('shows search input placeholder', () => {
    renderWeatherPage();

    const searchInput = screen.getByPlaceholderText(/search for a city/i);
    expect(searchInput).toBeInTheDocument();
  });

  it('shows empty state message initially', () => {
    renderWeatherPage();

    expect(
      screen.getByText(/search for a location or use your current location/i)
    ).toBeInTheDocument();
  });
});
