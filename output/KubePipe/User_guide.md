# KubePipe User Guide

Welcome to the **KubePipe** User Guide! KubePipe is a unified pipeline orchestration platform that bridges Kubeflow Pipelines (KFP) and Argo Workflows. It gives you a single interface to deploy, manage, and monitor your Machine Learning pipelines while automatically handling GDPR compliance checks and providing comprehensive sustainability (carbon/energy) tracking.

This guide is tailored for end-users (Data Scientists, ML Engineers, MLOps Professionals) who want to streamline their pipeline operations through KubePipe.

---

## 1. Initial Setup and Configuration

Before using KubePipe, you need to ensure the system is running and pointing to the right environment.

### Starting the Platform
From the source directory of KubePipe, start the backend API and the Web UI by running:
```bash
bash scripts/start_all.sh
```
This typically starts:
- **Backend API**: `http://127.0.0.1:8001` (or `8000`)
- **Web UI**: `http://localhost:3000`

### Execution Modes
KubePipe's behavior is governed by the `kubepipe.yaml` configuration file at the root of the project. Pay attention to the `execution.mode` setting:
- **`mock` mode**: Simulates API responses without talking to a real Kubernetes backend. Perfect for testing, local UI exploration, or development.
- **`kfp` mode**: Executes pipelines on a real Kubeflow Pipelines instance. 
  - *Note: To use this mode, you must have KFP running on your cluster and port-forwarded locally (e.g., `kubectl -n kubeflow port-forward svc/ml-pipeline 8888:8888`).*

---

## 2. Using the Command Line Interface (CLI)

KubePipe offers a CLI toolkit to manage workflows directly from your terminal.

### Managing Argo Workflows
You can deploy and manage Argo Workflow YAML definitions via the CLI.

- **Deploy a Workflow**:
  ```bash
  kubepipe argo-deploy path/to/my-workflow.yaml --namespace default
  ```
- **Check Workflow Status**:
  ```bash
  kubepipe argo-status <workflow-name> --namespace default
  ```
- **List All Active Workflows**:
  ```bash
  kubepipe argo-list --namespace default
  ```
- **Delete a Workflow**:
  ```bash
  kubepipe argo-delete <workflow-name> --namespace default
  ```

### Converting Argo Workflows to Kubeflow Pipelines
If you have a workflow written for Argo but want to run it on Kubeflow using Python DSL, you can convert it automatically:
```bash
kubepipe argo-to-kfp path/to/argo-workflow.yaml -o custom_output.py --compile
```
This generates standard KFP python code out of an Argo YAML and can compile it directly into a KFP-ready package (`--compile`).

### Local Simulation (Dry-Run)
To simulate pipeline execution locally and view logs and potential deployment adaptations, use the dry-run CLI tool:
```bash
kubepipe simulate-local
```

---

## 3. Using the Web Interface (UI)

For visual management, navigate to **http://localhost:3000** in your web browser. 

### Dashboard
The default dashboard gives you a live overview of your system's health, total pipeline runs, active workflows, and a recent activity stream.

### Kubeflow Pipelines Management 
Go to the **Pipelines** tab to manage KFP components:
1. **Execute**: Launch a pipeline by feeding it runtime parameters.
2. **Simulate**: Do a test run (dry-run) to estimate resource usages without scheduling pods.
3. **Compile**: Convert pipeline configurations into deployable YAML artifacts.

### Argo Workflows Deployment
The **Argo Workflows** page allows you to paste or load Argo YAML definitions directly into the browser and deploy them. You can monitor the real-time node progression of the workflow and delete workflows once finished.

### Pipeline Runs & Embedded UI
The **Runs** tab provides the execution history of all your deployed ML pipelines. From this page, you can review start/end timestamps and final statuses. 
To investigate inner step logs or node graphs, select the **View in Kubeflow UI** to interact natively with your embedded Kubeflow Interface.

### Sustainability & Carbon Tracking
A core feature of KubePipe is tracking environmental impact. On the **Sustainability** tab, view automatically collected telemetry per pipeline run:
- **CO₂ Emissions Tracking** (kg of CO₂)
- **Energy Consumption** (kWh)
KubePipe uses Kubernetes metrics and local carbon intensity forecasting to visualize how computationally clean your ML workloads are.

### GDPR Compliance Engine
KubePipe validates your ML workloads for privacy and compliance standard adherence (ISO 23894). The **Compliance** tab lets you verify:
- Automatically extracted GDPR compliance scores (0-100 scale).
- Active mitigations (e.g., PII anonymization, Data Minimization applied).
- Required consent checks enforced prior to pipeline deployment.

---

## 4. REST API Integration

For workflow automation scenarios (e.g. triggering KFP from a GitHub Action or external system), you can communicate via standard REST requests:

**Execute a Pipeline Example:**
```bash
curl -X POST http://127.0.0.1:8001/api/v1/execute \
  -H 'Content-Type: application/json' \
  -d '{
        "pipeline_id": "demo",
        "environment": "dev",
        "parameters": {"learning_rate": "0.01"}
     }'
```

Access the interactive OpenAPI Swagger documentation safely from **http://127.0.0.1:8001/docs** when the backend is online to explore more functionalities like dry-runs, metrics statuses, or carbon-forecast queries.
