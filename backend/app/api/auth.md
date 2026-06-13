# Auth Module

## Purpose
The Auth module handles user authentication, registration, session management, and JWT token issuance/refreshing. It ensures secure access to the PulseTask platform.

## Public API
### REST Endpoints
- `POST /api/v1/auth/signup`: Registers a new user.
- `POST /api/v1/auth/login`: Authenticates user and returns Access & Refresh tokens.
- `POST /api/v1/auth/refresh`: Issues a new access token using a valid refresh token.
- `POST /api/v1/auth/logout`: Revokes the user's refresh token.
- `GET /api/v1/auth/me`: Retrieves current user information (requires JWT).

## Data Models
### User
- `id`: Unique identifier (ObjectId).
- `email`: User's primary email address (unique).
- `name`: Display name.
- `password_hash`: Bcrypt hashed password.
- `created_at`: Creation timestamp.
- `disabled`: Boolean flag for account suspension.

### Token
- `access_token`: Short-lived JWT for API access.
- `refresh_token`: Long-lived token for session persistence.

## Events Emitted/Consumed
- **Emitted**: None (Auth is primarily request-response).
- **Consumed**: None.

## Invariants
- Email must be unique and valid format.
- Passwords must be at least 8 characters.
- Refresh tokens are revoked after use (one-time use for rotation).

## Edge Cases
- **Concurrent Logins**: Multiple refresh tokens can be active for different devices.
- **Token Stealing**: Revoking a refresh token invalidates that specific device session.
- **Rate Limiting**: Password attempts are limited to 5 per 60 seconds per user (in-memory).

## Test Coverage
- Unit tests for password hashing and validation in `backend/tests/unit/test_auth_service.py`.
- Integration tests for signup/login flows in `backend/tests/integration/test_auth_api.py`.
