# Church Financial Management System

A comprehensive financial management system for churches, featuring AI-powered transaction categorization, bank statement import, and detailed financial reporting.

## Features

- **JWT Authentication** — Secure token-based auth with access and refresh tokens
- **Transaction Management** — Create, edit, categorize, and search financial transactions
- **AI Categorization** — Machine-learning model automatically classifies transactions by category
- **File Upload & Parsing** — Import bank statements in CSV and OFX formats; PDF support is planned for a future release
- **Financial Reports** — Monthly summaries, category breakdowns, and exportable data
- **Audit Trail** — Full history of changes to transactions and settings
- **Async Processing** — Background jobs via Celery for heavy tasks (parsing, classification)

## Tech Stack

| Layer | Technology |
|---|---|
| API | FastAPI |
| ORM | SQLAlchemy 2.0 |
| Migrations | Alembic |
| Task Queue | Celery + Redis |
| Cache/Broker | Redis |
| Database | PostgreSQL 15 |
| ML | scikit-learn, pandas, numpy |
| Containerization | Docker / Docker Compose |

## Quick Start (Docker)

```bash
# 1. Clone the repository
git clone https://github.com/jorgevideira/system-church.git
cd system-church

# 2. Copy and configure environment variables
cp .env.example .env
# Edit .env and set a strong SECRET_KEY

# 3. Start all services
docker-compose up --build

# 4. Apply database migrations (first run only)
docker-compose exec backend alembic upgrade head
```

The API will be available at **http://localhost:8000** and proxied through Nginx at **http://localhost:80**.

## Manual Setup

```bash
# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install dependencies
cd backend
pip install -r requirements.txt

# Configure environment
cp ../.env.example ../.env
# Edit .env with your DATABASE_URL, SECRET_KEY, REDIS_URL

# Apply migrations
alembic upgrade head

# Start the API server
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Start the Celery worker (separate terminal)
celery -A app.tasks.celery_app worker --loglevel=info
```

## API Documentation

Interactive Swagger UI is available at **http://localhost:8000/docs** once the server is running.  
ReDoc is available at **http://localhost:8000/redoc**.

## Environment Variables

| Variable | Description | Default |
|---|---|---|
| `DATABASE_URL` | PostgreSQL connection string | — |
| `SECRET_KEY` | JWT signing secret (change in production) | — |
| `ALGORITHM` | JWT algorithm | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Access token lifetime | `30` |
| `REFRESH_TOKEN_EXPIRE_DAYS` | Refresh token lifetime | `7` |
| `REDIS_URL` | Redis connection URL | `redis://localhost:6379` |
| `CELERY_BROKER_URL` | Celery broker URL | `redis://localhost:6379/0` |
| `CELERY_RESULT_BACKEND` | Celery result backend URL | `redis://localhost:6379/0` |
| `UPLOAD_DIR` | Directory for uploaded files | `uploads` |
| `MAX_FILE_SIZE` | Maximum upload size in bytes | `10485760` (10 MB) |
| `BACKEND_CORS_ORIGINS` | Allowed CORS origins (JSON array) | `["http://localhost:3000"]` |
| `PROJECT_NAME` | Project display name | `Church Financial Management System` |
| `API_V1_STR` | API version prefix | `/api/v1` |

## Project Structure

```
system-church/
├── backend/
│   ├── app/
│   │   ├── api/            # Route handlers (v1 endpoints)
│   │   ├── core/           # Config, security, dependencies
│   │   ├── models/         # SQLAlchemy ORM models
│   │   ├── schemas/        # Pydantic request/response schemas
│   │   ├── services/       # Business logic layer
│   │   ├── tasks/          # Celery async tasks
│   │   └── main.py         # FastAPI application entry point
│   ├── alembic/            # Database migration scripts
│   ├── tests/              # Pytest test suite
│   ├── alembic.ini
│   ├── Dockerfile
│   └── requirements.txt
├── .env.example
├── docker-compose.yml
├── nginx.conf
├── ARCHITECTURE.md
└── README.md
```

## License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.
