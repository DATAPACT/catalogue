# Runtime Adaptation

KubePipe provides SOTA runtime adaptations for ML workflows based on **sustainability** and **compliance** requirements.

## Adaptation Strategies

### Carbon-Aware Scheduling

| Strategy | Description |
|----------|-------------|
| **Time-Shifting** | Delay workloads to low-carbon periods (2-24h window) |
| **Region-Shifting** | Migrate to regions with cleaner energy grids |
| **Workload Shaping** | Reduce parallelism during peak carbon hours |

### Compliance Injection

| Strategy | Description |
|----------|-------------|
| **GDPR Injection** | Auto-add pseudonymization, consent checks, audit logging |
| **Data Locality** | Enforce data stays in specific regions |
| **Audit Logging** | Inject comprehensive audit trail steps |

### Resource Optimization

| Strategy | Description |
|----------|-------------|
| **Dynamic Scaling** | Scale resources based on actual utilization |
| **GPU-to-CPU Fallback** | Switch to CPU when carbon intensity is high |
| **Batch Consolidation** | Combine small workloads to reduce idle power |

## API Endpoints

```bash
# Get carbon intensity forecast
curl http://127.0.0.1:8001/api/v1/adaptation/carbon-forecast

# Get greenest regions
curl http://127.0.0.1:8001/api/v1/adaptation/green-regions

# List available strategies
curl http://127.0.0.1:8001/api/v1/adaptation/strategies

# Analyze adaptation opportunities
curl -X POST http://127.0.0.1:8001/api/v1/adaptation/analyze \
  -H 'Content-Type: application/json' \
  -d '{"yaml_content": "...", "enable_carbon_aware": true}'

# Apply adaptations
curl -X POST http://127.0.0.1:8001/api/v1/adaptation/apply \
  -H 'Content-Type: application/json' \
  -d '{"yaml_content": "...", "strategies": ["time_shifting", "gdpr_injection"]}'
```

## Web UI

Access runtime adaptation from **Argo Workflows** page:

1. Paste or upload workflow YAML
2. Click **"Show Runtime Adaptation (Carbon-Aware)"**
3. View carbon forecast and select strategies
4. Apply adaptations to transform workflow

## Carbon Intensity Data

Based on IEA 2024 regional averages (gCO2eq/kWh):

| Region | Intensity | Rating |
|--------|-----------|--------|
| Iceland | 28 | 🟢 Very Low |
| Norway | 29 | 🟢 Very Low |
| Sweden | 45 | 🟢 Low |
| France | 56 | 🟢 Low |
| Germany | 350 | 🟡 Medium |
| US Average | 380 | 🟡 Medium |
| Poland | 650 | 🔴 High |
| Australia | 540 | 🔴 High |

## GDPR Compliance Injection

When enabled, automatically injects:

- **Pseudonymization steps** before processing personal data
- **Consent verification** with fallback handling
- **Data minimization** to remove unnecessary fields
- **Audit logging** for all data access operations

## Example Adaptation

```yaml
# Original workflow
apiVersion: argoproj.io/v1alpha1
kind: Workflow
spec:
  templates:
  - name: process-data
    container:
      image: python:3.10
      command: [python, -c, "process()"]

# After GDPR injection
spec:
  templates:
  - name: pseudonymize-data
    container:
      image: kubepipe/pseudonymizer:latest
  - name: verify-consent
    container:
      image: kubepipe/consent-checker:latest
  - name: process-data  # Original step
    container:
      image: python:3.10
  - name: audit-log
    container:
      image: kubepipe/audit-logger:latest
```

## References

- [Electricity Maps API](https://www.electricitymaps.com/)
- [IEA Electricity 2024](https://www.iea.org/reports/electricity-2024)
- [EU AI Act Compliance](https://artificialintelligenceact.eu/)
- [GDPR Article 25 - Data Protection by Design](https://gdpr-info.eu/art-25-gdpr/)
