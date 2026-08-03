# SocialMediaApp

A modern Python application built with **FastAPI** and managed with **uv**, a fast and reliable Python package manager.

---

## Prerequisites

Before getting started, ensure you have the necessary tools installed on your system.

### Installing `uv`

**uv** is a unified Python packaging toolchain that serves as both your Python version manager and package manager.
**On Windows (PowerShell):**

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

or look at the official doc for more
information [UV Installation](https://docs.astral.sh/uv/getting-started/installation/)

### Install python using uv

```
uv python list
uv python install [version]
```

### Create a Python project (This will create project.toml)

```
uv init
```

### You can add dependencies to project.toml or

```
uv add [dependency]
```

### Sync dependencies with project.toml

```
uv sync
```

### To see installed dependencies

```
uv pip freeze
```

More information about uv can be found at [UV Features](https://docs.astral.sh/uv/getting-started/features/)

After you set up uv and virtual environment,
you can run uv sync to sync dependencies with project.toml
make sure that you have installed **fastapi[standard]** dependency

### Start Dev Server

```
fastapi dev or fastapi dev main.py
```

### Run Tests

```
pytest or uv run pytest
# Run all tests
pytest

# Verbose output
pytest -v

# With coverage summary in terminal
pytest --cov=app --cov-report=term-missing

# With HTML coverage report
pytest --cov=app --cov-report=html

# Target ≥ 90% coverage, fail otherwise
pytest --cov=app --cov-fail-under=90
```

### Initialize Alembic

```
uv add alembic
uv run alembic --help
alembic init -t pyproject_async alembic
```

### Run Alembic

when we want to do a change in database we can make a revision.
this will help us to track the changes in database.

```
uv run alembic revision -m "create users table"
```

alembic revision --autogenerate -m "create tables" -to auto generate revision file
alembic current -to check the current revision
alembic heads -to check the latest revision
alembic upgrade head -to upgrade to latest revision
alembic upgrade {revision number} -to upgrade to selected revision
alembic history -to check the history of revisions   
alembic downgrade -1 -to downgrade to previous revision
alembic downgrade {revision number} -to downgrade to selected revision

make sure to import model classes to env.py.  
ex -> import app.models.models # noqa: F401

### CORS Policy

do you know that you can go to your web browser and got to the google.com then open up the Dev Tools and go to Console
tab.
there you can right this command to send a request to the server. and you can see the response.
fetch('http://localhost:8000/health').then(res => res.json()).then(console.log)
This is about CORS Policies, if you didn't set up it, you will get an error.

### Docker

create a docker image

````aiignore
docker build -t social-media-app .
docker image ls
````

use created docker image and use docker compose to create the container.

To completely remove the container and all its data,
then build the image again and run it.

````aiignore
docker compose down -v
docker volume prune -f
docker compose up --build
````

````aiignore
docker compose ps
docker compose logs -f
docker compose up
````

to enter into the container

````aiignore
docker exec -it socialmediaapp-api-1 bash
````

Contribution guide lines->

1. we use pydantic for data validation
2. we need to use uv for dependency management
3. Every variable, class or function should be documented, and type hinted
