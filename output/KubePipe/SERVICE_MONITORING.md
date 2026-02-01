# Service Status Monitoring

KubePipe UI includes comprehensive real-time service monitoring that automatically checks the health of all connected services.

## Features

### Automatic Health Checks
- **Auto-refresh**: Services are checked every 10 seconds
- **Real-time status**: Immediate feedback when services go up or down
- **Manual refresh**: Click the refresh button to check immediately

### Monitored Services

1. **FastAPI Backend** (`http://127.0.0.1:8000`)
   - API server availability
   - Endpoint accessibility

2. **Kubeflow Pipelines**
   - KFP server connection
   - Experiment listing capability
   - Endpoint: Configured via `KUBEPIPE_KFP_HOST`

3. **Kubernetes Cluster**
   - Cluster connectivity via kubectl
   - Namespace access
   - API server availability

4. **Argo Workflows**
   - Argo namespace detection
   - Workflow deployment capability
   - K8s integration status

5. **Grafana Monitoring** (Optional)
   - Monitoring system configuration
   - Dashboard availability

## Service Status Levels

### 🟢 Healthy
- Service is fully operational
- All checks passed
- Normal operation

### 🟡 Warning/Degraded
- Service has minor issues
- Some features may be limited
- Non-critical problems detected

### 🔴 Error
- Service is unavailable
- Critical functionality impacted
- Immediate attention required

### ⚪ Not Configured
- Service is optional and not set up
- No action required unless needed

## Dashboard Integration

The Service Status component is displayed prominently on the dashboard:

```jsx
<ServiceStatus autoRefresh={true} refreshInterval={10000} />
```

### Component Props

- `autoRefresh` (boolean): Enable automatic health checks
- `refreshInterval` (number): Milliseconds between checks (default: 10000 = 10 seconds)

## API Endpoint

### GET `/api/v1/health`

Returns comprehensive health status for all services.

**Response Example:**
```json
{
  "timestamp": "2026-01-21T16:10:30.123456Z",
  "overall_status": "healthy",
  "services": {
    "api": {
      "name": "FastAPI Backend",
      "status": "healthy",
      "message": "API server is running",
      "endpoint": "http://127.0.0.1:8000"
    },
    "kubeflow": {
      "name": "Kubeflow Pipelines",
      "status": "healthy",
      "message": "Successfully connected to KFP",
      "endpoint": "http://localhost:8080"
    },
    "kubernetes": {
      "name": "Kubernetes Cluster",
      "status": "healthy",
      "message": "Connected to Kubernetes cluster",
      "endpoint": "kubectl configured"
    },
    "argo": {
      "name": "Argo Workflows",
      "status": "healthy",
      "message": "Argo namespace detected",
      "endpoint": "namespace: argo"
    },
    "monitoring": {
      "name": "Grafana Monitoring",
      "status": "not_configured",
      "message": "Optional monitoring not configured",
      "endpoint": null
    }
  }
}
```

### Overall Status Logic

- **healthy**: All critical services operational
- **degraded**: One or more services have warnings or are not configured
- **error**: Critical services (API, Kubernetes, or KFP) are down

## Troubleshooting

### Backend Not Connecting

**Error**: `Cannot connect to backend server`

**Solution**:
```bash
cd /home/shekar/Documents/Kubepipe
uv run uvicorn kubepipe.api.main:app --reload --host 127.0.0.1 --port 8000
```

### Kubeflow Not Configured

**Error**: `KFP host not configured`

**Solution**:
```bash
# Set environment variable
export KUBEPIPE_KFP_HOST="http://localhost:8080"

# Or configure in kubepipe.yaml
execution:
  mode: kfp
  kfp_host: "http://localhost:8080"
```

### Kubernetes Connection Failed

**Error**: `Cannot connect: ...`

**Solution**:
```bash
# Verify kubectl is configured
kubectl cluster-info

# Check kubeconfig
kubectl config view

# Verify cluster access
kubectl get namespaces
```

### Argo Namespace Not Found

**Warning**: `Argo namespace not found`

**Solution**:
```bash
# Create argo namespace
kubectl create namespace argo

# Or install Argo Workflows
kubectl apply -n argo -f https://github.com/argoproj/argo-workflows/releases/download/v3.5.0/install.yaml
```

## Using the Service Status Component

### In Your Own Pages

```jsx
import ServiceStatus from '../components/ServiceStatus'

function MyPage() {
  return (
    <div>
      <h1>My Custom Page</h1>
      
      {/* With custom settings */}
      <ServiceStatus 
        autoRefresh={true} 
        refreshInterval={5000}  // 5 seconds
      />
      
      {/* Manual refresh only */}
      <ServiceStatus autoRefresh={false} />
    </div>
  )
}
```

## Benefits

1. **Proactive Monitoring**: Detect issues before they impact workflows
2. **Quick Diagnosis**: Immediately see which service is causing problems
3. **Reduced Downtime**: Auto-refresh catches problems within 10 seconds
4. **Better UX**: Users know exactly what's working and what needs attention
5. **Operational Visibility**: Clear view of the entire system state

## Future Enhancements

- Historical uptime tracking
- Service response time metrics
- Alert notifications when services go down
- Integration with PagerDuty/Slack
- Per-service logs viewer
- Custom health check configurations
