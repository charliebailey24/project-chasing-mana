# Code Review Report

## 1) Executive Summary
- Verdict: Ship with fixes
- Intended behavior: FastAPI serves `/health`, `/api/geocode`, `/api/weather/current`, `/api/weather/forecast`.
- Intended behavior: Geocoding returns normalized locations with display names and coords.
- Intended behavior: Forecast aggregates 3-hour data into up to 5 daily summaries.
- Intended behavior: Frontend `/weather` supports search + geolocation and displays current + 5-day forecast.
- Intended behavior: Dev uses Vite proxy; prod uses configured API base URL.
- Top 3 risks: Production API base ignores `VITE_API_URL`, breaking deployed frontend/backends on separate origins.
- Top 3 risks: Timestamp/forecast grouping depends on server timezone, shifting day/time for users.
- Top 3 risks: E2E suite fails because `.weather-card` selector does not exist.
- What I would do next: Fix `API_BASE` to read `VITE_API_URL` and update README.
- What I would do next: Align E2E selectors or add `weather-card` class, then re-run E2E.
- What I would do next: Normalize timestamps/timezone handling and add unit tests.
- Test execution: `npm run test:run` passed (11 tests); backend pytest not run (`python` missing/`pytest` not installed).

## 2) Requirement Traceability Matrix
| Requirement | Implementation | Tests | Status (Pass/Gap) |
|---|---|---|---|
| Health endpoint returns status + service | `backend/main.py` (health_check) | `backend/tests/test_api.py` (TestHealthEndpoint), `backend/tests/test_schema.py` | Gap (backend tests not run) |
| Geocode endpoint returns locations by query/limit | `backend/routers/geocoding.py`, `backend/services/geocoding.py`, `backend/models/geocoding.py` | `backend/tests/test_api.py` (TestGeocodeEndpoint), `backend/tests/test_services_geocoding.py`, `backend/tests/test_schema.py` | Gap (backend tests not run) |
| Current weather endpoint returns normalized data | `backend/routers/weather.py`, `backend/services/weather_provider.py`, `backend/models/weather.py` | `backend/tests/test_api.py` (TestCurrentWeatherEndpoint), `backend/tests/test_services_weather.py`, `backend/tests/test_schema.py` | Gap (backend tests not run; timezone risk) |
| Forecast endpoint returns N-day aggregated forecast | `backend/routers/weather.py`, `backend/services/weather_provider.py`, `backend/models/weather.py` | `backend/tests/test_api.py` (TestForecastEndpoint), `backend/tests/test_services_weather.py`, `backend/tests/test_schema.py` | Gap (backend tests not run; timezone grouping risk) |
| Frontend search + geolocation UX | `frontend/src/pages/WeatherPage.tsx`, `frontend/src/components/LocationSearch.tsx` | `frontend/src/test/WeatherPage.test.tsx`, `frontend/src/test/LocationSearch.test.tsx`, `backend/tests/e2e/test_weather_flow.py` | Pass (unit) / Gap (e2e not run + selector mismatch) |
| Frontend renders current weather + forecast cards | `frontend/src/components/CurrentWeatherCard.tsx`, `frontend/src/components/ForecastCard.tsx` | `backend/tests/e2e/test_weather_flow.py` | Gap (e2e selector mismatch) |
| Production API base config via env/proxy | `frontend/src/services/api.ts` | (none) | Gap (implementation ignores env) |

## 3) Findings
- Requirements fixes: Clarify production API base behavior; acceptance: Given `VITE_API_URL` set in prod, frontend calls that origin; given unset in dev, proxy handles `/api`.
- Requirements fixes: Clarify timezone semantics (UTC vs location) and forecast day boundaries; acceptance: forecast days align to location midnight using `city.timezone`.
- Requirement mismatches: README says `VITE_API_URL` is used in production, but `frontend/src/services/api.ts:7` hardcodes empty base.
- Requirement mismatches: E2E test expects `.weather-card`, but `frontend/src/components/CurrentWeatherCard.tsx:18` uses `.current-weather-card`.

### P0 (Blocking)
- None found.

### P1 (Important)
- What is wrong: `API_BASE` is always `''`, ignoring `VITE_API_URL`.
- Where: `frontend/src/services/api.ts:7`.
- Why it matters: On separate frontend/backend origins in prod, requests hit the wrong origin and 404/CORS.
- Fix (minimal): Read `VITE_API_URL` with a default.

```diff
-const API_BASE = import.meta.env.PROD ? '' : '';
+const API_BASE = import.meta.env.VITE_API_URL ?? '';
```

- What is wrong: E2E selector `.weather-card` never matches the current weather card.
- Where: `backend/tests/e2e/test_weather_flow.py:56` and `frontend/src/components/CurrentWeatherCard.tsx:18`.
- Why it matters: `pytest -m e2e` fails on `test_full_weather_flow`, so CI cannot validate the end-to-end flow.
- Fix (minimal): Add a stable class or data-testid on the card (or update the selector).

```diff
-  return (
-    <div className="current-weather-card">
+  return (
+    <div className="current-weather-card weather-card">
```

- What is wrong: Timestamps and forecast day grouping use server-local time.
- Where: `backend/models/weather.py:47,64-65` and `backend/services/weather_provider.py:101-112`.
- Why it matters: Users see shifted times/days and forecast days can be off by one when server timezone != location timezone.
- Fix (minimal): Make datetimes timezone-aware (UTC) and group forecasts using `city.timezone` offset from the API.

### P2 (Nice)
- What is wrong: Frontend type expects `timezone` as `string | null` but backend returns seconds as an `int`.
- Where: `frontend/src/types/weather.ts:61` and `backend/models/weather.py:160`.
- Why it matters: Type mismatches cause subtle runtime bugs when timezone is used.
- Fix (minimal): Change type to `number | null`.

- What is wrong: Location search requests can race and show stale results.
- Where: `frontend/src/components/LocationSearch.tsx:26-45`.
- Why it matters: Slower responses can overwrite newer queries during fast typing.
- Fix (minimal): Use `AbortController` or a request id guard to ignore outdated responses.

## 4) Delete Candidates
- `backend/models/weather.py` `DailyForecast.from_openweathermap_daily` is unused (One Call API not used); removing reduces surface area.
- `backend/services/geocoding.py` `reverse` is unused by any router; delete it and related tests, or add a reverse-geocode endpoint.

## 5) Simplification Plan
- 1) Remove unused `from_openweathermap_daily` and optionally `reverse` to reduce unneeded code paths.
- 2) Add a single time-conversion helper and apply timezone offsets consistently in `CurrentWeather` and forecast grouping.
- 3) Collapse API base configuration to a single env variable (`VITE_API_URL`) with a dev default.
- 4) Use stable E2E selectors (`data-testid`) instead of CSS classes.

## 6) Cycle Time Improvements
- Add `.python-version` or update README to call `python3.11` explicitly so `python` resolves.
- Add a root test runner script that runs backend pytest (excluding e2e) and frontend vitest.
- Add a single dev command (or document `concurrently`) to start backend + frontend together.

## 7) Automation
### Test Plan
- Add `test_current_weather_uses_utc` in `backend/tests/test_services_weather.py` to assert timezone-aware timestamps (UTC).
- Add `test_forecast_groups_by_timezone_offset` in `backend/tests/test_services_weather.py` with items around midnight and non-zero `city.timezone`.
- Add `api_base_uses_env` in `frontend/src/test/api.test.ts` to assert `VITE_API_URL` is honored.
- Update E2E selectors to `data-testid` and assert the current weather card renders.

### CI Plan
- PR: run `pytest --ignore=tests/e2e` and `npm run test:run` (optionally `npm run lint`).
- Nightly: run E2E Playwright with `OPENWEATHERMAP_API_KEY` and boot both servers.

## 8) If I Had 30 Minutes Quick Patch
- Update `API_BASE` to use `VITE_API_URL` in `frontend/src/services/api.ts`.
- Add `weather-card` class (or `data-testid`) to the current weather card and align E2E selector.
- Normalize timestamps to UTC and use `city.timezone` when grouping forecast days.
- Fix `ForecastResponse.timezone` type in `frontend/src/types/weather.ts`.
