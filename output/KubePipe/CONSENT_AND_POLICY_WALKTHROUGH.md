# Consent Manager + ODRL Policy Engine: End-to-End Walkthrough

This document walks through the complete, real flow of using KubePipe's
[Consent Manager](CONSENT_MANAGER.md) and [ODRL Policy Engine](ODRL_POLICY_ENGINE.md)
together to gate a pipeline on GDPR consent, using the actual manual steps required
today, via both the API and the UI.

Every command and response below was run against a live KubePipe backend
(Keycloak-authenticated) during development — nothing here is hypothetical. That
matters because the exercise surfaced four real behavioral gaps in the current
implementation (see [Known Issues](#known-issues-verified-live)) that are not
obvious from reading the code alone, and that change what "correct" manual usage
looks like today.

## Scenario

An ML team wants to train a customer-churn model on a dataset that contains personal
data. Before the pipeline can run, the data owner (the customer, represented here by
a data protection contact) must consent to that specific use.

- **Data owner**: Maria Schmidt (`maria.schmidt@example.com`)
- **Requester**: ML Platform Team (`ml-team@kubepipe.local`)
- **Pipeline**: `customer-churn-training-pipeline`
- **Permission requested**: `train` on `customer_churn_records` for purpose `ml-training`, 30-day retention

## Prerequisites

- Backend running (`bash scripts/start_all.sh`, or just `uvicorn kubepipe.api.main:app`).
- If Keycloak auth is enabled (`KEYCLOAK_ENABLED=true`), you need a Bearer token for
  a user with the `admin` or `compliance_officer` role (consent/policy endpoints
  require one of those; see [KEYCLOAK_INTEGRATION.md](KEYCLOAK_INTEGRATION.md)).
  All commands below assume `$AUTH` is set to `Authorization: Bearer <token>`.

```bash
TOKEN=$(curl -s -X POST http://localhost:8085/realms/kubepipe/protocol/openid-connect/token \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  -d "grant_type=password&client_id=kubepipe-ui&client_secret=$KEYCLOAK_CLIENT_SECRET&username=admin&password=admin123" \
  | python3 -c "import sys,json;print(json.load(sys.stdin)['access_token'])")
AUTH="Authorization: Bearer $TOKEN"
```

Access tokens expire in ~5 minutes by default — re-fetch `$TOKEN` if you see
`{"detail":"Invalid or expired token."}`.

## Step 0 — Baseline: no consent, no policy

Before any consent or policy exists, execution is **not gated at all**:

```bash
curl -s -X POST http://localhost:8001/api/v1/pipelines/customer-churn-training-pipeline/create-run -H "$AUTH"
```
```json
{"status": "error", "message": "Failed to create run: HTTPConnectionPool(host='127.0.0.1', port=8080): ... Connection refused"}
```

This is a plain KFP-unreachable error, not a policy decision — with zero ODRL
policies configured, `_evaluate_pre_exec_policy_gate` returns `None` and the request
proceeds straight to the (here, unavailable) execution backend. **No consent
records at all means no restriction whatsoever.**

## Step 1 — Register the data owner and requester

```bash
curl -s -X POST http://localhost:8001/api/v1/consent/owners -H "$AUTH" -H 'Content-Type: application/json' \
  -d '{"name":"Maria Schmidt","email":"maria.schmidt@example.com"}'
# -> {"status":"ok","owner":{"id":"e3f9142c-...","name":"Maria Schmidt", ...}}

curl -s -X POST http://localhost:8001/api/v1/consent/requesters -H "$AUTH" -H 'Content-Type: application/json' \
  -d '{"name":"ML Platform Team","email":"ml-team@kubepipe.local"}'
# -> {"status":"ok","requester":{"id":"6f209cd0-...","name":"ML Platform Team", ...}}
```

Keep the two `id` values — you need them below.

## Step 2 — Create the consent request (draft)

```bash
curl -s -X POST http://localhost:8001/api/v1/consent/requests -H "$AUTH" -H 'Content-Type: application/json' -d '{
  "request_name": "Customer Churn Model Training Data Access",
  "requester_id": "<requester_id>",
  "requester_name": "ML Platform Team",
  "requester_email": "ml-team@kubepipe.local",
  "permissions": [{"id":1,"dataset":"customer_churn_records","action":"train","purpose":"ml-training"}],
  "pipeline_id": "customer-churn-training-pipeline",
  "data_retention_days": 30
}'
```

Response: `"status": "draft"`. Note the `id` returned — this is the consent
request ID used in every subsequent step.

## Step 3 — Send it to the owner

```bash
curl -s -X POST http://localhost:8001/api/v1/consent/requests/<request_id>/send -H "$AUTH" -H 'Content-Type: application/json' \
  -d '{"owner_emails":["maria.schmidt@example.com"]}'
```

Status becomes `sent`, `owners_pending` now contains the owner's ID.

**Checkpoint** — try `create-run` again right now:

```bash
curl -s -X POST http://localhost:8001/api/v1/pipelines/customer-churn-training-pipeline/create-run -H "$AUTH"
```
Same connection-refused error as Step 0. **A pending (`sent`) consent request has
zero enforcement effect.** Only an evaluated ODRL policy can block execution, and
none exists yet.

## Step 4 — Owner approves

```bash
curl -s -X POST http://localhost:8001/api/v1/consent/requests/<request_id>/approve -H "$AUTH" -H 'Content-Type: application/json' \
  -d '{"owner_id":"<owner_id>"}'
```

Response includes both the now-`approved` request **and** an auto-created policy:

```json
{
  "status": "ok",
  "consent_request": { "...": "status: approved, odrl_policy_uid: 08d6e6f9-..." },
  "auto_created_policy": {
    "uid": "08d6e6f9-6345-4006-8d03-f955cce3c223",
    "permissions": [{
      "action": "train", "target": "customer_churn_records", "purpose": "ml-training",
      "constraints": [
        {"left_operand": "consent_verified", "operator": "eq", "right_operand": true},
        {"left_operand": "consent_status", "operator": "eq", "right_operand": "approved"},
        {"left_operand": "data_retention_days", "operator": "lteq", "right_operand": 30}
      ],
      "duties": [{"action": "obtainConsent"}, {"action": "deleteData"}]
    }],
    "prohibitions": [{
      "action": "use",
      "constraints": [{"left_operand": "consent_verified", "operator": "eq", "right_operand": false}]
    }]
  }
}
```

No manual policy-authoring step was needed — this is the consent → policy bridge
working as designed.

## Step 5 — Deploy, expecting success... but it's blocked

Deploy an Argo workflow whose `metadata.name` matches the pipeline ID above (the
gate matches on this name):

```bash
curl -s -X POST http://localhost:8001/api/v1/argo/deploy -H "$AUTH" -H 'Content-Type: application/json' -d '{
  "yaml_content": "apiVersion: argoproj.io/v1alpha1\nkind: Workflow\nmetadata:\n  name: customer-churn-training-pipeline\nspec:\n  entrypoint: main\n  templates:\n  - name: main\n    container:\n      image: python:3.11\n      command: [\"python\", \"-c\", \"print(1)\"]\n"
}'
```

**Actual response:**
```json
{
  "status": "blocked",
  "detail": "Workflow blocked by ODRL policy: Pipeline blocked: constraints/duties not satisfied (0 failed, 1 unfulfilled duties)"
}
```

Consent was just approved. This is not what most operators would expect — see
[Known Issue #1](#1-the-auto-created-policy-can-never-permit-on-first-run) below for
why, and the fix in the next step.

## Step 6 — The fix: edit the auto-created policy

```bash
curl -s -X PUT http://localhost:8001/api/v1/policy/policies/<policy_uid> -H "$AUTH" -H 'Content-Type: application/json' -d '{
  "permissions": [{
    "uid": "8e879114-4a09-42c9-97a2-dba00e83afe2",
    "action": "train", "target": "customer_churn_records", "purpose": "ml-training",
    "constraints": [
      {"left_operand": "consent_verified", "operator": "eq", "right_operand": true, "datatype": "boolean"},
      {"left_operand": "consent_status", "operator": "eq", "right_operand": "approved", "datatype": "string"},
      {"left_operand": "data_retention_days", "operator": "lteq", "right_operand": 30, "datatype": "number"}
    ],
    "duties": [{"action": "obtainConsent"}]
  }]
}'
```

We dropped the `deleteData` duty. Re-evaluating now gives:

```json
{
  "decision": "permit",
  "matched_permissions": [{ "...": "the train permission" }],
  "reason": "Pipeline permitted: 1 permission(s) matched"
}
```

Re-running the exact same Argo deploy from Step 5 now returns
`"status": "error"` with a Kubernetes connection error — **not** `"status":
"blocked"` — confirming the gate passed and the only remaining failure is that no
real cluster is running in this environment.

## Step 7 — Revoke consent

```bash
curl -s -X POST http://localhost:8001/api/v1/consent/requests/<request_id>/revoke -H "$AUTH" -H 'Content-Type: application/json' \
  -d '{"owner_id":"<owner_id>","reason":"Customer withdrew consent"}'
```

The linked policy is auto-disabled (`"odrl_policy_disabled": true` in the response).
Re-evaluating the pipeline immediately after:

```json
{
  "decision": "permit",
  "matched_policies": [],
  "reason": "No ODRL policies configured — default permit"
}
```

**Revoking consent just made the pipeline more permitted, not less.** See
[Known Issue #2](#2-revoking-consent-re-opens-execution-instead-of-blocking-it) —
this is the most important gap to understand before relying on revocation as a
safety mechanism.

## Manual steps via the UI

The API flow above maps to the following UI steps (`ConsentManager.jsx` and
`PolicyEngine.jsx`, both under the `compliance_officer`/`admin` role):

1. **Consent Manager → Owners tab** → add the data owner.
2. **Consent Manager → Requesters tab** → add the requester.
3. **Consent Manager → Create tab** → fill in request name, one permission
   (dataset/action/purpose), retention days, pipeline ID → submit. This only
   supports **one permission per request** from the UI form — for multiple
   datasets/actions you currently need the API.
4. Send the request to the owner's email from the request's detail view.
5. Approve as the owner (or on their behalf as `compliance_officer`) using the
   approve action — this uses a native browser `prompt()`/`confirm()` dialog, not a
   custom modal.
6. **Go to Policy Engine** and find the auto-created policy. **Manually remove the
   `deleteData` duty** (or any duty you cannot yet satisfy pre-execution) — the
   `CreatePolicyForm` only supports a flat single-permission structure with fixed
   fields and has no raw JSON editor, so this edit currently has to go through the
   API (`PUT /api/v1/policy/policies/{id}`), not the UI.
7. Deploy the pipeline from Pipeline Management (Argo deploy path is the one that
   reliably enforces the gate — see Known Issue #3).

## Known issues (verified live)

These were all reproduced against a running instance, not inferred from reading
code alone.

### 1. The auto-created policy can never permit on first run

`auto_create_policy_from_consent()` always attaches a `deleteData` duty to the
generated permission. Duty fulfillment for `deleteData` is checked against
*post-run* compliance data (`sow.compliance.run_compliance.components_found`,
looked up by `run_id`). The pre-execution gate always evaluates with `run_id=None`
(no run exists yet), so `components_found` is always empty and the duty can never be
satisfied. **Every pipeline relying on the default consent→policy bridge is denied
on its first deploy attempt**, regardless of how valid the underlying consent is.

**Reproduction**: Steps 4–5 above. **Workaround**: after approval, edit the
generated policy to remove (or relax) the `deleteData` duty before first deploy
(Step 6), or don't rely on auto-generated duties at all and author policies without
duties that depend on data that can't exist yet.

### 2. Revoking consent re-opens execution instead of blocking it

`revoke_consent()`'s handler disables the linked ODRL policy, and its own docstring
says this is "so the policy gate will block future pipeline executions." But the
evaluator's rule for "no *enabled* policies apply" is **default permit**
(`"reason": "No ODRL policies configured — default permit"`). Disabling the only
policy that covered a pipeline therefore removes the block instead of adding one.

**Reproduction**: Step 7 above. **Impact**: this is the most consequential gap —
revocation is the GDPR-mandated "as easy to withdraw as to give" mechanism, and
right now it doesn't actually stop anything by itself.

**Workaround today**: maintain a standing, pipeline-scoped (or global) prohibition
policy that denies `use`/action whenever `consent_status != "approved"` or
`consent_verified != true`, independent of any auto-created policy, so that
disabling one policy never leaves zero applicable policies. A durable fix would
change the evaluator's no-policy fallback to be pipeline-aware (e.g., default-deny
if the pipeline has ever had an approved-then-revoked consent) rather than a blanket
default-permit.

### 3. The gate can be silently skipped in `create-run` when the execution backend is unreachable

In `POST /api/v1/pipelines/{id}/create-run`, `kfp.Client(host=...)` is constructed
*before* the ODRL gate check, inside the same outer `try/except` that also handles
execution errors. If the KFP client fails to connect, that exception is caught by
the outer handler and returned as a generic `"status": "error"` — **the gate code is
never reached**, so a `deny` decision has no chance to fire in that scenario. This
was confirmed by comparing the `create-run` response against the same state's
`/api/v1/policy/evaluate/{pipeline_id}` result (which correctly returned `deny`)
side-by-side — the two disagreed. `POST /api/v1/argo/deploy` does **not** have this
problem: its gate check runs before any Kubernetes client is constructed, which is
why Steps 5–6 above use the Argo deploy path to demonstrate a real `blocked`
response. `POST /api/v1/execute` only calls the gate at all when `pipeline_id` is a
real KFP UUID *and* `execution.mode == "kfp"` — for the local/mock execution path it
does not evaluate the gate before submitting.

**Practical implication**: don't rely on `create-run` or `execute` to reliably
demonstrate or enforce a `deny` when the target cluster might be unreachable — use
`/api/v1/policy/evaluate/{pipeline_id}` to check the decision directly, and prefer
`argo/deploy` for actually gated deployment in environments where KFP connectivity
is uncertain.

### 4. Pending/unresolved consent has no independent enforcement

A `sent` (not yet approved) or `rejected` consent request does not, by itself,
block anything — enforcement only happens through an ODRL policy evaluation. If no
policy has been created yet (which only happens automatically on *approval*), a
pipeline can be deployed with consent outstanding or explicitly rejected, as long as
no other policy applies. If you need pending/rejected consent to block execution,
create an explicit policy for that pipeline up front (before requesting consent)
rather than depending solely on the auto-created bridge.

## Recommendations for operators, given the above

1. **Never assume "consent approved" implies "pipeline can run."** Always check
   `GET /api/v1/policy/evaluate/{pipeline_id}` after approval and adjust the
   generated policy if the decision isn't `permit`.
2. **Maintain a standing deny-by-default policy per sensitive pipeline** rather than
   relying solely on the auto-generated one, so that revocation (which disables a
   policy) doesn't silently fall back to default-permit.
3. **Use `argo/deploy` (or confirm cluster reachability first)** when you need the
   gate to be authoritative — `create-run`'s gate can be bypassed by an unreachable
   KFP host.
4. **Review the auto-generated `deleteData` duty before first deploy.** Either
   remove it, or make sure your compliance pipeline populates
   `run_compliance.components_found` in a way that could ever satisfy it — as
   shipped, it cannot be satisfied pre-execution.

## Files referenced

| File | Role |
|------|------|
| `kubepipe/core/consent_manager.py` | Consent lifecycle, audit trail |
| `kubepipe/core/odrl_policy_engine.py` | Policy CRUD, evaluation, consent bridge |
| `kubepipe/api/main.py` | `_evaluate_pre_exec_policy_gate`, `_build_policy_state_of_world`, endpoint wiring |
| `ui/src/pages/ConsentManager.jsx` | Consent UI |
| `ui/src/pages/PolicyEngine.jsx` | Policy UI |
