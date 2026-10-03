# Firefighter Safety Data Hub — Backend

REST API for the Firefighter Safety Data Hub, a platform that collects firefighter exposure data from a mobile app and makes it available to researchers through a web dashboard.

The API is built with **FastAPI**, **SQLAlchemy 2** and **Alembic** on **PostgreSQL**, and uses **Amazon SES** for transactional email.

The client applications live in the companion repository **`firefighter-data-hub-frontend`**.

---

## Contents

1. [Features](#1-features)
2. [Tech stack](#2-tech-stack)
3. [Project structure](#3-project-structure)
4. [Getting started](#4-getting-started)
5. [Configuration](#5-configuration)
6. [Database migrations](#6-database-migrations)
7. [Development workflow](#7-development-workflow)
8. [Connecting the frontend](#8-connecting-the-frontend)
9. [Further documentation](#9-further-documentation)

---

## 1. Features

**Mobile API (`/api/v1`)**, used by the firefighter app:

- Registration with firefighter profile, email verification, login and token refresh
- Forgot-password and change-password flows, with notification emails
- Account deletion with removal of all user data
- GPS location upload and latest-location history
- Fire event logging, PPE submission and smoke sampler submission
- Health check

**Web API (`/api/v1/web_api`)**, used by the researcher dashboard:

- Researcher registration, login and profile management
- Dashboard summary statistics
- Paginated GPS and event tables with CSV export

See [docs/API.md](docs/API.md) for every endpoint.

---

## 2. Tech stack

| Area | Library / service |
|---|---|
| Language | Python 3.11 |
| Web framework | FastAPI 0.115, uvicorn |
| ORM and migrations | SQLAlchemy 2.0, Alembic 1.13 |
| Database | PostgreSQL (Amazon RDS in production), `psycopg2` driver |
| Settings | pydantic-settings (reads `.env`) |
| Auth | python-jose (JWT, HS256), passlib + bcrypt |
| Email | Amazon SES through boto3 |
| File storage | Amazon S3 through boto3 (optional) |

---

## 3. Project structure

```
.
├── app/
│   ├── main.py                    # Application entry point: CORS and router registration
│   ├── core/
│   │   ├── config.py              # Settings loaded from environment variables
│   │   ├── security.py            # Password hashing, JWT creation and validation
│   │   ├── deps.py                # Database session dependency
│   │   └── s3.py                  # S3 client helper
│   ├── db/
│   │   ├── base.py                # SQLAlchemy declarative base
│   │   ├── base_class.py          # Imports every model so Alembic can see them
│   │   └── session.py             # Engine and session factory
│   ├── models/                    # SQLAlchemy models (one file per table group)
│   ├── schemas/                   # Shared Pydantic schemas
│   ├── services/
│   │   ├── email_service.py       # Sends email through SES
│   │   ├── email_templates.py     # HTML and text email bodies
│   │   └── email_token_service.py # Signed, time-limited email tokens
│   └── api/v1/
│       ├── router.py              # Mobile API router
│       ├── endpoints/             # Mobile API endpoint modules
│       ├── dtos/                  # Mobile API request models
│       └── web_api/
│           ├── router.py          # Web API router
│           ├── endpoints/         # Web API endpoint modules
│           ├── requestDTO/        # Web API request models
│           └── responseDTO/       # Web API response models
├── alembic/                       # Migration environment and versions
├── alembic.ini
├── requirements.txt
├── Dockerfile
├── .env.example                   # Template for the .env file
└── docs/                          # Architecture, API, deployment, database access and roadmap
```

**How a request is handled:** `main.py` routes the request to an endpoint module. The endpoint validates the body with a DTO, checks the bearer token through `core/security.py`, gets a database session from `core/deps.py`, reads or writes models, and calls `services/` when email is needed.

---

## 4. Getting started

### Step 1: Install the prerequisites

- Python 3.11
- PostgreSQL 14 or newer (local install or Docker), or access to an existing database
- Git

Check your Python version:

```bash
python3.11 --version
```

### Step 2: Clone the repository

```bash
git clone <repository-url> firefighter-data-hub-backend
cd firefighter-data-hub-backend
```

### Step 3: Create a virtual environment and install dependencies

macOS / Linux:

```bash
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Windows (PowerShell):

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### Step 4: Start a local PostgreSQL database

With Docker:

```bash
docker run --name firefighter-db -e POSTGRES_PASSWORD=postgres -e POSTGRES_DB=firefighter -p 5432:5432 -d postgres:16
```

Or, with PostgreSQL already installed on your machine:

```bash
createdb firefighter
```

### Step 5: Create the `.env` file

```bash
cp .env.example .env
```

Open `.env` and set at least `DATABASE_URL`, `SECRET_KEY`, `SES_FROM_EMAIL` and `EMAIL_TOKEN_SECRET`. The default `DATABASE_URL` in `.env.example` points at the Docker database from Step 4. For a local PostgreSQL install, change its user and password to your own. See [Configuration](#5-configuration) for every variable.

Generate random secrets with:

```bash
python -c "import secrets; print(secrets.token_urlsafe(48))"
```

### Step 6: Create the database tables

```bash
alembic upgrade head
```

> **Known issue.** The migrations do not create the `users_researcher` table, so web dashboard registration and login fail on a new database. The mobile API is not affected. See item F2 in [docs/ROADMAP.md](docs/ROADMAP.md).

### Step 7: Run the API

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Step 8: Check that it works

```bash
curl http://localhost:8000/api/v1/health
# {"status":"ok"}
```

Open the interactive API documentation at <http://localhost:8000/docs>.

> **Email in local development.** Registration sends a verification email through SES. Without valid AWS credentials the account is still created, but the email is not sent and login is refused until the address is verified. To test locally, either configure SES credentials for a verified sender address, or set `is_email_verified = true` on your test user directly in the database.

### Running with Docker instead

```bash
docker build -t firefighter-backend .
docker run --env-file .env -p 8000:8000 firefighter-backend
```

When the database runs on your host machine, use `host.docker.internal` instead of `localhost` in `DATABASE_URL`.

---

## 5. Configuration

All settings are read from environment variables, normally through the `.env` file. `.env` is ignored by Git and must never be committed.

| Variable | Required | Default | Description |
|---|---|---|---|
| `DATABASE_URL` | Yes | – | `postgresql+psycopg2://USER:PASSWORD@HOST:5432/DBNAME` |
| `SECRET_KEY` | Yes | – | Secret used to sign JWT access tokens |
| `ALGORITHM` | No | `HS256` | JWT signing algorithm |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | No | `10080` (7 days) | Access token lifetime |
| `CORS_ORIGINS` | No | `*` | `*` or a comma-separated list of allowed origins |
| `APP_NAME` | No | `FireFighterDataHub` | Title shown in the API docs |
| `API_V1_PREFIX` | No | `/api/v1` | URL prefix for all routes |
| `SES_REGION` | No | `us-east-1` | SES region |
| `SES_FROM_NAME` | No | `Firefighter-DataHub-Team` | Sender display name |
| `SES_FROM_EMAIL` | Yes | – | Sender address, verified in SES |
| `EMAIL_TOKEN_SECRET` | Yes | – | Secret used to sign email verification and reset tokens |
| `EMAIL_VERIFICATION_MODE` | No | `manual` | `manual`: the user pastes the emailed token into the app |
| `FRONTEND_VERIFY_BASE_URL` | No | – | Base URL for clickable verification links (future use) |
| `AWS_REGION`, `S3_BUCKET_NAME` | Only for `/files` | – | S3 bucket used for uploads |
| `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY` | No | – | Only when no IAM role is available. On EC2, use an IAM role instead |

The four AWS variables in the last two rows are listed in `.env.example` but are not yet defined in `app/core/config.py`, so the `/files` endpoints do not work. See item F3 in [docs/ROADMAP.md](docs/ROADMAP.md).

---

## 6. Database migrations

The schema is managed with Alembic. `alembic/env.py` reads `DATABASE_URL` from `.env`.

| Task | Command |
|---|---|
| Apply all migrations | `alembic upgrade head` |
| Show the current revision | `alembic current` |
| Show history | `alembic history` |
| Create a migration after changing a model | `alembic revision --autogenerate -m "short description"` |
| Roll back one migration | `alembic downgrade -1` |

When you add a new model, import it in `app/db/base_class.py` so that autogenerate detects it. Always review the generated file in `alembic/versions/` before applying it.

---

## 7. Development workflow

### Adding an endpoint

1. Create or update the request model in `app/api/v1/dtos/` (mobile) or `app/api/v1/web_api/requestDTO/` (web).
2. Add the route function to the relevant module in `endpoints/`, using `Depends(get_db)` for the session and the helpers in `core/security.py` to authenticate the user.
3. If the module is new, register its router in `app/api/v1/router.py` or `app/api/v1/web_api/router.py`.
4. Check the endpoint in `/docs`, then document it in [docs/API.md](docs/API.md).

### Changing the database

1. Edit or add a model in `app/models/`.
2. Import new models in `app/db/base_class.py`.
3. Generate and review a migration, then run `alembic upgrade head`.

### Conventions

- Mobile endpoints live under `/api/v1`, web dashboard endpoints under `/api/v1/web_api`.
- Secrets come from environment variables only.
- Keep changes to request and response shapes in sync with the frontend's `mobile/lib/services/` and `web/src/api/`.

---

## 8. Connecting the frontend

| Client | Where its API address is set | Value for a local backend |
|---|---|---|
| Web dashboard | `web/.env` (`API_PROXY_TARGET` or `VITE_API_BASE_URL`) | `API_PROXY_TARGET=http://127.0.0.1:8000` |
| Mobile app | `mobile/lib/config/app_config.dart` | `useAwsBackend = false`, `port = '8000'`, `localLanOverride = ''` |

For a deployed backend, add the web dashboard's URL to `CORS_ORIGINS`.

---

## 9. Further documentation

| Document | Contents |
|---|---|
| [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) | How the mobile app, web dashboard, API and AWS services fit together, data model, authentication |
| [docs/API.md](docs/API.md) | Every endpoint, with method, path, authentication and purpose |
| [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md) | Deploying to EC2 with systemd, logs, HTTPS setup and post-deployment checks |
| [docs/DATABASE_ACCESS.md](docs/DATABASE_ACCESS.md) | Connecting to the production or a local database with DBeaver, browsing and exporting data |
| [docs/ROADMAP.md](docs/ROADMAP.md) | Known issues and planned work |
