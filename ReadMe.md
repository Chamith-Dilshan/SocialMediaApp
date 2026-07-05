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

or look at the official doc for more information [UV Installation](https://docs.astral.sh/uv/getting-started/installation/)

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
```

Contribution guide lines->
1. we use pydantic for data validation
2. we need to use uv for dependency management
3. Every variable, class or function should be documented, and type hinted
