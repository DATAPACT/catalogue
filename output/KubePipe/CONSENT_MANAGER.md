# Consent Manager in KubePipe

## Overview

The Consent Manager implements a full GDPR-style consent lifecycle for data used by
ML pipelines, modeled on the DATAPACT/Consent-Manager Firestore schema but backed by
a local JSON file so KubePipe has no external dependency. It answers one question for
every pipeline: **has the person whose data this pipeline touches actually agreed to
that specific use?**

It is deliberately separate from the [ODRL Policy Engine](ODRL_POLICY_ENGINE.md):
the Consent Manager owns the human-facing request/approval workflow and the audit
trail; the Policy Engine owns machine-enforceable rules. The two are bridged
automatically (see [Consent → Policy Bridge](#consent--policy-bridge) below and the
full worked example in
[CONSENT_AND_POLICY_WALKTHROUGH.md](CONSENT_AND_POLICY_WALKTHROUGH.md)).

## Architecture

```
┌───────────────────────────────────────────────────────────────────────┐
│                         KubePipe API (main.py)                        │
│                                                                        │
│   Requester                Data Owner(s)              Pipeline        │
│   (ML team)                (data subject)              Executor       │
│      │                          │                         │           │
│      ▼                          │                         │           │
│  create_consent_request()       │                         │           │
│      │ (draft)                  │                         │           │
│      ▼                          │                         │           │
│  send_consent_request()  ──────▶│  (status: sent)          │           │
│                                  ▼                         │           │
│                          approve_consent() / reject_consent()         │
│                                  │  (status: approved / rejected)     │
│                                  ▼                                    │
│                       auto_create_policy_from_consent()               │
│                          (ODRL Policy Engine)                         │
│                                  │                                    │
│      revoke_consent() ──────────┘  (status: revoked,                 │
│         (owner, any time)           linked policy auto-disabled)      │
│                                                                        │
│  verify_pipeline_consent(pipeline_id) ─────────────────────▶ used by  │
│  verify_consent_for_data(pipeline_id, dataset, action)      the SoW   │
│                                                              builder   │
│                                                                        │
│  Every action above appends an immutable AuditEntry                   │
│  (actor_id, actor_role, action, timestamp, details)                   │
└───────────────────────────────────────────────────────────────────────┘
```

Implementation: `kubepipe/core/consent_manager.py`. Storage: a single JSON file
(`data/consent_store.json` by default, overridable via `KUBEPIPE_CONSENT_STORE` or
`consent.store_path` in `kubepipe.yaml`) with four top-level collections: `owners`,
`requesters`, `consent_requests`, `audit_log`.

## Data model

### DataOwner

The data subject — the person consent is being requested *from*.

```json
{
  "id": "e3f9142c-de7b-440e-83a0-a204d241290d",
  "name": "Maria Schmidt",
  "email": "maria.schmidt@example.com",
  "role": "owner",
  "created_at": "2026-09-22T06:47:19.426878+00:00"
}
```

Owners are looked up by email (`find_owner_by_email`) and are **auto-registered** if
a consent request is sent to an email address that has no existing owner record.

### Requester

The party asking to use the data (typically a pipeline team).

```json
{
  "id": "6f209cd0-3813-40bf-a90f-2d3e3d20bacc",
  "name": "ML Platform Team",
  "email": "ml-team@kubepipe.local",
  "role": "requester",
  "created_at": "2026-09-22T06:47:19.487917+00:00"
}
```

### Permission

A single fine-grained grant inside a consent request — mirrors the DATAPACT
`Permission` model, including four kinds of refinements for future extensibility
(currently unused by the evaluator beyond storage).

```json
{
  "id": 1,
  "dataset": "customer_churn_records",
  "action": "train",
  "purpose": "ml-training",
  "dataset_refinements": [],
  "purpose_refinements": [],
  "action_refinements": [],
  "constraint_refinements": []
}
```

`action` and `purpose` are free text (`"read"`, `"process"`, `"train"`, `"infer"` /
`"ml-training"`, `"analytics"`, `"model-serving"` are the conventions used elsewhere
in the codebase, but nothing enforces a fixed vocabulary).

### ConsentRequest

```json
{
  "id": "0e795e3c-a469-4871-afc0-3e8ea779ceb8",
  "request_name": "Customer Churn Model Training Data Access",
  "permissions": [ { "...": "Permission, see above" } ],
  "requester_id": "6f209cd0-3813-40bf-a90f-2d3e3d20bacc",
  "requester_name": "ML Platform Team",
  "requester_email": "ml-team@kubepipe.local",
  "status": "approved",
  "owners": ["e3f9142c-de7b-440e-83a0-a204d241290d"],
  "owners_accepted": ["e3f9142c-de7b-440e-83a0-a204d241290d"],
  "owners_rejected": [],
  "owners_pending": [],
  "pipeline_id": "customer-churn-training-pipeline",
  "data_retention_days": 30,
  "created_at": "2026-09-22T06:47:39.197279+00:00",
  "sent_at": "2026-09-22T06:47:39.273104+00:00",
  "resolved_at": "2026-09-22T06:47:46.381865+00:00",
  "expires_at": "",
  "odrl_policy_uid": "08d6e6f9-6345-4006-8d03-f955cce3c223"
}
```

`odrl_policy_uid` is only present once a policy has been auto-created (see below).

### AuditEntry

Appended, never mutated, for every state transition.

```json
{
  "id": "090bcba4-a2d4-4e76-8b7f-3d3715aa192a",
  "consent_request_id": "0e795e3c-a469-4871-afc0-3e8ea779ceb8",
  "action": "approved",
  "actor_id": "e3f9142c-de7b-440e-83a0-a204d241290d",
  "actor_role": "owner",
  "timestamp": "2026-09-22T06:47:46.383229+00:00",
  "details": {}
}
```

`action` is one of: `created`, `updated`, `sent`, `approved`, `rejected`, `revoked`,
`verified`, `verification_failed`, `expired`.

> **Note on trust**: `actor_id` here is the *business* identity passed in the request
> body (the owner's or requester's record ID), not necessarily the identity of the
> authenticated API caller. As of the RBAC hardening pass, all consent endpoints
> require the `admin` or `compliance_officer` role to call at all, which closes the
> "anyone could approve consent on someone else's behalf" gap — but the audit log
> itself still does not independently record *which authenticated user* performed
> the action, only the owner/requester ID they claimed to act for. Treat the audit
> log as accurate about *what* happened and *for whom*, not as cryptographic proof of
> *who at the keyboard* did it.

## Lifecycle

```
   draft ──send_consent_request──▶ sent ──┬─approve_consent(owner)──▶ approved ──revoke_consent(owner)──▶ revoked
     │                                    │        (all owners must approve;                                 │
     │                                    │         partial approval also                                     │
   update_consent_request                 │         resolves to "approved")                                   ▼
   (draft only)                           │                                                          [linked ODRL policy
     │                                    └─reject_consent(owner)──▶ rejected                          auto-disabled]
   delete_consent_request
   (draft only)
```

- **Multi-owner**: a request can target several owners; it only resolves once every
  pending owner has approved or rejected. If at least one approved and none are left
  pending, status becomes `approved` even if others rejected (a "partial approval").
- **Revocation** (GDPR Art. 7(3) — "as easy to withdraw as to give"): only an owner
  who previously accepted can revoke. This is the only path that can move a request
  *out of* `approved`.
- There is no automatic expiry sweep despite the `expires_at` field existing in the
  schema — nothing currently sets or checks it.

## Verification

Two read APIs answer "is this pipeline allowed to use this data right now?":

- `verify_pipeline_consent(pipeline_id)` — finds all consent requests for the
  pipeline, and if any is `approved`, returns its permissions and `verified: true`.
  If several requests exist, the most recently resolved `approved` one wins.
- `verify_consent_for_data(pipeline_id, dataset, action)` — same, but also checks
  that a specific `(dataset, action)` pair appears in the approved permissions.

Both are audit-logged (`verified` / `verification_failed`) with `actor_id: "system"`.
These are what the [SoW builder](ODRL_POLICY_ENGINE.md#1-state-of-the-world-sow-export)
calls to populate `consent_verified` / `consent_status` features for policy
evaluation — **consent verification by itself does not block anything**; only an
ODRL policy evaluation can produce a `deny` that halts execution. See
[CONSENT_AND_POLICY_WALKTHROUGH.md](CONSENT_AND_POLICY_WALKTHROUGH.md#known-issues-verified-live)
for what that means in practice.

## Consent → Policy bridge

- **On approval**, `POST /api/v1/consent/requests/{id}/approve` calls
  `ODRLPolicyEngine.auto_create_policy_from_consent(consent_request, pipeline_id)`,
  generating one ODRL permission per consented `(dataset, action, purpose)` with
  constraints (`consent_verified==true`, `consent_status=="approved"`,
  `data_retention_days<=N`) and duties (`obtainConsent`, `deleteData`), plus a
  blanket prohibition denying `use` when `consent_verified==false`. The new
  policy's `uid` is stored back onto the consent request as `odrl_policy_uid`.
- **On revocation**, `POST /api/v1/consent/requests/{id}/revoke` looks up
  `odrl_policy_uid` (falling back to any enabled policy linked to the same
  `pipeline_id`) and calls `disable_policy(...)` on it.
- See [CONSENT_AND_POLICY_WALKTHROUGH.md](CONSENT_AND_POLICY_WALKTHROUGH.md) for why
  both of these auto-bridges currently produce a **different practical effect than
  intended** and what to do about it today.

## API Endpoints

All consent endpoints require the `admin` or `compliance_officer` role (or, for
`verify`, additionally `data_scientist`) when Keycloak auth is enabled.

### Registration

| Method | Endpoint | Description |
|--------|----------|--------------|
| `POST` | `/api/v1/consent/owners` | Register a data owner |
| `GET` | `/api/v1/consent/owners` | List owners |
| `POST` | `/api/v1/consent/requesters` | Register a requester |
| `GET` | `/api/v1/consent/requesters` | List requesters |

### Consent Requests

| Method | Endpoint | Description |
|--------|----------|--------------|
| `POST` | `/api/v1/consent/requests` | Create a draft consent request |
| `GET` | `/api/v1/consent/requests` | List consent requests (filterable) |
| `GET` | `/api/v1/consent/requests/{id}` | Get one request |
| `PUT` | `/api/v1/consent/requests/{id}` | Update a **draft** request |
| `DELETE` | `/api/v1/consent/requests/{id}` | Delete a **draft** request |
| `POST` | `/api/v1/consent/requests/{id}/send` | Send to owner email(s) |
| `POST` | `/api/v1/consent/requests/{id}/approve` | Owner approves |
| `POST` | `/api/v1/consent/requests/{id}/reject` | Owner rejects |
| `POST` | `/api/v1/consent/requests/{id}/revoke` | Owner revokes (Art. 7(3)) |

### Verification, Audit, Reporting

| Method | Endpoint | Description |
|--------|----------|--------------|
| `POST` | `/api/v1/consent/verify` | Verify consent (body: `pipeline_id`, optional `dataset`/`action`) |
| `GET` | `/api/v1/consent/verify/{pipeline_id}` | Quick verify (GET) |
| `GET` | `/api/v1/consent/audit` | Audit trail (optionally filtered by `consent_request_id`) |
| `GET` | `/api/v1/consent/stats` | Summary counts by status |
| `GET` | `/api/v1/consent/report` | Full consent report |

## Configuration

`kubepipe.yaml`:

```yaml
consent:
  store_path: "data/consent_store.json"
  default_retention_days: 30
  enforce_on_execution: true
```

`enforce_on_execution` reflects intent, not a hard runtime switch — the only actual
enforcement mechanism today is the ODRL policy gate described in
[ODRL_POLICY_ENGINE.md](ODRL_POLICY_ENGINE.md); consent status alone is advisory
input to that gate, not an independent block.

Environment override: `KUBEPIPE_CONSENT_STORE=/path/to/consent_store.json`.

## Usage example

```bash
# 1. Register owner and requester
curl -X POST http://localhost:8001/api/v1/consent/owners \
  -H 'Content-Type: application/json' \
  -d '{"name":"Maria Schmidt","email":"maria.schmidt@example.com"}'

curl -X POST http://localhost:8001/api/v1/consent/requesters \
  -H 'Content-Type: application/json' \
  -d '{"name":"ML Platform Team","email":"ml-team@kubepipe.local"}'

# 2. Create a draft consent request
curl -X POST http://localhost:8001/api/v1/consent/requests \
  -H 'Content-Type: application/json' \
  -d '{
    "request_name": "Customer Churn Model Training Data Access",
    "requester_id": "<requester_id>",
    "requester_name": "ML Platform Team",
    "requester_email": "ml-team@kubepipe.local",
    "permissions": [{"id":1,"dataset":"customer_churn_records","action":"train","purpose":"ml-training"}],
    "pipeline_id": "customer-churn-training-pipeline",
    "data_retention_days": 30
  }'

# 3. Send it, then approve it
curl -X POST http://localhost:8001/api/v1/consent/requests/<id>/send \
  -H 'Content-Type: application/json' -d '{"owner_emails":["maria.schmidt@example.com"]}'

curl -X POST http://localhost:8001/api/v1/consent/requests/<id>/approve \
  -H 'Content-Type: application/json' -d '{"owner_id":"<owner_id>"}'
```

For the full end-to-end example — including what happens next when a pipeline
actually tries to execute — see
**[CONSENT_AND_POLICY_WALKTHROUGH.md](CONSENT_AND_POLICY_WALKTHROUGH.md)**.

## Known limitations

- **Storage**: a single flat JSON file, read-modify-write on every call, no file
  locking. Concurrent writes (e.g. two approvals landing at once) can race and
  silently drop one write. Not suitable beyond single-instance/demo use.
- **No encryption at rest**: owner names/emails are stored in plaintext JSON.
- **No expiry enforcement**: `expires_at` exists on the schema but nothing sets or
  checks it.
- **No DSAR/erasure automation**: revocation changes status and disables a policy,
  it does not locate or delete the underlying data anywhere.
- **Audit trail is not independently verifiable**: entries are appended in-process
  with no hash chaining or signing — sufficient for internal review, not for
  producing tamper-evident evidence to a regulator.

## Files

| File | Description |
|------|--------------|
| `kubepipe/core/consent_manager.py` | Core consent lifecycle logic and JSON store |
| `kubepipe/api/schemas.py` | Pydantic schemas for the consent API |
| `kubepipe/api/main.py` | FastAPI endpoints, consent→policy bridge wiring |
| `ui/src/pages/ConsentManager.jsx` | Consent Manager UI (Owners/Requests/Create tabs) |
| `data/consent_store.json` | JSON file store for owners, requesters, requests, audit log |
