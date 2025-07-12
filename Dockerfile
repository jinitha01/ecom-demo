FROM python:3.12-alpine
ENV PYTHONUNBUFFERED=1
ENV DJANGO_SETTINGS_MODULE=ecom_demo.settings

WORKDIR /app

RUN apk add --no-cache build-base libffi-dev openssl-dev bzip2-dev zlib-dev readline-dev postgresql-client postgresql-dev

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Explicitly set PYTHONPATH for management commands to ensure they find your project
RUN PYTHONPATH=/app python manage.py collectstatic --noinput

# Entrypoint script must use /bin/sh (Alpine doesn't have bash)
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

EXPOSE 8000
ENTRYPOINT ["/entrypoint.sh"]
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "ecom_demo.wsgi:application"]