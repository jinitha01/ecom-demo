#!/bin/sh

set -e

until PGPASSWORD=$DB_PASSWORD psql -h "db" -U "$DB_USER" -d "$DB_NAME" -c '\q'; do
  >&2 echo "Postgres is unavailable - sleeping"
  sleep 1
done

python manage.py collectstatic --noinput


>&2 echo "Postgres is up - executing migrations"
python manage.py migrate

exec "$@"