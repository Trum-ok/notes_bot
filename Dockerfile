ARG PYTHON_IMAGE=python:3.13.2-slim

FROM ${PYTHON_IMAGE} AS builder

ENV PYTHONFAULTHANDLER=1 \
    PYTHONHASHSEED=random \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    UV_PROJECT_ENVIRONMENT=/venv

COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

WORKDIR /code

COPY pyproject.toml uv.lock /code/

RUN uv sync --frozen --no-dev --no-install-project

FROM builder AS runtime

WORKDIR /code

ENV PATH=/venv/bin:$PATH

COPY . .

CMD ["uv", "run", "python", "-m", "notes.main"]