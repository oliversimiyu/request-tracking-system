#!/usr/bin/env bash
# exit on error
set -o errexit

# Install dependencies
pip install -r requirements.txt

# Fix database schema by removing conflicting columns
echo "Fixing database schema..."
python manage.py dbshell < fix_schema.sql || echo "Schema fix attempted"

# Mark all migrations as applied without running them
echo "Marking migrations as applied..."
python manage.py migrate --fake

# Collect static files
python manage.py collectstatic --no-input

# Create superuser if it doesn't exist (optional)
python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
    print('Superuser created: admin/admin123')
else:
    print('Superuser already exists')
"