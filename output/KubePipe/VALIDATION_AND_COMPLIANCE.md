# Workflow Validation, Dry-Run & Compliance Check

KubePipe now includes comprehensive workflow validation, dry-run simulation, and automatic compliance checking for Argo Workflows.

## Features Implemented

### 1. Input Validation (`POST /api/v1/workflows/validate`)

Validates Argo Workflow YAML files before deployment:

- **YAML Syntax Check**: Ensures valid YAML structure
- **Structure Validation**: Checks required fields (apiVersion, kind, spec, entrypoint, templates)
- **Template Validation**: Verifies all templates are properly defined
- **Security Checks**: Detects privileged containers, root users
- **Resource Validation**: Warns about missing resource limits

**Example:**
```bash
curl -X POST http://localhost:8001/api/v1/workflows/validate \
  -H "Content-Type: application/json" \
  -d '{"yaml_content": "...", "check_dependencies": true}'
```

### 2. Dependency Checks

Automatically verifies:
- **Container Images**: Validates image references are syntactically correct
- **PVCs**: Checks if PersistentVolumeClaims exist and are bound
- **Secrets**: Verifies referenced secrets exist
- **RBAC**: Checks ServiceAccount permissions for pod creation

### 3. Dry-Run Mode (`POST /api/v1/workflows/dry-run`)

Simulates workflow execution without actually running:

- **Task Categorization**: Automatically detects task types:
  - ML Training
  - ML Inference
  - Audio Processing
  - NLP Processing
  - Data Processing
  - Image/Video Processing
  
- **Resource Estimation**:
  - CPU and memory requirements
  - GPU detection
  - Estimated duration
  - Energy consumption (Wh)
  - Carbon footprint (grams CO2)

- **Execution Order**: Determines DAG execution sequence

**Example Response:**
```json
{
  "workflow_name": "sentiment-audio-pipeline-",
  "is_valid": true,
  "can_execute": true,
  "task_analyses": [
    {
      "name": "transcribe-audio",
      "category": "audio_processing",
      "confidence": 0.58,
      "compliance_requirements": {
        "gdpr": {
          "data_minimization": true,
          "requires_pseudonymization": true,
          "requires_consent_check": true,
          "pii_detection": true
        }
      }
    }
  ],
  "estimated_total_duration": 180,
  "estimated_total_energy_wh": 0.35,
  "estimated_total_carbon_grams": 0.17
}
```

### 4. Compliance Check (`POST /api/v1/workflows/compliance-check`)

Automatic compliance analysis based on detected task categories:

**GDPR Requirements** (for audio/NLP/data processing):
- Data minimization
- Purpose limitation
- Storage limitation
- Consent verification
- Pseudonymization
- PII detection

**Sustainability Requirements** (for ML tasks):
- Energy tracking
- Carbon footprint monitoring
- GPU utilization monitoring
- Idle timeout enforcement

**Security Requirements**:
- No privileged containers
- Resource limits required
- Network policies

**Example Response:**
```json
{
  "workflow_name": "sentiment-audio-pipeline-",
  "task_categories": {
    "audio_processing": ["transcribe-audio"],
    "nlp_processing": ["analyze-sentiment"]
  },
  "gdpr": {
    "applicable": true,
    "requirements": [
      "data_minimization",
      "requires_pseudonymization",
      "requires_consent_check"
    ]
  },
  "overall_risk_level": "medium",
  "recommendations": [
    "Implement consent verification before processing personal data",
    "Add pseudonymization step for personal data"
  ]
}
```

### 5. Kubernetes Metrics Server Integration

Real-time pod resource monitoring:

- **Check Status**: `GET /api/v1/metrics/status`
- **Install Metrics Server**: `POST /api/v1/metrics/install`
- **Pod Metrics**: `GET /api/v1/metrics/pods?namespace=argo`
- **Node Metrics**: `GET /api/v1/metrics/nodes`
- **Workflow Metrics**: `GET /api/v1/metrics/workflow/{workflow_name}`

Provides real-time CPU and memory usage for running workflows.

## Task Categorization Rules

The system automatically categorizes tasks based on:

| Category | Detection Patterns |
|----------|-------------------|
| ML Training | tensorflow, pytorch, train, fine-tune, lora |
| ML Inference | inference, predict, serve, triton, kserve |
| Audio Processing | transcribe, whisper, speech, audio, asr |
| NLP Processing | sentiment, nlp, bert, gpt, language, text |
| Data Processing | pandas, spark, dask, process, transform |
| Image Processing | opencv, image, vision, yolo, detectron |
| Video Processing | ffmpeg, video, stream, transcode |

## UI Integration

The ArgoWorkflows page now includes:

1. **Validation & Compliance Panel**: Click "Show Validation & Compliance" to see:
   - Validation results with issues and suggestions
   - Dry-run simulation with resource estimates
   - Compliance analysis with recommendations

2. **Validate & Deploy**: Single button to validate and deploy if all checks pass

## API Endpoints Summary

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/workflows/validate` | POST | Validate workflow YAML |
| `/api/v1/workflows/dry-run` | POST | Full dry-run simulation |
| `/api/v1/workflows/compliance-check` | POST | Compliance analysis |
| `/api/v1/workflows/validate-and-deploy` | POST | Validate then deploy |
| `/api/v1/metrics/status` | GET | Check metrics-server status |
| `/api/v1/metrics/install` | POST | Install metrics-server |
| `/api/v1/metrics/pods` | GET | Get pod metrics |
| `/api/v1/metrics/nodes` | GET | Get node metrics |
| `/api/v1/metrics/workflow/{name}` | GET | Get workflow pod metrics |

## Files Added/Modified

### New Files:
- `kubepipe/core/workflow_validator.py` - Core validation and compliance logic
- `ui/src/components/WorkflowValidator.jsx` - UI component for validation

### Modified Files:
- `kubepipe/api/main.py` - Added new API endpoints
- `kubepipe/api/schemas.py` - Added Pydantic schemas
- `ui/src/api/client.js` - Added API client functions
- `ui/src/pages/ArgoWorkflows.jsx` - Integrated validator component
