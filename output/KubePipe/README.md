# KubePipe

**University of Innsbruck**

[![License](https://img.shields.io/badge/license-TBD-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)

> Pipeline orchestration platform bridging Kubeflow Pipelines and Argo Workflows with GDPR compliance and sustainability awareness.

![KubePipe Dashboard](docs/images/dashboard.png)

## Features

| Category | Capabilities |
|----------|-------------|
| **Orchestration** | Kubeflow Pipelines, Argo Workflows, Automatic YAML↔Python conversion |
| **Compliance** | GDPR privacy assessment, PII anonymization, Data minimization |
| **Sustainability** | Carbon footprint tracking, Energy consumption monitoring, Carbon-aware scheduling |
| **Runtime Adaptation** | Time-shifting, Region-shifting, Dynamic resource scaling, GDPR injection |
| **Interface** | REST API, CLI, React Web UI, Real-time monitoring |

## Quick Start

### Prerequisites

- Python 3.10+ with [uv](https://github.com/astral-sh/uv)
- Node.js 18+ (for Web UI)
- Docker & Minikube (for Kubernetes)

### Installation

```bash
git clone https://github.com/DATAPACT/Kubepipe.git
cd Kubepipe && uv sync
```

### Start All Services

```bash
bash scripts/start_all.sh
```

| Service | URL |
|---------|-----|
| Backend API | http://127.0.0.1:8001 |
| Web UI | http://localhost:3000 |
| Argo Server | https://localhost:2746 |
| MinIO Console | http://localhost:9001 |

## Usage

### Argo Workflows

```bash
kubepipe argo-deploy examples/argo/hello-world.yaml   # Deploy
kubepipe argo-status <workflow-name>                   # Status
kubepipe argo-list                                     # List all
kubepipe argo-delete <workflow-name>                   # Delete
```

### Kubeflow Pipelines

```bash
# Port-forward KFP API
kubectl -n kubeflow port-forward svc/ml-pipeline 8888:8888

# Execute via API
curl -X POST http://127.0.0.1:8001/api/v1/execute \
  -H 'Content-Type: application/json' \
  -d '{"pipeline_id":"demo","environment":"dev","parameters":{}}'
```

### Argo → Kubeflow Conversion

```bash
uv run python demo_converter.py
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/execute` | POST | Execute KFP pipeline |
| `/api/v1/runs/{id}` | GET | Get run status |
| `/api/v1/argo/deploy` | POST | Deploy Argo workflow |
| `/api/v1/argo/workflows` | GET | List workflows |
| `/api/v1/workflows/validate` | POST | Validate workflow YAML |
| `/api/v1/workflows/dry-run` | POST | Dry-run with resource estimates |
| `/api/v1/workflows/compliance-check` | POST | GDPR compliance analysis |
| `/api/v1/adaptation/carbon-forecast` | GET | Carbon intensity forecast |
| `/api/v1/adaptation/analyze` | POST | Analyze adaptation opportunities |
| `/api/v1/adaptation/apply` | POST | Apply runtime adaptations |
| `/api/v1/metrics/status` | GET | Check metrics-server status |
| `/api/v1/metrics/cluster` | GET | Real-time cluster metrics |

## Accurate Measurements with Metrics-Server

For accurate energy and carbon measurements, install the Kubernetes metrics-server:

```bash
kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml
```

| Metric Source | Accuracy | Description |
|---------------|----------|-------------|
| **With metrics-server** | High | Real-time CPU/memory usage from pods |
| **Without metrics-server** | Estimated | Based on resource requests/limits |

## Configuration

```yaml
# kubepipe.yaml
execution:
  mode: "mock"  # mock | kfp
  kfp_host: "http://127.0.0.1:8888"
```

```bash
# Environment variables
export KUBEPIPE_EXECUTION_MODE=kfp
export KUBEPIPE_KFP_HOST=http://127.0.0.1:8888
```

## Project Structure

```
kubepipe/
├── api/           # FastAPI server
├── core/          # Compiler, executors, converters
└── config.py      # Configuration
examples/          # Sample pipelines
scripts/           # Helper scripts
ui/                # React web interface
```

## Documentation

- [UI Guide](docs/UI_GUIDE.md)
- [Runtime Adaptation](docs/RUNTIME_ADAPTATION.md)
- [Service Monitoring](docs/SERVICE_MONITORING.md)
- [Validation & Compliance](docs/VALIDATION_AND_COMPLIANCE.md)
- [Troubleshooting](docs/TROUBLESHOOTING.md)

## Contact

**University of Innsbruck**
- 📧 rajashekar.kolichala@uibk.ac.at
- 📧 radu.prodan@uibk.ac.at

## Acknowledgments

Funded by Horizon Europe (grant 101189771, DataPACT)

---
*Last Updated: February 2026*
