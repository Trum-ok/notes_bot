ARG PYTHON_IMAGE=python:3.13.2-slim

FROM ${PYTHON_IMAGE} AS builder

ENV PYTHONFAULTHANDLER=1 \
    PYTHONHASHSEED=random \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

COPY pyproject.toml uv.lock* ./

RUN uv venv
RUN uv sync --frozen --no-dev

RUN ls -la /app/.venv/bin && /app/.venv/bin/python -V

FROM ${PYTHON_IMAGE} AS runtime
WORKDIR /app

COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

COPY --from=builder /app/.venv /app/.venv

COPY . .

CMD ["uv", "run", "python", "-m", "notes.main"]