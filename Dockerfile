FROM python

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

COPY requirements.txt .
COPY . .

RUN pip install --no-cache-dir -r requirements.txt && python manage.py collectstatic --noinput


CMD ["gunicorn", "--bind", "0.0.0.0:8000", "src.wsgi:application"]
