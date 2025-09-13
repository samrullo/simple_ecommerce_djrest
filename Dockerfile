FROM python:3.12-slim

# Copy uv binary
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Set environment variables
ENV UV_PROJECT_ENVIRONMENT=/venv \
    UV_NO_MANAGED_PYTHON=1 \
    UV_PYTHON_DOWNLOADS=never \
    VIRTUAL_ENV=/venv \
    PATH="/venv/bin:$PATH"

# Create virtual environment
RUN uv venv $VIRTUAL_ENV

WORKDIR /app

# Install dependencies
COPY pyproject.toml uv.lock ./
COPY py_wheels ./py_wheels
RUN --mount=type=cache,target=/app/.cache/uv \
    uv sync --no-install-project --no-editable --find-links ./py_wheels

# Copy app code
COPY . .

# Default command (can be overridden by docker-compose)
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000"]