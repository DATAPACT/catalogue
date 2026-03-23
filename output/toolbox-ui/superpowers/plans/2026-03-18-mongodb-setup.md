# MongoDB Containerized Setup — Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a MongoDB containerized setup to `toolbox-ui` for both local Docker development and AKS production deployment, as infrastructure preparation for a future backend feature.

**Architecture:** Extend the existing `docker-compose.yml` with a `mongo` service sharing a bridge network with `frontend`. Add four Helm templates (`mongo-secret`, `mongo-storageclass`, `mongo-statefulset`, `mongo-service`) to the existing `helm/templates/` directory following the Contract_Service pattern exactly. Credentials managed via `.env` (dev) and Kubernetes Secret (prod).

**Tech Stack:** Docker / docker-compose, MongoDB 7, Helm 3, Kubernetes StatefulSet, Azure CSI (`disk.csi.azure.com`), Premium_LRS managed disks.

**Spec:** `docs/superpowers/specs/2026-03-18-mongodb-setup-design.md`

---

## File Map

| File | Action | Responsibility |
|------|--------|----------------|
| `docker-compose.yml` | Modify | Add `mongo` service, `mongo_data` volume, `app-network` |
| `.env` | Modify | Add `MONGO_*` vars for local dev |
| `.env.example` | Create | Document all env vars with safe placeholder values |
| `.gitignore` | Modify | Add `helm/values-secrets.yaml` exclusion |
| `helm/values.yaml` | Modify | Add `mongo:` config block |
| `helm/values-secrets.yaml` | Create | Prod credentials (gitignored) |
| `helm/templates/mongo-secret.yaml` | Create | K8s Secret with credentials |
| `helm/templates/mongo-storageclass.yaml` | Create | Azure CSI StorageClass (Premium_LRS, Retain) |
| `helm/templates/mongo-statefulset.yaml` | Create | MongoDB StatefulSet with auth + PVC |
| `helm/templates/mongo-service.yaml` | Create | ClusterIP Service on port 27017 |

---

## Task 1: Update `.gitignore`

**Files:**
- Modify: `.gitignore`

- [ ] **Step 1: Add `helm/values-secrets.yaml` to `.gitignore`**

Open `.gitignore` and add after the `# env files` block:

```gitignore
# helm secrets
helm/values-secrets.yaml
```

Note: `.env*` is already covered by line 34 of the existing `.gitignore`, so `.env` is already excluded.

- [ ] **Step 2: Verify `.env` is already excluded**

Run:
```bash
git check-ignore -v .env
```
Expected output: `.gitignore:34:.env*    .env`

- [ ] **Step 3: Commit**

```bash
git add .gitignore
git commit -m "chore: gitignore helm/values-secrets.yaml"
```

---

## Task 2: Create `.env.example`

**Files:**
- Create: `.env.example`

- [ ] **Step 1: Create `.env.example` with all vars documented**

```bash
cat > .env.example << 'EOF'
# Keycloak / NextAuth
KEYCLOAK_CLIENT_ID=your-client-id
KEYCLOAK_CLIENT_SECRET=your-client-secret
KEYCLOAK_ISSUER=https://auth.dp.assistcloud.net/realms/master
NEXTAUTH_SECRET=your-nextauth-secret
NEXTAUTH_URL=http://localhost:3000
BASE_LOGIN_URL=https://auth.dp.assistcloud.net

# MongoDB
MONGO_USER=root
MONGO_PASSWORD=changeme
MONGO_DB=toolboxdb
MONGO_AUTH_SOURCE=admin
EOF
```

- [ ] **Step 2: Verify `.env.example` is NOT gitignored**

The existing `.gitignore` has `.env*` — this would exclude `.env.example` too. Check:
```bash
git check-ignore -v .env.example
```

If it is ignored, add an explicit exception to `.gitignore`:
```gitignore
# env files (can opt-in for committing if needed)
.env*
!.env.example
```

- [ ] **Step 3: Commit**

```bash
git add .env.example .gitignore
git commit -m "docs: add .env.example with MongoDB vars"
```

---

## Task 3: Update `.env` for local dev

**Files:**
- Modify: `.env`

- [ ] **Step 1: Append MongoDB vars to `.env`**

Open `.env` and add at the end:

```env
# MongoDB
MONGO_USER=root
MONGO_PASSWORD=changeme_local
MONGO_DB=toolboxdb
MONGO_AUTH_SOURCE=admin
```

Use a non-trivial local password — `changeme_local` is fine for dev but should be something you remember.

- [ ] **Step 2: Verify `.env` is not tracked by git**

```bash
git status .env
```
Expected: `.env` should not appear (it is gitignored via `.env*`).

---

## Task 4: Update `docker-compose.yml`

**Files:**
- Modify: `docker-compose.yml`

- [ ] **Step 1: Add `mongo` service, shared network, and named volume**

Replace the contents of `docker-compose.yml` with:

```yaml
services:
  frontend:
    build:
      context: .
      dockerfile: Dockerfile.dev
    ports:
      - "3000:3000"
    environment:
      - NODE_ENV=development
      - CHOKIDAR_USEPOLLING=true
      - WATCHPACK_POLLING=true
    volumes:
      - .:/app
      - /app/node_modules
      - /app/.next
    networks:
      - app-network

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

- [ ] **Step 2: Verify docker-compose config is valid**

```bash
docker compose config
```
Expected: Prints the resolved config with no errors. Confirm `MONGO_USER`, `MONGO_PASSWORD`, `MONGO_DB` resolve to your `.env` values.

- [ ] **Step 3: Bring up MongoDB and verify it starts**

```bash
docker compose up mongo -d
docker compose logs mongo
```
Expected: Logs show `{"msg":"Waiting for connections","attr":{"port":27017,...}}` — MongoDB is ready.

- [ ] **Step 4: Verify auth is enabled**

```bash
docker compose exec mongo mongosh --eval "db.adminCommand({listDatabases:1})" --quiet
```
Expected: Error like `MongoServerError: Command listDatabases requires authentication` — confirms `--auth` is working.

- [ ] **Step 5: Verify auth works with credentials**

```bash
docker compose exec mongo mongosh \
  -u ${MONGO_USER:-root} \
  -p ${MONGO_PASSWORD:-changeme_local} \
  --authenticationDatabase admin \
  --eval "db.adminCommand({listDatabases:1})" \
  --quiet
```
Expected: JSON output listing databases including `toolboxdb`.

- [ ] **Step 6: Stop containers**

```bash
docker compose down
```

- [ ] **Step 7: Commit**

```bash
git add docker-compose.yml
git commit -m "feat: add MongoDB service to docker-compose"
```

---

## Task 5: Update `helm/values.yaml`

**Files:**
- Modify: `helm/values.yaml`

- [ ] **Step 1: Append `mongo:` block to `helm/values.yaml`**

Add at the end of the file:

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

- [ ] **Step 2: Commit**

```bash
git add helm/values.yaml
git commit -m "feat: add mongo values block to helm chart"
```

---

## Task 6: Create `helm/values-secrets.yaml`

**Files:**
- Create: `helm/values-secrets.yaml` (gitignored)

- [ ] **Step 1: Create `helm/values-secrets.yaml` with prod credentials**

```yaml
mongo:
  user: root
  password: "REPLACE_WITH_STRONG_PASSWORD"
  db: toolboxdb
  authSource: admin
```

Generate a strong password:
```bash
openssl rand -base64 32
```
Paste the output as the `password` value.

- [ ] **Step 2: Confirm the file is gitignored**

```bash
git check-ignore -v helm/values-secrets.yaml
```
Expected: `.gitignore:...:helm/values-secrets.yaml    helm/values-secrets.yaml`

---

## Task 7: Create `helm/templates/mongo-secret.yaml`

**Files:**
- Create: `helm/templates/mongo-secret.yaml`

- [ ] **Step 1: Create the Secret template**

```yaml
{{- if .Values.mongo.enabled }}
apiVersion: v1
kind: Secret
metadata:
  name: mongo-secret
  labels:
    {{- include "assist-frontend.labels" . | nindent 4 }}
type: Opaque
stringData:
  MONGO_USER: {{ .Values.mongo.user | quote }}
  MONGO_PASSWORD: {{ .Values.mongo.password | quote }}
  MONGO_DB: {{ .Values.mongo.db | quote }}
  MONGO_AUTH_SOURCE: {{ .Values.mongo.authSource | quote }}
{{- end }}
```

Note: `assist-frontend-portal` is the chart name from `helm/Chart.yaml`. Verify with:
```bash
grep "^name:" helm/Chart.yaml
```

- [ ] **Step 2: Lint the Helm chart**

```bash
helm lint helm/ -f helm/values.yaml -f helm/values-secrets.yaml
```
Expected: `1 chart(s) linted, 0 chart(s) failed`

- [ ] **Step 3: Dry-run template render and inspect Secret**

```bash
helm template toolbox-ui helm/ -f helm/values.yaml -f helm/values-secrets.yaml | grep -A 15 "kind: Secret" | grep -A 10 "name: mongo-secret"
```
Expected: Secret with `MONGO_USER`, `MONGO_PASSWORD`, `MONGO_DB`, `MONGO_AUTH_SOURCE` keys.

- [ ] **Step 4: Commit**

```bash
git add helm/templates/mongo-secret.yaml
git commit -m "feat: add mongo-secret helm template"
```

---

## Task 8: Create `helm/templates/mongo-storageclass.yaml`

**Files:**
- Create: `helm/templates/mongo-storageclass.yaml`

- [ ] **Step 1: Create the StorageClass template**

```yaml
{{- if and .Values.mongo.enabled .Values.mongo.persistence.enabled }}
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: {{ .Values.mongo.persistence.storageClass }}
provisioner: disk.csi.azure.com
parameters:
  skuName: Premium_LRS
reclaimPolicy: Retain
volumeBindingMode: WaitForFirstConsumer
allowVolumeExpansion: true
{{- end }}
```

- [ ] **Step 2: Lint the Helm chart**

```bash
helm lint helm/ -f helm/values.yaml -f helm/values-secrets.yaml
```
Expected: `1 chart(s) linted, 0 chart(s) failed`

- [ ] **Step 3: Dry-run render and inspect StorageClass**

```bash
helm template toolbox-ui helm/ -f helm/values.yaml -f helm/values-secrets.yaml | grep -A 10 "kind: StorageClass"
```
Expected: StorageClass named `toolbox-mongo-managed-retain` with `disk.csi.azure.com` provisioner.

- [ ] **Step 4: Commit**

```bash
git add helm/templates/mongo-storageclass.yaml
git commit -m "feat: add mongo-storageclass helm template"
```

---

## Task 9: Create `helm/templates/mongo-statefulset.yaml`

**Files:**
- Create: `helm/templates/mongo-statefulset.yaml`

- [ ] **Step 1: Create the StatefulSet template**

```yaml
{{- if .Values.mongo.enabled }}
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: mongo
  labels:
    {{- include "assist-frontend.labels" . | nindent 4 }}
spec:
  serviceName: mongo
  replicas: 1
  selector:
    matchLabels:
      app: mongo
  template:
    metadata:
      labels:
        app: mongo
    spec:
      containers:
        - name: mongo
          image: "{{ .Values.mongo.image.repository }}:{{ .Values.mongo.image.tag }}"
          imagePullPolicy: {{ .Values.mongo.image.pullPolicy }}
          args:
            - "--auth"
          ports:
            - containerPort: 27017
              name: mongo
          env:
            - name: MONGO_INITDB_ROOT_USERNAME
              valueFrom:
                secretKeyRef:
                  name: {{ .Values.mongo.credentialsSecretName }}
                  key: MONGO_USER
            - name: MONGO_INITDB_ROOT_PASSWORD
              valueFrom:
                secretKeyRef:
                  name: {{ .Values.mongo.credentialsSecretName }}
                  key: MONGO_PASSWORD
            - name: MONGO_INITDB_DATABASE
              valueFrom:
                secretKeyRef:
                  name: {{ .Values.mongo.credentialsSecretName }}
                  key: MONGO_DB
          volumeMounts:
            - name: mongo-data
              mountPath: /data/db
  volumeClaimTemplates:
    - metadata:
        name: mongo-data
        annotations:
          "helm.sh/resource-policy": keep
      spec:
        accessModes: ["ReadWriteOnce"]
        storageClassName: {{ .Values.mongo.persistence.storageClass | quote }}
        resources:
          requests:
            storage: {{ .Values.mongo.persistence.size }}
{{- end }}
```

- [ ] **Step 2: Lint the Helm chart**

```bash
helm lint helm/ -f helm/values.yaml -f helm/values-secrets.yaml
```
Expected: `1 chart(s) linted, 0 chart(s) failed`

- [ ] **Step 3: Dry-run render and inspect StatefulSet**

```bash
helm template toolbox-ui helm/ -f helm/values.yaml -f helm/values-secrets.yaml | grep -A 50 "kind: StatefulSet"
```
Expected: StatefulSet with `mongo:7` image, `--auth` arg, secret refs, 20Gi PVC.

- [ ] **Step 4: Commit**

```bash
git add helm/templates/mongo-statefulset.yaml
git commit -m "feat: add mongo-statefulset helm template"
```

---

## Task 10: Create `helm/templates/mongo-service.yaml`

**Files:**
- Create: `helm/templates/mongo-service.yaml`

- [ ] **Step 1: Create the Service template**

```yaml
{{- if .Values.mongo.enabled }}
apiVersion: v1
kind: Service
metadata:
  name: mongo
  labels:
    {{- include "assist-frontend.labels" . | nindent 4 }}
spec:
  clusterIP: None
  selector:
    app: mongo
  ports:
    - name: mongo
      port: {{ .Values.mongo.service.port }}
      targetPort: 27017
{{- end }}
```

Note: `clusterIP: None` creates a headless Service, which is required for StatefulSets so each pod gets stable DNS (`mongo-0.mongo`).

- [ ] **Step 2: Full Helm lint**

```bash
helm lint helm/ -f helm/values.yaml -f helm/values-secrets.yaml
```
Expected: `1 chart(s) linted, 0 chart(s) failed`

- [ ] **Step 3: Full dry-run render — inspect all MongoDB resources**

```bash
helm template toolbox-ui helm/ -f helm/values.yaml -f helm/values-secrets.yaml | grep "^kind:"
```
Expected output includes:
```
kind: StorageClass
kind: Secret
kind: StatefulSet
kind: Service        # mongo (headless)
kind: Deployment     # frontend
kind: Service        # frontend
kind: Ingress
```

- [ ] **Step 4: Commit**

```bash
git add helm/templates/mongo-service.yaml
git commit -m "feat: add mongo-service helm template"
```

---

## Task 11: Final verification

- [ ] **Step 1: Full end-to-end docker-compose smoke test**

```bash
docker compose up -d
docker compose ps
```
Expected: Both `frontend` (port 3000) and `mongo` (port 27017) show as `running`.

- [ ] **Step 2: Verify MongoDB connectivity from within the network**

```bash
docker compose exec mongo mongosh \
  -u root \
  -p changeme_local \
  --authenticationDatabase admin \
  --eval "db.runCommand({ping:1})" \
  --quiet
```
Expected: `{ ok: 1 }`

- [ ] **Step 3: Verify volume persistence across restart**

```bash
docker compose restart mongo
docker compose exec mongo mongosh \
  -u root \
  -p changeme_local \
  --authenticationDatabase admin \
  --eval "db.runCommand({ping:1})" \
  --quiet
```
Expected: `{ ok: 1 }` — data volume survives restart.

- [ ] **Step 4: Tear down**

```bash
docker compose down
```

Note: `docker compose down` removes containers but keeps the `mongo_data` volume. To also remove the volume: `docker compose down -v`.

- [ ] **Step 5: Final Helm template render with all resources**

```bash
helm template toolbox-ui helm/ -f helm/values.yaml -f helm/values-secrets.yaml > /tmp/toolbox-ui-rendered.yaml
cat /tmp/toolbox-ui-rendered.yaml
```
Review output — confirm all MongoDB resources are present and correct.

- [ ] **Step 6: Final commit**

```bash
git add -A
git status  # confirm only expected files staged
git commit -m "feat: MongoDB infrastructure setup complete (docker + helm)"
```
