FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Install dependencies
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Copy environment-specific files
COPY .env.prod ./.env

# Copy the rest of the app
COPY . .

ENV PORT=8000

EXPOSE ${PORT}

CMD gunicorn src.wsgi:application --bind 0.0.0.0:${PORT}
