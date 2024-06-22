FROM python
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .

# global env across build images
COPY .env.prod ./.env

HEALTHCHECK --interval=300s --timeout=30s --start-period=5s --retries=3 CMD [ "executable" ]


EXPOSE 80 443 222 8000


CMD gunicorn src.wsgi:application --bind 0.0.0.0:8000