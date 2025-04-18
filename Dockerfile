FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Install dependencies
COPY requirements.docker.txt .

RUN pip install --no-cache-dir -r requirements.docker.txt

# Copy environment-specific files
COPY .env.prod ./.env

# Copy the rest of the app
COPY . .

# Collect static files
RUN python manage.py collectstatic --noinput

# Remove the unused env file
RUN rm -rf .env.prod requirements.docker.txt

# Application port
EXPOSE 8000

CMD ["gunicorn", "src.wsgi:application", "--bind", "0.0.0.0:8000"]
