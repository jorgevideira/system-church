# Architecture — Church Financial Management System

## System Overview

The system follows a layered, service-oriented backend architecture built on FastAPI. All client interactions happen through a versioned REST API. Heavy workloads (file parsing, AI classification) are offloaded to asynchronous Celery workers so the API stays responsive.

```
Client (Browser / Mobile)
        │
        ▼
   Nginx (reverse proxy)
        │
        ▼
   FastAPI (API layer)
        │
   ┌────┴──────────┐
   │               │
Services        Celery Workers
   │               │
   ▼               ▼
SQLAlchemy      Redis (broker / result backend)
   │
PostgreSQL
```

---

## Layered Architecture

| Layer | Responsibility |
|---|---|
| **API (`app/api/`)** | HTTP routing, request validation, response serialization |
| **Schemas (`app/schemas/`)** | Pydantic models for input validation and output shaping |
| **Services (`app/services/`)** | Business logic, orchestration, AI calls, file processing |
| **Models (`app/models/`)** | SQLAlchemy ORM definitions; single source of truth for the DB schema |
| **Tasks (`app/tasks/`)** | Celery task definitions for async/background processing |
| **Core (`app/core/`)** | App config (pydantic-settings), JWT security helpers, dependency injection |

---

## Database Schema

### Core Entities

- **User** — system accounts with hashed passwords and role information
- **Category** — transaction categories with types: `income`, `expense`, or `both`
- **Transaction** — individual financial entries linked to a user and category
- **StatementFile** — tracks uploaded bank statement files and their processing state
- **AuditLog** — immutable record of every data mutation (who, what, when)

### Key Relationships

```
User ──< Transaction >── Category
User ──< StatementFile
StatementFile ──< Transaction
Transaction ──< AuditLog
```

---

## Authentication Flow (JWT)

1. Client `POST /api/v1/auth/login` with credentials.
2. Server validates password hash (bcrypt via `passlib`).
3. Server issues a short-lived **access token** (default 8 hours) and a long-lived **refresh token** (default 30 days), both signed with `python-jose`.
4. Client includes `Authorization: Bearer <access_token>` on subsequent requests.
5. When the access token expires, client calls `POST /api/v1/auth/refresh` with the refresh token to obtain a new pair and retries the protected request once.
6. FastAPI dependency `get_current_user` validates the token on every protected endpoint.

---

## File Processing Pipeline

```
1. Upload        POST /api/v1/upload/
                 ↓ validate MIME type & size
                 ↓ save to UPLOAD_DIR
                 ↓ create ImportJob (status=pending)

2. Parse         Celery task: parse_statement_task
                 ↓ detect format (OFX → ofxparse, PDF → pdfplumber)
                 ↓ extract raw transaction rows

3. AI Classify   Celery task: classify_transactions_task
                 ↓ vectorize description text (TF-IDF)
                 ↓ predict category with trained model
                 ↓ attach confidence score

4. Deduplicate   Service: deduplication_service
                 ↓ hash (date + amount + description)
                 ↓ skip duplicates already in DB

5. Persist       Bulk insert validated transactions
                 ↓ update ImportJob (status=completed | failed)
                 ↓ emit AuditLog entries
```

---

## AI Classification

- **Algorithm:** TF-IDF vectorizer + Logistic Regression (scikit-learn pipeline)
- **Training data:** Manually labelled transactions stored in the database
- **Retraining:** Triggered via Celery beat schedule or manual API call
- **Fallback:** When confidence < threshold (configurable), the transaction is flagged for manual review

The model artifact is serialized with `joblib` and stored on disk; the service layer loads it lazily and caches it in memory.

---

## Async Processing (Celery)

| Task | Trigger | Description |
|---|---|---|
| `parse_statement_task` | File upload | Parses OFX/PDF into raw rows |
| `classify_transactions_task` | After parsing | Runs AI categorization |
| `generate_report_task` | On-demand / scheduled | Builds aggregate reports |
| `retrain_model_task` | Scheduled (Celery beat) | Retrains the classification model |

Redis serves as both the **message broker** and the **result backend**. Workers are stateless and horizontally scalable.

---

## Security Considerations

- **Secrets** — All sensitive values (DB credentials, `SECRET_KEY`) are loaded from environment variables; never committed to source control.
- **Password storage** — bcrypt hashing via `passlib`; no plaintext passwords stored.
- **SQL injection** — Prevented by SQLAlchemy parameterized queries; raw SQL is never constructed from user input.
- **File uploads** — MIME type validation, configurable size limit (`MAX_FILE_SIZE`), files stored outside the web root.
- **CORS** — Restricted to origins listed in `BACKEND_CORS_ORIGINS`.
- **HTTPS** — Nginx is configured for HTTP in development; TLS termination should be added at the Nginx layer in production.
- **Audit trail** — Every write operation appends an immutable `AuditLog` record, enabling forensic review.
