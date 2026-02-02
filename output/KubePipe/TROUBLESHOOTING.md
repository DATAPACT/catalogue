# KubePipe Troubleshooting Guide

## Common Issues and Solutions

### 1. Pipeline Failures: MinIO Connection Refused

**Symptoms:**
- Pipelines fail after ~20 seconds
- Error: `dial tcp 10.109.7.40:9000: connect: connection refused`
- Error: `failed to put file: Get "http://minio-service.kubeflow:9000/mlpipeline/?location="`
- MinIO pod in `ImagePullBackOff` or `CrashLoopBackOff` state

**Root Cause:**
Platform-agnostic KFP configuration uses an unavailable MinIO image: `gcr.io/ml-pipeline/minio:RELEASE.2019-08-14T20-37-41Z-license-compliance`

**Solution:**

1. **Check MinIO status:**
```bash
kubectl get pods -n kubeflow | grep minio
```

2. **If ImagePullBackOff, update the image:**
```bash
kubectl set image deployment/minio -n kubeflow minio=minio/minio:RELEASE.2021-06-17T00-10-46Z
```

3. **If CrashLoopBackOff with permission errors, add init container:**
```bash
kubectl patch deployment minio -n kubeflow --type='json' -p='[
  {"op": "add", "path": "/spec/template/spec/initContainers", "value": [
    {
      "name": "fix-permissions",
      "image": "busybox",
      "command": ["sh", "-c", "chmod -R 777 /data || true; chown -R 1000:1000 /data || true"],
      "volumeMounts": [{"name": "data", "mountPath": "/data"}],
      "securityContext": {"runAsUser": 0}
    }
  ]}
]'
```

4. **Set security context:**
```bash
kubectl patch deployment minio -n kubeflow --type='json' -p='[
  {"op": "add", "path": "/spec/template/spec/securityContext", "value": {"runAsUser": 0, "runAsGroup": 0, "fsGroup": 0}}
]'
```

5. **Wait for MinIO to restart:**
```bash
kubectl get pods -n kubeflow -w | grep minio
```

**Prevention:**
The updated `scripts/start_all.sh` now automatically detects and fixes MinIO issues on startup.

---

### 2. MLMD Error: Cannot Get MLMD Objects

**Symptoms:**
- Error: "Cannot get MLMD objects from Metadata store"
- `metadata-envoy-deployment` scaled to 0/0 or crashing
- Pod logs show: "Invalid path: /etc/envoy.yaml"

**Root Cause:**
Missing or incorrect Envoy configuration in metadata-envoy deployment.

**Solution:**

1. **Apply platform-agnostic KFP configuration:**
```bash
export PIPELINE_VERSION=2.14.3
kubectl apply -k "github.com/kubeflow/pipelines/manifests/kustomize/env/platform-agnostic?ref=${PIPELINE_VERSION}"
```

2. **Verify metadata services are running:**
```bash
kubectl get pods -n kubeflow | grep metadata
```

Expected output:
```
metadata-envoy-deployment-xxx        1/1   Running
metadata-grpc-deployment-xxx         1/1   Running
metadata-writer-xxx                  1/1   Running
```

---

### 3. KFP Core Services Not Ready

**Symptoms:**
- `ml-pipeline` pod in CrashLoopBackOff
- `ml-pipeline-scheduledworkflow` restarting frequently
- Pipelines fail to submit

**Diagnosis:**
```bash
# Check all KFP pods
kubectl get pods -n kubeflow

# Check specific service logs
kubectl logs -n kubeflow deployment/ml-pipeline --tail=50
kubectl logs -n kubeflow deployment/ml-pipeline-scheduledworkflow --tail=50
```

**Common Causes:**
1. MinIO not accessible (see issue #1)
2. MySQL database issues
3. Resource constraints

**Solution:**
```bash
# Restart KFP deployments
kubectl rollout restart deployment/ml-pipeline -n kubeflow
kubectl rollout restart deployment/ml-pipeline-scheduledworkflow -n kubeflow

# Check MySQL
kubectl logs -n kubeflow deployment/mysql --tail=50
```

---

### 4. Port Conflicts

**Symptoms:**
- Backend or UI fails to start
- Error: "Port already in use"

**Solution:**
The `start_all.sh` script automatically finds free ports. To manually specify:

```bash
# Use custom ports
KUBEPIPE_API_PORT=8001 KUBEPIPE_UI_PORT=3001 bash scripts/start_all.sh
```

---

### 5. Node.js Version Issues

**Symptoms:**
- UI fails to build or start
- npm errors about unsupported Node.js version

**Solution:**
```bash
# Check Node.js version
node --version  # Must be 18+

# If using nvm
nvm install 18
nvm use 18

# Reinstall UI dependencies
cd ui
rm -rf node_modules package-lock.json
npm install
```

See `NODEJS_UPGRADE.md` for detailed instructions.

---

## Quick Health Check Commands

```bash
# Overall system health
curl http://127.0.0.1:8001/api/v1/health | python3 -m json.tool

# KFP pods status
kubectl get pods -n kubeflow | grep -E '(ml-pipeline|metadata|minio|mysql)'

# MinIO logs
kubectl logs -n kubeflow deployment/minio --tail=30

# Backend logs
tail -f /tmp/kubepipe-api.log

# UI logs
tail -f /tmp/kubepipe-ui.log

# Recent workflows
kubectl get workflow -n kubeflow --sort-by=.metadata.creationTimestamp | tail -10
```

---

## Automated Startup Checks

The enhanced `scripts/start_all.sh` now includes:

1. ✅ **MinIO Health Check**: Automatically detects ImagePullBackOff and permission issues
2. ✅ **Auto-Fix**: Applies known fixes for MinIO deployment
3. ✅ **KFP Validation**: Checks all core KFP services are ready
4. ✅ **Port Management**: Automatically finds free ports
5. ✅ **Service Status**: Displays detailed health of all components

Run with:
```bash
bash scripts/start_all.sh
```

---

## Getting Help

If issues persist:

1. Check the full logs:
   ```bash
   # KFP logs
   kubectl logs -n kubeflow deployment/ml-pipeline --tail=100
   
   # MinIO logs
   kubectl logs -n kubeflow deployment/minio --tail=100
   
   # Recent pod events
   kubectl get events -n kubeflow --sort-by='.lastTimestamp' | tail -20
   ```

2. Verify Kubernetes resources:
   ```bash
   kubectl get all -n kubeflow
   ```

3. Check disk space and resources:
   ```bash
   df -h
   kubectl top nodes
   kubectl top pods -n kubeflow
   ```

---

## Known Limitations

- **MinIO Image**: The official KFP platform-agnostic config uses an old MinIO image. This is automatically fixed by the startup script.
- **Metrics Server**: Not enabled by default in Minikube. Enable with: `minikube addons enable metrics-server`
- **Resource Limits**: ML workloads may require more than default Minikube resources (4 CPUs, 8GB RAM)

---

## Version Information

- **KFP**: v2.14.3 (platform-agnostic)
- **MinIO**: RELEASE.2021-06-17T00-10-46Z (fixed version)
- **Argo Workflows**: v3.5.0
- **Node.js**: 18+ required
- **Python**: 3.12

Last Updated: January 29, 2026
