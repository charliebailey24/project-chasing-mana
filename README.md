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
