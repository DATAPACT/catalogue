# MongoDB Containerized Setup — toolbox-ui

**Date:** 2026-03-18
**Project:** `DataPact/portal/dumi/toolbox-ui`
**Status:** Approved

---

## Context

`toolbox-ui` is a Next.js 16 authentication portal and dashboard aggregator. It currently has no persistent storage — Keycloak handles auth and external DataPact tools are embedded via iframes. MongoDB is being added as **infrastructure preparation** for a future backend feature (to be determined). No Next.js source code changes are included in this spec.

---

## Goals

- Deploy MongoDB as a Docker container for local development
- Deploy MongoDB on AKS (DataPact cluster) for production
- Enable authentication with configurable credentials
- Persist data using Docker volumes (dev) and Azure Managed Disks (prod)
- Keep credentials out of source control
- Follow existing DataPact monorepo conventions (Contract_Service pattern)

---

## Approach

**Option A selected:** Extend the existing `docker-compose.yml` and `helm/` directory directly. No separate compose files or external Helm chart dependencies. Consistent with how Contract_Service, DAVE, and lion_linker handle MongoDB across the monorepo.

---

## Design

### 1. Docker Compose (Local Development)

Add a `mongo` service to `docker-compose.yml` alongside the existing `frontend` service:

```yaml
mongo:
  image: mongo:7
  command: ["--auth"]
  ports:
    - "27017:27017"
  environment:
    MONGO_INITDB_ROOT_USERNAME: ${MONGO_USER}
    MONGO_INITDB_ROOT_PASSWORD: ${MONGO_PASSWORD}
    MONGO_INITDB_DATABASE: ${MONGO_DB}
  volumes:
    - mongo_data:/data/db
  networks:
    - app-network

volumes:
  mongo_data:

networks:
  app-network:
    driver: bridge
```

- Both `frontend` and `mongo` join `app-network` so future backend services can reach MongoDB at `mongo:27017`
- Authentication enabled via `--auth` flag
- Credentials sourced from `.env` (gitignored)
- Named volume `mongo_data` ensures data survives container restarts

### 2. Environment Variables

`.env` additions (local dev, gitignored):
```
MONGO_USER=root
MONGO_PASSWORD=<strong-password>
MONGO_DB=toolboxdb
MONGO_AUTH_SOURCE=admin
```

`.env.example` (committed, documents required vars):
```
MONGO_USER=root
MONGO_PASSWORD=changeme
MONGO_DB=toolboxdb
MONGO_AUTH_SOURCE=admin
```

### 3. Helm Chart (AKS Production)

Four new templates in `helm/templates/`:

#### `mongo-secret.yaml`
Kubernetes Secret containing `MONGO_USER`, `MONGO_PASSWORD`, `MONGO_DB`, `MONGO_AUTH_SOURCE`. Values sourced from `helm/values-secrets.yaml` (gitignored).

#### `mongo-storageclass.yaml`
Azure CSI StorageClass:
- Provisioner: `disk.csi.azure.com`
- SKU: `Premium_LRS`
- Reclaim policy: `Retain`
- Volume binding: `WaitForFirstConsumer`
- Allow volume expansion: `true`
- Name: `toolbox-mongo-managed-retain`

#### `mongo-statefulset.yaml`
Kubernetes StatefulSet:
- Image: `mongo:7`
- Replicas: 1
- Args: `["--auth"]`
- Port: 27017
- Credentials injected from `mongo-secret` Secret
- PVC: 20Gi via `toolbox-mongo-managed-retain` StorageClass
- Mount: `/data/db`

#### `mongo-service.yaml`
ClusterIP Service on port 27017. Internal only — not exposed via Traefik ingress. Future backend services connect via `mongo:27017` within the cluster namespace.

### 4. values.yaml additions

```yaml
mongo:
  enabled: true
  image:
    repository: mongo
    tag: "7"
    pullPolicy: IfNotPresent
  persistence:
    enabled: true
    storageClass: "toolbox-mongo-managed-retain"
    size: 20Gi
  service:
    port: 27017
  credentialsSecretName: mongo-secret
```

### 5. values-secrets.yaml (gitignored)

```yaml
mongo:
  user: root
  password: "<strong-generated-password>"
  db: toolboxdb
  authSource: admin
```

---

## Files Changed

| File | Action |
|------|--------|
| `docker-compose.yml` | Modified — add `mongo` service, `mongo_data` volume, `app-network` |
| `.env` | Modified — add `MONGO_*` vars |
| `.env.example` | Created — document all env vars with placeholders |
| `helm/values.yaml` | Modified — add `mongo:` block |
| `helm/values-secrets.yaml` | Created — prod credentials (gitignored) |
| `helm/templates/mongo-secret.yaml` | Created |
| `helm/templates/mongo-storageclass.yaml` | Created |
| `helm/templates/mongo-statefulset.yaml` | Created |
| `helm/templates/mongo-service.yaml` | Created |
| `.gitignore` | Verified — `.env` and `helm/values-secrets.yaml` are excluded |

---

## Security Notes

- Root credentials never committed to git
- Auth always enabled (`--auth` flag in both dev and prod)
- MongoDB not exposed outside the cluster (ClusterIP only)
- Azure Premium_LRS with Retain policy prevents accidental data loss on PVC deletion

---

## Out of Scope

- MongoDB replica sets or sharding
- Separate non-root application user (can be added later via init script)
- Backend API routes or Next.js source changes
- Data migration scripts
