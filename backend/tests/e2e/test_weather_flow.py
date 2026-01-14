"""E2E tests for the weather application flow."""

import pytest
from playwright.sync_api import Page, expect


pytestmark = pytest.mark.e2e


class TestWeatherFlow:
    """End-to-end tests for the main weather application flow."""

    def test_weather_page_loads(self, page: Page, base_url: str):
        """Test that the weather page loads successfully."""
        page.goto(f"{base_url}/weather")

        # Check page title/header is visible
        expect(page.get_by_text("ChasingMana Weather")).to_be_visible()

    def test_search_shows_suggestions(self, page: Page, base_url: str):
        """Test that typing in search shows location suggestions."""
        page.goto(f"{base_url}/weather")

        # Type in the search box
        search_input = page.get_by_placeholder("Search for a city...")
        search_input.fill("Paris")

        # Wait for suggestions to appear (they should appear from the API)
        # Use a longer timeout as the API might take time
        suggestions = page.locator(".search-results .search-result-item")
        expect(suggestions.first).to_be_visible(timeout=10000)

    def test_full_weather_flow(self, page: Page, base_url: str):
        """
        Test the complete weather flow:
        1. Open /weather
        2. Type "Paris"
        3. Click first suggestion
        4. Assert current weather card and 5-day forecast render
        """
        # 1. Open the weather page
        page.goto(f"{base_url}/weather")
        expect(page.get_by_text("ChasingMana Weather")).to_be_visible()

        # 2. Type "Paris" in the search
        search_input = page.get_by_placeholder("Search for a city...")
        search_input.fill("Paris")

        # 3. Wait for and click the first suggestion
        suggestions = page.locator(".search-results .search-result-item")
        expect(suggestions.first).to_be_visible(timeout=10000)
        suggestions.first.click()

        # 4a. Assert current weather card renders
        # Wait for loading to complete and weather card to appear
        current_weather_card = page.locator(".weather-card")
        expect(current_weather_card).to_be_visible(timeout=15000)

        # Verify weather data is displayed (temperature, conditions, etc.)
        expect(page.locator(".weather-card .temperature")).to_be_visible()

        # 4b. Assert 5-day forecast section renders
        forecast_section = page.locator(".forecast-section")
        expect(forecast_section).to_be_visible(timeout=15000)

        # Check that forecast heading is visible
        expect(page.get_by_text("5-Day Forecast")).to_be_visible()

        # Check that forecast cards are rendered
        forecast_cards = page.locator(".forecast-card")
        expect(forecast_cards.first).to_be_visible()

    def test_use_my_location_button_exists(self, page: Page, base_url: str):
        """Test that the 'Use My Location' button is present."""
        page.goto(f"{base_url}/weather")

        location_button = page.get_by_role("button", name="Use My Location")
        expect(location_button).to_be_visible()

    def test_empty_state_shown_initially(self, page: Page, base_url: str):
        """Test that empty state message is shown when no location is selected."""
        page.goto(f"{base_url}/weather")

        empty_state = page.get_by_text("Search for a location or use your current location")
        expect(empty_state).to_be_visible()
