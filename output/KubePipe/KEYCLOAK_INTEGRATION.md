# Keycloak Authentication Integration

KubePipe integrates [Keycloak](https://www.keycloak.org/) as its identity and access management (IAM) provider, enabling OIDC-based authentication, role-based access control (RBAC), and single sign-on (SSO).

## Architecture

```
┌─────────────────┐     OIDC Authorization Code Flow     ┌─────────────────┐
│   React UI      │ ──────────────────────────────────▶ │   Keycloak      │
│  (port 3000)    │ ◀────────────────────────────────── │  (port 8085)    │
│                 │     Access + Refresh Tokens          │                 │
└────────┬────────┘                                      └─────────────────┘
         │ Bearer Token (Authorization header)
         ▼
┌─────────────────┐     JWKS / Introspection             ┌─────────────────┐
│  FastAPI Backend│ ──────────────────────────────────▶ │   Keycloak      │
│  (port 8001)    │     Token Validation                 │  (port 8085)    │
└─────────────────┘                                      └─────────────────┘
```

## Components

### 1. Keycloak Server (Docker)
- **Script**: `scripts/setup_keycloak.sh`
- **Container**: `kubepipe-keycloak` (Docker)
- **Port**: 8085
- **Admin Console**: http://localhost:8085/admin (admin/admin)
- **Realm**: `kubepipe`

### 2. Backend Auth Module
- **File**: `kubepipe/core/keycloak_auth.py`
- JWT validation via Keycloak JWKS endpoint
- Token introspection fallback
- FastAPI dependencies: `get_current_user`, `require_role`, `optional_auth`
- Graceful degradation: when `KEYCLOAK_ENABLED=false`, all endpoints allow anonymous access

### 3. API Endpoints
- `GET /api/v1/auth/status` — Auth configuration status
- `GET /api/v1/auth/config` — Keycloak config for frontend
- `GET /api/v1/auth/me` — Current user info (requires Bearer token)
- `POST /api/v1/auth/token` — Exchange authorization code for tokens
- `POST /api/v1/auth/refresh` — Refresh access token
- `POST /api/v1/auth/logout` — Revoke tokens

### 4. Frontend Integration
- **Context**: `ui/src/context/KeycloakContext.jsx`
- `KeycloakProvider` wraps the entire app
- `useKeycloak()` hook for login/logout/user info
- `withAuth(Component)` HOC for route protection
- `withRole(...roles)(Component)` HOC for role-based access
- API client automatically injects Bearer token from localStorage

## Quick Start

### 1. Start Keycloak
```bash
bash scripts/setup_keycloak.sh
```
This starts Keycloak in Docker, creates the `kubepipe` realm, `kubepipe-ui` and `kubepipe-api` clients, roles, and test users.

### 2. Start KubePipe
```bash
bash scripts/start_all.sh
```
Keycloak is automatically started if Docker is available.

### 3. Login
Open http://localhost:3000 — you'll see a "Login with Keycloak" button if auth is enabled. Click it to be redirected to Keycloak's login page.

### 4. Stop Everything
```bash
bash scripts/stop_all.sh
```
This stops KubePipe services AND the Keycloak Docker container.

## Test Users

| Username | Password | Role | Access |
|----------|----------|------|--------|
| admin | admin123 | admin | Full access |
| datascientist | ds123 | data_scientist | Pipeline management |
| viewer | viewer123 | viewer | Read-only dashboards |
| compliance | compliance123 | compliance_officer | Consent & policy management |

## Configuration

### Environment Variables
| Variable | Default | Description |
|----------|---------|-------------|
| `KEYCLOAK_ENABLED` | `false` | Enable/disable authentication |
| `KEYCLOAK_URL` | `http://localhost:8085` | Keycloak server URL |
| `KEYCLOAK_REALM` | `kubepipe` | Keycloak realm name |
| `KEYCLOAK_API_CLIENT_ID` | `kubepipe-api` | Backend client ID (bearer-only) |

### Disabling Auth
Set `KEYCLOAK_ENABLED=false` or remove `~/.kubepipe_keycloak_env`:
```bash
export KEYCLOAK_ENABLED=false
bash scripts/start_all.sh
```
When disabled, all endpoints allow anonymous access with admin privileges.

## Roles & Permissions

| Role | Description | Pages |
|------|-------------|-------|
| `admin` | Full access | All pages |
| `data_scientist` | Pipeline management | Dashboard, Pipelines, Sustainability |
| `viewer` | Read-only | Dashboard, Sustainability, Compliance |
| `compliance_officer` | Consent & policy | Consent Manager, Policy Engine, Compliance |

## Token Flow

1. User clicks "Login with Keycloak" in the UI
2. Browser redirects to Keycloak login page
3. User authenticates with username/password
4. Keycloak redirects back to `http://localhost:3000?code=...`
5. Frontend sends code to `POST /api/v1/auth/token`
6. Backend exchanges code with Keycloak for access + refresh tokens
7. Tokens stored in localStorage
8. API client injects `Authorization: Bearer <token>` on every request
9. Backend validates token via JWKS or introspection
10. On 401, frontend tries refresh token, then redirects to login

## Security Notes

- Access tokens expire after 30 minutes (configurable in Keycloak)
- Refresh tokens expire after 10 hours
- Token validation uses RS256 signatures via Keycloak's JWKS endpoint
- Fallback: token introspection via Keycloak's introspection endpoint
- Client secrets are used for confidential clients
- PKCE (S256) is enabled for the frontend client
