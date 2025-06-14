FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Install dependencies
RUN uv sync --frozen --no-cache

# Copy source code
COPY src/ ./src/
COPY scripts/ ./scripts/

# Expose port
EXPOSE 8000

# Railway will handle health checks via the /health endpoint

# Run the API server
CMD ["uv", "run", "python", "src/api/main.py"]
