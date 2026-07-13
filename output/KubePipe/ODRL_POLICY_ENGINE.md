# ODRL Policy Engine Integration in KubePipe

## Overview

KubePipe integrates the [W3C ODRL (Open Digital Rights Language) Information Model 2.1](https://www.w3.org/TR/odrl-model/) to enforce data usage policies on ML pipelines. The integration ensures that pipeline execution is governed by formal, machine-readable policies that encode consent constraints, data retention limits, and usage prohibitions.

## Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                         KubePipe API                                │
│                                                                     │
│  ┌──────────────┐   ┌──────────────┐   ┌────────────────────────┐  │
│  │   Consent     │   │  Compliance  │   │  ODRL Policy Engine    │  │
│  │  Manager      │──▶│   Checker    │   │  (odrl_policy_engine)  │  │
│  │               │   │              │   │                        │  │
│  │ • Owners      │   │ • GDPR check │   │ • Policy CRUD          │  │
│  │ • Requests    │   │ • Auto-inject│   │ • Rule matching        │  │
│  │ • Approve     │   │ • Score      │   │ • Constraint eval      │  │
│  │ • Revoke      │   │              │   │ • Duty fulfillment     │  │
│  │ • Audit trail │   │              │   │ • Decision: permit/deny│  │
│  └──────┬───────┘   └──────┬───────┘   └───────────┬────────────┘  │
│         │                  │                       │               │
│         └──────────┬───────┘                       │               │
│                    ▼                               ▼               │
│         ┌──────────────────────────────────────────────────┐      │
│         │     State-of-the-World (SoW) Builder             │      │
│         │  _build_policy_state_of_world()                   │      │
│         │                                                  │      │
│         │  • consent_verified    • data_retention_days      │      │
│         │  • consent_status      • permissions              │      │
│         │  • compliance_score    • sustainability           │      │
│         │  • odrl_inputs (rows)  • events                   │      │
│         └──────────────────────┬───────────────────────────┘      │
│                                │                                   │
│                                ▼                                   │
│                    ┌───────────────────────┐                       │
│                    │  Evaluation Result    │                       │
│                    │  • permit             │                       │
│                    │  • deny               │                       │
│                    │  • indeterminate      │                       │
│                    └───────────────────────┘                       │
│                                                                    │
│  External mode (DATAPACT_POLICY_URL set):                          │
│    SoW ──HTTP POST──▶ External ODRL-Engine ──▶ Decision            │
└────────────────────────────────────────────────────────────────────┘
```

## How ODRL Policy Is Used in KubePipe

### 1. State-of-the-World (SoW) Export

KubePipe builds a **State-of-the-World** snapshot from three data sources:

| Source | Data | ODRL Feature Mapping |
|--------|------|---------------------|
| **Consent Manager** | `consent_verified`, `consent_status`, `permissions`, `data_retention_days` | `odrl:consent`, `odrl:permission`, `odrl:constraint` |
| **Compliance Checker** | `compliance_score`, `components_found` (anonymization, cleanup, etc.) | `odrl:duty` fulfillment |
| **Sustainability Monitor** | `energy_kwh`, `emissions_kg` | Context for policy evaluation |

The SoW is exposed via `GET /api/v1/policy/state-of-world` and is the primary interface for external ODRL engines.

### 2. Policy Evaluation

The `ODRLPolicyEngine` evaluates the SoW against stored policies:

- **Prohibitions** are checked first — if any match, the decision is `deny`
- **Permissions** are checked next — if any match with all constraints satisfied and duties fulfilled, the decision is `permit`
- If no permission matches but constraints fail, the decision is `deny`
- If no rules match at all, the decision is `indeterminate`

### 3. Execution-Time Policy Gate (Pre-Execution Blocking)

**This is the key mechanism**: ODRL policies **gate** pipeline execution. Before any pipeline is submitted to KFP or Argo, KubePipe evaluates the ODRL policies and **blocks** execution if the decision is `deny`.

#### Flow

```
User submits pipeline (KFP run / Argo deploy)
         │
         ▼
┌─────────────────────────────────────────────┐
│  _evaluate_pre_exec_policy_gate()           │
│                                             │
│  1. Check if any enabled ODRL policies exist│
│     → If none: skip gate, proceed freely    │
│  2. Build State-of-the-World (SoW) snapshot │
│     from consent + compliance + monitor     │
│  3. Evaluate SoW against all policies       │
│  4. Return decision: permit / deny /        │
│     indeterminate                           │
└──────────────────┬──────────────────────────┘
                   │
         ┌─────────┴─────────┐
         ▼                   ▼
   decision == "deny"   decision != "deny"
         │                   │
         ▼                   ▼
┌─────────────────┐  ┌──────────────────────┐
│ BLOCK execution │  │ Proceed with submit  │
│ Return status:  │  │ to KFP / Argo        │
│ "blocked"       │  │                      │
│ + policy_decision│ │ Store gate result as │
│ (reason,        │  │ policy_evaluation_pre│
│  violated_      │  │ artifact              │
│  prohibitions)  │  └──────────────────────┘
└─────────────────┘
```

#### What Happens on `deny`

When the policy gate returns `deny`, the API endpoint returns immediately with:

```json
{
  "status": "blocked",
  "run_id": "",
  "detail": "Pipeline blocked by ODRL policy: Pipeline blocked: 1 prohibition(s) violated",
  "policy_decision": {
    "decision": "deny",
    "pipeline_id": "my-pipeline",
    "run_id": null,
    "matched_policies": ["uuid-1"],
    "violated_prohibitions": [...],
    "reason": "Pipeline blocked: 1 prohibition(s) violated",
    "engine_mode": "local"
  }
}
```

The pipeline is **never submitted** to KFP or Argo. The user sees the `blocked` status and the reason (which prohibitions were violated, which constraints failed).

#### What Happens on `permit` or `indeterminate`

The pipeline proceeds normally. The gate result is stored as the `policy_evaluation_pre` run artifact (so it's not re-evaluated — the gate result is reused).

#### Endpoints with Policy Gate

| Endpoint | Gate Behavior |
|----------|---------------|
| `POST /api/v1/execute` | Blocks KFP run if `deny` |
| `POST /api/v1/pipelines/{id}/create-run` | Blocks KFP run if `deny` |
| `POST /api/v1/argo/deploy` | Blocks Argo deploy if `deny` |

#### Post-Execution Evaluation

After a pipeline completes, `_capture_post_exec_policy_sow()` builds a fresh SoW (now including run results, compliance artifacts, sustainability metrics) and evaluates it again. The result is stored as `policy_evaluation_post` artifact. This is for **audit** purposes — it doesn't block anything, but records whether the pipeline remained compliant throughout execution.

### 4. Consent → Policy Bridge

When consent is approved, an ODRL policy can be auto-generated from the consent request:

```
POST /api/v1/policy/auto-create-from-consent/{consent_request_id}
```

This creates an ODRL `Agreement` policy with:
- **Permissions** encoding each consent permission with constraints (`consent_verified == true`, `consent_status == "approved"`, `data_retention_days <= N`)
- **Duties** requiring `obtainConsent` and `deleteData`
- **Prohibition** blocking use without consent (`consent_verified == false`)

## ODRL Concepts Implemented

### Policy
```json
{
  "uid": "uuid",
  "name": "GDPR Policy for ML Training Pipeline",
  "policy_type": "agreement",
  "assigner": "data-owner-id",
  "assignee": "pipeline-requester-id",
  "permissions": [...],
  "prohibitions": [...],
  "obligations": [...],
  "pipeline_id": "my-pipeline",
  "enabled": true
}
```

### Permission
```json
{
  "uid": "perm-uuid",
  "action": "process",
  "target": "user-data-dataset",
  "purpose": "ml-training",
  "constraints": [
    {
      "left_operand": "consent_verified",
      "operator": "eq",
      "right_operand": true,
      "datatype": "boolean"
    }
  ],
  "duties": [
    {"action": "obtainConsent"},
    {"action": "deleteData"}
  ]
}
```

### Prohibition
```json
{
  "uid": "proh-uuid",
  "action": "use",
  "constraints": [
    {
      "left_operand": "consent_verified",
      "operator": "eq",
      "right_operand": false,
      "datatype": "boolean"
    }
  ]
}
```

### Constraint Operators

| Operator | Description | Example |
|----------|-------------|---------|
| `eq` | Equals | `consent_verified eq true` |
| `neq` | Not equals | `consent_status neq "revoked"` |
| `gt` | Greater than | `data_retention_days gt 0` |
| `gteq` | Greater than or equal | `compliance_score gteq 80` |
| `lt` | Less than | `data_retention_days lt 365` |
| `lteq` | Less than or equal | `data_retention_days lteq 30` |
| `in` | In list | `consent_status in "approved,sent"` |

### Duties

Duties are obligations that must be fulfilled for a permission to be valid:

| Duty Action | Fulfillment Check |
|-------------|-------------------|
| `obtainConsent` | Checks `consent_verified == true` in SoW |
| `deleteData` | Checks for PII cleanup component in compliance |
| `anonymize` | Checks for anonymization component in compliance |

## API Endpoints

### Policy Management

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/v1/policy/policies` | Create a new ODRL policy |
| `GET` | `/api/v1/policy/policies` | List policies (filter by `pipeline_id`, `enabled`) |
| `GET` | `/api/v1/policy/policies/{id}` | Get a specific policy |
| `PUT` | `/api/v1/policy/policies/{id}` | Update a policy |
| `DELETE` | `/api/v1/policy/policies/{id}` | Delete a policy |
| `POST` | `/api/v1/policy/policies/{id}/enable` | Enable a policy |
| `POST` | `/api/v1/policy/policies/{id}/disable` | Disable a policy |

### Policy Evaluation

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/v1/policy/evaluate` | Evaluate a pipeline against policies |
| `GET` | `/api/v1/policy/evaluate/{pipeline_id}` | Quick evaluation (GET) |
| `GET` | `/api/v1/policy/evaluations` | List past evaluation results |
| `GET` | `/api/v1/policy/state-of-world` | Export SoW for external engines |

### Consent → Policy Bridge

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/v1/policy/auto-create-from-consent/{id}` | Auto-create policy from approved consent |

### Statistics

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/v1/policy/stats` | Policy engine statistics |

## Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `DATAPACT_POLICY_ENABLED` | `true` | Enable/disable policy engine |
| `DATAPACT_POLICY_URL` | _(empty)_ | External ODRL-Engine URL (if set, delegates evaluation) |
| `KUBEPIPE_POLICY_STORE` | `data/odrl_policy_store.json` | Path to policy store file |

### Local vs External Engine

- **Local mode** (default): The built-in rule matcher evaluates policies. No external service required.
- **External mode**: When `DATAPACT_POLICY_URL` is set, KubePipe delegates evaluation to an external ODRL-Engine service via HTTP POST to `/api/v1/odrl/evaluate`.

## Usage Examples

### Create a Policy

```bash
curl -X POST http://localhost:8001/api/v1/policy/policies \
  -H 'Content-Type: application/json' \
  -d '{
    "name": "GDPR Policy for User Analytics",
    "permissions": [{
      "uid": "perm-1",
      "action": "process",
      "target": "user-data",
      "purpose": "analytics",
      "constraints": [
        {"left_operand": "consent_verified", "operator": "eq", "right_operand": true},
        {"left_operand": "data_retention_days", "operator": "lteq", "right_operand": 30}
      ],
      "duties": [{"action": "obtainConsent"}, {"action": "deleteData"}]
    }],
    "prohibitions": [{
      "uid": "proh-1",
      "action": "use",
      "constraints": [
        {"left_operand": "consent_verified", "operator": "eq", "right_operand": false}
      ]
    }],
    "pipeline_id": "user-analytics-pipeline"
  }'
```

### Evaluate a Pipeline

```bash
curl -X POST http://localhost:8001/api/v1/policy/evaluate \
  -H 'Content-Type: application/json' \
  -d '{"pipeline_id": "user-analytics-pipeline"}'
```

Response:
```json
{
  "decision": "permit",
  "pipeline_id": "user-analytics-pipeline",
  "matched_policies": ["uuid-1"],
  "matched_permissions": [{...}],
  "reason": "Pipeline permitted: 1 permission(s) matched",
  "engine_mode": "local"
}
```

### Auto-Create Policy from Consent

```bash
curl -X POST http://localhost:8001/api/v1/policy/auto-create-from-consent/consent-uuid
```

## Files

| File | Description |
|------|-------------|
| `kubepipe/core/odrl_policy_engine.py` | Core ODRL policy engine (policy store, evaluation, auto-creation) |
| `kubepipe/api/schemas.py` | Pydantic schemas for policy API |
| `kubepipe/api/main.py` | FastAPI endpoints for policy management and evaluation |
| `ui/src/api/client.js` | UI API client functions for policy engine |
| `data/odrl_policy_store.json` | JSON file store for policies and evaluation history |