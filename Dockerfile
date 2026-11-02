FROM python:3.15.2-slim

COPY --from=ghcr.io/astral-sh/uv:0.13.6 /uv /uvx /bin/

ENV UV_PROJECT_ENVIRONMENT=/opt/venv \
    UV_LINK_MODE=copy \
    UV_FROZEN=1 \
    UV_NO_CACHE=1 \
    RUFF_NO_CACHE=true \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY pyproject.toml uv.lock ./
RUN UV_COMPILE_BYTECODE=1 uv sync --locked

COPY . .

RUN useradd --create-home --uid 1000 maid
USER maid

CMD ["uv", "run", "python", "main.py"]
