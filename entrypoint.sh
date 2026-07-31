#!/bin/bash
set -e

echo "Running migrations..."
python manage.py migrate --noinput

echo "Seeding default categories..."
python manage.py seed_categories

echo "Collecting static files..."
python manage.py collectstatic --noinput

exec "$@"
