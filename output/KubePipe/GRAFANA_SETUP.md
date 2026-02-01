# Grafana Monitoring Configuration

Complete guide to setting up Grafana monitoring for KubePipe pipelines, sustainability metrics, and Kubernetes resources.

## Quick Setup

### Option 1: Automatic (Recommended)

```bash
cd /home/shekar/Documents/Kubepipe
bash scripts/setup_grafana.sh
```

This will:
- ✅ Install Prometheus for metrics collection
- ✅ Install Grafana with pre-configured dashboards
- ✅ Setup port forwarding (Grafana: 3001, Prometheus: 9090)
- ✅ Generate API token
- ✅ Update environment variables
- ✅ Configure KubePipe integration

**Duration**: 2-3 minutes

### Option 2: During Kubernetes Setup

```bash
bash scripts/setup_kubernetes.sh
# Answer 'y' when prompted for Grafana installation
```

## What Gets Installed

### Prometheus
- **Purpose**: Metrics collection and storage
- **Namespace**: `monitoring`
- **Port**: 9090
- **URL**: http://localhost:9090

### Grafana
- **Purpose**: Metrics visualization and dashboards
- **Namespace**: `monitoring`
- **Port**: 3001 (to avoid conflict with UI on 3000)
- **URL**: http://localhost:3001
- **Default Login**: admin / admin

### Pre-configured Dashboards

1. **KubePipe Overview**
   - Pipeline run metrics
   - Success rate trends
   - Active pipelines gauge
   - Resource usage graphs

2. **Sustainability Metrics**
   - CO₂ emissions tracking
   - Energy consumption (kWh)
   - Carbon intensity
   - GPU/CPU usage

3. **Kubernetes Resources**
   - Pod status across namespaces
   - Memory and CPU utilization
   - Resource quotas

## Access Information

### Grafana Web UI
```
URL: http://localhost:3001
Username: admin
Password: admin
```

### API Access
```bash
# Health check
curl http://localhost:3001/api/health

# With API token
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost:3001/api/dashboards/home
```

### Environment Variables

After setup, these are configured in `~/.kubepipe_env`:

```bash
export KUBEPIPE_GRAFANA_URL="http://localhost:3001"
export KUBEPIPE_GRAFANA_TOKEN="<generated-token>"
```

**Load in new terminals**:
```bash
source ~/.kubepipe_env
```

## KubePipe Integration

### Dashboard Service Status

Once Grafana is installed, the KubePipe dashboard will show:

```
🟢 Grafana Monitoring - Healthy
   Grafana is accessible
   http://localhost:3001
```

### Programmatic Access

```python
from kubepipe.core.monitor import KubePipeMonitor

monitor = KubePipeMonitor(
    grafana_url="http://localhost:3001",
    grafana_token="your-token-here"
)

# Deploy dashboard
monitor.deploy_dashboard("MyPipeline")

# Get metrics
metrics = monitor.parse_metrics()
```

### API Endpoint

```bash
# Setup monitoring
curl -X POST http://127.0.0.1:8000/api/v1/monitor/setup \
  -H "Content-Type: application/json" \
  -d '{
    "grafana_url": "http://localhost:3001",
    "grafana_token": "your-token"
  }'
```

## Using the Dashboards

### 1. Access Grafana

Open browser: http://localhost:3001

### 2. Navigate to Dashboards

- Click "Dashboards" in left sidebar
- Expand "KubePipe" folder
- Select a dashboard

### 3. Available Dashboards

#### KubePipe Overview
Shows:
- Total pipeline runs over time
- Success rate percentage
- Currently active pipelines
- Resource usage trends

**Refresh**: Every 10 seconds

#### Sustainability Metrics
Shows:
- CO₂ emissions in kg over time
- Energy consumption in kWh
- Carbon intensity per region
- GPU and CPU utilization

**Refresh**: Every 30 seconds

**Time Range**: Last 24 hours

#### Kubernetes Resources
Shows:
- Pod status by namespace
- Resource distribution
- Memory usage trends
- CPU usage trends

**Refresh**: Every 10 seconds

### 4. Customize Dashboards

1. Click dashboard title
2. Select "Settings"
3. Edit panels, add queries
4. Save changes

## Metrics Configuration

### CodeCarbon Integration

KubePipe automatically sends sustainability metrics to Prometheus:

```python
# In your pipeline
from codecarbon import EmissionsTracker

tracker = EmissionsTracker()
tracker.start()

# ... your ML training code ...

emissions = tracker.stop()

# Metrics automatically exported to Prometheus
```

### Custom Metrics

Add your own metrics:

```python
from prometheus_client import Counter, Gauge

# Define metrics
pipeline_runs = Counter('kubepipe_pipeline_runs_total', 'Total pipeline runs')
active_jobs = Gauge('kubepipe_active_jobs', 'Currently active jobs')

# Use in code
pipeline_runs.inc()
active_jobs.set(5)
```

## Troubleshooting

### Grafana Not Accessible

**Check pod status**:
```bash
kubectl get pods -n monitoring
kubectl logs -n monitoring deployment/grafana
```

**Restart port forwarding**:
```bash
pkill -f "kubectl port-forward.*monitoring.*grafana"
kubectl port-forward -n monitoring svc/grafana 3001:3000 &
```

### Dashboards Not Showing Data

**Verify Prometheus is running**:
```bash
curl http://localhost:9090/-/healthy

# Check targets
curl http://localhost:9090/api/v1/targets
```

**Check Prometheus logs**:
```bash
kubectl logs -n monitoring deployment/prometheus
```

### API Token Not Working

**Generate new token**:
```bash
# Port forward if needed
kubectl port-forward -n monitoring svc/grafana 3001:3000 &

# Create token
curl -X POST \
  -H "Content-Type: application/json" \
  -d '{"name":"kubepipe-new","role":"Admin"}' \
  http://admin:admin@localhost:3001/api/auth/keys
```

**Update environment**:
```bash
echo 'export KUBEPIPE_GRAFANA_TOKEN="new-token-here"' >> ~/.kubepipe_env
source ~/.kubepipe_env
```

### Health Check Shows Error

**Check connectivity**:
```bash
# Test Grafana API
curl -v http://localhost:3001/api/health

# Test with auth
curl -H "Authorization: Bearer $KUBEPIPE_GRAFANA_TOKEN" \
  http://localhost:3001/api/health
```

**Restart KubePipe backend**:
```bash
pkill -f uvicorn
source ~/.kubepipe_env
cd ~/Documents/Kubepipe
uv run uvicorn kubepipe.api.main:app --reload --host 127.0.0.1 --port 8000
```

## Advanced Configuration

### Data Retention

Edit Prometheus config:

```bash
kubectl edit configmap prometheus-config -n monitoring

# Add under global:
  storage:
    tsdb:
      retention.time: 30d
      retention.size: 10GB
```

### Alert Rules

Create alerts for pipeline failures:

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: prometheus-alerts
  namespace: monitoring
data:
  alerts.yml: |
    groups:
    - name: kubepipe
      rules:
      - alert: PipelineFailure
        expr: kubepipe_pipeline_success_rate < 0.8
        for: 5m
        annotations:
          summary: "Pipeline success rate below 80%"
```

### External Grafana

To use existing Grafana instead of installing:

```bash
# Set environment variables
export KUBEPIPE_GRAFANA_URL="https://your-grafana.com"
export KUBEPIPE_GRAFANA_TOKEN="your-existing-token"

# Update kubepipe.yaml
monitoring:
  enabled: true
  grafana_url: "https://your-grafana.com"
  grafana_token: "your-existing-token"
```

## Metrics Reference

### Pipeline Metrics

| Metric | Type | Description |
|--------|------|-------------|
| `kubepipe_pipeline_runs_total` | Counter | Total number of pipeline executions |
| `kubepipe_pipeline_success_rate` | Gauge | Success rate (0-1) |
| `kubepipe_active_pipelines` | Gauge | Currently running pipelines |
| `kubepipe_pipeline_duration_seconds` | Histogram | Pipeline execution time |

### Sustainability Metrics

| Metric | Type | Description |
|--------|------|-------------|
| `codecarbon_emissions_kg` | Gauge | CO₂ emissions in kilograms |
| `codecarbon_energy_kwh` | Gauge | Energy consumption in kWh |
| `codecarbon_carbon_intensity` | Gauge | gCO₂/kWh |
| `kubepipe_gpu_usage_percent` | Gauge | GPU utilization |
| `kubepipe_cpu_usage_percent` | Gauge | CPU utilization |

### Kubernetes Metrics

| Metric | Type | Description |
|--------|------|-------------|
| `kube_pod_status_phase` | Gauge | Pod status (running/pending/failed) |
| `kube_deployment_replicas` | Gauge | Number of replicas |
| `container_memory_usage_bytes` | Gauge | Memory usage |
| `container_cpu_usage_seconds_total` | Counter | CPU usage |

## Uninstallation

### Remove Grafana Only

```bash
kubectl delete namespace monitoring
pkill -f "kubectl port-forward.*monitoring"
```

### Clean Environment

```bash
# Remove from ~/.kubepipe_env
sed -i '/KUBEPIPE_GRAFANA/d' ~/.kubepipe_env

# Remove from kubepipe.yaml
# Edit manually and remove grafana_url and grafana_token
```

## Resources

- **Grafana Docs**: https://grafana.com/docs/
- **Prometheus Docs**: https://prometheus.io/docs/
- **CodeCarbon**: https://codecarbon.io/
- **Kubernetes Metrics**: https://kubernetes.io/docs/tasks/debug/debug-cluster/resource-metrics-pipeline/

## Next Steps

After Grafana is configured:

1. ✅ Check dashboard - Grafana shows as 🟢 Healthy
2. ✅ Open Grafana UI - http://localhost:3001
3. ✅ View pre-configured dashboards
4. ✅ Run a pipeline and watch metrics update
5. ✅ Customize dashboards for your needs
6. ✅ Set up alerts for critical events
