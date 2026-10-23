# AsyncFlow

AsyncFlow is a backend engineering project for processing uploaded CSV files as durable background jobs. The target architecture uses FastAPI, PostgreSQL, Redis, Celery, Pandas, and Docker Compose.

The project is currently building the first complete vertical slice: accept one CSV, persist a queued job, process it in a worker, track its lifecycle, and expose the result for download.

## Current progress

Overall vertical-slice progress is approximately **70%**.

Completed:

- CSV cleaning and statistics functions
- FastAPI application foundation
- PostgreSQL configuration through Docker Compose
- SQLAlchemy `Job` model and lifecycle fields
- Psycopg 3 throughout the application and migration tooling
- Alembic configuration and initial `jobs` table migration
- Verified model-to-database schema agreement
- Docker-managed shared job storage mounted at `/data/jobs`
- Verified file persistence across web-container recreation and visibility from a second container
- Redis broker running as a healthy Docker Compose service
- Celery application configured through the environment
- Celery worker connected to Redis and verified with an inspection ping
- Verified worker access to the shared `/data/jobs` volume
- Registered `app.tasks.process_job` with the Celery worker
- Verified delivery of a job UUID through Redis to the worker
- Verified worker-owned PostgreSQL session creation and job lookup
- Verified the durable `queued` to `processing` transition, UTC start time, and attempt count
- Celery task executes both clean and statistics operations
- Clean jobs write `output.csv` beside their persisted input file
- Statistics jobs store their JSON result in PostgreSQL
- Verified successful `processing` to `completed` transitions and completion timestamps
- Failed tasks persist `failed`, an error message, and a completion timestamp before re-raising to Celery

In progress or remaining:

- Durable job creation through the API
- Retry behavior
- Job status and result-download endpoints
- End-to-end integration testing

## Current architecture

- **FastAPI** exposes the HTTP API.
- **PostgreSQL** stores job metadata and lifecycle state.
- **SQLAlchemy** provides the application data model.
- **Alembic** owns database schema migrations.
- **Psycopg 3** is the PostgreSQL driver used by both the application and Alembic.
- **Pandas** implements CSV cleaning and statistics operations.
- **Redis** brokers background-task messages between the API and worker.
- **Celery** runs the background worker that will process queued jobs.
- **Docker Compose** runs the API, PostgreSQL, Redis, Celery worker, and Adminer, and manages the persistent `job_data` volume.

The broker, worker, and job task are operational. The worker can execute clean and statistics operations and persist both successful and failed outcomes, but the API does not enqueue uploaded jobs yet.

## Local setup

Create a local `.env` file with these variables:

```text
DATABASE_HOSTNAME=db
DATABASE_PORT=5432
DATABASE_USERNAME=postgres
DATABASE_PASSWORD=your-local-password
DATABASE_NAME=postgres
STORAGE_PATH=/data/jobs
CELERY_BROKER_URL=redis://redis:6379/0
```

Do not commit `.env`.
The database password must match `POSTGRES_PASSWORD` configured for the `db` service in `compose.yaml`.

Build and start the current services:

```bash
docker compose up -d --build
```

Apply database migrations:

```bash
docker compose exec web alembic upgrade head
```

Verify the migration state:

```bash
docker compose exec web alembic current
docker compose exec web alembic check
```

FastAPI documentation is available at `http://localhost/docs`. Adminer is available at `http://localhost:8080`.

## Migration workflow

Migration revision files must be generated in a persistent project directory and committed with the corresponding model changes. Do not generate a revision only inside an unmounted running container because the file will disappear when that container is recreated.

Before applying a generated migration:

1. Confirm the revision file exists under `alembic/versions/` in the repository.
2. Review both `upgrade()` and `downgrade()`.
3. Check PostgreSQL enum creation and cleanup.
4. Apply the migration.
5. Confirm `alembic current` and `alembic heads` report the same revision.
6. Run `alembic check` to detect model/schema drift.

## Current limitations

- The API still processes CSV operations within the request cycle.
- Jobs are not yet created or persisted through the upload endpoint.
- Failed tasks are recorded durably, but automatic retry behavior is not implemented.
- The shared volume is ready, but the API and future worker do not yet write job input and result files to it.
- Status, history, download, and retry endpoints are not implemented.
- Automated test coverage is not yet established.

These limitations are intentional at the current checkpoint and will be removed incrementally as the vertical slice is completed.
