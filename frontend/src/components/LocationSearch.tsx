import { useState, useEffect, useRef } from 'react';
import { useDebounce } from '../hooks/useDebounce';
import { searchLocations } from '../services/api';
import type { GeoLocation } from '../types/weather';

interface LocationSearchProps {
  onSelect: (location: GeoLocation) => void;
  onUseMyLocation: () => void;
  isLoadingLocation: boolean;
}

export function LocationSearch({
  onSelect,
  onUseMyLocation,
  isLoadingLocation,
}: LocationSearchProps) {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<GeoLocation[]>([]);
  const [isOpen, setIsOpen] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const wrapperRef = useRef<HTMLDivElement>(null);

  const debouncedQuery = useDebounce(query, 300);
  const abortControllerRef = useRef<AbortController | null>(null);

  useEffect(() => {
    async function fetchLocations() {
      if (debouncedQuery.length < 2) {
        setResults([]);
        setIsOpen(false);
        return;
      }

      // Abort previous request if still pending
      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
      }
      abortControllerRef.current = new AbortController();

      setIsLoading(true);
      setError(null);

      try {
        const response = await searchLocations(debouncedQuery, abortControllerRef.current.signal);
        setResults(response.results);
        setIsOpen(response.results.length > 0);
      } catch (err) {
        // Ignore aborted requests
        if (err instanceof Error && err.name === 'AbortError') {
          return;
        }
        setError('Failed to search locations');
        setResults([]);
      } finally {
        setIsLoading(false);
      }
    }

    fetchLocations();

    return () => {
      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
      }
    };
  }, [debouncedQuery]);

  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (wrapperRef.current && !wrapperRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    }

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  function handleSelect(location: GeoLocation) {
    setQuery(location.display_name);
    setIsOpen(false);
    onSelect(location);
  }

  return (
    <div className="location-search" ref={wrapperRef}>
      <div className="search-row">
        <div className="search-input-wrapper">
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search for a city..."
            className="search-input"
            onFocus={() => results.length > 0 && setIsOpen(true)}
          />
          {isLoading && <span className="search-spinner" />}
        </div>
        <button
          onClick={onUseMyLocation}
          disabled={isLoadingLocation}
          className="location-btn"
          title="Use my location"
        >
          {isLoadingLocation ? 'Locating...' : '\ud83d\udccd Use My Location'}
        </button>
      </div>

      {error && <div className="search-error">{error}</div>}

      {isOpen && results.length > 0 && (
        <ul className="search-results">
          {results.map((location, index) => (
            <li
              key={`${location.lat}-${location.lon}-${index}`}
              onClick={() => handleSelect(location)}
              className="search-result-item"
            >
              {location.display_name}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
