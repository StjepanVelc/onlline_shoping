# Authentication Quick Start

This project uses OAuth2 password flow with JWT access tokens for admin authentication.

## 1. Bootstrap First Admin

Use this endpoint only once on a new database.

```http
POST /auth/bootstrap-admin
Content-Type: application/json

{
  "username": "admin",
  "email": "admin@example.com",
  "password": "secure_password",
  "privileges": ["super_admin"]
}
```

Expected response:
- HTTP 201 with created admin payload

If admins already exist:
- HTTP 400 with validation message

## 2. Obtain Access Token

```http
POST /auth/token
Content-Type: application/x-www-form-urlencoded

username=admin&password=secure_password
```

Expected response:

```json
{
  "access_token": "<jwt>",
  "token_type": "bearer"
}
```

## 3. Call Protected Endpoints

Send token in Authorization header:

```http
Authorization: Bearer <jwt>
```

Example protected endpoint:
- GET /admins

## 4. Authorization Model

- Any authenticated admin can access endpoints protected by get_current_admin.
- Privileged endpoints use require_privilege and enforce fine-grained permissions.
- super_admin acts as global override for privilege checks.

## 5. Common Errors

- 401 Unauthorized: invalid, missing, or expired token
- 403 Forbidden: authenticated, but missing required privilege
- 400 Bad Request: invalid payload or bootstrap attempted after first admin
