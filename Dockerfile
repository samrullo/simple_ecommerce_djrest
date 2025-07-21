FROM python:3.12-slim

# Copy uv binary
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Set environment variables for uv and virtualenv
ENV UV_PROJECT_ENVIRONMENT=/venv \
    UV_NO_MANAGED_PYTHON=1 \
    UV_PYTHON_DOWNLOADS=never \
    VIRTUAL_ENV=/venv

# Create virtual environment
RUN uv venv $VIRTUAL_ENV

# Set workdir for dependency resolution
WORKDIR /app

# Copy dependency files and wheels directory
COPY pyproject.toml uv.lock ./  
COPY py_wheels ./py_wheels

# Install dependencies using local wheels
RUN --mount=type=cache,target=/app/.cache/uv \
    uv sync --no-install-project --no-editable --find-links ./py_wheels

# Copy Django project source code
COPY . .

# Tell Render which port to expose
EXPOSE 8000

# Start Gunicorn server
CMD ["gunicorn", "core.wsgi:application", "--bind", "0.0.0.0:8000"]