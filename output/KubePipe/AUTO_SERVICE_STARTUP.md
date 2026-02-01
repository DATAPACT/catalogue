# Automatic Service Startup

KubePipe now features automatic detection and startup of required Kubernetes services directly from the web UI.

## Overview

When you open the KubePipe dashboard, it automatically checks the health of all services. If Kubernetes services (minikube, Kubeflow Pipelines, or Argo Workflows) are not running, you'll see a **"Start Services"** button that will:

1. Start minikube cluster
2. Install Kubeflow Pipelines
3. Install Argo Workflows
4. Configure port forwarding
5. Set up environment variables

All with a single click!

## How It Works

### 1. Automatic Detection

The Service Status panel checks:
- ✅ FastAPI Backend
- 🔍 Kubeflow Pipelines connection
- 🔍 Kubernetes cluster
- 🔍 Argo Workflows
- ⚙️ Grafana Monitoring (optional)

### 2. Smart Button Display

The "Start Services" button appears when:
- Kubernetes cluster is not accessible
- Kubeflow Pipelines is not configured
- Argo Workflows is not accessible

### 3. One-Click Setup

Click the button and the system will:
- Run the complete setup script
- Install all required components
- Configure networking
- Set up environment variables

**⏱️ Duration**: 5-10 minutes for first-time setup

### 4. Auto-Refresh

The dashboard automatically:
- Checks service health every 10 seconds
- Updates status when services become available
- Shows progress notifications

## Using the Feature

### Via Web UI (Recommended)

1. **Open Dashboard**: http://localhost:3000
2. **Check Service Status**: View the Service Status panel
3. **Click "Start Services"**: If services are down
4. **Wait**: 5-10 minutes for first-time setup
5. **Auto-Refresh**: Dashboard updates automatically

### Via Command Line (Alternative)

```bash
# Start all services automatically
cd /home/shekar/Documents/Kubepipe
bash scripts/start_all.sh

# Or setup Kubernetes only
bash scripts/setup_kubernetes.sh
```

### Disable Auto-Start

If you don't want automatic Kubernetes startup:

```bash
AUTO_START_K8S=false bash scripts/start_all.sh
```

## What Gets Installed

### Minikube Configuration
- **CPUs**: 4
- **Memory**: 8GB
- **Disk**: 40GB
- **Driver**: Docker

### Kubeflow Pipelines v2.0.5
- Namespace: `kubeflow`
- UI Port: `8080`
- Endpoint: `http://localhost:8080`

### Argo Workflows v3.5.0
- Namespace: `argo`
- UI Port: `2746`
- Endpoint: `https://localhost:2746`

## Environment Configuration

After setup, the following files are created/updated:

### ~/.kubepipe_env
```bash
export KUBEPIPE_KFP_HOST="http://localhost:8080"
export KUBEPIPE_EXECUTION_MODE="kfp"
export KUBECONFIG="$HOME/.kube/config"
```

**Load in new terminals**:
```bash
source ~/.kubepipe_env
```

### kubepipe.yaml
```yaml
execution:
  mode: kfp
  kfp_host: "http://localhost:8080"

monitoring:
  enabled: true
  grafana_url: ""
  grafana_token: ""

compliance:
  gdpr_enabled: true
  anonymization: true

sustainability:
  tracking_enabled: true
  codecarbon_enabled: true
```

## API Endpoint

### POST `/api/v1/services/start`

Start Kubernetes services programmatically.

**Request Body**:
```json
{
  "auto_install": true,
  "start_minikube": true,
  "install_kubeflow": true,
  "install_argo": true
}
```

**Response**:
```json
{
  "status": "started",
  "message": "Kubernetes services are being started...",
  "services_started": ["minikube", "kubeflow-pipelines", "argo-workflows"],
  "detail": "Process started successfully..."
}
```

## Progress Monitoring

### During Setup

Watch the terminal output for:
```
🚀 Starting Minikube...
✅ Minikube started
🌿 Installing Argo Workflows...
✅ Argo Workflows installed
🔄 Installing Kubeflow Pipelines...
✅ Kubeflow Pipelines installed
🔌 Setting up port forwarding...
✅ Port forwarding configured
```

### In the Dashboard

Status updates appear automatically:
- 🔵 Blue: Starting/In Progress
- 🟢 Green: Healthy
- 🟡 Yellow: Warning/Degraded
- 🔴 Red: Error

## Troubleshooting

### Services Won't Start

**Check Prerequisites**:
```bash
# Docker must be running
docker ps

# Minikube must be installed
which minikube

# kubectl must be installed
which kubectl
```

**Check Logs**:
```bash
# Minikube status
minikube status

# Port forwarding logs
tail -f /tmp/kfp-port-forward.log
tail -f /tmp/argo-port-forward.log

# Pod status
kubectl get pods -n kubeflow
kubectl get pods -n argo
```

### Port Already in Use

**Kill existing port forwards**:
```bash
pkill -f "kubectl port-forward"
```

**Restart port forwarding**:
```bash
bash scripts/setup_kubernetes.sh
```

### Services Show as Error

**Verify pods are running**:
```bash
# Check Kubeflow
kubectl get pods -n kubeflow
kubectl wait --for=condition=available --timeout=600s deployment/ml-pipeline -n kubeflow

# Check Argo
kubectl get pods -n argo
kubectl wait --for=condition=available --timeout=300s deployment/argo-server -n argo
```

### Minikube Won't Start

**Check resources**:
```bash
# Stop and restart with more resources
minikube stop
minikube delete
minikube start --cpus=4 --memory=8192 --disk-size=40g
```

**Check Docker**:
```bash
# Restart Docker if needed
sudo systemctl restart docker
```

## Manual Setup (If Auto-Start Fails)

### 1. Start Minikube
```bash
minikube start --cpus=4 --memory=8192 --disk-size=40g --driver=docker
```

### 2. Install Argo Workflows
```bash
kubectl create namespace argo
kubectl apply -n argo -f https://github.com/argoproj/argo-workflows/releases/download/v3.5.0/install.yaml
```

### 3. Install Kubeflow Pipelines
```bash
kubectl create namespace kubeflow
export PIPELINE_VERSION=2.0.5
kubectl apply -k "github.com/kubeflow/pipelines/manifests/kustomize/cluster-scoped-resources?ref=$PIPELINE_VERSION"
kubectl wait --for condition=established --timeout=60s crd/applications.app.k8s.io
kubectl apply -k "github.com/kubeflow/pipelines/manifests/kustomize/env/platform-agnostic?ref=$PIPELINE_VERSION"
```

### 4. Port Forwarding
```bash
# KFP
kubectl port-forward -n kubeflow svc/ml-pipeline-ui 8080:80 &

# Argo
kubectl port-forward -n argo svc/argo-server 2746:2746 &
```

### 5. Configure Environment
```bash
echo 'export KUBEPIPE_KFP_HOST="http://localhost:8080"' >> ~/.bashrc
source ~/.bashrc
```

## Benefits

1. **One-Click Setup** - No manual Kubernetes configuration needed
2. **Automatic Detection** - System knows what's missing
3. **Progress Tracking** - Real-time status updates
4. **Persistent Configuration** - Settings saved for future sessions
5. **Error Recovery** - Clear messages when something fails

## Next Steps

After services start successfully:

1. ✅ All service status indicators turn green
2. ✅ Deploy your first Argo workflow
3. ✅ Execute Kubeflow Pipeline
4. ✅ View sustainability metrics
5. ✅ Access embedded Kubeflow UI

## Related Documentation

- [Service Monitoring Guide](SERVICE_MONITORING.md)
- [Kubernetes Setup Script](../scripts/setup_kubernetes.sh)
- [Startup Script](../scripts/start_all.sh)
- [UI Guide](UI_GUIDE.md)
