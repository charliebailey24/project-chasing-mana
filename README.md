# ChasingMana

A full-stack weather application with a Python FastAPI backend and React frontend.

## Project Structure

```
project-chasing-mana/
├── backend/
│   ├── main.py              # FastAPI app entry point
│   ├── config.py            # Settings from environment
│   ├── requirements.txt     # Python dependencies
│   ├── models/              # Pydantic models
│   │   ├── geocoding.py     # Location models
│   │   └── weather.py       # Weather models
│   ├── services/            # Business logic
│   │   ├── geocoding.py     # Geocoding service
│   │   └── weather_provider.py  # Weather API service
│   └── routers/             # API endpoints
│       ├── geocoding.py     # /api/geocode
│       └── weather.py       # /api/weather/*
├── frontend/
│   ├── src/
│   │   ├── components/      # React components
│   │   ├── pages/           # Page components
│   │   ├── hooks/           # Custom hooks
│   │   ├── services/        # API client
│   │   └── types/           # TypeScript types
│   └── package.json
└── README.md
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check |
| `/api/geocode?q=` | GET | Search locations by name |
| `/api/weather/current?lat=&lon=` | GET | Current weather |
| `/api/weather/forecast?lat=&lon=&days=5` | GET | 5-day forecast |

## Prerequisites

- Python 3.11+
- Node.js 18+
- OpenWeatherMap API key (free tier works)

## Local Development

### 1. Get an OpenWeatherMap API Key

Sign up at https://openweathermap.org/api and get a free API key.

### 2. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env
# Edit .env and add your OPENWEATHERMAP_API_KEY

# Run the server
uvicorn main:app --reload --port 8000
```

Backend runs at: http://localhost:8000
API docs at: http://localhost:8000/docs

### 3. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Run dev server
npm run dev
```

Frontend runs at: http://localhost:5173/weather

The Vite dev server proxies `/api` requests to the backend automatically.

## Deployment

### Backend (Render)

1. Create a new Web Service on Render
2. Connect your GitHub repo
3. Configure:
   - **Root Directory**: `backend`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
4. Add environment variables:
   - `OPENWEATHERMAP_API_KEY`: your API key
   - `FRONTEND_URL`: your Vercel frontend URL

### Backend (Fly.io)

```bash
cd backend

# Create fly.toml
cat > fly.toml << 'EOF'
app = "chasingmana-api"
primary_region = "sjc"

[build]
  builder = "paketobuildpacks/builder:base"

[env]
  PORT = "8080"

[http_service]
  internal_port = 8080
  force_https = true
  auto_stop_machines = true
  auto_start_machines = true
  min_machines_running = 0
EOF

# Deploy
fly launch
fly secrets set OPENWEATHERMAP_API_KEY=your_key_here
fly secrets set FRONTEND_URL=https://your-app.vercel.app
fly deploy
```

### Frontend (Vercel)

1. Import project to Vercel
2. Configure:
   - **Root Directory**: `frontend`
   - **Framework Preset**: Vite
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`
3. Add environment variable (if not using proxy):
   - `VITE_API_URL`: your backend URL

For production, update `frontend/src/services/api.ts` to use the deployed backend URL:
```typescript
const API_BASE = import.meta.env.PROD
  ? 'https://your-backend-url.com'
  : '';
```

## Environment Variables

### Backend
| Variable | Description | Default |
|----------|-------------|---------|
| `OPENWEATHERMAP_API_KEY` | OpenWeatherMap API key | (required) |
| `FRONTEND_URL` | Frontend URL for CORS | `http://localhost:5173` |

### Frontend
| Variable | Description | Default |
|----------|-------------|---------|
| `VITE_API_URL` | Backend API URL | (uses proxy in dev) |

## Testing

The project includes comprehensive tests across backend, frontend, and E2E.

### Quick Start

```bash
# Backend tests (from backend/)
cd backend
pip install -r requirements.txt
pytest

# Frontend tests (from frontend/)
cd frontend
npm install
npm test

# E2E tests (requires both servers running)
cd backend
pytest -m e2e
```

### Backend Tests (Python/pytest)

Located in `backend/tests/`:

| Test File | Description |
|-----------|-------------|
| `test_services_geocoding.py` | Unit tests for geocoding service parsing and error handling |
| `test_services_weather.py` | Unit tests for weather provider normalization and error handling |
| `test_api.py` | Integration tests using FastAPI TestClient |
| `test_schema.py` | Schemathesis OpenAPI schema validation tests |

**Commands:**

```bash
cd backend

# Run all backend tests (excluding E2E)
pytest

# Run with coverage
pytest --cov=. --cov-report=html

# Run specific test file
pytest tests/test_api.py

# Run only unit tests
pytest tests/test_services_*.py

# Run integration tests
pytest tests/test_api.py

# Run schema tests
pytest tests/test_schema.py -v
```

### Frontend Tests (Vitest + React Testing Library)

Located in `frontend/src/test/`:

| Test File | Description |
|-----------|-------------|
| `WeatherPage.test.tsx` | Tests for main weather page rendering |
| `LocationSearch.test.tsx` | Tests for location search component |

**Commands:**

```bash
cd frontend

# Run tests in watch mode
npm test

# Run tests once
npm run test:run

# Run with coverage
npm run test:coverage
```

### E2E Tests (Playwright for Python)

Located in `backend/tests/e2e/`:

| Test File | Description |
|-----------|-------------|
| `test_weather_flow.py` | Full user flow: search → select → view weather |

**Prerequisites for E2E:**
1. Backend server running on `http://localhost:8000`
2. Frontend server running on `http://localhost:5173`
3. Playwright browsers installed

**Setup:**

```bash
cd backend

# Install Playwright browsers (one-time)
playwright install chromium

# Or install all browsers
playwright install
```

**Commands:**

```bash
cd backend

# Run E2E tests
pytest -m e2e

# Run E2E with headed browser (visible)
pytest -m e2e --headed

# Run E2E with specific browser
pytest -m e2e --browser chromium
pytest -m e2e --browser firefox
pytest -m e2e --browser webkit
```

### CI Integration

Example GitHub Actions workflow:

```yaml
name: Tests

on: [push, pull_request]

jobs:
  backend-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - name: Install dependencies
        working-directory: backend
        run: pip install -r requirements.txt
      - name: Run tests
        working-directory: backend
        run: pytest --ignore=tests/e2e

  frontend-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '18'
      - name: Install dependencies
        working-directory: frontend
        run: npm ci
      - name: Run tests
        working-directory: frontend
        run: npm run test:run

  e2e-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - uses: actions/setup-node@v4
        with:
          node-version: '18'
      - name: Install backend dependencies
        working-directory: backend
        run: pip install -r requirements.txt
      - name: Install Playwright
        run: playwright install chromium
      - name: Install frontend dependencies
        working-directory: frontend
        run: npm ci
      - name: Start backend
        working-directory: backend
        run: uvicorn main:app --port 8000 &
        env:
          OPENWEATHERMAP_API_KEY: ${{ secrets.OPENWEATHERMAP_API_KEY }}
      - name: Start frontend
        working-directory: frontend
        run: npm run dev &
      - name: Wait for servers
        run: sleep 10
      - name: Run E2E tests
        working-directory: backend
        run: pytest -m e2e
```
