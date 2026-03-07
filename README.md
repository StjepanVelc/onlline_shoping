# Online Shopping Backend API

## Project Description

RESTful backend API for e-commerce platform built with FastAPI. Implements secure user and product management with JWT authentication, role-based admin access, and server-side order processing.

## Features

- **User Management** - CRUD operations with validation and search
- **Product Catalog** - Inventory management with stock tracking
- **Order Processing** - Server-side price calculation and stock validation
- **Admin Panel** - JWT/OAuth2 protected admin endpoints with privilege-based authorization
- **Pagination** - Query parameters (`limit`, `offset`) on all list endpoints
- **Auto Documentation** - Swagger UI and ReDoc available out-of-the-box

## Tech Stack

- **FastAPI** - Modern async web framework
- **SQLite** - Embedded relational database
- **Pydantic** - Data validation and serialization
- **JWT** - Token-based authentication (python-jose)
- **OAuth2** - Password flow for secure login
- **Uvicorn** - ASGI server

**Architecture**: Three-tier pattern (Routes → Services → Repositories)

## How to Run

### 1. Setup Environment

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### 2. Start Server

```powershell
uvicorn main:app --reload
```

### 3. Run with Docker

```powershell
docker compose up --build
```

- API: http://127.0.0.1:8000
- Data is persisted via volume mapping: `./data:/app/data`

### 4. Access API

- **Swagger UI**: http://127.0.0.1:8000/docs
- **ReDoc**: http://127.0.0.1:8000/redoc

### 5. Bootstrap Admin (First Time)

```http
POST /auth/bootstrap-admin
{
  "username": "admin",
  "email": "admin@example.com",
  "password": "secure_password",
  "privileges": ["super_admin"]
}
```

### 6. Obtain JWT Token

```http
POST /auth/token
Form Data:
  username: admin
  password: secure_password
```

Use the returned `access_token` as Bearer token in Swagger Authorize button.

Run with Docker

docker compose up --build
API available at http://localhost:8000/docs