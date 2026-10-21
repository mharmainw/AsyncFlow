# AsyncFlow

AsyncFlow is a backend engineering project for processing uploaded CSV files as durable background jobs. The target architecture uses FastAPI, PostgreSQL, Redis, Celery, Pandas, and Docker Compose.

The project is currently building the first complete vertical slice: accept one CSV, persist a queued job, process it in a worker, track its lifecycle, and expose the result for download.

## Current progress

Overall vertical-slice progress is approximately **45%**.

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

In progress or remaining:

- Durable job creation through the API
- Celery task implementation and registration
- Queued, processing, completed, and failed state transitions
- Job status and result-download endpoints
- Failure handling and retry behavior
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

The broker and worker infrastructure is operational, but no CSV-processing task is registered yet. CSV processing is not asynchronous yet.

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
- The Celery worker is operational but has no registered CSV-processing task yet.
- The shared volume is ready, but the API and future worker do not yet write job input and result files to it.
- Status, history, download, and retry endpoints are not implemented.
- Automated test coverage is not yet established.

These limitations are intentional at the current checkpoint and will be removed incrementally as the vertical slice is completed.
