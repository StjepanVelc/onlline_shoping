# System Architecture

## 1. Executive Summary
The project is split into two primary components:
- Backend API built with FastAPI (Python + SQLite)
- Frontend admin interface built with React + Vite

The architecture is designed for clear separation of responsibilities, maintainability, and secure administration workflows.

## 2. Logical Architecture
The backend follows a three-layer architecture:
- Routes layer: HTTP endpoints and error-to-status mapping
- Services layer: business rules and orchestration
- Repositories layer: SQL access and CRUD operations

Database connectivity and schema management are centralized in the data layer.

## 3. Module Structure
- [main.py](../main.py): application entry point importing the FastAPI app instance and exception handlers
- [routes/__init__.py](../routes/__init__.py): app initialization, middleware, lifecycle, logging, and router registration
- [routes](../routes): API endpoints (auth, admins, users, products, orders)
- [services](../services): business logic, validation, authentication, and transaction handling
- [repositories](../repositories): database access by domain entity
- [IO](../IO): Pydantic DTO models for requests and responses
- [data/base.py](../data/base.py): SQLite connection, schema initialization, and migration execution
- [data/database.sql](../data/database.sql): baseline DDL and indexes
- [frontend/src](../frontend/src): React pages and API helper layer

## 4. Request Lifecycle
Typical endpoint flow:
1. Client sends an HTTP request to a route handler.
2. Route layer validates and parses payloads using Pydantic DTOs.
3. Service layer enforces business rules, authorization checks, and transactions.
4. Repository layer executes SQL operations.
5. Service layer returns domain output.
6. Route layer returns JSON response with appropriate HTTP status code.

## 5. Authentication and Authorization
Authentication uses JWT with OAuth2 password flow:
- Login endpoint: POST /auth/token
- Token algorithm: HS256, including sub and admin_id claims
- Auth dependency: get_current_admin validates Bearer tokens

Authorization is privilege-based:
- require_privilege("manage_admins") protects sensitive admin operations
- super_admin is treated as a global authorization override

## 6. Data Model
Primary tables:
- users
- admins
- products
- orders
- order_items

Key relationships:
- orders.user_id -> users.id
- order_items.order_id -> orders.id
- order_items.product_id -> products.id

## 7. Transactions and Consistency
Order creation is executed in a single transaction:
- create order header
- insert order items
- decrement stock
- calculate and persist total_amount

Any failure during this flow triggers rollback.

## 8. Operational Characteristics
- Environment-driven CORS configuration
- Request logging middleware captures method, path, status, and latency
- Logs are written to logs/api.log
- Docker setup uses backend and frontend build targets from a single Dockerfile

## 9. Strengths
- Service layer can be tested independently of HTTP
- Strong separation of concerns
- Straightforward extensibility for new modules
- Predictable exception mapping and API behavior

## 10. Current Status
Current implementation status:
- Environment-based security configuration is implemented (.env.example, APP_ENV, CORS_ALLOW_ORIGINS, ALLOWED_HOSTS).
- CORS and trusted host controls are enabled through middleware configuration.
- Baseline automated tests for authentication and order flows are in place.
