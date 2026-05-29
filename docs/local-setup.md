# Local Setup

This guide covers how to run the project locally using either a Python virtual environment or Docker Compose.

## Prerequisites

- Python 3.12+
- Node.js 20+ (for local frontend development)
- Docker Desktop (optional, for containerized run)

## Option A: Run Backend with Python

1. Create and activate virtual environment.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2. Install dependencies.

```powershell
pip install -r requirements.txt
```

3. Start FastAPI server.

```powershell
uvicorn main:app --reload
```

Backend URLs:
- API root: http://127.0.0.1:8000
- Swagger UI: http://127.0.0.1:8000/docs
- ReDoc: http://127.0.0.1:8000/redoc

## Option B: Run Full Stack with Docker Compose

```powershell
docker compose up --build
```

Service URLs:
- Frontend: http://127.0.0.1:5173
- Backend API: http://127.0.0.1:8000

Notes:
- Data persists via volume mapping from local data folder.
- The root Dockerfile provides separate build targets for backend and frontend.

## Environment Configuration

Copy example configuration and adjust for your environment.

```powershell
Copy-Item .env.example .env
```

Important variables:
- APP_ENV
- JWT_SECRET_KEY
- CORS_ALLOW_ORIGINS
- CORS_ALLOW_CREDENTIALS
- ALLOWED_HOSTS

## Run Tests

```powershell
python -m pytest -q
```
