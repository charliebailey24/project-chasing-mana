import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { LocationSearch } from '../components/LocationSearch';

// Mock the API module
vi.mock('../services/api', () => ({
  searchLocations: vi.fn(),
}));

// Import after mocking
import { searchLocations } from '../services/api';

const mockSearchLocations = vi.mocked(searchLocations);

describe('LocationSearch', () => {
  const mockOnSelect = vi.fn();
  const mockOnUseMyLocation = vi.fn();

  beforeEach(() => {
    vi.clearAllMocks();
  });

  function renderLocationSearch(props = {}) {
    return render(
      <LocationSearch
        onSelect={mockOnSelect}
        onUseMyLocation={mockOnUseMyLocation}
        isLoadingLocation={false}
        {...props}
      />
    );
  }

  it('renders search input', () => {
    renderLocationSearch();

    expect(screen.getByPlaceholderText(/search for a city/i)).toBeInTheDocument();
  });

  it('renders "Use My Location" button', () => {
    renderLocationSearch();

    expect(screen.getByRole('button', { name: /use my location/i })).toBeInTheDocument();
  });

  it('calls onUseMyLocation when button is clicked', async () => {
    const user = userEvent.setup();
    renderLocationSearch();

    const button = screen.getByRole('button', { name: /use my location/i });
    await user.click(button);

    expect(mockOnUseMyLocation).toHaveBeenCalledTimes(1);
  });

  it('shows "Locating..." when isLoadingLocation is true', () => {
    renderLocationSearch({ isLoadingLocation: true });

    expect(screen.getByRole('button', { name: /locating/i })).toBeInTheDocument();
  });

  it('disables button when isLoadingLocation is true', () => {
    renderLocationSearch({ isLoadingLocation: true });

    const button = screen.getByRole('button', { name: /locating/i });
    expect(button).toBeDisabled();
  });

  it('shows search results when API returns locations', async () => {
    const user = userEvent.setup();
    mockSearchLocations.mockResolvedValueOnce({
      results: [
        {
          name: 'Paris',
          lat: 48.8566,
          lon: 2.3522,
          country: 'FR',
          state: 'Ile-de-France',
          display_name: 'Paris, Ile-de-France, FR',
        },
      ],
    });

    renderLocationSearch();

    const input = screen.getByPlaceholderText(/search for a city/i);
    await user.type(input, 'Paris');

    await waitFor(() => {
      expect(screen.getByText('Paris, Ile-de-France, FR')).toBeInTheDocument();
    });
  });

  it('calls onSelect when a result is clicked', async () => {
    const user = userEvent.setup();
    const mockLocation = {
      name: 'Paris',
      lat: 48.8566,
      lon: 2.3522,
      country: 'FR',
      state: 'Ile-de-France',
      display_name: 'Paris, Ile-de-France, FR',
    };

    mockSearchLocations.mockResolvedValueOnce({
      results: [mockLocation],
    });

    renderLocationSearch();

    const input = screen.getByPlaceholderText(/search for a city/i);
    await user.type(input, 'Paris');

    await waitFor(() => {
      expect(screen.getByText('Paris, Ile-de-France, FR')).toBeInTheDocument();
    });

    await user.click(screen.getByText('Paris, Ile-de-France, FR'));

    expect(mockOnSelect).toHaveBeenCalledWith(mockLocation);
  });
});
