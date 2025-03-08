FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Install dependencies
COPY requirements.prod.txt .

RUN pip install --no-cache-dir -r requirements.prod.txt

# Copy environment-specific files
COPY .env.prod ./.env

# Copy the rest of the app
COPY . .

RUN python manage.py collectstatic --noinput

EXPOSE 8000

CMD ["gunicorn", "src.wsgi:application", "--bind", "0.0.0.0:8000"]
