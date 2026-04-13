# Auth Service API Spec

## Token Refresh Endpoint
POST /v1/auth/refresh

## Request
Requires a valid refresh token.

## Response
Returns a new access token and refresh token pair.

## Failure Modes
- Expired refresh token
- Revoked session
- Rate limit exceeded
