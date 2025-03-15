# Stage 1: Build stage
FROM python:3.12-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.prod.txt .env.prod ./
RUN pip install --no-cache-dir -r requirements.prod.txt

# Copy the rest of the app
COPY . .

# Collect static files
RUN python manage.py collectstatic --noinput

# Stage 2: Final stage
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Copy only the necessary files from the build stage
COPY --from=builder /app /app

# Install runtime dependencies
COPY requirements.prod.txt .
RUN pip install --no-cache-dir -r requirements.prod.txt && \
    pip uninstall -y pip && \
    apt-get purge -y --auto-remove build-essential && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# Copy environment-specific files
COPY .env.prod ./.env

EXPOSE 8000

CMD ["gunicorn", "src.wsgi:application", "--bind", "0.0.0.0:8000"]
