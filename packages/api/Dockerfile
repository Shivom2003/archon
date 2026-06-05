FROM python:3.12-slim

WORKDIR /app

# System deps required by asyncpg (C extension)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies first (maximises Docker layer cache)
COPY pyproject.toml .
RUN pip install --no-cache-dir .

# Copy application code
COPY . .

# Make startup script executable
RUN chmod +x start.sh

# PORT is injected at runtime by Render / any PaaS
EXPOSE 8000

CMD ["./start.sh"]
