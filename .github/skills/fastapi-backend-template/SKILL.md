---
name: fastapi-backend-template
description: "Use when extending this FastAPI PostgreSQL template: add or change routes, DTOs, Pydantic validation, SQLAlchemy models, Alembic migrations, repositories, services, authentication, tests, Docker, or CI/CD."
---

# FastAPI Backend Development

Use this skill for changes in this repository. It describes the project conventions, the request/data flow, and the checks required before considering a change complete.

## Repository map

- `app/main.py`: FastAPI application, lifespan, CORS, exception handler, router registration, and `/health`.
- `app/api/v1/`: thin HTTP routers for auth, users, posts, and likes.
- `app/dependancies/`: FastAPI dependencies for `AsyncSession` and the authenticated user.
- `app/services/`: business rules, authorization, security operations, and orchestration.
- `app/repositories/`: async SQLAlchemy queries, persistence, commits, rollbacks, and database exceptions.
- `app/models/`: SQLAlchemy ORM models: `User`, `Post`, and `PostLike`.
- `app/dtos/`: Pydantic request and response contracts.
- `app/mappers/`: conversion from repository projection data to response DTOs.
- `app/core/`: settings, database engine/session, declarative base, JWT/password security, exceptions, and logging.
- `alembic/`: migration environment and version scripts.
- `tests/`: async API tests, fixtures, and Faker factories.
- `.github/workflows/`: CI/CD workflow; `Dockerfile`, Compose files, `gunicorn.service`, and `nginx` are deployment examples.

The directory is named `dependancies` in the current codebase. Preserve that import path unless a deliberate repository-wide rename is requested.

## Required request flow

Keep the normal flow as:

```text
Router -> dependency -> service -> repository -> SQLAlchemy/PostgreSQL
```

Routers should parse HTTP input, declare dependencies, select response models, and delegate. Services should enforce business rules and ownership, hash passwords, coordinate operations, and map results where appropriate. Repositories should perform data access and own the existing transaction boundary. Do not put SQL queries in routers or business rules in repositories.

When one domain needs another domain's business rule, call that service. Do not reach directly into another feature's repository just to bypass validation. Direct repository use is appropriate when the current service needs its own persistence operation.

## DTOs and Pydantic

- Add request and response schemas under `app/dtos/`.
- Use Pydantic fields for input constraints such as length, ranges, and valid email addresses.
- Use separate create, update, and response models. Update models should support partial updates with `exclude_unset=True`.
- Never expose the ORM password field in a response DTO.
- Preserve `ConfigDict(from_attributes=True)` when a DTO is built from ORM objects.
- Keep OAuth2 login compatible with the existing form fields: `username` contains the email and `password` contains the password.
- Return the declared response model, not an arbitrary ORM shape or raw database row.

## Models and migrations

When changing persistence:

1. Update the SQLAlchemy model in `app/models/` with typed `Mapped` fields and relationships.
2. Ensure the model is imported by `app/models/models.py` and `alembic/env.py` can see it through metadata imports.
3. Generate a migration with `uv run alembic revision --autogenerate -m "describe the change"`.
4. Read and correct the generated migration; autogeneration is not a review substitute.
5. Apply it with `uv run alembic upgrade head` and test upgrade behavior.

The current models use PostgreSQL UUID server defaults, cascading foreign keys, timestamps, and a composite `(user_id, post_id)` key for likes. Preserve those invariants unless the feature explicitly changes them. The application lifespan currently calls `Base.metadata.create_all()` for convenience; it does not version schema changes. Do not silently rely on `create_all()` for production migrations.

## Database and repositories

Use the async `AsyncSession` supplied by `SessionDep`. Keep repository methods async and use SQLAlchemy `select()` expressions. Successful mutations commit and refresh as the existing repositories do; database failures roll back and surface the project database exception where that pattern is already used.

For post reads, use the shared projection query in `PostRepository` so responses consistently include the author, `like_count`, and viewer-specific `is_liked`. Extend that query for feed metadata rather than adding an N+1 query in a router or service.

Do not load passwords into response objects, manually concatenate database URLs, or add a synchronous database path to an async feature. Database credentials come from `app/core/config.py` and `.env`.

## Authentication and authorization

- Hash new and changed passwords with `get_password_hash` from `app/core/security.py`; never persist plaintext passwords.
- Verify credentials with the existing security helpers and issue JWTs with the configured algorithm, secret, subject, and expiry.
- Protect non-public routes with `get_current_user_dep` and `CurrentUser`.
- Enforce resource ownership in the service layer, not only by trusting a route parameter.
- Return the established `401` bearer response for invalid credentials/tokens and `403` for authenticated users who do not own a resource.
- Never commit real secrets. Development Compose values are examples and production values must come from environment/secret storage.

When changing auth, test missing, malformed, expired, and valid tokens, wrong credentials, and access to another user's resources.

## Exceptions and responses

Use the project's domain exceptions such as `NotFoundException`, `ConflictException`, and `DatabaseException` where their semantics apply. `app/main.py` currently serializes `AppException` as `{"detail": message}`. Preserve response status codes and shapes unless the API contract is intentionally versioned. Check the active handler in `app/main.py`; `app/core/exception_handlers.py` is an alternate registration module and is not currently registered at startup.

## Tests

Add tests in the matching `tests/auth`, `tests/users`, `tests/posts`, or `tests/likes` area. Reuse fixtures in `tests/fixtures` and data factories in `tests/factories`. Tests use `httpx.AsyncClient`, `ASGITransport`, dependency overrides, and a PostgreSQL `TEST_DB`; the fixture recreates tables but does not create the database.

For every behavior change, cover the happy path and relevant validation, not-found, unauthorized, forbidden, conflict, persistence, pagination, and response-shape cases. Keep tests isolated and do not depend on data left by another test.

## Commands and completion check

Use `uv` for dependency and command execution:

```powershell
uv sync
uv run pytest
uv run pytest tests/posts/test_posts.py
uv run pytest --cov=app --cov-report=term-missing
uv run ruff check .
uv run ruff format --check .
uv run black --check .
uv run pyrefly check
```

Before finishing, confirm:

- the route is registered and its DTO contract is explicit;
- business logic and ownership checks live in services;
- repository queries are async, parameterized, and transaction-safe;
- new models are imported and migrations are reviewed;
- passwords and secrets are handled safely;
- focused tests cover success and failure paths;
- the relevant test, coverage, lint, format, and type checks pass;
- Docker/CI/deployment configuration was updated only when the feature requires it and image names, ports, environment variables, and migration steps still agree.

## Avoid

- Do not place SQL or business rules in routers.
- Do not make services depend on another feature's repository when a service boundary exists.
- Do not return ORM models with sensitive fields exposed.
- Do not write plaintext or un-hashed passwords during updates.
- Do not edit a model without a reviewed Alembic migration.
- Do not assume `TEST_DB` is created by test fixtures or Compose.
- Do not treat `create_all()` as a replacement for production migrations.
- Do not copy hardcoded Compose credentials or machine-specific systemd paths into a deployment.
- Do not broaden unrelated refactors while implementing a feature.
