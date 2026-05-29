# Backend Documentation

## 1. Technology Stack
- FastAPI
- SQLite
- Pydantic v2
- JWT (python-jose)
- Uvicorn

## 2. Running the Project

Local setup:
1. python -m venv .venv
2. .\.venv\Scripts\Activate.ps1
3. pip install -r requirements.txt
4. uvicorn main:app --reload

Docker:
- docker compose up --build

API documentation:
- /docs (Swagger)
- /redoc

## 3. API Endpoints

### Auth
- POST /auth/bootstrap-admin
  - Creates the first admin only when no admin records exist.
- POST /auth/token
  - OAuth2 login endpoint returning access_token and token_type.

### Admins
- POST /admins
  - Requires manage_admins privilege.
- GET /admins
  - Requires an authenticated admin user.
- GET /admins/{admin_id}
  - Requires an authenticated admin user.
- PATCH /admins/{admin_id}
  - Requires manage_admins privilege.
- DELETE /admins/{admin_id}
  - Requires manage_admins privilege.

### Users
- POST /users
- GET /users
- GET /users/{user_id}
- PATCH /users/{user_id}
- DELETE /users/{user_id}

### Products
- POST /products
- GET /products
- GET /products/{product_id}
- PATCH /products/{product_id}
- DELETE /products/{product_id}

### Orders
- POST /orders
  - Creates order and order items, validates user and stock, computes total.
- GET /orders
  - Lists orders with optional filters (user_id, status) and pagination (limit, offset).
- GET /orders/{order_id}
  - Returns order details including order_items.

## 4. DTO Models and Validation
Models are defined in [IO](../IO):
- [IO/user.py](../IO/user.py)
- [IO/product.py](../IO/product.py)
- [IO/admin.py](../IO/admin.py)

Validation examples:
- email must have valid format
- product price >= 0.01
- stock >= 0
- quantity > 0
- product name/description include extra sanitization and character restrictions

## 5. Business Rules
- Uniqueness for users, admins, and products is enforced by DB constraints and mapped to 409 or 400 responses.
- Update requests with no fields raise ValidationError.
- Orders without items are rejected.
- Negative stock levels are not allowed.

## 6. Error Handling
Custom exceptions in [services/exceptions.py](../services/exceptions.py):
- NotFoundError
- ConflictError
- ValidationError
- AuthError

Route handlers map exceptions to HTTP status codes:
- 400 ValidationError
- 401 AuthError
- 403 missing privilege
- 404 NotFoundError
- 409 ConflictError

## 7. Database
Schema and indexes are defined in [data/database.sql](../data/database.sql).

Key notes:
- foreign_keys is enabled
- indexes are present for frequent access patterns (for example orders status/date, users country)
- order_items uses a composite primary key (order_id, product_id)

Migrations:
- A lightweight SQL migration mechanism is implemented in [data/base.py](../data/base.py).
- Versioned migration files are stored in [data/migrations](../data/migrations).
- Manual migration command: python -m data.migrate

## 8. Security
- Admin passwords use PBKDF2-HMAC-SHA256 with random salt.
- JWT uses HS256.
- SECRET_KEY currently has a development fallback and must be overridden via environment variables in production.
- CORS is environment-driven through CORS_ALLOW_ORIGINS and CORS_ALLOW_CREDENTIALS.
- TrustedHostMiddleware and security headers are enabled (X-Content-Type-Options, X-Frame-Options, Referrer-Policy, Permissions-Policy).

## 9. Frontend Integration
The frontend calls the API through [frontend/src/api.js](../frontend/src/api.js).
- Base URL: VITE_API_URL or localhost:8000 fallback
- readApiError extracts the most useful message from API responses

Key pages:
- [frontend/src/pages/Login.jsx](../frontend/src/pages/Login.jsx)
- [frontend/src/pages/Products.jsx](../frontend/src/pages/Products.jsx)
- [frontend/src/pages/Orders.jsx](../frontend/src/pages/Orders.jsx)

## 10. Recent Improvements
- Added baseline auth and order-flow tests in [tests/test_auth_flow.py](../tests/test_auth_flow.py) and [tests/test_order_flow.py](../tests/test_order_flow.py)
- Added lightweight migration support with schema_migrations tracking and SQL scripts in [data/migrations](../data/migrations)
- Hardened CORS and security settings via environment-driven configuration
- Added order listing and order detail endpoints: GET /orders and GET /orders/{order_id}

Run tests:
- pytest
