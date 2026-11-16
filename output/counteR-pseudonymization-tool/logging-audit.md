# Logging and audit trail

The service writes two kinds of logs:

- **Application logs** (troubleshooting and monitoring): what the service did and why it failed.
- **Audit trail** (accountability): one record per use of a CPS tool, saying **who** called **which
  tool**, **when**, and whether it **succeeded, failed or was denied**.

Both share a correlation id, so you can go from an audit record to the application log lines of
the same call.

## Audit trail

### What gets recorded

Every endpoint annotated with `@Audited` is a CPS tool. Each call produces **exactly one** event,
written once the response status is known:

- calls that reach the endpoint are recorded by `AuditFilter`, a RESTEasy Reactive response filter;
- calls that security rejects (no token: 401, missing role: 403) are recorded by
  `DeniedAccessAuditor`. Quarkus 2.10 rejects these right after routing, before any filter runs and
  before the matched method is known, so this class maps them by request line through
  `AuditedRoutes`, an index built at startup from the endpoints' own annotations. It then delegates
  to Quarkus' own mappers, so the 401/403 responses themselves are unchanged. These events have no
  `durationMs`, and their log lines carry no `requestId` MDC value.

| `action`        | Endpoint                          |
|-----------------|-----------------------------------|
| `encrypt`       | `POST /transit/encrypt`           |
| `decrypt`       | `POST /transit/decrypt`           |
| `encrypt/batch` | `POST /transit/encrypt/batch`     |
| `decrypt/batch` | `POST /transit/decrypt/batch`     |
| `encrypt/csv`   | `POST /transit/encrypt/csv`       |
| `decrypt/csv`   | `POST /transit/decrypt/csv`       |
| `encrypt/pdf`   | `POST /transit/encrypt/pdf`       |
| `decrypt/pdf`   | `POST /transit/decrypt/pdf`       |
| `read-key`      | `GET /key` (admin only)           |

Events go to the `audit` log category as one JSON object per line. Null fields are omitted.

| Field          | Meaning |
|----------------|---------|
| `timestamp`    | When the call reached the service (UTC, ISO-8601). |
| `requestId`    | Correlation id; also returned in the `X-Request-Id` response header. |
| `action`       | The CPS tool (table above). |
| `outcome`      | `SUCCESS` (2xx/3xx), `DENIED` (401/403) or `FAILURE` (other 4xx/5xx). |
| `httpStatus`   | The HTTP status returned. |
| `durationMs`   | Processing time. |
| `userId`       | The access token's `sub` claim: the caller's Keycloak user id (a UUID). Absent for anonymous calls. Username and email are never logged. |
| `httpMethod`, `path` | The request line, without the query string. |
| `error`        | Class name of the exception that ended the call, if any. Never its message. |
| `details`      | Per-tool metadata, see below. |

`details` per tool:

- batch and CSV tools: `items` (number of values or tokens). CSV tools also record `fileBytes`.
- `encrypt/pdf`: `llmProvider` (`primary` = local, `secondary` = cloud), `fileBytes`, and on success
  also `entities`, `llmTokens` and `llmBatches`. `llmProvider` is recorded even when the call fails,
  because choosing the cloud provider sends the document text to a third party before tokenisation.
- `decrypt/pdf`: `fileBytes`.

Example:

```json
{"timestamp":"2026-10-22T09:14:03.118Z","requestId":"6f1c2e0a-5b7d-4c1e-9a43-0d6f2b8e7c11","action":"encrypt/pdf","outcome":"SUCCESS","httpStatus":200,"durationMs":8412,"userId":"6b1f4c2e-8d3a-4f5b-9c7e-2a1d0e9f8b7c","httpMethod":"POST","path":"/transit/encrypt/pdf","details":{"llmProvider":"primary","fileBytes":48211,"entities":17,"llmTokens":9120,"llmBatches":2}}
```

### What is never logged

Request or response content never reaches either log: plaintext, ciphertext or Vault tokens, CSV
or PDF contents, detected entities, access tokens or secrets. The audit trail records metadata only,
and the PDF and CSV services log counts only. Keep it that way: the audit log is retained for a long
time and must not become a second copy of the data this service pseudonymises.
`AuditContext.detail(...)` is for counts, sizes and selected options only.

The caller's **username, email and IP address** are not logged either: not in the audit trail, the
access log or the application logs. The audit trail identifies the caller only by their Keycloak
user id (`userId`). To find out who an
id belongs to, look it up in Keycloak (admin console, or
`GET /admin/realms/{realm}/users/{userId}`). That keeps re-identification behind Keycloak's own
access control instead of in every copy of the logs.

### Coverage limits

- A request whose bearer token is **present but invalid** (expired, bad signature) is rejected by
  Quarkus' HTTP security layer before any REST code runs, so it has no audit event. It does appear
  in the HTTP access log with status 401. A request with **no** token is audited as `DENIED`.
- A new endpoint is audited only once it is annotated with `@Audited` and its `AuditAction` exists.
  `AuditTrailTest.everyCpsToolResolvesFromItsRequestLine` lists every tool's route. Extend it when
  adding one.
- Requests over the 100 MB body limit (413) are rejected the same way and appear only in the
  access log.

## Error responses

All exceptions are mapped in one place (`GlobalExceptionMapper`):

- **Server-side faults** (Vault, LLM or I/O errors) return `500` with the body
  `Internal server error. Reference: <requestId>`. The full stack trace is logged server-side
  under that id. Exception messages are no longer sent to the client.
- **Invalid input** returns `400` with a message written for the caller. Examples: an upload that
  is not a CSV, a `words`/`tokens` part that is not a JSON array, a missing file part or body.
  These used to return `500`.
- An LLM failure is wrapped in `LlmCallException`, so the upstream provider's status (for example a
  cloud 401) is never passed through as this service's own status.

The UI can show the `X-Request-Id` header (or the reference in the body) to users, so a reported
problem can be traced to its audit event and log lines.

## Correlation id

`AuditFilter` gives every request a correlation id. It reuses a well-formed inbound `X-Request-Id`
(`[A-Za-z0-9._-]{1,64}`, so nginx or the UI can supply one) and generates a UUID otherwise. The id
is:

- returned in the `X-Request-Id` response header,
- set as the `requestId` MDC key, which the console format below prints on every log line,
- the `requestId` of the audit event, and quoted in 500 error bodies and error log lines.

## Configuration

> The block below belongs in `src/main/resources/application.yml`, merged into the existing
> `quarkus:` and `quarkus.http:` keys. YAML rejects duplicate keys, so edit the existing
> `cors.exposed-headers` line rather than adding a second `http:` block.
> The whole block has been verified with Quarkus 2.10, in tests and in a production build. Because
> the `%test` override keeps the `AUDIT` handler enabled, every `./mvnw test` builds the app with this
> logging setup, so a change that breaks it fails the tests rather than the deployment.
>
> **Running the tests from IntelliJ:** add `-Djava.util.logging.manager=org.jboss.logmanager.LogManager`
> to the VM options of the JUnit run-configuration template. Maven, Docker and `quarkus:dev` set it
> already. Without it Quarkus' log handlers are not applied, and `AuditLogFileTest` is skipped
> rather than failing.

```yaml
quarkus:
  log:
    level: ${LOG_LEVEL:INFO}
    console:
      # [%X{requestId}] ties each log line to its call's audit event (set by AuditFilter)
      format: "%d{yyyy-MM-dd HH:mm:ss,SSS} %-5p [%c{3.}] (%t) [%X{requestId}] %s%e%n"
    category:
      "ro.assist.datapact":
        level: ${APP_LOG_LEVEL:INFO}
      "audit":                           # the audit trail (AuditLogger.CATEGORY)
        level: INFO
        handlers: AUDIT                  # in addition to the console
    handler:
      file:
        AUDIT:
          enable: ${AUDIT_LOG_FILE_ENABLED:true}
          path: ${AUDIT_LOG_PATH:logs/audit.log}
          format: "%s%n"                 # each message is already one JSON object
          rotation:
            file-suffix: .yyyy-MM-dd     # one file per day
            max-file-size: 50M
            max-backup-index: 30
  http:
    record-request-start-time: true      # needed for %D (duration) in the access log
    access-log:
      enabled: ${ACCESS_LOG_ENABLED:true}
      # Metadata only. Never add request bodies, %q (query string), the Authorization header,
      # or client addresses (%h, %a, X-Forwarded-For): IP addresses are personal data.
      pattern: '"%m %U" %s %b %Dms req=%{o,X-Request-Id}'
      exclude-pattern: /q/.*
    cors:
      # existing list + X-Request-Id, so the UI can read the reference id
      exposed-headers: "Content-Disposition, X-Total-Tokens, X-Entities-Found, X-Llm-Batches, X-Request-Id"

"%test":
  quarkus:
    log:
      handler:
        file:
          AUDIT:
            # Stays enabled so every test build exercises the handler; the file goes under target/.
            path: target/audit.log
```

Do not add `quarkus-logging-json` (JSON console output) to this project. In Quarkus 2.10, combining it
with a named file handler such as `AUDIT` breaks every dev-mode and test build with
`You cannot invoke getValue() directly on an object returned from the bytecode recorder`
(`LoggingSetupRecorder.configureFileHandler`, called from `initializeBuildTimeLogging`). The audit
file does not need it: each event is already serialised to JSON by `AuditLogger`.

Environment variables:

| Variable                 | Default          | Purpose |
|--------------------------|------------------|---------|
| `LOG_LEVEL`              | `INFO`           | Root log level. |
| `APP_LOG_LEVEL`          | `INFO`           | Level for this service's own classes (`DEBUG` adds Vault batch sizes). |
| `AUDIT_LOG_FILE_ENABLED` | `true`           | Write the audit file. The audit trail always reaches the console too. |
| `AUDIT_LOG_PATH`         | `logs/audit.log` | Audit file. The Docker image sets `/opt/code/logs/audit.log`. |
| `ACCESS_LOG_ENABLED`     | `true`           | HTTP access log (category `io.quarkus.http.access-log`). |

## Deployment

- The image creates `/opt/code/logs`, owned by the runtime user, and points `AUDIT_LOG_PATH` there.
- `docker-compose.yml` mounts the `logs` named volume on it, so the audit trail survives container
  re-creation and redeploys. Stdout stays capped by the json-file driver (3 × 10 MB) and should not
  be relied on for audit.

## Retention and access (to be decided)

The audit trail identifies operators only by Keycloak user id. That id is still personal data under
the GDPR: it is pseudonymous rather than anonymous, because Keycloak can map it back to a person.
The trail needs:

- **A retention period.** This is a policy decision, not set in code. Quarkus rotates the file daily
  but does **not** delete old daily files (`max-backup-index` only limits size-based rollovers
  within a day). Enforce retention on the volume (logrotate or a cron job) or in the log platform
  that ships the file.
- **Restricted access** to the `logs` volume and to any system the logs are shipped to.

## Querying the audit file

```bash
# failed or denied calls
jq -c 'select(.outcome != "SUCCESS")' logs/audit.log

# tool usage per user and outcome
jq -r '[.userId, .action, .outcome] | @tsv' logs/audit.log | sort | uniq -c

# PDF documents sent to the cloud LLM
jq -c 'select(.action == "encrypt/pdf" and .details.llmProvider == "secondary")' logs/audit.log

# everything logged for one call
grep '<requestId>' logs/audit.log    # plus: docker logs encryption-service | grep '<requestId>'
```
